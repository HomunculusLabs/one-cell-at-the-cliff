"""Build l121_run.py from l120_run.py via exact-string transforms.

Strategy: (1) docstring swap, (2) G_CUTK3 const out, (3) seeds B15->B16
(+ l120 absence), (4) wholesale derivation-block swap (retained cutk5 +
non-glut dose ladder cutng via OLD tokens), (5) cutk3 stored-bisect block
DELETED, (6) fresh-bisect loop gains the third arm, (7) C0A-119 block ->
C0A-120 (cutk5 vs raw_l120), (8) excluded-arms log line, (9) out-dict
edits, (10) output paths l120->l121 (INPUT paths l113/l115/l117/l118/
l119/l120 kept — direction check), (11) global renames cutk4a->cutng19 /
cutk4b->cutng29 / cutk3->cutng39 + suffixes, (12) residual scan +
direction check + py_compile. Every rep prints its count; zero/mismatched
count aborts (drift guard).
"""
import py_compile
import sys

SRC = open("l120_run.py").read()
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
rep('''"""L120 run: cutk4-disambiguation. PREREG l120/PREREG.md FIRST.

L119 machinery VERBATIM (5-pair pools, graphs, gains, draw order); arms
full/b65/cut/cut19/cut58 retained as ANCHORS (stored seeds 801/901 vs
raw_l113) + ladder arms cutk3/cutk4a/cutk4b/cutk5 = closure minus
positional drops of the glut_desc mass-DESC order: k3 [286,313,561],
k4a [204,286,313,561] (4th heaviest), k4b [286,313,561,32014] (5th),
k5 all five — k4a/k4b MASS-MATCHED by construction (delta .0001 rounded,
9.2e-05 unrounded; l120/static.json pins; k3/k5 == l119 stored EXACT).
NO RNG draw arm. Seeds: [801, 901] + FRESH B15 1901-1916 (asserted
absent from raw_l113 + l115 + l117 + l118 + l119). g_cut/g_cut19/g_cut58/
g_cutk5 AND g_cutk3 (l119 fresh gain, NEW stored-form anchor) re-bisected
+ asserted == stored EXACT; cutk4a/cutk4b gains bisected FRESH (staircase
+ band DISCLOSED, never asserted). C0A-119: cutk3/cutk5 bit-anchored vs
raw_l119 at 801/901. CPU-only; raw checkpoint BEFORE analysis.
"""''',
    '''"""L121 run: nonglut-dose-ladder. PREREG l121/PREREG.md FIRST.

L120 machinery VERBATIM (5-pair pools, graphs, gains, draw order); arms
full/b65/cut/cut19/cut58 retained as ANCHORS (stored seeds 801/901 vs
raw_l113) + retained cutk5 (C0A-120 forward-chain anchor vs raw_l120 AND
free B16 replication read of the L120 XOR kill) + dose ladder cutng19/
cutng29/cutng39 = closure minus the k HEAVIEST NON-glutamatergic heavy
cells (deterministic mass-desc positional prefixes of ng_desc, NO RNG;
masses .1946/.2588/.3132; l121/static.json pins; k58 endpoint == the
cut58 arm by set identity + edge recompute). Seeds: [801, 901] + FRESH
B16 2001-2016 (asserted absent from raw_l113 + l115 + l117 + l118 +
l119 + l120). g_cut/g_cut19/g_cut58/g_cutk5 re-bisected + asserted ==
stored EXACT; cutng19/29/39 gains bisected FRESH (staircase + band
DISCLOSED, never asserted). C0A-120: cutk5 bit-anchored vs raw_l120 at
801/901. CPU-only; raw checkpoint BEFORE analysis.
"""''')

# 2. G_CUTK3 stored const out (no cutk3 stored arm in L121)
rep('G_CUTK3_STORED = 0.17404209494590758  # l119 stored fresh gain, C0A(k3)\n',
    '')

# 3. seeds header: B15 -> B16
rep('B15 = list(range(1901, 1917))       # fresh, absent l113/l115/l117/l118/l119',
    'B16 = list(range(2001, 2017))       # fresh, absent l113/l115/l117/l118/l119/l120')
rep('SEEDS = ANCH + B15                  # anchors FIRST: early wiring verdict',
    'SEEDS = ANCH + B16                  # anchors FIRST: early wiring verdict')
rep('FRESH = B15', 'FRESH = B16')

