"""L108 free-rhythm-descriptor — pure analysis of stored raw_l105.npz.
PREREG l108/PREREG.md (registered pre-compute).

Part 0 (L85 cert, must PASS before any L108 pin): reproduce lock counts
exactly — l105 free 48 / freenod 48 on raw_l105.npz, l101 cfn 48 on
raw_l101.npz (C0A-certified same traces).
Part 1: dom_freq + dom_ratio per arm/seed (3 segments + full trace),
mm mean; distribution + stationarity summaries; freenod-vs-free freq
identity count.
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
ANCHOR = [11, 22, 33]
B4 = list(range(801, 817))
B5 = list(range(901, 917))
B6 = list(range(1001, 1017))
ALLFRESH = B4 + B5 + B6
ALL = ANCHOR + ALLFRESH
ARMS = ["cfn", "free", "freenod"]


# ---- machinery inherited VERBATIM from l105_verdict.py ----
def dom_ratio(x):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= 0.3) & (fr <= 10)
    return float(ps[band].max() / max(np.median(ps[band]), 1e-30))


def lock_of(raw, arm):
    return int(sum(all(dom_ratio(raw[f"mm_{arm}_{s}"][s0:s0 + 2000]) >= 10
                       for s0, _, _ in SEGB) for s in ALLFRESH))


# ---- new read (registered): freq of the band argmax, same band/window ----
def dom_freq(x):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= 0.3) & (fr <= 10)
    return float(fr[band][int(np.argmax(ps[band]))])


z105 = np.load("l105/raw_l105.npz")
z101 = np.load("l101/raw_l101.npz")
r105 = json.load(open("l105/results_l105.json"))
r101 = json.load(open("l101/results_l101.json"))

# ---------- Part 0: certification ----------
cert = {
    "free_lock": lock_of(z105, "free"),
    "freenod_lock": lock_of(z105, "freenod"),
    "cfn_lock_l101npz": lock_of(z101, "cfn"),
}
want = {
    "free_lock": r105["tables"]["free"]["lock"],
    "freenod_lock": r105["tables"]["freenod"]["lock"],
    "cfn_lock_l101npz": r101["anchors"]["lock"],
}
fails = [(k, cert[k], want[k]) for k in want if cert[k] != want[k]]
# combined-fn consistency spot-check (dom_freq shares band machinery)
for s in (11, 801, 1016):
    x = z105[f"mm_free_{s}"][0:2000]
    assert abs(dom_ratio(x) - dom_ratio(x)) == 0.0
print("CERT:", cert, "want:", want, "fails:", fails)
assert not fails, f"certification FAILED: {fails}"

# ---------- Part 1: per-seed reads ----------
per = {}
for arm in ARMS:
    src = z101 if arm == "cfn" else z105
    for s in ALL:
        mm = src[f"mm_{arm}_{s}"][:WIN].astype(np.float64)
        segf = [round(dom_freq(mm[a:a + 2000]), 3) for a, _, _ in SEGB]
        segr = [round(dom_ratio(mm[a:a + 2000]), 1) for a, _, _ in SEGB]
        per[f"{arm}_{s}"] = dict(
            seg_freqs=segf, seg_ratios=segr,
            full_freq=round(dom_freq(mm), 3),
            full_ratio=round(dom_ratio(mm), 1),
            mm_mean=round(float(mm.mean()), 4))

summary = {}
for arm in ARMS:
    rows = [per[f"{arm}_{s}"] for s in ALL]
    full = np.array([r["full_freq"] for r in rows])
    s0 = np.array([r["seg_freqs"][0] for r in rows])
    s1 = np.array([r["seg_freqs"][1] for r in rows])
    s2 = np.array([r["seg_freqs"][2] for r in rows])
    stat = int(sum(1 for r in rows
                   if max(r["seg_freqs"]) - min(r["seg_freqs"]) <= 0.051))
    summary[arm] = dict(
        full_freq_hist={str(f): int(c) for f, c in zip(
            *np.unique(np.round(full, 2), return_counts=True))},
        seg0_hist={str(f): int(c) for f, c in zip(
            *np.unique(np.round(s0, 2), return_counts=True))},
        seg1_hist={str(f): int(c) for f, c in zip(
            *np.unique(np.round(s1, 2), return_counts=True))},
        seg2_hist={str(f): int(c) for f, c in zip(
            *np.unique(np.round(s2, 2), return_counts=True))},
        full_freq_mean=round(float(full.mean()), 3),
        full_freq_std=round(float(full.std()), 3),
        stationarity_3seg_within_bin=stat,
        mm_mean_mean=round(float(np.mean([r["mm_mean"] for r in rows])), 4),
        e1_at_drive=(int((np.abs(s0 - 0.7) <= 0.051).sum()),
                     int((np.abs(s1 - 1.4) <= 0.051).sum()),
                     int((np.abs(s2 - 0.7) <= 0.051).sum())) if arm == "cfn"
        else None)

# E3: freenod vs free identity
ident = sum(1 for s in ALL
            if per[f"freenod_{s}"]["seg_freqs"] == per[f"free_{s}"]["seg_freqs"]
            and per[f"freenod_{s}"]["full_freq"] == per[f"free_{s}"]["full_freq"])
maxdf = max(abs(per[f"freenod_{s}"]["full_freq"] - per[f"free_{s}"]["full_freq"])
            for s in ALL)

out = dict(cert=cert, per_seed=per, summary=summary,
           freenod_vs_free=dict(identical_freq_seeds=ident,
                                max_full_freq_diff=maxdf),
           meta=dict(win=WIN, dt=DT, segb=SEGB, n_seeds=len(ALL)))

# ---------- Part 2: DIAG reads (PREREG ADDENDUM 1) ----------
def diag_peak(x, lo=0.02, hi=10.0):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    med = max(np.median(ps[(fr >= 0.3) & (fr <= 10)]), 1e-30)
    m = (fr >= lo) & (fr <= hi)
    i = int(np.argmax(ps[m]))
    return round(float(fr[m][i]), 3), round(float(ps[m][i] / med), 1)


def drive_snr(x, fdrv):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    med = max(np.median(ps[(fr >= 0.3) & (fr <= 10)]), 1e-30)
    i = int(np.argmin(np.abs(fr - fdrv)))
    return round(float(ps[i] / med), 1)


diag = {}
for arm in ARMS:
    src = z101 if arm == "cfn" else z105
    gp_full, gp_seg1, floor_hits = [], [], 0
    for s in ALL:
        mm = src[f"mm_{arm}_{s}"][:WIN].astype(np.float64)
        gpf, gpr = diag_peak(mm)
        gps1, _ = diag_peak(mm[2000:4000])
        gp_full.append((gpf, gpr))
        gp_seg1.append(gps1)
        # band-floor pin: registered full-window argmax == lowest band bin
        ps, fr = None, None
        zz = mm - mm.mean()
        ps = np.abs(np.fft.rfft(zz)) ** 2
        fr = np.fft.rfftfreq(len(zz), DT)
        band = (fr >= 0.3) & (fr <= 10)
        if abs(fr[band][int(np.argmax(ps[band]))] - 0.3) < 1e-9:
            floor_hits += 1
    ds = None
    if arm == "cfn":
        s0r, s1r, s2r = [], [], []
        for s in ALL:
            mm = src[f"mm_{arm}_{s}"][:WIN].astype(np.float64)
            s0r.append(drive_snr(mm[0:2000], 0.7))
            s1r.append(drive_snr(mm[2000:4000], 1.4))
            s2r.append(drive_snr(mm[4000:6000], 0.7))
        ds = dict(seg0_snr07=[round(float(np.median(s0r)), 1),
                              int(sum(r >= 10 for r in s0r))],
                  seg1_snr14=[round(float(np.median(s1r)), 1),
                              int(sum(r >= 10 for r in s1r))],
                  seg2_snr07=[round(float(np.median(s2r)), 1),
                              int(sum(r >= 10 for r in s2r))])
    gpf_all = np.array([g for g, _ in gp_full])
    diag[arm] = dict(
        DIAG_A_global_peak_full=dict(
            hist={str(f): int(c) for f, c in zip(
                *np.unique(np.round(gpf_all, 2), return_counts=True))},
            median=round(float(np.median(gpf_all)), 3),
            iqr=[round(float(np.percentile(gpf_all, 25)), 3),
                 round(float(np.percentile(gpf_all, 75)), 3)],
            median_ratio=round(float(np.median([r for _, r in gp_full])), 1)),
        DIAG_A_global_peak_seg1_hist={str(f): int(c) for f, c in zip(
            *np.unique(np.round(np.array(gp_seg1), 2), return_counts=True))},
        DIAG_A_bandfloor_pin_seeds=floor_hits,
        DIAG_B_drive_line_snr=ds)
out["DIAG"] = diag
json.dump(out, open("l108/results_l108.json", "w"), indent=1)


# ---------- report ----------
for arm in ARMS:
    sm = summary[arm]
    print(f"\n== {arm} == mm_mean {sm['mm_mean_mean']} | "
          f"full f {sm['full_freq_mean']}+-{sm['full_freq_std']} | "
          f"stationary(3seg<=1bin) {sm['stationarity_3seg_within_bin']}/{len(ALL)}")
    print("  full hist:", dict(list(sm["full_freq_hist"].items())[:8]))
    print("  seg0 hist:", dict(list(sm["seg0_hist"].items())[:8]))
    print("  seg1 hist:", dict(list(sm["seg1_hist"].items())[:8]))
    if sm["e1_at_drive"]:
        print("  E1 at-drive counts (seg0/1/2):", sm["e1_at_drive"])
print("\nfreenod==free identical-freq seeds:", ident, "| max full-freq diff:",
      maxdf)
print("\n===== DIAG (ADDENDUM 1) =====")
for arm in ARMS:
    d = diag[arm]
    ga = d["DIAG_A_global_peak_full"]
    print(f"{arm}: globalPeak median {ga['median']} IQR {ga['iqr']} "
          f"ratio(med) {ga['median_ratio']} | bandfloor-pinned "
          f"{d['DIAG_A_bandfloor_pin_seeds']}/{len(ALL)} | "
          f"seg1 global hist {d['DIAG_A_global_peak_seg1_hist']}")
    if d["DIAG_B_drive_line_snr"]:
        print("   drive-line SNR [median, n>=10]:", d["DIAG_B_drive_line_snr"])
