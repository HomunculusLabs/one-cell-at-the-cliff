"""L68 addendum verdict: n:m spectral entrainment reads (PREREG ADDENDUM 1).

All reads from l68/raw_l68.npz; no rollouts.
"""
import json

import numpy as np

SEGS = {"slow": (0, 2000, 0.7), "fast": (2000, 4000, 1.4),
        "slow2": (4000, 6000, 0.7)}
SEEDS = [11, 22, 33]


def power_at(x, f, dt=0.01):
    q = x - x.mean()
    ps = np.abs(np.fft.rfft(q)) ** 2
    fr = np.fft.rfftfreq(len(x), dt)
    i = int(np.argmin(np.abs(fr - f)))
    return float(ps[i])


out = json.load(open("l68/results_l68.json"))
spec = {}
for fd, segs, arms in ((0.7, ("slow", "slow2"), ("hyb03", "hyb01")),
                       (1.4, ("fast",), ("hyb03", "hyb01"))):
    spec[f"fd{fd}"] = {}
    for a in arms:
        ratios = []
        for s in SEEDS:
            num = np.mean([power_at(np.load("l68/raw_l68.npz")[f"{a}_s{s}_mm"][lo:hi], fd)
                           for lo, hi, _ in (SEGS[k] for k in segs)])
            den = np.mean([power_at(np.load("l68/raw_l68.npz")[f"open_s{s}_mm"][lo:hi], fd)
                           for lo, hi, _ in (SEGS[k] for k in segs)])
            ratios.append(num / max(den, 1e-30))
        spec[f"fd{fd}"][a] = [round(r, 1) for r in ratios]
# chop envelope + subharmonic texture on hyb arms (slow segs)
tex = {}
for a in ("hyb03", "hyb01"):
    rows = []
    for s in SEEDS:
        z = np.load("l68/raw_l68.npz")
        chop = np.mean([power_at(z[f"{a}_s{s}_mm"][lo:hi], 0.1111)
                        for lo, hi, _ in (SEGS[k] for k in ("slow", "slow2"))])
        ochop = np.mean([power_at(z[f"open_s{s}_mm"][lo:hi], 0.1111)
                         for lo, hi, _ in (SEGS[k] for k in ("slow", "slow2"))])
        half = power_at(z[f"{a}_s{s}_mm"][2000:4000], 0.7)
        rows.append(dict(seed=s, chop_ratio=round(chop / max(ochop, 1e-30), 1),
                         fast_halfP=round(half, 1)))
    tex[a] = rows

g = out["gates"]
best07 = max(("hyb03", "hyb01"), key=lambda a: np.min(spec["fd0.7"][a]))
best14 = max(("hyb03", "hyb01"), key=lambda a: np.min(spec["fd1.4"][a]))
g["G1p_07"] = dict(arm=best07, ratios=spec["fd0.7"][best07],
                   ok=int(sum(r > 10 for r in spec["fd0.7"][best07])))
g["G1p_14"] = dict(arm=best14, ratios=spec["fd1.4"][best14],
                   ok=int(sum(r > 10 for r in spec["fd1.4"][best14])))
g["G1p_spectral"] = bool(g["G1p_07"]["ok"] >= 2 and g["G1p_14"]["ok"] >= 2)
g["texture"] = tex
g["verdict"] = ("PARTIAL REPLICATION" if (g["G1p_spectral"] and g["G2_structure"]
                and not g["G1_entrains"]) else g["verdict"])
out["spectral"] = spec
json.dump(out, open("l68/results_l68.json", "w"), indent=1)
print(f"G1 (1:1 razor lock, registered): {g['G1_entrains']} "
      f"(fast {g['G1_fast_ok']}/3 slow {g['G1_slow_ok']}/3)")
print(f"G1' spectral: 0.7 {best07} {spec['fd0.7'][best07]} ok {g['G1p_07']['ok']}/3"
      f" | 1.4 {best14} {spec['fd1.4'][best14]} ok {g['G1p_14']['ok']}/3")
print(f"G2 structure duty_07 {g['G2_duty07']} ok {g['G2_ok_n']}/3")
print(f"VERDICT: {g['verdict']}")
