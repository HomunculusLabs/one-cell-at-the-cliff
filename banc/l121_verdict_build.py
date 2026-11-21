"""Build l121_verdict.py from l120_verdict.py via exact-string transforms.

Duty machinery (S_of/s_arrays/duty_seeds/side_k/wilson) + C0B cert block
stay VERBATIM. Swapped: docstring, B15->B16, NEW_ARMS, LADDER (ng dose
curve 0/19/29/39/58 + cutk5 replication point), data loads (z121/ar/SM,
+ r120 context), P0 (c0a120, no cutk3 stored), fresh-gain prints, Part 4
k4-classification -> P1 MASS/POOL/MIXED classification + P2 cutk5
replication read, out dict, output path. Drift guard on every rep.
"""
import py_compile
import sys

SRC = open("l120_verdict.py").read()
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


# 1. docstring
rep('''"""L120 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
reads: (P1) Ti_R curve k in {0,3,4a,4b,5,19} FRESH on B15 with the
L118/L119-registered kill criterion and the k4 disambiguation
classification (XOR-named / both-k4 / neither / batch-drift); (P1b) kill
mass bound; per-side duty table 5 pairs x 9 arms; L-axis secondary;
Sr_R watch; sanity cells. PREREG l120/PREREG.md."""''',
    '''"""L121 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
reads: (P1) Ti_R dose curve over the NON-glut ladder k in {0,19,29,39,58}
FRESH on B16 with the L118/L119/L120-registered kill criterion and the
MASS-FRACTION / POOL-COHERENCE / MIXED classification; (P2) cutk5 B16
replication read of the L120 XOR kill (4th batch or batch-drift
disclosed); per-side duty table 5 pairs x 9 arms; L-axis secondary;
Sr_R watch; sanity cells. PREREG l121/PREREG.md."""''')

# 2. seeds / arms / ladder
rep('B15 = list(range(1901, 1917))', 'B16 = list(range(2001, 2017))')
rep('NEW_ARMS = ["cutk3", "cutk4a", "cutk4b", "cutk5"]',
    'NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutng39"]')
rep('''LADDER = [("0", "full"), ("3", "cutk3"), ("4a", "cutk4a"), ("4b", "cutk4b"),
          ("5", "cutk5"), ("19", "cut19")]''',
    '''LADDER = [("0", "full"), ("19", "cutng19"), ("29", "cutng29"),
          ("39", "cutng39"), ("58", "cut58"), ("k5", "cutk5")]''')

# 3. data loads
rep('''z113 = np.load("l113/raw_l113.npz")
z120 = np.load("l120/raw_l120.npz")
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
r119 = json.load(open("l119/results_l119.json"))
ar = json.load(open("l120/anchors_run.json"))
SM = json.load(open("l120/static.json"))''',
    '''z113 = np.load("l113/raw_l113.npz")
z121 = np.load("l121/raw_l121.npz")
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
r119 = json.load(open("l119/results_l119.json"))
r120 = json.load(open("l120/results_l120.json"))
ar = json.load(open("l121/anchors_run.json"))
SM = json.load(open("l121/static.json"))''')

# 4. P0 block
rep('''p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
          g_cut58_stored_exact=ar["g_cut58_stored_exact"],
          g_cutk5_stored_exact=ar["g_cutk5_stored_exact"],
          g_cutk3_stored_exact=ar["g_cutk3_stored_exact"],
          c0a119_pass=ar["c0a119_pass"], c0a119_max=ar["c0a119_max"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["c0a119_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"] and p0["g_cutk3_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-119 "
      "(cutk3/cutk5 vs raw_l119) + 5 stored gains:",
      "PASS" if p0["pass"] else "FAIL",
      f"(max113 {p0['c0a_max']:.1e} max119 {p0['c0a119_max']:.1e})")''',
    '''p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
          g_cut58_stored_exact=ar["g_cut58_stored_exact"],
          g_cutk5_stored_exact=ar["g_cutk5_stored_exact"],
          c0a120_pass=ar["c0a120_pass"], c0a120_max=ar["c0a120_max"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + 4 stored gains:",
      "PASS" if p0["pass"] else "FAIL",
      f"(max113 {p0['c0a_max']:.1e} max120 {p0['c0a120_max']:.1e})")''')

# 5. fresh-gain print
rep('''print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutk4a", "cutk4b")},
      "cutk5", round(float(z120["g_cutk5"]), 6),
      "cutk3", round(float(z120["g_cutk3"]), 6), "(stored, asserted)",
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})''',
    '''print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutng19", "cutng29", "cutng39")},
      "cutk5", round(float(z121["g_cutk5"]), 6), "(stored, asserted)",
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})''')

# 6. P4 + Part 2 z/B swaps
rep('for s in B15])', 'for s in B16])', count=1)
rep('float(z120[f"af_{a}_{s}"])', 'float(z121[f"af_{a}_{s}"])')
rep('        t = side_k(z120, a, B15, pk)', '        t = side_k(z121, a, B16, pk)')

# 7. Part 3 z/B swaps + l120 context
rep('''m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z120, "full", B15, "Ti")''',
    '''m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z121, "full", B16, "Ti")''')
rep('    _, Rd = duty_seeds(z120, a, B15, "Ti")',
    '    _, Rd = duty_seeds(z121, a, B16, "Ti")')
