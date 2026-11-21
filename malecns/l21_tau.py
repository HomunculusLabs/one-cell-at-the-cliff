"""L21: per-class kinetics on the cord INTRINSIC populations.

L18B/L19 pinned the timing bottleneck: at DT 2 ms the uniform-51 ms interior
smears the TTMn drive into a 172-233 step (344-466 ms) lag, while direct
amplified DNp01-04 edges bypass it (jump-first). L21 asks:
  (a) does per-class tau on vnc_intrinsic shrink the interior TRANSIT delay
      to TTMn at DT 2 ms, and where is the floor?
  (b) does any tau make BRAIN-ORIGIN ordering (DN port -> motor) resolvable
      through the bulk interior (no direct-edge amplification)?

Classing: vnc_intrinsic carries NO class column (only hemilineage type
names, ~20-30 cells each) — 'local vs projecting' is not annotated. The
graph-native classes are HOP-DISTANCE-TO-MOTOR tiers (reverse BFS from the
MN pools over interior edges): d1 premotor, d2, d3, far. Sum-of-taus
(commutative low-pass chain) predicts delay depends on the tau MULTISET on
the path, not which tier holds the fast taus; the tier arms + a
matched-fraction random null test that.

UNDERDETERMINED labels (L18 rule): interior taus are free parameters — the
field has not measured cord interneuron membrane taus. The sweep spans
{51, 20, 10, 5} ms; only the 51 ms side is anchored (L18 base = everything
.051). MN REPORTERS: monitored pools get the MEASURED 4 ms TDT twitch tau
(fast tau = drive reporter, the L18B lesson) so pool t_pk tracks drive
arrival, not pool kinetics — labeled reporter choice, not a claim about
every MN's twitch.

Anchors to reproduce:
  A0 tau_intr=51 ms  ~=  L18B homog (TTMn t_pk steps ~[164,172,233]).
  B2 (amp ON, tau 51) keeps L19's jump-first ordering at finer DT.

Arms:
  a0  uniform sweep tau_intr in {51,20,10,5} ms (cord mechano event, L16/18).
  a1  tier arms at 5 ms: d1-only / d2-only / d3-only fast.
  a2  random-fraction null: |d1|/|reachable| fast cells, 5 draws.
  b1  looming volley, amplification OFF: pool SNR vs tail floor per tau.
  b2  looming volley, L19 amplification ON: jump-first margin vs tau.
DESCRIPTIVE ONLY (owner movement law). CPU-only (8 threads) — GPU is the
live duck's.
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
GAIN = 0.8846            # op point bisected in L11 (DT-invariant ODE)
DT = 0.002               # DT 2 ms — the L18B downshift
TAU_BASE = 0.051         # L18 base everywhere
TAU_REP = 0.004          # MEASURED TDT twitch — reporter on monitored pools
AMP_MECH = 2.0           # L16/L17/L18 cord mechano amplitude
AMP_EV = 8.0             # L13b/L19 looming amplitude
G = 200.0                # L13b per-class gain
SEEDS = [11, 22, 33]
SETTLE, EVENT = 300, 20
POST_A, POST_B = 320, 300   # A: TTMn lag up to ~233 steps at tau 51; B: 600 ms

ap = argparse.ArgumentParser()
ap.add_argument("phase", choices=["a0a1", "a3", "a2", "b"])
ARGS = ap.parse_args()

os.makedirs("l21", exist_ok=True)
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
intr = np.where(sup == "vnc_intrinsic")[0]
cord_mech = np.where((sup == "vnc_sensory")
                     & pd.Series(cls).str.contains("mechano").to_numpy())[0]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(leg_dns) == 8 and len(neck_dns) == 4
PAIRS = {
    "Ti": (np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
           np.where(typm == "Ti extensor MN")[0]),
    "Tr": (np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0],
           np.where(typm == "Tr extensor MN")[0]),
}
POOL_F = np.concatenate([PAIRS["Ti"][0], PAIRS["Tr"][0]])
POOL_E = np.concatenate([PAIRS["Ti"][1], PAIRS["Tr"][1]])
TTM = np.where(np.array([str(t).startswith("TTMn") for t in typm]))[0]
LEG_U = np.concatenate([POOL_F, POOL_E])
for k, (f, e) in PAIRS.items():
    assert len(f) > 0 and len(e) > 0
assert len(TTM) > 0 and len(intr) > 0

# --- hop-distance-to-motor tiers over the interior (reverse BFS) ----------
# ABS-weight reachability: W carries SIGNS (GABA/glut) — a signed sum drops
# inhibitory premotor cells (20.3% of motor in-edges) from the closure.
Wt = W.transpose(0, 1).to_sparse_coo().coalesce()
Wt = torch.sparse_coo_tensor(Wt.indices(), Wt.values().abs(),
                             Wt.shape).coalesce()
is_intr = np.zeros(N, bool); is_intr[intr] = True
mvec = np.zeros(N, np.float32); mvec[motor] = 1.0
reach = torch.from_numpy(mvec).unsqueeze(1)
seen = np.zeros(N, bool); seen[motor] = True
tiers, frontier = {}, motor.copy()
cur = motor.copy()
for depth in range(1, 6):
    nxt = (torch.sparse.mm(Wt, reach) > 0).squeeze(1).numpy()
    new = nxt & ~seen
    t_i = np.where(new & is_intr)[0]
    tiers[f"d{depth}"] = t_i
    seen |= new
    cur = np.where(new)[0]
    if cur.size == 0:
        break
    reach = torch.from_numpy(seen.astype(np.float32)).unsqueeze(1)
reachable_intr = np.where(seen & is_intr)[0]
unreached_intr = intr[~np.isin(intr, reachable_intr)]
for d in ("d1", "d2"):
    assert len(tiers[d]) > 0, d
F_FRAC = len(tiers["d2"]) / max(len(reachable_intr), 1)
n1, n2 = len(tiers["d1"]), len(tiers["d2"])
print(f"motor {M} | intrinsic {len(intr)} | SHALLOW interior: d1 {n1} / "
      f"d2 {n2} / d3+ 0 / never-reach {len(unreached_intr)} | "
      f"null k=f(d2) {F_FRAC:.3f} | "
      f"cord mech {len(cord_mech)} | loom {len(loom)} | TTMn {len(TTM)} | "
      f"leg {len(LEG_U)}", flush=True)


def reporter_base():
    tv = np.full(N, TAU_BASE, np.float32)
    tv[motor[np.concatenate([TTM, LEG_U])]] = TAU_REP   # drive reporters
    return tv


def tau_vec(phase_arm, rng=None):
    tv = reporter_base()
    if phase_arm.startswith("u"):                       # uniform sweep
        tv[intr] = float(phase_arm[1:]) / 1000.0
    elif phase_arm == "d1":
        tv[tiers["d1"]] = 0.005
    elif phase_arm == "d2":
        tv[tiers["d2"]] = 0.005
    elif phase_arm == "far":                            # never-reach control
        tv[unreached_intr] = 0.005
    elif phase_arm == "asc5":                     # the long-loop cells only
        for sc_ in ("ascending_neuron", "descending_neuron"):
            tv[np.where(sup == sc_)[0]] = 0.005
    elif phase_arm == "all5":                     # every non-reporter cell
        tv[:] = 0.005
        tv[motor[np.concatenate([TTM, LEG_U])]] = TAU_REP
    elif phase_arm == "rand":                           # count-matched null
        k = len(tiers["d2"])
        pick = rng.choice(reachable_intr, size=k, replace=False)
        tv[pick] = 0.005
    else:
        raise ValueError(phase_arm)
    return tv


def build_amp():
    """L13b per-class amplification, verbatim l19."""
    rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
    cols = W.col_indices().numpy()
    mrow = np.zeros(N, bool); mrow[motor] = True
    leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
    neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
    em_leg = torch.from_numpy(mrow[rows.numpy()] & leg_src[cols])
    em_neck = torch.from_numpy(mrow[rows.numpy()] & neck_src[cols])
    assert int(em_leg.sum()) > 0 and int(em_neck.sum()) > 0
    Wg = W.clone()
    v = Wg.values(); Wv = W.values()
    v[em_leg] = Wv[em_leg] * G
    v[em_neck] = Wv[em_neck] * G
    print(f"amplified x{G:.0f}: leg {int(em_leg.sum())} + neck "
          f"{int(em_neck.sum())} DN->motor edges", flush=True)
    return Wg


def rollout(event_idx, amp, tv, seed, T, Wuse=None):
    Wu = W if Wuse is None else Wuse
    tau = torch.from_numpy(tv).unsqueeze(1)
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(Wu, X) + I      # [N,1] operands — never 1-D
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[event_idx] = amp
    for _ in range(SETTLE):
        step(Z)
    af = float((X > 0.05).float().mean())
    base_m = X[motor].squeeze(1).numpy().copy()
    base_dn = X[dn].squeeze(1).numpy().copy()
    rec = np.zeros((M, T), dtype=np.float32)
    rec_dn = np.zeros((len(dn), T), dtype=np.float32)
    for k in range(T):
        step(I0 if k < EVENT else Z)
        rec[:, k] = X[motor].squeeze(1).numpy() - base_m
        rec_dn[:, k] = X[dn].squeeze(1).numpy() - base_dn
    return rec, rec_dn, af


def pool_tp(rec, idx):
    """pool-mean trace peak step (and value)."""
    p = rec[idx].mean(0)
    return int(np.argmax(p)), float(p.max())


def tail_floor(rec, t_from):
    return float(rec[:, t_from:].std(axis=1).mean())


def sc3(vals):
    return bool(all(v > 0 for v in vals) or all(v < 0 for v in vals))


if ARGS.phase in ("a0a1", "a3", "a2"):
    T = EVENT + POST_A
    if ARGS.phase == "a0a1":
        ARMS = ["u51", "u20", "u10", "u5", "d1", "d2", "far"]
    elif ARGS.phase == "a3":
        ARMS = ["asc5", "all5"]
    else:
        ARMS = [f"rand{d}" for d in range(5)]
    out = {}
    rng = np.random.default_rng(20261111)
    TR = {}                                   # pool-mean traces for reading
    for arm in ARMS:
        name = "rand" if ARGS.phase == "a2" else arm
        tv = tau_vec(name, rng)
        tps_t, tps_l, afs = [], [], []
        for s in SEEDS:
            rec, _, af = rollout(cord_mech, AMP_MECH, tv, s, T)
            tt, _ = pool_tp(rec, TTM)
            tl, _ = pool_tp(rec, LEG_U)
            tps_t.append(tt); tps_l.append(tl); afs.append(af)
            if s == SEEDS[0]:
                TR[f"{arm}_ttm"] = rec[TTM].mean(0)
                TR[f"{arm}_leg"] = rec[LEG_U].mean(0)
        out[arm] = {"ttm_tp_steps": tps_t, "ttm_tp_ms": [t * 1000 * DT for t in tps_t],
                    "leg_tp_steps": tps_l, "leg_tp_ms": [t * 1000 * DT for t in tps_l],
                    "af": float(np.mean(afs)),
                    "fast_cells": int((tv[intr] < 0.01).sum())}
        print(f"{arm}: TTMn t_pk {out[arm]['ttm_tp_steps']} "
              f"({out[arm]['ttm_tp_ms'][0]:.0f}-{out[arm]['ttm_tp_ms'][-1]:.0f} ms)"
              f" | leg t_pk {out[arm]['leg_tp_steps']} | fast {out[arm]['fast_cells']}"
              f" | af {out[arm]['af']:.4f} | {time.time()-t0:.0f}s", flush=True)
    fn = f"l21/results_l21_{ARGS.phase}.json"
    json.dump(out, open(fn, "w"), indent=1)
    np.savez("l21/traces_l21_%s.npz" % ARGS.phase, **TR)
    print(f"wrote {fn} + traces", flush=True)

else:                                                   # phase b
    T = EVENT + POST_B
    Wg = build_amp()
    out = {"b1": {}, "b2": {}}
    TRB = {}
    for tau_ms in (51, 10, 5):
        tv = tau_vec(f"u{tau_ms}")
        # b1: bulk interior only (no amplification)
        snrs, tps, afs = {}, [], []
        for s in SEEDS:
            rec, _, af = rollout(loom, AMP_EV, tv, s, T)
            fl = tail_floor(rec, 240)
            for nm, idx in (("ttm", TTM), ("leg", LEG_U)):
                amp = float(np.abs(rec[idx]).max(axis=1).mean())
                snrs.setdefault(nm, []).append(amp / (fl + 1e-12))
            tt, _ = pool_tp(rec, TTM)
            tl, _ = pool_tp(rec, LEG_U)
            tps.append((tt, tl)); afs.append(af)
        out["b1"][f"tau{tau_ms}"] = {
            "snr": {k: [round(x, 2) for x in v] for k, v in snrs.items()},
            "ttm_tp": [p[0] for p in tps], "leg_tp": [p[1] for p in tps],
            "af": float(np.mean(afs))}
        # b2: L19 chain (amplified direct DN->motor)
        mar, tps2, dn_l, afs2 = [], [], [], []
        mar_e, tps_e = [], []
        for s in SEEDS:
            rec, rec_dn, af = rollout(loom, AMP_EV, tv, s, T, Wuse=Wg)
            tt, _ = pool_tp(rec, TTM)
            tl, _ = pool_tp(rec, LEG_U)
            td, _ = pool_tp(rec_dn, np.arange(rec_dn.shape[0]))
            # early window (first 100 steps): the direct-route component
            te = int(rec[TTM][:, :100].mean(0).argmax())
            le = int(rec[LEG_U][:, :100].mean(0).argmax())
            mar.append(tl - tt); tps2.append((tt, tl)); dn_l.append(td)
            mar_e.append(le - te); tps_e.append((te, le))
            afs2.append(af)
            if s == SEEDS[0]:
                TRB[f"tau{tau_ms}_ttm"] = rec[TTM].mean(0)
                TRB[f"tau{tau_ms}_leg"] = rec[LEG_U].mean(0)
                TRB[f"tau{tau_ms}_dn"] = rec_dn.mean(0)
        b2 = out["b2"][f"tau{tau_ms}"] = {
            "margin_leg_minus_ttm": mar, "sign_consistent": sc3(mar),
            "margin_early": mar_e, "sign_consistent_early": sc3(mar_e),
            "ttm_tp": [p[0] for p in tps2], "leg_tp": [p[1] for p in tps2],
            "ttm_tp_early": [p[0] for p in tps_e],
            "leg_tp_early": [p[1] for p in tps_e],
            "dn_tp": dn_l, "af": float(np.mean(afs2))}
        print(f"tau{tau_ms}: b1 SNR ttm {np.mean(snrs['ttm']):.1f}x leg "
              f"{np.mean(snrs['leg']):.1f}x | b2 margin {np.mean(mar):+.1f} "
              f"{mar} sc={sc3(mar)} | EARLY {np.mean(mar_e):+.1f} {mar_e} "
              f"sc_e={sc3(mar_e)} ttm_e {b2['ttm_tp_early']} leg_e "
              f"{b2['leg_tp_early']} dn {dn_l}"
              f" | af {np.mean(afs + afs2):.4f} | {time.time()-t0:.0f}s",
              flush=True)
    json.dump(out, open("l21/results_l21_b.json", "w"), indent=1)
    np.savez("l21/traces_l21_b.npz", **TRB)
    print("wrote l21/results_l21_b.json + traces", flush=True)
print(f"done {time.time()-t0:.0f}s", flush=True)
