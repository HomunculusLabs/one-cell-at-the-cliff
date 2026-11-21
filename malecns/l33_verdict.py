"""L33 verdict pass: evaluate PREREG claims C0-C4 + post-hoc AC summary."""
import json
import numpy as np

r = json.load(open("l33/results_l33.json"))
S = lambda name: r[name]["seeds"]

print("== C0 anchor (base) ==")
base = S("base")
c0_s = all(p["S_pooled"]["Tr"] > 0.15 for p in base)
c0_r = all(p["rhythm"]["ratio"] > 5 for p in base)
print(f"S_Tr {[round(p['S_pooled']['Tr'],2) for p in base]} > .15 all: {c0_s}")
print(f"rhythm {[round(p['rhythm']['ratio']) for p in base]} > 5 all: {c0_r}  -> C0 {'PASS' if c0_s and c0_r else 'FAIL'}")

print("\n== C1 survival (all L/R arms) ==")
ok = True
for name in r:
    if name == "base":
        continue
    for p in S(name):
        if not (p["S_pooled"]["Tr"] > 0.15 and p["rhythm"]["ratio"] > 5):
            ok = False
            print("violation:", name, p["seed"], round(p["S_pooled"]["Tr"], 2), round(p["rhythm"]["ratio"]))
print(f"-> C1 {'PASS' if ok else 'FAIL'}")

print("\n== C2 graded (|turn_Ti(f)| vs amp, L arm) ==")
amps = [0.0, 0.0125, 0.025, 0.05, 0.1, 0.2]
arms = ["base", "Lx0.25", "Lx0.5", "Lx1.0", "Lx2.0", "Lx4.0"]
for i, p in enumerate(S("base")):
    seq = [abs(S(a)[i]["turn"]["Ti"]["f"]) for a in arms]
    mono = all(np.diff(seq) >= -0.02)
    print(f"seed {p['seed']}: {[round(x,3) for x in seq]} monotone: {mono}")
base_small = all(abs(p["turn"]["Ti"]["f"]) < 0.05 for p in base)
print(f"|turn(base)| < .05: {base_small} (baseline asymmetry {[round(p['turn']['Ti']['f'],3) for p in base]})")

print("\n== C3 sign (Lx4.0 vs Rx4.0) ==")
for i in range(3):
    tl = S("Lx4.0")[i]["turn"]["Ti"]["f"]
    tr = S("Rx4.0")[i]["turn"]["Ti"]["f"]
    print(f"seed {S('Lx4.0')[i]['seed']}: L {tl:+.3f} R {tr:+.3f} flip: {tl * tr < 0}")

print("\n== C4 specificity (rand vs Lx4.0, |turn_Ti f|) ==")
for dr in (0, 1):
    rr = [abs(p["turn"]["Ti"]["f"]) for p in S(f"rand{dr}")]
    ll = [abs(p["turn"]["Ti"]["f"]) for p in S("Lx4.0")]
    print(f"rand{dr}: {rr} vs DNg95 {ll} -> specific: {all(a < b / 2 for a, b in zip(rr, ll))}")

print("\n== POST-HOC AC (labeled): amp asym + L/R flexor lag ==")
for a in arms + ["Rx1.0", "Rx4.0", "rand0", "rand1"]:
    for k in ("Ti", "Tr"):
        row = [f"{p['ac'][k]['amp_f']:+.2f}" for p in S(a)]
        lag = [f"{p['ac'][k]['lr_lag_s']*1000:+.0f}ms" for p in S(a)]
        cc = [f"{p['ac'][k]['lr_cc']:+.2f}" for p in S(a)]
        print(f"{a:>7} {k}: amp_f {row} lag {lag} cc {cc}")

print("\n== S_side table (which side organizes) ==")
for a in arms:
    for k in ("Tr",):
        row = [(round(p["S_side"][k + "L"], 2), round(p["S_side"][k + "R"], 2)) for p in S(a)]
        print(f"{a:>7} {k} (SL,SR): {row}")
