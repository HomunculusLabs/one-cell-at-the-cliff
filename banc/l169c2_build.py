"""l169c2_build.py — count-asserted ADDITIVE transform of l169b2_run.py
into l169c2_run.py for L169 stage (c2) (PREREG l169c2/PREREG.md).

Adds FOUR arms (rew1/rew2/rew3 = degree-preserving rewire of the carrier's
80 closure out-edges, draws 0/1/2 of the registered default_rng(16943)
stream; hom = cutwA minus gi 928, a SAME-FOOTPRINT DIFFERENT-CLASS
deletion) on a fresh batch B37 3481-3496. Every replacement is
count-asserted; a residual scan then refuses any surviving WRITE to a
prior run's artifact and py_compile gates the output.
"""
import py_compile
import re
import sys

SRC = "l169b2_run.py"
DST = "l169c2_run.py"
src = open(SRC).read()
reps = []


def rep(old, new, n=1, tag=""):
    reps.append((old, new, n, tag))


# ---------------- R1: header ----------------
rep('"""L169b2 run: pre-posting control (b2), the FLOOR-4 DYNAMIC arm.',
    '"""L169c2 run: pre-posting control (c2), the REWIRE + SAME-FOOTPRINT-\n'
    'DIFFERENT-CLASS DELETION arms. PREREG l169c2/PREREG.md FIRST (design\n'
    'pins stored by stage (c1) in l169c/static.json; rules C1 independent /\n'
    'C2 NONEQUIVALENT / C3 admissible). NEW ARMS: rew1/rew2/rew3 = the cutwA\n'
    'node set and edge COUNT verbatim with the carrier\'s 80 closure\n'
    'out-edges degree-preservingly REWIRED (draws 0/1/2 of the registered\n'
    'default_rng(16943) stream, weights travelling with the source edge);\n'
    'hom = the cutwA node set minus gi 928 (DNp33-R). CERT-1 = FC-169B2\n'
    'forward chain on the 12 inherited arms vs l169b2/raw_l169b2.npz;\n'
    'CERT-REW = the in-run rewire draws == l169c/static.json P5/P6\n'
    'field-for-field; CERT-HOM = 101 incident edges removed. FRESH B37\n'
    '3481-3496. Stage-(b2) prose retained below for lineage.\n'
    '\n'
    'L169b2 run: pre-posting control (b2), the FLOOR-4 DYNAMIC arm.',
    1, "R1 header")

# ---------------- R2/R3: ARMS + GAIN ----------------
rep('        "eMotBot5", "wAgN", "n25gW", "f4wA", "f4ng", "f4tw"]',
    '        "eMotBot5", "wAgN", "n25gW", "f4wA", "f4ng", "f4tw",\n'
    '        "rew1", "rew2", "rew3", "hom"]', 1, "R2 ARMS")
rep('            f4wA=None, f4ng=None, f4tw=None)  # silW/swap/f4 arms below',
    '            f4wA=None, f4ng=None, f4tw=None,\n'
    '            rew1=None, rew2=None, rew3=None,\n'
    '            hom=None)  # silW/swap/f4/c2 arms below', 1, "R3 GAIN")

# ---------------- R4: fresh batch ----------------
rep('B36 = list(range(3449, 3465))  # fresh (B35 = l169 stage a; key-scanned\n'
    '# absent from all 81 stored raw npzs before registration, L157 rule)\n'
    'SEEDS = ANCH + B36                  # anchors FIRST: early wiring verdict\n'
    'FRESH = B36',
    'B37 = list(range(3481, 3497))  # fresh (prior batch B36 = l169 stage b2;\n'
    '# key-scanned absent from all 72 stored raw npzs before registration,\n'
    '# L157 rule)\n'
    'SEEDS = ANCH + B37                  # anchors FIRST: early wiring verdict\n'
    'FRESH = B37', 1, "R4 B37")

