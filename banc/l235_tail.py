# ================= L235 TAIL (appended by l235_build.py) =================
# Everything above this line is SLICE A = l218_static.py lines 1-1624
# VERBATIM: a literal PREFIX of the GENERATED parent, cut immediately BEFORE
# L218's own per-draw deflation loop, so every gate L218 ran up to that point
# re-runs here as the code that ACTUALLY produced l218/static.json
# (CERT-218T, CERT-W50, CERT-DEFLV, CERT-206, CERT-MV, CERT-LEFT,
# CERT-REBUILD, CERT-178, CERT-NULL, CERT-F4, CERT-REW, the 50-depth walks,
# Q218-1/2 and the real-graph Q218-3 scalars). The parent's own draw loop is
# REPLACED by this card's loop, which captures all 35 actors instead of one;
# PREREG 0i registers that as a cost slice and CERT-235B is what admits it.
# SLICE D below is l231_tail.py's certified midrank/spearman (L221 tie law).
# Nothing here re-transcribes a certified def (L85); no lab module is
# imported (L175). PREREG: l235/PREREG.md. Writes l235/static.json ONLY.
# Zero rollouts, zero settles.

_T235 = _time.time()


def _e235(tag):
    log(f"[time-235] {tag}: {_time.time() - _T235:.1f}s")


_e235("SLICE A complete (L218's block up to the real-graph Q218-3)")

# ---------------- CERT-235A (HALTING): the parent artifact reproduced -------
# Every leaf of l218/static.json outside the keys the parent writes AFTER the
# slice boundary must equal what THIS run put in o, at float equality.
# Coverage bar DERIVED from the artifact's own leaf count (L224), never fixed.
S218 = json.load(open("l218/static.json"))
_LATE235 = ("Q218_3_u2", "predictions", "amendments", "limitations",
            "priors_readonly", "rows_per_draw_recomputed")
_n235a = 0


def _lc235(got, want, path):
    """recursive leaf compare at FLOAT/EXACT equality (the L211 pattern)."""
    global _n235a
    if isinstance(want, dict):
        assert isinstance(got, dict), (path, "type", type(got))
        assert set(got) == set(want), (path, "keys",
                                      sorted(set(got) ^ set(want)))
        for k in want:
            _lc235(got[k], want[k], f"{path}.{k}")
    elif isinstance(want, list):
        assert isinstance(got, list), (path, "type", type(got))
        assert len(got) == len(want), (path, "len", len(got), len(want))
        for i, w in enumerate(want):
            _lc235(got[i], w, f"{path}[{i}]")
    else:
        assert got == want, (path, got, want, "CERT-235A MISMATCH (STOP)")
        _n235a += 1


def _nleaf235(x):
    if isinstance(x, dict):
        return sum(_nleaf235(v) for v in x.values())
    if isinstance(x, list):
        return sum(_nleaf235(v) for v in x)
    return 1


_BAR235A = sum(_nleaf235(S218[k]) for k in S218 if k not in _LATE235)
for _k in S218:
    if _k in _LATE235:
        continue
    assert _k in o, (_k, "SLICE A did not produce a key the parent stored")
    _lc235(o[_k], S218[_k], _k)
assert _n235a == _BAR235A, (_n235a, _BAR235A, "CERT-235A coverage (STOP)")
_CORE235 = ("Q218_1_primary", "Q218_2_rate", "profile", "cert_218t",
            "cert_w50", "Q210_1_primary", "Q210_2_bare", "Q210_4_gap",
            "cert_206", "cert_rebuild")
_floor235 = sum(_nleaf235(S218[k]) for k in _CORE235)
assert _floor235 > 0 and _n235a >= _floor235, \
    (_n235a, _floor235, "CERT-235A misses a core block (STOP)")
assert o["banner"] == S218["banner"], "banner drift (STOP)"
log(f"[CERT-235A] GREEN {_n235a} float equalities == the artifact's own leaf "
    f"count {_BAR235A} over {len([k for k in S218 if k not in _LATE235])} "
    f"keys (CERT-218T {o['cert_218t']['n_checks']} + CERT-W50 "
    f"{o['cert_w50']['n_checks']} + CERT-DEFLV + Q218-1/2 + the 50-depth "
    f"profile), floor {_floor235} derived from 10 core blocks")
