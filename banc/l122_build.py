"""Build l122_run.py + l122_verdict.py from l121_* via exact-string transforms.

Strategy: (1) docstring swaps, (2) wholesale B16->B17 (count-pinned) +
range literal 2001->2101, (3) absence list gains l121, (4) ng gains become
STORED-FORM asserts (l121 fresh gains re-land EXACT — L120 addendum rule),
(5) NEW C0A-121 forward-chain block (ng arms + cutk5 vs raw_l121 at
801/901), (6) out-dict edits, (7) output paths l121->l122 (INPUT paths
l113/l115/.../l121/static.json kept — direction check), (8) verdict:
fresh reads z121/B16 -> z122/B17, Part-4 classification REPLACED by the
R1/R2/R3 rebase reads + B16-cert + R4 pooled n=32 union (L90 form),
(9) residual scan + direction check + py_compile. Every rep prints its
count; zero/mismatched count aborts (drift guard).
"""
import py_compile
import sys

SRC = open("l121_run.py").read()
n_err = 0


def rep(old, new, count=None):
    global SRC, n_err
    c = SRC.count(old)
    if c == 0 or (count is not None and c != count):
        print(f"PATTERN MISMATCH ({c} != {count}): {old[:70]!r}")
        n_err += 1
        return
    SRC = SRC.replace(old, new)
    print(f"ok x{c}: {old[:48]!r}")


# 1. docstring (splice — exact-match on wrapped text is fragile; guard on
#    the unique opener instead)
NEW_DOC = '''"""L122 run: cutng19/cutng29 batch-rebase on FRESH B17. PREREG
l122/PREREG.md FIRST.

L121 machinery VERBATIM (9 arms, 5-pair pools, graphs, gains, draw
order) — identical dose ladder re-rolled on FRESH B17 2101-2116
(asserted absent from raw_l113 + l115 + l117 + l118 + l119 + l120 +
l121). ng gains cutng19/29/39 are STORED-FORM anchors now: re-bisects
asserted == l121 fresh gains EXACT (deterministic re-bisects re-land
EXACT, L120 addendum rule). C0A-120 retained (cutk5 vs raw_l120) +
NEW C0A-121 forward chain (cutk5/cutng19/cutng29/cutng39 vs raw_l121
at 801/901). CPU-only; raw checkpoint BEFORE analysis.
"""'''
assert SRC.startswith('"""L121 run: nonglut-dose-ladder.') and \
    SRC.count('"""L121 run:') == 1, "docstring opener drift"
_doc_end = SRC.index('"""', 3) + 3
SRC = NEW_DOC + SRC[_doc_end:]
print("ok x1: run docstring spliced")

# 2. batch labels + fresh range (docstring carried 2 of the 10 B16 sites)
rep("B16", "B17", count=8)
rep("list(range(2001, 2017))", "list(range(2101, 2117))", count=1)

# 3. absence list gains l121
rep('''              "l120/raw_l120.npz"):''',
    '''              "l120/raw_l120.npz", "l121/raw_l121.npz"):''', count=1)

# 4. stored ng gain consts
rep('''G_CUTK5_STORED = 0.13981970071792604  # l117 stored dose gain, C0A(k5)''',
    '''G_CUTK5_STORED = 0.13981970071792604  # l117 stored dose gain, C0A(k5)
G_CUTNG19_STORED = 0.15025991678237915  # l121 fresh gain -> stored-form (C0A-121)
G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)
G_CUTNG39_STORED = 0.1462542486190796  # l121 fresh gain -> stored-form (C0A-121)''',
    count=1)

# 5. ng bisect loop asserts stored EXACT
rep('''    GAIN[_a] = lo_d
    af_d = bisect_af_mean(lo_d, _a)''',
    '''    GAIN[_a] = lo_d
    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,
           "cutng39": G_CUTNG39_STORED}[_a]
    assert GAIN[_a] == _st, (_a, GAIN[_a], _st)
    af_d = bisect_af_mean(lo_d, _a)''', count=1)

# 6. C0A-121 block (insert before the c0a_new_pools summary)
rep('''c0a_new_pools = sorted(''',
    '''# C0A-121 (NEW anchor class): ng arms + cutk5 at stored seeds vs raw_l121.
# l121 ran every arm at all 18 seeds, so all four have stored counterparts
# on ALL pool keys (L120 addendum forward-chain rule).
z121 = np.load("l121/raw_l121.npz")
c0a121 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29", "cutng39"):
            c0a121[f"121_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z121[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29", "cutng39"):
        c0a121[f"121_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z121[f"af_{a}_{s}"]))
c0a121_max = max(c0a121.values())
c0a121_pass = bool(all(v == 0.0 for v in c0a121.values()))
log(f"C0A-121 ng arms vs raw_l121: {'PASS' if c0a121_pass else 'FAIL'} "
    f"(max {c0a121_max:.1e}, {len(C0A120_KEYS)} keys x 4 arms x 2 seeds)")
c0a_new_pools = sorted(''', count=1)

