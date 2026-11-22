"""L199 instrument self-test on SYNTHETIC traces only (no lab data is read).
Plants a flexor-minus-extensor tone-phase difference Delta into sinusoid pools
gated by an S-law jittered pulse and checks that Part B recovers
theta = Delta + 180, Part C recovers Delta, and Part A's slope sign matches.
Also checks Part D's block algebra on a planted tone flip. Run from banc/."""
import json, math, sys
import numpy as np
sys.path.insert(0, "l199")
import ph
gj = ph.gj

PHI = ph.tone_phi()
rng = np.random.default_rng(199)
n, pulse, W, starts = 24, 500, 150, gj.starts_of("S")
res = {}
ok = True
for Dl in (0.0, 180.0, 90.0, -60.0):
    raw, ons = {}, {}
    for s in range(n):
        o = [int(x) for x in rng.integers(600, 1201, 2)]
        ons[s] = [o[0], 4000 + o[1]]
        gate = np.zeros(6000, bool)
        for a in ons[s]:
            gate[a:a + pulse] = True
        raw[f"gate_{s}"] = gate
        af = rng.normal(40, 8)
        for g, d in (("cutwA", Dl), ("sc25", Dl + 70.0)):
            raw[f"Ti_fR_{g}_{s}"] = (.3 + gate * .1 * np.cos(PHI - math.radians(af)) + rng.normal(0, .02, 6000)).astype(np.float32)
            raw[f"Ti_eR_{g}_{s}"] = (.3 + gate * .1 * np.cos(PHI - math.radians(af - d)) + rng.normal(0, .02, 6000)).astype(np.float32)
    seeds = list(range(n))
    h, lag = ph.seg_duty(raw, seeds, ons, W, starts)
    A, B, C = ph.part_a(h, lag), ph.part_b(h, lag), ph.part_c(raw, seeds, ons, pulse, PHI)
    for g, d in (("cutwA", Dl), ("sc25", Dl + 70.0)):
        th, De = B["graphs"][g]["theta"]["value"], C[g]["Delta"]["mean_deg"]
        e1, e2 = abs(float(ph.wrap(th - (d + 180)))), abs(float(ph.wrap(De - d)))
        good = e1 < 12 and e2 < 5
        ok &= good
        res[f"{Dl}:{g}"] = dict(planted=d, theta=th, theta_err=e1, Delta=De, Delta_err=e2, slope=A["slope"][g]["value"], ok=good)
        print(f"planted Delta {d:+6.1f} [{g}]: theta {th:+7.1f} (err {e1:.1f}) | direct Delta {De:+7.1f} (err {e2:.1f}) | 3-bin slope {A['slope'][g]['value']:+.3f}")
    assert abs(float(ph.wrap(B["dtheta"]["value"] - 70.0))) < 15, B["dtheta"]
# slope sign: co-move (Delta 0) -> negative; alternate (180) -> positive
ok &= res["0.0:cutwA"]["slope"] < -.3 and res["180.0:cutwA"]["slope"] > .3
# Part D block algebra: co-moving pools, phiPI tags see the flipped tone
nb = 8
raw, tags = {}, list(range(nb)) + [50000 + k for k in range(nb)]
for t in tags:
    gate = np.zeros(6000, bool); gate[900:1400] = True; gate[4900:5400] = True
    raw[f"gate_{t}"] = gate
    sh = math.pi if t >= 50000 else 0.0
    for g, d in (("cutwA", 0.0), ("sc25", 180.0)):
        raw[f"Ti_fR_{g}_{t}"] = (.3 + gate * .1 * np.cos(PHI + sh - .5) + rng.normal(0, .02, 6000)).astype(np.float32)
        raw[f"Ti_eR_{g}_{t}"] = (.3 + gate * .1 * np.cos(PHI + sh - .5 + math.radians(d)) + rng.normal(0, .02, 6000)).astype(np.float32)
h, lag = ph.seg_duty(raw, tags, {t: [900, 4900] for t in tags}, W, starts)
assert not lag.any()
Dd = ph.part_d(h, nb)
print("Part D synthetic:", {g: {k: round(v, 3) for k, v in Dd["blocks"][g].items()} for g in ph.GRAPHS}, "K", {g: round(Dd["K"][g]["value"], 3) for g in ph.GRAPHS}, "K_I", round(Dd["K_I"]["value"], 3), Dd["label"])
ok &= Dd["K"]["cutwA"]["value"] < -.8 and Dd["K"]["sc25"]["value"] > .8 and Dd["label"] == "CA1_sign"
res["part_d"] = dict(K={g: Dd["K"][g]["value"] for g in ph.GRAPHS}, label=Dd["label"])
res["pass"] = bool(ok)
json.dump(res, open("l199/selftest.json", "w"), indent=1)
print("SELFTEST", "PASS" if ok else "FAIL")
assert ok