o235_certA = dict(n_checks=_n235a, coverage_bar_derived=_BAR235A,
                  floor_derived=_floor235, mode="float equality (==)",
                  n_keys=len([k for k in S218 if k not in _LATE235]),
                  excluded=list(_LATE235),
                  subsumes=dict(cert_218t=o["cert_218t"]["n_checks"],
                                cert_w50=o["cert_w50"]["n_checks"]))
_e235("CERT-235A")

# ---------------- PREREG 0b asserted as an IDENTITY on the real graph -------
# K2(c) is coeff(U2, V2, c): the SAME expression the parent used inline, so
# the pool sum and the bilinear form are actor-independent BY CONSTRUCTION.
_n235b = 0
assert coeff(U2, V2, LC) == K2_REAL, "coeff(U2,V2) != the parent's K2 (STOP)"
_n235b += 1
for _f, _w in ((K2_REAL, S218["Q218_3_u2"]["K2_real"]),
               (A2_REAL, S218["Q218_3_u2"]["A2_real"]),
               (K_REAL, S218["Q218_3_u2"]["K_real"]),
               (float(U2[LC]), S218["Q218_3_u2"]["u2_carrier_real"]),
               (_resR, S218["Q218_3_u2"]["residual_real_right"]),
               (_resL, S218["Q218_3_u2"]["residual_real_left"]),
               (_lfR, S218["Q218_3_u2"]["lam2_signed_rayleigh_right"]),
               (_lfL, S218["Q218_3_u2"]["lam2_signed_rayleigh_left"]),
               (L2R, S218["Q218_3_u2"]["lam2_abs_right"]),
               (L2L, S218["Q218_3_u2"]["lam2_abs_left"]),
               (float(U1[LC]), o["Q210_2_bare"]["u1_carrier_real"])):
    assert _f == _w, (_f, _w, "CERT-235B real-graph scalar (STOP)")
    _n235b += 1

# ---------------- the cohort: 35 actors, the parent's own dict --------------
NAMES = list(ACTORS)
assert len(NAMES) == 35, (len(NAMES), "cohort != 35 (STOP)")
assert NAMES[0] == "carrier" and ACTORS["carrier"] == LC, "actor order (STOP)"
LOCS = np.array([ACTORS[n] for n in NAMES], dtype=np.int64)
assert np.unique(LOCS).size == 35, "duplicate actor local index (STOP)"
U1R = np.array([float(U1[lc]) for lc in LOCS])
U2R = np.array([float(U2[lc]) for lc in LOCS])
KR = np.array([coeff(U1, V1, int(lc)) for lc in LOCS])
K2R = np.array([coeff(U2, V2, int(lc)) for lc in LOCS])
A2R = K2R / KR
assert KR[0] == K_REAL and K2R[0] == K2_REAL and A2R[0] == A2_REAL, \
    "carrier row != the parent's own scalars (STOP)"
_n235b += 3
assert float(U1R.min()) > 0.0, "a Perron left entry is non-positive (STOP)"

