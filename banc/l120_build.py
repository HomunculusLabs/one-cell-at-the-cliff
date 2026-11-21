"""Build l120_run.py from l119_run.py via exact-string transforms.

Strategy: (1) docstring swap, (2) ARMS/GAIN header (10->9 arms), (3) stored
gain const for cutk3 (l119 fresh gain), (4) wholesale derivation-block swap
(ladder k3/k4a/k4b/k5 positional; r5 draw DELETED), (5) cutr5 slot removal
at every multi-arm site (build/wb/gi/pools/mech/motor/dng100/WB/N_OF/Xc/X/
noise/bisect-dict/tuples/savez/out), (6) NEW cutk3 stored-gain bisect block,
(7) NEW C0A-119 block (cutk3/cutk5 vs raw_l119 at 801/901), (8) seeds B14
1801-1816 -> B15 1901-1916 (+ l119 absence assert), (9) global renames
cutk1->cutk4a / cutk2->cutk4b / _k1->_k4a / _k2->_k4b, (10) output paths
l119->l120 (INPUT paths l113/l115/l117/l118/l119 kept — direction check),
(11) residual scan + direction check + py_compile. Every rep prints its
count; zero/mismatched count aborts (drift guard).
"""
import py_compile
import sys

SRC = open("l119_run.py").read()
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
rep('''"""L119 run: minimal-glut-subset-step. PREREG l119/PREREG.md FIRST.

L118 machinery VERBATIM (5-pair pools, graphs, gains, draw order); arms
full/b65/cut/cut19/cut58 retained as ANCHORS (stored seeds 801/901 vs
raw_l113) + NEW ladder arms cutk1/cutk2/cutk3/cutk5 = closure minus the
k HEAVIEST glutamatergic heavy cells (deterministic mass-desc filter, NO
RNG; l119/static.json pins; k5 == l117 stored EXACT) + draw arm cutr5 =
pinned-RNG random 5-of-19-glut (torch seed 1190, mass .0231, zero overlap
with the heaviest-5). Seeds: [801, 901] + FRESH B14 1801-1816 (asserted
absent from raw_l113 + l115 + l117 + l118). g_cut/g_cut19/g_cut58 AND
g_cutk5 re-bisected + asserted == stored EXACT; cutk1/cutk2/cutk3/cutr5
gains bisected FRESH (staircase + band DISCLOSED, never asserted).
CPU-only; raw checkpoint BEFORE analysis.
"""''',
    '''"""L120 run: cutk4-disambiguation. PREREG l120/PREREG.md FIRST.

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
"""''')

# 2. ARMS / GAIN header
rep('''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutk1", "cutk2", "cutk3", "cutk5", "cutr5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutk1=None, cutk2=None, cutk3=None, cutk5=None, cutr5=None)''',
    '''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutk3", "cutk4a", "cutk4b", "cutk5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutk3=None, cutk4a=None, cutk4b=None, cutk5=None)''')

# 3. stored-gain constant for cutk3 (l119 fresh gain)
rep('G_CUTK5_STORED = 0.13981970071792604  # l117 stored dose gain, C0A(k5)',
    '''G_CUTK5_STORED = 0.13981970071792604  # l117 stored dose gain, C0A(k5)
G_CUTK3_STORED = 0.17404209494590758  # l119 stored fresh gain, C0A(k3)''')

# 4. wholesale derivation-block swap (ladder + r5 draw OUT)
rep('''S119 = json.load(open("l119/static.json"))
NEW_ARMS = ("cutk1", "cutk2", "cutk3", "cutk5", "cutr5")
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
keep_cutk, n_cutk, cutk_drop, cutk_pins = {}, {}, {}, {}
for _kk, _a in ((1, "cutk1"), (2, "cutk2"), (3, "cutk3"), (5, "cutk5")):
    _pin = S119["ladder"][f"k{_kk}"]
    _drop = np.sort(glut_desc[:_kk])
    assert len(_drop) == _kk
    assert np.isin(_drop, cut19_drop).all(), "ladder drop not subset of glut-19"
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin
assert [int(x) for x in cutk_drop["cutk5"]] == [204, 286, 313, 561, 32014]
assert cutk_pins["cutk5"]["mass_removed"] == 0.0425, "k5 mass drift (STOP)"
_rp = S119["draw"]["cutr5"]
assert _rp["seed"] == 1190
_r5_drop = np.sort(np.array(_rp["drop_ids"], np.int64))
assert len(_r5_drop) == 5
assert np.isin(_r5_drop, cut19_drop).all(), "r5 draw not subset of glut-19"
assert is_glut[_r5_drop].all(), "non-glut cell in r5 draw (STOP)"
_r5_keep = keep_new.copy()
_r5_keep[_r5_drop] = False
assert int(_r5_keep.sum()) == _rp["n"], (int(_r5_keep.sum()), _rp["n"])
keep_cutk["cutr5"] = _r5_keep
n_cutk["cutr5"] = int(_r5_keep.sum())
cutk_drop["cutr5"] = _r5_drop
cutk_pins["cutr5"] = _rp
# (DNg100-not-in-heavy-77 asserted downstream in the dng100 section + pinned
# in l119/static.json — dng100_all is not yet defined at this point.)''',
    '''S120 = json.load(open("l120/static.json"))
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
# in l120/static.json — dng100_all is not yet defined at this point.)''')

