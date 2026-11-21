"""L93 verdict: re-derives every registered read from raw_l93.npz (+ stored
l93/static.json). No new rollouts. PREREG l93/PREREG.md."""
import json

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
TS = np.arange(MEAS0, WIN, 10)
SIGS = ("fL", "fR", "eL", "eR")
SEEDS = [11, 22, 33]
z = np.load("l93/raw_l93.npz")
ar = json.load(open("l93/anchors_run.json"))
ST = json.load(open("l93/static.json"))

CAND = ["xl080_L_20", "d74b_R_20", "d105_R_20", "intr16_05", "intr16_20"]
SHAM_DN = ["shamdn_20a", "shamdn_20b"]
SHAM_INT = ["shamint_20a", "shamint_20b"]
DONOR = ["tidon_20"]
ARMS = ["base"] + CAND + DONOR + SHAM_DN + SHAM_INT


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def s_windows(arm, s, pk):
    fL = z[f"{pk}_fL_{arm}_{s}"][:WIN].astype(np.float64)
    fR = z[f"{pk}_fR_{arm}_{s}"][:WIN].astype(np.float64)
    eL = z[f"{pk}_eL_{arm}_{s}"][:WIN].astype(np.float64)
    eR = z[f"{pk}_eR_{arm}_{s}"][:WIN].astype(np.float64)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    return SL, SR


def q(seg_idx):
    a0, b0, _ = SEGB[seg_idx]
    return (TS >= a0 + MEAS0) & (TS < b0)


def dom_freq(x, lo=0.3):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            return float(fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0]))
    return float(fb[i])


SM = {}


def sides(arm, s, pk):
    key = (arm, s, pk)
    if key not in SM:
        SM[key] = s_windows(arm, s, pk)
    return SM[key]


# ---------------- duty cells (seg0 primary / seg2 persistence) ----------------
cells = {}
for a in ARMS:
    cells[a] = {}
    for s in SEEDS:
        SLTr, SRTr = sides(a, s, "Tr")
        SLTi, SRTi = sides(a, s, "Ti")
        m0, m2 = q(0), q(2)
        cells[a][s] = dict(
            Tr_d07L_0=round(float(np.nanmean(SLTr[TS[m0]] >= .25)), 3),
            Tr_d07R_0=round(float(np.nanmean(SRTr[TS[m0]] >= .25)), 3),
            Tr_d07L_2=round(float(np.nanmean(SLTr[TS[m2]] >= .25)), 3),
            Tr_SLmed_0=round(float(np.nanmedian(SLTr[TS[m0]])), 3),
            Tr_SRmed_0=round(float(np.nanmedian(SRTr[TS[m0]])), 3),
            Ti_d07L_0=round(float(np.nanmean(SLTi[TS[m0]] >= .25)), 3),
            f0=round(dom_freq(z[f"mm_{a}_{s}"][:2000].astype(np.float64)), 3))

# base pin cross-check vs static-derived pin (seg0+seg2 pooled there)
for s in SEEDS:
    SLTr, _ = sides("base", s, "Tr")
    m07 = q(0) | q(2)
    pin = round(float(np.nanmean(SLTr[TS[m07]] >= .25)), 3)
    want = ST["base_cfn_cells"][str(s)]["duty07_L"]
    assert pin == want, (s, pin, want)

# ---------------- C2 delivery: dm + fd on Tr pools ----------------
c2 = {}
for a in ARMS[1:]:
    for s in SEEDS:
        for pk in ("Tr_fL", "Tr_eL"):
            d = np.abs(z[f"{pk}_{a}_{s}"][:WIN] - z[f"{pk}_base_{s}"][:WIN])
            c2[f"dm_{pk}_{a}_{s}"] = float(d.max())
            c2[f"fd_{pk}_{a}_{s}"] = int(np.argmax(d > 0)) if (d > 0).any() else -1
# volley-window-only delivery (segregates direct drive from downstream spread)
for a in CAND:
    for s in SEEDS:
        dmw = 0.0
        for pk in ("Tr_fL", "Tr_eL"):
            d = np.abs(z[f"{pk}_{a}_{s}"][:2000] - z[f"{pk}_base_{s}"][:2000])
            dmw = max(dmw, float(d.max()))
        c2[f"dmwin_{a}_{s}"] = dmw

