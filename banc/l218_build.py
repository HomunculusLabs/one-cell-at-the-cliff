"""l218_build.py — generate l218_static.py from SEVEN pieces, six of which are
VERBATIM SOURCE SLICES of already-certified scripts (L85: never re-transcribe
certified machinery; L175: a lab run script is a SCRIPT, never a library, so
slices are concatenated as source, never imported).

  CERT-HEAD1 = l151_static.py lines 1-319   (data load, pools, ladder, pins)
  CERT-HEAD2 = l178_tail.py   lines 7-149   (CERT-F4, gains, f4wA build, CSR)
  MID        = l206_mid.py                  (csr_rows/csr_cols bridge only)
  CERT-HEAD3 = l178_tail.py   lines 348-458 (CERT-REW + the 100 draws + map)
  CERT-HEAD4 = l206_tail.py   lines 22-263  (CERT-178's 420 values, lam1 by
                                             power iteration, the depth-1..10
                                             sweep + its float-equality
                                             self-check vs L178, the 100-draw
                                             null construction, CERT-NULL)
  CERT-210M  = l210_tail.py   lines 1-326   (CERT-206 HALTING, CERT-MV,
                                             CERT-LEFT, CERT-REBUILD HALTING,
                                             coeff/K, the 100 per-draw power
                                             iterations -> rows210, Q210-1/2/
                                             3/5 and the Hotelling gap) —
                                             SLICED to CUT l210's own
                                             predictions/writer block (L213:
                                             a successor build slices the
                                             parent tail at the end of its
                                             measurement block so every parent
                                             gate re-runs for free while the
                                             parent's json.dump is excluded by
                                             the forbidden-token audit)
  TAIL       = l218_tail.py                 (L218 body)

Every INHERITED sha256 is asserted against the value L210 RECORDED in its own
banner, so a moved or edited source HALTS this build instead of silently
certifying different code. The PARENT PIN additionally asserts that
l210_tail.py has not moved since it produced l210/static.json — otherwise the
CERT-210M slice would not be the code that produced the table CERT-218T
certifies against.
"""
import hashlib
import pathlib

H1_SRC = pathlib.Path("l151_static.py")
H2_SRC = pathlib.Path("l178_tail.py")
MID_SRC = pathlib.Path("l206_mid.py")
H4_SRC = pathlib.Path("l206_tail.py")
H5_SRC = pathlib.Path("l210_tail.py")
TAIL_SRC = pathlib.Path("l218_tail.py")
OUT = pathlib.Path("l218_static.py")

FORBIDDEN = ('"w"', "'w'", "import l1", "import l9", "savez", "to_csv",
             "json.dump")


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
h3, sha3 = slice_lines(H2_SRC, 348, 458)
h4, sha4 = slice_lines(H4_SRC, 22, 263)
m210, sha210m = slice_lines(H5_SRC, 1, 326)
mid = MID_SRC.read_text()
tail = TAIL_SRC.read_text()
sha_mid = hashlib.sha256(mid.encode()).hexdigest()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()
sha_l210_whole = hashlib.sha256(H5_SRC.read_bytes()).hexdigest()

# ---- INHERITED PINS: exactly the values L210 recorded in its own banner ----
INHERITED = {
    "CERT-HEAD1 l151_static.py 1-319": (sha1, "e6245e8306dc8a0f"),
    "CERT-HEAD2 l178_tail.py 7-149": (sha2, "6e2e8fa4bd19eced"),
    "MID l206_mid.py": (sha_mid, "febbc390ad4f1a02"),
    "CERT-HEAD3 l178_tail.py 348-458": (sha3, "5bb7b56e6b6487d5"),
    "CERT-HEAD4 l206_tail.py 22-263": (sha4, "772a2410e76516e5"),
}
for name, (got, want) in INHERITED.items():
    assert got[:16] == want, (name, got[:16], want,
                              "INHERITED sha MISMATCH -> source moved (STOP)")
print(f"[inherited] {len(INHERITED)} sha pins GREEN (L210's banner)")

# ---- PARENT PIN: l210_tail.py must still be the file that made l210/static --
_gen210 = pathlib.Path("l210_static.py").read_text()
assert f"TAIL       = l210_tail.py (sha256 {sha_l210_whole[:16]})" in _gen210, \
    (sha_l210_whole[:16], "l210_tail.py MOVED since l210_static.py was "
                          "generated -> the CERT-210M slice is not the code "
                          "that produced l210/static.json, so CERT-218T would "
                          "certify against a table this slice did not make "
                          "(STOP)")
print(f"[inherited] CERT-210M parent pin GREEN (l210_tail.py whole-file sha "
      f"{sha_l210_whole[:16]} == l210_static.py's recorded TAIL sha)")

# ---- boundary anchors: a source edit cannot silently shift what we certify --
assert h1.splitlines()[0].startswith('"""'), "H1 first line"
assert h2.splitlines()[0] == "import math", ("H2 first line", h2.splitlines()[0])
assert h2.splitlines()[-1].strip() == "I_vec[dng_l] = DRIVE_D", "H2 last line"
assert h2.splitlines()[15].strip() == "FLOOR = 4", ("H2 FLOOR", h2.splitlines()[15])
assert "CERT-F4" in h2 and "NL = int(keep_f4.sum())" in h2, "H2 lost NL"
assert "CERT-REW" in h3.splitlines()[0], "H3 first line"
assert h3.splitlines()[-1].strip().startswith("assert np.array_equal(_key_csr"), \
    ("H3 last line", h3.splitlines()[-1])
