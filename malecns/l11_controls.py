"""L11 closing controls:
  1. touch_cord with the 23,616 direct DN->motor edges CUT: how much of the
     reproducible motor command flows through real DN->motor wiring vs
     cord-intrinsic?  (load-bearing check for the item title)
  2. random visual_projection stimulation (949 cells, 3 seeds) at the DN
     port: is the DN fingerprint event-SPECIFIC (ctrl self-cos high,
     ctrl|looming low) or just 'any stimulation'?
"""
import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, EVENT = 300, 20
GAIN = 0.8846

ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
cord_mech = np.where((sup == "vnc_sensory")
                     & pd.Series(cls).str.contains("mechano").to_numpy())[0]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
vp_pool = np.where(sup == "visual_projection")[0]
vp_pool = vp_pool[~np.isin(vp_pool, loom)]
rng = np.random.default_rng(7)
ctrls = [rng.choice(vp_pool, size=len(loom), replace=False) for _ in range(3)]

rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
mrow = np.zeros(N, bool); mrow[motor] = True
ndn = np.zeros(N, bool); ndn[dn] = True
cut_mask = torch.from_numpy(mrow[rows.numpy()] & ndn[W.col_indices().numpy()])
Wc = W.clone()
Wc.values()[cut_mask] = 0.0
print(f"cut {int(cut_mask.sum()):,} DN->motor edges")


def run(W_, channel, amp, seed):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)

    I0 = torch.zeros(N, 1)
    I0[channel] = amp
    for _ in range(SETTLE):
        step(torch.zeros(N, 1))
    Xb = X.clone()
    peak, Xpk = -1.0, None
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else torch.zeros(N, 1))
        m = X[motor].mean().item()
        if m > peak:
            peak, Xpk = m, X.clone()
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    dd = (Xpk[dn].squeeze(1) - Xb[dn].squeeze(1)).numpy()
    return dm, dd, peak


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


SEEDS = [11, 22, 33]
cut = [run(Wc, cord_mech, 2.0, s) for s in SEEDS]
print("touch CUT : motor delta-peak",
      [round(v[2], 4) for v in cut],
      "mean|d|", round(float(np.mean([np.abs(v[0]).mean() for v in cut])), 5))
cut_cos = [cos(cut[i][0], cut[j][0]) for i in range(3) for j in range(i + 1, 3)]
print("          motor self-cos", [round(c, 3) for c in cut_cos])

ctl = [run(W, c, 8.0, s) for c, s in zip(ctrls, SEEDS)]
self_cs = [cos(ctl[i][1], ctl[j][1]) for i in range(3) for j in range(i + 1, 3)]
loo = [run(W, loom, 8.0, s) for s in SEEDS]
cross = [cos(ctl[i][1], loo[j][1]) for i in range(3) for j in range(3)]
print("ctrl_vp DN self-cos", round(float(np.mean(self_cs)), 3),
      "| ctrl|looming", round(float(np.mean(cross)), 3),
      "| ctrl top DNs:",
      [typ[dn][t] for t in np.argsort(-np.mean([v[1] for v in ctl], 0))[:4]])
np.save("l11/cut_touch_motor.npy", np.array([v[0] for v in cut]))
