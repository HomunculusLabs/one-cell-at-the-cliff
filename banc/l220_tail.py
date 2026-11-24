# ================= L220 TAIL (appended by l220_build.py) =================
# Everything above this line is VERBATIM source:
#   l151_static.py 1-319, l178_tail.py 7-149, l206_mid.py,
#   l178_tail.py 348-458, l206_tail.py 22-263, l211_mid2.py,
#   l206_tail.py 320-461  <-- L206's SEARCH-INFORMATION block, re-run whole,
#   l207_tail.py 26-146   <-- gain invariance + the GENERIC substrate builder
#                             + CERT-GEN,
#   l211_tail.py 29-322   <-- L211's WHOLE measurement block (CERT-SI,
#                             CERT-MENU, dijkstra_si_fh + fh_summary,
#                             CERT-FH's 61,819 exact equalities, the
#                             decomposition and the 35-actor cohort), sliced
#                             to CUT its predictions/writer block (L213).
# So CERT-F4, the three stored gains, the CSR orientation, the 20 pool sizes,
# CERT-178's 420 values, CERT-REW, the lam1 power iteration, the depth-1..10
# sweep, CERT-NULL, the whole search-information block, CERT-GEN, CERT-SI,
# CERT-MENU and CERT-FH have ALL re-run as free certification, and L211's
# f4wA decomposition has been RECOMPUTED, before any L220 number is read.
# PREREG: l220/PREREG.md (registered first).
# Writes l220/static.json ONLY. Zero rollouts, zero settles, zero dynamics.
import os as _os220

o["design"] = (
    "L220 does L211's FIRST-HOP/REMAINDER split TRANSPORT to the BASE "
    "unfloored cutwA substrate? Generalise L206's search-information index "
    "construction to a second substrate with ONE generic builder gated by "
    "exact array equality against the certified f4wA specialisation, then "
    "call the UNCHANGED certified dijkstra on the rebound globals. The null "
    "is the l169c NATIVE wA-block destination swap (seed 16943), so the leg "
    "is SCOREABLE, not descriptive. PREREG l220/PREREG.md.")
o["prereg"] = "l220/PREREG.md"
with open("l220_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(13)])

FP_SRC = {}
for _p in ("l206/static.json", "l178/static.json", "l169c/static.json",
           "l211/static.json"):
    _st = _os220.stat(_p)
    FP_SRC[_p] = (int(_st.st_size), int(_st.st_mtime_ns))

N_OUT_CUT_PIN = 80          # l151_static.py 126-133 pin, declared in 0b
LOG2_OUT_F4 = float(np.log2(69))
LOG2_OUT_CUT = float(np.log2(N_OUT_CUT_PIN))

log("=" * 72)
log("[L220] the L211 TRANSPORT leg on the BASE unfloored cutwA substrate")

# ---------------- CERT-211 (HALTING): the card's required anchor ------------
# The verbatim l211_tail.py 29-322 slice above RECOMPUTED L211's whole f4wA
# decomposition into o["L211_primary"] / o["L211_cohort"].  Every leaf must
# equal l211/static.json by FLOAT EQUALITY before a single cutwA number is
# read -- that is what licenses calling the cutwA result a TRANSPORT test.
_S211 = json.load(open("l211/static.json"))
_cert211 = [0]


def _cmp211(a, b, path):
    if isinstance(a, dict):
        assert isinstance(b, dict), (path, "dict/non-dict")
        assert set(a) == set(b), (path, sorted(set(a) ^ set(b)))
        for k in sorted(a):
            _cmp211(a[k], b[k], f"{path}/{k}")
        return
    if isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), (path, "list")
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp211(x, y, f"{path}[{i}]")
        return
    if isinstance(a, float) or isinstance(b, float):
        assert float(a) == float(b), (path, repr(a), repr(b), "NOT float-equal")
    else:
        assert a == b, (path, repr(a), repr(b))
    _cert211[0] += 1


for _blk in ("L211_primary", "L211_cohort"):
    _cmp211(o[_blk], _S211[_blk], _blk)
assert _cert211[0] >= 400, ("CERT-211 too few leaves", _cert211[0])
assert o["L211_primary"]["branch"] == "B_REMAINDER", "L211 branch drift"
assert o["L211_primary"]["share_fh"] == -0.005618879769401901, "share_fh drift"
assert o["L211_primary"]["carrier"]["si_mean"] == 22.39317740345491
assert o["L211_primary"]["carrier"]["fh_share_of_si"] == 0.2611188191551899
assert o["L211_primary"]["menu"]["n_out_edges"] == 69
log(f"[CERT-211] GREEN {_cert211[0]} stored L211 values (primary + cohort) "
    f"reproduced by FLOAT EQUALITY from my own re-run")
F4 = dict(primary=o["L211_primary"], cohort=o["L211_cohort"])

