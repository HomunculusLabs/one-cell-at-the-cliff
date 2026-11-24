"""t251_containment.py — POST-HOC, DESCRIPTIVE. Pure arithmetic on the sets
l221/static.json already stored; no new measurement, no new machinery, and it
writes nothing. Reason it exists: the registered Jaccard bar is SYMMETRIC and
therefore conflates "a different set" with "a nested subset" whenever the
candidate sets differ in size, which they do here (11 / 30 / 46).
"""
import json

S = json.load(open("l221/static.json"))
P = S["L221_primary"]
M = P["per_metric"]
out = {}
for key in ("realised_edges", "feasible_edges"):
    sets = {k: set(v[key]) for k, v in M.items()}
    assert len(sets["abs"]) == (11 if key == "realised_edges" else 11)
    for a in sets:
        for b in sets:
            if a == b:
                continue
            inter = sets[a] & sets[b]
            out[f"{key}:{a}->{b}"] = dict(
                n_a=len(sets[a]), n_b=len(sets[b]), n_inter=len(inter),
                containment_a_in_b=round(len(inter) / len(sets[a]), 6),
                jaccard=round(len(inter) / len(sets[a] | sets[b]), 6))
for k in sorted(out):
    if k.split(":")[1].startswith("abs->"):
        v = out[k]
        print(f"{k:34s} |a|={v['n_a']:2d} |b|={v['n_b']:2d} "
              f"inter={v['n_inter']:2d} containment(a in b)="
              f"{v['containment_a_in_b']:.4f} jaccard={v['jaccard']:.4f}")
# the claim, asserted so a wrong hand-reading cannot survive
assert set(M["abs"]["realised_edges"]) <= set(M["hop"]["realised_edges"]), \
    "abs realised is NOT a subset of hop realised"
assert set(M["abs"]["feasible_edges"]) <= set(M["hop"]["feasible_edges"]), \
    "abs feasible is NOT a subset of hop feasible"
_miss = set(M["abs"]["realised_edges"]) - set(M["crofts"]["realised_edges"])
print(f"abs realised NOT in crofts realised: {sorted(_miss)} "
      f"({len(_miss)} of {len(M['abs']['realised_edges'])})")
_ld = P["per_metric_load"]["abs"]
_tot = sum(_ld.values())
_top = sorted(_ld.items(), key=lambda kv: -kv[1])[:4]
print(f"abs load total {_tot} pool cells; top-4 entry edges "
      f"{[(k, v) for k, v in _top]} = {sum(v for _, v in _top)} "
      f"({sum(v for _, v in _top) / _tot * 100:.1f}%)")
assert _tot == 303, ("load does not sum to the 303 pool cells", _tot)
print("ALL CONTAINMENT ASSERTS GREEN")
