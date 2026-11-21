"""L148 build: count-asserted transform l142_run.py -> l148_run.py.

Keeps eAll end-to-end from l142; DELETES eOutInt/eOutMot/eOutAll/eIn
(residual scan, l131 law); ADDS se0 (eAll graph + window clamp, l137/
l144 form); B29->B32 batch; anchors C0A-148 + FC-142 + SE-ID. Every rep
count-pinned; residual token scan at the end must be ZERO on code lines.
"""
import re
import sys

src = open("l142_run.py").read()


def rep(old, new, n=1, what=""):
    global src
    c = src.count(old)
    assert c == n, (what or old[:60], f"count {c} != {n}")
    src = src.replace(old, new)


# 1. docstring
_doc = src[:src.index('"""', 3) + 3]
assert _doc.startswith('"""L142 run:'), "docstring opener"
_new_doc = '''"""L148 run: silent-and-edgeless identity arm on fresh B32. PREREG
l148/PREREG.md FIRST (registered before this build). Arms: full, b65,
cutwA (partial base), cutng25 (super ref), eAll (93-edge drop re-pin,
l142 build verbatim) + se0 (eAll graph + window-only clamp X[loc 467]=0,
l137/l144 clamp form). se0 rides eAll's gain (graph-identity af-match).
FRESH B32 3349-3364 (absent every npz under banc/; card's "B31" label
predates l145's ship — PREREG rename disclosure). Anchors: stored gains
EXACT (cutwA/cutng25/eAll), C0A-148 vs raw_l135 (4 arms), FC-142 eAll
traces vs raw_l142, SE-ID se0-vs-eAll (+vs cutng25) @801/901. CPU-only;
raw checkpoint BEFORE analysis. (l142's eOutInt/eOutMot/eOutAll/eIn arms
DELETED here — their B29 numbers stand, see l142/results_l142.json.)
"""'''
src = _new_doc + src[len(_doc):]

# 2. ARMS/GAIN
rep('ARMS = ["full", "b65", "cutwA", "cutng25",\n'
    '        "eOutInt", "eOutMot", "eOutAll", "eIn", "eAll"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,\n'
    '            eOutInt=None, eOutMot=None, eOutAll=None, eIn=None,\n'
    '            eAll=None)',
    'ARMS = ["full", "b65", "cutwA", "cutng25", "eAll", "se0"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,\n'
    '            eAll=None, se0=None)  # se0 gain set below (graph-id)')

# 3. batch
rep('B29 = list(range(3301, 3317))  # fresh, absent l107..l137 + l139 j0-j5\n'
    'SEEDS = ANCH + B29                  # anchors FIRST: early wiring verdict\n'
    'FRESH = B29',
    'B32 = list(range(3349, 3365))  # fresh (PREREG rename; B31 = l145)\n'
    'SEEDS = ANCH + B32                  # anchors FIRST: early wiring verdict\n'
    'FRESH = B32')

# 4. stored-gain constant for eAll (FC-142 pin)
rep('G_CUTNG25P_STORED = 0.1435265743732452  # l133 fresh gain -> stored-form (C0A-133)',
    'G_CUTNG25P_STORED = 0.1435265743732452  # l133 fresh gain -> stored-form (C0A-133)\n'
    'G_EALL_STORED = 0.1454454553127289  # l142 fresh gain -> stored-form (FC-142)')

# 5. E_ARMS + e_drop + helper deletions
rep('E_ARMS = ("eOutInt", "eOutMot", "eOutAll", "eIn", "eAll")',
    'E_ARMS = ("eAll",)')
rep('_sel_out = emask_wA & (src_all == GI_CARRIER)\n'
    'out_int_e = _sel_out & (tier_of_dst[dst_all] == "intrinsic")\n'
    'out_mot_e = _sel_out & (tier_of_dst[dst_all] == "motor_other")\n'
    'in_sel_e = emask_wA & (dst_all == GI_CARRIER)\n'
    'e_drop = {"eOutInt": out_int_e, "eOutMot": out_mot_e,\n'
    '          "eOutAll": _sel_out, "eIn": in_sel_e,\n'
    '          "eAll": _sel_out | in_sel_e}',
    '_sel_out = emask_wA & (src_all == GI_CARRIER)\n'
    'in_sel_e = emask_wA & (dst_all == GI_CARRIER)\n'
    'e_drop = {"eAll": _sel_out | in_sel_e}')
