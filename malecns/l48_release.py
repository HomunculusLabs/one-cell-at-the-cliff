"""L48: repair-release-shaping — L47's release lottery, shaped.

Arms (l47-verbatim machinery, WIN extended to 24000): shared prefix
ent-0.7Hz-amp.3 [0,4000) + stop DNg88 -8 [4000,6000); then per-arm release:
rep0 hard-off @8000 (anchor), ramp10/30/60 (linear amp fade), dwell60/120
(full-amp dwell then hard-off), norepair (anchor, self-repair floor probe
out to 220 s post-stop). PREREG l48/PREREG.md, written first.

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
WIN = 24000                        # 240 s; longest release-off = 18000 (dwell120)
ENT_AMP, ENT_F = 0.3, 0.7
REL_AMP = -8.0
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05       # l32 arm-A frozen
CORE_TYPES = ("IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012")
RAMP = {"ramp10": 1000, "ramp30": 3000, "ramp60": 6000}   # steps of fade
DWELL = {"dwell60": 12000, "dwell120": 18000}             # hard-off step
ARMS = ["norepair", "rep0"] + list(RAMP) + list(DWELL)
OFF = {"rep0": 8000, "ramp10": 9000, "ramp30": 11000, "ramp60": 14000,
       "dwell60": 12000, "dwell120": 18000}
POSTLEN = 6000
DUR = (6000, 8000)                 # full-amp phase, identical in every treatment arm
LATE_NOP = (18000, 24000)          # norepair floor-probe window
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l32/l34/l39-l47 verbatim) ----------
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

# per-arm AMP profile (ent = full amp; ramp = linear fade to 0) + stop mask.
# No inline conditionals in the step loop (L39v1/L43v1 wiring lesson).
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
ST_ON = {a: np.zeros(WIN, bool) for a in ARMS}
for a in ARMS:
    AMPA[a][:STOP0] = ENT_AMP                      # shared history [0,4000)
    ST_ON[a][STOP0:STOP0 + STOPD] = True           # shared stop [4000,6000)
    if a != "norepair":                            # norepair: nothing after stop
        AMPA[a][DUR[0]:DUR[1]] = ENT_AMP           # full-amp repair phase
for a, rl in RAMP.items():                          # fade [8000, 8000+rl)
    rr = np.arange(rl)
    AMPA[a][DUR[1]:DUR[1] + rl] = ENT_AMP * (1.0 - rr / rl)
for a, off in DWELL.items():                        # full amp to hard-off
    AMPA[a][DUR[1]:off] = ENT_AMP

log("amp tails: " + "; ".join(
    f"{a}<{OFF[a]}> {AMPA[a][OFF[a]-1]:.3f}->{AMPA[a][OFF[a]]:.3f}" for a in OFF))


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
            amp_k = AMPA[a][k] if k >= 0 else (ENT_AMP if k < 0 else 0.0)
            if k >= 0 and amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + float(amp_k) * (0.5 + 0.5 * ph_k)
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

# raw checkpoint BEFORE analysis, ALL pools the analysis reads (L45a lesson)
np.savez_compressed(
    "l48/raw_l48.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")},
    **{f"x88_{a}_{s}": res[str(s)]["x88"][a] for a in ARMS for s in SEEDS},
    **{f"xc_{a}_{s}": res[str(s)]["xc"][a] for a in ARMS for s in SEEDS})
log("raw_l48.npz checkpointed")

# ---------------- C0: bit-identity anchors ----------------
l47 = np.load("l47/traces_l47.npz")
c0 = dict(full={}, prefix_norepair={}, prefix_rep0={})
for s in SEEDS:
    for a in ("norepair", "rep0"):
        c0["full"][f"{a}_{s}"] = float(
            np.abs(res[str(s)]["mm"][a][:18000] - l47[f"mm_{a}_{s}"]).max())
for a in list(RAMP) + list(DWELL):
    for s in SEEDS:
        c0["prefix_norepair"][f"{a}_{s}"] = float(
            np.abs(res[str(s)]["mm"][a][:STOP0 + STOPD]
                   - res[str(s)]["mm"]["norepair"][:STOP0 + STOPD]).max())
        c0["prefix_rep0"][f"{a}_{s}"] = float(
            np.abs(res[str(s)]["mm"][a][:DUR[1]]
                   - res[str(s)]["mm"]["rep0"][:DUR[1]]).max())
c0["full_exact"] = all(v == 0.0 for v in c0["full"].values())
c0["prefix_exact"] = all(v == 0.0 for v in c0["prefix_norepair"].values())
and_all = all(v == 0.0 for v in c0["prefix_rep0"].values())
c0["prefix_exact"] = bool(c0["prefix_exact"] and and_all)

# ---------------- analysis ----------------
TS = np.arange(499, WIN, 10)


def band(f):
    return "0.7-band" if f <= 1.0 else ("1.4-band" if f <= 1.8 else "fast")


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

    def wmed(lo, hi, arr):
        q = (TS >= lo) & (TS < hi)
        return round(float(np.nanmedian(arr[TS[q]])), 3)

    lo, hi = (OFF[a], OFF[a] + POSTLEN) if a in OFF else LATE_NOP
    q = (TS >= lo) & (TS < hi)
    both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
    duty = float(np.nanmean(both))
    lat = None
    if a in OFF:
        for t in TS[TS >= OFF[a]]:
            if SL[t] >= 0.25 and SR[t] >= 0.25:
                lat = int(t - OFF[a])
                break
    r_dur, f_dur = rhythm2(r["mm"][a][DUR[0]:DUR[1]])
    r_post, f_post = rhythm2(r["mm"][a][lo:hi])
    d = dict(SL_dur=wmed(*DUR, SL), SR_dur=wmed(*DUR, SR))
    if a in RAMP:
        rl = RAMP[a]
        d.update(SL_ramp=wmed(DUR[1], DUR[1] + rl, SL),
                 SR_ramp=wmed(DUR[1], DUR[1] + rl, SR))
    st = f"{band(f_post)} SL{'+' if wmed(lo, hi, SL) >= 0 else '-'}" \
         f"|SR{'+' if wmed(lo, hi, SR) >= 0 else '-'}"
    return (dict(
        SL_med_post=wmed(lo, hi, SL), SR_med_post=wmed(lo, hi, SR),
        SP_med_post=wmed(lo, hi, SP), duty_both_post=round(duty, 3),
        lat_both_s=round(lat * DT, 2) if lat is not None else None,
        f_dur=round(f_dur, 3), f_post=round(f_post, 3),
        hop=round(f_post - f_dur, 3),
        core_dur=round(float(r["xc"][a][DUR[0]:DUR[1]].mean()), 4),
        core_post=round(float(r["xc"][a][lo:hi].mean()), 4),
        ratio_post=round(r_post, 1), state=st,
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

# C1: drive lands during DUR (vs norepair, which has none)
dm = {}
for a in ARMS:
    if a != "norepair":
        dm[a] = {str(s): float(np.abs(res[str(s)]["mm"][a]
                                     - res[str(s)]["mm"]["norepair"])[DUR[0]:DUR[1]].max())
                 for s in SEEDS}
c1 = dict(dm=dm, x88_unpin=all(tbl[a][str(s)]["x88min"] < 0.5
                               for a in ARMS for s in SEEDS),
          pass_=all(v > 0 for a in dm for v in dm[a].values()))


# C2 per PREREG
def c2_arm(a):
    rows = [tbl[a][str(s)]["SL_med_post"] >= 0.25
            and tbl[a][str(s)]["SR_med_post"] >= 0.25
            and tbl[a][str(s)]["duty_both_post"] >= 0.5 for s in SEEDS]
    pooled = [tbl[a][str(s)]["SP_med_post"] >= 0.25 for s in SEEDS]
    if sum(rows) == 3:
        return "REPAIRED"
    if sum(pooled) == 3:
        return "PARTIAL-POOLED"
    return "NOT-REPAIRED"


c2 = {a: c2_arm(a) for a in ARMS}
c3 = dict(states={a: {str(s): tbl[a][str(s)]["state"] for s in SEEDS}
                  for a in ARMS},
          f_post={a: {str(s): tbl[a][str(s)]["f_post"] for s in SEEDS}
                  for a in ARMS},
          core_post={a: {str(s): tbl[a][str(s)]["core_post"] for s in SEEDS}
                     for a in ARMS},
          f_memory_anchor=tbl["norepair"]["11"]["f_post"],
          core_norepair_anchor=round(
              float(np.mean([tbl["norepair"][str(s)]["core_post"]
                             for s in SEEDS])), 4))
c4 = dict(lat={a: {str(s): tbl[a][str(s)]["lat_both_s"] for s in SEEDS}
               for a in OFF},
          hop={a: {str(s): tbl[a][str(s)]["hop"] for s in SEEDS} for a in OFF},
          f_dur_anchor={a: {str(s): tbl[a][str(s)]["f_dur"] for s in SEEDS}
                        for a in OFF})

verdict = dict(C0=c0, C1=c1, C2=c2, C3=c3, C4=c4)
log("VERDICT " + json.dumps(verdict)[:3000])

np.savez_compressed("l48/traces_l48.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
                       for a in ARMS for s in SEEDS},
                    **{f"xc_{a}_{s}": res[str(s)]["xc"][a]
                       for a in ARMS for s in SEEDS},
                    **SIDE)
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, seeds=SEEDS,
                      ent_amp=ENT_AMP, ent_f=ENT_F, rel_amp=REL_AMP,
                      stop0=STOP0, stopd=STOPD, off=OFF, ramp=RAMP, dwell=DWELL,
                      postlen=POSTLEN, dur=list(DUR), late_nop=list(LATE_NOP),
                      nodes=int(n), edges=len(gsrc), core_counts=core_counts),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            table=tbl, verdict=verdict)
json.dump(dump, open("l48/results_l48.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l48/results_l48.json")
