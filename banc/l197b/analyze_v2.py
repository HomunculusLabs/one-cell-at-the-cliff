"""L197b analysis: reads the six workers' stored raws, certifies, applies the
registered readout (gj.py) per design arm, writes results_l197b.json and
L197b-FINDINGS.md. Run from banc/. Written BEFORE any rollout (PREREG)."""
import hashlib, json, os, sys
import numpy as np
sys.path.insert(0, "l197b")
import gj

OUT = "l197b"
NW = 6
frz = json.load(open(f"{OUT}/FREEZE.json"))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
assert sha(f"{OUT}/PREREG.md") == frz["prereg_sha256"], "PREREG changed after freeze"
assert sha(f"{OUT}/schedule.json") == frz["schedule_sha256"]
assert sha(f"{OUT}/gj.py") == frz["files"]["gj.py"], "readout changed after freeze"
SCHED = json.load(open(f"{OUT}/schedule.json"))
assert SCHED["gate"]["pass"] is True
G_CUTWA, G_SC25 = 0.14365819573402408, 0.1454454553127289

# ---- CERT-V1 (readout reproduces stored v1) ----
R1 = json.load(open("l186/results_l186.json"))
v1 = gj.analyse(np.load("l186/raw.npz"), R1["seeds"], {int(k): v for k, v in R1["onsets"].items()},
                500, np.arange(-250, 251, 10))
for k in "ATD":
    assert abs(v1[k]["value"] - R1["contrasts"][k]["value"]) < 1e-12
    assert np.allclose(v1[k]["ci95"], R1["contrasts"][k]["ci95"], atol=1e-12)
print("CERT-V1 PASS (gj.analyse == results_l186.json)")

