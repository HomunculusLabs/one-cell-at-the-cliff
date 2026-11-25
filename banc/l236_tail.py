
# =========================== L236 TAIL =====================================
# PREREG l236/PREREG.md, written before this file existed.
MU_MENU = float(U1[MENU].mean())
UM236 = U1[MENU].copy()          # the menu's importances, gathered once
assert UM236.size == MENU.size

# ---------------- CERT-236C (HALTING): the parent's own carrier null -------
WM236 = wm_null(MENU, 2000, 21901)
_rwm = float(np.median(WM236["S"])) / _S_car
_SW3 = S219["Q219_3_weight_matched"]
_n236c = 0
assert _SW3["S_car"] == _S_car, (_SW3["S_car"], _S_car, "CERT-236C S_car")
_n236c += 1
assert _SW3["menu"]["n_edges"] == int(MENU.size), "CERT-236C menu n_edges"
_n236c += 1
assert _SW3["menu"]["n_distinct"] == int(np.unique(MENU).size), \
    "CERT-236C menu n_distinct"
_n236c += 1
assert _SW3["menu_matched"]["ratio_med"] == _rwm, \
    (_SW3["menu_matched"]["ratio_med"], _rwm, "CERT-236C ratio_med (STOP)")
_n236c += 1
for _f, _v in (("S_med", float(np.median(WM236["S"]))),
               ("S_p05", float(np.percentile(WM236["S"], 5))),
               ("S_p95", float(np.percentile(WM236["S"], 95))),
               ("S_car_percentile", float((WM236["S"] < _S_car).mean())),
               ("Q_med", float(np.median(WM236["Q"]))),
               ("align_med", float(np.median(WM236["align"]))),
               ("ratio_Q", float(np.median(WM236["Q"])) / DR["Q"]),
               ("ratio_align", float(np.median(WM236["align"])) / DR["align"])):
    assert _SW3["menu_matched"][_f] == _v, (_f, _SW3["menu_matched"][_f], _v,
                                            "CERT-236C (STOP)")
    _n236c += 1
# the primary carrier numbers of Q219-1
_SQ1 = S219["Q219_1_primary"]["real"]
for _f, _v in (("U", DR["U"]), ("Q", DR["Q"]), ("align", DR["align"]),
               ("m_out", DR["m_out"]), ("S", DR["S"])):
    if _f in _SQ1:
        assert _SQ1[_f] == _v, (_f, _SQ1[_f], _v, "CERT-236C Q219-1 (STOP)")
        _n236c += 1
log(f"[CERT-236C] GREEN {_n236c} stored Q219-3/Q219-1 carrier values "
    f"reproduced by FLOAT EQUALITY (r_med {_rwm:.4f})")


# ---------------- the generalised kernel, admitted by EXACT agreement ------
def wm_cell(w, n_draws, seed, chunk=4000):
    """menu-matched weight-matched null for ANY cell. Admitted below by exact
    array equality with the parent's wm_null on the carrier (CERT-MV pattern).
    """
    k = int(w.size)
    rng = np.random.default_rng(seed)
    out = np.empty(n_draws, np.float64)
    i = 0
    while i < n_draws:
        j = min(i + chunk, n_draws)
        idx = rng.integers(0, UM236.size, size=(j - i, k))
        out[i:j] = UM236[idx] @ w
        i = j
    return out


# EXACT agreement gate: same seed, same draw count, no chunking -> the parent's
# own index stream, so the S arrays must be BIT-IDENTICAL.
_chk = wm_cell(W_CAR, 2000, 21901, chunk=2000)
assert np.array_equal(_chk, WM236["S"]), \
    ("wm_cell != wm_null on the carrier (STOP)",
     float(np.abs(_chk - WM236["S"]).max()))
log("[CERT-236K] GREEN wm_cell reproduces the parent's wm_null EXACTLY on the "
    "carrier (2000 draws, seed 21901, bit-identical)")

