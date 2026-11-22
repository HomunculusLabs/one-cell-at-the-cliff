# ================= L207 TAIL (appended by l207_build.py) =================
# Everything above this line is VERBATIM source: l151_static.py 1-319,
# l178_tail.py 7-149, the l206_mid bridge, l206_tail.py 22-121. So CERT-F4,
# the three stored gains at float equality, the CSR orientation, all 20 pool
# sizes, and CERT-178 (420 stored anatomical values at FLOAT EQUALITY) have
# ALL re-run as free certification before any L207 value is read, and LAM1
# for f4wA is already in hand. PREREG: l207/PREREG.md (registered first).
# Writes l207/static.json ONLY. Zero rollouts, zero settles, zero dynamics.

o["design"] = (
    "L207 is the avoidance the CELL or the LADDER SLOT? The ANATOMICAL "
    "lam1^2-normalised depth-2 per-out-mass walk mass into the 20 semantic "
    "motor pools, computed on THREE substrates (G0 closure / G1 cutwA / "
    "f4wA) where the carrier occupies TWO DIFFERENT ladder slots, against "
    "each substrate's own present-ladder cohort, plus the two slot "
    "comparators (closure slot 21, f4wA slot 25), the contralateral homolog "
    "gi 928 DNp33-R on a mass-matched cohort, and the v783 match handle. "
    "PREREG l207/PREREG.md.")
o["prereg"] = "l207/PREREG.md"

GI_MIR = 928
PCT_BAR = 0.10
RHO_BAR = 0.5
COHORT_K = 100

# ---------------- gain invariance of the normalised statistic --------------
# R = P2 / (lam1^2 * m_out) is gain invariant because P2 scales g^2 and
# lam1^2 scales g^2. Asserted numerically, never in prose.
jv_g1 = np.abs(_vnp)
assert np.array_equal(jv_abs_an, G_F4WA * jv_g1), "G>0 scaling not exact"
LAM1_G1, _V1G1, _LI_G1 = power_iter(jv_g1)
assert _LI_G1["rel_spread_last6"] < 1e-6, "g=1 power iteration not converged"
_lam_rel = abs(LAM1_G1 * G_F4WA - LAM1) / LAM1
assert _lam_rel < 1e-10, (_lam_rel, "lam1 not homogeneous in g (STOP)")
_r2_g1 = float(sum(reach(LC_CAR, jv_g1, depth=2)[2].values()))
_r2_g = float(sum(reach(LC_CAR, jv_abs_an, depth=2)[2].values()))
assert _r2_g == S178["E_anatomical"]["all_actors"]["carrier"]["P2abs"], \
    "carrier depth-2 != L178 stored (STOP)"
_r2_rel = abs(_r2_g1 * G_F4WA ** 2 - _r2_g) / _r2_g
assert _r2_rel < 1e-12, (_r2_rel, "depth-2 not homogeneous in g^2 (STOP)")
o["gain_invariance"] = dict(lam1_g1=LAM1_G1, lam1_g=LAM1,
                            lam1_rel_diff=_lam_rel, depth2_rel_diff=_r2_rel,
                            note="R is gain invariant; the cross-substrate "
                                 "comparison is therefore admissible without "
                                 "re-bisecting a gain per substrate.")
log(f"[GAIN-INV] GREEN lam1 rel {_lam_rel:.2e} | depth-2 rel {_r2_rel:.2e}")

