#!/usr/bin/env python
"""tick 216 independent verification of L186 (gate-jitter discriminator).

Zero rollouts. Reads only l186's stored artifacts + prior-run stored pins.
Recomputes: duty means, delete-one-seed jackknife CIs for A/T/D, schedule
legality, seed freshness, the C0A pin and the gain pin -- and ADDS one
instrument the child did not run: does the per-pair aligned-minus-elapsed
duty difference track the relative TONE-phase rotation the gate jitter
induces?  (If the cross-seed lock were carried by the shared elapsed-time
tone, aligned coordinates would degrade as that rotation nears antiphase.)
"""
import json, os, glob, zipfile, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BANC = os.path.dirname(HERE)
R = json.load(open(os.path.join(HERE, "results_l186.json")))
out, fail = {}, []


def chk(name, cond, detail=""):
    out[name] = bool(cond)
    print(("PASS " if cond else "FAIL ") + name + ("  " + detail if detail else ""))
    if not cond:
        fail.append(name)


# ---------------------------------------------------------------- seeds/schedule
seeds = [int(s) for s in R["seeds"]]
onsets = {int(k): [int(v) for v in vs] for k, vs in R["onsets"].items()}
chk("S1_16_fresh_seeds", len(seeds) == 16 and seeds == list(range(18601, 18617)),
    f"seeds={seeds[0]}..{seeds[-1]} n={len(seeds)}")
chk("S2_anchors_excluded_from_seed_set", not any(s in seeds for s in (801, 901)),
    "801/901 are anchors, not analysis seeds")
chk("S2b_anchor_schedules_unjittered", onsets.get(801) == [900, 4900] and onsets.get(901) == [900, 4900],
    f"801={onsets.get(801)} 901={onsets.get(901)} (C0A arms must keep the stored schedule)")

legal, d1, d2 = True, [], []
for s in seeds:
    a, b = onsets[s]
    d1.append(a - 900)
    d2.append(b - 4900)
    if not (600 <= a <= 1200 and a + 500 <= 2000 and 4600 <= b <= 5200 and b + 500 <= 6000):
        legal = False
chk("S3_schedule_in_registered_band", legal,
    f"seg0 onsets {min(o[0] for o in (onsets[s] for s in seeds))}-"
    f"{max(o[0] for o in (onsets[s] for s in seeds))} (900+-300), "
    f"seg2 {min(o[1] for o in (onsets[s] for s in seeds))}-"
    f"{max(o[1] for o in (onsets[s] for s in seeds))} (4900+-300), 500-step pulse inside segment")
chk("S4_jitter_nondegenerate_and_independent", len(set(d1)) > 8 and len(set(d2)) > 8
    and abs(np.corrcoef(d1, d2)[0, 1]) < 0.6,
    f"{len(set(d1))}/{len(set(d2))} distinct offsets, r(seg0,seg2)={np.corrcoef(d1,d2)[0,1]:+.2f}")

hits = []
for f in sorted(glob.glob(os.path.join(BANC, "**", "*.npz"), recursive=True)):
    if os.path.dirname(os.path.abspath(f)) == HERE:
        continue
    try:
        with zipfile.ZipFile(f) as z:
            names = " ".join(z.namelist())
    except Exception:
        continue
    for tok in re.findall(r"\d{4,}", names):
        if int(tok) in seeds:
            hits.append((os.path.relpath(f, BANC), tok))
chk("S5_no_seed_token_collision", not hits, f"{len(hits)} hits over prior banc npz archives")

# ---------------------------------------------------------------- C0A + gains
anc = R["anchors"]
chk("C0A_anchor_identity_zero", anc["c0a_pass"] is True and float(anc["c0a_max"]) == 0.0,
    f"{anc['n_checks']} checks, max |delta| = {anc['c0a_max']}, pairs {anc['pairs']}")
