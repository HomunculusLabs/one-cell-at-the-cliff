"""Build l125_run.py from l124_run.py via exact-string transforms.

L125 = window-scramble control on FRESH B20: cutscr0 (deterministic
max-mass k19+ranks30-39) + cutscr1/2/3 (pinned-RNG 10-of-pool draws),
FRESH-bisected; cutwA/cutwB arms REMOVED (batch union complete). (1)
docstring splice (opener guard), (2) ARMS/GAIN lists, (3) wA/wB stored
consts deleted, (4) B19->B20 rename + seed range, (5) absence list +=
raw_l124, (6) S123->S125 static load, (7) NEW_ARMS tuple, (8) window-
halves block -> scramble block (pins from l125/static.json, values
INLINED from the stored json), (9) wA/wB drift asserts -> scr asserts,
(10) bespoke per-arm sites (W build, pos/mask, POOLS, mech, motor, dng100,
WB, N_OF, Xc/noise dicts, bisect gains dict), (11) stored-loop trim,
(12) FRESH scr bisect loop, (13) output paths l124->l125 (resume FIRST —
L39 direction class), (14) savez kwargs, (15) C0A-123 trim to 3 shared
arms, (16) NEW C0A-124 forward chain, (17) out-dict. Residual scan +
input-direction whitelist + py_compile; every rep count-pinned (L123
anchored-rep discipline). Pin values inlined FROM l125/static.json.
"""
import json
import py_compile
import sys

SRC = open("l124_run.py").read()
S125 = json.load(open("l125/static.json"))
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


# 1. docstring splice (opener guard)
NEW_DOC = '''"""L125 run: window-SCRAMBLE control on FRESH B20. PREREG
l125/PREREG.md FIRST (card amendment registered there: the +-.01 window
mass match is infeasible; scr0 = deterministic max-mass arm .2490).

L124 machinery VERBATIM (pools, graphs, draw order) — scramble arms
cutscr0/1/2/3 = k19 + 10 NON-window ng cells (scr0 = ranks 30-39
deterministic; scr1-3 = pinned-RNG 10-of-pool, l125/static.json pins),
re-rolled on FRESH B20 2401-2416 (asserted absent from raw_l113 + l115 +
l117 + l118 + l119 + l120 + l121 + l122 + l123 + l124). Endpoint gains
STORED-FORM (re-bisect EXACT); scramble arms FRESH bisects (staircase +
band DISCLOSED). The L123 window-half arms are NOT re-run (batch union
n=32 complete); their drop-set identity is re-pinned by l125_static.py
as extraction regression only.
C0A-123 retained on the 3 shared arms + NEW C0A-124 forward chain vs
raw_l124. CPU-only; raw checkpoint BEFORE analysis.
"""'''
assert SRC.startswith('"""L124 run:') and SRC.count('"""L124 run:') == 1, \
    "docstring opener drift"
_doc_end = SRC.index('"""', 3) + 3
SRC = NEW_DOC + SRC[_doc_end:]
print("ok x1: run docstring spliced")

# 2. ARMS/GAIN lists
rep('''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutwA", "cutwB", "cutng19", "cutng29", "cutk5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutwA=None, cutwB=None, cutng19=None, cutng29=None, cutk5=None)''',
    '''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutscr0", "cutscr1", "cutscr2", "cutscr3", "cutng19", "cutng29",
        "cutk5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutscr0=None, cutscr1=None, cutscr2=None, cutscr3=None,
            cutng19=None, cutng29=None, cutk5=None)''', count=1)

# 3. wA/wB stored consts deleted
rep('''G_CUTWA_STORED = 0.14365819573402408  # l123 fresh gain -> stored-form (C0A-123)
G_CUTWB_STORED = 0.14922914385795596  # l123 fresh gain -> stored-form (C0A-123)
''',
    '''# (L125: wA/wB stored consts removed — arms not run here; C0A-123 is
# retained on the 3 shared arms only.)
''', count=1)

# 4. batch rename (docstring already replaced; 8 code sites) + seed range
rep("B19", "B20", count=8)
rep("B20 = list(range(2301, 2317))  # fresh, absent l113..l123 incl raw_l123",
    "B20 = list(range(2401, 2417))  # fresh, absent l113..l124 incl raw_l124",
    count=1)

