# L162 ADDENDUM-3 instruments: I4' per-channel phase reproducibility
# (PLV_self), I5 evoked fraction, I6 within-rollout coherence vs the
# dead-pool arm + analytic 1/K floor. Registered in l162/PREREG.md
# ADDENDUM 3 BEFORE this output (I4 withdrawn by its own CERT-5).
# Zero rollouts, read-only, deterministic (no RNG).
import json
import math
import re

import numpy as np

WIN, DT = 6000, 0.01
SEG, HOP = 2000, 1000
BIN_FULL, BIN_SEG = 6, 2
FILES = ["l154/raw_l154.npz", "l150/raw_l150.npz"]
POOLS = ([f"Ti_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"Tr_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"{j}_{s}" for j in ("Ta", "Pr", "Sr")
            for s in ("aL", "aR", "bL", "bR")])
EXTRA = ["mm", "xm"]
CHANNELS = POOLS + EXTRA
ARMS = {"l154/raw_l154.npz": ["b65", "off"], "l150/raw_l150.npz": ["b65"]}
K = len(range(0, WIN - SEG + 1, HOP))
FLOOR = 1.0 / K
assert abs(np.fft.rfftfreq(WIN, DT)[BIN_FULL] - 0.1) < 1e-12

# ---- CERT-6 analytic self-test for PLV_self (the NEW instrument) -----------
t = np.arange(WIN) * DT


def phase_of(x):
    return float(np.angle(np.fft.rfft(x - x.mean())[BIN_FULL]))


def plv(ph):
    return float(abs(np.mean(np.exp(1j * np.asarray(ph)))))


ev_pinned = plv([phase_of(np.sin(2 * math.pi * 0.1 * t + 0.0))
                 for _ in range(36)])
ev_free = plv([phase_of(np.sin(2 * math.pi * 0.1 * t + 2 * math.pi * j / 36))
               for j in range(36)])
assert ev_pinned > 0.999, ("CERT-6 pinned", ev_pinned)
assert ev_free < 0.05, ("CERT-6 free", ev_free)
print(f"CERT-6 PLV_self separates pinned {ev_pinned:.4f} from "
      f"free-running {ev_free:.2e}: PASS")

l157 = json.load(open("l157/static.json"))
l162 = json.load(open("l162/static.json"))
CARRIER = [c for c in POOLS if l157["pooled"][c]["wilson_lb"] >= 0.5]
CONTROL = [c for c in POOLS if l157["pooled"][c]["below"] <= 6]
assert len(CARRIER) == 8 and len(CONTROL) == 9
CP = [(CARRIER[i], CARRIER[j]) for i in range(8) for j in range(i + 1, 8)]
NP_ = [(CONTROL[i], CONTROL[j]) for i in range(9) for j in range(i + 1, 9)]

# ---- I4' + I5 --------------------------------------------------------------
PH, EV, seeds = {}, {}, {}
for f in FILES:
    z = np.load(f)
    ss = sorted(int(m.group(1)) for m in
                (re.match(r"^mm_b65_(\d+)$", k) for k in z.files) if m)
    seeds[f] = ss
    for a in ARMS[f]:
        for ch in CHANNELS:
            Xs = np.array([np.fft.rfft(
                z[f"{ch}_{a}_{s}"][:WIN].astype(np.float64)
                - z[f"{ch}_{a}_{s}"][:WIN].astype(np.float64).mean()
            )[BIN_FULL] for s in ss])
            PH[(f, a, ch)] = np.angle(Xs)
            EV[(f, a, ch)] = float(abs(Xs.mean()) ** 2
                                   / np.mean(np.abs(Xs) ** 2))
    del z

plv_self, circ_sd = {}, {}
for ch in CHANNELS:
    for f in FILES:
        p = PH[(f, "b65", ch)]
        r = plv(p)
        plv_self[f"{f}|{ch}"] = r
        circ_sd[f"{f}|{ch}"] = (float(math.degrees(math.sqrt(-2 * math.log(r))))
                                if r > 0 else float("inf"))
    pp = np.concatenate([PH[(f, "b65", ch)] for f in FILES])
    plv_self[f"pooled|{ch}"] = plv(pp)

med_plv_self = {f: float(np.median([plv_self[f"{f}|{c}"] for c in CARRIER]))
                for f in FILES}
med_plv_ctl = {f: float(np.median([plv_self[f"{f}|{c}"] for c in CONTROL]))
               for f in FILES}
if all(v >= 0.8 for v in med_plv_self.values()):
    ecls = "E1_evoked_dichotomy_not_expressed"
elif all(v <= 0.4 for v in med_plv_self.values()):
    ecls = "E2_induced_shared_clock_claimable"
else:
    ecls = "E3_mixed"

# ---- I6 from the stored l162 I1 table (matched arm only) -------------------
def matched(label, pa, pb):
    return l162["i1_pooled"][f"{label}|{pa}~{pb}"]["msc_matched_med"]


