"""L164 verdict: PLV_self / pair-PLV / evoked fraction on the fix vs rnd
arms (PREREG l164/PREREG.md; instruments copied VERBATIM from
l162c_phase.py — phase_of, plv, CARRIER/CONTROL derivation, I2 pair form,
I5 evoked fraction). Zero rollouts, read-only, deterministic.
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
BIN_FULL = 6
ARMS = ["fix", "rnd"]
POOLS = ([f"Ti_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"Tr_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"{j}_{s}" for j in ("Ta", "Pr", "Sr")
            for s in ("aL", "aR", "bL", "bR")])
EXTRA = ["mm", "xm"]
CHANNELS = POOLS + EXTRA
assert abs(np.fft.rfftfreq(WIN, DT)[BIN_FULL] - 0.1) < 1e-12, "CERT-bin"
print("CERT-bin fr[6] == 0.1 to 1e-12: PASS")

t = np.arange(WIN) * DT


def phase_of(x):                      # l162c_phase.py VERBATIM
    return float(np.angle(np.fft.rfft(x - x.mean())[BIN_FULL]))


def plv(ph):                          # l162c_phase.py VERBATIM
    return float(abs(np.mean(np.exp(1j * np.asarray(ph)))))


# ---- CERT-A (l162c CERT-6 VERBATIM, re-scaled to n = 16) -----------------
ev_pinned = plv([phase_of(np.sin(2 * math.pi * 0.1 * t + 0.0))
                 for _ in range(16)])
ev_free = plv([phase_of(np.sin(2 * math.pi * 0.1 * t + 2 * math.pi * j / 16))
               for j in range(16)])
assert ev_pinned > 0.999, ("CERT-A pinned", ev_pinned)
assert ev_free < 0.05, ("CERT-A free", ev_free)
print(f"CERT-A PLV_self separates pinned {ev_pinned:.4f} from free "
      f"{ev_free:.2e}: PASS")

l157 = json.load(open("l157/static.json"))
CARRIER = [c for c in POOLS if l157["pooled"][c]["wilson_lb"] >= 0.5]
CONTROL = [c for c in POOLS if l157["pooled"][c]["below"] <= 6]
assert len(CARRIER) == 8 and len(CONTROL) == 9, (len(CARRIER), len(CONTROL))
assert not (set(CARRIER) & set(CONTROL)), "CERT-sets not disjoint"
CP = [(CARRIER[i], CARRIER[j]) for i in range(8) for j in range(i + 1, 8)]
NP_ = [(CONTROL[i], CONTROL[j]) for i in range(9) for j in range(i + 1, 9)]
print(f"CERT-sets CARRIER {CARRIER}\n          CONTROL {CONTROL}: PASS")

z = np.load("l164/raw_l164.npz")
drv = json.load(open("l164/drive_static.json"))
SEEDS = [int(s) for s in drv["seeds"]]
n = len(SEEDS)
FLOOR = math.sqrt(math.pi / (4 * n))
for a in ARMS:
    for ch in CHANNELS:
        for s in SEEDS:
            assert f"{ch}_{a}_{s}" in z.files, (ch, a, s)
print(f"coverage {len(CHANNELS)} channels x {len(ARMS)} arms x {n} seeds: PASS")
print(f"free-phase PLV floor at n={n}: {FLOOR:.4f}")

X = {}
for a in ARMS:
    for ch in CHANNELS:
        X[(a, ch)] = np.array([
            np.fft.rfft(z[f"{ch}_{a}_{s}"][:WIN].astype(np.float64)
                        - z[f"{ch}_{a}_{s}"][:WIN].astype(np.float64).mean()
                        )[BIN_FULL] for s in SEEDS])

# ---- OP POINT (L30), adapted: the stored `af` is an END-OF-SETTLE snapshot
# taken at a drive phase that the fix protocol pins and the rnd arm frees,
# so af is NOT arm-comparable here. The window-mean motor/mech activity is.
afs = {a: [float(z[f"af_{a}_{s}"]) for s in SEEDS] for a in ARMS}
mmw = {a: [float(z[f"mm_{a}_{s}"][:WIN].mean()) for s in SEEDS] for a in ARMS}
xmw = {a: [float(z[f"xm_{a}_{s}"][:WIN].mean()) for s in SEEDS] for a in ARMS}
OP = {}
for a in ARMS:
    OP[f"af_settle_{a}"] = [float(np.median(afs[a])), float(min(afs[a])),
                            float(max(afs[a]))]
    OP[f"mm_window_{a}"] = [float(np.median(mmw[a])), float(min(mmw[a])),
                            float(max(mmw[a]))]
    OP[f"xm_window_{a}"] = [float(np.median(xmw[a])), float(min(xmw[a])),
                            float(max(xmw[a]))]
    assert all(0.01 < v < 0.9 for v in afs[a]), (a, "af out of band")
OP["mm_window_ratio_rnd_over_fix"] = (OP["mm_window_rnd"][0]
                                      / OP["mm_window_fix"][0])
print("\n--- op point (L30; af = end-of-settle SNAPSHOT, phase-pinned) -----")
for k, v in OP.items():
    print(f"  {k:32s} {v}")

plv_self, ev, amp = {}, {}, {}
for a in ARMS:
    for ch in CHANNELS:
        Xs = X[(a, ch)]
        plv_self[f"{a}|{ch}"] = plv(np.angle(Xs))
        ev[f"{a}|{ch}"] = float(abs(Xs.mean()) ** 2 / np.mean(np.abs(Xs) ** 2))
        amp[f"{a}|{ch}"] = float(np.median(np.abs(Xs)))

pair = {}
for label, pairs in (("carrier", CP), ("control", NP_)):
    for a in ARMS:
        for pa, pb in pairs:
            d = np.angle(X[(a, pa)] * np.conj(X[(a, pb)]))
            r = plv(d)
            pair[f"{label}|{a}|{pa}~{pb}"] = dict(
                n=n, plv=r, rayleigh_p=float(math.exp(-n * r * r)),
                circ_mean_deg=float(np.degrees(
                    np.angle(np.mean(np.exp(1j * d))))),
                locked=bool(r >= 0.5 and math.exp(-n * r * r) < 0.01))


def med_self(a, chs):
    return float(np.median([plv_self[f"{a}|{c}"] for c in chs]))


def med_pair(a, label, pairs):
    return float(np.median([pair[f"{label}|{a}|{x}~{y}"]["plv"]
                            for x, y in pairs]))


M = dict(
    self_carrier_fix=med_self("fix", CARRIER),
    self_carrier_rnd=med_self("rnd", CARRIER),
    self_control_fix=med_self("fix", CONTROL),
    self_control_rnd=med_self("rnd", CONTROL),
    pair_carrier_fix=med_pair("fix", "carrier", CP),
    pair_carrier_rnd=med_pair("rnd", "carrier", CP),
    pair_control_fix=med_pair("fix", "control", NP_),
    pair_control_rnd=med_pair("rnd", "control", NP_),
)
n_locked = {f"{lab}|{a}": int(sum(pair[f"{lab}|{a}|{x}~{y}"]["locked"]
                                  for x, y in prs))
            for lab, prs in (("carrier", CP), ("control", NP_))
            for a in ARMS}

pos_ok = M["self_carrier_fix"] >= 0.8
if not pos_ok:
    branch = "VOID_positive_control_failed"
elif M["self_carrier_rnd"] >= 0.4:
    branch = "B_NOT_FREED"
elif M["pair_carrier_rnd"] >= 0.8:
    branch = "B_SHARED"
elif M["pair_carrier_rnd"] < 0.8:
    branch = "B_INDEPENDENT"
else:
    branch = "B_MIXED"

print("\n--- PLV_self per channel (bin-6 phase reproducibility) -----------")
print(f"{'channel':10s} {'set':8s} {'fix':>8s} {'rnd':>8s} {'ev_fix':>8s} "
      f"{'ev_rnd':>8s} {'|X|_fix':>9s} {'|X|_rnd':>9s}")
for ch in CHANNELS:
    tag = ("CARRIER" if ch in CARRIER else
           "control" if ch in CONTROL else "-")
    print(f"{ch:10s} {tag:8s} {plv_self['fix|'+ch]:8.3f} "
          f"{plv_self['rnd|'+ch]:8.3f} {ev['fix|'+ch]:8.3f} "
          f"{ev['rnd|'+ch]:8.3f} {amp['fix|'+ch]:9.3g} {amp['rnd|'+ch]:9.3g}")

print("\n--- carrier pair PLV (phase RELATION across rollouts) ------------")
print(f"{'pair':24s} {'fix':>8s} {'rnd':>8s} {'p_rnd':>10s}")
for x, y in CP:
    pf = pair[f"carrier|fix|{x}~{y}"]
    pr = pair[f"carrier|rnd|{x}~{y}"]
    print(f"{x+'~'+y:24s} {pf['plv']:8.3f} {pr['plv']:8.3f} "
          f"{pr['rayleigh_p']:10.2e}")

print("\n--- medians -------------------------------------------------------")
for k, v in M.items():
    print(f"  {k:22s} {v:.4f}")
print(f"  locked pairs: {n_locked}")
print(f"\nfree-phase floor (n={n}) {FLOOR:.4f} | drive PLV rnd "
      f"{drv['d2_plv_drive_rnd']:.4f}")
print(f"positive control (fix carrier PLV_self >= .8): "
      f"{'PASS' if pos_ok else 'FAIL'}")
print(f"BRANCH: {branch}")

json.dump(dict(card="L164 slow-line origin rollout arm", seeds=SEEDS, n=n,
               floor=FLOOR, carrier=CARRIER, control=CONTROL,
               op_point=OP,
               plv_self=plv_self, evoked=ev, med_abs=amp, pair=pair,
               medians=M, n_locked=n_locked,
               positive_control_pass=bool(pos_ok), branch=branch,
               drive_plv_rnd=drv["d2_plv_drive_rnd"],
               offsets=drv["offsets"]),
          open("l164/results.json", "w"), indent=1)
print("\nl164/results.json written")