# 5. absence list += raw_l124
rep('''              "l122/raw_l122.npz", "l123/raw_l123.npz"):''',
    '''              "l122/raw_l122.npz", "l123/raw_l123.npz",
              "l124/raw_l124.npz"):''', count=1)

# 6. static load S123 -> S125
rep('S123 = json.load(open("l123/static.json"))',
    'S125 = json.load(open("l125/static.json"))', count=1)

# 6b. stale L123 section comment -> L125 (it references removed S123 pins)
rep('''# L123: ng[19:29] window XOR — window = ng_desc[19:29] (mass-desc ranks
# 20-29); cutwA = ng_desc[:24] (k19 + ranks 20-24); cutwB = ng_desc[:19] +
# ng_desc[24:29] (k19 + ranks 25-29). Both drop 24 cells, quasi-mass-
# matched .2286 vs .2248 (DISCLOSED). l121/static.json pins for k19/k29/k58
# (re-pinned EXACT by l123_static.py) + l123/static.json pins for wA/wB;
# retained cutk5 anchor arm (pins == l117/l119/l120 stored EXACT).''',
    '''# L125: window-scramble control — drop k19 + 10 NON-window ng cells
# instead of the ng[19:29] window; l121/static.json pins for k19/k29/k58
# (re-pinned EXACT by l125_static.py) + l125/static.json pins for the
# scr arms; retained cutk5 anchor arm (pins == l117/l119/l120 stored
# EXACT). The L123 window halves themselves are NOT run here.''', count=1)

# 7. NEW_ARMS tuple
rep('NEW_ARMS = ("cutk5", "cutng19", "cutng29", "cutwA", "cutwB")',
    'NEW_ARMS = ("cutk5", "cutng19", "cutng29", "cutscr0", "cutscr1",\n'
    '            "cutscr2", "cutscr3")', count=1)

# 8. window-halves block -> scramble block
rep('''# window halves (l123/static.json pins)
_wA = np.sort(ng_desc[:24])
_wB = np.sort(np.concatenate([ng_desc[:19], ng_desc[24:29]]))
assert len(_wA) == len(_wB) == 24
assert np.array_equal(
    np.union1d(_wA, _wB),
    np.array(S121["ngladder"]["k29"]["drop_ids"], np.int64)), \\
    "wA|wB != k29 window (STOP)"
assert np.array_equal(
    np.intersect1d(_wA, _wB), np.sort(ng_desc[:19])), \\
    "halves overlap beyond k19 (STOP)"
for _a, _drop in (("cutwA", _wA), ("cutwB", _wB)):
    _pin = S123["window_" + _a[-2:]]
    assert _pin["drop_ids"] == [int(x) for x in _drop], (_a, "drop drift")
    assert np.isin(_drop, cut58_drop).all()
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin''',
    '''# L125 scramble draws (l125/static.json pins): k19 + 10 NON-window ng
# cells. scr0 = deterministic max-mass (ranks 30-39, .2490); scr1-3 =
# pinned-RNG draws from the ranks-30-58 pool (masses DISCLOSED per draw;
# card amendment in PREREG).
_ng_pool = np.sort(ng_desc[29:58])               # ranks 30-58 (29 cells)
assert len(_ng_pool) == 29
for _a in ("cutscr0", "cutscr1", "cutscr2", "cutscr3"):
    _pin = S125["scr"][_a]
    _extra = np.sort(np.array(_pin["extra_ids_desc"], np.int64))
    assert len(_extra) == 10 and np.isin(_extra, _ng_pool).all(), \\
        (_a, "extra not in ranks 30-58 (STOP)")
    assert not np.isin(_extra, ng_desc[:29]).any(), (_a, "extra in k29")
    _drop = np.sort(np.concatenate([ng_desc[:19], _extra]))
    assert len(_drop) == 29
    assert _pin["drop_ids"] == [int(x) for x in _drop], (_a, "drop drift")
    assert np.isin(_drop, cut58_drop).all()
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin''', count=1)

