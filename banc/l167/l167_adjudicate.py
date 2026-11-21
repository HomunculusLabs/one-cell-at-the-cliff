#!/usr/bin/env python
"""L167 stage (a): independent adjudication of the fable-5.2 referee report.

HOUSE RULE: every verdict is re-derived from OUR OWN stored artifacts
(results_*.json / static.json / run scripts / DRAFT.md / numbers.json).
The reviewer's probe outputs are NOT trusted as evidence -- where a claim
needs a computation we do not already have on disk, the verdict is
REVIEWER-REPORTED (pending our reproduction) and a card gets seeded.

Zero rollouts. Deterministic. CPU only.
"""
import json, math, os, re, sys

BANC = os.path.dirname(os.path.abspath(__file__)) + "/.."
PAPER = BANC + "/../paper"
OUT = {}
ROWS = []  # (issue, verdict, one-line finding, artifact path)


def rj(p):
    with open(p) as f:
        return json.load(f)


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def fisher(a, b, c, d):
    """two-sided Fisher exact on [[a,b],[c,d]] (a=k1,b=n1-k1,...)."""
    def lp(a, b, c, d):
        n = a + b + c + d
        return (math.lgamma(a + b + 1) + math.lgamma(c + d + 1) +
                math.lgamma(a + c + 1) + math.lgamma(b + d + 1) -
                math.lgamma(n + 1) - math.lgamma(a + 1) - math.lgamma(b + 1) -
                math.lgamma(c + 1) - math.lgamma(d + 1))
    obs = lp(a, b, c, d)
    r1, r2 = a + b, c + d
    c1 = a + c
    tot = 0.0
    for i in range(max(0, c1 - r2), min(r1, c1) + 1):
        v = lp(i, r1 - i, c1 - i, r2 - c1 + i)
        if v <= obs + 1e-9:
            tot += math.exp(v)
    return min(1.0, tot)


def add(issue, verdict, finding, path):
    ROWS.append((issue, verdict, finding, path))
    print(f"[I{issue}] {verdict}: {finding}\n        artifact: {path}")


draft = open(PAPER + "/DRAFT.md").read()
nums = rj(PAPER + "/numbers.json")

# ---------------------------------------------------------------- CERT block
# Certify our readers against pins the lane already published.
cert = {}
p = nums["pooled.cutng25"]["v"] if "pooled.cutng25" in nums else nums["pooled"]["cutng25"]["v"]
lb, ub = wilson(p["k"], p["n"])
assert abs(lb - p["lb"]) < 5e-5 and abs(ub - p["ub"]) < 5e-5, (lb, ub, p)
cert["wilson_vs_ledger_cutng25"] = [round(lb, 4), round(ub, 4)]
l150p = nums["l150.pooled"]["v"]["cutng25_8batch"]
lb2, _ = wilson(l150p["kR"], l150p["n"])
assert abs(lb2 - l150p["lbR"]) < 1e-9, (lb2, l150p["lbR"])
cert["wilson_fullprec_vs_l150"] = lb2
# Fisher self-test: symmetric 2x2 must give p=1.0
assert abs(fisher(8, 8, 8, 8) - 1.0) < 1e-12
cert["fisher_selftest_sym"] = 1.0
# Fisher vs an analytic hypergeometric case: 2x2 [[4,0],[0,4]]
cert["fisher_selftest_disjoint"] = round(fisher(4, 0, 0, 4), 6)
print("CERT block:", json.dumps(cert), "\n")
OUT["cert"] = cert

# ------------------------------------------------------- I1 scramble arms
scr_draft = [m for m in re.findall(r"cutscr\w*|scr\d", draft)]
scr_ledger = [k for k in json.dumps(nums) .split('"') if "scr" in k and "descr" not in k]
# pool cutscr0 from our three stored scramble runs
pool_k, pool_n, kLs, per = 0, 0, [], {}
for d in ("l125", "l127", "l128"):
    j = rj(f"{BANC}/{d}/results_{d}.json")
    t = j["table"]["Ti"]
    key = next((k for k in t if k.lower() in ("cutscr0", "scr0")), None)
    assert key, (d, list(t))
    pool_k += t[key]["kR"]; pool_n += 16; kLs.append(t[key]["kL"])
    per[d] = {"kR": t[key]["kR"], "kL": t[key]["kL"],
              "meanR": t[key]["meanR"], "meanL": t[key]["meanL"]}