# ---------------- ONE generic SI-index builder (gated before use) ----------
def build_si_index(jv, rows, cols, n, pool_all):
    """L206's search-information index construction, EXPRESSION-IDENTICALLY
    (L206's float-equality law: a float claim is a claim about the
    expression), generalised over (operator, CSR, size, pools)."""
    A_E_ = jv
    AMAX_ = float(A_E_.max())
    LW_ = -np.log10(A_E_ / AMAX_)
    assert float(LW_.min()) >= 0.0
    s_out_ = np.zeros(n)
    np.add.at(s_out_, cols, A_E_)
    assert float(s_out_[cols].min()) > 0.0
    NLT_ = -np.log2(A_E_ / s_out_[cols])
    assert float(NLT_.min()) >= 0.0
    _o = np.argsort(cols, kind="stable")
    _ss = cols[_o]
    _ts = rows[_o]
    _pis = np.empty(_o.size, np.int64)
    _pis[_o] = np.arange(_o.size)
    return dict(
        START=np.searchsorted(_ss, np.arange(n)).tolist(),
        END=np.searchsorted(_ss, np.arange(n) + 1).tolist(),
        L_L=LW_[_o].tolist(), T_L=NLT_[_o].tolist(), TGT0=_ts.tolist(),
        POS=_pis, AMAX=AMAX_, NL=n, POOLS_IDX=pool_all.tolist(),
        N_POOL=int(len(pool_all)))


# CERT-SIGEN (HALTING): generic == certified f4wA specialisation, EXACTLY
_IX_F4 = build_si_index(jv_abs_an, csr_rows, csr_cols, NL, POOL_ALL)
_ngen = 0
for _k, _ref in (("START", START), ("END", END), ("L_L", L_L),
                 ("T_L", T_L), ("TGT0", TGT0), ("POOLS_IDX", POOLS_IDX)):
    assert _IX_F4[_k] == _ref, (_k, "generic SI index differs (STOP)")
    _ngen += len(_ref)
assert np.array_equal(_IX_F4["POS"], _pos_in_sorted), "pos_in_sorted (STOP)"
_ngen += int(_pos_in_sorted.size)
assert _IX_F4["AMAX"] == AMAX and _IX_F4["NL"] == NL
assert _IX_F4["N_POOL"] == N_POOL
_ngen += 3
log(f"[CERT-SIGEN] GREEN {_ngen} EXACT list/array equalities: ONE generic SI "
    f"index builder reproduces the certified f4wA specialisation (START, END, "
    f"L_L, T_L, TGT0, pos_in_sorted, A_max) before touching cutwA")

# ---------------- 0c: the gain no-op, MEASURED not assumed -----------------
# L and T are mathematically invariant to a positive global rescale of A.
# L209: a mathematical no-op is not a floating-point no-op.  cutwA will use
# its own g=1 operator (L209's convention); bound the induced error here.
_IX_F4_G1 = build_si_index(jv_g1, csr_rows, csr_cols, NL, POOL_ALL)
assert _IX_F4_G1["START"] == START and _IX_F4_G1["END"] == END
assert _IX_F4_G1["TGT0"] == TGT0, "edge ORDER depends on the gain (impossible)"
_dL = float(np.abs(np.array(_IX_F4_G1["L_L"]) - np.array(L_L)).max())
_dT = float(np.abs(np.array(_IX_F4_G1["T_L"]) - np.array(T_L)).max())
_START0, _END0, _L0, _T0, _TG0 = START, END, L_L, T_L, TGT0
_NL0, _PI0, _NP0 = NL, POOLS_IDX, N_POOL
_d_ref, _s_ref = dijkstra_si(LC_CAR, TGT0)
_ref_pool = [(_d_ref[_i], _s_ref[_i]) for _i in POOLS_IDX]
L_L, T_L = _IX_F4_G1["L_L"], _IX_F4_G1["T_L"]
_dg, _sg, _fg, _hg = dijkstra_si_fh(LC_CAR, TGT0)
_CARG1 = fh_summary(_dg, _sg, _fg, _hg)
L_L, T_L = _L0, _T0
_car_si_f4 = F4["primary"]["carrier"]["si_mean"]
_car_fh_f4 = F4["primary"]["carrier"]["fh_mean"]
o["gain_noop_measured"] = dict(
    max_abs_dL=_dL, max_abs_dT=_dT,
    rel_d_si_mean=abs(_CARG1["si_mean"] - _car_si_f4) / _car_si_f4,
    rel_d_fh_mean=abs(_CARG1["fh_mean"] - _car_fh_f4) / _car_fh_f4,
    g1_si_mean=_CARG1["si_mean"], g1_fh_mean=_CARG1["fh_mean"],
    g1_fh_share_of_si=_CARG1["fh_share_of_si"],
    gscaled_fh_share_of_si=F4["primary"]["carrier"]["fh_share_of_si"],
    note=("registered in PREREG 0c: f4wA keeps the certified G-scaled index "
          "so CERT-SI/CERT-211 hold at float equality; cutwA uses its own "
          "g=1 index; this is the measured size of that choice."))
log(f"[0c] gain no-op MEASURED: max|dL| {_dL:.3e} max|dT| {_dT:.3e} -> "
    f"carrier si_mean rel {o['gain_noop_measured']['rel_d_si_mean']:.3e}, "
    f"fh_mean rel {o['gain_noop_measured']['rel_d_fh_mean']:.3e}")

