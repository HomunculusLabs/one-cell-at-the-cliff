"""l131_build.py — asserted exact-string transform l126_run.py -> l131_run.py.

L131 run: rank-25/26 completion XOR on FRESH B24. Arms: cutng25 (NEW,
wA + rank 25 only) + ng23/wA/ng26 (now stored-form) + endpoints/skeleton.
cutng21/cutng28 dropped (l126 single-batch points, disclosed).
Every rep count-asserted; residual scan for stale tokens on CODE lines
(comments/docstrings whitelisted by line context, l126 refinement form);
np.load/savez direction check (input vs output paths); py_compile gate.
"""
import py_compile

SRC = open("l126_run.py").read()
n_reps = 0


def rep(old, new, count=1):
    global SRC, n_reps
    c = SRC.count(old)
    assert c == count, f"rep count {c} != {count}: {old[:70]!r}"
    SRC = SRC.replace(old, new)
    n_reps += 1


# 1: docstring (span)
i0 = SRC.index('"""')
i1 = SRC.index('"""', i0 + 3) + 3
NEW_DOC = '''"""L131 run: rank-25/26 COMPLETION XOR on FRESH B24. PREREG
l131/PREREG.md FIRST (cutng25 = ng_desc[:25] = wA + rank 25 (id 1110)
ONLY; if k25 SUPERs/RESTORES -> 1110 completes; if PARTIAL -> rank 26
(id 319) completes; registered degenerate branch X3 = neither).

L126 machinery VERBATIM (pools, graphs, draw order) — cutng21/cutng28
NOT run (l126 single-batch interpolation points stand, DISCLOSED);
cutng23/cutwA/cutng26 stored-form (l126 fresh gains -> stored consts,
re-bisect EXACT); cutng25 the ONE fresh bisect (staircase + .14-.16
band DISCLOSED, never abort). FRESH B24 2801-2816 (asserted absent
from raw_l113 + l115 + l117 + l118 + l119 + l120 + l121 + l122 + l123
+ l124 + l125 + l126 + l127 + l128). Anchors: C0A/C0A-120..125
retained, C0A-126 EXTENDED to all 9 shared cut arms vs raw_l126, NEW
C0A-127 (6 arms) + C0A-128 (6 arms) forward chains. CPU-only; raw
checkpoint BEFORE analysis.
"""'''
SRC = NEW_DOC + SRC[i1:]
n_reps += 1

# 2: ARMS
rep('ARMS = ["full", "b65", "cut", "cut19", "cut58",\n'
    '        "cutng19", "cutng21", "cutng23", "cutwA", "cutng26", "cutng28",\n'
    '        "cutng29", "cutk5"]',
    'ARMS = ["full", "b65", "cut", "cut19", "cut58",\n'
    '        "cutng19", "cutng23", "cutwA", "cutng25", "cutng26",\n'
    '        "cutng29", "cutk5"]')
# 3: GAIN dict
rep('GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,\n'
    '            cutng19=None, cutng21=None, cutng23=None, cutwA=None,\n'
    '            cutng26=None, cutng28=None, cutng29=None, cutk5=None)',
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,\n'
    '            cutng19=None, cutng23=None, cutwA=None, cutng25=None,\n'
    '            cutng26=None, cutng29=None, cutk5=None)')
# 4: stored consts (ng23/ng26 promoted stored-form)
rep('# (L126: cutwB stored const removed — arm not run here; C0A-123 is\n'
    '# retained on the 4 shared arms only.)',
    'G_CUTNG23_STORED = 0.14696856379508969  # l126 fresh gain -> stored-form\n'
    'G_CUTNG26_STORED = 0.14545363783836368  # l126 fresh gain -> stored-form\n'
    '# (L131: cutng21/cutng28 not run — l126 single-batch points stand,\n'
    '# DISCLOSED; C0A-123 retained on the 4 shared arms.)')
