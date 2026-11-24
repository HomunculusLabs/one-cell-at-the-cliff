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
