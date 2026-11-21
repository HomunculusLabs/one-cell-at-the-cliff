#!/usr/bin/env python3
"""L174 (b3b-iii) step 1 — freeze the §2.7 span and harvest every verifier
literal that lives inside it (the tick-206 lesson as step one; inherited from
l174b3bii/harvest.py with the span and the bullet pin changed).

Span = the exact draft slice from '### 2.7 Pre-posting controls' through the
character immediately before '### 2.8 The slow line' (tick-207 ADDENDUM 2:
freeze the EXACT slice, never a re-joined line list). No frozen sub-slice is
needed this stage — tick 209's sub-slice instrument existed only because
§2.7 sat inside that tick's natural span; here the span IS §2.7.

Harvest floor is 4 chars (tick-208 lesson: an 8-char floor silently drops
short number phrases such as '0 of 20', and a numeric MULTISET gate is
structurally blind to a lost adjacency).

Writes span_pre.txt (byte-exact pre-image) and literals.json.
No draft edit, no numbers.json touch.
"""
import ast, json, os, re, sys

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b3biii"
VERIFIERS = ["l143_verify.py", "l149_verify.py", "l158_verify.py",
             "l159_verify.py", "l161_verify.py", "l174_verify.py"]

START = "### 2.7 Pre-posting controls"
END = "### 2.8 The slow line"

draft = open(os.path.join(PAPER, "DRAFT.md")).read()
i = draft.index(START)
j = draft.index(END)
span = draft[i:j]
assert span.endswith("\n"), "span must keep its trailing newline(s)"
BULLET = re.compile(r"^\s*[-*]\s+\S", re.M)
n_bul = len(BULLET.findall(span))
assert n_bul == 16, (
    "the live span carries %d bullets, expected 16 "
    "— refusing to freeze an already-spliced span" % n_bul)
open(os.path.join(OUT, "span_pre.txt"), "w").write(span)

# T6 pins: the two bold leads and the three non-bullet paragraphs
BOLD = ["**Displacement is not removal, and the class axis is specific "
        "(stage c2).**",
        "**The XOR pair at swapped gains: identity wins in both gain columns\n"
        "(stage d).**"]
for b in BOLD:
    assert span.count(b) == 1, "bold lead pin moved: %r" % b[:40]

# ---- literal harvest -------------------------------------------------------
lits = {}
MINLEN = 4
for v in VERIFIERS:
    src = open(os.path.join(PAPER, v)).read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if len(s) >= MINLEN and len(re.sub(r"[^0-9A-Za-z]", "", s)) >= 2:
                lits.setdefault(s, set()).add(v)

in_span = {}
for s, vs in lits.items():
    if s in span:
        n_draft = draft.count(s)
        n_span = span.count(s)
        in_span[s] = {
            "verifiers": sorted(vs),
            "n_span": n_span,
            "n_elsewhere": n_draft - n_span,
            "multiline": "\n" in s,
        }

excl = [s for s, d in in_span.items() if d["n_elsewhere"] == 0]
multi = [s for s, d in in_span.items() if d["multiline"]]

NUM = re.compile(r"[-+−]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|×)?")
CIT = re.compile(r"\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]")

nums = sorted(NUM.findall(span))
keys = sorted(CIT.findall(span))

rep = {
    "span_chars": len(span),
    "span_lines": span.count("\n"),
    "bullet_lines": n_bul,
    "numeric_tokens": len(nums),
    "numeric_distinct": len(set(nums)),
    "citation_key_tokens": len(keys),
    "citation_keys_distinct": len(set(keys)),
    "literals_in_span": len(in_span),
    "literals_exclusive_to_span": len(excl),
    "literals_multiline": len(multi),
}
json.dump({"report": rep, "literals": in_span, "nums": nums, "keys": keys},
          open(os.path.join(OUT, "literals.json"), "w"), indent=1,
          sort_keys=True)

for k, v in rep.items():
    print(f"{k:34s} {v}")
print("\n-- MULTILINE literals (the declared T3 exception candidates) --")
for s in multi:
    print(repr(s))
print("\n-- bullet first-lines --")
for n, m in enumerate(re.finditer(r"^\s*[-*]\s+(.{0,76})", span, re.M)):
    print("  %2d %s" % (n + 1, m.group(1)))