# ---- workers ----
anch, gains, secs = {}, {}, {}
store = {}
for w in range(NW):
    for nm in ("done", "anchors", "gains"):
        assert os.path.exists(f"{OUT}/{nm}_w{w}.json"), f"worker {w} incomplete ({nm}) — no read"
    anch[w] = json.load(open(f"{OUT}/anchors_w{w}.json"))
    gj_ = json.load(open(f"{OUT}/gains_w{w}.json"))
    dn = json.load(open(f"{OUT}/done_w{w}.json"))
    assert anch[w]["c0a_pass"] and anch[w]["c0a_max"] == 0.0 and anch[w]["n_checks"] == 92, w
    assert gj_["gain"] == {"cutwA": G_CUTWA, "sc25": G_SC25} and all(gj_["stored_exact"].values()), w
    assert dn["prereg_sha256"] == frz["prereg_sha256"]
    gains[w], secs[w] = gj_, dn["secs"]
    z = np.load(f"{OUT}/raw_w{w}.npz")
    mine = SCHED["arms"]["S"]["seeds"][w::NW] + SCHED["arms"]["W"]["seeds"][w::NW]
    assert dn["seeds"] == [801, 901] + mine
    for s in mine:
        for k in ("gate_{s}", "Ti_fR_cutwA_{s}", "Ti_eR_cutwA_{s}", "Ti_fR_sc25_{s}", "Ti_eR_sc25_{s}",
                  "GI1110_cutwA_{s}", "GI1110_sc25_{s}"):
            key = k.format(s=s)
            assert key not in store
            store[key] = z[key]
    for s in (801, 901):      # anchors unjittered
        t = np.arange(6000)
        canon = (t // 2000 == 1) | (((t % 2000) % 900 < 500) & (t % 2000 < 2000))
        assert np.array_equal(z[f"gate_{s}"], canon), ("anchor gate not canonical", w, s)
n_c0a = sum(anch[w]["n_checks"] for w in range(NW))
print(f"C0A: {n_c0a} checks across {NW} workers, max 0.0 | gains == stored EXACT in every worker")

res = dict(design="L197b gate-jitter v2 (PREREG l197b/PREREG.md)", status="FINAL",
           prereg_sha256=frz["prereg_sha256"], schedule_sha256=frz["schedule_sha256"],
           certs=dict(c0a_checks=n_c0a, c0a_max=0.0, gains_stored_exact=True, cert_v1="PASS",
                      worker_secs=secs),
           gains=dict(cutwA=G_CUTWA, sc25=G_SC25), arms={})
KEEP = ("A", "T", "D", "T_on", "T_off", "A_inphase", "A_antiphase", "A_in_minus_anti",
        "means", "tone_instrument", "rot_bin_share", "n", "W", "n_offsets")
for arm in ("S", "W"):
    d = gj.DESIGN[arm]
    seeds = SCHED["arms"][arm]["seeds"]
    onsets = {s: SCHED["arms"][arm]["onsets"][str(s)] for s in seeds}
    for s in seeds:       # the gate actually applied == the registered schedule
        g = store[f"gate_{s}"]
        assert np.array_equal(g, gj.expected_gate(arm, onsets[s])), (arm, s)
        assert list(g.reshape(3, -1).sum(1)) == [700 + d["pulse"], 2000, 700 + d["pulse"]]
        for k in ("Ti_fR", "Ti_eR"):
            for a in ("cutwA", "sc25"):
                y = store[f"{k}_{a}_{s}"]
                assert y.shape == (6000,) and np.isfinite(y).all()
        assert np.isfinite(store[f"GI1110_cutwA_{s}"]).all() and np.isnan(store[f"GI1110_sc25_{s}"]).all()
    ov = gj.overlap_stats(onsets, seeds, d["W"])
    assert abs(ov["mean_overlap"] - SCHED["arms"][arm]["overlap"]["mean_overlap"]) < 1e-12 and ov["mean_overlap"] <= .25
    # POST-FREEZE PLUMBING FIX (19:25, before any v2 statistic was computed: the
    # frozen script stopped on gj.pair_hits' segment-bounds assert): the schedule
    # stores onsets RELATIVE to each outer segment's start, the readout takes
    # ABSOLUTE steps (v1's convention). Frozen original: analyze_v2.frozen.py.
    onsets_abs = {s: [o[0], gj.SEG0[1] + o[1]] for s, o in onsets.items()}
    for s in seeds:
        g = store[f"gate_{s}"]
        for o in onsets_abs[s]:
            assert g[o:o + d["pulse"]].all() and not g[o - 25:o].any() and not g[o + d["pulse"]:o + d["pulse"] + 25].any()
    a_ = gj.analyse(store, seeds, onsets_abs, d["W"], gj.starts_of(arm))
    r = {k: a_[k] for k in KEEP}
    A, T, D = (a_[k]["value"] for k in "ATD")
    lo, hi = a_["D"]["ci95"]
    hw = (hi - lo) / 2
    r["overlap"] = ov
    r["half_width_D"] = hw
    r["R0_no_elevation"] = bool(A < .15 and T < .15)
    r["clock"] = ("E1_external" if D >= .10 and lo > 0 else
                  "E2_elapsed" if D <= -.10 and hi < 0 else
                  "E3_equal_resolved" if lo > -.10 and hi < .10 else "E3_unresolved")
    r["underpowered_again"] = bool(hw > .10)
    r["clock_status"] = ("NOT READ (UNDERPOWERED_AGAIN)" if r["underpowered_again"] else
                         "DESCRIPTIVE (R0: no elevation at this resolution)" if r["R0_no_elevation"] else "READ")
    toff, din, aan, ain = a_["T_off"], a_["A_in_minus_anti"], a_["A_antiphase"], a_["A_inphase"]
    r["mechanism"] = ("M_internal" if toff["value"] >= .15 and toff["ci95"][0] > 0 else
                      "M_tone" if din["value"] >= .15 and din["ci95"][0] > 0 and aan["value"] < .15 else
                      "M_gate" if ain["value"] >= .15 and aan["value"] >= .15 and ain["ci95"][0] > 0
                      and aan["ci95"][0] > 0 else "M_unassigned")
    ti = a_["tone_instrument"]
    r["tone_control_verbatim_not_predictive"] = bool(all(abs(ti[g]["rho_rot"]) < .25 for g in ti))
    r["pair_matrices_sha256"] = hashlib.sha256(json.dumps(a_["pair_matrices"]).encode()).hexdigest()
    np.savez_compressed(f"{OUT}/pairmat_{arm}.npz", **{f"{g}_{c}": np.array(a_["pair_matrices"][g][c])
                                                       for g in a_["pair_matrices"] for c in ("aligned", "elapsed")})
    res["arms"][arm] = r
votes = [res["arms"][a]["clock"] for a in ("S", "W")
         if not res["arms"][a]["R0_no_elevation"] and not res["arms"][a]["underpowered_again"]]
if len(votes) == 2 and votes[0] == votes[1]:
    res["verdict"] = {"E1_external": "E1", "E2_elapsed": "E2", "E3_equal_resolved": "E3_EQUAL_POWERED",
                      "E3_unresolved": "E3_UNRESOLVED_BOTH"}[votes[0]]
elif len(votes) == 1:
    only = [a for a in ("S", "W") if not res["arms"][a]["R0_no_elevation"] and not res["arms"][a]["underpowered_again"]][0]
    res["verdict"] = f"{votes[0]} (arm {only} alone; the other arm does not vote)"
elif len(votes) == 0:
    res["verdict"] = "NO_VOTE (R0 / underpowered in both arms)"
else:
    res["verdict"] = "ARM_DEPENDENT"
res["mechanism_verdict"] = {a: res["arms"][a]["mechanism"] for a in ("S", "W")}
S, Wd = res["arms"]["S"], res["arms"]["W"]
ti = S["tone_instrument"]
res["predictions"] = dict(
    P1_certs_complete=dict(correct=True),
    P2_S=dict(got=[S["R0_no_elevation"], S["clock"], S["D"]["value"]],
              R0_correct=bool(S["R0_no_elevation"]), class_correct=bool(S["clock"] == "E3_equal_resolved"),
              D_in_minus10_0=bool(-.10 < S["D"]["value"] < 0)),
    P3_W=dict(got=[Wd["A"]["value"], Wd["clock"], Wd["D"]["value"]], A_ge_10=bool(Wd["A"]["value"] >= .10),
              modal_class_correct=bool(Wd["clock"] == "E3_equal_resolved"), D_positive=bool(Wd["D"]["value"] > 0)),
    P4_M_tone_both=dict(got=res["mechanism_verdict"], correct=bool(all(v == "M_tone" for v in res["mechanism_verdict"].values()))),
    P5_no_M_internal=dict(got=[S["T_off"]["ci95"], Wd["T_off"]["ci95"]],
                          correct=bool(S["T_off"]["ci95"][1] < .15 and Wd["T_off"]["ci95"][1] < .15
                                       and "M_internal" not in res["mechanism_verdict"].values())),
    P6_instrument=dict(got=[ti["sc25"]["rho_rot"], ti["cutwA"]["rho_rot"], ti["sc25"]["rho_rot_segment_aligned"]],
                       correct=bool(S["tone_control_verbatim_not_predictive"] and ti["sc25"]["rho_rot_segment_aligned"] > .25)),
    P7_halfwidth=dict(got=[S["half_width_D"], Wd["half_width_D"]],
                      correct=bool(S["half_width_D"] <= .06 and Wd["half_width_D"] <= .06)))
tmp = f"{OUT}/results_l197b.json.tmp"
json.dump(res, open(tmp, "w"), indent=1, allow_nan=False)
os.replace(tmp, f"{OUT}/results_l197b.json")
f3 = lambda d: f"{d['value']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]"
L = [f"L197b gate-jitter v2 — verdict {res['verdict']} | mechanism {res['mechanism_verdict']}",
     f"n = 96 seeds per design arm; C0A {n_c0a} checks max 0.0; gains == stored EXACT; CERT-V1 PASS; PREREG {frz['prereg_sha256'][:16]}"]
for arm in ("S", "W"):
    r = res["arms"][arm]
    d = gj.DESIGN[arm]
    L += [f"[{arm}] pulse {d['pulse']}, window {d['W']}, mean overlap {r['overlap']['mean_overlap']:.3f} | clock {r['clock']} ({r['clock_status']})",
          "    duty aligned / elapsed / same-seed: " + " ; ".join(f"{g} {m['aligned']:.3f} / {m['elapsed']:.3f} / {m['same']:.3f}" for g, m in r["means"].items()),
          f"    A {f3(r['A'])} | T {f3(r['T'])} | D {f3(r['D'])} (half-width {r['half_width_D']:.3f})",
          f"    T_on {f3(r['T_on'])} (share {r['T_on']['window_share']:.2f}) | T_off {f3(r['T_off'])}",
          f"    A_inphase {f3(r['A_inphase'])} | A_antiphase {f3(r['A_antiphase'])} | in - anti {f3(r['A_in_minus_anti'])} -> {r['mechanism']}",
          "    tone control: " + " ; ".join(f"{g} verbatim rho {v['rho_rot']:+.3f}, segment-level rho(aligned) {v['rho_rot_segment_aligned']:+.3f}" for g, v in r["tone_instrument"].items())]
L.append("predictions: " + json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'got'} for k, v in res["predictions"].items()}))
open(f"{OUT}/verdict.out", "w").write("\n".join(L) + "\n")
print("\n".join(L))
print("L197b VERDICT WRITTEN (FINAL)")
