import re, json, collections
P='/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md'
D=open(P).read(); lines=D.split('\n')
# scope boundaries, re-derived
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
TOK=re.compile(r'(?<![A-Za-z0-9])B(\d{1,3})(?![0-9])')
rows=[]
for n,l in enumerate(lines,1):
    for m in TOK.finditer(l):
        tok=m.group(0); num=int(m.group(1)); a,b=m.span()
        after=l[b:b+14]
        # artefact-key context: inside a [l1NN....] bracket
        pre=l[:a]
        # ARTEFACT KEY: the token is INSIDE a dotted/underscored stored key
        # (eAll_B29_B32, l145.pooled.eOutMot_B29_B31) -- purely syntactic, so a
        # bracket that opens on an EARLIER line is still caught.
        in_key = (a>0 and l[a-1] in '_.')
        branch = after.startswith('_') or tok+'-B' in l[a:a+6] or (num<=4 and not in_key)
        sec=sec_of(n)
        if sec=='BANNER':             cls='OUT_BANNER'
        elif sec.startswith('7. '):   cls='OUT_SEC7'
        elif in_key:                  cls='ARTEFACT_KEY'
        elif after.startswith('_') or l[a:a+5]=='B1-B4': cls='BRANCH'
        elif num<=4:                  cls='BRANCH'
        else:                         cls='BATCH'
        rows.append(dict(line=n,tok=tok,num=num,cls=cls,sec=sec[:22],ctx=l[max(0,a-60):b+40].strip()))
cnt=collections.Counter(r['cls'] for r in rows)
print('TOTAL occurrences', len(rows), dict(cnt))
for c in ['BATCH','BRANCH','ARTEFACT_KEY','OUT_BANNER','OUT_SEC7']:
    sub=[r for r in rows if r['cls']==c]
    print(f"\n--- {c} ({len(sub)} occ, {len(set(r['tok'] for r in sub))} distinct {sorted(set(r['tok'] for r in sub))}) ---")
    for r in sub:
        if c.startswith('OUT_'): continue
        print(f"  {r['line']:5d} {r['tok']:4s} [{r['sec']}] ...{r['ctx']}...")
json.dump(rows,open('classify.json','w'),indent=1)
