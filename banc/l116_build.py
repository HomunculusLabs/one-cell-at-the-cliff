"""Build l116_run.py from l113_run.py via exact-string transforms.
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
    '''"""L116 run: flip-joint-scan. PREREG l116/PREREG.md FIRST.

L113 machinery VERBATIM (arms, graphs, gains, draw order, seeds): a
replication-form EXTENSION readout of l113's own B10 trajectories with
the pool set extended to the 5 semantic pairs (Ta/Sr/Pr NEW, l101 a/b
naming; Ti/Tr keep f/e names so C0A keys match). g_cut58 additionally
re-bisected + asserted == l113 stored EXACT (C0A(c58) class). C0A is
FULL-BATCH: all 18 seeds x 5 arms x l113 key schema == raw_l113 EXACT.
CPU-only; raw checkpoint BEFORE analysis.
"""''')

# 2. stored g_cut58 constant next to the other stored gains
rep('G_CUT_STORED = 0.14510760426521305  # l107 stored, PREREG C0A(c)',
    'G_CUT_STORED = 0.14510760426521305  # l107 stored, PREREG C0A(c)\n'
    'G_CUT58_STORED = 0.15417299151420596  # l113 stored, PREREG C0A(c58)')

# 3. B10 comment (replication-form, not fresh)
rep('B10 = list(range(1401, 1417))       # fresh, verified absent pre-launch',
    'B10 = list(range(1401, 1417))       # l113 own batch: replication-form (PREREG)')

# 4. l101 static sizes
rep('S92 = json.load(open("l92/static.json"))',
    'S92 = json.load(open("l92/static.json"))\n'
    'S101 = json.load(open("l101/static.json"))["sizes"]')

# 5. pools_for: extend to 5 pairs (Ti/Tr f/e + Ta/Sr/Pr a/b)
rep('''def pools_for(loc, keep):
    out = {}
    for k, fpat, epat in [
        ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
        ("Tr", has("trochanter") & has("flexor"),
         has("trochanter") & has("extensor")),
    ]:
        for c in ("fL", "fR", "eL", "eR"):
            sel = fpat if c[0] == "f" else epat
            m = keep[mgi] & sel & (side_m == SIDE_MAP[c[1].upper()])
            out[f"{k}_{c}"] = np.sort(loc[mgi[m]])
    return out''',
    '''def pools_for(loc, keep):
    out = {}
    # L116: 5 semantic pairs (l101/l101_run.py patterns VERBATIM); Ti/Tr
    # keep f/e names (C0A key match), new pairs use l101 a/b names.
    for k, fpat, epat, pf, pe in [
        ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor"),
         "f", "e"),
        ("Tr", has("trochanter") & has("flexor"),
         has("trochanter") & has("extensor"), "f", "e"),
        ("Ta", has("tarsus") & has("depressor"), has("tarsus") & has("levator"),
         "a", "b"),
        ("Sr", has("sternal") & has("anterior") & has("rotator"),
         has("sternal") & has("posterior") & has("rotator"), "a", "b"),
        ("Pr", has("promotor"), has("remotor"), "a", "b"),
    ]:
        for c in ("L", "R"):
            m = keep[mgi] & fpat & (side_m == SIDE_MAP[c])
            out[f"{k}_{pf}{c}"] = np.sort(loc[mgi[m]])
            m = keep[mgi] & epat & (side_m == SIDE_MAP[c])
            out[f"{k}_{pe}{c}"] = np.sort(loc[mgi[m]])
    return out''')

# 6. pool size asserts: keep l92 pins, add l101 pins + cross-check
rep('''for pk, want in S92["pool_sizes"].items():
    assert len(POOLS["full"][pk]) == want, pk
    assert len(POOLS["cut"][pk]) == want and len(POOLS["b65"][pk]) == want
    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk''',
    '''for pk, want in S92["pool_sizes"].items():
    assert len(POOLS["full"][pk]) == want, pk
    assert len(POOLS["cut"][pk]) == want and len(POOLS["b65"][pk]) == want
    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk
# L116 NEW pools: sizes == l101 static, all arms (drops are DNs, never motor)
for pk, want in S101.items():
    if pk.split("_")[0] in ("Ti", "Tr"):
        continue  # covered above via the f/e form + cross-check below
    assert len(POOLS["full"][pk]) == want, pk
    for a in ("cut", "cut19", "cut58", "b65"):
        assert len(POOLS[a][pk]) == want, (a, pk)
# cross-check: l101 a/b sizes == l92 f/e sizes (extraction drift tripwire)
for k, (ag, bg) in {"Ti": ("f", "e"), "Tr": ("f", "e")}.items():
    for sd in ("L", "R"):
        assert len(POOLS["full"][f"{k}_{ag}{sd}"]) == S101[f"{k}_a{sd}"], (k, sd)
        assert len(POOLS["full"][f"{k}_{bg}{sd}"]) == S101[f"{k}_b{sd}"], (k, sd)''')

# 7. cut58 bisect: assert == l113 stored EXACT (new C0A(c58) class)
rep('''GAIN["cut58"] = lo3
af_final58 = bisect_af_mean(lo3, "cut58")
log(f"g_cut58 {lo3:.6f} | af_final58 {af_final58:.6f} "
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")''',
    '''GAIN["cut58"] = lo3
af_final58 = bisect_af_mean(lo3, "cut58")
# C0A(c58): deterministic re-bisect must land on the stored l113 gain EXACT
assert GAIN["cut58"] == G_CUT58_STORED, (GAIN["cut58"], G_CUT58_STORED)
log(f"g_cut58 {lo3:.6f} == l113 stored EXACT | af_final58 {af_final58:.6f} "
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")''')

# 8. npz paths
rep('if os.path.exists("l113/raw_partial.npz"):',
    'if os.path.exists("l116/raw_partial.npz"):')
rep('np.savez("l113/raw_partial.npz", **store)',
    'np.savez("l116/raw_partial.npz", **store)')
rep('''np.savez_compressed("l113/raw_l113.npz", K=K, g_cut=GAIN["cut"],''',
    '''np.savez_compressed("l116/raw_l116.npz", K=K, g_cut=GAIN["cut"],''')
rep('log("raw_l113.npz checkpointed BEFORE analysis")',
    'log("raw_l116.npz checkpointed BEFORE analysis")')

# 9. C0A block: FULL-BATCH vs raw_l113, enumerated old keys only (L59 rule)
rep('''# ---------------- C0A (PREREG): anchors bit-identity ----------------
z111 = np.load("l111/raw_l111.npz")
c0a = {}
for s in (801, 901):  # full/b65/cut/cut19 vs stored l111 (itself C0A-cert vs l109)
    for key in ["mm", "xm"] + list(POOLS["full"]):
        for a in ("full", "b65", "cut", "cut19"):
            c0a[f"111_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z111[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("full", "b65", "cut", "cut19"):
        c0a[f"111_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(z111[f"af_{a}_{s}"]))''',
    '''# ---------------- C0A (PREREG): FULL-BATCH anchors vs raw_l113 ----------------
# Enumerated OLD keys only (L59 anchor-key rule): the 8 Ti/Tr pools + mm/xm.
# New Ta/Sr/Pr keys do not exist in z113 and are excluded BY NAME.
zprev = np.load("l113/raw_l113.npz")
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
    f" | NEW pools excluded by name: {c0a_new_pools}")''')

# 10. anchors out dict
rep('''out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           K=K, mass_split=mass_split,
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l113/anchors_run.json", "w"), indent=1)''',
    '''out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           g_cut58_stored_exact=bool(GAIN["cut58"] == G_CUT58_STORED),
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           K=K, mass_split=mass_split, n_seeds=len(SEEDS),
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l116/anchors_run.json", "w"), indent=1)''')

if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
open("l116_run.py", "w").write(SRC)
print("l116_run.py written OK")