# 4. wholesale derivation-block swap (retained k5 + ng ladder, OLD tokens)
rep('''# L119: minimal glut subset — k HEAVIEST glut cells (deterministic
# mass-desc positional filter; l119/static.json pins; k5 asserted ==
# l117 stored) + pinned-RNG random 5-of-19-glut draw (seed 1190).
S120 = json.load(open("l120/static.json"))
NEW_ARMS = ("cutk3", "cutk4a", "cutk4b", "cutk5")
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
keep_cutk, n_cutk, cutk_drop, cutk_pins = {}, {}, {}, {}
for _pk, _a, _pos in (("k3", "cutk3", [0, 1, 2]),
                      ("k4a", "cutk4a", [0, 1, 2, 3]),
                      ("k4b", "cutk4b", [0, 1, 2, 4]),
                      ("k5", "cutk5", [0, 1, 2, 3, 4])):
    _pin = S120["ladder"][_pk]
    _drop = np.sort(glut_desc[_pos])
    assert len(_drop) == len(_pos)
    assert np.isin(_drop, cut19_drop).all(), "ladder drop not subset of glut-19"
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin
assert [int(x) for x in cutk_drop["cutk4a"]] == [204, 286, 313, 561]
assert [int(x) for x in cutk_drop["cutk4b"]] == [286, 313, 561, 32014]
assert [int(x) for x in cutk_drop["cutk5"]] == [204, 286, 313, 561, 32014]
assert cutk_pins["cutk4a"]["mass_removed"] == 0.0347, "k4a mass drift (STOP)"
assert cutk_pins["cutk4b"]["mass_removed"] == 0.0346, "k4b mass drift (STOP)"
assert cutk_pins["cutk5"]["mass_removed"] == 0.0425, "k5 mass drift (STOP)"
assert cutk_pins["cutk3"]["edges"] == 647526, "k3 edges drift (STOP)"
assert cutk_pins["cutk5"]["edges"] == 647252, "k5 edges drift (STOP)"
# (DNg100-not-in-heavy-77 asserted downstream in the dng100 section + pinned
# in l120/static.json — dng100_all is not yet defined at this point.)''',
    '''# L121: non-glut dose ladder — k HEAVIEST non-glut cells (deterministic
# mass-desc positional prefixes of ng_desc; l121/static.json pins; k58
# endpoint == the cut58 arm by set identity + edge recompute) + retained
# cutk5 anchor arm (pins == l117/l119/l120 stored EXACT).
S121 = json.load(open("l121/static.json"))
NEW_ARMS = ("cutk5", "cutk4a", "cutk4b", "cutk3")
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
ng_desc = heav[~is_glut[heav]]
assert len(ng_desc) == 58
assert np.array_equal(np.sort(ng_desc), cut58_drop), "ng58 != cut58 set (STOP)"
keep_cutk, n_cutk, cutk_drop, cutk_pins = {}, {}, {}, {}
_pin5 = S121["ladder"]["k5"]
_drop5 = np.sort(glut_desc[[0, 1, 2, 3, 4]])
assert np.isin(_drop5, cut19_drop).all(), "k5 drop not subset of glut-19"
_keep5 = keep_new.copy()
_keep5[_drop5] = False
assert int(_keep5.sum()) == _pin5["n"], ("cutk5", int(_keep5.sum()))
keep_cutk["cutk5"] = _keep5
n_cutk["cutk5"] = int(_keep5.sum())
cutk_drop["cutk5"] = _drop5
cutk_pins["cutk5"] = _pin5
for _pk, _a, _kk in (("k19", "cutk4a", 19), ("k29", "cutk4b", 29),
                     ("k39", "cutk3", 39)):
    _pin = S121["ngladder"][_pk]
    _drop = np.sort(ng_desc[:_kk])
    assert len(_drop) == _kk
    assert np.isin(_drop, cut58_drop).all(), "ng drop not subset of cut58"
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin
assert [int(x) for x in cutk_drop["cutk5"]] == [204, 286, 313, 561, 32014]
assert cutk_pins["cutk5"]["mass_removed"] == 0.0425, "k5 mass drift (STOP)"
assert cutk_pins["cutk5"]["edges"] == 647252, "k5 edges drift (STOP)"
assert cutk_pins["cutk4a"]["mass_removed"] == 0.1946, "ng19 mass drift (STOP)"
assert cutk_pins["cutk4b"]["mass_removed"] == 0.2588, "ng29 mass drift (STOP)"
assert cutk_pins["cutk3"]["mass_removed"] == 0.3132, "ng39 mass drift (STOP)"
assert cutk_pins["cutk4a"]["edges"] == 644729, "ng19 edges drift (STOP)"
assert cutk_pins["cutk4b"]["edges"] == 643623, "ng29 edges drift (STOP)"
assert cutk_pins["cutk3"]["edges"] == 642698, "ng39 edges drift (STOP)"
assert S121["ngladder"]["k58"]["edges"] == int(
    (keep_cut58[src_all] & keep_cut58[dst_all]).sum()), "k58 != cut58 arm (STOP)"
# (DNg100-not-in-heavy-77 asserted downstream in the dng100 section + pinned
# in l121/static.json — dng100_all is not yet defined at this point.)''')

