"""L169 stage (b1) BUILD: additive transform of l146_static.py -> l169b_static.py.

House pattern (l169_build.py / l126 / l131): count-asserted replacements,
residual scan over CODE lines, py_compile before launch. ONE site is
replaced (the final l146 dump block); everything above it is verbatim, so
l146's own pin asserts run again as free certification.
"""
import py_compile
import re

SRC = "l146_static.py"
OUT = "l169b_static.py"

src = open(SRC).read()

OLD_TAIL = '''import json as _json
import os as _os
_json.dump(out_json, open("l146/static.json", "w"), indent=1)
print(_json.dumps(out_json, indent=1))
print("L146 STATIC DONE", time.time() - t0)'''

NEW_TAIL = r'''# ==================== L169 stage (b1) tail ====================
# PREREG l169b/PREREG.md FIRST. Zero rollouts, no RNG. Everything above
# this line is verbatim l146_static.py (its own pin asserts already ran).
import ast as _ast
import json as _json
import re as _re

# ---- CERT-1: the re-derived l146 census must equal the STORED artifact ----
_rt = _json.loads(_json.dumps(out_json))          # tuple->list round trip
_stored146 = _json.load(open("l146/static.json"))
_json.dump(_rt, open("l169b/static_l146cert.json", "w"), indent=1)
# CERT-1 FIX (disclosed, L110 class): the stored artifact is AUGMENTED
# after the fact by l146/release_floor_addendum.py, which appends the
# S0_release block. l146_static.py cannot produce that key, so CERT-1 is a
# SUBSET compare over the keys this script writes, plus an explicit assert
# that S0_release is the ONLY extra stored key and that the addendum file
# is the thing that writes it.
_extra = sorted(set(_stored146) - set(_rt))
assert _extra == ["S0_release"], ("CERT-1 extra stored keys", _extra)
assert "S0_release" in open("l146/release_floor_addendum.py").read()
for _k in _rt:
    assert _rt[_k] == _stored146[_k], f"CERT-1 FAIL on key {_k}"
log("CERT-1 GREEN: re-derived l146 census == stored l146/static.json on "
    f"all {len(_rt)} keys it writes (extra stored key {_extra} comes from "
    "l146/release_floor_addendum.py; l146/static.json NOT rewritten)")

F4_STORED = _stored146["S4_ladder"]["f4"]
BASE_STORED = _stored146["S4_ladder"]["base"]

# ---- gi -> (cell_type, side) for naming cohort movers ----
_nm = {}
for _gi, _ct, _sd in zip(ann_gi, ann["cell_type"].fillna("").astype(str),
                         ann["side"].fillna("").astype(str)):
    _nm.setdefault(int(_gi), (_ct, _sd))


def nm(g):
    ct, sd = _nm.get(int(g), ("?", "?"))
    return f"{ct}-{sd[:1].upper()}" if ct else f"gi{int(g)}"


def outmass_at(floor):
    pm = w_syn >= floor
    om = np.asarray(out_rows & cord_of_dst & pm)
    m = np.zeros(Nall)
    np.add.at(m, src_all[om], absv[om])
    return m


OM4 = outmass_at(4)
TOT4 = float(OM4[dn_new_g].sum())


def prefixes(ng_order, om, tot):
    return {f"ng{k}": round(float(om[ng_order[:k]].sum() / tot), 4)
            for k in (19, 24, 25, 29)}


def rank_of(ng_order, g):
    w = np.where(ng_order == g)[0]
    return int(w[0]) + 1 if w.size else None


# ---- F1 FROZEN-ALL: base cohort, base order, f4 masses ----
F1 = dict(
    form="F1_frozen_all", floor=4, K=int(len(heav)),
    n_glut=int(is_glut[heav].sum()), n_ng=int((~is_glut[heav]).sum()),
    jaccard_heavy=1.0,
    carrier_rank=rank_of(ng_desc, GI_CARRIER),
    twin_rank=rank_of(ng_desc, GI_TWIN),
    prefix_mass_removed=prefixes(ng_desc, OM4, TOT4))
assert F1["carrier_rank"] == 25 and F1["twin_rank"] == 26, ("CERT-2", F1)
log("CERT-2 GREEN: F1 frozen-all ranks are 25/26 by construction")

# ---- F2 FROZEN-SET, RE-ORDERED by f4 mass ----
_h2 = heav[np.argsort(-OM4[heav])]
_ng2 = _h2[~is_glut[_h2]]
F2 = dict(
    form="F2_frozen_set_reordered", floor=4, K=int(len(_h2)),
    n_glut=int(is_glut[_h2].sum()), n_ng=int((~is_glut[_h2]).sum()),
    jaccard_heavy=1.0,
    carrier_rank=rank_of(_ng2, GI_CARRIER),
    twin_rank=rank_of(_ng2, GI_TWIN),
    prefix_mass_removed=prefixes(_ng2, OM4, TOT4))

# ---- F3 FULLY RE-DERIVED: the SAME function the stored artifact used ----
F3 = ladder(4)
F3["form"] = "F3_fully_rederived"
_f3cmp = {k: v for k, v in F3.items() if k != "form"}
assert _f3cmp == F4_STORED, ("CERT-3 FAIL", _f3cmp, F4_STORED)
log("CERT-3 GREEN: ladder(4) reproduces stored S4_ladder.f4 field-for-field")

# ---- CODE AUDIT (method note, never a finding): ast parse of l146 ladder ----
_tree = _ast.parse(open("l146_static.py").read())
_fn = [n for n in _ast.walk(_tree)
       if isinstance(n, _ast.FunctionDef) and n.name == "ladder"]
assert len(_fn) == 1, "ladder() not found once in l146_static.py"
_assigned = set()
for _n in _ast.walk(_fn[0]):
    if isinstance(_n, _ast.Assign):
        for _t in _n.targets:
            if isinstance(_t, _ast.Name):
                _assigned.add(_t.id)
_cohort_names = ["heav_f", "ng_desc_f", "K", "outmass_f", "cum", "o"]
_inside = {c: (c in _assigned) for c in _cohort_names}
_wholefile_heav = len(_re.findall(r"^heav\s*=", open("l146_static.py").read(),
                                  _re.M))
CODE_AUDIT = dict(
    ladder_body_assigns=_inside,
    cohort_rederived_inside_fn=bool(_inside["heav_f"] and _inside["ng_desc_f"]
                                    and _inside["K"]),
    module_level_heav_assignments=_wholefile_heav,
    note="I6's heuristic counted cohort-array definition SITES before vs "
         "inside the floor loop; the per-floor cohort is re-derived inside "
         "the ladder() FUNCTION (called once per floor), which a "
         "before/inside-loop site count cannot see. Method note only.")

# ---- P1 carrier footprint at f4 by tier ----
P1 = dict(out80_f4=int((w_syn[out_sel] >= 4).sum()),
          out_int70_f4=int((w_syn[out_int] >= 4).sum()),
          out_mot10_f4=int((w_syn[out_mot] >= 4).sum()),
          in13_f4=int((w_syn[in_sel] >= 4).sum()),
          out80_base=int(out_sel.sum()), in13_base=int(in_sel.sum()))

# ---- P2 cohort turnover ----
_h4 = dn_new_g[np.argsort(-OM4[dn_new_g])[:F3["K"]]]
_bs, _fs = set(int(x) for x in heav), set(int(x) for x in _h4)
_left, _ent = sorted(_bs - _fs), sorted(_fs - _bs)
P2 = dict(K_base=int(len(heav)), K_f4=F3["K"],
          left_n=len(_left), entered_n=len(_ent),
          left=[dict(gi=g, name=nm(g), glut=bool(is_glut[g])) for g in _left],
          entered=[dict(gi=g, name=nm(g), glut=bool(is_glut[g]))
                   for g in _ent],
          ng_left_n=int(sum(1 for g in _left if not is_glut[g])),
          ng_entered_n=int(sum(1 for g in _ent if not is_glut[g])),
          jaccard_heavy=F3["jaccard_heavy"])

# ---- P3 window portability + the f4 XOR boundary ----
_ng4 = _h4[~is_glut[_h4]]
assert rank_of(_ng4, GI_CARRIER) == F3["carrier_rank"], "ng4 order mismatch"
_cr4 = F3["carrier_rank"]
P3 = dict(
    base_window_k=24, base_window_overlap_f4=int(
        len(set(int(x) for x in ng_desc[:24]) &
            set(int(x) for x in _ng4[:24]))),
    f4_carrier_rank=_cr4,
    f4_xor_forms=dict(intact_k=_cr4 - 1, cut_k=_cr4),
    f4_prefix_mass=dict(
        intact=round(float(OM4[_ng4[:_cr4 - 1]].sum() / TOT4), 4),
        cut=round(float(OM4[_ng4[:_cr4]].sum() / TOT4), 4)),
    base_prefix_mass=dict(intact=BASE_STORED["prefix_mass_removed"]["ng24"],
                          cut=BASE_STORED["prefix_mass_removed"]["ng25"]),
    note="the wA/ng25 cut window is a POSITIONAL prefix of the ng ladder, "
         "so at f4 the XOR pair becomes cut-first-(rank-1) vs cut-first-rank "
         "over a re-derived ladder; a dynamic f4 arm cuts a different cell "
         "set unless the overlap is the full window.")

# ---- P4 twin design at f4 ----
_cm4 = OM4[_ng4]
_ci = _cr4 - 1
_cand = [(abs(float(_cm4[i] - _cm4[_ci])), int(_ng4[i]), i + 1)
         for i in range(len(_ng4)) if i != _ci]
_cand.sort()
P4 = dict(
    carrier_mass_f4=round(float(_cm4[_ci] / TOT4), 6),
    nearest=[dict(gi=g, name=nm(g), rank=r,
                  mass=round(float(OM4[g] / TOT4), 6),
                  gap=round(d / TOT4, 6)) for d, g, r in _cand[:3]],
    base_twin_gi=int(GI_TWIN), base_twin_name=nm(GI_TWIN),
    base_twin_f4_rank=F3["twin_rank"],
    base_twin_f4_mass=round(float(OM4[GI_TWIN] / TOT4), 6),
    note="base twin 319 sits at f4 rank 33, so the carrier-vs-twin XOR "
         "design does not port unmodified; a dynamic f4 arm must re-derive "
         "its mass-matched twin.")

# ---- P5 edge budget + bisect note ----
P5 = dict(closure_edges_base=BASE_STORED["closure_edges"],
          closure_edges_f4=F3["closure_edges"],
          wA_edges_base=BASE_STORED["wA_edges"],
          wA_edges_f4=F3["wA_edges"],
          deleted_share_closure=round(
              1 - F3["closure_edges"] / BASE_STORED["closure_edges"], 4),
          note="a dynamic f4 arm needs a FRESH af-matched bisect on the f4 "
               "graph (L118-L131 criteria verbatim; never port a gain).")

# ---- registered decision rule E1/E2/E3 ----
_stored_is_F3 = (_f3cmp == F4_STORED)
_stored_is_F1 = (F4_STORED["carrier_rank"] == F1["carrier_rank"]
                 and F4_STORED["twin_rank"] == F1["twin_rank"]
                 and F4_STORED["K"] == F1["K"])
e1 = (_stored_is_F3 and F4_STORED["carrier_rank"] != F1["carrier_rank"]
      and F4_STORED["jaccard_heavy"] < 1.0)
e2 = _stored_is_F1
verdict = ("E1_refuted_frozen_membership_premise" if e1
           else ("E2_confirmed_frozen_membership" if e2 else "E3_partial"))

out_b1 = dict(
    design="L169 stage (b1): is the published f4 floor robustness "
           "FROZEN-membership or fully RE-DERIVED? Static premise test for "
           "referee issue I6 + design pins for the (b2) dynamic f4 arm. "
           "PREREG l169b/PREREG.md FIRST. Zero rollouts, no RNG.",
    cert=dict(cert1_l146_census_identical=True,
              cert2_F1_ranks_by_construction=True,
              cert3_ladder4_eq_stored=True),
    forms=dict(F0_base=BASE_STORED, F1_frozen_all=F1,
               F2_frozen_set_reordered=F2, F3_fully_rederived=F3),
    code_audit=CODE_AUDIT,
    pins=dict(P1_carrier_footprint=P1, P2_cohort_turnover=P2,
              P3_window_portability=P3, P4_twin_design=P4,
              P5_edge_budget=P5),
    verdict=verdict, verdict_detail=dict(
        stored_is_F3=_stored_is_F3, stored_is_F1=_stored_is_F1,
        e1=bool(e1), e2=bool(e2),
        stored_carrier_rank=F4_STORED["carrier_rank"],
        F1_carrier_rank=F1["carrier_rank"], F2_carrier_rank=F2["carrier_rank"],
        stored_jaccard=F4_STORED["jaccard_heavy"]),
)
_json.dump(out_b1, open("l169b/static.json", "w"), indent=1)
print(_json.dumps(out_b1, indent=1))
print("L169b STATIC DONE", time.time() - t0)'''

assert src.count(OLD_TAIL) == 1, f"tail site count {src.count(OLD_TAIL)} != 1"
out = src.replace(OLD_TAIL, NEW_TAIL)
assert out != src and out.count(NEW_TAIL) == 1

# residual scan: no WRITE to l146/static.json may survive in CODE lines
bad = []
for i, line in enumerate(out.splitlines(), 1):
    s = line.strip()
    if s.startswith("#") or s.startswith('"') or s.startswith("'"):
        continue
    if "l146/static.json" in s and ('"w"' in s or "'w'" in s):
        bad.append((i, s))
assert not bad, f"residual write to l146 artifact: {bad}"
assert out.count('open("l169b/static.json", "w")') == 1
assert out.count('open("l169b/static_l146cert.json", "w")') == 1
open(OUT, "w").write(out)
py_compile.compile(OUT, doraise=True)
print("BUILD OK", OUT, len(out.splitlines()), "lines;",
      "reps 1, residual scan clean, py_compile green")
