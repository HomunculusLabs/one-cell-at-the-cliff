"""Build l117_run.py from l116_run.py via exact-string transforms.
Every pattern must occur the asserted number of times or we abort."""
import sys

SRC = open("l116_run.py").read()
n_err = 0


def rep(old, new, count=1):
    global SRC, n_err
    c = SRC.count(old)
    if c != count:
        print(f"PATTERN MISMATCH ({c} != {count}): {old[:70]!r}")
        n_err += 1
        return
    SRC = SRC.replace(old, new)


# 1. docstring
rep('''"""L116 run: flip-joint-scan. PREREG l116/PREREG.md FIRST.

L113 machinery VERBATIM (arms, graphs, gains, draw order, seeds): a
replication-form EXTENSION readout of l113's own B10 trajectories with
the pool set extended to the 5 semantic pairs (Ta/Sr/Pr NEW, l101 a/b
naming; Ti/Tr keep f/e names so C0A keys match). g_cut58 additionally
re-bisected + asserted == l113 stored EXACT (C0A(c58) class). C0A is
FULL-BATCH: all 18 seeds x 5 arms x l113 key schema == raw_l113 EXACT.
CPU-only; raw checkpoint BEFORE analysis.
"""''',
    '''"""L117 run: glut-dose-ladder. PREREG l117/PREREG.md FIRST.

L116 machinery VERBATIM (5-pair pools, graphs, gains, draw order); arms
full/b65/cut/cut19/cut58 retained as ANCHORS (stored seeds 801/901 vs
raw_l113) + NEW dose arms cutk5/cutk10/cutk15 = closure minus the k
HEAVIEST glutamatergic heavy cells (deterministic mass-desc positional
filter, NO RNG; l117/static.json pins). Seeds: [801, 901] + FRESH B12
1601-1616 (asserted absent from raw_l113). g_cut/g_cut19/g_cut58
re-bisected + asserted == stored EXACT; dose gains bisected FRESH
(staircase disclosed, PREREG band disclosed not asserted). CPU-only;
raw checkpoint BEFORE analysis.
"""''')

# 2. arms / gain
rep('ARMS = ["full", "b65", "cut", "cut19", "cut58"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None)',
    'ARMS = ["full", "b65", "cut", "cut19", "cut58",\n'
    '        "cutk5", "cutk10", "cutk15"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,\n'
    '            cutk5=None, cutk10=None, cutk15=None)')

# 3. seeds: fresh B12
rep('''B10 = list(range(1401, 1417))       # l113 own batch: replication-form (PREREG)
SEEDS = ANCH + B10                  # anchors FIRST: early wiring verdict
FRESH = B10''',
    '''B12 = list(range(1601, 1617))       # fresh, verified absent from raw_l113
SEEDS = ANCH + B12                  # anchors FIRST: early wiring verdict
FRESH = B12''')

# 4. dose derivation after the cut58 derivation
rep('''keep_cut58 = keep_new.copy()
keep_cut58[cut58_drop] = False
n_cut58 = int(keep_cut58.sum())
assert n_cut58 == int(keep_new.sum()) - 58''',
    '''keep_cut58 = keep_new.copy()
keep_cut58[cut58_drop] = False
n_cut58 = int(keep_cut58.sum())
assert n_cut58 == int(keep_new.sum()) - 58
# L117: glut dose ladder — k HEAVIEST glutamatergic heavy cells (heav is
# mass-desc; positional filter is DETERMINISTIC, zero RNG). Pins from
# l117/static.json (PREREG); STOP on any miss.
S117 = json.load(open("l117/static.json"))
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
DOSE_K = (5, 10, 15)
cutk_drop, keep_cutk, n_cutk, dose_pins = {}, {}, {}, {}
for _kk in DOSE_K:
    _pin = S117["ladder"][f"k{_kk}"]
    _drop = np.sort(glut_desc[:_kk])
    assert len(_drop) == _kk
    assert np.isin(_drop, cut19_drop).all(), "dose drop not subset of glut-19"
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_kk, int(_keep.sum()))
    cutk_drop[_kk] = _drop
    keep_cutk[_kk] = _keep
    n_cutk[_kk] = int(_keep.sum())
    dose_pins[_kk] = _pin
assert dose_pins[5]["mass_removed"] == 0.0425 and \\
    dose_pins[10]["mass_removed"] == 0.0723 and \\
    dose_pins[15]["mass_removed"] == 0.0952, "ladder masses drifted (STOP)"''')