car_vals = [matched("carrier", a, b) for a, b in CP]
ctl_vals = [matched("control", a, b) for a, b in NP_]
n_clear_f = sum(v >= 0.5 for v in car_vals)
n_clear_f_ctl = sum(v >= 0.5 for v in ctl_vals)
car_med, ctl_med = float(np.median(car_vals)), float(np.median(ctl_vals))
calib_ok = bool(0.5 * FLOOR <= ctl_med <= 2.0 * FLOOR)
per_file_f = {}
for f in FILES:
    cv = [l162["i1"][f"carrier|{f}|b65"][f"{a}~{b}"]["msc_matched_med"]
          for a, b in CP]
    nv = [l162["i1"][f"control|{f}|b65"][f"{a}~{b}"]["msc_matched_med"]
          for a, b in NP_]
    per_file_f[f] = dict(n_clear_f=int(sum(v >= 0.5 for v in cv)),
                         n_clear_f_control=int(sum(v >= 0.5 for v in nv)),
                         med_carrier=float(np.median(cv)),
                         med_control=float(np.median(nv)))
f_same = (per_file_f[FILES[0]]["n_clear_f"] >= 22) == \
         (per_file_f[FILES[1]]["n_clear_f"] >= 22)
if n_clear_f >= 22 and car_med >= 2 * ctl_med and calib_ok:
    fcls = "F1_carrier_coherent"
elif n_clear_f <= 7:
    fcls = "F2_not_coherent"
else:
    fcls = "F3_mixed"

out = dict(card="L162 ADDENDUM 3: I4' PLV_self + I5 evoked + I6 vs floor",
           cert6=dict(pinned=ev_pinned, free=ev_free),
           carrier=CARRIER, control=CONTROL, floor_1_over_K=FLOOR,
           plv_self=plv_self, circ_sd_deg=circ_sd,
           i5_evoked_fraction={f"{f}|{a}|{ch}": EV[(f, a, ch)]
                               for (f, a, ch) in EV},
           e_axis=dict(cls=ecls, med_plv_self_carrier=med_plv_self,
                       med_plv_self_control=med_plv_ctl),
           f_axis=dict(cls=fcls, n_clear_f=int(n_clear_f),
                       n_clear_f_control=int(n_clear_f_ctl),
                       med_carrier=car_med, med_control=ctl_med,
                       calibration_ok=calib_ok, per_file=per_file_f,
                       both_files_same_side=bool(f_same),
                       label="DESCRIPTIVE-STRONG (post-hoc recombination "
                             "of pre-registered components; no draft fold "
                             "this tick per ADDENDUM 3)"),
           fold_draft=False)
json.dump(out, open("l162/addendum3.json", "w"), indent=1)

print(f"\nE axis: {ecls} — median carrier PLV_self "
      f"{med_plv_self[FILES[0]]:.4f} / {med_plv_self[FILES[1]]:.4f} "
      f"(control {med_plv_ctl[FILES[0]]:.4f} / {med_plv_ctl[FILES[1]]:.4f})")
print(f"F axis: {fcls} (DESCRIPTIVE-STRONG) — clears-f {n_clear_f}/28 carrier "
      f"vs {n_clear_f_ctl}/36 control; med MSC {car_med:.3f} vs {ctl_med:.3f}; "
      f"analytic floor 1/K={FLOOR:.3f}; calibration_ok={calib_ok}; "
      f"both files same side: {f_same}")
for f in FILES:
    v = per_file_f[f]
    print(f"  {f}: clears-f {v['n_clear_f']}/28 (control "
          f"{v['n_clear_f_control']}/36) med {v['med_carrier']:.3f} vs "
          f"{v['med_control']:.3f}")
print("\nper-channel PLV_self at .100 Hz (36 pooled b65 seeds) + evoked frac:")
for ch in CHANNELS:
    tag = ("CARRIER" if ch in CARRIER else
           "control" if ch in CONTROL else "aggreg.")
    print(f"  {ch:5s} {tag} plv_self pooled {plv_self[f'pooled|{ch}']:.4f} "
          f"| l154 {plv_self[f'{FILES[0]}|{ch}']:.4f} "
          f"l150 {plv_self[f'{FILES[1]}|{ch}']:.4f} | ev "
          f"{EV[(FILES[0], 'b65', ch)]:.3f}/{EV[(FILES[1], 'b65', ch)]:.3f} "
          f"| circ_sd {circ_sd[f'{FILES[0]}|{ch}']:.1f} deg")
print(f"\noff-arm (descriptive): carrier med PLV_self "
      f"{np.median([plv([*PH[(FILES[0], 'off', c)]]) for c in CARRIER]):.4f}, "
      f"mm ev {EV[(FILES[0], 'off', 'mm')]:.3f}")
print("l162/addendum3.json written")
