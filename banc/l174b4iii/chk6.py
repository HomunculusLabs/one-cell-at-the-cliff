import re
MEAS=re.compile(r'(?<![A-Za-z0-9])[-+\u2212]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|\u00d7)?')
SREF=re.compile(r'\u00a7\d+(?:\.\d+)?')
pre=open('draft_pre.md').read(); d=open('/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md').read()
T='## Title'
bp,bn=pre[:pre.index(T)],d[:d.index(T)]
ins=bn.replace(bp.rstrip('\n'),'',1)
print(sorted(set(MEAS.findall(SREF.sub('',ins)))))
f=lambda t: sorted(MEAS.findall(SREF.sub('',t)))
print('title-onward T1 equal:', f(pre[pre.index(T):])==f(d[d.index(T):]))
