"""L106 figure data: laterality scatter for the closure vocabulary arc.

Certification (L85 rule) FIRST: this script's metric copies must reproduce
  - results_l101.json  5 pairs x per-batch duty07L/R means (cfn, raw_l101.npz)
  - results_l103.json  LT/FR alive spreadL/spreadR          (cfn, raw_l103.npz)
  - results_l105.json  free arm 5 pairs x per-batch duty07 means (raw_l105.npz)
EXACTLY before any L106 number is written. New reads (free-arm per-side
duty07/alive07, cfn pooled side means + batch min/max) use the certified
machinery verbatim. Metric copies follow l105_verdict.py (itself C0B-certified
vs l101/l103 in tick 128).
"""
import json
import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
ANCHOR = [11, 22, 33]
B4 = list(range(801, 817)); B5 = list(range(901, 917)); B6 = list(range(1001, 1017))
BATCHES = {"B4": B4, "B5": B5, "B6": B6}
ALLFRESH = B4 + B5 + B6
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
UNPAIRED = ["LT", "FR"]
TS = np.arange(499, WIN, 10)

z101 = np.load("l101/raw_l101.npz"); r101 = json.load(open("l101/results_l101.json"))
z103 = np.load("l103/raw_l103.npz"); r103 = json.load(open("l103/results_l103.json"))
z105 = np.load("l105/raw_l105.npz"); r105 = json.load(open("l105/results_l105.json"))


def s_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


SM = {}
def s_arrays(raw, s, pair, arm="cfn"):
    key = (id(raw), s, pair, arm)
    if key not in SM:
        def nm(c):
            return ("a" if c[0] == "f" else "b") + c[1]
        tr = {c: raw[f"{pair}_{nm(c)}_{arm}_{s}"][:WIN] for c in ("fL", "fR", "eL", "eR")}
        fL, fR, eL, eR = (tr[c] for c in ("fL", "fR", "eL", "eR"))
        SL = np.full(WIN, np.nan); SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = s_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
            SR[t] = s_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


def qmask(f=.7):
    q = np.zeros(len(TS), bool)
    for a0_, b0, ff in SEGB:
        if ff == f:
            q |= (TS >= a0_ + MEAS0) & (TS < b0)
    return q


Q07 = qmask(0.7); Q07_T = TS[Q07]


def cells_pair(raw, s, pair, arm="cfn"):
    SL, SR = s_arrays(raw, s, pair, arm)
    L07 = (SL[Q07_T] >= .25); R07 = (SR[Q07_T] >= .25)
    return dict(duty_07=round(float(np.nanmean(L07 & R07)), 3),
                duty07_L=round(float(np.nanmean(L07)), 3),
                duty07_R=round(float(np.nanmean(R07)), 3))


def cells_lr(raw, s, pool, arm="cfn"):
    L = raw[f"{pool}_L_{arm}_{s}"][:WIN]
    R = raw[f"{pool}_R_{arm}_{s}"][:WIN]
    return dict(alive07_L=round(float(np.mean(L[Q07_T] >= .05)), 3),
                alive07_R=round(float(np.mean(R[Q07_T] >= .05)), 3))


# ---------- C0B certification (L85 rule) ----------
fails = []


def chk(tag, got, want):
    if got != want:
        fails.append((tag, got, want))


for pk in PAIRS:
    tb = r101["tables"][pk]["per_batch"]
    for b in BATCHES:
        got = {s: cells_pair(z101, s, pk) for s in BATCHES[b]}
        chk(f"l101/{pk}/{b}/L", round(float(np.mean([got[s]["duty07_L"] for s in BATCHES[b]])), 3), tb[b]["duty07L_mean"])
        chk(f"l101/{pk}/{b}/R", round(float(np.mean([got[s]["duty07_R"] for s in BATCHES[b]])), 3), tb[b]["duty07R_mean"])
for p in UNPAIRED:
    got = {s: cells_lr(z103, s, p) for s in ALLFRESH}
    chk(f"l103/{p}/spreadL", [round(float(np.mean([got[s]["alive07_L"] for s in BATCHES[b]])), 3) for b in ("B4", "B5", "B6")],
        r103["tables"][p]["alive"]["spreadL"])
    chk(f"l103/{p}/spreadR", [round(float(np.mean([got[s]["alive07_R"] for s in BATCHES[b]])), 3) for b in ("B4", "B5", "B6")],
        r103["tables"][p]["alive"]["spreadR"])
for pk in PAIRS:
    tb = r105["tables"]["free"]["pairs"][pk]["per_batch"]
    for b in BATCHES:
        got = {s: cells_pair(z105, s, pk, "free") for s in BATCHES[b]}
        both = round(float(np.mean([got[s]["duty_07"] for s in BATCHES[b]])), 3)
        chk(f"l105/{pk}/{b}/duty", both, tb[b]["duty07_mean"])

if fails:
    print("CERT FAILS (first 6):")
    for f in fails[:6]:
        print("  ", f)
    raise SystemExit("certification failed - no figure data pinned")

print("C0B certification PASS: 30 l101 reads + 4 l103 lists + 15 l105 reads EXACT")

# ---------- figure data (certified machinery) ----------
fig = {"pairs": {}, "unpaired": {}}
for pk in PAIRS:
    row = {"cfn": {}, "free": {}}
    for arm, raw in (("cfn", z101), ("free", z105)):
        cL = [cells_pair(raw, s, pk, arm)["duty07_L"] for s in ALLFRESH]
        cR = [cells_pair(raw, s, pk, arm)["duty07_R"] for s in ALLFRESH]
        bL = [round(float(np.mean(cL[i * 16:(i + 1) * 16])), 3) for i in range(3)]
        bR = [round(float(np.mean(cR[i * 16:(i + 1) * 16])), 3) for i in range(3)]
        row[arm] = {"L": round(float(np.mean(cL)), 3), "R": round(float(np.mean(cR)), 3),
                    "Lb": [min(bL), max(bL)], "Rb": [min(bR), max(bR)]}
    fig["pairs"][pk] = row
for p in UNPAIRED:
    row = {"cfn": {}, "free": {}}
    for arm, raw in (("cfn", z103), ("free", z105)):
        cL = [cells_lr(raw, s, p, arm)["alive07_L"] for s in ALLFRESH]
        cR = [cells_lr(raw, s, p, arm)["alive07_R"] for s in ALLFRESH]
        bL = [round(float(np.mean(cL[i * 16:(i + 1) * 16])), 3) for i in range(3)]
        bR = [round(float(np.mean(cR[i * 16:(i + 1) * 16])), 3) for i in range(3)]
        row[arm] = {"L": round(float(np.mean(cL)), 3), "R": round(float(np.mean(cR)), 3),
                    "Lb": [min(bL), max(bL)], "Rb": [min(bR), max(bR)]}
    fig["unpaired"][p] = row

json.dump(fig, open("l106/figure_data.json", "w"), indent=1)
print("figure_data.json written")
for pk in PAIRS:
    print(f"  {pk:3s} cfn L {fig['pairs'][pk]['cfn']['L']:.3f} R {fig['pairs'][pk]['cfn']['R']:.3f} | free L {fig['pairs'][pk]['free']['L']:.3f} R {fig['pairs'][pk]['free']['R']:.3f}")
for p in UNPAIRED:
    print(f"  {p:3s} cfn L {fig['unpaired'][p]['cfn']['L']:.3f} R {fig['unpaired'][p]['cfn']['R']:.3f} | free L {fig['unpaired'][p]['free']['L']:.3f} R {fig['unpaired'][p]['free']['R']:.3f}")
