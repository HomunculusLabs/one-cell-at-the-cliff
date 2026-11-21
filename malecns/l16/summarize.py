import json
import numpy as np

r = json.load(open("l16/results_l16.json"))
real, nulls = r["real"], r["nulls"]
print("anchor:", round(r["anchor_peak_self_cos"], 3))
print("\nREAL per-seed:")
for k in ["Ti_lead_ext_minus_flex", "Tr_lead_ext_minus_flex", "Ti_xcorr_min",
          "Tr_xcorr_min", "tpk_sd_top200", "tpk_iqr_top200", "half_spread_top200",
          "half_jump", "motor_peak"]:
    print(f"  {k:26s}", [round(run[k], 3) for run in real["runs"]])
print("  Ti lead sign-consistent:", real["Ti_lead_sign_consistent"],
      "| Tr:", real["Tr_lead_sign_consistent"])
print("  pca:", real["pca"])
print("\nper-seed Ti t_pk flex/ext:", [(run["Ti_t_pk_flex"], run["Ti_t_pk_ext"]) for run in real["runs"]])
print("per-seed Tr t_pk flex/ext:", [(run["Tr_t_pk_flex"], run["Tr_t_pk_ext"]) for run in real["runs"]])
print("per-seed peak flex/ext Ti:", [(round(run["Ti_peak_flex"], 4), round(run["Ti_peak_ext"], 4)) for run in real["runs"]])

keys = ["st_self_cos", "Ti_lead_ext_minus_flex", "Tr_lead_ext_minus_flex",
        "Ti_xcorr_min", "Tr_xcorr_min", "tpk_sd_top200", "half_spread_top200", "top6_mass"]
print("\nnull ensemble (5 draws):")
for k in keys:
    if k == "st_self_cos":
        v = [n["st_self_cos"] for n in nulls]
    else:
        v = [n["agg"][k] for n in nulls]
    print(f"  {k:26s} real {real['agg'][k] if k in real['agg'] else real['st_self_cos']:+.4f}  null {np.mean(v):+.4f}±{np.std(v):.4f}")
print("  null pca var1:", [round(n["pca"]["var1"], 3) for n in nulls],
      "var2:", [round(n["pca"]["var2"], 4) for n in nulls])
print("  null comp2 flex-ext sep Ti:", [round(n["pca"]["comp2_flex_ext_sep"]["Ti"], 3) for n in nulls],
      "real:", round(real["pca"]["comp2_flex_ext_sep"]["Ti"], 3))
print("  null swaps:", [n["swaps"] for n in nulls])
print("  null Ti sign-consistent:", sum(n["Ti_lead_sign_consistent"] for n in nulls), "/5;",
      "Tr:", sum(n["Tr_lead_sign_consistent"] for n in nulls), "/5")
cfg = r["config"]
print("\nconfig: pairs", cfg["pairs"], "\ntop6_types:", cfg["top6_types"][:6])
