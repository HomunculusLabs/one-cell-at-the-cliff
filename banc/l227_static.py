#!/usr/bin/env python3
"""L227_static.py — the MIRROR COEFFICIENT as a required pre-step.

PREREG: l227/PREREG.md (+ AMENDMENT 1, both written before this file).
Static: zero rollouts, zero GPU, CPU only. Inputs are stored jsons only,
opened READ-ONLY. No lab module is imported (L175). Exactly ONE write:
l227/static.json.
"""
import json, os, sys, hashlib
import numpy as np

B = "/home/t3rpz/critters/peabrain-lab/banc/"
OUTP = B + "l227/static.json"
EPS = np.finfo(np.float64).eps

# ---- registered constants (PREREG, before any number was read) ----
N_CELLS, N_SEEDS = 20, 16
LAM_GRID = [round(0.1 * i, 2) for i in range(11)]
N_SIM, N_PERM_SIM = 400, 2000
CAL_SEED, SIM_SEED, PERM_SEED = 22702, 22701, 22703
BETA_TARGET = 0.32926470588235296      # L214 measured mean_absrhoA (DESCRIPTION)
BETA_TOL = 0.005
BETA_FIXED2 = 0.50
# L214's own registered null, reproduced
HH_SEED, N_PERM_214 = 77041, 20000

OUT = {"prereg": "l227/PREREG.md",
       "premise": ("Three of the card's four currency pairs are settled "
                   "structurally before any simulation: lvl/margin is an "
                   "exact sign-flip identity, flo/fhi is degenerate by data "
                   "(fhi == 0 on all 20 cells), duty/S-mean is a quantity "
                   "and its own mean. Each INSTRUMENT has its own mirror "
                   "coefficient (MAG <- r_rho, SGN <- r_cur); the card "
                   "quoted SGN's for MAG. Branches ride only on simulated "
                   "power curves and on the aggregation branch."),
       "cert": {}, "pairs": {}, "sim": {}, "rule": {},
       "branch": {}, "predictions": {}, "limitations": []}

# ================= read-only inputs + fingerprints =================
SRC = ["l214/static.json", "l214/addendum.json", "l208/static.json",
       "l200/results_l200.json", "l202/results_l202.json"]
FP = {}
for s in SRC:
    st = os.stat(B + s)
    FP[s] = (st.st_size, st.st_mtime_ns)
l214 = json.load(open(B + "l214/static.json"))
add = json.load(open(B + "l214/addendum.json"))
l208 = json.load(open(B + "l208/static.json"))
l200 = json.load(open(B + "l200/results_l200.json"))
l202 = json.load(open(B + "l202/results_l202.json"))

PAIRS2, ARMS5 = ("Ti", "Tr"), ("f4wA", "f4ng", "f4tw", "cutwA", "cutng25")
KEYS20 = [f"{bk}|{pk}|{arm}" for bk in ("B36", "B37")
          for pk in PAIRS2 for arm in ARMS5]
assert len(KEYS20) == 20
assert list(l214["cells"].keys()) == KEYS20, "cell order drift"

# ================= rank machinery (L221: AVERAGE ranks) =================
def midrank(a):
    """Average (midrank) ranks along the last axis. rank_i = #(<x) + (#(==x)+1)/2."""
    a = np.asarray(a, dtype=np.float64)
    lt = (a[..., None, :] < a[..., :, None]).sum(-1)
    eq = (a[..., None, :] == a[..., :, None]).sum(-1)
    return lt + (eq + 1.0) / 2.0


def midrank_ref(v):
    """Reference per-row midrank via np.unique — the slow, obviously-correct one."""
    v = np.asarray(v, dtype=np.float64)
    out = np.empty(v.shape[-1], dtype=np.float64)
    order = np.argsort(v, kind="stable")
    i = 0
    while i < v.shape[-1]:
        j = i
        while j + 1 < v.shape[-1] and v[order[j + 1]] == v[order[i]]:
            j += 1
        r = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            out[order[k]] = r
        i = j + 1
    return out


def ordrank(a):
    """The STORED convention in l214_addendum.py: argsort-of-argsort (ordinal)."""
    return np.argsort(np.argsort(np.asarray(a))).astype(np.float64)


def _corr(rx, ry):
    rx = rx - rx.mean(-1, keepdims=True)
    ry = ry - ry.mean(-1, keepdims=True)
    return (rx * ry).sum(-1) / np.sqrt((rx * rx).sum(-1) * (ry * ry).sum(-1))


