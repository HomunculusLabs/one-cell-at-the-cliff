"""Build l125_verdict.py from l124_verdict.py via exact-string transforms.

(1) docstring splice, (2) batch consts (B20 fresh l125; B19 context l124),
(3) ARMS/NEW_ARMS/LADDER -> scramble ladder, (4) loads: +z125/r124/S125,
z124 becomes context, (5) P0 anchor keys (c0a124, scr fresh gains),
(6) table/pooled reads on B20 via z125, (7) l124 stored context added,
(8) B19-cert (raw_l124 vs results_l124.json Ti table) BEFORE any B20 read,
(9) R1/R2/R3 window tree -> SC1/SC2 scramble tree, (10) pooled union
B16..B20 n=80, (11) output path. Count-pinned reps; py_compile.
"""
import py_compile
import sys

SRC = open("l124_verdict.py").read()
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
NEW_DOC = '''"""L125 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B19-cert of this machinery on raw_l124 vs results_l124.json BEFORE any
B20 scramble read, then the registered SCRAMBLE reads on FRESH B20 (kill
criterion VERBATIM): SC1 any scramble SUPER-RAISES (count/dose story
alive — placement dead), SC2 none super-raises/restores (placement-owned,
the registered expectation; scr0 = max-mass arm closes the mass
objection); pre-registered decision tree; S1 cutk5 8th-batch replication,
S2 endpoints 5th batch; POOLED R4 arms B16..B20 n=80 full-precision
Wilson (L90 form); per-side duty table 5 pairs x 12 arms; Ti_L + Tr_R +
Sr_R watch; sanity cells. PREREG l125/PREREG.md."""'''
assert SRC.startswith('"""L124 verdict:') and SRC.count('"""L124 verdict:') == 1
_doc_end = SRC.index('"""', 3) + 3
SRC = NEW_DOC + SRC[_doc_end:]
print("ok x1: verdict docstring spliced")

# 2. batch consts (B18 kept: pooled union still needs it)
rep('''B19 = list(range(2301, 2317))       # FRESH (l124)
B18 = list(range(2201, 2217))  # context batch (l123, cert + pooled)''',
    '''B20 = list(range(2401, 2417))       # FRESH (l125)
B19 = list(range(2301, 2317))  # context batch (l124, cert + pooled)
B18 = list(range(2201, 2217))  # context batch (l123, pooled)''',
    count=1)

# 3. arms / ladder
rep('''NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutwA", "cutwB"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("19", "cutng19"), ("wA", "cutwA"),
          ("wB", "cutwB"), ("29", "cutng29"), ("58", "cut58"),
          ("k5", "cutk5")]''',
    '''NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutscr0", "cutscr1",
            "cutscr2", "cutscr3"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("19", "cutng19"), ("scr0", "cutscr0"),
          ("scr1", "cutscr1"), ("scr2", "cutscr2"), ("scr3", "cutscr3"),
          ("29", "cutng29"), ("58", "cut58"), ("k5", "cutk5")]''', count=1)

# 4. loads: z125 + r124 + S125; z124 context
rep('''z124 = np.load("l124/raw_l124.npz")''',
    '''z124 = np.load("l124/raw_l124.npz")
z125 = np.load("l125/raw_l125.npz")''', count=1)
rep('''ar = json.load(open("l124/anchors_run.json"))''',
    '''ar = json.load(open("l125/anchors_run.json"))
r124 = json.load(open("l124/results_l124.json"))''', count=1)
rep('''S123 = json.load(open("l123/static.json"))''',
    '''S125 = json.load(open("l125/static.json"))''', count=1)

# 5. P0 anchor keys
rep('''          c0a123_pass=ar["c0a123_pass"], c0a123_max=ar["c0a123_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutwB_stored_exact=ar["g_cutwB_stored_exact"],''',
    '''          c0a123_pass=ar["c0a123_pass"], c0a123_max=ar["c0a123_max"],
          c0a124_pass=ar["c0a124_pass"], c0a124_max=ar["c0a124_max"],''',
    count=1)
