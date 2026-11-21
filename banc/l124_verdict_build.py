"""Build l124_verdict.py from l123_verdict.py via exact-string transforms.

(1) docstring splice, (2) batch defs (B19 fresh; B18 context), (3) inputs
(z124/ar-l124/r123 added), (4) p4 af reads z124/B19, (5) table + band +
dose reads z124/B19, (6) l123 B18 context block added, (7) B17-cert ->
B18-cert (r123 Ti table, ALL 10 arms, BEFORE any B19 window read),
(8) W1-W4 classification -> R1/R2/R3 pre-registered decision tree,
(9) S1 7th-batch / S2 4th-batch text, (10) pooled R4 -> n=64 union
+ NEW pooled_window n=32 (B18+B19), (11) out-dict rewires + results path.
Count-pinned reps; drift guard aborts; py_compile at the end.
"""
import py_compile
import sys

SRC = open("l123_verdict.py").read()
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


# 1. docstring splice
NEW_DOC = '''"""L124 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B18-cert of this machinery on raw_l123 vs results_l123.json BEFORE any
B19 window read, then the registered REBASE reads on FRESH B19 (kill
criterion VERBATIM): R1 cutwB deep-kill robust, R2 cutwA partial band
([.35,.50], kR 3-8) robust-or-redraw, R3 either half reaches RESTORE/
SUPER (revises L123 W4 toward W1/W2), pre-registered decision tree;
S1 cutk5 7th-batch replication, S2 endpoints 4th batch; POOLED window
arms B18+B19 n=32 + R4 arms n=64 full-precision Wilson (L90 form);
per-side duty table 5 pairs x 10 arms; L-axis + Sr_R watch; sanity
cells. PREREG l124/PREREG.md."""'''
assert SRC.startswith('"""L123 verdict:') and SRC.count('"""L123 verdict:') == 1, \
    "docstring opener drift"
_doc_end = SRC.index('"""', 3) + 3
SRC = NEW_DOC + SRC[_doc_end:]
print("ok x1: verdict docstring spliced")

# 2. batch defs
rep('''B18 = list(range(2201, 2217))       # FRESH (l123)
B17 = list(range(2101, 2117))  # context batch (l122, cert + pooled)''',
    '''B19 = list(range(2301, 2317))       # FRESH (l124)
B18 = list(range(2201, 2217))  # context batch (l123, cert + pooled)
B17 = list(range(2101, 2117))  # context batch (l122, pooled)''', count=1)

# 3. inputs
rep('''z123 = np.load("l123/raw_l123.npz")''',
    '''z123 = np.load("l123/raw_l123.npz")
z124 = np.load("l124/raw_l124.npz")''', count=1)
rep('''ar = json.load(open("l123/anchors_run.json"))''',
    '''ar = json.load(open("l124/anchors_run.json"))
r123 = json.load(open("l123/results_l123.json"))''', count=1)

# 4. p4 af reads -> z124/B19
rep('''af_mean = {a: round(float(np.mean([float(z123[f"af_{a}_{s}"]) for s in B18])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z123[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B18)''',
    '''af_mean = {a: round(float(np.mean([float(z124[f"af_{a}_{s}"]) for s in B19])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z124[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B19)''',
    count=1)

# 5. table + band + dose reads -> z124/B19
rep('''        t = side_k(z123, a, B18, pk)''',
    '''        t = side_k(z124, a, B19, pk)''', count=1)
rep('print("---- B18 per-side duty table ----")',
    'print("---- B19 per-side duty table ----")', count=1)
rep('print("full-arm B18 band check (disclosure only):", band_ok)',
    'print("full-arm B19 band check (disclosure only):", band_ok)', count=1)
rep('''_, Rfull = duty_seeds(z123, "full", B18, "Ti")''',
    '''_, Rfull = duty_seeds(z124, "full", B19, "Ti")''', count=1)
rep('''    _, Rd = duty_seeds(z123, a, B18, "Ti")''',
    '''    _, Rd = duty_seeds(z124, a, B19, "Ti")''', count=1)

