"""L24 dynamic: UNILATERAL VOLLEY TURN DEMO + superposition with the jump route.

Static pass said: no DN type is NET-lateralized (max |LI z| 3.3) but L/R
homologues are MIRROR channels — DNg105 (flexor, 243 edges, 1L+1R) is
CROSSED (LI_L -0.961 / LI_R +0.963: L-soma -> RIGHT motor), DNg95 ipsi
(+0.958/-1.000). Steering mechanism predicted by that table: volley ONE
side's cell -> motor burst on the MIRROR side -> turn. Net LI ~ 0 is the
symmetric default, not the absence of a steering channel.

Protocol (L23 machinery verbatim, G=200 on DNg105->motor + DNp01-04->motor):
  noise    no volley                          (SNR floor)
  steerL   volley DNg105 L cell (amp 8, optogenetic-style direct current)
  steerR   volley DNg105 R cell               (sign-flip control)
  jump     volley all 8 DNp01-04 cells        (bilateral, L13b anchor route)
  joint    steerL + jump, same onset          (L23 composition form)
  jClamp   joint with DNg105 clamped          (expect ~= jump)

Metrics: L19 SNR gate on flexor-L/flexor-R pools; L11 turn metric (whole
motor + flexor pool, normalized L-R shift at peak + absolute); per-side pool
peaks (which side lights up); superposition cos(dJoint, dSteer+dJump)
paired seeds; turn retained in joint.
CPU-only, no live changes.
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
SETTLE, EVENT = 300, 20
GAIN = 0.8846
G = 200
AMP = 8.0

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
mtyp = typ[motor]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]

dng105 = dn[dn_typ == "DNg105"]
dnp = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
dng105_L = dng105[side[dng105] == "L"]
dng105_R = dng105[side[dng105] == "R"]
assert len(dng105) == 2 and len(dng105_L) == 1 and len(dng105_R) == 1, \
    (len(dng105), len(dng105_L), len(dng105_R))
assert len(dnp) == 8, len(dnp)
print(f"DNg105 cells {list(dng105)} L={[int(dng105_L[0])]} R={[int(dng105_R[0])]}"
      f" | DNp01-04 {len(dnp)} cells", flush=True)

# pools: flexor (L20 definitions) split by side; extensor+jump for route B
flex_t = ["Ti flexor MN", "Acc. ti flexor MN", "Tr flexor MN", "Acc. tr flexor MN"]
ext_t = ["Ti extensor MN", "Tr extensor MN"]
mpool = {}
for name, tl in [("flexL", flex_t), ("flexR", flex_t),
                 ("extL", ext_t), ("extR", ext_t)]:
    sd = "L" if name.endswith("L") else "R"
    m = np.where(np.isin(mtyp, tl) & (side[motor] == sd))[0]
    mpool[name] = motor[m]
mpool["TTMn"] = motor[np.char.startswith(mtyp.astype(str), "TTMn")]
mpool["ext"] = motor[np.isin(mtyp, ext_t)]
POOLS = {k: v for k, v in mpool.items() if len(v)}
print("pools:", {k: len(v) for k, v in POOLS.items()}, flush=True)
mL_all = motor[side[motor] == "L"]
mR_all = motor[side[motor] == "R"]

rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
cols = W.col_indices().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
s105 = np.zeros(N, bool); s105[dng105] = True
sp = np.zeros(N, bool); sp[dnp] = True
e105 = torch.from_numpy(mrow[rows.numpy()] & s105[cols])
ep = torch.from_numpy(mrow[rows.numpy()] & sp[cols])
Wv = W.values()
n105, nP = int(e105.sum()), int(ep.sum())
assert n105 > 0 and nP > 0
W2 = W.clone()
v = W2.values()
v[e105] = Wv[e105] * G
v[ep] = Wv[ep] * G
print(f"DNg105->motor {n105} edges | DNp01-04->motor {nP} edges (both x{G})",
      flush=True)


def run(events, seed, clamp=None):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W2, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0

    Z = torch.zeros(N, 1)
    I0 = torch.zeros(N, 1)
    for ch, amp in events:
        I0[ch] = amp
    for _ in range(SETTLE):
        step(Z)
    Xb = X.clone()
    peak_m, Xpk = -1.0, None
    acc = np.zeros(len(motor)); sat = 0.0
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else Z)
        d = (X[motor] - Xb[motor]).squeeze(1)
        acc += d.numpy()
        sat = max(sat, float((X[motor] >= 0.999).float().mean()))
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m, Xpk = m, X.clone()
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    dm_int = acc / (EVENT + 10)

    def lr(a, b):
        ma, mb = float(Xpk[a].mean()), float(Xpk[b].mean())
        ba, bb = float(Xb[a].mean()), float(Xb[b].mean())
        return (ma - mb) / (ma + mb + 1e-9) - (ba - bb) / (ba + bb + 1e-9), \
               (ma - mb) - (ba - bb)

    turn_all, dabs_all = lr(mL_all, mR_all)
    turn_flex, dabs_flex = lr(POOLS["flexL"], POOLS["flexR"])
    pool_pk = {p: float(np.abs((Xpk[mi] - Xb[mi]).squeeze(1)).max())
               for p, mi in POOLS.items()}
    # signed per-side flexor means (which side lights up)
    flexL_d = float(dm[np.isin(motor, POOLS["flexL"])].mean())
    flexR_d = float(dm[np.isin(motor, POOLS["flexR"])].mean())
    return {"dm": dm, "dm_int": dm_int, "peak": peak_m, "sat": sat,
            "pool_pk": pool_pk, "turn_all": turn_all, "dabs_all": dabs_all,
            "turn_flex": turn_flex, "dabs_flex": dabs_flex,
            "flexL_d": flexL_d, "flexR_d": flexR_d}


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


SEEDS = [11, 22, 33]
PLAN = [
    ("noise", [], None),
    ("steerL", [(int(dng105_L[0]), AMP)], None),
    ("steerR", [(int(dng105_R[0]), AMP)], None),
    ("jump", [(int(c), AMP) for c in dnp], None),
    ("joint", [(int(dng105_L[0]), AMP)] + [(int(c), AMP) for c in dnp], None),
    ("jClamp", [(int(dng105_L[0]), AMP)] + [(int(c), AMP) for c in dnp], dng105),
]
V = {}
for key, ev, clamp in PLAN:
    V[key] = [run(ev, s, clamp=clamp) for s in SEEDS]
    print(f"{key:7s} turn_all {np.mean([r['turn_all'] for r in V[key]]):+.4f} "
          f"turn_flex {np.mean([r['turn_flex'] for r in V[key]]):+.4f} "
          f"flexL_d {np.mean([r['flexL_d'] for r in V[key]]):+.4f} "
          f"flexR_d {np.mean([r['flexR_d'] for r in V[key]]):+.4f} "
          f"sat {max(r['sat'] for r in V[key]):.3f}", flush=True)

res = {"G": G, "AMP": AMP, "seeds": SEEDS, "edges": {"DNg105": n105, "DNp": nP},
       "pool_sizes": {k: len(v) for k, v in POOLS.items()},
       "snr": {}, "turn": {}, "superposition": {}, "interference": {}}

# ---- SNR gate (L19 rule) on the steering pools ----
for p in ("flexL", "flexR"):
    ev = max(np.mean([r["pool_pk"][p] for r in V["steerL"]]),
             np.mean([r["pool_pk"][p] for r in V["steerR"]]))
    nz = np.mean([r["pool_pk"][p] for r in V["noise"]]) + 1e-12
    res["snr"][p] = float(ev / nz)
    print(f"SNR {p}: {ev / nz:7.1f}x", flush=True)

# ---- turn table: sign flip + per-seed consistency ----
for k in ("steerL", "steerR", "jump", "joint", "jClamp"):
    res["turn"][k] = {
        "turn_all": [r["turn_all"] for r in V[k]],
        "turn_flex": [r["turn_flex"] for r in V[k]],
        "flexL_d": [r["flexL_d"] for r in V[k]],
        "flexR_d": [r["flexR_d"] for r in V[k]],
    }
tl = np.array(res["turn"]["steerL"]["turn_all"])
tr = np.array(res["turn"]["steerR"]["turn_all"])
flip = bool((np.sign(tl) == -np.sign(tr)).all() and np.abs(tl).min() > 0)
print(f"\nTURN sign-flip control: steerL {tl.round(4)} vs steerR {tr.round(4)}"
      f" -> {'PASS' if flip else 'FAIL'}", flush=True)
res["turn"]["sign_flip_pass"] = flip
for k in ("steerL", "steerR"):
    dfl = np.array(res["turn"][k]["flexL_d"]); dfr = np.array(res["turn"][k]["flexR_d"])
    side = "RIGHT" if np.abs(dfr).mean() > np.abs(dfl).mean() else "LEFT"
    print(f"  {k}: flexor L {dfl.mean():+.4f} / R {dfr.mean():+.4f} "
          f"-> drives {side} (static predicts L-cell->RIGHT: crossed)",
          flush=True)

# ---- superposition (L23 form), paired seeds ----
for form in ("dm", "dm_int"):
    cs, resid, ratios = [], [], []
    for i in range(len(SEEDS)):
        dJ = V["joint"][i][form]
        dS = V["steerL"][i][form] + V["jump"][i][form]
        cs.append(cos(dJ, dS))
        resid.append(float(np.linalg.norm(dJ - dS) / (np.linalg.norm(dS) + 1e-12)))
        ratios.append(float(np.linalg.norm(dJ) / (np.linalg.norm(dS) + 1e-12)))
    res["superposition"][form] = {"cos_sum": float(np.mean(cs)),
                                  "resid": float(np.mean(resid)),
                                  "norm_ratio": float(np.mean(ratios))}
    print(f"SUPERPOS [{form}]: cos(dJ,dSteer+dJump) {np.mean(cs):+.3f} "
          f"resid {np.mean(resid):.3f} |dJ|/|dS| {np.mean(ratios):.3f}",
          flush=True)

# ---- turn retained in joint + per-pool interference ----
for k, solo in [("flexR", "steerL"), ("TTMn", "jump"), ("ext", "jump")]:
    j = np.mean([r["pool_pk"][k] for r in V["joint"]])
    s = np.mean([r["pool_pk"][k] for r in V[solo]]) + 1e-12
    res["interference"][k] = float(j / s)
    print(f"POOL {k:6s}: joint/solo {j / s:5.2f}", flush=True)
tj = np.array(res["turn"]["joint"]["turn_all"])
ts = np.array(res["turn"]["steerL"]["turn_all"])
res["turn"]["retained_ratio"] = float(np.mean(np.abs(tj) / (np.abs(ts) + 1e-12)))
print(f"turn(joint)/turn(steerL): {res['turn']['retained_ratio']:.2f} "
      f"(jump is bilateral -> adds no turn)", flush=True)

# clamp control: jClamp ~= jump
m = np.mean([cos(V["jClamp"][i]["dm"], V["jump"][j]["dm"])
             for i in range(3) for j in range(3)])
res["clamp_jump_cos"] = float(m)
print(f"clamp: cos(jClamp, jump) {m:+.3f} (steering removed -> pure jump)",
      flush=True)

json.dump(res, open("l24/results_l24_steer.json", "w"), indent=1)
print(f"\ndone {time.time() - t0:.0f}s -> l24/results_l24_steer.json", flush=True)
