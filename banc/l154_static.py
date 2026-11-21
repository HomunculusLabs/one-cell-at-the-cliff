"""L154 (a) STATIC — Sapkal motif vocabulary join, zero rollouts.

PREREG: l154/PREREG.md (H1-H4). Reads male annotations/weights/NT feathers +
BANC dataverse files; writes l154/static.json (full precision) and prints
the pinned table. Run with the PEBRAIN venv python.
"""
import json
import numpy as np
import pandas as pd

MD = '/home/t3rpz/critters/peabrain-lab/malecns/data/'
BD = '/home/t3rpz/critters/peabrain-lab/banc/data/'

# both spellings carried (PREREG vocabulary section)
MOTIF = ['IN12B003', 'IN9A002', 'IN3A006', 'INXX464', 'INXX466',
         'INXXX466', 'IN17A001', 'IN19A007', 'IN16B036', 'IN19B012']
FLEX_M = ['Ti flexor MN', 'Acc. ti flexor MN', 'Tr flexor MN',
          'Acc. tr flexor MN']
EXT_M = ['Ti extensor MN', 'Tr extensor MN']

out = {}

# ---------------- MALE ----------------
a = pd.read_feather(MD + 'body-annotations-male-cns-v1.0-minconf-0.5.feather')
t = a['type'].fillna('').astype(str)          # fillna BEFORE cast (L20 law)
male_counts = {m: int((t == m).sum()) for m in MOTIF}
out['male_join'] = male_counts
print('== MALE join (type exact) ==')
for m in MOTIF:
    print(f'  {m:<10s} {male_counts[m]}')

prof = {}
for m in MOTIF:
    if male_counts[m] == 0:
        continue
    sub = a[t == m]
    prof[m] = dict(n=len(sub),
                   sides=sub.somaSide.fillna('').astype(str)
                   .value_counts().to_dict(),
                   sup=sub.superclass.fillna('').astype(str)
                   .value_counts().to_dict())
out['male_profile'] = prof
print('== MALE motif cell profiles ==')
for m, p in prof.items():
    print(f'  {m}: n={p["n"]} sides={p["sides"]} sup={p["sup"]}')

# 19A/19B census (prefix)
out['male_19A_types'] = int(t.str.match(r'IN19A').sum())
out['male_19B_types'] = int(t.str.match(r'IN19B').sum())
out['male_19A_n_types'] = int(t[t.str.match(r'IN19A')].nunique())
out['male_19B_n_types'] = int(t[t.str.match(r'IN19B')].nunique())
print(f"== MALE census: IN19A* cells {out['male_19A_types']} "
      f"({out['male_19A_n_types']} types) | IN19B* cells "
      f"{out['male_19B_types']} ({out['male_19B_n_types']} types)")

# NT for the joining names (consensus_nt primary, predicted_nt fallback)
nt = pd.read_feather(MD + 'body-neurotransmitters-male-cns-v1.0.feather',
                     columns=['body', 'cell_type', 'predicted_nt',
                              'consensus_nt', 'celltype_predicted_nt'])
nt_by_type = {}
for m in MOTIF:
    if male_counts[m] == 0:
        continue
    sub = nt[nt.cell_type.fillna('').astype(str) == m]
    nt_by_type[m] = dict(
        n=len(sub),
        consensus=sorted(sub.consensus_nt.fillna('').astype(str)
                         .unique().tolist()),
        predicted=sorted(sub.predicted_nt.fillna('').astype(str)
                         .unique().tolist()),
        celltype=sorted(sub.celltype_predicted_nt.fillna('').astype(str)
                        .unique().tolist()))
out['male_nt'] = nt_by_type
print('== MALE NT ==')
for m, p in nt_by_type.items():
    print(f'  {m}: consensus={p["consensus"]} predicted={p["predicted"]}'
          f' celltype={p["celltype"]} (n={p["n"]})')

# weights: motif -> flexor/extensor projections (unsigned mass)
w = pd.read_feather(MD + 'connectome-weights-male-cns-v1.0-minconf-0.5-'
                    'significant-only.feather',
                    columns=['type_pre', 'type_post', 'weight'])
tp = w.type_pre.fillna('').astype(str)
tpost = w.type_post.fillna('').astype(str)
proj = {}
for m in MOTIF:
    if male_counts[m] == 0:
        continue
    sel = tp == m
    post = tpost[sel]
    ww = w.weight[sel].astype(float)
    flex_n = int(post.isin(FLEX_M).sum())
    ext_n = int(post.isin(EXT_M).sum())
    flex_w = float(ww[post.isin(FLEX_M)].sum())
    ext_w = float(ww[post.isin(EXT_M)].sum())
    tot = float(ww.sum())
    ti_flex_n = int(post.isin(['Ti flexor MN', 'Acc. ti flexor MN']).sum())
    proj[m] = dict(edges=int(sel.sum()), total_mass=tot,
                   flexor_edges=flex_n, extensor_edges=ext_n,
                   flexor_mass=flex_w, extensor_mass=ext_w,
                   ti_flexor_edges=ti_flex_n)
