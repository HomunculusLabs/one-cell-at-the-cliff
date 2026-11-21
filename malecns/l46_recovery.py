"""L46: post-stop recovery kinetics — L44's disclosed open note.

The MOST protected arm during the stop (h40, S_dur .39-.59) showed ~ZERO
antagonist structure at L44's 20-s post window (S_after -.037..+.032) while
h0/h20 recovered (.37-.51). Extend the post window to 120 s on the
h0/h20/h40 contrast, stop unchanged (20 s @ DNg88 -8): window artifact
(SLOW-RECOVERY) or cost of protection (IMPAIRED)? Machinery l44-verbatim
except WIN=18000 / POST=12000 and arms {0,20,40}. C0 anchor = bit-identity
to l44 traces over the shared [0,8000) prefix (noise-stream replication).

PREREG in l46/PREREG.md, written first. CPU-only; no live changes.
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
POST = 12000                       # 120 s post window (l44 had 2000)
WIN = STOP0 + STOPD + POST         # 18000
ENT_AMP, ENT_F = 0.3, 0.7
REL_AMP = -8.0
HISTS = (0, 20, 40)                # entrain history seconds
HSTEP = {h: h * 100 for h in HISTS}
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05       # l32 arm-A frozen (D inert per L35)
CORE_TYPES = ("IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012")
ARMS = [f"h{h}" for h in HISTS]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l32/l34/l39/l41-l44 verbatim) ----------
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

# global 0.7 Hz phase (settle prefix + win), only consulted when mech is on
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * ENT_F * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * ENT_F * DT
    PHI[i] = ph


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
            h = HSTEP[int(a[1:])]
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if 0 <= k and (STOP0 - h) <= k < STOP0:
                drive[mech, 0] = drive[mech, 0] + ENT_AMP * (0.5 + 0.5 * ph_k)
            if STOP0 <= k < STOP0 + STOPD:
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

# raw checkpoint BEFORE analysis, ALL pools the analysis reads (L43/L45a)
np.savez_compressed(
    "l46/raw_l46.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"fL_{a}_{s}": res[str(s)]["tr"][a]["fL"] for a in ARMS for s in SEEDS},
    **{f"fR_{a}_{s}": res[str(s)]["tr"][a]["fR"] for a in ARMS for s in SEEDS},
    **{f"eL_{a}_{s}": res[str(s)]["tr"][a]["eL"] for a in ARMS for s in SEEDS},
    **{f"eR_{a}_{s}": res[str(s)]["tr"][a]["eR"] for a in ARMS for s in SEEDS},
    **{f"x88_{a}_{s}": res[str(s)]["x88"][a] for a in ARMS for s in SEEDS},
    **{f"xc_{a}_{s}": res[str(s)]["xc"][a] for a in ARMS for s in SEEDS})
log("raw_l46.npz checkpointed")

# ---------------- C0: prefix bit-identity vs l44 stored traces ----------------
l44 = np.load("l44/traces.npz")
c0_maxd, s20_check = {}, {}
for a in ARMS:
    for s in SEEDS:
        ref = l44[f"mm_{a}_{s}"][:8000]
        cur = res[str(s)]["mm"][a][:8000]
        c0_maxd[f"{a}_{s}"] = float(np.abs(cur - ref).max())
c0_exact = all(v == 0.0 for v in c0_maxd.values())

# ---------------- analysis ----------------
P0 = STOP0 + STOPD  # 6000 post start


def arm_metrics(a, s):
    r = res[s]
    fL, fR, eL, eR = (r["tr"][a][c] for c in ("fL", "fR", "eL", "eR"))
    S = np.full(WIN, np.nan)
    for t in range(499, WIN, 10):
        S[t] = S_of(fL[t - 499:t + 1] + fR[t - 499:t + 1],
                    eL[t - 499:t + 1] + eR[t - 499:t + 1])
    ts = np.arange(499, WIN, 10)

    def med(lo, hi):
        return float(np.nanmedian(S[ts[(ts >= lo) & (ts < hi)]]))

    def duty(lo, hi):
        q = S[ts[(ts >= lo) & (ts < hi)]]
        return float(np.nanmean(q >= 0.25))

    post_ts = ts[ts >= P0]
    sq = S[post_ts]
    lat = None
    for j, v in enumerate(sq):
        if v >= 0.25:
            lat = int(post_ts[j] - P0)
            break
    late_r, f_late = rhythm2(r["mm"][a][12000:18000])
    late_r60, f_late60 = rhythm2(r["mm"][a][STOP0 + STOPD - 500:STOP0 + STOPD])
    xcv = r["xc"][a]
    return dict(
        S_med_20s=round(med(P0, 8000), 3),
        S_med_early=round(med(P0, P0 + 6000), 3),
        S_med_late=round(med(12000, 18000), 3),
        duty_early=round(duty(P0, P0 + 6000), 3),
        duty_late=round(duty(12000, 18000), 3),
        lat_first_s=round(lat * DT, 2) if lat is not None else None,
        ratio_stop_end=round(late_r60, 1), f_stop_end=round(f_late60, 3),
        ratio_late=round(late_r, 1), f_late=round(f_late, 3),
        x88min=round(float(r["x88"][a][STOP0:STOP0 + STOPD].min()), 3),
        core_stop_end=round(float(xcv[STOP0 + STOPD - 200:STOP0 + STOPD].mean()), 4),
        core_late_post=round(float(xcv[12000:18000].mean()), 4)), S


tbl, SR_all = {}, {}
for a in ARMS:
    tbl[a] = {}
    for s in SEEDS:
        m, S = arm_metrics(a, str(s))
        tbl[a][str(s)] = m
        SR_all[f"SR_{a}_{s}"] = S

# premise replication (comes free from C0 but checked numerically too)
l44res = json.load(open("l44/results_l44.json"))
premise = {
    "h40_S20s": [tbl["h40"][str(s)]["S_med_20s"] for s in SEEDS],
    "h0_S20s": [tbl["h0"][str(s)]["S_med_20s"] for s in SEEDS],
    "h20_S20s": [tbl["h20"][str(s)]["S_med_20s"] for s in SEEDS],
    "l44_stored_after": {a: [l44res["table"][a][str(s)]["S_med_after"]
                             for s in SEEDS] for a in ARMS}}
premise_pass = (all(v < 0.25 for v in premise["h40_S20s"])
                and sum(v >= 0.25 for v in premise["h0_S20s"]) >= 2
                and sum(v >= 0.25 for v in premise["h20_S20s"]) >= 2)
premise_match = all(
    abs(premise[f"{a}_S20s"][i] - l44res["table"][a][str(s)]["S_med_after"]) < 5e-3
    for a in ARMS for i, s in enumerate(SEEDS))

dm_land = {str(s): float(np.abs(res[str(s)]["mm"]["h40"]
                                - res[str(s)]["mm"]["h0"])[3500:4000].max())
           for s in SEEDS}
c1 = dict(dm_land=dm_land,
          x88_unpin=all(tbl[a][str(s)]["x88min"] < 0.5
                        for a in ARMS for s in SEEDS),
          pass_=all(v > 0 for v in dm_land.values())
          and all(tbl[a][str(s)]["x88min"] < 0.5 for a in ARMS for s in SEEDS))

h40_late = [tbl["h40"][str(s)]["S_med_late"] >= 0.25 for s in SEEDS]
h0_late = [tbl["h0"][str(s)]["S_med_late"] >= 0.25 for s in SEEDS]
if sum(h40_late) == 3:
    c2 = "SLOW-RECOVERY (window artifact; latency table is the deliverable)"
elif sum(h40_late) <= 1 and sum(h0_late) >= 2:
    c2 = "IMPAIRED (cost of protection; recovery budget after stops)"
else:
    c2 = "MIXED (read table; name the L45b spontaneous floor)"
lat_table = {a: {str(s): tbl[a][str(s)]["lat_first_s"] for s in SEEDS}
             for a in ARMS}
late_gap = {str(s): round(tbl["h40"][str(s)]["S_med_late"]
                          - tbl["h0"][str(s)]["S_med_late"], 3) for s in SEEDS}

c3 = dict(f_late={a: {str(s): tbl[a][str(s)]["f_late"] for s in SEEDS}
                  for a in ARMS},
          f_stop_end={a: {str(s): tbl[a][str(s)]["f_stop_end"]
                          for s in SEEDS} for a in ARMS},
          core={a: {str(s): [tbl[a][str(s)]["core_stop_end"],
                             tbl[a][str(s)]["core_late_post"]]
                    for s in SEEDS} for a in ARMS})

verdict = dict(
    C0=dict(prefix_maxd=c0_maxd, bit_exact=c0_exact,
            premise=premise, premise_pass=premise_pass,
            premise_match_l44=premise_match),
    C1=c1,
    C2=dict(verdict=c2, h40_late=h40_late, h0_late=h0_late,
            lat_table=lat_table, late_gap_h40_minus_h0=late_gap),
    C3=c3)
log("VERDICT " + json.dumps(verdict)[:2600])

np.savez_compressed("l46/traces_l46.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
                       for a in ARMS for s in SEEDS},
                    **{f"xc_{a}_{s}": res[str(s)]["xc"][a]
                       for a in ARMS for s in SEEDS},
                    **SR_all)
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, seeds=SEEDS,
                      ent_amp=ENT_AMP, ent_f=ENT_F, stop0=STOP0, stopd=STOPD,
                      post=POST, rel_amp=REL_AMP, hists=list(HISTS),
                      nodes=int(n), edges=len(gsrc), core_counts=core_counts),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            table=tbl, verdict=verdict)
json.dump(dump, open("l46/results_l46.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l46/results_l46.json")
