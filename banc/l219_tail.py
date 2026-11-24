# ================= L219 TAIL — TARGET CHOICE or TARGET QUALITY? ============
# PREREG l219/PREREG.md. Static: zero rollouts, zero settles, zero dynamics.
# Everything above this line is VERBATIM certified source (see the banner).

import os as _os219

o["design_l219"] = (
    "L219: decompose the carrier's left-Perron overlap u1[c] over its 69 "
    "out-edges. Identity (I) lam1*u1[c] = sum_e w_e u1[t_e]; identity (II) "
    "U(c) = (m_out/lam) * Q(c) * align(c) in scale-invariant currency. "
    "Branch on whether the l169c draws' advantage is target QUALITY (Q) or "
    "target CHOICE (align). PREREG l219/PREREG.md.")
o["prereg_l219"] = "l219/PREREG.md"

# ---------------- read-only fingerprints of every prior artifact ------------
_RO219 = ["l178/static.json", "l206/static.json", "l210/static.json",
          "l218/static.json", "l210_static.py", "l210_tail.py"]
_FP219 = {}
for _p in _RO219:
    _st = _os219.stat(_p)
    _FP219[_p] = (int(_st.st_size), int(_st.st_mtime_ns))
log(f"[L219 read-only] fingerprinted {len(_FP219)} prior artifacts")

S210 = json.load(open("l210/static.json"))

# ---------------- CERT-219P (HALTING): continuity with the parent cards -----
_n219p = 0
assert S210["Q210_1_primary"]["branch"] == "B_CLOSED_FORM", \
    "L210 branch moved (STOP)"
_n219p += 1
assert S210["Q210_1_primary"]["D10"] == D10 == 10.38807894033274, \
    (S210["Q210_1_primary"]["D10"], D10, "CERT-219P D10 (STOP)")
_n219p += 1
assert S210["Q210_1_primary"]["lam1"] == LAM1, \
    (S210["Q210_1_primary"]["lam1"], LAM1, "CERT-219P lam1 (STOP)")
_n219p += 1
assert S210["Q210_1_primary"]["K_real"] == K_REAL, \
    (S210["Q210_1_primary"]["K_real"], K_REAL, "CERT-219P K_real (STOP)")
_n219p += 1
assert S210["Q210_2_bare"]["u1_carrier_real"] == float(U1[LC_CAR]), \
    "CERT-219P u1[carrier] (STOP)"
_n219p += 1
assert S210["Q210_4_gap"]["gap"] == gap, "CERT-219P gap (STOP)"
_n219p += 1
_ROWS210 = S210["rows_per_draw"]
assert len(_ROWS210) == len(rows210) == 100, "draw count (STOP)"
for _i, (_st210, _mine) in enumerate(zip(_ROWS210, rows210)):
    for _f in ("draw", "n_changed", "lam", "lam_left", "K", "u_car",
               "pred_P10", "meas_P10", "spread_r", "spread_l"):
        assert _st210[_f] == _mine[_f], (_i, _f, _st210[_f], _mine[_f],
                                         "CERT-219P rows_per_draw (STOP)")
        _n219p += 1
    assert bool(_st210["conv_ok"]) and bool(_mine["conv_ok"]), (_i, "conv")
    _n219p += 1
log(f"[CERT-219P] GREEN {_n219p} stored L210 values reproduced by FLOAT "
    f"EQUALITY before any L219 quantity was read")
o["cert_219p"] = dict(n_checks=_n219p, mode="float equality (==)",
                      source="l210/static.json")

# ---------------- small helpers (NEW machinery, nothing certified) ----------
def gini219(x):
    """Gini of a nonnegative vector, sorted-cumulative form."""
    a = np.sort(np.asarray(x, np.float64))
    n = a.size
    s = float(a.sum())
    if n == 0 or s <= 0.0:
        return float("nan")
    i = np.arange(1, n + 1, dtype=np.float64)
    return float((2.0 * float(i @ a) - (n + 1.0) * s) / (n * s))


def _rank219(x):
    a = np.asarray(x, np.float64)
    order = np.argsort(a, kind="stable")
    r = np.empty(a.size, np.float64)
    srt = a[order]
    i = 0
    while i < a.size:
        j = i
        while j + 1 < a.size and srt[j + 1] == srt[i]:
            j += 1
        r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


