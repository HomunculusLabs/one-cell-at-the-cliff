# L157 static census: WHO carries the ~.100 Hz sub-band slow line?
# PREREG l157/PREREG.md registered FIRST. Zero rollouts, read-only.
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
HALF = WIN // 2
FBIN = 1.0 / (WIN * DT)          # 1/60 Hz
HBIN = 1.0 / (HALF * DT)         # 1/30 Hz
Z = 1.959963984540054

FILES = ["l154/raw_l154.npz", "l150/raw_l150.npz"]
B34 = list(range(3401, 3417))
B33 = list(range(3365, 3381))   # ADDENDUM 1: actual l150 grid (npz-derived)
ANCH = [801, 901]
POOLS = ([f"Ti_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"Tr_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"{j}_{s}" for j in ("Ta", "Pr", "Sr")
            for s in ("aL", "aR", "bL", "bR")])
EXTRA = ["mm", "xm"]
CHANNELS = POOLS + EXTRA
PAIRS = [("Ti_fL", "Ti_eL"), ("Ti_fR", "Ti_eR"),
         ("Tr_fL", "Tr_eL"), ("Tr_fR", "Tr_eR"),
         ("Ta_aL", "Ta_bL"), ("Ta_aR", "Ta_bR"),
         ("Pr_aL", "Pr_bL"), ("Pr_aR", "Pr_bR"),
         ("Sr_aL", "Sr_bL"), ("Sr_aR", "Sr_bR")]
ARMS = {"l154/raw_l154.npz": ["b65", "off"], "l150/raw_l150.npz": ["b65"]}


def dom_freq(x, lo=0.3):         # VERBATIM l154/l156 lineage
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
    return float(f_hat), int(i == 0)


def bin_argmax(x, lo=0.0):       # dual form (L156 ADDENDUM 1)
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    return float(fb[int(np.argmax(pb))])


def spec(x):
    zz = x - x.mean()
    return np.abs(np.fft.rfft(zz)) ** 2, np.fft.rfftfreq(len(zz), DT)


def slow_share(x, lo=0.05, hi=0.25):
    ps, fr = spec(x)
    return float(ps[(fr >= lo) & (fr <= hi)].sum() / ps.sum())


def slow_phase(xf, xe, lo=0.03, hi=0.30):
    """cross-periodogram phase (deg) of e rel f at the pair's slow bin."""
    zf, ze = xf - xf.mean(), xe - xe.mean()
    Xf, Xe = np.fft.rfft(zf), np.fft.rfft(ze)
    fr = np.fft.rfftfreq(len(zf), DT)
    m = (fr >= lo) & (fr < hi)
    ps = (np.abs(Xf) ** 2 + np.abs(Xe) ** 2) / 2.0
    b = int(np.argmax(ps * m))
    cp = Xe[b] * np.conj(Xf[b])
    return math.degrees(math.atan2(cp.imag, cp.real)), float(fr[b])


def wilson_lb(k, n):
    if n == 0:
        return float("nan")
    p = k / n
    den = 1 + Z * Z / n
    ctr = p + Z * Z / (2 * n)
    rad = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (ctr - rad) / den


def circ_mean_deg(degs):
    r = sum(complex(math.cos(math.radians(d)), math.sin(math.radians(d)))
            for d in degs)
    return math.degrees(math.atan2(r.imag, r.real))


# ---------------- CERT 1: l154 anchors (verbatim l156) -----------------------
t = np.arange(WIN) * DT
for f0 in (0.7, 1.4):
    fh, _ = dom_freq(np.sin(2 * math.pi * f0 * t))
    assert abs(fh - f0) < 0.01, ("self-test", f0, fh)
# CERT 3b: phase estimator on synthetic +0.10 rad lead
ph, fb_ = slow_phase(np.sin(2 * math.pi * 0.1 * t),
                     np.sin(2 * math.pi * 0.1 * t + 0.10))
assert abs(ph - math.degrees(0.10)) < 1.0, ("phase self-test", ph)
print(f"CERT analytic self-tests (0.7/1.4 Hz dom; phase {ph:.3f} deg "
      f"vs {math.degrees(0.10):.3f}): PASS")

raw154 = np.load("l154/raw_l154.npz")
r154 = json.load(open("l154/results_l154.json"))
cert_rows = {}
for a in ("b65", "off"):
    for s in ANCH + B34:
        x = raw154[f"mm_{a}_{s}"][:WIN]
        cert_rows[(a, s)] = (dom_freq(x)[0], dom_freq(x, lo=0.0)[0],
                             bin_argmax(x) < 0.3)
for s in ANCH:
    for a in ("b65", "off"):
        assert cert_rows[(a, s)][0] == r154["anchors"][str(s)][a], (s, a)
