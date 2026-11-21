"""L133 build: count-asserted exact-string transform of l131_run.py ->
l133_run.py and l131_verdict.py -> l133_verdict.py (PREREG l133/PREREG.md
FIRST). Every rep count-pinned; residual token scan at the end; py_compile
both outputs. Zero tolerance: a count miss aborts BEFORE any rollout."""
import py_compile


def apply(src, reps, tag):
    for old, new, cnt in reps:
        n = src.count(old)
        assert n == cnt, (tag, "count miss", cnt, n, old[:70])
        src = src.replace(old, new)
    return src


run = open("l131_run.py").read()

R = []

# ---- docstring ----
R.append((
    '"""L131 run: rank-25/26 COMPLETION XOR on FRESH B24. PREREG\n'
    'l131/PREREG.md FIRST (cutng25 = ng_desc[:25] = wA + rank 25 (id 1110)\n'
    'ONLY; if k25 SUPERs/RESTORES -> 1110 completes; if PARTIAL -> rank 26\n'
    '(id 319) completes; registered degenerate branch X3 = neither).',
    '"""L133 run: wA-plus-319-ALONE XOR on FRESH B25. PREREG\n'
    'l133/PREREG.md FIRST (cutng25p = wA + rank 26 (id 319) ONLY — NOT a\n'
    'prefix, skips rank 25/id 1110; if 25p PARTIALs -> clean identity XOR\n'
    'at mass-match; if SUPERs -> flip position-thin, both cells complete;\n'
    'registered degenerate branch W3 = neither).', 1))
R.append((
    'L126 machinery VERBATIM (pools, graphs, draw order) — cutng21/cutng28\n'
    'NOT run (l126 single-batch interpolation points stand, DISCLOSED);\n'
    'cutng23/cutwA/cutng26 stored-form (l126 fresh gains -> stored consts,\n'
    're-bisect EXACT); cutng25 the ONE fresh bisect (staircase + .14-.16\n'
    'band DISCLOSED, never abort). FRESH B24 2801-2816 (asserted absent\n'
    'from raw_l113 + l115 + l117 + l118 + l119 + l120 + l121 + l122 + l123\n'
    '+ l124 + l125 + l126 + l127 + l128). Anchors: C0A/C0A-120..125\n'
    'retained, C0A-126 EXTENDED to all 9 shared cut arms vs raw_l126, NEW\n'
    'C0A-127 (6 arms) + C0A-128 (6 arms) forward chains. CPU-only; raw\n'
    'checkpoint BEFORE analysis.\n'
    '"""',
    'L131 machinery VERBATIM (pools, graphs, draw order) — cutng25 now\n'
    'stored-form (l131 fresh gain); cutng25p the ONE fresh bisect\n'
    '(staircase + .14-.16 band DISCLOSED, never abort). FRESH B25\n'
    '2901-2916 (asserted absent from raw_l113 + l115 + l117 + l118 +\n'
    'l119 + l120 + l121 + l122 + l123 + l124 + l125 + l126 + l127 +\n'
    'l128 + l131). Anchors: C0A/C0A-120..128 retained, NEW C0A-131 (10\n'
    'shared cut arms vs raw_l131) forward chain. CPU-only; raw checkpoint\n'
    'BEFORE analysis.\n'
    '"""', 1))

# ---- ARMS / GAIN ----
R.append((
    'ARMS = ["full", "b65", "cut", "cut19", "cut58",\n'
    '        "cutng19", "cutng23", "cutwA", "cutng25", "cutng26",\n'
    '        "cutng29", "cutk5"]',
    'ARMS = ["full", "b65", "cut", "cut19", "cut58",\n'
    '        "cutng19", "cutng23", "cutwA", "cutng25", "cutng25p",\n'
    '        "cutng26", "cutng29", "cutk5"]', 1))
R.append((
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,\n'
    '            cutng19=None, cutng23=None, cutwA=None, cutng25=None,\n'
    '            cutng26=None, cutng29=None, cutk5=None)',
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,\n'
    '            cutng19=None, cutng23=None, cutwA=None, cutng25=None,\n'
    '            cutng25p=None, cutng26=None, cutng29=None, cutk5=None)',
    1))
R.append((
    'G_CUTNG26_STORED = 0.14545363783836368  # l126 fresh gain -> stored-form',
    'G_CUTNG26_STORED = 0.14545363783836368  # l126 fresh gain -> stored-form\n'
    'G_CUTNG25_STORED = 0.1454454553127289  # l131 fresh gain -> stored-form (C0A-131)',
    1))
R.append((
    'B24 = list(range(2801, 2817))  # fresh, absent l113..l128 incl raw_l128',
    'B25 = list(range(2901, 2917))  # fresh, absent l113..l131 incl raw_l131',
    1))

# ---- static loads + NEW_ARMS ----
R.append((
    'S121 = json.load(open("l121/static.json"))\n'
    'S131 = json.load(open("l131/static.json"))\n'
    'NEW_ARMS = ("cutk5", "cutng19", "cutng23", "cutwA", "cutng25",\n'
    '            "cutng26", "cutng29")',
    'S121 = json.load(open("l121/static.json"))\n'
    'S131 = json.load(open("l131/static.json"))\n'
    'S133 = json.load(open("l133/static.json"))\n'
    'NEW_ARMS = ("cutk5", "cutng19", "cutng23", "cutwA", "cutng25",\n'
    '            "cutng25p", "cutng26", "cutng29")', 1))

# ---- the 25p static pin block (insert before the k5 drop assert) ----
R.append((
    'assert [int(x) for x in cutk_drop["cutk5"]] == [204, 286, 313, 561, 32014]',
    '# L133 XOR arm: cutng25p = wA + rank 26 (id 319) ONLY — NOT a prefix\n'
    '# (skips rank 25 / id 1110); pins from l133/static.json (static-first).\n'
    '_pin25p = S133["xor25p"]["cutng25p"]\n'
    '_drop25p = np.sort(np.concatenate([ng_desc[:24], ng_desc[25:26]]))\n'
    'assert _pin25p["drop_ids"] == [int(x) for x in _drop25p], \\\n'
    '    "cutng25p drop drift (STOP)"\n'
    'assert np.isin(_drop25p, cut58_drop).all()\n'
    '_keep25p = keep_new.copy()\n'
    '_keep25p[_drop25p] = False\n'
    'assert int(_keep25p.sum()) == _pin25p["n"], ("cutng25p", int(_keep25p.sum()))\n'
    'keep_cutk["cutng25p"] = _keep25p\n'
    'n_cutk["cutng25p"] = int(_keep25p.sum())\n'
    'cutk_drop["cutng25p"] = _drop25p\n'
    'cutk_pins["cutng25p"] = _pin25p\n'
    'assert [int(x) for x in cutk_drop["cutk5"]] == [204, 286, 313, 561, 32014]',
    1))