# 6. l123 B18 context block (after the l122 B17 context)
rep('''dose["l122_stored_b17_context"] = {
    "Ti_meanR": r122["dose"]["Ti"]["meanR"],
    "Ti_kR": r122["dose"]["Ti"]["kR"],
    "kill": r122["dose"]["Ti"]["kill"]}''',
    '''dose["l122_stored_b17_context"] = {
    "Ti_meanR": r122["dose"]["Ti"]["meanR"],
    "Ti_kR": r122["dose"]["Ti"]["kR"],
    "kill": r122["dose"]["Ti"]["kill"]}
dose["l123_stored_b18_context"] = {
    "Ti_meanR": r123["dose"]["Ti"]["meanR"],
    "Ti_kR": r123["dose"]["Ti"]["kR"],
    "kill": r123["dose"]["Ti"]["kill"]}''', count=1)

# 7. B17-cert -> B18-cert (r123 Ti table, ALL 10 arms incl wA/wB)
rep('''# ---- Part 4: B17-cert FIRST, then W1-W4 + S1/S2 + R4 pooled n=48 ----
# B17-cert BEFORE any window read: machinery recomputed on raw_l122 B17 ==
# results_l122.json Ti table (l122's own arms only; wA/wB not in l122).
b17_cert_fail = []
for a in r122["table"]["Ti"]:
    want = r122["table"]["Ti"][a]
    got = side_k(z122, a, B17, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b17_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b17_cert_fail, ("B17-cert FAIL (no window read)",
                           b17_cert_fail[:5])
print(f"B17-cert vs results_l122.json Ti table: PASS "
      f"(all {len(r122['table']['Ti'])} arms)")''',
    '''# ---- Part 4: B18-cert FIRST, then R1/R2/R3 + S1/S2 + pooled ----
# B18-cert BEFORE any B19 window read: machinery recomputed on raw_l123
# B18 == results_l123.json Ti table (ALL 10 arms incl wA/wB — l123 ran
# every arm at all 18 seeds).
b18_cert_fail = []
for a in r123["table"]["Ti"]:
    want = r123["table"]["Ti"][a]
    got = side_k(z123, a, B18, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b18_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b18_cert_fail, ("B18-cert FAIL (no B19 read)",
                           b18_cert_fail[:5])
print(f"B18-cert vs results_l123.json Ti table: PASS "
      f"(all {len(r123['table']['Ti'])} arms)")''', count=1)