rep('''p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"] and p0["c0a123_pass"]
                  and p0["g_cutwA_stored_exact"] and p0["g_cutwB_stored_exact"]
                  and p0["g_cut58_stored_exact"]''',
    '''p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"] and p0["c0a123_pass"]
                  and p0["c0a124_pass"]
                  and p0["g_cut58_stored_exact"]''', count=1)
rep('''print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (3 arms vs raw_l121) + C0A-122 "
      "(3 arms vs raw_l122) + C0A-123 (5 arms vs raw_l123) + "
      "8 stored gains:",''',
    '''print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (3 arms vs raw_l121) + C0A-122 "
      "(3 arms vs raw_l122) + C0A-123 (3 shared arms vs raw_l123) + "
      "C0A-124 (3 arms vs raw_l124) + 6 stored gains:",''', count=1)
rep('''print("stored gains (asserted EXACT):",
      {k: round(ar["g_" + k], 6) for k in ("cutwA", "cutwB")},
      "cutk5", round(float(z124["g_cutk5"]), 6),
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})''',
    '''print("scr FRESH gains (band DISCLOSED):", ar["scr_fresh_gains"],
      "cutk5", round(float(z125["g_cutk5"]), 6),
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})''',
    count=1)

# 6. P4 + table reads -> B20 / z125
rep('''af_mean = {a: round(float(np.mean([float(z124[f"af_{a}_{s}"]) for s in B19])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z124[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B19)''',
    '''af_mean = {a: round(float(np.mean([float(z125[f"af_{a}_{s}"]) for s in B20])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z125[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B20)''',
    count=1)
rep('''# ---- Part 2: full 5-pair x 10-arm per-side table (B16, n=16) ----''',
    '''# ---- Part 2: full 5-pair x 12-arm per-side table (B20, n=16) ----''',
    count=1)
rep('''        t = side_k(z124, a, B19, pk)''', '''        t = side_k(z125, a, B20, pk)''', count=1)
rep('''print("---- B19 per-side duty table ----")''',
    '''print("---- B20 per-side duty table ----")''', count=1)
rep('''print("full-arm B19 band check (disclosure only):", band_ok)''',
    '''print("full-arm B20 band check (disclosure only):", band_ok)''', count=1)

# 7. Part 3 reads -> z125/B20 + l124 context added
rep('''_, Rfull = duty_seeds(z124, "full", B19, "Ti")''',
    '''_, Rfull = duty_seeds(z125, "full", B20, "Ti")''', count=1)
rep('''    _, Rd = duty_seeds(z124, a, B19, "Ti")''',
    '''    _, Rd = duty_seeds(z125, a, B20, "Ti")''', count=1)
rep('''dose["l123_stored_b18_context"] = {
    "Ti_meanR": r123["dose"]["Ti"]["meanR"],
    "Ti_kR": r123["dose"]["Ti"]["kR"],
    "kill": r123["dose"]["Ti"]["kill"]}
print("l117 B12 / l119 B14 / l120 B15 / l121 B16 / l122 B17 context:",''',
    '''dose["l123_stored_b18_context"] = {
    "Ti_meanR": r123["dose"]["Ti"]["meanR"],
    "Ti_kR": r123["dose"]["Ti"]["kR"],
    "kill": r123["dose"]["Ti"]["kill"]}
dose["l124_stored_b19_context"] = {
    "Ti_meanR": r124["dose"]["Ti"]["meanR"],
    "Ti_kR": r124["dose"]["Ti"]["kR"],
    "kill": r124["dose"]["Ti"]["kill"]}
print("l117 B12 / l119 B14 / l120 B15 / l121 B16 / l122 B17 / l124 B19 context:",''',
    count=1)

