"""C0A-166: HALTING anchor for L166. Reproduces the stored L162 pooled MSC
table and the ADDENDUM-3 F-axis aggregates from the stored npz, using
l162_static.py machinery EXEC'd as a verbatim source slice (L85 — never
re-transcribed). Halts on any mismatch. Zero rollouts, read-only, no RNG.
"""
import hashlib
import json
import os

import numpy as np

SRC = "l162_static.py"
lines = open(SRC).read().split("\n")
SLICE_A = "\n".join(lines[0:106])      # constants + machinery + CERT-3
SLICE_B = "\n".join(lines[205:218])    # pair_read + clears
sha_a = hashlib.sha256(SLICE_A.encode()).hexdigest()[:16]
sha_b = hashlib.sha256(SLICE_B.encode()).hexdigest()[:16]

NS = {}
exec(compile(SLICE_A, f"{SRC}[1:106]", "exec"), NS)
for name in ("seg_vec", "msc_matrix", "wilson_lb", "K", "WIN", "SEG", "HOP",
             "BIN_SEG", "BIN_FULL", "POOLS", "CHANNELS", "FILES", "ARMS"):
    assert name in NS, ("slice A missing", name)
assert NS["K"] == 5 and NS["WIN"] == 6000
FLOOR = 1.0 / NS["K"]
assert FLOOR == 0.2
print(f"slice A ok sha {sha_a} | K={NS['K']} FLOOR={FLOOR}")

# ---- partition RE-DERIVED, never quoted -----------------------------------
l157 = json.load(open("l157/static.json"))
l162 = json.load(open("l162/static.json"))
add3 = json.load(open("l162/addendum3.json"))
CARRIER = [c for c in NS["POOLS"] if l157["pooled"][c]["wilson_lb"] >= 0.5]
CONTROL = [c for c in NS["POOLS"] if l157["pooled"][c]["below"] <= 6]
assert len(CARRIER) == 8 and len(CONTROL) == 9
assert not set(CARRIER) & set(CONTROL)
assert CARRIER == l162["carrier"] and CONTROL == l162["control"]
assert CARRIER == add3["carrier"] and CONTROL == add3["control"]
CP = [(CARRIER[i], CARRIER[j]) for i in range(8) for j in range(i + 1, 8)]
NP_ = [(CONTROL[i], CONTROL[j]) for i in range(9) for j in range(i + 1, 9)]
assert len(CP) == 28 and len(NP_) == 36
# unrounded Wilson bar provenance
wl = {c: l157["pooled"][c]["wilson_lb"] for c in NS["POOLS"]}
margin_in = min(wl[c] for c in CARRIER) - 0.5
print(f"partition re-derived: 8 carrier / 9 control; tightest carrier "
      f"wilson_lb margin above the unrounded .5 bar = {margin_in:.6f}")

# ---- stacks from the stored npz -------------------------------------------
S_SEG = {}
seeds = {}
for f in NS["FILES"]:
    z = np.load(f)
    ss = sorted(int(k.split("_")[-1]) for k in z.files
                if k.startswith("mm_b65_"))
    seeds[f] = ss
    assert len(ss) == 18, (f, len(ss))
    for a in NS["ARMS"][f]:
        for ch in NS["CHANNELS"]:
            S_SEG[(f, a, ch)] = np.array(
                [NS["seg_vec"](z[f"{ch}_{a}_{s}"][:NS["WIN"]].astype(np.float64))
                 for s in ss])
    del z
NS["S_SEG"] = S_SEG
exec(compile(SLICE_B, f"{SRC}[206:218]", "exec"), NS)
pair_read, clears = NS["pair_read"], NS["clears"]
print(f"slice B ok sha {sha_b} | stacks built {len(S_SEG)}")

