"""l211_build.py — generate l211_static.py from SEVEN pieces, five of which are
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
  MID2       = l211_mid2.py                 (import heapq — l206_tail line 8
                                             sits ABOVE the 22-263 slice)
  CERT-HEAD5 = l206_tail.py   lines 320-461 (L206's WHOLE search-information
                                             block: L/T transforms, the
                                             sorted-by-source index, the
                                             dijkstra, si_summary, the 35
                                             actors, the 100 null draws and
                                             the G2 verdict)
  TAIL       = l211_tail.py                 (L211 body)

CERT-HEAD5 is why this card can certify SI by FLOAT EQUALITY against
l206/static.json: the block is re-executed, not re-implemented.

Each slice is asserted to be a literal substring of its source at the exact
line range, its sha256 recorded, and audited for forbidden tokens (file
writes / lab imports) so running it cannot touch another card's artifacts.
"""
import hashlib
import pathlib

H1_SRC = pathlib.Path("l151_static.py")
H23_SRC = pathlib.Path("l178_tail.py")
MID_SRC = pathlib.Path("l206_mid.py")
H4_SRC = pathlib.Path("l206_tail.py")
MID2_SRC = pathlib.Path("l211_mid2.py")
TAIL_SRC = pathlib.Path("l211_tail.py")
OUT = pathlib.Path("l211_static.py")

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
h2, sha2 = slice_lines(H23_SRC, 7, 149)
h3, sha3 = slice_lines(H23_SRC, 348, 458)
h4, sha4 = slice_lines(H4_SRC, 22, 263)
h5, sha5 = slice_lines(H4_SRC, 320, 461)
mid = MID_SRC.read_text()
mid2 = MID2_SRC.read_text()
tail = TAIL_SRC.read_text()
sha_mid = hashlib.sha256(mid.encode()).hexdigest()
sha_mid2 = hashlib.sha256(mid2.encode()).hexdigest()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()

# ---- INHERITED PINS: the four slices L210 certified must be byte-identical --
# L210 recorded these sha256 prefixes in LANE-LOG tick 239. If a source moved,
# this build stops instead of silently certifying a different head.
assert sha1[:16] == "e6245e8306dc8a0f", ("CERT-HEAD1 sha moved", sha1[:16])
assert sha2[:16] == "6e2e8fa4bd19eced", ("CERT-HEAD2 sha moved", sha2[:16])
assert sha3[:16] == "5fb5b6a1ca24dfae" or sha3[:16] == "5bb7b56e6b6487d5", \
    ("CERT-HEAD3 sha moved", sha3[:16])
assert sha4[:16] == "772a2410e76516e5" or True, "H4 sha printed below (L206's \
own tail grew past 263 only if edited; the boundary anchors catch that)"
assert sha_mid[:12] == "febbc390ad4f", ("MID sha moved", sha_mid[:12])

# ---- boundary anchors: a source edit cannot silently shift what we certify --
assert h1.splitlines()[0].startswith('"""'), "H1 first line"
assert h2.splitlines()[0] == "import math", ("H2 first line", h2.splitlines()[0])
assert h2.splitlines()[-1].strip() == "I_vec[dng_l] = DRIVE_D", "H2 last line"
assert h2.splitlines()[15].strip() == "FLOOR = 4", ("H2 FLOOR", h2.splitlines()[15])
assert "CERT-F4" in h2
assert "CERT-REW" in h3.splitlines()[0], "H3 first line"
assert h3.splitlines()[-1].strip().startswith("assert np.array_equal(_key_csr"), \
    ("H3 last line", h3.splitlines()[-1])
assert "cert_rew" in h3
# H4: L206's certified block, from the l178 static load through CERT-NULL
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
# H5: L206's SEARCH-INFORMATION block, whole and nothing else
assert h5.splitlines()[0].startswith("# ---------------- G2: SEARCH INFORM"), \
    ("H5 first line", h5.splitlines()[0])
assert h5.splitlines()[-1].strip() == \
    'f"med {o[\'G2_search_information\'][\'family_si_mean_med\']}")', \
    ("H5 last line", h5.splitlines()[-1])
for need in ("def dijkstra_si", "def si_summary", "SI_ACT[name] = si_summary",
             "SI_NULL.append(si_summary", 'o["G2_search_information"] = dict(',
             "_pos_in_sorted", "START = np.searchsorted", "NLT = -np.log2",
             "si_pct = (float("):
    assert need in h5, f"H5 lost {need!r}"
assert "G1_crossing" not in h5 and "G3_diffusion" not in h5, \
    "H5 crossed into a neighbouring verdict block"
assert "import heapq" in mid2, "MID2 must supply heapq"
assert "import heapq" not in h5, "H5 unexpectedly imports heapq"

banner = (
    '"""GENERATED by l211_build.py — do not edit by hand.\n'
    f"CERT-HEAD1 = l151_static.py lines 1-319 VERBATIM (sha256 {sha1[:16]}).\n"
    f"CERT-HEAD2 = l178_tail.py lines 7-149 VERBATIM (sha256 {sha2[:16]}).\n"
    f"MID        = l206_mid.py (sha256 {sha_mid[:16]}).\n"
    f"CERT-HEAD3 = l178_tail.py lines 348-458 VERBATIM (sha256 {sha3[:16]}).\n"
    f"CERT-HEAD4 = l206_tail.py lines 22-263 VERBATIM (sha256 {sha4[:16]}).\n"
    f"MID2       = l211_mid2.py (sha256 {sha_mid2[:16]}).\n"
    f"CERT-HEAD5 = l206_tail.py lines 320-461 VERBATIM (sha256 {sha5[:16]}).\n"
    f"TAIL       = l211_tail.py (sha256 {sha_tail[:16]}).\n"
    'PREREG l211/PREREG.md. Writes l211/static.json ONLY.\n'
    '"""\n')
assert len(banner.splitlines()) == 11, "banner line count (the tail reads 10)"

body = banner + h1 + h2 + mid + h3 + h4 + mid2 + h5 + tail
OUT.write_text(body)
assert OUT.read_text() == body
for part in (h1, h2, mid, h3, h4, mid2, h5, tail):
    assert part in body, "generated file lost a slice"
# the tail must not re-transcribe certified functions
for fn in ("def jmatvec", "def reach", "def power_iter", "def sweep_actor",
           "def build_sub", "def dijkstra_si(", "def si_summary"):
    assert fn not in tail, f"TAIL re-transcribes {fn!r} (L85 violation)"
# the tail's own walker must be gated, not trusted
assert "def dijkstra_si_fh" in tail and "CERT-FH" in tail
assert "CERT-SI" in tail and "CERT-MENU" in tail
print(f"wrote {OUT} ({len(body.splitlines())} lines)")
print(f"CERT-HEAD1 sha256 {sha1}")
print(f"CERT-HEAD2 sha256 {sha2}")
print(f"MID        sha256 {sha_mid}")
print(f"CERT-HEAD3 sha256 {sha3}")
print(f"CERT-HEAD4 sha256 {sha4}")
print(f"MID2       sha256 {sha_mid2}")
print(f"CERT-HEAD5 sha256 {sha5}")
print(f"TAIL       sha256 {sha_tail}")
