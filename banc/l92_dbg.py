import numpy as np
import pandas as pd

df = pd.read_csv("l92/dn_census_dyn.csv")
print("pandas", pd.__version__)
m1 = df.verdict == "viable"
m2 = df.out_cord > 0
print("m1 sum", int(m1.sum()), "m2 sum", int(m2.sum()))
amp = m1 & m2
print("proper AND:", int(amp.sum()))
weird = (m1 + m2 > 1)
print("(m1+m2>1):", int(weird.sum()))
print("m1+m2 dtype:", (m1 + m2).dtype, "values head:", (m1 + m2).head(6).tolist())
print("m1 dtype:", m1.dtype)
sub = df[amp]
print("by class:", sub.groupby("cls").size().to_dict())
vp = sub[sub.pool_any]
print("with pool reach:", vp.groupby("cls").size().to_dict())
print("DNn pool-reachers by type:")
print(vp[vp.cls == 1].groupby("type").size().sort_values(ascending=False)
      .head(10).to_string())
