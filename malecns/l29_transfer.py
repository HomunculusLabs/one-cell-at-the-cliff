"""L29: the cord reflex arc as a FILTER (transfer function).

L21 verdict: interior transit delay is PATH-INTEGRAL (~9 base-tau stages
summed along the route; tau assignments per class do not move it). A cascade
of n first-order 50 ms stages is also a LOW-PASS with cutoff
f_c = f_0 * sqrt(2^(1/n) - 1), f_0 = 1/(2*pi*tau) ~ 3.18 Hz — for n~9 that
predicts f_c ~ 0.9 Hz: the homogeneous-tau cord should NOT carry a stride
rhythm (fly step ~5-10 Hz). This tick measures it directly.

Protocol: sinusoidal current onto the cord mechano sensory population
(L11/L16 event channel, amp form 2.0*(0.5+0.5*sin) so the peak equals the
L16 event amp), freqs {0.5,1,2,5,10,20} Hz; DT 10 ms for f<=5 (>=20 steps/
cycle), DT 2 ms for f>=10 (>=25 steps/cycle); 5 Hz run at BOTH DTs as the
mixing consistency check. Readouts: Ti/Tr flexor+extensor pool means and
all-motor mean; DFT exactly at the drive freq over an integer-cycle window
(last cycles), depth = sinusoid amplitude / mean level; phase lag vs drive;
amplitude at 2f as the in-run noise/distortion reference.
Arms: real x 2 seeds; L16 focused interior null (MS rewire sens->intr +
intr->intr, weights travel with source, ALL edges INTO motor frozen) x 3
draws x 1 seed at {0.5, 2, 10} Hz (the filter question is model-class; the
null checks routing sensitivity only). Descriptive, no live changes.

Gates:
  - 0.5 Hz depth well above the 2f noise floor on every pool (pool driven).
  - 5 Hz depth DT10 vs DT2 agree within seed spread (mixing validated).
  - cutoff = lowest f with depth < 0.5 * depth(0.5 Hz), per pool + all-motor.
"""
import json
import math
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, RMAX, BG, NOISE = 0.05, 1.0, 0.02, 0.01
GAIN, AMP = 0.8846, 2.0
SETTLE, CYCLES = 300, 8
FREQS = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
NULL_FREQS = [0.5, 2.0, 10.0]
NULL_DRAWS = 3
SEEDS = [11, 22]
NTRIES_FIT = [1.0, 2.0, 3.0, 4.0, 6.0, 9.0, 12.0]

os.makedirs("l29", exist_ok=True)
t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
M = len(motor)
typm = typ[motor]
cord_mech = np.where((sup == "vnc_sensory")
                     & pd.Series(cls).str.contains("mechano").to_numpy())[0]
print(f"cord mechano sensory {len(cord_mech)} | motor {M}", flush=True)

POOLS = {
    "Ti_flex": np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
    "Ti_ext": np.where(typm == "Ti extensor MN")[0],
    "Tr_flex": np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0],
    "Tr_ext": np.where(typm == "Tr extensor MN")[0],
    "all": np.arange(M),
}
for k, v in POOLS.items():
    assert len(v) > 0, k
    print(f"pool {k}: {len(v)} cells", flush=True)

# ---- L16 edge partition + rewire (verbatim) ----
rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
sens = np.zeros(N, bool); sens[sup == "vnc_sensory"] = True
intr = sup == "vnc_intrinsic"
blk = intr[rows] & (sens[cols] | intr[cols])
b_dst, b_src, b_w = rows[blk].copy(), cols[blk].copy(), vals[blk].copy()
nb_dst, nb_src, nb_val = rows[~blk], cols[~blk], vals[~blk]
print(f"interior block {blk.sum():,} | non-block {len(nb_dst):,} | {time.time()-t0:.0f}s", flush=True)


