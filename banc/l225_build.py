"""l225_build.py — generate l225_static.py from TEN pieces, NINE of which are
VERBATIM SOURCE SLICES of already-certified scripts (L85: never re-transcribe
certified machinery; L175: a lab run script is a SCRIPT, never a library, so
slices are concatenated as SOURCE, never imported).

  CERT-HEAD1 = l151_static.py lines 1-319   (data load, pools, dn flags, pins)
  CERT-HEAD2 = l178_tail.py   lines 7-149   (CERT-F4, gains, f4wA build, CSR)
  MID206     = l206_mid.py                  (csr_rows/csr_cols bridge only)
  CERT-HEAD3 = l206_tail.py   lines 22-121  (CERT-178 HALTING + reach/power_iter)
  CERT-HEAD4 = l207_tail.py   lines 48-112  (build_sub/reach_sub/power_iter_sub)
  CERT-HEAD5 = l207_tail.py   lines 199-241 (Rstat/pct_of/rankvec/spearman_l)
  CERT-HEAD6 = l213_tail.py   lines 1-430   (L213's WHOLE pipeline: population,
                                             strata, Q1/Q2/Q3 -- runtime stamp
                                             and WRITER cut)
  MID225     = l225_mid.py                  (3-line bridge: os, `q`, the clock)
  CERT-HEAD7 = l224_tail.py   lines 48-124  (L224's CERT-213 HALTING block with
                                             its coverage bar DERIVED FROM THE
                                             ARTIFACT -- re-EXECUTED, never
                                             re-implemented; the L211 rule)
  TAIL       = l225_tail.py                 (L225 body)

Every inherited sha256 a previous card recorded is asserted here, so a moved
source HALTS the build instead of certifying a different head (L211).

TWO PARENT PINS (both halting):
  (1) l213_tail.py is a literal SUFFIX of l213_static.py and every head slice
      a literal substring in order with no trailing bytes -- which proves
      CERT-HEAD6 is the code that ACTUALLY produced l213/static.json.
  (2) l224_tail.py is a literal SUFFIX of l224_static.py -- which proves
      CERT-HEAD7 (the CERT-213 gate) is the code that ACTUALLY ran in L224
      rather than a file with the right name (the tick-254 pin shape).
"""
import hashlib
import pathlib

H1_SRC = pathlib.Path("l151_static.py")
H2_SRC = pathlib.Path("l178_tail.py")
MID_SRC = pathlib.Path("l206_mid.py")
H3_SRC = pathlib.Path("l206_tail.py")
H45_SRC = pathlib.Path("l207_tail.py")
H6_SRC = pathlib.Path("l213_tail.py")
MID2_SRC = pathlib.Path("l225_mid.py")
H7_SRC = pathlib.Path("l224_tail.py")
PARENT = pathlib.Path("l213_static.py")
PARENT2 = pathlib.Path("l224_static.py")
TAIL_SRC = pathlib.Path("l225_tail.py")
OUT = pathlib.Path("l225_static.py")

FORBIDDEN = ('"w"', "'w'", "import l1", "import l9", "savez", "to_csv",
             "json.dump")

# shas recorded by L210/L211/L213/L224 for the inherited heads
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
h7, sha7 = slice_lines(H7_SRC, 48, 124)
mid = MID_SRC.read_text()
mid2 = MID2_SRC.read_text()
tail = TAIL_SRC.read_text()
sha_mid = hashlib.sha256(mid.encode()).hexdigest()
sha_mid2 = hashlib.sha256(mid2.encode()).hexdigest()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()
h6_full = H6_SRC.read_text()
h7_full = H7_SRC.read_text()

# ---- INHERITED sha gate -----------------------------------------------------
assert sha1[:16] == SHA_H1, (sha1[:16], SHA_H1, "CERT-HEAD1 MOVED (STOP)")
assert sha2[:16] == SHA_H2, (sha2[:16], SHA_H2, "CERT-HEAD2 MOVED (STOP)")
assert sha_mid[:12] == SHA_MID, (sha_mid[:12], SHA_MID, "MID MOVED (STOP)")

