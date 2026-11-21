#!/usr/bin/env python3
"""Referee R4: checks on the items rounds 1-3 left open, plus my own fresh
probes. Stored artifacts only, no rollouts."""
import json, math, re, csv
ROOT = "/home/t3rpz/critters/peabrain-lab"

def wilson(k, n, z=1.959963984540054):
    if n == 0: return (float("nan"),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)

def newcombe(k1, n1, k2, n2):
    """Newcombe hybrid-score interval for p1 - p2."""
    l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    d = k1 / n1 - k2 / n2
    lo = d - math.sqrt((k1 / n1 - l1) ** 2 + (u2 - k2 / n2) ** 2)
    hi = d + math.sqrt((u1 - k1 / n1) ** 2 + (k2 / n2 - l2) ** 2)
    return d, lo, hi

print("#" * 72)
print("# A. THE 1% WEIGHT-JITTER ENSEMBLE, PER SET (round-1 major 5, round-2 N5)")
print("#" * 72)
J = json.load(open(f"{ROOT}/banc/l139/results_l139.json"))
sets = J["sets"]
arms = ["full", "cutwA", "cutng25", "cutng25p", "cutng29", "cutng23"]
print("source: banc/l139/results_l139.json:sets   (kR of 16 per arm per set)")
print()
print(f"{'set':>4} " + " ".join(f"{a:>10}" for a in arms) + "   carrier-vs-base   carrier-vs-twin")
for s in sorted(sets, key=int):
    row = sets[s]
    cells = []
    for a in arms:
        v = row.get(a)
        cells.append(f"{v['kR']:>2}/16 {v['cls'][:4]:<4}" if v else f"{'-':>10}")
    c = row["cutng25"]["kR"]; b = row["cutwA"]["kR"]; t = row["cutng25p"]["kR"]
    print(f"{s:>4} " + " ".join(f"{x:>10}" for x in cells) +
          f"   {c-b:+3d} seeds       {c-t:+3d} seeds")
print()
print("Registered-class summary the draft §2.10 gives:")
for a in ["cutng25", "cutng23", "cutng29", "cutwA", "cutng25p"]:
    su = J["sustain"][a]
    print(f"  {a:9s} {su['prior']:12s} -> {su['n']}/5 sustained  classes={su['classes']}")
print()
print("WHAT §2.10 DOES NOT SAY (my reading):")
for s in sorted(sets, key=int):
    row = sets[s]
    b, t, c = row["cutwA"], row["cutng25p"], row["cutng25"]
    if b["cls"] == "SUPER" or t["cls"] == "SUPER" or c["kR"] - t["kR"] <= 3:
        print(f"  set {s}: base {b['kR']}/16 {b['cls']}, twin {t['kR']}/16 {t['cls']}, "
              f"carrier {c['kR']}/16 {c['cls']}  <-- title contrast degraded or absent")
print(f"  base kR across sets: {[sets[s]['cutwA']['kR'] for s in sorted(sets,key=int)]}"
      f"  (draft §2.10 quotes only 'wA PARTIAL 0/5')")
print(f"  twin kR across sets: {[sets[s]['cutng25p']['kR'] for s in sorted(sets,key=int)]}")
print(f"  carrier kR across sets: {[sets[s]['cutng25']['kR'] for s in sorted(sets,key=int)]}")

print()
print("#" * 72)
print("# B. TABLE 4: is the continuous ladder really monotone? (fresh major)")
print("#" * 72)
# Table 4 continuous column as printed in the draft
t4 = [("b65", 513, 513), ("full", 0, 513), ("cutk5", 0, 226), ("cutng19", 0, 178),
      ("cutng23", 0, 82), ("cutwA", 0, 258), ("cutng25p", 0, 66),
      ("cutng25", 132, 210), ("cutng29", 108, 194), ("cut58", 186, 258),
      ("cutscr0", 9, 50)]
