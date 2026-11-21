"""L85 verdict: re-derive (subprocess, zero rollouts), certify the machinery
against l82's STORED verdict on the 3 shared arms, assert every PREREG-pinned
number, emit the mass table + GATE-L85. PREREG l85/PREREG.md FIRST."""
import json
import subprocess
import sys

r = subprocess.run([sys.executable, "l85/derive.py"], capture_output=True, text=True)
print(r.stdout[-500:] if len(r.stdout) > 500 else r.stdout)
assert r.returncode == 0, f"derive re-run failed:\n{r.stderr[-2000:]}"
D = json.load(open("l85/derived.json"))
L82 = json.load(open("l82/results_l82.json"))
fails = []


def eq(tag, a, b):
    if a != b:
        fails.append(f"{tag}: got {a} != pinned {b}")


# ---- certification: my machinery vs l82 stored verdict, 3 shared arms ----
for a in ("hynohop", "hynohop_fb", "hynohop_fb07"):
    m, s = D["dist"][a], L82["distributions"][a]
    eq(f"cert {a} duty07", [m["duty07_k"], m["duty07_mean"], m["duty07_wilson"]],
       [s["duty07_k"], s["duty07_mean"], s["duty07_wilson"]])
    eq(f"cert {a} d07_per_seed", m["per_seed"]["d07"], s["duty07_per_seed"])
    for i in range(3):
        eq(f"cert {a} seg{i}", [m["segs"][i]["mean"], m["segs"][i]["k"],
                                m["segs"][i]["err_le01"]],
           [s["segs"][i]["mean"], s["segs"][i]["k_ge_half"], s["segs"][i]["err_le01"]])

# ---- anchors ----
A = D["anchors"]
eq("A1", A["A1_hynohop_xrun"], True)
eq("A2", A["A2_hybrid_xrun"], True)
eq("A3", A["A3_base_eq_hynohop"], True)
eq("A4 prefix", A["A4_prefix4000"], True)
eq("A4 firstdiv", A["A4_first_div_set"], [4001])
eq("A5", A["A5_glide_prefix"], True)
eq("A5h", A["A5h_hyglide_prefix"], True)
eq("A6", A["A6_fb07_fb_prefix"], True)

# ---- family table (PREREG-pinned) ----
TAB = {
 "hynohop":      ([[.605,.375,.488]], [0,16,0], 11,.547,(.444,.858),4800,667.5,None),
 "hynohop_fb":   ([[.739,.292,.608]], [0,16,0], 15,.673,(.717,.989),4800,667.5,.127),
 "hynohop_fb07": ([[.739,.216,.556]], [0,16,0], 12,.647,(.505,.898),4800,667.5,.0862),
 "glide200":     ([[.605,.202,.580]], [0,15,0], 11,.593,(.444,.858),4800,667.5,None),
 "glide300":     ([[.605,.366,.517]], [0,16,0], 10,.561,(.386,.815),4800,667.5,None),
 "glide400":     ([[.605,.368,.649]], [0,16,0], 13,.627,(.570,.934),4800,667.5,None),
 "cont":         ([[.377,.107,.548]], [0,12,0],  6,.462,(.185,.614),5600,783.8,None),
 "nod":          ([[.116,.168,.455]], [0,16,0],  2,.285,(.035,.360),3600,483.8,None),
 "echo":         ([[.739,.216,.466]], [0,16,0], 15,.603,(.717,.989),4800,667.5,.0431),
 "hybrid":       ([[.605,.402,.533]], [0,16,0], 13,.569,(.570,.934),4800,667.5,None),
 "hybrid_fb":    ([[.739,.298,.560]], [0,16,0], 13,.649,(.570,.934),4800,667.5,.1283),
 "hyglide300":   ([[.605,.287,.463]], [0,16,0],  9,.534,(.332,.769),4800,667.5,None),
}
for a, (segs, errs, k, mean, W, on, mass, er) in TAB.items():
    m = D["dist"][a]
    eq(f"{a} segs", [s["mean"] for s in m["segs"]], segs[0])
    eq(f"{a} err01", [s["err_le01"] for s in m["segs"]], errs)
    eq(f"{a} d07", [m["duty07_k"], m["duty07_mean"], m["duty07_wilson"]], [k, mean, list(W)])
    eq(f"{a} on", D["budget"]["on"][a], on)
    eq(f"{a} mass", D["budget"]["mass"][a], mass)
    if er is not None:
        key = {"echo": "echo(l84,seg0)"}.get(a, a)
        eq(f"{a} echo", D["budget"]["echo"][key]["ratio"], er)

