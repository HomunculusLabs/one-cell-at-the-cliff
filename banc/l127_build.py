"""Build l127_run.py from l125_run.py via exact-string transforms.

L127 = coherence-vs-heaviness on FRESH B22: cutscr0 re-run same-batch
(contiguous-HEAVY adjacent decile, STORED-form gain from l125), cutcl40 =
k19 + ranks 40-49 (contiguous LIGHT decile, deterministic, FRESH bisect),
cutscrL1/2 = pinned-RNG scattered 10 mass-matched to cl40 (FRESH bisects).
(1) docstring splice (opener guard), (2) global arm renames cutscr1/2/3
-> cutcl40/cutscrL1/cutscrL2, (3) short var renames _s1/_s2/_s3 ->
_c40/_L1/_L2 (+ s1_/s2_/s3_ pos vars), (4) G_CUTSCR0_STORED const
inserted, (5) B20->B22 + seed range 2601-2616, (6) absence list +=
raw_l125 + raw_l126, (7) S125->S127 static load, (8) scr comment block ->
L127 wording, (9) scr assert table values INLINED from l127/static.json,
(10) stored bisect loop += cutscr0, fresh loop trims to cl40/scrL arms,
(11) output paths l125->l127 (resume FIRST — L39 direction class),
(12) NEW C0A-125 (4 arms incl scr0 vs raw_l125) + C0A-126 (3 arms vs
raw_l126) blocks, (13) out-dict + c0a_pass conjunction extended.
Residual scan (stale tokens, count-pinned) + py_compile; every rep
count-pinned (L123 anchored-rep discipline). Pin values INLINED FROM
l127/static.json.
"""
import json
import py_compile

SRC = open("l125_run.py").read()
S127 = json.load(open("l127/static.json"))
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


# 1. docstring splice (opener guard)
NEW_DOC = '''"""L127 run: contiguous-LIGHT-decile (coherence vs heaviness) on FRESH
B22. PREREG l127/PREREG.md FIRST (cl40 = k19 + ranks 40-49 contiguous
.2396 vs scrL1/2 scattered mass-matched .2406/.2386; scr0 re-run
same-batch as the contiguous-HEAVY context .2490).

L125 machinery VERBATIM (pools, graphs, draw order) — cutscr0 RESTORED
as a stored-form gain (l125 scr_fresh_gains, re-bisect EXACT; C0A-125);
cutcl40/cutscrL1/cutscrL2 = FRESH bisects (staircase + band DISCLOSED).
Re-rolled on FRESH B22 2601-2616 (asserted absent from raw_l113 + l115 +
l117 + l118 + l119 + l120 + l121 + l122 + l123 + l124 + l125 + l126).
C0A-123/124 retained on 3 shared arms + EXTENDED C0A-125 (4 arms incl
scr0) + NEW C0A-126 forward chain. CPU-only; raw checkpoint BEFORE
analysis.
"""'''
assert SRC.startswith('"""L125 run:') and SRC.count('"""L125 run:') == 1, \
    "docstring opener drift"
_doc_end = SRC.index('"""', 3) + 3
SRC = NEW_DOC + SRC[_doc_end:]
print("ok x1: run docstring spliced")

# 2. global arm renames
rep("cutscr1", "cutcl40", count=45)
rep("cutscr2", "cutscrL1", count=45)
rep("cutscr3", "cutscrL2", count=45)

# 3. short var renames (after arm renames; _s0 scr0 vars untouched)
rep("_s1", "_c40", count=28)
rep("_s2", "_L1", count=28)
rep("_s3", "_L2", count=28)
rep("s1_", "c40_", count=4)
rep("s2_", "L1_", count=4)
rep("s3_", "L2_", count=4)

# 4. G_CUTSCR0_STORED const inserted (scr0 = stored-form from l125)
rep('''G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)
# (L125: wA/wB stored consts removed — arms not run here; C0A-123 is
# retained on the 3 shared arms only.)''',
    '''G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)
G_CUTSCR0_STORED = 0.15423982501029967  # l125 scr fresh gain -> stored-form (C0A-125)
# (L127: wA/wB stored consts remain removed — arms not run here; scr0 is
# stored-form from l125; C0A-123/124 retained on the 3 shared arms only.)''',
    count=1)

# 5. batch rename + seed range (B20 docstring sites already spliced: 8)
rep("B20", "B22", count=8)
rep("B22 = list(range(2401, 2417))  # fresh, absent l113..l124 incl raw_l124",
    "B22 = list(range(2601, 2617))  # fresh, absent l113..l126 incl raw_l126",
    count=1)

