"""Build l113_run.py from l111_run.py via exact-string transforms.
Every pattern must occur the asserted number of times or we abort."""
import sys

SRC = open("l111_run.py").read()
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
rep('''"""L111 run: glutamate-subset ladder slice. PREREG l111/PREREG.md FIRST.

L109 machinery VERBATIM (graphs, gains, draw order); arms full/b65/cut
identical, h65 dropped (settled 32/32 twice), cut19 NEW = closure minus the
19 glutamatergic cells of the heavy-77 (l110 addendum). Seeds: anchors
[801, 901] vs raw_l109 + FRESH B9 1301-1316 (verified absent pre-launch).
g_cut re-bisected + asserted == stored; g_cut19 bisected fresh (disclosed).
CPU-only; raw checkpoint BEFORE analysis.
"""''',
    '''"""L113 run: cut58 mirror slice. PREREG l113/PREREG.md FIRST.

L111 machinery VERBATIM (graphs, gains, draw order); arms full/b65/cut/
cut19 identical (cut19 retained: doubles as L114 second batch; ZERO new
draws), cut58 NEW = closure minus the 58 NON-glutamatergic heavy (l110
addendum; mirror of L111). Seeds: anchors [801, 901] vs raw_l111 + FRESH
B10 1401-1416 (verified absent pre-launch). g_cut + g_cut19 re-bisected +
asserted == stored EXACT (both); g_cut58 bisected fresh (disclosed).
CPU-only; raw checkpoint BEFORE analysis.
"""''')

# 2. arms / gain
rep('ARMS = ["full", "b65", "cut", "cut19"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None)  # both by bisect',
    'ARMS = ["full", "b65", "cut", "cut19", "cut58"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None)\n'
    'G_CUT19_STORED = 0.15096808075904844  # l111 stored, PREREG C0A(c19)')

# 3. seeds
rep('''B9 = list(range(1301, 1317))        # fresh, verified absent pre-launch
SEEDS = ANCH + B9                   # anchors FIRST: early wiring verdict
FRESH = B9''',
    '''B10 = list(range(1401, 1417))       # fresh, verified absent pre-launch
SEEDS = ANCH + B10                  # anchors FIRST: early wiring verdict
FRESH = B10''')

# 4. cut58 derivation (after the cut19 block)
rep('''_mass_heavy = cell_mass[order[:K]]
mass_split = dict(
    glut19=round(float(_mass_heavy[is_glut[heav]].sum() / cell_mass.sum()), 4),
    other58=round(float(_mass_heavy[~is_glut[heav]].sum() / cell_mass.sum()), 4))''',
    '''_mass_heavy = cell_mass[order[:K]]
mass_split = dict(
    glut19=round(float(_mass_heavy[is_glut[heav]].sum() / cell_mass.sum()), 4),
    other58=round(float(_mass_heavy[~is_glut[heav]].sum() / cell_mass.sum()), 4))
# L113: NON-glutamatergic subset of the heavy-77 (mirror of L111's cut19)
cut58_drop = np.sort(heav[~is_glut[heav]])
assert len(cut58_drop) == 58, f"non-glut heavy = {len(cut58_drop)} != 58 (STOP)"
assert mass_split == {"glut19": 0.1103, "other58": 0.3921}, mass_split
keep_cut58 = keep_new.copy()
keep_cut58[cut58_drop] = False
n_cut58 = int(keep_cut58.sum())
assert n_cut58 == int(keep_new.sum()) - 58''')

# 5. graphs
rep('''Wc_c19, loc_c19 = build(keep_cut19)
assert Wc_o.values().numel() == S92["edges_old"]''',
    '''Wc_c19, loc_c19 = build(keep_cut19)
Wc_c58, loc_c58 = build(keep_cut58)
assert Wc_o.values().numel() == S92["edges_old"]''')
rep('Wb_o, Wb_n, Wb_c, Wb_c19 = wb(Wc_o), wb(Wc_n), wb(Wc_c), wb(Wc_c19)',
    'Wb_o, Wb_n, Wb_c, Wb_c19, Wb_c58 = (wb(Wc_o), wb(Wc_n), wb(Wc_c),\n'
    '                                    wb(Wc_c19), wb(Wc_c58))')

# 6. positions
rep('''gi_cut19 = np.where(keep_cut19)[0]
cut19_pos_in_new = loc_n[gi_cut19]
old_pos_in_c19 = loc_c19[gi_old]
kept_new_mask19 = keep_cut19[new_g]                  # new_g order
kept_new_cut19 = loc_c19[new_g[kept_new_mask19]]     # cut19-local of kept new''',
    '''gi_cut19 = np.where(keep_cut19)[0]
cut19_pos_in_new = loc_n[gi_cut19]
old_pos_in_c19 = loc_c19[gi_old]
kept_new_mask19 = keep_cut19[new_g]                  # new_g order
kept_new_cut19 = loc_c19[new_g[kept_new_mask19]]     # cut19-local of kept new
gi_cut58 = np.where(keep_cut58)[0]
cut58_pos_in_new = loc_n[gi_cut58]
old_pos_in_c58 = loc_c58[gi_old]
kept_new_mask58 = keep_cut58[new_g]                  # new_g order
kept_new_cut58 = loc_c58[new_g[kept_new_mask58]]     # cut58-local of kept new''')

# 7. pools
rep('''POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "b65": pools_for(loc_o, keep_old)}''',
    '''POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "cut58": pools_for(loc_c58, keep_cut58),
         "b65": pools_for(loc_o, keep_old)}''')
rep('''    assert len(POOLS["cut19"][pk]) == want, pk''',
    '''    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk''')