# ---------------- the population, and the EXACT partition gate (0i) --------
_blk_rows_all = np.where(_blk_f4)[0]
SRC_BLK = np.unique(src_all[_blk_rows_all])
LOC_BLK = loc_f4[SRC_BLK].astype(np.int64)
assert int(LOC_BLK.min()) >= 0, "a block DN source was dropped (STOP)"
assert np.unique(LOC_BLK).size == LOC_BLK.size, "duplicate local (STOP)"
N_POP = int(LOC_BLK.size)
# PREREG 0a, re-measured HALTING: the 35 actors are a SUBSET of this set
_ACTLOC = np.array(sorted(set(int(v) for v in ACTORS.values())), np.int64)
assert _ACTLOC.size == 35 and bool(np.all(np.isin(_ACTLOC, LOC_BLK))), \
    "the 35 L178 actors are not all block DN sources (STOP)"
log(f"[L236 pop] {N_POP:,} block DN source cells (35 actors inside), "
    f"mu_MENU {MU_MENU:.6e} Q_menu {MU_MENU/DR['mean_u']:.6f}")

# grouping of the operator's edges by SOURCE (exact partition, proven)
_ORD = np.argsort(csr_cols, kind="stable")
_CS = csr_cols[_ORD]
_LO = np.searchsorted(_CS, np.arange(NL), side="left")
_HI = np.searchsorted(_CS, np.arange(NL), side="right")
assert int((_HI - _LO).sum()) == int(csr_cols.size), "grouping not total"
# block-edge grouping (the identity-(B) gate operand)
_blk_edge_src = loc_f4[src_all[_blk_rows_all]].astype(np.int64)
_blk_edge_dst = loc_f4[dst_all[_blk_rows_all]].astype(np.int64)
assert int(_blk_edge_src.min()) >= 0 and int(_blk_edge_dst.min()) >= 0
_nblk_per_cell = np.bincount(_blk_edge_src, minlength=NL)
_ublk_per_cell = np.bincount(_blk_edge_src, weights=U1[_blk_edge_dst],
                             minlength=NL)
assert int(_nblk_per_cell.sum()) == int(_blk_rows_all.size), \
    "block grouping not total (STOP)"
_idB_num = float(_ublk_per_cell[LOC_BLK].sum())
_idB_den = float(_nblk_per_cell[LOC_BLK].sum())
_idB_lhs = _idB_num / _idB_den
_idB_rhs = float(U1[_blk_edge_dst].mean())
_idB_rel = abs(_idB_lhs - _idB_rhs) / abs(_idB_rhs)
assert _idB_rel < 1e-12, (_idB_lhs, _idB_rhs, _idB_rel,
                          "identity (B) exact-partition gate (STOP)")
log(f"[L236 gate B] GREEN edge-count-weighted mean target importance "
    f"{_idB_lhs:.8e} == block edge mean {_idB_rhs:.8e} (rel {_idB_rel:.2e}); "
    f"mu_MENU (carrier-excluded) {MU_MENU:.8e}")

# ---------------- the one pass over 1,253 cells -----------------------------
B236 = 30000
Q_FDR = 0.05
_floor236 = 1.0 / (B236 + 1.0)
_bar1 = Q_FDR / N_POP
log(f"[L236] B {B236:,} -> p floor {_floor236:.6e} vs BH rank-1 bar "
    f"{_bar1:.6e} (floor clears: {_floor236 <= _bar1})")

ROWS236 = []
_t_pop = time.time()


def dec236(w, t, lc):
    """decomp219 WITHOUT its mq > 0 assertion. PREREG AMENDMENT 0L (forced by
    a gate halt, journaled): the left Perron vector has EXACT zeros (cells
    that reach nothing), so a block DN whose targets are all at the Perron
    floor has S_c == 0 and the RATIO r_mean = m_out*mu_MENU/S_c is UNDEFINED,
    not large. L224's law: a zero in the outcome is a model-family verdict,
    not a missing value. Repair = carry the BOUNDED currency
    d_mean = (S_c/m_out)/mu_MENU (0 at the floor, finite everywhere) as the
    ranking primary, and quote r_mean = 1/d_mean only where d_mean > 0.
    Gated against decomp219 at float equality wherever decomp219 is defined
    (CERT-236D)."""
    mu = float(U1.mean())
    ut = U1[t]
    mq = float(ut.mean())
    m_out = float(w.sum())
    S = float(w @ ut)
    return dict(U=float(U1[lc]) / mu, Q=mq / mu, m_out=m_out, S=S, mq=mq,
                align=((S / m_out) / mq) if mq > 0.0 else None)