# 9. wA/wB drift asserts -> scr asserts (values INLINED from static json)
_sc = S125["scr"]
_lines = ["for _a, _m, _e in ("]
for a in ("cutscr0", "cutscr1", "cutscr2", "cutscr3"):
    _lines.append(f'    ("{a}", {repr(_sc[a]["mass_removed"])}, '
                  f'{_sc[a]["edges"]}),')
_lines.append('''):
    assert cutk_pins[_a]["mass_removed"] == _m, (_a, "mass drift (STOP)")
    assert cutk_pins[_a]["edges"] == _e, (_a, "edges drift (STOP)")
    assert cutk_pins[_a]["n"] == 21780, (_a, "n drift (STOP)")''')
rep('''assert cutk_pins["cutwA"]["mass_removed"] == 0.2286, "wA mass drift (STOP)"
assert cutk_pins["cutwB"]["mass_removed"] == 0.2248, "wB mass drift (STOP)"
assert cutk_pins["cutwA"]["edges"] == 644177, "wA edges drift (STOP)"
assert cutk_pins["cutwB"]["edges"] == 644174, "wB edges drift (STOP)"''',
    "\n".join(_lines), count=1)

# 10a. W build lines
rep('''Wc_wA, loc_wA = build(keep_cutk["cutwA"])
Wc_wB, loc_wB = build(keep_cutk["cutwB"])''',
    '''Wc_s0, loc_s0 = build(keep_cutk["cutscr0"])
Wc_s1, loc_s1 = build(keep_cutk["cutscr1"])
Wc_s2, loc_s2 = build(keep_cutk["cutscr2"])
Wc_s3, loc_s3 = build(keep_cutk["cutscr3"])''', count=1)
rep('''assert Wc_wA.values().numel() == cutk_pins["cutwA"]["edges"]
assert Wc_wB.values().numel() == cutk_pins["cutwB"]["edges"]''',
    '''for _a, _W in (("cutscr0", Wc_s0), ("cutscr1", Wc_s1),
               ("cutscr2", Wc_s2), ("cutscr3", Wc_s3)):
    assert _W.values().numel() == cutk_pins[_a]["edges"], (_a, "Wc edges")''',
    count=1)
rep('''Wb_ng19, Wb_ng29, Wb_wA, Wb_wB, Wb_k5 = (wb(Wc_ng19), wb(Wc_ng29),
                                        wb(Wc_wA), wb(Wc_wB), wb(Wc_k5))''',
    '''Wb_ng19, Wb_ng29, Wb_s0, Wb_s1, Wb_s2, Wb_s3, Wb_k5 = (
    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_s0), wb(Wc_s1), wb(Wc_s2),
    wb(Wc_s3), wb(Wc_k5))''', count=1)

# 10b. pos/mask blocks (generate 4)
_pos = []
for tag, arm in (("s0", "cutscr0"), ("s1", "cutscr1"),
                 ("s2", "cutscr2"), ("s3", "cutscr3")):
    _pos.append(f'''gi_{tag} = np.where(keep_cutk["{arm}"])[0]
{tag}_pos_in_new = loc_n[gi_{tag}]
old_pos_in_{tag} = loc_{tag}[gi_old]
kept_new_mask_{tag} = keep_cutk["{arm}"][new_g]
kept_new_cut{arm} = loc_{tag}[new_g[kept_new_mask_{tag}]]''')
rep('''gi_wA = np.where(keep_cutk["cutwA"])[0]
wA_pos_in_new = loc_n[gi_wA]
old_pos_in_wA = loc_wA[gi_old]
kept_new_mask_wA = keep_cutk["cutwA"][new_g]
kept_new_cutwA = loc_wA[new_g[kept_new_mask_wA]]
gi_wB = np.where(keep_cutk["cutwB"])[0]
wB_pos_in_new = loc_n[gi_wB]
old_pos_in_wB = loc_wB[gi_old]
kept_new_mask_wB = keep_cutk["cutwB"][new_g]
kept_new_cutwB = loc_wB[new_g[kept_new_mask_wB]]''',
    "\n".join(_pos), count=1)

