# ================= L228 TAIL (appended by l228_build.py) =================
# Everything above this line is:
#   HEAD1 = l151_static.py lines 1-319      VERBATIM
#   PRE   = the output dict `o`
#   HEAD2 = l178_tail.py lines 22-83        VERBATIM  (CERT-F4 + gains)
#   HEAD3 = l215_tail.py lines 1-157        VERBATIM  (CERT-G 2, CERT-205 36,
#           CERT-TBL 28, pool/SIDEMASK construction, L208 premise asserts)
# so every pin in those slices re-ran as FREE certification. No lab module was
# imported (L175). PREREG: l228/PREREG.md. Writes l228/static.json ONLY.
# Zero rollouts, zero settles, zero dynamics. RNG: the declared membership
# permutation null ONLY, seeded.
import itertools
import math

NDRAW2 = 2000
SEED_PERM2 = 22821
EPS = float(np.finfo(np.float64).eps)
PSIDES = ("Ti_L", "Ti_R", "Tr_L", "Tr_R")

log("=" * 72)
log(f"[L228] depth-2 resurrection static | NDRAW {NDRAW2} seed {SEED_PERM2}")

# ---------------- CERT-215 (HALTING): the parent's depth-1 table ------------
# Reproduced with the PARENT'S OWN EXPRESSION (separated positive/negative
# sums, then subtract) -- L206's law: a float-equality claim is a claim about
# the expression, not just the operands.
S215 = json.load(open("l215/static.json"))
_fp215 = os.stat("l215/static.json")
_FP215 = (_fp215.st_size, _fp215.st_mtime_ns)
assert S215["branch"] == "D_DEGENERATE", (S215["branch"], "L215 branch (STOP)")
assert S215["lam1_noop"]["is_noop"] is True, "L215 lam1 no-op drift (STOP)"


def _signed_in_parent(E, tgt):
    """L215's signed_in expression, re-stated here ONLY so the gate uses the
    parent's arithmetic; the parent's own def lives past the inherited slice."""
    sel = E & tgt[dst_all]
    v = vals_all[sel]
    return (float(v[v > 0].sum()), float(-v[v < 0].sum()), int(sel.sum()))


C215 = 0
D1 = {}
for key in PSIDES:
    J, side = key.split("_")
    tgt = SIDEMASK[(J, side)]
    n = NCELL[(J, side)]
    st = S215["rows"][key]
    assert st["n_cells"] == n, ("CERT-215 n_cells", key, "(STOP)")
    C215 += 1
    row = {"n_cells": n}
    for sname in ("cutwA", "f4wA"):
        Mp, Mm, ne = _signed_in_parent(SUB[sname][0], tgt)
        got = dict(Mp=Mp, Mm=Mm, NET=Mp - Mm, TOT=Mp + Mm, n_edges=ne,
                   NET_per_cell=(Mp - Mm) / n,
                   NET_gain=GAIN[sname] * (Mp - Mm) / n,
                   inh_frac=Mm / (Mp + Mm))
        for k, v in got.items():
            assert v == st[sname][k], ("CERT-215", key, sname, k, v,
                                       st[sname][k], "(STOP)")
            C215 += 1
        row[sname] = got
    ret = row["f4wA"]["TOT"] / row["cutwA"]["TOT"]
    assert ret == st["ret"], ("CERT-215 ret", key, ret, st["ret"], "(STOP)")
    C215 += 1
    dact = (GAIN["f4wA"] * row["f4wA"]["NET"] / n
            - GAIN["cutwA"] * row["cutwA"]["NET"] / n)
    assert dact == S215["Q2_sign_neutral"][key]["dNET_act"], \
        ("CERT-215 dNET_act", key, "(STOP)")
    C215 += 1
    row["ret"] = ret
    row["d1_ratio_f4_over_cut"] = row["f4wA"]["NET"] / row["cutwA"]["NET"]
    row["dd1_gain"] = dact
    D1[key] = row
