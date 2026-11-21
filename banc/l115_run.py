"""L115 run: random-19-subset flip control. PREREG l115/PREREG.md FIRST.

L113 machinery VERBATIM (graphs, gains, draw order); arms full/b65/cut/
cut19 identical (anchors vs raw_l113; ZERO new draws), cutR1/cutR2/cutR3
NEW = closure minus RANDOM 19-of-heavy-77 subsets (numpy default_rng(1150),
positional picks on the mass-order heavy array; torch RNG untouched).
Seeds: anchors [801, 901] vs raw_l113 + FRESH B11 1501-1516 (verified
absent pre-launch). g_cut + g_cut19 re-bisected + asserted == stored
EXACT (both); g_cutR1-3 bisected fresh (disclosed). CPU-only; raw
checkpoint BEFORE analysis.
"""
import json
import math
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN = 400, 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
BETA, D = 2.0, 0.2
ENT_AMP = 0.1
G_NEW, G65 = 0.153125, 0.14
GH = G_NEW
AF_T = 0.10905611018339793
ARMS = ["full", "b65", "cut", "cut19", "cutR1", "cutR2", "cutR3"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None,
            cutR1=None, cutR2=None, cutR3=None)
G_CUT19_STORED = 0.15096808075904844  # l111 stored, PREREG C0A(c19)
G_CUT_STORED = 0.14510760426521305  # l107 stored, PREREG C0A(c)
ANCH = [801, 901]                   # bit-identity anchors (excluded from sample)
B11 = list(range(1501, 1517))       # fresh, verified absent pre-launch
SEEDS = ANCH + B11                  # anchors FIRST: early wiring verdict
FRESH = B11
ST = json.load(open("l107/static.json"))
S92 = json.load(open("l92/static.json"))
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------------- extraction (l94_run.py verbatim) ----------------
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

# cut rule (l107/static.json): closure minus top-K dn_new by cord out-mass
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
in_new_cell = np.zeros(Nall, bool)
in_new_cell[dn_new_g] = True
out_rows = added & in_new_cell[src_all]

reg_ann = region
sup_ann = sup
tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup_ann == "motor"]] = "motor_other"
tier_of_dst[ann_gi[sup_ann == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup_ann == "sensory")
                   & (reg_ann == "ventral_nerve_cord")]] = "vnc_sensory"
cord_of_dst = np.isin(tier_of_dst[dst_all],
                      ["motor_other", "intrinsic", "vnc_sensory"])
om = out_rows & cord_of_dst
outmass = np.zeros(Nall)
np.add.at(outmass, src_all[om], np.abs(vals_all[om]))
cell_mass = outmass[dn_new_g]
order = np.argsort(-cell_mass)
cum = np.cumsum(cell_mass[order]) / cell_mass.sum()
K = int(np.searchsorted(cum, 0.50) + 1)
cut_drop = np.sort(dn_new_g[order[:K]])
keep_cut = keep_new.copy()
keep_cut[cut_drop] = False
assert (K, round(float(cum[K - 1]), 4)) == (ST["cut"]["K"], ST["cut"]["mass_share"])
assert int(keep_cut.sum()) == ST["n_cut"]
# L111: glutamatergic subset of the heavy-77 (l110 addendum: 19/77, z +5.9)
heav = dn_new_g[order[:K]]
cut19_drop = np.sort(heav[is_glut[heav]])
assert len(cut19_drop) == 19, f"glut heavy = {len(cut19_drop)} != 19 (STOP)"
keep_cut19 = keep_new.copy()
keep_cut19[cut19_drop] = False
n_cut19 = int(keep_cut19.sum())
assert n_cut19 == int(keep_new.sum()) - 19
_mass_heavy = cell_mass[order[:K]]
mass_split = dict(
    glut19=round(float(_mass_heavy[is_glut[heav]].sum() / cell_mass.sum()), 4),
    other58=round(float(_mass_heavy[~is_glut[heav]].sum() / cell_mass.sum()), 4))