# 10c. POOLS entries
rep('''         "cutwA": pools_for(loc_wA, keep_cutk["cutwA"]),
         "cutwB": pools_for(loc_wB, keep_cutk["cutwB"]),''',
    '''         "cutscr0": pools_for(loc_s0, keep_cutk["cutscr0"]),
         "cutscr1": pools_for(loc_s1, keep_cutk["cutscr1"]),
         "cutscr2": pools_for(loc_s2, keep_cutk["cutscr2"]),
         "cutscr3": pools_for(loc_s3, keep_cutk["cutscr3"]),''', count=1)
rep('''    for _da in ("cutwA", "cutwB", "cutng19", "cutng29", "cutk5"):''',
    '''    for _da in ("cutscr0", "cutscr1", "cutscr2", "cutscr3", "cutng19",
                "cutng29", "cutk5"):''', count=1)
rep('''    for a in ("cut", "cut19", "cut58", "cutng19", "cutng29", "cutwA",
              "cutwB", "cutk5", "b65"):''',
    '''    for a in ("cut", "cut19", "cut58", "cutng19", "cutng29", "cutscr0",
              "cutscr1", "cutscr2", "cutscr3", "cutk5", "b65"):''', count=1)

# 10d. mech entries
rep('''        "cutwA": np.where(mech_mask[keep_cutk["cutwA"]])[0],
        "cutwB": np.where(mech_mask[keep_cutk["cutwB"]])[0],''',
    '''        "cutscr0": np.where(mech_mask[keep_cutk["cutscr0"]])[0],
        "cutscr1": np.where(mech_mask[keep_cutk["cutscr1"]])[0],
        "cutscr2": np.where(mech_mask[keep_cutk["cutscr2"]])[0],
        "cutscr3": np.where(mech_mask[keep_cutk["cutscr3"]])[0],''', count=1)

# 10e. motor dict + loop
rep('''          ("cutwA", n_cutk["cutwA"]), ("cutwB", n_cutk["cutwB"]),''',
    '''          ("cutscr0", n_cutk["cutscr0"]), ("cutscr1", n_cutk["cutscr1"]),
          ("cutscr2", n_cutk["cutscr2"]), ("cutscr3", n_cutk["cutscr3"]),''',
    count=1)
rep('''                     ("cutwA", keep_cutk["cutwA"], loc_wA),
                     ("cutwB", keep_cutk["cutwB"], loc_wB),''',
    '''                     ("cutscr0", keep_cutk["cutscr0"], loc_s0),
                     ("cutscr1", keep_cutk["cutscr1"], loc_s1),
                     ("cutscr2", keep_cutk["cutscr2"], loc_s2),
                     ("cutscr3", keep_cutk["cutscr3"], loc_s3),''', count=1)

# 10f. dng100 entries + assert loop
rep('''          "cutwA": np.sort(loc_wA[dng100_all[keep_cutk["cutwA"][dng100_all]]]),
          "cutwB": np.sort(loc_wB[dng100_all[keep_cutk["cutwB"][dng100_all]]]),''',
    '''          "cutscr0": np.sort(loc_s0[dng100_all[keep_cutk["cutscr0"][dng100_all]]]),
          "cutscr1": np.sort(loc_s1[dng100_all[keep_cutk["cutscr1"][dng100_all]]]),
          "cutscr2": np.sort(loc_s2[dng100_all[keep_cutk["cutscr2"][dng100_all]]]),
          "cutscr3": np.sort(loc_s3[dng100_all[keep_cutk["cutscr3"][dng100_all]]]),''',
    count=1)
rep('''for _da in ("cutwA", "cutwB", "cutng19", "cutng29", "cutk5"):''',
    '''for _da in ("cutscr0", "cutscr1", "cutscr2", "cutscr3", "cutng19",
            "cutng29", "cutk5"):''', count=1)

# 10g. WB / N_OF
rep('''      "cutng19": Wb_ng19, "cutng29": Wb_ng29, "cutwA": Wb_wA,
      "cutwB": Wb_wB, "cutk5": Wb_k5,''',
    '''      "cutng19": Wb_ng19, "cutng29": Wb_ng29, "cutscr0": Wb_s0,
      "cutscr1": Wb_s1, "cutscr2": Wb_s2, "cutscr3": Wb_s3,
      "cutk5": Wb_k5,''', count=1)