# ---------------- the loop (PREREG 0i: replaces the parent's own) -----------
ND = len(rows210)
KK35 = np.zeros((ND, 35))
K2K35 = np.zeros((ND, 35))
U1K35 = np.zeros((ND, 35))
U2K35 = np.zeros((ND, 35))
CK = np.zeros(ND)
RESK35 = np.zeros(ND)
S234 = json.load(open("l234/static.json"))
_PDK2 = S234["Q2_K2_null"]["per_draw_K2"]
assert len(_PDK2) == ND, (len(_PDK2), ND, "stored per-draw K2 length (STOP)")
_ID_MAXREL = 0.0
_EPS64 = 64.0 * np.finfo(np.float64).eps
for k in range(ND):
    ls2, ld2, va2 = REB[k]
    _lk, _vk, _ = pi_dir(va2, ls2, ld2)
    _lkL, _uk, _ = pi_dir(va2, ld2, ls2)
    _l2r, _v2, _ = defl_pair(va2, ls2, ld2, _vk, _uk)
    _l2l, _u2, _ = defl_pair(va2, ld2, ls2, _uk, _vk)
    _f1, _r1 = defl_resid(va2, ls2, ld2, _vk, _uk, _v2)
    _f2, _r2 = defl_resid(va2, ld2, ls2, _uk, _vk, _u2)
    assert _lk == rows210[k]["lam"], (k, "per-draw lam drift (STOP)")
    RESK35[k] = max(_r1, _r2)
    _sv1 = float(_vk[POOL_IDX].sum())
    _uv1 = float(_uk @ _vk)
    _sv2 = float(_v2[POOL_IDX].sum())
    _uv2 = float(_u2 @ _v2)
    CK[k] = (_sv2 / _uv2) / (_sv1 / _uv1)
    for j in range(35):
        _lc = int(LOCS[j])
        KK35[k, j] = coeff(_uk, _vk, _lc)
        K2K35[k, j] = coeff(_u2, _v2, _lc)
        U1K35[k, j] = float(_uk[_lc])
        U2K35[k, j] = float(_u2[_lc])
        assert U1K35[k, j] > 0.0 and KK35[k, j] != 0.0, \
            (k, j, "a per-draw Perron entry is non-positive: the identity's "
                   "denominator does not exist (STOP)")
        # PREREG 0b, asserted per actor per draw (P3): the scale-invariant
        # currency IS the bare currency divided by u1, times C_k.
        _a = K2K35[k, j] / KK35[k, j]
        _b = (U2K35[k, j] / U1K35[k, j]) * CK[k]
        _rel = abs(_a - _b) / max(abs(_a), abs(_b), 1e-300)
        _ID_MAXREL = max(_ID_MAXREL, _rel)
        assert _rel <= _EPS64, (k, j, _a, _b, _rel, "0b identity (STOP)")
    # the carrier column must BE the parent's / L234's stored per-draw values
    assert KK35[k, 0] == KK[k], (k, "per-draw K drift (STOP)")
    assert K2K35[k, 0] == _PDK2[k], (k, "per-draw K2 vs L234 (STOP)")
    _n235b += 3
_e235("the 100-draw loop (35 actors captured)")

A2K35 = K2K35 / KK35
_nres235 = int((RESK35 <= RES_BAR).sum())
# ---- CERT-235B (HALTING): the stored carrier results, reproduced -----------
_pA2_car = float((A2K35[:, 0] < A2R[0]).mean())
_pu2_car = float((np.abs(U2K35[:, 0]) < abs(U2R[0])).mean())
_pu1_car = float((U1K35[:, 0] < U1R[0]).mean())
_pK_car = float((KK35[:, 0] < KR[0]).mean())
_pK2_car = float((K2K35[:, 0] < K2R[0]).mean())
for _f, _w, _tag in (
        (float(np.median(A2K35[:, 0])), S218["Q218_3_u2"]["A2_draw_med"], "A2med"),
        (float(np.percentile(A2K35[:, 0], 5)), S218["Q218_3_u2"]["A2_p05"], "A2p05"),
        (float(np.percentile(A2K35[:, 0], 95)), S218["Q218_3_u2"]["A2_p95"], "A2p95"),
        (_pA2_car, S218["Q218_3_u2"]["A2_percentile"], "A2pct"),
        (abs(A2R[0] - float(np.median(A2K35[:, 0]))),
         S218["Q218_3_u2"]["abs_gap_to_median"], "A2gap"),
        (_pu2_car, S218["Q218_3_u2"]["u2_carrier_percentile_absval"], "u2pct"),
        (float(np.median(np.abs(U2K35[:, 0]))),
         S218["Q218_3_u2"]["u2_draw_med_absval"], "u2med"),
        (_nres235, S218["Q218_3_u2"]["draws_resolved"], "nres"),
        (ND, S218["Q218_3_u2"]["draws_total"], "ndraws"),
        (float(RESK35.max()), S218["Q218_3_u2"]["residual_draw_max"], "resmax"),
        (float(np.median(RESK35)), S218["Q218_3_u2"]["residual_draw_med"], "resmed"),
        (_pu1_car, o["Q210_2_bare"]["carrier_u_percentile"], "u1pct"),
        (float(np.median(U1K35[:, 0])), o["Q210_2_bare"]["null_u_car_med"], "u1med"),
        (float(np.percentile(U1K35[:, 0], 5)),
         o["Q210_2_bare"]["null_u_car_p05"], "u1p05"),
        (float(np.percentile(U1K35[:, 0], 95)),
         o["Q210_2_bare"]["null_u_car_p95"], "u1p95"),
        (_pK_car * 100.0, o["Q210_1_primary"]["carrier_K_percentile"], "Kpct"),
        (float(np.median(KK35[:, 0])), o["Q210_1_primary"]["null_K_med"], "Kmed"),
        (_pK2_car, S234["Q2_K2_null"]["pct_K2"], "K2pct"),
        (float(np.median(K2K35[:, 0])), S234["Q2_K2_null"]["K2_draw_med"], "K2med")):
    assert _f == _w, (_tag, _f, _w, "CERT-235B stored carrier (STOP)")
    _n235b += 1