assert mass_split == {"glut19": 0.1103, "other58": 0.3921}, mass_split
# L115: RANDOM 19-of-heavy-77 subsets — numpy RNG only (DISJOINT from the
# torch settle/noise generators; draw order untouched). Picks are POSITIONAL
# on heav (mass-desc order); 3 unconditional draws, asserted distinct.
rng = np.random.default_rng(1150)
rand_picks = [np.sort(rng.choice(K, size=19, replace=False)) for _ in range(3)]
assert len({tuple(p) for p in rand_picks}) == 3, "random draws collided (STOP)"
rand_mass, rand_glut = [], []
cutR_drop = {}
for i, _pick in enumerate(rand_picks, 1):
    _drop = np.sort(heav[_pick])
    cutR_drop[i] = _drop
    keep_v = keep_new.copy()
    keep_v[_drop] = False
    globals()[f"keep_cutR{i}"] = keep_v
    globals()[f"n_cutR{i}"] = int(keep_v.sum())
    assert int(keep_v.sum()) == int(keep_new.sum()) - 19
    rand_mass.append(round(float(_mass_heavy[_pick].sum() / cell_mass.sum()), 4))
    rand_glut.append(int(is_glut[heav[_pick]].sum()))


def build(keep):
    emask = keep[src_all] & keep[dst_all]
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    lsrc, ldst = loc[gsrc], loc[gdst]
    gsign_a2 = sign_all[gsrc]
    gsign_b2 = np.where(is_glut[gsrc], -np.abs(gsign_a2), gsign_a2)
    vals = (np.log1p(gcount) * gsign_b2).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([ldst, lsrc])).long(),
        torch.from_numpy(vals), (int(keep.sum()), int(keep.sum()))
    ).coalesce().to_sparse_csr()
    return W, loc


def wb(W):
    neg = W.values() < 0
    vals = W.values().clone()
    vals[neg] *= BETA
    return torch.sparse_csr_tensor(W.crow_indices(), W.col_indices(), vals, W.shape)


Wc_o, loc_o = build(keep_old)
Wc_n, loc_n = build(keep_new)
Wc_c, loc_c = build(keep_cut)
Wc_c19, loc_c19 = build(keep_cut19)
Wc_cR1, loc_cR1 = build(keep_cutR1)
Wc_cR2, loc_cR2 = build(keep_cutR2)
Wc_cR3, loc_cR3 = build(keep_cutR3)
assert Wc_o.values().numel() == S92["edges_old"]
assert Wc_n.values().numel() == S92["edges_new"]
assert Wc_c.values().numel() == ST["edges_cut"]
Wb_o, Wb_n, Wb_c, Wb_c19 = (wb(Wc_o), wb(Wc_n), wb(Wc_c), wb(Wc_c19))
Wb_cR1, Wb_cR2, Wb_cR3 = wb(Wc_cR1), wb(Wc_cR2), wb(Wc_cR3)

