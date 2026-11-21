"""L78 verdict: R1-R5 from l78/raw_l78.npz + scan_l78.json (no reruns).

R1 Tr slow-seg duty (headroom) + off-window duty, per arm vs open, sham rule.
R2 Tr SL rescue (median > 0, SR >= .25).  R3 Ti duty_07 no-harm.
R4 lock: per-seg spectral ratio >= 0.5 x open.  R5 budget (reported).
"""
import json

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEEDS = [11, 22, 33]
SIGS = ("fL", "fR", "eL", "eR")
PAIRS = ("Ti", "Tr")
ARMS = ["open", "fbn_g01", "fbp_g01", "fbn_g03", "sham_g01"]
TREAT = ARMS[1:]
OFFS = [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)]
TS = np.arange(299, WIN, 10)

z = np.load("l78/raw_l78.npz")
scan = json.load(open("l78/scan_l78.json"))


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def roll_s(a, s, pk):
    """rolling 300-step SL/SR at sampled t"""
    fL, fR = z[f"{pk}_fL_{a}_{s}"], z[f"{pk}_fR_{a}_{s}"]
    eL, eR = z[f"{pk}_eL_{a}_{s}"], z[f"{pk}_eR_{a}_{s}"]
    SL = np.full(len(TS), np.nan)
    SR = np.full(len(TS), np.nan)
    for i, t in enumerate(TS):
        SL[i] = S_of(fL[t - 299:t + 1], eL[t - 299:t + 1])
        SR[i] = S_of(fR[t - 299:t + 1], eR[t - 299:t + 1])
    return SL, SR


m_slow = ((TS >= 799) & (TS < 2000)) | ((TS >= 4799) & (TS < 6000))
m_off = np.zeros(len(TS), bool)
for lo, hi in OFFS:
    m_off |= (TS >= lo + 299) & (TS < hi)
m_fast = (TS >= 2299) & (TS < 4000)

out = dict(windows=dict(slow=int(m_slow.sum()), off=int(m_off.sum()),
                        fast=int(m_fast.sum())),
           anchors=dict(c0a=scan["c0a_pass"], c0p_xm=scan["c0p_pass_xm"],
                        c0p_mm=scan["c0p_pass_mm"], c2=scan["c2_pass"]),
           budget=scan["budget"], arms={})

# per arm/seed reads
for a in ARMS:
    out["arms"][a] = {}
    for s in SEEDS:
        SLTr, SRTr = roll_s(a, s, "Tr")
        SLTi, SRTi = roll_s(a, s, "Ti")
        bothT = (SLTr >= .25) & (SRTr >= .25)
        bothI = (SLTi >= .25) & (SRTi >= .25)
        out["arms"][a][str(s)] = dict(
            duty_slow=round(float(np.nanmean(bothT[m_slow])), 3),
            duty_off=round(float(np.nanmean(bothT[m_off])), 3),
            duty_fast=round(float(np.nanmean(bothT[m_fast])), 3),
            Ti_duty07=round(float(np.nanmean(bothI[m_slow])), 3),
            Tr_SL_slow=round(float(np.nanmedian(SLTr[m_slow])), 3),
            Tr_SR_slow=round(float(np.nanmedian(SRTr[m_slow])), 3))

# lock ratios per seg (female spectral form)
def domf(x):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= 0.3) & (fr <= 10)
    return float(ps[band].max() / max(np.median(ps[band]), 1e-30))


lock = {}
for a in ARMS:
    lock[a] = {}
    for s in SEEDS:
        mm = z[f"mm_{a}_{s}"]
        lock[a][str(s)] = [round(domf(mm[s0:s0 + 2000]), 1) for s0, _, _ in SEGB]
out["lock"] = lock

# ---- R1 content: lift per window, sham rule ----
r1 = {}
for a in TREAT:
    for w in ("duty_slow", "duty_off", "duty_fast"):
        lifts = [out["arms"][a][str(s)][w] - out["arms"]["open"][str(s)][w]
                 for s in SEEDS]
        r1[f"{a}_{w}"] = dict(lifts=[round(x, 3) for x in lifts],
                              n_up=int(sum(x > 0 for x in lifts)))
