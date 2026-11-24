# ============== L224 ADDENDUM (appended by l224b_build.py) ==============
# This file is appended to a literal PREFIX of l224_static.py (lines 1-1428),
# which ends immediately BEFORE the parent's registered K_DEGENERATE
# short-circuit and therefore contains ZERO writes.  Every parent gate
# (CERT-178 420, CERT-207 522, CERT-T 272, CERT-213 289, CERT-ADD 33,
# CERT-RANK 18, CERT-K1 6, CERT-FAST 15) re-runs for free before anything
# here is read.
#
# DECLARED POST-HOC.  UNREGISTERED.  NO BRANCH, NO BAR, NO PREDICTION.
# It refutes nothing registered: the parent's branch K_DEGENERATE stands
# exactly as measured (excl_frac .0978 / .1013 / .1508 vs a registered .05).
#
# WHY IT EXISTS: the escape fired because log(P2) is undefined for the
# 9.8-15.1% of present descending cells whose depth-2 pool reach is EXACTLY
# ZERO, so the card's primary estimator family (log-log OLS) can only be
# computed on a subpopulation SELECTED ON ITS OWN OUTCOME.  But the
# NEUTRALISING EXPONENT is rank-based: R_k = P2/(lam1^2*m_out^k) is 0 for
# every k whenever P2 == 0, so those cells hold a tied bottom rank at every
# k and the bisection is defined on the WHOLE population with no exclusion.
# This addendum measures (A) the zero census and the direction of the
# outcome-selection bias, (B) k_NEUT on the full population vs on the
# subpopulation, (C) the card's three regression estimators on the
# outcome-selected subpopulation, labelled as such, (D) the component-
# shuffled spurious baselines, (E) the Q224-3 2x2 at the exclusion-free k*.

import os

_TB = time.time()

b = {}
b["design"] = (
    "L224 addendum: the card's log-log fit is undefined on 9.8-15.1% of its "
    "own population (P2 == 0), which is why the registered FIT-UNMEASURABLE "
    "escape fired. The RANK-BASED neutralising exponent needs no exclusion, "
    "so it is measured on the FULL population and compared against the "
    "outcome-selected regression estimators. POST-HOC, UNREGISTERED, "
    "descriptive; carries no branch.")
b["parent"] = "l224/static.json"
b["prereg"] = "l224/PREREG.md"
b["registered"] = False

# ---- CERT-224 (HALTING): the parent's stored branch-bearing values --------
_PP = "l224/static.json"
_stp = os.stat(_PP)
_fpp = (_stp.st_size, _stp.st_mtime_ns)
with open(_PP) as _fh:
    S224 = json.load(_fh)
_n224 = 0
assert S224["branch"] == "K_DEGENERATE", (S224.get("branch"), "parent branch")
_n224 += 1
assert S224["bars"]["excl_bar"] == EXCL_BAR
_n224 += 1
for _k in POP:
    _st = S224["fit_population"][_k]
    assert _st["n"] == FIT[_k]["n"] and _st["n_excluded"] == FIT[_k]["n_excluded"]
    assert float(_st["excl_frac"]) == float(FIT[_k]["excl_frac"])
    assert bool(_st["fit_unmeasurable"]) is True
    _n224 += 4
for _ck, _live in (("cert_213", _n213), ("cert_add", _nadd),
                   ("cert_rank", _nrank), ("cert_k1", _nk1),
                   ("cert_fast", _nfast)):
    assert S224[_ck]["n_checks"] == _live, (_ck, "cert count drift (STOP)")
    _n224 += 1
log(f"[CERT-224] GREEN {_n224} parent values at float/int equality BEFORE any "
    f"addendum number was read")
b["cert_224"] = dict(n_checks=_n224, mode="float/int equality (==)")


# ---- the exclusion-free rank residual ------------------------------------
def _Rk(k, kk):
    """R_k over the FULL population of substrate kk; 0 wherever P2 == 0."""
    return P2V[kk] / (LAM[kk] ** 2 * POP[kk]["m_out"] ** float(k))


def _rho_full(k, kk):
    return _spear_np(_Rk(k, kk), POP[kk]["m_out"])


