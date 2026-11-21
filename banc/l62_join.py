"""L62 banc-eval slice A part 2: JOINABILITY NUMBERS (read-only)."""
import pandas as pd
import numpy as np

D = "/home/t3rpz/critters/peabrain-lab/banc/data"
PUG = ["IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012"]

conn = pd.read_csv(f"{D}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
ann = pd.read_csv(f"{D}/dv_11845666", sep="\t", low_memory=False)
nt = pd.read_csv(f"{D}/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
mm = pd.read_csv(f"{D}/dv_11837145", low_memory=False,
                 usecols=["pt_root_id", "match_cell_type", "valid"])

pre = conn.pre_root_id.astype(np.uint64).to_numpy()
post = conn.post_root_id.astype(np.uint64).to_numpy()
conn_cells = np.unique(np.concatenate([pre, post]))
print(f"connection cells: {len(conn_cells):,}; pair-rows {len(conn):,}; "
      f"unique pairs {len(set(zip(pre.tolist(), post.tolist()))):,}")

ar = ann.pt_root_id.astype(np.uint64).to_numpy()
annset = set(ar.tolist())
cov = np.isin(conn_cells, list(annset))
print(f"annotated cells: {len(ann):,}; conn cells covered by annotations: "
      f"{cov.sum():,} ({cov.mean()*100:.1f}%)")
e_cov = np.isin(pre, list(annset)) & np.isin(post, list(annset))
print(f"edge rows with BOTH ends annotated: {e_cov.sum():,} ({e_cov.mean()*100:.1f}%) "
      f"of syn mass {conn.syn_count[e_cov].sum():,}/{conn.syn_count.sum():,}")

print("\n--- super_class distribution (annotated) ---")
sc = ann.super_class.fillna("NaN").value_counts()
for k, v in sc.items():
    print(f"  {k:>36} {v:>8,}")

print("\n--- NT join (root_626 -> annotations) ---")
ntmap = dict(zip(nt.root_626.astype(np.uint64), nt.neurotransmitter_predicted))
ann_nt = ann.pt_root_id.astype(np.uint64).map(ntmap)
joined = ann_nt.notna().sum()
print(f"NT joined {joined:,}/{len(ann):,} ({joined/len(ann)*100:.1f}%)")
print("NT mix (annotated, joined):")
print(ann_nt.value_counts().head(9).to_string())
ann["nt"] = ann_nt

print("\n--- motor / antagonist vocabulary (super_class==motor) ---")
mot = ann[ann.super_class == "motor"]
print(f"motor cells: {len(mot):,}")
for col in ["cell_class", "cell_sub_class"]:
    print(f"  {col}: {mot[col].fillna('NaN').value_counts().head(6).to_dict()}")
ptt = mot.peripheral_target_type.fillna("NaN")
flex = mot[ptt.str.contains("flexor", case=False)]
ext = mot[ptt.str.contains("extensor", case=False)]
print(f"  flexor-target MNs: {len(flex):,}; extensor-target: {len(ext):,}")
tf = flex[flex.peripheral_target_type.str.contains("tibia", case=False)]
te = ext[ext.peripheral_target_type.str.contains("tibia", case=False)]
print(f"  TIBIA flexor MNs: {len(tf):,}; TIBIA extensor MNs: {len(te):,}")
print("  tibia-flexor cell_type top:", tf.cell_type.value_counts().head(4).to_dict())
print("  tibia-extensor cell_type top:", te.cell_type.value_counts().head(4).to_dict())

print("\n--- descending vocabulary ---")
dn = ann[ann.super_class == "descending"]
print(f"descending cells: {len(dn):,}; classes: {dn.cell_class.fillna('NaN').value_counts().head(5).to_dict()}")
dnp = dn.cell_type.fillna("").str.match(r"^DN[a-z]?p?\d")
print(f"  DNp/DNg-style type names: {dnp.sum():,}; "
      f"sample types: {dn.cell_type.dropna().head(6).tolist()}")

print("\n--- Pugliese triad via MANC matches ---")
mv = mm[mm.valid == True] if mm.valid.dtype == bool else mm[mm.valid.astype(str) == "t"]
print(f"valid MANC matches: {len(mv):,}")
mt = mv.match_cell_type.astype(str)
for t in PUG:
    n = (mt == t).sum()
    print(f"  {t}: {n} BANC cells")
both = mv[mv.match_cell_type.astype(str).isin(PUG)]
print(f"  total triad cells: {len(both):,}")
manc_col = ann.manc_121_match_id.dropna().astype(str)
print(f"annotations w/ manc_121_match_id: {manc_col.size:,}; "
      f"triad hits there: {manc_col.isin(PUG).sum()}")

print("\n--- live-brain bridge: fafb_783_match_id ---")
f783 = ann.fafb_783_match_id.notna().sum()
print(f"annotated cells with v783 match id: {f783:,} "
      f"({f783/len(ann)*100:.1f}%) — direct join to the LIVE female brain")

print("\n--- region split ---")
print(ann.region.fillna("NaN").value_counts().head(8).to_string())