# ---------------- R5: the (c2) graph-build block ----------------
C2_BLOCK = '''

# ---- L169 (c2): REWIRE + SAME-FOOTPRINT-DIFFERENT-CLASS DELETION arms.
# PREREG l169c2/PREREG.md FIRST; design pins stored by stage (c1) in
# l169c/static.json. rew1/rew2/rew3 = the cutwA node set and edge COUNT
# VERBATIM with the carrier's 80 closure out-edges degree-preservingly
# REWIRED; hom = the cutwA node set minus gi 928 (DNp33-R), a
# SAME-FOOTPRINT DIFFERENT-CLASS deletion, never a homolog control.
S169C = json.load(open("l169c/static.json"))
HOM_GI = 928
REW_ARMS = ("rew1", "rew2", "rew3")
C2_ARMS = REW_ARMS + ("hom",)
_selc = emask_wA & (src_all == GI_CARRIER)
assert int(_selc.sum()) == S169C["P1_carrier"]["out_edges"] == 80
_carmass = float(np.abs(vals_all[_selc]).sum())
assert _carmass == S169C["P1_carrier"]["out_mass"], (_carmass, "P1 (STOP)")
T70_g = np.zeros(Nall, bool)
T70_g[dst_all[_selc & (tier_of_dst[dst_all] == "intrinsic")]] = True
T10_g = np.zeros(Nall, bool)
T10_g[dst_all[_selc & (tier_of_dst[dst_all] == "motor_other")]] = True
motor_G = np.zeros(Nall, bool)
motor_G[mg_all] = True
assert int(T70_g.sum()) == 70 and int(T10_g.sum()) == 10, "T70/T10 (STOP)"
# --- CERT-REW: the (c1) rewire loop re-derived VERBATIM, draws captured ---
dn_present_wA = dn_all & keep_wA_e
blk_c2 = emask_wA & dn_present_wA[src_all] & cord_of_dst
pool_rows_c2 = np.where(blk_c2 & (src_all != GI_CARRIER))[0]
car_rows_c2 = np.where(_selc)[0]
assert len(car_rows_c2) == 80
base_pairs_c2 = set(zip(src_all[np.where(blk_c2)[0]].tolist(),
                        dst_all[np.where(blk_c2)[0]].tolist()))
chance_T70_c2 = float(
    np.abs(vals_all[pool_rows_c2][T70_g[dst_all[pool_rows_c2]]]).sum()
    / np.abs(vals_all[pool_rows_c2]).sum())
car_vals_c2 = np.abs(vals_all[car_rows_c2])
assert int(blk_c2.sum()) == S169C["P5_rewire_pool"]["block_edges"] == 64408
assert len(pool_rows_c2) == S169C["P5_rewire_pool"]["partner_rows"] == 64328
assert chance_T70_c2 == S169C["P5_rewire_pool"]["chance_mass_share_T70"]
rng_c2 = np.random.default_rng(16943)
draws_c2, caps_c2 = [], []
for _d in range(100):
    cdst = dst_all[car_rows_c2].copy()
    pdst = {}
    added, removed = set(), set()

    def present(p):
        return (p in base_pairs_c2 and p not in removed) or p in added

    def do_remove(p):
        if p in added:
            added.discard(p)
        else:
            removed.add(p)

    def do_add(p):
        if p in removed:
            removed.discard(p)
        else:
            added.add(p)

    nrel = 0
    for i in range(len(car_rows_c2)):
        for _ in range(20):
            j = int(pool_rows_c2[rng_c2.integers(len(pool_rows_c2))])
            sf = int(src_all[j])
            df = int(pdst.get(j, dst_all[j]))
            de = int(cdst[i])
            if sf == GI_CARRIER or df == de or df == GI_CARRIER or de == sf:
                continue
            if present((GI_CARRIER, df)) or present((sf, de)):
                continue
            do_remove((GI_CARRIER, de))
            do_remove((sf, df))
            do_add((GI_CARRIER, df))
            do_add((sf, de))
            cdst[i] = df
            pdst[j] = de
            nrel += 1
            break
    moved = cdst != dst_all[car_rows_c2]
    tj = sorted(pdst)
    before = sorted(dst_all[car_rows_c2].tolist()
                    + [int(dst_all[j]) for j in tj])
    after = sorted(cdst.tolist() + [int(pdst[j]) for j in tj])
    assert before == after, ("degree non-neutral", _d)
    draws_c2.append(dict(
        relocated=int(nrel), moved=int(moved.sum()),
        mass_T70=float(car_vals_c2[T70_g[cdst]].sum()),
        mass_motor=float(car_vals_c2[motor_G[cdst]].sum()),
        n_dst=int(len(set(cdst.tolist())))))
    caps_c2.append((cdst.copy(), dict(pdst)))
assert draws_c2[:5] == S169C["P6_rewire_draws"]["per_draw_first5"], \\
    "CERT-REW: re-derived rewire draws != l169c stored (STOP)"
log("CERT-REW GREEN: 100 draws re-derived, first5 == l169c/static.json")


def build_rew(keep, dst_mod, pin_edges):
    """build() with the destination column REPLACED (placement destroyed,
    every degree preserved). Coalescing loss = a multi-edge slipped
    through the swap bookkeeping = STOP."""
    em = keep[src_all] & keep[dst_mod]
    assert np.array_equal(em, emask_wA), "rew emask drift (STOP)"
    gsrc, gdst, gcount = src_all[em], dst_mod[em], w_syn[em]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    lsrc, ldst = loc[gsrc], loc[gdst]
    _sa2 = sign_all[gsrc]
    _sb2 = np.where(is_glut[gsrc], -np.abs(_sa2), _sa2)
    vals = (np.log1p(gcount) * _sb2).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([ldst, lsrc])).long(),
        torch.from_numpy(vals), (int(keep.sum()), int(keep.sum()))
    ).coalesce().to_sparse_csr()
    assert int(W.values().numel()) == pin_edges, "rew coalesced (STOP)"
    return W, loc


C2_KEEP, C2_LOC, C2_OLDPOS, C2_KEPTNEW, C2_KEPTMASK, C2_POSINNEW = (
    {}, {}, {}, {}, {}, {})
_wA_edges_c2 = cutk_pins["cutwA"]["edges"]
_indeg_base = np.bincount(dst_all, minlength=Nall)
for _ci, _ca in enumerate(REW_ARMS):
    _cdst, _pdst = caps_c2[_ci]
    _dm = dst_all.copy()
    _dm[car_rows_c2] = _cdst
    for _j, _de in _pdst.items():
        _dm[_j] = _de
    assert not np.array_equal(_dm, dst_all), (_ca, "rewire is a no-op (STOP)")
    assert np.array_equal(np.bincount(_dm, minlength=Nall), _indeg_base), \\
        (_ca, "global in-degree not preserved (STOP)")
    _W2, _lc2 = build_rew(keep_wA_e, _dm, _wA_edges_c2)
    assert np.array_equal(_lc2, loc_wA), (_ca, "rew loc drift (STOP)")
    C2_KEEP[_ca], C2_LOC[_ca] = keep_wA_e, _lc2
    POOLS[_ca] = pools_for(_lc2, keep_wA_e)
    mech[_ca] = np.where(mech_mask[keep_wA_e])[0]
    _mt2 = np.zeros(int(keep_wA_e.sum()), bool)
    _mt2[_lc2[mg_all[keep_wA_e[mg_all]]]] = True
    motor[_ca] = _mt2
    dng100[_ca] = np.sort(_lc2[dng100_all[keep_wA_e[dng100_all]]])
    WB[_ca] = wb(_W2)
    N_OF[_ca] = int(keep_wA_e.sum())
    C2_OLDPOS[_ca] = _lc2[gi_old]
    C2_KEPTMASK[_ca] = keep_wA_e[new_g]
    C2_KEPTNEW[_ca] = _lc2[new_g[C2_KEPTMASK[_ca]]]
    C2_POSINNEW[_ca] = loc_n[np.where(keep_wA_e)[0]]
    log(f"{_ca}: n {N_OF[_ca]:,} | edges {int(WB[_ca].values().numel()):,} "
        f"| relocated {draws_c2[_ci]['relocated']} | own-sheet mass "
        f"{draws_c2[_ci]['mass_T70']:.4f} of {_carmass:.2f}")
# --- hom: node deletion on the cutwA base (CERT-HOM) ---
assert keep_wA_e[HOM_GI], "928 absent from cutwA (STOP)"
assert not np.isin(HOM_GI, cutk_drop["cutwA"]), "928 inside cut window (STOP)"
assert not np.isin(HOM_GI, dn_new_g), "928 is a pure projector (STOP)"
assert not np.isin(dng100_all, HOM_GI).any(), "928 is a DNg100 cell (STOP)"
_hk = keep_wA_e.copy()
_hk[HOM_GI] = False
_hom_inc = int((emask_wA & ((src_all == HOM_GI) | (dst_all == HOM_GI))).sum())
assert _hom_inc == 101, (_hom_inc, "928 incident != 88 out + 13 in (STOP)")
_Wh, _lch = build(_hk)
assert int(_Wh.values().numel()) == _wA_edges_c2 - _hom_inc, \\
    "hom edge count (STOP)"
C2_KEEP["hom"], C2_LOC["hom"] = _hk, _lch
POOLS["hom"] = pools_for(_lch, _hk)
mech["hom"] = np.where(mech_mask[_hk])[0]
_mth = np.zeros(int(_hk.sum()), bool)
_mth[_lch[mg_all[_hk[mg_all]]]] = True
motor["hom"] = _mth
dng100["hom"] = np.sort(_lch[dng100_all[_hk[dng100_all]]])
WB["hom"] = wb(_Wh)
N_OF["hom"] = int(_hk.sum())
C2_OLDPOS["hom"] = _lch[gi_old]
C2_KEPTMASK["hom"] = _hk[new_g]
C2_KEPTNEW["hom"] = _lch[new_g[C2_KEPTMASK["hom"]]]
C2_POSINNEW["hom"] = loc_n[np.where(_hk)[0]]
log(f"hom: n {N_OF['hom']:,} (cutwA {n_cutk['cutwA']:,}) | edges "
    f"{int(WB['hom'].values().numel()):,} | incident removed {_hom_inc}")
for _ca in C2_ARMS:
    assert len(mech[_ca]) == S92["mech"], (_ca, "mech size")
    assert len(dng100[_ca]) == S92["dng100"], (_ca, "dng100 size")
    for _pk2, _want2 in S92["pool_sizes"].items():
        assert len(POOLS[_ca][_pk2]) == _want2, (_ca, _pk2)
# static leg of C0-NT(c2): the three rewire CSRs are mutually distinct at
# identical (n, edges), and none is the cutwA CSR.
assert len({WB[_a2].values().numpy().tobytes() for _a2 in REW_ARMS}) == 3, \\
    "rew graphs collide (STOP)"
for _a2 in REW_ARMS:
    assert int(WB[_a2].values().numel()) == int(
        WB["cutwA"].values().numel()), (_a2, "rew edge count (STOP)")
    assert not np.array_equal(WB[_a2].col_indices().numpy(),
                              WB["cutwA"].col_indices().numpy()), \\
        (_a2, "rew CSR == cutwA (STOP)")
assert N_OF["hom"] == n_cutk["cutwA"] - 1, "hom node count (STOP)"'''
rep('assert int(WB["f4wA"].values().numel()) != int(\n'
    '    WB["cutwA"].values().numel()), "floor never applied (STOP)"',
    'assert int(WB["f4wA"].values().numel()) != int(\n'
    '    WB["cutwA"].values().numel()), "floor never applied (STOP)"'
    + C2_BLOCK, 1, "R5 c2 build block")