# 5. graphs
rep('''Wc_c19, loc_c19 = build(keep_cut19)
Wc_c58, loc_c58 = build(keep_cut58)''',
    '''Wc_c19, loc_c19 = build(keep_cut19)
Wc_c58, loc_c58 = build(keep_cut58)
Wc_ck5, loc_ck5 = build(keep_cutk[5])
Wc_ck10, loc_ck10 = build(keep_cutk[10])
Wc_ck15, loc_ck15 = build(keep_cutk[15])
assert Wc_ck5.values().numel() == dose_pins[5]["edges"]
assert Wc_ck10.values().numel() == dose_pins[10]["edges"]
assert Wc_ck15.values().numel() == dose_pins[15]["edges"]''')
rep('''Wb_o, Wb_n, Wb_c, Wb_c19, Wb_c58 = (wb(Wc_o), wb(Wc_n), wb(Wc_c),
                                    wb(Wc_c19), wb(Wc_c58))''',
    '''Wb_o, Wb_n, Wb_c, Wb_c19, Wb_c58 = (wb(Wc_o), wb(Wc_n), wb(Wc_c),
                                    wb(Wc_c19), wb(Wc_c58))
Wb_ck5, Wb_ck10, Wb_ck15 = wb(Wc_ck5), wb(Wc_ck10), wb(Wc_ck15)''')

# 6. positions
rep('''gi_cut58 = np.where(keep_cut58)[0]
cut58_pos_in_new = loc_n[gi_cut58]
old_pos_in_c58 = loc_c58[gi_old]
kept_new_mask58 = keep_cut58[new_g]                  # new_g order
kept_new_cut58 = loc_c58[new_g[kept_new_mask58]]     # cut58-local of kept new''',
    '''gi_cut58 = np.where(keep_cut58)[0]
cut58_pos_in_new = loc_n[gi_cut58]
old_pos_in_c58 = loc_c58[gi_old]
kept_new_mask58 = keep_cut58[new_g]                  # new_g order
kept_new_cut58 = loc_c58[new_g[kept_new_mask58]]     # cut58-local of kept new
gi_ck5 = np.where(keep_cutk[5])[0]
ck5_pos_in_new = loc_n[gi_ck5]
old_pos_in_ck5 = loc_ck5[gi_old]
kept_new_mask_k5 = keep_cutk[5][new_g]
kept_new_cutk5 = loc_ck5[new_g[kept_new_mask_k5]]
gi_ck10 = np.where(keep_cutk[10])[0]
ck10_pos_in_new = loc_n[gi_ck10]
old_pos_in_ck10 = loc_ck10[gi_old]
kept_new_mask_k10 = keep_cutk[10][new_g]
kept_new_cutk10 = loc_ck10[new_g[kept_new_mask_k10]]
gi_ck15 = np.where(keep_cutk[15])[0]
ck15_pos_in_new = loc_n[gi_ck15]
old_pos_in_ck15 = loc_ck15[gi_old]
kept_new_mask_k15 = keep_cutk[15][new_g]
kept_new_cutk15 = loc_ck15[new_g[kept_new_mask_k15]]''')

# 7. pools
rep('''POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "cut58": pools_for(loc_c58, keep_cut58),
         "b65": pools_for(loc_o, keep_old)}''',
    '''POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "cut58": pools_for(loc_c58, keep_cut58),
         "cutk5": pools_for(loc_ck5, keep_cutk[5]),
         "cutk10": pools_for(loc_ck10, keep_cutk[10]),
         "cutk15": pools_for(loc_ck15, keep_cutk[15]),
         "b65": pools_for(loc_o, keep_old)}''')
rep('''    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk''',
    '''    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk
    for _da in ("cutk5", "cutk10", "cutk15"):
        assert len(POOLS[_da][pk]) == want, (_da, pk)''')