# ---------------- the GENERIC substrate builder ----------------------------
# Certified against the certified SPECIALISATION (the f4wA build in
# CERT-HEAD2) before it is applied to any new substrate.
def build_sub(keep, emask, name):
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    ei = np.where(emask)[0]
    s_l = loc[src_all[ei]]
    d_l = loc[dst_all[ei]]
    _sa = sign_all[src_all[ei]]
    _sb = np.where(is_glut[src_all[ei]], -np.abs(_sa), _sa)
    ev = (np.log1p(w_syn[ei]) * _sb).astype(np.float32)
    n = int(keep.sum())
    Wl = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([d_l, s_l])).long(),
        torch.from_numpy(ev), (n, n)).coalesce().to_sparse_csr()
    assert int(Wl.values().numel()) == len(ei), (name, "coalesce changed nnz")
    vv = Wl.values().clone()
    vv[vv < 0] *= BETA_L
    crow = Wl.crow_indices().numpy()
    ccol = Wl.col_indices().numpy()
    rows = np.repeat(np.arange(n), np.diff(crow))
    pl = {pk: np.where(P[keep])[0] for pk, P in POOL_G.items()}
    for pk, want in S92["pool_sizes"].items():
        assert len(pl[pk]) == want, (name, pk, "pool size on substrate (STOP)")
    pall = np.unique(np.concatenate([pl[pk] for pk in pl]))
    assert len(pall) == sum(len(pl[pk]) for pk in pl), (name, "pool overlap")
    om = np.zeros(Nall)
    np.add.at(om, src_all[ei], np.abs(vals_all[ei]))
    return dict(name=name, keep=keep, loc=loc, n=n, n_edges=int(len(ei)),
                jv=np.abs(vv.numpy().astype(np.float64)), rows=rows,
                cols=ccol, pool_l=pl, pool_all=pall, om=om)


def reach_sub(c_local, sub, depth=2):
    """EXPRESSION-IDENTICAL to the certified reach() (L206 float-equality
    lesson: a float claim is a claim about the expression)."""
    x = np.zeros(sub["n"])
    x[c_local] = 1.0
    res = {}
    for d in range(1, depth + 1):
        y = np.zeros(sub["n"])
        np.add.at(y, sub["rows"], sub["jv"] * x[sub["cols"]])
        x = y
        res[d] = {pk: float(x[sub["pool_l"][pk]].sum()) for pk in sub["pool_l"]}
    return res


def power_iter_sub(sub, jv, iters=400):
    n = sub["n"]
    v = np.ones(n) / math.sqrt(n)
    lam, hist = 0.0, []
    for i in range(iters):
        w = np.zeros(n)
        np.add.at(w, sub["rows"], jv * v[sub["cols"]])
        nrm = float(np.linalg.norm(w))
        if nrm == 0.0:
            return 0.0, []
        v = w / nrm
        lam = nrm
        if i >= iters - 6:
            hist.append(nrm)
    return lam, float((max(hist) - min(hist)) / max(hist))


# ---------------- CERT-GEN (HALTING): generic == certified specialisation ---
_f4 = build_sub(keep_f4, emask_f4, "F4_f4wA")
assert _f4["n"] == NL and _f4["n_edges"] == int(emask_f4.sum())
assert np.array_equal(_f4["rows"], csr_rows), "generic CSR rows differ (STOP)"
assert np.array_equal(_f4["cols"], csr_cols), "generic CSR cols differ (STOP)"
assert np.array_equal(_f4["jv"], jv_g1), "generic |values| differ (STOP)"
for _pk in POOL_L:
    assert np.array_equal(_f4["pool_l"][_pk], POOL_L[_pk]), (_pk, "pool local")
assert list(_f4["pool_l"].keys()) == list(POOL_L.keys()), "pool key ORDER"
_rs = reach_sub(LC_CAR, _f4, 2)
_rc = reach(LC_CAR, jv_g1, depth=2)
for _d in (1, 2):
    for _pk in POOL_L:
        assert _rs[_d][_pk] == _rc[_d][_pk], (_d, _pk, "reach_sub (STOP)")
_n_gen = 2 * len(POOL_L)
# the G-scaled form must hit L178's stored values by FLOAT EQUALITY
_f4g = dict(_f4)
_f4g["jv"] = jv_abs_an
for _nm, _lc in (("carrier", LC_CAR), ("twin", LC_TWIN)):
    _rr = reach_sub(_lc, _f4g, 2)
    for _d in (1, 2):
        _pa = float(sum(_rr[_d].values()))
        assert _pa == S178["E_anatomical"]["all_actors"][_nm][f"P{_d}abs"], \
            (_nm, _d, "CERT-GEN vs L178 stored (STOP)")
        _n_gen += 1
