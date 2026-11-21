"""L13b: PER-DN-CLASS pathway gain — the decisive slice.

L13a (results_l13.json): flat x200 on ALL 23,616 DN->motor edges gives a
reproducible looming motor vector (self-cos .928) routed to leg pools (TTMn,
femur MNs) — but clamping DNp01-04 does NOT collapse it (.859): the carrier
is the broad DN population lift through the amplified edges, not the
class-specific volley. Also motor tonic 0.031->0.386 (flat gain amplifies
spontaneous DN drive).

L13b: amplify ONLY the event-class edges:
  leg path:   src in DNp01-04 (8 cells) -> motor, xg_leg
  neck path:  src in DNc01/02 (4 cells) -> motor, xg_neck
Predictions if pathway specificity is real:
  looming -> reproducible motor vector riding DNp01-04 (clamp DNp KILLS it),
  odor    -> distinct pattern riding DNc01/02  (clamp DNc kills it),
  cross-cos loom~odor LOW, motor tonic ~base.
Sweep g in {200, 2000} (few edges -> need bigger multiplier).
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

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
mL = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]) & (lab["somaSide"].astype(str) == "L"))[0]
mR = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]) & (lab["somaSide"].astype(str) == "R"))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
olf = np.where(lab["class"].astype(str) == "olfactory")[0]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(leg_dns) == 8 and len(neck_dns) == 4

rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
cols = W.col_indices().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
emask_leg = torch.from_numpy(mrow[rows.numpy()] & leg_src[cols])
emask_neck = torch.from_numpy(mrow[rows.numpy()] & neck_src[cols])
Wv = W.values()
print(f"leg edges {int(emask_leg.sum()):,} (w sum {Wv[emask_leg].sum():.2f}) | "
      f"neck edges {int(emask_neck.sum()):,} (w sum {Wv[emask_neck].sum():.2f})",
      flush=True)


def make_pc(g):
    W2 = W.clone()
    v = W2.values()
    v[emask_leg] = Wv[emask_leg] * g
    v[emask_neck] = Wv[emask_neck] * g
    return W2


def run(W_, channel, amp, seed, clamp=None):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[channel] = amp
    for _ in range(SETTLE):
        step(Z)
    Xb = X.clone()
    peak_m = -1.0
    Xpk = None
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else Z)
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m = m
            Xpk = X.clone()
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    turn = float((Xpk[mL].mean() - Xpk[mR].mean())
                 / (Xpk[mL].mean() + Xpk[mR].mean() + 1e-9)
                 - (Xb[mL].mean() - Xb[mR].mean())
                 / (Xb[mL].mean() + Xb[mR].mean() + 1e-9))
    return dm, peak_m, turn, float(Xb[motor].mean())


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


SEEDS = [11, 22, 33]
res = {"leg_edges": int(emask_leg.sum()), "neck_edges": int(emask_neck.sum()),
       "seeds": SEEDS, "g": {}, "cos": {}, "dm": {}}

for G in [200, 2000]:
    Wg = make_pc(G)
    PLAN = [
        (f"pc{G}|looming", "looming", loom, 8.0, None),
        (f"pc{G}|odor", "odor", olf, 8.0, None),
        (f"pc{G}|loom_clampLeg", "looming", loom, 8.0, leg_dns),
        (f"pc{G}|odor_clampNeck", "odor", olf, 8.0, neck_dns),
    ]
    V = {}
    for key, ev, ch, amp, clamp in PLAN:
        V[key] = [run(Wg, ch, amp, s, clamp=clamp) for s in SEEDS]
        print(f"{key:22s} |dm| {np.mean([np.abs(v[0]).mean() for v in V[key]]):.5f} "
              f"dpeak {np.mean([v[1] for v in V[key]]):.4f} "
              f"turn {np.mean([v[2] for v in V[key]]):+.4f} "
              f"mbase {np.mean([v[3] for v in V[key]]):.4f}", flush=True)
    for a, b in [("looming", "looming"), ("odor", "odor"), ("looming", "odor"),
                 ("loom_clampLeg", "loom_clampLeg"), ("odor_clampNeck", "odor_clampNeck")]:
        ka = f"pc{G}|{a}"; kb = f"pc{G}|{b}"
        if a == b:
            cs = [cos(V[ka][i][0], V[ka][j][0]) for i in range(3) for j in range(i + 1, 3)]
        else:
            cs = [cos(V[ka][i][0], V[kb][j][0]) for i in range(3) for j in range(3)]
        res["cos"][f"{a}~{b}@{G}"] = float(np.mean(cs))
        print(f"  @{G:4d} {a:16s}~{b:16s}: {np.mean(cs):+.3f}", flush=True)
    res["g"][str(G)] = {k: {"dpeak": [float(v[1]) for v in V[k]],
                            "turn": [float(v[2]) for v in V[k]],
                            "mbase": [float(v[3]) for v in V[k]],
                            "dm_mag": [float(np.abs(v[0]).mean()) for v in V[k]]}
                        for k in V}
    # top responder motor cells for looming at this G
    prof = np.mean([v[0] for v in V[f"pc{G}|looming"]], axis=0)
    top = np.argsort(-prof)[:6]
    print(f"  @{G} looming top motor:", [(typ[motor][t], round(float(prof[t]), 4))
                                         for t in top], flush=True)

json.dump(res, open("l13/results_l13b.json", "w"), indent=1)
print(f"\ndone {time.time()-t0:.0f}s -> l13/results_l13b.json", flush=True)