rep('''    for a in ("cut", "cut19", "cut58", "b65"):
        assert len(POOLS[a][pk]) == want, (a, pk)''',
    '''    for a in ("cut", "cut19", "cut58", "cutk5", "cutk10", "cutk15", "b65"):
        assert len(POOLS[a][pk]) == want, (a, pk)''')

# 8. mech
rep('''mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "cut58": np.where(mech_mask[keep_cut58])[0],
        "b65": np.where(mech_mask[keep_old])[0]}''',
    '''mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "cut58": np.where(mech_mask[keep_cut58])[0],
        "cutk5": np.where(mech_mask[keep_cutk[5]])[0],
        "cutk10": np.where(mech_mask[keep_cutk[10]])[0],
        "cutk15": np.where(mech_mask[keep_cutk[15]])[0],
        "b65": np.where(mech_mask[keep_old])[0]}''')

# 9. motor
rep('''motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cut58", n_cut58), ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19),
                     ("cut58", keep_cut58, loc_c58), ("b65", keep_old, loc_o)):''',
    '''motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cut58", n_cut58), ("cutk5", n_cutk[5]), ("cutk10", n_cutk[10]),
          ("cutk15", n_cutk[15]), ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19),
                     ("cut58", keep_cut58, loc_c58),
                     ("cutk5", keep_cutk[5], loc_ck5),
                     ("cutk10", keep_cutk[10], loc_ck10),
                     ("cutk15", keep_cutk[15], loc_ck15),
                     ("b65", keep_old, loc_o)):''')

# 10. dng100 (+ L115 pin re-asserted for the dose arms)
rep('''dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "cut58": np.sort(loc_c58[dng100_all[keep_cut58[dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}
assert len(dng100["full"]) == S92["dng100"]''',
    '''dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "cut58": np.sort(loc_c58[dng100_all[keep_cut58[dng100_all]]]),
          "cutk5": np.sort(loc_ck5[dng100_all[keep_cutk[5][dng100_all]]]),
          "cutk10": np.sort(loc_ck10[dng100_all[keep_cutk[10][dng100_all]]]),
          "cutk15": np.sort(loc_ck15[dng100_all[keep_cutk[15][dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}
assert len(dng100["full"]) == S92["dng100"]
# L115/L117 pin: no DNg100 cell sits in the heavy-77 (dose drops cannot
# touch the drive channel) — STOP if violated.
assert not np.isin(dng100_all, cut_drop).any(), "DNg100 in heavy-77 (STOP)"
for _da in ("cutk5", "cutk10", "cutk15"):
    assert len(dng100[_da]) == S92["dng100"], _da''')

# 11. WB / N_OF
rep('''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "b65": n_old}''',
    '''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "cutk5": Wb_ck5, "cutk10": Wb_ck10, "cutk15": Wb_ck15, "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "cutk5": n_cutk[5], "cutk10": n_cutk[10], "cutk15": n_cutk[15],
        "b65": n_old}''')

# 12. bisect gains dict
rep('''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g))''',
    '''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutk5=g, cutk10=g, cutk15=g))''')

# 13. fresh dose bisects after the cut58 bisect (C0A(c58) block retained)
rep('''GAIN["cut58"] = lo3
af_final58 = bisect_af_mean(lo3, "cut58")
# C0A(c58): deterministic re-bisect must land on the stored l113 gain EXACT
assert GAIN["cut58"] == G_CUT58_STORED, (GAIN["cut58"], G_CUT58_STORED)
log(f"g_cut58 {lo3:.6f} == l113 stored EXACT | af_final58 {af_final58:.6f} "
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")''',
    '''GAIN["cut58"] = lo3
af_final58 = bisect_af_mean(lo3, "cut58")
# C0A(c58): deterministic re-bisect must land on the stored l113 gain EXACT
assert GAIN["cut58"] == G_CUT58_STORED, (GAIN["cut58"], G_CUT58_STORED)
log(f"g_cut58 {lo3:.6f} == l113 stored EXACT | af_final58 {af_final58:.6f} "
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")

# L117: fresh bisects for the dose arms (no stored form; staircase + band
# DISCLOSED per PREREG — the .14-.16 band is a disclosure, never an abort)
dose_stairs = {}
for _a in ("cutk5", "cutk10", "cutk15"):
    lo_d, hi_d = 0.12, 0.18
    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _a), bisect_af_mean(hi_d, _a)
    log(f"{_a} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo_d < AF_T < af_hi_d, f"{_a} bracket fail"
    for it in range(24):
        mid = (lo_d + hi_d) / 2
        if bisect_af_mean(mid, _a) < AF_T:
            lo_d = mid
        else:
            hi_d = mid
    GAIN[_a] = lo_d
    af_d = bisect_af_mean(lo_d, _a)
    dose_stairs[_a] = abs(af_d - AF_T)
    _band = " [OUTSIDE PREREG band .14-.16 — DISCLOSED]" \\
        if not (0.14 <= lo_d <= 0.16) else ""
    log(f"g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "
        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")''')

