"""L34: rhythm-entrainment — does the L32 self-pacing cord rhythm LOCK to
periodic mechanosensory drive, or is it autonomous and drive-refractory?

L32 shipped a self-rhythmic cord (sustained bilateral DNg100, frozen
g .01 / beta 2 / d .05, arm A) at 1.2-1.4 Hz. L33 showed tonic DN bias cannot
steer it. The remaining modulation path is PHASIC external drive — the
body-feedback channel (L26: bridge-level feedback). This card drives the
mechano sensory sheet (L29 channel) sinusoidally on top of the regime and
asks whether the motor rhythm locks to the drive.

Claim levels pre-registered in l34/PREREG.md (C0..C4). P1-labeled
descriptive; CPU-only; no live changes.
"""
import json
import math
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 400
WIN = 6000           # 60 s
MEAS0 = 1500         # skip first 15 s of drive; measure last 45 s
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05          # l32 arm-A frozen, verbatim
FREQS = [0.7, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0, 2.5, 3.0]
AMPS = [0.01, 0.03, 0.1, 0.3]
LOCK_TOL = 0.03      # Hz
SNR_GATE = 5.0
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: subnetwork (l32/l33 verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()

nt = pd.read_feather("data/body-neurotransmitters-male-cns-v1.0.feather",
                     columns=["body", "consensus_nt"])
nt_map = dict(zip(nt["body"].astype(np.uint64).astype(str), nt["consensus_nt"]))
nt_names = np.array([str(nt_map.get(str(int(b)), "unknown")).lower() for b in ids])

w = pd.read_feather(
    "data/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
w = w[w["body_pre"].isin(idx) & w["body_post"].isin(idx)]
gsrc = w["body_pre"].map(idx).to_numpy(np.int64)
gdst = w["body_post"].map(idx).to_numpy(np.int64)
gw = w["weight"].to_numpy(np.float32)

cord = np.isin(sup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
dn_all = sup == "descending_neuron"
dn_into = np.zeros(len(ids), bool)
dn_into[gdst[cord[gsrc]]] = True
dn_into &= dn_all
keep = cord | dn_into

emask = keep[gsrc] & keep[gdst]
gsrc, gdst, gw = gsrc[emask], gdst[emask], gw[emask]
loc = -np.ones(len(ids), np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
lsup, ltyp, lside, lcls = sup[keep], typ[keep], side[keep], cls[keep]
lnt = nt_names[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)
log(f"sub nodes {n:,} | edges {len(gsrc):,} | {time.time()-t0:.0f}s")

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wa_vals = gw * signA[lsrc]
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy(Wa_vals.astype(np.float32)), (n, n)).coalesce().to_sparse_csr()

motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
tm = pd.Series(ltyp)
PAIRS = {}
for k in ("Ti", "Tr"):
    f = np.where(motor & tm.isin([f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (tm == f"{k} extensor MN"))[0]
    fL, fR = f[lside[f] == "L"], f[lside[f] == "R"]
    eL, eR = e[lside[e] == "L"], e[lside[e] == "R"]
    assert len(fL) and len(fR) and len(eL) and len(eR), (k, len(fL), len(fR))
    PAIRS[k] = dict(fL=fL, fR=fR, eL=eL, eR=eR)
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
assert len(mech) > 0
log(f"mech sensory cells in sub: {len(mech)}")


# ---------- rollout: regime + sinusoidal mech drive ----------
def run(seed, fd=None, amp=0.0):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D

    def step(cur, k):
        drive = torch.sparse.mm(Wb, cur) * G + I
        if fd is not None:
            drive[mech, 0] = drive[mech, 0] + amp * (0.5 + 0.5 * math.sin(2 * math.pi * fd * k * DT))
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for k in range(SETTLE):
        X = step(X, k)
    af = float((X > 0.05).float().mean())
    assert 0.01 < af < 0.9, f"op-point {af:.3f}"
    assert not torch.isnan(X).any(), "NaN"
    keys = ["fL", "fR", "eL", "eR"]
    tr = {k: {c: np.zeros(WIN, np.float32) for c in keys} for k in PAIRS}
    mm = np.zeros(WIN, np.float32)
    for i in range(WIN):
        X = step(X, SETTLE + i)
        for k, pools in PAIRS.items():
            for c in keys:
                tr[k][c][i] = X[pools[c]].mean()
        mm[i] = X[motor].mean()
    sl = slice(MEAS0, WIN)
    out = dict(af=af, S_pooled={}, rhythm={})
    for k, pools in PAIRS.items():
        a = tr[k]["fL"][sl] + tr[k]["fR"][sl]
        b = tr[k]["eL"][sl] + tr[k]["eR"][sl]
        out["S_pooled"][k] = float(-np.corrcoef(a, b)[0, 1]) if a.std() > 1e-6 and b.std() > 1e-6 else float("nan")
    out["_mm"] = mm[sl].copy()
    out["_tr"] = {k: {c: tr[k][c][sl].copy() for c in keys} for k in PAIRS}
    return out


def dom_freq(x):
    """Dominant freq 0.5-10 Hz with parabolic sub-bin interpolation."""
    z = x - x.mean()
    ps = np.abs(np.fft.rfft(z)) ** 2
    fr = np.fft.rfftfreq(len(z), DT)
    band = (fr >= 0.5) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            d = 0.5 * (y0 - y2) / den
            f_hat = fb[i] + d * (fb[1] - fb[0])
    peak_ratio = float(pb.max() / max(np.median(pb), 1e-30))
    return float(f_hat), peak_ratio, ps, fr


def power_at(ps, fr, f):
    """Power in the bin nearest f (Hz)."""
    i = int(np.argmin(np.abs(fr - f)))
    return float(ps[i])


def phase_R(x, fd):
    """Circular resultant of motor phase rel drive at fd, heterodyne +
    moving-average over exactly one drive period."""
    P = max(2, int(round(1.0 / (fd * DT))))
    tt = np.arange(len(x)) * DT
    z = x * np.exp(-2j * np.pi * fd * tt)
    ker = np.ones(P) / P
    zs = np.convolve(z, ker, mode="valid")
    R = float(np.abs(zs.mean()) / (np.abs(zs).mean() + 1e-30))
    ph = float(np.degrees(np.angle(zs.mean())))
    return R, ph


# ---------------- free run ----------------
# AMENDMENT (pre-grid, after probe l34/probe.out): l33's json rhythm metric
# read the FULL 60 s window (transient included) -> "1.33-1.43"; its saved
# npz traces (last 45 s) FFT to {0.800, 1.444, 1.422}. My rerun reproduces
# l33's traces BIT-FOR-BIT, so the substrate is identical and the difference
# is the WINDOW. C0 anchor moved to the pre-registered measurement window
# (last 45 s), per-seed, BEFORE any grid run.
ANCHOR = {11: 0.800, 22: 1.444, 33: 1.422}
free = {}
for s in SEEDS:
    o = run(s)
    f_hat, ratio, ps, fr = dom_freq(o["_mm"])
    S = o["S_pooled"]["Tr"]
    free[s] = dict(af=o["af"], f=f_hat, ratio=ratio, S_tr=S,
                   spec=None, ps=ps, fr=fr, mm=o["_mm"])
    log(f"free seed {s}: f {f_hat:.3f} Hz ratio {ratio:.0f} S(Tr) {S:+.2f} af {o['af']:.3f}")
assert all(abs(free[s]["f"] - ANCHOR[s]) <= 0.03 for s in SEEDS), "C0 anchor"
assert all(free[s]["S_tr"] >= 0.40 for s in SEEDS), "C0 S"
assert all(free[s]["ratio"] >= 100 for s in SEEDS), "C0 ratio"

# free-run power at each f_d (SNR denominator) + sham R
free_pd = {s: {fd: power_at(free[s]["ps"], free[s]["fr"], fd) for fd in FREQS} for s in SEEDS}
sham_R = {s: {fd: phase_R(free[s]["mm"], fd)[0] for fd in FREQS} for s in SEEDS}

# ---------------- grid ----------------
grid = []
for amp in AMPS:
    for fd in FREQS:
        per = []
        for s in SEEDS:
            o = run(s, fd=fd, amp=amp)
            f_hat, ratio, ps, fr = dom_freq(o["_mm"])
            pd_ = power_at(ps, fr, fd)
            snr = pd_ / max(free_pd[s][fd], 1e-30)
            R, ph = (phase_R(o["_mm"], fd) if snr >= SNR_GATE else (float("nan"),) * 2)
            per.append(dict(seed=s, f_mot=f_hat, ratio=ratio, S_tr=o["S_pooled"]["Tr"],
                            p_fd=pd_, snr=snr, R=R, ph=ph, af=o["af"],
                            mm=o["_mm"] if (fd in (0.7, 1.75) and amp in (0.03, 0.3)) else None))
        lock = [(abs(p["f_mot"] - fd) <= LOCK_TOL) for p in per]
        row = dict(amp=amp, fd=fd, seeds=per,
                   n_lock=int(sum(lock)), n_gate=int(sum(p["snr"] >= SNR_GATE for p in per)),
                   f_free={int(s): free[s]["f"] for s in SEEDS})
        grid.append(row)
        tagnote = ""
        for s, p in zip(SEEDS, per):
            if abs(free[s]["f"] - fd) >= 0.15 and p["snr"] >= SNR_GATE and abs(p["f_mot"] - fd) <= LOCK_TOL:
                tagnote = " LOCK?"
        log(f"A {amp:<5} fd {fd:<5}: f_mot " +
            " ".join(f"{p['f_mot']:.2f}" for p in per) +
            f" | gate {row['n_gate']}/3 | lock {row['n_lock']}/3 | S_Tr " +
            " ".join(f"{p['S_tr']:+.2f}" for p in per) +
            f" | snr " + " ".join(f"{p['snr']:.0f}" for p in per) +
            f" | R " + " ".join(f"{p['R']:.2f}" if p["R"] == p["R"] else "nan" for p in per) +
            tagnote + f" | {time.time()-t0:.0f}s")

# ---------------- verdict ----------------
def c2_cells():
    out = []
    for r in grid:
        if all(abs(free[s]["f"] - r["fd"]) >= 0.15 for s in SEEDS):
            k = sum(1 for p in r["seeds"]
                    if p["snr"] >= SNR_GATE and abs(p["f_mot"] - r["fd"]) <= LOCK_TOL)
            if k >= 2:
                out.append((r["amp"], r["fd"], k))
    return out


c2 = c2_cells()
c3 = []
for amp, fd, k in c2:
    r = next(x for x in grid if x["amp"] == amp and x["fd"] == fd)
    ok_r = sum(1 for p in r["seeds"] if p["R"] == p["R"] and p["R"] >= 0.5)
    ok_sham = all(sham_R[s][fd] < 0.3 for s in SEEDS)
    if ok_r >= 2 and ok_sham:
        c3.append((amp, fd))
lockset = {amp: sorted({r["fd"] for r in grid if r["amp"] == amp and r["n_lock"] >= 2
                        and all(abs(free[s]["f"] - r["fd"]) >= 0.15 for s in SEEDS)
                        and r["n_gate"] >= 2}) for amp in AMPS}
gate_any = any(r["n_gate"] >= 2 for r in grid)
free_peak_intact = True  # filled below
verdict = {
    "C0_substrate": True,
    "C1_survival": all(p["ratio"] >= 10 and 0.5 <= p["f_mot"] <= 10
                       for r in grid if r["amp"] == AMPS[0] for p in r["seeds"]),
    "C2_freq_lock_cells": c2,
    "C3_phase_lock_cells": c3,
    "C4_tongue": (len(lockset[AMPS[-1]]) > len(lockset[AMPS[0]])) if c2 else None,
    "lockset_by_amp": {str(a): v for a, v in lockset.items()},
    "gate_ever_passed": bool(gate_any),
    "forced_superposition": bool(gate_any and not c2),
    "n_runs": 3 + len(grid) * 3,
}
log("VERDICT " + json.dumps(verdict))

# ---------------- artifacts ----------------
np.savez_compressed(
    "l34/traces.npz",
    **{f"free_{s}": free[s]["mm"] for s in SEEDS},
    **{f"dr_A{r['amp']}_f{r['fd']}_{s}": p["mm"]
       for r in grid for s, p in zip(SEEDS, r["seeds"]) if p["mm"] is not None},
    **{f"tr_free_{s}_Tr_fL": free[s]["mm"] for s in []})
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, meas0=MEAS0,
                      freqs=FREQS, amps=AMPS, seeds=SEEDS, lock_tol=LOCK_TOL,
                      snr_gate=SNR_GATE, mech_cells=int(len(mech)),
                      nodes=int(n), edges=int(len(gsrc))),
            free={str(s): {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                           for k, v in free[s].items() if k not in ("ps", "fr", "spec", "mm")}
                  for s in SEEDS},
            sham_R={str(s): {str(fd): sham_R[s][fd] for fd in FREQS} for s in SEEDS},
            free_pd={str(s): {str(fd): free_pd[s][fd] for fd in FREQS} for s in SEEDS},
            grid=[{k: v for k, v in r.items() if k != "seeds"} |
                  {"seeds": [{kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv)
                              for kk, vv in p.items() if kk != "mm"} for p in r["seeds"]]}
                  for r in grid],
            verdict=verdict)
json.dump(dump, open("l34/results_l34.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l34/results_l34.json")