# 8. B19-cert BEFORE any B20 read (l124 machinery cert)
rep('''# ---- Part 4: B18-cert FIRST, then R1/R2/R3 + S1/S2 + pooled ----
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
      f"(all {len(r123['table']['Ti'])} arms)")''',
    '''# ---- Part 4: B19-cert FIRST, then SC1/SC2 + S1/S2 + pooled ----
# B19-cert BEFORE any B20 scramble read: machinery recomputed on raw_l124
# B19 == results_l124.json Ti table (ALL 10 l124 arms incl wA/wB — l124
# ran every arm at all 18 seeds).
b19_cert_fail = []
for a in r124["table"]["Ti"]:
    want = r124["table"]["Ti"][a]
    got = side_k(z124, a, B19, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b19_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b19_cert_fail, ("B19-cert FAIL (no B20 read)",
                           b19_cert_fail[:5])
print(f"B19-cert vs results_l124.json Ti table: PASS "
      f"(all {len(r124['table']['Ti'])} arms)")''', count=1)

# 9. SC1/SC2 scramble tree replaces the R1/R2/R3 window tree
rep('''tA, tB = table["Ti"]["cutwA"], table["Ti"]["cutwB"]
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
print(f"REBASE classification: {wcls}")''',
    '''SCR_ARMS = ("cutscr0", "cutscr1", "cutscr2", "cutscr3")
scr_read = {}
for _sa in SCR_ARMS:
    t = table["Ti"][_sa]
    scr_read[_sa] = dict(
        meanR=t["meanR"], kR=t["kR"], meanL=t["meanL"], kL=t["kL"],
        kill=killmap[_sa.replace("cutscr", "scr")],
        restore=_restore(t), super=_super(t),
        partial=bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8),
        mass=S125["scr"][_sa]["mass_removed"])
    print(f"SCR {_sa} (mass {S125['scr'][_sa]['mass_removed']:.4f}): "
          f"meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 -> "
          f"{'KILL' if scr_read[_sa]['kill'] else 'no-kill'}"
          f"{'/RESTORE' if scr_read[_sa]['restore'] else ''}"
          f"{'/SUPER' if scr_read[_sa]['super'] else ''}"
          f"{'/PARTIAL' if scr_read[_sa]['partial'] else ''}")
any_super = any(scr_read[_sa]["super"] for _sa in SCR_ARMS)
any_restore = any(scr_read[_sa]["restore"] for _sa in SCR_ARMS)
scr0_super = scr_read["cutscr0"]["super"]
sc1 = bool(any_super)
if sc1:
    wcls = ("COUNT-CARRIED: a scramble SUPER-RAISES — the flip is "
            "count/dose, placement story dead; disclosed (which arm "
            "fired is in scr_read)")
elif any_restore:
    wcls = ("MIXED: a scramble RESTORES without super-raising — neither "
            "pure story; disclosed")
else:
    wcls = ("PLACEMENT-OWNED: NO scramble flips the window's super-raise "
            "(registered expectation; scr0 no-super closes the mass "
            "objection: max-mass .2490 vs window .2588)")
print(f"SC1 any scramble SUPER: {'FIRED' if sc1 else 'no'} | "
      f"SC2 no-super/no-restore: "
      f"{'HOLDS' if not (sc1 or any_restore) else 'VIOLATED'} | "
      f"scr0 (max-mass) super: {'YES' if scr0_super else 'no'}")
print(f"SCRAMBLE classification: {wcls}")''', count=1)

# 10. S1/S2 wording + pooled union B16..B20 n=80
rep('''s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B19 — 7th consecutive batch (B12/B14/B15/B16/B17/B18/B19)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B19 — DISCLOSED (L118 lottery class)"))''',
    '''s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B20 — 8th consecutive batch (B12/B14/B15/B16/B17/B18/B19/B20)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B20 — DISCLOSED (L118 lottery class)"))''',
    count=1)
