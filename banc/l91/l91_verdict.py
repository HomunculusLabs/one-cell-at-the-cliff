"""L91 verdict: female multibatch table + certification. PREREG l91/PREREG.md.

Re-derives EVERY read from raw_l91.npz (+ stored l78 artifacts for the C0B
certification). Cells = male l90 500-step form, run on Ti (primary) and Tr
(secondary); certification = l78's own 300-step form on the shared arms.
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
BLK = 500
MEAS0 = 500
LOCK_TOL = 0.10
SIGS = ("fL", "fR", "eL", "eR")
ARMS = ["fn", "fn_fb", "fh", "fh_fb", "fsham"]
ECHO_ARMS = ["fn_fb", "fh_fb"]
ANCHOR = [11, 22, 33]
B1 = list(range(501, 517))
B2 = list(range(601, 617))
B3 = list(range(701, 717))
BATCHES = {"B1": B1, "B2": B2, "B3": B3}
ALLFRESH = B1 + B2 + B3
N_POOL = len(ALLFRESH)
FBG, FBD, ENT_AMP = 0.1, 5, 0.1
SETTLE = 400

z = np.load("l91/raw_l91.npz")
ar = json.load(open("l91/anchors_run.json"))
r78 = json.load(open("l78/results_l78.json"))


def arrs(a, s, pk):
    mm = z[f"mm_{a}_{s}"][:WIN]
    tr = {c: z[f"{pk}_{c}_{a}_{s}"][:WIN] for c in SIGS}
    return mm, tr


# ---------------- l78-form certification (C0B) ----------------
TS3 = np.arange(299, WIN, 10)
m_slow = ((TS3 >= 799) & (TS3 < 2000)) | ((TS3 >= 4799) & (TS3 < 6000))
OFFS = [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)]
m_off = np.zeros(len(TS3), bool)
for lo, hi in OFFS:
    m_off |= (TS3 >= lo + 299) & (TS3 < hi)
m_fast = (TS3 >= 2299) & (TS3 < 4000)


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


SM3 = {}


def roll_s3(a, s, pk):
    key = (a, s, pk)
    if key not in SM3:
        _, tr = arrs(a, s, pk)
        fL, fR, eL, eR = (tr[c] for c in SIGS)
        SL = np.full(len(TS3), np.nan)
        SR = np.full(len(TS3), np.nan)
        for i, t in enumerate(TS3):
            SL[i] = S_of(fL[t - 299:t + 1], eL[t - 299:t + 1])
            SR[i] = S_of(fR[t - 299:t + 1], eR[t - 299:t + 1])
        SM3[key] = (SL, SR)
    return SM3[key]


c0b_fail = []
for my_arm, l78_arm in (("fn", "open"), ("fn_fb", "fbn_g01"),
                        ("fsham", "sham_g01")):
    for s in ANCHOR:
        SLTr, SRTr = roll_s3(my_arm, s, "Tr")
        SLTi, SRTi = roll_s3(my_arm, s, "Ti")
        bothT = (SLTr >= .25) & (SRTr >= .25)
        bothI = (SLTi >= .25) & (SRTi >= .25)
        mine = dict(
            duty_slow=round(float(np.nanmean(bothT[m_slow])), 3),
            duty_off=round(float(np.nanmean(bothT[m_off])), 3),
            duty_fast=round(float(np.nanmean(bothT[m_fast])), 3),
            Ti_duty07=round(float(np.nanmean(bothI[m_slow])), 3),
            Tr_SL_slow=round(float(np.nanmedian(SLTr[m_slow])), 3),
            Tr_SR_slow=round(float(np.nanmedian(SRTr[m_slow])), 3))
        want = r78["arms"][l78_arm][str(s)]
        for k in mine:
            if mine[k] != want[k]:
                c0b_fail.append((my_arm, s, k, mine[k], want[k]))
c0b_pass = not c0b_fail

# ---------------- male-form cells (l90 verbatim) ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s, pk):
    key = (a, s, pk)
    if key not in SM:
        _, tr = arrs(a, s, pk)
        fL, fR, eL, eR = (tr[c] for c in SIGS)
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
            SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    return round(float(np.nanmedian(arr[TS[q]])), 3) if q.any() else None


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


def cells_of(a, s, pk):
    mm, _ = arrs(a, s, pk)
    SL, SR = s_arrays(a, s, pk)
    rows = []
    for a0_, b0, tg in SEGB:
        lo, hi = a0_ + MEAS0, b0
        q = (TS >= lo) & (TS < hi)
        both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
        f_seg = dom_freq(mm[a0_:b0])
        bl_errs, ttl = [], None
        for b in range(WIN // BLK):
            if a0_ <= b * BLK < b0 and b * BLK > a0_:
                e = abs(dom_freq(mm[b * BLK:(b + 1) * BLK]) - tg)
                bl_errs.append(e)
                if ttl is None and e <= LOCK_TOL:
                    ttl = b * BLK - a0_
        rows.append(dict(
            duty=round(float(np.nanmean(both)), 3),
            SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
            f=round(f_seg, 3),
            err=round(float(np.mean(bl_errs)), 4), ttl=ttl))
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
# (PREREG mis-carried 27 as the n=32 k_min — l90's stored assert says 28;
#  caught by this assert, clause moot: all 48 seeds ran. See ADDENDUM 1.)

CELLS = {a: {pk: {} for pk in ("Ti", "Tr")} for a in ARMS}
for a in ARMS:
    for pk in ("Ti", "Tr"):
        for s in ANCHOR + ALLFRESH:
            CELLS[a][pk][s] = cells_of(a, s, pk)

# ---------------- G1p lock (female spectral form) + male err diagnostic ----------------
lock = {a: {} for a in ARMS}
for a in ARMS:
    for s in ANCHOR + ALLFRESH:
        mm, _ = arrs(a, s, "Ti")
        lock[a][s] = dict(
            ratio=[round(dom_ratio(mm[s0:s0 + 2000]), 1) for s0, _, _ in SEGB],
            err=[r["err"] for r in CELLS[a]["Ti"][s]["segs"]])

# ---------------- budget (echo ratio, l78 form) ----------------
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
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        amph[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
amph[2000:4000] = ENT_AMP
on_steps = np.where(amph > 0)[0]
sin_mean = float(np.mean(0.5 + 0.5 * np.sin(PHI[on_steps])))
# l78 registered form: echo drive / ENTRAIN DRIVE (ENT_AMP * sin term).
# (v1 divided by sin_mean only -> .0251; l78/l90 form -> ~.25. ADDENDUM 1.)
budget = {}
for a in ECHO_ARMS:
    em = []
    for s in ANCHOR + ALLFRESH:
        mA = z[f"mA_{a}_{s}"][:WIN]
        e = np.abs(mA[[k - FBD for k in on_steps if k >= FBD]])
        em.append(float(FBG * e.mean() / (ENT_AMP * sin_mean)))
    budget[a] = round(float(np.mean(em)), 4)

# ---------------- the multibatch table ----------------
def table_for(pk):
    table = {}
    for a in ARMS:
        per_batch = {}
        for b, seeds in BATCHES.items():
            d07 = np.array([CELLS[a][pk][s]["duty_07"] for s in seeds])
            s1 = np.array([CELLS[a][pk][s]["segs"][1]["duty"] for s in seeds])
            s2 = np.array([CELLS[a][pk][s]["segs"][2]["duty"] for s in seeds])
            dL = np.array([CELLS[a][pk][s]["duty07_L"] for s in seeds])
            dR = np.array([CELLS[a][pk][s]["duty07_R"] for s in seeds])
            k = int((d07 >= .5).sum())
            per_batch[b] = dict(
                k=k, wilson=wilson(k, 16),
                duty07_mean=round(float(d07.mean()), 3),
                seg1_mean=round(float(s1.mean()), 3),
                seg2_mean=round(float(s2.mean()), 3),
                duty07L_mean=round(float(dL.mean()), 3),
                duty07R_mean=round(float(dR.mean()), 3),
                duty07_per_seed=[round(float(v), 3) for v in d07])
        kp = sum(per_batch[b]["k"] for b in BATCHES)
        lb = wilson_lb_full(kp, N_POOL)
        table[a] = dict(
            per_batch=per_batch,
            pooled=dict(k=kp, n=N_POOL, lb_full=round(lb, 4),
                        g2a_multi=bool(lb >= .717), k_min=41),
            k_spread=[per_batch[b]["k"] for b in BATCHES],
            seg1_spread=[per_batch[b]["seg1_mean"] for b in BATCHES],
            anchor={s: CELLS[a][pk][s]["duty_07"] for s in ANCHOR})
    return table


table_Ti = table_for("Ti")
table_Tr = table_for("Tr")

# ---------------- registered expectations ----------------
exp = {}
fn_anch_Ti = [CELLS["fn"]["Ti"][s]["duty_07"] for s in ANCHOR]
fn_anch_Tr = [CELLS["fn"]["Tr"][s]["duty_07"] for s in ANCHOR]
exp["E1_fn_anchor_Ti_.94_1.0"] = bool(all(.94 <= v <= 1.0 for v in fn_anch_Ti))
exp["E1b_fn_anchor_Tr_.04_.20"] = bool(all(.04 <= v <= .20 for v in fn_anch_Tr))


def lift(a, pk):
    return {s: CELLS[a][pk][s]["duty_07"] - CELLS["fn"][pk][s]["duty_07"]
            for s in ALLFRESH}


fb_Tr = lift("fn_fb", "Tr")
sham_Tr = lift("fsham", "Tr")
fb_Ti = lift("fn_fb", "Ti")
m_fb_Tr = float(np.mean(list(fb_Tr.values())))
m_sham_Tr = float(np.mean(list(sham_Tr.values())))
m_fb_Ti = float(np.mean(list(fb_Ti.values())))
exp["E2_fb_Tr_lift"] = bool(m_fb_Tr > 0)
exp["E2b_fb_Ti_tax"] = bool(m_fb_Ti <= 0)
exp["E3_sham_share"] = round(m_sham_Tr / m_fb_Tr, 3) if m_fb_Tr > 0 else None
exp["E3_sham_carries_half"] = bool(
    m_fb_Tr > 0 and m_sham_Tr / m_fb_Tr >= .5)
exp["E5_fn_G2a_multi"] = table_Ti["fn"]["pooled"]["g2a_multi"]

# anchors gate (ADDENDUM 1: hop arms = dead-channel duplicates; C2 re-scoped
# to the arms that claim treatment effects; hop_lands recorded, not gated)
c2_dup = {f"fh_{s}": float(np.abs(z[f"mm_fh_{s}"] - z[f"mm_fn_{s}"]).max())
          for s in ANCHOR + ALLFRESH}
c2_dup2 = {f"fhfb_{s}": float(np.abs(
    z[f"mm_fh_fb_{s}"] - z[f"mm_fn_fb_{s}"]).max()) for s in ANCHOR + ALLFRESH}
dups_ok = all(v == 0.0 for v in c2_dup.values()) and \
    all(v == 0.0 for v in c2_dup2.values())
c2_land = {f"{a}_{s}": float(np.abs(z[f"mm_{a}_{s}"] - z[f"mm_fn_{s}"]).max())
           for a in ("fn_fb", "fsham") for s in ANCHOR + ALLFRESH}
c2_land_pass = all(v > 0.0 for v in c2_land.values())
anchors = dict(c0a=ar["c0a_pass"], c0a2=ar["c0a2_pass"], c0a3=ar["c0a3_pass"],
               c0p_echo=ar["c0p_echo"], c2_landed=c2_land_pass,
               hop_duplicates=dups_ok, hop_lands_MEASURED=False, c1=ar["c1"],
               c0b=c0b_pass)
anchors_ok = all(v for k, v in anchors.items() if k != "hop_lands_MEASURED")

TABLE_ARMS = ["fn", "fn_fb", "fsham"]   # ADDENDUM 1: hop arms excluded

if not anchors_ok:
    verdict = f"ANCHOR-FAIL {anchors} (addendum before any read)"
else:
    clearing = [a for a in TABLE_ARMS if table_Ti[a]["pooled"]["g2a_multi"]]
    side = ("HOLDS (female base structure batch-robust)"
            if table_Ti["fn"]["pooled"]["g2a_multi"] else
            "COLLAPSES (male-like batch fragility)")
    verdict = (f"G2a-multi Ti n=48: clears {clearing or 'NONE'} | fn {side} "
               f"(k {table_Ti['fn']['pooled']['k']}/48 lb "
               f"{table_Ti['fn']['pooled']['lb_full']}) | fb vs fn: Ti "
               f"{m_fb_Ti:+.3f} Tr {m_fb_Tr:+.3f}, sham share "
               f"{exp['E3_sham_share']} | Tr fn k "
               f"{table_Tr['fn']['pooled']['k']}/48 lb "
               f"{table_Tr['fn']['pooled']['lb_full']}")

out = dict(meta=dict(batches={b: v for b, v in BATCHES.items()},
                     arms=TABLE_ARMS, hop_arms="excluded (ADDENDUM 1)",
                     n_pool=N_POOL, pair_primary="Ti", pair_secondary="Tr"),
           anchors=anchors, anchors_detail=dict(
               c0b_fail=c0b_fail[:8],
               hop_fd_mm=sorted(set(ar["c0p_hop_mm"])),
               dup_max_fh=float(max(c2_dup.values())),
               dup_max_fhfb=float(max(c2_dup2.values())),
               c0_max=dict(c0a=ar["c0a_max"], c0a2=ar["c0a2_max"],
                           c0a3=ar["c0a3_max"])),
           budget=budget, expectations=exp,
           table_Ti=table_Ti, table_Tr=table_Tr,
           lock_g1p={a: {str(s): lock[a][s] for s in ANCHOR + ALLFRESH[:4]}
                     for a in ARMS},
           lock_g1p_pass={a: int(sum(
               all(r >= 10 for r in lock[a][s]["ratio"])
               for s in ALLFRESH)) for a in ARMS},
           verdict=verdict)
json.dump(out, open("l91/results_l91.json", "w"), indent=1)
print("ANCHORS", anchors)
print("HOP fd_mm set:", sorted(set(ar["c0p_hop_mm"])),
      "| dup-proof fh/fhfb max:", float(max(c2_dup.values())),
      float(max(c2_dup2.values())))
for pk, tb in (("Ti", table_Ti), ("Tr", table_Tr)):
    print(f"--- {pk} ---")
    for a in TABLE_ARMS:
        t = tb[a]
        print(f"{a:8s} k/batch {t['k_spread']} pooled {t['pooled']['k']}/48 "
              f"lb {t['pooled']['lb_full']} G2a {t['pooled']['g2a_multi']} | "
              f"anchor {list(t['anchor'].values())} | seg1 "
              f"{t['seg1_spread']} | per-side "
              f"L {[t['per_batch'][b]['duty07L_mean'] for b in BATCHES]} "
              f"R {[t['per_batch'][b]['duty07R_mean'] for b in BATCHES]}")
print("BUDGET", budget)
print("EXPECT", json.dumps(exp))
print("G1p pass (all-ratio>=10, fresh):", out["lock_g1p_pass"])
print("VERDICT", verdict)
