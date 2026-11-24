"""l213_build.py — generate l213_static.py from SEVEN pieces, six of which are
VERBATIM SOURCE SLICES of already-certified scripts (L85: never re-transcribe
certified machinery; L175: a lab run script is a SCRIPT, never a library, so
slices are concatenated as SOURCE, never imported).

  CERT-HEAD1 = l151_static.py lines 1-319   (data load, pools, dn flags, pins)
  CERT-HEAD2 = l178_tail.py   lines 7-149   (CERT-F4, gains, f4wA build, CSR)
  MID        = l206_mid.py                  (csr_rows/csr_cols bridge only)
  CERT-HEAD3 = l206_tail.py   lines 22-121  (CERT-178 HALTING + reach/power_iter)
  CERT-HEAD4 = l207_tail.py   lines 48-112  (build_sub / reach_sub /
                                             power_iter_sub -- the generic
                                             substrate machinery)
  CERT-HEAD5 = l207_tail.py   lines 199-241 (Rstat / pct_of / rankvec /
                                             spearman_l -- THE statistic;
                                             cut BEFORE L207's own LAD loop,
                                             which needs L207's ladder state)
  TAIL       = l213_tail.py                 (L213 body)

Every inherited sha256 is asserted against the value the previous card
recorded, so a moved source HALTS the build instead of certifying a different
head (the L211 rule).
"""
import hashlib
import pathlib

H1_SRC = pathlib.Path("l151_static.py")
H2_SRC = pathlib.Path("l178_tail.py")
MID_SRC = pathlib.Path("l206_mid.py")
H3_SRC = pathlib.Path("l206_tail.py")
H45_SRC = pathlib.Path("l207_tail.py")
TAIL_SRC = pathlib.Path("l213_tail.py")
OUT = pathlib.Path("l213_static.py")

FORBIDDEN = ('"w"', "'w'", "import l1", "import l9", "savez", "to_csv",
             "json.dump")

# shas recorded by L210/L211 for the inherited heads (a moved source halts)
SHA_H1 = "e6245e8306dc8a0f"
SHA_H2 = "6e2e8fa4bd19eced"
SHA_MID = "febbc390ad4f"
SHA_H3_22_121 = None   # L207's own head3; recorded below for L214+


def slice_lines(path, a, b):
    """lines a..b inclusive, 1-indexed, asserted a literal substring."""
    txt = path.read_text()
    lines = txt.splitlines(keepends=True)
    assert len(lines) >= b, (path, len(lines), b, "source too short")
    s = "".join(lines[a - 1:b])
    assert s in txt, (path, a, b, "slice is not a literal substring")
    if a == 1:
        assert txt.startswith(s), "head slice is not a prefix"
    for bad in FORBIDDEN:
        assert bad not in s, f"{path} [{a},{b}] contains forbidden {bad!r}"
    return s, hashlib.sha256(s.encode()).hexdigest()


h1, sha1 = slice_lines(H1_SRC, 1, 319)
h2, sha2 = slice_lines(H2_SRC, 7, 149)
h3, sha3 = slice_lines(H3_SRC, 22, 121)
h4, sha4 = slice_lines(H45_SRC, 48, 112)
h5, sha5 = slice_lines(H45_SRC, 199, 241)
mid = MID_SRC.read_text()
tail = TAIL_SRC.read_text()
sha_mid = hashlib.sha256(mid.encode()).hexdigest()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()

# ---- INHERITED sha gate: a moved source halts the build --------------------
assert sha1[:16] == SHA_H1, (sha1[:16], SHA_H1, "CERT-HEAD1 MOVED (STOP)")
assert sha2[:16] == SHA_H2, (sha2[:16], SHA_H2, "CERT-HEAD2 MOVED (STOP)")
assert sha_mid[:12] == SHA_MID, (sha_mid[:12], SHA_MID, "MID MOVED (STOP)")

# ---- boundary anchors: a source edit cannot silently shift what we certify --
assert h1.splitlines()[0].startswith('"""'), "H1 first line"
assert "dn_proj = dn_proj & dn_all" in h1, "H1 lost the dn_proj flag"
assert "dn_into = dn_into & dn_all" in h1, "H1 lost the dn_into flag"
assert "keep_wA = keep_new.copy()" in h1, "H1 lost keep_wA"
assert h2.splitlines()[0] == "import math", ("H2 first line", h2.splitlines()[0])
assert h2.splitlines()[-1].strip() == "I_vec[dng_l] = DRIVE_D", "H2 last line"
assert h2.splitlines()[15].strip() == "FLOOR = 4", ("H2 FLOOR", h2.splitlines()[15])
assert "CERT-F4" in h2 and "keep_f4 = keep_new.copy()" in h2
assert h3.splitlines()[0] == 'S178 = json.load(open("l178/static.json"))', \
    ("H3 first line", h3.splitlines()[0])
