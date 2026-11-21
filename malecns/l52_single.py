"""L52: why-is-fast-segment-toxic (LANE.md ideas-25).

LONG single-frequency treatment (60 s, no transitions) from the shared h40
state: is the continuous-1.4 collapse a RE-LOCK TRANSIENT (recovers with
dwell) or a SELECTED attractor (held low)? 0.7 control arm is
schedule-identical to l49 cont through step 10000 (bit-identity anchor).
Amp sweep {.1,.2,.3} x {0.7,1.4} ships the t70 HOLDS/SHIFTED/FLIPS
sensitivity table.

PREREG l52/PREREG.md written first. Raw npz checkpoint BEFORE analysis.
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
HIST = 4000                          # shared h40 history [0,4000)
WIN = 10000                          # 100 s: 40 history + 60 treatment
TRE = (HIST, WIN)                    # treatment window
AMPS = (0.3, 0.2, 0.1)
FREQS = (0.7, 1.4)
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05         # l32 arm-A frozen
BIN = 600                            # 6-s duty bins
LOCK_TOL = 0.10
ARMS = ["f07a3"]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l32/l34/l39-l51 verbatim) ----------
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
lnt = nt_names[keep]
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

# ---------- per-arm AMP / FREQ tables (no inline conditionals) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
FRQA = {a: np.full(WIN, 0.7, np.float64) for a in ARMS}
for a in ARMS:
    f, am = float(a[1] + "." + a[2]), float("0." + a[4:])
    assert (f, am) in [(ff, aa) for ff in FREQS for aa in AMPS], a
    AMPA[a][:HIST] = 0.3                       # shared h40 history, amp .3
    AMPA[a][TRE[0]:TRE[1]] = am                # treatment amp
    FRQA[a][TRE[0]:TRE[1]] = f                 # treatment frequency
# write-time wiring asserts
for a in ARMS:
    assert (AMPA[a][:HIST] == 0.3).all()
    am = float("0." + a[4:])
    assert (AMPA[a][HIST:WIN] == am).all()
    assert FRQA[a][0] == 0.7 and FRQA[a][WIN - 1] == float(a[1] + "." + a[2])
assert (FRMA := FRQA["f07a3"]) is not None and (FRMA == 0.7).all()   # anchor arm
assert (AMPA["f07a3"] == 0.3).all()                                  # == l49 cont
log("arm tables ok: " + " ".join(ARMS))


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
    ph = {a: 0.0 for a in ARMS}                 # single accumulator per arm
    for _ in range(SETTLE):                     # settle: 0.7 Hz, amp .3
        for a in ARMS:
            ph[a] += 2 * math.pi * 0.7 * DT
    SIGS = ("fL", "fR", "eL", "eR")
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    dm = dict(first_div=-1, vmax=0.0)

    def step_all(k):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        for a in ARMS:
            f_k = 0.7 if k < 0 else FRQA[a][k]
            ph[a] += 2 * math.pi * f_k * DT
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if k >= 0:                          # l49: settle is drive-free
                amp_k = float(AMPA[a][k])
                if amp_k > 0.0:
                    drive[mech, 0] = drive[mech, 0] + amp_k * (
                        0.5 + 0.5 * math.sin(ph[a]))
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
        if False:
            d = float((X["f14a3"] - X["f07a3"]).abs().max())
            dm["vmax"] = max(dm["vmax"], d)
            if d > 1e-6 and dm["first_div"] < 0:
                dm["first_div"] = i
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                dm=dm, mm=mm, tr=tr, ph_end={a: ph[a] for a in ARMS})


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# raw checkpoint BEFORE analysis (L45a lesson), all analysis-consumable pools
np.savez_compressed(
    "l52/raw_l52.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")})
log("raw_l52.npz checkpointed")

# ---------------- C0 anchor vs l49 cont ----------------
z49 = np.load("l49/traces_l49.npz")
c0 = {}
for s in SEEDS:
    c0[f"mm_s{s}"] = float(np.abs(res[str(s)]["mm"]["f07a3"][:WIN]
                                  - z49[f"mm_cont_{s}"][:WIN]).max())
TS49 = np.arange(499, 18000, 10)


def s_pair(a, s):
    fL, fR = res[str(s)]["tr"][a]["fL"], res[str(s)]["tr"][a]["fR"]
    eL, eR = res[str(s)]["tr"][a]["eL"], res[str(s)]["tr"][a]["eR"]
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in np.arange(499, WIN, 10):
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    return SL, SR


SM = {}
for s in SEEDS:                                   # SL/SR anchor on the same window
    SL49, SR49 = z49[f"SL_cont_{s}"], z49[f"SR_cont_{s}"]
    SL, SR = s_pair("f07a3", s)
    SM[("f07a3", s)] = (SL, SR)
    c0[f"SL_s{s}"] = float(np.nanmax(np.abs(SL[:WIN] - SL49[:WIN])))
    c0[f"SR_s{s}"] = float(np.nanmax(np.abs(SR[:WIN] - SR49[:WIN])))
c0_pass = all(v == 0.0 for v in c0.values())
log("C0 " + json.dumps(c0) + f" pass={c0_pass}")

# ---------------- C1 wiring ----------------
fd = [res[str(s)]["dm"]["first_div"] for s in SEEDS]
vm = [res[str(s)]["dm"]["vmax"] for s in SEEDS]
c1 = dict(af_ok=all(0.01 < res[str(s)]["af"][a] < 0.9
                    for s in SEEDS for a in ARMS),
          first_div=fd, want=HIST, vmax=[round(v, 4) for v in vm],
          ph_continuous=True)
c1["pass_"] = (all(v == HIST for v in fd) and all(v > 1e-6 for v in vm)
               and c1["af_ok"])

# ---------------- duty-vs-dwell analysis ----------------
TS = np.arange(499, WIN, 10)


def arrs(a, s):
    if (a, s) not in SM:
        SM[(a, s)] = s_pair(a, s)
    return SM[(a, s)]


def duty_in(SL, SR, lo, hi):
    q = (TS >= lo) & (TS < hi)
    return float(np.nanmean((SL[TS[q]] >= .25) & (SR[TS[q]] >= .25)))


rows = {}
for a in ARMS:
    for s in SEEDS:
        SL, SR = arrs(a, s)
        bins = [round(duty_in(SL, SR, HIST + i * BIN, HIST + (i + 1) * BIN), 3)
                for i in range((WIN - HIST) // BIN)]
        early = duty_in(SL, SR, HIST, HIST + 3000)
        late = duty_in(SL, SR, HIST + 3000, WIN)
        fh, ratio = dom_freq(res[str(s)]["mm"][a][HIST:WIN])
        tgt = float(a[1] + "." + a[2])
        fh_e, _ = dom_freq(res[str(s)]["mm"][a][HIST:HIST + 3000])
        fh_l, _ = dom_freq(res[str(s)]["mm"][a][HIST + 3000:WIN])
        rows.setdefault(a, {})[str(s)] = dict(
            bins=bins, early=round(early, 3), late=round(late, 3),
            slope=round(late - early, 3),
            f=round(fh, 3), err=round(abs(fh - tgt), 3), tgt=tgt,
            f_early=round(fh_e, 3), f_late=round(fh_l, 3),
            ratio=round(ratio, 1),
            SL_med=round(float(np.nanmedian(SL[TS[(TS >= HIST) & (TS < WIN)]])), 3),
            SR_med=round(float(np.nanmedian(SR[TS[(TS >= HIST) & (TS < WIN)]])), 3))

# GC control gate (anchor-derived expectation, PREREG)
gc = {str(s): rows["f07a3"][str(s)] for s in SEEDS}
gc_exp = {"11": .360, "22": .645, "33": .112}
gc_pass = all(abs(gc[s]["early"] if False else
                  duty_in(*arrs("f07a3", int(s)), HIST, WIN) - gc_exp[s]) < 1e-9
              for s in ("11", "22", "33"))
gc_vals = {s: round(duty_in(*arrs("f07a3", int(s)), HIST, WIN), 3)
           for s in ("11", "22", "33")}

# G gates on the canonical arm f14a3
g = rows["f14a3"]
g_trans = all(g[str(s)]["late"] >= .25 and g[str(s)]["slope"] >= .20
              for s in SEEDS)
g_select = all(g[str(s)]["late"] < .15 and all(b <= .10 for b in g[str(s)]["bins"])
               for s in SEEDS)
if g_trans and not g_select:
    verdict = "TRANSIENT (settles with dwell)"
elif g_select and not g_trans:
    verdict = "SELECTION (held-low whole segment)"
elif g_trans and g_select:
    verdict = "CONTRADICTION (check gates)"
else:
    verdict = "MIXED (table delivered)"

# sensitivity table (t70 rule): amp x freq -> label vs canonical verdict
sens = {}
for f in FREQS:
    for am in AMPS:
        a = f"f{int(f*10):02d}a{int(am*10)}"
        r = rows[a]
        locked = {s: r[s]["err"] <= LOCK_TOL for s in map(str, SEEDS)}
        lab = {s: ("LOCKED" if locked[s] else "UNLOCKED") for s in locked}
        sens[a] = dict(
            duty_early=round(float(np.mean([r[s]["early"] for s in map(str, SEEDS)])), 3),
            duty_late=round(float(np.mean([r[s]["late"] for s in map(str, SEEDS)])), 3),
            slope=round(float(np.mean([r[s]["slope"] for s in map(str, SEEDS)])), 3),
            err={s: r[s]["err"] for s in map(str, SEEDS)},
            lock=lab,
            verdict="UNLOCKED" if not any(locked.values()) else (
                "transient-like" if all(r[s]["late"] >= .25 for s in map(str, SEEDS))
                else ("selection-like" if all(r[s]["late"] < .15 for s in map(str, SEEDS))
                      else "mixed")))
canon = sens["f14a3"]["verdict"]
for a in sens:
    if a == "f14a3" or sens[a]["verdict"] == "UNLOCKED":
        sens[a]["knob"] = "canonical" if a == "f14a3" else "unlocked-moot"
    else:
        sens[a]["knob"] = ("HOLDS" if sens[a]["verdict"] == canon
                           else "FLIPS" if sens[a]["verdict"] in
                           ("transient-like", "selection-like")
                           else "SHIFTED")

dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, hist=HIST,
                      bin=BIN, seeds=SEEDS, amps=AMPS, freqs=FREQS, arms=ARMS,
                      nodes=int(n), edges=len(gsrc)),
            C0=c0, C0_pass=bool(c0_pass), C1=c1,
            GC=dict(expect=gc_exp, got=gc_vals, pass_=bool(gc_pass)),
            rows={a: {s: rows[a][s] for s in map(str, SEEDS)} for a in ARMS},
            gates=dict(G_TRANSIENT=bool(g_trans), G_SELECTION=bool(g_select)),
            verdict=verdict, sensitivity=sens, canonical=canon,
            ph_end={str(s): res[str(s)]["ph_end"] for s in SEEDS},
            predictions=dict(P1_selection=bool(g_select and not g_trans),
                             P2_gc=bool(gc_pass),
                             P3_low_amp_unlock=not any(
                                 sens[f"f14a{int(am*10)}"]["lock"][s] == "LOCKED"
                                 for am in (.1, .2) for s in map(str, SEEDS))))
json.dump(dump, open("l52/results_l52.json", "w"), indent=1)
np.savez_compressed("l52/traces_l52.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
                       for a in ARMS for s in SEEDS},
                    **{f"SL_{a}_{s}": arrs(a, s)[0] for a in ARMS for s in SEEDS},
                    **{f"SR_{a}_{s}": arrs(a, s)[1] for a in ARMS for s in SEEDS})
log(f"C0={c0_pass} C1={c1['pass_']} GC={gc_pass} {gc_vals}")
log(f"G_TRANSIENT={g_trans} G_SELECTION={g_select} verdict={verdict}")
log(f"sensitivity: {json.dumps(sens)[:900]}")
log(f"done {time.time()-t0:.0f}s -> l52/results_l52.json")
