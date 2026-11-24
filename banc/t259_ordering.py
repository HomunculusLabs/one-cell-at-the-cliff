"""t259_ordering.py — POST-HOC, UNREGISTERED, DESCRIPTION ONLY.

Pure arithmetic on already-certified stored values. Reads
l228/static.json and l208/static.json READ-ONLY (size, mtime_ns fingerprinted
before and after) and writes l228/ordering.json ONLY. No branch, no bar, no
prediction, no RNG.

The question P4 asked on Ti only, asked on BOTH joints: does the depth-2
anatomical term recover the L/R ordering of the DYNAMIC level where the
depth-1 term gets it wrong (L208's dissociation)?  Resolution floor named
up front: with 2 joints a sign-pattern statistic has 4 outcomes, so the
smallest achievable one-sided probability under a coin-flip null is 1/4.
"""
import json
import os

FP = {}
for p in ("l228/static.json", "l208/static.json"):
    st = os.stat(p)
    FP[p] = (st.st_size, st.st_mtime_ns)

S = json.load(open("l228/static.json"))
A = json.load(open("l208/static.json"))["arms"]

# gates: this script may only read values the parent already certified
assert S["branch"] == "D2_RISES_EVERYWHERE", (S["branch"], "parent branch")
assert S["cert_l228"]["cert_215"] == 76, "parent CERT-215 count"
assert S["cert_l228"]["cert_d2"] == 86, "parent CERT-D2 count"
assert S["escape_fired"] is False, "parent escape"
NG = 4

JOINTS = ("Ti", "Tr")
rows = {}
for J in JOINTS:
    lvlL = A[f"B36|{J}|f4wA"]["lvlL"]
    lvlR = A[f"B36|{J}|f4wA"]["lvlR"]
    d1L = S["d1_parent_table"][f"{J}_L"]["f4wA"]["NET_gain"]
    d1R = S["d1_parent_table"][f"{J}_R"]["f4wA"]["NET_gain"]
    d2L = S["rows_d2"][f"{J}_L"]["f4wA"]["d2_gain"]
    d2R = S["rows_d2"][f"{J}_R"]["f4wA"]["d2_gain"]
    dyn = lvlL > lvlR
    rows[J] = dict(
        lvlL=lvlL, lvlR=lvlR, dyn_L_hotter=bool(dyn),
        d1_gain_L=d1L, d1_gain_R=d1R, d1_says_L_higher=bool(d1L > d1R),
        d2_gain_L=d2L, d2_gain_R=d2R, d2_says_L_higher=bool(d2L > d2R),
        d1_agrees=bool((d1L > d1R) == dyn),
        d2_agrees=bool((d2L > d2R) == dyn),
        d1_margin_rel=abs(d1L - d1R) / ((abs(d1L) + abs(d1R)) / 2),
        d2_margin_rel=abs(d2L - d2R) / ((abs(d2L) + abs(d2R)) / 2))
    NG += 2

n_d1 = sum(r["d1_agrees"] for r in rows.values())
n_d2 = sum(r["d2_agrees"] for r in rows.values())

# cross-check against the parent's own registered P4 (Ti leg) -- a stored
# field must agree with the derived one, never just the prose (L225's law)
p4 = S["predictions"]["P4"]
assert p4["scored"] is (rows["Ti"]["d2_agrees"]), "P4 vs derived Ti ordering"
assert p4["got"] == [rows["Ti"]["d2_gain_L"], rows["Ti"]["d2_gain_R"]], \
    "P4 stored pair vs derived pair"
NG += 2

out = dict(
    label=("POST-HOC, UNREGISTERED, DESCRIPTION ONLY. Pure arithmetic on "
           "certified stored values; no branch, no bar, no RNG."),
    question=("does the depth-2 anatomical term recover the L/R ordering of "
              "the dynamic level on BOTH joints, where depth-1 gets it "
              "wrong (L208's dissociation)?"),
    joints=rows,
    n_joints=len(JOINTS),
    depth1_orderings_correct=n_d1,
    depth2_orderings_correct=n_d2,
    resolution_floor=("with 2 joints a sign-pattern statistic has 4 "
                      "outcomes; the smallest one-sided coin-flip "
                      "probability is 1/4 = 0.25, so 2/2 is DESCRIPTION "
                      "and cannot be a p-value (L225)"),
    coinflip_p_two_of_two=0.25,
    note=("the depth-2 term is NEGATIVE on all four pool-sides, so 'higher "
          "d2' means LESS net two-hop inhibition; the ordering comparison is "
          "on the signed value, which is the quantity a linear expansion "
          "would feed forward"),
    gates_asserted=NG)
json.dump(out, open("l228/ordering.json", "w"), indent=1, default=float)

for p, fp in FP.items():
    st = os.stat(p)
    assert (st.st_size, st.st_mtime_ns) == fp, (p, "MUTATED (STOP)")

print(f"[gates] {NG} asserts GREEN; inputs unmutated")
for J in JOINTS:
    r = rows[J]
    print(f"[{J}] dyn L>R {r['dyn_L_hotter']} | d1 says {r['d1_says_L_higher']}"
          f" ({r['d1_gain_L']:+.4f} vs {r['d1_gain_R']:+.4f}) agrees "
          f"{r['d1_agrees']} | d2 says {r['d2_says_L_higher']} "
          f"({r['d2_gain_L']:+.4f} vs {r['d2_gain_R']:+.4f}) agrees "
          f"{r['d2_agrees']}")
print(f"[score] depth-1 {n_d1}/2 orderings correct, depth-2 {n_d2}/2 "
      f"(floor 1/4 = 0.25, DESCRIPTION)")
