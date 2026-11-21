"""Build l118_run.py from l117_run.py via exact-string transforms.

Strategy: (1) wholesale-swap the dose-ladder derivation block for the
pinned-draw block (arm-name-keyed), (2) global token renames cutk5/10/15 ->
cutnga/cutngb/cutngc (+ variable stems), (3) seeds B12 -> B13, paths l117 ->
l118, (4) FINAL RESIDUAL SCAN: none of the old tokens may remain. Every
rep prints its count; a zero count aborts (pattern vanished = drift).
"""
import sys

SRC = open("l117_run.py").read()
n_err = 0


def rep(old, new, count=None):
    global SRC, n_err
    c = SRC.count(old)
    if c == 0 or (count is not None and c != count):
        print(f"PATTERN MISMATCH ({c} != {count}): {old[:70]!r}")
        n_err += 1
        return
    SRC = SRC.replace(old, new)
    print(f"ok x{c}: {old[:48]!r}")


# 1. docstring
rep('''"""L117 run: glut-dose-ladder. PREREG l117/PREREG.md FIRST.

L116 machinery VERBATIM (5-pair pools, graphs, gains, draw order); arms
full/b65/cut/cut19/cut58 retained as ANCHORS (stored seeds 801/901 vs
raw_l113) + NEW dose arms cutk5/cutk10/cutk15 = closure minus the k
HEAVIEST glutamatergic heavy cells (deterministic mass-desc positional
filter, NO RNG; l117/static.json pins). Seeds: [801, 901] + FRESH B12
1601-1616 (asserted absent from raw_l113). g_cut/g_cut19/g_cut58
re-bisected + asserted == stored EXACT; dose gains bisected FRESH
(staircase disclosed, PREREG band disclosed not asserted). CPU-only;
raw checkpoint BEFORE analysis.
"""''',
    '''"""L118 run: mass-matched-pure-nonglut-19. PREREG l118/PREREG.md FIRST.

L117 machinery VERBATIM (5-pair pools, graphs, gains, draw order); arms
full/b65/cut/cut19/cut58 retained as ANCHORS (stored seeds 801/901 vs
raw_l113) + NEW draw arms cutnga/cutngb/cutngc = closure minus 19
NON-glutamatergic heavy cells, rejection-mass-matched to the glut-19
UNROUNDED share .11033 (pinned torch seeds 1180/1181/1182; l118/
static.json pins; zero glutamate asserted). Seeds: [801, 901] + FRESH
B13 1701-1716 (asserted absent from raw_l113 + raw_l115 + raw_l117).
g_cut/g_cut19/g_cut58 re-bisected + asserted == stored EXACT; draw gains
bisected FRESH (staircase disclosed, PREREG band disclosed not
asserted). CPU-only; raw checkpoint BEFORE analysis.
"""''')

# 2. wholesale derivation-block swap
rep('''# L117: glut dose ladder — k HEAVIEST glutamatergic heavy cells (heav is
# mass-desc; positional filter is DETERMINISTIC, zero RNG). Pins from
# l117/static.json (PREREG); STOP on any miss.
S117 = json.load(open("l117/static.json"))
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
DOSE_K = (5, 10, 15)
cutk_drop, keep_cutk, n_cutk, dose_pins = {}, {}, {}, {}
for _kk in DOSE_K:
    _pin = S117["ladder"][f"k{_kk}"]
    _drop = np.sort(glut_desc[:_kk])
    assert len(_drop) == _kk
    assert np.isin(_drop, cut19_drop).all(), "dose drop not subset of glut-19"
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_kk, int(_keep.sum()))
    cutk_drop[_kk] = _drop
    keep_cutk[_kk] = _keep
    n_cutk[_kk] = int(_keep.sum())
    dose_pins[_kk] = _pin
assert dose_pins[5]["mass_removed"] == 0.0425 and \\
    dose_pins[10]["mass_removed"] == 0.0723 and \\
    dose_pins[15]["mass_removed"] == 0.0952, "ladder masses drifted (STOP)"''',
    '''# L118: mass-matched PURE-NON-GLUT draws — 19-of-58 non-glutamatergic
# heavy cells, rejection-matched to the glut-19 UNROUNDED share (pinned
# torch seeds; l118/static.json pins; PREREG); STOP on any miss.
S118 = json.load(open("l118/static.json"))
NG_ARMS = ("cutnga", "cutngb", "cutngc")
cutng_drop, keep_cutng, n_cutng, ng_pins = {}, {}, {}, {}
for _a in NG_ARMS:
    _pin = S118["draws"][_a]
    assert _pin["seed"] in (1180, 1181, 1182) and not _pin["attempts_fallback"]
    _drop = np.sort(np.array(_pin["drop_ids"], np.int64))
    assert len(_drop) == 19
    assert not np.isin(_drop, cut19_drop).any(), "draw overlaps glut-19 (STOP)"
    assert np.isin(_drop, cut_drop).all(), "draw not subset of heavy-77 (STOP)"
    assert not is_glut[_drop].any(), "glutamate cell in pure-non-glut draw (STOP)"
    assert abs(_pin["mass_removed"] - S118["target_unrounded"]) <= S118["tol"]
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    cutng_drop[_a] = _drop
    keep_cutng[_a] = _keep
    n_cutng[_a] = int(_keep.sum())
    ng_pins[_a] = _pin
# (DNg100-not-in-heavy-77 asserted downstream in the dng100 section + pinned
# in l118/static.json — dng100_all is not yet defined at this point.)''')

