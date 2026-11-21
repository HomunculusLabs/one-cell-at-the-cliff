"""L69: echo-side-dose-response (LANE.md ideas-34). PREREG l69/PREREG.md FIRST.

Machinery l67_sidesplit.py verbatim; open arm reused from l67/raw_l67.npz.
8 arms: ronly/lonly x gain {.05,.1,.2,.4}, sign -, delay 5, census n=16.
NEW amplitude-landing probe: mean antagonist pool activity over OFF-window
samples vs open, per arm (monotone in gain = the dose physically lands).
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
SEEDS = [11, 22, 33] + list(range(101, 114))   # l45b census grid, n=16
G, BETA, D = 0.01, 2.0, 0.05
ENT_AMP = 0.3
SIGS = ("fL", "fR", "eL", "eR")
SIGN, DELAY = -1.0, 5
GAINS = [0.05, 0.1, 0.2, 0.4]
ARMS = [f"{rt}_g{int(g*1000):03d}" for rt in ("ronly", "lonly") for g in GAINS]
ANCHOR_R = "ronly_g100"
ANCHOR_L = "lonly_g100"
GAIN_OF = {a: GAINS[i % 4] for i, a in enumerate(ARMS)}
ROUTE_OF = {a: a.split("_")[0] for a in ARMS}
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l67 verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()
rside_g = lab["rootSide"].astype(str).to_numpy()

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

lrside = rside_g[keep]
mechL = mech[lrside[mech] == "L"]
mechR = mech[lrside[mech] == "R"]
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in ("fL", "fR", "eL", "eR")])   # l66/l67 exact
ANTL = np.concatenate([PAIRS["Tr"]["fL"], PAIRS["Tr"]["eL"]])
ANTR = np.concatenate([PAIRS["Tr"]["fR"], PAIRS["Tr"]["eR"]])
assert np.array_equal(np.sort(np.concatenate([ANTL, ANTR])), np.sort(ANTAG))
assert len(mechL) > 0 and len(mechR) > 0
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} "
    f"(L {len(mechL)} R {len(mechR)}) | antag {len(ANTAG)} | {time.time()-t0:.0f}s")

# ---------- phase + base chop AMPA (l67 verbatim) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

AMPA = np.zeros(WIN, np.float64)
for seg0, _, f in SEGB:
    if f != 0.7:
        AMPA[seg0:seg0 + SEG] = ENT_AMP
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
OFFS = [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)]

# ---------- open arm reused from l67 stored ----------
z67 = np.load("l67/raw_l67.npz")
OPEN_MM = {s: z67[f"mm_hynohop_{s}"] for s in SEEDS}
OPEN_TR = {s: {c: z67[f"{c}_hynohop_{s}"] for c in SIGS} for s in SEEDS}
need = [f"mm_hynohop_{s}" for s in SEEDS] + [f"{c}_hynohop_{s}" for s in SEEDS for c in SIGS]
missing = [k for k in need if k not in set(z67.keys())]
assert not missing, missing[:4]


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


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


TS3 = np.arange(299, WIN, 10)


def off_ts():
    out = []
    for lo, hi in OFFS:
        out.extend(TS3[(TS3 >= lo + 299) & (TS3 < hi)])
    return np.array(out, int)


OFF_TS = off_ts()
# each off-window [lo+299, hi) holds 11 stride-10 samples (e.g. 799..899), 4 windows
assert len(OFF_TS) == 44, len(OFF_TS)


def duty_off(fL, fR, eL, eR):
    hits, sls, srs, hl, hr = [], [], [], [], []
    for lo, hi in OFFS:
        for t in TS3[(TS3 >= lo + 299) & (TS3 < hi)]:
            SL = S_of(fL[t - 299:t + 1], eL[t - 299:t + 1])
            SR = S_of(fR[t - 299:t + 1], eR[t - 299:t + 1])
            hits.append((SL >= 0.25) & (SR >= 0.25))
            hl.append(SL >= 0.25)
            hr.append(SR >= 0.25)
            sls.append(SL)
            srs.append(SR)
    return dict(duty=round(float(np.nanmean(np.array(hits, float))), 3),
                dutyL=round(float(np.nanmean(np.array(hl, float))), 3),
                dutyR=round(float(np.nanmean(np.array(hr, float))), 3),
                SL=round(float(np.nanmean(sls)), 3),
                SR=round(float(np.nanmean(srs)), 3))


def seg2(mm):
    errs = []
    for b in range(WIN // 500):
        if 2000 <= b * 500 < 4000 and b * 500 > 2000:
            errs.append(abs(dom_freq(mm[b * 500:(b + 1) * 500]) - 1.4))
    return round(float(np.mean(errs)), 4)


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
    mLp = {a: np.zeros(WIN, np.float32) for a in ARMS}
    mRp = {a: np.zeros(WIN, np.float32) for a in ARMS}

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
            if k >= DELAY:
                gfb = GAIN_OF[a]
                if ROUTE_OF[a] == "ronly":
                    drive[mechR, 0] += gfb * SIGN * float(mRp[a][k - DELAY])
                else:
                    drive[mechL, 0] += gfb * SIGN * float(mLp[a][k - DELAY])
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
            mLp[a][i] = X[a][ANTL].mean()
            mRp[a][i] = X[a][ANTR].mean()
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                          mm=mm, tr=tr)
    np.savez_compressed(
        "l69/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l69/raw_l69.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS},
    **{f"mm_hynohop_{s}": OPEN_MM[s] for s in SEEDS},
    **{f"{c}_hynohop_{s}": OPEN_TR[s][c] for s in SEEDS for c in SIGS})

# ---------------- anchors (enumerated keys ONLY) ----------------
c0 = {}
for s in SEEDS:
    c0[f"r_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"][ANCHOR_R] - z67[f"mm_ronly_{s}"][:WIN]).max())
    c0[f"l_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"][ANCHOR_L] - z67[f"mm_lonly_{s}"][:WIN]).max())
    for c in SIGS:
        c0[f"r_{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"][ANCHOR_R][c] - z67[f"{c}_ronly_{s}"][:WIN]).max())
        c0[f"l_{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"][ANCHOR_L][c] - z67[f"{c}_lonly_{s}"][:WIN]).max())
c0_pass = all(v == 0.0 for v in c0.values())

dm, first_div, prefix_ok = {}, {}, {}
for a in ARMS:
    for s in SEEDS:
        m = res[str(s)]
        diffs = np.concatenate(
            [np.abs(m["mm"][a] - OPEN_MM[s])]
            + [np.abs(m["tr"][a][c] - OPEN_TR[s][c]) for c in SIGS])
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        first_div[f"{a}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{a}_{s}"] = round(float(diffs.max()), 5)
        prefix_ok[f"{a}_{s}"] = bool(diffs[:DELAY + 1].max() == 0.0)
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
c0p_pass = all(first_div[f"{a}_{s}"] == DELAY + 1 for a in ARMS for s in SEEDS) \
    and all(prefix_ok.values())
wired_dead = [f"{a}_{s}" for a in ARMS for s in SEEDS if dm[f"{a}_{s}"] == 0.0]
log(f"C0 anchors pass {c0_pass} ({len(c0)} keys) | C0P {c0p_pass} | C1 {c1} "
    f"| wired_dead {len(wired_dead)}")

# ---------------- analysis ----------------
cells = {("open", str(s)): duty_off(*[OPEN_TR[s][c] for c in SIGS]) for s in SEEDS}
for a in ARMS:
    for s in SEEDS:
        d = duty_off(*[res[str(s)]["tr"][a][c] for c in SIGS])
        d["e2"] = seg2(res[str(s)]["mm"][a])
        # amplitude-landing probe: mean pool activity over OFF-window samples
        d["amp"] = round(float(np.mean(
            [res[str(s)]["tr"][a][c][OFF_TS].mean() for c in SIGS])), 5)
        cells[(a, str(s))] = d
for s in SEEDS:
    cells[("open", str(s))]["e2"] = seg2(OPEN_MM[s])
    cells[("open", str(s))]["amp"] = round(float(np.mean(
        [OPEN_TR[s][c][OFF_TS].mean() for c in SIGS])), 5)


def arr(a, key):
    return np.array([cells[(a, str(s))][key] for s in SEEDS], float)


open_off = arr("open", "duty")
open_e2_med = float(np.median(arr("open", "e2")))
open_SL, open_SR = arr("open", "SL"), arr("open", "SR")
open_dL, open_dR = arr("open", "dutyL"), arr("open", "dutyR")
open_amp = float(np.mean(arr("open", "amp")))

# C0O: open recomputed == l67 stored json
r67 = json.load(open("l67/results_l67.json"))
c0o = dict(off=[round(abs(v - q), 4) for v, q in zip(open_off, r67["open"]["off"])],
           SL=[round(abs(v - q), 4) for v, q in zip(open_SL, r67["open"]["SL"])],
           SR=[round(abs(v - q), 4) for v, q in zip(open_SR, r67["open"]["SR"])])
c0o_pass = all(max(c0o[k]) == 0.0 for k in c0o)


def wilson(k, nn, z=1.96):
    if nn == 0:
        return (0.0, 0.0, 1.0)
    p = k / nn
    den = 1 + z * z / nn
    ctr = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return (round(p, 3), round(ctr - hw, 3), round(ctr + hw, 3))


def arm_block(a):
    e2 = arr(a, "e2")
    dSL, dSR = arr(a, "SL") - open_SL, arr(a, "SR") - open_SR
    dL, dR = arr(a, "dutyL") - open_dL, arr(a, "dutyR") - open_dR
    lock_ok = bool(np.median(e2) <= max(0.01, 2 * open_e2_med) and e2.max() <= 0.5)
    amp = float(np.mean(arr(a, "amp")))
    return dict(gain=GAIN_OF[a], route=ROUTE_OF[a],
                dSL=[round(float(v), 3) for v in dSL],
                dSR=[round(float(v), 3) for v in dSR],
                dSL_mean=round(float(dSL.mean()), 3),
                dSR_mean=round(float(dSR.mean()), 3),
                dSL_pos=int((dSL > 0).sum()), dSR_pos=int((dSR > 0).sum()),
                dSR_wilson=wilson(int((dSR > 0).sum()), len(SEEDS)),
                dL_mean=round(float(dL.mean()), 3), dR_mean=round(float(dR.mean()), 3),
                e2_med=round(float(np.median(e2)), 4), e2_max=round(float(e2.max()), 4),
                cat=bool(e2.max() > 0.5), lock_ok=lock_ok,
                amp=round(amp, 5), d_amp_pct=round(100 * (amp - open_amp) / open_amp, 1),
                dm_min=round(min(dm[f"{a}_{s}"] for s in SEEDS), 5))


blocks = {a: arm_block(a) for a in ARMS}

# ---------------- gates (PREREG P1-P5) ----------------
ronly_arms = [a for a in ARMS if ROUTE_OF[a] == "ronly"]
lonly_arms = [a for a in ARMS if ROUTE_OF[a] == "lonly"]


def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)).astype(float), np.argsort(np.argsort(y)).astype(float)
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


p1_hits = [a for a in ronly_arms
           if blocks[a]["dSR_mean"] >= .10 and blocks[a]["dSR_pos"] >= 11
           and blocks[a]["dSL_mean"] >= -.05 and blocks[a]["lock_ok"]
           and blocks[a]["dm_min"] > 0]
p1 = dict(hits=p1_hits, pass_P1=bool(p1_hits))

g_seq = np.array([GAIN_OF[a] for a in ronly_arms])
dsr_seq = np.array([blocks[a]["dSR_mean"] for a in ronly_arms])
amp_seq = np.array([blocks[a]["amp"] for a in ronly_arms])
rho_dsr = spearman(g_seq, dsr_seq)
amp_monotone = bool(np.all(np.diff(amp_seq[np.argsort(g_seq)]) >= -1e-9))
max_dsr = float(dsr_seq.max())
if not p1["pass_P1"]:
    flat_floor = bool(max_dsr < .10 and abs(rho_dsr) < .8)
    p2 = dict(pass_P2=flat_floor, max_dSR_mean=round(max_dsr, 3),
              rho_dSR_vs_gain=round(rho_dsr, 3),
              verdict=("FLAT-FLOOR structural ceiling" if flat_floor
                       else "MIXED: monotone trend without a flip"))
else:
    p2 = dict(pass_P2=False, max_dSR_mean=round(max_dsr, 3),
              rho_dSR_vs_gain=round(rho_dsr, 3),
              verdict="P1 surprise branch — routing-limited")

p3 = {a: dict(dSL_mean=blocks[a]["dSL_mean"], dSR_mean=blocks[a]["dSR_mean"],
              crossed=bool(abs(blocks[a]["dSL_mean"]) >= abs(blocks[a]["dSR_mean"])))
      for a in ronly_arms}
p3_pass = all(v["crossed"] for v in p3.values())
p4 = dict(pass_P4=bool(all(blocks[a]["lock_ok"] for a in ARMS)),
          locks={a: blocks[a]["lock_ok"] for a in ARMS},
          cats={a: blocks[a]["cat"] for a in ARMS})
p5 = dict(rows={a: dict(gain=blocks[a]["gain"], dSL_mean=blocks[a]["dSL_mean"],
                        dSR_mean=blocks[a]["dSR_mean"]) for a in lonly_arms},
          note="lonly ipsi-bonus dose curve (descriptive)")
landing = dict(amp_monotone_in_gain=amp_monotone,
               open_amp=round(open_amp, 5),
               ronly_amp_by_gain={str(GAIN_OF[a]): blocks[a]["amp"] for a in ronly_arms},
               ronly_damp_pct={str(GAIN_OF[a]): blocks[a]["d_amp_pct"] for a in ronly_arms})

# best-dose selection (PREREG rule): argmax dSR_mean; tiebreak pos, then lower gain
best = max(ronly_arms, key=lambda a: (blocks[a]["dSR_mean"], blocks[a]["dSR_pos"],
                                      -GAIN_OF[a]))
mirror = blocks[f"lonly_g{int(GAIN_OF[best]*1000):03d}"]

verdict = ("ROUTING-LIMITED (P1 hit)" if p1["pass_P1"]
           else (p2["verdict"] if not p1["pass_P1"] else ""))

out = dict(arms=ARMS, seeds=SEEDS, sign=SIGN, delay=DELAY, gains=GAINS,
           open=dict(off=[round(float(v), 3) for v in open_off],
                     e2_med=round(open_e2_med, 4),
                     SL=[round(float(v), 3) for v in open_SL],
                     SR=[round(float(v), 3) for v in open_SR],
                     dutyL=[round(float(v), 3) for v in open_dL],
                     dutyR=[round(float(v), 3) for v in open_dR],
                     amp=round(open_amp, 5)),
           blocks=blocks, best_r_dose=dict(arm=best, gain=GAIN_OF[best],
                                           dSR_mean=blocks[best]["dSR_mean"],
                                           dSR_pos=blocks[best]["dSR_pos"]),
           mirror_control=dict(arm=f"lonly_g{int(GAIN_OF[best]*1000):03d}",
                               dSL_mean=mirror["dSL_mean"],
                               dSR_mean=mirror["dSR_mean"],
                               lock_ok=mirror["lock_ok"]),
           gates=dict(P1=p1, P2=p2, P3=dict(rows=p3, pass_P3=p3_pass), P4=p4, P5=p5,
                      landing=landing),
           anchors=dict(c0_n=len(c0), c0_pass=c0_pass,
                        c0o=c0o, c0o_pass=bool(c0o_pass),
                        c0p_pass=bool(c0p_pass), c1=bool(c1),
                        wired_dead=wired_dead),
           dm=dm, first_div=first_div)
with open("l69/results_l69.json", "w") as f:
    json.dump(out, f, indent=1)

log(f"C0O open-vs-l67json pass {c0o_pass}")
for a in ARMS:
    b = blocks[a]
    log(f"{a}: dSL {b['dSL_mean']:+.3f} (pos {b['dSL_pos']}/16) "
        f"dSR {b['dSR_mean']:+.3f} (pos {b['dSR_pos']}/16 {b['dSR_wilson']}) "
        f"dutyR {b['dR_mean']:+.3f} lock_ok {b['lock_ok']} cat {b['cat']} "
        f"d_amp {b['d_amp_pct']:+.1f}% dm {b['dm_min']}")
log(f"P1 {'PASS' if p1['pass_P1'] else 'FAIL'} | P2 {p2.get('verdict')} "
    f"| P3 crossed-every-dose {p3_pass} | P4 {p4['pass_P4']} "
    f"| landing amp_monotone {amp_monotone}")
log(f"best r dose: {best} -> mirror lonly dSL {mirror['dSL_mean']:+.3f} "
    f"dSR {mirror['dSR_mean']:+.3f}")
log(f"VERDICT {verdict} | done {time.time()-t0:.0f}s")
