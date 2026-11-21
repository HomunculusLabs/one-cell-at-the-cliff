"""L101 verdict: closure-pool-vocabulary tables + gates. PREREG l101/PREREG.md.

Part 1 = C0B certification (L85 rule): THIS script's generalized cells/table
code on stored raw_l94.npz must reproduce results_l94.json cfn reads EXACTLY
(Ti/Tr per-batch k/wilson/5 means, pooled 5 keys, anchor duty_07 pins,
lock_g1p cfn == 48) BEFORE any L101 number is pinned.
Part 2 = L101 reads from raw_l101.npz (5 pairs, both-sides + side cells).
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
MAP = {"f": "a", "e": "b"}  # l94 name -> l101 name
TS = np.arange(499, WIN, 10)

z94 = np.load("l94/raw_l94.npz")
r94 = json.load(open("l94/results_l94.json"))
ar = json.load(open("l101/anchors_run.json"))
STATIC = json.load(open("l101/static.json"))


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


SM = {}


def s_arrays(raw, s, pair, names94):
    key = (id(raw), s, pair, names94)
    if key not in SM:
        # names94: z94 stores l94 names fL/fR/eL/eR; z101 stores aL/aR/bL/bR
        def nm(c):
            if names94:
                return c  # fL / eL
            return ("a" if c[0] == "f" else "b") + c[1]
        tr = {c: raw[f"{pair}_{nm(c)}_cfn_{s}"][:WIN]
              for c in ("fL", "fR", "eL", "eR")}
        fL, fR, eL, eR = (tr[c] for c in ("fL", "fR", "eL", "eR"))
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = s_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
            SR[t] = s_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


def cells_of(raw, s, pair, names94=False):
    SL, SR = s_arrays(raw, s, pair, names94)
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

# ---------- Part 1: C0B certification on l94 (BEFORE any L101 pin) ----------
c0b_fail = []
CERT94 = {}
for pk in ("Ti", "Tr"):
    for s in ANCHOR + ALLFRESH:
        CERT94[(pk, s)] = cells_of(z94, s, pk, names94=True)


def seg2_of94(pair, s):
    SL, SR = s_arrays(z94, s, pair, names94=True)
    q = (TS >= 4500) & (TS < 6000)
    return round(float(np.nanmean(
        (SL[TS[q]] >= .25) & (SR[TS[q]] >= .25))), 3)


for pk in ("Ti", "Tr"):
    want = r94[f"table_{pk}"]["cfn"]
    for b, seeds in BATCHES.items():
        d07 = np.array([CERT94[(pk, s)]["duty_07"] for s in seeds])
        s1 = np.array([CERT94[(pk, s)]["seg1"] for s in seeds])
        dL = np.array([CERT94[(pk, s)]["duty07_L"] for s in seeds])
        dR = np.array([CERT94[(pk, s)]["duty07_R"] for s in seeds])
        s2 = np.array([seg2_of94(pk, s) for s in seeds])
        got = dict(
            k=int((d07 >= .5).sum()),
            wilson=wilson(int((d07 >= .5).sum()), 16),
            duty07_mean=round(float(d07.mean()), 3),
            seg1_mean=round(float(s1.mean()), 3),
            seg2_mean=round(float(s2.mean()), 3),
            duty07L_mean=round(float(dL.mean()), 3),
            duty07R_mean=round(float(dR.mean()), 3))
        for kk in ("k", "wilson", "duty07_mean", "seg1_mean", "seg2_mean",
                   "duty07L_mean", "duty07R_mean"):
            if got[kk] != want["per_batch"][b][kk]:
                c0b_fail.append((pk, b, kk, got[kk], want["per_batch"][b][kk]))
    kall = sum(1 for s in ALLFRESH if CERT94[(pk, s)]["duty_07"] >= .5)
    lb = wilson_lb_full(kall, N_POOL)
    for kk, vv in (("k", kall), ("n", N_POOL), ("lb_full", round(lb, 4)),
                   ("g2a_multi", bool(lb >= .717)), ("k_min", 41)):
        if vv != want["pooled"][kk]:
            c0b_fail.append((pk, "pooled", kk, vv, want["pooled"][kk]))
    for s in ANCHOR:
        if CERT94[(pk, s)]["duty_07"] != want["anchor"][str(s)]:
            c0b_fail.append((pk, f"anchor{s}", CERT94[(pk, s)]["duty_07"],
                             want["anchor"][str(s)]))
lock94 = int(sum(all(dom_ratio(z94[f"mm_cfn_{s}"][s0:s0 + 2000]) >= 10
                    for s0, _, _ in SEGB) for s in ALLFRESH))
if lock94 != r94["lock_g1p"]["cfn"]:
    c0b_fail.append(("lock", lock94, r94["lock_g1p"]["cfn"]))
c0b_pass = not c0b_fail
print("C0B certification:", "PASS" if c0b_pass else f"FAIL {c0b_fail[:6]}")

# ---------- Part 2: L101 reads ----------
z101 = np.load("l101/raw_l101.npz")
SM.clear()
CELLS = {pk: {s: cells_of(z101, s, pk) for s in ANCHOR + ALLFRESH}
         for pk in PAIRS}
lock101 = int(sum(all(dom_ratio(z101[f"mm_cfn_{s}"][s0:s0 + 2000]) >= 10
                     for s0, _, _ in SEGB) for s in ALLFRESH))

tables = {}
for pk in PAIRS:
    per_batch = {}
    for b, seeds in BATCHES.items():
        d07 = np.array([CELLS[pk][s]["duty_07"] for s in seeds])
        dL = np.array([CELLS[pk][s]["duty07_L"] for s in seeds])
        dR = np.array([CELLS[pk][s]["duty07_R"] for s in seeds])
        nan07 = int(sum(np.isnan(CELLS[pk][s]["duty_07"]) for s in seeds))
        per_batch[b] = dict(
            k=int((d07 >= .5).sum()),
            kL=int((dL >= .5).sum()), kR=int((dR >= .5).sum()),
            wilson=wilson(int((d07 >= .5).sum()), 16),
            duty07_mean=round(float(d07.mean()), 3),
            seg1_mean=round(float(np.mean(
                [CELLS[pk][s]["seg1"] for s in seeds])), 3),
            duty07L_mean=round(float(dL.mean()), 3),
            duty07R_mean=round(float(dR.mean()), 3))
    kall = sum(per_batch[b]["k"] for b in BATCHES)
    kL = sum(per_batch[b]["kL"] for b in BATCHES)
    kR = sum(per_batch[b]["kR"] for b in BATCHES)
    lb = wilson_lb_full(kall, N_POOL)
    lbL, lbR = wilson_lb_full(kL, N_POOL), wilson_lb_full(kR, N_POOL)
    tables[pk] = dict(
        per_batch=per_batch,
        pooled=dict(k=kall, n=N_POOL, lb_full=round(lb, 4),
                    g2a_multi=bool(lb >= .717)),
        side=dict(kL=kL, lbL=round(lbL, 4), g2aL=bool(lbL >= .717),
                  kR=kR, lbR=round(lbR, 4), g2aR=bool(lbR >= .717)),
        nan_seed_count=int(sum(np.isnan(CELLS[pk][s]["duty_07"])
                               for s in ALLFRESH)),
        k_spread=[per_batch[b]["k"] for b in BATCHES],
        seg1_spread=[per_batch[b]["seg1_mean"] for b in BATCHES],
        dutyL_spread=[per_batch[b]["duty07L_mean"] for b in BATCHES],
        dutyR_spread=[per_batch[b]["duty07R_mean"] for b in BATCHES],
        sizes={c: STATIC["sizes"][f"{pk}_{c}"]
               for c in ("aL", "aR", "bL", "bR")})

anchors_ok = (ar["c0a_pass"] and ar["c1"] and c0b_pass)
robust = [pk for pk in PAIRS if tables[pk]["pooled"]["g2a_multi"]]
robust_side = [(pk, side) for pk in PAIRS
               for side in ("L", "R") if tables[pk]["side"][f"g2a{side}"]]
if not anchors_ok:
    verdict = f"ANCHOR-FAIL c0a={ar['c0a_pass']} c1={ar['c1']} c0b={c0b_pass}"
else:
    verdict = (
        f"vocabulary robust base pair: "
        f"{'NONE — closure claim now vocabulary-wide' if not robust else robust}"
        f" | side-cell clears: {robust_side or 'none'}"
        f" | lock {lock101}/48")

out = dict(meta=dict(pairs=PAIRS, n_pool=N_POOL, substrate="closure l92"),
           anchors=dict(c0a=ar["c0a_pass"], c0a_max=ar["c0a_max"],
                        c1=ar["c1"], c0b=c0b_pass, c0b_fails=c0b_fail[:8],
                        lock=lock101),
           tables=tables, robust=robust, robust_side=robust_side,
           verdict=verdict)
json.dump(out, open("l101/results_l101.json", "w"), indent=1)
print(verdict)
for pk in PAIRS:
    t = tables[pk]
    print(f"{pk}: k {t['k_spread']} pooled {t['pooled']['k']}/48 "
          f"lb {t['pooled']['lb_full']} | L {t['dutyL_spread']} "
          f"R {t['dutyR_spread']} kL {t['side']['kL']} kR {t['side']['kR']} "
          f"lbL {t['side']['lbL']} lbR {t['side']['lbR']} "
          f"| seg1 {t['seg1_spread']} | nan {t['nan_seed_count']} "
          f"| sizes {t['sizes']}")
