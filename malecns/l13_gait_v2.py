"""L13: malecns-gait-v2 — synapse-scale pathway weighting on DN->motor (lab only).

L11 verdict: brain events (looming/odor) die below MOTOR noise at in-degree-
diluted fidelity; direct DN->motor edges carry only 3.4% of the cord command
(modulatory). Question: can PER-SYNAPSE pathway weighting — multiply the real
DN->motor synapses (dst in motor, src in DN) by gain g — let a brain event
produce a REPRODUCIBLE (self-cos > .5) and EVENT-DISTINCT motor vector?

Honest framing: this is ENGINEERING, not biology — testing whether the
connectome CONTAINS a usable pathway once synaptic weights are freed (real
fly DNs gate cord programs; the flat-weight connectome may undercount their
effective drive).

Arms (3 noise seeds each, paired with l11 seeds 11/22/33):
  base    g=1   looming + odor                (paired baseline, ~noise per L11)
  eng5    g=5   looming + odor                (pathway gain sweep)
  eng50   g=50  looming + odor
  cut50   g=50  looming, engineered edges ZEROED after scaling? -> NO: cut = g=1
               equivalent... cleaner: eng50 W but DN activity CLAMPED at 0
               (opto lesson: clamp X, not edges) -> signal must vanish
  edgecut eng50 graph with ONLY the DN->motor edges removed, looming
               (edges carry it, not diffuse interior leakage)
Also: op-point (rho, active_frac, MOTOR baseline mean) per g — the gain must
not create tonic motor activity (that would be a fake signal).
"""
import json
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)  # be kind to the live duck on this box
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, EVENT = 300, 20
GAIN = 0.8846  # L11 bisected op point on this graph

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
mL = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]) & (side == "L"))[0]
mR = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]) & (side == "R"))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
olf = np.where(lab["class"].astype(str) == "olfactory")[0]
print(f"motor {len(motor)} (L {len(mL)}/R {len(mR)}) | DN {len(dn)} | "
      f"looming {len(loom)} | olf {len(olf)}", flush=True)

# --- engineered edge set: dst in motor, src in DN (same indexing as l11 cut)
rows = torch.repeat_interleave(torch.arange(N), W.crow_indices().diff())
mrow = np.zeros(N, bool); mrow[motor] = True
ndn = np.zeros(N, bool); ndn[dn] = True
emask = torch.from_numpy(mrow[rows.numpy()] & ndn[W.col_indices().numpy()])
n_eng = int(emask.sum())
Wv = W.values()
w_eng = Wv[emask]
print(f"engineered DN->motor edges: {n_eng:,} (mean w {w_eng.mean():.3f}, "
      f"max {w_eng.max():.1f})", flush=True)

# per-DN-class breakdown of the engineered set (interpretation)
src_cls = dn_typ[np.searchsorted(dn, W.col_indices().numpy()[emask.numpy()])]
import collections
cnt = collections.Counter(src_cls)
print("top DN classes into motor:", cnt.most_common(8), flush=True)


def make_W(g, cut=False):
    W2 = W.clone()  # CSR clone keeps structure; emask indices stay aligned
    v = W2.values()
    if cut:
        v[emask] = 0.0
    else:
        v[emask] = Wv[emask] * g
    return W2


def spectral_radius(W_, iters=100):
    v = torch.rand(W_.shape[0], 1)
    v /= v.norm()
    rho = 0.0
    for _ in range(iters):
        u = torch.sparse.mm(W_, v)
        n = u.norm()
        if n == 0 or torch.isnan(n):
            return float("nan")
        rho = float(n)
        v = u / n
    return rho


def run(W_, channel, amp, seed, clamp=None):
    """One arm. clamp = index set clamped to 0 every step (opto-silence)."""
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
    mbase = float(Xb[motor].mean())
    return dm, peak_m, turn, mbase


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


SEEDS = [11, 22, 33]
res = {"n_engineered_edges": n_eng, "w_eng_mean": float(w_eng.mean()),
       "gain_op": GAIN, "seeds": SEEDS, "arms": {}}

