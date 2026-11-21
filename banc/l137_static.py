"""L137 STATIC arm (zero rollouts): Zhang shared-input overlap of the
transition twins vs the ng-58 family (tick-158 field fold, 2610.00690).

PREREG l137/PREREG.md FIRST (Z1-Z4 registered before this ran).
Extraction VERBATIM l134_static.py (pins re-asserted so drift trips
before any overlap number is read). Deterministic, no RNG.

Measures (per PREREG):
  cos(v_a, v_b), v_c[s] = sum |w(s->c)|, on CLOSURE edges (primary, the
  substrate the dynamics runs on) and on the FULL in-graph edge set
  (robustness, Zhang's all-partner form). Family = ng-58; twins 1110/319.
"""
import json
import os

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
ST = json.load(open("l107/static.json"))
S92 = json.load(open("l92/static.json"))
S121 = json.load(open("l121/static.json"))
S126 = json.load(open("l126/static.json"))
S131 = json.load(open("l131/static.json"))

# ---------------- extraction (l134_static.py verbatim) ----------------
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
in_new_cell = np.zeros(Nall, bool)
in_new_cell[dn_new_g] = True
out_rows = added & in_new_cell[src_all]

tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup == "motor"]] = "motor_other"
tier_of_dst[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup == "sensory")
                   & (region == "ventral_nerve_cord")]] = "vnc_sensory"
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
heav = dn_new_g[order[:K]]
cut19_drop = np.sort(heav[is_glut[heav]])
assert len(cut19_drop) == 19, f"glut heavy = {len(cut19_drop)} != 19 (STOP)"
_mass_heavy = cell_mass[order[:K]]
mass_split = dict(
    glut19=round(float(_mass_heavy[is_glut[heav]].sum() / cell_mass.sum()), 4),
    other58=round(float(_mass_heavy[~is_glut[heav]].sum() / cell_mass.sum()), 4))
assert mass_split == {"glut19": 0.1103, "other58": 0.3921}, mass_split

glut_desc = heav[is_glut[heav]]
ng_desc = heav[~is_glut[heav]]
assert len(glut_desc) == 19 and len(ng_desc) == 58
total = cell_mass.sum()
for kk in (19, 29, 58):
    d = np.sort(ng_desc[:kk])
    want = S121["ngladder"][f"k{kk}"]["drop_ids"]
    assert [int(x) for x in d] == want, f"k{kk} drop drift (STOP)"
rank25_id, rank26_id = int(ng_desc[24]), int(ng_desc[25])
assert rank25_id == S131["rank_ids"]["rank25"] == 1110
assert rank26_id == S131["rank_ids"]["rank26"] == 319
print("extraction pins green: k-ladder + rank twins (1110/319)")

# ================= L137: Zhang shared-input overlap =================
TWINS = {1110: "DNp33-L (carrier)", 319: "DNpe025-R (neutral twin)"}
fam = [int(g) for g in ng_desc]          # ranks 1..58 in mass order
CORE = fam[:19]                           # always-cut in every ng arm
BAND = fam[19:24]                         # k20->k24 completion band
assert 1110 in fam and 319 in fam and 1110 not in CORE and 319 not in CORE


def in_vecs(cells, edge_mask):
    """dict gi -> {src: sum|w|} for the given edge mask."""
    src, dst, w = src_all[edge_mask], dst_all[edge_mask], np.abs(vals_all[edge_mask])
    want = set(cells)
    out = {c: {} for c in cells}
    for s, d, ww in zip(src, dst, w):
        if d in want:
            out[d][int(s)] = out[d].get(int(s), 0.0) + float(ww)
    return out


def cos(va, vb):
    if len(va) > len(vb):
        va, vb = vb, va
    dot = sum(v * vb.get(k, 0.0) for k, v in va.items())
    na = np.sqrt(sum(v * v for v in va.values()))
    nb = np.sqrt(sum(v * v for v in vb.values()))
    return dot / (na * nb) if na > 0 and nb > 0 else 0.0


