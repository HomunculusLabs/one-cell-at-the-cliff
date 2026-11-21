"""Build l115_run.py from l113_run.py via exact-string transforms.
Every pattern must occur the asserted number of times or we abort."""
import sys

SRC = open("l113_run.py").read()
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
rep('''"""L113 run: cut58 mirror slice. PREREG l113/PREREG.md FIRST.

L111 machinery VERBATIM (graphs, gains, draw order); arms full/b65/cut/
cut19 identical (cut19 retained: doubles as L114 second batch; ZERO new
draws), cut58 NEW = closure minus the 58 NON-glutamatergic heavy (l110
addendum; mirror of L111). Seeds: anchors [801, 901] vs raw_l111 + FRESH
B10 1401-1416 (verified absent pre-launch). g_cut + g_cut19 re-bisected +
asserted == stored EXACT (both); g_cut58 bisected fresh (disclosed).
CPU-only; raw checkpoint BEFORE analysis.
"""''',
    '''"""L115 run: random-19-subset flip control. PREREG l115/PREREG.md FIRST.

L113 machinery VERBATIM (graphs, gains, draw order); arms full/b65/cut/
cut19 identical (anchors vs raw_l113; ZERO new draws), cutR1/cutR2/cutR3
NEW = closure minus RANDOM 19-of-heavy-77 subsets (numpy default_rng(1150),
positional picks on the mass-order heavy array; torch RNG untouched).
Seeds: anchors [801, 901] vs raw_l113 + FRESH B11 1501-1516 (verified
absent pre-launch). g_cut + g_cut19 re-bisected + asserted == stored
EXACT (both); g_cutR1-3 bisected fresh (disclosed). CPU-only; raw
checkpoint BEFORE analysis.
"""''')

# 2. arms / gain
rep('ARMS = ["full", "b65", "cut", "cut19", "cut58"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None)',
    'ARMS = ["full", "b65", "cut", "cut19", "cutR1", "cutR2", "cutR3"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None,\n'
    '            cutR1=None, cutR2=None, cutR3=None)')

# 3. seeds
rep('''B10 = list(range(1401, 1417))       # fresh, verified absent pre-launch
SEEDS = ANCH + B10                  # anchors FIRST: early wiring verdict
FRESH = B10''',
    '''B11 = list(range(1501, 1517))       # fresh, verified absent pre-launch
SEEDS = ANCH + B11                  # anchors FIRST: early wiring verdict
FRESH = B11''')

# 4. cut58 derivation -> random draws
rep('''# L113: NON-glutamatergic subset of the heavy-77 (mirror of L111's cut19)
cut58_drop = np.sort(heav[~is_glut[heav]])
assert len(cut58_drop) == 58, f"non-glut heavy = {len(cut58_drop)} != 58 (STOP)"
assert mass_split == {"glut19": 0.1103, "other58": 0.3921}, mass_split
keep_cut58 = keep_new.copy()
keep_cut58[cut58_drop] = False
n_cut58 = int(keep_cut58.sum())
assert n_cut58 == int(keep_new.sum()) - 58''',
    '''assert mass_split == {"glut19": 0.1103, "other58": 0.3921}, mass_split
# L115: RANDOM 19-of-heavy-77 subsets — numpy RNG only (DISJOINT from the
# torch settle/noise generators; draw order untouched). Picks are POSITIONAL
# on heav (mass-desc order); 3 unconditional draws, asserted distinct.
rng = np.random.default_rng(1150)
rand_picks = [np.sort(rng.choice(K, size=19, replace=False)) for _ in range(3)]
assert len({tuple(p) for p in rand_picks}) == 3, "random draws collided (STOP)"
rand_mass, rand_glut = [], []
cutR_drop = {}
for i, _pick in enumerate(rand_picks, 1):
    _drop = np.sort(heav[_pick])
    cutR_drop[i] = _drop
    keep_v = keep_new.copy()
    keep_v[_drop] = False
    globals()[f"keep_cutR{i}"] = keep_v
    globals()[f"n_cutR{i}"] = int(keep_v.sum())
    assert int(keep_v.sum()) == int(keep_new.sum()) - 19
    rand_mass.append(round(float(_mass_heavy[_pick].sum() / cell_mass.sum()), 4))
    rand_glut.append(int(is_glut[heav[_pick]].sum()))''')

