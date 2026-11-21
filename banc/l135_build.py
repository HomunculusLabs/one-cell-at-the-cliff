"""L135 build: count-asserted exact-string transform of l133_static.py ->
l135_static.py, l133_run.py -> l135_run.py, l133_verdict.py ->
l135_verdict.py (PREREG l135/PREREG.md FIRST). Every rep count-pinned;
residual token scans per section; py_compile all three outputs. Zero
tolerance: a count miss aborts BEFORE any rollout."""
import py_compile


def apply(src, reps, tag):
    for old, new, cnt in reps:
        n = src.count(old)
        assert n == cnt, (tag, "count miss", cnt, n, old[:70])
        src = src.replace(old, new)
    return src


# ================= STATIC TRANSFORM =================
st = open("l133_static.py").read()
ST = []
ST.append((
    '"""L133 STATIC derivation (zero rollouts): wA-plus-319-alone XOR pins.',
    '"""L135 STATIC re-pin (zero rollouts): NO new arm in L135 — the\n'
    'derivation is l133 VERBATIM and every pin must equal l133/static.json\n'
    'EXACT (L44 re-open-the-prior-run rule at its cheapest: a pure rebase\n'
    're-pins everything it inherits).', 1))
ST.append((
    'S131 = json.load(open("l131/static.json"))',
    'S131 = json.load(open("l131/static.json"))\n'
    'S133 = json.load(open("l133/static.json"))', 1))
ST.append((
    'os.makedirs("l133", exist_ok=True)\n'
    'json.dump(pins, open("l133/static.json", "w"), indent=1)\n'
    'print("l133/static.json written")',
    'assert pins == S133, ("L135 re-pin drift vs l133/static.json (STOP)",\n'
    '                      [k for k in pins if pins[k] != S133.get(k)])\n'
    'os.makedirs("l135", exist_ok=True)\n'
    'json.dump(pins, open("l135/static.json", "w"), indent=1)\n'
    'print("l135/static.json written == l133/static.json EXACT (no new arm)")',
    1))
st = apply(st, ST, "static")
for bad in ('makedirs("l133"', 'open("l133/static.json", "w")'):
    assert bad not in st, ("static stale token", bad)
assert st.count('S133 = json.load') == 1
open("l135_static.py", "w").write(st)
py_compile.compile("l135_static.py", doraise=True)
print("l135_static.py written + py_compile OK")

# ================= RUN TRANSFORM =================
run = open("l133_run.py").read()
R = []

# ---- docstring ----
R.append((
    '"""L133 run: wA-plus-319-ALONE XOR on FRESH B25. PREREG\n'
    'l133/PREREG.md FIRST (cutng25p = wA + rank 26 (id 319) ONLY — NOT a\n'
    'prefix, skips rank 25/id 1110; if 25p PARTIALs -> clean identity XOR\n'
    'at mass-match; if SUPERs -> flip position-thin, both cells complete;\n'
    'registered degenerate branch W3 = neither).',
    '"""L135 run: cutng25p BATCH REBASE on FRESH B26. PREREG\n'
    'l135/PREREG.md FIRST (pool 25p across the l133 batch + B26 n=32 so\n'
    'the W3 band-edge (.508, kR 7/16 in, meanR out by .008) and the\n'
    '319-neutral decomposition become citable robust — or dissolve into\n'
    'batch swing; registered branches R1 intermediate-stable / R2\n'
    'kill-draw / R3 raise-draw).', 1))
R.append((
    'L131 machinery VERBATIM (pools, graphs, draw order) — cutng25 now\n'
    'stored-form (l131 fresh gain); cutng25p the ONE fresh bisect\n'
    '(staircase + .14-.16 band DISCLOSED, never abort). FRESH B25\n'
    '2901-2916 (asserted absent from raw_l113 + l115 + l117 + l118 +\n'
    'l119 + l120 + l121 + l122 + l123 + l124 + l125 + l126 + l127 +\n'
    'l128 + l131). Anchors: C0A/C0A-120..128 retained, NEW C0A-131 (10\n'
    'shared cut arms vs raw_l131) forward chain. CPU-only; raw checkpoint\n'
    'BEFORE analysis.\n'
    '"""',
    'L133 machinery VERBATIM (arms, pools, graphs, draw order) — ZERO\n'
    'fresh bisects, the first ALL-STORED run in the lineage: cutng25p\n'
    'promoted to stored-form (l133 fresh gain 0.1435265743732452; every\n'
    're-bisect must land EXACT, asserted). FRESH B26 3001-3016 (asserted\n'
    'absent from raw_l113 + l115 + l117 + l118 + l119 + l120 + l121 +\n'
    'l122 + l123 + l124 + l125 + l126 + l127 + l128 + l131 + l133).\n'
    'Anchors: C0A/C0A-120..128/C0A-131 retained, NEW C0A-133 (ALL 13\n'
    'arms vs raw_l133) forward chain. CPU-only; raw checkpoint BEFORE\n'
    'analysis.\n'
    '"""', 1))

