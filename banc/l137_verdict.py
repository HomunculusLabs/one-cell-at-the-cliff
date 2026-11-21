"""L137 verdict: C0B (l113 atoms) + B-cert of this machinery on
raw_l135 vs results_l135.json (ALL 13 arms, zero-rollout L85 form,
ADDENDUM A2) BEFORE any B27 read, then the registered intervention
reads on FRESH B27 (criteria VERBATIM L118-L131): G1 sil1110 vs
sil319 ACTIVITY/WIRING/WRONG-DIR branches (ADDENDUM A5), G2 vol1110
direction (sham volrand), G3 silrand spread floor, dm probes every
arm (A6), census clamp-no-op readout (A4), sil24 population-clamp
twin of cutwA, pooled full-union B16..B27 n=192 (A7). PREREG
l137/PREREG.md + ADDENDUM."""

import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B26 = list(range(3001, 3017))       # FRESH (l135)
B25 = list(range(2901, 2917))  # context batch (l133, cert + pooled)
B24 = list(range(2801, 2817))  # context batch (l131, pooled)
B23 = list(range(2701, 2717))  # context batch (l128, cert)
B22 = list(range(2601, 2617))  # context batch (l127, R4 pool)
B21 = list(range(2501, 2517))  # context batch (l126, P3 pool)
B20 = list(range(2401, 2417))  # context batch (l125, cert + pooled)
B19 = list(range(2301, 2317))  # context batch (l124, pooled)
B18 = list(range(2201, 2217))  # context batch (l123, pooled)
B17 = list(range(2101, 2117))  # context batch (l122, pooled)
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
NEW_ARMS = ["cutk5", "cutng19", "cutng23", "cutwA", "cutng25",
            "cutng25p", "cutng26", "cutng29"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("19", "cutng19"), ("23", "cutng23"),
          ("24", "cutwA"), ("25", "cutng25"), ("25p", "cutng25p"),
          ("26", "cutng26"), ("29", "cutng29"), ("58", "cut58"),
          ("k5", "cutk5")]
CURVE = ["19", "23", "24", "25", "25p", "26", "29"]   # registered curve
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054
B27 = list(range(3101, 3117))       # FRESH (l137)
z113 = np.load("l113/raw_l113.npz")
z121 = np.load("l121/raw_l121.npz")
z122 = np.load("l122/raw_l122.npz")
z123 = np.load("l123/raw_l123.npz")
z124 = np.load("l124/raw_l124.npz")
z125 = np.load("l125/raw_l125.npz")
z126 = np.load("l126/raw_l126.npz")
z127 = np.load("l127/raw_l127.npz")
z128 = np.load("l128/raw_l128.npz")
z131 = np.load("l131/raw_l131.npz")
z133 = np.load("l133/raw_l133.npz")
z135 = np.load("l135/raw_l135.npz")
z137 = np.load("l137/raw_l137.npz")
r113 = json.load(open("l113/results_l113.json"))
r135 = json.load(open("l135/results_l135.json"))
ar = json.load(open("l137/anchors_run.json"))
S131 = json.load(open("l131/static.json"))
S133 = json.load(open("l133/static.json"))
IARMS = ["sil1110", "sil319", "silrand1", "silrand2", "silrand3",
         "vol1110", "volrand", "sil24"]
V_ARMS = ["full", "b65"] + IARMS
POOL_BATCH = [("B16", z121, list(range(2001, 2017))),
              ("B17", z122, list(range(2101, 2117))),
              ("B18", z123, list(range(2201, 2217))),
              ("B19", z124, list(range(2301, 2317))),
              ("B20", z125, list(range(2401, 2417))),
              ("B21", z126, list(range(2501, 2517))),
              ("B22", z127, list(range(2601, 2617))),
              ("B23", z128, list(range(2701, 2717))),
              ("B24", z131, list(range(2801, 2817))),
              ("B25", z133, list(range(2901, 2917))),
              ("B26", z135, list(range(3001, 3017))),
              ("B27", z137, B27)]

def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


_SM = {}


