# ===================== L226 TAIL — the FLOOR currency OUT OF SAMPLE ====
# PREREG l226/PREREG.md (frozen BEFORE l226_run.py existed).
#
# Everything above this line is INHERITED VERBATIM SOURCE:
#   slice 1 = l169b2_verdict.py 13-63   (s_arrays / duty_seeds / side_k)
#   slice 2 = l208_add_tail.py 55-72    (flo_side / spearman = the currency)
#   slice 3 = l214_tail.py 1-95         (the FROZEN rule's constants, window,
#                                        CERT-FLO 40 + CERT-RHO 100 — both
#                                        re-run FREE before any B38 number)
# so the per-cell estimator is bit-identical to L214's, not re-implemented.

B38 = list(range(3801, 3817))
P38 = "l226/raw_l226.npz"
FP38 = (os.stat(P38).st_size, os.stat(P38).st_mtime_ns)
RAW38 = np.load(P38)
assert len(B38) == SIGNS.shape[1] == 16, "B38 size != frozen SIGNS width"
AN38 = json.load(open("l226/anchors_run.json"))

# ---- premise gates on the batch itself (PREREG 0a) --------------------
assert AN38["c0a_pass"] and AN38["fc169b2_pass"], "L226 run anchors FAILED"
assert AN38["fc169b2_max"] == 0.0, ("CERT-SUBSET not bit-exact",
                                    AN38["fc169b2_max"])
assert AN38["ntf4_pass"] and all(AN38["f4_gain_exact"].values())
assert sorted(AN38["arms"]) == sorted(ARMS5), ("arm slice drift", AN38["arms"])
assert AN38["batch"] == B38, ("batch drift", AN38["batch"])
for _a5 in ARMS5:
    for _s5 in B38:
        assert f"mm_{_a5}_{_s5}" in RAW38.files, ("B38 coverage", _a5, _s5)
print(f"premise GREEN: CERT-SUBSET {AN38['cert_subset_checks']} checks at "
      f"max {AN38['fc169b2_max']:.1e}; 5 arms x 16 fresh seeds present")

ARMPAIR = [(pk, arm) for pk in PAIRS2 for arm in ARMS5]
assert len(ARMPAIR) == 10

# ============ CERT-BH: the BH procedure re-implemented here is GATED by
# reproducing L214's stored per-batch survivor sets EXACTLY.
S214 = json.load(open("l214/static.json"))
FP214 = (os.stat("l214/static.json").st_size,
         os.stat("l214/static.json").st_mtime_ns)


def bh(hyp, q):
    """hyp = [(p, name), ...]; returns (kmax, survivors, smallest_p, name)."""
    hyp = sorted(hyp)
    m = len(hyp)
    kmax = 0
    for i, (p, _n) in enumerate(hyp, start=1):
        if p <= (i / m) * q:
            kmax = i
    return kmax, [n for _p, n in hyp[:kmax]], hyp[0][0], hyp[0][1]


nbh = 0
for bk in ("B36", "B37"):
    hyp = []
    for pk, arm in ARMPAIR:
        c = CUR[f"{bk}|{pk}|{arm}"]
        hyp.append((c["p_up"], f"{pk}|{arm}|up"))
        hyp.append((c["p_dn"], f"{pk}|{arm}|dn"))
    k, surv, sp, sn = bh(hyp, QFDR)
    w = S214["q2"][bk]
    assert k == w["n_survivors"] and surv == w["survivors"], ("CERT-BH", bk)
    assert sp == w["smallest_p"] and sn == w["smallest"], ("CERT-BH p", bk)
    nbh += 4
print(f"CERT-BH: {nbh} stored BH outputs reproduced EXACTLY (B36, B37)")

# ============ CERT-SGN: the sign-agreement currency (per-cell MEANS, the
# PREREG-0d definition taken from l214_tail.py 208-211) reproduces L214's
# published 17/20 before any B38 sign is counted.
def sign_agree(cells):
    return sum((CUR[k]["mean_A"] > 0) == (CUR[k]["mean_dS"] > 0) for k in cells)


