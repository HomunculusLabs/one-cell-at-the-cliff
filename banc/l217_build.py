"""l217_build.py — generate l217_static.py from TWELVE pieces, ten of which
are VERBATIM SOURCE SLICES of already-certified scripts (L85: never
re-transcribe certified machinery; L175: a lab run script is a SCRIPT, never
a library, so slices are concatenated as source, never imported).

  CERT-HEAD1 = l151_static.py lines 1-319   (data load, pools, ladder, pins)
  CERT-HEAD2 = l178_tail.py   lines 7-149   (CERT-F4, gains, f4wA build, CSR)
  MID        = l206_mid.py                  (csr_rows/csr_cols bridge only)
  CERT-HEAD3 = l206_tail.py   lines 22-121  (CERT-178 HALTING + reach/pi_index
                                             + ACTORS/M_OUT + power_iter)
  CERT-HEAD4 = l207_tail.py   lines 26-146  (gain invariance + the GENERIC
                                             substrate builder + CERT-GEN)
  CERT-MV    = l210_tail.py   lines 77-80   (mv: the certified fast matvec)
  CERT-PI    = l210_tail.py   lines 111-126 (pi_dir: directional power iter)
  CERT-DEFL  = l210_tail.py   lines 290-308 (lam2_defl: Hotelling deflation)
  HEAD       = l217_head.py                 (L217 constants + design)
  CERT-209M  = l209_tail.py   lines 34-226  (L205's seven substrates, GROUPS,
                                             the shared permutation draws,
                                             side_stats_from/decorate,
                                             CERT-205 HALTING, the two
                                             substrates, beta/Crofts + lam1,
                                             arrivals())
  CERT-216M  = l216_tail.py   lines 1-204   (pi_sub/gap_sub, CERT-GAP HALTING,
                                             CERT-209 HALTING, the lam1^d
                                             no-op re-measurement, the depth
                                             1..8 TABLE/NULLS, the Perron
                                             asymptotes AINF, the GAPS) —
                                             SLICED to CUT l216's own writer
                                             (L213: a post-hoc/successor build
                                             slices the parent tail at the end
                                             of its measurement block so every
                                             parent gate re-runs for free while
                                             the parent's json.dump is excluded
                                             by the forbidden-token audit)
  TAIL       = l217_tail.py                 (L217 body)

Every INHERITED sha256 is asserted against the value the generating card
RECORDED in its own banner, so a moved or edited source HALTS this build
instead of silently certifying different code.

Each slice is asserted to be a literal substring of its source at the exact
line range and audited for forbidden tokens (file writes / lab imports) so
running it cannot touch another card's artifacts.
"""
import hashlib
import pathlib

H1_SRC = pathlib.Path("l151_static.py")
H2_SRC = pathlib.Path("l178_tail.py")
MID_SRC = pathlib.Path("l206_mid.py")
H3_SRC = pathlib.Path("l206_tail.py")
H4_SRC = pathlib.Path("l207_tail.py")
H5_SRC = pathlib.Path("l210_tail.py")
H6_SRC = pathlib.Path("l209_tail.py")
H7_SRC = pathlib.Path("l216_tail.py")
HEAD_SRC = pathlib.Path("l217_head.py")
TAIL_SRC = pathlib.Path("l217_tail.py")
OUT = pathlib.Path("l217_static.py")

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
h3, sha3 = slice_lines(H3_SRC, 22, 121)
h4, sha4 = slice_lines(H4_SRC, 26, 146)
m1, shamv = slice_lines(H5_SRC, 77, 80)
m2, shapi = slice_lines(H5_SRC, 111, 126)
m3, shadf = slice_lines(H5_SRC, 290, 308)
m4, sha209m = slice_lines(H6_SRC, 34, 226)
m5, sha216m = slice_lines(H7_SRC, 1, 204)
mid = MID_SRC.read_text()
head = HEAD_SRC.read_text()
tail = TAIL_SRC.read_text()
sha_mid = hashlib.sha256(mid.encode()).hexdigest()
sha_head = hashlib.sha256(head.encode()).hexdigest()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()
sha_l209_whole = hashlib.sha256(H6_SRC.read_bytes()).hexdigest()
sha_l216_whole = hashlib.sha256(H7_SRC.read_bytes()).hexdigest()

# ---- INHERITED PINS: the values L209/L210/L216 recorded in their banners ----
INHERITED = {
    "CERT-HEAD1 l151_static.py 1-319": (sha1, "e6245e8306dc8a0f"),
    "CERT-HEAD2 l178_tail.py 7-149": (sha2, "6e2e8fa4bd19eced"),
    "MID l206_mid.py": (sha_mid, "febbc390ad4f1a02"),
    "CERT-HEAD3 l206_tail.py 22-121": (sha3, "29a830839ebc7837"),
    "CERT-HEAD4 l207_tail.py 26-146": (sha4, "e3aa8d3d40b79326"),
    "CERT-209M l209_tail.py WHOLE FILE": (sha_l209_whole, "31a28283be618de0"),
}
for name, (got, want) in INHERITED.items():
    assert got[:16] == want, (name, got[:16], want,
                              "INHERITED sha MISMATCH -> source moved (STOP)")