rep('assert E_EDGES == {"eOutInt": 70, "eOutMot": 10, "eOutAll": 80,\n'
    '                   "eIn": 13, "eAll": 93}, E_EDGES',
    'assert E_EDGES == {"eAll": 93}, E_EDGES')

# 6. se0 wiring after the e-arm alias loop
rep('# L142: edge arms share cutwA\'s node set — alias every per-arm map\n'
    'for _ea in E_ARMS:\n'
    '    POOLS[_ea] = POOLS["cutwA"]\n'
    '    mech[_ea] = mech["cutwA"]\n'
    '    motor[_ea] = motor["cutwA"]\n'
    '    dng100[_ea] = dng100["cutwA"]\n'
    '    WB[_ea] = Wb_e[_ea]\n'
    '    N_OF[_ea] = n_cutk["cutwA"]',
    '# L142: edge arms share cutwA\'s node set — alias every per-arm map\n'
    'for _ea in E_ARMS:\n'
    '    POOLS[_ea] = POOLS["cutwA"]\n'
    '    mech[_ea] = mech["cutwA"]\n'
    '    motor[_ea] = motor["cutwA"]\n'
    '    dng100[_ea] = dng100["cutwA"]\n'
    '    WB[_ea] = Wb_e[_ea]\n'
    '    N_OF[_ea] = n_cutk["cutwA"]\n'
    '\n'
    '# ---- L148: se0 = eAll graph + window clamp on 1110 (l137/l144) ----\n'
    'CLAMP = {"se0": torch.tensor([int(loc_wA[GI_CARRIER])])}\n'
    'assert int(loc_wA[GI_CARRIER]) == 467, "clamp loc != 467 (l144 pin)"\n'
    'POOLS["se0"] = POOLS["cutwA"]\n'
    'mech["se0"] = mech["cutwA"]\n'
    'motor["se0"] = motor["cutwA"]\n'
    'dng100["se0"] = dng100["cutwA"]\n'
    'WB["se0"] = Wb_e["eAll"]\n'
    'N_OF["se0"] = n_cutk["cutwA"]\n'
    '# A0 L148 (PREREG): 1110 ISOLATED on eAll, in NO readout set\n'
    '_cl = int(loc_wA[GI_CARRIER])\n'
    'assert int((We["eAll"].col_indices() == _cl).sum()) == 0, \\\n'
    '    "1110 has out-edges on eAll (STOP)"\n'
    'assert int(torch.diff(We["eAll"].crow_indices())[_cl]) == 0, \\\n'
    '    "1110 has in-edges on eAll (STOP)"\n'
    'for _pk, _arr in POOLS["cutwA"].items():\n'
    '    assert not np.isin(_cl, _arr), ("1110 in pool " + _pk + " (STOP)")\n'
    'assert not np.isin(_cl, mech["cutwA"]), "1110 in mech (STOP)"\n'
    'assert not motor["cutwA"][_cl], "1110 in motor (STOP)"\n'
    'assert not np.isin(_cl, dng100["cutwA"]), "1110 in dng100 (STOP)"')

# 7. settle st dict (bisect path)
rep('              eOutInt=Xc_wA.clone(), eOutMot=Xc_wA.clone(),\n'
    '              eOutAll=Xc_wA.clone(), eIn=Xc_wA.clone(),\n'
    '              eAll=Xc_wA.clone(),',
    '              eAll=Xc_wA.clone(), se0=Xc_wA.clone(),')
# 8. noise dict: the SAME block lives in THREE dicts (l123 law:
# settle_states + rollout settle-phase + rollout WIN-phase) — one n=3 rep
rep('                     eOutInt=nzn[wA_pos_in_new], eOutMot=nzn[wA_pos_in_new],\n'
    '                     eOutAll=nzn[wA_pos_in_new], eIn=nzn[wA_pos_in_new],\n'
    '                     eAll=nzn[wA_pos_in_new],',
    '                     eAll=nzn[wA_pos_in_new], se0=nzn[wA_pos_in_new],',
    n=3, what="noise dict x3 (settle/settle-phase/win-phase)")
# 9. bisect gains literal
rep('                                  cutng26=g, cutk5=g, eOutInt=g, eOutMot=g,\n'
    '                                  eOutAll=g, eIn=g, eAll=g))',
    '                                  cutng26=g, cutk5=g, eAll=g, se0=g))')