sa36 = sign_agree([f"B36|{pk}|{arm}" for pk, arm in ARMPAIR])
sa37 = sign_agree([f"B37|{pk}|{arm}" for pk, arm in ARMPAIR])
assert sa36 + sa37 == S214["q3"]["sign_agree_floor"] == 17, (sa36, sa37)
print(f"CERT-SGN: per-batch sign agreement {sa36}/10 + {sa37}/10 == stored "
      f"{S214['q3']['sign_agree_floor']}/20")

# ============ CERT-Q1: the self-ranked cross-batch null re-implemented
# here reproduces L214's stored p_C / C_null moments at FLOAT EQUALITY.
SELF = {}
for key, c in CUR.items():
    srt = np.sort(c["null"])
    SELF[key] = dict(
        p_up=(N_PERM - np.searchsorted(srt, c["null"], side="left")) / N_PERM,
        p_dn=np.searchsorted(srt, c["null"], side="right") / N_PERM)

prng = np.random.default_rng(PAIR_SEED)
SIG = prng.permutation(N_PERM)
C_null = np.zeros(N_PERM, np.int64)
for pk, arm in ARMPAIR:
    a = SELF[f"B36|{pk}|{arm}"]
    b = SELF[f"B37|{pk}|{arm}"]
    up = (a["p_up"] < ALPHA) & (b["p_up"][SIG] < ALPHA)
    dn = (a["p_dn"] < ALPHA) & (b["p_dn"][SIG] < ALPHA)
    C_null += (up | dn).astype(np.int64)
_w1 = S214["q1"]
assert float((C_null >= _w1["C_obs"]).mean()) == _w1["p_C"], "CERT-Q1 p_C"
assert float(C_null.mean()) == _w1["C_null_mean"], "CERT-Q1 mean"
assert float(C_null.var()) == _w1["C_null_var"], "CERT-Q1 var"
assert int(C_null.max()) == _w1["C_null_max"], "CERT-Q1 max"
assert _w1["cells"] == ["Tr|f4ng|up"] and _w1["C_obs"] == 1
print(f"CERT-Q1: stored p_C {_w1['p_C']} + 3 null moments reproduced at "
      f"FLOAT EQUALITY; the replicating cell is {_w1['cells'][0]}")
print("ALL GATES PASSED — reading B38 for the first time now\n")

# ================= B38: the frozen rule, out of sample =================
CUR38, SELF38 = {}, {}
for pk, arm in ARMPAIR:
    key = f"B38|{pk}|{arm}"
    dL, dR = duty_seeds(RAW38, arm, B38, pk)
    dS = np.array([float(dL[i] - dR[i]) for i in range(len(B38))])
    rows = [flo_side(RAW38, arm, s, pk, W) for s in B38]
    A = np.array([r["R"] - r["L"] for r in rows])
    rho = spearman(dS, A)
    null = np.array([spearman(dS * SIGNS[j], A) for j in range(N_PERM)])
    srt = np.sort(null)
    CUR38[key] = dict(rho=rho,
                      p_up=float((null >= rho).mean()),
                      p_dn=float((null <= rho).mean()),
                      mean_A=float(A.mean()), mean_dS=float(dS.mean()),
                      floL=float(np.mean([r["L"] for r in rows])),
                      floR=float(np.mean([r["R"] for r in rows])),
                      null_sd=float(null.std()))
    SELF38[key] = dict(
        p_up=(N_PERM - np.searchsorted(srt, null, side="left")) / N_PERM,
        p_dn=np.searchsorted(srt, null, side="right") / N_PERM)

ACTOR = "B38|Tr|f4ng"
p_up38 = CUR38[ACTOR]["p_up"]
SA38 = sum((CUR38[f"B38|{pk}|{arm}"]["mean_A"] > 0) ==
           (CUR38[f"B38|{pk}|{arm}"]["mean_dS"] > 0) for pk, arm in ARMPAIR)
