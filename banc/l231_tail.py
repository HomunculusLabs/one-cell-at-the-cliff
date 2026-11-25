# ================= L231 BODY (appended by l231_build.py) ==================
# Above this line: SLICE A (l216_static.py 1-1360), the L231 HEAD (P), and
# SLICE C = l230_tail.py lines 39-128 VERBATIM — L230's own CERT-216 block
# (artifact-derived ~1,900-leaf coverage gate) plus leafcmp/leaves and the
# lam1 NO-OP re-assertion, re-used as the code that passed it in tick 262
# (the L225 law: re-use a prior card's CERTIFICATION BLOCK as a verbatim
# source slice, not its statistic).
# This body adds ONLY: the global side/class/region label vectors, the unit
# construction, the whole-graph arm, the per-unit asymmetry of v1 with its
# membership-permutation null (exact where enumerable), BH-FDR over the whole
# family, the confound legs and the registered branch.
import itertools
from math import comb

log("=" * 72)
log("[L231] certifications inherited; building the nonselective family")

CMAX_ENUM = 200000
NDRAW_BIG = 5000
NDRAW_SM = 20000
N_TIER = 5000
SEED_SIDE = 231231
Q_BH = 0.05
PRIMARY_ARM = "f4wA|beta"
EPS8 = 8.0 * EPS

# ---------------- global label vectors (l217's sup_glob expression form) ---
sup_glob = np.full(Nall, "", dtype=object)
sup_glob[ann_gi] = sup
region_glob = np.full(Nall, "", dtype=object)
region_glob[ann_gi] = region
_sd = ann.side.fillna("").astype(str).str.lower().to_numpy()
side_glob = np.full(Nall, "", dtype=object)
side_glob[ann_gi] = _sd
isL_glob = (side_glob == "left")
isR_glob = (side_glob == "right")

# CENSUS PIN (HALTING) — the tooling probe's declared numbers (PREREG 0a-2).
assert int(isL_glob.sum()) == 26799, int(isL_glob.sum())
assert int(isR_glob.sum()) == 53050, int(isR_glob.sum())
assert int((side_glob == "midline").sum()) == 11
assert len(ann) == Nall == 80635, (len(ann), Nall)
CENSUS = {}
for _rg in ("ventral_nerve_cord", "central_brain", "optic_lobe",
            "neck_connective", "brain", ""):
    _m = region_glob == _rg
    CENSUS[_rg or "unlabelled"] = dict(
        n_L=int((_m & isL_glob).sum()), n_R=int((_m & isR_glob).sum()))
assert CENSUS["optic_lobe"] == dict(n_L=3311, n_R=27799), CENSUS["optic_lobe"]
assert CENSUS["ventral_nerve_cord"] == dict(n_L=10070, n_R=10494)
log("[census] HALTING PIN GREEN — side labels left 26799 / right 53050 / "
    "midline 11; optic_lobe L 3311 R 27799 (8.40:1 RIGHT) vs "
    "ventral_nerve_cord L 10070 R 10494 (0.96) = the RECONSTRUCTION caveat, "
    "measured")
P["side_census"] = dict(
    n_left=int(isL_glob.sum()), n_right=int(isR_glob.sum()),
    n_midline=11, n_unlabelled=int((side_glob == "").sum()),
    by_region=CENSUS,
    note="BANC v626 reconstructs one optic lobe far more completely than the "
         "other; the whole labelled population is right-heavy 2.0:1 in CELL "
         "COUNT while the ventral nerve cord, where L216's finding lives, is "
         "balanced to 0.96. Declared in PREREG 0a-2 as OBSERVED before "
         "registration.")

# ---------------- CERT-231B (HALTING): the ten pool-sides ------------------
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
JOINTS10 = ["Ti", "Tr", "Ta", "Sr", "Pr"]
SIDES = ["L", "R"]
SIDEMASK10, NCELL10, NPOOL10 = {}, {}, {}
_n231b = 0
for J in JOINTS10:
    ag, bg = PREF[J]
    for side in SIDES:
        ma = POOL_G[f"{J}_{ag}{side}"] & keep_wA
        mb = POOL_G[f"{J}_{bg}{side}"] & keep_wA
        na, nb = int(ma.sum()), int(mb.sum())
        assert na == S101[f"{J}_a{side}"], (J, side, na, "a size (STOP)")
        assert nb == S101[f"{J}_b{side}"], (J, side, nb, "b size (STOP)")
        assert int((ma & mb).sum()) == 0, (J, side, "a/b overlap (STOP)")
        _n231b += 3
        SIDEMASK10[(J, side)] = ma | mb
        NCELL10[(J, side)] = na + nb
        NPOOL10[(J, side)] = (na, nb)
