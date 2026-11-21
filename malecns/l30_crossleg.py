"""L30: CROSS-LEG-COUPLING — is the cord segment-modular, or does the
intrinsic sheet carry an inter-leg (serial T1->T3) vocabulary?

Segment keys (annotations): motor somaNeuromere T1 173 / T2 175 / T3 152
(+ A1-A10); vnc_intrinsic T1 3,380 / T2 4,493 / T3 3,417; vnc_sensory has
NO neuromere -> the segmentable sheet is the intrinsic one (scope note:
the MS null therefore rewires intr->intr only; sensory carries no T label).

STATIC (claim-carrier), CSR orientation W[target, source]:
  S1 direct  table intr(Ta)->motor(Tb)  weight mass, cross/within share
  S2 sheet   table intr(Ta)->intr(Tb)   weight mass, cross/within share
  S3 2-hop   effective drive of motor(Tb) from intr(Ta):
       P[a,b] = sum over intr->intr edges (t,s,w) with s in Ta of w * g_b[t],
       g_b[v] = sum_{m in motor(Tb)} W[m,v]  (v's efferent weight into pool b)
  nulls: 500-draw intrinsic-neuromere LABEL permutation (marginals kept) for
       S1/S2/S3; >=3-draw focused MS destination-swap on the intr->intr block
       (weights travel with source, in/out degrees kept) for S3 — the direct
       S1 block is frozen by construction under an intr->intr rewire, so the
       MS-null-claim lives on the 2-hop path mass only (honest scope).
  S4 readable table: per leg pool, in-weight provenance by source class.

DYNAMIC (P1-labeled, L20 optogenetic-style input volley, NO amplification):
  arms T1v / T3v (premotor-intrinsic volley, 300 ms @ amp 8) + rnd
  (size-matched random intrinsic, no premotor restriction), 3 seeds.
  pools: T1L/T1R/T2L/T2R/T3L/T3R/abd. Uniform tau 50 ms interior+motor
  (L15 rule: no WHEN-claims from uniform tau beyond path-integral DELAY,
  which L21 showed is path-carried and tau-invariant). SNR gate FIRST
  (L19): within-pool SNR must clear >>noise before any cross-pool read.
CPU-only, no live changes.
"""
import json
import os
import time
from collections import defaultdict

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
t0 = time.time()
rng = np.random.default_rng(20261111 + 30)

TAU, DT, RMAX = 0.05, 0.010, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 300
GAIN = 0.8846            # op point bisected in L11
AMP = 8.0
VOLLEY_STEPS = 30        # 300 ms
POST = 700
SEEDS = [11, 22, 33]
LABEL_DRAWS = 500
MS_DRAWS = 3
MS_ATTEMPTS = 2_500_000
MS_TIMEBOX = 240.0       # s per draw

ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].fillna("").astype(str).to_numpy()
typ = lab["type"].fillna("").astype(str).to_numpy()
side = lab["somaSide"].fillna("").astype(str).to_numpy()
nrom = lab["somaNeuromere"].fillna("").astype(str).to_numpy()  # fillna first (skill)

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
intr = np.where(sup == "vnc_intrinsic")[0]
sens = np.where(sup == "vnc_sensory")[0]
dn = np.where(sup == "descending_neuron")[0]

Torder = ["T1", "T2", "T3"]
def tcode(arr, idxs):
    c = np.full(len(idxs), -1, np.int64)
    for k, t in enumerate(Torder):
        c[nrom[idxs] == t] = k
    return c

mcode_all = tcode(nrom, motor)          # -1 = abdominal/other
icode_all = tcode(nrom, intr)
mT = [np.where(mcode_all == k)[0] for k in range(3)]   # indices INTO motor
iT = [np.where(icode_all == k)[0] for k in range(3)]   # indices INTO intr
assert [len(x) for x in mT] == [173, 175, 152], [len(x) for x in mT]
assert [len(x) for x in iT] == [3380, 4493, 3417], [len(x) for x in iT]
abd = np.where(mcode_all == -1)[0]

# 6 leg pools (motor indices) + abd
pools = {}
for k, t in enumerate(Torder):
    for s in ("L", "R"):
        sel = mT[k][side[motor[mT[k]]] == s]
        pools[f"{t}{s}"] = motor[sel]
pools["abd"] = motor[abd]
assert all(len(v) >= 40 for v in pools.values()), {k: len(v) for k, v in pools.items()}