rep('''        "cutwA": n_cutk["cutwA"], "cutwB": n_cutk["cutwB"],''',
    '''        "cutscr0": n_cutk["cutscr0"], "cutscr1": n_cutk["cutscr1"],
        "cutscr2": n_cutk["cutscr2"], "cutscr3": n_cutk["cutscr3"],''',
    count=1)

# 10h. Xc blocks (settle + rollout, same 4-space text) + st/X dict lines
_xc = []
for tag, arm in (("s0", "cutscr0"), ("s1", "cutscr1"),
                 ("s2", "cutscr2"), ("s3", "cutscr3")):
    _xc.append(f'''    Xc_{tag} = torch.zeros(n_cutk["{arm}"], 1)
    Xc_{tag}[old_pos_in_{tag}] = X0o
    Xc_{tag}[kept_new_cut{arm}] = X0n[kept_new_mask_{tag}]''')
rep('''    Xc_wA = torch.zeros(n_cutk["cutwA"], 1)
    Xc_wA[old_pos_in_wA] = X0o
    Xc_wA[kept_new_cutwA] = X0n[kept_new_mask_wA]
    Xc_wB = torch.zeros(n_cutk["cutwB"], 1)
    Xc_wB[old_pos_in_wB] = X0o
    Xc_wB[kept_new_cutwB] = X0n[kept_new_mask_wB]''',
    "\n".join(_xc), count=2)
rep('''              cutwA=Xc_wA.clone(), cutwB=Xc_wB.clone(), cutk5=Xc_k5.clone(),''',
    '''              cutscr0=Xc_s0.clone(), cutscr1=Xc_s1.clone(),
              cutscr2=Xc_s2.clone(), cutscr3=Xc_s3.clone(),
              cutk5=Xc_k5.clone(),''', count=1)
rep('''             cutwA=Xc_wA.clone(), cutwB=Xc_wB.clone(), cutk5=Xc_k5.clone(),''',
    '''             cutscr0=Xc_s0.clone(), cutscr1=Xc_s1.clone(),
             cutscr2=Xc_s2.clone(), cutscr3=Xc_s3.clone(),
             cutk5=Xc_k5.clone(),''', count=1)

# 10i. noise dicts (settle + WIN, same 21-space text)
rep('''                     cutwA=nzn[wA_pos_in_new],
                     cutwB=nzn[wB_pos_in_new],''',
    '''                     cutscr0=nzn[s0_pos_in_new],
                     cutscr1=nzn[s1_pos_in_new],
                     cutscr2=nzn[s2_pos_in_new],
                     cutscr3=nzn[s3_pos_in_new],''', count=3)

# 10j. bisect_af_mean gains dict
rep('''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutng19=g, cutng29=g, cutwA=g, cutwB=g,
                                  cutk5=g))''',
    '''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutng19=g, cutng29=g,
                                  cutscr0=g, cutscr1=g, cutscr2=g,
                                  cutscr3=g, cutk5=g))''', count=1)

# 11. stored-loop comment + tuple + _st trim
rep('''# L124 form: ALL dose/window gains are STORED-FORM anchors (re-bisect
# EXACT): ng endpoints from l121, window halves from l123. Staircase +
# band disclosures retained per PREREG (never an abort).
new_stairs = {}
for _a in ("cutng19", "cutng29", "cutwA", "cutwB"):''',
    '''# L125 form: endpoint gains are STORED-FORM anchors (re-bisect EXACT,
# l121); scramble arms are FRESH bisects below. Staircase + band
# disclosures retained per PREREG (never an abort).
new_stairs = {}
for _a in ("cutng19", "cutng29"):''', count=1)
rep('''    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,
           "cutwA": G_CUTWA_STORED, "cutwB": G_CUTWB_STORED}[_a]''',
    '''    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED}[_a]''',
    count=1)

