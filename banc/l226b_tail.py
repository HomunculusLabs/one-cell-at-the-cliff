
# ======================= L226b POST-HOC ADDENDUM =======================
# DECLARED POST-HOC. Unregistered. No branch, no bar, no prediction. Pure
# arithmetic on values the parent already certified, plus the two prior
# batches' stored values. Everything above this line is l226_static.py
# lines 1-503 VERBATIM (a literal PREFIX cut immediately BEFORE the
# parent's writer), so every parent gate re-ran for free and this file
# contains ZERO writes to the parent artifact.

_FPAR = (os.stat("l226/static.json").st_size,
         os.stat("l226/static.json").st_mtime_ns)
with open("l226/static.json") as _fh:
    PAR = json.load(_fh)

# ---- CERT-226 (HALTING): the parent's branch-bearing stored values at
# float/str/int equality BEFORE any addendum number is read.
_n226 = 0
for _k, _v in (("branch", q1), ("p_up", p_up38), ("SA38", int(SA38)),
               ("p_up_rank_of_10", rank_actor), ("cell_ok", bool(cell_ok)),
               ("currency_ok", bool(cur_ok)),
               ("SA_bar_exact_binomial_p", binom_p),
               ("rho", CUR38[ACTOR]["rho"])):
    assert PAR["q1"][_k] == _v, ("CERT-226", _k, PAR["q1"][_k], _v)
    _n226 += 1
assert PAR["q2"]["survivors"] == surv38 and PAR["q2"]["n_survivors"] == k38
assert PAR["q3"]["C3"] == C3 and PAR["q3"]["p_C3"] == p_C3
assert PAR["cert"]["cert_subset_max"] == 0.0
assert all(PAR["predictions"].values()), "parent predictions drifted"
_n226 += 6
for _pk, _arm in ARMPAIR:
    _kk = f"B38|{_pk}|{_arm}"
    for _m in ("rho", "p_up", "p_dn", "mean_A", "mean_dS"):
        assert PAR["q4"][_kk][_m] == CUR38[_kk][_m], ("CERT-226 q4", _kk, _m)
        _n226 += 1
print(f"\nCERT-226 (HALTING): {_n226} parent values reproduced at "
      f"float/int/str equality\n")

ALL3 = {"B36": CUR, "B37": CUR, "B38": CUR38}


def _cell(bk, pk, arm):
    return (CUR38 if bk == "B38" else CUR)[f"{bk}|{pk}|{arm}"]


# ====== (A) L214's Q4 'ACCOUNTED' leg, RE-READ OUT OF SAMPLE ============
# L214 registered Ti|f4wA as the exception that a pass must account for,
# and scored it ACCOUNTED because in BOTH batches (a) |mean_A| ranked in
# the bottom 3 of 10 and (b) NEITHER tail cleared alpha .05 — "its currency
# value is near zero and its sign is noise, so a sign disagreement there is
# uninformative rather than contradictory".
EXC = "Ti|f4wA"
_q4_314 = S214["q4"]["rows"]
assert _q4_314["B36"]["bottom3"] and _q4_314["B36"]["no_tail_sig"]
assert _q4_314["B37"]["bottom3"] and _q4_314["B37"]["no_tail_sig"]
assert S214["q4"]["branch"] == "ACCOUNTED"
_c38 = _cell("B38", "Ti", "f4wA")
_rank38 = absrank_of[EXC]
_bot3_38 = _rank38 <= 3
_nosig38 = (_c38["p_up"] >= ALPHA) and (_c38["p_dn"] >= ALPHA)
# ASSERT the contradiction against a stored field (L225's law), never
# merely describe it.
assert _bot3_38, "the magnitude clause failed too — different finding"
assert not _nosig38, "no contradiction to assert (addendum A is vacuous)"
print(f"(A) L214's Q4 exception {EXC} OUT OF SAMPLE: |mean_A| "
      f"{abs(_c38['mean_A']):.5f} rank {_rank38}/10 (bottom3 {_bot3_38}) "
      f"but p_dn {_c38['p_dn']:.5f} < {ALPHA} -> no_tail_sig False")
print(f"    => L214's Q4 would score UNACCOUNTED on B38. The MAGNITUDE "
      f"clause holds in 3/3 batches; the NO-SIGNIFICANCE clause holds in "
      f"2/3. It also survives B38's own BH: {'Ti|f4wA|dn' in surv38}.")

# ====== (B) why: a near-zero currency MEAN does not bound its CORRELATION
_absA, _absR, _names = [], [], []
for _bk in ("B36", "B37", "B38"):
    for _pk, _arm in ARMPAIR:
        _c = _cell(_bk, _pk, _arm)
        _absA.append(abs(_c["mean_A"]))
        _absR.append(abs(_c["rho"]))
        _names.append(f"{_bk}|{_pk}|{_arm}")
_absA, _absR = np.array(_absA), np.array(_absR)
_rho_AR = spearman(_absA, _absR)
_nd = len(set(_absA)), len(set(_absR))
print(f"\n(B) over all {len(_absA)} cells (3 batches x 10): Spearman"
      f"(|mean_A|, |rho|) = {_rho_AR:+.4f}  [distinct values {_nd[0]}/"
      f"{_nd[1]}, no tie inflation]")