# the Ti/Tr masks must be REPRODUCED by GROUPS, the object L216 itself used
for J in JOINTS:
    for side in SIDES:
        cf, isLf = GROUPS[(J, "f")]
        ce, isLe = GROUPS[(J, "e")]
        selF = isLf if side == "L" else ~isLf
        selE = isLe if side == "L" else ~isLe
        _m = np.zeros(Nall, bool)
        _m[cf[selF]] = True
        _m[ce[selE]] = True
        assert np.array_equal(_m, SIDEMASK10[(J, side)]), \
            (J, side, "pool-side mask disagrees with GROUPS (STOP)")
        _n231b += 1
# every pool cell must carry the side label its pool name asserts
for J in JOINTS10:
    for side in SIDES:
        _c = np.where(SIDEMASK10[(J, side)])[0]
        _want = "left" if side == "L" else "right"
        assert all(side_glob[g] == _want for g in _c), (J, side, "side label")
        _n231b += 1
log(f"[CERT-231B] GREEN {_n231b} structural checks — 10 pool-sides built by "
    f"L229's construction, all 20 S101 per-side sizes pinned, the four Ti/Tr "
    f"masks ARRAY-IDENTICAL to the GROUPS object L216 used, and every pool "
    f"cell's annotation `side` agrees with its pool name")
log("  " + " ".join(f"{J}_{s}:{NCELL10[(J, s)]}"
                    for J in JOINTS10 for s in SIDES))
P["cert_231b"] = dict(n_checks=_n231b, pool_sides={
    f"{J}_{s}": dict(n=NCELL10[(J, s)], n_a=NPOOL10[(J, s)][0],
                     n_b=NPOOL10[(J, s)][1])
    for J in JOINTS10 for s in SIDES})

# ---------------- the WHOLE-GRAPH arm (PREREG 0d/0e) ----------------------
keep_all = np.ones(Nall, bool)
emask_all = np.ones(len(src_all), bool)
S_WHOLE = build_sub(keep_all, emask_all, "whole")
assert S_WHOLE["n"] == Nall and S_WHOLE["n_edges"] == len(src_all)
log(f"[whole] built by the CERTIFIED generic builder: n {S_WHOLE['n']} "
    f"edges {S_WHOLE['n_edges']}")


def perron_residual(s, jv, lam, v):
    """||A v - lam v|| / (lam ||v||) — L217's law: diagnose an eigenpair with
    its RESIDUAL, never with the iteration's convergence spread."""
    y = np.zeros(s["n"])
    np.add.at(y, s["rows"], jv * v[s["cols"]])
    return (float(np.linalg.norm(y - lam * v) / (lam * np.linalg.norm(v))),
            float(np.linalg.norm(y)))


ARMS = {}
for sname in SUBS:
    for op in ("beta", "crofts"):
        lam1, v1, u1, inf_r, inf_l = PERRON[(sname, op)]
        res, nrm = perron_residual(SUBS[sname], OPS[sname][op], lam1, v1)
        ARMS[f"{sname}|{op}"] = dict(sub=SUBS[sname], jv=OPS[sname][op],
                                     v1=v1, lam=lam1, scope="restricted",
                                     residual=res, spread=inf_r["rel_spread_last6"],
                                     kind="cord")
_lamw, _v1w, _infw = pi_sub(S_WHOLE, S_WHOLE["jv"])
assert float(_v1w.min()) >= -1e-14, "whole-graph Perron vector not nonneg"
_v1w = np.abs(_v1w)
_resw, _ = perron_residual(S_WHOLE, S_WHOLE["jv"], _lamw, _v1w)
RES_BAR = 1e-3
WHOLE_OK = bool(_resw < RES_BAR)
for _k, _a in ARMS.items():
    log(f"[PI residual] {_k:14s} lam1 {_a['lam']:.6g} residual "
        f"{_a['residual']:.3e} (spread {_a['spread']:.2e})")
log(f"[PI residual] {'whole|beta':14s} lam1 {_lamw:.6g} residual "
    f"{_resw:.3e} (spread {_infw['rel_spread_last6']:.2e}) -> "
    f"{'RESOLVED' if WHOLE_OK else 'UNRESOLVED'} at bar {RES_BAR:.0e}")
if WHOLE_OK:
    ARMS["whole|beta"] = dict(sub=S_WHOLE, jv=S_WHOLE["jv"], v1=_v1w,
                              lam=_lamw, scope="any", residual=_resw,
                              spread=_infw["rel_spread_last6"], kind="whole")
