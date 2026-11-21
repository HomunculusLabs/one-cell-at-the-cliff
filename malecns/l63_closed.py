"""L63 slice A: closed-loop-cord (LANE.md ideas-30).

Delayed attenuated antagonist-motor-mass feedback onto vnc_sensory mechano
(body-level, L12 form) vs open-loop, on the l55/l59 hybrid-no-hop schedule +
a long-gap (500-on/700-off) variant. Registered outcomes in l63/PREREG.md.
Machinery l59_ensemble.py verbatim; CPU-only; P1-labeled; no live changes.
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
SEEDS8 = [11, 22, 33, 101, 105, 109, 111, 113]
ANCHOR_SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05
ENT_AMP = 0.3
LOCK_TOL = 0.10
GFB, DELAY = 0.5, 10
SIGS = ("fL", "fR", "eL", "eR")
BASE = ["hynohop", "fbh", "sham"]
LONG = ["openL", "fbL"]
ARMS = BASE + LONG
FB_SELF = {"fbh", "fbL"}
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

# ---------- AMPA tables: base (500/400) + long (500/700) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
for fam, cycle in ((BASE, 900), (LONG, 1200)):
    for a in fam:
        for seg0, _, f in SEGB:
            if f != 0.7:
                AMPA[a][seg0:seg0 + SEG] = ENT_AMP      # fast seg continuous
                continue
            c = 0
            while seg0 + c * cycle < seg0 + SEG:
                lo = seg0 + c * cycle
                AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
                c += 1
for a in BASE:
    assert np.array_equal(AMPA[a], AMPA["hynohop"])
for a in LONG:
    assert np.array_equal(AMPA[a], AMPA["openL"])
seg = AMPA["hynohop"][:2000]
assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
assert (seg[1800:2000] == ENT_AMP).all()
segl = AMPA["openL"][:2000]
assert (segl[:500] == ENT_AMP).all() and (segl[500:1200] == 0).all()
assert (segl[1200:1700] == ENT_AMP).all() and (segl[1700:2000] == 0).all()
assert np.array_equal(AMPA["hynohop"][2000:4000], AMPA["openL"][2000:4000])
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
log("drive-on " + " ".join(f"{a}:{DRIVE_ON[a]/100:.0f}s" for a in ARMS))


def off_intervals(ampa):
    """Maximal >=400-step zero runs inside the two 0.7 Hz segs."""
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


OFFS = {"base": off_intervals(AMPA["hynohop"]), "long": off_intervals(AMPA["openL"])}
assert OFFS["base"] == [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)], OFFS
assert OFFS["long"] == [(500, 1200), (4500, 5200)], OFFS  # 300-step tail gaps <400 excluded
log(f"offs base 4x400 | long 4x700: {OFFS['long']}")

# ---------- sham donor traces (l59 stored raw, open hynohop) ----------
z59 = np.load("l59/raw_l59.npz")
DONOR = {s: SEEDS8[(SEEDS8.index(s) + 1) % len(SEEDS8)] for s in SEEDS8}
DONOR_M = {}
for s in SEEDS8:
    d = DONOR[s]
    DONOR_M[s] = ((z59[f"fL_hynohop_{d}"] + z59[f"fR_hynohop_{d}"]
                   + z59[f"eL_hynohop_{d}"] + z59[f"eR_hynohop_{d}"]) / 4.0
                  ).astype(np.float32)
    assert len(DONOR_M[s]) == WIN
log("donors wired " + " ".join(f"{s}<-{DONOR[s]}" for s in SEEDS8))


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
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    mB = np.zeros(WIN, np.float32)        # fbh own antagonist mass
    mL = np.zeros(WIN, np.float32)        # fbL own antagonist mass
    fb_mag = np.zeros(WIN, np.float32)    # |fb| applied by fbh (diagnostic)
    don = DONOR_M[seed]

    def step_all(k):
        nonlocal settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        ph_k = PHI[k] if k >= 0 else None
        if k < 0:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
        sin_ph = math.sin(ph_k)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            amp_k = ENT_AMP if k < 0 else float(AMPA[a][k])
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            if k >= DELAY:
                if a in FB_SELF:
                    sig = mB[k - DELAY] if a == "fbh" else mL[k - DELAY]
                    drive[mech, 0] += GFB * float(sig)
                elif a == "sham":
                    drive[mech, 0] += GFB * float(don[k - DELAY])
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
        mB[i] = X["fbh"][ANTAG].mean()
        mL[i] = X["fbL"][ANTAG].mean()
        fb_mag[i] = GFB * (mB[i - DELAY] if i >= DELAY else 0.0)
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                mm=mm, tr=tr, mB=mB, mL=mL, fb_mag=fb_mag)


res = {str(s): run_seed(s) for s in SEEDS8}
log(f"runs done {time.time()-t0:.0f}s")

# raw checkpoint BEFORE analysis (L45a lesson)
np.savez_compressed(
    "l63/raw_l63.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS8},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS8 for c in SIGS},
    **{f"mB_{s}": res[str(s)]["mB"] for s in SEEDS8})

# ---------------- anchors (enumerated keys ONLY; diagnostics separate) ----------------
z55 = np.load("l55/raw_l55.npz")
c0 = {}
for s in ANCHOR_SEEDS:
    c0[f"hynohop_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hynohop"] - z55[f"mm_hynohop_{s}"][:WIN]).max())
    for c in SIGS:
        c0[f"hynohop_{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hynohop"][c] - z55[f"{c}_hynohop_{s}"][:WIN]).max())
c0L = {}
for s in ANCHOR_SEEDS:
    c0L[f"openL_mm_{s}_lt900"] = float(np.abs(
        res[str(s)]["mm"]["openL"][:900] - z55[f"mm_hynohop_{s}"][:900]).max())
    for c in SIGS:
        c0L[f"openL_{c}_{s}_lt900"] = float(np.abs(
            res[str(s)]["tr"]["openL"][c][:900]
            - z55[f"{c}_hynohop_{s}"][:900]).max())
c0P = {}
for a in ("fbh", "sham"):
    c0P[f"{a}_mm_ltDELAY"] = max(
        float(np.abs(res[str(s)]["mm"][a][:DELAY]
                     - res[str(s)]["mm"]["hynohop"][:DELAY]).max()) for s in SEEDS8)
c2 = max(float(np.abs(res[str(s)]["mm"]["fbh"]
                      - res[str(s)]["mm"]["hynohop"]).max()) for s in SEEDS8)
c1 = dict(af_ok=all(0.01 < res[str(s)]["af"][a] < 0.9
                    for s in SEEDS8 for a in ARMS))
c0_pass = all(v == 0.0 for v in c0.values())
c0L_pass = all(v == 0.0 for v in c0L.values())
c0P_pass = all(v == 0.0 for v in c0P.values())
c2_pass = c2 > 1e-3
log(f"C0 pass {c0_pass} | C0L pass {c0L_pass} | C0P pass {c0P_pass} "
    f"| C2 fb-lands {c2_pass} ({c2:.4f}) | C1 {c1['af_ok']}")

# ---------------- analysis ----------------
TS = np.arange(499, WIN, 10)
TS3 = np.arange(299, WIN, 10)
SM = {}
SM3 = {}


def s_arrays(a, s, w=500):
    store = SM if w == 500 else SM3
    if (a, s, w) in store:
        return store[(a, s, w)]
    fL, fR, eL, eR = (res[s]["tr"][a][c] for c in SIGS)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    grid, off = (TS, 499) if w == 500 else (TS3, 299)
    for t in grid:
        SL[t] = S_of(fL[t - off:t + 1], eL[t - off:t + 1])
        SR[t] = S_of(fR[t - off:t + 1], eR[t - off:t + 1])
    store[(a, s, w)] = (SL, SR)
    return SL, SR


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    return round(float(np.nanmedian(arr[TS[q]])), 3) if q.any() else None


def seg_rows(a, s):
    SL, SR = s_arrays(a, s)
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


def duty_off(a, s, fam):
    SL, SR = s_arrays(a, s, w=300)
    hits, sls, srs, npts = [], [], [], 0
    for lo, hi in OFFS[fam]:
        q = (TS3 >= lo + 299) & (TS3 < hi)
        pts = TS3[q]
        npts += len(pts)
        hits.extend([(SL[t] >= 0.25) & (SR[t] >= 0.25) for t in pts])
        sls.extend([SL[t] for t in pts])
        srs.extend([SR[t] for t in pts])
    hits = np.array(hits, float)
    return dict(duty=round(float(np.nanmean(hits)), 3) if npts else None,
                SL=round(float(np.nanmean(sls)), 3) if npts else None,
                SR=round(float(np.nanmean(srs)), 3) if npts else None,
                n=npts)


def off_amp(a, s, fam):
    m = (res[s]["tr"][a]["fL"] + res[s]["tr"][a]["fR"]
         + res[s]["tr"][a]["eL"] + res[s]["tr"][a]["eR"]) / 4.0
    return round(float(np.mean([m[lo:hi].std() for lo, hi in OFFS[fam]])), 4)


cells = {}
for a in ARMS:
    fam = "base" if a in BASE else "long"
    for s in SEEDS8:
        cells[(a, s)] = dict(segs=seg_rows(a, str(s)),
                             off=duty_off(a, str(s), fam),
                             off_amp=off_amp(a, str(s), fam))


def arr(a, key, sub=None):
    if sub is None:
        return np.array([cells[(a, s)][key] for s in SEEDS8], float)
    return np.array([cells[(a, s)][key][sub] for s in SEEDS8], float)


def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


duty_off = {a: arr(a, "off", "duty") for a in ARMS}
seg2_duty = {a: np.array([cells[(a, s)]["segs"][1]["duty"] for s in SEEDS8])
             for a in ARMS}
seg_err = {a: np.array([np.mean([r["err"] for r in cells[(a, s)]["segs"]])
                        for s in SEEDS8]) for a in ARMS}
lift_f = duty_off["fbh"] - duty_off["hynohop"]
lift_s = duty_off["sham"] - duty_off["hynohop"]
lift_L = duty_off["fbL"] - duty_off["openL"]
s2_f = seg2_duty["fbh"] - seg2_duty["hynohop"]
s2_s = seg2_duty["sham"] - seg2_duty["hynohop"]
k_f = int((duty_off["fbh"] >= .5).sum())
k_o = int((duty_off["hynohop"] >= .5).sum())

out = dict(
    arms=ARMS, seeds=SEEDS8, GFB=GFB, DELAY=DELAY,
    anchors=dict(c0={k: v for k, v in c0.items()}, c0_pass=c0_pass,
                 c0L_max=max(c0L.values()), c0L_pass=c0L_pass,
                 c0P=c0P, c0P_pass=c0P_pass, c2_fb_lands=c2, c2_pass=c2_pass,
                 c1=c1),
    P1=dict(duty_off={a: [round(float(v), 3) for v in duty_off[a]]
                      for a in ("hynohop", "fbh", "sham")},
            lift_fb=[round(float(v), 3) for v in lift_f],
            lift_fb_mean=round(float(lift_f.mean()), 3),
            lift_sham_mean=round(float(lift_s.mean()), 3),
            pass_P1=bool(lift_f.mean() >= 0.10
                         and lift_s.mean() < 0.5 * lift_f.mean()),
            p_ge_half=dict(fb=k_f, wilson_fb=wilson(k_f, 8),
                           open=k_o, wilson_open=wilson(k_o, 8))),
    P1L=dict(duty_off=dict(openL=[round(float(v), 3) for v in duty_off["openL"]],
                           fbL=[round(float(v), 3) for v in duty_off["fbL"]]),
             lift_mean=round(float(lift_L.mean()), 3),
             err_openL_med=round(float(np.median(
                 [np.mean([r['err'] for r in cells[('openL', s)]['segs']])
                  for s in SEEDS8])), 4),
             err_fbL_med=round(float(np.median(
                 [np.mean([r['err'] for r in cells[('fbL', s)]['segs']])
                  for s in SEEDS8])), 4),
             pass_P1L=bool(lift_L.mean() >= 0.10)),
    P2=dict(err_mean={a: [round(float(v), 4) for v in seg_err[a]]
                      for a in ("hynohop", "fbh", "sham")},
            err_fbh_med=round(float(np.median(seg_err["fbh"])), 4),
            err_hyn_med=round(float(np.median(seg_err["hynohop"])), 4)),
    P3=dict(seg2_duty={a: [round(float(v), 3) for v in seg2_duty[a]]
                       for a in ("hynohop", "fbh", "sham")},
            lift_fb_mean=round(float(s2_f.mean()), 3),
            lift_sham_mean=round(float(s2_s.mean()), 3),
            pass_P3=bool(s2_f.mean() >= 0.10
                         and s2_s.mean() < s2_f.mean())),
    sec=dict(off_amp={a: round(float(arr(a, "off_amp").mean()), 4) for a in ARMS},
             off_SL={a: round(float(np.nanmean(arr(a, "off", "SL"))), 3)
                     for a in ARMS},
             off_SR={a: round(float(np.nanmean(arr(a, "off", "SR"))), 3)
                     for a in ARMS},
             fb_share_of_on=round(float(np.mean(
                 [np.mean(res[str(s)]["fb_mag"][(AMPA["hynohop"] > 0)]) for s in SEEDS8]
             ) / ENT_AMP), 3),
             fb_mean_off=round(float(np.mean(
                 [np.mean(res[str(s)]["fb_mag"][(AMPA["hynohop"][:WIN] == 0)])
                  for s in SEEDS8])), 4)),
    segs={f"{a}_{s}": cells[(a, s)]["segs"] for a in ARMS for s in SEEDS8},
)
out["P2"]["pass_P2"] = bool(np.median(seg_err["fbh"])
                            <= max(0.01, 2 * np.median(seg_err["hynohop"])))
with open("l63/results.json", "w") as f:
    json.dump(out, f, indent=1)
log(f"P1 pass {out['P1']['pass_P1']} (fb lift {out['P1']['lift_fb_mean']} vs sham "
    f"{out['P1']['lift_sham_mean']}) | P1L pass {out['P1L']['pass_P1L']} "
    f"(lift {out['P1L']['lift_mean']}) | P2 pass {out['P2']['pass_P2']} "
    f"(err fb {out['P2']['err_fbh_med']} vs open {out['P2']['err_hyn_med']}) "
    f"| P3 pass {out['P3']['pass_P3']} (seg2 lift {out['P3']['lift_fb_mean']} "
    f"vs sham {out['P3']['lift_sham_mean']})")
log(f"done {time.time()-t0:.0f}s")