def spear_mid(x, y):
    return _corr(midrank(x), midrank(y))


def spear_ord(x, y):
    return _corr(ordrank(x), ordrank(y))


# ---- CERT-RANK: the fast kernel == the reference, and the tie structure ----
_nr = 0
_rng0 = np.random.default_rng(999)
probe = [np.array([1.0, 2.0, 2.0, 3.0]), np.array([5.0, 5.0, 5.0, 5.0]),
         _rng0.normal(size=16), _rng0.integers(0, 3, size=16).astype(float),
         _rng0.integers(0, 2, size=20).astype(float)]
for p in probe:
    assert np.array_equal(midrank(p), midrank_ref(p)), "CERT-RANK kernel mismatch"
    _nr += 1
    assert abs(midrank(p).sum() - len(p) * (len(p) + 1) / 2.0) < 1e-9
    _nr += 1
_blk = _rng0.normal(size=(7, 20, 16))
for i in range(7):
    for c in range(20):
        assert np.array_equal(midrank(_blk)[i, c], midrank_ref(_blk[i, c]))
_nr += 1
OUT["cert"]["cert_rank"] = _nr

# ================= CERT-214: L214's Q3 reproduced from stored jsons =================
_n214 = 0


def _eq(a, b, what):
    global _n214
    assert a == b, f"CERT-214 {what}: {a!r} != {b!r}"
    _n214 += 1


rhoA = np.array([l214["cells"][k]["rho"] for k in KEYS20])
rhoM = np.array([l208["arms"][k]["rho"] for k in KEYS20])
mA = np.array([l214["cells"][k]["mean_A"] for k in KEYS20])
mM = np.array([l208["arms"][k]["mean_dM"] for k in KEYS20])
mS = np.array([l214["cells"][k]["mean_dS"] for k in KEYS20])
for k in KEYS20:                        # the dominance column must be the SAME object
    _eq(l214["cells"][k]["mean_dS"], l208["arms"][k]["mean_dS"], f"mean_dS {k}")

_eq(float(np.abs(rhoA).mean()), l214["q3"]["mean_absrhoA"], "mean_absrhoA")
_eq(float(np.abs(rhoM).mean()), l214["q3"]["mean_absrhoM"], "mean_absrhoM")
diff = np.abs(rhoA) - np.abs(rhoM)      # 0j: the PAIRED form is the code that ran
D214 = float(diff.mean())
_eq(D214, l214["q3"]["D"], "D (paired difference vector)")
d_of_means = float(np.abs(rhoA).mean()) - float(np.abs(rhoM).mean())
OUT["cert"]["expr_form_residual_D"] = d_of_means - l214["q3"]["D"]   # reported, not asserted
hrng = np.random.default_rng(HH_SEED)
HS214 = hrng.choice([-1.0, 1.0], size=(N_PERM_214, 20))
Dn214 = (HS214 * diff).mean(axis=1)
_eq(float((np.abs(Dn214) >= abs(D214)).mean()), l214["q3"]["p_D"], "p_D")
_eq(int(sum((l214["cells"][k]["mean_A"] > 0) == (l214["cells"][k]["mean_dS"] > 0)
            for k in KEYS20)), l214["q3"]["sign_agree_floor"], "sign_agree_floor")
_eq(int(sum((l208["arms"][k]["mean_dM"] > 0) == (l208["arms"][k]["mean_dS"] > 0)
            for k in KEYS20)), l214["q3"]["sign_agree_ceiling"], "sign_agree_ceiling")
_eq(l214["q3"]["branch"], "H_TIE", "q3 branch")
# the addendum's mirror block, in the STORED (ordinal) convention
_eq(float(spear_ord(rhoA, rhoM)), add["mirror_test"]["spearman_rhoA_rhoM"], "r_rho ord")
_eq(float(spear_ord(mA, mM)), add["mirror_test"]["spearman_meanA_meandM"], "r_cur ord")
_eq(int(sum(1 for a, b in zip(rhoA, rhoM) if (a > 0) != (b > 0))),
    add["mirror_test"]["n_opposite_sign_rho"], "n_opp rho")
_eq(int(sum(1 for a, b in zip(mA, mM) if (a > 0) != (b > 0))),
    add["mirror_test"]["n_opposite_sign_currency"], "n_opp currency")
