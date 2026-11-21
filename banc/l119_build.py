"""Build l119_run.py from l118_run.py via exact-string transforms.

Strategy: (1) docstring swap, (2) wholesale derivation-block swap (draws ->
k-ladder + pinned r5 draw), (3) global arm renames cutnga/cutngb/cutngc ->
cutk1/cutk2/cutr5 (+ stem renames), (4) ADD cutk3 + cutk5 slots at every
multi-arm site, (5) cutk5 stored-gain bisect block (l117 anchor class),
(6) seeds B13 -> B14 1801-1816 (+ l118 absence assert), (7) paths l118 ->
l119, (8) residual scan + file-path direction check. Every rep prints its
count; zero/mismatched count aborts (drift guard).
"""
import sys

SRC = open("l118_run.py").read()
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
rep('''"""L118 run: mass-matched-pure-nonglut-19. PREREG l118/PREREG.md FIRST.

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
"""''',
    '''"""L119 run: minimal-glut-subset-step. PREREG l119/PREREG.md FIRST.

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
"""''')

# 2. ARMS / GAIN header
rep('''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutnga", "cutngb", "cutngc"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutnga=None, cutngb=None, cutngc=None)''',
    '''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutk1", "cutk2", "cutk3", "cutk5", "cutr5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutk1=None, cutk2=None, cutk3=None, cutk5=None, cutr5=None)''')

# stored-gain constant for cutk5 (l117 dose_gains)
rep('G_CUT58_STORED = 0.15417299151420596  # l113 stored, PREREG C0A(c58)',
    '''G_CUT58_STORED = 0.15417299151420596  # l113 stored, PREREG C0A(c58)
G_CUTK5_STORED = 0.13981970071792604  # l117 stored dose gain, C0A(k5)''')

# 3. wholesale derivation-block swap
rep('''# L118: mass-matched PURE-NON-GLUT draws — 19-of-58 non-glutamatergic
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
# in l118/static.json — dng100_all is not yet defined at this point.)''',
    '''# L119: minimal glut subset — k HEAVIEST glut cells (deterministic
# mass-desc positional filter; l119/static.json pins; k5 asserted ==
# l117 stored) + pinned-RNG random 5-of-19-glut draw (seed 1190).
S119 = json.load(open("l119/static.json"))
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
# in l119/static.json — dng100_all is not yet defined at this point.)''')

# 4. global arm renames (then stems)
rep("cutnga", "cutk1")
rep("cutngb", "cutk2")
rep("cutngc", "cutr5")
rep("keep_cutng", "keep_cutk")
rep("n_cutng", "n_cutk")
rep("cutng_drop", "cutk_drop")
rep("ng_pins", "cutk_pins")
rep("ng_stairs", "new_stairs")
rep("ng_band_ok", "new_band_ok")
rep("ng_mass", "new_mass")
rep("_nga", "_k1")
rep("_ngb", "_k2")
rep("_ngc", "_r5")
rep("nga_pos_in_new", "k1_pos_in_new")
rep("ngb_pos_in_new", "k2_pos_in_new")
rep("ngc_pos_in_new", "r5_pos_in_new")

# 5. ADD cutk3 + cutk5 slots at every multi-arm site
# 5a. graph builds + edge asserts
rep('''Wc_k1, loc_k1 = build(keep_cutk["cutk1"])
Wc_k2, loc_k2 = build(keep_cutk["cutk2"])
Wc_r5, loc_r5 = build(keep_cutk["cutr5"])
assert Wc_k1.values().numel() == cutk_pins["cutk1"]["edges"]
assert Wc_k2.values().numel() == cutk_pins["cutk2"]["edges"]
assert Wc_r5.values().numel() == cutk_pins["cutr5"]["edges"]''',
    '''Wc_k1, loc_k1 = build(keep_cutk["cutk1"])
Wc_k2, loc_k2 = build(keep_cutk["cutk2"])
Wc_k3, loc_k3 = build(keep_cutk["cutk3"])
Wc_k5, loc_k5 = build(keep_cutk["cutk5"])
Wc_r5, loc_r5 = build(keep_cutk["cutr5"])
assert Wc_k1.values().numel() == cutk_pins["cutk1"]["edges"]
assert Wc_k2.values().numel() == cutk_pins["cutk2"]["edges"]
assert Wc_k3.values().numel() == cutk_pins["cutk3"]["edges"]
assert Wc_k5.values().numel() == cutk_pins["cutk5"]["edges"]
assert Wc_r5.values().numel() == cutk_pins["cutr5"]["edges"]''')
# 5b. Wb line
rep('Wb_k1, Wb_k2, Wb_r5 = wb(Wc_k1), wb(Wc_k2), wb(Wc_r5)',
    '''Wb_k1, Wb_k2, Wb_k3, Wb_k5, Wb_r5 = (wb(Wc_k1), wb(Wc_k2), wb(Wc_k3),
                                    wb(Wc_k5), wb(Wc_r5))''')