# ---- edges (CSR: rows targets, cols sources) ----
rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
Wv = W.values().numpy().astype(np.float32)
rmask = np.zeros(N, bool); rmask[motor] = True
cmask_i = np.zeros(N, bool); cmask_i[intr] = True
cmask_s = np.zeros(N, bool); cmask_s[sens] = True

pos_m = np.full(N, -1, np.int64); pos_m[motor] = np.arange(len(motor))
pos_i = np.full(N, -1, np.int64); pos_i[intr] = np.arange(len(intr))

# S1 direct: rows in motor, cols in intrinsic
b1 = rmask[rows] & cmask_i[cols]
s1_src_i, s1_dst_m, s1_w = pos_i[cols[b1]], pos_m[rows[b1]], vals[b1]
s1_code = icode_all[s1_src_i]
s1_mcode = mcode_all[s1_dst_m]

# S2 sheet: rows in intrinsic, cols in intrinsic
b2 = cmask_i[rows] & cmask_i[cols]
s2_src_i, s2_dst_i, s2_w = pos_i[cols[b2]], pos_i[rows[b2]], vals[b2]
s2_code = icode_all[s2_src_i]
s2_dcode = icode_all[s2_dst_i]


def table_bincount(code_src, code_dst, w):
    okm = (code_src >= 0) & (code_dst >= 0)
    c = code_src[okm] * 3 + code_dst[okm]
    return np.bincount(c, weights=w[okm], minlength=9).reshape(3, 3).astype(np.float64)


T1 = table_bincount(s1_code, s1_mcode, s1_w)
T2 = table_bincount(s2_code, s2_dcode, s2_w)

def cross_share(T):
    tot = T.sum()
    return float(1.0 - np.trace(T) / tot) if tot > 0 else float("nan")

print("S1 intr(Ta)->motor(Tb) weight mass:\n", np.array2string(T1, precision=1))
print("S2 intr(Ta)->intr(Tb)  weight mass:\n", np.array2string(T2, precision=1))
print(f"cross-share S1 {cross_share(T1):.4f}  S2 {cross_share(T2):.4f}", flush=True)

# ---- label permutation null (permute T-codes among T-labeled intrinsic) ----
Tlab = np.where(icode_all >= 0)[0]   # indices into intr with T labels
cs1, cs2, tabs1, tabs2 = [], [], np.zeros((LABEL_DRAWS, 9)), np.zeros((LABEL_DRAWS, 9))
for d in range(LABEL_DRAWS):
    perm = icode_all.copy()
    perm[Tlab] = perm[rng.permutation(Tlab)]
    ta = table_bincount(perm[s1_src_i], s1_mcode, s1_w)
    tb = table_bincount(perm[s2_src_i], perm[s2_dst_i], s2_w)
    cs1.append(cross_share(ta)); cs2.append(cross_share(tb))
    tabs1[d] = ta.ravel(); tabs2[d] = tb.ravel()
cs1, cs2 = np.array(cs1), np.array(cs2)
z1 = (cross_share(T1) - cs1.mean()) / (cs1.std() + 1e-12)
z2 = (cross_share(T2) - cs2.mean()) / (cs2.std() + 1e-12)
cellz1 = ((T1.ravel() - tabs1.mean(0)) / (tabs1.std(0) + 1e-12)).reshape(3, 3)
cellz2 = ((T2.ravel() - tabs2.mean(0)) / (tabs2.std(0) + 1e-12)).reshape(3, 3)
print("per-cell z S1:\n", np.array2string(cellz1, precision=1))
print("per-cell z S2:\n", np.array2string(cellz2, precision=1), flush=True)
print(f"label-perm null ({LABEL_DRAWS} draws): S1 cross {cs1.mean():.4f}+-{cs1.std():.4f} z {z1:+.1f} | "
      f"S2 cross {cs2.mean():.4f}+-{cs2.std():.4f} z {z2:+.1f}", flush=True)

# ---- S3: 2-hop effective drive + MS rewire on intr->intr ----
# g_b[v] = v's efferent weight into leg motor pool b (frozen into-motor edges)
gmotor = rmask[rows] & cmask_i[cols]      # same block as S1
g_src, g_dst, g_w = pos_i[cols[gmotor]], pos_m[rows[gmotor]], vals[gmotor]
G3 = np.zeros((3, len(intr)), np.float64)
for b in range(3):
    msel = np.isin(g_dst, mT[b])
    np.add.at(G3[b], g_src[msel], g_w[msel])