# ---- mass/edges pin tuple ----
R.append((
    'for _a, _m, _e in (\n'
    '    ("cutng23", 0.222, 644282),\n'
    '    ("cutng25", 0.235, 644084),\n'
    '    ("cutng26", 0.2411, 643979),\n'
    '):',
    'for _a, _m, _e in (\n'
    '    ("cutng23", 0.222, 644282),\n'
    '    ("cutng25", 0.235, 644084),\n'
    '    ("cutng25p", 0.2346, 644072),\n'
    '    ("cutng26", 0.2411, 643979),\n'
    '):', 1))

# ---- Wc/Wb builds ----
R.append((
    'Wc_p25, loc_p25 = build(keep_cutk["cutng25"])',
    'Wc_p25, loc_p25 = build(keep_cutk["cutng25"])\n'
    'Wc_p25p, loc_p25p = build(keep_cutk["cutng25p"])', 1))
R.append((
    'for _a, _W in (("cutng25", Wc_p25), ("cutng23", Wc_p23),\n'
    '               ("cutng26", Wc_p26)):',
    'for _a, _W in (("cutng25", Wc_p25), ("cutng25p", Wc_p25p),\n'
    '               ("cutng23", Wc_p23), ("cutng26", Wc_p26)):', 1))
R.append((
    'Wb_ng19, Wb_ng29, Wb_wA, Wb_p23, Wb_p25, Wb_p26, Wb_k5 = (\n'
    '    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_p23), wb(Wc_p25),\n'
    '    wb(Wc_p26), wb(Wc_k5))',
    'Wb_ng19, Wb_ng29, Wb_wA, Wb_p23, Wb_p25, Wb_p25p, Wb_p26, Wb_k5 = (\n'
    '    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_p23), wb(Wc_p25),\n'
    '    wb(Wc_p25p), wb(Wc_p26), wb(Wc_k5))', 1))

# ---- gi/pos block ----
R.append((
    'gi_p25 = np.where(keep_cutk["cutng25"])[0]\n'
    'p25_pos_in_new = loc_n[gi_p25]\n'
    'old_pos_in_p25 = loc_p25[gi_old]\n'
    'kept_new_mask_p25 = keep_cutk["cutng25"][new_g]\n'
    'kept_new_cutcutng25 = loc_p25[new_g[kept_new_mask_p25]]',
    'gi_p25 = np.where(keep_cutk["cutng25"])[0]\n'
    'p25_pos_in_new = loc_n[gi_p25]\n'
    'old_pos_in_p25 = loc_p25[gi_old]\n'
    'kept_new_mask_p25 = keep_cutk["cutng25"][new_g]\n'
    'kept_new_cutcutng25 = loc_p25[new_g[kept_new_mask_p25]]\n'
    'gi_p25p = np.where(keep_cutk["cutng25p"])[0]\n'
    'p25p_pos_in_new = loc_n[gi_p25p]\n'
    'old_pos_in_p25p = loc_p25p[gi_old]\n'
    'kept_new_mask_p25p = keep_cutk["cutng25p"][new_g]\n'
    'kept_new_cutcutng25p = loc_p25p[new_g[kept_new_mask_p25p]]', 1))

# ---- POOLS + pool-size tuples ----
R.append((
    '         "cutng25": pools_for(loc_p25, keep_cutk["cutng25"]),',
    '         "cutng25": pools_for(loc_p25, keep_cutk["cutng25"]),\n'
    '         "cutng25p": pools_for(loc_p25p, keep_cutk["cutng25p"]),', 1))
R.append((
    '    for _da in ("cutwA", "cutng25", "cutng23", "cutng26",\n'
    '                "cutng19", "cutng29", "cutk5"):',
    '    for _da in ("cutwA", "cutng25", "cutng25p", "cutng23", "cutng26",\n'
    '                "cutng19", "cutng29", "cutk5"):', 1))
R.append((
    '    for a in ("cut", "cut19", "cut58", "cutng19", "cutng23", "cutwA",\n'
    '              "cutng25", "cutng26", "cutng29", "cutk5", "b65"):',
    '    for a in ("cut", "cut19", "cut58", "cutng19", "cutng23", "cutwA",\n'
    '              "cutng25", "cutng25p", "cutng26", "cutng29", "cutk5",\n'
    '              "b65"):', 1))

# ---- mech / motor / dng100 / WB / N_OF ----
R.append((
    '        "cutng25": np.where(mech_mask[keep_cutk["cutng25"]])[0],',
    '        "cutng25": np.where(mech_mask[keep_cutk["cutng25"]])[0],\n'
    '        "cutng25p": np.where(mech_mask[keep_cutk["cutng25p"]])[0],', 1))
R.append((
    '          ("cutwA", n_cutk["cutwA"]), ("cutng25", n_cutk["cutng25"]),',
    '          ("cutwA", n_cutk["cutwA"]), ("cutng25", n_cutk["cutng25"]),\n'
    '          ("cutng25p", n_cutk["cutng25p"]),', 1))
R.append((
    '                     ("cutng25", keep_cutk["cutng25"], loc_p25),',
    '                     ("cutng25", keep_cutk["cutng25"], loc_p25),\n'
    '                     ("cutng25p", keep_cutk["cutng25p"], loc_p25p),', 1))
R.append((
    '          "cutng25": np.sort(loc_p25[dng100_all[keep_cutk["cutng25"][dng100_all]]]),',
    '          "cutng25": np.sort(loc_p25[dng100_all[keep_cutk["cutng25"][dng100_all]]]),\n'
    '          "cutng25p": np.sort(loc_p25p[dng100_all[keep_cutk["cutng25p"][dng100_all]]]),',
    1))
R.append((
    'for _da in ("cutwA", "cutng25", "cutng23", "cutng26",\n'
    '            "cutng19", "cutng29", "cutk5"):',
    'for _da in ("cutwA", "cutng25", "cutng25p", "cutng23", "cutng26",\n'
    '            "cutng19", "cutng29", "cutk5"):', 1))
