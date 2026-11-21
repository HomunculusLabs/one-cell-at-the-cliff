"""l128_verdict_build.py — asserted exact-string transform
l127_verdict.py -> l128_verdict.py.

L128 verdict: C0B on raw_l113 + B22-cert on raw_l127 (9 shared arms)
BEFORE any B23 read; H1 scr1-replication tree (criteria VERBATIM);
pooled R4 n=128 + NEW pooled scr1/2/3 n=32 + scr0 n=48; watch; sanity.
Long blocks spliced on unique openers with count==1 guards (l122 form).
"""
import py_compile
import re

SRC = open("l127_verdict.py").read()
n_reps = 0


def rep(old, new, count=1):
    global SRC, n_reps
    c = SRC.count(old)
    assert c == count, f"rep count {c} != {count}: {old[:70]!r}"
    SRC = SRC.replace(old, new)
    n_reps += 1


def span(open_line, close_line, new_block):
    """Splice from open_line (inclusive) to close_line (inclusive)."""
    global SRC, n_reps
    i = SRC.index(open_line)
    j = SRC.index(close_line, i) + len(close_line)
    assert SRC.count(open_line) == 1, open_line[:60]
    SRC = SRC[:i] + new_block + SRC[j:]
    n_reps += 1


# V1: docstring
i0 = SRC.index('"""')
i1 = SRC.index('"""', i0 + 3) + 3
NEW_DOC = '''"""L128 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B22-cert of this machinery on raw_l127 vs results_l127.json (9 shared
arms) BEFORE any B23 read, then the registered H1 scr1-REPLICATION reads
on FRESH B23 (kill criterion VERBATIM): per-arm labels for {cutscr1,
cutscr2, cutscr3} + cutscr0 context; registered tree H1A kill-replicates /
H1B re-rolls / H1C super (report WHICH cell carries; L55/L109 rule);
S1 cutk5 11th-batch replication, S2 endpoints 8th batch; POOLED R4 arms
B16..B23 n=128 full-precision Wilson (L90 form) + NEW pooled scr1/2/3
B20+B23 n=32 each + scr0 B20+B22+B23 n=48; per-side duty table 5 pairs x
12 arms; Ti_L/Tr_R/Sr_R/Ta_L watch; sanity cells. PREREG l128/PREREG.md."""'''
SRC = NEW_DOC + SRC[i1:]
n_reps += 1

# V2: batches — B23 fresh, B22 becomes context
rep("B22 = list(range(2601, 2617))       # FRESH (l127)",
    "B23 = list(range(2701, 2717))       # FRESH (l128)\n"
    "B22 = list(range(2601, 2617))  # context batch (l127, cert + pooled)")
# V3: NEW_ARMS
rep('NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutscr0", "cutcl40",\n'
    '            "cutscrL1", "cutscrL2"]',
    'NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutscr0", "cutscr1",\n'
    '            "cutscr2", "cutscr3"]')
# V4: LADDER
rep('("k5", "cutk5"), ("scr0", "cutscr0"),\n'
    '          ("cl40", "cutcl40"), ("sL1", "cutscrL1"), ("sL2", "cutscrL2")]',
    '("k5", "cutk5"), ("scr0", "cutscr0"),\n'
    '          ("scr1", "cutscr1"), ("scr2", "cutscr2"), ("scr3", "cutscr3")]')
# V5: SCR_ARMS
rep('SCR_ARMS = ["cutscr0", "cutcl40", "cutscrL1", "cutscrL2"]',
    'SCR_ARMS = ["cutscr0", "cutscr1", "cutscr2", "cutscr3"]')
# V6: loads — own raw + anchors + pins + prior results
rep('z127 = np.load("l127/raw_l127.npz")',
    'z127 = np.load("l127/raw_l127.npz")\n'
    'z128 = np.load("l128/raw_l128.npz")')
rep('r126 = json.load(open("l126/results_l126.json"))',
    'r126 = json.load(open("l126/results_l126.json"))\n'
    'r127 = json.load(open("l127/results_l127.json"))')
rep('ar = json.load(open("l127/anchors_run.json"))',
    'ar = json.load(open("l128/anchors_run.json"))')
rep('S127 = json.load(open("l127/static.json"))',
    'S127 = json.load(open("l127/static.json"))\n'
    'S125 = json.load(open("l125/static.json"))  # scr1-3 pins live here')

