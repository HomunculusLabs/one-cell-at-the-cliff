# ================= L211 TAIL (appended by l211_build.py) =================
# Everything above this line is VERBATIM source:
#   l151_static.py 1-319, l178_tail.py 7-149, l206_mid.py,
#   l178_tail.py 348-458, l206_tail.py 22-263, l211_mid2.py,
#   l206_tail.py 320-461  <-- L206's SEARCH-INFORMATION block, re-run whole.
# So CERT-F4, the gains at float equality, the CSR orientation, the 20 pool
# sizes, CERT-REW (l169c P6), CERT-178's 420 anatomical values, the lam1
# power iteration, the depth-1..10 sweep and CERT-NULL have ALL re-run as
# free certification, and SI itself has been recomputed from scratch, before
# any L211 number is read.  PREREG: l211/PREREG.md (registered first).
# Writes l211/static.json ONLY. Zero rollouts, zero settles, zero dynamics.
import os as _os211

o["design"] = (
    "L211 is the hidden route the CARRIER's EDGES or its NEIGHBOURHOOD? "
    "Decompose L206's +3.675-bit search-information excess (pct 100.0) into "
    "the FIRST-HOP term -log2 T of the carrier's own chosen out-edge and the "
    "REMAINDER from its 69 targets onward, each against the SAME 100 "
    "degree-neutral destination-swap draws (seed 16943). PREREG l211/PREREG.md.")
o["prereg"] = "l211/PREREG.md"
with open("l211_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(11)])

FP_SRC = {}
for _p in ("l206/static.json", "l178/static.json"):
    _st = _os211.stat(_p)
    FP_SRC[_p] = (int(_st.st_size), int(_st.st_mtime_ns))

SHARE_HI, SHARE_LO = 0.60, 0.40
GI_MIRROR = 928

# ---------------- CERT-SI (halting): the card's required anchor -------------
# o["G2_search_information"] was just rebuilt by the verbatim L206 block.
# Every leaf of it must equal the STORED L206 block by float equality.
_S206 = json.load(open("l206/static.json"))
_stored_g2 = _S206["G2_search_information"]
_live_g2 = o["G2_search_information"]
_cert_si = [0]


def _cmp_leaf(a, b, path):
    if isinstance(a, dict):
        assert isinstance(b, dict), (path, "dict/non-dict")
        assert set(a) == set(b), (path, sorted(set(a) ^ set(b)))
        for k in sorted(a):
            _cmp_leaf(a[k], b[k], f"{path}/{k}")
        return
    if isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), (path, "list")
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp_leaf(x, y, f"{path}[{i}]")
        return
    if isinstance(a, float) or isinstance(b, float):
        assert float(a) == float(b), (path, repr(a), repr(b), "NOT float-equal")
    else:
        assert a == b, (path, repr(a), repr(b))
    _cert_si[0] += 1


_cmp_leaf(_live_g2, _stored_g2, "G2")
assert _cert_si[0] >= 150, ("CERT-SI too few leaves", _cert_si[0])
assert _live_g2["carrier"]["si_mean"] == 22.39317740345491, "carrier SI drift"
assert _live_g2["null_si_med"] == 18.71799427882452, "null SI med drift"
assert _live_g2["branch"] == "G2_SI_HIGH" and _live_g2["carrier_percentile"] == 100.0
log(f"[CERT-SI] GREEN {_cert_si[0]} stored L206 search-information values "
    f"reproduced by FLOAT EQUALITY (35 actors + null summary)")

# ---------------- CERT-MENU: the first-hop menu is INVARIANT ---------------
_cb0, _cb1 = START[LC_CAR], END[LC_CAR]
_menu_real = sorted(T_L[_cb0:_cb1])
assert len(_menu_real) == o["csr_orientation"]["out_edges"] == 69, \
    ("carrier out-edge count", len(_menu_real))
assert float(min(_menu_real)) > 0.0, "a first-hop cost of zero bits"
_menu_chk, _reloc = 0, []
for _ch in null_changed:
    _tg = list(TGT0)
    for _cidx, _nt in _ch["changed"]:
        _tg[int(_pos_in_sorted[_cidx])] = _nt
    assert sorted(T_L[_cb0:_cb1]) == _menu_real, "MENU MOVED (impossible)"
    _reloc.append(int(sum(1 for _i in range(_cb0, _cb1)
                          if _tg[_i] != TGT0[_i])))
    _menu_chk += 1
