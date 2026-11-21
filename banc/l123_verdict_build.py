"""Build l123_verdict.py from l122_verdict.py via exact-string transforms.

(1) docstring splice, (2) batches (+B18, B17/B16 context), (3) NEW_ARMS +
LADDER (wA/wB inserted), (4) loads (+z123, +r122, ar->l123, +S123), (5) p0
(drop ng39 boolean, +c0a122), (6) P4/table/dose reads z122->z123 B17->B18,
(7) Part 4 REPLACED by opener-splice: B17-cert FIRST, then W1-W4 + S1/S2 +
R4 pooled n=48, (8) out dict window keys, (9) results path + residual scan
+ py_compile. Duty machinery (S_of/s_arrays/duty_seeds/side_k/wilson) is
untouched by every rep (byte-identical inheritance).
"""
import py_compile
import re
import sys

V = open("l122_verdict.py").read()
n_err = 0


def vrep(old, new, count=None):
    global V, n_err
    c = V.count(old)
    if c == 0 or (count is not None and c != count):
        print(f"V PATTERN MISMATCH ({c} != {count}): {old[:70]!r}")
        n_err += 1
        return
    V = V.replace(old, new)
    print(f"v ok x{c}: {old[:48]!r}")


# 1. docstring splice
NEW_DOC = '''"""L123 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B17-cert of this machinery on raw_l122 vs results_l122.json BEFORE any
window read, then the registered WINDOW reads on FRESH B18 (kill criterion
VERBATIM): W1-W4 XOR/both-restore/both-kill/mixed classification of the
ng[19:29] halves cutwA/cutwB (RESTORE bar meanR>=.45 & kR>=12, SUPER-RAISE
>=.60), S1 cutk5 6th-batch replication, S2 endpoint replication (ng19 kill
+ ng29 super-raise, 3rd batch each), R4 pooled batch-union B16+B17+B18 n=48
full-precision Wilson (L90 form); per-side duty table 5 pairs x 10 arms;
L-axis + Sr_R watch; sanity cells. PREREG l123/PREREG.md."""'''
assert V.startswith('"""L122 verdict:') and V.count('"""L122 verdict:') == 1, \
    "verdict docstring opener drift"
_dend = V.index('"""', 3) + 3
V = NEW_DOC + V[_dend:]
print("v ok x1: verdict docstring spliced")

# 2. batches
vrep('''B17 = list(range(2101, 2117))
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)''',
     '''B18 = list(range(2201, 2217))       # FRESH (l123)
B17 = list(range(2101, 2117))  # context batch (l122, cert + pooled)
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)''')

# 3. arms + ladder
vrep('''NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutng39"]''',
     '''NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutwA", "cutwB"]''')
vrep('''LADDER = [("0", "full"), ("19", "cutng19"), ("29", "cutng29"),
          ("39", "cutng39"), ("58", "cut58"), ("k5", "cutk5")]''',
     '''LADDER = [("0", "full"), ("19", "cutng19"), ("wA", "cutwA"),
          ("wB", "cutwB"), ("29", "cutng29"), ("58", "cut58"),
          ("k5", "cutk5")]''')

# 4. loads
vrep('z122 = np.load("l122/raw_l122.npz")',
     '''z122 = np.load("l122/raw_l122.npz")
z123 = np.load("l123/raw_l123.npz")''')
vrep('''ar = json.load(open("l122/anchors_run.json"))
r121 = json.load(open("l121/results_l121.json"))
SM = json.load(open("l121/static.json"))''',
     '''ar = json.load(open("l123/anchors_run.json"))
r121 = json.load(open("l121/results_l121.json"))
r122 = json.load(open("l122/results_l122.json"))
SM = json.load(open("l121/static.json"))
S123 = json.load(open("l123/static.json"))''')

# 5. p0 dict
vrep('''          g_cutng39_stored_exact=ar["g_cutng39_stored_exact"],
''', '')
vrep('''          c0a121_pass=ar["c0a121_pass"], c0a121_max=ar["c0a121_max"],''',
     '''          c0a121_pass=ar["c0a121_pass"], c0a121_max=ar["c0a121_max"],
          c0a122_pass=ar["c0a122_pass"], c0a122_max=ar["c0a122_max"],''')
vrep('''p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]
                  and p0["g_cutng39_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])''',
     '''p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])''')
vrep('''print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (4 arms vs raw_l121) + 7 stored gains:",''',
     '''print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (3 arms vs raw_l121) + C0A-122 "
      "(3 arms vs raw_l122) + 6 stored gains:",''')
vrep('''print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutng19", "cutng29", "cutng39")},''',
     '''print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutwA", "cutwB")},''')

# 6. fresh reads z122 -> z123, B17 -> B18
vrep('[float(z122[f"af_{a}_{s}"]) for s in B17]',
     '[float(z123[f"af_{a}_{s}"]) for s in B18]', count=1)
vrep('all(0.01 < float(z122[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B17)',
     'all(0.01 < float(z123[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B18)',
     count=1)
vrep('t = side_k(z122, a, B17, pk)', 't = side_k(z123, a, B18, pk)', count=1)
vrep('_, Rfull = duty_seeds(z122, "full", B17, "Ti")',
     '_, Rfull = duty_seeds(z123, "full", B18, "Ti")', count=1)
vrep('_, Rd = duty_seeds(z122, a, B17, "Ti")',
     '_, Rd = duty_seeds(z123, a, B18, "Ti")', count=1)
vrep('float(z122["g_cutk5"])', 'float(z123["g_cutk5"])', count=2)
vrep('print("---- B17 per-side duty table ----")',
     'print("---- B18 per-side duty table ----")', count=1)