n_old, n_new, n_cut = int(keep_old.sum()), int(keep_new.sum()), int(keep_cut.sum())
n_add = len(dn_new_g)
new_g = dn_new_g
old_pos_in_new = loc_n[gi_old]
new_pos = loc_n[new_g]
old_pos_in_cut = loc_c[gi_old]
gi_cut = np.where(keep_cut)[0]
cut_pos_in_new = loc_n[gi_cut]
kept_new_mask = keep_cut[new_g]                      # new_g order
kept_new_cut = loc_c[new_g[kept_new_mask]]           # cut-local of kept new
gi_cut19 = np.where(keep_cut19)[0]
cut19_pos_in_new = loc_n[gi_cut19]
old_pos_in_c19 = loc_c19[gi_old]
kept_new_mask19 = keep_cut19[new_g]                  # new_g order
kept_new_cut19 = loc_c19[new_g[kept_new_mask19]]     # cut19-local of kept new
gi_cutR1 = np.where(keep_cutR1)[0]
cutR1_pos_in_new = loc_n[gi_cutR1]
old_pos_in_cR1 = loc_cR1[gi_old]
kept_new_maskR1 = keep_cutR1[new_g]                  # new_g order
kept_new_cutR1 = loc_cR1[new_g[kept_new_maskR1]]     # cutR1-local of kept new
gi_cutR2 = np.where(keep_cutR2)[0]
cutR2_pos_in_new = loc_n[gi_cutR2]
old_pos_in_cR2 = loc_cR2[gi_old]
kept_new_maskR2 = keep_cutR2[new_g]                  # new_g order
kept_new_cutR2 = loc_cR2[new_g[kept_new_maskR2]]     # cutR2-local of kept new
gi_cutR3 = np.where(keep_cutR3)[0]
cutR3_pos_in_new = loc_n[gi_cutR3]
old_pos_in_cR3 = loc_cR3[gi_old]
kept_new_maskR3 = keep_cutR3[new_g]                  # new_g order
kept_new_cutR3 = loc_cR3[new_g[kept_new_maskR3]]     # cutR3-local of kept new

# pools / mech / motor / dng100 per graph
mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


def pools_for(loc, keep):
    out = {}
    for k, fpat, epat in [
        ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
        ("Tr", has("trochanter") & has("flexor"),
         has("trochanter") & has("extensor")),
    ]:
        for c in ("fL", "fR", "eL", "eR"):
            sel = fpat if c[0] == "f" else epat
            m = keep[mgi] & sel & (side_m == SIDE_MAP[c[1].upper()])
            out[f"{k}_{c}"] = np.sort(loc[mgi[m]])
    return out


POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "cutR1": pools_for(loc_cR1, keep_cutR1),
         "cutR2": pools_for(loc_cR2, keep_cutR2),
         "cutR3": pools_for(loc_cR3, keep_cutR3),
         "b65": pools_for(loc_o, keep_old)}
for pk, want in S92["pool_sizes"].items():
    assert len(POOLS["full"][pk]) == want, pk
    assert len(POOLS["cut"][pk]) == want and len(POOLS["b65"][pk]) == want
    assert len(POOLS["cut19"][pk]) == want, pk
    for _ra in ("cutR1", "cutR2", "cutR3"):
        assert len(POOLS[_ra][pk]) == want, (_ra, pk)

cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "cutR1": np.where(mech_mask[keep_cutR1])[0],
        "cutR2": np.where(mech_mask[keep_cutR2])[0],
        "cutR3": np.where(mech_mask[keep_cutR3])[0],
        "b65": np.where(mech_mask[keep_old])[0]}
assert len(mech["full"]) == S92["mech"]

mg_all = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cutR1", n_cutR1), ("cutR2", n_cutR2), ("cutR3", n_cutR3),
          ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19),
                     ("cutR1", keep_cutR1, loc_cR1),
                     ("cutR2", keep_cutR2, loc_cR2),
                     ("cutR3", keep_cutR3, loc_cR3),
                     ("b65", keep_old, loc_o)):
    motor[a][loc[mg_all[keep[mg_all]]]] = True

sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
# L115 static pin (pre-verified pre-launch; STOP if violated): NO DNg100
# cell sits in the heavy-77, so no random draw can touch the drive channel.
assert not np.isin(dng100_all, cut_drop).any(), "DNg100 in heavy-77 (STOP)"
dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "cutR1": np.sort(loc_cR1[dng100_all[keep_cutR1[dng100_all]]]),
          "cutR2": np.sort(loc_cR2[dng100_all[keep_cutR2[dng100_all]]]),
          "cutR3": np.sort(loc_cR3[dng100_all[keep_cutR3[dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}
assert len(dng100["full"]) == S92["dng100"]
for _ra in ("cutR1", "cutR2", "cutR3"):
    assert len(dng100[_ra]) == S92["dng100"], _ra
WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19,
      "cutR1": Wb_cR1, "cutR2": Wb_cR2, "cutR3": Wb_cR3, "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19,
        "cutR1": n_cutR1, "cutR2": n_cutR2, "cutR3": n_cutR3, "b65": n_old}

AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
log(f"graphs built {time.time()-t0:.0f}s | K {K} n_cut {n_cut:,} "
    f"edges_cut {Wc_c.values().numel():,}")


# ---------------- settle machinery (l94 two-generator form) ----------------
def settle_states(seed, gains):
    """Draw per l94 order; settle all arms under `gains[arm]`."""
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    Xc_full = torch.zeros(n_new, 1)
    Xc_full[old_pos_in_new] = X0o
    Xc_full[new_pos] = X0n
    Xc_cut = torch.zeros(n_cut, 1)
    Xc_cut[old_pos_in_cut] = X0o
    Xc_cut[kept_new_cut] = X0n[kept_new_mask]
    Xc_cut19 = torch.zeros(n_cut19, 1)
    Xc_cut19[old_pos_in_c19] = X0o
    Xc_cut19[kept_new_cut19] = X0n[kept_new_mask19]
    Xc_cR1 = torch.zeros(n_cutR1, 1)
    Xc_cR1[old_pos_in_cR1] = X0o
    Xc_cR1[kept_new_cutR1] = X0n[kept_new_maskR1]
    Xc_cR2 = torch.zeros(n_cutR2, 1)
    Xc_cR2[old_pos_in_cR2] = X0o
    Xc_cR2[kept_new_cutR2] = X0n[kept_new_maskR2]
    Xc_cR3 = torch.zeros(n_cutR3, 1)
    Xc_cR3[old_pos_in_cR3] = X0o
    Xc_cR3[kept_new_cutR3] = X0n[kept_new_maskR3]
    Xo65 = X0o.clone()
    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), cutR1=Xc_cR1.clone(),
              cutR2=Xc_cR2.clone(), cutR3=Xc_cR3.clone(),
              b65=Xo65.clone())
    I = {}
    for a in ARMS:
        Iv = torch.zeros(N_OF[a], 1)
        Iv[dng100[a]] = D
        I[a] = Iv
    sp = 0.0
    for _ in range(SETTLE):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cutR1=nzn[cutR1_pos_in_new],
                     cutR2=nzn[cutR2_pos_in_new],
                     cutR3=nzn[cutR3_pos_in_new], b65=nz_o)
        sp += 2 * math.pi * 0.7 * DT
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))
        for a in ARMS:
            drive = torch.sparse.mm(WB[a], st[a]) * gains[a] + I[a]
            drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            st[a] = st[a] + (DT / TAU) * ((torch.relu(drive + BG) + noise[a])
                                          .clamp(max=RMAX) - st[a])
    return st


def af_of(st):
    return {a: float((st[a] > 0.05).float().mean()) for a in ARMS}


# ---------------- P1 bisect for g_cut (l92 form, settle-only) ----------------
ANCH = [11, 22, 33]
lo_g, hi_g = 0.12, 0.18


def bisect_af_mean(g, arm="cut"):
    afs = []
    for s in ANCH:
        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cutR1=g, cutR2=g, cutR3=g))
        afs.append(float((st[arm] > 0.05).float().mean()))
    return float(np.mean(afs))


af_lo, af_hi = bisect_af_mean(lo_g), bisect_af_mean(hi_g)
log(f"bisect bracket af({lo_g})={af_lo:.5f} af({hi_g})={af_hi:.5f} "
    f"target {AF_T:.5f}")
assert af_lo < AF_T < af_hi, "bracket fail"
for it in range(24):
    mid = (lo_g + hi_g) / 2
    if bisect_af_mean(mid) < AF_T:
        lo_g = mid
    else:
        hi_g = mid
