#!/usr/bin/env python3
"""L292 offline test 2: the idle-settle cap with a TRUST DELTA active.

tick 279's offline_settle.py showed 1,000 idle steps leave the brain as
settled as the full 60,000-step window -- with active_delta None. The one
gap the card names: a visitor with a written plas_d (Hebbian trust on the
DAN-input synapses) relaxes on a DIFFERENT effective graph, so its slowest
mode is not assumed. This measures the same quantity on REAL stored deltas.

Also measured (the cap touches it too): Session.__init__'s observe(30)
"arrive settled" boot from X = 0 drops 3,000 -> 1,000 steps.

For each case: full window under two seeds (the noise floor), then K steps
against the seed-11 full state -- per-cell mean|dX|, the population means
the app reads (DAN/LC/KC/oct/ser/dop, DN all/L/R -> move/turn), and the
next greet's neural peak. Sessions are READ (torch.load), never written.
Live modules are imported read-only; nothing here touches the service.

Run from ~/critters/peabrain:
    nice -n 15 timeout 900 .venv/bin/python lane/l292/offline_delta.py
"""
import glob
import json
import sys
import time

import torch

sys.path.insert(0, ".")
import brain as _brain            # noqa: E402
import mood as _mood              # noqa: E402
import senses as _senses          # noqa: E402

WINDOW_S = 600.0
DT = 0.01
FULL = int(WINDOW_S / DT)         # 60,000
KS = (250, 500, 1000, 2000)
SEEDS = (11, 12)
TOPN = 4
REAL_DARK = _mood.darkness_now()


def dan_edges(b, s):
    """Verbatim derivation of the plasticity substrate (bridge.py 222-231):
    every edge INTO a dopaminergic reward neuron."""
    W = b.W
    crow = W.crow_indices().to(torch.long)
    col = W.col_indices().to(torch.long)
    dan_rows = s.probes["DAN"]
    idx = torch.cat([torch.arange(a, e, device=b.device)
                     for a, e in zip(crow[dan_rows].tolist(),
                                     crow[dan_rows + 1].tolist())])
    src = col[idx]
    dst = torch.repeat_interleave(
        dan_rows, crow[dan_rows + 1] - crow[dan_rows])
    return src, dst


def tonic(s, dark):
    if dark <= 0.05:
        return None
    I = torch.zeros(s.brain.N, device=s.brain.device)
    I[s.probes["CX"]] = 0.30 * dark
    return I


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


def intent(p):
    """bridge.cx_intent ambient readout (CX_BASE .035, CX_SPAN .055)."""
    move = max(0.0, min(1.0, (p["dn"] - 0.035) / 0.055))
    turn = (p["R"] - p["L"]) / (p["R"] + p["L"] + 1e-6) * min(move, 1.0)
    return {"move": round(move, 4), "turn": round(turn, 4)}