def path_mass_fast(dst, src, w, code_of_src):
    """P[a,b] = sum over intr->intr edges (t,s,w) with s in Ta of w * G3[b][t]."""
    a = code_of_src[src]
    okm = a >= 0
    d, ww, aa = dst[okm], np.asarray(w, np.float64)[okm], a[okm]
    P = np.zeros((3, 3))
    for b in range(3):
        contrib = ww * G3[b][d]
        P[:, b] = np.bincount(aa, weights=contrib, minlength=3)
    return P


P_real = path_mass_fast(s2_dst_i, s2_src_i, s2_w, icode_all)
print("S3 2-hop intr(Ta)->sheet->motor(Tb) mass:\n", np.array2string(P_real, precision=1), flush=True)

# label-perm z for S3
cs3 = []
for d in range(LABEL_DRAWS):
    perm = icode_all.copy()
    perm[Tlab] = perm[rng.permutation(Tlab)]
    cs3.append(cross_share(path_mass_fast(s2_dst_i, s2_src_i, s2_w, perm)))
cs3 = np.array(cs3)
z3 = (cross_share(P_real) - cs3.mean()) / (cs3.std() + 1e-12)
print(f"label-perm S3 cross {cs3.mean():.4f}+-{cs3.std():.4f} z {z3:+.1f}", flush=True)

# MS destination-swap on the intr->intr block (weights travel with source)
ms_t, ms_s, ms_w = (s2_dst_i.copy(), s2_src_i.copy(), s2_w.astype(np.float64).copy())
adj = defaultdict(set)
for tt, ss in zip(ms_t, ms_s):
    adj[tt].add(ss)
print(f"MS block: {len(ms_t)} intr->intr edges", flush=True)

def ms_draw(seed):
    r = np.random.default_rng(seed)
    t_, s_, w_ = ms_t.copy(), ms_s.copy(), ms_w.copy()
    a = {k: set(v) for k, v in adj.items()}
    done = 0
    ts = time.time()
    E = len(t_)
    while done < MS_ATTEMPTS and time.time() - ts < MS_TIMEBOX:
        i, j = r.integers(0, E, 2)
        if i == j:
            continue
        t1c, s1c = t_[i], s_[i]
        t2c, s2c = t_[j], s_[j]
        if s1c == s2c or t1c == t2c:
            continue
        if s2c in a[t1c] or s1c in a[t2c]:
            continue
        # swap destinations; weights travel with sources (w[i] stays with s1c)
        a[t1c].remove(s1c); a[t2c].remove(s2c)
        t_[i], t_[j] = t2c, t1c
        a[t2c].add(s1c); a[t1c].add(s2c)
        done += 1
    return (t_, s_, w_), done

ms_cross = []
ms_P = []
for d in range(MS_DRAWS):
    (t_, s_, w_), ndone = ms_draw(7000 + d)
    P = path_mass_fast(t_, s_, w_, icode_all)
    ms_P.append(cross_share(P))
    ms_cross.append(ndone)
    print(f"MS draw {d}: {ndone} swaps | 2-hop cross {cross_share(P):.4f}", flush=True)
ms_P = np.array(ms_P)
z3ms = (cross_share(P_real) - ms_P.mean()) / (ms_P.std() + 1e-12)
print(f"MS-rewire null: S3 cross {ms_P.mean():.4f}+-{ms_P.std():.4f} z {z3ms:+.1f}", flush=True)

# ---- S4: motor pool in-provenance (readable table) ----
prov = {}
for name, sel in pools.items():
    rmask_p = np.zeros(N, bool); rmask_p[sel] = True
    e = rmask_p[rows]
    wsub = vals[e]
    wsum = float(wsub.sum())
    src = cols[e]

    def sh(m):
        return float(wsub[m].sum()) / wsum

    prov[name] = dict(
        cells=int(len(sel)), total_in_weight=wsum,
        from_sensory=sh(cmask_s[src]),
        from_intr_T1=sh(cmask_i[src] & (nrom[src] == 'T1')),
        from_intr_T2=sh(cmask_i[src] & (nrom[src] == 'T2')),
        from_intr_T3=sh(cmask_i[src] & (nrom[src] == 'T3')),
        from_intr_other=sh(cmask_i[src] & ~np.isin(nrom[src], Torder)),
        from_DN=sh(np.isin(sup[src], ['descending_neuron'])),
    )
for k, v in prov.items():
    print(f"S4 {k}: n={v['cells']} | intr T1 {v['from_intr_T1']:.3f} T2 {v['from_intr_T2']:.3f} "
          f"T3 {v['from_intr_T3']:.3f} | sens {v['from_sensory']:.3f} DN {v['from_DN']:.3f}", flush=True)

