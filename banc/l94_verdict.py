"""L94 verdict: closure multibatch table + certification. PREREG l94/PREREG.md.

Part 1 = C0B certification: THIS script's metric code on stored raw_l91.npz
must reproduce results_l91.json EVERY pinned read BEFORE any L94 number is
pinned (L85 rule). Part 2 = the L94 reads from raw_l94.npz. Crash-isolated
from the rollouts; re-derivable from raw alone.
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0, BLK, LOCK_TOL = 500, 500, 0.10
SIGS = ("fL", "fR", "eL", "eR")
SETTLE = 400
ENT_AMP = 0.1
FBG, FBD = 0.1, 5
ANCHOR = [11, 22, 33]

# L91 certification constants
L91_ARMS = ["fn", "fn_fb", "fsham"]
B1 = list(range(501, 517))
B2 = list(range(601, 617))
B3 = list(range(701, 717))
BATCHES91 = {"B1": B1, "B2": B2, "B3": B3}
ALLFRESH91 = B1 + B2 + B3

# L94 constants
ARMS = ["cfn", "cfn_fb", "csham", "cfh", "cfh_fb"]
ECHO_ARMS = ["cfn_fb", "cfh_fb"]
B4 = list(range(801, 817))
B5 = list(range(901, 917))
B6 = list(range(1001, 1017))
BATCHES = {"B4": B4, "B5": B5, "B6": B6}
ALLFRESH = B4 + B5 + B6
N_POOL = len(ALLFRESH)

z94 = np.load("l94/raw_l94.npz")
ar = json.load(open("l94/anchors_run.json"))
z91 = np.load("l91/raw_l91.npz")
r91 = json.load(open("l91/results_l91.json"))
pin = json.load(open("l94/prederive_anchor.json"))


def arrs(raw, a, s, pk):
    mm = raw[f"mm_{a}_{s}"][:WIN]
    tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN] for c in SIGS}
    return mm, tr


TS = np.arange(499, WIN, 10)


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


SM = {}


def s_arrays(raw, a, s, pk):
    key = (id(raw), a, s, pk)
    if key not in SM:
        _, tr = arrs(raw, a, s, pk)
        fL, fR, eL, eR = (tr[c] for c in SIGS)
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
            SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


def dom_freq(x, lo=0.3):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    return float(f_hat)


def dom_ratio(x):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= 0.3) & (fr <= 10)
    return float(ps[band].max() / max(np.median(ps[band]), 1e-30))


def cells_of(raw, a, s, pk):
    mm, _ = arrs(raw, a, s, pk)
    SL, SR = s_arrays(raw, a, s, pk)
    rows = []
    for a0_, b0, tg in SEGB:
        lo, hi = a0_ + MEAS0, b0
        q = (TS >= lo) & (TS < hi)
        both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
        bl_errs = []
        for b in range(WIN // BLK):
            if a0_ <= b * BLK < b0 and b * BLK > a0_:
                bl_errs.append(abs(dom_freq(mm[b * BLK:(b + 1) * BLK]) - tg))
        rows.append(dict(duty=round(float(np.nanmean(both)), 3),
                         err=round(float(np.mean(bl_errs)), 4)))
    qall = np.zeros(len(TS), bool)
    q07 = np.zeros(len(TS), bool)
    for a0_, b0, f in SEGB:
        qall |= (TS >= a0_ + MEAS0) & (TS < b0)
        if f == 0.7:
            q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
    L07 = (SL[TS[q07]] >= .25)
    R07 = (SR[TS[q07]] >= .25)
    return dict(segs=rows,
                duty_all=round(float(np.nanmean(
                    (SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
                duty_07=round(float(np.nanmean(L07 & R07)), 3),
                duty07_L=round(float(np.nanmean(L07)), 3),
                duty07_R=round(float(np.nanmean(R07)), 3))


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
assert wilson_lb_full(28, 32) >= .717 > wilson_lb_full(27, 32)  # l90 stored pin


# ---------------- Part 1: C0B certification on l91 (BEFORE any L94 pin) ----
CELLS91 = {a: {pk: {} for pk in ("Ti", "Tr")} for a in L91_ARMS}
for a in L91_ARMS:
    for pk in ("Ti", "Tr"):
        for s in ANCHOR + ALLFRESH91:
            CELLS91[a][pk][s] = cells_of(z91, a, s, pk)


def table_for(raw, cells, arms, batches, allfresh, pk):
    table = {}
    for a in arms:
        per_batch = {}
        for b, seeds in batches.items():
            d07 = np.array([cells[a][pk][s]["duty_07"] for s in seeds])
            s1 = np.array([cells[a][pk][s]["segs"][1]["duty"] for s in seeds])
            s2 = np.array([cells[a][pk][s]["segs"][2]["duty"] for s in seeds])
            dL = np.array([cells[a][pk][s]["duty07_L"] for s in seeds])
            dR = np.array([cells[a][pk][s]["duty07_R"] for s in seeds])
            k = int((d07 >= .5).sum())
            per_batch[b] = dict(
                k=k, wilson=wilson(k, 16),
                duty07_mean=round(float(d07.mean()), 3),
                seg1_mean=round(float(s1.mean()), 3),
                seg2_mean=round(float(s2.mean()), 3),
                duty07L_mean=round(float(dL.mean()), 3),
                duty07R_mean=round(float(dR.mean()), 3))
        kp = sum(per_batch[b]["k"] for b in batches)
        lb = wilson_lb_full(kp, len(allfresh))
        table[a] = dict(
            per_batch=per_batch,
            pooled=dict(k=kp, n=len(allfresh), lb_full=round(lb, 4),
                        g2a_multi=bool(lb >= .717), k_min=41),
            k_spread=[per_batch[b]["k"] for b in batches],
            seg1_spread=[per_batch[b]["seg1_mean"] for b in batches],
            anchor={s: cells[a][pk][s]["duty_07"] for s in ANCHOR})
    return table


cert91_Ti = table_for(z91, CELLS91, L91_ARMS, BATCHES91, ALLFRESH91, "Ti")
cert91_Tr = table_for(z91, CELLS91, L91_ARMS, BATCHES91, ALLFRESH91, "Tr")

c0b_fail = []
for pk, cert in (("Ti", cert91_Ti), ("Tr", cert91_Tr)):
    for a in L91_ARMS:
        want = r91[f"table_{pk}"][a]
        got = cert[a]
        for b in BATCHES91:
            for kk in ("k", "wilson", "duty07_mean", "seg1_mean", "seg2_mean",
                       "duty07L_mean", "duty07R_mean"):
                if got["per_batch"][b][kk] != want["per_batch"][b][kk]:
                    c0b_fail.append((pk, a, b, kk,
                                     got["per_batch"][b][kk],
                                     want["per_batch"][b][kk]))
        for kk in ("k", "n", "lb_full", "g2a_multi", "k_min"):
            if got["pooled"][kk] != want["pooled"][kk]:
                c0b_fail.append((pk, a, "pooled", kk,
                                 got["pooled"][kk], want["pooled"][kk]))
        for s in ANCHOR:
            if got["anchor"][s] != want["anchor"][str(s)]:
                c0b_fail.append((pk, a, f"anchor{s}", got["anchor"][s],
                                 want["anchor"][str(s)]))

# budget certification (l91 form)
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN)
for i in range(WIN):
    for a0_, b0, f in SEGB:
        if a0_ <= i < b0:
            tg = f
            break
    ph += 2 * math.pi * tg * DT
    PHI[i] = ph
amph = np.zeros(WIN)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + 2000:
        lo = seg0 + c * 900
        amph[lo:min(lo + 500, seg0 + 2000)] = ENT_AMP
        c += 1
amph[2000:4000] = ENT_AMP
on_steps = np.where(amph > 0)[0]
sin_mean = float(np.mean(0.5 + 0.5 * np.sin(PHI[on_steps])))


def budget_of(raw, a, seeds):
    em = []
    for s in seeds:
        mA = raw[f"mA_{a}_{s}"][:WIN]
        e = np.abs(mA[[k - FBD for k in on_steps if k >= FBD]])
        em.append(float(FBG * e.mean() / (ENT_AMP * sin_mean)))
    return round(float(np.mean(em)), 4)


budget91 = {a: budget_of(z91, a, ANCHOR + ALLFRESH91)
            for a in ("fn_fb", "fh_fb")}
for a in budget91:
    if budget91[a] != r91["budget"][a]:
        c0b_fail.append(("budget", a, budget91[a], r91["budget"][a]))
c0b_pass = not c0b_fail
print("C0B certification:", "PASS" if c0b_pass else f"FAIL {c0b_fail[:6]}")

# ---------------- Part 2: L94 reads ----------------
CELLS = {a: {pk: {} for pk in ("Ti", "Tr")} for a in ARMS}
for a in ARMS:
    for pk in ("Ti", "Tr"):
        for s in ANCHOR + ALLFRESH:
            CELLS[a][pk][s] = cells_of(z94, a, s, pk)

table_Ti = table_for(z94, CELLS, ARMS, BATCHES, ALLFRESH, "Ti")
table_Tr = table_for(z94, CELLS, ARMS, BATCHES, ALLFRESH, "Tr")

# anchor pins (exact, C0A-guaranteed)
pin_fail = []
for s in ANCHOR:
    for pk in ("Ti", "Tr"):
        for kk, form in (("duty_07", "duty_07"), ("duty07_L", "d07L"),
                         ("duty07_R", "d07R")):
            got = CELLS["cfn"][pk][s][kk]
            want = pin[str(s)][pk][form]
            if got != want:
                pin_fail.append((s, pk, kk, got, want))
pins_pass = not pin_fail

# E1: Ti robustness (measurement, no direction gate)
e1 = table_Ti["cfn"]["pooled"]

# E2: Tr side-split persistence (sign test, cfn)
split_batches = sum(
    1 for b in BATCHES
    if table_Tr["cfn"]["per_batch"][b]["duty07L_mean"]
    < table_Tr["cfn"]["per_batch"][b]["duty07R_mean"] - .10)
e2_split = bool(split_batches >= 2)


def lift(a, pk):
    return {s: CELLS[a][pk][s]["duty_07"] - CELLS["cfn"][pk][s]["duty_07"]
            for s in ALLFRESH}


fb_Ti = float(np.mean(list(lift("cfn_fb", "Ti").values())))
fb_Tr = float(np.mean(list(lift("cfn_fb", "Tr").values())))
sham_Tr = float(np.mean(list(lift("csham", "Tr").values())))
sham_Ti = float(np.mean(list(lift("csham", "Ti").values())))
sham_share = round(sham_Tr / fb_Tr, 3) if fb_Tr > 0 else None

# E4: hop arms (direction read only)
hop_dm = {f"cfh_{s}": float(np.abs(
    z94[f"mm_cfh_{s}"] - z94[f"mm_cfn_{s}"]).max()) for s in ALLFRESH}
hop_duty = {pk: {"L": round(float(np.mean(
    [CELLS["cfh"][pk][s]["duty07_L"] - CELLS["cfn"][pk][s]["duty07_L"]
     for s in ALLFRESH])), 3),
    "R": round(float(np.mean(
    [CELLS["cfh"][pk][s]["duty07_R"] - CELLS["cfn"][pk][s]["duty07_R"]
     for s in ALLFRESH])), 3)} for pk in ("Ti", "Tr")}

budget = {a: budget_of(z94, a, ANCHOR + ALLFRESH) for a in ECHO_ARMS}

lock = {a: int(sum(
    all(dom_ratio(z94[f"mm_{a}_{s}"][s0:s0 + 2000]) >= 10
        for s0, _, _ in SEGB) for s in ALLFRESH)) for a in ARMS}

anchors = dict(c0a=ar["c0a_pass"], c0a_max=ar["c0a_max"],
               c0b=c0b_pass, fd_echo_law=ar["fd_echo_law"],
               fd_hop_mm=ar["fd_hop_mm"], fd_hopfb_mm=ar["fd_hopfb_mm"],
               c2=ar["c2_pass"], c2_min=ar["c2_min"], c1=ar["c1"],
               pins_exact=pins_pass)
anchors_ok = (anchors["c0a"] and anchors["c0b"] and anchors["fd_echo_law"]
              and anchors["c2"] and anchors["c1"] and anchors["pins_exact"])

if not anchors_ok:
    verdict = f"ANCHOR-FAIL {anchors} (addendum before any read)"
else:
    ti = table_Ti["cfn"]["pooled"]
    tr = table_Tr["cfn"]
    side = ("SURVIVES (closure-robust)" if ti["g2a_multi"] else
            "COLLAPSES (l65-rule was load-bearing FOR the robustness)")
    split = "PERSISTS" if e2_split else "RE-DRAWS"
    verdict = (f"Ti base {side}: k {ti['k']}/48 lb {ti['lb_full']} "
               f"(l65 was 48/48 .9259) | Tr split {split} "
               f"(L {[tr['per_batch'][b]['duty07L_mean'] for b in BATCHES]} "
               f"R {[tr['per_batch'][b]['duty07R_mean'] for b in BATCHES]}; "
               f"l65 L .16-.17 / R .95-.98) | echo fb-vs-cfn Ti {fb_Ti:+.3f} "
               f"Tr {fb_Tr:+.3f} sham share {sham_share} | hop lands "
               f"(dm min {min(hop_dm.values()):.3f}) duty dL/dR "
               f"Ti {hop_duty['Ti']} Tr {hop_duty['Tr']}")

out = dict(meta=dict(batches={b: v for b, v in BATCHES.items()}, arms=ARMS,
                     n_pool=N_POOL, substrate="closure l92 (g* .153125)",
                     hop_target=[int(v) for v in z94["hop46"]]),
           anchors=anchors, cert91=dict(budget=budget91, fails=c0b_fail[:8]),
           anchor_pins_exact=pins_pass,
           table_Ti=table_Ti, table_Tr=table_Tr,
           lifts=dict(fb_Ti=round(fb_Ti, 3), fb_Tr=round(fb_Tr, 3),
                      sham_Ti=round(sham_Ti, 3), sham_Tr=round(sham_Tr, 3),
                      sham_share=sham_share),
           hop=dict(dm_min=round(min(hop_dm.values()), 4),
                    dm_max=round(max(hop_dm.values()), 4),
                    duty_deltas=hop_duty,
                    k_Ti=table_Ti["cfh"]["k_spread"],
                    k_Tr=table_Tr["cfh"]["k_spread"]),
           budget=budget, lock_g1p=lock,
           verdict=verdict)
json.dump(out, open("l94/results_l94.json", "w"), indent=1)
print("ANCHORS", anchors)
for pk, tb in (("Ti", table_Ti), ("Tr", table_Tr)):
    print(f"--- {pk} ---")
    for a in ARMS:
        t = tb[a]
        print(f"{a:8s} k/batch {t['k_spread']} pooled {t['pooled']['k']}/48 "
              f"lb {t['pooled']['lb_full']} G2a {t['pooled']['g2a_multi']} | "
              f"anchor {list(t['anchor'].values())} | seg1 {t['seg1_spread']} "
              f"| L {[t['per_batch'][b]['duty07L_mean'] for b in BATCHES]} "
              f"R {[t['per_batch'][b]['duty07R_mean'] for b in BATCHES]}")
print("LIFTS", out["lifts"])
print("HOP", out["hop"])
print("BUDGET", budget, "| lock", lock)
print("VERDICT", verdict)
