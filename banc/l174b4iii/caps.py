import re, collections, json
D=open('/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md').read()
lines=D.split('\n')
body='\n'.join(lines[456:1506])   # §1 .. §5 inclusive (1-indexed 457..1506)
CAPS=re.compile(r'\b[A-Z][A-Z0-9\|\-\']{2,}\b')
c=collections.Counter(CAPS.findall(body))
print('distinct',len(c),'occ',sum(c.values()))
for t,n in sorted(c.items(), key=lambda kv:(-kv[1],kv[0])):
    print(f'{n:4d}  {t}')
json.dump(dict(c),open('caps_body.json','w'),indent=1)