assert C215 == 76, (C215, "CERT-215 count (STOP)")
# The premise number is DERIVED FROM THE STORED FILE, never hand-typed (the
# tick-251/257/259 lesson): a retyped literal can contradict bytes already
# proven identical.  CERT-215 above already pinned both NETs at float
# equality, so this is the ratio of two certified values.
_st_TrL = S215["rows"]["Tr_L"]
_D1R_stored = _st_TrL["f4wA"]["NET"] / _st_TrL["cutwA"]["NET"]
_D1R = D1["Tr_L"]["d1_ratio_f4_over_cut"]
assert _D1R == _D1R_stored, (_D1R, _D1R_stored, "d1 ratio drift (STOP)")
assert 0.79 < _D1R < 0.81, (_D1R, "the ~20% d1 fall is not there (STOP)")
assert D1["Tr_L"]["dd1_gain"] < 0, "the premise (d1 FELL) is false (STOP)"
log(f"[CERT-215] GREEN {C215} float equalities | Tr_L d1 ratio {_D1R:.6f} "
    f"(= a {100*(1-_D1R):.1f}% fall) | dd1_gain {D1['Tr_L']['dd1_gain']:+.5f}")

# ---------------- the two-hop kernel, PROVEN before use (CERT-D2) ----------
GAIN2 = {k: v * v for k, v in GAIN.items()}
log(f"[0b] g^2 cutwA {GAIN2['cutwA']:.8f} f4wA {GAIN2['f4wA']:.8f} | "
    f"ratio {GAIN2['f4wA']/GAIN2['cutwA']:.6f} "
    f"(depth-1 ratio {GAIN['f4wA']/GAIN['cutwA']:.6f})")


def _acc_addat(idx, w):
    y = np.zeros(Nall)
    np.add.at(y, idx, w)
    return y


def _acc_bincount(idx, w):
    return np.bincount(idx, weights=w, minlength=Nall)


NET = {}
CONTRIB = {}
NMV = 0
for sname in ("cutwA", "f4wA"):
    E = SUB[sname][0]
    di, si, vv = dst_all[E], src_all[E], vals_all[E]
    net_a = _acc_addat(di, vv)
    net_b = _acc_bincount(di, vv)
    assert np.array_equal(net_a, net_b), (sname, "CERT-D2 net kernel (STOP)")
    NMV += 1
    NET[sname] = net_a
    cs = vv * net_a[si]                       # signed two-hop contribution
    ca = np.abs(vv) * np.abs(net_a[si])       # absolute two-hop mass
    for tag, w in (("signed", cs), ("abs", ca)):
        a = _acc_addat(di, w)
        b = _acc_bincount(di, w)
        assert np.array_equal(a, b), (sname, tag, "CERT-D2 d2 kernel (STOP)")
        NMV += 1
    CONTRIB[sname] = dict(E=E, di=di, si=si, vv=vv, cs=cs, ca=ca,
                          d2_cell=_acc_addat(di, cs),
                          t2_cell=_acc_addat(di, ca))

# (ii) the DEFINITIONAL per-cell sum on 40 pool cells, bar DERIVED from data
_rngp = np.random.default_rng(1228)
_pool_cells = np.unique(np.concatenate(
    [np.where(SIDEMASK[(J, s)])[0] for J in JOINTS for s in ("L", "R")]))
_probe = _rngp.choice(_pool_cells, size=40, replace=False)
_ndef = 0
for sname in ("cutwA", "f4wA"):
    C = CONTRIB[sname]
    for c in _probe:
        m = C["di"] == c
        want = math.fsum(C["cs"][m].tolist())
        got = float(C["d2_cell"][c])
        bar = 8 * EPS * float(np.abs(C["cs"][m]).sum()) + 1e-300
        assert abs(got - want) <= bar, (sname, int(c), got, want, bar,
                                        "CERT-D2 definitional (STOP)")
        _ndef += 1
NMV += _ndef
log(f"[CERT-D2] GREEN {NMV} checks ({_ndef} definitional fsum probes with "
    f"data-derived bars, 6 exact array equalities)")

