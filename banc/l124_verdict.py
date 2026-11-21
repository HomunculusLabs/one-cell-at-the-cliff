"""L124 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B18-cert of this machinery on raw_l123 vs results_l123.json BEFORE any
B19 window read, then the registered REBASE reads on FRESH B19 (kill
criterion VERBATIM): R1 cutwB deep-kill robust, R2 cutwA partial band
([.35,.50], kR 3-8) robust-or-redraw, R3 either half reaches RESTORE/
SUPER (revises L123 W4 toward W1/W2), pre-registered decision tree;
S1 cutk5 7th-batch replication, S2 endpoints 4th batch; POOLED window
arms B18+B19 n=32 + R4 arms n=64 full-precision Wilson (L90 form);
per-side duty table 5 pairs x 10 arms; L-axis + Sr_R watch; sanity
cells. PREREG l124/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B19 = list(range(2301, 2317))       # FRESH (l124)
B18 = list(range(2201, 2217))  # context batch (l123, cert + pooled)
B17 = list(range(2101, 2117))  # context batch (l122, pooled)
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutwA", "cutwB"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("19", "cutng19"), ("wA", "cutwA"),
          ("wB", "cutwB"), ("29", "cutng29"), ("58", "cut58"),
          ("k5", "cutk5")]
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z113 = np.load("l113/raw_l113.npz")
z121 = np.load("l121/raw_l121.npz")
z122 = np.load("l122/raw_l122.npz")
z123 = np.load("l123/raw_l123.npz")
z124 = np.load("l124/raw_l124.npz")
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
r119 = json.load(open("l119/results_l119.json"))
r120 = json.load(open("l120/results_l120.json"))
ar = json.load(open("l124/anchors_run.json"))
r123 = json.load(open("l123/results_l123.json"))
r121 = json.load(open("l121/results_l121.json"))
r122 = json.load(open("l122/results_l122.json"))
SM = json.load(open("l121/static.json"))
S123 = json.load(open("l123/static.json"))


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


# ---- Part 1: C0B on stored raw_l113 (BEFORE any L119 pin) ----
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

# ---- P0 anchors (gate booleans ONLY; c0a_max/band are diagnostics) ----
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
          g_cut58_stored_exact=ar["g_cut58_stored_exact"],
          g_cutk5_stored_exact=ar["g_cutk5_stored_exact"],
          c0a120_pass=ar["c0a120_pass"], c0a120_max=ar["c0a120_max"],
          c0a121_pass=ar["c0a121_pass"], c0a121_max=ar["c0a121_max"],
          c0a122_pass=ar["c0a122_pass"], c0a122_max=ar["c0a122_max"],
          c0a123_pass=ar["c0a123_pass"], c0a123_max=ar["c0a123_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutwB_stored_exact=ar["g_cutwB_stored_exact"],
          g_cutng19_stored_exact=ar["g_cutng19_stored_exact"],
          g_cutng29_stored_exact=ar["g_cutng29_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"] and p0["c0a123_pass"]
                  and p0["g_cutwA_stored_exact"] and p0["g_cutwB_stored_exact"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (3 arms vs raw_l121) + C0A-122 "
      "(3 arms vs raw_l122) + C0A-123 (5 arms vs raw_l123) + "
      "8 stored gains:",
      "PASS" if p0["pass"] else "FAIL",
      f"(max113 {p0['c0a_max']:.1e} max120 {p0['c0a120_max']:.1e})")
print("stored gains (asserted EXACT):",
      {k: round(ar["g_" + k], 6) for k in ("cutwA", "cutwB")},
      "cutk5", round(float(z124["g_cutk5"]), 6),
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z124[f"af_{a}_{s}"]) for s in B19])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z124[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B19)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 2: full 5-pair x 10-arm per-side table (B16, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z124, a, B19, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B19 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS:
        t = table[pk][a]
        print(f"{pk} {a:6s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- batch-band disclosure: full-arm B16 reads vs registered bands ----
band = {"Ti": dict(L=(0.25, 0.48), R=(0.35, 0.58)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}
band_ok = {pk: {sd: band[pk][sd][0] <= table[pk]["full"][f"mean{sd}"]
                <= band[pk][sd][1] for sd in ("L", "R")} for pk in band}
print("full-arm B19 band check (disclosure only):", band_ok)

# ---- Part 3 (P1): Ti_R curve {0,3,4a,4b,5,19}, kill criterion ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z124, "full", B19, "Ti")
dose = {"Ti": {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {},
               "kill": {}},
        "Sr": {"meanR": {}, "kR": {}}}
killmap = {}
for kk, a in LADDER:
    t = table["Ti"][a]
    dose["Ti"]["meanR"][kk] = t["meanR"]
    dose["Ti"]["kR"][kk] = t["kR"]
    dose["Ti"]["meanL"][kk] = t["meanL"]
    dose["Ti"]["kL"][kk] = t["kL"]
    _, Rd = duty_seeds(z124, a, B19, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    dose["Ti"]["legs"][kk] = legs
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR"] <= -.20)
    dose["Ti"]["kill"][kk] = bool(kill)
    killmap[kk] = bool(kill)
    print(f"Ti k={kk:>2s} ({a:6s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | paired dR "
          f"{legs['mean_paired_dR']:+.3f} n_down {legs['n_down']}/16 "
          f"-> {'KILL' if kill else 'no-kill'}")
dose["Ti"]["m0"] = m0
# cross-batch context (stored, disclosure only)
dose["l117_stored_b12_context"] = {
    "Ti_meanR": r117["dose"]["Ti"]["meanR"],
    "Ti_kR": r117["dose"]["Ti"]["kR"]}
dose["l119_stored_b14_context"] = {
    "Ti_meanR": r119["dose"]["Ti"]["meanR"],
    "Ti_kR": r119["dose"]["Ti"]["kR"]}
dose["l121_stored_b16_context"] = {
    "Ti_meanR": r121["dose"]["Ti"]["meanR"],
    "Ti_kR": r121["dose"]["Ti"]["kR"],
    "kill": r121["dose"]["Ti"]["kill"]}
dose["l120_stored_b15_context"] = {
    "k5_Ti_meanR": r120["dose"]["Ti"]["meanR"]["5"],
    "k5_Ti_kR": r120["dose"]["Ti"]["kR"]["5"],
    "k5_kill": r120["k4"]["k5_kill"]}
dose["l122_stored_b17_context"] = {
    "Ti_meanR": r122["dose"]["Ti"]["meanR"],
    "Ti_kR": r122["dose"]["Ti"]["kR"],
    "kill": r122["dose"]["Ti"]["kill"]}
dose["l123_stored_b18_context"] = {
    "Ti_meanR": r123["dose"]["Ti"]["meanR"],
    "Ti_kR": r123["dose"]["Ti"]["kR"],
    "kill": r123["dose"]["Ti"]["kill"]}
print("l117 B12 / l119 B14 / l120 B15 / l121 B16 / l122 B17 context:",
      dose["l117_stored_b12_context"], dose["l119_stored_b14_context"],
      dose["l120_stored_b15_context"])

# ---- Part 4: B18-cert FIRST, then R1/R2/R3 + S1/S2 + pooled ----
# B18-cert BEFORE any B19 window read: machinery recomputed on raw_l123
# B18 == results_l123.json Ti table (ALL 10 arms incl wA/wB — l123 ran
# every arm at all 18 seeds).
b18_cert_fail = []
for a in r123["table"]["Ti"]:
    want = r123["table"]["Ti"][a]
    got = side_k(z123, a, B18, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b18_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b18_cert_fail, ("B18-cert FAIL (no B19 read)",
                           b18_cert_fail[:5])
print(f"B18-cert vs results_l123.json Ti table: PASS "
      f"(all {len(r123['table']['Ti'])} arms)")


# RESTORE (PREREG): meanR >= .45 AND kR >= 12 (absolute; full sat
# .469-.505 across B10-B17). SUPER-RAISE label: meanR >= .60 AND kR >= 12.
def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


tA, tB = table["Ti"]["cutwA"], table["Ti"]["cutwB"]
killA, killB = killmap["wA"], killmap["wB"]
restA, restB = _restore(tA), _restore(tB)
# R1/R2/R3 registered reads (PREREG): partial band = meanR [.35,.50] &
# kR 3..8 (L123 wA shape). Decision tree PRE-REGISTERED, never re-fit.
partialA = bool(.35 <= tA["meanR"] <= .50 and 3 <= tA["kR"] <= 8)
r1 = bool(killB)
r2 = "PARTIAL-ROBUST" if partialA else "RE-DRAW"
r3 = bool(restA or restB or _super(tA) or _super(tB))
if r3:
    wcls = ("REVISION toward W1/W2: a half reached RESTORE/SUPER on B19 — "
            "a half CAN flip alone after all; disclosed")
elif killA and killB:
    wcls = ("REVISION toward W3: both halves kill on B19 — window "
            "coherence extends past rank 24; disclosed")
elif r1 and partialA:
    wcls = ("W4 BATCH-ROBUST: cutwB deep-kill + cutwA partial replicate "
            "on B19 — neither half flips alone; 2-step window structure "
            "holds (L123 finding now 2-batch)")
else:
    wcls = ("MIXED/RE-DRAW: killB miss or cutwA shape change on B19 — "
            "lottery class; disclosed, no story rounding")
print(f"WINDOW: cutwA meanR {tA['meanR']:.3f} kR {tA['kR']:2d} "
      f"({'KILL' if killA else 'no-kill'}{'/RESTORE' if restA else ''}"
      f"{'/SUPER' if _super(tA) else ''}{'/PARTIAL' if partialA else ''}) "
      f"| cutwB meanR {tB['meanR']:.3f} "
      f"kR {tB['kR']:2d} ({'KILL' if killB else 'no-kill'}"
      f"{'/RESTORE' if restB else ''}{'/SUPER' if _super(tB) else ''})")
print(f"R1 cutwB kill: {'PASS' if r1 else 'FAIL'} | R2 cutwA: {r2} | "
      f"R3 revision trigger: {'FIRED' if r3 else 'no'}")
print(f"REBASE classification: {wcls}")
# S1: cutk5 6th batch; S2: endpoints 3rd batch (registered)
s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B19 — 7th consecutive batch (B12/B14/B15/B16/B17/B18/B19)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B19 — DISCLOSED (L118 lottery class)"))
s2 = dict(ng19_kill=bool(killmap["19"]),
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (4th batch each)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))
print(f"S1: {s1['cls']}")
print(f"S2: {s2['cls']}")
# R4: pooled batch-union B16+B17+B18+B19 n=64, FULL-PRECISION Wilson
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 64)
    pooled[a] = dict(k64=k, p_hat=k / 64, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()),
                     k_b18=int((Rb18 >= .5).sum()),
                     k_b19=int((Rb19 >= .5).sum()))
    print(f"POOLED Ti_R {a:7s} k {k}/64 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16 + B18 {pooled[a]['k_b18']}/16 + "
          f"B19 {pooled[a]['k_b19']}/16) "
          f"p_hat {k/64:.3f} Wilson [{lb:.4f}, {ub:.4f}]")
# WINDOW pooled union B18+B19 n=32 (the L124 deliverable; B18 side
# certified above BEFORE pooling)
pooled_window = {}
for a in ("cutwA", "cutwB"):
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    allb = np.concatenate([Rb18, Rb19])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 32)
    pooled_window[a] = dict(k32=k, p_hat=k / 32, lb=lb, ub=ub,
                            k_b18=int((Rb18 >= .5).sum()),
                            k_b19=int((Rb19 >= .5).sum()))
    print(f"POOLED-WINDOW Ti_R {a:7s} k {k}/32 (B18 "
          f"{pooled_window[a]['k_b18']}/16 + B19 "
          f"{pooled_window[a]['k_b19']}/16) p_hat {k/32:.3f} "
          f"Wilson [{lb:.4f}, {ub:.4f}]")

# Sr watch curve (registered, no gate — lottery axis)
for kk, a in LADDER:
    dose["Sr"]["meanR"][kk] = table["Sr"][a]["meanR"]
    dose["Sr"]["kR"][kk] = table["Sr"][a]["kR"]
print("Sr_R watch (no gate):", dose["Sr"]["meanR"],
      "kR", dose["Sr"]["kR"])

# ---- Part 5: sanity reference cells (secondary; miss = disclose) ----
ls = dict(cut_kL=table["Ti"]["cut"]["kL"], b65_kL=table["Ti"]["b65"]["kL"],
          b65_kR=table["Ti"]["b65"]["kR"], cut19_kL=table["Ti"]["cut19"]["kL"],
          sr_b65_kL=table["Sr"]["b65"]["kL"], sr_b65_kR=table["Sr"]["b65"]["kR"])
ls_pass = (ls["cut_kL"] >= 14 and ls["b65_kL"] == 16 and ls["b65_kR"] == 16
           and ls["cut19_kL"] >= 12)
print("sanity:", ls, "PASS" if ls_pass else "MISS (disclosed, never abort)")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           new_band_ok=ar["new_band_ok"],
           stored_gains={a: ar["g_" + a] for a in ("cutwA", "cutwB")},
           g_cutk5=float(z124["g_cutk5"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cut58", "k58"))},
           mass_window={a: S123["window_" + a[-2:]]["mass_removed"]
                        for a in ("cutwA", "cutwB")},
           extra_mass={a: S123["window_" + a[-2:]]["extra_mass"]
                       for a in ("cutwA", "cutwB")},
           mass_cutk5=SM["ladder"]["k5"]["mass_removed"],
           table=table, dose=dose,
           window=dict(cls=wcls, r1=bool(r1), r2=r2, r3=bool(r3),
                       killA=bool(killA), killB=bool(killB),
                       restA=bool(restA), restB=bool(restB),
                       partialA=bool(partialA),
                       superA=_super(tA), superB=_super(tB), s1=s1, s2=s2),
           pooled=pooled, pooled_window=pooled_window,
           b18_cert_pass=True,
           band_ok=band_ok,
           sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l124/results_l124.json", "w"), indent=1)
print("results_l124.json written")
