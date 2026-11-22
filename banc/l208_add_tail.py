# ============ L208 ADDENDUM TAIL — POST-HOC, UNREGISTERED ============
# The PREREG registered `flo` as a MEASURED statistic but did NOT register
# any test on it. Everything below is therefore labelled POST-HOC and
# carries NO registered claim; the registered version is handed to L214.
# Zero new rollouts; same read-only npz; same shared permutation draws.

RMAX = 1.0
BG = 0.02
SEG = 2000
ENT_AMP = 0.1
ARMS5 = ["f4wA", "f4ng", "f4tw", "cutwA", "cutng25"]
PAIRS2 = ["Ti", "Tr"]
B36 = list(range(3449, 3465))
B37 = list(range(3701, 3717))
PERM_SEED = 20837
N_PERM = 20000

AMPA = np.zeros(WIN, np.float64)
for _s0, _, _ in SEGB:
    _c = 0
    while _s0 + _c * 900 < _s0 + SEG:
        _lo = _s0 + _c * 900
        AMPA[_lo:min(_lo + 500, _s0 + SEG)] = ENT_AMP
        _c += 1
AMPA[2000:4000] = ENT_AMP
W = np.zeros(WIN, bool)
for _a0, _b0, _f in SEGB:
    if _f == 0.7:
        W[_a0 + MEAS0:_b0] = True
assert int(W.sum()) == 3000

PATHS = {"B36": "l169b2/raw_l169b2.npz", "B37": "l175f/raw_l175f.npz"}
FP0 = {k: (os.stat(v).st_size, os.stat(v).st_mtime_ns) for k, v in PATHS.items()}
RAW = {k: np.load(v) for k, v in PATHS.items()}
SEEDS = {"B36": B36, "B37": B37}

# ---- CERT-ADD re-run as a halting gate (same atom as l208_static.py)
res36 = json.load(open("l169b2/results_l169b2.json"))
add = res36["addendum_L_descriptive"]
nchk = 0
for arm, row in add["rows"].items():
    t = side_k(RAW["B36"], arm, B36, "Ti")
    for f in ("meanL", "kL", "meanR", "kR"):
        assert t[f] == row[f], ("CERT-ADD", arm, f)
        nchk += 1
    L, _R = duty_seeds(RAW["B36"], arm, B36, "Ti")
    assert list(L) == row["perseedL"], ("CERT-ADD perseedL", arm)
    nchk += len(L)
# ---- plus the stored L208 primary values, at FLOAT EQUALITY
prev = json.load(open("l208/static.json"))
assert prev["head_sha"] == HEAD_SHA, "head drift vs l208/static.json"
print(f"CERT-ADD: {nchk} values reproduced; head sha matches l208/static.json")


def flo_side(raw, arm, seed, pk, mask):
    ag, bg = PREF[pk]
    out = {}
    for side in ("L", "R"):
        v = np.concatenate([
            raw[f"{pk}_{ag}{side}_{arm}_{seed}"][:WIN][mask],
            raw[f"{pk}_{bg}{side}_{arm}_{seed}"][:WIN][mask]]).astype(np.float64)
        out[side] = float((v <= BG).mean())
    return out


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rx -= rx.mean()
    ry -= ry.mean()
    den = math.sqrt(float((rx * rx).sum()) * float((ry * ry).sum()))
    return float((rx * ry).sum() / den) if den > 0 else float("nan")


rng = np.random.default_rng(PERM_SEED)
SIGNS = rng.choice([-1.0, 1.0], size=(N_PERM, 16))

OUT = {"label": ("POST-HOC, UNREGISTERED. The L208 PREREG registered flo as "
                 "a measured statistic only; no branch depends on anything "
                 "below. Registered version = queue item L214."),
       "currency": ("A = floR - floL = how much LESS floor-pinned the LEFT "
                    "side is; dS = dutyL - dutyR. Positive rho = the LESS "
                    "floor-pinned side carries MORE antiphase duty."),
       "cells": {}, "sign_table": {}}
print("\nPOST-HOC floor leg (aliveness, not ceiling margin):")
for bk in ("B36", "B37"):
    raw, seeds = RAW[bk], SEEDS[bk]
    for pk in PAIRS2:
        for arm in ARMS5:
            dL, dR = duty_seeds(raw, arm, seeds, pk)
            rows = [flo_side(raw, arm, s, pk, W) for s in seeds]
            dS = np.array([float(dL[i] - dR[i]) for i in range(len(seeds))])
            A = np.array([r["R"] - r["L"] for r in rows])
            rho = spearman(dS, A)
            null = np.array([spearman(dS * SIGNS[j], A) for j in range(N_PERM)])
            key = f"{bk}|{pk}|{arm}"
            OUT["cells"][key] = dict(
                rho=rho, p_up=float((null >= rho).mean()),
                p_dn=float((null <= rho).mean()),
                mean_A=float(A.mean()), mean_dS=float(dS.mean()),
                sign_agree=bool((A.mean() > 0) == (dS.mean() > 0)))
            c = OUT["cells"][key]
            print(f"  {key:22s} rho {rho:+.3f} p_up {c['p_up']:.4f} "
                  f"p_dn {c['p_dn']:.4f} | mean_A {c['mean_A']:+.4f} "
                  f"mean_dS {c['mean_dS']:+.3f} | sign_agree {c['sign_agree']}")

for bk in ("B36", "B37"):
    ag = sum(OUT["cells"][f"{bk}|{pk}|{a}"]["sign_agree"]
             for pk in PAIRS2 for a in ARMS5)
    OUT["sign_table"][bk] = dict(agree=ag, total=10)
    print(f"sign agreement {bk}: {ag}/10 arm x pair cells "
          f"(less-floor-pinned side is the dominant side)")

for k, v in PATHS.items():
    st = os.stat(v)
    assert (st.st_size, st.st_mtime_ns) == FP0[k], ("npz MUTATED", v)
print("npz fingerprints unchanged")
with open("l208/addendum_floor.json", "w") as fh:
    json.dump(OUT, fh, indent=1)
print("wrote l208/addendum_floor.json")