R.append((
    '      "cutng25": Wb_p25, "cutng23": Wb_p23, "cutng26": Wb_p26,',
    '      "cutng25": Wb_p25, "cutng25p": Wb_p25p, "cutng23": Wb_p23,\n'
    '      "cutng26": Wb_p26,', 1))
R.append((
    '        "cutwA": n_cutk["cutwA"], "cutng25": n_cutk["cutng25"],',
    '        "cutwA": n_cutk["cutwA"], "cutng25": n_cutk["cutng25"],\n'
    '        "cutng25p": n_cutk["cutng25p"],', 1))

# ---- settle Xc block (settle fn + rollout: SAME text, 2 sites) ----
R.append((
    '    Xc_p25 = torch.zeros(n_cutk["cutng25"], 1)\n'
    '    Xc_p25[old_pos_in_p25] = X0o\n'
    '    Xc_p25[kept_new_cutcutng25] = X0n[kept_new_mask_p25]',
    '    Xc_p25 = torch.zeros(n_cutk["cutng25"], 1)\n'
    '    Xc_p25[old_pos_in_p25] = X0o\n'
    '    Xc_p25[kept_new_cutcutng25] = X0n[kept_new_mask_p25]\n'
    '    Xc_p25p = torch.zeros(n_cutk["cutng25p"], 1)\n'
    '    Xc_p25p[old_pos_in_p25p] = X0o\n'
    '    Xc_p25p[kept_new_cutcutng25p] = X0n[kept_new_mask_p25p]', 2))
R.append((
    '              cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),',
    '              cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),\n'
    '              cutng25p=Xc_p25p.clone(),', 1))
# rollout X dict (13-space twin of the st-dict line — anchor on the
# OPENER or the 13-space substring ALSO matches the 14-space st line;
# the l131 per-site lesson: count-pin EVERY true site)
R.append((
    '    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),\n'
    '             cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),\n'
    '             cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),',
    '    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),\n'
    '             cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),\n'
    '             cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),\n'
    '             cutng25p=Xc_p25p.clone(),', 1))

# ---- noise dicts (settle + rollout-settle + rollout-WIN: 3 sites) ----
R.append((
    '                     cutng25=nzn[p25_pos_in_new],',
    '                     cutng25=nzn[p25_pos_in_new],\n'
    '                     cutng25p=nzn[p25p_pos_in_new],', 3))

# ---- bisect gains dict ----
R.append((
    '        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,\n'
    '                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,\n'
    '                                  cutng25=g, cutng23=g, cutng26=g,\n'
    '                                  cutk5=g))',
    '        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,\n'
    '                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,\n'
    '                                  cutng25=g, cutng25p=g, cutng23=g,\n'
    '                                  cutng26=g, cutk5=g))', 1))

# ---- stored loop + fresh loop ----
R.append((
    '# L131 form: endpoint + wA + ng23/ng26 gains are STORED-FORM anchors\n'
    '# (re-bisect EXACT, l121/l123/l126); cutng25 is the ONE fresh bisect\n'
    '# below. Staircase + band disclosures retained per PREREG (never abort).\n'
    'new_stairs = {}\n'
    'for _a in ("cutng19", "cutng29", "cutwA", "cutng23", "cutng26"):',
    '# L133 form: endpoint + wA + ng23/ng25/ng26 gains are STORED-FORM\n'
    '# anchors (re-bisect EXACT, l121/l123/l126/l131); cutng25p is the ONE\n'
    '# fresh bisect below. Staircase + band disclosures retained per PREREG\n'
    '# (never abort).\n'
    'new_stairs = {}\n'
    'for _a in ("cutng19", "cutng29", "cutwA", "cutng23", "cutng25",\n'
    '           "cutng26"):', 1))
R.append((
    '    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,\n'
    '           "cutwA": G_CUTWA_STORED, "cutng23": G_CUTNG23_STORED,\n'
    '           "cutng26": G_CUTNG26_STORED}[_a]',
    '    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,\n'
    '           "cutwA": G_CUTWA_STORED, "cutng23": G_CUTNG23_STORED,\n'
    '           "cutng25": G_CUTNG25_STORED,\n'
    '           "cutng26": G_CUTNG26_STORED}[_a]', 1))
R.append((
    '# L131 FRESH bisect: cutng25 only (staircase + band DISCLOSED per\n'
    '# PREREG — the .14-.16 band is a disclosure, never an abort).\n'
    'for _a in ("cutng25",):',
    '# L133 FRESH bisect: cutng25p only (staircase + band DISCLOSED per\n'
    '# PREREG — the .14-.16 band is a disclosure, never an abort).\n'
    'for _a in ("cutng25p",):', 1))

# ---- paths ----
R.append(('if os.path.exists("l131/raw_partial.npz"):',
          'if os.path.exists("l133/raw_partial.npz"):', 1))
R.append(('    z = np.load("l131/raw_partial.npz")',
          '    z = np.load("l133/raw_partial.npz")', 1))
R.append(('    np.savez("l131/raw_partial.npz", **store)',
          '    np.savez("l133/raw_partial.npz", **store)', 1))
R.append(('np.savez_compressed("l131/raw_l131.npz", K=K, g_cut=GAIN["cut"],',
          'np.savez_compressed("l133/raw_l133.npz", K=K, g_cut=GAIN["cut"],', 1))
R.append(('log("raw_l131.npz checkpointed BEFORE analysis")',
          'log("raw_l133.npz checkpointed BEFORE analysis")', 1))
R.append(('json.dump(out, open("l131/anchors_run.json", "w"), indent=1)',
          'json.dump(out, open("l133/anchors_run.json", "w"), indent=1)', 1))

# ---- savez payload ----
R.append((
    '                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],',
    '                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],\n'
    '                    g_cutng25p=GAIN["cutng25p"],', 1))
R.append((
    '                    cutng25_drop=cutk_drop["cutng25"],',
    '                    cutng25_drop=cutk_drop["cutng25"],\n'
    '                    cutng25p_drop=cutk_drop["cutng25p"],', 1))

# ---- absence tuple gains raw_l131 ----
R.append((
    '              "l126/raw_l126.npz", "l127/raw_l127.npz",\n'
    '              "l128/raw_l128.npz"):',
    '              "l126/raw_l126.npz", "l127/raw_l127.npz",\n'
    '              "l128/raw_l128.npz", "l131/raw_l131.npz"):', 1))