# ---------------- the cutwA substrate (certified generic builder) ----------
SUB_CUT = build_sub(keep_wA, emask_wA, "cutwA")
assert SUB_CUT["n"] == 21785 and SUB_CUT["n_edges"] == 644177, "cutwA (STOP)"
assert bool(keep_wA[GI_CARRIER]), "carrier not on cutwA (STOP)"
LC_CAR_CUT = int(SUB_CUT["loc"][GI_CARRIER])
assert LC_CAR_CUT >= 0
_cutcols = SUB_CUT["cols"]
_n_out_cut = int((_cutcols == LC_CAR_CUT).sum())
assert _n_out_cut == int(_sel_car_wA.sum()) == N_OUT_CUT_PIN, \
    (_n_out_cut, int(_sel_car_wA.sum()), "cutwA carrier out-degree (STOP)")
IX_CUT = build_si_index(SUB_CUT["jv"], SUB_CUT["rows"], _cutcols,
                        SUB_CUT["n"], SUB_CUT["pool_all"])
assert LC_CAR_CUT not in set(IX_CUT["POOLS_IDX"]), "source is a pool cell"
log(f"[L220] cutwA built: n {SUB_CUT['n']:,} edges {SUB_CUT['n_edges']:,} | "
    f"carrier local {LC_CAR_CUT} out-degree {_n_out_cut} (f4wA 69) | "
    f"pool cells {IX_CUT['N_POOL']} | A_max {IX_CUT['AMAX']:.6f}")

# ---------------- global edge -> cutwA CSR -> sorted-by-source maps --------
_ei_cut = np.where(emask_wA)[0]
_eipos_cut = {int(p): i for i, p in enumerate(_ei_cut)}
_lsrc_cut = SUB_CUT["loc"][src_all[_ei_cut]]
_ldst_cut = SUB_CUT["loc"][dst_all[_ei_cut]]
assert int(_lsrc_cut.min()) >= 0 and int(_ldst_cut.min()) >= 0
_NCUT = SUB_CUT["n"]
_key_csr_cut = (SUB_CUT["rows"].astype(np.int64) * _NCUT
                + _cutcols.astype(np.int64))
assert np.array_equal(np.sort(_key_csr_cut, kind="stable"), _key_csr_cut), \
    "cutwA CSR not row-major sorted (STOP)"
_key_e_cut = _ldst_cut.astype(np.int64) * _NCUT + _lsrc_cut.astype(np.int64)
_pos_in_csr_cut = np.searchsorted(_key_csr_cut, _key_e_cut)
assert np.array_equal(_key_csr_cut[_pos_in_csr_cut], _key_e_cut), \
    "cutwA edge->CSR map (STOP)"

# ---------------- CERT-REWCUT (HALTING): the l169c NATIVE wA-block null ----
# PREREG 0a: the stored l169c P6 draws ARE the wA-block draws, so the
# certified rewire_draws is called UNCHANGED with the certified cutwA
# arguments and gated against the stored artifact BEFORE any SI read.
DRAWS_CUT = rewire_draws(_blk_wA, _sel_car_wA, 100, 16943, T70, motor_G)
assert len(DRAWS_CUT) == 100
_nrw = 0
for _k, _v in (("med_relocated", _med(DRAWS_CUT, "relocated")),
               ("min_relocated", min(x["relocated"] for x in DRAWS_CUT)),
               ("med_moved", _med(DRAWS_CUT, "moved")),
               ("med_mass_T70", _med(DRAWS_CUT, "mass_T70")),
               ("med_mass_motor_share",
                _med(DRAWS_CUT, "mass_motor") / _car_mass_wA),
               ("med_n_dst", _med(DRAWS_CUT, "n_dst"))):
    assert _v == S169C[_k], (_k, _v, S169C[_k], "CERT-REWCUT (STOP)")
    _nrw += 1
for _i5, _st5 in enumerate(S169C["per_draw_first5"]):
    for _k5 in ("relocated", "moved", "mass_T70", "mass_motor", "n_dst"):
        assert DRAWS_CUT[_i5][_k5] == _st5[_k5], (_i5, _k5, "CERT-REWCUT")
        _nrw += 1
log(f"[CERT-REWCUT] GREEN {_nrw} stored l169c P6 values reproduced at FLOAT "
    f"EQUALITY from my own cutwA-block call (100 draws, seed 16943) -> the "
    f"cutwA SI null is the l169c NATIVE null, not an invented one")

# ---------------- cutwA changed-lists + CERT-MENUCUT -----------------------
CH_CUT = []
for _d in DRAWS_CUT:
    _cr = _d["car_rows"]
    _newd = _d["cdst"]
    _ch = []
    for _i, _gpos in enumerate(_cr):
        if int(_newd[_i]) == int(dst_all[_gpos]):
            continue
        _nt = int(SUB_CUT["loc"][int(_newd[_i])])
        assert _nt >= 0, "relocated target not on cutwA (STOP)"
        _ch.append((int(_pos_in_csr_cut[_eipos_cut[int(_gpos)]]), _nt))
    for _jpos, _de in _d["pdst"].items():
        _nt = int(SUB_CUT["loc"][int(_de)])
        assert _nt >= 0, "partner target not on cutwA (STOP)"
        _ch.append((int(_pos_in_csr_cut[_eipos_cut[int(_jpos)]]), _nt))
    CH_CUT.append(dict(n_changed=len(_ch), changed=_ch))
