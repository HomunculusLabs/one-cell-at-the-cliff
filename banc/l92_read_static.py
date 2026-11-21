import json
import pandas as pd

s = json.load(open("l92/static.json"))
print("C0S prefix", s["c0s_prefix_equal"], "vals", s["c0s_vals_equal"])
print("af_target", s["af_target"], "| dn_new", s["dn_new"], "| edges", s["edges_new"])
df = pd.read_csv("l92/dn_census.csv")
df["pool_any"] = df.pool_reach.fillna("{}").ne("{}")
print("\nDN cells with DIRECT antagonist-pool reach, by class (0=DNi 1=DNn):")
print(df[df.pool_any].groupby("cls").size().to_string())
print("\nDNn pool-reachers, top types:")
print(df[(df.cls == 1) + df.pool_any > 1] if False else
      df[(df.cls == 1).where(df.pool_any, False)].groupby("type").size()
      .sort_values(ascending=False).head(8).to_string())
cols = ["loc", "cls", "type", "side", "out_cord", "out_w", "pool_reach"]
print("\nTop-10 command cells by cord out_w:")
print(df.sort_values("out_w", ascending=False).head(10)[cols].to_string())
print("\nDNg100 rows (working entrain drive reference):")
print(df[df.type == "DNg100"][cols].to_string())
print("\nout_w medians:")
for c, name in ((0, "DNi"), (1, "DNn")):
    sub = df[df.cls == c]
    print(f"  {name}: n={len(sub)} med {sub.out_w.median():.1f} "
          f"p90 {sub.out_w.quantile(.9):.1f} p99 {sub.out_w.quantile(.99):.1f} "
          f"max {sub.out_w.max():.1f}")