OUT["cert"]["cert_214"] = _n214

# ---- 0h: the tie group that makes the convention load-bearing ----
vals, cnts = np.unique(rhoM, return_counts=True)
ties = {float(v): int(c) for v, c in zip(vals, cnts) if c > 1}
assert len(ties) == 1 and list(ties.values()) == [2], "0h tie structure changed"
r_rho_mid, r_cur_mid = float(spear_mid(rhoA, rhoM)), float(spear_mid(mA, mM))
_eq(r_cur_mid, add["mirror_test"]["spearman_meanA_meandM"], "r_cur midrank == stored")
assert r_rho_mid != add["mirror_test"]["spearman_rhoA_rhoM"], "0h: no convention effect"

# ================= the four pairs =================
# --- P1: lvl vs margin — ANALYTIC IDENTITY, tolerance DERIVED from the data
mlv = max(max(abs(l208["arms"][k]["lvlL"]), abs(l208["arms"][k]["lvlR"]))
          for k in KEYS20)
TOL_ID = 4.0 * EPS * mlv                       # derived, never guessed (L216/L224)
idmax, id_exact = 0.0, 0
for k in KEYS20:
    a = l208["arms"][k]
    d = a["mean_dM"] - (-(a["lvlL"] - a["lvlR"]))
    idmax = max(idmax, abs(d))
    id_exact += int(d == 0.0)
assert idmax <= TOL_ID, f"identity {idmax} > derived tol {TOL_ID}"
OUT["pairs"]["lvl_vs_margin"] = dict(
    klass="C_ANALYTIC_MIRROR", mirror_r=-1.0, mirror_basis="proof: dM = -(lvlL-lvlR)",
    max_abs_resid=idmax, derived_tol=TOL_ID, n_float_exact=id_exact, n_cells=20,
    D_forced=0.0, note=("Spearman flips sign under a strictly decreasing transform, "
                        "so rho_M == -rho_A cellwise, |rho_M| == |rho_A| cellwise, "
                        "and D is identically zero: the magnitude head-to-head has "
                        "EXACTLY ZERO power on this pair by proof."))

# --- P2: flo vs fhi — DEGENERATE BY DATA
_nz = 0
for k in KEYS20:
    for f in ("fhi95L", "fhi95R", "fhi90L", "fhi90R"):
        assert l208["arms"][k][f] == 0.0, f"fhi nonzero {k} {f}"
        _nz += 1
OUT["pairs"]["flo_vs_fhi"] = dict(
    klass="C_DEGENERATE", mirror_r=None, n_zero_checks=_nz,
    note=("fhi95/fhi90 are identically 0.0 on all 20 cells (80 checks): a Spearman "
          "against a constant is undefined. At this sparse relu operating point the "
          "ceiling-side currency never fires, so no head-to-head exists."))

# --- P3: A vs dM — the one genuine pair
fsg_rho = int(sum(1 for a, b in zip(rhoA, rhoM) if (a > 0) != (b > 0)))
fsg_cur = int(sum(1 for a, b in zip(mA, mM) if (a > 0) != (b > 0)))
OUT["pairs"]["A_vs_dM"] = dict(
    klass="C_EMPIRICAL_NEAR_MIRROR",
    r_rho_midrank=r_rho_mid, r_rho_stored_ordinal=add["mirror_test"]["spearman_rhoA_rhoM"],
    r_cur_midrank=r_cur_mid, r_cur_stored_ordinal=add["mirror_test"]["spearman_meanA_meandM"],
    tie_group_in_rhoM=ties, frac_opposite_rho=fsg_rho / 20.0,
    frac_opposite_currency=fsg_cur / 20.0,
    mag_consumes="r_rho", sgn_consumes="r_cur",
    note=("The card quotes -0.856 (the CURRENCY-level mirror, which is SGN's "
          "coefficient) to justify a claim about MAG, whose coefficient is the "
          "rho-level one. Both are reported; the stored rho-level value is "
          "argsort-of-argsort with one tie group in rho_M and the midrank repair "
          "moves it by %.4f." % (r_rho_mid - add["mirror_test"]["spearman_rhoA_rhoM"])))

