"""L28: grooming-alternation — L18's Ti-pair "co-activation (grooming
reading)" was never tested AS grooming: drive the antagonist channels
ALTERNATELY (flexor DNg95 + an extensor channel from the L22 atlas) at
grooming-range rhythms and ask whether the motor output alternates.

Channels (L13b/L20 optogenetic-style form): direct volley on the DN class
cells, x200 gain on THAT class's DN->motor edges only, lit5x decay taus
(ext 51 ms measured / flex 255 ms underdetermined, L18 A), DT 10 ms.

Static first (claim-carrier): double dissociation DNg95(flex z+18.4,
ext -0.2) vs extensor channel; SIGN gate (L24/L25): the chosen extensor
class must be net-EXCITATORY onto extensor MNs — candidates DNg79
(4 cells, 158 edges, ext .272 z+15.4, flex DEPLETED .018 z-2.2) then
DNge037 (2 cells, 141 edges, ext .248 z+16.6, flex .013 z-2.3).

Dynamic (P1-labeled, descriptive only — owner movement law): square-wave
DN drive, sweep f in {1, 2, 5} Hz around the L25 free-regime boundary
(half-period 30 steps = 1.67 Hz):
  alt{f}  A on half-cycle, B on the other  (anti-phase drive)
  sim{f}  A+B on the SAME half-cycle       (in-phase control)
  soloA / soloB  constant drive            (static refs + SNR gate)
Measures: per-pool modulation depth vs static ref, fundamental amplitude
at f (Goertzel over integer cycles), power fraction at f, flex-vs-ext
relative phase at f (180 deg = alternation, 0 = co-activation), pool SNR,
op point af0. 3 seeds. CPU-only.

Honest labels: this is a CARRIER test of the model class (uniform-tau
interior + lit-tau motor pools + x200 direct edges), not a wiring-credit
claim (no rewired null) and not a WHEN-claim from a uniform-tau model
(L15 rule respected: pools carry calibrated taus, drive is exogenous).
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU_BASE, DT, RMAX = 0.05, 0.010, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 300
GAIN = 0.8846            # op point bisected in L11
G = 200.0                # per-class pathway gain (L13b)
AMP = 8.0                # DN volley amp (RMAX-pinned; amp is a dead lever)
SEEDS = [11, 22, 33]
TAU_DEACT, RATIO = 0.051, 5.0   # L18 Arm A: ext 51 ms / flex 255 ms
FREQS = [1.0, 2.0, 5.0]
CYCLES = {1.0: 6, 2.0: 8, 5.0: 10}
SOLO_STEPS = 300

os.makedirs("l28", exist_ok=True)
t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).to_numpy()

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
typm = typ[motor]
M = len(motor)

POOL_F_idx = np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN",
                                     "Tr flexor MN", "Acc. tr flexor MN"]))[0]
POOL_E_idx = np.where(np.isin(typm, ["Ti extensor MN", "Tr extensor MN"]))[0]
assert len(POOL_F_idx) > 0 and len(POOL_E_idx) > 0

clsA = dn[np.isin(dn_typ, ["DNg95"])]
assert len(clsA) == 2, len(clsA)

rows_np = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
Wv = W.values()
mrow = np.zeros(N, bool); mrow[motor] = True
fpool = np.zeros(N, bool); fpool[motor[POOL_F_idx]] = True
epool = np.zeros(N, bool); epool[motor[POOL_E_idx]] = True


def class_mask(name):
    src = np.zeros(N, bool)
    src[dn[np.isin(dn_typ, [name])]] = True
    return src


def sign_share(name, poolmask):
    """net signed weight + edge count from class `name` onto `poolmask`.
    CSR convention: W[target, source] under torch.sparse.mm -> rows are
    TARGETS, cols are SOURCES (l27 emask form)."""
    src = class_mask(name)
    m = src[cols] & poolmask[rows_np]
    return float(Wv[m].sum()), int(m.sum())


cands = []
for name in ["DNg79", "DNge037"]:
    sE, nE = sign_share(name, epool)
    sF, nF = sign_share(name, fpool)
    cands.append(dict(name=name, sign_ext=sE, edges_ext=nE,
                      sign_flex=sF, edges_flex=nF))
    print(f"candidate {name}: ext sign {sE:+.4f} ({nE} edges) "
          f"flex sign {sF:+.4f} ({nF} edges)", flush=True)
pick = next((c for c in cands if c["sign_ext"] > 0), None)
assert pick is not None, "no excitatory extensor candidate"
nameB = pick["name"]
clsB = dn[np.isin(dn_typ, [nameB])]
print(f"channel B = {nameB} ({len(clsB)} cells, ext sign "
      f"{pick['sign_ext']:+.4f})", flush=True)

# static double-dissociation numbers for the record
sA_f, nA_f = sign_share("DNg95", fpool)
sA_e, nA_e = sign_share("DNg95", epool)
static = dict(
    A=dict(name="DNg95", cells=int(len(clsA)), sign_flex=sA_f,
           edges_flex=nA_f, sign_ext=sA_e, edges_ext=nA_e),
    B=pick,
    dissociation=dict(
        A_flex_over_ext=sA_f / (abs(sA_e) + 1e-12),
        B_ext_over_flex=pick["sign_ext"] / (abs(pick["sign_flex"]) + 1e-12)),
)

# per-class amplification (L13b): A->flexor MNs, B->extensor MNs only
# rows=targets (motor pools), cols=sources (the DN class cells)
srcA = np.zeros(N, bool); srcA[clsA] = True
srcB = np.zeros(N, bool); srcB[clsB] = True
emA = torch.from_numpy(mrow[rows_np] & fpool[rows_np] & srcA[cols])
emB = torch.from_numpy(mrow[rows_np] & epool[rows_np] & srcB[cols])
Wg = W.clone()
v = Wg.values()
v[emA] = Wv[emA] * G
v[emB] = Wv[emB] * G
assert int(emA.sum()) > 0 and int(emB.sum()) > 0
print(f"amplified x{G:.0f}: {nameB}->ext {int(emB.sum())} edges, "
      f"DNg95->flex {int(emA.sum())} edges", flush=True)

tv = np.full(N, TAU_BASE, np.float32)
tv[motor[POOL_E_idx]] = TAU_DEACT
tv[motor[POOL_F_idx]] = TAU_DEACT * RATIO
tau = torch.from_numpy(tv).unsqueeze(1)


def run(mode, freq, seed):
    """One rollout. mode in {alt, sim, soloA, soloB}."""
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(Wg, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)

    Z = torch.zeros(N, 1)
    for _ in range(SETTLE):
        step(Z)
    af0 = float((X > 0.05).float().mean())
    base = X[motor].squeeze(1).numpy().copy()
    # per-step pool noise from a settle tail (spontaneous fluctuation)
    settle_tail = []
    for _ in range(100):
        step(Z)
        xm = X[motor].squeeze(1).numpy()
        settle_tail.append((float(xm[POOL_F_idx].mean()),
                            float(xm[POOL_E_idx].mean())))
    st = np.array(settle_tail)
    noise = dict(flex=float(st[:, 0].std()), ext=float(st[:, 1].std()))
    basef = float(st[:, 0].mean()); basee = float(st[:, 1].mean())

    if mode.startswith("solo"):
        T, P = SOLO_STEPS, 0
    else:
        P = int(round(1.0 / (freq * DT)))
        T = CYCLES[freq] * P
    H = max(1, P // 2) if P else 1
    IA = Z.clone(); IA[clsA] = AMP
    IB = Z.clone(); IB[clsB] = AMP

    trF = np.zeros(T, np.float32); trE = np.zeros(T, np.float32)
    for k in range(T):
        if mode == "soloA":
            I = IA
        elif mode == "soloB":
            I = IB
        else:
            ph = (k // H) % 2
            if mode == "alt":
                I = IA if ph == 0 else IB
            else:  # sim: both on the same half-cycle
                I = IA + IB if ph == 0 else Z
        step(I)
        xm = X[motor].squeeze(1).numpy()
        trF[k] = float(xm[POOL_F_idx].mean()) - basef
        trE[k] = float(xm[POOL_E_idx].mean()) - basee
    return dict(trF=trF, trE=trE, af0=af0, noise=noise, T=T, P=P if not mode.startswith("solo") else 0)


def goertzel(x, P):
    """fundamental coefficient for a signal with integer cycles of period P."""
    T = len(x)
    assert T % P == 0, (T, P)
    k = np.arange(T)
    return (2.0 / T) * np.sum(x * np.exp(-2j * np.pi * k / P))


def analyze(r, freq, sref_f, sref_e):
    trF, trE = r["trF"] - r["trF"].mean(), r["trE"] - r["trE"].mean()
    P = r["P"]
    Cf, Ce = goertzel(trF, P), goertzel(trE, P)
    rel = np.angle(Ce * np.conj(Cf), deg=True)  # ext rel flex
    rel180 = abs(((rel + 180) % 360) - 180)      # distance from anti-phase
    pw = lambda x: float(np.mean(x ** 2))
    Pf, Pe = abs(Cf) ** 2 / 2, abs(Ce) ** 2 / 2
    fracf = Pf / (pw(trF) + 1e-12); frace = Pe / (pw(trE) + 1e-12)
    return dict(
        amp_f=float(abs(Cf)), amp_e=float(abs(Ce)),
        depth_ratio_f=float((trF.max() - trF.min()) / 2 /
                            (sref_f + 1e-12)),
        depth_ratio_e=float((trE.max() - trE.min()) / 2 /
                            (sref_e + 1e-12)),
        powfrac_f=float(fracf), powfrac_e=float(frace),
        rel_phase_deg=float(rel), dist_from_antiphase_deg=float(rel180),
        snr_f=float(abs(Cf) / (r["noise"]["flex"] + 1e-12)),
        snr_e=float(abs(Ce) / (r["noise"]["ext"] + 1e-12)),
        af0=r["af0"], T=r["T"],
    )


ARMS = {}
runs = {}
for mode in ["soloA", "soloB"]:
    runs[mode] = [run(mode, 0, s) for s in SEEDS]
sref_f = float(np.mean([r["trF"][-100:].mean() for r in runs["soloA"]]))
sref_e = float(np.mean([r["trE"][-100:].mean() for r in runs["soloB"]]))
print(f"static refs: flex {sref_f:.4f} ext {sref_e:.4f} | noise "
      f"{runs['soloA'][0]['noise']}", flush=True)
ARMS["soloA"] = dict(mean=dict(snr_f=float(sref_f /
                  (runs['soloA'][0]['noise']['flex'] + 1e-12)), sref=sref_f))
ARMS["soloB"] = dict(mean=dict(snr_e=float(sref_e /
                  (runs['soloB'][0]['noise']['ext'] + 1e-12)), sref=sref_e))

for f in FREQS:
    for mode in ["alt", "sim"]:
        tag = f"{mode}{f:g}"
        rs = [run(mode, f, s) for s in SEEDS]
        runs[tag] = rs
        st = [analyze(r, f, sref_f, sref_e) for r in rs]
        ARMS[tag] = dict(
            per_seed=st,
            mean={k: float(np.mean([x[k] for x in st]))
                  for k in st[0] if k != "rel_phase_deg"},
            mean_circ_phase=float(np.angle(np.mean(
                np.exp(1j * np.deg2rad([x["rel_phase_deg"] for x in st]))),
                deg=True)),
        )
        m = ARMS[tag]["mean"]
        print(f"{tag}: depth f {m['depth_ratio_f']:.2f} e "
              f"{m['depth_ratio_e']:.2f} | amp@f f {m['amp_f']:.4f} e "
              f"{m['amp_e']:.4f} (snr {m['snr_f']:.0f}x/{m['snr_e']:.0f}x) | "
              f"powfrac {m['powfrac_f']:.2f}/{m['powfrac_e']:.2f} | rel phase "
              f"{ARMS[tag]['mean_circ_phase']:+.0f} deg "
              f"(anti-dist {m['dist_from_antiphase_deg']:.0f})", flush=True)

out = dict(static=static, sref=dict(flex=sref_f, ext=sref_e),
           freqs=FREQS, arms=ARMS,
           channel_B=nameB, candidates=cands)
with open("l28/results_l28.json", "w") as f:
    json.dump(out, f, indent=1, default=float)
np.savez_compressed(
    "l28/pool_traces.npz",
    **{f"{tag}__{p}__{i}": runs[tag][i][p]
       for tag in runs for i in range(len(SEEDS)) for p in ["trF", "trE"]})
print(f"\nwrote l28/results_l28.json + pool_traces.npz | total "
      f"{time.time() - t0:.0f}s", flush=True)
