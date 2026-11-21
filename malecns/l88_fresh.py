"""L88: fresh-seed replication of a pre-registered 2-feature mid-seg rule
(LANE.md ideas 44). PREREG l88/PREREG.md FIRST.

Phase 1 (stored only): recompute l87 fork features from raw_l87.npz, certify
against the 24 stored single-feature rules, search the registered 96-rule
2-feature family on census cells, select winner+runner-up.
Phase 2: roll ONLY the winner fork's two arms (base + latch@2500) on census
16 (C0V bit-identity vs raw_l87 = 33rd chain anchor) + fresh 501-516, rule
applied ONLINE with census-frozen thresholds; GATE-L85 rows scored ONCE.
CPU-only; raw npz checkpoint BEFORE analysis.
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
CEN = [11, 22, 33] + list(range(101, 114))   # l87 census, n=16
FRESH = list(range(501, 517))                # never used in the chain
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
HOP_AMP, HOP_VW = 0.5, 40
TRANS = [2000, 4000]
LOCK_TOL = 0.10
FB = dict(gfb=.1, delay=5, sign=-1.0)          # l66 content cell verbatim
FORKS = {"nh_on2500": "hynohop", "nh_off2500": "hynohop_fb",
         "hy_on2500": "hybrid", "hy_off2500": "hybrid_fb"}
SIGS = ("fL", "fR", "eL", "eR")
TS = np.arange(499, WIN, 10)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


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


def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return [round(c - hw, 3), round(c + hw, 3)]   # LIST (json-comparable)


# ================= phase 1: stored-only rule search =================
z87 = np.load("l87/raw_l87.npz")
R87 = json.load(open("l87/results_l87.json"))
cells87 = R87["cells"]


def s_arrays_stored(a, s):
    fL = z87[f"fL_{a}_{s}"]
    fR = z87[f"fR_{a}_{s}"]
    eL = z87[f"eL_{a}_{s}"]
    eR = z87[f"eR_{a}_{s}"]
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    return SL, SR


def feats_from_arrays(SL, SR, mm):
    q = (TS >= 2300) & (TS < 2500)
    return (round(float(np.nanmedian(SL[TS[q]])), 3),
            round(float(np.nanmedian(SR[TS[q]])), 3),
            round(float(mm[2400:2500].mean()), 5))


FEATS = ("SL2500", "SR2500", "mm2500")
F = {}
for base in FORKS.values():
    F[base] = {f: [] for f in FEATS}
    for s in CEN:
        SL, SR = s_arrays_stored(base, s)
        v = feats_from_arrays(SL, SR, z87[f"mm_{base}_{s}"])
        for f, x in zip(FEATS, v):
            F[base][f].append(x)

# --- C0E certification: reproduce all 24 stored single-feature rules ---
cert_ok, cert_n = True, 0
for r in R87["rules"]:
    base = FORKS[r["fork"]]
    v = F[base][r["feature"]]
    thr = float(np.median(v))
    pick = []
    for i, s in enumerate(CEN):
        use_latch = (v[i] >= thr) if r["direction"] == ">=" else (v[i] < thr)
        pick.append(r["fork"] if use_latch else base)
    d07s = [cells87[pick[i]][str(s)]["duty_07"] for i, s in enumerate(CEN)]
    s1s = [cells87[pick[i]][str(s)]["segs"][1]["duty"] for i, s in enumerate(CEN)]
    k = int(sum(x >= .5 for x in d07s))
    s1m = round(float(np.mean(s1s)), 3)
    if k != r["k"] or s1m != r["seg1_mean"] or pick != r["picks"]:
        cert_ok = False
        log(f"C0E FAIL {r['fork']} {r['feature']} {r['direction']}"
            f" mine k={k} s1={s1m} stored k={r['k']} s1={r['seg1_mean']}")
    cert_n += 1
log(f"C0E certification {'PASS' if cert_ok else 'FAIL'} ({cert_n} stored rules)")
assert cert_ok, "feature machinery uncertified — addendum before anything else"

# --- the registered 96-rule 2-feature family ---
PAIRS_F = (("SL2500", "SR2500"), ("SL2500", "mm2500"), ("SR2500", "mm2500"))
CONDS = (">=", "<")


def rule_picks(base, latch, f1, c1, f2, c2, comb, thr1, thr2):
    pick = []
    for i in range(len(CEN)):
        a = (F[base][f1][i] >= thr1) if c1 == ">=" else (F[base][f1][i] < thr1)
        b = (F[base][f2][i] >= thr2) if c2 == ">=" else (F[base][f2][i] < thr2)
        use = (a and b) if comb == "AND" else (a or b)
        pick.append(latch if use else base)
    return pick


rules2 = []
idx = 0
for latch, base in FORKS.items():
    thr = {f: float(np.median(F[base][f])) for f in FEATS}
    for f1, f2 in PAIRS_F:
        for c1 in CONDS:
            for c2 in CONDS:
                for comb in ("AND", "OR"):
                    pick = rule_picks(base, latch, f1, c1, f2, c2, comb,
                                      thr[f1], thr[f2])
                    d07s = [cells87[pick[i]][str(s)]["duty_07"]
                            for i, s in enumerate(CEN)]
                    s1s = [cells87[pick[i]][str(s)]["segs"][1]["duty"]
                           for i, s in enumerate(CEN)]
                    locks = [cells87[pick[i]][str(s)]["segs"][1]["err"] <= .01
                             for i, s in enumerate(CEN)]
                    k = int(sum(x >= .5 for x in d07s))
                    s1m = round(float(np.mean(s1s)), 3)
                    w = wilson(k, len(CEN))
                    clears = (all(locks) and k >= 15 and w[0] >= .717
                              and s1m >= .358)
                    rules2.append(dict(
                        idx=idx, fork=latch, base=base, f1=f1, c1=c1, f2=f2,
                        c2=c2, comb=comb, thr1=thr[f1], thr2=thr[f2], k=k,
                        wilson=w, seg1_mean=s1m, n_lock=int(sum(locks)),
                        census_clears=bool(clears), picks=pick))
                    idx += 1
n_clear = sum(r["census_clears"] for r in rules2)
ranked = sorted(rules2, key=lambda r: (r["census_clears"], r["seg1_mean"],
                                       r["k"], -r["idx"]), reverse=True)
winner, runner = ranked[0], ranked[1]
log(f"phase1: {len(rules2)} rules, census-clears {n_clear} | winner "
    f"{winner['fork']} {winner['f1']}{winner['c1']}&/{winner['comb']}"
    f"{winner['f2']}{winner['c2']} k={winner['k']} s1={winner['seg1_mean']}"
    f" | runner {runner['fork']} {runner['f1']}{runner['c1']}"
    f"{runner['comb']}{runner['f2']}{runner['c2']} k={runner['k']}"
    f" s1={runner['seg1_mean']}")
json.dump(dict(winner=winner, runner=runner, n_rules=len(rules2),
               n_census_clear=n_clear,
               top5=[{k: v for k, v in r.items() if k != "picks"}
                     for r in ranked[:5]]),
          open("l88/phase1_selection.json", "w"), indent=1)
log(f"phase1 selection checkpointed BEFORE any rollout ({time.time()-t0:.0f}s)")

# ================= substrate (l87 verbatim) =================
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idxm = {int(r): i for i, r in enumerate(ids)}
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
w = w[w["body_pre"].isin(idxm) & w["body_post"].isin(idxm)]
gsrc = w["body_pre"].map(idxm).to_numpy(np.int64)
gdst = w["body_post"].map(idxm).to_numpy(np.int64)
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
PAIRS_MN = {}
for k in ("Ti", "Tr"):
    f = np.where(motor & tm.isin([f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (tm == f"{k} extensor MN"))[0]
    fL, fR = f[lside[f] == "L"], f[lside[f] == "R"]
    eL, eR = e[lside[e] == "L"], e[lside[e] == "R"]
    assert len(fL) and len(fR) and len(eL) and len(eR), (k, len(fL), len(fR))
    PAIRS_MN[k] = dict(fL=fL, fR=fR, eL=eL, eR=eR)
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2
hopL = np.where((ltyp == "DNge046") & (lside == "L"))[0]
assert len(hopL) == 2, len(hopL)
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
assert len(mech) > 0
ANTAG = np.concatenate([PAIRS_MN["Tr"][c] for c in SIGS])   # l66-verbatim
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} | antag {len(ANTAG)}"
    f" | 046L {len(hopL)} | {time.time()-t0:.0f}s")

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- phase-2 arm set: winner fork's two arms ----------
BASE, LATCH = winner["base"], winner["fork"]
K = 2500
ARMS2 = [BASE, LATCH]
HOP2 = {a: (a.startswith("hy")) for a in ARMS2}
EON2 = {}
for a in ARMS2:
    if a == BASE:
        EON2[a] = (np.ones(WIN, bool) if BASE.endswith("_fb")
                   else np.zeros(WIN, bool))
    else:
        e = np.zeros(WIN, bool)
        if LATCH.endswith("on2500"):
            e[K:] = True
        else:
            e[:K] = True
        EON2[a] = e
        trunk_eon = np.ones(WIN, bool) if BASE.endswith("_fb") else np.zeros(WIN, bool)
        assert (EON2[a][:K] == trunk_eon[:K]).all(), "latch prefix != trunk gate"
        on = LATCH.endswith("on2500")
        assert (EON2[a][K:] == (np.ones(WIN - K, bool) if on
                                else np.zeros(WIN - K, bool))).all()
ECHO2 = [a for a in ARMS2 if EON2[a].any()]
AMPA2 = {a: np.zeros(WIN, np.float64) for a in ARMS2}
for a in ARMS2:
    for seg0, _, _ in SEGB:
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA2[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA2[a][2000:4000] = ENT_AMP
HOPA2 = {a: np.zeros(WIN, bool) for a in ARMS2}
for o in TRANS:
    for a in ARMS2:
        if HOP2[a]:
            HOPA2[a][o:o + HOP_VW] = True
assert all(np.array_equal(AMPA2[a], AMPA2[BASE]) for a in ARMS2)
DRIVE_ON = {a: int((AMPA2[a] > 0).sum()) + SETTLE for a in ARMS2}
assert all(v == 4800 for v in DRIVE_ON.values()), DRIVE_ON
log(f"phase2 arms {ARMS2} | drive-on 4800 asserted | echo arms {ECHO2}")

# ---------- rollouts (l87 step order verbatim) ----------
res = {}
for seed in CEN + FRESH:
    gen = torch.Generator().manual_seed(seed)
    X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    X = {a: X0.clone() for a in ARMS2}
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    settle_ph = 0.0
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS2}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS2}
    mA = {a: np.zeros(WIN, np.float32) for a in ECHO2}

    def step_all(k):
        global settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            ph_k = PHI[k]
        else:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
        sin_ph = math.sin(ph_k)
        for a in ARMS2:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if k < 0:
                amp_k = ENT_AMP
            else:
                amp_k = float(AMPA2[a][k])
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            if k >= 0 and HOPA2[a][k]:
                drive[hopL, 0] += HOP_AMP
            if a in ECHO2 and k >= FB["delay"] and EON2[a][k]:
                drive[mech, 0] += (FB["gfb"] * FB["sign"]
                                   * float(mA[a][k - FB["delay"]]))
            t = torch.relu(drive + BG)
            t = (t + nz).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])

    for k in range(SETTLE):
        step_all(-1 - k)
    for a in ARMS2:
        af = float((X[a] > 0.05).float().mean())
        assert 0.01 < af < 0.9, (a, af, seed)
    for i in range(WIN):
        step_all(i)
        for a in ARMS2:
            mm[a][i] = X[a][motor].mean()
            for c in SIGS:
                tr[a][c][i] = X[a][PAIRS_MN["Tr"][c]].mean()
            if a in ECHO2:
                mA[a][i] = X[a][ANTAG].mean()
    res[str(seed)] = dict(
        af={a: float((X[a] > 0.05).float().mean()) for a in ARMS2},
        mm=mm, tr=tr, mA=mA)
    np.savez_compressed(
        "l88/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in CEN + FRESH if str(s) in res for a in ARMS2},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in CEN + FRESH if str(s) in res for a in ARMS2 for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

np.savez_compressed(
    "l88/raw_l88.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS2 for s in CEN + FRESH},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS2 for s in CEN + FRESH for c in SIGS},
    **{f"mA_{a}_{s}": res[str(s)]["mA"][a] for a in ECHO2 for s in CEN + FRESH})
log("raw_l88.npz checkpointed BEFORE analysis (crash => verdict re-derives)")

# ---------------- anchors ----------------
# C0V: census re-roll bit-identical to l87 stored raw (33rd chain anchor)
c0v = {}
for a in ARMS2:
    for s in CEN:
        c0v[f"mm|{a}_{s}"] = float(np.abs(
            res[str(s)]["mm"][a] - z87[f"mm_{a}_{s}"][:WIN]).max())
        for c in SIGS:
            c0v[f"{c}|{a}_{s}"] = float(np.abs(
                res[str(s)]["tr"][a][c] - z87[f"{c}_{a}_{s}"][:WIN]).max())
        if a in ECHO2:
            c0v[f"mA|{a}_{s}"] = float(np.abs(
                res[str(s)]["mA"][a] - z87[f"mA_{a}_{s}"][:WIN]).max())
c0v_pass = all(v == 0.0 for v in c0v.values())

# C0F: latch law both batches (prefix 0 + first-div 2501)
c0f_pref, c0f_fd, dm_lat = {}, {}, {}
for s in CEN + FRESH:
    m = res[str(s)]
    arrs = [np.abs(m["mm"][LATCH] - m["mm"][BASE])] + [
        np.abs(m["tr"][LATCH][c] - m["tr"][BASE][c]) for c in SIGS]
    diffs = np.concatenate(arrs)
    fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
    c0f_fd[str(s)] = int(fd % WIN) if fd >= 0 else -1
    c0f_pref[str(s)] = float(max(x[:K + 1].max() for x in arrs))
    dm_lat[str(s)] = round(float(diffs.max()), 5)
c0f_pass = (all(v == 0.0 for v in c0f_pref.values())
            and all(v == K + 1 for v in c0f_fd.values()))
degen_fresh = [s for s in FRESH if dm_lat[str(s)] == 0.0]
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in CEN + FRESH for a in ARMS2)

# C0M entrain mass
on_steps = np.where(AMPA2[BASE] > 0)[0]
sin_on = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in on_steps])
entrain_mass = round(float(ENT_AMP * sin_on.sum()), 1)
c0m_pass = entrain_mass == R87["meta"]["entrain_mass"]
log(f"C0V {'PASS' if c0v_pass else 'FAIL'} | C0F {'PASS' if c0f_pass else 'FAIL'}"
    f" fd set {sorted(set(c0f_fd.values()))} | C0M {c0m_pass}"
    f" ({entrain_mass}) | C1 {c1} | fresh-degenerate {degen_fresh}")

# ---------------- analysis (l87 cells machinery verbatim) ----------------
SM = {}


def s_arrays(a, s):
    if (a, s) not in SM:
        fL, fR, eL, eR = (res[s]["tr"][a][c] for c in SIGS)
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
            SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SM[(a, s)] = (SL, SR)
    return SM[(a, s)]


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    return round(float(np.nanmedian(arr[TS[q]])), 3) if q.any() else None


def cells_of(a, s):
    SL, SR = s_arrays(a, s)
    rows = []
    for a0_, b0, tg in SEGB:
        lo, hi = a0_ + MEAS0, b0
        q = (TS >= lo) & (TS < hi)
        both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
        f_seg = dom_freq(res[s]["mm"][a][a0_:b0])
        bl_errs, ttl = [], None
        for b in range(WIN // BLK):
            if a0_ <= b * BLK < b0 and b * BLK > a0_:
                f_hat = dom_freq(res[s]["mm"][a][b * BLK:(b + 1) * BLK])
                e = abs(f_hat - tg)
                bl_errs.append(e)
                if ttl is None and e <= LOCK_TOL:
                    ttl = b * BLK - a0_
        rows.append(dict(duty=round(float(np.nanmean(both)), 3),
                         SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                         f=round(f_seg, 3),
                         err=round(float(np.mean(bl_errs)), 4), ttl=ttl))
    qall = np.zeros(len(TS), bool)
    q07 = np.zeros(len(TS), bool)
    for a0_, b0, f in SEGB:
        qall |= (TS >= a0_ + MEAS0) & (TS < b0)
        if f == 0.7:
            q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
    return dict(segs=rows,
                duty_all=round(float(np.nanmean(
                    (SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
                duty_07=round(float(np.nanmean(
                    (SL[TS[q07]] >= .25) & (SR[TS[q07]] >= .25))), 3))


cells2 = {a: {str(s): cells_of(a, str(s)) for s in CEN + FRESH} for a in ARMS2}

# census cells must equal l87 stored cells (extra certification)
cencell_ok = all(
    cells2[a][str(s)]["segs"][i]["duty"] == cells87[a][str(s)]["segs"][i]["duty"]
    and cells2[a][str(s)]["duty_07"] == cells87[a][str(s)]["duty_07"]
    and cells2[a][str(s)]["segs"][1]["err"] == cells87[a][str(s)]["segs"][1]["err"]
    for a in ARMS2 for s in CEN for i in range(3))
log(f"census-cells certification {cencell_ok}")

# ---------------- ONLINE rule on both batches ----------------
def decide(seed_s):
    SL, SR = s_arrays(BASE, seed_s)
    v = feats_from_arrays(SL, SR, res[seed_s]["mm"][BASE])  # online read at K
    vals = dict(zip(FEATS, v))
    a1 = ((vals[winner["f1"]] >= winner["thr1"]) if winner["c1"] == ">="
          else (vals[winner["f1"]] < winner["thr1"]))
    b1 = ((vals[winner["f2"]] >= winner["thr2"]) if winner["c2"] == ">="
          else (vals[winner["f2"]] < winner["thr2"]))
    use = (a1 and b1) if winner["comb"] == "AND" else (a1 or b1)
    return LATCH if use else BASE, dict(SL2500=v[0], SR2500=v[1], mm2500=v[2])


def score(pick_map, seeds):
    d07s = [cells2[pick_map[str(s)]][str(s)]["duty_07"] for s in seeds]
    s1s = [cells2[pick_map[str(s)]][str(s)]["segs"][1]["duty"] for s in seeds]
    locks = [cells2[pick_map[str(s)]][str(s)]["segs"][1]["err"] <= .01
             for s in seeds]
    # echo budget per picked arm
    ratios = []
    for s in seeds:
        a = pick_map[str(s)]
        if a not in ECHO2:
            ratios.append(0.0)
        else:
            ks = np.where(EON2[a])[0]
            ks = ks[ks >= FB["delay"]]
            em = float(FB["gfb"] * res[str(s)]["mA"][a][ks - FB["delay"]].sum())
            ratios.append(round(em / float(entrain_mass), 4))
    k = int(sum(x >= .5 for x in d07s))
    w = wilson(k, len(seeds))
    return dict(
        k=k, wilson=w, n_lock=int(sum(locks)),
        seg1_mean=round(float(np.mean(s1s)), 3),
        d07_per_seed=[round(float(x), 3) for x in d07s],
        s1_per_seed=[round(float(x), 3) for x in s1s],
        lock_per_seed=[bool(x) for x in locks],
        ratio_max=max(ratios))


pick_cen, feats_cen = {}, {}
for s in CEN:
    pick_cen[str(s)], feats_cen[str(s)] = decide(str(s))
pick_fr, feats_fr = {}, {}
for s in FRESH:
    pick_fr[str(s)], feats_fr[str(s)] = decide(str(s))

cen_score = score(pick_cen, CEN)
fr_score = score(pick_fr, FRESH)

# runner-up descriptive only if same fork (same two rollouts)
runner_fr = None
if runner["fork"] == LATCH:
    pick_r = {}
    for s in FRESH:
        SL, SR = s_arrays(BASE, str(s))
        v = feats_from_arrays(SL, SR, res[str(s)]["mm"][BASE])
        vals = dict(zip(FEATS, v))
        a1 = ((vals[runner["f1"]] >= runner["thr1"]) if runner["c1"] == ">="
              else (vals[runner["f1"]] < runner["thr1"]))
        b1 = ((vals[runner["f2"]] >= runner["thr2"]) if runner["c2"] == ">="
              else (vals[runner["f2"]] < runner["thr2"]))
        use = (a1 and b1) if runner["comb"] == "AND" else (a1 or b1)
        pick_r[str(s)] = LATCH if use else BASE
    runner_fr = score(pick_r, FRESH)
    runner_fr["picks"] = pick_r

G1 = fr_score["n_lock"] == 16
G2a = fr_score["k"] >= 15 and fr_score["wilson"][0] >= 0.717
G3 = fr_score["seg1_mean"] >= 0.358
G4 = all(v == 4800 for v in DRIVE_ON.values()) and fr_score["ratio_max"] <= 0.127
anchors_ok = dict(c0v=c0v_pass, c0f=c0f_pass, c0e=cert_ok, c0m=c0m_pass,
                  c1=c1, census_cells=cencell_ok)
# census pick consistency: online census picks must equal phase-1 winner picks
picks_match = [pick_cen[str(s)] for s in CEN] == winner["picks"]
log(f"census online picks == phase1 winner picks: {picks_match}")

if not all(anchors_ok.values()):
    verdict = "ANCHOR-FAIL (addendum before any read)"
elif degen_fresh:
    verdict = (f"NO-GO-DEGENERATE: latch dead on fresh seeds {degen_fresh}"
               " (L55 rule — branch does not exist)")
elif G1 and G2a and G3 and G4:
    verdict = ("GO: pre-registered 2-feature rule clears GATE-L85 on FRESH "
               "seeds — fixed rule IS the policy (L89 holdout confirm)")
else:
    verdict = (f"NO-GO on fresh: G1={G1} G2a={G2a} G3={G3} G4={G4} — "
               "2-feature class closes; C4b/C4c stand; L80 final pending Bill")

out = dict(
    meta=dict(census=CEN, fresh=FRESH, base=BASE, latch=LATCH, fb=FB,
              drive_on=4800, nodes=int(n), edges=len(gsrc),
              entrain_mass=entrain_mass, winner=winner, runner=runner,
              n_rules=len(rules2), n_census_clear=n_clear),
    anchors=anchors_ok, picks_match_phase1=picks_match,
    first_div=c0f_fd, dm=dm_lat, fresh_degenerate=degen_fresh,
    census=score(pick_cen, CEN), fresh=fr_score, runner_fresh=runner_fr,
    feats_fresh=feats_fr, picks_fresh=pick_fr,
    gates=dict(G1=G1, G2a=G2a, G3=G3, G4=G4),
    verdict=verdict,
    cells={a: {str(s): cells2[a][str(s)] for s in CEN + FRESH} for a in ARMS2})
json.dump(out, open("l88/results_l88.json", "w"), indent=1)
log(f"census k={cen_score['k']} s1={cen_score['seg1_mean']}"
    f" | fresh k={fr_score['k']} wilson={fr_score['wilson']}"
    f" s1={fr_score['seg1_mean']} lock={fr_score['n_lock']}"
    f" ratio_max={fr_score['ratio_max']}")
log(f"VERDICT {verdict}")
log(f"done {time.time()-t0:.0f}s -> l88/results_l88.json")
