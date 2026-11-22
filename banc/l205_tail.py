# ================= L205 TAIL (appended by l205_build.py) =================
# Everything above this line is l151_static.py lines 1-319 VERBATIM (every
# L151/L142/L134/L92/L101 pin re-ran as free certification) plus l178_tail.py
# lines 22-83 VERBATIM (CERT-F4: the f4 ladder re-derivation and the stored
# float-equality gain leg). No lab module was imported (L175 lesson).
# PREREG: l205/PREREG.md (registered first). Writes l205/static.json ONLY.
# Zero rollouts, zero settles, zero dynamics. RNG: the membership permutation
# null ONLY, seeded.
import os

NDRAW = 2000
SEED_PERM = 20526
JOINTS = ("Ti", "Tr")

log("=" * 72)
log(f"[L205] handedness static | NDRAW {NDRAW} seed {SEED_PERM}")

# ---------------- substrates (both families, L175's five arms + closures) ----
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
# edge-count pins: the stored convention, asserted before any L205 value
assert int(SUB["f4wA"][0].sum()) == 469618, "f4wA edges (STOP)"
assert int(SUB["f4_closure"][0].sum()) == 472095, "f4 closure edges (STOP)"
assert int((emask_wA & pm4).sum()) == 469256, "f4-eligible wA edges (STOP)"
assert int(SUB["cutwA"][0].sum()) == 644177, "cutwA edges (STOP)"
assert int(SUB["cutng25"][0].sum()) == 644084, "cutng25 edges (STOP)"
assert int(SUB["base_closure"][0].sum()) == S92["edges_new"], "closure (STOP)"
EDGES = {k: int(v[0].sum()) for k, v in SUB.items()}
NODES = {k: int(v[1].sum()) for k, v in SUB.items()}
log("[pins] substrate edge counts GREEN: "
    + " ".join(f"{k} {EDGES[k]:,}" for k in SUB))

# ---------------- pools: per-side cell lists, size-invariance asserted ------
POOLSZ = S92["pool_sizes"]
GROUPS = {}          # joint -> {"f": (cells, isL), "e": (cells, isL)}
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
# every pool fully present on EVERY substrate (asserted, not assumed)
for sname, (E, keep, fam) in SUB.items():
    for pk, want in POOLSZ.items():
        assert int((POOL_G[pk] & keep).sum()) == want, (sname, pk, "pool size")
log("[pins] pool sizes invariant across all 7 substrates GREEN")

# ---------------- per-cell in-mass / in-degree per substrate ---------------
INMASS, INDEG = {}, {}
for sname, (E, keep, fam) in SUB.items():
    im = np.zeros(Nall)
    np.add.at(im, dst_all[E], np.abs(vals_all[E]))
    idg = np.zeros(Nall, np.int64)
    np.add.at(idg, dst_all[E], 1)
    INMASS[sname], INDEG[sname] = im, idg

# ---------------- the shared permutation draws (L45b/L70 handedness null) ---
rng = np.random.default_rng(SEED_PERM)
PERM = {}
for key, (cells, isL) in GROUPS.items():
    n, nL = len(cells), int(isL.sum())
    M = np.zeros((NDRAW, n), bool)
    for d in range(NDRAW):
        M[d, rng.permutation(n)[:nL]] = True
    assert (M.sum(1) == nL).all(), (key, "draw count drift (STOP)")
    PERM[key] = M
log("[null] permutation draws built (per-side counts held EXACT)")


def asym(mL, mR):
    t = mL + mR
    return float((mL - mR) / t) if t else None


def side_stats(sname, J):
    """real per-side totals/per-cell + the null distributions of A_cell/A_tot."""
    im = INMASS[sname]
    cf, isLf = GROUPS[(J, "f")]
    ce, isLe = GROUPS[(J, "e")]
    mf, me = im[cf], im[ce]
    Pf, Pe = PERM[(J, "f")], PERM[(J, "e")]
    nLf, nLe = int(isLf.sum()), int(isLe.sum())
    nRf, nRe = len(cf) - nLf, len(ce) - nLe
    # real
    ML = float(mf[isLf].sum() + me[isLe].sum())
    MR = float(mf[~isLf].sum() + me[~isLe].sum())
    nL, nR = nLf + nLe, nRf + nRe
    real = dict(M_L=ML, M_R=MR, n_L=nL, n_R=nR, m_L=ML / nL, m_R=MR / nR,
                A_tot=asym(ML, MR), A_cell=asym(ML / nL, MR / nR),
                M_fL=float(mf[isLf].sum()), M_fR=float(mf[~isLf].sum()),
                M_eL=float(me[isLe].sum()), M_eR=float(me[~isLe].sum()))
    # null (shared draws)
    sLf, sLe = Pf @ mf, Pe @ me
    nullML = sLf + sLe
    nullMR = (mf.sum() + me.sum()) - nullML
    nA_tot = (nullML - nullMR) / (nullML + nullMR)
    a, b = nullML / nL, nullMR / nR
    nA_cell = (a - b) / (a + b)
    return real, nA_cell, nA_tot