# 5. graphs
rep('''Wc_c19, loc_c19 = build(keep_cut19)
Wc_c58, loc_c58 = build(keep_cut58)''',
    '''Wc_c19, loc_c19 = build(keep_cut19)
Wc_cR1, loc_cR1 = build(keep_cutR1)
Wc_cR2, loc_cR2 = build(keep_cutR2)
Wc_cR3, loc_cR3 = build(keep_cutR3)''')
rep('Wb_o, Wb_n, Wb_c, Wb_c19, Wb_c58 = (wb(Wc_o), wb(Wc_n), wb(Wc_c),\n'
    '                                    wb(Wc_c19), wb(Wc_c58))',
    'Wb_o, Wb_n, Wb_c, Wb_c19 = (wb(Wc_o), wb(Wc_n), wb(Wc_c), wb(Wc_c19))\n'
    'Wb_cR1, Wb_cR2, Wb_cR3 = wb(Wc_cR1), wb(Wc_cR2), wb(Wc_cR3)')

# 6. positions
rep('''gi_cut58 = np.where(keep_cut58)[0]
cut58_pos_in_new = loc_n[gi_cut58]
old_pos_in_c58 = loc_c58[gi_old]
kept_new_mask58 = keep_cut58[new_g]                  # new_g order
kept_new_cut58 = loc_c58[new_g[kept_new_mask58]]     # cut58-local of kept new''',
    ''.join(
        f'''gi_cutR{i} = np.where(keep_cutR{i})[0]
cutR{i}_pos_in_new = loc_n[gi_cutR{i}]
old_pos_in_cR{i} = loc_cR{i}[gi_old]
kept_new_maskR{i} = keep_cutR{i}[new_g]                  # new_g order
kept_new_cutR{i} = loc_cR{i}[new_g[kept_new_maskR{i}]]     # cutR{i}-local of kept new
''' for i in (1, 2, 3)).rstrip('\n'))

# 7. pools
rep('''POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "cut58": pools_for(loc_c58, keep_cut58),
         "b65": pools_for(loc_o, keep_old)}''',
    '''POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "cutR1": pools_for(loc_cR1, keep_cutR1),
         "cutR2": pools_for(loc_cR2, keep_cutR2),
         "cutR3": pools_for(loc_cR3, keep_cutR3),
         "b65": pools_for(loc_o, keep_old)}''')
rep('''    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk''',
    '''    assert len(POOLS["cut19"][pk]) == want, pk
    for _ra in ("cutR1", "cutR2", "cutR3"):
        assert len(POOLS[_ra][pk]) == want, (_ra, pk)''')

# 8. mech
rep('''mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "cut58": np.where(mech_mask[keep_cut58])[0],
        "b65": np.where(mech_mask[keep_old])[0]}''',
    '''mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "cutR1": np.where(mech_mask[keep_cutR1])[0],
        "cutR2": np.where(mech_mask[keep_cutR2])[0],
        "cutR3": np.where(mech_mask[keep_cutR3])[0],
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
          ("cutR1", n_cutR1), ("cutR2", n_cutR2), ("cutR3", n_cutR3),
          ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19),
                     ("cutR1", keep_cutR1, loc_cR1),
                     ("cutR2", keep_cutR2, loc_cR2),
                     ("cutR3", keep_cutR3, loc_cR3),
                     ("b65", keep_old, loc_o)):''')

