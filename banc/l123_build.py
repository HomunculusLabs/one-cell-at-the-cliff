"""Build l123_run.py from l122_run.py via exact-string transforms.

Strategy (opener-splice for long blocks, count-pinned reps, L122 lesson):
(1) docstring splice (unique opener guard), (2) ladder-block splice between
two unique markers (the ONLY place arm construction changes), (3) remove the
cutng39 stored-form machinery (const, _st entry, out-dict boolean, C0A-121
arm narrowing), (4) wholesale cutng39->cutwA + var renames ng39->wA,
(5) fresh bisect loop for cutwA/cutwB, (6) cutwB twins at every keyed site,
(7) NEW C0A-122 forward-chain block, (8) B18/2201/absence-list, (9) output
paths l122->l123, (10) residual scan + input-direction whitelist +
py_compile. Every rep prints its count; zero/mismatch aborts (drift guard).
"""
import py_compile
import sys

SRC = open("l122_run.py").read()
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
NEW_DOC = '''"""L123 run: ng[19:29] window XOR on FRESH B18. PREREG
l123/PREREG.md FIRST.

L122 machinery VERBATIM (10 arms, 5-pair pools, graphs, draw order) —
window arms cutwA = ng_desc[:24] (k19 + ranks 20-24) and cutwB =
ng_desc[:19] + ng_desc[24:29] (k19 + ranks 25-29), quasi-mass-matched
.2286 vs .2248 (l123/static.json pins; halves partition the k29 window
EXACTLY, asserted). FRESH B18 2201-2216 (asserted absent from raw_l113 +
l115 + l117 + l118 + l119 + l120 + l121 + l122). ng gains cutng19/29
STORED-FORM anchors; cutwA/cutwB bisected FRESH (band disclosure).
C0A-120/121 retained (3 arms) + NEW C0A-122 forward chain
(cutk5/cutng19/cutng29 vs raw_l122 at 801/901). CPU-only; raw checkpoint
BEFORE analysis.
"""'''
assert SRC.startswith('"""L122 run:') and SRC.count('"""L122 run:') == 1, \
    "docstring opener drift"
_doc_end = SRC.index('"""', 3) + 3
SRC = NEW_DOC + SRC[_doc_end:]
print("ok x1: run docstring spliced")

# 2. ladder-block splice between unique markers
M_START = "# L121: non-glut dose ladder"
M_END = "# (DNg100-not-in-heavy-77 asserted downstream"
assert SRC.count(M_START) == 1 and SRC.count(M_END) == 1, "ladder markers"
NEW_LADDER = '''# L123: ng[19:29] window XOR — window = ng_desc[19:29] (mass-desc ranks
# 20-29); cutwA = ng_desc[:24] (k19 + ranks 20-24); cutwB = ng_desc[:19] +
# ng_desc[24:29] (k19 + ranks 25-29). Both drop 24 cells, quasi-mass-
# matched .2286 vs .2248 (DISCLOSED). l121/static.json pins for k19/k29/k58
# (re-pinned EXACT by l123_static.py) + l123/static.json pins for wA/wB;
# retained cutk5 anchor arm (pins == l117/l119/l120 stored EXACT).
S121 = json.load(open("l121/static.json"))
S123 = json.load(open("l123/static.json"))
NEW_ARMS = ("cutk5", "cutng19", "cutng29", "cutwA", "cutwB")
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
# window endpoints: k19/k29 positional prefixes (l121 stored pins)
for _pk, _a, _kk in (("k19", "cutng19", 19), ("k29", "cutng29", 29)):
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
# window halves (l123/static.json pins)
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
    cutk_pins[_a] = _pin
assert [int(x) for x in cutk_drop["cutk5"]] == [204, 286, 313, 561, 32014]
assert cutk_pins["cutk5"]["mass_removed"] == 0.0425, "k5 mass drift (STOP)"
assert cutk_pins["cutk5"]["edges"] == 647252, "k5 edges drift (STOP)"
assert cutk_pins["cutng19"]["mass_removed"] == 0.1946, "ng19 mass drift (STOP)"
assert cutk_pins["cutng29"]["mass_removed"] == 0.2588, "ng29 mass drift (STOP)"
assert cutk_pins["cutng19"]["edges"] == 644729, "ng19 edges drift (STOP)"
assert cutk_pins["cutng29"]["edges"] == 643623, "ng29 edges drift (STOP)"
assert cutk_pins["cutwA"]["mass_removed"] == 0.2286, "wA mass drift (STOP)"
assert cutk_pins["cutwB"]["mass_removed"] == 0.2248, "wB mass drift (STOP)"
assert cutk_pins["cutwA"]["edges"] == 644177, "wA edges drift (STOP)"
assert cutk_pins["cutwB"]["edges"] == 644174, "wB edges drift (STOP)"
assert S121["ngladder"]["k58"]["edges"] == int(
    (keep_cut58[src_all] & keep_cut58[dst_all]).sum()), "k58 != cut58 arm (STOP)"

'''
_i0, _i1 = SRC.index(M_START), SRC.index(M_END)
SRC = SRC[:_i0] + NEW_LADDER + SRC[_i1:]
print("ok x1: ladder block spliced")