# V7: cert block (span)
span("# ---- Part 1b: B21-cert BEFORE any B22 read (machinery == l126 stored) ----",
     '      f"(all {len(r126[\'table\'][\'Ti\'])} arms)")',
     '''# ---- Part 1b: B22-cert BEFORE any B23 read (machinery == l127 stored) ----
b22_cert_fail = []
_shared127 = [a for a in r127["table"]["Ti"] if a in ARMS]
for a in _shared127:
    want = r127["table"]["Ti"][a]
    got = side_k(z127, a, B22, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b22_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b22_cert_fail, ("B22-cert FAIL (no B23 read)",
                           b22_cert_fail[:5])
print(f"B22-cert vs results_l127.json Ti table: PASS "
      f"(all {len(_shared127)} shared arms)")''')

# V8: p0 dict — new anchor + stored flags
rep('          c0a126_pass=ar["c0a126_pass"], c0a126_max=ar["c0a126_max"],',
    '          c0a126_pass=ar["c0a126_pass"], c0a126_max=ar["c0a126_max"],\n'
    '          c0a127_pass=ar["c0a127_pass"], c0a127_max=ar["c0a127_max"],')
rep('          g_cutscr0_stored_exact=ar["g_cutscr0_stored_exact"],',
    '          g_cutscr0_stored_exact=ar["g_cutscr0_stored_exact"],\n'
    '          g_cutscr1_stored_exact=ar["g_cutscr1_stored_exact"],\n'
    '          g_cutscr2_stored_exact=ar["g_cutscr2_stored_exact"],\n'
    '          g_cutscr3_stored_exact=ar["g_cutscr3_stored_exact"],')
rep('and p0["c0a124_pass"] and p0["c0a125_pass"]\n'
    '                  and p0["c0a126_pass"]',
    'and p0["c0a124_pass"] and p0["c0a125_pass"]\n'
    '                  and p0["c0a126_pass"] and p0["c0a127_pass"]')
rep('and p0["g_cutscr0_stored_exact"]',
    'and p0["g_cutscr0_stored_exact"] and p0["g_cutscr1_stored_exact"]\n'
    '                  and p0["g_cutscr2_stored_exact"]\n'
    '                  and p0["g_cutscr3_stored_exact"]')
rep('print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..C0A-124 "\n'
    '      "+ EXTENDED C0A-125 (4 arms incl scr0) + NEW C0A-126 + 7 stored gains:",',
    'print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..C0A-124 "\n'
    '      "+ C0A-126 retained + C0A-125 ALL-ARMS + NEW C0A-127 + 10 stored gains:",')
rep('      f"(max113 {p0[\'c0a_max\']:.1e} max125 {p0[\'c0a125_max\']:.1e} "\n'
    '      f"max126 {p0[\'c0a126_max\']:.1e})")',
    '      f"(max113 {p0[\'c0a_max\']:.1e} max125 {p0[\'c0a125_max\']:.1e} "\n'
    '      f"max126 {p0[\'c0a126_max\']:.1e} max127 {p0[\'c0a127_max\']:.1e})")')
# V9: gains print
rep('print("scr FRESH gains (band DISCLOSED):", ar["scr_fresh_gains"],\n'
    '      "scr0 stored", round(float(z127["g_cutscr0"]), 6),\n'
    '      "band_ok", ar["new_band_ok"],',
    'print("scr STORED gains (band DISCLOSED):", ar["scr_stored_gains"],\n'
    '      "scr0 stored", round(float(z128["g_cutscr0"]), 6),\n'
    '      "band_ok", ar["new_band_ok"],')
# V10: P4 health on the fresh batch
rep('af_mean = {a: round(float(np.mean([float(z127[f"af_{a}_{s}"]) for s in B22])), 6)\n'
    '           for a in ARMS}',
    'af_mean = {a: round(float(np.mean([float(z128[f"af_{a}_{s}"]) for s in B23])), 6)\n'
    '           for a in ARMS}')
rep('af_range_ok = all(0.01 < float(z127[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B22)',
    'af_range_ok = all(0.01 < float(z128[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B23)')
