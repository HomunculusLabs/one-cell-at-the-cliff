"""L166 held-out F-axis read. PREREG l166/PREREG.md registered FIRST;
C0A-166 (l166_cert.py, 204 checks EXACT) passed before this script may run.

Machinery is l162_static.py EXEC'd as a verbatim source slice (same slices and
sha as the anchor). Bars are the PREREG's, unrounded. Zero rollouts here.
"""
import hashlib
import json
import re

import numpy as np

SRC = "l162_static.py"
lines = open(SRC).read().split("\n")
SLICE_A = "\n".join(lines[0:106])
SLICE_B = "\n".join(lines[205:218])
sha_a = hashlib.sha256(SLICE_A.encode()).hexdigest()[:16]
sha_b = hashlib.sha256(SLICE_B.encode()).hexdigest()[:16]
anchor = json.load(open("l166/anchor.json"))
assert anchor["n_fail"] == 0 and anchor["slice_sha"] == {"a": sha_a, "b": sha_b}
run_a = json.load(open("l166/anchors_run.json"))
assert run_a["c0a_pass"], "C0A-166b bit-identity FAIL — held-out read barred"

NS = {}
exec(compile(SLICE_A, f"{SRC}[1:106]", "exec"), NS)
WIN, K = NS["WIN"], NS["K"]
FLOOR = 1.0 / K
POOLS_L = NS["POOLS"]
CARRIER, CONTROL = anchor["carrier"], anchor["control"]
CP = [(CARRIER[i], CARRIER[j]) for i in range(8) for j in range(i + 1, 8)]
NP_ = [(CONTROL[i], CONTROL[j]) for i in range(9) for j in range(i + 1, 9)]
assert len(CP) == 28 and len(NP_) == 36

# ---- held-out sources ------------------------------------------------------
B44 = list(range(4401, 4419))
SOURCES = []           # (tag, file, arm, seeds-or-None, strength)
SOURCES.append(("H1_fresh_b65_B44", "l166/raw_l166.npz", "b65", B44, "PRIMARY"))
SOURCES.append(("H2_l154_off", "l154/raw_l154.npz", "off", None, "WEAK"))
z150 = np.load("l150/raw_l150.npz")
arms150 = sorted({m.group(1) for m in
                  (re.match(r"^mm_(.+)_\d+$", k) for k in z150.files) if m})
H3 = [a for a in arms150 if a != "b65"]
for a in H3:
    SOURCES.append((f"H3_l150_{a}", "l150/raw_l150.npz", a, None, "FREE"))
del z150
print(f"held-out sources: {[s[0] for s in SOURCES]}")
assert any(s[0] == "H1_fresh_b65_B44" for s in SOURCES)


def stacks(path, arm, keep_seeds):
    z = np.load(path)
    ss = sorted(int(k.split("_")[-1]) for k in z.files
                if k.startswith(f"mm_{arm}_"))
    if keep_seeds is not None:
        ss = [s for s in ss if s in keep_seeds]
    out, ptp = {}, {}
    for ch in POOLS_L:
        xs = [z[f"{ch}_{arm}_{s}"][:WIN].astype(np.float64) for s in ss]
        out[ch] = np.array([NS["seg_vec"](x) for x in xs])
        ptp[ch] = float(np.median([np.ptp(x) for x in xs]))
    del z
    return out, ss, ptp


