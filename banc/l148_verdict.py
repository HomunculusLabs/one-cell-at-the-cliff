"""L148 verdict: B-cert (raw_l135 B26 / raw_l142 B29 incl eAll / raw_l144
B30 incl sil1110_wA / raw_l145 B31) BEFORE any B32 read; SE-ID all-seed
identity gate BEFORE classes (PREREG A5); then anchors/P4/B32 table/
classes/H-branches/pooled. Criteria VERBATIM L118-L131, helper code
verbatim l145_verdict (L85 cert rule). PREREG l148/PREREG.md."""
import json
import math
import sys

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


# ---- L148 verdict (PREREG l148/PREREG.md): B-cert FIRST, then B32 ----
B32 = list(range(3349, 3365))
B31 = list(range(3333, 3349))
B30 = list(range(3317, 3333))
B29 = list(range(3301, 3317))
B26 = list(range(3001, 3017))
B25 = list(range(2901, 2917))
B24 = list(range(2801, 2817))
B21 = list(range(2501, 2517))
ARMS148 = ["full", "b65", "cutwA", "cutng25", "eAll", "se0"]
LADDER148 = [("0", "full"), ("24", "cutwA"), ("eAll", "eAll"),
             ("se0", "se0"), ("25", "cutng25")]
z148 = np.load("l148/raw_l148.npz")
z145 = np.load("l145/raw_l145.npz")
z144 = np.load("l144/raw_l144.npz")
z142 = np.load("l142/raw_l142.npz")
z135 = np.load("l135/raw_l135.npz")
z133 = np.load("l133/raw_l133.npz")
z131 = np.load("l131/raw_l131.npz")
z126 = np.load("l126/raw_l126.npz")
ar = json.load(open("l148/anchors_run.json"))
r135 = json.load(open("l135/results_l135.json"))
r142 = json.load(open("l142/results_l142.json"))
r144 = json.load(open("l144/results_l144.json"))
r145 = json.load(open("l145/results_l145.json"))
MASS = r142["static"]["arm_mass_frac_dn"]

# ---- B-cert BEFORE any B32 read (L85 rule), FOUR certs ----
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
for a in ("cutwA", "cutng25"):
    want = r145["table"]["Ti"][a]
    got = side_k(z145, a, B31, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append(("l145", a, kk, got[kk], want[kk]))
assert not bcert_fail, ("B-cert FAIL (no B32 read)", bcert_fail[:5])
print("B-cert vs results_l135 (B26) + l142 (B29 eAll/cutwA/cutng25) + "
      "l144 (B30 cutwA/cutng25/sil1110_wA) + l145 (B31 cutwA/cutng25) "
      "Ti tables: PASS")

# ---- P0 anchors (gate booleans ONLY, L59 rule) ----
p0 = dict(c0a_pass=ar["c0a148_pass"], c0a_max=ar["c0a148_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"],
          g_eall_stored_exact=ar["g_eall_stored_exact"],
          fc142_pass=ar["fc142_pass"], fc142_max=ar["fc142_max"],
          seid_pass=ar["seid_pass"], seid_max=ar["seid_max"],
          a_eall_max=ar["a_eall_max"])
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cutwA_stored_exact"]
                  and p0["g_cutng25_stored_exact"] and p0["g_eall_stored_exact"]
                  and p0["fc142_pass"] and p0["seid_pass"])
print("P0 anchors (C0A-148 + stored gains + FC-142 + SE-ID@801/901):",
      "PASS" if p0["pass"] else "FAIL",
      f"(c0a {p0['c0a_max']:.1e} | FC-142 {p0['fc142_max']:.1e} | "
      f"SE-ID {p0['seid_max']:.1e})")

# ---- SE-ID on ALL seeds (PREREG A5): BEFORE any class read ----
_poolkeys = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _poolkeys.append(f"{_pk}_{_c}{_s}")
ID_KEYS = ["mm", "xm"] + _poolkeys
seid_all = {}
for s in B32:
    for key in ID_KEYS:
        d = float(np.abs(z148[f"{key}_se0_{s}"]
                         - z148[f"{key}_eAll_{s}"]).max())
        seid_all[f"{key}_{s}"] = d
    seid_all[f"af_{s}"] = abs(float(z148[f"af_se0_{s}"])
                              - float(z148[f"af_eAll_{s}"]))
