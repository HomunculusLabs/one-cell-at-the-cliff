# ================= L224 TAIL (appended by l224_build.py) =================
# Everything above this line is VERBATIM source:
#   l151_static.py 1-319, l178_tail.py 7-149, l206_mid.py,
#   l206_tail.py 22-121, l207_tail.py 48-112, l207_tail.py 199-241,
#   l213_tail.py 1-430  (L213's WHOLE pipeline with its runtime stamp and
#                        its writer CUT -- the L213 slicing pattern).
# So CERT-F4, the three stored gains, the CSR orientation, all 20 pool sizes,
# CERT-178 (420 stored anatomical values at float equality), CERT-207 (522)
# and CERT-T (272) have ALL re-run as free certification, and the L213
# population / strata / Q1 / Q2 / Q3 blocks have re-executed, before any L224
# value is read.
# PREREG: l224/PREREG.md (registered FIRST, incl. premise corrections 0a-0f).
# Writes l224/static.json ONLY. Zero rollouts, zero settles, zero dynamics.

import os

_T224 = time.time()

SEED_SPUR = 22401
SEED_BOOT = 22402
B_SPUR = 2000
B_BOOT = 2000
PRIMARY = "G0_closure"
RHO_BAR = 0.05
Q3_BAR = 0.05
K_LO, K_HI = 0.5, 3.0
EXCL_BAR = 0.05

q = {}
q["design"] = (
    "L224 the MASS-NEUTRAL statistic. L213's addendum measured "
    "Spearman(R, m_out) = +.53 INSIDE a statistic explicitly divided by "
    "m_out. Here P2 ~ m_out^k is fitted over the present-descending "
    "population on the three L207/L213 BANC substrates (OLS primary, "
    "Theil-Sen, RMA-as-identity, plus the bisected neutralising exponent), "
    "R_k = P2/(lam1^2*m_out^k) is formed, and the residual rank "
    "correlation is read AGAINST ITS COMPONENT-SHUFFLED SPURIOUS BASELINE "
    "(Pearson 1897; Jackson & Somers 1991) rather than against zero. "
    "PREREG l224/PREREG.md.")
q["prereg"] = "l224/PREREG.md"
q["parents"] = ["l213/static.json", "l213/addendum.json"]
q["seeds"] = dict(spurious=SEED_SPUR, bootstrap=SEED_BOOT,
                  b_spurious=B_SPUR, b_bootstrap=B_BOOT)
q["primary_substrate"] = PRIMARY
q["bars"] = dict(rho_bar=RHO_BAR, q3_bar=Q3_BAR, k_lo=K_LO, k_hi=K_HI,
                 excl_bar=EXCL_BAR)

# =====================================================================
# CERT-213 (HALTING): every stored leaf of l213/static.json except
# runtime_s, reproduced at float/int/str equality by the re-executed
# pipeline above.  Premise correction 0a: the artifact does NOT store the
# population R vector, so this -- plus CERT-ADD -- is what pins it.
# =====================================================================
_P213 = "l213/static.json"
_P213A = "l213/addendum.json"
_st213 = os.stat(_P213)
_fp213 = (_st213.st_size, _st213.st_mtime_ns)
with open(_P213) as _fh:
    S213 = json.load(_fh)
_st213a = os.stat(_P213A)
_fp213a = (_st213a.st_size, _st213a.st_mtime_ns)
with open(_P213A) as _fh:
    A213 = json.load(_fh)

_n213 = 0


def _leafcmp(stored, live, path):
    """recursive leaf compare at float/int/str equality (HALTING)."""
    global _n213
    if isinstance(stored, dict):
        assert isinstance(live, dict), (path, "live is not a dict")
        assert set(stored) == set(live), (path, sorted(set(stored) ^ set(live)))
        for _k in stored:
            _leafcmp(stored[_k], live[_k], path + "/" + str(_k))
        return
    if isinstance(stored, list):
        assert isinstance(live, (list, tuple)), (path, "live is not a list")
        assert len(stored) == len(live), (path, len(stored), len(live))
        for _i, (_a, _b) in enumerate(zip(stored, live)):
            _leafcmp(_a, _b, path + f"[{_i}]")
        return
    if isinstance(stored, bool) or isinstance(live, bool):
        assert bool(stored) == bool(live), (path, stored, live)
    elif isinstance(stored, (int, float)) and not isinstance(stored, bool):
        assert float(stored) == float(live), (path, stored, live, "CERT-213")
    else:
        assert stored == live, (path, stored, live, "CERT-213")
    _n213 += 1


