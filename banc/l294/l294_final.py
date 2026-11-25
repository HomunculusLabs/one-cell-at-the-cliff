#!/usr/bin/env python3
"""L294 -- WHAT PREDICTS A WEIGHT-MATCHED SET'S EFFECT. Static re-analysis of the STORED L290 +
L291 arrays. PREREG-first (banc/l294/PREREG.md, sha256 in PREREG.sha256), zero rollouts.
Read-only on every prior dir. Gates G1-G5 run BEFORE any test is computed or printed; a failed
gate halts with nothing written. Every number is printed only after the whole computation ends."""
import hashlib
import itertools
import json
import math
import os
import sys

import numpy as np

B = os.path.expanduser("~/critters/peabrain-lab/banc")
D = os.path.join(B, "l294")
J = lambda p: json.load(open(os.path.join(B, p)))
G_BASE = 0.14365819573402408
B_PERM = 20000
SEED = 29400
Q_BH = 0.10


def halt(where, msg):
    print("HALT %s: %s" % (where, msg))
    sys.exit(2)


# ------------------------------------------------------------------ populations
L291_15 = ["s11f1", "s11f2", "s11w1", "s11w2", "s11w3", "s30f1", "s30f2", "s30w1", "s30w2",
           "s30w3", "s46f1", "s46f2", "s46w1", "s46w2", "s46w3"]
FIXED291 = ["gc30f", "gh46f"]
L290_18 = ["r11k1", "r11k2", "r11k3", "r11k4", "r11k5", "r30k1", "r30k2", "r30k3", "r30k4",
           "r30k5", "r46k1", "r46k2", "r46k3", "r46k4", "r46k5", "rw11", "rw30", "rw46"]
B33 = L291_15 + L290_18
CARD35 = B33 + FIXED291
TW7 = [("gc30", "gc30f", "l290", "l291"), ("gh46", "gh46f", "l290", "l291"),
       ("e14", "e14f", "l290", "l290"), ("e25", "e25f", "l290", "l290"),
       ("e67", "e67f", "l290", "l290"), ("e12", "e12f", "l290", "l290"),
       ("e27", "e27f", "l290", "l290")]
W291 = {"w0": ["cutwA", "s11w1", "s11w2", "s11w3", "s11f1", "s11f2", "s30w1", "s30w2", "s30w3",
               "gc30f"],
        "w1": ["cutwA", "s30f1", "s30f2", "s46w1", "s46w2", "s46w3", "s46f1", "s46f2", "gh46f"]}
W290 = {"w0": ["cutwA", "gc30", "gh46", "rw11", "rw30", "rw46", "e14f", "e25f", "e67f"],
        "w1": ["cutwA", "r11k1", "r11k2", "r11k3", "r11k4", "r11k5", "r30k1", "r30k2", "e12f"],
        "w2": ["cutwA", "r30k3", "r30k4", "r30k5", "r46k1", "r46k2", "r46k3", "r46k4", "r46k5",
               "e27f"]}
WORKERS = {"l291": W291, "l290": W290}
import re
SIZE = {}
for a in L291_15 + L290_18:
    SIZE[a] = int(re.search(r"\d+", a).group())
SIZE.update({"gc30f": 30, "gh46f": 46})

# ------------------------------------------------------------------ G5 PREREG
sha_rec = open(os.path.join(D, "PREREG.sha256")).read().split()[0]
sha_now = hashlib.sha256(open(os.path.join(D, "PREREG.md"), "rb").read()).hexdigest()
if sha_rec != sha_now:
    halt("G5", "PREREG sha mismatch %s vs %s" % (sha_rec[:16], sha_now[:16]))

r291, r290 = J("l291/results_l291.json"), J("l290/results_l290.json")
RES = {"l291": r291, "l290": r290}
F = r291["F"]
if not (r291["F"] == r290["F"] == 0.00022931491480943385):
    halt("G1", "F mismatch %r %r" % (r291["F"], r290["F"]))
EPS = 2 * F
SEEDS = list(range(3769, 3785))
if list(r291["seeds"]) != SEEDS:
    halt("G1", "l291 seeds %r" % (r291["seeds"],))

