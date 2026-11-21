"""L169b2 build: count-asserted transform of l169_run.py -> l169b2_run.py.

Adds THREE floor-4 arms (f4wA = closure@floor4 minus ng4[:20]; f4ng =
minus ng4[:21], the carrier included at f4 rank 21; f4tw = minus
ng4[:20] + the f4 mass-twin gi 290) with FRESH per-arm af-matched
bisects, re-derives the floor-4 ladder in-run and asserts it against
l169b/static.json (CERT-3), restricts settle_states to the arm under
bisect (L139 spectator law; certified by the four stored-form bisects
landing EXACT = CERT-2/C0-SUB), swaps the batch to B36 3449-3464,
repoints every OUTPUT path to l169b2/, adds l169's npzs to the absence
list, and appends FC-169 (CERT-1 forward chain on the 9 inherited arms),
C0-NT(b2) and the f4 P-af report.

No arm removed. Every rep count-asserted on FULL indentation (l123 law);
shared lines pinned across ALL true sites (the noise dict lives in THREE
loops). Residual scan over CODE lines with an explicit input whitelist
(l126 law: whitelist by line context, never by token).
"""
import py_compile
import re

SRC = "l169_run.py"
DST = "l169b2_run.py"
s = open(SRC).read()
reps = []


def rep(old, new, n=1):
    c = s.count(old)
    assert c == n, (f"COUNT MISS {c} != {n}", old[:110])
    reps.append((old, new, n))
    return None


# ---- 1. header docstring opener (lineage prose below retained) ----
rep('''"""L169 run: pre-posting control (a), the GAIN-SWAP 2x2. PREREG
l169/PREREG.md FIRST (registered before this build). NEW ARMS: wAgN =''',
    '''"""L169b2 run: pre-posting control (b2), the FLOOR-4 DYNAMIC arm.
PREREG l169b2/PREREG.md FIRST (registered before this build). NEW ARMS:
f4wA / f4ng / f4tw = the closure node set VERBATIM with a pair-level
synapse floor of 4 on the EDGES (the stored l146 ladder convention), cut
at the f4-re-derived window: ng4[:20] (carrier intact), ng4[:21] (carrier
DNp33-L gi 1110, f4 rank 21) and ng4[:20]+gi 290 (the f4 mass-twin
DNpe005-R, rank 22, gap 2.4e-05). Fresh per-arm bisects, never ported.
CERT-1 FC-169 forward chain on the 9 inherited arms vs l169/raw_l169.npz;
CERT-2 = the four stored-form bisects EXACT (also certifies the
settle-subset); CERT-3 = the in-run f4 ladder == l169b/static.json F3.
FRESH B36 3449-3464. Stage-(a) prose retained below for lineage.

L169 run (stage a): the GAIN-SWAP 2x2. NEW ARMS: wAgN =''')

# ---- 2. ARMS + GAIN dicts ----
rep('''ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
        "eMotBot5", "wAgN", "n25gW"]''',
    '''ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
        "eMotBot5", "wAgN", "n25gW", "f4wA", "f4ng", "f4tw"]''')
rep('''            wAgN=None, n25gW=None)  # silW/swap arms below''',
    '''            wAgN=None, n25gW=None,
            f4wA=None, f4ng=None, f4tw=None)  # silW/swap/f4 arms below''')

# ---- 3. batch ----
rep('''B35 = list(range(3417, 3433))  # fresh (B34 = l154; lineage in PREREG)''',
    '''B36 = list(range(3449, 3465))  # fresh (B35 = l169 stage a; key-scanned
# absent from all 81 stored raw npzs before registration, L157 rule)''')
rep('''SEEDS = ANCH + B35                  # anchors FIRST: early wiring verdict
FRESH = B35''',
    '''SEEDS = ANCH + B36                  # anchors FIRST: early wiring verdict
FRESH = B36''')
rep('''    assert not any(f"mm_full_{s}" in _zp.files for s in B35), \\
        ("B35 collides with " + _p + " (STOP)")
log(f"B35 absence across {len(_prevs)} stored npzs: PASS")''',
    '''    assert not any(f"mm_full_{s}" in _zp.files for s in B36), \\
        ("B36 collides with " + _p + " (STOP)")
log(f"B36 absence across {len(_prevs)} stored npzs: PASS")''')