vrep('print("full-arm B17 band check (disclosure only):", band_ok)',
     'print("full-arm B18 band check (disclosure only):", band_ok)', count=1)

# 7. context: add l122 B17
vrep('''dose["l120_stored_b15_context"] = {
    "k5_Ti_meanR": r120["dose"]["Ti"]["meanR"]["5"],
    "k5_Ti_kR": r120["dose"]["Ti"]["kR"]["5"],
    "k5_kill": r120["k4"]["k5_kill"]}''',
     '''dose["l120_stored_b15_context"] = {
    "k5_Ti_meanR": r120["dose"]["Ti"]["meanR"]["5"],
    "k5_Ti_kR": r120["dose"]["Ti"]["kR"]["5"],
    "k5_kill": r120["k4"]["k5_kill"]}
dose["l122_stored_b17_context"] = {
    "Ti_meanR": r122["dose"]["Ti"]["meanR"],
    "Ti_kR": r122["dose"]["Ti"]["kR"],
    "kill": r122["dose"]["Ti"]["kill"]}''')
vrep('''print("l117 B12 / l119 B14 / l120 B15 / l121 B16 cross-batch context:",''',
     '''print("l117 B12 / l119 B14 / l120 B15 / l121 B16 / l122 B17 context:",''')

# 8. Part 4 REPLACED (opener-to-marker splice)
M4_START = "# ---- Part 4: REBASE reads R1/R2/R3 + B16-cert + R4 pooled union ----"
M4_END = "# Sr watch curve"
assert V.count(M4_START) == 1 and V.count(M4_END) == 1, "part4 markers"
NEW_P4 = '''# ---- Part 4: B17-cert FIRST, then W1-W4 + S1/S2 + R4 pooled n=48 ----
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
      f"(all {len(r122['table']['Ti'])} arms)")


# RESTORE (PREREG): meanR >= .45 AND kR >= 12 (absolute; full sat
# .469-.505 across B10-B17). SUPER-RAISE label: meanR >= .60 AND kR >= 12.
def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


tA, tB = table["Ti"]["cutwA"], table["Ti"]["cutwB"]
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
print(f"W classification: {wcls}")
# S1: cutk5 6th batch; S2: endpoints 3rd batch (registered)
s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B18 — 6th consecutive batch (B12/B14/B15/B16/B17/B18)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B18 — DISCLOSED (L118 lottery class)"))
s2 = dict(ng19_kill=bool(killmap["19"]),
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (3rd batch each)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))
print(f"S1: {s1['cls']}")
print(f"S2: {s2['cls']}")
# R4: pooled batch-union B16+B17+B18 n=48, FULL-PRECISION Wilson (L90)
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
          f"p_hat {k/48:.3f} Wilson [{lb:.4f}, {ub:.4f}]")

'''
_i0, _i1 = V.index(M4_START), V.index(M4_END)
V = V[:_i0] + NEW_P4 + V[_i1:]
print("v ok x1: Part 4 spliced")

# 9. out dict
vrep('''           rebase=dict(r1=r1, r2=r2, r3=r3, ng_kills=ng_kills,
                       k58_kill=bool(k58_kill), k5_kill=bool(k5_kill)),
           pooled=pooled, b16_cert_pass=True,''',
     '''           window=dict(cls=wcls, killA=bool(killA), killB=bool(killB),
                       restA=bool(restA), restB=bool(restB),
                       superA=_super(tA), superB=_super(tB), s1=s1, s2=s2),
           pooled=pooled, b17_cert_pass=True,''')
vrep('''           fresh_gains={a: ar["g_" + a]
                        for a in ("cutng19", "cutng29", "cutng39")},''',
     '''           fresh_gains={a: ar["g_" + a] for a in ("cutwA", "cutwB")},''')
vrep('''           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cutng39", "k39"), ("cut58", "k58"))},''',
     '''           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cut58", "k58"))},
           mass_window={a: S123["window_" + a[-2:]]["mass_removed"]
                        for a in ("cutwA", "cutwB")},
           extra_mass={a: S123["window_" + a[-2:]]["extra_mass"]
                       for a in ("cutwA", "cutwB")},''')
vrep('json.dump(out, open("l122/results_l122.json", "w"), indent=1)',
     'json.dump(out, open("l123/results_l123.json", "w"), indent=1)')
vrep('print("results_l122.json written")',
     'print("results_l123.json written")')

open("l123_verdict.py", "w").write(V)

# ---------------- residual scan + direction check ----------------
bad = []
s = open("l123_verdict.py").read()
for tok in ("cutng39", "r1 =", "r2 =", "REBASE reads", "B16-cert"):
    if tok in s:
        bad.append(("l123_verdict.py", "stale token " + tok))
OK_IN = {"l113/raw_l113.npz", "l121/raw_l121.npz", "l122/raw_l122.npz",
         "l123/raw_l123.npz", "l113/results_l113.json",
         "l117/results_l117.json", "l119/results_l119.json",
         "l120/results_l120.json", "l121/results_l121.json",
         "l122/results_l122.json", "l123/anchors_run.json",
         "l121/static.json", "l123/static.json"}
for m in re.finditer(r'"(l1\d+/[^"]+)"', s):
    p = m.group(1)
    if p.startswith("l123/"):
        continue
    if p not in OK_IN:
        bad.append(("l123_verdict.py", "unexpected l-path " + p))
if n_err or bad:
    print("VERDICT BUILD FAIL:", n_err, bad)
    sys.exit(1)
py_compile.compile("l123_verdict.py", doraise=True)
print("VERDICT BUILD OK: l123_verdict.py compiled; scans clean")