assert _menu_chk == 100
assert min(_reloc) >= 1, "a draw that relocated no carrier out-edge"
log(f"[CERT-MENU] GREEN: 69-edge first-hop menu bit-identical in all 100 "
    f"draws (median {float(np.median(_reloc)):.1f} of 69 carrier out-edges "
    f"relocated per draw) -> any first-hop effect is SELECTION, not allocation")

assert LC_CAR not in set(POOLS_IDX), "source is itself a pool cell"


# ---------------- the first-hop-tracking walker (gated by CERT-FH) ---------
def dijkstra_si_fh(src, tgt):
    """The certified dijkstra_si relaxation, verbatim in structure, carrying
    two extra inherited fields: the SI of the FIRST hop out of src, and the
    hop count. Gated by CERT-FH against the certified function itself."""
    INF = float("inf")
    dist = [INF] * NL
    si = [INF] * NL
    fh = [INF] * NL
    hop = [0] * NL
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
        hu = hop[u]
        for e in range(START[u], END[u]):
            v = tgt[e]
            if done[v]:
                continue
            nd = d + L_L[e]
            if nd < dist[v]:
                dist[v] = nd
                si[v] = su + T_L[e]
                fh[v] = T_L[e] if u == src else fu
                hop[v] = hu + 1
                push(h, (nd, v))
    return dist, si, fh, hop


def fh_summary(dist, si, fh, hop):
    pd = [dist[i] for i in POOLS_IDX]
    ps = [si[i] for i in POOLS_IDX]
    pf = [fh[i] for i in POOLS_IDX]
    ph = [hop[i] for i in POOLS_IDX]
    fin = [i for i, x in enumerate(pd) if x != float("inf")]
    if not fin:
        return None
    sim = float(np.mean([ps[i] for i in fin]))
    fhm = float(np.mean([pf[i] for i in fin]))
    return dict(
        n_reach=len(fin), si_mean=sim, fh_mean=fhm, rem_mean=sim - fhm,
        fh_share_of_si=fhm / sim, hop_mean=float(np.mean([ph[i] for i in fin])),
        dist_mean=float(np.mean([pd[i] for i in fin])),
        n_distinct_first_hops=int(len(set(round(pf[i], 12) for i in fin))),
        fh_min=float(min(pf[i] for i in fin)),
        fh_max=float(max(pf[i] for i in fin)))


# ---------------- CERT-FH (halting): exact equality vs the certified walker -
_cert_fh = 0
for _nm, _lc in (("carrier", LC_CAR), ("twin", LC_TWIN)):
    _d0, _s0 = dijkstra_si(_lc, TGT0)
    _d1, _s1, _f1, _h1 = dijkstra_si_fh(_lc, TGT0)
    for _i in POOLS_IDX:
        assert _d0[_i] == _d1[_i], (_nm, _i, "dist not EXACTLY equal")
        assert _s0[_i] == _s1[_i], (_nm, _i, "si not EXACTLY equal")
        _cert_fh += 2
    _sm = fh_summary(_d1, _s1, _f1, _h1)
    assert _sm["si_mean"] == _live_g2[_nm]["si_mean"], (_nm, "si_mean drift")
    assert _sm["dist_mean"] == _live_g2[_nm]["dist_mean"], (_nm, "dist drift")
    _cert_fh += 2
log(f"[CERT-FH] GREEN actors: {_cert_fh} EXACT equalities "
    f"(carrier+twin pool dist/si) vs the certified dijkstra_si")

# ---------------- the 100 draws, both walkers, exact-equality gated --------
NULL_FH = []
for _k, _ch in enumerate(null_changed):
    _tg = list(TGT0)
    for _cidx, _nt in _ch["changed"]:
        _tg[int(_pos_in_sorted[_cidx])] = _nt
    _d0, _s0 = dijkstra_si(LC_CAR, _tg)
    _d1, _s1, _f1, _h1 = dijkstra_si_fh(LC_CAR, _tg)
    for _i in POOLS_IDX:
        assert _d0[_i] == _d1[_i], (_k, _i, "null dist not EXACTLY equal")
        assert _s0[_i] == _s1[_i], (_k, _i, "null si not EXACTLY equal")
        _cert_fh += 2
    _sm = fh_summary(_d1, _s1, _f1, _h1)
    assert _sm is not None, (_k, "unreachable draw")
    NULL_FH.append(_sm)
    if _k == 0:
        log(f"[L211] draw 0: si {_sm['si_mean']:.4f} = fh {_sm['fh_mean']:.4f} "
            f"+ rem {_sm['rem_mean']:.4f}")