# a precision gate: the zero SET must be k-invariant (no underflow ties)
_nz = 0
for _k in POP:
    _n0 = int((P2V[_k] == 0).sum())
    for _kv in (0.0, 1.0, 2.0, 4.0, 6.0):
        assert int((_Rk(_kv, _k) == 0).sum()) == _n0, \
            (_k, _kv, "R_k zero set not k-invariant (underflow) (STOP)")
        _nz += 1
    # and at k=1 the full-population rho must BE L213's published number
    _r = _rho_full(1.0, _k)
    _rel = abs(_r - A213["per_substrate"][_k]["rho_R_vs_mout_population"]) \
        / abs(_r)
    assert _rel < 1e-12, (_k, "k=1 continuity with l213/addendum (STOP)")
    _nz += 1
log(f"[CERT-ZK] GREEN {_nz} checks: the P2==0 set is k-invariant over "
    f"k in [0,6] and the k=1 full-population rho IS L213's published value")
b["cert_zk"] = dict(n_checks=_nz)

# ---- (A) the ZERO census and the bias direction -------------------------
ZC = {}
for _k, _p in POP.items():
    _m, _p2 = _p["m_out"], P2V[_k]
    _z = _p2 == 0
    _mz, _mn = _m[_z], _m[~_z]
    ZC[_k] = dict(
        n=int(len(_m)), n_zero=int(_z.sum()), frac_zero=float(_z.mean()),
        median_mout_zero=float(np.median(_mz)),
        median_mout_nonzero=float(np.median(_mn)),
        ratio_median_mout=float(np.median(_mn) / np.median(_mz)),
        max_mout_zero=float(_mz.max()),
        mass_pct_of_zeros=float(np.mean([
            (_m < v).mean() for v in _mz])),
        rho_indicator_mout=_spear_np((~_z).astype(float), _m),
        zero_frac_pure=float(_z[_p["pure"]].mean()),
        zero_frac_nonpure=float(_z[~_p["pure"]].mean()))
    log(f"[A] {_k}: {ZC[_k]['n_zero']}/{ZC[_k]['n']} cells with P2==0 "
        f"({ZC[_k]['frac_zero']:.4f}) | median m_out zero "
        f"{ZC[_k]['median_mout_zero']:.2f} vs nonzero "
        f"{ZC[_k]['median_mout_nonzero']:.2f} "
        f"({ZC[_k]['ratio_median_mout']:.2f}x) | rho(P2>0, m_out) "
        f"{ZC[_k]['rho_indicator_mout']:+.4f} | zero frac pure "
        f"{ZC[_k]['zero_frac_pure']:.3f} vs nonpure "
        f"{ZC[_k]['zero_frac_nonpure']:.3f}")
b["A_zero_census"] = dict(
    per_substrate=ZC,
    note="the excluded cells are NOT a random sample of the population: "
         "dropping them is selection on the OUTCOME, and the m_out contrast "
         "gives the direction of the induced bias.")


# ---- (B) k_NEUT on the FULL population (no exclusion) -------------------
def _bisect_neut(fn, lo=0.0, hi=8.0, grid_step=0.25):
    grid = np.arange(lo, hi + 1e-9, grid_step)
    rg = np.array([fn(float(x)) for x in grid])
    mono = bool(np.all(np.diff(rg) <= 1e-12))
    if not (mono and rg[0] > 0 > rg[-1]):
        return None, mono, float(rg[0]), float(rg[-1])
    a, c = lo, hi
    for _ in range(60):
        mid = 0.5 * (a + c)
        if fn(mid) > 0:
            a = mid
        else:
            c = mid
    return 0.5 * (a + c), mono, float(rg[0]), float(rg[-1])


