"""L197b zero-rollout planning pass on STORED v1 data (banc/l186/raw.npz).
(1) CERT-V1: gj.analyse with v1 parameters reproduces results_l186.json.
(2) Pilot of the short-window readout (W=150) on v1's 16 seeds: seed-level SE.
(3) Power: n needed to resolve a .10 aligned-minus-elapsed difference.
Run from banc/. Writes l197b/pilot.json."""
import json, math, sys
import numpy as np
sys.path.insert(0, "l197b")
import gj

R = json.load(open("l186/results_l186.json"))
raw = np.load("l186/raw.npz")
seeds = R["seeds"]
onsets = {int(k): v for k, v in R["onsets"].items()}
out = {}
v1 = gj.analyse(raw, seeds, onsets, 500, np.arange(-250, 251, 10))
chk = {}
for k in "ATD":
    chk[k] = [v1[k]["value"], R["contrasts"][k]["value"], v1[k]["ci95"], R["contrasts"][k]["ci95"]]
    assert abs(v1[k]["value"] - R["contrasts"][k]["value"]) < 1e-12, k
    assert np.allclose(v1[k]["ci95"], R["contrasts"][k]["ci95"], atol=1e-12), k
for a in ("cutwA", "sc25"):
    for c in ("aligned", "elapsed", "same"):
        assert abs(v1["means"][a][c] - R["means"][a][c]) < 1e-12, (a, c)
    assert np.allclose(np.array(v1["pair_matrices"][a]["aligned"]), np.array(R["ordered_pair_duties"][a])[0], atol=1e-12)
    assert np.allclose(np.array(v1["pair_matrices"][a]["elapsed"]), np.array(R["ordered_pair_duties"][a])[1], atol=1e-12)
t216 = json.load(open("l186/t216_verify.json"))
out["cert_v1"] = dict(status="PASS (A/T/D values + CIs, 6 means, 4 pair matrices == results_l186.json to 1e-12)",
                      tone_instrument_v1=v1["tone_instrument"])
print("CERT-V1 PASS:", {k: round(v1[k]["value"], 4) for k in "ATD"}, "| tone rho", {a: round(v["rho_rot"], 3) for a, v in v1["tone_instrument"].items()})
ov500 = gj.overlap_stats(onsets, seeds, 500)
assert abs(ov500["mean_overlap"] - 0.6209083333333333) < 1e-12
out["v1"] = {k: v1[k] for k in ("A", "T", "D", "T_on", "T_off", "A_inphase", "A_antiphase", "A_in_minus_anti", "means")}
out["v1"]["overlap"] = ov500
# pilot: short window on v1's schedule
pil = {}
for W, starts in ((150, np.arange(-75, 426, 10)), (250, np.arange(-125, 376, 10))):
    p = gj.analyse(raw, seeds, onsets, W, starts)
    pil[str(W)] = {k: p[k] for k in ("A", "T", "D", "T_on", "T_off", "A_inphase", "A_antiphase", "A_in_minus_anti", "means", "tone_instrument")}
    pil[str(W)]["overlap"] = gj.overlap_stats(onsets, seeds, W)
    print(f"pilot W={W}: A {p['A']['value']:+.3f} se {p['A']['se']:.4f} | T {p['T']['value']:+.3f} se {p['T']['se']:.4f} | "
          f"D {p['D']['value']:+.3f} se {p['D']['se']:.4f} | overlap {pil[str(W)]['overlap']['mean_overlap']:.3f} | means {p['means']}")
    print(f"   T_on {p['T_on']['value']:+.3f} (share {p['T_on']['window_share']:.2f}) T_off {p['T_off']['value']:+.3f} | A_in {p['A_inphase']['value']:+.3f} A_anti {p['A_antiphase']['value']:+.3f}")
out["pilot"] = pil


def n_needed(se16, delta=.10, power=.90):
    zb = {.80: 0.8416, .90: 1.2816, .95: 1.6449}[power]
    return math.ceil(16 * (se16 * (1.96 + zb) / delta) ** 2)


pw = {}
for nm, se in (("v1_W500", v1["D"]["se"]), ("pilot_W150", pil["150"]["D"]["se"]), ("pilot_W250", pil["250"]["D"]["se"])):
    pw[nm] = dict(se_D_n16=se, n_power80=n_needed(se, power=.80), n_power90=n_needed(se, power=.90),
                  n_power95=n_needed(se, power=.95),
                  n_halfwidth_le_05=math.ceil(16 * (1.96 * se / .05) ** 2))
    print(nm, pw[nm])
out["power"] = pw
json.dump(out, open("l197b/pilot.json", "w"), indent=1)