# 12. FRESH scr bisect loop (l123 form) replaces the deleted-loop comment
rep('''# (L124: the L123 fresh cutwA/cutwB bisect loop is DELETED — both gains
# are stored-form now; the stored loop above re-bisects them EXACT.)''',
    '''# L125 FRESH bisects: scramble arms (staircase + band DISCLOSED per
# PREREG — the .14-.16 band is a disclosure, never an abort).
for _a in ("cutscr0", "cutscr1", "cutscr2", "cutscr3"):
    lo_d, hi_d = 0.12, 0.18
    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _a), bisect_af_mean(hi_d, _a)
    log(f"{_a} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo_d < AF_T < af_hi_d, f"{_a} bracket fail"
    for it in range(24):
        mid = (lo_d + hi_d) / 2
        if bisect_af_mean(mid, _a) < AF_T:
            lo_d = mid
        else:
            hi_d = mid
    GAIN[_a] = lo_d
    af_d = bisect_af_mean(lo_d, _a)
    new_stairs[_a] = abs(af_d - AF_T)
    _band = " [OUTSIDE PREREG band .14-.16 — DISCLOSED]" \\
        if not (0.14 <= lo_d <= 0.16) else ""
    log(f"g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "
        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")''', count=1)

# 13. output paths l124 -> l125 (resume path FIRST — L39 direction class)
rep('if os.path.exists("l124/raw_partial.npz"):',
    'if os.path.exists("l125/raw_partial.npz"):', count=1)
rep('z = np.load("l124/raw_partial.npz")',
    'z = np.load("l125/raw_partial.npz")', count=1)
rep('np.savez("l124/raw_partial.npz", **store)',
    'np.savez("l125/raw_partial.npz", **store)', count=1)
rep('np.savez_compressed("l124/raw_l124.npz"',
    'np.savez_compressed("l125/raw_l125.npz"', count=1)
rep('log("raw_l124.npz checkpointed BEFORE analysis")',
    'log("raw_l125.npz checkpointed BEFORE analysis")', count=1)
rep('json.dump(out, open("l124/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l125/anchors_run.json", "w"), indent=1)', count=1)

# 14. savez kwargs
rep('''                    g_cutwA=GAIN["cutwA"], g_cutwB=GAIN["cutwB"],''',
    '''                    g_cutscr0=GAIN["cutscr0"], g_cutscr1=GAIN["cutscr1"],
                    g_cutscr2=GAIN["cutscr2"], g_cutscr3=GAIN["cutscr3"],''',
    count=1)
rep('''                    cutwA_drop=cutk_drop["cutwA"], cutwB_drop=cutk_drop["cutwB"],''',
    '''                    cutscr0_drop=cutk_drop["cutscr0"],
                    cutscr1_drop=cutk_drop["cutscr1"],
                    cutscr2_drop=cutk_drop["cutscr2"],
                    cutscr3_drop=cutk_drop["cutscr3"],''', count=1)

# 15. C0A-123 trim to 3 shared arms
rep('''# C0A-123 (NEW anchor class): forward chain — {cutk5,cutng19,cutng29,
# cutwA,cutwB} at stored seeds vs raw_l123 (l123 ran every arm at all 18
# seeds).''',
    '''# C0A-123 (RETAINED, 3 shared arms): {cutk5,cutng19,cutng29} at stored
# seeds vs raw_l123 (wA/wB trimmed — not run in L125; DISCLOSED).''',
    count=1)
rep('''        for a in ("cutk5", "cutng19", "cutng29", "cutwA", "cutwB"):
            c0a123[f"123_{key}_{a}_{s}"]''',
    '''        for a in ("cutk5", "cutng19", "cutng29"):
            c0a123[f"123_{key}_{a}_{s}"]''', count=1)
rep('''    for a in ("cutk5", "cutng19", "cutng29", "cutwA", "cutwB"):
        c0a123[f"123_af_{a}_{s}"]''',
    '''    for a in ("cutk5", "cutng19", "cutng29"):
        c0a123[f"123_af_{a}_{s}"]''', count=1)
rep('''log(f"C0A-123 forward chain vs raw_l123: {'PASS' if c0a123_pass else 'FAIL'} "
    f"(max {c0a123_max:.1e}, {len(C0A120_KEYS)} keys x 5 arms x 2 seeds)")''',
    '''log(f"C0A-123 (3 shared arms) vs raw_l123: {'PASS' if c0a123_pass else 'FAIL'} "
    f"(max {c0a123_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")''',
    count=1)