# ---------------- R6/R7/R8: per-arm state + noise plumbing ----------------
rep('''    for _fa in F4_ARMS:
        _xf = torch.zeros(N_OF[_fa], 1)
        _xf[F4_OLDPOS[_fa]] = X0o
        _xf[F4_KEPTNEW[_fa]] = X0n[F4_KEPTMASK[_fa]]
        st[_fa] = _xf''',
    '''    for _fa in F4_ARMS:
        _xf = torch.zeros(N_OF[_fa], 1)
        _xf[F4_OLDPOS[_fa]] = X0o
        _xf[F4_KEPTNEW[_fa]] = X0n[F4_KEPTMASK[_fa]]
        st[_fa] = _xf
    for _ca in C2_ARMS:
        _xc = torch.zeros(N_OF[_ca], 1)
        _xc[C2_OLDPOS[_ca]] = X0o
        _xc[C2_KEPTNEW[_ca]] = X0n[C2_KEPTMASK[_ca]]
        st[_ca] = _xc''', 1, "R6 settle st")
rep('''    for _fa in F4_ARMS:
        _xf = torch.zeros(N_OF[_fa], 1)
        _xf[F4_OLDPOS[_fa]] = X0o
        _xf[F4_KEPTNEW[_fa]] = X0n[F4_KEPTMASK[_fa]]
        X[_fa] = _xf''',
    '''    for _fa in F4_ARMS:
        _xf = torch.zeros(N_OF[_fa], 1)
        _xf[F4_OLDPOS[_fa]] = X0o
        _xf[F4_KEPTNEW[_fa]] = X0n[F4_KEPTMASK[_fa]]
        X[_fa] = _xf
    for _ca in C2_ARMS:
        _xc = torch.zeros(N_OF[_ca], 1)
        _xc[C2_OLDPOS[_ca]] = X0o
        _xc[C2_KEPTNEW[_ca]] = X0n[C2_KEPTMASK[_ca]]
        X[_ca] = _xc''', 1, "R7 rollout X")
