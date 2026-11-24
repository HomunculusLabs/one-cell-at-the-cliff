"""l221_build.py — generate l221_static.py from TEN pieces, NINE of which are
VERBATIM SOURCE SLICES of already-certified scripts (L85: never re-transcribe
certified machinery; L175: a lab run script is a SCRIPT, never a library, so
slices are concatenated as source, never imported).

  CERT-HEAD1  = l151_static.py lines 1-319   (data load, pools, ladder, pins)
  CERT-HEAD2  = l178_tail.py   lines 7-149   (CERT-F4, gains, f4wA build, CSR,
                                              pools local / POOL_ALL)
  MID         = l206_mid.py                  (csr_rows/csr_cols bridge only)
  CERT-HEAD3  = l178_tail.py   lines 348-458 (CERT-REW + rewire_draws + the
                                              100 f4 draws + edge->CSR map)
  CERT-HEAD4  = l206_tail.py   lines 22-263  (CERT-178's 420 values, power_iter,
                                              s_tot/s_safe/jv_crofts/LAM1C =
                                              metric 2's operator, the depth
                                              sweep, the null construction,
                                              CERT-NULL)
  MID2        = l211_mid2.py                 (import heapq)
  CERT-HEAD5  = l206_tail.py   lines 320-461 (L206's WHOLE search-information
                                              block: L/T transforms, the
                                              sorted-by-source index, dijkstra_si,
                                              si_summary, the 35 actors, the 100
                                              draws, the G2 verdict)
  CERT-211SL  = l211_tail.py   lines 29-322  (L211's WHOLE measurement block,
                                              sliced to CUT its predictions/
                                              writer: CERT-SI, CERT-MENU,
                                              CERT-FH, dijkstra_si_fh,
                                              fh_summary, _pct, NULL_FH, CAR,
                                              COH, L211_primary/cohort)
  CERT-220SL  = l220_tail.py   lines 47-128  (CERT-211's 434-leaf anchor on the
                                              recomputed L211 table + the
                                              GENERIC build_si_index and its
                                              CERT-SIGEN 1,922,356-check gate,
                                              sliced to CUT every cutwA block,
                                              the 0c gain leg and the writer)
  TAIL        = l221_tail.py                 (L221 body)

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
H7_SRC = pathlib.Path("l211_tail.py")
H8_SRC = pathlib.Path("l220_tail.py")
TAIL_SRC = pathlib.Path("l221_tail.py")
OUT = pathlib.Path("l221_static.py")

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
h7, sha7 = slice_lines(H7_SRC, 29, 322)
h8, sha8 = slice_lines(H8_SRC, 47, 128)
mid = MID_SRC.read_text()
mid2 = MID2_SRC.read_text()
tail = TAIL_SRC.read_text()
sha_mid = hashlib.sha256(mid.encode()).hexdigest()
sha_mid2 = hashlib.sha256(mid2.encode()).hexdigest()
sha_tail = hashlib.sha256(tail.encode()).hexdigest()

# ---- INHERITED PINS: shas L220 recorded in its own generated banner --------
assert sha1[:16] == "e6245e8306dc8a0f", ("CERT-HEAD1 sha moved", sha1[:16])
assert sha2[:16] == "6e2e8fa4bd19eced", ("CERT-HEAD2 sha moved", sha2[:16])
assert sha3[:16] == "5bb7b56e6b6487d5", ("CERT-HEAD3 sha moved", sha3[:16])
assert sha4[:16] == "772a2410e76516e5", ("CERT-HEAD4 sha moved", sha4[:16])
assert sha_mid[:16] == "febbc390ad4f1a02", ("MID sha moved", sha_mid[:16])
assert sha_mid2[:16] == "5a3b65c25fe714fa", ("MID2 sha moved", sha_mid2[:16])
assert sha5[:16] == "1268be32fd73e4e9", ("CERT-HEAD5 sha moved", sha5[:16])
assert sha7[:16] == "ce02a2d16a4f85cf", ("CERT-211SL sha moved", sha7[:16])


# ---- PARENT PINS: each sliced tail must be the file that produced its own
# generated script, else the slice is not the code whose stored outputs the
# gates certify against.  Both banners record their own TAIL sha256.
def parent_pin(gen_name, tail_path, label):
    gen = pathlib.Path(gen_name).read_text().splitlines()
    cand = [ln for ln in gen[:14] if ln.startswith("TAIL ")]
    assert len(cand) == 1, (gen_name, "banner TAIL line", cand)
    pin = cand[0].split("sha256 ")[1].rstrip(").")
    assert len(pin) == 16, (gen_name, "parent pin length", pin)
    whole = hashlib.sha256(tail_path.read_text().encode()).hexdigest()
    assert whole[:16] == pin, \
        (f"PARENT PIN {label}: {tail_path} MOVED since it produced {gen_name}",
         whole[:16], pin)
    return pin, gen


pin211, gen211 = parent_pin("l211_static.py", H7_SRC, "L211")
pin220, gen220 = parent_pin("l220_static.py", H8_SRC, "L220")
# and each generated parent must still carry the heads this build re-slices
for _need in ("CERT-HEAD4 = l206_tail.py lines 22-263",
              "CERT-HEAD5 = l206_tail.py lines 320-461"):
    assert any(_need in ln for ln in gen211[:14]), ("L211 banner", _need)
assert any("CERT-211SL  = l211_tail.py lines 29-322" in ln
           for ln in gen220[:14]), "L220 banner lost CERT-211SL"

# ---- boundary anchors: a source edit cannot silently shift what we certify --
assert h1.splitlines()[0].startswith('"""'), "H1 first line"
assert "keep_f4 = " in h1 or "keep_f4" in h2, "no keep_f4 anywhere in the heads"
assert h2.splitlines()[0] == "import math", ("H2 first line", h2.splitlines()[0])
assert h2.splitlines()[-1].strip() == "I_vec[dng_l] = DRIVE_D", "H2 last line"
assert h2.splitlines()[15].strip() == "FLOOR = 4", ("H2 FLOOR",
                                                    h2.splitlines()[15])
