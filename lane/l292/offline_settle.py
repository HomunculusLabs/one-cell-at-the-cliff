#!/usr/bin/env python3
"""L292 offline test: how many brain steps does an IDLE window need?

mood.observe(seconds) steps the whole brain `seconds/0.01` times, so a
600 s idle window (the session_turn cap) costs 60,000 steps on the request
thread under the lock -- the measured 16.5 s cold /needs. Every mood axis
and drive in observe() is closed-form in `seconds` (hold(), hunger, sleep),
so the loop exists ONLY to relax X. This measures how far X still moves
between K steps and the full window, against the noise floor of the step
itself (two seeds), for several starting states. Live modules are IMPORTED
READ-ONLY; nothing is written to sessions/ or the service.

Run from ~/critters/peabrain:  nice -n 15 python3 lane/l292/offline_settle.py
"""
import copy
import json
import sys
import time

import torch

sys.path.insert(0, ".")
import brain as _brain          # noqa: E402
import mood as _mood            # noqa: E402
import senses as _senses        # noqa: E402

WINDOW_S = 600.0                # session_turn's idle cap
DT = 0.01
FULL = int(WINDOW_S / DT)       # 60,000 steps
KS = (100, 250, 500, 1000, 2000)   # 1 s / 2.5 s / 5 s / 10 s / 20 s of sim
STATES = ((None, 1.0), ("greet", 1.0), ("swat", 1.0), ("greet", 0.0))

Mood = _mood.MoodState            # brain.step draws its noise from b.gen, so
SEED = None                       # that generator (not torch.manual_seed) is
                                  # what has to be reseeded between arms


def snapshot(b):
    return b.X.clone()


def relax(b, gain, I, n):
    for _ in range(n):
        b.step(I=I, gain=gain)


def tonic(s, dark):
    """The circadian input observe() builds for this darkness."""
    if dark <= 0.05:
        return None
    I = torch.zeros(s.brain.N, device=s.brain.device)
    I[s.probes["CX"]] = 0.30 * dark
    return I


def readouts(b, s):
    X = b.X
    dn = float(X[s.dn["all"]].mean())
    L = float(X[s.dn["left"]].mean())
    R = float(X[s.dn["right"]].mean())
    return {"dn": dn, "L": L, "R": R, "af": float((X > 0.02).float().mean()),
            "mean": float(X.mean())}


def main():
    t_start = time.time()
    b = _brain.FlyBrain()
    b.op_gain = 0.95 / b.rho
    s = _senses.DuckSenses(b)
    m = Mood(s)
    gain = b.op_gain

    def seed(n):
        b.gen.manual_seed(n)

    rows = []
    for ev, dark in STATES:
        _mood.darkness_now = lambda d=dark: d      # this process only
        seed(7)
        b.X.zero_()
        relax(b, gain, tonic(s, dark), 1500)       # a settled start
        m.observe(0.2, event=ev)                   # the state she is left in
        X0 = snapshot(b)
        I = tonic(s, dark)
        # full window under two seeds = the noise floor of the step itself
        outs = []
        for sd in (11, 12):
            b.X.copy_(X0)
            seed(sd)
            relax(b, gain, I, FULL)
            outs.append((snapshot(b), readouts(b, s)))
        (Xf, rf), (Xg, rg) = outs
        noise_max = float((Xf - Xg).abs().max())
        noise_mean = float((Xf - Xg).abs().mean())
        t0 = time.time()
        per = {}
        kept = {}
        for K in KS:
            b.X.copy_(X0)
            seed(11)
            relax(b, gain, I, K)
            kept[K] = snapshot(b)
            r = readouts(b, s)
            d = (b.X - Xf).abs()
            per[K] = {"max_dx_vs_full": float(d.max()), "mean_dx_vs_full": float(d.mean()),
                      "dn": r["dn"], "af": r["af"]}
        t_cap = time.time() - t0

        # the neural peak she shows for the NEXT event (a greet), started
        # from K steps of idle vs the full window -- what the mood axes read
        def next_peak(X):
            b.X.copy_(X)
            seed(3)
            m.observe(0.2, event="greet")
            return {k: (m.last_peak or {}).get(k) for k in ("lc", "dan", "kc", "dop", "dn")}

        nxt = {K: next_peak(kept[K]) for K in KS}
        nxt_full = next_peak(Xf)
        # and from a second full-window seed: the same floor, in peak units
        nxt_seed2 = next_peak(Xg)
        row = {"event": ev, "dark": dark, "noise_floor_max": noise_max,
               "noise_floor_mean": noise_mean,
               "full": {"dn": rf["dn"], "L": rf["L"], "R": rf["R"], "af": rf["af"],
                        "mean": rf["mean"]},
               "seed2": {"dn": rg["dn"], "L": rg["L"], "R": rg["R"], "af": rg["af"]},
               "by_K": per, "next_event_greet": {"by_K": nxt, "full": nxt_full,
                                                 "full_seed2": nxt_seed2},
               "seconds_for_all_K": round(t_cap, 1)}
        rows.append(row)
        print(json.dumps(row), flush=True)
    summary = {"window_steps": FULL, "ks": KS, "rows": rows,
               "wall_s": round(time.time() - t_start, 1)}
    with open("lane/l292/offline_settle.json", "w") as f:
        json.dump(summary, f, indent=1)
    print("done", summary["wall_s"], "s")


if __name__ == "__main__":
    main()
