"""L150 build: l148_run.py -> l150_run.py. Count-asserted exact reps
(l123/l131 laws); full-indentation anchors; residual token scan at the
end (code lines must not survive with retired-arm tokens)."""
import re
import sys

src = open("l148_run.py").read()
n_reps = 0


def rep(old, new, count=1):
    global src, n_reps
    found = src.count(old)
    assert found == count, (f"rep count {found} != {count}", old[:70])
    src = src.replace(old, new)
    n_reps += 1


# ---- 1. docstring (unique opener, whole block splice; l122 law) ----
_doc_old = src[:src.index('"""', 3) + 3]
_doc_new = '''"""L150 run: silW batch rebase + eMot halves second batch. PREREG
l150/PREREG.md FIRST (registered before this build). Arms: full, b65,
cutwA (partial base), cutng25 (super ref), silW (cutwA graph VERBATIM +
window-only clamp X[loc 467]=0, l144 form, gain graph-identity to cutwA —
NO fresh bisect, l144 A1) + eMotTop5/eMotBot5 (l145 dose split verbatim,
fresh bisects asserted == l145 stored gains EXACT). FRESH B33 3365-3380.
Anchors: stored gains EXACT (cutwA/cutng25/eMot pair), C0A-150 vs raw_l135
(4 arms), FC-144 silW-vs-l144-sil1110_wA @801/901 (clamp-wiring cert),
FC-145 eMot arms vs raw_l145 @801/901 + bisect EXACT. CPU-only; raw
checkpoint BEFORE analysis. (the prior run's identity arms stand on their
own batch — see its results json; not re-rolled here.)
"""'''
rep(_doc_old, _doc_new)

# ---- 2. arm set + gains ----
rep('ARMS = ["full", "b65", "cutwA", "cutng25", "eAll", "se0"]',
    'ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",\n'
    '        "eMotBot5"]')
rep('''GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            eAll=None, se0=None)  # se0 gain set below (graph-id)''',
    '''GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            silW=None, eMotTop5=None, eMotBot5=None)  # silW below (graph-id)''')

# ---- 3. stored gains ----
rep('G_EALL_STORED = 0.1454454553127289  # l142 fresh gain -> stored-form (FC-142)',
    'G_EMOTTOP5_STORED = 0.1436134350299835  # l145 stored, FC-145 EXACT assert\n'
    'G_EMOTBOT5_STORED = 0.14367126345634465  # l145 stored, FC-145 EXACT assert')

# ---- 4. batch seeds ----
rep('B32 = list(range(3349, 3365))  # fresh (PREREG rename; B31 = l145)',
    'B33 = list(range(3365, 3381))  # fresh (batch lineage in PREREG)')
rep('SEEDS = ANCH + B32                  # anchors FIRST: early wiring verdict',
    'SEEDS = ANCH + B33                  # anchors FIRST: early wiring verdict')
rep('FRESH = B32', 'FRESH = B33')

