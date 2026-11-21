"""L45a probe: what mediates the E1-clamp disruption that coreAll cancels?

c_E1 alone: f slows 3/3, S inverts 2/3. c_coreAll (36 cells incl. E1):
f + S intact, ratio 3-8x base. Mediator candidates = types clamped in
coreAll but not in c_E1: {E2, I1, I2, E3, X464}; flexor-in-weight-heavy
ones are I2 (.0201), E3 (.0425), X464 (.0264). Arms (paired noise, same
seeds/window as l45_prune):
  base / c_E1 / c_I2E3 (the flexor pair, no E1) / c_E1I2E3 (mediator test)
  / c_E1X464 (the two big singletons together)
PASS-form mediation: c_E1I2E3 (or c_E1X464) restores f/S toward base while
c_E1's disruption remains -> the disruption rides the un-clamped partner.
Deterministic; CPU-only; no live changes.
"""
import json
import time

import numpy as np
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN = 400, 11000
CL0, CL1 = 4000, 9000
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05
t0 = time.time()


def log(*a):
    print(*a, flush=True)


import pandas as pd

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()

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
lsup, ltyp, lside = sup[keep], typ[keep], side[keep]
assert n == 21516 and len(gsrc) == 2977920

nt = pd.read_feather("data/body-neurotransmitters-male-cns-v1.0.feather",
                     columns=["body", "consensus_nt"])
nt_map = dict(zip(nt["body"].astype(np.uint64).astype(str), nt["consensus_nt"]))
nt_names = np.array([str(nt_map.get(str(int(b)), "unknown")).lower() for b in ids])
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(str(nt_names[keep][i]), 0.3) for i in range(n)],
                 np.float32)
Wa_vals = gw * signA[loc[gsrc]]
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([loc[gdst], loc[gsrc]])).long(),
    torch.from_numpy(Wa_vals.astype(np.float32)), (n, n)).coalesce().to_sparse_csr()

motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
tm = pd.Series(ltyp)
PAIRS = {}
for k in ("Ti", "Tr"):
    f = np.where(motor & tm.isin([f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (tm == f"{k} extensor MN"))[0]
    PAIRS[k] = dict(fL=f[lside[f] == "L"], fR=f[lside[f] == "R"],
                    eL=e[lside[e] == "L"], eR=e[lside[e] == "R"])
dng100 = np.where(ltyp == "DNg100")[0]

E1 = np.where(ltyp == "IN17A001")[0]
I2 = np.where(ltyp == "IN19A007")[0]
E3 = np.where(ltyp == "IN19B012")[0]
X464 = np.where(ltyp == "INXXX464")[0]
for nm, v in (("E1", E1), ("I2", I2), ("E3", E3), ("X464", X464)):
    assert len(v) == 6, (nm, len(v))
CLAMP = {"base": np.array([], np.int64), "c_E1": E1,
         "c_I2E3": np.concatenate([I2, E3]),
         "c_E1I2E3": np.concatenate([E1, I2, E3]),
         "c_E1X464": np.concatenate([E1, X464])}
ARMS = list(CLAMP)
log(f"sub {n:,} | arms {ARMS}")

SIGS = ("fL", "fR", "eL", "eR")


def rhythm2(x, lo=0.5, hi=10.0):
    x = x - x.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    b = (fr >= lo) & (fr <= hi)
    pb, fb = ps[b], fr[b]
    i = int(np.argmax(pb))
    return (float(pb[i] / max(np.median(pb), 1e-30)), float(fb[i])) if pb.max() > 0 else (0.0, 0.0)


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


out = {}
for seed in SEEDS:
    gen = torch.Generator().manual_seed(seed)
    X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    X = {a: X0.clone() for a in ARMS}  # ONE init draw, cloned (L36 rule)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}

    def step(k):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        for a in ARMS:
            t = torch.relu(torch.sparse.mm(Wb, X[a]) * G + I + BG)
            X[a] = X[a] + (DT / TAU) * ((t + nz).clamp(max=RMAX) - X[a])
            if a != "base" and CL0 <= k < CL1:
                X[a][CLAMP[a]] = 0.0

    for k in range(SETTLE):
        step(-1 - k)
    for i in range(WIN):
        step(i)
        for a in ARMS:
            mm[a][i] = X[a][motor].mean()
            for c in SIGS:
                tr[a][c][i] = X[a][PAIRS["Tr"][c]].mean()
    for a in ARMS:
        r_pre, f_pre = rhythm2(mm[a][3400:4000])
        r_dur, f_dur = rhythm2(mm[a][4100:8900])
        fL, fR, eL, eR = (tr[a][c] for c in SIGS)
        S = np.array([S_of(fL[t - 499:t + 1] + fR[t - 499:t + 1],
                           eL[t - 499:t + 1] + eR[t - 499:t + 1])
                      for t in range(4099, 8899, 10)])
        out[f"{a}_{seed}"] = dict(r_pre=round(r_pre, 1), f_pre=round(f_pre, 3),
                                  r_dur=round(r_dur, 1), f_dur=round(f_dur, 3),
                                  S_dur=round(float(np.nanmedian(S)), 3))
        np.savez_compressed("l45/probe_traces.npz",
                            **{f"mm_{a}_{s}": mm[a] for a in ARMS for s in SEEDS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

json.dump(out, open("l45/results_l45a_probe.json", "w"), indent=1)
for a in ARMS:
    print(a, {s: out[f"{a}_{s}"] for s in SEEDS}, flush=True)
log(f"done {time.time()-t0:.0f}s")
