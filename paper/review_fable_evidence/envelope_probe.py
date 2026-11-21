# Reviewer's own probe (read-only on lab files): spectrum of the chopped entrainment-drive envelope
import json, math, numpy as np, collections
WIN, DT, ENT_AMP, SEG = 6000, 0.01, 0.1, 2000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
def target(k):
    for a, b, f in SEGB:
        if a <= k < b: return f
    return SEGB[-1][2]
AMPA = np.zeros(WIN)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
ph = 0.0; PHI = np.empty(WIN)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT; PHI[i] = ph
drive = np.where(AMPA > 0, ENT_AMP * (0.5 + 0.5 * np.sin(PHI)), 0.0)
env = AMPA.copy()
def spec(x):
    x = x - x.mean(); P = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), DT); return f, P
for name, x in (("drive(sin*chop)", drive), ("chop envelope only", env)):
    f, P = spec(x)
    order = np.argsort(-P)[:8]
    print(name, "top bins:", [(round(float(f[i]), 4), round(float(P[i] / P.max()), 3)) for i in order])
    lowmask = f < 0.3
    i0 = np.argmax(np.where(lowmask, P, 0)); print("   strongest sub-0.3Hz bin:", round(float(f[i0]), 4), "rel power", round(float(P[i0] / P.max()), 3))
# low-pass view: what a slow integrator (tau 50 ms cells but network-level smoothing) sees = running mean over one 0.7 Hz cycle
k = int(round(1 / 0.7 / DT)); sm = np.convolve(drive, np.ones(k) / k, mode="same")
f, P = spec(sm); order = np.argsort(-P)[:6]
print("cycle-averaged drive top bins:", [(round(float(f[i]), 4), round(float(P[i] / P.max()), 3)) for i in order])

# census rows from the lab's stored static.json (read-only)
s = json.load(open("/home/t3rpz/critters/peabrain-lab/banc/l156/static.json"))
rows = s["rows"]
print("files:", len(rows))
cnt = collections.Counter(); cntbin = collections.Counter()
perfile = {}
for fn, arms in rows.items():
    if "b65" in arms and "l139" not in fn:
        v = [x["f_glob_bin"] for x in arms["b65"].values()]
        perfile[fn] = collections.Counter(round(x, 4) for x in v)
        for x in arms["b65"].values():
            cntbin[round(x["f_glob_bin"], 4)] += 1
print("b65 f_glob_bin histogram (non-jitter):", sorted(cntbin.items()))
for fn in list(perfile)[:40]:
    print("  ", fn, dict(sorted(perfile[fn].items())))
# closure 'full' arm
cf = collections.Counter()
for fn, arms in rows.items():
    if "full" in arms and "l139" not in fn:
        for x in arms["full"].values(): cf[round(x["f_glob_bin"], 4)] += 1
print("full f_glob_bin histogram:", sorted(cf.items()))
# l154 off arm
if "l154/raw_l154.npz" in rows:
    for arm in rows["l154/raw_l154.npz"]:
        c = collections.Counter(round(x["f_glob_bin"], 4) for x in rows["l154/raw_l154.npz"][arm].values())
        print("l154 arm", arm, sorted(c.items()))
print("keys of a row:", list(next(iter(next(iter(rows.values())).values())).values())[0].keys())
