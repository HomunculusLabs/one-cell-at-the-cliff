"""L19: full-chain escape gesture — the first honest whole-path demo.

Chain (each link shipped standalone; this run strings them into ONE trace):
  looming volley at LC4/LC16/LC11/LC12 (L11 event class)
    -> DN port event (L11: read the DN population AT ITS peak)
    -> per-class amplified DN->motor edges, DNp01-04 x200 + DNc01/02 x200
       (L13b machinery verbatim, g=200)
    -> lit5x decay-side tau tiers on the antagonist pools
       (L18 Arm A: ext 51 ms MEASURED TDT relaxation / flex 255 ms
       underdetermined-swept tonic; base .05 elsewhere, IFM base tau)
    -> full motor cells-x-time difference tensor = the gesture.

Metrics reproduced INSIDE the chain (the verify line):
  L11 : DN-port vector self-cos across seeds + DNp01-04 vs DNc01/02 loading.
  L13b: peak motor-vector self-cos; clamp-DNp kill; loom~odor cross-cos.
  L17/18: Ti/Tr ext-minus-flex leads, sign-consistency 3/3 vs tau-shuffle
        null (5 draws, same multiset, random cells — looming drive now).
  L14/15: top-6 |dm| mass share time-integrated vs chance 6/M.
  L18B expectation check: jump family (TTMn) leg-phased, not jump-first.

DESCRIPTIVE ONLY (owner movement law): lab evidence, never app-side motion.
CPU-only (8 threads) — the live duck keeps the GPU.
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU_BASE, DT, RMAX = 0.05, 0.010, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, EVENT, POST = 300, 20, 220
T = EVENT + POST
GAIN = 0.8846            # op point bisected in L11
G = 200.0                # per-class pathway gain (L13b's .971 setting)
AMP_EV = 8.0             # L13b event amplitude
SEEDS = [11, 22, 33]
NDRAW = 5
TAU_DEACT = 0.051        # MEASURED TDT relaxation (tick 29)
RATIO = 5.0              # lit5x — the calibrated arm that cleared L18's gate

os.makedirs("l19", exist_ok=True)
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
side = lab["somaSide"].astype(str).to_numpy()

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
mL = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]) & (side == "L"))[0]
mR = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]) & (side == "R"))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
olf = np.where(cls == "olfactory")[0]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(leg_dns) == 8 and len(neck_dns) == 4
typm = typ[motor]
M = len(motor)
PAIRS = {
    "Ti": (np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
           np.where(typm == "Ti extensor MN")[0]),
    "Tr": (np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0],
           np.where(typm == "Tr extensor MN")[0]),
}
POOL_F = np.concatenate([PAIRS["Ti"][0], PAIRS["Tr"][0]])
POOL_E = np.concatenate([PAIRS["Ti"][1], PAIRS["Tr"][1]])
TTM = np.where(np.array([str(t).startswith("TTMn") for t in typm]))[0]
for k, (f, e) in PAIRS.items():
    assert len(f) > 0 and len(e) > 0
assert len(TTM) > 0
print(f"motor {M} | loom {len(loom)} | olf {len(olf)} | legDN {len(leg_dns)} "
      f"| neckDN {len(neck_dns)} | TTMn {len(TTM)} | pools flex "
      f"{len(POOL_F)} / ext {len(POOL_E)}", flush=True)

# --- L13b per-class amplification, verbatim -------------------------------
rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
cols = W.col_indices().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
emask_leg = torch.from_numpy(mrow[rows.numpy()] & leg_src[cols])
emask_neck = torch.from_numpy(mrow[rows.numpy()] & neck_src[cols])
Wv = W.values()
Wg = W.clone()
v = Wg.values()
v[emask_leg] = Wv[emask_leg] * G
v[emask_neck] = Wv[emask_neck] * G
print(f"amplified x{G:.0f}: leg {int(emask_leg.sum())} + neck "
      f"{int(emask_neck.sum())} DN->motor edges", flush=True)

# --- L18 Arm A tau vectors ------------------------------------------------


def tau_vec(arm, rng=None):
    tv = np.full(N, TAU_BASE, np.float32)
    if arm == "homog":
        pass
    elif arm == "lit5x":
        tv[motor[POOL_E]] = TAU_DEACT
        tv[motor[POOL_F]] = TAU_DEACT * RATIO
    elif arm == "lit5rev":
        tv[motor[POOL_F]] = TAU_DEACT
        tv[motor[POOL_E]] = TAU_DEACT * RATIO
    elif arm.startswith("shuf"):
        vals = np.array([TAU_DEACT] * len(POOL_E)
                        + [TAU_DEACT * RATIO] * len(POOL_F), np.float32)
        vals = vals[rng.permutation(len(vals))]
        tv[motor[np.concatenate([POOL_E, POOL_F])]] = vals
    else:
        raise ValueError(arm)
    return tv


def run_chain(channel, tv, seed, clamp=None):
    """One full-chain rollout: event at `channel`, record the whole gesture."""
    tau = torch.from_numpy(tv).unsqueeze(1)
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(Wg, X) + I      # [N,1] operands — never 1-D
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[channel] = AMP_EV
    for _ in range(SETTLE):
        step(Z)
    af = float((X > 0.05).float().mean())
    base_m = X[motor].squeeze(1).numpy().copy()
    base_dn = X[dn].squeeze(1).numpy().copy()
    base_turn = ((X[mL].mean() - X[mR].mean())
                 / (X[mL].mean() + X[mR].mean() + 1e-9)).item()
    rec = np.zeros((M, T), dtype=np.float32)
    dn_pk, m_pk = -1.0, -1.0
    dn_vec = np.zeros(len(dn), np.float32)
    dm_pk = np.zeros(M, np.float32)
    turn_pk = 0.0
    for k in range(T):
        step(I0 if k < EVENT else Z)
        rec[:, k] = X[motor].squeeze(1).numpy() - base_m
        mdn = float(X[dn].mean())
        if mdn > dn_pk:
            dn_pk = mdn
            dn_vec = X[dn].squeeze(1).numpy() - base_dn
        mm = float(X[motor].mean())
        if mm > m_pk:
            m_pk = mm
            dm_pk = X[motor].squeeze(1).numpy() - base_m
            turn_pk = ((X[mL].mean() - X[mR].mean())
                       / (X[mL].mean() + X[mR].mean() + 1e-9)
                       - base_turn).item()
    return dict(rec=rec, dn_vec=dn_vec, dm_pk=dm_pk, af=af,
                mbase=float(base_m.mean()), turn=turn_pk)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


def t_pk(p):
    return int(np.argmax(p))


def leads_of(rec):
    out = {}
    for k, (f, e) in PAIRS.items():
        out[k] = [t_pk(r[e].mean(0)) - t_pk(r[f].mean(0)) for r in rec]
    return out


# --- the chain arms --------------------------------------------------------
TAU_ARM = {"loom": "lit5x", "loom_clampDNp": "lit5x", "odor": "lit5x",
           "loom_homog": "homog", "loom_lit5rev": "lit5rev"}
ARMS = {}
for arm, ch, clamp in [
    ("loom", loom, None),            # THE chain
    ("loom_clampDNp", loom, leg_dns),  # L13b kill test
    ("odor", olf, None),             # cross-event arm
    ("loom_homog", loom, None),      # phasing control (L18 anchor)
    ("loom_lit5rev", loom, None),    # sign-opposite check
]:
    runs = [run_chain(ch, tau_vec(TAU_ARM[arm]), s, clamp=clamp)
            for s in SEEDS]
    ARMS[arm] = runs
    ld = leads_of([r["rec"] for r in runs])
    print(f"{arm:14s} af {np.mean([r['af'] for r in runs]):.4f} "
          f"mbase {np.mean([r['mbase'] for r in runs]):.4f} "
          f"turn {np.mean([r['turn'] for r in runs]):+.4f} | leads "
          + " ".join(f"{k} {ld[k]}" for k in PAIRS)
          + f" | {time.time() - t0:.0f}s", flush=True)

rng = np.random.default_rng(20261111 + 19)
SHUF = []
for d in range(NDRAW):
    runs = [run_chain(loom, tau_vec("shuf", rng), s) for s in SEEDS]
    SHUF.append(runs)
    ld = leads_of([r["rec"] for r in runs])
    print(f"shuf{d}          leads "
          + " ".join(f"{k} {ld[k]}" for k in PAIRS)
          + f" | {time.time() - t0:.0f}s", flush=True)

# --- metric 1: DN port (L11) ----------------------------------------------
loom_ = ARMS["loom"]
dn_self = float(np.mean([cos(loom_[i]["dn_vec"], loom_[j]["dn_vec"])
                         for i in range(3) for j in range(i + 1, 3)]))
dn_cross = float(np.mean([cos(loom_[i]["dn_vec"], ARMS["odor"][j]["dn_vec"])
                          for i in range(3) for j in range(3)]))
dn_mean = np.mean([r["dn_vec"] for r in loom_], axis=0)
ldn = np.zeros(len(dn), bool); ldn[np.isin(dn, leg_dns)] = True
ndn = np.zeros(len(dn), bool); ndn[np.isin(dn, neck_dns)] = True
dn_abs = np.abs(dn_mean)
dn_load = {"DNp0104": float(dn_abs[ldn].sum() / (dn_abs.sum() + 1e-12)),
           "DNc0102": float(dn_abs[ndn].sum() / (dn_abs.sum() + 1e-12)),
           "n_dn": int(len(dn)), "n_dnp": int(ldn.sum()), "n_dnc": int(ndn.sum())}
print(f"\nL11 DN port: self-cos {dn_self:+.3f} cross loom~odor {dn_cross:+.3f} "
      f"| loading DNp01-04 {dn_load['DNp0104']:.3f} vs DNc01/02 "
      f"{dn_load['DNc0102']:.3f}", flush=True)

# --- metric 2: peak motor command (L13b) -----------------------------------
m_self = float(np.mean([cos(loom_[i]["dm_pk"], loom_[j]["dm_pk"])
                        for i in range(3) for j in range(i + 1, 3)]))
m_cross = float(np.mean([cos(loom_[i]["dm_pk"], ARMS["odor"][j]["dm_pk"])
                         for i in range(3) for j in range(3)]))
cl = ARMS["loom_clampDNp"]
cl_self = float(np.mean([cos(cl[i]["dm_pk"], cl[j]["dm_pk"])
                         for i in range(3) for j in range(i + 1, 3)]))
cl_vs = float(cos(np.mean([r["dm_pk"] for r in cl], axis=0),
                  np.mean([r["dm_pk"] for r in loom_], axis=0)))
o_self = float(np.mean([cos(ARMS["odor"][i]["dm_pk"], ARMS["odor"][j]["dm_pk"])
                        for i in range(3) for j in range(i + 1, 3)]))
print(f"L13b motor peak: loom self {m_self:+.3f} | odor self {o_self:+.3f} "
      f"| cross {m_cross:+.3f} | clampDNp self {cl_self:+.3f} "
      f"(vs chain {cl_vs:+.3f})", flush=True)

# --- metric 3: antagonist phasing (L17/L18) -------------------------------
ph = {}
for arm in ["loom", "loom_homog", "loom_lit5rev"]:
    ld = leads_of([r["rec"] for r in ARMS[arm]])
    ph[arm] = {k: {"leads": ld[k],
                   "mean": float(np.mean(ld[k])),
                   "sc": bool(all(x > 0 for x in ld[k])
                              or all(x < 0 for x in ld[k]))} for k in PAIRS}
nmax = {k: float(max(abs(float(np.mean(leads_of([r["rec"] for r in SHUF[d]])[k])))
                     for d in range(NDRAW))) for k in PAIRS}
gate = {k: bool(ph["loom"][k]["sc"]
                and abs(ph["loom"][k]["mean"]) > nmax[k]) for k in PAIRS}
print(f"L17/18 phasing: chain lit5x leads "
      + " ".join(f"{k} {ph['loom'][k]['leads']}" for k in PAIRS)
      + f" | null(5x draw) max|lead| "
      + " ".join(f"{k} {nmax[k]:.1f}" for k in PAIRS)
      + f" | clears null {gate}", flush=True)

# --- metric 4: anatomy through time (L14/L15) ------------------------------
tens = np.mean([r["rec"] for r in loom_], axis=0)   # seed-mean tensor
mass_t = np.abs(tens).sum(1)                        # time-integrated |dm|
top6 = np.argsort(-mass_t)[:6]
top6_share = float(mass_t[top6].sum() / (mass_t.sum() + 1e-12))
chance6 = 6.0 / M
print(f"L14/15 anatomy: top-6 time-integrated mass {top6_share:.4f} "
      f"vs chance {chance6:.4f} | top cells "
      + ", ".join(f"{typm[t]}" for t in top6), flush=True)

# --- metric 5: jump-family timing (L18 B expectation) ----------------------
ttm_tpk = [t_pk(r["rec"][TTM].mean(0)) for r in loom_]
leg_u = np.concatenate([POOL_F, POOL_E])
leg_tpk = [t_pk(r["rec"][leg_u].mean(0)) for r in loom_]
jump_label = ("LEG-PHASED (jump lags)"
              if np.mean(ttm_tpk) > np.mean(leg_tpk) else "jump-first")
print(f"L18B jump timing: TTMn t_pk {ttm_tpk} vs leg pools {leg_tpk} "
      f"-> {jump_label}", flush=True)

# --- artifacts ---------------------------------------------------------------
np.savez_compressed("l19/gesture_mean.npz", tensor=tens, top6=top6,
                    **{f"{k}_f": v[0] for k, v in PAIRS.items()},
                    **{f"{k}_e": v[1] for k, v in PAIRS.items()},
                    ttm=TTM, leg_u=leg_u)
res = {
    "config": dict(DT=DT, EVENT=EVENT, POST=POST, T=T, settle=SETTLE,
                   gain=GAIN, g_path=G, amp_ev=AMP_EV, seeds=SEEDS,
                   ndraw=NDRAW, tau_deact=TAU_DEACT, ratio=RATIO,
                   motor=M, pools={"flex": len(POOL_F), "ext": len(POOL_E)},
                   ttm=len(TTM), loom=len(loom), olf=len(olf)),
    "dn_port": {"self_cos": dn_self, "cross_cos": dn_cross, "loading": dn_load},
    "motor_peak": {"loom_self": m_self, "odor_self": o_self,
                   "cross": m_cross, "clamp_self": cl_self, "clamp_vs": cl_vs,
                   "turn": [r["turn"] for r in loom_]},
    "phasing": ph, "null_max_abs_lead": nmax, "gate_clears_null": gate,
    "anatomy": {"top6_share": top6_share, "chance": chance6,
                "top6_names": [str(typm[t]) for t in top6]},
    "jump_timing": {"ttm": ttm_tpk, "leg": leg_tpk},
    "af": {a: float(np.mean([r["af"] for r in ARMS[a]])) for a in ARMS},
}
json.dump(res, open("l19/results_l19.json", "w"), indent=1)
print(f"\ndone {time.time() - t0:.0f}s -> l19/results_l19.json", flush=True)
