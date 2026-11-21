"""L150 verdict: B-cert (raw_l135 B26 / raw_l142 B29 / raw_l144 B30 incl
sil1110_wA / raw_l145 B31 incl eMot halves / raw_l148 B33-preceding batch)
BEFORE any B33 read; then anchors/P4/B33 table/classes/H-branches/pooled.
Criteria VERBATIM L118-L131, helper code verbatim l145/l148 verdict (L85
cert rule). PREREG l150/PREREG.md (bands registered before the run)."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


_SM = {}


def s_arrays(raw, a, s, pk):
    key = (id(raw), a, s, pk)
    if key not in _SM:
        ag, bg = PREF[pk]
        tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN]
              for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(tr[f"{ag}L"][t - 499:t + 1], tr[f"{bg}L"][t - 499:t + 1])
            SR[t] = S_of(tr[f"{ag}R"][t - 499:t + 1], tr[f"{bg}R"][t - 499:t + 1])
        _SM[key] = (SL, SR)
    return _SM[key]


def duty_seeds(raw, a, seeds, pk):
    """Rounded per-seed duty values (the l109/l111/l113 rounding-path atom)."""
    L, R = [], []
    for s in seeds:
        SL, SR = s_arrays(raw, a, s, pk)
        q07 = np.zeros(len(TS), bool)
        for a0, b0, f in SEGB:
            if f == 0.7:
                q07 |= (TS >= a0 + MEAS0) & (TS < b0)
        L.append(round(float(np.nanmean(SL[TS[q07]] >= .25)), 3))
        R.append(round(float(np.nanmean(SR[TS[q07]] >= .25)), 3))
    return np.array(L), np.array(R)


def side_k(raw, a, seeds, pk):
    L, R = duty_seeds(raw, a, seeds, pk)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ---- batches ----
B33 = list(range(3365, 3381))
B32 = list(range(3349, 3365))
B31 = list(range(3333, 3349))
B30 = list(range(3317, 3333))
B29 = list(range(3301, 3317))
B26 = list(range(3001, 3017))
B25 = list(range(2901, 2917))
B24 = list(range(2801, 2817))
B21 = list(range(2501, 2517))
ARMS150 = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5", "eMotBot5"]
LADDER150 = [("0", "full"), ("24", "cutwA"), ("top5", "eMotTop5"),
             ("bot5", "eMotBot5"), ("silW", "silW"), ("25", "cutng25")]
z150 = np.load("l150/raw_l150.npz")
z148 = np.load("l148/raw_l148.npz")
z145 = np.load("l145/raw_l145.npz")
z144 = np.load("l144/raw_l144.npz")
z142 = np.load("l142/raw_l142.npz")
z135 = np.load("l135/raw_l135.npz")
z133 = np.load("l133/raw_l133.npz")
z131 = np.load("l131/raw_l131.npz")
z126 = np.load("l126/raw_l126.npz")
ar = json.load(open("l150/anchors_run.json"))
r135 = json.load(open("l135/results_l135.json"))
r142 = json.load(open("l142/results_l142.json"))
r144 = json.load(open("l144/results_l144.json"))
r145 = json.load(open("l145/results_l145.json"))
r148 = json.load(open("l148/results_l148.json"))
MASS = r142["static"]["arm_mass_frac_dn"]

# ---- B-cert BEFORE any B33 read (L85 rule), FIVE certs ----
bcert_fail = []
for a in ("cutwA", "cutng25"):
    want = r135["table"]["Ti"][a]
    got = side_k(z135, a, B26, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append(("l135", a, kk, got[kk], want[kk]))
for a in ("eAll", "cutwA", "cutng25"):
    want = r142["table"]["Ti"][a]
    got = side_k(z142, a, B29, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append(("l142", a, kk, got[kk], want[kk]))
for a in ("cutwA", "cutng25", "sil1110_wA"):
    want = r144["table"]["Ti"][a]
    got = side_k(z144, a, B30, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append(("l144", a, kk, got[kk], want[kk]))
for a in ("cutwA", "cutng25", "eMotTop5", "eMotBot5"):
    want = r145["table"]["Ti"][a]
    got = side_k(z145, a, B31, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append(("l145", a, kk, got[kk], want[kk]))
for a in ("cutwA", "cutng25"):
    want = r148["table"]["Ti"][a]
    got = side_k(z148, a, B32, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append(("l148", a, kk, got[kk], want[kk]))
assert not bcert_fail, ("B-cert FAIL (no B33 read)", bcert_fail[:5])
print("B-cert vs results_l135 (B26) + l142 (B29) + l144 (B30 incl clamp arm)"
      " + l145 (B31 incl eMot halves) + l148 (B32) Ti tables: PASS")

# ---- P0 anchors (gate booleans ONLY, L59 rule) ----
p0 = dict(c0a_pass=ar["c0a150_pass"], c0a_max=ar["c0a150_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"],
          g_emottop5_stored_exact=ar["g_emottop5_stored_exact"],
          g_emotbot5_stored_exact=ar["g_emotbot5_stored_exact"],
          g_silW_graphid=bool(ar["g_silW"] == ar["g_cutwA"]),
          fc144_pass=ar["fc144_pass"], fc144_max=ar["fc144_max"],
          fc145_pass=ar["fc145_pass"], fc145_max=ar["fc145_max"])
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cutwA_stored_exact"]
                  and p0["g_cutng25_stored_exact"]
                  and p0["g_emottop5_stored_exact"]
                  and p0["g_emotbot5_stored_exact"] and p0["g_silW_graphid"]
                  and p0["fc144_pass"] and p0["fc145_pass"])
print("P0 anchors (C0A-150 + stored gains x4 + FC-144 + FC-145):",
      "PASS" if p0["pass"] else "FAIL",
      f"(c0a {p0['c0a_max']:.1e} | FC-144 {p0['fc144_max']:.1e} | "
      f"FC-145 {p0['fc145_max']:.1e})")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z150[f"af_{a}_{s}"]) for s in B33])), 6)
           for a in ARMS150}
af_range_ok = all(0.01 < float(z150[f"af_{a}_{s}"]) < 0.9
                  for a in ARMS150 for s in B33)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band),
          af_mean=af_mean, e_band_ok=ar["e_band_ok"],
          new_stairs=ar["new_stairs"])
print("P4", json.dumps({k: p4[k] for k in ("af_range_ok", "b65_band",
                                           "e_band_ok")}))

# ---- B33 per-side duty table (5 pairs x 7 arms) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS150:
        t = side_k(z150, a, B33, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B33 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS150:
        t = table[pk][a]
        print(f"{pk} {a:9s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Ti ladder classification (criteria VERBATIM L118-L131) ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z150, "full", B33, "Ti")
_, RwA = duty_seeds(z150, "cutwA", B33, "Ti")
dose = {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {}}


def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


cls, killmap = {}, {}
for kk, a in LADDER150:
    t = table["Ti"][a]
    _, Rd = duty_seeds(z150, a, B33, "Ti")
    legs = dict(
        mean_paired_dR_vs_full=round(float((Rd - Rfull).mean()), 3),
        n_down_vs_full=int(((Rd - Rfull) <= -.20).sum()),
        mean_paired_dR_vs_wA=round(float((Rd - RwA).mean()), 3),
        n_down_vs_wA=int(((Rd - RwA) <= -.20).sum()),
        n_up_vs_wA=int(((Rd - RwA) >= .20).sum()))
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR_vs_full"] <= -.20)
    dose["meanR"][kk] = t["meanR"]; dose["kR"][kk] = t["kR"]
    dose["meanL"][kk] = t["meanL"]; dose["kL"][kk] = t["kL"]
    dose["legs"][kk] = legs
    killmap[kk] = bool(kill)
    cls[kk] = dict(arm=a, meanR=t["meanR"], kR=t["kR"], meanL=t["meanL"],
                   kL=t["kL"], kill=bool(kill), restore=_restore(t),
                   super=_super(t), partial=_partial(t), legs=legs,
                   mass=MASS.get(a))
    print(f"Ti {kk:>5s} ({a:9s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | dR_wA "
          f"{legs['mean_paired_dR_vs_wA']:+.3f} n_up_wA "
          f"{legs['n_up_vs_wA']:2d}/16 -> "
          f"{'KILL' if kill else 'no-kill'}"
          f"{'/RESTORE' if _restore(t) else ''}"
          f"{'/SUPER' if _super(t) else ''}"
          f"{'/PARTIAL' if _partial(t) else ''}")
dose["m0"] = m0

# ---- pooled reads (L90 full-precision Wilson, unrounded) ----
def pooled(raws, a, batches, pk="Ti"):
    Ls, Rs = [], []
    for raw, b in zip(raws, batches):
        L, R = duty_seeds(raw, a, b, pk)
        Ls.append(L); Rs.append(R)
    R_ = np.concatenate(Rs); L_ = np.concatenate(Ls)
    kR, kL = int((R_ >= .5).sum()), int((L_ >= .5).sum())
    lbR, ubR = wilson(kR, len(R_)); lbL, ubL = wilson(kL, len(L_))
    return dict(kR=kR, n=len(R_), lbR=lbR, ubR=ubR, kL=kL, lbL=lbL, ubL=ubL,
                meanR=round(float(R_.mean()), 3),
                meanL=round(float(L_.mean()), 3))


# silW pooled leg: B30 traces live in z144 under the l144 arm name
# ('sil1110_wA'), B33 in z150 under 'silW' — concatenate manually.
L30, R30 = duty_seeds(z144, "sil1110_wA", B30, "Ti")
L33, R33 = duty_seeds(z150, "silW", B33, "Ti")
R_ = np.concatenate([R30, R33]); L_ = np.concatenate([L30, L33])
kR = int((R_ >= .5).sum()); kL = int((L_ >= .5).sum())
lbR, ubR = wilson(kR, len(R_)); lbL, ubL = wilson(kL, len(L_))
pooled_silW = dict(kR=kR, n=len(R_), lbR=lbR, ubR=ubR, kL=kL, lbL=lbL,
                   ubL=ubL, meanR=round(float(R_.mean()), 3),
                   meanL=round(float(L_.mean()), 3),
                   batches="B30(l144 sil1110_wA)+B33(l150 silW)")
pooled_top5 = pooled([z145, z150], "eMotTop5", [B31, B33])
pooled_bot5 = pooled([z145, z150], "eMotBot5", [B31, B33])
pooled_ng25 = pooled([z131, z133, z135, z142, z144, z145, z148, z150],
                     "cutng25",
                     [B24, B25, B26, B29, B30, B31, B32, B33])
pooled_wA = pooled([z126, z131, z133, z135, z142, z144, z145, z148, z150],
                   "cutwA", [B21, B24, B25, B26, B29, B30, B31, B32, B33])
print("pooled silW B30+B33:", json.dumps(pooled_silW))
print("pooled eMotTop5 B31+B33:", json.dumps(pooled_top5))
print("pooled eMotBot5 B31+B33:", json.dumps(pooled_bot5))
print("pooled cutng25 8-batch:", json.dumps(pooled_ng25))
print("pooled cutwA 9-batch:", json.dumps(pooled_wA))

# ---- H1 (PRIMARY): silW replication, PREREG bands ----
c_silW = cls["silW"]
cls_of = lambda c: ("KILL" if c["kill"] else
                    "SUPER" if c["super"] else
                    "RESTORE" if c["restore"] else
                    "PARTIAL" if c["partial"] else "NONE")
h1 = dict(
    arm="silW", b33_class=cls_of(c_silW), meanR=c_silW["meanR"],
    kR=c_silW["kR"], paired_dR_vs_wA=c_silW["legs"]["mean_paired_dR_vs_wA"],
    n_up_vs_wA=c_silW["legs"]["n_up_vs_wA"],
    class_leg=bool(c_silW["super"]),
    pooled_leg=bool(pooled_silW["kR"] >= 20 and pooled_silW["lbR"] >= .50),
    pooled=pooled_silW,
    b30_ctx=dict(meanR=.622, kR=14, paired_dR_vs_wA=.189, n_up=6))
h1["replicates"] = bool(h1["class_leg"] or h1["pooled_leg"])
h1["paired_leg"] = bool(c_silW["legs"]["mean_paired_dR_vs_wA"] >= .10)
h1["note"] = ("substrate-gated flip REPLICATES on a fresh batch"
              if h1["replicates"] else
              "NON-REPLICATION branch (PREREG): B33 meanR "
              f"{c_silW['meanR']:.3f}, pooled lb {pooled_silW['lbR']:.3f} — "
              "DRAFT v3 abstract substrate-gate sentence gets a "
              "batch-scoped amendment this tick")
print("H1", json.dumps(h1))

# ---- H2: halves second batch (threshold footprint) ----
c_t5, c_b5 = cls["top5"], cls["bot5"]
h2 = dict(
    top5_b33=dict(cls=cls_of(c_t5), meanR=c_t5["meanR"], kR=c_t5["kR"],
                  dR_wA=c_t5["legs"]["mean_paired_dR_vs_wA"]),
    bot5_b33=dict(cls=cls_of(c_b5), meanR=c_b5["meanR"], kR=c_b5["kR"],
                  dR_wA=c_b5["legs"]["mean_paired_dR_vs_wA"]),
    pooled_top5=pooled_top5, pooled_bot5=pooled_bot5,
    all10_ctx=dict(pooled_B29_B31="21/32 lbR .483 (l145)"),
    predicted=("threshold footprint holds: each half pooled kR below the "
               "all-10 rate and both below cutng25 lb .912")
    if (pooled_top5["kR"] < 21 and pooled_bot5["kR"] < 21
        and pooled_top5["lbR"] < .912 and pooled_bot5["lbR"] < .912)
    else "half EXCEEDS the all-10 pooled rate — threshold claim amended",
    b33_super_flip=[nm for nm, c in (("top5", c_t5), ("bot5", c_b5))
                    if c["super"]])
if h2["b33_super_flip"]:
    h2["b33_super_flip_note"] = ("single-batch SUPER on B33 alone = batch "
                                 "re-draw disclosure (L139 interior class); "
                                 "pooled carries any amendment")
print("H2", json.dumps(h2))

# ---- P3: Ti_L dead on flipping arms (crossed law) ----
flips = [kk for kk in cls if cls[kk]["super"] or cls[kk]["restore"]]
p3 = dict(flipping_arms=flips,
          tiL_dead={kk: dict(meanL=cls[kk]["meanL"], kL=cls[kk]["kL"])
                    for kk in flips},
          note="Ti_L dies with every flipping arm (crossed law holds)"
          if all(cls[kk]["kL"] <= 2 for kk in flips) else
          "Ti_L SURVIVES a flipping arm — disclosed")
print("P3", json.dumps(p3))

# ---- disclosures + sanity ----
san = dict(
    full_class_batch_drawn=dict(meanR=m0, kR=table["Ti"]["full"]["kR"],
        note="class labels read vs m0/paired legs, not bare bands (L109)"),
    silW_gain="graph-identity af-match to cutwA (l144 A1 form); settle "
              "clamp-free; window clamp X[467]=0 from step 0",
    silW_name_map="l150 arm 'silW' == l144 arm 'sil1110_wA' (same clamp, "
                  "same graph, same gain; FC-144 certifies bit-identity)",
    eMot_bisects="fresh, asserted == l145 stored EXACT (deterministic "
                 "re-land); staircase residuals in anchors_run.json",
    no_renorm_arm="lineage build has no in-degree renorm")
print("watch: Tr_R wA", table["Tr"]["cutwA"]["meanR"], "silW",
      table["Tr"]["silW"]["meanR"])
print("sanity b65 Ti kL/kR", table["Ti"]["b65"]["kL"], table["Ti"]["b65"]["kR"])

out = dict(design="L150 silW batch rebase + eMot halves second batch "
                  "(PREREG l150/PREREG.md)",
           anchors=ar, p0=p0, p4=p4, table=table, dose=dose, classes=cls,
           hypotheses=dict(H1_silW=h1, H2_halves=h2, P3=p3),
           pooled=dict(silW_B30_B33=pooled_silW,
                       eMotTop5_B31_B33=pooled_top5,
                       eMotBot5_B31_B33=pooled_bot5,
                       cutng25_8batch=pooled_ng25,
                       cutwA_9batch=pooled_wA),
           disclosures=san)
json.dump(out, open("l150/results_l150.json", "w"), indent=1)
print("L150 VERDICT WRITTEN")