# ---------------- 0f: the ZERO class in net_in, counted first ---------------
CLS = np.sign(NET["cutwA"])          # 0g: FIXED baseline classification
ZERO = {}
for sname in ("cutwA", "f4wA"):
    C = CONTRIB[sname]
    cz = CLS[C["si"]] == 0
    ZERO[sname] = dict(n_edges=int(C["E"].sum()),
                       n_edges_zero_src=int(cz.sum()),
                       frac_edges_zero_src=float(cz.mean()),
                       abs_mass_frac_zero_src=float(
                           np.abs(C["vv"][cz]).sum() / np.abs(C["vv"]).sum()))
ZERO["n_nodes_net_zero_cutwA"] = int((NET["cutwA"] == 0).sum())
ZERO["n_nodes_net_zero_f4wA"] = int((NET["f4wA"] == 0).sum())
ZERO["n_nodes_kept_cutwA"] = int(keep_wA.sum())
MIG = int((np.sign(NET["f4wA"]) != CLS).sum())
ZERO["n_nodes_class_migrated"] = MIG
log(f"[0f] net_in == 0 nodes: cutwA {ZERO['n_nodes_net_zero_cutwA']:,} "
    f"f4wA {ZERO['n_nodes_net_zero_f4wA']:,} | zero-src edges cutwA "
    f"{ZERO['cutwA']['frac_edges_zero_src']:.5f} | class migrations {MIG:,}")

# ---------------- primary measurement: d2 per pool-side --------------------
ROWS2 = {}
for key in PSIDES:
    J, side = key.split("_")
    tgt = SIDEMASK[(J, side)]
    n = NCELL[(J, side)]
    r = {"n_cells": n}
    for sname in ("cutwA", "f4wA"):
        C = CONTRIB[sname]
        sel = C["di"]
        m = tgt[sel]
        d2 = float(C["cs"][m].sum())
        t2 = float(C["ca"][m].sum())
        p2 = float(C["cs"][m][C["cs"][m] > 0].sum())
        n2 = float(-C["cs"][m][C["cs"][m] < 0].sum())
        r[sname] = dict(d2=d2, TOT2=t2, d2_pos=p2, d2_neg=n2,
                        n_edges=int(m.sum()),
                        d2_per_cell=d2 / n,
                        d2_gain=GAIN2[sname] * d2 / n,
                        d2_gain_g1=GAIN[sname] * d2 / n,
                        neg_frac=n2 / (p2 + n2) if (p2 + n2) else None)
        # the three-class decomposition must SUM to d2 (0f)
        cls_s = CLS[C["si"][m]]
        parts = {c: float(C["cs"][m][cls_s == v].sum())
                 for c, v in (("neg", -1.0), ("zero", 0.0), ("pos", 1.0))}
        _bar = 8 * EPS * float(np.abs(C["cs"][m]).sum()) + 1e-300
        assert abs(sum(parts.values()) - d2) <= _bar, (key, sname, parts, d2,
                                                       "class split (STOP)")
        # 0f/0g INTERACTION, found by this gate (disclosed in the VERDICT):
        # the zero class is a NULL class only on the arm whose net_in defines
        # it.  Under the registered FIXED baseline classification (0g) a
        # source with net_in_cutwA == 0 can acquire net_in_f4wA != 0, so on
        # the floored arm the zero class carries real mass.  Assert the true
        # statement (exact zero on the BASELINE arm) and MEASURE the rest.
        if sname == "cutwA":
            assert parts["zero"] == 0.0, (key, "baseline zero class (STOP)")
        r[sname]["by_src_class"] = parts
        r[sname]["zero_class_share_of_abs"] = (
            abs(parts["zero"]) / float(np.abs(C["cs"][m]).sum())
            if float(np.abs(C["cs"][m]).sum()) else None)
        # the four sign quadrants (0h)
        q = {}
        for en, em in (("exc", C["vv"][m] > 0), ("inh", C["vv"][m] < 0)):
            for cn, cm in (("srcneg", cls_s < 0), ("srcpos", cls_s > 0)):
                q[f"{en}_{cn}"] = float(C["cs"][m][em & cm].sum())
        r[sname]["quadrants"] = q
    r["ret2"] = r["f4wA"]["TOT2"] / r["cutwA"]["TOT2"]
    r["d2_pred"] = r["cutwA"]["d2"] * r["ret2"]
    r["dd2_gain"] = r["f4wA"]["d2_gain"] - r["cutwA"]["d2_gain"]
    r["dd2_pred"] = (GAIN2["f4wA"] * r["d2_pred"] / n
                     - GAIN2["cutwA"] * r["cutwA"]["d2"] / n)
    r["dd2_gain_g1"] = r["f4wA"]["d2_gain_g1"] - r["cutwA"]["d2_gain_g1"]
    r["degen_bar"] = 0.01 * GAIN2["cutwA"] * r["cutwA"]["TOT2"] / n
    r["DEGENERATE"] = bool(abs(r["dd2_gain"]) < r["degen_bar"])
    r["RISE"] = bool(r["dd2_gain"] > 0)
    r["rel_dd2"] = (r["f4wA"]["d2_gain"] / r["cutwA"]["d2_gain"]
                    if r["cutwA"]["d2_gain"] else None)
    if r["DEGENERATE"]:
        r["S2_sign"] = None
        r["share_neg"] = None
    else:
        r["S2_sign"] = (r["dd2_gain"] - r["dd2_pred"]) / r["dd2_gain"]

        def _dcls(c):
            return (GAIN2["f4wA"] * r["f4wA"]["by_src_class"][c] / n
                    - GAIN2["cutwA"] * r["cutwA"]["by_src_class"][c] / n)

        dneg, dzero, dpos = _dcls("neg"), _dcls("zero"), _dcls("pos")
        _b2 = 1e-9 * max(abs(dneg), abs(dzero), abs(dpos), abs(r["dd2_gain"]))
        assert abs((dneg + dzero + dpos) - r["dd2_gain"]) <= _b2, (
            key, dneg, dzero, dpos, r["dd2_gain"], "dd2 3-class split (STOP)")
        r["dd2_neg_class"] = dneg
        r["dd2_zero_class"] = dzero
        r["dd2_pos_class"] = dpos
        r["share_neg"] = dneg / r["dd2_gain"]
        r["share_zero"] = dzero / r["dd2_gain"]
        r["share_pos"] = dpos / r["dd2_gain"]
    ROWS2[key] = r
    log(f"[d2 {key}] n {n} | cut d2 {r['cutwA']['d2']:.4g} -> f4 "
        f"{r['f4wA']['d2']:.4g} | gain^2 {r['cutwA']['d2_gain']:+.5f} -> "
        f"{r['f4wA']['d2_gain']:+.5f} | dd2 {r['dd2_gain']:+.5f} bar "
        f"{r['degen_bar']:.5f} | RISE {r['RISE']} DEGEN {r['DEGENERATE']} | "
        f"share_neg {'None' if r['share_neg'] is None else format(r['share_neg'], '+.4f')}")