# 10. post-bisect: eAll stored-exact + se0 gain identity
rep('g_eall_vs_g25 = dict(g_eAll=GAIN["eAll"], g_cutng25=GAIN["cutng25"],\n'
    '                     equal=bool(GAIN["eAll"] == GAIN["cutng25"]))',
    'assert GAIN["eAll"] == G_EALL_STORED, ("eAll bisect drift", GAIN["eAll"])\n'
    'GAIN["se0"] = GAIN["eAll"]  # graph-identity af-match (l144 silW form)\n'
    'assert GAIN["se0"] == G_EALL_STORED == GAIN["cutng25"], \\\n'
    '    (GAIN["se0"], "se0/eAll/ng25 gain identity broken (STOP)")\n'
    'g_eall_vs_g25 = dict(g_eAll=GAIN["eAll"], g_cutng25=GAIN["cutng25"],\n'
    '                     equal=bool(GAIN["eAll"] == GAIN["cutng25"]))')
# 11. rollout X dict
rep('             eOutInt=Xc_wA.clone(), eOutMot=Xc_wA.clone(),\n'
    '             eOutAll=Xc_wA.clone(), eIn=Xc_wA.clone(),\n'
    '             eAll=Xc_wA.clone(),',
    '             eAll=Xc_wA.clone(), se0=Xc_wA.clone(),')
# 12/13. (noise dicts covered by the n=3 rep above — l123 law)
# 14. clamp in the window loop (unique 3-line block)
rep('            t = torch.relu(drive + BG)\n'
    '            t = (t + noise[a]).clamp(max=RMAX)\n'
    '            X[a] = X[a] + (DT / TAU) * (t - X[a])',
    '            t = torch.relu(drive + BG)\n'
    '            t = (t + noise[a]).clamp(max=RMAX)\n'
    '            X[a] = X[a] + (DT / TAU) * (t - X[a])\n'
    '            if a in CLAMP:\n'
    '                X[a][CLAMP[a], 0] = 0.0', what="window-loop clamp")
# 15. raw paths (OUTPUT direction)
rep('if os.path.exists("l142/raw_partial.npz"):',
    'if os.path.exists("l148/raw_partial.npz"):')
rep('    np.savez("l142/raw_partial.npz", **store)',
    '    np.savez("l148/raw_partial.npz", **store)')
rep('np.savez_compressed("l142/raw_l142.npz", K=K,\n'
    '                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],\n'
    '                    g_eOutInt=GAIN["eOutInt"], g_eOutMot=GAIN["eOutMot"],\n'
    '                    g_eOutAll=GAIN["eOutAll"], g_eIn=GAIN["eIn"],\n'
    '                    g_eAll=GAIN["eAll"],',
    'np.savez_compressed("l148/raw_l148.npz", K=K,\n'
    '                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],\n'
    '                    g_eAll=GAIN["eAll"], g_se0=GAIN["se0"],\n'
    '                    clamp_loc=np.array([467]), clamp_id=np.array([1110]),')
rep('log("raw_l135.npz checkpointed BEFORE analysis")',
    'log("raw_l148.npz checkpointed BEFORE analysis")')
# 15b. resume-path np.load (L120 addendum-2: EVERY np.load path, both sites)
rep('    z = np.load("l142/raw_partial.npz")',
    '    z = np.load("l148/raw_partial.npz")')
# 15c. absence-assert block B29->B32 (scan catch: NameError waiting)
rep('    assert not any(f"mm_full_{s}" in _zp.files for s in B29), \\\n'
    '        ("B29 collides with " + _p + " (STOP)")\n'
    'log(f"B29 absence across {len(_prevs)} stored npzs: PASS")',
    '    assert not any(f"mm_full_{s}" in _zp.files for s in B32), \\\n'
    '        ("B32 collides with " + _p + " (STOP)")\n'
    'log(f"B32 absence across {len(_prevs)} stored npzs: PASS")')
# 16. absence list: add prior-run npzs (INPUT direction)
rep('          "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz",\n'
    '          "l113/raw_l113.npz"]',
    '          "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz",\n'
    '          "l113/raw_l113.npz", "l142/raw_l142.npz",\n'
    '          "l144/raw_l144.npz", "l145/raw_l145.npz",\n'
    '          "l142/raw_partial.npz", "l144/raw_partial.npz",\n'
    '          "l145/raw_partial.npz"]')
