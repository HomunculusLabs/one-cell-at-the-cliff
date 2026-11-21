"""L84: seg0-entry-library (LANE.md ideas 42). PREREG l84/PREREG.md FIRST.

Only seg0 [0,2000) varies across arms; seg1/seg2 are the l59 hynohop form for
every arm; no hops. Arms: base (l59 verbatim) / cont (continuous 0.7) / nod
(no mech) / echo (base chop + l66 echo during seg0 only). Exit features on
the seg0 tail predict the seg1 structure draw: pooled univariate AUCs, LOSO
multivariate logistic, within-seed paired reads. CPU-only; raw npz
checkpointed BEFORE analysis; no live changes.
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
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
FB = dict(gfb=.1, delay=5, sign=-1.0)          # l66 content cell verbatim
SIGS = ("fL", "fR", "eL", "eR")
CORE_TYPES = ("IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012")
ARMS = ["base", "cont", "nod", "echo"]
FEATS = ("SL_exit", "SR_exit", "both_exit", "mm_exit", "cpg_exit")
F_EXIT = (1500, 2000)               # S-feature window (TS-gated)
F_LEV = (1900, 2000)                # level-feature window
Y1_WIN = (2500, 4000)               # primary outcome: seg1 duty
Y2_WIN = (3200, 4000)               # secondary: wpost duty
LOCK_TOL = 0.10
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l59/l66/l82 verbatim) ----------
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
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in SIGS])   # l66-verbatim
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
assert len(mech) > 0
CORE = {ct: np.where(ltyp == ct)[0] for ct in CORE_TYPES}
for ct, v in CORE.items():
    assert len(v) == 6, (ct, len(v))
core_all = np.concatenate([CORE[ct] for ct in CORE_TYPES])
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} | antag "
    f"{len(ANTAG)} | cpg core {len(core_all)} | {time.time()-t0:.0f}s")

# ---------- global phase (l39 convention) + per-arm AMPA / EON ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

AMPA = {}
for a in ARMS:                                  # l59 hynohop form everywhere
    t_ = np.zeros(WIN, np.float64)
    for seg0, _, _ in SEGB:                     # 500-on/400-off per 0.7 seg
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            t_[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    t_[2000:4000] = ENT_AMP                     # fast segment CONTINUOUS
    AMPA[a] = t_
AMPA["cont"][:2000] = ENT_AMP                   # seg0 continuous 0.7
AMPA["nod"][:2000] = 0.0                        # seg0 no drive
# base/echo keep the l59 chop in seg0
for a in ARMS:                                  # seg1/2 IDENTICAL all arms
    assert np.array_equal(AMPA[a][2000:], AMPA["base"][2000:]), a
assert (AMPA["base"][:500] == ENT_AMP).all() and (AMPA["base"][500:900] == 0).all()

EON = {a: np.zeros(WIN, bool) for a in ARMS}
EON["echo"][:2000] = True                       # l82 fb07's mirror: seg0 only
assert EON["echo"][:2000].all() and not EON["echo"][2000:].any()
assert not any(EON[a].any() for a in ARMS if a != "echo")

DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
sin_carr = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in range(WIN)])
MASS = {a: float((AMPA[a] * sin_carr).sum()) for a in ARMS}
log("drive-on steps " + json.dumps(DRIVE_ON) + " | amp mass "
    + json.dumps({a: round(v, 1) for a, v in MASS.items()}))


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


# ---------- rollouts (l82 step_all form; per-arm AMPA + EON-gated echo) ----------
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
    xc = {a: np.zeros(WIN, np.float32) for a in ARMS}
    mA = np.zeros(WIN, np.float32)                # echo arm only

    def step_all(k):
        global settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            ph_k = PHI[k]
            sin_ph = math.sin(ph_k)
        else:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
            sin_ph = math.sin(ph_k)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            amp_k = ENT_AMP if k < 0 else float(AMPA[a][k])
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            if a == "echo" and k >= FB["delay"] and EON[a][k]:
                drive[mech, 0] += FB["gfb"] * FB["sign"] * float(mA[k - FB["delay"]])
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
            xc[a][i] = X[a][core_all].mean()
        mA[i] = X["echo"][ANTAG].mean()
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                          mm=mm, tr=tr, xc=xc)
    np.savez_compressed(
        "l84/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l84/raw_l84.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS},
    **{f"xc_{a}_{s}": res[str(s)]["xc"][a] for a in ARMS for s in SEEDS})
log("raw_l84.npz checkpointed BEFORE analysis (crash => verdict re-derives)")

# ---------------- anchors (enumerated keys ONLY) ----------------
z59 = np.load("l59/raw_l59.npz")
z82 = np.load("l82/raw_l82.npz")
c0a = {}
for s in SEEDS:
    c0a[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["base"] - z59[f"mm_hynohop_{s}"][:WIN]).max())
    for c in SIGS:
        c0a[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["base"][c] - z59[f"{c}_hynohop_{s}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())

c0x = {}
for s in SEEDS:
    c0x[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["echo"][:2000] - z82[f"mm_hynohop_fb_{s}"][:2000]).max())
    for c in SIGS:
        c0x[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["echo"][c][:2000]
            - z82[f"{c}_hynohop_fb_{s}"][:2000]).max())
c0x_pass = all(v == 0.0 for v in c0x.values())

# C0x2: echo vs l82 fb first divergence == 2001
c0x2 = {}
for s in SEEDS:
    d = np.concatenate(
        [np.abs(res[str(s)]["mm"]["echo"] - z82[f"mm_hynohop_fb_{s}"][:WIN])]
        + [np.abs(res[str(s)]["tr"]["echo"][c] - z82[f"{c}_hynohop_fb_{s}"][:WIN])
           for c in SIGS])
    fd = int(np.argmax(d > 0)) if (d > 0).any() else -1
    c0x2[str(s)] = fd
c0x2_pass = all(v == 2001 for v in c0x2.values())

# C0P: first-divergence laws vs base (own run; PREREG ADDENDUM 1: the
# compared traces are MOTOR pools — mech-drive changes land one hop later,
# l77 {6:16} / l83 {2001:64} stored law)
EXPECT_FD = {"echo": 6, "cont": 501, "nod": 1}
c0p, dm = {}, {}
for va in ("echo", "cont", "nod"):
    for s in SEEDS:
        m = res[str(s)]
        d = np.concatenate(
            [np.abs(m["mm"][va] - m["mm"]["base"])]
            + [np.abs(m["tr"][va][c] - m["tr"]["base"][c]) for c in SIGS])
        fd = int(np.argmax(d > 0)) if (d > 0).any() else -1
        c0p[f"{va}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{va}_{s}"] = round(float(d.max()), 5)
c0p_pass = all(c0p[f"{va}_{s}"] == EXPECT_FD[va]
               for va in EXPECT_FD for s in SEEDS)
c2_pass = all(v > 0.0 for v in dm.values())
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
log(f"C0a {c0a_pass} | C0x {c0x_pass} | C0x2 {c0x2_pass} | C0P {c0p_pass}"
    f" | C1 {c1} | C2 {c2_pass}"
    f" | fd counts {dict((v, list(c0p.values()).count(v)) for v in set(c0p.values()))}"
    f" | c0x2 counts {dict((v, list(c0x2.values()).count(v)) for v in set(c0x2.values()))}")

# ---------------- S arrays, features, outcomes ----------------
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


def duty_in(a, s, lo, hi):
    SL, SR = s_arrays(a, str(s))
    q = (TS >= lo) & (TS < hi)
    both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
    return float(np.nanmean(both)), float(np.nanmedian(SL[TS[q]])), \
        float(np.nanmedian(SR[TS[q]]))


rows = []
for a in ARMS:
    for s in SEEDS:
        d0, sl0, sr0 = duty_in(a, s, MEAS0, 2000)      # seg0 structure
        d_ex, sl_ex, sr_ex = duty_in(a, s, *F_EXIT)     # exit features
        y1, sl1, sr1 = duty_in(a, s, *Y1_WIN)           # primary outcome
        y2, _, _ = duty_in(a, s, *Y2_WIN)               # secondary
        rows.append(dict(
            arm=a, seed=s,
            seg0_duty=round(float(d0), 3),
            SL_exit=round(float(sl_ex), 3), SR_exit=round(float(sr_ex), 3),
            both_exit=round(float(d_ex), 3),
            mm_exit=round(float(res[str(s)]["mm"][a][F_LEV[0]:F_LEV[1]].mean()), 4),
            cpg_exit=round(float(res[str(s)]["xc"][a][F_LEV[0]:F_LEV[1]].mean()), 4),
            f0_exit=round(float(dom_freq(res[str(s)]["mm"][a][1200:2000])), 3),
            y1=round(float(y1), 3), y2=round(float(y2), 3),
            y1_lab=int(y1 >= .25),
            sl1=round(float(sl1), 3), sr1=round(float(sr1), 3)))
df = pd.DataFrame(rows)

# lock (diagnostic): seg1 block errors vs 1.4
lock = {}
for a in ARMS:
    errs = []
    for s in SEEDS:
        for b0 in (2500, 3000, 3500):
            errs.append(abs(dom_freq(res[str(s)]["mm"][a][b0:b0 + BLK]) - 1.4))
    lock[a] = dict(le01=int(sum(e <= LOCK_TOL for e in errs)),
                   mean=round(float(np.mean(errs)), 4))

# ---------------- registered prediction reads ----------------
def auc(score, lab):
    pos = score[lab == 1]
    neg = score[lab == 0]
    if not len(pos) or not len(neg):
        return None
    gt = (pos[:, None] > neg[None, :]).sum()
    eq = (pos[:, None] == neg[None, :]).sum()
    return float((gt + .5 * eq) / (len(pos) * len(neg)))


y = df["y1_lab"].to_numpy()
var_all = int(df.y1_lab.nunique())
p2 = {}
for f in FEATS + ("f0_exit",):
    a_ = auc(df[f].to_numpy(), y) if var_all == 2 else None
    # within-seed PAIRED read (controller question): discordant-label arm
    # pairs inside a seed, ranked correctly by the feature?
    conc = disc = 0
    for s in SEEDS:
        g = df[df.seed == s]
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                li, lj = int(g.y1_lab.iloc[i]), int(g.y1_lab.iloc[j])
                if li == lj:
                    continue
                hi_, lo_ = (i, j) if li > lj else (j, i)
                if g[f].iloc[hi_] > g[f].iloc[lo_]:
                    conc += 1
                disc += 1
    p2[f] = dict(auc=(round(a_, 3) if a_ is not None else None),
                 eligible=f in FEATS,
                 paired_within=(round(conc / disc, 3) if disc else None),
                 n_pairs=disc)

# per-seed Spearman across arms (P4)
def spear(x, yy):
    rx = pd.Series(x).rank().to_numpy()
    ry = pd.Series(yy).rank().to_numpy()
    rx, ry = rx - rx.mean(), ry - ry.mean()
    den = math.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 1e-12 else None


p4 = {}
for f in FEATS:
    rhos, ns = [], 0
    for s in SEEDS:
        g = df[df.seed == s]
        if g.y1.nunique() > 1:
            rhos.append(spear(g[f].to_numpy(), g["y1"].to_numpy()))
    rhos = [r for r in rhos if r is not None]
    p4[f] = dict(mean_rho=round(float(np.mean(rhos)), 3) if rhos else None,
                 n_pos=int(sum(r > 0 for r in rhos)), n=len(rhos))

# P3 LOSO multivariate logistic on F1-F5 (ridge-Newton, standardized on train)
F = df[list(FEATS)].to_numpy(np.float64)
Y = df["y1_lab"].to_numpy(np.float64)
held = np.zeros(len(df))
if var_all == 2:
    for s in SEEDS:
        tr = (df.seed.to_numpy() != s)
        te = ~tr
        mu, sd = F[tr].mean(0), F[tr].std(0)
        sd[sd < 1e-9] = 1.0
        Xt = (F[tr] - mu) / sd
        Xt = np.hstack([Xt, np.ones((tr.sum(), 1))])
        w = np.zeros(Xt.shape[1])
        lam = 1e-3
        for _ in range(50):
            zarg = np.clip(Xt @ w, -30, 30)
            z = 1 / (1 + np.exp(-zarg))
            gr = Xt.T @ (z - Y[tr]) + lam * w
            hh = (z * (1 - z))[:, None] * Xt
            H = Xt.T @ hh + lam * np.eye(Xt.shape[1])
            step = np.linalg.solve(H, gr)
            w -= step
            if np.abs(step).max() < 1e-9:
                break
        Xe = np.hstack([(F[te] - mu) / sd, np.ones((te.sum(), 1))])
        held[te] = Xe @ w
    p3 = dict(loso_auc=round(auc(held, Y), 3), n=int(len(df)))
else:
    p3 = dict(loso_auc=None, n=int(len(df)))

# E2 library spans: nod vs base both_exit per seed (registered form)
e2 = int((df[df.arm == "nod"].both_exit.to_numpy()
          < df[df.arm == "base"].both_exit.to_numpy()).sum())

# verdict (registered levels; degenerate branches take precedence)
seed_locked = all(df[df.seed == s].y1_lab.nunique() == 1 for s in SEEDS)
if var_all < 2:
    verdict = "NULL-VARIANCE (no AUC)"
    best_f = best_paired = None
elif e2 < 13:
    verdict = "UNDERPOWERED-LIBRARY (E2 fail: entry arms did not span)"
    best_f = max(FEATS, key=lambda f: (p2[f]["auc"] if p2[f]["auc"] is not None else -1))
    best_paired = max(FEATS, key=lambda f: (p2[f]["paired_within"] or -1))
elif seed_locked:
    verdict = "DRAW-SEED-LOCKED"
    best_f = max(FEATS, key=lambda f: (p2[f]["auc"] if p2[f]["auc"] is not None else -1))
    best_paired = max(FEATS, key=lambda f: (p2[f]["paired_within"] or -1))
else:
    best_f = max(FEATS, key=lambda f: (p2[f]["auc"] if p2[f]["auc"] is not None else -1))
    best_paired = max(FEATS, key=lambda f: (p2[f]["paired_within"] or -1))
    settable = (p2[best_f]["auc"] >= .75
                and (p2[best_f]["paired_within"] or 0) >= .70
                and p3["loso_auc"] >= .70)
    trace = (all(p2[f]["auc"] < .65 for f in FEATS)
             and all((p2[f]["paired_within"] or 0) < .65 for f in FEATS)
             and p3["loso_auc"] < .60)
    verdict = ("SETTABLE" if settable else
               "TRACE-LEVEL" if trace else "PARTIAL")

arm_tbl = {}
for a in ARMS:
    g = df[df.arm == a]
    k1 = int((g.y1 >= .25).sum())
    arm_tbl[a] = dict(
        seg0_duty=round(float(g.seg0_duty.mean()), 3),
        seg2_note="seg2 identical drive; see cells",
        y1_mean=round(float(g.y1.mean()), 3), k1=k1,
        y2_mean=round(float(g.y2.mean()), 3),
        SL_exit=round(float(g.SL_exit.mean()), 3),
        SR_exit=round(float(g.SR_exit.mean()), 3),
        mm_exit=round(float(g.mm_exit.mean()), 4),
        cpg_exit=round(float(g.cpg_exit.mean()), 4))
    # seg2 duty for the persistence read
    d2 = [duty_in(a, s, 4500, 6000)[0] for s in SEEDS]
    arm_tbl[a]["seg2_duty"] = round(float(np.mean(d2)), 3)


def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


for a in ARMS:
    arm_tbl[a]["wilson_k1"] = wilson(arm_tbl[a]["k1"], len(SEEDS))

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, feats=list(FEATS),
                     windows=dict(f_exit=F_EXIT, f_lev=F_LEV, y1=Y1_WIN, y2=Y2_WIN),
                     drive_on=DRIVE_ON, mass={a: round(MASS[a], 1) for a in ARMS},
                     nodes=int(n), edges=len(gsrc)),
           anchors=dict(c0a_pass=c0a_pass, c0x_pass=c0x_pass,
                        c0x2_pass=bool(c0x2_pass), c0p_pass=bool(c0p_pass),
                        c1=bool(c1), c2=bool(c2_pass),
                        first_div=c0p, dm=dm, c0x2=c0x2),
           arm_table=arm_tbl, lock=lock,
           p2=p2, p3=p3, p4=p4,
           e2_nod_below_base=e2,
           seed_locked=bool(seed_locked),
           best_feat=best_f, best_paired_feat=best_paired,
           verdict=verdict,
           rows=json.loads(df.round(4).to_json(orient="records")))
json.dump(out, open("l84/results_l84.json", "w"), indent=1)
log("P2 " + json.dumps({k: v["auc"] for k, v in p2.items()}))
log("P2 paired-within " + json.dumps({k: v["paired_within"] for k, v in p2.items()}))
log("P3 " + json.dumps(p3))
log("P4 " + json.dumps(p4))
log(f"E2 nod<base both_exit {e2}/16 | seed_locked {seed_locked} | "
    f"var_all {var_all}")
if best_f:
    log(f"VERDICT {verdict} | best {best_f} auc {p2[best_f]['auc']} paired "
        f"{p2[best_f]['paired_within']}")
else:
    log(f"VERDICT {verdict}")
log(f"done {time.time()-t0:.0f}s -> l84/results_l84.json")