# ---------------- 0a diagnostic: the HYBRID operator (no branch) -----------
Ccut, Cf4 = CONTRIB["cutwA"], CONTRIB["f4wA"]
HYB = {}
for key in PSIDES:
    J, side = key.split("_")
    tgt = SIDEMASK[(J, side)]
    n = NCELL[(J, side)]
    m = tgt[Cf4["di"]]
    d2h = float((Cf4["vv"][m] * NET["cutwA"][Cf4["si"][m]]).sum())
    HYB[key] = dict(d2_hybrid=d2h, d2_hybrid_gain=GAIN2["f4wA"] * d2h / n,
                    dd2_edgeset_only=(GAIN2["f4wA"] * d2h / n
                                      - ROWS2[key]["cutwA"]["d2_gain"]),
                    dd2_total=ROWS2[key]["dd2_gain"])
    HYB[key]["share_edgeset"] = (HYB[key]["dd2_edgeset_only"]
                                 / HYB[key]["dd2_total"]
                                 if HYB[key]["dd2_total"] else None)
log("[0a] hybrid diagnostic: Tr_L edge-set-only share "
    f"{HYB['Tr_L']['share_edgeset']}")

# ---------------- branch table (PREREG section 3, in order) ----------------
act2 = ROWS2["Tr_L"]
if act2["DEGENERATE"]:
    BRANCH2 = "D2_DEGENERATE"
