#!/usr/bin/env python3
"""Round-2 probe 4: what is in the simulated subnet? Annotation table only
(same file + same filter lines as banc/l135_run.py lines 86-108). Read-only."""
import pandas as pd, numpy as np, json, os
os.chdir('/home/t3rpz/critters/peabrain-lab/banc')
ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
print('annotated rows', len(ann))
print('\nsuper_class x region==ventral_nerve_cord:')
t = ann.groupby(['super_class', ann.region.fillna('') == 'ventral_nerve_cord']).size().unstack(fill_value=0)
print(t.to_string())
cord_cls = ann.super_class.isin(["sensory", "ventral_nerve_cord_intrinsic", "motor"]) & (ann.region == "ventral_nerve_cord")
print('\ncord_mask rule keeps', int(cord_cls.sum()), 'annotated rows; classes kept: sensory / ventral_nerve_cord_intrinsic / motor ONLY')
for cls in ann.super_class.unique():
    if 'ascend' in str(cls).lower():
        print('ASCENDING class present in table:', cls, int((ann.super_class == cls).sum()), '-> excluded by the cord_mask rule')
for f in ['l92/static.json', 'l107/static.json']:
    if os.path.exists(f):
        s = json.load(open(f)); print(f, {k: s[k] for k in s if k in ('n_old', 'n_new', 'dn_new', 'dn_into', 'dng100', 'n_cut', 'cut')})
dn = ann[ann.super_class == 'descending']
print('\ndescending rows', len(dn))
for ct in ['DNp33', 'DNpe025', 'DNg100']:
    r = dn[dn.cell_type.fillna('').astype(str) == ct]
    cols = [c for c in ['cell_type', 'side', 'region', 'cell_class', 'cell_sub_class', 'fafb_783_match', 'manc_121_match', 'pt_root_id'] if c in r.columns]
    print(ct, len(r)); print(r[cols].to_string(index=False)[:900])
