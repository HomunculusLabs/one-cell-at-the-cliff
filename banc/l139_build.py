"""L139 build: generate l139_run.py from l135_run.py via count-asserted
reps (lineage discipline: every find asserted count-exact; wrap-fragile
long blocks spliced on UNIQUE OPENERS + CLOSERS, never exact-matched;
residual token scan over CODE lines at the end; py_compile gate).

Design (PREREG l139/PREREG.md): keep ALL per-arm plumbing verbatim (the 7
dropped arms stay as spectators — never advanced once ARMS is subset;
arms evolve independently, certified by the C0A-135 bit-identity anchor),
subset ARMS to the 6 decisive arms, add an argv-driven per-set 1% edge
jitter on the base table, replace the bisect section (set 0 = stored
asserts; j>=1 = fresh af-matched bisects incl. full) and the anchor tail
(C0A-135 vs raw_l135 at 801/901, set 0 only).
"""

import py_compile

SRC = "l135_run.py"
DST = "l139_run.py"
s = open(SRC).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, n, old[:90])
    s = s.replace(old, new)
    print(f"rep ok ({c}x): {old.splitlines()[0][:70]}")


# ---- S1 docstring (opener-splice to next closing quotes) ----
i0 = s.find('"""L135 run:')
assert i0 == 0, i0
i1 = s.find('"""', i0 + 3)
assert i1 > 0
NEW_DOC = '''"""L139 run (set j = sys.argv[1]): GAIN-ENSEMBLE ROBUSTNESS of the
BANC identity cliff. PREREG l139/PREREG.md FIRST. 6 decisive arms
{full, cutng23, cutwA, cutng25, cutng25p, cutng29}; set 0 = base
(no jitter, stored-form gains asserted EXACT, seeds 801/901+B28 +
C0A-135 bit-identity vs raw_l135); sets 1-5 = 1% iid edge-weight
jitter (default_rng(2000+j)) on the BASE table — same per-edge
multiplier flows into every arm's build() — with FRESH af-matched
bisects (bracket [.10,.20]) on the jittered graphs, seeds B28 only.
FRESH B28 3201-3216 (asserted absent from ALL 59 stored npzs,
l139_precheck.py). l135_run.py machinery VERBATIM except the named
reps in l139_build.py; dropped arms are spectators (ARMS-subset;
independence certified by C0A-135). CPU-only; checkpoint per set
BEFORE anchors. Per-set partial resume partial_j{j}.npz.
"""'''
s = NEW_DOC + s[i1 + 3:]

# ---- S2 ARMS subset ----
rep('''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutng19", "cutng23", "cutwA", "cutng25", "cutng25p",
        "cutng26", "cutng29", "cutk5"]''',
    '''ARMS = ["full", "cutng23", "cutwA", "cutng25", "cutng25p",
        "cutng29"]  # L139: 6 decisive arms; other 7 = spectators (never advanced)''')

# ---- S3 GAIN subset ----
rep('''GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutng19=None, cutng23=None, cutwA=None, cutng25=None,
            cutng25p=None, cutng26=None, cutng29=None, cutk5=None)''',
    '''GAIN = dict(full=G_NEW, cutng23=None, cutwA=None, cutng25=None,
            cutng25p=None, cutng29=None)''')

# ---- S4 seeds block -> argv-driven set ----
rep('''B26 = list(range(3001, 3017))  # fresh, absent l113..l133 incl raw_l133
SEEDS = ANCH + B26                  # anchors FIRST: early wiring verdict
FRESH = B26''',
    '''import sys
SET_J = int(sys.argv[1])        # 0 = base (no jitter, stored gains); 1..5 jitter
B28 = list(range(3201, 3217))   # fresh for L139 (B27 3101-3116 reserved, L141)
SEEDS = (ANCH + B28) if SET_J == 0 else B28   # set 0: anchors FIRST
FRESH = B28''')

# ---- S5 jitter block after the base table ----
rep("w_syn = g_grp.to_numpy(np.float64)",
    """w_syn = g_grp.to_numpy(np.float64)

# L139 (PREREG A3): per-set edge-weight jitter, L2/diffduck15 form —
# 1% iid multiplicative on the BASE table (post-log1p application is
# inside build); sign preserved; ONE array instance flows into every
# arm's subnet extraction = same per-edge multiplier across arms.
if SET_J > 0:
    _rng = np.random.default_rng(2000 + SET_J)
    JIT = 1.0 + 0.01 * _rng.standard_normal(len(w_syn))
    assert np.isfinite(JIT).all() and JIT.min() > 0.9, (JIT.min(), JIT.max())
    log(f"jitter set {SET_J}: n {len(JIT):,} mean {JIT.mean():.6f} "
        f"std {JIT.std():.6f} min {JIT.min():.4f} max {JIT.max():.4f}")
else:
    JIT = None""")

