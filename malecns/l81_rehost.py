"""L81: reflex-arc re-host (LANE.md ideas-40). PREREG l81/PREREG.md FIRST.

l79 machinery verbatim; the off-gap is replaced by a STRONG sinusoidal
mechano volley at the 1.4 carrier (amp {2x,3x} entrain amp, [2500,2800)),
then back to continuous .3. Twinned vs l59 hynohop/hybrid on the shared
noise stream. CPU-only; raw npz checkpointed BEFORE analysis; no live
changes.
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
SEEDS = [11, 22, 33] + list(range(101, 114))   # l45b census grid, n=16
ANCHOR_SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
HOP_AMP, HOP_VW = 0.5, 40
TRANS = [2000, 4000]
LOCK_TOL = 0.10
VOL0, VOL1 = 2500, 2800            # the volley window (3 s at the step)
DOSE = {"rehost2x": 2.0, "rehost3x": 3.0, "hyrehost2x": 2.0, "hyrehost3x": 3.0}
ARMS = ["hynohop", "hybrid", "rehost2x", "rehost3x", "hyrehost2x", "hyrehost3x"]
TWINS = {"rehost2x": "hynohop", "rehost3x": "hynohop",
         "hyrehost2x": "hybrid", "hyrehost3x": "hybrid"}
SIGS = ("fL", "fR", "eL", "eR")
W_EARLY = (2500, 3200)             # EXPOSURE (contains the volley)
W_POST = (3200, 4000)              # PRIMARY: fully inside resumed drive
W_SPLIT = (3600, 4000)             # late half of W_post
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l59/l66/l77/l79 verbatim) ----------
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
hopL = np.where((ltyp == "DNge046") & (lside == "L"))[0]
assert len(hopL) == 2, len(hopL)
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)}"
    f" | {time.time()-t0:.0f}s")

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- per-arm AMPA / HOPA tables (write-time asserts) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
for a in ARMS:                                  # base table for every arm
    for seg0, _, _ in SEGB:
        c = 0                                   # 500-on/400-off per 0.7 seg
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA[a][2000:4000] = ENT_AMP                # fast segment CONTINUOUS
for a, mult in DOSE.items():                    # THE reflex-arc volley
    AMPA[a][VOL0:VOL1] = ENT_AMP * mult

HOPA = {a: np.zeros(WIN, bool) for a in ARMS}
for o in TRANS:
    HOPA["hybrid"][o:o + HOP_VW] = True
    for a in DOSE:
        if TWINS[a] == "hybrid":
            HOPA[a][o:o + HOP_VW] = True        # same volleys for the twin

for va, tw in TWINS.items():
    m = np.ones(WIN, bool)
    m[VOL0:VOL1] = False
    assert np.array_equal(AMPA[va][m], AMPA[tw][m])          # prefix+suffix parity
    assert (AMPA[va][VOL0:VOL1] == ENT_AMP * DOSE[va]).all()
    assert (AMPA[tw][VOL0:VOL1] == ENT_AMP).all()
    if tw == "hybrid":
        assert np.array_equal(HOPA[va], HOPA["hybrid"])
    else:
        assert not HOPA[va].any()
assert all(np.array_equal(AMPA[a], AMPA["hynohop"])
           for a in ("hynohop", "hybrid"))
# 1x parity control: registered NO-OP, proven at table level, not rolled out
ampe1x = AMPA["hynohop"].copy()
ampe1x[VOL0:VOL1] = ENT_AMP * 1.0
assert np.array_equal(ampe1x, AMPA["hynohop"])
for seg0, segend, f in SEGB:
    seg = AMPA["hynohop"][seg0:seg0 + SEG]
    if f == 0.7:
        assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
        assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
        assert (seg[1800:2000] == ENT_AMP).all()
    else:
        assert (AMPA["hynohop"][seg0:segend] == ENT_AMP).all()
assert not HOPA["hynohop"].any() and not HOPA["rehost2x"].any()
assert HOPA["hybrid"].sum() == 2 * HOP_VW
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
assert all(DRIVE_ON[a] == 4800 for a in ARMS), DRIVE_ON     # no off-steps added
log("drive-on 48.0s every arm (volley adds MASS not off-steps) | tables asserted")


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


# ---------- rollouts (l59 step loop verbatim; no FB) ----------
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

    def step_all(k):
        global settle_ph
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
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                          mm=mm, tr=tr)
    np.savez_compressed(
        "l81/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l81/raw_l81.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS})
log("raw_l81.npz checkpointed BEFORE analysis (crash => verdict re-derives)")

# ---------------- anchors (enumerated keys ONLY) ----------------
z59 = np.load("l59/raw_l59.npz")
c0a, c0b = {}, {}
for s in ANCHOR_SEEDS:
    c0a[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hynohop"] - z59[f"mm_hynohop_{s}"][:WIN]).max())
    c0b[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hybrid"] - z59[f"mm_hybrid_{s}"][:WIN]).max())
    for c in SIGS:
        c0a[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hynohop"][c] - z59[f"{c}_hynohop_{s}"][:WIN]).max())
        c0b[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hybrid"][c] - z59[f"{c}_hybrid_{s}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())
c0b_pass = all(v == 0.0 for v in c0b.values())

c0p1, c0p2, dm = {}, {}, {}
for va in TWINS:
    tw = TWINS[va]
    for s in SEEDS:
        m = res[str(s)]
        pre = [np.abs(m["mm"][va][:VOL0] - m["mm"][tw][:VOL0])]
        pre += [np.abs(m["tr"][va][c][:VOL0] - m["tr"][tw][c][:VOL0]) for c in SIGS]
        c0p1[f"{va}_{s}"] = float(np.concatenate(pre).max())
        diffs = np.concatenate(
            [np.abs(m["mm"][va] - m["mm"][tw])]
            + [np.abs(m["tr"][va][c] - m["tr"][tw][c]) for c in SIGS])
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        c0p2[f"{va}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{va}_{s}"] = round(float(diffs.max()), 5)
wired_dead = [k for k, v in dm.items() if v == 0.0]
c0p1_pass = all(v == 0.0 for v in c0p1.values())
c0p2_pass = (not wired_dead
             and all(v in (VOL0, VOL0 + 1) for v in c0p2.values()))
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
log(f"C0a {c0a_pass} | C0b {c0b_pass} | C0P-1 {c0p1_pass} | C0P-2 {c0p2_pass}"
    f" | C1 {c1} | wired_dead {len(wired_dead)}"
    f" | first_div counts {dict((v, list(c0p2.values()).count(v)) for v in set(c0p2.values()))}")

# ---------------- S arrays + window rows (l79 verbatim) ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    fL, fR, eL, eR = (res[s]["tr"][a][c] for c in SIGS)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    SM[(a, s)] = (SL, SR)
    return SL, SR


def win_rows(a, s):
    SL, SR = s_arrays(a, str(s))
    out = {}
    for name, (lo, hi) in (("wearly", W_EARLY), ("wpost", W_POST),
                           ("wpost_late", (W_SPLIT[0], W_SPLIT[1]))):
        q = (TS >= lo) & (TS < hi)
        both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
        out[name] = dict(
            duty=round(float(np.nanmean(both)), 3),
            SL=round(float(np.nanmedian(SL[TS[q]])), 3),
            SR=round(float(np.nanmedian(SR[TS[q]])), 3))
    return out


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
            f_seg = dom_freq(res[str(s)]["mm"][a][a0_:b0])
            bl_errs, ttl = [], None
            for b in range(WIN // BLK):
                if a0_ <= b * BLK < b0 and b * BLK > a0_:
                    f_hat = dom_freq(res[str(s)]["mm"][a][b * BLK:(b + 1) * BLK])
                    e = abs(f_hat - tg)
                    bl_errs.append(e)
                    if ttl is None and e <= LOCK_TOL:
                        ttl = b * BLK - a0_
            rows.append(dict(
                duty=round(float(np.nanmean(both)), 3),
                SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                f=round(f_seg, 3),
                err=round(float(np.mean(bl_errs)), 4), ttl=ttl))
        # post-volley lock: blocks fully inside resumed drive [2800,4000)
        post_errs = []
        for b0 in (3000, 3500):
            f_hat = dom_freq(res[str(s)]["mm"][a][b0:b0 + BLK])
            post_errs.append(abs(f_hat - 1.4))
        f_strad = dom_freq(res[str(s)]["mm"][a][2500:3000])   # contains volley
        cells[a][str(s)] = dict(
            segs=rows, **win_rows(a, s),
            lock_post=round(float(np.mean(post_errs)), 4),
            lock_straddle=round(abs(f_strad - 1.4), 4))
        cells[a][str(s)]["seg1"] = rows[1]["duty"]

for a in ARMS:                                  # pooled duty_all (diagnostic only)
    for s in SEEDS:
        SL, SR = s_arrays(a, str(s))
        qa = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            qa |= (TS >= a0_ + MEAS0) & (TS < b0)
        both = (SL[TS[qa]] >= 0.25) & (SR[TS[qa]] >= 0.25)
        cells[a][str(s)]["duty_all"] = round(float(np.nanmean(both)), 3)


# ---------------- registered reads ----------------
def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


def dist_of(a, key, sub=None):
    v = np.array([cells[a][str(s)][key] if sub is None
                  else cells[a][str(s)][key][sub] for s in SEEDS])
    return dict(vals=[round(float(x), 3) for x in v],
                mean=round(float(v.mean()), 3),
                med=round(float(np.median(v)), 3),
                mn=round(float(v.min()), 3))


p1 = {}
for va in TWINS:
    tw = TWINS[va]
    d_early = np.array([cells[va][str(s)]["wearly"]["duty"]
                        - cells[tw][str(s)]["wearly"]["duty"] for s in SEEDS])
    d_post = np.array([cells[va][str(s)]["wpost"]["duty"]
                       - cells[tw][str(s)]["wpost"]["duty"] for s in SEEDS])
    d_late = np.array([cells[va][str(s)]["wpost_late"]["duty"]
                       - cells[tw][str(s)]["wpost_late"]["duty"] for s in SEEDS])
    kp = int((np.array([cells[va][str(s)]["wpost"]["duty"] for s in SEEDS]) >= .25).sum())
    kt = int((np.array([cells[tw][str(s)]["wpost"]["duty"] for s in SEEDS]) >= .25).sum())
    mean_d = round(float(d_post.mean()), 3)
    n_up = int((d_post >= 0).sum())
    if mean_d >= .10 and n_up >= 11:
        verdict = "HELP"
    elif mean_d <= -.10 and int((d_post <= 0).sum()) >= 11:
        verdict = "HURT"
    else:
        verdict = "NULL/INCONCLUSIVE"
    p1[va] = dict(
        twin=tw,
        wpost_twin=dist_of(tw, "wpost", "duty"), wpost=dist_of(va, "wpost", "duty"),
        wearly_twin=dist_of(tw, "wearly", "duty"), wearly=dist_of(va, "wearly", "duty"),
        wpost_late_twin=dist_of(tw, "wpost_late", "duty"),
        wpost_late=dist_of(va, "wpost_late", "duty"),
        d_post=[round(float(x), 3) for x in d_post],
        d_early=[round(float(x), 3) for x in d_early],
        d_late=[round(float(x), 3) for x in d_late],
        d_post_mean=mean_d, d_post_up=n_up,
        d_early_mean=round(float(d_early.mean()), 3),
        d_late_mean=round(float(d_late.mean()), 3),
        k_post_ge25=kp, k_twin_ge25=kt,
        wilson_post=wilson(kp, len(SEEDS)), wilson_twin=wilson(kt, len(SEEDS)),
        verdict=verdict)

# P1b dose ordering (descriptive)
p1b = {}
for fam, (lo_, hi_) in {"nohop": ("rehost2x", "rehost3x"),
                        "hy": ("hyrehost2x", "hyrehost3x")}.items():
    dd = np.array([cells[hi_][str(s)]["wpost"]["duty"]
                   - cells[lo_][str(s)]["wpost"]["duty"] for s in SEEDS])
    p1b[fam] = dict(d30_minus_d20=[round(float(x), 3) for x in dd],
                    mean=round(float(dd.mean()), 3),
                    n_pos=int((dd > 0).sum()))

p2 = {}
for a in ARMS:
    errs = np.array([cells[a][str(s)]["lock_post"] for s in SEEDS])
    strad = np.array([cells[a][str(s)]["lock_straddle"] for s in SEEDS])
    p2[a] = dict(le01=int((errs <= .01).sum()), mean=round(float(errs.mean()), 4),
                 vals=[round(float(x), 4) for x in errs],
                 straddle_mean=round(float(strad.mean()), 4))

p4 = {}
for va in TWINS:
    sl = sr = bothb = 0
    miss = []
    for s in SEEDS:
        cell = cells[va][str(s)]
        if cell["wpost"]["duty"] >= .25:
            continue
        sl_low = cell["wpost"]["SL"] < .25
        sr_low = cell["wpost"]["SR"] < .25
        if sl_low and sr_low:
            bothb += 1
        elif sl_low:
            sl += 1
        elif sr_low:
            sr += 1
        miss.append(dict(seed=s, duty=cell["wpost"]["duty"],
                         SL=cell["wpost"]["SL"], SR=cell["wpost"]["SR"]))
    tot = sl + sr + bothb
    p4[va] = dict(n_miss=len(miss), sl_owned=sl, sr_owned=sr, both=bothb,
                  sl_share=round(sl / tot, 3) if tot else None, misses=miss)

# P5 budget: amp-weighted entrain mass (drive-on steps equal by design)
sin_tab = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in range(WIN)])
on_steps = {a: int((AMPA[a] > 0).sum()) for a in ARMS}
mass = {a: float((AMPA[a] * sin_tab).sum()) for a in ARMS}
base_mass = mass["hynohop"]
p5 = dict(drive_on_steps=on_steps,
          mass_ratio={a: round(mass[a] / base_mass, 4) for a in ARMS},
          volley_extra_steps=VOL1 - VOL0)

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, vol=[VOL0, VOL1], dose=DOSE,
                     windows=dict(wearly=W_EARLY, wpost=W_POST,
                                  wpost_late=W_SPLIT),
                     drive_on=DRIVE_ON, nodes=int(n), edges=len(gsrc)),
           anchors=dict(c0a_pass=c0a_pass, c0b_pass=c0b_pass,
                        c0p1_pass=c0p1_pass, c0p2_pass=bool(c0p2_pass),
                        c1=bool(c1), wired_dead=wired_dead,
                        first_div=c0p2, prefix_maxd=c0p1, dm=dm),
           p1=p1, p1b=p1b, p2=p2, p4=p4, p5=p5,
           seg1={a: dist_of(a, "seg1") for a in ARMS},
           cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS})
json.dump(out, open("l81/results_l81.json", "w"), indent=1)
log("P1 " + json.dumps({k: dict(verdict=v["verdict"],
                                d_post_mean=v["d_post_mean"],
                                d_early_mean=v["d_early_mean"],
                                d_late_mean=v["d_late_mean"],
                                k=v["k_post_ge25"], k_twin=v["k_twin_ge25"])
                        for k, v in p1.items()}))
log("P1b " + json.dumps(p1b))
log("P2 " + json.dumps(p2))
log("P4 " + json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "misses"}
                        for k, v in p4.items()}))
log(f"done {time.time()-t0:.0f}s -> l81/results_l81.json")
