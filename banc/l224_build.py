"""l224_build.py — generate l224_static.py from EIGHT pieces, seven of which are
VERBATIM SOURCE SLICES of already-certified scripts (L85: never re-transcribe
certified machinery; L175: a lab run script is a SCRIPT, never a library, so
slices are concatenated as SOURCE, never imported).

  CERT-HEAD1 = l151_static.py lines 1-319   (data load, pools, dn flags, pins)
  CERT-HEAD2 = l178_tail.py   lines 7-149   (CERT-F4, gains, f4wA build, CSR)
  MID        = l206_mid.py                  (csr_rows/csr_cols bridge only)
  CERT-HEAD3 = l206_tail.py   lines 22-121  (CERT-178 HALTING + reach/power_iter)
  CERT-HEAD4 = l207_tail.py   lines 48-112  (build_sub/reach_sub/power_iter_sub)
  CERT-HEAD5 = l207_tail.py   lines 199-241 (Rstat/pct_of/rankvec/spearman_l)
  CERT-HEAD6 = l213_tail.py   lines 1-430   (L213's WHOLE pipeline: population,
                                             strata, Q1/Q2/Q3 -- with its
                                             runtime stamp and its WRITER cut,
                                             the L213 slicing pattern)
  TAIL       = l224_tail.py                 (L224 body)

Every inherited sha256 that a previous card recorded is asserted here, so a
moved source HALTS the build instead of certifying a different head (L211).

PARENT PIN: l213_tail.py is asserted to be a literal SUFFIX of l213_static.py
and every head slice a literal substring of it, in order -- which is what
proves CERT-HEAD6 is the code that ACTUALLY produced l213/static.json rather
than a file with the right name (the tick-254 pin shape).
"""
import hashlib
import pathlib

H1_SRC = pathlib.Path("l151_static.py")
H2_SRC = pathlib.Path("l178_tail.py")
MID_SRC = pathlib.Path("l206_mid.py")
H3_SRC = pathlib.Path("l206_tail.py")
H45_SRC = pathlib.Path("l207_tail.py")
H6_SRC = pathlib.Path("l213_tail.py")
TAIL_SRC = pathlib.Path("l224_tail.py")
PARENT = pathlib.Path("l213_static.py")
OUT = pathlib.Path("l224_static.py")

FORBIDDEN = ('"w"', "'w'", "import l1", "import l9", "savez", "to_csv",
             "json.dump")

# shas recorded by L210/L211/L213 for the inherited heads (a moved source halts)
SHA_H1 = "e6245e8306dc8a0f"
SHA_H2 = "6e2e8fa4bd19eced"
SHA_MID = "febbc390ad4f"


def slice_lines(path, a, b, audit=True):
    """lines a..b inclusive, 1-indexed, asserted a literal substring."""
    txt = path.read_text()
    lines = txt.splitlines(keepends=True)
    assert len(lines) >= b, (path, len(lines), b, "source too short")
    s = "".join(lines[a - 1:b])
    assert s in txt, (path, a, b, "slice is not a literal substring")
    if a == 1:
        assert txt.startswith(s), "head slice is not a prefix"
    if audit:
        for bad in FORBIDDEN:
            assert bad not in s, f"{path} [{a},{b}] contains forbidden {bad!r}"
    return s, hashlib.sha256(s.encode()).hexdigest()


h1, sha1 = slice_lines(H1_SRC, 1, 319)
h2, sha2 = slice_lines(H2_SRC, 7, 149)
h3, sha3 = slice_lines(H3_SRC, 22, 121)
h4, sha4 = slice_lines(H45_SRC, 48, 112)
h5, sha5 = slice_lines(H45_SRC, 199, 241)
h6, sha6 = slice_lines(H6_SRC, 1, 430)
mid = MID_SRC.read_text()
tail = TAIL_SRC.read_text()
sha_mid = hashlib.sha256(mid.encode()).hexdigest()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()
h6_full = H6_SRC.read_text()

# ---- INHERITED sha gate -----------------------------------------------------
assert sha1[:16] == SHA_H1, (sha1[:16], SHA_H1, "CERT-HEAD1 MOVED (STOP)")
assert sha2[:16] == SHA_H2, (sha2[:16], SHA_H2, "CERT-HEAD2 MOVED (STOP)")
assert sha_mid[:12] == SHA_MID, (sha_mid[:12], SHA_MID, "MID MOVED (STOP)")