log(f"[CERT-235B] GREEN {_n235b} float equalities: this card's own 35-actor "
    f"loop reproduces L218's ENTIRE stored carrier draw block (A2 median/p05/"
    f"p95/percentile, |u2| percentile + median, residuals, draws resolved), "
    f"L218's Q210-2 u1 block (percentile {_pu1_car:.3f}, median), Q210-1's K "
    f"percentile and median, and L234's 100 stored per-draw K2 values — so "
    f"the cost slice (PREREG 0i) is the parent's loop, measured not assumed")
o235_certB = dict(n_checks=_n235b, mode="float equality (==)",
                  identity_max_rel=_ID_MAXREL, identity_bar=float(_EPS64),
                  identity_checks=ND * 35,
                  sources=["l218/static.json Q218_3_u2 + Q210_2_bare + "
                           "Q210_1_primary", "l234/static.json Q2_K2_null "
                           "per_draw_K2", "the slice's own KK / rows210"])
_e235("CERT-235B")

# ---------------- the cohort audit (PREREG registered quantities) -----------
PA2 = np.array([float((A2K35[:, j] < A2R[j]).mean()) for j in range(35)])
PA2ABS = np.array([float((np.abs(A2K35[:, j]) < abs(A2R[j])).mean())
                   for j in range(35)])
PU2 = np.array([float((np.abs(U2K35[:, j]) < abs(U2R[j])).mean())
                for j in range(35)])
PU1 = np.array([float((U1K35[:, j] < U1R[j]).mean()) for j in range(35)])
_RK = np.abs(U2K35 / U1K35)
PR = np.array([float((_RK[:, j] < abs(U2R[j] / U1R[j])).mean())
               for j in range(35)])
PK = np.array([float((KK35[:, j] < KR[j]).mean()) for j in range(35)])
PK2 = np.array([float((K2K35[:, j] < K2R[j]).mean()) for j in range(35)])
D = np.abs(PA2 - PU2)
DABS = np.abs(PA2ABS - PU2)
S1 = np.abs(PR - PU2)
S2 = np.abs(PA2ABS - PR)
S3 = np.abs(PA2 - PA2ABS)
BAR235 = 0.5
_ndis = int((D > BAR235).sum())
RATE = float(_ndis / 35)
_ndis_abs = int((DABS > BAR235).sum())
if RATE >= 0.25:
    BRANCH235 = "I_CONVENTION"
elif _ndis <= 3 and bool(D[0] > BAR235):
    BRANCH235 = "I_CARRIER"
else:
    BRANCH235 = "I_MIXED"
_rho_main = spearman(PA2, PU2)
_rho_abs = spearman(PA2ABS, PU2)
_rho_u1D = spearman(PU1, D)
_rho_RK = spearman(PR, PA2ABS)
_ord = np.argsort(-D, kind="mergesort")
_car_rank = int(np.where(_ord == 0)[0][0]) + 1
_nd_pa2 = int(np.unique(PA2).size)
_nd_pu2 = int(np.unique(PU2).size)
_nd_pu1 = int(np.unique(PU1).size)
_nd_D = int(np.unique(D).size)
log(f"[Q235-1] {BRANCH235} | disagreement |pA2 - p|u2|| > {BAR235}: "
    f"{_ndis}/35 = rate {RATE:.4f} (abs-matched companion {_ndis_abs}/35) | "
    f"carrier D {D[0]:.3f} (pA2 {PA2[0]:.3f} vs p|u2| {PU2[0]:.3f}) rank "
    f"{_car_rank}/35 | median D {float(np.median(D)):.3f} mean "
    f"{float(D.mean()):.3f}")
log(f"[Q235-2] midrank Spearman(pA2, p|u2|) {_rho_main:+.6f} "
    f"(distinct {_nd_pa2}/{_nd_pu2}) | abs form {_rho_abs:+.6f} | "
    f"Spearman(pu1, D) {_rho_u1D:+.6f} (distinct {_nd_pu1}/{_nd_D}) | "
    f"Spearman(pR, pA2abs) {_rho_RK:+.6f}")