for need in ("CERT-F4", "POOL_ALL = np.unique", "keep_f4", "loc_f4"):
    assert need in h2, f"H2 lost {need!r}"
assert "CERT-REW" in h3.splitlines()[0], "H3 first line"
assert h3.splitlines()[-1].strip().startswith("assert np.array_equal(_key_csr"), \
    ("H3 last line", h3.splitlines()[-1])
for need in ("def rewire_draws", "cert_rew", "S169C = json.load", "def _med"):
    assert need in h3, f"H3 lost {need!r}"
assert h4.splitlines()[0] == 'S178 = json.load(open("l178/static.json"))', \
    ("H4 first line", h4.splitlines()[0])
assert h4.splitlines()[1] == "DMAX = 10", ("H4 DMAX", h4.splitlines()[1])
assert h4.splitlines()[-1].strip() == \
    'source="l178/static.json Q2b_null_anatomical")', \
    ("H4 last line", h4.splitlines()[-1])
for need in ("CERT-178", "CERT-NULL", "def power_iter", "def jmatvec",
             "null_changed.append", "jv_crofts = jv_abs_an / np.sqrt",
             "s_safe = np.where", "LAM1C, V1C, LAMINFOC = power_iter(jv_crofts)",
             'assert pa == st[f"P{d}abs"]'):
    assert need in h4, f"H4 lost {need!r} (metric 2's operator lives here)"
assert "G1_crossing" not in h4, "H4 reaches into L206's own verdict block"
assert h5.splitlines()[0].startswith("# ---------------- G2: SEARCH INFORM"), \
    ("H5 first line", h5.splitlines()[0])
assert h5.splitlines()[-1].strip() == \
    'f"med {o[\'G2_search_information\'][\'family_si_mean_med\']}")', \
    ("H5 last line", h5.splitlines()[-1])
for need in ("def dijkstra_si", "def si_summary", "_pos_in_sorted",
             "START = np.searchsorted", "NLT = -np.log2", "POOL_ALL.tolist()"):
    assert need in h5, f"H5 lost {need!r}"
assert "G1_crossing" not in h5 and "G3_diffusion" not in h5, \
    "H5 crossed into a neighbouring verdict block"

# ---- H7: L211's measurement block, sliced to CUT its writer (L213) --------
assert h7.splitlines()[0] == "SHARE_HI, SHARE_LO = 0.60, 0.40", \
    ("H7 first line", h7.splitlines()[0])
assert h7.splitlines()[1] == "GI_MIRROR = 928", ("H7 2nd line",
                                                 h7.splitlines()[1])
assert h7.splitlines()[-1].strip() == \
    '+ ("na" if MIR is None else f"{MIR[\'fh_share_of_si\']:.3f}"))', \
    ("H7 last line", h7.splitlines()[-1])
for need in ("CERT-SI", "CERT-MENU", "CERT-FH", "def _cmp_leaf",
             "def dijkstra_si_fh", "def fh_summary", "def _pct",
             'o["L211_primary"] = dict(', 'o["L211_cohort"] = dict(',
             "NULL_FH.append(_sm)", "CAR = fh_summary("):
    assert need in h7, f"H7 lost {need!r}"
for bad in ('o["predictions"]', 'o["predictions_score"]', 'o["pins"]',
            'o["limitations"]', 'o["certification"]', "FP_SRC", "_os211",
            "json.dump", "L211 DONE"):
    assert bad not in h7, f"H7 reaches into L211's writer block ({bad!r})"

# ---- H8: L220's anchor + generic builder, sliced to CUT all cutwA work ----
assert h8.splitlines()[0].startswith("# ---------------- CERT-211 (HALTING)"), \
    ("H8 first line", h8.splitlines()[0])
assert h8.splitlines()[-1].strip() == \
    'f"L_L, T_L, TGT0, pos_in_sorted, A_max) before touching cutwA")', \
    ("H8 last line", h8.splitlines()[-1])