elif not act2["RISE"]:
    BRANCH2 = "D2_FALLS"
elif ROWS2["Ti_L"]["RISE"] and ROWS2["Ti_R"]["RISE"]:
    BRANCH2 = "D2_RISES_EVERYWHERE"
else:
    BRANCH2 = "D2_RISES_SPECIFIC"
log(f"[branch] {BRANCH2}")

# registered escape (section 5) SHORT-CIRCUITS the mechanism claim
ESCAPE_FIRED = BRANCH2 in ("D2_FALLS", "D2_DEGENERATE")
if ESCAPE_FIRED:
    MECH_CLAIM = None
    MECH_NOTE = ("registered escape FIRED: no static depth-k account; no "
                 "mechanism claim is made from share_neg. Next instrument = "
                 "the LINEARISED GATED operator at the operating point (L178 "
                 "class).")
else:
    MECH_CLAIM = bool(act2["share_neg"] is not None and act2["share_neg"] > 0.50)
    MECH_NOTE = "mechanism clause read (escape did not fire)"
log(f"[escape] fired {ESCAPE_FIRED} | MECH_CLAIM {MECH_CLAIM}")

# ---------------- Q4: the SAME membership-permutation handedness null ------
rng2 = np.random.default_rng(SEED_PERM2)
PERM2 = {}
for gkey, (cells, isL) in GROUPS.items():
    nn, nL = len(cells), int(isL.sum())
    M = np.zeros((NDRAW2, nn), bool)
    for d in range(NDRAW2):
        M[d, rng2.permutation(nn)[:nL]] = True
    assert (M.sum(1) == nL).all(), (gkey, "draw count drift (STOP)")
    PERM2[gkey] = M
log("[null] L228 permutation draws built (per-side counts held EXACT)")


def _pct2(real, null):
    up = float((null >= real).mean())
    return dict(pct_up=up, pct_two=float(2 * min(up, 1 - up)),
                null_mean=float(null.mean()), null_sd=float(null.std()),
                null_p05=float(np.percentile(null, 5)),
                null_p95=float(np.percentile(null, 95)))


# per-cell gain-scaled dd2 (the primary statistic, per cell)
dd2_cell = (GAIN2["f4wA"] * CONTRIB["f4wA"]["d2_cell"]
            - GAIN2["cutwA"] * CONTRIB["cutwA"]["d2_cell"])
Q4b = {}
for J in JOINTS:
    cf, isLf = GROUPS[(J, "f")]
    ce, isLe = GROUPS[(J, "e")]
    xf, xe = dd2_cell[cf], dd2_cell[ce]
    Pf, Pe = PERM2[(J, "f")], PERM2[(J, "e")]
    nLf, nLe = int(isLf.sum()), int(isLe.sum())
    nL = nLf + nLe
    nR = len(cf) + len(ce) - nL

    def _A(sL, sR):
        a, b = sL / nL, sR / nR
        den = abs(a) + abs(b)
        return float((a - b) / den) if den else None

    tot = float(xf.sum() + xe.sum())
    realA = _A(float(xf[isLf].sum() + xe[isLe].sum()),
               float(xf[~isLf].sum() + xe[~isLe].sum()))
    nsL = Pf @ xf + Pe @ xe
    nsR = tot - nsL
    na, nb = nsL / nL, nsR / nR
    nullA = (na - nb) / (np.abs(na) + np.abs(nb))
    Q4b[J] = dict(A_dd2=realA, n_L=nL, n_R=nR, **_pct2(realA, nullA))
    log(f"[Q4 {J}] A_dd2 {realA:+.5f} pct_up {Q4b[J]['pct_up']:.4f} two "
        f"{Q4b[J]['pct_two']:.4f} [null {Q4b[J]['null_p05']:+.4f},"
        f"{Q4b[J]['null_p95']:+.4f}]")

