# ================= L210 TAIL (appended by l210_build.py) =================
# Everything above this line is VERBATIM certified source:
#   l151_static.py 1-319, l178_tail.py 7-149, the l206_mid bridge,
#   l178_tail.py 348-458 (CERT-REW + the 100 draws), l206_tail.py 22-263
#   (CERT-178's 420 values, lam1, the depth-1..10 sweep with its own
#    float-equality self-check vs L178, the null construction, CERT-NULL).
# So nothing below re-transcribes certified machinery (L85) and no lab module
# is imported (L175: a lab run script is a SCRIPT, not a library).
# PREREG: l210/PREREG.md (registered first). Writes l210/static.json ONLY.
# Zero rollouts, zero settles, zero dynamics.

o["design"] = (
    "L210 the dominant-mode COEFFICIENT: does L206's depth-invariant ~10.39x "
    "carrier pool-reach deficit have a closed form in the LEFT Perron vector? "
    "K(c) = u1[c]*S_v/(u1.v1) on the real f4wA anatomical operator and on each "
    "of the same 100 l169c degree-neutral destination swaps, compared against "
    "the stored depth-10 deficit; plus the spectral gap |lam2|/lam1 by "
    "Hotelling deflation. PREREG l210/PREREG.md.")
o["prereg"] = "l210/PREREG.md"
with open("l210_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(9)])

S206 = json.load(open("l206/static.json"))
G206 = S206["G1_crossing"]

# ---------------- CERT-206 (HALTING) ----------------------------------------
# Reproduce every field of L206's stored G1 rows by FLOAT EQUALITY, using the
# SOURCE's own expressions (L206 lesson: a float-equality claim is a claim
# about the EXPRESSION, not just the operands).
car_n = [SW["carrier"]["P"][d] / (LAM1 ** (d + 1) * _m_car)
         for d in range(DMAX)]
null_n = np.array([[NP_[i, d] / (LAM1 ** (d + 1) * _m_car) for d in range(DMAX)]
                   for i in range(NP_.shape[0])])
_n206 = 0
for d in range(DMAX):
    col = null_n[:, d]
    r = G206["rows"][d]
    assert r["depth"] == d + 1, "CERT-206 row order"
    got = dict(
        carrier=car_n[d], null_med=float(np.median(col)),
        null_p05=float(np.percentile(col, 5)),
        null_p95=float(np.percentile(col, 95)),
        pct=float((col < car_n[d]).mean() * 100),
        ratio_med_over_carrier=(float(np.median(col) / car_n[d])
                                if car_n[d] else None),
        carrier_share=SW["carrier"]["share"][d],
        null_share_med=float(np.median(NP_[:, d] / NT_[:, d])),
        carrier_cos_v1=SW["carrier"]["cos_v1"][d])
    for k_, v_ in got.items():
        assert v_ == r[k_], (d + 1, k_, v_, r[k_], "CERT-206 (STOP)")
        _n206 += 1
assert LAM1 == G206["lam1"], "CERT-206 lam1 (STOP)"
_n206 += 1
# the source's OWN expression, cut included (L206 lesson: a float-equality
# claim is a claim about the EXPRESSION, not just the operands — d_conv_car is
# None here, so L206's "tail" is the depth-10 value alone)
_ratd = [(i + 1, v) for i, v in enumerate(G206["deficit_ratio_by_depth"])
         if v is not None]
_cut206 = d_conv_car if d_conv_car is not None else DMAX
_tailr206 = [v for dd_, v in _ratd if dd_ >= _cut206] or [v for _, v in _ratd]
assert float(np.mean(_tailr206)) == G206["deficit_ratio_tail_mean"], \
    (_tailr206, G206["deficit_ratio_tail_mean"], "CERT-206 tail mean (STOP)")
assert float((max(_tailr206) - min(_tailr206)) / max(_tailr206)) == \
    G206["deficit_ratio_tail_spread"], "CERT-206 tail spread (STOP)"
_n206 += 2
D10 = G206["deficit_ratio_by_depth"][DMAX - 1]
assert D10 == 10.38807894033274, (D10, "CERT-206 D10 pin (STOP)")
_n206 += 1
log(f"[CERT-206] GREEN {_n206} stored L206 G1 values reproduced by FLOAT "
    f"EQUALITY (10 depths x 9 fields + lam1 + tail mean + the D10 pin); "
    f"D10 = {D10:.11f}")
o["cert_206"] = dict(n_checks=_n206, mode="float equality (==)",
                     source="l206/static.json G1_crossing",
                     D10=D10)

# ---------------- CERT-MV (HALTING): the fast matvec is the certified one ---
def mv(x, jv, ls, ld):
    """A x for the COO operator with values jv, sources ls, targets ld.
    Transposition is the SAME function with ls/ld swapped — no new machinery."""
    return np.bincount(ld, weights=jv * x[ls], minlength=NL)


_rngmv = np.random.default_rng(21001)
_probes = dict(ones=np.ones(NL), e_car=np.zeros(NL), v1=V1.copy(),
               rand=_rngmv.random(NL))
_probes["e_car"][LC_CAR] = 1.0
_nmv = 0
for _pn, _px in _probes.items():
    a = jmatvec(_px, jv_abs_an, csr_cols, csr_rows)
    b = mv(_px, jv_abs_an, csr_cols, csr_rows)
    assert np.array_equal(a, b), (_pn, "CERT-MV forward (STOP)")
    aT = jmatvec(_px, jv_abs_an, csr_rows, csr_cols)
    bT = mv(_px, jv_abs_an, csr_rows, csr_cols)
    assert np.array_equal(aT, bT), (_pn, "CERT-MV transpose (STOP)")
    _nmv += 2
# bilinear identity: u.(A x) == (A^T u).x  (summation order differs -> rel bar)
_u0 = _rngmv.random(NL)
_x0 = _rngmv.random(NL)
_lhs = float(_u0 @ mv(_x0, jv_abs_an, csr_cols, csr_rows))
_rhs = float(mv(_u0, jv_abs_an, csr_rows, csr_cols) @ _x0)
_bil = abs(_lhs - _rhs) / abs(_lhs)
assert _bil < 1e-12, (_lhs, _rhs, _bil, "CERT-MV bilinear (STOP)")
log(f"[CERT-MV] GREEN {_nmv} exact array equalities vs the certified "
    f"np.add.at matvec (4 probes x 2 index orders); bilinear rel {_bil:.2e}")
o["cert_mv"] = dict(n_checks=_nmv, mode="exact array equality",
                    bilinear_rel_diff=_bil,
                    note="transpose is the same function with ls/ld swapped")


# ---------------- power iteration in either direction -----------------------
def pi_dir(jv, ls, ld, iters=400):
    v = np.ones(NL) / math.sqrt(NL)
    lam, hist = 0.0, []
    for i in range(iters):
        w = mv(v, jv, ls, ld)
        nrm = float(np.linalg.norm(w))
        if nrm == 0.0:
            return 0.0, v, dict(rayleigh=0.0, rel_spread_last6=1.0)
        v = w / nrm
        lam = nrm
        if i >= iters - 6:
            hist.append(nrm)
    ray = float(v @ mv(v, jv, ls, ld))
    return lam, v, dict(rayleigh=ray,
                        rel_spread_last6=float((max(hist) - min(hist))
                                               / max(hist)))


# CERT-LEFT: right replay reproduces LAM1/V1; left iteration agrees on lam1
_lamR, _vR, _infR = pi_dir(jv_abs_an, csr_cols, csr_rows)
_relR = abs(_lamR - LAM1) / LAM1
_cosR = abs(float(_vR @ V1))
assert _relR < 1e-12 and abs(_cosR - 1.0) < 1e-12, (_relR, _cosR, "CERT-LEFT R")
LAM1L, U1, INFL = pi_dir(jv_abs_an, csr_rows, csr_cols)
_relL = abs(LAM1L - LAM1) / LAM1
assert INFL["rel_spread_last6"] < 1e-6, ("left PI not converged", INFL)
assert _relL < 1e-9, (LAM1L, LAM1, _relL, "CERT-LEFT lam1 disagreement (STOP)")
assert float(U1.min()) >= 0.0, "left Perron vector not nonnegative"
log(f"[CERT-LEFT] GREEN right-replay rel {_relR:.2e} / |cos-1| "
    f"{abs(_cosR-1.0):.2e}; left lam1 {LAM1L:.6f} vs {LAM1:.6f} "
    f"(rel {_relL:.2e}, spread {INFL['rel_spread_last6']:.2e})")
o["cert_left"] = dict(lam1_right_replay=_lamR, rel_vs_LAM1_right=_relR,
                      cos_v1_right=_cosR, lam1_left=LAM1L,
                      rel_vs_LAM1_left=_relL,
                      left_rel_spread_last6=INFL["rel_spread_last6"],
                      right_rel_spread_last6=_infR["rel_spread_last6"],
                      iters=400)

# ---------------- K: the dominant-mode coefficient --------------------------
POOL_IDX = np.concatenate([POOL_L[pk] for pk in POOL_L])
assert POOL_IDX.size == 303, (POOL_IDX.size, "pool cell count")
assert np.unique(POOL_IDX).size == 303, "pool cells not disjoint"


def coeff(u, v, c_local):
    """K(c) = u[c] * (sum of v over the pool cells) / (u . v).
    Invariant to the scaling of u and of v."""
    return float(u[c_local]) * float(v[POOL_IDX].sum()) / float(u @ v)


K_REAL = coeff(U1, V1, LC_CAR)
_P10 = SW["carrier"]["P"][DMAX - 1]
C_real = _P10 / (LAM1 ** DMAX * K_REAL)
K_TWIN = coeff(U1, V1, LC_TWIN)
C_twin = SW["twin"]["P"][DMAX - 1] / (LAM1 ** DMAX * K_TWIN)
log(f"[K] real carrier K {K_REAL:.6e} | P10 {_P10:.6e} | "
    f"lam1^10*K {LAM1**DMAX*K_REAL:.6e} | C_real {C_real:.6f} "
    f"(twin C {C_twin:.6f})")

# Q210-5: the 35-actor cohort in the coefficient currency
K_COH = {n: coeff(U1, V1, lc) / M_OUT[n] for n, lc in ACTORS.items()}
_kv = sorted(K_COH.values())
_kcar = K_COH["carrier"]
_rank = int(sum(1 for x in _kv if x < _kcar)) + 1
log(f"[Q210-5] carrier K/m_out {_kcar:.6e} rank {_rank} of {len(K_COH)} "
    f"(family median {float(np.median([K_COH[n] for n in K_COH if n.startswith('fam')])):.6e})")

# ---------------- the 100 draws: rebuild, certify, then eigen ---------------
_nreb = 0
rows210 = []
for i, ch in enumerate(null_changed):
    jv2 = jv_abs_an.copy()
    extra_ls, extra_ld, extra_an = [], [], []
    for cidx, new_target in ch["changed"]:
        extra_ls.append(int(csr_cols[cidx]))
        extra_ld.append(int(new_target))
        jv2[cidx] = 0.0
        extra_an.append(abs(G_F4WA * _vnp[cidx]))
    ls2 = np.concatenate([csr_cols, np.array(extra_ls, np.int64)])
    ld2 = np.concatenate([csr_rows, np.array(extra_ld, np.int64)])
    va2 = np.concatenate([jv2, np.array(extra_an, np.float64)])
    # CERT-REBUILD: the forward walk must reproduce the certified null numbers
    xa = np.zeros(NL)
    xa[LC_CAR] = 1.0
    for dd in range(1, DMAX + 1):
        ya = np.zeros(NL)
        np.add.at(ya, ld2, va2 * xa[ls2])
        xa = ya
        _got = float(sum(xa[POOL_L[pk]].sum() for pk in POOL_L))
        assert _got == NP_[i, dd - 1], (i, dd, _got, NP_[i, dd - 1],
                                        "CERT-REBUILD (STOP)")
        _nreb += 1
    lam_k, v_k, inf_rk = pi_dir(va2, ls2, ld2)
    lamL_k, u_k, inf_lk = pi_dir(va2, ld2, ls2)
    ok = (inf_rk["rel_spread_last6"] < 1e-6 and inf_lk["rel_spread_last6"] < 1e-6
          and abs(lamL_k - lam_k) / lam_k < 1e-9)
    K_k = float(u_k[LC_CAR]) * float(v_k[POOL_IDX].sum()) / float(u_k @ v_k)
    rows210.append(dict(draw=i, n_changed=ch["n_changed"], lam=lam_k,
                        lam_left=lamL_k, K=K_k, u_car=float(u_k[LC_CAR]),
                        pred_P10=lam_k ** DMAX * K_k,
                        meas_P10=float(NP_[i, DMAX - 1]),
                        conv_ok=bool(ok),
                        spread_r=inf_rk["rel_spread_last6"],
                        spread_l=inf_lk["rel_spread_last6"]))
log(f"[CERT-REBUILD] GREEN {_nreb} stored null values (100 draws x depths "
    f"1-10) reproduced by FLOAT EQUALITY from my own operator rebuild")
o["cert_rebuild"] = dict(n_checks=_nreb, mode="float equality (==)",
                         source="the certified null loop's NP_")

_nconv = sum(1 for r in rows210 if r["conv_ok"])
_lams = np.array([r["lam"] for r in rows210])
_Ks = np.array([r["K"] for r in rows210])
_ucs = np.array([r["u_car"] for r in rows210])
_pred = _lams ** DMAX * _Ks
_meas = np.array([r["meas_P10"] for r in rows210])
C_null = float(np.median(_meas / _pred))

# ---------------- Q210-1 (PRIMARY) ------------------------------------------
R_asym = float(np.median(_pred)) / (LAM1 ** DMAX * K_REAL)
R_bare = float(np.median(_ucs)) / float(U1[LC_CAR])
rel = R_asym / D10
if _nconv < len(rows210) or INFL["rel_spread_last6"] >= 1e-6:
    BR = "B_DEGENERATE"
elif abs(rel - 1.0) <= 0.10:
    BR = "B_CLOSED_FORM"
elif 0.5 <= rel <= 2.0:
    BR = "B_ORDER_ONLY"
else:
    BR = "B_NO_MATCH"
log(f"[Q210-1] {BR} | R_asym {R_asym:.4f} vs D10 {D10:.4f} "
    f"(ratio {rel:.4f}) | R_bare {R_bare:.4f} | converged draws "
    f"{_nconv}/{len(rows210)}")
log(f"[Q210-3] C_real {C_real:.6f} | C_null_med {C_null:.6f} | "
    f"C_twin {C_twin:.6f} | carrier cos(x10,v1) "
    f"{SW['carrier']['cos_v1'][DMAX-1]:.6f}")

o["Q210_1_primary"] = dict(
    branch=BR, R_asym=R_asym, D10=D10, ratio_R_over_D10=rel,
    bar=0.10, n_draws=len(rows210), n_converged=_nconv,
    K_real=K_REAL, lam1=LAM1, pred_P10_real=LAM1 ** DMAX * K_REAL,
    meas_P10_real=_P10,
    null_K_med=float(np.median(_Ks)), null_K_p05=float(np.percentile(_Ks, 5)),
    null_K_p95=float(np.percentile(_Ks, 95)),
    null_lam_med=float(np.median(_lams)),
    null_lam_min=float(_lams.min()), null_lam_max=float(_lams.max()),
    lam_ratio_med_pow10=float(np.median(_lams) ** DMAX / LAM1 ** DMAX),
    K_ratio_med=float(np.median(_Ks)) / K_REAL,
    carrier_K_percentile=float((_Ks < K_REAL).mean() * 100))
o["Q210_2_bare"] = dict(
    R_bare=R_bare, u1_carrier_real=float(U1[LC_CAR]),
    null_u_car_med=float(np.median(_ucs)),
    null_u_car_p05=float(np.percentile(_ucs, 5)),
    null_u_car_p95=float(np.percentile(_ucs, 95)),
    carrier_u_percentile=float((_ucs < float(U1[LC_CAR])).mean() * 100),
    rel_vs_R_asym=R_bare / R_asym,
    disclosure=("unit-L2 normalisation of u on two different operators is a "
                "CONVENTION, not a canonical comparison; Q210-1's K is the "
                "scaling-invariant form and carries the branch"))
o["Q210_3_ceiling"] = dict(
    C_real=C_real, C_twin=C_twin, C_null_med=C_null,
    C_null_p05=float(np.percentile(_meas / _pred, 5)),
    C_null_p95=float(np.percentile(_meas / _pred, 95)),
    cos_x10_v1_carrier=SW["carrier"]["cos_v1"][DMAX - 1],
    cos_x10_v1_twin=SW["twin"]["cos_v1"][DMAX - 1],
    bar=0.10,
    pointwise_reachable=bool(abs(C_real - 1.0) <= 0.10),
    note=("if |C_real-1| > 0.10 a Q210-1 pass is a RATIO-level pass "
          "(error cancelling between numerator and denominator), never a "
          "pointwise one"))
o["Q210_5_cohort"] = dict(
    carrier_K_per_mass=_kcar, carrier_rank_of=len(K_COH), carrier_rank=_rank,
    twin_K_per_mass=K_COH["twin"],
    family_med=float(np.median([K_COH[n] for n in K_COH
                                if n.startswith("fam")])),
    all_actors={n: K_COH[n] for n in K_COH},
    l178_depth2_rank_for_reference=S178["E_anatomical"].get("carrier_rank"),
    note="K/m_out is the depth-infinity analogue of L178's per-mass reach")

# ---------------- Q210-4: the spectral gap by Hotelling deflation -----------
def lam2_defl(jv, ls, ld, v1, u1, iters=400, seed=21004):
    uv = float(u1 @ v1)
    rng = np.random.default_rng(seed)
    x = rng.random(NL)
    x -= v1 * float(u1 @ x) / uv
    x /= np.linalg.norm(x)
    hist = []
    for i in range(iters):
        y = mv(x, jv, ls, ld)
        y -= v1 * float(u1 @ y) / uv
        nrm = float(np.linalg.norm(y))
        if nrm == 0.0:
            return 0.0, dict(rel_spread_last6=0.0, last6=[], converged=True)
        x = y / nrm
        if i >= iters - 6:
            hist.append(nrm)
    sp = float((max(hist) - min(hist)) / max(hist))
    return float(np.median(hist)), dict(rel_spread_last6=sp, last6=hist,
                                        converged=bool(sp < 1e-6))


LAM2, INF2 = lam2_defl(jv_abs_an, csr_cols, csr_rows, V1, U1)
gap = LAM2 / LAM1
log(f"[Q210-4] |lam2| ~ {LAM2:.6f} | lam2/lam1 {gap:.6f} | rel spread "
    f"{INF2['rel_spread_last6']:.2e} | converged {INF2['converged']}")
o["Q210_4_gap"] = dict(
    lam2_estimate=LAM2, lam1=LAM1, gap=gap,
    rel_spread_last6=INF2["rel_spread_last6"],
    converged=INF2["converged"],
    last6=INF2["last6"],
    range_if_not_converged=[float(min(INF2["last6"])),
                            float(max(INF2["last6"]))] if INF2["last6"] else None,
    method=("Hotelling deflation x <- A x - v1*(u1.x)/(u1.v1), real power "
            "iteration: a COMPLEX subdominant pair will not converge and is "
            "reported as NOT_CONVERGED with its range, never as a number"),
    implied_mixing=("misalignment of x_d from v1 decays like (|lam2|/lam1)^d "
                    "if lam2 is real and simple"))

o["rows_per_draw"] = rows210
o["predictions"] = dict(
    Q210_1=dict(registered="B_CLOSED_FORM", measured=BR,
                correct=bool(BR == "B_CLOSED_FORM")),
    Q210_2=dict(registered="|R_bare/R_asym - 1| <= 0.25",
                measured=R_bare / R_asym,
                correct=bool(abs(R_bare / R_asym - 1.0) <= 0.25)),
    Q210_3=dict(registered="|C_real - 1| > 0.10 and C_real in [0.75, 1.00)",
                measured=C_real,
                correct=bool(abs(C_real - 1.0) > 0.10
                             and 0.75 <= C_real < 1.0)),
    Q210_4=dict(registered="gap in [0.75, 0.95], converged",
                measured=gap,
                correct=bool(INF2["converged"] and 0.75 <= gap <= 0.95)),
    Q210_5=dict(registered="carrier in the bottom 3 of 35", measured=_rank,
                correct=bool(_rank <= 3)))
_npred = sum(1 for v in o["predictions"].values() if v["correct"])
log(f"[PREDICTIONS] {_npred} of {len(o['predictions'])} correct: "
    + " ".join(f"{k}={'Y' if v['correct'] else 'N'}"
               for k, v in o["predictions"].items()))

import os
os.makedirs("l210", exist_ok=True)
with open("l210/static.json", "x") as f:
    json.dump(o, f, indent=1, default=float)
log("[done] wrote l210/static.json")