log(f"[Q235-3 ladder] mean rungs: u1-division s1 {float(S1.mean()):.4f} | "
    f"per-draw constant s2 {float(S2.mean()):.4f} | sign s3 "
    f"{float(S3.mean()):.4f} | carrier (s1 {S1[0]:.3f}, s2 {S2[0]:.3f}, "
    f"s3 {S3[0]:.3f}) | pu1 carrier {PU1[0]:.3f} median cohort "
    f"{float(np.median(PU1)):.3f}")

COHORT = {}
for j, nm in enumerate(NAMES):
    COHORT[nm] = dict(gi=GI_OF[nm], local=int(LOCS[j]), m_out=M_OUT[nm],
                      u1_real=float(U1R[j]), u2_real=float(U2R[j]),
                      K_real=float(KR[j]), K2_real=float(K2R[j]),
                      A2_real=float(A2R[j]),
                      pA2=float(PA2[j]), pA2abs=float(PA2ABS[j]),
                      pu2=float(PU2[j]), pu1=float(PU1[j]), pR=float(PR[j]),
                      pK=float(PK[j]), pK2=float(PK2[j]),
                      D=float(D[j]), Dabs=float(DABS[j]),
                      s1=float(S1[j]), s2=float(S2[j]), s3=float(S3[j]),
                      disagrees=bool(D[j] > BAR235))
o235_Q1 = dict(
    branch=BRANCH235, bar=BAR235, n_actors=35, n_draws=ND,
    n_disagree=_ndis, rate=RATE, n_disagree_abs_matched=_ndis_abs,
    rate_abs_matched=float(_ndis_abs / 35),
    bar_convention=0.25, bar_carrier_max_n=3,
    carrier_D=float(D[0]), carrier_pA2=float(PA2[0]),
    carrier_pu2=float(PU2[0]), carrier_rank_by_D=_car_rank,
    D_median=float(np.median(D)), D_mean=float(D.mean()),
    D_min=float(D.min()), D_max=float(D.max()),
    resolution_floor=1.0 / ND,
    note=("nonselective over L178's 35 actors against the SAME 100 l169c "
          "draws; the carrier's own row is DESCRIPTION (PREREG 0h) and the "
          "rate is the inferential object"))
o235_Q2 = dict(
    spearman_pA2_pu2=_rho_main, spearman_pA2abs_pu2=_rho_abs,
    spearman_pu1_D=_rho_u1D, spearman_pR_pA2abs=_rho_RK,
    distinct_pA2=_nd_pa2, distinct_pu2=_nd_pu2, distinct_pu1=_nd_pu1,
    distinct_D=_nd_D, rank_method="midrank (l231_tail.py 429-450, L221)",
    bar_rank_equiv=0.5,
    note=("percentiles over 100 draws take at most 101 values, so ties are "
          "expected and cap a rank correlation below its analytic value "
          "(L227) — distinct counts are printed for every rank statistic"))
o235_Q3 = dict(
    ladder=["pu2", "pR", "pA2abs", "pA2"],
    s1_u1_division_mean=float(S1.mean()), s1_median=float(np.median(S1)),
    s2_perdraw_constant_mean=float(S2.mean()), s2_median=float(np.median(S2)),
    s3_sign_mean=float(S3.mean()), s3_median=float(np.median(S3)),
    s1_carrier=float(S1[0]), s2_carrier=float(S2[0]), s3_carrier=float(S3[0]),
    pu1_carrier=float(PU1[0]), pu1_median=float(np.median(PU1)),
    pu1_min=float(PU1.min()), pu1_max=float(PU1.max()),
    C_k_median=float(np.median(CK)), C_k_min=float(CK.min()),
    C_k_max=float(CK.max()), C_k_n_negative=int((CK < 0).sum()),
    identity="A2_k(c) == (u2_k[c]/u1_k[c]) * C_k, C_k actor-independent",
    note=("DESCRIPTION, no branch: the ladder decomposes the published "
          "disagreement into the u1 division (s1), the actor-independent "
          "per-draw constant (s2) and the sign convention (s3)"))
o235_cohort = COHORT
_e235("Q235-1/2/3")

