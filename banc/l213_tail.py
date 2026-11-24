# ================= L213 TAIL (appended by l213_build.py) =================
# Everything above this line is VERBATIM source: l151_static.py 1-319,
# l178_tail.py 7-149, the l206_mid bridge, l206_tail.py 22-121, and
# l207_tail.py 48-112 (build_sub / reach_sub / power_iter_sub) + 199-253
# (Rstat / pct_of / rankvec / spearman_l). So CERT-F4, the three stored gains
# at float equality, the CSR orientation, all 20 pool sizes and CERT-178 (420
# stored anatomical values at FLOAT EQUALITY) have ALL re-run as free
# certification before any L213 value is read.
# PREREG: l213/PREREG.md (registered first, incl. the premise correction that
# the MIRROR gi 928 is NOT pure_proj). Writes l213/static.json ONLY.
# Zero rollouts, zero settles, zero dynamics.

import os

o["design"] = (
    "L213 TYPE or CLASS? L207 found both members of the bilateral DNp33 pair "
    "at pct .06-.10 of mass-matched descending cohorts on three substrates "
    "and called it a cell-TYPE property. Here the same anatomical statistic "
    "R = P2/(lam1^2*m_out) is computed for EVERY present descending cell on "
    "the three L207 substrates, aggregated (Q1) by cell_type with a "
    "within-mass-stratum type-label permutation null, (Q2) by the pure_proj "
    "class flag with the same null on the flag, and (Q3) per actor WITHIN "
    "ITS OWN class -- the carrier inside pure_proj, the mirror inside "
    "non-pure_proj, because the mirror is not pure_proj. "
    "PREREG l213/PREREG.md.")
o["prereg"] = "l213/PREREG.md"

GI_MIR = 928
TYPE_NAME = "DNp33"
N_DRAWS = 2000
SEED = 21342
N_STRATA = 10
PCT_BAR = 0.10
NULL_BAR = 0.05

# ---------------- the class flag (premise, asserted) -----------------------
pure_proj = dn_proj & ~dn_into
assert bool(pure_proj[GI_CARRIER]), "carrier is not pure_proj (STOP)"
assert not bool(pure_proj[GI_MIR]), \
    "mirror IS pure_proj -- the PREREG premise correction is wrong (STOP)"
assert bool(dn_into[GI_MIR]) and bool(dn_proj[GI_MIR]), "mirror flags (STOP)"
o["premise"] = dict(
    carrier_gi=GI_CARRIER, mirror_gi=GI_MIR,
    carrier_pure_proj=True, mirror_pure_proj=False,
    carrier_dn_into=bool(dn_into[GI_CARRIER]),
    mirror_dn_into=bool(dn_into[GI_MIR]),
    n_dn_all=int(dn_all.sum()), n_dn_into=int(dn_into.sum()),
    n_dn_proj=int(dn_proj.sum()), n_pure_proj=int(pure_proj.sum()),
    note="registered in l213/PREREG.md BEFORE any aggregate was computed: "
         "the two DNp33 members sit in DIFFERENT classes under the very flag "
         "hypothesis (ii) proposes as the explanation.")
log(f"[premise] pure_proj {int(pure_proj.sum())} of {int(dn_all.sum())} DNs | "
    f"carrier True / mirror False (registered)")

# ---------------- cell_type map -------------------------------------------
_ct = ann.cell_type.fillna("").astype(str).to_numpy()
CT_OF = {}
for _g, _c in zip(ann.gi.to_numpy(), _ct):
    _c = _c.strip()
    if _c and _c.lower() != "nan":
        CT_OF[int(_g)] = _c
assert CT_OF.get(GI_CARRIER) == TYPE_NAME, (CT_OF.get(GI_CARRIER), "carrier type")
assert CT_OF.get(GI_MIR) == TYPE_NAME, (CT_OF.get(GI_MIR), "mirror type")

# ---------------- the three substrates ------------------------------------
SUBS = {"G0_closure": build_sub(keep_new, emask_n, "G0_closure"),
        "G1_cutwA": build_sub(keep_wA, emask_wA, "G1_cutwA"),
        "F4_f4wA": build_sub(keep_f4, emask_f4, "F4_f4wA")}