# ---- stored gain const ----
R.append((
    'G_CUTNG25_STORED = 0.1454454553127289  # l131 fresh gain -> stored-form (C0A-131)',
    'G_CUTNG25_STORED = 0.1454454553127289  # l131 fresh gain -> stored-form (C0A-131)\n'
    'G_CUTNG25P_STORED = 0.1435265743732452  # l133 fresh gain -> stored-form (C0A-133)',
    1))

# ---- static load ----
R.append((
    'S133 = json.load(open("l133/static.json"))\n'
    'NEW_ARMS = (',
    'S133 = json.load(open("l133/static.json"))\n'
    'S135 = json.load(open("l135/static.json"))\n'
    'assert S135 == S133  # L135 re-pin EXACT (no new arm)\n'
    'NEW_ARMS = (', 1))

# ---- seeds line (BEFORE the global B25 count) ----
R.append((
    'B25 = list(range(2901, 2917))  # fresh, absent l113..l131 incl raw_l131',
    'B26 = list(range(3001, 3017))  # fresh, absent l113..l133 incl raw_l133',
    1))

# ---- stored loop: add 25p ----
R.append((
    'for _a in ("cutng19", "cutng29", "cutwA", "cutng23", "cutng25",\n'
    '           "cutng26"):',
    'for _a in ("cutng19", "cutng29", "cutwA", "cutng23", "cutng25",\n'
    '           "cutng25p", "cutng26"):', 1))
R.append((
    '    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,\n'
    '           "cutwA": G_CUTWA_STORED, "cutng23": G_CUTNG23_STORED,\n'
    '           "cutng25": G_CUTNG25_STORED,\n'
    '           "cutng26": G_CUTNG26_STORED}[_a]',
    '    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,\n'
    '           "cutwA": G_CUTWA_STORED, "cutng23": G_CUTNG23_STORED,\n'
    '           "cutng25": G_CUTNG25_STORED,\n'
    '           "cutng25p": G_CUTNG25P_STORED,\n'
    '           "cutng26": G_CUTNG26_STORED}[_a]', 1))

# ---- retire the fresh bisect block (splice on the unique opener) ----
R.append((
    '# L133 FRESH bisect: cutng25p only (staircase + band DISCLOSED per\n'
    '# PREREG — the .14-.16 band is a disclosure, never an abort).\n'
    'for _a in ("cutng25p",):\n'
    '    lo_d, hi_d = 0.12, 0.18\n'
    '    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _a), bisect_af_mean(hi_d, _a)\n'
    '    log(f"{_a} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "\n'
    '        f"target {AF_T:.5f}")\n'
    '    assert af_lo_d < AF_T < af_hi_d, f"{_a} bracket fail"\n'
    '    for it in range(24):\n'
    '        mid = (lo_d + hi_d) / 2\n'
    '        if bisect_af_mean(mid, _a) < AF_T:\n'
    '            lo_d = mid\n'
    '        else:\n'
    '            hi_d = mid\n'
    '    GAIN[_a] = lo_d\n'
    '    af_d = bisect_af_mean(lo_d, _a)\n'
    '    new_stairs[_a] = abs(af_d - AF_T)\n'
    '    _band = " [OUTSIDE PREREG band .14-.16 — DISCLOSED]" \\\n'
    '        if not (0.14 <= lo_d <= 0.16) else ""\n'
    '    log(f"g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "\n'
    '        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")\n',
    '# L135: ZERO fresh bisects (first all-stored run) — the l133 fresh\n'
    '# cutng25p loop is RETIRED; the gain is G_CUTNG25P_STORED, asserted\n'
    '# EXACT in the stored loop above.\n', 1))

# ---- paths ----
R.append(('if os.path.exists("l133/raw_partial.npz"):',
          'if os.path.exists("l135/raw_partial.npz"):', 1))
R.append(('    z = np.load("l133/raw_partial.npz")',
          '    z = np.load("l135/raw_partial.npz")', 1))
R.append(('    np.savez("l133/raw_partial.npz", **store)',
          '    np.savez("l135/raw_partial.npz", **store)', 1))
R.append(('np.savez_compressed("l133/raw_l133.npz", K=K, g_cut=GAIN["cut"],',
          'np.savez_compressed("l135/raw_l135.npz", K=K, g_cut=GAIN["cut"],', 1))
R.append(('log("raw_l133.npz checkpointed BEFORE analysis")',
          'log("raw_l135.npz checkpointed BEFORE analysis")', 1))
R.append(('json.dump(out, open("l133/anchors_run.json", "w"), indent=1)',
          'json.dump(out, open("l135/anchors_run.json", "w"), indent=1)', 1))

# ---- absence tuple: add raw_l133 ----
R.append((
    '              "l128/raw_l128.npz", "l131/raw_l131.npz"):',
    '              "l128/raw_l128.npz", "l131/raw_l131.npz",\n'
    '              "l133/raw_l133.npz"):', 1))