# ---- C0A-131 block (insert before c0a_new_pools) ----
R.append((
    'c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}',
    '# C0A-131 (NEW): 10 shared cut arms vs raw_l131 (l131 ran every arm\n'
    '# at all 18 seeds; cutng25p has NO stored counterpart — excluded by name).\n'
    'z131c = np.load("l131/raw_l131.npz")\n'
    '_arms131 = ("cut", "cut19", "cut58", "cutk5", "cutng19", "cutng23",\n'
    '            "cutwA", "cutng25", "cutng26", "cutng29")\n'
    'c0a131 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A120_KEYS:\n'
    '        for a in _arms131:\n'
    '            c0a131[f"131_{key}_{a}_{s}"] = float(np.abs(\n'
    '                store[f"{key}_{a}_{s}"] - z131c[f"{key}_{a}_{s}"][:WIN]).max())\n'
    '    for a in _arms131:\n'
    '        c0a131[f"131_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])\n'
    '                                        - float(z131c[f"af_{a}_{s}"]))\n'
    'c0a131_max = max(c0a131.values())\n'
    'c0a131_pass = bool(all(v == 0.0 for v in c0a131.values()))\n'
    'log(f"C0A-131 forward chain vs raw_l131: {\'PASS\' if c0a131_pass else \'FAIL\'} "\n'
    '    f"(max {c0a131_max:.1e}, {len(C0A120_KEYS)} keys x 10 arms x 2 seeds)")\n'
    'c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}', 1))

# ---- out dict fields (anchored on sibling line: the 11-space form is a
# ---- SUBSTRING of the savez 20-space line — l123 un-anchored hazard) ----
R.append((
    '           g_cutng19=GAIN["cutng19"], g_cutng29=GAIN["cutng29"],\n'
    '           g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],',
    '           g_cutng19=GAIN["cutng19"], g_cutng29=GAIN["cutng29"],\n'
    '           g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],\n'
    '           g_cutng25p=GAIN["cutng25p"],\n'
    '           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),',
    1))
R.append((
    '           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16\n'
    '                                 for a in ("cutng25",))),',
    '           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16\n'
    '                                 for a in ("cutng25p",))),', 1))
R.append((
    '           c0a128_max=c0a128_max, c0a128_pass=c0a128_pass,',
    '           c0a128_max=c0a128_max, c0a128_pass=c0a128_pass,\n'
    '           c0a131_max=c0a131_max, c0a131_pass=c0a131_pass,', 1))
R.append((
    '           prefix_fresh_gains={a: GAIN[a] for a in ("cutng25",)},',
    '           prefix_fresh_gains={a: GAIN[a] for a in ("cutng25p",)},', 1))
R.append((
    '           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass\n'
    '                          and c0a121_pass and c0a122_pass and c0a123_pass\n'
    '                          and c0a124_pass and c0a125_pass and c0a126_pass\n'
    '                          and c0a127_pass and c0a128_pass))',
    '           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass\n'
    '                          and c0a121_pass and c0a122_pass and c0a123_pass\n'
    '                          and c0a124_pass and c0a125_pass and c0a126_pass\n'
    '                          and c0a127_pass and c0a128_pass\n'
    '                          and c0a131_pass))', 1))

# ---- cosmetic comment (new-arms excluded list) ----
R.append((
    '    f"| NEW arms excluded (no l113 counterpart): [\'cutk5\',\'cutng19\',\'cutng29\',"\n'
    '    "\'cutng25\'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120)")',
    '    f"| NEW arms excluded (no l113 counterpart): [\'cutk5\',\'cutng19\',\'cutng29\',"\n'
    '    "\'cutng25\',\'cutng25p\'] | cutk5 additionally C0A-anchored vs raw_l120"\n'
    '    " (C0A-120)")', 1))

run = apply(run, R, "run")

# global B24 -> B25 for all remaining sites (7: SEEDS/FRESH lines,
# 2 comments, 2 asserts, 1 collision message)
n = run.count("B24")
assert n == 7, ("global B24 count miss", n)
run = run.replace("B24", "B25")

# residual scan: no stale tokens that should not survive
for bad in ('"l131/raw_partial', "l131/raw_l131.npz\", K=K",
            "l131/anchors_run.json"):
    assert bad not in run, ("stale token", bad)
# raw_l131 references that REMAIN must be deliberate reads of the prior
# run (np.load input) or the absence-tuple entry — whitelist by LINE
# CONTEXT (code np.load / absence tuple / comment / docstring region),
# never by enumerating tokens (l126 refinement)
for i, line in enumerate(run.splitlines()):
    if "raw_l131" in line:
        in_comment = line.split("#", 1)[1] if "#" in line else ""
        assert ("np.load" in line or '"l131/raw_l131.npz"' in line
                or "l131 ran every arm" in line
                or "raw_l131" in in_comment
                or "forward chain vs raw_l131" in line
                or line.lstrip().startswith("#") or i < 16), \
            ("unwhitelisted", i, line)
# every per-arm plumbing block must carry 25p beside 25 (spot-grep)
for probe in ('"cutng25p": pools_for', '"cutng25p": Wb_p25p',
              'cutng25p=nzn[p25p_pos_in_new]', 'cutng25p=Xc_p25p.clone()',
              '("cutng25p", keep_cutk["cutng25p"], loc_p25p)',
              'g_cutng25p=GAIN'):
    n = run.count(probe)
    assert n >= 1, ("missing plumbing", probe)
assert run.count("cutng25p=Xc_p25p.clone(),") == 2, \
    "Xc clone sites must be exactly 2 (settle st dict + rollout X dict)"
assert run.count("cutng25p=nzn[p25p_pos_in_new],") == 3, \
    "noise dict sites must be exactly 3 (settle + rollout x2)"

open("l133_run.py", "w").write(run)
py_compile.compile("l133_run.py", doraise=True)
print(f"l133_run.py written ({len(run.splitlines())} lines) + py_compile OK")