def spear219(x, y):
    rx, ry = _rank219(x), _rank219(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    dn = float(np.linalg.norm(rx) * np.linalg.norm(ry))
    return float(rx @ ry / dn) if dn > 0 else float("nan")


def decomp219(u, w, t, lam, lc):
    """Identity (II) in the scale-invariant currency (PREREG 0b).
    Returns U, Q, align, m_out, S, and the identity residual."""
    mu = float(u.mean())
    assert mu > 0.0, "mean(u) <= 0 (STOP)"
    ut = u[t]
    mq = float(ut.mean())
    assert mq > 0.0, "mean target u <= 0 (STOP)"
    m_out = float(w.sum())
    S = float(w @ ut)
    U = float(u[lc]) / mu
    Q = mq / mu
    al = (S / m_out) / mq
    rhs = (m_out / lam) * Q * al
    res = abs(U - rhs) / abs(U)
    return dict(U=U, Q=Q, align=al, m_out=m_out, S=S, u_bare=float(u[lc]),
                mean_u=mu, mean_target_u_bare=mq, ident_rel=res)


# ---------------- the REAL wiring: the carrier's 69 out-edges ---------------
IDX_CAR = np.where(csr_cols == LC_CAR)[0]
assert IDX_CAR.size == 69, (IDX_CAR.size, "carrier out-degree != 69 (STOP)")
W_CAR = jv_abs_an[IDX_CAR].copy()
T_CAR = csr_rows[IDX_CAR].astype(np.int64).copy()
assert float(W_CAR.min()) > 0.0, "a carrier out-weight is zero (STOP)"
MOUT_OP = float(W_CAR.sum())

# identity (I), HALTING
_S_car = float(W_CAR @ U1[T_CAR])
_i1 = abs(_S_car - LAM1 * float(U1[LC_CAR])) / abs(_S_car)
assert _i1 < 1e-12, (_S_car, LAM1 * float(U1[LC_CAR]), _i1,
                     "identity (I) lam1*u1[c] != sum_e w_e u1[t_e] (STOP)")
DR = decomp219(U1, W_CAR, T_CAR, LAM1, LC_CAR)
assert DR["ident_rel"] < 1e-12, (DR, "identity (II) real (STOP)")
log(f"[L219 real] S_car {_S_car:.6e} | identity (I) rel {_i1:.2e} | "
    f"m_out_op {MOUT_OP:.6f} | U {DR['U']:.6f} Q {DR['Q']:.6f} "
    f"align {DR['align']:.6f} | identity (II) rel {DR['ident_rel']:.2e}")
o["identity_gates"] = dict(
    identity_I_rel=_i1, identity_II_rel_real=DR["ident_rel"], bar=1e-12,
    S_car=_S_car, lam1_times_u1_car=LAM1 * float(U1[LC_CAR]),
    m_out_operator=MOUT_OP, m_out_raw_log1p=M_OUT["carrier"],
    m_out_operator_over_raw=MOUT_OP / M_OUT["carrier"],
    note=("m_out_operator is sum of |g*W_beta| over the carrier's out-edges "
          "and is the quantity identity (II) uses; M_OUT is L178's RAW "
          "log1p out-mass and is reported for continuity only"))

# ---------------- CERT-WMULT + CERT-219D (HALTING): the 100 l169c draws -----
# DISCLOSED re-transcription (L218 CERT-W50 pattern): the parent's per-draw
# operator rebuild is not exposed as a function, so it is rebuilt here and
# gated by FLOAT EQUALITY of lam / lam_left / K / u_car against rows210.
_nwm = 0
_n219d = 0
ROWS219 = []
for _i, _ch in enumerate(null_changed):
    _jv2 = jv_abs_an.copy()
    _els, _eld, _ean = [], [], []
    _reloc = {}
    for _cidx, _nt in _ch["changed"]:
        _els.append(int(csr_cols[_cidx]))
        _eld.append(int(_nt))
        _jv2[_cidx] = 0.0
        _ean.append(abs(G_F4WA * _vnp[_cidx]))
        if int(csr_cols[_cidx]) == LC_CAR:
            assert _cidx not in _reloc, (_i, _cidx, "carrier edge relocated "
                                                    "twice (STOP)")
            # the moved edge keeps its own value: multiset invariance
            assert abs(G_F4WA * _vnp[_cidx]) == jv_abs_an[_cidx], \
                (_i, _cidx, "CERT-WMULT moved weight changed (STOP)")
            _nwm += 1
            _reloc[int(_cidx)] = int(_nt)
    _ls2 = np.concatenate([csr_cols, np.array(_els, np.int64)])
    _ld2 = np.concatenate([csr_rows, np.array(_eld, np.int64)])
    _va2 = np.concatenate([_jv2, np.array(_ean, np.float64)])

    # the draw's carrier out-edge (weight, target) multiset, rebuilt two ways
    _Tk = T_CAR.copy()
    for _p, _cidx in enumerate(IDX_CAR):
        if int(_cidx) in _reloc:
            _Tk[_p] = _reloc[int(_cidx)]
    _sel = _ls2 == LC_CAR
    _wsel = _va2[_sel]
    _tsel = _ld2[_sel].astype(np.int64)
    _nz = _wsel > 0.0
    assert int(_nz.sum()) == 69, (_i, int(_nz.sum()),
                                  "CERT-WMULT draw out-degree != 69 (STOP)")
    _ordA = np.lexsort((_wsel[_nz], _tsel[_nz]))
    _ordB = np.lexsort((W_CAR, _Tk))
    assert np.array_equal(_wsel[_nz][_ordA], W_CAR[_ordB]), \
        (_i, "CERT-WMULT weight multiset (STOP)")
    assert np.array_equal(_tsel[_nz][_ordA], _Tk[_ordB]), \
        (_i, "CERT-WMULT target multiset (STOP)")
    assert np.array_equal(np.sort(_wsel[_nz]), np.sort(W_CAR)), \
        (_i, "CERT-WMULT sorted weights (STOP)")
    _nwm += 3

    _lam_k, _v_k, _ir = pi_dir(_va2, _ls2, _ld2)
    _lamL_k, _u_k, _il = pi_dir(_va2, _ld2, _ls2)
    _K_k = (float(_u_k[LC_CAR]) * float(_v_k[POOL_IDX].sum())
            / float(_u_k @ _v_k))
    _st = rows210[_i]
    for _f, _got in (("lam", _lam_k), ("lam_left", _lamL_k), ("K", _K_k),
                     ("u_car", float(_u_k[LC_CAR])),
                     ("spread_r", _ir["rel_spread_last6"]),
                     ("spread_l", _il["rel_spread_last6"])):
        assert _st[_f] == _got, (_i, _f, _st[_f], _got,
                                 "CERT-219D (STOP)")
        _n219d += 1
    assert _ir["rel_spread_last6"] < 1e-6 and _il["rel_spread_last6"] < 1e-6, \
        (_i, "draw power iteration not converged (STOP)")
    assert float(_u_k.min()) >= 0.0, (_i, "draw left Perron negative (STOP)")

    _d = decomp219(_u_k, W_CAR, _Tk, _lam_k, LC_CAR)
    assert _d["ident_rel"] < 1e-12, (_i, _d, "identity (II) draw (STOP)")
    _d.update(draw=_i, lam=_lam_k, n_changed=_ch["n_changed"],
              n_car_reloc=len(_reloc),
              n_distinct_targets=int(np.unique(_Tk).size))
    ROWS219.append(_d)
log(f"[CERT-WMULT] GREEN {_nwm} checks: the carrier's out-weight MULTISET is "
    f"float-identical in all 100 draws and the out-degree is 69 in all 100 "
    f"(the PREREG 0a premise, measured not assumed)")
log(f"[CERT-219D] GREEN {_n219d} stored L210 per-draw values reproduced by "
    f"FLOAT EQUALITY from my own rebuild -> the u_k read below ARE the "
    f"certified draws' left Perron vectors")
o["cert_wmult"] = dict(n_checks=_nwm, mode="float equality + exact array "
                       "equality", out_degree_all_draws=69,
                       premise="PREREG 0a: weights travel with the source")
o["cert_219d"] = dict(n_checks=_n219d, mode="float equality (==)",
                      source="l210/static.json rows_per_draw via my rebuild")

# ---------------- Q219-1 (PRIMARY): the product decomposition --------------
_Uk = np.array([r["U"] for r in ROWS219])
_Qk = np.array([r["Q"] for r in ROWS219])
_Ak = np.array([r["align"] for r in ROWS219])
_Lk = np.array([r["lam"] for r in ROWS219])
_identmax = float(max(r["ident_rel"] for r in ROWS219))

rQ = float(np.median(_Qk)) / DR["Q"]
rA = float(np.median(_Ak)) / DR["align"]
rU = float(np.median(_Uk)) / DR["U"]
rL = float(np.median(_Lk)) / LAM1
_prodk = _Uk / DR["U"]
_rho_QA = spear219(np.log(_Qk), np.log(_Ak))

if rQ > 5.0 and rA > 5.0:
    BR219 = "BOTH_EXCEED"
elif rQ > 5.0:
    BR219 = "TARGET_QUALITY"
elif rA > 5.0:
    BR219 = "TARGET_CHOICE"
else:
    BR219 = "NEITHER"
log(f"[Q219-1] {BR219} | rQ {rQ:.4f} | rA {rA:.4f} | rU {rU:.4f} "
    f"| lam ratio {rL:.6f} | bar 5.0 | spearman(logQ,logA) {_rho_QA:+.4f}")
log(f"[Q219-1] real  U {DR['U']:.6f} Q {DR['Q']:.6f} align {DR['align']:.6f}")
log(f"[Q219-1] draws U med {float(np.median(_Uk)):.6f} "
    f"Q med {float(np.median(_Qk)):.6f} "
    f"[p05 {float(np.percentile(_Qk,5)):.6f}, "
    f"p95 {float(np.percentile(_Qk,95)):.6f}] "
    f"align med {float(np.median(_Ak)):.6f} "
    f"[p05 {float(np.percentile(_Ak,5)):.6f}, "
    f"p95 {float(np.percentile(_Ak,95)):.6f}]")

o["Q219_1_primary"] = dict(
    branch=BR219, bar=5.0,
    ratio_Q=rQ, ratio_align=rA, ratio_U_per_draw_median=rU,
    ratio_lam_median=rL,
    real=dict(U=DR["U"], Q=DR["Q"], align=DR["align"], m_out=MOUT_OP,
              lam=LAM1, u_bare=DR["u_bare"], mean_u=DR["mean_u"],
              mean_target_u_bare=DR["mean_target_u_bare"], S=DR["S"]),
    draws=dict(
        U_med=float(np.median(_Uk)), U_p05=float(np.percentile(_Uk, 5)),
        U_p95=float(np.percentile(_Uk, 95)),
        Q_med=float(np.median(_Qk)), Q_p05=float(np.percentile(_Qk, 5)),
        Q_p95=float(np.percentile(_Qk, 95)),
        align_med=float(np.median(_Ak)),
        align_p05=float(np.percentile(_Ak, 5)),
        align_p95=float(np.percentile(_Ak, 95)),
        lam_med=float(np.median(_Lk))),
    real_percentile_U=float((_Uk < DR["U"]).mean()),
    real_percentile_Q=float((_Qk < DR["Q"]).mean()),
    real_percentile_align=float((_Ak < DR["align"]).mean()),
    spearman_logQ_logAlign=_rho_QA,
    per_draw_product_ratio_med=float(np.median(_prodk)),
    identity_II_max_rel_over_draws=_identmax,
    median_composition_disclosure=(
        "median(Q*align) != median(Q)*median(align) (L218): ratio_Q and "
        "ratio_align are separate MARGINALS, ratio_U_per_draw_median is the "
        "per-draw product, and no number here is formed by multiplying "
        "medians"),
    currency_disclosure=(
        "PRIMARY currency is scale-invariant U = u[c]/mean(u) and "
        "Q = mean_e u[t_e]/mean(u) (PREREG 0b, L218's law). The bare "
        "unit-L2 u[c] and mean target u are in real/draws as *_bare."))

# ---------------- Q219-2 (leg a): the per-target contribution table ---------
_contrib = W_CAR * U1[T_CAR]
_ordc = np.argsort(-_contrib)
TOP10 = [dict(rank=int(_r + 1), local_target=int(T_CAR[_j]),
              w=float(W_CAR[_j]), u1_target=float(U1[T_CAR[_j]]),
              u1_target_over_mean=float(U1[T_CAR[_j]]) / DR["mean_u"],
              contribution=float(_contrib[_j]),
              share_of_S=float(_contrib[_j]) / _S_car)
         for _r, _j in enumerate(_ordc[:10])]
GINI_C = gini219(_contrib)
GINI_W = gini219(W_CAR)
RHO_WU = spear219(W_CAR, U1[T_CAR])
log(f"[Q219-2] contribution Gini {GINI_C:.4f} | weight Gini {GINI_W:.4f} | "
    f"spearman(w, u1[t]) {RHO_WU:+.4f} | top-1 share "
    f"{TOP10[0]['share_of_S']:.4f} | top-10 share "
    f"{sum(t['share_of_S'] for t in TOP10):.4f}")

COH219 = {}
for _n, _lc in ACTORS.items():
    _ia = np.where(csr_cols == _lc)[0]
    if _ia.size == 0:
        COH219[_n] = None
        continue
    _wa = jv_abs_an[_ia]
    _ta = csr_rows[_ia].astype(np.int64)
    _da = decomp219(U1, _wa, _ta, LAM1, _lc)
    _ca = _wa * U1[_ta]
    COH219[_n] = dict(n_out=int(_ia.size), U=_da["U"], Q=_da["Q"],
                      align=_da["align"], m_out=_da["m_out"],
                      gini_contrib=gini219(_ca), gini_w=gini219(_wa),
                      spearman_w_u=spear219(_wa, U1[_ta]),
                      ident_rel=_da["ident_rel"])
    assert _da["ident_rel"] < 1e-12, (_n, "identity (II) cohort (STOP)")
_fam = [k for k in COH219 if k.startswith("fam") and COH219[k]]
assert len(_fam) == 33, (len(_fam), "family size (STOP)")


def _fmed(key):
    return float(np.median([COH219[k][key] for k in _fam]))


def _fpct(key, val):
    return float(np.mean([COH219[k][key] < val for k in _fam]))


log(f"[Q219-2] cohort medians (33 family): Q {_fmed('Q'):.4f} "
    f"align {_fmed('align'):.4f} gini_contrib {_fmed('gini_contrib'):.4f} "
    f"| twin Q {COH219['twin']['Q']:.4f} align "
    f"{COH219['twin']['align']:.4f} gini {COH219['twin']['gini_contrib']:.4f}")
o["Q219_2_table"] = dict(
    top10=TOP10, gini_contrib=GINI_C, gini_w=GINI_W, spearman_w_u1t=RHO_WU,
    top1_share=TOP10[0]["share_of_S"],
    top10_share=float(sum(t["share_of_S"] for t in TOP10)),
    n_distinct_targets=int(np.unique(T_CAR).size),
    carrier=COH219["carrier"], twin=COH219["twin"],
    family_median=dict(Q=_fmed("Q"), align=_fmed("align"),
                       gini_contrib=_fmed("gini_contrib"),
                       gini_w=_fmed("gini_w"),
                       spearman_w_u=_fmed("spearman_w_u"),
                       U=_fmed("U"), n_out=_fmed("n_out")),
    family_p05=dict(Q=float(np.percentile([COH219[k]["Q"] for k in _fam], 5)),
                    align=float(np.percentile([COH219[k]["align"]
                                               for k in _fam], 5))),
    family_p95=dict(Q=float(np.percentile([COH219[k]["Q"] for k in _fam], 95)),
                    align=float(np.percentile([COH219[k]["align"]
                                               for k in _fam], 95))),
    carrier_family_percentile=dict(
        Q=_fpct("Q", COH219["carrier"]["Q"]),
        align=_fpct("align", COH219["carrier"]["align"]),
        gini_contrib=_fpct("gini_contrib", GINI_C)),
    all_actors=COH219,
    selection_disclosure=(
        "the carrier was SELECTED for being extreme on a related statistic, "
        "so every carrier-vs-cohort percentile in this block is DESCRIPTIVE "
        "(Kriegeskorte 2009; PREREG 0c). The branch rests on Q219-1/Q219-3, "
        "whose nulls relocate the carrier's OWN edges."))

# ---------------- Q219-3 (leg b): the WEIGHT-MATCHED semi-analytic nulls ---
_pool_rows219 = np.where(_blk_f4 & (src_all != GI_CARRIER))[0]
MENU = loc_f4[dst_all[_pool_rows219]].astype(np.int64)
assert MENU.size == _pool_rows219.size and int(MENU.min()) >= 0, \
    "menu carries a dropped node (STOP)"
assert int(_blk_f4.sum()) > 0 and not bool(np.any(src_all[_pool_rows219]
                                                  == GI_CARRIER)), \
    "menu (STOP)"
log(f"[Q219-3] menu = {MENU.size:,} block edge destinations "
    f"({np.unique(MENU).size:,} distinct cells)")


def wm_null(targets_pool, n_draws, seed):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, targets_pool.size, size=(n_draws, 69))
    T = targets_pool[idx]
    UT = U1[T]
    S = UT @ W_CAR
    Qd = UT.mean(axis=1) / DR["mean_u"]
    Ad = (S / MOUT_OP) / UT.mean(axis=1)
    return dict(S=S, Q=Qd, align=Ad)


