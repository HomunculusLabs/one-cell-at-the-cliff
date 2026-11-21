"""L17: the kinetics lever — per-class tau tiers on the antagonist MN pools.

L15+L16 verdict: uniform-tau first-order rates cannot phase-sequence —
wiring specifies WHICH cells act, never WHEN. This tick tests the one
remaining honest lever INSIDE the model class: heterogeneous time
constants on the MN pools themselves.

Arms (cord mechano event, amp 2.0, EVENT 20 + POST 220, T=240 — l16 verbatim):
  homog:  tau .05 everywhere = the L16 real arm (anchor; leads <=1 step).
  A1:     FAST tau (.02) on the EXTENSOR pools, SLOW (.20) on flexors —
          the bio-suggested direction (extensor tibiae = phasic jump power).
  A2:     the reverse (fast flexors, slow extensors).
  shuf:   5 draws — A1's tau multiset PERMUTED across the pool-union cells
          (same number of fast/slow cells, random placement) — the control
          that separates CLASS-STRUCTURED kinetics from mere tau mixing.

Honest framing (queue text): this tests the MODEL CLASS's expressivity,
NOT a wiring claim — tau values are free parameters chosen for contrast,
not measured MN time constants. Real CPG phasing = nonspiking premotor +
plateau currents + conduction delays (outside this class).

Gate: per-seed antagonist leads + sign-consistency in BOTH assignments
(A1 and A2 expected sign-OPPOSITE) vs the shuffle-null spread; homog arm
reproduces L16's simultaneous recruitment.
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
TAU_FAST, TAU_SLOW = 0.02, 0.20
BG, NOISE = 0.02, 0.01
SETTLE = 300
GAIN = 0.8846
AMP = 2.0
SEEDS = [11, 22, 33]
NDRAW = 5
EVENT, POST = 20, 220
T = EVENT + POST

os.makedirs("l17", exist_ok=True)
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
typm = typ[motor]
M = len(motor)
cord_mech = np.where((sup == "vnc_sensory")
                     & pd.Series(cls).str.contains("mechano").to_numpy())[0]
print(f"cord mechano sensory: {len(cord_mech)} | motor {M}", flush=True)

PAIRS = {
    "Ti": (np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
           np.where(typm == "Ti extensor MN")[0]),
    "Tr": (np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0],
           np.where(typm == "Tr extensor MN")[0]),
}
POOL_F = np.concatenate([PAIRS["Ti"][0], PAIRS["Tr"][0]])
POOL_E = np.concatenate([PAIRS["Ti"][1], PAIRS["Tr"][1]])
POOL_U = np.concatenate([POOL_F, POOL_E])
jump_loc = np.where(np.array([str(t).startswith(("TTMn", "DLMn", "DVMn"))
                              for t in typm]))[0]
for k, (f, e) in PAIRS.items():
    assert len(f) > 0 and len(e) > 0
    print(f"pair {k}: flexor {len(f)} | extensor {len(e)}", flush=True)
print(f"pool-union {len(POOL_U)} cells (flex {len(POOL_F)} / ext {len(POOL_E)}) "
      f"| fast:slow multiset {len(POOL_E)}:{len(POOL_F)}", flush=True)


def tau_vec(arm, rng=None):
    tv = np.full(N, TAU, np.float32)
    if arm == "homog":
        pass
    elif arm == "A1_fastext":
        tv[motor[POOL_E]] = TAU_FAST
        tv[motor[POOL_F]] = TAU_SLOW
    elif arm == "A2_fastflex":
        tv[motor[POOL_F]] = TAU_FAST
        tv[motor[POOL_E]] = TAU_SLOW
    elif arm.startswith("shuf"):
        vals = np.array([TAU_FAST] * len(POOL_E) + [TAU_SLOW] * len(POOL_F),
                        np.float32)
        vals = vals[rng.permutation(len(vals))]
        tv[motor[POOL_U]] = vals
    else:
        raise ValueError(arm)
    return torch.from_numpy(tv).unsqueeze(1)


def run_gesture(tau, seed, W_=W):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)

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


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


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


def run_metrics(r):
    out = {"half_jump": half_time(r[jump_loc].mean(0)),
           "peak_jump": float(r[jump_loc].mean(0).max())}
    for k, (f, e) in PAIRS.items():
        pf, pe = r[f].mean(0), r[e].mean(0)
        xc, xlag = xcorr_min(pf, pe)
        out[f"{k}_lead_ext_minus_flex"] = int(np.argmax(pe) - np.argmax(pf))
        out[f"{k}_t_pk_flex"] = int(np.argmax(pf))
        out[f"{k}_t_pk_ext"] = int(np.argmax(pe))
        out[f"{k}_peak_flex"] = float(pf.max())
        out[f"{k}_peak_ext"] = float(pe.max())
        out[f"{k}_half_flex"] = half_time(pf)
        out[f"{k}_half_ext"] = half_time(pe)
        out[f"{k}_xcorr_min"] = xc
        out[f"{k}_xcorr_lag"] = xlag
    return out


def arm_summary(recs, label):
    runs = [run_metrics(r) for r in recs]
    flat = [r.ravel() for r in recs]
    out = {"label": label, "runs": runs,
           "st_self_cos": float(np.mean([cos(flat[i], flat[j])
                                         for i in range(len(flat))
                                         for j in range(i + 1, len(flat))]))}
    for k in ["Ti", "Tr"]:
        leads = [r[f"{k}_lead_ext_minus_flex"] for r in runs]
        xcs = [r[f"{k}_xcorr_min"] for r in runs]
        out[f"{k}_leads"] = leads
        out[f"{k}_lead_mean"] = float(np.mean(leads))
        out[f"{k}_sign_consistent"] = bool(all(l > 0 for l in leads)
                                           or all(l < 0 for l in leads))
        out[f"{k}_xcorr_neg_consistent"] = bool(all(x < 0 for x in xcs))
        out[f"{k}_half_flex"] = float(np.mean([r[f"{k}_half_flex"] for r in runs]))
        out[f"{k}_half_ext"] = float(np.mean([r[f"{k}_half_ext"] for r in runs]))
    return out


ARMS = {}
RECS = {}
for arm in ["homog", "A1_fastext", "A2_fastflex"]:
    RECS[arm] = [run_gesture(tau_vec(arm), s) for s in SEEDS]
    ARMS[arm] = arm_summary(RECS[arm], arm)
    a = ARMS[arm]
    print(f"{arm}: Ti lead {a['Ti_lead_mean']:+.1f} {a['Ti_leads']} sc={a['Ti_sign_consistent']} | "
          f"Tr lead {a['Tr_lead_mean']:+.1f} {a['Tr_leads']} sc={a['Tr_sign_consistent']} | "
          f"Ti half f/e {a['Ti_half_flex']:.0f}/{a['Ti_half_ext']:.0f} | "
          f"xc {np.mean([r['Ti_xcorr_min'] for r in a['runs']]):+.3f} | "
          f"st-cos {a['st_self_cos']:.3f} | {time.time()-t0:.0f}s", flush=True)

rng = np.random.default_rng(20261110 + 17)
SHUF = []
for d in range(NDRAW):
    s = arm_summary([run_gesture(tau_vec("shuf", rng), sd) for sd in SEEDS],
                    f"shuf{d}")
    SHUF.append(s)
    print(f"shuf{d}: Ti lead {s['Ti_lead_mean']:+.1f} {s['Ti_leads']} sc={s['Ti_sign_consistent']} | "
          f"Tr lead {s['Tr_lead_mean']:+.1f} {s['Tr_leads']} sc={s['Tr_sign_consistent']} | "
          f"st-cos {s['st_self_cos']:.3f} | {time.time()-t0:.0f}s", flush=True)

# ---------- verdict numbers ----------
nv = {k: {"leads": [x[f"{k}_lead_mean"] for x in SHUF],
          "max_abs": float(max(abs(x[f"{k}_lead_mean"]) for x in SHUF)),
          "sc_count": int(sum(x[f"{k}_sign_consistent"] for x in SHUF))}
      for k in ["Ti", "Tr"]}
opp = {k: bool((ARMS["A1_fastext"][f"{k}_lead_mean"] < 0
                < ARMS["A2_fastflex"][f"{k}_lead_mean"])
               or (ARMS["A2_fastflex"][f"{k}_lead_mean"] < 0
                   < ARMS["A1_fastext"][f"{k}_lead_mean"]))
       for k in ["Ti", "Tr"]}
clears = {k: bool(abs(ARMS["A1_fastext"][f"{k}_lead_mean"]) > nv[k]["max_abs"]
                  and abs(ARMS["A2_fastflex"][f"{k}_lead_mean"]) > nv[k]["max_abs"])
          for k in ["Ti", "Tr"]}
print(f"\nNULL: Ti max|lead| {nv['Ti']['max_abs']:.1f} sc {nv['Ti']['sc_count']}/5 | "
      f"Tr max|lead| {nv['Tr']['max_abs']:.1f} sc {nv['Tr']['sc_count']}/5", flush=True)
print(f"A1/A2 sign-opposite: {opp} | assignments clear null max: {clears}", flush=True)

res = {"config": {"AMP": AMP, "EVENT": EVENT, "POST": POST, "T": T,
                  "seeds": SEEDS, "ndraw": NDRAW, "gain": GAIN,
                  "tau_base": TAU, "tau_fast": TAU_FAST, "tau_slow": TAU_SLOW,
                  "pool": {"flex": int(len(POOL_F)), "ext": int(len(POOL_E)),
                           "union": int(len(POOL_U))},
                  "pairs": {k: {"n_flex": int(len(f)), "n_ext": int(len(e))}
                            for k, (f, e) in PAIRS.items()}},
       "arms": ARMS, "shuffle_nulls": SHUF, "null_agg": nv,
       "sign_opposite": opp, "clears_null_max": clears}
json.dump(res, open("l17/results_l17.json", "w"), indent=1)
np.savez_compressed("l17/mean_tensors.npz",
                     homog=np.mean(RECS["homog"], axis=0),
                     A1=np.mean(RECS["A1_fastext"], axis=0),
                     A2=np.mean(RECS["A2_fastflex"], axis=0),
                     **{f"Ti_flex": PAIRS["Ti"][0], f"Ti_ext": PAIRS["Ti"][1],
                        f"Tr_flex": PAIRS["Tr"][0], f"Tr_ext": PAIRS["Tr"][1]})
print(f"\ndone {time.time()-t0:.0f}s -> l17/results_l17.json", flush=True)
