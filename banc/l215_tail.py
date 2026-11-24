# ================= L215 TAIL (appended by l215_build.py) =================
# Everything above this line is l151_static.py lines 1-319 VERBATIM (every
# L151/L142/L134/L92/L101 pin re-ran as free certification) plus l178_tail.py
# lines 22-83 VERBATIM (CERT-F4: the f4 ladder re-derivation and the stored
# float-equality gain leg). No lab module was imported (L175 lesson).
# PREREG: l215/PREREG.md (registered first). Writes l215/static.json ONLY.
# Zero rollouts, zero settles, zero dynamics. RNG: the membership permutation
# null ONLY, seeded.
import os

NDRAW = 2000
SEED_PERM = 21521
JOINTS = ("Ti", "Tr")

log("=" * 72)
log(f"[L215] resurrection static | NDRAW {NDRAW} seed {SEED_PERM}")

# ---------------- substrates: the two the card names -----------------------
SUB = {
    "cutwA": (emask_wA, keep_wA),
    "f4wA": (emask_f4, keep_f4),
}
E_ELIG = emask_wA & pm4          # node-matched floor comparator (disclosed)
E_REMOVED = emask_wA & ~pm4      # the sub-floor edges the floor strips
assert int(SUB["cutwA"][0].sum()) == 644177, "cutwA edges (STOP)"
assert int(SUB["f4wA"][0].sum()) == 469618, "f4wA edges (STOP)"
assert int(E_ELIG.sum()) == 469256, "floor-eligible wA edges (STOP)"
assert int(E_ELIG.sum()) + int(E_REMOVED.sum()) == 644177, "partition (STOP)"
assert int(keep_wA.sum()) == 21785 and int(keep_f4.sum()) == 21789
log(f"[pins] substrates GREEN | cutwA {int(emask_wA.sum()):,} "
    f"f4wA {int(emask_f4.sum()):,} elig {int(E_ELIG.sum()):,} "
    f"removed {int(E_REMOVED.sum()):,}")

# ---------------- CERT-G: the two bisected gains, FLOAT EQUALITY -----------
_zg = np.load("l169b2/raw_l169b2.npz", allow_pickle=True)
G_CUTWA = float(_zg["g_cutwA"])
G_F4WA2 = float(_zg["g_f4wA"])
del _zg
assert G_CUTWA == 0.14365819573402408, (G_CUTWA, "g_cutwA drift (STOP)")
assert G_F4WA2 == 0.15051452517509462, (G_F4WA2, "g_f4wA drift (STOP)")
assert G_F4WA2 == G_F4WA, "HEAD2 gain disagrees with CERT-G (STOP)"
GAIN = {"cutwA": G_CUTWA, "f4wA": G_F4WA2}
log(f"[CERT-G] GREEN g_cutwA {G_CUTWA!r} g_f4wA {G_F4WA2!r} "
    f"ratio {G_F4WA2/G_CUTWA:.5f}")

# ---------------- pools: per-side cell lists (L205 GROUPS convention) ------
POOLSZ = S92["pool_sizes"]
GROUPS = {}
for J in JOINTS:
    for g in ("f", "e"):
        cl = np.where(POOL_G[f"{J}_{g}L"])[0]
        cr = np.where(POOL_G[f"{J}_{g}R"])[0]
        assert len(cl) == POOLSZ[f"{J}_{g}L"] and len(cr) == POOLSZ[f"{J}_{g}R"]
        assert len(np.intersect1d(cl, cr)) == 0, (J, g, "side overlap (STOP)")
        cells = np.concatenate([cl, cr])
        isL = np.zeros(len(cells), bool)
        isL[:len(cl)] = True
        GROUPS[(J, g)] = (cells, isL)
for sname, (E, keep) in SUB.items():
    for pk, want in POOLSZ.items():
        assert int((POOL_G[pk] & keep).sum()) == want, (sname, pk, "pool size")
log("[pins] pool sizes invariant on both substrates GREEN")

