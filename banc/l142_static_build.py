"""Build l142_static.py: verbatim extraction slice of l135_run.py (lines
18-338: imports/constants through all Wc/Wb builds + edge-count pins) +
the L142 static tail (1110 edge enumeration within the cutwA window edge
set, tier split, in-edge provenance, eAll-vs-cutng25 CSR structural
identity). Zero rollouts, no RNG. Writes l142/static.json."""
import io

src = open("l135_run.py").read().splitlines(keepends=True)
# lines 18-338 (1-indexed) = imports .. Wb_* builds
slice_txt = "".join(src[17:338])
assert "Gf = torch.load" in slice_txt and "Wb_k5" in slice_txt
assert "def settle_states" not in slice_txt, "settle leaked into static"
assert 'B26 = list(range(3001, 3017))' in slice_txt

TAIL = '''

# ============ L142 static tail (edge-footprint enumeration) ============
# PREREG l142/PREREG.md registered BEFORE this computation's numbers are
# pinned into it (order: hypotheses first, feasibility numbers second).
GI_CARRIER = 1110            # DNp33-L, ng rank 25 (index 24)
GI_TWIN = 319                # DNpe025-R, ng rank 26 (index 25)
E_ARMS = ("eOutInt", "eOutMot", "eOutAll", "eIn", "eAll")

# rank re-pin (L131/L133 stored): rank 25 == 1110, rank 26 == 319
assert int(ng_desc[24]) == GI_CARRIER, (int(ng_desc[24]), "rank25 != 1110")
assert int(ng_desc[25]) == GI_TWIN, (int(ng_desc[25]), "rank26 != 319")

# cutwA keep + window edge mask (re-pin == l131 static)
keep_wA = keep_new.copy()
keep_wA[ng_desc[:24]] = False
n_wA = int(keep_wA.sum())
assert n_wA == S131["prefix"]["cutwA"]["n"], (n_wA, "wA n drift")
emask_wA = keep_wA[src_all] & keep_wA[dst_all]
n_edges_wA = int(emask_wA.sum())
assert n_edges_wA == cutk_pins["cutwA"]["edges"], (n_edges_wA, "wA edges drift")

# tier of dst (l135 lines 148-154 verbatim classes)
tier_dst = tier_of_dst

# ---- 1110's OUT-edges inside the cutwA window ----
out_sel = emask_wA & (src_all == GI_CARRIER)
out_int = out_sel & (tier_dst[dst_all] == "intrinsic")
out_mot = out_sel & (tier_dst[dst_all] == "motor_other")
out_oth = out_sel & ~np.isin(tier_dst[dst_all], ["intrinsic", "motor_other"])
absv = np.abs(vals_all)
total_dn_mass = float(cell_mass.sum())   # ladder mass convention (out-cord |vals|)


def _m(mask):
    return round(float(absv[mask].sum() / total_dn_mass), 6)


out_stats = dict(
    n_out_wA=int(out_sel.sum()),
    n_out_intrinsic=int(out_int.sum()), n_out_motor=int(out_mot.sum()),
    n_out_other=int(out_oth.sum()),
    other_tiers=sorted(set(tier_dst[dst_all][out_oth].tolist())),
    mass_out_all=_m(out_sel), mass_out_intrinsic=_m(out_int),
    mass_out_motor=_m(out_mot),
    raw_out_mass=float(outmass[GI_CARRIER]),
)
# cross-check vs l134 closure profile (80 out / 87% intrinsic / 13% motor)
assert out_stats["n_out_wA"] == 80, out_stats["n_out_wA"]
assert out_stats["n_out_intrinsic"] == 70 and out_stats["n_out_motor"] == 10
assert abs(out_stats["raw_out_mass"] - 183.96376182027785) < 1e-6

# ---- 1110's IN-edges inside the cutwA window ----
in_sel = emask_wA & (dst_all == GI_CARRIER)
in_mass_raw = float(absv[in_sel].sum())
in_src_gi = np.unique(src_all[in_sel])
in_src_sup = sorted(set(sup[in_src_gi].tolist()))
# are any in-edge sources members of the ng-58 family (rank provenance)?
rank_of = {int(g): i + 1 for i, g in enumerate(ng_desc)}
in_src_rank = {int(g): rank_of[int(g)] for g in in_src_gi if int(g) in rank_of}
in_stats = dict(
    n_in_wA=int(in_sel.sum()),
    mass_in_raw=round(in_mass_raw, 4),
    mass_in_frac_dn=round(in_mass_raw / total_dn_mass, 6),
    n_sources=int(len(in_src_gi)),
    src_super_class=in_src_sup,
    src_ng_ranks=in_src_rank,
)
# l137 closure census: 13 in-edges, all-DN sources — within-wA must be <= 13
assert 0 < in_stats["n_in_wA"] <= 13, in_stats["n_in_wA"]
assert in_src_sup == ["descending"], in_src_sup

# ---- per-arm edge-drop masks (global, applied INSIDE emask_wA) ----
e_drop = {
    "eOutInt": out_int,
    "eOutMot": out_mot,
    "eOutAll": out_sel,
    "eIn": in_sel,
    "eAll": out_sel | in_sel,
}
arm_edges = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert arm_edges["eOutAll"] == arm_edges["eOutInt"] + arm_edges["eOutMot"]
assert arm_edges["eAll"] == arm_edges["eOutAll"] + arm_edges["eIn"]
for a in E_ARMS:
    assert arm_edges[a] > 0, (a, "EMPTY edge set (STOP, L24 rule)")

# ---- build_e + structural identity: eAll EDGE SET == cutng25 EDGE SET ----
# (node-drop vs incident-edge-drop). Local CSR indices CANNOT match by
# construction (eAll keeps 1110 as an isolated node -> every local index
# above it shifts +1), so identity is on GLOBAL edge triples (src gi,
# dst gi, value) in the shared base edge-table order.
def build_e(keep, drop):
    emask = keep[src_all] & keep[dst_all] & ~drop
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    lsrc, ldst = loc[gsrc], loc[gdst]
    gsign_a2 = sign_all[gsrc]
    gsign_b2 = np.where(is_glut[gsrc], -np.abs(gsign_a2), gsign_a2)
    vals = (np.log1p(gcount) * gsign_b2).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([ldst, lsrc])).long(),
        torch.from_numpy(vals), (int(keep.sum()), int(keep.sum()))
    ).coalesce().to_sparse_csr()
    return W


We = {a: build_e(keep_wA, e_drop[a]) for a in E_ARMS}
arm_nnz = {a: int(We[a].values().numel()) for a in E_ARMS}
for a in E_ARMS:
    assert arm_nnz[a] == n_edges_wA - arm_edges[a], (a, "nnz != wA - dropped")
# THE structural cert: eAll (keep node, drop all incident edges) selects
# the SAME global edge positions as cutng25 (drop node) — src, dst, and
# per-edge values EXACT, in the shared base-table order.
keep_p25 = keep_new.copy()
keep_p25[ng_desc[:25]] = False
emask_eA = emask_wA & ~e_drop["eAll"]
emask_p25 = keep_p25[src_all] & keep_p25[dst_all]
csr_ident = bool(
    int(emask_eA.sum()) == int(emask_p25.sum())
    and np.array_equal(np.where(emask_eA)[0], np.where(emask_p25)[0]))
assert csr_ident, "eAll edge set != cutng25 edge set (STOP — build path broken)"
assert int(emask_eA.sum()) == cutk_pins["cutng25"]["edges"], (int(emask_eA.sum()),)

# af-denominator note: eAll keeps 1110 as an isolated node (n 21785) vs
# cutng25 (n 21784); isolated X ~ relu(BG+noise) ~ .02 < .05 threshold.
out_json = dict(
    design="L142 static: 1110 (DNp33-L) edge footprint inside the cutwA "
           "window edge set. Zero rollouts, no RNG. PREREG l142/PREREG.md "
           "FIRST. Structural law: node-drop == incident-edge-drop "
           "(eAll CSR == cutng25 CSR, indices+values EXACT).",
    carrier=dict(gi=GI_CARRIER, cell_type="DNp33", side="left",
                 nt="acetylcholine", ng_rank=25),
    twin=dict(gi=GI_TWIN, cell_type="DNpe025", side="right", ng_rank=26),
    window=dict(n_wA=n_wA, n_edges_wA=n_edges_wA,
                mass_removed_wA=cutk_pins["cutwA"]["mass_removed"],
                mass_removed_ng25=cutk_pins["cutng25"]["mass_removed"]),
    out_edges=out_stats,
    in_edges=in_stats,
    arm_edge_counts=arm_edges,
    arm_mass_frac_dn={a: _m(emask_wA & e_drop[a]) for a in E_ARMS},
    arm_nnz=arm_nnz,
    eall_csr_identical_to_cutng25=csr_ident,
    mass_note="out-arm fractions use the ladder convention (out-cord |vals| "
              "/ dn out-cord total); eIn/eAll fractions include in-edge "
              "mass on the same denominator for comparability (disclosed).",
)
import json as _json
import os as _os
_os.makedirs("l142", exist_ok=True)
_json.dump(out_json, open("l142/static.json", "w"), indent=1)
print(_json.dumps(out_json, indent=1))
print("L142 STATIC DONE")
'''

out = '"""L142 static: PREREG-first; verbatim l135 extraction slice\n(lines 18-338) + 1110 edge-footprint enumeration tail. Zero rollouts."""\n' + slice_txt + TAIL
open("l142_static.py", "w").write(out)
print("l142_static.py written", len(out), "chars")
import py_compile
py_compile.compile("l142_static.py", doraise=True)
print("py_compile OK")
