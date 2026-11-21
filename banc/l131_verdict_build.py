"""l131_verdict_build.py — asserted exact-string transform
l126_verdict.py -> l131_verdict.py.

L131 verdict: C0B on raw_l113 + B23-cert on raw_l128 vs results_l128.json
(ALL its table arms) BEFORE any B24 read; the registered XOR reads on
FRESH B24 (criteria VERBATIM): X1/X2/X3 branches for cutng25 + P2
mass-twin disclosure + P3 pooled transition arms B21+B24 n=32 (L132
prebase); S1 cutk5 12th batch pooled n=144 (B16..B24); S2 endpoints 9th
batch (dR-leg note); S3 wA partial 4th batch; watch; sanity. Long blocks
spliced on unique openers with count==1 guards (l122 form).
"""
import py_compile

SRC = open("l126_verdict.py").read()
n_reps = 0


def rep(old, new, count=1):
    global SRC, n_reps
    c = SRC.count(old)
    assert c == count, f"rep count {c} != {count}: {old[:70]!r}"
    SRC = SRC.replace(old, new)
    n_reps += 1


def span(open_line, close_line, new_block):
    global SRC, n_reps
    i = SRC.index(open_line)
    j = SRC.index(close_line, i) + len(close_line)
    assert SRC.count(open_line) == 1, open_line[:60]
    assert SRC.count(close_line) == 1, close_line[:60]
    SRC = SRC[:i] + new_block + SRC[j:]
    n_reps += 1


# V1: docstring
i0 = SRC.index('"""')
i1 = SRC.index('"""', i0 + 3) + 3
NEW_DOC = '''"""L131 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B23-cert of this machinery on raw_l128 vs results_l128.json (ALL its
table arms) BEFORE any B24 read, then the registered XOR reads on FRESH
B24 (criteria VERBATIM): X1 cutng25 SUPER/RESTORE -> rank 25 (id 1110)
completes; X2 cutng25 PARTIAL -> rank 26 (id 319) completes; X3
registered degenerate branch (kill/out-of-band -> NEITHER single cell;
the {1110,319} pair stays the unit). P2 mass-twin disclosure (static
pins). P3 pooled transition arms {ng23, wA, ng26, ng29} B21+B24 n=32
full-precision Wilson (L132 prebase). S1 cutk5 12th batch pooled R4
B16..B24 n=144; S2 endpoints 9th batch (dR-leg disclosure); S3 wA
partial 4th batch; per-side duty table 5 pairs x 12 arms; Ti_L/Tr_R/Sr_R
watch; sanity cells. PREREG l131/PREREG.md."""
'''
SRC = NEW_DOC + SRC[i1:]
n_reps += 1

# V2: batches — B24 fresh, B23 (l128) cert context, B22 (l127) R4 pool,
# B21 (l126) P3 pool
rep("B21 = list(range(2501, 2517))       # FRESH (l126)",
    "B24 = list(range(2801, 2817))       # FRESH (l131)\n"
    "B23 = list(range(2701, 2717))  # context batch (l128, cert)\n"
    "B22 = list(range(2601, 2617))  # context batch (l127, R4 pool)\n"
    "B21 = list(range(2501, 2517))  # context batch (l126, P3 pool)")
# V3: NEW_ARMS / ARMS
rep('NEW_ARMS = ["cutk5", "cutng19", "cutng21", "cutng23", "cutwA", "cutng26",\n'
    '            "cutng28", "cutng29"]',
    'NEW_ARMS = ["cutk5", "cutng19", "cutng23", "cutwA", "cutng25", "cutng26",\n'
    '            "cutng29"]')
# V4: LADDER / CURVE
rep('LADDER = [("0", "full"), ("19", "cutng19"), ("21", "cutng21"),\n'
    '          ("23", "cutng23"), ("24", "cutwA"), ("26", "cutng26"),\n'
    '          ("28", "cutng28"), ("29", "cutng29"), ("58", "cut58"),\n'
    '          ("k5", "cutk5")]',
    'LADDER = [("0", "full"), ("19", "cutng19"), ("23", "cutng23"),\n'
    '          ("24", "cutwA"), ("25", "cutng25"), ("26", "cutng26"),\n'
    '          ("29", "cutng29"), ("58", "cut58"),\n'
    '          ("k5", "cutk5")]')
rep('CURVE = ["19", "21", "23", "24", "26", "28", "29"]   # registered curve',
    'CURVE = ["19", "23", "24", "25", "26", "29"]   # registered curve')