# 7. out dict: c0a121 + ng stored-exact booleans
rep('''           c0a120_max=c0a120_max, c0a120_pass=c0a120_pass,
           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass))''',
    '''           c0a120_max=c0a120_max, c0a120_pass=c0a120_pass,
           c0a121_max=c0a121_max, c0a121_pass=c0a121_pass,
           g_cutng19_stored_exact=bool(GAIN["cutng19"] == G_CUTNG19_STORED),
           g_cutng29_stored_exact=bool(GAIN["cutng29"] == G_CUTNG29_STORED),
           g_cutng39_stored_exact=bool(GAIN["cutng39"] == G_CUTNG39_STORED),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass
                          and c0a121_pass))''', count=1)

# 8. output paths (INPUT paths untouched: l121/static.json, l113, l120, l121 raws)
rep('if os.path.exists("l121/raw_partial.npz"):',
    'if os.path.exists("l122/raw_partial.npz"):', count=1)
rep('z = np.load("l121/raw_partial.npz")',
    'z = np.load("l122/raw_partial.npz")', count=1)
rep('np.savez("l121/raw_partial.npz", **store)',
    'np.savez("l122/raw_partial.npz", **store)', count=1)
rep('np.savez_compressed("l121/raw_l121.npz"',
    'np.savez_compressed("l122/raw_l122.npz"', count=1)
rep('log("raw_l121.npz checkpointed BEFORE analysis")',
    'log("raw_l122.npz checkpointed BEFORE analysis")', count=1)
rep('json.dump(out, open("l121/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l122/anchors_run.json", "w"), indent=1)', count=1)

open("l122_run.py", "w").write(SRC)

# ---------------- verdict ----------------
V = open("l121_verdict.py").read()


def vrep(old, new, count=None):
    global V, n_err
    c = V.count(old)
    if c == 0 or (count is not None and c != count):
        print(f"V PATTERN MISMATCH ({c} != {count}): {old[:70]!r}")
        n_err += 1
        return
    V = V.replace(old, new)
    print(f"v ok x{c}: {old[:48]!r}")


# V1. docstring
vrep('''"""L121 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
reads: (P1) Ti_R dose curve over the NON-glut ladder k in {0,19,29,39,58}
FRESH on B16 with the L118/L119/L120-registered kill criterion and the
MASS-FRACTION / POOL-COHERENCE / MIXED classification; (P2) cutk5 B16
replication read of the L120 XOR kill (4th batch or batch-drift
disclosed); per-side duty table 5 pairs x 9 arms; L-axis secondary;
Sr_R watch; sanity cells. PREREG l121/PREREG.md."""''',
     '''"""L122 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B16-cert of this machinery on raw_l121 vs results_l121.json BEFORE any
pooling, then the registered REBASE reads on FRESH B17 (kill criterion
VERBATIM): R1 cutng19 kill, R2 cutng29 raise, R3 endpoints (cut58 3rd
batch, cutk5 5th), R4 pooled batch-union B16+B17 n=32 full-precision
Wilson (L90 form — the CITABLE number); per-side duty table 5 pairs x 9
arms; L-axis + Sr_R watch; sanity cells. PREREG l122/PREREG.md."""''')

# V2. batches: B17 fresh, B16 kept as context
vrep('''B10 = list(range(1401, 1417))
B16 = list(range(2001, 2017))''',
     '''B10 = list(range(1401, 1417))
B17 = list(range(2101, 2117))
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)''')

# V3. loads: z122 + r121 context + anchors from l122
vrep('z121 = np.load("l121/raw_l121.npz")',
     'z121 = np.load("l121/raw_l121.npz")\nz122 = np.load("l122/raw_l122.npz")')
vrep('ar = json.load(open("l121/anchors_run.json"))',
     'ar = json.load(open("l122/anchors_run.json"))\n'
     'r121 = json.load(open("l121/results_l121.json"))')

# V4. p0 dict: c0a121 + ng stored-exact booleans
vrep('''          c0a120_pass=ar["c0a120_pass"], c0a120_max=ar["c0a120_max"],''',
     '''          c0a120_pass=ar["c0a120_pass"], c0a120_max=ar["c0a120_max"],
          c0a121_pass=ar["c0a121_pass"], c0a121_max=ar["c0a121_max"],
          g_cutng19_stored_exact=ar["g_cutng19_stored_exact"],
          g_cutng29_stored_exact=ar["g_cutng29_stored_exact"],
          g_cutng39_stored_exact=ar["g_cutng39_stored_exact"],''')