assert "CERT-178" in h3 and "def power_iter" in h3 and "def reach" in h3
assert 'assert pa == st[f"P{d}abs"]' in h3, "H3 lost the CERT-178 assert"
assert "LAM1, V1, LAMINFO = power_iter(jv_abs_an)" in h3, "H3 lost lam1"
assert "crofts" not in h3.lower()
# H4: the generic substrate machinery, all three functions, nothing else
assert h4.splitlines()[0].startswith("# ---------------- the GENERIC"), \
    ("H4 first line", h4.splitlines()[0])
for _f in ("def build_sub(", "def reach_sub(", "def power_iter_sub("):
    assert _f in h4, ("H4 lost", _f)
assert "CERT-GEN" not in h4, "H4 overran into the CERT-GEN block"
assert 'assert len(pl[pk]) == want' in h4, "H4 lost the pool-size assert"
assert "EXPRESSION-IDENTICAL" in h4, "H4 lost the reach_sub expression note"
# H5: the statistic + percentile helpers, stopping before Q1a
assert h5.splitlines()[0].startswith("# ---------------- the statistic"), \
    ("H5 first line", h5.splitlines()[0])
for _f in ("def Rstat(", "def pct_of(", "def rankvec(", "def spearman_l("):
    assert _f in h5, ("H5 lost", _f)
assert "Q1 = {}" not in h5, "H5 overran into the Q1 block"
assert "LAD = {}" not in h5, "H5 overran into L207's ladder loop"
assert h5.splitlines()[-1].strip().startswith("return float(num / (da * db))"), \
    ("H5 last line", h5.splitlines()[-1])
assert "l207_tail.py   lines 199-241" in __doc__, "docstring/slice drift"
assert "R=(p2 / (lam1 ** 2 * m))" in h5, "H5 lost the R expression"
assert "STRICTLY SMALLER" in h5, "H5 lost the pct_of convention"
# the tail must NOT re-transcribe certified machinery
for _f in ("def build_sub", "def reach_sub", "def power_iter_sub",
           "def Rstat", "def pct_of"):
    assert _f not in tail, ("TAIL re-transcribes certified", _f)
assert "import l1" not in tail and "import l2" not in tail, "TAIL imports a lab module"
assert 'json.dump(o' in tail and 'l213/static.json' in tail
assert "l207/static.json" in tail and "mtime_ns" in tail, \
    "TAIL lost the read-only fingerprint of l207/static.json"

banner = (
    '"""GENERATED by l213_build.py — do not edit by hand.\n'
    f"CERT-HEAD1 = l151_static.py lines 1-319 VERBATIM (sha256 {sha1[:16]}).\n"
    f"CERT-HEAD2 = l178_tail.py lines 7-149 VERBATIM (sha256 {sha2[:16]}).\n"
    f"MID        = l206_mid.py (sha256 {sha_mid[:16]}).\n"
    f"CERT-HEAD3 = l206_tail.py lines 22-121 VERBATIM (sha256 {sha3[:16]}).\n"
    f"CERT-HEAD4 = l207_tail.py lines 48-112 VERBATIM (sha256 {sha4[:16]}).\n"
    f"CERT-HEAD5 = l207_tail.py lines 199-253 VERBATIM (sha256 {sha5[:16]}).\n"
    f"TAIL       = l213_tail.py (sha256 {sha_tail[:16]}).\n"
    'PREREG l213/PREREG.md. Writes l213/static.json ONLY.\n'
    '"""\n')

body = banner + h1 + h2 + mid + h3 + h4 + h5 + tail
OUT.write_text(body)
assert OUT.read_text() == body
for part in (h1, h2, mid, h3, h4, h5, tail):
    assert part in body, "generated file lost a slice"
print(f"wrote {OUT} ({len(body.splitlines())} lines)")
print(f"CERT-HEAD1 sha256 {sha1}")
print(f"CERT-HEAD2 sha256 {sha2}")
print(f"MID        sha256 {sha_mid}")
print(f"CERT-HEAD3 sha256 {sha3}")
print(f"CERT-HEAD4 sha256 {sha4}")
print(f"CERT-HEAD5 sha256 {sha5}")
print(f"TAIL       sha256 {sha_tail}")
print(f"GENERATED  sha256 {hashlib.sha256(body.encode()).hexdigest()}")
