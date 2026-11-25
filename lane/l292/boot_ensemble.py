#!/usr/bin/env python3
"""L292 offline test 3: the cap read with an ENSEMBLE instead of a 2-seed floor.

offline_settle.py / offline_delta.py each compare one K-step state with one
full-window state and scale by a floor estimated from ONE pair of seeds -- a
ratio of two half-normals has no finite mean, so "1.6x floor" is not a
measurement. Here every seed runs ONE trajectory from the start state and is
read twice, at K = 1,000 steps (the cap) and again at K2 (3,000 for the
session boot, 20,000 for an idle window with the world session's real trust
delta active). Paired differences over seeds: mean, SE, and the largest
standardised shift among the readouts the app consumes.

    A  boot:  X = 0, no delta   (Session.__init__ observe(30), 3,000 -> 1,000)
    B  idle:  world.pt X + its plas_d, real night tonic (observe(600) path)

Run from ~/critters/peabrain:
    nice -n 15 timeout 600 .venv/bin/python lane/l292/boot_ensemble.py
"""
import json
import math
import sys
import time

import torch

sys.path.insert(0, ".")
import brain as _brain            # noqa: E402
import mood as _mood              # noqa: E402
import senses as _senses          # noqa: E402

N = 12
K_CAP = 1000


def dan_edges(b, s):
    W = b.W
    crow = W.crow_indices().to(torch.long)
    col = W.col_indices().to(torch.long)
    dan_rows = s.probes["DAN"]
    idx = torch.cat([torch.arange(a, e, device=b.device)
                     for a, e in zip(crow[dan_rows].tolist(),
                                     crow[dan_rows + 1].tolist())])
    return col[idx], torch.repeat_interleave(
        dan_rows, crow[dan_rows + 1] - crow[dan_rows])


def pops(b, s):
    X = b.X
    return {"dan": float(X[s.probes["DAN"]].mean()),
            "lc": float(X[s.probes["LC"]].mean()),
            "kc": float(X[s.probes["KC"]].mean()),
            "oct": float(X[b.mod_idx["octopamine"]].mean()),
            "ser": float(X[b.mod_idx["serotonin"]].mean()),
            "dop": float(X[b.mod_idx["dopamine"]].mean()),
            "dn": float(X[s.dn["all"]].mean()),
            "L": float(X[s.dn["left"]].mean()),
            "R": float(X[s.dn["right"]].mean())}


def move(p):
    return max(0.0, min(1.0, (p["dn"] - 0.035) / 0.055))


def turn(p):
    return (p["R"] - p["L"]) / (p["R"] + p["L"] + 1e-6) * min(move(p), 1.0)


def peak(m, s, b, seed):
    b.gen.manual_seed(seed)
    m.observe(0.2, event="greet")
    p = m.last_peak or {}
    # the axis targets observe() derives from this peak (event "greet")
    t_joy = max(0.0, p["ser"] - 0.04) * 2.5 + max(0.0, p["dan"] - 0.07) * 2.0
    t_sal = max(0.0, p["dop"] - 0.05) * 4.0
    return {"pk_dan": p["dan"], "pk_dop": p["dop"], "pk_kc": p["kc"],
            "pk_lc": p["lc"], "pk_dn": p["dn"], "t_joy": t_joy, "t_sal": t_sal}


def stats(v):
    n = len(v)
    mu = sum(v) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in v) / (n - 1)) if n > 1 else 0.0
    return mu, sd, sd / math.sqrt(n)


def main():
    t0 = time.time()
    b = _brain.FlyBrain()
    b.op_gain = 0.95 / b.rho
    s = _senses.DuckSenses(b)
    m = _mood.MoodState(s)
    gain = b.op_gain
    dark = _mood.darkness_now()
    _mood.darkness_now = lambda: dark
    I = None
    if dark > 0.05:
        I = torch.zeros(b.N, device=b.device)
        I[s.probes["CX"]] = 0.30 * dark
    dan_src, dan_dst = dan_edges(b, s)
    blob = torch.load("sessions/world.pt", weights_only=True)
    X0w = blob["X"].to(b.device).clone()
    dw = blob["plas_d"].to(b.device).clone()

    out = {"n_seeds": N, "k_cap": K_CAP, "dark": dark, "cases": {}}
    for name, X0, delta, k2 in (("A_boot_x0_nodelta", None, None, 3000),
                                ("B_idle_world_delta", X0w, dw, 20000)):
        b.active_delta = None if delta is None else (dan_src, dan_dst, delta)
        a, c = [], []
        for sd in range(N):
            if X0 is None:
                b.X.zero_()
            else:
                b.X.copy_(X0)
            b.gen.manual_seed(1000 + sd)
            for _ in range(K_CAP):
                b.step(I=I, gain=gain)
            Xk = b.X.clone()
            c.append({**pops(b, s), "move": move(pops(b, s)), "turn": turn(pops(b, s)),
                      **peak(m, s, b, 5000 + sd)})
            b.X.copy_(Xk)
            b.gen.manual_seed(1000 + sd)      # continue the SAME noise stream
            # (the greet above consumed draws; rebuild the stream state by
            #  re-running is costly, so the continuation uses a fresh stream)
            b.gen.manual_seed(7000 + sd)
            for _ in range(k2 - K_CAP):
                b.step(I=I, gain=gain)
            a.append({**pops(b, s), "move": move(pops(b, s)), "turn": turn(pops(b, s)),
                      **peak(m, s, b, 5000 + sd)})
        keys = list(a[0].keys())
        res = {}
        for k in keys:
            vk = [r[k] for r in c]
            v2 = [r[k] for r in a]
            mk, sk, ek = stats(vk)
            m2, s2, e2 = stats(v2)
            dif = [x - y for x, y in zip(vk, v2)]
            md, sdd, ed = stats(dif)
            res[k] = {"at_cap": mk, "cap_sd": sk, "at_k2": m2, "k2_sd": s2,
                      "diff": md, "diff_se": ed,
                      "diff_se_units": (md / ed if ed > 0 else None),
                      "diff_over_k2_sd": (md / s2 if s2 > 0 else None)}
        out["cases"][name] = {"k2": k2, "readouts": res}
        worst = max((abs(v["diff_se_units"] or 0), k) for k, v in res.items())
        print(json.dumps({"case": name, "k2": k2,
                          "worst_abs_se_units": [worst[1], round(worst[0], 2)],
                          "max_abs_diff_over_k2_sd": round(max(abs(v["diff_over_k2_sd"] or 0)
                                                               for v in res.values()), 4)}),
              flush=True)
        for k in keys:
            v = res[k]
            print(f"   {k:7s} cap {v['at_cap']:.6f} (sd {v['cap_sd']:.2e})  "
                  f"k2 {v['at_k2']:.6f} (sd {v['k2_sd']:.2e})  diff {v['diff']:+.2e} "
                  f"+- {v['diff_se']:.1e} = {v['diff_se_units']:+.1f} SE  "
                  f"({v['diff_over_k2_sd']:+.2f} sd)", flush=True)
    out["wall_s"] = round(time.time() - t0, 1)
    with open("lane/l292/boot_ensemble.json", "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("done", out["wall_s"], "s", flush=True)


if __name__ == "__main__":
    main()
