"""L67 verdict re-derivation from stored artifacts (post run.out analysis crash:
arm_block(bi) read dm['bi_*'] which was side-arms-only). Raw rollouts are
checkpointed in l67/raw_l67.npz (saved BEFORE analysis); this recomputes
anchors + analysis + gates from stored traces ONLY. Mirrors l66_verdict.py.
"""
import json
import math

import numpy as np

TAU, DT = 0.05, 0.01
WIN = 6000
SEEDS = [11, 22, 33] + list(range(101, 114))
SIGS = ("fL", "fR", "eL", "eR")
GFB, SIGN, DELAY = 0.1, -1.0, 5
BI, LONLY, RONLY, SPLIT = "bi", "lonly", "ronly", "split"
ARMS = [BI, LONLY, RONLY, SPLIT]
OFFS = [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)]
TS3 = np.arange(299, WIN, 10)

z = np.load("l67/raw_l67.npz")
z66 = np.load("l66/raw_l66.npz")
MM = {a: {s: z[f"mm_{a}_{s}"] for s in SEEDS} for a in ARMS + ["hynohop"]}
TR = {a: {s: {c: z[f"{c}_{a}_{s}"] for c in SIGS} for s in SEEDS}
      for a in ARMS + ["hynohop"]}


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def dom_freq(x, lo=0.3):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    return float(f_hat)


def duty_off(fL, fR, eL, eR):
    hits, sls, srs, hl, hr = [], [], [], [], []
    for lo, hi in OFFS:
        for t in TS3[(TS3 >= lo + 299) & (TS3 < hi)]:
            SL = S_of(fL[t - 299:t + 1], eL[t - 299:t + 1])
            SR = S_of(fR[t - 299:t + 1], eR[t - 299:t + 1])
            hits.append((SL >= 0.25) & (SR >= 0.25))
            hl.append(SL >= 0.25)
            hr.append(SR >= 0.25)
            sls.append(SL)
            srs.append(SR)
    return dict(duty=round(float(np.nanmean(np.array(hits, float))), 3),
                dutyL=round(float(np.nanmean(np.array(hl, float))), 3),
                dutyR=round(float(np.nanmean(np.array(hr, float))), 3),
                SL=round(float(np.nanmean(sls)), 3),
                SR=round(float(np.nanmean(srs)), 3))


