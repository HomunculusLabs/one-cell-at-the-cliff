# ================= L209 TAIL (appended by l209_build.py) =================
# Everything above this line is VERBATIM source: l151_static.py 1-319,
# l178_tail.py 7-149, the l206_mid bridge, l206_tail.py 22-121 (CERT-178 =
# 420 stored L178 anatomical values at FLOAT EQUALITY, reach(), power_iter,
# LAM1), l207_tail.py 26-146 (gain invariance + the GENERIC substrate builder
# + CERT-GEN). So CERT-F4, the three stored gains, the CSR orientation, all
# 20 pool sizes, CERT-178 and CERT-GEN have ALL re-run as free certification
# before any L209 value is read. PREREG: l209/PREREG.md (registered first).
# Writes l209/static.json ONLY. Zero rollouts, zero settles, zero dynamics.
# RNG: the membership permutation null ONLY, seeded (L205's stream).
import os

NDRAW = 2000
SEED_PERM = 20526
JOINTS = ("Ti", "Tr")
DMAX = 3
PCT_HI = 0.95

o["design"] = (
    "L209 does the handedness appear DEEPER? Per-side depth-1..3 ARRIVAL "
    "mass r_d = A^d 1 of the ANATOMICAL operator A = |W_beta| (g=1, no row "
    "mask, no settle, no seed) into the Ti/Tr flexor+extensor pools on "
    "cutwA vs f4wA, lam1^d-normalised (PRIMARY) with the Crofts/Estrada "
    "W/sqrt(s_i s_j) form as the required second leg, scored against the "
    "SAME 2000 shared membership-permutation draws L205 used (seed 20526). "
    "PREREG l209/PREREG.md.")