assert SUBS["G0_closure"]["n"] == int(keep_new.sum()) == S92["n_new"]
assert SUBS["G0_closure"]["n_edges"] == S92["edges_new"]
assert SUBS["G1_cutwA"]["n"] == 21785 and SUBS["G1_cutwA"]["n_edges"] == 644177
assert SUBS["F4_f4wA"]["n"] == 21789 and SUBS["F4_f4wA"]["n_edges"] == 469618
LAM = {}
for _k, _s in SUBS.items():
    LAM[_k], _spr = power_iter_sub(_s, _s["jv"])
    assert LAM[_k] > 0 and _spr < 1e-6, (_k, "power iteration (STOP)")
    log(f"[sub] {_k}: n {_s['n']:,} edges {_s['n_edges']:,} "
        f"lam1(g=1) {LAM[_k]:.6f} (rel spread {_spr:.2e})")
o["substrates"] = {k: dict(n=v["n"], n_edges=v["n_edges"], lam1_g1=LAM[k])
                   for k, v in SUBS.items()}

# ---------------- CERT-207 (HALTING): L207's stored ladder, FLOAT EQUALITY --
# l207/static.json is opened READ-ONLY and fingerprinted (L175: never rewrite
# another card's artifact). Every stored R/R1/P2/m_out of every present
# ladder cell on all three substrates must be reproduced by the verbatim
# Rstat/reach_sub path BEFORE any type or class aggregate is read.
_L207_PATH = "l207/static.json"
_st207 = os.stat(_L207_PATH)
_fp207 = (_st207.st_size, _st207.st_mtime_ns)
with open(_L207_PATH) as _fh:
    S207 = json.load(_fh)
assert S207["branches"]["Q1"] == "B_NEITHER" and \
    S207["branches"]["Q2"] == "M_AVOIDS", "l207 verdict drift (STOP)"
assert S207["ladders"]["carrier_gi"] == GI_CARRIER
_n207 = 0
_VERB = {}          # (sub, gi) -> verbatim Rstat dict, reused by CERT-T
for _k in SUBS:
    _rows = S207["ladder_table"][_k]
    assert len(_rows) == S207["ladders"]["n_present"][_k]
    for _row in _rows:
        _d = Rstat(SUBS[_k], int(_row["gi"]), LAM[_k])
        _VERB[(_k, int(_row["gi"]))] = _d
        for _f in ("R", "R1", "P2", "m_out"):
            assert _d[_f] == _row[_f], (_k, _row["gi"], _f, _d[_f], _row[_f],
                                        "CERT-207 ladder (STOP)")
            _n207 += 1
# the two slot comparators as their own objects
for _k, _gi in (("G0_closure", int(S207["ladders"]["slot21_closure_gi"])),
                ("F4_f4wA", int(S207["ladders"]["slot25_f4_gi"]))):
    _d = Rstat(SUBS[_k], _gi, LAM[_k])
    _hit = [r for r in S207["ladder_table"][_k] if int(r["gi"]) == _gi]
    assert len(_hit) == 1, (_k, _gi, "slot comparator not in ladder (STOP)")
    assert _d["R"] == _hit[0]["R"], (_k, _gi, "slot comparator R (STOP)")
    _n207 += 1
# L207's Q2 mirror/carrier R per substrate
for _k in SUBS:
    _q2 = S207["Q2_mirror"]["per_substrate"][_k]
    assert not _q2["absent"]
    _dm = Rstat(SUBS[_k], GI_MIR, LAM[_k])
    _dc = Rstat(SUBS[_k], GI_CARRIER, LAM[_k])
    _VERB[(_k, GI_MIR)] = _dm
    _VERB[(_k, GI_CARRIER)] = _dc
    assert _dm["R"] == _q2["mirror_R"], (_k, "CERT-207 mirror_R (STOP)")
    assert _dc["R"] == _q2["carrier_R"], (_k, "CERT-207 carrier_R (STOP)")
    assert _dm["m_out"] == _q2["mirror_m_out"] and \
        _dc["m_out"] == _q2["carrier_m_out"], (_k, "CERT-207 m_out (STOP)")
    _n207 += 4
_st207b = os.stat(_L207_PATH)
assert (_st207b.st_size, _st207b.st_mtime_ns) == _fp207, \
    "l207/static.json CHANGED during this run (STOP)"
log(f"[CERT-207] GREEN {_n207} checks at FLOAT EQUALITY (l207 ladder_table "
    f"x3 substrates + 2 slot comparators + Q2 actors); artifact fingerprint "
    f"unchanged")
o["cert_207"] = dict(n_checks=_n207, mode="float equality (==)",
                     source="l207/static.json (read-only, fingerprinted)",
                     fingerprint_size=_fp207[0], verdict_asserted=True)


