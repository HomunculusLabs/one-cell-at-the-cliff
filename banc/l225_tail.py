# ================= L225 TAIL (appended by l225_build.py) =================
# Everything above this line is VERBATIM source:
#   l151_static.py 1-319, l178_tail.py 7-149, l206_mid.py,
#   l206_tail.py 22-121, l207_tail.py 48-112, l207_tail.py 199-241,
#   l213_tail.py 1-430  (L213's WHOLE pipeline with its runtime stamp and
#                        its writer CUT -- the L213 slicing pattern),
#   l225_mid.py         (3-line bridge: os, the output dict, the clock),
#   l224_tail.py 48-124 (the CERT-213 HALTING block with its coverage bar
#                        DERIVED FROM THE ARTIFACT -- re-used as SOURCE,
#                        never re-implemented; the L211 rule).
# So CERT-F4, the three stored gains, the CSR orientation, all 20 pool sizes,
# CERT-178 (420), CERT-207 (522) and CERT-T (272) re-run as free
# certification, the L213 population/strata/Q1/Q2/Q3 blocks re-execute, and
# CERT-213 halts on any drift, BEFORE any L225 value is read.
# PREREG: l225/PREREG.md (registered FIRST, incl. premise corrections 0a-0h).
# Writes l225/static.json ONLY. Zero rollouts, zero settles, zero dynamics.

PRIMARY = "G0_closure"
ALPHA = 0.05
N_CERT = 2000            # l213's draw count -- the reproduced PREFIX
N_EXT = 20000            # the per-type sweep (premise 0a resolution floor)
SEED_ENR = 22501         # size-matched type-set draws for Q225-2
B_ENR = 2000
SURV_SMALL = 10          # F_SMALL_FAMILY upper bound
ENR_SHARE_BAR = 0.50     # Q225-2 "names a cheaper explanation" share bar
ANN_COLS = ("side", "region", "nerve", "hemilineage",
            "neurotransmitter_predicted", "cell_class", "flow")

q["design"] = (
    "L225 the TYPE-LEVEL null applied NONSELECTIVELY. L213 scored ONE "
    "preselected type (DNp33) against a within-mass-stratum type-label "
    "permutation null and read pct .0105-.0145. Here EVERY >=2-member "
    "descending cell type on the three L207/L213 substrates is scored "
    "against the SAME null (same seed, same perm_within, the first 2000 "
    "draws asserted bit-identical to L213's) and the family is corrected "
    "with Benjamini-Hochberg at alpha .05 -- Kriegeskorte et al. 2009 "
    "policy step (1), the nonselective analysis. PREREG l225/PREREG.md.")
q["prereg"] = "l225/PREREG.md"
q["parents"] = ["l213/static.json", "l207/static.json"]
q["bars"] = dict(alpha=ALPHA, n_cert=N_CERT, n_ext=N_EXT,
                 surv_small=SURV_SMALL, enr_share_bar=ENR_SHARE_BAR,
                 b_enrichment=B_ENR, seed_type_null=SEED,
                 seed_enrichment=SEED_ENR, primary=PRIMARY)
q["prior_art"] = [
    "Kriegeskorte, Simmons, Bellgowan & Baker, Nat Neurosci 12:535-540 "
    "(2009) -- circular analysis; this card is their policy step (1).",
    "Benjamini & Hochberg, J R Stat Soc B 57:289-300 (1995) -- the FDR "
    "ladder, used verbatim.",
    "Phipson & Smyth, Stat Appl Genet Mol Biol 9:39 (2010) -- the add-one "
    "permutation p-value, which is why no p here is ever exactly zero.",
]