# the settle-phase noise loop occurs TWICE (settle_states + rollout settle)
rep('''        for _fa in F4_ARMS:
            noise[_fa] = nzn[F4_POSINNEW[_fa]]
        sp += 2 * math.pi * 0.7 * DT''',
    '''        for _fa in F4_ARMS:
            noise[_fa] = nzn[F4_POSINNEW[_fa]]
        for _ca in C2_ARMS:
            noise[_ca] = nzn[C2_POSINNEW[_ca]]
        sp += 2 * math.pi * 0.7 * DT''', 2, "R8 settle noise x2")
rep('''        for _fa in F4_ARMS:
            noise[_fa] = nzn[F4_POSINNEW[_fa]]
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0''',
    '''        for _fa in F4_ARMS:
            noise[_fa] = nzn[F4_POSINNEW[_fa]]
        for _ca in C2_ARMS:
            noise[_ca] = nzn[C2_POSINNEW[_ca]]
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0''',
    1, "R9 WIN noise")
rep('                                  **{_fa: g for _fa in F4_ARMS}),',
    '                                  **{_fa: g for _fa in F4_ARMS},\n'
    '                                  **{_ca: g for _ca in C2_ARMS}),',
    1, "R10 bisect gains")

# ---------------- R11: fresh (c2) bisects ----------------
rep('assert len({GAIN[_fa] for _fa in F4_ARMS}) == 3, "f4 gains collide (STOP)"',
    'assert len({GAIN[_fa] for _fa in F4_ARMS}) == 3, "f4 gains collide (STOP)"\n'
    '# ---- L169 (c2): FRESH af-matched bisects on the four (c2) graphs.\n'
    '# REW keeps the edge COUNT but redistributes per-target in-degree; HOM\n'
    '# removes 101 edges — stored g_cutwA may NOT be ported (PREREG P7).\n'
    'c2_band_ok, c2_stairs, c2_af = {}, {}, {}\n'
    'for _ca in C2_ARMS:\n'
    '    lo_d, hi_d = 0.12, 0.18\n'
    '    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _ca), bisect_af_mean(hi_d, _ca)\n'
    '    log(f"{_ca} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "\n'
    '        f"target {AF_T:.5f}")\n'
    '    assert af_lo_d < AF_T < af_hi_d, f"{_ca} bracket fail"\n'
    '    for it in range(24):\n'
    '        mid = (lo_d + hi_d) / 2\n'
    '        if bisect_af_mean(mid, _ca) < AF_T:\n'
    '            lo_d = mid\n'
    '        else:\n'
    '            hi_d = mid\n'
    '    GAIN[_ca] = lo_d\n'
    '    _afd2 = bisect_af_mean(lo_d, _ca)\n'
    '    c2_af[_ca] = _afd2\n'
    '    c2_stairs[_ca] = abs(_afd2 - AF_T)\n'
    '    c2_band_ok[_ca] = bool(c2_stairs[_ca] <= 5e-3)\n'
    '    log(f"g_{_ca} {lo_d:.9f} | af_final {_afd2:.6f} | "\n'
    '        f"|af-target| {c2_stairs[_ca]:.2e} (staircase)")',
    1, "R11 c2 bisects")