rep('''print("l117 B12 / l119 B14 cross-batch context (no gate):",
      dose["l117_stored_b12_context"], dose["l119_stored_b14_context"])''',
    '''dose["l120_stored_b15_context"] = {
    "k5_Ti_meanR": r120["dose"]["Ti"]["meanR"]["5"],
    "k5_Ti_kR": r120["dose"]["Ti"]["kR"]["5"],
    "k5_kill": r120["k4"]["k5_kill"]}
print("l117 B12 / l119 B14 / l120 B15 cross-batch context (no gate):",
      dose["l117_stored_b12_context"], dose["l119_stored_b14_context"],
      dose["l120_stored_b15_context"])''')

# 8. Part 4 wholesale: k4 classification -> P1 classification + P2 replication
rep('''# ---- Part 4 (P1): k4 disambiguation classification (PREREG forms) ----
k4a_k, k4b_k, k5_k = killmap["4a"], killmap["4b"], killmap["5"]
named_cell = None
if not k5_k:
    k_star = None
    k4_cls = ("BATCH-DRIFT: cutk5 itself does not kill on B15 — k4 reads "
              "reported, k* claim downgraded to same-batch-only (L118 "
              "lottery class; l117 B12 + l119 B14 kills were their batches)")
elif k4a_k != k4b_k:
    named_cell = 204 if k4a_k else 32014
    k_star = 4
    k4_cls = (f"XOR — CELL {named_cell} COMPLETES THE KILL: cutk4"
              f"{'a' if k4a_k else 'b'} (drop incl {named_cell}) kills at "
              f".034{'7' if k4a_k else '6'} while its mass-matched partner "
              "does not; minimal killing set = 4 cells; PLACEMENT-PURE by "
              "construction (unrounded mass delta 9.2e-05)")
elif k4a_k and k4b_k:
    k_star = 4
    k4_cls = ("BOTH K4 ARMS KILL: k*=4, window tightens k3->k4; placement "
              "is 2-cell-redundant at matched mass (either 204 or 32014 "
              "completes the set)")
else:
    k_star = 5
    k4_cls = ("NEITHER K4 ARM KILLS (cutk5 does): the kill needs the FULL "
              "heaviest-5 SET — a 5-cell coherent unit; k4 arms at ~.0347 "
              "sit in the gap [no-kill .0268/.0346/-.0347, kill .0425]")
print(f"P1 k4 classification: {k4_cls}")
# P1b mass bound
if not k5_k:
    mass_bound = "cutk5 no-kill this batch — bound not carried"
elif k4a_k or k4b_k:
    mass_bound = ("kill reached at ~.0347 (a k4 arm) — bound tightens from "
                  "[.0268,.0425] to [.0268,.0347]")
    if k4a_k != k4b_k:
        mass_bound += ("; XOR partner survives at matched mass — completing "
                       "cell NAMED, mass cannot explain the difference")
else:
    mass_bound = "no k4 kill; bound stays [.0347 no-kill, .0425 kill]"
print("P1b", mass_bound)''',
    '''# ---- Part 4 (P1): MASS vs POOL classification (PREREG forms) ----
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
p2_cls = ("cutk5 KILLS on B16 — 4th batch replicate (B12/B14/B15/B16) of "
          "the L117 step / L119 placement / L120 XOR" if k5_kill else
          "cutk5 does NOT kill on B16 — batch-drift DISCLOSED (L118 "
          "lottery class); L120's B15 evidence stands, never a fail")
print(f"P2 cutk5 replication: {p2_cls}")''')

# 9. out dict
rep('''           fresh_gains={a: ar["g_" + a] for a in ("cutk4a", "cutk4b")},
           g_cutk5=float(z120["g_cutk5"]), g_cutk3=float(z120["g_cutk3"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ladder"][k]["mass_removed"]
                 for a, k in (("cutk3", "k3"), ("cutk4a", "k4a"),
                              ("cutk4b", "k4b"), ("cutk5", "k5"))},
           mass_match=SM["mass_match"],
           table=table, dose=dose, k4=dict(cls=k4_cls, k4a_kill=k4a_k,
                                           k4b_kill=k4b_k, k5_kill=k5_k,
                                           named_cell=named_cell,
                                           k_star=k_star),
           mass_bound=mass_bound, band_ok=band_ok,''',
    '''           fresh_gains={a: ar["g_" + a]
                        for a in ("cutng19", "cutng29", "cutng39")},
           g_cutk5=float(z121["g_cutk5"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cutng39", "k39"), ("cut58", "k58"))},
           mass_cutk5=SM["ladder"]["k5"]["mass_removed"],
           table=table, dose=dose,
           classification=dict(cls=p1_cls, ng_kills=ng_kills,
                               full_like=full_like, k58_kill=k58_kill),
           cutk5_replication=dict(cls=p2_cls, k5_kill=k5_kill),
           band_ok=band_ok,''')

# 10. output path
rep('json.dump(out, open("l120/results_l120.json", "w"), indent=1)',
    'json.dump(out, open("l121/results_l121.json", "w"), indent=1)')
rep('print("results_l120.json written")', 'print("results_l121.json written")')

# 11. sweeps + residual scan
if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
for old, new in (("B15", "B16"), ("z120", "z121")):
    if SRC.count(old):
        SRC = SRC.replace(old, new)
        print(f"sweep ok: {old!r} -> {new!r}")
bad = ["cutk3", "cutk4a", "cutk4b", "c0a119", "mass_bound", "k4_cls",
       "B15", "z120", "af_finalk3"]
left = {t: SRC.count(t) for t in bad if SRC.count(t)}
print("residual scan:", left if left else "CLEAN")
if left:
    sys.exit(1)
open("l121_verdict.py", "w").write(SRC)
py_compile.compile("l121_verdict.py", doraise=True)
print("l121_verdict.py written + py_compile OK, lines:", SRC.count("\\n") + 1)
