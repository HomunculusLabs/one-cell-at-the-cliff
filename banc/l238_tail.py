# ================= L238 TAIL (appended by l238_build.py) =================
# Everything above this line is VERBATIM l220_static.py lines 1-1916 (see
# l238_build.py): the nine certified slices of L220 AND the L220 body sliced
# to CUT its predictions/writer block. So L220's f4wA + cutwA walkers, its
# 100 cutwA draws, its cohort on BOTH substrates and every parent gate
# (CERT-F4, CERT-178, CERT-REW, CERT-SI, CERT-GEN, CERT-211, CERT-SIGEN,
# CERT-REWCUT, CERT-MENUCUT, CERT-WALKCUT, CERT-REBIND, CERT-FH) have ALL
# re-run as free certification before any L238 number is read.
# PREREG: l238/PREREG.md (registered first).
# Writes l238/static.json ONLY. Zero rollouts, zero settles, zero dynamics.
import os as _os238
import hashlib as _hl238
from fractions import Fraction as _Fr238

N_SLICE238 = 1916
o["design"] = (
    "L238 asks whether the ELEVEN realised first hops L220 counted on f4wA "
    "AND on cutwA are the SAME eleven targets. An edge-identity twin of the "
    "certified first-hop walker (gated node-by-node, CERT-FE) records, per "
    "substrate, which first-hop edges the certified shortest-path tree "
    "actually uses, their target global ids, T_L in bits and per-edge loads. "
    "Primary: Jaccard of the two realised target sets for the carrier. "
    "Nonselective companion: the same over the 31 cutwA-present actors with "
    "an exact size-matched overlap null and BH. Registered escape read "
    "first: is the funnel a property of the POOL geometry rather than of "
    "the carrier? PREREG l238/PREREG.md.")
o["prereg"] = "l238/PREREG.md"
with open("l238_static.py", "rb") as _bf:
    _lines238 = [next(_bf) for _ in range(N_SLICE238)]
o["banner"] = b"".join(_lines238[:13]).decode()
o["slice"] = dict(
    n_lines=N_SLICE238, source="l220_static.py lines 1-1916 VERBATIM",
    sha256=_hl238.sha256(b"".join(_lines238)).hexdigest())
PARENTS238 = ("l206/static.json", "l178/static.json", "l169c/static.json",
              "l211/static.json", "l220/static.json")
FP238 = {}
for _p in PARENTS238:
    _st = _os238.stat(_p)
    FP238[_p] = (int(_st.st_size), int(_st.st_mtime_ns))

log("=" * 72)
log("[L238] are the eleven realised first hops the SAME eleven targets on both "
    "substrates?")

# ---------------- CERT-220 (HALTING): the card's required anchor ------------
# The verbatim slice RECOMPUTED L211's and L220's whole measurement blocks
# into o[...]. Every leaf must equal l220/static.json by FLOAT EQUALITY, and
# the coverage bar is the stored file's OWN leaf count (never a guess).
_S220 = json.load(open("l220/static.json"))
_c220 = [0]


def _cmp220(a, b, path):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), (path, "dict keys",
                                                          sorted(set(a) ^ set(b)))
        for k in sorted(a):
            _cmp220(a[k], b[k], f"{path}/{k}")
        return
    if isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), (path, "list len")
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp220(x, y, f"{path}[{i}]")
        return
    if isinstance(a, float) or isinstance(b, float):
        assert float(a) == float(b), (path, repr(a), repr(b), "NOT float-equal")
    else:
        assert a == b, (path, repr(a), repr(b))
    _c220[0] += 1


def _nleaf(a):
    if isinstance(a, dict):
        return sum(_nleaf(v) for v in a.values())
    if isinstance(a, list):
        return sum(_nleaf(v) for v in a)
    return 1


_BLOCKS220 = ("L211_primary", "L211_cohort", "L220_primary", "L220_transport",
              "L220_cohort")
_BAR220 = sum(_nleaf(_S220[_b]) for _b in _BLOCKS220)
for _b in _BLOCKS220:
    _cmp220(o[_b], _S220[_b], _b)
assert _c220[0] == _BAR220, (_c220[0], _BAR220, "CERT-220 coverage (STOP)")
assert o["L220_primary"]["branch"] == _S220["L220_primary"]["branch"]
log(f"[CERT-220] GREEN {_c220[0]} stored L211 + L220 values (five blocks) "
    f"reproduced by FLOAT EQUALITY from my own re-run; coverage bar "
    f"{_BAR220} DERIVED from the stored file's own leaf count")

