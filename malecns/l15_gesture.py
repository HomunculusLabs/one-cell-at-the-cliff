"""L15: does the wiring-carried anatomy become a GESTURE in time?

L13b: per-class DN->motor gain (DNp01-04 118 edges + DNc01/02 60, x200) makes
a looming volley land reproducibly (peak self-cos .971) on TTMn/DLMn jump MNs
+ leg extensors. L14: reproducibility is BULK (survives DN->motor rewiring,
.958) but WHICH cells load is WIRING (top-6 mass .205 real vs .022 null,
jump-MN enrichment z=+16.7). Open: does that anatomy carry TEMPORAL
structure — family timing (jump vs drive), sustained vs transient decay,
L/R asymmetry through time — or is time another gain-carried dimension?

Arms (machinery verbatim from l13b/l14):
  anchor: exact l13b protocol (EVENT=20, peak snapshot) x3 seeds -> must
          reproduce self-cos ~.971 (pipeline anchor).
  real:   looming volley 60 steps (0.6 s) + 180 decay (T=240), record the
          full (815 motor x T) difference tensor, 3 seeds.
  null:   5 rewire_block draws (l14 focused MS null on the 23.6k DN->motor
          block, weights travel with source DN, interior frozen), SAME
          per-class amplification re-applied, 3 seeds each.

Family masks FROZEN from the real mean profile (so null timing compares on
the same cells): jump = TTMn/DLMn/DVMn types; drive = real top-20 loaded
cells minus jump; top6 = real top-6 (the L14 anatomy metric, through time).
2D path (v = mean motor dm, omega = L/R asym) is a DESCRIPTOR, not a
locomotion claim.
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
G, AMP = 200, 8.0
SEEDS = [11, 22, 33]
NDRAW = 5
EVENT, POST = 60, 180
T = EVENT + POST  # 240 steps = 2.4 s

os.makedirs("l15", exist_ok=True)
t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
side_m = lab["somaSide"].astype(str).to_numpy()[motor]
mL_loc = np.where(side_m == "L")[0]
mR_loc = np.where(side_m == "R")[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(leg_dns) == 8 and len(neck_dns) == 4
typm = typ[motor]
M = len(motor)

rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
mrow = np.zeros(N, bool); mrow[motor] = True
sdn = np.zeros(N, bool); sdn[dn] = True
blk = mrow[rows] & sdn[cols]
b_dst, b_src, b_w = rows[blk].copy(), cols[blk].copy(), vals[blk].copy()
nb_dst, nb_src, nb_val = rows[~blk], cols[~blk], vals[~blk]
print(f"block {blk.sum():,} | non-block {len(nb_dst):,} | {time.time()-t0:.0f}s", flush=True)

leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
NL, NN_ = int((mrow[rows] & leg_src[cols]).sum()), int((mrow[rows] & neck_src[cols]).sum())
assert NL == 118 and NN_ == 60, (NL, NN_)  # L14 counts


def rewire_block(rng, factor=10):
    """MS destination swaps; weights stay with sources; reject duplicates."""
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


def make_pc(Wc):
    """Per-class amplification wherever the class edges are in THIS graph."""
    r2 = np.repeat(np.arange(N), np.diff(Wc.crow_indices().numpy()))
    c2 = Wc.col_indices().numpy()
    ml = int((mrow[r2] & leg_src[c2]).sum())
    mn = int((mrow[r2] & neck_src[c2]).sum())
    assert ml == 118 and mn == 60, (ml, mn)  # swaps preserve source degrees
    W2 = Wc.clone()
    v = W2.values()
    v[torch.from_numpy(mrow[r2] & leg_src[c2])] *= G
    v[torch.from_numpy(mrow[r2] & neck_src[c2])] *= G
    return W2


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


def run_anchor(W_, seed):
    """Exact l13b peak protocol (EVENT=20): returns peak-snapshot dm."""
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[loom] = AMP
    for _ in range(SETTLE):
        step(Z)
    Xb = X[motor].squeeze(1).numpy().copy()
    peak_m, Xpk = -1.0, None
    for k in range(30):
        step(I0 if k < 20 else Z)
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m, Xpk = m, X.clone()
    return Xpk[motor].squeeze(1).numpy() - Xb


def run_gesture(W_, seed):
    """Full (M x T) motor difference tensor through event + decay."""
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[loom] = AMP
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


def path_stats(rec):
    v = np.clip(rec.mean(0), 0, None)
    dL, dR = rec[mL_loc].mean(0), rec[mR_loc].mean(0)
    w = (dL - dR) / (np.abs(dL) + np.abs(dR) + 1e-9)
    th = np.cumsum(w) * DT
    x = np.cumsum(v * np.cos(th)) * DT
    y = np.cumsum(v * np.sin(th)) * DT
    net = float(np.hypot(x[-1], y[-1]))
    total = float(np.sum(np.abs(v)) * DT)
    return net, net / (total + 1e-9), float(th[-1])


def gesture_metrics(recs, jump_loc, drive_loc, top6_loc):
    flat = [r.ravel() for r in recs]
    st_cos = float(np.mean([cos(flat[i], flat[j])
                            for i in range(len(flat)) for j in range(i + 1, len(flat))]))
    out = {"st_self_cos": st_cos, "runs": []}
    for r in recs:
        pj, pd = r[jump_loc].mean(0), r[drive_loc].mean(0)
        lead = int(np.argmax(pd) - np.argmax(pj))
        top6_mass = float(np.abs(r[top6_loc]).mean() / (np.abs(r).mean() + 1e-12))
        net, straight, dth = path_stats(r)
        out["runs"].append({
            "t_pk_jump": int(np.argmax(pj)), "t_pk_drive": int(np.argmax(pd)),
            "drive_minus_jump_lead": lead,
            "half_jump": half_time(pj), "half_drive": half_time(pd),
            "top6_mass": top6_mass,
            "peak_pj": float(pj.max()), "peak_pd": float(pd.max()),
            "path_net": net, "path_straight": straight, "path_dtheta": dth,
            "motor_peak": float(r.max(axis=0).max()) if r.size else 0.0,
        })
    agg = {}
    for k in ["drive_minus_jump_lead", "half_jump", "half_drive", "top6_mass",
              "path_net", "path_straight", "t_pk_jump", "t_pk_drive"]:
        v = [r_[k] for r_ in out["runs"]]
        agg[k] = float(np.mean(v))
    leads = [r_["drive_minus_jump_lead"] for r_ in out["runs"]]
    out["lead_sign_consistent"] = bool(all(l > 0 for l in leads) or all(l < 0 for l in leads))
    out["agg"] = agg
    return out


# ---------- anchor ----------
Wg_real = make_pc(W)
anch = [run_anchor(Wg_real, s) for s in SEEDS]
anchor_cos = float(np.mean([cos(anch[i], anch[j])
                            for i in range(2 + 1) for j in range(i + 1, 3)]))
print(f"anchor l13b peak self-cos: {anchor_cos:.3f} (expect ~.971) | {time.time()-t0:.0f}s", flush=True)

# ---------- real gesture ----------
real_recs = [run_gesture(Wg_real, s) for s in SEEDS]
prof = np.mean([np.abs(r).mean(axis=1) for r in real_recs], axis=0)  # per-cell
jump_loc = np.where(np.array([str(t).startswith(("TTMn", "DLMn", "DVMn"))
                              for t in typm]))[0]
assert len(jump_loc) > 0, "jump family empty — check type names"
order = np.argsort(-prof)
drive_loc = np.array([i for i in order if i not in set(jump_loc.tolist())][:20])
top6_loc = order[:6]
print(f"jump family {len(jump_loc)} cells: {sorted(set(typm[jump_loc]))[:8]}", flush=True)
print(f"drive family top types: {sorted(set(typm[drive_loc]))[:8]}", flush=True)
print(f"top6 types: {list(typm[top6_loc])}", flush=True)
real_m = gesture_metrics(real_recs, jump_loc, drive_loc, top6_loc)
print(f"REAL: st-cos {real_m['st_self_cos']:.3f} lead {real_m['agg']['drive_minus_jump_lead']:+.0f} "
      f"half_j/d {real_m['agg']['half_jump']:.0f}/{real_m['agg']['half_drive']:.0f} "
      f"top6 {real_m['agg']['top6_mass']:.3f} net {real_m['agg']['path_net']:.4f} "
      f"straight {real_m['agg']['path_straight']:.3f} | {time.time()-t0:.0f}s", flush=True)

# ---------- null ensemble ----------
rng = np.random.default_rng(20261110)
nulls = []
for d in range(NDRAW):
    dst, src, w, done = rewire_block(rng)
    Wn = make_pc(build_W(dst, src, w))
    recs = [run_gesture(Wn, s) for s in SEEDS]
    m_ = gesture_metrics(recs, jump_loc, drive_loc, top6_loc)
    m_["swaps"] = done
    nulls.append(m_)
    print(f"null{d}: st-cos {m_['st_self_cos']:.3f} lead {m_['agg']['drive_minus_jump_lead']:+.0f} "
          f"half_j/d {m_['agg']['half_jump']:.0f}/{m_['agg']['half_drive']:.0f} "
          f"top6 {m_['agg']['top6_mass']:.3f} net {m_['agg']['path_net']:.4f} "
          f"straight {m_['agg']['path_straight']:.3f} | {time.time()-t0:.0f}s", flush=True)

def spread(key):
    v = [n["agg"][key] for n in nulls]
    return float(np.mean(v)), float(np.std(v))

summary = {k: {"real": real_m["agg"][k], "null_mean": spread(k)[0], "null_sd": spread(k)[1]}
           for k in real_m["agg"]}
lead_consist_null = sum(n["lead_sign_consistent"] for n in nulls)

res = {
    "anchor_peak_self_cos": anchor_cos,
    "config": {"G": G, "AMP": AMP, "EVENT": EVENT, "POST": POST, "T": T,
               "seeds": SEEDS, "ndraw": NDRAW, "gain": GAIN,
               "jump_types": sorted(set(typm[jump_loc].tolist())),
               "drive_types": sorted(set(typm[drive_loc].tolist())),
               "top6_types": typm[top6_loc].tolist()},
    "real": real_m,
    "nulls": nulls,
    "summary": summary,
    "null_lead_sign_consistent_draws": f"{lead_consist_null}/{NDRAW}",
}
json.dump(res, open("l15/results_l15.json", "w"), indent=1)
np.savez_compressed("l15/gesture_mats.npz",
                    real_seed11=real_recs[0],
                    jump_loc=jump_loc, drive_loc=drive_loc, top6_loc=top6_loc)
print(f"\ndone {time.time()-t0:.0f}s -> l15/results_l15.json", flush=True)
for k, v in summary.items():
    print(f"  {k:26s} real {v['real']:+.4f}  null {v['null_mean']:+.4f}±{v['null_sd']:.4f}")