def rewire_block(rng, factor=8):
    dst, src, w = b_dst.copy(), b_src.copy(), b_w.copy()
    Mn = len(dst)
    pairs = set((dst.astype(np.int64) * N + src).tolist())
    ii = rng.integers(0, Mn, factor * Mn)
    jj = rng.integers(0, Mn, factor * Mn)
    done = 0
    for k in range(len(ii)):
        i, j = ii[k], jj[k]
        if i == j:
            continue
        a = dst[i] * N + src[j]
        b = dst[j] * N + src[i]
        if a in pairs or b in pairs:
            continue
        pairs.discard(dst[i] * N + src[i])
        pairs.discard(dst[j] * N + src[j])
        pairs.add(a); pairs.add(b)
        dst[i], dst[j] = dst[j], dst[i]
        done += 1
    assert len(pairs) == Mn
    return dst, src, w, done


def build_W(dst, src, w):
    idx = np.vstack([np.concatenate([nb_dst, dst]),
                     np.concatenate([nb_src, src])])
    vv = np.concatenate([nb_val, w])
    t = torch.sparse_coo_tensor(torch.from_numpy(idx).long(),
                                torch.from_numpy(vv), (N, N))
    return t.coalesce().to_sparse_csr()


def dt_for(f):
    return 0.002 if f >= 10 else 0.01


def run_freq(W_, seed, f, dt=None, cycles=CYCLES):
    dt = dt_for(f) if dt is None else dt
    per = int(round(1.0 / (f * dt)))
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)
    state = {"X": X}

    def step(I):
        drive = torch.sparse.mm(W_, state["X"]) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        state["X"] = state["X"] + (dt / TAU) * (t - state["X"])

    Z = torch.zeros(N, 1)
    Imean = Z.clone(); Imean[cord_mech] = AMP * 0.5
    for _ in range(SETTLE):
        step(Imean)
    n_tot = cycles * per
    rec = {k: np.zeros(n_tot, dtype=np.float32) for k in POOLS}
    I = Z.clone()
    for k in range(n_tot):
        I[cord_mech] = AMP * (0.5 + 0.5 * math.sin(2 * math.pi * f * k * dt))
        step(I)
        xm = state["X"][motor].squeeze(1)
        for pname, pidx in POOLS.items():
            rec[pname][k] = xm[pidx].mean().item()
    return rec, per, dt


def dft_amp(x, per, ncyc, harmonic=1):
    """Single-sided sinusoid amplitude at harmonic*drive freq over the last
    ncyc integer cycles; returns (amp, mean, phase_deg)."""
    seg = x[-ncyc * per:]
    Wn = len(seg)
    k = np.arange(Wn)
    w = 2 * np.pi * harmonic * k / per
    z = (2.0 / Wn) * np.sum(seg * np.exp(-1j * w))
    return float(np.abs(z)), float(seg.mean()), float(np.degrees(np.angle(z)))


def analyze(rec, per):
    out = {}
    ncyc = max(2, CYCLES - 2)
    for pname, x in rec.items():
        a1, mu, ph = dft_amp(x, per, ncyc, 1)
        a2, _, _ = dft_amp(x, per, ncyc, 2)
        out[pname] = {"amp": a1, "mean": mu, "depth": a1 / mu if mu > 1e-9 else 0.0,
                      "phase_deg": ph, "noise2f": a2}
    return out


# ---------------- real arm ----------------
results = {"real": [], "null": [], "meta": {
    "freqs": FREQS, "null_freqs": NULL_FREQS, "seeds": SEEDS,
    "cycles": CYCLES, "settle": SETTLE, "amp": AMP, "tau": TAU,
    "gain": GAIN, "dt_rule": "f>=10 -> 2ms else 10ms"}}
for seed in SEEDS:
    for f in FREQS:
        rec, per, dt = run_freq(W, seed, f)
        a = analyze(rec, per)
        results["real"].append({"seed": seed, "f": f, "dt": dt, "per": per, "pools": a})
        d = a["all"]
        print(f"real seed {seed} f {f:>4}Hz dt {dt*1000:.0f}ms | all depth "
              f"{d['depth']:.3f} ph {d['phase_deg']:+.0f} snr2f "
              f"{d['amp']/max(d['noise2f'],1e-9):6.1f} | "
              f"Ti_flex {a['Ti_flex']['depth']:.3f} Ti_ext {a['Ti_ext']['depth']:.3f}"
              f" | {time.time()-t0:.0f}s", flush=True)
