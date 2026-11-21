import re, json, collections
P='/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md'
D=open(P).read()
lines=D.split('\n')
hdr=[(i,l) for i,l in enumerate(lines) if re.match(r'^## ',l)]
secs=[]
for k,(i,l) in enumerate(hdr):
    j = hdr[k+1][0] if k+1<len(hdr) else len(lines)
    secs.append((l[3:].strip(), i, j))
BATCH=re.compile(r'(?<![A-Za-z0-9])B\d{1,3}(?![0-9])')
LANE=re.compile(r'(?<![A-Za-z0-9])L\d{1,3}(?![0-9])')
print("SECTIONS (1-indexed line ranges):")
tot=collections.Counter()
for name,i,j in secs:
    txt='\n'.join(lines[i:j])
    b=BATCH.findall(txt); l=LANE.findall(txt)
    tot['batch']+=len(b); tot['lane']+=len(l)
    print(f"{i+1:5d}-{j:5d} chars={len(txt):7d} batch={len(b):3d} lane={len(l):3d}  {name[:50]}")
print("TOTAL", dict(tot))
print()
print("EVERY BATCH OCCURRENCE WITH LINE + CONTEXT:")
occ=[]
for n,l in enumerate(lines,1):
    for m in BATCH.finditer(l):
        occ.append((n,m.group(0),l.strip()))
for n,tok,l in occ:
    print(f"L{n:5d} {tok:5s} | {l[:230]}")
print()
print("distinct:", sorted(set(t for _,t,_ in occ)), "count", len(occ))
json.dump([dict(line=n,tok=t,text=l) for n,t,l in occ], open('batch_occ.json','w'), indent=1)
