"""l220_build.py — generate l220_static.py from NINE pieces, EIGHT of which are
VERBATIM SOURCE SLICES of already-certified scripts (L85: never re-transcribe
certified machinery; L175: a lab run script is a SCRIPT, never a library, so
slices are concatenated as source, never imported).

  CERT-HEAD1  = l151_static.py lines 1-319   (data load, pools, ladder, pins;
                                              carries the carrier out-degree
                                              80 pin PREREG 0b leans on)
  CERT-HEAD2  = l178_tail.py   lines 7-149   (CERT-F4, gains, f4wA build, CSR)
  MID         = l206_mid.py                  (csr_rows/csr_cols bridge only)
  CERT-HEAD3  = l178_tail.py   lines 348-458 (CERT-REW + rewire_draws + the
                                              100 f4 draws + the edge->CSR map;
                                              this is where _blk_wA /
                                              _sel_car_wA / S169C live, i.e.
                                              the cutwA null's own definition)
  CERT-HEAD4  = l206_tail.py   lines 22-263  (CERT-178's 420 values, lam1 by
                                              power iteration, the depth-1..10
                                              sweep, the 100-draw null
                                              construction, CERT-NULL)
  MID2        = l211_mid2.py                 (import heapq — l206_tail line 8
                                              sits ABOVE the 22-263 slice)
  CERT-HEAD5  = l206_tail.py   lines 320-461 (L206's WHOLE search-information
                                              block: L/T transforms, the
                                              sorted-by-source index, the
                                              dijkstra, si_summary, the 35
                                              actors, the 100 null draws and
                                              the G2 verdict)
  CERT-HEAD6  = l207_tail.py   lines 26-146  (gain invariance + the GENERIC
                                              substrate builder build_sub +
                                              CERT-GEN; this is how cutwA is
                                              built)
  CERT-211SL  = l211_tail.py   lines 29-322  (L211's WHOLE measurement block,
                                              sliced to CUT its predictions/
                                              writer block — L213's pattern:
                                              every parent gate re-runs for
                                              free, dijkstra_si_fh and
                                              fh_summary arrive as SOURCE
                                              rather than as a
                                              re-transcription, and the f4wA
                                              decomposition is RECOMPUTED so
                                              CERT-211 can certify it against
                                              l211/static.json)
  TAIL        = l220_tail.py                 (L220 body)

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
H6_SRC = pathlib.Path("l207_tail.py")
H7_SRC = pathlib.Path("l211_tail.py")
TAIL_SRC = pathlib.Path("l220_tail.py")
OUT = pathlib.Path("l220_static.py")

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
h6, sha6 = slice_lines(H6_SRC, 26, 146)
h7, sha7 = slice_lines(H7_SRC, 29, 322)
mid = MID_SRC.read_text()
mid2 = MID2_SRC.read_text()
tail = TAIL_SRC.read_text()
sha_mid = hashlib.sha256(mid.encode()).hexdigest()
sha_mid2 = hashlib.sha256(mid2.encode()).hexdigest()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()

# ---- INHERITED PINS: shas L210/L211/L219 recorded in their own banners -----
assert sha1[:16] == "e6245e8306dc8a0f", ("CERT-HEAD1 sha moved", sha1[:16])
assert sha2[:16] == "6e2e8fa4bd19eced", ("CERT-HEAD2 sha moved", sha2[:16])
assert sha3[:16] == "5bb7b56e6b6487d5", ("CERT-HEAD3 sha moved", sha3[:16])
assert sha4[:16] == "772a2410e76516e5", ("CERT-HEAD4 sha moved", sha4[:16])
assert sha_mid[:16] == "febbc390ad4f1a02", ("MID sha moved", sha_mid[:16])
assert sha_mid2[:16] == "5a3b65c25fe714fa", ("MID2 sha moved", sha_mid2[:16])
assert sha5[:16] == "1268be32fd73e4e9", ("CERT-HEAD5 sha moved", sha5[:16])

# ---- PARENT PIN: l211_tail.py must be the file that produced l211/static.json
# l211_static.py's own generated banner recorded its TAIL sha256; if the tail
# moved since, the CERT-211SL slice is not the code that produced the stored
# table CERT-211 certifies against, and this build must STOP.
_l211_gen = pathlib.Path("l211_static.py").read_text().splitlines()
_pin_line = [ln for ln in _l211_gen[:11] if ln.startswith("TAIL ")]
assert len(_pin_line) == 1, ("l211_static.py banner TAIL line", _pin_line)
_pin = _pin_line[0].split("sha256 ")[1].rstrip(").")
assert len(_pin) == 16, ("parent pin length", _pin)
_sha_h7_whole = hashlib.sha256(H7_SRC.read_text().encode()).hexdigest()
assert _sha_h7_whole[:16] == _pin, \
    ("PARENT PIN: l211_tail.py MOVED since it produced l211/static.json",
     _sha_h7_whole[:16], _pin)
# and the generated parent must still carry the heads this build re-slices
for _need in ("CERT-HEAD4 = l206_tail.py lines 22-263",
              "CERT-HEAD5 = l206_tail.py lines 320-461"):
    assert any(_need in ln for ln in _l211_gen[:11]), ("parent banner", _need)

# ---- boundary anchors: a source edit cannot silently shift what we certify --
assert h1.splitlines()[0].startswith('"""'), "H1 first line"
assert "sel_out_wA = emask_wA & (src_all == GI)" in h1, \
    "H1 lost the cutwA carrier out-edge pin (PREREG 0b)"