# 5: batch
rep('B21 = list(range(2501, 2517))  # fresh, absent l113..l125 incl raw_l125\n'
    'SEEDS = ANCH + B21                  # anchors FIRST: early wiring verdict\n'
    'FRESH = B21',
    'B24 = list(range(2801, 2817))  # fresh, absent l113..l128 incl raw_l128\n'
    'SEEDS = ANCH + B24                  # anchors FIRST: early wiring verdict\n'
    'FRESH = B24')
# 6: static pin source
rep('S126 = json.load(open("l126/static.json"))',
    'S131 = json.load(open("l131/static.json"))')
# 7: NEW_ARMS
rep('NEW_ARMS = ("cutk5", "cutng19", "cutng21", "cutng23", "cutwA",\n'
    '            "cutng26", "cutng28", "cutng29")',
    'NEW_ARMS = ("cutk5", "cutng19", "cutng23", "cutwA", "cutng25",\n'
    '            "cutng26", "cutng29")')
# 8: prefix loop comment + tuple + pin source
rep('# L126 nested prefixes (l126/static.json pins): ng_desc[:k] for k in\n'
    '# {21,23,24,26,28}; cutwA == ng_desc[:24] re-pinned == l123 stored\n'
    '# (extraction regression). Strictly nested by construction; DNg100 in\n'
    '# no drop.',
    '# L131 prefixes (l131/static.json pins): ng_desc[:k] for k in\n'
    '# {23,24,25,26}; cutng25 = wA + rank 25 (id 1110) ONLY — the XOR arm;\n'
    '# cutng23/wA/cutng26 re-pinned == l126/l123 stored EXACT. Strictly\n'
    '# nested by construction; DNg100 in no drop.')
rep('for _a, _k in (("cutng21", 21), ("cutng23", 23), ("cutwA", 24),\n'
    '               ("cutng26", 26), ("cutng28", 28)):',
    'for _a, _k in (("cutng23", 23), ("cutwA", 24), ("cutng25", 25),\n'
    '               ("cutng26", 26)):')
rep('    _pin = S126["prefix"][_a]',
    '    _pin = S131["prefix"][_a]')
# 9: pins assert tuple
rep('for _a, _m, _e in (\n'
    '    ("cutng21", 0.2086, 644509),\n'
    '    ("cutng23", 0.222, 644282),\n'
    '    ("cutng26", 0.2411, 643979),\n'
    '    ("cutng28", 0.2529, 643725),\n'
    '):',
    'for _a, _m, _e in (\n'
    '    ("cutng23", 0.222, 644282),\n'
    '    ("cutng25", 0.235, 644084),\n'
    '    ("cutng26", 0.2411, 643979),\n'
    '):')
# 10: build calls
rep('Wc_p21, loc_p21 = build(keep_cutk["cutng21"])\n'
    'Wc_p23, loc_p23 = build(keep_cutk["cutng23"])\n'
    'Wc_p26, loc_p26 = build(keep_cutk["cutng26"])\n'
    'Wc_p28, loc_p28 = build(keep_cutk["cutng28"])',
    'Wc_p23, loc_p23 = build(keep_cutk["cutng23"])\n'
    'Wc_p25, loc_p25 = build(keep_cutk["cutng25"])\n'
    'Wc_p26, loc_p26 = build(keep_cutk["cutng26"])')
# 11: Wc numel assert loop
rep('for _a, _W in (("cutng21", Wc_p21), ("cutng23", Wc_p23),\n'
    '               ("cutng26", Wc_p26), ("cutng28", Wc_p28)):',
    'for _a, _W in (("cutng25", Wc_p25), ("cutng23", Wc_p23),\n'
    '               ("cutng26", Wc_p26)):')
# 11b: POOLS dict entries
rep('         "cutng21": pools_for(loc_p21, keep_cutk["cutng21"]),\n'
    '         "cutng23": pools_for(loc_p23, keep_cutk["cutng23"]),\n'
    '         "cutng26": pools_for(loc_p26, keep_cutk["cutng26"]),\n'
    '         "cutng28": pools_for(loc_p28, keep_cutk["cutng28"]),',
    '         "cutng25": pools_for(loc_p25, keep_cutk["cutng25"]),\n'
    '         "cutng23": pools_for(loc_p23, keep_cutk["cutng23"]),\n'
    '         "cutng26": pools_for(loc_p26, keep_cutk["cutng26"]),')