# 10. dng100 + L115 static pin
rep('''dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "cut58": np.sort(loc_c58[dng100_all[keep_cut58[dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}
assert len(dng100["full"]) == S92["dng100"]''',
    '''# L115 static pin (pre-verified pre-launch; STOP if violated): NO DNg100
# cell sits in the heavy-77, so no random draw can touch the drive channel.
assert not np.isin(dng100_all, cut_drop).any(), "DNg100 in heavy-77 (STOP)"
dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "cutR1": np.sort(loc_cR1[dng100_all[keep_cutR1[dng100_all]]]),
          "cutR2": np.sort(loc_cR2[dng100_all[keep_cutR2[dng100_all]]]),
          "cutR3": np.sort(loc_cR3[dng100_all[keep_cutR3[dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}
assert len(dng100["full"]) == S92["dng100"]
for _ra in ("cutR1", "cutR2", "cutR3"):
    assert len(dng100[_ra]) == S92["dng100"], _ra''')

# 11. WB / N_OF
rep('''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "b65": n_old}''',
    '''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19,
      "cutR1": Wb_cR1, "cutR2": Wb_cR2, "cutR3": Wb_cR3, "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19,
        "cutR1": n_cutR1, "cutR2": n_cutR2, "cutR3": n_cutR3, "b65": n_old}''')

# 12. bisect gains dict
rep('        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,\n'
    '                                  cut58=g))',
    '        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,\n'
    '                                  cutR1=g, cutR2=g, cutR3=g))')

# 13. cut58 bisect -> three fresh random bisects
rep('''# L113: fresh bisect for the cut58 subnet (staircase disclosed)
lo3, hi3 = 0.12, 0.18
af_lo3, af_hi3 = bisect_af_mean(lo3, "cut58"), bisect_af_mean(hi3, "cut58")
log(f"cut58 bracket af({lo3})={af_lo3:.5f} af({hi3})={af_hi3:.5f} "
    f"target {AF_T:.5f}")
assert af_lo3 < AF_T < af_hi3, "cut58 bracket fail"
for it in range(24):
    mid = (lo3 + hi3) / 2
    if bisect_af_mean(mid, "cut58") < AF_T:
        lo3 = mid
    else:
        hi3 = mid
GAIN["cut58"] = lo3
af_final58 = bisect_af_mean(lo3, "cut58")
log(f"g_cut58 {lo3:.6f} | af_final58 {af_final58:.6f} "
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")''',
    '''# L115: fresh bisects for the three random-19 subnets (staircase disclosed)
af_finalR = {}
for _ra in ("cutR1", "cutR2", "cutR3"):
    lo3, hi3 = 0.12, 0.32  # ADDENDUM 1: widened (attempt 1 cutR3 bracket fail)
    af_lo3 = bisect_af_mean(lo3, _ra)
    af_hi3 = bisect_af_mean(hi3, _ra)
    log(f"{_ra} bracket af({lo3})={af_lo3:.5f} af({hi3})={af_hi3:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo3 < AF_T < af_hi3, f"{_ra} bracket fail"
    for it in range(24):
        mid = (lo3 + hi3) / 2
        if bisect_af_mean(mid, _ra) < AF_T:
            lo3 = mid
        else:
            hi3 = mid
    GAIN[_ra] = lo3
    af_finalR[_ra] = bisect_af_mean(lo3, _ra)
    log(f"g_{_ra} {lo3:.6f} | af_final {af_finalR[_ra]:.6f} "
        f"|af-target| {abs(af_finalR[_ra] - AF_T):.2e} (staircase disclosed)")''')

# 14. Xc construction blocks (settle + rollout: same text, count=2)
rep('''    Xc_cut58 = torch.zeros(n_cut58, 1)
    Xc_cut58[old_pos_in_c58] = X0o
    Xc_cut58[kept_new_cut58] = X0n[kept_new_mask58]''',
    ''.join(
        f'''    Xc_cR{i} = torch.zeros(n_cutR{i}, 1)
    Xc_cR{i}[old_pos_in_cR{i}] = X0o
    Xc_cR{i}[kept_new_cutR{i}] = X0n[kept_new_maskR{i}]
''' for i in (1, 2, 3)).rstrip('\n'), count=2)