# ---- 4. the floor-4 derivation + arm plumbing (one block, before AMPA) ----
rep('''AMPA = np.zeros(WIN, np.float64)''',
    '''# ---- L169 (b2): FLOOR-4 DYNAMIC arms. PREREG l169b2/PREREG.md FIRST.
# Registered convention: node set = keep_new VERBATIM, edges filtered by
# pair-level summed syn_count >= 4 — the SAME convention the stored l146
# ladder used, so the (b1) static pins apply unchanged.
S169B = json.load(open("l169b/static.json"))
F4_STAT = S169B["forms"]["F3_fully_rederived"]
FLOOR = 4
# the base twin is not named in this script's lineage (l169 only pins the
# carrier) — re-derive it from the BASE ladder instead of trusting a number
GI_TWIN = int(ng_desc[25])
assert GI_TWIN == 319, (GI_TWIN, "base ng rank 26 != DNpe025-R 319 (STOP)")
pm4 = w_syn >= FLOOR
drop4 = ~pm4                       # edge-level floor for build_e
_om4 = out_rows & cord_of_dst & pm4
outmass4 = np.zeros(Nall)
np.add.at(outmass4, src_all[_om4], np.abs(vals_all[_om4]))
_cm4 = outmass4[dn_new_g]
_tot4 = float(_cm4.sum())
_o4 = np.argsort(-_cm4)
_cum4 = np.cumsum(_cm4[_o4]) / _tot4
K4 = int(np.searchsorted(_cum4, 0.50) + 1)
heav4 = dn_new_g[_o4[:K4]]
ng4 = heav4[~is_glut[heav4]]
# CERT-3: in-run re-derivation == l169b static F3, field-for-field
assert K4 == F4_STAT["K"] == 73, (K4, "f4 K drift (STOP)")
assert int((~is_glut[heav4]).sum()) == F4_STAT["n_ng"] == 55
assert int(is_glut[heav4].sum()) == F4_STAT["n_glut"] == 18
_r_carrier = int(np.where(ng4 == GI_CARRIER)[0][0]) + 1
_r_twin319 = int(np.where(ng4 == GI_TWIN)[0][0]) + 1
assert _r_carrier == F4_STAT["carrier_rank"] == 21, (_r_carrier, "f4 rank")
assert _r_twin319 == F4_STAT["twin_rank"] == 33, (_r_twin319, "319 f4 rank")
_jac4 = (len(set(int(x) for x in heav) & set(int(x) for x in heav4))
         / len(set(int(x) for x in heav) | set(int(x) for x in heav4)))
assert round(_jac4, 4) == F4_STAT["jaccard_heavy"] == 0.9231, _jac4
_pref4 = {f"ng{_k}": round(float(outmass4[ng4[:_k]].sum() / _tot4), 4)
          for _k in (19, 24, 25, 29)}
assert _pref4 == F4_STAT["prefix_mass_removed"], (_pref4, "f4 prefix mass")
assert int((emask_n & pm4).sum()) == F4_STAT["closure_edges"] == 472095
assert int((emask_wA & pm4).sum()) == F4_STAT["wA_edges"] == 469256
GI_F4TWIN = int(ng4[21])           # f4 rank 22 = the mass-nearest twin
assert GI_F4TWIN == 290, (GI_F4TWIN, "f4 twin != DNpe005-R gi 290 (STOP)")
_gap4 = abs(float(outmass4[GI_F4TWIN] - outmass4[GI_CARRIER]) / _tot4)
assert round(_gap4, 6) == 2.4e-05, (_gap4, "f4 twin mass gap drift (STOP)")
log(f"CERT-3 GREEN: f4 ladder K {K4} | carrier rank {_r_carrier} | "
    f"319 rank {_r_twin319} | f4 twin gi {GI_F4TWIN} gap {_gap4:.2e}")

F4_ARMS = ("f4wA", "f4ng", "f4tw")
F4_DROP = {"f4wA": np.sort(ng4[:20]),
           "f4ng": np.sort(ng4[:21]),
           "f4tw": np.sort(np.concatenate([ng4[:20], ng4[21:22]]))}
_sw, _sn, _st2 = (set(int(x) for x in F4_DROP["f4wA"]),
                  set(int(x) for x in F4_DROP["f4ng"]),
                  set(int(x) for x in F4_DROP["f4tw"]))
assert GI_CARRIER not in _sw and GI_CARRIER in _sn, "f4 XOR design broken"
assert GI_CARRIER not in _st2 and GI_F4TWIN in _st2, "f4 twin arm broken"
assert _sw < _sn and len(_sn) == 21 and len(_st2) == 21, "f4 nesting broken"
assert _sn != _st2, "f4ng == f4tw (STOP)"
F4_KEEP, F4_LOC, F4_OLDPOS, F4_KEPTNEW, F4_KEPTMASK, F4_POSINNEW = (
    {}, {}, {}, {}, {}, {})
for _fa in F4_ARMS:
    _k4 = keep_new.copy()
    _k4[F4_DROP[_fa]] = False
    assert int(_k4.sum()) == int(keep_new.sum()) - len(F4_DROP[_fa])
    assert not np.isin(dng100_all, F4_DROP[_fa]).any(), (_fa, "DNg100 dropped")
    _lc4 = -np.ones(Nall, np.int64)
    _lc4[_k4] = np.arange(int(_k4.sum()))
    _W4 = build_e(_k4, drop4)
    assert int(_W4.values().numel()) == int(
        (_k4[src_all] & _k4[dst_all] & pm4).sum()), (_fa, "f4 edge count")
    F4_KEEP[_fa], F4_LOC[_fa] = _k4, _lc4
    POOLS[_fa] = pools_for(_lc4, _k4)
    mech[_fa] = np.where(mech_mask[_k4])[0]
    _mt4 = np.zeros(int(_k4.sum()), bool)
    _mt4[_lc4[mg_all[_k4[mg_all]]]] = True
    motor[_fa] = _mt4
    dng100[_fa] = np.sort(_lc4[dng100_all[_k4[dng100_all]]])
    WB[_fa] = wb(_W4)
    N_OF[_fa] = int(_k4.sum())
    F4_OLDPOS[_fa] = _lc4[gi_old]
    F4_KEPTMASK[_fa] = _k4[new_g]
    F4_KEPTNEW[_fa] = _lc4[new_g[F4_KEPTMASK[_fa]]]
    F4_POSINNEW[_fa] = loc_n[np.where(_k4)[0]]
    assert len(mech[_fa]) == S92["mech"], (_fa, "mech size")
    assert len(dng100[_fa]) == S92["dng100"], (_fa, "dng100 size")
    for _pk4, _want4 in S92["pool_sizes"].items():
        assert len(POOLS[_fa][_pk4]) == _want4, (_fa, _pk4)
    log(f"{_fa}: n {N_OF[_fa]:,} | edges {int(WB[_fa].values().numel()):,} "
        f"| dropped {len(F4_DROP[_fa])}")
# static leg of C0-NT: the three f4 graphs are mutually distinct and none
# equals its base-substrate counterpart in edge count
assert len({(N_OF[_a4], int(WB[_a4].values().numel()))
            for _a4 in F4_ARMS}) == 3, "f4 graphs collide (STOP)"
assert int(WB["f4wA"].values().numel()) != int(
    WB["cutwA"].values().numel()), "floor never applied (STOP)"

AMPA = np.zeros(WIN, np.float64)''')

