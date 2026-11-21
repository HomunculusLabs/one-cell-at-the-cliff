"""L35 verdict recompute (tick 52) — the run data in results_l35.json is valid;
the IN-SCRIPT analysis had three bugs, caught on the log before any claim:

(a) `amp_deg, mean_at, per_at = max(curve, ...)` unpacks (phi, mean_dphi,
    per_seed) into swapped names -> logged "amplitude"/"bin" are exchanged,
    and C4's rows_hi filtered phi==mean_at -> empty early/late lists.
(b) C2's frequency leg compared f_post (post-window FLEXOR dom freq) against
    the control's FULL-WINDOW flexor freq (ripple-prone; seed 33 flexor ripple
    3.465 Hz) instead of the control's POST-window freq (prereg wording).
(c) dng100pulse arms are all dm_mm==0 (bit-identical, volley absorbed by the
    clamp ceiling) -> their dphi is EXACTLY 0; any nonzero-looking PRC for
    them would be angle-of-noise (with the swap it reads as "amplitude 180").

This script recomputes C2/C3/C4 from the saved arms + traces with the
corrections, labels absorbed arms, and emits l35/verdict_l35.json.
Honesty note: gates were frozen in PREREG; this pass fixes INSTRUMENT reading
errors, it does not move claim levels. C2 freq leg reported BOTH as-coded
(flexor, full-window ctrl) and amendment-3-consistent (motor-mean, matched
post window) - labeled, not cherry-picked.
"""
import json

import numpy as np

DT = 0.01
WIN = 6000
MEAS0 = 1500
SEEDS = [11, 22, 33]
NBINS = 8


def dom_freq(x, lo=0.5, hi=10.0):
    z = x - x.mean()
    ps = np.abs(np.fft.rfft(z)) ** 2
    fr = np.fft.rfftfreq(len(z), DT)
    band = (fr >= lo) & (fr <= hi)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    ratio = float(pb.max() / max(np.median(pb), 1e-30))
    return float(f_hat), ratio


r = json.load(open("l35/results_l35.json"))
tr = np.load("l35/traces.npz")
arms = r["arms"]
ctrl_f_flx_full = {int(s): r["ctrl"][s]["f_flx"] for s in r["ctrl"]}
ctrl_f_mm_full = {int(s): r["ctrl"][s]["f"] for s in r["ctrl"]}

# control post-window freqs matched to each arm's volley end (ke)
cache = {}


def ctrl_post(seed, ke, chan):
    key = (seed, ke, chan)
    if key not in cache:
        sig = tr[f"ctrl_{seed}" if chan == "flx" else f"ctrl_{seed}_mm"]
        f, _ = dom_freq(sig[ke + 50:])
        cache[key] = f
    return cache[key]


# ---------------- C2 (survival), corrected ----------------
c2_rows = []
for a in arms:
    if a["tag"] not in ("dng95", "dng100pulse", "dng95_dur100"):
        continue
    s, ke = a["seed"], a["k0"] + a["vsteps"]
    legs = dict(ratio=a["ratio_post"] >= 10, S=a["S_post"] >= 0.30)
    # as-coded (flexor vs full-window ctrl flexor)
    legs["freq_as_coded"] = abs(a["f_post"] - ctrl_f_flx_full[s]) <= 0.15
    # corrected: flexor post vs ctrl post (matched window)
    legs["freq_flx_post"] = abs(a["f_post"] - ctrl_post(s, ke, "flx")) <= 0.15
    # amendment-3-consistent: motor-mean rhythm
    f_mm_post, _ = dom_freq(tr[f"{a['tag']}_s{s}_phi{int(a['phi'])}_mm"][ke + 50:]) \
        if f"{a['tag']}_s{s}_phi{int(a['phi'])}_mm" in tr.files else (np.nan, 0)
    if not np.isnan(f_mm_post):
        legs["freq_mm_post"] = abs(f_mm_post - ctrl_post(s, ke, "mm")) <= 0.15
    c2_rows.append(dict(tag=a["tag"], seed=s, phi=a["phi"], vamp=a["vamp"],
                        vsteps=a["vsteps"], absorbed=a["dm_mm"] == 0.0,
                        legs=legs, f_post=a["f_post"],
                        f_ctrl_flx_full=ctrl_f_flx_full[s],
                        f_ctrl_flx_post=ctrl_post(s, ke, "flx"),
                        f_ctrl_mm_post=ctrl_post(s, ke, "mm"),
                        f_mm_post=None if np.isnan(f_mm_post) else f_mm_post))


def leg_summary(name):
    fails = [(c["tag"], c["seed"], c["phi"]) for c in c2_rows if not c["legs"].get(name, True)]
    return dict(n_fail=len(fails), fails=fails[:8],
                pass_all=bool(not fails))


c2 = {leg: leg_summary(leg) for leg in
      ("ratio", "S", "freq_as_coded", "freq_flx_post", "freq_mm_post")}

