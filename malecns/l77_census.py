"""L77: echo-on-endgame-census (LANE.md ideas-38). PREREG l77/PREREG.md FIRST.

The l59 hybrid + hynohop endgame schedules at census n=16, WITH the l66
content-cell echo (g .1, sign -, delay 5) on: 4 arms (twin, twin, +fb, +fb).
Machinery l59_ensemble.py verbatim; echo wiring l66_census.py verbatim.
CPU-only; raw npz checkpoint BEFORE analysis; no live changes.
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
FB = dict(gfb=.1, delay=5, sign=-1.0)          # l66 content cell verbatim
ARMS = ["hynohop", "hybrid", "hynohop_fb", "hybrid_fb"]
FB_ARMS = ["hynohop_fb", "hybrid_fb"]
TWINS = {"hynohop_fb": "hynohop", "hybrid_fb": "hybrid"}
SIGS = ("fL", "fR", "eL", "eR")
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l59/l66 verbatim) ----------
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
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in SIGS])   # l66-verbatim
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

# ---------- per-arm AMPA / HOPA tables (l59 write-time asserts) ----------
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
    HOPA["hybrid_fb"][o:o + HOP_VW] = True      # same volleys for the fb twin

assert all(np.array_equal(AMPA[a], AMPA["hynohop"]) for a in ARMS)
for seg0, segend, f in SEGB:
    seg = AMPA["hynohop"][seg0:seg0 + SEG]
    if f == 0.7:
        assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
        assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
        assert (seg[1800:2000] == ENT_AMP).all()
    else:
        assert (AMPA["hynohop"][seg0:segend] == ENT_AMP).all()
assert not HOPA["hynohop"].any() and not HOPA["hynohop_fb"].any()
assert HOPA["hybrid"].sum() == 2 * HOP_VW
assert np.array_equal(HOPA["hybrid"], HOPA["hybrid_fb"])
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
assert all(DRIVE_ON[a] == 4800 for a in ARMS), DRIVE_ON
log("drive-on 48.0s all arms | tables asserted")


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


# ---------- rollouts (l59 step loop + l66 echo line) ----------
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
    mA = {a: np.zeros(WIN, np.float32) for a in FB_ARMS}

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
            if a in FB_ARMS and k >= FB["delay"]:
                drive[mech, 0] += (FB["gfb"] * FB["sign"]
                                   * float(mA[a][k - FB["delay"]]))
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
            if a in FB_ARMS:
                mA[a][i] = X[a][ANTAG].mean()
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                          mm=mm, tr=tr, mA=mA)
    np.savez_compressed(
        "l77/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l77/raw_l77.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS},
    **{f"mA_{a}_{s}": res[str(s)]["mA"][a] for a in FB_ARMS for s in SEEDS})

# ---------------- anchors (enumerated keys ONLY) ----------------
z59 = np.load("l59/raw_l59.npz")
z66 = np.load("l66/raw_l66.npz")
c0a, c0b, c0x = {}, {}, {}
for s in ANCHOR_SEEDS:
    c0a[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hynohop"] - z59[f"mm_hynohop_{s}"][:WIN]).max())
    c0b[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hybrid"] - z59[f"mm_hybrid_{s}"][:WIN]).max())
    c0x[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hynohop_fb"] - z66[f"mm_g01_d05_m_{s}"][:WIN]).max())
    for c in SIGS:
        c0a[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hynohop"][c] - z59[f"{c}_hynohop_{s}"][:WIN]).max())
        c0b[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hybrid"][c] - z59[f"{c}_hybrid_{s}"][:WIN]).max())
        c0x[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hynohop_fb"][c]
            - z66[f"{c}_g01_d05_m_{s}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())
c0b_pass = all(v == 0.0 for v in c0b.values())
c0x_pass = all(v == 0.0 for v in c0x.values())

dm, first_div = {}, {}
for fb in FB_ARMS:
    twin = TWINS[fb]
    for s in SEEDS:
        m = res[str(s)]
        diffs = np.concatenate(
            [np.abs(m["mm"][fb] - m["mm"][twin])]
            + [np.abs(m["tr"][fb][c] - m["tr"][twin][c]) for c in SIGS])
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        first_div[f"{fb}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{fb}_{s}"] = round(float(diffs.max()), 5)
wired_dead = [k for k, v in dm.items() if v == 0.0]
c0p_ok = (not wired_dead
          and all(first_div[f"{fb}_{s}"] == FB["delay"]
                  for fb in FB_ARMS for s in SEEDS))
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
log(f"C0a {c0a_pass} | C0b {c0b_pass} | C0x l66-fb {c0x_pass} | C0P {c0p_ok}"
    f" | C1 {c1} | wired_dead {len(wired_dead)}")

# ---------------- analysis (l59 cells machinery verbatim) ----------------
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


# ---------------- P3 drive budget ----------------
on_steps = np.where(AMPA["hynohop"] > 0)[0]
sin_on = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in on_steps])
entrain_mass = float(ENT_AMP * sin_on.sum())           # per mech cell
budget = {}
for fb in FB_ARMS:
    em = [float(FB["gfb"] * res[str(s)]["mA"][fb][:WIN - FB["delay"]].sum())
          for s in SEEDS]
    budget[fb] = dict(echo_mass_mean=round(float(np.mean(em)), 4),
                      echo_mass_min=round(float(np.min(em)), 4),
                      echo_mass_max=round(float(np.max(em)), 4),
                      entrain_mass=round(entrain_mass, 1),
                      ratio_mean=round(float(np.mean(em)) / entrain_mass, 4),
                      echo_amp_mean=round(float(np.mean(
                          [res[str(s)]["mA"][fb][:WIN - FB["delay"]].mean()
                           for s in SEEDS])) * FB["gfb"], 5))
log(f"P3 budget {json.dumps(budget)}")


# ---------------- registered reads ----------------
def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


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
        p_ge_half=k_gate, p_ge_half_wilson=wilson(k_gate, len(SEEDS)),
        seg1=[round(float(v), 3) for v in seg1],
        seg1_mean=round(float(seg1.mean()), 3),
        seg1_err_le01=int((seg1e <= .01).sum()),
        seg1_err=[round(float(v), 4) for v in seg1e],
        seg_err_means=[round(float(np.mean(
            [cells[a][str(s)]["segs"][i]["err"] for s in SEEDS])), 4)
            for i in range(3)],
        duty07_mean=round(float(d07.mean()), 3),
        seg_SL_means=[round(float(np.mean([
            cells[a][str(s)]["segs"][i]["SL"] for s in SEEDS
            if cells[a][str(s)]["segs"][i]["SL"] is not None])), 3)
            for i in range(3)],
        seg_SR_means=[round(float(np.mean([
            cells[a][str(s)]["segs"][i]["SR"] for s in SEEDS
            if cells[a][str(s)]["segs"][i]["SR"] is not None])), 3)
            for i in range(3)])

# P1 paired flips fb vs twin
flips = {}
for fb in FB_ARMS:
    twin = TWINS[fb]
    up = down = both_up = both_dn = 0
    per_seed = []
    for s in SEEDS:
        v_fb = cells[fb][str(s)]["duty_all"]
        v_tw = cells[twin][str(s)]["duty_all"]
        per_seed.append(dict(seed=s, twin=v_tw, fb=v_fb,
                             d=round(v_fb - v_tw, 3)))
        if v_fb >= .5 and v_tw < .5:
            up += 1
        elif v_fb < .5 and v_tw >= .5:
            down += 1
        elif v_fb >= .5:
            both_up += 1
        else:
            both_dn += 1
    flips[fb] = dict(up=up, down=down, both_up=both_up, both_down=both_dn,
                     per_seed=per_seed)

# P4 miss anatomy for fb arms
anatomy = {}
for fb in FB_ARMS:
    sl_owned = sr_owned = both_below = 0
    miss_rows = []
    for s in SEEDS:
        cell = cells[fb][str(s)]
        if cell["duty_all"] >= .5:
            continue
        fails = []
        for si, row in enumerate(cell["segs"]):
            if row["duty"] < .5:
                fails.append(si)
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
    tot = sl_owned + sr_owned + both_below
    anatomy[fb] = dict(
        n_miss=len(miss_rows), sl_owned=sl_owned, sr_owned=sr_owned,
        both_below=both_below,
        sl_share=round(sl_owned / tot, 3) if tot else None, misses=miss_rows)

preds = {}
for fb, label in (("hybrid_fb", "primary"), ("hynohop_fb", "secondary")):
    k = dist[fb]["p_ge_half"]
    lock_ok = dist[fb]["seg1_err_le01"] >= 12
    preds[f"P1_{label}"] = dict(k=k, n=16, biased=bool(k >= 11),
                                wilson=dist[fb]["p_ge_half_wilson"],
                                lock_le01=dist[fb]["seg1_err_le01"],
                                lock_ok=lock_ok,
                                verdict=("BIASED-LEVER" if k >= 11 and lock_ok
                                         else ("TOXIC-BIASED" if k >= 11
                                               else "REAL-NEGATIVE-or-null")))
preds["P2_lock"] = {a: dict(le01=dist[a]["seg1_err_le01"],
                            seg_err_means=dist[a]["seg_err_means"])
                    for a in ARMS}
preds["P4_anatomy"] = {fb: dict(n_miss=anatomy[fb]["n_miss"],
                                sl_share=anatomy[fb]["sl_share"])
                       for fb in FB_ARMS}

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, fb=FB, drive_on=4800,
                     nodes=int(n), edges=len(gsrc),
                     entrain_mass=round(entrain_mass, 1)),
           anchors=dict(c0a_pass=c0a_pass, c0b_pass=c0b_pass, c0x_pass=c0x_pass,
                        c0p_ok=bool(c0p_ok), c1=bool(c1),
                        wired_dead=wired_dead,
                        first_div=first_div, dm=dm),
           distributions=dist, flips=flips, budget=budget,
           anatomy=anatomy, predictions=preds,
           cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS})
json.dump(out, open("l77/results_l77.json", "w"), indent=1)
log("P1 " + json.dumps({k: v for k, v in preds.items() if k.startswith("P1")}))
log(f"k per arm " + json.dumps({a: dist[a]["p_ge_half"] for a in ARMS}))
log(f"pooled means " + json.dumps({a: dist[a]["pooled_mean"] for a in ARMS}))
log(f"duty07 means " + json.dumps({a: dist[a]["duty07_mean"] for a in ARMS}))
log(f"seg1 means " + json.dumps({a: dist[a]["seg1_mean"] for a in ARMS}))
log(f"flips " + json.dumps({fb: {k: v for k, v in flips[fb].items()
                                 if k != 'per_seed'} for fb in FB_ARMS}))
log(f"done {time.time()-t0:.0f}s -> l77/results_l77.json")
