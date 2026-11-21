"""L39: discrete-gait-controller — the smallest honest closed loop on the lab
cord. Two primitives from the L38 action set: ENTRAIN (sinusoidal mechano
drive, L34 regime, amp .3) tracking a stepped target 0.7 -> 1.4 -> 0.7 Hz,
plus a single brief HOP volley (DNge046_L free side / DNg110, amp .5,
400 ms) fired at each target transition. Can 2 primitives hold a target
gait-frequency trajectory against the cord's intrinsic attractors and
metastable side-flips (L33)?

PREREG claim levels in l39/PREREG.md, written first. Paired arms share ONE
generator + ONE per-step noise tensor (L36 lesson) so the free arm is
bit-identical to l34 anchors. P1-labeled descriptive; CPU-only; no live
changes; owner movement law respected (lab demo, never app motion).
"""
import json
import math
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 400
WIN = 6000
SEG = 2000                      # 20 s per target segment
BLK = 500                       # 5 s tracking blocks
MEAS0_SEG = 500                 # skip first 5 s of each segment for S
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05    # l32 arm-A frozen
ENT_AMP = 0.3                   # l34: locks + re-hosts antiphase
HOP_AMP, HOP_VW = 0.5, 40       # volley amp, 400 ms
TARGETS = [0.7, 1.4, 0.7]
LOCK_TOL = 0.10
ANCHOR = {11: 0.800, 22: 1.444, 33: 1.422}
ARMS = ["free", "ent", "ent_h046", "ent_h110"]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: subnetwork (l32/l34 verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()

nt = pd.read_feather("data/body-neurotransmitters-male-cns-v1.0.feather",
                     columns=["body", "consensus_nt"])
nt_map = dict(zip(nt["body"].astype(np.uint64).astype(str), nt["consensus_nt"]))
nt_names = np.array([str(nt_map.get(str(int(b)), "unknown")).lower() for b in ids])

w = pd.read_feather(
    "data/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
w = w[w["body_pre"].isin(idx) & w["body_post"].isin(idx)]
gsrc = w["body_pre"].map(idx).to_numpy(np.int64)
gdst = w["body_post"].map(idx).to_numpy(np.int64)
gw = w["weight"].to_numpy(np.float32)

cord = np.isin(sup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
dn_all = sup == "descending_neuron"
dn_into = np.zeros(len(ids), bool)
dn_into[gdst[cord[gsrc]]] = True
dn_into &= dn_all
keep = cord | dn_into

emask = keep[gsrc] & keep[gdst]
gsrc, gdst, gw = gsrc[emask], gdst[emask], gw[emask]
loc = -np.ones(len(ids), np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
lsup, ltyp, lside, lcls = sup[keep], typ[keep], side[keep], cls[keep]
lnt = nt_names[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)
log(f"sub nodes {n:,} | edges {len(gsrc):,} | {time.time()-t0:.0f}s")

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wa_vals = gw * signA[lsrc]
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy(Wa_vals.astype(np.float32)), (n, n)).coalesce().to_sparse_csr()

motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
tm = pd.Series(ltyp)
PAIRS = {}
for k in ("Ti", "Tr"):
    f = np.where(motor & tm.isin([f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (tm == f"{k} extensor MN"))[0]
    fL, fR = f[lside[f] == "L"], f[lside[f] == "R"]
    eL, eR = e[lside[e] == "L"], e[lside[e] == "R"]
    assert len(fL) and len(fR) and len(eL) and len(eR), (k, len(fL), len(fR))
    PAIRS[k] = dict(fL=fL, fR=fR, eL=eL, eR=eR)
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
assert len(mech) > 0

hop046 = np.where((ltyp == "DNge046") & (lside == "L"))[0]
hop110 = np.where(ltyp == "DNg110")[0]
assert len(hop046) == 2 and len(hop110) == 6, (len(hop046), len(hop110))
log(f"mech {len(mech)} | hop046_L {len(hop046)} | hop110 {len(hop110)}")


# ---------- paired 4-arm rollout, shared noise ----------
def dom_freq(x, lo=0.3):
    z = x - x.mean()
    ps = np.abs(np.fft.rfft(z)) ** 2
    fr = np.fft.rfftfreq(len(z), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    ratio = float(pb.max() / max(np.median(pb), 1e-30))
    return float(f_hat), ratio


def run_seed(seed):
    gen = torch.Generator().manual_seed(seed)
    X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    X = {a: X0.clone() for a in ARMS}
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    trans = [SEG, 2 * SEG]                       # volley steps
    in_volley = lambda k: any(t <= k < t + HOP_VW for t in trans)
    ph = 0.0
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in ("fL", "fR", "eL", "eR")}
          for a in ARMS}
    dm = {a: dict(first_div=-1, volley_max=0.0) for a in ("ent_h046", "ent_h110")}
    WbX = {a: None for a in ARMS}

    def step_all(k):
        nonlocal ph
        seg = min(k // SEG, 2)
        fd = TARGETS[seg]
        ph += 2 * math.pi * fd * DT
        mech_add = ENT_AMP * (0.5 + 0.5 * math.sin(ph))
        vol = in_volley(k)
        nz = NOISE * torch.randn(n, 1, generator=gen)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if a != "free":
                drive[mech, 0] = drive[mech, 0] + mech_add
            # BUG FIX (post-run catch): v1's `else hop110` fed the h110 volley
            # to the ent CONTROL arm too -> ent_h110 === ent by construction.
            # Volley now strictly per hop arm; ent is entrain-only.
            if vol and a == "ent_h046":
                drive[hop046, 0] += HOP_AMP
            if vol and a == "ent_h110":
                drive[hop110, 0] += HOP_AMP
            t = torch.relu(drive + BG)
            t = (t + nz).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])

    for k in range(SETTLE):
        step_all(-1 - k)                          # settle: no mech/volley
    for a in ARMS:
        af = float((X[a] > 0.05).float().mean())
        assert 0.01 < af < 0.9, (a, af)
    for i in range(WIN):
        step_all(i)
        for a in ARMS:
            mm[a][i] = X[a][motor].mean()
            for c, pools_c in (("fL", "fL"), ("fR", "fR"), ("eL", "eL"), ("eR", "eR")):
                tr[a][c][i] = X[a][PAIRS["Tr"][pools_c]].mean()
        for ha, ref in (("ent_h046", "ent"), ("ent_h110", "ent")):
            d = float((X[ha] - X[ref]).abs().max())
            if in_volley(i):
                dm[ha]["volley_max"] = max(dm[ha]["volley_max"], d)
                if d > 1e-6 and dm[ha]["first_div"] < 0:
                    dm[ha]["first_div"] = i - trans[0] if i < trans[0] + HOP_VW \
                        else i - trans[1]
    out = {"af": {a: float((X[a] > 0.05).float().mean()) for a in ARMS},
           "dm": dm, "blocks": {}, "segments": {}}
    nblk = WIN // BLK
    for a in ARMS:
        out["blocks"][a] = []
        for b in range(nblk):
            f_hat, ratio = dom_freq(mm[a][b * BLK:(b + 1) * BLK])
            seg = min(b * BLK // SEG, 2)
            out["blocks"][a].append(dict(b=b, f=f_hat, ratio=ratio,
                                         target=TARGETS[seg],
                                         err=abs(f_hat - TARGETS[seg])))
        segs = []
        for s in range(3):
            sl = slice(s * SEG + MEAS0_SEG, (s + 1) * SEG)
            fL, fR, eL, eR = (tr[a][c][sl] for c in ("fL", "fR", "eL", "eR"))
            S = -np.corrcoef(fL + fR, eL + eR)[0, 1]
            SL = -np.corrcoef(fL, eL)[0, 1]
            SR = -np.corrcoef(fR, eR)[0, 1]
            blocks = out["blocks"][a][s * 4:(s + 1) * 4]
            err = float(np.mean([x["err"] for x in blocks[1:]]))
            ttl = next((x["b"] - s * 4 for x in blocks[1:]
                        if x["err"] <= LOCK_TOL), None)
            _, ratio_seg = dom_freq(mm[a][sl])
            segs.append(dict(S=float(S), SL=float(SL), SR=float(SR),
                             track_err=err, ttl=ttl, ratio=ratio_seg))
        out["segments"][a] = segs
    out["_mm"] = {a: mm[a].copy() for a in ARMS}
    return out


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# ---------------- verdict ----------------
def seg_val(a, f, s):
    return res[str(s)]["segments"][a][f] if False else res[str(s)]["segments"][a][f]


c0 = True
# C0 on l34's EXACT window+band (last 45 s, 0.5 Hz floor) — window lesson
free_f = {s: dom_freq(res[str(s)]["_mm"]["free"][1500:], lo=0.5)[0] for s in SEEDS}
c0 = all(abs(free_f[s] - ANCHOR[s]) <= 0.03 for s in SEEDS)
c0_S = all(res[str(s)]["segments"]["free"][0]["S"] >= 0.40 for s in SEEDS)
c0_r = all(res[str(s)]["segments"]["free"][0]["ratio"] >= 100 for s in SEEDS)
c1 = {ha: all(res[str(s)]["dm"][ha]["volley_max"] > 1e-6
              and 0 <= res[str(s)]["dm"][ha]["first_div"] < HOP_VW
              for s in SEEDS) for ha in ("ent_h046", "ent_h110")}


def mean_track(a, s):
    return float(np.mean([x["track_err"] for x in res[str(s)]["segments"][a]]))


c2_n = sum(1 for s in SEEDS
           if mean_track("ent", s) <= 0.15
           and mean_track("ent", s) < 0.5 * mean_track("free", s))
c3 = {}
for ha in ("ent_h046", "ent_h110"):
    ttl_e = [x["ttl"] if x["ttl"] is not None else 4 for s in SEEDS
             for x in res[str(s)]["segments"]["ent"][1:]]
    ttl_h = [x["ttl"] if x["ttl"] is not None else 4 for s in SEEDS
             for x in res[str(s)]["segments"][ha][1:]]
    faster = float(np.median(ttl_h)) < float(np.median(ttl_e))
    better = sum(1 for s in SEEDS if mean_track(ha, s) < mean_track("ent", s))
    survives = all(x["S"] >= 0.25 for s in SEEDS
                   for x in res[str(s)]["segments"][ha])
    c3[ha] = dict(faster=faster, better_n=better, survives=survives,
                  pass_=bool((faster or better >= 2) and survives))
c4 = all(x["S"] >= 0.25 for a in ("ent", "ent_h046", "ent_h110")
         for s in SEEDS for x in res[str(s)]["segments"][a])
side_flips = {a: [[int(np.sign(x["SL"] - x["SR"])) for x in res[str(s)]["segments"][a]]
                  for s in SEEDS] for a in ARMS}

verdict = dict(C0_substrate=bool(c0 and c0_S and c0_r), free_f=free_f,
               C1_hop_lands=c1, C2_entrain_tracks=dict(n=c2_n),
               C3_hop_accelerates=c3, C4_survival=bool(c4),
               side_dominance=side_flips,
               track={a: {str(s): [round(x["track_err"], 3) for x in
                                   res[str(s)]["segments"][a]] for s in SEEDS}
                      for a in ARMS},
               ttl={a: {str(s): [x["ttl"] for x in res[str(s)]["segments"][a][1:]]
                        for s in SEEDS} for a in ARMS},
               S={a: {str(s): [round(x["S"], 3) for x in res[str(s)]["segments"][a]]
                      for s in SEEDS} for a in ARMS},
               dm={ha: {str(s): res[str(s)]["dm"][ha] for s in SEEDS}
                   for ha in ("ent_h046", "ent_h110")})
log("VERDICT " + json.dumps(verdict)[:1500])

np.savez_compressed("l39/traces.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["_mm"][a]
                       for a in ARMS for s in SEEDS})
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, seg=SEG,
                      blk=BLK, seeds=SEEDS, ent_amp=ENT_AMP, hop_amp=HOP_AMP,
                      hop_vw=HOP_VW, targets=TARGETS, lock_tol=LOCK_TOL,
                      hop046=hop046.tolist(), hop110=hop110.tolist(),
                      mech_cells=int(len(mech)), nodes=int(n), edges=len(gsrc)),
            blocks={a: {str(s): res[str(s)]["blocks"][a] for s in SEEDS}
                    for a in ARMS},
            segments={a: {str(s): res[str(s)]["segments"][a] for s in SEEDS}
                      for a in ARMS},
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            dm={ha: {str(s): res[str(s)]["dm"][ha] for s in SEEDS}
                for ha in ("ent_h046", "ent_h110")},
            verdict=verdict)
json.dump(dump, open("l39/results_l39.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l39/results_l39.json")