_n236d = 0
for _i, _lc in enumerate(LOC_BLK):
    _lc = int(_lc)
    _ix = _ORD[_LO[_lc]:_HI[_lc]]
    assert _ix.size > 0, (_lc, "block DN source with no operator out-edge")
    _w = jv_abs_an[_ix]
    _t = csr_rows[_ix].astype(np.int64)
    _d = dec236(_w, _t, _lc)
    _Sc = _d["S"]
    _mo = _d["m_out"]
    _meas = _Sc > 0.0
    if _meas:
        # CERT-236D: the parent's certified decomp219 agrees EXACTLY wherever
        # it is defined, which is what admits dec236 on the rest.
        _dp = decomp219(U1, _w, _t, LAM1, _lc)
        for _f in ("U", "Q", "align", "m_out", "S"):
            assert _dp[_f] == _d[_f], (_lc, _f, _dp[_f], _d[_f], "CERT-236D")
            _n236d += 1
        assert _dp["ident_rel"] < 1e-11, (_lc, "identity II (STOP)")
        _identrel = _dp["ident_rel"]
    else:
        _identrel = None
    _dmean = (_Sc / _mo) / MU_MENU
    _rmean = (1.0 / _dmean) if _dmean > 0.0 else None
    _Sd = wm_cell(_w, B236, 236000 + _i)
    _rmed = (float(np.median(_Sd)) / _Sc) if _meas else None
    _plow = (1.0 + int((_Sd <= _Sc).sum())) / (B236 + 1.0)
    _phigh = (1.0 + int((_Sd >= _Sc).sum())) / (B236 + 1.0)
    ROWS236.append(dict(
        gi=int(SRC_BLK[_i]), local=_lc, n_out=int(_ix.size), m_out=_mo,
        S=_Sc, U=_d["U"], Q=_d["Q"], align=_d["align"], measurable=bool(_meas),
        n_blk=int(_nblk_per_cell[_lc]),
        blk_frac=float(_nblk_per_cell[_lc]) / float(_ix.size),
        d_mean=_dmean, r_mean=_rmean, r_med=_rmed, p_low=_plow, p_high=_phigh,
        null_med_over_mean=float(np.median(_Sd)) / float(_Sd.mean()),
        ident_rel=_identrel))
log(f"[L236] population pass done in {time.time()-_t_pop:.1f}s")
log(f"[CERT-236D] GREEN {_n236d} float equalities: dec236 == the parent's "
    f"certified decomp219 on every cell where decomp219 is defined")

_DM_ = np.array([r["d_mean"] for r in ROWS236])
_MEAS = np.array([r["measurable"] for r in ROWS236])
_NZERO = int((~_MEAS).sum())
_RM = np.where(_MEAS, 1.0 / np.where(_MEAS, _DM_, 1.0), np.inf)
_RD = np.array([(r["r_med"] if r["measurable"] else np.inf)
                for r in ROWS236])
_NO = np.array([r["n_out"] for r in ROWS236], np.float64)
_MO = np.array([r["m_out"] for r in ROWS236])
_PL = np.array([r["p_low"] for r in ROWS236])
_PH = np.array([r["p_high"] for r in ROWS236])
_LOCA = np.array([r["local"] for r in ROWS236], np.int64)
_CARI = int(np.where(_LOCA == LC_CAR)[0][0])
assert bool(_MEAS[_CARI]), "the carrier itself is unmeasurable (STOP)"
log(f"[0L] zero class: {_NZERO} of {N_POP} cells have S_c == 0 exactly "
    f"(all targets at the Perron floor) -> r_mean UNDEFINED, d_mean 0")

# the carrier's r_med MUST be the parent's stored value (currency continuity)
_car_rmed_B = ROWS236[_CARI]["r_med"]
assert abs(_car_rmed_B - _rwm) / _rwm < 0.05, \
    (_car_rmed_B, _rwm, "carrier r_med moved >5% at B=30k (STOP)")

# the BRANCH is read on the MEASURABLE subpopulation (the zero class is
# reported separately and is MORE extreme than any finite value by definition)
_RMm = _RM[_MEAS]
MED_RM = float(np.median(_RMm))
if MED_RM >= 5.0:
    BR236 = "MENU_PROPERTY"
elif MED_RM >= 1.6:
    BR236 = "PARTIAL"
