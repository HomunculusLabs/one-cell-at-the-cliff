"""(b3) DIAGNOSTIC: per-cell band-floor fractions (the run printed only the range,
and the male substrate is the FIRST in the lineage with a nonzero band floor).
No verdict depends on this file; it names WHICH cells the published band eats."""
import json, os, numpy as np, comp
exec(open("comp_b3.py").read().split("# ================= B3-CERT")[0].replace(
     'import comp  # certified stage-(a) component code', 'pass'))
out = {}
TS_SAVE = comp.TSQ
for si, (a0, b0, _f) in enumerate(SEGB):
    q = (TS >= a0 + MEAS0) & (TS < b0)
    comp.TSQ = TS[q]
    for arm in ARMS:
        for s in SEEDS:
            tr = tr_of(arm, s)
            for side, (fk, ek) in (("L", ("fL", "eL")), ("R", ("fR", "eR"))):
                for band in comp.BANDS:
                    c = comp.comp_windows(tr[fk], tr[ek], band)
                    out[f"{arm}|{s}|seg{si}|{side}|{band}"] = round(float(np.mean(c["floor"])), 4)
comp.TSQ = TS_SAVE
json.dump(out, open("results_l176b3_floor.json", "w"), indent=1)
nz = {k: v for k, v in out.items() if v > 0}
print("cells", len(out), "nonzero band-floor", len(nz))
for k, v in sorted(nz.items(), key=lambda kv: -kv[1])[:12]:
    print(f"  {k:34s} {v:.4f}")
import collections
print("by band:", {b: round(float(np.mean([v for k, v in out.items() if k.endswith(b)])), 4) for b in comp.BANDS})
print("by band nonzero count:", {b: sum(1 for k, v in out.items() if k.endswith(b) and v > 0) for b in comp.BANDS})
print("by arm (mean):", {a: round(float(np.mean([v for k, v in out.items() if k.startswith(a+'|')])), 4) for a in ARMS})