# 8. W1-W4 -> R1/R2/R3 pre-registered decision tree (whole block)
rep('''tA, tB = table["Ti"]["cutwA"], table["Ti"]["cutwB"]
killA, killB = killmap["wA"], killmap["wB"]
restA, restB = _restore(tA), _restore(tB)
if (killA != killB) and ((killA and restB) or (killB and restA)):
    wcls = ("W1 XOR: the flip is carried by ONE 5-cell half at quasi-equal "
            "mass — placement pattern; NAME the half; single-batch, "
            "rebase owed (L88/L90)")
elif (not killA) and (not killB) and restA and restB:
    wcls = ("W2 BOTH-RESTORE: the flip completes within EITHER half "
            "(k* <= 24); window redundancy")
elif killA and killB:
    wcls = ("W3 BOTH-KILL: the flip needs cells beyond rank 24 (k* in "
            "(24,29]) or the whole window")
else:
    wcls = ("W4 INTERMEDIATE/MIXED: per-arm disclosed, lottery class "
            "(L118/L121 middle); no rounding to any story")
print(f"WINDOW: cutwA meanR {tA['meanR']:.3f} kR {tA['kR']:2d} "
      f"({'KILL' if killA else 'no-kill'}{'/RESTORE' if restA else ''}"
      f"{'/SUPER' if _super(tA) else ''}) | cutwB meanR {tB['meanR']:.3f} "
      f"kR {tB['kR']:2d} ({'KILL' if killB else 'no-kill'}"
      f"{'/RESTORE' if restB else ''}{'/SUPER' if _super(tB) else ''})")
print(f"W classification: {wcls}")''',
    '''tA, tB = table["Ti"]["cutwA"], table["Ti"]["cutwB"]
killA, killB = killmap["wA"], killmap["wB"]
restA, restB = _restore(tA), _restore(tB)
# R1/R2/R3 registered reads (PREREG): partial band = meanR [.35,.50] &
# kR 3..8 (L123 wA shape). Decision tree PRE-REGISTERED, never re-fit.
partialA = bool(.35 <= tA["meanR"] <= .50 and 3 <= tA["kR"] <= 8)
r1 = bool(killB)
r2 = "PARTIAL-ROBUST" if partialA else "RE-DRAW"
r3 = bool(restA or restB or _super(tA) or _super(tB))
if r3:
    wcls = ("REVISION toward W1/W2: a half reached RESTORE/SUPER on B19 — "
            "a half CAN flip alone after all; disclosed")
elif killA and killB:
    wcls = ("REVISION toward W3: both halves kill on B19 — window "
            "coherence extends past rank 24; disclosed")
elif r1 and partialA:
    wcls = ("W4 BATCH-ROBUST: cutwB deep-kill + cutwA partial replicate "
            "on B19 — neither half flips alone; 2-step window structure "
            "holds (L123 finding now 2-batch)")
else:
    wcls = ("MIXED/RE-DRAW: killB miss or cutwA shape change on B19 — "
            "lottery class; disclosed, no story rounding")
print(f"WINDOW: cutwA meanR {tA['meanR']:.3f} kR {tA['kR']:2d} "
      f"({'KILL' if killA else 'no-kill'}{'/RESTORE' if restA else ''}"
      f"{'/SUPER' if _super(tA) else ''}{'/PARTIAL' if partialA else ''}) "
      f"| cutwB meanR {tB['meanR']:.3f} "
      f"kR {tB['kR']:2d} ({'KILL' if killB else 'no-kill'}"
      f"{'/RESTORE' if restB else ''}{'/SUPER' if _super(tB) else ''})")
print(f"R1 cutwB kill: {'PASS' if r1 else 'FAIL'} | R2 cutwA: {r2} | "
      f"R3 revision trigger: {'FIRED' if r3 else 'no'}")
print(f"REBASE classification: {wcls}")''', count=1)

# 9. S1/S2 batch-count text
rep('''s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B18 — 6th consecutive batch (B12/B14/B15/B16/B17/B18)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B18 — DISCLOSED (L118 lottery class)"))''',
    '''s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B19 — 7th consecutive batch (B12/B14/B15/B16/B17/B18/B19)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B19 — DISCLOSED (L118 lottery class)"))''', count=1)
rep('''s2 = dict(ng19_kill=bool(killmap["19"]),
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (3rd batch each)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))''',
    '''s2 = dict(ng19_kill=bool(killmap["19"]),
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (4th batch each)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))''', count=1)

# 10. pooled: R4 -> n=64 union + NEW pooled_window n=32
rep('''# R4: pooled batch-union B16+B17+B18 n=48, FULL-PRECISION Wilson (L90)
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    allb = np.concatenate([Rb16, Rb17, Rb18])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 48)
    pooled[a] = dict(k48=k, p_hat=k / 48, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()),
                     k_b18=int((Rb18 >= .5).sum()))
    print(f"POOLED Ti_R {a:7s} k {k}/48 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16 + B18 {pooled[a]['k_b18']}/16) "
          f"p_hat {k/48:.3f} Wilson [{lb:.4f}, {ub:.4f}]")''',
    '''# R4: pooled batch-union B16+B17+B18+B19 n=64, FULL-PRECISION Wilson
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 64)
    pooled[a] = dict(k64=k, p_hat=k / 64, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()),
                     k_b18=int((Rb18 >= .5).sum()),
                     k_b19=int((Rb19 >= .5).sum()))
    print(f"POOLED Ti_R {a:7s} k {k}/64 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16 + B18 {pooled[a]['k_b18']}/16 + "
          f"B19 {pooled[a]['k_b19']}/16) "
          f"p_hat {k/64:.3f} Wilson [{lb:.4f}, {ub:.4f}]")
# WINDOW pooled union B18+B19 n=32 (the L124 deliverable; B18 side
# certified above BEFORE pooling)
pooled_window = {}
for a in ("cutwA", "cutwB"):
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    allb = np.concatenate([Rb18, Rb19])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 32)
    pooled_window[a] = dict(k32=k, p_hat=k / 32, lb=lb, ub=ub,
                            k_b18=int((Rb18 >= .5).sum()),
                            k_b19=int((Rb19 >= .5).sum()))
    print(f"POOLED-WINDOW Ti_R {a:7s} k {k}/32 (B18 "
          f"{pooled_window[a]['k_b18']}/16 + B19 "
          f"{pooled_window[a]['k_b19']}/16) p_hat {k/32:.3f} "
          f"Wilson [{lb:.4f}, {ub:.4f}]")''', count=1)