print(f"{'arm':10s} {'k/n':>9} {'prop':>6} {'Wilson 95%':>18}   draft Table 4 interval")
draftiv = {"b65": "[.993,1.000]", "full": "[.000,.007]", "cutk5": "[.000,.017]",
           "cutng19": "[.000,.021]", "cutng23": "[.000,.045]", "cutwA": "[.000,.015]",
           "cutng25p": "[.000,.055]", "cutng25": "[.561,.691]", "cutng29": "[.486,.625]",
           "cut58": "[.663,.772]", "cutscr0": "[.098,.308]"}
for a, k, n in t4:
    lo, hi = wilson(k, n)
    print(f"{a:10s} {k:>4}/{n:<4} {k/n:>6.3f}   [{lo:.3f},{hi:.3f}]   {draftiv[a]}")
print()
print("the draft claims the window (non-monotonicity) is CHOPPED-SPECIFIC.")
print("but in the CONTINUOUS column the ladder is also non-monotone:")
d, lo, hi = newcombe(132, 210, 108, 194)
print(f"  k=25 (132/210=.629) vs k=29 (108/194=.557): difference {d:+.3f} [{lo:+.3f},{hi:+.3f}]"
      "  -> NOT resolved, so non-monotone but not demonstrably so")
d, lo, hi = newcombe(186, 258, 108, 194)
print(f"  k=58 (186/258=.721) vs k=29 (108/194=.557): difference {d:+.3f} [{lo:+.3f},{hi:+.3f}]"
      "  -> resolved rise")
d, lo, hi = newcombe(513, 513, 0, 513)
print(f"  b65 (513/513) vs closure (0/513):          difference {d:+.3f} [{lo:+.3f},{hi:+.3f}]"
      "  -> the biggest effect in the paper is ADDING the projectors")

print()
print("#" * 72)
print("# C. HOW MANY ACTIVE CELLS MOVE THE READOUT AT ALL? (second-opinion follow-up)")
print("#" * 72)
L = json.load(open(f"{ROOT}/banc/l175/results_l175.json"))
base = L["base"]; bk, bm = base["kR"], base["meanR"]
act = [w for w in L["window"] if w["active"]]
print(f"base = {bk}/16, meanR {bm:.3f}. The 14 active window cells, by paired dR_vs_wA:")
for w in sorted(act, key=lambda z: z["dR_vs_wA"]):
    print(f"  {w['arm']:6s} rank{w['rank']:3d} {w['cell_type']:9s} sign{int(w['eff_sign']):+d} "
          f"drive x{w['drive_ratio_to_carrier']:.2f}  kR={w['kR']:2d}/16 meanR={w['meanR']:.3f}  "
          f"dR_vs_base={w['dR_vs_wA']:+.3f}  up/dn={w['n_up_vs_wA']}/{w['n_dn_vs_wA']}")
up = [w for w in act if w["dR_vs_wA"] > 0.05]
dn = [w for w in act if w["dR_vs_wA"] < -0.05]
print(f"\n  active cells moving duty UP   by >.05: {len(up)}  {[w['arm'] for w in up]}")
print(f"  active cells moving duty DOWN by >.05: {len(dn)}  {[w['arm'] for w in dn]}")
print(f"  the draft §2.1 mentions only ranks 33 and 34 as opposite-direction movers")
# same for the silent set, as a null
sil = [w for w in L["window"] if not w["active"]]
supn = [w for w in sil if w["dR_vs_wA"] > 0.05]
sdnn = [w for w in sil if w["dR_vs_wA"] < -0.05]
print(f"  SILENT cells moving UP by >.05: {len(supn)}/{len(sil)}  {[w['arm'] for w in supn]}")
print(f"  SILENT cells moving DN by >.05: {len(sdnn)}/{len(sil)}  {[w['arm'] for w in sdnn]}")