# ---- dynamic arms ----
premotor_into_motor = rmask[rows] & cmask_i[cols]
pm_src = cols[premotor_into_motor]
vol_T1 = np.array(sorted(set(pm_src[np.isin(pm_src, intr[iT[0]])].tolist())), np.int64)
vol_T3 = np.array(sorted(set(pm_src[np.isin(pm_src, intr[iT[2]])].tolist())), np.int64)
vol_rnd = np.array(sorted(rng.choice(intr, size=len(vol_T1), replace=False).tolist()), np.int64)
print(f"volley sets: T1pmi {len(vol_T1)} | T3pmi {len(vol_T3)} | rnd {len(vol_rnd)}", flush=True)

tau = torch.full((N, 1), TAU)
def rollout(vol_cells, seed):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)
    Z = torch.zeros(N, 1)
    I = Z.clone(); I[vol_cells] = AMP

    def drive_step(inp):
        drive = torch.sparse.mm(W, X) + inp
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        return t

    for _ in range(SETTLE):
        X += (DT / tau) * (drive_step(Z) - X)
    af0 = float((X > 0.05).float().mean())
    tail = []
    for _ in range(100):
        X += (DT / tau) * (drive_step(Z) - X)
        tail.append([float(X[ptens[k]].mean()) for k in pnames])
    tail = np.array(tail)
    base = tail.mean(0); noise = tail.std(0)
    T = VOLLEY_STEPS + POST
    tr = np.zeros((T, len(pools)), np.float32)
    for k in range(T):
        cur = I if k < VOLLEY_STEPS else Z
        X += (DT / tau) * (drive_step(cur) - X)
        tr[k] = [float(X[ptens[p]].mean()) for p in pnames] - base
    snr = (tr.max(0) / (noise + 1e-12))
    tpk = tr.argmax(0)
    return dict(tr=tr, snr=snr, tpk=tpk, noise=noise, af0=af0)

pnames = list(pools.keys())
ptens = {k: torch.from_numpy(v) for k, v in pools.items()}
dyn = {}
for arm, vc in [("T1v", vol_T1), ("T3v", vol_T3), ("rnd", vol_rnd)]:
    per = []
    for sd in SEEDS:
        r = rollout(vc, sd)
        per.append(dict(snr=[float(x) for x in r["snr"]], tpk=[int(x) for x in r["tpk"]],
                        af0=r["af0"]))
        if arm == "T1v" and sd == SEEDS[0]:
            np.savez("l30/traces_T1v.npz", tr=r["tr"], pnames=np.array(pnames))
    dyn[arm] = per
    m = np.array([p["snr"] for p in per]); tp = np.array([p["tpk"] for p in per])
    print(f"arm {arm}: " + " | ".join(
        f"{pn} snr {m[:, i].mean():6.1f}x t_pk {tp[:, i].mean():5.1f}"
        for i, pn in enumerate(pnames)), flush=True)

os.makedirs("l30", exist_ok=True)
res = dict(
    T1_direct=T1.tolist(), T2_sheet=T2.tolist(), P_2hop=P_real.tolist(),
    cellz_S1=cellz1.tolist(), cellz_S2=cellz2.tolist(),
    cross_share=dict(S1=cross_share(T1), S2=cross_share(T2), S3=cross_share(P_real)),
    label_perm=dict(draws=LABEL_DRAWS, S1_mean=float(cs1.mean()), S1_std=float(cs1.std()), z_S1=float(z1),
                    S2_mean=float(cs2.mean()), S2_std=float(cs2.std()), z_S2=float(z2),
                    S3_mean=float(cs3.mean()), S3_std=float(cs3.std()), z_S3=float(z3)),
    ms_rewire=dict(draws=len(ms_cross), swaps=ms_cross, S3_mean=float(ms_P.mean()),
                   S3_std=float(ms_P.std()), z_S3=float(z3ms)),
    provenance=prov,
    volley_sizes=dict(T1pmi=len(vol_T1), T3pmi=len(vol_T3), rnd=len(vol_rnd)),
    dynamic=dyn, pools=pnames,
    af0=dyn["T1v"][0]["af0"], elapsed_s=time.time() - t0,
)
with open("l30/results_l30.json", "w") as f:
    json.dump(res, f, indent=1)
print(f"DONE {time.time()-t0:.0f}s af0 {res['af0']:.3f} -> l30/results_l30.json", flush=True)
