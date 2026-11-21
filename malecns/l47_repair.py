"""L47: repair-after-stop — L46's spec line made a measurement.

L46: a 20-s stop on a deeply-entrained cord (h40) leaves the L45b census
state SL+|SR- for >=120 s (no recovery) while the entrained STATE persists
(0.7 Hz memory, CPG core recruited). Test the L42 re-entrain restart AS the
repair primitive: norepair / rep0 (entrain [6000,8000)) / rep60 (deferred
[12000,14000)). Machinery l46-verbatim except the per-arm DRIVE TABLE
(L39v1/L43v1 wiring lesson). PREREG l47/PREREG.md, written first.

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
STOP0, STOPD = 4000, 2000          # stop [4000,6000) = 20 s @ -8
POST = 12000                       # post window to 18000 (l46-identical)
WIN = STOP0 + STOPD + POST         # 18000
ENT_AMP, ENT_F = 0.3, 0.7
REL_AMP = -8.0
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05       # l32 arm-A frozen
CORE_TYPES = ("IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012")
PLAN = {  # per-arm drive table: (lo, hi, kind); ent = mech 0.7 Hz, stop = DNg88
    "norepair": [(0, STOP0, "ent"), (STOP0, STOP0 + STOPD, "stop")],
    "rep0": [(0, STOP0, "ent"), (STOP0, STOP0 + STOPD, "stop"),
             (STOP0 + STOPD, STOP0 + STOPD + 2000, "ent")],
    "rep60": [(0, STOP0, "ent"), (STOP0, STOP0 + STOPD, "stop"),
              (12000, 14000, "ent")],
}
ARMS = list(PLAN)
LATE_WIN = {"norepair": (12000, 18000), "rep0": (10000, 18000),
            "rep60": (16000, 18000)}
REP_ON = {"rep0": STOP0 + STOPD, "rep60": 12000}
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l32/l34/l39/l41-l46 verbatim) ----------
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
REL = np.where(ltyp == "DNg88")[0]
assert len(REL) > 0

CORE = {ct: np.where(ltyp == ct)[0] for ct in CORE_TYPES}
core_counts = {ct: len(v) for ct, v in CORE.items()}
for ct, c in core_counts.items():
    assert c > 0, ct
core_all = np.concatenate([CORE[ct] for ct in CORE_TYPES])
log(f"sub {n:,}/{len(gsrc):,} | mech {len(mech)} | DNg88 {len(REL)} | "
    f"core {core_counts} pool {len(core_all)}")

# global 0.7 Hz phase (settle prefix + win) — never stops, drives consult it
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * ENT_F * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * ENT_F * DT
    PHI[i] = ph

# per-arm drive table -> boolean masks (L39v1/L43v1: no inline conditionals)
ENT_ON = {a: np.zeros(WIN, bool) for a in ARMS}
ST_ON = {a: np.zeros(WIN, bool) for a in ARMS}
for a, plan in PLAN.items():
    for lo, hi, kind in plan:
        (ENT_ON if kind == "ent" else ST_ON)[a][lo:hi] = True


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
    x88 = {a: np.zeros(WIN, np.float32) for a in ARMS}
    xc = {a: np.zeros(WIN, np.float32) for a in ARMS}

    def step_all(k):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        ph_k = math.sin(PHI[k]) if k >= 0 else 0.0
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if k >= 0 and ENT_ON[a][k]:
                drive[mech, 0] = drive[mech, 0] + ENT_AMP * (0.5 + 0.5 * ph_k)
            if k >= 0 and ST_ON[a][k]:
                drive[REL, 0] = drive[REL, 0] + REL_AMP
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
            x88[a][i] = X[a][REL].mean()
            xc[a][i] = X[a][core_all].mean()
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                mm=mm, tr=tr, x88=x88, xc=xc)


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# raw checkpoint BEFORE analysis, ALL pools the analysis reads (L45a)
np.savez_compressed(
    "l47/raw_l47.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")},
    **{f"x88_{a}_{s}": res[str(s)]["x88"][a] for a in ARMS for s in SEEDS},
    **{f"xc_{a}_{s}": res[str(s)]["xc"][a] for a in ARMS for s in SEEDS})
log("raw_l47.npz checkpointed")

# ---------------- C0: bit-identity anchors ----------------
l46 = np.load("l46/traces_l46.npz")
c0_full, c0_prefix = {}, {}
for s in SEEDS:
    ref = l46[f"mm_h40_{s}"]
    cur = res[str(s)]["mm"]["norepair"]
    c0_full[str(s)] = float(np.abs(cur - ref).max())
for a in ("rep0", "rep60"):
    for s in SEEDS:
        c0_prefix[f"{a}_{s}"] = float(
            np.abs(res[str(s)]["mm"][a][:STOP0 + STOPD]
                   - res[str(s)]["mm"]["norepair"][:STOP0 + STOPD]).max())
c0 = dict(full_vs_l46h40=c0_full, prefix_vs_norepair=c0_prefix,
          full_exact=all(v == 0.0 for v in c0_full.values()),
          prefix_exact=all(v == 0.0 for v in c0_prefix.values()))

# ---------------- analysis ----------------
TS = np.arange(499, WIN, 10)


def arm_metrics(a, s):
    r = res[s]
    fL, fR, eL, eR = (r["tr"][a][c] for c in ("fL", "fR", "eL", "eR"))
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    SP = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SP[t] = S_of(fL[t - 499:t + 1] + fR[t - 499:t + 1],
                     eL[t - 499:t + 1] + eR[t - 499:t + 1])
    lo, hi = LATE_WIN[a]
    q = (TS >= lo) & (TS < hi)

    def med(arr):
        return round(float(np.nanmedian(arr[TS[q]])), 3)

    both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
    duty_both = float(np.nanmean(both))
    lat = None
    if a in REP_ON:
        on = REP_ON[a]
        for t in TS[TS >= on]:
            if SL[t] >= 0.25 and SR[t] >= 0.25:
                lat = int(t - on)
                break
    late_r, f_late = rhythm2(r["mm"][a][lo:hi])
    # during-repair pooled/per-side (rep arms only)
    d = {}
    if a in REP_ON:
        on = REP_ON[a]
        qd = (TS >= on) & (TS < on + 2000)
        d = dict(SL_dur=round(float(np.nanmedian(SL[TS[qd]])), 3),
                 SR_dur=round(float(np.nanmedian(SR[TS[qd]])), 3),
                 SP_dur=round(float(np.nanmedian(SP[TS[qd]])), 3))
    return (dict(
        SL_med_late=med(SL), SR_med_late=med(SR), SP_med_late=med(SP),
        duty_both_late=round(duty_both, 3),
        lat_both_s=round(lat * DT, 2) if lat is not None else None,
        ratio_late=round(late_r, 1), f_late=round(f_late, 3),
        core_late=round(float(r["xc"][a][lo:hi].mean()), 4),
        x88min=round(float(r["x88"][a][STOP0:STOP0 + STOPD].min()), 3), **d),
        dict(SL=SL, SR=SR, SP=SP))


tbl, SIDE = {}, {}
for a in ARMS:
    tbl[a] = {}
    for s in SEEDS:
        m, side = arm_metrics(a, str(s))
        tbl[a][str(s)] = m
        SIDE[f"SL_{a}_{s}"] = side["SL"]
        SIDE[f"SR_{a}_{s}"] = side["SR"]

# C1: repair lands
dm = {}
for a in ("rep0", "rep60"):
    on = REP_ON[a]
    dm[a] = {str(s): float(np.abs(res[str(s)]["mm"][a]
                                  - res[str(s)]["mm"]["norepair"])[on:on + 2000].max())
             for s in SEEDS}
c1 = dict(dm=dm, x88_unpin=all(tbl[a][str(s)]["x88min"] < 0.5
                               for a in ARMS for s in SEEDS),
          pass_=all(v > 0 for a in dm for v in dm[a].values())
          and all(tbl[a][str(s)]["x88min"] < 0.5 for a in ARMS for s in SEEDS))


# C2: per-side verdict per PREREG
def c2_arm(a):
    rows = [tbl[a][str(s)]["SL_med_late"] >= 0.25
            and tbl[a][str(s)]["SR_med_late"] >= 0.25 for s in SEEDS]
    pooled = [tbl[a][str(s)]["SP_med_late"] >= 0.25 for s in SEEDS]
    if sum(rows) == 3:
        return "REPAIRED"
    if sum(pooled) == 3:
        return "PARTIAL-POOLED"
    return "NOT-REPAIRED"


c2 = {a: c2_arm(a) for a in ARMS}

# C3: state conservation vs norepair anchors
c3 = dict(f_late={a: {str(s): tbl[a][str(s)]["f_late"] for s in SEEDS}
                  for a in ARMS},
          core={a: {str(s): tbl[a][str(s)]["core_late"] for s in SEEDS}
                for a in ARMS},
          f_norepair_anchor=tbl["norepair"]["11"]["f_late"],
          core_norepair_anchor=round(
              float(np.mean([tbl["norepair"][str(s)]["core_late"]
                             for s in SEEDS])), 4))
c4 = {a: {str(s): tbl[a][str(s)]["lat_both_s"] for s in SEEDS}
      for a in ("rep0", "rep60")}

verdict = dict(C0=c0, C1=c1, C2=c2, C3=c3, C4=c4)
log("VERDICT " + json.dumps(verdict)[:2600])

np.savez_compressed("l47/traces_l47.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
                       for a in ARMS for s in SEEDS},
                    **{f"xc_{a}_{s}": res[str(s)]["xc"][a]
                       for a in ARMS for s in SEEDS},
                    **SIDE)
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, seeds=SEEDS,
                      ent_amp=ENT_AMP, ent_f=ENT_F, rel_amp=REL_AMP,
                      stop0=STOP0, stopd=STOPD, plan={k: list(map(list, v))
                                                      for k, v in PLAN.items()},
                      late_win=LATE_WIN, nodes=int(n), edges=len(gsrc),
                      core_counts=core_counts),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            table=tbl, verdict=verdict)
json.dump(dump, open("l47/results_l47.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l47/results_l47.json")
