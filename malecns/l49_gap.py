"""L49: drive-gap-tolerance — the scheduling slack curve (LANE.md ideas-24).

Arms (l48-verbatim machinery, no stop, no DNg88 — a gap is pure drive-off):
shared h40 prefix ent-0.7Hz-amp.3 [0,4000); then cont (drive never off) or
gap{5,10,20,40,80}s drive-off, then drive back on to 18000. PREREG first:
l49/PREREG.md. Raw npz checkpoint BEFORE analysis (L45a lesson).

CPU-only; no live changes.
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
HIST = 4000                          # h40 shared history [0,4000)
WIN = 18000                          # 180 s: 40 history + 80 max gap + 60 resume
ENT_AMP, ENT_F = 0.3, 0.7
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05         # l32 arm-A frozen
CORE_TYPES = ("IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012")
GAP = {"gap5": 500, "gap10": 1000, "gap20": 2000, "gap40": 4000, "gap80": 8000}
ARMS = ["cont"] + list(GAP)
RESUME = 6000                        # 60 s resume window
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l32/l34/l39-l48 verbatim) ----------
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
lsup, ltyp, lside, lcls = sup[keep], typ[keep], side[keep], cls[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(str(nt_names[keep][i]), 0.3) for i in range(n)],
                 np.float32)
lsrc, ldst = loc[gsrc], loc[gdst]
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

CORE = {ct: np.where(ltyp == ct)[0] for ct in CORE_TYPES}
core_counts = {ct: len(v) for ct, v in CORE.items()}
for ct, c in core_counts.items():
    assert c > 0, ct
core_all = np.concatenate([CORE[ct] for ct in CORE_TYPES])
log(f"sub {n:,}/{len(gsrc):,} | mech {len(mech)} | core {core_counts} "
    f"pool {len(core_all)}")

# global 0.7 Hz phase (settle prefix + win) — never stops, drives consult it
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * ENT_F * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * ENT_F * DT
    PHI[i] = ph

# per-arm AMP table (no inline conditionals in the step loop — L39v1/L43v1).
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
AMPA["cont"][:] = ENT_AMP
for a, gst in GAP.items():
    AMPA[a][:HIST] = ENT_AMP
    AMPA[a][HIST + gst:] = ENT_AMP
    # gap span [HIST, HIST+gst) stays 0.0
for a in GAP:
    gst = GAP[a]
    assert AMPA[a][HIST + gst - 1] == 0.0 and AMPA[a][HIST + gst] == ENT_AMP
    assert (AMPA[a][HIST:HIST + gst] == 0.0).all()
log("amp table: " + "; ".join(
    f"{a} gap[{HIST},{HIST + GAP[a]}) off, resume at {(HIST + GAP[a]) * DT:.0f}s"
    for a in GAP))


def rhythm2(x, lo=0.5, hi=10.0):
    x = x - x.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    b = (fr >= lo) & (fr <= hi)
    pb, fb = ps[b], fr[b]
    if pb.max() <= 0:
        return 0.0, 0.0
    i = int(np.argmax(pb))
    return float(pb[i] / max(np.median(pb), 1e-30)), float(fb[i])


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
    SIGS = ("fL", "fR", "eL", "eR")
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    xc = {a: np.zeros(WIN, np.float32) for a in ARMS}

    def step_all(k):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        ph_k = math.sin(PHI[k]) if k >= 0 else 0.0
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            amp_k = AMPA[a][k] if k >= 0 else (ENT_AMP if k < 0 else 0.0)
            if k >= 0 and amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + float(amp_k) * (0.5 + 0.5 * ph_k)
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
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                mm=mm, tr=tr, xc=xc)


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# raw checkpoint BEFORE analysis, ALL pools the registered metrics read
np.savez_compressed(
    "l49/raw_l49.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")},
    **{f"xc_{a}_{s}": res[str(s)]["xc"][a] for a in ARMS for s in SEEDS})
log("raw_l49.npz checkpointed")

# ---------------- C0: bit-identity anchors ----------------
l48 = np.load("l48/traces_l48.npz")
c0 = dict(prefix_vs_l48={}, pairwise={})
for s in SEEDS:
    for a in ARMS:
        c0["prefix_vs_l48"][f"{a}_{s}"] = float(
            np.abs(res[str(s)]["mm"][a][:HIST] - l48[f"mm_norepair_{s}"][:HIST]).max())
for s in SEEDS:
    for a in GAP:
        c0["pairwise"][f"{a}_vs_cont_{s}"] = float(
            np.abs(res[str(s)]["mm"][a][:HIST] - res[str(s)]["mm"]["cont"][:HIST]).max())
c0["prefix_exact"] = all(v == 0.0 for v in c0["prefix_vs_l48"].values())
c0["pairwise_exact"] = all(v == 0.0 for v in c0["pairwise"].values())

# ---------------- C1: drive wiring ----------------
c1 = dict(amp_asserts=True, first_div={}, dm_gap={})
for a in GAP:
    gst = GAP[a]
    for s in SEEDS:
        d = np.abs(res[str(s)]["mm"][a] - res[str(s)]["mm"]["cont"])
        fd = int(np.argmax(d > 0)) if (d > 0).any() else -1
        c1["first_div"][f"{a}_{s}"] = fd
        c1["dm_gap"][f"{a}_{s}"] = float(d[HIST:HIST + gst].max())
c1["pass_"] = (all(v == HIST for v in c1["first_div"].values())
               and all(v > 0 for v in c1["dm_gap"].values()))

# ---------------- analysis ----------------
TS = np.arange(499, WIN, 10)


def band(f):
    return "0.7-band" if f <= 1.0 else ("1.4-band" if f <= 1.8 else "fast")


SIDE = {}
SM = {}   # per arm/seed rolling S arrays


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    r = res[s]
    fL, fR, eL, eR = (r["tr"][a][c] for c in ("fL", "fR", "eL", "eR"))
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    SM[(a, s)] = (SL, SR)
    SIDE[f"SL_{a}_{s}"], SIDE[f"SR_{a}_{s}"] = SL, SR
    return SL, SR


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    if not q.any():
        return None
    return round(float(np.nanmedian(arr[TS[q]])), 3)


def sustained_from(arr_ok, t_start, t_end, hold=500, want=True):
    """first TS sample t in [t_start,t_end) where arr_ok holds on [t,t+hold]"""
    for t in TS[TS >= t_start]:
        if t >= t_end:
            break
        w = TS[(TS >= t) & (TS <= t + hold)]
        if len(w) and bool(np.all(arr_ok[w] == want)):
            return int(t)
    return None


tbl = {"cont": {}}
for s in SEEDS:
    SL, SR = s_arrays("cont", str(s))
    q = (TS >= HIST) & (TS < WIN)
    both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
    f_c, _ = rhythm2(res[str(s)]["mm"]["cont"][HIST:WIN])
    tbl["cont"][str(s)] = dict(
        duty_both=round(float(np.nanmean(both)), 3),
        SL_med=wmed(HIST, WIN, SL), SR_med=wmed(HIST, WIN, SR),
        f=round(f_c, 3), core=round(float(res[str(s)]["xc"]["cont"][HIST:WIN].mean()), 4))

for a in GAP:
    gst = GAP[a]
    g1 = HIST + gst
    tbl[a] = {}
    for s in SEEDS:
        SL, SR = s_arrays(a, str(s))
        both_ts = (SL >= 0.25) & (SR >= 0.25)
        ok_gap = np.zeros(WIN, bool)
        ok_gap[TS] = both_ts[TS]
        eL_med, eR_med = wmed(g1 - 500, g1, SL), wmed(g1 - 500, g1, SR)
        held = (eL_med is not None and eR_med is not None
                and eL_med >= 0.25 and eR_med >= 0.25)
        d = dict(SL_end=eL_med, SR_end=eR_med, held=bool(held))
        if gst >= 1000:
            d.update(SL_h1=wmed(HIST, HIST + gst // 2, SL),
                     SR_h1=wmed(HIST, HIST + gst // 2, SR),
                     SL_h2=wmed(HIST + gst // 2, g1, SL),
                     SR_h2=wmed(HIST + gst // 2, g1, SR),
                     f_gap=round(rhythm2(res[str(s)]["mm"][a][HIST:g1])[1], 3))
        # collapse inside gap (sustained 500-step fail), only if not held at end
        tc = sustained_from(ok_gap, HIST + 499, g1, 500, want=False)
        d["t_collapse_s"] = round((tc - HIST) * DT, 2) if tc is not None else None
        # resume window
        rq_lo, rq_hi = g1, min(g1 + RESUME, WIN)
        q = (TS >= rq_lo) & (TS < rq_hi)
        both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
        duty = float(np.nanmean(both))
        lf = sustained_from(ok_gap, rq_lo, rq_hi, 500, want=True)
        ls = sustained_from(ok_gap, rq_lo, rq_hi, 5000, want=True)
        d.update(duty_resume=round(duty, 3),
                 SL_resume=wmed(rq_lo, rq_hi, SL), SR_resume=wmed(rq_lo, rq_hi, SR),
                 lat_first_s=round((lf - g1) * DT, 2) if lf is not None else None,
                 lat_sust5_s=round((ls - g1) * DT, 2) if ls is not None else None,
                 f_resume=round(rhythm2(res[str(s)]["mm"][a][rq_lo:rq_hi])[1], 3),
                 core_end=round(float(res[str(s)]["xc"][a][g1 - 500:g1].mean()), 4),
                 core_resume=round(float(res[str(s)]["xc"][a][rq_lo:rq_hi].mean()), 4))
        # tail (continued drive beyond 60 s resume), if any
        if g1 + RESUME < WIN:
            t_lo, t_hi = g1 + RESUME, WIN
            q = (TS >= t_lo) & (TS < t_hi)
            d.update(duty_tail=round(float(np.nanmean(
                (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25))), 3),
                f_tail=round(rhythm2(res[str(s)]["mm"][a][t_lo:t_hi])[1], 3))
        tbl[a][str(s)] = d

# P0 premise
p0 = dict(pass_=all(tbl["cont"][str(s)]["duty_both"] >= 0.5
                    and tbl["cont"][str(s)]["SL_med"] >= 0.25
                    and tbl["cont"][str(s)]["SR_med"] >= 0.25 for s in SEEDS),
          rows={str(s): tbl["cont"][str(s)] for s in SEEDS})

# C2 slack verdicts
c2 = {}
for a in GAP:
    held = [tbl[a][str(s)]["held"] for s in SEEDS]
    c2[a] = dict(held_n=sum(held),
                 verdict="HELD" if sum(held) == 3 else
                         ("SPLIT" if sum(held) >= 1 else "LOST"))

# C3 resume verdicts
c3 = {}
for a in GAP:
    rows = [tbl[a][str(s)]["duty_resume"] >= 0.5
            and (tbl[a][str(s)]["SL_resume"] or -1) >= 0.25
            and (tbl[a][str(s)]["SR_resume"] or -1) >= 0.25 for s in SEEDS]
    c3[a] = dict(reform_n=sum(rows),
                 verdict="RE-FORMS" if sum(rows) == 3 else
                         ("PARTIAL" if sum(rows) >= 1 else "NOT"))

# C4 slack curve
held_g = [(GAP[a], c2[a]["held_n"]) for a in GAP]
c4 = dict(slack_s=None, curve={str(GAP[a] * DT): c2[a]["held_n"] for a in GAP},
          resume={str(GAP[a] * DT): c3[a]["verdict"] for a in GAP})
safe = [g for g, hn in sorted(held_g) if hn == 3]
c4["slack_s"] = max(safe) * DT if safe else 0

verdict = dict(P0=p0, C0=c0, C1=c1, C2=c2, C3=c3, C4=c4)
log("VERDICT " + json.dumps(verdict)[:2600])

np.savez_compressed("l49/traces_l49.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
                       for a in ARMS for s in SEEDS},
                    **{f"xc_{a}_{s}": res[str(s)]["xc"][a]
                       for a in ARMS for s in SEEDS},
                    **SIDE)
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, seeds=SEEDS,
                      ent_amp=ENT_AMP, ent_f=ENT_F, hist=HIST, gap=GAP,
                      resume=RESUME, nodes=int(n), edges=len(gsrc),
                      core_counts=core_counts),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            table=tbl, verdict=verdict)
json.dump(dump, open("l49/results_l49.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l49/results_l49.json")