assert len(NULL_FH) == 100
# the rebuilt draws must reproduce L206's own stored null summary
_sin211 = np.array([r["si_mean"] for r in NULL_FH], float)
assert float(np.median(_sin211)) == _live_g2["null_si_med"], "null med drift"
assert float(np.percentile(_sin211, 5)) == _live_g2["null_si_p05"], "p05 drift"
assert float(np.percentile(_sin211, 95)) == _live_g2["null_si_p95"], "p95 drift"
_cert_fh += 3
log(f"[CERT-FH] GREEN all 100 draws: {_cert_fh} EXACT equalities total; "
    f"rebuilt null median/p05/p95 float-identical to the certified block")

# ---------------- the DECOMPOSITION (primary) ------------------------------
_dcar, _scar, _fcar, _hcar = dijkstra_si_fh(LC_CAR, TGT0)
CAR = fh_summary(_dcar, _scar, _fcar, _hcar)
assert CAR["si_mean"] == 22.39317740345491, "carrier si_mean drift (STOP)"

_fhn = np.array([r["fh_mean"] for r in NULL_FH], float)
_remn = np.array([r["rem_mean"] for r in NULL_FH], float)
_hopn = np.array([r["hop_mean"] for r in NULL_FH], float)
_distn = np.array([r["dist_mean"] for r in NULL_FH], float)
_ndfh = np.array([r["n_distinct_first_hops"] for r in NULL_FH], float)

D_total = CAR["si_mean"] - float(_sin211.mean())
D_fh = CAR["fh_mean"] - float(_fhn.mean())
D_rem = CAR["rem_mean"] - float(_remn.mean())
_addit = abs(D_total - (D_fh + D_rem))
assert _addit < 1e-9, (_addit, "decomposition is NOT additive (STOP)")

if (not np.isfinite([D_total, D_fh, D_rem]).all()) or D_total <= 0:
    BRANCH = "B_DEGENERATE"
    share_fh = None
else:
    share_fh = D_fh / D_total
    if share_fh >= SHARE_HI:
        BRANCH = "B_FIRSTHOP"
    elif share_fh <= SHARE_LO:
        BRANCH = "B_REMAINDER"
    else:
        BRANCH = "B_SPLIT"


def _pct(v, arr):
    return float((np.asarray(arr) < v).mean() * 100.0)


o["L211_primary"] = dict(
    branch=BRANCH,
    share_fh=share_fh,
    share_rem=(None if share_fh is None else 1.0 - share_fh),
    bars=dict(firsthop_if_share_ge=SHARE_HI, remainder_if_share_le=SHARE_LO),
    D_total_bits=D_total, D_fh_bits=D_fh, D_rem_bits=D_rem,
    additivity_abs_err=_addit,
    carrier=CAR,
    null_mean=dict(si=float(_sin211.mean()), fh=float(_fhn.mean()),
                   rem=float(_remn.mean()), hop=float(_hopn.mean()),
                   dist=float(_distn.mean())),
    null_median=dict(si=float(np.median(_sin211)), fh=float(np.median(_fhn)),
                     rem=float(np.median(_remn)), hop=float(np.median(_hopn)),
                     dist=float(np.median(_distn))),
    null_spread=dict(fh_p05=float(np.percentile(_fhn, 5)),
                     fh_p95=float(np.percentile(_fhn, 95)),
                     fh_sd=float(_fhn.std(ddof=1)),
                     rem_p05=float(np.percentile(_remn, 5)),
                     rem_p95=float(np.percentile(_remn, 95)),
                     rem_sd=float(_remn.std(ddof=1))),
    percentiles=dict(fh=_pct(CAR["fh_mean"], _fhn),
                     rem=_pct(CAR["rem_mean"], _remn),
                     si=_pct(CAR["si_mean"], _sin211),
                     hop=_pct(CAR["hop_mean"], _hopn),
                     dist=_pct(CAR["dist_mean"], _distn)),
    menu=dict(n_out_edges=len(_menu_real),
              log2_n_out=float(np.log2(len(_menu_real))),
              menu_min_bits=float(min(_menu_real)),
              menu_med_bits=float(np.median(_menu_real)),
              menu_max_bits=float(max(_menu_real)),
              invariant_across_draws=True,
              carrier_n_distinct_first_hops=CAR["n_distinct_first_hops"],
              null_n_distinct_first_hops_med=float(np.median(_ndfh))),
    reading=("D_fh can only be SELECTION among a fixed 69-edge menu (the "
             "null relocates destinations with the weight travelling with "
             "its source, so the menu is bit-identical in every draw) — "
             "registered in the PREREG before measuring."))
