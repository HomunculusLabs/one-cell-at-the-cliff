import json
import re

res = json.load(open("l59/results_l59.json"))
svg = open("l59/ensemble.svg").read()
W, H = 1560, 880
bad = []
for m in re.finditer(r'<(text|circle|rect)[^>]*?([xy])="(-?[\d.]+)"', svg):
    if float(m.group(3)) < 0 or float(m.group(3)) > (W if m.group(2) == "x" else H):
        bad.append(m.group(0)[:80])
print("OOB elements:", len(bad), bad[:5])

d = res["distributions"]
an = res["miss_anatomy"]
c1 = all(d[a]["p_ge_half"] == 8 for a in ("hynohop", "hybrid"))
c2 = (d["hynohop"]["p_ge_half_wilson"] == [0.28, 0.72]
      and d["hybrid"]["p_ge_half_wilson"] == [0.28, 0.72])
mh = {a: {m["seed"] for m in an[a]["misses"]} for a in an}
c3 = len(mh["hynohop"] & mh["hybrid"]) == 4
c4 = (11 in mh["hybrid"] and 11 not in mh["hynohop"]
      and 33 in mh["hybrid"] and 33 not in mh["hynohop"])
c5 = d["hynohop"]["seg1_lt10"] == 4 and d["hybrid"]["seg1_lt10"] == 4
c6 = d["hynohop"]["seg1_lt25"] == 7 and d["hybrid"]["seg1_lt25"] == 7
c7 = (d["hynohop"]["seg1_err_le01"] == 16
      and d["hybrid"]["seg1_err_le01"] == 16)
c8 = (abs(d["hynohop"]["seg1_mean"] - .375) < 5e-4
      and abs(d["hybrid"]["seg1_mean"] - .402) < 5e-4)
c9 = an["hynohop"]["fail_segs"] == 14 and an["hybrid"]["fail_segs"] == 15
c10 = an["hynohop"]["sl_share"] == 0.692 and an["hybrid"]["sl_share"] == 0.545
c11 = res["predictions"]["P5_entry_join"]["hynohop"]["rank_corr_seg0SL_vs_pooled"] == 0.612
c12 = res["predictions"]["P5_entry_join"]["hybrid"]["rank_corr_seg0SL_vs_pooled"] == 0.174
checks = dict(gate_8of16=c1, wilson=c2, shared4=c3, s11s33_hybrid_only=c4,
              seg1_lt10_4=c5, seg1_lt25_7=c6, err16=c7, seg1_means=c8,
              failsegs=c9, sl_shares=c10, p5a=c11, p5b=c12)
print(checks)
print("ALL CLAIM CHECKS PASS" if all(checks.values()) else "SOME FAIL")