# ---- NEW C0A-133 block (insert before c0a_new_pools) ----
R.append((
    'c0a_new_pools = sorted(',
    '# C0A-133 (NEW): ALL 13 arms vs raw_l133 (l133 ran every arm at both\n'
    '# anchor seeds — L120 forward-chain law; incl cutng25p itself).\n'
    'z133c = np.load("l133/raw_l133.npz")\n'
    '_arms133 = ("full", "b65", "cut", "cut19", "cut58", "cutk5", "cutng19",\n'
    '            "cutng23", "cutwA", "cutng25", "cutng25p", "cutng26",\n'
    '            "cutng29")\n'
    'assert all(f"{_k}_{_a}_801" in z133c.files for _k in C0A120_KEYS\n'
    '           for _a in _arms133), "C0A-133 coverage miss"\n'
    'c0a133 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A120_KEYS:\n'
    '        for a in _arms133:\n'
    '            c0a133[f"133_{key}_{a}_{s}"] = float(np.abs(\n'
    '                store[f"{key}_{a}_{s}"] - z133c[f"{key}_{a}_{s}"][:WIN]).max())\n'
    '    for a in _arms133:\n'
    '        c0a133[f"133_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])\n'
    '                                        - float(z133c[f"af_{a}_{s}"]))\n'
    'c0a133_max = max(c0a133.values())\n'
    'c0a133_pass = bool(all(v == 0.0 for v in c0a133.values()))\n'
    'log(f"C0A-133 forward chain vs raw_l133: {\'PASS\' if c0a133_pass else \'FAIL\'} "\n'
    '    f"(max {c0a133_max:.1e}, {len(C0A120_KEYS)} keys x 13 arms x 2 seeds)")\n'
    'c0a_new_pools = sorted(', 1))

# ---- out dict fields ----
R.append((
    '           c0a131_max=c0a131_max, c0a131_pass=c0a131_pass,',
    '           c0a131_max=c0a131_max, c0a131_pass=c0a131_pass,\n'
    '           c0a133_max=c0a133_max, c0a133_pass=c0a133_pass,\n'
    '           g_cutng25p_stored_exact=bool(GAIN["cutng25p"] == G_CUTNG25P_STORED),',
    1))
R.append((
    '           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16\n'
    '                                 for a in ("cutng25p",))),',
    '           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16\n'
    '                                 for a in ())),  # L135: zero fresh bisects',
    1))
R.append((
    '           prefix_fresh_gains={a: GAIN[a] for a in ("cutng25p",)},',
    '           prefix_fresh_gains={},  # L135: zero fresh bisects (all-stored)',
    1))
R.append((
    '                          and c0a127_pass and c0a128_pass\n'
    '                          and c0a131_pass))',
    '                          and c0a127_pass and c0a128_pass\n'
    '                          and c0a131_pass and c0a133_pass))', 1))

run = apply(run, R, "run")

# global B25 -> B26 for all remaining sites (7: SEEDS/FRESH lines x2,
# fresh-comment, 2 asserts + 2 collision messages)
n = run.count("B25")
assert n == 7, ("global B25 count miss", n)
run = run.replace("B25", "B26")

# residual scan: no stale OUTPUT tokens
for bad in ('"l133/raw_partial', "l133/raw_l133.npz\", K=K",
            "l133/anchors_run.json", 'for _a in ("cutng25p",)'):
    assert bad not in run, ("stale token", bad)
# raw_l133 / l133/static references that REMAIN must be deliberate reads
# of the prior run (np.load input / absence tuple) — whitelist by LINE
# CONTEXT (l126 refinement), never by token enumeration
for i, line in enumerate(run.splitlines()):
    if "l133/" in line:
        assert ("np.load" in line or '"l133/raw_l133.npz"' in line
                or "static.json" in line
                or "l133/raw_l133" in line.split("#", 1)[1]
                if "#" in line else True) or line.lstrip().startswith("#") or i < 16, \
            ("unwhitelisted l133/ ref", i, line)
# plumbing spot-greps
assert run.count("G_CUTNG25P_STORED") == 4, run.count("G_CUTNG25P_STORED")
for probe in ("c0a133_pass", "z133c", "g_cutng25p_stored_exact",
              "B26 = list(range(3001, 3017))"):
    assert run.count(probe) >= 1, ("missing plumbing", probe)
assert "B25" not in run, "B25 survived"

open("l135_run.py", "w").write(run)
py_compile.compile("l135_run.py", doraise=True)
print(f"l135_run.py written ({len(run.splitlines())} lines) + py_compile OK")

