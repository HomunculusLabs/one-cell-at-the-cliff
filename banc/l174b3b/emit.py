#!/usr/bin/env python3
"""L174 stage (b3b-i) — bullets to prose in §1, §2.1, §2.2, §2.3.

Format-only by construction and by gate (PREREG T1): the numeric-token and
citation-key multisets of the edited span must be IDENTICAL before and after.
Body lines are de-indented mechanically; only the 15 opener lines are
re-authored (CERT-4). One-shot: refuses to run twice.
"""
import json, os, re, sys

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b3b"
DRAFT = os.path.join(PAPER, "DRAFT.md")

span_pre = open(os.path.join(OUT, "span_pre.txt")).read()
draft = open(DRAFT).read()
i = draft.index("## 1. Introduction")
j = draft.index("### 2.4 Mechanism")
live = draft[i:j]
assert live == span_pre, ("T4/CERT-3: live span differs from the freeze — "
                         "emit.py refuses to run (already spliced?)")

# --------------------------------------------------------------------------
# The rewrite map. Key = the bullet's exact opener line (dash included).
# 'new'  = the replacement line(s); 'eat' = how many BODY lines the opener
# replacement consumes; 'join' = paragraph continues into the next block.
# --------------------------------------------------------------------------
MAP = {
 "- The four load-bearing results, up front: (1) at gain-certified MATCHED": dict(
   new=["We report four load-bearing results, and state them up front: (1) at gain-certified MATCHED"],
   eat=0),
 "- Framing: connectome-constrained models now reproduce activity or behaviour in": dict(
   new=["Connectome-constrained models now reproduce activity or behaviour in"], eat=0),
 "- What a perturbation in a model can and cannot license is itself an old": dict(
   new=["What a perturbation in a model can and cannot license is itself an old"], eat=0),
 "- Walking-CPG field context (Sapkal et al. [34]):": dict(
   new=["Walking-CPG field context (Sapkal et al. [34]) supplies three findings",
        "that bear on this one:"], eat=0,
   fix=[("seeds): NOT\nMET —", "seeds): NOT MET —")]),
 "- Nearest neighbors and the gap (from the targeted novelty sweep, logged in": dict(
   new=["Nearest neighbours and the gap come from the targeted novelty sweep",
        "logged in LANE-RESEARCH.md 2026-11-18. There are four neighbours and",
        "one gap."], eat=1),
 "  - The gap this paper fills, stated after both narrowings above: not that": dict(
   new=["The gap this paper fills, stated after both narrowings above: not that identity matters",
        "— [6] and [36] show that already — but that an"], eat=1),
 "- Substrate: l65 cord subnet, 20,521 cord + 728 DN-into cells; Ti flexor pool": dict(
   new=["The substrate is the l65 cord subnet, 20,521 cord + 728 DN-into cells,",
        "and the Ti flexor pool has n=101 [subnet]; 11 runs are summed",
        "[n_runs_summed]."], eat=1, join=True),
 "- U-law with pooled Wilson intervals; the k=24→25 step (+.371 meanR": dict(
   new=["The U-law is read with pooled Wilson intervals, and the k=24→25 step",
        "(+.371 meanR"], eat=0, join=True),
 "- Non-monotone: k=58 kills again (1 of 258 [l172.pooled]) — a WINDOW, not a": dict(
   new=["The ladder is non-monotone: k=58 kills again (1 of 258 [l172.pooled]) — a",
        "WINDOW, not a"], eat=0, join=True),
 "- Every arm's count in this paper is its single canonical pooled count": dict(
   new=["Every arm's count in this paper is its single canonical pooled count"],
   eat=0),
 "- rank 25 = id 1110 (DNp33-L — THE carrier; m .00644), rank 26 = id 319": dict(
   new=["At the transition, rank 25 = id 1110 (DNp33-L — THE carrier; m .00644),",
        "rank 26 = id 319"], eat=0, join=True),
 "- The twin is not neutral and the question is not underpowered at the": dict(
   new=["The twin is not neutral and the question is not underpowered at the"],
   eat=0),
 "- Both READS of the flip ride the same cell (right-side super-raise AND": dict(
   new=["Both READS of the flip ride the same cell (right-side super-raise AND"], eat=0, join=True),
 "- Canonical pooled counts (unique seeds, all admissible batches): carrier": dict(
   new=["The canonical pooled counts (unique seeds, all admissible batches) are:",
        "carrier"], eat=0),
 "- DNp33-L: ACh, neck-connective class; 80 out-edges, 87% intrinsic / 13%": dict(
   new=["The carrier cell DNp33-L is ACh, neck-connective class; 80 out-edges,",
        "87% intrinsic / 13%"], eat=0),
}
# the §1 lettered neighbours become their own paragraphs
LETTERED = re.compile(r"^\s{2}\((a|b|c|d)\) ")

