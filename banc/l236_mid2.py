
# =========================== L236 MID2 =====================================
# CERT-236A (HALTING): every leaf of l219/static.json under the keys the
# VERBATIM slices have assigned so far, reproduced from THIS run's own o dict
# at FLOAT EQUALITY. The coverage bar is DERIVED from the artifact's own leaf
# count (L224: never guess a coverage bar) with a floor derived from the
# artifact's own core blocks.

_KEYS_A = list(o.keys())          # exactly what the slices assigned, derived
assert "identity_gates" in _KEYS_A, "SLICE R did not run (STOP)"
assert "predictions" not in _KEYS_A and "Q219_2_table" not in _KEYS_A


def _leaves236(a, b, path, out):
    """recursive float-equality compare; counts LEAVES."""
    if isinstance(a, dict):
        assert isinstance(b, dict), (path, "shape")
        assert set(a.keys()) == set(b.keys()), (path, "key set")
        for k in sorted(a.keys()):
            _leaves236(a[k], b[k], f"{path}/{k}", out)
    elif isinstance(a, (list, tuple)):
        assert isinstance(b, (list, tuple)) and len(a) == len(b), (path, "len")
        for i, (x, y) in enumerate(zip(a, b)):
            _leaves236(x, y, f"{path}[{i}]", out)
    else:
        if isinstance(a, float) or isinstance(b, float):
            assert float(a) == float(b), (path, a, b, "CERT-236A (STOP)")
        else:
            assert a == b, (path, a, b, "CERT-236A (STOP)")
        out[0] += 1


_n236a = [0]
for _k in _KEYS_A:
    assert _k in S219, (_k, "slice assigned a key the artifact lacks (STOP)")
    _leaves236(o[_k], S219[_k], _k, _n236a)
_n236a = _n236a[0]

# the DERIVED floor: leaf count of the artifact's own core blocks
_core236 = ["cert_f4", "gains", "csr_orientation", "pools", "cert_rew",
            "cert_178", "spectral", "cert_null", "cert_206", "cert_mv",
            "cert_left", "identity_gates"]
_fl = [0]
for _k in _core236:
    _leaves236(S219[_k], S219[_k], _k, _fl)
_FLOOR236 = _fl[0]
assert _n236a >= _FLOOR236, (_n236a, _FLOOR236, "CERT-236A coverage (STOP)")
log(f"[CERT-236A] GREEN {_n236a} stored L219 leaves reproduced by FLOAT "
    f"EQUALITY over {len(_KEYS_A)} keys (artifact-derived floor {_FLOOR236})")
o_cert236a = dict(n_checks=int(_n236a), floor=int(_FLOOR236),
                  n_keys=len(_KEYS_A), keys=sorted(_KEYS_A),
                  mode="float equality (==)", source="l219/static.json",
                  bar_derivation=("leaf count of the artifact's own core "
                                  "blocks, counted in code (L224)"))

# ---------------- CERT-236B (HALTING): the whole Q219_2_table --------------
# SLICE T + SLICE C are the parent's OWN cohort machinery, so this proves the
# decomp219 pipeline I am about to run on 1,253 cells reproduces the parent's
# 35 stored actor rows bit-for-bit.
_Q2T = dict(
    top10=TOP10, gini_contrib=GINI_C, gini_w=GINI_W, spearman_w_u1t=RHO_WU,
    top1_share=TOP10[0]["share_of_S"],
    top10_share=float(sum(t["share_of_S"] for t in TOP10)),
    n_distinct_targets=int(np.unique(T_CAR).size),
    carrier=COH219["carrier"], twin=COH219["twin"],
    family_median=dict(Q=_fmed("Q"), align=_fmed("align"),
                       gini_contrib=_fmed("gini_contrib"),
                       gini_w=_fmed("gini_w"),
                       spearman_w_u=_fmed("spearman_w_u"),
                       U=_fmed("U"), n_out=_fmed("n_out")),
    family_p05=dict(Q=float(np.percentile([COH219[k]["Q"] for k in _fam], 5)),
                    align=float(np.percentile([COH219[k]["align"]
                                               for k in _fam], 5))),
    family_p95=dict(Q=float(np.percentile([COH219[k]["Q"] for k in _fam], 95)),
                    align=float(np.percentile([COH219[k]["align"]
                                               for k in _fam], 95))),
    carrier_family_percentile=dict(
        Q=_fpct("Q", COH219["carrier"]["Q"]),
        align=_fpct("align", COH219["carrier"]["align"]),
        gini_contrib=_fpct("gini_contrib", GINI_C)),
    all_actors=COH219,
    selection_disclosure=S219["Q219_2_table"]["selection_disclosure"])
_n236b = [0]
_leaves236(_Q2T, S219["Q219_2_table"], "Q219_2_table", _n236b)
_n236b = _n236b[0]
assert len(COH219) == 35 and len(_fam) == 33, (len(COH219), "actor set (STOP)")
log(f"[CERT-236B] GREEN {_n236b} stored Q219_2_table leaves (35 actors x 9 "
    f"fields + the whole table) reproduced by FLOAT EQUALITY")
o_cert236b = dict(n_checks=int(_n236b), mode="float equality (==)",
                  source="l219/static.json Q219_2_table",
                  n_actors=35, n_family=33,
                  note=("SLICE T (l219_static.py 1459-1474) + SLICE C "
                        "(1476-1493) VERBATIM: the parent's own cohort loop "
                        "is what admits extending decomp219 to 1,253 cells"))
