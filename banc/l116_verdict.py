"""L116 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
5-pair x 5-arm per-side duty table + flip classification. PREREG l116/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
ARMS = ["full", "b65", "cut", "cut19", "cut58"]
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]          # ag/bg agonist/antagonist prefixes
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z113 = np.load("l113/raw_l113.npz")
z116 = np.load("l116/raw_l116.npz")
r113 = json.load(open("l113/results_l113.json"))
ar = json.load(open("l116/anchors_run.json"))
SM = {}


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def s_arrays(raw, a, s, pk):
    """Sliding 500-step antagonist anticorrelation per side (l113 VERBATIM,
    generalized only in the agonist/antagonist pool-name prefixes)."""
    key = (id(raw), a, s, pk)
    if key not in SM:
        ag, bg = PREF[pk]
        tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN]
              for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(tr[f"{ag}L"][t - 499:t + 1], tr[f"{bg}L"][t - 499:t + 1])
            SR[t] = S_of(tr[f"{ag}R"][t - 499:t + 1], tr[f"{bg}R"][t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


def per_seed(raw, a, seeds, pk):
    """Rounded per-seed duty values (the l109/l111/l113 rounding-path atom)."""
    L, R = [], []
    for s in seeds:
        SL, SR = s_arrays(raw, a, s, pk)
        q07 = np.zeros(len(TS), bool)
        for a0, b0, f in SEGB:
            if f == 0.7:
                q07 |= (TS >= a0 + MEAS0) & (TS < b0)
        L.append(round(float(np.nanmean(SL[TS[q07]] >= .25)), 3))
        R.append(round(float(np.nanmean(SR[TS[q07]] >= .25)), 3))
    return np.array(L), np.array(R)


def side_k(raw, a, seeds, pk):
    L, R = per_seed(raw, a, seeds, pk)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ---- Part 1: C0B on stored raw_l113 (BEFORE any L116 pin) ----
c0b_fail = []
for a in ARMS:
    for tab, pk in ((r113["table_b10"], "Ti"), (r113["tr_b10"], "Tr")):
        want = tab[a]
        got = side_k(z113, a, B10, pk)
        for kk in ("kL", "kR", "meanL", "meanR"):
            if got[kk] != want[kk]:
                c0b_fail.append((a, pk, kk, got[kk], want[kk]))
c0b_pass = not c0b_fail
print("C0B certification (stored l113, Ti+Tr tables, ALL 5 arms):",
      "PASS" if c0b_pass else f"FAIL {c0b_fail[:5]}")

# ---- Part 2: metric-level bit-identity (l116 npz vs l113 pins) ----
mli_fail = []
for a in ARMS:
    for pk in ("Ti", "Tr"):
        got = side_k(z116, a, B10, pk)
        want = (r113["table_b10"] if pk == "Ti" else r113["tr_b10"])[a]
        for kk in ("kL", "kR", "meanL", "meanR"):
            if got[kk] != want[kk]:
                mli_fail.append((a, pk, kk, got[kk], want[kk]))
mli_pass = not mli_fail
print("Metric-level identity (l116 npz Ti/Tr vs l113 pins):",
      "PASS" if mli_pass else f"FAIL {mli_fail[:5]}")

# ---- P0 anchors (gate booleans ONLY; c0a_max is a diagnostic, L59 rule) ----
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
          g_cut58_stored_exact=ar["g_cut58_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cut58_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (full batch):", "PASS" if p0["pass"] else "FAIL",
      f"(max {p0['c0a_max']:.1e}, seeds {p0['n_seeds']}, g58 {p0['g_cut58_stored_exact']})")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z116[f"af_{a}_{s}"]) for s in B10])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z116[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B10)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 3: the registered 5-pair x 5-arm per-side table (B10) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z116, a, B10, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
    for a in ARMS:
        t = table[pk][a]
        print(f"{pk} {a:6s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Part 4: registered flip classification (cut58 vs full; cut vs full) ----
def classify(pk, arm):
    c, f = table[pk][arm], table[pk]["full"]
    dL = c["meanL"] - f["meanL"]
    dR = c["meanR"] - f["meanR"]
    flip_l = dL >= .20
    kill_r = dR <= -.20
    r_spared = c["meanR"] >= f["meanR"] - .10
    if flip_l and kill_r:
        cls = "Ti-like flip (L restored + R killed)"
    elif flip_l and r_spared:
        cls = "L-restore with R-SPARED (Tr pattern)"
    elif flip_l:
        cls = "L-only"
    elif dR >= .20:
        cls = "INVERTED (R-side restoration)"
    elif dL <= -.20 or dR <= -.20:
        cls = "suppress-only"
    else:
        cls = "no-flip"
    return dict(cls=cls, dL=round(dL, 3), dR=round(dR, 3), kL=c["kL"],
                kR=c["kR"], full_kL=f["kL"], full_kR=f["kR"])

flip = {arm: {pk: classify(pk, arm) for pk in PAIRS}
        for arm in ("cut58", "cut")}
for arm in ("cut58", "cut"):
    print(f"---- flip classification {arm} vs full ----")
    for pk in PAIRS:
        c = flip[arm][pk]
        print(f"{pk}: {c['cls']} (dL {c['dL']:+.3f}, dR {c['dR']:+.3f})")

# ---- Pr floor disclosure (registered as expected-floor) ----
pr = table["Pr"]
pr_note = dict(base_floor=bool(max(pr["full"]["meanL"], pr["full"]["meanR"]) < .20),
               note="Pr registered expected-floor: no structure to flip; "
                    "'no-flip' there is a floor artifact, never specificity")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], mli_pass=mli_pass,
           p0=p0, p4=p4, table=table, flip=flip, pr_note=pr_note,
           g_cut58=ar["g_cut58"])
json.dump(out, open("l116/results_l116.json", "w"), indent=1)
print("results_l116.json written")
