"""L145 verdict: B-cert (raw_l135 B26 {cutwA,cutng25} AND raw_l142 B29
{eOutMot,cutwA,cutng25}) BEFORE any B31 read, then anchors/P4/B31
table/dose/H-branches/pooled. Criteria VERBATIM L118-L131, helper code
verbatim l142_verdict (L85 cert rule). PREREG l145/PREREG.md."""
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


# ---- L145 verdict (PREREG l145/PREREG.md): B-cert FIRST, then B31 ----
B31 = list(range(3333, 3349))
B30 = list(range(3317, 3333))
B29 = list(range(3301, 3317))
B26 = list(range(3001, 3017))
B25 = list(range(2901, 2917))
B24 = list(range(2801, 2817))
B21 = list(range(2501, 2517))
ARMS145 = ["full", "b65", "cutwA", "cutng25",
           "eOutMot", "eMotTop5", "eMotBot5", "eMotIn"]
LADDER145 = [("0", "full"), ("24", "cutwA"), ("bot5", "eMotBot5"),
             ("top5", "eMotTop5"), ("mot", "eOutMot"),
             ("motIn", "eMotIn"), ("25", "cutng25")]
z145 = np.load("l145/raw_l145.npz")
z144 = np.load("l144/raw_l144.npz")
z142 = np.load("l142/raw_l142.npz")
z135 = np.load("l135/raw_l135.npz")
z133 = np.load("l133/raw_l133.npz")
z131 = np.load("l131/raw_l131.npz")
z126 = np.load("l126/raw_l126.npz")
ar = json.load(open("l145/anchors_run.json"))
r135 = json.load(open("l135/results_l135.json"))
r142 = json.load(open("l142/results_l142.json"))
S145 = json.load(open("l145/static.json"))

# ---- B-cert BEFORE any B31 read (L85 rule), TWO certs ----
bcert_fail = []
for a in ("cutwA", "cutng25"):
    want = r135["table"]["Ti"][a]
    got = side_k(z135, a, B26, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append(("l135", a, kk, got[kk], want[kk]))
for a in ("eOutMot", "cutwA", "cutng25"):
    want = r142["table"]["Ti"][a]
    got = side_k(z142, a, B29, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append(("l142", a, kk, got[kk], want[kk]))
assert not bcert_fail, ("B-cert FAIL (no B31 read)", bcert_fail[:5])
print("B-cert vs results_l135 (B26 cutwA/cutng25) + results_l142 "
      "(B29 eOutMot/cutwA/cutng25) Ti tables: PASS")

# ---- P0 anchors (gate booleans ONLY, L59 rule) ----
p0 = dict(c0a_pass=ar["c0a142_pass"], c0a_max=ar["c0a142_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"],
          g_emot_exact=ar["g_emot_exact"], fc142_pass=ar["fc142_pass"],
          fc142_max=ar["fc142_max"])
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cutwA_stored_exact"]
                  and p0["g_cutng25_stored_exact"] and p0["g_emot_exact"]
                  and p0["fc142_pass"])
print("P0 anchors (C0A-145 + stored gains + FC-142):",
      "PASS" if p0["pass"] else "FAIL", f"(C0A max {p0['c0a_max']:.1e} | "
      f"FC-142 max {p0['fc142_max']:.1e})")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z145[f"af_{a}_{s}"]) for s in B31])), 6)
           for a in ARMS145}
af_range_ok = all(0.01 < float(z145[f"af_{a}_{s}"]) < 0.9
                  for a in ARMS145 for s in B31)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band),
          af_mean=af_mean, e_band_ok=ar["e_band_ok"],
          new_stairs=ar["new_stairs"])
print("P4", json.dumps({k: p4[k] for k in ("af_range_ok", "b65_band",
                                           "e_band_ok")}))