P["arms"] = {k: dict(lam1=a["lam"], residual=a["residual"],
                     rel_spread_last6=a["spread"], kind=a["kind"])
             for k, a in ARMS.items()}
P["whole_graph_arm"] = dict(
    lam1=_lamw, residual=_resw, rel_spread_last6=_infw["rel_spread_last6"],
    residual_bar=RES_BAR, resolved=WHOLE_OK, n=int(S_WHOLE["n"]),
    n_edges=int(S_WHOLE["n_edges"]),
    cord_arm_residual_calibration={k: a["residual"] for k, a in ARMS.items()
                                   if a["kind"] == "cord"},
    note="PREREG 0e: accepted only on the RESIDUAL, with the four certified "
         "cord arms printed as the calibration reference. Beta only "
         "(PREREG 0d).")

# ---------------- the UNITS (PREREG 0j, nonselective) ---------------------
UNITS = {}


def add_unit(name, leg, mask, scope):
    mL = mask & isL_glob
    mR = mask & isR_glob
    nL, nR = int(mL.sum()), int(mR.sum())
    if nL < 2 or nR < 2:
        return False
    cl, cr = np.where(mL)[0], np.where(mR)[0]
    cells = np.concatenate([cl, cr])
    isL = np.zeros(len(cells), bool)
    isL[:nL] = True
    UNITS[name] = dict(leg=leg, scope=scope, cells=cells, isL=isL,
                       n_L=nL, n_R=nR)
    return True


for J in JOINTS10:
    _m = SIDEMASK10[(J, "L")] | SIDEMASK10[(J, "R")]
    assert add_unit(f"pool/{J}", "a_pools", _m, "restricted"), J
    _u = UNITS[f"pool/{J}"]
    assert np.array_equal(np.where(SIDEMASK10[(J, "L")])[0],
                          _u["cells"][_u["isL"]]), (J, "L split (STOP)")
    assert np.array_equal(np.where(SIDEMASK10[(J, "R")])[0],
                          _u["cells"][~_u["isL"]]), (J, "R split (STOP)")

CLS_SUB = sorted(set(sup_glob[keep_wA].tolist()))
for c in CLS_SUB:
    add_unit(f"class/{c}", "b_class", (sup_glob == c) & keep_wA, "restricted")
add_unit("pop/all", "c_pop", keep_wA.copy(), "restricted")
for rg in ("ventral_nerve_cord", "central_brain", "optic_lobe",
           "neck_connective"):
    add_unit(f"pop/{rg}", "c_pop", (region_glob == rg) & keep_wA, "restricted")

# WHOLE-GRAPH NATIVE units (scored on whole|beta only)
add_unit("wg/pop/all", "c_whole", keep_all.copy(), "whole")
for rg in ("ventral_nerve_cord", "central_brain", "optic_lobe",
           "neck_connective"):
    add_unit(f"wg/pop/{rg}", "c_whole", region_glob == rg, "whole")
for c in sorted(set(sup_glob.tolist())):
    if c:
        add_unit(f"wg/class/{c}", "c_whole", sup_glob == c, "whole")

log(f"[units] {len(UNITS)} units: "
    + ", ".join(f"{lg}:{sum(1 for u in UNITS.values() if u['leg'] == lg)}"
                for lg in ("a_pools", "b_class", "c_pop", "c_whole")))
log(f"[units] substrate super_classes: {CLS_SUB}")

# ---------------- CERT-231A (HALTING): the general statistic == A_inf -----
# PREREG 0h: my general unit sum and side_stats_from's two-sub-sum expression
# are the same real number by DIFFERENT expressions (L218), so the gate is a
# DERIVED bracket against the values CERT-216 has already pinned at float
# equality.
def unit_stat(v1, loc, u):
    lv = loc[u["cells"]]
    assert (lv >= 0).all(), "unit cell absent from arm substrate (STOP)"
    x = np.asarray(v1, float)[lv]
    nL, nR = u["n_L"], u["n_R"]
    mL = float(x[u["isL"]].sum()) / nL
    mR = float(x[~u["isL"]].sum()) / nR
    return asym(mL, mR), x, mL, mR


