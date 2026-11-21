import re
pre=open('/home/t3rpz/critters/peabrain-lab/banc/l174b3b/span_pre.txt').read()
now=open('/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md').read()
now=now[now.index('## 1. Introduction'):now.index('### 2.4 Mechanism')]
vis=lambda s: len(re.sub(r'\s','',s))
s=(pre.replace('set-dependently so (L168).**','set-dependently so.**')
      .replace('novelty sweep logged in\nLANE-RESEARCH.md 2026-11-18.','novelty sweep run on\n2026-11-18.'))
print('edit1 applied:', pre.count('set-dependently so (L168).**'))
print('edit2 applied:', pre.count('novelty sweep logged in\nLANE-RESEARCH.md 2026-11-18.'))
print('vis pre',vis(pre),'vis strip-adj',vis(s),'vis now',vis(now))
print('now - stripadj =',vis(now)-vis(s),' stripadj - pre =',vis(s)-vis(pre))