assert "cert_rew" in h3
assert h4.splitlines()[0] == 'S178 = json.load(open("l178/static.json"))', \
    ("H4 first line", h4.splitlines()[0])
assert h4.splitlines()[1] == "DMAX = 10", ("H4 DMAX", h4.splitlines()[1])
assert h4.splitlines()[-1].strip() == \
    'source="l178/static.json Q2b_null_anatomical")', \
    ("H4 last line", h4.splitlines()[-1])
for need in ("CERT-178", "CERT-NULL", "def power_iter", "def jmatvec",
             "def reach", "def sweep_actor", "null_changed.append",
             "LAM1, V1, LAMINFO = power_iter(jv_abs_an)",
             'assert pa == st[f"P{d}abs"]',
             "assert _sweep_maxrel < 1e-12"):
    assert need in h4, f"H4 lost {need!r}"
assert "G1_crossing" not in h4, "H4 reaches into L206's own verdict block"

# ---- CERT-210M boundary anchors: carry every parent gate, STOP before the
# ---- parent's own predictions/writer block
assert m210.splitlines()[0].startswith("# ================= L210 TAIL"), \
    ("210M first line", m210.splitlines()[0])
assert m210.splitlines()[-1].strip() == '"if lam2 is real and simple"))', \
    ("210M last line", m210.splitlines()[-1])
for _tok in ("CERT-206", "CERT-MV", "CERT-LEFT", "CERT-REBUILD",
             "def mv(x, jv, ls, ld):", "def pi_dir(", "def lam2_defl(",
             "def coeff(", "rows210.append", 'o["cert_206"]',
             'o["cert_rebuild"]', 'o["Q210_1_primary"]', 'o["Q210_4_gap"]',
             "assert _got == NP_[i, dd - 1]", "seed=21004"):
    assert _tok in m210, ("210M lost", _tok)
for _tok in ('o["predictions"]', 'o["rows_per_draw"]', "os.makedirs",
             "json.dump", "_npred"):
    assert _tok not in m210, ("210M slice reaches into the parent's own "
                              "predictions/writer block", _tok)

# ---- the tail must not re-transcribe certified machinery -------------------
for fn in ("def jmatvec", "def reach(", "def power_iter(", "def sweep_actor",
           "def build_sub", "def mv(", "def pi_dir(", "def lam2_defl(",
           "def coeff("):
    assert fn not in tail, f"TAIL re-transcribes certified {fn!r} (L85)"
# ---- the tail MUST contain this card's own new gates -----------------------
for need in ("CERT-218T", "CERT-W50", "CERT-DEFLV", "DEEP = 50",
             "def defl_pair", "def defl_resid", "NO-OP", "_leafcmp",
             'o["Q218_1_primary"]', 'o["Q218_2_rate"]', 'o["Q218_3_u2"]'):
    assert need in tail, f"TAIL lost {need!r}"

banner = (
    '"""GENERATED by l218_build.py — do not edit by hand.\n'
    f"CERT-HEAD1 = l151_static.py lines 1-319 VERBATIM (sha256 {sha1[:16]}).\n"
    f"CERT-HEAD2 = l178_tail.py lines 7-149 VERBATIM (sha256 {sha2[:16]}).\n"
    f"MID        = l206_mid.py (sha256 {sha_mid[:16]}).\n"
    f"CERT-HEAD3 = l178_tail.py lines 348-458 VERBATIM (sha256 {sha3[:16]}).\n"
    f"CERT-HEAD4 = l206_tail.py lines 22-263 VERBATIM (sha256 {sha4[:16]}).\n"
    f"CERT-210M  = l210_tail.py lines 1-326 VERBATIM (sha256 {sha210m[:16]}; "
    f"parent whole-file {sha_l210_whole[:16]}).\n"
    f"TAIL       = l218_tail.py (sha256 {sha_tail[:16]}).\n"
    'PREREG l218/PREREG.md. Writes l218/static.json ONLY.\n'
    '"""\n')
assert len(banner.splitlines()) == 10, ("banner line count (the tail reads 10)",
                                        len(banner.splitlines()))

body = banner + h1 + h2 + mid + h3 + h4 + m210 + "\n\n" + tail
OUT.write_text(body)
assert OUT.read_text() == body
for part in (h1, h2, mid, h3, h4, m210, tail):
    assert part in body, "generated file lost a slice"
print(f"wrote {OUT} ({len(body.splitlines())} lines)")
for nm, s in (("CERT-HEAD1", sha1), ("CERT-HEAD2", sha2), ("MID", sha_mid),
              ("CERT-HEAD3", sha3), ("CERT-HEAD4", sha4),
              ("CERT-210M", sha210m), ("TAIL", sha_tail)):
    print(f"{nm:11s} sha256 {s}")
print(f"PARENT-L210 whole-file sha256 {sha_l210_whole}")
print(f"GENERATED   sha256 {hashlib.sha256(body.encode()).hexdigest()}")