# ---------------- verdict assembly ----------------
def lift(a, s, k="Tr_d07L_0"):
    return round(cells[a][s][k] - cells["base"][s][k], 3)


res = dict(anchors=dict(c0_max=ar["c0_max"],
                        c1_af_equal=all(v for k, v in ar["c1"].items()
                                        if "af_equal" in k)),
           cells=cells, c2=c2)
table = {}
for a in ARMS:
    table[a] = dict(
        lift_L=[lift(a, s) for s in SEEDS],
        lift_R=[lift(a, s, k="Tr_d07R_0") for s in SEEDS],
        lift_L_seg2=[lift(a, s, k="Tr_d07L_2") for s in SEEDS],
        SLmed0=[round(cells[a][s]["Tr_SLmed_0"] - cells["base"][s]["Tr_SLmed_0"], 3)
                for s in SEEDS],
        TiL=[lift(a, s, k="Ti_d07L_0") for s in SEEDS],
        df0=[round(cells[a][s]["f0"] - cells["base"][s]["f0"], 3) for s in SEEDS],
        dm_Tr=[0.0, 0.0, 0.0] if a == "base" else
              [round(max(c2[f"dm_Tr_fL_{a}_{s}"], c2[f"dm_Tr_eL_{a}_{s}"]), 4)
               for s in SEEDS],
        vsat=[round(float(z[f"vsat_{a}_{s}"]), 3) for s in SEEDS],
    )
res["table"] = table

# P1 delivery ordering: intr16_20 >= every DN arm (Tr pools)
p1 = all(min(table["intr16_20"]["dm_Tr"]) >= max(table[a]["dm_Tr"])
         for a in ("xl080_L_20", "d74b_R_20", "d105_R_20"))
res["p1_delivery_ordering"] = bool(p1)

# E2 classification (registered)
def cls(a, sham_cls):
    lifts = table[a]["lift_L"]
    sh_max = max(max(table[sa]["lift_L"]) for sa in sham_cls)
    lands = min(table[a]["dm_Tr"]) > 0
    if not lands:
        return "BURIED-or-unreachable"
    if all(l >= .25 for l in lifts) and min(lifts) >= sh_max + .15:
        return "CONTENT"
    if max(lifts) <= sh_max + .10:
        return "PERTURBATION"
    if all(abs(l) < .10 for l in lifts):
        return "NO-STRUCTURE"
    return "MIXED"


verdict = {}
for a in CAND:
    sham_cls = SHAM_DN if a.endswith("_20") and a.startswith(("xl", "d7", "d1")) \
        else SHAM_INT
    verdict[a] = cls(a, sham_cls)
verdict["tidon_20"] = cls("tidon_20", SHAM_INT)
res["verdict"] = verdict

# E3 no-harm
res["e3_noharm"] = dict(
    TiL_ok=all(min(table[a]["TiL"]) > -0.25 for a in ARMS),
    lock_ok=all(abs(d) <= 0.10 for a in ARMS for d in table[a]["df0"]))

json.dump(res, open("l93/results_l93.json", "w"), indent=1)
print("C0", res["anchors"]["c0_max"], "| C1", res["anchors"]["c1_af_equal"],
      "| P1", p1, "| E3", res["e3_noharm"])
print(f"\n{'arm':<12} {'liftL(seg0)':<16} {'liftL(seg2)':<16} "
      f"{'SLmed0':<16} {'dm_Tr':<18} {'vsat':<14} verdict")
for a in ARMS:
    t = table[a]
    v = verdict.get(a, "-")
    print(f"{a:<12} {str(t['lift_L']):<16} {str(t['lift_L_seg2']):<16} "
          f"{str(t['SLmed0']):<16} {str(t['dm_Tr']):<18} {str(t['vsat']):<14} {v}")
print("\nfd Tr_fL (first-div) candidate arms:",
      {a: [c2[f"fd_Tr_fL_{a}_{s}"] for s in SEEDS] for a in CAND})
print("sham delivery dm_Tr:",
      {a: table[a]["dm_Tr"] for a in SHAM_DN + SHAM_INT + DONOR})