# ================= VERDICT TRANSFORM =================
v = open("l133_verdict.py").read()
V = []
V.append((
    '"""L133 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +\n'
    'B24-cert of this machinery on raw_l131 vs results_l131.json (ALL its\n'
    'table arms) BEFORE any B25 read, then the registered XOR reads on FRESH\n'
    'B25 (criteria VERBATIM): W1 cutng25p PARTIAL -> clean identity XOR at\n'
    'mass-match (1110 completes, 319 does not); W2 cutng25p SUPER/RESTORE ->\n'
    'flip position-thin, BOTH cells complete; W3 registered degenerate\n'
    'branch. P2 mass-twin disclosure (static pins). P3 pooled transition\n'
    'arms {ng23, wA, ng26, ng29} B21+B24+B25 n=48 Wilson; ng25 2nd batch\n'
    'n=32 (X1 replication). S1 cutk5 13th batch pooled B16..B25 n=160;\n'
    'S2 endpoints 10th batch; S3 wA partial 5th batch; S4 ng25 SUPER 2nd\n'
    'batch; per-side duty table 5 pairs x 13 arms; Ti_L/Tr_R/Sr_R watch;\n'
    'sanity cells. PREREG l133/PREREG.md."""',
    '"""L135 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +\n'
    'B25-cert of this machinery on raw_l133 vs results_l133.json (ALL its\n'
    '13 table arms) BEFORE any B26 read, then the registered rebase reads\n'
    'on FRESH B26 (criteria VERBATIM): R1 25p intermediate-stable (window\n'
    '+ pooled B25+B26 n=32 Wilson CONTAINS .5) -> the 319-neutral\n'
    'decomposition is citable pooled; R2 kill-draw (B25 .508 was a draw,\n'
    'downgrade disclosed); R3 raise-draw (position-thin revives late).\n'
    'P2 mass-twin disclosure (static pins). P3 pooled transition arms\n'
    '{ng23, wA, ng26, ng29} B21+B24+B25+B26 n=64 Wilson; ng25 3rd batch\n'
    'n=48; ng25p pooled B25+B26 n=32 (the card read). S1 cutk5 14th batch\n'
    'pooled B16..B26 n=176; S2 endpoints 11th batch; S3 wA partial 6th\n'
    'batch; S4 ng25 SUPER 3rd batch; per-side duty table 5 pairs x 13\n'
    'arms; Ti_L/Tr_R/Sr_R watch; sanity cells. PREREG l135/PREREG.md."""',
    1))
V.append((
    'B25 = list(range(2901, 2917))       # FRESH (l133)\n'
    'B24 = list(range(2801, 2817))  # context batch (l131, cert + pooled)',
    'B26 = list(range(3001, 3017))       # FRESH (l135)\n'
    'B25 = list(range(2901, 2917))  # context batch (l133, cert + pooled)\n'
    'B24 = list(range(2801, 2817))  # context batch (l131, pooled)', 1))
V.append((
    'z133 = np.load("l133/raw_l133.npz")',
    'z133 = np.load("l133/raw_l133.npz")\n'
    'z135 = np.load("l135/raw_l135.npz")', 1))
V.append((
    'ar = json.load(open("l133/anchors_run.json"))\n'
    'r131 = json.load(open("l131/results_l131.json"))',
    'ar = json.load(open("l135/anchors_run.json"))\n'
    'r131 = json.load(open("l131/results_l131.json"))\n'
    'r133 = json.load(open("l133/results_l133.json"))', 1))

# fresh reads: z133/B25 -> z135/B26 (the pooled blocks KEEP z133/B25)
V.append((
    'af_mean = {a: round(float(np.mean([float(z133[f"af_{a}_{s}"]) for s in B25])), 6)\n'
    '           for a in ARMS}\n'
    'af_range_ok = all(0.01 < float(z133[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B25)',
    'af_mean = {a: round(float(np.mean([float(z135[f"af_{a}_{s}"]) for s in B26])), 6)\n'
    '           for a in ARMS}\n'
    'af_range_ok = all(0.01 < float(z135[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B26)',
    1))
V.append(('        t = side_k(z133, a, B25, pk)',
          '        t = side_k(z135, a, B26, pk)', 1))
V.append(('print("---- B25 per-side duty table ----")',
          'print("---- B26 per-side duty table ----")', 1))
V.append(('# ---- batch-band disclosure: full-arm B25 reads vs registered bands ----',
          '# ---- batch-band disclosure: full-arm B26 reads vs registered bands ----', 1))
V.append(('print("full-arm B25 band check (disclosure only):", band_ok)',
          'print("full-arm B26 band check (disclosure only):", band_ok)', 1))
V.append(('_, Rfull = duty_seeds(z133, "full", B25, "Ti")',
          '_, Rfull = duty_seeds(z135, "full", B26, "Ti")', 1))
V.append(('    _, Rd = duty_seeds(z133, a, B25, "Ti")',
          '    _, Rd = duty_seeds(z135, a, B26, "Ti")', 1))
V.append(('      "cutwA", round(float(z133["g_cutwA"]), 6),',
          '      "cutwA", round(float(z135["g_cutwA"]), 6),', 1))