SA_BAR = 7
# PREREG 0e: the card's 7/10 bar is a REPLICATION threshold, not an alpha.
binom_p = sum(math.comb(10, k) for k in range(SA_BAR, 11)) / 2 ** 10

cell_ok = p_up38 < ALPHA
cur_ok = SA38 >= SA_BAR
if cell_ok and cur_ok:
    q1 = "O_TRANSPORTS"
elif cur_ok:
    q1 = "O_CELL_FAILS"
elif cell_ok:
    q1 = "O_CELL_ONLY"
else:
    q1 = "O_CURRENCY_FAILS"

ranked = sorted((CUR38[f"B38|{pk}|{arm}"]["p_up"], f"{pk}|{arm}")
                for pk, arm in ARMPAIR)
rank_actor = [n for _p, n in ranked].index("Tr|f4ng") + 1

print(f"Q1 PRIMARY (frozen rule, out of sample): Tr|f4ng rho "
      f"{CUR38[ACTOR]['rho']:+.4f} p_up {p_up38:.5f} (p_dn "
      f"{CUR38[ACTOR]['p_dn']:.5f}) vs ALPHA {ALPHA} -> "
      f"{'SIGNIFICANT' if cell_ok else 'MISS'}; p_up rank {rank_actor}/10")
print(f"   sign agreement B38 {SA38}/10 vs registered bar {SA_BAR} "
      f"(exact binomial P(X>={SA_BAR}) = {binom_p:.4f}, DISCLOSED: the bar "
      f"is a replication threshold, not an alpha-.05 test)")
print(f"   prior batches (OBSERVED, description): B36 p_up "
      f"{CUR['B36|Tr|f4ng']['p_up']:.5f} SA {sa36}/10 | B37 p_up "
      f"{CUR['B37|Tr|f4ng']['p_up']:.5f} SA {sa37}/10")
print(f"Q1 BRANCH -> {q1}")

# ---- Q2 (companion): BH within B38's own 20 hypotheses
hyp38 = []
for pk, arm in ARMPAIR:
    c = CUR38[f"B38|{pk}|{arm}"]
    hyp38.append((c["p_up"], f"{pk}|{arm}|up"))
    hyp38.append((c["p_dn"], f"{pk}|{arm}|dn"))
k38, surv38, sp38, sn38 = bh(hyp38, QFDR)
print(f"\nQ2 BH B38: {k38}/20 survive at q={QFDR} -> {surv38} "
      f"(smallest p {sp38} = {sn38})")

# ---- Q3 (companion): three-batch joint replication + its null
C3_cells = []
for pk, arm in ARMPAIR:
    a, b, c = (CUR[f"B36|{pk}|{arm}"], CUR[f"B37|{pk}|{arm}"],
               CUR38[f"B38|{pk}|{arm}"])
    up = a["p_up"] < ALPHA and b["p_up"] < ALPHA and c["p_up"] < ALPHA
    dn = a["p_dn"] < ALPHA and b["p_dn"] < ALPHA and c["p_dn"] < ALPHA
    if up or dn:
        C3_cells.append(f"{pk}|{arm}" + ("|up" if up else "|dn"))
C3 = len(C3_cells)
# DECLARED as an EXTENSION of L214's Q1 machinery: a SECOND permutation is
# drawn from the same PAIR_SEED stream (the first one is bit-identical to
# L214's, gated by CERT-Q1 above), so the three batches are independent
# under the null.
SIG2 = prng.permutation(N_PERM)
C3_null = np.zeros(N_PERM, np.int64)
for pk, arm in ARMPAIR:
    a = SELF[f"B36|{pk}|{arm}"]
    b = SELF[f"B37|{pk}|{arm}"]
    c = SELF38[f"B38|{pk}|{arm}"]
    up = ((a["p_up"] < ALPHA) & (b["p_up"][SIG] < ALPHA)
          & (c["p_up"][SIG2] < ALPHA))
    dn = ((a["p_dn"] < ALPHA) & (b["p_dn"][SIG] < ALPHA)
          & (c["p_dn"][SIG2] < ALPHA))
    C3_null += (up | dn).astype(np.int64)