# ------------------------------------------------------------------ G1 stored shapes
for tag, names in (("l291", L291_15 + FIXED291), ("l290", L290_18 + ["gc30", "gh46", "e14", "e25",
                                                                "e67", "e12", "e27"])):
    for a in names:
        rec = RES[tag]["arms"].get(a)
        if rec is None:
            halt("G1", "%s arms missing %s" % (tag, a))
        ps = rec.get("per_seed")
        if ps is None or len(ps) != 16:
            halt("G1", "%s/%s per_seed len %r" % (tag, a, None if ps is None else len(ps)))
        if abs(float(np.mean(ps)) - rec["E"]) > 1e-15:
            halt("G1", "%s/%s E != mean(per_seed)" % (tag, a))
        if abs(rec["E"] / F - rec["in_F"]) > 1e-9 * max(1.0, abs(rec["in_F"])):
            halt("G1", "%s/%s in_F != E/F" % (tag, a))

# ------------------------------------------------------------------ covariates (G3 provenance)
menu = J("l291/sets.json")["menu"]
if len(menu) != 69:
    halt("G3", "menu len %d" % len(menu))
NOOP = set(J("l291/sets.json")["noop"])
edges_rec = {}
for tag in ("l291", "l290"):
    for w, names in WORKERS[tag].items():
        ar = J("%s/arms_%s.json" % (tag, w))
        for a in names:
            if a == "cutwA":
                continue
            if a in edges_rec:
                halt("G3", "arm %s in two workers" % a)
            edges_rec[a] = ar["edges"][a]
COV = {}
for a in CARD35:
    e = edges_rec[a]
    rm = e["removed"]
    tg_rm = [x["target"] for x in rm]
    if sorted(tg_rm) != sorted(menu[j]["target"] for j in e["set"]):
        halt("G3", "%s set targets != removed targets" % a)
    syn = sum(menu[j]["syn"] for j in e["set"])
    syn_rm = sum(x["syn"] for x in rm)
    tag = "l291" if a in L291_15 + FIXED291 else "l290"
    if not (syn == syn_rm == RES[tag]["arms"][a]["syn_sum"]):
        halt("G3", "%s syn_sum %r %r %r" % (a, syn, syn_rm, RES[tag]["arms"][a]["syn_sum"]))
    ew = float(sum(math.log1p(menu[j]["syn"]) for j in e["set"]))
    ew_rm = float(sum(x["effective_weight"] for x in rm))
    if abs(ew - ew_rm) > 1e-5:
        halt("G3", "%s EW_SUM menu %r vs removed %r" % (a, ew, ew_rm))
    neff = sum(1 for j in e["set"] if j not in NOOP)
    if neff != e["eff"]:
        halt("G3", "%s eff %d vs stored %r" % (a, neff, e["eff"]))
    has14 = 14 in e["set"]
    if has14 != bool(RES[tag]["arms"][a]["has14"]):
        halt("G3", "%s has14 mismatch" % a)
    gain = RES[tag]["arms"][a]["gain"]
    COV[a] = dict(n=len(e["set"]), syn=syn, ew=ew, neff=neff, has14=has14, fixed=(a in FIXED291),
                  gain=gain, dgain=(0.0 if a in FIXED291 else gain - G_BASE),
                  ew_neg=0.0, ntgt=len(set(tg_rm)), ntgt_pool=0,
                  signs=sorted(set(x["sign"] for x in rm)))
    if a in L291_15 and COV[a]["dgain"] != r291["arms"][a]["dgain"]:
        halt("G3", "%s L291 dgain %r vs gain-g_base %r" % (a, r291["arms"][a]["dgain"], COV[a]["dgain"]))
    if COV[a]["ntgt"] != COV[a]["n"]:
        halt("G3", "%s ntgt != n" % a)

# ------------------------------------------------------------------ pools + npz (G2, G2b)
pools = J("l291/pools_w0.json")
pool_ids = sorted(set(itertools.chain.from_iterable(pools["pools"].values())))
if len(pool_ids) != 303:
    halt("G2", "pool union %d" % len(pool_ids))
pool_idx = np.array(pool_ids)
for a in CARD35:
    if any(menu[j]["target"] in set(pool_ids) for j in edges_rec[a]["set"]):
        halt("G3", "%s has a direct pool target" % a)
