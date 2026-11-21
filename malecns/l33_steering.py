"""L33: steering-modulated-rhythm — can the L32 self-pacing cord regime be
STEERED, or does a unilateral bias break the self-ordered antiphase?

L32 shipped: sustained bilateral DNg100 drive at frozen (g .01, beta 2,
d .05, arm A signs) -> real wiring self-orders antagonist antiphase,
S(Tr) +.49. The CX-gait endgame needs steering = MODULATION of that
rhythm (L31: CX owns steering, never the power stroke). This card adds a
unilateral tonic DNg95 bias (L24 ipsi flexor channel, excitatory) at
graded amps on top of the rhythm drive and measures:
  turn (L/R flexor mass asymmetry), pooled + per-side S, rhythm survival.

Claim levels pre-registered in l33/PREREG.md (C0..C4). P1-labeled
descriptive; CPU-only; no live changes.
"""
import json
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
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05          # l32 arm-A frozen, verbatim
AMPS = [0.25, 0.5, 1.0, 2.0, 4.0]     # x D (graded sweep)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: subnetwork (l32 verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
neuro_full = lab["somaNeuromere"].astype("string").to_numpy()

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
lsup, ltyp, lside = sup[keep], typ[keep], side[keep]
lnt = nt_names[keep]
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
    log(f"pair {k}: fL {len(fL)} fR {len(fR)} eL {len(eL)} eR {len(eR)}")
dng100 = np.where(ltyp == "DNg100")[0]
dng95L = np.where((ltyp == "DNg95") & (lside == "L"))[0]
dng95R = np.where((ltyp == "DNg95") & (lside == "R"))[0]
assert len(dng100) == 2 and len(dng95L) == 1 and len(dng95R) == 1
rng_np = np.random.default_rng(20261112)
dncells = np.where(lsup == "descending_neuron")[0]
pool = dncells[~np.isin(ltyp[dncells], ["DNg95", "DNg100"])]
rand_pairs = [rng_np.choice(pool, 2, replace=False) for _ in range(2)]
log(f"rand null pairs: {[list(map(int, p)) for p in rand_pairs]} | {time.time()-t0:.0f}s")


# ---------- rollout (l32 run() with generalized drive) ----------
def run(steer_cells, steer_amp, seed):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    if steer_cells is not None:
        I[np.asarray(steer_cells)] = steer_amp
    Z = torch.zeros(n, 1)

    def step(cur):
        drive = torch.sparse.mm(Wb, cur) * G + I
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for _ in range(SETTLE):
        X = step(X)
    af = float((X > 0.05).float().mean())
    assert 0.01 < af < 0.9, f"op-point {af:.3f}"
    assert not torch.isnan(X).any(), "NaN"
    T = WIN
    keys = ["fL", "fR", "eL", "eR"]
    tr = {k: {c: np.zeros(T, np.float32) for c in keys} for k in PAIRS}
    mm = np.zeros(T, np.float32)
    for i in range(T):
        X = step(X)
        for k, pools in PAIRS.items():
            for c in keys:
                tr[k][c][i] = X[pools[c]].mean()
        mm[i] = X[motor].mean()
    sl = slice(int(0.25 * T), T)
    out = dict(af=af, turn={}, S_pooled={}, S_side={}, depth={}, rhythm={})
    for k, pools in PAIRS.items():
        a = tr[k]["fL"][sl] + tr[k]["fR"][sl]
        b = tr[k]["eL"][sl] + tr[k]["eR"][sl]
        out["S_pooled"][k] = float(-np.corrcoef(a, b)[0, 1]) if a.std() > 1e-6 and b.std() > 1e-6 else np.nan
        for s_ in ("L", "R"):
            x1, x2 = tr[k][f"f{s_}"][sl], tr[k][f"e{s_}"][sl]
            out["S_side"][k + s_] = float(-np.corrcoef(x1, x2)[0, 1]) if x1.std() > 1e-6 and x2.std() > 1e-6 else np.nan
            out["depth"][k + s_ + "f"] = float(x1.max() - x1.min())
        out["turn"][k] = {}
    for k in PAIRS:
        for c in ("f", "e"):
            mL = tr[k][f"{c}L"][sl].mean()
            mR = tr[k][f"{c}R"][sl].mean()
            out["turn"][k][c] = float((mL - mR) / (mL + mR + 1e-9))
    x = mm - mm.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    band = (fr >= 0.5) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    out["rhythm"] = dict(ratio=float(pb[i] / max(np.median(pb), 1e-30)),
                         f=float(fb[i]))
    # post-hoc AC metrics (labeled): oscillation amplitude asymmetry + L/R phase
    for k in PAIRS:
        out.setdefault("ac", {})[k] = {}
        for c in ("f", "e"):
            aL = float(tr[k][f"{c}L"][sl].std())
            aR = float(tr[k][f"{c}R"][sl].std())
            out["ac"][k][f"amp_{c}"] = float((aL - aR) / (aL + aR + 1e-12))
        u, v = tr[k]["fL"][sl] - tr[k]["fL"][sl].mean(), tr[k]["fR"][sl] - tr[k]["fR"][sl].mean()
        cc = np.correlate(u, v, "full") / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-12)
        lag = int(np.argmax(np.abs(cc)) - (len(v) - 1))
        out["ac"][k]["lr_lag_s"] = float(lag * DT)
        out["ac"][k]["lr_cc"] = float(cc[lag + len(v) - 1])
    out["_traces"] = {k: {c: tr[k][c][sl].copy() for c in keys} for k in PAIRS}
    out["_mm"] = mm[sl].copy()
    return out


ARMS = [("base", None, 0.0)]
for a in AMPS:
    ARMS.append((f"Lx{a}", dng95L, D * a))
for a in (1.0, 4.0):
    ARMS.append((f"Rx{a}", dng95R, D * a))
for dr, p in enumerate(rand_pairs):
    ARMS.append((f"rand{dr}", p, D * 4.0))

res = {}
traces_keep = {}
pool_keep = {}
for name, cells, amp in ARMS:
    per = []
    for s in SEEDS:
        o = run(cells, amp, s)
        pool_keep.setdefault(name, []).append(o.pop("_traces"))
        per.append(dict(seed=s, **{k: v for k, v in o.items() if k != "_mm"}))
        traces_keep.setdefault(name, []).append(o["_mm"])
    res[name] = dict(steer=None if cells is None else [int(c) for c in cells],
                     amp=float(amp), seeds=per)
    t = np.mean([p["turn"] for p in per], 0) if False else None
    log(f"{name:>7} amp {amp:.4f}: turn_Ti " +
        " ".join(f"{p['turn']['Ti']['f']:+.3f}" for p in per) +
        " turn_Tr " + " ".join(f"{p['turn']['Tr']['f']:+.3f}" for p in per) +
        f" | S_Tr pool " + " ".join(f"{p['S_pooled']['Tr']:+.2f}" for p in per) +
        f" | rhy " + " ".join(f"{p['rhythm']['ratio']:.0f}@{p['rhythm']['f']:.2f}" for p in per) +
        f" | {time.time()-t0:.0f}s")

np.savez_compressed("l33/mm_traces.npz",
                    **{f"{name}_{i}": tr for name, ts in traces_keep.items()
                       for i, tr in enumerate(ts)},
                    **{f"pool_{name}_{i}_{k}_{c}": p[k][c]
                       for name, ps in pool_keep.items() for i, p in enumerate(ps)
                       for k in p for c in p[k]})
json.dump(res, open("l33/results_l33.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l33/results_l33.json")
