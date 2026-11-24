# ===== VERBATIM l212_head.py lines 1-26 (sha f211e030f283d7a2) =====
"""L212 HEAD — the FAFB v783 anatomical substrate, built from the RAW Zenodo
release (NOT from peabrain/brain_graph.pt: that graph is IN-DEGREE NORMALISED,
Wv /= max(indeg,1)[dst], which is not invertible — every row with indeg>=1 sums
to exactly 1, so the raw log1p mass cannot be recovered from it. PREREG amended
on this point BEFORE any L212 number was measured; the live graph is still used
as a PROVENANCE GATE).

Operator form is expression-identical to l151/l207's build_sub:
    ev = log1p(syn_pair) * sign_b,  sign_b = -|sign_a| if glutamate else sign_a
    jv = |ev| with ev<0 scaled by BETA_L
No in-degree normalisation, no synapse floor, no mask, no settle, no seed.
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd
import torch

T0 = time.time()
PB = "/home/t3rpz/critters/peabrain"
LAB = "/home/t3rpz/critters/peabrain-lab/banc"

# ===== L223 DECLARED MODIFICATION (replaces l212_head.py line 27) =====
# the parent wrote to {LAB}/l212; this card must never touch that dir.
OUT = f"{LAB}/l223"

# ===== VERBATIM l212_head.py lines 28-116 (sha 28ffbf5260f4bd0b) =====
BETA_L = 2.0
COHORT_K = 100
PCT_BAR = 0.10
GI_CARRIER = None  # set after the id join (v783 row index of the matched cell)
GI_MIR = None
o = {}
o["design"] = ("L212 the v783 leg, re-posed: does the DNp33 match avoid the "
               "nearest readout its own (brain-only) volume HAS? EXPLORATORY.")
o["prereg"] = "l212/PREREG.md"
o["beta_L"] = BETA_L


def log(s):
    print(f"[{time.time() - T0:7.1f}s] {s}", flush=True)


# ---------------- NT_CLASS: build_graph_banc.py's own table ------------------
NT_CLASS = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0,
            "histamine": -1.0, "dopamine": 0.2, "serotonin": 0.2,
            "octopamine": 0.2, "tyramine": 0.3}
NT_DEFAULT = 0.3  # ("unk", 0.3)

# ---------------- CERT-783 (HALTING): provenance ----------------------------
ids_all = np.load(f"{PB}/data/proofread_root_ids_783.npy")
Nall = int(len(ids_all))
assert Nall == 139255, (Nall, "v783 id count (STOP)")
assert ids_all.dtype == np.uint64, ids_all.dtype
idx_all = {int(r): i for i, r in enumerate(ids_all)}
assert len(idx_all) == Nall, "duplicate root ids (STOP)"

_live = torch.load(f"{PB}/brain_graph.pt", map_location="cpu",
                   weights_only=False)
_live_ids = _live["ids"].numpy().astype(np.uint64)
assert np.array_equal(_live_ids, ids_all), "live ids != Zenodo npy (STOP)"
_live_nnz = int(_live["W"].values().numel())
_live_meta = dict(_live["meta"])
assert _live_meta["neurons"] == 139255 and _live_meta["edges"] == 16847997, \
    (_live_meta, "live meta pins (STOP)")
assert _live_meta["signs"]["gaba"] == -1.0 and _live_meta["signs"]["dopamine"] == 0.2
_live_rowsum_pin = None
del _live
n_cert783 = 5
log(f"[CERT-783] GREEN ids array-equal (N {Nall}), live nnz {_live_nnz}, "
    f"meta pins asserted")

# ---------------- annotations ----------------------------------------------
ann = pd.read_csv(f"{PB}/data/neuron_annotations.tsv", sep="\t",
                  low_memory=False)
ann = ann[ann["root_id"].notna()].copy()
ann["gi"] = ann["root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()].copy()
ann["gi"] = ann["gi"].astype(int)
log(f"[ann] {len(ann)} annotated rows joined onto the v783 id set")

sup = ann["super_class"].fillna("").astype(str).to_numpy()
ctype = ann["cell_type"].fillna("").astype(str).to_numpy()
side = ann["side"].fillna("").astype(str).to_numpy()
nerve = ann["nerve"].fillna("").astype(str).to_numpy()
topnt = ann["top_nt"].fillna("unknown").astype(str).str.lower().to_numpy()
ann_gi = ann["gi"].to_numpy()

nt_name = np.array(["unknown"] * Nall, dtype=object)
nt_name[ann_gi] = topnt
sign_all = np.array([NT_CLASS.get(str(n), NT_DEFAULT) for n in nt_name],
                    np.float64)
is_glut = np.array([str(n) == "glutamate" for n in nt_name], bool)
o["nt_mix"] = {k: int(v) for k, v in
               pd.Series([str(x) for x in nt_name]).value_counts().items()}
log(f"[nt] mix {o['nt_mix']}")

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
mot_all = np.zeros(Nall, bool)
mot_all[ann_gi[sup == "motor"]] = True
assert int(dn_all.sum()) == 1303, (int(dn_all.sum()), "DN count (STOP)")
assert int(mot_all.sum()) == 110, (int(mot_all.sum()), "motor count (STOP)")

# ---------------- the two matched cells + CERT-L207 -------------------------
_st = os.stat(f"{LAB}/l207/static.json")
_fp = (_st.st_size, _st.st_mtime_ns)
with open(f"{LAB}/l207/static.json") as _fh:
    S207 = json.load(_fh)
_st2 = os.stat(f"{LAB}/l207/static.json")
assert (_st2.st_size, _st2.st_mtime_ns) == _fp, "l207/static.json MUTATED (STOP)"
CAR_783 = int(S207["Q3_v783_handle"]["carrier_match_id"])
MIR_783 = int(S207["Q3_v783_handle"]["mirror_match_id"])
assert S207["Q3_v783_handle"]["verdict"] == "UNANSWERABLE-BY-VOLUME"
assert S207["Q2_mirror"]["carrier_identity"]["cell_type"] == "DNp33"
assert CAR_783 == 720575940604103084 and MIR_783 == 720575940633165452

# ===== L223 DECLARED MODIFICATION (replaces l212_head.py lines 117-122)
# the parent's graceful-blocker block WRITES into OUT/static.json.
# A HALTING assert is strictly stronger and writes nothing.
assert CAR_783 in idx_all and MIR_783 in idx_all, (
    "L223: a DNp33 match id is absent from the v783 proofread id set "
    "(STOP) - this would be a real blocker, not a worked-around one")

# ===== VERBATIM l212_head.py lines 123-241 (sha b8c9434580e52d59) =====
GI_CARRIER = idx_all[CAR_783]
GI_MIR = idx_all[MIR_783]
_ca = ann[ann["gi"] == GI_CARRIER]
_mi = ann[ann["gi"] == GI_MIR]
assert len(_ca) == 1 and len(_mi) == 1, "annotation row count (STOP)"
CAR_ID = dict(gi=GI_CARRIER, root_id=str(CAR_783),
              cell_type=str(_ca["cell_type"].iloc[0]),
              side=str(_ca["side"].iloc[0]),
              super_class=str(_ca["super_class"].iloc[0]),
              nt=str(_ca["top_nt"].iloc[0]), nerve=str(_ca["nerve"].iloc[0]))
MIR_ID = dict(gi=GI_MIR, root_id=str(MIR_783),
              cell_type=str(_mi["cell_type"].iloc[0]),
              side=str(_mi["side"].iloc[0]),
              super_class=str(_mi["super_class"].iloc[0]),
              nt=str(_mi["top_nt"].iloc[0]), nerve=str(_mi["nerve"].iloc[0]))
assert CAR_ID["cell_type"] == "DNp33" == MIR_ID["cell_type"], "not DNp33 (STOP)"
assert CAR_ID["side"] == "left" and MIR_ID["side"] == "right", "sides (STOP)"
assert dn_all[GI_CARRIER] and dn_all[GI_MIR], "match not descending (STOP)"
o["cert_l207"] = dict(n_checks=8, carrier=CAR_ID, mirror=MIR_ID,
                      source="l207/static.json (read-only, mtime asserted)")
log(f"[CERT-L207] GREEN carrier {CAR_ID} | mirror {MIR_ID}")

# ---------------- the readout pools ----------------------------------------
# PRIMARY: super_class == motor, partitioned by NERVE (5 semantic groups).
POOL_G = {}
_mg = ann_gi[sup == "motor"]
_mn = nerve[sup == "motor"]
for _nv in ["PhN", "MxLbN", "CV", "AN", "ON"]:
    m = np.zeros(Nall, bool)
    m[_mg[_mn == _nv]] = True
    POOL_G[f"mot_{_nv}"] = m
_named = int(sum(int(m.sum()) for m in POOL_G.values()))
m = np.zeros(Nall, bool)
m[_mg[~np.isin(_mn, ["PhN", "MxLbN", "CV", "AN", "ON"])]] = True
if int(m.sum()) > 0:
    POOL_G["mot_other"] = m
POOL_SIZES = {k: int(v.sum()) for k, v in POOL_G.items()}
_stack = np.zeros(Nall, np.int64)
for _k, _m in POOL_G.items():
    _stack += _m.astype(np.int64)
assert _stack.max() <= 1, "readout pool overlap (STOP)"
assert int(_stack.sum()) == 110, (int(_stack.sum()), "readout != motor (STOP)")
o["readout_primary"] = dict(kind="v783 super_class==motor by nerve",
                            sizes=POOL_SIZES, n_cells=110, named=_named)
log(f"[readout] PRIMARY {POOL_SIZES}")

# SECONDARY (descriptive, no branch): descending minus the two actors.
POOL_S = {}
_dm = dn_all.copy()
_dm[GI_CARRIER] = False
_dm[GI_MIR] = False
POOL_S["desc"] = _dm
o["readout_secondary"] = dict(kind="v783 super_class==descending minus actors",
                              n_cells=int(_dm.sum()))

# ---------------- the raw edge table ---------------------------------------
import pyarrow.feather as _ft  # noqa: E402

_tb = _ft.read_table(f"{PB}/data/proofread_connections_783.feather",
                     columns=["pre_pt_root_id", "post_pt_root_id", "syn_count"],
                     memory_map=True)
assert _tb.num_rows == 16847997, (_tb.num_rows, "feather rows (STOP)")
_pre = _tb.column("pre_pt_root_id").to_numpy().astype(np.uint64)
_post = _tb.column("post_pt_root_id").to_numpy().astype(np.uint64)
_syn = _tb.column("syn_count").to_numpy().astype(np.int64)
del _tb
_srt = np.argsort(ids_all, kind="stable")
_sid = ids_all[_srt]


def _to_gi(arr):
    p = np.searchsorted(_sid, arr)
    p[p >= Nall] = 0
    ok = _sid[p] == arr
    gi = np.where(ok, _srt[p], -1)
    return gi.astype(np.int64)


src_e = _to_gi(_pre)
dst_e = _to_gi(_post)
keepe = (src_e >= 0) & (dst_e >= 0)
src_e, dst_e, syn_e = src_e[keepe], dst_e[keepe], _syn[keepe]
del _pre, _post, _syn
log(f"[edges] {int(keepe.sum())} of 16847997 rows inside the id set")

# collapse per-NEUROPIL rows by SUMMING syn_count (the BANC pair rule)
_key = src_e * np.int64(Nall) + dst_e
_uk, _inv = np.unique(_key, return_inverse=True)
w_syn = np.bincount(_inv, weights=syn_e.astype(np.float64)).astype(np.float64)
src_all = (_uk // np.int64(Nall)).astype(np.int64)
dst_all = (_uk % np.int64(Nall)).astype(np.int64)
NEDGE = int(len(_uk))
assert NEDGE == _live_nnz, (NEDGE, _live_nnz, "pair count != live nnz (STOP)")
n_cert783 += 1
del _key, _inv, src_e, dst_e, syn_e, _uk
log(f"[CERT-783] GREEN unique pairs {NEDGE} == live graph nnz")
o["cert_783"] = dict(n_checks=n_cert783, N=Nall, n_pairs=NEDGE,
                     live_nnz=_live_nnz, raw_rows=16847997,
                     mode="array_equal / ==",
                     note="ids from the Zenodo npy; pair count cross-checked "
                          "against the live coalesced graph's nnz.")


def build_v783(beta, pools, name):
    """build_sub's expression, specialised to the single v783 substrate."""
    _sa = sign_all[src_all]
    _sb = np.where(is_glut[src_all], -np.abs(_sa), _sa)
    ev = (np.log1p(w_syn) * _sb).astype(np.float64)
    vv = ev.copy()
    vv[vv < 0] *= beta
    jv = np.abs(vv)
    om = np.zeros(Nall)
    np.add.at(om, src_all, jv)
    loc = np.arange(Nall, dtype=np.int64)    # whole volume, no sub-selection
    keep = np.ones(Nall, bool)
    pl = {pk: np.where(P)[0] for pk, P in pools.items()}
    return dict(name=name, keep=keep, loc=loc, n=Nall, n_edges=NEDGE,
                jv=jv, rows=dst_all, cols=src_all, pool_l=pl,
                pool_all=np.unique(np.concatenate([pl[k] for k in pl])), om=om)

