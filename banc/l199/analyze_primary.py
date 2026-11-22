"""L199 Parts A-C: the registered tone-phase test on STORED raws (zero
rollouts). Run from banc/ AFTER freeze. Writes l199/results_primary.json and
l199/primary.out. Written BEFORE any statistic was computed (PREREG)."""
import hashlib, json, os, sys
import numpy as np
sys.path.insert(0, "l199")
import ph
gj = ph.gj

OUT = "l199"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
frz = json.load(open(f"{OUT}/FREEZE.json"))
assert sha(f"{OUT}/PREREG.md") == frz["prereg_sha256"], "PREREG changed after freeze"
assert sha(f"{OUT}/ph.py") == frz["files"]["ph.py"], "instrument changed after freeze"
assert sha("l197b/gj.py") == json.load(open("l197b/FREEZE.json"))["files"]["gj.py"], "gj.py is not L197b's frozen readout"
SCHED = json.load(open("l197b/schedule.json"))
R197 = json.load(open("l197b/results_l197b.json"))
ADD = json.load(open("l197b/addendum.json"))
PHI = ph.tone_phi()

# ---- load ----
store = {}
for w in range(6):
    z = np.load(f"l197b/raw_w{w}.npz")
    for s in SCHED["arms"]["S"]["seeds"][w::6] + SCHED["arms"]["W"]["seeds"][w::6]:
        for k in ("gate_{s}", "Ti_fR_cutwA_{s}", "Ti_eR_cutwA_{s}", "Ti_fR_sc25_{s}", "Ti_eR_sc25_{s}"):
            store[k.format(s=s)] = z[k.format(s=s)]
R1 = json.load(open("l186/results_l186.json"))
z1 = np.load("l186/raw.npz")
DS = {}
for arm in ("S", "W"):
    d = gj.DESIGN[arm]
    seeds = SCHED["arms"][arm]["seeds"]
    ons = {s: [o[0], gj.SEG0[1] + o[1]] for s, o in ((s, SCHED["arms"][arm]["onsets"][str(s)]) for s in seeds)}
    for s in seeds:
        assert np.array_equal(store[f"gate_{s}"], gj.expected_gate(arm, SCHED["arms"][arm]["onsets"][str(s)])), (arm, s)
    DS[arm] = dict(raw=store, seeds=seeds, onsets=ons, pulse=d["pulse"], W=d["W"], starts=gj.starts_of(arm))
v1seeds = R1["seeds"]
v1ons = {s: R1["onsets"][str(s)] for s in v1seeds}
for s in v1seeds:
    g = z1[f"gate_{s}"]
    for o in v1ons[s]:
        assert g[o:o + 500].all() and not g[o - 25:o].any() and not g[o + 500:o + 525].any(), ("v1 gate", s, o)
v1raw = {k.format(s=s): z1[k.format(s=s)] for s in v1seeds
         for k in ("gate_{s}", "Ti_fR_cutwA_{s}", "Ti_eR_cutwA_{s}", "Ti_fR_sc25_{s}", "Ti_eR_sc25_{s}")}
DS["V1"] = dict(raw=v1raw, seeds=v1seeds, onsets=v1ons, pulse=500, W=150, starts=gj.starts_of("S"))

res = dict(design="L199 tone-phase registered test, Parts A-C (PREREG l199/PREREG.md)", status="FINAL",
           prereg_sha256=frz["prereg_sha256"], datasets={})
for tag, d in DS.items():
    for s in d["seeds"]:
        for o in d["onsets"][s]:
            g = d["raw"][f"gate_{s}"]
            assert g[o:o + d["pulse"]].all() and not g[o - 25:o].any()
    h, lag = ph.seg_duty(d["raw"], d["seeds"], d["onsets"], d["W"], d["starts"])
    A, B = ph.part_a(h, lag), ph.part_b(h, lag)
    C = ph.part_c(d["raw"], d["seeds"], d["onsets"], d["pulse"], PHI)
    res["datasets"][tag] = dict(n=len(d["seeds"]), W=int(d["W"]), n_offsets=len(d["starts"]), pulse=d["pulse"], A=A, B=B, C=C)
    np.savez_compressed(f"{OUT}/segduty_{tag}.npz", lag=lag, **{f"h_{g}": h[g] for g in h})

# ---- CERT-197b: this instrument == L197b's stored numbers ----
cert = {}
for arm in ("S", "W"):
    A = res["datasets"][arm]["A"]
    for mine, theirs in ((A["I"], R197["arms"][arm]["A_in_minus_anti"]), (A["A_inphase"], R197["arms"][arm]["A_inphase"]),
                         (A["E"], R197["arms"][arm]["A"]),
                         (A["A_antiphase"], R197["arms"][arm]["A_antiphase"])):
        assert abs(mine["value"] - theirs["value"]) < 1e-12 and np.allclose(mine["ci95"], theirs["ci95"], atol=1e-12), (arm, mine, theirs)
    for g in ph.GRAPHS:
        for b in ("inphase", "mid", "antiphase"):
            assert abs(A["profile"][g][b]["value"] - ADD[f"{arm}_by_graph"][g][f"aligned_{b}"]) < 1e-12, (arm, g, b)
    cert[arm] = "PASS (I, A_inphase, A_antiphase values + CIs == results_l197b.json; 6 bin means == addendum.json; 1e-12)"
res["cert_197b"] = cert
print("CERT-197b PASS (S, W)")

