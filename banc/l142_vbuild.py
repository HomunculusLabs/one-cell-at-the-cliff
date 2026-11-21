"""Assemble l142_verdict.py from verbatim l135_verdict.py helper slices
(constants + S_of/s_arrays/duty_seeds/side_k/wilson — the certified
metric path) + L142 verdict logic. Drift-guarded by count asserts."""
import py_compile

v = open("l135_verdict.py").read().splitlines(keepends=True)
# lines 14-48 (1-indexed): imports/constants through Z; lines 81-131:
# S_of .. wilson (verbatim certified metric machinery)
head = "".join(v[14:48])
assert head.startswith("import json") and "Z = 1.959963984540054" in head
funcs = "".join(v[80:131])
assert funcs.startswith("def S_of") and "def wilson" in funcs
assert "def duty_seeds" in funcs and "def side_k" in funcs

NEW = '''
# ---- L142 verdict (PREREG l142/PREREG.md): B-cert FIRST, then B29 ----
B29 = list(range(3301, 3317))
B26 = list(range(3001, 3017))
B25 = list(range(2901, 2917))
B24 = list(range(2801, 2817))
B21 = list(range(2501, 2517))
ARMS142 = ["full", "b65", "cutwA", "cutng25",
           "eOutInt", "eOutMot", "eOutAll", "eIn", "eAll"]
LADDER142 = [("0", "full"), ("24", "cutwA"), ("eOutInt", "eOutInt"),
             ("eOutMot", "eOutMot"), ("eOutAll", "eOutAll"),
             ("eIn", "eIn"), ("eAll", "eAll"), ("25", "cutng25")]
z142 = np.load("l142/raw_l142.npz")
z135 = np.load("l135/raw_l135.npz")
z133 = np.load("l133/raw_l133.npz")
z131 = np.load("l131/raw_l131.npz")
z126 = np.load("l126/raw_l126.npz")
ar = json.load(open("l142/anchors_run.json"))
r135 = json.load(open("l135/results_l135.json"))
S142 = json.load(open("l142/static.json"))

# ---- B-cert BEFORE any B29 read (L85 rule): machinery on raw_l135 B26
# for {cutwA, cutng25} == results_l135.json Ti table EXACT ----
bcert_fail = []
for a in ("cutwA", "cutng25"):
    want = r135["table"]["Ti"][a]
    got = side_k(z135, a, B26, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append((a, kk, got[kk], want[kk]))
assert not bcert_fail, ("B-cert FAIL (no B29 read)", bcert_fail[:5])
print(f"B-cert vs results_l135.json Ti table {{cutwA,cutng25}}: PASS")

# ---- P0 anchors (gate booleans ONLY, L59 rule) ----
p0 = dict(c0a142_pass=ar["c0a142_pass"], c0a142_max=ar["c0a142_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"],
          a_eall_max=ar["a_eall_max"], g_eall_eq_g25=ar["g_eall_vs_g25"]["equal"])
p0["pass"] = bool(p0["c0a142_pass"] and p0["g_cutwA_stored_exact"]
                  and p0["g_cutng25_stored_exact"])
print("P0 anchors (C0A-142 + stored gains):", "PASS" if p0["pass"] else "FAIL",
      f"(max {p0['c0a142_max']:.1e}) | A-EALL max {p0['a_eall_max']:.1e} "
      f"gains-equal {p0['g_eall_eq_g25']}")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z142[f"af_{a}_{s}"]) for s in B29])), 6)
           for a in ARMS142}
af_range_ok = all(0.01 < float(z142[f"af_{a}_{s}"]) < 0.9
                  for a in ARMS142 for s in B29)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band),
          af_mean=af_mean, e_band_ok=ar["e_band_ok"],
          new_stairs=ar["new_stairs"])
print("P4", json.dumps({k: p4[k] for k in ("af_range_ok", "b65_band",
                                           "e_band_ok")}))

# ---- B29 per-side duty table (5 pairs x 9 arms) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS142:
        t = side_k(z142, a, B29, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B29 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS142:
        t = table[pk][a]
        print(f"{pk} {a:8s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Ti ladder classification (criteria VERBATIM L118-L131) ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z142, "full", B29, "Ti")
_, RwA = duty_seeds(z142, "cutwA", B29, "Ti")
dose = {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {}}


def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


cls, killmap = {}, {}
for kk, a in LADDER142:
    t = table["Ti"][a]
    _, Rd = duty_seeds(z142, a, B29, "Ti")
    legs = dict(
        mean_paired_dR_vs_full=round(float((Rd - Rfull).mean()), 3),
        n_down_vs_full=int(((Rd - Rfull) <= -.20).sum()),
        mean_paired_dR_vs_wA=round(float((Rd - RwA).mean()), 3),
        n_down_vs_wA=int(((Rd - RwA) <= -.20).sum()),
        n_up_vs_wA=int(((Rd - RwA) >= .20).sum()))
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \\
        (legs["mean_paired_dR_vs_full"] <= -.20)
    dose["meanR"][kk] = t["meanR"]; dose["kR"][kk] = t["kR"]
    dose["meanL"][kk] = t["meanL"]; dose["kL"][kk] = t["kL"]
    dose["legs"][kk] = legs
    killmap[kk] = bool(kill)
    cls[kk] = dict(arm=a, meanR=t["meanR"], kR=t["kR"], meanL=t["meanL"],
                   kL=t["kL"], kill=bool(kill), restore=_restore(t),
                   super=_super(t), partial=_partial(t), legs=legs)
    print(f"Ti {kk:>7s} ({a:8s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | dR_wA "
          f"{legs['mean_paired_dR_vs_wA']:+.3f} n_up_wA "
          f"{legs['n_up_vs_wA']:2d}/16 -> "
          f"{'KILL' if kill else 'no-kill'}"
          f"{'/RESTORE' if _restore(t) else ''}"
          f"{'/SUPER' if _super(t) else ''}"
          f"{'/PARTIAL' if _partial(t) else ''}")
dose["m0"] = m0

# ---- H-branch verdicts (registered BOTH directions) ----
c_ea, c_25 = cls["eAll"], cls["25"]
c_wa = cls["24"]
cls_of = lambda c: ("KILL" if c["kill"] else
                    "SUPER" if c["super"] else
                    "RESTORE" if c["restore"] else
                    "PARTIAL" if c["partial"] else "NONE")
h1 = dict(eall_class=cls_of(c_ea), ng25_class=cls_of(c_25),
          agree=bool(cls_of(c_ea) == cls_of(c_25)),
          note="H1 edge-carrier: eAll class == cutng25 class"
          if cls_of(c_ea) == cls_of(c_25) else
          "H1 counter-branch: eAll != cutng25 class — af-denominator/"
          "noise-index difference does work; disclose paired table")
h2a = dict(arm="eOutInt", fires=bool(cls["eOutInt"]["super"]
          or cls["eOutInt"]["restore"]),
           meanR=cls["eOutInt"]["meanR"], kR=cls["eOutInt"]["kR"],
           dR_vs_wA=cls["eOutInt"]["legs"]["mean_paired_dR_vs_wA"],
           mass=S142["arm_mass_frac_dn"]["eOutInt"],
           note="H2a intrinsic-sheet carrier at .0056 << .0544 band — "
           "identity beats mass at cell scale" if
           cls["eOutInt"]["super"] or cls["eOutInt"]["restore"] else
           "H2a no: intrinsic sheet alone does not carry the flip")
h2b = dict(arm="eOutMot", fires=bool(cls["eOutMot"]["super"]
          or cls["eOutMot"]["restore"]),
           meanR=cls["eOutMot"]["meanR"], kR=cls["eOutMot"]["kR"],
           dR_vs_wA=cls["eOutMot"]["legs"]["mean_paired_dR_vs_wA"],
           mass=S142["arm_mass_frac_dn"]["eOutMot"])
h2c = dict(arm="eOutAll", fires=bool(cls["eOutAll"]["super"]
          or cls["eOutAll"]["restore"]),
           int_fires=h2a["fires"], mot_fires=h2b["fires"],
           meanR=cls["eOutAll"]["meanR"], kR=cls["eOutAll"]["kR"],
           note="H2c distributed: union flips, parts do not" if
           (cls["eOutAll"]["super"] or cls["eOutAll"]["restore"])
           and not h2a["fires"] and not h2b["fires"] else "")
h3 = dict(arm="eIn", in_partial=bool(_partial(table["Ti"]["eIn"])),
          dR_vs_wA=cls["eIn"]["legs"]["mean_paired_dR_vs_wA"],
          meanR=cls["eIn"]["meanR"], kR=cls["eIn"]["kR"],
          note="H3 inert: eIn stays in the partial band" if
          _partial(table["Ti"]["eIn"]) else
          "H3 counter: eIn MOVES the readout — in-edges are not inert")
for nm, h in (("H1", h1), ("H2a", h2a), ("H2b", h2b), ("H2c", h2c),
              ("H3", h3)):
    print(nm, json.dumps(h))

# ---- pooled reads (L90 full-precision Wilson, unrounded) ----
def pooled(raws, a, batches, pk="Ti"):
    Ls, Rs = [], []
    for raw, b in zip(raws, batches):
        L, R = duty_seeds(raw, a, b, pk)
        Ls.append(L); Rs.append(R)
    R_ = np.concatenate(Rs); L_ = np.concatenate(Ls)
    kR, kL = int((R_ >= .5).sum()), int((L_ >= .5).sum())
    lbR, ubR = wilson(kR, len(R_)); lbL, ubL = wilson(kL, len(L_))
    return dict(kR=kR, n=len(R_), lbR=lbR, ubR=ubR, kL=kL, lbL=lbL, ubL=ubL,
                meanR=round(float(R_.mean()), 3),
                meanL=round(float(L_.mean()), 3))


pooled_ng25 = pooled([z131, z133, z135, z142], "cutng25",
                     [B24, B25, B26, B29])
pooled_wA = pooled([z126, z131, z133, z135, z142], "cutwA",
                   [B21, B24, B25, B26, B29])
print("pooled cutng25 B24+B25+B26+B29:", json.dumps(pooled_ng25))
print("pooled cutwA  B21+B24+B25+B26+B29:", json.dumps(pooled_wA))

# ---- disclosures + sanity ----
san = dict(
    full_class_batch_drawn=dict(meanR=m0, kR=table["Ti"]["full"]["kR"],
        note="class labels read vs m0/paired legs, not bare bands (L109)"),
    secondaries_not_rerun="cutk5/ng19/ng29 stand on stored pooled tables "
                          "(14/11/11 consecutive batches; spectator law)",
    no_renorm_arm="lineage build has no in-degree renorm (PREREG "
                  "disclosure; card text mis-carry)",
    e_arms_single_batch="eOutInt/eOutMot/eOutAll/eIn/eAll: B29 only, "
                        "disclosed")
tr_R = table["Tr"]; sr = table["Sr"]
print("watch: Tr_R wA", tr_R["cutwA"]["meanR"], "eOutInt",
      tr_R["eOutInt"]["meanR"], "| Sr_R wA", sr["cutwA"]["meanR"],
      "eOutInt", sr["eOutInt"]["meanR"])
print("sanity b65 Ti kL/kR", table["Ti"]["b65"]["kL"], table["Ti"]["b65"]["kR"])

out = dict(design="L142 edge-footprint ladder (PREREG l142/PREREG.md)",
           static=S142, anchors=ar, p0=p0, p4=p4, table=table, dose=dose,
           classes=cls, hypotheses=dict(H1=h1, H2a=h2a, H2b=h2b, H2c=h2c,
                                        H3=h3),
           pooled=dict(cutng25_B24_B25_B26_B29=pooled_ng25,
                       cutwA_B21_B24_B25_B26_B29=pooled_wA),
           disclosures=san)
json.dump(out, open("l142/results_l142.json", "w"), indent=1)
print("L142 VERDICT WRITTEN")
'''
out_src = ('"""L142 verdict: B-cert (raw_l135 B26, cutwA+cutng25) BEFORE any\n'
           'B29 read, then anchors/P4/B29 table/ladder/H-branches/pooled.\n'
           'Criteria VERBATIM L118-L131. PREREG l142/PREREG.md."""\n'
           + head + "\n" + funcs + "\n\n" + NEW)
assert "def side_k" in out_src and "def duty_seeds" in out_src \
    and "def wilson" in out_src, "certified metric fns missing in output"
open("l142_verdict.py", "w").write(out_src)
py_compile.compile("l142_verdict.py", doraise=True)
print("l142_verdict.py written", len(out_src), "chars | py_compile OK")
