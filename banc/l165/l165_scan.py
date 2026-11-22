"""L165 scan: 7-arm x 22-channel PLV_self + evoked-fraction table at 0.100 Hz.

PREREG l165/PREREG.md registered FIRST. Zero rollouts, zero RNG, read-only.
Machinery copied VERBATIM from l162c_phase.py (L85 rule): same WIN/DT/BIN,
same phase_of / plv / evoked-fraction definitions, same CARRIER/CONTROL
derivation from l157/static.json.
"""
import json
import math
import re

import numpy as np

B = "/home/t3rpz/critters/peabrain-lab/banc/"
WIN, DT = 6000, 0.01
BIN_FULL = 6
POOLS = ([f"Ti_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"Tr_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"{j}_{s}" for j in ("Ta", "Pr", "Sr")
            for s in ("aL", "aR", "bL", "bR")])
EXTRA = ["mm", "xm"]
CHANNELS = POOLS + EXTRA
L150_ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5", "eMotBot5"]
assert abs(np.fft.rfftfreq(WIN, DT)[BIN_FULL] - 0.1) < 1e-12, "bin drift"

t = np.arange(WIN) * DT


def phase_of(x):
    return float(np.angle(np.fft.rfft(x - x.mean())[BIN_FULL]))


def plv(ph):
    return float(abs(np.mean(np.exp(1j * np.asarray(ph)))))


# ---- CERT-6 (verbatim l162c) ------------------------------------------------
ev_pinned = plv([phase_of(np.sin(2 * math.pi * 0.1 * t + 0.0)) for _ in range(36)])
ev_free = plv([phase_of(np.sin(2 * math.pi * 0.1 * t + 2 * math.pi * j / 36))
               for j in range(36)])
assert ev_pinned > 0.999, ("CERT-6 pinned", ev_pinned)
assert ev_free < 0.05, ("CERT-6 free", ev_free)
print(f"CERT-6 PASS pinned {ev_pinned:.4f} free {ev_free:.2e}")

# ---- CARRIER/CONTROL re-derived, then asserted vs stored --------------------
l157 = json.load(open(B + "l157/static.json"))
add3 = json.load(open(B + "l162/addendum3.json"))
CARRIER = [c for c in POOLS if l157["pooled"][c]["wilson_lb"] >= 0.5]
CONTROL = [c for c in POOLS if l157["pooled"][c]["below"] <= 6]
assert CARRIER == add3["carrier"], (CARRIER, add3["carrier"])
assert CONTROL == add3["control"], (CONTROL, add3["control"])
assert len(CARRIER) == 8 and len(CONTROL) == 9
print(f"CERT-sets PASS carrier {CARRIER}")
print(f"CERT-sets PASS control {CONTROL}")


def spectra(z, arm, ch, seeds):
    out = []
    for s in seeds:
        x = z[f"{ch}_{arm}_{s}"][:WIN].astype(np.float64)
        out.append(np.fft.rfft(x - x.mean())[BIN_FULL])
    return np.array(out)


def table(path, arms):
    z = np.load(path)
    seeds = sorted(int(m.group(1)) for m in
                   (re.match(r"^mm_b65_(\d+)$", k) for k in z.files) if m)
    res = {}
    for a in arms:
        for ch in CHANNELS:
            Xs = spectra(z, a, ch, seeds)
            ph = np.angle(Xs)
            r = plv(ph)
            res[(a, ch)] = dict(
                plv_self=r,
                circ_sd_deg=(float(math.degrees(math.sqrt(-2 * math.log(r))))
                             if r > 0 else float("inf")),
                evoked=float(abs(Xs.mean()) ** 2 / np.mean(np.abs(Xs) ** 2)),
                ptp=float(np.median([np.ptp(z[f"{ch}_{a}_{s}"][:WIN])
                                     for s in seeds])),
            )
        afs = [float(z[f"af_{a}_{s}"]) for s in seeds]
        res[(a, "__af__")] = dict(af_med=float(np.median(afs)),
                                  af_min=float(min(afs)), af_max=float(max(afs)))
        assert 0.01 < min(afs) and max(afs) < 0.9, ("af range", a, min(afs), max(afs))
    del z
    return res, seeds


T150, SEEDS150 = table(B + "l150/raw_l150.npz", L150_ARMS)
T154, SEEDS154 = table(B + "l154/raw_l154.npz", ["b65", "off"])
print(f"seeds l150 n={len(SEEDS150)} {SEEDS150}")
print(f"seeds l154 n={len(SEEDS154)} {SEEDS154}")

