#!/usr/bin/env python3
"""L174 stage (b3b-iii) — bullets to prose in §2.7 (the pre-posting controls).

Final slice of (b3b). Format-only by construction and by gate (PREREG T1):
the numeric-token and citation-key multisets of the edited span must be
IDENTICAL before and after. No frozen sub-slice is needed this stage (tick
209's instrument existed only because §2.7 sat inside that tick's span).

Body lines are de-indented mechanically; three of the sixteen openers are
already full sentences and are de-dashed by the PARSER rather than retyped
(CERT-4); the stage-(d) anchors block is the one block re-authored over its
full body, to split a 67-word sentence (PREREG ADDENDUM 1-b).
One-shot: refuses to run twice.
"""
import json, os, re, sys

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b3biii"
DRAFT = os.path.join(PAPER, "DRAFT.md")

START, END = "### 2.7 Pre-posting controls", "### 2.8 The slow line"

span_pre = open(os.path.join(OUT, "span_pre.txt")).read()
draft = open(DRAFT).read()
i = draft.index(START)
j = draft.index(END)
live = draft[i:j]
assert live == span_pre, ("T4/CERT-3: live span differs from the freeze — "
                         "emit.py refuses to run (already spliced?)")

# --------------------------------------------------------------------------
# The rewrite map. Key = the bullet's exact opener line (dash included).
# new=None   -> DEDASH: the opener is already a full prose sentence, so the
#               parser strips '- ' and nothing is retyped (3 of 16 blocks).
# new=[...]  -> re-authored opener; every numeric token and citation key of
#               the line(s) it replaces is carried over verbatim (T1).
# 'eat' = how many BODY lines the replacement consumes (only the stage-(d)
#               anchors block uses eat>0, per ADDENDUM 1-b).
# 'join' = the paragraph continues into the next converted block.
# --------------------------------------------------------------------------
MAP = {
 # ---- stage (a): the gain-swap 2x2 ---------------------------------------
 "- 2x2 on Ti right-side duty [l169.grid]: graph-wA at its own gain": dict(
   new=["The 2x2 on Ti right-side duty divides along both axes [l169.grid].",
        "Graph-wA at its own gain is"], eat=0),
 "- Paired on the same batch [l169.swap_legs]: `n25gW` sits +.276 above cutwA": dict(
   new=["Paired on the same batch [l169.swap_legs], `n25gW` sits +.276 above cutwA"],
   eat=0, join=True),
 "- Registered branch D1 fired [l169.branch]: the transition follows the": dict(
   new=None, eat=0),
 "- Probe and anchors: the swap arms are deliberately off their matched": dict(
   new=["The probe and its anchors are reported next. The swap arms are",
        "deliberately off their matched"], eat=0),
 "- Batch unions re-pooled with B35 [l169.pooled]: silW 42/48 (lb .753, three": dict(
   new=["The batch unions were re-pooled with B35 [l169.pooled]: silW 42/48 (lb .753, three"],
   eat=0),
 # ---- stage (c2): rewire + deletion ---------------------------------------
 "- Rewire [l169c2.rew]: three independent draws of the registered": dict(
   new=["On the rewire arm [l169c2.rew], three independent draws of the registered"],
   eat=0, join=True),
 "- Registered reading [l169c2.branch]: the 2-of-3 majority fires": dict(
   new=["The registered reading [l169c2.branch] is that the 2-of-3 majority fires"],
   eat=0),
 "- Not a gain artifact [l169c2.gains]: the three draws' re-bisected gains": dict(
   new=["This is not a gain artifact [l169c2.gains]: the three draws' re-bisected gains"],
   eat=0),
 "- Deletion [l169c2.hom]: deleting gi 928 — same footprint, different": dict(
   new=["On the deletion arm [l169c2.hom], deleting gi 928 — same footprint, different"],
   eat=0),
 "- Anchors [l169c2.cert]: all twelve inherited arms are bit-identical to the": dict(
   new=["The anchors hold [l169c2.cert]: all twelve inherited arms are bit-identical to the"],
   eat=0),
 # ---- stage (d): the XOR pair at swapped gains ----------------------------
 "- Own-gain diagonal reproduces on B38 [l169d.grid]: cutng25 SUPER (meanR": dict(
   new=["The own-gain diagonal reproduces on B38 [l169d.grid]: cutng25 SUPER (meanR"],
   eat=0, join=True),
 "- Off-diagonal [l169d.grid]: the twin graph run at the carrier arm's": dict(
   new=["Off the diagonal [l169d.grid], the twin graph run at the carrier arm's"],
   eat=0),
 "- Read at FIXED gain, the contrast is maximal [l169d.legs]: at": dict(
   new=None, eat=0, join=True),
 "- Registered branch E1_graph_tracking fired [l169d.branch], the strongest": dict(
   new=None, eat=0),
 "- Honest boundaries. The twin arm sits AT the NOT-SUPER boundary on this": dict(
   new=["The boundaries are reported honestly. The twin arm sits AT the NOT-SUPER boundary on this"],
   eat=0),
 # ADDENDUM 1-b: the only full-body re-author — a 67-word sentence split at
 # its own clause boundaries into three, no token moved.
 "- Anchors [l169d.cert]: all sixteen inherited arms bit-identical to the": dict(
   new=["The anchors hold [l169d.cert]. All sixteen inherited arms are",
        "bit-identical to the prior run at the anchor seeds (max 0.0), and the twin",
        "arm is additionally bit-identical to the much earlier run that first",
        "rolled it (max 0.0), which certifies the new arm's wiring for free. Its",
        "fresh bisect re-lands the stored gain exactly; staircase residual",
        "5.4e-07; each swap arm separates from its own-gain self in the motor",
        "trace (min 1.9e-2)."], eat=5),
}