for a in ("b65", "off"):
    mb = float(np.mean([cert_rows[(a, s)][0] for s in B34]))
    mu = float(np.mean([cert_rows[(a, s)][1] for s in B34]))
    assert abs(mb - r154["dom_band_mean"][a]) < 1e-12
    assert abs(mu - r154["dom_full_mean"][a]) < 1e-12
bb = {a: int(sum(cert_rows[(a, s)][2] for s in B34)) for a in ("b65", "off")}
assert bb["b65"] == r154["below_band_census"]["on"], bb
assert bb["off"] == r154["below_band_census"]["off"], bb
dl = [cert_rows[("off", s)][0] - cert_rows[("b65", s)][0] for s in B34]
assert (sum(v > 0 for v in dl), sum(v < 0 for v in dl)) == \
    (r154["n_pos"], r154["n_neg"])
print(f"CERT-1 vs l154 stored (anchors/means/below {bb}/signs): PASS")
del raw154

# ---------------- census ------------------------------------------------------
tt = np.arange(WIN, dtype=np.float64)
rows = {}          # (file, arm, channel) -> {seed: metrics}
phase = {}         # (file, arm, pair)   -> [(deg, fbin) per seed]
share = {}         # (file, arm, channel) -> [slow_share per seed]
for f in FILES:
    z = np.load(f)
    seeds = B34 if "l154" in f else B33
    for a in ARMS[f]:
        for ch in CHANNELS:
            for s in ANCH + seeds:
                x = z[f"{ch}_{a}_{s}"][:WIN].astype(np.float64)
                assert len(x) == WIN and np.isfinite(x).all(), (f, a, ch, s)
                f_band, _ = dom_freq(x)
                f_glob, _ = dom_freq(x, lo=0.0)
                c = np.polyfit(tt, x, 1)
                f_det, _ = dom_freq(x - np.polyval(c, tt), lo=0.0)
                below = bool(f_glob < 0.3)
                survive = bool(below and f_det < 0.3
                               and abs(f_det - f_glob) <= FBIN + 1e-9)
                f1, _ = dom_freq(x[:HALF], lo=0.0)
                f2, _ = dom_freq(x[HALF:], lo=0.0)
                rows.setdefault((f, a, ch), {})[s] = dict(
                    f_band=f_band, f_glob=f_glob, below=below,
                    f_glob_bin=bin_argmax(x), below_bin=bool(bin_argmax(x) < 0.3),
                    survive=survive,
                    agree=bool(abs(f1 - f2) <= HBIN + 1e-9))
                share.setdefault((f, a, ch), []).append(slow_share(x))
        for pa, pb_ in PAIRS:
            for s in ANCH + seeds:
                xf = z[f"{pa}_{a}_{s}"][:WIN].astype(np.float64)
                xe = z[f"{pb_}_{a}_{s}"][:WIN].astype(np.float64)
                phase.setdefault((f, a, (pa, pb_)), []).append(
                    slow_phase(xf, xe))
    del z

# ---------------- CERT 2: mm rows == l156/static.json ------------------------
l156 = json.load(open("l156/static.json"))
for f, a in [("l154/raw_l154.npz", "b65"), ("l154/raw_l154.npz", "off"),
             ("l150/raw_l150.npz", "b65")]:
    ref = l156["per_arm"][f"{f}|{a}"]
    d = rows[(f, a, "mm")]
    bl = [v for v in d.values() if v["below"]]
    mine = dict(
        n=len(d), below=len(bl),
        below_bin=sum(v["below_bin"] for v in d.values()),
        survive=sum(v["survive"] for v in bl),
        agree=sum(v["agree"] for v in bl),
        med_f_below=float(np.median([v["f_glob"] for v in bl])),
        med_f_all=float(np.median([v["f_glob"] for v in d.values()])))
    for k, v in mine.items():
        assert ref[k] == v, ("CERT-2", f, a, k, ref[k], v)
print("CERT-2 mm rows == l156/static.json (3 file|arm combos, 7 fields): PASS")

# ---------------- per-channel table ------------------------------------------
table = {}
for (f, a, ch), d in rows.items():
    bl = [v for v in d.values() if v["below"]]
    table[f"{f}|{a}|{ch}"] = dict(
        n=len(d), below=len(bl),
        below_bin=sum(v["below_bin"] for v in d.values()),
        wilson_lb=wilson_lb(len(bl), len(d)),
        survive=sum(v["survive"] for v in bl),
        med_f_below=float(np.median([v["f_glob"] for v in bl])) if bl else None,
        med_f_all=float(np.median([v["f_glob"] for v in d.values()])),
        mean_slow_share=float(np.mean(share[(f, a, ch)])))
