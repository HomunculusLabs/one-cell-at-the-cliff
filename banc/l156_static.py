# L156 static census: sub-band slow-line prevalence across the stored lineage
# PREREG l156/PREREG.md registered FIRST. Zero rollouts, read-only.
import glob
import json
import math
import os

import numpy as np

WIN, DT = 6000, 0.01
HALF = WIN // 2
FBIN = 1.0 / (WIN * DT)          # 1/60 Hz fine bin
HBIN = 1.0 / (HALF * DT)         # 1/30 Hz coarse (half-window) bin
Z = 1.959963984540054


def dom_freq(x, lo=0.3):         # VERBATIM l154_verdict.py (l94 lineage)
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


def bin_argmax(x, lo=0.0):       # ADDENDUM 1: un-interpolated form
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    return float(fb[int(np.argmax(pb))])


def wilson_lb(k, n):
    if n == 0:
        return float("nan")
    p = k / n
    den = 1 + Z * Z / n
    ctr = p + Z * Z / (2 * n)
    rad = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (ctr - rad) / den


# ---------------- CERT (PREREG): machinery vs l154 STORED -------------------
t = np.arange(WIN) * DT
for f0 in (0.7, 1.4):
    fh, _ = dom_freq(np.sin(2 * math.pi * f0 * t))
    assert abs(fh - f0) < 0.01, ("self-test", f0, fh)
print("CERT analytic self-test (0.7/1.4 Hz): PASS")

raw154 = np.load("l154/raw_l154.npz")
r154 = json.load(open("l154/results_l154.json"))
B34 = list(range(3401, 3417))
ANCH = [801, 901]
cert_rows = {}
for a in ("b65", "off"):
    for s in ANCH + B34:
        x = raw154[f"mm_{a}_{s}"][:WIN]
        fb_, _ = dom_freq(x)
        fu_, _ = dom_freq(x, lo=0.0)
        cert_rows[(a, s)] = (fb_, fu_, bin_argmax(x) < 0.3)   # ADDENDUM 1: bin form
for s in ANCH:
    for a in ("b65", "off"):
        assert cert_rows[(a, s)][0] == r154["anchors"][str(s)][a], \
            ("anchor", s, a)
for a in ("b65", "off"):
    mb = float(np.mean([cert_rows[(a, s)][0] for s in B34]))
    mu = float(np.mean([cert_rows[(a, s)][1] for s in B34]))
    assert abs(mb - r154["dom_band_mean"][a]) < 1e-12, ("band mean", a)
    assert abs(mu - r154["dom_full_mean"][a]) < 1e-12, ("full mean", a)
bb = {a: int(sum(cert_rows[(a, s)][2] for s in B34)) for a in ("b65", "off")}
assert bb["b65"] == r154["below_band_census"]["on"], bb
assert bb["off"] == r154["below_band_census"]["off"], bb
deltas = [cert_rows[("off", s)][0] - cert_rows[("b65", s)][0] for s in B34]
npos = sum(1 for v in deltas if v > 0)
nneg = sum(1 for v in deltas if v < 0)
assert (npos, nneg) == (r154["n_pos"], r154["n_neg"]), (npos, nneg)
print(f"CERT vs l154 stored (anchors/means/below {bb}/signs {npos}+/{nneg}-): PASS")

# ---------------- enumeration (input pin) ------------------------------------
files = sorted(glob.glob("*/raw_l*.npz"))
inventory, included = [], []
for f in files:
    z = np.load(f)
    mmks = [k for k in z.files if k.startswith("mm_")]
    has_b65 = any(k.startswith("mm_b65_") for k in mmks)
    inventory.append(dict(file=f, mm_keys=len(mmks), has_b65=bool(has_b65)))
    if has_b65:
        included.append(f)
print(f"inventory: {len(files)} raw npz, {len(included)} carry mm_b65_*")