# ---------------- the FAST census kernel, GATED (CERT-T) -------------------
# P2(c) for ALL sources at once: with A = sub operator (A[t,s]), the depth-2
# pool reach from source c is  P2(c) = sum_{t in pools} (A @ A)[t, c]
#                                   = ((A^T)^2 @ 1_pools)[c].
# The transposed matvec is the SAME np.add.at expression with the index
# arrays swapped (the L210/CERT-MV transpose identity), so no new machinery
# exists -- but the ACCUMULATION ORDER differs from reach_sub's forward walk,
# so float equality is NOT claimed (L206: a float-equality claim is a claim
# about the expression). It is gated at max rel diff < 1e-12 instead.
def _atv(sub, x):
    """A^T @ x using reach_sub's expression with rows/cols swapped."""
    y = np.zeros(sub["n"])
    np.add.at(y, sub["cols"], sub["jv"] * x[sub["rows"]])
    return y


def census(sub):
    p = np.zeros(sub["n"])
    p[sub["pool_all"]] = 1.0
    u = _atv(sub, p)            # u[c] = depth-1 pool reach from c
    v = _atv(sub, u)            # v[c] = depth-2 pool reach from c
    return u, v


CENS = {}
_nT = 0
_maxrel = 0.0
for _k, _s in SUBS.items():
    _u, _v = census(_s)
    CENS[_k] = (_u, _v)
    # bilinear identity on probes: forward pool-sum == transpose read
    for _gi in (GI_CARRIER, GI_MIR):
        _lc = int(_s["loc"][_gi])
        _rr = reach_sub(_lc, _s, 2)
        for _d, _arr in ((1, _u), (2, _v)):
            _fwd = float(sum(_rr[_d].values()))
            _bwd = float(_arr[_lc])
            _rel = abs(_fwd - _bwd) / max(abs(_fwd), 1e-300)
            assert _rel < 1e-12, (_k, _gi, _d, _fwd, _bwd, "CERT-T (STOP)")
            _maxrel = max(_maxrel, _rel)
            _nT += 1
    # and against every certified L207 ladder cell
    for (_kk, _gi), _d in _VERB.items():
        if _kk != _k:
            continue
        _lc = int(_s["loc"][_gi])
        for _f, _arr in (("P1", _u), ("P2", _v)):
            _rel = abs(_d[_f] - float(_arr[_lc])) / max(abs(_d[_f]), 1e-300)
            assert _rel < 1e-12, (_k, _gi, _f, "CERT-T ladder (STOP)")
            _maxrel = max(_maxrel, _rel)
            _nT += 1
log(f"[CERT-T] GREEN {_nT} checks: fast transposed census agrees with the "
    f"verbatim reach_sub at max rel diff {_maxrel:.2e} (< 1e-12)")
o["cert_T"] = dict(n_checks=_nT, max_rel_diff=_maxrel, bar=1e-12,
                   mode="relative difference (summation order differs; float "
                        "equality deliberately NOT claimed)",
                   note="transpose = same np.add.at expression with rows/cols "
                        "swapped (L210 CERT-MV transpose identity)")

# ---------------- the population, per substrate ---------------------------
POP = {}
for _k, _s in SUBS.items():
    _u, _v = CENS[_k]
    _pres = np.where(_s["keep"] & dn_all)[0]
    _pres = _pres[_s["om"][_pres] > 0]
    _gis = [int(g) for g in _pres]
    _lc = np.array([int(_s["loc"][g]) for g in _gis])
    _R = _v[_lc] / (LAM[_k] ** 2 * _s["om"][_pres])
    # the two actors' census R must equal the verbatim R to < 1e-12
    for _gi in (GI_CARRIER, GI_MIR):
        _i = _gis.index(_gi)
        _rel = abs(_R[_i] - _VERB[(_k, _gi)]["R"]) / _VERB[(_k, _gi)]["R"]
        assert _rel < 1e-12, (_k, _gi, "population R vs verbatim (STOP)")
    POP[_k] = dict(gis=_gis, R=_R, m_out=_s["om"][_pres].copy(),
                   pure=pure_proj[_pres].copy(),
                   ct=[CT_OF.get(g, "") for g in _gis])
    _nt = sum(1 for c in POP[_k]["ct"] if c)
    log(f"[pop] {_k}: {len(_gis)} present descending cells with m_out>0 "
        f"({_nt} named types, {int(POP[_k]['pure'].sum())} pure_proj)")
