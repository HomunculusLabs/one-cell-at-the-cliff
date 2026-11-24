
# ===================== L222b ADDENDUM TAIL =================================
# POST-HOC, declared as such, no branch depends on it. Everything above is the
# VERBATIM l222_static.py prefix (lines 1-906), so CERT-783 / CERT-L207 /
# CERT-212 (139) / CERT-FLOORGEN (15) / CERT-MONOTONE (6) / CERT-MV /
# CERT-GATE all re-ran before this line.
#
# QUESTION: l222's LOCAL floor deleted ~6,951 weak edges into the motor
# readout at once. Is the mirror's ONE direct motor synapse itself causally
# relevant to its percentile, or was L212's P1 = log1p(1) a coincidence
# sitting next to the finding?

oa = {}
oa["design"] = ("L222b: delete EXACTLY the mirror's single direct motor edge "
                "and nothing else. POST-HOC addendum to L222.")
oa["parent"] = dict(script="l222_static.py", prefix_lines=906,
                    note="generated as a literal PREFIX slice; the parent's "
                         "static.json is never opened for writing.")

# the target edge, re-derived from the raw pair arrays (not read from the json)
_tgt = np.where((src_all == GI_MIR) & MOT_MASK[dst_all])[0]
assert len(_tgt) == 1, (len(_tgt), "expected exactly ONE mirror motor edge")
E_IDX = int(_tgt[0])
assert float(w_syn[E_IDX]) == 1.0, (float(w_syn[E_IDX]), "not one synapse")
_car_tgt = np.where((src_all == GI_CARRIER) & MOT_MASK[dst_all])[0]
assert len(_car_tgt) == 0, (len(_car_tgt), "carrier has a direct motor edge?")
oa["target_edge"] = dict(
    edge_index=E_IDX, src_gi=int(src_all[E_IDX]), dst_gi=int(dst_all[E_IDX]),
    syn_count=float(w_syn[E_IDX]), dst_root_id=str(int(ids_all[dst_all[E_IDX]])),
    dst_cell_type=str(_ct_full[dst_all[E_IDX]]),
    dst_nerve=str(_nv_full[dst_all[E_IDX]]), dst_side=str(_sd_full[dst_all[E_IDX]]))
log(f"[target] {oa['target_edge']}")


def build_drop(beta, pools, name, drop_idx):
    """build_v783's EXPRESSION with an explicit edge-index DROP SET.
    drop_idx empty is a provable no-op, which is how this builder is gated."""
    keep_e = np.ones(len(w_syn), bool)
    keep_e[np.asarray(drop_idx, dtype=np.int64)] = False
    s_e = src_all[keep_e]
    d_e = dst_all[keep_e]
    _sa = sign_all[s_e]
    _sb = np.where(is_glut[s_e], -np.abs(_sa), _sa)
    ev = (np.log1p(w_syn[keep_e]) * _sb).astype(np.float64)
    vv = ev.copy()
    vv[vv < 0] *= beta
    jv = np.abs(vv)
    om = np.zeros(Nall)
    np.add.at(om, s_e, jv)
    pl = {pk: np.where(P)[0] for pk, P in pools.items()}
    return dict(name=name, keep=np.ones(Nall, bool),
                loc=np.arange(Nall, dtype=np.int64), n=Nall,
                n_edges=int(keep_e.sum()), jv=jv, rows=d_e, cols=s_e,
                pool_l=pl, om=om,
                pool_all=np.unique(np.concatenate([pl[k] for k in pl])))


# CERT-DROPGEN (HALTING): the empty drop set IS the verbatim build_v783
_g0 = build_drop(BETA_L, POOL_G, "drop_none", [])
n_dg = 0
for _k in ("jv", "rows", "cols", "om"):
    assert np.array_equal(_g0[_k], SUB[_k]), (_k, "CERT-DROPGEN (STOP)")
    n_dg += 1
assert _g0["n_edges"] == NEDGE, "CERT-DROPGEN n_edges (STOP)"
n_dg += 1
for _pk in SUB["pool_l"]:
    assert np.array_equal(_g0["pool_l"][_pk], SUB["pool_l"][_pk]), (_pk, "STOP")
    n_dg += 1