for a in CARD35:
    COV[a]["ntgt_pool"] = sum(1 for j in edges_rec[a]["set"] if menu[j]["target"] in set(pool_ids))

XM = {}      # (dir, worker) -> npz handle
RAW = {}
for tag in ("l291", "l290"):
    for w in WORKERS[tag]:
        XM[(tag, w)] = np.load(os.path.join(B, tag, "xm_%s.npz" % w), allow_pickle=False)
        RAW[(tag, w)] = np.load(os.path.join(B, tag, "raw_%s.npz" % w), allow_pickle=False)
NC = XM[("l291", "w0")]["xmean_cutwA_3769"].shape[0]
if NC != 21785 or max(pool_ids) >= NC:
    halt("G2", "n cells %d / max pool id %d" % (NC, max(pool_ids)))
mask = np.ones(NC, bool)
mask[pool_idx] = False
ctrl_idx = np.flatnonzero(mask)
if len(ctrl_idx) != NC - 303:
    halt("G2", "ctrl cells %d" % len(ctrl_idx))

for tag in ("l291", "l290"):
    for w, names in WORKERS[tag].items():
        arm = names[1]
        xk = XM[(tag, w)]
        tr = RAW[(tag, w)]["Ti_fL_%s_3769" % arm]
        xm = xk["xmean_%s_3769" % arm]
        a_mean = float(np.mean(tr))
        b_mean = float(np.mean(xm[np.array(pools["pools"]["Ti_fL"])]))
        if abs(a_mean - b_mean) > 1e-4 * max(abs(a_mean), abs(b_mean), 1e-12):
            halt("G2b", "%s/%s/%s pool trace mean %r vs xmean over pool %r" % (tag, w, arm, a_mean, b_mean))

# re-derive E, E_CTRL, E_DIFF per arm from xmean
ARMX = {}    # arm -> dict(E=..., Ectrl=..., Ediff=..., Elr=...)
NEED = set(CARD35) | {"gc30", "gh46"}
MAXDEV_E = 0.0
for tag in ("l291", "l290"):
    for w, names in WORKERS[tag].items():
        xk = XM[(tag, w)]
        base = np.stack([xk["xmean_cutwA_%d" % s] for s in SEEDS]).astype(np.float64)   # 16 x NC
        baseP = base[:, pool_idx].mean(axis=1)
        baseC = base[:, ctrl_idx].mean(axis=1)
        for a in names:
            if a not in NEED:
                continue
            X = np.stack([xk["xmean_%s_%d" % (a, s)] for s in SEEDS]).astype(np.float64)
            if not np.isfinite(X).all():
                halt("G2", "%s/%s non-finite xmean" % (tag, a))
            P = X[:, pool_idx].mean(axis=1)
            C = X[:, ctrl_idx].mean(axis=1)
            dP = P - baseP
            E = float(dP.mean())
            tagres = tag
            dev = abs(E - RES[tagres]["arms"][a]["E"])
            if dev > MAXDEV_E:
                MAXDEV_E = dev
            if dev > 2e-9:
                halt("G2", "%s E re-derived %r vs stored %r (dev %r)" % (a, E, RES[tagres]["arms"][a]["E"], dev))
            ps = np.array(RES[tagres]["arms"][a]["per_seed"])
            if np.max(np.abs(dP - ps)) > 2e-9:
                halt("G2", "%s per-seed re-derived max dev %r" % (a, float(np.max(np.abs(dP - ps)))))
            ARMX[a] = dict(E=E, Ef=E / F, Ectrl=float((C - baseC).mean()),
                           Ediff=float(((P - baseP) - (C - baseC)).mean()),
                           Elr=float((np.log(np.maximum(P, 1e-30)) - np.log(np.maximum(baseP, 1e-30))
                                      - np.log(np.maximum(C, 1e-30)) + np.log(np.maximum(baseC, 1e-30))).mean()),
                           baseP=float(baseP.mean()), baseC=float(baseC.mean()))
del XM, RAW

# ------------------------------------------------------------------ rank machinery
def midrank(x):
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[i:j + 1] = 0.5 * (i + j) + 1.0
        i = j + 1
    out = np.empty(len(x))
    out[order] = r
    return out