print(f"[inherited] {len(INHERITED)} sha pins GREEN (L209/L210/L216 banners)")

# ---- L216's own generated banner must still describe the file we slice ----
_gen216 = pathlib.Path("l216_static.py").read_text()
assert f"TAIL       = l216_tail.py (sha256 {sha_l216_whole[:16]})" in _gen216, \
    (sha_l216_whole[:16], "l216_tail.py MOVED since l216_static.py was "
                          "generated -> the CERT-216M slice is not the code "
                          "that produced l216/static.json (STOP)")
print(f"[inherited] CERT-216M parent pin GREEN (l216_tail.py whole-file sha "
      f"{sha_l216_whole[:16]} == l216_static.py's recorded TAIL sha)")

# ---- boundary anchors: a source edit cannot silently shift what we certify --
assert h1.splitlines()[0].startswith('"""'), "H1 first line"
assert h2.splitlines()[0] == "import math", ("H2 first line", h2.splitlines()[0])
assert h2.splitlines()[-1].strip() == "I_vec[dng_l] = DRIVE_D", "H2 last line"
assert "CERT-F4" in h2 and "NL = int(keep_f4.sum())" in h2, "H2 lost NL"
assert h3.splitlines()[0] == 'S178 = json.load(open("l178/static.json"))', \
    ("H3 first line", h3.splitlines()[0])
assert "CERT-178" in h3 and "def power_iter" in h3 and "def reach" in h3
assert 'assert pa == st[f"P{d}abs"]' in h3, "H3 lost the CERT-178 assert"
assert "LAM1, V1, LAMINFO = power_iter(jv_abs_an)" in h3, "H3 lost lam1/V1"
assert h4.splitlines()[0].startswith("# ---------------- gain invariance"), \
    ("H4 first line", h4.splitlines()[0])
assert h4.splitlines()[-1].strip() == '"substrate was built (L44).")', \
    ("H4 last line", h4.splitlines()[-1])
assert "def build_sub" in h4 and "def reach_sub" in h4 \
    and "def power_iter_sub" in h4, "H4 lost a generic function"
assert "CERT-GEN" in h4 and "LAM1_G1, _V1G1, _LI_G1 = power_iter(jv_g1)" in h4
# the three L210 machinery slices: each is EXACTLY one def, nothing else
assert m1.splitlines()[0] == "def mv(x, jv, ls, ld):", ("MV head", m1[:40])
assert m1.splitlines()[-1].strip() == \
    "return np.bincount(ld, weights=jv * x[ls], minlength=NL)", "MV tail"
assert m2.splitlines()[0] == "def pi_dir(jv, ls, ld, iters=400):", "PI head"
assert m2.splitlines()[-1].strip() == "/ max(hist)))", ("PI tail", m2.splitlines()[-1])
assert m3.splitlines()[0] == \
    "def lam2_defl(jv, ls, ld, v1, u1, iters=400, seed=21004):", "DEFL head"
assert m3.splitlines()[-1].strip() == 'converged=bool(sp < 1e-6))', "DEFL tail"
for _s, _n in ((m1, "mv"), (m2, "pi_dir"), (m3, "lam2_defl")):
    assert _s.count("\ndef ") == 0, (_n, "slice contains a second def (STOP)")
    assert "log(" not in _s and "o[" not in _s, (_n, "slice has side effects")
assert "seed=21004" in m3, "DEFL lost L210's seed -> CERT-GAP would be vacuous"
# CERT-209M boundary anchors
assert m4.splitlines()[0].startswith("# ---------------- L205's seven substrates"), \
    ("209M first line", m4.splitlines()[0])
assert m4.splitlines()[-1].strip() == "return out", \
    ("209M last line", m4.splitlines()[-1])
assert "CERT-205" in m4 and "def side_stats_from" in m4 \
    and "def arrivals" in m4 and "def decorate" in m4, "209M lost a function"
assert 'SUBS = {"cutwA": build_sub(keep_wA, emask_wA, "cutwA"), "f4wA": _f4}' in m4
assert 'assert LAMS["f4wA"]["beta"] == LAM1_G1' in m4, "209M lost the lam1 pin"
assert "PERM[key] = M" in m4 and "default_rng(SEED_PERM)" in m4
# CERT-216M boundary anchors: the slice must carry every parent gate and
# must STOP before the parent's own fits/output/writer block
assert m5.splitlines()[0].startswith("# ================= L216 BODY"), \
    ("216M first line", m5.splitlines()[0])