# =====================================================================
# PREMISE 0a (HALTING, read FIRST): the RESOLUTION FLOOR of a permutation
# FDR.  p_min = 1/(B+1); BH rejects rank 1 only if p_1 <= alpha/m.  At
# L213's B=2000 and m~426 that is 4.998e-04 vs 1.174e-04, so F_UNIQUE is
# UNREACHABLE BY CONSTRUCTION and porting the null unchanged would have
# manufactured a guaranteed answer.  Recomputed here from the MEASURED m
# per substrate; the branch set is asserted reachable before any survivor
# count is read, and the escape SHORT-CIRCUITS (L222).
# =====================================================================
RESFLOOR = {}
for _k in POP:
    _m = Q1[_k]["n_types_ge2"]
    _pmin_old = 1.0 / (N_CERT + 1)
    _pmin_new = 1.0 / (N_EXT + 1)
    _thr1 = ALPHA / _m
    RESFLOOR[_k] = dict(
        m_types=_m,
        p_min_at_l213_draws=_pmin_old,
        p_min_at_l225_draws=_pmin_new,
        bh_rank1_threshold=_thr1,
        rank1_rejectable_at_l213_draws=bool(_pmin_old <= _thr1),
        rank1_rejectable_at_l225_draws=bool(_pmin_new <= _thr1),
        min_floor_tied_types_for_any_rejection_at_l213=int(
            math.ceil(_m * _pmin_old / ALPHA)),
        min_floor_tied_types_for_any_rejection_at_l225=int(
            math.ceil(_m * _pmin_new / ALPHA)))
    log(f"[0a floor] {_k}: m {_m} | p_min {_pmin_old:.3e} (B={N_CERT}) vs "
        f"BH rank-1 thr {_thr1:.3e} -> F_UNIQUE reachable "
        f"{RESFLOOR[_k]['rank1_rejectable_at_l213_draws']} "
        f"(needs {RESFLOOR[_k]['min_floor_tied_types_for_any_rejection_at_l213']}"
        f" floor-tied types) | at B={N_EXT} p_min {_pmin_new:.3e} -> "
        f"reachable {RESFLOOR[_k]['rank1_rejectable_at_l225_draws']}")
q["premise_0a_resolution_floor"] = RESFLOOR
_REACH = all(RESFLOOR[_k]["rank1_rejectable_at_l225_draws"] for _k in RESFLOOR)
_ESCAPE = None
if not _REACH:
    _ESCAPE = ("F_DEGENERATE: the registered branch set is UNREACHABLE at "
               f"B={N_EXT} on at least one substrate (premise 0a).")
assert _REACH, (_ESCAPE, "escape SHORT-CIRCUITS (STOP)")
log(f"[0a floor] branch set REACHABLE on all three substrates at B={N_EXT} "
    f"(it would NOT have been at L213's B={N_CERT})")

# =====================================================================
# CERT-GRP (HALTING): rebuild the >=2-member type grouping and assert it
# against L213's STORED aggregates before any sweep runs.  The grouping is
# bookkeeping, not certified machinery, so it is rebuilt -- and GATED.
# =====================================================================
GRP = {}
_ngrp = 0
for _k, _p in POP.items():
    _bt = {}
    for _i, _c in enumerate(_p["ct"]):
        if _c:
            _bt.setdefault(_c, []).append(_i)
    _big = {c: np.array(ix) for c, ix in _bt.items() if len(ix) >= 2}
    assert TYPE_NAME in _big, (_k, "DNp33 < 2 present members (STOP)")
    _names = sorted(_big)
    _realm = np.array([float(np.median(_p["R"][_big[c]])) for c in _names])
    _i33 = _names.index(TYPE_NAME)
    assert len(_big) == Q1[_k]["n_types_ge2"], (_k, "CERT-GRP m (STOP)")
    assert sum(len(v) for v in _big.values()) == \
        Q1[_k]["n_cells_in_types"], (_k, "CERT-GRP cells (STOP)")
    assert [_p["gis"][i] for i in _big[TYPE_NAME]] == \
        Q1[_k]["dnp33_members"], (_k, "CERT-GRP members (STOP)")
    assert _realm[_i33] == Q1[_k]["type_median"], \
        (_k, _realm[_i33], Q1[_k]["type_median"], "CERT-GRP median (STOP)")
    _ngrp += 4
    # size-grouped padded index blocks (the fast kernel's substrate)
    _bysize = {}
    for _ti, _c in enumerate(_names):
        _bysize.setdefault(len(_big[_c]), []).append(_ti)
    BLK = []
    for _s in sorted(_bysize):
        _tpos = np.array(_bysize[_s])
        _idx = np.stack([_big[_names[t]] for t in _tpos])
        assert _idx.shape == (len(_tpos), _s)
        BLK.append((_s, _tpos, _idx))
    assert sum(len(t) for _, t, _i in BLK) == len(_names)
    GRP[_k] = dict(names=_names, big=_big, real=_realm, i33=_i33, blk=BLK,
                   sizes={int(s): int(len(t)) for s, t, _i in BLK})
    log(f"[CERT-GRP] {_k}: {len(_names)} types >=2 members | DNp33 index "
        f"{_i33} | size blocks {GRP[_k]['sizes']}")