def seg2(mm):
    errs = []
    for b in range(WIN // 500):
        if 2000 <= b * 500 < 4000 and b * 500 > 2000:
            errs.append(abs(dom_freq(mm[b * 500:(b + 1) * 500]) - 1.4))
    return round(float(np.mean(errs)), 4)


# anchors from stored traces
c0 = {}
for s in SEEDS:
    c0[f"bi_mm_{s}"] = float(np.abs(MM[BI][s] - z66[f"mm_g01_d05_m_{s}"][:WIN]).max())
    for c in SIGS:
        c0[f"bi_{c}_{s}"] = float(np.abs(
            TR[BI][s][c] - z66[f"{c}_g01_d05_m_{s}"][:WIN]).max())
c0_pass = all(v == 0.0 for v in c0.values())
dm, first_div, prefix_ok = {}, {}, {}
for a in ARMS:                      # ALL four arms incl. bi (the crash fix)
    for s in SEEDS:
        diffs = np.concatenate(
            [np.abs(MM[a][s] - MM["hynohop"][s])]
            + [np.abs(TR[a][s][c] - TR["hynohop"][s][c]) for c in SIGS])
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        first_div[f"{a}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{a}_{s}"] = round(float(diffs.max()), 5)
        prefix_ok[f"{a}_{s}"] = bool(diffs[:DELAY + 1].max() == 0.0)
c0s_pass = all(first_div[f"{a}_{s}"] == DELAY + 1 for a in ARMS for s in SEEDS) \
    and all(prefix_ok.values())
print(f"C0 pass {c0_pass} ({len(c0)} keys) | C0s {c0s_pass} "
      f"| fd==6 all {all(v == 6 for v in first_div.values())}")

cells = {}
for a in ARMS + ["hynohop"]:
    for s in SEEDS:
        d = duty_off(*[TR[a][s][c] for c in SIGS])
        d["e2"] = seg2(MM[a][s])
        cells[(a, str(s))] = d


def arr(a, key):
    return np.array([cells[(a, str(s))][key] for s in SEEDS], float)


open_off = arr("hynohop", "duty")
open_e2_med = float(np.median(arr("hynohop", "e2")))
open_SL, open_SR = arr("hynohop", "SL"), arr("hynohop", "SR")
open_dL, open_dR = arr("hynohop", "dutyL"), arr("hynohop", "dutyR")

r66 = json.load(open("l66/results_l66.json"))
c0o = dict(off=[round(abs(v - q), 4) for v, q in zip(open_off, r66["open"]["off"])],
           SL=[round(abs(v - q), 4) for v, q in zip(open_SL, r66["open"]["SL"])],
           SR=[round(abs(v - q), 4) for v, q in zip(open_SR, r66["open"]["SR"])])
c0o_pass = all(max(c0o[k]) == 0.0 for k in c0o)


def wilson(k, nn, z=1.96):
    if nn == 0:
        return (0.0, 0.0, 1.0)
    p = k / nn
    den = 1 + z * z / nn
    ctr = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return (round(p, 3), round(ctr - hw, 3), round(ctr + hw, 3))


def arm_block(a):
    e2 = arr(a, "e2")
    dSL, dSR = arr(a, "SL") - open_SL, arr(a, "SR") - open_SR
    dL, dR = arr(a, "dutyL") - open_dL, arr(a, "dutyR") - open_dR
    lock_ok = bool(np.median(e2) <= max(0.01, 2 * open_e2_med) and e2.max() <= 0.5)
    return dict(SL=[round(float(v), 3) for v in arr(a, "SL")],
                SR=[round(float(v), 3) for v in arr(a, "SR")],
                dutyL=[round(float(v), 3) for v in arr(a, "dutyL")],
                dutyR=[round(float(v), 3) for v in arr(a, "dutyR")],
                dSL=[round(float(v), 3) for v in dSL],
                dSR=[round(float(v), 3) for v in dSR],
                dSL_mean=round(float(dSL.mean()), 3),
                dSR_mean=round(float(dSR.mean()), 3),
                dSL_pos=int((dSL > 0).sum()), dSR_pos=int((dSR > 0).sum()),
                dSR_wilson=wilson(int((dSR > 0).sum()), len(SEEDS)),
                dL_mean=round(float(dL.mean()), 3), dR_mean=round(float(dR.mean()), 3),
                e2=[round(float(v), 4) for v in e2],
                e2_med=round(float(np.median(e2)), 4),
                cat=bool(e2.max() > 0.5), lock_ok=lock_ok,
                dm_min=round(min(dm[f"{a}_{s}"] for s in SEEDS), 5))


blocks = {a: arm_block(a) for a in ARMS}
bi, lo, ro, sp = blocks[BI], blocks[LONLY], blocks[RONLY], blocks[SPLIT]
bi_rep = dict(dSL_mean=bi["dSL_mean"], dSR_mean=bi["dSR_mean"],
              l66_fb_SL=round(float(np.mean(r66["fb"]["SL"])), 3),
              l66_fb_SR=round(float(np.mean(r66["fb"]["SR"])), 3),
              l66_lift=round(float(np.mean(
                  np.array(r66["fb"]["lift"]))), 3),
              bi_off_lift_mean=round(float(np.mean(arr(BI, "duty") - open_off)), 3))

p1 = dict(need_dSR=.10, dSR_mean=ro["dSR_mean"], dSR_pos=ro["dSR_pos"],
          dSR_wilson=ro["dSR_wilson"], dSL_mean=ro["dSL_mean"],
          lock_ok=ro["lock_ok"], dm_min=ro["dm_min"],
          pass_P1=bool(ro["dSR_mean"] >= .10 and ro["dSR_pos"] >= 11
                       and ro["dSL_mean"] >= -.05 and ro["lock_ok"]
                       and ro["dm_min"] > 0))
p2 = dict(dSL_mean=lo["dSL_mean"], dSR_mean=lo["dSR_mean"], dm_min=lo["dm_min"],
          pass_P2=bool(lo["dSL_mean"] >= .10 and lo["dSL_mean"] > lo["dSR_mean"]
                       and lo["dm_min"] > 0))
crossed = bool(np.mean(np.abs(np.array(ro["dSL"])))
               >= np.mean(np.abs(np.array(ro["dSR"]))))
p3 = dict(dSL_mean_ro=ro["dSL_mean"], crossed=crossed,
          pass_P3=bool(ro["dSL_mean"] <= .05))
flips = int(sum((ro["dSR"][i] > 0) != (sp["dSR"][i] > 0) for i in range(len(SEEDS))))
p4 = dict(pass_P4=bool(all(blocks[a]["lock_ok"] for a in ARMS)),
          locks={a: blocks[a]["lock_ok"] for a in ARMS},
          cats={a: blocks[a]["cat"] for a in ARMS})
p5 = dict(dSL_mean=sp["dSL_mean"], dSR_mean=sp["dSR_mean"], lock_ok=sp["lock_ok"],
          dm_min=sp["dm_min"],
          pass_P5=bool(sp["dSL_mean"] >= .10 and sp["dSR_mean"] >= .10
                       and sp["lock_ok"] and sp["dm_min"] > 0))
branch_b = bool(not p1["pass_P1"] and (crossed
              or lo["dSL_mean"] < bi["dSL_mean"] - .10 or flips >= 5))
verdict = ("SIDE-TUNABLE" if p1["pass_P1"] else
           ("LOTTERY-CROSSED (branch B)" if branch_b else "MIXED/INFORMATIVE"))
wired_dead = [f"{a}_{s}" for a in ARMS for s in SEEDS if dm[f"{a}_{s}"] == 0.0]

out = dict(arms=ARMS, seeds=SEEDS, gfb=GFB, sign=SIGN, delay=DELAY,
           open=dict(off=[round(float(v), 3) for v in open_off],
                     e2_med=round(open_e2_med, 4),
                     SL=[round(float(v), 3) for v in open_SL],
                     SR=[round(float(v), 3) for v in open_SR],
                     dutyL=[round(float(v), 3) for v in open_dL],
                     dutyR=[round(float(v), 3) for v in open_dR]),
           blocks=blocks, bi_replication=bi_rep,
           gates=dict(P1=p1, P2=p2, P3=p3, P4=p4, P5=p5,
                      dSR_flips_ronly_vs_split=flips,
                      branch_B_selected=branch_b, verdict=verdict),
           anchors=dict(c0_n=len(c0), c0_pass=c0_pass,
                        c0o=c0o, c0o_pass=bool(c0o_pass),
                        c0s_pass=bool(c0s_pass),
                        prefix_all=bool(all(prefix_ok.values())),
                        fd_all_delay_plus_1=bool(
                            all(v == DELAY + 1 for v in first_div.values())),
                        c1_in_run=True,  # asserted in run.out before crash
                        c0w=dict(idx_checks="passed (run.out line 1)")),
           dm=dm, first_div=first_div, wired_dead=wired_dead)
with open("l67/results_l67.json", "w") as f:
    json.dump(out, f, indent=1)

print(f"C0O open-vs-l66json {c0o_pass} | bi dSL {bi['dSL_mean']:+.3f} "
      f"dSR {bi['dSR_mean']:+.3f} (l66 fb {bi_rep['l66_fb_SL']}/"
      f"{bi_rep['l66_fb_SR']}, bi off-lift {bi_rep['bi_off_lift_mean']:+.3f} "
      f"vs l66 {bi_rep['l66_lift']:+.3f})")
for a in ARMS:
    b = blocks[a]
    print(f"{a}: dSL {b['dSL_mean']:+.3f} (pos {b['dSL_pos']}/16) "
          f"dSR {b['dSR_mean']:+.3f} (pos {b['dSR_pos']}/16 {b['dSR_wilson']}) "
          f"dutyL {b['dL_mean']:+.3f} dutyR {b['dR_mean']:+.3f} "
          f"lock_ok {b['lock_ok']} cat {b['cat']} dm {b['dm_min']}")
print(f"P1 {p1['pass_P1']} | P2 {p2['pass_P2']} | P3 crossed {crossed} "
      f"(pass {p3['pass_P3']}) | P4 {p4['pass_P4']} | P5 {p5['pass_P5']} "
      f"| flips {flips} | wired_dead {len(wired_dead)}")
print(f"VERDICT {verdict}")