STORED_CUTWA = 0.14365819573402408  # l144 g_sil1110_wA / l150 g_silW / l173b pin
g = R["gains"]["gain"]
chk("G1_cutwA_gain_exact_vs_lineage_pin", float(g["cutwA"]) == STORED_CUTWA, f"{g['cutwA']!r}")
chk("G2_flagged_stored_exact", all(R["gains"]["stored_exact"].values()))
chk("G3_af_matched_across_arms", abs(R["gains"]["af_final"]["cutwA"] - R["gains"]["af_final"]["sc25"]) < 5e-4,
    f"af {R['gains']['af_final']['cutwA']:.5f} vs {R['gains']['af_final']['sc25']:.5f} "
    f"(sc25 gain +{100*(g['sc25']/STORED_CUTWA-1):.3f}% vs cut base)")

# ---------------------------------------------------------------- means + CIs
clocks = R["clock_order"]
chk("P0_clock_order", clocks == ["aligned", "elapsed"], str(clocks))
M = {}
for arm in ("cutwA", "sc25"):
    mats = R["ordered_pair_duties"][arm]
    for ci, cl in enumerate(clocks):
        A = np.array(mats[ci], dtype=float)
        assert A.shape == (16, 16), A.shape
        M[(arm, cl)] = A
    diag_al = np.diag(M[(arm, "aligned")])
    diag_el = np.diag(M[(arm, "elapsed")])
    chk(f"P1_{arm}_diagonal_clock_invariant", np.array_equal(diag_al, diag_el),
        "same-seed diagonal identical between clocks (wiring check)")
    chk(f"P2_{arm}_same_mean", abs(float(diag_al.mean()) - R["means"][arm]["same"]) < 5e-4,
        f"recomputed {diag_al.mean():.4f} vs stored {R['means'][arm]['same']:.4f}")
    for cl in clocks:
        A = M[(arm, cl)]
        off = A[~np.eye(16, dtype=bool)]
        chk(f"M_{arm}_{cl}", abs(float(off.mean()) - R["means"][arm][cl]) < 5e-4,
            f"recomputed {off.mean():.4f} vs stored {R['means'][arm][cl]:.4f} over {off.size} ordered pairs")


def sub_off(A, idx):
    S = A[np.ix_(idx, idx)]
    m = ~np.eye(len(idx), dtype=bool)
    return float(S[m].mean())


def jack(fn):
    full = fn(list(range(16)))
    reps = np.array([fn([k for k in range(16) if k != d]) for d in range(16)])
    n = 16.0
    se = np.sqrt((n - 1) / n * ((reps - reps.mean()) ** 2).sum())
    return full, (full - 1.96 * se, full + 1.96 * se)


def contrast(cl, idx):
    return sub_off(M[("sc25", cl)], idx) - sub_off(M[("cutwA", cl)], idx)


for nm, cl in (("A", "aligned"), ("T", "elapsed")):
    val, ci = jack(lambda idx, cl=cl: contrast(cl, idx))
    st = R["contrasts"][nm]
    chk(f"C_{nm}_value", abs(val - st["value"]) < 5e-4, f"recomputed {val:+.4f} vs stored {st['value']:+.4f}")
    chk(f"C_{nm}_ci_excludes_zero_above", ci[0] > 0 and st["ci95"][0] > 0,
        f"recomputed [{ci[0]:+.3f},{ci[1]:+.3f}] vs stored [{st['ci95'][0]:+.3f},{st['ci95'][1]:+.3f}]")
    chk(f"C_{nm}_survival_bar", val >= 0.15, "registered survival bar A/T >= .15")
    out[f"c_{nm}"] = [val, list(ci)]

valD, ciD = jack(lambda idx: contrast("aligned", idx) - contrast("elapsed", idx))
stD = R["contrasts"]["D"]
chk("C_D_value", abs(valD - stD["value"]) < 5e-4, f"recomputed {valD:+.4f} vs stored {stD['value']:+.4f}")
chk("C_D_ci_straddles_zero", ciD[0] < 0 < ciD[1],
    f"recomputed [{ciD[0]:+.3f},{ciD[1]:+.3f}] vs stored [{stD['ci95'][0]:+.3f},{stD['ci95'][1]:+.3f}]")
chk("E3_branch_consistent", R["branch"].startswith("E3") and abs(valD) < 0.10,
    f"branch={R['branch']}, |D|={abs(valD):.3f} < the registered .10 margin for E1/E2")
