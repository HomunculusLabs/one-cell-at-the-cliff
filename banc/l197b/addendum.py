"""L197b addendum — POST HOC, descriptive (written after the FINAL verdict was
read). Zero rollouts; stored l197b raws only; frozen gj.py unchanged.
(1) v1's OWN readout (W=500, starts -250..+250) on arm S's 96 fresh seeds —
    arm S uses v1's schedule law, so this is a 6x replication of L186 as run.
(2) per-GRAPH aligned duty by tone-rotation bin (which graph carries the
    in-phase / antiphase split), both design arms.
(3) same-seed (diagonal) duty per graph, both arms (does the phenotype itself
    survive the 250-step pulse?)."""
import json, sys
import numpy as np
sys.path.insert(0, "l197b")
import gj
SCHED = json.load(open("l197b/schedule.json"))
store = {}
for w in range(6):
    z = np.load(f"l197b/raw_w{w}.npz")
    for s in SCHED["arms"]["S"]["seeds"][w::6] + SCHED["arms"]["W"]["seeds"][w::6]:
        for k in ("gate_{s}", "Ti_fR_cutwA_{s}", "Ti_eR_cutwA_{s}", "Ti_fR_sc25_{s}", "Ti_eR_sc25_{s}"):
            store[k.format(s=s)] = z[k.format(s=s)]
out = {}
f3 = lambda d: f"{d['value']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]"
seedsS = SCHED["arms"]["S"]["seeds"]
onsS = {s: [o[0], 4000 + o[1]] for s, o in ((s, SCHED["arms"]["S"]["onsets"][str(s)]) for s in seedsS)}
v = gj.analyse(store, seedsS, onsS, 500, np.arange(-250, 251, 10))
out["S_seeds_v1_readout_W500"] = {k: v[k] for k in ("A", "T", "D", "T_on", "T_off", "A_inphase", "A_antiphase", "A_in_minus_anti", "means", "tone_instrument")}
out["S_seeds_v1_readout_W500"]["overlap"] = gj.overlap_stats(onsS, seedsS, 500)
print("v1 readout (W=500) on S's 96 seeds: A", f3(v["A"]), "T", f3(v["T"]), "D", f3(v["D"]), "| overlap", round(out["S_seeds_v1_readout_W500"]["overlap"]["mean_overlap"], 3))
print("   T_on", f3(v["T_on"]), "T_off", f3(v["T_off"]), "| A_in", f3(v["A_inphase"]), "A_anti", f3(v["A_antiphase"]), "diff", f3(v["A_in_minus_anti"]))
print("   means", v["means"])
print("   tone", v["tone_instrument"])
for arm in ("S", "W"):
    d = gj.DESIGN[arm]; seeds = SCHED["arms"][arm]["seeds"]
    ons = {s: [o[0], 4000 + o[1]] for s, o in ((s, SCHED["arms"][arm]["onsets"][str(s)]) for s in seeds)}
    n = len(seeds); mo = np.broadcast_to(~np.eye(n, dtype=bool), (2, n, n))
    blk = {}
    for g in ("cutwA", "sc25"):
        H = gj.pair_hits(store, g, seeds, ons, d["W"], gj.starts_of(arm))
        al = H["hit_al"].mean(-1); rot = gj.rot_of(H["lag"])
        blk[g] = dict(aligned_inphase=float(al[mo & (rot >= .75)].mean()), aligned_mid=float(al[mo & (rot > .25) & (rot < .75)].mean()),
                      aligned_antiphase=float(al[mo & (rot <= .25)].mean()),
                      same_seed=float(np.mean([al[s_, i, i] for s_ in range(2) for i in range(n)])))
    out[f"{arm}_by_graph"] = blk
    print(arm, json.dumps({g: {k: round(x, 3) for k, x in b.items()} for g, b in blk.items()}))
json.dump(out, open("l197b/addendum.json", "w"), indent=1)