# ---------------- P6: the fold-rank leg (DESCRIPTION, floor 1/24) ----------
# FOLD is DERIVED from l208/static.json, never hand-typed.
_lv = json.load(open("l208/static.json"))["arms"]
FOLD = {}
for key in PSIDES:
    J, side = key.split("_")
    lc = _lv[f"B36|{J}|cutwA"][f"lvl{side}"]
    lf = _lv[f"B36|{J}|f4wA"][f"lvl{side}"]
    assert lc > 0 and lf > 0, (key, lc, lf, "stored level non-positive (STOP)")
    FOLD[key] = lf / lc
assert FOLD["Tr_L"] == max(FOLD.values()), "Tr_L is not the largest fold (STOP)"
assert min(FOLD.values()) > 1.0, "a pool-side does not rise dynamically (STOP)"
log("[0e] stored dynamic folds " + " ".join(
    f"{k} {FOLD[k]:.2f}x" for k in PSIDES))


def _midrank(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


_f = np.array([FOLD[k] for k in PSIDES])
_d = np.array([ROWS2[k]["rel_dd2"] if ROWS2[k]["rel_dd2"] is not None
               else np.nan for k in PSIDES])
_ra, _rb = _midrank(_f), _midrank(_d)
_sp = float(np.corrcoef(_ra, _rb)[0, 1])
_perms = list(itertools.permutations(range(4)))
_null_sp = [float(np.corrcoef(_ra, _rb[list(p)])[0, 1]) for p in _perms]
P6 = dict(fold=FOLD, rel_dd2={k: ROWS2[k]["rel_dd2"] for k in PSIDES},
          spearman_midrank=_sp,
          exact_perm_p_up=float(np.mean(np.array(_null_sp) >= _sp)),
          resolution_floor=1.0 / len(_perms), n=4,
          status="DESCRIPTION (n=4, floor 1/24 = .0417)")
log(f"[P6] Spearman(fold, rel_dd2) {_sp:+.4f} exact perm p_up "
    f"{P6['exact_perm_p_up']:.4f} (floor {P6['resolution_floor']:.4f})")

# ---------------- predictions ----------------------------------------------
PRED2 = dict(
    P1=dict(claim='branch == "D2_RISES_SPECIFIC" (the card as written)',
            got=BRANCH2, scored=BRANCH2 == "D2_RISES_SPECIFIC"),
    P2=dict(claim="RISE(Tr_L) TRUE (d2 rises where d1 fell)",
            got=act2["RISE"], scored=bool(act2["RISE"])),
    P3=dict(claim="share_neg(Tr_L) > 0.50 (rise carried by net-negative "
                  "sources)",
            got=act2["share_neg"],
            scored=bool(act2["share_neg"] is not None
                        and act2["share_neg"] > 0.50)),
    P4=dict(claim="d2_gain_f4wA(Ti_L) > d2_gain_f4wA(Ti_R) -- the "
                  "out-of-selection L/R sign depth-1 gets WRONG",
            got=[ROWS2["Ti_L"]["f4wA"]["d2_gain"],
                 ROWS2["Ti_R"]["f4wA"]["d2_gain"]],
            scored=bool(ROWS2["Ti_L"]["f4wA"]["d2_gain"]
                        > ROWS2["Ti_R"]["f4wA"]["d2_gain"])),
    P5=dict(claim="Q4 Tr pct_two < Ti pct_two",
            got=[Q4b["Tr"]["pct_two"], Q4b["Ti"]["pct_two"]],
            scored=bool(Q4b["Tr"]["pct_two"] < Q4b["Ti"]["pct_two"])),
    P6=dict(claim="Spearman(fold, rel_dd2) > 0 (DESCRIPTION)",
            got=_sp, scored=bool(_sp > 0)))

# depth-1 comparator table, so the anti-predictive premise is in the artifact
D1_VS_D2 = {k: dict(dd1_gain=D1[k]["dd1_gain"],
                    d1_ratio=D1[k]["d1_ratio_f4_over_cut"],
                    dd2_gain=ROWS2[k]["dd2_gain"],
                    rel_dd2=ROWS2[k]["rel_dd2"],
                    sign_flip=bool((D1[k]["dd1_gain"] < 0)
                                   != (ROWS2[k]["dd2_gain"] < 0)),
                    dyn_fold=FOLD[k]) for k in PSIDES}

o["prereg"] = "l228/PREREG.md"
o["design_l228"] = ("depth-2 signed drive d2(P) = sum_{e into P} vals[e] * "
                    "net_in(src[e]) on cutwA vs f4wA, per side per joint, "
                    "gain^2-scaled, with L215's sign-neutral counterfactual "
                    "and membership null. Static, zero rollouts.")
o["gains_used_l228"] = dict(g_cutwA=GAIN["cutwA"], g_f4wA=GAIN["f4wA"],
                            g2_cutwA=GAIN2["cutwA"], g2_f4wA=GAIN2["f4wA"],
                            ratio_g1=GAIN["f4wA"] / GAIN["cutwA"],
                            ratio_g2=GAIN2["f4wA"] / GAIN2["cutwA"])
o["cert_l228"] = dict(cert_215=C215, cert_d2=NMV,
                      cert_d2_definitional=_ndef,
                      inherited_free=("CERT-205 36, CERT-TBL 28, CERT-G 2, "
                                      "substrate+pool pins, L208 premise "
                                      "asserts -- l215_tail.py lines 1-157 "
                                      "VERBATIM"))
o["d1_parent_table"] = D1
o["zero_and_class"] = ZERO
o["rows_d2"] = ROWS2
o["hybrid_diagnostic"] = HYB
o["d1_vs_d2"] = D1_VS_D2
o["Q4_null_l228"] = dict(ndraw=NDRAW2, seed=SEED_PERM2,
                         kind="membership permutation (L215 Q4 class); "
                              "per-side counts held EXACT; statistic = "
                              "handedness asymmetry of per-cell gain^2 dd2, "
                              "normalised by |a|+|b| so it is bounded",
                         **{k: v for k, v in Q4b.items()})
o["P6_fold_rank"] = P6
o["branch"] = BRANCH2
o["escape_fired"] = bool(ESCAPE_FIRED)
o["escape_note"] = MECH_NOTE
o["mechanism_claim"] = MECH_CLAIM
o["predictions"] = PRED2
o["limits"] = [
    "uniform-X anatomical expansion: net_in is the depth-1 drive onto a "
    "source assuming unit activity everywhere; the real system is relu-gated "
    "and ~16.8% active (L208), so d2 is an ANATOMICAL two-hop quantity, not "
    "the operating-point two-hop gain",
    "the Tr_L pools were SELECTED for being dead (L208 post-hoc floor leg): "
    "every Tr_L number is a DESCRIPTION of a selected object; Q4 is a "
    "handedness null on a preselected pool (Kriegeskorte 2009)",
    "ret2 mixes the floor with the small node-set change (cutwA drops "
    "ng_desc[:24], f4wA drops ng4[:20]); the node-matched eligible "
    "comparator is inherited from the L215 slice",
    "n = 4 pool-sides: every cross-pool rank statistic has an exact "
    "permutation resolution floor of 1/24 = .0417 and is DESCRIPTION (L225)",
    "the source-class decomposition is classified on the BASELINE arm "
    "(0g); per-arm classification migrates on "
    f"{ZERO['n_nodes_class_migrated']} nodes and is a diagnostic only"]

# ---------------- read-only fingerprints asserted unchanged ----------------
for path, fp in (("l205/static.json", _FP205), ("l208/static.json", _FP208),
                 ("l208/addendum_floor.json", _FPA),
                 ("l215/static.json", _FP215)):
    st = os.stat(path)
    assert (st.st_size, st.st_mtime_ns) == fp, (path, "MUTATED (STOP)")
log("[fingerprints] prior artifacts unchanged GREEN")

os.makedirs("l228", exist_ok=True)
json.dump(o, open("l228/static.json", "w"), indent=1, default=float)
log("=" * 72)
log(f"L228 DONE {time.time()-t0:.0f}s | BRANCH {BRANCH2} | "
    f"preds {sum(1 for v in PRED2.values() if v['scored'])}/6 | "
    f"Tr_L dd1 {D1['Tr_L']['dd1_gain']:+.5f} dd2 {act2['dd2_gain']:+.5f} | "
    f"escape {ESCAPE_FIRED}")