def pearson(a, b):
    a = a - a.mean()
    b = b - b.mean()
    den = math.sqrt(float(a @ a) * float(b @ b))
    return float(a @ b) / den if den > 0 else float("nan")


def spear(x, y):
    return pearson(midrank(x), midrank(y))


def ordinal(x):
    return np.argsort(np.argsort(np.asarray(x, dtype=float)), kind="mergesort").astype(float)


def strata_of(names):
    out = {}
    for n in sorted(set(SIZE[a] for a in names)):
        out[n] = [a for a in names if SIZE[a] == n]
    return out


def strat_rho(ys, xs, strata):
    rhos, ws, unread = {}, {}, []
    for n, names in strata.items():
        xv = [xs[a] for a in names]
        if len(names) < 3 or len(set(xv)) < 4:
            unread.append(n)
            continue
        rhos[n] = spear(xv, [ys[a] for a in names])
        ws[n] = len(names) - 1
    if len(rhos) < 2:
        return None, rhos, unread
    W = sum(ws.values())
    return sum(ws[n] * rhos[n] for n in rhos) / W, rhos, unread


def strat_perm(ys, xs, strata, what):
    obs, rhos, unread = strat_rho(ys, xs, strata)
    out = dict(stat=what, obs=None if obs is None else float(obs), per_stratum=rhos,
               unmeasurable_strata=[int(u) for u in unread], p_two=None, B=B_PERM, readable=False)
    if obs is None:
        out["status"] = "UNMEASURABLE"
        return out
    rng = np.random.default_rng(SEED)
    acc = np.zeros(B_PERM)
    W = 0
    for n, names in strata.items():
        if n not in rhos:
            continue
        Xv = np.array([xs[a] for a in names])
        Yv = np.array([ys[a] for a in names])
        rx = midrank(Xv)
        rx -= rx.mean()
        ry = midrank(Yv)
        ry -= ry.mean()
        den = math.sqrt(float(rx @ rx) * float(ry @ ry))
        if abs(float(rx @ ry) / den - rhos[n]) > 1e-12:
            halt("SELF", "per-stratum rho mismatch in %s" % what)
        Pi = np.stack([rng.permutation(len(names)) for _ in range(B_PERM)])
        rho_b = (rx[Pi] @ ry) / den
        acc += (len(names) - 1) * rho_b
        W += len(names) - 1
    null = acc / W
    out["p_two"] = float((1 + int(np.sum(np.abs(null) >= abs(obs) - 1e-12))) / (B_PERM + 1))
    out["readable"] = True
    out["status"] = "READ"
    return out


def bh(pvals, m):
    pv = [1.0 if (p is None or not np.isfinite(p)) else float(p) for p in pvals]
    order = np.argsort(pv)
    ranked = np.array(pv)[order] * m / np.arange(1, m + 1)
    qv = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.minimum(qv, 1.0)
    return out.tolist()


E_F = {a: ARMX[a]["Ef"] for a in ARMX}
EC_F = {a: ARMX[a]["Ectrl"] / F for a in ARMX}
ED_F = {a: ARMX[a]["Ediff"] / F for a in ARMX}
ELR = {a: ARMX[a]["Elr"] for a in ARMX}
DG = {a: COV[a]["dgain"] for a in COV}
EW = {a: COV[a]["ew"] for a in COV}
SY = {a: COV[a]["syn"] for a in COV}
NF = {a: COV[a]["neff"] for a in COV}
H14 = {a: 1.0 if COV[a]["has14"] else 0.0 for a in COV}
NT = {a: float(COV[a]["ntgt"]) for a in COV}
NTP = {a: float(COV[a]["ntgt_pool"]) for a in COV}
EWN = {a: 0.0 for a in COV}

# ------------------------------------------------------------------ G4 anchors
a1_ord = pearson(ordinal([E_F[a] for a in L291_15]), ordinal([DG[a] for a in L291_15]))
if abs(a1_ord - 0.82) > 0.005:
    halt("G4", "anchor 1 DGAIN x E ordinal L291-15 = %r" % a1_ord)