# ---- C0A-165 HALTING anchor -------------------------------------------------
n_anchor = 0
for ch in CHANNELS:
    sp = add3["plv_self"][f"l150/raw_l150.npz|{ch}"]
    assert T150[("b65", ch)]["plv_self"] == sp, ("C0A-165 plv", ch,
                                                 T150[("b65", ch)]["plv_self"], sp)
    se = add3["i5_evoked_fraction"][f"l150/raw_l150.npz|b65|{ch}"]
    assert T150[("b65", ch)]["evoked"] == se, ("C0A-165 ev", ch,
                                               T150[("b65", ch)]["evoked"], se)
    n_anchor += 2
for ch in CHANNELS:
    sp = add3["plv_self"][f"l154/raw_l154.npz|{ch}"]
    assert T154[("b65", ch)]["plv_self"] == sp, ("C0A-165 l154 plv", ch)
    n_anchor += 1
print(f"C0A-165 PASS {n_anchor} stored values reproduced to FLOAT EQUALITY")

# ---- the table --------------------------------------------------------------
def med(arm, T, names, key="plv_self"):
    return float(np.median([T[(arm, c)][key] for c in names]))


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / math.sqrt((ra @ ra) * (rb @ rb)))


rows = {}
b65_vec = [T150[("b65", c)]["plv_self"] for c in CHANNELS]
for a in L150_ARMS:
    vec = [T150[(a, c)]["plv_self"] for c in CHANNELS]
    evec = [T150[(a, c)]["evoked"] for c in CHANNELS]
    rows[a] = dict(
        src="l150",
        carrier_med=med(a, T150, CARRIER),
        control_med=med(a, T150, CONTROL),
        all22_med=float(np.median(vec)),
        mm_plv=T150[(a, "mm")]["plv_self"],
        mm_evoked=T150[(a, "mm")]["evoked"],
        carrier_evoked_med=med(a, T150, CARRIER, "evoked"),
        control_evoked_med=med(a, T150, CONTROL, "evoked"),
        n_carrier_locked=int(sum(T150[(a, c)]["plv_self"] >= 0.8 for c in CARRIER)),
        n_control_locked=int(sum(T150[(a, c)]["plv_self"] >= 0.8 for c in CONTROL)),
        rho_vs_b65=spearman(vec, b65_vec),
        rho_plv_vs_evoked=spearman(vec, evec),
        af_med=T150[(a, "__af__")]["af_med"],
        carrier_ptp_med=med(a, T150, CARRIER, "ptp"),
    )
for a in ["b65", "off"]:
    vec = [T154[(a, c)]["plv_self"] for c in CHANNELS]
    evec = [T154[(a, c)]["evoked"] for c in CHANNELS]
    rows[f"l154_{a}"] = dict(
        src="l154",
        carrier_med=med(a, T154, CARRIER),
        control_med=med(a, T154, CONTROL),
        all22_med=float(np.median(vec)),
        mm_plv=T154[(a, "mm")]["plv_self"],
        mm_evoked=T154[(a, "mm")]["evoked"],
        carrier_evoked_med=med(a, T154, CARRIER, "evoked"),
        control_evoked_med=med(a, T154, CONTROL, "evoked"),
        n_carrier_locked=int(sum(T154[(a, c)]["plv_self"] >= 0.8 for c in CARRIER)),
        n_control_locked=int(sum(T154[(a, c)]["plv_self"] >= 0.8 for c in CONTROL)),
        rho_vs_b65=spearman(vec, b65_vec),
        rho_plv_vs_evoked=spearman(vec, evec),
        af_med=T154[(a, "__af__")]["af_med"],
        carrier_ptp_med=med(a, T154, CARRIER, "ptp"),
    )

print("\narm           carr_med ctl_med lock_c/8 lock_t/9 mm_plv mm_evok "
      "carrE_med rho_b65 af_med ptp_med")
for a, r in rows.items():
    print(f"{a:<13} {r['carrier_med']:.4f}  {r['control_med']:.4f}  "
          f"{r['n_carrier_locked']}/8      {r['n_control_locked']}/9      "
          f"{r['mm_plv']:.3f}  {r['mm_evoked']:.3f}   "
          f"{r['carrier_evoked_med']:.3f}     {r['rho_vs_b65']:+.3f}  "
          f"{r['af_med']:.4f} {r['carrier_ptp_med']:.4f}")