# 11c: pool-size _da loop (4-space, inside pool-size for)
rep('    for _da in ("cutwA", "cutng21", "cutng23", "cutng26", "cutng28",\n'
    '                "cutng19", "cutng29", "cutk5"):',
    '    for _da in ("cutwA", "cutng25", "cutng23", "cutng26",\n'
    '                "cutng19", "cutng29", "cutk5"):')
# 11d: NEW pools arm list (6/14-space)
rep('    for a in ("cut", "cut19", "cut58", "cutng19", "cutng21", "cutng23",\n'
    '              "cutwA", "cutng26", "cutng28", "cutng29", "cutk5", "b65"):',
    '    for a in ("cut", "cut19", "cut58", "cutng19", "cutng23", "cutwA",\n'
    '              "cutng25", "cutng26", "cutng29", "cutk5", "b65"):')
# 11e: mech dict
rep('        "cutng21": np.where(mech_mask[keep_cutk["cutng21"]])[0],\n'
    '        "cutng23": np.where(mech_mask[keep_cutk["cutng23"]])[0],\n'
    '        "cutng26": np.where(mech_mask[keep_cutk["cutng26"]])[0],\n'
    '        "cutng28": np.where(mech_mask[keep_cutk["cutng28"]])[0],',
    '        "cutng25": np.where(mech_mask[keep_cutk["cutng25"]])[0],\n'
    '        "cutng23": np.where(mech_mask[keep_cutk["cutng23"]])[0],\n'
    '        "cutng26": np.where(mech_mask[keep_cutk["cutng26"]])[0],')
# 11f: motor n_of dict
rep('          ("cutwA", n_cutk["cutwA"]), ("cutng21", n_cutk["cutng21"]),\n'
    '          ("cutng23", n_cutk["cutng23"]), ("cutng26", n_cutk["cutng26"]),\n'
    '          ("cutng28", n_cutk["cutng28"]),',
    '          ("cutwA", n_cutk["cutwA"]), ("cutng25", n_cutk["cutng25"]),\n'
    '          ("cutng23", n_cutk["cutng23"]), ("cutng26", n_cutk["cutng26"]),')
# 11g: motor loop tuples
rep('                     ("cutng21", keep_cutk["cutng21"], loc_p21),\n'
    '                     ("cutng23", keep_cutk["cutng23"], loc_p23),\n'
    '                     ("cutng26", keep_cutk["cutng26"], loc_p26),\n'
    '                     ("cutng28", keep_cutk["cutng28"], loc_p28),',
    '                     ("cutng25", keep_cutk["cutng25"], loc_p25),\n'
    '                     ("cutng23", keep_cutk["cutng23"], loc_p23),\n'
    '                     ("cutng26", keep_cutk["cutng26"], loc_p26),')
# 11h: dng100 dict
rep('          "cutng21": np.sort(loc_p21[dng100_all[keep_cutk["cutng21"][dng100_all]]]),\n'
    '          "cutng23": np.sort(loc_p23[dng100_all[keep_cutk["cutng23"][dng100_all]]]),\n'
    '          "cutng26": np.sort(loc_p26[dng100_all[keep_cutk["cutng26"][dng100_all]]]),\n'
    '          "cutng28": np.sort(loc_p28[dng100_all[keep_cutk["cutng28"][dng100_all]]]),',
    '          "cutng25": np.sort(loc_p25[dng100_all[keep_cutk["cutng25"][dng100_all]]]),\n'
    '          "cutng23": np.sort(loc_p23[dng100_all[keep_cutk["cutng23"][dng100_all]]]),\n'
    '          "cutng26": np.sort(loc_p26[dng100_all[keep_cutk["cutng26"][dng100_all]]]),')