GAIN["cut"] = lo_g
af_final = bisect_af_mean(lo_g)
# C0A(c): deterministic re-bisect must land on the stored l107 gain EXACTLY
assert GAIN["cut"] == G_CUT_STORED, (GAIN["cut"], G_CUT_STORED)
log(f"g_cut {lo_g:.6f} == stored EXACT | af_final {af_final:.6f} "
    f"({time.time()-t0:.0f}s)")

# L111: fresh bisect for the cut19 subnet (staircase disclosed)
lo2, hi2 = 0.12, 0.18
af_lo2, af_hi2 = bisect_af_mean(lo2, "cut19"), bisect_af_mean(hi2, "cut19")
log(f"cut19 bracket af({lo2})={af_lo2:.5f} af({hi2})={af_hi2:.5f} "
    f"target {AF_T:.5f}")
assert af_lo2 < AF_T < af_hi2, "cut19 bracket fail"
for it in range(24):
    mid = (lo2 + hi2) / 2
    if bisect_af_mean(mid, "cut19") < AF_T:
        lo2 = mid
    else:
        hi2 = mid
GAIN["cut19"] = lo2
af_final19 = bisect_af_mean(lo2, "cut19")
# C0A(c19): deterministic re-bisect must land on the stored l111 gain EXACT
assert GAIN["cut19"] == G_CUT19_STORED, (GAIN["cut19"], G_CUT19_STORED)
log(f"g_cut19 {lo2:.6f} == stored EXACT | af_final19 {af_final19:.6f} "
    f"|af-target| {abs(af_final19 - AF_T):.2e} (staircase disclosed)")

# L115: fresh bisects for the three random-19 subnets (staircase disclosed)
af_finalR = {}
for _ra in ("cutR1", "cutR2", "cutR3"):
    lo3, hi3 = 0.12, 0.32  # ADDENDUM 1: widened (attempt 1 cutR3 bracket fail)
    af_lo3 = bisect_af_mean(lo3, _ra)
    af_hi3 = bisect_af_mean(hi3, _ra)
    log(f"{_ra} bracket af({lo3})={af_lo3:.5f} af({hi3})={af_hi3:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo3 < AF_T < af_hi3, f"{_ra} bracket fail"
    for it in range(24):
        mid = (lo3 + hi3) / 2
        if bisect_af_mean(mid, _ra) < AF_T:
            lo3 = mid
        else:
            hi3 = mid
    GAIN[_ra] = lo3
    af_finalR[_ra] = bisect_af_mean(lo3, _ra)
    log(f"g_{_ra} {lo3:.6f} | af_final {af_finalR[_ra]:.6f} "
        f"|af-target| {abs(af_finalR[_ra] - AF_T):.2e} (staircase disclosed)")

# ---------------- rollouts ----------------
store = {}
if os.path.exists("l115/raw_partial.npz"):
    z = np.load("l113/raw_partial.npz")
    store = {k: z[k] for k in z.files}
for seed in SEEDS:
    if f"mm_full_{seed}" in store:
        log(f"seed {seed} cached, skip")
        continue
    # l94 draw order, ONE generator pair across settle+WIN (contiguous)
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    Xc_full = torch.zeros(n_new, 1)
    Xc_full[old_pos_in_new] = X0o
    Xc_full[new_pos] = X0n
    Xc_cut = torch.zeros(n_cut, 1)
    Xc_cut[old_pos_in_cut] = X0o
    Xc_cut[kept_new_cut] = X0n[kept_new_mask]
    Xc_cut19 = torch.zeros(n_cut19, 1)
    Xc_cut19[old_pos_in_c19] = X0o
    Xc_cut19[kept_new_cut19] = X0n[kept_new_mask19]
    Xc_cR1 = torch.zeros(n_cutR1, 1)
    Xc_cR1[old_pos_in_cR1] = X0o
    Xc_cR1[kept_new_cutR1] = X0n[kept_new_maskR1]
    Xc_cR2 = torch.zeros(n_cutR2, 1)
    Xc_cR2[old_pos_in_cR2] = X0o
    Xc_cR2[kept_new_cutR2] = X0n[kept_new_maskR2]
    Xc_cR3 = torch.zeros(n_cutR3, 1)
    Xc_cR3[old_pos_in_cR3] = X0o
    Xc_cR3[kept_new_cutR3] = X0n[kept_new_maskR3]
    Xo65 = X0o.clone()
    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), cutR1=Xc_cR1.clone(),
             cutR2=Xc_cR2.clone(), cutR3=Xc_cR3.clone(),
             b65=Xo65.clone())
    Iv = {}
    for a in ARMS:
        v = torch.zeros(N_OF[a], 1)
        v[dng100[a]] = D
        Iv[a] = v
    sp = 0.0
    for _ in range(SETTLE):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cutR1=nzn[cutR1_pos_in_new],
                     cutR2=nzn[cutR2_pos_in_new],
                     cutR3=nzn[cutR3_pos_in_new], b65=nz_o)
        sp += 2 * math.pi * 0.7 * DT
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))
        for a in ARMS:
            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            X[a] = X[a] + (DT / TAU) * ((torch.relu(drive + BG) + noise[a])
                                        .clamp(max=RMAX) - X[a])
    af_c = {a: float((X[a] > 0.05).float().mean()) for a in ARMS}
    for a in ARMS:
        assert 0.01 < af_c[a] < 0.9, (a, af_c[a])
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    xm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {kk: np.zeros(WIN, np.float32) for kk in POOLS[a]} for a in ARMS}
    for k in range(WIN):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cutR1=nzn[cutR1_pos_in_new],
                     cutR2=nzn[cutR2_pos_in_new],
                     cutR3=nzn[cutR3_pos_in_new], b65=nz_o)
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
        for a in ARMS:
            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            if sin_t > 0:
                drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            t = torch.relu(drive + BG)
            t = (t + noise[a]).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
        for a in ARMS:
            mm[a][k] = X[a][motor[a]].mean()
            xm[a][k] = X[a][mech[a]].mean()
            for kk in POOLS[a]:
                tr[a][kk][k] = X[a][POOLS[a][kk]].mean()
    for a in ARMS:
        store[f"mm_{a}_{seed}"] = mm[a]
        store[f"xm_{a}_{seed}"] = xm[a]
        for kk in POOLS[a]:
            store[f"{kk}_{a}_{seed}"] = tr[a][kk]
        store[f"af_{a}_{seed}"] = np.float32(af_c[a])
    np.savez("l115/raw_partial.npz", **store)
    log(f"seed {seed} done af {af_c} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")
