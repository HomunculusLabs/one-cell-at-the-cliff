# ================= L218 TAIL (appended by l218_build.py) =================
# Everything above this line is VERBATIM certified source:
#   l151_static.py 1-319, l178_tail.py 7-149, the l206_mid bridge,
#   l178_tail.py 348-458 (CERT-REW + the 100 draws), l206_tail.py 22-263
#   (CERT-178, lam1, the depth-1..10 sweep + its self-check, the null
#    construction, CERT-NULL), and CERT-210M = l210_tail.py lines 1-326
#   (CERT-206 HALTING, CERT-MV, CERT-LEFT, CERT-REBUILD HALTING, the K
#    coefficient, the 100 per-draw power iterations -> rows210, Q210-1/2/3/5
#    and the Hotelling gap) SLICED to CUT L210's own predictions/writer block
#    (L213: a successor build slices the parent tail at the end of its
#    measurement block so every parent gate re-runs for free while the
#    parent's json.dump is excluded by the forbidden-token audit).
# So nothing below re-transcribes a certified def (L85) and no lab module is
# imported (L175: a lab run script is a SCRIPT, not a library).
# PREREG: l218/PREREG.md (registered first). Writes l218/static.json ONLY.
# Zero rollouts, zero settles, zero dynamics.

import time as _time
_T0 = _time.time()


def _el(tag):
    log(f"[time] {tag}: {_time.time() - _T0:.1f}s")


_el("CERT-210M complete (parent measurement block re-run)")

o["design"] = (
    "L218 the CONVERGENCE CORRECTION as its own object: extend L206's deficit "
    "profile and L210's closed-form prediction from depth 10 to depth 50 on "
    "the f4wA anatomical operator and all 100 l169c destination swaps, and ask "
    "whether the measured deficit converges to the u1-overlap ratio, to a "
    "different plateau, or to no plateau at all; plus the subdominant-overlap "
    "account of the carrier's slower mixing. PREREG l218/PREREG.md.")
