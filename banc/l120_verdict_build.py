"""Build l120_verdict.py from l119_verdict.py via exact-string transforms.

(1) docstring, (2) seeds B14->B15 + range, (3) NEW_ARMS/LADDER, (4) fresh
source z119->z120 + anchors/static paths l120 (+ r119 context load),
(5) P0 gains incl cutk3 stored + c0a119, (6) fresh-gain print keys,
(7) wholesale Part 3/4 replacement (k4 disambiguation classification +
mass bound), (8) out dict + results path. Residual scan at the end.
"""
import py_compile
import sys

SRC = open("l119_verdict.py").read()
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
rep('''"""L119 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
reads: (P1) Ti_R dose curve k in {0,1,2,3,5,19} FRESH on B14 with the
L118-registered kill criterion and the k* step classification; (P2) cutr5
(random 5-of-19 glut, mass .0231, zero heaviest-5 overlap) classification
IDENTITY vs PLACEMENT vs MIXED; per-side duty table 5 pairs x 10 arms;
L-axis secondary; Sr_R watch; sanity cells. PREREG l119/PREREG.md."""''',
    '''"""L120 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
reads: (P1) Ti_R curve k in {0,3,4a,4b,5,19} FRESH on B15 with the
L118/L119-registered kill criterion and the k4 disambiguation
classification (XOR-named / both-k4 / neither / batch-drift); (P1b) kill
mass bound; per-side duty table 5 pairs x 9 arms; L-axis secondary;
Sr_R watch; sanity cells. PREREG l120/PREREG.md."""''')

# 2. seeds + batch
rep("B14 = list(range(1801, 1817))", "B15 = list(range(1901, 1917))")
rep("B14", "B15")

# 3. arms / ladder
rep('''NEW_ARMS = ["cutk1", "cutk2", "cutk3", "cutk5", "cutr5"]''',
    '''NEW_ARMS = ["cutk3", "cutk4a", "cutk4b", "cutk5"]''')
rep('''LADDER = [("0", "full"), ("1", "cutk1"), ("2", "cutk2"), ("3", "cutk3"),
          ("5", "cutk5"), ("19", "cut19")]''',
    '''LADDER = [("0", "full"), ("3", "cutk3"), ("4a", "cutk4a"), ("4b", "cutk4b"),
          ("5", "cutk5"), ("19", "cut19")]''')

# 4. fresh source + paths (+ r119 context)
rep('''z113 = np.load("l113/raw_l113.npz")
z119 = np.load("l119/raw_l119.npz")
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
ar = json.load(open("l119/anchors_run.json"))
SM = json.load(open("l119/static.json"))''',
    '''z113 = np.load("l113/raw_l113.npz")
z120 = np.load("l120/raw_l120.npz")
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
r119 = json.load(open("l119/results_l119.json"))
ar = json.load(open("l120/anchors_run.json"))
SM = json.load(open("l120/static.json"))''')
rep("z119", "z120")

# 5. P0 gains + c0a119
rep('''p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
          g_cut58_stored_exact=ar["g_cut58_stored_exact"],
          g_cutk5_stored_exact=ar["g_cutk5_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (stored arms, seeds 801/901) + l117 k5 gain:",
      "PASS" if p0["pass"] else "FAIL", f"(max {p0['c0a_max']:.1e})")''',
    '''p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
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
      f"(max113 {p0['c0a_max']:.1e} max119 {p0['c0a119_max']:.1e})")''')

# 6. fresh-gain print keys
rep('''print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutk1", "cutk2", "cutk3", "cutr5")},
      "cutk5", round(float(z120["g_cutk5"]), 6), "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})''',
    '''print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutk4a", "cutk4b")},
      "cutk5", round(float(z120["g_cutk5"]), 6),
      "cutk3", round(float(z120["g_cutk3"]), 6), "(stored, asserted)",
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})''')

