"""L27b: mechanism probes for the L27 oct-alone TTM nudge (2.5% of gesture,
SNR 3.3x) and the untested PERIPHERAL oct population. Standalone (loads the
graph itself; does NOT import l27_arousal).

1. octC-alone + X[DNp01-04]=0 clamp every step (L2 opto form): if the nudge
   collapses to the undriven floor (~1.5-1.7x, L19), it rides the x200
   DNp->motor gate (any DNp lift is an amplifier), not a separate path.
2. octALL-alone (101 cells incl. the 50 vnc_efferent whose census carries
   33% DN / 47% cord weight) amp 4: does the WIRED oct population move the
   cord on its own more than the central 51 do?
CPU-only, 12 rollouts.
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
SETTLE, OCTON, EVENT, POST = 300, 50, 20, 150
T = OCTON + EVENT + POST
GAIN, G, AMP = 0.8846, 200.0, 4.0
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
nt = pd.read_feather("data/body-neurotransmitters-male-cns-v1.0.feather")
mrg = lab.merge(nt[["body", "consensus_nt"]], left_on="bodyId",
                right_on="body", how="left")
cnt = mrg["consensus_nt"].fillna("none").astype(str).to_numpy()

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
oct_all = np.where(cnt == "octopamine")[0]
oct_periph = oct_all[np.isin(sup[oct_all],
                             ["vnc_efferent", "efferent_ascending"])]
oct_central = np.array([i for i in oct_all if i not in set(oct_periph)])
assert len(oct_all) == 101 and len(oct_central) == 51

typm = typ[motor]
M = len(motor)
TTM = np.where(np.array([str(t).startswith("TTMn") for t in typm]))[0]
POOL_E = np.where(typm == "Ti extensor MN")[0]
POOL_E = np.concatenate([POOL_E, np.where(typm == "Tr extensor MN")[0]])
POOL_F = np.concatenate([
    np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
    np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0]])

rows_np = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
emask_leg = torch.from_numpy(mrow[rows_np] & leg_src[cols])
emask_neck = torch.from_numpy(mrow[rows_np] & neck_src[cols])
Wv = W.values()
Wg = W.clone()
v = Wg.values()
v[emask_leg] = Wv[emask_leg] * G
v[emask_neck] = Wv[emask_neck] * G
assert int(emask_leg.sum()) == 118 and int(emask_neck.sum()) == 60

tv = np.full(N, TAU_BASE, np.float32)
tv[motor[POOL_E]] = TAU_DEACT
tv[motor[POOL_F]] = TAU_DEACT * RATIO
tau = torch.from_numpy(tv).unsqueeze(1)


def run_alone(oct_idx, amp, seed, clamp_dn=False):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)
    Z = torch.zeros(N, 1)
    clamp = torch.tensor(leg_dns) if clamp_dn else None

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(Wg, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0

    for _ in range(SETTLE):
        step(Z)
    I_oct = Z.clone(); I_oct[oct_idx] = amp
    for _ in range(OCTON):
        step(I_oct)
    base_m = X[motor].squeeze(1).numpy().copy()
    rec = np.zeros((M, T), dtype=np.float32)
    for k in range(T):
        step(I_oct)
        rec[:, k] = X[motor].squeeze(1).numpy() - base_m
    out = {}
    for nm, idx in [("TTM", TTM), ("ext", POOL_E), ("flex", POOL_F)]:
        tr = rec[idx].mean(0)
        noise = float(np.std(tr[EVENT + 40:EVENT + 100]))
        out[nm] = dict(peak=float(np.max(tr[:EVENT + 60])), snr=float(
            np.max(tr[:EVENT + 60]) / (noise + 1e-9)))
    out["dn_lift"] = float(np.mean([(X[leg_dns].mean()).item()]))
    return out


res = {}
for tag, idx, clamp in [
    ("octC4_alone", oct_central, False),
    ("octC4_alone_clampDNp", oct_central, True),
    ("octALL4_alone", oct_all, False),
    ("octALL4_alone_clampDNp", oct_all, True),
]:
    runs = [run_alone(idx, AMP, s, clamp_dn=clamp) for s in SEEDS]
    res[tag] = {p: dict(peak=float(np.mean([r[p]["peak"] for r in runs])),
                        snr=float(np.mean([r[p]["snr"] for r in runs])))
                for p in ["TTM", "ext", "flex"]}
    res[tag]["dn_lift"] = float(np.mean([r["dn_lift"] for r in runs]))
    print(f"{tag:22s} TTM {res[tag]['TTM']['peak']:.4f} "
          f"SNR {res[tag]['TTM']['snr']:.2f}x | ext "
          f"{res[tag]['ext']['peak']:.4f} | flex {res[tag]['flex']['peak']:.4f}"
          f" | DNp lift {res[tag]['dn_lift']:.4f} | {time.time() - t0:.0f}s",
          flush=True)

with open("l27/results_l27b.json", "w") as f:
    json.dump(res, f, indent=1)
print("wrote l27/results_l27b.json")