sham_lifts = {w: [out["arms"]["sham_g01"][str(s)][w] - out["arms"]["open"][str(s)][w]
                  for s in SEEDS] for w in ("duty_slow", "duty_off", "duty_fast")}
r1["sham_lifts"] = {w: [round(x, 3) for x in v] for w, v in sham_lifts.items()}
content = []
for a in TREAT:
    for w in ("duty_slow", "duty_off", "duty_fast"):
        fb = r1[f"{a}_{w}"]["lifts"]
        sh = sham_lifts[w]
        fb_mean, sh_mean = float(np.mean(fb)), float(np.mean(sh))
        if r1[f"{a}_{w}"]["n_up"] >= 2 and sh_mean <= 0.5 * max(fb_mean, 1e-9) and fb_mean > 0:
            content.append(f"{a}:{w}")
r1["content_windows"] = content

# ---- R2 side rescue ----
r2 = {}
for a in TREAT:
    dsl = [out["arms"][a][str(s)]["Tr_SL_slow"] for s in SEEDS]
    dsr = [out["arms"][a][str(s)]["Tr_SR_slow"] for s in SEEDS]
    r2[a] = dict(SL=dsl, SR=dsr,
                 n_SL_pos=int(sum(x > 0 for x in dsl)),
                 n_SR_kept=int(sum(x >= .25 for x in dsr)))
r2["open"] = {k: [out["arms"]["open"][str(s)][k] for s in SEEDS]
              for k in ("Tr_SL_slow", "Tr_SR_slow")}
rescue = [a for a in TREAT if r2[a]["n_SL_pos"] >= 2 and r2[a]["n_SR_kept"] >= 2]
r2["rescue_arms"] = rescue

# ---- R3 no-harm ceiling (Ti) ----
r3 = {a: dict(Ti=[out["arms"][a][str(s)]["Ti_duty07"] for s in SEEDS],
              open=[out["arms"]["open"][str(s)]["Ti_duty07"] for s in SEEDS])
      for a in TREAT}
r3_pass = {a: all(r3[a]["Ti"][i] >= r3[a]["open"][i] - .05 for i in range(3))
           for a in TREAT}

# ---- R4 lock ----
r4 = {}
for a in TREAT:
    ok = all(lock[a][str(s)][seg] >= 0.5 * lock["open"][str(s)][seg]
             for s in SEEDS for seg in range(3))
    r4[a] = dict(ok=bool(ok),
                 ratios={str(s): lock[a][str(s)] for s in SEEDS},
                 open={str(s): lock["open"][str(s)] for s in SEEDS})

out["gates"] = dict(
    R1_content=bool(content), R1_content_windows=content,
    R2_rescue=bool(rescue), R2_rescue_arms=rescue,
    R3_noharm=r3_pass, R4_lock={a: r4[a]["ok"] for a in TREAT},
    R5_budget=scan["budget"])

# verdict shape (PREREG)
toxic = (not all(r3_pass.values())) or (not all(r4[a]["ok"] for a in TREAT))
if content or rescue:
    verdict = "CONTENT-GENERALIZES"
elif toxic:
    verdict = "TOXIC"
else:
    verdict = "MALE-ONLY"
out["gates"]["verdict"] = verdict

json.dump(dict(r1=r1, r2=r2, r3=r3, r4=r4, **out),
          open("l78/results_l78.json", "w"), indent=1)

print("open:", json.dumps(out["arms"]["open"]))
for a in TREAT:
    print(f"{a}: {json.dumps(out['arms'][a])}")
print("lock open:", lock["open"])
for a in TREAT:
    print(f"lock {a}: {lock[a]} ok={r4[a]['ok']} | R3 {r3_pass[a]}")
print("R1 lifts:", json.dumps({k: v for k, v in r1.items()
                               if k not in ('sham_lifts', 'content_windows')}))
print("sham lifts:", r1["sham_lifts"])
print("R2:", json.dumps(r2))
print("VERDICT:", verdict, "| content:", content, "| rescue:", rescue)