def s_arrays(raw, a, s, pk):
    key = (id(raw), a, s, pk)
    if key not in _SM:
        ag, bg = PREF[pk]
        tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN]
              for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(tr[f"{ag}L"][t - 499:t + 1], tr[f"{bg}L"][t - 499:t + 1])
            SR[t] = S_of(tr[f"{ag}R"][t - 499:t + 1], tr[f"{bg}R"][t - 499:t + 1])
        _SM[key] = (SL, SR)
    return _SM[key]


def duty_seeds(raw, a, seeds, pk):
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
    L, R = duty_seeds(raw, a, seeds, pk)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ---- Part 1: C0B on stored raw_l113 (BEFORE any L137 pin) ----
c0b_fail = []
for a in STORED_ARMS:
    for tab, pk in ((r113["table_b10"], "Ti"), (r113["tr_b10"], "Tr")):
        want = tab[a]
        got = side_k(z113, a, B10, pk)
        for kk in ("kL", "kR", "meanL", "meanR"):
            if got[kk] != want[kk]:
                c0b_fail.append((a, pk, kk, got[kk], want[kk]))
c0b_pass = not c0b_fail
print("C0B certification (stored l113, Ti+Tr tables, ALL 5 stored arms):",
      "PASS" if c0b_pass else f"FAIL {c0b_fail[:5]}")

# ---- P0 anchors (gate booleans ONLY; magnitudes are diagnostics) ----
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"],
          c0a135_pass=ar["c0a135_pass"], c0a135_max=ar["c0a135_max"],
          probe_pass=ar["probe_pass"], probe_max=ar["probe_max"],
          vamp=ar["vamp"], census_1110=ar["census_1110"],
          census_319=ar["census_319"], silrand=ar["silrand"],
          all_pass=bool(ar["c0a_pass"] and ar["c0a135_pass"]
                        and ar["probe_pass"]))
print("P0 anchors full/b65@801/901 vs raw_l113 + raw_l135 + probe "
      "reroll@3101:", "PASS" if p0["all_pass"] else "FAIL",
      f"(max113 {p0['c0a_max']:.1e} max135 {p0['c0a135_max']:.1e} "
      f"probe {p0['probe_max']:.1e})")

# ---- B-cert (ADDENDUM A2): l135's FULL 13-arm Ti table from stored
# raw_l135 B26 traces == results_l135.json EXACT, BEFORE any B27 read ----
bcert_fail = []
for a in ARMS:
    want = r135["table"]["Ti"][a]
    got = side_k(z135, a, B26, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append((a, kk, got[kk], want[kk]))
assert not bcert_fail, ("B-cert FAIL (no B27 read)", bcert_fail[:5])
print(f"B-cert vs results_l135.json Ti table: PASS (all {len(ARMS)} arms)")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z137[f"af_{a}_{s}"]) for s in B27])), 6)
           for a in V_ARMS}
af_range_ok = all(0.01 < float(z137[f"af_{a}_{s}"]) < 0.9
                  for a in V_ARMS for s in B27)
b65_af = dict(b27_mean=af_mean["b65"],
              l135_b26_band=(0.105056, 0.113056), disclosed=True)
p4 = dict(af_range_ok=bool(af_range_ok), af_mean=af_mean, b65_af=b65_af)
print("P4", json.dumps(p4))