print()
print("#" * 72)
print("# D. THE 'SILENT' LABEL (fresh major)")
print("#" * 72)
print("§2.1: 'Removing any one of the 20 silent cells, which deliver essentially nothing'")
print("§3.4: 'A cell counts as active when x > 0.05' -- so 'silent' here means x <= 0.05,")
print("      which is the OPERATING-POINT bar, not a statement about delivered drive.")
nz = sorted([w for w in sil if w["x_mean"] > 0.005], key=lambda z: -z["x_mean"])
print(f"\n{len(nz)} of the 20 'silent' cells fire well above numerical zero:")
for w in nz:
    print(f"  {w['arm']:6s} rank{w['rank']:3d} x̄={w['x_mean']:.4f} "
          f"({w['x_mean']/L['window'][0]['x_mean']*100:4.1f}% of carrier's rate) "
          f"drive x{w['drive_ratio_to_carrier']:.3f}  kR={w['kR']:2d}/16 meanR={w['meanR']:.3f}")
print(f"\nthe two 'edge-of-band' arms the draft singles out (ranks 27 and 40) are the TOP TWO")
print("of this subgroup by rate -- i.e. the arms closest to the SUPER band inside the")
print("'silent-cell null' are the least silent members of it.")
tz = [w for w in sil if w["x_mean"] <= 0.005]
print(f"\n  12 genuinely near-zero cells: kR {min(w['kR'] for w in tz)}-{max(w['kR'] for w in tz)}, "
      f"meanR {min(w['meanR'] for w in tz):.3f}-{max(w['meanR'] for w in tz):.3f}")
print(f"  8 sub-threshold-active cells: kR {min(w['kR'] for w in nz)}-{max(w['kR'] for w in nz)}, "
      f"meanR {min(w['meanR'] for w in nz):.3f}-{max(w['meanR'] for w in nz):.3f}")
print("  -> the quoted null width (2-11 seeds, .340-.605) is set at its TOP by the")
print("     sub-threshold-active members, not by inert deletions.")

print()
print("#" * 72)
print("# E. EDGE-CUT 60% AND THE 'DOUBLE DISSOCIATION IN A LIMITED SENSE'")
print("#" * 72)
print("§2.4 Table 3b point estimates, as printed in the draft:")
print("  base      5/16 .402      --")
print("  sc25     15/16 .772   +.370 [+.257,+.483]   1.4Hz 8/16 .488")
print("  E-edge   12/16 .624   +.223 [+.082,+.364]   1.4Hz 0/16 .000")
print("  E-sham    5/16 .421   +.020 [-.094,+.133]   1.4Hz 0/16 .002")
print()
print("the draft's '60%' = .223/.370 point ratio, 'and that ratio has no interval'.")
print("a referee CAN put an interval on it from the printed CIs, pessimistically:")
print(f"  ratio of point estimates           = {0.223/0.370:.3f}")
print(f"  lo/hi bound from the two CIs       = {0.082/0.483:.3f} .. {0.364/0.257:.3f}"
      "   (i.e. 17% to >100%)")
print("  -> '60%' is one draw inside a range that spans 'a sixth of it' to 'all of it'.")
print("     The draft says the ratio has no interval but then uses 60% twice as a")
print("     quantitative mechanism statement ('about 60% of the carrier's shift').")
print()
print("the dissociation's second leg (1.4 Hz appears only with the whole carrier gone):")
print("  E-edge 0/16 vs sc25 8/16 on shared seeds -> that leg is clean on this batch.")
print("  but both legs are ONE batch of 16 at RE-BISECTED gains only (no fixed-gain form),")
print("  and the edge arm's gain is -0.358%, which by §2.2's own slope (-.0228/+0.1%)")
print(f"  predicts a duty rise of {0.358/0.1*0.0228:+.3f} from gain ALONE -- against an")
print(f"  observed +.223. So gain could account for {0.358/0.1*0.0228/0.223*100:.0f}% of the edge-cut effect.")
print("  The draft states this risk in prose but does not do the subtraction.")
