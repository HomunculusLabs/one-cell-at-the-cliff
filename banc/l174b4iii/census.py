import re, json, collections
D=open('/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md').read()
lines=D.split('\n')
# section map by top-level headings
hdr=[(i,l) for i,l in enumerate(lines) if re.match(r'^## ',l)]
secs=[]
for k,(i,l) in enumerate(hdr):
    j = hdr[k+1][0] if k+1<len(hdr) else len(lines)
    secs.append((l[3:].strip(), i, j))
LANE=re.compile(r'\bL\d{1,3}\b')
BATCH=re.compile(r'\bB\d{1,3}\b')
CAPS=re.compile(r'\b[A-Z][A-Z0-9\|\-]{2,}\b')
rows=[]
for name,i,j in secs:
    txt='\n'.join(lines[i:j])
    l=LANE.findall(txt); b=BATCH.findall(txt); c=CAPS.findall(txt)
    rows.append(dict(sec=name[:42], i=i+1, j=j, chars=len(txt), lane=len(l), batch=len(b), caps=len(c),
                     lane_set=sorted(set(l)), batch_set=sorted(set(b)), caps_top=collections.Counter(c).most_common(14)))
for r in rows:
    print(f"{r['i']:5d}-{r['j']:5d} {r['chars']:7d} lane={r['lane']:4d} batch={r['batch']:3d} caps={r['caps']:4d}  {r['sec']}")
print()
tot=dict(lane=sum(r['lane'] for r in rows),batch=sum(r['batch'] for r in rows),caps=sum(r['caps'] for r in rows))
print('TOTAL',tot)
json.dump(rows,open('census.json','w'),indent=1)