# 14. X-init blocks (settle_states + rollout): add cutk states, 2 sites
rep('''    Xc_cut58 = torch.zeros(n_cut58, 1)
    Xc_cut58[old_pos_in_c58] = X0o
    Xc_cut58[kept_new_cut58] = X0n[kept_new_mask58]
    Xo65 = X0o.clone()
    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
              b65=Xo65.clone())''',
    '''    Xc_cut58 = torch.zeros(n_cut58, 1)
    Xc_cut58[old_pos_in_c58] = X0o
    Xc_cut58[kept_new_cut58] = X0n[kept_new_mask58]
    Xc_ck5 = torch.zeros(n_cutk[5], 1)
    Xc_ck5[old_pos_in_ck5] = X0o
    Xc_ck5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xc_ck10 = torch.zeros(n_cutk[10], 1)
    Xc_ck10[old_pos_in_ck10] = X0o
    Xc_ck10[kept_new_cutk10] = X0n[kept_new_mask_k10]
    Xc_ck15 = torch.zeros(n_cutk[15], 1)
    Xc_ck15[old_pos_in_ck15] = X0o
    Xc_ck15[kept_new_cutk15] = X0n[kept_new_mask_k15]
    Xo65 = X0o.clone()
    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
              cutk5=Xc_ck5.clone(), cutk10=Xc_ck10.clone(),
              cutk15=Xc_ck15.clone(), b65=Xo65.clone())''')
rep('''    Xc_cut58 = torch.zeros(n_cut58, 1)
    Xc_cut58[old_pos_in_c58] = X0o
    Xc_cut58[kept_new_cut58] = X0n[kept_new_mask58]
    Xo65 = X0o.clone()
    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
             b65=Xo65.clone())''',
    '''    Xc_cut58 = torch.zeros(n_cut58, 1)
    Xc_cut58[old_pos_in_c58] = X0o
    Xc_cut58[kept_new_cut58] = X0n[kept_new_mask58]
    Xc_ck5 = torch.zeros(n_cutk[5], 1)
    Xc_ck5[old_pos_in_ck5] = X0o
    Xc_ck5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xc_ck10 = torch.zeros(n_cutk[10], 1)
    Xc_ck10[old_pos_in_ck10] = X0o
    Xc_ck10[kept_new_cutk10] = X0n[kept_new_mask_k10]
    Xc_ck15 = torch.zeros(n_cutk[15], 1)
    Xc_ck15[old_pos_in_ck15] = X0o
    Xc_ck15[kept_new_cutk15] = X0n[kept_new_mask_k15]
    Xo65 = X0o.clone()
    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
             cutk5=Xc_ck5.clone(), cutk10=Xc_ck10.clone(),
             cutk15=Xc_ck15.clone(), b65=Xo65.clone())''')

# 15. noise dicts: add cutk entries, 3 sites
rep('''        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cut58=nzn[cut58_pos_in_new], b65=nz_o)''',
    '''        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cut58=nzn[cut58_pos_in_new],
                     cutk5=nzn[ck5_pos_in_new],
                     cutk10=nzn[ck10_pos_in_new],
                     cutk15=nzn[ck15_pos_in_new], b65=nz_o)''', count=3)