a2 = spear([E_F[a] for a in L290_18[:15]], [SY[a] for a in L290_18[:15]])
if abs(a2 - 0.5892857142857143) > 1e-12:
    halt("G4", "anchor 2 SYN x E L290-15 = %r" % a2)
a3 = spear([E_F[a] for a in L290_18[:15]], [NF[a] for a in L290_18[:15]])
if abs(a3 - 0.4286057678550518) > 1e-12:
    halt("G4", "anchor 3 eff x E L290-15 = %r" % a3)
a4 = {}
for n, mk in ((11, "abs"), (30, "crofts"), (46, "hop")):
    wv = [E_F[a] for a in L291_15 if SIZE[a] == n and H14[a] == 1]
    fv = [E_F[a] for a in L291_15 if SIZE[a] == n and H14[a] == 0]
    a4[n] = (float(np.mean(wv)), float(np.mean(fv)))
    if (abs(a4[n][0] - r291["means"]["strat_with_e14"][mk]) > 0.005
            or abs(a4[n][1] - r291["means"]["strat_free_e14"][mk]) > 0.005):
        halt("G4", "anchor cell means n=%d %r" % (n, a4[n]))

# everything below is computed only after every gate passed
S_B33 = strata_of(B33)
S_L18 = strata_of(L290_18)
S_C35 = strata_of(CARD35)
T = {}
T["T1"] = strat_perm(E_F, DG, S_L18, "STRAT-RHO(E, DGAIN) on L18")
T["T2"] = strat_perm(E_F, DG, S_B33, "STRAT-RHO(E, DGAIN) on B33")
T["T3"] = strat_perm(E_F, EW, S_B33, "STRAT-RHO(E, EW_SUM) on B33")
T["T5"] = strat_perm(EC_F, DG, S_B33, "STRAT-RHO(E_CTRL, DGAIN) on B33")
T["T6"] = strat_perm(ED_F, DG, S_B33, "STRAT-RHO(E_DIFF, DGAIN) on B33")
T["T2_card35"] = strat_perm(E_F, DG, S_C35, "STRAT-RHO(E, DGAIN) on CARD35 (companion)")

# T4 twin leg
tw = []
for b, f, db, df in TW7:
    Eb = RES[db]["arms"][b]["E"]
    Ef = RES[df]["arms"][f]["E"]
    gb = RES[db]["arms"][b]["gain"]
    row = RES["l290"]["twins"]["rows"].get(f) if f in RES["l290"]["twins"]["rows"] else RES["l291"]["twins"].get(f)
    if row is not None:
        if abs(row["E_fixed"] - Ef) > 1e-15 or abs(row["E_bisected"] - Eb) > 1e-15:
            halt("G4", "twin %s stored pair != arms records" % f)
        if "dgain" in row and abs(row["dgain"] - (gb - G_BASE)) > 1e-15:
            halt("G4", "twin %s stored dgain != gain - g_base" % f)
    if abs(RES[df]["arms"][f]["gain"] - G_BASE) > 0:
        halt("G4", "fixed twin %s not at base gain" % f)
    tw.append(dict(bisected=b, fixed=f, dgain=gb - G_BASE, dE_F=(Eb - Ef) / F))
dg = np.array([t["dgain"] for t in tw])
dE = np.array([t["dE_F"] for t in tw])
S_obs = float(np.mean(np.sign(dg) * dE))
pats = np.array(list(itertools.product([1.0, -1.0], repeat=7)))
S_null = pats @ (np.sign(dg) * dE) / 7.0
p_t4 = float(np.sum(S_null >= S_obs - 1e-12) / 128.0)
conc = int(np.sum(np.sign(dE) == np.sign(dg)))
rho_tw = spear(dg, dE)
perm7 = np.array(list(itertools.permutations(range(7))))
rhos_perm7 = np.array([pearson(midrank(dg[p]), midrank(dE)) for p in perm7])
p_tw_rho = float(np.sum(rhos_perm7 >= rho_tw - 1e-12) / 5040.0)
T["T4"] = dict(stat="TWIN S = mean sign(dgain)*dE over 7 pairs", obs=S_obs, p_one=p_t4,
               concordant=conc, rho_dgain_dE=float(rho_tw), p_rho_exact=p_tw_rho,
               pairs=tw, readable=True, status="READ")