assert "runtime_s" in S213, "l213/static.json lost runtime_s"
for _key in S213:
    if _key == "runtime_s":
        continue
    assert _key in o, (_key, "re-executed L213 pipeline lost a key (STOP)")
    _leafcmp(S213[_key], o[_key], "/" + _key)
assert set(S213) - {"runtime_s"} == set(o) - {"runtime_s"}, \
    (sorted(set(S213) ^ set(o)), "key set drift (STOP)")
assert S213["branches"]["Q1"] == "T_TYPE_LOW", "L213 Q1 branch moved"
assert S213["branches"]["Q3"] == "D_CLASS_EXPLAINS", "L213 Q3 branch moved"


# the coverage bar is DERIVED FROM THE ARTIFACT ITSELF, never guessed in
# advance (L216's law, in a counting currency): count the stored leaves and
# require the comparator to have visited exactly that many.  A fixed
# magnitude bar is a guess about someone else's file; this is a proof that
# every stored leaf was compared.
def _nleaves(x):
    if isinstance(x, dict):
        return sum(_nleaves(v) for v in x.values())
    if isinstance(x, list):
        return sum(_nleaves(v) for v in x)
    return 1


_want213 = sum(_nleaves(S213[_k]) for _k in S213 if _k != "runtime_s")
assert _n213 == _want213, (_n213, _want213, "CERT-213 coverage (STOP)")
assert _n213 > 0, "CERT-213 compared nothing"
log(f"[CERT-213] GREEN {_n213} stored l213 leaves reproduced at "
    f"float/int/str equality BEFORE any L224 number was read")
q["cert_213"] = dict(n_checks=_n213, mode="float/int/str equality (==)",
                     source="l213/static.json (read-only, fingerprinted)",
                     excluded=["runtime_s"])

# =====================================================================
# CERT-ADD (HALTING): the addendum's three stored rho_R_vs_mout_population
# through the addendum's OWN expression, plus its within-class raw and
# mass-matched percentiles through ITS own expressions.
# =====================================================================
_nadd = 0
MM = {}
for _k, _p in POP.items():
    _R, _pu, _gis, _m = _p["R"], _p["pure"], _p["gis"], _p["m_out"]
    _rho = spearman_l([float(x) for x in _R], [float(x) for x in _m])
    assert _rho == A213["per_substrate"][_k]["rho_R_vs_mout_population"], \
        (_k, _rho, "CERT-ADD rho (STOP)")
    _nadd += 1
    assert spearman_l([float(x) for x in _R[_pu]],
                      [float(x) for x in _m[_pu]]) == \
        A213["per_substrate"][_k]["rho_R_vs_mout_pure"], (_k, "CERT-ADD pure")
    _nadd += 1
    assert spearman_l([float(x) for x in _R[~_pu]],
                      [float(x) for x in _m[~_pu]]) == \
        A213["per_substrate"][_k]["rho_R_vs_mout_nonpure"], (_k, "CERT-ADD np")
    _nadd += 1
    MM[_k] = {}
    for _nm, _gi, _cls in (("carrier", GI_CARRIER, _pu),
                           ("mirror", GI_MIR, ~_pu)):
        _row = A213["per_substrate"][_k][_nm]
        _i = _gis.index(_gi)
        _ci = np.where(_cls)[0]
        _rpct = float((_R[_ci] < _R[_i]).sum() / len(_ci))
        assert _rpct == _row["R_pct_in_class_raw"], (_k, _nm, "CERT-ADD raw")
        _nadd += 1
        _oth = _ci[_ci != _i]
        _d = np.abs(np.log(_m[_oth]) - math.log(float(_m[_i])))
        _sel = _oth[np.argsort(_d, kind="stable")[:100]]
        assert len(_sel) == 100, (_k, _nm, "class cohort short")
        _mmpct = float((_R[_sel] < _R[_i]).sum() / len(_sel))
        assert _mmpct == _row["R_pct_in_class_massmatched"], \
            (_k, _nm, _mmpct, "CERT-ADD massmatched (STOP)")
        _nadd += 1
        assert float(_R[_i]) == _row["R"] and float(_m[_i]) == _row["m_out"]
        _nadd += 2
        MM[_k][_nm] = dict(i=int(_i), ci=_ci, sel=_sel,
                           pct_mm_R=_mmpct, pct_cls_R=_rpct)