# ---------------- R12: output paths (direction-checked) ----------------
rep('if os.path.exists("l169b2/raw_partial.npz"):\n'
    '    z = np.load("l169b2/raw_partial.npz")   # own partial (L120 direction)',
    'if os.path.exists("l169c2/raw_partial.npz"):\n'
    '    z = np.load("l169c2/raw_partial.npz")   # own partial (L120 direction)',
    1, "R12a resume path")
rep('    np.savez("l169b2/raw_partial.npz", **store)',
    '    np.savez("l169c2/raw_partial.npz", **store)', 1, "R12b partial write")
rep('np.savez_compressed("l169b2/raw_l169b2.npz", K=K,',
    'np.savez_compressed("l169c2/raw_l169c2.npz", K=K,', 1, "R12c raw write")
rep('log("raw_l169b2.npz checkpointed BEFORE analysis")',
    'log("raw_l169c2.npz checkpointed BEFORE analysis")', 1, "R12d log")
rep('json.dump(out, open("l169b2/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l169c2/anchors_run.json", "w"), indent=1)',
    1, "R12e anchors json")

# ---------------- R13: savez pins ----------------
rep('                    batches=np.array(SEEDS), **store)',
    '                    g_rew1=GAIN["rew1"], g_rew2=GAIN["rew2"],\n'
    '                    g_rew3=GAIN["rew3"], g_hom=GAIN["hom"],\n'
    '                    hom_gi=np.array([HOM_GI]),\n'
    '                    hom_incident=np.array([_hom_inc]),\n'
    '                    car_rows=car_rows_c2,\n'
    '                    rew_cdst=np.vstack([caps_c2[_i2][0]\n'
    '                                        for _i2 in range(3)]),\n'
    '                    batches=np.array(SEEDS), **store)', 1, "R13 savez pins")

