# ===================== L239 TAIL (appended by l239_build.py) =====================
# Everything above this line is VERBATIM l220_static.py lines 1-1587 (see
# l239_build.py): the nine certified slices of the L151 -> L178 -> L206 -> L207
# -> L211 chain AND L220's body up to the end of its cutwA build (IX_CUT). So
# every parent gate up to CERT-211 / CERT-SIGEN / CERT-GEN re-ran as free
# certification before any L239 number is read. L220's own cutwA draws / null /
# cohort (its lines 1588-1916) are NOT in the slice: the blocks below re-run
# them VERBATIM (the carrier leg, re-gated against l220/static.json) and then
# EXTEND the certified null to a second source — the matched twin.
# PREREG: l239/PREREG.md (rule + branches frozen BEFORE the selection code
# below was written or run). Static: zero rollouts, zero settles, zero
# dynamics. Writes l239/static.json ONLY.
import ast as _ast239
import hashlib as _hl239
import os as _os239

N_SLICE239 = 1587
with open("l239_static.py") as _bf239:
    _me239 = _bf239.readlines()
with open("l220_static.py") as _pf239:
    _par239 = _pf239.readlines()
with open("l220/static.json") as _sf239:
    S220 = json.load(_sf239)


def _leafcnt239(x):
    if isinstance(x, dict):
        return sum(_leafcnt239(v) for v in x.values())
    if isinstance(x, list):
        return sum(_leafcnt239(v) for v in x)
    return 1


FP239 = {}
for _p, _k in (("l220/static.json", "l220"), ("l220_static.py", "l220s"),
               ("l220_tail.py", "l220t"), ("l220/PREREG.md", "l220p")):
    _st = _os239.stat(_p)
    FP239[_k] = (int(_st.st_size), int(_st.st_mtime_ns))


def _astaudit239(src):
    """(keys assigned as `o["k"] = ...`, write sites) by AST — never a token
    scan (L226/L227). A write site = open() with a w/a/+ mode, or a call to
    .dump/.save/.savez/.write_text/.write_bytes/.makedirs/.mkdir/.to_csv."""
    _ks, _wr = set(), []
    for _n in _ast239.walk(_ast239.parse(src)):
        if isinstance(_n, _ast239.Assign) and len(_n.targets) == 1:
            _tg = _n.targets[0]
            if (isinstance(_tg, _ast239.Subscript)
                    and isinstance(_tg.value, _ast239.Name)
                    and _tg.value.id == "o"
                    and isinstance(_tg.slice, _ast239.Constant)
                    and isinstance(_tg.slice.value, str)):
                _ks.add(_tg.slice.value)
        if isinstance(_n, _ast239.Call) and isinstance(_n.func, _ast239.Name) \
                and _n.func.id == "open" and len(_n.args) >= 2 \
                and isinstance(_n.args[1], _ast239.Constant) \
                and isinstance(_n.args[1].value, str) \
                and any(_c in _n.args[1].value for _c in "wa+"):
            _wr.append((_n.lineno, "open"))
        if isinstance(_n, _ast239.Call) \
                and isinstance(_n.func, _ast239.Attribute) \
                and _n.func.attr in ("dump", "save", "savez", "write_text",
                                     "write_bytes", "makedirs", "mkdir",
                                     "to_csv"):
            _wr.append((_n.lineno, _n.func.attr))
    return _ks, _wr


# ---- PARENT PIN (HALTING) ---------------------------------------------------
# 1 the parent artifact carries the parent's own 13-line banner;
# 2 that banner records the sha of l220_tail.py, that file is a literal SUFFIX
#   of the parent, and it owns the whole region this card cuts away;
# 3 this script's head IS the parent's lines 1-1587, byte-for-byte.
assert len(_par239) == 2007, (len(_par239), "parent line count (STOP)")
assert "".join(_par239[:13]) == S220["banner"], "PARENT PIN 1 (STOP)"
_ptb239 = open("l220_tail.py", "rb").read()
_ptsha239 = _hl239.sha256(_ptb239).hexdigest()[:16]
_bl239 = [_l for _l in S220["banner"].split("\n") if "l220_tail.py" in _l]
assert len(_bl239) == 1 and f"sha256 {_ptsha239}" in _bl239[0], \
    (_bl239, _ptsha239, "PARENT PIN 2 (STOP)")
assert _ptb239.endswith(b"\n"), "PARENT PIN 2 (STOP)"
assert open("l220_static.py", "rb").read().endswith(_ptb239), \
    "PARENT PIN 2b: l220_tail.py is not a literal SUFFIX (STOP)"
assert len(_par239) - _ptb239.count(b"\n") + 1 <= N_SLICE239 + 1, \
    "PARENT PIN 2c: the cut region leaves the parent's tail (STOP)"
assert _me239[:N_SLICE239] == _par239[:N_SLICE239], "PARENT PIN 3 (STOP)"
assert _par239[N_SLICE239] == "\n" and _par239[N_SLICE239 + 1].startswith(
    "# ---------------- global edge -> cutwA CSR"), "cut boundary (STOP)"

# ---- SLICE / WRITE-SITE audit (HALTING, structural) -------------------------
_sl_src239 = "".join(_me239[:N_SLICE239])
_cut_src239 = "".join(_par239[N_SLICE239:])
_tail_src239 = "".join(_me239[N_SLICE239:])
_k_slice, _w_slice = _astaudit239(_sl_src239)
_k_cut, _w_cut = _astaudit239(_cut_src239)
_k_tail, _w_tail = _astaudit239(_tail_src239)
assert not _w_slice, (_w_slice, "the slice must be write-free (STOP)")
assert not (_k_slice & _k_cut), sorted(_k_slice & _k_cut)
assert (_k_slice | _k_cut) == set(S220), (
    sorted(set(S220) ^ (_k_slice | _k_cut)), "stored keys vs code (STOP)")
assert {"L220_primary", "L220_transport", "L220_cohort", "predictions",
        "predictions_score", "certification", "limitations",
        "pins"} <= _k_cut, "the cut region does not own L220's writer keys"