BRE = re.compile(r"^(\s*)([-*]) (\S.*)$")
lines = span_pre.split("\n")

# ---- parse blocks ---------------------------------------------------------
blocks, k = [], 0
while k < len(lines):
    m = BRE.match(lines[k])
    if not m:
        blocks.append(("text", [lines[k]]))
        k += 1
        continue
    body_start = k + 1
    e = body_start
    while e < len(lines):
        nxt = lines[e]
        if nxt.strip() == "" or BRE.match(nxt) or not nxt.startswith(" "):
            break
        e += 1
    blocks.append(("bullet", [lines[k]] + lines[body_start:e]))
    k = e

bullets = [b for t, b in blocks if t == "bullet"]
assert len(bullets) == 15, "expected 15 bullet blocks, found %d" % len(bullets)
seen = {}
for b in bullets:
    op = b[0]
    assert op in MAP, "unmapped bullet opener: %r" % op[:70]
    seen[op] = seen.get(op, 0) + 1
for op, c in seen.items():
    assert c == 1, "opener matched %d blocks (must be 1): %r" % (c, op[:60])
assert set(seen) == set(MAP), "unused map entries: %r" % (set(MAP) - set(seen))

# ---- literal-aware reflow -------------------------------------------------
# A prose paragraph is re-wrapped to <=WRAP chars, but never inside a span
# that a verifier asserts verbatim: protected literal occurrences are atoms.
# This is the l122 wrap-fragility lesson turned into a tool — the gate below
# is still the net, this just stops it from firing for cosmetic reasons.
WRAP = 78
_LITS = sorted(json.load(open(os.path.join(OUT, "literals.json")))["literals"],
               key=len, reverse=True)
_PROT = [re.sub(r"\s+", " ", s) for s in _LITS if len(re.sub(r"\s+", " ", s)) > 3]

def reflow(text):
    t = re.sub(r"\s+", " ", text).strip()
    if not t:
        return []
    guard = [False] * len(t)
    for p in _PROT:
        start = 0
        while True:
            k2 = t.find(p, start)
            if k2 < 0:
                break
            for q in range(k2, k2 + len(p)):
                guard[q] = True
            start = k2 + 1
    # break candidates: spaces not inside a protected span
    breaks = [q for q, ch in enumerate(t) if ch == " " and not guard[q]]
    out_lines, line_start = [], 0
    while line_start < len(t):
        if len(t) - line_start <= WRAP:
            out_lines.append(t[line_start:])
            break
        cand = [b for b in breaks if line_start < b <= line_start + WRAP]
        if not cand:                      # an atom longer than WRAP: let it ride
            nxt = [b for b in breaks if b > line_start + WRAP]
            if not nxt:
                out_lines.append(t[line_start:])
                break
            b = nxt[0]
        else:
            b = cand[-1]
        out_lines.append(t[line_start:b])
        line_start = b + 1
    return out_lines

# ---- build the new span ---------------------------------------------------
# Units are either verbatim source lines ('raw') or converted prose
# paragraphs ('para'). Consecutive bullets carry no blank line between them,
# so each converted block opens a new paragraph unless its predecessor
# declared join=True (§2.1's four bullets become one paragraph, §2.2's four
# become two). A blank source line is swallowed ONLY between two joined
# bullets — never before a heading (that bug ate the §2.2 header's blank).
units, join_prev = [], False
for bi, (kind, body) in enumerate(blocks):
    if kind == "text":
        nxt_is_bullet = (bi + 1 < len(blocks) and blocks[bi + 1][0] == "bullet")
        if join_prev and body[0].strip() == "" and nxt_is_bullet:
            continue
        units.append(("raw", body[0]))
        join_prev = False
        continue
    spec = MAP[body[0]]
    rest = body[1 + spec["eat"]:]
    flat = []
    for ln in rest:
        s = ln.strip()
        if LETTERED.match(ln):
            flat.append("")           # lettered neighbour starts a paragraph
        flat.append(s)
    para = spec["new"] + flat
    if spec.get("fix"):
        txt = "\n".join(para)
        for old, new in spec["fix"]:
            assert txt.count(old) == 1, "fix pattern %r hit %d sites" % (old, txt.count(old))
            txt = txt.replace(old, new)
        para = txt.split("\n")
    subs = [s for s in "\n".join(para).split("\n\n") if s.strip()]
    for si, sub in enumerate(subs):
        if si == 0 and join_prev and units and units[-1][0] == "para":
            units[-1] = ("para", units[-1][1] + " " + sub)
        else:
            units.append(("para", sub))
    join_prev = bool(spec.get("join"))