# ---- 5. settle_states: optional arm subset (L139 spectator law) ----
rep('''def settle_states(seed, gains):
    """Draw per l94 order; settle all arms under `gains[arm]`."""''',
    '''def settle_states(seed, gains, arms=None):
    """Draw per l94 order; settle `arms` (default ARMS) under `gains[arm]`.

    L139 spectator law applied to the BISECT: arms evolve independently and
    the two noise generators are drawn globally per step, so settling a
    subset is numerically a no-op for the arm being read. Certified by the
    four stored-form bisects landing EXACT (CERT-2 / C0-SUB in
    l169b2/PREREG.md) — never assumed.
    """
    arms = ARMS if arms is None else list(arms)''')
rep('''    I = {}
    for a in ARMS:
        Iv = torch.zeros(N_OF[a], 1)''',
    '''    I = {}
    for a in arms:
        Iv = torch.zeros(N_OF[a], 1)''')
rep('''        for a in ARMS:
            drive = torch.sparse.mm(WB[a], st[a]) * gains[a] + I[a]''',
    '''        for a in arms:
            drive = torch.sparse.mm(WB[a], st[a]) * gains[a] + I[a]''')

# ---- 6. Xc construction for the f4 arms (settle + rollout, 2 sites) ----
rep('''              wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),
              b65=Xo65.clone())
    I = {}''',
    '''              wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),
              b65=Xo65.clone())
    for _fa in F4_ARMS:
        _xf = torch.zeros(N_OF[_fa], 1)
        _xf[F4_OLDPOS[_fa]] = X0o
        _xf[F4_KEPTNEW[_fa]] = X0n[F4_KEPTMASK[_fa]]
        st[_fa] = _xf
    I = {}''')