# 5. cutr5 slot removal at every multi-arm site
rep('Wc_r5, loc_r5 = build(keep_cutk["cutr5"])\n', '')
rep('assert Wc_r5.values().numel() == cutk_pins["cutr5"]["edges"]\n', '')
rep('''Wb_k1, Wb_k2, Wb_k3, Wb_k5, Wb_r5 = (wb(Wc_k1), wb(Wc_k2), wb(Wc_k3),
                                    wb(Wc_k5), wb(Wc_r5))''',
    '''Wb_k1, Wb_k2, Wb_k3, Wb_k5 = (wb(Wc_k1), wb(Wc_k2), wb(Wc_k3), wb(Wc_k5))''')
rep('''gi_r5 = np.where(keep_cutk["cutr5"])[0]
r5_pos_in_new = loc_n[gi_r5]
old_pos_in_r5 = loc_r5[gi_old]
kept_new_mask_r5 = keep_cutk["cutr5"][new_g]
kept_new_cutr5 = loc_r5[new_g[kept_new_mask_r5]]
''', '')
rep('         "cutr5": pools_for(loc_r5, keep_cutk["cutr5"]),\n', '')
rep('("cutk1", "cutk2", "cutk3", "cutk5", "cutr5")',
    '("cutk3", "cutk4a", "cutk4b", "cutk5")', count=2)
rep('              "cutk5", "cutr5", "b65"):', '              "cutk5", "b65"):')
rep('        "cutr5": np.where(mech_mask[keep_cutk["cutr5"]])[0],\n', '')
rep('          ("cutr5", n_cutk["cutr5"]), ("b65", n_old))}',
    '          ("b65", n_old))}')
rep('                     ("cutr5", keep_cutk["cutr5"], loc_r5),\n', '')
rep('          "cutr5": np.sort(loc_r5[dng100_all[keep_cutk["cutr5"][dng100_all]]]),\n',
    '')
rep('''      "cutk1": Wb_k1, "cutk2": Wb_k2, "cutk3": Wb_k3, "cutk5": Wb_k5,
      "cutr5": Wb_r5, "b65": Wb_o}''',
    '''      "cutk1": Wb_k1, "cutk2": Wb_k2, "cutk3": Wb_k3, "cutk5": Wb_k5,
      "b65": Wb_o}''')
rep('        "cutr5": n_cutk["cutr5"], "b65": n_old}', '        "b65": n_old}')
rep('''    Xc_r5 = torch.zeros(n_cutk["cutr5"], 1)
    Xc_r5[old_pos_in_r5] = X0o
    Xc_r5[kept_new_cutr5] = X0n[kept_new_mask_r5]
''', '', count=2)
rep('cutr5=Xc_r5.clone(), b65=Xo65.clone())', 'b65=Xo65.clone())', count=2)
rep('                     cutr5=nzn[r5_pos_in_new], b65=nz_o)',
    '                     b65=nz_o)', count=3)
rep('''                                  cut58=g, cutk1=g, cutk2=g, cutk3=g,
                                  cutk5=g, cutr5=g))''',
    '''                                  cut58=g, cutk1=g, cutk2=g, cutk3=g,
                                  cutk5=g))''')
rep('("cutk1", "cutk2", "cutk3", "cutr5")', '("cutk1", "cutk2")', count=2)
rep('g_cutk3=GAIN["cutk3"], g_cutr5=GAIN["cutr5"],\n', 'g_cutk3=GAIN["cutk3"],\n')
rep('                    cutr5_drop=cutk_drop["cutr5"],\n', '')

# 6. NEW cutk3 stored-gain bisect block (after the cutk5 block)
rep('''log(f"g_cutk5 {lo4:.6f} == l117 stored EXACT | af_finalk5 {af_finalk5:.6f} "
    f"|af-target| {abs(af_finalk5 - AF_T):.2e} (staircase disclosed)")''',
    '''log(f"g_cutk5 {lo4:.6f} == l117 stored EXACT | af_finalk5 {af_finalk5:.6f} "
    f"|af-target| {abs(af_finalk5 - AF_T):.2e} (staircase disclosed)")

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
    f"|af-target| {abs(af_finalk3 - AF_T):.2e} (staircase disclosed)")''')

