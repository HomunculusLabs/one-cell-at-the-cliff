#!/usr/bin/env python3
"""Referee round-4 (opus) independent recompute. CPU, stored artifacts only.
Written from scratch by the referee; does not import any lab helper."""
import json, csv, math, hashlib, os, sys

ROOT = "/home/t3rpz/critters/peabrain-lab"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

# ---- my own Wilson score interval (no scipy) --------------------------------
def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - half) / d, (c + half) / d)

print("=" * 72)
print("REFEREE R4 RECOMPUTE — independent code")
print("=" * 72)

# =============================================================== TASK 1a
# carrier / twin / base pooled counts, recomputed from PER-SEED records,
# not from the lab's own 'pooled' summary block.
s = json.load(open(f"{ROOT}/banc/l172/stats.json"))
print("\n[1a] POOLED COUNTS recomputed from l172 per_seed records")
print("     source:", f"banc/l172/stats.json sha={sha(ROOT+'/banc/l172/stats.json')[:16]}")
per = s["per_seed"]
print("     per_seed container:", type(per).__name__,
      (list(per.keys())[:8] if isinstance(per, dict) else len(per)))

def recount(arm):
    """Recount structured seeds for an arm from its per-seed duty records,
    deduplicating by seed (the canonical unique-seed union rule, §2.14)."""
    rec = per[arm]
    seeds, duty = rec["seeds"], rec["dutyR"]
    assert len(seeds) == len(duty), f"{arm}: seed/duty length mismatch"
    best = dict(zip(seeds, duty))          # dedupe by seed id
    dups = len(seeds) - len(best)
    k = sum(1 for v in best.values() if v >= 0.50)
    n = len(best)
    mean = sum(best.values()) / n if n else float("nan")
    return k, n, mean, dups

for arm, label in [("cutng25", "carrier removed (k=25)"),
                   ("cutng25p", "k=24 + mass twin"),
                   ("cutwA", "base, 24-cell cut"),
                   ("silW", "carrier activity clamp on cut base"),
                   ("cutscr0", "heaviest carrier-free cohort"),
                   ("cut58", "k=58, largest cut"),
                   ("cutng29", "k=29")]:
    try:
        k, n, m, dups = recount(arm)
        lo, hi = wilson(k, n)
        c = s["pooled"].get(arm, {})
        agree = (k == c.get("kR") and n == c.get("n")
                 and abs(m - c.get("meanR", -9)) < 1e-6
                 and abs(lo - c.get("lbR", -9)) < 1e-6)
        print(f"     {'OK ' if agree else 'DIFF'} {arm:9s} {label:36s} "
              f"mine k/n={k}/{n} mean={m:.4f} Wilson[{lo:.4f},{hi:.4f}] dup-seeds={dups}")
        print(f"          stored: kR={c.get('kR')}/{c.get('n')} meanR={c.get('meanR'):.4f} "
              f"lbR={c.get('lbR'):.4f} ubR={c.get('ubR'):.4f}")
    except Exception as e:
        print(f"     {arm}: RECOUNT FAILED {type(e).__name__}: {e}")

# =============================================================== TASK 1b
# three rows of the L175 scan table, recomputed from raw per-seed dutyR.
print("\n[1b] L175 TABLE 1 ROWS recomputed from results_l175.json per-seed dutyR")
L = json.load(open(f"{ROOT}/banc/l175/results_l175.json"))
print("     source sha=", sha(ROOT + "/banc/l175/results_l175.json")[:16])
bands = L["bands"]
print("     registered bands:", json.dumps(bands))

index = {L["base"]["arm"]: L["base"]}
for w in L["window"]:
    index[w["arm"]] = w
for t in L["twins"].values():
    index[t["arm"]] = t

def classify(k, mean, b):
    if k >= b["super_kR_min"] and mean >= b["super_meanR_min"]:
        return "super"
    if k <= b["not_kR_max"] and mean <= b["not_meanR_max"]:
        return "not-super"
    return "intermediate"

CHECK = ["cutwA", "sc25", "sc26", "sc27", "sc40", "dmA", "dmC", "sc47"]
for arm in CHECK:
    a = index[arm]
    duty = a["dutyR"]
    k = sum(1 for d in duty if d >= 0.50)
    mean = sum(duty) / len(duty)
    lo, hi = wilson(k, len(duty))
    tag = "OK " if (k == a["kR"] and abs(mean - a["meanR"]) < 5e-4) else "MISMATCH"
    print(f"     {tag} {arm:7s} mine k={k:2d}/{len(duty)} mean={mean:.4f} "
          f"cls={classify(k,mean,bands):12s} | stored kR={a['kR']} meanR={a['meanR']} "
          f"cls={a.get('cls')} | Wilson[{lo:.3f},{hi:.3f}]")