assert sorted(a for _, a in _w_cut) == ["dump", "open"], _w_cut
assert (_k_tail & set(S220)) == {"design", "prereg", "certification", "limitations",
                                 "pins"}, \
    sorted(_k_tail & set(S220))  # the per-card keys, overwritten only AFTER every compare
assert sorted(a for _, a in _w_tail) == ["dump", "makedirs", "open"], _w_tail
assert len(_w_slice) + len(_w_tail) == len(_astaudit239(
    "".join(_me239))[1]), "a write site sits on a block boundary (STOP)"
log(f"[PARENT PIN] GREEN: l220_static.py {len(_par239)} lines, tail sha "
    f"{_ptsha239} = literal suffix; slice = lines 1-{N_SLICE239}; "
    f"{len(_k_slice)} keys assigned by the slice, "
    f"{len(_k_cut)} by the cut; ONE write in the cut, "
    f"{len(_w_tail)} in this tail (makedirs + json.dump)")

# ---- CERT-239A (HALTING): every leaf the slice assigns, FLOAT EQUALITY ------
# against l220/static.json, on a coverage bar DERIVED from the artifact's own
# leaf count (L224/L234), with its floor derived from three core blocks.
_n239a, _l239a = 0, 0
for _k in sorted(_k_slice):
    _l239a += _leafcnt239(S220[_k])
    _cmp_leaf(o[_k], S220[_k], _k)
    _n239a += _leafcnt239(S220[_k])
_floor239 = sum(_leafcnt239(S220[k])
                for k in ("L211_primary", "L211_cohort", "G2_search_information"))
assert _n239a == _l239a and _n239a >= _floor239, \
    (_n239a, _l239a, _floor239, "CERT-239A (STOP)")
log(f"[CERT-239A] GREEN {_n239a} leaves of l220/static.json over "
    f"{len(_k_slice)} slice keys reproduced at FLOAT EQUALITY (artifact-derived "
    f"bar {_l239a}, floor {_floor239})")

o["design"] = (
    "L239 selects a matched twin for the carrier gi 1110 ON the base unfloored "
    "cutwA substrate (the f4 twin gi 290 is absent there) by a rule derived "
    "from cutwA's own out-degree and out-mass distributions, then reads the "
    "twin's within-source first-hop share against the carrier, the bilateral "
    "homolog and the L211 family. PRIMARY: G = |fh_share_of_si(twin) - "
    "fh_share_of_si(carrier)| vs the stored homolog gap and the family's "
    "median distance from the carrier. SECONDARY: the twin's own 100-draw "
    "degree-neutral destination-swap decomposition (the certified null "
    "extended to a second source by a parameterised kernel admitted only by "
    "exact agreement with the certified one). PREREG l239/PREREG.md.")
o["prereg"] = "l239/PREREG.md"
o["banner_l239"] = "".join(_me239[N_SLICE239:N_SLICE239 + 10])
o["slice_l239"] = dict(
    head="l220_static.py lines 1-1587 VERBATIM (literal prefix)",
    n_lines=N_SLICE239,
    sha256_16=_hl239.sha256(_sl_src239.encode()).hexdigest()[:16],
    cut_sha256_16=_hl239.sha256(_cut_src239.encode()).hexdigest()[:16],
    static_sha256_16=_hl239.sha256("".join(_me239).encode()).hexdigest()[:16],
    parent_static_sha256_16=_hl239.sha256(
        "".join(_par239).encode()).hexdigest()[:16],
    keys_assigned_by_slice=sorted(_k_slice),
    keys_assigned_by_cut=sorted(_k_cut),
    verbatim_blocks=dict(
        edge_maps="l220_static.py 1590-1603",
        rewcut="l220_static.py 1609-1627",
        ch_body="l220_static.py 1631-1645 as a function body (+1 indent)",
        carrier_and_null="l220_static.py 1648-1707",
        cohort="l220_static.py 1710-1725",
        l220_cohort="l220_static.py 1875-1880 + 1882-1910 (target renamed)",
        decomposition="l220_static.py 1742-1813 as a function body (+1 "
                     "indent), ONE token changed: the assignment target",
        restore="l220_static.py 1728-1729"))

#@@EDGE_MAPS@@

#@@REWCUT@@

# ---------------- the kernel (PREREG 0a): source-parameterised --------------
# rewire_draws is mask-generic but NOT source-generic: GI_CARRIER is hard-coded
# in it five times. Below is its body with every GI_CARRIER replaced by the
# argument `gi` and NOTHING else. It is admitted only by CERT-239K.
def rewire_draws_src(emask_block, carrier_rows_sel, n_draws, seed, Tmask, Mmask, gi):
    blk = emask_block
    pool_rows = np.where(blk & (src_all != gi))[0]
    car_rows = np.where(carrier_rows_sel)[0]
    base_pairs = set(zip(src_all[np.where(blk)[0]].tolist(),
                         dst_all[np.where(blk)[0]].tolist()))
    car_vals = np.abs(vals_all[car_rows])
    rng = np.random.default_rng(seed)
    out_draws = []
    for d in range(n_draws):
        cdst = dst_all[car_rows].copy()
        pdst = {}
        added, removed = set(), set()

        def present(p):
            return (p in base_pairs and p not in removed) or p in added

        def do_remove(p):
            if p in added:
                added.discard(p)
            else:
                removed.add(p)

        def do_add(p):
            if p in removed:
                removed.discard(p)
            else:
                added.add(p)

        nrel = 0
        for i in range(len(car_rows)):
            for _ in range(20):
                j = int(pool_rows[rng.integers(len(pool_rows))])
                sf = int(src_all[j])
                df = int(pdst.get(j, dst_all[j]))
                de = int(cdst[i])
                if sf == gi or df == de or df == gi or de == sf:
                    continue
                if present((gi, df)) or present((sf, de)):
                    continue
                do_remove((gi, de))
                do_remove((sf, df))
                do_add((gi, df))
                do_add((sf, de))
                cdst[i] = df
                pdst[j] = de
                nrel += 1
                break
        moved = cdst != dst_all[car_rows]
        tj = sorted(pdst)
        before = sorted(dst_all[car_rows].tolist() + [int(dst_all[j]) for j in tj])
        after = sorted(cdst.tolist() + [int(pdst[j]) for j in tj])
        assert before == after, ("degree non-neutral", d)
        out_draws.append(dict(
            relocated=int(nrel), moved=int(moved.sum()),
            mass_T70=float(car_vals[Tmask[cdst]].sum()),
            mass_motor=float(car_vals[Mmask[cdst]].sum()),
            n_dst=int(len(set(cdst.tolist()))),
            cdst=cdst.copy(), car_rows=car_rows, pdst=dict(pdst)))
    return out_draws