# 3. remove cutng39 stored-form machinery
rep('G_CUTNG39_STORED = 0.1462542486190796  # l121 fresh gain -> stored-form (C0A-121)\n', '')
rep('''    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,
           "cutng39": G_CUTNG39_STORED}[_a]''',
    '''    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED}[_a]''')
rep('           g_cutng39_stored_exact=bool(GAIN["cutng39"] == G_CUTNG39_STORED),\n', '')

# 4. C0A-121 narrowed to the 3 arms run here (+ comment/log honesty)
rep('for a in ("cutk5", "cutng19", "cutng29", "cutng39"):',
    'for a in ("cutk5", "cutng19", "cutng29"):', count=2)
rep('so all four have stored counterparts',
    'so all three run here have stored counterparts')
rep('keys x 4 arms x 2 seeds)', 'keys x 3 arms x 2 seeds)')

# 5. bisect loop: ng endpoints stored; window arms fresh
rep('''# L118: fresh bisects for the draw arms (no stored form; staircase + band
# DISCLOSED per PREREG — the .14-.16 band is a disclosure, never an abort)
new_stairs = {}
for _a in ("cutng19", "cutng29", "cutng39"):''',
    '''# L122 form: ng endpoint gains are STORED-FORM anchors (re-bisect EXACT).
# L123 fresh bisects: cutwA/cutwB only (staircase + band DISCLOSED per
# PREREG — the .14-.16 band is a disclosure, never an abort).
new_stairs = {}
for _a in ("cutng19", "cutng29"):''')
rep('''        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")

# ---------------- rollouts ----------------''',
    '''        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")
for _a in ("cutwA", "cutwB"):
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
        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")

# ---------------- rollouts ----------------''')
rep('''                                 for a in ("cutng19", "cutng29", "cutng39"))),''',
    '''                                 for a in ("cutwA", "cutwB"))),''')

# 6. wholesale renames
rep("cutng39", "cutwA", count=40)
rep("ng39", "wA")
rep("k3_pos_in_new", "wA_pos_in_new")

# 7. batch + absence list
rep("B17", "B18", count=8)
rep("list(range(2101, 2117))", "list(range(2201, 2217))", count=1)
rep('''              "l120/raw_l120.npz", "l121/raw_l121.npz"):''',
    '''              "l120/raw_l120.npz", "l121/raw_l121.npz",
              "l122/raw_l122.npz"):''', count=1)

# 8. cutwB twins (post-rename, keyed on cutwA sites)
rep('''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutwA", "cutng19", "cutng29", "cutk5"]''',
    '''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutwA", "cutwB", "cutng19", "cutng29", "cutk5"]''')
rep('cutwA=None, cutng19=None, cutng29=None, cutk5=None)',
    'cutwA=None, cutwB=None, cutng19=None, cutng29=None, cutk5=None)')
rep('''Wc_wA, loc_wA = build(keep_cutk["cutwA"])''',
    '''Wc_wA, loc_wA = build(keep_cutk["cutwA"])
Wc_wB, loc_wB = build(keep_cutk["cutwB"])''')
rep('''assert Wc_wA.values().numel() == cutk_pins["cutwA"]["edges"]''',
    '''assert Wc_wA.values().numel() == cutk_pins["cutwA"]["edges"]
assert Wc_wB.values().numel() == cutk_pins["cutwB"]["edges"]''')
rep('''Wb_ng19, Wb_ng29, Wb_wA, Wb_k5 = (wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_k5))''',
    '''Wb_ng19, Wb_ng29, Wb_wA, Wb_wB, Wb_k5 = (wb(Wc_ng19), wb(Wc_ng29),
                                        wb(Wc_wA), wb(Wc_wB), wb(Wc_k5))''')