# 17. anchor section renames + new anchors
rep('_poolkeys142 = []', '_poolkeys148 = []')
rep('_poolkeys142.append(f"{_pk}_{_c}{_s}")', '_poolkeys148.append(f"{_pk}_{_c}{_s}")')
rep('C0A142_KEYS = ["mm", "xm"] + _poolkeys142', 'C0A148_KEYS = ["mm", "xm"] + _poolkeys148')
rep('_arms142 = ("full", "b65", "cutwA", "cutng25")', '_arms148 = ("full", "b65", "cutwA", "cutng25")')
rep('assert all(f"{_k}_{_a}_801" in z135c.files for _k in C0A142_KEYS\n'
    '           for _a in _arms142), "C0A-142 coverage miss"',
    'assert all(f"{_k}_{_a}_801" in z135c.files for _k in C0A148_KEYS\n'
    '           for _a in _arms148), "C0A-148 coverage miss"\n'
    'z142c = np.load("l142/raw_l142.npz")\n'
    'assert all(f"{_k}_eAll_801" in z142c.files for _k in C0A148_KEYS), \\\n'
    '    "FC-142 coverage miss"')
rep('c0a142 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A142_KEYS:\n'
    '        for a in _arms142:\n'
    '            c0a142[f"135_{key}_{a}_{s}"] = float(np.abs(\n'
    '                store[f"{key}_{a}_{s}"] - z135c[f"{key}_{a}_{s}"][:WIN]).max())\n'
    '    for a in _arms142:\n'
    '        c0a142[f"135_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])\n'
    '                                        - float(z135c[f"af_{a}_{s}"]))\n'
    'c0a142_max = max(c0a142.values())\n'
    'c0a142_pass = bool(all(v == 0.0 for v in c0a142.values()))\n'
    'log(f"C0A-142 (4 arms x {len(C0A142_KEYS)} keys x 2 seeds) vs raw_l135: "\n'
    '    f"{\'PASS\' if c0a142_pass else \'FAIL\'} (max {c0a142_max:.1e})")',
    'c0a148 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A148_KEYS:\n'
    '        for a in _arms148:\n'
    '            c0a148[f"135_{key}_{a}_{s}"] = float(np.abs(\n'
    '                store[f"{key}_{a}_{s}"] - z135c[f"{key}_{a}_{s}"][:WIN]).max())\n'
    '    for a in _arms148:\n'
    '        c0a148[f"135_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])\n'
    '                                        - float(z135c[f"af_{a}_{s}"]))\n'
    'c0a148_max = max(c0a148.values())\n'
    'c0a148_pass = bool(all(v == 0.0 for v in c0a148.values()))\n'
    'log(f"C0A-148 (4 arms x {len(C0A148_KEYS)} keys x 2 seeds) vs raw_l135: "\n'
    '    f"{\'PASS\' if c0a148_pass else \'FAIL\'} (max {c0a148_max:.1e})")\n'
    'fc142 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A148_KEYS:\n'
    '        fc142[f"{key}_{s}"] = float(np.abs(\n'
    '            store[f"{key}_eAll_{s}"] - z142c[f"{key}_eAll_{s}"][:WIN]).max())\n'
    '    fc142[f"af_{s}"] = abs(float(store[f"af_eAll_{s}"])\n'
    '                           - float(z142c[f"af_eAll_{s}"]))\n'
    'fc142_max = max(fc142.values())\n'
    'fc142_pass = bool(all(v == 0.0 for v in fc142.values()))\n'
    'log(f"FC-142 eAll (24 keys x 2 seeds) vs raw_l142: "\n'
    '    f"{\'PASS\' if fc142_pass else \'FAIL\'} (max {fc142_max:.1e})")\n'
    'seid = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A148_KEYS:\n'
    '        seid[f"se0e_{key}_{s}"] = float(np.abs(\n'
    '            store[f"{key}_se0_{s}"] - store[f"{key}_eAll_{s}"]).max())\n'
    '        seid[f"se0n_{key}_{s}"] = float(np.abs(\n'
    '            store[f"{key}_se0_{s}"] - store[f"{key}_cutng25_{s}"]).max())\n'
    '    seid[f"se0e_af_{s}"] = abs(float(store[f"af_se0_{s}"])\n'
    '                               - float(store[f"af_eAll_{s}"]))\n'
    'seid_max = max(seid.values())\n'
    'seid_pass = bool(all(v == 0.0 for v in seid.values()))\n'
    'log(f"SE-ID se0 vs eAll + vs cutng25 @801/901: "\n'
    '    f"{\'PASS\' if seid_pass else \'FAIL\'} (max {seid_max:.1e})")')