# 12: Wb tuple
rep('Wb_ng19, Wb_ng29, Wb_wA, Wb_p21, Wb_p23, Wb_p26, Wb_p28, Wb_k5 = (\n'
    '    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_p21), wb(Wc_p23),\n'
    '    wb(Wc_p26), wb(Wc_p28), wb(Wc_k5))',
    'Wb_ng19, Wb_ng29, Wb_wA, Wb_p23, Wb_p25, Wb_p26, Wb_k5 = (\n'
    '    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_p23), wb(Wc_p25),\n'
    '    wb(Wc_p26), wb(Wc_k5))')
# 13: gi_p21 block -> gi_p25
rep('gi_p21 = np.where(keep_cutk["cutng21"])[0]\n'
    'p21_pos_in_new = loc_n[gi_p21]\n'
    'old_pos_in_p21 = loc_p21[gi_old]\n'
    'kept_new_mask_p21 = keep_cutk["cutng21"][new_g]\n'
    'kept_new_cutcutng21 = loc_p21[new_g[kept_new_mask_p21]]',
    'gi_p25 = np.where(keep_cutk["cutng25"])[0]\n'
    'p25_pos_in_new = loc_n[gi_p25]\n'
    'old_pos_in_p25 = loc_p25[gi_old]\n'
    'kept_new_mask_p25 = keep_cutk["cutng25"][new_g]\n'
    'kept_new_cutcutng25 = loc_p25[new_g[kept_new_mask_p25]]')
# 14: gi_p28 block delete
rep('gi_p28 = np.where(keep_cutk["cutng28"])[0]\n'
    'p28_pos_in_new = loc_n[gi_p28]\n'
    'old_pos_in_p28 = loc_p28[gi_old]\n'
    'kept_new_mask_p28 = keep_cutk["cutng28"][new_g]\n'
    'kept_new_cutcutng28 = loc_p28[new_g[kept_new_mask_p28]]\n',
    '')
# 15: Xc_p21 -> Xc_p25 (settle_states + seed loop: 2 sites, same text)
rep('    Xc_p21 = torch.zeros(n_cutk["cutng21"], 1)\n'
    '    Xc_p21[old_pos_in_p21] = X0o\n'
    '    Xc_p21[kept_new_cutcutng21] = X0n[kept_new_mask_p21]',
    '    Xc_p25 = torch.zeros(n_cutk["cutng25"], 1)\n'
    '    Xc_p25[old_pos_in_p25] = X0o\n'
    '    Xc_p25[kept_new_cutcutng25] = X0n[kept_new_mask_p25]', count=2)
# 16: Xc_p28 delete (2 sites)
rep('    Xc_p28 = torch.zeros(n_cutk["cutng28"], 1)\n'
    '    Xc_p28[old_pos_in_p28] = X0o\n'
    '    Xc_p28[kept_new_cutcutng28] = X0n[kept_new_mask_p28]\n',
    '', count=2)
# 17: settle X dict (14-space)
rep('    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),\n'
    '              cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),\n'
    '              cutwA=Xc_wA.clone(), cutng21=Xc_p21.clone(),\n'
    '              cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),\n'
    '              cutng28=Xc_p28.clone(), cutk5=Xc_k5.clone(),\n'
    '              b65=Xo65.clone())',
    '    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),\n'
    '              cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),\n'
    '              cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),\n'
    '              cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),\n'
    '              cutk5=Xc_k5.clone(),\n'
    '              b65=Xo65.clone())')
# 18: dng100 assert loop
rep('for _da in ("cutwA", "cutng21", "cutng23", "cutng26", "cutng28",\n'
    '            "cutng19", "cutng29", "cutk5"):',
    'for _da in ("cutwA", "cutng25", "cutng23", "cutng26",\n'
    '            "cutng19", "cutng29", "cutk5"):')