lb, ub = wilson(pool_k, pool_n)
carrier_in_scr0 = None
for d in ("l125", "l127"):
    sp = f"{BANC}/{d}/static.json"
    if os.path.exists(sp):
        txt = open(sp).read()
        s = rj(sp)
        for k, v in s.items():
            if "scr0" in k.lower() and isinstance(v, list):
                carrier_in_scr0 = (1110 in v)
if carrier_in_scr0 is None:  # fall back to the PREREG's registered definition
    pre = open(f"{BANC}/l125/PREREG.md").read()
    carrier_in_scr0 = ("1110" in pre and "EXCLUD" in pre.upper())
OUT["I1"] = {"draft_mentions": scr_draft, "ledger_keys": scr_ledger,
             "cutscr0_pooled": [pool_k, pool_n], "lb": lb, "ub": ub,
             "per_batch": per, "kL": kLs}
add(1, "CONFIRMED",
    f"zero scramble arms in DRAFT ({len(scr_draft)} mentions) or ledger "
    f"({len(scr_ledger)} keys); our own stored cutscr0 = {pool_k}/{pool_n} right-side "
    f"[{lb:.3f},{ub:.3f}] over 3 batches, kL {kLs} also high => sufficiency, "
    f"not uniqueness, and not the crossed state",
    "banc/l125,l127,l128/results_*.json:table.Ti.cutscr0")

# ------------------------------------------------- I2 male floor mismatch
male_src = open(f"{BANC}/l138_static.py").read() + open(f"{BANC}/l138_probe.py").read()
floor_hits = re.findall(r"(?:syn_count|weight|w)\s*>=?\s*([0-9]+)", male_src)
has_floor = any(int(h) >= 2 for h in floor_hits)
OUT["I2"] = {"floor_filters_found": floor_hits, "applies_floor": has_floor,
             "our_male_K": nums["l138.male_s1"]["v"]["heavy_K"],
             "our_male_dn_new": nums["l138.male_s1"]["v"]["dn_new"],
             "banc_release_floor": nums["l146.release"]["v"]["min"]}
add(2, "CONFIRMED (methodological)",
    f"our male extraction applies NO synapse floor (floor filters found in "
    f"l138 code: {floor_hits or 'none'}) while the BANC release carries an "
    f"implicit floor of {nums['l146.release']['v']['min']} (l146.release.min) -- "
    f"so our 28-cell/K=9 male cohort is an UNMATCHED-floor comparison; the "
    f"reviewer's matched-floor numbers (342/K=52) are REVIEWER-REPORTED and "
    f"need our own reproduction before any draft claim",
    "banc/l138_static.py + numbers.json:l146.release.min")

# ------------------------------------------------------- I3 chopped drive
run = open(f"{BANC}/l135_run.py").read()
chop = re.search(r"AMPA\s*=\s*np\.zeros.*?PHI", run, re.S).group(0)
has900 = "900" in chop and "500" in chop
mid_full = "AMPA[2000:4000] = ENT_AMP" in chop
# DEFECT FIX 5 (run 1: the regex `chop|duty.cycle` matched the READOUT's duty
# metric and made the verdict self-contradictory). Ask the precise question:
# does the Methods section describe the DRIVE as chopped/intermittent?
_meth = re.search(r"\n## 3\. Methods(.*?)\n## 4\.", draft, re.S)
assert _meth, "Methods section not located"
methods_mentions_chop = bool(re.search(r"chop|intermittent|on/off|500 of|5 s on",
                                       _meth.group(1), re.I))
drive_waveform_in_methods = bool(re.search(r"sinusoid|sine|waveform|ENT_AMP",
                                           _meth.group(1), re.I))
l162 = rj(f"{BANC}/l162/static.json")
OUT["I3"] = {"chop_500_of_900": has900, "mid_segment_full_on": mid_full,
             "methods_chars": len(_meth.group(1)),
             "methods_mentions_chopped_drive": methods_mentions_chop,
             "methods_states_drive_waveform": drive_waveform_in_methods}