# ---- 5. E-arm block: eAll single mask -> l145 dose split verbatim ----
rep('''E_ARMS = ("eAll",)
assert int(ng_desc[24]) == GI_CARRIER and int(ng_desc[25]) == 319
keep_wA_e = keep_cutk["cutwA"]
emask_wA = keep_wA_e[src_all] & keep_wA_e[dst_all]
assert int(emask_wA.sum()) == cutk_pins["cutwA"]["edges"]
_sel_out = emask_wA & (src_all == GI_CARRIER)
in_sel_e = emask_wA & (dst_all == GI_CARRIER)
e_drop = {"eAll": _sel_out | in_sel_e}
E_EDGES = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert E_EDGES == {"eAll": 93}, E_EDGES''',
    '''E_ARMS = ("eMotTop5", "eMotBot5")
assert int(ng_desc[24]) == GI_CARRIER and int(ng_desc[25]) == 319
keep_wA_e = keep_cutk["cutwA"]
emask_wA = keep_wA_e[src_all] & keep_wA_e[dst_all]
assert int(emask_wA.sum()) == cutk_pins["cutwA"]["edges"]
_sel_out = emask_wA & (src_all == GI_CARRIER)
out_mot_e = _sel_out & (tier_of_dst[dst_all] == "motor_other")
in_sel_e = emask_wA & (dst_all == GI_CARRIER)
# L145 dose split VERBATIM: rank the 10 motor edges by |vals| = log1p(syn)
# DESC, tiebreak global edge pos ASC (rank pins vs l145/static.json below)
_mp = np.where(out_mot_e)[0]
_mo = _mp[np.lexsort((_mp, -np.log1p(w_syn[_mp])))]
_top5 = np.zeros_like(emask_wA)
_top5[_mo[:5]] = True
_bot5 = np.zeros_like(emask_wA)
_bot5[_mo[5:]] = True
assert int(_top5.sum()) == 5 and int(_bot5.sum()) == 5
assert np.array_equal(np.where(_top5 | _bot5)[0],
                      np.where(out_mot_e)[0]), "top5|bot5 != all-10 motor"
e_drop = {"eMotTop5": _top5, "eMotBot5": _bot5}
E_EDGES = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert E_EDGES == {"eMotTop5": 5, "eMotBot5": 5}, E_EDGES
# ADDENDUM 1 pin: l145 static TABLE has a zip bug (pos column = unranked
# ascending list); TRUSTED columns are dst_gi/syn (the ranked order).
_S145 = json.load(open("l145/static.json"))
_stored_pos = [int(e["pos"]) for e in _S145["motor_edges_ranked"]]
assert _stored_pos == sorted(_stored_pos), \
    "stored pos column no longer ascending — defect signature changed"
assert _stored_pos == sorted(int(p) for p in _mo), \
    "position SET mismatch vs stored table (real drift, STOP)"
for _i, _e in enumerate(_S145["motor_edges_ranked"]):
    assert int(_e["syn"]) == int(w_syn[_mo[_i]]), ("rank syn drift", _i)
    assert int(_e["dst_gi"]) == int(dst_all[_mo[_i]]), ("rank dst drift", _i)''')

# ---- 6. retire the A0 eAll==cutng25 structural block (settled in l142) ----
rep('''# A0 structural law (PREREG): eAll edge positions == cutng25 node-drop
_keep25 = keep_new.copy()
_keep25[ng_desc[:25]] = False
_em25 = _keep25[src_all] & _keep25[dst_all]
assert np.array_equal(np.where(emask_wA & ~e_drop["eAll"])[0],
                      np.where(_em25)[0]), "A0 eAll != cutng25 (STOP)"
Wb_e''', '''# (edge-positions == node-drop identity law settled l142 static+run;
# not re-asserted here)
Wb_e''')

# ---- 7. se0 block -> silW block (clamp on the cutwA graph, l144 form) ----
rep('''# ---- L148: se0 = eAll graph + window clamp on 1110 (l137/l144) ----
CLAMP = {"se0": torch.tensor([int(loc_wA[GI_CARRIER])])}
assert int(loc_wA[GI_CARRIER]) == 467, "clamp loc != 467 (l144 pin)"
POOLS["se0"] = POOLS["cutwA"]
mech["se0"] = mech["cutwA"]
motor["se0"] = motor["cutwA"]
dng100["se0"] = dng100["cutwA"]
WB["se0"] = Wb_e["eAll"]
N_OF["se0"] = n_cutk["cutwA"]
# A0 L148 (PREREG): 1110 ISOLATED on eAll, in NO readout set
_cl = int(loc_wA[GI_CARRIER])
assert int((We["eAll"].col_indices() == _cl).sum()) == 0, \\
    "1110 has out-edges on eAll (STOP)"
assert int(torch.diff(We["eAll"].crow_indices())[_cl]) == 0, \\
    "1110 has in-edges on eAll (STOP)"
for _pk, _arr in POOLS["cutwA"].items():
    assert not np.isin(_cl, _arr), ("1110 in pool " + _pk + " (STOP)")
assert not np.isin(_cl, mech["cutwA"]), "1110 in mech (STOP)"
assert not motor["cutwA"][_cl], "1110 in motor (STOP)"
assert not np.isin(_cl, dng100["cutwA"]), "1110 in dng100 (STOP)"''',
    '''# ---- L150: silW = cutwA graph + window clamp on 1110 (l144 form) ----
CLAMP = {"silW": torch.tensor([int(loc_wA[GI_CARRIER])])}
assert int(loc_wA[GI_CARRIER]) == 467, "clamp loc != 467 (l144 pin)"
POOLS["silW"] = POOLS["cutwA"]
mech["silW"] = mech["cutwA"]
motor["silW"] = motor["cutwA"]
dng100["silW"] = dng100["cutwA"]
WB["silW"] = Wb_wA  # cutwA matrix VERBATIM — clamp is the only difference
N_OF["silW"] = n_cutk["cutwA"]''')