# --- P4: duty vs S-mean — a quantity and its own mean (AGGREGATION branch)
agg = []
for src, dd in (("l200", l200), ("l202", l202)):
    for arm, v in dd["arms"].items():
        for side in ("L", "R"):
            dl = v.get("duty" + side)
            mv = v.get("mean" + side)
            if dl is None or mv is None:
                continue
            agg.append((src, arm, side, float(np.mean(np.array(dl, dtype=float))),
                        float(mv), len(dl)))
assert len(agg) >= 50, f"aggregation units {len(agg)}"
d_exact = sum(1 for a in agg if a[3] == a[4])
d_max = max(abs(a[3] - a[4]) for a in agg)
if d_exact == len(agg):
    abr = "A_IDENTITY"
elif d_max <= 5e-4:
    abr = "A_ROUNDED"
else:
    abr = "A_DIFFERENT"
r_duty = float(spear_mid(np.array([a[3] for a in agg]), np.array([a[4] for a in agg])))
OUT["pairs"]["duty_vs_Smean"] = dict(
    klass="C_NOT_APPLICABLE", agg_branch=abr, n_units=len(agg),
    n_float_exact=d_exact, max_abs_resid=d_max, mirror_r=r_duty,
    note=("mean<side> is the mean of the per-seed duty<side> list, so this is one "
          "quantity at two granularities, not two candidate currencies; and "
          "l200/l202 store per-arm scalars with no shared within-cell regression, "
          "so the magnitude instrument does not exist there. Serves as the "
          "NOT-A-MIRROR positive control: its coefficient is positive."))
OUT["cert"]["cert_agg"] = len(agg)

# ================= the simulation =================
def sim_block(lam, beta, n_sim, seed):
    """Return (rho_A, rho_M, mean_A, mean_M, mean_t) per sim x cell."""
    rng = np.random.default_rng(seed)
    sh = (n_sim, N_CELLS, N_SEEDS)
    t = rng.normal(size=sh)
    e = rng.normal(size=sh)
    f = rng.normal(size=sh)
    A = beta * t + np.sqrt(max(0.0, 1.0 - beta * beta)) * e
    M = -(lam * A) + np.sqrt(max(0.0, 1.0 - lam * lam)) * f
    rt, ra, rm = midrank(t), midrank(A), midrank(M)
    return (_corr(ra, rt), _corr(rm, rt),
            A.mean(-1), M.mean(-1), t.mean(-1))


def binom_two_tailed(k, n):
    """Exact two-tailed binomial p against p=0.5 (integer arithmetic)."""
    from math import comb
    tot = 2 ** n
    pk = comb(n, k)
    s = sum(comb(n, i) for i in range(n + 1) if comb(n, i) <= pk)
    return s / tot


BT = {k: binom_two_tailed(k, N_CELLS) for k in range(N_CELLS + 1)}
PRNG = np.random.default_rng(PERM_SEED)
HSS = PRNG.choice([-1.0, 1.0], size=(N_PERM_SIM, N_CELLS))


def score(lam, beta, seed):
    ra, rm, ma, mm, mt = sim_block(lam, beta, N_SIM, seed)
    dv = np.abs(ra) - np.abs(rm)                       # (n_sim, 20)
    Dv = dv.mean(axis=1)
    Dn = dv @ HSS.T / N_CELLS                          # (n_sim, N_PERM)
    pD = (np.abs(Dn) >= np.abs(Dv)[:, None]).mean(axis=1)
    mag = float(((pD <= 0.05) & (Dv > 0)).mean())
    kA = ((ma > 0) == (mt > 0)).sum(axis=1)            # L214's granularity (0i)
    kM = ((mm > 0) == (mt > 0)).sum(axis=1)
    pA = np.array([BT[int(k)] for k in kA])
    pM = np.array([BT[int(k)] for k in kM])
    sgn = float((((pA <= 0.05) & (kA > N_CELLS / 2)) &
                 ((pM <= 0.05) & (kM < N_CELLS / 2))).mean())
    rr = float(np.mean([spear_mid(ra[i], rm[i]) for i in range(N_SIM)]))
    rc = float(np.mean([spear_mid(ma[i], mm[i]) for i in range(N_SIM)]))
    return dict(lam=lam, power_mag=mag, power_sgn=sgn, r_rho=rr, r_cur=rc,
                mean_absrhoA=float(np.abs(ra).mean()),
                mean_D=float(Dv.mean()), max_abs_dv=float(np.abs(dv).max()),
                frac_pD_one=float((pD == 1.0).mean()))