seid_all_max = max(seid_all.values())
h_id = dict(arm="se0", n_seeds=16, n_keys=len(ID_KEYS) + 1,
            max_abs_diff=seid_all_max,
            bit_identical=bool(seid_all_max == 0.0),
            note="se0 == eAll on EVERY stored channel/seed: activity-"
                 "silence is a strict SUBSET of edge-removal; the "
                 "silW->eAll remainder is settle-history/edge-carried"
            if seid_all_max == 0.0 else
            "H-DENOM branch: isolated cell's presence/noise/denominator "
            "carries readout mass (or clamp wiring) — per-key table, "
            "no class forced")
print(f"SE-ID all-B32: max|d| {seid_all_max:.1e} -> "
      f"{'H-ID PASS (bit-identical)' if seid_all_max == 0.0 else 'H-DENOM'}")
if seid_all_max != 0.0:
    bad = {k: v for k, v in seid_all.items() if v != 0.0}
    json.dump(dict(design="L148 SE-ID FAIL — H-DENOM branch, no class read",
                   h_id=h_id, nonzero=bad, anchors=ar),
              open("l148/results_l148_seid_fail.json", "w"), indent=1)
    print("H-DENOM nonzero keys:", json.dumps(
        dict(list(bad.items())[:10])))
    sys.exit(2)

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z148[f"af_{a}_{s}"]) for s in B32])), 6)
           for a in ARMS148}
af_range_ok = all(0.01 < float(z148[f"af_{a}_{s}"]) < 0.9
                  for a in ARMS148 for s in B32)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band),
          af_mean=af_mean, e_band_ok=ar["e_band_ok"],
          new_stairs=ar["new_stairs"])
print("P4", json.dumps({k: p4[k] for k in ("af_range_ok", "b65_band",
                                           "e_band_ok")}))