# 19: WB dict
rep('WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,\n'
    '      "cutng19": Wb_ng19, "cutng29": Wb_ng29, "cutwA": Wb_wA,\n'
    '      "cutng21": Wb_p21, "cutng23": Wb_p23, "cutng26": Wb_p26,\n'
    '      "cutng28": Wb_p28, "cutk5": Wb_k5,\n'
    '      "b65": Wb_o}',
    'WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,\n'
    '      "cutng19": Wb_ng19, "cutng29": Wb_ng29, "cutwA": Wb_wA,\n'
    '      "cutng25": Wb_p25, "cutng23": Wb_p23, "cutng26": Wb_p26,\n'
    '      "cutk5": Wb_k5,\n'
    '      "b65": Wb_o}')
# 20: N_OF dict
rep('        "cutwA": n_cutk["cutwA"], "cutng21": n_cutk["cutng21"],\n'
    '        "cutng23": n_cutk["cutng23"], "cutng26": n_cutk["cutng26"],\n'
    '        "cutng28": n_cutk["cutng28"],\n'
    '        "cutk5": n_cutk["cutk5"],',
    '        "cutwA": n_cutk["cutwA"], "cutng25": n_cutk["cutng25"],\n'
    '        "cutng23": n_cutk["cutng23"], "cutng26": n_cutk["cutng26"],\n'
    '        "cutk5": n_cutk["cutk5"],')
# 21: noise dict entries (3 dicts each)
rep('                     cutng21=nzn[p21_pos_in_new],\n',
    '                     cutng25=nzn[p25_pos_in_new],\n', count=3)
rep('                     cutng28=nzn[p28_pos_in_new],\n', '', count=3)
# 22: seed-loop X dict (13-space)
rep('    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),\n'
    '             cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),\n'
    '             cutwA=Xc_wA.clone(), cutng21=Xc_p21.clone(),\n'
    '             cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),\n'
    '             cutng28=Xc_p28.clone(), cutk5=Xc_k5.clone(),\n'
    '             b65=Xo65.clone())',
    '    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),\n'
    '             cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),\n'
    '             cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),\n'
    '             cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),\n'
    '             cutk5=Xc_k5.clone(),\n'
    '             b65=Xo65.clone())')
# 23: raw_partial paths (3 sites: load x2-guard + savez)
rep('"l126/raw_partial.npz"', '"l131/raw_partial.npz"', count=3)
# 24: bisect stored-form loop
rep('for _a in ("cutng19", "cutng29", "cutwA"):',
    'for _a in ("cutng19", "cutng29", "cutwA", "cutng23", "cutng26"):')
rep('    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,\n'
    '           "cutwA": G_CUTWA_STORED}[_a]',
    '    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,\n'
    '           "cutwA": G_CUTWA_STORED, "cutng23": G_CUTNG23_STORED,\n'
    '           "cutng26": G_CUTNG26_STORED}[_a]')
# 24b: bisect gains-dict signature
rep('                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,\n'
    '                                  cutng21=g, cutng23=g, cutng26=g,\n'
    '                                  cutng28=g, cutk5=g))',
    '                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,\n'
    '                                  cutng25=g, cutng23=g, cutng26=g,\n'
    '                                  cutk5=g))')
# 25: fresh bisect loop
rep('# L126 FRESH bisects: interpolation prefixes (staircase + band\n'
    '# DISCLOSED per PREREG — the .14-.16 band is a disclosure, never an\n'
    '# abort).\n'
    'for _a in ("cutng21", "cutng23", "cutng26", "cutng28"):',
    '# L131 FRESH bisect: cutng25 only (staircase + band DISCLOSED per\n'
    '# PREREG — the .14-.16 band is a disclosure, never an abort).\n'
    'for _a in ("cutng25",):')
# 26: stored-form loop comment (mentions endpoints+wA only)
rep('# L126 form: endpoint + wA gains are STORED-FORM anchors (re-bisect\n'
    '# EXACT, l121/l123); the 4 interpolation prefixes are FRESH bisects\n'
    '# below. Staircase + band disclosures retained per PREREG (never abort).',
    '# L131 form: endpoint + wA + ng23/ng26 gains are STORED-FORM anchors\n'
    '# (re-bisect EXACT, l121/l123/l126); cutng25 is the ONE fresh bisect\n'
    '# below. Staircase + band disclosures retained per PREREG (never abort).')