o["population"] = {k: dict(n=len(v["gis"]),
                           n_named=sum(1 for c in v["ct"] if c),
                           n_pure=int(v["pure"].sum()))
                   for k, v in POP.items()}


# ---------------- mass strata + the within-stratum permutation null -------
def strata_of(m_out, n_strata=N_STRATA):
    lm = np.log(m_out)
    qs = np.quantile(lm, np.linspace(0, 1, n_strata + 1))
    qs[0], qs[-1] = -np.inf, np.inf
    st = np.digitize(lm, qs[1:-1], right=False)
    assert st.min() >= 0 and st.max() <= n_strata - 1
    return st


def perm_within(st, rng, n_strata=N_STRATA):
    """index permutation that stays inside each stratum."""
    idx = np.arange(len(st))
    out = idx.copy()
    for s in range(n_strata):
        sel = idx[st == s]
        out[sel] = rng.permutation(sel)
    return out


for _k in POP:
    POP[_k]["st"] = strata_of(POP[_k]["m_out"])
o["strata"] = {k: dict(n_strata=N_STRATA,
                       counts=[int((v["st"] == s).sum())
                               for s in range(N_STRATA)])
               for k, v in POP.items()}
log("[strata] counts " + " | ".join(
    f"{k} {o['strata'][k]['counts']}" for k in o["strata"]))

# ---------------- Q213-1: TYPE ------------------------------------------
Q1 = {}
for _k, _p in POP.items():
    _R, _ct, _st = _p["R"], _p["ct"], _p["st"]
    _bytype = {}
    for _i, _c in enumerate(_ct):
        if _c:
            _bytype.setdefault(_c, []).append(_i)
    _big = {c: ix for c, ix in _bytype.items() if len(ix) >= 2}
    assert TYPE_NAME in _big, (_k, "DNp33 has < 2 present members (STOP)")
    _tix = np.array(_big[TYPE_NAME])
    _real = float(np.median(_R[_tix]))
    _meds = {c: float(np.median(_R[np.array(ix)])) for c, ix in _big.items()}
    _mv = np.array(sorted(_meds.values()))
    _pct_of_type_medians = float((_mv < _real).sum() / len(_mv))
    # the within-stratum permutation null on the DNp33 type median
    _rng = np.random.default_rng(SEED)
    _cnt0 = np.bincount(_st, minlength=N_STRATA)
    _null = np.empty(N_DRAWS)
    for _d in range(N_DRAWS):
        _pi = perm_within(_st, _rng)
        assert np.array_equal(np.bincount(_st[_pi], minlength=N_STRATA),
                              _cnt0), (_k, _d, "stratum counts (STOP)")
        _null[_d] = float(np.median(_R[_pi][_tix]))
    _npct = float((_null < _real).sum() / N_DRAWS)
    _br = ("T_TYPE_LOW" if _npct <= NULL_BAR else
           "T_TYPE_HIGH" if _npct >= 1 - NULL_BAR else "T_TYPE_TYPICAL")
    Q1[_k] = dict(
        n_types_ge2=len(_big), n_cells_in_types=sum(len(v) for v in _big.values()),
        dnp33_members=[_p["gis"][i] for i in _tix],
        dnp33_member_R=[float(_R[i]) for i in _tix],
        type_median=_real,
        pct_among_type_medians=_pct_of_type_medians,
        type_median_all_median=float(np.median(_mv)),
        ratio_to_median_of_type_medians=float(np.median(_mv) / _real),
        null_pct=_npct, null_median=float(np.median(_null)),
        null_p05=float(np.quantile(_null, 0.05)),
        null_p95=float(np.quantile(_null, 0.95)),
        n_draws=N_DRAWS, branch=_br)
    log(f"[Q1] {_k}: DNp33 type median {_real:.6g} | pct among "
        f"{len(_big)} type medians {_pct_of_type_medians:.3f} | NULL pct "
        f"{_npct:.4f} (null med {np.median(_null):.6g}) -> {_br}")
_b1 = [Q1[k]["branch"] for k in Q1]
BR1 = max(set(_b1), key=_b1.count) if max(
    _b1.count(b) for b in set(_b1)) >= 2 else "T_MIXED"
log(f"[Q1] BRANCH {BR1} ({_b1})")
o["Q1_type"] = dict(branch=BR1, per_substrate=Q1,
                    limit="DNp33 has 2 present members, so the type median "
                          "is a 2-POINT statistic: a DIRECTION only, never a "
                          "magnitude (PREREG limit 1).")