# ---- CERT-239K (HALTING): the kernel IS the certified function on the carrier
DRAWS_K = rewire_draws_src(_blk_wA, _sel_car_wA, 100, 16943, T70, motor_G,
                           GI_CARRIER)
assert len(DRAWS_K) == 100
_nk239 = 0
for _a, _b in zip(DRAWS_CUT, DRAWS_K):
    for _f in ("relocated", "moved", "mass_T70", "mass_motor", "n_dst"):
        assert _a[_f] == _b[_f], (_f, _a[_f], _b[_f], "CERT-239K (STOP)")
        _nk239 += 1
    assert np.array_equal(_a["cdst"], _b["cdst"]), ("cdst", "CERT-239K (STOP)")
    assert np.array_equal(_a["car_rows"], _b["car_rows"]), ("car_rows", "CERT-239K")
    assert _a["pdst"] == _b["pdst"], ("pdst", "CERT-239K (STOP)")
    _nk239 += 3
assert _nk239 == 800, (_nk239, "CERT-239K count (STOP)")
del DRAWS_K
log(f"[CERT-239K] GREEN {_nk239} EXACT equalities: the parameterised kernel "
    f"equals the certified rewire_draws on all 100 carrier draws (cdst, pdst, "
    f"car_rows included) -> the twin's null is the SAME operator")

#@@CH_FN@@

CH_CUT = _build_ch239(DRAWS_CUT)
assert len(CH_CUT) == 100

#@@REBIND@@

#@@CARNULL@@

# ---------------- two kernels, each gated against verbatim L220 code ---------
def _null239(lc, CH, strict):
    """L220's null loop (its lines 1690-1701) with the source and the
    changed-list as arguments; `strict` only replaces the halting assert so a
    twin draw that reaches no pool cell is REPORTED (T_DEGENERATE) instead of
    killing the run. Admitted by CERT-239N below, never by this docstring."""
    NULL_, ncr = [], 0
    for _k, _ch in enumerate(CH):
        _tg = list(TGT0_CUT)
        for _cidx, _nt in _ch["changed"]:
            _tg[int(IX_CUT["POS"][_cidx])] = _nt
        _d0, _s0 = dijkstra_si(lc, _tg)
        _d1, _s1, _f1, _h1 = dijkstra_si_fh(lc, _tg)
        for _i in POOLS_IDX:
            assert _d0[_i] == _d1[_i] and _s0[_i] == _s1[_i], (_k, _i, "cut null")
            ncr += 2
        _sm = fh_summary(_d1, _s1, _f1, _h1)
        if _sm is None:
            assert not strict, (_k, "unreachable cutwA draw (STOP)")
        NULL_.append(_sm)
    return NULL_, ncr


#@@DECOMP_FN@@

# ---- CERT-239N (HALTING): the kernels ARE L220's primary on the carrier ----
NULL_K, _ = _null239(LC_CAR_CUT, CH_CUT, strict=True)
_cmp_leaf(NULL_K, NULL_CUT, "NULL")
_n239n = _leafcnt239(NULL_CUT)          # DERIVED from the compared artifact
assert _n239n == len(NULL_CUT) * _leafcnt239(NULL_CUT[0]) == 100 * 10, \
    (_n239n, "CERT-239N per-draw leaf count (STOP)")
L220_PRIM_R = _decomp239(CAR_CUT, NULL_CUT, N_OUT_CUT_PIN, LOG2_OUT_CUT,
                         _menu_cut, _relocc)
_cmp_leaf(L220_PRIM_R, S220["L220_primary"], "L220_primary")
_n239n += _leafcnt239(S220["L220_primary"])
assert L220_PRIM_R["branch"] == S220["L220_primary"]["branch"]
log(f"[CERT-239N] GREEN {_n239n} leaves: the null kernel reproduces all 100 "
    f"verbatim L220 draws and L220's whole primary block at FLOAT EQUALITY "
    f"({L220_PRIM_R['branch']}, share_fh {L220_PRIM_R['share_fh']:+.6f}) -> "
    f"it may now be applied to a second source")

#@@COHORT@@

#@@L220COH@@

# ---- CERT-239B (HALTING): L220's cutwA cohort re-derived before it is used --
_cmp_leaf(L220_COH_R, S220["L220_cohort"], "L220_cohort")
_n239b = _leafcnt239(S220["L220_cohort"])
assert _n239b == _leafcnt239(L220_COH_R), "CERT-239B size (STOP)"
assert [k for k, v in COH_CUT.items() if v is None] == ["twin", "fam00_307",
                                                        "fam01_585", "fam02_32072"]
log(f"[CERT-239B] GREEN {_n239b} leaves: L220's cutwA cohort (carrier, "
    f"homolog, {L220_COH_R['n_family']} family, 4 absent) re-derived at FLOAT "
    f"EQUALITY from this run's own walkers")

# ---------------- THE SELECTION (rule frozen in l239/PREREG.md) --------------
assert GI_TWIN4 == 290 and not bool(keep_wA[GI_TWIN4]), \
    "the f4 twin gi 290 is ON cutwA: the card's premise fails (STOP)"