log(f"[CERT-ADD] GREEN {_nadd} checks: l213/addendum.json's population rho, "
    f"within-class raw and mass-matched percentiles at FLOAT equality")
q["cert_add"] = dict(n_checks=_nadd, mode="float equality (==)",
                     source="l213/addendum.json (read-only, fingerprinted)")

# =====================================================================
# CERT-RANK (HALTING): the inherited rankvec PROVEN an average-rank
# (midrank) estimator on THIS data before any rank statistic is read.
# tick 252's law converted from a remembered lesson into a gate.
# =====================================================================
_nrank = 0
for _k, _p in POP.items():
    for _nmv, _v in (("R", _p["R"]), ("m_out", _p["m_out"])):
        _a = [float(x) for x in _v]
        _r = rankvec(_a)
        _n = len(_a)
        assert abs(sum(_r) - _n * (_n + 1) / 2.0) < 1e-6, \
            (_k, _nmv, "rank sum != n(n+1)/2 (STOP)")
        _nrank += 1
        _byval = {}
        for _x, _rr in zip(_a, _r):
            _byval.setdefault(_x, set()).add(_rr)
        for _x, _s in _byval.items():
            assert len(_s) == 1, (_k, _nmv, _x, "tie group split (STOP)")
        assert len(_byval) == len(set(_r)), \
            (_k, _nmv, "distinct values != distinct ranks (STOP)")
        _nrank += 2
log(f"[CERT-RANK] GREEN {_nrank} checks: rankvec is a midrank estimator on "
    f"all six population vectors (tie groups unsplit, rank sum exact)")
q["cert_rank"] = dict(n_checks=_nrank,
                      note="tick 252 law as a GATE: argsort-of-argsort would "
                           "fail the tie-group check")

# =====================================================================
# CERT-K1 (HALTING): R_k at k=1 is BIT-identical to L213's R (0b).
# =====================================================================
LC = {}
P2V = {}
_nk1 = 0
for _k, _s in SUBS.items():
    _gis = POP[_k]["gis"]
    _lc = np.array([int(_s["loc"][g]) for g in _gis])
    LC[_k] = _lc
    _v = CENS[_k][1]
    P2V[_k] = _v[_lc]
    _m = POP[_k]["m_out"]
    _Rk1 = P2V[_k] / (LAM[_k] ** 2 * _m ** 1.0)
    assert np.array_equal(_Rk1, POP[_k]["R"]), (_k, "CERT-K1 (STOP)")
    _nk1 += 1
    assert np.all(_m > 0) and np.all(np.isfinite(P2V[_k]))
    _nk1 += 1
log(f"[CERT-K1] GREEN {_nk1} checks: R_k(k=1) array-equal to the inherited R "
    f"on all three substrates (x**1.0 is a float no-op here)")
q["cert_k1"] = dict(n_checks=_nk1, mode="np.array_equal")


# =====================================================================
# CERT-FAST: numpy midrank kernel admitted ONLY by exact array equality
# against rankvec; numpy Spearman within 1e-12 relative of spearman_l
# (summation order differs -> float equality deliberately NOT claimed).
# =====================================================================
def _rank_np(a):
    a = np.asarray(a, dtype=float)
    n = a.size
    order = np.argsort(a, kind="stable")
    sa = a[order]
    new = np.empty(n, dtype=bool)
    new[0] = True
    new[1:] = sa[1:] != sa[:-1]
    gid = np.cumsum(new) - 1
    starts = np.flatnonzero(new)
    ends = np.append(starts[1:], n) - 1
    avg = (starts + ends) / 2.0 + 1.0
    r = np.empty(n)
    r[order] = avg[gid]
    return r