vrep('''p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])''',
     '''p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]
                  and p0["g_cutng39_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])''')
vrep('''print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + 4 stored gains:",''',
     '''print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (4 arms vs raw_l121) + 7 stored gains:",''')

# V5. fresh reads -> z122 / B17
vrep('[float(z121[f"af_{a}_{s}"]) for s in B16]',
     '[float(z122[f"af_{a}_{s}"]) for s in B17]', count=1)
vrep('all(0.01 < float(z121[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B16)',
     'all(0.01 < float(z122[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B17)',
     count=1)
vrep('t = side_k(z121, a, B16, pk)', 't = side_k(z122, a, B17, pk)', count=1)
vrep('_, Rfull = duty_seeds(z121, "full", B16, "Ti")',
     '_, Rfull = duty_seeds(z122, "full", B17, "Ti")', count=1)
vrep('_, Rd = duty_seeds(z121, a, B16, "Ti")',
     '_, Rd = duty_seeds(z122, a, B17, "Ti")', count=1)
vrep('float(z121["g_cutk5"])', 'float(z122["g_cutk5"])', count=2)
vrep('print("---- B16 per-side duty table ----")',
     'print("---- B17 per-side duty table ----")', count=1)

# V6. widened B17 disclosure bands
vrep('''band = {"Ti": dict(L=(0.30, 0.45), R=(0.35, 0.55)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}''',
     '''band = {"Ti": dict(L=(0.25, 0.48), R=(0.35, 0.58)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}''')
vrep('print("full-arm B16 band check (disclosure only):", band_ok)',
     'print("full-arm B17 band check (disclosure only):", band_ok)')

# V7. l121 context added beside the l117/l119/l120 ones
vrep('''dose["l120_stored_b15_context"] = {''',
     '''dose["l121_stored_b16_context"] = {
    "Ti_meanR": r121["dose"]["Ti"]["meanR"],
    "Ti_kR": r121["dose"]["Ti"]["kR"],
    "kill": r121["dose"]["Ti"]["kill"]}
dose["l120_stored_b15_context"] = {''')
vrep('''print("l117 B12 / l119 B14 / l120 B16 cross-batch context (no gate):",''',
     '''print("l117 B12 / l119 B14 / l120 B15 / l121 B16 cross-batch context:",''')

# V8. Part 4: classification REPLACED by rebase reads + B16-cert + pooled R4
vrep('''# ---- Part 4 (P1): MASS vs POOL classification (PREREG forms) ----
ng_kills = {k: killmap[k] for k in ("19", "29", "39")}
full_like = {k: (table["Ti"][a]["meanR"] >= m0 - .10)
             and (table["Ti"][a]["kR"] >= 12)
             for k, a in (("19", "cutng19"), ("29", "cutng29"),
                          ("39", "cutng39"))}
k58_kill = killmap["58"]
if ng_kills["19"]:
    p1_cls = ("MASS-FRACTION: cutng19 kills at .1946 — the non-glut R-kill "
              "tracks removed mass, firing well below pool completeness")
elif (not any(ng_kills.values())) and all(full_like.values()) and k58_kill:
    p1_cls = ("POOL-COHERENCE/THRESHOLD: no ng dose kills (all full-like) "
              "while cut58 kills in-batch — the non-glut kill needs "
              "near-whole-pool removal, mirroring the glut-side step at "
              "pool scale")
else:
    p1_cls = ("MIXED/LOTTERY (L118 class): per-dose kill booleans + means "
              "disclosed, no rounding to either story")
print(f"P1 classification: {p1_cls}")
# P2: cutk5 B16 replication read (registered, no gate)
k5_kill = killmap["k5"]
p2_cls = ("cutk5 KILLS on B16 — 4th batch replicate (B12/B14/B16/B16) of "
          "the L117 step / L119 placement / L120 XOR" if k5_kill else
          "cutk5 does NOT kill on B16 — batch-drift DISCLOSED (L118 "
          "lottery class); L120's B16 evidence stands, never a fail")
print(f"P2 cutk5 replication: {p2_cls}")''',
     '''# ---- Part 4: REBASE reads R1/R2/R3 + B16-cert + R4 pooled union ----
ng_kills = {k: killmap[k] for k in ("19", "29", "39")}
k58_kill = killmap["58"]
k5_kill = killmap["k5"]
r1 = dict(kill=bool(killmap["19"]), cls=(
    "cutng19 KILL replicates on B17 — the .1946 non-glut kill is "
    "BATCH-ROBUST (2/2 batches, pooled n=32 citable)" if killmap["19"] else
    "cutng19 does NOT kill on B17 — B16 kill reclassified batch-drawn "
    "(L88 class); L121 MASS-FRACTION firing amended single-batch"))
r2_raise = (table["Ti"]["cutng29"]["meanR"] >= m0
            and table["Ti"]["cutng29"]["kR"] >= 12
            and dose["Ti"]["legs"]["29"]["mean_paired_dR"] >= .20)
r2 = dict(raise_replicates=bool(r2_raise), cls=(
    "cutng29 raise REPLICATES on B17 — the middle-dose super-raise is "
    "batch-robust" if r2_raise else
    "cutng29 raise does NOT replicate on B17 — B16's .727 (highest R of "
    "any arm) is a single-batch draw; middle stays lottery (L118 class)"))
r3 = dict(cut58_kill=bool(k58_kill), cutk5_kill=bool(k5_kill), cls=(
    "cut58 kills (endpoint, 3rd batch) + cutk5 kills (5th consecutive "
    "batch B12/B14/B15/B16/B17)" if k58_kill and k5_kill else
    "endpoint miss DISCLOSED (registered R3, never silent)"))
print(f"R1: {r1['cls']}")
print(f"R2: {r2['cls']}")
print(f"R3: {r3['cls']}")
# B16-cert BEFORE pooling: recomputed B16 Ti cells == results_l121.json
b16_cert_fail = []
for a in ARMS:
    want = r121["table"]["Ti"][a]
    got = side_k(z121, a, B16, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b16_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b16_cert_fail, ("B16-cert FAIL (no pooling read)",
                           b16_cert_fail[:5])
print(f"B16-cert vs results_l121.json Ti table: PASS (all {len(ARMS)} arms)")
# R4: pooled batch-union, FULL-PRECISION Wilson, unrounded pins (L90)
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutng39", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    both = np.concatenate([Rb16, Rb17])
    k = int((both >= .5).sum())
    lb, ub = wilson(k, 32)
    pooled[a] = dict(k32=k, p_hat=k / 32, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()))
    print(f"POOLED Ti_R {a:7s} k {k}/32 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16) p_hat {k/32:.3f} "
          f"Wilson [{lb:.4f}, {ub:.4f}]")''')