# ---- C0A-166 part 1: 64 pooled msc_matched_med values ---------------------
checks = {}
pooled_med = {}
for label, pairs in (("carrier", CP), ("control", NP_)):
    for pa, pb in pairs:
        mats = []
        for f in NS["FILES"]:
            M = NS["msc_matrix"](S_SEG[(f, "b65", pa)], S_SEG[(f, "b65", pb)])
            mats.append(np.diag(M))
        mm = float(np.median(np.concatenate(mats)))
        pooled_med[f"{label}|{pa}~{pb}"] = mm
        ref = l162["i1_pooled"][f"{label}|{pa}~{pb}"]["msc_matched_med"]
        checks[f"pooled|{label}|{pa}~{pb}"] = (mm == ref)

# ---- C0A-166 part 2: per-file i1 rows used by addendum 3 ------------------
per_file = {}
for f in NS["FILES"]:
    cv = []
    for pa, pb in CP:
        mm_med = pair_read(f, "b65", pa, pb)[0]
        ref = l162["i1"][f"carrier|{f}|b65"][f"{pa}~{pb}"]["msc_matched_med"]
        checks[f"i1|carrier|{f}|{pa}~{pb}"] = (mm_med == ref)
        cv.append(mm_med)
    nv = []
    for pa, pb in NP_:
        mm_med = pair_read(f, "b65", pa, pb)[0]
        ref = l162["i1"][f"control|{f}|b65"][f"{pa}~{pb}"]["msc_matched_med"]
        checks[f"i1|control|{f}|{pa}~{pb}"] = (mm_med == ref)
        nv.append(mm_med)
    per_file[f] = dict(n_clear_f=int(sum(v >= 0.5 for v in cv)),
                       n_clear_f_control=int(sum(v >= 0.5 for v in nv)),
                       med_carrier=float(np.median(cv)),
                       med_control=float(np.median(nv)))

# ---- C0A-166 part 3: the six ADDENDUM-3 F-axis aggregates -----------------
car_vals = [pooled_med[f"carrier|{a}~{b}"] for a, b in CP]
ctl_vals = [pooled_med[f"control|{a}~{b}"] for a, b in NP_]
agg = dict(n_clear_f=int(sum(v >= 0.5 for v in car_vals)),
           n_clear_f_control=int(sum(v >= 0.5 for v in ctl_vals)),
           med_carrier=float(np.median(car_vals)),
           med_control=float(np.median(ctl_vals)))
fa = add3["f_axis"]
for k in ("n_clear_f", "n_clear_f_control", "med_carrier", "med_control"):
    checks[f"add3|{k}"] = (agg[k] == fa[k])
for f in NS["FILES"]:
    for k in ("n_clear_f", "n_clear_f_control", "med_carrier", "med_control"):
        checks[f"add3|{f}|{k}"] = (per_file[f][k] == fa["per_file"][f][k])

n_fail = sum(1 for v in checks.values() if not v)
print(f"\nC0A-166: {len(checks)} checks, {n_fail} FAIL")
if n_fail:
    for k, v in checks.items():
        if not v:
            print("  FAIL", k)
json.dump(dict(card="C0A-166 halting anchor for L166",
               slice_sha=dict(a=sha_a, b=sha_b),
               carrier=CARRIER, control=CONTROL, floor=FLOOR,
               carrier_wilson_margin=margin_in,
               n_checks=len(checks), n_fail=n_fail,
               stored_pooled=agg, stored_per_file=per_file,
               seeds={f: seeds[f] for f in NS["FILES"]},
               mtimes={p: os.path.getmtime(p)
                       for p in NS["FILES"] + ["l157/static.json",
                                               "l162/static.json",
                                               "l162/addendum3.json"]}),
          open("l166/anchor.json", "w"), indent=1)
assert n_fail == 0, "C0A-166 FAIL — STOP before any held-out read"
print("C0A-166 PASS (float equality, not rounded) — held-out reads admissible")
print(f"  stored pooled: {agg['n_clear_f']}/28 carrier vs "
      f"{agg['n_clear_f_control']}/36 control, med "
      f"{agg['med_carrier']:.4f} vs {agg['med_control']:.4f}")
for f in NS["FILES"]:
    v = per_file[f]
    print(f"  stored {f}: {v['n_clear_f']}/28 (ctl {v['n_clear_f_control']}/36)"
          f" med {v['med_carrier']:.4f} vs {v['med_control']:.4f}")
