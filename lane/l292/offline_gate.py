#!/usr/bin/env python3
"""L292 offline gate for the IDLE_SETTLE_S cap in mood.py (before deploy).

Twins: the PRE-PATCH module (lane/l292/mood_before.py, a byte copy of
mood.py taken before the edit) and the PATCHED live module (mood.py), on
ONE shared brain, same seed, same starting state. Every axis and drive in
observe() is closed-form in `seconds`, so an idle window's axes must come
out BIT-IDENTICAL with and without the cap; the step loop must run exactly
min(int(seconds/0.01), 1000) steps; an event window must be unchanged.

Run from ~/critters/peabrain:
    .venv/bin/python lane/l292/offline_gate.py        -> exit 0 = PASS
"""
import difflib
import hashlib
import importlib.util
import json
import sys

import torch

sys.path.insert(0, ".")
import brain as _brain            # noqa: E402
import senses as _senses          # noqa: E402

DT = 0.01
CAP_STEPS = 1000


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


results = []


def check(name, ok, detail):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + " | " + str(detail), flush=True)


def twin_axes(mod, s, X, axes0, seconds, dark, event=None, seed=5):
    b = s.brain
    b.X.copy_(X)
    b.gen.manual_seed(seed)
    mod.darkness_now = lambda d=dark: d          # this process only
    m = mod.MoodState(s)
    for k, v in axes0.items():
        setattr(m, k, v)
    c0 = b.step_count
    m.observe(seconds, event=event)
    return m, b.step_count - c0