log(f"[CERT-GRP] GREEN {_ngrp} checks against L213's stored Q1 aggregates")
q["cert_grp"] = dict(n_checks=_ngrp, mode="int/list/float equality (==)",
                     per_substrate={k: dict(m=len(v["names"]),
                                            sizes=v["sizes"])
                                    for k, v in GRP.items()})


# =====================================================================
# the fast per-type median kernel, GATED (CERT-FAST, EXACT array equality
# -- licensed by premise 0e's measured bit-identity probe)
# =====================================================================
def type_medians(Rv, blk):
    """median R of every >=2-member type, in the `names` order."""
    out = np.empty(sum(len(t) for _, t, _i in blk))
    for _s, _tpos, _idx in blk:
        out[_tpos] = np.median(Rv[_idx], axis=1)
    return out


_nfast = 0
for _k, _g in GRP.items():
    _Rv = POP[_k]["R"]
    _fast = type_medians(_Rv, _g["blk"])
    _slow = np.array([float(np.median(_Rv[_g["big"][c]]))
                      for c in _g["names"]])
    assert np.array_equal(_fast, _slow), (_k, "CERT-FAST real (STOP)")
    assert np.array_equal(_fast, _g["real"]), (_k, "CERT-FAST vs grp (STOP)")
    _nfast += 2
    # and on a permuted vector, so the gate covers the sweep's own input
    _rngp = np.random.default_rng(7777)
    _pi = perm_within(POP[_k]["st"], _rngp)
    _Rp = _Rv[_pi]
    _f2 = type_medians(_Rp, _g["blk"])
    _s2 = np.array([float(np.median(_Rp[_g["big"][c]]))
                    for c in _g["names"]])
    assert np.array_equal(_f2, _s2), (_k, "CERT-FAST permuted (STOP)")
    _nfast += 1
log(f"[CERT-FAST] GREEN {_nfast} EXACT array equalities: the padded "
    f"axis-median kernel == a per-type np.median loop on real AND permuted "
    f"R (premise 0e)")
q["cert_fast"] = dict(n_checks=_nfast, mode="np.array_equal (EXACT)",
                      note="premise 0e probed axis-median bit-identity at "
                           "sizes 2-11 (max abs diff 0.0) before the card "
                           "was written")