WM = wm_null(MENU, 2000, 21901)
NU = wm_null(np.arange(NL, dtype=np.int64), 2000, 21902)
ratio_wm = float(np.median(WM["S"])) / _S_car
ratio_nu = float(np.median(NU["S"])) / _S_car
if ratio_wm > 5.0:
    WMV = "WM_REPRODUCES"
elif ratio_wm <= 2.0:
    WMV = "WM_REFUTES"
else:
    WMV = "WM_PARTIAL"
log(f"[Q219-3] {WMV} | menu-matched median S / S_car {ratio_wm:.4f} "
    f"(S_car pct {float((WM['S'] < _S_car).mean()):.4f}) | node-uniform "
    f"{ratio_nu:.4f} (pct {float((NU['S'] < _S_car).mean()):.4f}) | "
    f"L210 K_ratio_med {S210['Q210_1_primary']['K_ratio_med']:.4f}")
o["Q219_3_weight_matched"] = dict(
    verdict=WMV, bar_reproduces=5.0, bar_refutes=2.0,
    menu=dict(n_edges=int(MENU.size), n_distinct=int(np.unique(MENU).size),
              seed=21901, n_draws=2000,
              construction=("uniform over loc_f4[dst_all[pool_rows]] = "
                            "exactly the array rewire_draws samples its "
                            "partner edge from, so the target law is "
                            "edge-destination weighted as in the real null")),
    S_car=_S_car,
    menu_matched=dict(
        ratio_med=ratio_wm, S_med=float(np.median(WM["S"])),
        S_p05=float(np.percentile(WM["S"], 5)),
        S_p95=float(np.percentile(WM["S"], 95)),
        S_car_percentile=float((WM["S"] < _S_car).mean()),
        Q_med=float(np.median(WM["Q"])), align_med=float(np.median(WM["align"])),
        ratio_Q=float(np.median(WM["Q"])) / DR["Q"],
        ratio_align=float(np.median(WM["align"])) / DR["align"]),
    node_uniform=dict(
        ratio_med=ratio_nu, S_med=float(np.median(NU["S"])),
        S_car_percentile=float((NU["S"] < _S_car).mean()),
        Q_med=float(np.median(NU["Q"])),
        align_med=float(np.median(NU["align"])),
        ratio_Q=float(np.median(NU["Q"])) / DR["Q"],
        ratio_align=float(np.median(NU["align"])) / DR["align"],
        seed=21902, n_draws=2000),
    l210_K_ratio_med=S210["Q210_1_primary"]["K_ratio_med"],
    note=("these nulls hold the REAL u1 fixed and only relocate targets, so "
          "they isolate 'its targets are globally unimportant' from any "
          "eigenvector change the real null also causes"))

