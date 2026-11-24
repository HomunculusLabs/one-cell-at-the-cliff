"""Build l226_static.py from VERBATIM source slices + my tail.

PREREG l226/PREREG.md. ZERO new rollouts in this script (the batch was
produced by l226_run.py).

Slice 1 = l169b2_verdict.py lines 13-63 byte-for-byte (the certified
  s_arrays/duty_seeds/side_k atom; sha asserted against the value
  l208_build_add.py / l214_build.py recorded).
Slice 2 = l208_add_tail.py lines 55-72 byte-for-byte (flo_side + spearman
  = the floor currency itself).
Slice 3 = l214_tail.py lines 1-95 byte-for-byte — the FROZEN DECISION
  RULE: its constants, the measurement window, and its two reproduction
  gates (CERT-FLO 40 + CERT-RHO 100), which therefore re-run FREE before
  any B38 number can be read. The card's Verify line demands the rule be
  "re-executed as a verbatim source slice, not re-implemented"; this is
  that, structurally.

PARENT PIN: l214_tail.py is asserted to be a literal SUFFIX of
l214_static.py, which is what proves slice 3 is the code that ACTUALLY
produced l214/static.json rather than a file with the right name.

Nothing is imported (L175: a lab *_verdict.py / run script is a SCRIPT;
importing it re-executes it and rewrites its own artifacts).
"""
import ast
import hashlib
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC1 = HERE / "l169b2_verdict.py"
SRC2 = HERE / "l208_add_tail.py"
SRC3 = HERE / "l214_tail.py"
PAR3 = HERE / "l214_static.py"
TAIL = HERE / "l226_tail.py"
OUT = HERE / "l226_static.py"

HEAD_SHA_EXPECTED = (
    "de636f4a18ee789b8bd51fca5f7823ea6302ffd58be630b50c70965e865b8e0c")
SLICE2_SHA_EXPECTED = (
    "595f869b450e2d25eefdc89193dfbdba5d988276738434b02d8f4d930b6dad0e")

t1 = SRC1.read_text()
s1 = "".join(t1.splitlines(keepends=True)[12:63])          # lines 13..63
assert s1 in t1, "slice 1 is NOT a literal slice (STOP)"
assert s1.startswith("WIN, DT = 6000, 0.01\n"), "slice 1 first line drift"
h1 = hashlib.sha256(s1.encode()).hexdigest()
assert h1 == HEAD_SHA_EXPECTED, ("slice 1 sha DRIFT vs l208/l214 record", h1)
assert "def duty_seeds" in s1 and "def s_arrays" in s1 and "def side_k" in s1

t2 = SRC2.read_text()
s2 = "".join(t2.splitlines(keepends=True)[54:72])          # lines 55..72
assert s2 in t2, "slice 2 is NOT a literal slice (STOP)"
assert s2.startswith("def flo_side(raw, arm, seed, pk, mask):\n")
h2 = hashlib.sha256(s2.encode()).hexdigest()
assert h2 == SLICE2_SHA_EXPECTED, ("slice 2 sha DRIFT", h2)
assert "def spearman" in s2, "slice 2 lost spearman"

t3 = SRC3.read_text()
s3 = "".join(t3.splitlines(keepends=True)[0:95])           # lines 1..95
assert s3 in t3, "slice 3 is NOT a literal slice (STOP)"
assert s3.startswith("# ===================== L214 TAIL — the FLOOR currency")
assert s3.rstrip().endswith(
    'print("GATES PASSED — reading L214 numbers now\\n")'), \
    "slice 3 last line drift — the cut must land exactly at L214's gate exit"
h3 = hashlib.sha256(s3.encode()).hexdigest()
# slice 3 must carry the WHOLE frozen rule and BOTH reproduction gates,
# and must NOT carry any of L214's own verdict machinery or its writer.
for tok in ("N_PERM = 20000", "PERM_SEED = 20837", "PAIR_SEED = 51423",
            "ALPHA = 0.05", "QFDR = 0.10", "CERT-FLO", "CERT-RHO",
            'ARMS5 = ["f4wA", "f4ng", "f4tw", "cutwA", "cutng25"]',
            'PAIRS2 = ["Ti", "Tr"]'):
    assert tok in s3, ("slice 3 lost a frozen-rule element", tok)
for tok in ("json.dump", "l214/static.json", 'OUT = {', "F_REPLICATES",
            "H_TIE", "ACCOUNTED", "predictions"):
    assert tok not in s3, ("slice 3 carries L214 verdict machinery", tok)
assert s3.count("savez") == 0 and s3.count('"w")') == 0

