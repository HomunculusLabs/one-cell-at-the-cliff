import re, json, textwrap, ast
P='/home/t3rpz/critters/peabrain-lab/paper/'
lines=open(P+'DRAFT.md').read().split('\n')
plan=json.load(open('plan.json'))
touch={int(k):v for k,v in plan.items()}
# paragraph bounds (blank-line delimited) for the over-78 lines
def para(n):
    i=n
    while i>1 and lines[i-2].strip(): i-=1
    j=n
    while j<len(lines) and lines[j].strip(): j+=1
    return i,j   # 1-indexed inclusive i..j
overs=[772,827,828]
paras=sorted(set(para(n) for n in overs))
print('paragraphs needing reflow:',paras)
new=list(lines)
for n,v in touch.items(): new[n-1]=v['new']
out={}
for (i,j) in paras:
    block=new[i-1:j]
    txt=' '.join(x.strip() for x in block)
    wrapped=textwrap.wrap(txt,width=78,break_long_words=False,break_on_hyphens=False)
    print(f'\n--- para {i}-{j}: {len(block)} -> {len(wrapped)} lines ---')
    for w in wrapped: print(f'  {len(w):3d}| {w}')
    out[f'{i}-{j}']=dict(pre=lines[i-1:j], post=wrapped)
json.dump(out,open('reflow.json','w'),indent=1)
# which in-draft verifier literals span a line break inside these paragraphs?
VS=['l143_verify.py','l149_verify.py','l158_verify.py','l159_verify.py','l161_verify.py','l174_verify.py']
lits={}
for v in VS:
    for node in ast.walk(ast.parse(open(P+v).read())):
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            s=node.value
            if len(s)>=4 and sum(ch.isalnum() for ch in s)>=2: lits.setdefault(s,set()).add(v)
draft='\n'.join(lines)
final=[]
k=0
for n in range(1,len(lines)+1):
    hit=[p for p in paras if p[0]<=n<=p[1]]
    if hit:
        if n==hit[0][0]: final.extend(out[f'{hit[0][0]}-{hit[0][1]}']['post'])
    else: final.append(new[n-1])
newdraft='\n'.join(final)
broke=[s for s in lits if s in draft and s not in newdraft]
print('\nliterals in draft that BREAK under the plan:',len(broke))
for s in sorted(broke): print('   ',sorted(lits[s]),repr(s[:130]))
open('newdraft_preview.md','w').write(newdraft)
json.dump(sorted(broke),open('broken_literals.json','w'),indent=1)