# =====================================================================
# THE SWEEP: one rng stream per substrate, seeded exactly as L213 seeded
# its Q1 null, 20000 draws.  The first 2000 ARE L213's own draws
# (premise 0b, verified prefix property) -> CERT-SEED.
# =====================================================================
SWEEP = {}
_nseed = 0
for _k, _g in GRP.items():
    _p = POP[_k]
    _R, _st = _p["R"], _p["st"]
    _m = len(_g["names"])
    _realm = _g["real"]
    _cnt_le = np.zeros(_m, np.int64)
    _cnt_lt = np.zeros(_m, np.int64)
    _cnt_ge = np.zeros(_m, np.int64)
    _col33 = np.empty(N_CERT)
    _rng = np.random.default_rng(SEED)          # L213's Q1 seed, verbatim
    _cnt0 = np.bincount(_st, minlength=N_STRATA)
    _t0s = time.time()
    for _d in range(N_EXT):
        _pi = perm_within(_st, _rng)
        assert np.array_equal(np.bincount(_st[_pi], minlength=N_STRATA),
                              _cnt0), (_k, _d, "stratum counts (STOP)")
        _med = type_medians(_R[_pi], _g["blk"])
        _cnt_le += (_med <= _realm)
        _cnt_lt += (_med < _realm)
        _cnt_ge += (_med >= _realm)
        if _d < N_CERT:
            _col33[_d] = _med[_g["i33"]]
    _el = time.time() - _t0s
    # ---- CERT-SEED (HALTING): L213's stored DNp33 null, FLOAT EQUALITY ----
    _s33 = Q1[_k]
    _pct33 = float((_col33 < _realm[_g["i33"]]).sum() / N_CERT)
    assert _pct33 == _s33["null_pct"], \
        (_k, _pct33, _s33["null_pct"], "CERT-SEED null_pct (STOP)")
    assert float(np.median(_col33)) == _s33["null_median"], \
        (_k, "CERT-SEED null_median (STOP)")
    assert float(np.quantile(_col33, 0.05)) == _s33["null_p05"], \
        (_k, "CERT-SEED null_p05 (STOP)")
    assert float(np.quantile(_col33, 0.95)) == _s33["null_p95"], \
        (_k, "CERT-SEED null_p95 (STOP)")
    assert _realm[_g["i33"]] == _s33["type_median"], \
        (_k, "CERT-SEED type_median (STOP)")
    _nseed += 5
    log(f"[CERT-SEED] {_k}: the DNp33 column over the first {N_CERT} draws "
        f"reproduces l213's null_pct {_pct33:.4f}, null_median "
        f"{np.median(_col33):.6g} and p05/p95 at FLOAT EQUALITY "
        f"({_el:.1f}s for {N_EXT} draws)")
    SWEEP[_k] = dict(p_low=(1.0 + _cnt_le) / (N_EXT + 1.0),
                     p_high=(1.0 + _cnt_ge) / (N_EXT + 1.0),
                     real=_realm, pct_strict=_cnt_lt / float(N_EXT),
                     elapsed_s=_el, n_at_floor_low=int((_cnt_le == 0).sum()))
log(f"[CERT-SEED] GREEN {_nseed} checks at FLOAT EQUALITY (5 per substrate) "
    f"-- the extension is CONTINUITY, not replacement (premise 0b)")
q["cert_seed"] = dict(n_checks=_nseed, mode="float equality (==)",
                      note="the first 2000 draws of the 20000-draw stream "
                           "ARE l213's Q1 draws (prefix property probed "
                           "before the card was written)")


# =====================================================================
# Q225-1 (PRIMARY): Benjamini-Hochberg over the m type medians
# =====================================================================
def bh_reject(p, alpha=ALPHA):
    """BH 1995: largest i (1-indexed, sorted ascending) with p_i <= a*i/m;
    reject every test with p <= p_i.  Returns (mask, qvals, k_reject)."""
    p = np.asarray(p, float)
    m = len(p)
    order = np.argsort(p, kind="stable")
    ps = p[order]
    thr = alpha * np.arange(1, m + 1) / m
    ok = np.where(ps <= thr)[0]
    qs = np.minimum.accumulate((ps * m / np.arange(1, m + 1))[::-1])[::-1]
    qs = np.minimum(qs, 1.0)
    qv = np.empty(m)
    qv[order] = qs
    if len(ok) == 0:
        return np.zeros(m, bool), qv, 0
    kk = int(ok.max())
    return (p <= ps[kk]), qv, int((p <= ps[kk]).sum())