# 7. wholesale Part 3 + Part 4 replacement
rep('''# ---- Part 3 (P1): Ti_R dose curve, kill criterion, k* step ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z120, "full", B15, "Ti")
dose = {"Ti": {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {},
               "kill": {}},
        "Sr": {"meanR": {}, "kR": {}}}
kill_ks = []
for kk, a in LADDER:
    t = table["Ti"][a]
    dose["Ti"]["meanR"][kk] = t["meanR"]
    dose["Ti"]["kR"][kk] = t["kR"]
    dose["Ti"]["meanL"][kk] = t["meanL"]
    dose["Ti"]["kL"][kk] = t["kL"]
    _, Rd = duty_seeds(z120, a, B15, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    dose["Ti"]["legs"][kk] = legs
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \\
        (legs["mean_paired_dR"] <= -.20)
    dose["Ti"]["kill"][kk] = bool(kill)
    if kk in ("1", "2", "3", "5") and kill:
        kill_ks.append(int(kk))
    print(f"Ti k={kk:>2s} ({a:6s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | paired dR "
          f"{legs['mean_paired_dR']:+.3f} n_down {legs['n_down']}/16 "
          f"-> {'KILL' if kill else 'no-kill'}")
dose["Ti"]["m0"] = m0
if kill_ks:
    k_star = min(kill_ks)
    if k_star == 1:
        shape = ("SINGLE-CELL (.0096 mass): the R-kill is an ultra-local "
                 "placement effect — one cell's removal flips the axis")
    else:
        shape = f"STEP AT k={k_star} ({ {'2': '.0185', '3': '.0268', '5': '.0425'}[str(k_star)] } mass)"
else:
    k_star = None
    shape = ("NO KILL at k<=5 on B15 — batch-drift disclosed (l117's k5 kill "
             "was B12); k5 point re-rolls (L118 lottery class), never "
             "rounded into a kill")
print(f"P1 k* = {k_star}: {shape}")
# cross-batch context (l117 stored B12, disclosure only)
dose["l117_stored_b12_context"] = {
    "Ti_meanR": r117["dose"]["Ti"]["meanR"],
    "Ti_kR": r117["dose"]["Ti"]["kR"]}
print("l117 B12 cross-batch context (no gate):",
      dose["l117_stored_b12_context"])

# ---- Part 4 (P2): cutr5 classification ----
mR5, kR5 = table["Ti"]["cutr5"]["meanR"], table["Ti"]["cutr5"]["kR"]
_, Rr5 = duty_seeds(z120, "cutr5", B15, "Ti")
legs5 = dict(mean_paired_dR=round(float((Rr5 - Rfull).mean()), 3),
             n_down=int(((Rr5 - Rfull) <= -.20).sum()),
             n_up=int(((Rr5 - Rfull) >= .20).sum()))
kill5 = (mR5 <= m0 - .10) and (kR5 <= 4) and (legs5["mean_paired_dR"] <= -.20)
surv5 = mR5 >= m0 - .10
if kill5:
    cls5 = ("IDENTITY: ANY 5-of-19 glut kills R at .0231 mass (below k3's "
            ".0268) — mass irrelevant, class identity at 5-cell granularity")
elif surv5:
    cls5 = ("PLACEMENT: random-5 (.0231, zero heaviest-5 overlap) does NOT "
            "kill — the HEAVIEST-5's specific cells carry the R-kill")
else:
    cls5 = ("MIXED (near-miss band, disclosed with legs; never rounded — "
            "L118 precedent)")
print(f"P2 cutr5: meanR {mR5:.3f} kR {kR5:2d}/16 paired dR "
      f"{legs5['mean_paired_dR']:+.3f} n_down {legs5['n_down']}/16 -> {cls5}")''',
    '''# ---- Part 3 (P1): Ti_R curve {0,3,4a,4b,5,19}, kill criterion ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z120, "full", B15, "Ti")
dose = {"Ti": {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {},
               "kill": {}},
        "Sr": {"meanR": {}, "kR": {}}}
killmap = {}
for kk, a in LADDER:
    t = table["Ti"][a]
    dose["Ti"]["meanR"][kk] = t["meanR"]
    dose["Ti"]["kR"][kk] = t["kR"]
    dose["Ti"]["meanL"][kk] = t["meanL"]
    dose["Ti"]["kL"][kk] = t["kL"]
    _, Rd = duty_seeds(z120, a, B15, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    dose["Ti"]["legs"][kk] = legs
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \\
        (legs["mean_paired_dR"] <= -.20)
    dose["Ti"]["kill"][kk] = bool(kill)
    killmap[kk] = bool(kill)
    print(f"Ti k={kk:>2s} ({a:6s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | paired dR "
          f"{legs['mean_paired_dR']:+.3f} n_down {legs['n_down']}/16 "
          f"-> {'KILL' if kill else 'no-kill'}")
dose["Ti"]["m0"] = m0
# cross-batch context (stored, disclosure only)
dose["l117_stored_b12_context"] = {
    "Ti_meanR": r117["dose"]["Ti"]["meanR"],
    "Ti_kR": r117["dose"]["Ti"]["kR"]}
dose["l119_stored_b14_context"] = {
    "Ti_meanR": r119["dose"]["Ti"]["meanR"],
    "Ti_kR": r119["dose"]["Ti"]["kR"]}
print("l117 B12 / l119 B14 cross-batch context (no gate):",
      dose["l117_stored_b12_context"], dose["l119_stored_b14_context"])

# ---- Part 4 (P1): k4 disambiguation classification (PREREG forms) ----
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
print("P1b", mass_bound)''')

