"""L65 verdict derivation from stored results (PREREG gates)."""
import json

r = json.load(open("/home/t3rpz/critters/peabrain-lab/banc/l65/results_l65.json"))
print("P1:", r["P1"]["g_star"], round(r["P1"]["af"], 4), r["P1"]["in_band"])
for arm in ["A", "B"]:
    c = r["arms"][arm]["confirm"]
    fz = r["arms"][arm]["frozen"]
    print(f"\nARM {arm} frozen g={fz['g']:.4g} beta={fz['beta']} d={fz['d']}")
    for p in c:
        if "S" in p:
            print(f"  seed {p['seed']}: S {({k: round(v,3) for k,v in p['S'].items()})} "
                  f"depth {({k: round(v,3) for k,v in p['depth'].items()})} "
                  f"rhythm {p['rhythm']:.0f}@{p['rhythm_f']:.2f}Hz af {p['af']:.3f}")
        else:
            print(f"  seed {p['seed']}: INVALID {p['invalid']}")
    # P2 gate
    for k in ["Ti", "Tr"]:
        S = [p["S"][k] for p in c if "S" in p]
        D = [p["depth"][k] for p in c if "S" in p]
        m = sum(S) / len(S)
        pos = sum(1 for v in S if v > 0)
        dep_ok = all(v >= 0.03 for v in D)
        print(f"  P2[{k}]: mean {m:.3f} pos {pos}/3 depth_ok {dep_ok} -> "
              f"{'PASS' if (m>=0.30 and pos>=2 and dep_ok) else ('PARTIAL' if m>=0.15 else 'FAIL')}")
la, bp = r["ladder_arm"], r["ladder_best_pair"]
real = r["ladder_real_S"]
print(f"\nladder arm {la} best pair {bp} real mean S {real:.3f}")
for tier in ["density", "degree"]:
    means = []
    for d in r["ladder"][tier]:
        S = [p["S"][bp] for p in d["seeds"] if "S" in p]
        means.append(sum(S) / len(S))
    print(f"  {tier}: per-draw mean S {[round(m,3) for m in means]} "
          f"max {max(means):.3f}")
gap_ok = max(sum([p["S"][bp] for p in d["seeds"] if "S" in p])
             / max(1, len([p for p in d["seeds"] if "S" in p]))
             for d in r["ladder"]["degree"]) <= real - 0.15
print(f"P3 (wiring-specific, gap>=.15): {'PASS' if gap_ok else 'FAIL'}")