assert "assert int(sel_out_n.sum()) == 80" in h1, "H1 lost the 80 pin"
assert "keep_wA = keep_new.copy()" in h1 and "emask_wA" in h1
assert h2.splitlines()[0] == "import math", ("H2 first line", h2.splitlines()[0])
assert h2.splitlines()[-1].strip() == "I_vec[dng_l] = DRIVE_D", "H2 last line"
assert h2.splitlines()[15].strip() == "FLOOR = 4", ("H2 FLOOR",
                                                    h2.splitlines()[15])
assert "CERT-F4" in h2
assert "CERT-REW" in h3.splitlines()[0], "H3 first line"
assert h3.splitlines()[-1].strip().startswith("assert np.array_equal(_key_csr"), \
    ("H3 last line", h3.splitlines()[-1])
for need in ("def rewire_draws", "cert_rew", "S169C = json.load",
             "_blk_wA = emask_wA", "_sel_car_wA = emask_wA",
             "def _med", "_car_mass_wA = float"):
    assert need in h3, f"H3 lost {need!r} (the cutwA null's own definition)"
assert h4.splitlines()[0] == 'S178 = json.load(open("l178/static.json"))', \
    ("H4 first line", h4.splitlines()[0])
assert h4.splitlines()[1] == "DMAX = 10", ("H4 DMAX", h4.splitlines()[1])
assert h4.splitlines()[-1].strip() == \
    'source="l178/static.json Q2b_null_anatomical")', \
    ("H4 last line", h4.splitlines()[-1])
for need in ("CERT-178", "CERT-NULL", "def power_iter", "def jmatvec",
             "def reach", "def sweep_actor", "null_changed.append",
             "LAM1, V1, LAMINFO = power_iter(jv_abs_an)",
             'assert pa == st[f"P{d}abs"]', "assert _sweep_maxrel < 1e-12"):
    assert need in h4, f"H4 lost {need!r}"
assert "G1_crossing" not in h4, "H4 reaches into L206's own verdict block"
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
assert h6.splitlines()[0].startswith("# ---------------- gain invariance"), \
    ("H6 first line", h6.splitlines()[0])
for need in ("def build_sub", "def reach_sub", "def power_iter_sub",
             "CERT-GEN", 'o["cert_gen"] = dict(', "jv_g1 = np.abs(_vnp)"):
    assert need in h6, f"H6 lost {need!r}"
assert "P2_normalised" not in h6, "H6 crossed into L207's own verdict block"

# ---- H7: L211's measurement block, sliced to CUT its writer (L213) --------
assert h7.splitlines()[0] == "SHARE_HI, SHARE_LO = 0.60, 0.40", \
    ("H7 first line", h7.splitlines()[0])
assert h7.splitlines()[1] == "GI_MIRROR = 928", ("H7 2nd line",
                                                 h7.splitlines()[1])
assert h7.splitlines()[-1].strip() == \
    '+ ("na" if MIR is None else f"{MIR[\'fh_share_of_si\']:.3f}"))', \
    ("H7 last line", h7.splitlines()[-1])
