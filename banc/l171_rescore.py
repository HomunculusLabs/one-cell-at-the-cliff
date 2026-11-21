"""L171: slow-line re-attribution + robustness panel. ZERO ROLLOUTS.

PREREG banc/l171/PREREG.md registered FIRST (branches A1/A2/A3 on the
attribution axis with a mandatory mech-off disclosure, B1/B2/B3/B4 on
the robustness axis with B4 checked first per re-score).

Everything here re-scores STORED traces (banc/l135/raw_l135.npz, 18
seeds, arms cutng25 / cutng25p). The published pipeline is
re-implemented and CERTIFIED against l135's stored table BEFORE any new
window or filter is read (L85 rule).
"""
import json
import math
import os
import re

import numpy as np

OUT = "l171"
os.makedirs(OUT, exist_ok=True)

# ---- constants, verbatim from banc/l135_run.py -------------------------
WIN, DT, RMAX = 6000, 0.01, 1.0
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
ENT_AMP = 0.1
MEAS0 = 500
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054
XOR = ("cutng25", "cutng25p")
HP_HZ = 0.3

log_lines = []


def log(s):
    print(s, flush=True)
    log_lines.append(str(s))


# ---------------- A. envelope attribution ------------------------------
def build_ampa():
    """l135_run.py lines 550-557, verbatim logic."""
    A = np.zeros(WIN, np.float64)
    for seg0, _, _ in SEGB:
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            A[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    A[2000:4000] = ENT_AMP
    return A


AMPA = build_ampa()
# P3: structure pins, derived not typed
on = AMPA > 0
edges = np.diff(on.astype(np.int8))
n_off_gaps = int((edges == -1).sum())
assert on[0] and on[-1], "envelope must start and end ON"
assert n_off_gaps == 4, f"expected 4 off-gaps, got {n_off_gaps}"
gap_bounds = [(int(a) + 1, int(b) + 1) for a, b in
              zip(np.where(edges == -1)[0], np.where(edges == 1)[0])]
assert all(b - a == 400 for a, b in gap_bounds), gap_bounds
n_on = int(on.sum())
assert n_on == WIN - 4 * 400, n_on

# own FFT of the envelope (mean removed; bins k/60 Hz)
sp = np.abs(np.fft.rfft(AMPA - AMPA.mean()))
freqs = np.fft.rfftfreq(WIN, d=DT)
BIN_HZ = freqs[1]
bin6 = 6
assert abs(freqs[bin6] - 0.100) < 1e-12, freqs[bin6]
chop_f = 1.0 / (900 * DT)                     # 9-s cycle fundamental
chop_bin_exact = chop_f / BIN_HZ
order = np.argsort(sp[1:])[::-1] + 1          # non-DC lines, descending
top5 = [int(i) for i in order[:5]]
is_local_max = bool(sp[bin6] > sp[bin6 - 1] and sp[bin6] > sp[bin6 + 1])
dom = int(order[0])
env = dict(
    bin_hz=BIN_HZ, bin6_hz=float(freqs[bin6]), chop_period_s=900 * DT,
    chop_fundamental_hz=chop_f, chop_bin_exact=chop_bin_exact,
    n_off_gaps=n_off_gaps, gap_bounds=gap_bounds, n_on_steps=n_on,
    dom_bin=dom, dom_hz=float(freqs[dom]), top5_bins=top5,
    top5_hz=[float(freqs[i]) for i in top5],
    top5_amp=[float(sp[i]) for i in top5],
    bin6_amp=float(sp[bin6]), bin5_amp=float(sp[5]), bin7_amp=float(sp[7]),
    bin6_local_max=is_local_max,
    bin6_rank=int(np.where(order == bin6)[0][0]) + 1,
    bin6_rel_dom=float(sp[bin6] / sp[dom]),
)
log(f"[A] envelope: bin width {BIN_HZ:.6f} Hz | chop {chop_f:.6f} Hz "
    f"= bin {chop_bin_exact:.4f} | dominant non-DC bin {dom} "
    f"({freqs[dom]:.4f} Hz)")
log(f"[A] top5 bins {top5} -> {[round(float(freqs[i]), 4) for i in top5]} Hz")
log(f"[A] bin6 (.100 Hz) amp {sp[bin6]:.4f} vs bin5 {sp[5]:.4f} / bin7 "
    f"{sp[7]:.4f} | local max {is_local_max} | rank {env['bin6_rank']} "
    f"| {env['bin6_rel_dom']:.3f} of dominant")

if env["bin6_local_max"] and bin6 in top5:
    A_BRANCH = "A1_envelope_line"
elif dom == int(round(chop_bin_exact)) or abs(dom - chop_bin_exact) <= 1.0:
    A_BRANCH = "A2_envelope_near" if abs(bin6 - dom) <= 1 else "A3_no_envelope_line"
else:
    A_BRANCH = "A3_no_envelope_line"
gap_c = np.array([(a + b) / 2 * DT for a, b in gap_bounds])
def vstrength(f):
    return float(abs(np.exp(2j * np.pi * f * gap_c).sum()) / len(gap_c))
env["gap_centers_s"] = [float(v) for v in gap_c]
env["vs_bin6"] = vstrength(freqs[bin6])
env["vs_chop"] = vstrength(chop_f)
log(f"[A] gap centers {list(np.round(gap_c,1))} s | 4-gap vector strength "
    f"at .100 Hz {env['vs_bin6']:.3f} vs at the 9-s chop line "
    f"{env['vs_chop']:.3f}")
log(f"[A] BRANCH {A_BRANCH}")

# ---------------- published pipeline (re-implemented) -------------------
PREF = {"Ti": ("f", "e")}


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def highpass(x):
    """Brick-wall rFFT high-pass at HP_HZ (DC included in the stop band)."""
    F = np.fft.rfft(x.astype(np.float64))
    F[freqs < HP_HZ] = 0.0
    return np.fft.irfft(F, n=WIN)


# P4: filter self-test BEFORE it touches a pool trace
t = np.arange(WIN) * DT
slow = np.sin(2 * np.pi * 0.05 * t)
fast = np.sin(2 * np.pi * 1.4 * t)
att = float(np.abs(highpass(slow)).max() / np.abs(slow).max())
keep = float(np.abs(highpass(fast) - fast).max() / np.abs(fast).max())
assert att < 0.01, f"slow not attenuated: {att}"
assert keep < 1e-6, f"fast not preserved: {keep}"
log(f"[P4] filter self-test: .05 Hz attenuation x{1/att:.0f}, "
    f"1.4 Hz rel err {keep:.2e}")


def s_arrays(raw, a, s, pk, hp=False):
    ag, bg = PREF[pk]
    tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN].astype(np.float64)
          for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
    if hp:
        tr = {c: highpass(v) for c, v in tr.items()}
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for tt in TS:
        SL[tt] = S_of(tr[f"{ag}L"][tt - 499:tt + 1], tr[f"{bg}L"][tt - 499:tt + 1])
        SR[tt] = S_of(tr[f"{ag}R"][tt - 499:tt + 1], tr[f"{bg}R"][tt - 499:tt + 1])
    return SL, SR