out = []
for ui, (kind, val) in enumerate(units):
    if kind == "raw":
        out.append(val)
        continue
    if out and out[-1].strip() != "":
        out.append("")
    out.extend(reflow(val))
    nxt = units[ui + 1] if ui + 1 < len(units) else None
    if nxt and (nxt[0] == "para" or nxt[1].strip() != ""):
        out.append("")
new_span = "\n".join(out)

# ---- gates ----------------------------------------------------------------
NUM = re.compile(r"[-+−]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|×)?")
CIT = re.compile(r"\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]")
BUL = re.compile(r"^\s*[-*]\s+\S", re.M)
norm = lambda s: re.sub(r"\s+", " ", s)

n_old, n_new = sorted(NUM.findall(span_pre)), sorted(NUM.findall(new_span))
c_old, c_new = sorted(CIT.findall(span_pre)), sorted(CIT.findall(new_span))
assert n_old == n_new, ("T1 BREACH (branch B2_tokens_moved): numeric multiset "
                        "changed. only-old=%r only-new=%r"
                        % (sorted(set(n_old) - set(n_new)), sorted(set(n_new) - set(n_old))))
assert c_old == c_new, ("T1 BREACH: citation-key multiset changed. %r / %r"
                        % (sorted(set(c_old) - set(c_new)), sorted(set(c_new) - set(c_old))))
assert len(BUL.findall(new_span)) == 0, "bullet lines remain in the span"

LIT = json.load(open(os.path.join(OUT, "literals.json")))["literals"]
WRAP_EXEMPT = ["NOT\n  MET", "not that\n    identity matters"]
missing, exempt_ok = [], []
for s in LIT:
    if s in new_span:
        continue
    if s in WRAP_EXEMPT:
        assert norm(s) in norm(new_span), "declared wrap-fragile literal lost: %r" % s
        exempt_ok.append(s)
    else:
        missing.append(s)
assert not missing, ("branch B3_literal_lost: %d literal(s) not verbatim: %r"
                     % (len(missing), [m[:60] for m in missing]))

# P3: the scramble sub-block is untouched
scr_i = span_pre.index("**Scramble controls:")
scr_j = span_pre.index("### 2.3 ")
assert span_pre[scr_i:scr_j] in new_span, "P3: the scramble block changed"

# P4 / T5: no long new sentences inside the span. Table rows carry no
# sentence punctuation, so a pipe table would read as one giant "sentence" —
# measure prose only (the same exclusion l159 makes).
prose_lines = [ln for ln in new_span.split("\n")
               if not ln.lstrip().startswith(("|", "#", "**Scramble"))]
sents = [x for x in re.split(r"(?<=[.!?])\s+", norm("\n".join(prose_lines))) if x.strip()]
longest = max(len(x.split()) for x in sents)
vis = lambda s: len(re.sub(r"\s", "", s))

rep = dict(
  chars_pre=len(span_pre), chars_post=len(new_span),
  char_delta=len(new_span) - len(span_pre),
  char_delta_pct=round(100.0 * (len(new_span) - len(span_pre)) / len(span_pre), 2),
  visible_chars_pre=vis(span_pre), visible_chars_post=vis(new_span),
  visible_char_delta=vis(new_span) - vis(span_pre),
  bullets_pre=len(BUL.findall(span_pre)), bullets_post=len(BUL.findall(new_span)),
  numeric_tokens=len(n_new), numeric_multiset_identical=(n_old == n_new),
  citation_tokens=len(c_new), citation_multiset_identical=(c_old == c_new),
  literals_checked=len(LIT), literals_verbatim=len(LIT) - len(exempt_ok),
  literals_wrap_exempt=exempt_ok, longest_sentence_words=longest,
  paragraphs=len([p for p in new_span.split("\n\n") if p.strip()]),
)
json.dump(rep, open(os.path.join(OUT, "emit_report.json"), "w"), indent=1)
for k2, v in rep.items():
    print("%-32s %s" % (k2, v))

if "--apply" not in sys.argv:
    open(os.path.join(OUT, "span_post_preview.txt"), "w").write(new_span)
    print("\nDRY RUN — preview written, draft untouched. Re-run with --apply.")
    sys.exit(0)

open(os.path.join(OUT, "span_post.txt"), "w").write(new_span)
open(DRAFT, "w").write(draft[:i] + new_span + draft[j:])
print("\nSPLICED: §1-§2.3 bullets -> prose (single-block substitution).")
