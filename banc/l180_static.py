"""L180 static: floor-sensitivity of the BANC-side cohort rule.

ZERO rollouts, zero RNG, no graph build. Extraction copied VERBATIM from
l92_static.py up to the keep rule (L85 rule: never re-invent a certified
derivation). C0S-180 CERT runs FIRST and halts on mismatch; the floor
histogram prints before any counterfactual number.

PREREG: l180/PREREG.md
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

t0 = time.time()
DATA = "data"
OUT = "l180"
INPUTS = [f"{DATA}/dv_11842997", f"{DATA}/dv_11845666", f"{DATA}/dv_11837016",
          "banc_graph.pt", "l92/static.json", "l170/static.json"]
mt0 = {p: os.stat(p).st_mtime_ns for p in INPUTS}

pin = json.load(open("l92/static.json"))
male = json.load(open("l170/static.json"))

# ---------------- extraction, VERBATIM from l92_static.py ----------------
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()

ann = pd.read_csv(f"{DATA}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv(f"{DATA}/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64),
                  nt["neurotransmitter_predicted"].astype(str).str.lower()))
is_glut = np.zeros(Nall, bool)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate":
        is_glut[j] = True

region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True

conn = pd.read_csv(f"{DATA}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all)
            & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True


def cohort(emask):
    """dn_into / dn_proj / dn_new under an edge subset mask (l92 keep rule)."""
    s, d = src_all[emask], dst_all[emask]
    di = np.zeros(Nall, bool)
    di[d[cord_mask[s]]] = True
    di &= dn_all
    dp = np.zeros(Nall, bool)
    dp[s[cord_mask[d]]] = True
    dp &= dn_all
    return di, dp, dp & ~di


all_e = np.ones(len(src_all), bool)
dn_into, dn_proj, dn_new = cohort(all_e)
keep_old = cord_mask | dn_into
keep_new = cord_mask | dn_into | dn_proj
n_old, n_new = int(keep_old.sum()), int(keep_new.sum())


def build(keep):
    emask = keep[src_all] & keep[dst_all]
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    lsrc, ldst = loc[gsrc], loc[gdst]
    gsign_a = sign_all[gsrc]
    gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
    vals = (np.log1p(gcount) * gsign_b).astype(np.float32)
    return lsrc, ldst, vals, loc


lsrc_o, ldst_o, vals_o, loc_o = build(keep_old)
lsrc_n, ldst_n, vals_n, loc_n = build(keep_new)

cls_new = np.zeros(n_new, np.int8)
gi_new = np.where(keep_new)[0]
cls_new[np.isin(gi_new, np.where(dn_into)[0])] = 1
cls_new[np.isin(gi_new, np.where(dn_new)[0])] = 2
blk = {}
for a in (0, 1, 2):
    for b in (0, 1, 2):
        m = (cls_new[lsrc_n] == a) & (cls_new[ldst_n] == b)
        blk[f"{['cord','DNi','DNn'][a]}->{['cord','DNi','DNn'][b]}"] = int(m.sum())

mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


POOLS = {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"), has("trochanter") & has("extensor")),
]:
    for c in ("fL", "fR", "eL", "eR"):
        sel = fpat if c[0] == "f" else epat
        m = keep_new[mgi] & sel & (side_m == SIDE_MAP[c[1].upper()])
        POOLS[f"{k}_{c}"] = np.sort(loc_n[mgi[m]])
pool_sizes = {k: len(v) for k, v in POOLS.items()}

motor_g = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor_new = np.zeros(n_new, bool)
motor_new[loc_n[motor_g[keep_new[motor_g]]]] = True
cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech_new = np.where(mech_mask[keep_new])[0]
sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100_new = np.sort(loc_n[dng100_all[keep_new[dng100_all]]])
dn46_all = sub_dn.gi[ct_dn == "DNge046"].to_numpy()
in_new46 = keep_new[dn46_all]
d46_pos = np.sort(loc_n[dn46_all[in_new46]])

# ---------------- C0S-180 CERT (FIRST, halts on mismatch) ----------------
checks = []


def chk(name, got, want):
    checks.append(dict(name=name, got=got, want=want, ok=bool(got == want)))


chk("n_old", n_old, pin["n_old"])
chk("n_new", n_new, pin["n_new"])
chk("cord", int(cord_mask.sum()), pin["cord"])
chk("dn_into", int(dn_into.sum()), pin["dn_into"])
chk("dn_proj", int(dn_proj.sum()), pin["dn_proj"])
chk("dn_new", int(dn_new.sum()), pin["dn_new"])
chk("edges_old", int(len(lsrc_o)), pin["edges_old"])
chk("edges_new", int(len(lsrc_n)), pin["edges_new"])
for k, v in pin["blocks"].items():
    chk(f"block_{k}", blk[k], v)
for k, v in pin["pool_sizes"].items():
    chk(f"pool_{k}", pool_sizes[k], v)
chk("mech", int(len(mech_new)), pin["mech"])
chk("motor", int(motor_new.sum()), pin["motor"])
chk("dng100", int(len(dng100_new)), pin["dng100"])
chk("dn46_in_subnet", int(in_new46.sum()), pin["dn46_in_subnet"])
chk("dn46_pos", [int(x) for x in d46_pos], pin["dn46_pos"])
n_fail = sum(1 for c in checks if not c["ok"])
print(f"C0S-180 CERT: {len(checks)-n_fail}/{len(checks)} exact, fails={n_fail}")
if n_fail:
    for c in checks:
        if not c["ok"]:
            print("  FAIL", c)
    raise SystemExit("CERT FAILED — no counterfactual number reported")

# ---------------- FLOOR REPORT FIRST (L146 rule) ----------------
cd_e = cord_mask[src_all] & dn_all[dst_all]          # cord -> DN class
dc_e = dn_all[src_all] & cord_mask[dst_all]          # DN -> cord class
hist_all = {int(k): int(v) for k, v in
            zip(*np.unique(np.minimum(w_syn, 12).astype(int),
                           return_counts=True))}
hist_cd = {int(k): int(v) for k, v in
           zip(*np.unique(np.minimum(w_syn[cd_e], 12).astype(int),
                          return_counts=True))}
floor_report = dict(
    pairs_total=int(len(w_syn)), min_syn_all=float(w_syn.min()),
    min_syn_cord_to_dn=float(w_syn[cd_e].min()),
    n_cord_to_dn=int(cd_e.sum()), n_dn_to_cord=int(dc_e.sum()),
    hist_all_capped12=hist_all, hist_cord_to_dn_capped12=hist_cd,
    l146_floor3_holds=bool(w_syn.min() == 3.0),
)
print("FLOOR REPORT:", json.dumps(floor_report, indent=1))
assert w_syn.min() == 3.0, "L146 pin broken — halt and disclose"

# ---------------- M1/M2 marginality censuses ----------------
def census(emask, cellmask, keyed_by_dst):
    s, d = src_all[emask], dst_all[emask]
    key = d if keyed_by_dst else s
    cnt = np.zeros(Nall, np.int64)
    np.add.at(cnt, key, 1)
    mx = np.zeros(Nall, np.float64)
    np.maximum.at(mx, key, w_syn[emask])
    tot = np.zeros(Nall, np.float64)
    np.add.at(tot, key, w_syn[emask])
    g = np.where(cellmask)[0]
    return g, cnt[g], mx[g], tot[g]


ct_g = np.full(Nall, "", dtype=object)
sd_g = np.full(Nall, "", dtype=object)
ct_g[ann_gi] = ann.cell_type.fillna("").astype(str).to_numpy()
sd_g[ann_gi] = ann.side.fillna("").astype(str).str.upper().to_numpy()

gi_i, cnt_i, mx_i, tot_i = census(cd_e, dn_into, True)
gi_p, cnt_p, mx_p, tot_p = census(dc_e, dn_new, False)


def q(a):
    return [float(np.percentile(a, p)) for p in (25, 50, 75)] + [float(a.max())]


m1 = dict(
    n_cells=int(len(gi_i)),
    single_pair=int((cnt_i == 1).sum()),
    single_pair_frac=round(float((cnt_i == 1).mean()), 4),
    maxsyn_eq3=int((mx_i == 3).sum()), maxsyn_le4=int((mx_i <= 4).sum()),
    maxsyn_le5=int((mx_i <= 5).sum()), maxsyn_le9=int((mx_i <= 9).sum()),
    inpair_q25_med_q75_max=q(cnt_i), maxsyn_q25_med_q75_max=q(mx_i),
    totsyn_q25_med_q75_max=q(tot_i),
    single_and_3syn=int(((cnt_i == 1) & (mx_i == 3)).sum()),
)
m2 = dict(
    n_cells=int(len(gi_p)),
    single_pair=int((cnt_p == 1).sum()),
    single_pair_frac=round(float((cnt_p == 1).mean()), 4),
    maxsyn_eq3=int((mx_p == 3).sum()), maxsyn_le4=int((mx_p <= 4).sum()),
    maxsyn_le5=int((mx_p <= 5).sum()),
    outpair_q25_med_q75_max=q(cnt_p), maxsyn_q25_med_q75_max=q(mx_p),
    single_and_3syn=int(((cnt_p == 1) & (mx_p == 3)).sum()),
)
print("M1 dn_into marginality:", json.dumps(m1, indent=1))
print("M2 dn_new admitting side:", json.dumps(m2, indent=1))

pd.DataFrame(dict(gi=gi_i, cell_type=[str(ct_g[g]) for g in gi_i],
                  side=[str(sd_g[g]) for g in gi_i],
                  in_pairs=cnt_i, maxsyn=mx_i, totsyn=tot_i)).to_csv(
    f"{OUT}/census_dn_into.csv", index=False)
pd.DataFrame(dict(gi=gi_p, cell_type=[str(ct_g[g]) for g in gi_p],
                  side=[str(sd_g[g]) for g in gi_p],
                  out_pairs=cnt_p, maxsyn=mx_p, totsyn=tot_p)).to_csv(
    f"{OUT}/census_dn_new.csv", index=False)

# ---------------- M3 ladder, two declared regimes ----------------
base_new_set = set(np.where(dn_new)[0].tolist())
ladder = {}
for f in (3, 4, 5, 6, 10):
    # regime A: GLOBAL floor (mirror of L170 edges_kept)
    emA = w_syn >= f
    diA, dpA, dnA = cohort(emA)
    keepA = cord_mask | diA | dpA
    eA = int((keepA[src_all] & keepA[dst_all] & emA).sum())
    keepA_old = cord_mask | diA
    eA_old = int((keepA_old[src_all] & keepA_old[dst_all] & emA).sum())
    setA = set(np.where(dnA)[0].tolist())
    mig = len(setA - base_new_set)
    evi = len(base_new_set - setA)
    stay = len(base_new_set & setA)
    # regime B: cord->DN ONLY floor (dn_proj held at baseline)
    emB = ~cd_e | (w_syn >= f)
    diB, _, _ = cohort(emB)
    dnB = dn_proj & ~diB
    ladder[str(f)] = dict(
        floor=f, edges_kept_global=int(emA.sum()),
        A=dict(dn_into=int(diA.sum()), dn_proj=int(dpA.sum()),
               dn_new=int(dnA.sum()), n_new=int(keepA.sum()),
               n_old=int(keepA_old.sum()), edges_new=eA, edges_old=eA_old,
               migration_in=mig, eviction=evi, stay=stay),
        B=dict(dn_into=int(diB.sum()), dn_proj=int(dn_proj.sum()),
               dn_new=int(dnB.sum()),
               evicted_from_dn_into=int(dn_into.sum()) - int(diB.sum())),
    )
    print(f"  floor {f}: " + json.dumps(ladder[str(f)]))

# ---------------- M5 sensitivity, stated beside the male ----------------
a3, a4, a5 = (ladder[k]["A"]["dn_new"] for k in ("3", "4", "5"))
b3, b4, b5 = (ladder[k]["B"]["dn_new"] for k in ("3", "4", "5"))
male_v = male["verdict"]
male_l = male["ladder"]
m5 = dict(
    banc_A_3=a3, banc_A_4=a4, banc_A_5=a5,
    banc_rel_change_3to5_A=round((a5 - a3) / a3, 4),
    banc_step_3to4_A=round((a4 - a3) / a3, 4),
    banc_rel_change_3to5_B=round((b5 - b3) / b3, 4),
    banc_step_3to4_B=round((b4 - b3) / b3, 4),
    male_dn_new_1=male_v["dn_new_1"], male_dn_new_3=male_v["dn_new_3"],
    male_rel_change_1to3=male_v["rel_change"],
    male_dn_new_2=male_l["2"]["s1"]["dn_new"],
    male_step_2to3=round((male_l["3"]["s1"]["dn_new"]
                          - male_l["2"]["s1"]["dn_new"])
                         / male_l["2"]["s1"]["dn_new"], 4),
    span_note=("male span is floors 1->3; BANC's admissible span is 3->5 "
               "because the v626 release's own pair floor is 3 (L146) — the "
               "spans are NOT rung-matched; the rung-matched comparison is "
               "BANC 3->4 against male 2->3"),
)
evict_frac_A = ladder["4"]["A"]["eviction"] / max(1, a3)
into_evict_frac = (int(dn_into.sum()) - ladder["4"]["A"]["dn_into"]) / int(dn_into.sum())
q4_cond1 = abs((a4 - a3) / a3) < male_v["rel_change"]
q4_cond2 = into_evict_frac < 0.10
verdict = dict(
    branch="B_ROBUST" if (q4_cond1 and q4_cond2) else "B_FRAGILE",
    Q1_banc_step_smaller=bool(abs(m5["banc_step_3to4_A"])
                              < abs(m5["male_step_2to3"])),
    Q2_not_single_edge=bool(m1["single_pair_frac"] < 0.25),
    Q3_B_rises=bool(b4 >= b3 and b5 >= b4),
    Q4_cond1_move_lt_male=bool(q4_cond1), Q4_cond2_evict_lt_10pct=bool(q4_cond2),
    dn_into_evicted_frac_f4=round(float(into_evict_frac), 4),
    dn_new_evicted_frac_f4=round(float(evict_frac_A), 4),
    vacuous_f4=bool(ladder["4"]["edges_kept_global"] == len(w_syn)),
    subnet_n_new_change_3to5=round(
        (ladder["5"]["A"]["n_new"] - ladder["3"]["A"]["n_new"])
        / ladder["3"]["A"]["n_new"], 5),
    cohort_relabel_frac_f4=round(
        ladder["4"]["B"]["evicted_from_dn_into"] / int(dn_into.sum()), 4),
    single_3syn_frac_of_dn_into=round(m1["single_and_3syn"]
                                      / m1["n_cells"], 4),
    sparsity_ratio_dc_over_cd=round(float(dc_e.sum()) / float(cd_e.sum()), 3),
)
print("M5:", json.dumps(m5, indent=1))
print("VERDICT:", json.dumps(verdict, indent=1))

mt1 = {p: os.stat(p).st_mtime_ns for p in INPUTS}
res = dict(
    cert=dict(n=len(checks), n_fail=n_fail, checks=checks),
    floor_report=floor_report, m1_dn_into=m1, m2_dn_new=m2,
    ladder=ladder, m5=m5, verdict=verdict,
    mtimes_unchanged=bool(mt0 == mt1), wall_s=round(time.time() - t0, 1),
)
json.dump(res, open(f"{OUT}/results_l180.json", "w"), indent=1)
print(f"done {res['wall_s']}s  mtimes_unchanged={res['mtimes_unchanged']}")
