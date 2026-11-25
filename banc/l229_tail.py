# ================= L229 TAIL (appended by l229_build.py) ===================
# Everything above this line is certified VERBATIM slices (see the generated
# banner). No lab module imported (L175). PREREG: l229/PREREG.md (registered
# BEFORE this file existed). Writes l229/static.json ONLY.
# ZERO rollouts, zero settles, zero new dynamics: every dynamic number is
# read from the stored npz, opened read-only and fingerprinted.
import hashlib
import itertools
import math

log("=" * 72)
log("[L229] near-balance as a POPULATION question | PREREG l229/PREREG.md")

RMAX, BG, NOISE = 1.0, 0.02, 0.01
ENT_AMP = 0.1
SEG = 2000
ARMS5 = ["f4wA", "f4ng", "f4tw", "cutwA", "cutng25"]
ARMS12 = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5", "eMotBot5",
          "f4wA", "f4ng", "f4tw", "wAgN", "n25gW"]
ARMS7 = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5", "eMotBot5"]
JOINTS10 = ["Ti", "Tr", "Ta", "Sr", "Pr"]
SIDES = ["L", "R"]
BATCH = {
    "B35": ("l150/raw_l150.npz", list(range(3365, 3381)), ARMS7),
    "B36": ("l169b2/raw_l169b2.npz", list(range(3449, 3465)), ARMS12),
    "B37": ("l175f/raw_l175f.npz", list(range(3701, 3717)), ARMS12),
}
FLOOR_DEAD = BG + 2 * NOISE          # 0.04, registered in PREREG 0c
BAND_STRONG, BAND_WEAK = 0.70, 0.40  # registered effect-size band (0i)

# ---------------- CERT-W: window literals from the run script TEXT ---------
RUNSRC = open("l169b2_run.py").read()
for lit in ("TAU, DT, RMAX = 0.05, 0.01, 1.0",
            "BG, NOISE = 0.02, 0.01",
            "SETTLE, WIN = 400, 6000",
            "SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]",
            "ENT_AMP = 0.1",
            "SEG = 2000"):
    assert lit in RUNSRC, ("CERT-W missing literal", lit)
