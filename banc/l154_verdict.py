# L154 verdict: Sapkal deprivation reads. PREREG l154/PREREG.md + ADDENDUM 2
# FIRST (registered before the run). Claim-carrier: paired per-seed sign of
# dom_freq(off) - dom_freq(on) over B34 (16 fresh); wet-lab direction =
# OFF SPEEDS (more positive deltas). Metric machinery copied from
# l94_verdict.py; CERTIFIED vs l94 STORED anchor values before any L154 read.
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0, BLK = 500, 500
SIGS = ("fL", "fR", "eL", "eR")
TS = np.arange(499, WIN, 10)
ARMS = ("b65", "off")           # b65 = on
B34 = list(range(3401, 3417))
ANCH = [801, 901]


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def dom_freq(x, lo=0.3):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    return float(f_hat), int(i == 0)  # L108: band-argmax-at-floor flag


def s_arrays(raw, a, s, pk):
    tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN] for c in SIGS}
    fL, fR, eL, eR = (tr[c] for c in SIGS)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    return SL, SR


def cells_of(raw, a, s, pk):          # l94_verdict form (duty07 reads)
    mm = raw[f"mm_{a}_{s}"][:WIN]
    SL, SR = s_arrays(raw, a, s, pk)
    q07 = np.zeros(len(TS), bool)
    for a0_, b0, f in SEGB:
        if f == 0.7:
            q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
    L07 = (SL[TS[q07]] >= .25)
    R07 = (SR[TS[q07]] >= .25)
    return dict(duty_07=round(float(np.nanmean(L07 & R07)), 3),
                duty07_L=round(float(np.nanmean(L07)), 3),
                duty07_R=round(float(np.nanmean(R07)), 3),
                S07_L=float(np.nanmean(SL[TS[q07]])),
                S07_R=float(np.nanmean(SR[TS[q07]])))


# ---------------- CERT (L85): machinery vs l94 STORED anchor values -------
z94 = np.load("l94/raw_l94.npz")
r94 = json.load(open("l94/results_l94.json"))
pin = r94["table_Ti"]["cfn"]["anchor"]
for s_, want in ((11, pin["11"]), (22, pin["22"]), (33, pin["33"])):
    got = cells_of(z94, "cfn", s_, "Ti")["duty_07"]
    assert got == want, ("CERT FAIL", s_, got, want)
print(f"CERT vs l94 stored (cfn duty_07 @ 11/22/33 == {pin}): PASS")
# dom_freq analytic self-test (parabola code copied verbatim from l94)
t = np.arange(WIN) * DT
for f0 in (0.7, 1.4):
    fh, _ = dom_freq(np.sin(2 * math.pi * f0 * t))
    assert abs(fh - f0) < 0.01, ("dom_freq self-test", f0, fh)
print("dom_freq analytic self-test (0.7/1.4 Hz): PASS")
# anchors: this run's on-arm == l150 stored (from l154_run.py; re-assert here)
ar = json.load(open("l154/anchors_run.json"))
assert ar["c0a154_pass"] and ar["c0a154_max"] == 0.0

# ---------------- reads ----------------------------------------------------
raw = np.load("l154/raw_l154.npz")
rows = {}
for a in ARMS:
    for s in ANCH + B34:
        mm = raw[f"mm_{a}_{s}"][:WIN]
        fb, at_floor = dom_freq(mm)                 # claim-carrier form
        fu, _ = dom_freq(mm, lo=0.0)                # untruncated (L108 diag)
        cells = {pk: cells_of(raw, a, s, pk) for pk in ("Ti", "Tr")}
        rows[(a, s)] = dict(dom_band=float(fb), dom_full=float(fu),
                            at_floor=bool(at_floor), **cells)

# paired claim-carrier: dom_freq(off) - dom_freq(on), B34
deltas = {s: rows[("off", s)]["dom_band"] - rows[("b65", s)]["dom_band"]
          for s in B34}