rep('''             wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),
             b65=Xo65.clone())
    Iv = {}''',
    '''             wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),
             b65=Xo65.clone())
    for _fa in F4_ARMS:
        _xf = torch.zeros(N_OF[_fa], 1)
        _xf[F4_OLDPOS[_fa]] = X0o
        _xf[F4_KEPTNEW[_fa]] = X0n[F4_KEPTMASK[_fa]]
        X[_fa] = _xf
    Iv = {}''')

# ---- 7. noise dict: THREE loops (settle_states, rollout settle, rollout WIN)
rep('''                     wAgN=nzn[wA_pos_in_new], n25gW=nzn[p25_pos_in_new],
                     b65=nz_o)
''',
    '''                     wAgN=nzn[wA_pos_in_new], n25gW=nzn[p25_pos_in_new],
                     b65=nz_o)
        for _fa in F4_ARMS:
            noise[_fa] = nzn[F4_POSINNEW[_fa]]
''', 3)

# ---- 8. bisect: pass the f4 gains + restrict the settle to the read arm ----
rep('''                                  wAgN=g, n25gW=g))''',
    '''                                  wAgN=g, n25gW=g,
                                  **{_fa: g for _fa in F4_ARMS}),
                           arms=[arm])''')

# ---- 9. three FRESH f4 bisects (before the silW gain-identity line) ----
rep('''GAIN["silW"] = GAIN["cutwA"]  # graph-identity af-match (l144 A1 form)''',
    '''# ---- L169 (b2): FRESH af-matched bisects on the three floor-4 graphs.
# The floor deletes 27.14% of closure edges, so the bracket is widened;
# gains are NEVER ported between substrates (L118-L131 criteria).
f4_band_ok, f4_stairs, f4_af = {}, {}, {}
for _fa in F4_ARMS:
    lo_d, hi_d = 0.10, 0.40
    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _fa), bisect_af_mean(hi_d, _fa)
    log(f"{_fa} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo_d < AF_T < af_hi_d, f"{_fa} bracket fail"
    for it in range(24):
        mid = (lo_d + hi_d) / 2
        if bisect_af_mean(mid, _fa) < AF_T:
            lo_d = mid
        else:
            hi_d = mid
    GAIN[_fa] = lo_d
    _afd4 = bisect_af_mean(lo_d, _fa)
    f4_af[_fa] = _afd4
    f4_stairs[_fa] = abs(_afd4 - AF_T)
    f4_band_ok[_fa] = bool(f4_stairs[_fa] <= 5e-3)
    log(f"g_{_fa} {lo_d:.9f} | af_final {_afd4:.6f} | "
        f"|af-target| {f4_stairs[_fa]:.2e} (staircase)")
assert len({GAIN[_fa] for _fa in F4_ARMS}) == 3, "f4 gains collide (STOP)"
GAIN["silW"] = GAIN["cutwA"]  # graph-identity af-match (l144 A1 form)''')

# ---- 10. output paths (own partial, L120 direction) ----
rep('''if os.path.exists("l169/raw_partial.npz"):
    z = np.load("l169/raw_partial.npz")   # L120 direction fix (l150 loaded l148)''',
    '''if os.path.exists("l169b2/raw_partial.npz"):
    z = np.load("l169b2/raw_partial.npz")   # own partial (L120 direction)''')