# ---- B32 per-side duty table (5 pairs x 6 arms) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS148:
        t = side_k(z148, a, B32, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B32 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS148:
        t = table[pk][a]
        print(f"{pk} {a:8s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Ti ladder classification (criteria VERBATIM L118-L131) ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z148, "full", B32, "Ti")
_, RwA = duty_seeds(z148, "cutwA", B32, "Ti")
_, ReAll = duty_seeds(z148, "eAll", B32, "Ti")
dose = {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {}}


def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


cls, killmap = {}, {}
for kk, a in LADDER148:
    t = table["Ti"][a]
    _, Rd = duty_seeds(z148, a, B32, "Ti")
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
    print(f"Ti {kk:>5s} ({a:8s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | dR_wA "
          f"{legs['mean_paired_dR_vs_wA']:+.3f} n_up_wA "
          f"{legs['n_up_vs_wA']:2d}/16 -> "
          f"{'KILL' if kill else 'no-kill'}"
          f"{'/RESTORE' if _restore(t) else ''}"
          f"{'/SUPER' if _super(t) else ''}"
          f"{'/PARTIAL' if _partial(t) else ''}")
dose["m0"] = m0

# ---- H-branch verdicts (registered BOTH directions) ----
c_eall, c_se0, c_25 = cls["eAll"], cls["se0"], cls["25"]
cls_of = lambda c: ("KILL" if c["kill"] else
                    "SUPER" if c["super"] else
                    "RESTORE" if c["restore"] else
                    "PARTIAL" if c["partial"] else "NONE")
h_replic = dict(arm="eAll", b32_class=cls_of(c_eall), meanR=c_eall["meanR"],
                kR=c_eall["kR"],
                super_replicates=bool(c_eall["super"]),
                note="endpoint SUPER replicates on the first fresh batch "
                     "(.745/14 B29 -> fresh-batch read; pooled carries)"
                if c_eall["super"] else
                "B32 re-draws eAll out of SUPER — single-batch class was "
                "batch-drawn (L88/L90); pooled B29+B32 carries the verdict")
dR_eall = ReAll - RwA
h_grid = dict(
    silW_b30=dict(meanR=r144["table"]["Ti"]["sil1110_wA"]["meanR"],
                  kR=r144["table"]["Ti"]["sil1110_wA"]["kR"],
                  batch="B30 (l144, ctx)"),
    eAll_b29=dict(meanR=r142["table"]["Ti"]["eAll"]["meanR"],
                  kR=r142["table"]["Ti"]["eAll"]["kR"],
                  batch="B29 (l142, ctx)"),
    eAll_b32=dict(meanR=c_eall["meanR"], kR=c_eall["kR"]),
    se0_b32=dict(meanR=c_se0["meanR"], kR=c_se0["kR"]),
    mean_paired_dR_eAll_vs_wA_B32=round(float(dR_eall.mean()), 3),
    remainder_note="silW(.622 B30) < eAll(.745 B29): the .09-.12 remainder "
                   "is settle-history/edge-carried (se0==eAll bitwise), "
                   "NOT window activity on top of the cut")
flips = [kk for kk in cls if cls[kk]["super"] or cls[kk]["restore"]]
p3 = dict(flipping_arms=flips,
          tiL_dead={kk: dict(meanL=cls[kk]["meanL"], kL=cls[kk]["kL"])
                    for kk in flips},
          note="Ti_L dies with every flipping arm (crossed law holds)"
          if all(cls[kk]["kL"] <= 2 for kk in flips) else
          "Ti_L SURVIVES a flipping arm — disclosed")
for nm, h in (("H-ID", h_id), ("H-REPLIC", h_replic), ("H-GRID", h_grid),
              ("P3", p3)):
    print(nm, json.dumps(h))

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


pooled_eall = pooled([z142, z148], "eAll", [B29, B32])
pooled_ng25 = pooled([z131, z133, z135, z142, z144, z145, z148], "cutng25",
                     [B24, B25, B26, B29, B30, B31, B32])
pooled_wA = pooled([z126, z131, z133, z135, z142, z144, z145, z148],
                   "cutwA", [B21, B24, B25, B26, B29, B30, B31, B32])
print("pooled eAll B29+B32:", json.dumps(pooled_eall))
print("pooled cutng25 B24+B25+B26+B29+B30+B31+B32:", json.dumps(pooled_ng25))
print("pooled cutwA B21+B24+B25+B26+B29+B30+B31+B32:", json.dumps(pooled_wA))

# ---- disclosures + sanity ----
san = dict(
    full_class_batch_drawn=dict(meanR=m0, kR=table["Ti"]["full"]["kR"],
        note="class labels read vs m0/paired legs, not bare bands (L109)"),
    batch_rename="card 'fresh B31' -> B32 (L145 shipped B31 11-19; "
                 "L44 #6, PREREG disclosure)",
    se0_no_independent_gain="graph-identity af-match to eAll (l144 silW "
                            "form); settle clamp-free and identical",
    clamp_window_only="l137 form: X[1110] zeroed from window step 0 only",
    silW_single_batch="sil1110_wA .622/14 stands on B30 (l144, ctx)",
    h_id_derived="H-ID prediction machinery-derived (no out-edges + no "
                 "membership); payload = all-seed falsifiable gate + "
                 "first eAll replication + pooled growth (L55 guard)",
    no_renorm_arm="lineage build has no in-degree renorm")
print("watch: Tr_R wA", table["Tr"]["cutwA"]["meanR"], "eAll",
      table["Tr"]["eAll"]["meanR"])
print("sanity b65 Ti kL/kR", table["Ti"]["b65"]["kL"], table["Ti"]["b65"]["kR"])

out = dict(design="L148 silent-and-edgeless identity arm "
                  "(PREREG l148/PREREG.md)",
           anchors=ar, p0=p0, seid_all_max=seid_all_max, p4=p4,
           table=table, dose=dose, classes=cls,
           hypotheses=dict(H_ID=h_id, H_REPLIC=h_replic, H_GRID=h_grid,
                           P3=p3),
           pooled=dict(eAll_B29_B32=pooled_eall,
                       cutng25_7batch=pooled_ng25,
                       cutwA_8batch=pooled_wA),
           disclosures=san)
json.dump(out, open("l148/results_l148.json", "w"), indent=1)
print("L148 VERDICT WRITTEN")