_lam_f4, _sp_f4 = power_iter_sub(_f4g, jv_abs_an)
assert _lam_f4 == LAM1, (_lam_f4, LAM1, "power_iter_sub != certified (STOP)")
assert _sp_f4 < 1e-6
log(f"[CERT-GEN] GREEN {_n_gen} checks: generic builder/reach/power-iteration "
    f"reproduce the certified f4wA specialisation at FLOAT EQUALITY")
o["cert_gen"] = dict(n_checks=_n_gen, mode="float equality (==) / array_equal",
                     lam1_f4_via_generic=_lam_f4,
                     note="generic machinery certified on f4wA BEFORE any new "
                          "substrate was built (L44).")

# ---------------- the three substrates -------------------------------------
SUBS = {"G0_closure": build_sub(keep_new, emask_n, "G0_closure"),
        "G1_cutwA": build_sub(keep_wA, emask_wA, "G1_cutwA"),
        "F4_f4wA": _f4}
assert SUBS["G0_closure"]["n"] == int(keep_new.sum()) == S92["n_new"]
assert SUBS["G0_closure"]["n_edges"] == S92["edges_new"]
assert SUBS["G1_cutwA"]["n"] == 21785 and SUBS["G1_cutwA"]["n_edges"] == 644177
assert SUBS["F4_f4wA"]["n"] == 21789 and SUBS["F4_f4wA"]["n_edges"] == 469618
LAM = {}
for _k, _s in SUBS.items():
    if _k == "F4_f4wA":
        LAM[_k], _spr = LAM1_G1, _LI_G1["rel_spread_last6"]
    else:
        LAM[_k], _spr = power_iter_sub(_s, _s["jv"])
    assert LAM[_k] > 0 and _spr < 1e-6, (_k, "power iteration (STOP)")
    log(f"[sub] {_k}: n {_s['n']:,} edges {_s['n_edges']:,} "
        f"lam1(g=1) {LAM[_k]:.6f} (rel spread {_spr:.2e})")
o["substrates"] = {k: dict(n=v["n"], n_edges=v["n_edges"], lam1_g1=LAM[k])
                   for k, v in SUBS.items()}

# ---------------- ladders and slots ----------------------------------------
NGD = [int(x) for x in ng_desc]
NG4 = [int(x) for x in ng4]
assert len(NGD) == 58 and len(NG4) == 55
assert NGD[24] == GI_CARRIER, "carrier closure slot != 25 (STOP)"
assert NG4[20] == GI_CARRIER, "carrier f4 slot != 21 (STOP)"
LADDER_OF = {"G0_closure": ("ng_desc", NGD), "G1_cutwA": ("ng_desc", NGD),
             "F4_f4wA": ("ng4", NG4)}
PRESENT = {}
for _k, (_ln, _lad) in LADDER_OF.items():
    PRESENT[_k] = [(i + 1, g) for i, g in enumerate(_lad)
                   if SUBS[_k]["keep"][g]]
assert len(PRESENT["G0_closure"]) == 58, len(PRESENT["G0_closure"])
assert len(PRESENT["G1_cutwA"]) == 34, len(PRESENT["G1_cutwA"])
assert len(PRESENT["F4_f4wA"]) == 35, len(PRESENT["F4_f4wA"])
assert PRESENT["G1_cutwA"][0] == (25, GI_CARRIER)
assert PRESENT["F4_f4wA"][0] == (21, GI_CARRIER)
SLOT21_CLOSURE = NGD[20]
SLOT25_F4 = NG4[24]
assert SLOT21_CLOSURE != GI_CARRIER and SLOT25_F4 != GI_CARRIER
assert SUBS["G0_closure"]["keep"][SLOT21_CLOSURE]
assert SUBS["F4_f4wA"]["keep"][SLOT25_F4]
assert not SUBS["G1_cutwA"]["keep"][SLOT21_CLOSURE], \
    "slot-21 occupant unexpectedly present on cutwA (PREREG said removed)"
