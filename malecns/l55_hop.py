"""L55: hop-scheduling for the pooled gate (LANE.md ideas-26).

2x2 hop factorial (none / entry / exit / both) on the hybrid AMPA schedule
+ the LANE-registered conditional policy (hop at KD=3000 iff in-flight
fast-seg lock err > THR=.05). hynohop and hybrid are chain anchors vs
l51/raw_l51.npz (bit-identical). Pooled duty table + factorial contrast.

PREREG l55/PREREG.md written first. Raw npz checkpoint BEFORE analysis.
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
MEAS0 = 500                       # per-seg measurement start (l39-l51 conv.)
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
HOP_AMP, HOP_VW = 0.5, 40
TRANS = [2000, 4000]
KD, WF, THR = 3000, 1000, 0.05    # conditional: decide @10s into fast seg
LOCK_TOL = 0.10
ARMS = ["hynohop", "hop2k", "hop4k", "cond", "hybrid"]
DM_PAIRS = [(a, "hynohop") for a in ("hop2k", "hop4k", "hybrid", "cond")]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l32/l34/l39/l50/l51 verbatim) ----------
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

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- per-arm AMPA / HOPA tables (write-time asserted) ----------
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
HOPA["hop2k"][2000:2000 + HOP_VW] = True
HOPA["hop4k"][4000:4000 + HOP_VW] = True
for o in TRANS:
    HOPA["hybrid"][o:o + HOP_VW] = True

assert all(np.array_equal(AMPA[a], AMPA["hynohop"]) for a in ARMS)
for seg0, segend, f in SEGB:
    seg = AMPA["hynohop"][seg0:seg0 + SEG]
    if f == 0.7:
        assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
        assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
        assert (seg[1800:2000] == ENT_AMP).all()
    else:
        assert (AMPA["hynohop"][seg0:segend] == ENT_AMP).all()
assert not HOPA["hynohop"].any() and not HOPA["cond"].any()
assert HOPA["hop2k"].sum() == HOP_VW and HOPA["hop2k"][:2000].sum() == 0 \
    and HOPA["hop2k"][2040:].sum() == 0
assert HOPA["hop4k"].sum() == HOP_VW and HOPA["hop4k"][:4000].sum() == 0
assert HOPA["hybrid"].sum() == 2 * HOP_VW
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
    fire = {"cond": False}
    cond_rec = dict(f=False, f_hat=None, err=None, ratio=None)
    hop_win = np.zeros(WIN, bool)                # dm probe windows (union)
    for o in (2000, KD, 4000):
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
            if a == "cond" and fire["cond"] and KD <= k < KD + HOP_VW:
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
        if i == KD:                              # conditional decision
            f_hat, ratio = dom_freq(mm["cond"][KD - WF:KD])
            cond_rec["f_hat"] = round(f_hat, 4)
            cond_rec["ratio"] = round(ratio, 1)
            cond_rec["err"] = round(abs(f_hat - 1.4), 4)
            fire["cond"] = bool(abs(f_hat - 1.4) > THR)
            cond_rec["f"] = fire["cond"]
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
               dm=dm, mm=mm, tr=tr, x046=x046, cond=cond_rec)
    return out


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s | cond fired: "
    + " ".join(f"s{s}:{res[str(s)]['cond']['f']}(err {res[str(s)]['cond']['err']})"
               for s in SEEDS))

# raw checkpoint BEFORE analysis (L45a lesson)
np.savez_compressed(
    "l55/raw_l55.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")},
    **{f"x046_{a}_{s}": res[str(s)]["x046"][a] for a in ARMS for s in SEEDS})

# ---------------- C0 anchors ----------------
z51 = np.load("l51/raw_l51.npz")
c0 = {}
for a in ("hynohop", "hybrid"):                  # chain anchors vs l51
    c0[f"{a}_vs_l51"] = max(float(np.abs(res[str(s)]["mm"][a][:WIN]
                                        - z51[f"mm_{a}_{s}"][:WIN]).max())
                            for s in SEEDS)
fd_ok = {}
for a, want in (("hop2k", 2000), ("hop4k", 4000), ("hybrid", 2000)):
    fd = [res[str(s)]["dm"][(a, "hynohop")]["first_div"] for s in SEEDS]
    fd_ok[a] = all(v == want for v in fd)
fd_cond = [res[str(s)]["dm"][("cond", "hynohop")]["first_div"] for s in SEEDS]
cond_bit = max(float(np.abs(res[str(s)]["mm"]["cond"]
                            - res[str(s)]["mm"]["hynohop"]).max()) for s in SEEDS)
fired_any = [res[str(s)]["cond"]["f"] for s in SEEDS]
c0["fd_hop2k_2000"] = fd_ok["hop2k"]
c0["fd_hop4k_4000"] = fd_ok["hop4k"]
c0["fd_hybrid_2000"] = fd_ok["hybrid"]
c0["fd_cond"] = fd_cond
c0["cond_full_bitid"] = bool(cond_bit == 0.0 and not any(fired_any))
c0_pass = (all(v == 0.0 for k, v in c0.items() if isinstance(v, float))
           and all(fd_ok.values())
           and ((not any(fired_any) and cond_bit == 0.0)
                or all(v == KD for v in fd_cond)))

# ---------------- C1 wiring ----------------
vm = {a: [round(res[str(s)]["dm"][(a, "hynohop")]["vmax"], 4) for s in SEEDS]
      for a in ("hop2k", "hop4k", "hybrid", "cond")}
c1 = dict(af_ok=all(0.01 < res[str(s)]["af"][a] < 0.9
                    for s in SEEDS for a in ARMS), volley_max=vm)
c1["pass_"] = (c1["af_ok"]
               and all(v > 1e-6 for a in ("hop2k", "hop4k", "hybrid")
                       for v in vm[a]))

# ---------------- analysis (l51-verbatim) ----------------
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

# factorial contrast: fast-seg (idx 1) and seg2 duty per cell
fact = {a: dict(seg1=[seg_tbl[a][str(s)]["segs"][1]["duty"] for s in SEEDS],
                seg1_mean=seg_tbl[a]["mean_duty_seg"][1],
                seg2=[seg_tbl[a][str(s)]["segs"][2]["duty"] for s in SEEDS],
                seg2_mean=seg_tbl[a]["mean_duty_seg"][2],
                pooled=[seg_tbl[a][str(s)]["duty_all"] for s in SEEDS],
                pooled_mean=seg_tbl[a]["mean_duty_all"],
                seg1_err=[seg_tbl[a][str(s)]["segs"][1]["err"] for s in SEEDS])
       for a in ARMS}

# ---------------- gates + predictions + verdict ----------------
cond_d = [seg_tbl["cond"][str(s)]["duty_all"] for s in SEEDS]
cond_e = [seg_tbl["cond"][str(s)]["segs"][1]["err"] for s in SEEDS]
p1 = bool(sum(v >= .5 for v in cond_d) >= 2 and all(v <= .01 for v in cond_e))
p2 = bool(not any(fired_any))
p3 = bool(sum(fact["hop2k"]["seg1"][i] < fact["hynohop"]["seg1"][i]
              for i in range(3)) >= 2)
preds = dict(P1_gate=p1, P2_never_fires=p2, P3_entry_hop_costs_structure=p3,
             P4_exit_hop_recorded=dict(
                 hop4k_seg2=fact["hop4k"]["seg2"],
                 nohop_seg2=fact["hynohop"]["seg2"],
                 hybrid_seg2=fact["hybrid"]["seg2"]))
if p1 and p2:
    verdict = ("GATE MET BY HOP DELETION: cond never fires at amp .3 (lock "
               "free from chopped entry) and the no-hop schedule already "
               "meets pooled >= .5 on 2/3 seeds — the L39 hop is pure "
               "structure cost here; controller spec: drop the hops")
elif p1 and not p2:
    verdict = ("CONDITIONAL EARNS ITS KEEP on >=1 seed (fired and still "
               "met the gate); report where")
else:
    miss = {str(s): [seg_tbl["cond"][str(s)]["segs"][i]["duty"]
                     for i in range(3)] for s in SEEDS}
    verdict = ("GATE NOT REACHABLE by fast-seg hop scheduling; per-seed "
               "seg duties: " + json.dumps(miss))

verdict_d = dict(C0=c0, C0_pass=bool(c0_pass), C1=c1,
                 cond_record={str(s): res[str(s)]["cond"] for s in SEEDS},
                 pooled_table={a: fact[a]["pooled"] for a in ARMS},
                 pooled_mean={a: fact[a]["pooled_mean"] for a in ARMS},
                 predictions=preds, verdict=verdict)
log("VERDICT " + json.dumps(verdict_d)[:2600])

np.savez_compressed("l55/traces_l55.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
                       for a in ARMS for s in SEEDS},
                    **{f"SL_{a}_{s}": s_arrays(a, str(s))[0]
                       for a in ARMS for s in SEEDS},
                    **{f"SR_{a}_{s}": s_arrays(a, str(s))[1]
                       for a in ARMS for s in SEEDS})
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, segb=SEGB,
                      blk=BLK, seeds=SEEDS, ent_amp=ENT_AMP, hop_amp=HOP_AMP,
                      hop_vw=HOP_VW, trans=TRANS, kd=KD, wf=WF, thr=THR,
                      drive_on=DRIVE_ON, nodes=int(n), edges=len(gsrc)),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            dm={f"{p[0]}-{p[1]}": {str(s): res[str(s)]["dm"][p]
                                   for s in SEEDS} for p in DM_PAIRS},
            segments=seg_tbl, factorial=fact, verdict=verdict_d)
json.dump(dump, open("l55/results_l55.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l55/results_l55.json")