# 27: savez header + checkpoint log
rep('np.savez_compressed("l126/raw_l126.npz", K=K, g_cut=GAIN["cut"],',
    'np.savez_compressed("l131/raw_l131.npz", K=K, g_cut=GAIN["cut"],')
rep('log("raw_l126.npz checkpointed BEFORE analysis")',
    'log("raw_l131.npz checkpointed BEFORE analysis")')
# 28: savez gain kwargs
rep('                    g_cutwA=GAIN["cutwA"], g_cutng21=GAIN["cutng21"],\n'
    '                    g_cutng23=GAIN["cutng23"], g_cutng26=GAIN["cutng26"],\n'
    '                    g_cutng28=GAIN["cutng28"],',
    '                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],\n'
    '                    g_cutng23=GAIN["cutng23"], g_cutng26=GAIN["cutng26"],')
# 29: savez drop kwargs
rep('                    cutng21_drop=cutk_drop["cutng21"],\n'
    '                    cutng23_drop=cutk_drop["cutng23"],\n'
    '                    cutng26_drop=cutk_drop["cutng26"],\n'
    '                    cutng28_drop=cutk_drop["cutng28"],',
    '                    cutng25_drop=cutk_drop["cutng25"],\n'
    '                    cutng23_drop=cutk_drop["cutng23"],\n'
    '                    cutng26_drop=cutk_drop["cutng26"],')
# 30: batch-absence block
rep('# B21 is fresh: no stored counterpart (asserted absent pre-C0A)\n'
    'assert not any(f"mm_full_{s}" in zprev.files for s in B21), \\\n'
    '    "B21 collides with stored batches (STOP)"\n'
    'for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",\n'
    '              "l118/raw_l118.npz", "l119/raw_l119.npz",\n'
    '              "l120/raw_l120.npz", "l121/raw_l121.npz",\n'
    '              "l122/raw_l122.npz", "l123/raw_l123.npz",\n'
    '              "l124/raw_l124.npz", "l125/raw_l125.npz"):\n'
    '    _zp = np.load(_prev)\n'
    '    assert not any(f"mm_full_{s}" in _zp.files for s in B21), \\\n'
    '        ("B21 collides with " + _prev + " (STOP)")',
    '# B24 is fresh: no stored counterpart (asserted absent pre-C0A)\n'
    'assert not any(f"mm_full_{s}" in zprev.files for s in B24), \\\n'
    '    "B24 collides with stored batches (STOP)"\n'
    'for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",\n'
    '              "l118/raw_l118.npz", "l119/raw_l119.npz",\n'
    '              "l120/raw_l120.npz", "l121/raw_l121.npz",\n'
    '              "l122/raw_l122.npz", "l123/raw_l123.npz",\n'
    '              "l124/raw_l124.npz", "l125/raw_l125.npz",\n'
    '              "l126/raw_l126.npz", "l127/raw_l127.npz",\n'
    '              "l128/raw_l128.npz"):\n'
    '    _zp = np.load(_prev)\n'
    '    assert not any(f"mm_full_{s}" in _zp.files for s in B24), \\\n'
    '        ("B24 collides with " + _prev + " (STOP)")')
