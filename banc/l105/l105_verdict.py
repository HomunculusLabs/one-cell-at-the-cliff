"""L105 verdict: free-run tables + gates. PREREG l105/PREREG.md.

Part 1 = C0B certification (L85 rule): THIS script's cells/table code on
stored raw_l101.npz must reproduce results_l101.json (5 pairs: per-batch 7
reads, pooled, side, nan, lock) AND on raw_l103.npz reproduce results_l103.json
(LT/FR: per-batch k, pooled, flyhack real/shift/margin) EXACTLY — BEFORE any
L105 number is pinned.
Part 2 = L105 reads from raw_l105.npz: free/freenod arms, paired cells (5
pairs) + LR cells (LT/FR), P1 gate, P2 bit-identity, P3 FlyHack secondary,
P4 paired deltas free-cfn.
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
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
z103 = np.load("l103/raw_l103.npz")
r103 = json.load(open("l103/results_l103.json"))
ar = json.load(open("l105/anchors_run.json"))


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

SM = {}


def s_arrays(raw, s, pair, arm="cfn"):
    key = (id(raw), s, pair, arm)
    if key not in SM:
        tr = {c: raw[f"{pair}_{('a' if c[0] == 'f' else 'b')}{c[1]}_{arm}_{s}"][:WIN]
              for c in ("fL", "fR", "eL", "eR")}
        fL, fR, eL, eR = (tr[c] for c in ("fL", "fR", "eL", "eR"))
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = s_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
            SR[t] = s_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


def cells_of(raw, s, pair, arm="cfn"):
    SL, SR = s_arrays(raw, s, pair, arm)
    q07 = np.zeros(len(TS), bool)
    for a0_, b0, f in SEGB:
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


def lr_arrays(raw, s, pool, arm="cfn", shift=0):
    key = (id(raw), s, pool, arm, shift)
    if key not in SM:
        L = raw[f"{pool}_L_{arm}_{s}"][:WIN]
        R = raw[f"{pool}_R_{arm}_{s}"][:WIN]
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


def cells_lr(raw, s, pool, arm="cfn", shift=0):
    S = lr_arrays(raw, s, pool, arm, shift)
    ok = (S[Q07_T] >= .25)
    L = raw[f"{pool}_L_{arm}_{s}"][:WIN]
    R = raw[f"{pool}_R_{arm}_{s}"][:WIN]
    return dict(
        duty_07=round(float(np.nanmean(ok)), 3),
        alive07_L=round(float(np.mean(L[Q07_T] >= .05)), 3),
        alive07_R=round(float(np.mean(R[Q07_T] >= .05)), 3))


def lock_of(raw, arm):
    return int(sum(all(dom_ratio(raw[f"mm_{arm}_{s}"][s0:s0 + 2000]) >= 10
                       for s0, _, _ in SEGB) for s in ALLFRESH))


# ---------- Part 1: C0B certification BEFORE any L105 pin ----------
c0b_fail = []
CERT = {pk: {s: cells_of(z101, s, pk) for s in ANCHOR + ALLFRESH}
        for pk in PAIRS}
for pk in PAIRS:
    want = r101["tables"][pk]
    for b, seeds in BATCHES.items():
        d07 = np.array([CERT[pk][s]["duty_07"] for s in seeds])
        dL = np.array([CERT[pk][s]["duty07_L"] for s in seeds])
        dR = np.array([CERT[pk][s]["duty07_R"] for s in seeds])
        got = dict(
            k=int((d07 >= .5).sum()),
            kL=int((dL >= .5).sum()), kR=int((dR >= .5).sum()),
            wilson=wilson(int((d07 >= .5).sum()), 16),
            duty07_mean=round(float(d07.mean()), 3),
            seg1_mean=round(float(np.mean(
                [CERT[pk][s]["seg1"] for s in seeds])), 3),
            duty07L_mean=round(float(dL.mean()), 3),
            duty07R_mean=round(float(dR.mean()), 3))
        for kk in ("k", "kL", "kR", "wilson", "duty07_mean", "seg1_mean",
                   "duty07L_mean", "duty07R_mean"):
            if got[kk] != want["per_batch"][b][kk]:
                c0b_fail.append(("l101", pk, b, kk, got[kk],
                                 want["per_batch"][b][kk]))
    kall = sum(1 for s in ALLFRESH if CERT[pk][s]["duty_07"] >= .5)
    kL = sum(1 for s in ALLFRESH if CERT[pk][s]["duty07_L"] >= .5)
    kR = sum(1 for s in ALLFRESH if CERT[pk][s]["duty07_R"] >= .5)
    lb, lbL, lbR = (wilson_lb_full(kall, N_POOL), wilson_lb_full(kL, N_POOL),
                    wilson_lb_full(kR, N_POOL))
    for kk, vv in (("k", kall), ("n", N_POOL), ("lb_full", round(lb, 4)),
                   ("g2a_multi", bool(lb >= .717)),
                   ("kL", kL), ("lbL", round(lbL, 4)),
                   ("g2aL", bool(lbL >= .717)), ("kR", kR),
                   ("lbR", round(lbR, 4)), ("g2aR", bool(lbR >= .717)),
                   ("nan_seed_count",
                    int(sum(np.isnan(CERT[pk][s]["duty_07"])
                            for s in ALLFRESH)))):
        ref = want["pooled"].get(kk, want["side"].get(kk, want.get(kk)))
        if vv != ref:
            c0b_fail.append(("l101", pk, "pooled/side/table", kk, vv, ref))
lock101 = lock_of(z101, "cfn")
if lock101 != r101["anchors"]["lock"]:
    c0b_fail.append(("l101", "lock", lock101, r101["anchors"]["lock"]))
# l103 LR cert
for p in UNPAIRED:
    want = r103["tables"][p]
    got_cells = {s: cells_lr(z103, s, p) for s in ALLFRESH}
    got_cells_sh = {s: cells_lr(z103, s, p, shift=500) for s in ALLFRESH}
    for b, seeds in BATCHES.items():
        k = int(sum(got_cells[s]["duty_07"] >= .5 for s in seeds))
        if k != want["per_batch"][b]["k"]:
            c0b_fail.append(("l103", p, b, "k", k, want["per_batch"][b]["k"]))
    kall = sum(got_cells[s]["duty_07"] >= .5 for s in ALLFRESH)
    real_mean = round(float(np.mean(
        [got_cells[s]["duty_07"] for s in ALLFRESH])), 3)
    shuf_mean = round(float(np.mean(
        [got_cells_sh[s]["duty_07"] for s in ALLFRESH])), 3)
    f = want["flyhack"]
    if (kall, want["pooled"]["n"]) != (want["pooled"]["k"], N_POOL):
        c0b_fail.append(("l103", p, "pooled.k", kall, want["pooled"]["k"]))
    if real_mean != f["real_mean"]:
        c0b_fail.append(("l103", p, "real_mean", real_mean, f["real_mean"]))
    if shuf_mean != f["shift500_mean"]:
        c0b_fail.append(("l103", p, "shift500_mean", shuf_mean,
                         f["shift500_mean"]))
c0b_pass = not c0b_fail
print("C0B certification:", "PASS" if c0b_pass else f"FAIL {c0b_fail[:6]}")

# ---------- Part 2: L105 reads ----------
z = np.load("l105/raw_l105.npz")
SM.clear()
tables = {}
for arm in ("free", "freenod"):
    CELLS = {pk: {s: cells_of(z, s, pk, arm) for s in ANCHOR + ALLFRESH}
             for pk in PAIRS}
    per = {}
    for pk in PAIRS:
        per_batch = {}
        for b, seeds in BATCHES.items():
            d07 = np.array([CELLS[pk][s]["duty_07"] for s in seeds])
            per_batch[b] = dict(
                k=int((d07 >= .5).sum()),
                wilson=wilson(int((d07 >= .5).sum()), 16),
                duty07_mean=round(float(d07.mean()), 3),
                seg1_mean=round(float(np.mean(
                    [CELLS[pk][s]["seg1"] for s in seeds])), 3))
        kall = sum(per_batch[b]["k"] for b in BATCHES)
        lb = wilson_lb_full(kall, N_POOL)
        per[pk] = dict(per_batch=per_batch,
                       pooled=dict(k=kall, n=N_POOL, p_hat=round(kall / N_POOL, 4),
                                   lb_full=round(lb, 4),
                                   g2a_multi=bool(lb >= .717)),
                       k_spread=[per_batch[b]["k"] for b in BATCHES],
                       nan_seed_count=int(sum(np.isnan(CELLS[pk][s]["duty_07"])
                                              for s in ALLFRESH)))
    # unpaired LR cells + flyhack shift-500 for this arm
    lr = {}
    for p in UNPAIRED:
        cells = {s: cells_lr(z, s, p, arm) for s in ALLFRESH}
        shuf = {s: cells_lr(z, s, p, arm, shift=500) for s in ALLFRESH}
        kall = sum(cells[s]["duty_07"] >= .5 for s in ALLFRESH)
        lb = wilson_lb_full(kall, N_POOL)
        lr[p] = dict(
            pooled=dict(k=kall, n=N_POOL, p_hat=round(kall / N_POOL, 4),
                        lb_full=round(lb, 4), g2a_multi=bool(lb >= .717)),
            flyhack=dict(
                real_mean=round(float(np.mean(
                    [cells[s]["duty_07"] for s in ALLFRESH])), 3),
                shift500_mean=round(float(np.mean(
                    [shuf[s]["duty_07"] for s in ALLFRESH])), 3)))
        lr[p]["flyhack"]["margin"] = round(
            lr[p]["flyhack"]["real_mean"] - lr[p]["flyhack"]["shift500_mean"], 3)
    tables[arm] = dict(pairs=per, unpaired=lr, lock=lock_of(z, arm))

# P4: paired deltas free - cfn (duty_07 per seed, 5 pairs)
paired_delta = {}
for pk in PAIRS:
    d = np.array([cells_of(z, s, pk, "free")["duty_07"]
                  - cells_of(z, s, pk, "cfn")["duty_07"] for s in ALLFRESH])
    paired_delta[pk] = dict(
        mean=round(float(np.nanmean(d)), 3),
        up=int((d > 0).sum()), down=int((d < 0).sum()), same=int((d == 0).sum()))

# P2: bit-identity freenod vs free (verdict-side re-derive)
ALL = ANCHOR + ALLFRESH
nod_maxd = max(float(np.abs(z[f"mm_freenod_{s}"] - z[f"mm_free_{s}"]).max())
               for s in ALL)

# P1 + P3
free_robust = [pk for pk in PAIRS if tables["free"]["pairs"][pk]["pooled"]["g2a_multi"]]
free_robust_lr = [p for p in UNPAIRED
                  if tables["free"]["unpaired"][p]["pooled"]["g2a_multi"]]
# best free cell for P3 (max p_hat across 5 pairs + 2 LR)
cands = ([(tables["free"]["pairs"][pk]["pooled"]["p_hat"], "pair", pk)
          for pk in PAIRS]
         + [(tables["free"]["unpaired"][p]["pooled"]["p_hat"], "lr", p)
            for p in UNPAIRED])
best = max(cands)
if best[1] == "pair":
    pk = best[2]
    real = np.mean([cells_of(z, s, pk, "free")["duty_07"] for s in ALLFRESH])
    # shift null for a PAIR cell: shift the antagonist-side trace by 500
    # (anticorrelation window becomes phase-mismatched) — same trick as LR.
    # Implement directly:
    def cells_of_shift(raw, s, pair, arm, shift):
        Lsel = raw[f"{pair}_aL_{arm}_{s}"][:WIN]
        Rsel = np.roll(raw[f"{pair}_bL_{arm}_{s}"][:WIN], shift)
        RRsel = raw[f"{pair}_bR_{arm}_{s}"][:WIN]
        SL = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = s_of(Lsel[t - 499:t + 1], Rsel[t - 499:t + 1])
        ok = (SL[Q07_T] >= .25)
        return float(np.nanmean(ok))
    shuf = float(np.mean([cells_of_shift(z, s, pk, "free", 500)
                          for s in ALLFRESH]))
else:
    p = best[2]
    real = tables["free"]["unpaired"][p]["flyhack"]["real_mean"]
    shuf = tables["free"]["unpaired"][p]["flyhack"]["shift500_mean"]
p3 = dict(best_cell=f"{best[1]}:{best[2]}", p_hat=best[0],
          real_mean=round(float(real), 3), shift500_mean=round(float(shuf), 3))
p3["margin"] = round(p3["real_mean"] - p3["shift500_mean"], 3)

anchors_ok = (ar["c0a_pass"] and ar["c1"] and ar["c0d_free_ne_cfn"]
              and c0b_pass)
if not anchors_ok:
    verdict = (f"ANCHOR-FAIL c0a={ar['c0a_pass']} c1={ar['c1']} "
               f"c0d={ar['c0d_free_ne_cfn']} c0b={c0b_pass}")
else:
    if not free_robust and not free_robust_lr:
        verdict = ("P1 (expected): NO free-run self-ordering on the closure "
                   "substrate — the l65 extraction rule owned the self-"
                   "ordering, not the cord; L94's law now covers zero drive")
    else:
        verdict = (f"P1 FIRED: free-run clears {free_robust + free_robust_lr} "
                   f"— P3 secondary required (margin {p3['margin']})")

af_free = {str(s): float(z[f"af_free_{s}"]) for s in ANCHOR}
af_nod = {str(s): float(z[f"af_freenod_{s}"]) for s in ANCHOR}
out = dict(meta=dict(arms=["cfn", "free", "freenod"], n_pool=N_POOL,
                     substrate="closure l92"),
           anchors=dict(c0a=ar["c0a_pass"], c0a_max=ar["c0a_max"],
                        c1=ar["c1"], c0b=c0b_pass, c0b_fails=c0b_fail[:8],
                        c0d=ar["c0d_free_ne_cfn"]),
           tables=tables, paired_delta_free_vs_cfn=paired_delta,
           p2_freenod_vs_free_maxd=nod_maxd, p3=p3,
           free_robust=free_robust, free_robust_lr=free_robust_lr,
           af_free=af_free, af_freenod=af_nod,
           verdict=verdict)
json.dump(out, open("l105/results_l105.json", "w"), indent=1)
print(verdict)
for pk in PAIRS:
    t = tables["free"]["pairs"][pk]
    print(f"free {pk}: k {t['k_spread']} pooled {t['pooled']['k']}/48 "
          f"lb {t['pooled']['lb_full']} | duty07 "
          f"{[t['per_batch'][b]['duty07_mean'] for b in BATCHES]} "
          f"| seg1 {[t['per_batch'][b]['seg1_mean'] for b in BATCHES]} "
          f"| nan {t['nan_seed_count']}")
for p in UNPAIRED:
    t = tables["free"]["unpaired"][p]
    print(f"free {p} LR: k {t['pooled']['k']}/48 lb {t['pooled']['lb_full']} "
          f"| flyhack real {t['flyhack']['real_mean']} "
          f"shift {t['flyhack']['shift500_mean']} "
          f"margin {t['flyhack']['margin']}")
print("P4 paired delta free-cfn:",
      {k: (v["mean"], f"{v['up']}up/{v['down']}dn/{v['same']}same")
       for k, v in paired_delta.items()})
print("P2 freenod-vs-free max|d|:", nod_maxd)
print("P3:", p3)
print("lock free:", tables["free"]["lock"], "| freenod:",
      tables["freenod"]["lock"])