o["ladders"] = dict(
    carrier_gi=GI_CARRIER, carrier_slot_closure=25, carrier_slot_f4=21,
    slot21_closure_gi=SLOT21_CLOSURE, slot25_f4_gi=SLOT25_F4,
    n_present={k: len(v) for k, v in PRESENT.items()},
    ladder_of={k: v[0] for k, v in LADDER_OF.items()})


# ---------------- the statistic --------------------------------------------
def Rstat(sub, gi, lam1):
    lc = int(sub["loc"][gi])
    assert lc >= 0, (sub["name"], gi, "cell absent (STOP)")
    rr = reach_sub(lc, sub, 2)
    p2 = float(sum(rr[2].values()))
    p1 = float(sum(rr[1].values()))
    m = float(sub["om"][gi])
    return dict(gi=int(gi), P1=p1, P2=p2, m_out=m,
                R=(p2 / (lam1 ** 2 * m)) if m > 0 else None,
                R1=(p1 / (lam1 * m)) if m > 0 else None)


def pct_of(val, cohort_vals):
    """fraction of the cohort STRICTLY SMALLER (low = avoider)."""
    vs = [v for v in cohort_vals if v is not None]
    assert len(vs) >= 10, "cohort too small"
    return float(sum(1 for v in vs if v < val) / len(vs))


