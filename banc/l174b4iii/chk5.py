import re
vis=lambda s: len(re.sub(r'\s','',s))
post=open('/home/t3rpz/critters/peabrain-lab/banc/l174b4ii/s28_post.txt').read()
d=open('/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md').read()
now=d[d.index('### 2.8 The slow line'):d.index('### 2.9 Statistics')]
print('vis post',vis(post),'vis now',vis(now),'diff',vis(post)-vis(now))
