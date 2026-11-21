"""L16: does the CORD REFLEX ARC interior carry gesture TIME?

L15 verdict: under a looming (brain) event with homogeneous tau, gesture
TIME is bulk — only WHICH cells act (top-6 anatomy) is wiring-carried; the
open card says the TIME structure may live in the cord arc interior
(vnc_sensory -> intrinsic -> motor; L11: cord event -> reproducible motor
vector, self-cos .987) which L14 froze.

This tick: L15's gesture-time protocol applied to the L11 CORD mechano
event, with the antagonist MN pairs the MaleCNS type vocabulary actually
names (Ti/Tr flexor vs extensor = swing/stance substrate).

Arms:
  anchor: exact L11 peak protocol x3 seeds -> must reproduce ~.987.
  real:   cord mechano event (amp 2.0, EVENT 20 + POST 220, T=240), full
          (815 motor x 240) difference tensor, 3 seeds.
  null:   5 draws of a FOCUSED INTERIOR rewire — MS swaps on the cord
          interior block (src in vnc_sensory|vnc_intrinsic AND dst in
          vnc_intrinsic; 2.19M edges: sensory->intrinsic + intrinsic->
          intrinsic), weights travel with source; ALL dst==motor edges
          (intrinsic->motor 155k + sensory->motor 9.3k + DN->motor 23.6k)
          and everything outside the cord FROZEN — the readout boundary
          is preserved (Dhiman/Park lesson). 3 seeds each.

Metrics (L15 rule: per-seed sign-consistency, never mean lead):
  - antagonist pairs (Ti, Tr): lead = t_pk(extensor) - t_pk(flexor) per
    seed; demeaned xcorr min + lag per seed (reciprocal-inhibition
    signature = anti-phase dip).
  - temporal PCA of the M x T tensor: variance shares comp1/comp2; a
    SECOND component with flex-vs-ext opposite loadings = sequencing.
  - per-cell t_pk spread (top-200 loaded cells), half-time spread.
  - family continuity: jump vs drive masks (l15), st self-cos, top-6
    mass through time.
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 300
GAIN = 0.8846
AMP = 2.0
SEEDS = [11, 22, 33]
NDRAW = 5
EVENT, POST = 20, 220
T = EVENT + POST  # 240 steps = 2.4 s

os.makedirs("l16", exist_ok=True)
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
side_m = lab["somaSide"].astype(str).to_numpy()[motor]
mL_loc = np.where(side_m == "L")[0]
mR_loc = np.where(side_m == "R")[0]
typm = typ[motor]
M = len(motor)
dn = np.where(sup == "descending_neuron")[0]
cord_mech = np.where((sup == "vnc_sensory")
                     & pd.Series(cls).str.contains("mechano").to_numpy())[0]
print(f"cord mechano sensory: {len(cord_mech)} | motor {M} | dn {len(dn)}", flush=True)

# antagonist pools (LOCAL indices into the 815-row motor readout)
PAIRS = {
    "Ti": (np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
           np.where(typm == "Ti extensor MN")[0]),
    "Tr": (np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0],
           np.where(typm == "Tr extensor MN")[0]),
}
for k, (f, e) in PAIRS.items():
    assert len(f) > 0 and len(e) > 0, (k, len(f), len(e))
    print(f"pair {k}: flexor {len(f)} cells {sorted(set(typm[f]))} | "
          f"extensor {len(e)} {sorted(set(typm[e]))}", flush=True)

# l15 family masks for continuity
jump_loc = np.where(np.array([str(t).startswith(("TTMn", "DLMn", "DVMn"))
                              for t in typm]))[0]

# ---------- edge partition: cord interior block vs frozen rest ----------
rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
mrow = np.zeros(N, bool); mrow[motor] = True
sens = np.zeros(N, bool); sens[sup == "vnc_sensory"] = True
intr = sup == "vnc_intrinsic"
blk = intr[rows] & (sens[cols] | intr[cols])
b_dst, b_src, b_w = rows[blk].copy(), cols[blk].copy(), vals[blk].copy()
nb_dst, nb_src, nb_val = rows[~blk], cols[~blk], vals[~blk]
frozen_motor_in = int((mrow[rows] & (intr[cols] | sens[cols]
                                     | (sup[cols] == "descending_neuron"))).sum())
print(f"interior block {blk.sum():,} (sens->intr {int((intr[rows] & sens[cols]).sum()):,} "
      f"+ intr->intr {int((intr[rows] & intr[cols]).sum()):,}) | frozen edges INTO motor "
      f"{frozen_motor_in:,} | non-block {len(nb_dst):,} | {time.time()-t0:.0f}s", flush=True)


def rewire_block(rng, factor=8):
    """MS destination swaps INSIDE the interior block; weights stay with
    sources; reject duplicates; in/out degrees preserved."""
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


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


def run_anchor(W_, seed):
    """Exact L11 peak protocol: returns peak dm motor vector."""
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[cord_mech] = AMP
    for _ in range(SETTLE):
        step(Z)
    Xb = X[motor].squeeze(1).numpy().copy()
    peak_m, Xpk = -1.0, None
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else Z)
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m, Xpk = m, X.clone()
    return Xpk[motor].squeeze(1).numpy() - Xb


def run_gesture(W_, seed):
    """Full (M x T) motor difference tensor through cord event + decay."""
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[cord_mech] = AMP
    for _ in range(SETTLE):
        step(Z)
    base = X[motor].squeeze(1).numpy().copy()
    rec = np.zeros((M, T), dtype=np.float32)
    for k in range(T):
        step(I0 if k < EVENT else Z)
        rec[:, k] = X[motor].squeeze(1).numpy() - base
    return rec


def half_time(p):
    pk = float(p.max()); tp = int(np.argmax(p))
    below = np.where(p[tp:] < 0.5 * pk)[0]
    return int(tp + below[0]) if len(below) else T


def xcorr_min(a, b, maxlag=40):
    a = a - a.mean(); b = b - b.mean()
    best, blag = 1.0, 0
    for lag in range(-maxlag, maxlag + 1):
        if lag < 0:
            x, y = a[:lag], b[-lag:]
        elif lag > 0:
            x, y = a[lag:], b[:-lag]
        else:
            x, y = a, b
        c = cos(x, y)
        if c < best:
            best, blag = c, lag
    return float(best), int(blag)


def temporal_pca(rec):
    """Variance shares of the first 2 temporal components + flex/ext
    loading separation on comp2 (z-scored difference of pool means)."""
    C = rec - rec.mean(axis=1, keepdims=True)
    U, S, Vt = np.linalg.svd(C, full_matrices=False)
    sh = (S ** 2) / (S ** 2).sum()
    out = {"var1": float(sh[0]), "var2": float(sh[1]) if len(sh) > 1 else 0.0}
    if len(sh) > 1:
        L2 = U[:, 1]  # cell loadings on temporal comp2
        z = (L2 - L2.mean()) / (L2.std() + 1e-12)
        seps = {}
        for k, (f, e) in PAIRS.items():
            seps[k] = float(z[e].mean() - z[f].mean())
        out["comp2_flex_ext_sep"] = seps
    return out


def gesture_metrics(recs):
    flat = [r.ravel() for r in recs]
    st_cos = float(np.mean([cos(flat[i], flat[j])
                            for i in range(len(flat)) for j in range(i + 1, len(flat))]))
    out = {"st_self_cos": st_cos, "runs": []}
    for r in recs:
        run = {"half_jump": half_time(r[jump_loc].mean(0))}
        for k, (f, e) in PAIRS.items():
            pf, pe = r[f].mean(0), r[e].mean(0)
            xc, xlag = xcorr_min(pf, pe)
            run[f"{k}_lead_ext_minus_flex"] = int(np.argmax(pe) - np.argmax(pf))
            run[f"{k}_t_pk_flex"] = int(np.argmax(pf))
            run[f"{k}_t_pk_ext"] = int(np.argmax(pe))
            run[f"{k}_peak_flex"] = float(pf.max())
            run[f"{k}_peak_ext"] = float(pe.max())
            run[f"{k}_xcorr_min"] = xc
            run[f"{k}_xcorr_lag"] = xlag
        # per-cell t_pk among top-200 loaded cells (sign-corrected: an
        # inhibited cell peaks where its NEGATIVE deflection is deepest)
        prof = np.abs(r).mean(axis=1)
        top = np.argsort(-prof)[:200]
        tpk = []
        for i in top:
            tr = r[i] if r[i].max() > -r[i].min() else -r[i]
            tpk.append(int(np.argmax(tr)))
        tpk = np.array(tpk)
        run["tpk_iqr_top200"] = float(np.percentile(tpk, 75) - np.percentile(tpk, 25))
        run["tpk_sd_top200"] = float(tpk.std())
        run["half_spread_top200"] = float(np.std([half_time(r[i]) for i in top[:60]]))
        run["motor_peak"] = float(r.max(axis=0).max())
        out["runs"].append(run)
    agg = {}
    keys = sorted({k for run in out["runs"] for k in run})
    for k in keys:
        v = [run[k] for run in out["runs"] if k in run]
        agg[k] = float(np.mean(v))
    for k in ["Ti", "Tr"]:
        leads = [run[f"{k}_lead_ext_minus_flex"] for run in out["runs"]]
        out[f"{k}_lead_sign_consistent"] = bool(
            all(l > 0 for l in leads) or all(l < 0 for l in leads))
        xcs = [run[f"{k}_xcorr_min"] for run in out["runs"]]
        out[f"{k}_xcorr_neg_consistent"] = bool(all(x < 0 for x in xcs))
    out["agg"] = agg
    out["pca"] = temporal_pca(np.mean(recs, axis=0))
    return out


# ---------- anchor ----------
anch = [run_anchor(W, s) for s in SEEDS]
anchor_cos = float(np.mean([cos(anch[i], anch[j])
                            for i in range(3) for j in range(i + 1, 3)]))
print(f"anchor L11 cord peak self-cos: {anchor_cos:.3f} (expect ~.987) | "
      f"{time.time()-t0:.0f}s", flush=True)

# ---------- real ----------
real_recs = [run_gesture(W, s) for s in SEEDS]
prof = np.mean([np.abs(r).mean(axis=1) for r in real_recs], axis=0)
order = np.argsort(-prof)
drive_loc = np.array([i for i in order if i not in set(jump_loc.tolist())][:20])
top6_loc = order[:6]
real_m = gesture_metrics(real_recs)
real_m["agg"]["top6_mass"] = float(np.mean(
    [np.abs(r[top6_loc]).mean() / (np.abs(r).mean() + 1e-12) for r in real_recs]))
print(f"REAL: st-cos {real_m['st_self_cos']:.3f} | Ti lead "
      f"{real_m['agg']['Ti_lead_ext_minus_flex']:+.0f} xc "
      f"{real_m['agg']['Ti_xcorr_min']:+.3f}@{real_m['agg']['Ti_xcorr_lag']:+.0f} | "
      f"Tr lead {real_m['agg']['Tr_lead_ext_minus_flex']:+.0f} xc "
      f"{real_m['agg']['Tr_xcorr_min']:+.3f}@{real_m['agg']['Tr_xcorr_lag']:+.0f} | "
      f"pca var1/2 {real_m['pca']['var1']:.3f}/{real_m['pca']['var2']:.3f} | "
      f"tpk_sd {real_m['agg']['tpk_sd_top200']:.1f} | top6 "
      f"{real_m['agg']['top6_mass']:.3f} | {time.time()-t0:.0f}s", flush=True)

# ---------- interior-null ensemble ----------
rng = np.random.default_rng(20261110 + 16)
nulls = []
for d in range(NDRAW):
    dst, src, w, done = rewire_block(rng)
    Wn = build_W(dst, src, w)
    recs = [run_gesture(Wn, s) for s in SEEDS]
    m_ = gesture_metrics(recs)
    m_["swaps"] = done
    m_["agg"]["top6_mass"] = float(np.mean(
        [np.abs(r[top6_loc]).mean() / (np.abs(r).mean() + 1e-12) for r in recs]))
    nulls.append(m_)
    print(f"null{d}: st-cos {m_['st_self_cos']:.3f} | Ti lead "
          f"{m_['agg']['Ti_lead_ext_minus_flex']:+.0f} xc "
          f"{m_['agg']['Ti_xcorr_min']:+.3f}@{m_['agg']['Ti_xcorr_lag']:+.0f} | "
          f"Tr lead {m_['agg']['Tr_lead_ext_minus_flex']:+.0f} xc "
          f"{m_['agg']['Tr_xcorr_min']:+.3f}@{m_['agg']['Tr_xcorr_lag']:+.0f} | "
          f"pca var1/2 {m_['pca']['var1']:.3f}/{m_['pca']['var2']:.3f} | "
          f"top6 {m_['agg']['top6_mass']:.3f} | {time.time()-t0:.0f}s", flush=True)

res = {
    "anchor_peak_self_cos": anchor_cos,
    "config": {"AMP": AMP, "EVENT": EVENT, "POST": POST, "T": T, "seeds": SEEDS,
               "ndraw": NDRAW, "gain": GAIN, "tau": TAU,
               "cord_mech_n": int(len(cord_mech)),
               "pairs": {k: {"flex": sorted(set(typm[f].tolist())),
                             "ext": sorted(set(typm[e].tolist())),
                             "n_flex": int(len(f)), "n_ext": int(len(e))}
                         for k, (f, e) in PAIRS.items()},
               "interior_block_edges": int(blk.sum()),
               "jump_types": sorted(set(typm[jump_loc].tolist())),
               "drive_types": sorted(set(typm[drive_loc].tolist())),
               "top6_types": typm[top6_loc].tolist()},
    "real": real_m,
    "nulls": nulls,
}
json.dump(res, open("l16/results_l16.json", "w"), indent=1)
np.savez_compressed("l16/cord_mats.npz",
                    real_seed11=real_recs[0],
                    jump_loc=jump_loc, drive_loc=drive_loc, top6_loc=top6_loc,
                    **{f"Ti_flex": PAIRS["Ti"][0], f"Ti_ext": PAIRS["Ti"][1],
                       f"Tr_flex": PAIRS["Tr"][0], f"Tr_ext": PAIRS["Tr"][1]})
print(f"\ndone {time.time()-t0:.0f}s -> l16/results_l16.json", flush=True)