else:
    BR236 = "CELL_SPECIFIC"
# ranks over ALL 1,253 use d_mean ASCENDING (bounded, zero-admitting)
_rank_car = int((_DM_ < _DM_[_CARI]).sum())        # cells strictly MORE extreme
_rank_car_meas = int((_RMm > _RM[_CARI]).sum())
_pct_car = float((_DM_ > _DM_[_CARI]).mean())
_frac5 = float((_RM >= 5.0).mean())                # inf counts as >= 5
_frac5_meas = float((_RMm >= 5.0).mean())
_med_over_mean = MED_RM / float(_RMm.mean())

# ---------------- 0g: the degree confound screen ---------------------------
# screened on d_mean (defined for all 1,253); sign flipped so the reported rho
# is in the r_mean direction
_rho_nout = -spear219(_DM_, _NO)
_rho_mout = -spear219(_DM_, np.log(_MO))
_rho_blkf = -spear219(_DM_, np.array([r["blk_frac"] for r in ROWS236]))
_screen_bites = bool(abs(_rho_nout) >= 0.30 or abs(_rho_mout) >= 0.30)
_dm = (_NO >= 55) & (_NO <= 83)
_dm_n = int(_dm.sum())
_dm_pct = float((_RM[_dm] < _RM[_CARI]).mean())
_dm_rank = int((_RM[_dm] > _RM[_CARI]).sum())


def _fin(x):
    """None instead of a non-finite float (the zero class's r_mean), so the
    artifact stays valid JSON (PREREG amendment 0L)."""
    x = float(x)
    return x if np.isfinite(x) else None


log(f"[0g] spearman(r_mean, n_out) {_rho_nout:+.4f} | "
    f"(r_mean, log m_out) {_rho_mout:+.4f} | (r_mean, blk_frac) "
    f"{_rho_blkf:+.4f} | screen bites {_screen_bites} | degree-matched "
    f"cohort n {_dm_n} carrier rank {_dm_rank} pct {_dm_pct:.4f}")

# ---------------- BH-FDR over the 1,253 p_low (and p_high separately) ------
def bh236(p, q):
    p = np.asarray(p, np.float64)
    m = p.size
    o_ = np.argsort(p, kind="stable")
    ps = p[o_]
    thr = q * (np.arange(1, m + 1) / m)
    ok = ps <= thr
    kmax = int(np.where(ok)[0].max() + 1) if bool(ok.any()) else 0
    rej = np.zeros(m, bool)
    if kmax:
        rej[o_[:kmax]] = True
    qv = np.minimum.accumulate((m * ps / np.arange(1, m + 1))[::-1])[::-1]
    qv = np.minimum(qv, 1.0)
    out = np.empty(m)
    out[o_] = qv
    return rej, out, kmax


_rejL, _qL, _kL = bh236(_PL, Q_FDR)
_rejH, _qH, _kH = bh236(_PH, Q_FDR)
_rank_p = int((_PL < _PL[_CARI]).sum())
log(f"[Q236-2] BH q={Q_FDR}: p_low rejections {_kL} of {N_POP} | carrier "
    f"q {_qL[_CARI]:.6e} rejected {bool(_rejL[_CARI])} (p {_PL[_CARI]:.3e}, "
    f"{_rank_p} cells strictly smaller) | p_high rejections {_kH}")

# ---------------- Q236-3: the homolog --------------------------------------
_LCH = int(loc_f4[GI_HOMOLOG])
_hom_in = bool(_LCH >= 0 and np.any(_LOCA == _LCH))
if _hom_in:
    _HI_ = int(np.where(_LOCA == _LCH)[0][0])
    HOM = dict(in_population=True, gi=GI_HOMOLOG, local=_LCH,
               n_out=ROWS236[_HI_]["n_out"], Q=ROWS236[_HI_]["Q"],
               align=ROWS236[_HI_]["align"], r_mean=_fin(_RM[_HI_]),
               measurable=bool(_MEAS[_HI_]), d_mean=ROWS236[_HI_]["d_mean"],
               r_med=ROWS236[_HI_]["r_med"], p_low=float(_PL[_HI_]),
               q_low=float(_qL[_HI_]), rejected=bool(_rejL[_HI_]),
               rank_above=int((_DM_ < _DM_[_HI_]).sum()),
               pct=float((_DM_ > _DM_[_HI_]).mean()),
               carrier_r_mean=_fin(_RM[_CARI]),
               ratio_to_carrier=_fin(_RM[_HI_] / _RM[_CARI]))