_ann_of239 = {int(_g): _i for _i, _g in enumerate(ann_gi)}
_ct239 = ann.cell_type.fillna("").astype(str).to_numpy()
_sd239 = ann.side.fillna("").astype(str).to_numpy()
_sup_car = str(sup[_ann_of239[GI_CARRIER]])
_isdn = np.zeros(Nall, bool)
_isdn[ann_gi[sup == _sup_car]] = True
_g_of_l239 = np.full(SUB_CUT["n"], -1, np.int64)
_g_of_l239[SUB_CUT["loc"][keep_wA]] = np.where(keep_wA)[0]
assert np.array_equal(np.sort(SUB_CUT["loc"][keep_wA]), np.arange(SUB_CUT["n"]))
assert np.array_equal(SUB_CUT["loc"][_g_of_l239], np.arange(SUB_CUT["n"])), \
    "global<->local inverse (STOP)"
_nout_l239 = np.bincount(SUB_CUT["cols"], minlength=SUB_CUT["n"]).astype(np.int64)
_mout_l239 = np.zeros(SUB_CUT["n"])
np.add.at(_mout_l239, SUB_CUT["cols"], SUB_CUT["jv"])
_nout_g239 = np.zeros(Nall, np.int64)
_mout_g239 = np.zeros(Nall)
_nout_g239[_g_of_l239] = _nout_l239
_mout_g239[_g_of_l239] = _mout_l239
_mraw_g239 = np.zeros(Nall)
np.add.at(_mraw_g239, src_all[emask_wA], np.abs(vals_all[emask_wA]))
_d_car = int(_nout_g239[GI_CARRIER])
assert _d_car == N_OUT_CUT_PIN == int(IX_CUT["END"][LC_CAR_CUT]
                                      - IX_CUT["START"][LC_CAR_CUT])
P239 = _isdn & keep_wA
assert P239[GI_CARRIER] and P239[GI_MIRROR], "an actor is not in its own class"
P239[GI_CARRIER] = False
P239[GI_MIRROR] = False
P239 &= (_nout_g239 >= 1)
_P239 = np.where(P239)[0]
_Dv239 = np.unique(_nout_g239[_P239])
_below = _Dv239[_Dv239 < _d_car]
_above = _Dv239[_Dv239 > _d_car]
assert len(_below) > 0 and len(_above) > 0, \
    "the carrier's degree is an extreme of the pool (STOP)"
D_LO239, D_HI239 = int(_below.max()), int(_above.min())
_lmP = np.log(_mout_g239[_P239])
_lm_car = float(np.log(_mout_g239[GI_CARRIER]))
_lmP_s = np.sort(_lmP, kind="stable")
_ihi = int(np.searchsorted(_lmP_s, _lm_car, side="right"))
_g_lo = (_lm_car - float(_lmP_s[_ihi - 1])) if _ihi >= 1 else float("inf")
_g_hi = (float(_lmP_s[_ihi]) - _lm_car) if _ihi < len(_lmP_s) else float("inf")
B_MASS239 = float(max(_x for _x in (_g_lo, _g_hi) if np.isfinite(_x)))
RANK_CAR239 = _ihi + 1
_C239 = _P239[(_nout_g239[_P239] >= D_LO239) & (_nout_g239[_P239] <= D_HI239)]
_lmC = np.log(_mout_g239[_C239])
_dlmC = np.abs(_lmC - _lm_car)
_oC = np.lexsort((_C239, _dlmC))
_C_sorted = _C239[_oC].tolist()
_dlm_sorted = _dlmC[_oC].tolist()
_nout_sorted = _nout_g239[_C239[_oC]].tolist()
TWIN_GI = int(_C_sorted[0]) if len(_C_sorted) else None
_dlm_twin = float(_dlm_sorted[0]) if len(_C_sorted) else None


def _pickrec239(gi, dlm):
    if gi is None:
        return None
    gi = int(gi)
    _i = _ann_of239[gi]
    return dict(
        gi=gi, cell_type=str(_ct239[_i]), side=str(_sd239[_i]),
        is_glut=bool(is_glut[gi]), carrier_is_glut=bool(is_glut[GI_CARRIER]),
        super_class=_sup_car, n_out=int(_nout_g239[gi]),
        dn_out=int(_nout_g239[gi]) - _d_car,
        m_out_operator=float(_mout_g239[gi]),
        m_out_ratio_to_carrier=float(_mout_g239[gi] / _mout_g239[GI_CARRIER]),
        m_out_raw_no_beta=float(_mraw_g239[gi]),
        carrier_m_out_raw_no_beta=float(_mraw_g239[GI_CARRIER]),
        lm_gap=float(dlm), lm_rank=int(1 + int(np.searchsorted(
            _lmP_s, float(np.log(_mout_g239[gi])), side="right"))),
        in_L211_family=bool(gi in FAMILY),
        frac_out_edges_in_block=(float((_blk_wA & (src_all == gi)).sum()
                                      / _nout_g239[gi])
                                 if _nout_g239[gi] > 0 else None))


MASS_QUAL239 = ("TW_NONE" if TWIN_GI is None
                else ("TW_TIGHT" if _dlm_twin <= B_MASS239 else "TW_LOOSE"))
SEL239 = dict(
    rule=("pool = cutwA cells of the carrier's super_class with n_out >= 1, "
          "carrier and homolog excluded; degree band = the carrier's adjacent "
          "REALISED pool rungs; twin = nearest in ln(out-mass) inside the "
          "band, ties to the smaller gi (l239/PREREG.md, frozen first)"),
    carrier_gi=GI_CARRIER, super_class=_sup_car,
    n_pool=int(len(_P239)), pool_n_out_min=int(int(_Dv239.min())),
    pool_n_out_max=int(int(_Dv239.max())),
    carrier=dict(n_out=_d_car, m_out_operator=float(_mout_g239[GI_CARRIER]),
                 m_out_raw_no_beta=float(_mraw_g239[GI_CARRIER]),
                 lm_rank=RANK_CAR239, lm_rank_frac=float(
                     RANK_CAR239 / (len(_P239) + 1))),
    degree_band=dict(lo=D_LO239, hi=D_HI239, n_in_band=int(len(_C_sorted)),
                     d_lo_from_carrier=_d_car - D_LO239,
                     d_hi_from_carrier=D_HI239 - _d_car,
                     n_pool_lt_80=int(len(_below)),
                     n_pool_gt_80=int(len(_above)),
                     n_pool_eq_80=int(int((_nout_g239[_P239] == _d_car).sum()))),
    mass_bar=dict(g_lo=float(_g_lo) if np.isfinite(_g_lo) else None,
                  g_hi=float(_g_hi) if np.isfinite(_g_hi) else None,
                  B_mass=B_MASS239),
    twin_gi=TWIN_GI, mass_quality=MASS_QUAL239,
    runners_up=[dict(gi=int(_C_sorted[_j]), n_out=int(_nout_sorted[_j]),
                     lm_gap=float(_dlm_sorted[_j]),
                     is_glut=bool(is_glut[_C_sorted[_j]]))
                for _j in range(min(6, len(_C_sorted)))])