# ---- 8. per-arm state dicts (st in settle_states; X in rollout) ----
rep('              eAll=Xc_wA.clone(), se0=Xc_wA.clone(),',
    '              silW=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),\n'
    '              eMotBot5=Xc_wA.clone(),')
rep('             eAll=Xc_wA.clone(), se0=Xc_wA.clone(),',
    '             silW=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),\n'
    '             eMotBot5=Xc_wA.clone(),')

# ---- 9. noise dicts x3 (21-space pattern, count-pinned 3; l123 law) ----
rep('                     eAll=nzn[wA_pos_in_new], se0=nzn[wA_pos_in_new],',
    '                     silW=nzn[wA_pos_in_new], eMotTop5=nzn[wA_pos_in_new],\n'
    '                     eMotBot5=nzn[wA_pos_in_new],', count=3)

# ---- 10. bisect gains-dict signature ----
rep('                                  cutng26=g, cutk5=g, eAll=g, se0=g))',
    '                                  cutng26=g, cutk5=g, silW=g,\n'
    '                                  eMotTop5=g, eMotBot5=g))')

# ---- 11. post-bisect block: eAll/se0 identity -> silW + eMot EXACT ----
rep('''assert GAIN["eAll"] == G_EALL_STORED, ("eAll bisect drift", GAIN["eAll"])
GAIN["se0"] = GAIN["eAll"]  # graph-identity af-match (l144 silW form)
assert GAIN["se0"] == G_EALL_STORED == GAIN["cutng25"], \\
    (GAIN["se0"], "se0/eAll/ng25 gain identity broken (STOP)")
g_eall_vs_g25 = dict(g_eAll=GAIN["eAll"], g_cutng25=GAIN["cutng25"],
                     equal=bool(GAIN["eAll"] == GAIN["cutng25"]))
log(f"A-EALL branch: {g_eall_vs_g25}")''',
    '''assert GAIN["eMotTop5"] == G_EMOTTOP5_STORED, \\
    ("eMotTop5 bisect drift", GAIN["eMotTop5"])
assert GAIN["eMotBot5"] == G_EMOTBOT5_STORED, \\
    ("eMotBot5 bisect drift", GAIN["eMotBot5"])
GAIN["silW"] = GAIN["cutwA"]  # graph-identity af-match (l144 A1 form)
assert GAIN["silW"] == G_CUTWA_STORED == GAIN["cutwA"], \\
    (GAIN["silW"], "silW/cutwA gain identity broken (STOP)")''')

# ---- 12. checkpoint paths ----
rep('if os.path.exists("l148/raw_partial.npz"):',
    'if os.path.exists("l150/raw_partial.npz"):')
rep('np.savez("l148/raw_partial.npz", **store)',
    'np.savez("l150/raw_partial.npz", **store)')
rep('np.savez_compressed("l148/raw_l148.npz", K=K,',
    'np.savez_compressed("l150/raw_l150.npz", K=K,')