# ---- S6 build(): jitter application (None path = bit-identical expr) ----
rep("    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]",
    """    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    jf = JIT[emask] if JIT is not None else None""")
rep("    vals = (np.log1p(gcount) * gsign_b2).astype(np.float32)",
    """    vals = (np.log1p(gcount) * gsign_b2).astype(np.float32) \\
        if jf is None else \\
        (np.log1p(gcount) * gsign_b2 * jf).astype(np.float32)""")

# ---- S7 bisect section (opener..closer inclusive) ----
OP = "# ---------------- P1 bisect for g_cut (l92 form, settle-only) ----------------"
CL = "# EXACT in the stored loop above."
assert s.count(OP) == 1 and s.count(CL) == 1
a, b = s.find(OP), s.find(CL) + len(CL)
NEW_BISECT = '''# ---------------- L139 bisects (settle-only; l92/l133 form) ----------------
ANCH = [11, 22, 33]
STAIRS = {}


def bisect_af_mean(g, arm="cut"):
    # l135 VERBATIM except ONE disclosed line: full honors g when it is
    # the arm under test (L139 bisects full under jitter per PREREG;
    # set 0 never calls this with arm="full", so chain anchors unaffected).
    afs = []
    for s in ANCH:
        st = settle_states(s, dict(full=g if arm == "full" else G_NEW,
                                  b65=G65, cut=g, cut19=g,
                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,
                                  cutng25=g, cutng25p=g, cutng23=g,
                                  cutng26=g, cutk5=g))
        afs.append(float((st[arm] > 0.05).float().mean()))
    return float(np.mean(afs))


if SET_J == 0:
    # base set: stored-form chain asserts (PREREG A2) — re-bisect EXACT
    for _a in ("cutng23", "cutwA", "cutng25", "cutng25p", "cutng29"):
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
        _st = {"cutwA": G_CUTWA_STORED, "cutng23": G_CUTNG23_STORED,
               "cutng25": G_CUTNG25_STORED,
               "cutng25p": G_CUTNG25P_STORED,
               "cutng29": G_CUTNG29_STORED}[_a]
        assert GAIN[_a] == _st, (_a, GAIN[_a], _st)
        af_d = bisect_af_mean(lo_d, _a)
        STAIRS[_a] = abs(af_d - AF_T)
        log(f"g_{_a} {lo_d:.6f} == stored EXACT | af_final {af_d:.6f} | "
            f"|af-target| {STAIRS[_a]:.2e} (staircase)")
else:
    # jitter sets: fresh af-matched bisect per arm incl. full (PREREG;
    # bracket [.10,.20]; stairs disclosed unrounded; assert < 2e-3)
    for _a in ARMS:
        lo_d, hi_d = 0.10, 0.20
        af_lo_d, af_hi_d = bisect_af_mean(lo_d, _a), bisect_af_mean(hi_d, _a)
        log(f"J{SET_J} {_a} bracket af({lo_d})={af_lo_d:.5f} "
            f"af({hi_d})={af_hi_d:.5f} target {AF_T:.5f}")
        assert af_lo_d < AF_T < af_hi_d, f"{_a} bracket fail"
        for it in range(24):
            mid = (lo_d + hi_d) / 2
            if bisect_af_mean(mid, _a) < AF_T:
                lo_d = mid
            else:
                hi_d = mid
        GAIN[_a] = lo_d
        af_d = bisect_af_mean(lo_d, _a)
        STAIRS[_a] = abs(af_d - AF_T)
        assert STAIRS[_a] < 2e-3, (_a, STAIRS[_a])
        _band = " [OUTSIDE .12-.18 lineage band — DISCLOSED]" \\
            if not (0.12 <= lo_d <= 0.18) else ""
        log(f"J{SET_J} g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "
            f"|af-target| {STAIRS[_a]:.2e} (staircase){_band}")'''
s = s[:a] + NEW_BISECT + s[b:]
print("rep ok (splice): bisect section")

# ---- S8 partial resume per set ----
rep('if os.path.exists("l135/raw_partial.npz"):\n    z = np.load("l135/raw_partial.npz")',
    '_PARTIAL = f"l139/partial_j{SET_J}.npz"\nif os.path.exists(_PARTIAL):\n    z = np.load(_PARTIAL)')
rep('    np.savez("l135/raw_partial.npz", **store)',
    '    np.savez(_PARTIAL, **store)')