# ================= VERDICT TRANSFORM =================
v = open("l131_verdict.py").read()
V = []
V.append((
    '"""L131 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +\n'
    'B23-cert of this machinery on raw_l128 vs results_l128.json (ALL its\n'
    'table arms) BEFORE any B24 read, then the registered XOR reads on FRESH\n'
    'B24 (criteria VERBATIM): X1 cutng25 SUPER/RESTORE -> rank 25 (id 1110)\n'
    'completes; X2 cutng25 PARTIAL -> rank 26 (id 319) completes; X3\n'
    'registered degenerate branch (kill/out-of-band -> NEITHER single cell;\n'
    'the {1110,319} pair stays the unit). P2 mass-twin disclosure (static\n'
    'pins). P3 pooled transition arms {ng23, wA, ng26, ng29} B21+B24 n=32\n'
    'full-precision Wilson (L132 prebase). S1 cutk5 12th batch pooled R4\n'
    'B16..B24 n=144; S2 endpoints 9th batch (dR-leg disclosure); S3 wA\n'
    'partial 4th batch; per-side duty table 5 pairs x 12 arms; Ti_L/Tr_R/Sr_R\n'
    'watch; sanity cells. PREREG l131/PREREG.md."""',
    '"""L133 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +\n'
    'B24-cert of this machinery on raw_l131 vs results_l131.json (ALL its\n'
    'table arms) BEFORE any B25 read, then the registered XOR reads on FRESH\n'
    'B25 (criteria VERBATIM): W1 cutng25p PARTIAL -> clean identity XOR at\n'
    'mass-match (1110 completes, 319 does not); W2 cutng25p SUPER/RESTORE ->\n'
    'flip position-thin, BOTH cells complete; W3 registered degenerate\n'
    'branch. P2 mass-twin disclosure (static pins). P3 pooled transition\n'
    'arms {ng23, wA, ng26, ng29} B21+B24+B25 n=48 Wilson; ng25 2nd batch\n'
    'n=32 (X1 replication). S1 cutk5 13th batch pooled B16..B25 n=160;\n'
    'S2 endpoints 10th batch; S3 wA partial 5th batch; S4 ng25 SUPER 2nd\n'
    'batch; per-side duty table 5 pairs x 13 arms; Ti_L/Tr_R/Sr_R watch;\n'
    'sanity cells. PREREG l133/PREREG.md."""', 1))
V.append((
    'B24 = list(range(2801, 2817))       # FRESH (l131)',
    'B25 = list(range(2901, 2917))       # FRESH (l133)\n'
    'B24 = list(range(2801, 2817))  # context batch (l131, cert + pooled)',
    1))
V.append((
    'z131 = np.load("l131/raw_l131.npz")',
    'z131 = np.load("l131/raw_l131.npz")\n'
    'z133 = np.load("l133/raw_l133.npz")', 1))
V.append((
    'ar = json.load(open("l131/anchors_run.json"))',
    'ar = json.load(open("l133/anchors_run.json"))\n'
    'r131 = json.load(open("l131/results_l131.json"))', 1))
V.append((
    'S131 = json.load(open("l131/static.json"))',
    'S131 = json.load(open("l131/static.json"))\n'
    'S133 = json.load(open("l133/static.json"))', 1))
V.append((
    'NEW_ARMS = ["cutk5", "cutng19", "cutng23", "cutwA", "cutng25", "cutng26",\n'
    '            "cutng29"]\n'
    'ARMS = STORED_ARMS + NEW_ARMS\n'
    'LADDER = [("0", "full"), ("19", "cutng19"), ("23", "cutng23"),\n'
    '          ("24", "cutwA"), ("25", "cutng25"), ("26", "cutng26"),\n'
    '          ("29", "cutng29"), ("58", "cut58"),\n'
    '          ("k5", "cutk5")]\n'
    'CURVE = ["19", "23", "24", "25", "26", "29"]   # registered curve',
    'NEW_ARMS = ["cutk5", "cutng19", "cutng23", "cutwA", "cutng25",\n'
    '            "cutng25p", "cutng26", "cutng29"]\n'
    'ARMS = STORED_ARMS + NEW_ARMS\n'
    'LADDER = [("0", "full"), ("19", "cutng19"), ("23", "cutng23"),\n'
    '          ("24", "cutwA"), ("25", "cutng25"), ("25p", "cutng25p"),\n'
    '          ("26", "cutng26"), ("29", "cutng29"), ("58", "cut58"),\n'
    '          ("k5", "cutk5")]\n'
    'CURVE = ["19", "23", "24", "25", "25p", "26", "29"]   # registered curve',
    1))
# fresh-batch reads z131/B24 -> z133/B25
V.append((
    'af_mean = {a: round(float(np.mean([float(z131[f"af_{a}_{s}"]) for s in B24])), 6)\n'
    '           for a in ARMS}\n'
    'af_range_ok = all(0.01 < float(z131[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B24)',
    'af_mean = {a: round(float(np.mean([float(z133[f"af_{a}_{s}"]) for s in B25])), 6)\n'
    '           for a in ARMS}\n'
    'af_range_ok = all(0.01 < float(z133[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B25)',
    1))
V.append(('        t = side_k(z131, a, B24, pk)',
          '        t = side_k(z133, a, B25, pk)', 1))
V.append(('print("---- B24 per-side duty table ----")',
          'print("---- B25 per-side duty table ----")', 1))
V.append(('# ---- batch-band disclosure: full-arm B21 reads vs registered bands ----',
          '# ---- batch-band disclosure: full-arm B25 reads vs registered bands ----', 1))
V.append(('print("full-arm B24 band check (disclosure only):", band_ok)',
          'print("full-arm B25 band check (disclosure only):", band_ok)', 1))
V.append(('_, Rfull = duty_seeds(z131, "full", B24, "Ti")',
          '_, Rfull = duty_seeds(z133, "full", B25, "Ti")', 1))
V.append(('    _, Rd = duty_seeds(z131, a, B24, "Ti")',
          '    _, Rd = duty_seeds(z133, a, B25, "Ti")', 1))
V.append(('      "cutwA", round(float(z131["g_cutwA"]), 6),',
          '      "cutwA", round(float(z133["g_cutwA"]), 6),', 1))
V.append(('           g_cutk5=float(z131["g_cutk5"]),',
          '           g_cutk5=float(z133["g_cutk5"]),', 1))
