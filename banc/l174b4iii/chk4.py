import re
MEAS=re.compile(r'(?<![A-Za-z0-9])[-+\u2212]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|\u00d7)?')
SREF=re.compile(r'\u00a7\d+(?:\.\d+)?')
d=open('/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md').read()
s=d[d.index('### 2.8 The slow line'):d.index('### 2.9 Statistics')]
print('meas tokens now:',len(MEAS.findall(SREF.sub('',s))))
