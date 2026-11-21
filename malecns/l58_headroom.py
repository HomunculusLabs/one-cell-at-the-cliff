"""L58: gait-reachable-mass (LANE.md ideas-28) — pre-measure what ANY
controller can own on the hybrid task BEFORE training (L6d-0 form).

(a) family sweep: new chop/amp/drive arms + anchor cells re-derived from
    stored raw npz (l51/l55/l56/l50) — max over FIXED policies.
(b) fork oracle: state-conditioned 1-segment greedy from stored branch arms
    sharing the noise stream (prefix bit-identity asserted).

PREREG l58/PREREG.md written first. Raw npz checkpoint BEFORE analysis.
CPU-only; P1-labeled; no live changes.
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
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05
ENT_AMP = 0.3
ARMS = ["nohop", "off200", "off300", "off500", "off700", "min5seg",
        "fast2", "seg2off", "seg2a2"]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l32/l34/l39/l42/l49/l50/l51 verbatim) ----------
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
lnt = nt_names[keep]

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wa_vals = gw * signA[loc[gsrc]]
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([loc[gdst], loc[gsrc]])).long(),
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
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} | {time.time()-t0:.0f}s")

ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- AMPA tables (write-time asserted, no inline conditionals) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}


def chop_into(arr, seg_lo, amp, on, off):
    c = 0
    while seg_lo + c * (on + off) < seg_lo + SEG:
        lo = seg_lo + c * (on + off)
        arr[lo:min(lo + on, seg_lo + SEG)] = amp
        c += 1


CHOP07 = {"nohop": (500, 400, .3), "off200": (500, 200, .3),
          "off300": (500, 300, .3), "off500": (500, 500, .3),
          "off700": (500, 700, .3), "fast2": (500, 400, .3),
          "seg2off": (500, 400, .3), "seg2a2": (500, 400, .3)}
for a, (on, off, amp) in CHOP07.items():
    for seg_lo, _, f in SEGB:
        if f == 0.7:
            chop_into(AMPA[a], seg_lo, amp, on, off)
for seg_lo, _, f in SEGB:                        # min5seg: 500-on then off
    if f == 0.7:
        AMPA["min5seg"][seg_lo:seg_lo + 500] = ENT_AMP
FAST_AMP = {"nohop": .3, "off200": .3, "off300": .3, "off500": .3, "off700": .3,
            "min5seg": .3, "fast2": .2, "seg2off": .3, "seg2a2": .3}
for a in ARMS:
    if a != "seg2off":
        AMPA[a][2000:4000] = FAST_AMP[a]
AMPA["seg2off"][2000:4000] = .3                  # fast segment stays on
AMPA["seg2off"][4000:6000] = 0.0                 # seg2 fully off
chop_into(AMPA["seg2a2"], 4000, 0.2, 500, 400)   # seg2 chop at amp .2

# table asserts
assert (AMPA["nohop"][:500] == .3).all() and (AMPA["nohop"][500:900] == 0).all()
assert (AMPA["nohop"][900:1400] == .3).all() and (AMPA["nohop"][1400:1800] == 0).all()
assert (AMPA["nohop"][1800:2000] == .3).all()
for a in ("off200", "off300", "off500", "off700", "min5seg"):
    assert (AMPA[a][:500] == .3).all() and (AMPA[a][500:700] == 0).all()
assert AMPA["off200"][700] == .3 and AMPA["off300"][800] == .3
assert AMPA["off500"][1000] == .3 and AMPA["off700"][1200] == .3
assert (AMPA["min5seg"][500:2000] == 0).all() and (AMPA["min5seg"][4500:6000] == 0).all()
assert (AMPA["min5seg"][4000:4500] == .3).all()
assert (AMPA["fast2"][2000:4000] == .2).all()
assert (AMPA["seg2off"][4000:6000] == 0).all() and (AMPA["seg2off"][2000:4000] == .3).all()
assert (AMPA["seg2a2"][4000:4500] == .2).all() and (AMPA["seg2a2"][4500:4900] == 0).all()
fd_expected = {}
for a in ARMS[1:]:
    d = np.nonzero(AMPA[a] != AMPA["nohop"])[0]
    fd_expected[a] = int(d[0]) if len(d) else WIN
assert fd_expected == {"off200": 700, "off300": 800, "off500": 900,
                       "off700": 900, "min5seg": 900, "fast2": 2000,
                       "seg2off": 4000, "seg2a2": 4000}, fd_expected
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
assert DRIVE_ON == {"nohop": 4800, "off200": 5400, "off300": 5200,
                    "off500": 4400, "off700": 4400, "min5seg": 3400,
                    "fast2": 4800, "seg2off": 3600, "seg2a2": 4800}, DRIVE_ON
log("drive-on: " + " | ".join(f"{a} {DRIVE_ON[a]*DT:.1f}s" for a in ARMS))


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
    ratio = float(pb.max() / max(np.median(pb), 1e-30))
    return float(f_hat), ratio


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
    SIGS = ("fL", "fR", "eL", "eR")
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    dm = {a: -1 for a in ARMS[1:]}

    def step_all(k):
        nonlocal settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            ph_k = PHI[k]
        else:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
        sin_ph = math.sin(ph_k)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            amp_k = ENT_AMP if k < 0 else float(AMPA[a][k])
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
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
        if i >= 1:
            for a in ARMS[1:]:
                if dm[a] < 0 and float((X[a] - X["nohop"]).abs().max()) > 1e-6:
                    dm[a] = i
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                dm=dm, mm=mm, tr=tr)


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

np.savez_compressed(
    "l58/raw_l58.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")})
log("raw_l58.npz checkpointed")

# ---------------- C0 anchors ----------------
z55 = np.load("l55/raw_l55.npz")
c0 = {"nohop_mm_vs_l55": max(
    float(np.abs(res[str(s)]["mm"]["nohop"] - z55[f"mm_hynohop_{s}"]).max())
    for s in SEEDS)}
for c in ("fL", "fR", "eL", "eR"):
    c0[f"nohop_{c}_vs_l55"] = max(
        float(np.abs(res[str(s)]["tr"]["nohop"][c] - z55[f"{c}_hynohop_{s}"]).max())
        for s in SEEDS)
fd_ok = all(res[str(s)]["dm"][a] == fd_expected[a]
            for a in ARMS[1:] for s in SEEDS)
c0["fd_expected_match"] = bool(fd_ok)
c0["fd_measured"] = {a: [res[str(s)]["dm"][a] for s in SEEDS] for a in ARMS[1:]}
c0_pass = (all(v == 0.0 for k, v in c0.items() if isinstance(v, float)) and fd_ok)
c1 = dict(af_ok=all(0.01 < res[str(s)]["af"][a] < 0.9
                    for s in SEEDS for a in ARMS),
          af={a: round(float(np.mean([res[str(s)]["af"][a] for s in SEEDS])), 4)
              for a in ARMS})
log(f"C0 pass={c0_pass} | C1 af_ok={c1['af_ok']}")
assert c0_pass and c1["af_ok"], (c0, c1)

# ---------------- analysis helpers (l51 conventions verbatim) ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(key, get_sig):
    if key in SM:
        return SM[key]
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    fL, fR, eL, eR = (get_sig(c) for c in ("fL", "fR", "eL", "eR"))
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    SM[key] = (SL, SR)
    return SL, SR


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    return round(float(np.nanmedian(arr[TS[q]])), 3) if q.any() else None


def seg_table(key, mm_arr, get_sig):
    SL, SR = s_arrays(key, get_sig)
    blocks = []
    for b in range(WIN // BLK):
        f_hat, ratio = dom_freq(mm_arr[b * BLK:(b + 1) * BLK])
        seg = next(i for i, (a0_, b0, _) in enumerate(SEGB)
                   if a0_ <= b * BLK < b0)
        blocks.append(dict(b=b, f=round(f_hat, 3), seg=seg,
                           err=round(abs(f_hat - SEGB[seg][2]), 3)))
    rows = []
    for si, (a0_, b0, tg) in enumerate(SEGB):
        bl = [x for x in blocks if x["seg"] == si]
        err = round(float(np.mean([x["err"] for x in bl[1:]])), 4)
        ttl = next((x["b"] - si * 4 for x in bl[1:] if x["err"] <= 0.10), None)
        lo, hi = a0_ + MEAS0, b0
        q = (TS >= lo) & (TS < hi)
        both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
        rows.append(dict(err=err, ttl=ttl,
                         duty=round(float(np.nanmean(both)), 3),
                         SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                         f=round(dom_freq(mm_arr[a0_:b0])[0], 3)))
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


z51 = np.load("l51/raw_l51.npz")
z56 = np.load("l56/raw_l56.npz")
z56_arms = sorted({k.split("_")[1] for k in z56.files if k.startswith("mm_")})
log(f"l56 arms present: {z56_arms}")
try:
    z50 = np.load("l50/traces_l50.npz")
    has_free_sigs = all(f"fL_free_{s}" in z50.files for s in SEEDS)
except FileNotFoundError:
    z50, has_free_sigs = None, False
log(f"l50 free sigs available: {has_free_sigs}")

PERSEED = {}   # (label, seed) -> seg_table


def get_run(a, s):
    return lambda c: res[str(s)]["tr"][a][c]


def get_z(z, arm, s):
    return lambda c: z[f"{c}_{arm}_{s}"]


def register(label, drive_steps, tables):
    for s, tb in tables.items():
        PERSEED[(label, str(s))] = tb
    per = tables
    row = dict(label=label, drive_on_s=round(drive_steps * DT, 1),
               fast_err={s: per[s]["segs"][1]["err"] for s in per},
               fast_lock=all(per[s]["segs"][1]["err"] <= .01 for s in per),
               duty07={s: per[s]["duty_07"] for s in per},
               duty07_mean=round(float(np.mean([per[s]["duty_07"] for s in per])), 3),
               duty07_min=round(float(min(per[s]["duty_07"] for s in per)), 3),
               pooled={s: per[s]["duty_all"] for s in per},
               pooled_mean=round(float(np.mean([per[s]["duty_all"] for s in per])), 3),
               pooled_min=round(float(min(per[s]["duty_all"] for s in per)), 3),
               seg_duty=[round(float(np.mean([per[s]["segs"][i]["duty"] for s in per])), 3)
                         for i in range(3)])
    return row


FAM = []
for a in ARMS:
    FAM.append(register(a, DRIVE_ON[a],
                        {str(s): seg_table(f"inrun_{a}_{s}",
                                           res[str(s)]["mm"][a], get_run(a, s))
                         for s in SEEDS}))
FAM.append(register("allw", 6400, {
    str(s): seg_table(f"allw_{s}", z51[f"mm_allw_{s}"], get_z(z51, "allw", s))
    for s in SEEDS}))
FAM.append(register("duty58", 4000, {
    str(s): seg_table(f"d58_{s}", z51[f"mm_duty58_{s}"], get_z(z51, "duty58", s))
    for s in SEEDS}))
FAM.append(register("hybrid(2hops)", 4800, {
    str(s): seg_table(f"hyb_{s}", z51[f"mm_hybrid_{s}"], get_z(z51, "hybrid", s))
    for s in SEEDS}))
FAM.append(register("hop2k(entry)", 4800, {
    str(s): seg_table(f"h2k_{s}", z55[f"mm_hop2k_{s}"], get_z(z55, "hop2k", s))
    for s in SEEDS}))
FAM.append(register("hop4k(exit)", 4800, {
    str(s): seg_table(f"h4k_{s}", z55[f"mm_hop4k_{s}"], get_z(z55, "hop4k", s))
    for s in SEEDS}))
FAM.append(register("cond(l55)", 4800, {
    str(s): seg_table(f"cond_{s}", z55[f"mm_cond_{s}"], get_z(z55, "cond", s))
    for s in SEEDS}))
for arm in z56_arms:
    if arm in ("nohop", "hop4k"):
        continue
    FAM.append(register(f"l56:{arm}", 4800, {
        str(s): seg_table(f"l56_{arm}_{s}", z56[f"mm_{arm}_{s}"],
                          get_z(z56, arm, s)) for s in SEEDS}))
if has_free_sigs:
    FAM.append(register("free", 400, {
        str(s): seg_table(f"free_{s}", z50[f"mm_free_{s}"], get_z(z50, "free", s))
        for s in SEEDS}))
log("family rows: " + " ".join(r["label"] for r in FAM))

# ---------------- fork oracle (branches share the noise stream) ----------
def prefix_ok(z, arm, k):
    return max(float(np.abs(z[f"mm_{arm}_{s}"][:k]
                              - res[str(s)]["mm"]["nohop"][:k]).max())
               for s in SEEDS) == 0.0


def fork_state(k):
    out = {}
    for s in SEEDS:
        fL = res[str(s)]["tr"]["nohop"]["fL"]
        eL = res[str(s)]["tr"]["nohop"]["eL"]
        fR = res[str(s)]["tr"]["nohop"]["fR"]
        eR = res[str(s)]["tr"]["nohop"]["eR"]
        out[str(s)] = dict(SL=round(S_of(fL[k - 499:k + 1], eL[k - 499:k + 1]), 3),
                           SR=round(S_of(fR[k - 499:k + 1], eR[k - 499:k + 1]), 3))
    return out


oracle = {}
oracle["forkA_2000"] = dict(
    state=fork_state(2000),
    nohop={s: PERSEED[("nohop", s)]["segs"][1]["duty"] for s in map(str, SEEDS)},
    branch={s: PERSEED[("hop2k(entry)", s)]["segs"][1]["duty"] for s in map(str, SEEDS)},
    prefix_ok=bool(prefix_ok(z55, "hop2k", 2000)))
oracle["forkB_4000"] = dict(
    state=fork_state(4000),
    nohop={s: PERSEED[("nohop", s)]["segs"][2]["duty"] for s in map(str, SEEDS)},
    branch={s: PERSEED[("hop4k(exit)", s)]["segs"][2]["duty"] for s in map(str, SEEDS)},
    prefix_ok=bool(prefix_ok(z55, "hop4k", 4000)))
forkC = {}
for arm in z56_arms:
    if not arm.startswith("v"):
        continue
    kf = int(arm[1:]) * 100
    forkC[arm] = dict(k=kf, prefix_ok=bool(prefix_ok(z56, arm, kf)),
                      duty={s: PERSEED[(f"l56:{arm}", s)]["segs"][2]["duty"]
                            for s in map(str, SEEDS)})
oracle["forkC_mid"] = forkC

fb = oracle["forkB_4000"]
cl = {s: max(fb["nohop"][s], fb["branch"][s]) for s in fb["nohop"]}
bf = max(float(np.mean(list(fb["nohop"].values()))),
         float(np.mean(list(fb["branch"].values()))))
oracle["forkB_closed_loop"] = dict(
    per_seed=cl, cl_mean=round(float(np.mean(list(cl.values()))), 3),
    best_fixed_mean=round(bf, 3),
    gap=round(float(np.mean(list(cl.values()))) - bf, 3),
    benefit_hop={s: round(fb["branch"][s] - fb["nohop"][s], 3) for s in fb["nohop"]})
sls = [fb["state"][str(s)]["SL"] for s in SEEDS]
bens = [oracle["forkB_closed_loop"]["benefit_hop"][str(s)] for s in SEEDS]
rho = float(np.corrcoef(np.argsort(np.argsort(sls)),
                        np.argsort(np.argsort(bens)))[0, 1])
oracle["P5_sep"] = dict(SL_at_4000={str(s): round(v, 3) for s, v in zip(SEEDS, sls)},
                        benefit={str(s): v for s, v in zip(SEEDS, bens)},
                        rank_corr=rho)

# ---------------- registered gates + predictions ----------------
def R(label):
    return next(r for r in FAM if r["label"] == label)


gates = {}
gates["H1_tracking"] = dict(
    cells=[r["label"] for r in FAM if r["fast_lock"] and r["drive_on_s"] <= 48.0],
    pass_=any(r["fast_lock"] and r["drive_on_s"] <= 48.0 for r in FAM))
best07 = max(FAM, key=lambda r: r["duty07_mean"])
gates["H2_structure"] = dict(best_cell=best07["label"],
                             duty07_mean=best07["duty07_mean"],
                             duty07_min=best07["duty07_min"],
                             pass_=best07["duty07_mean"] >= .55)
pool_ok = [r for r in FAM if r["pooled_min"] >= .5]
gates["H3_pooled"] = dict(cells_clearing=[r["label"] for r in pool_ok],
                          best_pooled_min=max(r["pooled_min"] for r in FAM),
                          gate_is_bug=not pool_ok)
lock_struct = [r for r in FAM if r["fast_lock"] and r["duty07_mean"] >= .5]
gates["H4_drive_floor"] = dict(
    eligible=[(r["label"], r["drive_on_s"]) for r in lock_struct],
    min_drive_s=min((r["drive_on_s"] for r in lock_struct), default=None))
preds = {}
preds["P1_slack_in_schedules"] = dict(
    hold={a: R(a)["duty07_mean"] for a in ("off200", "off300")},
    collapse={a: R(a)["duty07_mean"] for a in ("off500", "off700", "min5seg")},
    pass_=(all(R(a)["duty07_mean"] >= .5 for a in ("off200", "off300"))
           and all(R(a)["duty07_mean"] < .4
                   for a in ("off500", "off700", "min5seg"))))
preds["P1b_duty_not_gap_limited"] = dict(
    diffs={a: round(R(a)["duty07_mean"] - R("nohop")["duty07_mean"], 3)
           for a in ("off200", "off300")},
    pass_=all(abs(R(a)["duty07_mean"] - R("nohop")["duty07_mean"]) <= .1
              for a in ("off200", "off300")))
preds["P2_gas_owns_pooled"] = dict(
    best_pooled_min=max(r["pooled_min"] for r in FAM),
    pass_=max(r["pooled_min"] for r in FAM) < .5)
f2 = R("fast2")
f2_fastmin = min(PERSEED[("fast2", str(s))]["segs"][1]["duty"] for s in SEEDS)
preds["P3_fast2"] = dict(fast_err=f2["fast_err"], fast_lock=f2["fast_lock"],
                         fast_duty_min=f2_fastmin,
                         pass_=bool(f2["fast_lock"] and f2_fastmin < .25))
s2off, s2a2 = R("seg2off"), R("seg2a2")
preds["P4_seg2"] = dict(
    seg2off_seg2_mean=s2off["seg_duty"][2],
    seg2a2_delta=round(s2a2["duty07_mean"] - R("nohop")["duty07_mean"], 3),
    pass_=(s2off["seg_duty"][2] < .15
           and abs(s2a2["duty07_mean"] - R("nohop")["duty07_mean"]) <= .1))
preds["P5_oracle"] = dict(
    rank_corr=rho, gap=oracle["forkB_closed_loop"]["gap"],
    prefix_all=all([oracle["forkA_2000"]["prefix_ok"],
                    oracle["forkB_4000"]["prefix_ok"]]
                   + [v["prefix_ok"] for v in forkC.values()]),
    pass_=(rho == -1.0 and oracle["forkB_closed_loop"]["gap"] >= .05))
preds["P6_free_cell"] = dict(available=has_free_sigs,
                             free_row=R("free") if has_free_sigs else None)

verdict = dict(
    tracking="cells with fast lock <=.01 3/3 at <=48s: "
             + ",".join(gates["H1_tracking"]["cells"]),
    structure=f"best duty07 mean {best07['duty07_mean']} ({best07['label']}), "
              f"min-seed {best07['duty07_min']}",
    pooled="GATE-IS-THE-BUG (gas owns it)" if gates["H3_pooled"]["gate_is_bug"]
           else f"cleared by {gates['H3_pooled']['cells_clearing']}",
    drive_floor_s=gates["H4_drive_floor"]["min_drive_s"],
    closed_loop_gap=oracle["forkB_closed_loop"]["gap"],
    SL_sep_rank_corr=rho)

dump = dict(meta=dict(task="l51 SEGB", seeds=SEEDS, ent_amp=ENT_AMP,
                      win=WIN, settle=SETTLE, drive_on=DRIVE_ON,
                      fd_expected=fd_expected, l56_arms=z56_arms,
                      free_sigs=has_free_sigs),
            c0=c0, c0_pass=bool(c0_pass), c1=c1,
            family=FAM,
            perseed={f"{k[0]}|{k[1]}": v for k, v in PERSEED.items()},
            oracle=oracle, gates=gates, predictions=preds, verdict=verdict)
json.dump(dump, open("l58/results_l58.json", "w"), indent=1)
log("VERDICT " + json.dumps(verdict))
log("GATES " + json.dumps({k: v.get("pass_", v.get("gate_is_bug"))
                           for k, v in gates.items()}))
log("PREDS " + json.dumps({k: v.get("pass_") for k, v in preds.items()}))
log(f"done {time.time()-t0:.0f}s -> l58/results_l58.json")
