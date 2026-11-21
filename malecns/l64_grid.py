"""L64: echo-dose-phase-map (LANE.md ideas-31). PREREG l64/PREREG.md FIRST.

Grid gain {.1,.25,.5} x delay {2,5,10,20} steps x sign {+,-} of the L63
delayed own-antagonist-mass echo onto mechano, on the l55/l59 base chop
schedule, seeds 11/22/33. Machinery l63_closed.py verbatim; CPU-only; no
live changes.
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
SEEDS = [11, 22, 33]
SEEDS8 = [11, 22, 33, 101, 105, 109, 111, 113]
G, BETA, D = 0.01, 2.0, 0.05
ENT_AMP = 0.3
SIGS = ("fL", "fR", "eL", "eR")

GAINS = [(.1, "01"), (.25, "025"), (.5, "05")]
DELAYS = [(2, "02"), (5, "05"), (10, "10"), (20, "20")]
SIGNS = [(1.0, "p"), (-1.0, "m")]
OPEN = "hynohop"
ARMS = [OPEN] + [f"g{gi}_d{di}_{si}"
                 for _, gi in GAINS for _, di in DELAYS for _, si in SIGNS]
CFG = {f"g{gi}_d{di}_{si}": dict(gfb=g, delay=dl, sign=sg)
       for g, gi in GAINS for dl, di in DELAYS for sg, si in SIGNS}
assert OPEN not in CFG and len(ARMS) == 25
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l63 verbatim) ----------
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
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in ("fL", "fR", "eL", "eR")])
assert len(ANTAG) > 0
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} | antag {len(ANTAG)}"
    f" | {time.time()-t0:.0f}s")

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- AMPA table: base chop 500-on/400-off (l63 BASE family) ----------
AMPA = np.zeros(WIN, np.float64)
for seg0, _, f in SEGB:
    if f != 0.7:
        AMPA[seg0:seg0 + SEG] = ENT_AMP      # fast seg continuous
        continue
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
seg = AMPA[:2000]
assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
assert (seg[1800:2000] == ENT_AMP).all()
DRIVE_ON = int((AMPA > 0).sum()) + SETTLE
log(f"drive-on {DRIVE_ON/100:.0f}s | arms {len(ARMS)}")


def off_intervals(ampa):
    segs = [(0, 2000), (4000, 6000)]
    out = []
    for lo, hi in segs:
        z = ampa[lo:hi] == 0
        k = 0
        while k < len(z):
            if z[k]:
                j = k
                while j < len(z) and z[j]:
                    j += 1
                if j - k >= 400:
                    out.append((lo + k, lo + j))
                k = j
            else:
                k += 1
    return out


OFFS = off_intervals(AMPA)
assert OFFS == [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)], OFFS


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
    return float(f_hat)


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


# ---------- rollouts ----------
res = {}
for seed in SEEDS:
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
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    mA = {a: np.zeros(WIN, np.float32) for a in ARMS}

    def step_all(k):
        global settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        ph_k = PHI[k] if k >= 0 else None
        if k < 0:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
        sin_ph = math.sin(ph_k)
        amp_k = ENT_AMP if k < 0 else float(AMPA[k])
        sin_term = amp_k * (0.5 + 0.5 * sin_ph)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + sin_term
            if a in CFG and k >= CFG[a]["delay"]:
                drive[mech, 0] += CFG[a]["gfb"] * CFG[a]["sign"] \
                    * float(mA[a][k - CFG[a]["delay"]])
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
            if a in CFG:
                mA[a][i] = X[a][ANTAG].mean()
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean())
                              for a in ARMS}, mm=mm, tr=tr)
    # incremental checkpoint (L45a rule): crash costs <= 1 seed
    np.savez_compressed(
        "l64/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l64/raw_l64.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS})

# ---------------- anchors (enumerated keys ONLY) ----------------
z55 = np.load("l55/raw_l55.npz")
z63 = np.load("l63/raw_l63.npz")
c0 = {}
for s in SEEDS:
    c0[f"open_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"][OPEN] - z55[f"mm_hynohop_{s}"][:WIN]).max())
    for c in SIGS:
        c0[f"open_{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"][OPEN][c] - z55[f"{c}_hynohop_{s}"][:WIN]).max())
c0x = {}
for s in SEEDS:
    c0x[f"g05d10_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["g05_d10_p"] - z63[f"mm_fbh_{s}"][:WIN]).max())
    for c in SIGS:
        c0x[f"g05d10_{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["g05_d10_p"][c] - z63[f"{c}_fbh_{s}"][:WIN]).max())
c0p, first_div = {}, {}
for a in ARMS[1:]:
    dl = CFG[a]["delay"]
    for s in SEEDS:
        m = res[str(s)]
        pre = max(float(np.abs(m["mm"][a][:dl] - m["mm"][OPEN][:dl]).max()),
                  max(float(np.abs(m["tr"][a][c][:dl] - m["tr"][OPEN][c][:dl]).max())
                      for c in SIGS))
        c0p[f"{a}_pre{s}"] = pre
        diffs = np.concatenate(
            [np.abs(m["mm"][a] - m["mm"][OPEN]),
             np.abs(m["tr"][a]["fL"] - m["tr"][OPEN]["fL"]),
             np.abs(m["tr"][a]["fR"] - m["tr"][OPEN]["fR"]),
             np.abs(m["tr"][a]["eL"] - m["tr"][OPEN]["eL"]),
             np.abs(m["tr"][a]["eR"] - m["tr"][OPEN]["eR"])])
        nz_ = np.maximum(diffs > 0, 0)
        fd = int(np.argmax(nz_)) if nz_.any() else -1
        first_div[f"{a}_{s}"] = fd % WIN if fd >= 0 else -1  # step index
c2 = {a: max(float(np.abs(res[str(s)]["mm"][a]
                          - res[str(s)]["mm"][OPEN]).max()) for s in SEEDS)
      for a in ARMS[1:]}
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
c0_pass = all(v == 0.0 for v in c0.values())
c0x_pass = all(v == 0.0 for v in c0x.values())
c0p_pass = all(v == 0.0 for v in c0p.values())
log(f"C0 pass {c0_pass} (18th chain) | C0x l63-fbh pass {c0x_pass} "
    f"| C0P pass {c0p_pass} | C1 {c1}")

# ---------------- analysis ----------------
TS = np.arange(499, WIN, 10)
TS3 = np.arange(299, WIN, 10)


def s_arrays(a, s, w=300):
    fL, fR, eL, eR = (res[s]["tr"][a][c] for c in SIGS)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    grid, off = (TS3, 299) if w == 300 else (TS, 499)
    for t in grid:
        SL[t] = S_of(fL[t - off:t + 1], eL[t - off:t + 1])
        SR[t] = S_of(fR[t - off:t + 1], eR[t - off:t + 1])
    return SL, SR


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    return round(float(np.nanmedian(arr[TS[q]])), 3) if q.any() else None


def seg_rows(a, s):
    SL, SR = s_arrays(a, s, w=500)
    rows = []
    for a0_, b0, tg in SEGB:
        lo, hi = a0_ + MEAS0, b0
        q = (TS >= lo) & (TS < hi)
        both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
        bl_errs = []
        for b in range(WIN // BLK):
            if a0_ <= b * BLK < b0 and b * BLK > a0_:
                f_hat = dom_freq(res[s]["mm"][a][b * BLK:(b + 1) * BLK])
                bl_errs.append(abs(f_hat - tg))
        rows.append(dict(duty=round(float(np.nanmean(both)), 3),
                         SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                         err=round(float(np.mean(bl_errs)), 4)))
    return rows


def duty_off(a, s):
    SL, SR = s_arrays(a, s, w=300)
    hits, sls, srs, npts = [], [], [], 0
    for lo, hi in OFFS:
        q = (TS3 >= lo + 299) & (TS3 < hi)
        pts = TS3[q]
        npts += len(pts)
        hits.extend([(SL[t] >= 0.25) & (SR[t] >= 0.25) for t in pts])
        sls.extend([SL[t] for t in pts])
        srs.extend([SR[t] for t in pts])
    hits = np.array(hits, float)
    return dict(duty=round(float(np.nanmean(hits)), 3),
                SL=round(float(np.nanmean(sls)), 3),
                SR=round(float(np.nanmean(srs)), 3), n=npts)


def off_amp(a, s):
    m = (res[s]["tr"][a]["fL"] + res[s]["tr"][a]["fR"]
         + res[s]["tr"][a]["eL"] + res[s]["tr"][a]["eR"]) / 4.0
    return round(float(np.mean([m[lo:hi].std() for lo, hi in OFFS])), 4)


cells = {}
for a in ARMS:
    for s in SEEDS:
        cells[(a, str(s))] = dict(segs=seg_rows(a, str(s)),
                                  off=duty_off(a, str(s)),
                                  off_amp=off_amp(a, str(s)))
log(f"analysis done {time.time()-t0:.0f}s")


def arr(a, key, sub=None):
    if sub is None:
        return np.array([cells[(a, str(s))][key] for s in SEEDS], float)
    return np.array([cells[(a, str(s))][key][sub] for s in SEEDS], float)


grid = {}
open_off = arr(OPEN, "off", "duty")
open_e2 = np.array([cells[(OPEN, str(s))]["segs"][1]["err"] for s in SEEDS])
open_e2_med = float(np.median(open_e2))
for a in ARMS[1:]:
    g = CFG[a]
    off = arr(a, "off", "duty")
    e2 = np.array([cells[(a, str(s))]["segs"][1]["err"] for s in SEEDS])
    s2d = np.array([cells[(a, str(s))]["segs"][1]["duty"] for s in SEEDS])
    lift = off - open_off
    lands = c2[a] > 1e-3
    floor_buried = (not lands) and g["sign"] < 0
    p1 = bool(lift.mean() >= 0.10
              and float(np.median(e2)) <= max(0.01, 2 * open_e2_med)
              and float(e2.max()) <= 0.5)
    grid[a] = dict(gfb=g["gfb"], delay=g["delay"], sign=g["sign"],
                   off=[round(float(v), 3) for v in off],
                   lift_mean=round(float(lift.mean()), 3),
                   e2=[round(float(v), 4) for v in e2],
                   e2_med=round(float(np.median(e2)), 4),
                   cat=bool(e2.max() > 0.5),
                   s2_duty=[round(float(v), 3) for v in s2d],
                   SL=round(float(np.nanmean(arr(a, "off", "SL"))), 3),
                   SR=round(float(np.nanmean(arr(a, "off", "SR"))), 3),
                   off_amp=round(float(arr(a, "off_amp").mean()), 4),
                   dm=round(c2[a], 5), lands=bool(lands),
                   floor_buried=bool(floor_buried), pass_P1=p1)

open_amp = round(float(arr(OPEN, "off_amp").mean()), 4)
winners = [a for a in grid if grid[a]["pass_P1"]]
# P3 phase read: positive-sign lift by delay (mean over gains)
p3 = {f"pos_d{di}": round(float(np.mean(
    [grid[f"g{gi}_d{di}_p"]["lift_mean"] for _, gi in GAINS])), 3)
    for _, di in DELAYS}
p3.update({f"neg_d{di}": dict(lift=round(float(np.mean(
    [grid[f"g{gi}_d{di}_m"]["lift_mean"] for _, gi in GAINS])), 3),
    dm_min=round(min(grid[f"g{gi}_d{di}_m"]["dm"] for _, gi in GAINS), 5),
    n_floor=int(sum(grid[f"g{gi}_d{di}_m"]["floor_buried"] for _, gi in GAINS)))
    for _, di in DELAYS})

out = dict(arms=ARMS, seeds=SEEDS, open=dict(off=[round(float(v), 3) for v in open_off],
        e2=[round(float(v), 4) for v in open_e2], e2_med=round(open_e2_med, 4),
        s2_duty=[round(float(v), 3) for v in
                 np.array([cells[(OPEN, str(s))]["segs"][1]["duty"] for s in SEEDS])],
        SL=round(float(np.nanmean(arr(OPEN, "off", "SL"))), 3),
        SR=round(float(np.nanmean(arr(OPEN, "off", "SR"))), 3),
        off_amp=open_amp),
    anchors=dict(c0_n=len(c0), c0_pass=c0_pass, c0x_n=len(c0x), c0x_pass=c0x_pass,
                 c0p_n=len(c0p), c0p_pass=c0p_pass, c0p_max=max(c0p.values()),
                 c1=bool(c1)),
    grid=grid, winners=winners,
    P2_closed=bool(not winners),
    P3=p3,
    first_div={k: int(v) for k, v in first_div.items()},
    dm={a: round(c2[a], 5) for a in ARMS[1:]})
with open("l64/results.json", "w") as f:
    json.dump(out, f, indent=1)
log(f"P1 winners {winners} | P2 closed {out['P2_closed']}")
log(f"open off-duty {[round(float(v),3) for v in open_off]} mean "
    f"{open_off.mean():.3f} | e2_med {open_e2_med:.4f}")
for _, di in DELAYS:
    for si in ("p", "m"):
        for _, gi in GAINS:
            a = f"g{gi}_d{di}_{si}"
            g = grid[a]
            log(f"{a}: lift {g['lift_mean']:+.3f} e2 {g['e2_med']:.3f}"
                f" dm {g['dm']:.4f}{' FLOOR' if g['floor_buried'] else ''}"
                f"{' LANDS-NOT' if not g['lands'] and not g['floor_buried'] else ''}")
log(f"done {time.time()-t0:.0f}s")