KN = {}
for _k, _f in FIT.items():
    _lg, _lp = _f["logm"], _f["logp"]
    _kn_full, _mo_f, _r0_f, _r6_f = _bisect_neut(lambda x, kk=_k: _rho_full(x, kk))
    _kn_sub, _mo_s, _r0_s, _r6_s = _bisect_neut(
        lambda x, a=_lp, g=_lg: _spear_np(a - x * g, g))
    KN[_k] = dict(k_neut_full=_kn_full, monotone_full=_mo_f,
                  rho_at_k0_full=_r0_f, rho_at_k8_full=_r6_f,
                  k_neut_sub=_kn_sub, monotone_sub=_mo_s,
                  rho_at_k0_sub=_r0_s, rho_at_k8_sub=_r6_s,
                  d_full_minus_sub=(None if (_kn_full is None or _kn_sub is None)
                                    else _kn_full - _kn_sub))
    log(f"[B] {_k}: k_NEUT FULL (no exclusion) "
        f"{'None' if _kn_full is None else round(_kn_full, 5)} "
        f"[monotone {_mo_f}, rho(0) {_r0_f:+.4f} -> rho(8) {_r6_f:+.4f}] | "
        f"k_NEUT SUBPOP {'None' if _kn_sub is None else round(_kn_sub, 5)} "
        f"[monotone {_mo_s}] | full-sub "
        f"{KN[_k]['d_full_minus_sub']}")
b["B_neutralising_exponent"] = dict(
    per_substrate=KN,
    note="k_NEUT is defined on the FULL population because P2==0 gives "
         "R_k == 0 for EVERY k (a tied bottom rank at every exponent), so "
         "this estimator requires no outcome-selected exclusion. The "
         "subpopulation value is the same estimator restricted to the "
         "cells the card's fit could have used.")

# ---- (C) the card's three regression estimators, OUTCOME-SELECTED -------
RG = {}
for _k, _f in FIT.items():
    _lg, _lp, _n = _f["logm"], _f["logp"], _f["n"]
    _dg, _dp = _lg - _lg.mean(), _lp - _lp.mean()
    _vg = float((_dg * _dg).sum())
    k_ols = float((_dg * _dp).sum() / _vg)
    _res = _dp - k_ols * _dg
    _orel = abs(float((_res * _dg).sum())) / max(
        float(math.sqrt((_res * _res).sum()) * math.sqrt(_vg)), 1e-300)
    assert _orel < 1e-10, (_k, _orel, "CERT-OLS orthogonality (STOP)")
    _r = float((_dg * _dp).sum()
               / (math.sqrt(_vg) * math.sqrt(float((_dp * _dp).sum()))))
    k_rma = float(np.sign(_r) * _dp.std(ddof=1) / _dg.std(ddof=1))
    assert abs(k_rma - k_ols / abs(_r)) / abs(k_rma) < 1e-12, \
        (_k, "CERT-RMA identity (STOP)")
    _ii, _jj = np.triu_indices(_n, 1)
    _ddg = _lg[_jj] - _lg[_ii]
    _ok = _ddg != 0.0
    k_ts = float(np.median((_lp[_jj][_ok] - _lp[_ii][_ok]) / _ddg[_ok]))
    _npairs = int(_ok.sum())
    del _ii, _jj, _ddg, _ok
    _rng = np.random.default_rng(SEED_BOOT)
    _bk = np.empty(B_BOOT)
    for _bb in range(B_BOOT):
        _s = _rng.integers(0, _n, _n)
        _x, _y = _lg[_s], _lp[_s]
        _x = _x - _x.mean()
        _y = _y - _y.mean()
        _bk[_bb] = (_x * _y).sum() / (_x * _x).sum()
    RG[_k] = dict(k_ols=k_ols, k_ts=k_ts, k_rma=k_rma, pearson_r=_r,
                  k_ols_ci95=[float(np.quantile(_bk, 0.025)),
                              float(np.quantile(_bk, 0.975))],
                  k_spread=float(max(k_ols, k_ts, k_rma)
                                 - min(k_ols, k_ts, k_rma)),
                  n_fit=_n, n_pairs_used=_npairs, ortho_rel=_orel,
                  outcome_selected=True,
                  k_neut_sub_minus_k_ols=(None if KN[_k]["k_neut_sub"] is None
                                          else KN[_k]["k_neut_sub"] - k_ols),
                  k_neut_full_minus_k_ols=(None if KN[_k]["k_neut_full"] is None
                                           else KN[_k]["k_neut_full"] - k_ols))
    log(f"[C] {_k}: k_OLS {k_ols:.4f} CI95 "
        f"[{RG[_k]['k_ols_ci95'][0]:.4f},{RG[_k]['k_ols_ci95'][1]:.4f}] | "
        f"k_TS {k_ts:.4f} | k_RMA {k_rma:.4f} (r {_r:+.4f}) | spread "
        f"{RG[_k]['k_spread']:.4f} | k_NEUT_full - k_OLS "
        f"{RG[_k]['k_neut_full_minus_k_ols']}")
