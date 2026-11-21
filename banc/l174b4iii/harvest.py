import re, json, ast, sys
P='/home/t3rpz/critters/peabrain-lab/paper/'
VS=['l143_verify.py','l149_verify.py','l158_verify.py','l159_verify.py','l161_verify.py','l174_verify.py']
lits=set()
for v in VS:
    src=open(P+v).read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            s=node.value
            if len(s)>=4 and sum(ch.isalnum() for ch in s)>=2:
                lits.add(s)
draft=open(P+'DRAFT.md').read()
# only literals that actually occur in the draft are gate-relevant
inD=sorted([s for s in lits if s in draft])
print('literals parsed',len(lits),'occurring in draft',len(inD))
# which of those contain a lane ID or one of the target substrings
TARGETS=[' (L139)',' (L138, L170)','and after L169 (b2) we do not assume a static',
 ' (L169 stages a\u2013d)','L172 statistics pass',' (L156, L157, L162, L171)',
 "with L162's evoked phase lock",'the lane log',' (L172)','LANE-RESEARCH.md 2026-11-18',
 'lane scripts + PREREG chain',' (L152)']
risk={}
for s in inD:
    hits=[t for t in TARGETS if t.strip() and (t in s or (re.search(r'\bL\d{2,3}\b',s) and re.search(r'\bL\d{2,3}\b',t)))]
    if re.search(r'\bL\d{2,3}\b',s) or any(t in s for t in TARGETS):
        risk[s]=hits
print('AT-RISK literals:',len(risk))
for s,h in risk.items(): print('   ',repr(s[:110]))
json.dump({'in_draft':inD,'at_risk':list(risk)},open('literals.json','w'),indent=1)