# ---------------- R14: absence scan (B37 + two new input npzs) ----------
rep('          "l169/raw_l169.npz",\n          "l169/raw_partial.npz"]',
    '          "l169/raw_l169.npz",\n'
    '          "l169/raw_partial.npz",\n'
    '          "l169b2/raw_l169b2.npz",\n'
    '          "l169b2/raw_partial.npz"]', 1, "R14a prevs")
rep('    assert not any(f"mm_full_{s}" in _zp.files for s in B36), \\\n'
    '        ("B36 collides with " + _p + " (STOP)")\n'
    'log(f"B36 absence across {len(_prevs)} stored npzs: PASS")',
    '    assert not any(f"mm_full_{s}" in _zp.files for s in B37), \\\n'
    '        ("B37 collides with " + _p + " (STOP)")\n'
    'log(f"B37 absence across {len(_prevs)} stored npzs: PASS")',
    1, "R14b B37 absence")

# ---------------- R15: FC-169B2 + C0-NT(c2) + P-af(c2) ----------------
rep('out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],',
    '''# ---- FC-169B2 (CERT-1): the 12 inherited arms must be BIT-IDENTICAL to
# l169b2/raw_l169b2.npz at 801/901 — adding arms consumes no generator
# draws, so any non-zero here is a stream break and the run is VOID.
z169b2 = np.load("l169b2/raw_l169b2.npz")
_arms169b2 = ("full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
              "eMotBot5", "wAgN", "n25gW", "f4wA", "f4ng", "f4tw")
assert all(f"{_k}_{_a}_801" in z169b2.files for _k in C0A150_KEYS
           for _a in _arms169b2), "FC-169B2 coverage miss"
fc169b2 = {}
for s in (801, 901):
    for key in C0A150_KEYS:
        for a in _arms169b2:
            fc169b2[f"{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z169b2[f"{key}_{a}_{s}"][:WIN]).max())
    for a in _arms169b2:
        fc169b2[f"af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(z169b2[f"af_{a}_{s}"]))
fc169b2_max = max(fc169b2.values())
fc169b2_pass = bool(all(v == 0.0 for v in fc169b2.values()))
log(f"FC-169B2 (12 arms x {len(C0A150_KEYS)} keys x 2 seeds) vs raw_l169b2: "
    f"{'PASS' if fc169b2_pass else 'FAIL'} (max {fc169b2_max:.1e})")
# ---- C0-NT(c2): every (c2) arm separated from the cutwA base, and the
# three rewire draws separated from each other (L35/L39 dead-channel).
ntc2 = {}
for _ca in C2_ARMS:
    for s in (801, 901):
        ntc2[f"{_ca}_vs_cutwA_{s}"] = float(np.abs(
            store[f"mm_{_ca}_{s}"] - store[f"mm_cutwA_{s}"]).max())
for _p2, _q2 in (("rew1", "rew2"), ("rew1", "rew3"), ("rew2", "rew3")):
    for s in (801, 901):
        ntc2[f"{_p2}_vs_{_q2}_{s}"] = float(np.abs(
            store[f"mm_{_p2}_{s}"] - store[f"mm_{_q2}_{s}"]).max())
ntc2_pass = bool(all(v > 0.0 for v in ntc2.values()))
log(f"C0-NT(c2) separation: {'PASS' if ntc2_pass else 'VOID'} "
    f"(min {min(ntc2.values()):.3e})")
# ---- P-af(c2): gate on the SETTLED staircase residual; the rollout af is
# a different quantity (6000 extra steps) and is DISCLOSED only.
pafc2 = {}
for _ca in C2_ARMS:
    _v2 = [float(store[f"af_{_ca}_{s}"]) for s in FRESH]
    pafc2[_ca] = dict(g=GAIN[_ca], bisect_af=c2_af[_ca], stair=c2_stairs[_ca],
                      rollout_af_mean=float(np.mean(_v2)),
                      rollout_af_maxoff=float(np.max(np.abs(
                          np.array(_v2) - AF_T))))
    log(f"P-af {_ca}: g {GAIN[_ca]:.9f} | settled stair "
        f"{c2_stairs[_ca]:.2e} | rollout af mean "
        f"{pafc2[_ca]['rollout_af_mean']:.5f} (max off "
        f"{pafc2[_ca]['rollout_af_maxoff']:.2e})")
pafc2_ok = bool(all(v["stair"] <= 5e-3 for v in pafc2.values()))
c2_gains_distinct = bool(len({GAIN[_ca] for _ca in C2_ARMS}) == len(C2_ARMS))
log(f"P-af(c2) staircase gate: {'PASS' if pafc2_ok else 'DISCLOSE'} | "
    f"gains distinct {c2_gains_distinct}")
out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],''',
    1, "R15 c2 anchors")