# 6. absence list += raw_l125 + raw_l126
rep('''              "l124/raw_l124.npz"):''',
    '''              "l124/raw_l124.npz", "l125/raw_l125.npz",
              "l126/raw_l126.npz"):''', count=1)

# 7. static load S125 -> S127
rep('S125 = json.load(open("l125/static.json"))',
    'S127 = json.load(open("l127/static.json"))', count=1)
rep('S125["scr"]', 'S127["scr"]', count=1)

# 8. scr comment block -> L127 wording
rep('''# L125 scramble draws (l125/static.json pins): k19 + 10 NON-window ng
# cells. scr0 = deterministic max-mass (ranks 30-39, .2490); scr1-3 =
# pinned-RNG draws from the ranks-30-58 pool (masses DISCLOSED per draw;
# card amendment in PREREG).''',
    '''# L127 coherence-vs-heaviness (l127/static.json pins): k19 + 10
# NON-window ng cells. scr0 = contiguous-HEAVY adjacent decile (ranks
# 30-39, .2490, re-run same-batch, == l125 stored EXACT); cl40 =
# contiguous-LIGHT decile (ranks 40-49, deterministic); scrL1/2 =
# pinned-RNG scattered draws mass-matched to cl40 (card amendment in
# PREREG).''', count=1)

# 9. scr assert table values INLINED from l127/static.json
_newtab = "    (\"cutscr0\", {m0}, {e0}),\n".format(
    m0=S127["scr"]["cutscr0"]["mass_removed"], e0=S127["scr"]["cutscr0"]["edges"]) + \
    "".join("    (\"{a}\", {m}, {e}),\n".format(
        a=a, m=S127["scr"][a]["mass_removed"], e=S127["scr"][a]["edges"])
        for a in ("cutcl40", "cutscrL1", "cutscrL2")) + ")"
rep('''    ("cutscr0", 0.249, 643802),
    ("cutcl40", 0.2422, 643848),
    ("cutscrL1", 0.2409, 643807),
    ("cutscrL2", 0.2388, 643942),
)''',
    _newtab.rstrip("\n"), count=1)

# 10. bisect changes: scr0 -> stored-form loop; fresh loop trims
rep('for _a in ("cutng19", "cutng29"):',
    'for _a in ("cutng19", "cutng29", "cutscr0"):', count=1)
rep('_st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED}[_a]',
    '_st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,\n'
    '           "cutscr0": G_CUTSCR0_STORED}[_a]', count=1)
rep('''# L125 form: endpoint gains are STORED-FORM anchors (re-bisect EXACT,
# l121); scramble arms are FRESH bisects below. Staircase + band
# disclosures retained per PREREG (never an abort).''',
    '''# L127 form: endpoint gains are STORED-FORM anchors (re-bisect EXACT,
# l121/l125); cl40/scrL arms are FRESH bisects below. Staircase + band
# disclosures retained per PREREG (never an abort).''', count=1)
rep('''# L125 FRESH bisects: scramble arms (staircase + band DISCLOSED per
# PREREG — the .14-.16 band is a disclosure, never an abort).
for _a in ("cutscr0", "cutcl40", "cutscrL1", "cutscrL2"):''',
    '''# L127 FRESH bisects: cl40/scrL arms (staircase + band DISCLOSED per
# PREREG — the .14-.16 band is a disclosure, never an abort).
for _a in ("cutcl40", "cutscrL1", "cutscrL2"):''', count=1)

# 11. output paths l125 -> l127 (resume FIRST — L39 direction class).
# NOTE: the absence-list INPUT "l125/raw_l125.npz" (rep #6) must survive —
# only the savez OUTPUT site is renamed, matched by its savez context.
rep("l125/raw_partial.npz", "l127/raw_partial.npz", count=3)
rep('np.savez_compressed("l125/raw_l125.npz"',
    'np.savez_compressed("l127/raw_l127.npz"', count=1)
rep("l125/anchors_run.json", "l127/anchors_run.json", count=1)
rep("raw_l125.npz checkpointed", "raw_l127.npz checkpointed", count=1)

