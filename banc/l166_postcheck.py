"""L166 postcheck: (1) B44 disjointness from every stored batch (true
held-out), (2) does the fresh batch clear the SAME carrier pairs as the stored
table (set identity, not just the count), (3) inversion magnitude on H3.
Read-only, deterministic."""
import json

import numpy as np

r = json.load(open("l166/results_l166.json"))
a = json.load(open("l166/anchor.json"))
CARRIER, CONTROL = r["carrier"], r["control"]
CP = [(CARRIER[i], CARRIER[j]) for i in range(8) for j in range(i + 1, 8)]

# (1) disjointness
b44 = set(r["held_out"]["H1_fresh_b65_B44"]["seeds"])
stored = set()
for f, ss in a["seeds"].items():
    stored |= set(ss)
assert not (b44 & stored), ("B44 collides with a stored batch", b44 & stored)
print(f"(1) B44 {sorted(b44)[0]}-{sorted(b44)[-1]} disjoint from all "
      f"{len(stored)} stored b65 seeds: PASS")

# (2) clearing-SET identity vs the stored pooled table
import hashlib
lines = open("l162_static.py").read().split("\n")
NS = {}
exec(compile("\n".join(lines[0:106]), "slice", "exec"), NS)
l162 = json.load(open("l162/static.json"))
stored_clear = {f"{pa}~{pb}" for pa, pb in CP
                if l162["i1_pooled"][f"carrier|{pa}~{pb}"]["msc_matched_med"]
                >= 0.5}
h1 = r["held_out"]["H1_fresh_b65_B44"]
fresh_clear = {f"{pa}~{pb}" for (pa, pb), v in zip(CP, h1["carrier_vals"])
               if v >= 0.5}
inter = stored_clear & fresh_clear
jac = len(inter) / len(stored_clear | fresh_clear)
rho = float(np.corrcoef(
    np.argsort(np.argsort([l162["i1_pooled"][f"carrier|{pa}~{pb}"]
                           ["msc_matched_med"] for pa, pb in CP])),
    np.argsort(np.argsort(h1["carrier_vals"])))[0, 1])
print(f"(2) clearing SETS: stored {len(stored_clear)}/28, fresh "
      f"{len(fresh_clear)}/28, intersection {len(inter)}, Jaccard {jac:.3f}; "
      f"28-pair rank rho(stored, fresh) = {rho:+.3f}")
print(f"    stored-only: {sorted(stored_clear - fresh_clear)}")
print(f"    fresh-only : {sorted(fresh_clear - stored_clear)}")

# (3) inversion magnitude on H3 + the amplitude read
print("(3) H3 inversion (med_control - med_carrier), ptp vs b65:")
ptp_ref = h1["ptp_carrier_med"]
rows = {}
for t, v in sorted(r["held_out"].items()):
    if not t.startswith("H3_"):
        continue
    rows[t] = dict(delta=v["med_control"] - v["med_carrier"],
                   ratio=v["ratio"], ptp_frac=v["ptp_carrier_med"] / ptp_ref,
                   clears=v["n_clear_f"], clears_ctl=v["n_clear_f_control"])
    print(f"    {t:20s} delta {rows[t]['delta']:+.4f} ratio "
          f"{v['ratio']:.2f} | carrier ptp {v['ptp_carrier_med']:.4f} = "
          f"{rows[t]['ptp_frac']:.2f}x b65 | clears {v['n_clear_f']}/28 "
          f"carrier vs {v['n_clear_f_control']}/36 control")
n_inv = sum(1 for v in rows.values() if v["delta"] > 0)
amp_break = [t for t, v in rows.items() if v["ptp_frac"] >= 0.8]
print(f"    inverted on {n_inv}/{len(rows)} lesion arms; arms at b65-class "
      f"amplitude (>=0.8x) that still invert: {amp_break}")

json.dump(dict(disjoint=True, n_stored_seeds=len(stored),
               stored_clear=sorted(stored_clear),
               fresh_clear=sorted(fresh_clear),
               n_intersection=len(inter), jaccard=jac, rank_rho=rho,
               h3=rows, n_inverted=n_inv, amplitude_breakers=amp_break),
          open("l166/postcheck.json", "w"), indent=1)
print("l166/postcheck.json written")