# 5c. gi blocks (insert k3/k5 blocks before the r5 block)
rep('''gi_r5 = np.where(keep_cutk["cutr5"])[0]
r5_pos_in_new = loc_n[gi_r5]''',
    '''gi_k3 = np.where(keep_cutk["cutk3"])[0]
k3_pos_in_new = loc_n[gi_k3]
old_pos_in_k3 = loc_k3[gi_old]
kept_new_mask_k3 = keep_cutk["cutk3"][new_g]
kept_new_cutk3 = loc_k3[new_g[kept_new_mask_k3]]
gi_k5 = np.where(keep_cutk["cutk5"])[0]
k5_pos_in_new = loc_n[gi_k5]
old_pos_in_k5 = loc_k5[gi_old]
kept_new_mask_k5 = keep_cutk["cutk5"][new_g]
kept_new_cutk5 = loc_k5[new_g[kept_new_mask_k5]]
gi_r5 = np.where(keep_cutk["cutr5"])[0]
r5_pos_in_new = loc_n[gi_r5]''')
# 5d. POOLS dict
rep('''         "cutk1": pools_for(loc_k1, keep_cutk["cutk1"]),
         "cutk2": pools_for(loc_k2, keep_cutk["cutk2"]),
         "cutr5": pools_for(loc_r5, keep_cutk["cutr5"]),''',
    '''         "cutk1": pools_for(loc_k1, keep_cutk["cutk1"]),
         "cutk2": pools_for(loc_k2, keep_cutk["cutk2"]),
         "cutk3": pools_for(loc_k3, keep_cutk["cutk3"]),
         "cutk5": pools_for(loc_k5, keep_cutk["cutk5"]),
         "cutr5": pools_for(loc_r5, keep_cutk["cutr5"]),''')
# 5e. pool-assert tuples
rep('''    for _da in ("cutk1", "cutk2", "cutr5"):
        assert len(POOLS[_da][pk]) == want, (_da, pk)''',
    '''    for _da in ("cutk1", "cutk2", "cutk3", "cutk5", "cutr5"):
        assert len(POOLS[_da][pk]) == want, (_da, pk)''')
rep('    for a in ("cut", "cut19", "cut58", "cutk1", "cutk2", "cutr5", "b65"):',
    '''    for a in ("cut", "cut19", "cut58", "cutk1", "cutk2", "cutk3",
              "cutk5", "cutr5", "b65"):''')
# 5f. mech dict
rep('''        "cutk1": np.where(mech_mask[keep_cutk["cutk1"]])[0],
        "cutk2": np.where(mech_mask[keep_cutk["cutk2"]])[0],
        "cutr5": np.where(mech_mask[keep_cutk["cutr5"]])[0],''',
    '''        "cutk1": np.where(mech_mask[keep_cutk["cutk1"]])[0],
        "cutk2": np.where(mech_mask[keep_cutk["cutk2"]])[0],
        "cutk3": np.where(mech_mask[keep_cutk["cutk3"]])[0],
        "cutk5": np.where(mech_mask[keep_cutk["cutk5"]])[0],
        "cutr5": np.where(mech_mask[keep_cutk["cutr5"]])[0],''')
# 5g. motor dict + loop tuple
rep('''         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cut58", n_cut58), ("cutk1", n_cutk["cutk1"]), ("cutk2", n_cutk["cutk2"]),
          ("cutr5", n_cutk["cutr5"]), ("b65", n_old))}''',
    '''         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cut58", n_cut58), ("cutk1", n_cutk["cutk1"]), ("cutk2", n_cutk["cutk2"]),
          ("cutk3", n_cutk["cutk3"]), ("cutk5", n_cutk["cutk5"]),
          ("cutr5", n_cutk["cutr5"]), ("b65", n_old))}''')
rep('''                     ("cutk1", keep_cutk["cutk1"], loc_k1),
                     ("cutk2", keep_cutk["cutk2"], loc_k2),
                     ("cutr5", keep_cutk["cutr5"], loc_r5),''',
    '''                     ("cutk1", keep_cutk["cutk1"], loc_k1),
                     ("cutk2", keep_cutk["cutk2"], loc_k2),
                     ("cutk3", keep_cutk["cutk3"], loc_k3),
                     ("cutk5", keep_cutk["cutk5"], loc_k5),
                     ("cutr5", keep_cutk["cutr5"], loc_r5),''')