def zhang_block(edge_mask, label):
    vecs = in_vecs(fam, edge_mask)
    deg = {c: (len(vecs[c]), sum(vecs[c].values())) for c in fam}
    # 58x58 cos matrix
    C = np.zeros((58, 58))
    for i in range(58):
        for j in range(i + 1, 58):
            v = cos(vecs[fam[i]], vecs[fam[j]])
            C[i, j] = C[j, i] = v
    fam_mean = {fam[i]: float(np.delete(C[i], i).mean()) for i in range(58)}
    order_fam = sorted(fam, key=lambda c: -fam_mean[c])
    rank_of = {c: i + 1 for i, c in enumerate(order_fam)}
    # paired twin comparison over the 56 non-twin family cells
    i1, i3 = fam.index(1110), fam.index(319)
    others = [k for k in range(58) if k not in (i1, i3)]
    d_pair = [float(C[i1, k] - C[i3, k]) for k in others]
    n_pos = int(sum(d > 0 for d in d_pair))
    mean1 = float(np.mean([C[i1, k] for k in others]))
    mean3 = float(np.mean([C[i3, k] for k in others]))
    # subsets (twins excluded from both sides)
    def subset_mean(cell, sub):
        ii = fam.index(cell)
        vals = [C[ii, fam.index(f)] for f in sub if f != cell]
        return float(np.mean(vals)) if vals else 0.0

    def subset_sign(sub):
        i1s, i3s = fam.index(1110), fam.index(319)
        ds = [C[i1s, fam.index(f)] - C[i3s, fam.index(f)] for f in sub]
        return int(sum(d > 0 for d in ds)), len(ds)

    core1, core3 = subset_mean(1110, CORE), subset_mean(319, CORE)
    band1, band3 = subset_mean(1110, BAND), subset_mean(319, BAND)
    core_sign, band_sign = subset_sign(CORE), subset_sign(BAND)
    # top overlap partners of each twin (writeup)
    def top_partners(cell, n=5):
        ii = fam.index(cell)
        pairs = sorted(((float(C[ii, k]), fam[k]) for k in range(58) if k != ii),
                       reverse=True)[:n]
        return [dict(rank=fam.index(g) + 1, gi=g, cos=round(v, 5)) for v, g in pairs]

    twin_cos = float(C[i1, i3])
    res = dict(
        label=label,
        fam_mean_1110=round(fam_mean[1110], 6),
        fam_mean_319=round(fam_mean[319], 6),
        paired_mean_diff=round(mean1 - mean3, 6),
        paired_n_pos=n_pos, paired_n=len(d_pair),
        rank_1110=rank_of[1110], rank_319=rank_of[319],
        core_mean_1110=round(core1, 6), core_mean_319=round(core3, 6),
        core_sign=core_sign, band_mean_1110=round(band1, 6),
        band_mean_319=round(band3, 6), band_sign=band_sign,
        twin_pair_cos=round(twin_cos, 6),
        fam_mean_range=[round(min(fam_mean.values()), 6),
                        round(max(fam_mean.values()), 6)],
        fam_mean_median=round(float(np.median(list(fam_mean.values()))), 6),
        top_partners_1110=top_partners(1110), top_partners_319=top_partners(319),
        in_degree={str(t): deg[t] for t in TWINS},
    )
    # Z3 interconnection column: direct twin<->family |w| mass (both dirs)
    inter = {}
    src_f, dst_f = src_all[edge_mask], dst_all[edge_mask]
    w_f = np.abs(vals_all[edge_mask])
    for t in TWINS:
        m_to = (src_f == t) & np.isin(dst_f, fam)
        m_from = (dst_f == t) & np.isin(src_f, fam)
        tot = float(w_f[m_to].sum() + w_f[m_from].sum())
        n_e = int(m_to.sum() + m_from.sum())
        partners = {}
        for arr, wsel, key in ((dst_f[m_to], w_f[m_to], "out"),
                               (src_f[m_from], w_f[m_from], "in")):
            for d, ww in zip(arr, wsel):
                partners.setdefault(int(d), [0.0, 0, 0])
                partners[int(d)][0] += float(ww)
                partners[int(d)][1 if key == "out" else 2] += 1
        top = sorted(partners.items(), key=lambda kv: -kv[1][0])[:5]
        inter[str(t)] = dict(mass=round(tot, 5), edges=n_e,
                             n_partners=len(partners),
                             top=[dict(rank=fam.index(g) + 1, gi=g,
                                       mass=round(v[0], 4),
                                       n_out=v[1], n_in=v[2]) for g, v in top])
    res["interconnect"] = inter
    z1 = dict(leg_i=bool(mean1 > mean3), leg_ii=bool(n_pos >= 31),
              leg_iii=bool(rank_of[1110] < rank_of[319]))
    z1["FIRES"] = all(z1.values())
    z2 = dict(core=dict(twin_gt=bool(core1 > core3),
                        sign=f"{core_sign[0]}/{core_sign[1]}"),
              band=dict(twin_gt=bool(band1 > band3),
                        sign=f"{band_sign[0]}/{band_sign[1]}"))
    res["Z1"], res["Z2"] = z1, z2
    print(f"\n== {label} ==")
    print(f"  fam_mean 1110 {res['fam_mean_1110']:.6f} (rank {res['rank_1110']}/58)"
          f"  vs 319 {res['fam_mean_319']:.6f} (rank {res['rank_319']}/58)")
    print(f"  paired diff {res['paired_mean_diff']:+.6f}  pos {n_pos}/56"
          f"   family median {res['f_mean' if False else 'fam_mean_median']:.6f}"
          f"  range {res['fam_mean_range']}")
    print(f"  core(r1-19) 1110 {core1:.6f} vs 319 {core3:.6f} sign "
          f"{core_sign[0]}/{core_sign[1]} |  band(r20-24) {band1:.6f} vs "
          f"{band3:.6f} sign {band_sign[0]}/{band_sign[1]}")
    print(f"  twin-pair cos {twin_cos:.6f}   Z1 {z1}   Z2 core {z2['core']}"
          f" band {z2['band']}")
    print(f"  interconnect 1110 mass {inter['1110']['mass']} edges "
          f"{inter['1110']['edges']} | 319 {inter['319']['mass']}/"
          f"{inter['319']['edges']}")
    print(f"  in-deg 1110 {deg[1110]}  319 {deg[319]}")
    return res


closure = zhang_block(emask_n, "closure (PRIMARY)")
fullg = zhang_block(np.ones(len(src_all), bool), "full-graph (robustness)")

out = dict(design="L137 static Zhang arm: shared-in-neighbor overlap of "
                  "twins 1110/319 vs ng-58. Zero rollouts, no RNG. "
                  "PREREG l137/PREREG.md registered first.",
           closure=closure, full_graph=fullg,
           prereg_else_branch="Z4: if Z1 fails on BOTH substrates, the "
                              "mechanism hunt stays dynamic (l137_run card).")
os.makedirs("l137", exist_ok=True)
json.dump(out, open("l137/static.json", "w"), indent=1)
print("\nl137/static.json written")
print(f"VERDICT: Z1 closure={closure['Z1']['FIRES']} full={fullg['Z1']['FIRES']}"
      f" -> {'STATIC HANDLE FOUND' if closure['Z1']['FIRES'] or fullg['Z1']['FIRES'] else 'Z4: stays DYNAMIC (registered)'}")
