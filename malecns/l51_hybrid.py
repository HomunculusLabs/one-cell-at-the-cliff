"""L51: structure-aware-hybrid-schedule (LANE.md ideas-25).

Hybrid controller: duty58's exact 5-on/4-off table on the 0.7 segments,
CONTINUOUS amp on the fast 1.4 segment, hops at both transitions. Score the
triple (seg1 tracking err, pooled + window-scoped bilateral duty, drive-on)
vs allw / duty58 (both l50-verbatim, chain-anchored bit-identically).
hynohop = hybrid AMPA without hops (hop-wiring reference + does a
chopped-entry 1.4 lock without the hop?).

PREREG l51/PREREG.md written first. Raw npz checkpoint BEFORE analysis.
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
MEAS0 = 500                       # per-seg measurement start (l39 convention)
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
HOP_AMP, HOP_VW = 0.5, 40
TRANS = [2000, 4000]
LOCK_TOL = 0.10
ARMS = ["allw", "duty58", "hybrid", "hynohop"]
HOP_ARMS = ("allw", "duty58", "hybrid")
DM_PAIRS = [("hybrid", "allw"), ("hybrid", "duty58"),
            ("allw", "duty58"), ("hybrid", "hynohop")]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l32/l34/l39/l42/l49/l50 verbatim) ----------
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
lnt = nt_names[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)
log(f"sub nodes {n:,} | edges {len(gsrc):,} | {time.time()-t0:.0f}s")

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
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
log(f"mech {len(mech)} | 046L {len(hopL)}")

# ---------- global phase (l39 convention: settle @0.7, then @target) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- per-arm AMPA / HOPA tables (no inline conditionals) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
AMPA["allw"][:] = ENT_AMP
for seg0, _, _ in SEGB:
    c = 0                                   # duty58: 500-on/400-off per segment
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA["duty58"][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        AMPA["hybrid"][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP   # 0.7 segs
        AMPA["hynohop"][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA["hybrid"][2000:4000] = ENT_AMP         # fast segment CONTINUOUS
AMPA["hynohop"][2000:4000] = ENT_AMP
HOPA = {a: np.zeros(WIN, bool) for a in ARMS}
for a in HOP_ARMS:
    for o in TRANS:
        HOPA[a][o:o + HOP_VW] = True

# table asserts (write-time wiring checks)
assert (AMPA["allw"] == ENT_AMP).all()
for seg0, segend, f in SEGB:
    seg = AMPA["duty58"][seg0:seg0 + SEG]         # duty58 chopped everywhere
    assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
    assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
    assert (seg[1800:2000] == ENT_AMP).all()
    if f == 0.7:                                  # hybrid chopped on 0.7 segs
        for a in ("hybrid", "hynohop"):
            seg = AMPA[a][seg0:seg0 + SEG]
            assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
            assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
            assert (seg[1800:2000] == ENT_AMP).all()
    else:                                         # hybrid continuous on 1.4
        for a in ("hybrid", "hynohop"):
            assert (AMPA[a][seg0:segend] == ENT_AMP).all()
assert (AMPA["hybrid"][2000:4000] == ENT_AMP).all()
assert (AMPA["hynohop"][2000:4000] == ENT_AMP).all()
assert (AMPA["hybrid"] == AMPA["hynohop"]).all()
assert np.array_equal(AMPA["hybrid"][:2500], AMPA["duty58"][:2500])
assert not np.array_equal(AMPA["hybrid"][2500:], AMPA["duty58"][2500:])
assert not (HOPA["hynohop"]).any()
assert sum(HOPA[a].tolist().count(True) for a in HOP_ARMS) == 3 * 2 * HOP_VW
for o in TRANS:                                        # hops ride on-windows
    assert AMPA["hybrid"][o] == ENT_AMP and AMPA["duty58"][o] == ENT_AMP
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
assert DRIVE_ON["hybrid"] == 4800 and DRIVE_ON["hynohop"] == 4800
assert DRIVE_ON["allw"] == 6400 and DRIVE_ON["duty58"] == 4000
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
    x046 = {a: np.zeros(WIN, np.float32) for a in ARMS}
    dm = {p: dict(first_div=-1, vmax=0.0) for p in DM_PAIRS}
    hop_win = np.zeros(WIN, bool)
    for o in TRANS:
        hop_win[o:o + HOP_VW] = True

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
            if k < 0:
                amp_k = ENT_AMP
            else:
                amp_k = float(AMPA[a][k])
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            if k >= 0 and HOPA[a][k]:
                drive[hopL, 0] += HOP_AMP
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
            x046[a][i] = X[a][hopL].mean()
        if i >= 1:
            for p in DM_PAIRS:
                d = float((X[p[0]] - X[p[1]]).abs().max())
                if hop_win[i] and d > dm[p]["vmax"]:
                    dm[p]["vmax"] = d
                if d > 1e-6 and dm[p]["first_div"] < 0:
                    dm[p]["first_div"] = i
    out = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
               dm=dm, mm=mm, tr=tr, x046=x046)
    return out


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# raw checkpoint BEFORE analysis (L45a lesson), all pools metrics read
np.savez_compressed(
    "l51/raw_l51.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")},
    **{f"x046_{a}_{s}": res[str(s)]["x046"][a] for a in ARMS for s in SEEDS})
log("raw_l51.npz checkpointed")

# ---------------- C0 anchors ----------------
z50 = np.load("l50/traces_l50.npz")
c0 = {}
for a in ("allw", "duty58"):                       # C0c chain anchor vs l50
    c0[f"{a}_vs_l50"] = max(float(np.abs(res[str(s)]["mm"][a][:WIN]
                                        - z50[f"mm_{a}_{s}"][:WIN]).max())
                            for s in SEEDS)
c0["hyb_prefix_duty58"] = max(                     # C0a prefix anchor
    float(np.abs(res[str(s)]["mm"]["hybrid"][:2500]
                 - res[str(s)]["mm"]["duty58"][:2500]).max()) for s in SEEDS)
for p, want in ((("hybrid", "allw"), 500), (("hybrid", "duty58"), 2500),
                (("allw", "duty58"), 500)):
    fd = [res[str(s)]["dm"][p]["first_div"] for s in SEEDS]
    c0[f"first_div_{'-'.join(p)}"] = dict(vals=fd, want=want,
                                          ok=all(v == want for v in fd))
c0_pass = (all(v == 0.0 for k, v in c0.items() if isinstance(v, float))
           and all(c0[k]["ok"] for k in c0 if k.startswith("first_div")))

# ---------------- C1 wiring ----------------
fd_hop = [res[str(s)]["dm"][("hybrid", "hynohop")]["first_div"] for s in SEEDS]
vm_hop = [res[str(s)]["dm"][("hybrid", "hynohop")]["vmax"] for s in SEEDS]
c1 = dict(af_ok=all(0.01 < res[str(s)]["af"][a] < 0.9
                    for s in SEEDS for a in ARMS),
          first_div_hop=fd_hop, volley_max_hop=[round(v, 4) for v in vm_hop])
c1["pass_"] = (all(v == 2000 for v in fd_hop) and all(v > 1e-6 for v in vm_hop)
               and c1["af_ok"])

# ---------------- analysis: blocks, rolling per-side S, duty ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    fL, fR, eL, eR = (res[str(s)]["tr"][a][c] for c in ("fL", "fR", "eL", "eR"))
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


blocks = {a: {str(s): [] for s in SEEDS} for a in ARMS}
for a in ARMS:
    for s in SEEDS:
        for b in range(WIN // BLK):
            f_hat, ratio = dom_freq(res[str(s)]["mm"][a][b * BLK:(b + 1) * BLK])
            seg = next(i for i, (a0_, b0, _) in enumerate(SEGB)
                       if a0_ <= b * BLK < b0)
            blocks[a][str(s)].append(dict(
                b=b, f=round(f_hat, 3), ratio=round(ratio, 1), seg=seg,
                target=SEGB[seg][2], err=round(abs(f_hat - SEGB[seg][2]), 3)))

seg_tbl = {a: {} for a in ARMS}
for a in ARMS:
    for s in SEEDS:
        SL, SR = s_arrays(a, str(s))
        rows = []
        for si, (a0_, b0, tg) in enumerate(SEGB):
            bl = [x for x in blocks[a][str(s)] if x["seg"] == si]
            err = round(float(np.mean([x["err"] for x in bl[1:]])), 4)
            ttl = next((x["b"] - si * 4 for x in bl[1:]
                        if x["err"] <= LOCK_TOL), None)
            lo, hi = a0_ + MEAS0, b0
            q = (TS >= lo) & (TS < hi)
            both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
            f_seg = dom_freq(res[str(s)]["mm"][a][a0_:b0])[0]
            rows.append(dict(
                err=err, ttl=ttl, duty=round(float(np.nanmean(both)), 3),
                SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                f=round(f_seg, 3)))
        qall = np.zeros(len(TS), bool)
        for a0_, b0, _ in SEGB:
            qall |= (TS >= a0_ + MEAS0) & (TS < b0)
        SLq, SRq = SL[TS[qall]], SR[TS[qall]]
        # window-scoped duty: the two 0.7 segments only
        q07 = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            if f == 0.7:
                q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
        seg_tbl[a][str(s)] = dict(
            segs=rows,
            duty_all=round(float(np.nanmean((SLq >= .25) & (SRq >= .25))), 3),
            duty_07=round(float(np.nanmean(
                (SL[TS[q07]] >= .25) & (SR[TS[q07]] >= .25))), 3))
    for k, m in (("duty_all", np.mean), ("duty_07", np.mean)):
        seg_tbl[a]["mean_" + k] = round(float(m(
            [seg_tbl[a][str(s)][k] for s in SEEDS])), 3)
    seg_tbl[a]["mean_duty_seg"] = [round(float(np.mean(
        [seg_tbl[a][str(s)]["segs"][i]["duty"] for s in SEEDS])), 3)
        for i in range(3)]

# hybrid on/off split inside the two 0.7 segments
off07 = np.zeros(WIN, bool)
on07 = np.zeros(WIN, bool)
for seg0, _, f in SEGB:
    if f != 0.7:
        continue
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        on07[lo:min(lo + 500, seg0 + SEG)] = True
        off07[min(lo + 500, seg0 + SEG):min(lo + 900, seg0 + SEG)] = True
        c += 1
split = {}
for s in SEEDS:
    SL, SR = s_arrays("hybrid", str(s))
    ok_ts = ((SL >= .25) & (SR >= .25))[TS]
    qm = (TS >= 500)
    split[str(s)] = dict(
        duty_on=round(float(np.nanmean(ok_ts[qm & on07[TS]])), 3),
        duty_off=round(float(np.nanmean(ok_ts[qm & off07[TS]])), 3))
split["mean"] = dict(
    duty_on=round(float(np.mean([split[str(s)]["duty_on"] for s in SEEDS])), 3),
    duty_off=round(float(np.mean([split[str(s)]["duty_off"] for s in SEEDS])), 3))

# ---------------- registered triple + verdicts ----------------
hyb = seg_tbl["hybrid"]
g1_vals = {str(s): hyb[str(s)]["segs"][1]["err"] for s in SEEDS}
g1 = all(v <= 0.01 for v in g1_vals.values())
d_all = [hyb[str(s)]["duty_all"] for s in SEEDS]
g2 = bool(np.mean(d_all) >= 0.5 and min(d_all) >= 0.45)
d_07 = [hyb[str(s)]["duty_07"] for s in SEEDS]
g2p = bool(np.mean(d_07) >= 0.5)
nohop_err = {str(s): seg_tbl["hynohop"][str(s)]["segs"][1]["err"] for s in SEEDS}
preds = dict(
    P_a_g1=bool(g1),
    P_b_g2fail_band=bool((not g2) and 0.30 <= float(np.mean(d_all)) <= 0.45),
    P_c_g2p_and_split=bool(g2p and split["mean"]["duty_on"] >= 0.4
                           and split["mean"]["duty_off"] >= 0.4),
    P_d_nohop_misses=bool(any(v > 0.01 for v in nohop_err.values())))
if g1 and g2:
    verdict = "SPEC COMPLETE (pooled)"
elif g1 and g2p and not g2:
    verdict = ("IRREDUCIBLE AT THE FAST WINDOW (amp .3): hybrid holds "
               "allw-level tracking AND duty58-level structure in their "
               "windows; pooled duty cannot reach .5 with a toxic fast window")
else:
    broke = "tracking" if not g1 else "0.7-window structure"
    verdict = f"CONFLICT BEYOND SCHEDULING: {broke} broke"

triple = dict(
    tracking={**g1_vals, "gate_.01": bool(g1)},
    duty_pooled={str(s): v for s, v in zip(SEEDS, d_all)},
    duty_pooled_mean=round(float(np.mean(d_all)), 3),
    duty_07={str(s): v for s, v in zip(SEEDS, d_07)},
    duty_07_mean=round(float(np.mean(d_07)), 3),
    drive_on_s={a: round(DRIVE_ON[a] * DT, 1) for a in ARMS})
cost = {a: dict(drive_on_s=round(DRIVE_ON[a] * DT, 1),
                mean_duty=seg_tbl[a]["mean_duty_all"],
                mean_duty_07=seg_tbl[a]["mean_duty_07"],
                mean_duty_seg=seg_tbl[a]["mean_duty_seg"],
                seg_err={str(s): [seg_tbl[a][str(s)]["segs"][i]["err"]
                                  for i in range(3)] for s in SEEDS})
        for a in ARMS}
verdict_d = dict(C0=c0, C0_pass=bool(c0_pass), C1=c1, triple=triple,
                 split_hybrid=split, nohop_seg1=nohop_err,
                 predictions=preds, verdict=verdict)
log("VERDICT " + json.dumps(verdict_d)[:2800])

np.savez_compressed("l51/traces_l51.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
                       for a in ARMS for s in SEEDS},
                    **{f"SL_{a}_{s}": s_arrays(a, str(s))[0]
                       for a in ARMS for s in SEEDS},
                    **{f"SR_{a}_{s}": s_arrays(a, str(s))[1]
                       for a in ARMS for s in SEEDS})
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, segb=SEGB,
                      blk=BLK, seeds=SEEDS, ent_amp=ENT_AMP, hop_amp=HOP_AMP,
                      hop_vw=HOP_VW, trans=TRANS, drive_on=DRIVE_ON,
                      nodes=int(n), edges=len(gsrc)),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            dm={f"{p[0]}-{p[1]}": {str(s): res[str(s)]["dm"][p]
                                   for s in SEEDS} for p in DM_PAIRS},
            segments=seg_tbl, blocks=blocks, split_hybrid=split,
            cost=cost, verdict=verdict_d)
json.dump(dump, open("l51/results_l51.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l51/results_l51.json")