b["C_regression_estimators"] = dict(
    per_substrate=RG,
    label="OUTCOME-SELECTED: computed on the P2>0 subpopulation only, "
          "because log(0) is undefined. Reported for the card's sake; the "
          "exclusion is not random (see leg A).",
    refs="Forstmeier 2018 (OLS with predictor noise biases the slope LOW; "
         "Theil-Sen is robust to outliers, NOT to predictor noise); "
         "RMA gated as the identity k_RMA = k_OLS/|r|.")

# ---- (D) the COMPONENT-SHUFFLED spurious baselines (Pearson 1897) ------
SP = {}
for _k in POP:
    _m = POP[_k]["m_out"]
    _p2 = P2V[_k]
    _row = {}
    for _nm, _kv in (("k0", 0.0), ("k1", 1.0),
                     ("k_neut_full", KN[_k]["k_neut_full"]),
                     ("k_ols", RG[_k]["k_ols"])):
        if _kv is None:
            continue
        _rng = np.random.default_rng(SEED_SPUR)
        _dr = np.empty(B_SPUR)
        _den = LAM[_k] ** 2 * _m ** float(_kv)
        for _i in range(B_SPUR):
            _dr[_i] = _spear_np(_rng.permutation(_p2) / _den, _m)
        _row[_nm] = dict(
            k=float(_kv), measured=_rho_full(float(_kv), _k),
            spur_median=float(np.median(_dr)),
            spur_p05=float(np.quantile(_dr, 0.05)),
            spur_p95=float(np.quantile(_dr, 0.95)),
            excess=_rho_full(float(_kv), _k) - float(np.median(_dr)))
        log(f"[D] {_k} {_nm} (k={float(_kv):.4f}): measured "
            f"{_row[_nm]['measured']:+.4f} | SPURIOUS median "
            f"{_row[_nm]['spur_median']:+.4f} "
            f"[{_row[_nm]['spur_p05']:+.4f},{_row[_nm]['spur_p95']:+.4f}] "
            f"-> Pearson-corrected excess {_row[_nm]['excess']:+.4f}")
    SP[_k] = _row
b["D_spurious_baseline"] = dict(
    per_substrate=SP, n_draws=B_SPUR, seed=SEED_SPUR,
    kind="component shuffling on the FULL population: P2 permuted across "
         "cells (zeros included), m_out held, R_sh = P2_perm/(lam1^2*m^k)",
    note="the k=0 arm is the built-in positive control -- with no "
         "denominator the shuffled index must be uncorrelated with m_out.",
    refs="Pearson 1897 Proc R Soc 60:489-498 (spurious organic "
         "correlation); Jackson & Somers 1991 Oecologia 86:147-151 "
         "(identify the appropriate null correlation; randomisation test).")

