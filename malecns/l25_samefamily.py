"""L25: SAME-FAMILY composition — two flexor routes into SHARED pools.

L23's superposition pair (DNp01-04 jump + DNc01/02) had disjoint motor
targets; the honest counter-test is same-family: two crouch/flexor DN
classes fired together. Prediction if composition breaks: sub-additive
flexor peak (shared-pool mass joint < soloA+soloB) + RMAX ceiling onset
at high gain; staggered onsets (L20 form) may rescue B's peak.

Route choice (L24 sign lesson): DNg105's flexor edges are ALL inhibitory
-> excluded as an excitatory route. A = DNg95 (positive IPSI mirror,
L20 crouch carrier). B = argmax over the other L20 crouch classes
(DNge079/DNg74_b/DNg35/DNg108) by POSITIVE flexor weight, tie-broken by
flexor-type profile overlap with DNg95 (shared-pool honesty).

ESTIMAND LABEL (tick 37 amendment, 2611.14508): every arm re-applies the
real-tuned per-class gain G on the REAL wiring = P1-form. The
additivity/sub-additivity QUESTION (cos ~ 1, joint/solo ratios) is valid
in P1-form; any claim read as "the wiring PREVENTS X" would need a
gain-re-tuned (P2) control — not made here.
Sobol one-deciding-param: solo peak HEADROOM to RMAX at G — saturation
sub-additivity is decided by how close solo flexor peaks sit to 1.0;
we measure absolute pool levels, not just deltas.

Arms (3 seeds, G=200, L24 machinery verbatim; G=2000 arms for sat onset):
  noise / soloA / soloB / joint / jClampA (joint, A clamped)
  stag30/60/100  (A at t=0 for 20 steps, B at t=DEL for 20)
  hi_soloA / hi_soloB / hi_joint  (G=2000)
CPU-only, no live changes.
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
G, G_HI, AMP = 200, 2000, 8.0
CAND = ["DNg95", "DNge079", "DNg74_b", "DNg35", "DNg108"]

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
mtyp = typ[motor]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]

flex_t = ["Ti flexor MN", "Acc. ti flexor MN", "Tr flexor MN", "Acc. tr flexor MN"]
mflex = np.isin(mtyp, flex_t)

rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy()
mrow = np.zeros(N, bool)
mrow[motor] = True
dn_edge = mrow[rows] & np.isin(cols, dn)  # edges DN -> motor
pos = {int(c): i for i, c in enumerate(motor)}


def class_stat(name):
    cells = dn[dn_typ == name]
    sel = dn_edge & np.isin(cols, cells)
    w = vals[sel]
    # row = postsynaptic target (motor), col = presynaptic source (DN)
    tgt_idx = rows[sel]
    src_ok = bool(np.isin(cols[sel], cells).all()) if sel.sum() else True
    assert src_ok, "source cells leaked into class edge set"
    ttypes = np.array([mtyp[pos[int(c)]] for c in tgt_idx]) if len(tgt_idx) else np.array([], dtype="<U32")
    flex = np.isin(ttypes, flex_t)
    prof = {}
    for tname in flex_t:
        prof[tname] = float(w[ttypes == tname].sum())
    return {
        "cells": len(cells), "edges": int(sel.sum()),
        "w_sum": float(w.sum()), "w_pos": float(w[w > 0].sum()),
        "w_neg": float(w[w < 0].sum()),
        "flex_edges": int(flex.sum()), "flex_wsum": float(w[flex].sum()),
        "flex_profile": prof,
    }


print("== static sign/pass over L20 crouch classes ==", flush=True)
stats = {c: class_stat(c) for c in CAND}
for c, s in stats.items():
    print(f"{c:9s} cells {s['cells']} edges {s['edges']:4d} w_sum {s['w_sum']:+.3f} "
          f"(+{s['w_pos']:.3f}/{s['w_neg']:.3f}) flex_w {s['flex_wsum']:+.3f} "
          f"flex_edges {s['flex_edges']}", flush=True)

A = "DNg95"
assert stats[A]["w_pos"] > 0 and stats[A]["flex_wsum"] > 0
# B: positive flexor weight sum, max cosine of flexor-type profile with A
pa = np.array([stats[A]["flex_profile"][t] for t in flex_t])
best, bestk = None, -2.0
for c in CAND:
    if c == A or stats[c]["flex_wsum"] <= 0:
        continue
    pc = np.array([stats[c]["flex_profile"][t] for t in flex_t])
    k = float(pa @ pc / (np.linalg.norm(pa) * np.linalg.norm(pc) + 1e-12))
    print(f"  overlap {c} vs {A}: flex-profile cos {k:+.3f} flex_w {stats[c]['flex_wsum']:+.3f}",
          flush=True)
    if k > bestk:
        best, bestk = c, k
B = best
print(f"ROUTE A = {A}, ROUTE B = {B} (profile-overlap pick)", flush=True)

cellsA = dn[dn_typ == A]
cellsB = dn[dn_typ == B]
assert len(cellsA) > 0 and len(cellsB) > 0


def amplify(cells, gain):
    s = np.zeros(N, bool)
    s[cells] = True
    m = torch.from_numpy(mrow[rows] & s[cols])
    W2 = W.clone()
    v = W2.values()
    v[m] = W.values()[m] * gain
    return W2, int(m.sum())


Wg, nA = amplify(cellsA, G)
_, nB = amplify(cellsB, G)  # count only; combined W built per-arm below
assert nA > 0 and nB > 0


def build(arms, gain):
    """arms: list of cell-arrays; one W2 with all amplified."""
    W2 = W.clone()
    v = W2.values()
    tot = 0
    for cells in arms:
        s = np.zeros(N, bool)
        s[cells] = True
        m = torch.from_numpy(mrow[rows] & s[cols])
        v[m] = W.values()[m] * gain
        tot += int(m.sum())
    return W2, tot


Wg, nAB = build([cellsA, cellsB], G)
Wh, nABh = build([cellsA, cellsB], G_HI)
print(f"amplified edges: G{nA}+{nB}={nAB} | G_HI {nABh} (x{G}/x{G_HI})", flush=True)

flex_mask_motor = mflex
flexL_idx = motor[mflex & (lab["somaSide"].astype(str).to_numpy()[motor] == "L")]
flexR_idx = motor[mflex & (lab["somaSide"].astype(str).to_numpy()[motor] == "R")]
POOLS = {"flexL": flexL_idx, "flexR": flexR_idx}
print("pools:", {k: len(v) for k, v in POOLS.items()}, flush=True)

TOT = 180  # covers A(20) + DEL<=100 + B(20) + tail


def run(events, seed, W2, clamp=None):
    """events: list of (cell, amp, start, dur)."""
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W2, X) + I
        t = torch.relu(GAIN * drive + BG)
        # L25 mechanism probe: fraction of cells whose PRE-noise relu target
        # sits at the RMAX ceiling — t-clipping can make composition
        # sub-additive even when sat(X) (post-integration) reads 0.
        c = float((t[motor] >= 0.999).float().mean())
        cp = {p: float((t[mi] >= 0.999).float().mean()) for p, mi in POOLS.items()}
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0
        return c, cp

    Z = torch.zeros(N, 1)
    for _ in range(SETTLE):
        step(Z)
    Xb = X.clone()
    I0 = torch.zeros(N, 1)
    for c, a, st, du in events:
        I0[c] = a

    tr = {p: np.zeros(TOT) for p in POOLS}
    lvl = {p: [] for p in POOLS}
    clips, clipp = [], {p: [] for p in POOLS}
    peak_m, Xpk = -1.0, None
    acc = np.zeros(len(motor))
    sat = 0.0
    for k in range(TOT):
        # input mask per step (few events)
        I = torch.zeros(N, 1)
        for c, a, st, du in events:
            if st <= k < st + du:
                I[c] = a
        cm, cpm = step(I)
        clips.append(cm)
        for p in cpm:
            clipp[p].append(cpm[p])
        d = (X[motor] - Xb[motor]).squeeze(1)
        acc += d.numpy()
        for p, mi in POOLS.items():
            tr[p][k] = float(X[mi].mean() - Xb[mi].mean())
            lvl[p].append(float(X[mi].mean()))
        sat = max(sat, float((X[motor] >= 0.999).float().mean()))
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m, Xpk = m, X.clone()
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    dm_int = acc / TOT
    return {"dm": dm, "dm_int": dm_int, "tr": tr,
            "lvl_max": {p: float(np.max(v)) for p, v in lvl.items()},
            "sat": sat, "peak": peak_m,
            "clip": {"motor_mean": float(np.mean(clips)),
                     "motor_max": float(np.max(clips)),
                     "pools": {p: float(np.mean(v)) for p, v in clipp.items()}}}


def ev(cells, start=0, dur=EVENT):
    return [(int(c), AMP, start, dur) for c in np.asarray(cells).reshape(-1)]


SEEDS = [11, 22, 33]
DEL = 30
PLAN = [
    ("noise", [], None, Wg),
    ("soloA", ev(cellsA), None, Wg),
    ("soloB", ev(cellsB), None, Wg),
    ("joint", ev(cellsA) + ev(cellsB), None, Wg),
    ("jClampA", ev(cellsA) + ev(cellsB), cellsA, Wg),
    ("stag10", ev(cellsA) + ev(cellsB, start=10), None, Wg),
    ("stag20", ev(cellsA) + ev(cellsB, start=20), None, Wg),
    ("stag30", ev(cellsA) + ev(cellsB, start=30), None, Wg),
    ("stag60", ev(cellsA) + ev(cellsB, start=60), None, Wg),
    ("stag100", ev(cellsA) + ev(cellsB, start=100), None, Wg),
    ("hi_soloA", ev(cellsA), None, Wh),
    ("hi_soloB", ev(cellsB), None, Wh),
    ("hi_joint", ev(cellsA) + ev(cellsB), None, Wh),
]
V = {}
for key, e, clamp, W2 in PLAN:
    V[key] = [run(e, s, W2, clamp=clamp) for s in SEEDS]
    ms = {p: np.mean([r["tr"][p].max() for r in V[key]]) for p in POOLS}
    print(f"{key:9s} flexL_pk {ms['flexL']:+.4f} flexR_pk {ms['flexR']:+.4f} "
          f"sat {max(r['sat'] for r in V[key]):.3f} "
          f"lvlL {np.mean([r['lvl_max']['flexL'] for r in V[key]]):.3f} "
          f"clipL {np.mean([r['clip']['pools']['flexL'] for r in V[key]]):.3f}", flush=True)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


res = {"A": A, "B": B, "G": G, "G_HI": G_HI, "seeds": SEEDS,
       "edges": {"A": nA, "B": nB}, "static": stats,
       "pool_sizes": {k: len(v) for k, v in POOLS.items()},
       "arms": {}, "snr": {}, "ratios": {}, "stagger": {}, "hi": {}, "clamp": {}}

# SNR gate (L19 rule): solo window-trace peak / noise, per pool
for p in POOLS:
    s = max(np.mean([r["tr"][p].max() for r in V["soloA"]]),
            np.mean([r["tr"][p].max() for r in V["soloB"]]))
    nz = np.mean([np.abs(r["tr"][p]).max() for r in V["noise"]]) + 1e-12
    res["snr"][p] = float(s / nz)
    print(f"SNR {p}: {s / nz:7.1f}x", flush=True)

# per-arm window stats
for k in V:
    res["arms"][k] = {
        "tr_pk": {p: [float(r["tr"][p].max()) for r in V[k]] for p in POOLS},
        "lvl_max": {p: [float(r["lvl_max"][p]) for r in V[k]] for p in POOLS},
        "sat": [r["sat"] for r in V[k]],
        "clip_flexL": [r["clip"]["pools"]["flexL"] for r in V[k]],
        "clip_motor_max": [r["clip"]["motor_max"] for r in V[k]],
    }

# shared-pool mass ratio joint/(soloA+soloB) — THE sub-additivity measure
print("\n== shared-pool mass ratio joint/(soloA+soloB) ==", flush=True)
for p in POOLS:
    for tag, hi in (("", False), ("hi_", True)):
        j = np.array(res["arms"][f"{tag}joint"]["tr_pk"][p])
        sA = np.array(res["arms"][f"{tag}soloA"]["tr_pk"][p])
        sB = np.array(res["arms"][f"{tag}soloB"]["tr_pk"][p])
        r = j / (sA + sB + 1e-12)
        key = f"{p}{'_hi' if hi else ''}"
        res["ratios"][key] = [float(x) for x in r]
        print(f"  {key:9s}: {np.mean(r):.3f}  (seeds {r.round(3)})", flush=True)

# additivity of the vector
for form in ("dm", "dm_int"):
    cs, rr = [], []
    for i in range(3):
        dJ = V["joint"][i][form]
        dS = V["soloA"][i][form] + V["soloB"][i][form]
        cs.append(cos(dJ, dS))
        rr.append(float(np.linalg.norm(dJ - dS) / (np.linalg.norm(dS) + 1e-12)))
    res["ratios"][f"cos_{form}"] = float(np.mean(cs))
    res["ratios"][f"resid_{form}"] = float(np.mean(rr))
    print(f"COS[{form}] dJoint vs dA+dB: {np.mean(cs):+.3f} resid {np.mean(rr):.3f}",
          flush=True)

# stagger rescue: B's own peak in its window vs solo B peak
print("\n== stagger: B-window peak / solo-B peak (rescue) ==", flush=True)
for d in (10, 20, 30, 60, 100):
    arm = f"stag{d}"
    rec = {}
    for p in POOLS:
        vals_ = []
        for r in V[arm]:
            w = r["tr"][p][d + 5: d + 60]  # B window+tail
            vals_.append(float(np.max(w)))
        solo = np.array(res["arms"]["soloB"]["tr_pk"][p])
        rec[p] = float(np.mean(np.array(vals_) / (solo + 1e-12)))
    res["stagger"][arm] = rec
    print(f"  DEL={d:3d}: " + "  ".join(f"{p} {v:.2f}" for p, v in rec.items()), flush=True)

# saturation onset vs gain
res["hi"]["sat"] = {k: max(r["sat"] for r in V[k]) for k in ("hi_soloA", "hi_soloB", "hi_joint")}
res["hi"]["lvl_flexL"] = {k: float(np.mean([r["lvl_max"]["flexL"] for r in V[k]]))
                          for k in ("hi_soloA", "hi_soloB", "hi_joint")}
print(f"\nG=200 sat joint {max(r['sat' ] for r in V['joint']):.3f} | "
      f"G=2000 sat soloA {res['hi']['sat']['hi_soloA']:.3f} "
      f"soloB {res['hi']['sat']['hi_soloB']:.3f} joint {res['hi']['sat']['hi_joint']:.3f}",
      flush=True)

# clamp control: jClampA ~ soloB
m = np.mean([cos(V["jClampA"][i]["dm"], V["soloB"][j]["dm"])
             for i in range(3) for j in range(3)])
res["clamp"]["cos_clampA_vs_soloB"] = float(m)
print(f"clamp: cos(jClampA, soloB) {m:+.3f}", flush=True)

json.dump(res, open("l25/results_l25.json", "w"), indent=1)
print(f"\ndone {time.time() - t0:.0f}s -> l25/results_l25.json", flush=True)
