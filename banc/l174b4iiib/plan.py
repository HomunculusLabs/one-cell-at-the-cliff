import re, json
P='/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md'
lines=open(P).read().split('\n')
rows=[r for r in json.load(open('classify.json')) if r['cls']=='BATCH']
MAP={'B26':'A','B27':'B','B29':'C','B30':'D','B31':'E','B32':'F','B33':'G','B34':'H','B35':'J','B37':'K','B38':'L'}
PREV=re.compile(r'(?i)(\bbatch(es)?[,:]?\s*\(?\s*|(?:[A-HJ-L]|B\d{1,3})/)$')
TOK=re.compile(r'(?<![A-Za-z0-9])B\d{1,3}(?![0-9])')
bare=0; pref=0
newlines=list(lines)
touched=sorted(set(r['line'] for r in rows))
for n in touched:
    l=lines[n-1]; out=''; last=0
    for m in TOK.finditer(l):
        tok=m.group(0)
        if not any(r['line']==n and r['tok']==tok and r['cls']=='BATCH' for r in rows): continue
        # per-occurrence: skip artefact/branch spans by re-checking classify spans via context
        before=l[:m.start()]
        if PREV.search(before): new=MAP[tok]; bare_=True
        else: new='batch '+MAP[tok]; bare_=False
    # full rebuild with span fidelity below
# precise rebuild using classify spans
cl=json.load(open('classify.json'))
occ_by_line={}
for n,l in enumerate(lines,1):
    spans=[]
    for m in TOK.finditer(l):
        spans.append((m.start(),m.end(),m.group(0)))
    if spans: occ_by_line[n]=spans
def cls_of(n,tok,idx):
    # match classify rows in order
    cands=[r for r in cl if r['line']==n and r['tok']==tok]
    return cands[idx]['cls'] if idx<len(cands) else '?'
res={}
for n,spans in occ_by_line.items():
    l=lines[n-1]; out=[]; prev=0; seen={}
    for (a,b,tok) in spans:
        i=seen.get(tok,0); seen[tok]=i+1
        c=cls_of(n,tok,i)
        if c!='BATCH': continue
        before=l[:a]
        new=MAP[tok] if PREV.search(before) else 'batch '+MAP[tok]
        out.append((a,b,tok,new))
    if out:
        s=l; 
        for (a,b,tok,new) in reversed(out): s=s[:a]+new+s[b:]
        res[n]=(l,s,out)
over=[]
for n,(old,new,out) in sorted(res.items()):
    flag='OVER' if len(new)>78 else ''
    if flag: over.append(n)
    print(f"{n:5d} {len(old):3d}->{len(new):3d} {flag:4s} | {new}")
print('\nlines over 78:',over)
print('substitutions:',sum(len(v[2]) for v in res.values()),'bare',sum(1 for v in res.values() for o in v[2] if ' ' not in o[3]))
json.dump({str(k):dict(old=v[0],new=v[1],subs=v[2]) for k,v in res.items()},open('plan.json','w'),indent=1)
