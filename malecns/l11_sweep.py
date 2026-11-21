"""L11 sweep: find stimulus amplitude where events propagate in the male graph.

Male in-degrees (~150 avg) are ~5-10x the female's (~30), so female amps
(0.5-3.0) die in one hop here. Sweep looming amp, read DN/motor deflection
and global saturation; pick the smallest amp with a real motor read.
"""
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, EVENT = 300, 20

ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
olf = np.where(lab["class"].astype(str).to_numpy() == "olfactory")[0]


class B:
    def __init__(self):
        self.gen = torch.Generator().manual_seed(1234)
        self.X = (BG + NOISE * torch.randn(N, 1, generator=self.gen)).clamp(0, 1)

    def step(self, I, gain):
        drive = torch.sparse.mm(W, self.X) + I
        t = torch.relu(gain * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=self.gen)).clamp(max=RMAX)
        self.X = self.X + (DT / TAU) * (t - self.X)


GAIN = 0.8846  # bisected op point af .164 (l11 run)


def arm(channel, amp):
    b = B()
    g = torch.Generator().manual_seed(99)
    for _ in range(SETTLE):
        I = torch.zeros(N, 1)
        I += NOISE * 0  # noise inside step already
        b.step(torch.zeros(N, 1), GAIN)
    I0 = torch.zeros(N, 1)
    I0[channel] = amp
    base_m, base_d = b.X[motor].mean().item(), b.X[dn].mean().item()
    hist = []
    for k in range(EVENT + 30):
        b.step(I0 if k < EVENT else torch.zeros(N, 1), GAIN)
        hist.append((b.X[motor].mean().item(), b.X[dn].mean().item(),
                     b.X[channel].mean().item()))
    af = (b.X.squeeze(1) > 0.05).float().mean().item()
    pm = max(h[0] for h in hist)
    pd_ = max(h[1] for h in hist)
    return base_m, pm, base_d, pd_, hist[0][2], af


t0 = time.time()
print("amp | motor .base->peak | DN base->peak | stim-rate | af_after")
for amp in [1, 3, 6, 10, 15, 22, 30]:
    bm, pm, bd, pd_, sr, af = arm(loom, float(amp))
    print(f"{amp:3d} | {bm:.4f} -> {pm:.4f} (d {pm-bm:+.4f}) | {bd:.4f} -> "
          f"{pd_:.4f} (d {pd_-bd:+.4f}) | {sr:.2f} | {af:.3f}")
print(f"{time.time()-t0:.0f}s")
