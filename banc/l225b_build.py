"""l225b_build.py — generate l225b_static.py as a literal PREFIX of
l225_static.py (lines 1-1735: the parent with its runtime stamp and its
WRITER cut) plus l225b_tail.py.

The prefix is asserted to contain ZERO writes, which is what makes it
impossible for the addendum to touch the parent's artifact; every parent
gate (premise 0a, CERT-213, CERT-GRP, CERT-FAST, CERT-SEED, CERT-207,
CERT-T, CERT-178) therefore re-runs as free certification.
"""
import ast
import hashlib
import pathlib

PAR = pathlib.Path("l225_static.py")
TAIL = pathlib.Path("l225b_tail.py")
OUT = pathlib.Path("l225b_static.py")
CUT = 1735

SHA_PAR = "43dbee573ba67c62"      # recorded by l225_build.py

par = PAR.read_text()
sha_par = hashlib.sha256(par.encode()).hexdigest()
assert sha_par[:16] == SHA_PAR, (sha_par[:16], SHA_PAR, "PARENT MOVED (STOP)")

lines = par.splitlines(keepends=True)
assert len(lines) >= CUT, (len(lines), CUT)
pre = "".join(lines[:CUT])
assert par.startswith(pre), "prefix is not a literal prefix (STOP)"

# the CUT lands immediately after the parent's limitations list and BEFORE
# its runtime stamp / makedirs / writer
assert lines[CUT - 1].rstrip() == "]", ("cut line", repr(lines[CUT - 1]))
assert 'q["limitations"]' in pre, "prefix lost the limitations block"
assert 'q["headline"]' in pre, "prefix lost the headline"
assert 'q["runtime_s"]' not in pre, "prefix kept the parent's runtime stamp"
assert 'os.makedirs("l225"' not in pre, "prefix kept the parent's makedirs"
# ZERO writes in the prefix: the addendum CANNOT touch l225/static.json
assert pre.count("json.dump(") == 0, "prefix contains a write (STOP)"
assert pre.count('"w"') == 0 and pre.count("'w'") == 0, \
    "prefix contains a write mode (STOP)"
for _need in ("CERT-213", "CERT-GRP", "CERT-FAST", "CERT-SEED",
              "premise_0a_resolution_floor", "def bh_reject(",
              "Q225_1 = {}", "def type_mode(", "def type_medians("):
    assert _need in pre, ("prefix lost", _need)

tail = TAIL.read_text()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()
# the addendum must not re-transcribe anything certified
for _f in ("def bh_reject", "def type_medians", "def type_mode",
           "def perm_within", "def _leafcmp", "def _nleaves",
           "def build_sub", "def Rstat", "def pct_of"):
    assert _f not in tail, ("ADDENDUM re-transcribes", _f)
assert "import l1" not in tail and "import l2" not in tail
# exactly ONE write, to the ADDENDUM artifact
assert tail.count("json.dump(") == 1, ("addendum write count",
                                       tail.count("json.dump("))
assert tail.count('open("l225/addendum.json", "w")') == 1, \
    "the addendum write does not target l225/addendum.json"
assert 'l225/static.json", "w"' not in tail, "ADDENDUM writes the PARENT"
assert tail.count('"w"') == 1, ("addendum \"w\" count", tail.count('"w"'))
for _need in ("CERT-225", "POST-HOC", "parent_headline_is_wrong",
              "B_power_or_magnitude", "C_uncorrected_vs_corrected",
              "D_survivor_family", "E_what_l213_becomes", "def _wilson(",
              "method_laws"):
    assert _need in tail, ("ADDENDUM lost", _need)

body = pre + tail
OUT.write_text(body)
assert OUT.read_text() == body
assert body.startswith(pre) and body.endswith(tail)
ast.parse(body)
print(f"wrote {OUT} ({len(body.splitlines())} lines; prefix {CUT} lines)")
print(f"PARENT    sha256 {sha_par}")
print(f"PREFIX    sha256 {hashlib.sha256(pre.encode()).hexdigest()}")
print(f"TAIL      sha256 {sha_tail}")
print(f"GENERATED sha256 {hashlib.sha256(body.encode()).hexdigest()}")