_small = _absA <= np.quantile(_absA, 0.3)
print(f"    the 30% smallest-|mean_A| cells carry mean |rho| "
      f"{_absR[_small].mean():.4f} vs {_absR[~_small].mean():.4f} for the "
      f"rest, and their max |rho| is {_absR[_small].max():.4f}")
print(f"    => a near-zero currency MEAN and a strong per-seed "
      f"CORRELATION are different objects. L214's Q4 used a MAGNITUDE "
      f"screen to excuse a CORRELATION result; the screen cannot do that "
      f"job, and B38 is where it broke.")

# ====== (C) what actually carries L214's reading: SIGN INSTABILITY ======
_exc_rhos = [_cell(b, "Ti", "f4wA")["rho"] for b in ("B36", "B37", "B38")]
_exc_signs = [int(np.sign(r)) for r in _exc_rhos]
_act_rhos = [_cell(b, "Tr", "f4ng")["rho"] for b in ("B36", "B37", "B38")]
print(f"\n(C) {EXC} rho across the three batches: "
      f"{[round(r, 4) for r in _exc_rhos]} signs {_exc_signs} = UNSTABLE; "
      f"Tr|f4ng {[round(r, 4) for r in _act_rhos]} = 3/3 positive")
# multiplicity context: 20 one-tailed hypotheses per batch at alpha .05
_hits = {}
for _bk in ("B36", "B37", "B38"):
    _h = [f"{_pk}|{_arm}|" + ("up" if _cell(_bk, _pk, _arm)["p_up"] < ALPHA
                              else "dn")
          for _pk, _arm in ARMPAIR
          if min(_cell(_bk, _pk, _arm)["p_up"],
                 _cell(_bk, _pk, _arm)["p_dn"]) < ALPHA]
    _hits[_bk] = _h
_exp_fp = 20 * ALPHA
_consist = {}
for _pk, _arm in ARMPAIR:
    for _t in ("up", "dn"):
        _n3 = sum(_cell(b, _pk, _arm)[f"p_{_t}"] < ALPHA
                  for b in ("B36", "B37", "B38"))
        if _n3:
            _consist[f"{_pk}|{_arm}|{_t}"] = _n3
print(f"    per-batch cells with ANY tail < {ALPHA}: "
      + " | ".join(f"{b} {len(v)} {v}" for b, v in _hits.items())
      + f" (expected false positives per batch at 20 hypotheses: {_exp_fp})")
print(f"    cross-batch consistency count: "
      f"{dict(sorted(_consist.items(), key=lambda kv: -kv[1]))}")
print(f"    => L214's Q4 CONCLUSION survives but on a different clause: "
      f"the exception cell is sign-UNSTABLE (one significant tail in one "
      f"of three batches is what 20 hypotheses predict), while the actor "
      f"is 3/3 in the SAME tail. The CROSS-BATCH filter is the instrument "
      f"that works; a within-batch magnitude screen is not.")

ADD = {
    "label": "L226b POST-HOC ADDENDUM — declared unregistered, no branch",
    "parent": "l226/static.json",
    "cert_226": _n226,
    "A_q4_exception_out_of_sample": {
        "cell": EXC,
        "stored_L214_branch": S214["q4"]["branch"],
        "B38_absA": abs(_c38["mean_A"]), "B38_absA_rank_of_10": _rank38,
        "B38_bottom3": bool(_bot3_38),
        "B38_p_up": _c38["p_up"], "B38_p_dn": _c38["p_dn"],
        "B38_no_tail_sig": bool(_nosig38),
        "would_score": "UNACCOUNTED",
        "survives_B38_BH": bool("Ti|f4wA|dn" in surv38),
        "magnitude_clause_batches": 3, "nosig_clause_batches": 2,
        "finding": ("L214's registered ACCOUNTED verdict for its own "
                    "exception cell does NOT hold out of sample: the "
                    "magnitude clause holds 3/3, the no-significance "
                    "clause 2/3.")},
    "B_magnitude_vs_correlation": {
        "n_cells": int(len(_absA)),
        "spearman_absA_absrho": _rho_AR,
        "distinct_absA": _nd[0], "distinct_absrho": _nd[1],
        "mean_absrho_small_absA": float(_absR[_small].mean()),
        "mean_absrho_rest": float(_absR[~_small].mean()),
        "max_absrho_small_absA": float(_absR[_small].max()),
        "finding": ("a near-zero currency MEAN does not bound the "
                    "per-seed CORRELATION; a magnitude screen cannot "
                    "excuse a correlation result.")},
    "C_what_carries_the_reading": {
        "exception_rhos": [float(r) for r in _exc_rhos],
        "exception_signs": _exc_signs,
        "actor_rhos": [float(r) for r in _act_rhos],
        "per_batch_any_tail_hits": {k: v for k, v in _hits.items()},
        "expected_false_positives_per_batch": _exp_fp,
        "cross_batch_consistency": _consist,
        "finding": ("the CROSS-BATCH filter is the instrument that "
                    "separates signal from multiplicity here: the actor "
                    "is 3/3 in one tail, every other hit is 1/3 or 2/3.")},
}
assert (os.stat("l226/static.json").st_size,
        os.stat("l226/static.json").st_mtime_ns) == _FPAR, \
    "parent artifact MUTATED by the addendum (STOP)"
with open("l226/addendum.json", "w") as _fh:
    json.dump(ADD, _fh, indent=1)
print("\nwrote l226/addendum.json; parent artifact fingerprint unchanged")