# ---- Part A verdict ----
lab = {t: res["datasets"][t]["A"]["label"] for t in DS}
ph1 = ("PH1_sign", "PH1_shape")
if lab["S"] in ph1 and lab["V1"] in ph1 and lab["W"] != "PH0":
    va = "PH1_sign" if lab["S"] == lab["V1"] == "PH1_sign" else "PH1"
elif sum(v == "PH0" for v in lab.values()) >= 2:
    va = "PH0"
else:
    va = "MIXED"
res["part_a_verdict"] = va
res["labels"] = dict(A=lab, B={t: res["datasets"][t]["B"]["label"] for t in DS}, C={t: res["datasets"][t]["C"]["label"] for t in DS})

# ---- descriptive: V1 at its own 500-step readout ----
h5, lag5 = ph.seg_duty(v1raw, v1seeds, v1ons, 500, np.arange(-250, 251, 10))
res["descriptive_V1_W500"] = dict(A=ph.part_a(h5, lag5), B=ph.part_b(h5, lag5))

# ---- predictions ----
D = res["datasets"]
below = lambda x: bool(x["value"] < 0 and x["ci95"][1] < 0)
above = lambda x: bool(x["value"] > 0 and x["ci95"][0] > 0)
near = lambda v, c: bool(abs(float(ph.wrap(v - c))) <= 45.0)
res["predictions"] = dict(
    Q1_cert=dict(correct=True),
    Q2_S=dict(base_slope_below0=below(D["S"]["A"]["slope"]["cutwA"]), removed_slope_above0=above(D["S"]["A"]["slope"]["sc25"]),
              label_PH1_sign=bool(lab["S"] == "PH1_sign")),
    Q3_W=dict(removed_slope_below0=below(D["W"]["A"]["slope"]["sc25"])),
    Q4_V1=dict(I_ge15_ci_above0=bool(D["V1"]["A"]["I"]["value"] >= .15 and D["V1"]["A"]["I"]["ci95"][0] > 0),
               base_slope_below0=below(D["V1"]["A"]["slope"]["cutwA"]), label=lab["V1"]),
    Q5_B=dict(S_base_near180=near(D["S"]["B"]["graphs"]["cutwA"]["theta"]["value"], 180), S_removed_near0=near(D["S"]["B"]["graphs"]["sc25"]["theta"]["value"], 0),
              S_label=D["S"]["B"]["label"], W_not_H1=bool(D["W"]["B"]["label"] != "H1")),
    Q6_C=dict(base_comove_all=bool(all(D[t]["C"]["cutwA"]["label"] == "co-move" for t in DS)), S_removed_label=D["S"]["C"]["sc25"]["label"]))
tmp = f"{OUT}/results_primary.json.tmp"
json.dump(res, open(tmp, "w"), indent=1, allow_nan=False)
os.replace(tmp, f"{OUT}/results_primary.json")

f3 = lambda d: f"{d['value']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]"
fa = lambda d: f"{d['value']:+.1f} (SE {d['se']:.1f})"
L = [f"L199 Parts A-C — Part A verdict {va} | A {lab} | B {res['labels']['B']} | C {res['labels']['C']}",
     f"CERT-197b PASS; PREREG {frz['prereg_sha256'][:16]}"]
for t in DS:
    A, B, C = (D[t][k] for k in "ABC")
    L += [f"[{t}] n {D[t]['n']} seeds, window {D[t]['W']}, bins in/mid/anti {A['bin_counts']}",
          "    profile in / mid / anti: " + " ; ".join(f"{g} {A['profile'][g]['inphase']['value']:.3f} / {A['profile'][g]['mid']['value']:.3f} / {A['profile'][g]['antiphase']['value']:.3f}" for g in ph.GRAPHS),
          f"    slope (in - anti): cutwA {f3(A['slope']['cutwA'])} | sc25 {f3(A['slope']['sc25'])} | I {f3(A['I'])} | pooled E {f3(A['E'])} -> {A['label']}",
          "    B: " + " ; ".join(f"{g} theta {fa(B['graphs'][g]['theta'])} R {B['graphs'][g]['R']:.3f}" for g in ph.GRAPHS)
          + f" | dtheta {fa(B['dtheta'])} | phenotype theta {fa(B['phenotype']['theta'])} R {B['phenotype']['R']:.3f} -> {B['label']}",
          "    B octants (0,45,..,315): " + " ; ".join(f"{g} " + " ".join("--" if x is None else f"{x:.2f}" for x in B["octants"][g]) for g in ph.GRAPHS),
          "    C: " + " ; ".join(f"{g} Delta {C[g]['Delta']['mean_deg']:+.1f} R {C[g]['Delta']['R']:.2f} n {C[g]['Delta']['n']} ({C[g]['label']})" for g in ph.GRAPHS)
          + f" | paired shift {C['paired_shift']['mean_deg']:+.1f} R {C['paired_shift']['R']:.2f} -> {C['label']}"]
A5 = res["descriptive_V1_W500"]["A"]
L.append(f"[V1 @ W500, descriptive] slope cutwA {f3(A5['slope']['cutwA'])} | sc25 {f3(A5['slope']['sc25'])} | I {f3(A5['I'])} ({A5['label']}); B {res['descriptive_V1_W500']['B']['label']}")
L.append("predictions: " + json.dumps(res["predictions"]))
open(f"{OUT}/primary.out", "w").write("\n".join(L) + "\n")
print("\n".join(L))
print("L199 PRIMARY WRITTEN (FINAL)")
