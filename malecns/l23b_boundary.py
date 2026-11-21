"""L23b: superposition BOUNDARY — G=200 composes by superposition (cos .987,
per-pool joint/solo 1.00-1.03, sat 0.000). Push the gain to L13b's other
anchor (G=2000, tonic .061 there) and double amp: does RMAX/relu nonlinearity
start coupling the routes? Same protocol, core conditions only.
"""
import json
import sys

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, EVENT = 300, 20
GAIN = 0.8846

G = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
AMP = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
TAG = sys.argv[3] if len(sys.argv) > 3 else f"g{G}_a{int(AMP)}"

ck = torch.load("male_graph.pt", map_location="cpu")
W = ck["W"]
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
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
assert int(emask_leg.sum()) == 118 and int(emask_neck.sum()) == 60
W2 = W.clone()
v = W2.values()
v[emask_leg] = Wv[emask_leg] * G
v[emask_neck] = Wv[emask_neck] * G


def run(events, seed):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W2, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)

    Z = torch.zeros(N, 1)
    I0 = torch.zeros(N, 1)
    for ch, amp in events:
        I0[ch] = amp
    for _ in range(SETTLE):
        step(Z)
    Xb = X.clone()
    peak_m, Xpk = -1.0, None
    sat = 0.0
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else Z)
        sat = max(sat, float((X[motor] >= 0.999).float().mean()))
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m, Xpk = m, X.clone()
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    return dm, sat


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


SEEDS = [11, 22, 33]
V = {k: [run(ev, s) for s in SEEDS] for k, ev in
     [("soloA", [(loom, AMP)]), ("soloB", [(olf, AMP)]),
      ("joint", [(loom, AMP), (olf, AMP)])]}
out = {"G": G, "amp": AMP, "seeds": SEEDS}
for k in V:
    out[f"{k}_mag"] = float(np.mean([np.abs(d).mean() for d, _ in V[k]]))
    out[f"{k}_sat"] = float(max(s for _, s in V[k]))
cs, resid, nr = [], [], []
for i in range(len(SEEDS)):
    dJ = V["joint"][i][0]
    dS = V["soloA"][i][0] + V["soloB"][i][0]
    cs.append(cos(dJ, dS))
    resid.append(float(np.linalg.norm(dJ - dS) / (np.linalg.norm(dS) + 1e-12)))
    nr.append(float(np.linalg.norm(dJ) / (np.linalg.norm(dS) + 1e-12)))
out.update({"cos_sum": float(np.mean(cs)), "resid": float(np.mean(resid)),
            "norm_ratio": float(np.mean(nr)),
            "cos_AB": float(np.mean([cos(V["soloA"][i][0], V["soloB"][j][0])
                                     for i in range(3) for j in range(3)]))})
print(f"[{TAG}] G={G} amp={AMP}: cos(dJ,dA+dB) {out['cos_sum']:+.3f} "
      f"resid {out['resid']:.3f} |dJ|/|dS| {out['norm_ratio']:.3f} "
      f"cos(A,B) {out['cos_AB']:+.3f} sat {out['joint_sat']:.3f} "
      f"mags A {out['soloA_mag']:.5f} B {out['soloB_mag']:.5f} J {out['joint_mag']:.5f}",
      flush=True)
json.dump(out, open(f"l23/results_l23b_{TAG}.json", "w"), indent=1)