Q225_1 = {}
for _k, _g in GRP.items():
    _sw = SWEEP[_k]
    _m = len(_g["names"])
    _mask, _qv, _krej = bh_reject(_sw["p_low"])
    _maskh, _qvh, _krejh = bh_reject(_sw["p_high"])
    assert int(_mask.sum()) == _krej, (_k, "BH mask/k mismatch (STOP)")
    _surv = sorted([i for i in range(_m) if _mask[i]],
                   key=lambda i: _sw["p_low"][i])
    _i33 = _g["i33"]
    _nsmaller = int((_sw["p_low"] < _sw["p_low"][_i33]).sum())
    _br = ("F_UNIQUE" if _krej == 1 and bool(_mask[_i33]) else
           "F_SMALL_FAMILY" if 1 <= _krej <= SURV_SMALL else
           "F_COMMON" if _krej > SURV_SMALL else "F_NONE_SURVIVES")
    Q225_1[_k] = dict(
        m_types=_m, n_survivors_low=_krej, n_survivors_high=_krejh,
        n_at_p_floor_low=_sw["n_at_floor_low"],
        dnp33_p_low=float(_sw["p_low"][_i33]),
        dnp33_q_low=float(_qv[_i33]),
        dnp33_survives=bool(_mask[_i33]),
        dnp33_rank_by_p=int(_nsmaller + 1),
        dnp33_n_types_with_smaller_p=_nsmaller,
        dnp33_pct_among_type_medians=Q1[_k]["pct_among_type_medians"],
        dnp33_l213_null_pct=Q1[_k]["null_pct"],
        dnp33_pct_strict_at_20k=float(_sw["pct_strict"][_i33]),
        survivor_share=float(_krej / _m),
        top20=[dict(type=_g["names"][i],
                    n_members=int(len(_g["big"][_g["names"][i]])),
                    median_R=float(_sw["real"][i]),
                    p_low=float(_sw["p_low"][i]), q_low=float(_qv[i]))
               for i in _surv[:20]],
        survivor_types=[_g["names"][i] for i in _surv],
        branch=_br)
    log(f"[Q225-1] {_k}: {_krej} of {_m} types survive BH(low) "
        f"({100 * _krej / _m:.1f}%) | HIGH side {_krejh} | at the p floor "
        f"{_sw['n_at_floor_low']} | DNp33 p {_sw['p_low'][_i33]:.3e} q "
        f"{_qv[_i33]:.3e} survives {bool(_mask[_i33])} rank "
        f"{_nsmaller + 1} -> {_br}")
BR1 = Q225_1[PRIMARY]["branch"]
_b1 = [Q225_1[k]["branch"] for k in Q225_1]
log(f"[Q225-1] BRANCH {BR1} (primary {PRIMARY}); all three {_b1}")
q["Q225_1_fdr"] = dict(branch=BR1, branch_primary_substrate=PRIMARY,
                       per_substrate=Q225_1, all_substrate_branches=_b1,
                       agree=bool(len(set(_b1)) == 1))

# =====================================================================
# Q225-2 (DESCRIPTIVE with a registered rule, NO branch): do the survivors
# share an annotation?  Size-matched random type sets give the background.
# =====================================================================
_ANN = {}
for _c in ANN_COLS:
    if _c in ann.columns:
        _v = ann[_c].fillna("").astype(str).to_numpy()
        _ANN[_c] = {int(g): s.strip() for g, s in zip(ann.gi.to_numpy(), _v)}
    else:
        log(f"[Q225-2] column {_c} ABSENT from the annotation release -- "
            f"declared unmeasurable")
q["Q225_2_columns_used"] = sorted(_ANN)
q["Q225_2_columns_absent"] = [c for c in ANN_COLS if c not in _ANN]
assert _ANN, "no annotation column available -- M_UNMEASURABLE (STOP)"


