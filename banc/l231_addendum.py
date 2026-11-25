"""l231_addendum.py — POST-HOC, DESCRIPTIVE, declared as such.

Reads l231/static.json READ-ONLY and does pure arithmetic on its stored rows.
No branch, no prediction, no new null. Writes l231/addendum.json ONLY.

Why it exists: the whole-graph native read showed A_v1 (+0.335930) and the
per-side CELL-COUNT asymmetry (-0.328800) nearly equal and OPPOSITE. That is
the signature of an identity: if the TOTAL per-side Perron mass is equal, then
A_cell = asym(M_L/n_L, M_R/n_R) = asym(n_R, n_L) = -A_n exactly. So the
count-free companion statistic A_tot = asym(M_L, M_R) is what separates "the
mode is left-heavy" from "the left hemisphere has fewer cells carrying the
same mass", and it is recoverable from the stored means without re-running
anything.
"""
import hashlib
import json
import os

PATH = "l231/static.json"
_fp = os.stat(PATH)
with open(PATH, "rb") as f:
    _raw = f.read()
SHA = hashlib.sha256(_raw).hexdigest()
P = json.loads(_raw.decode())
ROWS = P["rows"]


def asym(a, b):
    t = a + b
    return (a - b) / t if t else None


OUT = {"source": PATH, "source_sha256": SHA,
       "source_size": _fp.st_size,
       "status": "POST-HOC DESCRIPTION — pure arithmetic on l231/static.json "
                 "stored rows. No branch, no prediction, no new null.",
       "identity": "if asym(M_L, M_R) == 0 then A_v1 == -A_n exactly; "
                   "A_tot = asym(M_L, M_R) is therefore the count-free form "
                   "of the same measurement, and (A_v1 + A_n) is the residual "
                   "of the equal-total-mass hypothesis.",
       "rows": {}}

for k, r in sorted(ROWS.items()):
    ML = r["mean_L"] * r["n_L"]
    MR = r["mean_R"] * r["n_R"]
    A_tot = asym(ML, MR)
    OUT["rows"][k] = dict(
        arm=r["arm"], unit=r["unit"], leg=r["leg"],
        n_L=r["n_L"], n_R=r["n_R"], A_n=r["A_n"],
        A_v1=r["A_v1"], A_tot=A_tot,
        resid_equal_mass=r["A_v1"] + r["A_n"],
        bh_sig=r["bh_sig"], p_two=r["p_two"])

PRIM = "f4wA|beta"
WG = "whole|beta"
print("=" * 100)
print(f"{'unit':40s} {'n_L':>6s} {'n_R':>6s} {'A_n':>8s} {'A_v1':>9s} "
      f"{'A_tot':>9s} {'A_v1+A_n':>9s} sig")
for aname in (PRIM, WG):
    print(f"--- arm {aname} " + "-" * 60)
    for k in sorted(ROWS):
        if ROWS[k]["arm"] != aname:
            continue
        r = OUT["rows"][k]
        print(f"{r['unit']:40s} {r['n_L']:6d} {r['n_R']:6d} {r['A_n']:+8.4f} "
              f"{r['A_v1']:+9.5f} {r['A_tot']:+9.5f} "
              f"{r['resid_equal_mass']:+9.5f} {'*' if r['bh_sig'] else ''}")

# how much of A_v1 does the equal-total-mass identity account for, per arm?
SUM = {}
for aname in sorted(set(r["arm"] for r in ROWS.values())):
    ks = [k for k in ROWS if ROWS[k]["arm"] == aname]
    num = sum(abs(OUT["rows"][k]["resid_equal_mass"]) for k in ks)
    den = sum(abs(OUT["rows"][k]["A_v1"]) for k in ks)
    tots = [abs(OUT["rows"][k]["A_tot"]) for k in ks]
    SUM[aname] = dict(n_units=len(ks),
                      mean_abs_A_v1=den / len(ks),
                      mean_abs_resid=num / len(ks),
                      mean_abs_A_tot=sum(tots) / len(ks),
                      share_unexplained_by_count=num / den if den else None)
    print(f"[arm {aname:12s}] mean|A_v1| {SUM[aname]['mean_abs_A_v1']:.5f} "
          f"mean|A_v1+A_n| {SUM[aname]['mean_abs_resid']:.5f} "
          f"mean|A_tot| {SUM[aname]['mean_abs_A_tot']:.5f} "
          f"unexplained-by-count share "
          f"{SUM[aname]['share_unexplained_by_count']:.4f}")
OUT["per_arm"] = SUM

_fp2 = os.stat(PATH)
assert (_fp2.st_size, _fp2.st_mtime_ns) == (_fp.st_size, _fp.st_mtime_ns), \
    "l231/static.json MOVED during the addendum (STOP)"
json.dump(OUT, open("l231/addendum.json", "w"), indent=1)
print(f"[addendum] wrote l231/addendum.json; source sha256 {SHA[:16]} "
      f"unchanged")