res = {}
for tag, path, arm, keep, strength in SOURCES:
    S, ss, ptp = stacks(path, arm, keep)
    assert len(ss) >= 16, (tag, len(ss))

    def med_of(pairs):
        vals = []
        for pa, pb in pairs:
            M = NS["msc_matrix"](S[pa], S[pb])
            vals.append(float(np.median(np.diag(M))))
        return vals

    cv, nv = med_of(CP), med_of(NP_)
    n_clear_f = int(sum(v >= 0.5 for v in cv))
    n_clear_f_ctl = int(sum(v >= 0.5 for v in nv))
    med_c, med_n = float(np.median(cv)), float(np.median(nv))
    bar_count = bool(n_clear_f >= 22)
    bar_ratio = bool(med_c >= 2.0 * med_n)
    bar_calib = bool(0.5 * FLOOR <= med_n <= 2.0 * FLOOR)
    cls = ("F1_carrier_coherent" if (bar_count and bar_ratio and bar_calib)
           else "F2_not_coherent" if n_clear_f <= 7 else "F3_mixed")
    failing = [n for n, b in (("count>=22", bar_count),
                              ("ratio>=2x", bar_ratio),
                              ("calibration", bar_calib)) if not b]
    res[tag] = dict(
        strength=strength, file=path, arm=arm, n_seeds=len(ss), seeds=ss,
        n_clear_f=n_clear_f, n_clear_f_control=n_clear_f_ctl,
        med_carrier=med_c, med_control=med_n,
        ratio=(med_c / med_n if med_n > 0 else float("inf")),
        bar_count=bar_count, bar_ratio=bar_ratio, bar_calibration=bar_calib,
        failing_bars=failing, cls=cls,
        inverted=bool(med_n > med_c),
        carrier_vals=cv, control_vals=nv,
        ptp_carrier_med=float(np.median([ptp[c] for c in CARRIER])),
        ptp_control_med=float(np.median([ptp[c] for c in CONTROL])))
    print(f"{tag:22s} [{strength:7s}] n={len(ss):2d} {cls:20s} "
          f"clears {n_clear_f:2d}/28 (ctl {n_clear_f_ctl:2d}/36) med "
          f"{med_c:.4f} vs {med_n:.4f} ratio {res[tag]['ratio']:5.2f} "
          f"| bars fail: {failing or 'none'} | ptp car "
          f"{res[tag]['ptp_carrier_med']:.4f}")

# ---- registered questions --------------------------------------------------
h1 = res["H1_fresh_b65_B44"]
q1 = bool(h1["cls"] == "F1_carrier_coherent" and h1["bar_count"]
          and h1["bar_calibration"])
h2 = res["H2_l154_off"]
q2 = bool(h2["cls"] == "F2_not_coherent")
h3tags = [t for t in res if t.startswith("H3_")]
h3_fail = [t for t in h3tags
           if (not res[t]["bar_ratio"]) or res[t]["inverted"]]
q3 = bool(len(h3_fail) >= 4)
branch = ("B_REBASED" if q1 else
          "B_LOST" if h1["n_clear_f"] <= 7 else "B_SHRUNK")

# stored per-file comparator (the right yardstick for one 18-seed batch)
stored_pf = anchor["stored_per_file"]
cmp_rows = {f: dict(n_clear_f=v["n_clear_f"], med_carrier=v["med_carrier"])
            for f, v in stored_pf.items()}

out = dict(card="L166 F-axis held-out re-basing",
           prereg="l166/PREREG.md", slice_sha=dict(a=sha_a, b=sha_b),
           floor_1_over_K=FLOOR, carrier=CARRIER, control=CONTROL,
           anchor_checks=anchor["n_checks"], anchor_fail=anchor["n_fail"],
           c0a_run=dict(max=run_a["c0a_max"], n=run_a["n_checks"],
                        af_range=[run_a["af_b44_min"], run_a["af_b44_max"]]),
           stored_per_file=cmp_rows, stored_pooled=anchor["stored_pooled"],
           held_out=res,
           questions=dict(Q1_primary_rebased=q1, Q2_off_is_F2=q2,
                          Q3_h3_nontransport=q3, Q3_failing_arms=h3_fail,
                          Q3_n_arms=len(h3tags)),
           branch=branch,
           fold_licensed=bool(q1),
           fold_qualifiers=["L164: phase-pinned protocol => drive-FOLLOWING "
                            "coherence, never an intrinsic clock",
                            "L165/Q3: carrier-pool vocabulary is b65-substrate "
                            "scoped" if q3 else "Q3 did not fire"])
json.dump(out, open("l166/results_l166.json", "w"), indent=1)

print(f"\nstored comparator per file: "
      + " | ".join(f"{f.split('/')[0]} {v['n_clear_f']}/28 "
                   f"med {v['med_carrier']:.4f}" for f, v in cmp_rows.items()))
print(f"\nQ1 (primary re-basing on fresh B44): {'PASS' if q1 else 'FAIL'} "
      f"-> {h1['n_clear_f']}/28, med {h1['med_carrier']:.4f} vs "
      f"{h1['med_control']:.4f}, calib {h1['bar_calibration']}")
print(f"Q2 (off arm lands F2): {'CORRECT' if q2 else 'WRONG'} -> {h2['cls']}, "
      f"{h2['n_clear_f']}/28 med {h2['med_carrier']:.4f}")
print(f"Q3 (H3 non-transport on >=4 of {len(h3tags)}): "
      f"{'CORRECT' if q3 else 'WRONG'} -> {len(h3_fail)} arms fail/invert "
      f"{h3_fail}")
print(f"BRANCH {branch} | draft fold licensed: {bool(q1)}")
print("l166/results_l166.json written")
