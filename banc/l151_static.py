"""L151 static: substrate-gate statics — WHY is 1110's activity load-bearing
only on the cut base? Zero rollouts, no RNG. PREREG l151/PREREG.md FIRST
(registered before this run). Graphs G0=closure / G1=cutwA / G2=eAll built
VERBATIM from the l142_run.py extraction; metrics on global edge arrays,
|log1p(syn)*sign| masses (ladder convention); every pin asserted EXACT
before any new read (L44 rule). Output: l151/static.json + verdict table.
"""
import json
import time

import numpy as np
import pandas as pd
import torch

t0 = time.time()
ST = json.load(open("l107/static.json"))
S92 = json.load(open("l92/static.json"))
S101 = json.load(open("l101/static.json"))["sizes"]
S134 = json.load(open("l134/static.json"))
S131 = json.load(open("l131/static.json"))


def log(*a):
    print(*a, flush=True)


# ---------------- extraction (l142_run.py lines 76-124 verbatim) ----------------
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()

ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv("data/dv_11837016", low_memory=False,
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

conn = pd.read_csv("data/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = (conn["pre_root_id"].astype(np.uint64).isin(idx_all)
        & conn["post_root_id"].astype(np.uint64).isin(idx_all))
conn = conn[in_g]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into = dn_into & dn_all
dn_proj = np.zeros(Nall, bool)
dn_proj[src_all[cord_mask[dst_all]]] = True
dn_proj = dn_proj & dn_all
keep_old = cord_mask | dn_into
keep_new = cord_mask | dn_into | dn_proj
assert int(keep_old.sum()) == S92["n_old"] and int(keep_new.sum()) == S92["n_new"]

gsign_a = sign_all[src_all]
gsign_b = np.where(is_glut[src_all], -np.abs(gsign_a), gsign_a)
vals_all = (np.log1p(w_syn) * gsign_b).astype(np.float64)
emask_o = keep_old[src_all] & keep_old[dst_all]
emask_n = keep_new[src_all] & keep_new[dst_all]
added = emask_n & ~emask_o
gi_new = np.where(keep_new)[0]
gi_old = np.where(keep_old)[0]
dn_new_g = gi_new[~np.isin(gi_new, gi_old)]
assert len(dn_new_g) == S92["dn_new"]

# ---------------- ladder (l142_run.py verbatim, pins EXACT) ----------------
in_new_cell = np.zeros(Nall, bool)
in_new_cell[dn_new_g] = True
out_rows = added & in_new_cell[src_all]
tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup == "motor"]] = "motor_other"
tier_of_dst[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = \
    "vnc_sensory"
cord_of_dst = np.isin(tier_of_dst[dst_all],
                      ["motor_other", "intrinsic", "vnc_sensory"])
om = out_rows & cord_of_dst
outmass = np.zeros(Nall)
np.add.at(outmass, src_all[om], np.abs(vals_all[om]))
cell_mass = outmass[dn_new_g]
order = np.argsort(-cell_mass)
cum = np.cumsum(cell_mass[order]) / cell_mass.sum()
K = int(np.searchsorted(cum, 0.50) + 1)
assert (K, round(float(cum[K - 1]), 4)) == (ST["cut"]["K"], ST["cut"]["mass_share"])
heav = dn_new_g[order[:K]]
glut_desc = heav[is_glut[heav]]
ng_desc = heav[~is_glut[heav]]
assert len(glut_desc) == 19 and len(ng_desc) == 58
GI = 1110
assert int(ng_desc[24]) == GI and int(ng_desc[25]) == 319

keep_wA = keep_new.copy()
keep_wA[np.sort(ng_desc[:24])] = False
keep_25 = keep_new.copy()
keep_25[np.sort(ng_desc[:25])] = False
emask_wA = keep_wA[src_all] & keep_wA[dst_all]
emask_25 = keep_25[src_all] & keep_25[dst_all]
assert int(keep_wA.sum()) == 21785 and int(emask_wA.sum()) == 644177
assert int(keep_25.sum()) == 21784 and int(emask_25.sum()) == 644084
assert int(emask_n.sum()) == S92["edges_new"]
# l134 pins: 80 out (70 int / 10 motor), 13 in, raw out-mass EXACT
sel_out_n = emask_n & (src_all == GI)
assert int(sel_out_n.sum()) == 80
assert np.isclose(float(np.abs(vals_all[sel_out_n]).sum()),
                 183.96376182027785, rtol=0, atol=1e-9)
# 1110 out-edge SET identical on G0 and G1 (PREREG pin)
sel_out_wA = emask_wA & (src_all == GI)
assert np.array_equal(np.where(sel_out_n)[0], np.where(sel_out_wA)[0]), \
    "1110 out-edge set differs G0/G1 (STOP)"
sel_in_n = emask_n & (dst_all == GI)
sel_in_wA = emask_wA & (dst_all == GI)
assert int(sel_in_n.sum()) == 13 and int(sel_in_wA.sum()) == 13

T70 = np.zeros(Nall, bool)
T70[dst_all[sel_out_n & (tier_of_dst[dst_all] == "intrinsic")]] = True
T10 = np.zeros(Nall, bool)
T10[dst_all[sel_out_n & (tier_of_dst[dst_all] == "motor_other")]] = True
assert int(T70.sum()) == 70 and int(T10.sum()) == 10
assert int((T70 & keep_wA).sum()) == 70  # all kept on wA

# eAll edge set (l142 E_ARMS form): drop all 93 incident edges on the wA set
e_drop_all = (src_all == GI) | (dst_all == GI)
emask_eA = emask_wA & ~e_drop_all
assert int((emask_wA & e_drop_all).sum()) == 93
assert int(emask_eA.sum()) == 644084
# A0 re-verified (L142b law): eAll global edge positions == cutng25 node drop
assert np.array_equal(np.where(emask_eA)[0], np.where(emask_25)[0]), \
    "A0 eAll != cutng25 (STOP)"
log(f"[pins] ladder+graphs GREEN ({time.time()-t0:.0f}s)")

# ---------------- pools (l142 pools_for form, GLOBAL masks) ----------------
mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


POOL_G = {}
for k, fpat, epat, pf, pe in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor"), "f", "e"),
    ("Tr", has("trochanter") & has("flexor"),
     has("trochanter") & has("extensor"), "f", "e"),
    ("Ta", has("tarsus") & has("depressor"), has("tarsus") & has("levator"), "a", "b"),
    ("Sr", has("sternal") & has("anterior") & has("rotator"),
     has("sternal") & has("posterior") & has("rotator"), "a", "b"),
    ("Pr", has("promotor"), has("remotor"), "a", "b"),
]:
    for c in ("L", "R"):
        m1 = np.zeros(Nall, bool)
        m1[mgi[fpat & (side_m == SIDE_MAP[c])]] = True
        POOL_G[f"{k}_{pf}{c}"] = m1
        m2 = np.zeros(Nall, bool)
        m2[mgi[epat & (side_m == SIDE_MAP[c])]] = True
        POOL_G[f"{k}_{pe}{c}"] = m2
