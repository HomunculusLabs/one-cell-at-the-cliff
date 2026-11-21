"""L174 (b4-iii-a): the lane-ID / internal-artifact strip. 12 DECLARED edits,
applied against the FROZEN pre-image. Dry run unless --apply. Refuses a 2nd run."""
import re, sys, json, os, collections
PAPER='/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md'
FREEZE='draft_pre.md'
APPLY='--apply' in sys.argv
pre=open(FREEZE).read()
live=open(PAPER).read()
if APPLY:
    assert not os.path.exists('emit_report.json'), 'emit.py already ran (one-shot guard)'
assert live==pre, 'T4: live draft != frozen pre-image (another edit landed)'

# ---- the 12 declared edits ----
EDITS=[
 (1,'### 2.5 heading',            '### 2.5 Robustness: endpoints hold, interior re-draws (L139)',
                                  '### 2.5 Robustness: endpoints hold, interior re-draws'),
 (2,'### 2.6 heading',            'matched synapse floor (L138, L170)','matched synapse floor'),
 (3,'§2.6 prose (deleted, not re-pointed)',
                                  'and after L169 (b2) we do not assume a static','and we do not assume a static'),
 (4,'### 2.7 heading',            'the rewire and the deletion (L169 stages a\u2013d)','the rewire and the deletion'),
 (5,'§2.7 prose (re-pointed)',    'is the\nL172 statistics pass','is the\n\u00a72.9 statistics pass'),
 (6,'### 2.8 heading',            'does not ride on it (L156, L157, L162, L171)','does not ride on it'),
 (7,'§2.8 prose',                 "with L162's evoked phase lock",'with the evoked phase lock'),
 (8,'§2.8 prose',                 'recorded in\nthe lane log','recorded in\nthe project log'),
 (9,'### 2.9 heading',            'what the interval means (L172)','what the interval means'),
 (10,'§1 prose',                  'novelty sweep logged in\nLANE-RESEARCH.md 2026-11-18.',
                                  'novelty sweep run on\n2026-11-18.'),
 (11,'§6 data & code',            '- Code: lane scripts + PREREG chain under peabrain-lab/banc/ (release form\n  TBD by owner \u2014 private tree today; a public release needs owner decision).',
                                  '- Code: analysis scripts + the preregistration chain under\n  peabrain-lab/banc/ (release form TBD by owner \u2014 private tree today; a\n  public release needs owner decision).'),
 (12,'references preamble',       '2026-11-19 (L152) and re-resolved','2026-11-19 and re-resolved'),
 # ADDENDUM 2: found by the T10 residue gate, not by the hand-built list.
 (13,'§2.2 bold lead',          'set-dependently so (L168).**','set-dependently so.**'),
]
out=pre
for n,where,old,new in EDITS:
    assert pre.count(old)==1, (n,where,'old form not unique in pre-image',pre.count(old))
    trunc = new in old          # a parenthetical/clause DROP: new is a prefix-slice of old
    if not trunc:
        assert new not in pre, (n,where,'new form already present')
    nbefore=out.count(new)
    out=out.replace(old,new,1)
    assert out.count(old)==0, (n,where,'old form survived the edit')
    exp = nbefore if trunc else nbefore+1
    assert out.count(new)==exp, (n,where,'new form count off',out.count(new),exp)

# ---- T1: both multisets over the WHOLE draft ----
# ADDENDUM 1: measurement tokens only -- strip §-refs, exclude identifier-internal
# digit runs (L139/B30/v3.28), and account for the removed runs BY NAME.
NUM=re.compile(r'(?<![A-Za-z0-9])[-+]?\d[\d,\.eE+\-/]*')
IDNUM=re.compile(r'(?<=[A-Za-z])\d[\d\.]*')
SREF=re.compile(r'\u00a7\d+(?:\.\d+)?')
KEY=re.compile(r'\[l\d+[a-z]*\.[A-Za-z0-9_]+\]')
def nums(t): return sorted(x.rstrip(',') for x in NUM.findall(SREF.sub('',t)))
def idnums(t): return sorted(IDNUM.findall(t))
def keys(t): return sorted(KEY.findall(t))
assert nums(pre)==nums(out), 'T1: measurement multiset changed'
assert keys(pre)==keys(out), 'T1: citation-key multiset changed'
ip,io=collections.Counter(idnums(pre)),collections.Counter(idnums(out))
gone=sorted((ip-io).elements()); came=sorted((io-ip).elements())
# 13 lane IDs (L169 and L172 and L162 twice each) + the '2' of the stage label
# '(b2)' that leaves with declared edit 3's clause.
DECLARED_GONE=sorted(['139','138','170','169','169','172','172','156','157',
                      '162','162','171','152','168','2'])
assert gone==DECLARED_GONE, ('identifier digits removed != declared lane IDs',gone)
assert came==[], ('identifier digits ADDED',came)
print('ADDENDUM 1: identifier digit runs removed =',gone,'| added =',came)

# ---- T7-strong: pre-image + declared edits == live (identity by construction) ----
CONN={'and','while','so','therefore','the'}
WORD=re.compile(r"[A-Za-z0-9][A-Za-z0-9'\u2013\-\.]*")
def cw(t): return [w for w in WORD.findall(t) if w.lower() not in CONN]
d_pre,d_out=cw(pre),cw(out)
drop=[w for w in d_pre if w not in d_out]
print('content-word count pre/post:',len(d_pre),len(d_out))