log(f"[L211] {BRANCH}: D_total {D_total:+.4f} bits = fh {D_fh:+.4f} + rem "
    f"{D_rem:+.4f} -> share_fh "
    + ("na" if share_fh is None else f"{share_fh:.3f}")
    + f" | pct fh {_pct(CAR['fh_mean'], _fhn):.1f} rem "
      f"{_pct(CAR['rem_mean'], _remn):.1f}")

# ---------------- the 35-actor cohort + the mirror (descriptive) -----------
assert bool(keep_f4[GI_MIRROR]), "mirror gi 928 not in the f4wA substrate"
LC_MIR = int(loc_f4[GI_MIRROR])
_src_all = dict(ACTORS)
_src_all["mirror_928"] = LC_MIR
COH = {}
for _nm, _lc in _src_all.items():
    _d, _s, _f, _h = dijkstra_si_fh(_lc, TGT0)
    _sm = fh_summary(_d, _s, _f, _h)
    COH[_nm] = _sm
    if _nm in _live_g2["all_actors"] and _sm is not None:
        _st = _live_g2["all_actors"][_nm]
        if _st["si_mean"] is not None:
            assert _sm["si_mean"] == _st["si_mean"], (_nm, "cohort si drift")
            assert _sm["dist_mean"] == _st["dist_mean"], (_nm, "cohort dist")
_fam = [v for k, v in COH.items()
        if k.startswith("fam") and v is not None]
_fam_share = np.array([v["fh_share_of_si"] for v in _fam], float)
_fam_fh = np.array([v["fh_mean"] for v in _fam], float)
_fam_rem = np.array([v["rem_mean"] for v in _fam], float)
MIR = COH["mirror_928"]
_mir_share_gap = (None if MIR is None
                  else abs(MIR["fh_share_of_si"] - CAR["fh_share_of_si"]))
o["L211_cohort"] = dict(
    note=("DESCRIPTIVE. The 100 draws swap the CARRIER's out-edges, so they "
          "are not a null for any other source; the cohort is read as a "
          "cohort (L207: a percentile against 35 is resolution-limited)."),
    n_family=len(_fam),
    carrier_fh_share_of_si=CAR["fh_share_of_si"],
    twin_fh_share_of_si=COH["twin"]["fh_share_of_si"],
    family_fh_share_med=float(np.median(_fam_share)),
    family_fh_share_min=float(_fam_share.min()),
    family_fh_share_max=float(_fam_share.max()),
    family_fh_mean_med=float(np.median(_fam_fh)),
    family_rem_mean_med=float(np.median(_fam_rem)),
    carrier_rem_rank_of_35=int(1 + sum(
        1 for k, v in COH.items()
        if k != "mirror_928" and v is not None
        and v["rem_mean"] < CAR["rem_mean"])),
    carrier_fh_rank_of_35=int(1 + sum(
        1 for k, v in COH.items()
        if k != "mirror_928" and v is not None
        and v["fh_mean"] < CAR["fh_mean"])),
    mirror=dict(gi=GI_MIRROR, local=LC_MIR, summary=MIR,
                share_gap_vs_carrier=_mir_share_gap,
                n_out_edges=int((csr_cols == LC_MIR).sum())),
    all_actors=COH)
log(f"[L211] cohort: carrier fh-share {CAR['fh_share_of_si']:.3f} vs family "
    f"med {float(np.median(_fam_share)):.3f}; carrier rem rank "
    f"{o['L211_cohort']['carrier_rem_rank_of_35']}/35, fh rank "
    f"{o['L211_cohort']['carrier_fh_rank_of_35']}/35; mirror 928 share "
    + ("na" if MIR is None else f"{MIR['fh_share_of_si']:.3f}"))

# ---------------- predictions, scored ---------------------------------------
_q = {}
_q["Q211-1_branch_B_REMAINDER_and_share_in_0_025"] = dict(
    registered="B_REMAINDER with share_fh in [0.00, 0.25]",
    measured=f"{BRANCH} share_fh "
             + ("na" if share_fh is None else f"{share_fh:.4f}"),
    correct=bool(BRANCH == "B_REMAINDER" and share_fh is not None
                 and 0.0 <= share_fh <= 0.25))
