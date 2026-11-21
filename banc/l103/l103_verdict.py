"""L103 verdict: unpaired-pool tables + gates. PREREG l103/PREREG.md.

Part 1 = C0B certification (L85 rule): THIS script's l101-verbatim
cells/table code on stored raw_l101.npz must reproduce results_l101.json
EXACTLY (5 pairs: per-batch 7 reads, pooled 5 keys, side 6 keys,
nan_seed_count, lock) BEFORE any L103 number is pinned.
Part 2 = L103 reads from raw_l103.npz (LR cells + alive cells + FlyHack
phase-shift secondary + sustain fractions).
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0, BLK = 500, 500
ANCHOR = [11, 22, 33]
B4 = list(range(801, 817))
B5 = list(range(901, 917))
B6 = list(range(1001, 1017))
BATCHES = {"B4": B4, "B5": B5, "B6": B6}
ALLFRESH = B4 + B5 + B6
N_POOL = len(ALLFRESH)
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
UNPAIRED = ["LT", "FR"]
TS = np.arange(499, WIN, 10)

z101 = np.load("l101/raw_l101.npz")
r101 = json.load(open("l101/results_l101.json"))
ar = json.load(open("l103/anchors_run.json"))
STATIC = json.load(open("l103/static.json"))


def s_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 \
        else float("nan")


def dom_ratio(x):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= 0.3) & (fr <= 10)
    return float(ps[band].max() / max(np.median(ps[band]), 1e-30))


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(c - hw, 3), round(c + hw, 3)]


def wilson_lb_full(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - hw


assert wilson_lb_full(41, 48) >= .717 > wilson_lb_full(40, 48)

# ---------- Part 1: C0B certification on l101 (BEFORE any L103 pin) ----------
SM = {}


def s_arrays(raw, s, pair):
    key = (id(raw), s, pair)
    if key not in SM:
        tr = {c: raw[f"{pair}_{c}_cfn_{s}"][:WIN]
              for c in ("aL", "aR", "bL", "bR")}
        fL, fR, eL, eR = (tr[c] for c in ("aL", "aR", "bL", "bR"))
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = s_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
            SR[t] = s_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


def cells_of(raw, s, pair):
    SL, SR = s_arrays(raw, s, pair)
    qall = np.zeros(len(TS), bool)
    q07 = np.zeros(len(TS), bool)
    for a0_, b0, f in SEGB:
        qall |= (TS >= a0_ + MEAS0) & (TS < b0)
        if f == 0.7:
            q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
    L07 = (SL[TS[q07]] >= .25)
    R07 = (SR[TS[q07]] >= .25)
    return dict(
        duty_07=round(float(np.nanmean(L07 & R07)), 3),
        duty07_L=round(float(np.nanmean(L07)), 3),
        duty07_R=round(float(np.nanmean(R07)), 3),
        seg1=round(float(np.nanmean(
            (SL[TS[(TS >= 2500) & (TS < 4000)]] >= .25)
            & (SR[TS[(TS >= 2500) & (TS < 4000)]] >= .25))), 3))


c0b_fail = []
CERT = {pk: {s: cells_of(z101, s, pk) for s in ANCHOR + ALLFRESH}
        for pk in PAIRS}
for pk in PAIRS:
    want = r101["tables"][pk]
    for b, seeds in BATCHES.items():
        d07 = np.array([CERT[pk][s]["duty_07"] for s in seeds])
        dL = np.array([CERT[pk][s]["duty07_L"] for s in seeds])
        dR = np.array([CERT[pk][s]["duty07_R"] for s in seeds])
        s1 = np.array([CERT[pk][s]["seg1"] for s in seeds])
        got = dict(
            k=int((d07 >= .5).sum()),
            kL=int((dL >= .5).sum()), kR=int((dR >= .5).sum()),
            wilson=wilson(int((d07 >= .5).sum()), 16),
            duty07_mean=round(float(d07.mean()), 3),
            seg1_mean=round(float(s1.mean()), 3),
            duty07L_mean=round(float(dL.mean()), 3),
            duty07R_mean=round(float(dR.mean()), 3))
        for kk in ("k", "kL", "kR", "wilson", "duty07_mean", "seg1_mean",
                   "duty07L_mean", "duty07R_mean"):
            if got[kk] != want["per_batch"][b][kk]:
                c0b_fail.append((pk, b, kk, got[kk], want["per_batch"][b][kk]))
    kall = sum(1 for s in ALLFRESH if CERT[pk][s]["duty_07"] >= .5)
    kL = sum(1 for s in ALLFRESH if CERT[pk][s]["duty07_L"] >= .5)
    kR = sum(1 for s in ALLFRESH if CERT[pk][s]["duty07_R"] >= .5)
    lb = wilson_lb_full(kall, N_POOL)
    for kk, vv in (("k", kall), ("n", N_POOL), ("lb_full", round(lb, 4)),
                   ("g2a_multi", bool(lb >= .717))):
        if vv != want["pooled"][kk]:
            c0b_fail.append((pk, "pooled", kk, vv, want["pooled"][kk]))
    lbL, lbR = wilson_lb_full(kL, N_POOL), wilson_lb_full(kR, N_POOL)
    for kk, vv in (("kL", kL), ("lbL", round(lbL, 4)),
                   ("g2aL", bool(lbL >= .717)), ("kR", kR),
                   ("lbR", round(lbR, 4)), ("g2aR", bool(lbR >= .717))):
        if vv != want["side"][kk]:
            c0b_fail.append((pk, "side", kk, vv, want["side"][kk]))
    nanct = int(sum(np.isnan(CERT[pk][s]["duty_07"]) for s in ALLFRESH))
    if nanct != want["nan_seed_count"]:
        c0b_fail.append((pk, "nan", nanct, want["nan_seed_count"]))
lock101 = int(sum(all(dom_ratio(z101[f"mm_cfn_{s}"][s0:s0 + 2000]) >= 10
                     for s0, _, _ in SEGB) for s in ALLFRESH))
if lock101 != r101["anchors"]["lock"]:
    c0b_fail.append(("lock", lock101, r101["anchors"]["lock"]))
c0b_pass = not c0b_fail
print("C0B certification:", "PASS" if c0b_pass else f"FAIL {c0b_fail[:6]}")

# ---------- Part 2: L103 reads (LR cells + alive + FlyHack secondary) ----------
z103 = np.load("l103/raw_l103.npz")
SM.clear()
SHIFTS = [500, 100, 300, 700, 900]  # 500 = registered carrier; rest descriptive


def lr_arrays(raw, s, pool, shift=0):
    key = (id(raw), s, pool, shift)
    if key not in SM:
        L = raw[f"{pool}_L_cfn_{s}"][:WIN]
        R = raw[f"{pool}_R_cfn_{s}"][:WIN]
        if shift:
            R = np.roll(R, shift)
        S = np.full(WIN, np.nan)
        for t in TS:
            S[t] = s_of(L[t - 499:t + 1], R[t - 499:t + 1])
        SM[key] = S
    return SM[key]


def qmask(f=.7):
    q = np.zeros(len(TS), bool)
    for a0_, b0, ff in SEGB:
        if ff == f:
            q |= (TS >= a0_ + MEAS0) & (TS < b0)
    return q


Q07 = qmask(0.7)
Q07_T = TS[Q07]


def cells_lr(raw, s, pool, shift=0):
    S = lr_arrays(raw, s, pool, shift)
    ok = (S[Q07_T] >= .25)
    L = raw[f"{pool}_L_cfn_{s}"][:WIN]
    R = raw[f"{pool}_R_cfn_{s}"][:WIN]
    aliveL = float(np.mean(L[Q07_T] >= .05))
    aliveR = float(np.mean(R[Q07_T] >= .05))
    q1 = (TS >= 2500) & (TS < 4000)
    return dict(
        duty_07=round(float(np.nanmean(ok)), 3),
        seg1=round(float(np.nanmean(S[TS[q1]] >= .25)), 3),
        alive07_L=round(aliveL, 3), alive07_R=round(aliveR, 3))


CELLS = {p: {s: cells_lr(z103, s, p) for s in ANCHOR + ALLFRESH}
         for p in UNPAIRED}
SHUF = {p: {s: cells_lr(z103, s, p, shift=500) for s in ALLFRESH}
        for p in UNPAIRED}
SHUF_EXTRA = {p: {sh: round(float(np.mean([cells_lr(z103, s, p, shift=sh)
                                           ["duty_07"] for s in ALLFRESH])), 3)
                  for sh in SHIFTS[1:]} for p in UNPAIRED}
lock103 = int(sum(all(dom_ratio(z103[f"mm_cfn_{s}"][s0:s0 + 2000]) >= 10
                      for s0, _, _ in SEGB) for s in ALLFRESH))

tables = {}
for p in UNPAIRED:
    per_batch = {}
    for b, seeds in BATCHES.items():
        d07 = np.array([CELLS[p][s]["duty_07"] for s in seeds])
        aL = np.array([CELLS[p][s]["alive07_L"] for s in seeds])
        aR = np.array([CELLS[p][s]["alive07_R"] for s in seeds])
        per_batch[b] = dict(
            k=int((d07 >= .5).sum()),
            kL=int((aL >= .5).sum()), kR=int((aR >= .5).sum()),
            wilson=wilson(int((d07 >= .5).sum()), 16),
            duty07_mean=round(float(d07.mean()), 3),
            seg1_mean=round(float(np.mean(
                [CELLS[p][s]["seg1"] for s in seeds])), 3),
            alive07L_mean=round(float(aL.mean()), 3),
            alive07R_mean=round(float(aR.mean()), 3))
    kall = sum(per_batch[b]["k"] for b in BATCHES)
    kL = sum(per_batch[b]["kL"] for b in BATCHES)
    kR = sum(per_batch[b]["kR"] for b in BATCHES)
    lb = wilson_lb_full(kall, N_POOL)
    lbL, lbR = wilson_lb_full(kL, N_POOL), wilson_lb_full(kR, N_POOL)
    real_mean = round(float(np.mean([CELLS[p][s]["duty_07"]
                                     for s in ALLFRESH])), 3)
    shuf_mean = round(float(np.mean([SHUF[p][s]["duty_07"]
                                     for s in ALLFRESH])), 3)
    tables[p] = dict(
        per_batch=per_batch,
        pooled=dict(k=kall, n=N_POOL, p_hat=round(kall / N_POOL, 4),
                    lb_full=round(lb, 4), g2a_multi=bool(lb >= .717)),
        sustain_frac=round(
            sum(per_batch[b]["k"] >= 8 for b in BATCHES) / 3, 3),
        k_spread=[per_batch[b]["k"] for b in BATCHES],
        seg1_spread=[per_batch[b]["seg1_mean"] for b in BATCHES],
        alive=dict(kL=kL, lbL=round(lbL, 4), g2aL=bool(lbL >= .717),
                   kR=kR, lbR=round(lbR, 4), g2aR=bool(lbR >= .717),
                   spreadL=[per_batch[b]["alive07L_mean"] for b in BATCHES],
                   spreadR=[per_batch[b]["alive07R_mean"] for b in BATCHES]),
        flyhack=dict(real_mean=real_mean, shift500_mean=shuf_mean,
                     margin=round(real_mean - shuf_mean, 3),
                     secondary_pass=bool(real_mean - shuf_mean >= .20),
                     extra_shifts=SHUF_EXTRA[p]),
        nan_seed_count=int(sum(np.isnan(CELLS[p][s]["duty_07"])
                               for s in ALLFRESH)),
        sizes={c: STATIC["sizes"][f"{p}_{c}"] for c in ("L", "R")})

anchors_ok = (ar["c0a_pass"] and ar["c1"] and c0b_pass)
clears = [p for p in UNPAIRED if tables[p]["pooled"]["g2a_multi"]]
if not anchors_ok:
    verdict = (f"ANCHOR-FAIL c0a={ar['c0a_pass']} c1={ar['c1']} "
               f"c0b={c0b_pass}")
else:
    if clears:
        # secondary check is verdict-carrier only now (FlyHack, registered)
        held = [p for p in clears if tables[p]["flyhack"]["secondary_pass"]]
        none_msg = "NONE (primary clear did not survive the phase-shift null)"
        verdict = (f"second life sign: {clears} clear G2a-multi; "
                   f"secondary-checked {held or none_msg}")
    else:
        verdict = ("motor vocabulary COMPLETE under the registered LR cell: "
                   "no unpaired pool clears G2a-multi — no robust base "
                   "anywhere but l65's Ti; closure endgame closed as a base "
                   "substrate (caveat: unpaired cell = contralateral-"
                   "homologue anticorrelation, a definitional port from the "
                   "paired-pool cell)")

out = dict(meta=dict(pools=UNPAIRED, cell="S_LR contralateral homologue",
                     n_pool=N_POOL, substrate="closure l92"),
           anchors=dict(c0a=ar["c0a_pass"], c0a_max=ar["c0a_max"],
                        c1=ar["c1"], c0b=c0b_pass, c0b_fails=c0b_fail[:8],
                        lock=lock103),
           tables=tables, clears=clears, verdict=verdict)
json.dump(out, open("l103/results_l103.json", "w"), indent=1)
print(verdict)
for p in UNPAIRED:
    t = tables[p]
    f = t["flyhack"]
    print(f"{p}: k {t['k_spread']} pooled {t['pooled']['k']}/48 "
          f"lb {t['pooled']['lb_full']} sustain {t['sustain_frac']} "
          f"| seg1 {t['seg1_spread']} | alive L {t['alive']['spreadL']} "
          f"R {t['alive']['spreadR']} kL {t['alive']['kL']} "
          f"kR {t['alive']['kR']} | flyhack real {f['real_mean']} "
          f"shuf {f['shift500_mean']} margin {f['margin']} "
          f"extra {f['extra_shifts']} | nan {t['nan_seed_count']} "
          f"| sizes {t['sizes']}")
