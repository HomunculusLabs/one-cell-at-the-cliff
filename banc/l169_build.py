"""L169 build: count-asserted additive transform of l150_run.py -> l169_run.py.
Adds TWO arms (wAgN = cutwA graph @ g_cutng25; n25gW = cutng25 graph @
g_cutwA) aliased to their own-graph twins (l150 silW alias form), swaps the
batch to B35, repoints every output path to l169/, FIXES the inherited
resume-path direction bug (l150 checked its OWN partial and loaded l148's),
and appends the C0-NT non-triviality probe + af mismatch report.
No arm removed (L139 spectator law not needed); every rep count-asserted
(l131/l123 laws: full-indentation anchors, shared lines pinned across ALL
true sites). Residual scan over CODE lines at the end.
"""
import py_compile
import re

SRC = "l150_run.py"
DST = "l169_run.py"
s = open(SRC).read()
reps = []


def rep(old, new, n=1):
    c = s.count(old)
    assert c == n, (f"COUNT MISS {c} != {n}", old[:90])
    reps.append((old, new, n))
    return None


# ---- 1. header docstring ----
rep('''"""L150 run: silW batch rebase + eMot halves second batch. PREREG
l150/PREREG.md FIRST (registered before this build). Arms: full, b65,''',
    '''"""L169 run: pre-posting control (a), the GAIN-SWAP 2x2. PREREG
l169/PREREG.md FIRST (registered before this build). NEW ARMS: wAgN =
cutwA graph VERBATIM at g_cutng25, n25gW = cutng25 graph VERBATIM at
g_cutwA — the two off-diagonal cells of {graph} x {gain}. Both are
DELIBERATELY off their matched operating point (that is the test);
P-af direction registered instead of an af identity. C0-NT probe: a
swap arm bit-identical to its own-gain twin = VOID run. Inherited
arms (all seven) ride along for free forward-chain anchors and a
third batch. FRESH B35 3417-3432. Arms: full, b65,''')

# ---- 2. ARMS + GAIN dict ----
rep('''ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
        "eMotBot5"]
GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            silW=None, eMotTop5=None, eMotBot5=None)  # silW below (graph-id)''',
    '''ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
        "eMotBot5", "wAgN", "n25gW"]
GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            silW=None, eMotTop5=None, eMotBot5=None,
            wAgN=None, n25gW=None)  # silW/swap arms below''')

# ---- 3. batch ----
rep('''fresh bisects asserted == l145 stored gains EXACT). FRESH B33 3365-3380.''',
    '''fresh bisects asserted == l145 stored gains EXACT). FRESH B35 3417-3432.''')
rep('''B33 = list(range(3365, 3381))  # fresh (batch lineage in PREREG)''',
    '''B35 = list(range(3417, 3433))  # fresh (B34 = l154; lineage in PREREG)''')
rep('''SEEDS = ANCH + B33                  # anchors FIRST: early wiring verdict
FRESH = B33''',
    '''SEEDS = ANCH + B35                  # anchors FIRST: early wiring verdict
FRESH = B35''')
rep('''    assert not any(f"mm_full_{s}" in _zp.files for s in B33), \\
        ("B33 collides with " + _p + " (STOP)")
log(f"B33 absence across {len(_prevs)} stored npzs: PASS")''',
    '''    assert not any(f"mm_full_{s}" in _zp.files for s in B35), \\
        ("B35 collides with " + _p + " (STOP)")
log(f"B35 absence across {len(_prevs)} stored npzs: PASS")''')

# ---- 4. absence list gains the newer stored npzs (direction: INPUTS only) ----
rep('''          "l145/raw_partial.npz", "l148/raw_l148.npz",
          "l148/raw_partial.npz"]''',
    '''          "l145/raw_partial.npz", "l148/raw_l148.npz",
          "l148/raw_partial.npz", "l150/raw_l150.npz",
          "l150/raw_partial.npz", "l154/raw_l154.npz",
          "l154/raw_partial.npz"]''')

# ---- 5. alias block for the two swap arms (after the silW alias block) ----
rep('''N_OF["silW"] = n_cutk["cutwA"]

AMPA = np.zeros(WIN, np.float64)''',
    '''N_OF["silW"] = n_cutk["cutwA"]

# ---- L169: gain-swap arms. Graph objects are the SAME CSR objects as
# their own-gain twins (asserted by object identity below); the ONLY
# difference is the scalar GAIN. No clamp, no bisect.
for _sa, _tw, _Wtw in (("wAgN", "cutwA", Wb_wA), ("n25gW", "cutng25", Wb_p25)):
    POOLS[_sa] = POOLS[_tw]
    mech[_sa] = mech[_tw]
    motor[_sa] = motor[_tw]
    dng100[_sa] = dng100[_tw]
    WB[_sa] = _Wtw
    N_OF[_sa] = n_cutk[_tw]
assert WB["wAgN"] is WB["cutwA"] and WB["n25gW"] is WB["cutng25"], \\
    "L169 GRAPH-IDENTITY broken (STOP)"
assert N_OF["wAgN"] == n_cutk["cutwA"] and N_OF["n25gW"] == n_cutk["cutng25"]

AMPA = np.zeros(WIN, np.float64)''')