oa["cert_dropgen"] = dict(n_checks=n_dg, mode="EXACT array_equal (==)")
log(f"[CERT-DROPGEN] GREEN {n_dg} exact array equalities")
del _g0

SUBD = build_drop(BETA_L, POOL_G, "drop_one_synapse", [E_IDX])
assert SUBD["n_edges"] == NEDGE - 1, (SUBD["n_edges"], "drop count (STOP)")
# The drop must move EXACTLY ONE cell's out-mass, by log1p(1). But om is a
# np.add.at accumulation over 31 edges, so the DIFFERENCE OF TWO SUMS is not
# bit-identical to the removed summand (the L218 law: a mathematical no-op is
# not a floating-point no-op). The bar is DERIVED from the operand's own ulp,
# never fixed in advance (the L216 law).
_d_om = SUB["om"] - SUBD["om"]
_want = math.log1p(1.0)
_ulp = float(np.spacing(float(SUB["om"][GI_MIR])))
_err = abs(float(_d_om[GI_MIR]) - _want)
assert _err <= 4.0 * _ulp, (_err, _ulp, "drop mass (STOP)")
assert int((_d_om != 0.0).sum()) == 1, (int((_d_om != 0.0).sum()),
                                        "the drop touched more than one cell")
oa["cert_drop_mass"] = dict(d_om_mirror=float(_d_om[GI_MIR]), want=_want,
                            abs_err=_err, ulp_of_om=_ulp,
                            err_in_ulp=(_err / _ulp), bar_ulp=4.0,
                            note="difference-of-sums vs summand: bar derived "
                                 "from np.spacing(om), not fixed (L216/L218)")
log(f"[drop] exactly one edge, one cell's out-mass moved by "
    f"{float(_d_om[GI_MIR]):.15f} vs log1p(1) {_want:.15f} "
    f"(err {_err:.3e} = {_err/_ulp:.2f} ulp of om)")

LAMD, SPRD = power_iter_fast(SUBD, SUBD["jv"], 400)
assert SPRD < 1e-6, (SPRD, "power iteration (STOP)")
RCD = Rfast(SUBD, GI_CARRIER, LAMD)
RMD = Rfast(SUBD, GI_MIR, LAMD)
assert RCD["P1"] == 0.0, (RCD["P1"], "carrier P1 (STOP)")
CCD = matched_cohort(SUBD, GI_CARRIER)
CMD = matched_cohort(SUBD, GI_MIR)
CUD = sorted(set(CCD) | set(CMD))
CVD = {g: Rfast(SUBD, g, LAMD)["R"] for g in CUD}
LD = leg(RCD, RMD, CCD, CMD, CVD, SUBD)
_vu = [CVD[g] for g in CUD]
LD["pct_carrier_union"] = pct_of(RCD["R"], _vu)
LD["pct_mirror_union"] = pct_of(RMD["R"], _vu)
LD["gap_union"] = abs(LD["pct_mirror_union"] - LD["pct_carrier_union"])
LD["gap"] = abs(LD["mirror_pct"] - LD["carrier_pct"])
LD["ratio_R"] = float(RMD["R"] / RCD["R"])
LD["ratio_P2"] = float(RMD["P2"] / RCD["P2"])
LD["lam1"] = float(LAMD)
LD["rel_spread_last6"] = float(SPRD)
LD["n_edges"] = int(SUBD["n_edges"])
LD["cohort_jaccard_carrier_vs_f1"] = float(
    len(set(CCD) & set(COH_C)) / len(set(CCD) | set(COH_C)))
LD["cohort_jaccard_mirror_vs_f1"] = float(
    len(set(CMD) & set(COH_M)) / len(set(CMD) | set(COH_M)))
oa["drop_one"] = LD