_q["Q211-2_fh_inside_rem_at_ceiling"] = dict(
    registered="fh pct in (5,95) AND rem pct >= 99",
    measured=f"fh pct {_pct(CAR['fh_mean'], _fhn):.1f}, rem pct "
             f"{_pct(CAR['rem_mean'], _remn):.1f}",
    correct=bool(5.0 < _pct(CAR["fh_mean"], _fhn) < 95.0
                 and _pct(CAR["rem_mean"], _remn) >= 99.0))
_q["Q211-3_fh_above_log2_69_and_share_of_si_below_045"] = dict(
    registered="carrier fh_mean > 6.1085 bits AND fh/si < 0.45",
    measured=f"fh_mean {CAR['fh_mean']:.4f}, fh/si {CAR['fh_share_of_si']:.4f}",
    correct=bool(CAR["fh_mean"] > float(np.log2(69))
                 and CAR["fh_share_of_si"] < 0.45))
_q["Q211-4_carrier_paths_also_longer_in_L"] = dict(
    registered="carrier dist_mean > null median dist_mean",
    measured=f"{CAR['dist_mean']:.4f} vs {float(np.median(_distn)):.4f}",
    correct=bool(CAR["dist_mean"] > float(np.median(_distn))))
_q["Q211-5_mirror_share_within_015_of_carrier"] = dict(
    registered="|mirror share - carrier share| <= 0.15",
    measured=("na" if _mir_share_gap is None else f"{_mir_share_gap:.4f}"),
    correct=bool(_mir_share_gap is not None and _mir_share_gap <= 0.15))
o["predictions"] = _q
o["predictions_score"] = f"{sum(1 for v in _q.values() if v['correct'])} of 5"

o["certification"] = dict(
    inherited_free=["CERT-HEAD1 l151_static.py 1-319", "CERT-HEAD2 l178_tail.py "
                    "7-149 (CERT-F4, gains, CSR, 20 pools)",
                    "MID l206_mid.py", "CERT-HEAD3 l178_tail.py 348-458 "
                    "(CERT-REW, the 100 draws)",
                    "CERT-HEAD4 l206_tail.py 22-263 (CERT-178 420 values, "
                    "lam1, depth sweep, CERT-NULL)",
                    "MID2 l211_mid2.py (heapq)",
                    "CERT-HEAD5 l206_tail.py 320-461 (the whole SI block)"],
    CERT_SI_leaves=_cert_si[0],
    CERT_FH_exact_equalities=_cert_fh,
    CERT_MENU_draws=_menu_chk,
    no_lab_module_imported=True,
    read_only_sources=FP_SRC)
for _p, _fp in FP_SRC.items():
    _st = _os211.stat(_p)
    assert (int(_st.st_size), int(_st.st_mtime_ns)) == _fp, (_p, "SOURCE MUTATED")

o["limitations"] = [
    "ONE substrate (f4wA floor-4), ONE operator (A = |g*W_beta|), ONE null "
    "family (degree-neutral destination swaps, seed 16943) — L207's law: a "
    "deficit magnitude is null-specific and does not transport.",
    "the SI length transform divides by A_max (a domain choice, disclosed; "
    "the field normalises weights to (0,1] first) and SI ties in L are "
    "broken by heap order, not controlled.",
    "the first-hop menu invariance makes D_fh a SELECTION effect by "
    "construction; it is NOT evidence about how the carrier allocates "
    "out-weight, and the verdict says so.",
    "the cohort and mirror legs are DESCRIPTIVE: the draws swap the "
    "carrier's edges and are not a null for another source.",
    "the cutwA (unfloored) transport leg of the card is DEFERRED, declared "
    "in the PREREG and appended to the queue, not silently dropped.",
    "relation to L219 declared: L219 asks target-choice-vs-quality in the "
    "left-Perron currency; whichever runs second cites the first and does "
    "NOT re-bank the finding as independent evidence.",
]
o["pins"] = "ALL GREEN"
json.dump(o, open("l211/static.json", "w"), indent=1)
log("=" * 72)
log(f"L211 DONE {time.time()-t0:.0f}s | {BRANCH} | share_fh "
    + ("na" if share_fh is None else f"{share_fh:.3f}")
    + f" | D_total {D_total:+.4f} = fh {D_fh:+.4f} + rem {D_rem:+.4f} | "
      f"CERT-SI {_cert_si[0]} + CERT-FH {_cert_fh} + CERT-MENU {_menu_chk} | "
      f"predictions {o['predictions_score']}")
