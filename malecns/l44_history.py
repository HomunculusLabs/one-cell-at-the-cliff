"""L44: entrain-history-protection — graded resistance curve or basin entry?

Arms H in {0,5,10,20,40} s of 0.7 Hz mech entrainment immediately before a
FIXED stop (DNg88 -8, 20 s). All arms free-settled (NO mech in settle, unlike
l43) and free before their entrain window; stop + post identical across arms.
Tick-61 amendment: record the NAMED CPG-core cells (IN17A001/INXXX466/
IN16B036/IN19A007/IN19B012) through history/stop/post.

PREREG in l44/PREREG.md, written first. Machinery l43-verbatim except: free
settle, global 0.7 phase, no hop, per-arm entrain window. ONE generator + ONE
shared per-step noise tensor per seed (L36). CPU-only; no live changes.
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
WIN = 8000
STOP0, STOPD = 4000, 2000          # stop [4000,6000) = 20 s @ -8
ENT_AMP, ENT_F = 0.3, 0.7
REL_AMP = -8.0
HISTS = (0, 5, 10, 20, 40)          # seconds of entrain history
HSTEP = {h: h * 100 for h in HISTS}
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05        # l32 arm-A frozen (D inert per L35)
CORE_TYPES = ("IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012")
ARMS = [f"h{h}" for h in HISTS]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l32/l34/l39/l41-l43 verbatim) ----------
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
    xct = {a: {ct: np.zeros(WIN, np.float32) for ct in CORE_TYPES} for a in ARMS}

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
            for ct in CORE_TYPES:
                xct[a][ct][i] = X[a][CORE[ct]].mean()
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                mm=mm, tr=tr, x88=x88, xc=xc, xct=xct)


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l44/raw.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"fL_{a}_{s}": res[str(s)]["tr"][a]["fL"] for a in ARMS for s in SEEDS},
    **{f"fR_{a}_{s}": res[str(s)]["tr"][a]["fR"] for a in ARMS for s in SEEDS},
    **{f"eL_{a}_{s}": res[str(s)]["tr"][a]["eL"] for a in ARMS for s in SEEDS},
    **{f"eR_{a}_{s}": res[str(s)]["tr"][a]["eR"] for a in ARMS for s in SEEDS},
    **{f"x88_{a}_{s}": res[str(s)]["x88"][a] for a in ARMS for s in SEEDS},
    **{f"xc_{a}_{s}": res[str(s)]["xc"][a] for a in ARMS for s in SEEDS},
    **{f"xct_{ct}_{a}_{s}": res[str(s)]["xct"][a][ct]
       for a in ARMS for s in SEEDS for ct in CORE_TYPES})
log("raw.npz checkpointed")

# ---------------- analysis ----------------
def arm_metrics(a, s):
    r = res[s]
    late, f_late = rhythm2(r["mm"][a][STOP0 + STOPD - 500:STOP0 + STOPD])
    pre, _ = rhythm2(r["mm"][a][3500:4000])
    kill = next((c for c in range(STOPD // 100)
                 if rhythm2(r["mm"][a][STOP0 + c * 100:STOP0 + (c + 1) * 100])[0] < 5),
                None)
    fL, fR, eL, eR = (r["tr"][a][c] for c in ("fL", "fR", "eL", "eR"))
    S = np.full(WIN, np.nan)
    for t in range(499, WIN, 10):
        S[t] = S_of(fL[t - 499:t + 1] + fR[t - 499:t + 1],
                    eL[t - 499:t + 1] + eR[t - 499:t + 1])
    ts = np.arange(499, WIN, 10)
    S_during = float(np.nanmedian(S[ts[(ts >= STOP0) & (ts < STOP0 + STOPD)]]))
    S_after = float(np.nanmedian(S[ts[(ts >= STOP0 + STOPD) & (ts < STOP0 + STOPD + 3000)]]))
    xcv = r["xc"][a]
    core_ratio, f_core = rhythm2(xcv[STOP0 + STOPD - 500:STOP0 + STOPD])
    return dict(
        pre_ratio=round(pre, 1), late_ratio=round(late, 1), f_late=round(f_late, 3),
        kill_latency=kill, S_med_during=round(S_during, 3), S_med_after=round(S_after, 3),
        x88min=round(float(r["x88"][a][STOP0:STOP0 + STOPD].min()), 3),
        core_late_hist=round(float(xcv[3500:4000].mean()), 4),
        core_early_stop=round(float(xcv[STOP0:STOP0 + 200].mean()), 4),
        core_late_stop=round(float(xcv[STOP0 + STOPD - 200:STOP0 + STOPD].mean()), 4),
        core_ratio_late=round(core_ratio, 1), f_core_late=round(f_core, 3),
        core_types={ct: dict(hist=round(float(r["xct"][a][ct][3500:4000].mean()), 4),
                             stop=round(float(r["xct"][a][ct][
                                 STOP0 + STOPD - 200:STOP0 + STOPD].mean()), 4))
                    for ct in CORE_TYPES}), S


tbl, SR_all = {}, {}
for a in ARMS:
    tbl[a] = {}
    for s in SEEDS:
        m, S = arm_metrics(a, str(s))
        tbl[a][str(s)] = {k: v for k, v in m.items() if k != "core_types" and k != "S"}
        tbl[a][str(s)]["core_types"] = m["core_types"]
        SR_all[f"SR_{a}_{s}"] = S

# ---------------- verdict ----------------
def med(a, key):
    return float(np.median([tbl[a][str(s)][key] for s in SEEDS]))


c0_seeds = [s for s in SEEDS if tbl["h0"][str(s)]["late_ratio"] < 5
            and tbl["h0"][str(s)]["kill_latency"] is not None]
c0 = dict(killed_seeds=len(c0_seeds), pass_=len(c0_seeds) >= 2,
          latencies={str(s): tbl["h0"][str(s)]["kill_latency"] for s in SEEDS})

dm_land = {str(s): float(np.abs(res[str(s)]["mm"]["h40"] - res[str(s)]["mm"]["h0"])
                         [3500:4000].max()) for s in SEEDS}
prefix = {}
for h in (5, 10, 20):
    a = f"h{h}"
    prefix[f"h{h}_vs_h0_{4000 - h * 100}"] = max(
        float(np.abs(res[str(s)]["mm"][a][:4000 - h * 100]
                     - res[str(s)]["mm"]["h0"][:4000 - h * 100]).max()) for s in SEEDS)
c1 = dict(dm_land=dm_land, prefix_bitident=prefix,
          x88_unpin=all(tbl[a][str(s)]["x88min"] < 0.5 for a in ARMS for s in SEEDS),
          pass_=all(v > 0 for v in dm_land.values())
          and all(v == 0.0 for v in prefix.values())
          and all(tbl[a][str(s)]["x88min"] < 0.5 for a in ARMS for s in SEEDS))

curve = {a: dict(med_late=round(med(a, "late_ratio"), 1),
                 med_S_during=round(med(a, "S_med_during"), 3),
                 protected=sum(tbl[a][str(s)]["late_ratio"] >= 5 for s in SEEDS),
                 med_f_late=round(med(a, "f_late"), 3)) for a in ARMS}
gains = [curve[f"h{b}"]["med_late"] / max(curve[f"h{a}"]["med_late"], 0.1)
         for a, b in zip(HISTS, HISTS[1:])]
prots = [curve[f"h{h}"]["protected"] for h in HISTS]
threshold = any(g >= 10 and p1 <= 1 and p2 == 3
                for g, p1, p2 in zip(gains, prots, prots[1:]))
graded = ((len(set(prots)) >= 3) or (all(g < 10 for g in gains) and prots[-1] > prots[0]))
c2 = dict(curve=curve, gains=[round(g, 1) for g in gains],
          verdict=("THRESHOLD-basin-entry" if threshold else
                   "GRADED-resistance-curve" if graded else "MIXED"))

core_survive = core_specific = 0
for a in ARMS:
    for s in SEEDS:
        m = tbl[a][str(s)]
        if m["late_ratio"] >= 5:
            if m["core_ratio_late"] >= 5:
                core_survive += 1
            else:
                core_specific += 1
c3 = dict(protected_cellarm_pairs=core_survive + core_specific,
          core_survives_with_motor=core_survive, core_silenced_specifically=core_specific,
          note="in killed h0 seeds both die: "
               + str(sum(1 for s in SEEDS if tbl["h0"][str(s)]["late_ratio"] < 5
                         and tbl["h0"][str(s)]["core_ratio_late"] < 5)) + "/3")

verdict = dict(C0_anchor=c0, C1_drives=c1, C2_curve=c2, C3_core=c3)
log("VERDICT " + json.dumps(verdict)[:2400])

np.savez_compressed("l44/traces.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
                    **{f"xc_{a}_{s}": res[str(s)]["xc"][a] for a in ARMS for s in SEEDS},
                    **SR_all)
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, seeds=SEEDS,
                      ent_amp=ENT_AMP, ent_f=ENT_F, stop0=STOP0, stopd=STOPD,
                      rel_amp=REL_AMP, hists=list(HISTS), nodes=int(n),
                      edges=len(gsrc), core_counts=core_counts),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            table=tbl, verdict=verdict)
json.dump(dump, open("l44/results_l44.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l44/results_l44.json")