# ---------------- Q213-2: CLASS -----------------------------------------
Q2 = {}
for _k, _p in POP.items():
    _R, _pu, _st = _p["R"], _p["pure"], _p["st"]
    _med_p = float(np.median(_R[_pu]))
    _med_n = float(np.median(_R[~_pu]))
    _real = float(np.log10(_med_p) - np.log10(_med_n))
    _rng = np.random.default_rng(SEED + 1)
    _cnt0 = np.bincount(_st, minlength=N_STRATA)
    _null = np.empty(N_DRAWS)
    for _d in range(N_DRAWS):
        _pi = perm_within(_st, _rng)
        assert np.array_equal(np.bincount(_st[_pi], minlength=N_STRATA),
                              _cnt0), (_k, _d, "stratum counts (STOP)")
        _pu_s = _pu[_pi]
        assert int(_pu_s.sum()) == int(_pu.sum())
        _null[_d] = float(np.log10(np.median(_R[_pu_s]))
                          - np.log10(np.median(_R[~_pu_s])))
    _npct = float((_null < _real).sum() / N_DRAWS)
    _br = ("C_CLASS_LOW" if _npct <= NULL_BAR else
           "C_CLASS_HIGH" if _npct >= 1 - NULL_BAR else "C_CLASS_TYPICAL")
    Q2[_k] = dict(n_pure=int(_pu.sum()), n_nonpure=int((~_pu).sum()),
                  median_pure=_med_p, median_nonpure=_med_n,
                  dlog10=_real, ratio_pure_over_nonpure=float(_med_p / _med_n),
                  null_pct=_npct, null_median=float(np.median(_null)),
                  null_p05=float(np.quantile(_null, 0.05)),
                  null_p95=float(np.quantile(_null, 0.95)),
                  n_draws=N_DRAWS, branch=_br)
    log(f"[Q2] {_k}: median pure {_med_p:.6g} vs nonpure {_med_n:.6g} "
        f"(dlog10 {_real:+.4f}, ratio {_med_p / _med_n:.3f}) | NULL pct "
        f"{_npct:.4f} -> {_br}")
_b2 = [Q2[k]["branch"] for k in Q2]
BR2 = max(set(_b2), key=_b2.count) if max(
    _b2.count(b) for b in set(_b2)) >= 2 else "C_MIXED"
log(f"[Q2] BRANCH {BR2} ({_b2})")
o["Q2_class"] = dict(branch=BR2, per_substrate=Q2,
                     flag="pure_proj = dn_proj & ~dn_into (l169c flag)")

# ---------------- Q213-3: CONDITIONAL (within own class) -----------------
Q3 = {}
for _k, _p in POP.items():
    _R, _pu, _gis = _p["R"], _p["pure"], _p["gis"]
    _ic = _gis.index(GI_CARRIER)
    _im = _gis.index(GI_MIR)
    assert bool(_pu[_ic]) and not bool(_pu[_im]), (_k, "actor class (STOP)")
    _cls_c = _R[_pu]
    _cls_m = _R[~_pu]
    _pc = pct_of(float(_R[_ic]), [float(x) for x in _cls_c])
    _pm = pct_of(float(_R[_im]), [float(x) for x in _cls_m])
    _br = ("D_TYPE_SURVIVES" if (_pc <= PCT_BAR and _pm <= PCT_BAR) else
           "D_CLASS_EXPLAINS" if (_pc > PCT_BAR and _pm > PCT_BAR) else
           "D_SPLIT")
    Q3[_k] = dict(carrier_class="pure_proj", mirror_class="non_pure_proj",
                  carrier_R=float(_R[_ic]), mirror_R=float(_R[_im]),
                  carrier_pct_in_class=_pc, mirror_pct_in_class=_pm,
                  carrier_class_n=int(_pu.sum()),
                  mirror_class_n=int((~_pu).sum()),
                  carrier_class_median=float(np.median(_cls_c)),
                  mirror_class_median=float(np.median(_cls_m)),
                  carrier_deficit_x=float(np.median(_cls_c) / _R[_ic]),
                  mirror_deficit_x=float(np.median(_cls_m) / _R[_im]),
                  branch=_br)
    log(f"[Q3] {_k}: carrier pct-in-pure_proj {_pc:.3f} ({_pu.sum()} cells) | "
        f"mirror pct-in-nonpure {_pm:.3f} ({(~_pu).sum()} cells) -> {_br}")