# ---------------- predictions ------------------------------------------------
o235_pred = dict(
    P1=dict(registered="branch == I_CONVENTION (rate >= 0.25)",
            measured=BRANCH235, correct=bool(BRANCH235 == "I_CONVENTION")),
    P2=dict(registered="midrank Spearman(pA2, p|u2|) in [-0.5, +0.5]",
            measured=_rho_main,
            correct=bool(_rho_main is not None and -0.5 <= _rho_main <= 0.5)),
    P3=dict(registered="the 0b identity holds at rel <= 64 eps on all "
                       "35 x 100 cells",
            measured=_ID_MAXREL, correct=bool(_ID_MAXREL <= _EPS64)),
    P4=dict(registered="carrier rank by D <= 5 of 35",
            measured=_car_rank, correct=bool(_car_rank <= 5)),
    P5=dict(registered="mean(s1) > mean(s2): u1 moves it more than C_k",
            measured=[float(S1.mean()), float(S2.mean())],
            correct=bool(float(S1.mean()) > float(S2.mean()))),
    P6=dict(registered="mean(s3) >= 0.05 (the sign step is not negligible)",
            measured=float(S3.mean()), correct=bool(float(S3.mean()) >= 0.05)),
)
_np235 = sum(1 for _v in o235_pred.values() if _v["correct"])
log(f"[predictions-235] {_np235}/6 TRUE: " + " ".join(
    f"{_k}={'T' if _v['correct'] else 'F'}" for _k, _v in o235_pred.items()))

# ---------------- priors read-only + the writer ------------------------------
import os as _os235
_FP235 = {p: (_os235.stat(p).st_size, _os235.stat(p).st_mtime_ns)
          for p in ("l178/static.json", "l206/static.json",
                    "l210/static.json", "l218/static.json",
                    "l218_static.py", "l218_tail.py", "l231_tail.py",
                    "l234/static.json")}
for _p, _v in _FP235.items():
    assert (_os235.stat(_p).st_size, _os235.stat(_p).st_mtime_ns) == _v, \
        (_p, "a prior artifact MOVED during the run (STOP)")
log(f"[priors-235] GREEN {len(_FP235)} prior artifacts unchanged "
    f"(size, mtime_ns) across the run")

out235 = dict(o)
out235["design"] = dict(
    card="L235 the CURRENCY-INVERSION audit, asked NONSELECTIVELY",
    prereg="l235/PREREG.md",
    slice_a="l218_static.py lines 1-1624 VERBATIM (literal PREFIX, cut "
            "immediately before the parent's own per-draw deflation loop)",
    slice_d="l231_tail.py lines 429-450 VERBATIM (midrank + spearman)",
    parent_design=S218["design"], rollouts=0)
out235["parent_l218"] = dict(prereg="l218/PREREG.md",
                             banner=S218["banner"])
out235["cert_235a"] = o235_certA
out235["cert_235b"] = o235_certB
out235["Q1_inversion_rate"] = o235_Q1
out235["Q2_rank"] = o235_Q2
out235["Q3_ladder"] = o235_Q3
out235["cohort_35"] = o235_cohort
out235["predictions_235"] = o235_pred
out235["n_predictions_true_235"] = _np235
out235["limitations_235"] = [
    "one substrate (f4wA), one operator |g*W_beta|, one null family (the "
    "l169c destination swaps); L207's cross-null law applies",
    "100 draws cap every percentile at 0.01 resolution (PREREG 0e)",
    "the 35-actor cohort is itself L178's selected DN-adjacent family, so "
    "'cohort-wide' means within that family and not within the graph",
    "unit-L2 normalisation of u2 across operators is a CONVENTION (PREREG "
    "0g): a disagreement rate is a statement about the convention and is "
    "NOT evidence either currency is wrong",
    "the carrier's own row is DESCRIPTION (selected on a related statistic, "
    "Kriegeskorte 2009); only the cohort rate, the rank correlations and the "
    "ladder means are inferential",
    "modes 1 and 2 only: no third-mode currency is audited here (L234's A3 "
    "has no null of its own)",
]
out235["priors_readonly_235"] = {k: list(v) for k, v in _FP235.items()}
_os235.makedirs("l235", exist_ok=True)
json.dump(out235, open("l235/static.json", "w"), indent=1)
_e235("total")
log("[done] wrote l235/static.json")
