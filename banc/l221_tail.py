# ================= L221 TAIL (appended by l221_build.py) =================
# Everything above this line is VERBATIM source:
#   l151_static.py 1-319, l178_tail.py 7-149, l206_mid.py,
#   l178_tail.py 348-458, l206_tail.py 22-263, l211_mid2.py,
#   l206_tail.py 320-461, l211_tail.py 29-322, l220_tail.py 47-128.
# So CERT-F4, the gains at float equality, the CSR orientation, the 20 pool
# sizes, CERT-REW (l169c P6), CERT-178's 420 anatomical values, the lam1
# power iteration, CERT-NULL, L206's WHOLE search-information block (CERT-SI
# 240, dijkstra_si, si_summary), L211's WHOLE decomposition (CERT-MENU 100,
# CERT-FH 61,819, dijkstra_si_fh, fh_summary, _pct, NULL_FH, COH), CERT-211
# (434) and CERT-SIGEN (1,922,356 — the generic SI-index builder) have ALL
# re-run as free certification before any L221 number is read.
# PREREG: l221/PREREG.md (registered first, with three premise corrections).
# Writes l221/static.json ONLY. Zero rollouts, zero settles, zero dynamics.
import os as _os221

o["design"] = (
    "L221 the FIRST-HOP FUNNEL: is L211's 11-of-69 narrow first-hop set a "
    "property of the carrier's out-weight SKEW (0b: degenerate as written), "
    "its TARGETS' onward reach, or an artifact of the -log10 length metric? "
    "Three metrics (abs / Crofts strength / plain hop count), EDGE-identity "
    "walker, tie-free feasible sets via a shortest-path-DAG bitmask, and a "
    "nonselective 35-actor pool-geometry control reported BEFORE the branch. "
    "PREREG l221/PREREG.md.")