def type_mode(gis, col):
    """modal value of `col` over a type's member cells; "" if none named."""
    vals = [v for v in (_ANN[col].get(g, "") for g in gis) if v]
    if not vals:
        return ""
    return max(sorted(set(vals)), key=vals.count)


Q225_2 = {}
for _k, _g in GRP.items():
    _p = POP[_k]
    _names = _g["names"]
    _m = len(_names)
    _survset = set(Q225_1[_k]["survivor_types"])
    _ns = len(_survset)
    _sidx = np.array([i for i, c in enumerate(_names) if c in _survset],
                     dtype=np.int64)
    assert len(_sidx) == _ns, (_k, "survivor index rebuild (STOP)")
    _tg = {c: [_p["gis"][i] for i in _g["big"][c]] for c in _names}
    _cols = {}
    _rng = np.random.default_rng(SEED_ENR)
    for _col in sorted(_ANN):
        _lab = np.array([type_mode(_tg[c], _col) for c in _names])
        _cats = sorted(set(_lab[_lab != ""]))
        if not _cats or _ns == 0:
            _cols[_col] = dict(n_categories=len(_cats), rows=[],
                               dnp33_label=type_mode(_tg[TYPE_NAME], _col),
                               any_cheaper=False,
                               note="no annotated category or no survivors")
            continue
        _code = np.full(_m, -1, np.int64)
        for _ci, _cat in enumerate(_cats):
            _code[_lab == _cat] = _ci
        _nc = len(_cats)
        _sc = np.bincount(_code[_sidx][_code[_sidx] >= 0], minlength=_nc)
        _bg = np.bincount(_code[_code >= 0], minlength=_nc)
        _nullc = np.empty((B_ENR, _nc), np.int64)
        for _b in range(B_ENR):
            _pick = _rng.choice(_m, size=_ns, replace=False)
            _cp = _code[_pick]
            _nullc[_b] = np.bincount(_cp[_cp >= 0], minlength=_nc)
        _pe = (1.0 + (_nullc >= _sc[None, :]).sum(axis=0)) / (B_ENR + 1.0)
        _bonf = ALPHA / _nc
        _rows = []
        for _ci, _cat in enumerate(_cats):
            _rs = float(_sc[_ci] / _ns)
            _rb = float(_bg[_ci] / _m)
            _rows.append(dict(category=_cat, n_survivor_types=int(_sc[_ci]),
                              survivor_share=_rs, background_share=_rb,
                              enrichment=float(_rs / _rb) if _rb > 0 else None,
                              p_enrich=float(_pe[_ci]),
                              bonferroni_bar=_bonf,
                              names_cheaper_explanation=bool(
                                  _rs >= ENR_SHARE_BAR and
                                  float(_pe[_ci]) <= _bonf)))
        _rows.sort(key=lambda r: -r["survivor_share"])
        _cols[_col] = dict(n_categories=_nc, rows=_rows[:12],
                           dnp33_label=type_mode(_tg[TYPE_NAME], _col),
                           any_cheaper=bool(any(
                               r["names_cheaper_explanation"] for r in _rows)))
        log(f"[Q225-2] {_k} {_col}: {_nc} cats | top {_rows[0]['category']!r} "
            f"share {_rows[0]['survivor_share']:.3f} vs bg "
            f"{_rows[0]['background_share']:.3f} (p {_rows[0]['p_enrich']:.4f})"
            f" | DNp33 {_cols[_col]['dnp33_label']!r} | cheaper "
            f"{_cols[_col]['any_cheaper']}")
    Q225_2[_k] = dict(n_survivors=_ns, per_column=_cols,
                      any_cheaper_explanation=bool(
                          any(v["any_cheaper"] for v in _cols.values())))