# V5: npz/json loads
rep('z126 = np.load("l126/raw_l126.npz")',
    'z126 = np.load("l126/raw_l126.npz")\n'
    'z127 = np.load("l127/raw_l127.npz")\n'
    'z128 = np.load("l128/raw_l128.npz")\n'
    'z131 = np.load("l131/raw_l131.npz")')
rep('ar = json.load(open("l126/anchors_run.json"))',
    'ar = json.load(open("l131/anchors_run.json"))\n'
    'r128 = json.load(open("l128/results_l128.json"))')
rep('S126 = json.load(open("l126/static.json"))',
    'S126 = json.load(open("l126/static.json"))\n'
    'S131 = json.load(open("l131/static.json"))')
# V6: z126 -> z131 for the B24 reads (table + dose + pooled-R4 latest)
rep('        t = side_k(z126, a, B21, pk)', '        t = side_k(z131, a, B24, pk)')
rep('_, Rfull = duty_seeds(z126, "full", B21, "Ti")',
    '_, Rfull = duty_seeds(z131, "full", B24, "Ti")')
rep('    _, Rd = duty_seeds(z126, a, B21, "Ti")',
    '    _, Rd = duty_seeds(z131, a, B24, "Ti")')
# V7: P0 anchors dict — new classes + stored-exact keys
rep('          c0a125_pass=ar["c0a125_pass"], c0a125_max=ar["c0a125_max"],\n'
    '          g_cutng19_stored_exact=ar["g_cutng19_stored_exact"],',
    '          c0a125_pass=ar["c0a125_pass"], c0a125_max=ar["c0a125_max"],\n'
    '          c0a126_pass=ar["c0a126_pass"], c0a126_max=ar["c0a126_max"],\n'
    '          c0a127_pass=ar["c0a127_pass"], c0a127_max=ar["c0a127_max"],\n'
    '          c0a128_pass=ar["c0a128_pass"], c0a128_max=ar["c0a128_max"],\n'
    '          g_cutng23_stored_exact=ar["g_cutng23_stored_exact"],\n'
    '          g_cutng26_stored_exact=ar["g_cutng26_stored_exact"],\n'
    '          g_cutng19_stored_exact=ar["g_cutng19_stored_exact"],')
rep('p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]\n'
    '                  and p0["c0a122_pass"] and p0["c0a123_pass"]\n'
    '                  and p0["c0a124_pass"] and p0["c0a125_pass"]\n'
    '                  and p0["g_cut58_stored_exact"]\n'
    '                  and p0["g_cutk5_stored_exact"]\n'
    '                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]\n'
    '                  and p0["g_cutwA_stored_exact"]\n'
    '                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])',
    'p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]\n'
    '                  and p0["c0a122_pass"] and p0["c0a123_pass"]\n'
    '                  and p0["c0a124_pass"] and p0["c0a125_pass"]\n'
    '                  and p0["c0a126_pass"] and p0["c0a127_pass"]\n'
    '                  and p0["c0a128_pass"]\n'
    '                  and p0["g_cut58_stored_exact"]\n'
    '                  and p0["g_cutk5_stored_exact"]\n'
    '                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]\n'
    '                  and p0["g_cutwA_stored_exact"]\n'
    '                  and p0["g_cutng23_stored_exact"] and p0["g_cutng26_stored_exact"]\n'
    '                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])')
rep('print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "\n'
    '      "(cutk5 vs raw_l120) + C0A-121 (3 arms vs raw_l121) + C0A-122 "\n'
    '      "(3 arms vs raw_l122) + C0A-123 (4 shared arms vs raw_l123) + "\n'
    '      "C0A-124 (4 arms vs raw_l124) + C0A-125 (3 arms vs raw_l125) + "\n'
    '      "7 stored gains:",',
    'print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..125 "\n'
    '      "retained + C0A-126 EXT (9 arms) + C0A-127 (6) + C0A-128 (6) + "\n'
    '      "9 stored gains:",')
# V8: P4 af reads z126->z131, B21->B24
rep('af_mean = {a: round(float(np.mean([float(z126[f"af_{a}_{s}"]) for s in B21])), 6)\n'
    '           for a in ARMS}',
    'af_mean = {a: round(float(np.mean([float(z131[f"af_{a}_{s}"]) for s in B24])), 6)\n'
    '           for a in ARMS}')
rep('af_range_ok = all(0.01 < float(z126[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B21)',
    'af_range_ok = all(0.01 < float(z131[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B24)')