# V11: Part 2 table
rep('        t = side_k(z127, a, B22, pk)', '        t = side_k(z128, a, B23, pk)')
rep('print("---- B22 per-side duty table ----")',
    'print("---- B23 per-side duty table ----")')
# V12: band print
rep('print("full-arm B22 band check (disclosure only):", band_ok)',
    'print("full-arm B23 band check (disclosure only):", band_ok)')
# V13: Part 3 reads
rep('_, Rfull = duty_seeds(z127, "full", B22, "Ti")',
    '_, Rfull = duty_seeds(z128, "full", B23, "Ti")')
rep('    _, Rd = duty_seeds(z127, a, B22, "Ti")',
    '    _, Rd = duty_seeds(z128, a, B23, "Ti")')
rep('            mass=S127["scr"][a]["mass_removed"],\n'
    '            extra_mass=S127["scr"][a]["extra_mass"])',
    '            mass=S125["scr"][a]["mass_removed"],\n'
    '            extra_mass=S125["scr"][a]["extra_mass"])')
rep('        print(f"SCR {a:9s} (mass {S127[\'scr\'][a][\'mass_removed\']:.4f} extra "\n'
    '              f"{S127[\'scr\'][a][\'extra_mass\']:.4f}): meanR {t[\'meanR\']:.3f} "',
    '        print(f"SCR {a:9s} (mass {S125[\'scr\'][a][\'mass_removed\']:.4f} extra "\n'
    '              f"{S125[\'scr\'][a][\'extra_mass\']:.4f}): meanR {t[\'meanR\']:.3f} "')

# V14: classification tree (span) — H1 tree replaces C1/C2/C3
span("# ---- registered classification cells (PREREG; report WHICH carries) ----",
     'print(f"CLASSIFICATION: {cls_txt}")',
     '''# ---- registered H1/H2/H3 cells (PREREG; report WHICH carries) ----
scr1_kill = bool(scr_read["cutscr1"]["kill"])
scr1_sup = bool(scr_read["cutscr1"]["super"])
scr1_rolls = not (scr1_kill or scr1_sup)
scr2_part = bool(scr_read["cutscr2"]["partial"])
scr3_part = bool(scr_read["cutscr3"]["partial"])
scr0_sup = bool(scr_read["cutscr0"]["super"])
h1a = bool(scr1_kill)
h1c = bool(scr1_sup)
h1b = bool(scr1_rolls and not h1a and not h1c)
cells = dict(H1A_KILL_REPLICATES=h1a, H1B_RE_ROLLS=h1b, H1C_SUPER=h1c,
             scr0_super=scr0_sup, scr0_expected_super=bool(scr0_sup),
             scr2_partial=scr2_part, scr3_partial=scr3_part,
             labels={a: ("KILL" if scr_read[a]["kill"] else "no-kill")
                     + ("/SUPER" if scr_read[a]["super"] else "")
                     + ("/RESTORE" if scr_read[a]["restore"] else "")
                     + ("/PARTIAL" if scr_read[a]["partial"] else "")
                     for a in SCR_ARMS})
cls_txt = ("H1A scr1 KILL replicates on B23 — pooled 2/2 batches; the "
           "scattered .0476 kill is draw-reliable, band edge is "
           "DRAW-STRUCTURED (scr2 at .0463 does not kill-reliably)") if h1a else (
          "H1B scr1 re-rolls on B23 (no kill, no super) — the "
          ".0442-.0476 scattered band is a LOTTERY on both batches; "
          "reliable kill->super starts ~.054 removed-extra (L127 law "
          "extends)") if h1b else (
          "H1C scr1 SUPER-raises on B23 — widest lottery spread (kill -> "
          "super across batches at a fixed draw); H1B conclusion with the "
          "strongest spread") if h1c else "MIXED (should not reach)"
print(f"CLASSIFICATION: {cls_txt}")''')
rep('if not scr0_sup:\n'
    '    print("scr0 context MISS (expected SUPER 2nd batch) — scr-family "\n'
    '          "batch-fragility disclosure QUALIFIES every cell above")',
    'if not scr0_sup:\n'
    '    print("scr0 context MISS (expected SUPER 3rd batch) — scr-family "\n'
    '          "batch-fragility disclosure QUALIFIES every cell above")')

