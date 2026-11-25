#!/usr/bin/env python3
"""L292: bounded foreground wait for a lab exit file, then print the
offline_delta results in a readable table. Usage:
    python3 lane/l292/show_delta.py <exit-file> <out-file> [max-wait-s]
"""
import json
import os
import sys
import time

exit_file, out_file = sys.argv[1], sys.argv[2]
max_wait = float(sys.argv[3]) if len(sys.argv) > 3 else 400.0
t0 = time.time()
while not os.path.exists(exit_file) and time.time() - t0 < max_wait:
    time.sleep(5)
print("exit:", open(exit_file).read().strip() if os.path.exists(exit_file) else "NOT WRITTEN (still running?)",
      "| waited", round(time.time() - t0, 1), "s")
rows = [json.loads(l) for l in open(out_file) if l.startswith("{")]
print("n rows", len(rows))
for r in rows:
    if "case" in r:
        d = r["delta"]
        fp = r["full_pops"]
        print(f"\nCASE {r['case']} dark {r['dark']:.3f} delta mass {d['mass']:.1f} "
              f"max {d['max']:.4f} min {d['min']:.4f}")
        print(f"  floor mean {r['floor_mean']:.5f} max {r['floor_max']:.5f} | full pops "
              f"dan {fp['dan']:.4f} dop {fp['dop']:.4f} dn {fp['dn']:.4f} "
              f"intent {r['full_intent']} seed2 {r['seed2_intent']}")
        for K, v in r["by_K"].items():
            pf = r["pop_floor"]
            ratio = {k: (round(v["pop_dx"][k] / pf[k], 2) if pf[k] > 0 else None) for k in v["pop_dx"]}
            print(f"  K {K} mean_dx {v['mean_dx']:.5f} (x{v['mean_dx'] / r['floor_mean']:.2f} floor) "
                  f"max_dx {v['max_dx']:.5f} (x{v['max_dx'] / r['floor_max']:.2f} floor) intent {v['intent']}")
            print("     pop_dx/floor", ratio)
            print("     peak_dx", {k: round(x, 6) for k, x in v["peak_dx"].items()},
                  "| peak_floor", {k: round(x, 6) for k, x in v["peak_floor"].items()})
    elif "cold_boot" in r:
        cb = r["cold_boot"]
        print(f"\nCOLD BOOT floor mean {cb['floor_mean']:.5f} max {cb['floor_max']:.5f} pop_floor",
              {k: round(v, 6) for k, v in cb["pop_floor"].items()})
        b3 = cb["boot3000"]
        print("  boot3000 pops", {k: round(v, 5) for k, v in b3["pops"].items()},
              "intent", b3["intent"], "seed2", b3["intent_seed2"],
              "peak", {k: round(v, 6) for k, v in b3["peak"].items()})
        for K in (500, 1000, 2000):
            v = cb[f"boot{K}"]
            print(f"  boot {K} mean_dx {v['mean_dx']:.5f} (x{v['mean_dx'] / cb['floor_mean']:.2f} floor) "
                  f"max_dx {v['max_dx']:.5f} pop_dx",
                  {k: round(x, 6) for k, x in v["pop_dx"].items()}, "intent", v["intent"],
                  "peak", {k: round(x, 6) for k, x in v["peak"].items()})
    elif "done" in str(r) or "wall_s" in r:
        print("\n", {k: v for k, v in r.items() if k in ("wall_s", "window_steps")})