# V9: table print header
rep('print("---- B21 per-side duty table ----")',
    'print("---- B24 per-side duty table ----")')
# V10: band block B21->B24 label
rep('print("full-arm B21 band check (disclosure only):", band_ok)',
    'print("full-arm B24 band check (disclosure only):", band_ok)')
# V11: B-cert block -> B23-cert on raw_l128 vs results_l128 (BEFORE B24 reads)
rep('# ---- Part 4: B20-cert FIRST, then curve labels + D1/D2/D3 + S/S + pooled ----\n'
    '# B20-cert BEFORE any B21 read: machinery recomputed on raw_l125 B20 ==\n'
    '# results_l125.json Ti table (ALL 12 l125 arms).\n'
    'b20_cert_fail = []\n'
    'for a in r125["table"]["Ti"]:\n'
    '    want = r125["table"]["Ti"][a]\n'
    '    got = side_k(z125, a, B20, "Ti")\n'
    '    for kk in ("kL", "kR", "meanL", "meanR"):\n'
    '        if got[kk] != want[kk]:\n'
    '            b20_cert_fail.append((a, kk, got[kk], want[kk]))\n'
    'assert not b20_cert_fail, ("B20-cert FAIL (no B21 read)",\n'
    '                           b20_cert_fail[:5])\n'
    'print(f"B20-cert vs results_l125.json Ti table: PASS "\n'
    '      f"(all {len(r125[\'table\'][\'Ti\'])} arms)")',
    '# ---- Part 4: B23-cert FIRST, then XOR reads + S/S + pooled ----\n'
    '# B23-cert BEFORE any B24 read: machinery recomputed on raw_l128 B23 ==\n'
    '# results_l128.json Ti table (ALL 12 l128 table arms).\n'
    'b23_cert_fail = []\n'
    'for a in r128["table"]["Ti"]:\n'
    '    want = r128["table"]["Ti"][a]\n'
    '    got = side_k(z128, a, B23, "Ti")\n'
    '    for kk in ("kL", "kR", "meanL", "meanR"):\n'
    '        if got[kk] != want[kk]:\n'
    '            b23_cert_fail.append((a, kk, got[kk], want[kk]))\n'
    'assert not b23_cert_fail, ("B23-cert FAIL (no B24 read)",\n'
    '                           b23_cert_fail[:5])\n'
    'print(f"B23-cert vs results_l128.json Ti table: PASS "\n'
    '      f"(all {len(r128[\'table\'][\'Ti\'])} arms)")')
# V12: interp block -> XOR block (span the shape-cells section)
span('# registered shape cells (can overlap; report WHICH carries)',
     'print(f"CURVE steps: {steps}")\n'
     'print(f"SHAPE CELLS: D1 SMOOTH {d1} | D2 SECOND STEP {d2} "\n'
     '      f"(jumps {inner_pairs}) | D3 CLIFF AT 29 {d3} (k28 not-super "\n'
     '      f"{k28_ns}, k29 super {interp_read[\'29\'][\'super\']}) | "\n'
     '      f"LOTTERY {lottery} (dips {dips})")',
     '# registered XOR branches (PREREG X1/X2/X3; report WHICH carries)\n'
     't25 = interp_read["25"]\n'
     'x1 = bool(t25["super"] or t25["restore"])\n'
     'x2 = bool(t25["partial"])\n'
     'x3 = bool(t25["kill"] or not (x1 or x2))\n'
     'xor = dict(\n'
     '    X1_rank25_completes=x1, X2_rank26_completes=x2,\n'
     '    X3_neither=x3,\n'
     '    cls=("X1: rank 25 (id 1110) COMPLETES the kill->super flip — k25 "\n'
     '          "supers/restores alone, k26 adds nothing material"\n'
     '          if x1 else\n'
     '          "X2: rank 26 (id 319) is the completing cell — k25 stays "\n'
     '          "PARTIAL, k26 supers same-batch"\n'
     '          if x2 else\n'
     '          "X3 (registered degenerate): NO single named cell carries "\n'
     '          "the flip — k25 kills or lands outside every band; the "\n'
     '          "{1110, 319} PAIR stays the unit (L55 rule)"))\n'
     'steps_x = {"24->25": round(interp_read["25"]["meanR"]\n'
     '                           - interp_read["24"]["meanR"], 3),\n'
     '           "25->26": round(interp_read["26"]["meanR"]\n'
     '                           - interp_read["25"]["meanR"], 3)}\n'
     'p2 = dict(rank25_id=S131["rank_ids"]["rank25"],\n'
     '          rank26_id=S131["rank_ids"]["rank26"],\n'
     '          m25=S131["rank_mass"]["rank25"], m26=S131["rank_mass"]["rank26"],\n'
     '          pair_delta=S131["rank_mass"]["pair_delta"],\n'
     '          note="arms differ by one full cell mass each way; the "\n'
     '               "alternative reading is any ~.006 mass beyond .2350")\n'
     'print(f"XOR: {xor[\'cls\']} | steps {steps_x}")\n'
     'print(f"P2 mass-twins: id {p2[\'rank25_id\']} m {p2[\'m25\']:.6f} vs "\n'
     '      f"id {p2[\'rank26_id\']} m {p2[\'m26\']:.6f} (delta "\n'
     '      f"{p2[\'pair_delta\']:.2e})")')
