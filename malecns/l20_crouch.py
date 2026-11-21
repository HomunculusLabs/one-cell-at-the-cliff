"""L20 stage 2: the crouch-then-jump two-phase descriptive gesture.

Stage 1 (l20_scan.py) found the flexor DN channel: DNg-family classes
(DNg105/DNg95/DNge079/DNg74_b/DNg35/DNg108 — 2 cells each, 35-80% of their
motor weight onto Ti/Tr flexor MNs, z +13..+25 vs MS null) while DNp01-04
is jump/extensor-pure. Upstream of the DNg crouch cells is cord-intrinsic +
ascending (no direct sensory route) — so the crouch is driven here as a
direct DN volley (optogenetic-style), labeled as such.

Protocol (L19 machinery verbatim: lit5x decay-side taus, per-class x200):
  0. SNR GATE (L19 rule, BEFORE any phasing claim): crouch volley alone —
     flexor pool must clear noise (>=3x); clamp-DNg must kill it.
  1. crouch_only   — DNg volley, no stroke: theta dips, no swing.
  2. stroke_only   — DNp01-04 volley, no crouch: theta swings, no dip.
  3. two_phase     — crouch volley at k=0 (C steps), DNp01-04 volley at
     k=DEL, DEL in {30, 60, 100}: theta(t) = ext - flex (joint proxy)
     becomes BIPHASIC — trough (crouch) BEFORE peak (stroke).

Pre-registered biphasic verdict: in ALL seeds, argmin(theta) < argmax(theta),
|trough| > 3*theta_tail_noise, trough earlier than the stroke peak, and
two-phase trough deeper than stroke_only trough.

DESCRIPTIVE ONLY (owner movement law). CPU-only, 8 threads.
"""
import json
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU_BASE, DT, RMAX = 0.05, 0.010, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, POST = 300, 300
GAIN = 0.8846
G = 200.0
AMP_EV = 8.0
SEEDS = [11, 22, 33]
CROUCH_STEPS = 20
STROKE_STEPS = 20
DELS = [30, 60, 100]
TAU_DEACT, RATIO = 0.051, 5.0
CROUCH_TYPES = ["DNg105", "DNg95", "DNge079", "DNg74_b", "DNg35", "DNg108"]

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].fillna("").astype(str).to_numpy()
typ = lab["type"].fillna("").astype(str).to_numpy()

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
crouch_dns = dn[np.isin(dn_typ, CROUCH_TYPES)]
assert len(leg_dns) == 8
assert len(crouch_dns) == 2 * len(CROUCH_TYPES), len(crouch_dns)
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
assert len(POOL_F) > 0 and len(POOL_E) > 0 and len(TTM) > 0

rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
cols = W.col_indices().numpy()
rows_np = rows.numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
cro_src = np.zeros(N, bool); cro_src[crouch_dns] = True
is_flex_m = np.zeros(M, bool); is_flex_m[POOL_F] = True
flex_dst = np.zeros(N, bool); flex_dst[motor[POOL_F]] = True
emask_leg = torch.from_numpy(mrow[rows_np] & leg_src[cols])
emask_cro = torch.from_numpy(mrow[rows_np] & cro_src[cols] & flex_dst[rows_np])
Wv = W.values()
Wg = W.clone()
v = Wg.values()
v[emask_leg] = Wv[emask_leg] * G
v[emask_cro] = Wv[emask_cro] * G
n_cro = int(emask_cro.sum())
assert n_cro > 0, "empty crouch edge set would fake the comparison"
print(f"amplified: DNp01-04->motor {int(emask_leg.sum())} edges | "
      f"{'/'.join(CROUCH_TYPES)}->flexor {n_cro} edges x{G:.0f} | "
      f"crouch cells {len(crouch_dns)} | {time.time()-t0:.0f}s", flush=True)

tv = np.full(N, TAU_BASE, np.float32)
tv[motor[POOL_E]] = TAU_DEACT
tv[motor[POOL_F]] = TAU_DEACT * RATIO
tau = torch.from_numpy(tv).unsqueeze(1)


