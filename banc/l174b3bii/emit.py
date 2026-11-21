#!/usr/bin/env python3
"""L174 stage (b3b-ii) — bullets to prose in §2.5, §2.6 and §2.8.

Format-only by construction and by gate (PREREG T1): the numeric-token and
citation-key multisets of the edited span must be IDENTICAL before and after.
§2.7 sits inside the edit span and belongs to stage (b3b-iii): it is proven
BYTE-IDENTICAL rather than excluded by span surgery (PREREG P3).

Body lines are de-indented mechanically; markdown table rows are emitted
verbatim and never reflowed (P4); eight of the eleven openers need no
re-authoring at all and are de-dashed by the PARSER rather than retyped
(CERT-4, Q4). One-shot: refuses to run twice.
"""
import json, os, re, sys

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b3bii"
DRAFT = os.path.join(PAPER, "DRAFT.md")

START, END = "### 2.5 Robustness", "### 2.9 Statistics"
SEV_START, SEV_END = "### 2.7 Pre-posting controls", "### 2.8 The slow line"

span_pre = open(os.path.join(OUT, "span_pre.txt")).read()
sev_pre = open(os.path.join(OUT, "sev_pre.txt")).read()
draft = open(DRAFT).read()
i = draft.index(START)
j = draft.index(END)
live = draft[i:j]
assert live == span_pre, ("T4/CERT-3: live span differs from the freeze — "
                         "emit.py refuses to run (already spliced?)")

# --------------------------------------------------------------------------
# The rewrite map. Key = the bullet's exact opener line (dash included).
# new=None  -> DEDASH: the opener is already a full prose sentence, so the
#              parser strips '- ' and nothing is retyped (8 of 11 blocks).
# new=[...]  -> re-authored opener (the 3 label-ish §2.5 fragments).
# 'eat' = how many BODY lines the replacement consumes; 'join' = the
# paragraph continues into the next converted block.
# --------------------------------------------------------------------------
MAP = {
 # ---- §2.5: three label-ish fragments, re-authored into sentences --------
 "- 5 af-matched 1% edge-jitter gain sets + base, same seeds paired": dict(
   new=["The robustness ensemble is 5 af-matched 1% edge-jitter gain sets plus base,",
        "with the same seeds paired"], eat=0, join=True),
 "- Carrier SUPER 5/5 [sustain.cutng25]; ng23 KILL 4/5 [sustain.cutng23];": dict(
   new=["Across those sets the carrier reads SUPER 5/5 [sustain.cutng25]; ng23 KILL",
        "4/5 [sustain.cutng23];"], eat=0),
 "- Untreated full subnet stays inside its base spread across all sets": dict(
   new=["The untreated full subnet stays inside its base spread across all sets"],
   eat=0),
 # ---- §2.6: four full sentences ------------------------------------------
 "- The original comparison was UNMATCHED-FLOOR, and we corrected it": dict(
   new=None, eat=0),
 "- The window shares become computable for the first time at the matched": dict(
   new=None, eat=0),
 "- The honest status is therefore UNTESTED AT MATCHED FLOOR, not \"no": dict(
   new=None, eat=0),
 "- What DOES survive the floor match: the male DNp33 pair stays RECIPROCAL": dict(
   new=None, eat=0),
 # ---- §2.8: four bold claim leads (the house form §2.7 already uses) -----
 "- **Re-attribution (branch A1 fired).** The drive envelope is rebuilt": dict(
   new=None, eat=0),
 "- **What the envelope cannot explain (mandatory disclosure, registered": dict(
   new=None, eat=0),
 "- **Robustness panel (branch B2_preserved).** The published readout is": dict(
   new=None, eat=0),
 "- **What this does and does not license.** It licenses dropping the": dict(
   new=None, eat=0),
}

BRE = re.compile(r"^(\s*)([-*]) (\S.*)$")
lines = span_pre.split("\n")

# §2.7's line range is passed through verbatim (P3)
sev_first = next(k for k, ln in enumerate(lines) if ln.startswith(SEV_START))
sev_last = next(k for k, ln in enumerate(lines) if ln.startswith(SEV_END))
assert sev_first < sev_last

# ---- parse blocks ---------------------------------------------------------
# A bullet block continues over blank lines while the next non-empty line is
# an indented continuation (that is how §2.8's robustness panel carries its
# table and its trailing paragraph inside one bullet).
def nxt_nonblank(k):
    while k < len(lines) and lines[k].strip() == "":
        k += 1
    return k

blocks, k = [], 0
while k < len(lines):
    frozen = sev_first <= k < sev_last
    m = None if frozen else BRE.match(lines[k])
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
            if (nb < len(lines) and not (sev_first <= nb < sev_last)
                    and lines[nb].startswith("  ")
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
assert len(bullets) == 11, "expected 11 editable bullet blocks, found %d" % len(bullets)
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
# Units: ('raw', line) verbatim, ('para', text) reflowed, ('tbl', [rows])
# emitted verbatim (P4 — reflowing a pipe table destroys it).
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
assert len(BUL.findall(new_span)) == 16, (
    "bullet census must fall to §2.7's 16, found %d" % len(BUL.findall(new_span)))
# P3: §2.7 byte-identical
assert sev_pre in new_span, "P3: §2.7 is not byte-identical after the splice"
assert len(BUL.findall(sev_pre)) == 16

LIT = json.load(open(os.path.join(OUT, "literals.json")))["literals"]
WRAP_EXEMPT = ["0.1946 / 0.0642 /\n  0.1333", "agrees to\n  within .0025",
               "from 37/33 to 6/2 but never\n  reach zero"]
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

# P4: the robustness-panel table survived as a table, de-indented
tbl_rows = [ln for ln in new_span.split("\n") if ln.startswith("| ")]
assert len(tbl_rows) == 4, "P4: expected 4 de-indented table rows, got %d" % len(tbl_rows)
assert "|---|---|---|---|---|" in new_span
# P5: the four bold claim leads survive verbatim at line start
for lead in ("**Re-attribution (branch A1 fired).**",
             "**What the envelope cannot explain",
             "**Robustness panel (branch B2_preserved).**",
             "**What this does and does not license.**"):
    assert lead in new_span, "P5: bold claim lead lost: %r" % lead
    assert re.search(r"(?m)^" + re.escape(lead[:24]), new_span), \
        "P5: bold lead not at line start: %r" % lead

prose_lines = [ln for ln in new_span.split("\n")
               if not ln.lstrip().startswith(("|", "#"))]
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
  sev_byte_identical=(sev_pre in new_span),
  numeric_tokens=len(n_new), numeric_multiset_identical=(n_old == n_new),
  citation_tokens=len(c_new), citation_multiset_identical=(c_old == c_new),
  literals_checked=len(LIT), literals_verbatim=len(LIT) - len(exempt_ok),
  literals_wrap_exempt=exempt_ok, dedash_blocks=sum(1 for v in MAP.values() if v["new"] is None),
  reauthored_blocks=sum(1 for v in MAP.values() if v["new"] is not None),
  longest_sentence_words=longest,
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
print("\nSPLICED: §2.5/§2.6/§2.8 bullets -> prose (single-block substitution).")