# ---- boundary anchors (L213/L224's, so a source edit cannot shift us) -------
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
for _need in ('POP[_k] = dict(gis=_gis, R=_R,', 'o["population"]',
              'o["cert_207"]', 'o["cert_T"]', "def strata_of(",
              "def perm_within(", 'o["Q1_type"]', 'o["Q2_class"]',
              'o["Q3_conditional"]', 'o["predictions"]', 'o["limitations"]'):
    assert _need in h6, ("H6 lost", _need)
assert 'o["runtime_s"]' not in h6, "H6 kept L213's runtime stamp (STOP)"
assert 'os.makedirs("l213"' not in h6, "H6 kept L213's makedirs (STOP)"
assert "l207/static.json" in h6 and "mtime_ns" in h6, \
    "H6 lost the read-only fingerprint of l207/static.json"

# ---- H7: L224's CERT-213 block, nothing more -------------------------------
assert h7.splitlines()[0].startswith("# ====="), ("H7 first line",)
for _need in ("CERT-213 (HALTING)", "def _leafcmp(", "def _nleaves(",
              "_want213 = sum(", "assert _n213 == _want213",
              'q["cert_213"]', "DERIVED FROM THE ARTIFACT ITSELF",
              'S213["branches"]["Q1"] == "T_TYPE_LOW"'):
    assert _need in h7, ("H7 lost", _need)
assert "_nadd = 0" not in h7 and "MM = {}" not in h7, \
    "H7 overran into L224's CERT-ADD block"  # the token 'CERT-ADD' itself
# appears in H7's own prose (premise 0a) -- gate on the BLOCK, never the
# bare token (the tick-248 trap, hit again here)
assert "def _rank_np(" not in h7 and "def _spur(" not in h7, "H7 overran"
assert "mtime_ns" in h7, "H7 lost the read-only fingerprint"

# ---- MID225: the bridge, and nothing but the bridge ------------------------
assert mid2.count("\n") <= 8, "MID225 is not a bridge"
assert "q = {}" in mid2 and "import os" in mid2 and "_T225" in mid2
assert "json" not in mid2 and "np." not in mid2, "MID225 does real work"

# ---- PARENT PIN 1: H6 is the code that produced l213/static.json -----------
par = PARENT.read_text()
assert par.endswith(h6_full), "l213_tail.py is NOT a suffix of l213_static.py"
_pos = 0
for _nm, _s in (("H1", h1), ("H2", h2), ("MID", mid), ("H3", h3),
                ("H4", h4), ("H5", h5), ("H6full", h6_full)):
    _i = par.find(_s, _pos)
    assert _i >= 0, ("parent slice out of order", _nm)
    _pos = _i + len(_s)
assert _pos == len(par), "parent has trailing bytes after the tail"
sha_par = hashlib.sha256(par.encode()).hexdigest()

# ---- PARENT PIN 2: H7 is the code that actually ran in L224 ----------------
par2 = PARENT2.read_text()
assert par2.endswith(h7_full), "l224_tail.py is NOT a suffix of l224_static.py"
assert h7 in par2, "the CERT-213 block is not in l224_static.py"
assert h6 in par2, "l224_static.py lost L213's pipeline slice"
sha_par2 = hashlib.sha256(par2.encode()).hexdigest()

# ---- the tail must NOT re-transcribe certified machinery -------------------
NO_RETRANSCRIBE = ("def build_sub", "def reach_sub", "def power_iter_sub",
                   "def Rstat", "def pct_of", "def rankvec", "def spearman_l",
                   "def census", "def _atv", "def strata_of",
                   "def perm_within", "def power_iter", "def reach",
                   "def _leafcmp", "def _nleaves")
for _f in NO_RETRANSCRIBE:
    assert _f not in tail, ("TAIL re-transcribes certified", _f)
assert "import l1" not in tail and "import l2" not in tail, \
    "TAIL imports a lab module"
# ---- write audit: exactly ONE write, and it targets l225 -------------------
assert tail.count("json.dump(") == 1, ("tail write count",
                                       tail.count("json.dump("))