# ---- (E) the Q224-3 2x2 at the EXCLUSION-FREE k* -----------------------
TR = {}
for _k, _p in POP.items():
    _m, _R = _p["m_out"], _p["R"]
    _row = {}
    for _kname, _kv in (("k_neut_full", KN[_k]["k_neut_full"]),
                        ("k_ols_outcome_selected", RG[_k]["k_ols"])):
        if _kv is None:
            continue
        _Rkv = _Rk(float(_kv), _k)
        _sub = {"k": float(_kv)}
        for _nm in ("carrier", "mirror"):
            _d = MM[_k][_nm]
            _i, _ci = _d["i"], _d["ci"]
            _sub[_nm] = dict(
                pct_mm_R=_d["pct_mm_R"], pct_cls_R=_d["pct_cls_R"],
                pct_pop_R=float((_R < _R[_i]).sum() / len(_R)),
                pct_pop_Rk=float((_Rkv < _Rkv[_i]).sum() / len(_Rkv)),
                pct_cls_Rk=float((_Rkv[_ci] < _Rkv[_i]).sum() / len(_ci)))
            _sub[_nm]["d_primary"] = abs(_sub[_nm]["pct_cls_Rk"]
                                         - _d["pct_mm_R"])
            _sub[_nm]["d_companion"] = abs(_sub[_nm]["pct_pop_Rk"]
                                           - _d["pct_mm_R"])
            log(f"[E] {_k} {_kname} {_nm}: mass-matched R "
                f"{_d['pct_mm_R']:.4f} | class R {_d['pct_cls_R']:.4f} -> "
                f"class R_k {_sub[_nm]['pct_cls_Rk']:.4f} "
                f"(d {_sub[_nm]['d_primary']:.4f}) | pop R "
                f"{_sub[_nm]['pct_pop_R']:.4f} -> pop R_k "
                f"{_sub[_nm]['pct_pop_Rk']:.4f} "
                f"(d {_sub[_nm]['d_companion']:.4f})")
        _sub["max_d_primary"] = max(_sub["carrier"]["d_primary"],
                                    _sub["mirror"]["d_primary"])
        _sub["max_d_companion"] = max(_sub["carrier"]["d_companion"],
                                      _sub["mirror"]["d_companion"])
        _row[_kname] = _sub
    TR[_k] = _row
b["E_transport"] = dict(
    per_substrate=TR,
    note="descriptive only. The parent's registered Q224-3 bar is NOT "
         "scored here: the branch is K_DEGENERATE and stays so. Read as "
         "'does a global exponent reproduce a LOCAL mass match', with the "
         "premise-0c 2x2 so that the comparison SET and the STATISTIC are "
         "not moved in the same step (L222).")

b["reading"] = (
    "The card's primary estimator family is undefined on 9.8-15.1% of its "
    "own population: P2 == 0 for 126/1288, 128/1264 and 190/1260 present "
    "descending cells, and those cells are systematically LOW out-mass, so "
    "the log-log fit is a regression on a sample selected on its own "
    "outcome. The registered FIT-UNMEASURABLE escape therefore fired "
    "correctly. The exclusion-free instrument is the RANK-BASED "
    "neutralising exponent, which is defined on the whole population "
    "because a zero numerator gives R_k == 0 at every k. Report k_NEUT "
    "(full) as the mass-neutral exponent, k_NEUT (subpopulation) and the "
    "three regression estimators as outcome-selected companions, and every "
    "residual rho against its COMPONENT-SHUFFLED spurious baseline rather "
    "than against zero (Pearson 1897).")
b["limitations"] = [
    "POST-HOC and UNREGISTERED: no branch, no bar, no prediction. The "
    "parent's K_DEGENERATE stands exactly as measured.",
    "k_NEUT is a DESCRIPTIVE reparametrisation that zeroes a rank "
    "correlation; it is not a better model of the biology.",
    "The zeros are tied at the bottom of R_k at every k, so k_NEUT is "
    "determined entirely by the non-zero cells' ORDERING against m_out -- "
    "the zeros contribute rank mass, not slope information.",
    "Three substrates sharing a graph are not three independent "
    "replications; one depth, one weighting, no dynamics.",
    "Both actors' percentiles are DESCRIPTIONS OF A SELECTED CELL "
    "(Kriegeskorte 2009).",
]

_s2 = os.stat(_PP)
assert (_s2.st_size, _s2.st_mtime_ns) == _fpp, "l224/static.json MUTATED"
_s3 = os.stat(_P213)
assert (_s3.st_size, _s3.st_mtime_ns) == _fp213, "l213/static.json MUTATED"
b["readonly_fingerprints_ok"] = True
b["runtime_s"] = time.time() - _TB
os.makedirs("l224", exist_ok=True)
with open("l224/addendum.json", "w") as _fh:
    json.dump(b, _fh, indent=1, default=float)
log(f"[done] addendum {b['runtime_s']:.1f}s -> l224/addendum.json")
