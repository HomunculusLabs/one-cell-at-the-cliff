"""L60: side-asymmetric-entrain (LANE.md ideas-29 + t80 amendment).

Machinery l59_ensemble.py VERBATIM (l32 arm-A frozen, hynohop schedule, no
hops), seeds = the 8 hynohop misses of l59. Arms split the mech entrain drive
by rootSide: a100 (symmetric, bit-identity anchor vs l59 raw), a125/a150
(L-side boost x1.25/x1.5), r080 (L-side cut x0.8, direction control).
Ratio applies ONLY at k>=0 (settle symmetric) so every arm shares the settled
state and diverges purely from the window drive (paired read, L45b rule).

PREREG l60/PREREG.md + ADDENDUM first. Raw npz checkpoint before analysis.
CPU-only; P1-labeled; no live changes.
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
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
BLK = 500
MEAS0 = 500
SEEDS = [22, 101, 103, 104, 107, 109, 111, 112]     # l59 hynohop misses
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
LOCK_TOL = 0.10
ARMS = ["a100", "a125", "a150", "r080"]
RATIO = {"a100": 1.0, "a125": 1.25, "a150": 1.5, "r080": 0.8}
DM_PAIRS = [(a, "a100") for a in ("a125", "a150", "r080")]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l59 verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
rside = lab["rootSide"].astype(str).to_numpy()
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
lroot = rside[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)
log(f"sub nodes {n:,} | edges {len(gsrc):,} | {time.time()-t0:.0f}s")

ntk = nt_names[keep]
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in ntk], np.float32)
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
assert len(mech) == 3588, len(mech)
mechL = mech[lroot[mech] == "L"]
mechR = mech[lroot[mech] == "R"]
mechU = mech[~np.isin(lroot[mech], ["L", "R"])]
assert len(mechL) + len(mechR) + len(mechU) == len(mech)
assert len(np.intersect1d(mechL, mechR)) == 0
log(f"mech {len(mech)} | rootSide L {len(mechL)} R {len(mechR)} unkn {len(mechU)}")

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- AMPA table: hynohop schedule (no hops) ----------
AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
DRIVE_ON = int((AMPA > 0).sum()) + SETTLE
assert DRIVE_ON == 4800, DRIVE_ON
for seg0, segend, f in SEGB:
    seg = AMPA[seg0:seg0 + SEG]
    if f == 0.7:
        assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
        assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
        assert (seg[1800:2000] == ENT_AMP).all()
    else:
        assert (AMPA[seg0:segend] == ENT_AMP).all()
log("drive-on 48.0s | hynohop AMPA asserted")


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


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


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
    settle_ph = 0.0
    SIGS = ("fL", "fR", "eL", "eR")
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    dm = {p: dict(first_div=-1, vmax=0.0, signed=0.0) for p in DM_PAIRS}
    dm_last = {p: 0.0 for p in DM_PAIRS}

    def step_all(k):
        nonlocal settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            ph_k = PHI[k]
        else:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
        sin_ph = math.sin(ph_k)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if k < 0:
                amp_k = ENT_AMP            # settle SYMMETRIC for every arm
            else:
                amp_k = float(AMPA[k])
            if amp_k > 0.0:
                if RATIO[a] == 1.0:        # l59 original form (bit-identity)
                    drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
                else:                       # ratio only at k>=0 (PREREG ADD 1)
                    drive[mechL, 0] = drive[mechL, 0] + amp_k * RATIO[a] * (0.5 + 0.5 * sin_ph)
                    drive[mechR, 0] = drive[mechR, 0] + amp_k * (0.5 + 0.5 * sin_ph)
                    drive[mechU, 0] = drive[mechU, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            t = torch.relu(drive + BG)
            t = (t + nz).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])

    for k in range(SETTLE):
        step_all(-1 - k)
    for a in ARMS:
        af = float((X[a] > 0.05).float().mean())
        assert 0.01 < af < 0.9, (a, af)
    for i in range(WIN):
        step_all(i)
        for a in ARMS:
            mm[a][i] = X[a][motor].mean()
            for c in SIGS:
                tr[a][c][i] = X[a][PAIRS["Tr"][c]].mean()
        if i >= 1:
            for p in DM_PAIRS:
                d = float((X[p[0]] - X[p[1]]).abs().max())
                if d > 1e-6 and dm[p]["first_div"] < 0:
                    dm[p]["first_div"] = i
                if d > dm[p]["vmax"]:
                    dm[p]["vmax"] = d
                dm_last[p] = d
    for p in DM_PAIRS:
        dm[p]["signed"] = dm_last[p]
    out = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
               dm=dm, mm=mm, tr=tr)
    return out


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# raw checkpoint BEFORE analysis (L45a lesson)
np.savez_compressed(
    "l60/raw_l60.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")})

# ---------------- C0 anchors (16th chain anchor) ----------------
z59 = np.load("l59/raw_l59.npz")
c0 = {}
c0["a100_mm_maxd"] = max(
    float(np.abs(res[str(s)]["mm"]["a100"][:WIN]
                 - z59[f"mm_hynohop_{s}"][:WIN]).max()) for s in SEEDS)
for c in ("fL", "fR", "eL", "eR"):
    c0[f"a100_{c}_maxd"] = max(
        float(np.abs(res[str(s)]["tr"]["a100"][c][:WIN]
                     - z59[f"{c}_hynohop_{s}"][:WIN]).max()) for s in SEEDS)
c0["dm_probes"] = {f"{p[0]}-a100": dict(
    first_div=res[str(s)]["dm"][p]["first_div"],
    vmax=round(res[str(s)]["dm"][p]["vmax"], 4))
    for p in DM_PAIRS for s in SEEDS[:2]}
anchor_maxds = [v for k, v in c0.items() if k.endswith("_maxd")]
c1 = dict(af_ok=all(0.01 < res[str(s)]["af"][a] < 0.9
                    for s in SEEDS for a in ARMS))
dm_ok = all(res[str(s)]["dm"][p]["first_div"] == 0 and
            res[str(s)]["dm"][p]["vmax"] > 1e-6
            for s in SEEDS for p in DM_PAIRS)
c0_pass = (all(v == 0.0 for v in anchor_maxds) and c1["af_ok"] and dm_ok)
log(f"C0 {json.dumps({k: v for k, v in c0.items() if k != 'dm_probes'})} "
    f"| dm_ok {dm_ok} | pass {c0_pass}")

# ---------------- analysis ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    fL, fR, eL, eR = (res[s]["tr"][a][c] for c in ("fL", "fR", "eL", "eR"))
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    SM[(a, s)] = (SL, SR)
    return SL, SR


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    if not q.any():
        return None
    return round(float(np.nanmedian(arr[TS[q]])), 3)


cells = {a: {str(s): {} for s in SEEDS} for a in ARMS}
for a in ARMS:
    for s in SEEDS:
        SL, SR = s_arrays(a, str(s))
        rows = []
        for si, (a0_, b0, tg) in enumerate(SEGB):
            lo, hi = a0_ + MEAS0, b0
            q = (TS >= lo) & (TS < hi)
            both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
            dSL = float(np.nanmean(SL[TS[q]] >= 0.25))
            dSR = float(np.nanmean(SR[TS[q]] >= 0.25))
            f_seg = dom_freq(res[str(s)]["mm"][a][a0_:b0])[0]
            bl_errs, ttl = [], None
            for b in range(WIN // BLK):
                if a0_ <= b * BLK < b0 and b * BLK > a0_:
                    f_hat, ratio_ = dom_freq(res[str(s)]["mm"][a][b * BLK:(b + 1) * BLK])
                    e = abs(f_hat - tg)
                    bl_errs.append(e)
                    if ttl is None and e <= LOCK_TOL:
                        ttl = b * BLK - a0_
            rows.append(dict(
                duty=round(float(np.nanmean(both)), 3),
                dutySL=round(dSL, 3), dutySR=round(dSR, 3),
                SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                f=round(f_seg, 3),
                err=round(float(np.mean(bl_errs)), 4), ttl=ttl))
        qall = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            qall |= (TS >= a0_ + MEAS0) & (TS < b0)
        cells[a][str(s)] = dict(
            segs=rows,
            duty_all=round(float(np.nanmean(
                (SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
            dutySL_all=round(float(np.nanmean(SL[TS[qall]] >= .25)), 3),
            dutySR_all=round(float(np.nanmean(SR[TS[qall]] >= .25)), 3),
            err_all=round(float(np.mean([r["err"] for r in rows])), 4))

# ---------------- PREREG predictions ----------------
def arm_side(a, key):
    return np.array([cells[a][str(s)][key] for s in SEEDS])


sl100 = arm_side("a100", "dutySL_all")
sl125 = arm_side("a125", "dutySL_all")
sl150 = arm_side("a150", "dutySL_all")
sl080 = arm_side("r080", "dutySL_all")
sr100 = arm_side("a100", "dutySR_all")
preds = {}
preds["P1_dose"] = dict(
    means={a: round(float(arm_side(a, "dutySL_all").mean()), 3)
           for a in ARMS},
    gate=round(float(sl150.mean() - sl100.mean()), 3),
    P1_pass=bool(sl150.mean() > sl125.mean() > sl100.mean()
                 and sl150.mean() - sl100.mean() >= 0.10))
preds["P2_gate"] = dict(
    k_ge_half={a: int((arm_side(a, "duty_all") >= .5).sum()) for a in ARMS},
    P2_pass=bool(max(int((arm_side(a, "duty_all") >= .5).sum())
                     for a in ARMS) >= 6))
preds["P3_lock"] = dict(
    err_all={a: round(float(arm_side(a, "err_all").mean()), 4) for a in ARMS},
    n_le01={a: int((arm_side(a, "err_all") <= .01).sum()) for a in ARMS},
    P3_pass=bool(all(int((arm_side(a, "err_all") <= .01).sum()) >= 6
                     for a in ARMS)))
preds["P4_nocrash"] = dict(
    meansSR={a: round(float(arm_side(a, "dutySR_all").mean()), 3) for a in ARMS},
    P4_pass=bool(all(arm_side(a, "dutySR_all").mean()
                     >= sr100.mean() - 0.10 for a in ARMS)))
preds["P5_direction"] = dict(
    P5_pass=bool(sl080.mean() <= sl100.mean()
                 and int((sl125 > sl080).sum()) >= 6),
    n_a125_gt_r080=int((sl125 > sl080).sum()))
per_seed = {a: dict(pooled=[cells[a][str(s)]["duty_all"] for s in SEEDS],
                    dSL=[cells[a][str(s)]["dutySL_all"] for s in SEEDS],
                    dSR=[cells[a][str(s)]["dutySR_all"] for s in SEEDS])
            for a in ARMS}

verdict = dict(C0={k: v for k, v in c0.items() if k != "dm_probes"},
               C0_pass=bool(c0_pass), dm_ok=bool(dm_ok),
               predictions=preds, per_seed=per_seed)
log("VERDICT " + json.dumps(verdict)[:3000])

np.savez_compressed("l60/traces_l60.npz",
                    **{f"SL_{a}_{s}": s_arrays(a, str(s))[0]
                       for a in ARMS for s in SEEDS},
                    **{f"SR_{a}_{s}": s_arrays(a, str(s))[1]
                       for a in ARMS for s in SEEDS})
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, segb=SEGB,
                      blk=BLK, seeds=SEEDS, ent_amp=ENT_AMP, ratios=RATIO,
                      asym_window_only=True, drive_on=DRIVE_ON,
                      nodes=int(n), edges=len(gsrc),
                      mech=dict(nL=int(len(mechL)), nR=int(len(mechR)),
                                nU=int(len(mechU)))),
            cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS},
            predictions=preds, per_seed=per_seed,
            C0={k: v for k, v in c0.items() if k != "dm_probes"},
            C0_pass=bool(c0_pass), dm_ok=bool(dm_ok))
json.dump(dump, open("l60/results_l60.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l60/results_l60.json")