o["prereg"] = "l209/PREREG.md"
with open("l209_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(9)])

log("=" * 72)
log(f"[L209] deep handedness | NDRAW {NDRAW} seed {SEED_PERM} DMAX {DMAX}")

# ---------------- L205's seven substrates (for the CERT-205 halting gate) ---
keep_f4ng = keep_new.copy()
keep_f4ng[np.sort(ng4[:21])] = False
keep_f4tw = keep_new.copy()
keep_f4tw[np.sort(np.concatenate([ng4[:20], ng4[21:22]]))] = False
assert GI_CARRIER not in set(int(x) for x in ng4[:20]), "f4wA XOR broken (STOP)"
assert not keep_f4ng[GI_CARRIER] and keep_f4[GI_CARRIER], "f4ng XOR (STOP)"
assert keep_f4tw[GI_CARRIER] and not keep_f4tw[GI_TWIN4], "f4tw XOR (STOP)"

SUB = {
    "base_closure": (emask_n, keep_new, "base"),
    "cutwA": (emask_wA, keep_wA, "base"),
    "cutng25": (emask_25, keep_25, "base"),
    "f4_closure": (emask_n & pm4, keep_new, "floor4"),
    "f4wA": (emask_f4, keep_f4, "floor4"),
    "f4ng": (keep_f4ng[src_all] & keep_f4ng[dst_all] & pm4, keep_f4ng, "floor4"),
    "f4tw": (keep_f4tw[src_all] & keep_f4tw[dst_all] & pm4, keep_f4tw, "floor4"),
}
assert int(SUB["f4wA"][0].sum()) == 469618, "f4wA edges (STOP)"
assert int(SUB["f4_closure"][0].sum()) == 472095, "f4 closure edges (STOP)"
assert int((emask_wA & pm4).sum()) == 469256, "f4-eligible wA edges (STOP)"
assert int(SUB["cutwA"][0].sum()) == 644177, "cutwA edges (STOP)"
assert int(SUB["cutng25"][0].sum()) == 644084, "cutng25 edges (STOP)"
assert int(SUB["base_closure"][0].sum()) == S92["edges_new"], "closure (STOP)"
log("[pins] L205 substrate edge counts GREEN")

# ---------------- pools: per-side cell lists (L205's expressions) ----------
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
assert list(GROUPS.keys()) == [("Ti", "f"), ("Ti", "e"), ("Tr", "f"), ("Tr", "e")], \
    "GROUPS key ORDER differs from L205 -> RNG stream would differ (STOP)"
for sname, (E, keep, fam) in SUB.items():
    for pk, want in POOLSZ.items():
        assert int((POOL_G[pk] & keep).sum()) == want, (sname, pk, "pool size")
log("[pins] pool sizes invariant across all 7 L205 substrates GREEN")

# ---------------- the shared permutation draws (L205's stream) -------------
rng = np.random.default_rng(SEED_PERM)
PERM = {}
for key, (cells, isL) in GROUPS.items():
    n, nL = len(cells), int(isL.sum())
    M = np.zeros((NDRAW, n), bool)
    for d in range(NDRAW):
        M[d, rng.permutation(n)[:nL]] = True
    assert (M.sum(1) == nL).all(), (key, "draw count drift (STOP)")
    PERM[key] = M
log("[null] permutation draws rebuilt (per-side counts held EXACT)")


def asym(mL, mR):
    t = mL + mR
    return float((mL - mR) / t) if t else None


def pct_up(real, null):
    return float((null <= real).mean())


def side_stats_from(mf, me, J):
    """L205's side_stats EXPRESSION-IDENTICALLY, over any per-cell vector
    pair (flexor group, extensor group) in GROUPS order (L cells then R)."""
    cf, isLf = GROUPS[(J, "f")]
    ce, isLe = GROUPS[(J, "e")]
    Pf, Pe = PERM[(J, "f")], PERM[(J, "e")]
    nLf, nLe = int(isLf.sum()), int(isLe.sum())
    nRf, nRe = len(cf) - nLf, len(ce) - nLe
    ML = float(mf[isLf].sum() + me[isLe].sum())
    MR = float(mf[~isLf].sum() + me[~isLe].sum())
    nL, nR = nLf + nLe, nRf + nRe
    real = dict(M_L=ML, M_R=MR, n_L=nL, n_R=nR, m_L=ML / nL, m_R=MR / nR,
                A_tot=asym(ML, MR), A_cell=asym(ML / nL, MR / nR),
                M_fL=float(mf[isLf].sum()), M_fR=float(mf[~isLf].sum()),
                M_eL=float(me[isLe].sum()), M_eR=float(me[~isLe].sum()))
    sLf, sLe = Pf @ mf, Pe @ me
    nullML = sLf + sLe
    nullMR = (mf.sum() + me.sum()) - nullML
    nA_tot = (nullML - nullMR) / (nullML + nullMR)
    a, b = nullML / nL, nullMR / nR
    nA_cell = (a - b) / (a + b)
    return real, nA_cell, nA_tot


def decorate(real, nA_cell, nA_tot):
    real["A_cell_pct_up"] = pct_up(real["A_cell"], nA_cell)
    real["A_cell_pct_abs"] = pct_up(abs(real["A_cell"]), np.abs(nA_cell))
    real["A_tot_pct_up"] = pct_up(real["A_tot"], nA_tot)
    real["null_A_cell_mean"] = float(nA_cell.mean())
    real["null_A_cell_p05"] = float(np.percentile(nA_cell, 5))
    real["null_A_cell_p95"] = float(np.percentile(nA_cell, 95))
    real["null_A_cell_sd"] = float(nA_cell.std())
    return real


# ---------------- CERT-205 (HALTING): L205's table at FLOAT EQUALITY -------
S205 = json.load(open("l205/static.json"))
_FIELDS = ("M_L", "M_R", "m_L", "m_R", "A_tot", "A_cell", "M_fL", "M_fR",
           "M_eL", "M_eR", "A_cell_pct_up", "A_cell_pct_abs", "A_tot_pct_up",
           "null_A_cell_mean", "null_A_cell_p05", "null_A_cell_p95",
           "null_A_cell_sd")
INMASS = {}
for sname, (E, keep, fam) in SUB.items():
    im = np.zeros(Nall)
    np.add.at(im, dst_all[E], np.abs(vals_all[E]))
    INMASS[sname] = im
_n205 = 0
_N205 = {}
for J in JOINTS:
    _N205[J] = {}
    for sname in SUB:
        cf, _ = GROUPS[(J, "f")]
        ce, _ = GROUPS[(J, "e")]
        real, nAc, nAt = side_stats_from(INMASS[sname][cf], INMASS[sname][ce], J)
        real = decorate(real, nAc, nAt)
        _N205[J][sname] = nAc
        st = S205["table"][J][sname]
        for f in _FIELDS:
            assert real[f] == st[f], (J, sname, f, real[f], st[f], "CERT-205")
            _n205 += 1
    dreal = (S205["table"][J]["f4wA"]["A_cell"]
             - S205["table"][J]["cutwA"]["A_cell"])
    dnull = _N205[J]["f4wA"] - _N205[J]["cutwA"]
    std = S205["table"][J]["_delta_f4wA_minus_cutwA"]
    for f, v in (("delta", dreal), ("pct_up", pct_up(dreal, dnull)),
                 ("null_mean", float(dnull.mean())),
                 ("null_sd", float(dnull.std())),
                 ("null_p05", float(np.percentile(dnull, 5))),
                 ("null_p95", float(np.percentile(dnull, 95)))):
        assert v == std[f], (J, "delta", f, v, std[f], "CERT-205 delta")
        _n205 += 1
log(f"[CERT-205] GREEN {_n205} stored L205 values reproduced by FLOAT "
    f"EQUALITY (2 joints x 7 substrates x 17 fields + 2 paired deltas) "
    f"-> RNG stream, side convention, pool membership and the depth-1 "
    f"anchor all certified")
o["cert_205"] = dict(n_checks=_n205, mode="float equality (==)",
                     source="l205/static.json table", n_substrates=len(SUB),
                     fields=list(_FIELDS))

# ---------------- the two L209 substrates (certified generic builder) ------
SUBS = {"cutwA": build_sub(keep_wA, emask_wA, "cutwA"), "f4wA": _f4}
assert SUBS["cutwA"]["n"] == 21785 and SUBS["cutwA"]["n_edges"] == 644177
assert SUBS["f4wA"]["n"] == 21789 and SUBS["f4wA"]["n_edges"] == 469618
LOCAL = {}
for sname, s in SUBS.items():
    LOCAL[sname] = {}
    for key, (cells, isL) in GROUPS.items():
        lc = s["loc"][cells]
        assert (lc >= 0).all(), (sname, key, "pool cell absent (STOP)")
        LOCAL[sname][key] = lc

# ---------------- operators per substrate: beta (g=1) and Crofts ----------
OPS, LAMS = {}, {}
for sname, s in SUBS.items():
    jv = s["jv"]
    s_out_l = np.zeros(s["n"])
    np.add.at(s_out_l, s["cols"], jv)
    s_in_l = np.zeros(s["n"])
    np.add.at(s_in_l, s["rows"], jv)
    s_tot_l = s_out_l + s_in_l
    s_safe_l = np.where(s_tot_l > 0, s_tot_l, 1.0)
    jv_cr = jv / np.sqrt(s_safe_l[s["rows"]] * s_safe_l[s["cols"]])
    OPS[sname] = dict(beta=jv, crofts=jv_cr)
    LAMS[sname] = {}
    for op, v in OPS[sname].items():
        lam, spr = power_iter_sub(s, v)
        assert lam > 0 and spr < 1e-6, (sname, op, "power iteration (STOP)")
        LAMS[sname][op] = lam
        log(f"[spectral] {sname} {op}: lam1 {lam:.6f} (rel spread {spr:.2e})")
assert LAMS["f4wA"]["beta"] == LAM1_G1, \
    (LAMS["f4wA"]["beta"], LAM1_G1, "f4wA g=1 lam1 != certified (STOP)")
log("[spectral] f4wA beta lam1 == the head's certified LAM1_G1 GREEN")


def arrivals(s, jv, dmax, lam=None):
    """r_d = A^d 1 (A[dst,src]); if lam is given the operator is A/lam."""
    v = jv if lam is None else jv / lam
    x = np.ones(s["n"])
    out = {}
    for d in range(1, dmax + 1):
        y = np.zeros(s["n"])
        np.add.at(y, s["rows"], v * x[s["cols"]])
        x = y
        out[d] = x.copy()
    return out


# ---------------- the depth table ------------------------------------------
TABLE, NULLS = {}, {}
MAXREL = 0.0
for sname, s in SUBS.items():
    for op in ("beta", "crofts"):
        rn = arrivals(s, OPS[sname][op], DMAX, lam=LAMS[sname][op])
        ru = arrivals(s, OPS[sname][op], DMAX, lam=None)
        for J in JOINTS:
            lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
            for d in range(1, DMAX + 1):
                real, nAc, nAt = side_stats_from(rn[d][lf], rn[d][le], J)
                real = decorate(real, nAc, nAt)
                # registered no-op check: unnormalised A_cell must agree
                ru_real, _, _ = side_stats_from(ru[d][lf], ru[d][le], J)
                rel = abs(ru_real["A_cell"] - real["A_cell"]) / \
                    max(abs(real["A_cell"]), 1e-300)
                MAXREL = max(MAXREL, rel)
                real["A_cell_unnormalised"] = ru_real["A_cell"]
                real["A_cell_norm_rel_diff"] = float(rel)
                TABLE[(sname, op, J, d)] = real
                NULLS[(sname, op, J, d)] = nAc
assert MAXREL < 1e-10, (MAXREL, "lam1 normalisation NOT a no-op for A_cell")
log(f"[NO-OP] GREEN lam1^d normalisation is a measured no-op for A_cell "
    f"(max rel diff {MAXREL:.2e} over {len(TABLE)} cells)")

# depth-1 convention: the walk operator's own depth 1 vs L205's raw in-mass
D1 = {}
for sname in SUBS:
    for J in JOINTS:
        D1[f"{J}|{sname}"] = dict(
            A_cell_beta=TABLE[(sname, "beta", J, 1)]["A_cell"],
            A_cell_raw_L205=S205["table"][J][sname]["A_cell"],
            pct_abs_beta=TABLE[(sname, "beta", J, 1)]["A_cell_pct_abs"],
            pct_abs_raw_L205=S205["table"][J][sname]["A_cell_pct_abs"],
            same_sign=bool(TABLE[(sname, "beta", J, 1)]["A_cell"]
                           * S205["table"][J][sname]["A_cell"] > 0))
        log(f"[depth-1] {J}|{sname}: beta {D1[f'{J}|{sname}']['A_cell_beta']:+.4f} "
            f"vs L205 raw {D1[f'{J}|{sname}']['A_cell_raw_L205']:+.4f} "
            f"(same sign {D1[f'{J}|{sname}']['same_sign']})")

log("-" * 72)
for sname in SUBS:
    for op in ("beta", "crofts"):
        for J in JOINTS:
            for d in range(1, DMAX + 1):
                r = TABLE[(sname, op, J, d)]
                log(f"[{J}] {sname:6s} {op:6s} d{d} "
                    f"m_L {r['m_L']:.6g} m_R {r['m_R']:.6g} "
                    f"A_cell {r['A_cell']:+.4f} pct_up {r['A_cell_pct_up']:.3f} "
                    f"pct_abs {r['A_cell_pct_abs']:.3f} "
                    f"[null {r['null_A_cell_p05']:+.4f},"
                    f"{r['null_A_cell_p95']:+.4f}]")

# ---------------- paired delta f4wA - cutwA per depth (shared draws) ------
DELTA = {}
for op in ("beta", "crofts"):
    for J in JOINTS:
        for d in range(1, DMAX + 1):
            dreal = (TABLE[("f4wA", op, J, d)]["A_cell"]
                     - TABLE[("cutwA", op, J, d)]["A_cell"])
            dnull = NULLS[("f4wA", op, J, d)] - NULLS[("cutwA", op, J, d)]
            DELTA[f"{op}|{J}|d{d}"] = dict(
                delta=dreal, pct_up=pct_up(dreal, dnull),
                pct_abs=pct_up(abs(dreal), np.abs(dnull)),
                null_mean=float(dnull.mean()), null_sd=float(dnull.std()),
                null_p05=float(np.percentile(dnull, 5)),
                null_p95=float(np.percentile(dnull, 95)))
            log(f"[delta] {op} {J} d{d}: {dreal:+.5f} pct_up "
                f"{DELTA[f'{op}|{J}|d{d}']['pct_up']:.4f} pct_abs "
                f"{DELTA[f'{op}|{J}|d{d}']['pct_abs']:.4f}")

# ---------------- branch: SIGN x BAND on Ti / f4wA / depth 2 / beta -------
def cell_of(key):
    r = TABLE[key]
    outside = bool(r["A_cell_pct_abs"] >= PCT_HI)
    left = bool(r["A_cell"] > 0)
    if outside and left:
        return "D_DEEP_LEFT"
    if outside and not left:
        return "D_DEEP_RIGHT"
    if (not outside) and left:
        return "D_NULL_LEFTWARD"
    return "D_NULL_RIGHTWARD"


PRIMARY = ("f4wA", "beta", "Ti", 2)
BRANCH = cell_of(PRIMARY)
_cells = {f"{J}|{sn}|d{d}": cell_of((sn, "beta", J, d))
          for sn in SUBS for J in JOINTS for d in (2, 3)}
_ti_cells = [v for k, v in _cells.items() if k.startswith("Ti|")]
DISAGREE = bool(len(set(_ti_cells)) > 1)
log(f"[BRANCH] {BRANCH} (primary Ti|f4wA|d2|beta: A_cell "
    f"{TABLE[PRIMARY]['A_cell']:+.4f} pct_abs "
    f"{TABLE[PRIMARY]['A_cell_pct_abs']:.3f}) | Ti depth/substrate cells "
    f"{_ti_cells} | D_DEPTH_DISAGREE {DISAGREE}")

# ---------------- Crofts sign agreement (Q209-3) --------------------------
_sign_agree = {}
for sn in SUBS:
    for J in JOINTS:
        for d in (2, 3):
            a = TABLE[(sn, "beta", J, d)]["A_cell"]
            b = TABLE[(sn, "crofts", J, d)]["A_cell"]
            _sign_agree[f"{J}|{sn}|d{d}"] = bool(a * b > 0)
_ti_agree = all(v for k, v in _sign_agree.items() if k.startswith("Ti|"))

# ---------------- predictions, scored -------------------------------------
_q4 = all(DELTA[f"beta|Ti|d{d}"]["pct_abs"] < PCT_HI for d in (2, 3))
o["predictions"] = dict(
    Q209_1=dict(registered="D_NULL_RIGHTWARD", measured=BRANCH,
                correct=BRANCH == "D_NULL_RIGHTWARD"),
    Q209_2=dict(registered="lam1 normalisation a no-op for A_cell (<1e-10)",
                measured=MAXREL, correct=bool(MAXREL < 1e-10)),
    Q209_3=dict(registered="Crofts agrees in SIGN with beta on Ti d2-d3 "
                           "on both substrates",
                measured=_sign_agree, correct=bool(_ti_agree)),
    Q209_4=dict(registered="paired delta f4wA-cutwA INSIDE its null at "
                           "Ti d2-d3 (unlike depth 1, L205 C3)",
                measured={f"d{d}": DELTA[f'beta|Ti|d{d}']["pct_abs"]
                          for d in (2, 3)},
                correct=bool(_q4)))
o["n_predictions_correct"] = int(sum(1 for v in o["predictions"].values()
                                     if v["correct"]))

o["substrates"] = {k: dict(n=v["n"], n_edges=v["n_edges"],
                           lam1_beta=LAMS[k]["beta"],
                           lam1_crofts=LAMS[k]["crofts"]) for k, v in SUBS.items()}
o["table"] = {f"{sn}|{op}|{J}|d{d}": TABLE[(sn, op, J, d)]
              for (sn, op, J, d) in TABLE}
o["depth1_convention"] = D1
o["delta_f4wA_minus_cutwA"] = DELTA
o["branch"] = BRANCH
o["branch_cells"] = _cells
o["depth_disagree"] = DISAGREE
o["crofts_sign_agreement"] = _sign_agree
o["norm_noop_max_rel_diff"] = MAXREL
o["bars"] = dict(pct_abs_outside=PCT_HI, ndraw=NDRAW, seed=SEED_PERM,
                 dmax=DMAX)
o["null"] = dict(kind="membership permutation (L45b/L70 handedness class), "
                      "L205's stream",
                 ndraw=NDRAW, seed=SEED_PERM,
                 note="per-side counts held EXACT; draws SHARED across "
                      "substrates/operators/depths so every delta is paired")
o["limitations"] = [
    "ANATOMICAL leg only: wiring geometry, NOT an operating point (L164).",
    "Operator powers are walks WITH revisits, not paths; pool cells are "
    "themselves reachable so deeper arrivals include recurrent mass.",
    "r_d = A^d 1 is source-FREE (summed over all sources) — it is the "
    "depth-d generalisation of in-mass, not a per-actor reach.",
    "The null is a HANDEDNESS (membership-permutation) null, not a degree-"
    "preserving rewire null; magnitudes from the two are never swapped.",
    "Depth-1 of the walk operator carries BETA_L on inhibitory edges while "
    "L205's in-mass did not: both are reported in depth1_convention.",
    "The Crofts leg is a different OPERATOR (per-edge reweighting), not a "
    "normalisation of the same one, and is scored as its own leg.",
    "No neuromere column exists on BANC, so no legblock tier is possible.",
]
o["pins"] = "ALL GREEN"

os.makedirs("l209", exist_ok=True)
json.dump(o, open("l209/static.json", "w"), indent=1, default=float)
log("=" * 72)
log(f"L209 DONE {time.time()-t0:.0f}s | BRANCH {BRANCH} | "
    f"Ti f4wA d2 A_cell {TABLE[PRIMARY]['A_cell']:+.4f} "
    f"pct_abs {TABLE[PRIMARY]['A_cell_pct_abs']:.3f} | "
    f"predictions {o['n_predictions_correct']}/4")
