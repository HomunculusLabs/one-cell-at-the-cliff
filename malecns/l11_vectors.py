"""L11 vectors: event-distinct motor/DN population PATTERNS + the reflex arc.

l11_sweep showed: a saturating LC volley moves motor MEAN by only +2e-4
(male in-degrees ~5x female => multi-hop focal events die at population-mean
level). Two honest questions remain for the gait prototype:
  1. VECTOR level: do looming and odor produce DISTINCT motor deflection
     vectors (per-cell patterns through real DN->motor wiring), above the
     same-event across-noise-seed spread?
  2. REFLEX arc: vnc_sensory -> intrinsic -> motor is 2 hops (357k + 155k
     edges) -- does a cord mechano event produce a REAL motor command?
Arms: looming(8) odor(8) touch_cord(2) x 3 noise seeds each.
"""
import json
import time

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
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
mL = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]) & (side == "L"))[0]
mR = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]) & (side == "R"))[0]
dn = np.where(sup == "descending_neuron")[0]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
olf = np.where(cls == "olfactory")[0]
cord_mech = np.where((sup == "vnc_sensory")
                     & pd.Series(cls).str.contains("mechano").to_numpy())[0]
print(f"cord mechano sensory: {len(cord_mech)}")
dn_typ = typ[dn]

ARMS = {"looming": (loom, 8.0), "odor": (olf, 8.0), "touch_cord": (cord_mech, 2.0)}
SEEDS = [11, 22, 33]


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
    peak_m = -1.0
    Xpk = None
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else torch.zeros(N, 1))
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m = m
            Xpk = X.clone()
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    dd = (Xpk[dn].squeeze(1) - Xb[dn].squeeze(1)).numpy()
    turn = float((Xpk[mL].mean() - Xpk[mR].mean())
                 / (Xpk[mL].mean() + Xpk[mR].mean() + 1e-9)
                 - (Xb[mL].mean() - Xb[mR].mean())
                 / (Xb[mL].mean() + Xb[mR].mean() + 1e-9))
    return dm, dd, peak_m, turn


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


t0 = time.time()
V = {}
for name, (ch, amp) in ARMS.items():
    V[name] = [run(W, ch, amp, s) for s in SEEDS]
    mags = [np.abs(v[0]).mean() for v in V[name]]
    turns = [v[3] for v in V[name]]
    print(f"{name:10s} motor-vec mean|d| {np.mean(mags):.5f} "
          f"delta-mean {np.mean([v[2] for v in V[name]]):.4f} turn {np.mean(turns):+.4f}")

print("\npairwise motor-VECTOR cos (mean over seed pairs):")
events = list(ARMS)
S = {}
for i, a in enumerate(events):
    for b in events[i:]:
        if a == b:
            cs = [cos(V[a][si][0], V[a][sj][0])
                  for si in range(3) for sj in range(si + 1, 3)]
        else:
            cs = [cos(V[a][si][0], V[b][sj][0])
                  for si in range(3) for sj in range(3)]
        S[f"{a}|{b}"] = float(np.mean(cs))
        print(f"  {a:10s} vs {b:10s}: {np.mean(cs):+.3f}")

# DN-level pattern (where brain events ARE visible) + top responder DNs
print("\nDN-vector cos + top responders:")
D = {}
for i, a in enumerate(events):
    for b in events[i:]:
        if a == b:
            cs = [cos(V[a][si][1], V[a][sj][1])
                  for si in range(3) for sj in range(si + 1, 3)]
        else:
            cs = [cos(V[a][si][1], V[b][sj][1])
                  for si in range(3) for sj in range(3)]
        D[f"{a}|{b}"] = float(np.mean(cs))
        print(f"  {a:10s} vs {b:10s}: {np.mean(cs):+.3f}")
for name in events:
    prof = np.mean([v[1] for v in V[name]], axis=0)
    top = np.argsort(-prof)[:6]
    print(f"  {name} top DN responders:",
          [(dn_typ[t], round(float(prof[t]), 4)) for t in top])

json.dump({"motor_cos": S, "dn_cos": D,
           "mags": {k: [float(np.abs(v[0]).mean()) for v in V[k]] for k in V},
           "turns": {k: [v[3] for v in V[k]] for k in V},
           "seeds": SEEDS},
          open("l11/vectors_l11.json", "w"), indent=1)
print(f"\n{time.time()-t0:.0f}s -> l11/vectors_l11.json")
