import json
import pandas as pd

st = json.load(open("l93/static.json"))
print("ti_share:", st["ti_cand_share"])
print("ti_cand[:4]:", st["ti_cand"][:4])
v = pd.read_csv("l93/viability.csv")
vi = v[(v.u_max > 0) & (v.x_mean < .95)]
print("viable DN cells:", len(vi), "of", len(v))
ic = st["int_cand"]
tc = st["ti_cand"]
overlap = set(c["loc"] for c in ic).intersection(set(c["loc"] for c in tc))
print("overlap Tr16 vs Ti16:", len(overlap))
print("Tr16 locs:", sorted(c["loc"] for c in ic))
print("Ti16 locs:", sorted(c["loc"] for c in tc))
