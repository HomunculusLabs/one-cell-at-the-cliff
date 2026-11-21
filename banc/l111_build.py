"""Build l111_run.py from l109_run.py via exact-string transforms.
Every pattern must occur the asserted number of times or we abort."""
import sys

SRC = open("l109_run.py").read()
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
rep('''"""L109 run: per-side membership-ladder rebase. PREREG l109/PREREG.md FIRST.

Arms identical to l107 (graphs, gains, draw order VERBATIM); seeds:
  ANCH = [801, 901] run FIRST (bit-identity anchors, excluded from sample)
  B7 1101-1116 + B8 1201-1216 (fresh, verified absent from raw_l94/l107)
g_cut re-bisected deterministically then asserted == stored l107 value.
CPU-only; raw checkpoint BEFORE analysis.
"""''',
    '''"""L111 run: glutamate-subset ladder slice. PREREG l111/PREREG.md FIRST.

L109 machinery VERBATIM (graphs, gains, draw order); arms full/b65/cut
identical, h65 dropped (settled 32/32 twice), cut19 NEW = closure minus the
19 glutamatergic cells of the heavy-77 (l110 addendum). Seeds: anchors
[801, 901] vs raw_l109 + FRESH B9 1301-1316 (verified absent pre-launch).
g_cut re-bisected + asserted == stored; g_cut19 bisected fresh (disclosed).
CPU-only; raw checkpoint BEFORE analysis.
"""''')

# 2. arms / gain
rep('ARMS = ["full", "b65", "h65", "cut"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, h65=GH, cut=None)  # cut set by bisect',
    'ARMS = ["full", "b65", "cut", "cut19"]\n'
    'GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None)  # both by bisect')

# 3. seeds
rep('''B7 = list(range(1101, 1117))
B8 = list(range(1201, 1217))
SEEDS = ANCH + B7 + B8              # anchors FIRST: early wiring verdict
FRESH = B7 + B8''',
    '''B9 = list(range(1301, 1317))        # fresh, verified absent pre-launch
SEEDS = ANCH + B9                   # anchors FIRST: early wiring verdict
FRESH = B9''')

# 4. cut19 derivation
rep('''assert (K, round(float(cum[K - 1]), 4)) == (ST["cut"]["K"], ST["cut"]["mass_share"])
assert int(keep_cut.sum()) == ST["n_cut"]''',
    '''assert (K, round(float(cum[K - 1]), 4)) == (ST["cut"]["K"], ST["cut"]["mass_share"])
assert int(keep_cut.sum()) == ST["n_cut"]
# L111: glutamatergic subset of the heavy-77 (l110 addendum: 19/77, z +5.9)
heav = dn_new_g[order[:K]]
cut19_drop = np.sort(heav[is_glut[heav]])
assert len(cut19_drop) == 19, f"glut heavy = {len(cut19_drop)} != 19 (STOP)"
keep_cut19 = keep_new.copy()
keep_cut19[cut19_drop] = False
n_cut19 = int(keep_cut19.sum())
assert n_cut19 == int(keep_new.sum()) - 19
_mass_heavy = cell_mass[order[:K]]
mass_split = dict(
    glut19=round(float(_mass_heavy[is_glut[heav]].sum() / cell_mass.sum()), 4),
    other58=round(float(_mass_heavy[~is_glut[heav]].sum() / cell_mass.sum()), 4))''')

# 5. graphs
rep('''Wc_o, loc_o = build(keep_old)
Wc_n, loc_n = build(keep_new)
Wc_c, loc_c = build(keep_cut)''',
    '''Wc_o, loc_o = build(keep_old)
Wc_n, loc_n = build(keep_new)
Wc_c, loc_c = build(keep_cut)
Wc_c19, loc_c19 = build(keep_cut19)''')
rep('Wb_o, Wb_n, Wb_c = wb(Wc_o), wb(Wc_n), wb(Wc_c)',
    'Wb_o, Wb_n, Wb_c, Wb_c19 = wb(Wc_o), wb(Wc_n), wb(Wc_c), wb(Wc_c19)')

# 6. positions
rep('''kept_new_mask = keep_cut[new_g]                      # new_g order
kept_new_cut = loc_c[new_g[kept_new_mask]]           # cut-local of kept new''',
    '''kept_new_mask = keep_cut[new_g]                      # new_g order
kept_new_cut = loc_c[new_g[kept_new_mask]]           # cut-local of kept new
gi_cut19 = np.where(keep_cut19)[0]
cut19_pos_in_new = loc_n[gi_cut19]
old_pos_in_c19 = loc_c19[gi_old]
kept_new_mask19 = keep_cut19[new_g]                  # new_g order
kept_new_cut19 = loc_c19[new_g[kept_new_mask19]]     # cut19-local of kept new''')

# 7. pools
rep('''POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "b65": pools_for(loc_o, keep_old), "h65": pools_for(loc_o, keep_old)}''',
    '''POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "b65": pools_for(loc_o, keep_old)}''')
rep('''    assert len(POOLS["cut"][pk]) == want and len(POOLS["b65"][pk]) == want''',
    '''    assert len(POOLS["cut"][pk]) == want and len(POOLS["b65"][pk]) == want
    assert len(POOLS["cut19"][pk]) == want, pk''')

# 8. mech
rep('''mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "b65": np.where(mech_mask[keep_old])[0],
        "h65": np.where(mech_mask[keep_old])[0]}''',
    '''mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "b65": np.where(mech_mask[keep_old])[0]}''')

# 9. motor
rep('''motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("b65", n_old), ("h65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("b65", keep_old, loc_o), ("h65", keep_old, loc_o)):''',
    '''motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19), ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19), ("b65", keep_old, loc_o)):''')