V.append(('           g_cutk5=float(z133["g_cutk5"]),',
          '           g_cutk5=float(z135["g_cutk5"]),', 1))

# B-cert: B24-cert (vs l131) -> B25-cert (vs l133)
V.append((
    '# ---- Part 4: B24-cert FIRST, then XOR reads + S/S + pooled ----\n'
    '# B24-cert BEFORE any B25 read: machinery recomputed on raw_l131 B24 ==\n'
    '# results_l131.json Ti table (ALL 12 l131 table arms).\n'
    'b24_cert_fail = []\n'
    'for a in r131["table"]["Ti"]:\n'
    '    want = r131["table"]["Ti"][a]\n'
    '    got = side_k(z131, a, B24, "Ti")\n'
    '    for kk in ("kL", "kR", "meanL", "meanR"):\n'
    '        if got[kk] != want[kk]:\n'
    '            b24_cert_fail.append((a, kk, got[kk], want[kk]))\n'
    'assert not b24_cert_fail, ("B24-cert FAIL (no B25 read)",\n'
    '                           b24_cert_fail[:5])\n'
    'print(f"B24-cert vs results_l131.json Ti table: PASS "\n'
    '      f"(all {len(r131[\'table\'][\'Ti\'])} arms)")',
    '# ---- Part 4: B25-cert FIRST, then rebase reads + S/S + pooled ----\n'
    '# B25-cert BEFORE any B26 read: machinery recomputed on raw_l133 B25 ==\n'
    '# results_l133.json Ti table (ALL 13 l133 table arms).\n'
    'b25_cert_fail = []\n'
    'for a in r133["table"]["Ti"]:\n'
    '    want = r133["table"]["Ti"][a]\n'
    '    got = side_k(z133, a, B25, "Ti")\n'
    '    for kk in ("kL", "kR", "meanL", "meanR"):\n'
    '        if got[kk] != want[kk]:\n'
    '            b25_cert_fail.append((a, kk, got[kk], want[kk]))\n'
    'assert not b25_cert_fail, ("B25-cert FAIL (no B26 read)",\n'
    '                           b25_cert_fail[:5])\n'
    'print(f"B25-cert vs results_l133.json Ti table: PASS "\n'
    '      f"(all {len(r133[\'table\'][\'Ti\'])} arms)")', 1))

# W branches -> R branches (computed AFTER pooled_t; placeholder here)
V.append((
    '# registered XOR branches (PREREG W1/W2/W3; report WHICH carries)\n'
    't25p = interp_read["25p"]\n'
    'w1 = bool(t25p["partial"])\n'
    'w2 = bool(t25p["super"] or t25p["restore"])\n'
    'w3 = bool(t25p["kill"] or not (w1 or w2))\n'
    'xor = dict(\n'
    '    W1_identity_xor=w1, W2_position_thin=w2,\n'
    '    W3_neither=w3,\n',
    '# L135: the R-branches (R1/R2/R3, PREREG) are computed AFTER the\n'
    '# pooled_t block — R1 reads the pooled 25p Wilson interval.\n'
    'xor = dict(\n', 1))
V.append((
    '    cls=("W1: cutng25p PARTIALs — clean IDENTITY XOR at mass-match: "\n'
    '          "1110 completes the flip, 319 does NOT (L120 cell-204 "\n'
    '          "claim upgrades to mass-matched)"\n'
    '          if w1 else\n'
    '          "W2: cutng25p SUPERs/RESTORES — the flip is POSITION-THIN: "\n'
    '          "BOTH transition cells complete individually (window claim "\n'
    '          "revised to either-cell; reported honestly)"\n'
    '          if w2 else\n'
    '          "W3 (registered degenerate): 25p kills or lands outside "\n'
    '          "every band — neither branch; report which band it landed "\n'
    '          "in (L55 rule)"))\n',
    '    R_branches="computed after pooled_t (needs lb25p/ub25p)")\n', 1))

# S batch-count strings
V.append((
    '    "cutk5 KILLS on B25 — 13th consecutive batch "\n'
    '    "(B12..B25)"\n'
    '    if killmap["k5"] else\n'
    '    "cutk5 does NOT kill on B25 — DISCLOSED (L118 lottery class)"))',
    '    "cutk5 KILLS on B26 — 14th consecutive batch "\n'
    '    "(B12..B26)"\n'
    '    if killmap["k5"] else\n'
    '    "cutk5 does NOT kill on B26 — DISCLOSED (L118 lottery class)"))', 1))
V.append((
    '    "cutng29 SUPER-RAISES in-batch (10th)"',
    '    "cutng29 SUPER-RAISES in-batch (11th)"', 1))
V.append((
    '    "cutwA lands in the PARTIAL band [.35,.50] & kR 3-8 — 5th batch "\n'
    '    "(B18 .413/5, B19 .376/4, B21 .365/3, B24 .436/6, B25)"',
    '    "cutwA lands in the PARTIAL band [.35,.50] & kR 3-8 — 6th batch "\n'
    '    "(B18 .413/5, B19 .376/4, B21 .365/3, B24 .436/6, B25 .466/6, "\n'
    '    "B26)"', 1))