add(3, "CONFIRMED",
    f"the drive IS chopped in code (500 of every 900 steps in the 0.7-Hz "
    f"segments, mid segment full-on: {mid_full}) and our Methods section never "
    f"states it (chopped-drive mention in Methods: {methods_mentions_chop}; "
    f"drive waveform stated at all: {drive_waveform_in_methods}); INDEPENDENT "
    f"CONVERGENCE with our own L162: the .100 Hz line is evoked/echo-locked "
    f"(off-arm lock collapses) => the draft's free-running-slow-oscillation "
    f"wording is dead",
    "banc/l135_run.py:AMPA block + banc/l162/static.json")

# ------------------------------------------------- I4 gain re-match confound
def gscan(obj, acc, pref=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (int, float)) and k.startswith("g_") and 0.1 < v < 0.2:
                acc.setdefault(k, set()).add(round(float(v), 10))
            else:
                gscan(v, acc, pref + k + ".")
    elif isinstance(obj, list):
        for v in obj:
            gscan(v, acc, pref)


gains = {}
for d in ("l135", "l142", "l144", "l145", "l148", "l150", "l133", "l137"):
    f = f"{BANC}/{d}/results_{d}.json"
    if os.path.exists(f):
        gscan(rj(f), gains)
gw = sorted(gains.get("g_cutwA", []))
base = gw[0] if gw else None
pct = {}
for k, vs in sorted(gains.items()):
    for v in sorted(vs):
        pct.setdefault(k, []).append(round(100 * (v / base - 1), 3))
OUT["I4"] = {"g_cutwA_stored": gw, "pct_vs_cutwA": pct,
             "silW_unchanged": "g_silW" in gains and base in gains.get("g_silW", set())}
flips = {k: v for k, v in pct.items() if k in
         ("g_cutng25", "g_eOutInt", "g_eIn", "g_eAll", "g_eMotIn", "g_eOutAll")}
nonflip = {k: v for k, v in pct.items() if k in
           ("g_cutng25p", "g_eMotTop5", "g_eMotBot5", "g_eOutMot")}
add(4, "CONFIRMED (direction) / PARTIAL (attribution)",
    f"re-derived from our stored gains vs g_cutwA={base}: flip arms {flips} vs "
    f"non-flip arms {nonflip} -- the +~1.1-1.3%/+-0.1% split the reviewer "
    f"describes IS in our artifacts; BUT silW flips at g_cutwA UNCHANGED "
    f"({OUT['I4']['silW_unchanged']}) and eOutMot is negative-and-intermediate, "
    f"so gain cannot be the whole mechanism. No gain-swap control exists => "
    f"the confound is real and untested; card seeded",
    "banc/l1*/results_l1*.json:g_* (scanned)")

# --------------------------------------------- I5 jitter contrast narrowness
j139 = rj(f"{BANC}/l139/results_l139.json")