assert len(CH_CUT) == 100

_cb0c, _cb1c = IX_CUT["START"][LC_CAR_CUT], IX_CUT["END"][LC_CAR_CUT]
assert _cb1c - _cb0c == N_OUT_CUT_PIN, (_cb0c, _cb1c, "SI menu size (STOP)")
_menu_cut = sorted(IX_CUT["T_L"][_cb0c:_cb1c])
assert float(min(_menu_cut)) > 0.0, "a first-hop cost of zero bits"
_relocc, _menuchkc = [], 0
for _ch in CH_CUT:
    _tg = list(IX_CUT["TGT0"])
    for _cidx, _nt in _ch["changed"]:
        _tg[int(IX_CUT["POS"][_cidx])] = _nt
    assert sorted(IX_CUT["T_L"][_cb0c:_cb1c]) == _menu_cut, "MENU MOVED"
    _relocc.append(int(sum(1 for _i in range(_cb0c, _cb1c)
                           if _tg[_i] != IX_CUT["TGT0"][_i])))
    _menuchkc += 1
assert _menuchkc == 100 and min(_relocc) >= 1, "menu/reloc guard (STOP)"
log(f"[CERT-MENUCUT] GREEN: the {N_OUT_CUT_PIN}-edge cutwA first-hop menu is "
    f"bit-identical in all 100 draws (median {float(np.median(_relocc)):.1f} "
    f"of {N_OUT_CUT_PIN} relocated) -> D_fh on cutwA is SELECTION, not "
    f"allocation, by construction")

# ---------------- REBIND the globals, call the UNCHANGED certified walkers -
START, END, L_L, T_L = (IX_CUT["START"], IX_CUT["END"],
                        IX_CUT["L_L"], IX_CUT["T_L"])
NL, POOLS_IDX, N_POOL = IX_CUT["NL"], IX_CUT["POOLS_IDX"], IX_CUT["N_POOL"]
TGT0_CUT = IX_CUT["TGT0"]

_dc, _sc = dijkstra_si(LC_CAR_CUT, TGT0_CUT)
SI_CAR_CUT = si_summary(_dc, _sc)
_dc1, _sc1, _fc1, _hc1 = dijkstra_si_fh(LC_CAR_CUT, TGT0_CUT)
_ncross = 0
for _i in POOLS_IDX:
    assert _dc[_i] == _dc1[_i] and _sc[_i] == _sc1[_i], (_i, "cut walker")
    _ncross += 2
CAR_CUT = fh_summary(_dc1, _sc1, _fc1, _hc1)
assert CAR_CUT is not None, "carrier reaches NO cutwA pool cell (STOP)"
assert CAR_CUT["si_mean"] == SI_CAR_CUT["si_mean"], "cut si_mean mismatch"
log(f"[L220] cutwA carrier: reach {CAR_CUT['n_reach']}/{N_POOL} | si "
    f"{CAR_CUT['si_mean']:.4f} = fh {CAR_CUT['fh_mean']:.4f} + rem "
    f"{CAR_CUT['rem_mean']:.4f} | fh/si {CAR_CUT['fh_share_of_si']:.4f} | "
    f"hops {CAR_CUT['hop_mean']:.3f} | distinct fh "
    f"{CAR_CUT['n_distinct_first_hops']}")

NULL_CUT = []
for _k, _ch in enumerate(CH_CUT):
    _tg = list(TGT0_CUT)
    for _cidx, _nt in _ch["changed"]:
        _tg[int(IX_CUT["POS"][_cidx])] = _nt
    _d0, _s0 = dijkstra_si(LC_CAR_CUT, _tg)
    _d1, _s1, _f1, _h1 = dijkstra_si_fh(LC_CAR_CUT, _tg)
    for _i in POOLS_IDX:
        assert _d0[_i] == _d1[_i] and _s0[_i] == _s1[_i], (_k, _i, "cut null")
        _ncross += 2
    _sm = fh_summary(_d1, _s1, _f1, _h1)
    assert _sm is not None, (_k, "unreachable cutwA draw")
    NULL_CUT.append(_sm)
    if _k == 0:
        log(f"[L220] cut draw 0: si {_sm['si_mean']:.4f} = fh "
            f"{_sm['fh_mean']:.4f} + rem {_sm['rem_mean']:.4f}")
assert len(NULL_CUT) == 100
log(f"[CERT-WALKCUT] GREEN {_ncross} EXACT equalities on cutwA between the "
    f"certified dijkstra_si and the first-hop walker (carrier + 100 draws)")

