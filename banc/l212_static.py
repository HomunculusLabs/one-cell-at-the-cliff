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
OUT = f"{LAB}/l212"
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
# a missing id is a valid journaled blocker, not a worked-around one
if CAR_783 not in idx_all or MIR_783 not in idx_all:
    o["blocker"] = ("match id absent from the v783 proofread id set: "
                    f"carrier {CAR_783 in idx_all} mirror {MIR_783 in idx_all}")
    json.dump(o, open(f"{OUT}/static.json", "w"), indent=1)
    sys.exit("BLOCKER: match id not in v783 id set")
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
if SPR >= 1e-6:
    o["branch"] = "V_DEGENERATE"
    o["degenerate_reason"] = f"power iteration rel spread {SPR}"
    json.dump(o, open(f"{OUT}/static.json", "w"), indent=1)
    sys.exit("V_DEGENERATE: power iteration did not converge")
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

# ---------------- predictions ----------------------------------------------
P = {}
P["Q212_1"] = dict(registered="V_AVOIDS", measured=BRANCH,
                   correct=bool(BRANCH == "V_AVOIDS"))
P["Q212_2"] = dict(registered="mirror_pct <= carrier_pct AND mirror low",
                   measured=dict(mirror_pct=PRI["mirror_pct"],
                                 carrier_pct=PRI["carrier_pct"]),
                   correct=bool(PRI["mirror_pct"] <= PRI["carrier_pct"]
                                and PRI["mirror_pct"] <= PCT_BAR))
P["Q212_3"] = dict(registered="secondary pct > primary pct",
                   measured=dict(secondary=SEC["carrier_pct"],
                                 primary=PRI["carrier_pct"]),
                   correct=bool(SEC["carrier_pct"] > PRI["carrier_pct"]))
P["Q212_4"] = dict(registered="|d carrier_pct| <= 0.10 under BETA_L=1",
                   measured=ROB["d_carrier_pct_vs_primary"],
                   correct=bool(abs(ROB["d_carrier_pct_vs_primary"]) <= 0.10))
P["Q212_5"] = dict(registered="cohort log-mass spread <= 0.15 both actors",
                   measured=dict(carrier=PRI["mass_match_logspread_carrier"],
                                 mirror=PRI["mass_match_logspread_mirror"]),
                   correct=bool(PRI["mass_match_logspread_carrier"] <= 0.15
                                and PRI["mass_match_logspread_mirror"] <= 0.15))
o["predictions"] = P
o["n_predictions_correct"] = int(sum(1 for v in P.values() if v["correct"]))
log(f"[predictions] {o['n_predictions_correct']} of 5")

o["bars"] = dict(pct_extreme=PCT_BAR, cohort_k=COHORT_K, beta_L=BETA_L,
                 degenerate_zero_frac=0.50)
o["comparators_L207"] = dict(
    G0_closure_carrier_pct=S207["Q1a_carrier_by_substrate"]["G0_closure"]["carrier_pct"],
    G1_cutwA_carrier_pct=S207["Q1a_carrier_by_substrate"]["G1_cutwA"]["carrier_pct"],
    F4_f4wA_carrier_pct=S207["Q1a_carrier_by_substrate"]["F4_f4wA"]["carrier_pct"],
    mirror_leg_closure=dict(
        mirror_pct=S207["Q2_mirror"]["per_substrate"]["G0_closure"]["mirror_pct"],
        carrier_pct=S207["Q2_mirror"]["per_substrate"]["G0_closure"]["carrier_pct"]),
    note="BANC leg-motor readout. NOT the same object as this card's readout; "
         "listed so the reader can see the direction, never as a test.")
o["limitations"] = [
    "EXPLORATORY (L78 non-transport law): the readout, the volume AND the body "
    "segment all changed at once, so neither direction can confirm or refute "
    "L207's leg-motor finding.",
    "ANATOMICAL leg only: no row mask, no settle, no seed, no rollouts - "
    "wiring geometry, NOT an operating point (L164).",
    "Operator powers are walks WITH revisits, not paths.",
    "v783 carries NO synapse floor, so the closest BANC comparator is the "
    "closure/cutwA substrate, not f4wA.",
    "The readout is 110 cells against BANC's 303-cell 20-pool readout, and "
    "head motor neurons are not leg motor neurons: a smaller, functionally "
    "different terminal set.",
    "A descending neuron's real output LEAVES this volume; its in-brain "
    "out-edges are not its functional output. This is the deepest limit of "
    "the whole v783 leg and it is why the card is exploratory.",
    "MASS-MATCHED COHORT percentile (k=100 nearest v783 descending cells in "
    "log out-mass), NOT the l169c degree-neutral rewire null - different "
    "nulls, never compared as if they were the same (L207).",
    "v783 'unknown' top_nt is scored at the build_graph_banc default "
    "magnitude 0.3; BANC's NT release has no unknown class.",
    "No BANC pin chain is inherited (the BANC head is not sliced because it "
    "loads banc_graph.pt); provenance rests on CERT-783 instead.",
]
o["pins"] = "ALL GREEN"
o["runtime_s"] = time.time() - T0
json.dump(o, open(f"{OUT}/static.json", "w"), indent=1)
log(f"[done] {o['runtime_s']:.1f}s -> {OUT}/static.json  branch={BRANCH}")
