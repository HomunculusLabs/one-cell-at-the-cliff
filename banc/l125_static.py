"""L125 STATIC derivation (zero rollouts): scramble-control pins.

Extraction VERBATIM from l123_static.py (l113 form), then:
  - re-pin k19/k29/k58 == l121/static.json EXACT (extraction regression);
  - re-pin wA/wB == l123/static.json EXACT (extraction regression; arms
    themselves are NOT run in L125 — drop-set identity only);
  - NEW scramble arms (L125 card): cutscr_j = k19 + 10 PINNED-RNG cells
    drawn from ng ranks 30-58 (pool = ng_desc[29:58], 29 cells),
    rejection-sampled until total drop mass is within +-0.01 of the k29
    window mass .2588; 3 draws (seeds 1251/1252/1253), 29 cells dropped,
    masses + attempt counts DISCLOSED in the pins.
  - set identities: scr drop == k19 drop UNION extra-10; subset of cut58;
    extra-10 disjoint from the ng[19:29] window AND from k19; DNg100 not
    in any drop.
Writes l125/static.json for the PREREG pins. RNG is PINNED (the card's
design: the draws themselves are deterministic and pre-registrable).
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
S123 = json.load(open("l123/static.json"))

# ---------------- extraction (l113_run.py verbatim) ----------------
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

# ---------------- L125: scramble pins ----------------
glut_desc = heav[is_glut[heav]]
ng_desc = heav[~is_glut[heav]]
assert len(glut_desc) == 19 and len(ng_desc) == 58
total = cell_mass.sum()
ngmass = cell_mass[order[:K]][~is_glut[heav]]           # ng_desc order
sub_dn = ann[ann.super_class == "descending"]
dng100_all = sub_dn.gi[(sub_dn.cell_type == "DNg100").to_numpy()].to_numpy()
assert not np.isin(dng100_all, heav).any(), "DNg100 in heavy-77 (STOP)"

# re-pin k19/k29/k58 == l121 stored EXACT (extraction regression)
for kk in (19, 29, 58):
    d = np.sort(ng_desc[:kk])
    want = S121["ngladder"][f"k{kk}"]["drop_ids"]
    assert [int(x) for x in d] == want, f"k{kk} drop drift (STOP)"
# re-pin wA/wB == l123 stored EXACT (extraction regression)
_wA = np.sort(ng_desc[:24])
_wB = np.sort(np.concatenate([ng_desc[:19], ng_desc[24:29]]))
assert S123["window_wA"]["drop_ids"] == [int(x) for x in _wA], "wA drift (STOP)"
assert S123["window_wB"]["drop_ids"] == [int(x) for x in _wB], "wB drift (STOP)"

k29_mass_share = float(ngmass[:29].sum() / total)
assert round(k29_mass_share, 4) == 0.2588, k29_mass_share
pool = np.sort(ng_desc[29:58])                           # ranks 30-58
assert len(pool) == 29
# id -> mass-share map (ng_desc is MASS-DESC, never searchsorted)
mass_of = {int(c): float(m / total) for c, m in zip(ng_desc, ngmass)}
k19_mass_share = float(ngmass[:19].sum() / total)
window_ids = set(int(x) for x in ng_desc[19:29])
k19_ids = set(int(x) for x in ng_desc[:19])
assert not (set(map(int, pool)) & window_ids) and not (set(map(int, pool)) & k19_ids)

pins = {"mass_split": mass_split,
        "k29_window_mass": round(k29_mass_share, 4),
        "pool_ids": [int(x) for x in pool],
        "mass_band_amendment": (
            "CARD AMENDMENT (registered pre-run): the card's +-0.01 mass "
            "match to .2588 is INFEASIBLE for 10-of-ranks-30-58 — the "
            "entire pool carries only .1333; max non-window-10 = ranks "
            "30-39 = .0544 -> max total .2490 (verified from l121 stored "
            "pins), i.e. only near-prefix draws could ever qualify and "
            "100000 rejection attempts found none. Amended design: scr0 "
            "= DETERMINISTIC max-mass scramble (k19 + ranks 30-39, .2490, "
            "just .0098 below the window — the mass-armor arm); scr1-3 = "
            "pinned-RNG random draws, representative band [.2340,.2495], "
            "masses DISCLOSED per draw.")}
pins["scr"] = {}
# scr0: deterministic max-mass scramble (k19 + ranks 30-39)
_extra0 = np.sort(ng_desc[29:39])
assert len(_extra0) == 10 and np.isin(_extra0, pool).all()
assert not (set(map(int, _extra0)) & window_ids)
_drop0 = np.sort(np.concatenate([ng_desc[:19], _extra0]))
assert len(_drop0) == 29
_keep0 = keep_new.copy()
_keep0[_drop0] = False
_n0, _em0 = int(_keep0.sum()), int((_keep0[src_all] & _keep0[dst_all]).sum())
assert _n0 == int(keep_new.sum()) - 29
assert not np.isin(dng100_all, _drop0).any()
_mr0 = k19_mass_share + sum(mass_of[int(c)] for c in _extra0)
pins["scr"]["cutscr0"] = dict(
    drop_ids=[int(x) for x in _drop0],
    n=_n0, edges=_em0, mass_removed=round(_mr0, 4),
    extra_ids_desc=[int(x) for x in _extra0],
    extra_mass=round(float(_mr0 - k19_mass_share), 4),
    rng_seed=0, attempts=0)
print(f"scr0 (deterministic max-mass): n={_n0} edges={_em0} "
      f"mass_removed={_mr0:.4f} extra_mass="
      f"{pins['scr']['cutscr0']['extra_mass']:.4f}")
for j, seed in ((1, 1251), (2, 1252), (3, 1253)):
    rng = np.random.default_rng(seed)
    attempts = 0
    ok = False
    while attempts < 100000 and not ok:
        attempts += 1
        pick = rng.choice(29, size=10, replace=False)
        extra = np.sort(pool[pick])
        mr = k19_mass_share + sum(mass_of[int(c)] for c in extra)
        if 0.2340 <= mr <= 0.2495:
            ok = True
    assert ok, f"scr{j}: no draw in representative band (STOP)"
    drop = np.sort(np.concatenate([ng_desc[:19], extra]))
    assert len(drop) == 29
    keep_v = keep_new.copy()
    keep_v[drop] = False
    n_v = int(keep_v.sum())
    assert n_v == int(keep_new.sum()) - 29
    em = int((keep_v[src_all] & keep_v[dst_all]).sum())
    assert not np.isin(dng100_all, drop).any()
    assert not (set(map(int, extra)) & window_ids)
    pins["scr"][f"cutscr{j}"] = dict(
        drop_ids=[int(x) for x in drop],
        n=n_v, edges=em, mass_removed=round(mr, 4),
        extra_ids_desc=[int(x) for x in extra],
        extra_mass=round(float(mr - k19_mass_share), 4),
        rng_seed=seed, attempts=attempts)
    print(f"scr{j} (seed {seed}, {attempts} attempts): n={n_v} edges={em} "
          f"mass_removed={mr:.4f} extra_mass="
          f"{pins['scr'][f'cutscr{j}']['extra_mass']:.4f} "
          f"extra={pins['scr'][f'cutscr{j}']['extra_ids_desc']}")

pins["edges_stored"] = {
    "cut": int((keep_cut[src_all] & keep_cut[dst_all]).sum()),
    "n_cut": int(keep_cut.sum()), "n_new": int(keep_new.sum())}
assert pins["edges_stored"]["cut"] == ST["edges_cut"]

os.makedirs("l125", exist_ok=True)
json.dump(pins, open("l125/static.json", "w"), indent=1)
print("k19/k29/k58 + wA/wB re-pin == stored EXACT; l125/static.json written")