# 5. cutk3 stored-bisect block DELETED (no stored gain for ng39)
rep('''
# L120: cutk3 re-bisect must land on the stored l119 fresh gain EXACTLY
lo5, hi5 = 0.12, 0.18
af_lo5, af_hi5 = bisect_af_mean(lo5, "cutk3"), bisect_af_mean(hi5, "cutk3")
log(f"cutk3 bracket af({lo5})={af_lo5:.5f} af({hi5})={af_hi5:.5f} "
    f"target {AF_T:.5f}")
assert af_lo5 < AF_T < af_hi5, "cutk3 bracket fail"
for it in range(24):
    mid = (lo5 + hi5) / 2
    if bisect_af_mean(mid, "cutk3") < AF_T:
        lo5 = mid
    else:
        hi5 = mid
GAIN["cutk3"] = lo5
af_finalk3 = bisect_af_mean(lo5, "cutk3")
assert GAIN["cutk3"] == G_CUTK3_STORED, (GAIN["cutk3"], G_CUTK3_STORED)
log(f"g_cutk3 {lo5:.6f} == l119 stored EXACT | af_finalk3 {af_finalk3:.6f} "
    f"|af-target| {abs(af_finalk3 - AF_T):.2e} (staircase disclosed)")
''', '\n')

# 6. fresh-bisect loop gains the third arm
rep('for _a in ("cutk4a", "cutk4b"):', 'for _a in ("cutk4a", "cutk4b", "cutk3"):')

# 7. C0A-119 block -> C0A-120 (cutk5 only, vs raw_l120)
rep('''# C0A-119 (NEW anchor class): cutk3/cutk5 at stored seeds vs raw_l119.
# l119 ran every arm at all 18 seeds, so these two arms have stored
# counterparts on ALL pool keys; cutk4a/cutk4b have NONE (excluded by name).
z119 = np.load("l119/raw_l119.npz")
_c0a119_poolkeys = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _c0a119_poolkeys.append(f"{_pk}_{_c}{_s}")
C0A119_KEYS = ["mm", "xm"] + _c0a119_poolkeys
assert all(f"{_k}_cutk3_801" in z119.files for _k in C0A119_KEYS)
c0a119 = {}
for s in (801, 901):
    for key in C0A119_KEYS:
        for a in ("cutk3", "cutk5"):
            c0a119[f"119_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z119[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk3", "cutk5"):
        c0a119[f"119_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z119[f"af_{a}_{s}"]))
c0a119_max = max(c0a119.values())
c0a119_pass = bool(all(v == 0.0 for v in c0a119.values()))
log(f"C0A-119 cutk3/cutk5 vs raw_l119: {'PASS' if c0a119_pass else 'FAIL'} "
    f"(max {c0a119_max:.1e}, {len(C0A119_KEYS)} keys x 2 arms x 2 seeds)")''',
    '''# C0A-120 (NEW anchor class): cutk5 at stored seeds vs raw_l120.
# l120 ran every arm at all 18 seeds, so cutk5 has a stored counterpart
# on ALL pool keys; cutng19/29/39 have NONE (excluded by name).
z120 = np.load("l120/raw_l120.npz")
_c0a120_poolkeys = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _c0a120_poolkeys.append(f"{_pk}_{_c}{_s}")
C0A120_KEYS = ["mm", "xm"] + _c0a120_poolkeys
assert all(f"{_k}_cutk5_801" in z120.files for _k in C0A120_KEYS)
c0a120 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5",):
            c0a120[f"120_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z120[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5",):
        c0a120[f"120_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z120[f"af_{a}_{s}"]))
c0a120_max = max(c0a120.values())
c0a120_pass = bool(all(v == 0.0 for v in c0a120.values()))
log(f"C0A-120 cutk5 vs raw_l120: {'PASS' if c0a120_pass else 'FAIL'} "
    f"(max {c0a120_max:.1e}, {len(C0A120_KEYS)} keys x 1 arm x 2 seeds)")''')