# ---------------- census -----------------------------------------------------
tt = np.arange(WIN, dtype=np.float64)
rows, excluded = {}, 0
per_arm = {}
for f in included:
    z = np.load(f)
    for k in sorted(z.files):
        if not k.startswith("mm_"):
            continue
        arm, seed = k[3:].rsplit("_", 1)
        x = z[k][:WIN].astype(np.float64)
        if len(x) < WIN or not np.isfinite(x).all():
            excluded += 1
            continue
        f_band, at_floor = dom_freq(x)
        f_glob, _ = dom_freq(x, lo=0.0)
        below = bool(f_glob < 0.3)
        f_gbin = bin_argmax(x)                      # ADDENDUM 1 dual form
        below_bin = bool(f_gbin < 0.3)
        c = np.polyfit(tt, x, 1)
        f_det, _ = dom_freq(x - np.polyval(c, tt), lo=0.0)
        survive = bool(below and f_det < 0.3 and abs(f_det - f_glob) <= FBIN + 1e-9)
        f1, _ = dom_freq(x[:HALF], lo=0.0)
        f2, _ = dom_freq(x[HALF:], lo=0.0)
        agree = bool(abs(f1 - f2) <= HBIN + 1e-9)
        rows.setdefault(f, {}).setdefault(arm, {})[seed] = dict(
            f_band=f_band, at_floor=bool(at_floor), f_glob=f_glob,
            below=below, f_glob_bin=f_gbin, below_bin=below_bin,
            f_det=f_det, survive=survive, agree=agree)
    del z

for f in included:
    for arm, d in rows[f].items():
        bl = [v for v in d.values() if v["below"]]
        per_arm[(f, arm)] = dict(
            n=len(d), below=len(bl), below_bin=sum(v["below_bin"] for v in d.values()),
            below_frac=len(bl) / len(d),
            survive=sum(v["survive"] for v in bl),
            agree=sum(v["agree"] for v in bl),
            med_f_below=float(np.median([v["f_glob"] for v in bl])) if bl else None,
            med_f_all=float(np.median([v["f_glob"] for v in d.values()])))

# ---------------- pooling (registered form) ----------------------------------
def pool(arm, flist):
    allv = [v for f in flist for v in rows.get(f, {}).get(arm, {}).values()]
    bl = [v for v in allv if v["below"]]
    return dict(files=len([f for f in flist if rows.get(f, {}).get(arm)]),
                n=len(allv), below=len(bl),
                below_bin=sum(v["below_bin"] for v in allv),
                below_frac=len(bl) / len(allv) if allv else float("nan"),
                wilson_lb=wilson_lb(len(bl), len(allv)),
                survive=sum(v["survive"] for v in bl),
                agree=sum(v["agree"] for v in bl),
                med_f_below=float(np.median([v["f_glob"] for v in bl])) if bl else None)

nonjitter = [f for f in included if "l139" not in f]
jitter = [f for f in included if "l139" in f]
pooled = {
    "b65_nonjitter": pool("b65", nonjitter),
    "b65_jitter_l139": pool("b65", jitter),
    "full_nonjitter": pool("full", nonjitter),
}

# ---------------- static.json -------------------------------------------------
out = dict(
    card="L156 sub-band slow-line census", win=WIN, dt=DT,
    inventory=inventory, included_files=included, excluded=excluded,
    per_arm={f"{f}|{a}": v for (f, a), v in sorted(per_arm.items())},
    pooled=pooled,
    rows=rows,
)
json.dump(out, open("l156/static.json", "w"), indent=1)

# ---------------- report ------------------------------------------------------
print(f"\nexcluded traces: {excluded}")
for name, p in pooled.items():
    print(f"POOLED {name}: below {p['below']}/{p['n']} "
          f"frac {p['below_frac']:.3f} lb {p['wilson_lb']:.3f} | "
          f"survive {p['survive']}/{p['below']} agree {p['agree']}/{p['below']}"
          + (f" | med slow {p['med_f_below']:.3f} Hz" if p["med_f_below"] is not None else ""))
print("\nper-file b65/full rows (n, below, survive, agree, med f_below):")
for f in included:
    for arm in ("b65", "full"):
        if (f, arm) in per_arm:
            p = per_arm[(f, arm)]
            mb = f"{p['med_f_below']:.3f}" if p["med_f_below"] is not None else "-"
            print(f"  {f:22s} {arm:5s} n={p['n']:3d} below={p['below']:3d} "
                  f"surv={p['survive']:3d} agr={p['agree']:3d} med={mb}")

# decision rule (registered)
pb65 = pooled["b65_nonjitter"]
amend = bool(pb65["n"] and pb65["wilson_lb"] >= 0.5
             and pb65["survive"] >= pb65["below"] / 2)
print(f"\nDECISION RULE amend-draft §4: {'YES' if amend else 'NO'} "
      f"(lb {pb65['wilson_lb']:.4f} >= 0.5? survive "
      f"{pb65['survive']}/{pb65['below']} >= half?)")
print("l156/static.json written")
