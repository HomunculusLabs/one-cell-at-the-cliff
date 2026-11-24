# ================= L213 ADDENDUM TAIL (appended by l213b_build.py) ========
# UNREGISTERED, POST HOC, DESCRIPTIVE. Writes l213/addendum.json ONLY and
# never touches l213/static.json (L175).
#
# WHY: the registered run returned Q1 = T_TYPE_LOW (DNp33's type median at
# null pct .010-.015 against a MASS-STRATIFIED label permutation) and
# Q3 = D_CLASS_EXPLAINS (both actors mid-pack in a RAW within-class
# percentile). Those are not contradictory readings of the cell -- they are
# two different nulls, and the PREREG said in advance that Q3's null is not
# mass-matched. This addendum measures the ONE quantity that decides which
# it is: where the actors sit in their own class's MASS distribution, and
# what their within-class percentile becomes once the class cohort is
# mass-matched the way L207's cohort was.

import os

a = {"design": "L213 addendum: reconcile Q1 (mass-stratified, LOW) with Q3 "
                "(raw within-class, MID-PACK) by measuring the actors' MASS "
                "rank inside their own class and re-reading the within-class "
                "percentile on a mass-matched sub-cohort. UNREGISTERED, "
                "descriptive.",
     "parent": "l213/static.json", "prereg": "l213/PREREG.md",
     "registered": False}

ADD = {}
for _k, _p in POP.items():
    _R, _pu, _gis, _m = _p["R"], _p["pure"], _p["gis"], _p["m_out"]
    _row = {}
    for _nm, _gi, _cls in (("carrier", GI_CARRIER, _pu),
                           ("mirror", GI_MIR, ~_pu)):
        _i = _gis.index(_gi)
        _ci = np.where(_cls)[0]
        assert _i in set(int(x) for x in _ci), (_k, _nm, "actor not in class")
        # (a) MASS percentile inside its own class
        _mpct = float((_m[_ci] < _m[_i]).sum() / len(_ci))
        # (b) raw within-class R percentile (the registered Q3 number)
        _rpct = float((_R[_ci] < _R[_i]).sum() / len(_ci))
        # (c) within-class percentile on the 100 nearest in log out-mass
        _oth = _ci[_ci != _i]
        _d = np.abs(np.log(_m[_oth]) - math.log(float(_m[_i])))
        _sel = _oth[np.argsort(_d, kind="stable")[:100]]
        assert len(_sel) == 100, (_k, _nm, "class cohort short")
        _mmpct = float((_R[_sel] < _R[_i]).sum() / len(_sel))
        _spread = float(np.max(np.abs(np.log(_m[_sel])
                                      - math.log(float(_m[_i])))))
        _row[_nm] = dict(
            gi=_gi, class_n=int(len(_ci)), R=float(_R[_i]),
            m_out=float(_m[_i]),
            mass_pct_in_class=_mpct,
            R_pct_in_class_raw=_rpct,
            R_pct_in_class_massmatched=_mmpct,
            cohort_k=100, cohort_logmass_spread=_spread,
            cohort_median_R=float(np.median(_R[_sel])),
            deficit_x_vs_massmatched=float(np.median(_R[_sel]) / _R[_i]))
        log(f"[add] {_k} {_nm}: mass pct in class {_mpct:.3f} | R pct raw "
            f"{_rpct:.3f} -> mass-matched {_mmpct:.3f} "
            f"({_row[_nm]['deficit_x_vs_massmatched']:.2f}x, spread "
            f"{_spread:.3f})")
    # (d) does R correlate with mass across the whole population? the
    #     mechanism by which a raw within-class percentile mis-reads.
    _rho = spearman_l([float(x) for x in _R], [float(x) for x in _m])
    _row["rho_R_vs_mout_population"] = _rho
    # (e) and the same for each class separately
    _row["rho_R_vs_mout_pure"] = spearman_l(
        [float(x) for x in _R[_pu]], [float(x) for x in _m[_pu]])
    _row["rho_R_vs_mout_nonpure"] = spearman_l(
        [float(x) for x in _R[~_pu]], [float(x) for x in _m[~_pu]])
    # (f) class MASS composition -- why the 4x raw class gap is mass
    _row["median_mout_pure"] = float(np.median(_m[_pu]))
    _row["median_mout_nonpure"] = float(np.median(_m[~_pu]))
    ADD[_k] = _row
    log(f"[add] {_k}: rho(R, m_out) pop {_rho:+.4f} | pure "
        f"{_row['rho_R_vs_mout_pure']:+.4f} | nonpure "
        f"{_row['rho_R_vs_mout_nonpure']:+.4f} | median m_out pure "
        f"{_row['median_mout_pure']:.1f} vs nonpure "
        f"{_row['median_mout_nonpure']:.1f}")
a["per_substrate"] = ADD
a["reading"] = (
    "Both actors are HIGH-mass cells inside their own class. A RAW "
    "within-class percentile therefore compares them against a class whose "
    "bulk is lower-mass, and R rises with out-mass, so the raw number reads "
    "mid-pack by construction. The mass-matched within-class percentile is "
    "the comparable object and it is the one to read against L207.")
a["limitations"] = [
    "UNREGISTERED and POST HOC: these numbers carry no branch and refute no "
    "registered branch. Q3 stands as measured.",
    "The mass-matched class cohort is a THIRD null (neither Q3's raw class "
    "nor L207's whole-descending cohort): its magnitude transports to "
    "neither (L207 cross-null law).",
    "Descriptive correlations only; no causal or mechanistic claim.",
]
a["runtime_s"] = time.time() - t0
os.makedirs("l213", exist_ok=True)
with open("l213/addendum.json", "w") as _fh:
    json.dump(a, _fh, indent=1, default=float)
log(f"[add] done {a['runtime_s']:.1f}s -> l213/addendum.json")