# 8. mech
rep('''mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "b65": np.where(mech_mask[keep_old])[0]}''',
    '''mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "cut58": np.where(mech_mask[keep_cut58])[0],
        "b65": np.where(mech_mask[keep_old])[0]}''')

# 9. motor
rep('''motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19), ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19), ("b65", keep_old, loc_o)):''',
    '''motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cut58", n_cut58), ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19),
                     ("cut58", keep_cut58, loc_c58), ("b65", keep_old, loc_o)):''')

# 10. dng100
rep('''dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}''',
    '''dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "cut58": np.sort(loc_c58[dng100_all[keep_cut58[dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}''')

# 11. WB / N_OF
rep('''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "b65": n_old}''',
    '''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "b65": n_old}''')

# 12. X-init blocks (settle + rollout) — cut58 init
rep('''    Xc_cut19 = torch.zeros(n_cut19, 1)
    Xc_cut19[old_pos_in_c19] = X0o
    Xc_cut19[kept_new_cut19] = X0n[kept_new_mask19]
    Xo65 = X0o.clone()''',
    '''    Xc_cut19 = torch.zeros(n_cut19, 1)
    Xc_cut19[old_pos_in_c19] = X0o
    Xc_cut19[kept_new_cut19] = X0n[kept_new_mask19]
    Xc_cut58 = torch.zeros(n_cut58, 1)
    Xc_cut58[old_pos_in_c58] = X0o
    Xc_cut58[kept_new_cut58] = X0n[kept_new_mask58]
    Xo65 = X0o.clone()''', count=2)
rep('''    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), b65=Xo65.clone())''',
    '''    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
              b65=Xo65.clone())''')
rep('''    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), b65=Xo65.clone())''',
    '''    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
             b65=Xo65.clone())''')

# 13. noise dicts (settle + rollout x2)
rep('noise = dict(full=nzn, cut=nzn[cut_pos_in_new],\n'
    '                     cut19=nzn[cut19_pos_in_new], b65=nz_o)',
    'noise = dict(full=nzn, cut=nzn[cut_pos_in_new],\n'
    '                     cut19=nzn[cut19_pos_in_new],\n'
    '                     cut58=nzn[cut58_pos_in_new], b65=nz_o)', count=3)

# 14. bisect gains dict + cut19 stored assert + cut58 bisect
rep('        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g))',
    '        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,\n'
    '                                  cut58=g))')
rep('''GAIN["cut19"] = lo2
af_final19 = bisect_af_mean(lo2, "cut19")
log(f"g_cut19 {lo2:.6f} | af_final19 {af_final19:.6f} "
    f"|af-target| {abs(af_final19 - AF_T):.2e} (staircase disclosed)")''',
    '''GAIN["cut19"] = lo2
af_final19 = bisect_af_mean(lo2, "cut19")
# C0A(c19): deterministic re-bisect must land on the stored l111 gain EXACT
assert GAIN["cut19"] == G_CUT19_STORED, (GAIN["cut19"], G_CUT19_STORED)
log(f"g_cut19 {lo2:.6f} == stored EXACT | af_final19 {af_final19:.6f} "
    f"|af-target| {abs(af_final19 - AF_T):.2e} (staircase disclosed)")

# L113: fresh bisect for the cut58 subnet (staircase disclosed)
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
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")''')

# 15. partial/raw paths (fix the l111 inherited-load quirk: load OUR partial)
rep('''if os.path.exists("l111/raw_partial.npz"):
    z = np.load("l109/raw_partial.npz")
    store = {k: z[k] for k in z.files}''',
    '''if os.path.exists("l113/raw_partial.npz"):
    z = np.load("l113/raw_partial.npz")
    store = {k: z[k] for k in z.files}''')
rep('np.savez("l111/raw_partial.npz", **store)',
    'np.savez("l113/raw_partial.npz", **store)')
rep('''np.savez_compressed("l111/raw_l111.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l111.npz checkpointed BEFORE analysis")''',
    '''np.savez_compressed("l113/raw_l113.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l113.npz checkpointed BEFORE analysis")''')

# 16. C0A anchors -> vs raw_l111 (full/b65/cut/cut19 on 801+901)
rep('''z109 = np.load("l109/raw_l109.npz")
c0a = {}
for s in (801, 901):  # full/b65/cut vs stored l109 (itself C0A-cert vs l94/l107)
    for key in ["mm", "xm"] + list(POOLS["full"]):
        for a in ("full", "b65", "cut"):
            c0a[f"109_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z109[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("full", "b65", "cut"):
        c0a[f"109_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(z109[f"af_{a}_{s}"]))
out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], af_final=af_final,
           af_final19=af_final19, K=K, mass_split=mass_split,
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l111/anchors_run.json", "w"), indent=1)
log(f"C0A {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")''',
    '''z111 = np.load("l111/raw_l111.npz")
c0a = {}
for s in (801, 901):  # full/b65/cut/cut19 vs stored l111 (itself C0A-cert vs l109)
    for key in ["mm", "xm"] + list(POOLS["full"]):
        for a in ("full", "b65", "cut", "cut19"):
            c0a[f"111_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z111[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("full", "b65", "cut", "cut19"):
        c0a[f"111_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(z111[f"af_{a}_{s}"]))
out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           K=K, mass_split=mass_split,
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l113/anchors_run.json", "w"), indent=1)
log(f"C0A {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")''')

if n_err:
    sys.exit(f"ABORT: {n_err} pattern mismatches — nothing written")
open("l113_run.py", "w").write(SRC)
import py_compile
py_compile.compile("l113_run.py", doraise=True)
print("l113_run.py written + compiles clean")