# ---- beta calibration (nuisance, against an OBSERVED target => description) ----
lo, hi, beta = 0.0, 1.0, 0.5
for _ in range(40):
    beta = 0.5 * (lo + hi)
    ra, _, _, _, _ = sim_block(0.0, beta, 200, CAL_SEED)
    if float(np.abs(ra).mean()) < BETA_TARGET:
        lo = beta
    else:
        hi = beta
ra, _, _, _, _ = sim_block(0.0, beta, 200, CAL_SEED)
cal_hit = float(np.abs(ra).mean())
if abs(cal_hit - BETA_TARGET) > BETA_TOL:              # registered escape, SHORT-CIRCUITS
    OUT["branch"] = {"verdict": "M_DEGENERATE",
                     "reason": f"beta calibration missed: {cal_hit} vs {BETA_TARGET}"}
    json.dump(OUT, open(OUTP, "w"), indent=1)
    print("M_DEGENERATE: calibration")
    sys.exit(0)
OUT["sim"]["beta_calibrated"] = beta
OUT["sim"]["beta_cal_mean_absrhoA"] = cal_hit
OUT["sim"]["beta_target"] = BETA_TARGET

rows = {}
for arm_name, bval in (("cal", beta), ("fixed50", BETA_FIXED2)):
    rr = [score(l, bval, SIM_SEED + 101 * i) for i, l in enumerate(LAM_GRID)]
    rows[arm_name] = rr
OUT["sim"]["grid"] = rows

# ---- CERT-SIM: the lam == 1 analytic degeneracy, measured ----
top = rows["cal"][-1]
assert top["lam"] == 1.0
assert top["max_abs_dv"] == 0.0, f"lam=1 diff not identically zero: {top['max_abs_dv']}"
assert top["frac_pD_one"] == 1.0, "lam=1 p_D not 1.0 in every sim"
assert top["power_mag"] == 0.0, f"lam=1 MAG power {top['power_mag']} != 0"
OUT["cert"]["cert_sim"] = 4

# ---- crossing + refinement ----
cal = rows["cal"]
cross_i = next((i for i, r in enumerate(cal) if r["power_mag"] < r["power_sgn"]), None)
ref = []
if cross_i is not None and cross_i > 0:
    a, b = cal[cross_i - 1]["lam"], cal[cross_i]["lam"]
    sub = [round(a + 0.01 * j, 3) for j in range(1, int(round((b - a) / 0.01)))]
    ref = [score(l, beta, SIM_SEED + 7717 + 11 * j) for j, l in enumerate(sub)]
    OUT["sim"]["refine"] = ref
    fine = [cal[cross_i - 1]] + ref + [cal[cross_i]]
    xi = next(i for i, r in enumerate(fine) if r["power_mag"] < r["power_sgn"])
    Xrow = fine[xi]
else:
    Xrow = cal[cross_i] if cross_i is not None else None

mono_tol = 0.08
pm = [r["power_mag"] for r in cal]
nonmono = max((pm[i + 1] - pm[i]) for i in range(len(pm) - 1))
OUT["sim"]["mag_power_max_increase"] = nonmono

if Xrow is None:
    br = "M_MAG_DOMINATES"
elif cross_i == 0:
    br = "M_SGN_DOMINATES"
elif nonmono > mono_tol:
    br = "M_DEGENERATE"
elif -1.0 < Xrow["r_rho"] < 0.0:
    br = "M_CROSSES"
else:
    br = "M_DEGENERATE"

OUT["branch"] = {"verdict": br, "crossing_grid_index": cross_i}
if br == "M_CROSSES":
    X_rho, X_cur = abs(Xrow["r_rho"]), abs(Xrow["r_cur"])
    p50 = next((r for r in cal if r["power_mag"] < 0.50), None)
    OUT["rule"] = {
        "X_lam": Xrow["lam"], "X_abs_r_rho": X_rho, "X_abs_r_cur": X_cur,
        "power_mag_at_X": Xrow["power_mag"], "power_sgn_at_X": Xrow["power_sgn"],
        "X50_lam": (p50["lam"] if p50 else None),
        "X50_abs_r_rho": (abs(p50["r_rho"]) if p50 else None),
        "measured_pair_abs_r_rho": abs(r_rho_mid),
        "measured_pair_abs_r_cur": abs(r_cur_mid),
        "retro_flags_L214_Q3": bool(abs(r_rho_mid) >= X_rho),
        "one_line": ("PRE-STEP: before registering a MAGNITUDE head-to-head "
                     "between two candidate currencies, compute the mirror "
                     "coefficient in the currency the instrument consumes "
                     "(per-cell correlations for a mean-|rho| statistic, "
                     "per-cell currency means for a sign-agreement statistic). "
                     "If |mirror r| >= %.2f, register the SIGN comparison as "
                     "the primary; the magnitude test has less power than the "
                     "sign test there and exactly zero power at |r| = 1."
                     % X_rho)}

