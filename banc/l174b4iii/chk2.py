import re,pathlib
P=pathlib.Path('/home/t3rpz/critters/peabrain-lab')
vis=lambda s: len(re.sub(r'\s','',s))
pre=(P/'banc/l174b3bii/span_pre.txt').read_text(); sev=(P/'banc/l174b3bii/sev_pre.txt').read_text()
d=(P/'paper/DRAFT.md').read_text(); m=(P/'banc/l174b4iii/draft_pre.md').read_text()
def reg(t):
    s=t[t.index('### 2.5 Robustness'):t.index('### 2.9 Statistics')]
    i=s.index('### 2.7 '); j=s.index('### 2.8 ')
    return s[:i]+s[j:]
pe=pre.replace(sev,'')
print('pre_edit',vis(pe),'mid_edit',vis(reg(m)),'now_edit',vis(reg(d)))
print('mid-pre',vis(reg(m))-vis(pe),' now-mid',vis(reg(d))-vis(reg(m)),' now-pre',vis(reg(d))-vis(pe))