def pct_up(real, null):
    return float((null <= real).mean())


# ---------------- C1-C3 + the full table ------------------------------------
TABLE, NULLS = {}, {}
for J in JOINTS:
    TABLE[J], NULLS[J] = {}, {}
    for sname in SUB:
        real, nA_cell, nA_tot = side_stats(sname, J)
        real["A_cell_pct_up"] = pct_up(real["A_cell"], nA_cell)
        real["A_cell_pct_abs"] = pct_up(abs(real["A_cell"]), np.abs(nA_cell))
        real["A_tot_pct_up"] = pct_up(real["A_tot"], nA_tot)
        real["null_A_cell_mean"] = float(nA_cell.mean())
        real["null_A_cell_p05"] = float(np.percentile(nA_cell, 5))
        real["null_A_cell_p95"] = float(np.percentile(nA_cell, 95))
        real["null_A_cell_sd"] = float(nA_cell.std())
        TABLE[J][sname] = real
        NULLS[J][sname] = nA_cell
    # paired delta null: f4wA - cutwA on the SAME draws
    dreal = TABLE[J]["f4wA"]["A_cell"] - TABLE[J]["cutwA"]["A_cell"]
    dnull = NULLS[J]["f4wA"] - NULLS[J]["cutwA"]
    TABLE[J]["_delta_f4wA_minus_cutwA"] = dict(
        delta=dreal, pct_up=pct_up(dreal, dnull),
        null_mean=float(dnull.mean()), null_sd=float(dnull.std()),
        null_p05=float(np.percentile(dnull, 5)),
        null_p95=float(np.percentile(dnull, 95)))

Ti = TABLE["Ti"]
C1 = bool(Ti["f4wA"]["A_cell"] > 0 and Ti["f4wA"]["A_cell_pct_up"] >= 0.95)
C2 = bool(Ti["cutwA"]["A_cell"] < 0 and Ti["cutwA"]["A_cell_pct_up"] <= 0.05)
d = Ti["_delta_f4wA_minus_cutwA"]
C3 = bool(d["delta"] > 0 and d["pct_up"] >= 0.95)

log("-" * 72)
for J in JOINTS:
    for sname in SUB:
        r = TABLE[J][sname]
        log(f"[{J}] {sname:13s} fam {SUB[sname][2]:6s} "
            f"M_L {r['M_L']:9.2f} M_R {r['M_R']:9.2f} "
            f"m_L {r['m_L']:7.3f} m_R {r['m_R']:7.3f} "
            f"A_cell {r['A_cell']:+.4f} pct {r['A_cell_pct_up']:.3f} "
            f"[null {r['null_A_cell_p05']:+.4f},{r['null_A_cell_p95']:+.4f}]")
    dd = TABLE[J]["_delta_f4wA_minus_cutwA"]
    log(f"[{J}] delta(f4wA-cutwA) A_cell {dd['delta']:+.4f} "
        f"pct {dd['pct_up']:.3f} [null {dd['null_p05']:+.4f},"
        f"{dd['null_p95']:+.4f}]")
log(f"[GATES] C1 {C1} C2 {C2} C3 {C3}")

# ---------------- C4 MECHANISM: per-side floor retention (node set FIXED) ---
C4 = {}
for J in JOINTS:
    cf, isLf = GROUPS[(J, "f")]
    ce, isLe = GROUPS[(J, "e")]
    row = {}
    for side, self_, sele in (("L", isLf, isLe), ("R", ~isLf, ~isLe)):
        tgt = np.zeros(Nall, bool)
        tgt[cf[self_]] = True
        tgt[ce[sele]] = True
        e_all = emask_wA & tgt[dst_all]
        e_f4 = e_all & pm4
        m_all = float(np.abs(vals_all[e_all]).sum())
        m_f4 = float(np.abs(vals_all[e_f4]).sum())
        row[side] = dict(
            n_edges_cutwA=int(e_all.sum()), n_edges_floor_eligible=int(e_f4.sum()),
            edge_retention=float(e_f4.sum() / e_all.sum()) if e_all.sum() else None,
            mass_cutwA=m_all, mass_floor_eligible=m_f4,
            mass_retention=m_f4 / m_all if m_all else None,
            median_syn=float(np.median(w_syn[e_all])),
            frac_syn_lt4=float((w_syn[e_all] < FLOOR).mean()))
    row["edge_retention_ratio_L_over_R"] = (
        row["L"]["edge_retention"] / row["R"]["edge_retention"])
    row["mass_retention_ratio_L_over_R"] = (
        row["L"]["mass_retention"] / row["R"]["mass_retention"])
    C4[J] = row
    log(f"[C4 {J}] L keep {row['L']['edge_retention']:.4f} edges / "
        f"{row['L']['mass_retention']:.4f} mass | R keep "
        f"{row['R']['edge_retention']:.4f} / {row['R']['mass_retention']:.4f} "
        f"| ratio {row['edge_retention_ratio_L_over_R']:.4f} / "
        f"{row['mass_retention_ratio_L_over_R']:.4f}")