# ---- T10: zero residue in scope, out-of-scope byte-unchanged ----
def span(t,a,b): return t[t.index(a):t.index(b)]
SCOPE_A,SCOPE_B='## 1. Introduction','## 7. Author/submit notes'
sc=span(out,SCOPE_A,SCOPE_B)
lane=re.findall(r'\bL\d{2,3}\b',sc)
arte=[s for s in ('LANE-RESEARCH','lane log','lane scripts','the lane ') if s in sc]
assert not lane, ('T10 residue lane IDs',lane)
assert not arte, ('T10 residue artefacts',arte)
# references preamble paragraph (in scope)
assert '(L152)' not in out[out.index('## References'):out.index('[1]')], 'T10 refs preamble residue'
# out of scope spans byte-identical
assert out[:out.index(SCOPE_A)]==pre[:pre.index(SCOPE_A)], 'out-of-scope: banner/title/abstract changed'
assert span(out,SCOPE_B,'## References')==span(pre,SCOPE_B,'## References'), 'out-of-scope: §7 changed'

# ---- T11: caps occurrence count UNCHANGED (a derivation may not leak) ----
CAPS=re.compile(r"\b[A-Z][A-Z0-9\|\-\']{2,}\b")
pl,ol=pre.split('\n'),out.split('\n')
cpre=collections.Counter(CAPS.findall('\n'.join(pl[456:1506])))
# body end shifts by the §6 rewrap (+1 line) only AFTER §5, so compare §1-§5 by span
def b15(t): return t[t.index('## 1. Introduction'):t.index('## 6. Data & code')]
cp,co=collections.Counter(CAPS.findall(b15(pre))),collections.Counter(CAPS.findall(b15(out)))
# ADDENDUM 3: read the STORED partition; only the class this stage owns may move.
PART=json.load(open('caps_partition.json'))['class']
OWNED={t for t,c in PART.items() if c=='DEFER_LANE'}|{'LANE-RESEARCH'}
leak={k:(cp.get(k,0),co.get(k,0)) for k in set(cp)|set(co)
       if k not in OWNED and cp.get(k,0)!=co.get(k,0)}
assert not leak, ('T11: a non-owned caps class moved',leak)
assert all(co.get(t,0)==0 for t in OWNED), ('T11: owned class not driven to zero',
       {t:co.get(t,0) for t in OWNED if co.get(t,0)})
nk=sum(n for t,n in cp.items() if t not in OWNED)
print(f'T11 non-owned caps unchanged: {nk} occ / {len([t for t in cp if t not in OWNED])} distinct;'
      f' owned class {sorted(OWNED)} -> 0')

# ---- measurements ----
vis=lambda t: len(re.sub(r'\s+','',t))
rep=dict(raw_pre=len(pre),raw_post=len(out),raw_delta=len(out)-len(pre),
         vis_pre=vis(pre),vis_post=vis(out),vis_delta=vis(out)-vis(pre),
         lane_pre=len(re.findall(r'\bL\d{2,3}\b',span(pre,SCOPE_A,SCOPE_B))),lane_post=0,
         dropped_content_words=drop, n_edits=len(EDITS),
         caps_occ_15=sum(cp.values()), caps_distinct_15=len(cp),
         lines_pre=len(pl), lines_post=len(ol))
# house width: no NEW line over 78 in the edited prose range
# House width governs PROSE only: the pre-image already carries 30 lines >78
# in 403-1520, every one of them a heading or a markdown table row (verified
# pre-apply). So the gate is: no PROSE line may be over 78 unless it already
# was, and no edited line may GROW past 78.
def prose(l): return not (l.startswith('#') or l.lstrip().startswith('|'))
bad=[(i+1,len(l)) for i,l in enumerate(ol[:1520])
     if len(l)>78 and prose(l) and l not in pl]
# declared edit 11 re-wraps a §6 bullet from 2 lines to 3, so line indices
# below §6 are comparable and indices above are shifted by exactly one. The
# growth check runs on the comparable region; the tail is covered by the
# by-construction identity (out = pre + the 13 declared replacements), the
# §7 out-of-scope byte-identity and the shift proof below.
i6=[i for i,l in enumerate(pl) if l.startswith('## 6. Data & code')][0]
grew=[(i+1,len(ol[i])) for i in range(i6)
      if ol[i]!=pl[i] and len(ol[i])>78 and len(ol[i])>len(pl[i])]
assert len(ol)==len(pl)+1, ('line-count delta != the one declared rewrap',len(ol),len(pl))
ref_pre=[l for l in pl[i6:] if '(L152) and re-resolved' not in l]
ref_out=[l for l in ol[i6:] if 'and re-resolved' not in l or '(L152)' in l]
assert len([l for l in ol if '(L152) and re-resolved' in l])==0, 'edit 12 not applied'
rep['prose_over78_new']=bad; rep['grew_past78']=grew
rep['s28_heading_len']=[len([l for l in pl if l.startswith('### 2.8')][0]),
                        len([l for l in ol if l.startswith('### 2.8')][0])]
print(json.dumps({k:v for k,v in rep.items() if k!='dropped_content_words'},indent=1))
print('dropped content words:',drop)
assert not bad, ('house width: new over-78 prose line',bad)
assert not grew, ('house width: an edited line grew past 78',grew)
if APPLY:
    open(PAPER,'w').write(out)
    json.dump(rep,open('emit_report.json','w'),indent=1)
    open('draft_post.md','w').write(out)
    print('\nAPPLIED.')
else:
    open('draft_post_preview.md','w').write(out)
    print('\nDRY RUN CLEAN (preview written, draft untouched).')
