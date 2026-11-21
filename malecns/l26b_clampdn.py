"""L26b: is the ascending corollary carried by the JUMP-COMMAND DNs?

L26 main: the ascending lift during the looming chain is motor-INDEPENDENT
(jump_clampM identical) — a central corollary. This addendum asks WHICH
descending neurons carry it: clamp ONLY the 12 amplified command DNs
(DNp01-04 + DNc01/02) during the looming volley and read the ascending
pool again. Compares against the main run's saved jump mean vector.

  asc SNR drops   -> corollary rides the specific jump-command DNs
  asc SNR stays   -> corollary distributed across the broader DN population
                     (looming drives ~1300 DNs; only 12 were clamped)

CPU-only, descriptive only.
"""
import json
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU_BASE, DT, RMAX = 0.05, 0.010, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, EVENT, POST = 300, 20, 220
T = EVENT + POST
GAIN, G, AMP_EV = 0.8846, 200.0, 8.0
SEEDS = [11, 22, 33]
TAU_DEACT, RATIO = 0.051, 5.0

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
asc = np.where(np.isin(sup, ["ascending_neuron"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
cmd = np.concatenate([leg_dns, neck_dns])
typm = typ[motor]
POOL_F = np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN",
                                 "Tr flexor MN", "Acc. tr flexor MN"]))[0]
POOL_E = np.where(typm == "Ti extensor MN")[0]
A = len(asc)

rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
cols = W.col_indices().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
Wg = W.clone()
v = Wg.values()
v[torch.from_numpy(mrow[rows.numpy()] & leg_src[cols])] = \
    W.values()[torch.from_numpy(mrow[rows.numpy()] & leg_src[cols])] * G
v[torch.from_numpy(mrow[rows.numpy()] & neck_src[cols])] = \
    W.values()[torch.from_numpy(mrow[rows.numpy()] & neck_src[cols])] * G


def run(channel, seed, clamp):
    tv = np.full(N, TAU_BASE, np.float32)
    tv[motor[POOL_E]] = TAU_DEACT
    tv[motor[POOL_F]] = TAU_DEACT * RATIO
    tau = torch.from_numpy(tv).unsqueeze(1)
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(Wg, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[channel] = AMP_EV
    for _ in range(SETTLE):
        step(Z)
    base_a = X[asc].squeeze(1).numpy().copy()
    base_m = X[motor].squeeze(1).numpy().copy()
    noise = []
    for _ in range(60):
        step(Z)
        noise.append(float(X[asc].mean()))
    a_mu, a_sd = float(np.mean(noise)), float(np.std(noise))
    a_pk, m_pk = -1.0, -1.0
    da_pk = np.zeros(A, np.float32)
    dm_pk = np.zeros(len(motor), np.float32)
    for k in range(T):
        step(I0 if k < EVENT else Z)
        ma, aa = float(X[motor].mean()), float(X[asc].mean())
        if ma > m_pk:
            m_pk, dm_pk = ma, X[motor].squeeze(1).numpy() - base_m
        if aa > a_pk:
            a_pk, da_pk = aa, X[asc].squeeze(1).numpy() - base_a
    return dict(da_pk=da_pk, dm_pk=dm_pk, snr_a=float((a_pk - a_mu) / (a_sd + 1e-12)))


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


R = [run(loom, s, torch.from_numpy(cmd)) for s in SEEDS]
vecs = [r["da_pk"] for r in R]
self_c = float(np.mean([cos(vecs[i], vecs[j])
                        for i in range(3) for j in range(i + 1, 3)]))
jv = np.load("l26/asc_vectors.npz")["jump"]
cv = np.mean(vecs, axis=0)
snr = float(np.mean([r["snr_a"] for r in R]))
print(f"jump_clampDN asc SNR {snr:8.1f}x self {self_c:+.3f} "
      f"cos_vs_jump {cos(cv, jv):+.3f} | {time.time() - t0:.0f}s", flush=True)
json.dump({"asc_snr": snr, "asc_self": self_c,
           "cos_vs_jump": cos(cv, jv)},
          open("l26/results_l26b.json", "w"), indent=1)
print("done -> l26/results_l26b.json", flush=True)