# ---------------- global ids, menus, pools ----------------------------------
_INF = float("inf")
_GID_F4 = np.where(keep_f4)[0]
_GID_CUT = np.where(keep_wA)[0]
assert _GID_F4.size == NL and _GID_CUT.size == SUB_CUT["n"]
assert int(_GID_F4[LC_CAR]) == GI_CARRIER and int(_GID_CUT[LC_CAR_CUT]) == GI_CARRIER
_TGT_F4 = list(_IX_F4["TGT0"])
assert _TGT_F4 == TGT0, "f4wA target list drift (STOP)"
assert _IX_F4["START"] == START and _IX_F4["END"] == END
assert _IX_F4["L_L"] == L_L and _IX_F4["T_L"] == T_L, "globals not on f4wA (STOP)"
_POOLG_F4 = _GID_F4[np.asarray(POOLS_IDX, np.int64)]
_POOLG_CUT = _GID_CUT[np.asarray(IX_CUT["POOLS_IDX"], np.int64)]
_COMMON_SET = set(_POOLG_F4.tolist()) & set(_POOLG_CUT.tolist())
_COMMON = sorted(_COMMON_SET)
_GI_OF = {}
for _nm, _lc in _src_all.items():
    if _nm == "carrier":
        _gi = GI_CARRIER
    elif _nm == "twin":
        _gi = GI_TWIN4
    elif _nm == "mirror_928":
        _gi = GI_MIRROR
    else:
        _gi = int(_nm.rsplit("_", 1)[1])
    _GI_OF[_nm] = _gi
    assert int(loc_f4[_gi]) == int(_lc), (_nm, "f4wA local index drift (STOP)")
_PRESENT = [_nm for _nm in _src_all
            if _nm != "mirror_928" and bool(keep_wA[_GI_OF[_nm]])]
_N_PRES = len(_PRESENT)
assert _N_PRES == (len(_src_all) - 1) - _S220["L220_cohort"]["n_absent_from_cutwA"], \
    (_N_PRES, "family width is not the stored 31 (STOP)")
assert _N_PRES == 31, (_N_PRES, "PREREG 0b width (STOP)")
assert sorted(_GI_OF[_nm] for _nm in _PRESENT)[0] >= 0 and "carrier" in _PRESENT
log(f"[L238] pools: f4wA {len(_POOLG_F4)} cutwA {len(_POOLG_CUT)} common "
    f"{len(_COMMON)} | actors {len(_src_all)} (mirror apart) | cutwA-present "
    f"non-mirror {_N_PRES} (stored absent {len(_absent)})")

# ---------------- the edge-identity twin of the certified walker ------------
def dijkstra_si_fe(src, tgt):
    """dijkstra_si_fh's relaxation, structure for structure, carrying the
    first-hop CSR EDGE INDEX beside the first-hop cost it is the cost OF.
    Not trusted: gated node-by-node against the certified walker (CERT-FE)."""
    dist = [_INF] * NL
    si = [_INF] * NL
    fh = [_INF] * NL
    hop = [0] * NL
    fe = [-1] * NL
    done = bytearray(NL)
    dist[src] = 0.0
    si[src] = 0.0
    fh[src] = 0.0
    h = [(0.0, src)]
    pop = heapq.heappop
    push = heapq.heappush
    while h:
        d, u = pop(h)
        if done[u]:
            continue
        done[u] = 1
        su = si[u]
        fu = fh[u]
        eu = fe[u]
        hu = hop[u]
        for e in range(START[u], END[u]):
            v = tgt[e]
            if done[v]:
                continue
            nd = d + L_L[e]
            if nd < dist[v]:
                dist[v] = nd
                si[v] = su + T_L[e]
                if u == src:
                    fh[v] = T_L[e]
                    fe[v] = e
                else:
                    fh[v] = fu
                    fe[v] = eu
                hop[v] = hu + 1
                push(h, (nd, v))
    return dist, si, fh, hop, fe


_nfe = [0]