# 31: NEW anchor classes after C0A-125 block
rep('log(f"C0A-125 forward chain vs raw_l125: {\'PASS\' if c0a125_pass else \'FAIL\'} "\n'
    '    f"(max {c0a125_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")',
    'log(f"C0A-125 forward chain vs raw_l125: {\'PASS\' if c0a125_pass else \'FAIL\'} "\n'
    '    f"(max {c0a125_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")\n'
    '# C0A-126 EXTENDED (L131 PREREG): ALL 9 shared cut arms with l126\n'
    '# (cutng21/cutng28 not run here — excluded by name, DISCLOSED).\n'
    'z126c = np.load("l126/raw_l126.npz")\n'
    '_arms126 = ("cut", "cut19", "cut58", "cutk5", "cutng19", "cutng23",\n'
    '            "cutwA", "cutng26", "cutng29")\n'
    'c0a126 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A120_KEYS:\n'
    '        for a in _arms126:\n'
    '            c0a126[f"126_{key}_{a}_{s}"] = float(np.abs(\n'
    '                store[f"{key}_{a}_{s}"] - z126c[f"{key}_{a}_{s}"][:WIN]).max())\n'
    '    for a in _arms126:\n'
    '        c0a126[f"126_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])\n'
    '                                        - float(z126c[f"af_{a}_{s}"]))\n'
    'c0a126_max = max(c0a126.values())\n'
    'c0a126_pass = bool(all(v == 0.0 for v in c0a126.values()))\n'
    'log(f"C0A-126 EXTENDED (9 shared cut arms) vs raw_l126: "\n'
    '    f"{\'PASS\' if c0a126_pass else \'FAIL\'} "\n'
    '    f"(max {c0a126_max:.1e}, {len(C0A120_KEYS)} keys x 9 arms x 2 seeds)")\n'
    '# C0A-127 (NEW): 6 shared cut arms vs raw_l127 (scr/cl arms excluded).\n'
    'z127c = np.load("l127/raw_l127.npz")\n'
    '_arms127 = ("cut", "cut19", "cut58", "cutk5", "cutng19", "cutng29")\n'
    'c0a127 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A120_KEYS:\n'
    '        for a in _arms127:\n'
    '            c0a127[f"127_{key}_{a}_{s}"] = float(np.abs(\n'
    '                store[f"{key}_{a}_{s}"] - z127c[f"{key}_{a}_{s}"][:WIN]).max())\n'
    '    for a in _arms127:\n'
    '        c0a127[f"127_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])\n'
    '                                        - float(z127c[f"af_{a}_{s}"]))\n'
    'c0a127_max = max(c0a127.values())\n'
    'c0a127_pass = bool(all(v == 0.0 for v in c0a127.values()))\n'
    'log(f"C0A-127 forward chain vs raw_l127: {\'PASS\' if c0a127_pass else \'FAIL\'} "\n'
    '    f"(max {c0a127_max:.1e}, {len(C0A120_KEYS)} keys x 6 arms x 2 seeds)")\n'
    '# C0A-128 (NEW): same 6 shared cut arms vs raw_l128 (scr excluded).\n'
    'z128c = np.load("l128/raw_l128.npz")\n'
    'c0a128 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A120_KEYS:\n'
    '        for a in _arms127:\n'
    '            c0a128[f"128_{key}_{a}_{s}"] = float(np.abs(\n'
    '                store[f"{key}_{a}_{s}"] - z128c[f"{key}_{a}_{s}"][:WIN]).max())\n'
    '    for a in _arms127:\n'
    '        c0a128[f"128_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])\n'
    '                                        - float(z128c[f"af_{a}_{s}"]))\n'
    'c0a128_max = max(c0a128.values())\n'
    'c0a128_pass = bool(all(v == 0.0 for v in c0a128.values()))\n'
    'log(f"C0A-128 forward chain vs raw_l128: {\'PASS\' if c0a128_pass else \'FAIL\'} "\n'
    '    f"(max {c0a128_max:.1e}, {len(C0A120_KEYS)} keys x 6 arms x 2 seeds)")')
# 32: c0a_new_pools log line token
rep('    f"| NEW arms excluded (no l113 counterpart): [\'cutk5\',\'cutng19\',\'cutng29\',\"\n'
    '    "\'cutng21\'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120)")',
    '    f"| NEW arms excluded (no l113 counterpart): [\'cutk5\',\'cutng19\',\'cutng29\',\"\n'
    '    "\'cutng25\'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120)")')
