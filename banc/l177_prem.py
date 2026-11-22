"""L177(a): the beta dependence ALREADY STORED in l65's stage-2 scan.

Read-only pre-measurement. No rollouts, no RNG, no graph build.
L44 rule: the card says "beta ... was never laddered"; l65_banc_oppoint.py
line 28 pins BETAS = [0.5, 1.0, 2.0, 4.0] and stores 36 scan rows per sign
arm (4 beta x 3 g-ratio x 3 d) at SCAN_WIN 800 (8 s), SCAN_SEEDS [11,22].
So the ladder EXISTS coarsely; this script derives its shape so the L177
PREREG registers predictions against measured numbers, not a sentence.

Caveats carried into the PREREG (what this scan is NOT):
  - g is a RATIO grid (0.7/1.0/1.4 x gstar), never re-bisected per beta,
    so af is free to move with beta -> cannot separate "inhibition helps"
    from "the op point moved" (L139 gain-family lesson).
  - 8 s window, 2 seeds, S from the scan's own readability filter.
  - the frozen (g,beta,d) was SELECTED on this table, so the winning rung
    is selection-biased by construction.
"""
import json
import numpy as np

S = json.load(open("l65/scan_l65.json"))
R = json.load(open("l65/results_l65.json"))
out = {"source": "l65/scan_l65.json + results_l65.json", "arms": {}}

print("=" * 72)
print("L177(a) stored beta ladder — l65 stage-2 scan (8 s, seeds 11/22)")
print("=" * 72)