# the 35-actor cohort on cutwA (DESCRIPTIVE, registered as such)
COH_CUT, _absent = {}, []
_gi_of = {"carrier": GI_CARRIER, "twin": GI_TWIN4}
for _nm in F4["cohort"]["all_actors"]:
    if _nm in _gi_of:
        _gi = _gi_of[_nm]
    elif _nm == "mirror_928":
        _gi = GI_MIRROR
    else:
        _gi = int(_nm.rsplit("_", 1)[1])
    if not bool(keep_wA[_gi]):
        _absent.append(_nm)
        COH_CUT[_nm] = None
        continue
    _lc = int(SUB_CUT["loc"][_gi])
    _d, _s, _f, _h = dijkstra_si_fh(_lc, TGT0_CUT)
    COH_CUT[_nm] = fh_summary(_d, _s, _f, _h)

# ---------------- RESTORE + CERT-REBIND (HALTING) --------------------------
START, END, L_L, T_L = _START0, _END0, _L0, _T0
NL, N_POOL, POOLS_IDX = _NL0, _NP0, _PI0
_d2, _s2 = dijkstra_si(LC_CAR, TGT0)
_nreb = 0
for _j, _i in enumerate(POOLS_IDX):
    assert _d2[_i] == _ref_pool[_j][0], (_i, "REBIND leaked dist (STOP)")
    assert _s2[_i] == _ref_pool[_j][1], (_i, "REBIND leaked si (STOP)")
    _nreb += 2
assert NL == _NL0 and N_POOL == _NP0 and len(START) == _NL0
log(f"[CERT-REBIND] GREEN {_nreb} BIT-IDENTICAL f4wA values after rebinding "
    f"the globals to cutwA and back -> the rebind is reversible, nothing "
    f"leaked between substrates")

# ---------------- the DECOMPOSITION on cutwA (primary) ---------------------
SHARE_HI_220, SHARE_LO_220 = 0.60, 0.40
_sinc = np.array([r["si_mean"] for r in NULL_CUT], float)
_fhnc = np.array([r["fh_mean"] for r in NULL_CUT], float)
_remnc = np.array([r["rem_mean"] for r in NULL_CUT], float)
_hopnc = np.array([r["hop_mean"] for r in NULL_CUT], float)
_distnc = np.array([r["dist_mean"] for r in NULL_CUT], float)
_rchnc = np.array([r["n_reach"] for r in NULL_CUT], float)
_ndfhc = np.array([r["n_distinct_first_hops"] for r in NULL_CUT], float)
assert np.isfinite(_sinc).all() and np.isfinite(_fhnc).all(), "non-finite null"

Dc_total = CAR_CUT["si_mean"] - float(_sinc.mean())
Dc_fh = CAR_CUT["fh_mean"] - float(_fhnc.mean())
Dc_rem = CAR_CUT["rem_mean"] - float(_remnc.mean())
_additc = abs(Dc_total - (Dc_fh + Dc_rem))
assert _additc < 1e-9, (_additc, "cutwA decomposition NOT additive (STOP)")