# ---------------- Q219-4 (leg c): the draws' own Q / align distributions ----
o["Q219_4_draw_distributions"] = dict(
    n_draws=len(ROWS219),
    Q=dict(med=float(np.median(_Qk)), p05=float(np.percentile(_Qk, 5)),
           p95=float(np.percentile(_Qk, 95)), min=float(_Qk.min()),
           max=float(_Qk.max()),
           real=DR["Q"], real_percentile=float((_Qk < DR["Q"]).mean())),
    align=dict(med=float(np.median(_Ak)), p05=float(np.percentile(_Ak, 5)),
               p95=float(np.percentile(_Ak, 95)), min=float(_Ak.min()),
               max=float(_Ak.max()), real=DR["align"],
               real_percentile=float((_Ak < DR["align"]).mean())),
    lam=dict(med=float(np.median(_Lk)), real=LAM1, ratio=rL),
    m_out_invariant=bool(all(r["m_out"] == MOUT_OP for r in ROWS219)),
    n_distinct_targets=dict(
        real=int(np.unique(T_CAR).size),
        draw_med=float(np.median([r["n_distinct_targets"] for r in ROWS219])),
        draw_min=int(min(r["n_distinct_targets"] for r in ROWS219))),
    n_car_reloc_med=float(np.median([r["n_car_reloc"] for r in ROWS219])),
    rows=ROWS219)

