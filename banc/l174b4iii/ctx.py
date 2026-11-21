import re
L=open('/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md').read().split('\n')
pat=re.compile(r'\b(?:L\d{2,3}|B\d{1,2}(?:-B\d{1,2})?)\b')
for i in range(402,1527):
    m=pat.findall(L[i])
    if m: print(f'{i+1:5d} {sorted(set(m))} | {L[i].strip()[:150]}')