# ---------------- R16: out dict ----------------
rep('           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass\n'
    '                         and nt_pass and fc169_pass and ntf4_pass))',
    '           fc169b2_max=fc169b2_max, fc169b2_pass=fc169b2_pass,\n'
    '           ntc2=ntc2, ntc2_pass=ntc2_pass, pafc2=pafc2,\n'
    '           pafc2_ok=pafc2_ok, c2_gains_distinct=c2_gains_distinct,\n'
    '           g_rew1=GAIN["rew1"], g_rew2=GAIN["rew2"],\n'
    '           g_rew3=GAIN["rew3"], g_hom=GAIN["hom"],\n'
    '           hom_gi=HOM_GI, hom_incident=_hom_inc,\n'
    '           c2_stairs=c2_stairs, c2_band_ok=c2_band_ok,\n'
    '           c2_edges={_a2: int(WB[_a2].values().numel())\n'
    '                     for _a2 in C2_ARMS},\n'
    '           c2_n={_a2: N_OF[_a2] for _a2 in C2_ARMS},\n'
    '           rew_draws_first5=draws_c2[:5], rew_chance_T70=chance_T70_c2,\n'
    '           carrier_out_mass=_carmass,\n'
    '           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass\n'
    '                         and nt_pass and fc169_pass and ntf4_pass\n'
    '                         and fc169b2_pass and ntc2_pass))',
    1, "R16 out dict")