# 10. dng100
rep('''dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]]),
          "h65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}''',
    '''dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}''')

# 11. WB / N_OF
rep('''WB = {"full": Wb_n, "cut": Wb_c, "b65": Wb_o, "h65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "b65": n_old, "h65": n_old}''',
    '''WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "b65": n_old}''')

# 12. X-init blocks (settle + rollout) — cut19 init, drop h65 clones
rep('''    Xc_cut[old_pos_in_cut] = X0o
    Xc_cut[kept_new_cut] = X0n[kept_new_mask]
    Xo65 = X0o.clone()''',
    '''    Xc_cut[old_pos_in_cut] = X0o
    Xc_cut[kept_new_cut] = X0n[kept_new_mask]
    Xc_cut19 = torch.zeros(n_cut19, 1)
    Xc_cut19[old_pos_in_c19] = X0o
    Xc_cut19[kept_new_cut19] = X0n[kept_new_mask19]
    Xo65 = X0o.clone()''', count=2)
rep('''    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              b65=Xo65.clone(), h65=Xo65.clone())''',
    '''    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), b65=Xo65.clone())''')
rep('''    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             b65=Xo65.clone(), h65=Xo65.clone())''',
    '''    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), b65=Xo65.clone())''')

# 13. noise dicts (settle + rollout)
rep('noise = dict(full=nzn, cut=nzn[cut_pos_in_new], b65=nz_o, h65=nz_o)',
    'noise = dict(full=nzn, cut=nzn[cut_pos_in_new],\n'
    '                     cut19=nzn[cut19_pos_in_new], b65=nz_o)', count=3)

# 14. bisect: generalize + add cut19 bisect after the stored-exact assert
rep('''def bisect_af_mean(g):
    afs = []
    for s in ANCH:
        st = settle_states(s, dict(full=G_NEW, b65=G65, h65=GH, cut=g))
        afs.append(float((st["cut"] > 0.05).float().mean()))
    return float(np.mean(afs))''',
    '''def bisect_af_mean(g, arm="cut"):
    afs = []
    for s in ANCH:
        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g))
        afs.append(float((st[arm] > 0.05).float().mean()))
    return float(np.mean(afs))''')
rep('''log(f"g_cut {lo_g:.6f} == stored EXACT | af_final {af_final:.6f} "
    f"({time.time()-t0:.0f}s)")''',
    '''log(f"g_cut {lo_g:.6f} == stored EXACT | af_final {af_final:.6f} "
    f"({time.time()-t0:.0f}s)")

# L111: fresh bisect for the cut19 subnet (staircase disclosed)
lo2, hi2 = 0.12, 0.18
af_lo2, af_hi2 = bisect_af_mean(lo2, "cut19"), bisect_af_mean(hi2, "cut19")
log(f"cut19 bracket af({lo2})={af_lo2:.5f} af({hi2})={af_hi2:.5f} "
    f"target {AF_T:.5f}")
assert af_lo2 < AF_T < af_hi2, "cut19 bracket fail"
for it in range(24):
    mid = (lo2 + hi2) / 2
    if bisect_af_mean(mid, "cut19") < AF_T:
        lo2 = mid
    else:
        hi2 = mid
GAIN["cut19"] = lo2
af_final19 = bisect_af_mean(lo2, "cut19")
log(f"g_cut19 {lo2:.6f} | af_final19 {af_final19:.6f} "
    f"|af-target| {abs(af_final19 - AF_T):.2e} (staircase disclosed)")''')

# 15. partial/raw paths
rep('if os.path.exists("l109/raw_partial.npz"):', 'if os.path.exists("l111/raw_partial.npz"):')
rep('np.savez("l109/raw_partial.npz", **store)', 'np.savez("l111/raw_partial.npz", **store)')
rep('''np.savez_compressed("l109/raw_l109.npz", K=K, g_cut=GAIN["cut"],
                    g_full=G_NEW, g65=G65, gh=GH,
                    cut_drop=cut_drop, batches=np.array(SEEDS), **store)
log("raw_l109.npz checkpointed BEFORE analysis")''',
    '''np.savez_compressed("l111/raw_l111.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l111.npz checkpointed BEFORE analysis")''')

# 16. C0A anchors -> vs raw_l109 (full/b65/cut on 801+901)
rep('''z94 = np.load("l94/raw_l94.npz")
z107 = np.load("l107/raw_l107.npz")
c0a = {}
for s in (801, 901):  # full vs stored l94 cfn, both seeds
    for key in ["mm", "xm"] + list(POOLS["full"]):
        c0a[f"94_{key}_{s}"] = float(np.abs(
            store[f"{key}_full_{s}"] - z94[f"{key}_cfn_{s}"][:WIN]).max())
    c0a[f"94_af_{s}"] = abs(float(store[f"af_full_{s}"])
                            - float(z94[f"af_cfn_{s}"]))
for key in ["mm", "xm"] + list(POOLS["full"]):  # b65/h65/cut vs stored l107
    for a in ("b65", "h65", "cut"):
        c0a[f"107_{key}_{a}_801"] = float(np.abs(
            store[f"{key}_{a}_801"] - z107[f"{key}_{a}_801"][:WIN]).max())
out = dict(g_cut=GAIN["cut"], af_final=af_final, K=K,
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l109/anchors_run.json", "w"), indent=1)
log(f"C0A {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")''',
    '''z109 = np.load("l109/raw_l109.npz")
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
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")''')

if n_err:
    sys.exit(f"ABORT: {n_err} pattern mismatches — nothing written")
open("l111_run.py", "w").write(SRC)
import py_compile
py_compile.compile("l111_run.py", doraise=True)
print("l111_run.py written + compiles clean")