# 5 Hz mixing consistency check at DT 2 ms
rec, per, dt = run_freq(W, SEEDS[0], 5.0, dt=0.002)
results["real"].append({"seed": SEEDS[0], "f": 5.0, "dt": dt, "per": per,
                        "pools": analyze(rec, per), "tag": "5Hz@dt2"})
print(f"5Hz@dt2ms all depth {results['real'][-1]['pools']['all']['depth']:.3f}", flush=True)

# ---------------- null arm (L16 focused interior rewire) ----------------
for draw in range(NULL_DRAWS):
    rng = np.random.default_rng(1000 + draw)
    dst, src, w, done = rewire_block(rng)
    Wn_ = build_W(dst, src, w)
    print(f"null draw {draw}: {done:,} swaps | {time.time()-t0:.0f}s", flush=True)
    for f in NULL_FREQS:
        rec, per, dt = run_freq(Wn_, SEEDS[0], f)
        a = analyze(rec, per)
        results["null"].append({"draw": draw, "f": f, "dt": dt, "per": per, "pools": a})
        print(f"null draw {draw} f {f:>4}Hz | all depth {a['all']['depth']:.3f} "
              f"ph {a['all']['phase_deg']:+.0f} | {time.time()-t0:.0f}s", flush=True)

# ---------------- summary: cutoffs + cascade fit ----------------
f0 = 1.0 / (2 * math.pi * TAU)


def pool_curve(entries, f, pname, field="depth"):
    return [e["pools"][pname][field] for e in entries if e["f"] == f]


summary = {"f0_hz": f0, "cutoffs": {}, "cascade_fit_n": {}, "phase": {}}
for pname in POOLS:
    lo = np.mean(pool_curve(results["real"], 0.5, pname))
    curve = np.array([np.mean(pool_curve(results["real"], f, pname)) for f in FREQS])
    below = [f for f, d in zip(FREQS, curve) if d < 0.5 * lo]
    summary["cutoffs"][pname] = {"depth_0.5Hz": float(lo),
                                 "half_depth_cutoff": below[0] if below else None,
                                 "curve": [float(x) for x in curve]}
    # fit n (continuous) to log depth ratio vs log |H|^n
    best = None
    H = np.array([1.0 / math.sqrt(1 + (f / f0) ** 2) for f in FREQS])
    y = np.log(np.maximum(curve, 1e-6) / max(curve[0], 1e-6))
    xL = np.log(H / H[0])
    nn = np.linspace(0.5, 15, 292)
    errs = [float(np.mean((y - n * xL) ** 2)) for n in nn]
    n_fit = float(nn[int(np.argmin(errs))])
    summary["cascade_fit_n"][pname] = {"n": n_fit, "rmse_log": min(errs)}
    ph = [float(np.mean(pool_curve(results["real"], f, pname, "phase_deg"))) for f in FREQS]
    summary["phase"][pname] = ph
    print(f"{pname}: depth@0.5 {lo:.3f} cutoff {below[0] if below else '>20Hz'} "
          f"n_fit {n_fit:.1f} (rmse {min(errs):.3f})", flush=True)

# null vs real at the null freqs
nullcmp = {}
for f in NULL_FREQS:
    nullcmp[str(f)] = {p: {
        "real": float(np.mean(pool_curve(results["real"], f, p))),
        "null_mean": float(np.mean([e["pools"][p]["depth"] for e in results["null"] if e["f"] == f])),
        "null_sd": float(np.std([e["pools"][p]["depth"] for e in results["null"] if e["f"] == f])),
    } for p in ["all", "Ti_flex", "Ti_ext"]}
summary["null_vs_real"] = nullcmp
# 5 Hz DT consistency
d10 = [e for e in results["real"] if e["f"] == 5.0 and e.get("dt", 0) == 0.01]
d2 = [e for e in results["real"] if e.get("tag") == "5Hz@dt2"][0]
summary["dt_consistency_5Hz"] = {
    "depth_dt10_seeds": [e["pools"]["all"]["depth"] for e in d10],
    "depth_dt2": d2["pools"]["all"]["depth"]}
with open("l29/results_l29.json", "w") as fh:
    json.dump(results | {"summary": summary}, fh, indent=1)
print(f"DONE {time.time()-t0:.0f}s", flush=True)
