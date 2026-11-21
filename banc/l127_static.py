"""L127 STATIC derivation (zero rollouts): contiguous-LIGHT decile pins.

Extraction VERBATIM from l125_static.py (l113 form), then:
  - re-pin k19/k29/k58 == l121/static.json EXACT (extraction regression);
  - re-pin wA == l123/static.json EXACT (extraction regression; arm NOT
    run in L127 — drop-set identity only);
  - re-pin scr0 == l125/static.json EXACT (extraction regression; scr0 IS
    re-run in L127 same-batch as the coherence context arm);
  - NEW L127 arms (card ideas-67 L127):
      cutcl40  = k19 + ng_desc[39:49]  (ranks 40-49 = the contiguous
                 LIGHT decile, next decile below scr0's ranks 30-39),
                 DETERMINISTIC;
      cutscrL1/cutscrL2 = k19 + 10 PINNED-RNG cells drawn from ng ranks
                 30-58 (same 29-cell pool as l125), rejection-sampled
                 until total drop mass is within the registered light band
                 of the cl40 mass (matched-mass scattered arms; band tried
                 in order +-.002 / +-.003 / +-.005 — the achieved band is
                 DISCLOSED per draw; infeasibility would amend like l125).
  - set identities: every drop == k19 drop UNION extra-10; subset of
    cut58; extra-10 disjoint from the ng[19:29] window AND from k19 AND
    (for scrL draws) NOT identical to the cl40 decile set; DNg100 not in
    any drop.
Writes l127/static.json for the PREREG pins. RNG is PINNED (the draws are
deterministic and pre-registrable, l125 form).
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
S125 = json.load(open("l125/static.json"))

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

# ---------------- L127: contiguous-light-decile pins ----------------
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
# re-pin wA == l123 stored EXACT (extraction regression; arm not run)
_wA = np.sort(ng_desc[:24])
assert S123["window_wA"]["drop_ids"] == [int(x) for x in _wA], "wA drift (STOP)"

k29_mass_share = float(ngmass[:29].sum() / total)
assert round(k29_mass_share, 4) == 0.2588, k29_mass_share
pool = np.sort(ng_desc[29:58])                           # ranks 30-58
assert len(pool) == 29
mass_of = {int(c): float(m / total) for c, m in zip(ng_desc, ngmass)}
k19_mass_share = float(ngmass[:19].sum() / total)
window_ids = set(int(x) for x in ng_desc[19:29])
k19_ids = set(int(x) for x in ng_desc[:19])
assert not (set(map(int, pool)) & window_ids) and not (set(map(int, pool)) & k19_ids)

# decile mass ladder disclosure (ranks 30-39 / 40-49 / 50-58)
m_30_39 = sum(mass_of[int(c)] for c in ng_desc[29:39])
m_40_49 = sum(mass_of[int(c)] for c in ng_desc[39:49])
m_50_58 = sum(mass_of[int(c)] for c in ng_desc[49:58])
print(f"decile masses: 30-39 {m_30_39:.4f} | 40-49 {m_40_49:.4f} | "
      f"50-58 {m_50_58:.4f} | pool total {m_30_39 + m_40_49 + m_50_58:.4f}")

pins = {"mass_split": mass_split,
        "k29_window_mass": round(k29_mass_share, 4),
        "pool_ids": [int(x) for x in pool],
        "decile_masses": {"r30_39": round(m_30_39, 4),
                          "r40_49": round(m_40_49, 4),
                          "r50_58": round(m_50_58, 4)},
        "design": (
            "L127 coherence-vs-heaviness: cutscr0 re-run same-batch "
            "(contiguous-HEAVY adjacent decile, ranks 30-39, .2490); "
            "cutcl40 = k19 + ranks 40-49 (contiguous-LIGHT decile, "
            "DETERMINISTIC); cutscrL1/2 = k19 + pinned-RNG scattered 10 "
            "from ranks 30-58 mass-matched to cutcl40 (light band tried "
            "+-.002/+-.003/+-.005, achieved band DISCLOSED per draw).")}
pins["scr"] = {}

# ---- scr0 re-pin == l125 stored EXACT (arm re-run same-batch) ----
_extra0 = np.sort(np.array(S125["scr"]["cutscr0"]["extra_ids_desc"], np.int64))
assert [int(x) for x in _extra0] == [int(x) for x in np.sort(ng_desc[29:39])], \
    "scr0 extra != ranks 30-39 (STOP)"
_drop0 = np.sort(np.concatenate([ng_desc[:19], _extra0]))
assert [int(x) for x in _drop0] == S125["scr"]["cutscr0"]["drop_ids"], \
    "scr0 drop drift vs l125 stored (STOP)"
_keep0 = keep_new.copy()
_keep0[_drop0] = False
_n0, _em0 = int(_keep0.sum()), int((_keep0[src_all] & _keep0[dst_all]).sum())
assert (_n0, _em0, round(k19_mass_share + m_30_39, 4)) == (
    S125["scr"]["cutscr0"]["n"], S125["scr"]["cutscr0"]["edges"],
    S125["scr"]["cutscr0"]["mass_removed"]), "scr0 pin drift (STOP)"
assert not np.isin(dng100_all, _drop0).any()
pins["scr"]["cutscr0"] = dict(
    drop_ids=[int(x) for x in _drop0],
    n=_n0, edges=_em0, mass_removed=S125["scr"]["cutscr0"]["mass_removed"],
    extra_ids_desc=[int(x) for x in _extra0],
    extra_mass=round(m_30_39, 4), rng_seed=0, attempts=0,
    repin="== l125/static.json EXACT (arm re-run same-batch)")
print(f"scr0 re-pin == l125 stored EXACT: n={_n0} edges={_em0} "
      f"mass={S125['scr']['cutscr0']['mass_removed']}")

# ---- cutcl40: k19 + ranks 40-49 (contiguous LIGHT decile, deterministic) ----
_extra_c = np.sort(ng_desc[39:49])
assert len(_extra_c) == 10 and np.isin(_extra_c, pool).all()
assert not (set(map(int, _extra_c)) & window_ids)
_drop_c = np.sort(np.concatenate([ng_desc[:19], _extra_c]))
assert len(_drop_c) == 29
_keep_c = keep_new.copy()
_keep_c[_drop_c] = False
_n_c, _em_c = int(_keep_c.sum()), int((_keep_c[src_all] & _keep_c[dst_all]).sum())
assert _n_c == int(keep_new.sum()) - 29
assert not np.isin(dng100_all, _drop_c).any()
_mr_c = k19_mass_share + m_40_49
pins["scr"]["cutcl40"] = dict(
    drop_ids=[int(x) for x in _drop_c],
    n=_n_c, edges=_em_c, mass_removed=round(_mr_c, 4),
    extra_ids_desc=[int(x) for x in _extra_c],
    extra_mass=round(m_40_49, 4), rng_seed=0, attempts=0,
    contiguous="ranks 40-49 of the ng mass ladder (deterministic)")
print(f"cl40 (contiguous LIGHT decile): n={_n_c} edges={_em_c} "
      f"mass_removed={_mr_c:.4f} extra_mass={m_40_49:.4f}")

# ---- cutscrL1/2: pinned-RNG scattered 10, mass-matched to cl40 ----
pool_sorted_masses = np.sort([mass_of[int(c)] for c in pool])[::-1]
_min10 = float(pool_sorted_masses[-10:].sum())   # 10 lightest of pool
_max10 = float(pool_sorted_masses[:10].sum())    # 10 heaviest (= ranks 30-39)
print(f"pool 10-draw extra-mass range: [{_min10:.4f}, {_max10:.4f}] "
      f"(cl40 extra {m_40_49:.4f})")
assert _min10 <= m_40_49 <= _max10, \
    "cl40 extra outside ANY 10-of-pool draw range (STOP — amend design)"
for j, seed in ((1, 1271), (2, 1272)):
    rng = np.random.default_rng(seed)
    attempts = 0
    ok = False
    band = None
    for _bd, _bt in ((.002, "+-.002"), (.003, "+-.003"), (.005, "+-.005")):
        while attempts < 100000 and not ok:
            attempts += 1
            pick = rng.choice(29, size=10, replace=False)
            extra = np.sort(pool[pick])
            mr = k19_mass_share + sum(mass_of[int(c)] for c in extra)
            if abs(mr - _mr_c) <= _bd:
                ok = True
                band = _bt
                break
        if ok:
            break
        print(f"scrL{j}: band {_bt} exhausted at {attempts} attempts")
    assert ok, f"scrL{j}: no mass-matched draw (STOP — amend like l125)"
    assert set(map(int, extra)) != set(map(int, _extra_c)), \
        f"scrL{j} draw == cl40 decile (not scattered; STOP)"
    drop = np.sort(np.concatenate([ng_desc[:19], extra]))
    assert len(drop) == 29
    keep_v = keep_new.copy()
    keep_v[drop] = False
    n_v = int(keep_v.sum())
    assert n_v == int(keep_new.sum()) - 29
    em = int((keep_v[src_all] & keep_v[dst_all]).sum())
    assert not np.isin(dng100_all, drop).any()
    assert not (set(map(int, extra)) & window_ids)
    pins["scr"][f"cutscrL{j}"] = dict(
        drop_ids=[int(x) for x in drop],
        n=n_v, edges=em, mass_removed=round(mr, 4),
        extra_ids_desc=[int(x) for x in extra],
        extra_mass=round(float(mr - k19_mass_share), 4),
        rng_seed=seed, attempts=attempts, band=band)
    print(f"scrL{j} (seed {seed}, {attempts} attempts, band {band}): "
          f"n={n_v} edges={em} mass_removed={mr:.4f} "
          f"extra_mass={pins['scr'][f'cutscrL{j}']['extra_mass']:.4f} "
          f"delta_vs_cl40={abs(mr - _mr_c):.4f}")

pins["edges_stored"] = {
    "cut": int((keep_cut[src_all] & keep_cut[dst_all]).sum()),
    "n_cut": int(keep_cut.sum()), "n_new": int(keep_new.sum())}
assert pins["edges_stored"]["cut"] == ST["edges_cut"]

os.makedirs("l127", exist_ok=True)
json.dump(pins, open("l127/static.json", "w"), indent=1)
print("k19/k29/k58 + wA re-pin == stored EXACT; scr0 == l125 EXACT; "
      "l127/static.json written")