assert tail.count("json.dump(q") == 1, "the tail write does not dump q"
assert tail.count('"w"') == 1, ("tail \"w\" count", tail.count('"w"'))
assert tail.count('open("l225/static.json", "w")') == 1, \
    "the tail write does not target l225/static.json"
assert 'l213/static.json", "w"' not in tail and \
    'os.makedirs("l213"' not in tail, "TAIL writes to the PARENT (STOP)"
assert tail.count('os.makedirs("l225"') == 1, "makedirs/write mismatch"
for _need in ("CERT-GRP", "CERT-FAST", "CERT-SEED", "premise_0a",
              "def bh_reject(", "F_UNIQUE", "F_SMALL_FAMILY", "F_COMMON",
              "F_DEGENERATE", "Q225_1_fdr", "Q225_2_annotation",
              "Q225_3_menu", "Kriegeskorte", "Benjamini", "Phipson"):
    assert _need in tail, ("TAIL lost", _need)

banner = (
    '"""GENERATED by l225_build.py — do not edit by hand.\n'
    f"CERT-HEAD1 = l151_static.py lines 1-319 VERBATIM (sha256 {sha1[:16]}).\n"
    f"CERT-HEAD2 = l178_tail.py lines 7-149 VERBATIM (sha256 {sha2[:16]}).\n"
    f"MID206     = l206_mid.py (sha256 {sha_mid[:16]}).\n"
    f"CERT-HEAD3 = l206_tail.py lines 22-121 VERBATIM (sha256 {sha3[:16]}).\n"
    f"CERT-HEAD4 = l207_tail.py lines 48-112 VERBATIM (sha256 {sha4[:16]}).\n"
    f"CERT-HEAD5 = l207_tail.py lines 199-241 VERBATIM (sha256 {sha5[:16]}).\n"
    f"CERT-HEAD6 = l213_tail.py lines 1-430 VERBATIM (sha256 {sha6[:16]}) --\n"
    f"             L213's whole pipeline, runtime stamp + writer CUT.\n"
    f"MID225     = l225_mid.py (sha256 {sha_mid2[:16]}).\n"
    f"CERT-HEAD7 = l224_tail.py lines 48-124 VERBATIM (sha256 {sha7[:16]}) --\n"
    f"             L224's CERT-213 HALTING block, artifact-derived coverage.\n"
    f"PARENT PIN1 = l213_static.py sha256 {sha_par[:16]} (l213_tail.py is its\n"
    f"             literal SUFFIX; every head slice a substring, in order).\n"
    f"PARENT PIN2 = l224_static.py sha256 {sha_par2[:16]} (l224_tail.py is its\n"
    f"             literal SUFFIX, so CERT-HEAD7 is the code that ran).\n"
    f"TAIL       = l225_tail.py (sha256 {sha_tail[:16]}).\n"
    'PREREG l225/PREREG.md. Writes l225/static.json ONLY.\n'
    '"""\n')

body = banner + h1 + h2 + mid + h3 + h4 + h5 + h6 + mid2 + h7 + tail
OUT.write_text(body)
assert OUT.read_text() == body
for part in (h1, h2, mid, h3, h4, h5, h6, mid2, h7, tail):
    assert part in body, "generated file lost a slice"
import ast
ast.parse(body)
print(f"wrote {OUT} ({len(body.splitlines())} lines)")
print(f"CERT-HEAD1 sha256 {sha1}")
print(f"CERT-HEAD2 sha256 {sha2}")
print(f"MID206     sha256 {sha_mid}")
print(f"CERT-HEAD3 sha256 {sha3}")
print(f"CERT-HEAD4 sha256 {sha4}")
print(f"CERT-HEAD5 sha256 {sha5}")
print(f"CERT-HEAD6 sha256 {sha6}")
print(f"MID225     sha256 {sha_mid2}")
print(f"CERT-HEAD7 sha256 {sha7}")
print(f"PARENT1    sha256 {sha_par}")
print(f"PARENT2    sha256 {sha_par2}")
print(f"TAIL       sha256 {sha_tail}")
print(f"GENERATED  sha256 {hashlib.sha256(body.encode()).hexdigest()}")