rep('                    g_eAll=GAIN["eAll"], g_se0=GAIN["se0"],',
    '                    g_silW=GAIN["silW"], g_eMotTop5=GAIN["eMotTop5"],\n'
    '                    g_eMotBot5=GAIN["eMotBot5"],')
rep('log("raw_l148.npz checkpointed BEFORE analysis")',
    'log("raw_l150.npz checkpointed BEFORE analysis")')

# ---- 13. absence list: add l148 raws; B32->B33 tokens ----
rep('''          "l142/raw_partial.npz", "l144/raw_partial.npz",
          "l145/raw_partial.npz"]''',
    '''          "l142/raw_partial.npz", "l144/raw_partial.npz",
          "l145/raw_partial.npz", "l148/raw_l148.npz",
          "l148/raw_partial.npz"]''')
rep('''    assert not any(f"mm_full_{s}" in _zp.files for s in B32), \\
        ("B32 collides with " + _p + " (STOP)")
log(f"B32 absence across {len(_prevs)} stored npzs: PASS")''',
    '''    assert not any(f"mm_full_{s}" in _zp.files for s in B33), \\
        ("B33 collides with " + _p + " (STOP)")
log(f"B33 absence across {len(_prevs)} stored npzs: PASS")''')

# ---- 14. anchor-block renames + FC blocks ----
src = src.replace("_poolkeys148", "_poolkeys150")
src = src.replace("C0A148_KEYS", "C0A150_KEYS")
src = src.replace("c0a148", "c0a150")
src = src.replace("_arms148", "_arms150")
rep('''z142c = np.load("l142/raw_l142.npz")
assert all(f"{_k}_eAll_801" in z142c.files for _k in C0A150_KEYS), \\
    "FC-142 coverage miss"''',
    '''z144c = np.load("l144/raw_l144.npz")
assert all(f"{_k}_sil1110_wA_801" in z144c.files for _k in C0A150_KEYS), \\
    "FC-144 coverage miss"''')
rep('''fc142 = {}
for s in (801, 901):
    for key in C0A150_KEYS:
        fc142[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_eAll_{s}"] - z142c[f"{key}_eAll_{s}"][:WIN]).max())
    fc142[f"af_{s}"] = abs(float(store[f"af_eAll_{s}"])
                           - float(z142c[f"af_eAll_{s}"]))
fc142_max = max(fc142.values())
fc142_pass = bool(all(v == 0.0 for v in fc142.values()))
log(f"FC-142 eAll (24 keys x 2 seeds) vs raw_l142: "
    f"{'PASS' if fc142_pass else 'FAIL'} (max {fc142_max:.1e})")''',
    '''fc144 = {}
for s in (801, 901):
    for key in C0A150_KEYS:
        fc144[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_silW_{s}"]
            - z144c[f"{key}_sil1110_wA_{s}"][:WIN]).max())
    fc144[f"af_{s}"] = abs(float(store[f"af_silW_{s}"])
                           - float(z144c[f"af_sil1110_wA_{s}"]))
fc144_max = max(fc144.values())
fc144_pass = bool(all(v == 0.0 for v in fc144.values()))
log(f"FC-144 silW (24 keys x 2 seeds) vs raw_l144 sil1110_wA: "
    f"{'PASS' if fc144_pass else 'FAIL'} (max {fc144_max:.1e})")
z145c = np.load("l145/raw_l145.npz")
assert all(f"{_k}_eMotTop5_801" in z145c.files for _k in C0A150_KEYS), \\
    "FC-145 coverage miss"
fc145 = {}
for _ea in ("eMotTop5", "eMotBot5"):
    for s in (801, 901):
        for key in C0A150_KEYS:
            fc145[f"{_ea}_{key}_{s}"] = float(np.abs(
                store[f"{key}_{_ea}_{s}"]
                - z145c[f"{key}_{_ea}_{s}"][:WIN]).max())
        fc145[f"{_ea}_af_{s}"] = abs(float(store[f"af_{_ea}_{s}"])
                                     - float(z145c[f"af_{_ea}_{s}"]))
fc145_max = max(fc145.values())
fc145_pass = bool(all(v == 0.0 for v in fc145.values()))
log(f"FC-145 eMot arms (2 x 24 keys x 2 seeds) vs raw_l145: "
    f"{'PASS' if fc145_pass else 'FAIL'} (max {fc145_max:.1e})")''')

