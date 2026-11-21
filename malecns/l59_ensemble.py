"""L59: spec-seed-ensemble (LANE.md ideas-28).

The l51 hybrid + l55 hynohop schedules on the l45b 16-seed census grid —
distributional claims for the L57 contract (pooled gate, fast-window duty,
miss anatomy S_L-share, tracking robustness). Machinery l55_hop.py verbatim,
ARMS trimmed to the two schedules, SEEDS = census grid.

PREREG l59/PREREG.md first. Raw npz checkpoint BEFORE analysis (L45a).
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
MEAS0 = 500                       # per-seg measurement start (l39-l51 conv.)
SEEDS = [11, 22, 33] + list(range(101, 114))   # l45b census grid, n=16
ANCHOR_SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
HOP_AMP, HOP_VW = 0.5, 40
TRANS = [2000, 4000]
LOCK_TOL = 0.10
ARMS = ["hynohop", "hybrid"]
DM_PAIRS = [("hybrid", "hynohop")]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l32/l34/l39/l50/l51/l55 verbatim) ----------
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
assert len(mech) > 0
hopL = np.where((ltyp == "DNge046") & (lside == "L"))[0]
assert len(hopL) == 2, len(hopL)
log(f"mech {len(mech)} | 046L {len(hopL)}")

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- per-arm AMPA / HOPA tables (write-time asserted) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
for a in ARMS:                                  # hybrid AMPA for every arm
    for seg0, _, _ in SEGB:
        c = 0                                   # 500-on/400-off per 0.7 seg
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA[a][2000:4000] = ENT_AMP                # fast segment CONTINUOUS
HOPA = {a: np.zeros(WIN, bool) for a in ARMS}
for o in TRANS:
    HOPA["hybrid"][o:o + HOP_VW] = True

assert all(np.array_equal(AMPA[a], AMPA["hynohop"]) for a in ARMS)
for seg0, segend, f in SEGB:
    seg = AMPA["hynohop"][seg0:seg0 + SEG]
    if f == 0.7:
        assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
        assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
        assert (seg[1800:2000] == ENT_AMP).all()
    else:
        assert (AMPA["hynohop"][seg0:segend] == ENT_AMP).all()
assert not HOPA["hynohop"].any()
assert HOPA["hybrid"].sum() == 2 * HOP_VW
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
assert all(DRIVE_ON[a] == 4800 for a in ARMS), DRIVE_ON
log("drive-on 48.0s both arms | tables asserted")


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
    dm = {p: dict(first_div=-1, vmax=0.0) for p in DM_PAIRS}
    hop_win = np.zeros(WIN, bool)
    for o in TRANS:
        hop_win[o:o + HOP_VW] = True

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
                amp_k = ENT_AMP
            else:
                amp_k = float(AMPA[a][k])
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            if k >= 0 and HOPA[a][k]:
                drive[hopL, 0] += HOP_AMP
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
                if hop_win[i] and d > dm[p]["vmax"]:
                    dm[p]["vmax"] = d
                if d > 1e-6 and dm[p]["first_div"] < 0:
                    dm[p]["first_div"] = i
    out = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
               dm=dm, mm=mm, tr=tr)
    return out


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# raw checkpoint BEFORE analysis (L45a lesson)
np.savez_compressed(
    "l59/raw_l59.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")})

# ---------------- C0 anchors (15th chain anchor) ----------------
z55 = np.load("l55/raw_l55.npz")
c0 = {}
for a in ARMS:
    c0[f"{a}_maxd"] = max(
        float(np.abs(res[str(s)]["mm"][a][:WIN]
                     - z55[f"mm_{a}_{s}"][:WIN]).max()) for s in ANCHOR_SEEDS)
    for c in ("fL", "fR", "eL", "eR"):
        c0[f"{a}_{c}_maxd"] = max(
            float(np.abs(res[str(s)]["tr"][a][c][:WIN]
                         - z55[f"{c}_{a}_{s}"][:WIN]).max())
            for s in ANCHOR_SEEDS)
fd = [res[str(s)]["dm"][("hybrid", "hynohop")]["first_div"] for s in SEEDS]
vm = [res[str(s)]["dm"][("hybrid", "hynohop")]["vmax"] for s in SEEDS]
c0["fd_hybrid_all2000"] = all(v == 2000 for v in fd)
c0["volley_vmax_min"] = round(min(vm), 4)
c1 = dict(af_ok=all(0.01 < res[str(s)]["af"][a] < 0.9
                    for s in SEEDS for a in ARMS))
anchor_maxds = [v for k, v in c0.items() if k.endswith("_maxd")]
c0_pass = (all(v == 0.0 for v in anchor_maxds)
           and c0["fd_hybrid_all2000"] and min(vm) > 1e-6 and c1["af_ok"])
log(f"C0 {json.dumps(c0)} | pass {c0_pass}")

# ---------------- analysis (l55-verbatim) ----------------
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
            f_seg = dom_freq(res[str(s)]["mm"][a][a0_:b0])[0]
            bl_errs, ttl = [], None
            for b in range(WIN // BLK):
                if a0_ <= b * BLK < b0 and b * BLK > a0_:
                    f_hat, ratio = dom_freq(res[str(s)]["mm"][a][b * BLK:(b + 1) * BLK])
                    e = abs(f_hat - tg)
                    bl_errs.append(e)
                    if ttl is None and e <= LOCK_TOL:
                        ttl = b * BLK - a0_
            rows.append(dict(
                duty=round(float(np.nanmean(both)), 3),
                SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                f=round(f_seg, 3),
                err=round(float(np.mean(bl_errs)), 4), ttl=ttl))
        qall = np.zeros(len(TS), bool)
        q07 = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            qall |= (TS >= a0_ + MEAS0) & (TS < b0)
            if f == 0.7:
                q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
        cells[a][str(s)] = dict(
            segs=rows,
            duty_all=round(float(np.nanmean(
                (SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
            duty_07=round(float(np.nanmean(
                (SL[TS[q07]] >= .25) & (SR[TS[q07]] >= .25))), 3))

# ---------------- distributional reads (PREREG P1-P5) ----------------
def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


def rankcorr(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


preds = {}
dist = {}
for a in ARMS:
    pooled = np.array([cells[a][str(s)]["duty_all"] for s in SEEDS])
    seg1 = np.array([cells[a][str(s)]["segs"][1]["duty"] for s in SEEDS])
    seg1e = np.array([cells[a][str(s)]["segs"][1]["err"] for s in SEEDS])
    d07 = np.array([cells[a][str(s)]["duty_07"] for s in SEEDS])
    k_gate = int((pooled >= .5).sum())
    dist[a] = dict(
        pooled=[round(float(v), 3) for v in pooled],
        pooled_mean=round(float(pooled.mean()), 3),
        pooled_median=round(float(np.median(pooled)), 3),
        pooled_min=round(float(pooled.min()), 3),
        pooled_max=round(float(pooled.max()), 3),
        p_ge_half=k_gate, p_ge_half_wilson=wilson(k_gate, len(SEEDS)),
        seg1=[round(float(v), 3) for v in seg1],
        seg1_mean=round(float(seg1.mean()), 3),
        seg1_lt10=int((seg1 < .1).sum()),
        seg1_lt25=int((seg1 < .25).sum()),
        seg1_ge50=int((seg1 >= .5).sum()),
        seg1_err_le01=int((seg1e <= .01).sum()),
        seg1_err=[round(float(v), 4) for v in seg1e],
        duty07=[round(float(v), 3) for v in d07],
        duty07_mean=round(float(d07.mean()), 3))

# P3 miss anatomy: pooled-miss seeds -> failing segments -> side ownership
anatomy = {}
for a in ARMS:
    miss_rows, fail_segs = [], 0
    sl_owned = sr_owned = both_below = 0
    for s in SEEDS:
        cell = cells[a][str(s)]
        if cell["duty_all"] >= .5:
            continue
        fails = []
        for si, row in enumerate(cell["segs"]):
            if row["duty"] < .5:
                fails.append(si)
                fail_segs += 1
                sl_low = (row["SL"] is not None and row["SL"] < .25)
                sr_low = (row["SR"] is not None and row["SR"] < .25)
                if sl_low and sr_low:
                    both_below += 1
                elif sl_low:
                    sl_owned += 1
                elif sr_low:
                    sr_owned += 1
        miss_rows.append(dict(seed=s, duty=cell["duty_all"], fail_segs=fails,
                              seg_duties=[r["duty"] for r in cell["segs"]],
                              seg_SL=[r["SL"] for r in cell["segs"]],
                              seg_SR=[r["SR"] for r in cell["segs"]]))
    tot_sided = sl_owned + sr_owned + both_below
    anatomy[a] = dict(
        n_miss=len(miss_rows), fail_segs=fail_segs,
        sl_owned=sl_owned, sr_owned=sr_owned, both_below=both_below,
        sl_share=round(sl_owned / tot_sided, 3) if tot_sided else None,
        misses=miss_rows)

# P5 entry join (exploratory, small-n)
entry_join = {}
for a in ARMS:
    seg0_SL = np.array([cells[a][str(s)]["segs"][0]["SL"] or np.nan
                        for s in SEEDS], float)
    pooled = np.array([cells[a][str(s)]["duty_all"] for s in SEEDS])
    ok = ~np.isnan(seg0_SL)
    entry_join[a] = dict(
        rank_corr_seg0SL_vs_pooled=round(rankcorr(seg0_SL[ok], pooled[ok]), 3)
        if ok.sum() > 2 else None, n_ok=int(ok.sum()))

preds["P1_pooled_point_below_half"] = {
    a: bool(dist[a]["p_ge_half"] / len(SEEDS) < .5) for a in ARMS}
preds["P1_pooled"] = {a: dict(k=dist[a]["p_ge_half"], n=len(SEEDS),
                              wilson=dist[a]["p_ge_half_wilson"],
                              mean=dist[a]["pooled_mean"]) for a in ARMS}
preds["P2_fast_lottery_ge5of16_in_some_arm"] = bool(
    max(dist[a]["seg1_lt10"] for a in ARMS) >= 5)
preds["P2_seg1_lt10"] = {a: dist[a]["seg1_lt10"] for a in ARMS}
preds["P3_miss_SL_share"] = {a: anatomy[a]["sl_share"] for a in ARMS}
preds["P3_pass"] = {a: bool(anatomy[a]["sl_share"] is not None
                            and anatomy[a]["sl_share"] >= .5) for a in ARMS}
preds["P4_lock_12of16"] = {a: bool(dist[a]["seg1_err_le01"] >= 12)
                           for a in ARMS}
preds["P4_seg1_err_le01"] = {a: dist[a]["seg1_err_le01"] for a in ARMS}
preds["P5_entry_join"] = entry_join

verdict = dict(
    C0=c0, C0_pass=bool(c0_pass), C1=c1, fd_all=fd[:3] + ["..."] + fd[-3:],
    distributions=dist, miss_anatomy=anatomy, predictions=preds)
log("VERDICT " + json.dumps(
    {k: verdict[k] for k in ("C0_pass", "distributions", "miss_anatomy",
                             "predictions")})[:3400])

np.savez_compressed("l59/traces_l59.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
                       for a in ARMS for s in SEEDS},
                    **{f"SL_{a}_{s}": s_arrays(a, str(s))[0]
                       for a in ARMS for s in SEEDS},
                    **{f"SR_{a}_{s}": s_arrays(a, str(s))[1]
                       for a in ARMS for s in SEEDS})
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, segb=SEGB,
                      blk=BLK, seeds=SEEDS, ent_amp=ENT_AMP, hop_amp=HOP_AMP,
                      hop_vw=HOP_VW, trans=TRANS, drive_on=DRIVE_ON,
                      nodes=int(n), edges=len(gsrc)),
            cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS},
            distributions=dist, miss_anatomy=anatomy,
            predictions=preds, C0=c0, C0_pass=bool(c0_pass), C1=c1)
json.dump(dump, open("l59/results_l59.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l59/results_l59.json")