# ---- S9 final savez (opener..closer inclusive) ----
OP = 'np.savez_compressed("l135/raw_l135.npz", K=K, g_cut=GAIN["cut"],'
CL = 'log("raw_l135.npz checkpointed BEFORE analysis")'
assert s.count(OP) == 1 and s.count(CL) == 1
a, b = s.find(OP), s.find(CL) + len(CL)
NEW_SAVEZ = '''np.savez_compressed(f"l139/raw_l139_j{SET_J}.npz", K=K, set_j=SET_J,
                    jit_seed=2000 + SET_J,
                    gains=np.array([GAIN[a] for a in ARMS]),
                    arms=np.array(ARMS),
                    stairs=np.array([float(STAIRS.get(a, np.nan))
                                     for a in ARMS]),
                    cutng23_drop=cutk_drop["cutng23"],
                    cutwA_drop=cutk_drop["cutwA"],
                    cutng25_drop=cutk_drop["cutng25"],
                    cutng25p_drop=cutk_drop["cutng25p"],
                    cutng29_drop=cutk_drop["cutng29"],
                    batches=np.array(SEEDS), **store)
log(f"raw_l139_j{SET_J}.npz checkpointed BEFORE anchors")'''
s = s[:a] + NEW_SAVEZ + s[b:]
print("rep ok (splice): final savez")

# ---- S10 anchor tail (opener .. EOF) ----
OP = "# ---------------- C0A (PREREG): FULL-BATCH anchors vs raw_l113 ----------------"
assert s.count(OP) == 1
a = s.find(OP)
NEW_TAIL = '''# ---------------- C0A-135 (L139 PREREG A1): set-0 bit-identity vs raw_l135 ----
# Set 0 only: the ARMS-subset transform must reproduce l135's stored
# traces for the 6 kept arms at the anchor seeds EXACTLY (arms evolve
# independently; dropped arms are spectators). Jitter sets have no
# stored twin BY CONSTRUCTION — their anchor is the in-run stored/assert
# discipline + af certification above.
out = dict(set_j=SET_J, jit_seed=2000 + SET_J,
           gains={a: GAIN[a] for a in ARMS},
           stairs={a: float(STAIRS.get(a, np.nan)) for a in ARMS})
if SET_J == 0:
    zprev = np.load("l135/raw_l135.npz")
    C0A_KEYS = ["mm", "xm"] + [f"{k}_{c}{s}" for k in ("Ti", "Tr")
                               for c in ("f", "e") for s in ("L", "R")]
    c0a = {}
    for a in ARMS:
        assert all(f"{k}_{a}_801" in zprev.files for k in C0A_KEYS), a
        for s in (801, 901):
            for key in C0A_KEYS:
                d = float(np.max(np.abs(
                    np.asarray(store[f"{key}_{a}_{s}"]) -
                    zprev[f"{key}_{a}_{s}"])))
                c0a[f"{key}_{a}_{s}"] = d
    c0a_max = max(c0a.values())
    out.update(c0a_nkeys=len(C0A_KEYS) * len(ARMS) * 2,
               c0a_max=c0a_max, c0a_pass=bool(c0a_max == 0.0))
else:
    out.update(c0a_max=None, c0a_pass=None)
json.dump(out, open(f"l139/anchors_j{SET_J}.json", "w"), indent=1)
if SET_J == 0:
    assert out["c0a_pass"], ("C0A-135 FAIL", out["c0a_max"])
    log(f"C0A-135 PASS (max {out['c0a_max']:.1e}, "
        f"{out['c0a_nkeys']} key-arm-seeds)")
log(f"set {SET_J} done {time.time()-t0:.0f}s")'''
s = s[:a] + NEW_TAIL + "\n"
print("rep ok (splice): anchor tail")

# ---- residual scan (CODE lines; comments/docstrings whitelisted by context) ----
open(DST, "w").write(s)
code_lines = []
for ln in s.splitlines():
    t = ln.strip()
    if t.startswith("#") or t.startswith('"""') or '"""' in t:
        continue
    code_lines.append(ln)
joined = "\n".join(code_lines)
for tok in ("B26", "raw_partial", 'raw_l135.npz", K=K', "NEW_ARMS="):
    assert tok not in joined, ("residual token survived", tok)
assert joined.count('"l135/raw_l135.npz"') == 1, "raw_l135 must be INPUT only"
assert 'np.load("l135/raw_l135.npz")' in joined
assert "SET_J" in joined and joined.count("SET_J") >= 8
assert 'ARMS = ["full", "cutng23"' in s
py_compile.compile(DST, doraise=True)
print(f"RESIDUAL SCAN CLEAN + py_compile OK -> {DST} ({len(s.splitlines())} lines)")
