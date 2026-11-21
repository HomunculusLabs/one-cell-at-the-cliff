"""L145 static build: emit l145_static.py from l142_static.py's verbatim
extraction slice + a new L145 tail (motor-edge dose enumeration).
Count-asserted, drift-guarded (L142 builder laws)."""
import re

SRC = open("l142_static.py").read()
MARK = "# ---- 1110's OUT-edges inside the cutwA window ----"
i = SRC.index(MARK)
head = SRC[:i]

TAIL = '''# ---- L145: motor-edge DOSE enumeration (top-5 / bottom-5 by mass) ----
# out/in masks recomputed exactly as L142 (verbatim forms)
tier_dst = tier_of_dst
out_sel = emask_wA & (src_all == GI_CARRIER)
out_int = out_sel & (tier_dst[dst_all] == "intrinsic")
out_mot = out_sel & (tier_dst[dst_all] == "motor_other")
absv = np.abs(vals_all)
total_dn_mass = float(cell_mass.sum())   # ladder mass convention


def _m(mask):
    return round(float(absv[mask].sum() / total_dn_mass), 6)


assert int(out_sel.sum()) == 80 and int(out_int.sum()) == 70
assert int(out_mot.sum()) == 10, int(out_mot.sum())
in_sel = emask_wA & (dst_all == GI_CARRIER)
assert int(in_sel.sum()) == 13, int(in_sel.sum())

# rank the 10 motor edges by |vals| DESC, tiebreak global edge pos ASC
mot_pos = np.where(out_mot)[0]
mot_ord = mot_pos[np.lexsort((mot_pos, -absv[mot_pos]))]
mot_w = absv[mot_ord]
mot_dst = dst_all[mot_ord]
mot_cnt = w_syn[mot_ord]
# per-edge destination identity for the dose table
ann_by_gi = ann.set_index("gi")
def _ident(g):
    try:
        r = ann_by_gi.loc[int(g)]
        return str(r.get("cell_type", "") or "")
    except Exception:
        return "?"
mot_table = [dict(pos=int(p), dst_gi=int(g), w=round(float(w), 6),
                  syn=int(c), dst_type=_ident(g))
             for p, g, w, c in zip(mot_pos, mot_dst, mot_w, mot_cnt)]
tie_note = "mass DESC, tiebreak global-pos ASC" if len(set(mot_w.tolist())) < 10 \\
    else "all 10 masses distinct"
top5 = np.zeros_like(emask_wA)
top5[mot_ord[:5]] = True
bot5 = np.zeros_like(emask_wA)
bot5[mot_ord[5:]] = True
assert int(top5.sum()) == 5 and int(bot5.sum()) == 5
# subset law: top5 | bot5 == eOutMot edge set, EXACT positions
assert np.array_equal(np.where(top5 | bot5)[0], np.where(out_mot)[0]), \\
    "top5|bot5 != eOutMot (STOP)"

E_ARMS = ("eOutMot", "eMotTop5", "eMotBot5", "eMotIn")
e_drop = {"eOutMot": out_mot, "eMotTop5": top5, "eMotBot5": bot5,
          "eMotIn": out_mot | in_sel}
arm_edges = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert arm_edges == {"eOutMot": 10, "eMotTop5": 5, "eMotBot5": 5,
                     "eMotIn": 23}, arm_edges
for a in E_ARMS:
    assert arm_edges[a] > 0, (a, "EMPTY edge set (STOP, L24 rule)")


def build_e(keep, drop):
    emask = keep[src_all] & keep[dst_all] & ~drop
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    gsign_a2 = sign_all[gsrc]
    gsign_b2 = np.where(is_glut[gsrc], -np.abs(gsign_a2), gsign_a2)
    vals = (np.log1p(gcount) * gsign_b2).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([loc[gdst], loc[gsrc]])).long(),
        torch.from_numpy(vals), (int(keep.sum()), int(keep.sum()))
    ).coalesce().to_sparse_csr()
    return W


We = {a: build_e(keep_wA, e_drop[a]) for a in E_ARMS}
arm_nnz = {a: int(We[a].values().numel()) for a in E_ARMS}
for a in E_ARMS:
    assert arm_nnz[a] == n_edges_wA - arm_edges[a], (a, "nnz mismatch")
# structural cross-check vs L142 pins: eOutMot arm nnz must equal l142's
assert arm_nnz["eOutMot"] == 644167, arm_nnz["eOutMot"]

out_json = dict(
    design="L145 static: motor-edge DOSE (top-5/bottom-5 by |vals|) + "
           "eMotIn combo on the cutwA node set. Zero rollouts, no RNG. "
           "PREREG l145/PREREG.md FIRST. Subset law pinned: top5|bot5 == "
           "eOutMot edge positions EXACT.",
    carrier=dict(gi=GI_CARRIER, cell_type="DNp33", side="left",
                 nt="acetylcholine", ng_rank=25),
    motor_edges_ranked=mot_table,
    rank_rule=tie_note,
    mass_split=dict(
        mot_all=_m(out_mot), mot_top5=_m(top5), mot_bot5=_m(bot5),
        eMotIn=_m(e_drop["eMotIn"]),
        top5_share_of_mot=round(float(absv[top5].sum() / absv[out_mot].sum()), 4),
    ),
    arm_edge_counts=arm_edges,
    arm_mass_frac_dn={a: _m(emask_wA & e_drop[a]) for a in E_ARMS},
    arm_nnz=arm_nnz,
    mass_note="ladder convention (out-cord |vals| / dn out-cord total); "
              "eMotIn includes in-edge mass on the same denominator "
              "(disclosed, l142 form).",
)
import json as _json
import os as _os
_os.makedirs("l145", exist_ok=True)
_json.dump(out_json, open("l145/static.json", "w"), indent=1)
print(_json.dumps(out_json, indent=1))
print("L145 STATIC DONE")
'''

out = head + TAIL
assert out.count("l142_static") == 0
open("l145_static.py", "w").write(out)
# drift guard: extraction slice must still carry its load-bearing pins
for token, want in [("GI_CARRIER = 1110", 1), ("cutk_pins[", 3),
                    ("n_edges_wA = int(emask_wA.sum())", 1),
                    ("vals_all", 1)]:
    n = out.count(token)
    assert n >= want, (token, n, want)
import py_compile
py_compile.compile("l145_static.py", doraise=True)
print("l145_static.py emitted + compiled OK, lines:", out.count("\\n") + 1)