def realised_edges(src, tgt, gid, pools_idx):
    """Realised first-hop EDGE SET of the certified shortest-path tree from
    src, with per-edge cost (T_L bits) and the pool cells it serves."""
    _d1, _s1, _f1, _h1 = dijkstra_si_fh(src, tgt)
    _d, _s, _f, _h, _fe = dijkstra_si_fe(src, tgt)
    for v in range(NL):                      # CERT-FE: EVERY node, not pools only
        assert _d[v] == _d1[v], (src, v, "CERT-FE dist (STOP)")
        assert _s[v] == _s1[v], (src, v, "CERT-FE si (STOP)")
        assert _f[v] == _f1[v], (src, v, "CERT-FE fh (STOP)")
        assert _h[v] == _h1[v], (src, v, "CERT-FE hop (STOP)")
        _nfe[0] += 4
        if v != src and _d[v] != _INF:
            assert START[src] <= _fe[v] < END[src], (src, v, "CERT-FE range (STOP)")
            assert _f[v] == T_L[_fe[v]], (src, v, "CERT-FE cost-of-edge (STOP)")
            _nfe[0] += 2
    serve = {}
    n_self = 0
    for i in pools_idx:
        if _d[i] != _INF:
            if _fe[i] < 0:
                assert i == src, (src, i, "reached pool cell with no first hop")
                n_self += 1
                continue
            serve.setdefault(_fe[i], []).append(i)
    _sm = fh_summary(_d1, _s1, _f1, _h1)
    _c_rec = len({round(_f[i], 12) for i in pools_idx if _d[i] != _INF})
    edges = [dict(e=int(e), gi_tgt=int(gid[tgt[e]]), tl=float(T_L[e]),
                  cells=sorted(int(gid[i]) for i in cells),
                  hops=float(np.mean([_h[i] for i in cells])))
             for e, cells in sorted(serve.items())]
    _c_cert = 0 if _sm is None else int(_sm["n_distinct_first_hops"])
    assert _c_rec == _c_cert, (src, _c_rec, _c_cert, "CERT-COST (STOP)")
    return dict(summary=_sm, edges=edges, n_self=n_self,
                c_cert=_c_cert, c_rec=_c_rec, r=len(edges))


def _menu(gi, emask):
    return set(int(x) for x in np.unique(dst_all[emask & (src_all == gi)]))


def _collect(tgt, gid, pools_idx, emask):
    out = {}
    for _nm in _src_all:
        _gi = _GI_OF[_nm]
        _lc = int(SUB_CUT["loc"][_gi]) if emask is emask_wA else int(loc_f4[_gi])
        if _lc < 0 or not bool((keep_wA if emask is emask_wA else keep_f4)[_gi]):
            out[_nm] = None
            continue
        _r = realised_edges(_lc, tgt, gid, pools_idx)
        _m = _menu(_gi, emask)
        for _e in _r["edges"]:
            assert _e["gi_tgt"] in _m, (_nm, "realised edge outside its menu")
        _r["menu"] = _m
        _r["n_out"] = len(_m)
        out[_nm] = _r
    return out


# f4wA: the globals are on f4wA (L220's RESTORE + CERT-REBIND ran in the slice)
R4 = _collect(_TGT_F4, _GID_F4, POOLS_IDX, emask_f4)
_nfe_f4 = _nfe[0]
# cutwA: rebind exactly as L220 did, collect, restore, and prove nothing leaked
START, END, L_L, T_L = (IX_CUT["START"], IX_CUT["END"],
                        IX_CUT["L_L"], IX_CUT["T_L"])
NL, POOLS_IDX, N_POOL = IX_CUT["NL"], IX_CUT["POOLS_IDX"], IX_CUT["N_POOL"]
RC = _collect(TGT0_CUT, _GID_CUT, IX_CUT["POOLS_IDX"], emask_wA)
_nfe_cut = _nfe[0] - _nfe_f4
START, END, L_L, T_L = _START0, _END0, _L0, _T0
NL, N_POOL, POOLS_IDX = _NL0, _NP0, _PI0
_d3, _s3 = dijkstra_si(LC_CAR, TGT0)
_nreb238 = 0
for _j, _i in enumerate(POOLS_IDX):
    assert _d3[_i] == _ref_pool[_j][0], (_i, "REBIND-238 leaked dist (STOP)")
    assert _s3[_i] == _ref_pool[_j][1], (_i, "REBIND-238 leaked si (STOP)")
    _nreb238 += 2
log(f"[CERT-FE] GREEN {_nfe[0]} EXACT equalities (dist/si/fh/hop on EVERY node "
    f"+ range + cost-of-edge): identity walker == certified walker, "
    f"{len(_src_all)} actors x 2 substrates (f4wA {_nfe_f4}, cutwA {_nfe_cut})")
log(f"[CERT-COST] GREEN {2 * len(_src_all)} recomputed cost counts == certified "
    f"| [CERT-REBIND-238] GREEN {_nreb238}")


# ---------------- statistics (self-tested before use) ----------------------
def hyper_sf(k, N, K, n):
    """P(X >= k), X ~ Hypergeom(N, K, n). Exact rational arithmetic."""
    assert 0 <= K <= N and 0 <= n <= N, (N, K, n)
    if k <= 0:
        return 1.0
    hi = min(K, n)
    if k > hi:
        return 0.0
    _num = sum(math.comb(K, x) * math.comb(N - K, n - x) for x in range(k, hi + 1))
    return float(_Fr238(_num, math.comb(N, n)))