# ---- 6. X-dict sites (settle_states + rollout: 2 sites, same text) ----
rep('''              silW=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),
              eMotBot5=Xc_wA.clone(),''',
    '''              silW=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),
              eMotBot5=Xc_wA.clone(),
              wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),''')
rep('''             silW=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),
             eMotBot5=Xc_wA.clone(),''',
    '''             silW=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),
             eMotBot5=Xc_wA.clone(),
             wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),''')

# ---- 7. noise dicts: THREE true sites (l123 law), two indent families ----
rep('''                     silW=nzn[wA_pos_in_new], eMotTop5=nzn[wA_pos_in_new],
                     eMotBot5=nzn[wA_pos_in_new],''',
    '''                     silW=nzn[wA_pos_in_new], eMotTop5=nzn[wA_pos_in_new],
                     eMotBot5=nzn[wA_pos_in_new],
                     wAgN=nzn[wA_pos_in_new], n25gW=nzn[p25_pos_in_new],''',
    n=3)

# ---- 8. bisect gains-dict signature (l131 law: the 4th plumbing copy) ----
rep('''                                  cutng26=g, cutk5=g, silW=g,
                                  eMotTop5=g, eMotBot5=g))''',
    '''                                  cutng26=g, cutk5=g, silW=g,
                                  eMotTop5=g, eMotBot5=g,
                                  wAgN=g, n25gW=g))''')

# ---- 9. gain assignment for the swap arms + P-af registration ----
rep('''GAIN["silW"] = GAIN["cutwA"]  # graph-identity af-match (l144 A1 form)
assert GAIN["silW"] == G_CUTWA_STORED == GAIN["cutwA"], \\
    (GAIN["silW"], "silW/cutwA gain identity broken (STOP)")''',
    '''GAIN["silW"] = GAIN["cutwA"]  # graph-identity af-match (l144 A1 form)
assert GAIN["silW"] == G_CUTWA_STORED == GAIN["cutwA"], \\
    (GAIN["silW"], "silW/cutwA gain identity broken (STOP)")
# L169 swap: the OTHER arm's bisected gain, imported, never re-bisected.
GAIN["wAgN"] = GAIN["cutng25"]
GAIN["n25gW"] = GAIN["cutwA"]
assert GAIN["wAgN"] == G_CUTNG25_STORED and GAIN["n25gW"] == G_CUTWA_STORED, \\
    "L169 swap gains not the stored pair (STOP)"
assert GAIN["wAgN"] != GAIN["cutwA"] and GAIN["n25gW"] != GAIN["cutng25"], \\
    "L169 swap is a no-op (STOP)"
log(f"L169 swap gains | wAgN {GAIN['wAgN']:.9f} (cutwA graph) | "
    f"n25gW {GAIN['n25gW']:.9f} (cutng25 graph)")''')

# ---- 10. resume path: FIX the inherited direction bug (own output both) ----
rep('''if os.path.exists("l150/raw_partial.npz"):
    z = np.load("l148/raw_partial.npz")''',
    '''if os.path.exists("l169/raw_partial.npz"):
    z = np.load("l169/raw_partial.npz")   # L120 direction fix (l150 loaded l148)''')

# ---- 11. af asserts: keep house bound for all, add P-af direction ----
rep('''    af_c = {a: float((X[a] > 0.05).float().mean()) for a in ARMS}
    for a in ARMS:
        assert 0.01 < af_c[a] < 0.9, (a, af_c[a])
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}''',
    '''    af_c = {a: float((X[a] > 0.05).float().mean()) for a in ARMS}
    for a in ARMS:
        assert 0.01 < af_c[a] < 0.9, (a, af_c[a])
    # P-af (PREREG): swap arms are DELIBERATELY off the matched point.
    paf[seed] = dict(wAgN=af_c["wAgN"], n25gW=af_c["n25gW"],
                     cutwA=af_c["cutwA"], cutng25=af_c["cutng25"],
                     wAgN_above=bool(af_c["wAgN"] > AF_T),
                     n25gW_below=bool(af_c["n25gW"] < AF_T))
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}''')