else:
    HOM = dict(in_population=False, gi=GI_HOMOLOG, local=_LCH,
               note="homolog is not a block DN source: leg FALSE BY "
                    "UNMEASURABILITY (L222)")
log("[Q236-3] homolog " + json.dumps(HOM, default=float))

# ---------------- Q236-4 (DESCRIPTION): the 35-actor cohort ---------------
_isact = np.isin(_LOCA, _ACTLOC)
assert int(_isact.sum()) == 35
_actm = _isact & _MEAS
ACT = dict(
    n=35, n_measurable=int(_actm.sum()),
    median_r_mean=float(np.median(_RM[_actm])),
    median_r_med=float(np.median(_RD[_actm])),
    p05=float(np.percentile(_RM[_actm], 5)),
    p95=float(np.percentile(_RM[_actm], 95)),
    carrier_r_mean=_fin(_RM[_CARI]),
    carrier_rank_in_actors=int((_DM_[_isact] < _DM_[_CARI]).sum()),
    status=("DESCRIPTION: observed-derivable from l219/static.json's stored "
            "family medians before this run (PREREG 0c)"))
log(f"[Q236-4] actor cohort median r_mean {ACT['median_r_mean']:.4f} "
    f"(carrier {ACT['carrier_r_mean']:.4f}, rank {ACT['carrier_rank_in_actors']}"
    f" of 35)")

log(f"[Q236-1] {BR236} | population median r_mean {MED_RM:.4f} "
    f"(mean {float(_RM.mean()):.4f}, med/mean {_med_over_mean:.4f}) | "
    f"carrier {float(_RM[_CARI]):.4f} rank {_rank_car} of {N_POP} (meas {_rank_car_meas}) "
    f"pct {_pct_car:.4f} | frac >= 5x {_frac5:.4f} | r_med population "
    f"median {float(np.median(_RD)):.4f}")

# ---------------- the artifact ---------------------------------------------
# the generated script's OWN banner, read from itself and STORED in the
# artifact — the pin l219/static.json denied this card (its "banner" key
# carries L210's). A future card gets banner-inside-artifact for free.
with open("l236_static.py") as _bf:
    _BL236 = [next(_bf) for _ in range(14)]
_BANNER236 = "".join(_BL236)
assert _BANNER236.startswith('"""GENERATED by l236_build.py'), "banner (STOP)"
assert "PREREG l236/PREREG.md. Writes l236/static.json ONLY." in _BANNER236
o["banner_l236"] = _BANNER236
o["design_l236"] = (
    "L236 IS THE 11.4x SPECIAL, OR IS IT THE MENU? L219's menu-matched "
    "weight-matched null reproduces L210's 11.4x while holding u1 fixed, so "
    "the quantity is computable for every cell in one pass. Asked "
    "NONSELECTIVELY over all 1,253 DN source cells of the l169c block (which "
    "CONTAINS all 35 L178 actors), with BH-FDR, a degree screen and the "
    "bilateral homolog. Static: zero rollouts, zero settles.")
o["prereg_l236"] = "l236/PREREG.md"
o["cert_236a"] = o_cert236a
o["cert_236b"] = o_cert236b
o["cert_236c"] = dict(n_checks=int(_n236c), mode="float equality (==)",
                      source="l219/static.json Q219_3 + Q219_1 real",
                      carrier_r_med_B2000=_rwm,
                      carrier_r_med_B30000=_car_rmed_B)
o["cert_236d"] = dict(
    n_checks=int(_n236d), mode="float equality (==)",
    note="dec236 (the zero-admitting decomp of PREREG amendment 0L) equals "
         "the parent's certified decomp219 on every cell where decomp219 is "
         "defined (5 fields x measurable cells)")
o["cert_236k"] = dict(mode="exact array equality (np.array_equal)",
                      n_draws=2000, seed=21901,
                      note="wm_cell admitted only by bit-identity with the "
                           "parent's wm_null on the carrier (CERT-MV pattern)")