assert TWIN_GI not in (GI_CARRIER, GI_MIRROR, GI_TWIN4), "twin is an actor"
SEL_SHA239 = _hl239.sha256(json.dumps(SEL239, sort_keys=True).encode()
                           ).hexdigest()[:16]
o["L239_selection"] = SEL239
o["L239_selection_sha16"] = SEL_SHA239
log(f"[L239] SELECTION (frozen sha {SEL_SHA239}): pool {len(_P239)} "
    f"{_sup_car} | degree band [{D_LO239}, {D_HI239}] holds "
    f"{len(_C_sorted)} | B_mass {B_MASS239:.4f} -> "
    + ("NO candidate" if TWIN_GI is None else
       f"twin gi {TWIN_GI} {_ct239[_ann_of239[TWIN_GI]]} "
       f"{_sd239[_ann_of239[TWIN_GI]]} n_out {_nout_g239[TWIN_GI]} "
       f"lm gap {_dlm_twin:.4f} [{MASS_QUAL239}]"))

# ---------------- the twin, by the UNCHANGED certified walkers ---------------
TWIN_CUT, LC_TWIN_CUT, _menu_t = None, -1, []
_nw239 = 0
if TWIN_GI is not None:
    LC_TWIN_CUT = int(SUB_CUT["loc"][TWIN_GI])
    assert 0 <= LC_TWIN_CUT < SUB_CUT["n"] and LC_TWIN_CUT != LC_CAR_CUT
    assert LC_TWIN_CUT not in set(IX_CUT["POOLS_IDX"])
    assert LC_TWIN_CUT != int(SUB_CUT["loc"][GI_MIRROR])
    _tb0, _tb1 = IX_CUT["START"][LC_TWIN_CUT], IX_CUT["END"][LC_TWIN_CUT]
    assert _tb1 - _tb0 == int(_nout_g239[TWIN_GI]) == int(
        (emask_wA & (src_all == TWIN_GI)).sum()), "twin SI menu size (STOP)"
    _menu_t = sorted(IX_CUT["T_L"][_tb0:_tb1])
    assert float(min(_menu_t)) > 0.0, "a first-hop cost of zero bits"
    _dt0, _st0 = dijkstra_si(LC_TWIN_CUT, TGT0_CUT)
    TWIN_SI = si_summary(_dt0, _st0)
    _dt1, _st1, _ft1, _ht1 = dijkstra_si_fh(LC_TWIN_CUT, TGT0_CUT)
    for _i in POOLS_IDX:
        assert _dt0[_i] == _dt1[_i] and _st0[_i] == _st1[_i], \
            (_i, "twin walker (STOP)")
        _nw239 += 2
    TWIN_CUT = fh_summary(_dt1, _st1, _ft1, _ht1)
    if TWIN_CUT is not None:
        assert TWIN_CUT["si_mean"] == TWIN_SI["si_mean"], "twin si_mean"
QUAL239 = MASS_QUAL239 if TWIN_CUT is not None else (
    "TW_DEGENERATE" if TWIN_GI is not None else "TW_NONE")

