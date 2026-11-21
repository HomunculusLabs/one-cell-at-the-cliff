import re, json, sys, textwrap, hashlib, collections
DRY = '--apply' not in sys.argv
P='/home/t3rpz/critters/peabrain-lab/paper/'
PRE=open('draft_pre.md').read()
LIVE=open(P+'DRAFT.md').read()
assert LIVE==PRE, 'live draft != frozen pre-image (CERT-3)'
MAP={'B26':'A','B27':'B','B29':'C','B30':'D','B31':'E','B32':'F','B33':'G',
     'B34':'H','B35':'J','B37':'K','B38':'L'}
LAB=''.join(MAP.values())
lines=PRE.split('\n')
TOK=re.compile(r'(?<![A-Za-z0-9])B(\d{1,3})(?![0-9])')
PREV=re.compile(r'(?i)(\bbatch(es)?[,:]?\s*\(?\s*|(?:[A-HJ-L]|B\d{1,3})/)$')
hdr=[(i,l) for i,l in enumerate(lines) if re.match(r'^## ',l)]
secs=[]
for k,(i,l) in enumerate(hdr):
    j = hdr[k+1][0] if k+1<len(hdr) else len(lines)
    secs.append((l[3:].strip(), i+1, j))
TITLE=secs[0][1]
def sec_of(n):
    for name,i,j in secs:
        if i<=n<=j: return name
    return 'BANNER' if n<TITLE else '?'
# ---- CERT-4: the transform is PARSED, not typed -------------------------
subs=[]   # (line, a, b, tok, new)
other={'ARTEFACT_KEY':0,'BRANCH':0,'OUT_BANNER':0,'OUT_SEC7':0}
for n,l in enumerate(lines,1):
    for m in TOK.finditer(l):
        tok,a,b=m.group(0),m.start(),m.end(); num=int(m.group(1)); sec=sec_of(n)
        if sec=='BANNER': other['OUT_BANNER']+=1; continue
        if sec.startswith('7. '): other['OUT_SEC7']+=1; continue
        if a>0 and l[a-1] in '_.': other['ARTEFACT_KEY']+=1; continue
        if l[b:b+1]=='_' or l[a:a+5]=='B1-B4' or num<=4: other['BRANCH']+=1; continue
        assert tok in MAP, f'unmapped batch token {tok} line {n}'
        new = MAP[tok] if PREV.search(l[:a]) else 'batch '+MAP[tok]
        subs.append((n,a,b,tok,new))
assert len(subs)==19, len(subs)
assert sorted(set(s[3] for s in subs))==sorted(MAP), 'every code must occur in the body'
assert other=={'ARTEFACT_KEY':6,'BRANCH':4,'OUT_BANNER':10,'OUT_SEC7':0}, other
n_bare=sum(1 for s in subs if ' ' not in s[4]); n_pref=len(subs)-n_bare
assert (n_bare,n_pref)==(6,13), (n_bare,n_pref)
new=list(lines)
for n in sorted(set(s[0] for s in subs)):
    l=lines[n-1]
    for (ln,a,b,tok,nw) in sorted([s for s in subs if s[0]==n], reverse=True):
        l=l[:a]+nw+l[b:]
    new[n-1]=l
# ---- T14 declared reflow of exactly two paragraphs ----------------------
PARAS=[(771,780),(827,831)]
reflow={}
for (i,j) in PARAS:
    blk=new[i-1:j]
    w=textwrap.wrap(' '.join(x.strip() for x in blk),width=78,
                    break_long_words=False,break_on_hyphens=False)
    assert len(w)==len(blk), f'reflow changed line count {i}-{j}: {len(blk)}->{len(w)}'
    reflow[(i,j)]=w
    new[i-1:j]=w
# ---- T12 the Methods mapping block, inserted at the end of §3.7 ---------
ANCHOR='reported with their up/down counts.'
ai=[k for k,l in enumerate(new) if l.strip()==ANCHOR]
assert len(ai)==1, ai
MAPBLOCK=[
 '',
 '**Batch labels.** The eleven seed batches this manuscript cites are labelled',
 'A, B, C, D, E, F, G, H, J, K and L in the order they were run (I and O are',
 'skipped so that a label cannot be read as a digit); the labels map one-to-one',
 'onto the internal run codes, which the stored artefact keys retain verbatim:',
 'A = B26, B = B27, C = B29, D = B30, E = B31, F = B32, G = B33, H = B34,',
 'J = B35, K = B37, L = B38. Gaps in the internal codes are batches this',
 'manuscript does not cite, and a label never renames the batch it points at, so',
 'every pooled cell stays traceable to the batches it unions.',
]
new[ai[0]+1:ai[0]+1]=MAPBLOCK
RES='\n'.join(new)
MB='\n'.join(MAPBLOCK)
# ================= GATES ================================================
def meas(t):
    # measurement tokens: digit runs NOT inside an identifier, §-refs stripped
    t=re.sub(r'§[\d.]+','',t)
    return sorted(re.findall(r'(?<![A-Za-z0-9])\d[\d,.]*',t))
