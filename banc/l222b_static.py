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

# ===== L222 DECLARED MODIFICATION (replaces l212_head.py line 27) =====
# the parent wrote to {LAB}/l212; this card must never touch that dir.
OUT = f"{LAB}/l222"

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

# ===== L222 DECLARED MODIFICATION (replaces l212_head.py lines 117-122)
# the parent's graceful-blocker block WRITES into OUT/static.json.
# A HALTING assert is strictly stronger and writes nothing.
assert CAR_783 in idx_all and MIR_783 in idx_all, (
    "L222: a DNp33 match id is absent from the v783 proofread id set "
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
# ===== L222b DECLARED MODIFICATION (replaces l222_static.py lines 432-436) =====
# the inherited V_DEGENERATE escape is the prefix's ONLY write and it
# targets OUT/static.json = the PARENT artifact. A halting assert is
# strictly stronger (measured rel spread 4.11e-16) and writes nothing.
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

# ===================== L222 TAIL ==========================================
# Everything above this line is VERBATIM inherited source (l212_head.py sliced
# to CUT its blocker-writer and to re-point OUT, the three l207_tail.py
# function slices, and l212_tail.py lines 1-227 = L212's ENTIRE measurement
# pipeline). So CERT-783, CERT-L207, CERT-MV, CERT-GATE, the lam1 power
# iteration, the rescale NO-OP and L212's Q1/Q2/Q3 legs all re-ran as SOURCE
# before a single L222 number exists.

assert OUT.endswith("/l222") and os.path.isdir(OUT), (OUT, "OUT (STOP)")
PARENT_BRANCH = o.get("branch")
o["design"] = ("L222 the BILATERAL BREAK: is the v783 DNp33 left/right "
               "asymmetry a SYNAPSE-FLOOR artifact? static, zero rollouts.")
o["prereg"] = "l222/PREREG.md"
o["parent_branch_reproduced"] = PARENT_BRANCH
FLOORS = [1, 2, 4]
GAP_ARTIFACT_BAR = 0.10
GAP_SURVIVES_BAR = 0.15
# NOTE: l212_tail sets o["bars"] at line 254, BEYOND the inherited 1-227 slice,
# so this card builds its own bars dict rather than mutating a missing one.
o["bars"] = dict(gap_artifact=GAP_ARTIFACT_BAR, gap_survives=GAP_SURVIVES_BAR,
                 floors=FLOORS, pct_extreme=PCT_BAR, cohort_k=COHORT_K,
                 beta_L=BETA_L, degenerate_zero_frac=0.50,
                 power_rel_spread=1e-6)

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
del SUB2, SUB3, CV2, CV3

# ---------------- the floored builders -------------------------------------
assert float(w_syn.min()) >= 1.0, (float(w_syn.min()), "PREREG 0d (STOP)")
MOT_MASK = mot_all.copy()
assert int(MOT_MASK.sum()) == 110


def build_v783_floor(beta, pools, name, floor, dst_only=None):
    """build_v783's EXPRESSION with a syn_count floor on the COLLAPSED pair
    (PREREG 0a). dst_only=None -> GLOBAL floor; dst_only=mask -> the floor
    applies ONLY to edges landing in that mask (PREREG 0c LOCAL floor).
    floor == 1 with dst_only=None is a provable no-op (w_syn.min() >= 1)."""
    hit = w_syn >= float(floor)
    keep_e = hit if dst_only is None else (hit | (~dst_only[dst_all]))
    s_e = src_all[keep_e]
    d_e = dst_all[keep_e]
    _sa = sign_all[s_e]
    _sb = np.where(is_glut[s_e], -np.abs(_sa), _sa)
    ev = (np.log1p(w_syn[keep_e]) * _sb).astype(np.float64)
    vv = ev.copy()
    vv[vv < 0] *= beta
    jv = np.abs(vv)
    om = np.zeros(Nall)
    np.add.at(om, s_e, jv)
    loc = np.arange(Nall, dtype=np.int64)
    keep = np.ones(Nall, bool)
    pl = {pk: np.where(P)[0] for pk, P in pools.items()}
    return dict(name=name, keep=keep, loc=loc, n=Nall, n_edges=int(keep_e.sum()),
                jv=jv, rows=d_e, cols=s_e, pool_l=pl, floor=int(floor),
                pool_all=np.unique(np.concatenate([pl[k] for k in pl])), om=om,
                keep_e=keep_e, local=(dst_only is not None))


# CERT-FLOORGEN (HALTING): floor 1 == the verbatim build_v783, EXACTLY
_g1 = build_v783_floor(BETA_L, POOL_G, "gen_f1", 1)
n_fg = 0
for _k in ("jv", "rows", "cols", "om"):
    assert np.array_equal(_g1[_k], SUB[_k]), (_k, "CERT-FLOORGEN (STOP)")
    n_fg += 1
assert _g1["n_edges"] == SUB["n_edges"] == NEDGE, "CERT-FLOORGEN n_edges (STOP)"
n_fg += 1
for _pk in SUB["pool_l"]:
    assert np.array_equal(_g1["pool_l"][_pk], SUB["pool_l"][_pk]), (_pk, "STOP")
    n_fg += 1
assert bool(_g1["keep_e"].all()), "floor 1 is not a no-op mask (STOP)"
n_fg += 1
# and the LOCAL builder at floor 1 is the same no-op
_g1l = build_v783_floor(BETA_L, POOL_G, "gen_f1_local", 1, dst_only=MOT_MASK)
for _k in ("jv", "rows", "cols", "om"):
    assert np.array_equal(_g1l[_k], SUB[_k]), (_k, "CERT-FLOORGEN local (STOP)")
    n_fg += 1
o["cert_floorgen"] = dict(n_checks=n_fg, mode="EXACT array_equal (==)",
                          note="the generic floored builder at F=1 IS the "
                               "verbatim build_v783 (L207 CERT-GEN pattern)")
log(f"[CERT-FLOORGEN] GREEN {n_fg} exact array equalities")
del _g1, _g1l

# CERT-MONOTONE (HALTING): the floors are strictly NESTED and om is monotone
KEEPS = {F: (w_syn >= float(F)) for F in FLOORS}
OMS = {}
n_mon = 0
for F in FLOORS:
    _sf = build_v783_floor(BETA_L, POOL_G, f"mon_f{F}", F)
    OMS[F] = _sf["om"].copy()
    del _sf
for a, b in ((1, 2), (2, 4)):
    assert bool((KEEPS[b] <= KEEPS[a]).all()), (a, b, "not nested (STOP)")
    n_mon += 1
    assert bool((OMS[b] <= OMS[a] + 0.0).all()), (a, b, "om not monotone (STOP)")
    n_mon += 1
    assert int(KEEPS[b].sum()) < int(KEEPS[a].sum()), (a, b, "floor inert (STOP)")
    n_mon += 1
o["cert_monotone"] = dict(n_checks=n_mon, n_cells_checked=Nall,
                          mode="elementwise <= over 139255 cells / 15091983 edges",
                          note="a floor that is not nested is not a floor")
log(f"[CERT-MONOTONE] GREEN {n_mon} nesting/monotonicity gates over {Nall} cells")

# ---------------- leg (a): the ANATOMICAL per-target edge table -------------
_ct_full = np.array([""] * Nall, dtype=object)
_nv_full = np.array([""] * Nall, dtype=object)
_sd_full = np.array([""] * Nall, dtype=object)
_ct_full[ann_gi] = ctype
_nv_full[ann_gi] = nerve
_sd_full[ann_gi] = side
ACT = (("carrier", GI_CARRIER), ("mirror", GI_MIR))
EDGE_TBL = {}
OUTDEG = {}
for _nm, _gi in ACT:
    _sel = np.where((src_all == _gi) & MOT_MASK[dst_all])[0]
    rows_t = []
    for _e in _sel:
        _d = int(dst_all[_e])
        rows_t.append(dict(
            dst_gi=_d, dst_root_id=str(int(ids_all[_d])),
            cell_type=str(_ct_full[_d]), nerve=str(_nv_full[_d]),
            side=str(_sd_full[_d]),
            syn_count=float(w_syn[_e]), log1p_w=float(np.log1p(w_syn[_e])),
            survives_f2=bool(w_syn[_e] >= 2.0),
            survives_f4=bool(w_syn[_e] >= 4.0)))
    rows_t.sort(key=lambda r: (-r["syn_count"], r["dst_gi"]))
    EDGE_TBL[_nm] = rows_t
    _all_out = np.where(src_all == _gi)[0]
    _ws = w_syn[_all_out]
    OUTDEG[_nm] = dict(
        n_out_edges=int(len(_all_out)),
        n_out_edges_f2=int((_ws >= 2.0).sum()),
        n_out_edges_f4=int((_ws >= 4.0).sum()),
        syn_min=float(_ws.min()), syn_median=float(np.median(_ws)),
        syn_max=float(_ws.max()),
        frac_edges_syn1=float((_ws == 1.0).mean()),
        frac_edges_below4=float((_ws < 4.0).mean()),
        out_mass_f1=float(OMS[1][_gi]), out_mass_f2=float(OMS[2][_gi]),
        out_mass_f4=float(OMS[4][_gi]),
        mass_retention_f4=float(OMS[4][_gi] / OMS[1][_gi]),
        n_direct_motor_edges=int(len(EDGE_TBL[_nm])))
o["Qa_anatomical"] = dict(
    edge_table=EDGE_TBL, out_degree=OUTDEG,
    readout="the 110-cell v783 super_class==motor set (5 nerve pools)",
    note="COLLAPSED-pair syn_count per PREREG 0a: one synapse TOTAL across all "
         "neuropils, which is the reading that makes 'at the detection floor' "
         "correct.")
log(f"[leg a] carrier direct motor edges {len(EDGE_TBL['carrier'])} | "
    f"mirror {len(EDGE_TBL['mirror'])} "
    f"| mirror syns {[r['syn_count'] for r in EDGE_TBL['mirror']]}")

# ---------------- the per-floor legs ---------------------------------------
DEG = None


def floor_leg(F, beta, dst_only, tag):
    """one floor x one beta: substrate report + both actors + both cohorts."""
    global DEG
    SUBF = build_v783_floor(beta, POOL_G, tag, F, dst_only=dst_only)
    # CERT-MV re-run AT THIS FLOOR (never assumed from floor 1)
    _r = np.random.default_rng(22200 + F)
    nmv = 0
    for _p in range(3):
        if _p == 0:
            _x = np.zeros(SUBF["n"]); _x[GI_CARRIER] = 1.0
        elif _p == 1:
            _x = np.zeros(SUBF["n"]); _x[GI_MIR] = 1.0
        else:
            _x = _r.random(SUBF["n"])
        assert np.array_equal(mv_slow(SUBF, _x), mv_fast(SUBF, _x)), (tag, _p)
        nmv += 1
    # CERT-GATE re-run AT THIS FLOOR: fast kernels == verbatim l207 functions
    ngt = 0
    for _nm, _gi in ACT:
        _a = reach_sub(int(SUBF["loc"][_gi]), SUBF, 2)
        _b = reach_fast(int(SUBF["loc"][_gi]), SUBF, 2)
        for _d in (1, 2):
            for _pk in SUBF["pool_l"]:
                assert _a[_d][_pk] == _b[_d][_pk], (tag, _nm, _d, _pk, "STOP")
                ngt += 1
    _l1, _s1 = power_iter_sub(SUBF, SUBF["jv"], iters=12)
    _l2, _s2 = power_iter_fast(SUBF, SUBF["jv"], iters=12)
    assert _l1 == _l2 and _s1 == _s2, (tag, "power gate (STOP)")
    ngt += 2
    LAMF, SPRF = power_iter_fast(SUBF, SUBF["jv"], 400)
    if SPRF >= 1e-6:
        DEG = f"F_DEGENERATE_POWER ({tag} rel spread {SPRF})"
    rc = Rfast(SUBF, GI_CARRIER, LAMF)
    rm = Rfast(SUBF, GI_MIR, LAMF)
    # card-required halting assert: the carrier has no direct motor edge to lose
    assert rc["P1"] == 0.0, (tag, rc["P1"], "carrier P1 != 0 (STOP)")
    omc = float(SUBF["om"][GI_CARRIER])
    omm = float(SUBF["om"][GI_MIR])
    _elig = np.where(dn_all)[0]
    _elig = int((SUBF["om"][_elig] > 0).sum())
    base = dict(floor=int(F), beta_L=float(beta),
                local_floor=bool(dst_only is not None),
                n_edges=int(SUBF["n_edges"]),
                edge_retention_vs_f1=float(SUBF["n_edges"] / NEDGE),
                lam1=float(LAMF), rel_spread_last6=float(SPRF),
                carrier_m_out=omc, mirror_m_out=omm,
                carrier_P1=rc["P1"], mirror_P1=rm["P1"],
                carrier_P2=rc["P2"], mirror_P2=rm["P2"],
                cohort_eligible_dn=_elig,
                P1_per_pool_carrier=reach_fast(int(SUBF["loc"][GI_CARRIER]),
                                               SUBF, 1)[1],
                P1_per_pool_mirror=reach_fast(int(SUBF["loc"][GI_MIR]),
                                              SUBF, 1)[1],
                per_pool_carrier=reach_fast(int(SUBF["loc"][GI_CARRIER]),
                                            SUBF, 2)[2],
                per_pool_mirror=reach_fast(int(SUBF["loc"][GI_MIR]),
                                           SUBF, 2)[2],
                cert_mv_checks=nmv, cert_gate_checks=ngt)
    # ---- the REGISTERED F_DEGENERATE_ACTOR escape --------------------------
    # An actor with zero surviving out-mass has no R, no cohort (matched_cohort
    # takes math.log of its out-mass) and no percentile: the card's branch
    # table is UNREACHABLE at this floor, which is the escape's whole point.
    if omc <= 0.0 or omm <= 0.0:
        DEG = (f"F_DEGENERATE_ACTOR ({tag}: carrier om {omc} mirror om {omm} "
               f"- no surviving out-edges, so R / cohort / percentile do not "
               f"exist at this floor)")
        L = dict(base)
        L["degenerate"] = True
        L["degenerate_reason"] = DEG
        for _k in ("carrier_R", "mirror_R", "carrier_pct", "mirror_pct", "gap",
                   "ratio_R", "ratio_P2", "gap_union", "gap_cohC",
                   "pct_carrier_union", "pct_mirror_union",
                   "pct_carrier_cohC", "pct_mirror_cohC",
                   "cohort_jaccard_carrier_vs_f1",
                   "cohort_jaccard_mirror_vs_f1"):
            L[_k] = None
        L["ratio_m_out"] = (float(omm / omc) if omc > 0 else None)
        log(f"[{tag}] DEGENERATE edges {L['n_edges']} "
            f"({L['edge_retention_vs_f1']:.4f}) lam1 {LAMF:.4f} | om car {omc} "
            f"mir {omm} | eligible DN {_elig} of 1303 | P2 car {rc['P2']:.4f} "
            f"mir {rm['P2']:.4f}")
        del SUBF
        return L
    cc = matched_cohort(SUBF, GI_CARRIER)
    cm = matched_cohort(SUBF, GI_MIR)
    cu = sorted(set(cc) | set(cm))
    cv = {}
    for _i, _g in enumerate(cu):
        cv[_g] = Rfast(SUBF, _g, LAMF)["R"]
    L = leg(rc, rm, cc, cm, cv, SUBF)
    if L["cohort_zero_frac_carrier"] > 0.50:
        DEG = f"F_DEGENERATE_COHORT ({tag} zero frac)"
    # cohort-COMMON companions (PREREG 0b): one distribution, both actors
    _vu = [cv[g] for g in cu]
    _vc = [cv[g] for g in cc]
    L["pct_carrier_union"] = pct_of(rc["R"], _vu)
    L["pct_mirror_union"] = pct_of(rm["R"], _vu)
    L["gap_union"] = abs(L["pct_mirror_union"] - L["pct_carrier_union"])
    L["pct_carrier_cohC"] = pct_of(rc["R"], _vc)
    L["pct_mirror_cohC"] = pct_of(rm["R"], _vc)
    L["gap_cohC"] = abs(L["pct_mirror_cohC"] - L["pct_carrier_cohC"])
    # cohort-FREE companions
    L["ratio_R"] = float(rm["R"] / rc["R"]) if rc["R"] > 0 else None
    L["ratio_P2"] = float(rm["P2"] / rc["P2"]) if rc["P2"] > 0 else None
    L["ratio_m_out"] = float(rm["m_out"] / rc["m_out"])
    # the registered gap
    L["gap"] = abs(L["mirror_pct"] - L["carrier_pct"])
    # substrate report (card-required)
    L.update(base)
    L["degenerate"] = False
    L["cohort_jaccard_carrier_vs_f1"] = float(
        len(set(cc) & set(COH_C)) / len(set(cc) | set(COH_C)))
    L["cohort_jaccard_mirror_vs_f1"] = float(
        len(set(cm) & set(COH_M)) / len(set(cm) | set(COH_M)))
    log(f"[{tag}] edges {L['n_edges']} ({L['edge_retention_vs_f1']:.4f}) "
        f"lam1 {LAMF:.4f} | car pct {L['carrier_pct']:.3f} mir pct "
        f"{L['mirror_pct']:.3f} GAP {L['gap']:.3f} | union gap "
        f"{L['gap_union']:.3f} | ratio_R {L['ratio_R']:.4f} "
        f"| P1 car {rc['P1']:.6f} mir {rm['P1']:.6f} "
        f"| J_car {L['cohort_jaccard_carrier_vs_f1']:.3f}")
    del SUBF
    return L

# ===================== L222b ADDENDUM TAIL =================================
# POST-HOC, declared as such, no branch depends on it. Everything above is the
# VERBATIM l222_static.py prefix (lines 1-906), so CERT-783 / CERT-L207 /
# CERT-212 (139) / CERT-FLOORGEN (15) / CERT-MONOTONE (6) / CERT-MV /
# CERT-GATE all re-ran before this line.
#
# QUESTION: l222's LOCAL floor deleted ~6,951 weak edges into the motor
# readout at once. Is the mirror's ONE direct motor synapse itself causally
# relevant to its percentile, or was L212's P1 = log1p(1) a coincidence
# sitting next to the finding?

oa = {}
oa["design"] = ("L222b: delete EXACTLY the mirror's single direct motor edge "
                "and nothing else. POST-HOC addendum to L222.")
oa["parent"] = dict(script="l222_static.py", prefix_lines=906,
                    note="generated as a literal PREFIX slice; the parent's "
                         "static.json is never opened for writing.")

# the target edge, re-derived from the raw pair arrays (not read from the json)
_tgt = np.where((src_all == GI_MIR) & MOT_MASK[dst_all])[0]
assert len(_tgt) == 1, (len(_tgt), "expected exactly ONE mirror motor edge")
E_IDX = int(_tgt[0])
assert float(w_syn[E_IDX]) == 1.0, (float(w_syn[E_IDX]), "not one synapse")
_car_tgt = np.where((src_all == GI_CARRIER) & MOT_MASK[dst_all])[0]
assert len(_car_tgt) == 0, (len(_car_tgt), "carrier has a direct motor edge?")
oa["target_edge"] = dict(
    edge_index=E_IDX, src_gi=int(src_all[E_IDX]), dst_gi=int(dst_all[E_IDX]),
    syn_count=float(w_syn[E_IDX]), dst_root_id=str(int(ids_all[dst_all[E_IDX]])),
    dst_cell_type=str(_ct_full[dst_all[E_IDX]]),
    dst_nerve=str(_nv_full[dst_all[E_IDX]]), dst_side=str(_sd_full[dst_all[E_IDX]]))
log(f"[target] {oa['target_edge']}")


def build_drop(beta, pools, name, drop_idx):
    """build_v783's EXPRESSION with an explicit edge-index DROP SET.
    drop_idx empty is a provable no-op, which is how this builder is gated."""
    keep_e = np.ones(len(w_syn), bool)
    keep_e[np.asarray(drop_idx, dtype=np.int64)] = False
    s_e = src_all[keep_e]
    d_e = dst_all[keep_e]
    _sa = sign_all[s_e]
    _sb = np.where(is_glut[s_e], -np.abs(_sa), _sa)
    ev = (np.log1p(w_syn[keep_e]) * _sb).astype(np.float64)
    vv = ev.copy()
    vv[vv < 0] *= beta
    jv = np.abs(vv)
    om = np.zeros(Nall)
    np.add.at(om, s_e, jv)
    pl = {pk: np.where(P)[0] for pk, P in pools.items()}
    return dict(name=name, keep=np.ones(Nall, bool),
                loc=np.arange(Nall, dtype=np.int64), n=Nall,
                n_edges=int(keep_e.sum()), jv=jv, rows=d_e, cols=s_e,
                pool_l=pl, om=om,
                pool_all=np.unique(np.concatenate([pl[k] for k in pl])))


# CERT-DROPGEN (HALTING): the empty drop set IS the verbatim build_v783
_g0 = build_drop(BETA_L, POOL_G, "drop_none", [])
n_dg = 0
for _k in ("jv", "rows", "cols", "om"):
    assert np.array_equal(_g0[_k], SUB[_k]), (_k, "CERT-DROPGEN (STOP)")
    n_dg += 1
assert _g0["n_edges"] == NEDGE, "CERT-DROPGEN n_edges (STOP)"
n_dg += 1
for _pk in SUB["pool_l"]:
    assert np.array_equal(_g0["pool_l"][_pk], SUB["pool_l"][_pk]), (_pk, "STOP")
    n_dg += 1
oa["cert_dropgen"] = dict(n_checks=n_dg, mode="EXACT array_equal (==)")
log(f"[CERT-DROPGEN] GREEN {n_dg} exact array equalities")
del _g0

SUBD = build_drop(BETA_L, POOL_G, "drop_one_synapse", [E_IDX])
assert SUBD["n_edges"] == NEDGE - 1, (SUBD["n_edges"], "drop count (STOP)")
# The drop must move EXACTLY ONE cell's out-mass, by log1p(1). But om is a
# np.add.at accumulation over 31 edges, so the DIFFERENCE OF TWO SUMS is not
# bit-identical to the removed summand (the L218 law: a mathematical no-op is
# not a floating-point no-op). The bar is DERIVED from the operand's own ulp,
# never fixed in advance (the L216 law).
_d_om = SUB["om"] - SUBD["om"]
_want = math.log1p(1.0)
_ulp = float(np.spacing(float(SUB["om"][GI_MIR])))
_err = abs(float(_d_om[GI_MIR]) - _want)
assert _err <= 4.0 * _ulp, (_err, _ulp, "drop mass (STOP)")
assert int((_d_om != 0.0).sum()) == 1, (int((_d_om != 0.0).sum()),
                                        "the drop touched more than one cell")
oa["cert_drop_mass"] = dict(d_om_mirror=float(_d_om[GI_MIR]), want=_want,
                            abs_err=_err, ulp_of_om=_ulp,
                            err_in_ulp=(_err / _ulp), bar_ulp=4.0,
                            note="difference-of-sums vs summand: bar derived "
                                 "from np.spacing(om), not fixed (L216/L218)")
log(f"[drop] exactly one edge, one cell's out-mass moved by "
    f"{float(_d_om[GI_MIR]):.15f} vs log1p(1) {_want:.15f} "
    f"(err {_err:.3e} = {_err/_ulp:.2f} ulp of om)")

LAMD, SPRD = power_iter_fast(SUBD, SUBD["jv"], 400)
assert SPRD < 1e-6, (SPRD, "power iteration (STOP)")
RCD = Rfast(SUBD, GI_CARRIER, LAMD)
RMD = Rfast(SUBD, GI_MIR, LAMD)
assert RCD["P1"] == 0.0, (RCD["P1"], "carrier P1 (STOP)")
CCD = matched_cohort(SUBD, GI_CARRIER)
CMD = matched_cohort(SUBD, GI_MIR)
CUD = sorted(set(CCD) | set(CMD))
CVD = {g: Rfast(SUBD, g, LAMD)["R"] for g in CUD}
LD = leg(RCD, RMD, CCD, CMD, CVD, SUBD)
_vu = [CVD[g] for g in CUD]
LD["pct_carrier_union"] = pct_of(RCD["R"], _vu)
LD["pct_mirror_union"] = pct_of(RMD["R"], _vu)
LD["gap_union"] = abs(LD["pct_mirror_union"] - LD["pct_carrier_union"])
LD["gap"] = abs(LD["mirror_pct"] - LD["carrier_pct"])
LD["ratio_R"] = float(RMD["R"] / RCD["R"])
LD["ratio_P2"] = float(RMD["P2"] / RCD["P2"])
LD["lam1"] = float(LAMD)
LD["rel_spread_last6"] = float(SPRD)
LD["n_edges"] = int(SUBD["n_edges"])
LD["cohort_jaccard_carrier_vs_f1"] = float(
    len(set(CCD) & set(COH_C)) / len(set(CCD) | set(COH_C)))
LD["cohort_jaccard_mirror_vs_f1"] = float(
    len(set(CMD) & set(COH_M)) / len(set(CMD) | set(COH_M)))
oa["drop_one"] = LD

# the paired comparison against the UNFLOORED parent state (CERT-212-certified)
BASE = dict(carrier_pct=o["Q1_primary"]["carrier_pct"],
            mirror_pct=o["Q1_primary"]["mirror_pct"],
            gap=abs(o["Q1_primary"]["mirror_pct"] - o["Q1_primary"]["carrier_pct"]),
            carrier_R=o["Q1_primary"]["carrier_R"],
            mirror_R=o["Q1_primary"]["mirror_R"],
            carrier_P1=o["Q1_primary"]["carrier_P1"],
            mirror_P1=o["Q1_primary"]["mirror_P1"],
            carrier_P2=o["Q1_primary"]["carrier_P2"],
            mirror_P2=o["Q1_primary"]["mirror_P2"],
            ratio_R=float(o["Q1_primary"]["mirror_R"] / o["Q1_primary"]["carrier_R"]),
            ratio_P2=float(o["Q1_primary"]["mirror_P2"] / o["Q1_primary"]["carrier_P2"]),
            lam1=float(LAM1))
oa["baseline_unfloored"] = BASE
oa["delta"] = dict(
    d_mirror_pct=LD["mirror_pct"] - BASE["mirror_pct"],
    d_carrier_pct=LD["carrier_pct"] - BASE["carrier_pct"],
    d_gap=LD["gap"] - BASE["gap"],
    d_ratio_R=LD["ratio_R"] - BASE["ratio_R"],
    d_ratio_P2=LD["ratio_P2"] - BASE["ratio_P2"],
    d_mirror_P2=LD["mirror_P2"] - BASE["mirror_P2"],
    d_mirror_P1=LD["mirror_P1"] - BASE["mirror_P1"],
    d_lam1=float(LAMD) - BASE["lam1"],
    frac_of_mirror_P2_lost=float((BASE["mirror_P2"] - LD["mirror_P2"])
                                 / BASE["mirror_P2"]))
# the registered-style read: does deleting the one synapse CLOSE the break?
_closes = bool(LD["gap"] < BASE["gap"] and LD["ratio_R"] < BASE["ratio_R"])
oa["verdict"] = dict(
    one_synapse_closes_the_break=_closes,
    direction=("the gap MOVED TOWARD symmetry" if LD["gap"] < BASE["gap"]
               else "the gap WIDENED or held"),
    reading=("L212's P1 = log1p(1) coincidence is NOT the mechanism of the "
             ".020 / .250 split: deleting exactly that synapse does not close "
             "it." if not _closes else
             "the single synapse is causally load-bearing for the split."))
oa["limitations"] = [
    "POST-HOC: this leg was not in L222's PREREG; it is reported as "
    "DESCRIPTIVE and no L222 branch depends on it.",
    "A one-edge deletion is a static anatomical perturbation, not a lesion "
    "experiment: no settle, no seed, no rollouts (L164).",
    "The mirror's depth-1 motor arrival is carried ENTIRELY by this edge, so "
    "d_mirror_P1 is exactly -log1p(1) BY CONSTRUCTION and is a gate on the "
    "drop, never a finding.",
    "Every L222 and L212 limitation is inherited verbatim.",
]
log(f"[DROP] gap {BASE['gap']:.3f} -> {LD['gap']:.3f} "
    f"(d {oa['delta']['d_gap']:+.3f}) | ratio_R {BASE['ratio_R']:.4f} -> "
    f"{LD['ratio_R']:.4f} | mirror pct {BASE['mirror_pct']:.3f} -> "
    f"{LD['mirror_pct']:.3f} | mirror P2 {BASE['mirror_P2']:.4f} -> "
    f"{LD['mirror_P2']:.4f} ({oa['delta']['frac_of_mirror_P2_lost']*100:.3f}% lost)")
log(f"[DROP] closes_the_break={_closes}")
oa["parent_gates_reran"] = dict(cert_212=o["cert_212"]["n_checks"],
                                cert_floorgen=o["cert_floorgen"]["n_checks"],
                                cert_monotone=o["cert_monotone"]["n_checks"],
                                cert_783=o["cert_783"]["n_checks"],
                                cert_mv=o["cert_mv"]["n_checks"],
                                cert_gate=o["cert_gate"]["n_checks"],
                                cert_l207=o["cert_l207"]["n_checks"])
oa["runtime_s"] = time.time() - T0
json.dump(oa, open(f"{OUT}/addendum.json", "w"), indent=1)
log(f"[done] addendum {oa['runtime_s']:.1f}s -> {OUT}/addendum.json")