V.append((
    '    "cutng25 SUPER/RESTORE replicates on B25 — L131 X1 2nd batch"',
    '    "cutng25 SUPER/RESTORE replicates on B26 — L131 X1 3rd batch"', 1))
V.append((
    '    "cutng25 misses SUPER/RESTORE on B25 — DISCLOSED (X1 single-batch)"))',
    '    "cutng25 misses SUPER/RESTORE on B26 — DISCLOSED (X1 two-batch "\n'
    '    "only; would end the X1 frame)"))', 1))

# R4 pooled: n=160 -> n=176
V.append((
    '# R4: pooled batch-union B16..B24 n=144, FULL-PRECISION Wilson',
    '# R4: pooled batch-union B16..B26 n=176, FULL-PRECISION Wilson', 1))
V.append((
    '    _, Rb25 = duty_seeds(z133, a, B25, "Ti")\n'
    '    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21,\n'
    '                           Rb22, Rb23, Rb24, Rb25])\n'
    '    k = int((allb >= .5).sum())\n'
    '    lb, ub = wilson(k, 160)\n'
    '    pooled[a] = dict(k160=k, p_hat=k / 160, lb=lb, ub=ub,\n'
    '                     k_b21=int((Rb21 >= .5).sum()),\n'
    '                     k_b24=int((Rb24 >= .5).sum()),\n'
    '                     k_b25=int((Rb25 >= .5).sum()))\n'
    '    print(f"POOLED Ti_R {a:7s} k {k}/160 p_hat {k/160:.3f} "\n'
    '          f"Wilson [{lb:.4f}, {ub:.4f}] (B21 {pooled[a][\'k_b21\']}/16, "\n'
    '          f"B24 {pooled[a][\'k_b24\']}/16, B25 {pooled[a][\'k_b25\']}/16)")',
    '    _, Rb25 = duty_seeds(z133, a, B25, "Ti")\n'
    '    _, Rb26 = duty_seeds(z135, a, B26, "Ti")\n'
    '    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21,\n'
    '                           Rb22, Rb23, Rb24, Rb25, Rb26])\n'
    '    k = int((allb >= .5).sum())\n'
    '    lb, ub = wilson(k, 176)\n'
    '    pooled[a] = dict(k176=k, p_hat=k / 176, lb=lb, ub=ub,\n'
    '                     k_b21=int((Rb21 >= .5).sum()),\n'
    '                     k_b24=int((Rb24 >= .5).sum()),\n'
    '                     k_b25=int((Rb25 >= .5).sum()),\n'
    '                     k_b26=int((Rb26 >= .5).sum()))\n'
    '    print(f"POOLED Ti_R {a:7s} k {k}/176 p_hat {k/176:.3f} "\n'
    '          f"Wilson [{lb:.4f}, {ub:.4f}] (B21 {pooled[a][\'k_b21\']}/16, "\n'
    '          f"B24 {pooled[a][\'k_b24\']}/16, B25 {pooled[a][\'k_b25\']}/16, "\n'
    '          f"B26 {pooled[a][\'k_b26\']}/16)")', 1))