# ---------------- C3 (PRC), corrected ----------------
def prc(chan, amp):
    rows = [a for a in arms if a["tag"] == chan and a["vamp"] == amp
            and a["vsteps"] == 25]
    curve, absorbed_bins = [], []
    for b in range(NBINS):
        per = [a for a in rows if a["phi"] == b * 45.0]
        n_abs = sum(1 for a in per if a["dm_mm"] == 0.0)
        absorbed_bins.append(n_abs)
        curve.append((b * 45.0, float(np.mean([a["dphi"] for a in per])),
                      [a["dphi"] for a in per]))
    bin_phi, mean_dphi, per_at = max(curve, key=lambda c: abs(c[1]))
    signs = [np.sign(x) for x in per_at]
    return dict(argmax_bin=bin_phi, prc_amplitude=abs(float(mean_dphi)),
                per_seed_at_argmax=per_at, sign_consistent=len(set(signs)) == 1,
                n_absorbed_per_bin=absorbed_bins,
                curve=[(float(p), float(m)) for p, m, _ in curve])


sham_rows = [a for a in arms if a["tag"].startswith("sham")]
sham_means = {s: abs(float(np.mean([a["dphi"] for a in sham_rows if a["seed"] == s])))
              for s in SEEDS}
sham_max = float(max(sham_means.values()))
sham_single_max = float(max(abs(a["dphi"]) for a in sham_rows))

prc_c = {}
for chan in ("dng95", "dng100pulse"):
    for amp in (0.05, 0.15):
        p = prc(chan, amp)
        key = f"{chan}_A{amp}"
        prc_c[key] = p
        p["gate_amp10"] = p["prc_amplitude"] >= 10.0
        p["gate_3xsham"] = p["prc_amplitude"] >= 3 * sham_max
        p["gate_sign"] = p["sign_consistent"]
        p["passes"] = p["gate_amp10"] and p["gate_3xsham"] and p["gate_sign"]

# ---------------- C4 (dose + persistence), corrected ----------------
c4 = {}
for chan in ("dng95", "dng100pulse"):
    hi, lo = prc_c[f"{chan}_A0.15"], prc_c[f"{chan}_A0.05"]
    rows_hi = [a for a in arms if a["tag"] == chan and a["vamp"] == 0.15
               and a["vsteps"] == 25 and a["phi"] == hi["argmax_bin"]]
    c4[chan] = dict(
        dose_monotone=bool(hi["prc_amplitude"] >= lo["prc_amplitude"]),
        amp05=lo["prc_amplitude"], amp15=hi["prc_amplitude"],
        argmax_bin=hi["argmax_bin"],
        dphi_early=[a["dphi_early"] for a in rows_hi],
        dphi_late=[a["dphi_late"] for a in rows_hi],
        dm=[a["dm_mm"] for a in rows_hi])
dur = {str(int(p)): dict(
    dur100=[a["dphi"] for a in arms if a["tag"] == "dng95_dur100" and a["phi"] == p],
    dur25=[a["dphi"] for a in arms if a["tag"] == "dng95" and a["vamp"] == 0.15
           and a["vsteps"] == 25 and a["phi"] == p]) for p in (0.0, 180.0)}
c4["dur"] = dur

absorbed_counts = {
    f"{c}_A{a}": sum(1 for x in arms if x["tag"] == c and x["vamp"] == a
                     and x["vsteps"] == 25 and x["dm_mm"] == 0.0)
    for c in ("dng95", "dng100pulse") for a in (0.05, 0.15)}

out = dict(c2=c2, c2_rows=c2_rows, prc=prc_c, c4=c4,
           sham=dict(per_seed_mean=sham_means, max_mean=sham_max,
                     single_max=sham_single_max),
           absorbed_arms=absorbed_counts,
           n_arms=len(arms))
json.dump(out, open("l35/verdict_l35.json", "w"), indent=1)

print("== corrected verdict ==")
print("C2 legs:", json.dumps({k: v["n_fail"] for k, v in c2.items()}))
for k, v in c2.items():
    if v["n_fail"]:
        print(f"  C2 {k}: {v['n_fail']} fails e.g. {v['fails'][:4]}")
for k, p in prc_c.items():
    print(f"C3 {k}: amp {p['prc_amplitude']:.1f} deg @ bin {p['argmax_bin']:.0f} "
          f"| per-seed {['%+.0f' % x for x in p['per_seed_at_argmax']]} "
          f"| absorbed/bin {p['n_absorbed_per_bin']} "
          f"| amp10 {p['gate_amp10']} 3xsham({3*sham_max:.1f}) {p['gate_3xsham']} "
          f"sign {p['gate_sign']} -> {'PASS' if p['passes'] else 'FAIL'}")
print(f"sham: per-seed |mean| {['%.1f' % sham_means[s] for s in SEEDS]} "
      f"max {sham_max:.1f} single {sham_single_max:.1f}")
print("absorbed arms (dm==0 of 24 each):", absorbed_counts)
for chan in ("dng95", "dng100pulse"):
    c = c4[chan]
    print(f"C4 {chan}: dose {c['amp05']:.1f}->{c['amp15']:.1f} mono {c['dose_monotone']} "
          f"@ bin {c['argmax_bin']:.0f} | early {['%+.0f' % x for x in c['dphi_early']]} "
          f"| late {['%+.0f' % x for x in c['dphi_late']]} | dm {['%.1e' % x for x in c['dm']]}")
print("C4 dur:", json.dumps({k: {kk: [round(x) for x in vv] for kk, vv in v.items()}
                             for k, v in dur.items()}))