def main():
    before = load("mood_before_l292", "lane/l292/mood_before.py")
    after = load("mood_after_l292", "mood.py")
    src_b = open("lane/l292/mood_before.py").read()
    src_a = open("mood.py").read()
    live_src = open("/home/t3rpz/critters/peabrain/mood.py").read()
    print(json.dumps({"before_sha": sha("lane/l292/mood_before.py"),
                      "after_sha": sha("mood.py")}), flush=True)

    # ---- structure: the delta is exactly two statements plus comments
    removed, added = [], []
    for line in difflib.unified_diff(src_b.splitlines(), src_a.splitlines(),
                                     lineterm="", n=0):
        if line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    added_code = [a for a in added if a.strip() and not a.strip().startswith("#")]
    check("delta.removed_lines_empty", removed == [], removed)
    check("delta.added_code_is_exactly_the_two_lines",
          added_code == ["IDLE_SETTLE_S = 10.0",
                         "        steps = min(steps, int(IDLE_SETTLE_S / 0.01))"],
          added_code)
    check("patched_file_is_the_live_file", src_a == live_src, "mood.py == live path")
    for attr in ("observe", "axes", "mood_tag"):
        check(f"structure.MoodState.{attr}", hasattr(after.MoodState, attr), attr)
    check("structure.IDLE_SETTLE_S", getattr(after, "IDLE_SETTLE_S", None) == 10.0,
          getattr(after, "IDLE_SETTLE_S", None))
    check("structure.before_has_no_cap", not hasattr(before, "IDLE_SETTLE_S"), "absent")

    b = _brain.FlyBrain()
    b.op_gain = 0.95 / b.rho
    s = _senses.DuckSenses(b)

    # ---- a settled shared start + a non-default axis state
    after.darkness_now = lambda: 0.0
    b.gen.manual_seed(7)
    for _ in range(1500):
        b.step(gain=b.op_gain)
    X0 = b.X.clone()
    AX0 = {"fear": 0.7, "food_joy": 0.5, "trust": 0.6, "salience": 0.9,
           "hunger": 0.4, "sleep": 0.3, "clock_s": 1000.0, "last_peas_s": -600.0,
           "learn_pressure": 0.1}

    # ---- T1: the step count of observe(), across the cap boundary
    for seconds in (1.0, 5.0, 9.99, 10.0, 10.01, 45.0, 600.0):
        _, n = twin_axes(after, s, X0, AX0, seconds, 1.0)
        want = min(int(seconds / DT), CAP_STEPS)
        check(f"steps.observe({seconds})", n == want, {"ran": n, "want": want})

    # ---- T2: idle window axes bit-identical, 600 s and 45 s, night and day
    for seconds, dark in ((600.0, 1.0), (600.0, 0.0), (45.0, 1.0)):
        mb, nb = twin_axes(before, s, X0, AX0, seconds, dark)
        ma, na = twin_axes(after, s, X0, AX0, seconds, dark)
        same = (ma.axes() == mb.axes() and ma.clock_s == mb.clock_s
                and ma.last_peas_s == mb.last_peas_s
                and ma.fear == mb.fear and ma.food_joy == mb.food_joy
                and ma.trust == mb.trust and ma.salience == mb.salience
                and ma.hunger == mb.hunger and ma.sleep == mb.sleep
                and ma.learn_pressure == mb.learn_pressure)
        want_b = int(seconds / DT)
        check(f"axes.identical idle {seconds}s dark {dark}", same,
              {"after": ma.axes(), "before": mb.axes(),
               "steps_after": na, "steps_before": nb})
        check(f"steps idle {seconds}s dark {dark}", na == CAP_STEPS and nb == want_b,
              {"after": na, "before": nb})

    # ---- T3: event windows are untouched. NOT a bit-equality claim: the
    # SAME module run twice differs in the last bit on this GPU (5.96e-08
    # over ~10.9k of 139k cells, gate_debug.py), so torch.equal failed the
    # first build of this gate on before-vs-before. The equality instrument
    # is CALIBRATED on a same-module twin in the same run; before-vs-after
    # must sit at or below that order (1e-6), axes exactly equal.
    for seconds, ev in ((2.0, "greet"), (2.0, "swat"), (5.0, "water")):
        mb, nb = twin_axes(before, s, X0, AX0, seconds, 1.0, event=ev)
        Xb = b.X.clone()
        ma, na = twin_axes(after, s, X0, AX0, seconds, 1.0, event=ev)
        Xa = b.X.clone()
        twin_axes(before, s, X0, AX0, seconds, 1.0, event=ev)   # same code again
        floor = float((b.X - Xb).abs().max())
        dx = float((Xa - Xb).abs().max())
        want = int(seconds / DT)
        peak_dx = max(abs(ma.last_peak[k] - mb.last_peak[k]) for k in mb.last_peak)
        check(f"calibration: same module twice reproduces to <= 1e-6 ({ev})",
              floor <= 1e-6, {"same_code_max_dx": floor})
        check(f"event window identical {ev} {seconds}s",
              (ma.axes() == mb.axes() and ma.clock_s == mb.clock_s
               and na == want and nb == want and dx <= 1e-6 and peak_dx <= 1e-7),
              {"after": ma.axes(), "before": mb.axes(), "steps": [na, nb],
               "max_dx": dx, "same_code_floor": floor, "peak_max_dx": peak_dx})

    # ---- T4: an event riding a capped window (not a live path): axes still
    # closed-form, peak still read at the stimulus
    mb, nb = twin_axes(before, s, X0, AX0, 45.0, 1.0, event="peas")
    ma, na = twin_axes(after, s, X0, AX0, 45.0, 1.0, event="peas")
    check("capped window + peas: axes identical",
          ma.axes() == mb.axes() and ma.clock_s == mb.clock_s
          and ma.last_peas_s == mb.last_peas_s and na == CAP_STEPS,
          {"after": ma.axes(), "before": mb.axes(), "steps": [na, nb]})

    # ---- T5: the session boot observe(30) from X = 0: axes identical
    zeros = torch.zeros_like(X0)
    mb, nb = twin_axes(before, s, zeros, AX0, 30.0, 1.0)
    ma, na = twin_axes(after, s, zeros, AX0, 30.0, 1.0)
    check("boot observe(30): axes identical",
          ma.axes() == mb.axes() and ma.clock_s == mb.clock_s
          and na == CAP_STEPS and nb == 3000,
          {"after": ma.axes(), "before": mb.axes(), "steps": [na, nb]})

    # ---- T6: the live cap in-situ -- DuckBridge.session_turn's exact call
    # observe(idle) with idle = min(now - last_seen, 600): 600 s costs 1,000
    c0 = b.step_count
    after.darkness_now = lambda: 1.0
    b.gen.manual_seed(9)
    after.MoodState(s).observe(600.0)
    n = b.step_count - c0
    check("live path observe(600) runs exactly 1,000 steps", n == CAP_STEPS, n)

    passed = sum(1 for r in results if r[1])
    doc = {"passed": passed, "total": len(results),
           "results": [{"name": n, "ok": ok, "detail": str(d)[:600]} for n, ok, d in results],
           "before_sha": sha("lane/l292/mood_before.py"), "after_sha": sha("mood.py")}
    with open("lane/l292/offline_gate.json", "w") as f:
        json.dump(doc, f, indent=1)
    print(f"GATE {'PASS' if passed == len(results) else 'FAIL'} {passed}/{len(results)}",
          flush=True)
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