# 8. out dict + results path
rep('''out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           new_band_ok=ar["new_band_ok"],
           fresh_gains={a: ar["g_" + a] for a in ("cutk1", "cutk2",
                                                  "cutk3", "cutr5")},
           g_cutk5=float(z120["g_cutk5"]), new_stairs=ar["new_stairs"],
           mass={a: SM["ladder"][f"k{k}"]["mass_removed"]
                 for a, k in (("cutk1", 1), ("cutk2", 2), ("cutk3", 3),
                              ("cutk5", 5))} | {"cutr5": SM["draw"]["cutr5"]["mass_removed"]},
           table=table, dose=dose, k_star=k_star, shape=shape,
           cutr5=dict(meanR=mR5, kR=kR5, legs=legs5, kill=bool(kill5),
                      survivor=bool(surv5), cls=cls5,
                      overlap_with_heaviest5=SM["draw"]["cutr5"]["overlap_with_heaviest5"]),
           band_ok=band_ok, sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l119/results_l119.json", "w"), indent=1)
print("results_l119.json written")''',
    '''out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           new_band_ok=ar["new_band_ok"],
           fresh_gains={a: ar["g_" + a] for a in ("cutk4a", "cutk4b")},
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
           mass_bound=mass_bound, band_ok=band_ok,
           sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l120/results_l120.json", "w"), indent=1)
print("results_l120.json written")''')

if n_err:
    print(f"ABORT: {n_err} pattern mismatches")
    sys.exit(1)
bad_tokens = ["cutk1", "cutk2", "cutr5", "1801"]
leftovers = {t: SRC.count(t) for t in bad_tokens if SRC.count(t)}
# 'B14' whitelist: the two INTENTIONAL historical labels referencing l119's
# own batch ("l119 B14 cross-batch context", lowercase keys not counted)
_b14 = SRC.count("B14") - SRC.count("l119 B14")
if _b14:
    leftovers["B14(non-historical)"] = _b14
print("residual scan:", leftovers if leftovers else "CLEAN")
if leftovers:
    sys.exit(1)
open("l120_verdict.py", "w").write(SRC)
py_compile.compile("l120_verdict.py", doraise=True)
print("l120_verdict.py written + py_compile OK")
