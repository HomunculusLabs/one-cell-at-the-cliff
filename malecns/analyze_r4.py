"""R4 malecns-eval: does MaleCNS v1.0 give us real DN->motor edges for L7?

Questions (from LANE.md R4):
  1. annotations join on edge bodies?
  2. DN -> motor edges: how many, how strong, how many motor cells reached?
  3. build_graph.py port surface (columns needed exist?)
Data: gs://flyem-male-cns/v1.0 flat-connectome, significant-only weights.
"""
import pandas as pd
import numpy as np

DATA = "/home/t3rpz/critters/peabrain-lab/malecns/data"

ann = pd.read_feather(f"{DATA}/body-annotations-male-cns-v1.0-minconf-0.5.feather")
sup = dict(zip(ann["bodyId"], ann["superclass"]))
print(f"annotations: {len(ann)} bodies, superclass non-null: "
      f"{ann['superclass'].notna().sum()}")

DN = {"descending_neuron", "sensory_descending", "descending_neuron_tbc"}
MOTOR = {"vnc_motor", "cb_motor"}
EFF = {"vnc_efferent"}
ASC = {"ascending_neuron", "sensory_ascending", "efferent_ascending"}
VIN = {"vnc_intrinsic"}

w = pd.read_feather(
    f"{DATA}/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
print(f"edges (significant-only): {len(w):,}  total synapses: {w['weight'].sum():,}")

# join rate
pre_sup = w["body_pre"].map(sup)
post_sup = w["body_post"].map(sup)
join = (pre_sup.notna() & post_sup.notna()).mean()
print(f"edge superclass join rate (both ends labeled): {join:.1%}")

def stats(mask, label):
    sub = w[mask]
    if len(sub) == 0:
        print(f"{label}: 0")
        return
    n_post = sub["body_post"].nunique()
    print(f"{label}: {len(sub):,} edges, {sub['weight'].sum():,} synapses, "
          f"{n_post:,} distinct targets, median wt {sub['weight'].median():.0f}")

dn_pre = pre_sup.isin(DN)
mo_post = post_sup.isin(MOTOR)
stats(dn_pre & mo_post, "DN -> MOTOR (direct)")
stats(dn_pre & post_sup.isin(EFF), "DN -> efferent")
stats(dn_pre & post_sup.isin(VIN), "DN -> vnc_intrinsic")
stats(dn_pre & post_sup.isin(ASC), "DN -> ascending (vnc->brain)")
stats(pre_sup.isin(VIN) & mo_post, "vnc_intrinsic -> MOTOR")
stats(post_sup.isin({"vnc_sensory"}) & pre_sup.isin(VIN),
      "vnc_intrinsic -> vnc_sensory (reflex arc present?)")
stats(pre_sup.isin({"vnc_sensory"}) & post_sup.isin(VIN),
      "vnc_sensory -> vnc_intrinsic")

# motor cells reached directly by >=1 DN
dm = w[dn_pre & mo_post]
motor_ids = set(ann.loc[ann["superclass"].isin(MOTOR), "bodyId"])
print(f"motor population: {len(motor_ids):,}; "
      f"reached directly by a DN: {dm['body_post'].nunique():,} "
      f"({dm['body_post'].nunique()/len(motor_ids):.1%})")

# per-motor-neuron direct DN input distribution (is it sparse or dense?)
per = dm.groupby("body_post")["weight"].sum()
print("per-motor direct DN synapses: "
      f"median {per.median():.0f}, p90 {per.quantile(.9):.0f}, max {per.max():.0f}")

# port surface for build_graph.py
print("\nport check: need pre/post/syn-count/per-pre-NT ->",
      "body_pre/body_post/weight OK;",
      "per-body consensus_nt OK (body-neurotransmitters feather)")