# ---- boundary anchors (same as L213's, so a source edit cannot shift us) ----
assert h1.splitlines()[0].startswith('"""'), "H1 first line"
assert "dn_proj = dn_proj & dn_all" in h1, "H1 lost the dn_proj flag"
assert "dn_into = dn_into & dn_all" in h1, "H1 lost the dn_into flag"
assert "keep_wA = keep_new.copy()" in h1, "H1 lost keep_wA"
assert h2.splitlines()[0] == "import math", ("H2 first line",)
assert h2.splitlines()[-1].strip() == "I_vec[dng_l] = DRIVE_D", "H2 last line"
assert h2.splitlines()[15].strip() == "FLOOR = 4", ("H2 FLOOR",)
assert "CERT-F4" in h2 and "keep_f4 = keep_new.copy()" in h2
assert h3.splitlines()[0] == 'S178 = json.load(open("l178/static.json"))', \
    ("H3 first line", h3.splitlines()[0])
assert "CERT-178" in h3 and "def power_iter" in h3 and "def reach" in h3
assert 'assert pa == st[f"P{d}abs"]' in h3, "H3 lost the CERT-178 assert"
assert "LAM1, V1, LAMINFO = power_iter(jv_abs_an)" in h3, "H3 lost lam1"
assert h4.splitlines()[0].startswith("# ---------------- the GENERIC"), \
    ("H4 first line",)
for _f in ("def build_sub(", "def reach_sub(", "def power_iter_sub("):
    assert _f in h4, ("H4 lost", _f)
assert "CERT-GEN" not in h4, "H4 overran into the CERT-GEN block"
assert h5.splitlines()[0].startswith("# ---------------- the statistic"), \
    ("H5 first line",)
for _f in ("def Rstat(", "def pct_of(", "def rankvec(", "def spearman_l("):
    assert _f in h5, ("H5 lost", _f)
assert "Q1 = {}" not in h5 and "LAD = {}" not in h5, "H5 overran"
assert "R=(p2 / (lam1 ** 2 * m))" in h5, "H5 lost the R expression"
assert "STRICTLY SMALLER" in h5, "H5 lost the pct_of convention"

# ---- H6: L213's whole pipeline, writer CUT ---------------------------------
assert h6.splitlines()[0].startswith("# ================= L213 TAIL"), \
    ("H6 first line", h6.splitlines()[0])
assert h6.splitlines()[-1].strip() == "]", ("H6 last line", h6.splitlines()[-1])
for _need in ('POP[_k] = dict(gis=_gis, R=_R,', "o[\"population\"]",
              "o[\"cert_207\"]", "o[\"cert_T\"]", "def strata_of(",
              "def perm_within(", "o[\"Q1_type\"]", "o[\"Q2_class\"]",
              "o[\"Q3_conditional\"]", "o[\"predictions\"]",
              "o[\"limitations\"]"):
    assert _need in h6, ("H6 lost", _need)
# the CUT is what makes this card safe: no runtime stamp, no writer
assert 'o["runtime_s"]' not in h6, "H6 kept L213's runtime stamp (STOP)"
assert "l213/static.json\", \"w\"" not in h6, "H6 kept L213's writer (STOP)"
assert 'os.makedirs("l213"' not in h6, "H6 kept L213's makedirs (STOP)"
assert "l207/static.json" in h6 and "mtime_ns" in h6, \
    "H6 lost the read-only fingerprint of l207/static.json"

# ---- PARENT PIN: H6 is the code that produced l213/static.json -------------
par = PARENT.read_text()
assert par.endswith(h6_full), "l213_tail.py is NOT a suffix of l213_static.py"
for _nm, _s in (("H1", h1), ("H2", h2), ("MID", mid), ("H3", h3),
                ("H4", h4), ("H5", h5)):
    assert _s in par, ("parent lost slice", _nm)
_pos = 0
for _nm, _s in (("H1", h1), ("H2", h2), ("MID", mid), ("H3", h3),
                ("H4", h4), ("H5", h5), ("H6full", h6_full)):
    _i = par.find(_s, _pos)
    assert _i >= 0, ("parent slice out of order", _nm)
    _pos = _i + len(_s)