pooled = {}
for ch in CHANNELS:
    allv = [v for f in FILES for v in rows.get((f, "b65", ch), {}).values()]
    bl = [v for v in allv if v["below"]]
    pooled[ch] = dict(n=len(allv), below=len(bl),
                      below_bin=sum(v["below_bin"] for v in allv),
                      wilson_lb=wilson_lb(len(bl), len(allv)),
                      survive=sum(v["survive"] for v in bl),
                      med_f_below=float(np.median([v["f_glob"] for v in bl])))
pair_tbl = {}
for (f, a, pr), lst in phase.items():
    degs = [d for d, _ in lst]
    pair_tbl[f"{f}|{a}|{pr[0]}~{pr[1]}"] = dict(
        n=len(degs), circ_mean=circ_mean_deg(degs),
        n_antiphase=sum(1 for d in degs if 90 <= d <= 270),
        med_bin=float(np.median([b for _, b in lst])))

# ---------------- claim classes (registered) ---------------------------------
def shows(f, ch):
    r = table.get(f"{f}|b65|{ch}")
    return r is not None and r["below"] >= 14 and r["below_bin"] >= 14

per_file_cls = {}
for f in FILES:
    pool_show = {ch: shows(f, ch) for ch in POOLS}
    n_pools = sum(pool_show.values())
    pairs_ok = sum(1 for pa, pb_ in PAIRS if pool_show[pa] and pool_show[pb_])
    extra_show = {ch: shows(f, ch) for ch in EXTRA}
    if pairs_ok >= 9:
        cls = "C1_clock_wide"
    elif (extra_show["mm"] or extra_show["xm"]) and n_pools <= 10:
        cls = "C2_readout_only"
    elif 3 <= n_pools:
        cls = "C3_sheet_specific"
    else:
        cls = "C4_mm_only_aggregate"
    per_file_cls[f] = dict(cls=cls, n_pools_showing=n_pools,
                           pairs_both=pairs_ok, extra=extra_show,
                           pools={k: int(v) for k, v in pool_show.items()})
same = per_file_cls[FILES[0]]["cls"] == per_file_cls[FILES[1]]["cls"]
cls = per_file_cls[FILES[0]]["cls"]
defining_ok = True
if cls == "C1_clock_wide":
    defining_ok = all(pooled[pa]["wilson_lb"] >= .5 and
                      pooled[pb_]["wilson_lb"] >= .5
                      for pa, pb_ in PAIRS)
elif cls == "C2_readout_only":
    defining_ok = any(pooled[c]["wilson_lb"] >= .5 for c in EXTRA)
elif cls == "C3_sheet_specific":
    showing = [c for c in POOLS if pooled[c]["below"] >= 28
               and pooled[c]["wilson_lb"] >= .5]
    defining_ok = len(showing) >= 3
else:
    defining_ok = pooled["mm"]["wilson_lb"] >= .5
fold = bool(same and defining_ok)

out = dict(card="L157 slow-line-carrier census", win=WIN, dt=DT,
           channels=CHANNELS, pairs=[list(p) for p in PAIRS],
           table=table, pooled=pooled, pairs_table=pair_tbl,
           per_file_cls=per_file_cls, claim_class=cls,
           fold_draft=fold)
json.dump(out, open("l157/static.json", "w"), indent=1)

print(f"\nclaim class: {cls} (same on both files: {same}); "
      f"draft fold: {'YES' if fold else 'NO'}")
for f in FILES:
    c = per_file_cls[f]
    print(f"  {f}: {c['cls']} pools_showing={c['n_pools_showing']}/20 "
          f"pairs_both={c['pairs_both']}/10 extra={c['extra']}")
print("\npooled b65 (36 traces/ch): below/bin/lb/surv/medf  | slow_share mean")
for ch in CHANNELS:
    p = pooled[ch]
    sh = np.mean([share[(f, 'b65', ch)] for f in FILES])
    print(f"  {ch:5s} {p['below']:2d}/{p['n']} bin {p['below_bin']:2d} "
          f"lb {p['wilson_lb']:.3f} surv {p['survive']:2d} "
          f"med {p['med_f_below'] if p['med_f_below'] is None else round(p['med_f_below'],3)} "
          f"| {sh:.3f}")
print("\nantagonist slow phase (b65): pair | file | circ_mean | antiphase/18")
for k, v in pair_tbl.items():
    if "|b65|" in k:
        print(f"  {k.replace('|b65|', ' | ')}: {v['circ_mean']:+7.1f} deg "
              f"anti {v['n_antiphase']}/{v['n']} bin {v['med_bin']:.3f}")
print("l157/static.json written")