Q07 = np.zeros(len(TS), bool)
for a0, b0, f in SEGB:
    if f == 0.7:
        Q07 |= (TS >= a0 + MEAS0) & (TS < b0)
Q14 = np.zeros(len(TS), bool)
for a0, b0, f in SEGB:
    if f == 1.4:
        Q14 |= (TS >= a0 + MEAS0) & (TS < b0)
# P5
assert int(Q14.sum()) == 150, int(Q14.sum())
assert not (Q07 & Q14).any()
log(f"[P5] windows: q07 {int(Q07.sum())} points, q14 {int(Q14.sum())}, "
    f"overlap 0")


def side_k(raw, a, seeds, mask, hp=False):
    L, R = [], []
    for s in seeds:
        SL, SR = s_arrays(raw, a, s, "Ti", hp=hp)
        L.append(round(float(np.nanmean(SL[TS[mask]] >= .25)), 3))
        R.append(round(float(np.nanmean(SR[TS[mask]] >= .25)), 3))
    L, R = np.array(L), np.array(R)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3),
                perseedR=[float(v) for v in R], perseedL=[float(v) for v in L])


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ---------------- CERT: reproduce the stored published cells -----------
z = np.load("l135/raw_l135.npz")
allseeds = sorted({int(m.group(1)) for k in z.files
                   if (m := re.search(r"_(\d+)$", k))})       # P6
# the npz also carries the two forward-chain ANCHOR seeds (801/901 from
# the l133 lineage); the published B26 table is the 16-seed batch, which
# the stored Wilson bound for k=0 (ub .19360768 == n=16) identifies.
seeds = [s for s in allseeds if s >= 3000]
anchor_seeds = [s for s in allseeds if s < 3000]
assert len(allseeds) == 18 and anchor_seeds == [801, 901], allseeds
assert seeds == list(range(3001, 3017)), seeds
log(f"[P6] npz seeds {allseeds} -> B26 batch {seeds} (n={len(seeds)}), "
    f"anchors {anchor_seeds} excluded (stored k=0 Wilson ub identifies n=16)")

