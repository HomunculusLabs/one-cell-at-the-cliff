"""L202 addendum — POST HOC, written and run AFTER the registered verdict
(results_l202.json FINAL). Reads stored L202 files only. Two parts:
 (1) independent re-derivation of the headline per-seed duties (own
     vectorised code, not the lineage helper) vs results_l202.json;
 (2) descriptive: how far ru2's FREE trajectory under carrier removal is from
     the base trajectory the clamp replays (mean, correlation, 1.4-Hz
     amplitude in the middle segment). Nothing here re-labels a branch."""
import json
import math

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

OUT = "l202"
B45 = list(range(3737, 3753))
res = json.load(open(f"{OUT}/results_l202.json"))
assert res["status"] == "FINAL"
PLAN = {0: ["sc25", "sc25F", "l2c", "l2cF"], 1: ["l2", "s2k", "s2kF", "lt5"],
        2: ["lt4", "lt4F", "t4c", "t4cF"], 3: ["rcut", "rcutF", "edge", "sham"]}
raws = {w: np.load(f"{OUT}/raw_w{w}.npz") for w in range(4)}
TS = np.arange(499, 6000, 10)


def s_right(z, a, s, side="R"):
    f, e = z[f"Ti_f{side}_{a}_{s}"].astype(np.float32), z[f"Ti_e{side}_{a}_{s}"].astype(np.float32)
    F, E = swv(f, 500)[TS - 499], swv(e, 500)[TS - 499]
    out = np.full(len(TS), np.nan)
    for i in range(len(TS)):                      # np.corrcoef on float32 windows (helper's dtype)
        if F[i].std() > 1e-6 and E[i].std() > 1e-6:
            out[i] = -np.corrcoef(F[i], E[i])[0, 1]
    return out


Q07 = ((TS >= 500) & (TS < 2000)) | ((TS >= 4500) & (TS < 6000))
Q14 = (TS >= 2500) & (TS < 4000)
chk, mx = 0, 0.0
mine = {}
for w, arms in PLAN.items():
    for a in arms + (["cutwA"] if w == 0 else []):
        d07, d14, dL = [], [], []
        for s in B45:
            S = s_right(raws[w], a, s)
            d07.append(round(float(np.nanmean(S[Q07] >= .25)), 3))
            d14.append(round(float(np.nanmean(S[Q14] >= .25)), 3))
            SL = s_right(raws[w], a, s, "L")
            dL.append(round(float(np.nanmean(SL[Q07] >= .25)), 3))
        ref = res["base"] if a == "cutwA" else res["arms"][a]
        for got, key in ((d07, "dutyR"), (d14, "duty14R"), (dL, "dutyL")):
            mx = max(mx, float(np.abs(np.array(got) - np.array(ref[key])).max()))
            chk += len(got)
        mine[a] = dict(R=d07, R14=d14, L=dL)
print(f"(1) independent duty re-derivation, 17 arms x 16 seeds x (R chopped, R 1.4-Hz, L chopped): "
      f"{chk} values, max |diff| vs results_l202.json = {mx}")
assert mx == 0.0


def pci(x, y):
    d = np.array(x, float) - np.array(y, float)
    h = 2.131449546 * d.std(ddof=1) / math.sqrt(len(d))
    return round(float(d.mean()), 4), [round(float(d.mean() - h), 4), round(float(d.mean() + h), 4)]


hl = dict(W=pci(mine["l2c"]["R"], mine["sc25"]["R"]), W_fixed=pci(mine["l2cF"]["R"], mine["sc25F"]["R"]),
          N_clamp_minus_free=pci(mine["s2k"]["R"], mine["sc25"]["R"]),
          N_clamp_minus_cut=pci(mine["s2k"]["R"], mine["l2c"]["R"]),
          S_twin_minus_cut=pci(mine["t4c"]["R"], mine["l2c"]["R"]))
for k, (mu, ci) in hl.items():
    want = {"W": "R_l2c_minus_sc25", "W_fixed": "R_l2cF_minus_sc25F",
            "N_clamp_minus_free": "R_s2k_minus_sc25", "N_clamp_minus_cut": "R_s2k_minus_l2c",
            "S_twin_minus_cut": "R_t4c_minus_l2c"}[k]
    c = res["contrasts"][want]
    assert abs(mu - c["mean"]) < 2e-4 and all(abs(a - b) < 2e-4 for a, b in zip(ci, c["ci95"])), k
print("    headline paired contrasts recomputed (exact t quantile) == verdict to 2e-4:", hl)

# (2) ru2 free vs base trajectory (worker 0 holds sc25 / sc25F and its own cutwA)
z = raws[0]
t = np.arange(6000) * 0.01
mid = slice(2500, 4000)


def amp(x, f):
    x = x - x.mean()
    tt = t[mid]
    return 2 * abs(np.mean(x * np.exp(-2j * math.pi * f * tt)))


rows = {}
for a in ("sc25", "sc25F"):
    r_all, r_mid, dmean, a14f, a14b, a07f, a07b = [], [], [], [], [], [], []
    for s in B45:
        fr, bs = z[f"c70994_{a}_{s}"].astype(float), z[f"c70994_cutwA_{s}"].astype(float)
        r_all.append(np.corrcoef(fr, bs)[0, 1])
        r_mid.append(np.corrcoef(fr[mid], bs[mid])[0, 1])
        dmean.append(fr.mean() - bs.mean())
        a14f.append(amp(fr[mid], 1.4))
        a14b.append(amp(bs[mid], 1.4))
        a07f.append(amp(fr[mid], 0.7))
        a07b.append(amp(bs[mid], 0.7))
    rows[a] = dict(corr_window=round(float(np.mean(r_all)), 3),
                   corr_window_range=[round(float(min(r_all)), 3), round(float(max(r_all)), 3)],
                   corr_middle=round(float(np.mean(r_mid)), 3),
                   mean_rate_diff=round(float(np.mean(dmean)), 4),
                   amp14_free=round(float(np.mean(a14f)), 4), amp14_base=round(float(np.mean(a14b)), 4),
                   amp14_ratio_seeds_gt1=int(sum(f > b for f, b in zip(a14f, a14b))),
                   amp07mid_free=round(float(np.mean(a07f)), 4),
                   amp07mid_base=round(float(np.mean(a07b)), 4))
    print(f"(2) ru2 free under {a} vs base trajectory:", rows[a])
json.dump(dict(note="POST HOC (after the registered verdict); descriptive only",
               independent_duty_checks=chk, independent_duty_max_diff=mx, headline=hl,
               ru2_free_vs_base=rows), open(f"{OUT}/addendum.json", "w"), indent=1)