# ---- oracles ----
ORC = {"O1": (.375,.590,.215,12, .548,.679, .603,.668),
       "O2": (.375,.561,.186,12, .649,.759, .627,.682),
       "O3": (.292,.401,.109,14, .608,.719, .673,.729),
       "O4": (.402,.565,.163,10, .533,.599, .569,.602)}
for o in D["oracles"]:
    tag = o["name"][:2]
    s1, s1o, s1g, pk, s2, s2o, dd, ddo = ORC[tag]
    eq(f"{tag} seg1", [o["seg1"]["best_fixed"], o["seg1"]["oracle_mean"],
                       o["seg1"]["gap"], o["seg1"]["pick_d07_k"]], [s1, s1o, s1g, pk])
    eq(f"{tag} seg2", [o["seg2"]["best_fixed"], o["seg2"]["oracle_mean"]], [s2, s2o])
    eq(f"{tag} d07", [o["d07"]["best_fixed"], o["d07"]["oracle_mean"]], [dd, ddo])

# ---- realizability ----
RZ = {"O2_glide300_minus_step_vs_SLexit": -.05, "O2_glide300_minus_step_vs_mmexit": .35,
      "O2_glide400_minus_step_vs_SLexit": -.5, "O2_glide400_minus_step_vs_mmexit": .226,
      "O3_fb07_minus_fb_seg1_vs_SLexit": .088, "O3_fb07_minus_fb_seg1_vs_mmexit": .206}
for k, v in RZ.items():
    eq(f"RZ {k}", D["realiz"][k], v)

GATE = {
    "G1_tracking": "seg1 block-err <= .01 on 16/16 census seeds",
    "G2a_duty07": "k >= 15/16 AND Wilson lb >= .717",
    "G2b_budget_tier": "k>=15 with echo ratio <= .0431 => BUDGET-DOMINANT (descriptive)",
    "G3_duty_fast_separate": "seg1 duty mean >= .358 (= .292 + 0.8*(.375-.292))",
    "G4_budget": "entrain on-steps <= 4800 AND echo ratio <= .127",
    "union_G2a_AND_G3": "DEMOTED to diagnostic: no fixed arm clears; best "
                        "branch-consistent oracle pick k=14 @ seg1 .401",
    "degenerate_branch": "always-fb mimic passes G1/G2a/G4, fails G3 (non-vacuous)",
    "training_go_no_go": "NO-GO on this branch library (realizability rho -.5..+.35, "
                         "n=16); GO requires a grown mid-seg branch library + re-measure",
}
out = dict(meta=dict(card="L85 gait-reachable-mass", seeds=16,
                     source="stored npz l59/l77/l82/l83/l84, zero new rollouts",
                     prereg="l85/PREREG.md"),
           certification="3 l82 arms equal to results_l82.json on every pinned read",
           anchors_pass=not fails, table=D["dist"], budget=D["budget"],
           oracles=D["oracles"], realizability=D["realiz"], GATE_L85=GATE)
json.dump(out, open("l85/mass_table.json", "w"), indent=1)

if fails:
    print("VERDICT FAIL — PREREG mismatches:")
    [print("  -", f) for f in fails]
    sys.exit(1)
print("VERDICT PASS — all anchors + certification + every PREREG-pinned value equal.")
print("GATE-L85:", json.dumps(GATE, indent=1)[:900])
print("written l85/mass_table.json")