o["identity_B_partition"] = dict(
    lhs=_idB_lhs, rhs=_idB_rhs, rel=_idB_rel, bar=1e-12,
    n_block_edges=int(_blk_rows_all.size),
    n_cells=N_POP, mu_MENU_carrier_excluded=MU_MENU,
    Q_menu=MU_MENU / DR["mean_u"],
    note=("PREREG 0i: the edge-count-weighted mean of each cell's unweighted "
          "mean target importance equals the block's edge-destination mean "
          "EXACTLY, so the population is CENTRED by construction and only "
          "its SHAPE is informative"))
o["Q236_1_primary"] = dict(
    branch=BR236, bars=dict(menu_property=5.0, partial=1.6),
    n_cells=N_POP,
    n_measurable=int(_MEAS.sum()), n_zero_class=_NZERO,
    r_mean=dict(median=MED_RM, mean=float(_RMm.mean()),
                med_over_mean=_med_over_mean,
                p05=float(np.percentile(_RMm, 5)),
                p25=float(np.percentile(_RMm, 25)),
                p75=float(np.percentile(_RMm, 75)),
                p95=float(np.percentile(_RMm, 95)),
                min=float(_RMm.min()), max=float(_RMm.max()),
                frac_ge_2=float((_RMm >= 2.0).mean()),
                frac_ge_5_measurable=_frac5_meas,
                frac_ge_5_all=_frac5,
                frac_ge_11p4=float((_RMm >= 11.4016).mean()),
                scope="measurable cells only unless named _all"),
    d_mean_all=dict(median=float(np.median(_DM_)), mean=float(_DM_.mean()),
                    min=float(_DM_.min()), max=float(_DM_.max()),
                    n_zero=_NZERO, carrier=_DM_[_CARI],
                    note="bounded, zero-admitting ranking primary (0L)"),
    r_med_companion=dict(median=float(np.median(_RD[_MEAS])),
                         mean=float(_RD[_MEAS].mean()),
                         carrier=_car_rmed_B,
                         spearman_vs_r_mean=spear219(
                             _RM[_MEAS], _RD[_MEAS]),
                         bias_note=("PREREG 0b: r_med is biased downward at "
                                    "low out-degree because the null's "
                                    "median/mean ratio is degree-dependent")),
    carrier=dict(local=LC_CAR, gi=GI_CARRIER, r_mean=_fin(_RM[_CARI]),
                 rank_above_measurable=_rank_car_meas,
                 r_med=_car_rmed_B, Q=DR["Q"], align=DR["align"],
                 n_out=69, rank_above=_rank_car, percentile=_pct_car,
                 p_low=float(_PL[_CARI]), q_low=float(_qL[_CARI]),
                 rejected=bool(_rejL[_CARI])),
    mu_MENU=MU_MENU, mean_u=DR["mean_u"], Q_menu=MU_MENU / DR["mean_u"],
    currency=("PRIMARY r_mean = m_out * mu_MENU / S_c (analytic, degree-free "
              "by PREREG 0b identity (A)); r_med is the L219-comparable "
              "companion"))
o["Q236_2_fdr"] = dict(
    q=Q_FDR, m=N_POP, bar_rank1=_bar1, B=B236, p_floor=_floor236,
    floor_clears_rank1_bar=bool(_floor236 <= _bar1),
    p_low=dict(n_rejected=_kL, carrier_q=float(_qL[_CARI]),
               carrier_rejected=bool(_rejL[_CARI]),
               carrier_rank_by_p=_rank_p,
               n_at_floor=int((_PL == _floor236).sum()),
               min_p=float(_PL.min())),
    p_high=dict(n_rejected=_kH, min_p=float(_PH.min())),
    disclosure=("PREREG 0f: the menu null ignores neuropil, side and cell "
                "type, so the REJECTION COUNT is a property of the null's "
                "crudeness and is NOT the instrument. The instruments are the "
                "r_mean distribution and the carrier's rank in it."))
o["Q236_3_homolog"] = HOM
o["Q236_4_actors"] = ACT
o["Q236_5_degree_screen"] = dict(
    spearman_r_mean_n_out=_rho_nout,
    spearman_r_mean_log_m_out=_rho_mout,
    spearman_r_mean_blk_frac=_rho_blkf,
    bar=0.30, screen_bites=_screen_bites,
    degree_matched=dict(band=[55, 83], n=_dm_n, carrier_rank_above=_dm_rank,
                        carrier_percentile=_dm_pct),
    note="midrank Spearman (L221) via the parent's certified spear219")
