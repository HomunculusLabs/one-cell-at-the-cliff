"""L18: literature-tau calibration of the L17 phasing result.

L17 used free-parameter taus (.02/.20 = 10x contrast) and proved the model
class CAN phase. Tick-29 field calibration (LANE-RESEARCH.md) gives the
honest anchors:
  - TDT/jump muscle (the muscle TTMn drives): twitch >=9% ML in <5 ms
    (SUB-STEP at DT 10 ms), exponential relaxation -19.7 1/s ->
    tau_deact ~= 51 ms (MEASURED, prep temp).
  - per-muscle activation taus: NOT measured by the field (2509.06426
    fixed them at literature defaults) -> the slow/tonic side is
    UNDERDETERMINED; we sweep plausible tonic ratios 2x/3x/5x and label
    them as such, never as measurements.
  - IFM (DLM/DVM) is asynchronous/stretch-activated: neural drive does NOT
    time its contractions -> DLMn/DVMn get NO twitch kinetics (base tau).
  - Azevedo 2020: the femur-tibia pair is FAST flexor + FAST extensor
    (both fast) -> the honest antagonist contrast is family-level
    (jump vs leg), not flexor-vs-extensor; we run the L17-style pair
    contrast anyway with the measured fast side to close that question.

Arm A (DT 10 ms, decay side):
  homog    tau .05 everywhere (L17 anchor; leads ~0 expected).
  lit{r}   ext = .051 (measured TDT deact), flex = .051*r, r in {2,3,5}
           (real arm only -> emergence threshold).
  lit5rev  reverse assignment at 5x (sign-opposite check).
  shuf     5 draws: the 5x tau multiset permuted over the pool union
           (the null for the gate).

Arm B (DT 2 ms downshift, twitch side):
  homog    all .051 (op-point + pair leads ~0 at fine DT).
  lit      TTMn = .004 (measured twitch <5 ms), leg pools .051.
  shuf     5 draws: same multiset over TTMn+leg union.

Gate (queue): do MEASURED-tau leads still clear the tau-shuffle null, or
does phasing live only at unrealistic contrast? Sub-step separations are
reported as the model's temporal-resolution floor. No wiring claim: the
graph is identical in every arm; only taus move.
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
BG, NOISE, RMAX = 0.02, 0.01, 1.0
GAIN = 0.8846          # op-point bisected in L11 (16.4% active at DT .01)
AMP = 2.0              # l16/l17 cord mechano amplitude
SEEDS = [11, 22, 33]
NDRAW = 5
SETTLE = 300

# literature anchors (LANE-RESEARCH.md tick 29)
TAU_DEACT = 0.051      # TDT myofibril relaxation, MEASURED
TAU_TWITCH = 0.004     # TDT twitch <5 ms, MEASURED
RATIOS = [2.0, 3.0, 5.0]   # tonic slow side, UNDERDETERMINED (sweep)

ap = argparse.ArgumentParser()
ap.add_argument("arm", choices=["A", "B"])
ARGS = ap.parse_args()

os.makedirs("l18", exist_ok=True)
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

PAIRS = {
    "Ti": (np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
           np.where(typm == "Ti extensor MN")[0]),
    "Tr": (np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0],
           np.where(typm == "Tr extensor MN")[0]),
}
POOL_F = np.concatenate([PAIRS["Ti"][0], PAIRS["Tr"][0]])
POOL_E = np.concatenate([PAIRS["Ti"][1], PAIRS["Tr"][1]])
TTM = np.where(np.array([str(t).startswith("TTMn") for t in typm]))[0]
IFM = np.where(np.array([str(t).startswith(("DLMn", "DVMn"))
                         for t in typm]))[0]
LEG_U = np.concatenate([POOL_F, POOL_E])          # leg-family union
for k, (f, e) in PAIRS.items():
    assert len(f) > 0 and len(e) > 0
assert len(TTM) > 0
print(f"motor {M} | cord mechano {len(cord_mech)} | TTMn {len(TTM)} | "
      f"IFM(DLMn/DVMn, async -> base tau) {len(IFM)} | leg pools "
      f"flex {len(POOL_F)} / ext {len(POOL_E)}", flush=True)

DT = 0.010 if ARGS.arm == "A" else 0.002
EVENT, POST = 20, 220
T = EVENT + POST


def run_gesture(tv, seed):
    tau = torch.from_numpy(tv).unsqueeze(1)
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[cord_mech] = AMP
    for _ in range(SETTLE):
        step(Z)
    af = float((X > 0.05).float().mean())
    base = X[motor].squeeze(1).numpy().copy()
    rec = np.zeros((M, T), dtype=np.float32)
    for k in range(T):
        step(I0 if k < EVENT else Z)
        rec[:, k] = X[motor].squeeze(1).numpy() - base
    return rec, af


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


def half_time(p):
    pk = float(p.max()); tp = int(np.argmax(p))
    below = np.where(p[tp:] < 0.5 * pk)[0]
    return int(tp + below[0]) if len(below) else T


def t_pk(p):
    return int(np.argmax(p))


if ARGS.arm == "A":
    def tau_vec(arm, rng=None):
        tv = np.full(N, 0.05, np.float32)
        if arm == "homog":
            pass
        elif arm == "lit5rev":
            tv[motor[POOL_F]] = TAU_DEACT
            tv[motor[POOL_E]] = TAU_DEACT * 5.0
        elif arm.startswith("lit"):
            r = float(arm[3:].replace("x", ""))
            tv[motor[POOL_E]] = TAU_DEACT
            tv[motor[POOL_F]] = TAU_DEACT * r
        elif arm.startswith("shuf"):
            vals = np.array([TAU_DEACT] * len(POOL_E)
                            + [TAU_DEACT * 5.0] * len(POOL_F), np.float32)
            vals = vals[rng.permutation(len(vals))]
            tv[motor[np.concatenate([POOL_F, POOL_E])]] = vals
        else:
            raise ValueError(arm)
        return tv

    def arm_summary(recs, afs, label):
        flat = [r.ravel() for r in recs]
        out = {"label": label, "af": float(np.mean(afs)),
               "st_self_cos": float(np.mean([cos(flat[i], flat[j])
                                             for i in range(len(flat))
                                             for j in range(i + 1, len(flat))]))}
        for k, (f, e) in PAIRS.items():
            leads, halves = [], []
            for r in recs:
                pf, pe = r[f].mean(0), r[e].mean(0)
                leads.append(t_pk(pe) - t_pk(pf))
                halves.append((half_time(pf), half_time(pe)))
            out[f"{k}_leads"] = leads
            out[f"{k}_lead_mean"] = float(np.mean(leads))
            out[f"{k}_sign_consistent"] = bool(all(l > 0 for l in leads)
                                               or all(l < 0 for l in leads))
            out[f"{k}_half_flex"] = float(np.mean([h[0] for h in halves]))
            out[f"{k}_half_ext"] = float(np.mean([h[1] for h in halves]))
        return out

    RUNS = ["homog", "lit2x", "lit3x", "lit5x", "lit5rev"]
    ARMS, AFS = {}, {}
    for arm in RUNS:
        recs, afs = [], []
        for s in SEEDS:
            r, af = run_gesture(tau_vec(arm), s)
            recs.append(r); afs.append(af)
        ARMS[arm] = arm_summary(recs, afs, arm)
        AFS[arm] = afs
        a_ = ARMS[arm]
        print(f"{arm}: Ti lead {a_['Ti_lead_mean']:+.1f} {a_['Ti_leads']} "
              f"sc={a_['Ti_sign_consistent']} | Tr lead "
              f"{a_['Tr_lead_mean']:+.1f} {a_['Tr_leads']} "
              f"sc={a_['Tr_sign_consistent']} | half f/e "
              f"{a_['Ti_half_flex']:.0f}/{a_['Ti_half_ext']:.0f} | "
              f"af {a_['af']:.4f} | {time.time()-t0:.0f}s", flush=True)

    rng = np.random.default_rng(20261110 + 18)
    SHUF = []
    for d in range(NDRAW):
        recs, afs = [], []
        for s in SEEDS:
            r, af = run_gesture(tau_vec("shuf", rng), s)
            recs.append(r); afs.append(af)
        SHUF.append(arm_summary(recs, afs, f"shuf{d}"))
        s_ = SHUF[-1]
        print(f"shuf{d}: Ti lead {s_['Ti_lead_mean']:+.1f} {s_['Ti_leads']} "
              f"sc={s_['Ti_sign_consistent']} | Tr lead "
              f"{s_['Tr_lead_mean']:+.1f} {s_['Tr_leads']} "
              f"sc={s_['Tr_sign_consistent']} | {time.time()-t0:.0f}s",
              flush=True)

    nv = {k: {"leads": [x[f"{k}_lead_mean"] for x in SHUF],
              "max_abs": float(max(abs(x[f"{k}_lead_mean"]) for x in SHUF)),
              "sc_count": int(sum(x[f"{k}_sign_consistent"] for x in SHUF))}
          for k in ["Ti", "Tr"]}
    gate5 = {k: bool(abs(ARMS["lit5x"][f"{k}_lead_mean"]) > nv[k]["max_abs"]
                     and ARMS["lit5x"][f"{k}_sign_consistent"])
             for k in ["Ti", "Tr"]}
    print(f"\nNULL(5x): Ti max|lead| {nv['Ti']['max_abs']:.1f} "
          f"sc {nv['Ti']['sc_count']}/5 | Tr max|lead| "
          f"{nv['Tr']['max_abs']:.1f} sc {nv['Tr']['sc_count']}/5", flush=True)
    print(f"lit5x clears null: {gate5} | emergence: "
          + ", ".join(f"{a}:{ARMS[a]['Ti_lead_mean']:+.1f}/{ARMS[a]['Tr_lead_mean']:+.1f}"
                      for a in ["lit2x", "lit3x", "lit5x"]), flush=True)
    res = {"config": {"arm": "A", "DT": DT, "EVENT": EVENT, "POST": POST,
                      "T": T, "settle": SETTLE, "gain": GAIN, "amp": AMP,
                      "seeds": SEEDS, "ndraw": NDRAW,
                      "tau_deact": TAU_DEACT, "ratios": RATIOS,
                      "ttm": int(len(TTM)), "ifm_excluded": int(len(IFM)),
                      "pools": {"flex": int(len(POOL_F)),
                                "ext": int(len(POOL_E))}},
           "arms": ARMS, "shuffle_nulls": SHUF, "null_agg": nv,
           "gate_lit5x_clears_null": gate5}
    json.dump(res, open("l18/results_l18_A.json", "w"), indent=1)
else:
    def tau_vec(arm, rng=None):
        tv = np.full(N, 0.05, np.float32)
        if arm == "homog":
            tv[motor[LEG_U]] = TAU_DEACT
        elif arm == "lit":
            tv[motor[TTM]] = TAU_TWITCH
            tv[motor[LEG_U]] = TAU_DEACT
        elif arm.startswith("shuf"):
            vals = np.array([TAU_TWITCH] * len(TTM)
                            + [TAU_DEACT] * len(LEG_U), np.float32)
            assert len(vals) == len(TTM) + len(LEG_U)
            vals = vals[rng.permutation(len(vals))]
            tv[motor[np.concatenate([TTM, LEG_U])]] = vals
        else:
            raise ValueError(arm)
        return tv

    def arm_summary(recs, afs, label):
        flat = [r.ravel() for r in recs]
        out = {"label": label, "af": float(np.mean(afs)),
               "st_self_cos": float(np.mean([cos(flat[i], flat[j])
                                             for i in range(len(flat))
                                             for j in range(i + 1, len(flat))]))}
        jt = [r[TTM].mean(0) for r in recs]
        out["ttm_half"] = float(np.mean([half_time(p) for p in jt]))
        out["ttm_t_pk"] = [t_pk(p) for p in jt]
        for k, (f, e) in PAIRS.items():
            pair = np.concatenate([f, e])
            leads = [t_pk(r[TTM].mean(0)) - t_pk(r[pair].mean(0))
                     for r in recs]
            out[f"{k}_jump_minus_leg_leads"] = leads
            out[f"{k}_jump_lead_mean"] = float(np.mean(leads))
            out[f"{k}_jump_sign_consistent"] = bool(
                all(l > 0 for l in leads) or all(l < 0 for l in leads))
            out[f"{k}_half_leg"] = float(np.mean(
                [half_time(r[pair].mean(0)) for r in recs]))
            out[f"{k}_pair_leads"] = [t_pk(r[e].mean(0)) - t_pk(r[f].mean(0))
                                      for r in recs]
        return out

    RUNS = ["homog", "lit"]
    ARMS = {}
    for arm in RUNS:
        recs, afs = [], []
        for s in SEEDS:
            r, af = run_gesture(tau_vec(arm), s)
            recs.append(r); afs.append(af)
        ARMS[arm] = arm_summary(recs, afs, arm)
        a_ = ARMS[arm]
        print(f"{arm}: jump-lead vs Ti {a_['Ti_jump_lead_mean']:+.1f} "
              f"{a_['Ti_jump_minus_leg_leads']} sc="
              f"{a_['Ti_jump_sign_consistent']} | vs Tr "
              f"{a_['Tr_jump_lead_mean']:+.1f} {a_['Tr_jump_minus_leg_leads']} "
              f"sc={a_['Tr_jump_sign_consistent']} | ttm half "
              f"{a_['ttm_half']:.0f} vs leg {a_['Ti_half_leg']:.0f} | "
              f"pair lead Ti {a_['Ti_pair_leads']} | af {a_['af']:.4f} | "
              f"{time.time()-t0:.0f}s", flush=True)
        if arm == "lit":
            np.savez_compressed("l18/ttm_mean_tensor_B.npz",
                                lit=np.mean(recs, axis=0),
                                ttm=TTM, leg_u=LEG_U,
                                **{f"{k}_f": v[0] for k, v in PAIRS.items()},
                                **{f"{k}_e": v[1] for k, v in PAIRS.items()})

    rng = np.random.default_rng(20261110 + 19)
    SHUF = []
    for d in range(NDRAW):
        recs, afs = [], []
        for s in SEEDS:
            r, af = run_gesture(tau_vec("shuf", rng), s)
            recs.append(r); afs.append(af)
        SHUF.append(arm_summary(recs, afs, f"shuf{d}"))
        s_ = SHUF[-1]
        print(f"shuf{d}: jump-lead vs Ti {s_['Ti_jump_lead_mean']:+.1f} "
              f"sc={s_['Ti_jump_sign_consistent']} | vs Tr "
              f"{s_['Tr_jump_lead_mean']:+.1f} sc="
              f"{s_['Tr_jump_sign_consistent']} | {time.time()-t0:.0f}s",
              flush=True)

    nv = {k: {"leads": [x[f"{k}_jump_lead_mean"] for x in SHUF],
              "max_abs": float(max(abs(x[f"{k}_jump_lead_mean"])
                                   for x in SHUF)),
              "sc_count": int(sum(x[f"{k}_jump_sign_consistent"]
                                  for x in SHUF))}
          for k in ["Ti", "Tr"]}
    gate = {k: bool(abs(ARMS["lit"][f"{k}_jump_lead_mean"]) > nv[k]["max_abs"]
                    and ARMS["lit"][f"{k}_jump_sign_consistent"])
            for k in ["Ti", "Tr"]}
    print(f"\nNULL: Ti max|lead| {nv['Ti']['max_abs']:.1f} "
          f"sc {nv['Ti']['sc_count']}/5 | Tr max|lead| "
          f"{nv['Tr']['max_abs']:.1f} sc {nv['Tr']['sc_count']}/5", flush=True)
    print(f"lit (TTMn 4ms twitch tau) clears null: {gate}", flush=True)
    res = {"config": {"arm": "B", "DT": DT, "EVENT": EVENT, "POST": POST,
                      "T": T, "settle": SETTLE, "gain": GAIN, "amp": AMP,
                      "seeds": SEEDS, "ndraw": NDRAW,
                      "tau_twitch": TAU_TWITCH, "tau_deact": TAU_DEACT,
                      "ttm": int(len(TTM)), "ifm_excluded": int(len(IFM)),
                      "pools": {"flex": int(len(POOL_F)),
                                "ext": int(len(POOL_E))}},
           "arms": ARMS, "shuffle_nulls": SHUF, "null_agg": nv,
           "gate_lit_clears_null": gate}
    json.dump(res, open("l18/results_l18_B.json", "w"), indent=1)

print(f"done {time.time()-t0:.0f}s -> l18/results_l18_{ARGS.arm}.json",
      flush=True)