# ---------------- C5 SHARED-DRIVE COMPANION (descriptive, Ti, 2 substrates) -
C5 = {}
for sname in ("cutwA", "f4wA"):
    E = SUB[sname][0]
    cf, isLf = GROUPS[("Ti", "f")]
    ce, isLe = GROUPS[("Ti", "e")]
    pool = np.concatenate([cf, ce])
    col = -np.ones(Nall, np.int64)
    col[pool] = np.arange(len(pool))
    sel = E & (col[dst_all] >= 0)
    srcs = np.unique(src_all[sel])
    rowi = -np.ones(Nall, np.int64)
    rowi[srcs] = np.arange(len(srcs))
    Mden = np.zeros((len(srcs), len(pool)), np.float64)
    np.add.at(Mden, (rowi[src_all[sel]], col[dst_all[sel]]),
              np.abs(vals_all[sel]))
    Mf = Mden[:, :len(cf)]
    Me = Mden[:, len(cf):]
    Pf, Pe = PERM[("Ti", "f")], PERM[("Ti", "e")]

    def shared(self_, sele):
        return float(np.minimum(Mf[:, self_].sum(1), Me[:, sele].sum(1)).sum())

    sL, sR = shared(isLf, isLe), shared(~isLf, ~isLe)
    # null: matrix form (sources x draws), CHUNKED over draws to bound memory
    totf = Mf.sum(1)[:, None]
    tote = Me.sum(1)[:, None]
    nsL = np.zeros(NDRAW)
    nsR = np.zeros(NDRAW)
    CH = 250
    for lo in range(0, NDRAW, CH):
        hi = min(lo + CH, NDRAW)
        mfL = Mf @ Pf[lo:hi].T.astype(np.float64)
        meL = Me @ Pe[lo:hi].T.astype(np.float64)
        nsL[lo:hi] = np.minimum(mfL, meL).sum(0)
        nsR[lo:hi] = np.minimum(totf - mfL, tote - meL).sum(0)
        del mfL, meL
    nAs = (nsL - nsR) / (nsL + nsR)
    Areal = asym(sL, sR)
    C5[sname] = dict(n_sources=int(len(srcs)), shared_L=sL, shared_R=sR,
                     A_shared=Areal, pct_up=pct_up(Areal, nAs),
                     null_mean=float(nAs.mean()), null_sd=float(nAs.std()),
                     null_p05=float(np.percentile(nAs, 5)),
                     null_p95=float(np.percentile(nAs, 95)))
    log(f"[C5 {sname}] shared-drive L {sL:.3f} R {sR:.3f} A {Areal:+.4f} "
        f"pct {C5[sname]['pct_up']:.3f} "
        f"[null {C5[sname]['null_p05']:+.4f},{C5[sname]['null_p95']:+.4f}]")
    del Mden, Mf, Me, totf, tote

# ---------------- branch ----------------------------------------------------
if C1 and C3:
    BRANCH = "H_STATIC"
elif C1 and not C3:
    BRANCH = "H_STATIC_NOFLIP"
elif not C1 and 0.05 < Ti["f4wA"]["A_cell_pct_up"] < 0.95:
    BRANCH = "H_DYNAMIC"
else:
    BRANCH = "H_UNREGISTERED_SHAPE"

o["substrates"] = dict(edges=EDGES, nodes=NODES,
                       family={k: v[2] for k, v in SUB.items()})
o["table"] = TABLE
o["gates"] = dict(C1_floored=C1, C2_base=C2, C3_flip=C3,
                  C1_detail=dict(A_cell=Ti["f4wA"]["A_cell"],
                                 pct_up=Ti["f4wA"]["A_cell_pct_up"]),
                  C2_detail=dict(A_cell=Ti["cutwA"]["A_cell"],
                                 pct_up=Ti["cutwA"]["A_cell_pct_up"]),
                  C3_detail=d)
o["c4_floor_retention"] = C4
o["c5_shared_drive"] = C5
o["branch"] = BRANCH
o["null"] = dict(kind="membership permutation (L45b/L70 handedness class)",
                 ndraw=NDRAW, seed=SEED_PERM,
                 note="per-side counts held EXACT; draws SHARED across "
                      "substrates so the delta null is paired")
o["limits"] = ["depth-1 in-mass is a plausible but not necessary precursor "
               "of a within-side flexor-extensor correlation",
               "A is a ratio: direction only, absolute masses printed",
               "handedness null, not a degree null (no neuromere on BANC)"]

os.makedirs("l205", exist_ok=True)
json.dump(o, open("l205/static.json", "w"), indent=1, default=float)
log("=" * 72)
log(f"L205 DONE {time.time()-t0:.0f}s | BRANCH {BRANCH} | "
    f"C1 {C1} C2 {C2} C3 {C3} | Ti A_cell f4wA "
    f"{Ti['f4wA']['A_cell']:+.4f} cutwA {Ti['cutwA']['A_cell']:+.4f}")