assert (WIN, DT) == (6000, 0.01) and MEAS0 == 500, "CERT-W window drift (STOP)"
assert SEGB == [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
AMPA = np.zeros(WIN, np.float64)
for _s0, _, _ in SEGB:
    _c = 0
    while _s0 + _c * 900 < _s0 + SEG:
        _lo = _s0 + _c * 900
        AMPA[_lo:min(_lo + 500, _s0 + SEG)] = ENT_AMP
        _c += 1
AMPA[2000:4000] = ENT_AMP
W = np.zeros(WIN, bool)
for _a0, _b0, _f in SEGB:
    if _f == 0.7:
        W[_a0 + MEAS0:_b0] = True
assert int(W.sum()) == 3000, (int(W.sum()), "CERT-W |W| (STOP)")
W_ON = W & (AMPA > 0)
log(f"[CERT-W] GREEN | |W| {int(W.sum())} |W_on| {int(W_ON.sum())}")

# ---------------- the TEN pool-sides (nonselective population) -------------
SIDEMASK10, NCELL10, NPOOL10 = {}, {}, {}
for J in JOINTS10:
    ag, bg = PREF[J]
    for side in SIDES:
        ma = POOL_G[f"{J}_{ag}{side}"] & keep_wA
        mb = POOL_G[f"{J}_{bg}{side}"] & keep_wA
        na, nb = int(ma.sum()), int(mb.sum())
        assert na == S101[f"{J}_a{side}"], (J, side, "a size (STOP)")
        assert nb == S101[f"{J}_b{side}"], (J, side, "b size (STOP)")
        assert int((ma & mb).sum()) == 0, (J, side, "a/b overlap (STOP)")
        t = ma | mb
        SIDEMASK10[(J, side)] = t
        NCELL10[(J, side)] = int(t.sum())
        NPOOL10[(J, side)] = (na, nb)
        assert NCELL10[(J, side)] == na + nb, (J, side, "union size (STOP)")
# the four certified HEAD3 masks must be REPRODUCED by my construction
for J in JOINTS:
    for side in SIDES:
        assert np.array_equal(SIDEMASK10[(J, side)], SIDEMASK[(J, side)]), \
            (J, side, "SIDEMASK10 disagrees with certified SIDEMASK (STOP)")
        assert NCELL10[(J, side)] == NCELL[(J, side)], (J, side, "NCELL")
KEYS10 = [f"{J}_{s}" for J in JOINTS10 for s in SIDES]
assert len(KEYS10) == 10
log("[pool-sides] 10 built; all 20 pool sizes pinned; Ti/Tr masks "
    "ARRAY-IDENTICAL to the certified HEAD3 masks")
log("  " + " ".join(f"{k}:{NCELL10[(k.split('_')[0], k.split('_')[1])]}"
                    for k in KEYS10))

# ---------------- CERT-215R: L215's own ROWS reproduced, float equality ----
S215 = json.load(open("l215/static.json"))
_fp215 = os.stat("l215/static.json")
_FP215 = (_fp215.st_size, _fp215.st_mtime_ns)
n215 = 0
for J in JOINTS:
    for side in SIDES:
        st = S215["rows"][f"{J}_{side}"]
        tgt = SIDEMASK10[(J, side)]
        n = NCELL10[(J, side)]
        assert n == st["n_cells"], (J, side, "n_cells (STOP)")
        n215 += 1
        for sname in ("cutwA", "f4wA"):
            Mp, Mm, ne = signed_in(SUB[sname][0], tgt)
            got = dict(Mp=Mp, Mm=Mm, NET=Mp - Mm, TOT=Mp + Mm, n_edges=ne,
                       NET_per_cell=(Mp - Mm) / n,
                       NET_gain=GAIN[sname] * (Mp - Mm) / n,
                       inh_frac=Mm / (Mp + Mm))
            for k, v in got.items():
                assert v == st[sname][k], ("CERT-215R", J, side, sname, k, v,
                                           st[sname][k], "(STOP)")
                n215 += 1
            # COVERAGE DERIVED FROM THE ARTIFACT (L224): every stored field of
            # this sub-dict must have been compared, not a chosen subset.
            assert set(got) == set(st[sname]), (J, side, sname,
                                                sorted(set(st[sname]) - set(got)),
                                                "CERT-215R coverage (STOP)")
_want215 = sum(1 + sum(len(S215["rows"][f"{J}_{s}"][sn])
                       for sn in ("cutwA", "f4wA"))
               for J in JOINTS for s in SIDES)
assert n215 == _want215 == 68, (n215, _want215, "CERT-215R count (STOP)")
log(f"[CERT-215R] GREEN {n215} float equalities (L215 rows reproduced) — "
    "this is what licenses extending inh_frac to six NEW pool-sides")

# ---------------- ANATOMY: inh_frac for all ten, both substrates -----------
ANAT = {}
for J in JOINTS10:
    for side in SIDES:
        key = f"{J}_{side}"
        tgt = SIDEMASK10[(J, side)]
        n = NCELL10[(J, side)]
        row = {"n_cells": n, "n_pool_a": NPOOL10[(J, side)][0],
               "n_pool_b": NPOOL10[(J, side)][1]}
        for sname in ("cutwA", "f4wA"):
            Mp, Mm, ne = signed_in(SUB[sname][0], tgt)
            assert Mp + Mm > 0.0, (key, sname, "no in-mass (STOP)")
            row[sname] = dict(Mp=Mp, Mm=Mm, NET=Mp - Mm, TOT=Mp + Mm,
                              n_edges=ne, NET_per_cell=(Mp - Mm) / n,
                              inh_frac=Mm / (Mp + Mm),
                              near=-abs(Mm / (Mp + Mm) - 0.5))
        ANAT[key] = row
        log(f"[anat {key:5s}] n {n:3d} ({row['n_pool_a']}+{row['n_pool_b']}) "
            f"| cutwA edges {row['cutwA']['n_edges']:6d} TOT "
            f"{row['cutwA']['TOT']:10.1f} inh_frac "
            f"{row['cutwA']['inh_frac']:.6f} near "
            f"{row['cutwA']['near']:+.6f} | f4wA inh_frac "
            f"{row['f4wA']['inh_frac']:.6f}")
N_ABOVE_HALF = sum(1 for k in KEYS10 if ANAT[k]["cutwA"]["inh_frac"] > 0.5)
log(f"[0a] pool-sides with cutwA inh_frac > 0.5: {N_ABOVE_HALF} of 10 "
    f"(0 => `near` and `inh_frac` are rank-identical by construction)")

# ---------------- DYNAMICS: lvl per pool-side per arm, from stored npz -----
PATHS = {k: v[0] for k, v in BATCH.items()}
FP0 = {k: (os.stat(v).st_size, os.stat(v).st_mtime_ns)
       for k, v in PATHS.items()}
RAW = {k: np.load(v) for k, v in PATHS.items()}


def side_lvl(raw, arm, seed, pk, side, mask):
    """l208's side_stats expression, restricted to ONE side (L206: a
    float-equality claim is a claim about the EXPRESSION)."""
    ag, bg = PREF[pk]
    cols = [raw[f"{pk}_{ag}{side}_{arm}_{seed}"][:WIN][mask],
            raw[f"{pk}_{bg}{side}_{arm}_{seed}"][:WIN][mask]]
    v = np.concatenate(cols).astype(np.float64)
    return dict(lvl=float(v.mean()), fhi95=float((v >= 0.95).mean()),
                fhi90=float((v >= 0.90).mean()), flo=float((v <= BG).mean()),
                pmax=float(v.max()))


# ---- CERT-208L (halting): reproduce l208's stored lvl/fhi95/flo EXACTLY
S208L = json.load(open("l208/static.json"))
_fp208L = os.stat("l208/static.json")
_FP208L = (_fp208L.st_size, _fp208L.st_mtime_ns)
assert S208L["window"]["n_W"] == int(W.sum()), "L208 window disagrees (STOP)"
assert S208L["window"]["n_W_on"] == int(W_ON.sum()), "L208 W_on (STOP)"
n208 = 2
for bk in ("B36", "B37"):
    raw, seeds, _ = RAW[bk], BATCH[bk][1], BATCH[bk][2]
    for pk in JOINTS:
        for arm in ARMS5:
            st = S208L["arms"][f"{bk}|{pk}|{arm}"]
            for side, suf in (("L", "L"), ("R", "R")):
                rows = [side_lvl(raw, arm, s, pk, side, W) for s in seeds]
                for f in ("lvl", "fhi95", "fhi90", "flo"):
                    got = float(np.mean([r[f] for r in rows]))
                    want = st[{"lvl": "lvl", "fhi95": "fhi95",
                               "fhi90": "fhi90", "flo": "flo"}[f] + suf]
                    assert got == want, ("CERT-208L", bk, pk, arm, side, f,
                                         got, want, "(STOP)")
                    n208 += 1
                got_pmax = float(max(r["pmax"] for r in rows))
                assert got_pmax == st["pmax" + suf], ("CERT-208L pmax", bk,
                                                      pk, arm, side, "(STOP)")
                n208 += 1
assert n208 == 2 + 2 * 2 * 5 * 2 * 5, (n208, "CERT-208L count (STOP)")
log(f"[CERT-208L] GREEN {n208} float equalities (L208 lvl/fhi/flo/pmax) — "
    "this is what licenses reading lvl for SIX NEW pool-sides and 12 arms")

# ---- the measurement proper: every pool-side x every arm x every batch
DYN = {}
for bk in ("B35", "B36", "B37"):
    raw, seeds, arms = RAW[bk], BATCH[bk][1], BATCH[bk][2]
    DYN[bk] = {}
    for J in JOINTS10:
        for side in SIDES:
            key = f"{J}_{side}"
            per_arm = {}
            for arm in arms:
                rows = [side_lvl(raw, arm, s, pk=J, side=side, mask=W)
                        for s in seeds]
                per_arm[arm] = dict(
                    lvl=float(np.mean([r["lvl"] for r in rows])),
                    fhi95=float(np.mean([r["fhi95"] for r in rows])),
                    flo=float(np.mean([r["flo"] for r in rows])),
                    pmax=float(max(r["pmax"] for r in rows)),
                    lvl_sd=float(np.std([r["lvl"] for r in rows])))
            lv = np.array([per_arm[a]["lvl"] for a in arms])
            DYN[bk][key] = dict(
                arms=arms, per_arm=per_arm,
                lvl_max=float(lv.max()), lvl_min=float(lv.min()),
                lvl_mean=float(lv.mean()),
                rng=float(lv.max() - lv.min()),
                rng_rel=float((lv.max() - lv.min()) / lv.mean()),
                arm_max=arms[int(np.argmax(lv))],
                arm_min=arms[int(np.argmin(lv))],
                fhi95_mean=float(np.mean([per_arm[a]["fhi95"] for a in arms])),
                flo_mean=float(np.mean([per_arm[a]["flo"] for a in arms])),
                dead=bool(lv.max() < FLOOR_DEAD))
            d = DYN[bk][key]
            log(f"[dyn {bk} {key:5s}] lvl {d['lvl_min']:.5f}..{d['lvl_max']:.5f} "
                f"(mean {d['lvl_mean']:.5f}) rng {d['rng']:.6f} relrng "
                f"{d['rng_rel']:.4f} | max@{d['arm_max']} min@{d['arm_min']} "
                f"| fhi95 {d['fhi95_mean']:.4f} flo {d['flo_mean']:.4f} "
                f"| DEAD {d['dead']}")
# menu companion: the SAME 7 arms inside B36/B37 (isolates menu from batch)
for bk in ("B36", "B37"):
    for key in KEYS10:
        pa = DYN[bk][key]["per_arm"]
        lv = np.array([pa[a]["lvl"] for a in ARMS7])
        DYN[bk][key]["rng_arms7"] = float(lv.max() - lv.min())

# ---------------- rank machinery: MIDRANK Spearman + EXACT n=10 null -------
def midrank(x):
    x = np.asarray(x, dtype=np.float64)
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), np.float64)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]:
            j += 1
        r[o[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


def spearman_mid(x, y):
    rx, ry = midrank(x), midrank(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = math.sqrt(float((rx * rx).sum()) * float((ry * ry).sum()))
    assert den > 0.0, "degenerate rank vector (STOP)"
    return float((rx * ry).sum() / den)


def ndistinct(x):
    return int(len(set(float(v) for v in x)))


# EXACT enumeration of the n=10 membership-permutation null (PREREG 0g).
# S = sum_i i*perm(i) determines rho when there are no ties, and its
# distribution over all 10! label assignments is independent of which
# permutation x is — so one enumeration serves every n=10 leg.
_N = 10
_S_MIN = sum((i + 1) * (_N - i) for i in range(_N))
_S_MAX = sum((i + 1) * (i + 1) for i in range(_N))
_hist = np.zeros(_S_MAX - _S_MIN + 1, np.int64)
for _p in itertools.permutations(range(1, _N + 1)):
    _hist[(1 * _p[0] + 2 * _p[1] + 3 * _p[2] + 4 * _p[3] + 5 * _p[4]
           + 6 * _p[5] + 7 * _p[6] + 8 * _p[7] + 9 * _p[8] + 10 * _p[9])
          - _S_MIN] += 1
NFACT = int(_hist.sum())
assert NFACT == math.factorial(_N), (NFACT, "enumeration count (STOP)")
_S_VALS = np.arange(_S_MIN, _S_MAX + 1, dtype=np.float64)
_S_CEN = _N * (_N + 1) ** 2 / 4.0
_S_SCALE = _N * (_N * _N - 1) / 12.0
_RHO_NULL = (_S_VALS - _S_CEN) / _S_SCALE
assert abs(_RHO_NULL[0] + 1.0) < 1e-12 and abs(_RHO_NULL[-1] - 1.0) < 1e-12
log(f"[null] EXACT enumeration GREEN: {NFACT:,} permutations, "
    f"{int((_hist > 0).sum())} attainable rho values, "
    f"min two-sided p = {2.0 / NFACT:.3e}")


def exact_p(rho):
    """Exact one- and two-sided p for a tie-free n=10 rank correlation."""
    up = float(_hist[_RHO_NULL >= rho - 1e-12].sum()) / NFACT
    dn = float(_hist[_RHO_NULL <= rho + 1e-12].sum()) / NFACT
    two = float(_hist[np.abs(_RHO_NULL) >= abs(rho) - 1e-12].sum()) / NFACT
    return dict(p_up=up, p_dn=dn, p_two=two)


# ---------------- the registered primary + companions ----------------------
def leg(xname, x, yname, y):
    rho = spearman_mid(x, y)
    nd = (ndistinct(x), ndistinct(y))
    tie_free = nd == (10, 10)
    out = dict(x=xname, y=yname, rho=rho, n=10, n_distinct_x=nd[0],
               n_distinct_y=nd[1], tie_free=bool(tie_free))
    out.update(exact_p(rho) if tie_free else
               dict(p_up=None, p_dn=None, p_two=None))
    return out


NEAR = {s: [ANAT[k][s]["near"] for k in KEYS10] for s in ("cutwA", "f4wA")}
IFRAC = {s: [ANAT[k][s]["inh_frac"] for k in KEYS10] for s in ("cutwA", "f4wA")}
NCELLS = [ANAT[k]["n_cells"] for k in KEYS10]
TOTM = [ANAT[k]["cutwA"]["TOT"] for k in KEYS10]
RNG = {bk: [DYN[bk][k]["rng"] for k in KEYS10] for bk in BATCH}
RNGREL = {bk: [DYN[bk][k]["rng_rel"] for k in KEYS10] for bk in BATCH}
LVLM = {bk: [DYN[bk][k]["lvl_mean"] for k in KEYS10] for bk in BATCH}

LEGS = {}
LEGS["primary"] = leg("near_cutwA", NEAR["cutwA"], "rng_B36", RNG["B36"])
LEGS["replication_B37"] = leg("near_cutwA", NEAR["cutwA"], "rng_B37",
                              RNG["B37"])
LEGS["menu_B35"] = leg("near_cutwA", NEAR["cutwA"], "rng_B35", RNG["B35"])
LEGS["currency_ifrac_B36"] = leg("inh_frac_cutwA", IFRAC["cutwA"], "rng_B36",
                                 RNG["B36"])
LEGS["substrate_f4wA_B36"] = leg("near_f4wA", NEAR["f4wA"], "rng_B36",
                                 RNG["B36"])
LEGS["relrange_B36"] = leg("near_cutwA", NEAR["cutwA"], "rng_rel_B36",
                           RNGREL["B36"])
LEGS["arms7_B36"] = leg("near_cutwA", NEAR["cutwA"], "rng_arms7_B36",
                        [DYN["B36"][k]["rng_arms7"] for k in KEYS10])
LEGS["level_B36"] = leg("near_cutwA", NEAR["cutwA"], "lvl_mean_B36",
                        LVLM["B36"])
LEGS["confound_near_ncells"] = leg("near_cutwA", NEAR["cutwA"], "n_cells",
                                   NCELLS)
LEGS["confound_near_TOT"] = leg("near_cutwA", NEAR["cutwA"], "TOT_cutwA",
                                TOTM)
LEGS["confound_rng_ncells"] = leg("rng_B36", RNG["B36"], "n_cells", NCELLS)
LEGS["confound_rng_TOT"] = leg("rng_B36", RNG["B36"], "TOT_cutwA", TOTM)
LEGS["batch_agreement_B36_B37"] = leg("rng_B36", RNG["B36"], "rng_B37",
                                      RNG["B37"])
for nm, L in LEGS.items():
    log(f"[leg {nm:26s}] rho {L['rho']:+.6f} | distinct "
        f"{L['n_distinct_x']}/{L['n_distinct_y']} tie_free {L['tie_free']} | "
        f"p_up {L['p_up']} p_two {L['p_two']}")

# ---------------- branches, in the REGISTERED order ------------------------
DEAD = [k for k in KEYS10 if DYN["B36"][k]["dead"]]
DEAD_ANY = sorted({k for bk in BATCH for k in KEYS10 if DYN[bk][k]["dead"]})
rho_p = LEGS["primary"]["rho"]
rho_37 = LEGS["replication_B37"]["rho"]
rho_35 = LEGS["menu_B35"]["rho"]
c_nc = LEGS["confound_near_ncells"]["rho"]
c_tot = LEGS["confound_near_TOT"]["rho"]

BRANCH = None
if DEAD:
    BRANCH = "B_FLOOR_DEGENERATE"
elif abs(c_nc) >= BAND_STRONG or abs(c_tot) >= BAND_STRONG:
    BRANCH = "B_CONFOUNDED"
elif (rho_p >= BAND_STRONG
      and (rho_37 > 0) == (rho_p > 0) and (rho_35 > 0) == (rho_p > 0)):
    BRANCH = "B_BALANCE_PREDICTS"
elif rho_p >= BAND_WEAK:
    BRANCH = "B_SUGGESTIVE"
elif rho_p <= -BAND_WEAK:
    BRANCH = "B_INVERTS"
else:
    BRANCH = "B_UNINFORMATIVE"

# B_FLOOR_DEGENERATE SHORT-CIRCUITS the population claim (L222) — the
# surviving-subset reading is computed only on that branch, and the branch
# records that the ten units are not comparable.
SURV = None
if BRANCH == "B_FLOOR_DEGENERATE":
    alive = [k for k in KEYS10 if not DYN["B36"][k]["dead"]]
    nal = len(alive)
    if nal >= 4:
        xs = [ANAT[k]["cutwA"]["near"] for k in alive]
        ys = [DYN["B36"][k]["rng"] for k in alive]
        SURV = dict(n=nal, keys=alive, rho=spearman_mid(xs, ys),
                    note=("exact n=10 null does NOT apply at this n; "
                          "p withheld rather than approximated"))
    else:
        SURV = dict(n=nal, keys=alive, rho=None,
                    note="too few surviving pool-sides to rank")
POP_CLAIM_AVAILABLE = BRANCH != "B_FLOOR_DEGENERATE"
log(f"[BRANCH] {BRANCH} | dead(B36) {DEAD} dead(any batch) {DEAD_ANY} | "
    f"rho primary {rho_p:+.4f} B37 {rho_37:+.4f} B35 {rho_35:+.4f} | "
    f"confound ncells {c_nc:+.4f} TOT {c_tot:+.4f} | "
    f"population claim available: {POP_CLAIM_AVAILABLE}")
if SURV is not None:
    log(f"[surviving subset] n {SURV['n']} rho "
        f"{'None' if SURV['rho'] is None else format(SURV['rho'], '+.6f')}")

# ---------------- predictions, scored AS WRITTEN ---------------------------
near_rank = midrank(NEAR["cutwA"])
tr_ranks = {k: float(near_rank[KEYS10.index(k)]) for k in ("Tr_L", "Tr_R")}
P = {}
P["P1_all_below_half"] = dict(
    registered="all ten cutwA inh_frac < 0.5 => near and inh_frac rank-identical",
    n_above_half=N_ABOVE_HALF,
    rank_identical=bool(spearman_mid(NEAR["cutwA"], IFRAC["cutwA"]) == 1.0),
    result=bool(N_ABOVE_HALF == 0))
P["P2_primary_positive"] = dict(registered="rho(near, rng_B36) > 0",
                                rho=rho_p, result=bool(rho_p > 0))
P["P3_Tr_most_balanced"] = dict(
    registered="Tr_L and Tr_R are the two highest `near` ranks (9 and 10)",
    tr_near_ranks=tr_ranks,
    result=bool(sorted(tr_ranks.values()) == [9.0, 10.0]))
P["P4_not_strong"] = dict(
    registered="branch is NOT B_BALANCE_PREDICTS",
    branch=BRANCH, result=bool(BRANCH != "B_BALANCE_PREDICTS"))
P["P5_three_batch_sign"] = dict(
    registered="rho(near, rng) agrees in SIGN across B35/B36/B37",
    rhos=[rho_35, rho_p, rho_37],
    result=bool((rho_35 > 0) == (rho_p > 0) == (rho_37 > 0)))
P["P6_some_dead"] = dict(
    registered="at least one pool-side has max-over-arms level < 0.04",
    dead_B36=DEAD, dead_any=DEAD_ANY, result=bool(len(DEAD_ANY) > 0))
NP_TRUE = sum(1 for v in P.values() if v["result"])
for k, v in P.items():
    log(f"[pred {k:22s}] {'TRUE ' if v['result'] else 'FALSE'} | "
        f"{v['registered']}")
log(f"[predictions] {NP_TRUE} of {len(P)} TRUE")

# ---------------- fingerprints + write ------------------------------------
for k, v in PATHS.items():
    st = os.stat(v)
    assert (st.st_size, st.st_mtime_ns) == FP0[k], (k, "npz mutated (STOP)")
for nm, (pth, fp) in {"l215/static.json": ("l215/static.json", _FP215),
                      "l208/static.json": ("l208/static.json", _FP208L)}.items():
    st = os.stat(pth)
    assert (st.st_size, st.st_mtime_ns) == fp, (nm, "prior json mutated (STOP)")
log("[fingerprints] all npz + prior json UNCHANGED after the run")

o["design"] = ("L229 near-balance as a POPULATION question (static): "
               "per-pool-side inhibitory in-mass fraction for ALL TEN cord "
               "pool-sides (Ti/Tr/Ta/Sr/Pr x L/R) against each pool-side's "
               "dynamic range over the stored arms, with an EXACT n=10 "
               "membership-permutation null. Zero rollouts, zero dynamics.")
o["prereg"] = "l229/PREREG.md"
o["cert"] = dict(cert_W=True, cert_215R=n215, cert_208L=n208,
                 nfact=NFACT, attainable_rho=int((_hist > 0).sum()))
o["pool_sides"] = KEYS10
o["anat"] = ANAT
o["n_above_half"] = N_ABOVE_HALF
o["dyn"] = DYN
o["legs"] = LEGS
o["dead"] = dict(B36=DEAD, any_batch=DEAD_ANY, bar=FLOOR_DEAD)
o["band"] = dict(strong=BAND_STRONG, weak=BAND_WEAK)
o["branch"] = BRANCH
o["population_claim_available"] = bool(POP_CLAIM_AVAILABLE)
o["surviving_subset"] = SURV
o["predictions"] = P
o["n_predictions_true"] = NP_TRUE
o["limits"] = (
    "One connectome (BANC v626 female cord), one operating-point family, "
    "pool MEANS only (per-cell ceiling fraction is not recoverable from "
    "stored traces — L208's declared limit), TEN units, and the six new "
    "pool-sides are 7-19 cells against Ti/Tr's 55-57. inh_frac is an "
    "ANATOMICAL in-mass ratio under the log1p ladder convention, not a "
    "measured E/I current balance. Correlation over ten pool-sides with an "
    "exact null is a population DESCRIPTION, not causality in either "
    "direction. L215's four Ti/Tr inh_frac values and three of l208's Ti "
    "lvl values were READ while scoping and are declared DESCRIPTION in "
    "PREREG 0h; every branch sits on unobserved quantities.")
o["npz_fingerprints"] = {k: list(v) for k, v in FP0.items()}
o["tail_sha"] = hashlib.sha256(open(__file__).read().encode()).hexdigest()
json.dump(o, open("l229/static.json", "w"), indent=1)
log("[done] wrote l229/static.json")
log(f"[verdict] branch {BRANCH} | predictions {NP_TRUE}/{len(P)} | "
    f"primary rho {rho_p:+.6f} p_two {LEGS['primary']['p_two']}")