# ---- Part 2: 5-pair x 10-arm per-side table (B27, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in V_ARMS:
        t = side_k(z137, a, B27, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B27 per-side duty table ----")
for pk in PAIRS:
    for a in V_ARMS:
        t = table[pk][a]
        print(f"{pk} {a:8s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- dm probes (ADDENDUM A6; L30/L35 form) ----
dm = {}
for a in V_ARMS[1:]:
    dmm = [float(np.abs(z137[f"mm_{a}_{s}"] - z137[f"mm_full_{s}"]).max())
           for s in B27]
    dxm = [float(np.abs(z137[f"xm_{a}_{s}"] - z137[f"xm_full_{s}"]).max())
           for s in B27]
    dm[a] = dict(dm_mm_max=round(max(dmm), 6),
                 dm_mm_mean=round(float(np.mean(dmm)), 6),
                 dm_xm_max=round(max(dxm), 6),
                 n_bitident_mm=int(sum(1 for v in dmm if v == 0.0)))
print("dm probes (vs full, same stream):",
      {a: (d["dm_mm_max"], d["n_bitident_mm"]) for a, d in dm.items()})

# RESTORE (PREREG): meanR >= .45 AND kR >= 12. SUPER: meanR >= .60 AND
# kR >= 12. PARTIAL band: meanR in [.35,.50] AND kR in 3..8.
def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


# ---- intervention reads (criteria VERBATIM; m0 = B27 full meanR) ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z137, "full", B27, "Ti")
indep = {}
for a in IARMS:
    t = table["Ti"][a]
    _, Rd = duty_seeds(z137, a, B27, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR"] <= -.20)
    indep[a] = dict(meanR=t["meanR"], kR=t["kR"], meanL=t["meanL"],
                    kL=t["kL"], legs=legs, kill=bool(kill),
                    super=_super(t), partial=_partial(t),
                    restore=_restore(t))
    print(f"INT {a:8s}: meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 | "
          f"meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | dR "
          f"{legs['mean_paired_dR']:+.3f} n_down {legs['n_down']}/16 "
          f"-> {'KILL' if kill else ''}{'SUPER' if _super(t) else ''}"
          f"{'PARTIAL' if _partial(t) else ''}"
          f"{'RESTORE' if _restore(t) else ''}")


def in_full_band(t):
    """ADDENDUM A5: no classification AND |dmeanR|<.10 AND kR gap<=4."""
    return bool(not _super(t) and not _partial(t) and not _restore(t)
                and abs(t["meanR"] - m0) < .10
                and abs(t["kR"] - table["Ti"]["full"]["kR"]) <= 4)


s1t, s3t = table["Ti"]["sil1110"], table["Ti"]["sil319"]
g1_a = bool((_super(s1t) or _partial(s1t)) and in_full_band(s3t))
g1_c = bool(indep["sil1110"]["kill"] or s1t["meanR"] <= m0 - .10)
g1_b = bool(not g1_a and not g1_c
            and abs(s1t["meanR"] - s3t["meanR"]) <= .10
            and abs(s1t["kR"] - s3t["kR"]) <= 4)
g1 = dict(
    a_activity=g1_a, b_wiring=g1_b, c_wrong_dir=g1_c,
    sil1110=dict(indep["sil1110"], in_band=in_full_band(s1t)),
    sil319=dict(indep["sil319"], in_band=in_full_band(s3t)),
    dm_sil1110=dm["sil1110"], dm_sil319=dm["sil319"],
    cls=("G1(a) ACTIVITY: sil1110 flips while sil319 stays in full's "
         "band — the cell's ongoing drive carries the suppression"
         if g1_a else
         "G1(c) WRONG DIRECTION: sil1110 kills — census re-read before "
         "wording (L35/L38)"
         if g1_c else
         "G1(b) WIRING: sil1110 ~ sil319 — the flip rides the edge "
         "footprint/renormalization, not the cell's activity"
         if g1_b else
         "G1 MIXED: neither branch cleanly (L55 degenerate — report "
         "where each landed)"))
print(f"G1: {g1['cls']}")
print(f"    sil1110 meanR {s1t['meanR']:.3f} kR {s1t['kR']}/16 "
      f"in_band {in_full_band(s1t)} | sil319 meanR {s3t['meanR']:.3f} "
      f"kR {s3t['kR']}/16 in_band {in_full_band(s3t)} | m0 {m0:.3f}")

# G2: vol1110 direction (sham-referenced)
g2 = dict(vol1110=indep["vol1110"], volrand=indep["volrand"],
          direction=round(indep["vol1110"]["meanR"]
                          - indep["volrand"]["meanR"], 3),
          cls=("vol1110 KILLS vs sham — mirror of removal->super: the "
               "cell's drive SUPPRESSES (activity story)"
               if indep["vol1110"]["kill"] and
               not indep["volrand"]["kill"] else
               "vol1110 direction reported (no kill mirror; disclose)"))
print(f"G2: {g2['cls']} | vol1110 dR "
      f"{indep['vol1110']['legs']['mean_paired_dR']:+.3f} vs volrand "
      f"{indep['volrand']['legs']['mean_paired_dR']:+.3f}")

# G3: sham spread floor (L91 law: the sham share is a headline number)
sr = [indep[f"silrand{i}"]["meanR"] for i in (1, 2, 3)]
srk = [indep[f"silrand{i}"]["kR"] for i in (1, 2, 3)]
spread = round(max(sr) - min(sr), 3)
g3 = dict(silrand_meanR=sr, silrand_kR=srk, spread=spread,
          sil1110_gap=round(abs(indep["sil1110"]["meanR"] - m0), 3),
          sil24_gap=round(abs(indep["sil24"]["meanR"] - m0), 3),
          cls=f"sham spread {spread:.3f} (kR {min(srk)}-{max(srk)}) — "
              f"every clamp credit reads arm-minus-this-spread")
print(f"G3: {g3['cls']}")

# census clamp-no-op readout (ADDENDUM A4)
c1, c3 = ar["census_1110"], ar["census_319"]


def _noop(c):
    if c["x_mean"] < .01:
        return "near-vacuous (cell ~silent -> census leans WIRING)"
    if c["x_mean"] >= .95:
        return "ceiling-pinned (clamp = only visible direction)"
    return f"active (x_mean {c['x_mean']:.3f})"


census = dict(sil1110=dict(c1, read=_noop(c1)),
              sil319=dict(c3, read=_noop(c3)), vamp=ar["vamp"])
print(f"CENSUS 1110: {census['sil1110']['read']} | 319: "
      f"{census['sil319']['read']}")

# sil24 population clamp vs cutwA (stored l135 B26: partial .383/5)
sil24 = indep["sil24"]
sil24_read = dict(sil24, cutwA_l135_b26=dict(meanR=r135["table"]["Ti"]["cutwA"]["meanR"],
                                             kR=r135["table"]["Ti"]["cutwA"]["kR"]),
                  cls=("sil24 (clamp ranks 1-24) lands PARTIAL like the "
                       "cutwA CUT — population-drive effect"
                       if _partial(table["Ti"]["sil24"]) else
                       "sil24 misses the partial band — clamp != cut at "
                       "population scale (the honest divergence)"))
print(f"SIL24: {sil24_read['cls']} | meanR {sil24['meanR']:.3f} "
      f"kR {sil24['kR']}/16 vs cutwA-B26 "
      f"{sil24_read['cutwA_l135_b26']['meanR']:.3f}")

# pooled full-union B16..B27 n=192 (ADDENDUM A7)
Rall = []
for _nm, z, b in POOL_BATCH:
    _, Rb = duty_seeds(z, "full", b, "Ti")
    Rall.append(Rb)
allR = np.concatenate(Rall)
k = int((allR >= .5).sum())
lb, ub = wilson(k, 192)
pooled_full = dict(k192=k, p_hat=k / 192, lb=lb, ub=ub,
                   k_b27=int((Rall[-1] >= .5).sum()))
print(f"POOLED full Ti_R B16..B27 k {k}/192 p_hat {k/192:.3f} "
      f"Wilson [{lb:.4f}, {ub:.4f}] (B27 {pooled_full['k_b27']}/16)")

# watch axes (registered, no gate)
watch = dict(
    Ti_L={a: indep[a]["meanL"] for a in IARMS},
    Ti_L_k={a: indep[a]["kL"] for a in IARMS},
    Sr_R={a: table["Sr"][a]["meanR"] for a in IARMS},
    Tr_R={a: table["Tr"][a]["meanR"] for a in IARMS})
print("WATCH Ti_L:", watch["Ti_L"])

# sanity (secondary; miss = disclose)
ls = dict(b65_kL=table["Ti"]["b65"]["kL"], b65_kR=table["Ti"]["b65"]["kR"],
          full_kR=table["Ti"]["full"]["kR"])
ls_pass = bool(ls["b65_kL"] >= 14 and ls["b65_kR"] == 16)
print("sanity:", ls, "PASS" if ls_pass else "MISS (disclosed, never abort)")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           bcert_pass=True, table=table, dm=dm, indep=indep,
           m0=m0, g1=g1, g2=g2, g3=g3, census=census,
           sil24=sil24_read, pooled_full=pooled_full, watch=watch,
           vamp=ar["vamp"], silrand_ids=[int(x) for x in z137["silrand_ids"]],
           sanity=ls, sanity_pass=ls_pass)
json.dump(out, open("l137/results_l137.json", "w"), indent=1)
print("results_l137.json written")