rep('a_eall = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A142_KEYS:',
    'a_eall = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A148_KEYS:')
# 18. out json
rep('out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],\n'
    '           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),\n'
    '           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),\n'
    '           g_eOutInt=GAIN["eOutInt"], g_eOutMot=GAIN["eOutMot"],\n'
    '           g_eOutAll=GAIN["eOutAll"], g_eIn=GAIN["eIn"], g_eAll=GAIN["eAll"],\n'
    '           e_band_ok=e_band_ok, new_stairs=new_stairs,\n'
    '           e_edges=E_EDGES, K=K, mass_split=mass_split,\n'
    '           n_seeds=len(SEEDS), g_eall_vs_g25=g_eall_vs_g25,\n'
    '           a_eall_max=a_eall_max,\n'
    '           c0a142_max=c0a142_max, c0a142_pass=c0a142_pass,\n'
    '           c0a_pass=bool(c0a142_pass))\n'
    'json.dump(out, open("l142/anchors_run.json", "w"), indent=1)\n'
    'log(f"C0A-142 {\'PASS\' if out[\'c0a_pass\'] else \'FAIL\'} "\n'
    '    f"(max {out[\'c0a142_max\']:.1e}) | A-EALL max {a_eall_max:.1e} | "\n'
    '    f"done {time.time()-t0:.0f}s")',
    'out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],\n'
    '           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),\n'
    '           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),\n'
    '           g_eAll=GAIN["eAll"], g_se0=GAIN["se0"],\n'
    '           g_eall_stored_exact=bool(GAIN["eAll"] == G_EALL_STORED),\n'
    '           clamp_loc=467, clamp_id=1110,\n'
    '           e_band_ok=e_band_ok, new_stairs=new_stairs,\n'
    '           e_edges=E_EDGES, K=K, mass_split=mass_split,\n'
    '           n_seeds=len(SEEDS), g_eall_vs_g25=g_eall_vs_g25,\n'
    '           a_eall_max=a_eall_max,\n'
    '           c0a148_max=c0a148_max, c0a148_pass=c0a148_pass,\n'
    '           fc142_max=fc142_max, fc142_pass=fc142_pass,\n'
    '           seid_max=seid_max, seid_pass=seid_pass,\n'
    '           c0a_pass=bool(c0a148_pass and fc142_pass and seid_pass))\n'
    'json.dump(out, open("l148/anchors_run.json", "w"), indent=1)\n'
    'log(f"C0A-148 {\'PASS\' if out[\'c0a_pass\'] else \'FAIL\'} "\n'
    '    f"(c0a {out[\'c0a148_max\']:.1e} | FC-142 {out[\'fc142_max\']:.1e} | "\n'
    '    f"SE-ID {out[\'seid_max\']:.1e}) | A-EALL max {a_eall_max:.1e} | "\n'
    '    f"done {time.time()-t0:.0f}s")')

open("l148_run.py", "w").write(src)

# ---- residual scan (l131 law): deleted arm tokens + B29, code lines only
BAD_RE = [r"\beIn\b", r"\bB29\b"]
BAD_LIT = ["eOutInt", "eOutMot", "eOutAll", "raw_l142.npz checkpointed",
           'open("l142/', 'savez_compressed("l142',
           'np.load("l142/raw_partial']
fails = []
in_doc = True
for i, line in enumerate(src.split("\n"), 1):
    if i == 1:
        in_doc = True
    if line.strip().endswith('"""') and i <= 16:
        in_doc = False
    if in_doc and i <= 16:
        continue  # docstring disclosure line whitelisted by region
    if line.lstrip().startswith("#"):
        continue  # comment lines whitelisted by line context (l126 law)
    for pat in BAD_RE:
        if re.search(pat, line):
            fails.append((i, pat, line.strip()[:80]))
    for pat in BAD_LIT:
        if pat in line:
            fails.append((i, pat, line.strip()[:80]))
assert not fails, ("RESIDUAL SCAN FAIL", fails[:10])
n_arms = src.count('"se0"') + src.count("se0=")
print(f"l148_run.py written | se0 token sites: {n_arms} | residual scan PASS")