p_C3 = float((C3_null >= C3).mean()) if C3 > 0 else float("nan")
print(f"Q3 three-batch joint replication: C3 {C3} {C3_cells} | null mean "
      f"{C3_null.mean():.5f} max {int(C3_null.max())} | p_C3 {p_C3}")

# ---- Q4 (descriptive): the full B38 table
absrank = sorted((abs(CUR38[f"B38|{pk}|{arm}"]["mean_A"]), f"{pk}|{arm}")
                 for pk, arm in ARMPAIR)
absrank_of = {n: i + 1 for i, (_v, n) in enumerate(absrank)}
print("\nQ4 B38 per-cell table (rho | p_up | p_dn | mean_A | mean_dS | "
      "sign | |A| rank):")
for pk, arm in ARMPAIR:
    c = CUR38[f"B38|{pk}|{arm}"]
    ag = (c["mean_A"] > 0) == (c["mean_dS"] > 0)
    print(f"  {pk}|{arm:8s} {c['rho']:+.4f} | {c['p_up']:.5f} | "
          f"{c['p_dn']:.5f} | {c['mean_A']:+.5f} | {c['mean_dS']:+.5f} | "
          f"{'agree' if ag else 'DISAGREE'} | {absrank_of[f'{pk}|{arm}']}")

# ---- predictions
P = {}
P["P1_O_TRANSPORTS"] = bool(q1 == "O_TRANSPORTS")
P["P2_actor_p_up_lt_alpha"] = bool(cell_ok)
P["P3_SA38_ge_7"] = bool(cur_ok)
P["P4_actor_smallest_p_up"] = bool(rank_actor == 1)
P["P5_actor_survives_BH"] = bool("Tr|f4ng|up" in surv38)
P["P6_cert_subset_exactly_zero"] = bool(AN38["fc169b2_max"] == 0.0)
print("\npredictions:", {k: bool(v) for k, v in P.items()},
      f"-> {sum(bool(v) for v in P.values())}/6")

READING = {
    "O_TRANSPORTS": ("the floor currency AND the single cell replicate "
                     "out of sample; L214's p_C .0465 stops being a "
                     "description of an observed pattern and becomes a "
                     "prediction that held"),
    "O_CELL_FAILS": ("the CURRENCY transports but Tr|f4ng was a "
                     "within-batch hit (the card's registered failure "
                     "reading 1)"),
    "O_CURRENCY_FAILS": ("the floor leg was a two-batch coincidence and "
                         "L208's descriptive mechanism loses its only "
                         "quantitative support (the card's registered "
                         "failure reading 2)"),
    "O_CELL_ONLY": ("the cell replicates while the population sign "
                    "currency does not — unregistered-as-expected corner"),
}[q1]
print("READING:", READING)