# V13: S1/S2/S3 cls strings
span('# S1: cutk5 9th batch; S2: endpoints 6th batch; S3: wA partial 3rd batch',
     'print(f"S1: {s1[\'cls\']}")\n'
     'print(f"S2: {s2[\'cls\']}")\n'
     'print(f"S3: {s3[\'cls\']}")',
     '# S1: cutk5 12th batch; S2: endpoints 9th batch (dR-leg note);\n'
     '# S3: wA partial 4th batch\n'
     's1 = dict(k5_kill=bool(killmap["k5"]), cls=(\n'
     '    "cutk5 KILLS on B24 — 12th consecutive batch "\n'
     '    "(B12/B14/B15/B16/B17/B18/B19/B20/B21/B22/B23/B24)"\n'
     '    if killmap["k5"] else\n'
     '    "cutk5 does NOT kill on B24 — DISCLOSED (L118 lottery class)"))\n'
     's2 = dict(ng19_kill=bool(killmap["19"]),\n'
     '          ng19_dR_leg=dose["Ti"]["legs"]["19"]["mean_paired_dR"],\n'
     '          ng29_super=bool(_super(table["Ti"]["cutng29"])),\n'
     '          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(\n'
     '    "cutng19 KILLs (kR+meanR legs; dR leg reported separately, "\n'
     '    "3-batch miss pattern) + cutng29 SUPER-RAISES in-batch (9th)"\n'
     '    if killmap["19"] and _super(table["Ti"]["cutng29"]) else\n'
     '    "endpoint miss DISCLOSED (registered S2, never silent)"))\n'
     's3 = dict(wA_partial=bool(_partial(table["Ti"]["cutwA"])),\n'
     '          wA_meanR=table["Ti"]["cutwA"]["meanR"],\n'
     '          wA_kR=table["Ti"]["cutwA"]["kR"], cls=(\n'
     '    "cutwA lands in the PARTIAL band [.35,.50] & kR 3-8 — 4th batch "\n'
     '    "(B18 .413/5, B19 .376/4, B21 .365/3, B24)"\n'
     '    if _partial(table["Ti"]["cutwA"]) else\n'
     '    "cutwA MISSES the partial band — DISCLOSED (would revise L124\'s "\n'
     '    "stable-intermediate reading)"))\n'
     'print(f"S1: {s1[\'cls\']}")\n'
     'print(f"S2: {s2[\'cls\']} | ng19 dR leg {s2[\'ng19_dR_leg\']:+.3f}")\n'
     'print(f"S3: {s3[\'cls\']}")')