assert m5.splitlines()[-1].strip() == \
    'f"(rel {_rel210:.2e}) — scale invariance of a spectral ratio")', \
    ("216M last line", m5.splitlines()[-1])
for _tok in ("CERT-GAP", "CERT-209", "def pi_sub", "def gap_sub",
             "NO-OP", "PERRON[(sname, op)]", "GAPS[(sname, op)]",
             'o["cert_gap"]', 'o["cert_209"]'):
    assert _tok in m5, ("216M lost", _tok)
for _tok in ('o["branch"]', 'o["fits"]', 'o["predictions"]', "def fit_exp",
             'o["limitations"]', "BRANCH =", 'o["table"]', 'o["A_inf"]',
             'o["gaps"]', "os.makedirs"):
    assert _tok not in m5, ("216M slice reaches into the parent's own "
                            "verdict/output block", _tok)
assert "TABLE, NULLS = {}, {}" in m5 and "PERRON, AINF = {}, {}" in m5
# the HEAD must only set constants/design, never measure (comments exempt)
_head_code = "\n".join(l for l in head.splitlines()
                       if not l.lstrip().startswith("#"))
for name in ("def ", "arrivals(", "side_stats_from(", "power_iter"):
    assert name not in _head_code, f"HEAD contains measurement token {name!r}"
# the tail must not redefine certified machinery
for name in ("def build_sub", "def reach_sub", "def power_iter_sub",
             "def reach(", "def power_iter(", "def mv(", "def pi_dir(",
             "def lam2_defl(", "def arrivals(", "def side_stats_from",
             "def decorate", "def asym(", "def pct_up(", "def pi_sub",
             "def gap_sub"):
    assert name not in tail, f"TAIL re-transcribes certified {name!r}"
# the tail MUST contain this card's own new gates
for name in ("CERT-216", "CERT-SEED", "ADDITIVITY", "rw_in", "def dcross",
             "def arrivals_from"):
    assert name in tail, f"TAIL lost {name!r}"

banner = (
    '"""GENERATED by l217_build.py — do not edit by hand.\n'
    f"CERT-HEAD1 = l151_static.py lines 1-319 VERBATIM (sha256 {sha1[:16]}).\n"
    f"CERT-HEAD2 = l178_tail.py lines 7-149 VERBATIM (sha256 {sha2[:16]}).\n"
    f"MID        = l206_mid.py (sha256 {sha_mid[:16]}).\n"
    f"CERT-HEAD3 = l206_tail.py lines 22-121 VERBATIM (sha256 {sha3[:16]}).\n"
    f"CERT-HEAD4 = l207_tail.py lines 26-146 VERBATIM (sha256 {sha4[:16]}).\n"
    f"CERT-MV    = l210_tail.py lines 77-80 VERBATIM (sha256 {shamv[:16]}).\n"
    f"CERT-PI    = l210_tail.py lines 111-126 VERBATIM (sha256 {shapi[:16]}).\n"
    f"CERT-DEFL  = l210_tail.py lines 290-308 VERBATIM (sha256 {shadf[:16]}).\n"
    f"HEAD       = l217_head.py (sha256 {sha_head[:16]}).\n"
    f"CERT-209M  = l209_tail.py lines 34-226 VERBATIM (sha256 {sha209m[:16]}).\n"
    f"CERT-216M  = l216_tail.py lines 1-204 VERBATIM (sha256 {sha216m[:16]}; "
    f"parent whole-file {sha_l216_whole[:16]}).\n"
    f"TAIL       = l217_tail.py (sha256 {sha_tail[:16]}).\n"
    'PREREG l217/PREREG.md. Writes l217/static.json ONLY.\n'
    '"""\n')
assert len(banner.splitlines()) == 15, len(banner.splitlines())

body = banner + h1 + h2 + mid + h3 + h4 + m1 + "\n\n" + m2 + "\n\n" + m3 \
    + "\n\n" + head + m4 + m5 + "\n\n" + tail
OUT.write_text(body)
assert OUT.read_text() == body
for part in (h1, h2, mid, h3, h4, m1, m2, m3, head, m4, m5, tail):
    assert part in body, "generated file lost a slice"
print(f"wrote {OUT} ({len(body.splitlines())} lines)")
for nm, s in (("CERT-HEAD1", sha1), ("CERT-HEAD2", sha2), ("MID", sha_mid),
              ("CERT-HEAD3", sha3), ("CERT-HEAD4", sha4), ("CERT-MV", shamv),
              ("CERT-PI", shapi), ("CERT-DEFL", shadf), ("HEAD", sha_head),
              ("CERT-209M", sha209m), ("CERT-216M", sha216m),
              ("TAIL", sha_tail)):
    print(f"{nm:11s} sha256 {s}")
print(f"GENERATED   sha256 {hashlib.sha256(body.encode()).hexdigest()}")