SIDEMASK = {}            # (J, side) -> bool mask over Nall
NCELL = {}
for J in JOINTS:
    cf, isLf = GROUPS[(J, "f")]
    ce, isLe = GROUPS[(J, "e")]
    for side, sf, se in (("L", isLf, isLe), ("R", ~isLf, ~isLe)):
        t = np.zeros(Nall, bool)
        t[cf[sf]] = True
        t[ce[se]] = True
        SIDEMASK[(J, side)] = t
        NCELL[(J, side)] = int(t.sum())
        assert NCELL[(J, side)] == int(sf.sum()) + int(se.sum())


# ---------------- CERT-205: reproduce l205 c4_floor_retention EXACTLY ------
S205 = json.load(open("l205/static.json"))
_fp205 = os.stat("l205/static.json")
_FP205 = (_fp205.st_size, _fp205.st_mtime_ns)
C4_cert = 0
for J in JOINTS:
    stored = S205["c4_floor_retention"][J]
    for side in ("L", "R"):
        tgt = SIDEMASK[(J, side)]
        e_all = emask_wA & tgt[dst_all]
        e_f4 = e_all & pm4
        m_all = float(np.abs(vals_all[e_all]).sum())
        m_f4 = float(np.abs(vals_all[e_f4]).sum())
        got = dict(n_edges_cutwA=int(e_all.sum()),
                   n_edges_floor_eligible=int(e_f4.sum()),
                   edge_retention=float(e_f4.sum() / e_all.sum()),
                   mass_cutwA=m_all, mass_floor_eligible=m_f4,
                   mass_retention=m_f4 / m_all,
                   median_syn=float(np.median(w_syn[e_all])),
                   frac_syn_lt4=float((w_syn[e_all] < FLOOR).mean()))
        for k, v in got.items():
            assert v == stored[side][k], ("CERT-205", J, side, k, v,
                                          stored[side][k], "(STOP)")
            C4_cert += 1
    rr_e = stored["L"]["edge_retention"] / stored["R"]["edge_retention"]
    rr_m = stored["L"]["mass_retention"] / stored["R"]["mass_retention"]
    assert rr_e == stored["edge_retention_ratio_L_over_R"], (J, "rr_e")
    assert rr_m == stored["mass_retention_ratio_L_over_R"], (J, "rr_m")
    C4_cert += 2
assert C4_cert == 36, (C4_cert, "CERT-205 count (STOP)")
assert S205["c4_floor_retention"]["Tr"]["edge_retention_ratio_L_over_R"] == \
    1.013747143709093, "C4 Tr ratio drift (STOP)"
assert S205["c4_floor_retention"]["Ti"]["edge_retention_ratio_L_over_R"] == \
    0.9796818164438116, "C4 Ti ratio drift (STOP)"
log(f"[CERT-205] GREEN {C4_cert} float equalities (c4_floor_retention)")


# ---------------- CERT-TBL: reproduce l205 table M_* / A_cell EXACTLY ------
def _asym(a, b):
    t = a + b
    return float((a - b) / t) if t else None


TBL_cert = 0
for J in JOINTS:
    cf, isLf = GROUPS[(J, "f")]
    ce, isLe = GROUPS[(J, "e")]
    for sname in ("cutwA", "f4wA"):
        E = SUB[sname][0]
        im = np.zeros(Nall)
        np.add.at(im, dst_all[E], np.abs(vals_all[E]))
        mf, me = im[cf], im[ce]
        ML = float(mf[isLf].sum() + me[isLe].sum())
        MR = float(mf[~isLf].sum() + me[~isLe].sum())
        nL = int(isLf.sum()) + int(isLe.sum())
        nR = len(cf) + len(ce) - nL
        got = dict(M_L=ML, M_R=MR,
                   M_fL=float(mf[isLf].sum()), M_fR=float(mf[~isLf].sum()),
                   M_eL=float(me[isLe].sum()), M_eR=float(me[~isLe].sum()),
                   A_cell=_asym(ML / nL, MR / nR))
        st = S205["table"][J][sname]
        for k, v in got.items():
            assert v == st[k], ("CERT-TBL", J, sname, k, v, st[k], "(STOP)")
            TBL_cert += 1
assert TBL_cert == 28, (TBL_cert, "CERT-TBL count (STOP)")
log(f"[CERT-TBL] GREEN {TBL_cert} float equalities (table M_*/A_cell)")