# B23-cert -> B24-cert
V.append((
    '# ---- Part 4: B23-cert FIRST, then XOR reads + S/S + pooled ----\n'
    '# B23-cert BEFORE any B24 read: machinery recomputed on raw_l128 B23 ==\n'
    '# results_l128.json Ti table (ALL 12 l128 table arms).\n'
    'b23_cert_fail = []\n'
    'for a in r128["table"]["Ti"]:\n'
    '    want = r128["table"]["Ti"][a]\n'
    '    got = side_k(z128, a, B23, "Ti")\n'
    '    for kk in ("kL", "kR", "meanL", "meanR"):\n'
    '        if got[kk] != want[kk]:\n'
    '            b23_cert_fail.append((a, kk, got[kk], want[kk]))\n'
    'assert not b23_cert_fail, ("B23-cert FAIL (no B24 read)",\n'
    '                           b23_cert_fail[:5])\n'
    'print(f"B23-cert vs results_l128.json Ti table: PASS "\n'
    '      f"(all {len(r128[\'table\'][\'Ti\'])} arms)")',
    '# ---- Part 4: B24-cert FIRST, then XOR reads + S/S + pooled ----\n'
    '# B24-cert BEFORE any B25 read: machinery recomputed on raw_l131 B24 ==\n'
    '# results_l131.json Ti table (ALL 12 l131 table arms).\n'
    'b24_cert_fail = []\n'
    'for a in r131["table"]["Ti"]:\n'
    '    want = r131["table"]["Ti"][a]\n'
    '    got = side_k(z131, a, B24, "Ti")\n'
    '    for kk in ("kL", "kR", "meanL", "meanR"):\n'
    '        if got[kk] != want[kk]:\n'
    '            b24_cert_fail.append((a, kk, got[kk], want[kk]))\n'
    'assert not b24_cert_fail, ("B24-cert FAIL (no B25 read)",\n'
    '                           b24_cert_fail[:5])\n'
    'print(f"B24-cert vs results_l131.json Ti table: PASS "\n'
    '      f"(all {len(r131[\'table\'][\'Ti\'])} arms)")', 1))
# interp mass source gains 25p
V.append((
    '        mass=S131["prefix"][a]["mass_removed"] if a in S131["prefix"]\n'
    '        else (SM["ngladder"]["k19"]["mass_removed"] if kk == "19"\n'
    '              else SM["ngladder"]["k29"]["mass_removed"] if kk == "29"\n'
    '              else None))',
    '        mass=S131["prefix"][a]["mass_removed"] if a in S131["prefix"]\n'
    '        else (SM["ngladder"]["k19"]["mass_removed"] if kk == "19"\n'
    '              else SM["ngladder"]["k29"]["mass_removed"] if kk == "29"\n'
    '              else S133["xor25p"]["cutng25p"]["mass_removed"]\n'
    '              if a == "cutng25p" else None))', 1))
# XOR branches W1/W2/W3
V.append((
    '# registered XOR branches (PREREG X1/X2/X3; report WHICH carries)\n'
    't25 = interp_read["25"]\n'
    'x1 = bool(t25["super"] or t25["restore"])\n'
    'x2 = bool(t25["partial"])\n'
    'x3 = bool(t25["kill"] or not (x1 or x2))\n'
    'xor = dict(\n'
    '    X1_rank25_completes=x1, X2_rank26_completes=x2,\n'
    '    X3_neither=x3,\n'
    '    cls=("X1: rank 25 (id 1110) COMPLETES the kill->super flip — k25 "\n'
    '          "supers/restores alone, k26 adds nothing material"\n'
    '          if x1 else\n'
    '          "X2: rank 26 (id 319) is the completing cell — k25 stays "\n'
    '          "PARTIAL, k26 supers same-batch"\n'
    '          if x2 else\n'
    '          "X3 (registered degenerate): NO single named cell carries "\n'
    '          "the flip — k25 kills or lands outside every band; the "\n'
    '          "{1110, 319} PAIR stays the unit (L55 rule)"))\n'
    'steps_x = {"24->25": round(interp_read["25"]["meanR"]\n'
    '                           - interp_read["24"]["meanR"], 3),\n'
    '           "25->26": round(interp_read["26"]["meanR"]\n'
    '                           - interp_read["25"]["meanR"], 3)}\n'
    'p2 = dict(rank25_id=S131["rank_ids"]["rank25"],\n'
    '          rank26_id=S131["rank_ids"]["rank26"],\n'
    '          m25=S131["rank_mass"]["rank25"], m26=S131["rank_mass"]["rank26"],\n'
    '          pair_delta=S131["rank_mass"]["pair_delta"],\n'
    '          note="arms differ by one full cell mass each way; the "\n'
    '               "alternative reading is any ~.006 mass beyond .2350")',
    '# registered XOR branches (PREREG W1/W2/W3; report WHICH carries)\n'
    't25p = interp_read["25p"]\n'
    'w1 = bool(t25p["partial"])\n'
    'w2 = bool(t25p["super"] or t25p["restore"])\n'
    'w3 = bool(t25p["kill"] or not (w1 or w2))\n'
    'xor = dict(\n'
    '    W1_identity_xor=w1, W2_position_thin=w2,\n'
    '    W3_neither=w3,\n'
    '    cls=("W1: cutng25p PARTIALs — clean IDENTITY XOR at mass-match: "\n'
    '          "1110 completes the flip, 319 does NOT (L120 cell-204 "\n'
    '          "claim upgrades to mass-matched)"\n'
    '          if w1 else\n'
    '          "W2: cutng25p SUPERs/RESTORES — the flip is POSITION-THIN: "\n'
    '          "BOTH transition cells complete individually (window claim "\n'
    '          "revised to either-cell; reported honestly)"\n'
    '          if w2 else\n'
    '          "W3 (registered degenerate): 25p kills or lands outside "\n'
    '          "every band — neither branch; report which band it landed "\n'
    '          "in (L55 rule)"))\n'
    'steps_x = {"24->25": round(interp_read["25"]["meanR"]\n'
    '                           - interp_read["24"]["meanR"], 3),\n'
    '           "24->25p": round(interp_read["25p"]["meanR"]\n'
    '                            - interp_read["24"]["meanR"], 3),\n'
    '           "25p->26": round(interp_read["26"]["meanR"]\n'
    '                            - interp_read["25p"]["meanR"], 3)}\n'
    'p2 = dict(rank25_id=S131["rank_ids"]["rank25"],\n'
    '          rank26_id=S131["rank_ids"]["rank26"],\n'
    '          m25=S131["rank_mass"]["rank25"], m26=S131["rank_mass"]["rank26"],\n'
    '          pair_delta=S131["rank_mass"]["pair_delta"],\n'
    '          mass_25p=S133["xor25p"]["cutng25p"]["mass_removed"],\n'
    '          note="25p vs 25 differ ONLY by which twin is in the drop "\n'
    '               "(319 vs 1110) at 3.9e-04 mass delta — identity XOR")',
    1))