for need in ("def _cmp211", "def build_si_index", "CERT-SIGEN",
             '_S211 = json.load(open("l211/static.json"))',
             "_IX_F4 = build_si_index(jv_abs_an, csr_rows, csr_cols, NL, POOL_ALL)",
             'assert o["L211_primary"]["menu"]["n_out_edges"] == 69',
             'assert _cert211[0] >= 400'):
    assert need in h8, f"H8 lost {need!r}"
# NEGATIVE: not one line of L220's cutwA work, verdict or writer may enter
for bad in ("SUB_CUT", "build_sub", "CERT-REWCUT", "CERT-MENUCUT",
            "CERT-WALKCUT", "CERT-REBIND", 'o["L220_primary"]',
            'o["L220_transport"]', 'o["L220_cohort"]', 'o["gain_noop_measured"]',
            'o["predictions"]', 'o["certification"]', "FP_SRC", "_os220",
            "json.dump", "L220 DONE", "N_OUT_CUT_PIN"):
    assert bad not in h8, f"H8 reaches into L220's cutwA/writer block ({bad!r})"
assert "import heapq" in mid2, "MID2 must supply heapq"
assert "import heapq" not in h5, "H5 unexpectedly imports heapq"

banner = (
    '"""GENERATED by l221_build.py — do not edit by hand.\n'
    f"CERT-HEAD1  = l151_static.py lines 1-319 VERBATIM (sha256 {sha1[:16]}).\n"
    f"CERT-HEAD2  = l178_tail.py lines 7-149 VERBATIM (sha256 {sha2[:16]}).\n"
    f"MID         = l206_mid.py (sha256 {sha_mid[:16]}).\n"
    f"CERT-HEAD3  = l178_tail.py lines 348-458 VERBATIM (sha256 {sha3[:16]}).\n"
    f"CERT-HEAD4  = l206_tail.py lines 22-263 VERBATIM (sha256 {sha4[:16]}).\n"
    f"MID2        = l211_mid2.py (sha256 {sha_mid2[:16]}).\n"
    f"CERT-HEAD5  = l206_tail.py lines 320-461 VERBATIM (sha256 {sha5[:16]}).\n"
    f"CERT-211SL  = l211_tail.py lines 29-322 VERBATIM (sha256 {sha7[:16]}).\n"
    f"CERT-220SL  = l220_tail.py lines 47-128 VERBATIM (sha256 {sha8[:16]}).\n"
    f"PARENT PINS l211_tail {pin211} / l220_tail {pin220} GREEN.\n"
    f"TAIL        = l221_tail.py (sha256 {sha_tail[:16]}).\n"
    'PREREG l221/PREREG.md. Writes l221/static.json ONLY.\n'
    '"""\n')
assert len(banner.splitlines()) == 14, ("banner line count (the tail reads 14)",
                                        len(banner.splitlines()))

body = banner + h1 + h2 + mid + h3 + h4 + mid2 + h5 + h7 + h8 + tail
OUT.write_text(body)
assert OUT.read_text() == body
for part in (h1, h2, mid, h3, h4, mid2, h5, h7, h8, tail):
    assert part in body, "generated file lost a slice"
# the tail must not re-transcribe certified machinery
for fn in ("def jmatvec", "def reach", "def power_iter", "def sweep_actor",
           "def build_sub", "def dijkstra_si(", "def si_summary",
           "def dijkstra_si_fh", "def fh_summary", "def rewire_draws",
           "def _pct", "def build_si_index", "def _cmp211", "def _cmp_leaf",
           "jv_crofts = "):
    assert fn not in tail, f"TAIL re-transcribes {fn!r} (L85 violation)"
# the tail's own new machinery must be gated, not trusted
for need in ("CERT-D5", "CERT-CROFTS", "CERT-FHE", "CERT-DAG",
             "def dijkstra_fe", "def feasible_mask", "def realised_set",
             "Q221_pool_geometry_control", "Q221_0a_costs_vs_edges",
             'o["L221_primary"]'):
    assert need in tail, f"TAIL lost gate {need!r}"
assert tail.count('json.dump(o, open("l221/static.json", "w"), indent=1)') == 1
print(f"wrote {OUT} ({len(body.splitlines())} lines)")
print(f"CERT-HEAD1  sha256 {sha1}")
print(f"CERT-HEAD2  sha256 {sha2}")
print(f"MID         sha256 {sha_mid}")
print(f"CERT-HEAD3  sha256 {sha3}")
print(f"CERT-HEAD4  sha256 {sha4}")
print(f"MID2        sha256 {sha_mid2}")
print(f"CERT-HEAD5  sha256 {sha5}")
print(f"CERT-211SL  sha256 {sha7}  [parent pin {pin211} GREEN]")
print(f"CERT-220SL  sha256 {sha8}  [parent pin {pin220} GREEN]")
print(f"TAIL        sha256 {sha_tail}")
print(f"GENERATED    sha256 {hashlib.sha256(body.encode()).hexdigest()}")
