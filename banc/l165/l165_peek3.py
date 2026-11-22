import json
d=json.load(open("l162/addendum3.json"))
print("TOP",list(d.keys()))
for k in d:
    v=d[k]
    if isinstance(v,dict):
        ks=list(v.keys())
        print(k,"ndict",len(ks),ks[:6])
    else: print(k,"=",v)
ps=d.get("plv_self",{})
for k in sorted(ps):
    if "l150" in k: print("  ",k,ps[k])
print("EV keys sample:", [k for k in d.get("evoked_frac",{}) if "l150" in k][:30])
ev=d.get("evoked_frac",{})
for k in sorted(ev):
    if "l150" in k: print("  EV",k,ev[k])
