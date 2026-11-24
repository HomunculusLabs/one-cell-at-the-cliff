"""Build l226b_static.py = a literal PREFIX of l226_static.py + my addendum.

The prefix is cut IMMEDIATELY BEFORE the parent's writer (line 504), so:
 - every parent gate (CERT-FLO 40, CERT-RHO 100, CERT-BH 8, CERT-SGN 3,
   CERT-Q1 6, the premise block and all fingerprint asserts) re-runs FREE,
 - the prefix is asserted to contain ZERO writes, so the addendum cannot
   touch l226/static.json even by accident.

Declared POST-HOC: the addendum has no registered branch, bar or
prediction. PREREG l226/PREREG.md is unamended.
"""
import ast
import hashlib
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PAR = HERE / "l226_static.py"
TAIL = HERE / "l226b_tail.py"
OUT = HERE / "l226b_static.py"

PAR_SHA_EXPECTED = "1f8f06d50823740a"          # printed by l226_build_verdict

par = PAR.read_text()
par_sha = hashlib.sha256(par.encode()).hexdigest()
assert par_sha.startswith(PAR_SHA_EXPECTED), ("parent sha drift", par_sha[:16])
plines = par.splitlines(keepends=True)
assert len(plines) == 506, ("parent line count drift", len(plines))

CUT = 503                                       # keep lines 1..503
pre = "".join(plines[:CUT])
assert pre in par and par.startswith(pre), "prefix is not a literal prefix"
assert plines[CUT].startswith('with open("l226/static.json", "w")'), \
    ("cut must land immediately before the writer", plines[CUT])
assert pre.rstrip().endswith(
    'print("\\nall npz + prior-json fingerprints unchanged (incl. l226 raw)")'), \
    "prefix last statement drift"

# ---- the prefix must contain NO writes at all ----
for tok in ('json.dump', 'savez', 'write_text', 'os.replace', '"w")',
            "'w')", '"a")', 'to_csv'):
    assert tok not in pre, ("prefix contains a WRITE (STOP)", tok)
_t = ast.parse(pre)
for _n in ast.walk(_t):
    if isinstance(_n, ast.Call) and isinstance(_n.func, ast.Name) \
            and _n.func.id == "open":
        _modes = [a for a in _n.args[1:]] + [k.value for k in _n.keywords
                                             if k.arg == "mode"]
        for _m in _modes:
            assert isinstance(_m, ast.Constant) and _m.value == "r", \
                ("prefix opens a file for writing", ast.dump(_m))
print(f"prefix = l226_static.py lines 1-{CUT} VERBATIM, ZERO writes "
      f"(AST-verified open() modes)")

tail = TAIL.read_text()
assert tail.count("json.dump") == 1 and "l226/addendum.json" in tail
assert "l226/static.json" in tail, "addendum must gate on the parent"
assert 'open("l226/static.json", "w")' not in tail, "addendum writes parent!"
# no inherited atom re-transcribed
for tok in ("def flo_side", "def spearman", "def duty_seeds", "def s_arrays",
            "def side_k", "def S_of", "def bh(", "def sign_agree"):
    assert tok not in tail, ("addendum RE-TRANSCRIBES an inherited atom", tok)
# L175: AST import gate (never a bare substring — it fires on prose)
import re as _re
_lab = _re.compile(r"^l\d|^banc")
for _n in ast.walk(ast.parse(tail)):
    if isinstance(_n, ast.Import):
        for _al in _n.names:
            assert not _lab.match(_al.name), ("lab import", _al.name)
    elif isinstance(_n, ast.ImportFrom):
        assert not (_n.module and _lab.match(_n.module)), ("lab import",
                                                           _n.module)
print("addendum audit: 1 write (addendum.json), 0 re-transcriptions, "
      "no lab import")

gen = pre + tail
ast.parse(gen)
assert gen.count("json.dump") == 1, "generated write-count drift"
assert 'open("l226/static.json", "w")' not in gen
OUT.write_text(gen)
print("wrote", OUT, OUT.stat().st_size, "bytes; sha",
      hashlib.sha256(OUT.read_bytes()).hexdigest()[:16],
      len(gen.splitlines()), "lines; parent sha", par_sha[:16])