BRE = re.compile(r"^(\s*)([-*]) (\S.*)$")
lines = span_pre.split("\n")

# ---- parse blocks ---------------------------------------------------------
def nxt_nonblank(k):
    while k < len(lines) and lines[k].strip() == "":
        k += 1
    return k

blocks, k = [], 0
while k < len(lines):
    m = BRE.match(lines[k])
    if not m:
        blocks.append(("text", [lines[k]]))
        k += 1
        continue
    body = []
    e = k + 1
    while e < len(lines):
        ln = lines[e]
        if ln.strip() == "":
            nb = nxt_nonblank(e)
            if (nb < len(lines) and lines[nb].startswith("  ")
                    and not BRE.match(lines[nb])):
                body.extend(lines[e:nb])
                e = nb
                continue
            break
        if BRE.match(ln) or not ln.startswith(" "):
            break
        body.append(ln)
        e += 1
    blocks.append(("bullet", [lines[k]] + body))
    k = e

bullets = [b for t, b in blocks if t == "bullet"]
assert len(bullets) == 16, "expected 16 bullet blocks, found %d" % len(bullets)
seen = {}
for b in bullets:
    op = b[0]
    assert op in MAP, "unmapped bullet opener: %r" % op[:72]
    seen[op] = seen.get(op, 0) + 1
for op, c in seen.items():
    assert c == 1, "opener matched %d blocks (must be 1): %r" % (c, op[:60])
assert set(seen) == set(MAP), "unused map entries: %r" % (set(MAP) - set(seen))

# ---- literal-aware reflow (tick-208 instrument) ---------------------------
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
    breaks = [q for q, ch in enumerate(t) if ch == " " and not guard[q]]
    out_lines, line_start = [], 0
    while line_start < len(t):
        if len(t) - line_start <= WRAP:
            out_lines.append(t[line_start:])
            break
        cand = [b for b in breaks if line_start < b <= line_start + WRAP]
        if not cand:
            nx = [b for b in breaks if b > line_start + WRAP]
            if not nx:
                out_lines.append(t[line_start:])
                break
            b = nx[0]
        else:
            b = cand[-1]
        out_lines.append(t[line_start:b])
        line_start = b + 1
    return out_lines

