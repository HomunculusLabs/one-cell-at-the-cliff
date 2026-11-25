"""L99 seeded baseline: l100_baseline + random.seed on the GLOBAL module
so even the legacy unseeded diary t-draws become deterministic."""
import os, random, sys, json
os.environ["PEBRAIN_FORCE_HOUR"] = "14"
sys.path.insert(0, "/home/t3rpz/critters/peabrain")
import bridge  # noqa
from bridge import DuckBridge  # noqa

def main():
    random.seed(31337)
    b = DuckBridge()
    s = b.open_session(seed=11)
    rng = random.Random(4242)
    trace = []
    for i in range(40):
        if i % 8 == 2:
            s.mood.sleep = 0.9
        elif i % 8 == 4:
            s.mood.hunger = 0.9
        elif i % 8 == 6:
            s.mood.fear = 0.5
        else:
            s.mood.sleep, s.mood.hunger, s.mood.fear = 0.1, 0.3, 0.05
            s.curiosity = 0.6
        act = b.world_tick(s, rng)
        trace.append({"i": i, "act": act, "hoard": s.hoard,
                      "curio": round(float(s.curiosity), 6),
                      "n_diary": len(s.diary),
                      "ts": [e["t"] for e in s.diary],
                      "texts": [e["text"] for e in s.diary]})
    json.dump(trace, open(sys.argv[1], "w"), indent=1)
    print("wrote", sys.argv[1])

main()
