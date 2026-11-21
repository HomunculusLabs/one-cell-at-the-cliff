"""L67: side-split-echo (LANE.md ideas-33). PREREG l67/PREREG.md FIRST.

Machinery l66_census.py verbatim; open arm reused from l66/raw_l66.npz
(not rerun); 4 stepped echo arms x 16 census seeds; CPU-only; no live
changes. NEW per-side reads: dutyL/dutyR over the same off-window samples.
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
GFB, SIGN, DELAY = 0.1, -1.0, 5
BI, LONLY, RONLY, SPLIT = "bi", "lonly", "ronly", "split"
ARMS = [BI, LONLY, RONLY, SPLIT]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l66 verbatim) ----------
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

# L67: rootSide split (L60 join form)
lrside = rside_g[keep]
mechL = mech[lrside[mech] == "L"]
mechR = mech[lrside[mech] == "R"]
mechU = mech[~np.isin(lrside[mech], ["L", "R"])]
ECHO_IDX = {BI: mech, LONLY: mechL, RONLY: mechR, SPLIT: np.sort(np.concatenate([mechL, mechR]))}
for a in (LONLY, RONLY, SPLIT):
    assert len(ECHO_IDX[a]) > 0, a
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in ("fL", "fR", "eL", "eR")])   # l66 exact
ANTL = np.concatenate([PAIRS["Tr"]["fL"], PAIRS["Tr"]["eL"]])
ANTR = np.concatenate([PAIRS["Tr"]["fR"], PAIRS["Tr"]["eR"]])
assert np.array_equal(np.sort(np.concatenate([ANTL, ANTR])), np.sort(ANTAG))
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} "
    f"(L {len(mechL)} R {len(mechR)} unkn {len(mechU)}) | antag {len(ANTAG)} "
    f"(L {len(ANTL)} R {len(ANTR)}) | {time.time()-t0:.0f}s")

# C0w: wiring identity asserts (echo index sets)
assert np.array_equal(ECHO_IDX[LONLY], np.sort(mechL))
assert np.array_equal(ECHO_IDX[RONLY], np.sort(mechR))
assert np.array_equal(ECHO_IDX[SPLIT], np.sort(np.concatenate([mechL, mechR])))
assert len(np.intersect1d(ECHO_IDX[LONLY], ECHO_IDX[RONLY])) == 0
assert set(ECHO_IDX[SPLIT].tolist()) | set(mechU.tolist()) == set(mech.tolist())

# ---------- phase + base chop AMPA (l66 verbatim) ----------
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

# ---------- open arm reused from l66 stored ----------
z66 = np.load("l66/raw_l66.npz")
OPEN_MM = {s: z66[f"mm_hynohop_{s}"] for s in SEEDS}
OPEN_TR = {s: {c: z66[f"{c}_hynohop_{s}"] for c in SIGS} for s in SEEDS}
need = [f"mm_hynohop_{s}" for s in SEEDS] + [f"{c}_hynohop_{s}" for s in SEEDS for c in SIGS]
missing = [k for k in need if k not in set(z66.keys())]
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
    mAp = {a: np.zeros(WIN, np.float32) for a in ARMS}
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
                if a == BI:
                    drive[mech, 0] += GFB * SIGN * float(mAp[a][k - DELAY])
                elif a == LONLY:
                    drive[mechL, 0] += GFB * SIGN * float(mLp[a][k - DELAY])
                elif a == RONLY:
                    drive[mechR, 0] += GFB * SIGN * float(mRp[a][k - DELAY])
                else:
                    drive[mechL, 0] += GFB * SIGN * float(mLp[a][k - DELAY])
                    drive[mechR, 0] += GFB * SIGN * float(mRp[a][k - DELAY])
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
            mAp[a][i] = X[a][ANTAG].mean()
            mLp[a][i] = X[a][ANTL].mean()
            mRp[a][i] = X[a][ANTR].mean()
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                          mm=mm, tr=tr)
    np.savez_compressed(
        "l67/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l67/raw_l67.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS},
    **{f"mm_hynohop_{s}": OPEN_MM[s] for s in SEEDS},
    **{f"{c}_hynohop_{s}": OPEN_TR[s][c] for s in SEEDS for c in SIGS})

# ---------------- anchors (enumerated keys ONLY) ----------------
c0 = {}
for s in SEEDS:
    c0[f"bi_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"][BI] - z66[f"mm_g01_d05_m_{s}"][:WIN]).max())
    for c in SIGS:
        c0[f"bi_{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"][BI][c] - z66[f"{c}_g01_d05_m_{s}"][:WIN]).max())
c0_pass = all(v == 0.0 for v in c0.values())

dm, first_div, prefix_ok = {}, {}, {}
for a in (LONLY, RONLY, SPLIT):
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
c0s_pass = all(first_div[f"{a}_{s}"] == DELAY + 1 for a in (LONLY, RONLY, SPLIT)
               for s in SEEDS) and all(prefix_ok.values())
log(f"C0 bi==l66 pass {c0_pass} ({len(c0)} keys) | C0s side-prefix "
    f"{c0s_pass} | C1 {c1}")

# ---------------- analysis ----------------
cells = {("open", str(s)): duty_off(*[OPEN_TR[s][c] for c in SIGS]) for s in SEEDS}
for a in ARMS:
    for s in SEEDS:
        d = duty_off(*[res[str(s)]["tr"][a][c] for c in SIGS])
        d["e2"] = seg2(res[str(s)]["mm"][a])
        cells[(a, str(s))] = d
for s in SEEDS:
    cells[("open", str(s))]["e2"] = seg2(OPEN_MM[s])


def arr(a, key):
    return np.array([cells[(a, str(s))][key] for s in SEEDS], float)


open_off = arr("open", "duty")
open_e2_med = float(np.median(arr("open", "e2")))
open_SL, open_SR = arr("open", "SL"), arr("open", "SR")
open_dL, open_dR = arr("open", "dutyL"), arr("open", "dutyR")

# C0O: open recomputed == l66 stored json
r66 = json.load(open("l66/results_l66.json"))
c0o = dict(off=[round(abs(v - q), 4) for v, q in zip(open_off, r66["open"]["off"])],
           SL=[round(abs(v - q), 4) for v, q in zip(open_SL, r66["open"]["SL"])],
           SR=[round(abs(v - q), 4) for v, q in zip(open_SR, r66["open"]["SR"])])
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
    return dict(SL=[round(float(v), 3) for v in arr(a, "SL")],
                SR=[round(float(v), 3) for v in arr(a, "SR")],
                dutyL=[round(float(v), 3) for v in arr(a, "dutyL")],
                dutyR=[round(float(v), 3) for v in arr(a, "dutyR")],
                dSL=[round(float(v), 3) for v in dSL],
                dSR=[round(float(v), 3) for v in dSR],
                dSL_mean=round(float(dSL.mean()), 3),
                dSR_mean=round(float(dSR.mean()), 3),
                dSL_pos=int((dSL > 0).sum()), dSR_pos=int((dSR > 0).sum()),
                dSR_wilson=wilson(int((dSR > 0).sum()), len(SEEDS)),
                dL_mean=round(float(dL.mean()), 3), dR_mean=round(float(dR.mean()), 3),
                e2=[round(float(v), 4) for v in e2],
                e2_med=round(float(np.median(e2)), 4),
                cat=bool(e2.max() > 0.5), lock_ok=lock_ok,
                dm_min=round(min(dm[f"{a}_{s}"] for s in SEEDS), 5))


blocks = {a: arm_block(a) for a in ARMS}
bi, lo, ro, sp = blocks[BI], blocks[LONLY], blocks[RONLY], blocks[SPLIT]

# L66 value replication on the bi arm
bi_rep = dict(dSL_mean=bi["dSL_mean"], dSR_mean=bi["dSR_mean"],
              l66_fb_SL=round(float(np.mean(r66["fb"]["SL"])), 3),
              l66_fb_SR=round(float(np.mean(r66["fb"]["SR"])), 3))

# gates (PREREG P1-P5, branch B)
p1 = dict(need_dSR=.10, dSR_mean=ro["dSR_mean"], dSR_pos=ro["dSR_pos"],
          dSL_mean=ro["dSL_mean"], lock_ok=ro["lock_ok"], dm_min=ro["dm_min"],
          pass_P1=bool(ro["dSR_mean"] >= .10 and ro["dSR_pos"] >= 11
                       and ro["dSL_mean"] >= -.05 and ro["lock_ok"]
                       and ro["dm_min"] > 0))
p2 = dict(dSL_mean=lo["dSL_mean"], dSR_mean=lo["dSR_mean"],
          pass_P2=bool(lo["dSL_mean"] >= .10 and lo["dSL_mean"] > lo["dSR_mean"]
                       and lo["dm_min"] > 0))
crossed = bool(np.mean(np.abs(np.array(ro["dSL"]))) >=
               np.mean(np.abs(np.array(ro["dSR"]))))
p3 = dict(dSL_mean_ro=ro["dSL_mean"], crossed=crossed,
          pass_P3=bool(ro["dSL_mean"] <= .05))
flips = int(sum((ro["dSR"][i] > 0) != (sp["dSR"][i] > 0) for i in range(len(SEEDS))))
p4 = dict(pass_P4=bool(all(blocks[a]["lock_ok"] for a in ARMS)),
          locks={a: blocks[a]["lock_ok"] for a in ARMS},
          cats={a: blocks[a]["cat"] for a in ARMS})
p5 = dict(dSL_mean=sp["dSL_mean"], dSR_mean=sp["dSR_mean"], lock_ok=sp["lock_ok"],
          pass_P5=bool(sp["dSL_mean"] >= .10 and sp["dSR_mean"] >= .10
                       and sp["lock_ok"] and sp["dm_min"] > 0))
branch_b = bool(not p1["pass_P1"] and (crossed
              or lo["dSL_mean"] < bi["dSL_mean"] - .10 or flips >= 5))
verdict = ("SIDE-TUNABLE" if p1["pass_P1"] else
           ("LOTTERY-CROSSED (branch B)" if branch_b else "MIXED/INFORMATIVE"))
wired_dead = [f"{a}_{s}" for a in (LONLY, RONLY, SPLIT) for s in SEEDS
              if dm[f"{a}_{s}"] == 0.0]

out = dict(arms=ARMS, seeds=SEEDS, gfb=GFB, sign=SIGN, delay=DELAY,
           open=dict(off=[round(float(v), 3) for v in open_off],
                     e2_med=round(open_e2_med, 4),
                     SL=[round(float(v), 3) for v in open_SL],
                     SR=[round(float(v), 3) for v in open_SR],
                     dutyL=[round(float(v), 3) for v in open_dL],
                     dutyR=[round(float(v), 3) for v in open_dR]),
           blocks=blocks, bi_replication=bi_rep,
           gates=dict(P1=p1, P2=p2, P3=p3, P4=p4, P5=p5,
                      dSR_flips_ronly_vs_split=flips,
                      branch_B_selected=branch_b, verdict=verdict),
           anchors=dict(c0_n=len(c0), c0_pass=c0_pass,
                        c0o=c0o, c0o_pass=bool(c0o_pass),
                        c0s_pass=bool(c0s_pass),
                        prefix_all=bool(all(prefix_ok.values())), c1=bool(c1),
                        c0w=dict(mechL=len(mechL), mechR=len(mechR),
                                 mechU=len(mechU), idx_checks="passed")),
           dm=dm, first_div=first_div, wired_dead=wired_dead)
with open("l67/results_l67.json", "w") as f:
    json.dump(out, f, indent=1)

log(f"C0O open-vs-l66json pass {c0o_pass} | bi replication dSL {bi['dSL_mean']:+.3f} "
    f"dSR {bi['dSR_mean']:+.3f} (l66 fb means {bi_rep['l66_fb_SL']}/{bi_rep['l66_fb_SR']})")
for a in ARMS:
    b = blocks[a]
    log(f"{a}: dSL {b['dSL_mean']:+.3f} (pos {b['dSL_pos']}/16) "
        f"dSR {b['dSR_mean']:+.3f} (pos {b['dSR_pos']}/16 {b['dSR_wilson']}) "
        f"dutyL {b['dL_mean']:+.3f} dutyR {b['dR_mean']:+.3f} "
        f"lock_ok {b['lock_ok']} cat {b['cat']} dm {b['dm_min']}")
log(f"P1 {p1['pass_P1']} | P2 {p2['pass_P2']} | P3 crossed {crossed} "
    f"(pass {p3['pass_P3']}) | P4 {p4['pass_P4']} | P5 {p5['pass_P5']} "
    f"| flips {flips} | wired_dead {len(wired_dead)}")
log(f"VERDICT {verdict} | done {time.time()-t0:.0f}s")