npos = sum(1 for v in deltas.values() if v > 0)
nneg = sum(1 for v in deltas.values() if v < 0)
nzero = sum(1 for v in deltas.values() if v == 0)
n = npos + nneg
k = min(npos, nneg)
pbin = min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) * 0.5 ** n)

# secondary: duty07 L/R asymmetry (duty->0.5 analog, ADDENDUM 2) + S07
asym = {a: {s: abs(rows[(a, s)]["Ti"]["duty07_L"]
                    - rows[(a, s)]["Ti"]["duty07_R"]) for s in B34}
        for a in ARMS}
asym_paired = [asym["off"][s] - asym["b65"][s] for s in B34]
S07 = {a: {pk: float(np.mean([rows[(a, s)][pk]["S07_L"]
                              for s in B34])) for pk in ("Ti", "Tr")}
       for a in ARMS}

out = dict(
    claim="paired sign dom_freq(off)-dom_freq(on), band form, full WIN",
    n_pos=npos, n_neg=nneg, n_zero=nzero, p_two_sided=pbin,
    wetlab_direction="off speeds (more positive deltas)",
    direction_met=bool(npos > nneg),
    deltas={str(s): deltas[s] for s in B34},
    dom_band_mean={a: float(np.mean([rows[(a, s)]["dom_band"]
                                     for s in B34])) for a in ARMS},
    dom_full_mean={a: float(np.mean([rows[(a, s)]["dom_full"]
                                     for s in B34])) for a in ARMS},
    at_floor_count={a: int(sum(rows[(a, s)]["at_floor"] for s in B34))
                    for a in ARMS},
    duty07_Ti={a: {s: rows[(a, s)]["Ti"] for s in B34} for a in ARMS},
    duty07_Tr={a: {s: rows[(a, s)]["Tr"] for s in B34} for a in ARMS},
    duty07_asym_Ti_mean={a: float(np.mean(list(asym[a].values())))
                         for a in ARMS},
    duty07_asym_paired_mean=float(np.mean(asym_paired)),
    S07_L_mean=S07,
    anchors={s: {a: rows[(a, s)]["dom_band"] for a in ARMS} for s in ANCH},
)
json.dump(out, open("l154/results_l154.json", "w"), indent=1)

print(f"\nCLAIM dom_freq(off)-dom_freq(on): +{npos} / -{nneg} / 0:{nzero} "
      f"| two-sided p={pbin:.4f} | wet-lab 'off speeds' "
      f"{'MET' if npos > nneg else 'NOT MET'}")
print(f"dom_band mean: on {out['dom_band_mean']['b65']:.3f} Hz -> "
      f"off {out['dom_band_mean']['off']:.3f} Hz | "
      f"untrunc {out['dom_full_mean']['b65']:.3f} -> "
      f"{out['dom_full_mean']['off']:.3f} | at-floor "
      f"{out['at_floor_count']['b65']}/{out['at_floor_count']['off']} of 16")
print(f"duty07 asym Ti (L/R): on {out['duty07_asym_Ti_mean']['b65']:.3f} -> "
      f"off {out['duty07_asym_Ti_mean']['off']:.3f} "
      f"(paired mean d {out['duty07_asym_paired_mean']:+.3f})")
for pk in ("Ti", "Tr"):
    print(f"S07 {pk}: on L {S07['b65'][pk]:+.3f} R "  # per-side R below
          f"{np.mean([rows[('b65', s)][pk]['S07_R'] for s in B34]):+.3f} -> "
          f"off L {S07['off'][pk]:+.3f} R "
          f"{np.mean([rows[('off', s)][pk]['S07_R'] for s in B34]):+.3f}")
print("anchors 801/901 dom_band on/off:",
      {s: (round(out['anchors'][s]['b65'], 3), round(out['anchors'][s]['off'], 3))
       for s in ANCH})
print("results_l154.json written")