# P3 transition pooled: n=48 -> n=64
V.append((
    '# P3: transition arms pooled B21+B24+B25 n=48; ng25/ng25p separate\n'
    'pooled_t = {}\n'
    'for a in ("cutng23", "cutwA", "cutng26", "cutng29"):\n'
    '    _, Rb21 = duty_seeds(z126, a, B21, "Ti")\n'
    '    _, Rb24 = duty_seeds(z131, a, B24, "Ti")\n'
    '    _, Rb25 = duty_seeds(z133, a, B25, "Ti")\n'
    '    allb = np.concatenate([Rb21, Rb24, Rb25])\n'
    '    k = int((allb >= .5).sum())\n'
    '    lb, ub = wilson(k, 48)\n'
    '    pooled_t[a] = dict(k48=k, p_hat=k / 48, lb=lb, ub=ub,\n'
    '                       k_b21=int((Rb21 >= .5).sum()),\n'
    '                       k_b24=int((Rb24 >= .5).sum()),\n'
    '                       k_b25=int((Rb25 >= .5).sum()))\n'
    '    print(f"P3 POOLED transition {a:8s} k {k}/48 "\n'
    '          f"(B21 {pooled_t[a][\'k_b21\']}/16 + B24 "\n'
    '          f"{pooled_t[a][\'k_b24\']}/16 + B25 "\n'
    '          f"{pooled_t[a][\'k_b25\']}/16) p_hat {k/48:.3f} "\n'
    '          f"Wilson [{lb:.4f}, {ub:.4f}]")\n'
    '# ng25 2nd batch (L131 X1 replication); ng25p single-batch (disclosed)\n'
    '_, R25a = duty_seeds(z131, "cutng25", B24, "Ti")\n'
    '_, R25b = duty_seeds(z133, "cutng25", B25, "Ti")\n'
    'k25 = int((np.concatenate([R25a, R25b]) >= .5).sum())\n'
    'lb25, ub25 = wilson(k25, 32)\n'
    'pooled_t["cutng25"] = dict(k32=k25, p_hat=k25 / 32, lb=lb25, ub=ub25,\n'
    '                           k_b24=int((R25a >= .5).sum()),\n'
    '                           k_b25=int((R25b >= .5).sum()))\n'
    '_, R25p = duty_seeds(z133, "cutng25p", B25, "Ti")\n'
    'k25p = int((R25p >= .5).sum())\n'
    'lb25p, ub25p = wilson(k25p, 16)\n'
    'pooled_t["cutng25p"] = dict(k16=k25p, p_hat=k25p / 16, lb=lb25p,\n'
    '                            ub=ub25p, single_batch=True)\n'
    'print(f"P3 ng25 2nd batch k {k25}/32 Wilson [{lb25:.4f}, {ub25:.4f}] "\n'
    '      f"| ng25p single-batch k {k25p}/16 [{lb25p:.4f}, {ub25p:.4f}]")\n',
    '# P3: transition arms pooled B21+B24+B25+B26 n=64; ng25/ng25p below\n'
    'pooled_t = {}\n'
    'for a in ("cutng23", "cutwA", "cutng26", "cutng29"):\n'
    '    _, Rb21 = duty_seeds(z126, a, B21, "Ti")\n'
    '    _, Rb24 = duty_seeds(z131, a, B24, "Ti")\n'
    '    _, Rb25 = duty_seeds(z133, a, B25, "Ti")\n'
    '    _, Rb26 = duty_seeds(z135, a, B26, "Ti")\n'
    '    allb = np.concatenate([Rb21, Rb24, Rb25, Rb26])\n'
    '    k = int((allb >= .5).sum())\n'
    '    lb, ub = wilson(k, 64)\n'
    '    pooled_t[a] = dict(k64=k, p_hat=k / 64, lb=lb, ub=ub,\n'
    '                       k_b21=int((Rb21 >= .5).sum()),\n'
    '                       k_b24=int((Rb24 >= .5).sum()),\n'
    '                       k_b25=int((Rb25 >= .5).sum()),\n'
    '                       k_b26=int((Rb26 >= .5).sum()))\n'
    '    print(f"P3 POOLED transition {a:8s} k {k}/64 "\n'
    '          f"(B21 {pooled_t[a][\'k_b21\']}/16 + B24 "\n'
    '          f"{pooled_t[a][\'k_b24\']}/16 + B25 "\n'
    '          f"{pooled_t[a][\'k_b25\']}/16 + B26 "\n'
    '          f"{pooled_t[a][\'k_b26\']}/16) p_hat {k/64:.3f} "\n'
    '          f"Wilson [{lb:.4f}, {ub:.4f}]")\n'
    '# ng25 3rd batch (L131 X1); ng25p POOLED B25+B26 n=32 (the card read)\n'
    '_, R25a = duty_seeds(z131, "cutng25", B24, "Ti")\n'
    '_, R25b = duty_seeds(z133, "cutng25", B25, "Ti")\n'
    '_, R25c = duty_seeds(z135, "cutng25", B26, "Ti")\n'
    'k25 = int((np.concatenate([R25a, R25b, R25c]) >= .5).sum())\n'
    'lb25, ub25 = wilson(k25, 48)\n'
    'pooled_t["cutng25"] = dict(k48=k25, p_hat=k25 / 48, lb=lb25, ub=ub25,\n'
    '                           k_b24=int((R25a >= .5).sum()),\n'
    '                           k_b25=int((R25b >= .5).sum()),\n'
    '                           k_b26=int((R25c >= .5).sum()))\n'
    '_, R25p = duty_seeds(z133, "cutng25p", B25, "Ti")\n'
    '_, R25p2 = duty_seeds(z135, "cutng25p", B26, "Ti")\n'
    'k25p = int((np.concatenate([R25p, R25p2]) >= .5).sum())\n'
    'lb25p, ub25p = wilson(k25p, 32)\n'
    'pooled_t["cutng25p"] = dict(k32=k25p, p_hat=k25p / 32, lb=lb25p,\n'
    '                            ub=ub25p, k_b25=int((R25p >= .5).sum()),\n'
    '                            k_b26=int((R25p2 >= .5).sum()))\n'
    'print(f"P3 ng25 3rd batch k {k25}/48 Wilson [{lb25:.4f}, {ub25:.4f}] "\n'
    '      f"| ng25p POOLED B25+B26 k {k25p}/32 [{lb25p:.4f}, {ub25p:.4f}]")\n'
    '# ---- L135 registered R-branches (PREREG R1/R2/R3; AFTER pooled_t) ----\n'
    't26p = interp_read["25p"]\n'
    'r2 = bool(t26p["kill"])\n'
    'r3 = bool(t26p["super"] or t26p["restore"])\n'
    'r1 = bool(not r2 and not r3 and 0.45 < t26p["meanR"] < 0.60\n'
    '          and 4 <= t26p["kR"] <= 10 and lb25p < 0.5 < ub25p)\n'
    'rnone = not (r1 or r2 or r3)\n'
    'xor = dict(\n'
    '    R1_intermediate_stable=r1, R2_kill_draw=r2, R3_raise_draw=r3,\n'
    '    NEITHER=rnone,\n'
    '    cls=("R1: 25p intermediate-STABLE on B26 — window (.45,.60) & "\n'
    '         "kR 4-10 AND pooled n=32 Wilson CONTAINS .5 — the "\n'
    '         "319-neutral decomposition is CITABLE pooled (1110 carries "\n'
    '         "the flip, 319 ~neutral)"\n'
    '         if r1 else\n'
    '         "R2: 25p KILLs on B26 — the B25 .508 was a draw; the "\n'
    '         "intermediate reading downgrades to single-batch (report "\n'
    '         "which leg moved)"\n'
    '         if r2 else\n'
    '         "R3: 25p SUPERs/RESTORES on B26 — position-thin (W2) "\n'
    '         "revives one batch late; report honestly"\n'
    '         if r3 else\n'
    '         "NEITHER (registered degenerate): outside every branch — "\n'
    '         "report where it landed (L55 rule)"))\n'
    'print(f"R: {xor[\'cls\']}")\n', 1))