# ---- the twin's OWN null: the certified operator on a second source ---------
TWIN_PRIM, NULL_TWIN, _n_unreach_t, _menuchk_t = None, None, 0, 0
_reloc_t, _drawstats_t = [], dict()
if TWIN_CUT is not None:
    _sel_tw = emask_wA & (src_all == TWIN_GI)
    DRAWS_TWIN = rewire_draws_src(_blk_wA, _sel_tw, 100, 16943, T70, motor_G,
                                  TWIN_GI)
    assert len(DRAWS_TWIN) == 100
    _drawstats_t = dict(
        med_relocated=float(np.median([x["relocated"] for x in DRAWS_TWIN])),
        med_moved=float(np.median([x["moved"] for x in DRAWS_TWIN])),
        med_n_dst=float(np.median([x["n_dst"] for x in DRAWS_TWIN])),
        min_relocated=int(min(x["relocated"] for x in DRAWS_TWIN)))
    CH_TWIN = _build_ch239(DRAWS_TWIN)
    assert len(CH_TWIN) == 100
    for _ch in CH_TWIN:
        _tg = list(IX_CUT["TGT0"])
        for _cidx, _nt in _ch["changed"]:
            _tg[int(IX_CUT["POS"][_cidx])] = _nt
        assert sorted(IX_CUT["T_L"][_tb0:_tb1]) == _menu_t, "TWIN MENU MOVED (STOP)"
        _reloc_t.append(int(sum(1 for _i in range(_tb0, _tb1)
                                if _tg[_i] != IX_CUT["TGT0"][_i])))
        _menuchk_t += 1
    assert _menuchk_t == 100 and min(_reloc_t) >= 1, "twin menu/reloc guard (STOP)"
    NULL_TWIN, _nct239 = _null239(LC_TWIN_CUT, CH_TWIN, strict=False)
    _nw239 += _nct239
    _n_unreach_t = int(sum(1 for r in NULL_TWIN if r is None))
    if _n_unreach_t == 0:
        TWIN_PRIM = _decomp239(TWIN_CUT, NULL_TWIN, int(_nout_g239[TWIN_GI]),
                               float(np.log2(int(_nout_g239[TWIN_GI]))),
                               _menu_t, _reloc_t)
        TWIN_PRIM["n_unreachable_draws"] = 0
    else:
        TWIN_PRIM = dict(
            branch="T_DEGENERATE", share_fh=None, share_rem=None,
            bars=dict(degenerate_if_reach_le=IX_CUT["N_POOL"] // 2),
            n_unreachable_draws=_n_unreach_t, D_total_bits=None, D_fh_bits=None,
            D_rem_bits=None, additivity_abs_err=None, carrier=TWIN_CUT,
            null_mean=None, null_median=None, null_spread=None,
            percentiles=None, menu=None,
            substrate=dict(name="cutwA", n=SUB_CUT["n"],
                           n_edges=SUB_CUT["n_edges"],
                           n_pool_cells=IX_CUT["N_POOL"]))
    TWIN_PRIM["actor"] = "twin"
    TWIN_PRIM["gi"] = TWIN_GI
    TWIN_PRIM["draws"] = _drawstats_t
    del DRAWS_TWIN, CH_TWIN
log(f"[CERT-239W] GREEN {_nw239} EXACT equalities between dijkstra_si and the "
    f"first-hop walker for the twin + every usable draw; twin menu invariant "
    f"in {_menuchk_t}/100 draws")

# ---------------- the two readings (PREREG "Branches") -----------------------
_CAR_SHARE = CAR_CUT["fh_share_of_si"]
_G_H = S220["L220_cohort"]["mirror"]["share_gap_vs_carrier"]
_famv = [v for k, v in COH_CUT.items() if k.startswith("fam") and v is not None]
_Dfam = np.array([abs(v["fh_share_of_si"] - _CAR_SHARE) for v in _famv])
assert len(_famv) == L220_COH_R["n_family"] == 30
D_FAM239 = float(np.median(_Dfam))


def _branch239(share):
    _g = abs(share - _CAR_SHARE)
    if _g <= _G_H:
        return "TW_HOMOLOG_LIKE", _g
    return ("TW_FAMILY_LIKE" if _g <= D_FAM239 else "TW_OUTSIDE_FAMILY"), _g


G239, PRI239 = None, "NOT_SCORED"
if TWIN_CUT is not None:
    PRI239, G239 = _branch239(TWIN_CUT["fh_share_of_si"])
SCORABLE239 = QUAL239 in ("TW_TIGHT", "TW_LOOSE")
if not SCORABLE239:
    PRI239 = "NOT_SCORED"

# UNREGISTERED description (written after the PREREG froze; no null, no
# branch reads it): every band candidate's raw share, so "how often a
# degree-matched class-mate sits within the homolog gap" is on record.
_CAND239 = []
for _j, _g in enumerate(_C_sorted):
    _lc = int(SUB_CUT["loc"][_g])
    _d, _s, _f, _h = dijkstra_si_fh(_lc, TGT0_CUT)
    _sm = fh_summary(_d, _s, _f, _h)
    _sh = None if _sm is None else _sm["fh_share_of_si"]
    _br = (None if _sm is None else _branch239(_sh)[0])
    _CAND239.append(dict(
        gi=int(_g), rank_by_mass=_j + 1, n_out=int(_nout_sorted[_j]),
        lm_gap=float(_dlm_sorted[_j]), is_glut=bool(is_glut[_g]),
        in_L211_family=bool(int(_g) in FAMILY), reaches_pool=_sm is not None,
        fh_share_of_si=_sh, gap_vs_carrier=(None if _sh is None else abs(_sh - _CAR_SHARE)),
        branch=_br, si_mean=(None if _sm is None else _sm["si_mean"]),
        is_pick=bool(int(_g) == TWIN_GI)))
_gaps_c = np.array([r["gap_vs_carrier"] for r in _CAND239 if r["gap_vs_carrier"] is not None])
_CANDSUM239 = dict(
    label="UNREGISTERED description (no null, no branch reads it)",
    n_candidates=int(len(_CAND239)), n_reaching_pool=int(len(_gaps_c)),
    n_gap_le_homolog_gap=int((_gaps_c <= _G_H).sum()) if len(_gaps_c) else 0,
    gap_min=float(_gaps_c.min()) if len(_gaps_c) else None,
    gap_med=float(np.median(_gaps_c)) if len(_gaps_c) else None,
    gap_max=float(_gaps_c.max()) if len(_gaps_c) else None)

# SENSITIVITY (PREREG 0d): a half-IQR degree band, same nearest-in-mass rule
_q25, _q75 = np.percentile(_nout_g239[_P239].astype(float), [25, 75])
B_DEG2 = float((_q75 - _q25) / 2.0)
_C2 = _P239[np.abs(_nout_g239[_P239] - _d_car) <= B_DEG2]
SENS239 = dict(B_deg2=B_DEG2, q25=float(_q25), q75=float(_q75),
               n_in_band=int(len(_C2)), gi=None, same_pick=None)
if len(_C2):
    _lm2 = np.abs(np.log(_mout_g239[_C2]) - _lm_car)
    _o2 = np.lexsort((_C2, _lm2))
    _g2 = int(_C2[_o2[0]])
    _lc = int(SUB_CUT["loc"][_g2])
    _d, _s, _f, _h = dijkstra_si_fh(_lc, TGT0_CUT)
    _sm2 = fh_summary(_d, _s, _f, _h)
    SENS239.update(
        gi=_g2, same_pick=bool(_g2 == TWIN_GI), n_out=int(_nout_g239[_g2]),
        lm_gap=float(_lm2[_o2[0]]),
        reaches_pool=_sm2 is not None,
        fh_share_of_si=(None if _sm2 is None else _sm2["fh_share_of_si"]),
        branch=(None if _sm2 is None else _branch239(_sm2["fh_share_of_si"])[0]))

# sign-class alternative (PREREG 0f): descriptive
SIGN239 = dict(twin_is_glut=None, carrier_is_glut=bool(is_glut[GI_CARRIER]),
               same_sign_required=False, gi=None, branch=None)
if TWIN_GI is not None:
    SIGN239["twin_is_glut"] = bool(is_glut[TWIN_GI])
    if is_glut[TWIN_GI] != is_glut[GI_CARRIER]:
        for _j, _g in enumerate(_C_sorted):
            if is_glut[_g] == is_glut[GI_CARRIER]:
                _lc = int(SUB_CUT["loc"][_g])
                _d, _s, _f, _h = dijkstra_si_fh(_lc, TGT0_CUT)
                _sm3 = fh_summary(_d, _s, _f, _h)
                SIGN239.update(
                    gi=int(_g), rank_by_mass=_j + 1, n_out=int(_nout_sorted[_j]),
                    lm_gap=float(_dlm_sorted[_j]),
                    fh_share_of_si=(None if _sm3 is None else _sm3["fh_share_of_si"]),
                    branch=(None if _sm3 is None else _branch239(_sm3["fh_share_of_si"])[0]))
                break

_F4C = F4["cohort"]
_G_f4 = abs(_F4C["twin_fh_share_of_si"] - _F4C["carrier_fh_share_of_si"])
_m4 = F4["cohort"]["all_actors"].get("mirror_928")
_G_H_f4 = (None if _m4 is None else abs(
    _m4["fh_share_of_si"] - _F4C["carrier_fh_share_of_si"]))

# ---------------- predictions, scored (never amended) ------------------------
_ndfh_t = (None if TWIN_CUT is None else TWIN_CUT["n_distinct_first_hops"])
_sec239 = (None if TWIN_PRIM is None else TWIN_PRIM["branch"])
_p5 = None if (SENS239["gi"] is None or SENS239["same_pick"]
               or not SENS239["reaches_pool"]) else (SENS239["branch"] == PRI239)
o["L239_predictions"] = dict(
    P1_primary_TW_FAMILY_LIKE=dict(
        registered="primary branch TW_FAMILY_LIKE", value=PRI239,
        score=(PRI239 == "TW_FAMILY_LIKE") if SCORABLE239 else False),
    P2_quality_not_tight=dict(
        registered="quality TW_LOOSE or TW_NONE", value=QUAL239,
        score=QUAL239 in ("TW_LOOSE", "TW_NONE")),
    P3_secondary_T_TRANSPORTS=dict(
        registered="twin's own-null branch T_TRANSPORTS", value=_sec239,
        score=(_sec239 == "T_TRANSPORTS") if _sec239 is not None else False),
    P4_funnel_transports_to_twin=dict(
        registered="n_distinct_first_hops(twin) <= 0.35 * n_out(twin)",
        value=(None if _ndfh_t is None else dict(
            n_distinct_first_hops=int(_ndfh_t), n_out=int(_nout_g239[TWIN_GI]),
            ratio=float(_ndfh_t / _nout_g239[TWIN_GI]))),
        score=bool(_ndfh_t is not None
                   and _ndfh_t <= 0.35 * _nout_g239[TWIN_GI])),
    P5_band_robust=dict(
        registered="half-IQR pick (if different and non-degenerate) lands in "
                   "the same primary branch", value=SENS239["branch"],
        score=_p5, note=("VACUOUS: same pick or degenerate (not scored)"
                         if _p5 is None else None)))
o["L239_predictions_score"] = dict(
    n_scored=sum(1 for v in o["L239_predictions"].values() if v["score"] is not None),
    n_true=sum(1 for v in o["L239_predictions"].values() if v["score"] is True),
    n_false=sum(1 for v in o["L239_predictions"].values() if v["score"] is False),
    n_vacuous=sum(1 for v in o["L239_predictions"].values() if v["score"] is None))

# ---------------- restore + CERT-REBIND (HALTING) ----------------------------
#@@RESTORE@@
_d2, _s2 = dijkstra_si(LC_CAR, TGT0)
_nreb239 = 0
for _j, _i in enumerate(POOLS_IDX):
    assert _d2[_i] == _ref_pool[_j][0], (_i, "REBIND leaked dist (STOP)")
    assert _s2[_i] == _ref_pool[_j][1], (_i, "REBIND leaked si (STOP)")
    _nreb239 += 2
assert NL == _NL0 and N_POOL == _NP0 and len(START) == _NL0
assert _nreb239 == 606, (_nreb239, "CERT-REBIND count (STOP)")
assert _hl239.sha256(json.dumps(SEL239, sort_keys=True).encode()
                     ).hexdigest()[:16] == SEL_SHA239, "the pick moved"
assert _hl239.sha256(open("l239_static.py", "rb").read()).hexdigest()[:16] == \
    o["slice_l239"]["static_sha256_16"], "the running script changed"
for _p, _fp in FP_SRC.items():
    _st = _os239.stat(_p)
    assert (int(_st.st_size), int(_st.st_mtime_ns)) == _fp, (_p, "prior moved (STOP)")
for _p, _k in (("l220/static.json", "l220"), ("l220_static.py", "l220s"),
               ("l220_tail.py", "l220t"), ("l220/PREREG.md", "l220p")):
    _st = _os239.stat(_p)
    assert (int(_st.st_size), int(_st.st_mtime_ns)) == FP239[_k], \
        (_p, "prior moved (STOP)")
with open("l239/PREREG.md") as _pr239:
    _prh239 = _hl239.sha256(_pr239.read().encode()).hexdigest()[:16]
log(f"[CERT-REBIND] GREEN {_nreb239} BIT-IDENTICAL f4wA values after rebinding "
    f"the globals to cutwA and back")

o["L239_primary"] = dict(
    label=("PRIMARY (PREREG): G = |fh_share_of_si(twin) - fh_share_of_si"
           "(carrier)| on cutwA, read against the stored homolog gap and the "
           "family's median distance from the carrier"),
    quality=QUAL239, mass_quality=MASS_QUAL239, branch=PRI239, G=G239,
    G_homolog=_G_H, D_family_median=D_FAM239,
    family=dict(n=len(_famv), gap_min=float(_Dfam.min()),
                gap_med=D_FAM239, gap_max=float(_Dfam.max()),
                n_within_homolog_gap=int((_Dfam <= _G_H).sum())),
    carrier=dict(gi=GI_CARRIER, fh_share_of_si=_CAR_SHARE,
                 si_mean=CAR_CUT["si_mean"], fh_mean=CAR_CUT["fh_mean"],
                 rem_mean=CAR_CUT["rem_mean"], n_out=N_OUT_CUT_PIN,
                 n_distinct_first_hops=CAR_CUT["n_distinct_first_hops"],
                 summary=CAR_CUT),
    twin=(None if TWIN_CUT is None else dict(
        pick=_pickrec239(TWIN_GI, _dlm_twin), fh_share_of_si=TWIN_CUT["fh_share_of_si"],
        si_mean=TWIN_CUT["si_mean"], fh_mean=TWIN_CUT["fh_mean"],
        rem_mean=TWIN_CUT["rem_mean"],
        n_distinct_first_hops=TWIN_CUT["n_distinct_first_hops"],
        summary=TWIN_CUT)),
    homolog=dict(gi=GI_MIRROR,
                 fh_share_of_si=L220_COH_R["mirror"]["summary"]["fh_share_of_si"],
                 summary=L220_COH_R["mirror"]["summary"]),
    f4wA_for_reference=dict(
        carrier_fh_share_of_si=_F4C["carrier_fh_share_of_si"],
        twin_gi=GI_TWIN4, twin_fh_share_of_si=_F4C["twin_fh_share_of_si"],
        G_twin=_G_f4, G_homolog=_G_H_f4,
        family_fh_share_med=_F4C["family_fh_share_med"],
        note="the f4 twin was selected by the L178 f4 out-mass rule, not by "
             "this card's; shown only as the pattern being re-run"))
o["L239_twin_null"] = dict(
    label=("SECONDARY (PREREG 0b/0h): the twin's own 100 degree-neutral "
           "destination-swap draws, same family and seed (16943); the first "
           "null any non-carrier cell of this family has had"),
    kernel="rewire_draws_src (admitted by CERT-239K); loop gated by CERT-239N",
    n_unreachable_draws=_n_unreach_t,
    menu_invariant_draws=_menuchk_t, result=TWIN_PRIM)
o["L239_carrier_recertified"] = dict(
    note="L220's own primary block re-derived by this run's kernels (CERT-239N)",
    result=L220_PRIM_R)
o["L239_candidates"] = _CAND239
o["L239_candidates_summary"] = _CANDSUM239
o["L239_sensitivity_half_iqr"] = SENS239
o["L239_sign_class"] = SIGN239
o["certification"] = dict(
    parent_pin="GREEN", n_slice_keys=len(_k_slice), CERT_239A=_n239a,
    CERT_REWCUT=_nrw, CERT_239K=_nk239, CERT_MENUCUT=_menuchkc,
    CERT_WALKCUT_parent=_ncross, CERT_239N=_n239n, CERT_239B=_n239b,
    CERT_239W=_nw239, CERT_REBIND=_nreb239, pins="ALL GREEN")
o["limitations"] = [
    "ONE substrate (cutwA), ONE operator (g = 1 anatomical |W_beta|), ONE "
    "null family (degree-neutral destination swaps, seed 16943). L207's law: "
    "a magnitude does not transport between nulls.",
    "ONE twin answers whether THIS matched cell is like the carrier, not how "
    "often; the registered runners-up have raw shares and no nulls.",
    "the degree band is the pool's own resolution at out-degree 80; a reader "
    "who prefers a caliper should read the half-IQR sensitivity leg.",
    "the first-hop menu is invariant across a source's own draws (re-measured "
    "for the twin), so D_fh is SELECTION among a fixed menu by construction.",
    "mass_T70 / mass_motor in the twin's draw records use the CARRIER's "
    "target masks (PREREG 0g) and are not interpreted.",
    "selected-unit caveat: the carrier was selected for an extreme SI; the "
    "twin leg is a control on that selection, not an independent test of it.",
    "the stored family dispersion is a DESCRIPTION of 30 cells, no null.",
    "relation to L236/L237 declared (PREREG 0j): cited, not re-banked.",
]
o["pins"] = "ALL GREEN"
o["prereg_sha16"] = _prh239
_os239.makedirs("l239", exist_ok=True)


def _js239(x):
    """numpy scalars only (bool_/int64/...): anything else is a real error"""
    if hasattr(x, "item") and callable(x.item):
        return x.item()
    raise TypeError(f"{type(x).__name__} is not JSON serializable")


json.dump(o, open("l239/static.json", "w"), indent=1, default=_js239)
log("=" * 72)
log(f"L239 DONE {time.time()-t0:.0f}s | {QUAL239} | twin "
    + ("none" if TWIN_GI is None else f"gi {TWIN_GI} n_out {_nout_g239[TWIN_GI]} "
       f"lm gap {_dlm_twin:.4f} (B_mass {B_MASS239:.4f})")
    + f" | fh/si carrier {_CAR_SHARE:.4f} homolog "
    f"{L220_COH_R['mirror']['summary']['fh_share_of_si']:.4f} (gap {_G_H:.4f}) "
    + ("" if TWIN_CUT is None else
       f"twin {TWIN_CUT['fh_share_of_si']:.4f} -> G {G239:.4f} vs family "
       f"median distance {D_FAM239:.4f}")
    + f" | {PRI239} | twin own-null {_sec239} share_fh "
    + ("na" if TWIN_PRIM is None or TWIN_PRIM["share_fh"] is None
       else f"{TWIN_PRIM['share_fh']:+.4f}")
    + f" | CERT 239A {_n239a} + REWCUT {_nrw} + 239K {_nk239} + MENUCUT "
    f"{_menuchkc} + 239N {_n239n} + 239B {_n239b} + 239W {_nw239} + REBIND "
    f"{_nreb239} | predictions {o['L239_predictions_score']}")