rep('''    np.savez("l169/raw_partial.npz", **store)''',
    '''    np.savez("l169b2/raw_partial.npz", **store)''')
rep('''np.savez_compressed("l169/raw_l169.npz", K=K,''',
    '''np.savez_compressed("l169b2/raw_l169b2.npz", K=K,''')
rep('''log("raw_l169.npz checkpointed BEFORE analysis")''',
    '''log("raw_l169b2.npz checkpointed BEFORE analysis")''')
rep('''json.dump(out, open("l169/anchors_run.json", "w"), indent=1)''',
    '''json.dump(out, open("l169b2/anchors_run.json", "w"), indent=1)''')

# ---- 11. absence list gains l169's own npzs ----
rep('''          "l150/raw_partial.npz", "l154/raw_l154.npz",
          "l154/raw_partial.npz"]''',
    '''          "l150/raw_partial.npz", "l154/raw_l154.npz",
          "l154/raw_partial.npz",
          "l169/raw_l169.npz",
          "l169/raw_partial.npz"]''')

# ---- 12. savez: f4 gains, drops, floor ----
rep('''                    g_wAgN=GAIN["wAgN"], g_n25gW=GAIN["n25gW"],''',
    '''                    g_wAgN=GAIN["wAgN"], g_n25gW=GAIN["n25gW"],
                    g_f4wA=GAIN["f4wA"], g_f4ng=GAIN["f4ng"],
                    g_f4tw=GAIN["f4tw"], floor=FLOOR, K4=K4,
                    f4wA_drop=F4_DROP["f4wA"], f4ng_drop=F4_DROP["f4ng"],
                    f4tw_drop=F4_DROP["f4tw"],
                    f4_twin_gi=np.array([GI_F4TWIN]),''')

# ---- 13. FC-169 (CERT-1) + C0-NT(b2) + f4 P-af, before the out dict ----
rep('''# ---- C0-NT (PREREG): a swap arm bit-identical to its own-gain twin''',
    '''# ---- FC-169 (CERT-1): the 9 inherited arms must be BIT-IDENTICAL to
# l169/raw_l169.npz at 801/901 — adding arms consumes no generator draws,
# so any non-zero here is a stream break and the run is VOID.
z169c = np.load("l169/raw_l169.npz")
_arms169 = ("full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
            "eMotBot5", "wAgN", "n25gW")
assert all(f"{_k}_{_a}_801" in z169c.files for _k in C0A150_KEYS
           for _a in _arms169), "FC-169 coverage miss"
fc169 = {}
for s in (801, 901):
    for key in C0A150_KEYS:
        for a in _arms169:
            fc169[f"{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z169c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in _arms169:
        fc169[f"af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                   - float(z169c[f"af_{a}_{s}"]))
fc169_max = max(fc169.values())
fc169_pass = bool(all(v == 0.0 for v in fc169.values()))
log(f"FC-169 (9 arms x {len(C0A150_KEYS)} keys x 2 seeds) vs raw_l169: "
    f"{'PASS' if fc169_pass else 'FAIL'} (max {fc169_max:.1e})")
# ---- C0-NT(b2): every f4 arm separated from its base counterpart AND
# from the other two f4 arms; a bit-identical pair = floor/cut never
# entered the step loop = VOID (L35/L39 dead-channel class).
ntf4 = {}
for _fa, _bs in (("f4wA", "cutwA"), ("f4ng", "cutng25"), ("f4tw", "cutwA")):
    for s in (801, 901):
        ntf4[f"{_fa}_vs_{_bs}_{s}"] = float(np.abs(
            store[f"mm_{_fa}_{s}"] - store[f"mm_{_bs}_{s}"]).max())
for _p4, _q4 in (("f4wA", "f4ng"), ("f4wA", "f4tw"), ("f4ng", "f4tw")):
    for s in (801, 901):
        ntf4[f"{_p4}_vs_{_q4}_{s}"] = float(np.abs(
            store[f"mm_{_p4}_{s}"] - store[f"mm_{_q4}_{s}"]).max())
ntf4_pass = bool(all(v > 0.0 for v in ntf4.values()))
log(f"C0-NT(b2) f4 separation: {'PASS' if ntf4_pass else 'VOID'} "
    f"(min {min(ntf4.values()):.3e})")
# ---- P-af (PREREG): gate on the SETTLED staircase residual; the rollout
# af is a different quantity (6000 extra steps) and is DISCLOSED only.
paf4 = {}
for _fa in F4_ARMS:
    _v4 = [float(store[f"af_{_fa}_{s}"]) for s in FRESH]
    paf4[_fa] = dict(g=GAIN[_fa], bisect_af=f4_af[_fa],
                     stair=f4_stairs[_fa],
                     rollout_af_mean=float(np.mean(_v4)),
                     rollout_af_maxoff=float(np.max(np.abs(
                         np.array(_v4) - AF_T))))
    log(f"P-af {_fa}: g {GAIN[_fa]:.9f} | settled stair "
        f"{f4_stairs[_fa]:.2e} | rollout af mean "
        f"{paf4[_fa]['rollout_af_mean']:.5f} (max off "
        f"{paf4[_fa]['rollout_af_maxoff']:.2e})")
paf4_ok = bool(all(v["stair"] <= 5e-3 for v in paf4.values()))
log(f"P-af(b2) settled-staircase gate: {'PASS' if paf4_ok else 'DISCLOSE'}")
# ---- C0-NT (PREREG): a swap arm bit-identical to its own-gain twin''')