# 5h. dng100 dict + loop
rep('''          "cutk1": np.sort(loc_k1[dng100_all[keep_cutk["cutk1"][dng100_all]]]),
          "cutk2": np.sort(loc_k2[dng100_all[keep_cutk["cutk2"][dng100_all]]]),
          "cutr5": np.sort(loc_r5[dng100_all[keep_cutk["cutr5"][dng100_all]]]),''',
    '''          "cutk1": np.sort(loc_k1[dng100_all[keep_cutk["cutk1"][dng100_all]]]),
          "cutk2": np.sort(loc_k2[dng100_all[keep_cutk["cutk2"][dng100_all]]]),
          "cutk3": np.sort(loc_k3[dng100_all[keep_cutk["cutk3"][dng100_all]]]),
          "cutk5": np.sort(loc_k5[dng100_all[keep_cutk["cutk5"][dng100_all]]]),
          "cutr5": np.sort(loc_r5[dng100_all[keep_cutk["cutr5"][dng100_all]]]),''')
rep('''for _da in ("cutk1", "cutk2", "cutr5"):
    assert len(dng100[_da]) == S92["dng100"], _da''',
    '''for _da in ("cutk1", "cutk2", "cutk3", "cutk5", "cutr5"):
    assert len(dng100[_da]) == S92["dng100"], _da''')
# 5i. WB / N_OF dicts
rep('''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "cutk1": Wb_k1, "cutk2": Wb_k2, "cutr5": Wb_r5, "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "cutk1": n_cutk["cutk1"], "cutk2": n_cutk["cutk2"], "cutr5": n_cutk["cutr5"],
        "b65": n_old}''',
    '''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "cutk1": Wb_k1, "cutk2": Wb_k2, "cutk3": Wb_k3, "cutk5": Wb_k5,
      "cutr5": Wb_r5, "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "cutk1": n_cutk["cutk1"], "cutk2": n_cutk["cutk2"],
        "cutk3": n_cutk["cutk3"], "cutk5": n_cutk["cutk5"],
        "cutr5": n_cutk["cutr5"], "b65": n_old}''')

# 6. settle_states: Xc blocks + st dict (BOTH the settle fn and the rollout
#    body have identical per-arm triplets — replace_all via count=2 pairs)
rep('''    Xc_k1 = torch.zeros(n_cutk["cutk1"], 1)
    Xc_k1[old_pos_in_k1] = X0o
    Xc_k1[kept_new_cutk1] = X0n[kept_new_mask_k1]
    Xc_k2 = torch.zeros(n_cutk["cutk2"], 1)
    Xc_k2[old_pos_in_k2] = X0o
    Xc_k2[kept_new_cutk2] = X0n[kept_new_mask_k2]
    Xc_r5 = torch.zeros(n_cutk["cutr5"], 1)
    Xc_r5[old_pos_in_r5] = X0o
    Xc_r5[kept_new_cutr5] = X0n[kept_new_mask_r5]''',
    '''    Xc_k1 = torch.zeros(n_cutk["cutk1"], 1)
    Xc_k1[old_pos_in_k1] = X0o
    Xc_k1[kept_new_cutk1] = X0n[kept_new_mask_k1]
    Xc_k2 = torch.zeros(n_cutk["cutk2"], 1)
    Xc_k2[old_pos_in_k2] = X0o
    Xc_k2[kept_new_cutk2] = X0n[kept_new_mask_k2]
    Xc_k3 = torch.zeros(n_cutk["cutk3"], 1)
    Xc_k3[old_pos_in_k3] = X0o
    Xc_k3[kept_new_cutk3] = X0n[kept_new_mask_k3]
    Xc_k5 = torch.zeros(n_cutk["cutk5"], 1)
    Xc_k5[old_pos_in_k5] = X0o
    Xc_k5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xc_r5 = torch.zeros(n_cutk["cutr5"], 1)
    Xc_r5[old_pos_in_r5] = X0o
    Xc_r5[kept_new_cutr5] = X0n[kept_new_mask_r5]''', count=2)
rep('''              cutk1=Xc_k1.clone(), cutk2=Xc_k2.clone(),
              cutr5=Xc_r5.clone(), b65=Xo65.clone())''',
    '''              cutk1=Xc_k1.clone(), cutk2=Xc_k2.clone(),
              cutk3=Xc_k3.clone(), cutk5=Xc_k5.clone(),
              cutr5=Xc_r5.clone(), b65=Xo65.clone())''')