# 11. p0 additions + out-dict rewires + results path
rep('''          c0a122_pass=ar["c0a122_pass"], c0a122_max=ar["c0a122_max"],''',
    '''          c0a122_pass=ar["c0a122_pass"], c0a122_max=ar["c0a122_max"],
          c0a123_pass=ar["c0a123_pass"], c0a123_max=ar["c0a123_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutwB_stored_exact=ar["g_cutwB_stored_exact"],''', count=1)
rep('''p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"]''',
    '''p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"] and p0["c0a123_pass"]
                  and p0["g_cutwA_stored_exact"] and p0["g_cutwB_stored_exact"]''',
    count=1)
rep('''print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (3 arms vs raw_l121) + C0A-122 "
      "(3 arms vs raw_l122) + 6 stored gains:",''',
    '''print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (3 arms vs raw_l121) + C0A-122 "
      "(3 arms vs raw_l122) + C0A-123 (5 arms vs raw_l123) + "
      "8 stored gains:",''', count=1)
rep('''print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutwA", "cutwB")},
      "cutk5", round(float(z123["g_cutk5"]), 6), "(stored, asserted)",
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})''',
    '''print("stored gains (asserted EXACT):",
      {k: round(ar["g_" + k], 6) for k in ("cutwA", "cutwB")},
      "cutk5", round(float(z124["g_cutk5"]), 6),
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})''',
    count=1)
rep('''           fresh_gains={a: ar["g_" + a] for a in ("cutwA", "cutwB")},
           g_cutk5=float(z123["g_cutk5"]),''',
    '''           stored_gains={a: ar["g_" + a] for a in ("cutwA", "cutwB")},
           g_cutk5=float(z124["g_cutk5"]),''', count=1)
rep('''           window=dict(cls=wcls, killA=bool(killA), killB=bool(killB),
                       restA=bool(restA), restB=bool(restB),
                       superA=_super(tA), superB=_super(tB), s1=s1, s2=s2),
           pooled=pooled, b17_cert_pass=True,''',
    '''           window=dict(cls=wcls, r1=bool(r1), r2=r2, r3=bool(r3),
                       killA=bool(killA), killB=bool(killB),
                       restA=bool(restA), restB=bool(restB),
                       partialA=bool(partialA),
                       superA=_super(tA), superB=_super(tB), s1=s1, s2=s2),
           pooled=pooled, pooled_window=pooled_window,
           b18_cert_pass=True,''', count=1)
rep('''json.dump(out, open("l123/results_l123.json", "w"), indent=1)
print("results_l123.json written")''',
    '''json.dump(out, open("l124/results_l124.json", "w"), indent=1)
print("results_l124.json written")''', count=1)

open("l124_verdict.py", "w").write(SRC)

# ---------------- residual scan ----------------
bad = []
s = open("l124_verdict.py").read()
for tok in ("W1 XOR", "W2 BOTH-RESTORE", "W3 BOTH-KILL", "W4 INTERMEDIATE",
            "b17_cert", "B17-cert", "6th consecutive", "3rd batch each",
            "k48", "n=48"):
    if tok in s:
        bad.append(("l124_verdict.py", "stale token " + tok))
if n_err or bad:
    print("BUILD FAIL:", n_err, bad)
    sys.exit(1)
py_compile.compile("l124_verdict.py", doraise=True)
print("BUILD OK: l124_verdict.py compiled; scans clean")