# 15. state dicts (settle + rollout variants differ)
rep('    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),\n'
    '              b65=Xo65.clone())',
    '    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '              cut19=Xc_cut19.clone(), cutR1=Xc_cR1.clone(),\n'
    '              cutR2=Xc_cR2.clone(), cutR3=Xc_cR3.clone(),\n'
    '              b65=Xo65.clone())')
rep('    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),\n'
    '             b65=Xo65.clone())',
    '    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),\n'
    '             cut19=Xc_cut19.clone(), cutR1=Xc_cR1.clone(),\n'
    '             cutR2=Xc_cR2.clone(), cutR3=Xc_cR3.clone(),\n'
    '             b65=Xo65.clone())')

# 16. noise dicts (settle_states + rollout settle + rollout WIN: count=3)
rep('''        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cut58=nzn[cut58_pos_in_new], b65=nz_o)''',
    '''        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cutR1=nzn[cutR1_pos_in_new],
                     cutR2=nzn[cutR2_pos_in_new],
                     cutR3=nzn[cutR3_pos_in_new], b65=nz_o)''', count=3)

# 17. npz paths
rep('if os.path.exists("l113/raw_partial.npz"):',
    'if os.path.exists("l115/raw_partial.npz"):')
rep('np.savez("l113/raw_partial.npz", **store)',
    'np.savez("l115/raw_partial.npz", **store)')
rep('''np.savez_compressed("l113/raw_l113.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l113.npz checkpointed BEFORE analysis")''',
    '''np.savez_compressed("l115/raw_l115.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"],
                    g_cutR1=GAIN["cutR1"], g_cutR2=GAIN["cutR2"],
                    g_cutR3=GAIN["cutR3"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cutR1_drop=cutR_drop[1], cutR2_drop=cutR_drop[2],
                    cutR3_drop=cutR_drop[3],
                    rand_mass=np.array(rand_mass), rand_glut=np.array(rand_glut),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l115.npz checkpointed BEFORE analysis")''')

# 18. C0A block
rep('''z111 = np.load("l111/raw_l111.npz")
c0a = {}
for s in (801, 901):  # full/b65/cut/cut19 vs stored l111 (itself C0A-cert vs l109)
    for key in ["mm", "xm"] + list(POOLS["full"]):
        for a in ("full", "b65", "cut", "cut19"):
            c0a[f"111_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z111[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("full", "b65", "cut", "cut19"):
        c0a[f"111_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(z111[f"af_{a}_{s}"]))''',
    '''zprev = np.load("l113/raw_l113.npz")
c0a = {}
for s in (801, 901):  # full/b65/cut/cut19 vs stored l113 (itself C0A-cert vs l111)
    for key in ["mm", "xm"] + list(POOLS["full"]):
        for a in ("full", "b65", "cut", "cut19"):
            c0a[f"113_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - zprev[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("full", "b65", "cut", "cut19"):
        c0a[f"113_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(zprev[f"af_{a}_{s}"]))''')

# 19. anchors out dict
rep('''out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           K=K, mass_split=mass_split,
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l113/anchors_run.json", "w"), indent=1)
log(f"C0A {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")''',
    '''out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"],
           g_cutR={a: GAIN[a] for a in ("cutR1", "cutR2", "cutR3")},
           af_final=af_final, af_final19=af_final19,
           af_finalR=af_finalR, K=K, mass_split=mass_split,
           rand_mass=rand_mass, rand_glut=rand_glut,
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l115/anchors_run.json", "w"), indent=1)
log(f"C0A {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")''')

if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
open("l115_run.py", "w").write(SRC)
print("l115_run.py written OK")