rep('''             cutk1=Xc_k1.clone(), cutk2=Xc_k2.clone(),
             cutr5=Xc_r5.clone(), b65=Xo65.clone())''',
    '''             cutk1=Xc_k1.clone(), cutk2=Xc_k2.clone(),
             cutk3=Xc_k3.clone(), cutk5=Xc_k5.clone(),
             cutr5=Xc_r5.clone(), b65=Xo65.clone())''')

# 7. noise dicts (x3: settle, rollout-settle, win loop)
rep('''                     cutk1=nzn[k1_pos_in_new],
                     cutk2=nzn[k2_pos_in_new],
                     cutr5=nzn[r5_pos_in_new], b65=nz_o)''',
    '''                     cutk1=nzn[k1_pos_in_new],
                     cutk2=nzn[k2_pos_in_new],
                     cutk3=nzn[k3_pos_in_new],
                     cutk5=nzn[k5_pos_in_new],
                     cutr5=nzn[r5_pos_in_new], b65=nz_o)''')
# 8. bisect gains dict inside bisect_af_mean
rep('''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutk1=g, cutk2=g, cutr5=g))''',
    '''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutk1=g, cutk2=g, cutk3=g,
                                  cutk5=g, cutr5=g))''')

# 9. cutk5 stored-gain bisect block, inserted after the cut58 block
rep('''log(f"g_cut58 {lo3:.6f} == l113 stored EXACT | af_final58 {af_final58:.6f} "
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")''',
    '''log(f"g_cut58 {lo3:.6f} == l113 stored EXACT | af_final58 {af_final58:.6f} "
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")

# L119: cutk5 re-bisect must land on the stored l117 dose gain EXACT
lo4, hi4 = 0.12, 0.18
af_lo4, af_hi4 = bisect_af_mean(lo4, "cutk5"), bisect_af_mean(hi4, "cutk5")
log(f"cutk5 bracket af({lo4})={af_lo4:.5f} af({hi4})={af_hi4:.5f} "
    f"target {AF_T:.5f}")
assert af_lo4 < AF_T < af_hi4, "cutk5 bracket fail"
for it in range(24):
    mid = (lo4 + hi4) / 2
    if bisect_af_mean(mid, "cutk5") < AF_T:
        lo4 = mid
    else:
        hi4 = mid
GAIN["cutk5"] = lo4
af_finalk5 = bisect_af_mean(lo4, "cutk5")
assert GAIN["cutk5"] == G_CUTK5_STORED, (GAIN["cutk5"], G_CUTK5_STORED)
log(f"g_cutk5 {lo4:.6f} == l117 stored EXACT | af_finalk5 {af_finalk5:.6f} "
    f"|af-target| {abs(af_finalk5 - AF_T):.2e} (staircase disclosed)")''')

# 10. fresh-bisect loop: four arms (cutk5 excluded — stored-asserted above)
rep('for _a in ("cutk1", "cutk2", "cutr5"):', 'for _a in ("cutk1", "cutk2", "cutk3", "cutr5"):')

# 11. savez block
rep('''np.savez_compressed("l118/raw_l118.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
                    g_cutk1=GAIN["cutk1"], g_cutk2=GAIN["cutk2"],
                    g_cutr5=GAIN["cutr5"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    cutk1_drop=cutk_drop["cutk1"], cutk2_drop=cutk_drop["cutk2"],
                    cutr5_drop=cutk_drop["cutr5"],
                    new_mass=np.array([cutk_pins[a]["mass_removed"] for a in
                                      ("cutk1", "cutk2", "cutr5")]),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l118.npz checkpointed BEFORE analysis")''',
    '''np.savez_compressed("l119/raw_l119.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
                    g_cutk5=GAIN["cutk5"],
                    g_cutk1=GAIN["cutk1"], g_cutk2=GAIN["cutk2"],
                    g_cutk3=GAIN["cutk3"], g_cutr5=GAIN["cutr5"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    cutk1_drop=cutk_drop["cutk1"], cutk2_drop=cutk_drop["cutk2"],
                    cutk3_drop=cutk_drop["cutk3"], cutk5_drop=cutk_drop["cutk5"],
                    cutr5_drop=cutk_drop["cutr5"],
                    new_mass=np.array([cutk_pins[a]["mass_removed"] for a in NEW_ARMS]),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l119.npz checkpointed BEFORE analysis")''')