# ---------------- L208 premise asserts (halting) ---------------------------
S208 = json.load(open("l208/static.json"))
_fp208 = os.stat("l208/static.json")
_FP208 = (_fp208.st_size, _fp208.st_mtime_ns)
A208 = json.load(open("l208/addendum_floor.json"))
_fpA = os.stat("l208/addendum_floor.json")
_FPA = (_fpA.st_size, _fpA.st_mtime_ns)
assert S208["branch"] == "H_UNREGISTERED_SHAPE", "L208 branch drift (STOP)"
assert A208["label"].startswith("POST-HOC, UNREGISTERED"), "L208 add label (STOP)"
log("[premise] L208 branch + POST-HOC label GREEN")
log(f"[CERT total] {C4_cert + TBL_cert + 2} float equalities before any "
    f"L215 statistic")


# ================= L215 MEASUREMENT =========================================
def signed_in(E, tgt):
    """(Mp, Mm, n_edges) for edge set E into bool target mask tgt."""
    sel = E & tgt[dst_all]
    v = vals_all[sel]
    return (float(v[v > 0].sum()), float(-v[v < 0].sum()), int(sel.sum()))


ROWS = {}
for J in JOINTS:
    for side in ("L", "R"):
        tgt = SIDEMASK[(J, side)]
        n = NCELL[(J, side)]
        r = {"n_cells": n}
        for sname in ("cutwA", "f4wA"):
            Mp, Mm, ne = signed_in(SUB[sname][0], tgt)
            r[sname] = dict(Mp=Mp, Mm=Mm, NET=Mp - Mm, TOT=Mp + Mm,
                            n_edges=ne,
                            NET_per_cell=(Mp - Mm) / n,
                            NET_gain=GAIN[sname] * (Mp - Mm) / n,
                            inh_frac=Mm / (Mp + Mm))
        Ep, Em, ene = signed_in(E_ELIG, tgt)
        r["elig_nodematched"] = dict(Mp=Ep, Mm=Em, NET=Ep - Em, TOT=Ep + Em,
                                     n_edges=ene)
        Rp, Rm, rne = signed_in(E_REMOVED, tgt)
        r["removed"] = dict(Rp=Rp, Rm=Rm, NET=Rp - Rm, TOT=Rp + Rm,
                            n_edges=rne,
                            frac_of_exc=Rp / r["cutwA"]["Mp"],
                            frac_of_inh=Rm / r["cutwA"]["Mm"],
                            inh_frac=Rm / (Rp + Rm))
        # partition identity: cutwA == eligible + removed, EXACT to 1e-9
        assert abs((Ep + Rp) - r["cutwA"]["Mp"]) < 1e-9, (J, side, "Mp split")
        assert abs((Em + Rm) - r["cutwA"]["Mm"]) < 1e-9, (J, side, "Mm split")
        assert ene + rne == r["cutwA"]["n_edges"], (J, side, "edge split")
        r["ret"] = r["f4wA"]["TOT"] / r["cutwA"]["TOT"]
        r["ret_nodematched"] = r["elig_nodematched"]["TOT"] / r["cutwA"]["TOT"]
        ROWS[f"{J}_{side}"] = r
        log(f"[row {J}_{side}] n {n} | cutwA Mp {r['cutwA']['Mp']:.1f} "
            f"Mm {r['cutwA']['Mm']:.1f} NET {r['cutwA']['NET']:.1f} | "
            f"f4wA Mp {r['f4wA']['Mp']:.1f} Mm {r['f4wA']['Mm']:.1f} "
            f"NET {r['f4wA']['NET']:.1f} | removed inh_frac "
            f"{r['removed']['inh_frac']:.4f} | ret {r['ret']:.5f}")

