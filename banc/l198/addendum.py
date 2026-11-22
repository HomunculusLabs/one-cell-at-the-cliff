"""L198 addendum — POST HOC, descriptive (written after the FINAL verdict was
read). Zero rollouts: stored results_l198.json / results_l187.json only.
(1) relay arm pooled over its two batches (B41 L187 + B43 L198), scaled bands;
(2) each drive-matched cell vs the same-batch relay arm, paired;
(3) gain-only null expectation (L185 B40 slope) and each arm's excess."""
import json, math
import numpy as np
r = json.load(open("l198/results_l198.json")); r7 = json.load(open("l187/results_l187.json"))
assert r["status"] == "FINAL" and r7["status"] == "FINAL"
SL = r7["gain_null_slope_b40"]          # meanR per +0.1% gain
out = {}
pool = {}
for a in ("rcut", "rcutF", "sc25", "sc25F"):
    R = np.array(r7["arms"][a]["dutyR"] + r["arms"][a]["dutyR"]); n = len(R)
    k, mu = int((R >= .5).sum()), float(R.mean())
    cls = "SUPER" if mu >= .60 and k >= math.ceil(.75 * n) else "NOT-SUPER" if k <= n // 2 and mu <= .50 else "INTERMEDIATE"
    m14 = float(np.mean(r7["arms"][a]["duty14"] + r["arms"][a]["duty14"]))
    pool[a] = dict(n=n, kR=k, meanR=round(mu, 3), cls=cls, mean14=round(m14, 3),
                   batches=dict(B41=[r7["arms"][a]["kR"], r7["arms"][a]["meanR"]], B43=[r["arms"][a]["kR"], r["arms"][a]["meanR"]]))
bR = np.array(r7["base"]["dutyR"] + r["base"]["dutyR"])
pool["cutwA"] = dict(n=len(bR), kR=int((bR >= .5).sum()), meanR=round(float(bR.mean()), 3))
out["pooled_two_batches"] = pool
T = 2.131
def paired(x, y):
    d = np.array(x) - np.array(y); mu = float(d.mean()); h = T * float(d.std(ddof=1)) / 4
    return dict(mean=round(mu, 4), ci95=[round(mu - h, 4), round(mu + h, 4)])
out["vs_relay_same_batch"] = {a: paired(r["arms"][a]["dutyR"], r["arms"]["rcut"]["dutyR"]) for a in ("tw", "ru1", "ru2", "ru3", "ru4", "ru5")}
out["gain_null"] = {}
for a in ("rcut", "tw", "ru1", "ru2", "ru3", "ru4", "ru5", "sc25"):
    g = r["arms"][a]["gain_delta_pct"]; pred = SL * g / 0.1; obs = r["arms"][a]["vs_base"]["mean"]
    out["gain_null"][a] = dict(gain_delta_pct=round(g, 3), null_pred_dR=round(pred, 4), observed_dR=obs,
                               excess=round(obs - pred, 4), extrapolated=bool(abs(g) > .5))
six = ["tw", "ru1", "ru2", "ru3", "ru4", "ru5"]
dr = [r["arms"][a]["vs_base"]["mean"] for a in six]
out["six_cell_null"] = dict(dR=dict(zip(six, dr)), mean=round(float(np.mean(dr)), 4), sd=round(float(np.std(dr, ddof=1)), 4),
                            max=max(dr), relay_dR=r["arms"]["rcut"]["vs_base"]["mean"],
                            relay_rank_among_7=1 + sum(d > r["arms"]["rcut"]["vs_base"]["mean"] for d in dr),
                            n_ci_excludes_zero_up=sum(r["arms"][a]["vs_base"]["ci95"][0] > 0 for a in six))
json.dump(out, open("l198/addendum.json", "w"), indent=1)
print(json.dumps(out, indent=1))