# pool size pins (l142 form, keep-intersected — pools_for applies keep[mgi]):
for pk, want in S92["pool_sizes"].items():
    assert int((POOL_G[pk] & keep_new).sum()) == want, (pk, int(POOL_G[pk].sum()), want)
    assert int((POOL_G[pk] & keep_wA).sum()) == want, (pk, "wA")
for pk, want in S101.items():
    if pk.split("_")[0] in ("Ti", "Tr"):
        continue
    assert int((POOL_G[pk] & keep_new).sum()) == want, (pk, want)
for k, (ag, bg) in {"Ti": ("f", "e"), "Tr": ("f", "e")}.items():
    for sd in ("L", "R"):
        assert (POOL_G[f"{k}_{ag}{sd}"] & keep_new).sum() == S101[f"{k}_a{sd}"]
        assert (POOL_G[f"{k}_{bg}{sd}"] & keep_new).sum() == S101[f"{k}_b{sd}"]
motor_G = np.zeros(Nall, bool)
motor_G[ann_gi[sup == "motor"]] = True
# NOTE: tier_of_dst marked ALL super_class=="motor" as motor_other — mirror it:
assert motor_G.sum() == (tier_of_dst == "motor_other").sum()
intr_G = np.zeros(Nall, bool)
intr_G[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = True
sens_G = np.zeros(Nall, bool)
sens_G[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = True

ng58_mask = np.zeros(Nall, bool)
ng58_mask[ng_desc] = True
win24_mask = np.zeros(Nall, bool)
win24_mask[ng_desc[:24]] = True

GRAPHS = {"G0_closure": (emask_n, keep_new),
          "G1_cutwA": (emask_wA, keep_wA),
          "G2_eAll": (emask_eA, keep_wA)}
CARRIER = np.zeros(Nall, bool)
CARRIER[GI] = True


def mass(E, src_mask=None, dst_mask=None):
    m = E.copy()
    if src_mask is not None:
        m &= src_mask[src_all]
    if dst_mask is not None:
        m &= dst_mask[dst_all]
    return float(np.abs(vals_all[m]).sum())


out = {"design": "L151 substrate-gate statics (PREREG l151/PREREG.md). "
       "Masses |log1p(syn)*sign| subnet-internal; denominators are in-mass "
       "sums on the same convention, disclosed per metric.",
       "carrier": {"gi": GI, "type": "DNp33", "side": "left", "ng_rank": 25},
       "s1_sheet": {}, "s2_pools": {}, "s3_motor": {}, "pins": "ALL GREEN"}

res_s1 = {}
for gname, (E, keep) in GRAPHS.items():
    dn_present = dn_all & keep
    m1110 = mass(E, src_mask=CARRIER, dst_mask=T70)
    ng_others = ng58_mask & keep & ~CARRIER
    m_ng = mass(E, src_mask=ng_others, dst_mask=T70)
    dn_rest = dn_present & ~ng58_mask & ~CARRIER
    m_dnr = mass(E, src_mask=dn_rest, dst_mask=T70)
    m_intr = mass(E, src_mask=intr_G, dst_mask=T70)
    m_sens = mass(E, src_mask=sens_G, dst_mask=T70)
    D = mass(E, dst_mask=T70)
    res_s1[gname] = dict(
        D_sheet=D, m1110=m1110, m_ng58_others=m_ng, m_dn_rest=m_dnr,
        m_intr_src=m_intr, m_sens_src=m_sens,
        m_other_src=D - m1110 - m_ng - m_dnr - m_intr - m_sens,
        share_1110_sheet=m1110 / D if D else None,
        share_1110_of_DNsheet=m1110 / (m1110 + m_ng + m_dnr)
        if (m1110 + m_ng + m_dnr) else None,
        redundancy_ratio=m_ng / m1110 if m1110 else None,
        n_ng_others_present=int((ng_others).sum()),
        n_dn_present=int(dn_present.sum()))
out["s1_sheet"] = res_s1
# consistency (PREREG): D_sheet(G2) == D_sheet(G1) - m1110  (in-edges touch only 1110)
assert abs(res_s1["G2_eAll"]["D_sheet"]
           - (res_s1["G1_cutwA"]["D_sheet"] - res_s1["G1_cutwA"]["m1110"])) < 1e-9
# 1110 signed out (context)
out["s1_sheet"]["signed_1110_out_G1"] = float(
    vals_all[emask_wA & (src_all == GI)].sum())

# S2 pools at entry depth
res_s2 = {}
for gname, (E, keep) in GRAPHS.items():
    dn_present = dn_all & keep
    # dn input mass per T70 cell
    dn_in = np.zeros(Nall)
    em = E & dn_present[src_all] & T70[dst_all]
    np.add.at(dn_in, dst_all[em], np.abs(vals_all[em]))
    w1110 = np.zeros(Nall)
    em1 = E & (src_all == GI) & T70[dst_all]
    np.add.at(w1110, dst_all[em1], np.abs(vals_all[em1]))
    row = {}
    for pk, P in POOL_G.items():
        Dp = mass(E, dst_mask=P)
        direct = mass(E, src_mask=CARRIER, dst_mask=P)
        e2 = E & T70[src_all] & P[dst_all]
        prod_dn = float((np.abs(vals_all[e2]) * dn_in[src_all[e2]]).sum())
        prod_11 = float((np.abs(vals_all[e2]) * w1110[src_all[e2]]).sum())
        row[pk] = dict(
            D_pool=Dp, direct_1110=direct,
            sheet_to_pool_share=float(np.abs(vals_all[e2]).sum()) / Dp if Dp else None,
            twohop_1110=prod_11, twohop_dn_total=prod_dn,
            twohop_share=prod_11 / prod_dn if prod_dn else None)
    res_s2[gname] = row
out["s2_pools"] = res_s2
# pins: direct_1110 == 0 for every pool on every graph (l134 pool_direct=0)
for g in res_s2:
    for pk in res_s2[g]:
        assert res_s2[g][pk]["direct_1110"] == 0.0, (g, pk)
# consistency: D_pool(G2) == D_pool(G1) - direct (=0)
for pk in POOL_G:
    assert abs(res_s2["G2_eAll"][pk]["D_pool"] - res_s2["G1_cutwA"][pk]["D_pool"]) < 1e-9

# S3 motor flank
res_s3 = {}
for gname, (E, keep) in GRAPHS.items():
    dn_present = dn_all & keep
    dn_in = np.zeros(Nall)
    em = E & dn_present[src_all] & T70[dst_all]
    np.add.at(dn_in, dst_all[em], np.abs(vals_all[em]))
    w1110 = np.zeros(Nall)
    em1 = E & (src_all == GI) & T70[dst_all]
    np.add.at(w1110, dst_all[em1], np.abs(vals_all[em1]))
    Dm = mass(E, dst_mask=motor_G)
    e2 = E & T70[src_all] & motor_G[dst_all]
    dmot = mass(E, src_mask=CARRIER, dst_mask=motor_G)
    res_s3[gname] = dict(
        D_motor=Dm,
        direct_1110_motor=dmot,
        share_direct=dmot / Dm,
        twohop_1110=float((np.abs(vals_all[e2]) * w1110[src_all[e2]]).sum()),
        twohop_dn_total=float((np.abs(vals_all[e2]) * dn_in[src_all[e2]]).sum()))
    res_s3[gname]["twohop_share"] = (
        res_s3[gname]["twohop_1110"] / res_s3[gname]["twohop_dn_total"]
        if res_s3[gname]["twohop_dn_total"] else None)
out["s3_motor"] = res_s3
assert abs(res_s3["G2_eAll"]["D_motor"]
           - (res_s3["G1_cutwA"]["D_motor"] - res_s3["G1_cutwA"]["direct_1110_motor"])) < 1e-9

# ---------------- verdict ----------------
s0, s1 = res_s1["G0_closure"], res_s1["G1_cutwA"]
leg1 = s1["share_1110_of_DNsheet"] / s0["share_1110_of_DNsheet"]
leg2 = s0["redundancy_ratio"] / s1["redundancy_ratio"]
hsub = bool(leg1 >= 3 and leg2 >= 3)
out["verdict"] = {
    "leg_share_ratio_G1_over_G0": leg1,
    "leg_redundancy_ratio_G0_over_G1": leg2,
    "H_SUB_fires": hsub,
    "label": "observation (card)"}
log("=" * 72)
log(f"S1 sheet (T70):           G0 closure   G1 cutwA    G2 eAll")
for kk in ("D_sheet", "m1110", "m_ng58_others", "m_dn_rest", "m_intr_src",
           "m_sens_src", "m_other_src"):
    log(f"  {kk:22s} {s0[kk]:11.2f} {s1[kk]:11.2f} "
        f"{res_s1['G2_eAll'][kk]:11.2f}")
log(f"  share_1110_sheet       {s0['share_1110_sheet']:.4f}      "
    f"{s1['share_1110_sheet']:.4f}       "
    f"{res_s1['G2_eAll']['share_1110_sheet']:.4f}")
log(f"  share_1110_of_DNsheet  {s0['share_1110_of_DNsheet']:.4f}      "
    f"{s1['share_1110_of_DNsheet']:.4f}       "
    f"{res_s1['G2_eAll']['share_1110_of_DNsheet'] if res_s1['G2_eAll']['share_1110_of_DNsheet'] is not None else float('nan'):.4f}")
log(f"  redundancy_ratio       {s0['redundancy_ratio']:.2f}        "
    f"{s1['redundancy_ratio']:.2f}         "
    f"{res_s1['G2_eAll']['redundancy_ratio'] if res_s1['G2_eAll']['redundancy_ratio'] is not None else float('nan'):.2f}")
log(f"  n_ng_others_present    {s0['n_ng_others_present']:11d} "
    f"{s1['n_ng_others_present']:11d} {res_s1['G2_eAll']['n_ng_others_present']:11d}")
log(f"H-SUB legs: share x{leg1:.2f} (>=3?), redundancy x{leg2:.2f} (>=3?) "
    f"-> {'FIRES' if hsub else 'does NOT fire'}")
log("-" * 72)
log("S2 pools (readout pools flagged *): D_pool / sheet_share / twohop_1110_share")
for pk in POOL_G:
    fl = "*" if pk in ("Ti_fL", "Ti_fR") else " "
    r0 = res_s2["G0_closure"][pk]
    r1 = res_s2["G1_cutwA"][pk]
    r2 = res_s2["G2_eAll"][pk]
    log(f"  {pk:6s}{fl} D {r0['D_pool']:8.1f}/{r1['D_pool']:8.1f}/{r2['D_pool']:8.1f}"
        f"  sheet {r0['sheet_to_pool_share']:.3f}/{r1['sheet_to_pool_share']:.3f}"
        f"/{r2['sheet_to_pool_share']:.3f}"
        f"  2hop11 {(r0['twohop_share'] or 0):.3f}/{(r1['twohop_share'] or 0):.3f}"
        f"/{(r2['twohop_share'] or 0):.3f}")
log("-" * 72)
for g in res_s3:
    r = res_s3[g]
    log(f"S3 {g:11s} D_motor {r['D_motor']:.0f} direct1110 {r['direct_1110_motor']:.2f}"
        f" ({r['share_direct']*100:.2f}%) twohop_share {r['twohop_share']}")
log("=" * 72)
json.dump(out, open("l151/static.json", "w"), indent=1)
log(f"written l151/static.json ({time.time()-t0:.0f}s)")