# ---------------- Q1: BULK side-symmetry -----------------------------------
ratio_ret_Tr = ROWS["Tr_L"]["ret"] / ROWS["Tr_R"]["ret"]
ratio_ret_Ti = ROWS["Ti_L"]["ret"] / ROWS["Ti_R"]["ret"]
BULK_SYMMETRIC = abs(ratio_ret_Tr - 1.0) <= 0.05
Q1 = dict(ret_Tr_L=ROWS["Tr_L"]["ret"], ret_Tr_R=ROWS["Tr_R"]["ret"],
          ratio_Tr=ratio_ret_Tr, ret_Ti_L=ROWS["Ti_L"]["ret"],
          ret_Ti_R=ROWS["Ti_R"]["ret"], ratio_Ti=ratio_ret_Ti,
          BULK_SYMMETRIC=bool(BULK_SYMMETRIC), bar=0.05)
log(f"[Q1] ret Tr L {ratio_ret_Tr:.5f} Ti {ratio_ret_Ti:.5f} | "
    f"BULK_SYMMETRIC {BULK_SYMMETRIC}")

# ---------------- Q2: sign-neutral counterfactual --------------------------
Q2 = {}
for key, r in ROWS.items():
    n = r["n_cells"]
    NETc = r["cutwA"]["NET"]
    NETf = r["f4wA"]["NET"]
    NETpred = NETc * r["ret"]
    dact = GAIN["f4wA"] * NETf / n - GAIN["cutwA"] * NETc / n
    dpred = GAIN["f4wA"] * NETpred / n - GAIN["cutwA"] * NETc / n
    S_sign = (dact - dpred) / dact if dact else None
    # raw (ungained) twin, reported so the gain's contribution is visible
    dact_raw = (NETf - NETc) / n
    dpred_raw = (NETpred - NETc) / n
    S_sign_raw = (dact_raw - dpred_raw) / dact_raw if dact_raw else None
    degen_bar = 0.01 * GAIN["cutwA"] * r["cutwA"]["TOT"] / n
    degen = abs(dact) < degen_bar
    bulk_acc = (S_sign is not None) and abs(S_sign) < 0.25
    dir_conf = r["removed"]["frac_of_inh"] > r["removed"]["frac_of_exc"]
    sign_acc = (S_sign is not None) and S_sign >= 0.50 and dir_conf
    Q2[key] = dict(NET_cutwA=NETc, NET_f4wA=NETf, NET_pred=NETpred,
                   dNET_act=dact, dNET_pred=dpred, S_sign=S_sign,
                   dNET_act_raw=dact_raw, S_sign_raw=S_sign_raw,
                   degen_bar=degen_bar, D_DEGENERATE=bool(degen),
                   frac_of_exc=r["removed"]["frac_of_exc"],
                   frac_of_inh=r["removed"]["frac_of_inh"],
                   dir_confirm=bool(dir_conf),
                   BULK_ACCOUNTS=bool(bulk_acc), SIGN_ACCOUNTS=bool(sign_acc))
    log(f"[Q2 {key}] NET {NETc:.1f} -> {NETf:.1f} pred {NETpred:.1f} | "
        f"dact {dact:+.5f} dpred {dpred:+.5f} S_sign "
        f"{'None' if S_sign is None else format(S_sign, '+.4f')} | "
        f"rem exc {r['removed']['frac_of_exc']:.4f} inh "
        f"{r['removed']['frac_of_inh']:.4f} dir {dir_conf} | "
        f"BULK {bulk_acc} SIGN {sign_acc} DEGEN {degen}")

# ---------------- Q2b: relu-crossing check ---------------------------------
CROSSES = (Q2["Tr_L"]["NET_cutwA"] <= 0) and (Q2["Tr_L"]["NET_f4wA"] > 0)
Q2b = dict(NET_cutwA_Tr_L=Q2["Tr_L"]["NET_cutwA"],
           NET_f4wA_Tr_L=Q2["Tr_L"]["NET_f4wA"], CROSSES=bool(CROSSES))
log(f"[Q2b] Tr_L NET cutwA {Q2b['NET_cutwA_Tr_L']:.2f} f4wA "
    f"{Q2b['NET_f4wA_Tr_L']:.2f} | CROSSES {CROSSES}")

# ---------------- Q3: specificity on Ti ------------------------------------
SILENT_ON_Ti = (Q2["Ti_L"]["S_sign"] is not None
                and Q2["Ti_R"]["S_sign"] is not None
                and abs(Q2["Ti_L"]["S_sign"]) < 0.25
                and abs(Q2["Ti_R"]["S_sign"]) < 0.25)