def main():
    t_start = time.time()
    b = _brain.FlyBrain()
    b.op_gain = 0.95 / b.rho
    s = _senses.DuckSenses(b)
    m = _mood.MoodState(s)
    gain = b.op_gain
    dan_src, dan_dst = dan_edges(b, s)
    print(json.dumps({"dan_edges": int(len(dan_src)), "dan_cells": int(len(s.probes["DAN"])),
                      "rho": b.rho, "gain": gain, "real_dark": REAL_DARK}), flush=True)

    def seed(n):
        b.gen.manual_seed(n)

    def relax(I, n):
        for _ in range(n):
            b.step(I=I, gain=gain)

    # ---- scan stored sessions (READ ONLY): the largest written deltas
    rows = []
    n_len_ok = n_len_bad = 0
    for f in sorted(glob.glob("sessions/*.pt")):
        try:
            blob = torch.load(f, weights_only=True)
        except Exception as e:  # noqa: BLE001
            print("unreadable", f, repr(e)[:80], flush=True)
            continue
        d = blob["plas_d"]
        if d.numel() == len(dan_src):
            n_len_ok += 1
        else:
            n_len_bad += 1
        mass = float(d.abs().sum())
        rows.append((mass, f, float(d.max()), float(d.min()), int((d != 0).sum())))
    rows.sort(reverse=True)
    nz = [r for r in rows if r[0] > 0]
    print(json.dumps({"sessions": len(rows), "len_ok": n_len_ok, "len_bad": n_len_bad,
                      "with_nonzero_delta": len(nz),
                      "top5": [(round(r[0], 4), r[1].split("/")[-1], round(r[2], 5),
                                round(r[3], 5), r[4]) for r in rows[:5]],
                      "world": [r for r in rows if r[1].endswith("world.pt")][:1]}),
          flush=True)

    cases = []
    for mass, f, mx, mn, nnz in nz[:TOPN]:
        cases.append({"name": f.split("/")[-1], "file": f, "synthetic": None,
                      "dark": REAL_DARK})
    if cases:   # the strongest real delta, by day as well as by night
        cases.append({**cases[0], "dark": 0.0, "name": cases[0]["name"] + "@day"})
    wfile = [r[1] for r in rows if r[1].endswith("world.pt")]
    cases.append({"name": "syn+0.75", "file": wfile[0] if wfile else None,
                  "synthetic": +0.75, "dark": REAL_DARK})
    cases.append({"name": "syn-0.75", "file": wfile[0] if wfile else None,
                  "synthetic": -0.75, "dark": REAL_DARK})

    out = []
    for c in cases:
        if c["file"]:
            blob = torch.load(c["file"], weights_only=True)
            X0 = blob["X"].to(b.device).clone()
            dlt = blob["plas_d"].to(b.device).clone()
        else:
            X0 = torch.zeros(b.N, device=b.device)
            dlt = torch.zeros(len(dan_src), device=b.device)
        if c["synthetic"] is not None:
            dlt = torch.full_like(dlt, c["synthetic"])
        _mood.darkness_now = lambda d=c["dark"]: d       # this process only
        I = tonic(s, c["dark"])
        b.active_delta = (dan_src, dan_dst, dlt)
        row = {"case": c["name"], "dark": c["dark"],
               "delta": {"mass": float(dlt.abs().sum()), "max": float(dlt.max()),
                         "min": float(dlt.min()), "nnz": int((dlt != 0).sum())}}

        fulls, pf = [], []
        for sd in SEEDS:
            b.X.copy_(X0)
            seed(sd)
            relax(I, FULL)
            fulls.append(b.X.clone())
            pf.append(pops(b, s))
        (Xf, Xg), (pf1, pf2) = fulls, pf
        floor_mean = float((Xf - Xg).abs().mean())
        floor_max = float((Xf - Xg).abs().max())
        pop_floor = {k: abs(pf1[k] - pf2[k]) for k in pf1}
        row.update({"floor_mean": floor_mean, "floor_max": floor_max,
                    "full_pops": pf1, "full_intent": intent(pf1),
                    "seed2_intent": intent(pf2), "pop_floor": pop_floor})

        def next_peak(X):
            b.X.copy_(X)
            seed(3)
            m.observe(0.2, event="greet")
            return {k: (m.last_peak or {}).get(k) for k in ("lc", "dan", "kc", "dop", "dn")}
        nx_full = next_peak(Xf)
        nx_seed2 = next_peak(Xg)

        by_k = {}
        for K in KS:
            b.X.copy_(X0)
            seed(11)
            relax(I, K)
            Xk = b.X.clone()
            dd = (Xk - Xf).abs()
            pk = pops(b, s)
            nk = next_peak(Xk)
            by_k[K] = {"mean_dx": float(dd.mean()), "max_dx": float(dd.max()),
                       "pop_dx": {k: pk[k] - pf1[k] for k in pk},
                       "pop_dx_over_floor": {k: (abs(pk[k] - pf1[k]) / pop_floor[k]
                                                 if pop_floor[k] > 0 else None) for k in pk},
                       "intent": intent(pk),
                       "peak_dx": {k: nk[k] - nx_full[k] for k in nk},
                       "peak_floor": {k: nx_seed2[k] - nx_full[k] for k in nk}}
        row["by_K"] = by_k
        out.append(row)
        print(json.dumps(row), flush=True)

    # ---- cold boot: Session.__init__ observe(30) from X = 0, no delta
    b.active_delta = None
    _mood.darkness_now = lambda: REAL_DARK
    I = tonic(s, REAL_DARK)
    boot = {}
    ref = {}
    for sd in SEEDS:
        b.X.zero_()
        seed(sd)
        relax(I, 3000)
        ref[sd] = (b.X.clone(), pops(b, s))
    boot["floor_mean"] = float((ref[11][0] - ref[12][0]).abs().mean())
    boot["floor_max"] = float((ref[11][0] - ref[12][0]).abs().max())
    boot["pop_floor"] = {k: abs(ref[11][1][k] - ref[12][1][k]) for k in ref[11][1]}
    boot["boot3000"] = {"pops": ref[11][1], "intent": intent(ref[11][1]),
                        "intent_seed2": intent(ref[12][1]), "peak": next_peak(ref[11][0]),
                        "peak_seed2": next_peak(ref[12][0])}
    for K in (500, 1000, 2000):
        b.X.zero_()
        seed(11)
        relax(I, K)
        Xk = b.X.clone()
        pk = pops(b, s)
        boot[f"boot{K}"] = {
            "mean_dx": float((Xk - ref[11][0]).abs().mean()),
            "max_dx": float((Xk - ref[11][0]).abs().max()),
            "pop_dx": {k: pk[k] - ref[11][1][k] for k in pk}, "intent": intent(pk),
            "peak": next_peak(Xk)}
    print(json.dumps({"cold_boot": boot}), flush=True)

    doc = {"window_steps": FULL, "ks": KS, "real_dark": REAL_DARK, "cases": out,
           "cold_boot": boot, "wall_s": round(time.time() - t_start, 1)}
    with open("lane/l292/offline_delta.json", "w") as f:
        json.dump(doc, f, indent=1, default=float)
    print("done", doc["wall_s"], "s", flush=True)


if __name__ == "__main__":
    main()
