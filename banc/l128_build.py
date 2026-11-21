"""l128_build.py — asserted exact-string transform l125_run.py -> l128_run.py.

L128: scr1/scr2/scr3 batch rebase on FRESH B23 (L125 machinery VERBATIM,
identical arm list; scr gains now STORED-FORM with re-bisect-EXACT asserts;
anchors extended: C0A-125 ALL-ARMS, C0A-126 retained, C0A-127 NEW forward).
Every rep count-pinned; residual scan + npz-direction check at the end.
"""
import re

SRC = open("l125_run.py").read()
n_reps = 0


def rep(old, new, count=1):
    global SRC, n_reps
    c = SRC.count(old)
    assert c == count, f"rep count {c} != {count}: {old[:70]!r}"
    SRC = SRC.replace(old, new)
    n_reps += 1


# R1: docstring (whole-block splice on the first triple-quote pair)
i0 = SRC.index('"""')
i1 = SRC.index('"""', i0 + 3) + 3
NEW_DOC = '''"""L128 run: scr1/scr2/scr3 BATCH REBASE on FRESH B23. PREREG
l128/PREREG.md FIRST (card amended by L127/tick 151: scr0 do-not-reroll as
the QUESTION — 2 batches banked; it still rolls here as a structural
necessity of the uniform arm set, banked as BONUS pooled n=48).

L125 machinery VERBATIM (pools, graphs, draw order) — IDENTICAL arm list:
the scr1-3 pinned draws re-derived from l125/static.json EXACT; every gain
STORED-FORM (deterministic re-bisects land EXACT; scr1/scr3 outside the
.14-.16 band, af-matched, disclosed). FRESH B23 2701-2716 (asserted absent
from raw_l113 + l115 + l117 + l118 + l119 + l120 + l121 + l122 + l123 +
l124 + l125 + l126 + l127). Anchors: C0A/C0A-120..124 retained, C0A-126
retained, C0A-125 EXTENDED to ALL 12 arms vs raw_l125, NEW C0A-127 forward
chain (9 shared arms) vs raw_l127. CPU-only; raw checkpoint BEFORE analysis.
"""'''
SRC = NEW_DOC + SRC[i1:]
n_reps += 1

# R2: batch definition
rep("B20 = list(range(2401, 2417))  # fresh, absent l113..l124 incl raw_l124",
    "B23 = list(range(2701, 2717))  # fresh, absent l113..l127 incl raw_l127")
# R3/R4: seed wiring
rep("SEEDS = ANCH + B20                  # anchors FIRST: early wiring verdict",
    "SEEDS = ANCH + B23                  # anchors FIRST: early wiring verdict")
rep("FRESH = B20", "FRESH = B23")
# R5: absence list extended through l127
rep('"l124/raw_l124.npz"):',
    '"l124/raw_l124.npz",\n              "l125/raw_l125.npz", "l126/raw_l126.npz",\n'
    '              "l127/raw_l127.npz"):')
# R6: fresh-batch comment + collision assert (2 B20 tokens in one span)
rep("# B20 is fresh: no stored counterpart (asserted absent pre-C0A)\n"
    'assert not any(f"mm_full_{s}" in zprev.files for s in B20), \\\n'
    '    "B20 collides with stored batches (STOP)"',
    "# B23 is fresh: no stored counterpart (asserted absent pre-C0A)\n"
    'assert not any(f"mm_full_{s}" in zprev.files for s in B23), \\\n'
    '    "B23 collides with stored batches (STOP)"')
# R7: scr stored-gain constants
rep("G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)",
    "G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)\n"
    "G_CUTSCR0_STORED = 0.15423982501029967  # l125 scr gain -> stored-form (l127 EXACT)\n"
    "G_CUTSCR1_STORED = 0.16989078283309933  # l125 scr gain -> stored-form\n"
    "G_CUTSCR2_STORED = 0.1424216973781586  # l125 scr gain -> stored-form\n"
    "G_CUTSCR3_STORED = 0.16503094553947448  # l125 scr gain -> stored-form")
# R8: scr bisect header comment
rep("# L125 FRESH bisects: scramble arms (staircase + band DISCLOSED per\n"
    "# PREREG — the .14-.16 band is a disclosure, never an abort).\n"
    'for _a in ("cutscr0", "cutscr1", "cutscr2", "cutscr3"):',
    "# L128: scr gains STORED-FORM (deterministic re-bisect lands EXACT on\n"
    "# the l125 scr gains — C0A(scr) anchor class; band still DISCLOSED).\n"
    'for _a in ("cutscr0", "cutscr1", "cutscr2", "cutscr3"):')