# ---- build the new span ---------------------------------------------------
def split_chunks(body_lines):
    """body -> list of ('para', text) / ('tbl', rows), blank-line separated."""
    chunks, cur = [], []
    for ln in body_lines + [""]:
        if ln.strip() == "":
            if cur:
                if all(c.lstrip().startswith("|") for c in cur):
                    chunks.append(("tbl", [c.strip() for c in cur]))
                else:
                    chunks.append(("para", " ".join(c.strip() for c in cur)))
                cur = []
            continue
        cur.append(ln)
    return chunks

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
    opener = [body[0][2:].rstrip()] if spec["new"] is None else spec["new"]
    chunks = split_chunks(rest)
    if chunks and chunks[0][0] == "para":
        chunks[0] = ("para", " ".join(opener) + " " + chunks[0][1])
    else:
        chunks = [("para", " ".join(opener))] + chunks
    for ci, (ck, cv) in enumerate(chunks):
        if ci == 0 and join_prev and units and units[-1][0] == "para":
            assert ck == "para"
            units[-1] = ("para", units[-1][1] + " " + cv)
        else:
            units.append((ck, cv))
    join_prev = bool(spec.get("join"))

out = []
for ui, (kind, val) in enumerate(units):
    if kind == "raw":
        out.append(val)
        continue
    if out and out[-1].strip() != "":
        out.append("")
    out.extend(reflow(val) if kind == "para" else val)
    nxt = units[ui + 1] if ui + 1 < len(units) else None
    if nxt and (nxt[0] != "raw" or nxt[1].strip() != ""):
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
assert len(BUL.findall(new_span)) == 0, (
    "bullet census must fall to 0, found %d" % len(BUL.findall(new_span)))

LIT = json.load(open(os.path.join(OUT, "literals.json")))["literals"]
# PREREG ADDENDUM 1-a: exactly seven bullet-internal literals carry the OLD
# BULLET INDENTATION inside their own line break and cannot survive
# de-indentation. The three l149 loops that own them are made
# wrap-insensitive (claim text unchanged, strictly stronger).
WRAP_EXEMPT = ["follows the\n  GRAPH, not the gain",
               "differ per seed by up to\n  .46",
               "meanR\n  .798, kR 16/16, [.806,1.000]",
               "(.477, kR 8/16,\n  [.280,.720])",
               "meanR .651, kR 15/16,\n  [.717,.989], paired \u2212.147",
               "+.474 above the twin-removed\n  graph with 16 of 16 seeds up",
               "at g_cutng25p it is +.174 with 12 of\n  16 up"]
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
assert sorted(exempt_ok) == sorted(WRAP_EXEMPT), (
    "the exemption set must be EXACTLY the seven declared: used %r" % sorted(exempt_ok))

# T6: the two bold leads survive verbatim and stay at line start; the three
# non-bullet paragraphs come through byte-unchanged.
for lead in ("**Displacement is not removal, and the class axis is specific",
             "**The XOR pair at swapped gains: identity wins in both gain columns"):
    assert lead in new_span, "T6: bold lead lost: %r" % lead
    assert re.search(r"(?m)^" + re.escape(lead[:28]), new_span), \
        "T6: bold lead not at line start: %r" % lead
for para in ("Scope: one fresh batch per new cell, and a two-point gain probe cannot",
             "Design pins for the rewire and deletion arms are stored [l169c.design]. The",
             "With stage (d) the four pre-posting controls of this section are complete:"):
    assert para in new_span, "T6: non-bullet paragraph altered: %r" % para[:48]
# the two multiline literals in the Design-pins paragraph must be VERBATIM
for s in ("carrier's\n80", "6 shared, Jaccard\n.037"):
    assert s in new_span, "T6: raw-passthrough literal lost: %r" % s

# ADDENDUM 1-b: no sentence in the new span over 60 words
sents = [x for x in re.split(r"(?<=[.!?])\s+", norm(new_span)) if x.strip()]
longest = max(len(x.split()) for x in sents)
top = sorted(((len(x.split()), x[:60]) for x in sents), reverse=True)[:3]
assert longest <= 60, "ADDENDUM 1-b: a sentence of %d words survives: %r" % top[0]
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
  literals_wrap_exempt=sorted(exempt_ok),
  dedash_blocks=sum(1 for v in MAP.values() if v["new"] is None),
  reauthored_blocks=sum(1 for v in MAP.values() if v["new"] is not None),
  full_body_reauthored=sum(1 for v in MAP.values() if v["eat"] > 0),
  longest_sentence_words=longest, top_sentences=top,
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
print("\nSPLICED: §2.7 bullets -> prose (single-block substitution).")