# degenerate covariates (definition-first)
DEGEN = {
    "EW_NEG": dict(identically_zero=all(COV[a]["ew_neg"] == 0.0 for a in COV), n_negative_menu=sum(1 for m in menu if m["sign"] < 0 or m["effective_weight"] < 0)),
    "NTGT": dict(equals_n=all(COV[a]["ntgt"] == COV[a]["n"] for a in COV)),
    "NTGT_POOL": dict(identically_zero=all(COV[a]["ntgt_pool"] == 0 for a in COV)),
}
DEGEN["NTGT"]["strat"] = strat_perm(E_F, NT, S_B33, "STRAT-RHO(E, NTGT) on B33")
DEGEN["NTGT_POOL"]["strat"] = strat_perm(E_F, NTP, S_B33, "STRAT-RHO(E, NTGT_POOL) on B33")
DEGEN["EW_NEG"]["strat"] = strat_perm(E_F, EWN, S_B33, "STRAT-RHO(E, EW_NEG) on B33")

# BH over the family m = 6 (unmeasurable -> p = 1)
fam = ["T1", "T2", "T3", "T4", "T5", "T6"]
pv = [(T[k]["p_two"] if T[k]["readable"] else None) if k != "T4" else T["T4"]["p_one"] for k in fam]
qv = bh(pv, 6)
Q = {k: dict(p=pv[i], q=qv[i], readable=(T[k]["readable"] if k != "T4" else True), status=T[k]["status"]) for i, k in enumerate(fam)}

sig = lambda k: bool(Q[k]["readable"] and Q[k]["q"] <= Q_BH)
sgn = lambda k: float(np.sign(T[k]["obs"])) if T[k]["obs"] is not None else 0.0
twin_gain = bool(T["T4"]["obs"] > 0 and T["T4"]["p_one"] <= 0.05)
both = sig("T1") and sig("T2") and sgn("T1") > 0 and sgn("T2") > 0
if both and twin_gain:
    verdict = "A_GAIN_DELTA_MEDIATED"
    sub = "A_POOL_SPECIFIC" if sig("T6") else "A_COMMON"
elif both:
    verdict, sub = "B_GAIN_DELTA_MARKER", None
elif sig("T3") and sgn("T3") > 0 and not both:
    verdict, sub = "C_WEIGHT_CARRIES", None
elif not sig("T1") and not sig("T2") and not sig("T3"):
    verdict, sub = "D_LOTTERY", None
else:
    verdict, sub = "NO_DECISION", None
gshift = "G_SHIFT_ON" if sig("T5") else "G_SHIFT_OFF"

PRED = {
    "P1": bool(T["T1"]["readable"] and T["T1"]["obs"] > 0 and T["T1"]["p_two"] <= 0.05),
    "P2": bool(T["T2"]["readable"] and T["T2"]["obs"] > 0 and T["T2"]["p_two"] <= 0.05),
    "P3": bool(T["T4"]["obs"] > 0 and T["T4"]["p_one"] <= 0.05),
    "P4": sig("T5"),
    "P5": bool(not T["T3"]["readable"] or T["T3"]["p_two"] is None or T["T3"]["p_two"] > 0.05),
    "P6": True,
}