rep('''gi_wA = np.where(keep_cutk["cutwA"])[0]
wA_pos_in_new = loc_n[gi_wA]
old_pos_in_wA = loc_wA[gi_old]
kept_new_mask_wA = keep_cutk["cutwA"][new_g]
kept_new_cutwA = loc_wA[new_g[kept_new_mask_wA]]''',
    '''gi_wA = np.where(keep_cutk["cutwA"])[0]
wA_pos_in_new = loc_n[gi_wA]
old_pos_in_wA = loc_wA[gi_old]
kept_new_mask_wA = keep_cutk["cutwA"][new_g]
kept_new_cutwA = loc_wA[new_g[kept_new_mask_wA]]
gi_wB = np.where(keep_cutk["cutwB"])[0]
wB_pos_in_new = loc_n[gi_wB]
old_pos_in_wB = loc_wB[gi_old]
kept_new_mask_wB = keep_cutk["cutwB"][new_g]
kept_new_cutwB = loc_wB[new_g[kept_new_mask_wB]]''')
rep('''         "cutwA": pools_for(loc_wA, keep_cutk["cutwA"]),''',
    '''         "cutwA": pools_for(loc_wA, keep_cutk["cutwA"]),
         "cutwB": pools_for(loc_wB, keep_cutk["cutwB"]),''')
rep('for _da in ("cutwA", "cutng19", "cutng29", "cutk5"):',
    'for _da in ("cutwA", "cutwB", "cutng19", "cutng29", "cutk5"):', count=2)
rep('''for a in ("cut", "cut19", "cut58", "cutng19", "cutng29", "cutwA",
              "cutk5", "b65"):''',
    '''for a in ("cut", "cut19", "cut58", "cutng19", "cutng29", "cutwA",
              "cutwB", "cutk5", "b65"):''')
rep('''        "cutwA": np.where(mech_mask[keep_cutk["cutwA"]])[0],''',
    '''        "cutwA": np.where(mech_mask[keep_cutk["cutwA"]])[0],
        "cutwB": np.where(mech_mask[keep_cutk["cutwB"]])[0],''')
rep('''          ("cutwA", n_cutk["cutwA"]), ("cutk5", n_cutk["cutk5"]),''',
    '''          ("cutwA", n_cutk["cutwA"]), ("cutwB", n_cutk["cutwB"]),
          ("cutk5", n_cutk["cutk5"]),''')
rep('''                     ("cutwA", keep_cutk["cutwA"], loc_wA),''',
    '''                     ("cutwA", keep_cutk["cutwA"], loc_wA),
                     ("cutwB", keep_cutk["cutwB"], loc_wB),''')
rep('''          "cutwA": np.sort(loc_wA[dng100_all[keep_cutk["cutwA"][dng100_all]]]),''',
    '''          "cutwA": np.sort(loc_wA[dng100_all[keep_cutk["cutwA"][dng100_all]]]),
          "cutwB": np.sort(loc_wB[dng100_all[keep_cutk["cutwB"][dng100_all]]]),''')
rep('''      "cutng19": Wb_ng19, "cutng29": Wb_ng29, "cutwA": Wb_wA, "cutk5": Wb_k5,''',
    '''      "cutng19": Wb_ng19, "cutng29": Wb_ng29, "cutwA": Wb_wA,
      "cutwB": Wb_wB, "cutk5": Wb_k5,''')
rep('''        "cutwA": n_cutk["cutwA"], "cutk5": n_cutk["cutk5"],''',
    '''        "cutwA": n_cutk["cutwA"], "cutwB": n_cutk["cutwB"],
        "cutk5": n_cutk["cutk5"],''')
# Xc init blocks appear twice verbatim (settle + rollout) -> count=2
rep('''    Xc_wA = torch.zeros(n_cutk["cutwA"], 1)
    Xc_wA[old_pos_in_wA] = X0o
    Xc_wA[kept_new_cutwA] = X0n[kept_new_mask_wA]''',
    '''    Xc_wA = torch.zeros(n_cutk["cutwA"], 1)
    Xc_wA[old_pos_in_wA] = X0o
    Xc_wA[kept_new_cutwA] = X0n[kept_new_mask_wA]
    Xc_wB = torch.zeros(n_cutk["cutwB"], 1)
    Xc_wB[old_pos_in_wB] = X0o
    Xc_wB[kept_new_cutwB] = X0n[kept_new_mask_wB]''', count=2)
rep('''              cutwA=Xc_wA.clone(), cutk5=Xc_k5.clone(),''',
    '''              cutwA=Xc_wA.clone(), cutwB=Xc_wB.clone(), cutk5=Xc_k5.clone(),''')
rep('''             cutwA=Xc_wA.clone(), cutk5=Xc_k5.clone(),''',
    '''             cutwA=Xc_wA.clone(), cutwB=Xc_wB.clone(), cutk5=Xc_k5.clone(),''')
rep('''                     cutwA=nzn[wA_pos_in_new],''',
    '''                     cutwA=nzn[wA_pos_in_new],
                     cutwB=nzn[wB_pos_in_new],''', count=3)