# ---------------- apply ----------------
out = src
for old, new, n, tag in reps:
    c = out.count(old)
    assert c == n, f"REP COUNT MISS [{tag}]: found {c}, expected {n}"
    out = out.replace(old, new)
    print(f"  rep ok ({c}x): {tag}")

# ---------------- residual scan (L120/l126 form) ----------------
# Whitelist by LINE CONTEXT (l126 rule): docstring bodies and comments may
# name the prior run for lineage; CODE lines may name it only as an INPUT
# path literal. A log/label string that merely mentions it is not a path.
bad = []
in_doc = False
for i, line in enumerate(out.split("\n"), 1):
    nq = line.count('"""')
    code = line.split("#")[0] if not line.strip().startswith("#") else ""
    if in_doc:
        if nq:
            in_doc = (nq % 2 == 0)
        continue
    if nq % 2 == 1:
        in_doc = True
        continue
    if line.strip().startswith("#") or not code.strip():
        continue
    for lit in re.findall(r'"([^"]*)"', code):
        looks_path = "/" in lit or lit.endswith((".npz", ".json", ".md"))
        if looks_path and "l169b2" in lit:
            if not re.fullmatch(r"l169b2/raw_(l169b2|partial)\.npz", lit):
                bad.append((i, "l169b2 non-input path", line))
        if looks_path and not lit.startswith(("l169c2/",)) and \
                re.fullmatch(r"l169c2/.*", lit) is None and "l169c2" in lit:
            bad.append((i, "malformed l169c2 path", line))
    if re.search(r"\bB36\b", code):
        bad.append((i, "B36 survivor", line))
for m in re.finditer(r'np\.savez(?:_compressed)?\("([^"]+)"', out):
    if not m.group(1).startswith("l169c2/"):
        bad.append((0, "write outside l169c2/", m.group(1)))
for m in re.finditer(r'open\("([^"]+)", "w"\)', out):
    if not m.group(1).startswith("l169c2/"):
        bad.append((0, "json write outside l169c2/", m.group(1)))
if bad:
    for b in bad:
        print("RESIDUAL:", b)
    sys.exit("RESIDUAL SCAN FAILED")
print("residual scan: CLEAN")

open(DST, "w").write(out)
py_compile.compile(DST, doraise=True)
print(f"wrote {DST} ({len(out.splitlines())} lines) | py_compile OK")