# 7. seeds: B14 -> B15, range, absence asserts (+ l119)
rep('B14 = list(range(1801, 1817))       # fresh, absent from l113/l115/l117/l118',
    'B15 = list(range(1901, 1917))       # fresh, absent l113/l115/l117/l118/l119')
rep('SEEDS = ANCH + B14                  # anchors FIRST: early wiring verdict',
    'SEEDS = ANCH + B15                  # anchors FIRST: early wiring verdict')
rep('FRESH = B14', 'FRESH = B15')
rep('''assert not any(f"mm_full_{s}" in zprev.files for s in B14), \\
    "B14 collides with stored batches (STOP)"''',
    '''assert not any(f"mm_full_{s}" in zprev.files for s in B15), \\
    "B15 collides with stored batches (STOP)"''')
rep('''for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",
              "l118/raw_l118.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B14), \\
        ("B14 collides with " + _prev + " (STOP)")''',
    '''for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",
              "l118/raw_l118.npz", "l119/raw_l119.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B15), \\
        ("B15 collides with " + _prev + " (STOP)")''')

# 8. NEW C0A-119 block (cutk3/cutk5 vs raw_l119 at stored seeds)
rep('''c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}''',
    '''# C0A-119 (NEW anchor class): cutk3/cutk5 at stored seeds vs raw_l119.
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
    f"(max {c0a119_max:.1e}, {len(C0A119_KEYS)} keys x 2 arms x 2 seeds)")
c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}''')

# 9. C0A excluded-arms log line (pre-rename form)
rep('''    f"| NEW arms excluded by name: ['cutk1','cutk2','cutk3','cutk5','cutr5']")''',
    '''    f"| NEW arms excluded (no l113 counterpart): ['cutk3','cutk4a','cutk4b',"
    "'cutk5'] | cutk3/cutk5 additionally C0A-anchored vs raw_l119")''')

# 10. out dict: new anchor booleans + c0a119
rep('           g_cutk5_stored_exact=bool(GAIN["cutk5"] == G_CUTK5_STORED),',
    '''           g_cutk5_stored_exact=bool(GAIN["cutk5"] == G_CUTK5_STORED),
           g_cutk3_stored_exact=bool(GAIN["cutk3"] == G_CUTK3_STORED),''')
rep('           af_finalk5=af_finalk5,', '           af_finalk5=af_finalk5, af_finalk3=af_finalk3,')
rep('''           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))''',
    '''           c0a_max=max(c0a.values()),
           c0a119_max=c0a119_max, c0a119_pass=c0a119_pass,
           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a119_pass))''')

# 11. output paths l119 -> l120 (INPUTS stay: l113/l115/l117/l118/l119)
rep('if os.path.exists("l119/raw_partial.npz"):', 'if os.path.exists("l120/raw_partial.npz"):')
rep('np.savez("l119/raw_partial.npz", **store)', 'np.savez("l120/raw_partial.npz", **store)')
rep('np.savez_compressed("l119/raw_l119.npz", K=K, g_cut=GAIN["cut"],',
    'np.savez_compressed("l120/raw_l120.npz", K=K, g_cut=GAIN["cut"],')
rep('log("raw_l119.npz checkpointed BEFORE analysis")',
    'log("raw_l120.npz checkpointed BEFORE analysis")')
rep('json.dump(out, open("l119/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l120/anchors_run.json", "w"), indent=1)')

# 12. global renames (LAST: arm tokens, then per-arm variable suffixes)
rep("cutk1", "cutk4a")
rep("cutk2", "cutk4b")
rep("_k1", "_k4a")
rep("_k2", "_k4b")

# 12b. final sweeps: leftover B14 comment + resume-load direction (L39 class)
rep("B14", "B15")
rep('np.load("l119/raw_partial.npz")', 'np.load("l120/raw_partial.npz")')

# 13. residual scan + file-path direction check
if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
bad_tokens = ["cutk1", "cutk2", "cutr5", "_r5", "cutnga", "1801", "B14",
              "S119"]
leftovers = {t: SRC.count(t) for t in bad_tokens if SRC.count(t)}
print("residual scan:", leftovers if leftovers else "CLEAN")
import re
paths = sorted(set(re.findall(r'np\.load\("([^"]+)"\)|open\("([^"]+)"\)',
                              SRC)))
paths = sorted({a or b for a, b in re.findall(
    r'np\.load\("([^"]+)"\)|open\("([^"]+)"\)', SRC)})
outs = [p for p in paths if p.startswith("l120")]
ins = [p for p in paths if not p.startswith("l120")]
print("OUTPUT paths:", outs)
print("INPUT paths:", ins)
if leftovers:
    print("ABORT: residual tokens survive")
    sys.exit(1)
open("l120_run.py", "w").write(SRC)
py_compile.compile("l120_run.py", doraise=True)
print("l120_run.py written + py_compile OK, lines:", SRC.count("\n") + 1)