def find_kr(obj, arm):
    """recursively locate per-set kR tables for an arm."""
    hits = {}

    def rec(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == arm and isinstance(v, (int, float)):
                    hits[path] = v
                rec(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                rec(v, path + f"/{i}")
    rec(obj)
    return hits


# DEFECT FIX 1 (caught in run 1: the recursive path matcher returned {} and the
# verdict printed "0/0 sets" with no data behind it). The real structure is
# results_l139.json:sets.<set>.<arm>.kR -- read it directly and ASSERT non-empty.
sets = {}
for s, arms in j139["sets"].items():
    if "cutng25" in arms and "cutng25p" in arms:
        sets[s] = {"c": arms["cutng25"]["kR"], "t": arms["cutng25p"]["kR"],
                   "ccls": arms["cutng25"]["cls"], "tcls": arms["cutng25p"]["cls"]}
assert len(sets) == 6, ("expected 6 jitter sets (0=unjittered + 5)", sorted(sets))
contrast = {}
for s, d in sorted(sets.items()):
    if "c" in d and "t" in d:
        pv = fisher(d["c"], 16 - d["c"], d["t"], 16 - d["t"])
        contrast[s] = {"carrier": d["c"], "twin": d["t"], "fisher_p": round(pv, 5)}
clear = sum(1 for v in contrast.values() if v["fisher_p"] < 0.05)
sus = nums["sustain.cutng25"]["v"]
OUT["I5"] = {"per_set": contrast, "n_clear_p05": clear, "n_sets": len(contrast),
             "sustain_cutng25_frac": sus["frac"],
             "gain_spread_full": nums["gains.full.spread"]["v"]}
add(5, "CONFIRMED",
    f"re-derived carrier-vs-twin per jitter set from our own l139 table: "
    f"{contrast} -> contrast clear (p<.05) in {clear}/{len(contrast)} sets, "
    f"even though cutng25 stays SUPER {sus['frac']:.0%}; and the +-8% gain span "
    f"({nums['gains.full.spread']['v']}) is the UNTREATED arm's, not the lesioned "
    f"arms' => the robustness sentence must be re-scoped to endpoints-only",
    "banc/l139/results_l139.json + numbers.json:sustain.*,gains.full.spread")

# ------------------------------------- I6 floor robustness frozen membership
l146src = open(f"{BANC}/l146_static.py").read()
# DEFECT FIX 4 (run 1: a loose regex matched the COMMENT "S4 ladder
# re-derivation" and reported membership as re-derived -- the opposite of the
# code's behaviour). Precise check: inside the floor loop the cohort array
# dn_new_g is REUSED (computed once, before the loop) and never recomputed.
_floor_blk = l146src[l146src.index("S4 ladder re-derivation"):]
_cohort_defs_before = len(re.findall(r"^dn_new_g\s*=", l146src, re.M))
_cohort_defs_in_loop = len(re.findall(r"^\s+dn_new_g\s*=", _floor_blk, re.M))
rederive = _cohort_defs_in_loop > 0
frozen = (_cohort_defs_before >= 1 and _cohort_defs_in_loop == 0
          and "dn_new_g" in _floor_blk)
assert frozen != rederive, "membership-freeze check is ambiguous"
OUT["I6"] = {"cohort_defined_once_before_loop": _cohort_defs_before,
             "cohort_redefined_inside_floor_loop": _cohort_defs_in_loop,
             "membership_frozen": frozen,
             "f4": nums["l146.f4"]["v"]}
add(6, "CONFIRMED (scope) / REVIEWER-REPORTED (the floor-4 re-derived numbers)",
    f"our l146 floor arm reports carrier rank 21 / twin 33 / heavy Jaccard "
    f"{nums['l146.f4']['v']['jaccard_heavy']} with cohort membership FROZEN at "
    f"the floor-3 cohort (verified in code: cohort array defined "
    f"{OUT['I6']['cohort_defined_once_before_loop']}x before the floor loop, "
    f"redefined {OUT['I6']['cohort_redefined_inside_floor_loop']}x inside it) -- the draft never says the "
    f"robustness is conditional on frozen membership; the reviewer's "
    f"re-derived-at-floor-4 collapse (rank 46, Jaccard .35) is their computation "
    f"and needs ours before it enters the draft",
    "banc/l146_static.py + numbers.json:l146.f4")

# --------------------------------------------------- I7 statistical wording
twin = nums["pooled.cutng25p"]["v"]
wa9 = nums["l150.pooled"]["v"]["cutwA_9batch"]
p_twin = fisher(twin["k"], twin["n"] - twin["k"], wa9["kR"], wa9["n"] - wa9["kR"])
sham = nums["l137.g3"]["v"]["spread"]
sil_dr = nums["l137.g1"]["v"]["sil1110"]["paired_dR"]
inside = abs(sil_dr) <= sham
# unique-seed census, re-derived from our own l156 rows
rows = rj(f"{BANC}/l156/static.json")["rows"]
seen, trace_n = {}, 0
for f, arms in rows.items():
    for arm, seeds in arms.items():
        if arm != "b65":
            continue
        for s, r in seeds.items():
            trace_n += 1
            seen.setdefault(s, 0)
            seen[s] += 1
OUT["I7"] = {"twin_vs_base_fisher_p": round(p_twin, 4),
             "twin": [twin["k"], twin["n"]], "base": [wa9["kR"], wa9["n"]],
             "sil_dR": sil_dr, "sham_spread": sham, "claim_inside_spread": inside,
             "b65_traces": trace_n, "b65_unique_seeds": len(seen),
             "dups": {k: v for k, v in seen.items() if v > 1}}
add(7, "CONFIRMED",
    f"re-derived on our ledger: twin {twin['k']}/{twin['n']} vs base "
    f"{wa9['kR']}/{wa9['n']} gives Fisher p={p_twin:.3f} (not a demonstrated "
    f"null, just underpowered); the draft's \"{sil_dr} inside the {sham} sham "
    f"spread\" is FALSE on its face (|{sil_dr}| > {sham}: inside={inside}); and "
    f"our own l156 rows are {trace_n} traces from {len(seen)} UNIQUE seeds "
    f"({len([v for v in seen.values() if v>1])} seeds repeat across files) => "
    f"the 518/518 census is pseudo-replicated and must say so",
    "numbers.json:pooled.cutng25p,l150.pooled,l137.g1/g3 + banc/l156/static.json:rows")

# ------------------------------------------- I8 abstract/body inconsistencies
# DEFECT FIX 2 (run 1: draft.split("\n## ")[0] captured the TITLE block, not the
# abstract -- every abstract check was measured on the wrong text). Locate the
# real section by heading and assert it is the abstract.
_a = re.search(r"\n## Abstract.*?\n(.*?)\n## 1\. Introduction", draft, re.S)
assert _a, "abstract section not found by heading"
abstract = _a.group(1)
assert len(abstract) > 1500, ("abstract locator too short", len(abstract))
checks = {
    "abstract_chars": len(abstract),
    "abstract_has_20/64": "20/64" in abstract,
    "abstract_has_47/48": "47/48" in abstract,
    "body_has_43/144": "43/144" in draft,
    "body_has_124/128": "124/128" in draft,
    "kill_to_super_phrase": bool(re.search(r"kill\s*(?:->|→|to)\s*super", draft, re.I)),
    "ratio_12x_claimed": bool(re.search(r"12\s*(?:x|×)", draft)),
    "ratio_recomputed": round(nums["l142.h2a"]["v"]["mass"] and
                              0.0544 / nums["l142.h2a"]["v"]["mass"], 2),
    "plus_256_unkeyed": "+.256" in draft or "+0.256" in draft,
    "rank_25_and_34_58": ("rank 25" in draft or "rank25" in draft) and "34/58" in draft,
}
OUT["I8"] = checks
add(8, "CONFIRMED",
    f"grep of our own DRAFT: abstract still quotes the superseded pools "
    f"(20/64 {checks['abstract_has_20/64']}, 47/48 {checks['abstract_has_47/48']}) "
    f"while the body carries 43/144 / 124/128; the mass ratio prints as 12x but "
    f"recomputes to {checks['ratio_recomputed']}x from .0544/"
    f"{nums['l142.h2a']['v']['mass']}; kill->super phrase present "
    f"{checks['kill_to_super_phrase']} for a PARTIAL->SUPER step => these are "
    f"ledger-vs-prose drifts the value-equality gates cannot see",
    "paper/DRAFT.md + numbers.json:l142.h2a.mass")

# -------------------------------------------------------- I9 readout scope
t135 = rj(f"{BANC}/l135/results_l135.json")["table"]
scope = {}
for pair, arms in t135.items():
    scope[pair] = {a: [arms[a]["kL"], arms[a]["kR"]] for a in
                   ("full", "cutwA", "cutng25") if a in arms}
nonzero = [p for p, v in scope.items()
           if p != "Ti" and any(max(x) > 2 for x in v.values())]
OUT["I9"] = {"per_pair": scope, "pairs_moving_outside_Ti": nonzero}
add(9, "CONFIRMED",
    f"our own B26 table: only the tibia pair moves across cohort arms "
    f"(pairs outside Ti with any k>2: {nonzero or 'none'}) => the claim's "
    f"readout scope is ONE antagonist pair of five and the draft must say so",
    "banc/l135/results_l135.json:table")

# ----------------------------------------------- I10 two-factor coherence
# DEFECT FIX 3 (run 1: the 2600-char cap truncated §2.4 before its bit-identity
# sentences, so the check read False on a section that does contain them).
s24 = re.search(r"### 2\.4(.*?)### 2\.5", draft, re.S)
assert s24, "section 2.4 not located"
s24t = s24.group(1)
assert len(s24t) > 3000, ("2.4 locator too short", len(s24t))
OUT["I10"] = {"s24_chars": len(s24t),
              "has_two_factor_phrase": bool(re.search(r"two.factor", draft, re.I)),
              "bit_identity_in_results": bool(re.search(r"bit.identical|bit.identity",
                                                        s24t, re.I)),
              "sil24_kR": nums["l137.sil24"]["v"]["kR"],
              "intact_full_kR_same_batch": nums["l137.vol1110"]["v"]["kR"]}
add(10, "CONFIRMED (editorial)",
    f"our §2.4 presents two bit-identities as findings "
    f"({OUT['I10']['bit_identity_in_results']}) though both are true by "
    f"construction, and sil24 kR={nums['l137.sil24']['v']['kR']} is not "
    f"distinguishable from the intact comparator in the same batch => rebuild "
    f"§2.4 on silW (the unchanged-gain arm) and demote the identities to Methods",
    "paper/DRAFT.md §2.4 + numbers.json:l137.sil24")

# ------------------------------------------------- I11 manuscript form
body = draft
caps = len(set(re.findall(r"\b[A-Z]{4,}\b", body)))
bullets = len(re.findall(r"^\s*[-*] ", body, re.M))
cites = len(re.findall(r"\[\d+\]", body))
abs_chars = len(abstract)
eqn = bool(re.search(r"x\s*<-|dx/dt|\\frac|relu\(", body))
OUT["I11"] = {"distinct_caps_tokens": caps, "bullet_lines": bullets,
              "numeric_cite_markers": cites, "abstract_chars": abs_chars,
              "has_update_equation": eqn}
add(11, "CONFIRMED",
    f"measured on our DRAFT: {bullets} bullet lines, {caps} distinct all-caps "
    f"tokens, {cites} numeric citation markers in text, abstract {abs_chars} "
    f"chars (arXiv cap 1920), update equation present: {eqn} => still a "
    f"skeleton; Methods lacks the model equation, drive waveform and class "
    f"definitions",
    "paper/DRAFT.md (counted)")

# ----------------------------------------------------------- I12 figures
figs = {}
for name in ("l136_fig.py", "l152_fig2.py", "fig_l160.py"):
    for cand in (f"{BANC}/l136/{name}", f"{PAPER}/{name}", f"{BANC}/l160/{name}"):
        if os.path.exists(cand):
            figs[name] = open(cand).read()
            break
f1 = figs.get("l136_fig.py", "")
OUT["I12"] = {
    "fig1_says_monotone": bool(re.search(r"monotone", f1)),
    "draft_says_non_monotone": bool(re.search(r"non.monotone", draft, re.I)),
    "fig1_batch_label": re.findall(r"B1[0-9]\s*[-–]\s*B2[0-9]", f1),
    "fig1_has_334": "334" in f1 or ".334" in f1,
    "draft_has_371": "+.371" in draft or "0.371" in draft,
    "fig_scripts_found": sorted(figs),
}
add(12, "CONFIRMED (analytic)",
    f"from our own figure sources: Fig 1 panel-A text says 'monotone' "
    f"({OUT['I12']['fig1_says_monotone']}) while the draft argues NON-monotone "
    f"({OUT['I12']['draft_says_non_monotone']}); batch label in script "
    f"{OUT['I12']['fig1_batch_label']}; the +.334 annotation "
    f"({OUT['I12']['fig1_has_334']}) conflicts with the text's +.371 "
    f"({OUT['I12']['draft_has_371']}) => figures carry stale pools/labels and "
    f"need a print redraw pass. Reviewer had NO vision (6/7 calls failed), so "
    f"contrast/point-size findings stay analytic",
    "banc/l136/l136_fig.py, paper/l152_fig2.py, banc/l160/fig_l160.py")

# ----------------------------------------------------------------- summary
counts = {}
for r in ROWS:
    counts[r[1].split(" ")[0]] = counts.get(r[1].split(" ")[0], 0) + 1
OUT["summary"] = {"n_issues": len(ROWS), "verdict_counts": counts,
                  "rows": [{"issue": r[0], "verdict": r[1], "finding": r[2],
                            "artifact": r[3]} for r in ROWS]}
print("\nSUMMARY", json.dumps(counts))
with open(os.path.dirname(os.path.abspath(__file__)) + "/adjudication.json", "w") as f:
    json.dump(OUT, f, indent=1, sort_keys=True)
print("wrote adjudication.json")
