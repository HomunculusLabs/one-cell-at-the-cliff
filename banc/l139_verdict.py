"""L139 verdict: gain-ensemble robustness of the BANC identity cliff.

C0B-135 certification FIRST (L85 rule): this machinery re-derives l135's
stored B26 Ti table for the 6 shared arms from raw_l135.npz and asserts
EXACT equality — BEFORE any L139 number is pinned. Then per-set reads on
raw_l139_j{0..5}.npz: registered classes (PREREG l139/PREREG.md, VERBATIM
lineage criteria), sustain fractions (gate >= 4/5), per-seed paired flips,
full-arm base context. Metric atoms (S_of/s_arrays/duty_seeds/side_k)
copied VERBATIM from l135_verdict.py (same rounding path, L109 class).
"""

import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
TS = np.arange(499, WIN, 10)
PREF = {"Ti": ("f", "e")}
B26 = list(range(3001, 3017))       # l135 batch (cert source)
B28 = list(range(3201, 3217))       # L139 fresh batch, every set
ARMS = ["full", "cutng23", "cutwA", "cutng25", "cutng25p", "cutng29"]
PRIOR = {"cutng23": "KILL", "cutwA": "PARTIAL", "cutng25": "SUPER",
         "cutng25p": "NEUTRAL-INT", "cutng29": "SUPER"}   # full = reference


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


# ---- Part 0: C0B-135 certification BEFORE any L139 read ----
z135 = np.load("l135/raw_l135.npz")
r135 = json.load(open("l135/results_l135.json"))
c0b_fail = []
for a in ARMS:
    want = r135["table"]["Ti"][a]
    got = side_k(z135, a, B26, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            c0b_fail.append((a, kk, got[kk], want[kk]))
c0b_pass = not c0b_fail
print("C0B-135 certification (6 shared arms, B26 Ti table):",
      "PASS" if c0b_pass else f"FAIL {c0b_fail}")
assert c0b_pass, c0b_fail

# ---- Part 1: anchors + af health per set ----
raws = {j: np.load(f"l139/raw_l139_j{j}.npz") for j in range(6)}
anch = {j: json.load(open(f"l139/anchors_j{j}.json")) for j in range(6)}
assert anch[0]["c0a_pass"] is True and anch[0]["c0a_max"] == 0.0, anch[0]["c0a_max"]
print(f"A1 C0A-135 (set 0 vs raw_l135): PASS max {anch[0]['c0a_max']:.1e} "
      f"({anch[0]['c0a_nkeys']} key-arm-seeds)")
af_bad = []
for j in range(6):
    for a in ARMS:
        for s in B28:
            v = float(raws[j][f"af_{a}_{s}"])
            if not (0.01 < v < 0.9):
                af_bad.append((j, a, s, v))
assert not af_bad, af_bad[:5]
print("A5 af sanity all sets/arms/seeds: PASS (0.01 < af < 0.9)")
print("A4 stairs:", {j: {a: f"{v:.1e}" for a, v in anch[j]["stairs"].items()
                         if not math.isnan(v)} for j in range(1, 6)})
print("gains:", {j: {a: round(g, 6) for a, g in anch[j]["gains"].items()}
                 for j in range(6)})


# ---- Part 2: per-set classes (registered criteria VERBATIM) ----
def classify(a, t, m0, pdR):
    if t["meanR"] <= m0 - .10 and t["kR"] <= 4 and pdR <= -.20:
        return "KILL"
    if t["meanR"] >= .60 and t["kR"] >= 12:
        return "SUPER"
    if .35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8:
        return "PARTIAL"
    if abs(pdR) < .10:
        return "NEUTRAL-INT"
    return "OTHER"


sets = {}
for j in range(6):
    t_full = side_k(raws[j], "full", B28, "Ti")
    _, Rfull = duty_seeds(raws[j], "full", B28, "Ti")
    row = {"full": {**t_full, "pdR": 0.0, "cls": "REF"}}
    for a in PRIOR:
        t = side_k(raws[j], a, B28, "Ti")
        _, Ra = duty_seeds(raws[j], a, B28, "Ti")
        pdR = round(float((Ra - Rfull).mean()), 3)
        row[a] = {**t, "pdR": pdR,
                  "cls": classify(a, t, t_full["meanR"], pdR)}
    sets[j] = row
    print(f"J{j}: " + " | ".join(
        f"{a} {row[a]['cls']:10s} mR {row[a]['meanR']:.3f} kR "
        f"{row[a]['kR']:2d}/16 pdR {row[a]['pdR']:+.3f}" for a in ARMS))

# ---- Part 3: sustain fractions (the registered read) ----
sustain = {}
for a in PRIOR:
    hits = [j for j in range(1, 6) if sets[j][a]["cls"] == PRIOR[a]]
    sustain[a] = dict(prior=PRIOR[a], n=len(hits), frac=len(hits) / 5,
                      classes={j: sets[j][a]["cls"] for j in range(1, 6)},
                      robust=bool(len(hits) >= 4))
    print(f"SUSTAIN {a:9s} -> {PRIOR[a]:10s}: {len(hits)}/5 "
          f"{'ROBUST' if len(hits) >= 4 else 'BOUNDARY-DISCLOSED'} "
          f"{sustain[a]['classes']}")

# ---- Part 4: secondaries ----
full_kR = {j: sets[j]["full"]["kR"] for j in range(6)}
in_spread = all(2 <= v <= 10 for v in full_kR.values())
flips = {}
for a in PRIOR:
    base = duty_seeds(raws[0], a, B28, "Ti")[1] >= .5
    fl = {}
    for j in range(1, 6):
        cur = duty_seeds(raws[j], a, B28, "Ti")[1] >= .5
        fl[j] = int((cur != base).sum())
    flips[a] = fl
    print(f"paired seed flips {a:9s} (duty>=.5 vs set 0): {fl}")

print(f"P3 full kR across sets {full_kR} inside 2-10 base spread: {in_spread}")

out = dict(c0b_pass=c0b_pass, c0a135=dict(max=anch[0]["c0a_max"],
                                          nkeys=anch[0]["c0a_nkeys"]),
           gains={j: anch[j]["gains"] for j in range(6)},
           stairs={j: anch[j]["stairs"] for j in range(6)},
           sets={j: sets[j] for j in range(6)}, sustain=sustain,
           full_kR=full_kR, full_kR_in_spread=in_spread, flips=flips,
           batch_note="single batch B28 per set; sustain over SETS not seeds "
                      "(L88/L90 batch-swing caveat applies to any <= 4/5 verdict)",
           jitter_note="1% iid multiplicative on base edge table, "
                       "default_rng(2001..2005), post-log1p signed vals")
json.dump(out, open("l139/results_l139.json", "w"), indent=1)
print("results_l139.json written")