# R9: scr stored assert (insert between GAIN assignment and af_d — this
# exact pair is unique to the scr block; the ng block carries _st lines)
rep("    GAIN[_a] = lo_d\n    af_d = bisect_af_mean(lo_d, _a)\n"
    "    new_stairs[_a] = abs(af_d - AF_T)",
    "    GAIN[_a] = lo_d\n"
    '    _st = {"cutscr0": G_CUTSCR0_STORED, "cutscr1": G_CUTSCR1_STORED,\n'
    '           "cutscr2": G_CUTSCR2_STORED, "cutscr3": G_CUTSCR3_STORED}[_a]\n'
    "    assert GAIN[_a] == _st, (_a, GAIN[_a], _st)\n"
    "    af_d = bisect_af_mean(lo_d, _a)\n"
    "    new_stairs[_a] = abs(af_d - AF_T)")
# R10: own-output paths (resume + checkpoint + savez) — ALL THREE sites
rep('if os.path.exists("l125/raw_partial.npz"):',
    'if os.path.exists("l128/raw_partial.npz"):')
rep('z = np.load("l125/raw_partial.npz")',
    'z = np.load("l128/raw_partial.npz")')
rep('np.savez("l125/raw_partial.npz", **store)',
    'np.savez("l128/raw_partial.npz", **store)')
rep('np.savez_compressed("l125/raw_l125.npz"', 'np.savez_compressed("l128/raw_l128.npz"')
rep('log("raw_l125.npz checkpointed BEFORE analysis")',
    'log("raw_l128.npz checkpointed BEFORE analysis")')
# R10b: the per-_prev absence loop's own B20 collision assert (2 tokens)
rep('assert not any(f"mm_full_{s}" in _zp.files for s in B20), \\\n'
    '        ("B20 collides with " + _prev + " (STOP)")',
    'assert not any(f"mm_full_{s}" in _zp.files for s in B23), \\\n'
    '        ("B23 collides with " + _prev + " (STOP)")')
# R11: NEW anchor blocks (C0A-125 all-arms, C0A-126 retained, C0A-127
# forward) spliced before the c0a_new_pools summary line
ANCH_BLOCK = '''# C0A-125 (EXTENDED: ALL 12 arms): identical arm list to raw_l125, which
# ran every arm at all 18 seeds — the strongest chain form to date.
z125c = np.load("l125/raw_l125.npz")
C0A125_ARMS = ("full", "b65", "cut", "cut19", "cut58", "cutk5",
               "cutng19", "cutng29", "cutscr0", "cutscr1", "cutscr2",
               "cutscr3")
assert all(f"{_k}_cutscr3_801" in z125c.files for _k in C0A120_KEYS)
c0a125 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in C0A125_ARMS:
            c0a125[f"125_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z125c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in C0A125_ARMS:
        c0a125[f"125_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z125c[f"af_{a}_{s}"]))
c0a125_max = max(c0a125.values())
c0a125_pass = bool(all(v == 0.0 for v in c0a125.values()))
log(f"C0A-125 ALL 12 arms vs raw_l125: {'PASS' if c0a125_pass else 'FAIL'} "
    f"(max {c0a125_max:.1e}, {len(C0A120_KEYS)} keys x 12 arms x 2 seeds)")
# C0A-126 (retained): {cutk5,cutng19,cutng29} vs raw_l126 (3 shared arms).
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
log(f"C0A-126 (3 shared arms) vs raw_l126: {'PASS' if c0a126_pass else 'FAIL'} "
    f"(max {c0a126_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")
# C0A-127 (NEW forward chain): 9 shared arms vs raw_l127 (l127 ran every
# arm at all 18 seeds; cl40/scrL1/scrL2 have no L128 counterpart —
# excluded by name, DISCLOSED).
z127c = np.load("l127/raw_l127.npz")
C0A127_ARMS = ("full", "b65", "cut", "cut19", "cut58", "cutk5",
               "cutng19", "cutng29", "cutscr0")
assert all(f"{_k}_cutscr0_801" in z127c.files for _k in C0A120_KEYS)
c0a127 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in C0A127_ARMS:
            c0a127[f"127_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z127c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in C0A127_ARMS:
        c0a127[f"127_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z127c[f"af_{a}_{s}"]))
c0a127_max = max(c0a127.values())
c0a127_pass = bool(all(v == 0.0 for v in c0a127.values()))
log(f"C0A-127 forward chain vs raw_l127: {'PASS' if c0a127_pass else 'FAIL'} "
    f"(max {c0a127_max:.1e}, {len(C0A120_KEYS)} keys x 9 arms x 2 seeds)")
c0a_new_pools = sorted('''
rep("c0a_new_pools = sorted(", ANCH_BLOCK, 1)
# R12: out dict — new anchor keys, scr stored-exact flags, key rename
rep("           scr_fresh_gains={a: GAIN[a] for a in\n"
    '                            ("cutscr0", "cutscr1", "cutscr2", "cutscr3")},',
    "           scr_stored_gains={a: GAIN[a] for a in\n"
    '                            ("cutscr0", "cutscr1", "cutscr2", "cutscr3")},')