assert _pos == len(par), "parent has trailing bytes after the tail"
sha_par = hashlib.sha256(par.encode()).hexdigest()

# ---- the tail must NOT re-transcribe certified machinery -------------------
NO_RETRANSCRIBE = ("def build_sub", "def reach_sub", "def power_iter_sub",
                   "def Rstat", "def pct_of", "def rankvec", "def spearman_l",
                   "def census", "def _atv", "def strata_of",
                   "def perm_within", "def power_iter", "def reach")
for _f in NO_RETRANSCRIBE:
    assert _f not in tail, ("TAIL re-transcribes certified", _f)
assert "import l1" not in tail and "import l2" not in tail, \
    "TAIL imports a lab module"
# ---- write audit: exactly THREE writes, every one to l224 ------------------
assert tail.count('json.dump(') == 3, ("tail write count", tail.count('json.dump('))
assert tail.count('json.dump(q') == 3, "a tail write does not dump q"
assert tail.count('"w"') == 3, ("tail \"w\" count", tail.count('"w"'))
assert tail.count('open("l224/static.json", "w")') == 3, \
    "a tail write does not target l224/static.json"
assert "l213/static.json\", \"w\"" not in tail and \
    'os.makedirs("l213"' not in tail, "TAIL writes to the PARENT (STOP)"
assert tail.count('os.makedirs("l224"') == 3, "makedirs/write mismatch"
for _need in ("CERT-213", "CERT-ADD", "CERT-RANK", "CERT-K1", "CERT-FAST",
              "CERT-OLS", "CERT-RMA", "Q0_spurious_baseline", "Q1_exponent",
              "Q2_residual", "Q3_transport", "K_DEGENERATE", "raise SystemExit"):
    assert _need in tail, ("TAIL lost", _need)

banner = (
    '"""GENERATED by l224_build.py — do not edit by hand.\n'
    f"CERT-HEAD1 = l151_static.py lines 1-319 VERBATIM (sha256 {sha1[:16]}).\n"
    f"CERT-HEAD2 = l178_tail.py lines 7-149 VERBATIM (sha256 {sha2[:16]}).\n"
    f"MID        = l206_mid.py (sha256 {sha_mid[:16]}).\n"
    f"CERT-HEAD3 = l206_tail.py lines 22-121 VERBATIM (sha256 {sha3[:16]}).\n"
    f"CERT-HEAD4 = l207_tail.py lines 48-112 VERBATIM (sha256 {sha4[:16]}).\n"
    f"CERT-HEAD5 = l207_tail.py lines 199-241 VERBATIM (sha256 {sha5[:16]}).\n"
    f"CERT-HEAD6 = l213_tail.py lines 1-430 VERBATIM (sha256 {sha6[:16]}) --\n"
    f"             L213's whole pipeline, runtime stamp + writer CUT.\n"
    f"PARENT PIN  = l213_static.py sha256 {sha_par[:16]}; l213_tail.py is its\n"
    f"             literal SUFFIX and every head slice a substring, in order.\n"
    f"TAIL       = l224_tail.py (sha256 {sha_tail[:16]}).\n"
    'PREREG l224/PREREG.md. Writes l224/static.json ONLY.\n'
    '"""\n')

body = banner + h1 + h2 + mid + h3 + h4 + h5 + h6 + tail
OUT.write_text(body)
assert OUT.read_text() == body
for part in (h1, h2, mid, h3, h4, h5, h6, tail):
    assert part in body, "generated file lost a slice"
import ast
ast.parse(body)
print(f"wrote {OUT} ({len(body.splitlines())} lines)")
print(f"CERT-HEAD1 sha256 {sha1}")
print(f"CERT-HEAD2 sha256 {sha2}")
print(f"MID        sha256 {sha_mid}")
print(f"CERT-HEAD3 sha256 {sha3}")
print(f"CERT-HEAD4 sha256 {sha4}")
print(f"CERT-HEAD5 sha256 {sha5}")
print(f"CERT-HEAD6 sha256 {sha6}")
print(f"PARENT     sha256 {sha_par}")
print(f"TAIL       sha256 {sha_tail}")
print(f"GENERATED  sha256 {hashlib.sha256(body.encode()).hexdigest()}")