# descriptive companions
mirror = spear([EW[a] for a in B33], [SY[a] for a in B33])
desc = {
    "mirror_rho_EW_SYN_B33": float(mirror),
    "pooled_rho_E_DGAIN_L290_18": float(spear([E_F[a] for a in L290_18], [DG[a] for a in L290_18])),
    "pooled_rho_E_DGAIN_L291_15_midrank": float(spear([E_F[a] for a in L291_15], [DG[a] for a in L291_15])),
    "pooled_rho_E_DGAIN_L291_15_ordinal": float(a1_ord),
    "pooled_rho_E_SYN_L291_15_ordinal": float(pearson(ordinal([E_F[a] for a in L291_15]), ordinal([SY[a] for a in L291_15]))),
    "strat_rho_ELR_DGAIN_B33": strat_rho(ELR, DG, S_B33),
    "strat_rho_E_ECTRL_B33": strat_rho(E_F, EC_F, S_B33),
    "pooled_rho_ECTRL_DGAIN_B33": float(spear([EC_F[a] for a in B33], [DG[a] for a in B33])),
    "share_surviving": (None if (T["T2"]["obs"] in (None, 0)) or T["T6"]["obs"] is None
                        else float((T["T2"]["obs"] - T["T6"]["obs"]) / T["T2"]["obs"])),
    "floor_only": {},
    "neg_dgain_table": {},
    "e14_strat_B33": strat_rho(E_F, H14, S_B33),
    "neff_strat_B33": strat_rho(E_F, NF, S_B33),
}
for k, names, ss in (("T1", L290_18, S_L18), ("T2", B33, S_B33)):
    keep = [a for a in names if abs(E_F[a]) > 2.0]
    st = strata_of(keep)
    o, ps_, un_ = strat_rho(E_F, DG, st)
    desc["floor_only"][k] = dict(n=len(keep), obs=o, per_stratum=ps_, unmeasurable=un_,
                                 pooled=pearson(ordinal([E_F[a] for a in keep]), ordinal([DG[a] for a in keep])) if len(keep) > 3 else None)
desc["e14_two_group_F"] = {}
for n, names in S_B33.items():
    wv = [E_F[a] for a in names if H14[a] == 1]
    fv = [E_F[a] for a in names if H14[a] == 0]
    desc["e14_two_group_F"][int(n)] = {"with": float(np.mean(wv)) if wv else None,
                                      "without": float(np.mean(fv)) if fv else None,
                                      "n_with": len(wv), "n_without": len(fv)}
for pop, names in (("L291_15", L291_15), ("L290_18", L290_18)):
    neg = [a for a in names if DG[a] < 0]
    desc["neg_dgain_table"][pop] = dict(
        n_neg=len(neg), neg_at_floor=sum(1 for a in neg if abs(E_F[a]) <= 2.0),
        pos_at_floor=sum(1 for a in names if DG[a] > 0 and abs(E_F[a]) <= 2.0),
        n_pos=sum(1 for a in names if DG[a] > 0),
        neg_E_F=[round(E_F[a], 3) for a in neg])
for n, names in S_B33.items():
    desc.setdefault("per_stratum_Ectrl_mean_F", {})[int(n)] = float(np.mean([EC_F[a] for a in names]))
    desc.setdefault("per_stratum_E_mean_F", {})[int(n)] = float(np.mean([E_F[a] for a in names]))
    desc.setdefault("per_stratum_dgain_range", {})[int(n)] = [float(min(DG[a] for a in names)), float(max(DG[a] for a in names))]

arms_table = []
for a in CARD35:
    arms_table.append(dict(arm=a, size=SIZE[a], family=("L291" if a in r291["arms"] else "L290"),
                           fixed=COV[a]["fixed"], E_F=round(E_F[a], 4), Ectrl_F=round(EC_F[a], 4),
                           Ediff_F=round(ED_F[a], 4), dgain=float("%.6g" % DG[a]), ew=round(EW[a], 3),
                           syn=COV[a]["syn"], neff=COV[a]["neff"], has14=COV[a]["has14"]))

out = dict(
    card="L294", prereg_sha256=sha_now, tick=287, frozen="2026-11-25 13:10 EST",
    F=F, eps=EPS, g_base=G_BASE, B_PERM=B_PERM, seed=SEED, q_bh=Q_BH,
    populations=dict(B33=B33, L290_18=L290_18, CARD35=CARD35, strata_B33={str(k): v for k, v in S_B33.items()}),
    gates=dict(G1="pass", G2="pass (35 arms + 2, E and 16 per-seed values to 2e-9)",
               G2_max_abs_dev_E=float(MAXDEV_E), G2b="pass",
               G3="pass", G4=dict(anchor1_dgain_ordinal_L291_15=float(a1_ord), anchor2_syn_L290_15=float(a2),
                                  anchor3_eff_L290_15=float(a3),
                                  anchor4_6_cell_means={str(k): v for k, v in a4.items()}),
               G5="pass"),
    tests={k: {kk: vv for kk, vv in v.items() if kk != "pairs"} for k, v in T.items()},
    twin_pairs=tw, family_order=fam, qvals=Q, verdict=verdict, sub_label=sub, global_shift=gshift,
    predictions=PRED, score=int(sum(PRED.values())), degenerate=DEGEN, descriptive=desc,
    arms=arms_table,
    provenance=dict(results_l291_sha256=hashlib.sha256(open(os.path.join(B, "l291/results_l291.json"), "rb").read()).hexdigest(),
                    results_l290_sha256=hashlib.sha256(open(os.path.join(B, "l290/results_l290.json"), "rb").read()).hexdigest(),
                    sets_sha256=hashlib.sha256(open(os.path.join(B, "l291/sets.json"), "rb").read()).hexdigest()),
)
json.dump(out, open(os.path.join(D, "results_l294.json"), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))