rep('''cut58=g, cutng19=g, cutng29=g, cutwA=g,
                                  cutk5=g)''',
    '''cut58=g, cutng19=g, cutng29=g, cutwA=g, cutwB=g,
                                  cutk5=g)''')

# 9. NEW C0A-122 forward chain (insert after the c0a121 log)
rep('''log(f"C0A-121 ng arms vs raw_l121: {'PASS' if c0a121_pass else 'FAIL'} "
    f"(max {c0a121_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")''',
    '''log(f"C0A-121 ng arms vs raw_l121: {'PASS' if c0a121_pass else 'FAIL'} "
    f"(max {c0a121_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")
# C0A-122 (NEW anchor class): forward chain — {cutk5,cutng19,cutng29} at
# stored seeds vs raw_l122 (l122 ran every arm at all 18 seeds).
z122 = np.load("l122/raw_l122.npz")
c0a122 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29"):
            c0a122[f"122_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z122[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29"):
        c0a122[f"122_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z122[f"af_{a}_{s}"]))
c0a122_max = max(c0a122.values())
c0a122_pass = bool(all(v == 0.0 for v in c0a122.values()))
log(f"C0A-122 forward chain vs raw_l122: {'PASS' if c0a122_pass else 'FAIL'} "
    f"(max {c0a122_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")''')

# 10. savez + out dict additions
rep('''                    g_cutwA=GAIN["cutwA"],''',
    '''                    g_cutwA=GAIN["cutwA"], g_cutwB=GAIN["cutwB"],''')
rep('''                    cutwA_drop=cutk_drop["cutwA"], cutk5_drop=cutk_drop["cutk5"],''',
    '''                    cutwA_drop=cutk_drop["cutwA"], cutwB_drop=cutk_drop["cutwB"],
                    cutk5_drop=cutk_drop["cutk5"],''')
rep('''           g_cutng19=GAIN["cutng19"], g_cutng29=GAIN["cutng29"],
           g_cutwA=GAIN["cutwA"],''',
    '''           g_cutng19=GAIN["cutng19"], g_cutng29=GAIN["cutng29"],
           g_cutwA=GAIN["cutwA"], g_cutwB=GAIN["cutwB"],''')
rep('''           c0a121_max=c0a121_max, c0a121_pass=c0a121_pass,''',
    '''           c0a121_max=c0a121_max, c0a121_pass=c0a121_pass,
           c0a122_max=c0a122_max, c0a122_pass=c0a122_pass,''')
rep('''           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass
                          and c0a121_pass))''',
    '''           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass
                          and c0a121_pass and c0a122_pass))''')

# 11. output paths l122 -> l123 (INPUT paths kept — direction check below)
rep('if os.path.exists("l122/raw_partial.npz"):',
    'if os.path.exists("l123/raw_partial.npz"):', count=1)
rep('z = np.load("l122/raw_partial.npz")',
    'z = np.load("l123/raw_partial.npz")', count=1)
rep('np.savez("l122/raw_partial.npz", **store)',
    'np.savez("l123/raw_partial.npz", **store)', count=1)
rep('np.savez_compressed("l122/raw_l122.npz"',
    'np.savez_compressed("l123/raw_l123.npz"', count=1)
rep('log("raw_l122.npz checkpointed BEFORE analysis")',
    'log("raw_l123.npz checkpointed BEFORE analysis")', count=1)
rep('json.dump(out, open("l122/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l123/anchors_run.json", "w"), indent=1)', count=1)

open("l123_run.py", "w").write(SRC)

# ---------------- residual scan + direction check ----------------
bad = []
s = open("l123_run.py").read()
for tok in ("cutng39", "ng39", "k3_pos_in_new", "G_CUTNG39", "B17", "2101"):
    if tok in s:
        bad.append(("l123_run.py", "stale token " + tok))
import re
OK_IN = {"l107/static.json", "l92/static.json", "l101/static.json",
         "l121/static.json", "l123/static.json", "l113/raw_l113.npz",
         "l115/raw_l115.npz", "l117/raw_l117.npz", "l118/raw_l118.npz",
         "l119/raw_l119.npz", "l120/raw_l120.npz", "l121/raw_l121.npz",
         "l122/raw_l122.npz"}
for m in re.finditer(r'"(l1\d+/[^"]+)"', s):
    p = m.group(1)
    if p.startswith("l123/"):
        continue
    if p not in OK_IN:
        bad.append(("l123_run.py", "unexpected l-path " + p))
if n_err or bad:
    print("BUILD FAIL:", n_err, bad)
    sys.exit(1)
py_compile.compile("l123_run.py", doraise=True)
print("BUILD OK: l123_run.py compiled; scans clean (verdict built separately)")
