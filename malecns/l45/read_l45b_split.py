import json

r = json.load(open("l45/results_l45b.json"))
v = r["verdict"]
cen = r["census"]
TSEEDS = r["meta"]["tseeds"]

# rebuild per-seed: FROM(B, shared), TO(channel arm C), base C
import numpy as np
lab_state = {}
for s in TSEEDS:
    lab_state[s] = dict(B=cen[str(s)]["B"]["label"], Cbase=cen[str(s)]["C"]["label"])
# channel-arm TO labels: stored only inside edges; re-derive from raw npz seg C
z = np.load("l45/raw_l45b.npz")

def rhythm2(x, lo=0.5, hi=10.0):
    x = x - x.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), 0.01)
    b = (fr >= lo) & (fr <= hi)
    pb, fb = ps[b], fr[b]
    i = int(np.argmax(pb))
    return float(pb[i] / max(np.median(pb), 1e-30)), float(fb[i])

def ssign(s):
    return "+" if s > 0.15 else ("-" if s < -0.15 else "0")

def seg_label(a, s, lo, hi):
    rmm, f = rhythm2(z[f"mm_{a}_{s}"][lo:hi])
    out = []
    for sd, ff, ee in (("L", "fL", "eL"), ("R", "fR", "eR")):
        ss = []
        for t in range(lo + 499, hi, 10):
            x1 = z[f"{ff}_{a}_{s}"][t - 499:t + 1]
            x2 = z[f"{ee}_{a}_{s}"][t - 499:t + 1]
            ss.append(-np.corrcoef(x1, x2)[0, 1] if x1.std() > 1e-6 and x2.std() > 1e-6 else np.nan)
        out.append(ssign(float(np.nanmedian(ss))))
    b = "FLAT" if rmm < 5 else ("slow" if f < 1 else "mid" if f < 1.8 else "fast2" if f < 2.6 else "fast3")
    return f"{b}|{out[0]}{out[1]}"

print("channel      seed  FROM      arm_TO    base_TO   verdict")
from collections import Counter
counts = {}
for ch, _, _ in [("d_DNg110", 0, 0), ("d_DNge046", 0, 0), ("d_DNg95", 0, 0),
                 ("d_DNg88rel", 0, 0), ("d_E1", 0, 0), ("d_X464", 0, 0)]:
    cc = Counter()
    for s in TSEEDS:
        frm = lab_state[s]["B"]
        to = seg_label(ch, s, 7500, 11000)
        bt = lab_state[s]["Cbase"]
        if to == bt:
            v_ = "same-as-base"
        elif to == frm and bt != frm:
            v_ = "HELD (base drifted, arm did not)"
        elif to != frm:
            v_ = "MOVED (driven)"
        else:
            v_ = "MOVED-BASE-ONLY->arm went third state"
        cc[v_] += 1
        print(f"{ch:11s} {s:4d}  {frm:9s} {to:9s} {bt:9s} {v_}")
    counts[ch] = dict(cc)
print()
for ch, cc in counts.items():
    print(ch, cc)