Q3 = dict(S_sign_Ti_L=Q2["Ti_L"]["S_sign"], S_sign_Ti_R=Q2["Ti_R"]["S_sign"],
          SILENT_ON_Ti=bool(SILENT_ON_Ti))
log(f"[Q3] SILENT_ON_Ti {SILENT_ON_Ti}")

# ---------------- Q4: membership-permutation handedness null ---------------
rng = np.random.default_rng(SEED_PERM)
PERM = {}
for key, (cells, isL) in GROUPS.items():
    nn, nL = len(cells), int(isL.sum())
    M = np.zeros((NDRAW, nn), bool)
    for d in range(NDRAW):
        M[d, rng.permutation(nn)[:nL]] = True
    assert (M.sum(1) == nL).all(), (key, "draw count drift (STOP)")
    PERM[key] = M
log("[null] permutation draws built (per-side counts held EXACT)")


def pct2(real, null):
    up = float((null >= real).mean())
    return dict(pct_up=up, pct_two=float(2 * min(up, 1 - up)),
                null_mean=float(null.mean()), null_sd=float(null.std()),
                null_p05=float(np.percentile(null, 5)),
                null_p95=float(np.percentile(null, 95)))


Q4 = {}
for J in JOINTS:
    cf, isLf = GROUPS[(J, "f")]
    ce, isLe = GROUPS[(J, "e")]
    cells = np.concatenate([cf, ce])
    # per-cell removed-inhibitory mass and per-cell cutwA total mass
    rm_cell = np.zeros(Nall)
    sel = E_REMOVED & (vals_all < 0)
    np.add.at(rm_cell, dst_all[sel], np.abs(vals_all[sel]))
    tot_cell = np.zeros(Nall)
    np.add.at(tot_cell, dst_all[emask_wA], np.abs(vals_all[emask_wA]))
    rf, re_ = rm_cell[cf], rm_cell[ce]
    tf, te = tot_cell[cf], tot_cell[ce]
    Pf, Pe = PERM[(J, "f")], PERM[(J, "e")]

    def ainh(rL, tL, rR, tR):
        a, b = rL / tL, rR / tR
        return float((a - b) / (a + b))

    realA = ainh(float(rf[isLf].sum() + re_[isLe].sum()),
                 float(tf[isLf].sum() + te[isLe].sum()),
                 float(rf[~isLf].sum() + re_[~isLe].sum()),
                 float(tf[~isLf].sum() + te[~isLe].sum()))
    nrL = Pf @ rf + Pe @ re_
    ntL = Pf @ tf + Pe @ te
    nrR = (rf.sum() + re_.sum()) - nrL
    ntR = (tf.sum() + te.sum()) - ntL
    na, nb = nrL / ntL, nrR / ntR
    nullA = (na - nb) / (na + nb)
    Q4[J] = dict(A_inh=realA, **pct2(realA, nullA))
    log(f"[Q4 {J}] A_inh {realA:+.5f} pct_up {Q4[J]['pct_up']:.4f} "
        f"two {Q4[J]['pct_two']:.4f} [null {Q4[J]['null_p05']:+.4f},"
        f"{Q4[J]['null_p95']:+.4f}]")

# ---------------- lam1 no-op leg (premise 0a, measured not assumed) --------
# a GLOBAL rescale of the operator by any c>0 leaves every registered ratio
# untouched; demonstrate on the actual registered quantities.
_c = 3.7
_moved = []
for key in ROWS:
    n = ROWS[key]["n_cells"]
    NETc, NETf = Q2[key]["NET_cutwA"], Q2[key]["NET_f4wA"]
    NETp = Q2[key]["NET_pred"]
    da = _c * (GAIN["f4wA"] * NETf / n - GAIN["cutwA"] * NETc / n)
    dp = _c * (GAIN["f4wA"] * NETp / n - GAIN["cutwA"] * NETc / n)
    s2 = (da - dp) / da if da else None
    if s2 is not None and Q2[key]["S_sign"] is not None:
        _moved.append(abs(s2 - Q2[key]["S_sign"]))