def run(seed, crouch=True, stroke=True, del_=60, clamp=None):
    """One rollout. Crouch volley [0,C), stroke volley [del_, del_+S)."""
    T = max(DELS) + STROKE_STEPS + POST
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(Wg, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0

    Z = torch.zeros(N, 1)
    Ic, Is = Z.clone(), Z.clone()
    if crouch:
        Ic[crouch_dns] = AMP_EV
    if stroke:
        Is[leg_dns] = AMP_EV
    for _ in range(SETTLE):
        step(Z)
    base_m = X[motor].squeeze(1).numpy().copy()
    rec = np.zeros((M, T), np.float32)
    for k in range(T):
        I = Z
        if crouch and k < CROUCH_STEPS:
            I = Ic
        elif stroke and del_ <= k < del_ + STROKE_STEPS:
            I = Is
        step(I)
        rec[:, k] = X[motor].squeeze(1).numpy() - base_m
    return rec


def pool_peak_snr(rec, idx):
    tail = rec[:, -150:]
    floor = float(np.mean(tail.std(axis=1))) + 1e-12
    amp = float(np.abs(rec[idx]).max(axis=1).mean())
    return amp, amp / floor, floor


def theta_of(rec):
    return rec[POOL_E].mean(0) - rec[POOL_F].mean(0)


# --- 0. SNR gate: crouch volley alone --------------------------------------
res = {"crouch_types": CROUCH_TYPES, "n_crouch_edges": n_cro}
snr_arm = [run(s, crouch=True, stroke=False) for s in SEEDS]
clamp_arm = [run(s, crouch=True, stroke=False, clamp=crouch_dns) for s in SEEDS]
gate = {}
for name, idx in [("flex", POOL_F), ("ext", POOL_E), ("TTMn", TTM)]:
    a = np.mean([pool_peak_snr(r, idx)[1] for r in snr_arm])
    c = np.mean([pool_peak_snr(r, idx)[1] for r in clamp_arm])
    gate[name] = {"crouch_snr": float(a), "clamp_snr": float(c)}
    print(f"SNR gate {name:5s}: crouch {a:7.1f}x | clamp-DNg {c:5.1f}x", flush=True)
res["snr_gate"] = gate
FLEX_GATE = gate["flex"]["crouch_snr"] >= 3.0 and \
    gate["flex"]["clamp_snr"] < 0.5 * gate["flex"]["crouch_snr"]
print(f"FLEX SNR GATE: {'PASS' if FLEX_GATE else 'FAIL'} "
      f"(L19 rule — no phasing claim if undriven) | {time.time()-t0:.0f}s",
      flush=True)

# --- 1+2. crouch-only / stroke-only ----------------------------------------
cro_only = [run(s, crouch=True, stroke=False) for s in SEEDS]
str_only = [run(s, crouch=False, stroke=True, del_=60) for s in SEEDS]


def theta_stats(recs):
    out = []
    tail = np.concatenate([theta_of(r)[-150:] for r in recs])
    tn = float(tail.std()) + 1e-12
    for r in recs:
        th = theta_of(r)
        out.append(dict(trough=float(th.min()), t_trough=int(np.argmin(th)),
                        peak=float(th.max()), t_peak=int(np.argmax(th))))
    return out, tn


co, theta_noise = theta_stats(cro_only)
so, _ = theta_stats(str_only)
res["theta_noise"] = theta_noise
res["crouch_only"] = co
res["stroke_only"] = so
print(f"theta tail noise {theta_noise:.5f} | crouch-only trough "
      f"{np.mean([x['trough'] for x in co]):+.4f} (peak "
      f"{np.mean([x['peak'] for x in co]):+.4f}) | stroke-only peak "
      f"{np.mean([x['peak'] for x in so]):+.4f} (trough "
      f"{np.mean([x['trough'] for x in so]):+.4f}) | {time.time()-t0:.0f}s",
      flush=True)

# --- 3. two-phase, DEL sweep -------------------------------------------------
two = {}
biphasic = {}
for d in DELS:
    recs = [run(s, crouch=True, stroke=True, del_=d) for s in SEEDS]
    th = [theta_of(r) for r in recs]
    st = []
    for t_ in th:
        st.append(dict(trough=float(t_.min()), t_trough=int(np.argmin(t_)),
                       peak=float(t_.max()), t_peak=int(np.argmax(t_))))
    ttm_tpk = [int(np.argmax(r[TTM].mean(0))) for r in recs]
    ok = all(s["t_trough"] < s["t_peak"] and s["trough"] < -3 * theta_noise
             and s["peak"] > 3 * theta_noise for s in st)
    ok = ok and np.mean([s["trough"] for s in st]) < \
        np.mean([s["trough"] for s in so]) - theta_noise
    ok = ok and all(tp > d for tp in ttm_tpk)
    two[d] = {"theta": st, "ttm_tpk": ttm_tpk}
    biphasic[d] = bool(ok and FLEX_GATE)
    print(f"two-phase DEL={d:3d}: trough {np.mean([s['trough'] for s in st]):+.4f}"
          f" @ {np.mean([s['t_trough'] for s in st]):5.1f} | peak "
          f"{np.mean([s['peak'] for s in st]):+.4f} @ "
          f"{np.mean([s['t_peak'] for s in st]):5.1f} | TTMn t_pk {ttm_tpk} "
          f"| BIPHASIC {biphasic[d]} | {time.time()-t0:.0f}s", flush=True)

res["two_phase"] = two
res["biphasic"] = biphasic
res["flex_gate_pass"] = bool(FLEX_GATE)

# save theta traces + pool means of the best DEL for the figure
best = max(DELS, key=lambda d: biphasic[d])
recs = [run(s, crouch=True, stroke=True, del_=best) for s in SEEDS]
np.savez_compressed(
    "l20/two_phase.npz",
    theta=np.stack([theta_of(r) for r in recs]),
    flex=np.stack([r[POOL_F].mean(0) for r in recs]),
    ext=np.stack([r[POOL_E].mean(0) for r in recs]),
    ttm=np.stack([r[TTM].mean(0) for r in recs]),
    theta_cro=np.stack([theta_of(r) for r in cro_only]),
    theta_str=np.stack([theta_of(r) for r in str_only]),
    del_=best)
res["figure_del"] = best
json.dump(res, open("l20/results_l20.json", "w"), indent=1)
print(f"\nfigure arm DEL={best} saved -> l20/two_phase.npz | "
      f"done {time.time()-t0:.0f}s -> l20/results_l20.json", flush=True)