# ---- 12. paf accumulator next to `store` ----
rep('''# ---------------- rollouts ----------------
store = {}''',
    '''# ---------------- rollouts ----------------
store = {}
paf = {}''')

# ---- 13. output paths ----
rep('''    np.savez("l150/raw_partial.npz", **store)''',
    '''    np.savez("l169/raw_partial.npz", **store)''')
rep('''np.savez_compressed("l150/raw_l150.npz", K=K,''',
    '''np.savez_compressed("l169/raw_l169.npz", K=K,''')
rep('''log("raw_l150.npz checkpointed BEFORE analysis")''',
    '''log("raw_l169.npz checkpointed BEFORE analysis")''')
rep('''json.dump(out, open("l150/anchors_run.json", "w"), indent=1)''',
    '''json.dump(out, open("l169/anchors_run.json", "w"), indent=1)''')

# ---- 14. savez gains for the swap arms (both savez calls) ----
rep('''                    g_silW=GAIN["silW"], g_eMotTop5=GAIN["eMotTop5"],''',
    '''                    g_silW=GAIN["silW"], g_eMotTop5=GAIN["eMotTop5"],
                    g_wAgN=GAIN["wAgN"], g_n25gW=GAIN["n25gW"],''')

# ---- 15. C0-NT probe + af report, spliced into the anchors out-dict ----
rep('''out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],''',
    '''# ---- C0-NT (PREREG): a swap arm bit-identical to its own-gain twin
# means the gain never entered the step loop -> VOID, read nothing.
nt = {}
for _sa, _tw in (("wAgN", "cutwA"), ("n25gW", "cutng25")):
    for s in (801, 901):
        nt[f"{_sa}_{s}"] = float(np.abs(
            store[f"mm_{_sa}_{s}"] - store[f"mm_{_tw}_{s}"]).max())
nt_pass = bool(all(v > 0.0 for v in nt.values()))
log(f"C0-NT swap-vs-own-gain mm separation: "
    f"{'PASS' if nt_pass else 'VOID'} (min {min(nt.values()):.3e})")
paf_ok = bool(all(d["wAgN_above"] and d["n25gW_below"] for d in paf.values()))
log(f"P-af direction (wAgN above / n25gW below AF_T) on "
    f"{len(paf)} seeds: {'PASS' if paf_ok else 'PARTIAL'}")
_afmis = {k: dict(wAgN=abs(d["wAgN"] - AF_T), n25gW=abs(d["n25gW"] - AF_T))
          for k, d in paf.items()}
log("af mismatch |af-AF_T| mean | wAgN "
    f"{np.mean([v['wAgN'] for v in _afmis.values()]):.4f} | n25gW "
    f"{np.mean([v['n25gW'] for v in _afmis.values()]):.4f}")
out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],''')

rep('''           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass))''',
    '''           g_wAgN=GAIN["wAgN"], g_n25gW=GAIN["n25gW"],
           nt=nt, nt_pass=nt_pass, paf=paf, paf_ok=paf_ok,
           af_target=AF_T,
           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass
                         and nt_pass))''')

# ---- apply ----
for old, new, n in reps:
    assert s.count(old) == n, ("DRIFT at apply", old[:80])
    s = s.replace(old, new)

# ---- residual scan over CODE lines (l126 law: whitelist by line context) ----
bad = []
for i, line in enumerate(s.split("\n"), 1):
    st = line.strip()
    if st.startswith("#") or st.startswith('"""') or st.startswith("'''"):
        continue
    # whitelist: pure string-literal elements of the _prevs INPUT absence
    # list (deliberate cross-references to prior runs' stored npzs — these
    # are read-only inputs; direction checked by hand above, l118/l120 law)
    if re.fullmatch(r'\s*(?:"l\d+/raw_[a-z0-9_]+\.npz",?\s*)+\]?', line):
        continue
    if re.search(r'l150/|"B33"|\bB33\b', line):
        bad.append((i, line))
assert not bad, ("RESIDUAL old-token code lines", bad)
# docstring/comment survivors are deliberate cross-references; list them
xref = [(i, l) for i, l in enumerate(s.split("\n"), 1)
        if re.search(r'l150|B33', l) and l.strip().startswith("#")]

open(DST, "w").write(s)
py_compile.compile(DST, doraise=True)
print(f"wrote {DST}: {len(reps)} reps applied, residual scan CLEAN")
print(f"deliberate comment cross-references kept: {len(xref)}")
for i, l in xref:
    print(f"  L{i}: {l.strip()[:100]}")