LAM1_NOOP = dict(scale_tested=_c, max_abs_move=max(_moved) if _moved else None,
                 is_noop=bool(_moved and max(_moved) <= 1e-9))
assert LAM1_NOOP["is_noop"], ("lam1 no-op claim FALSE", LAM1_NOOP)
log(f"[0a] global-rescale no-op VERIFIED max move {LAM1_NOOP['max_abs_move']:.2e}")

# ---------------- branch table ---------------------------------------------
act = Q2["Tr_L"]
if act["D_DEGENERATE"]:
    BRANCH = "D_DEGENERATE"
elif act["BULK_ACCOUNTS"] and act["SIGN_ACCOUNTS"]:
    BRANCH = "B_BOTH"
elif act["BULK_ACCOUNTS"]:
    BRANCH = "B_BULK"
elif act["SIGN_ACCOUNTS"]:
    BRANCH = "B_SIGN"
else:
    BRANCH = "B_NEITHER"

PRED = dict(
    P1=dict(claim="BULK_SYMMETRIC TRUE", got=bool(BULK_SYMMETRIC),
            scored=bool(BULK_SYMMETRIC)),
    P2=dict(claim="Q2b CROSSES FALSE", got=bool(CROSSES),
            scored=bool(not CROSSES)),
    P3=dict(claim="branch B_SIGN", got=BRANCH, scored=BRANCH == "B_SIGN"),
    P4=dict(claim="SILENT_ON_Ti TRUE", got=bool(SILENT_ON_Ti),
            scored=bool(SILENT_ON_Ti)),
    P5=dict(claim="Q4 Tr percentile more extreme than Ti",
            got=[Q4["Tr"]["pct_two"], Q4["Ti"]["pct_two"]],
            scored=bool(Q4["Tr"]["pct_two"] < Q4["Ti"]["pct_two"])))

o["prereg"] = "l215/PREREG.md"
o["gains_used"] = dict(g_cutwA=G_CUTWA, g_f4wA=G_F4WA2,
                       ratio=G_F4WA2 / G_CUTWA)
o["cert"] = dict(cert_205=C4_cert, cert_tbl=TBL_cert, cert_g=2,
                 total_float_equalities=C4_cert + TBL_cert + 2)
o["rows"] = ROWS
o["Q1_bulk"] = Q1
o["Q2_sign_neutral"] = Q2
o["Q2b_relu_crossing"] = Q2b
o["Q3_specificity"] = Q3
o["Q4_null"] = dict(ndraw=NDRAW, seed=SEED_PERM,
                    kind="membership permutation (L45b/L70 handedness class); "
                         "per-side counts held EXACT",
                    **{k: v for k, v in Q4.items()})
o["lam1_noop"] = LAM1_NOOP
o["branch"] = BRANCH
o["predictions"] = PRED
o["limits"] = [
    "depth-1 in-mass under a uniform-X approximation; L208 already showed "
    "static drive does not predict dynamic level even in sign on Ti",
    "the Tr_L pools were SELECTED for being dead (L208 post-hoc floor leg): "
    "every number here is a DESCRIPTION of a selected object, and Q4 is a "
    "handedness null on a preselected pool, not a p-value for 'a pool'",
    "ret() mixes the floor with the small node-set change (cutwA drops "
    "ng_desc[:24], f4wA drops ng4[:20]); the node-matched eligible leg is "
    "reported beside it",
    "B_BOTH is unreachable by construction (declared in the PREREG)"]

# ---------------- read-only fingerprints asserted unchanged ----------------
for path, fp in (("l205/static.json", _FP205), ("l208/static.json", _FP208),
                 ("l208/addendum_floor.json", _FPA)):
    st = os.stat(path)
    assert (st.st_size, st.st_mtime_ns) == fp, (path, "MUTATED (STOP)")
log("[fingerprints] prior artifacts unchanged GREEN")

os.makedirs("l215", exist_ok=True)
json.dump(o, open("l215/static.json", "w"), indent=1, default=float)
log("=" * 72)
log(f"L215 DONE {time.time()-t0:.0f}s | BRANCH {BRANCH} | "
    f"preds {sum(1 for v in PRED.values() if v['scored'])}/5 | "
    f"Tr_L S_sign {act['S_sign']}")