# ---- PARENT PIN: slice 3's whole file is a literal SUFFIX of l214_static.py
par3 = PAR3.read_text()
assert par3.endswith(t3), ("l214_tail.py is NOT a suffix of l214_static.py "
                           "(the frozen rule's provenance is unproven) STOP")
par3_sha = hashlib.sha256(par3.encode()).hexdigest()
# and the two atoms are literal substrings of that same parent, in order
_i1, _i2 = par3.index(s1), par3.index(s2)
assert 0 < _i1 < _i2 < par3.index(t3), "parent slice order broken (STOP)"
print("PARENT PIN GREEN: l214_tail.py is a literal SUFFIX of l214_static.py "
      f"(sha {par3_sha[:16]}), slices 1/2 literal substrings in order")

print("SLICE1 sha256", h1[:16], "lines", len(s1.splitlines()))
print("SLICE2 sha256", h2[:16], "lines", len(s2.splitlines()))
print("SLICE3 sha256", h3[:16], "lines", len(s3.splitlines()))

FORBIDDEN = ("savez", "json.dump", "write_text", "os.replace", "to_csv",
             "pickle")
for nm, sl in (("slice1", s1), ("slice2", s2), ("slice3", s3)):
    for tok in FORBIDDEN:
        assert tok not in sl, ("forbidden token in " + nm, tok)
print("forbidden-token audit on all three slices: clean")

tail = TAIL.read_text()
# L175 gate, STRUCTURAL not textual: a bare substring scan for "from l2"
# fires on the tail's own PROSE (a comment citing l214_tail.py line numbers)
# — the tick-248/256/257/this-tick bare-token trap. Ask the AST instead.
_lab = __import__("re").compile(r"^l\d|^banc")
for _n in ast.walk(ast.parse(tail)):
    if isinstance(_n, ast.Import):
        for _al in _n.names:
            assert not _lab.match(_al.name), ("tail imports a lab module",
                                              _al.name)
    elif isinstance(_n, ast.ImportFrom):
        assert not (_n.module and _lab.match(_n.module)), \
            ("tail imports from a lab module", _n.module)
print("tail import audit (AST): no lab module imported (L175)")
assert tail.count("json.dump") == 1 and "l226/static.json" in tail, \
    "tail write-count drift"
assert 'open("l226/static.json", "w")' in tail
# the tail must not re-transcribe an inherited function body
NO_RETRANSCRIBE = ("def flo_side", "def spearman", "def duty_seeds",
                   "def s_arrays", "def side_k", "def S_of")
for tok in NO_RETRANSCRIBE:
    assert tok not in tail, ("tail RE-TRANSCRIBES an inherited atom", tok)
# every re-implemented piece must be gated by a reproduction assert
for tok in ("CERT-BH", "CERT-SGN", "CERT-Q1", "CERT-SUBSET"):
    assert tok in tail, ("tail lost a gate", tok)
print("tail audit: clean (no lab import, 1 write, 0 re-transcriptions, "
      "4 gates present)")

preamble = (
    '"""L226 static (GENERATED by l226_build_verdict.py — do not hand-edit).'
    "\n\nSlice 1 = l169b2_verdict.py lines 13-63 BYTE-FOR-BYTE (sha256 "
    + h1[:16] + ").\nSlice 2 = l208_add_tail.py lines 55-72 BYTE-FOR-BYTE "
    "(sha256 " + h2[:16] + ").\nSlice 3 = l214_tail.py lines 1-95 "
    "BYTE-FOR-BYTE (sha256 " + h3[:16] + ") = THE FROZEN RULE,\n  a literal "
    "SUFFIX-slice of l214_static.py (sha256 " + par3_sha[:16] + ").\n"
    "Tail = l226_tail.py. PREREG l226/PREREG.md.\n"
    '"""\n'
    "import json\n"
    "import math\n"
    "import os\n"
    "\n"
    "import numpy as np\n"
    "\n"
    'HEAD_SHA = "' + h1 + '"\n'
    'SLICE2_SHA = "' + h2 + '"\n'
    'SLICE3_SHA = "' + h3 + '"\n'
    'L214_STATIC_SHA = "' + par3_sha + '"\n'
    "\n"
)
gen = preamble + s1 + "\n\n" + s2 + "\n\n" + s3 + "\n\n" + tail
ast.parse(gen)
assert gen.count("json.dump") == 1, "generated script write-count drift"
assert gen.count("l226/static.json") == 2
OUT.write_text(gen)
print("wrote", OUT, OUT.stat().st_size, "bytes; generated sha",
      hashlib.sha256(OUT.read_bytes()).hexdigest()[:16],
      len(gen.splitlines()), "lines")
