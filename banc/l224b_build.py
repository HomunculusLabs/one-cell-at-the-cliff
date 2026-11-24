"""l224b_build.py — generate l224b_static.py as a literal PREFIX of
l224_static.py (lines 1-1428) + l224b_tail.py.

The cut lands immediately BEFORE the parent's registered K_DEGENERATE
short-circuit, so the prefix is asserted to contain ZERO writes: the
addendum cannot touch the parent's artifact.  Every parent gate re-runs for
free inside the prefix.
"""
import ast
import hashlib
import pathlib

PAR = pathlib.Path("l224_static.py")
TAIL = pathlib.Path("l224b_tail.py")
OUT = pathlib.Path("l224b_static.py")
CUT = 1427

par = PAR.read_text()
lines = par.splitlines(keepends=True)
pre = "".join(lines[:CUT])
assert par.startswith(pre), "prefix is not a literal prefix"
tail = TAIL.read_text()

# the prefix must contain ZERO writes
assert 'json.dump(' not in pre, "prefix contains a write (STOP)"
assert '"w"' not in pre and "'w'" not in pre, "prefix contains a write mode"
assert 'os.makedirs(' not in pre, "prefix contains a makedirs"
# and it must end exactly where the registered escape begins
assert pre.rstrip().endswith("for k, v in FIT.items()}"), \
    ("prefix last statement", pre.rstrip()[-60:])
assert "# escape SHORT-CIRCUITS (0f)" not in pre, "prefix overran the escape"
assert 'q["branch"] = "K_DEGENERATE"' not in pre, "prefix overran the branch"
# the parent's own gates must be inside the prefix
for need in ("CERT-213", "CERT-ADD", "CERT-RANK", "CERT-K1", "CERT-FAST",
             "FIT = {}", "def _rank_np", "def _spear_np",
             'q["fit_population"]'):
    assert need in pre, ("prefix lost", need)
# the addendum tail must not re-transcribe certified machinery
for f in ("def build_sub", "def reach_sub", "def power_iter_sub", "def Rstat",
          "def pct_of", "def rankvec", "def spearman_l", "def census",
          "def _atv", "def strata_of", "def perm_within", "def _rank_np",
          "def _spear_np", "def power_iter", "def reach"):
    assert f not in tail, ("TAIL re-transcribes certified", f)
assert "import l1" not in tail and "import l2" not in tail
# exactly ONE write, to the addendum artifact
assert tail.count('json.dump(') == 1 and tail.count('json.dump(b') == 1
assert tail.count('"w"') == 1
assert tail.count('open("l224/addendum.json", "w")') == 1
assert 'l224/static.json", "w"' not in tail, "TAIL writes the parent (STOP)"
assert "CERT-224" in tail and "CERT-ZK" in tail
assert 'b["registered"] = False' in tail, "addendum must declare unregistered"

body = pre + tail
OUT.write_text(body)
assert OUT.read_text() == body
ast.parse(body)
print(f"wrote {OUT} ({len(body.splitlines())} lines; prefix {CUT})")
print(f"PREFIX    sha256 {hashlib.sha256(pre.encode()).hexdigest()}")
print(f"PARENT    sha256 {hashlib.sha256(par.encode()).hexdigest()}")
print(f"TAIL      sha256 {hashlib.sha256(tail.encode()).hexdigest()}")
print(f"GENERATED sha256 {hashlib.sha256(body.encode()).hexdigest()}")