# ------------------------------------------------------------------ print
print("L294 | PREREG sha %s | F %.6g | B %d | gates G1 G2 G2b G3 G4 G5 PASS" % (sha_now[:16], F, B_PERM))
print("ANCHORS: dgain x E ordinal L291-15 %+.4f | SYN x E L290-15 %+.10f | eff x E L290-15 %+.10f" % (a1_ord, a2, a3))
print("         cell means with/without (F): n11 %+.2f/%+.2f  n30 %+.2f/%+.2f  n46 %+.2f/%+.2f" % (
    a4[11][0], a4[11][1], a4[30][0], a4[30][1], a4[46][0], a4[46][1]))
print("\nFAMILY (BH q %.2f, m 6):" % Q_BH)
for k in fam:
    t = T[k]
    if k == "T4":
        print("  %s  S %+.4f F  p_one %.4f  concordant %d/7  rho(dgain,dE) %+.3f p_exact %.4f" % (
            k, t["obs"], t["p_one"], t["concordant"], t["rho_dgain_dE"], t["p_rho_exact"]))
    else:
        ps = " ".join("n%d:%+.3f" % (n, v) for n, v in t["per_stratum"].items())
        print("  %s  strat-rho %+.4f  p_two %.5f  q %.4f  [%s]%s" % (
            k, t["obs"], t["p_two"], Q[k]["q"], ps,
            ("  UNMEASURABLE strata %r" % t["unmeasurable_strata"]) if t["unmeasurable_strata"] else ""))
print("  T2 CARD35 companion: strat-rho %+.4f p_two %.5f" % (T["T2_card35"]["obs"], T["T2_card35"]["p_two"]))
print("\nVERDICT: %s%s | %s | predictions %s | score %d/6" % (
    verdict, (" / " + sub) if sub else "", gshift, json.dumps(PRED), out["score"]))
print("\nDEGENERATE (definition-first):")
for k, v in DEGEN.items():
    s = v["strat"]
    print("  %s: %s | strat test %s obs %s unmeasurable %r" % (
        k, {kk: vv for kk, vv in v.items() if kk != "strat"}, s["status"],
        None if s["obs"] is None else round(s["obs"], 4), s["unmeasurable_strata"]))
print("\nDESCRIPTIVE:")
for k, v in desc.items():
    if k in ("floor_only",):
        continue
    print("  %s: %s" % (k, v))
print("  floor_only: " + json.dumps(desc["floor_only"], default=str))
print("\nTWIN PAIRS (dgain x1e-3, dE F bisected - fixed):")
for t in tw:
    print("  %-5s/%-5s dgain %+.4f  dE %+6.3f F  %s" % (t["bisected"], t["fixed"], t["dgain"] * 1e3, t["dE_F"],
                                                         "concordant" if np.sign(t["dgain"]) == np.sign(t["dE_F"]) else "DISCORDANT"))
print("\nARMS (B33 + fixed):")
for r in arms_table:
    print("  %-6s n%2d %s%s E %+7.3f F  Ectrl %+7.3f F  Ediff %+7.3f F  dgain %+.4fe-3  EW %6.1f syn %3d eff %2d e14 %d" % (
        r["arm"], r["size"], r["family"], "*" if r["fixed"] else " ", r["E_F"], r["Ectrl_F"], r["Ediff_F"],
        r["dgain"] * 1e3, r["ew"], r["syn"], r["neff"], int(r["has14"])))
print("\nwrote results_l294.json")