# ---- 15. SE-ID + A-EALL blocks -> DELETE (no such arms here) ----
_i0 = src.index("seid = {}")
_i1 = src.index("out = dict(")
src = src[:_i0] + src[_i1:]
n_reps += 1

# ---- 16. out dict + final log ----
rep('''out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),
           g_eAll=GAIN["eAll"], g_se0=GAIN["se0"],
           g_eall_stored_exact=bool(GAIN["eAll"] == G_EALL_STORED),
           clamp_loc=467, clamp_id=1110,
           e_band_ok=e_band_ok, new_stairs=new_stairs,
           e_edges=E_EDGES, K=K, mass_split=mass_split,
           n_seeds=len(SEEDS), g_eall_vs_g25=g_eall_vs_g25,
           a_eall_max=a_eall_max,
           c0a150_max=c0a150_max, c0a150_pass=c0a150_pass,
           fc142_max=fc142_max, fc142_pass=fc142_pass,
           seid_max=seid_max, seid_pass=seid_pass,
           c0a_pass=bool(c0a150_pass and fc142_pass and seid_pass))
json.dump(out, open("l148/anchors_run.json", "w"), indent=1)
log(f"C0A-148 {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(c0a {out['c0a150_max']:.1e} | FC-142 {out['fc142_max']:.1e} | "
    f"SE-ID {out['seid_max']:.1e}) | A-EALL max {a_eall_max:.1e} | "
    f"done {time.time()-t0:.0f}s")''',
    '''out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),
           g_silW=GAIN["silW"], g_eMotTop5=GAIN["eMotTop5"],
           g_eMotBot5=GAIN["eMotBot5"],
           g_emottop5_stored_exact=bool(
               GAIN["eMotTop5"] == G_EMOTTOP5_STORED),
           g_emotbot5_stored_exact=bool(
               GAIN["eMotBot5"] == G_EMOTBOT5_STORED),
           clamp_loc=467, clamp_id=1110,
           e_band_ok=e_band_ok, new_stairs=new_stairs,
           e_edges=E_EDGES, K=K, mass_split=mass_split,
           n_seeds=len(SEEDS),
           c0a150_max=c0a150_max, c0a150_pass=c0a150_pass,
           fc144_max=fc144_max, fc144_pass=fc144_pass,
           fc145_max=fc145_max, fc145_pass=fc145_pass,
           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass))
json.dump(out, open("l150/anchors_run.json", "w"), indent=1)
log(f"C0A-150 {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(c0a {out['c0a150_max']:.1e} | FC-144 {out['fc144_max']:.1e} | "
    f"FC-145 {out['fc145_max']:.1e}) | done {time.time()-t0:.0f}s")''')

open("l150_run.py", "w").write(src)
print(f"l150_run.py written ({len(src.splitlines())} lines, {n_reps} rep ops)")

# ---- residual token scan (l126/l131 law): code lines must be clean;
# npz path literals are the disclosed whitelist (deliberate cross-run
# inputs: the absence precheck reads the prior runs' raws) ----
BAD = ("eAll", "se0", "B32", "EALL", "seid")
PATH_RE = re.compile(r'^\s*"[^"]*\.npz",?$')
survivors = []
for ln_no, ln in enumerate(src.splitlines(), 1):
    if PATH_RE.match(ln):
        continue
    if any(b in ln for b in BAD):
        survivors.append((ln_no, ln.strip()))
assert not survivors, ("retired-arm token survivors", survivors)
print("residual scan: PASS (zero retired-arm tokens outside npz paths)")