# 3. seeds: fresh B13
rep('''B12 = list(range(1601, 1617))       # fresh, verified absent from raw_l113
SEEDS = ANCH + B12                  # anchors FIRST: early wiring verdict
FRESH = B12''',
    '''B13 = list(range(1701, 1717))       # fresh, absent from l113/l115/l117
SEEDS = ANCH + B13                  # anchors FIRST: early wiring verdict
FRESH = B13''')

# 4. global renames (disjoint token stems; counts printed, must be >0)
rep("cutk5", "cutnga")
rep("cutk10", "cutngb")
rep("cutk15", "cutngc")
rep("loc_ck5", "loc_nga")
rep("loc_ck10", "loc_ngb")
rep("loc_ck15", "loc_ngc")
rep("Wc_ck5", "Wc_nga")
rep("Wc_ck10", "Wc_ngb")
rep("Wc_ck15", "Wc_ngc")
rep("Wb_ck5", "Wb_nga")
rep("Wb_ck10", "Wb_ngb")
rep("Wb_ck15", "Wb_ngc")
rep("gi_ck5", "gi_nga")
rep("gi_ck10", "gi_ngb")
rep("gi_ck15", "gi_ngc")
rep("old_pos_in_ck5", "old_pos_in_nga")
rep("old_pos_in_ck10", "old_pos_in_ngb")
rep("old_pos_in_ck15", "old_pos_in_ngc")
rep("ck5_pos_in_new", "nga_pos_in_new")
rep("ck10_pos_in_new", "ngb_pos_in_new")
rep("ck15_pos_in_new", "ngc_pos_in_new")
rep("kept_new_mask_k5", "kept_new_mask_nga")
rep("kept_new_mask_k10", "kept_new_mask_ngb")
rep("kept_new_mask_k15", "kept_new_mask_ngc")
# remaining ck5/ck10/ck15 (e.g. Xc_ck5 state vars) — catch-all, then scan
rep("ck5", "nga")
rep("ck10", "ngb")
rep("ck15", "ngc")
rep("keep_cutk[5]", 'keep_cutng["cutnga"]')
rep("keep_cutk[10]", 'keep_cutng["cutngb"]')
rep("keep_cutk[15]", 'keep_cutng["cutngc"]')
rep("n_cutk[5]", 'n_cutng["cutnga"]')
rep("n_cutk[10]", 'n_cutng["cutngb"]')
rep("n_cutk[15]", 'n_cutng["cutngc"]')
rep("cutk_drop[5]", 'cutng_drop["cutnga"]')
rep("cutk_drop[10]", 'cutng_drop["cutngb"]')
rep("cutk_drop[15]", 'cutng_drop["cutngc"]')

# 5. stairs/band/mass names
rep("dose_stairs", "ng_stairs")
rep("dose_band_ok", "ng_band_ok")
rep('''                    dose_mass=np.array([dose_pins[5]["mass_removed"],
                                        dose_pins[10]["mass_removed"],
                                        dose_pins[15]["mass_removed"]]),''',
    '''                    ng_mass=np.array([ng_pins[a]["mass_removed"] for a in
                                      ("cutnga", "cutngb", "cutngc")]),''')