# graphs: g=1 (base), g=20, g=200 (mean w .002 -> DN slice needs big g to matter)
GRAPHS = {"base": make_W(1.0), "eng20": make_W(20.0), "eng200": make_W(200.0)}
GRAPHS["edgecut200"] = make_W(200.0, cut=True)
for name, Wg in GRAPHS.items():
    rho = spectral_radius(Wg)
    # motor baseline: settle once, read motor mean + active frac (seed 11)
    gen = torch.Generator().manual_seed(11)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)
    for _ in range(SETTLE):
        drive = torch.sparse.mm(Wg, X)
        t = (torch.relu(GAIN * drive + BG)
             + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
    res["arms"][name] = {"rho": rho,
                         "motor_base": float(X[motor].mean()),
                         "active_frac": float((X.squeeze(1) > 0.05).float().mean())}
    print(f"{name:10s} rho {rho:.4f} motor_base {X[motor].mean():.4f} "
          f"af {(X.squeeze(1) > 0.05).float().mean():.3f}", flush=True)

# DN sets to clamp (opto) — event-relevant port classes from L11
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(leg_dns) > 0, "DNp01-04 not found in male annotations"
assert len(neck_dns) > 0, "DNc01/02 not found in male annotations"
print(f"clamp sets: DNp01-04 {len(leg_dns)}, DNc01/02 {len(neck_dns)}", flush=True)

PLAN = [
    ("base",    GRAPHS["base"],    "looming", loom, 8.0, None),
    ("base",    GRAPHS["base"],    "odor",    olf,  8.0, None),
    ("eng20",   GRAPHS["eng20"],   "looming", loom, 8.0, None),
    ("eng20",   GRAPHS["eng20"],   "odor",    olf,  8.0, None),
    ("eng200",  GRAPHS["eng200"],  "looming", loom, 8.0, None),
    ("eng200",  GRAPHS["eng200"],  "odor",    olf,  8.0, None),
    ("clamp200", GRAPHS["eng200"], "looming", loom, 8.0, leg_dns),
    ("clamp200", GRAPHS["eng200"], "odor",    olf,  8.0, neck_dns),
    ("edgecut200", GRAPHS["edgecut200"], "looming", loom, 8.0, None),
]
V = {}
for gname, Wg, ev, ch, amp, clamp in PLAN:
    key = f"{gname}|{ev}"
    V[key] = [run(Wg, ch, amp, s, clamp=clamp) for s in SEEDS]
    mags = [float(np.abs(v[0]).mean()) for v in V[key]]
    print(f"{key:20s} |dm| {np.mean(mags):.5f} dpeak {np.mean([v[1] for v in V[key]]):.4f} "
          f"turn {np.mean([v[2] for v in V[key]]):+.4f} mbase {np.mean([v[3] for v in V[key]]):.4f}",
          flush=True)

print("\nmotor-VECTOR pairwise cos (3 seed pairs same-event = SELF; cross = loom vs odor):",
      flush=True)
COS = {}
for gname in ["base", "eng20", "eng200", "clamp200"]:
    for a, b in [("looming", "looming"), ("odor", "odor"), ("looming", "odor")]:
        ka, kb = f"{gname}|{a}", f"{gname}|{b}"
        if a == b:
            cs = [cos(V[ka][i][0], V[ka][j][0])
                  for i in range(3) for j in range(i + 1, 3)]
        else:
            cs = [cos(V[ka][i][0], V[kb][j][0])
                  for i in range(3) for j in range(3)]
        COS[f"{ka}~{kb}"] = float(np.mean(cs))
        print(f"  {gname:9s} {a:7s}~{b:7s}: {np.mean(cs):+.3f}", flush=True)

# edgecut self-cos (does the signal survive removing the engineered edges?)
for a in ["looming"]:
    cs = [cos(V[f"edgecut200|{a}"][i][0], V[f"edgecut200|{a}"][j][0])
          for i in range(3) for j in range(i + 1, 3)]
    COS[f"edgecut200|{a}~{a}"] = float(np.mean(cs))
    print(f"  edgecut200 {a}~{a}: {np.mean(cs):+.3f}", flush=True)

# top responder motor cells under eng200 looming (interpretation: leg pools?)
prof = np.mean([v[0] for v in V["eng200|looming"]], axis=0)
top = np.argsort(-prof)[:8]
mtyp = typ[motor]
print("eng200|looming top motor cells:", [(mtyp[t], round(float(prof[t]), 4))
                                          for t in top], flush=True)

res["cos"] = COS
res["dm_mag"] = {k: [float(np.abs(v[0]).mean()) for v in V[k]] for k in V}
res["dpeak"] = {k: [float(v[1]) for v in V[k]] for k in V}
res["turn"] = {k: [float(v[2]) for v in V[k]] for k in V}
res["motor_base_run"] = {k: [float(v[3]) for v in V[k]] for k in V}
json.dump(res, open("l13/results_l13.json", "w"), indent=1)
print(f"\ndone in {time.time()-t0:.0f}s -> l13/results_l13.json", flush=True)