# S1/S2/S3 batch-count strings + S4 block
V.append((
    's1 = dict(k5_kill=bool(killmap["k5"]), cls=(\n'
    '    "cutk5 KILLS on B24 — 12th consecutive batch "\n'
    '    "(B12/B14/B15/B16/B17/B18/B19/B20/B21/B22/B23/B24)"\n'
    '    if killmap["k5"] else\n'
    '    "cutk5 does NOT kill on B24 — DISCLOSED (L118 lottery class)"))',
    's1 = dict(k5_kill=bool(killmap["k5"]), cls=(\n'
    '    "cutk5 KILLS on B25 — 13th consecutive batch "\n'
    '    "(B12..B25)"\n'
    '    if killmap["k5"] else\n'
    '    "cutk5 does NOT kill on B25 — DISCLOSED (L118 lottery class)"))', 1))
V.append((
    '    "cutng19 KILLs (kR+meanR legs; dR leg reported separately, "\n'
    '    "3-batch miss pattern) + cutng29 SUPER-RAISES in-batch (9th)"',
    '    "cutng19 KILLs (kR+meanR legs; dR leg reported separately) + "\n'
    '    "cutng29 SUPER-RAISES in-batch (10th)"', 1))
V.append((
    's3 = dict(wA_partial=bool(_partial(table["Ti"]["cutwA"])),\n'
    '          wA_meanR=table["Ti"]["cutwA"]["meanR"],\n'
    '          wA_kR=table["Ti"]["cutwA"]["kR"], cls=(\n'
    '    "cutwA lands in the PARTIAL band [.35,.50] & kR 3-8 — 4th batch "\n'
    '    "(B18 .413/5, B19 .376/4, B21 .365/3, B24)"\n'
    '    if _partial(table["Ti"]["cutwA"]) else\n'
    '    "cutwA MISSES the partial band — DISCLOSED (would revise L124\'s "\n'
    '    "stable-intermediate reading)"))',
    's3 = dict(wA_partial=bool(_partial(table["Ti"]["cutwA"])),\n'
    '          wA_meanR=table["Ti"]["cutwA"]["meanR"],\n'
    '          wA_kR=table["Ti"]["cutwA"]["kR"], cls=(\n'
    '    "cutwA lands in the PARTIAL band [.35,.50] & kR 3-8 — 5th batch "\n'
    '    "(B18 .413/5, B19 .376/4, B21 .365/3, B24 .436/6, B25)"\n'
    '    if _partial(table["Ti"]["cutwA"]) else\n'
    '    "cutwA MISSES the partial band — DISCLOSED (would revise L124\'s "\n'
    '    "stable-intermediate reading)"))\n'
    '# S4 (L133): cutng25 SUPER 2nd batch — L131 X1 replication\n'
    't25b = table["Ti"]["cutng25"]\n'
    's4 = dict(ng25_super=bool(_super(t25b)), ng25_restore=bool(_restore(t25b)),\n'
    '          ng25_meanR=t25b["meanR"], ng25_kR=t25b["kR"], cls=(\n'
    '    "cutng25 SUPER/RESTORE replicates on B25 — L131 X1 2nd batch"\n'
    '    if _super(t25b) or _restore(t25b) else\n'
    '    "cutng25 misses SUPER/RESTORE on B25 — DISCLOSED (X1 single-batch)"))', 1))
V.append(('print(f"S3: {s3[\'cls\']}")',
          'print(f"S3: {s3[\'cls\']}")\n'
          'print(f"S4: {s4[\'cls\']} | ng25 meanR {s4[\'ng25_meanR\']:.3f} '
          'kR {s4[\'ng25_kR\']}/16")', 1))
# pooled R4 -> n=160
V.append((
    '    _, Rb24 = duty_seeds(z131, a, B24, "Ti")\n'
    '    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21,\n'
    '                           Rb22, Rb23, Rb24])\n'
    '    k = int((allb >= .5).sum())\n'
    '    lb, ub = wilson(k, 144)\n'
    '    pooled[a] = dict(k144=k, p_hat=k / 144, lb=lb, ub=ub,\n'
    '                     k_b21=int((Rb21 >= .5).sum()),\n'
    '                     k_b24=int((Rb24 >= .5).sum()))\n'
    '    print(f"POOLED Ti_R {a:7s} k {k}/144 p_hat {k/144:.3f} "\n'
    '          f"Wilson [{lb:.4f}, {ub:.4f}] (B21 {pooled[a][\'k_b21\']}/16, "\n'
    '          f"B24 {pooled[a][\'k_b24\']}/16)")',
    '    _, Rb24 = duty_seeds(z131, a, B24, "Ti")\n'
    '    _, Rb25 = duty_seeds(z133, a, B25, "Ti")\n'
    '    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21,\n'
    '                           Rb22, Rb23, Rb24, Rb25])\n'
    '    k = int((allb >= .5).sum())\n'
    '    lb, ub = wilson(k, 160)\n'
    '    pooled[a] = dict(k160=k, p_hat=k / 160, lb=lb, ub=ub,\n'
    '                     k_b21=int((Rb21 >= .5).sum()),\n'
    '                     k_b24=int((Rb24 >= .5).sum()),\n'
    '                     k_b25=int((Rb25 >= .5).sum()))\n'
    '    print(f"POOLED Ti_R {a:7s} k {k}/160 p_hat {k/160:.3f} "\n'
    '          f"Wilson [{lb:.4f}, {ub:.4f}] (B21 {pooled[a][\'k_b21\']}/16, "\n'
    '          f"B24 {pooled[a][\'k_b24\']}/16, B25 {pooled[a][\'k_b25\']}/16)")',
    1))