rep('''s2 = dict(ng19_kill=bool(killmap["19"]),
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (4th batch each)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))''',
    '''s2 = dict(ng19_kill=bool(killmap["19"]),
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (5th batch each)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))''', count=1)
rep('''# R4: pooled batch-union B16+B17+B18+B19 n=64, FULL-PRECISION Wilson
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
          f"Wilson [{lb:.4f}, {ub:.4f}]")''',
    '''# R4: pooled batch-union B16+B17+B18+B19+B20 n=80, FULL-PRECISION Wilson
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    _, Rb20 = duty_seeds(z125, a, B20, "Ti")
    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 80)
    pooled[a] = dict(k80=k, p_hat=k / 80, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()),
                     k_b18=int((Rb18 >= .5).sum()),
                     k_b19=int((Rb19 >= .5).sum()),
                     k_b20=int((Rb20 >= .5).sum()))
    print(f"POOLED Ti_R {a:7s} k {k}/80 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16 + B18 {pooled[a]['k_b18']}/16 + "
          f"B19 {pooled[a]['k_b19']}/16 + B20 {pooled[a]['k_b20']}/16) "
          f"p_hat {k/80:.3f} Wilson [{lb:.4f}, {ub:.4f}]")
# NO window pooling in L125 (window halves not re-run; l124 union final)
pooled_window = {"note": "not run in L125 — l124 n=32 union stands"}''',
    count=1)

# 11. out dict
rep('''out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           new_band_ok=ar["new_band_ok"],
           stored_gains={a: ar["g_" + a] for a in ("cutwA", "cutwB")},
           g_cutk5=float(z124["g_cutk5"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cut58", "k58"))},
           mass_window={a: S123["window_" + a[-2:]]["mass_removed"]
                        for a in ("cutwA", "cutwB")},
           extra_mass={a: S123["window_" + a[-2:]]["extra_mass"]
                       for a in ("cutwA", "cutwB")},
           mass_cutk5=SM["ladder"]["k5"]["mass_removed"],
           table=table, dose=dose,
           window=dict(cls=wcls, r1=bool(r1), r2=r2, r3=bool(r3),
                       killA=bool(killA), killB=bool(killB),
                       restA=bool(restA), restB=bool(restB),
                       partialA=bool(partialA),
                       superA=_super(tA), superB=_super(tB), s1=s1, s2=s2),
           pooled=pooled, pooled_window=pooled_window,
           b18_cert_pass=True,
           band_ok=band_ok,
           sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l124/results_l124.json", "w"), indent=1)
print("results_l124.json written")''',
    '''out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           new_band_ok=ar["new_band_ok"],
           scr_fresh_gains=ar["scr_fresh_gains"],
           g_cutk5=float(z125["g_cutk5"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cut58", "k58"))},
           mass_scr={a: S125["scr"][a]["mass_removed"] for a in SCR_ARMS},
           extra_mass_scr={a: S125["scr"][a]["extra_mass"]
                           for a in SCR_ARMS},
           mass_cutk5=SM["ladder"]["k5"]["mass_removed"],
           table=table, dose=dose,
           scramble=dict(cls=wcls, sc1=bool(sc1), scr0_super=bool(scr0_super),
                         any_restore=bool(any_restore), scr_read=scr_read,
                         s1=s1, s2=s2),
           pooled=pooled, pooled_window=pooled_window,
           b19_cert_pass=True,
           band_ok=band_ok,
           sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l125/results_l125.json", "w"), indent=1)
print("results_l125.json written")''', count=1)

open("l125_verdict.py", "w").write(SRC)

# residual scan + compile
bad = []
s = open("l125_verdict.py").read()
for tok in ("cutwA", "cutwB", "S123", "b18_cert", "r1=", "tA,", "partialA"):
    if tok in s:
        bad.append(("l125_verdict.py", "stale token " + tok))
if n_err or bad:
    print("BUILD FAIL:", n_err, bad)
    sys.exit(1)
py_compile.compile("l125_verdict.py", doraise=True)
print("BUILD OK: l125_verdict.py compiled; scans clean")
