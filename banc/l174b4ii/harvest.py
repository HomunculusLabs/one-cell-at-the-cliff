#!/usr/bin/env python3
"""L174 (b4-ii) step 1 — freeze §2.8 and harvest every verifier literal that
lives in it (the tick-206 lesson as step one; inherited from
l174b4i/harvest.py with the span changed and the bullet pin replaced by a
sentence pin, since §2.8 carries no bullets any more).

Span = the exact draft slice from '### 2.8 The slow line' through the
character immediately before '### 2.9 Statistics' (tick-207 ADDENDUM 2:
freeze the EXACT slice, never a re-joined line list).

Harvest floor 4 chars (tick-208 lesson).
Writes s28_pre.txt and literals.json. No draft edit, no numbers.json touch.
"""
import ast, json, os, re

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b4ii"
VERIFIERS = ["l143_verify.py", "l149_verify.py", "l158_verify.py",
             "l159_verify.py", "l161_verify.py", "l174_verify.py"]

START = "### 2.8 The slow line"
END = "### 2.9 Statistics"

draft = open(os.path.join(PAPER, "DRAFT.md")).read()
span = draft[draft.index(START):draft.index(END)]
assert span.endswith("\n"), "span must keep its trailing newline(s)"
BULLET = re.compile(r"^\s*[-*]\s+\S", re.M)
assert len(BULLET.findall(span)) == 0, "§2.8 should carry no bullets (b3b-ii)"
open(os.path.join(OUT, "s28_pre.txt"), "w").write(span)

# ---- literal harvest -------------------------------------------------------
lits = {}
MINLEN = 4
for v in VERIFIERS:
    tree = ast.parse(open(os.path.join(PAPER, v)).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if len(s) >= MINLEN and len(re.sub(r"[^0-9A-Za-z]", "", s)) >= 2:
                lits.setdefault(s, set()).add(v)

in_span = {}
for s, vs in lits.items():
    if s in span:
        in_span[s] = {"verifiers": sorted(vs), "n_span": span.count(s),
                      "n_elsewhere": draft.count(s) - span.count(s),
                      "multiline": "\n" in s}
multi = [s for s, d in in_span.items() if d["multiline"]]

NUM = re.compile(r"[-+\u2212]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|\u00d7)?")
CIT = re.compile(r"\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]")
nums = sorted(x.rstrip(",") for x in NUM.findall(span))
keys = sorted(CIT.findall(span))

# ---- sentence scan, measured PER PARAGRAPH with table paragraphs excluded
# (l149 §(26)'s form: a flattened markdown table reads as one long
# pseudo-sentence and masks the real offender).
norm = lambda s: re.sub(r"\s+", " ", s)
ABB = re.compile(r"(?<![A-Z])(?<!Fig)(?<!cf)(?<!vs)(?<!e\.g)(?<!i\.e)"
                 r"(?<!approx)(?<![.])([.!?]) +(?=[\"\u201c(\u00a7*A-Z0-9])")
def sents(t):
    t = norm(t).strip()
    return [s for s in ABB.sub(r"\1\n", t).split("\n") if s.strip()]

cand = []
for p in span.split("\n\n"):
    if not p.strip() or any(l.lstrip().startswith("|") for l in p.split("\n")):
        continue
    cand += [(len(s.split()), s) for s in sents(p)]
cand.sort(reverse=True)

rep = {"span_chars": len(span), "span_lines": span.count("\n"),
       "paragraphs": len([p for p in span.split("\n\n") if p.strip()]),
       "numeric_tokens": len(nums), "citation_key_tokens": len(keys),
       "literals_in_span": len(in_span), "literals_multiline": len(multi),
       "sentences_over_60w": len([1 for w, _ in cand if w > 60]),
       "longest_sentence_words": cand[0][0]}
json.dump({"report": rep, "literals": in_span, "nums": nums, "keys": keys,
           "sentences_desc": cand[:8]},
          open(os.path.join(OUT, "literals.json"), "w"), indent=1,
          sort_keys=True)

for k, v in rep.items():
    print("%-26s %s" % (k, v))
print("\n-- MULTILINE literals (declared T3 exception candidates) --")
for s in multi:
    print(repr(s))
print("\n-- longest sentences --")
for w, s in cand[:5]:
    print("  %3d  %s" % (w, s[:160]))
