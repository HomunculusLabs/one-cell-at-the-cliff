# ================= L206 TAIL (appended by l206_build.py) =================
# Everything above this line is VERBATIM source: l151_static.py 1-319,
# l178_tail.py 7-149, the two-line l206_mid bridge, l178_tail.py 348-458.
# So CERT-F4, the gains at float equality, the CSR orientation, all 20 pool
# sizes and CERT-REW (l169c P6) have ALL re-run as free certification before
# any L206 value is read. PREREG: l206/PREREG.md (registered first).
# Writes l206/static.json ONLY. Zero rollouts, zero settles, zero dynamics.
import heapq

o["design"] = (
    "L206 the avoidance LENGTH SCALE: depths 1-10 of the ANATOMICAL "
    "(seed-free, row-mask-free) linearized walk operator A = |g*W_beta| on "
    "f4wA, for carrier / mass-matched twin / 33-cell ng family / the same "
    "100 l169c degree-neutral destination swaps. Two normalisations "
    "(leading-eigenvalue lam1^d primary; Crofts/Estrada strength form "
    "reported beside it) plus the scale-free pool share, and SEARCH "
    "INFORMATION as its own gate cell. PREREG l206/PREREG.md.")
o["prereg"] = "l206/PREREG.md"
with open("l206_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(8)])

S178 = json.load(open("l178/static.json"))
DMAX = 10

# ---------------- anatomical operator (no row mask, no settle) --------------
_vnp = _v.numpy().astype(np.float64)
jv_abs_an = np.abs(G_F4WA * _vnp)
jv_sgn_an = G_F4WA * _vnp
assert float(jv_abs_an.min()) > 0.0, "zero-weight edge (breaks -log10)"


def jmatvec(x, jv, ls, ld):
    y = np.zeros(NL)
    np.add.at(y, ld, jv * x[ls])
    return y


def reach(c_local, jv, depth=3):
    """complete length-d walk sums of the operator from c into each pool."""
    x = np.zeros(NL)
    x[c_local] = 1.0
    res = {}
    for d in range(1, depth + 1):
        x = jmatvec(x, jv, csr_cols, csr_rows)
        res[d] = {pk: float(x[POOL_L[pk]].sum()) for pk in POOL_L}
    return res


def pi_index(sgn_d):
    num = sum(abs(sgn_d[a] - sgn_d[b]) for a, b in PAIRS)
    den = sum(abs(sgn_d[a]) + abs(sgn_d[b]) for a, b in PAIRS)
    return float(num / den) if den else float("nan")


ACTORS = {"carrier": LC_CAR, "twin": LC_TWIN}
for _k, _gi in enumerate(FAMILY):
    ACTORS[f"fam{_k:02d}_{_gi}"] = int(loc_f4[_gi])
GI_OF = {"carrier": GI_CARRIER, "twin": GI_TWIN4}
GI_OF.update({f"fam{_k:02d}_{_gi}": int(_gi) for _k, _gi in enumerate(FAMILY)})
assert len(ACTORS) == 35, (len(ACTORS), "actor set != L178's 35 (STOP)")

out_mass_global = np.zeros(Nall)
np.add.at(out_mass_global, src_all[_ei], np.abs(vals_all[_ei]))
M_OUT = {n: float(out_mass_global[GI_OF[n]]) for n in ACTORS}
for n in ACTORS:
    assert M_OUT[n] == S178["census"][n]["m_out"], (n, "m_out drift (STOP)")

# ---------------- CERT-178 (HALTING): depths 1-3 reproduce L178 exactly -----
_A178 = S178["E_anatomical"]["all_actors"]
assert len(_A178) == 35
_n_chk = 0
for name, lc in ACTORS.items():
    ra = reach(lc, jv_abs_an)
    rs = reach(lc, jv_sgn_an)
    st = _A178[name]
    m_out = M_OUT[name]
    for d in (1, 2, 3):
        pa = float(sum(ra[d].values()))
        sg = float(sum(rs[d].values()))
        assert pa == st[f"P{d}abs"], (name, d, pa, st[f"P{d}abs"], "CERT-178")
        assert sg == st[f"S{d}sgn"], (name, d, "CERT-178 signed")
        pm = pa / m_out if m_out else None
        assert pm == st[f"P{d}abs_per_mass"], (name, d, "CERT-178 per-mass")
        pi = pi_index(rs[d])
        sp = st[f"PI{d}"]
        assert (pi == sp) or (not np.isfinite(pi) and sp is None) or \
               (isinstance(sp, float) and not np.isfinite(sp)
                and not np.isfinite(pi)), (name, d, pi, sp, "CERT-178 PI")
        _n_chk += 4
assert S178["E_anatomical"]["r2_anat"] == (
    (_A178["carrier"]["P2abs_per_mass"] / _A178["twin"]["P2abs_per_mass"]))
log(f"[CERT-178] GREEN {_n_chk} stored anatomical values reproduced by "
    f"FLOAT EQUALITY (35 actors x depths 1-3 x P/S/per-mass/PI)")
o["cert_178"] = dict(n_checks=_n_chk, mode="float equality (==)",
                     source="l178/static.json E_anatomical.all_actors",
                     n_actors=35, depths=[1, 2, 3])

# ---------------- spectral radius: power iteration (branch iii machinery) ---
def power_iter(jv, iters=400):
    v = np.ones(NL) / math.sqrt(NL)
    lam, hist = 0.0, []
    for i in range(iters):
        w = jmatvec(v, jv, csr_cols, csr_rows)
        nrm = float(np.linalg.norm(w))
        if nrm == 0.0:
            return 0.0, v, []
        v = w / nrm
        lam = nrm
        if i >= iters - 6:
            hist.append(nrm)
    ray = float(v @ jmatvec(v, jv, csr_cols, csr_rows))
    return lam, v, dict(rayleigh=ray, last6=hist,
                        rel_spread_last6=float((max(hist) - min(hist))
                                               / max(hist)))


LAM1, V1, LAMINFO = power_iter(jv_abs_an)
assert LAM1 > 0 and LAMINFO["rel_spread_last6"] < 1e-6, \
    ("power iteration not converged", LAMINFO)
log(f"[spectral] lam1(A_abs) = {LAM1:.6f} (Rayleigh {LAMINFO['rayleigh']:.6f}, "
    f"rel spread last 6 {LAMINFO['rel_spread_last6']:.2e})")

# Crofts/Estrada strength normalisation (tick-233 amendment (b)) -------------
s_out_n = np.zeros(NL)
np.add.at(s_out_n, csr_cols, jv_abs_an)
s_in_n = np.zeros(NL)
np.add.at(s_in_n, csr_rows, jv_abs_an)
s_tot = s_out_n + s_in_n
s_safe = np.where(s_tot > 0, s_tot, 1.0)
jv_crofts = jv_abs_an / np.sqrt(s_safe[csr_rows] * s_safe[csr_cols])
LAM1C, V1C, LAMINFOC = power_iter(jv_crofts)
log(f"[spectral] lam1(A_crofts) = {LAM1C:.6f} "
    f"(rel spread {LAMINFOC['rel_spread_last6']:.2e})")
o["spectral"] = dict(
    lam1_abs=LAM1, rayleigh_abs=LAMINFO["rayleigh"],
    rel_spread_abs=LAMINFO["rel_spread_last6"],
    lam1_crofts=LAM1C, rayleigh_crofts=LAMINFOC["rayleigh"],
    rel_spread_crofts=LAMINFOC["rel_spread_last6"],
    strength_convention="s(n) = out-strength + in-strength of |g*W_beta| "
                        "(our reading of the review's undirected convention, "
                        "DISCLOSED as a choice on a directed graph)",
    note="lam1 by power iteration on the nonnegative operator "
         "(Perron-Frobenius); normalisation leg N1 divides depth-d sums by "
         "lam1^d so depths are comparable.")


# ---------------- the depth sweep -------------------------------------------
def sweep_actor(lc, jv, v1, dmax=DMAX):
    x = np.zeros(NL)
    x[lc] = 1.0
    P, T, SH, CS = [], [], [], []
    for d in range(1, dmax + 1):
        x = jmatvec(x, jv, csr_cols, csr_rows)
        # IDENTICAL arithmetic to reach() so the depth-1..3 self-check is a
        # bit-level comparison and not a re-derivation
        p = float(sum({pk: float(x[POOL_L[pk]].sum()) for pk in POOL_L}.values()))
        t = float(x.sum())
        nr = float(np.linalg.norm(x))
        P.append(p)
        T.append(t)
        SH.append(p / t if t else None)
        CS.append(float(x @ v1 / nr) if nr else None)
    return P, T, SH, CS


SW = {}
_sweep_maxrel = 0.0
for name, lc in ACTORS.items():
    P, T, SH, CS = sweep_actor(lc, jv_abs_an, V1)
    Pc, Tc, SHc, CSc = sweep_actor(lc, jv_crofts, V1C)
    SW[name] = dict(P=P, T=T, share=SH, cos_v1=CS,
                    P_crofts=Pc, share_crofts=SHc, cos_v1_crofts=CSc)
    for _i in (0, 1, 2):
        _st = _A178[name][f"P{_i+1}abs"]
        _rd = abs(P[_i] - _st) / abs(_st) if _st else abs(P[_i] - _st)
        _sweep_maxrel = max(_sweep_maxrel, _rd)
    assert _sweep_maxrel < 1e-12, (name, _sweep_maxrel, "sweep != CERT-178")
log(f"[sweep] {len(SW)} actors x depths 1-{DMAX}, both normalisations "
    f"(depth-1..3 vs L178 stored: max rel diff {_sweep_maxrel:.1e})")
o["sweep_selfcheck_max_rel_diff_vs_l178"] = _sweep_maxrel

COS_BAR = 0.99


def conv_depth(cs):
    for i, c in enumerate(cs):
        if c is not None and c > COS_BAR:
            return i + 1
    return None


D_CONV = {n: conv_depth(SW[n]["cos_v1"]) for n in ACTORS}
d_conv_car = D_CONV["carrier"]
log(f"[conv] carrier cos(x_d, v1) = "
    + " ".join(f"{c:.4f}" for c in SW['carrier']['cos_v1'])
    + f" -> d_conv {d_conv_car}")

# ---------------- the NULL: same 100 l169c draws, all depths ----------------
_pos_in_sorted = None  # built with the SI adjacency below
null_P = []            # [draw][depth-1] anatomical pool reach
null_T = []
null_changed = []
for d_ in draws:
    cr = d_["car_rows"]
    newd = d_["cdst"]
    changed = []
    for i, gpos in enumerate(cr):
        if int(newd[i]) == int(dst_all[gpos]):
            continue
        changed.append((int(_pos_in_csr[_eipos[int(gpos)]]),
                        int(loc_f4[int(newd[i])])))
    for jpos, de in d_["pdst"].items():
        changed.append((int(_pos_in_csr[_eipos[int(jpos)]]),
                        int(loc_f4[int(de)])))
    # l178's zero-the-slot + append-the-relocated-weight construction,
    # kept IDENTICAL so the depth-2/3 null statistics reproduce exactly
    jv_an2 = jv_abs_an.copy()
    extra_ls, extra_ld, extra_an = [], [], []
    for cidx, new_target in changed:
        extra_ls.append(int(csr_cols[cidx]))
        extra_ld.append(new_target)
        jv_an2[cidx] = 0.0
        extra_an.append(abs(G_F4WA * _vnp[cidx]))
    ls2 = np.concatenate([csr_cols, np.array(extra_ls, np.int64)])
    ld2 = np.concatenate([csr_rows, np.array(extra_ld, np.int64)])
    va2_an = np.concatenate([jv_an2, np.array(extra_an, np.float64)])
    xa = np.zeros(NL)
    xa[LC_CAR] = 1.0
    Pd, Td = [], []
    for dd in range(1, DMAX + 1):
        ya = np.zeros(NL)
        np.add.at(ya, ld2, va2_an * xa[ls2])
        xa = ya
        Pd.append(float(sum(xa[POOL_L[pk]].sum() for pk in POOL_L)))
        Td.append(float(xa.sum()))
    null_P.append(Pd)
    null_T.append(Td)
    null_changed.append(dict(n_changed=len(changed), changed=changed))
NP_ = np.array(null_P)          # (100, DMAX)
NT_ = np.array(null_T)
log(f"[null] {NP_.shape[0]} draws x depths 1-{DMAX} "
    f"(med changed {float(np.median([c['n_changed'] for c in null_changed])):.1f})")

# ---------------- CERT-NULL (HALTING): reproduce L178's Q2b statistics ------
_m_car = M_OUT["carrier"]
_Q2b = S178["Q2b_null_anatomical"]
_an2 = NP_[:, 1] / _m_car
_an3 = NP_[:, 2] / _m_car
_c2 = _A178["carrier"]["P2abs_per_mass"]
_c3 = _A178["carrier"]["P3abs_per_mass"]
for _k, _got in (("null_P2_med", float(np.median(_an2))),
                 ("null_P2_p05", float(np.percentile(_an2, 5))),
                 ("null_P2_p95", float(np.percentile(_an2, 95))),
                 ("null_P2_q25", float(np.percentile(_an2, 25))),
                 ("null_P2_q75", float(np.percentile(_an2, 75))),
                 ("null_P3_med", float(np.median(_an3))),
                 ("carrier_percentile_P2", float((_an2 < _c2).mean() * 100)),
                 ("carrier_percentile_P3", float((_an3 < _c3).mean() * 100))):
    assert _got == _Q2b[_k], (_k, _got, _Q2b[_k], "CERT-NULL (STOP)")
log("[CERT-NULL] GREEN: all 8 stored L178 Q2b_null_anatomical statistics "
    "reproduced by FLOAT EQUALITY from my own null construction")
o["cert_null"] = dict(n_checks=8, mode="float equality (==)",
                      source="l178/static.json Q2b_null_anatomical")

# ---------------- G1: the crossing depth ------------------------------------
car_n = [SW["carrier"]["P"][d] / (LAM1 ** (d + 1) * _m_car)
         for d in range(DMAX)]
null_n = np.array([[NP_[i, d] / (LAM1 ** (d + 1) * _m_car) for d in range(DMAX)]
                   for i in range(NP_.shape[0])])
g1_rows = []
for d in range(DMAX):
    col = null_n[:, d]
    g1_rows.append(dict(
        depth=d + 1, carrier=car_n[d], null_med=float(np.median(col)),
        null_p05=float(np.percentile(col, 5)),
        null_p95=float(np.percentile(col, 95)),
        pct=float((col < car_n[d]).mean() * 100),
        ratio_med_over_carrier=float(np.median(col) / car_n[d]) if car_n[d] else None,
        carrier_share=SW["carrier"]["share"][d],
        null_share_med=float(np.median(NP_[:, d] / NT_[:, d])),
        carrier_cos_v1=SW["carrier"]["cos_v1"][d]))
d_star, d_star_kind = None, None
for r in g1_rows:
    if r["carrier"] >= r["null_p05"]:
        d_star = r["depth"]
        d_star_kind = "ABOVE_P95" if r["carrier"] > r["null_p95"] else "IN_BAND"
        break
if d_star is not None and (d_conv_car is None or d_star <= d_conv_car):
    G1 = "G1_THROUGH_ABOVE" if d_star_kind == "ABOVE_P95" else "G1_INTO_BAND"
elif d_conv_car is not None:
    G1 = "G1_VACUOUS"
elif d_star is None:
    G1 = "G1_NEVER"
else:
    G1 = "G1_UNREGISTERED_SHAPE"
# depth-invariance of the deficit past convergence (the honest reading of
# G1_VACUOUS: the ratio stops being a function of depth)
_rat = [r["ratio_med_over_carrier"] for r in g1_rows]
_ratd = [(i + 1, v) for i, v in enumerate(_rat) if v is not None]
_cut = d_conv_car if d_conv_car is not None else DMAX
_tailr = [v for dd_, v in _ratd if dd_ >= _cut] or [v for _, v in _ratd]
o["G1_crossing"] = dict(
    branch=G1, d_star=d_star, d_star_kind=d_star_kind,
    d_conv_carrier=d_conv_car, cos_bar=COS_BAR,
    d_conv_all={k: v for k, v in D_CONV.items()},
    rows=g1_rows,
    deficit_ratio_by_depth=_rat,
    deficit_ratio_tail_mean=float(np.mean(_tailr)),
    deficit_ratio_tail_spread=float((max(_tailr) - min(_tailr)) / max(_tailr)),
    lam1=LAM1,
    interpretation=(
        "past d_conv every actor's walk direction is the leading eigenvector, "
        "so the per-mass value converges to (left-eigenvector overlap of the "
        "source) x a depth-independent constant: the DEPTH-RESOLVED question "
        "dies there and the deficit becomes a single depth-invariant number."))
log(f"[G1] {G1} | d* {d_star} ({d_star_kind}) | d_conv {d_conv_car} | "
    f"deficit ratio by depth "
    + " ".join("na" if r is None else f"{r:.2f}" for r in _rat))

# ---------------- G2: SEARCH INFORMATION (routing leg) ----------------------
A_E = jv_abs_an
AMAX = float(A_E.max())
LW = -np.log10(A_E / AMAX)
assert float(LW.min()) >= 0.0
s_out_A = np.zeros(NL)
np.add.at(s_out_A, csr_cols, A_E)
assert float(s_out_A[csr_cols].min()) > 0.0
NLT = -np.log2(A_E / s_out_A[csr_cols])
assert float(NLT.min()) >= 0.0

_ordS = np.argsort(csr_cols, kind="stable")
_src_s = csr_cols[_ordS]
_tgt_s = csr_rows[_ordS]
_pos_in_sorted = np.empty(_ordS.size, np.int64)
_pos_in_sorted[_ordS] = np.arange(_ordS.size)
START = np.searchsorted(_src_s, np.arange(NL)).tolist()
END = np.searchsorted(_src_s, np.arange(NL) + 1).tolist()
L_L = LW[_ordS].tolist()
T_L = NLT[_ordS].tolist()
TGT0 = _tgt_s.tolist()
POOLS_IDX = POOL_ALL.tolist()
N_POOL = len(POOLS_IDX)
assert N_POOL == int(len(POOL_ALL)) == o["pools"]["n_pool_cells"]


def dijkstra_si(src, tgt):
    """L-shortest paths from src, carrying search information along the
    selected path. Pure python (no scipy in this venv)."""
    INF = float("inf")
    dist = [INF] * NL
    si = [INF] * NL
    done = bytearray(NL)
    dist[src] = 0.0
    si[src] = 0.0
    h = [(0.0, src)]
    pop = heapq.heappop
    push = heapq.heappush
    while h:
        d, u = pop(h)
        if done[u]:
            continue
        done[u] = 1
        su = si[u]
        for e in range(START[u], END[u]):
            v = tgt[e]
            if done[v]:
                continue
            nd = d + L_L[e]
            if nd < dist[v]:
                dist[v] = nd
                si[v] = su + T_L[e]
                push(h, (nd, v))
    return dist, si


def si_summary(dist, si):
    pd = [dist[i] for i in POOLS_IDX]
    ps = [si[i] for i in POOLS_IDX]
    fin = [i for i, x in enumerate(pd) if x != float("inf")]
    if not fin:
        return dict(n_reach=0, n_unreach=N_POOL, si_mean=None, si_min=None,
                    si_med=None, dist_mean=None)
    sv = sorted(ps[i] for i in fin)
    return dict(n_reach=len(fin), n_unreach=N_POOL - len(fin),
                si_mean=float(np.mean([ps[i] for i in fin])),
                si_min=float(sv[0]), si_med=float(sv[len(sv) // 2]),
                dist_mean=float(np.mean([pd[i] for i in fin])))


SI_ACT = {}
for name, lc in ACTORS.items():
    dd, ss = dijkstra_si(lc, TGT0)
    SI_ACT[name] = si_summary(dd, ss)
log(f"[G2] actors done: carrier SI mean {SI_ACT['carrier']['si_mean']} "
    f"({SI_ACT['carrier']['n_reach']}/{N_POOL} pool cells reachable) | twin "
    f"{SI_ACT['twin']['si_mean']}")

SI_NULL = []
for i, ch in enumerate(null_changed):
    tg = list(TGT0)
    for cidx, new_target in ch["changed"]:
        tg[int(_pos_in_sorted[cidx])] = new_target
    dd, ss = dijkstra_si(LC_CAR, tg)
    SI_NULL.append(si_summary(dd, ss))
    if i == 0:
        log(f"[G2] null draw 0: SI mean {SI_NULL[0]['si_mean']} "
            f"reach {SI_NULL[0]['n_reach']}")
_sin = np.array([(r["si_mean"] if r["si_mean"] is not None else np.nan)
                 for r in SI_NULL], float)
_rchn = np.array([r["n_reach"] for r in SI_NULL], float)
_car_si = SI_ACT["carrier"]["si_mean"]
_fam_si = [SI_ACT[n]["si_mean"] for n in list(ACTORS)[2:]
           if SI_ACT[n]["si_mean"] is not None]
_n_null_fin = int(np.isfinite(_sin).sum())
si_pct = (float((_sin[np.isfinite(_sin)] < _car_si).mean() * 100)
          if (_car_si is not None and _n_null_fin) else None)
if SI_ACT["carrier"]["n_reach"] <= N_POOL // 2 or si_pct is None:
    G2 = "G2_UNREACHABLE"
elif si_pct >= 95.0:
    G2 = "G2_SI_HIGH"
elif si_pct <= 5.0:
    G2 = "G2_SI_LOW"
else:
    G2 = "G2_SI_INSIDE"


def _siv(n):
    v = SI_ACT[n]["si_mean"]
    return float("inf") if v is None else v


o["G2_search_information"] = dict(
    branch=G2, carrier=SI_ACT["carrier"], twin=SI_ACT["twin"],
    family_si_mean_med=float(np.median(_fam_si)) if _fam_si else None,
    family_si_mean_min=float(np.min(_fam_si)) if _fam_si else None,
    family_si_mean_max=float(np.max(_fam_si)) if _fam_si else None,
    n_family_with_si=len(_fam_si),
    carrier_rank_of_35=int(1 + sum(1 for n in ACTORS
                                   if _siv(n) < _siv("carrier"))),
    null_si_med=float(np.nanmedian(_sin)),
    null_si_p05=float(np.nanpercentile(_sin, 5)),
    null_si_p95=float(np.nanpercentile(_sin, 95)),
    n_null_finite=_n_null_fin,
    carrier_percentile=si_pct,
    null_reach_med=float(np.median(_rchn)),
    n_pool_cells=N_POOL,
    definitions=dict(
        length="L_uv = -log10(A_uv / A_max), A = |g*W_beta| (our domain "
               "choice, DISCLOSED: the field normalises weights to (0,1] "
               "before the log)",
        A_max=AMAX,
        transition="T_uv = A_uv / out-strength(u)",
        SI="-log2(prod T) accumulated along the L-shortest path during "
           "relaxation (so it is the SI of the path the length metric picks)",
        tie_note="ties in L are broken by heap order; disclosed, not "
                 "controlled."),
    all_actors=SI_ACT)
log(f"[G2] {G2}: carrier SI mean {_car_si} vs null med "
    f"{float(np.nanmedian(_sin)):.4f} [p05 {float(np.nanpercentile(_sin,5)):.4f}, "
    f"p95 {float(np.nanpercentile(_sin,95)):.4f}] -> pct {si_pct}; family "
    f"med {o['G2_search_information']['family_si_mean_med']}")

# ---------------- G3: diffusion vs routing (descriptive, no bar) ------------
_diff_pct2 = g1_rows[1]["pct"]
agree = (si_pct is not None
         and ((_diff_pct2 <= 5.0 and si_pct >= 95.0)
              or (_diff_pct2 >= 95.0 and si_pct <= 5.0)))
o["G3_diffusion_vs_routing"] = dict(
    diffusion_percentile_depth2=_diff_pct2,
    diffusion_percentile_depth3=g1_rows[2]["pct"],
    routing_percentile=si_pct,
    AGREE_on_avoidance=bool(agree),
    reading=("agreement = the carrier is both low-communicability AND "
             "hidden-route; disagreement DATES the avoidance to a "
             "broadcast-vs-route level and is informative, not an instrument "
             "failure (registered in advance, tick-233 amendment (d))."),
    field_prior="Seguin et al: diffusion beat routing for SC-FC "
                "correspondence (communicability +7.9% peak AMI over SC, "
                "p<1e-16; navigation the only model that made it WORSE).")

# ---------------- the Crofts leg, reported beside N1 ------------------------
_car_c = [SW["carrier"]["P_crofts"][d] / (LAM1C ** (d + 1)) for d in range(DMAX)]
_fam_c2 = [SW[n]["P_crofts"][1] / (LAM1C ** 2) for n in list(ACTORS)[2:]]
o["N2_crofts"] = dict(
    lam1=LAM1C,
    carrier_by_depth=_car_c,
    twin_by_depth=[SW["twin"]["P_crofts"][d] / (LAM1C ** (d + 1))
                   for d in range(DMAX)],
    family_depth2_med=float(np.median(_fam_c2)),
    carrier_rank_of_35_depth2=int(
        1 + sum(1 for n in ACTORS
                if SW[n]["P_crofts"][1] / (LAM1C ** 2)
                > SW["carrier"]["P_crofts"][1] / (LAM1C ** 2))),
    carrier_share_crofts=SW["carrier"]["share_crofts"],
    note="Crofts/Estrada strength normalisation applied to the weights "
         "BEFORE the walk sum; no spectral-death diagnostic, hence not "
         "primary (tick-233 amendment (b)). No null re-run on this leg: the "
         "swaps preserve out-strength but NOT every node's total strength "
         "under the sqrt(s_i s_j) transform, so a Crofts null would not be "
         "the registered null — DISCLOSED, and the leg is reported as an "
         "ordering check only.")

# ---------------- family context + the 35-actor depth table ----------------
_fam = list(ACTORS)[2:]
o["family_context"] = dict(
    n_family=len(_fam),
    carrier_rank_by_depth={
        str(d + 1): int(1 + sum(1 for n in ACTORS
                                if SW[n]["P"][d] / M_OUT[n]
                                > SW["carrier"]["P"][d] / _m_car))
        for d in range(DMAX)},
    family_med_per_mass_by_depth={
        str(d + 1): float(np.median([SW[n]["P"][d] / M_OUT[n] for n in _fam]))
        for d in range(DMAX)},
    carrier_per_mass_by_depth={str(d + 1): SW["carrier"]["P"][d] / _m_car
                               for d in range(DMAX)},
    twin_per_mass_by_depth={str(d + 1): SW["twin"]["P"][d] / M_OUT["twin"]
                            for d in range(DMAX)},
    share_by_depth_carrier=SW["carrier"]["share"],
    share_by_depth_twin=SW["twin"]["share"],
    share_by_depth_family_med={
        str(d + 1): float(np.median([SW[n]["share"][d] for n in _fam]))
        for d in range(DMAX)})

o["sweep"] = {n: dict(P=SW[n]["P"], share=SW[n]["share"],
                      cos_v1=SW[n]["cos_v1"], m_out=M_OUT[n],
                      gi=GI_OF[n]) for n in ACTORS}
o["null_sweep"] = dict(
    n_draws=int(NP_.shape[0]), seed=16943,
    P_med=[float(np.median(NP_[:, d])) for d in range(DMAX)],
    P_p05=[float(np.percentile(NP_[:, d], 5)) for d in range(DMAX)],
    P_p95=[float(np.percentile(NP_[:, d], 95)) for d in range(DMAX)],
    share_med=[float(np.median(NP_[:, d] / NT_[:, d])) for d in range(DMAX)],
    med_n_changed=float(np.median([c["n_changed"] for c in null_changed])))

# ---------------- predictions, scored --------------------------------------
_q1 = (G1 == "G1_VACUOUS" and d_conv_car is not None and d_conv_car <= 6)
_rv = [v for _, v in _ratd]
_mono = (len(_rv) > 1
         and all(_rv[i + 1] <= _rv[i] + 1e-12 for i in range(len(_rv) - 1)))
o["predictions"] = dict(
    Q206_1=dict(text="G1_VACUOUS with d_conv <= 6", correct=bool(_q1),
                measured=dict(branch=G1, d_conv=d_conv_car)),
    Q206_2=dict(text="the deficit ratio shrinks monotonically from depth 2",
                correct=bool(_mono),
                measured=dict(ratio_by_depth=_rat)),
    Q206_3=dict(text="SI does not separate the carrier (G2_SI_INSIDE)",
                correct=bool(G2 == "G2_SI_INSIDE"),
                measured=dict(branch=G2, percentile=si_pct)),
    Q206_4=dict(text="the Crofts leg agrees in ORDER (carrier below family)",
                correct=bool(o["N2_crofts"]["carrier_rank_of_35_depth2"] > 17),
                measured=dict(rank=o["N2_crofts"]["carrier_rank_of_35_depth2"],
                              of=35)))

o["references_for_L174"] = [
    "Seguin, Sporns & Zalesky, Nat Rev Neurosci 24:557-574 (2023) — taxonomy",
    "Estrada & Hatano, Phys Rev E 77:036111 (2008) — communicability",
    "Rosvall et al, Phys Rev E 72:046117 (2005) — search information",
    "Goni et al, PNAS 111:833-838 (2014) — FC from communication",
    "Avena-Koenigsberger, Misic & Sporns, Nat Rev Neurosci 19:17-33 (2018)",
    "Winding et al, Science 379:eadd9330 (2023) — the in-insect precedent",
]
o["limitations"] = [
    "ANATOMICAL leg only: no row mask, no settle, no dynamics — this is the "
    "wiring's walk geometry, NOT an operating point (L164).",
    "operator powers are walks WITH revisits, not simple paths (L178).",
    "the null is a GEOMETRY null (degree-neutral destination swaps of the "
    "carrier's own edges), not a re-settled dynamics null.",
    "the SI length transform divides by A_max — a domain choice, disclosed; "
    "and SI ties are broken by heap order.",
    "the Crofts leg carries NO null (the swaps are not strength-neutral "
    "under sqrt(s_i s_j)) and is an ordering check only.",
    "a crossing depth is only meaningful BELOW d_conv: past it every walk "
    "points along v1 and the deficit is depth-invariant by construction.",
]
o["pins"] = "ALL GREEN"
json.dump(o, open("l206/static.json", "w"), indent=1)
log("=" * 72)
log(f"L206 DONE {time.time()-t0:.0f}s | lam1 {LAM1:.4f} | G1 {G1} "
    f"(d* {d_star}, d_conv {d_conv_car}) | G2 {G2} (pct {si_pct:.1f}) | "
    f"G3 agree {bool(agree)} | CERT-178 {_n_chk} + CERT-NULL 8 float-exact")
