import re, pathlib
P = pathlib.Path.home()/'critters/peabrain-lab'
old = (P/'banc/l174b2/abstract_v321.txt').read_text()
new = (P/'banc/l174b2/abstract_new.txt').read_text()
draft = (P/'paper/DRAFT.md').read_text()
body = draft[draft.index('## 1. Introduction'):]
bflat = re.sub(r'\s+',' ',body)
tok = lambda s: set(re.findall(r'\d+\.\d+|\d+/\d+|\d+', re.sub(r'\s+',' ',s)))
to, tn = tok(old), tok(new)
dropped = sorted(to - tn)
print('old tokens', len(to), 'new tokens', len(tn), 'dropped', len(dropped))
orphans = [t for t in dropped if t not in bflat]
print('DROPPED:', dropped)
print('ORPHANS (not in body):', orphans)
# claim-phrase relocation: the v3.21 abstract's claim phrases
PHRASES = ['449','348','16/16 on-drive','sil','SET-dependent','carrier-free','mass-matched',
           'BIT-IDENTICAL','9.72']
print('new has carrier-free/mass-matched/not unique:',
      all(p in new for p in ('carrier-free','mass-matched','not unique','sufficient')))