# the paired comparison against the UNFLOORED parent state (CERT-212-certified)
BASE = dict(carrier_pct=o["Q1_primary"]["carrier_pct"],
            mirror_pct=o["Q1_primary"]["mirror_pct"],
            gap=abs(o["Q1_primary"]["mirror_pct"] - o["Q1_primary"]["carrier_pct"]),
            carrier_R=o["Q1_primary"]["carrier_R"],
            mirror_R=o["Q1_primary"]["mirror_R"],
            carrier_P1=o["Q1_primary"]["carrier_P1"],
            mirror_P1=o["Q1_primary"]["mirror_P1"],
            carrier_P2=o["Q1_primary"]["carrier_P2"],
            mirror_P2=o["Q1_primary"]["mirror_P2"],
            ratio_R=float(o["Q1_primary"]["mirror_R"] / o["Q1_primary"]["carrier_R"]),
            ratio_P2=float(o["Q1_primary"]["mirror_P2"] / o["Q1_primary"]["carrier_P2"]),
            lam1=float(LAM1))
oa["baseline_unfloored"] = BASE
oa["delta"] = dict(
    d_mirror_pct=LD["mirror_pct"] - BASE["mirror_pct"],
    d_carrier_pct=LD["carrier_pct"] - BASE["carrier_pct"],
    d_gap=LD["gap"] - BASE["gap"],
    d_ratio_R=LD["ratio_R"] - BASE["ratio_R"],
    d_ratio_P2=LD["ratio_P2"] - BASE["ratio_P2"],
    d_mirror_P2=LD["mirror_P2"] - BASE["mirror_P2"],
    d_mirror_P1=LD["mirror_P1"] - BASE["mirror_P1"],
    d_lam1=float(LAMD) - BASE["lam1"],
    frac_of_mirror_P2_lost=float((BASE["mirror_P2"] - LD["mirror_P2"])
                                 / BASE["mirror_P2"]))
# the registered-style read: does deleting the one synapse CLOSE the break?
_closes = bool(LD["gap"] < BASE["gap"] and LD["ratio_R"] < BASE["ratio_R"])
oa["verdict"] = dict(
    one_synapse_closes_the_break=_closes,
    direction=("the gap MOVED TOWARD symmetry" if LD["gap"] < BASE["gap"]
               else "the gap WIDENED or held"),
    reading=("L212's P1 = log1p(1) coincidence is NOT the mechanism of the "
             ".020 / .250 split: deleting exactly that synapse does not close "
             "it." if not _closes else
             "the single synapse is causally load-bearing for the split."))
oa["limitations"] = [
    "POST-HOC: this leg was not in L222's PREREG; it is reported as "
    "DESCRIPTIVE and no L222 branch depends on it.",
    "A one-edge deletion is a static anatomical perturbation, not a lesion "
    "experiment: no settle, no seed, no rollouts (L164).",
    "The mirror's depth-1 motor arrival is carried ENTIRELY by this edge, so "
    "d_mirror_P1 is exactly -log1p(1) BY CONSTRUCTION and is a gate on the "
    "drop, never a finding.",
    "Every L222 and L212 limitation is inherited verbatim.",
]
log(f"[DROP] gap {BASE['gap']:.3f} -> {LD['gap']:.3f} "
    f"(d {oa['delta']['d_gap']:+.3f}) | ratio_R {BASE['ratio_R']:.4f} -> "
    f"{LD['ratio_R']:.4f} | mirror pct {BASE['mirror_pct']:.3f} -> "
    f"{LD['mirror_pct']:.3f} | mirror P2 {BASE['mirror_P2']:.4f} -> "
    f"{LD['mirror_P2']:.4f} ({oa['delta']['frac_of_mirror_P2_lost']*100:.3f}% lost)")
log(f"[DROP] closes_the_break={_closes}")
oa["parent_gates_reran"] = dict(cert_212=o["cert_212"]["n_checks"],
                                cert_floorgen=o["cert_floorgen"]["n_checks"],
                                cert_monotone=o["cert_monotone"]["n_checks"],
                                cert_783=o["cert_783"]["n_checks"],
                                cert_mv=o["cert_mv"]["n_checks"],
                                cert_gate=o["cert_gate"]["n_checks"],
                                cert_l207=o["cert_l207"]["n_checks"])
oa["runtime_s"] = time.time() - T0
json.dump(oa, open(f"{OUT}/addendum.json", "w"), indent=1)
log(f"[done] addendum {oa['runtime_s']:.1f}s -> {OUT}/addendum.json")