_b3 = [Q3[k]["branch"] for k in Q3]
BR3 = max(set(_b3), key=_b3.count) if max(
    _b3.count(b) for b in set(_b3)) >= 2 else "D_MIXED"
log(f"[Q3] BRANCH {BR3} ({_b3})")
o["Q3_conditional"] = dict(
    branch=BR3, per_substrate=Q3, pct_bar=PCT_BAR,
    null_kind="WITHIN-CLASS percentile among present descending cells of the "
              "actor's own class, NOT mass-matched -- a different null from "
              "L207's cohort, so the MAGNITUDE does not transport (L207).")

# ---------------- derived reading (not a branch) -------------------------
if BR3 == "D_TYPE_SURVIVES":
    READ = "TYPE"
elif BR2 == "C_CLASS_LOW" and BR3 == "D_CLASS_EXPLAINS":
    READ = "CLASS"
else:
    READ = "MIXTURE"
o["derived_reading"] = dict(
    reading=READ,
    rule="(i) TYPE iff Q3 == D_TYPE_SURVIVES; (ii) CLASS iff Q2 == "
         "C_CLASS_LOW AND Q3 == D_CLASS_EXPLAINS; else MIXTURE.",
    premise_note="the strong CLASS reading was already strained before any "
                 "measurement: the mirror is not pure_proj (see o['premise']).")
log(f"[READ] derived reading: {READ}")

# ---------------- predictions, scored ------------------------------------
_p1 = sum(1 for k in Q1 if Q1[k]["branch"] == "T_TYPE_LOW") >= 2
_p2 = BR2 == "C_CLASS_TYPICAL"
_p3 = all(Q3[k]["branch"] == "D_TYPE_SURVIVES" for k in Q3)
_p4 = all(Q3[k]["mirror_pct_in_class"] <= 0.10 for k in Q3)
_p5 = sum(1 for k in Q1 if Q1[k]["null_pct"] <= 0.02) >= 2
o["predictions"] = {
    "Q213_P1": dict(registered="Q1 == T_TYPE_LOW on >= 2 of 3",
                    measured=_b1, correct=bool(_p1)),
    "Q213_P2": dict(registered="Q2 == C_CLASS_TYPICAL", measured=BR2,
                    correct=bool(_p2)),
    "Q213_P3": dict(registered="Q3 == D_TYPE_SURVIVES on all 3",
                    measured=_b3, correct=bool(_p3)),
    "Q213_P4": dict(registered="mirror within-non-pure_proj pct <= 0.10 on all 3",
                    measured={k: Q3[k]["mirror_pct_in_class"] for k in Q3},
                    correct=bool(_p4)),
    "Q213_P5": dict(registered="DNp33 type-median null pct <= 0.02 on >= 2 of 3",
                    measured={k: Q1[k]["null_pct"] for k in Q1},
                    correct=bool(_p5))}
o["n_predictions_correct"] = int(sum(
    1 for v in o["predictions"].values() if v["correct"]))
o["branches"] = dict(Q1=BR1, Q2=BR2, Q3=BR3, derived=READ)
o["bars"] = dict(null_bar=NULL_BAR, pct_bar=PCT_BAR, n_strata=N_STRATA,
                 n_draws=N_DRAWS, seed=SEED)
o["limitations"] = [
    "DNp33 has 2 present members: the type median is a 2-POINT statistic. "
    "Direction only, never a magnitude.",
    "One type, one class flag, one statistic, one null family. Other "
    "partitions of descending cells are untested.",
    "ANATOMICAL leg only: no row mask, no settle, no seed -- wiring "
    "geometry, not an operating point (L164).",
    "The within-stratum permutation holds log out-mass stratum and type "
    "SIZE but not neurotransmitter, side, or neuropil composition.",
    "Q3 is a within-class percentile and is NOT mass-matched: its magnitude "
    "does not transport to L207's cohort percentile (L207 cross-null law).",
    "The three substrates share a graph and most cells, so they are not "
    "three independent replications.",
]
o["runtime_s"] = time.time() - t0
os.makedirs("l213", exist_ok=True)
with open("l213/static.json", "w") as _fh:
    json.dump(o, _fh, indent=1, default=float)
log(f"[done] {o['runtime_s']:.1f}s -> l213/static.json | Q1 {BR1} | "
    f"Q2 {BR2} | Q3 {BR3} | reading {READ} | predictions "
    f"{o['n_predictions_correct']}/5")