# ===== VERBATIM l207_tail.py lines 82-110 (sha256-16 fce1e71189eb1ed7) =====
def reach_sub(c_local, sub, depth=2):
    """EXPRESSION-IDENTICAL to the certified reach() (L206 float-equality
    lesson: a float claim is a claim about the expression)."""
    x = np.zeros(sub["n"])
    x[c_local] = 1.0
    res = {}
    for d in range(1, depth + 1):
        y = np.zeros(sub["n"])
        np.add.at(y, sub["rows"], sub["jv"] * x[sub["cols"]])
        x = y
        res[d] = {pk: float(x[sub["pool_l"][pk]].sum()) for pk in sub["pool_l"]}
    return res


def power_iter_sub(sub, jv, iters=400):
    n = sub["n"]
    v = np.ones(n) / math.sqrt(n)
    lam, hist = 0.0, []
    for i in range(iters):
        w = np.zeros(n)
        np.add.at(w, sub["rows"], jv * v[sub["cols"]])
        nrm = float(np.linalg.norm(w))
        if nrm == 0.0:
            return 0.0, []
        v = w / nrm
        lam = nrm
        if i >= iters - 6:
            hist.append(nrm)
    return lam, float((max(hist) - min(hist)) / max(hist))

# ===== VERBATIM l207_tail.py lines 199-241 (sha256-16 340c0432c85c6e7b) =====
# ---------------- the statistic --------------------------------------------
def Rstat(sub, gi, lam1):
    lc = int(sub["loc"][gi])
    assert lc >= 0, (sub["name"], gi, "cell absent (STOP)")
    rr = reach_sub(lc, sub, 2)
    p2 = float(sum(rr[2].values()))
    p1 = float(sum(rr[1].values()))
    m = float(sub["om"][gi])
    return dict(gi=int(gi), P1=p1, P2=p2, m_out=m,
                R=(p2 / (lam1 ** 2 * m)) if m > 0 else None,
                R1=(p1 / (lam1 * m)) if m > 0 else None)