# 33: anchors out dict gains
rep('           g_cutwA=GAIN["cutwA"], g_cutng21=GAIN["cutng21"],\n'
    '           g_cutng23=GAIN["cutng23"], g_cutng26=GAIN["cutng26"],\n'
    '           g_cutng28=GAIN["cutng28"],\n'
    '           new_stairs=new_stairs,',
    '           g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],\n'
    '           g_cutng23=GAIN["cutng23"], g_cutng26=GAIN["cutng26"],\n'
    '           new_stairs=new_stairs,')
rep('           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16\n'
    '                                 for a in ("cutng21", "cutng23", "cutng26",\n'
    '                                           "cutng28"))),',
    '           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16\n'
    '                                 for a in ("cutng25",))),')
rep('           c0a125_max=c0a125_max, c0a125_pass=c0a125_pass,\n'
    '           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),\n'
    '           prefix_fresh_gains={a: GAIN[a] for a in\n'
    '                               ("cutng21", "cutng23", "cutng26",\n'
    '                                "cutng28")},',
    '           c0a125_max=c0a125_max, c0a125_pass=c0a125_pass,\n'
    '           c0a126_max=c0a126_max, c0a126_pass=c0a126_pass,\n'
    '           c0a127_max=c0a127_max, c0a127_pass=c0a127_pass,\n'
    '           c0a128_max=c0a128_max, c0a128_pass=c0a128_pass,\n'
    '           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),\n'
    '           g_cutng23_stored_exact=bool(GAIN["cutng23"] == G_CUTNG23_STORED),\n'
    '           g_cutng26_stored_exact=bool(GAIN["cutng26"] == G_CUTNG26_STORED),\n'
    '           prefix_fresh_gains={a: GAIN[a] for a in ("cutng25",)},')
rep('           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass\n'
    '                          and c0a121_pass and c0a122_pass and c0a123_pass\n'
    '                          and c0a124_pass and c0a125_pass))',
    '           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass\n'
    '                          and c0a121_pass and c0a122_pass and c0a123_pass\n'
    '                          and c0a124_pass and c0a125_pass and c0a126_pass\n'
    '                          and c0a127_pass and c0a128_pass))')
# 34: anchors file path
rep('json.dump(out, open("l126/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l131/anchors_run.json", "w"), indent=1)')

# ---------------- residual scan (code lines only) ----------------
STALE = ["cutng21", "cutng28", "p21", "p28", "B21", "l126/", "raw_l126",
         "S126", "2501", "2601", "2701"]
bad = []
in_doc = False
for ln, line in enumerate(SRC.split("\n"), 1):
    st = line.strip()
    if st.startswith('"""') or (st.endswith('"""') and st.count('"""') % 2):
        in_doc = not in_doc if st.count('"""') == 1 else in_doc
        continue
    if in_doc or st.startswith("#"):
        continue
    for t in STALE:
        if t in line:
            # whitelist by LINE CONTEXT (l126 refinement form): prior-run
            # INPUT reads of raw_l126 (np.load / absence tuple / C0A-126
            # log) are deliberate cross-references, never code survivors.
            if t in ("l126/", "raw_l126") and (
                    "np.load" in line or "collides" in line
                    or "C0A-126" in line or "raw_l127" in line):
                continue
            bad.append((ln, t, line.strip()[:80]))
assert not bad, f"STALE tokens on code lines: {bad[:8]}"

# ---------------- direction check (input vs output paths) ----------------
loads = [l.strip() for l in SRC.split("\n") if "np.load(" in l]
saves = [l.strip() for l in SRC.split("\n") if "np.savez" in l]
out_files = [l for l in saves if "raw_l131" in l or "raw_partial" in l]
assert all("l131/" in l for l in out_files), out_files
# every np.load of a raw_ file must point at a PRIOR run's dir or own resume
for l in loads:
    assert ("raw_l1" not in l) or ("l131/raw_partial" in l
                                   or "l11" in l or "l12" in l), l

open("l131_run.py", "w").write(SRC)
py_compile.compile("l131_run.py", doraise=True)
print(f"l131_run.py written: {n_reps} reps, residual scan clean, "
      f"direction check clean, py_compile OK")