q["Q225_2_annotation"] = dict(
    status="DESCRIPTIVE with a registered rule; NO branch",
    rule=f"a category 'names a cheaper explanation' iff it covers >= "
         f"{ENR_SHARE_BAR} of the survivor TYPES and its size-matched "
         f"enrichment p <= {ALPHA}/n_categories (Bonferroni)",
    per_substrate=Q225_2)

# =====================================================================
# Q225-3 (DESCRIPTIVE, NO branch): the first-hop MENU SIZE, measured ON
# THESE substrates (premise 0g: L211's 69 is the l169c operator's number).
# cols = SOURCE in the certified orientation (reach_sub: y[rows] += jv *
# x[cols]), so out-degree = bincount over cols.
# =====================================================================
Q225_3 = {}
for _k, _g in GRP.items():
    _s = SUBS[_k]
    _od = np.bincount(_s["cols"], minlength=_s["n"])
    assert int(_od.sum()) == _s["n_edges"], (_k, "out-degree sum (STOP)")
    _p = POP[_k]
    _lc = np.array([int(_s["loc"][g]) for g in _p["gis"]])
    _odp = _od[_lc]
    _survset = set(Q225_1[_k]["survivor_types"])
    _smem = [i for i, c in enumerate(_p["ct"]) if c in _survset]
    _cl = _p["gis"].index(GI_CARRIER)
    _ml = _p["gis"].index(GI_MIR)
    _enough = len(_smem) >= 10
    Q225_3[_k] = dict(
        carrier_out_degree=int(_odp[_cl]),
        mirror_out_degree=int(_odp[_ml]),
        l211_l169c_menu_note=69,
        population_median_out_degree=float(np.median(_odp)),
        survivor_member_median_out_degree=float(np.median(_odp[_smem]))
        if _smem else None,
        n_survivor_member_cells=len(_smem),
        carrier_pct_in_population=pct_of(float(_odp[_cl]),
                                         [float(x) for x in _odp]),
        carrier_pct_among_survivor_members=pct_of(
            float(_odp[_cl]), [float(_odp[i]) for i in _smem])
        if _enough else None,
        survivor_cohort_too_small=bool(not _enough),
        note="out-degree on THIS substrate; L211's 69 is the l169c/b65 "
             "operator's number, reported for cross-substrate context "
             "only (premise 0g)")
    log(f"[Q225-3] {_k}: carrier out-degree {_odp[_cl]} (pop median "
        f"{np.median(_odp):.1f}, pct "
        f"{Q225_3[_k]['carrier_pct_in_population']:.3f}) | survivor-member "
        f"median {Q225_3[_k]['survivor_member_median_out_degree']} over "
        f"{len(_smem)} cells | mirror {_odp[_ml]}")
q["Q225_3_menu"] = dict(status="DESCRIPTIVE; NO branch",
                        per_substrate=Q225_3)

# =====================================================================
# predictions, scored
# =====================================================================
_PP = Q225_1[PRIMARY]
_p1 = _PP["branch"] == "F_COMMON"
_p2 = _PP["dnp33_q_low"] <= ALPHA
_p3 = _PP["dnp33_n_types_with_smaller_p"] >= 10
_lo, _hi = _PP["n_survivors_low"], _PP["n_survivors_high"]
_p4 = (max(_lo, _hi) >= 2 * max(1, min(_lo, _hi)))
_p5 = _nseed == 15
_p6 = not Q225_2[PRIMARY]["any_cheaper_explanation"]
q["predictions"] = {
    "Q225_P1": dict(registered="branch == F_COMMON (> 10 survivors) on the "
                               "primary substrate",
                    measured=_PP["branch"], correct=bool(_p1)),
    "Q225_P2": dict(registered="DNp33 BH q <= 0.05 on the primary substrate",
                    measured=_PP["dnp33_q_low"], correct=bool(_p2)),
    "Q225_P3": dict(registered=">= 10 types have a strictly smaller p than "
                               "DNp33",
                    measured=_PP["dnp33_n_types_with_smaller_p"],
                    correct=bool(_p3)),
    "Q225_P4": dict(registered="LOW and HIGH survivor counts differ >= 2x",
                    measured=[_lo, _hi], correct=bool(_p4)),
    "Q225_P5": dict(registered="CERT-SEED reproduces l213's stored DNp33 "
                               "null on all 3 substrates (15 checks)",
                    measured=_nseed, correct=bool(_p5)),
    "Q225_P6": dict(registered="no annotation category names a cheaper "
                               "explanation at the registered bar",
                    measured=Q225_2[PRIMARY]["any_cheaper_explanation"],
                    correct=bool(_p6))}