# POSITIVE: every parent gate and both walkers must be inside the slice
for need in ("CERT-SI", "CERT-MENU", "CERT-FH", "def _cmp_leaf",
             "def dijkstra_si_fh", "def fh_summary", "def _pct",
             'o["L211_primary"] = dict(', 'o["L211_cohort"] = dict(',
             "NULL_FH.append(_sm)", "_cmp_leaf(_live_g2, _stored_g2",
             'assert _live_g2["branch"] == "G2_SI_HIGH"'):
    assert need in h7, f"H7 lost {need!r}"
# NEGATIVE: the parent's predictions/certification/writer must be EXCLUDED
for bad in ('o["predictions"]', 'o["predictions_score"]', 'o["pins"]',
            'o["limitations"]', 'o["certification"]', "FP_SRC", "_os211",
            "json.dump", "L211 DONE"):
    assert bad not in h7, f"H7 reaches into L211's writer block ({bad!r})"
assert "import heapq" in mid2, "MID2 must supply heapq"
assert "import heapq" not in h5, "H5 unexpectedly imports heapq"

banner = (
    '"""GENERATED by l220_build.py — do not edit by hand.\n'
    f"CERT-HEAD1  = l151_static.py lines 1-319 VERBATIM (sha256 {sha1[:16]}).\n"
    f"CERT-HEAD2  = l178_tail.py lines 7-149 VERBATIM (sha256 {sha2[:16]}).\n"
    f"MID         = l206_mid.py (sha256 {sha_mid[:16]}).\n"
    f"CERT-HEAD3  = l178_tail.py lines 348-458 VERBATIM (sha256 {sha3[:16]}).\n"
    f"CERT-HEAD4  = l206_tail.py lines 22-263 VERBATIM (sha256 {sha4[:16]}).\n"
    f"MID2        = l211_mid2.py (sha256 {sha_mid2[:16]}).\n"
    f"CERT-HEAD5  = l206_tail.py lines 320-461 VERBATIM (sha256 {sha5[:16]}).\n"
    f"CERT-HEAD6  = l207_tail.py lines 26-146 VERBATIM (sha256 {sha6[:16]}).\n"
    f"CERT-211SL  = l211_tail.py lines 29-322 VERBATIM (sha256 {sha7[:16]}).\n"
    f"TAIL        = l220_tail.py (sha256 {sha_tail[:16]}).\n"
    'PREREG l220/PREREG.md. Writes l220/static.json ONLY.\n'
    '"""\n')
assert len(banner.splitlines()) == 13, ("banner line count (the tail reads 13)",
                                        len(banner.splitlines()))

body = banner + h1 + h2 + mid + h3 + h4 + mid2 + h5 + h6 + h7 + tail
OUT.write_text(body)
assert OUT.read_text() == body
for part in (h1, h2, mid, h3, h4, mid2, h5, h6, h7, tail):
    assert part in body, "generated file lost a slice"
# the tail must not re-transcribe certified machinery
for fn in ("def jmatvec", "def reach", "def power_iter", "def sweep_actor",
           "def build_sub", "def dijkstra_si(", "def si_summary",
           "def dijkstra_si_fh", "def fh_summary", "def rewire_draws",
           "def _pct"):
    assert fn not in tail, f"TAIL re-transcribes {fn!r} (L85 violation)"
# the tail's own new machinery must be gated, not trusted
for need in ("def build_si_index", "CERT-SIGEN", "CERT-211", "CERT-REWCUT",
             "CERT-MENUCUT", "CERT-REBIND", "CERT-WALKCUT",
             "gain_noop_measured"):
    assert need in tail, f"TAIL lost gate {need!r}"
assert tail.count('json.dump(o, open("l220/static.json", "w"), indent=1)') == 1
print(f"wrote {OUT} ({len(body.splitlines())} lines)")
print(f"CERT-HEAD1  sha256 {sha1}")
print(f"CERT-HEAD2  sha256 {sha2}")
print(f"MID         sha256 {sha_mid}")
print(f"CERT-HEAD3  sha256 {sha3}")
print(f"CERT-HEAD4  sha256 {sha4}")
print(f"MID2        sha256 {sha_mid2}")
print(f"CERT-HEAD5  sha256 {sha5}")
print(f"CERT-HEAD6  sha256 {sha6}")
print(f"CERT-211SL  sha256 {sha7}  [parent pin {_pin} GREEN]")
print(f"TAIL        sha256 {sha_tail}")
print(f"GENERATED    sha256 {hashlib.sha256(body.encode()).hexdigest()}")