def pct_of(val, cohort_vals):
    """fraction of the cohort STRICTLY SMALLER (low = avoider)."""
    vs = [v for v in cohort_vals if v is not None]
    assert len(vs) >= 10, "cohort too small"
    return float(sum(1 for v in vs if v < val) / len(vs))


def rankvec(a):
    order = sorted(range(len(a)), key=lambda i: a[i])
    r = [0.0] * len(a)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and a[order[j + 1]] == a[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman_l(a, b):
    ra, rb = rankvec(a), rankvec(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return float(num / (da * db)) if da > 0 and db > 0 else None

# ===== VERBATIM l207_tail.py lines 338-346 (sha256-16 f4585bcc52f7ab0a) =====
def matched_cohort(sub, gi, k=COHORT_K):
    pres = np.where(sub["keep"] & dn_all)[0]
    pres = pres[sub["om"][pres] > 0]
    pres = pres[~np.isin(pres, [GI_CARRIER, GI_MIR])]
    tgt = math.log(float(sub["om"][gi]))
    d = np.abs(np.log(sub["om"][pres]) - tgt)
    sel = pres[np.argsort(d, kind="stable")[:k]]
    assert len(sel) == k, (sub["name"], "cohort short")
    return [int(x) for x in sel]

# ===== VERBATIM l212_tail.py lines 1-227 (sha 79271ef179d9c9be) = L212's WHOLE measurement pipeline, writer CUT =====

# ===================== L212 TAIL ==========================================
# CERT-MV (HALTING): the fast bincount matvec must be EXACTLY array-equal to
# the verbatim np.add.at kernel, and the gated reach/power-iteration must
# reproduce the verbatim functions at FLOAT EQUALITY, before any cohort value
# is read (the L210/L211 pattern).

SUB = build_v783(BETA_L, POOL_G, "V783_primary")
log(f"[sub] n {SUB['n']} edges {SUB['n_edges']} om>0 {int((SUB['om']>0).sum())}")
assert SUB["om"][GI_CARRIER] > 0 and SUB["om"][GI_MIR] > 0, "zero out-mass (STOP)"


def mv_slow(sub, x):
    y = np.zeros(sub["n"])
    np.add.at(y, sub["rows"], sub["jv"] * x[sub["cols"]])
    return y


def mv_fast(sub, x):
    return np.bincount(sub["rows"], weights=sub["jv"] * x[sub["cols"]],
                       minlength=sub["n"])


_rng = np.random.default_rng(21200)
n_mv = 0
for _p in range(4):
    if _p == 0:
        _x = np.zeros(SUB["n"]); _x[GI_CARRIER] = 1.0
    elif _p == 1:
        _x = np.zeros(SUB["n"]); _x[GI_MIR] = 1.0
    elif _p == 2:
        _x = np.ones(SUB["n"]) / math.sqrt(SUB["n"])
    else:
        _x = _rng.random(SUB["n"])
    assert np.array_equal(mv_slow(SUB, _x), mv_fast(SUB, _x)), (_p, "CERT-MV")
    n_mv += 1
log(f"[CERT-MV] GREEN {n_mv} EXACT array equalities (bincount == np.add.at)")


def reach_fast(c_local, sub, depth=2):
    """reach_sub's EXPRESSION with the gated matvec substituted."""
    x = np.zeros(sub["n"])
    x[c_local] = 1.0
    res = {}
    for d in range(1, depth + 1):
        x = mv_fast(sub, x)
        res[d] = {pk: float(x[sub["pool_l"][pk]].sum()) for pk in sub["pool_l"]}
    return res


def power_iter_fast(sub, jv, iters=400):
    """power_iter_sub's EXPRESSION with the gated matvec substituted."""
    n = sub["n"]
    v = np.ones(n) / math.sqrt(n)
    lam, hist = 0.0, []
    _s = dict(sub)
    _s["jv"] = jv
    for i in range(iters):
        w = mv_fast(_s, v)
        nrm = float(np.linalg.norm(w))
        if nrm == 0.0:
            return 0.0, []
        v = w / nrm
        lam = nrm
        if i >= iters - 6:
            hist.append(nrm)
    return lam, float((max(hist) - min(hist)) / max(hist))


# gate reach: float equality vs the VERBATIM reach_sub on both actors
n_gate = 0
for _nm, _gi in (("carrier", GI_CARRIER), ("mirror", GI_MIR)):
    _a = reach_sub(int(SUB["loc"][_gi]), SUB, 2)
    _b = reach_fast(int(SUB["loc"][_gi]), SUB, 2)
    for _d in (1, 2):
        for _pk in SUB["pool_l"]:
            assert _a[_d][_pk] == _b[_d][_pk], (_nm, _d, _pk, "reach gate (STOP)")
            n_gate += 1
# gate the power iteration: 12 iters, both kernels, float equality
_l1, _s1 = power_iter_sub(SUB, SUB["jv"], iters=12)
_l2, _s2 = power_iter_fast(SUB, SUB["jv"], iters=12)
assert _l1 == _l2 and _s1 == _s2, (_l1, _l2, "power gate (STOP)")
n_gate += 2
log(f"[CERT-GATE] GREEN {n_gate} float equalities: the fast kernels ARE the "
    f"verbatim l207_tail functions")
o["cert_mv"] = dict(n_checks=n_mv, mode="EXACT array_equal (==)")
o["cert_gate"] = dict(n_checks=n_gate, mode="float equality (==)",
                      source="l207_tail.py reach_sub / power_iter_sub verbatim")

# ---------------- lam1 and the registered NO-OP check ----------------------
LAM1, SPR = power_iter_fast(SUB, SUB["jv"], iters=400)
log(f"[lam1] {LAM1:.6f} (rel spread last6 {SPR:.3e})")
# ===== L223b DECLARED MODIFICATION (replaces the inherited escape)
# the parent escape WRITES l223/static.json; this addendum must never
# touch it.  SPR was MEASURED at 4.11e-16, so a halting assert is
# strictly stronger and writes nothing.
assert SPR < 1e-6, (SPR, "power iteration did not converge (STOP)")
o["lam1"] = dict(value=LAM1, rel_spread_last6=SPR, iters=400)


def Rfast(sub, gi, lam1):
    """Rstat's EXPRESSION with the gated reach."""
    lc = int(sub["loc"][gi])
    assert lc >= 0, (sub["name"], gi, "cell absent (STOP)")
    rr = reach_fast(lc, sub, 2)
    p2 = float(sum(rr[2].values()))
    p1 = float(sum(rr[1].values()))
    m = float(sub["om"][gi])
    return dict(gi=int(gi), P1=p1, P2=p2, m_out=m,
                R=(p2 / (lam1 ** 2 * m)) if m > 0 else None,
                R1=(p1 / (lam1 * m)) if m > 0 else None)


for _nm, _gi in (("carrier", GI_CARRIER), ("mirror", GI_MIR)):
    _ra = Rstat(SUB, _gi, LAM1)
    _rb = Rfast(SUB, _gi, LAM1)
    for _k in ("P1", "P2", "m_out", "R", "R1"):
        assert _ra[_k] == _rb[_k], (_nm, _k, "Rstat gate (STOP)")
log("[CERT-GATE] GREEN Rfast == verbatim Rstat on both actors (10 checks)")

# registered NO-OP: R is invariant to a global rescale of A (L209's law)
_s3 = dict(SUB)
_s3["jv"] = SUB["jv"] * 3.0
_l3, _ = power_iter_fast(_s3, _s3["jv"], iters=400)
_r_a = Rfast(SUB, GI_CARRIER, LAM1)["R"]
_r_b = Rfast(_s3, GI_CARRIER, _l3)["R"]
_noop = abs(_r_b - _r_a) / abs(_r_a)
o["rescale_noop"] = dict(rel_diff=_noop, lam1_scaled=_l3,
                         note="R measured invariant under A -> 3A (L209)")
assert _noop < 1e-9, (_noop, "R not rescale-invariant (STOP)")
log(f"[NO-OP] GREEN R rescale-invariance rel diff {_noop:.2e}")
del _s3

# ---------------- PRIMARY leg ----------------------------------------------
R_CAR = Rfast(SUB, GI_CARRIER, LAM1)
R_MIR = Rfast(SUB, GI_MIR, LAM1)
COH_C = matched_cohort(SUB, GI_CARRIER)
COH_M = matched_cohort(SUB, GI_MIR)
COH_U = sorted(set(COH_C) | set(COH_M))
log(f"[cohort] carrier {len(COH_C)} mirror {len(COH_M)} union {len(COH_U)} "
    f"- measuring R on each")
CV = {}
for _i, _g in enumerate(COH_U):
    CV[_g] = Rfast(SUB, _g, LAM1)["R"]
    if _i % 25 == 0:
        log(f"  cohort {_i}/{len(COH_U)}")


def leg(r_car, r_mir, cohc, cohm, cv, sub):
    _vc = [cv[g] for g in cohc]
    _vm = [cv[g] for g in cohm]
    return dict(
        carrier_R=r_car["R"], mirror_R=r_mir["R"],
        carrier_P2=r_car["P2"], mirror_P2=r_mir["P2"],
        carrier_P1=r_car["P1"], mirror_P1=r_mir["P1"],
        carrier_m_out=r_car["m_out"], mirror_m_out=r_mir["m_out"],
        carrier_pct=pct_of(r_car["R"], _vc),
        mirror_pct=pct_of(r_mir["R"], _vm),
        cohort_k=COHORT_K, cohort_union_n=len(set(cohc) | set(cohm)),
        cohort_median_carrier=float(np.median(_vc)),
        cohort_median_mirror=float(np.median(_vm)),
        cohort_zero_frac_carrier=float(np.mean([v == 0.0 for v in _vc])),
        cohort_zero_frac_mirror=float(np.mean([v == 0.0 for v in _vm])),
        cohort_min_carrier=float(np.min(_vc)), cohort_max_carrier=float(np.max(_vc)),
        carrier_rank_of_cohort=int(1 + sum(1 for v in _vc if v < r_car["R"])),
        mirror_rank_of_cohort=int(1 + sum(1 for v in _vm if v < r_mir["R"])),
        deficit_vs_median=(float(np.median(_vc)) / r_car["R"]
                           if r_car["R"] > 0 else None),
        mass_match_logspread_carrier=float(np.max(np.abs(
            np.log([sub["om"][g] for g in cohc]) - math.log(r_car["m_out"])))),
        mass_match_logspread_mirror=float(np.max(np.abs(
            np.log([sub["om"][g] for g in cohm]) - math.log(r_mir["m_out"])))))


PRI = leg(R_CAR, R_MIR, COH_C, COH_M, CV, SUB)
PRI["readout"] = "PRIMARY v783 motor (110 cells, 5 nerve pools)"
PRI["per_pool_carrier"] = reach_fast(int(SUB["loc"][GI_CARRIER]), SUB, 2)[2]
PRI["per_pool_mirror"] = reach_fast(int(SUB["loc"][GI_MIR]), SUB, 2)[2]
o["Q1_primary"] = PRI
log(f"[PRIMARY] carrier R {PRI['carrier_R']:.6g} pct {PRI['carrier_pct']:.3f} "
    f"| mirror R {PRI['mirror_R']:.6g} pct {PRI['mirror_pct']:.3f} "
    f"| cohort med {PRI['cohort_median_carrier']:.6g} "
    f"| zero frac {PRI['cohort_zero_frac_carrier']:.3f}")

# ---------------- the branch (registered table) -----------------------------
_pc = PRI["carrier_pct"]
if (PRI["carrier_m_out"] == 0 or PRI["cohort_zero_frac_carrier"] > 0.50):
    BRANCH = "V_DEGENERATE"
elif _pc <= PCT_BAR:
    BRANCH = "V_AVOIDS"
elif _pc >= 0.90:
    BRANCH = "V_HIGH"
else:
    BRANCH = "V_MIDDLE"
o["branch"] = BRANCH
log(f"[BRANCH] {BRANCH} (carrier_pct {_pc})")

# ---------------- SECONDARY leg (descriptive, no branch) --------------------
SUB2 = build_v783(BETA_L, POOL_S, "V783_secondary_desc")
assert np.array_equal(SUB2["jv"], SUB["jv"]), "operator differs (STOP)"
R_CAR2 = Rfast(SUB2, GI_CARRIER, LAM1)
R_MIR2 = Rfast(SUB2, GI_MIR, LAM1)
CV2 = {g: Rfast(SUB2, g, LAM1)["R"] for g in COH_U}
SEC = leg(R_CAR2, R_MIR2, COH_C, COH_M, CV2, SUB2)
SEC["readout"] = "SECONDARY v783 descending minus actors (1301), DESCRIPTIVE"
o["Q2_secondary_descriptive"] = SEC
log(f"[SECONDARY] carrier pct {SEC['carrier_pct']:.3f} "
    f"mirror pct {SEC['mirror_pct']:.3f}")

# ---------------- BETA_L = 1.0 robustness leg (reported, no branch) ---------
SUB3 = build_v783(1.0, POOL_G, "V783_primary_beta1")
LAM3, SPR3 = power_iter_fast(SUB3, SUB3["jv"], iters=400)
R_CAR3 = Rfast(SUB3, GI_CARRIER, LAM3)
R_MIR3 = Rfast(SUB3, GI_MIR, LAM3)
COH_C3 = matched_cohort(SUB3, GI_CARRIER)
COH_M3 = matched_cohort(SUB3, GI_MIR)
CV3 = {g: Rfast(SUB3, g, LAM3)["R"] for g in sorted(set(COH_C3) | set(COH_M3))}
ROB = leg(R_CAR3, R_MIR3, COH_C3, COH_M3, CV3, SUB3)
ROB["readout"] = "PRIMARY readout, BETA_L=1.0 (pure |W|), ROBUSTNESS"
ROB["lam1"] = LAM3
ROB["rel_spread_last6"] = SPR3
ROB["cohort_identity_jaccard_carrier"] = float(
    len(set(COH_C3) & set(COH_C)) / len(set(COH_C3) | set(COH_C)))
ROB["d_carrier_pct_vs_primary"] = ROB["carrier_pct"] - PRI["carrier_pct"]
o["Q3_robust_beta1"] = ROB
log(f"[BETA1] carrier pct {ROB['carrier_pct']:.3f} "
    f"(d {ROB['d_carrier_pct_vs_primary']:+.3f}) lam1 {LAM3:.6f}")

# ===== L223 INJECT (3 lines): the two names the inherited CERT-212
# slice needs from its parent tail, plus this card's OUT guard. =====
assert OUT.endswith("/l223") and os.path.isdir(OUT), (OUT, "OUT (STOP)")
PARENT_BRANCH = o.get("branch")
o["parent_branch_reproduced"] = PARENT_BRANCH

# ===== VERBATIM l222_tail.py lines 26-88 (sha f738545799e6f4fb) = CERT-212, inherited as SOURCE (L211) =====
# ---------------- CERT-212 (HALTING): reproduce the parent exactly ----------
_stp = os.stat(f"{LAB}/l212/static.json")
_fpp = (_stp.st_size, _stp.st_mtime_ns)
with open(f"{LAB}/l212/static.json") as _fh:
    S212 = json.load(_fh)
n212 = 0
_bad = []


def _eq(path, got, want):
    global n212
    n212 += 1
    if isinstance(want, float) or isinstance(got, float):
        ok = (float(got) == float(want))
    else:
        ok = (got == want)
    if not ok:
        _bad.append((path, got, want))


def _walk(path, got, want):
    if isinstance(want, dict):
        assert isinstance(got, dict), (path, "shape (STOP)")
        assert set(got.keys()) == set(want.keys()), (path, "keys (STOP)")
        for k in sorted(want.keys()):
            _walk(f"{path}.{k}", got[k], want[k])
    elif isinstance(want, list):
        assert isinstance(got, list) and len(got) == len(want), (path, "len")
        for i, (g, w) in enumerate(zip(got, want)):
            _walk(f"{path}[{i}]", g, w)
    else:
        _eq(path, got, want)


_mine = dict(Q1_primary=o["Q1_primary"],
             Q2_secondary_descriptive=o["Q2_secondary_descriptive"],
             Q3_robust_beta1=o["Q3_robust_beta1"],
             lam1=o["lam1"], rescale_noop=o["rescale_noop"],
             readout_primary=o["readout_primary"],
             readout_secondary=o["readout_secondary"],
             cert_783=o["cert_783"], cert_mv=o["cert_mv"],
             cert_gate=o["cert_gate"], cert_l207=o["cert_l207"],
             nt_mix=o["nt_mix"], beta_L=o["beta_L"])
for _k in sorted(_mine):
    _walk(_k, _mine[_k], S212[_k])
assert not _bad, ("CERT-212 MISMATCH (STOP)", _bad[:12])
assert PARENT_BRANCH == S212["branch"] == "V_AVOIDS", (PARENT_BRANCH, "STOP")
n212 += 1
_stp2 = os.stat(f"{LAB}/l212/static.json")
assert (_stp2.st_size, _stp2.st_mtime_ns) == _fpp, "l212/static.json MUTATED"
o["cert_212"] = dict(n_checks=n212, mode="float/int equality (==), recursive",
                     source="l212/static.json (read-only, mtime asserted)",
                     note="L212's whole Q1/Q2/Q3 table reproduced by RE-RUNNING "
                          "its pipeline as a verbatim source slice, never by "
                          "re-implementing it (L211 lesson).")
log(f"[CERT-212] GREEN {n212} stored L212 values reproduced at float equality")

# the floor-1 anchors, read from MY rebuild (identical to the parent by CERT-212)
PCT_CAR_1 = o["Q1_primary"]["carrier_pct"]
PCT_MIR_1 = o["Q1_primary"]["mirror_pct"]
GAP_1 = abs(PCT_MIR_1 - PCT_CAR_1)
assert o["Q1_primary"]["carrier_P1"] == 0.0, "carrier P1 != 0 at floor 1 (STOP)"
assert o["Q1_primary"]["mirror_P1"] == math.log1p(1.0), "mirror P1 (STOP)"

# ===================== L223 TAIL ==========================================
# Everything above this line is VERBATIM inherited source: l212_head.py sliced
# to CUT its blocker-writer and re-point OUT, the three l207_tail.py function
# slices, l212_tail.py lines 1-227 (L212's ENTIRE measurement pipeline, writer
# CUT) and l222_tail.py lines 26-88 (CERT-212, inherited as SOURCE rather than
# re-implemented -- the L211 lesson).  So CERT-783, CERT-L207, CERT-MV,
# CERT-GATE, the lam1 power iteration, the rescale NO-OP, L212's Q1/Q2/Q3 legs
# and CERT-212's whole float-equality table all ran before a single L223 number
# exists.

ZERO_FRAC_BAR = 0.10
RHO_DEGEN_BAR = 0.95
o["bars"] = dict(pct_specific=PCT_BAR, rho_degenerate=RHO_DEGEN_BAR,
                 zero_frac_escape=ZERO_FRAC_BAR, cohort_k=COHORT_K,
                 beta_L=BETA_L)

# ---------------- CERT-PAIR (HALTING): the paired table IS the published one -
nP = 0
assert set(CV.keys()) == set(COH_U), "CV keys != COH_U (STOP)"
nP += 1
assert set(CV2.keys()) == set(COH_U), "CV2 keys != COH_U (STOP)"
nP += 1
assert len(COH_U) == o["Q1_primary"]["cohort_union_n"] == \
    o["Q2_secondary_descriptive"]["cohort_union_n"], "union n (STOP)"
nP += 1
assert np.array_equal(SUB2["jv"], SUB["jv"]), "legs differ in operator (STOP)"
nP += 1
assert np.array_equal(SUB2["rows"], SUB["rows"]) and \
    np.array_equal(SUB2["cols"], SUB["cols"]), "legs differ in edges (STOP)"
nP += 1
for _nm, _ra, _rb, _blk, _key in (
        ("carrier_motor", R_CAR, None, "Q1_primary", "carrier_R"),
        ("mirror_motor", R_MIR, None, "Q1_primary", "mirror_R"),
        ("carrier_desc", R_CAR2, None, "Q2_secondary_descriptive", "carrier_R"),
        ("mirror_desc", R_MIR2, None, "Q2_secondary_descriptive", "mirror_R")):
    assert _ra["R"] == o[_blk][_key], (_nm, "paired value != published (STOP)")
    nP += 1
assert R_CAR["m_out"] == R_CAR2["m_out"] and R_MIR["m_out"] == R_MIR2["m_out"], \
    "m_out differs between legs (STOP)"
nP += 1
assert all(CV[g] is not None and CV2[g] is not None for g in COH_U), \
    "a cohort cell has R=None (zero out-mass) (STOP)"
nP += 1
o["cert_pair"] = dict(n_checks=nP, mode="set / array_equal / float equality",
                      note="CV (motor) and CV2 (descending) cover the IDENTICAL "
                           "cohort key set on the IDENTICAL operator, and both "
                           "actors' entries equal L212's published R values.")
log(f"[CERT-PAIR] GREEN {nP} checks - both legs on one cohort, one operator")

# ---------------- CERT-RANK (HALTING): rankvec IS a midrank -----------------
_ra_in = [CV[g] for g in COH_U] + [R_CAR["R"], R_MIR["R"]]
_rb_in = [CV2[g] for g in COH_U] + [R_CAR2["R"], R_MIR2["R"]]
nR = 0
for _vec in (_ra_in, _rb_in):
    _rk = rankvec(_vec)
    _n = len(_vec)
    assert abs(sum(_rk) - _n * (_n + 1) / 2.0) < 1e-9, "rank sum (STOP)"
    nR += 1
    _by = {}
    for _v, _r in zip(_vec, _rk):
        _by.setdefault(_v, set()).add(_r)
    for _v, _rs in _by.items():
        assert len(_rs) == 1, (_v, "a tie group got DIFFERENT ranks (STOP)")
        nR += 1
    assert len(_by) == len(set(_rk)), "distinct values != distinct ranks (STOP)"
    nR += 1
o["cert_rank"] = dict(n_checks=nR, mode="exact tie-group identity",
                      note="the inherited rankvec is verified to be an "
                           "AVERAGE-rank (midrank) estimator on THIS data "
                           "before any C_rank is read (tick-252 midrank law); "
                           "argsort-of-argsort would fail the tie-group gate.")
log(f"[CERT-RANK] GREEN {nR} checks - rankvec is a midrank on this data")

# ---------------- Q223-0 (READ FIRST): are the two legs the same thing? -----
RHO = {}
for _nm, _coh in (("COH_C", COH_C), ("COH_M", COH_M), ("COH_U", COH_U)):
    RHO[_nm] = spearman_l([CV[g] for g in _coh], [CV2[g] for g in _coh])
o["Q223_0_rho_first"] = dict(
    rho_COH_C=RHO["COH_C"], rho_COH_M=RHO["COH_M"], rho_COH_U=RHO["COH_U"],
    n_COH_C=len(COH_C), n_COH_M=len(COH_M), n_COH_U=len(COH_U),
    bar=RHO_DEGEN_BAR,
    note="Spearman (midranks) between the motor-readout R and the "
         "descending-readout R across the cohort. Read BEFORE the carrier's "
         "contrast because it decides whether the contrast carries any "
         "information at all.")
log(f"[Q223-0] rho COH_C {RHO['COH_C']:.4f} | COH_M {RHO['COH_M']:.4f} "
    f"| COH_U {RHO['COH_U']:.4f} (bar {RHO_DEGEN_BAR})")

# ---------------- the contrast ----------------------------------------------
C_CAR = math.log(R_CAR["R"]) - math.log(R_CAR2["R"])
C_MIR = math.log(R_MIR["R"]) - math.log(R_MIR2["R"])


def clog_vec(coh):
    """C_log over a cohort, EXCLUDING cells with a zero leg (PREREG 0d)."""
    keep, drop = [], []
    for g in coh:
        if CV[g] > 0.0 and CV2[g] > 0.0:
            keep.append(math.log(CV[g]) - math.log(CV2[g]))
        else:
            drop.append(int(g))
    return keep, drop


VC, DROP_C = clog_vec(COH_C)
VM, DROP_M = clog_vec(COH_M)
VU, DROP_U = clog_vec(COH_U)
ZFRAC_C = len(DROP_C) / float(len(COH_C))
ZFRAC_M = len(DROP_M) / float(len(COH_M))
log(f"[C_log] carrier {C_CAR:.4f} mirror {C_MIR:.4f} "
    f"| excluded zero cells C {len(DROP_C)} M {len(DROP_M)} U {len(DROP_U)}")


def crank_pct(coh, r_act, r_act2):
    """C_rank on the common pool coh + {actor}; actor is the LAST element."""
    am = [CV[g] for g in coh] + [r_act["R"]]
    ad = [CV2[g] for g in coh] + [r_act2["R"]]
    rm, rd = rankvec(am), rankvec(ad)
    n = float(len(am))
    cr = [(rm[i] - rd[i]) / n for i in range(len(am))]
    return pct_of(cr[-1], cr[:-1]), cr[-1], cr[:-1]


# ---------------- BRANCH (registered order; the escape SHORT-CIRCUITS) ------
PRIMARY = None
if ZFRAC_C > ZERO_FRAC_BAR:
    BRANCH223 = "S_ZERO_DEGENERATE"
    PRIMARY = "C_rank (switched by the registered 0d escape)"
    _pc_car, _cr_car, _crv = crank_pct(COH_C, R_CAR, R_CAR2)
    _pc_mir, _cr_mir, _ = crank_pct(COH_M, R_MIR, R_MIR2)
    o["Q223_1_primary"] = dict(
        escape="S_ZERO_DEGENERATE: C_log is undefined on too much of the "
               "cohort, so the C_log legs were NOT read (control flow skipped "
               "them, not a flag - the L222 lesson).",
        zero_frac_COH_C=ZFRAC_C, bar=ZERO_FRAC_BAR,
        carrier_pct_rank=_pc_car, mirror_pct_rank=_pc_mir,
        carrier_C_rank=_cr_car, mirror_C_rank=_cr_mir)
    PCT_LOG_CAR = None
    PCT_LOG_MIR = None
else:
    PRIMARY = "C_log percentile vs COH_C"
    PCT_LOG_CAR = pct_of(C_CAR, VC)
    PCT_LOG_MIR = pct_of(C_MIR, VM)
    PCT_LOG_CAR_U = pct_of(C_CAR, VU)
    PCT_LOG_MIR_U = pct_of(C_MIR, VU)
    if RHO["COH_C"] is not None and RHO["COH_C"] >= RHO_DEGEN_BAR:
        BRANCH223 = "S_DEGENERATE"
    elif PCT_LOG_CAR <= PCT_BAR:
        BRANCH223 = "S_SPECIFIC"
    else:
        BRANCH223 = "S_GENERIC"
    o["Q223_1_primary"] = dict(
        carrier_C_log=C_CAR, mirror_C_log=C_MIR,
        carrier_pct_own_cohort=PCT_LOG_CAR, mirror_pct_own_cohort=PCT_LOG_MIR,
        carrier_rank_of_cohort=int(1 + sum(1 for v in VC if v < C_CAR)),
        mirror_rank_of_cohort=int(1 + sum(1 for v in VM if v < C_MIR)),
        n_scored_carrier=len(VC), n_scored_mirror=len(VM),
        excluded_zero_carrier=len(DROP_C), excluded_zero_mirror=len(DROP_M),
        zero_frac_COH_C=ZFRAC_C, zero_frac_COH_M=ZFRAC_M,
        bar=PCT_BAR,
        note="C_log(g) = log R_motor(g) - log R_desc(g). COHORT-FREE by "
             "construction: a cell's value cannot move when the comparison "
             "set moves (L222's cohort-relocation law applied prophylactically)")
    o["Q223_2_homolog_and_common"] = dict(
        carrier_pct_union=PCT_LOG_CAR_U, mirror_pct_union=PCT_LOG_MIR_U,
        n_scored_union=len(VU), excluded_zero_union=len(DROP_U),
        d_pct_own=PCT_LOG_MIR - PCT_LOG_CAR,
        d_pct_union=PCT_LOG_MIR_U - PCT_LOG_CAR_U,
        cohort_free_d_C_log=C_MIR - C_CAR,
        cohort_free_ratio=math.exp(C_MIR - C_CAR),
        note="L222's companion set: the OWN-cohort reading, the COMMON-cohort "
             "(union) reading and the COHORT-FREE raw values, all three "
             "reported so a cohort relocation cannot flip the sign unseen.")
o["branch"] = BRANCH223
o["primary_currency"] = PRIMARY
log(f"[BRANCH] {BRANCH223} (primary = {PRIMARY})")

# ---------------- Q223-3 companion currency ---------------------------------
PC_RANK_CAR, CR_CAR, CRV_C = crank_pct(COH_C, R_CAR, R_CAR2)
PC_RANK_MIR, CR_MIR, CRV_M = crank_pct(COH_M, R_MIR, R_MIR2)

# ===== L223b INJECT (1 line): alias the parent OUT for the guard
OUTB = OUT

# ===================== L223b ADDENDUM (POST-HOC, declared) ================
# Q223-5 FAILED: the carrier's two currencies disagree by 0.1496 of a
# percentile (C_log .0404 vs C_rank .1900) while the mirror's agree to 0.0134.
# This addendum asks the ONE question that decides whether that is a statement
# about the CARRIER or about the CURRENCIES, and it is POST-HOC: it was
# written after reading l223/static.json and carries NO registered branch.
#
# Everything above this line is l223_static.py lines 1-819 VERBATIM, with ONE
# declared modification (the inherited V_DEGENERATE escape at 432-436, whose
# json-dump write targets the PARENT's artifact, replaced by a halting assert), so
# this prefix contains ZERO writes and every L223 gate re-ran for free.

assert OUTB.endswith("/l223"), (OUTB, "OUT (STOP)")
a = {}
a["design"] = ("L223b POST-HOC: is the C_log / C_rank currency disagreement a "
               "property of the CARRIER or of the two currencies? Nonselective "
               "leave-one-out over the carrier's own cohort.")
a["post_hoc"] = ("Written AFTER reading l223/static.json. No branch, no bar, "
                 "no prediction - descriptive only (the L214 rule).")
a["parent_sha_checked"] = True

# ---------------- CERT-223 (HALTING): the parent's own numbers --------------
_stp = os.stat(f"{LAB}/l223/static.json")
_fpp = (_stp.st_size, _stp.st_mtime_ns)
with open(f"{LAB}/l223/static.json") as _fh:
    S223 = json.load(_fh)
n223 = 0
for _k, _v in (("carrier_C_log", C_CAR), ("mirror_C_log", C_MIR),
               ("carrier_pct_own_cohort", PCT_LOG_CAR),
               ("mirror_pct_own_cohort", PCT_LOG_MIR)):
    assert S223["Q223_1_primary"][_k] == _v, (_k, "CERT-223 (STOP)")
    n223 += 1
for _k, _v in (("carrier_pct_rank", PC_RANK_CAR), ("mirror_pct_rank", PC_RANK_MIR),
               ("carrier_C_rank", CR_CAR), ("mirror_C_rank", CR_MIR)):
    assert S223["Q223_3_companion_rank"][_k] == _v, (_k, "CERT-223 (STOP)")
    n223 += 1
for _k in ("rho_COH_C", "rho_COH_M", "rho_COH_U"):
    assert S223["Q223_0_rho_first"][_k] == RHO[_k.split("_", 1)[1]], \
        (_k, "CERT-223 rho (STOP)")
    n223 += 1
assert S223["branch"] == "S_SPECIFIC" and S223["n_predictions_correct"] == 5
n223 += 2
assert S223["cert_212"]["n_checks"] == 139 and S223["cert_pair"]["n_checks"] == 11 \
    and S223["cert_rank"]["n_checks"] == 252
n223 += 3
a["cert_223"] = dict(n_checks=n223, mode="float/int equality (==)",
                     source="l223/static.json (read-only, mtime asserted)")
log(f"[CERT-223] GREEN {n223} parent values reproduced at float equality")

# ---------------- the leave-one-out currency comparison ---------------------
# For EVERY cohort cell, score it the way the carrier was scored: its own
# C_log percentile against the OTHER cohort members, and its own C_rank
# percentile against theirs. Nonselective by construction - the carrier is
# one more point, not the subject.
_keep = [int(g) for g in COH_C if CV[g] > 0.0 and CV2[g] > 0.0]
_clog = {g: math.log(CV[g]) - math.log(CV2[g]) for g in _keep}
_am = [CV[g] for g in _keep] + [R_CAR["R"]]
_ad = [CV2[g] for g in _keep] + [R_CAR2["R"]]
_rm, _rd = rankvec(_am), rankvec(_ad)
_nn = float(len(_am))
_crank = {g: (_rm[i] - _rd[i]) / _nn for i, g in enumerate(_keep)}
_crank_car = (_rm[-1] - _rd[-1]) / _nn

ROWS = []
for g in _keep:
    _others_log = [_clog[h] for h in _keep if h != g]
    _others_rk = [_crank[h] for h in _keep if h != g]
    ROWS.append(dict(gi=g,
                     C_log=_clog[g], C_rank=_crank[g],
                     pct_log=pct_of(_clog[g], _others_log),
                     pct_rank=pct_of(_crank[g], _others_rk)))
DIS = [abs(r["pct_log"] - r["pct_rank"]) for r in ROWS]
D_CAR = abs(PCT_LOG_CAR - PC_RANK_CAR)
a["Q223b_1_disagreement_is_generic"] = dict(
    carrier_disagreement=D_CAR,
    carrier_pct_in_cohort_disagreement=pct_of(D_CAR, DIS),
    cohort_disagreement_median=float(np.median(DIS)),
    cohort_disagreement_p90=float(np.quantile(np.asarray(DIS), 0.90)),
    cohort_disagreement_max=float(np.max(DIS)),
    cohort_disagreement_mean=float(np.mean(DIS)),
    n_cohort_scored=len(ROWS),
    note="each cohort cell scored EXACTLY as the carrier was (leave-one-out "
         "against the other members), so the carrier's 0.1496 is placed in a "
         "distribution of disagreements that already exists in this cohort.")
log(f"[Q223b-1] carrier disagreement {D_CAR:.4f} at pct "
    f"{a['Q223b_1_disagreement_is_generic']['carrier_pct_in_cohort_disagreement']:.3f} "
    f"| cohort median {np.median(DIS):.4f} max {np.max(DIS):.4f}")

# ---------------- do the currencies rank the cohort the same way? -----------
_rho_cc = spearman_l([r["C_log"] for r in ROWS], [r["C_rank"] for r in ROWS])
_rho_pp = spearman_l([r["pct_log"] for r in ROWS], [r["pct_rank"] for r in ROWS])
# the compression test: |C_log| vs |C_rank| in the LOWER tail of C_log
_lo = sorted(ROWS, key=lambda r: r["C_log"])[:20]
a["Q223b_2_currency_relation"] = dict(
    spearman_C_log_vs_C_rank=_rho_cc,
    spearman_pct_log_vs_pct_rank=_rho_pp,
    lower20_mean_pct_log=float(np.mean([r["pct_log"] for r in _lo])),
    lower20_mean_pct_rank=float(np.mean([r["pct_rank"] for r in _lo])),
    lower20_mean_shift=float(np.mean([r["pct_rank"] - r["pct_log"] for r in _lo])),
    all_mean_shift=float(np.mean([r["pct_rank"] - r["pct_log"] for r in ROWS])),
    note="if the rank currency COMPRESSES the lower tail, the 20 most "
         "motor-specific cells by C_log sit systematically HIGHER in pct_rank "
         "than in pct_log, i.e. a positive lower20_mean_shift, while the "
         "cohort-wide mean shift stays ~0 by construction.")
log(f"[Q223b-2] rho(C_log,C_rank) {_rho_cc:.4f} | rho(pct,pct) {_rho_pp:.4f} "
    f"| lower-20 shift {a['Q223b_2_currency_relation']['lower20_mean_shift']:+.4f} "
    f"(all {a['Q223b_2_currency_relation']['all_mean_shift']:+.4f})")

# ---------------- would the branch have flipped? ----------------------------
a["Q223b_3_branch_under_companion"] = dict(
    registered_primary="C_log percentile vs COH_C",
    primary_pct=PCT_LOG_CAR, primary_branch="S_SPECIFIC",
    companion_pct=PC_RANK_CAR,
    companion_branch=("S_SPECIFIC" if PC_RANK_CAR <= PCT_BAR else "S_GENERIC"),
    bar=PCT_BAR,
    agree_in_direction=bool((PCT_LOG_CAR < PCT_LOG_MIR)
                            == (PC_RANK_CAR < PC_RANK_MIR)),
    note="DISCLOSED PLAINLY: the registered primary (declared in PREREG 0c "
         "BEFORE measurement) branches S_SPECIFIC; the companion currency does "
         "NOT clear the same 0.10 bar. Both order carrier BELOW mirror, so the "
         "DIRECTION is currency-invariant and the BINARY CALL is not.")
log(f"[Q223b-3] companion branch "
    f"{a['Q223b_3_branch_under_companion']['companion_branch']} "
    f"(direction agrees: {a['Q223b_3_branch_under_companion']['agree_in_direction']})")

a["rows"] = ROWS
a["limitations"] = [
    "POST-HOC: no registered bar, no prediction, no branch. Descriptive.",
    "The leave-one-out cohort is the carrier's own mass-matched cohort, which "
    "inherits L212's LOOSE mass match (log-spread 0.316 against a 0.15 bar).",
    "One cell is one percentile point in a 99-cell comparison set (L207).",
]
_stp2 = os.stat(f"{LAB}/l223/static.json")
assert (_stp2.st_size, _stp2.st_mtime_ns) == _fpp, "l223/static.json MUTATED"
a["runtime_s"] = time.time() - T0
json.dump(a, open(f"{LAB}/l223/addendum.json", "w"), indent=1)
log(f"[done] addendum -> {LAB}/l223/addendum.json")