# 16. NEW C0A-124 forward chain (after the C0A-123 log)
rep('''log(f"C0A-123 (3 shared arms) vs raw_l123: {'PASS' if c0a123_pass else 'FAIL'} "
    f"(max {c0a123_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")''',
    '''log(f"C0A-123 (3 shared arms) vs raw_l123: {'PASS' if c0a123_pass else 'FAIL'} "
    f"(max {c0a123_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")
# C0A-124 (NEW anchor class): forward chain — {cutk5,cutng19,cutng29} at
# stored seeds vs raw_l124 (l124 ran every arm at all 18 seeds).
z124c = np.load("l124/raw_l124.npz")
c0a124 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29"):
            c0a124[f"124_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z124c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29"):
        c0a124[f"124_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z124c[f"af_{a}_{s}"]))
c0a124_max = max(c0a124.values())
c0a124_pass = bool(all(v == 0.0 for v in c0a124.values()))
log(f"C0A-124 forward chain vs raw_l124: {'PASS' if c0a124_pass else 'FAIL'} "
    f"(max {c0a124_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")''',
    count=1)

# 17. covered-keys log + out-dict
rep('''    f"| NEW arms excluded (no l113 counterpart): ['cutk5','cutng19','cutng29',"
    "'cutwA'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120)")''',
    '''    f"| NEW arms excluded (no l113 counterpart): ['cutk5','cutng19','cutng29',"
    "'cutscr0'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120)")''',
    count=1)
rep('''           g_cutwA=GAIN["cutwA"], g_cutwB=GAIN["cutwB"],''',
    '''           g_cutscr0=GAIN["cutscr0"], g_cutscr1=GAIN["cutscr1"],
           g_cutscr2=GAIN["cutscr2"], g_cutscr3=GAIN["cutscr3"],''', count=1)
rep('''           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutwA", "cutwB"))),''',
    '''           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutscr0", "cutscr1", "cutscr2",
                                           "cutscr3"))),''', count=1)
rep('''           c0a123_max=c0a123_max, c0a123_pass=c0a123_pass,
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           g_cutwB_stored_exact=bool(GAIN["cutwB"] == G_CUTWB_STORED),''',
    '''           c0a123_max=c0a123_max, c0a123_pass=c0a123_pass,
           c0a124_max=c0a124_max, c0a124_pass=c0a124_pass,
           scr_fresh_gains={a: GAIN[a] for a in
                            ("cutscr0", "cutscr1", "cutscr2", "cutscr3")},''',
    count=1)
rep('''           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass
                          and c0a121_pass and c0a122_pass and c0a123_pass))''',
    '''           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass
                          and c0a121_pass and c0a122_pass and c0a123_pass
                          and c0a124_pass))''', count=1)

open("l125_run.py", "w").write(SRC)

# ---------------- residual scan + direction check ----------------
bad = []
s = open("l125_run.py").read()
for tok in ("B19", "2301", "2316", "cutwA", "cutwB", "Xc_wA", "loc_wA",
            "Wc_wA", "Wb_wA", "S123"):
    if tok in s:
        bad.append(("l125_run.py", "stale token " + tok))
import re
# l1xx inputs are LEGITIMATE (static pins + raw C0A anchors); the ONLY
# output paths must be l125/*.
OK_IN = {"l107/static.json", "l92/static.json", "l101/static.json",
         "l121/static.json", "l125/static.json", "l113/raw_l113.npz",
         "l115/raw_l115.npz", "l117/raw_l117.npz", "l118/raw_l118.npz",
         "l119/raw_l119.npz", "l120/raw_l120.npz", "l121/raw_l121.npz",
         "l122/raw_l122.npz", "l123/raw_l123.npz", "l124/raw_l124.npz"}
for m in re.finditer(r'"(l1\d+/[^"]+)"', s):
    p = m.group(1)
    if p.startswith("l125/"):
        continue
    if p not in OK_IN:
        bad.append(("l125_run.py", "unexpected l-path " + p))
if n_err or bad:
    print("BUILD FAIL:", n_err, bad)
    sys.exit(1)
py_compile.compile("l125_run.py", doraise=True)
print("BUILD OK: l125_run.py compiled; scans clean (verdict built separately)")