def midrank(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="stable")
    r = np.empty(x.size, float)
    xs = x[order]
    i = 0
    while i < x.size:
        j = i
        while j + 1 < x.size and xs[j + 1] == xs[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spear(x, y):
    """Midrank Spearman; UNMEASURABLE (None) below 3 distinct values a side."""
    if len(x) < 3:
        return None, len(set(x)), len(set(y))
    dx, dy = len(set(x)), len(set(y))
    if dx < 3 or dy < 3:
        return None, dx, dy
    return float(np.corrcoef(midrank(x), midrank(y))[0, 1]), dx, dy


# CERT-STAT (HALTING): the instruments are checked on closed forms first
assert hyper_sf(0, 80, 11, 11) == 1.0 and hyper_sf(12, 80, 11, 11) == 0.0
assert hyper_sf(11, 80, 11, 11) == 1.0 / math.comb(80, 11), "hyper perfect-overlap"
for _kk in (0, 1, 5, 10, 11):
    _pmf = (math.comb(11, _kk) * math.comb(69, 11 - _kk)
            / _Fr238(math.comb(80, 11)))
    assert abs((hyper_sf(_kk, 80, 11, 11) - hyper_sf(_kk + 1, 80, 11, 11))
               - float(_pmf)) < 1e-15, (_kk, "hyper tail/pmf mismatch")
assert midrank(np.array([1.0, 1.0, 2.0])).tolist() == [1.5, 1.5, 3.0], "midrank ties"
assert midrank(np.array([3.0, 1.0, 4.0, 1.0, 5.0])).tolist() == [3.0, 1.5, 4.0, 1.5, 5.0]
assert abs(spear([1, 2, 3, 4], [1, 2, 3, 4])[0] - 1.0) < 1e-12
assert abs(spear([1, 2, 3, 4], [4, 3, 2, 1])[0] + 1.0) < 1e-12
assert spear([1, 1, 1, 2], [1, 2, 3, 4])[0] is None, "tie gate"
log("[CERT-STAT] GREEN: hypergeometric tail == closed forms (5 pmf terms + "
    "floor + perfect overlap), midrank tie convention, Spearman +-1, tie gate")


def bh_exact(pvals, m):
    """Benjamini-Hochberg with the family width m FIXED at the derived 31
    (unmeasurable actors keep their width: conservative). Returns
    (n_rejected, q-values in input order, ranks 1-based in input order)."""
    pv = list(pvals)
    k = len(pv)
    order = sorted(range(k), key=lambda i: (pv[i], i))
    ps = [pv[i] for i in order]
    passed = [ps[i] <= 0.05 * (i + 1) / m for i in range(k)]
    nrej = 0
    for i in range(k - 1, -1, -1):
        if passed[i]:
            nrej = i + 1
            break
    raw = [min(1.0, ps[i] * m / (i + 1)) for i in range(k)]
    for i in range(k - 2, -1, -1):
        raw[i] = min(raw[i], raw[i + 1])
    qv = [None] * k
    rank = [0] * k
    for i, idx in enumerate(order):
        qv[idx] = raw[i]
        rank[idx] = i + 1
    return nrej, qv, rank


# BH self-test: a known 3-member family
_t = bh_exact([0.01, 0.03, 0.06], 3.0)
assert _t[0] == 2, _t                                        # step-up stops at rank 2
assert all(abs(_t[1][i] - v) < 1e-12 for i, v in enumerate([0.03, 0.045, 0.06])), _t
assert _t[2] == [1, 2, 3], _t
assert bh_exact([0.01, 0.03, 0.06], 4.0)[0] == 1, "a wider family must reject less"
log("[CERT-BH] GREEN: step-up count, monotone q-values, width sensitivity")

# ---------------- per-actor cross-substrate table ---------------------------
PER = {}
for _nm in _src_all:
    _a, _b = R4[_nm], RC[_nm]
    _rec = dict(gi=_GI_OF[_nm], present_cutwA=bool(keep_wA[_GI_OF[_nm]]),
                in_family=(_nm != "mirror_928"))

    def _side(r, gid, tag):
        if r is None:
            return None
        _s = dict(n_out=r["n_out"], r=r["r"], c=r["c_cert"],
                  n_reach=(0 if r["summary"] is None else r["summary"]["n_reach"]),
                  n_self=r["n_self"],
                  hop_mean=(None if r["summary"] is None else r["summary"]["hop_mean"]),
                  top1_gi=(max(r["edges"], key=lambda e: len(e["cells"]))["gi_tgt"]
                           if r["edges"] else None),
                  top1_load=(max(len(e["cells"]) for e in r["edges"])
                             if r["edges"] else 0),
                  edges=[dict(gi_tgt=e["gi_tgt"], tl=e["tl"], load=len(e["cells"]),
                              loadC=sum(1 for g in e["cells"] if g in _COMMON_SET),
                              hops=e["hops"]) for e in r["edges"]])
        assert _s["r"] >= _s["c"] >= 0, (tag, "edges must outnumber costs")
        assert sum(e["load"] for e in _s["edges"]) + _s["n_self"] == _s["n_reach"], \
            (tag, "loads do not partition the reached pool cells")
        return _s

    _rec["f4"] = _side(_a, _GID_F4, "f4wA")
    _rec["cut"] = _side(_b, _GID_CUT, "cutwA")
    _x = dict(measurable=False)
    if _rec["f4"] is not None and _rec["cut"] is not None:
        _A = {e["gi_tgt"]: e for e in _rec["f4"]["edges"]}
        _B = {e["gi_tgt"]: e for e in _rec["cut"]["edges"]}
        _i = set(_A) & set(_B)
        _u = set(_A) | set(_B)
        _x.update(r_f4=len(_A), r_cut=len(_B), k=len(_i))
        if _u:
            _N = len(_a["menu"] | _b["menu"])
            _K, _n = len(_a["menu"]), len(_b["menu"])
            _x.update(
                measurable=True, J=len(_i) / len(_u), N=_N, K=_K, n=_n,
                contain_f4=len(_i) / len(_A), contain_cut=len(_i) / len(_B),
                p=hyper_sf(len(_i), _N, _K, _n),
                p_floor=hyper_sf(min(_K, _n), _N, _K, _n),
                only_f4=len(set(_A) - set(_B)), only_cut=len(set(_B) - set(_A)),
                rhoC=spear([_A[g]["loadC"] for g in sorted(_i)],
                           [_B[g]["loadC"] for g in sorted(_i)]),
                rhoU=spear([(_A[g]["loadC"] if g in _A else 0) for g in sorted(_u)],
                           [(_B[g]["loadC"] if g in _B else 0) for g in sorted(_u)]),
                rho_tl=spear([_A[g]["tl"] for g in sorted(_i)],
                             [_B[g]["tl"] for g in sorted(_i)]))
            _x["common_cells_f4"] = sum(e["loadC"] for e in _rec["f4"]["edges"])
            _x["common_cells_cut"] = sum(e["loadC"] for e in _rec["cut"]["edges"])
    _rec["cross"] = _x
    PER[_nm] = _rec


def _rho(t):
    """(value, measurable, distinct a, distinct b) -> JSON-friendly."""
    if t is None:
        return dict(value=None, measurable=False)
    v, dx, dy = t
    return dict(value=v, measurable=(v is not None), n_distinct_a=dx, n_distinct_b=dy)


for _nm in PER:
    for _key in ("rhoC", "rhoU", "rho_tl"):
        if _key in PER[_nm]["cross"]:
            PER[_nm]["cross"][_key] = _rho(PER[_nm]["cross"][_key])
PER_car = PER["carrier"]["cross"]
assert PER_car["measurable"], "carrier unmeasurable on a substrate (STOP)"

# ---------------- the primary (the carrier) ----------------------------------
_J = PER_car["J"]
if _J >= 0.70:
    BR238 = "SAME_SET"
elif _J <= 0.30:
    BR238 = "SAME_COUNT_DIFFERENT_SET"
else:
    BR238 = "PARTIAL"
log(f"[L238] carrier: r_f4 {PER_car['r_f4']} (costs {PER['carrier']['f4']['c']}) "
    f"r_cut {PER_car['r_cut']} (costs {PER['carrier']['cut']['c']}) overlap "
    f"{PER_car['k']} -> J {_J:.4f} = {BR238} | contain f4 "
    f"{PER_car['contain_f4']:.3f} cut {PER_car['contain_cut']:.3f} | only f4 "
    f"{PER_car['only_f4']} only cut {PER_car['only_cut']} | N {PER_car['N']} "
    f"K {PER_car['K']} n {PER_car['n']} p {PER_car['p']:.3e} (floor "
    f"{PER_car['p_floor']:.3e}) | rhoC {PER_car['rhoC']} rhoU {PER_car['rhoU']}")
for _tag in ("f4", "cut"):
    _es = sorted(PER["carrier"][_tag]["edges"], key=lambda e: -e["load"])
    log(f"[L238] carrier {_tag}: menu {PER['carrier'][_tag]['n_out']} reach "
        f"{PER['carrier'][_tag]['n_reach']} top " + " ".join(
            f"{e['gi_tgt']}:{e['load']}" for e in _es[:12]))

# ---------------- the registered escape, read FIRST -------------------------
# an actor unmeasurable on either substrate keeps its WIDTH in the family
# (m stays 31) but cannot be ranked or vote in the escape
_MEAS = [_nm for _nm in _PRESENT if PER[_nm]["cross"]["measurable"]]
_N_UNM = _N_PRES - len(_MEAS)
assert len(_MEAS) >= 1, "no actor measurable on both substrates (STOP)"
_r4v = np.array([PER[_nm]["cross"]["r_f4"] for _nm in _MEAS], float)
_no = np.array([PER[_nm]["f4"]["n_out"] for _nm in _MEAS], float)
_e1 = bool(np.median(_r4v) <= 15.0)
_e2 = bool(np.mean((_r4v >= 8) & (_r4v <= 14)) >= 0.50)
_sp_e = spear(_r4v.tolist(), _no.tolist())
_e3 = (None if _sp_e[0] is None else bool(_sp_e[0] < 0.50))
if _N_UNM:
    ESC238 = "E_UNDECIDED"                       # the family is not whole
elif _e1 and _e2 and _e3 is True:
    ESC238 = "E_POOL"
elif _e3 is None and _e1 and _e2:
    ESC238 = "E_UNDECIDED"                       # clause e3 unmeasurable
else:
    ESC238 = "E_ACTOR_SPECIFIC"
log(f"[L238] escape over {len(_MEAS)} of {_N_PRES}: median r_f4 "
    f"{float(np.median(_r4v)):.1f} (e1 {_e1}: <=15) | frac in [8,14] "
    f"{float(np.mean((_r4v >= 8) & (_r4v <= 14))):.3f} (e2 {_e2}: >=.50) | "
    f"Spearman(r_f4, n_out) {_sp_e[0]} (e3 {_e3}: <.50) -> {ESC238}")

# ---------------- the nonselective companion (BH, m = 31) -------------------
_pv = [PER[_nm]["cross"]["p"] for _nm in _MEAS]
_nrej, _qv, _rk = bh_exact(_pv, float(_N_PRES))
for _nm, _q, _r in zip(_MEAS, _qv, _rk):
    PER[_nm]["cross"]["q"] = _q
    PER[_nm]["cross"]["p_rank"] = _r
_Jv = np.array([PER[_nm]["cross"]["J"] for _nm in _MEAS], float)
_bands = dict(SAME_SET=int(np.sum(_Jv >= 0.70)),
              PARTIAL=int(np.sum((_Jv > 0.30) & (_Jv < 0.70))),
              SAME_COUNT_DIFFERENT_SET=int(np.sum(_Jv <= 0.30)))
o["L238_family"] = dict(
    m=_N_PRES, q=0.05,
    note=("m is the DERIVED width 31 and is held fixed for every actor "
          "(PREREG 0b); the mirror is tabulated apart. The per-actor p is a "
          "size-matched SET-OVERLAP null (PREREG 0h), not a wiring null."),
    median_J=float(np.median(_Jv)), min_J=float(_Jv.min()), max_J=float(_Jv.max()),
    n_measurable=int(_Jv.size), n_unmeasurable=int(_N_UNM), bands=_bands,
    n_bh_rejected=int(_nrej),
    rejected=[_nm for _nm in _MEAS if PER[_nm]["cross"]["q"] <= 0.05],
    min_p=float(min(_pv)),
    n_at_p_floor=int(sum(1 for _nm in _MEAS
                         if PER[_nm]["cross"]["p"] == PER[_nm]["cross"]["p_floor"])),
    spearman_J_vs_r_f4=_rho(spear(_Jv.tolist(), _r4v.tolist())),
    spearman_J_vs_n_out=_rho(spear(_Jv.tolist(), _no.tolist())),
    median_k=float(np.median([PER[_nm]["cross"]["k"] for _nm in _MEAS])),
    median_r_f4=float(np.median(_r4v)),
    median_r_cut=float(np.median([PER[_nm]["cross"]["r_cut"] for _nm in _MEAS])),
    median_n_out_f4=float(np.median(_no)),
    median_n_out_cut=float(np.median([PER[_nm]["cut"]["n_out"] for _nm in _MEAS])),
    n_r_equal=int(sum(1 for _nm in _MEAS
                      if PER[_nm]["cross"]["r_f4"] == PER[_nm]["cross"]["r_cut"])),
    n_identity_equals_cost_both=int(sum(
        1 for _nm in _MEAS
        if PER[_nm]["f4"]["r"] == PER[_nm]["f4"]["c"]
        and PER[_nm]["cut"]["r"] == PER[_nm]["cut"]["c"])),
    carrier_q=PER["carrier"]["cross"]["q"], carrier_p_rank=PER["carrier"]["cross"]["p_rank"],
    carrier_J_percentile=float(np.mean(_Jv <= _J)))
o["L238_escape"] = dict(
    branch=ESC238, e1_median_r_f4_le_15=dict(value=bool(_e1),
                                             median=float(np.median(_r4v))),
    e2_frac_in_8_14_ge_half=dict(value=bool(_e2),
                                 frac=float(np.mean((_r4v >= 8) & (_r4v <= 14)))),
    e3_spearman_r_vs_n_out_lt_half=dict(value=_e3, stat=_rho(_sp_e)),
    per_actor={_nm: dict(r_f4=PER[_nm]["cross"]["r_f4"], n_out_f4=PER[_nm]["f4"]["n_out"])
               for _nm in _MEAS}, n_unmeasurable=int(_N_UNM))
o["L238_primary"] = dict(
    branch=BR238, J=_J, k=PER_car["k"], r_f4=PER_car["r_f4"], r_cut=PER_car["r_cut"],
    c_f4=PER["carrier"]["f4"]["c"], c_cut=PER["carrier"]["cut"]["c"],
    n_out_f4=PER_car["K"], n_out_cut=PER_car["n"], N_menu_union=PER_car["N"],
    contain_f4=PER_car["contain_f4"], contain_cut=PER_car["contain_cut"],
    only_f4=PER_car["only_f4"], only_cut=PER_car["only_cut"],
    p=PER_car["p"], p_floor=PER_car["p_floor"],
    rhoC=PER_car["rhoC"], rhoU=PER_car["rhoU"], rho_tl_rank=PER_car["rho_tl"],
    common_pool_cells=dict(f4wA=PER_car["common_cells_f4"],
                           cutwA=PER_car["common_cells_cut"], n=len(_COMMON)),
    bars=dict(SAME_SET=0.70, SAME_COUNT_DIFFERENT_SET=0.30),
    note=("T_L in bits is per-substrate (PREREG 0d); 'realised' = used by the "
          "certified shortest-path tree under strict-< relaxation and heap "
          "order (PREREG 0g)."))
o["L238_pools"] = dict(n_f4wA=int(len(_POOLG_F4)), n_cutwA=int(len(_POOLG_CUT)),
                       n_common=len(_COMMON))
o["L238_carrier_edges"] = dict(
    f4wA=PER["carrier"]["f4"]["edges"], cutwA=PER["carrier"]["cut"]["edges"])
o["L238_per_actor"] = PER
o["L238_mirror"] = dict(
    gi=GI_MIRROR, cross=PER["mirror_928"]["cross"],
    r_f4=(None if PER["mirror_928"]["f4"] is None else PER["mirror_928"]["f4"]["r"]),
    r_cut=(None if PER["mirror_928"]["cut"] is None else PER["mirror_928"]["cut"]["r"]))
log(f"[L238] family (m {_N_PRES}): median J {float(np.median(_Jv)):.4f} "
    f"[{float(_Jv.min()):.3f}, {float(_Jv.max()):.3f}] bands {_bands} | BH "
    f"rejected {_nrej} of {_Jv.size} measurable (m {_N_PRES}; min p {min(_pv):.3e}, "
    f"carrier q "
    f"{PER['carrier']['cross']['q']:.4f} rank {PER['carrier']['cross']['p_rank']}) "
    f"| identity==cost on BOTH substrates for "
    f"{o['L238_family']['n_identity_equals_cost_both']} of {_Jv.size} | r_f4 == "
    f"r_cut for {o['L238_family']['n_r_equal']}")

# ---------------- predictions, scored ---------------------------------------
P = {}
P["P1_carrier_SAME_SET"] = dict(
    registered="carrier branch SAME_SET (J >= 0.70)",
    measured=f"J {_J:.4f} = {BR238}", correct=bool(BR238 == "SAME_SET"))
P["P2_family_median_J_ge_070"] = dict(
    registered="cohort median J over actors measurable on both >= 0.70",
    measured=f"median J {float(np.median(_Jv)):.4f} over {_Jv.size}",
    correct=bool(float(np.median(_Jv)) >= 0.70))
P["P3_E_POOL_fires"] = dict(
    registered="E_POOL fires (e1 median r_f4 <= 15 AND e2 frac in [8,14] >= .50 "
               "AND e3 Spearman(r_f4, n_out) < .50; E_UNDECIDED scores FALSE)",
    measured=ESC238, correct=bool(ESC238 == "E_POOL"))
P["P4_identity_equals_cost_11_both"] = dict(
    registered="r_f4 == c_f4 == 11 AND r_cut == c_cut == 11 for the carrier",
    measured=(f"r_f4 {PER_car['r_f4']} c_f4 {PER['carrier']['f4']['c']} | r_cut "
              f"{PER_car['r_cut']} c_cut {PER['carrier']['cut']['c']}"),
    correct=bool(PER_car["r_f4"] == PER["carrier"]["f4"]["c"] == 11
                 and PER_car["r_cut"] == PER["carrier"]["cut"]["c"] == 11))
_rc = PER_car["rhoC"]
P["P5_carrier_rhoC_ge_070_measurable"] = dict(
    registered="carrier rhoC >= 0.70 and MEASURABLE (>= 3 distinct loads a side)",
    measured=(f"rhoC {_rc['value']} measurable {_rc['measurable']} over "
              f"{PER_car['k']} shared first hops"),
    correct=bool(_rc["measurable"] and _rc["value"] >= 0.70))
o["predictions"] = P
o["predictions_score"] = f"{sum(1 for v in P.values() if v['correct'])} of {len(P)}"
o["false_predictions"] = [k for k, v in P.items() if not v["correct"]]

# ---------------- fingerprints, certification, limits, pins -----------------
for _p in PARENTS238:
    _st = _os238.stat(_p)
    assert FP238[_p] == (int(_st.st_size), int(_st.st_mtime_ns)), (_p, "PARENT MOVED (STOP)")
o["certification"] = dict(
    all_green=True,
    CERT_SLICE=f"l238_static.py 1-{N_SLICE238} == l220_static.py 1-{N_SLICE238} "
               f"(byte-identical, asserted by l238_build.py; sha256 "
               f"{o['slice']['sha256'][:16]})",
    CERT_220=f"{_c220[0]} stored L211+L220 leaves at float equality, bar "
             f"{_BAR220} derived from the stored file",
    CERT_FE=int(_nfe[0]), CERT_COST=int(2 * len(_src_all)),
    CERT_REBIND_238=int(_nreb238), CERT_STAT="closed forms",
    free_in_slice="CERT-F4, CERT-178, CERT-REW, CERT-SI, CERT-GEN, CERT-211, "
                  "CERT-SIGEN, CERT-REWCUT, CERT-MENUCUT, CERT-WALKCUT, "
                  "CERT-REBIND, CERT-FH",
    fingerprints=dict(FP238), n_actors=len(_src_all), n_family=_N_PRES)
o["limitations"] = [
    "ONE operator family (anatomical |W_beta|), ONE routing convention: "
    "'realised' = used by the certified shortest-path tree under strict-< "
    "relaxation and heap order (PREREG 0g); equal-length alternative first "
    "hops are not counted.",
    "the two substrates share their edge weights up to the eigenvector and "
    "route by L-lengths, so similar realised sets are the mechanically "
    "expected outcome (PREREG 0i): a high Jaccard is a TRANSPORT statement "
    "about the metric, never evidence that the carrier is special.",
    "the per-actor p is a size-matched SET-OVERLAP null (PREREG 0h), not a "
    "wiring null: the L220 draws swap the carrier's edges and are a null for "
    "no other source (L211's limitation, inherited verbatim).",
    "E_POOL's three thresholds were fixed in the PREREG before measurement "
    "and are the card's prose made checkable, not a calibrated instrument.",
    "Jaccard is a symmetric overlap bar (L221): directed containment "
    "fractions are reported beside it as companions.",
    "static, zero rollouts: nothing here is a dynamics claim.",
]
o["pins"] = "ALL GREEN"
json.dump(o, open("l238/static.json", "w"), indent=1)
log("=" * 72)
log(f"L238 DONE {time.time()-t0:.0f}s | carrier {BR238} J {_J:.4f} "
    f"(r {PER_car['r_f4']}/{PER_car['r_cut']}, k {PER_car['k']}) | escape "
    f"{ESC238} | family median J {float(np.median(_Jv)):.4f} BH {_nrej}/"
    f"{_N_PRES} | CERT-220 {_c220[0]}/{_BAR220} + FE {_nfe[0]} + COST "
    f"{2 * len(_src_all)} + REBIND {_nreb238} | predictions {o['predictions_score']}"
    f" (FALSE: {o['false_predictions']})")