np.savez_compressed("l115/raw_l115.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"],
                    g_cutR1=GAIN["cutR1"], g_cutR2=GAIN["cutR2"],
                    g_cutR3=GAIN["cutR3"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cutR1_drop=cutR_drop[1], cutR2_drop=cutR_drop[2],
                    cutR3_drop=cutR_drop[3],
                    rand_mass=np.array(rand_mass), rand_glut=np.array(rand_glut),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l115.npz checkpointed BEFORE analysis")

# ---------------- C0A (PREREG): anchors bit-identity ----------------
zprev = np.load("l113/raw_l113.npz")
c0a = {}
for s in (801, 901):  # full/b65/cut/cut19 vs stored l113 (itself C0A-cert vs l111)
    for key in ["mm", "xm"] + list(POOLS["full"]):
        for a in ("full", "b65", "cut", "cut19"):
            c0a[f"113_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - zprev[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("full", "b65", "cut", "cut19"):
        c0a[f"113_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(zprev[f"af_{a}_{s}"]))
out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"],
           g_cutR={a: GAIN[a] for a in ("cutR1", "cutR2", "cutR3")},
           af_final=af_final, af_final19=af_final19,
           af_finalR=af_finalR, K=K, mass_split=mass_split,
           rand_mass=rand_mass, rand_glut=rand_glut,
           c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())))
json.dump(out, open("l115/anchors_run.json", "w"), indent=1)
log(f"C0A {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")