def rankvec(a):
    order = sorted(range(len(a)), key=lambda i: a[i])
    r = [0.0] * len(a)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and a[order[j + 1]] == a[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman_l(a, b):
    ra, rb = rankvec(a), rankvec(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return float(num / (da * db)) if da > 0 and db > 0 else None


LAD = {}
for _k in SUBS:
    rows = []
    for slot, gi in PRESENT[_k]:
        d = Rstat(SUBS[_k], gi, LAM[_k])
        d["slot"] = slot
        rows.append(d)
    LAD[_k] = rows
    log(f"[ladder] {_k}: {len(rows)} present cells measured")

# ---------------- Q1a / Q1b / Q1c ------------------------------------------
Q1 = {}
for _k in SUBS:
    vals = [r["R"] for r in LAD[_k]]
    by_gi = {r["gi"]: r for r in LAD[_k]}
    car = by_gi[GI_CARRIER]
    others = [r["R"] for r in LAD[_k] if r["gi"] != GI_CARRIER]
    Q1[_k] = dict(
        carrier_R=car["R"], carrier_slot=car["slot"],
        carrier_pct=pct_of(car["R"], others),
        cohort_n=len(vals),
        cohort_median=float(np.median([v for v in vals if v is not None])),
        cohort_min=float(min(v for v in vals if v is not None)),
        rho_slot_vs_R=spearman_l([r["slot"] for r in LAD[_k]],
                                 [r["R"] for r in LAD[_k]]),
        rho_mout_vs_R=spearman_l([r["m_out"] for r in LAD[_k]],
                                 [r["R"] for r in LAD[_k]]),
        carrier_rank_of_cohort=int(1 + sum(1 for v in vals
                                           if v is not None and v < car["R"])))
    log(f"[Q1a] {_k} slot {car['slot']}: carrier R {car['R']:.6g} "
        f"pct {Q1[_k]['carrier_pct']:.3f} (cohort med "
        f"{Q1[_k]['cohort_median']:.6g}, n {len(vals)}) | rho(slot,R) "
        f"{Q1[_k]['rho_slot_vs_R']:.4f}")

SLOTC = {}
for _tag, _k, _gi in (("slot21_closure", "G0_closure", SLOT21_CLOSURE),
                      ("slot25_f4", "F4_f4wA", SLOT25_F4)):
    by_gi = {r["gi"]: r for r in LAD[_k]}
    rr = by_gi[_gi]
    others = [r["R"] for r in LAD[_k] if r["gi"] != _gi]
    SLOTC[_tag] = dict(substrate=_k, gi=int(_gi), slot=rr["slot"], R=rr["R"],
                       pct=pct_of(rr["R"], others), m_out=rr["m_out"])
    log(f"[Q1b] {_tag} gi {_gi} slot {rr['slot']} on {_k}: R {rr['R']:.6g} "
        f"pct {SLOTC[_tag]['pct']:.3f}")

o["Q1a_carrier_by_substrate"] = Q1
o["Q1b_slot_comparators"] = SLOTC
o["Q1c_slot_structure"] = {k: dict(rho_slot_vs_R=Q1[k]["rho_slot_vs_R"],
                                   rho_mout_vs_R=Q1[k]["rho_mout_vs_R"],
                                   slot_structure=abs(Q1[k]["rho_slot_vs_R"])
                                   >= RHO_BAR) for k in Q1}

# ---------------- Q1 branch (four cells + catch-all) -----------------------
_car_all_extreme = all(Q1[k]["carrier_pct"] <= PCT_BAR for k in Q1)
_car_some_not = any(Q1[k]["carrier_pct"] > PCT_BAR for k in Q1)
_slot_pcts = [SLOTC[t]["pct"] for t in SLOTC]
_both_slots_mid = all(PCT_BAR < p < 1 - PCT_BAR for p in _slot_pcts)
_both_slots_extreme = all(p <= PCT_BAR for p in _slot_pcts)
_any_slot_extreme = any(p <= PCT_BAR for p in _slot_pcts)
_no_slot_extreme = all(p > PCT_BAR for p in _slot_pcts)
if _car_all_extreme and _both_slots_mid:
    BR1 = "B_CELL"
elif _car_some_not and _both_slots_extreme:
    BR1 = "B_SLOT"
elif _car_all_extreme and _any_slot_extreme:
    BR1 = "B_BOTH"
elif _car_some_not and _no_slot_extreme:
    BR1 = "B_NEITHER"
else:
    BR1 = "UNREGISTERED_SHAPE"
log(f"[Q1] BRANCH {BR1} (carrier pct "
    + " ".join(f"{k}:{Q1[k]['carrier_pct']:.3f}" for k in Q1)
    + " | slots " + " ".join(f"{t}:{SLOTC[t]['pct']:.3f}" for t in SLOTC) + ")")

# ---------------- Q2: the contralateral homolog ----------------------------
_hom = json.load(open("l169c/static.json"))["P2_hom_identity"]["identity"]
assert int(_hom["gi"]) == GI_MIR and _hom["cell_type"] == "DNp33"
_arow = ann[ann.gi == GI_MIR]
_crow_ann = ann[ann.gi == GI_CARRIER]
assert len(_arow) == 1 and len(_crow_ann) == 1
MIR_ID = dict(gi=GI_MIR, cell_type=str(_arow.cell_type.iloc[0]),
              side=str(_arow.side.iloc[0]),
              super_class=str(_arow.super_class.iloc[0]),
              nt=str(_arow.neurotransmitter_predicted.iloc[0]))
CAR_ID = dict(gi=GI_CARRIER, cell_type=str(_crow_ann.cell_type.iloc[0]),
              side=str(_crow_ann.side.iloc[0]),
              super_class=str(_crow_ann.super_class.iloc[0]),
              nt=str(_crow_ann.neurotransmitter_predicted.iloc[0]))
assert MIR_ID["cell_type"] == _hom["cell_type"], "annotation/l169c drift (STOP)"
_homology_ok = (CAR_ID["cell_type"] == MIR_ID["cell_type"]
                and CAR_ID["side"] != MIR_ID["side"])
log(f"[Q2] carrier {CAR_ID} | mirror {MIR_ID} | homology_ok {_homology_ok}")


def matched_cohort(sub, gi, k=COHORT_K):
    pres = np.where(sub["keep"] & dn_all)[0]
    pres = pres[sub["om"][pres] > 0]
    pres = pres[~np.isin(pres, [GI_CARRIER, GI_MIR])]
    tgt = math.log(float(sub["om"][gi]))
    d = np.abs(np.log(sub["om"][pres]) - tgt)
    sel = pres[np.argsort(d, kind="stable")[:k]]
    assert len(sel) == k, (sub["name"], "cohort short")
    return [int(x) for x in sel]


Q2 = {}
for _k, _s in SUBS.items():
    if not _s["keep"][GI_MIR]:
        Q2[_k] = dict(absent=True)
        continue
    r_mir = Rstat(_s, GI_MIR, LAM[_k])
    r_car = Rstat(_s, GI_CARRIER, LAM[_k])
    coh_m = matched_cohort(_s, GI_MIR)
    coh_c = matched_cohort(_s, GI_CARRIER)
    coh_u = sorted(set(coh_m) | set(coh_c))
    cv = {g: Rstat(_s, g, LAM[_k])["R"] for g in coh_u}
    Q2[_k] = dict(
        absent=False, mirror_R=r_mir["R"], carrier_R=r_car["R"],
        mirror_m_out=r_mir["m_out"], carrier_m_out=r_car["m_out"],
        mirror_pct=pct_of(r_mir["R"], [cv[g] for g in coh_m]),
        carrier_pct=pct_of(r_car["R"], [cv[g] for g in coh_c]),
        cohort_k=COHORT_K, cohort_union_n=len(coh_u),
        cohort_median_mirror=float(np.median([cv[g] for g in coh_m])),
        cohort_median_carrier=float(np.median([cv[g] for g in coh_c])),
        mass_match_logspread_mirror=float(np.max(np.abs(
            np.log([_s["om"][g] for g in coh_m])
            - math.log(r_mir["m_out"])))),
        mass_match_logspread_carrier=float(np.max(np.abs(
            np.log([_s["om"][g] for g in coh_c])
            - math.log(r_car["m_out"])))))
    log(f"[Q2] {_k}: mirror R {r_mir['R']:.6g} pct {Q2[_k]['mirror_pct']:.3f} "
        f"| carrier R {r_car['R']:.6g} pct {Q2[_k]['carrier_pct']:.3f} "
        f"(mass-matched cohorts, k={COHORT_K})")

_mp = [Q2[k]["mirror_pct"] for k in Q2 if not Q2[k]["absent"]]
if sum(1 for p in _mp if p <= PCT_BAR) >= 2:
    BR2 = "M_AVOIDS"
elif sum(1 for p in _mp if PCT_BAR < p < 1 - PCT_BAR) >= 2:
    BR2 = "M_TYPICAL"
elif sum(1 for p in _mp if p >= 1 - PCT_BAR) >= 2:
    BR2 = "M_HIGH"
else:
    BR2 = "M_MIXED"
log(f"[Q2] BRANCH {BR2} (mirror pcts {['%.3f' % p for p in _mp]})")
o["Q2_mirror"] = dict(branch=BR2, carrier_identity=CAR_ID,
                      mirror_identity=MIR_ID, homology_ok=bool(_homology_ok),
                      per_substrate=Q2,
                      null_kind="MASS-MATCHED COHORT percentile (100 nearest "
                                "present descending cells in log out-mass), "
                                "NOT the l169c degree-neutral rewire null")

# ---------------- Q3: the v783 handle (exploratory) ------------------------
_m783_car = _crow_ann.fafb_783_match_id.iloc[0]
_m783_mir = _arow.fafb_783_match_id.iloc[0]
_has_car = bool(pd.notna(_m783_car)) and str(_m783_car).strip() not in ("", "0")
_has_mir = bool(pd.notna(_m783_mir)) and str(_m783_mir).strip() not in ("", "0")
_n_motor_leg = int(((sup == "motor")).sum())
o["Q3_v783_handle"] = dict(
    carrier_has_match=_has_car, carrier_match_id=str(_m783_car),
    mirror_has_match=_has_mir, mirror_match_id=str(_m783_mir),
    banc_motor_cells_annotated=_n_motor_leg,
    verdict="UNANSWERABLE-BY-VOLUME",
    note="v783 is a BRAIN-ONLY volume: it contains no leg motor neurons and "
         "no VNC premotor pools, so the readout this card's statistic is "
         "defined against has NO counterpart there. A present match id "
         "identifies the cell but cannot carry the measurement, so the "
         "cross-connectome leg is SLICED to its own item rather than "
         "answered with a substituted statistic (L78 non-transport law "
         "would in any case make it exploratory).",
    exploratory=True)
log(f"[Q3] carrier v783 match {_has_car} ({_m783_car}) | mirror {_has_mir} "
    f"({_m783_mir}) -> UNANSWERABLE-BY-VOLUME, sliced")

# ---------------- predictions, scored --------------------------------------
o["predictions"] = dict(
    Q207_1=dict(registered="B_CELL", measured=BR1, correct=BR1 == "B_CELL"),
    Q207_2=dict(registered="|rho(slot,R)| < 0.5 on all three",
                measured={k: Q1[k]["rho_slot_vs_R"] for k in Q1},
                correct=all(abs(Q1[k]["rho_slot_vs_R"]) < RHO_BAR for k in Q1)),
    Q207_3=dict(registered="M_AVOIDS", measured=BR2, correct=BR2 == "M_AVOIDS"),
    Q207_4=dict(registered="Q3 UNANSWERABLE-BY-VOLUME", measured=True,
                correct=True))
o["n_predictions_correct"] = int(sum(1 for v in o["predictions"].values()
                                     if v["correct"]))

o["branches"] = dict(Q1=BR1, Q2=BR2)
o["bars"] = dict(pct_extreme=PCT_BAR, rho_slot=RHO_BAR, cohort_k=COHORT_K)
o["ladder_table"] = {k: [dict(slot=r["slot"], gi=r["gi"], R=r["R"],
                              R1=r["R1"], m_out=r["m_out"], P2=r["P2"])
                         for r in LAD[k]] for k in LAD}
o["limitations"] = [
    "ANATOMICAL leg only: no row mask, no settle, no seed — this is wiring "
    "geometry and NOT an operating point (L164).",
    "Operator powers are walks WITH revisits, not paths.",
    "The Crofts/Estrada second leg is NOT run (PREREG-disclosed): the "
    "strength normalisation is not neutral under a substrate change, and "
    "L206 already reported it agrees in ORDER on f4wA.",
    "The cohorts differ in SIZE across substrates (58 / 34 / 35 present "
    "ladder cells), so a percentile has coarser resolution on the smaller "
    "ones (1/34 = 0.029).",
    "The mirror leg uses a MASS-MATCHED COHORT percentile, not the l169c "
    "degree-neutral rewire null that L206 used for the carrier; the two are "
    "different nulls and are never compared as if they were the same.",
    "The closure and cutwA substrates share one ladder (ng_desc, no syn "
    "floor) while f4wA has its own (ng4, syn>=4): each substrate is scored "
    "against the ladder it was derived with, which is why the carrier's slot "
    "differs (25 vs 21) — that difference IS the design, not a confound.",
    "Q3 is exploratory and structurally unanswerable on this volume pair.",
]
o["pins"] = "ALL GREEN"
json.dump(o, open("l207/static.json", "w"), indent=1)
log(f"[done] wrote l207/static.json in {time.time() - t0:.1f}s | "
    f"Q1 {BR1} | Q2 {BR2} | predictions {o['n_predictions_correct']}/4")