# V14: pooled R4 -> n=144 over B16..B24 + NEW P3 transition pool n=32
span('# R4: pooled batch-union B16..B21 n=96, FULL-PRECISION Wilson',
     'pooled_scr = {"note": "not run in L126 — l125 single-batch stands (L128 owes "\n'
     '                      "the rebase)"}',
     '# R4: pooled batch-union B16..B24 n=144, FULL-PRECISION Wilson\n'
     'pooled = {}\n'
     'for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):\n'
     '    _, Rb16 = duty_seeds(z121, a, B16, "Ti")\n'
     '    _, Rb17 = duty_seeds(z122, a, B17, "Ti")\n'
     '    _, Rb18 = duty_seeds(z123, a, B18, "Ti")\n'
     '    _, Rb19 = duty_seeds(z124, a, B19, "Ti")\n'
     '    _, Rb20 = duty_seeds(z125, a, B20, "Ti")\n'
     '    _, Rb21 = duty_seeds(z126, a, B21, "Ti")\n'
     '    _, Rb22 = duty_seeds(z127, a, B22, "Ti")\n'
     '    _, Rb23 = duty_seeds(z128, a, B23, "Ti")\n'
     '    _, Rb24 = duty_seeds(z131, a, B24, "Ti")\n'
     '    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21,\n'
     '                           Rb22, Rb23, Rb24])\n'
     '    k = int((allb >= .5).sum())\n'
     '    lb, ub = wilson(k, 144)\n'
     '    pooled[a] = dict(k144=k, p_hat=k / 144, lb=lb, ub=ub,\n'
     '                     k_b21=int((Rb21 >= .5).sum()),\n'
     '                     k_b24=int((Rb24 >= .5).sum()))\n'
     '    print(f"POOLED Ti_R {a:7s} k {k}/144 p_hat {k/144:.3f} "\n'
     '          f"Wilson [{lb:.4f}, {ub:.4f}] (B21 {pooled[a][\'k_b21\']}/16, "\n'
     '          f"B24 {pooled[a][\'k_b24\']}/16)")\n'
     '# P3 (L132 prebase): transition arms pooled B21+B24 n=32\n'
     'pooled_t = {}\n'
     'for a in ("cutng23", "cutwA", "cutng26", "cutng29"):\n'
     '    _, Rb21 = duty_seeds(z126, a, B21, "Ti")\n'
     '    _, Rb24 = duty_seeds(z131, a, B24, "Ti")\n'
     '    allb = np.concatenate([Rb21, Rb24])\n'
     '    k = int((allb >= .5).sum())\n'
     '    lb, ub = wilson(k, 32)\n'
     '    pooled_t[a] = dict(k32=k, p_hat=k / 32, lb=lb, ub=ub,\n'
     '                       k_b21=int((Rb21 >= .5).sum()),\n'
     '                       k_b24=int((Rb24 >= .5).sum()))\n'
     '    print(f"P3 POOLED transition {a:8s} k {k}/32 "\n'
     '          f"(B21 {pooled_t[a][\'k_b21\']}/16 + B24 "\n'
     '          f"{pooled_t[a][\'k_b24\']}/16) p_hat {k/32:.3f} "\n'
     '          f"Wilson [{lb:.4f}, {ub:.4f}]")\n'
     'pooled_scr = {"note": "not run in L131 — l128 rebase stands"}')
# V15: out json keys
rep('           interp=dict(curve=interp_read, cells=cells,\n'
    '                       s1=s1, s2=s2, s3=s3),\n'
    '           pooled=pooled, pooled_scr=pooled_scr,\n'
    '           b20_cert_pass=True,',
    '           interp=dict(curve=interp_read, steps=steps_x, s1=s1, s2=s2,\n'
    '                       s3=s3),\n'
    '           xor=dict(**xor, steps=steps_x, p2=p2),\n'
    '           pooled=pooled, pooled_transition=pooled_t,\n'
    '           pooled_scr=pooled_scr,\n'
    '           b23_cert_pass=True,')
# V15b: interp_read mass source S126 -> S131 (cutng25 pin lives there)
rep('        mass=S126["prefix"][a]["mass_removed"] if a in S126["prefix"]',
    '        mass=S131["prefix"][a]["mass_removed"] if a in S131["prefix"]')
# V15c: remaining z126 value reads -> z131 (this run's gains)
rep('      "cutwA", round(float(z126["g_cutwA"]), 6),',
    '      "cutwA", round(float(z131["g_cutwA"]), 6),')
rep('           g_cutk5=float(z126["g_cutk5"]),',
    '           g_cutk5=float(z131["g_cutk5"]),')
rep('json.dump(out, open("l126/results_l126.json", "w"), indent=1)\n'
    'print("results_l126.json written")',
    'json.dump(out, open("l131/results_l131.json", "w"), indent=1)\n'
    'print("results_l131.json written")')

# residual scan
STALE = ["cutng21", "cutng28", "z120 =", "D1", "scr0"]
# (light scan: arm tokens + l126-specific reads)
bad = []
in_doc = False
for ln, line in enumerate(SRC.split("\n"), 1):
    st = line.strip()
    if st.count('"""') % 2 == 1:
        in_doc = not in_doc
        continue
    if in_doc or st.startswith("#"):
        continue
    for t in ("cutng21", "cutng28"):
        if t in line:
            bad.append((ln, t, line.strip()[:70]))
assert not bad, bad[:6]

open("l131_verdict.py", "w").write(SRC)
py_compile.compile("l131_verdict.py", doraise=True)
print(f"l131_verdict.py written: {n_reps} reps/spans, scan clean, "
      f"py_compile OK")