# ---- 14. out dict + c0a_pass gain the (b2) cells ----
rep('''           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass
                         and nt_pass))''',
    '''           g_f4wA=GAIN["f4wA"], g_f4ng=GAIN["f4ng"],
           g_f4tw=GAIN["f4tw"], floor=FLOOR, K4=K4,
           f4_twin_gi=GI_F4TWIN, f4_carrier_rank=_r_carrier,
           f4_stairs=f4_stairs, f4_band_ok=f4_band_ok,
           f4_edges={_a4: int(WB[_a4].values().numel()) for _a4 in F4_ARMS},
           f4_n={_a4: N_OF[_a4] for _a4 in F4_ARMS},
           fc169_max=fc169_max, fc169_pass=fc169_pass,
           ntf4=ntf4, ntf4_pass=ntf4_pass, paf4=paf4, paf4_ok=paf4_ok,
           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass
                         and nt_pass and fc169_pass and ntf4_pass))''')

# ---- apply ----
for old, new, n in reps:
    assert s.count(old) == n, ("DRIFT at apply", old[:80])
    s = s.replace(old, new)

# ---- residual scan over CODE lines (l126 law: whitelist by line context) --
INPUT_OK = ('z169c = np.load("l169/raw_l169.npz")',)
# docstring continuation lines describing STAGE (a)'s own batch are
# deliberate lineage prose (l121 label-honesty) and are not code
DOC_OK = ("third batch. FRESH B35 3417-3432. Arms: full, b65,",
          "fresh bisects asserted == l145 stored gains EXACT). FRESH B35 "
          "3417-3432.",
          "CERT-1 FC-169 forward chain on the 9 inherited arms vs "
          "l169/raw_l169.npz;",
          "B36 = list(range(3449, 3465))  # fresh (B35 = l169 stage a; "
          "key-scanned")
bad = []
for i, line in enumerate(s.split("\n"), 1):
    stl = line.strip()
    if stl.startswith("#") or stl.startswith('"""') or stl.startswith("'''"):
        continue
    # whitelist: pure string-literal elements of the _prevs INPUT absence
    # list (read-only cross-references to prior runs' stored npzs)
    if re.fullmatch(r'\s*(?:"l\d+/raw_[a-z0-9_]+\.npz",?\s*)+\]?', line):
        continue
    if stl in INPUT_OK or stl in DOC_OK:
        continue
    if re.search(r'l169/|\bB35\b', line):
        bad.append((i, line))
assert not bad, ("RESIDUAL old-token code lines", bad)
xref = [(i, l) for i, l in enumerate(s.split("\n"), 1)
        if re.search(r'l169/|B35', l) and l.strip().startswith("#")]

open(DST, "w").write(s)
py_compile.compile(DST, doraise=True)
print(f"wrote {DST}: {len(reps)} reps applied, residual scan CLEAN")
print(f"deliberate comment cross-references kept: {len(xref)}")
for i, l in xref:
    print(f"  L{i}: {l.strip()[:100]}")