def _spear_np(a, b):
    ra, rb = _rank_np(a), _rank_np(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    return float((ra * rb).sum()
                 / (math.sqrt((ra * ra).sum()) * math.sqrt((rb * rb).sum())))


_nfast = 0
_maxrelf = 0.0
for _k, _p in POP.items():
    _m = _p["m_out"]
    _lg = np.log(_m)
    _lp = np.log(np.maximum(P2V[_k], 1e-300))
    for _nmv, _v in (("R", _p["R"]), ("m_out", _m), ("logm", _lg),
                     ("logp_floored", _lp)):
        assert np.array_equal(_rank_np(_v),
                              np.array(rankvec([float(x) for x in _v]))), \
            (_k, _nmv, "CERT-FAST rank (STOP)")
        _nfast += 1
    _r1 = spearman_l([float(x) for x in _p["R"]], [float(x) for x in _m])
    _r2 = _spear_np(_p["R"], _m)
    _rel = abs(_r1 - _r2) / abs(_r1)
    assert _rel < 1e-12, (_k, _r1, _r2, "CERT-FAST spearman (STOP)")
    _maxrelf = max(_maxrelf, _rel)
    _nfast += 1
log(f"[CERT-FAST] GREEN {_nfast} checks: numpy midrank EXACTLY array-equal to "
    f"rankvec; numpy Spearman within {_maxrelf:.2e} relative")
q["cert_fast"] = dict(n_checks=_nfast, max_rel_diff=_maxrelf, bar=1e-12)

# =====================================================================
# the FIT population per substrate: P2 > 0 (log(0) exclusion, 0-leg)
# =====================================================================
FIT = {}
for _k, _p in POP.items():
    _m = _p["m_out"]
    _p2 = P2V[_k]
    _ok = _p2 > 0
    _nex = int((~_ok).sum())
    _frac = _nex / len(_p2)
    _degen = _frac > EXCL_BAR
    FIT[_k] = dict(ok=_ok, n=int(_ok.sum()), n_excluded=_nex,
                   excl_frac=_frac, fit_unmeasurable=bool(_degen),
                   logm=np.log(_m[_ok]), logp=np.log(_p2[_ok]),
                   m=_m[_ok], p2=_p2[_ok])
    log(f"[fit] {_k}: {FIT[_k]['n']} cells in the fit "
        f"({_nex} excluded for P2==0, {_frac:.4f})")
q["fit_population"] = {k: dict(n=v["n"], n_excluded=v["n_excluded"],
                               excl_frac=v["excl_frac"],
                               fit_unmeasurable=v["fit_unmeasurable"])
                       for k, v in FIT.items()}
# escape SHORT-CIRCUITS (0f)
if any(v["fit_unmeasurable"] for v in FIT.values()):
    q["branch"] = "K_DEGENERATE"
    q["degenerate_reason"] = "a substrate exceeded the P2==0 exclusion bar"
    os.makedirs("l224", exist_ok=True)
    with open("l224/static.json", "w") as _fh:
        json.dump(q, _fh, indent=1, default=float)
    log("[STOP] K_DEGENERATE by FIT-UNMEASURABLE; short-circuited")
    raise SystemExit(0)


# =====================================================================
# the rank-space residual: rank(R_k) == rank(logp - k*logm) exactly,
# because lam1^2 is a positive constant (gated at k=1 against the
# inherited rho).
# =====================================================================
def _rho_resid(k, f):
    return _spear_np(f["logp"] - k * f["logm"], f["logm"])


_nid = 0
for _k, _f in FIT.items():
    if _f["n_excluded"] == 0:
        _a = _rho_resid(1.0, _f)
        _b = _spear_np(POP[_k]["R"], POP[_k]["m_out"])
        _rel = abs(_a - _b) / abs(_b)
        assert _rel < 1e-12, (_k, _a, _b, "rank-space identity (STOP)")
        _nid += 1
log(f"[CERT-IDENT] GREEN {_nid} checks: rho(R_k,m) == rho(logp-k*logm, logm) "
    f"at k=1 to < 1e-12 (monotone reparametrisation of the same ranks)")
q["cert_ident"] = dict(n_checks=_nid, bar=1e-12)

# =====================================================================
# Q224-0 (REQUIRED FIRST LEG): the COMPONENT-SHUFFLED spurious baseline.
# Pearson 1897 / Jackson & Somers 1991: an index correlates with its own
# denominator even when the components are independent, so ZERO is the
# wrong null for rho(R, m_out).
# =====================================================================
def _spur(f, k, b, seed):
    rng = np.random.default_rng(seed)
    lp, lg = f["logp"], f["logm"]
    out = np.empty(b)
    for _i in range(b):
        out[_i] = _spear_np(rng.permutation(lp) - k * lg, lg)
    return out


Q0 = {}
for _k, _f in FIT.items():
    _meas1 = _rho_resid(1.0, _f)
    _sp1 = _spur(_f, 1.0, B_SPUR, SEED_SPUR)
    _sp0 = _spur(_f, 0.0, B_SPUR, SEED_SPUR + 1)
    Q0[_k] = dict(
        rho_measured_k1=_meas1,
        spur_k1_median=float(np.median(_sp1)),
        spur_k1_p05=float(np.quantile(_sp1, 0.05)),
        spur_k1_p95=float(np.quantile(_sp1, 0.95)),
        spur_k0_median=float(np.median(_sp0)),
        delta_k1=_meas1 - float(np.median(_sp1)),
        n_draws=B_SPUR, seed=SEED_SPUR)
    log(f"[Q0] {_k}: rho(R,m_out) {_meas1:+.4f} | SPURIOUS baseline at k=1 "
        f"median {Q0[_k]['spur_k1_median']:+.4f} "
        f"[{Q0[_k]['spur_k1_p05']:+.4f},{Q0[_k]['spur_k1_p95']:+.4f}] "
        f"-> Pearson-corrected excess {Q0[_k]['delta_k1']:+.4f} "
        f"(k=0 control {Q0[_k]['spur_k0_median']:+.4f})")
q["Q0_spurious_baseline"] = dict(
    per_substrate=Q0,
    kind="component shuffling: P2 permuted across cells, m_out held, "
         "R_sh = P2_perm/(lam1^2*m_out^k)",
    refs="Pearson 1897 Proc R Soc 60:489-498; Jackson & Somers 1991 "
         "Oecologia 86:147-151",
    note="the k=0 arm is the built-in positive control: with no denominator "
         "the shuffled index must be uncorrelated with m_out.")

# =====================================================================
# Q224-1: the exponent -- OLS (primary), Theil-Sen, RMA (identity),
# bootstrap CI, and the bisected NEUTRALISING exponent.
# =====================================================================
Q1K = {}
DEGEN = []
for _k, _f in FIT.items():
    _lg, _lp = _f["logm"], _f["logp"]
    _n = _f["n"]
    _mg, _mp = _lg.mean(), _lp.mean()
    _dg, _dp = _lg - _mg, _lp - _mp
    _vg = float((_dg * _dg).sum())
    assert _vg > 0, (_k, "log m_out has zero variance (STOP)")
    k_ols = float((_dg * _dp).sum() / _vg)
    # CERT-OLS: the OLS residual is orthogonal to the predictor
    _res = _dp - k_ols * _dg
    _ortho = float((_res * _dg).sum())
    _scale = float(math.sqrt((_res * _res).sum()) * math.sqrt(_vg))
    _orel = abs(_ortho) / max(_scale, 1e-300)
    assert _orel < 1e-10, (_k, _orel, "CERT-OLS orthogonality (STOP)")
    # Pearson r and the RMA identity
    _r = float((_dg * _dp).sum()
               / (math.sqrt(_vg) * math.sqrt(float((_dp * _dp).sum()))))
    k_rma = float(np.sign(_r) * _dp.std(ddof=1) / _dg.std(ddof=1))
    _idrel = abs(k_rma - k_ols / abs(_r)) / abs(k_rma)
    assert _idrel < 1e-12, (_k, k_rma, k_ols / abs(_r), "CERT-RMA (STOP)")
    # Theil-Sen: median pairwise slope (pairs with distinct logm only)
    _ii, _jj = np.triu_indices(_n, 1)
    _ddg = _lg[_jj] - _lg[_ii]
    _nz = _ddg != 0.0
    _n_pairs = int(_nz.sum())
    assert _n_pairs > 10 * _n, (_k, _n_pairs, "too few usable pairs (STOP)")
    k_ts = float(np.median((_lp[_jj][_nz] - _lp[_ii][_nz]) / _ddg[_nz]))
    del _ii, _jj, _ddg, _nz
    # bootstrap CI on k_ols
    _rng = np.random.default_rng(SEED_BOOT)
    _bk = np.empty(B_BOOT)
    for _b in range(B_BOOT):
        _s = _rng.integers(0, _n, _n)
        _x, _y = _lg[_s], _lp[_s]
        _x = _x - _x.mean()
        _y = _y - _y.mean()
        _bk[_b] = (_x * _y).sum() / (_x * _x).sum()
    _ci = (float(np.quantile(_bk, 0.025)), float(np.quantile(_bk, 0.975)))
    # the NEUTRALISING exponent by bisection, monotonicity GATED
    _grid = np.arange(0.0, 6.01, 0.25)
    _rg = np.array([_rho_resid(float(kk), _f) for kk in _grid])
    _mono = bool(np.all(np.diff(_rg) <= 1e-12))
    k_neut = None
    if _mono and _rg[0] > 0 > _rg[-1]:
        _lo, _hi = 0.0, 6.0
        for _ in range(60):
            _mid = 0.5 * (_lo + _hi)
            if _rho_resid(_mid, _f) > 0:
                _lo = _mid
            else:
                _hi = _mid
        k_neut = 0.5 * (_lo + _hi)
    else:
        DEGEN.append((_k, "non-monotone or unbracketed rho(k)"))
    if not (K_LO <= k_ols <= K_HI):
        DEGEN.append((_k, f"k_ols {k_ols} outside [{K_LO},{K_HI}]"))
    Q1K[_k] = dict(k_ols=k_ols, k_ts=k_ts, k_rma=k_rma, pearson_r=_r,
                   k_ols_ci95=list(_ci), k_neut=k_neut,
                   rho_monotone_in_k=_mono,
                   k_spread=float(max(k_ols, k_ts, k_rma)
                                  - min(k_ols, k_ts, k_rma)),
                   n_fit=_n, n_pairs_used=_n_pairs,
                   ortho_rel=_orel, rma_identity_rel=_idrel)
    log(f"[Q1] {_k}: k_OLS {k_ols:.4f} CI95 [{_ci[0]:.4f},{_ci[1]:.4f}] | "
        f"k_TS {k_ts:.4f} | k_RMA {k_rma:.4f} (r {_r:+.4f}) | k_NEUT "
        f"{k_neut if k_neut is None else round(k_neut, 4)} | spread "
        f"{Q1K[_k]['k_spread']:.4f}")
q["Q1_exponent"] = dict(per_substrate=Q1K,
                        estimators="OLS (primary, biases k LOW under "
                                   "predictor noise -- Forstmeier 2018), "
                                   "Theil-Sen (outlier-robust, NOT a remedy "
                                   "for predictor noise), RMA "
                                   "(errors-in-variables, gated as the "
                                   "identity k_RMA = k_OLS/|r|), and the "
                                   "bisected neutralising exponent k_NEUT")
q["cert_ols"] = dict(mode="OLS residual orthogonality, relative, < 1e-10",
                     max_rel=max(v["ortho_rel"] for v in Q1K.values()))
q["cert_rma"] = dict(mode="k_RMA == k_OLS/|r|, relative, < 1e-12",
                     max_rel=max(v["rma_identity_rel"] for v in Q1K.values()))

if DEGEN:
    q["branch"] = "K_DEGENERATE"
    q["degenerate_reason"] = [list(x) for x in DEGEN]
    q["runtime_s"] = time.time() - _T224
    os.makedirs("l224", exist_ok=True)
    with open("l224/static.json", "w") as _fh:
        json.dump(q, _fh, indent=1, default=float)
    log(f"[STOP] K_DEGENERATE: {DEGEN}; short-circuited before Q2/Q3")
    raise SystemExit(0)

# =====================================================================
# Q224-2: the residual, read BESIDE its spurious baseline at the same k.
# =====================================================================
Q2R = {}
for _k, _f in FIT.items():
    _kk = Q1K[_k]
    _row = {}
    for _nm, _kv in (("k1", 1.0), ("k_ols", _kk["k_ols"]),
                     ("k_ts", _kk["k_ts"]), ("k_rma", _kk["k_rma"]),
                     ("k_neut", _kk["k_neut"])):
        _row[f"rho_{_nm}"] = _rho_resid(float(_kv), _f)
    _spo = _spur(_f, float(_kk["k_ols"]), B_SPUR, SEED_SPUR + 2)
    _row["spur_k_ols_median"] = float(np.median(_spo))
    _row["spur_k_ols_p05"] = float(np.quantile(_spo, 0.05))
    _row["spur_k_ols_p95"] = float(np.quantile(_spo, 0.95))
    _row["delta_k_ols"] = _row["rho_k_ols"] - _row["spur_k_ols_median"]
    _row["neutral_bar_pass"] = bool(abs(_row["rho_k_ols"]) <= RHO_BAR)
    Q2R[_k] = _row
    log(f"[Q2] {_k}: rho_resid k=1 {_row['rho_k1']:+.4f} | k_OLS "
        f"{_row['rho_k_ols']:+.4f} (bar {RHO_BAR}: "
        f"{'PASS' if _row['neutral_bar_pass'] else 'FAIL'}) | k_TS "
        f"{_row['rho_k_ts']:+.4f} | k_NEUT {_row['rho_k_neut']:+.4f} | "
        f"SPURIOUS at k_OLS {_row['spur_k_ols_median']:+.4f} -> excess "
        f"{_row['delta_k_ols']:+.4f}")
q["Q2_residual"] = dict(
    per_substrate=Q2R, bar=RHO_BAR,
    note="the neutrality bar is a DESCRIPTIVE property of the "
         "reparametrisation, not a null test; the spurious baseline at the "
         "SAME exponent is what the achieved zero is read against "
         "(field amendment (a)).")

# =====================================================================
# Q224-3: does the reparametrisation replace the mass match?  The 0c 2x2.
# =====================================================================
Q3P = {}
for _k, _p in POP.items():
    _R, _m = _p["R"], _p["m_out"]
    _kst = float(Q1K[_k]["k_ols"])
    _Rk = P2V[_k] / (LAM[_k] ** 2 * _m ** _kst)
    _row = {"k_star": _kst}
    for _nm in ("carrier", "mirror"):
        _d = MM[_k][_nm]
        _i, _ci = _d["i"], _d["ci"]
        _pct_pop_R = float((_R < _R[_i]).sum() / len(_R))
        _pct_pop_Rk = float((_Rk < _Rk[_i]).sum() / len(_Rk))
        _pct_cls_Rk = float((_Rk[_ci] < _Rk[_i]).sum() / len(_ci))
        _row[_nm] = dict(
            pct_mm_R=_d["pct_mm_R"], pct_cls_R=_d["pct_cls_R"],
            pct_pop_R=_pct_pop_R, pct_pop_Rk=_pct_pop_Rk,
            pct_cls_Rk=_pct_cls_Rk,
            d_primary=abs(_pct_cls_Rk - _d["pct_mm_R"]),
            d_companion=abs(_pct_pop_Rk - _d["pct_mm_R"]))
        log(f"[Q3] {_k} {_nm}: mass-matched R {_d['pct_mm_R']:.4f} | "
            f"class R {_d['pct_cls_R']:.4f} -> class R_k "
            f"{_pct_cls_Rk:.4f} (d {_row[_nm]['d_primary']:.4f}) | pop R "
            f"{_pct_pop_R:.4f} -> pop R_k {_pct_pop_Rk:.4f} "
            f"(d {_row[_nm]['d_companion']:.4f})")
    _row["max_d_primary"] = max(_row["carrier"]["d_primary"],
                                _row["mirror"]["d_primary"])
    _row["max_d_companion"] = max(_row["carrier"]["d_companion"],
                                  _row["mirror"]["d_companion"])
    _row["primary_pass"] = bool(_row["max_d_primary"] <= Q3_BAR)
    Q3P[_k] = _row
q["Q3_transport"] = dict(
    per_substrate=Q3P, bar=Q3_BAR,
    primary="|pct_cls_Rk* - pct_mm_R| for both actors (only the STATISTIC "
            "changes; premise correction 0c)",
    companion="|pct_pop_Rk* - pct_mm_R| (the card's literal form, which "
              "moves the comparison SET and the statistic at once)",
    note="if this fails the registered conclusion is 'mass matching is "
         "irreplaceable', never 'R_k is wrong'.")

# =====================================================================
# BRANCH (read on the PRIMARY substrate) + predictions
# =====================================================================
_c1 = Q2R[PRIMARY]["neutral_bar_pass"]
_c2 = Q3P[PRIMARY]["primary_pass"]
BR = ("K_NEUTRALISES" if (_c1 and _c2)
      else "K_PARTIAL" if (_c1 or _c2) else "K_FAILS")
q["branch"] = BR
q["branch_per_substrate"] = {
    k: ("K_NEUTRALISES" if (Q2R[k]["neutral_bar_pass"]
                            and Q3P[k]["primary_pass"])
        else "K_PARTIAL" if (Q2R[k]["neutral_bar_pass"]
                             or Q3P[k]["primary_pass"]) else "K_FAILS")
    for k in POP}
q["substrates_agree"] = (len(set(q["branch_per_substrate"].values())) == 1)

_P1 = all(1.00 <= Q1K[k]["k_ols"] <= 2.00 for k in POP)
_P2 = Q0[PRIMARY]["spur_k1_median"] <= -0.30
_P3 = all(Q1K[k]["k_neut"] is not None
          and Q1K[k]["k_neut"] >= Q1K[k]["k_ols"] for k in POP)
_P4 = abs(Q2R[PRIMARY]["rho_k_ols"]) <= RHO_BAR
_P5 = BR != "K_DEGENERATE"
_P6 = Q3P[PRIMARY]["max_d_primary"] > Q3_BAR
q["predictions"] = {
    "P1_k_ols_in_1_to_2_all_substrates": dict(pred=True, got=bool(_P1),
                                              correct=bool(_P1)),
    "P2_spurious_k1_median_le_-0.30": dict(
        pred=True, got=Q0[PRIMARY]["spur_k1_median"], correct=bool(_P2)),
    "P3_k_neut_ge_k_ols_all_substrates": dict(pred=True, got=bool(_P3),
                                              correct=bool(_P3)),
    "P4_abs_rho_resid_k_ols_le_0.05": dict(
        pred=True, got=Q2R[PRIMARY]["rho_k_ols"], correct=bool(_P4)),
    "P5_branch_not_degenerate": dict(pred=True, got=BR, correct=bool(_P5)),
    "P6_Q3_primary_fails": dict(
        pred=True, got=Q3P[PRIMARY]["max_d_primary"], correct=bool(_P6)),
}
q["n_predictions_correct"] = int(sum(
    1 for v in q["predictions"].values() if v["correct"]))

q["limitations"] = [
    "A zeroed residual rho is a DESCRIPTIVE reparametrisation of the "
    "statistic, NOT a better model of the biology (the card's own caveat).",
    "One population, one depth (P2), one statistic, one weighting (log1p). "
    "No dynamics, no operating point, no rollouts (L164).",
    "The three substrates share a graph and most cells, so they are NOT "
    "three independent replications.",
    "OLS on logs biases k LOW when the predictor carries noise (Forstmeier "
    "2018); the three-estimator spread is reported AS the uncertainty and "
    "Theil-Sen does not remedy predictor noise.",
    "The spurious baseline decouples the components by permutation, which "
    "destroys any real covariance BETWEEN them: it bounds what an index "
    "gives under independence, it does not model the biology.",
    "Both actors' percentiles are DESCRIPTIONS OF A SELECTED CELL "
    "(Kriegeskorte 2009): gi 1110 entered this chain because L178 found it "
    "extreme on a related depth-2 statistic. Q1/Q2 are selection-free.",
    "This is biometry, not connectomics -- it transfers because the "
    "mathematics is about ratios, not organs (Pearson 1897).",
]
q["refs"] = ["Pearson 1897 Proc R Soc 60:489-498",
             "Jackson & Somers 1991 Oecologia 86:147-151",
             "Forstmeier 2018 bioRxiv 10.1101/298786",
             "Atchley et al 1976 Syst Zool 25:137-148",
             "Kriegeskorte et al 2009 Nat Neurosci 12:535-540"]

# read-only fingerprints asserted unchanged
_s2 = os.stat(_P213)
assert (_s2.st_size, _s2.st_mtime_ns) == _fp213, "l213/static.json MUTATED"
_s3 = os.stat(_P213A)
assert (_s3.st_size, _s3.st_mtime_ns) == _fp213a, "l213/addendum.json MUTATED"
q["readonly_fingerprints_ok"] = True

q["runtime_s"] = time.time() - _T224
os.makedirs("l224", exist_ok=True)
with open("l224/static.json", "w") as _fh:
    json.dump(q, _fh, indent=1, default=float)
log(f"[done] L224 {q['runtime_s']:.1f}s -> l224/static.json | branch {BR} | "
    f"per-substrate {q['branch_per_substrate']} | predictions "
    f"{q['n_predictions_correct']}/6")