# p0 + conjunction
V.append((
    'print(f"XOR: {xor[\'cls\']} | steps {steps_x}")',
    'print(f"R-branches computed after pooled_t (below) | steps {steps_x}")',
    1))
V.append((
    '          c0a131_pass=ar["c0a131_pass"], c0a131_max=ar["c0a131_max"],\n'
    '          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"],',
    '          c0a131_pass=ar["c0a131_pass"], c0a131_max=ar["c0a131_max"],\n'
    '          c0a133_pass=ar["c0a133_pass"], c0a133_max=ar["c0a133_max"],\n'
    '          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"],\n'
    '          g_cutng25p_stored_exact=ar["g_cutng25p_stored_exact"],', 1))
V.append((
    '                  and p0["c0a128_pass"] and p0["c0a131_pass"]\n'
    '                  and p0["g_cut58_stored_exact"]',
    '                  and p0["c0a128_pass"] and p0["c0a131_pass"]\n'
    '                  and p0["c0a133_pass"]\n'
    '                  and p0["g_cut58_stored_exact"]', 1))
V.append((
    '                  and p0["g_cutng23_stored_exact"] and p0["g_cutng26_stored_exact"]\n'
    '                  and p0["g_cutng25_stored_exact"]\n'
    '                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])',
    '                  and p0["g_cutng23_stored_exact"] and p0["g_cutng26_stored_exact"]\n'
    '                  and p0["g_cutng25_stored_exact"]\n'
    '                  and p0["g_cutng25p_stored_exact"]\n'
    '                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])',
    1))
V.append((
    'print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..128 "\n'
    '      "retained + C0A-131 (10 arms NEW) + 10 stored gains:",',
    'print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..131 "\n'
    '      "retained + C0A-133 (13 arms NEW) + 11 stored gains:",', 1))
V.append(('           b24_cert_pass=True,', '           b25_cert_pass=True,', 1))
V.append(('json.dump(out, open("l133/results_l133.json", "w"), indent=1)',
          'json.dump(out, open("l135/results_l135.json", "w"), indent=1)', 1))
V.append(('print("results_l133.json written")',
          'print("results_l135.json written")', 1))

v = apply(v, V, "verdict")

# verdict residual scan
for bad in ("B24-cert", "b24_cert", "l133/anchors_run",
            "results_l133.json\", \"w", "W1_identity_xor", "W2_position_thin",
            "W3_neither", "single_batch=True", "2nd batch (L131 X1 replication)"):
    assert bad not in v, ("verdict stale token", bad)
# every B25 use must be context-only (z133/r133/cert/pooled context)
for i, line in enumerate(v.splitlines()):
    if "B25" in line:
        assert ("z133" in line or "r133" in line or "context batch" in line
                or "B25-cert" in line or "k_b25" in line or "B25 " in line
                or "B25+" in line or "B25 " in line
                or line.lstrip().startswith("#") or i < 16), \
            ("unwhitelisted B25", i, line)
for probe in ("z135", "R1_intermediate_stable", "k176", "k64", "k48=k25",
              "B26", "b25_cert", "r133"):
    assert v.count(probe) >= 1, ("missing verdict plumbing", probe)

open("l135_verdict.py", "w").write(v)
py_compile.compile("l135_verdict.py", doraise=True)
print(f"l135_verdict.py written ({len(v.splitlines())} lines) + py_compile OK")
