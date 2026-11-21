import json, collections, numpy as np, math
s = json.load(open("/home/t3rpz/critters/peabrain-lab/banc/l156/static.json"))
rows = s["rows"]
# which seeds carry the 0.0167 bin, and how many unique seeds overall in pooled b65 (non-jitter)
seed_files = collections.defaultdict(list); odd = collections.Counter()
for fn, arms in rows.items():
    if "b65" in arms and "l139" not in fn:
        for seed, x in arms["b65"].items():
            seed_files[seed].append(fn)
            if abs(x["f_glob_bin"] - 0.1) > 1e-6: odd[seed] += 1
print("traces:", sum(len(v) for v in seed_files.values()), "unique seeds:", len(seed_files))
dups = {k: len(v) for k, v in seed_files.items() if len(v) > 1}
print("seeds appearing in >1 file:", dups)
print("seeds with non-0.1 peak (count of files):", dict(odd))
# same for the 'full' arm
sf = collections.defaultdict(list)
for fn, arms in rows.items():
    if "full" in arms and "l139" not in fn:
        for seed in arms["full"]: sf[seed].append(fn)
print("full traces:", sum(len(v) for v in sf.values()), "unique seeds:", len(sf), "dups:", {k: len(v) for k, v in sf.items() if len(v) > 1})
# below-band among unique seeds only (full arm): take first occurrence
first = {}
for fn, arms in rows.items():
    if "full" in arms and "l139" not in fn:
        for seed, x in arms["full"].items():
            first.setdefault(seed, x)
k = sum(1 for x in first.values() if x["below"]); n = len(first)
def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z * math.sqrt((p*(1-p) + z*z/(4*n)) / n) / d
    return c - h, c + h
print("full arm unique-seed below-band:", k, n, wilson(k, n))
print("b65 unique-seed n:", len(seed_files), "wilson lb for n/n:", wilson(len(seed_files), len(seed_files))[0])
# direct look at stored traces (read-only): l154 b65 vs off, power at 0.1 Hz bin and correlation with chop envelope
z = np.load("/home/t3rpz/critters/peabrain-lab/banc/l154/raw_l154.npz")
keys = [k for k in z.files if k.startswith("mm_") or k.startswith("xm_")]
print("example keys:", keys[:6], "n keys", len(z.files))
WIN = 6000; DT = 0.01
AMPA = np.zeros(WIN)
for seg0 in (0, 2000, 4000):
    c = 0
    while seg0 + c * 900 < seg0 + 2000:
        lo = seg0 + c * 900; AMPA[lo:min(lo + 500, seg0 + 2000)] = 1; c += 1
AMPA[2000:4000] = 1
f = np.fft.rfftfreq(WIN, DT); b01 = int(np.argmin(abs(f - 0.1)))
def frac01(x):
    x = x[:WIN] - x[:WIN].mean(); P = np.abs(np.fft.rfft(x)) ** 2
    return P[b01] / P[1:].sum(), f[1 + int(np.argmax(P[1:]))]
arms = sorted({k.split("_")[1] for k in z.files if k.startswith("mm_")})
print("arms in l154:", arms)
for arm in arms:
    seeds = sorted({k.split("_")[-1] for k in z.files if k.startswith(f"mm_{arm}_")})
    fr, cors, pk = [], [], []
    for sd in seeds:
        x = z[f"mm_{arm}_{sd}"][:WIN].astype(float)
        a, b = frac01(x); fr.append(a); pk.append(round(float(b), 4))
        cors.append(float(np.corrcoef(x, AMPA)[0, 1]))
    print(f"arm {arm}: n={len(seeds)} median frac power @0.1Hz={np.median(fr):.3f} | median corr(mm, chop envelope)={np.median(cors):+.3f} (min {min(cors):+.3f}, max {max(cors):+.3f}) | peak bins {collections.Counter(pk).most_common(4)}")
    if f"xm_{arm}_{seeds[0]}" in z.files:
        cx = [float(np.corrcoef(z[f"xm_{arm}_{sd}"][:WIN].astype(float), AMPA)[0, 1]) for sd in seeds]
        print(f"     xm (mech sensory mean) corr with chop envelope: median {np.median(cx):+.3f}")
