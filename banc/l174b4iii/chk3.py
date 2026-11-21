import re,pathlib
P=pathlib.Path('/home/t3rpz/critters/peabrain-lab'); vis=lambda s: len(re.sub(r'\s','',s))
pre=(P/'banc/l174b3biii/span_pre.txt').read_text()
f=lambda t: t[t.index('### 2.7 '):t.index('### 2.8 The slow line')]
d=f((P/'paper/DRAFT.md').read_text()); m=f((P/'banc/l174b4iii/draft_pre.md').read_text())
print('mid-pre',vis(m)-vis(pre),'now-mid',vis(d)-vis(m),'now-pre',vis(d)-vis(pre))
# and §4 / §2.8+§5 spans for sections (26)/(27)
