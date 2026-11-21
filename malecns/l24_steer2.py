"""L24 dynamic v2: steering volley via the EXCITATORY mirror channel (DNg95)
+ inhibitory push-pull (DNg105) + superposition with the jump route.

v1 lesson: DNg105's 243 flexor edges are ALL NEGATIVE (w-sum -1.52, max edge
-0.0004) — an inhibitory CROSSED-mirror channel (LI_L -0.96/LI_R +0.96);
volleying it cannot RAISE flexors off the relu floor, it suppresses the
mirror side. DNg95 is the excitatory IPSI mirror (w-sum +0.40, LI_L +0.96/
LI_R -1.00, L20 crouch carrier). Push-pull pair on the same Ti/Tr flexor
pools: DNg95-L excites LEFT, DNg105-L inhibits RIGHT -> same turn direction.

Arms (3 seeds, G=200 per-class, L13b/L23 machinery verbatim):
  noise      no volley
  steerL     DNg95 L cell volley        -> LEFT flexors (ipsi prediction)
  steerR     DNg95 R cell volley        -> RIGHT flexors (sign-flip control)
  jump       DNp01-04 bilateral volley  (works in v1)
  joint      steerL + jump              (L23 superposition form)
  jClamp     joint w/ DNg95 clamped     (expect ~= jump)
  inhibL     DNg105 L cell volley alone -> SUPPRESSION of RIGHT flexors
  pushpull   DNg95-L + DNg105-L         (excite L + inhibit R)
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

d95 = dn[dn_typ == "DNg95"]
d105 = dn[dn_typ == "DNg105"]
dnp = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
d95_L = d95[side[d95] == "L"]; d95_R = d95[side[d95] == "R"]
d105_L = d105[side[d105] == "L"]
assert len(d95_L) == 1 and len(d95_R) == 1 and len(d105_L) == 1 and len(dnp) == 8

flex_t = ["Ti flexor MN", "Acc. ti flexor MN", "Tr flexor MN", "Acc. tr flexor MN"]
ext_t = ["Ti extensor MN", "Tr extensor MN"]
mpool = {}
for name, tl, sd in [("flexL", flex_t, "L"), ("flexR", flex_t, "R"),
                     ("ext", ext_t, None)]:
    m = np.where(np.isin(mtyp, tl))[0] if sd is None else \
        np.where(np.isin(mtyp, tl) & (side[motor] == sd))[0]
    mpool[name] = motor[m]
mpool["TTMn"] = motor[np.char.startswith(mtyp.astype(str), "TTMn")]
POOLS = {k: v for k, v in mpool.items() if len(v)}
mL_all = motor[side[motor] == "L"]
mR_all = motor[side[motor] == "R"]
print("cells: DNg95-L", int(d95_L[0]), "DNg95-R", int(d95_R[0]),
      "DNg105-L", int(d105_L[0]), "| pools:", {k: len(v) for k, v in POOLS.items()},
      flush=True)

rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
cols = W.col_indices().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True


def amplify(cells):
    s = np.zeros(N, bool); s[cells] = True
    return torch.from_numpy(mrow[rows.numpy()] & s[cols])


e95, e105, ep = amplify(d95), amplify(d105), amplify(dnp)
Wv = W.values()
W2 = W.clone()
v = W2.values()
for e in (e95, e105, ep):
    v[e] = Wv[e] * G
n95, n105, nP = int(e95.sum()), int(e105.sum()), int(ep.sum())
assert n95 > 0 and n105 > 0 and nP > 0
print(f"amplified: DNg95 {n95} (+w) | DNg105 {n105} (-w) | DNp01-04 {nP} "
      f"(all x{G})", flush=True)


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
    # steering readout window: track flexor pool means through the event
    flexL_tr = np.zeros(EVENT + 10); flexR_tr = np.zeros(EVENT + 10)
    peak_m, Xpk = -1.0, None
    acc = np.zeros(len(motor)); sat = 0.0
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else Z)
        d = (X[motor] - Xb[motor]).squeeze(1)
        acc += d.numpy()
        flexL_tr[k] = float(X[POOLS["flexL"]].mean() - Xb[POOLS["flexL"]].mean())
        flexR_tr[k] = float(X[POOLS["flexR"]].mean() - Xb[POOLS["flexR"]].mean())
        sat = max(sat, float((X[motor] >= 0.999).float().mean()))
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m, Xpk = m, X.clone()
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    dm_int = acc / (EVENT + 10)

    def lr(a, b):
        ma, mb = float(Xpk[a].mean()), float(Xpk[b].mean())
        ba, bb = float(Xb[a].mean()), float(Xb[b].mean())
        return (ma - mb) / (ma + mb + 1e-9) - (ba - bb) / (ba + bb + 1e-9)

    turn_all = lr(mL_all, mR_all)
    turn_flex = lr(POOLS["flexL"], POOLS["flexR"])
    # window-mean dm on the flexor pools (signed, robust to peak timing)
    flexL_d = float(dm_int[np.isin(motor, POOLS["flexL"])].mean())
    flexR_d = float(dm_int[np.isin(motor, POOLS["flexR"])].mean())
    pool_pk = {p: float(np.abs((Xpk[mi] - Xb[mi]).squeeze(1)).max())
               for p, mi in POOLS.items()}
    # window-peak pool amp (L20 pool_peak_snr form: per-cell max |dm|, mean)
    def wpk(mi):
        rec = X_window_dm[mi]
        return float(np.abs(rec).max())
    X_window_dm = None  # placeholder, filled below

    # recompute window dm matrix for pool peaks (cells x window)
    return {"dm": dm, "dm_int": dm_int, "peak": peak_m, "sat": sat,
            "turn_all": turn_all, "turn_flex": turn_flex,
            "flexL_d": flexL_d, "flexR_d": flexR_d,
            "flexL_tr": flexL_tr, "flexR_tr": flexR_tr,
            "pool_pk": pool_pk}


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


SEEDS = [11, 22, 33]
def ev(*cells):
    return [(int(np.asarray(c).reshape(-1)[0]), AMP) for c in cells]


PLAN = [
    ("noise", [], None),
    ("steerL", ev(d95_L), None),
    ("steerR", ev(d95_R), None),
    ("jump", ev(dnp), None),
    ("joint", ev(d95_L) + ev(dnp), None),
    ("jClamp", ev(d95_L) + ev(dnp), d95),
    ("inhibL", ev(d105_L), None),
    ("pushpull", ev(d95_L) + ev(d105_L), None),
]
V = {}
for key, e, clamp in PLAN:
    V[key] = [run(e, s, clamp=clamp) for s in SEEDS]
    print(f"{key:8s} turn_all {np.mean([r['turn_all'] for r in V[key]]):+.4f} "
          f"turn_flex {np.mean([r['turn_flex'] for r in V[key]]):+.4f} "
          f"flexL_d {np.mean([r['flexL_d'] for r in V[key]]):+.4f} "
          f"flexR_d {np.mean([r['flexR_d'] for r in V[key]]):+.4f} "
          f"sat {max(r['sat'] for r in V[key]):.3f}", flush=True)

res = {"G": G, "AMP": AMP, "seeds": SEEDS,
       "edges": {"DNg95": n95, "DNg105": n105, "DNp": nP},
       "pool_sizes": {k: len(v) for k, v in POOLS.items()},
       "snr": {}, "turn": {}, "superposition": {}, "misc": {}}

# ---- SNR gate (L19/L20 rule): window-peak |dm| per flexor pool vs noise ----
def wpk_arm(arm, pool):
    # per-cell max |window dm| using the flexor traces' cells: use dm_int proxy
    # simpler robust form: max |pool window trace| over cells is expensive;
    # use pool-mean window trace peak (recorded) / noise
    tr = np.max([np.abs(r[f"flex{pool}_tr"]) for r in V[arm]])
    return tr

for p in ("L", "R"):
    ev_s = max(wpk_arm("steerL", p), wpk_arm("steerR", p))
    nz = wpk_arm("noise", p) + 1e-12
    res["snr"][f"flex{p}"] = float(ev_s / nz)
    print(f"SNR flex{p} (steer window-trace peak / noise): {ev_s / nz:7.1f}x",
          flush=True)

# ---- turn table ----
for k in V:
    res["turn"][k] = {m: [r[m] for r in V[k]]
                      for m in ("turn_all", "turn_flex", "flexL_d", "flexR_d")}
tl = np.array(res["turn"]["steerL"]["turn_flex"])
tr = np.array(res["turn"]["steerR"]["turn_flex"])
flip = bool((np.sign(tl) == -np.sign(tr)).all() and np.abs(tl).min() > 1e-6)
print(f"\nTURN sign-flip (turn_flex): steerL {tl.round(4)} steerR {tr.round(4)}"
      f" -> {'PASS 3/3' if flip else 'FAIL'}", flush=True)
res["turn"]["sign_flip_pass"] = flip
for k in ("steerL", "steerR", "inhibL", "pushpull"):
    dl = np.array(res["turn"][k]["flexL_d"]); dr = np.array(res["turn"][k]["flexR_d"])
    sc = int(((dl > 0) & (dr <= 0)).sum()) if k != "inhibL" else \
        int(((dr < 0) & (dl <= 0)).sum())
    print(f"  {k:8s}: flexL {dl.mean():+.4f} flexR {dr.mean():+.4f} "
          f"({sc}/3 seeds predicted shape)", flush=True)

# ---- superposition (L23 form) ----
for form in ("dm", "dm_int"):
    cs, resid = [], []
    for i in range(len(SEEDS)):
        dJ = V["joint"][i][form]
        dS = V["steerL"][i][form] + V["jump"][i][form]
        cs.append(cos(dJ, dS))
        resid.append(float(np.linalg.norm(dJ - dS) / (np.linalg.norm(dS) + 1e-12)))
    res["superposition"][form] = {"cos_sum": float(np.mean(cs)),
                                  "resid": float(np.mean(resid))}
    print(f"SUPERPOS [{form}]: cos(dJ, dSteer+dJump) {np.mean(cs):+.3f} "
          f"resid {np.mean(resid):.3f}", flush=True)

# ---- turn retained in joint; push-pull gain ----
tj = np.abs(np.array(res["turn"]["joint"]["turn_flex"]))
ts = np.abs(np.array(res["turn"]["steerL"]["turn_flex"]))
res["turn"]["retained_ratio"] = float(np.mean(tj / (ts + 1e-12)))
print(f"turn_flex(joint)/steerL: {res['turn']['retained_ratio']:.2f}", flush=True)
tp = np.abs(np.array(res["turn"]["pushpull"]["turn_flex"]))
res["turn"]["pushpull_over_steer"] = float(np.mean(tp / (ts + 1e-12)))
res["turn"]["pushpull_sign_consistent"] = bool(
    (np.sign(np.array(res["turn"]["pushpull"]["turn_flex"]))
     == np.sign(tl)).all())
print(f"pushpull/steer turn gain: {res['turn']['pushpull_over_steer']:.2f} "
      f"(sign-consistent with steerL: "
      f"{res['turn']['pushpull_sign_consistent']})", flush=True)

# ---- clamp control ----
m = np.mean([cos(V["jClamp"][i]["dm"], V["jump"][j]["dm"])
             for i in range(3) for j in range(3)])
res["clamp_jump_cos"] = float(m)
print(f"clamp: cos(jClamp, jump) {m:+.3f}", flush=True)
res["misc"]["sat"] = {k: max(r["sat"] for r in V[k]) for k in V}

json.dump(res, open("l24/results_l24_steer2.json", "w"), indent=1)
print(f"\ndone {time.time() - t0:.0f}s -> l24/results_l24_steer2.json", flush=True)