# 12. NEW C0A-125 (4 arms incl scr0 vs raw_l125) + C0A-126 (3 arms vs
# raw_l126), inserted before the c0a_new_pools log line.
rep('''c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}''',
    '''# C0A-125 (EXTENDED anchor class): 4 arms incl cutscr0 at stored seeds
# vs raw_l125 (l125 ran cutscr0 at all 18 seeds).
z125c = np.load("l125/raw_l125.npz")
c0a125 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29", "cutscr0"):
            c0a125[f"125_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z125c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29", "cutscr0"):
        c0a125[f"125_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z125c[f"af_{a}_{s}"]))
c0a125_max = max(c0a125.values())
c0a125_pass = bool(all(v == 0.0 for v in c0a125.values()))
log(f"C0A-125 (4 arms incl scr0) vs raw_l125: {'PASS' if c0a125_pass else 'FAIL'} "
    f"(max {c0a125_max:.1e}, {len(C0A120_KEYS)} keys x 4 arms x 2 seeds)")
# C0A-126 (NEW forward-chain class): {cutk5,cutng19,cutng29} at stored
# seeds vs raw_l126 (l126 ran every arm at all 18 seeds; scr/cl arms have
# no l126 counterpart — excluded by name).
z126c = np.load("l126/raw_l126.npz")
c0a126 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29"):
            c0a126[f"126_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z126c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29"):
        c0a126[f"126_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z126c[f"af_{a}_{s}"]))
c0a126_max = max(c0a126.values())
c0a126_pass = bool(all(v == 0.0 for v in c0a126.values()))
log(f"C0A-126 forward chain vs raw_l126: {'PASS' if c0a126_pass else 'FAIL'} "
    f"(max {c0a126_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")
c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}''',
    count=1)

# 12b. covered-keys log tail wording (scr0 now anchored vs raw_l125)
rep('''    "'cutscr0'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120)")''',
    '''    "'cutscr0'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120); "
    "cutscr0 vs raw_l125 (C0A-125); 3 arms vs raw_l126 (C0A-126)")''', count=1)

# 13. out-dict: fresh-gain tuple trims, scr0 stored-exact, c0a125/126 fields
rep('''           scr_fresh_gains={a: GAIN[a] for a in
                            ("cutscr0", "cutcl40", "cutscrL1", "cutscrL2")},''',
    '''           scr_fresh_gains={a: GAIN[a] for a in
                            ("cutcl40", "cutscrL1", "cutscrL2")},
           g_cutscr0_stored_exact=bool(GAIN["cutscr0"] == G_CUTSCR0_STORED),''',
    count=1)
rep('''           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutscr0", "cutcl40", "cutscrL1",
                                           "cutscrL2"))),''',
    '''           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutcl40", "cutscrL1",
                                           "cutscrL2"))),''', count=1)
rep('''           c0a124_max=c0a124_max, c0a124_pass=c0a124_pass,''',
    '''           c0a124_max=c0a124_max, c0a124_pass=c0a124_pass,
           c0a125_max=c0a125_max, c0a125_pass=c0a125_pass,
           c0a126_max=c0a126_max, c0a126_pass=c0a126_pass,''', count=1)
rep('''                          and c0a124_pass))''',
    '''                          and c0a124_pass and c0a125_pass
                          and c0a126_pass))''', count=1)

# ---- residual scan (stale tokens; the absence-list INPUT
# ---- "l125/raw_l125.npz" is the ONE deliberate l125 cross-reference)
for stale in ("cutscr1", "cutscr2", "cutscr3", "_s1", "_s2", "_s3",
              "B20", "S125", "2401", "2417", "l125/anchors"):
    c = SRC.count(stale)
    if c:
        print(f"STALE TOKEN SURVIVES: {stale!r} x{c}")
        n_err += 1
_deliberate = SRC.count('"l125/raw_l125.npz"')
if (_deliberate != 2 or '"l125/raw_l125.npz",\n' not in SRC
        or 'np.load("l125/raw_l125.npz")' not in SRC
        or SRC.count('np.savez_compressed("l125')):
    print(f"l125/raw_l125.npz input-reference count {_deliberate} != 2 "
          "(absence-list + C0A-125 np.load inputs; savez output must be 0)")
    n_err += 1
print("residual scan: clean" if not n_err else "residual scan: FAIL")

if n_err:
    raise SystemExit("BUILD REFUSED (pattern mismatches above)")
open("l127_run.py", "w").write(SRC)
py_compile.compile("l127_run.py", doraise=True)
print("l127_run.py written + py_compile OK")

# ---- input-direction check (L118 class): every npz/json path literal
import re
paths = sorted(set(re.findall(r'"((?:l1\d+|l9\d*|l92|l107)/[^"]+\.(?:npz|json))"', SRC)))
print("path literals (inputs must be PRIOR runs; outputs must be l127/):")
for p in paths:
    print("  ", p)
bad = [p for p in paths if p.startswith("l127/") and "raw_partial" not in p
       and "raw_l127" not in p and "anchors_run" not in p]
outs = [p for p in paths if p.startswith("l127/")]
ins = [p for p in paths if not p.startswith("l127/")]
print(f"inputs {len(ins)} prior-run paths, outputs {len(outs)} l127 paths")