# 16. raw_partial path (exists + load — l116's load line kept the l113 path,
#     a latent resume quirk never hit because l116/raw_partial never existed;
#     fixed here for L117) + savez + log
rep('''if os.path.exists("l116/raw_partial.npz"):
    z = np.load("l113/raw_partial.npz")''',
    '''if os.path.exists("l117/raw_partial.npz"):
    z = np.load("l117/raw_partial.npz")''')
rep('    np.savez("l116/raw_partial.npz", **store)',
    '    np.savez("l117/raw_partial.npz", **store)')
rep('''np.savez_compressed("l116/raw_l116.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l116.npz checkpointed BEFORE analysis")''',
    '''np.savez_compressed("l117/raw_l117.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
                    g_cutk5=GAIN["cutk5"], g_cutk10=GAIN["cutk10"],
                    g_cutk15=GAIN["cutk15"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    cutk5_drop=cutk_drop[5], cutk10_drop=cutk_drop[10],
                    cutk15_drop=cutk_drop[15],
                    dose_mass=np.array([dose_pins[5]["mass_removed"],
                                        dose_pins[10]["mass_removed"],
                                        dose_pins[15]["mass_removed"]]),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l117.npz checkpointed BEFORE analysis")''')

# 17. C0A: stored arms + stored seeds only; B12-absent assert
rep('''zprev = np.load("l113/raw_l113.npz")
C0A_KEYS = ["mm", "xm"] + [f"{k}_{c}{s}" for k in ("Ti", "Tr")
                           for c in ("f", "e") for s in ("L", "R")]
assert all(f"{k}_full_801" in zprev.files for k in C0A_KEYS)
c0a = {}
for s in SEEDS:  # ALL 18 seeds: first full-batch chain anchor
    for key in C0A_KEYS:
        for a in ARMS:
            c0a[f"113_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - zprev[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ARMS:
        c0a[f"113_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(zprev[f"af_{a}_{s}"]))
c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}
                       - {"Ti", "Tr"})
log(f"C0A covered keys {len(C0A_KEYS)} x arms {len(ARMS)} x seeds {len(SEEDS)}"
    f" | NEW pools excluded by name: {c0a_new_pools}")''',
    '''zprev = np.load("l113/raw_l113.npz")
C0A_KEYS = ["mm", "xm"] + [f"{k}_{c}{s}" for k in ("Ti", "Tr")
                           for c in ("f", "e") for s in ("L", "R")]
assert all(f"{k}_full_801" in zprev.files for k in C0A_KEYS)
# B12 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B12), \\
    "B12 collides with stored batches (STOP)"
STORED_ARMS = ("full", "b65", "cut", "cut19", "cut58")
c0a = {}
for s in (801, 901):  # stored seeds only: anchors vs raw_l113
    for key in C0A_KEYS:
        for a in STORED_ARMS:
            c0a[f"113_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - zprev[f"{key}_{a}_{s}"][:WIN]).max())
    for a in STORED_ARMS:
        c0a[f"113_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(zprev[f"af_{a}_{s}"]))
c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}
                       - {"Ti", "Tr"})
log(f"C0A covered keys {len(C0A_KEYS)} x stored arms {len(STORED_ARMS)} "
    f"x anchor seeds 2 | NEW pools excluded by name: {c0a_new_pools} "
    f"| NEW arms excluded by name: ['cutk5','cutk10','cutk15']")''')

# 18. anchors out dict
rep('''out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           g_cut58_stored_exact=bool(GAIN["cut58"] == G_CUT58_STORED),
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           K=K, mass_split=mass_split, n_seeds=len(SEEDS),
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l116/anchors_run.json", "w"), indent=1)''',
    '''out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           g_cut58_stored_exact=bool(GAIN["cut58"] == G_CUT58_STORED),
           g_cutk5=GAIN["cutk5"], g_cutk10=GAIN["cutk10"],
           g_cutk15=GAIN["cutk15"], dose_stairs=dose_stairs,
           dose_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutk5", "cutk10", "cutk15"))),
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           K=K, mass_split=mass_split, n_seeds=len(SEEDS),
           dose_mass={k: dose_pins[k]["mass_removed"] for k in DOSE_K},
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l117/anchors_run.json", "w"), indent=1)''')

if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
open("l117_run.py", "w").write(SRC)
print("l117_run.py written OK")