# V15/V16: S1/S2 text
rep('s1 = dict(k5_kill=bool(killmap["k5"]), cls=(\n'
    '    "cutk5 KILLS on B22 — 10th consecutive batch "\n'
    '    "(B12/B14/B15/B16/B17/B18/B19/B20/B21/B22)"\n'
    '    if killmap["k5"] else\n'
    '    "cutk5 does NOT kill on B22 — DISCLOSED (L118 lottery class)"))',
    's1 = dict(k5_kill=bool(killmap["k5"]), cls=(\n'
    '    "cutk5 KILLS on B23 — 11th consecutive batch "\n'
    '    "(B12/B14/B15/B16/B17/B18/B19/B20/B21/B22/B23)"\n'
    '    if killmap["k5"] else\n'
    '    "cutk5 does NOT kill on B23 — DISCLOSED (L118 lottery class)"))')
rep('    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (7th batch each)"',
    '    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (8th batch each)"')

# V17: pooled R4 block (span) — n=128 incl B23
span("pooled = {}",
     '          f"B21 {pooled[a][\'k_b21\']}/16 + B22 {pooled[a][\'k_b22\']}/16) "\n'
     '          f"p_hat {k/112:.3f} Wilson [{lb:.4f}, {ub:.4f}]")',
     '''pooled = {}
for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    _, Rb20 = duty_seeds(z125, a, B20, "Ti")
    _, Rb21 = duty_seeds(z126, a, B21, "Ti")
    _, Rb22 = duty_seeds(z127, a, B22, "Ti")
    _, Rb23 = duty_seeds(z128, a, B23, "Ti")
    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21, Rb22, Rb23])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 128)
    pooled[a] = dict(k128=k, p_hat=k / 128, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()),
                     k_b18=int((Rb18 >= .5).sum()),
                     k_b19=int((Rb19 >= .5).sum()),
                     k_b20=int((Rb20 >= .5).sum()),
                     k_b21=int((Rb21 >= .5).sum()),
                     k_b22=int((Rb22 >= .5).sum()),
                     k_b23=int((Rb23 >= .5).sum()))
    print(f"POOLED Ti_R {a:8s} k {k}/128 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16 + B18 {pooled[a]['k_b18']}/16 + "
          f"B19 {pooled[a]['k_b19']}/16 + B20 {pooled[a]['k_b20']}/16 + "
          f"B21 {pooled[a]['k_b21']}/16 + B22 {pooled[a]['k_b22']}/16 + "
          f"B23 {pooled[a]['k_b23']}/16) "
          f"p_hat {k/128:.3f} Wilson [{lb:.4f}, {ub:.4f}]")''')

# V18: pooled scr family (span) — scr0 n=48, scr1-3 n=32
span("# NEW pooled cutscr0: B20 + B22 union n=32 (2-batch; L128 owes the rest)",
     '      f"B22 {pooled_scr0[\'k_b22\']}/16) p_hat {k_sc/32:.3f} "\n'
     '      f"Wilson [{lb:.4f}, {ub:.4f}]")',
     '''# scr family pooled: scr0 = B20+B22+B23 (n=48, bonus 3rd batch);
# scr1/scr2/scr3 = B20+B23 (n=32 each — THE L128 deliverable).
pooled_scr = {}
for a in SCR_ARMS:
    _, Rs_b20 = duty_seeds(z125, a, B20, "Ti")
    if a == "cutscr0":
        _, Rs_b22 = duty_seeds(z127, a, B22, "Ti")
        _, Rs_b23 = duty_seeds(z128, a, B23, "Ti")
        alls = np.concatenate([Rs_b20, Rs_b22, Rs_b23])
        n = 48
        k_s = int((alls >= .5).sum())
        lb, ub = wilson(k_s, n)
        pooled_scr[a] = dict(k48=k_s, p_hat=k_s / n, lb=lb, ub=ub,
                             k_b20=int((Rs_b20 >= .5).sum()),
                             k_b22=int((Rs_b22 >= .5).sum()),
                             k_b23=int((Rs_b23 >= .5).sum()))
        print(f"POOLED Ti_R {a} k {k_s}/48 (B20 {pooled_scr[a]['k_b20']}/16"
              f" + B22 {pooled_scr[a]['k_b22']}/16"
              f" + B23 {pooled_scr[a]['k_b23']}/16) "
              f"p_hat {k_s/n:.3f} Wilson [{lb:.4f}, {ub:.4f}]")
    else:
        _, Rs_b23 = duty_seeds(z128, a, B23, "Ti")
        alls = np.concatenate([Rs_b20, Rs_b23])
        n = 32
        k_s = int((alls >= .5).sum())
        lb, ub = wilson(k_s, n)
        pooled_scr[a] = dict(k32=k_s, p_hat=k_s / n, lb=lb, ub=ub,
                             k_b20=int((Rs_b20 >= .5).sum()),
                             k_b23=int((Rs_b23 >= .5).sum()))
        print(f"POOLED Ti_R {a} k {k_s}/32 (B20 {pooled_scr[a]['k_b20']}/16"
              f" + B23 {pooled_scr[a]['k_b23']}/16) "
              f"p_hat {k_s/n:.3f} Wilson [{lb:.4f}, {ub:.4f}]")''')