def keys(t): return sorted(re.findall(r'\[([a-z]\d+[a-z]*\.[^\]]*|\d+)\]',t))
def idruns(t): return sorted(re.findall(r'(?<=[A-Za-z])\d{1,3}(?![0-9])',t))
g={}
g['G1_strong_form'] = (RES != PRE)
g['G2_measurement_multiset'] = meas(PRE)==meas(RES)
g['G3_citation_keys'] = keys(PRE)==keys(RES)
# identifier runs: body loses 19, mapping block adds 11
dpre,dres=collections.Counter(idruns(PRE)),collections.Counter(idruns(RES))
lost={k:dpre[k]-dres[k] for k in dpre if dpre[k]>dres[k]}
g['G4_idruns_body_minus19_plus11'] = sum(lost.values())==19-11 and \
    collections.Counter(idruns(MB))==collections.Counter(['26','27','29','30','31','32','33','34','35','37','38'])
# zero residue: no BATCH-class token left in §1..§6 + References preamble,
# outside the mapping block and outside artefact keys / branch labels
rl=RES.split('\n')
h2=[(i,l) for i,l in enumerate(rl) if re.match(r'^## ',l)]
s2=[]
for k,(i,l) in enumerate(h2):
    j=h2[k+1][0] if k+1<len(h2) else len(rl)
    s2.append((l[3:].strip(),i+1,j))
resid=[]
for name,i,j in s2:
    if name=='7. Author/submit notes' or i<s2[0][1]: continue
    if not re.match(r'^[1-6]\. |^References|^Title|^Abstract',name): continue
    for n in range(i,j+1):
        if n-1>=len(rl): break
        l=rl[n-1]
        if l in MAPBLOCK: continue
        for m in TOK.finditer(l):
            a,b,num=m.start(),m.end(),int(m.group(1))
            if a>0 and l[a-1] in '_.': continue
            if l[b:b+1]=='_' or l[a:a+5]=='B1-B4' or num<=4: continue
            resid.append((n,m.group(0),l.strip()[:70]))
g['G5_zero_residue']= not resid
# byte-unchanged out-of-scope ranges
g['G6_banner_unchanged']   = PRE.split('## Title')[0]==RES.split('## Title')[0]
g['G7_sec7_unchanged']     = PRE.split('## 7. Author/submit notes')[1].split('## References')[0] \
                          == RES.split('## 7. Author/submit notes')[1].split('## References')[0]
g['G8_artefact_keys']      = all(k in RES for k in ['l145.pooled.eOutMot_B29_B31','l148.pooled.eAll_B29_B32'])
g['G9_branch_labels']      = all(k in RES for k in ['B1-B4','B2_preserved','registered B4 degenerate'])
g['G10_house_width']       = not [l for l in rl if len(l)>78 and (l in MAPBLOCK or any(l==x for x in sum(reflow.values(),[])) )]
g['G11_bijection']         = len(set(MAP.values()))==11 and all(f'= {c}' in MB for c in MAP) \
                             and all(MB.count(c)==1 for c in MAP)
g['G12_labels_in_body']    = all(re.search(r'(?:batch |/|, )'+lab+r'\b',RES) for lab in MAP.values())
# T7' content-word sequence identical modulo the declared substitutions
def cw(t): return [w for w in re.findall(r"[A-Za-z0-9ΔβΩ'’.\-/%§×≥≤−]+",t)]
pre_app=PRE
for (n,a,b,tok,nw) in subs: pass
g['G13_inserted_batch_words']= cw(RES).count('batch')-cw(PRE).count('batch') == 13+1  # 13 subs + 1 in the mapping lead
g['G14_no_new_numeric_cite']= len(re.findall(r'\[\d+\]',PRE))==len(re.findall(r'\[\d+\]',RES))
print('--- SUBSTITUTIONS (%d: %d bare / %d prefixed) ---'%(len(subs),n_bare,n_pref))
for (n,a,b,tok,nw) in subs: print(f'  {n:5d} {tok} -> {nw}')
print('--- OTHER CLASSES (byte-unchanged) ---', other)
print('--- REFLOW ---', {f'{i}-{j}':len(v) for (i,j),v in reflow.items()})
if resid: print('!! RESIDUE', resid)
print('--- GATES ---')
for k,v in g.items(): print(f'  {"OK " if v else "FAIL"} {k}')
print('raw chars %d -> %d (%+d); mapping block %d chars'%(len(PRE),len(RES),len(RES)-len(PRE),len(MB)))
body_only=len('\n'.join(new[:ai[0]+1]+new[ai[0]+1+len(MAPBLOCK):]))-len(PRE)
print('body-only raw delta %+d'%body_only)
json.dump(dict(subs=[dict(line=n,tok=t,new=w) for (n,a,b,t,w) in subs],other=other,
               gates=g,map=MAP,raw_delta=len(RES)-len(PRE),body_delta=body_only,
               reflow={f'{i}-{j}':v for (i,j),v in reflow.items()},mapblock=MAPBLOCK),
          open('emit_report.json','w'),indent=1)
assert all(g.values()), [k for k,v in g.items() if not v]
if DRY:
    open('draft_post_preview.md','w').write(RES); print('\nDRY RUN OK -> draft_post_preview.md')
else:
    assert 'batch D [l144.silw]' not in LIVE, 'already applied (refusing second run)'
    open(P+'DRAFT.md','w').write(RES); open('draft_post.md','w').write(RES)
    print('\nAPPLIED to DRAFT.md')
