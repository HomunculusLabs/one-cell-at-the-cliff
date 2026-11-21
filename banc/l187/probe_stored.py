"""L187 pre-registration probe: STORED covariates only (zero rollouts, no RNG).
Relay GI 75494 activity on the k=24 base census and in stored L175 (B39) arms."""
import json, glob
import numpy as np
cen = np.load("l175/census_k24.npz")
gi = cen["gi"]; xb = cen["x_mean_3seed"]; xs = cen["x_mean"]
CELLS = {"relay": 75494, "carrier": 1110, "sc40": 559, "pm69410": 69410, "pm72158": 72158,
         "74914": 74914, "71392": 71392, "74468": 74468, "64322": 64322, "66994": 66994, "69186": 69186}
print("base n", len(gi), "active frac", float((xb > .05).mean()))
for k, g in CELLS.items():
    i = int(np.where(gi == g)[0][0])
    print(f"{k:8s} gi {g:6d} loc {i:6d} x3 {xb[i]:.4f} seeds {np.round(xs[:, i], 4)} sign {cen['eff_sign'][i]:+.0f} ow_eff {cen['out_w_eff'][i]:.2f} drive {cen['delivered_drive'][i]:.3f}")
# stored L175 arms on B39: relay x_mean under cutwA / sc25 / sc40 (arm loc = base loc minus removed cells below)
B39 = list(range(3545, 3561))
def armloc(g, removed):
    assert g not in removed
    i = int(np.where(gi == g)[0][0])
    return i - sum(1 for r in removed if int(np.where(gi == r)[0][0]) < i)
gains = {}
for w in range(5):
    gj = json.load(open(f"l175/gains_w{w}.json"))["gain"]
    for a in gj: gains[a] = (gj[a], w)
for arm, rem in (("cutwA", []), ("sc25", [1110]), ("sc40", [559]), ("sc26", [319]), ("sc27", [707])):
    w = gains[arm][1]
    z = np.load(f"l175/xm_w{w}.npz")
    for k in ("relay", "carrier", "sc40", "74914", "71392", "74468", "64322"):
        g = CELLS[k]
        if g in rem: continue
        v = np.array([z[f"xmean_{arm}_{s}"][armloc(g, rem)] for s in B39])
        print(f"{arm:6s} {k:8s} mean {v.mean():.4f} sd {v.std(ddof=1):.4f} min {v.min():.4f} max {v.max():.4f}")