# V9. out dict: rebase + pooled keys
vrep('''           classification=dict(cls=p1_cls, ng_kills=ng_kills,
                               full_like=full_like, k58_kill=k58_kill),
           cutk5_replication=dict(cls=p2_cls, k5_kill=k5_kill),''',
     '''           rebase=dict(r1=r1, r2=r2, r3=r3, ng_kills=ng_kills,
                       k58_kill=bool(k58_kill), k5_kill=bool(k5_kill)),
           pooled=pooled, b16_cert_pass=True,''')

# V10. results path
vrep('json.dump(out, open("l121/results_l121.json", "w"), indent=1)',
     'json.dump(out, open("l122/results_l122.json", "w"), indent=1)')
vrep('print("results_l121.json written")', 'print("results_l122.json written")')

open("l122_verdict.py", "w").write(V)

# ---------------- residual scan + direction check ----------------
bad = []
for f in ("l122_run.py", "l122_verdict.py"):
    s = open(f).read()
    if "results_l121.json\", \"w\"" in s or "raw_l121.npz\", \"w\"" in s:
        bad.append((f, "stale l121 OUTPUT literal"))
    for lit in ('"l121/PREREG.md"', "B16 = list(range(2001, 2017))"):
        if lit in s and f == "l122_run.py":
            bad.append((f, "stale " + lit))
# every l121/ path literal in outputs must be INPUTS (static/raws/results)
import re
for f in ("l122_run.py", "l122_verdict.py"):
    for m in re.finditer(r'"(l1\d+/[^"]+)"', open(f).read()):
        p = m.group(1)
        if p.startswith("l122/"):
            continue
        if not (p.endswith("static.json") or p.startswith(("l113/", "l115/",
                "l117/", "l118/", "l119/", "l120/"))
                or p in ("l121/raw_l121.npz", "l121/results_l121.json")):
            bad.append((f, "unexpected l-path " + p))
if "range(2001, 2017)" in open("l122_run.py").read():
    bad.append(("l122_run.py", "stale 2001 range in run"))
if "FRESH B16 2001" in SRC:
    bad.append(("l122_run.py", "stale B16 docstring"))
if n_err or bad:
    print("BUILD FAIL:", n_err, bad)
    sys.exit(1)
py_compile.compile("l122_run.py", doraise=True)
py_compile.compile("l122_verdict.py", doraise=True)
print("BUILD OK: l122_run.py + l122_verdict.py compiled; scans clean")