# pooled_t -> n=48 + ng25/ng25p
V.append((
    '# P3 (L132 prebase): transition arms pooled B21+B24 n=32\n'
    'pooled_t = {}\n'
    'for a in ("cutng23", "cutwA", "cutng26", "cutng29"):\n'
    '    _, Rb21 = duty_seeds(z126, a, B21, "Ti")\n'
    '    _, Rb24 = duty_seeds(z131, a, B24, "Ti")\n'
    '    allb = np.concatenate([Rb21, Rb24])\n'
    '    k = int((allb >= .5).sum())\n'
    '    lb, ub = wilson(k, 32)\n'
    '    pooled_t[a] = dict(k32=k, p_hat=k / 32, lb=lb, ub=ub,\n'
    '                       k_b21=int((Rb21 >= .5).sum()),\n'
    '                       k_b24=int((Rb24 >= .5).sum()))\n'
    '    print(f"P3 POOLED transition {a:8s} k {k}/32 "\n'
    '          f"(B21 {pooled_t[a][\'k_b21\']}/16 + B24 "\n'
    '          f"{pooled_t[a][\'k_b24\']}/16) p_hat {k/32:.3f} "\n'
    '          f"Wilson [{lb:.4f}, {ub:.4f}]")\n'
    'pooled_scr = {"note": "not run in L131 — l128 rebase stands"}',
    '# P3: transition arms pooled B21+B24+B25 n=48; ng25/ng25p separate\n'
    'pooled_t = {}\n'
    'for a in ("cutng23", "cutwA", "cutng26", "cutng29"):\n'
    '    _, Rb21 = duty_seeds(z126, a, B21, "Ti")\n'
    '    _, Rb24 = duty_seeds(z131, a, B24, "Ti")\n'
    '    _, Rb25 = duty_seeds(z133, a, B25, "Ti")\n'
    '    allb = np.concatenate([Rb21, Rb24, Rb25])\n'
    '    k = int((allb >= .5).sum())\n'
    '    lb, ub = wilson(k, 48)\n'
    '    pooled_t[a] = dict(k48=k, p_hat=k / 48, lb=lb, ub=ub,\n'
    '                       k_b21=int((Rb21 >= .5).sum()),\n'
    '                       k_b24=int((Rb24 >= .5).sum()),\n'
    '                       k_b25=int((Rb25 >= .5).sum()))\n'
    '    print(f"P3 POOLED transition {a:8s} k {k}/48 "\n'
    '          f"(B21 {pooled_t[a][\'k_b21\']}/16 + B24 "\n'
    '          f"{pooled_t[a][\'k_b24\']}/16 + B25 "\n'
    '          f"{pooled_t[a][\'k_b25\']}/16) p_hat {k/48:.3f} "\n'
    '          f"Wilson [{lb:.4f}, {ub:.4f}]")\n'
    '# ng25 2nd batch (L131 X1 replication); ng25p single-batch (disclosed)\n'
    '_, R25a = duty_seeds(z131, "cutng25", B24, "Ti")\n'
    '_, R25b = duty_seeds(z133, "cutng25", B25, "Ti")\n'
    'k25 = int((np.concatenate([R25a, R25b]) >= .5).sum())\n'
    'lb25, ub25 = wilson(k25, 32)\n'
    'pooled_t["cutng25"] = dict(k32=k25, p_hat=k25 / 32, lb=lb25, ub=ub25,\n'
    '                           k_b24=int((R25a >= .5).sum()),\n'
    '                           k_b25=int((R25b >= .5).sum()))\n'
    '_, R25p = duty_seeds(z133, "cutng25p", B25, "Ti")\n'
    'k25p = int((R25p >= .5).sum())\n'
    'lb25p, ub25p = wilson(k25p, 16)\n'
    'pooled_t["cutng25p"] = dict(k16=k25p, p_hat=k25p / 16, lb=lb25p,\n'
    '                            ub=ub25p, single_batch=True)\n'
    'print(f"P3 ng25 2nd batch k {k25}/32 Wilson [{lb25:.4f}, {ub25:.4f}] "\n'
    '      f"| ng25p single-batch k {k25p}/16 [{lb25p:.4f}, {ub25p:.4f}]")\n'
    'pooled_scr = {"note": "not run in L133 — l128 rebase stands"}', 1))
# p0 dict + conjunction + s4 in interp
V.append((
    '          c0a128_pass=ar["c0a128_pass"], c0a128_max=ar["c0a128_max"],',
    '          c0a128_pass=ar["c0a128_pass"], c0a128_max=ar["c0a128_max"],\n'
    '          c0a131_pass=ar["c0a131_pass"], c0a131_max=ar["c0a131_max"],\n'
    '          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"],', 1))
V.append((
    '                  and p0["c0a126_pass"] and p0["c0a127_pass"]\n'
    '                  and p0["c0a128_pass"]\n'
    '                  and p0["g_cut58_stored_exact"]',
    '                  and p0["c0a126_pass"] and p0["c0a127_pass"]\n'
    '                  and p0["c0a128_pass"] and p0["c0a131_pass"]\n'
    '                  and p0["g_cut58_stored_exact"]', 1))
V.append((
    '                  and p0["g_cutng23_stored_exact"] and p0["g_cutng26_stored_exact"]\n'
    '                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])',
    '                  and p0["g_cutng23_stored_exact"] and p0["g_cutng26_stored_exact"]\n'
    '                  and p0["g_cutng25_stored_exact"]\n'
    '                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])',
    1))
V.append((
    'print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..125 "\n'
    '      "retained + C0A-126 EXT (9 arms) + C0A-127 (6) + C0A-128 (6) + "\n'
    '      "9 stored gains:",',
    'print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..128 "\n'
    '      "retained + C0A-131 (10 arms NEW) + 10 stored gains:",', 1))
V.append((
    '           interp=dict(curve=interp_read, steps=steps_x, s1=s1, s2=s2,\n'
    '                       s3=s3),',
    '           interp=dict(curve=interp_read, steps=steps_x, s1=s1, s2=s2,\n'
    '                       s3=s3, s4=s4),', 1))
V.append(('           b23_cert_pass=True,', '           b24_cert_pass=True,', 1))
V.append(('json.dump(out, open("l131/results_l131.json", "w"), indent=1)',
          'json.dump(out, open("l133/results_l133.json", "w"), indent=1)', 1))
V.append(('print("results_l131.json written")',
          'print("results_l133.json written")', 1))

v = apply(v, V, "verdict")

# verdict residual scan
for bad in ("B23-cert", "b23_cert", "l131/anchors_run", "results_l131.json\", \"w"):
    assert bad not in v, ("verdict stale token", bad)
# every B24 use must be context-only (z131/r131 reads) — enumerate lines
for i, line in enumerate(v.splitlines()):
    if "B24" in line:
        assert ("z131" in line or "r131" in line or "context batch" in line
                or "raw_l131" in line or "l131" in line or "B24-cert" in line
                or "k_b24" in line or "B24 {" in line or "B24 " in line
                or line.lstrip().startswith("#") or i < 16), \
            ("unwhitelisted B24", i, line)
for probe in ('z133', '"25p"', 'cutng25p', 'S133', 's4', 'B25'):
    assert v.count(probe) >= 1, ("missing verdict plumbing", probe)

open("l133_verdict.py", "w").write(v)
py_compile.compile("l133_verdict.py", doraise=True)
print(f"l133_verdict.py written ({len(v.splitlines())} lines) + py_compile OK")