rep('           dose_mass={k: dose_pins[k]["mass_removed"] for k in DOSE_K},',
    '           ng_mass={a: ng_pins[a]["mass_removed"] for a in NG_ARMS},')

# 6. bisect comment wording
rep('''# L117: fresh bisects for the dose arms (no stored form; staircase + band
# DISCLOSED per PREREG — the .14-.16 band is a disclosure, never an abort)''',
    '''# L118: fresh bisects for the draw arms (no stored form; staircase + band
# DISCLOSED per PREREG — the .14-.16 band is a disclosure, never an abort)''')

# 7. dng100 comment wording
rep('''# L115/L117 pin: no DNg100 cell sits in the heavy-77 (dose drops cannot
# touch the drive channel) — STOP if violated.''',
    '''# L115/L117/L118 pin: no DNg100 cell sits in the heavy-77 (draw drops
# cannot touch the drive channel) — STOP if violated.''')

# 8. C0A: B12->B13 + extra absence asserts vs raw_l115 / raw_l117
rep('''# B12 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B12), \\
    "B12 collides with stored batches (STOP)"''',
    '''# B13 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B13), \\
    "B13 collides with stored batches (STOP)"
for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B13), \\
        ("B13 collides with " + _prev + " (STOP)")''')
rep('log(f"C0A covered keys {len(C0A_KEYS)} x stored arms {len(STORED_ARMS)} "',
    'log(f"C0A covered keys {len(C0A_KEYS)} x stored arms {len(STORED_ARMS)} "')

# 9. paths l117 -> l118 (raw_partial, savez, anchors, logs)
rep("l117/raw_partial.npz", "l118/raw_partial.npz")
rep("l117/raw_l117.npz", "l118/raw_l118.npz")
rep("raw_l117.npz checkpointed BEFORE analysis", "raw_l118.npz checkpointed BEFORE analysis")
rep('json.dump(out, open("l117/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l118/anchors_run.json", "w"), indent=1)')

# edges asserts in the graphs block (post-rename form: Wc_* already renamed,
# dose_pins[...] was never covered by the bracket renames)
rep('assert Wc_nga.values().numel() == dose_pins[5]["edges"]',
    'assert Wc_nga.values().numel() == ng_pins["cutnga"]["edges"]')
rep('assert Wc_ngb.values().numel() == dose_pins[10]["edges"]',
    'assert Wc_ngb.values().numel() == ng_pins["cutngb"]["edges"]')
rep('assert Wc_ngc.values().numel() == dose_pins[15]["edges"]',
    'assert Wc_ngc.values().numel() == ng_pins["cutngc"]["edges"]')

# 9b. the global path rename in 9 also rewired the C0A absence-assert loop
# onto the run's OWN output file (l118/raw_l118.npz) — restore the intended
# PRIOR-run reference (L39-class control rewiring, caught pre-launch).
rep('for _prev in ("l115/raw_l115.npz", "l118/raw_l118.npz"):',
    'for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz"):')

# 10. residual scan — NO old token may remain (rename completeness).
# 'l117' is allowed ONLY as the deliberate cross-check reference
# ("l117/raw_l117.npz" absence assert + the "l113/l115/l117" comment).
_allowed = ("l117/raw_l117.npz", "l113/l115/l117", "raw_l117")
_scrub = SRC
for _a in _allowed:
    _scrub = _scrub.replace(_a, "")
LEFTOVER = [t for t in ("cutk", "ck5", "ck10", "ck15", "_k5", "_k10", "_k15",
                        "dose_pins", "DOSE_K", "S117", "B12", "l117",
                        "glut_desc", "dose_stairs", "dose_mass",
                        "dose_band_ok") if t in _scrub]
if LEFTOVER:
    print(f"RESIDUAL OLD TOKENS: {LEFTOVER}")
    for i, line in enumerate(_scrub.split("\n"), 1):
        if any(t in line for t in LEFTOVER):
            print(f"  {i} | {line[:110]}")
    n_err += 1
else:
    print("residual scan clean: no old tokens remain")

if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
open("l118_run.py", "w").write(SRC)
print("l118_run.py written OK")