# 12. seeds B13 -> B14 + absence asserts
rep('B13 = list(range(1701, 1717))       # fresh, absent from l113/l115/l117',
    'B14 = list(range(1801, 1817))       # fresh, absent from l113/l115/l117/l118')
rep("SEEDS = ANCH + B13                  # anchors FIRST: early wiring verdict",
    "SEEDS = ANCH + B14                  # anchors FIRST: early wiring verdict")
rep("FRESH = B13", "FRESH = B14")
rep('''# B13 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B13), \\
    "B13 collides with stored batches (STOP)"
for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B13), \\
        ("B13 collides with " + _prev + " (STOP)")''',
    '''# B14 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B14), \\
    "B14 collides with stored batches (STOP)"
for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",
              "l118/raw_l118.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B14), \\
        ("B14 collides with " + _prev + " (STOP)")''')

# 13. remaining paths l118 -> l119 (raw_partial load+exists+save, anchors)
rep('if os.path.exists("l118/raw_partial.npz"):', 'if os.path.exists("l119/raw_partial.npz"):')
rep('z = np.load("l118/raw_partial.npz")', 'z = np.load("l119/raw_partial.npz")')
rep('np.savez("l118/raw_partial.npz", **store)', 'np.savez("l119/raw_partial.npz", **store)')
rep('json.dump(out, open("l118/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l119/anchors_run.json", "w"), indent=1)')

# 14. NEW-arms exclusion log + out dict
rep('''    f"| NEW arms excluded by name: ['cutk1','cutk2','cutr5']")''',
    '''    f"| NEW arms excluded by name: ['cutk1','cutk2','cutk3','cutk5','cutr5']")''')
rep('''out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           g_cut58_stored_exact=bool(GAIN["cut58"] == G_CUT58_STORED),
           g_cutk1=GAIN["cutk1"], g_cutk2=GAIN["cutk2"],
           g_cutr5=GAIN["cutr5"], new_stairs=new_stairs,
           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutk1", "cutk2", "cutr5"))),
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           K=K, mass_split=mass_split, n_seeds=len(SEEDS),
           new_mass={a: cutk_pins[a]["mass_removed"] for a in NG_ARMS},
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))''',
    '''out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           g_cut58_stored_exact=bool(GAIN["cut58"] == G_CUT58_STORED),
           g_cutk5_stored_exact=bool(GAIN["cutk5"] == G_CUTK5_STORED),
           g_cutk1=GAIN["cutk1"], g_cutk2=GAIN["cutk2"],
           g_cutk3=GAIN["cutk3"], g_cutr5=GAIN["cutr5"],
           new_stairs=new_stairs,
           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutk1", "cutk2", "cutk3", "cutr5"))),
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           af_finalk5=af_finalk5,
           K=K, mass_split=mass_split, n_seeds=len(SEEDS),
           new_mass={a: cutk_pins[a]["mass_removed"] for a in NEW_ARMS},
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))''')

# 15. residual scan — no old token may remain. 'l118' is allowed ONLY as
# the deliberate prior-run references: the absence-assert npz path and the
# two docstring provenance mentions.
_allowed = ("l118/raw_l118.npz", "L118 machinery VERBATIM",
            "l113 + l115 + l117 + l118", "l113/l115/l117/l118")
_scrub = SRC
for _a in _allowed:
    _scrub = _scrub.replace(_a, "")
LEFTOVER = [t for t in ("cutng", "nga", "ngb", "ngc", "ng_pins", "ng_stairs",
                        "ng_band", "ng_mass", "NG_ARMS", "S118", "B13",
                        "1701", "l118", "Xc_nga") if t in _scrub]
if LEFTOVER:
    print(f"RESIDUAL OLD TOKENS: {sorted(set(LEFTOVER))}")
    for i, line in enumerate(_scrub.split("\\n"), 1):
        if any(t in line for t in LEFTOVER):
            print(f"  {i} | {line[:110]}")
    n_err += 1
else:
    print("residual scan clean: no old tokens remain")

# 16. file-path direction check (L118 lesson): every npz literal must be
# either a PRIOR-run input (l113/l115/l117/l118 raw) or THIS run's output
# (l119/...). Print them for eyeball verification.
import re
_paths = sorted(set(re.findall(r'"(l1\\d\\d/[^"]+\\.npz)"', SRC)))
for _p in _paths:
    _dir = "OUTPUT(this-run)" if _p.startswith("l119/") else "INPUT(prior-run)"
    print(f"path {_p}: {_dir}")

if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
open("l119_run.py", "w").write(SRC)
print("l119_run.py written OK")
