"""L23: route COMPOSITION — do two simultaneous class-amplified DN routes stay
orthogonal (linear superposition) or interfere?

L13b amplified DNp01-04 (jump/leg) + DNc01/02 (atlas targets MNml78/MNad25/
MNx04/MNad03 — leg+abdominal; L22 renamed the old 'neck' label) and measured
SOLO motor vectors: looming self .971, odor .672, cross -.002, clamps kill
(.018/.008). L20 composed crouch->stroke SEQUENTIALLY; L23 fires two routes
TOGETHER at the same onset.

Protocol (L13b machinery verbatim, G=200 anchor gain, both classes amplified
in ONE brain — exactly the L13b substrate):
  noise    no event                      (SNR floor, same seeds)
  soloA    looming amp 8                 (drives DNp01-04)
  soloB    odor amp 8                    (drives DNc01/02)
  joint    looming + odor, same onset
  jClampA  joint with DNp01-04 clamped   (expect ~= soloB)
  jClampB  joint with DNc01/02 clamped   (expect ~= soloA)
  killA    looming + clamp DNp01-04      (L13 anchor .018)

Metrics:
  SNR gate FIRST (L19 rule): each route's target pools, event peak vs the
  noise control peak. Then the deliverable table: solo~solo, joint~solo,
  joint~(A+B) superposition + residual, per-pool mass ratios joint/solo
  (interference), clamp fidelity, motor saturation fraction (mechanism:
  relu/RMAX is the only nonlinearity that can couple routes).
Both dm forms recorded: L13 peak-snapshot AND window-averaged dm_int (the
fair superposition readout when the two routes peak at different steps).
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

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
mtyp = typ[motor]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
olf = np.where(lab["class"].astype(str) == "olfactory")[0]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(leg_dns) == 8 and len(neck_dns) == 4, (len(leg_dns), len(neck_dns))

# target pools (route-owned): A = L13 looming landing zone; B = L22 DNc01/02
# atlas top targets.
POOLS = {
    "TTMn": np.where(mtyp == "TTMn")[0],
    "extensor": np.where(np.char.find(mtyp.astype(str), "extensor") >= 0)[0],
    "MNml78": np.where(mtyp == "MNml78")[0],
    "MNad25": np.where(mtyp == "MNad25")[0],
    "MNx04": np.where(mtyp == "MNx04")[0],
    "MNad03": np.where(mtyp == "MNad03")[0],
}
POOLS = {k: v for k, v in POOLS.items() if len(v)}
A_POOLS = [p for p in ("TTMn", "extensor") if p in POOLS]
B_POOLS = [p for p in ("MNml78", "MNad25", "MNx04", "MNad03") if p in POOLS]
assert A_POOLS and B_POOLS, POOLS.keys()
print("pools:", {k: len(v) for k, v in POOLS.items()}, flush=True)

rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
cols = W.col_indices().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
emask_leg = torch.from_numpy(mrow[rows.numpy()] & leg_src[cols])
emask_neck = torch.from_numpy(mrow[rows.numpy()] & neck_src[cols])
Wv = W.values()
assert int(emask_leg.sum()) > 0 and int(emask_neck.sum()) > 0
W2 = W.clone()
v = W2.values()
v[emask_leg] = Wv[emask_leg] * G
v[emask_neck] = Wv[emask_neck] * G
print(f"leg edges {int(emask_leg.sum()):,} | neck edges {int(emask_neck.sum()):,} "
      f"(both x{G}, L13b substrate)", flush=True)


def run(events, seed, clamp=None):
    """events: list of (channel_idx, amp); clamp: iterable of DN cell idx."""
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
    peak_m, Xpk, tpk = -1.0, None, -1
    acc = np.zeros(len(motor)); sat = 0.0
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else Z)
        d = (X[motor] - Xb[motor]).squeeze(1)
        acc += d.numpy()
        sat = max(sat, float((X[motor] >= 0.999).float().mean()))
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m, Xpk, tpk = m, X.clone(), k
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    dm_int = acc / (EVENT + 10)
    pool_pk = {p: float(np.abs(d[mi]).max()) for p, mi in POOLS.items()}
    return {"dm": dm, "dm_int": dm_int, "peak": peak_m, "tpk": tpk,
            "sat": sat, "pool_pk": pool_pk, "mbase": float(Xb[motor].mean())}


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


SEEDS = [11, 22, 33]
PLAN = [
    ("noise", [], None),
    ("soloA", [(loom, 8.0)], None),
    ("soloB", [(olf, 8.0)], None),
    ("joint", [(loom, 8.0), (olf, 8.0)], None),
    ("jClampA", [(loom, 8.0), (olf, 8.0)], leg_dns),
    ("jClampB", [(loom, 8.0), (olf, 8.0)], neck_dns),
    ("killA", [(loom, 8.0)], leg_dns),
]
V = {}
for key, ev, clamp in PLAN:
    V[key] = [run(ev, s, clamp=clamp) for s in SEEDS]
    mag = np.mean([np.abs(r["dm"]).mean() for r in V[key]])
    magi = np.mean([np.abs(r["dm_int"]).mean() for r in V[key]])
    tp = [r["tpk"] for r in V[key]]
    print(f"{key:8s} |dm| {mag:.5f} |dm_int| {magi:.5f} t_pk {tp} "
          f"sat {max(r['sat'] for r in V[key]):.3f}", flush=True)

res = {"G": G, "seeds": SEEDS, "pool_sizes": {k: len(v) for k, v in POOLS.items()},
       "edges": {"leg": int(emask_leg.sum()), "neck": int(emask_neck.sum())},
       "snr": {}, "cos": {}, "interference": {}, "clamp": {}, "misc": {}}

# ---- SNR gate (L19 rule): event pool peak / noise-control pool peak -------
for p in POOLS:
    ev = max(np.mean([r["pool_pk"][p] for r in V["soloA"]]),
             np.mean([r["pool_pk"][p] for r in V["soloB"]]))
    nz = np.mean([r["pool_pk"][p] for r in V["noise"]]) + 1e-12
    res["snr"][p] = float(ev / nz)
    print(f"SNR {p:9s}: {ev / nz:8.1f}x", flush=True)

# ---- cross-cos table (both dm forms) --------------------------------------
def pair(a, b, form, same_seed=False):
    if same_seed:
        cs = [cos(V[a][i][form], V[b][i][form]) for i in range(len(SEEDS))]
    else:
        cs = [cos(V[a][i][form], V[b][j][form])
              for i in range(len(SEEDS)) for j in range(len(SEEDS))]
    return float(np.mean(cs)), cs

FORMS = ("dm", "dm_int")
for a, b, ss in [("soloA", "soloA", False), ("soloB", "soloB", False),
                 ("soloA", "soloB", False),
                 ("joint", "soloA", False), ("joint", "soloB", False),
                 ("joint", "killA", False),
                 ("jClampA", "soloB", False), ("jClampB", "soloA", False),
                 ("jClampA", "soloA", False), ("jClampB", "soloB", False)]:
    for form in FORMS:
        m, _ = pair(a, b, form, same_seed=ss)
        res["cos"][f"{a}~{b}|{form}"] = m
        print(f"cos {a:7s}~{b:7s} [{form:6s}]: {m:+.3f}", flush=True)

# ---- superposition: joint vs (soloA+soloB), paired seeds -------------------
sup = {}
for form in FORMS:
    cs, resid, norms = [], [], []
    for i in range(len(SEEDS)):
        dJ = V["joint"][i][form]
        dS = V["soloA"][i][form] + V["soloB"][i][form]
        cs.append(cos(dJ, dS))
        resid.append(float(np.linalg.norm(dJ - dS) / (np.linalg.norm(dS) + 1e-12)))
        norms.append(float(np.linalg.norm(dJ) / (np.linalg.norm(dS) + 1e-12)))
    sup[form] = {"cos_sum": float(np.mean(cs)), "cos": cs,
                 "resid": [float(r) for r in resid],
                 "norm_ratio": [float(r) for r in norms]}
    print(f"SUPERPOS [{form}]: cos(dJ, dA+dB) {np.mean(cs):+.3f} "
          f"resid {np.mean(resid):.3f} |dJ|/|dS| {np.mean(norms):.3f}", flush=True)
res["superposition"] = sup

# ---- per-pool interference: joint peak / owning-solo peak ------------------
for p, solo in [(p, "soloA") for p in A_POOLS] + [(p, "soloB") for p in B_POOLS]:
    j = np.mean([r["pool_pk"][p] for r in V["joint"]])
    s = np.mean([r["pool_pk"][p] for r in V[solo]]) + 1e-12
    # cross-leak: pool response under the OTHER route's solo
    other = "soloB" if solo == "soloA" else "soloA"
    leak = np.mean([r["pool_pk"][p] for r in V[other]])
    res["interference"][p] = {"joint_over_solo": float(j / s), "leak": float(leak)}
    print(f"POOL {p:9s}: joint/solo {j / s:5.2f}  leak(other solo) {leak:.5f} "
          f"(solo {s:.5f})", flush=True)

# ---- clamp fidelity in the joint -------------------------------------------
for key, solo in [("jClampA", "soloB"), ("jClampB", "soloA")]:
    for form in FORMS:
        m, _ = pair(key, solo, form)
        res["clamp"][f"{key}~{solo}|{form}"] = m
for key in ("jClampA", "jClampB"):
    mag = np.mean([np.abs(r["dm"]).mean() for r in V[key]])
    res["misc"][f"{key}_dm_mag"] = float(mag)
res["misc"]["killA_dm_mag"] = float(np.mean([np.abs(r["dm"]).mean() for r in V["killA"]]))
res["misc"]["sat"] = {k: max(r["sat"] for r in V[k]) for k, _, _ in PLAN}
res["misc"]["tpk"] = {k: [r["tpk"] for r in V[k]] for k, _, _ in PLAN}

json.dump(res, open("l23/results_l23.json", "w"), indent=1)
print(f"\ndone {time.time() - t0:.0f}s -> l23/results_l23.json", flush=True)