out["c_D"] = [valD, list(ciD)]

# ------------------------------------------------------- tick-216 ADDED INSTRUMENT
# The jitter displaces the GATE; the 0.7-Hz tone keeps running on elapsed time
# (registered).  For ordered pair (i,j) the aligned clock shifts seed j's window
# by (onset_i - onset_j) relative to the elapsed clock, rotating the RELATIVE
# TONE PHASE by that lag mod one period.  Tone-carried lock => aligned duty must
# fall as the rotation approaches antiphase.
DT, F = 0.01, 0.7
per = 1.0 / F / DT  # 142.857 steps per tone period
rows = []
for arm in ("sc25", "cutwA"):
    Aal, Ael = M[(arm, "aligned")], M[(arm, "elapsed")]
    rot, dd, lag = [], [], []
    for i, si in enumerate(seeds):
        for j, sj in enumerate(seeds):
            if i == j:
                continue
            L = float(np.mean(np.array(onsets[si]) - np.array(onsets[sj])))
            r = abs(((L / per) % 1.0) - 0.5) * 2.0  # 1 = in phase, 0 = antiphase
            rot.append(r); lag.append(abs(L)); dd.append(Aal[i, j] - Ael[i, j])
    rot, dd, lag = np.array(rot), np.array(dd), np.array(lag)
    rho = float(np.corrcoef(rot, dd)[0, 1])
    near, far = rot >= 0.75, rot <= 0.25
    rows.append(dict(arm=arm, n=int(rot.size), rho_rot=rho,
                     rho_abslag=float(np.corrcoef(lag, dd)[0, 1]),
                     d_inphase=float(dd[near].mean()), n_inphase=int(near.sum()),
                     d_antiphase=float(dd[far].mean()), n_antiphase=int(far.sum()),
                     aligned=float(Aal[~np.eye(16, dtype=bool)].mean()),
                     elapsed=float(Ael[~np.eye(16, dtype=bool)].mean())))
    print(f"\n[tick-216 instrument | {arm}] tone-phase rotation vs (aligned - elapsed) pair duty")
    print(f"   n={rot.size}  rho(rotation)={rho:+.3f}  rho(|lag|)={rows[-1]['rho_abslag']:+.3f}")
    print(f"   near-in-phase (n={near.sum()}): mean delta {dd[near].mean():+.4f} | "
          f"near-antiphase (n={far.sum()}): mean delta {dd[far].mean():+.4f}")
out["tone_instrument"] = rows
out["tone_period_steps"] = per
chk("I1_tone_rotation_not_predictive", all(abs(r["rho_rot"]) < 0.25 for r in rows),
    "|rho| < .25 both arms => the cross-seed duty readout is not locked to the shared tone phase")
chk("I2_jitter_spans_multiple_tone_periods", (max(d1) - min(d1)) / per > 2.0,
    f"seg0 jitter span {max(d1)-min(d1)} steps = {(max(d1)-min(d1))/per:.1f} tone periods")

# ---------------------------------------------------------------- phase block
ph = R["phase"]
chk("PH1_both_pools_concentrated", all(ph[k]["R"] >= 0.7 for k in ("Ti_fR", "Ti_eR")),
    f"R flex {ph['Ti_fR']['R']:.3f} / ext {ph['Ti_eR']['R']:.3f}")
chk("PH2_phase_near_quarter_cycle", all(-135 < ph[k]["degrees"] < -45 for k in ("Ti_fR", "Ti_eR")),
    f"flex {ph['Ti_fR']['degrees']:.1f} deg / ext {ph['Ti_eR']['degrees']:.1f} deg")
chk("PH3_n_is_16", all(ph[k]["n"] == 16 for k in ("Ti_fR", "Ti_eR")))

out["_fail"] = fail
json.dump(out, open(os.path.join(HERE, "t216_verify.json"), "w"), indent=1, sort_keys=True)
n = sum(1 for k, v in out.items() if isinstance(v, bool))
print("\n" + (f"ALL GREEN ({n} named checks)" if not fail else "FAILED: " + ", ".join(fail)))