# ---- B31 per-side duty table (5 pairs x 8 arms) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS145:
        t = side_k(z145, a, B31, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B31 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS145:
        t = table[pk][a]
        print(f"{pk} {a:8s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Ti ladder classification (criteria VERBATIM L118-L131) ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z145, "full", B31, "Ti")
_, RwA = duty_seeds(z145, "cutwA", B31, "Ti")
_, Rmot = duty_seeds(z145, "eOutMot", B31, "Ti")
_, Rtop5 = duty_seeds(z145, "eMotTop5", B31, "Ti")
_, Rbot5 = duty_seeds(z145, "eMotBot5", B31, "Ti")
dose = {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {}}


def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


cls, killmap = {}, {}
for kk, a in LADDER145:
    t = table["Ti"][a]
    _, Rd = duty_seeds(z145, a, B31, "Ti")
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
                   mass=S145["arm_mass_frac_dn"].get(a))
    print(f"Ti {kk:>6s} ({a:8s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | dR_wA "
          f"{legs['mean_paired_dR_vs_wA']:+.3f} n_up_wA "
          f"{legs['n_up_vs_wA']:2d}/16 -> "
          f"{'KILL' if kill else 'no-kill'}"
          f"{'/RESTORE' if _restore(t) else ''}"
          f"{'/SUPER' if _super(t) else ''}"
          f"{'/PARTIAL' if _partial(t) else ''}")
dose["m0"] = m0

# ---- H-branch verdicts (registered BOTH directions) ----
c_mot, c_top5, c_bot5 = cls["mot"], cls["top5"], cls["bot5"]
c_motin, c_25 = cls["motIn"], cls["25"]
cls_of = lambda c: ("KILL" if c["kill"] else
                    "SUPER" if c["super"] else
                    "RESTORE" if c["restore"] else
                    "PARTIAL" if c["partial"] else "NONE")
middle = ((.50 < c_mot["meanR"] < .60) or (8 < c_mot["kR"] < 12)) and \
    not c_mot["super"] and not c_mot["partial"] and not c_mot["kill"]
h_replic = dict(arm="eOutMot", b31_class=cls_of(c_mot), meanR=c_mot["meanR"],
                kR=c_mot["kR"], middle_replicates=bool(middle),
                note="middle is a stable dose step" if middle else
                "B31 lands in a class band — middle was batch-drawn "
                "(L88/L90); pooled read carries the verdict")
d_top5 = Rtop5 - RwA
d_bot5 = Rbot5 - RwA
d_mot = Rmot - RwA
sign_n = int((d_top5 > d_bot5).sum())
prop_half = bool(d_mot.mean() > 0 and d_top5.mean() >= 0.5 * d_mot.mean())
h_dose = dict(order_sign_count=sign_n, order_pass=bool(sign_n >= 12),
              mean_dR_top5=round(float(d_top5.mean()), 3),
              mean_dR_bot5=round(float(d_bot5.mean()), 3),
              mean_dR_mot=round(float(d_mot.mean()), 3),
              proportionality_half_mass=prop_half,
              fires=bool(sign_n >= 12 and prop_half),
              note="graded within-sheet: top5 > bot5 per-seed and top5 "
                   "carries >= half the motor arm's paired lift" if
              (sign_n >= 12 and prop_half) else
              "ordering fails / proportionality fails — within-sheet "
              "re-draw at the 5-edge scale (L115/L118 class)")
h_combo = dict(arm="eMotIn", b31_class=cls_of(c_motin),
               meanR=c_motin["meanR"], kR=c_motin["kR"],
               super_predicted=bool(cls_of(c_motin) == "SUPER"),
               note="motor+in combo supers (eIn redundancy confirmed on "
                    "fresh batch)" if cls_of(c_motin) == "SUPER" else
               "combo fails to super while eIn alone did on B29 — "
               "batch/subset interaction, disclosed")
flips = [kk for kk in cls if cls[kk]["super"] or cls[kk]["restore"]]
p3 = dict(flipping_arms=flips,
          tiL_dead={kk: dict(meanL=cls[kk]["meanL"], kL=cls[kk]["kL"])
                    for kk in flips},
          note="Ti_L dies with every flipping arm (crossed law holds)"
          if all(cls[kk]["kL"] <= 2 for kk in flips) else
          "Ti_L SURVIVES a flipping arm — dose split reaches L differently")
for nm, h in (("H-REPLIC", h_replic), ("H-DOSE", h_dose),
              ("H-COMBO", h_combo), ("P3", p3)):
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


pooled_mot = pooled([z142, z145], "eOutMot", [B29, B31])
pooled_ng25 = pooled([z131, z133, z135, z142, z144, z145], "cutng25",
                     [B24, B25, B26, B29, B30, B31])
pooled_wA = pooled([z126, z131, z133, z135, z142, z144, z145], "cutwA",
                   [B21, B24, B25, B26, B29, B30, B31])
print("pooled eOutMot B29+B31:", json.dumps(pooled_mot))
print("pooled cutng25 B24+B25+B26+B29+B30+B31:", json.dumps(pooled_ng25))
print("pooled cutwA B21+B24+B25+B26+B29+B30+B31:", json.dumps(pooled_wA))

# ---- disclosures + sanity ----
san = dict(
    full_class_batch_drawn=dict(meanR=m0, kR=table["Ti"]["full"]["kR"],
        note="class labels read vs m0/paired legs, not bare bands (L109)"),
    new_arms_single_batch="eMotTop5/eMotBot5/eMotIn: B31 only, disclosed",
    eOutMot_pooled="B29+B31 n=32 (recomputed from stored raws)",
    tie_break="two syn-8 ties broken by global position (PREREG)",
    no_renorm_arm="lineage build has no in-degree renorm",
    masses=S145["arm_mass_frac_dn"],
    motor_targets=dict(top5=[e["dst_type"] for e in
                             S145["motor_edges_ranked"][:5]],
                       bot5=[e["dst_type"] for e in
                             S145["motor_edges_ranked"][5:]]))
tr_R = table["Tr"]; sr = table["Sr"]
print("watch: Tr_R wA", tr_R["cutwA"]["meanR"], "top5",
      tr_R["eMotTop5"]["meanR"], "| Sr_R wA", sr["cutwA"]["meanR"],
      "top5", sr["eMotTop5"]["meanR"])
print("sanity b65 Ti kL/kR", table["Ti"]["b65"]["kL"], table["Ti"]["b65"]["kR"])

out = dict(design="L145 eOutMot middle-dose (PREREG l145/PREREG.md)",
           static=S145, anchors=ar, p0=p0, p4=p4, table=table, dose=dose,
           classes=cls, hypotheses=dict(H_REPLIC=h_replic, H_DOSE=h_dose,
                                        H_COMBO=h_combo, P3=p3),
           pooled=dict(eOutMot_B29_B31=pooled_mot,
                       cutng25_6batch=pooled_ng25,
                       cutwA_7batch=pooled_wA),
           disclosures=san)
json.dump(out, open("l145/results_l145.json", "w"), indent=1)
print("L145 VERDICT WRITTEN")