q["n_predictions_correct"] = int(sum(
    1 for v in q["predictions"].values() if v["correct"]))
q["branches"] = dict(Q225_1=BR1)
q["escape_fired"] = _ESCAPE

# the headline, derived from the measurement rather than written in advance
if BR1 == "F_COMMON":
    _head = (f"DNp33 is one of {_PP['n_survivors_low']} descending cell "
             f"types (of {_PP['m_types']}) whose median depth-2 pool reach "
             f"is low beyond a BH-corrected type-label permutation null; it "
             f"ranks {_PP['dnp33_rank_by_p']} of {_PP['m_types']} by "
             f"p-value. The TYPE-level avoidance is REAL and NOT UNIQUE.")
elif BR1 == "F_UNIQUE":
    _head = ("DNp33 is the ONLY type surviving the nonselective FDR at "
             f"alpha {ALPHA}.")
elif BR1 == "F_SMALL_FAMILY":
    _head = (f"DNp33 is one of a small family of {_PP['n_survivors_low']} "
             f"types surviving the nonselective FDR.")
else:
    _head = ("NO type survives the nonselective FDR, DNp33 included: the "
             "L213 type-level reading does not survive multiplicity.")
q["headline"] = _head
log(f"[HEADLINE] {_head}")

q["limitations"] = [
    "One statistic (R = P2/(lam1^2*m_out)), one null family (within-mass-"
    "stratum type-label permutation), one annotation release, three "
    "non-independent substrates sharing a graph and most cells.",
    "BH controls the FDR over TYPE MEDIANS, not over cells; DNp33's median "
    "is a 2-POINT statistic (direction only, never a magnitude -- L213 "
    "limit 1) and every other type's inherits the same caveat scaled by "
    "its member count.",
    "The permutation holds log-out-mass stratum and type SIZE, not "
    "neurotransmitter, side, neuropil or hemilineage composition -- which "
    "is exactly why Q225-2 can only DESCRIBE a shared-annotation family.",
    "The resolution floor is 5.00e-05, so p-values are censored there and "
    "the BH ladder cannot separate types tied at the floor.",
    "Q225-2's modal-label-per-type reduction discards within-type "
    "annotation heterogeneity.",
    "ANATOMICAL leg only: no row mask, no settle, no seed (L164).",
    "A nonselective survivor count de-circularises the TYPE claim only. "
    "The per-cell claims of L206-L212 keep their selected status; "
    "Kriegeskorte's step (3), an independent specimen, is L212's v783 leg.",
]
q["runtime_s"] = time.time() - t0
q["runtime_l225_s"] = time.time() - _T225
_st213c = os.stat(_P213)
assert (_st213c.st_size, _st213c.st_mtime_ns) == _fp213, \
    "l213/static.json CHANGED during this run (STOP)"
os.makedirs("l225", exist_ok=True)
with open("l225/static.json", "w") as _fh:
    json.dump(q, _fh, indent=1, default=float)
log(f"[done] {q['runtime_s']:.1f}s (L225 body {q['runtime_l225_s']:.1f}s) -> "
    f"l225/static.json | {BR1} | predictions "
    f"{q['n_predictions_correct']}/6")