o["prereg"] = "l218/PREREG.md"
with open("l218_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(10)])

o["parent_l210"] = dict(
    design=("L210 the dominant-mode COEFFICIENT (re-run verbatim as "
            "CERT-210M; its gates are this card's inherited certification)"),
    prereg="l210/PREREG.md")

# ---------------- read-only fingerprints of every prior artifact ------------
import os as _os
_PRIORS = ["l178/static.json", "l206/static.json", "l210/static.json",
           "l210_static.py"]
_FP0 = {p: (_os.stat(p).st_size, _os.stat(p).st_mtime_ns) for p in _PRIORS}
S210 = json.load(open("l210/static.json"))

# ---------------- CERT-218T (HALTING): L210's stored table reproduced -------
# Nothing at d > 10 is computed until this is green. rows210 was RE-COMPUTED
# by the CERT-210M slice (full per-draw power iterations), never read.
_n218t = 0


def _leafcmp(got, want, path):
    """recursive leaf compare at FLOAT/EXACT equality (L211 pattern)."""
    global _n218t
    if isinstance(want, dict):
        assert isinstance(got, dict), (path, "type", type(got))
        assert set(got) == set(want), (path, sorted(set(got) ^ set(want)))
        for k in want:
            _leafcmp(got[k], want[k], f"{path}.{k}")
    elif isinstance(want, list):
        assert isinstance(got, (list, tuple)), (path, "type", type(got))
        assert len(got) == len(want), (path, len(got), len(want))
        for i, w in enumerate(want):
            _leafcmp(got[i], w, f"{path}[{i}]")
    else:
        if isinstance(want, bool) or isinstance(got, bool):
            assert bool(got) == bool(want), (path, got, want, "CERT-218T")
        elif want is None:
            assert got is None, (path, got, "CERT-218T")
        elif isinstance(want, str):
            assert got == want, (path, "CERT-218T str")
        else:
            assert float(got) == float(want), (path, got, want, "CERT-218T")
        _n218t += 1


_stored_rows = S210["rows_per_draw"]
assert len(_stored_rows) == len(rows210) == 100, \
    (len(_stored_rows), len(rows210), "CERT-218T row count (STOP)")
for _i, (_g, _w) in enumerate(zip(rows210, _stored_rows)):
    _leafcmp(_g, _w, f"rows_per_draw[{_i}]")
_n_rowchk = _n218t
for _key in ("Q210_1_primary", "Q210_2_bare", "Q210_3_ceiling",
             "Q210_5_cohort", "Q210_4_gap", "cert_206", "cert_mv",
             "cert_rebuild", "cert_178", "cert_null", "spectral"):
    _leafcmp(o[_key], S210[_key], _key)
log(f"[CERT-218T] GREEN {_n218t} stored L210 values reproduced by FLOAT "
    f"EQUALITY ({_n_rowchk} from the 100-draw per-draw table, "
    f"{_n218t - _n_rowchk} from the headline/certification blocks) BEFORE any "
    f"d>10 number was read")
o["cert_218t"] = dict(n_checks=_n218t, n_per_draw=_n_rowchk,
                      mode="float equality (==)",
                      source="l210/static.json rows_per_draw + headline blocks",
                      note=("rows210 was RECOMPUTED by the CERT-210M slice "
                            "(100 draws x 2 power iterations), not read"))

# the registered pins, asserted (not assumed) before use
GAP = o["Q210_4_gap"]["gap"]
assert GAP == 0.8928793607351002, (GAP, "CERT-218T gap pin (STOP)")
assert D10 == 10.38807894033274, (D10, "CERT-218T D10 pin (STOP)")
assert o["Q210_1_primary"]["branch"] == "B_CLOSED_FORM", "L210 branch drift"
_el("CERT-218T")

# =============== THE EXTENSION (every number below is new) ==================
DEEP = 50
LC = LC_CAR
POOL_KEYS = list(POOL_L)


def _psum_sweep(x):
    """sweep_actor's OWN pool-sum expression, character for character, so the
    depth-1..10 comparison with SW is a bit-level one (L206's law: a
    float-equality claim is a claim about the EXPRESSION)."""
    return float(sum({pk: float(x[POOL_L[pk]].sum()) for pk in POOL_L}.values()))


def _psum_null(xa):
    """the null loop's OWN pool-sum expression (differs from _psum_sweep in
    where float() is applied -- the two are NOT interchangeable)."""
    return float(sum(xa[POOL_L[pk]].sum() for pk in POOL_L))


# ---- the real carrier walk to DEEP, gated on its first 10 depths -----------
# AMENDMENT A1, disclosed (made after the PREREG, changes no registered
# quantity): the PREREG's degeneracy guard says "any P_d ... zero" and was
# written for the float64 OVERFLOW risk at large d. It fires at d=1 for a
# reason that is not degeneracy at all: the carrier's 69 out-edges reach NO
# pool cell directly, so P_1 == 0 is a STRUCTURAL anatomical fact that L206
# already stores (its deficit_ratio_by_depth[0] is None, by the same cut).
# The guard is therefore scoped to the depths the registered statistics are
# READ at -- d >= 2 for D_d / C_prof (exactly L206's own reporting range) and
# d = 10..50 for every branch-bearing quantity. d=1 is RECORDED, not used.
D_FIRST = 2
_x = np.zeros(NL)
_x[LC] = 1.0
P_REAL = []
for _d in range(1, DEEP + 1):
    _x = jmatvec(_x, jv_abs_an, csr_cols, csr_rows)
    _p = _psum_sweep(_x)
    assert np.isfinite(_p), (_d, _p, "real walk FINITENESS (STOP)")
    assert _p > 0.0 or _d < D_FIRST, (_d, _p, "real walk POSITIVITY (STOP)")
    P_REAL.append(_p)
assert P_REAL[0] == 0.0, (P_REAL[0], "A1 premise: P_1 is a structural zero")
_nw50 = 0
for _d in range(DMAX):
    assert P_REAL[_d] == SW["carrier"]["P"][_d], \
        (_d + 1, P_REAL[_d], SW["carrier"]["P"][_d], "CERT-W50 real (STOP)")
    _nw50 += 1

# ---- the 100 draw walks to DEEP, each gated on its first 10 depths ---------
# DISCLOSED re-transcription: the operator rebuild below repeats the slice's
# own construction (it is not exposed as a function there). Its GATE is the
# 1,000 float equalities against NP_ -- the same gate CERT-REBUILD uses.
P_NULL = np.zeros((len(null_changed), DEEP))
REB = []
for _i, _ch in enumerate(null_changed):
    jv2 = jv_abs_an.copy()
    extra_ls, extra_ld, extra_an = [], [], []
    for cidx, new_target in _ch["changed"]:
        extra_ls.append(int(csr_cols[cidx]))
        extra_ld.append(int(new_target))
        jv2[cidx] = 0.0
        extra_an.append(abs(G_F4WA * _vnp[cidx]))
    ls2 = np.concatenate([csr_cols, np.array(extra_ls, np.int64)])
    ld2 = np.concatenate([csr_rows, np.array(extra_ld, np.int64)])
    va2 = np.concatenate([jv2, np.array(extra_an, np.float64)])
    REB.append((ls2, ld2, va2))
    xa = np.zeros(NL)
    xa[LC] = 1.0
    for dd in range(1, DEEP + 1):
        ya = np.zeros(NL)
        np.add.at(ya, ld2, va2 * xa[ls2])
        xa = ya
        _p = _psum_null(xa)
        assert np.isfinite(_p), (_i, dd, "null FINITENESS (STOP)")
        assert _p > 0.0 or dd < D_FIRST, (_i, dd, "null POSITIVITY (STOP)")
        P_NULL[_i, dd - 1] = _p
    for dd in range(DMAX):
        assert P_NULL[_i, dd] == NP_[_i, dd], \
            (_i, dd + 1, "CERT-W50 null (STOP)")
        _nw50 += 1
log(f"[CERT-W50] GREEN {_nw50} float equalities: the depth-1..{DMAX} segment "
    f"of every extended walk (1 real + {len(null_changed)} draws) reproduces "
    f"the certified arrays exactly; extended to d={DEEP}")
o["cert_w50"] = dict(n_checks=_nw50, mode="float equality (==)",
                     deep=DEEP,
                     source="SW['carrier']['P'] and NP_ (both certified)")
_el("extended walks")

# ---- the profiles ----------------------------------------------------------
LAMK = np.array([r["lam"] for r in rows210])
KK = np.array([r["K"] for r in rows210])
UCK = np.array([r["u_car"] for r in rows210])
DS = np.arange(1, DEEP + 1)

PRED_REAL = np.array([LAM1 ** d * K_REAL for d in DS])
PRED_NULL = np.array([[LAMK[k] ** d * KK[k] for d in DS]
                      for k in range(len(rows210))])
assert np.isfinite(PRED_REAL).all() and (PRED_REAL > 0).all(), \
    "PRED_REAL finiteness (STOP)"
assert np.isfinite(PRED_NULL).all() and (PRED_NULL > 0).all(), \
    "PRED_NULL finiteness (STOP)"

# AMENDMENT A2, disclosed (after the PREREG, changes no registered quantity —
# it makes a registered quantity bit-identical to its parent's definition):
# the first build computed D_d as median(P_null)/P_real directly. L206's
# SOURCE divides BOTH by (LAM1**(d+1) * _m_car) first, and that normalisation
# — a provable NO-OP in exact arithmetic (L209) — moves the LAST BIT:
# 10.388078940332742 vs the stored 10.38807894033274. The d=10 anchor gate
# caught it. L206's own lesson, a THIRD time: a float-equality claim is a
# claim about the EXPRESSION, not just the operands. D_d is now computed with
# the source's expression, character for character.
_NRM = np.array([LAM1 ** (j + 1) * _m_car for j in range(DEEP)])
_car_n = np.array(P_REAL) / _NRM
_null_n = P_NULL / _NRM[None, :]
D_PROF = np.array([float(np.median(_null_n[:, j]) / _car_n[j])
                   if j >= D_FIRST - 1 else np.nan for j in range(DEEP)])
R_ASYM = np.array([float(np.median(PRED_NULL[:, j])) / PRED_REAL[j]
                   for j in range(DEEP)])
C_PROF = D_PROF / R_ASYM
C_CAR = np.array(P_REAL) / PRED_REAL
C_NULLK = P_NULL / PRED_NULL
_J = slice(D_FIRST - 1, DEEP)     # the registered read range (A1)
assert np.isfinite(D_PROF[_J]).all() and (D_PROF[_J] > 0).all() \
    and np.isfinite(R_ASYM).all() and np.isfinite(C_PROF[_J]).all() \
    and np.isfinite(C_CAR).all() and (C_CAR[_J] > 0).all(), \
    "profile FINITENESS (STOP)"
assert np.isfinite(C_NULLK[:, _J]).all() and (C_NULLK[:, _J] > 0).all(), \
    "per-draw correction FINITENESS (STOP)"

# the depth-10 anchors must reproduce L210/L206 exactly
assert D_PROF[DMAX - 1] == D10, (D_PROF[DMAX - 1], D10, "D10 anchor (STOP)")
assert R_ASYM[DMAX - 1] == o["Q210_1_primary"]["R_asym"], \
    (R_ASYM[DMAX - 1], "R_asym(10) anchor (STOP)")
assert C_CAR[DMAX - 1] == o["Q210_3_ceiling"]["C_real"], \
    (C_CAR[DMAX - 1], "C_real anchor (STOP)")
log(f"[anchors] GREEN D_prof(10)==D10, R_asym(10)==L210 R_asym, "
    f"C_car(10)==L210 C_real -- the extension is continuous with the parent")

K_RATIO_MED = float(np.median(KK)) / K_REAL
LAMPOW50 = float(np.median(LAMK) ** DEEP / LAM1 ** DEEP)

# ---------------- NO-OP re-measurement (L209's law, MEASURED) ---------------
# A global rescale of the operator cannot move a same-depth mass RATIO.
# Measured in full on the real walk at all 50 depths and on 5 draws; the
# remaining step (a positive scalar commutes with the median over draws) is
# arithmetic and is DISCLOSED as such.
_S = 3.7
_xs = np.zeros(NL)
_xs[LC] = 1.0
_Ps = []
for _d in range(1, DEEP + 1):
    _xs = jmatvec(_xs, _S * jv_abs_an, csr_cols, csr_rows)
    _Ps.append(_psum_sweep(_xs))
_lam1s, _v1s, _lis = pi_dir(_S * jv_abs_an, csr_cols, csr_rows)
_lam1Ls, _u1s, _lils = pi_dir(_S * jv_abs_an, csr_rows, csr_cols)
_Ks = coeff(_u1s, _v1s, LC)
_noop = max(abs(np.array(_Ps)[j] / (_lam1s ** DS[j] * _Ks) - C_CAR[j])
            / abs(C_CAR[j]) for j in range(D_FIRST - 1, DEEP))
_noop_k = 0.0
for _i in range(5):
    ls2, ld2, va2 = REB[_i]
    xa = np.zeros(NL)
    xa[LC] = 1.0
    _Pk = []
    for dd in range(1, DEEP + 1):
        ya = np.zeros(NL)
        np.add.at(ya, ld2, (_S * va2) * xa[ls2])
        xa = ya
        _Pk.append(_psum_null(xa))
    _lk, _vk, _ = pi_dir(_S * va2, ls2, ld2)
    _lkL, _uk, _ = pi_dir(_S * va2, ld2, ls2)
    _Kk = float(_uk[LC]) * float(_vk[POOL_IDX].sum()) / float(_uk @ _vk)
    for j in range(D_FIRST - 1, DEEP):
        _noop_k = max(_noop_k, abs(_Pk[j] / (_lk ** DS[j] * _Kk)
                                   - C_NULLK[_i, j]) / abs(C_NULLK[_i, j]))
assert _noop < 1e-10 and _noop_k < 1e-10, (_noop, _noop_k, "NO-OP (STOP)")
log(f"[NO-OP] GREEN max rel move under a global x{_S} rescale: real "
    f"{_noop:.2e} over {DEEP} depths, draws {_noop_k:.2e} over 5x{DEEP}")
o["noop"] = dict(scale=_S, max_rel_real=_noop, max_rel_draws_5=_noop_k,
                 depths=DEEP,
                 note=("the median over draws of a set all multiplied by the "
                       "same positive scalar is that scalar times the median "
                       "-- the only step not re-measured here"))
_el("NO-OP")

# ---------------- Q218-1 (PRIMARY) ------------------------------------------
_fin = bool(np.isfinite(P_NULL).all() and (P_NULL[:, _J] > 0).all()
            and np.isfinite(D_PROF[_J]).all() and (D_PROF[_J] > 0).all()
            and np.isfinite(PRED_NULL).all())
C50 = float(C_PROF[DEEP - 1])
_plateau = float(max(abs(C_PROF[j] - C50) / abs(C50) for j in range(39, DEEP)))
if not _fin:
    BRANCH1 = "OVERFLOW_DEGENERATE"
elif abs(C50 - 1.0) <= 0.01:
    BRANCH1 = "CF_EXACT"
elif _plateau <= 0.005:
    BRANCH1 = "CF_PLATEAU_OTHER"
else:
    BRANCH1 = "NO_PLATEAU"
log(f"[Q218-1] {BRANCH1} | D_50 {D_PROF[-1]:.5f} | R_asym(50) "
    f"{R_ASYM[-1]:.5f} | C_prof(50) {C50:.6f} | plateau spread d40-50 "
    f"{_plateau:.2e} | K_ratio_med {K_RATIO_MED:.5f} | lam-power factor "
    f"{LAMPOW50:.6f} | C_car(50) {C_CAR[-1]:.6f}")
o["Q218_1_primary"] = dict(
    branch=BRANCH1, deep=DEEP,
    D_50=float(D_PROF[-1]), R_asym_50=float(R_ASYM[-1]), C_prof_50=C50,
    bar=0.01, plateau_spread_d40_50=_plateau, plateau_bar=0.005,
    D_10=float(D_PROF[DMAX - 1]), R_asym_10=float(R_ASYM[DMAX - 1]),
    C_prof_10=float(C_PROF[DMAX - 1]),
    K_ratio_med=K_RATIO_MED,
    D50_over_K_ratio_med=float(D_PROF[-1]) / K_RATIO_MED,
    lam_power_factor_50=LAMPOW50,
    C_car_50=float(C_CAR[-1]), C_car_10=float(C_CAR[DMAX - 1]),
    C_null_med_50=float(np.median(C_NULLK[:, -1])),
    C_null_med_10=float(np.median(C_NULLK[:, DMAX - 1])),
    finite=_fin,
    note=("R_asym(50) is the PRIMARY form (registered 0a); K_ratio_med is the "
          "card's literal depth-free wording and differs by the lam-power "
          "factor"))
o["profile"] = dict(
    depths=[int(d) for d in DS],
    d_first_read=D_FIRST,
    P_real_d1_structural_zero=float(P_REAL[0]),
    D=[None if j < D_FIRST - 1 else float(D_PROF[j]) for j in range(DEEP)],
    R_asym=[float(v) for v in R_ASYM],
    C_prof=[None if j < D_FIRST - 1 else float(C_PROF[j])
            for j in range(DEEP)],
    C_car=[float(v) for v in C_CAR],
    C_null_med=[float(np.median(C_NULLK[:, j])) for j in range(DEEP)],
    P_real=[float(v) for v in P_REAL],
    P_null_med=[float(np.median(P_NULL[:, j])) for j in range(DEEP)])

# ---------------- Q218-2: the RATE of the correction ------------------------
_e = C_CAR - 1.0
_sgn = np.sign(_e[14:DEEP])
_alt = bool(np.any(_sgn[:-1] * _sgn[1:] < 0))
_rat = [float(_e[j + 1] / _e[j]) for j in range(19, 45) if _e[j] != 0.0]
_rat_med = float(np.median(_rat)) if _rat else float("nan")
_rat_lo, _rat_hi = (float(min(_rat)), float(max(_rat))) if _rat else (
    float("nan"), float("nan"))
if _alt:
    BRANCH2 = "RATE_ALTERNATING"
elif abs(_rat_med - GAP) <= 0.02:
    BRANCH2 = "RATE_SPECTRAL"
else:
    BRANCH2 = "RATE_OTHER"
# the same rate read on the DRAWS, as a population (unregistered, descriptive)
_rat_k = []
for k in range(len(rows210)):
    ek = C_NULLK[k] - 1.0
    rk = [float(ek[j + 1] / ek[j]) for j in range(19, 45) if ek[j] != 0.0]
    if rk:
        _rat_k.append(float(np.median(rk)))
log(f"[Q218-2] {BRANCH2} | per-hop ratio of (C_car-1) over d20-45: median "
    f"{_rat_med:.6f} [{_rat_lo:.6f}, {_rat_hi:.6f}] vs certified gap "
    f"{GAP:.6f} (|diff| {abs(_rat_med - GAP):.2e}) | sign alternation "
    f"{_alt} | draw-median rate {float(np.median(_rat_k)):.6f}")
o["Q218_2_rate"] = dict(
    branch=BRANCH2, rate_median_d20_45=_rat_med, rate_min=_rat_lo,
    rate_max=_rat_hi, gap_certified=GAP, abs_diff=abs(_rat_med - GAP),
    bar_abs=0.02, sign_alternates_d15_50=_alt,
    e_d10=float(_e[DMAX - 1]), e_d50=float(_e[-1]),
    draw_rate_median=float(np.median(_rat_k)),
    draw_rate_p05=float(np.percentile(_rat_k, 5)),
    draw_rate_p95=float(np.percentile(_rat_k, 95)),
    note=("needs NO eigenvector, so it survives an unresolved deflation and "
          "is the registered fallback carrier of the card's second question"))
_el("Q218-1 + Q218-2")


# ---------------- CERT-DEFLV: a vector-returning deflation, gated -----------
def defl_pair(jv, ls, ld, v1, u1, iters=400, seed=21004):
    """IDENTICAL arithmetic to the certified lam2_defl; returns the iterate as
    well. Admitted ONLY by exact float equality with lam2_defl (CERT-MV
    pattern: a new kernel is gated by exact agreement with the certified
    one)."""
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
            return 0.0, x, dict(rel_spread_last6=0.0, last6=[], converged=True)
        x = y / nrm
        if i >= iters - 6:
            hist.append(nrm)
    sp = float((max(hist) - min(hist)) / max(hist))
    return float(np.median(hist)), x, dict(rel_spread_last6=sp, last6=hist,
                                           converged=bool(sp < 1e-6))


def defl_resid(jv, ls, ld, v1, u1, x):
    """L217's law: diagnose an eigenpair with its RESIDUAL. Returns the SIGNED
    eigenvalue estimate (Rayleigh quotient on the deflated operator) and the
    relative residual ||Bx - lam x|| / ||Bx||."""
    uv = float(u1 @ v1)
    y = mv(x, jv, ls, ld)
    y = y - v1 * float(u1 @ y) / uv
    lam_fit = float(x @ y) / float(x @ x)
    r = y - lam_fit * x
    ny = float(np.linalg.norm(y))
    return lam_fit, (float(np.linalg.norm(r)) / ny if ny else float("inf"))


_ndv = 0
_a, _ia = lam2_defl(jv_abs_an, csr_cols, csr_rows, V1, U1)
_b, _xb, _ib = defl_pair(jv_abs_an, csr_cols, csr_rows, V1, U1)
assert _a == _b, (_a, _b, "CERT-DEFLV lam (STOP)")
_leafcmp(_ib, _ia, "CERT-DEFLV info")
_ndv += 1
assert _a == LAM2, (_a, LAM2, "CERT-DEFLV vs the parent's LAM2 (STOP)")
for _i in (0, 1, 2):
    ls2, ld2, va2 = REB[_i]
    _lk, _vk, _ = pi_dir(va2, ls2, ld2)
    _lkL, _uk, _ = pi_dir(va2, ld2, ls2)
    _c, _ic = lam2_defl(va2, ls2, ld2, _vk, _uk)
    _d2, _xd, _id = defl_pair(va2, ls2, ld2, _vk, _uk)
    assert _c == _d2, (_i, _c, _d2, "CERT-DEFLV draw lam (STOP)")
    _leafcmp(_id, _ic, f"CERT-DEFLV draw{_i} info")
    _ndv += 1
log(f"[CERT-DEFLV] GREEN {_ndv} deflations (real + 3 probe draws) agree with "
    f"the certified lam2_defl at EXACT float equality on the eigenvalue and "
    f"every convergence field; real |lam2| {_a:.6f} == parent LAM2")
o["cert_deflv"] = dict(n_pairs=_ndv, mode="exact float equality (==)",
                       source="the certified lam2_defl (l210_tail.py 290-308)")
_el("CERT-DEFLV")

# ---------------- Q218-3: the subdominant overlap ---------------------------
# K2(c) = u2[c] * S_v2 / (u2 . v2): the exact subdominant analogue of K, and
# like K it is INVARIANT to the (arbitrary) sign and scale of BOTH u2 and v2.
L2R, V2, INF2R = defl_pair(jv_abs_an, csr_cols, csr_rows, V1, U1)
L2L, U2, INF2L = defl_pair(jv_abs_an, csr_rows, csr_cols, U1, V1)
_lfR, _resR = defl_resid(jv_abs_an, csr_cols, csr_rows, V1, U1, V2)
_lfL, _resL = defl_resid(jv_abs_an, csr_rows, csr_cols, U1, V1, U2)
RES_BAR = 1e-3
_res_ok_real = bool(_resR <= RES_BAR and _resL <= RES_BAR)
K2_REAL = float(U2[LC]) * float(V2[POOL_IDX].sum()) / float(U2 @ V2)
A2_REAL = K2_REAL / K_REAL
log(f"[Q218-3 real] |lam2| R {L2R:.6f} / L {L2L:.6f} | signed Rayleigh "
    f"{_lfR:+.6f} / {_lfL:+.6f} | residual {_resR:.3e} / {_resL:.3e} "
    f"(bar {RES_BAR:.0e}, resolved {_res_ok_real}) | K2 {K2_REAL:.6e} | "
    f"A2 = K2/K {A2_REAL:+.6f} | u2[carrier] {float(U2[LC]):+.6e}")

A2K, U2K, RESK, LFK = [], [], [], []
for k in range(len(rows210)):
    ls2, ld2, va2 = REB[k]
    _lk, _vk, _ = pi_dir(va2, ls2, ld2)
    _lkL, _uk, _ = pi_dir(va2, ld2, ls2)
    _l2r, _v2, _ = defl_pair(va2, ls2, ld2, _vk, _uk)
    _l2l, _u2, _ = defl_pair(va2, ld2, ls2, _uk, _vk)
    _f1, _r1 = defl_resid(va2, ls2, ld2, _vk, _uk, _v2)
    _f2, _r2 = defl_resid(va2, ld2, ls2, _uk, _vk, _u2)
    _k2 = float(_u2[LC]) * float(_v2[POOL_IDX].sum()) / float(_u2 @ _v2)
    A2K.append(_k2 / KK[k])
    U2K.append(float(_u2[LC]))
    RESK.append(max(_r1, _r2))
    LFK.append((_f1, _f2))
    # the per-draw Perron pair must reproduce the certified per-draw scalars
    assert _lk == rows210[k]["lam"], (k, "per-draw lam drift (STOP)")
A2K = np.array(A2K)
U2K = np.array(U2K)
RESK = np.array(RESK)
_nres_ok = int((RESK <= RES_BAR).sum())
_pct_A2 = float((A2K < A2_REAL).mean())
_pct_u2 = float((np.abs(U2K) < abs(float(U2[LC]))).mean())
_med_A2 = float(np.median(A2K))
_direction_only = bool(abs(A2_REAL - _med_A2) < 0.05)
if not _res_ok_real:
    BRANCH3 = "U2_UNRESOLVED"
elif _pct_A2 >= 0.95:
    BRANCH3 = "U2_HIGH"
elif _pct_A2 <= 0.05:
    BRANCH3 = "U2_LOW"
else:
    BRANCH3 = "U2_NULL"
log(f"[Q218-3] {BRANCH3} | A2_real {A2_REAL:+.6f} vs draw median "
    f"{_med_A2:+.6f} [p05 {float(np.percentile(A2K, 5)):+.6f}, p95 "
    f"{float(np.percentile(A2K, 95)):+.6f}] pct {_pct_A2:.3f} | "
    f"|A2-med| {abs(A2_REAL - _med_A2):.4f} -> DIRECTIONAL_ONLY "
    f"{_direction_only} | u2[car] pct {_pct_u2:.3f} | draws resolved "
    f"{_nres_ok}/{len(RESK)} (max residual {float(RESK.max()):.2e})")
# the closed-form check the card asked for: C_car(d) - 1 == A2 * gap^d ?
_A2_implied = float(_e[DMAX - 1]) / (GAP ** DMAX)
_pred_e = np.array([A2_REAL * (GAP ** d) for d in DS])
_cf_relerr = [abs(_pred_e[j] - _e[j]) / abs(_e[j]) for j in range(9, DEEP)]
o["Q218_3_u2"] = dict(
    branch=BRANCH3, A2_real=A2_REAL, K2_real=K2_REAL, K_real=K_REAL,
    u2_carrier_real=float(U2[LC]),
    A2_draw_med=_med_A2, A2_p05=float(np.percentile(A2K, 5)),
    A2_p95=float(np.percentile(A2K, 95)), A2_percentile=_pct_A2,
    abs_gap_to_median=abs(A2_REAL - _med_A2),
    directional_only=_direction_only, direction_bar=0.05,
    u2_carrier_percentile_absval=_pct_u2,
    u2_draw_med_absval=float(np.median(np.abs(U2K))),
    residual_real_right=_resR, residual_real_left=_resL,
    residual_bar=RES_BAR, resolved_real=_res_ok_real,
    draws_resolved=_nres_ok, draws_total=int(len(RESK)),
    residual_draw_max=float(RESK.max()),
    residual_draw_med=float(np.median(RESK)),
    lam2_signed_rayleigh_right=_lfR, lam2_signed_rayleigh_left=_lfL,
    lam2_abs_right=L2R, lam2_abs_left=L2L,
    A2_implied_by_d10_anchor=_A2_implied,
    A2_direct_over_implied=A2_REAL / _A2_implied if _A2_implied else None,
    closed_form_max_relerr_d10_50=float(max(_cf_relerr)),
    closed_form_relerr_d50=float(_cf_relerr[-1]),
    disclosure=("unit-L2 normalisation of u2 on two DIFFERENT operators is a "
                "CONVENTION, not a canonical comparison (L210 Q210-2); A2 = "
                "K2/K is the scaling- AND sign-invariant form and carries the "
                "branch"))
_el("Q218-3")

# ---------------- predictions ------------------------------------------------
o["predictions"] = dict(
    P1=dict(registered="Q218-1 branch == CF_EXACT", measured=BRANCH1,
            correct=bool(BRANCH1 == "CF_EXACT")),
    P2=dict(registered="D_50 in [11.2, 11.6] and D_50 > D10",
            measured=float(D_PROF[-1]),
            correct=bool(11.2 <= float(D_PROF[-1]) <= 11.6
                         and float(D_PROF[-1]) > D10)),
    P3=dict(registered="Q218-2 branch == RATE_SPECTRAL (not ALTERNATING)",
            measured=BRANCH2, correct=bool(BRANCH2 == "RATE_SPECTRAL")),
    P4=dict(registered="Q218-3 branch == U2_HIGH", measured=BRANCH3,
            correct=bool(BRANCH3 == "U2_HIGH")),
    P5=dict(registered="direct A2 in [0.315, 1.26] (within 2x of the d10 "
                       "anchor's implied 0.630)",
            measured=A2_REAL,
            correct=bool(0.315 <= A2_REAL <= 1.26)))
_npred = sum(1 for v in o["predictions"].values() if v["correct"])
log(f"[PREDICTIONS] {_npred} of {len(o['predictions'])} correct: "
    + " ".join(f"{k}={'Y' if v['correct'] else 'N'}"
               for k, v in o["predictions"].items()))

o["amendments"] = [
    dict(id="A1", when="after the PREREG, before any L218 number was read",
         what=("the PREREG's OVERFLOW_DEGENERATE guard says 'any P_d ... "
               "zero'. It fired at d=1, where P_1 == 0 is not degeneracy but "
               "a STRUCTURAL anatomical fact: the carrier's 69 out-edges "
               "reach NO pool cell directly. L206 already records this (its "
               "deficit_ratio_by_depth[0] is None, by the same cut). The "
               "guard is scoped to the depths the registered statistics are "
               "READ at -- d >= 2 for D_d / C_prof, exactly L206's own "
               "reporting range -- and d=1 is RECORDED, never used."),
         changes_a_registered_quantity=False,
         evidence="P_real[0] == 0.0 asserted as the amendment's own premise"),
    dict(id="A2", when="after the PREREG, caught by the d=10 anchor gate",
         what=("D_d was first computed as median(P_null)/P_real. L206's "
               "SOURCE divides BOTH by (LAM1**(d+1) * m_out_carrier) first — "
               "a provable NO-OP in exact arithmetic (L209) that moves the "
               "LAST BIT: 10.388078940332742 vs the stored "
               "10.38807894033274. D_d now uses the source's expression "
               "character for character. L206's law a third time: a "
               "float-equality claim is a claim about the EXPRESSION."),
         changes_a_registered_quantity=False,
         evidence="D_PROF[9] == D10 at float equality (halting)"),
]
o["limitations"] = [
    "one substrate (f4wA), one operator (|g W_beta|), one null family (the "
    "l169c destination swaps); L207's cross-null law stands",
    "a closed form is not a mechanism -- the avoidance is moved to where the "
    "carrier's 69 out-edges point, which is L219/L211 and is NOT re-banked",
    "the carrier was SELECTED for being extreme on a related statistic "
    "(Kriegeskorte 2009): every carrier-specific number is a DESCRIPTION of "
    "a selected object; the 100 draws null the WIRING, not the selection",
    "depth 50 is not infinity -- a d50 verdict is a statement about d50 with "
    "a measured rate attached, never about the limit",
]

# ---------------- fingerprints unchanged + write ----------------------------
for _p in _PRIORS:
    _now = (_os.stat(_p).st_size, _os.stat(_p).st_mtime_ns)
    assert _now == _FP0[_p], (_p, _FP0[_p], _now, "prior artifact MUTATED")
log(f"[priors] GREEN {len(_PRIORS)} prior artifacts unchanged "
    f"(size, mtime_ns) across the run")
o["priors_readonly"] = {p: list(_FP0[p]) for p in _PRIORS}
o["rows_per_draw_recomputed"] = rows210
_el("total")

import os
os.makedirs("l218", exist_ok=True)
with open("l218/static.json", "x") as f:
    json.dump(o, f, indent=1, default=float)
log("[done] wrote l218/static.json")