o["rows_per_cell"] = ROWS236

o["Q236_6_zero_class"] = dict(
    n=_NZERO, n_pop=N_POP, frac=float(_NZERO) / N_POP,
    n_out_median=(float(np.median(_NO[~_MEAS])) if _NZERO else None),
    n_out_median_measurable=float(np.median(_NO[_MEAS])),
    blk_frac_median=(float(np.median(np.array(
        [r["blk_frac"] for r in ROWS236])[~_MEAS])) if _NZERO else None),
    p_low_median=(float(np.median(_PL[~_MEAS])) if _NZERO else None),
    n_rejected=(int(_rejL[~_MEAS].sum()) if _NZERO else 0),
    statement=("PREREG AMENDMENT 0L, forced by a HALTING gate: the left "
               "Perron vector has EXACT zeros, so a block DN all of whose "
               "targets sit at the Perron floor has S_c == 0 and its deficit "
               "ratio is UNDEFINED rather than large (L224: a zero in the "
               "outcome is a model-family verdict, not a missing value). "
               "These cells are MORE extreme than every finite r_mean by "
               "definition; the branch is read on the measurable "
               "subpopulation and this class is reported beside it."))

_P1 = BR236 == "CELL_SPECIFIC"
_P2 = (_dm_rank if _screen_bites else _rank_car) <= 9
_P3 = _frac5 <= 0.05
_P4 = _med_over_mean <= 0.80
_P5 = abs(_rho_nout) < 0.30
_P6 = bool(_hom_in and 1.0 < HOM["r_mean"] < float(_RM[_CARI]))
o["predictions"] = dict(
    P1=dict(registered="Q236-1 lands on CELL_SPECIFIC (median r_mean < 1.6)",
            measured=[BR236, MED_RM], correct=bool(_P1)),
    P2=dict(registered="carrier in the TOP 10 by r_mean (<= 9 cells above); "
                       "read degree-matched if 0g bites",
            measured=[_rank_car, _rank_car_meas, _dm_rank, _screen_bites],
            correct=bool(_P2)),
    P3=dict(registered="fraction with r_mean >= 5.0 is <= 0.05",
            measured=_frac5, correct=bool(_P3)),
    P4=dict(registered="r_mean median/mean <= 0.80 (right-skewed)",
            measured=_med_over_mean, correct=bool(_P4)),
    P5=dict(registered="|spearman(r_mean, n_out)| < 0.30",
            measured=_rho_nout, correct=bool(_P5)),
    P6=dict(registered="homolog r_mean strictly between 1.0 and the carrier's",
            measured=[HOM.get("r_mean"), float(_RM[_CARI])],
            correct=bool(_P6)),
    n_correct=int(sum((_P1, _P2, _P3, _P4, _P5, _P6))), n_total=6)
log(f"[predictions] {int(sum((_P1,_P2,_P3,_P4,_P5,_P6)))} of 6 "
    f"(P1 {_P1} P2 {_P2} P3 {_P3} P4 {_P4} P5 {_P5} P6 {_P6})")

o["certification_summary_l236"] = dict(
    cert_236a=int(_n236a), cert_236b=int(_n236b), cert_236c=int(_n236c),
    cert_236d=int(_n236d),
    halting_total=int(_n236a + _n236b + _n236c + _n236d),
    identity_B_rel=_idB_rel,
    slices=_BANNER236,
    cost_slice=("the parent's ~370 s per-draw eigendecomposition loop is CUT; "
                "the cut is admitted by CERT-236A/B/C reproducing its stored "
                "output at float equality (L226/L235)"))

for _p in _RO236:
    _st = _os236.stat(_p)
    assert _FP236[_p] == (int(_st.st_size), int(_st.st_mtime_ns)), \
        (_p, "prior artifact MUTATED during the run (STOP)")
log(f"[L236 read-only] all {len(_FP236)} prior artifacts unchanged")

_os236.makedirs("l236", exist_ok=True)
with open("l236/static.json", "w") as _f:
    json.dump(o, _f, indent=1, default=float)
log(f"[L236] wrote l236/static.json in {time.time()-t0:.1f}s")