# V19: watch context note
rep('        note="scr1 (scattered, .0476 extra) KILLED on B20 — the "\n'
    '             "heavy-scattered 2x2 cell, cross-batch"))',
    '        note="scr1 (scattered, .0476 extra) KILLED on B20; L128 "\n'
    '             "re-rolls it on B23 (pooled_scr.cutscr1) — the "\n'
    '             "heavy-scattered cell, now 2-batch"))')

# V20: out dict
rep('           scr_fresh_gains=ar["scr_fresh_gains"],',
    '           scr_stored_gains=ar["scr_stored_gains"],')
rep('           g_cutk5=float(z127["g_cutk5"]),\n'
    '           g_cutscr0=float(z127["g_cutscr0"]),',
    '           g_cutk5=float(z128["g_cutk5"]),\n'
    '           g_cutscr0=float(z128["g_cutscr0"]),\n'
    '           g_cutscr1=float(z128["g_cutscr1"]),\n'
    '           g_cutscr2=float(z128["g_cutscr2"]),\n'
    '           g_cutscr3=float(z128["g_cutscr3"]),')
rep('           mass_scr={a: S127["scr"][a]["mass_removed"] for a in SCR_ARMS},\n'
    '           extra_mass_scr={a: S127["scr"][a]["extra_mass"] for a in SCR_ARMS},',
    '           mass_scr={a: S125["scr"][a]["mass_removed"] for a in SCR_ARMS},\n'
    '           extra_mass_scr={a: S125["scr"][a]["extra_mass"] for a in SCR_ARMS},')
rep('           coherence=dict(cells=cells, cls=cls_txt, s1=s1, s2=s2),\n'
    '           pooled=pooled, pooled_scr0=pooled_scr0,\n'
    '           b21_cert_pass=True,',
    '           h1=dict(cells=cells, cls=cls_txt, s1=s1, s2=s2),\n'
    '           pooled=pooled, pooled_scr=pooled_scr,\n'
    '           b22_cert_pass=True,')
rep('json.dump(out, open("l127/results_l127.json", "w"), indent=1)\n'
    'print("results_l127.json written")',
    'json.dump(out, open("l128/results_l128.json", "w"), indent=1)\n'
    'print("results_l128.json written")')

open("l128_verdict.py", "w").write(SRC)
print(f"l128_verdict.py written ({len(SRC)} chars, {n_reps} reps)")

# ---- residual scan (code lines only) ----
bad = []
for ln, line in enumerate(SRC.splitlines(), 1):
    if line.strip().startswith("#"):
        continue
    for tok in ("cutcl40", "cutscrL", "b21_cert", "k112", "/112", " 112)",
                "scr_fresh_gains", "coherence=",
                "pooled_scr0", "B22 read"):
        if tok in line:
            bad.append((ln, tok, line.strip()[:80]))
assert not bad, ("stale tokens in code lines", bad[:10])
print("residual scan: CLEAN")

# direction check: reads/writes
loads = re.findall(r'np\.load\(\s*"(l1\d+/[^"]+\.npz)"', SRC)
writes = re.findall(r'json\.dump\([^,]+, open\("(l1\d+/[^"]+)"', SRC)
assert "l128/raw_l128.npz" in loads
assert writes == ["l128/results_l128.json"], writes
print("direction check OK:", sorted(set(loads)))

py_compile.compile("l128_verdict.py", doraise=True)
print("py_compile OK")