# carrier Wilson lower bound quoted in draft §2.1 as .806
k, n = 16, 16
print(f"     carrier 16/16 Wilson = [{wilson(16,16)[0]:.4f},{wilson(16,16)[1]:.4f}]"
      "   (draft §2.1 quotes lower bound .806)")
print(f"     s2t twin 2/16 Wilson = [{wilson(2,16)[0]:.4f},{wilson(2,16)[1]:.4f}]"
      "   (draft §2.2 quotes upper bound .360)")

# =============================================================== TASK 1c
# descriptive correlations the draft quotes (my own Spearman, no scipy)
def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for t in range(i, j + 1):
                r[order[t]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")

print("\n[1c] DESCRIPTIVE CORRELATIONS (my own Spearman)")
win = L["window"]
noncar = [w for w in win if w["arm"] != "sc25"]
print(f"     gain-vs-duty, all 34 window arms:      rho={spearman([w['gain_delta_vs_wA'] for w in win],[w['meanR'] for w in win]):+.3f}"
      f"   (stored descriptive: {L['descriptive']['rho_gain_meanR_all34']:+.3f})")
print(f"     gain-vs-duty, 33 NON-carrier arms:     rho={spearman([w['gain_delta_vs_wA'] for w in noncar],[w['meanR'] for w in noncar]):+.3f}"
      "   (draft §2.1 quotes -.723)")
sil = [w for w in win if not w["active"]]
print(f"     gain-vs-duty, {len(sil)} silent arms:            rho={spearman([w['gain_delta_vs_wA'] for w in sil],[w['meanR'] for w in sil]):+.3f}"
      "   (draft §2.1 quotes -.833)")
act = [w for w in win if w["active"]]
print(f"     drive-vs-duty, {len(act)} active arms:           rho={spearman([w['delivered_drive'] for w in act],[w['meanR'] for w in act]):+.3f}"
      "   (draft §2.1 quotes +.187)")
ae = [w for w in act if w["eff_sign"] > 0]
print(f"     drive-vs-duty, {len(ae)} active excitatory:     rho={spearman([w['delivered_drive'] for w in ae],[w['meanR'] for w in ae]):+.3f}"
      "   (draft §2.1 quotes +.548)")
# silent-null width
print(f"     silent-cell null: k range {min(w['kR'] for w in sil)}-{max(w['kR'] for w in sil)}, "
      f"mean-duty range {min(w['meanR'] for w in sil):.3f}-{max(w['meanR'] for w in sil):.3f}"
      "   (draft: 2-11 seeds, .340-.605)")
cls = {}
for w in win:
    c = classify(w["kR"], w["meanR"], bands)
    cls[c] = cls.get(c, 0) + 1
print(f"     class census of 34 window arms (my rule): {cls}   (draft: 1 super, 10 intermediate, 23 not-super)")
print(f"     n_active={len(act)} n_active_exc={len(ae)} n_silent={len(sil)}"
      f"   (stored branch_inputs: active={L['branch_inputs']['n_active']},"
      f" exc={L['branch_inputs']['n_active_exc']}, silent={L['branch_inputs']['silent_n']})")

# =============================================================== TASK 1d
# threepanel.csv row vs Table 1
print("\n[1d] THREEPANEL ROW CHECK (banc/l184/threepanel.csv)")
print("     source sha=", sha(ROOT + "/banc/l184/threepanel.csv")[:16])
tp = {r["arm"]: r for r in csv.DictReader(open(f"{ROOT}/banc/l184/threepanel.csv"))}
for arm, draft in [("sc25", ("16/16 .758", "8/16 .510", "193/240 .622")),
                   ("cutwA", ("5/16 .408", "0/16 .000", "0/240 .097")),
                   ("dmA", ("5/16 .390", "0/16 .004", "36/240 .376"))]:
    r = tp[arm]
    print(f"     {arm:6s} chopped {r['chopped_k']}/16 {float(r['chopped_mean']):.3f} | "
          f"fast {r['fast_k']}/16 {float(r['fast_mean']):.3f} | "
          f"cross {r['cross_k']}/240 {float(r['cross_mean']):.3f}   "
          f"|| draft Table 1: {draft[0]} | {draft[1]} | {draft[2]}")
# consistency between the two independent artifacts for the same quantity
print("\n     cross-artifact consistency, chopped column, l175 vs l184:")
bad = []
for arm, r in tp.items():
    if arm in index:
        # stored meanR in l175 is rounded to 3dp; compare at that tolerance
        if int(r["chopped_k"]) != index[arm]["kR"] or \
           abs(round(float(r["chopped_mean"]), 3) - index[arm]["meanR"]) > 1e-9:
            bad.append((arm, r["chopped_k"], index[arm]["kR"],
                        float(r["chopped_mean"]), index[arm]["meanR"]))
print("     disagreements beyond 3dp rounding:", bad if bad else "NONE across all 37 shared arms")

print("\nDONE")