o["Q219_5_l211_relation"] = dict(
    declared_up_front=True,
    statement=("L211 asked the same question in the search-information "
               "currency and found the whole routing excess in the "
               "REMAINDER with the first hop INSIDE its nulls. L219 "
               "decomposes the SAME deficit in the Perron currency. Any "
               "agreement is ONE finding measured twice and is CITED to "
               "L211, never re-banked as independent evidence."))

# ---------------- predictions, scored ---------------------------------------
_P1 = BR219 == "TARGET_QUALITY"
_P2 = True   # CERT-WMULT is halting: reaching here means it passed
_P3 = 5.70 <= ratio_wm <= 22.81
_P4 = DR["align"] < 1.0
_P5 = GINI_C > _fmed("gini_contrib")
o["predictions"] = dict(
    P1=dict(registered="Q219-1 lands on TARGET_QUALITY", measured=BR219,
            correct=bool(_P1)),
    P2=dict(registered="CERT-WMULT passes on all 100 draws, out-degree 69",
            measured=f"{_nwm} checks green, out-degree 69 x 100",
            correct=bool(_P2)),
    P3=dict(registered="ratio_wm in [5.70, 22.81] (factor 2 of L210's 11.4x)",
            measured=ratio_wm, correct=bool(_P3)),
    P4=dict(registered="align_real < 1.0", measured=DR["align"],
            correct=bool(_P4)),
    P5=dict(registered="carrier contribution Gini > family median",
            measured=[GINI_C, _fmed("gini_contrib")], correct=bool(_P5)),
    n_correct=int(sum((_P1, _P2, _P3, _P4, _P5))), n_total=5)