o["prereg"] = "l221/PREREG.md"
with open("l221_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(14)])

FP221 = {}
for _p in ("l206/static.json", "l178/static.json", "l211/static.json",
           "l169c/static.json"):
    _st = _os221.stat(_p)
    FP221[_p] = (int(_st.st_size), int(_st.st_mtime_ns))

log("=" * 72)
log("[L221] the FIRST-HOP FUNNEL on f4wA (static, zero rollouts)")

# the inherited CERT-SIGEN gate proved build_si_index reproduces the certified
# f4wA index.  That is the object every metric below is built with.
assert _IX_F4["START"] == START and _IX_F4["END"] == END
assert _IX_F4["TGT0"] == TGT0
N_EDGE_221 = len(T_L)
CB0, CB1 = START[LC_CAR], END[LC_CAR]
K_OUT = CB1 - CB0
assert K_OUT == 69 == o["csr_orientation"]["out_edges"], ("out-degree", K_OUT)

# ---------------- CERT-D5 (HALTING): L178's five, re-derived and gated ------
# L178's own expression (l178_tail.py 625-639) over csr_rows/csr_cols/POOL_ALL.
# The parent stored only the COUNTS (5 carrier, 19 twin), never the identities,
# so a re-derivation is NECESSARY -- and therefore it is GATED against those
# stored counts at integer equality (the L219 CERT-219D pattern).
_pool_flag221 = np.zeros(NL, bool)
_pool_flag221[POOL_ALL] = True
_pool_out_deg221 = np.zeros(NL, np.int64)
_into221 = _pool_flag221[csr_rows]
np.add.at(_pool_out_deg221, csr_cols[_into221], 1)
_S178_221 = json.load(open("l178/static.json"))
_D5 = {}
_cert_d5 = 0
for _nm, _lc in (("carrier", LC_CAR), ("twin", LC_TWIN)):
    _tg221 = np.unique(np.asarray(TGT0)[START[_lc]:END[_lc]])
    _withpool = _tg221[_pool_out_deg221[_tg221] > 0]
    _st178 = _S178_221["D_depth2_anatomy"]["per_actor"][_nm]
    assert int(len(_tg221)) == int(_st178["n_targets"]), (_nm, "n_targets")
    assert int(len(_withpool)) == int(_st178["n_targets_with_pool_outedge"]), \
        (_nm, len(_withpool), _st178["n_targets_with_pool_outedge"], "CERT-D5")
    assert int(_pool_out_deg221[_tg221].sum()) == \
        int(_st178["pool_outedges_from_targets"]), (_nm, "pool_outedges")
    _cert_d5 += 3
    _D5[_nm] = [int(x) for x in _withpool]
assert len(_D5["carrier"]) == 5 and len(_D5["twin"]) == 19, "CERT-D5 pin"
FIVE = set(_D5["carrier"])
log(f"[CERT-D5] GREEN {_cert_d5} integer equalities vs L178's stored anatomy; "
    f"the carrier's FIVE pool-out-edge targets identified: {sorted(FIVE)}")

# ---------------- CERT-CROFTS (HALTING): metric 2 is L206's own operator ----
# jv_crofts / s_safe / LAM1C come from the certified l206_tail.py 22-263 slice,
# so the transform is NOT re-transcribed here; this gate proves the operator in
# hand is the one l206/static.json certified.  The bar is DERIVED from that
# operator's own measured convergence (rel_spread_crofts ~1.06e-08, the L216
# law: never a fixed 1e-9 bar on an operator that cannot reach it).
_S206_221 = json.load(open("l206/static.json"))
_lc_stored = _S206_221["spectral"]["lam1_crofts"]
_spread_stored = _S206_221["spectral"]["rel_spread_crofts"]
_bar_crofts = max(10.0 * float(_spread_stored), 1e-12)
_rel_lc = abs(LAM1C - _lc_stored) / abs(_lc_stored)
assert _rel_lc <= _bar_crofts, (LAM1C, _lc_stored, _rel_lc, _bar_crofts)
assert float(jv_crofts.min()) > 0.0, "a nonpositive Crofts weight"
assert jv_crofts.shape == jv_abs_an.shape
log(f"[CERT-CROFTS] GREEN lam1(A_crofts) {LAM1C:.12f} vs stored "
    f"{_lc_stored:.12f} (rel {_rel_lc:.3e} <= derived bar {_bar_crofts:.3e} "
    f"= 10x the operator's own measured rel_spread)")

# ---------------- the three metrics (edge INDEXING is shared) ---------------
_IX_CR = build_si_index(jv_crofts, csr_rows, csr_cols, NL, POOL_ALL)
# build_si_index sorts by cols with a STABLE argsort, so the edge index map is
# a function of csr_cols ALONE: identical across metrics.  Asserted, not assumed
# -- without this the three used-sets would not be comparable at all.
assert _IX_CR["START"] == START and _IX_CR["END"] == END, "crofts START/END"
assert _IX_CR["TGT0"] == TGT0, "crofts edge order differs (sets incomparable)"
assert _IX_CR["POOLS_IDX"] == POOLS_IDX and _IX_CR["N_POOL"] == N_POOL
L_CR, T_CR = _IX_CR["L_L"], _IX_CR["T_L"]
L_HOP = [1.0] * N_EDGE_221          # metric 3: L constant, T_L UNCHANGED
METRICS = (("abs", L_L, T_L), ("crofts", L_CR, T_CR), ("hop", L_HOP, T_L))
assert L_CR != L_L, "the Crofts length metric is identical to abs (no re-rank)"
log(f"[L221] three metrics ready on {N_EDGE_221:,} shared edge indices: "
    f"abs (L=-log10 A/Amax), crofts (A/sqrt(s_i s_j)), hop (L==1, T_L kept)")


# ---------------- the EDGE-IDENTITY walker (gated by CERT-FHE) -------------
def dijkstra_fe(src, tgt, Lm, Tm, start, end, nl):
    """The certified dijkstra_si relaxation, verbatim in structure, carrying
    the first-hop EDGE INDEX (not its cost) as the inherited field. Gated by
    CERT-FHE against the certified dijkstra_si / dijkstra_si_fh themselves."""
    INF = float("inf")
    dist = [INF] * nl
    si = [INF] * nl
    fe = [-1] * nl
    hop = [0] * nl
    done = bytearray(nl)
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
        fu = fe[u]
        hu = hop[u]
        for e in range(start[u], end[u]):
            v = tgt[e]
            if done[v]:
                continue
            nd = d + Lm[e]
            if nd < dist[v]:
                dist[v] = nd
                si[v] = su + Tm[e]
                fe[v] = e if u == src else fu
                hop[v] = hu + 1
                push(h, (nd, v))
    return dist, si, fe, hop


def realised_set(fe, pools):
    """the first-hop EDGES actually used on the chosen optimal paths."""
    return set(fe[i] for i in pools if fe[i] >= 0)


def feasible_mask(src, tgt, Lm, start, end, nl, tol):
    """every out-edge of src lying on AT LEAST ONE optimal path to each node,
    exactly: a forward pass over the shortest-path DAG carrying a K_OUT-bit
    integer mask (one bit per out-edge of src). Tie-free by construction --
    which is why metric 3 (L==1, massive ties) is scoreable at all (PREREG 0c).
    Zero-length edges exist (the A_max edge has L==0), so equal-distance
    propagation is possible: sweep to a FIXPOINT and assert convergence."""
    INF = float("inf")
    dist = [INF] * nl
    done = bytearray(nl)
    dist[src] = 0.0
    h = [(0.0, src)]
    pop = heapq.heappop
    push = heapq.heappush
    while h:
        d, u = pop(h)
        if done[u]:
            continue
        done[u] = 1
        for e in range(start[u], end[u]):
            v = tgt[e]
            if done[v]:
                continue
            nd = d + Lm[e]
            if nd < dist[v]:
                dist[v] = nd
                push(h, (nd, v))
    mask = [0] * nl
    k0, k1 = start[src], end[src]
    for j in range(k0, k1):
        v = tgt[j]
        if dist[v] != INF and abs(dist[v] - Lm[j]) <= tol:
            mask[v] |= 1 << (j - k0)
    order = sorted((i for i in range(nl) if dist[i] != INF and i != src),
                   key=lambda i: dist[i])
    sweeps = 0
    while True:
        changed = 0
        for u in order:
            mu = mask[u]
            if not mu:
                continue
            du = dist[u]
            for e in range(start[u], end[u]):
                v = tgt[e]
                if v == src:
                    continue
                if du + Lm[e] <= dist[v] + tol:
                    nm = mask[v] | mu
                    if nm != mask[v]:
                        mask[v] = nm
                        changed += 1
        sweeps += 1
        if changed == 0:
            break
        assert sweeps <= 6, ("feasible mask did not converge", sweeps, changed)
    return dist, mask, sweeps


def bits(x):
    s = set()
    j = 0
    while x:
        if x & 1:
            s.add(j)
        x >>= 1
        j += 1
    return s


def jac(a, b):
    return (1.0 if not a and not b
            else float(len(a & b)) / float(len(a | b)))


# ---------------- CERT-FHE (HALTING): the edge walker vs both certified ones -
_cert_fhe = 0
for _nm, _lc in (("carrier", LC_CAR), ("twin", LC_TWIN)):
    _d0, _s0 = dijkstra_si(_lc, TGT0)
    _d1, _s1, _f1, _h1 = dijkstra_si_fh(_lc, TGT0)
    _d2, _s2, _fe2, _h2 = dijkstra_fe(_lc, TGT0, L_L, T_L, START, END, NL)
    for _i in POOLS_IDX:
        assert _d0[_i] == _d2[_i], (_nm, _i, "dist not EXACTLY equal")
        assert _s0[_i] == _s2[_i], (_nm, _i, "si not EXACTLY equal")
        assert _h1[_i] == _h2[_i], (_nm, _i, "hop not EXACTLY equal")
        assert T_L[_fe2[_i]] == _f1[_i], (_nm, _i, "first-hop COST mismatch")
        assert START[_lc] <= _fe2[_i] < END[_lc], (_nm, _i, "fe not an out-edge")
        _cert_fhe += 5
log(f"[CERT-FHE] GREEN actors: {_cert_fhe} EXACT equalities (dist/si/hop and "
    f"T_L[first-hop edge] == the certified fh) for carrier + twin")

NULL_FE = []
for _k, _ch in enumerate(null_changed):
    _tg = list(TGT0)
    for _cidx, _nt in _ch["changed"]:
        _tg[int(_pos_in_sorted[_cidx])] = _nt
    _d1, _s1, _f1, _h1 = dijkstra_si_fh(LC_CAR, _tg)
    _d2, _s2, _fe2, _h2 = dijkstra_fe(LC_CAR, _tg, L_L, T_L, START, END, NL)
    for _i in POOLS_IDX:
        assert _d1[_i] == _d2[_i], (_k, _i, "null dist")
        assert _s1[_i] == _s2[_i], (_k, _i, "null si")
        assert T_L[_fe2[_i]] == _f1[_i], (_k, _i, "null first-hop COST")
        _cert_fhe += 3
    _rs = realised_set(_fe2, POOLS_IDX)
    NULL_FE.append(dict(n_edges=int(len(_rs)),
                        n_costs=int(NULL_FH[_k]["n_distinct_first_hops"]),
                        edges=sorted(int(x - CB0) for x in _rs)))
assert len(NULL_FE) == 100
log(f"[CERT-FHE] GREEN all 100 draws: {_cert_fhe} EXACT equalities total")

# ---------------- the carrier, under all three metrics ---------------------
TOL = 1e-12
MET = {}
for _mn, _Lm, _Tm in METRICS:
    _d, _s, _fe, _h = dijkstra_fe(LC_CAR, TGT0, _Lm, _Tm, START, END, NL)
    _rs = realised_set(_fe, POOLS_IDX)
    _dd, _mask, _sw = feasible_mask(LC_CAR, TGT0, _Lm, START, END, NL, TOL)
    _dd0, _mask0, _sw0 = feasible_mask(LC_CAR, TGT0, _Lm, START, END, NL, 0.0)
    _feas = set()
    for _i in POOLS_IDX:
        _feas |= bits(_mask[_i])
    _feas0 = set()
    for _i in POOLS_IDX:
        _feas0 |= bits(_mask0[_i])
    _rs_j = set(int(x - CB0) for x in _rs)
    # CERT-DAG (HALTING): a realised optimum IS feasible, per pool cell.
    _nd = 0
    for _i in POOLS_IDX:
        if _fe[_i] >= 0:
            assert (_fe[_i] - CB0) in bits(_mask[_i]), \
                (_mn, _i, "realised first hop absent from its feasible mask")
            _nd += 1
    assert _rs_j <= _feas, (_mn, "realised set is not a subset of feasible")
    assert len(_dd) == NL and abs(_dd[LC_CAR]) == 0.0
    _load = {}
    for _i in POOLS_IDX:
        if _fe[_i] >= 0:
            _load[int(_fe[_i] - CB0)] = _load.get(int(_fe[_i] - CB0), 0) + 1
    MET[_mn] = dict(
        n_reach=int(sum(1 for _i in POOLS_IDX if _d[_i] != float("inf"))),
        realised_edges=sorted(_rs_j), n_realised=int(len(_rs_j)),
        n_realised_costs=int(len(set(round(_Tm[_e], 12) for _e in _rs))),
        feasible_edges=sorted(_feas), n_feasible=int(len(_feas)),
        n_feasible_tol0=int(len(_feas0)),
        feasible_tol_added=sorted(_feas - _feas0),
        sweeps=int(_sw), cert_dag_checks=int(_nd),
        load=dict(sorted(((str(k), v) for k, v in _load.items()),
                         key=lambda kv: -kv[1])),
        si_mean=float(np.mean([_s[_i] for _i in POOLS_IDX
                               if _d[_i] != float("inf")])),
        hop_mean=float(np.mean([_h[_i] for _i in POOLS_IDX
                                if _d[_i] != float("inf")])))
    log(f"[L221] metric {_mn}: realised {MET[_mn]['n_realised']} edges "
        f"({MET[_mn]['n_realised_costs']} distinct costs) | feasible "
        f"{MET[_mn]['n_feasible']} (tol0 {MET[_mn]['n_feasible_tol0']}) | "
        f"reach {MET[_mn]['n_reach']}/{N_POOL} | sweeps {MET[_mn]['sweeps']}")

# 0a: the parent's 11 was a COST count. Is it the EDGE count?
_ab = MET["abs"]
assert _ab["n_reach"] == 303 and _ab["si_mean"] == CAR["si_mean"], "abs drift"
assert _ab["n_realised_costs"] == CAR["n_distinct_first_hops"] == 11, \
    ("0a: the cost count did not reproduce the parent's 11",
     _ab["n_realised_costs"])
o["Q221_0a_costs_vs_edges"] = dict(
    parent_n_distinct_first_hop_COSTS=int(CAR["n_distinct_first_hops"]),
    measured_n_distinct_first_hop_EDGES=int(_ab["n_realised"]),
    equal=bool(_ab["n_realised"] == CAR["n_distinct_first_hops"]),
    note="L211's n_distinct_first_hops counts distinct ROUNDED T_L VALUES "
         "(fh_summary), i.e. costs. If EDGES > COSTS the parent's 11 is a "
         "LOWER BOUND on the realised edge set. Registered as PREREG 0a and "
         "as prediction P2 before measuring.")

# ---------------- the registered bar ---------------------------------------
_pairs = (("abs", "crofts"), ("abs", "hop"), ("crofts", "hop"))
JF = {f"{a}|{b}": jac(set(MET[a]["feasible_edges"]),
                      set(MET[b]["feasible_edges"])) for a, b in _pairs}
JR = {f"{a}|{b}": jac(set(MET[a]["realised_edges"]),
                      set(MET[b]["realised_edges"])) for a, b in _pairs}
J_MIN_F = float(min(JF.values()))
J_MIN_R = float(min(JR.values()))
_ndfe = np.array([r["n_edges"] for r in NULL_FE], float)
P05_NULL = float(np.percentile(_ndfe, 5))
N_REAL = int(_ab["n_realised"])
NARROW = bool(N_REAL < P05_NULL)
BAR_J = 0.80
if J_MIN_F >= BAR_J and NARROW:
    BR221 = "F_REAL"
elif J_MIN_F < BAR_J and NARROW:
    BR221 = "F_METRIC"
elif J_MIN_F >= BAR_J and not NARROW:
    BR221 = "F_NOT_NARROW"
else:
    BR221 = "F_BOTH_FAIL"

# ---------------- the POOL-GEOMETRY control, BEFORE the branch -------------
# Borrowed from L238's registered demotion escape, CITED to L238 and NOT
# re-banked as independent evidence (the Q219-5 discipline). Nonselective over
# all 35 L178 actors, because the carrier was SELECTED on a related statistic.
CENSUS = {}
for _nm, _lc in ACTORS.items():
    _d, _s, _fe, _h = dijkstra_fe(_lc, TGT0, L_L, T_L, START, END, NL)
    _rs = realised_set(_fe, POOLS_IDX)
    _k = END[_lc] - START[_lc]
    CENSUS[_nm] = dict(menu=int(_k), n_realised=int(len(_rs)),
                       n_reach=int(sum(1 for _i in POOLS_IDX
                                       if _d[_i] != float("inf"))),
                       frac_menu_used=(float(len(_rs)) / _k if _k else None))
assert len(CENSUS) == 35
assert CENSUS["carrier"]["n_realised"] == N_REAL, "census/carrier disagree"
_cn = np.array([v["n_realised"] for v in CENSUS.values()], float)
_cf = np.array([v["frac_menu_used"] for v in CENSUS.values()], float)
CAR_PCT_N = float((_cn < N_REAL).mean())
CAR_PCT_F = float((_cf < CENSUS["carrier"]["frac_menu_used"]).mean())
o["Q221_pool_geometry_control"] = dict(
    cited_to="L238 (which owns the nonselective cross-substrate version); "
             "borrowed here because L221's claim is unreadable without it, "
             "and NOT re-banked as independent evidence (Q219-5 discipline)",
    n_actors=35,
    census_n_realised_med=float(np.median(_cn)),
    census_n_realised_min=float(_cn.min()), census_n_realised_max=float(_cn.max()),
    census_menu_med=float(np.median([v["menu"] for v in CENSUS.values()])),
    census_frac_menu_used_med=float(np.median(_cf)),
    carrier_n_realised=N_REAL,
    carrier_percentile_count=CAR_PCT_N,
    carrier_percentile_frac=CAR_PCT_F,
    spearman_menu_vs_realised=float(np.corrcoef(
        np.argsort(np.argsort([v["menu"] for v in CENSUS.values()])),
        np.argsort(np.argsort(_cn)))[0, 1]),
    demotes_card=bool(CAR_PCT_N > 0.20),
    note="if the carrier's realised count is unremarkable here the funnel "
         "belongs to the 303 pool cells' ENTRY GEOMETRY, not to the carrier, "
         "and this card's framing is demoted. Reported BEFORE the branch "
         "(L223's rho-first rule).",
    all_actors=CENSUS)
log(f"[L221] POOL-GEOMETRY control (nonselective, 35 actors): carrier "
    f"{N_REAL} realised vs census med {float(np.median(_cn)):.1f} "
    f"[{_cn.min():.0f}, {_cn.max():.0f}] -> pct {CAR_PCT_N:.3f}; "
    f"frac-of-menu pct {CAR_PCT_F:.3f}; demotes={CAR_PCT_N > 0.20}")

# ---------------- leg (a): the ONE weight statistic (PREREG 0b) ------------
_ordS221 = np.argsort(csr_cols, kind="stable")
_A_sorted = jv_abs_an[_ordS221]
assert _A_sorted.size == N_EDGE_221
_w = np.array([float(_A_sorted[CB0 + j]) for j in range(K_OUT)])
# the sorted-order weight vector must reproduce the certified T_L exactly
_sout_car = float(_w.sum())
for j in range(K_OUT):
    assert abs(T_L[CB0 + j] - float(-np.log2(_w[j] / _sout_car))) < 1e-12, \
        (j, "weight vector does not reproduce T_L")
_used = np.array([1.0 if j in set(_ab["realised_edges"]) else 0.0
                  for j in range(K_OUT)])


def _spear(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


_rho_w_used = _spear(_w, _used)
_rho_t_used = _spear(np.array([T_L[CB0 + j] for j in range(K_OUT)]), _used)
_rho_l_used = _spear(np.array([L_L[CB0 + j] for j in range(K_OUT)]), _used)
_wsort = np.sort(_w)[::-1]
_rank_of_used = sorted(int(1 + (_w > _w[j]).sum()) for j in range(K_OUT)
                       if _used[j] > 0)
o["Q221_a_weight_skew"] = dict(
    prereg="0b: for a FIXED source, T_L and L_L are both strictly DECREASING "
           "functions of A[e], so weight-vs-used, T_L-vs-used and L_L-vs-used "
           "are ONE statistic up to sign. Measured all three to show the "
           "identity rather than assert it. A positive rho is MECHANICALLY "
           "EXPECTED and is not evidence.",
    spearman_weight_vs_used=_rho_w_used,
    spearman_T_L_vs_used=_rho_t_used,
    spearman_L_L_vs_used=_rho_l_used,
    identity_holds=bool(abs(_rho_w_used + _rho_t_used) < 1e-12
                        and abs(_rho_w_used + _rho_l_used) < 1e-12),
    out_weight_rank_of_used_edges=_rank_of_used,
    mass_share_of_used_edges=float(_w[_used > 0].sum() / _w.sum()),
    n_used=int(_used.sum()), menu=K_OUT,
    top_weight_used=bool(_used[int(np.argmax(_w))] > 0),
    gini_DESCRIPTION_from_L219=dict(
        carrier=0.1493, family_med=0.1530, twin=0.1489,
        status="DESCRIPTION (observed while scoping; PREREG 0b.3)"))
log(f"[L221] leg (a): rho(w, used) {_rho_w_used:+.4f} == -rho(T_L, used) "
    f"{_rho_t_used:+.4f} (identity {o['Q221_a_weight_skew']['identity_holds']})"
    f"; the {int(_used.sum())} used edges carry "
    f"{float(_w[_used > 0].sum() / _w.sum()) * 100:.1f}% of out-mass; "
    f"weight ranks {_rank_of_used}")

# ---------------- leg (b): the used set vs L178's FIVE ---------------------
_tg_arr = np.asarray(TGT0)
_used_tg = {j: int(_tg_arr[CB0 + j]) for j in sorted(_ab["realised_edges"])}
_gid_f4 = np.where(keep_f4)[0]
assert _gid_f4.size == NL, ("local->global map", _gid_f4.size, NL)
try:
    _annmap = {int(r.gi): (str(r.super_class), str(r.cell_type), str(r.side))
               for r in ann.itertuples()}
except Exception as _e:                                    # noqa: BLE001
    _annmap = {}
    log(f"[L221] annotation map unavailable ({_e!r}) -- ids reported bare")
_rows_b = []
for j, _lt in _used_tg.items():
    _g = int(_gid_f4[_lt])
    _sc, _ct, _sd = _annmap.get(_g, ("?", "?", "?"))
    _rows_b.append(dict(
        edge_j=int(j), target_local=_lt, target_gid=_g,
        super_class=_sc, cell_type=_ct, side=_sd,
        T_L_bits=float(T_L[CB0 + j]), weight=float(_w[j]),
        pool_outedges=int(_pool_out_deg221[_lt]),
        in_L178_five=bool(_lt in FIVE),
        pool_cells_served=int(_ab["load"].get(str(j), 0))))
_used_tgs = set(_used_tg.values())
_five_in_used = FIVE & _used_tgs
_five_feasible = set()
for j in _ab["feasible_edges"]:
    _five_feasible |= ({int(_tg_arr[CB0 + j])} & FIVE)
o["Q221_b_target_reach"] = dict(
    n_used_edges=int(len(_used_tg)), n_used_distinct_targets=int(len(_used_tgs)),
    L178_five_targets_local=sorted(FIVE),
    n_five_in_realised=int(len(_five_in_used)),
    n_five_in_feasible=int(len(_five_feasible)),
    relation=("superset" if FIVE <= _used_tgs else
              "subset" if _used_tgs <= FIVE else
              "disjoint" if not _five_in_used else "overlapping"),
    five_pool_outedges={str(int(t)): int(_pool_out_deg221[int(t)])
                        for t in sorted(FIVE)},
    used_targets_with_pool_outedge=int(sum(
        1 for t in _used_tgs if _pool_out_deg221[int(t)] > 0)),
    used_edge_table=_rows_b)
log(f"[L221] leg (b): {len(_used_tg)} used first-hop edges -> "
    f"{len(_used_tgs)} distinct targets; "
    f"{len(_five_in_used)}/5 of L178's pool-out-edge targets realised, "
    f"{len(_five_feasible)}/5 feasible; relation "
    f"{o['Q221_b_target_reach']['relation']}; "
    f"{o['Q221_b_target_reach']['used_targets_with_pool_outedge']} used "
    f"targets carry a pool out-edge")

# ---------------- the primary ---------------------------------------------
o["L221_primary"] = dict(
    branch=BR221,
    bars=dict(jaccard_min_ge=BAR_J, narrow_if_n_edges_lt_null_p05=True),
    substrate="f4wA", tol_registered=TOL,
    J_feasible_pairwise=JF, J_min_feasible=J_MIN_F,
    J_realised_pairwise=JR, J_min_realised=J_MIN_R,
    n_realised_edges_abs=N_REAL,
    n_realised_costs_abs=int(_ab["n_realised_costs"]),
    null_n_edges_med=float(np.median(_ndfe)),
    null_n_edges_p05=P05_NULL,
    null_n_edges_min=float(_ndfe.min()), null_n_edges_max=float(_ndfe.max()),
    null_n_costs_med=float(np.median([r["n_costs"] for r in NULL_FE])),
    carrier_pct_vs_null=_pct(float(N_REAL), _ndfe),
    narrow=NARROW,
    per_metric={k: {kk: vv for kk, vv in v.items() if kk != "load"}
                for k, v in MET.items()},
    per_metric_load={k: v["load"] for k, v in MET.items()},
    reading="the >=80% bar is scored on the FEASIBLE sets (tie-free, "
            "metric-comparable, PREREG 0c); the realised sets are reported "
            "beside and are tie-sensitive under metric 3 by construction.")
log(f"[L221] {BR221}: J_min(feasible) {J_MIN_F:.4f} vs bar {BAR_J} | "
    f"realised edges {N_REAL} vs null p05 {P05_NULL:.1f} "
    f"(med {float(np.median(_ndfe)):.1f}) -> narrow={NARROW} | "
    f"J_min(realised) {J_MIN_R:.4f}")

# ---------------- predictions, scored --------------------------------------
_q = {}
_q["Q221_1"] = dict(text="branch is F_REAL", correct=bool(BR221 == "F_REAL"),
                    measured=BR221)
_q["Q221_2"] = dict(text="n_distinct_first_hop_EDGES == 11 (no T_L ties)",
                    correct=bool(N_REAL == 11), measured=N_REAL)
_q["Q221_3"] = dict(text=">=3 of L178's five pool-out-edge targets are in the "
                         "realised first-hop set",
                    correct=bool(len(_five_in_used) >= 3),
                    measured=int(len(_five_in_used)))
_q["Q221_4"] = dict(text="spearman(A_e, used) > 0 (mechanically expected)",
                    correct=bool(_rho_w_used > 0), measured=_rho_w_used)
_q["Q221_5"] = dict(text="carrier realised count at/below the 20th percentile "
                         "of the nonselective 35-actor census",
                    correct=bool(CAR_PCT_N <= 0.20), measured=CAR_PCT_N)
o["predictions"] = _q
o["predictions_score"] = f"{sum(1 for v in _q.values() if v['correct'])} of 5"

o["certification"] = dict(
    inherited_free=[
        "CERT-F4 + gains at float equality + CSR orientation (69 out / 12 in) "
        "+ 20 pool sizes (l178_tail 7-149)",
        "CERT-REW = l169c P6 + rewire_draws + the 100 draws (l178_tail 348-458)",
        "CERT-178 = 420 stored L178 anatomical values at float equality, lam1 "
        "power iteration, CERT-NULL 8 (l206_tail 22-263)",
        "CERT-SI = 240 stored L206 search-information values at float "
        "equality (l206_tail 320-461 re-executed whole)",
        "CERT-MENU 100 + CERT-FH 61,819 + the whole L211 decomposition "
        "(l211_tail 29-322)",
        "CERT-211 434 + CERT-SIGEN 1,922,356 (l220_tail 47-128)"],
    new_halting_gates=dict(
        CERT_D5=dict(checks=_cert_d5,
                     what="L178's n_targets / n_targets_with_pool_outedge / "
                          "pool_outedges_from_targets re-derived from its own "
                          "expression and gated at INTEGER equality against "
                          "the stored 5 (carrier) and 19 (twin) -- the parent "
                          "never stored the identities, so the re-derivation "
                          "is necessary and therefore gated"),
        CERT_CROFTS=dict(rel=_rel_lc, bar=_bar_crofts,
                         what="power_iter(jv_crofts) reproduces "
                              "l206/static.json lam1_crofts; the bar is "
                              "DERIVED from that operator's own measured "
                              "rel_spread (L216), never fixed in advance"),
        CERT_FHE=dict(checks=_cert_fhe,
                      what="the edge-index walker's dist/si/hop and "
                           "T_L[first-hop edge] equal the certified "
                           "dijkstra_si / dijkstra_si_fh at EXACT equality on "
                           "all 303 pool cells for carrier, twin and all 100 "
                           "draws -- the modified walker is GATED, never "
                           "trusted (the L210 CERT-MV pattern)"),
        CERT_DAG=dict(checks={k: v["cert_dag_checks"] for k, v in MET.items()},
                      what="every realised first hop is a MEMBER of its pool "
                           "cell's feasible mask and the realised set is a "
                           "SUBSET of the feasible set, on all three metrics"),
        CERT_EDGEIDX=dict(
            what="build_si_index's edge index map is a function of csr_cols "
                 "ALONE (stable argsort), so START/END/TGT0 are asserted "
                 "IDENTICAL across the three metrics -- without this the "
                 "three used-sets would not be comparable at all")),
    fingerprints_unchanged=None,
    source_slices=[
        "l151_static.py 1-319", "l178_tail.py 7-149", "l206_mid.py",
        "l178_tail.py 348-458", "l206_tail.py 22-263", "l211_mid2.py",
        "l206_tail.py 320-461", "l211_tail.py 29-322 (CERT-211SL)",
        "l220_tail.py 47-128 (CERT-220SL: CERT-211 + build_si_index + "
        "CERT-SIGEN, sliced to CUT every cutwA block and the writer)"])

o["limitations"] = [
    "ONE substrate (f4wA). The cutwA leg is DEFERRED to L238 on purpose, "
    "which owns the two-substrate first-hop IDENTITY comparison "
    "nonselectively with BH-FDR; doing it here would double-bank it.",
    "ONE null family (the l169c degree-neutral destination swaps) -- L207's "
    "cross-null law: a deficit/narrowness magnitude is null-specific and does "
    "not transport between comparison sets.",
    "The null relocates the CARRIER's destinations only, so it is not a null "
    "for any other actor: the 35-actor census is a DESCRIPTIVE cohort read, "
    "and its only job is the demotion check, not an effect size.",
    "The carrier's out-weight Gini and L219's Spearman(w_e, u1[t_e]) are "
    "DESCRIPTION here (observed while scoping, PREREG 0b.3 / section 5).",
    "Metric 3 keeps T_L fixed and changes only path SELECTION; metric 2 "
    "changes both. So an agreement across all three is evidence about the "
    "length metric's domain choice, not about the transition law in general.",
    "The feasible set is 'feasible up to TOL=1e-12' on the weighted metrics; "
    "the TOL=0.0 set is reported beside it so the tolerance's effect is "
    "visible rather than assumed.",
    "A used-set is not a mechanism: WHY those particular targets are the "
    "entry points is L237's question (why those cells have low u1) in the "
    "routing currency."]

for _p, _fp in FP221.items():
    _st = _os221.stat(_p)
    assert (int(_st.st_size), int(_st.st_mtime_ns)) == _fp, (_p, "MUTATED")
o["certification"]["fingerprints_unchanged"] = {k: list(v)
                                                for k, v in FP221.items()}
o["pins"] = "ALL GREEN"
json.dump(o, open("l221/static.json", "w"), indent=1)
log("=" * 72)
log(f"L221 DONE {time.time()-t0:.0f}s | {BR221} | J_min(feas) {J_MIN_F:.4f} | "
    f"edges {N_REAL} vs null p05 {P05_NULL:.1f} | census pct {CAR_PCT_N:.3f} | "
    f"predictions {o['predictions_score']} | CERT-FHE {_cert_fhe} + CERT-D5 "
    f"{_cert_d5}")