_maxrel231 = 0.0
_maxabs231 = 0.0
_cond231 = 0.0
_n231a = 0
for sname in SUBS:
    for op in ("beta", "crofts"):
        _v1 = PERRON[(sname, op)][1]
        _loc = SUBS[sname]["loc"]
        for J in JOINTS:
            _a, _x, _, _ = unit_stat(_v1, _loc, UNITS[f"pool/{J}"])
            _cert = AINF[(sname, op, J)]["A_cell"]
            _ab = abs(_a - _cert)
            _rel = _ab / abs(_cert)
            # TOOLING FIX, disclosed (made after the PREREG; changes no
            # registered quantity). The first run gated on the RELATIVE
            # difference and HALTED at cutwA|crofts|Ti, rel 8.45e-15 against
            # 8*eps — the one cell whose A_inf is indistinguishable from zero
            # (-0.008413). A = (mL-mR)/(mL+mR) amplifies a relative
            # perturbation of its summands by 1/|A| (here 119x), so a
            # relative bracket on a near-zero ratio demands more precision
            # than the quantity carries. A is bounded in [-1,1], so its
            # ABSOLUTE resolution is what eps means here: the gate is the
            # ABSOLUTE bracket and the relative value is REPORTED beside its
            # conditioning factor.
            assert _ab <= EPS8, (sname, op, J, _a, _cert, _ab,
                                 "CERT-231A absolute bracket (STOP)")
            _maxabs231 = max(_maxabs231, _ab)
            _maxrel231 = max(_maxrel231, _rel)
            _cond231 = max(_cond231, 1.0 / abs(_cert))
            _n231a += 1
assert _n231a == 8, _n231a
log(f"[CERT-231A] GREEN {_n231a} cells — the general per-unit statistic "
    f"reproduces every CERT-216-pinned A_inf within max ABSOLUTE "
    f"{_maxabs231:.3e} (bar 8*eps = {EPS8:.3e}); max relative "
    f"{_maxrel231:.3e} at a worst conditioning factor 1/|A| of "
    f"{_cond231:.1f}; the four BETA pool cells are the card's own Verify line")
P["cert_231a"] = dict(n_checks=_n231a, max_abs_diff=_maxabs231,
                      max_rel_diff=_maxrel231, worst_conditioning=_cond231,
                      bar=EPS8, mode="derived ABSOLUTE bracket (PREREG 0h, "
                                     "currency repaired after a halt)",
                      certified_by="CERT-216 float equality vs "
                                   "l216/static.json A_inf",
                      halt_note="the relative form halted at cutwA|crofts|Ti "
                                "(A_inf -0.008413, 1/|A| = 118.9): a ratio of "
                                "a difference of sums is ill-conditioned near "
                                "zero, and a statistic bounded in [-1,1] is "
                                "gated on its ABSOLUTE resolution.")


# ---------------- the null (PREREG 0f) ------------------------------------
def n_assign(n, nL):
    """C(n, nL), computed ONLY where the answer can possibly be <= CMAX_ENUM.
    A bare math.comb(79849, 26799) is a 22,000-digit integer: the guard is a
    cost guard, and it is CONSERVATIVE (it can only over-report, never
    under-report, the assignment count)."""
    k = min(nL, n - nL)
    if k <= 1:
        return n
    if (k <= 6 and n <= 2000) or n <= 45:
        return comb(n, k)
    return CMAX_ENUM + 1


