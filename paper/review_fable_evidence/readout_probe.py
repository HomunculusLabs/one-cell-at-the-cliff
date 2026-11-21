# Reviewer's read-only probe: is the Ti antiphase-duty readout sensitive to the 0.1-Hz stimulus chop envelope?
# Re-implements l135_verdict.py S_of/duty_seeds exactly (validation row), then re-scores the SAME stored traces after
# (hp) FFT high-pass at 0.3 Hz, (on) restricting to 5-s windows lying fully inside a drive-ON block, (s14) the unchopped 1.4-Hz segment.
import numpy as np
WIN, MEAS0 = 6000, 500
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
TS = np.arange(499, WIN, 10)
z = np.load("/home/t3rpz/critters/peabrain-lab/banc/l135/raw_l135.npz")
AMPA = np.zeros(WIN)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + 2000:
        lo = seg0 + c * 900; AMPA[lo:min(lo + 500, seg0 + 2000)] = 1; c += 1
AMPA[2000:4000] = 1
def S_of(a, b):
    return float(-np.corrcoef(a, b)[0, 1]) if a.std() > 1e-6 and b.std() > 1e-6 else float("nan")
def hp(x, fc=0.3, dt=0.01):
    X = np.fft.rfft(x - x.mean()); f = np.fft.rfftfreq(len(x), dt); X[f < fc] = 0; return np.fft.irfft(X, len(x))
q07 = np.zeros(len(TS), bool); q14 = np.zeros(len(TS), bool)
for a0, b0, f in SEGB:
    if f == 0.7: q07 |= (TS >= a0 + MEAS0) & (TS < b0)
    else: q14 |= (TS >= a0 + MEAS0) & (TS < b0)
full_on = np.array([AMPA[t - 499:t + 1].min() > 0 for t in TS])       # window entirely inside a drive-ON block
mixed = np.array([0 < AMPA[t - 499:t + 1].mean() < 1 for t in TS])    # window straddles an on/off edge
print("0.7-Hz scoring windows:", int(q07.sum()), "| of which fully drive-ON:", int((q07 & full_on).sum()), "| straddling an on/off edge:", int((q07 & mixed).sum()), "| fully OFF:", int((q07 & ~full_on & ~mixed).sum()))
seeds = list(range(3001, 3017))
arms = ["full", "cutng19", "cutng23", "cutwA", "cutng25", "cutng25p", "cutng26", "cutng29", "cut58"]
def score(arm, side, mode):
    d = []
    for s in seeds:
        f = z[f"Ti_f{side}_{arm}_{s}"][:WIN].astype(float); e = z[f"Ti_e{side}_{arm}_{s}"][:WIN].astype(float)
        if mode == "hp": f, e = hp(f), hp(e)
        S = np.array([S_of(f[t - 499:t + 1], e[t - 499:t + 1]) for t in TS])
        m = {"orig": q07, "hp": q07, "on": q07 & full_on, "edge": q07 & mixed, "s14": q14}[mode]
        d.append(round(float(np.nanmean(S[m] >= .25)), 3))
    d = np.array(d); return int((d >= .5).sum()), round(float(d.mean()), 3), d
print(f"{'arm':9s} | " + " | ".join(f"{m:>16s}" for m in ("orig kR (mean)", "high-pass 0.3Hz", "ON-only windows", "edge windows", "1.4Hz unchopped")))
keep = {}
for a in arms:
    row = []
    for m in ("orig", "hp", "on", "edge", "s14"):
        k, mu, d = score(a, "R", m); row.append(f"{k:2d}/16 ({mu:.2f})"); keep[(a, m)] = d
    print(f"{a:9s} | " + " | ".join(f"{r:>16s}" for r in row))
for a in ("full", "cutwA", "cutng25", "cutng25p"):
    print(f"per-seed R duty sorted, {a:8s}:", " ".join(f"{v:.2f}" for v in sorted(keep[(a, 'orig')])))
# spectral content of the Ti_R pool traces: share of (non-DC) power below 0.3 Hz and at the 0.1-Hz bin
for a in ("full", "cutwA", "cutng25"):
    sh, s01 = [], []
    for s in seeds:
        for pool in ("f", "e"):
            x = z[f"Ti_{pool}R_{a}_{s}"][:WIN].astype(float); P = np.abs(np.fft.rfft(x - x.mean())) ** 2; f = np.fft.rfftfreq(WIN, 0.01)
            sh.append(P[(f > 0) & (f < 0.3)].sum() / P[f > 0].sum()); s01.append(P[np.argmin(abs(f - 0.1))] / P[f > 0].sum())
    print(f"Ti_R pools, arm {a:8s}: median share of power <0.3 Hz = {np.median(sh):.2f}; at 0.1-Hz bin = {np.median(s01):.3f}")