log(f"[predictions] {int(sum((_P1,_P2,_P3,_P4,_P5)))} of 5 "
    f"(P1 {_P1} P2 {_P2} P3 {_P3} P4 {_P4} P5 {_P5})")

o["certification_summary_l219"] = dict(
    cert_219p=_n219p, cert_wmult=_nwm, cert_219d=_n219d,
    halting_total_new=_n219p + _nwm + _n219d,
    identity_I_rel=_i1, identity_II_max_rel=max(_identmax, DR["ident_rel"]),
    inherited_free=("CERT-206 94, CERT-MV 8, CERT-LEFT, CERT-REBUILD 1000, "
                    "CERT-178 420, CERT-GEN 44, CERT-F4, CERT-REW, CERT-NULL "
                    "all re-run inside the verbatim slices"))

# ---------------- read-only check + write ----------------------------------
for _p in _RO219:
    _st = _os219.stat(_p)
    assert _FP219[_p] == (int(_st.st_size), int(_st.st_mtime_ns)), \
        (_p, "prior artifact MUTATED during the run (STOP)")
log(f"[L219 read-only] all {len(_FP219)} prior artifacts unchanged")

_os219.makedirs("l219", exist_ok=True)
with open("l219/static.json", "w") as _f:
    json.dump(o, _f, indent=1, default=float)
log("[L219] wrote l219/static.json")