_degen = (not np.isfinite([Dc_total, Dc_fh, Dc_rem]).all()
          or Dc_total <= 0 or CAR_CUT["n_reach"] <= IX_CUT["N_POOL"] // 2)
if _degen:
    BR220 = "T_DEGENERATE"
    share_fh_cut = None
else:
    share_fh_cut = Dc_fh / Dc_total
    if share_fh_cut <= SHARE_LO_220:
        BR220 = "T_TRANSPORTS"
    elif share_fh_cut >= SHARE_HI_220:
        BR220 = "T_INVERTS"
    else:
        BR220 = "T_SPLIT"

_si_pct_cut = _pct(CAR_CUT["si_mean"], _sinc)
o["L220_primary"] = dict(
    branch=BR220, share_fh=share_fh_cut,
    share_rem=(None if share_fh_cut is None else 1.0 - share_fh_cut),
    bars=dict(transports_if_share_le=SHARE_LO_220,
              inverts_if_share_ge=SHARE_HI_220,
              degenerate_if_reach_le=IX_CUT["N_POOL"] // 2),
    D_total_bits=Dc_total, D_fh_bits=Dc_fh, D_rem_bits=Dc_rem,
    additivity_abs_err=_additc,
    carrier=CAR_CUT,
    null_mean=dict(si=float(_sinc.mean()), fh=float(_fhnc.mean()),
                   rem=float(_remnc.mean()), hop=float(_hopnc.mean()),
                   dist=float(_distnc.mean()), reach=float(_rchnc.mean())),
    null_median=dict(si=float(np.median(_sinc)), fh=float(np.median(_fhnc)),
                     rem=float(np.median(_remnc)),
                     hop=float(np.median(_hopnc)),
                     dist=float(np.median(_distnc)),
                     reach=float(np.median(_rchnc))),
    null_spread=dict(si_p05=float(np.percentile(_sinc, 5)),
                     si_p95=float(np.percentile(_sinc, 95)),
                     fh_p05=float(np.percentile(_fhnc, 5)),
                     fh_p95=float(np.percentile(_fhnc, 95)),
                     fh_sd=float(_fhnc.std(ddof=1)),
                     rem_p05=float(np.percentile(_remnc, 5)),
                     rem_p95=float(np.percentile(_remnc, 95)),
                     rem_sd=float(_remnc.std(ddof=1))),
    percentiles=dict(si=_si_pct_cut, fh=_pct(CAR_CUT["fh_mean"], _fhnc),
                     rem=_pct(CAR_CUT["rem_mean"], _remnc),
                     hop=_pct(CAR_CUT["hop_mean"], _hopnc),
                     dist=_pct(CAR_CUT["dist_mean"], _distnc),
                     reach=_pct(float(CAR_CUT["n_reach"]), _rchnc)),
    menu=dict(n_out_edges=N_OUT_CUT_PIN, log2_n_out=LOG2_OUT_CUT,
              menu_min_bits=float(min(_menu_cut)),
              menu_med_bits=float(np.median(_menu_cut)),
              menu_max_bits=float(max(_menu_cut)),
              invariant_across_draws=True,
              median_relocated_per_draw=float(np.median(_relocc)),
              carrier_n_distinct_first_hops=CAR_CUT["n_distinct_first_hops"],
              null_n_distinct_first_hops_med=float(np.median(_ndfhc))),
    substrate=dict(name="cutwA", n=SUB_CUT["n"], n_edges=SUB_CUT["n_edges"],
                   n_pool_cells=IX_CUT["N_POOL"], A_max=IX_CUT["AMAX"],
                   operator="g=1 anatomical |W_beta| (PREREG 0c)"))
log(f"[L220] {BR220}: cutwA D_total {Dc_total:+.4f} bits = fh {Dc_fh:+.4f} + "
    f"rem {Dc_rem:+.4f} -> share_fh "
    + ("na" if share_fh_cut is None else f"{share_fh_cut:.4f}")
    + f" | pct si {_si_pct_cut:.1f} fh {_pct(CAR_CUT['fh_mean'], _fhnc):.1f} "
      f"rem {_pct(CAR_CUT['rem_mean'], _remnc):.1f}")

# ---------------- the TRANSPORT table (the card's actual deliverable) ------
_f4p = F4["primary"]
_bl_f4 = _f4p["carrier"]["fh_mean"] - LOG2_OUT_F4
_bl_cut = CAR_CUT["fh_mean"] - LOG2_OUT_CUT
o["L220_transport"] = dict(
    rule=("PREREG 0b: a first-hop cost in bits is read against its OWN "
          "substrate's uniform-allocation baseline log2(out-degree), never "
          "against the other substrate's."),
    f4wA=dict(n_out=69, log2_n_out=LOG2_OUT_F4,
              si_mean=_f4p["carrier"]["si_mean"],
              fh_mean=_f4p["carrier"]["fh_mean"],
              rem_mean=_f4p["carrier"]["rem_mean"],
              fh_share_of_si=_f4p["carrier"]["fh_share_of_si"],
              fh_minus_log2_out=_bl_f4,
              n_reach=_f4p["carrier"]["n_reach"],
              n_distinct_first_hops=_f4p["carrier"]["n_distinct_first_hops"],
              hop_mean=_f4p["carrier"]["hop_mean"],
              share_fh=_f4p["share_fh"], D_total=_f4p["D_total_bits"],
              D_fh=_f4p["D_fh_bits"], D_rem=_f4p["D_rem_bits"],
              si_pct=_f4p["percentiles"]["si"],
              fh_pct=_f4p["percentiles"]["fh"],
              rem_pct=_f4p["percentiles"]["rem"],
              branch=_f4p["branch"]),
    cutwA=dict(n_out=N_OUT_CUT_PIN, log2_n_out=LOG2_OUT_CUT,
               si_mean=CAR_CUT["si_mean"], fh_mean=CAR_CUT["fh_mean"],
               rem_mean=CAR_CUT["rem_mean"],
               fh_share_of_si=CAR_CUT["fh_share_of_si"],
               fh_minus_log2_out=_bl_cut,
               n_reach=CAR_CUT["n_reach"],
               n_distinct_first_hops=CAR_CUT["n_distinct_first_hops"],
               hop_mean=CAR_CUT["hop_mean"],
               share_fh=share_fh_cut, D_total=Dc_total, D_fh=Dc_fh,
               D_rem=Dc_rem, si_pct=_si_pct_cut,
               fh_pct=_pct(CAR_CUT["fh_mean"], _fhnc),
               rem_pct=_pct(CAR_CUT["rem_mean"], _remnc),
               branch=BR220),
    delta=dict(
        d_fh_share_of_si=(CAR_CUT["fh_share_of_si"]
                          - _f4p["carrier"]["fh_share_of_si"]),
        d_share_fh=(None if share_fh_cut is None
                    else share_fh_cut - _f4p["share_fh"]),
        d_fh_minus_log2_out=_bl_cut - _bl_f4,
        d_si_mean=CAR_CUT["si_mean"] - _f4p["carrier"]["si_mean"],
        d_rem_mean=CAR_CUT["rem_mean"] - _f4p["carrier"]["rem_mean"],
        baseline_shift_bits=LOG2_OUT_CUT - LOG2_OUT_F4,
        bare_fh_difference=CAR_CUT["fh_mean"] - _f4p["carrier"]["fh_mean"]))
log(f"[L220] TRANSPORT: fh/si {_f4p['carrier']['fh_share_of_si']:.4f} (f4wA) "
    f"-> {CAR_CUT['fh_share_of_si']:.4f} (cutwA), d "
    f"{o['L220_transport']['delta']['d_fh_share_of_si']:+.4f}; share_fh "
    f"{_f4p['share_fh']:+.4f} -> "
    + ("na" if share_fh_cut is None else f"{share_fh_cut:+.4f}")
    + f"; fh-log2(out) {_bl_f4:+.4f} -> {_bl_cut:+.4f} (baseline shift "
      f"{LOG2_OUT_CUT - LOG2_OUT_F4:+.4f})")

# ---------------- the cohort on cutwA (DESCRIPTIVE) -----------------------
_famc = [v for k, v in COH_CUT.items()
         if k.startswith("fam") and v is not None]
_fshare = np.array([v["fh_share_of_si"] for v in _famc], float)
_fremc = np.array([v["rem_mean"] for v in _famc], float)
_ffhc = np.array([v["fh_mean"] for v in _famc], float)
_MIRC = COH_CUT.get("mirror_928")
o["L220_cohort"] = dict(
    note=("DESCRIPTIVE (registered): the 100 draws swap the CARRIER's "
          "out-edges, so they are not a null for any other source; a "
          "percentile against 35 is resolution-limited (L207)."),
    n_family=len(_famc), n_absent_from_cutwA=len(_absent), absent=_absent,
    carrier_fh_share_of_si=CAR_CUT["fh_share_of_si"],
    twin_fh_share_of_si=(None if COH_CUT.get("twin") is None
                         else COH_CUT["twin"]["fh_share_of_si"]),
    family_fh_share_med=float(np.median(_fshare)),
    family_fh_share_min=float(_fshare.min()),
    family_fh_share_max=float(_fshare.max()),
    family_fh_mean_med=float(np.median(_ffhc)),
    family_rem_mean_med=float(np.median(_fremc)),
    carrier_rem_rank=int(1 + sum(1 for k, v in COH_CUT.items()
                                 if k != "mirror_928" and v is not None
                                 and v["rem_mean"] < CAR_CUT["rem_mean"])),
    carrier_fh_rank=int(1 + sum(1 for k, v in COH_CUT.items()
                                if k != "mirror_928" and v is not None
                                and v["fh_mean"] < CAR_CUT["fh_mean"])),
    n_ranked=int(sum(1 for k, v in COH_CUT.items()
                     if k != "mirror_928" and v is not None)),
    mirror=dict(gi=GI_MIRROR, on_cutwA=bool(keep_wA[GI_MIRROR]),
                summary=_MIRC,
                share_gap_vs_carrier=(None if _MIRC is None else abs(
                    _MIRC["fh_share_of_si"] - CAR_CUT["fh_share_of_si"]))),
    f4wA_for_reference=dict(
        family_fh_share_med=F4["cohort"]["family_fh_share_med"],
        carrier_fh_share_of_si=F4["cohort"]["carrier_fh_share_of_si"],
        twin_fh_share_of_si=F4["cohort"]["twin_fh_share_of_si"]),
    all_actors=COH_CUT)
log(f"[L220] cohort cutwA: carrier fh-share {CAR_CUT['fh_share_of_si']:.3f} "
    f"vs family med {float(np.median(_fshare)):.3f} (f4wA family med "
    f"{F4['cohort']['family_fh_share_med']:.3f}); carrier rem rank "
    f"{o['L220_cohort']['carrier_rem_rank']}/"
    f"{o['L220_cohort']['n_ranked']}; absent from cutwA {len(_absent)}")

# ---------------- predictions, scored --------------------------------------
_q = {}
_q["P1_branch_T_TRANSPORTS"] = dict(
    registered="branch T_TRANSPORTS (share_fh(cutwA) <= 0.40)",
    measured=f"{BR220} share_fh "
             + ("na" if share_fh_cut is None else f"{share_fh_cut:.4f}"),
    correct=bool(BR220 == "T_TRANSPORTS"))
_q["P2_abs_share_fh_le_025"] = dict(
    registered="|share_fh(cutwA)| <= 0.25 (both signs admitted)",
    measured=("na" if share_fh_cut is None else f"{share_fh_cut:.4f}"),
    correct=bool(share_fh_cut is not None and abs(share_fh_cut) <= 0.25))
_q["P3_funnel_transports"] = dict(
    registered=f"cutwA n_distinct_first_hops <= 0.35*{N_OUT_CUT_PIN} = 28",
    measured=f"{CAR_CUT['n_distinct_first_hops']} of {N_OUT_CUT_PIN} "
             f"(null med {float(np.median(_ndfhc)):.1f})",
    correct=bool(CAR_CUT["n_distinct_first_hops"]
                 <= 0.35 * N_OUT_CUT_PIN))
_q["P4_si_pct_ge_95"] = dict(
    registered="carrier SI percentile on cutwA >= 95.0",
    measured=f"{_si_pct_cut:.1f}",
    correct=bool(_si_pct_cut >= 95.0))
_q["P5_fh_share_within_010"] = dict(
    registered="|fh_share_of_si(cutwA) - 0.2611188191551899| <= 0.10",
    measured=f"{CAR_CUT['fh_share_of_si']:.4f} (d "
             f"{CAR_CUT['fh_share_of_si'] - 0.2611188191551899:+.4f})",
    correct=bool(abs(CAR_CUT["fh_share_of_si"] - 0.2611188191551899) <= 0.10))
o["predictions"] = _q
o["predictions_score"] = f"{sum(1 for v in _q.values() if v['correct'])} of 5"

o["certification"] = dict(
    inherited_free=["CERT-HEAD1 l151_static.py 1-319",
                    "CERT-HEAD2 l178_tail.py 7-149 (CERT-F4, gains, CSR, "
                    "20 pools)", "MID l206_mid.py",
                    "CERT-HEAD3 l178_tail.py 348-458 (CERT-REW, the draws)",
                    "CERT-HEAD4 l206_tail.py 22-263 (CERT-178 420 values, "
                    "lam1, depth sweep, CERT-NULL)",
                    "MID2 l211_mid2.py (heapq)",
                    "CERT-HEAD5 l206_tail.py 320-461 (the whole SI block)",
                    "CERT-HEAD6 l207_tail.py 26-146 (gain invariance, "
                    "build_sub, CERT-GEN)",
                    "CERT-211SL l211_tail.py 29-322 (CERT-SI, CERT-MENU, "
                    "dijkstra_si_fh/fh_summary, CERT-FH, the f4wA "
                    "decomposition and cohort; writer block CUT)"],
    CERT_211_leaves=_cert211[0],
    CERT_SIGEN_equalities=_ngen,
    CERT_REWCUT_checks=_nrw,
    CERT_MENUCUT_draws=_menuchkc,
    CERT_WALKCUT_equalities=_ncross,
    CERT_REBIND_equalities=_nreb,
    CERT_SI_leaves=_cert_si[0],
    CERT_FH_exact_equalities=_cert_fh,
    CERT_MENU_draws=_menu_chk,
    no_lab_module_imported=True,
    read_only_sources=FP_SRC)
for _p, _fp in FP_SRC.items():
    _st = _os220.stat(_p)
    assert (int(_st.st_size), int(_st.st_mtime_ns)) == _fp, (_p, "MUTATED")

o["limitations"] = [
    "TWO substrates (cutwA base, f4wA floor-4), ONE operator family "
    "(anatomical |W_beta|), ONE null family (degree-neutral destination "
    "swaps, seed 16943). L207's law: a deficit MAGNITUDE is null-specific "
    "and does not transport; this card tests transport of a dimensionless "
    "SHARE, not of a magnitude.",
    "the two substrates differ in BOTH edge set and the carrier's "
    "out-degree (80 vs 69), so bare first-hop bit magnitudes are reported "
    "only beside their own log2(out-degree) baselines (PREREG 0b).",
    "f4wA uses the certified G-scaled operator and cutwA its own g=1 "
    "operator; L and T are mathematically gain-invariant and the "
    "floating-point size of that choice is MEASURED in "
    "o['gain_noop_measured'], not assumed (PREREG 0c).",
    "the SI length transform divides by A_max (a domain choice, disclosed; "
    "the field normalises weights to (0,1] first) and ties in L are broken "
    "by heap order, not controlled -- inherited from L206 unchanged.",
    "the first-hop menu invariance (CERT-MENUCUT) makes D_fh a SELECTION "
    "effect among a fixed 80-edge menu BY CONSTRUCTION; it is NOT evidence "
    "about how the carrier allocates out-weight.",
    "the cutwA cohort and mirror legs are DESCRIPTIVE: the draws swap the "
    "carrier's edges and are not a null for another source.",
    "relation to L211 declared: this is L211's own deferred leg, cites "
    "L211, and does NOT re-bank L211's finding as independent evidence.",
]
o["pins"] = "ALL GREEN"
json.dump(o, open("l220/static.json", "w"), indent=1)
log("=" * 72)
log(f"L220 DONE {time.time()-t0:.0f}s | {BR220} | cutwA share_fh "
    + ("na" if share_fh_cut is None else f"{share_fh_cut:+.4f}")
    + f" vs f4wA {_f4p['share_fh']:+.4f} | fh/si {CAR_CUT['fh_share_of_si']:.4f}"
      f" vs {_f4p['carrier']['fh_share_of_si']:.4f} | CERT-211 {_cert211[0]} + "
      f"SIGEN {_ngen} + REWCUT {_nrw} + MENUCUT {_menuchkc} + WALKCUT "
      f"{_ncross} + REBIND {_nreb} | predictions {o['predictions_score']}")