for arm in ["A", "B"]:
    sc = S["arms"][arm]["scan"]
    fz = R["arms"][arm]["frozen"]
    gstar = S["arms"][arm]["gstar"]
    betas = sorted({r["beta"] for r in sc})
    ds = sorted({r["d"] for r in sc})
    gs = sorted({round(r["g"], 6) for r in sc})
    print(f"\n### arm {arm}  (gstar {gstar:.6f}; n rows {len(sc)}; "
          f"betas {betas}; d {ds}; g {['%.5f' % g for g in gs]})")
    print(f"    frozen: g={fz['g']:.6f} beta={fz['beta']} d={fz['d']} "
          f"af={fz['af']:.4f} meanS={fz['mean_S']} "
          f"S={{Ti:{fz['S']['Ti']}, Tr:{fz['S']['Tr']}}}")
    arec = {"gstar": gstar, "frozen": fz, "rows": [], "by_beta": {}}

    print(f"\n    {'beta':>5} {'g/gstar':>8} {'d':>5} | {'af':>7} "
          f"{'S_Ti':>8} {'S_Tr':>8} {'rhythm_f':>9} {'readable':>9}")
    for b in betas:
        for r in sorted([x for x in sc if x["beta"] == b],
                        key=lambda x: (x["d"], x["g"])):
            sti, str_ = r["S"]["Ti"], r["S"]["Tr"]
            arec["rows"].append(dict(beta=b, g=r["g"], gratio=r["g"] / gstar,
                                     d=r["d"], af=r["af"], S_Ti=sti,
                                     S_Tr=str_, rhythm_f=r["rhythm_f"],
                                     readable=r["readable"]))
            print(f"    {b:>5} {r['g']/gstar:>8.2f} {r['d']:>5} | "
                  f"{r['af']:>7.4f} "
                  f"{(('%+.3f' % sti) if sti == sti else '   nan'):>8} "
                  f"{(('%+.3f' % str_) if str_ == str_ else '   nan'):>8} "
                  f"{r['rhythm_f']:>9.3f} {str(r['readable']):>9}")

    # per-beta marginals (max and median over the 9 (g,d) cells)
    print(f"\n    --- marginal over the 9 (g,d) cells per beta ---")
    print(f"    {'beta':>5} | {'maxS_Ti':>8} {'medS_Ti':>8} | {'maxS_Tr':>8} "
          f"{'medS_Tr':>8} | {'af_min':>7} {'af_med':>7} {'af_max':>7} "
          f"{'n_nan_Ti':>8}")
    for b in betas:
        rb = [x for x in arec["rows"] if x["beta"] == b]
        ti = np.array([x["S_Ti"] for x in rb], float)
        tr = np.array([x["S_Tr"] for x in rb], float)
        af = np.array([x["af"] for x in rb], float)
        fin_ti, fin_tr = ti[np.isfinite(ti)], tr[np.isfinite(tr)]
        rec = dict(
            n=len(rb),
            maxS_Ti=float(np.max(fin_ti)) if fin_ti.size else None,
            medS_Ti=float(np.median(fin_ti)) if fin_ti.size else None,
            maxS_Tr=float(np.max(fin_tr)) if fin_tr.size else None,
            medS_Tr=float(np.median(fin_tr)) if fin_tr.size else None,
            af_min=float(af.min()), af_med=float(np.median(af)),
            af_max=float(af.max()),
            n_nan_Ti=int(np.sum(~np.isfinite(ti))),
            n_nan_Tr=int(np.sum(~np.isfinite(tr))))
        arec["by_beta"][str(b)] = rec
        f = lambda v: ("%+.3f" % v) if v is not None else "    nan"
        print(f"    {b:>5} | {f(rec['maxS_Ti']):>8} {f(rec['medS_Ti']):>8} | "
              f"{f(rec['maxS_Tr']):>8} {f(rec['medS_Tr']):>8} | "
              f"{rec['af_min']:>7.4f} {rec['af_med']:>7.4f} "
              f"{rec['af_max']:>7.4f} {rec['n_nan_Ti']:>8}")

    # matched-cell ladders: hold (g_ratio, d) fixed, walk beta
    print(f"\n    --- PAIRED cells: S_Ti vs beta at fixed (g/gstar, d) ---")
    shapes = {}
    for gr in sorted({round(x["gratio"], 3) for x in arec["rows"]}):
        for d in ds:
            cells = [x for x in arec["rows"]
                     if round(x["gratio"], 3) == gr and x["d"] == d]
            cells.sort(key=lambda x: x["beta"])
            if len(cells) != len(betas):
                continue
            v = [x["S_Ti"] for x in cells]
            vs = ["%+.3f" % t if t == t else "  nan" for t in v]
            fin = [t for t in v if t == t]
            shape = "all-nan"
            if len(fin) == len(v):
                inc = all(v[i + 1] >= v[i] for i in range(len(v) - 1))
                dec = all(v[i + 1] <= v[i] for i in range(len(v) - 1))
                am = int(np.argmax(v))
                shape = ("monotone-up" if inc else "monotone-down" if dec
                         else ("interior-max@beta=%s" % betas[am] if 0 < am <
                               len(v) - 1 else "non-monotone-edge-max"))
            print(f"      g/gstar {gr:.2f} d {d:<5} : "
                  + "  ".join(f"b{b}={s}" for b, s in zip(betas, vs))
                  + f"   [{shape}]")
            shapes[f"gr{gr}_d{d}"] = shape
    arec["ti_shapes"] = shapes
    out["arms"][arm] = arec

# headline: which prediction would the STORED table carry?
print("\n" + "=" * 72)
print("SHAPE CENSUS over paired (g,d) cells, S_Ti, arm B (the shipped arm):")
cnt = {}
for k, v in out["arms"]["B"]["ti_shapes"].items():
    cnt[v] = cnt.get(v, 0) + 1
print("   ", cnt)
print("arm A:", {k: v for k, v in
                 sorted({s: list(out['arms']['A']['ti_shapes'].values()).count(s)
                         for s in set(out['arms']['A']['ti_shapes'].values())}.items())})
out["shape_census_B_Ti"] = cnt
json.dump(out, open("l177/static_prem.json", "w"), indent=1)
print("\nwrote l177/static_prem.json")