stored = json.load(open("l135/results_l135.json"))["table"]["Ti"]
cert = {}
pub = {}
for a in XOR:
    got = side_k(z, a, seeds, Q07)
    pub[a] = got
    st = stored[a]
    for f in ("kL", "kR", "meanL", "meanR"):
        assert got[f] == st[f], (a, f, got[f], st[f])
    lo, hi = wilson(got["kR"], len(seeds))
    assert abs(lo - st["lbR"]) < 1e-9 and abs(hi - st["ubR"]) < 1e-9
    cert[a] = dict(stored=dict((f, st[f]) for f in ("kL", "kR", "meanL", "meanR")),
                   lbR=lo, ubR=hi)
    log(f"[P1/P2 CERT] {a} q07 reproduced EXACT: kR {got['kR']}/{len(seeds)} "
        f"meanR {got['meanR']} kL {got['kL']} meanL {got['meanL']} "
        f"Wilson [{lo:.4f},{hi:.4f}]")

pub_contrast = round(pub["cutng25"]["meanR"] - pub["cutng25p"]["meanR"], 3)
pub_d_kR = pub["cutng25"]["kR"] - pub["cutng25p"]["kR"]
log(f"[CERT] published q07 contrast meanR {pub_contrast:+.3f}, d_kR {pub_d_kR}")

# ---------------- B/C: the two re-scores --------------------------------
panel = {"q07_published": {a: {k: v for k, v in pub[a].items()} for a in XOR}}
for name, mask, hp in (("fast_seg_1p4", Q14, False), ("highpass_0p3", Q07, True)):
    cells = {}
    for a in XOR:
        got = side_k(z, a, seeds, mask, hp=hp)
        lo, hi = wilson(got["kR"], len(seeds))
        got["lbR"], got["ubR"] = lo, hi
        cells[a] = got
        log(f"[{name}] {a}: kR {got['kR']}/{len(seeds)} meanR {got['meanR']} "
            f"[{lo:.3f},{hi:.3f}] | kL {got['kL']} meanL {got['meanL']}")
    c = cells["cutng25"]
    p = cells["cutng25p"]
    dR = np.array(c["perseedR"]) - np.array(p["perseedR"])
    cells["contrast"] = dict(
        d_meanR=round(c["meanR"] - p["meanR"], 3),
        d_kR=c["kR"] - p["kR"],
        paired_up=int((dR > 0).sum()), paired_down=int((dR < 0).sum()),
        paired_tie=int((dR == 0).sum()),
        paired_mean=round(float(dR.mean()), 3),
    )
    degen = bool(c["meanR"] <= .05 and p["meanR"] <= .05
                 and c["kR"] == 0 and p["kR"] == 0)
    ceil = bool(c["meanR"] >= .95 and p["meanR"] >= .95)
    cells["degenerate"] = degen or ceil
    cells["ordering_preserved"] = bool(c["meanR"] > p["meanR"] and c["kR"] >= p["kR"])
    cells["cleaner_meanR"] = bool(cells["contrast"]["d_meanR"] >= pub_contrast)
    cells["cleaner_kR"] = bool(cells["contrast"]["d_kR"] >= pub_d_kR)
    cells["cleaner"] = cells["cleaner_meanR"]
    panel[name] = cells
    log(f"[{name}] contrast {cells['contrast']} degenerate={degen or ceil} "
        f"ordering={cells['ordering_preserved']} cleaner={cells['cleaner']}")

live = [n for n in ("fast_seg_1p4", "highpass_0p3") if not panel[n]["degenerate"]]
if not live:
    B_BRANCH = "B4_degenerate"
elif all(panel[n]["ordering_preserved"] for n in live):
    if all(panel[n]["cleaner"] for n in live) and len(live) == 2:
        B_BRANCH = "B1_cleaner"
    else:
        B_BRANCH = "B2_preserved"
else:
    B_BRANCH = "B3_regime_dependent"
if len(live) == 1:
    B_BRANCH += f"|one_arm_degenerate:{[n for n in panel if n not in live and n != 'q07_published']}"
log(f"[B] live re-scores {live} -> BRANCH {B_BRANCH}")

res = dict(prereg="banc/l171/PREREG.md", zero_rollouts=True,
           n_seeds=len(seeds), seeds=seeds,
           envelope=env, a_branch=A_BRANCH, b_branch=B_BRANCH,
           cert=cert, pub_contrast=pub_contrast, pub_d_kR=pub_d_kR, panel=panel,
           mechoff_disclosure="l154.band 11/16 mech-off seeds sub-band: "
                              "the envelope explains the LINE POSITION and "
                              "(L162) its phase lock, not the existence of "
                              "sub-band power with the drive off")
json.dump(res, open(f"{OUT}/results.json", "w"), indent=1)
open(f"{OUT}/run.out", "w").write("\n".join(log_lines) + "\n")
log(f"wrote {OUT}/results.json")