rep('           g_cutng19_stored_exact=bool(GAIN["cutng19"] == G_CUTNG19_STORED),\n'
    '           g_cutng29_stored_exact=bool(GAIN["cutng29"] == G_CUTNG29_STORED),',
    '           g_cutng19_stored_exact=bool(GAIN["cutng19"] == G_CUTNG19_STORED),\n'
    '           g_cutng29_stored_exact=bool(GAIN["cutng29"] == G_CUTNG29_STORED),\n'
    '           g_cutscr0_stored_exact=bool(GAIN["cutscr0"] == G_CUTSCR0_STORED),\n'
    '           g_cutscr1_stored_exact=bool(GAIN["cutscr1"] == G_CUTSCR1_STORED),\n'
    '           g_cutscr2_stored_exact=bool(GAIN["cutscr2"] == G_CUTSCR2_STORED),\n'
    '           g_cutscr3_stored_exact=bool(GAIN["cutscr3"] == G_CUTSCR3_STORED),')
rep("           c0a124_max=c0a124_max, c0a124_pass=c0a124_pass,",
    "           c0a124_max=c0a124_max, c0a124_pass=c0a124_pass,\n"
    "           c0a125_max=c0a125_max, c0a125_pass=c0a125_pass,\n"
    "           c0a126_max=c0a126_max, c0a126_pass=c0a126_pass,\n"
    "           c0a127_max=c0a127_max, c0a127_pass=c0a127_pass,")
rep("           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass\n"
    "                          and c0a121_pass and c0a122_pass and c0a123_pass\n"
    "                          and c0a124_pass))",
    "           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass\n"
    "                          and c0a121_pass and c0a122_pass and c0a123_pass\n"
    "                          and c0a124_pass and c0a125_pass and c0a126_pass\n"
    "                          and c0a127_pass))")
rep('json.dump(out, open("l125/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l128/anchors_run.json", "w"), indent=1)')

open("l128_run.py", "w").write(SRC)
print(f"l128_run.py written ({len(SRC)} chars, {n_reps} reps)")

# ---- residual scan: NO stale tokens in CODE lines (comments/docstrings
# may keep historical l125/B20 context per the l126 whitelist-by-context
# rule; 'l125/static.json' is a legitimate INPUT direction, whitelisted) ----
bad = []
for ln, line in enumerate(SRC.splitlines(), 1):
    stripped = line.strip()
    is_comment = stripped.startswith("#")
    in_doc = '"""' in SRC.split('"""')[0]  # only the header docstring
    if is_comment or (ln < 30 and in_doc):
        continue
    for tok in ("B20", "2401", '"l125/raw_partial.npz"',
                "B22", "l125/anchors_run", "scr_fresh_gains"):
        if tok in line:
            bad.append((ln, tok, line.strip()[:80]))
assert not bad, ("stale tokens in code lines", bad[:10])
print("residual scan: CLEAN (code lines)")

# ---- direction check: every np.savez*/np.load site has the right
# DIRECTION (own-output writes only to l128/, input reads only l1XX/) ----
writes = re.findall(r'np\.savez\w*\(\s*"(l1\d+/[^"]+\.npz)"', SRC)
assert set(writes) == {"l128/raw_l128.npz", "l128/raw_partial.npz"}, writes
loads = re.findall(r'np\.load\(\s*"(l1\d+/[^"]+\.npz)"', SRC)
own = {p for p in loads if p.startswith("l128/")}
assert own <= {"l128/raw_partial.npz"}, own  # resume-only self-read
inputs = set(loads) - own
assert all(re.match(r"l1\d\d/raw_", p) for p in inputs), inputs
print(f"direction check: {len(inputs)} input reads, writes {sorted(set(writes))}")

# ---- syntax gate before launch ----
import py_compile
py_compile.compile("l128_run.py", doraise=True)
print("py_compile OK")