def null_dist(x, nL):
    """Membership permutation holding n_L / n_R EXACT. Exact enumeration when
    C(n,nL) <= CMAX_ENUM, else a size-tiered sampled null (PREREG 0f)."""
    n = len(x)
    nR = n - nL
    tot = float(x.sum())
    c = n_assign(n, nL)
    if c <= CMAX_ENUM:
        k_small = min(nL, nR)
        small_is_L = nL <= nR
        out = np.empty(c)
        k = 0
        for idx in itertools.combinations(range(n), k_small):
            s = float(x[list(idx)].sum())
            sL = s if small_is_L else tot - s
            a, b = sL / nL, (tot - sL) / nR
            out[k] = (a - b) / (a + b) if (a + b) else 0.0
            k += 1
        assert k == c == comb(n, k_small), (k, c, "enumeration count (STOP)")
        return out, "exact", c, 0.0
    B = NDRAW_SM if n <= N_TIER else NDRAW_BIG
    rng = np.random.default_rng(SEED_SIDE)
    out = np.empty(B)
    done = 0
    CH = max(25, min(4000, int(2.0e7 // max(n, 1))))   # memory-bounded chunk
    while done < B:
        k = min(CH, B - done)
        M = np.tile(x, (k, 1))
        M = rng.permuted(M, axis=1)
        sL = M[:, :nL].sum(axis=1)
        a, b = sL / nL, (tot - sL) / nR
        out[done:done + k] = (a - b) / (a + b)
        done += k
    return out, "sampled", B, 1.0 / (B + 1)


ROWS = {}
_t_null = time.time()
for aname, arm in ARMS.items():
    loc = arm["sub"]["loc"]
    s = arm["sub"]
    inm = np.zeros(s["n"])
    np.add.at(inm, s["rows"], arm["jv"])
    for uname, u in UNITS.items():
        if u["scope"] == "restricted" and arm["kind"] == "cord":
            pass
        elif u["scope"] == "restricted" and arm["kind"] == "whole":
            pass
        elif u["scope"] == "whole" and arm["kind"] == "whole":
            pass
        else:
            continue
        A, x, mL, mR = unit_stat(arm["v1"], loc, u)
        nd, mode, nn, floor = null_dist(x, u["n_L"])
        if mode == "exact":
            p = float((np.abs(nd) >= abs(A)).mean())
            p_up = float((nd >= A).mean())
        else:
            p = float((1 + int((np.abs(nd) >= abs(A)).sum())) / (nn + 1))
            p_up = float((1 + int((nd >= A).sum())) / (nn + 1))
        # a membership null on a per-cell MEAN asymmetry is centred near zero,
        # but it is NOT exactly symmetric when n_L != n_R (the statistic is a
        # ratio), so the gate is scoped to the null's OWN spread and the mean
        # and median are both REPORTED rather than assumed (L218: never phrase
        # a numerical guard so broadly that it fires on a structural fact).
        _nm = float(nd.mean())
        _ns = float(nd.std())
        _nmed = float(np.median(nd))
        assert abs(_nm) <= 0.5 * _ns + 1e-12, \
            (aname, uname, _nm, _ns, "null not centred (STOP)")
        lv = loc[u["cells"]]
        MinL = float(inm[lv[u["isL"]]].sum())
        MinR = float(inm[lv[~u["isL"]]].sum())
        ROWS[f"{aname}||{uname}"] = dict(
            arm=aname, unit=uname, leg=u["leg"], n_L=u["n_L"], n_R=u["n_R"],
            A_n=asym(u["n_L"], u["n_R"]),
            M_in_L=MinL, M_in_R=MinR,
            A_inmass=asym(MinL / u["n_L"], MinR / u["n_R"]),
            A_v1=A, mean_L=mL, mean_R=mR,
            p_two=p, p_up=p_up, null_mode=mode, null_n=nn,
            null_floor=floor, null_mean=_nm, null_sd=_ns, null_median=_nmed,
            null_p05=float(np.percentile(nd, 5)),
            null_p95=float(np.percentile(nd, 95)))
log(f"[null] {len(ROWS)} (arm, unit) tests measured in "
    f"{time.time()-_t_null:.0f}s")

# L216's OWN null percentile reported beside the union null for Ti/Tr (0g)
P["l216_null_comparison"] = {}
for sname in SUBS:
    for op in ("beta", "crofts"):
        for J in JOINTS:
            k = f"{sname}|{op}||pool/{J}"
            P["l216_null_comparison"][k] = dict(
                union_null_p_two=ROWS[k]["p_two"],
                union_null_mode=ROWS[k]["null_mode"],
                l216_pct_abs=AINF[(sname, op, J)]["A_cell_pct_abs"],
                l216_pct_up=AINF[(sname, op, J)]["A_cell_pct_up"],
                note="DIFFERENT NULLS on the same real value (PREREG 0g): "
                     "L216 permutes within flexor and within extensor "
                     "separately; this card permutes within the pool-side "
                     "union because the six new pool-sides and every class "
                     "and population unit have no antagonist split.")

# ---------------- BH-FDR over the WHOLE family (PREREG 0i) ----------------
KEYS = sorted(ROWS)
M_FAM = len(KEYS)
_pv = np.array([ROWS[k]["p_two"] for k in KEYS])
_ord = np.argsort(_pv, kind="mergesort")
_thr = Q_BH * (np.arange(1, M_FAM + 1)) / M_FAM
_below = _pv[_ord] <= _thr
_kmax = int(np.where(_below)[0].max()) + 1 if _below.any() else 0
_rej = set(int(i) for i in _ord[:_kmax])
for i, k in enumerate(KEYS):
    ROWS[k]["bh_rank"] = int(np.where(_ord == i)[0][0]) + 1
    ROWS[k]["bh_sig"] = bool(i in _rej)
    ROWS[k]["bh_bar"] = float(Q_BH * ROWS[k]["bh_rank"] / M_FAM)
FLOOR_MAX = max(ROWS[k]["null_floor"] for k in KEYS)
BAR_RANK1 = Q_BH / M_FAM
log(f"[BH] family m={M_FAM}, q={Q_BH}, rank-1 bar {BAR_RANK1:.3e}, worst "
    f"resolution floor {FLOOR_MAX:.3e} "
    f"({'REJECTABLE' if FLOOR_MAX <= BAR_RANK1 else 'FLOOR BLOCKS RANK 1'}), "
    f"rejections {len(_rej)}/{M_FAM}")
P["bh"] = dict(m=M_FAM, q=Q_BH, bar_rank1=BAR_RANK1,
               worst_resolution_floor=FLOOR_MAX,
               rank1_rejectable=bool(FLOOR_MAX <= BAR_RANK1),
               n_rejected=len(_rej),
               n_exact_null=sum(1 for k in KEYS
                                if ROWS[k]["null_mode"] == "exact"))

# ---------------- the rank statistics (MIDRANK, L221) ---------------------
def midrank(a):
    a = np.asarray(a, float)
    o = np.argsort(a, kind="mergesort")
    r = np.empty(len(a))
    sa = a[o]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sa[j + 1] == sa[i]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = midrank(a), midrank(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    d = float(np.sqrt(float((ra * ra).sum()) * float((rb * rb).sum())))
    return float((ra * rb).sum() / d) if d > 0 else None


CONF = {}
for aname in ARMS:
    ks = [k for k in KEYS if ROWS[k]["arm"] == aname]
    if len(ks) < 4:
        continue
    av = [ROWS[k]["A_v1"] for k in ks]
    an = [ROWS[k]["A_n"] for k in ks]
    am = [ROWS[k]["A_inmass"] for k in ks]
    CONF[aname] = dict(
        n_units=len(ks),
        rho_A_count=spearman(av, an), rho_A_inmass=spearman(av, am),
        distinct_A_v1=len(set(av)), distinct_A_n=len(set(an)),
        distinct_A_inmass=len(set(am)),
        ties_A_n=bool(len(set(an)) < len(an)),
        ties_A_inmass=bool(len(set(am)) < len(am)))
    log(f"[confound] {aname:14s} n {len(ks):3d} rho(A_v1,A_count) "
        f"{CONF[aname]['rho_A_count']:+.4f} rho(A_v1,A_inmass) "
        f"{CONF[aname]['rho_A_inmass']:+.4f} "
        f"(distinct {CONF[aname]['distinct_A_v1']}/"
        f"{CONF[aname]['distinct_A_n']}/{CONF[aname]['distinct_A_inmass']})")
P["confound"] = CONF

# ---------------- the registered BRANCH (PREREG section 1) ----------------
_gk = f"{PRIMARY_ARM}||pop/all"
A_GLOB = ROWS[_gk]["A_v1"]
GLOB_SIG = ROWS[_gk]["bh_sig"]
POOLA = [ROWS[f"{PRIMARY_ARM}||pool/{J}"]["A_v1"] for J in JOINTS10]
POOLSIG = [ROWS[f"{PRIMARY_ARM}||pool/{J}"]["bh_sig"] for J in JOINTS10]
MED_POOL_ABS = float(np.median(np.abs(POOLA)))
MED_POOL = float(np.median(POOLA))
R_GLOB = abs(A_GLOB) / MED_POOL_ABS
N_POOL_SIG = int(sum(POOLSIG))
CLS_SIG = [(k, ROWS[k]["A_v1"]) for k in KEYS
           if ROWS[k]["arm"] == PRIMARY_ARM and ROWS[k]["leg"] == "b_class"
           and ROWS[k]["bh_sig"] and abs(ROWS[k]["A_v1"]) >= 0.10]
_rc = CONF[PRIMARY_ARM]["rho_A_count"]
F_CONFOUND = bool(_rc is not None and abs(_rc) >= 0.70
                  and np.sign(_rc) == np.sign(A_GLOB if A_GLOB else 1.0))

if (np.sign(A_GLOB) != np.sign(MED_POOL)) and GLOB_SIG:
    BRANCH = "B_SIGN_OPPOSED"
elif R_GLOB >= 0.50:
    BRANCH = "B_GLOBAL"
elif R_GLOB >= 0.15:
    BRANCH = "B_PARTIAL_GLOBAL"
elif N_POOL_SIG >= 3:
    BRANCH = "B_POOL_SPECIFIC"
elif len(CLS_SIG) >= 1:
    BRANCH = "B_CLASS_SPECIFIC"
else:
    BRANCH = "B_UNREGISTERED_SHAPE"

log("=" * 72)
log(f"[BRANCH] {BRANCH}  (primary arm {PRIMARY_ARM})")
log(f"  A_glob(pop/all) {A_GLOB:+.6f} p {ROWS[_gk]['p_two']:.3e} "
    f"BH-sig {GLOB_SIG} | median pool |A| {MED_POOL_ABS:.6f} "
    f"-> R_glob {R_GLOB:.4f}")
log(f"  pools: " + " ".join(
    f"{J} {ROWS[f'{PRIMARY_ARM}||pool/{J}']['A_v1']:+.4f}"
    f"{'*' if ROWS[f'{PRIMARY_ARM}||pool/{J}']['bh_sig'] else ''}"
    for J in JOINTS10) + f" | {N_POOL_SIG}/5 BH-significant")
log(f"  classes |A|>=0.10 and BH-sig: {[(k.split('||')[1], round(v, 4)) for k, v in CLS_SIG]}")
log(f"  F_CONFOUND {F_CONFOUND} (rho(A_v1,A_count) {_rc:+.4f})")
P["branch"] = BRANCH
P["branch_inputs"] = dict(
    primary_arm=PRIMARY_ARM, A_glob=A_GLOB, glob_p_two=ROWS[_gk]["p_two"],
    glob_bh_sig=GLOB_SIG, glob_n_L=ROWS[_gk]["n_L"], glob_n_R=ROWS[_gk]["n_R"],
    pool_A={J: ROWS[f"{PRIMARY_ARM}||pool/{J}"]["A_v1"] for J in JOINTS10},
    pool_bh_sig={J: ROWS[f"{PRIMARY_ARM}||pool/{J}"]["bh_sig"]
                 for J in JOINTS10},
    median_pool_abs=MED_POOL_ABS, median_pool_signed=MED_POOL,
    R_glob=R_GLOB, n_pool_sig=N_POOL_SIG,
    class_sig_over_0p10=[[k, v] for k, v in CLS_SIG],
    F_CONFOUND=F_CONFOUND, rho_A_count=_rc,
    rho_A_inmass=CONF[PRIMARY_ARM]["rho_A_inmass"])

# whole-graph native read, the card's own sentence (leg c)
WG = {}
if WHOLE_OK:
    for k in KEYS:
        if ROWS[k]["leg"] == "c_whole":
            WG[ROWS[k]["unit"]] = dict(
                A_v1=ROWS[k]["A_v1"], A_n=ROWS[k]["A_n"],
                A_inmass=ROWS[k]["A_inmass"], p_two=ROWS[k]["p_two"],
                bh_sig=ROWS[k]["bh_sig"], n_L=ROWS[k]["n_L"],
                n_R=ROWS[k]["n_R"])
    _wa = WG.get("wg/pop/all")
    if _wa:
        log(f"[leg c] whole-graph NATIVE all-population A_v1 "
            f"{_wa['A_v1']:+.6f} (count asym {_wa['A_n']:+.4f}) "
            f"p {_wa['p_two']:.3e}")
    for _u in sorted(WG):
        log(f"   {_u:34s} A_v1 {WG[_u]['A_v1']:+.6f} A_n {WG[_u]['A_n']:+.4f} "
            f"A_inm {WG[_u]['A_inmass']:+.6f} p {WG[_u]['p_two']:.2e} "
            f"sig {WG[_u]['bh_sig']}")
P["whole_graph_native"] = WG

# cord-arm cross-arm consistency of the same units
XARM = {}
for uname, u in UNITS.items():
    if u["scope"] != "restricted":
        continue
    vals = {a: ROWS[f"{a}||{uname}"]["A_v1"] for a in ARMS
            if f"{a}||{uname}" in ROWS}
    XARM[uname] = vals
P["cross_arm"] = XARM

# ---------------- predictions, scored AS WRITTEN --------------------------
PRED = {}
PRED["P1"] = dict(
    registered="A_glob > 0 on the primary arm (cord subnet's whole labelled "
               "population is LEFT-heavy in per-cell Perron overlap)",
    measured=A_GLOB, result=bool(A_GLOB > 0), status="UNOBSERVED at prereg")
PRED["P2"] = dict(
    registered="R_glob < 0.50 (branch is NOT B_GLOBAL)",
    measured=R_GLOB, result=bool(R_GLOB < 0.50),
    status="UNOBSERVED at prereg")
PRED["P3"] = dict(
    registered="at least 3 of 5 pools BH-significant on the primary arm",
    measured=N_POOL_SIG, result=bool(N_POOL_SIG >= 3),
    status="PARTIALLY OBSERVED (Ti/Tr under a DIFFERENT null, PREREG 0g)")
_WA = WG.get("wg/pop/all") if WHOLE_OK else None
PRED["P4"] = dict(
    registered="whole-graph NATIVE all-population A_v1 < 0 (RIGHT-heavy), "
               "given the 2.0:1 right-heavy cell count and the 8.4:1 "
               "optic-lobe imbalance",
    measured=(_WA["A_v1"] if _WA else None),
    result=(bool(_WA["A_v1"] < 0) if _WA else None),
    status=("UNOBSERVED at prereg (counts observed)" if _WA
            else "UNSCOREABLE — whole-graph arm UNRESOLVED (PREREG 0e)"))
PRED["P5"] = dict(
    registered="|rho(A_v1, A_count)| < 0.70 on the primary arm "
               "(F_CONFOUND does not fire)",
    measured=_rc, result=bool(not F_CONFOUND), status="UNOBSERVED at prereg")
PRED["P6"] = dict(
    registered="at least one super_class BH-significant with |A| >= 0.10 on "
               "the primary arm",
    measured=len(CLS_SIG), result=bool(len(CLS_SIG) >= 1),
    status="UNOBSERVED at prereg")
_ok = sum(1 for v in PRED.values() if v["result"] is True)
_sc = sum(1 for v in PRED.values() if v["result"] is not None)
log(f"[predictions] {_ok}/{_sc} scoreable TRUE: "
    + " ".join(f"{k}={v['result']}" for k, v in PRED.items()))
P["predictions"] = PRED
P["predictions_true"] = _ok
P["predictions_scoreable"] = _sc

P["rows"] = ROWS
P["units"] = {k: dict(leg=v["leg"], scope=v["scope"], n_L=v["n_L"],
                      n_R=v["n_R"]) for k, v in UNITS.items()}
P["constants"] = dict(CMAX_ENUM=CMAX_ENUM, NDRAW_BIG=NDRAW_BIG,
                      NDRAW_SM=NDRAW_SM, N_TIER=N_TIER, SEED_SIDE=SEED_SIDE,
                      Q_BH=Q_BH, EPS8=EPS8, RES_BAR=RES_BAR)
P["limitations"] = (
    "(1) The whole-graph arm is BETA only (PREREG 0d) — the Crofts "
    "reweighting is constructed inside the certified SUBS loop and was not "
    "re-implemented outside it. (2) The restricted units are keep_wA-"
    "intersected on every arm (PREREG 0c) so arms are compared on identical "
    "cell sets; one extra Pr_bL cell that exists unrestricted is in no unit. "
    "(3) The union null is NOT L216's within-group null (PREREG 0g); both are "
    "reported for Ti/Tr. (4) The whole labelled population's side census is "
    "right-heavy 2.0:1 in CELL COUNT, driven 8.4:1 by the optic lobe, so any "
    "whole-graph asymmetry is confounded with reconstruction completeness BY "
    "CONSTRUCTION — which is why the branch rests on the cord subnet, whose "
    "count ratio is 0.96. (5) p-values for the large units rest on 5000 "
    "sampled draws (floor 1.9996e-04); the small units are EXACT. (6) "
    "A_inmass is measured in the ARM's OWN operator currency, so on the "
    "Crofts arms it is the degree-reweighted mass, not raw |log1p(syn)*sign|; "
    "the primary arm is beta, where it is the raw ladder mass with BETA_L on "
    "inhibitory edges. (7) The branch's sign leg compares np.sign of two "
    "measured reals; both are far from zero on the primary arm, and the "
    "signed median pool value is stored beside it so a near-zero case would "
    "be visible.")

# ---------------- prior artifacts untouched -------------------------------
for _p, _fp in (("l216/static.json", _f216), ("l209/static.json", _f209),
                ("l210/static.json", _f210)):
    _n = os.stat(_p)
    assert (_n.st_size, _n.st_mtime_ns) == (_fp.st_size, _fp.st_mtime_ns), \
        (_p, "prior artifact MOVED during the run (STOP)")
log("[prior] l216/l209/l210 static.json (size, mtime_ns) unchanged GREEN")

P["runtime_s"] = time.time() - _T231
P["total_runtime_s"] = time.time() - t0
os.makedirs("l231", exist_ok=True)
json.dump(P, open("l231/static.json", "w"), indent=1, default=str)
log(f"[L231] DONE branch={BRANCH} preds={_ok}/{_sc} "
    f"({P['runtime_s']:.0f}s body, {P['total_runtime_s']:.0f}s total)")