# 8. excluded-arms log line
rep('''    f"| NEW arms excluded (no l113 counterpart): ['cutk3','cutk4a','cutk4b',"
    "'cutk5'] | cutk3/cutk5 additionally C0A-anchored vs raw_l119")''',
    '''    f"| NEW arms excluded (no l113 counterpart): ['cutk5','cutk4a','cutk4b',"
    "'cutk3'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120)")''')

# 9. out-dict edits
rep('           g_cutk3_stored_exact=bool(GAIN["cutk3"] == G_CUTK3_STORED),\n',
    '')
rep('''           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutk4a", "cutk4b"))),''',
    '''           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutk4a", "cutk4b", "cutk3"))),''')
rep('           af_finalk5=af_finalk5, af_finalk3=af_finalk3,',
    '           af_finalk5=af_finalk5,')
rep('''           c0a119_max=c0a119_max, c0a119_pass=c0a119_pass,
           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a119_pass))''',
    '''           c0a120_max=c0a120_max, c0a120_pass=c0a120_pass,
           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass))''')

# 10. absence asserts: B15 -> B16, + l120 prev
rep('''# B15 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B15), \\
    "B15 collides with stored batches (STOP)"''',
    '''# B16 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B16), \\
    "B16 collides with stored batches (STOP)"''')
rep('''for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",
              "l118/raw_l118.npz", "l119/raw_l119.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B15), \\
        ("B15 collides with " + _prev + " (STOP)")''',
    '''for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",
              "l118/raw_l118.npz", "l119/raw_l119.npz",
              "l120/raw_l120.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B16), \\
        ("B16 collides with " + _prev + " (STOP)")''')

# 11. output paths l120 -> l121 (INPUTS stay: l113..l120 npzs/statics)
rep('if os.path.exists("l120/raw_partial.npz"):',
    'if os.path.exists("l121/raw_partial.npz"):')
rep('    z = np.load("l120/raw_partial.npz")',
    '    z = np.load("l121/raw_partial.npz")')
rep('np.savez("l120/raw_partial.npz", **store)',
    'np.savez("l121/raw_partial.npz", **store)')
rep('np.savez_compressed("l120/raw_l120.npz", K=K, g_cut=GAIN["cut"],',
    'np.savez_compressed("l121/raw_l121.npz", K=K, g_cut=GAIN["cut"],')
rep('log("raw_l120.npz checkpointed BEFORE analysis")',
    'log("raw_l121.npz checkpointed BEFORE analysis")')
rep('json.dump(out, open("l120/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l121/anchors_run.json", "w"), indent=1)')

# 12. global renames (LAST: old arm tokens -> ng names)
rep("cutk4a", "cutng19")
rep("cutk4b", "cutng29")
rep("cutk3", "cutng39")
rep("_k4a", "_ng19")
rep("_k4b", "_ng29")
rep("_k3", "_ng39")

# 13. residual scan + file-path direction check
if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
bad_tokens = ["cutk3", "cutk4a", "cutk4b", "G_CUTK3", "c0a119", "z119",
              "1901", "1917", "B15", "S120", "af_finalk3"]
leftovers = {t: SRC.count(t) for t in bad_tokens if SRC.count(t)}
print("residual scan:", leftovers if leftovers else "CLEAN")
import re
paths = sorted({a or b for a, b in re.findall(
    r'np\.load\("([^"]+)"\)|open\("([^"]+)"\)', SRC)})
outs = [p for p in paths if p.startswith("l121")]
ins = [p for p in paths if not p.startswith("l121")]
print("OUTPUT-side l121 paths:", outs)
print("(l121/static.json among them is an INPUT written by l121_static.py)")
print("INPUT paths:", ins)
if leftovers:
    print("ABORT: residual tokens survive")
    sys.exit(1)
open("l121_run.py", "w").write(SRC)
py_compile.compile("l121_run.py", doraise=True)
print("l121_run.py written + py_compile OK, lines:", SRC.count("\n") + 1)