OUT = {
    "prereg": "l226/PREREG.md",
    "premise": ("FIRST genuinely OUT-OF-SAMPLE test in this family. B36 and "
                "B37 were both inside the post-hoc leg that discovered the "
                "currency (Kriegeskorte 2009); B38 did not exist when the "
                "PREREG was frozen. The decision rule is L214's, re-executed "
                "as a verbatim source slice, never re-implemented."),
    "head_sha": HEAD_SHA, "slice2_sha": SLICE2_SHA,
    "frozen_rule": {"N_PERM": N_PERM, "PERM_SEED": PERM_SEED,
                    "ALPHA": ALPHA, "QFDR": QFDR, "n_W": int(W.sum()),
                    "signs_shape": list(SIGNS.shape),
                    "arms": ARMS5, "pairs": PAIRS2},
    "cert": {"cert_flo": nflo, "cert_rho": nrho, "cert_bh": nbh,
             "cert_sgn": 3, "cert_q1": 6,
             "cert_subset_checks": AN38["cert_subset_checks"],
             "cert_subset_max": AN38["fc169b2_max"]},
    "batch": {"B38": B38, "gains": {k: AN38[f"g_{k}"] for k in ARMS5},
              "f4_gain_exact": AN38["f4_gain_exact"],
              "paf4_ok": AN38["paf4_ok"]},
    "q1": {"actor": "Tr|f4ng", "tail": "up", "rho": CUR38[ACTOR]["rho"],
           "p_up": p_up38, "p_dn": CUR38[ACTOR]["p_dn"],
           "p_up_rank_of_10": rank_actor,
           "SA38": int(SA38), "SA_bar": SA_BAR,
           "SA_bar_exact_binomial_p": binom_p,
           "cell_ok": bool(cell_ok), "currency_ok": bool(cur_ok),
           "branch": q1, "reading": READING},
    "q2": {"m": 20, "q": QFDR, "n_survivors": k38, "survivors": surv38,
           "smallest_p": sp38, "smallest": sn38},
    "q3": {"C3": C3, "cells": C3_cells, "p_C3": p_C3,
           "C3_null_mean": float(C3_null.mean()),
           "C3_null_max": int(C3_null.max()),
           "note": ("EXTENSION of L214's Q1 null to a third batch: a second "
                    "permutation from the same PAIR_SEED stream. The first "
                    "permutation is bit-identical to L214's (CERT-Q1).")},
    "q4": {k: {m: v[m] for m in ("rho", "p_up", "p_dn", "mean_A", "mean_dS",
                                 "floL", "floR", "null_sd")}
           for k, v in CUR38.items()},
    "prior_observed": {"B36_p_up_actor": CUR["B36|Tr|f4ng"]["p_up"],
                       "B37_p_up_actor": CUR["B37|Tr|f4ng"]["p_up"],
                       "SA36": int(sa36), "SA37": int(sa37),
                       "L214_p_C": _w1["p_C"],
                       "L214_branch": _w1["branch"]},
    "predictions": P,
    "limitations": [
        "The out-of-sample test is on ONE pre-named cell and ONE population "
        "sign bar, both fixed by the card before B38 existed; no multiplicity "
        "correction is needed for the PRIMARY, and none is claimed for the "
        "Q2/Q3 companions beyond their own stated procedures.",
        "The 7/10 sign bar is a replication threshold, not an alpha-.05 "
        "test: its exact one-sided binomial p is " + f"{binom_p:.4f}" + ".",
        "B38 shares the substrate, the drive, the window and the gains with "
        "B36/B37 — it is a fresh SEED batch, not a fresh specimen or a "
        "fresh protocol. It tests seed-level generalisation only.",
        "Q3's third-batch null is a declared EXTENSION of L214's machinery, "
        "not a registered instrument with its own prior validation.",
    ],
}

for k, v in PATHS.items():
    st = os.stat(v)
    assert (st.st_size, st.st_mtime_ns) == FP0[k], ("npz MUTATED", v)
for k, v in PRIOR.items():
    st = os.stat(v)
    assert (st.st_size, st.st_mtime_ns) == FPP[k], ("prior json MUTATED", v)
assert (os.stat(P38).st_size, os.stat(P38).st_mtime_ns) == FP38, \
    "l226 npz MUTATED"
assert (os.stat("l214/static.json").st_size,
        os.stat("l214/static.json").st_mtime_ns) == FP214, "l214 json MUTATED"
print("\nall npz + prior-json fingerprints unchanged (incl. l226 raw)")

with open("l226/static.json", "w") as fh:
    json.dump(OUT, fh, indent=1)
print("wrote l226/static.json")
