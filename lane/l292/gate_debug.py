#!/usr/bin/env python3
"""L292 gate debug: WHY did the event-window twins differ? Runs the exact
twin call three ways and prints the per-component differences (axes, clock,
peak, X) so the cause is read, not guessed. Read-only.
Run from ~/critters/peabrain: .venv/bin/python lane/l292/gate_debug.py
"""
import importlib.util
import sys

import torch

sys.path.insert(0, ".")
import brain as _brain            # noqa: E402
import senses as _senses          # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(mod, s, X, axes0, seconds, event, seed):
    b = s.brain
    b.X.copy_(X)
    b.gen.manual_seed(seed)
    mod.darkness_now = lambda: 1.0
    m = mod.MoodState(s)
    for k, v in axes0.items():
        setattr(m, k, v)
    m.observe(seconds, event=event)
    return m, b.X.clone()


before = load("mood_before_dbg", "lane/l292/mood_before.py")
after = load("mood_after_dbg", "mood.py")
b = _brain.FlyBrain()
b.op_gain = 0.95 / b.rho
s = _senses.DuckSenses(b)
b.gen.manual_seed(7)
for _ in range(1500):
    b.step(gain=b.op_gain)
X0 = b.X.clone()
AX0 = {"fear": 0.7, "food_joy": 0.5, "trust": 0.6, "salience": 0.9, "hunger": 0.4,
       "sleep": 0.3, "clock_s": 1000.0, "last_peas_s": -600.0, "learn_pressure": 0.1}

for label, ma_, mb_ in (("before vs before", before, before),
                        ("after vs after", after, after),
                        ("before vs after", before, after),
                        ("after vs before", after, before)):
    m1, X1 = run(ma_, s, X0, AX0, 2.0, "greet", 5)
    m2, X2 = run(mb_, s, X0, AX0, 2.0, "greet", 5)
    d = (X1 - X2).abs()
    print(f"{label}: max|dX| {float(d.max()):.3e} n_diff {int((d > 0).sum())} "
          f"torch.equal {torch.equal(X1, X2)} axes_eq {m1.axes() == m2.axes()} "
          f"clock {m1.clock_s} {m2.clock_s} peak_eq {m1.last_peak == m2.last_peak}")
    for k in m1.last_peak:
        if m1.last_peak[k] != m2.last_peak[k]:
            print("   peak differs", k, repr(m1.last_peak[k]), repr(m2.last_peak[k]))