# ---- registered branches ----------------------------------------------------
others = [a for a in L150_ARMS if a != "b65"]
cm = {a: rows[a]["carrier_med"] for a in others}
if all(v >= 0.80 for v in cm.values()):
    branch = "A_GENERIC_LOCK"
elif any(v <= 0.40 for v in cm.values()):
    branch = "A_LESION_SENSITIVE"
else:
    branch = "A_MIXED"
s1 = {a: rows[a]["rho_vs_b65"] for a in others}
s1_pass = {a: bool(v >= 0.70) for a, v in s1.items()}
s2 = {a: bool(rows[a]["control_med"] < rows[a]["carrier_med"]) for a in L150_ARMS}
s2_recruit = {a: bool(rows[a]["control_med"] > 0.8) for a in L150_ARMS}
s3 = {a: bool(rows[a]["rho_plv_vs_evoked"] >= 0.8) for a in rows}
MASS = dict(full=0.0, b65=0.0, eMotTop5=0.0, eMotBot5=0.0,
            cutwA=0.2286, cutng25=0.235, silW=0.2286)
s4 = sorted(((MASS[a], a, rows[a]["carrier_med"]) for a in L150_ARMS))

print(f"\nBRANCH {branch}")
print("S1 pattern invariance rho_vs_b65:",
      {a: round(v, 3) for a, v in s1.items()}, "pass:", s1_pass)
print("S2 control<carrier:", s2, "| control recruited(>.8):", s2_recruit)
print("S3 plv~evoked consistency:", s3)
print("S4 dose (mass_removed, arm, carrier_med):",
      [(m, a, round(v, 4)) for m, a, v in s4])
print(f"\nl154 off pole: carrier_med {rows['l154_off']['carrier_med']:.4f} "
      f"mm_evoked {rows['l154_off']['mm_evoked']:.4f} vs l154 b65 "
      f"carrier_med {rows['l154_b65']['carrier_med']:.4f} "
      f"mm_evoked {rows['l154_b65']['mm_evoked']:.4f}")

# per-channel full table
per_ch = {}
for a in L150_ARMS:
    per_ch[a] = {c: dict(plv=T150[(a, c)]["plv_self"],
                         evoked=T150[(a, c)]["evoked"],
                         sd_deg=T150[(a, c)]["circ_sd_deg"],
                         ptp=T150[(a, c)]["ptp"]) for c in CHANNELS}
for a in ["b65", "off"]:
    per_ch[f"l154_{a}"] = {c: dict(plv=T154[(a, c)]["plv_self"],
                                   evoked=T154[(a, c)]["evoked"],
                                   sd_deg=T154[(a, c)]["circ_sd_deg"],
                                   ptp=T154[(a, c)]["ptp"]) for c in CHANNELS}

print("\nPER-CHANNEL PLV_self (rows=channel, cols=arms l150)")
print(f"{'channel':<9}" + "".join(f"{a:>11}" for a in L150_ARMS) + f"{'l154off':>11}")
for c in CHANNELS:
    line = f"{c:<9}" + "".join(f"{per_ch[a][c]['plv']:>11.4f}" for a in L150_ARMS)
    line += f"{per_ch['l154_off'][c]['plv']:>11.4f}"
    tag = " [C]" if c in CARRIER else (" [n]" if c in CONTROL else "")
    print(line + tag)

out = dict(card="L165 echo-lock dose: 7-arm PLV_self/evoked specificity scan",
           prereg="l165/PREREG.md",
           premise_correction=("l154 'off' removes the MECH SINUSOID, not an "
                               "echo; all 7 l150 arms carry the identical "
                               "sinusoid by construction (l150_run.py "
                               "L885-889/L917-922)"),
           cert6=dict(pinned=ev_pinned, free=ev_free),
           carrier=CARRIER, control=CONTROL,
           seeds_l150=SEEDS150, seeds_l154=SEEDS154,
           anchor_checks=n_anchor,
           rows=rows, branch=branch,
           s1_rho=s1, s1_pass=s1_pass, s2_control_below=s2,
           s2_recruited=s2_recruit, s3_consistency=s3,
           s4_dose=[[m, a, v] for m, a, v in s4],
           per_channel=per_ch)
with open(B + "l165/results_l165.json", "w") as f:
    json.dump(out, f, indent=1)
print("\nwrote l165/results_l165.json")
