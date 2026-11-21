"""L11: DN->motor on the MALE connectome — real-wiring gait prototype (lab only).

Question (LANE.md L11): with the REAL DN->motor edges (23,720 direct) in
male_graph.pt, do sensory events produce DISTINCT motor-population gait
commands {move, turn} — replacing the female's linear-head stand-in?

Design (mirrors live brain.py exactly, CPU, [N,1] sparse operands):
  rate update:  X += dt/tau * (relu(gain*(W@X + I) + bg) + noise).clamp(max=1) - X
  op point:     gain = 0.95/rho (bisected to 15% active if off-target)
  arms:         looming (LC4/16/11/12, 949 cells) vs odor (olfactory, 2639)
                vs 3x random same-size visual_projection controls
                vs looming/odor rerun with DN->motor edges CUT (load-bearing)
  read:         motor L/R means AT the event peak (fast-transient lesson);
                move = peak - baseline, turn = L/R asymmetry shift.
Run: .venv/bin/python l11_dn_motor.py   (writes l11/ artifacts)
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
DATA = "data"
OUT = "l11"
os.makedirs(OUT, exist_ok=True)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, EVENT, POST = 300, 12, 40

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
print(f"graph loaded {tuple(W.shape)} nnz {W._nnz():,} ({time.time()-t0:.0f}s)")

ann = pd.read_feather(f"{DATA}/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all(), "id order mismatch"

sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()

motor_all = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
motor_L = motor_all[side[motor_all] == "L"]
motor_R = motor_all[side[motor_all] == "R"]
dn_all = np.where(sup == "descending_neuron")[0]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
olf = np.where(cls == "olfactory")[0]
vp_pool = np.where(sup == "visual_projection")[0]
vp_pool = vp_pool[~np.isin(vp_pool, loom)]
print(f"motor {len(motor_all)} (L {len(motor_L)}/R {len(motor_R)}) | DN {len(dn_all)} "
      f"| looming {len(loom)} | olfactory {len(olf)} | vp-control pool {len(vp_pool)}")


def spectral_radius(W, iters=200):
    v = torch.rand(W.shape[0], 1)
    v /= v.norm()
    rho = 0.0
    for _ in range(iters):
        u = torch.sparse.mm(W, v)
        n = u.norm()
        if n == 0 or torch.isnan(n):
            return float("nan")
        rho = float(n)
        v = u / n
    return rho


class MaleBrain:
    def __init__(self, W):
        self.W, self.N = W, W.shape[0]
        self.reset()

    def reset(self):
        gen = torch.Generator().manual_seed(1234)  # same seed every arm -> paired noise
        self.gen = gen
        self.X = (BG + NOISE * torch.randn(self.N, 1, generator=gen)).clamp(0, 1)

    def step(self, I=None, gain=1.0):
        drive = torch.sparse.mm(self.W, self.X)          # [N,1] operand!
        if I is not None:
            drive = drive + I
        target = torch.relu(gain * drive + BG)
        target = target + NOISE * torch.randn(self.N, 1, generator=self.gen)
        target = target.clamp(max=RMAX)
        self.X = self.X + (DT / TAU) * (target - self.X)


def read(br, sigs):
    X = br.X.squeeze(1)
    return {k: float(X[ix].mean()) for k, ix in sigs.items()}


sigs = {"motor": motor_all, "mL": motor_L, "mR": motor_R, "dn": dn_all}
tX = torch.arange(N).unsqueeze(1)


def run_arm(W, gain, channel=None, amp=1.0):
    br = MaleBrain(W)
    for _ in range(SETTLE):
        br.step(gain=gain)
    base = read(br, sigs)
    traj = []
    I = None
    if channel is not None:
        I = torch.zeros(N, 1)
        I[channel] = amp
    for k in range(EVENT + POST):
        br.step(I=I if k < EVENT else None, gain=gain)
        traj.append(read(br, sigs))
    return base, traj


rho = spectral_radius(W)
gain = 0.95 / rho
brain = MaleBrain(W)
for _ in range(SETTLE):
    brain.step(gain=gain)
af0 = float((brain.X.squeeze(1) > 0.05).float().mean())
print(f"rho {rho:.4f} gain {gain:.4f} -> active_frac {af0:.3f}")
if not 0.05 <= af0 <= 0.35:  # matched op point (null-lesson)
    lo, hi = 0.2 / rho, 2.5 / rho
    for _ in range(14):
        mid = (lo + hi) / 2
        b = MaleBrain(W)
        for _ in range(SETTLE):
            b.step(gain=mid)
        af = float((b.X.squeeze(1) > 0.05).float().mean())
        print(f"  bisect gain {mid:.3f} -> af {af:.3f}")
        if af > 0.15:
            hi = mid
        else:
            lo = mid
        if abs(af - 0.15) < 0.02:
            break
    gain, af0 = mid, af
print(f"operating point: gain {gain:.4f}, active_frac {af0:.3f}")

rng = np.random.default_rng(7)
ctrls = [rng.choice(vp_pool, size=len(loom), replace=False) for _ in range(3)]

results = {"op": {"rho": rho, "gain": gain, "active_frac": af0,
                  "N": int(N), "nnz": int(W._nnz())},
           "pops": {"motor": len(motor_all), "motor_L": len(motor_L),
                    "motor_R": len(motor_R), "dn": len(dn_all),
                    "looming": len(loom), "olfactory": len(olf)},
           "arms": {}}

for name, ch in [("looming", loom), ("odor", olf),
                 ("ctrl_vp_0", ctrls[0]), ("ctrl_vp_1", ctrls[1]),
                 ("ctrl_vp_2", ctrls[2])]:
    base, traj = run_arm(W, gain, ch)
    results["arms"][name] = {"base": base, "traj": traj}
    pk = int(np.argmax([t["motor"] for t in traj]))
    print(f"{name:10s} motor base {base['motor']:.4f} peak {traj[pk]['motor']:.4f} "
          f"dn {base['dn']:.3f}->{traj[pk]['dn']:.3f}")

# DN->motor CUT control: zero the direct edges (dst in motor, src in DN)
rows = torch.repeat_interleave(
    torch.arange(N), W.crow_indices().diff())
mrow = np.zeros(N, bool); mrow[motor_all] = True
ndn = np.zeros(N, bool); ndn[dn_all] = True
cut_mask = torch.from_numpy(
    mrow[rows.numpy()] & ndn[W.col_indices().numpy()])
n_cut = int(cut_mask.sum())
W2 = W.clone()
W2.values()[cut_mask] = 0.0
print(f"DN->motor edges cut: {n_cut:,} (R4 measured 23,720)")
results["n_dn_motor_cut"] = n_cut

for name, ch in [("looming_CUT", loom), ("odor_CUT", olf)]:
    base, traj = run_arm(W2, gain, ch)
    results["arms"][name] = {"base": base, "traj": traj}
    pk = int(np.argmax([t["motor"] for t in traj]))
    print(f"{name:10s} motor base {base['motor']:.4f} peak {traj[pk]['motor']:.4f} "
          f"dn {base['dn']:.3f}->{traj[pk]['dn']:.3f}")


def decode(traj, base, ev=EVENT):
    win = traj[:ev + 10]  # peak read at/just after stimulus (fast-transient lesson)
    mpk = max(t["motor"] for t in win)
    k = next(i for i, t in enumerate(win) if t["motor"] == mpk)
    t = win[k]
    asym = (t["mL"] - t["mR"]) / (t["mL"] + t["mR"] + 1e-9)
    basym = (base["mL"] - base["mR"]) / (base["mL"] + base["mR"] + 1e-9)
    return {"move": mpk - base["motor"], "turn": asym - basym,
            "motor_peak": mpk, "dn_peak": max(w["dn"] for w in win) - base["dn"],
            "peak_step": k}


for name, a in results["arms"].items():
    a["decode"] = decode(a["traj"], a["base"])

json.dump(results, open(f"{OUT}/results_l11.json", "w"), indent=1)
print(f"\ndone in {time.time()-t0:.0f}s -> {OUT}/results_l11.json")
for name, a in results["arms"].items():
    d = a["decode"]
    print(f"{name:12s} move {d['move']:+.4f} turn {d['turn']:+.4f} "
          f"dn {d['dn_peak']:+.4f} (peak@{d['peak_step']})")
