"""l221b_build.py — generate l221b_static.py = the L221 parent SLICED TO CUT
its writer, plus the post-hoc addendum tail (the L213 pattern).

Pieces:
  PARENT  = l221_static.py lines 1 .. (the line ending the leg-(a) block)
            VERBATIM. That is the parent's own banner + its nine verbatim
            source slices + its measurement body through leg (a), so every
            parent gate (CERT-F4 / CERT-178 / CERT-NULL / CERT-REW / CERT-SI /
            CERT-MENU / CERT-FH / CERT-211 / CERT-SIGEN / CERT-D5 /
            CERT-CROFTS / CERT-FHE / CERT-DAG) re-runs for free.
  TAIL    = l221b_tail.py (the addendum body)

The slice is asserted to contain NO registered-verdict block and NO json.dump
of the parent dict, so running it cannot rewrite l221/static.json (L175: a
lab run script is a SCRIPT, never a library). The parent file's md5 is
recorded here and re-verified by the caller AFTER the addendum run.
"""
import hashlib
import pathlib

PARENT = pathlib.Path("l221_static.py")
TAIL_SRC = pathlib.Path("l221b_tail.py")
TAIL_PARENT = pathlib.Path("l221_tail.py")
OUT = pathlib.Path("l221b_static.py")

ptxt = PARENT.read_text()
plines = ptxt.splitlines(keepends=True)
ttxt = TAIL_PARENT.read_text()
tlines = ttxt.splitlines(keepends=True)

# ---- locate the cut in the PARENT TAIL, then map it into the generated file
# the slice must end with the leg-(a) log, i.e. the line BEFORE leg (b).
cut_t = [i for i, ln in enumerate(tlines)
         if ln.startswith("# ---------------- leg (b): the used set")]
assert len(cut_t) == 1, ("leg (b) header not unique in l221_tail.py", cut_t)
tail_keep = "".join(tlines[:cut_t[0]])
assert tail_keep.rstrip().endswith('f"weight ranks {_rank_of_used}")'), \
    "the kept parent-tail slice does not end at the leg-(a) log"
# the generated parent = banner + heads + tail, so the kept prefix of the
# GENERATED file is everything up to the same point.
pos = ptxt.find(tail_keep)
assert pos > 0 and ptxt.count(tail_keep) == 1, "tail prefix not unique in parent"
keep = ptxt[:pos + len(tail_keep)]
n_keep = len(keep.splitlines())
assert keep in ptxt and ptxt.startswith(keep), "slice is not a literal prefix"

# ---- NEGATIVE audit: no parent verdict, prediction or writer may survive ----
for bad in ('o["L221_primary"]', 'o["predictions"]', 'o["predictions_score"]',
            'o["certification"]', 'o["limitations"]', 'o["pins"]',
            'o["Q221_b_target_reach"]', "json.dump", "L221 DONE",
            'o["certification"]["fingerprints_unchanged"]'):
    assert bad not in keep, f"the slice reaches into L221's writer ({bad!r})"
# ---- POSITIVE audit: every gate and every object the addendum needs --------
for need in ("CERT-SI", "CERT-MENU", "CERT-FH", "CERT-211", "CERT-SIGEN",
             "CERT-D5", "CERT-CROFTS", "CERT-FHE", "CERT-DAG",
             "def dijkstra_fe", "def feasible_mask", "NULL_FE.append",
             'o["Q221_a_weight_skew"]', 'o["Q221_0a_costs_vs_edges"]',
             'o["Q221_pool_geometry_control"]', "FP221", "_rho_w_used",
             "_rho_t_used", "_rho_l_used", "_used = np.array", "_w = np.array",
             "CB0, CB1 = START[LC_CAR], END[LC_CAR]"):
    assert need in keep, f"the slice lost {need!r}"

tail = TAIL_SRC.read_text()
for fn in ("def dijkstra_fe", "def feasible_mask", "def realised_set",
           "def build_si_index", "def _pct", "def _spear("):
    assert fn not in tail, f"addendum re-transcribes {fn!r} (L85 violation)"
for need in ("def _avg_rank", "CERT-MONO", "A_rank_identity",
             "B_edge_vs_cost_null"):
    assert need in tail, f"addendum lost {need!r}"
assert tail.count('json.dump(o221B, open("l221/addendum.json", "w"), indent=1)') == 1
assert 'json.dump(o,' not in tail, "addendum must not rewrite the parent dict"

body = keep + tail
OUT.write_text(body)
assert OUT.read_text() == body
assert body.startswith(keep) and tail in body
sha_parent = hashlib.sha256(ptxt.encode()).hexdigest()
sha_keep = hashlib.sha256(keep.encode()).hexdigest()
md5_parent = hashlib.md5(ptxt.encode()).hexdigest()
print(f"wrote {OUT} ({len(body.splitlines())} lines; parent slice {n_keep} "
      f"lines of {len(plines)})")
print(f"PARENT       sha256 {sha_parent}  md5 {md5_parent}")
print(f"PARENT SLICE sha256 {sha_keep}")
print(f"ADDENDUM TAIL sha256 {hashlib.sha256(tail.encode()).hexdigest()}")
print(f"GENERATED    sha256 {hashlib.sha256(body.encode()).hexdigest()}")
