import re, json, ast
P='/home/t3rpz/critters/peabrain-lab/paper/'
VS=['l143_verify.py','l149_verify.py','l158_verify.py','l159_verify.py','l161_verify.py','l174_verify.py']
lits={}
for v in VS:
    src=open(P+v).read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            s=node.value
            if len(s)>=4 and sum(ch.isalnum() for ch in s)>=2:
                lits.setdefault(s,set()).add(v)
draft=open(P+'DRAFT.md').read()
inD=sorted([s for s in lits if s in draft])
print('literals parsed',len(lits),'occurring in draft',len(inD))
# the declared old forms of this stage (prose batch occurrences), from classify.json
rows=json.load(open('classify.json'))
olds=sorted(set(r['tok'] for r in rows if r['cls']=='BATCH'))
TOK=re.compile(r'(?<![A-Za-z0-9])B\d{1,3}(?![0-9])')
# BIDIRECTIONAL overlap (tick-213 Q2 lesson): literal contains a token OR a token
# string contains the literal; plus any literal mentioning the word batch
risk={}
for s in inD:
    hit=[t for t in olds if t in s] + [t for t in olds if s in t]
    if hit or TOK.search(s):
        risk[s]=sorted(set(hit)) or ['TOKENSHAPE']
print('AT-RISK literals:',len(risk))
for s,h in sorted(risk.items()):
    print('   ',h, repr(s[:120]), '->', sorted(lits[s]))
json.dump({'in_draft':inD,'at_risk':{k:v for k,v in risk.items()},'olds':olds},open('literals.json','w'),indent=1)
