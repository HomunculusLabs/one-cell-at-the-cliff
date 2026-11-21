"""L90 verdict: multi-batch table + amended G2a + C4b margin re-read.

Re-derives EVERY read from stored npz (raw_l87.npz census, raw_l88.npz cert,
raw_l90.npz B1/B2/B3). Cells machinery = l87_branch.py verbatim port.
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
TRUNKS = ["hynohop", "hynohop_fb", "hybrid", "hybrid_fb"]
ECHO_ARMS = ["hynohop_fb", "hybrid_fb"]
CENSUS = [11, 22, 33] + list(range(101, 114))
B1 = list(range(501, 517))
B2 = list(range(601, 617))
B3 = list(range(701, 717))
BATCHES = {"B0": CENSUS, "B1": B1, "B2": B2, "B3": B3}
FBG, FBD = 0.1, 5
ENT_AMP = 0.3

z87 = np.load("l87/raw_l87.npz")
z88 = np.load("l88/raw_l88.npz")
z90 = np.load("l90/raw_l90.npz")
r87 = json.load(open("l87/results_l87.json"))
r88 = json.load(open("l88/results_l88.json"))


def arrs(batch, a, s):
    z = z87 if batch == "B0" else z90
    mm = z[f"mm_{a}_{s}"][:WIN]
    tr = {c: z[f"{c}_{a}_{s}"][:WIN] for c in SIGS}
    mA = z[f"mA_{a}_{s}"][:WIN] if f"mA_{a}_{s}" in z.files else None
    return mm, tr, mA


TS = np.arange(499, WIN, 10)
SM = {}


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def s_arrays(batch, a, s):
    key = (batch, a, s)
    if key not in SM:
        _, tr, _ = arrs(batch, a, s)
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
    return float(f_hat)


def cells_of(batch, a, s):
    mm, tr, _ = arrs(batch, a, s)
    SL, SR = s_arrays(batch, a, s)
    rows = []
    for a0_, b0, tg in SEGB:
        lo, hi = a0_ + MEAS0, b0
        q = (TS >= lo) & (TS < hi)
        both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
        f_seg = dom_freq(mm[a0_:b0])
        bl_errs, ttl = [], None
        for b in range(WIN // BLK):
            if a0_ <= b * BLK < b0 and b * BLK > a0_:
                f_hat = dom_freq(mm[b * BLK:(b + 1) * BLK])
                e = abs(f_hat - tg)
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
    return dict(segs=rows,
                duty_all=round(float(np.nanmean(
                    (SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
                duty_07=round(float(np.nanmean(
                    (SL[TS[q07]] >= .25) & (SR[TS[q07]] >= .25))), 3))


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


# pin the prereg equivalence numbers
assert wilson_lb_full(53, 64) >= .717 > wilson_lb_full(52, 64)
assert wilson_lb_full(41, 48) >= .717 > wilson_lb_full(40, 48)
assert wilson_lb_full(28, 32) >= .717 > wilson_lb_full(27, 32)
# disclose the n=16 rounding artifact
assert round(wilson_lb_full(15, 16), 3) == .717 and wilson_lb_full(15, 16) < .717

# ---------------- cells for all arm x batch ----------------
CELLS = {a: {b: {} for b in BATCHES} for a in TRUNKS}
for a in TRUNKS:
    for b, seeds in BATCHES.items():
        for s in seeds:
            CELLS[a][b][s] = cells_of(b, a, s)

# ---------------- C0B: metric certification vs results_l87 ----------------
c0b_fail = []
for a in TRUNKS:
    row = r87["distributions"][a]
    for i in range(3):
        d = np.array([CELLS[a]["B0"][s]["segs"][i]["duty"] for s in CENSUS])
        e = np.array([CELLS[a]["B0"][s]["segs"][i]["err"] for s in CENSUS])
        mine = dict(mean=round(float(d.mean()), 3), k_ge_half=int((d >= .5).sum()),
                    wilson=wilson(int((d >= .5).sum()), 16),
                    err_le01=int((e <= .01).sum()))
        want = dict(mean=row["segs"][i]["mean"],
                    k_ge_half=row["segs"][i]["k_ge_half"],
                    wilson=row["segs"][i]["wilson"],
                    err_le01=row["segs"][i]["err_le01"])
        if mine != want:
            c0b_fail.append((a, i, mine, want))
    d07 = np.array([CELLS[a]["B0"][s]["duty_07"] for s in CENSUS])
    mine = dict(duty07_mean=round(float(d07.mean()), 3),
                duty07_k=int((d07 >= .5).sum()),
                duty07_per_seed=[round(float(v), 3) for v in d07])
    want = dict(duty07_mean=row["duty07_mean"], duty07_k=row["duty07_k"],
                duty07_per_seed=row["duty07_per_seed"])
    for k in mine:
        if mine[k] != want[k]:
            c0b_fail.append((a, k, mine[k], want[k]))
c0b_pass = not c0b_fail

# ---------------- C0D cells: hybrid B1 == l88 stored cells ----------------
c0d_fail = []
for s in B1:
    m, w = CELLS["hybrid"]["B1"][s], r88["cells"]["hybrid"][str(s)]
    if (m["duty_07"] != w["duty_07"] or m["duty_all"] != w["duty_all"]
            or [r["duty"] for r in m["segs"]] != [r["duty"] for r in w["segs"]]):
        c0d_fail.append((s, m["duty_07"], w["duty_07"]))
c0d_cells_pass = not c0d_fail

ar = json.load(open("l90/anchors_run.json"))
anchors = dict(c0a=ar["c0a_pass"], c0d_bits=ar["c0d_pass"],
               c0d_cells=c0d_cells_pass, c0e=ar["c0e_pass"], c1=ar["c1"],
               c0b=c0b_pass)
anchors_ok = all(anchors.values())

# ---------------- budget (echo ratio per fb arm per batch) ----------------
PHI = None
ph, SETTLE = 0.0, 400
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


PHI = np.empty(WIN)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
on_steps = np.arange(WIN)[np.zeros(WIN, bool)]  # placeholder, recomputed below
amph = np.zeros(WIN)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        amph[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
amph[2000:4000] = ENT_AMP
on_steps = np.where(amph > 0)[0]
sin_on = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in on_steps])
entrain_mass = float(ENT_AMP * sin_on.sum())
budget = {}
for a in ECHO_ARMS:
    per_batch = {}
    for b, seeds in BATCHES.items():
        em = []
        for s in seeds:
            _, _, mA = arrs(b, a, s)
            ks = np.arange(WIN)[np.ones(WIN, bool)]
            ks = ks[ks >= FBD]
            em.append(float(FBG * mA[ks - FBD].sum()))
        per_batch[b] = round(float(np.mean(em)) / entrain_mass, 4)
    pooled = float(np.mean([per_batch[b] for b in BATCHES]))
    budget[a] = dict(per_batch=per_batch, pooled_ratio=round(pooled, 4))

# ---------------- the multi-batch table ----------------
table = {}
for a in TRUNKS:
    per_batch = {}
    for b, seeds in BATCHES.items():
        d07 = np.array([CELLS[a][b][s]["duty_07"] for s in seeds])
        s1 = np.array([CELLS[a][b][s]["segs"][1]["duty"] for s in seeds])
        s2 = np.array([CELLS[a][b][s]["segs"][2]["duty"] for s in seeds])
        err = np.array([CELLS[a][b][s]["segs"][1]["err"] for s in seeds])
        k = int((d07 >= .5).sum())
        per_batch[b] = dict(
            k=k, wilson=wilson(k, 16), duty07_mean=round(float(d07.mean()), 3),
            seg1_mean=round(float(s1.mean()), 3), seg2_mean=round(float(s2.mean()), 3),
            g1_lock=int((err <= .01).sum()),
            g3=bool(round(float(s1.mean()), 3) >= .358),
            duty07_per_seed=[round(float(v), 3) for v in d07])
    kp = sum(per_batch[b]["k"] for b in BATCHES)
    lb64 = wilson_lb_full(kp, 64)
    table[a] = dict(
        per_batch=per_batch,
        pooled=dict(k=kp, n=64, lb_full=round(lb64, 4),
                    lb_rounded=wilson(kp, 64)[0],
                    g2a_multi=bool(lb64 >= .717),
                    k_min_64=53, n48_k= sum(per_batch[b]["k"] for b in BATCHES if b != "B0")),
        k_spread=[per_batch[b]["k"] for b in BATCHES],
        seg1_spread=[per_batch[b]["seg1_mean"] for b in BATCHES],
        seg2_spread=[per_batch[b]["seg2_mean"] for b in BATCHES],
        g1_all=bool(all(per_batch[b]["g1_lock"] == 16 for b in BATCHES)))

# secondary descriptive: hy_on2500 n=32 (census raw_l87 + B1 raw_l88), NOT a full re-base
hy = {}
try:
    d_c = np.array([r87["distributions"]["hy_on2500"]["duty07_per_seed"][i]
                    for i in range(16)])
    d_f = np.array([r88["cells"]["hy_on2500"][str(s)]["duty_07"] for s in B1])
    k32 = int((d_c >= .5).sum()) + int((d_f >= .5).sum())
    hy = dict(k=k32, n=32, lb_full=round(wilson_lb_full(k32, 32), 4),
              g2a_multi_32=bool(wilson_lb_full(k32, 32) >= .717),
              note="n=32 descriptive (B0+B1 only), not a full re-base")
except KeyError:
    hy = dict(note="hy_on2500 per-seed absent in stored jsons")

# ---------------- C4b adjudication ----------------
def c4b_read(fb, base):
    lbf = table[fb]["pooled"]["lb_full"]
    lbb = table[base]["pooled"]["lb_full"]
    pos_batches, deltas = 0, {}
    for b in BATCHES:
        d = [CELLS[fb][b][s]["duty_07"] - CELLS[base][b][s]["duty_07"]
             for s in BATCHES[b]]
        deltas[b] = round(float(np.mean(d)), 3)
        if np.mean(d) > 0:
            pos_batches += 1
    if not (lbf >= .717) or lbb >= .717:
        outcome = "COLLAPSED"
    elif pos_batches >= 3:
        outcome = "STRENGTHENED"
    else:
        outcome = "WEAKENED"
    return dict(fb=fb, base=base, lb_fb=round(lbf, 4), lb_base=round(lbb, 4),
                k_fb=table[fb]["pooled"]["k"], k_base=table[base]["pooled"]["k"],
                mean_delta_per_batch=deltas, pos_batches=pos_batches,
                outcome=outcome)


c4b_primary = c4b_read("hynohop_fb", "hynohop")
c4b_secondary = c4b_read("hybrid_fb", "hybrid")

# ---------------- verdict ----------------
if not anchors_ok:
    verdict = f"ANCHOR-FAIL {anchors} (addendum before any read)"
else:
    arms_clear = [a for a in TRUNKS if table[a]["pooled"]["g2a_multi"]]
    verdict = (f"G2a-multi (pooled lb>=.717, n=64): clears {arms_clear or 'NONE'} | "
               f"C4b {c4b_primary['outcome']} (fb k {c4b_primary['k_fb']}/64 lb "
               f"{c4b_primary['lb_fb']} vs base {c4b_primary['k_base']}/64 lb "
               f"{c4b_primary['lb_base']}, delta+ {c4b_primary['pos_batches']}/4 "
               f"batches) | secondary hybrid_fb {c4b_secondary['outcome']}")

out = dict(meta=dict(batches={b: v for b, v in BATCHES.items()},
                     arms=TRUNKS, entrain_mass=round(entrain_mass, 1)),
           anchors=anchors, anchors_detail=dict(
               c0b_fail=c0b_fail[:6], c0d_fail=c0d_fail[:6],
               c0e_fd_set=sorted(set(ar["c0e_fd"].values()))),
           budget=budget, table=table, hy_on2500_n32=hy,
           c4b=dict(primary=c4b_primary, secondary=c4b_secondary),
           rounding_disclosure="original n=16 lb .717 passed at k=15 only via "
                              "3-decimal rounding (true .71674); amended gate "
                              "uses full-precision lb",
           verdict=verdict)
json.dump(out, open("l90/results_l90.json", "w"), indent=1)
print("ANCHORS", anchors)
for a in TRUNKS:
    t = table[a]
    print(f"{a:12s} k/batch {t['k_spread']} pooled {t['pooled']['k']}/64 "
          f"lb {t['pooled']['lb_full']} G2a-multi {t['pooled']['g2a_multi']} | "
          f"seg1 {t['seg1_spread']} | lock "
          f"{[t['per_batch'][b]['g1_lock'] for b in BATCHES]}")
print("BUDGET", json.dumps(budget))
print("hy_on2500 n32:", hy)
print("C4b primary:", json.dumps(c4b_primary))
print("C4b secondary:", json.dumps(c4b_secondary))
print("VERDICT", verdict)