out['male_proj'] = proj
print('== MALE motif -> pool projections (unsigned) ==')
for m, p in proj.items():
    print(f'  {m}: edges={p["edges"]} tot={p["total_mass"]:.1f} '
          f'flex(e={p["flexor_edges"]}, m={p["flexor_mass"]:.1f}) '
          f'ext(e={p["extensor_edges"]}, m={p["extensor_mass"]:.1f}) '
          f'TiFlex_e={p["ti_flexor_edges"]}')

# ---------------- BANC ----------------
ann = pd.read_csv(f'{BD}/dv_11845666', sep='\t', low_memory=False)
ntb = pd.read_csv(f'{BD}/dv_11837016', low_memory=False,
                  usecols=['root_626', 'neurotransmitter_predicted'])
mm = pd.read_csv(f'{BD}/dv_11837145', low_memory=False,
                 usecols=['pt_root_id', 'match_cell_type', 'valid'])
mv = mm[mm.valid == True] if mm.valid.dtype == bool \
    else mm[mm.valid.astype(str) == 't']
mt = mv.match_cell_type.fillna('').astype(str)

banc_rm = {m: int((mt == m).sum()) for m in MOTIF}
mc = ann.manc_121_match_id.fillna('').astype(str)
banc_manc = {m: int((mc == m).sum()) for m in MOTIF}
out['banc_rm'] = banc_rm
out['banc_manc'] = banc_manc
print('== BANC join (reviewed-matches / manc_121_match_id) ==')
for m in MOTIF:
    print(f'  {m:<10s} rm={banc_rm[m]:>3d}  manc={banc_manc[m]:>3d}')

out['banc_19A'] = int(mt.str.match(r'IN19A').sum())
out['banc_19B'] = int(mt.str.match(r'IN19B').sum())
out['banc_19A_types'] = int(mt[mt.str.match(r'IN19A')].nunique())
out['banc_19B_types'] = int(mt[mt.str.match(r'IN19B')].nunique())
print(f"== BANC census (reviewed matches): IN19A* {out['banc_19A']} "
      f"({out['banc_19A_types']} types) | IN19B* {out['banc_19B']} "
      f"({out['banc_19B_types']} types)")

# matched motif cells -> ids; NT + flexor projections via connections
motif_ids = {}
for m in MOTIF:
    ids = mv.pt_root_id[mt == m].astype(np.uint64).tolist()
    ids += ann.pt_root_id[mc == m].astype(np.uint64).tolist()
    motif_ids[m] = sorted(set(ids))
    if ids and m == 'IN19A007':
        sub = ntb[ntb.root_626.astype(np.uint64).isin(set(ids))]
        out['banc_in19a007_nt'] = sorted(
            sub.neurotransmitter_predicted.fillna('').astype(str)
            .unique().tolist())
        print(f'  IN19A007 BANC NT: {out["banc_in19a007_nt"]} '
              f'({len(sub)}/{len(set(ids))} cells)')

conn = pd.read_csv(f'{BD}/dv_11842997', compression='gzip',
                   usecols=['pre_root_id', 'post_root_id', 'syn_count'])
pre = conn.pre_root_id.astype(np.uint64).to_numpy()
post = conn.post_root_id.astype(np.uint64).to_numpy()
syn = conn.syn_count.astype(np.int64).to_numpy()

ptt = ann.peripheral_target_type.fillna('').astype(str)
ann_id = ann.pt_root_id.astype(np.uint64).to_numpy()
is_flex = ptt.str.contains('flexor', case=False).to_numpy()
is_ext = ptt.str.contains('extensor', case=False).to_numpy()
id_flex = set(ann_id[is_flex].tolist())
id_ext = set(ann_id[is_ext].tolist())
out['banc_pool_sizes'] = dict(flexor=len(id_flex), extensor=len(id_ext))
print(f"== BANC pools: flexor-target {len(id_flex)} / "
      f"extensor-target {len(id_ext)} cells")

bproj = {}
for m in MOTIF:
    ids = motif_ids[m]
    if not ids:
        continue
    sel = np.isin(pre, ids)
    po = post[sel]
    ss = syn[sel]
    flexmask = np.isin(po, list(id_flex))
    extmask = np.isin(po, list(id_ext))
    bproj[m] = dict(cells=len(ids), edges=int(sel.sum()),
                    flexor_edges=int(flexmask.sum()),
                    extensor_edges=int(extmask.sum()),
                    flexor_syn=int(ss[flexmask].sum()),
                    extensor_syn=int(ss[extmask].sum()))
out['banc_proj'] = bproj
print('== BANC motif -> pool projections (syn) ==')
for m, p in bproj.items():
    print(f'  {m}: cells={p["cells"]} edges={p["edges"]} '
          f'flex(e={p["flexor_edges"]}, syn={p["flexor_syn"]}) '
          f'ext(e={p["extensor_edges"]}, syn={p["extensor_syn"]})')

with open('l154/static.json', 'w') as f:
    json.dump(out, f, indent=1, sort_keys=True)
print('\nwrote l154/static.json')