OUT["predictions"] = {
    "P1_M_CROSSES": br == "M_CROSSES",
    "P2_mag_power_zero_at_lam1": cal[-1]["power_mag"] == 0.0,
    "P3_threshold_le_0.6767": (br == "M_CROSSES" and
                               OUT["rule"]["X_abs_r_rho"] <= 0.6767),
    "P4prime_A_ROUNDED": abr == "A_ROUNDED",
    "P5_mag_beats_sgn_at_lam0": cal[0]["power_mag"] > cal[0]["power_sgn"],
}
OUT["limitations"] = [
    "The simulation's generative model is Gaussian with a linear mirror; real "
    "currencies may be mirrors through a nonlinear monotone map, which leaves "
    "the ANALYTIC arm (rho_M == -rho_A exactly) untouched but changes the "
    "induced coefficient at intermediate lam.",
    "The within-cell mirror strength of the real A/dM pair is not recoverable "
    "from the stored jsons (per-seed values live in the npz), so the measured "
    "pair is placed on the grid through the INDUCED across-cell coefficient.",
    "N_PERM_SIM = 2000 (vs L214's 20000): p resolution 1/2001, adequate at "
    "alpha .05 and registered in advance with its cost reason.",
    "beta is calibrated against an OBSERVED value (L214's mean_absrhoA), so it "
    "is a nuisance parameter and description; the branch rides on curve SHAPE.",
    "SGN's success criterion requires BOTH currencies' binomial tests to be "
    "significant in opposite directions, which is a strict reading; a looser "
    "one would only move the crossing further toward low |r|.",
]

# ================= no artifact moved =================
for s in SRC:
    st = os.stat(B + s)
    assert FP[s] == (st.st_size, st.st_mtime_ns), f"input moved: {s}"
OUT["cert"]["inputs_unmoved"] = len(SRC)
OUT["self_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:16]

json.dump(OUT, open(OUTP, "w"), indent=1)
print("=" * 70)
print("BRANCH", br, "| predictions",
      sum(1 for v in OUT["predictions"].values() if v), "of",
      len(OUT["predictions"]), OUT["predictions"])
print("pairs:", {k: v["klass"] for k, v in OUT["pairs"].items()})
print("agg branch", abr, "exact", d_exact, "/", len(agg), "max resid", d_max,
      "mirror", round(r_duty, 4))
print("r_rho mid", r_rho_mid, "stored ord", add["mirror_test"]["spearman_rhoA_rhoM"],
      "| r_cur", r_cur_mid)
print("identity maxresid", idmax, "<= derived tol", TOL_ID, "| float-exact",
      id_exact, "/20")
for r in cal:
    print(f"  lam {r['lam']:.2f} r_rho {r['r_rho']:+.4f} r_cur {r['r_cur']:+.4f} "
          f"MAG {r['power_mag']:.3f} SGN {r['power_sgn']:.3f} "
          f"meanD {r['mean_D']:+.4f}")
if ref:
    print(" refine:")
    for r in ref:
        print(f"  lam {r['lam']:.3f} r_rho {r['r_rho']:+.4f} MAG {r['power_mag']:.3f} "
              f"SGN {r['power_sgn']:.3f}")
print("fixed50 arm:", [(r["lam"], round(r["power_mag"], 3), round(r["power_sgn"], 3))
                       for r in rows["fixed50"]])
if br == "M_CROSSES":
    print("RULE:", OUT["rule"]["one_line"])
    print("retro-flags L214 Q3:", OUT["rule"]["retro_flags_L214_Q3"],
          "| X50", OUT["rule"]["X50_lam"], OUT["rule"]["X50_abs_r_rho"])
print("certs", OUT["cert"])
print("L227 DONE")
