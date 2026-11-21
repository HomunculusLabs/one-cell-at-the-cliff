#!/usr/bin/env python3
"""L174 (b3b) step 1 — freeze the §1-§2.3 span and harvest every verifier
literal that lives inside it (the tick-206 lesson, made step one again).

Span = the exact draft slice from the '## 1. Introduction' line through the
character immediately before '### 2.4' (tick-207 ADDENDUM 2: freeze the EXACT
slice, never a re-joined line list).

Writes l174b3b/span_pre.txt (byte-exact pre-image) and l174b3b/literals.json.
No draft edit, no numbers.json touch.
"""
import ast, json, os, re, sys

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b3b"
VERIFIERS = ["l143_verify.py", "l149_verify.py", "l158_verify.py",
             "l159_verify.py", "l161_verify.py", "l174_verify.py"]

draft = open(os.path.join(PAPER, "DRAFT.md")).read()
i = draft.index("## 1. Introduction")
j = draft.index("### 2.4 Mechanism")
span = draft[i:j]
assert span.endswith("\n"), "span must keep its trailing newline(s)"
assert len(re.findall(r"^\s*[-*]\s+\S", span, re.M)) == 15, (
    "the live span does not carry the 15 pre-image bullets — refusing to "
    "freeze an already-spliced span (run restore.py first)")
open(os.path.join(OUT, "span_pre.txt"), "w").write(span)

# ---- literal harvest -------------------------------------------------------
lits = {}
MINLEN = 4   # was 8 in run 1: a >=8 floor silently dropped SHORT gate
             # literals such as '0 of 20' (7 chars), which the reflow then
             # broke across a line. A numeric MULTISET gate cannot see that
             # (both tokens survive, only their adjacency is lost), so the
             # floor has to be low enough to protect number phrases.
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

# ---- token inventories of the span ----------------------------------------
NUM = re.compile(r"[-+−]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|×)?")
CIT = re.compile(r"\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]")
BULLET = re.compile(r"^\s*[-*]\s+\S", re.M)

nums = sorted(NUM.findall(span))
keys = sorted(CIT.findall(span))
bullets = BULLET.findall(span)

rep = {
    "span_chars": len(span),
    "span_lines": span.count("\n"),
    "bullet_lines": len(BULLET.findall(span)),
    "numeric_tokens": len(nums),
    "numeric_distinct": len(set(nums)),
    "citation_key_tokens": len(keys),
    "citation_keys_distinct": len(set(keys)),
    "literals_in_span": len(in_span),
    "literals_exclusive_to_span": len(excl),
    "literals_multiline": len(multi),
}
json.dump({"report": rep, "literals": in_span,
           "nums": nums, "keys": keys},
          open(os.path.join(OUT, "literals.json"), "w"), indent=1, sort_keys=True)

for k, v in rep.items():
    print(f"{k:28s} {v}")
print("\n-- multiline literals (wrapping must be preserved verbatim) --")
for s in multi:
    print(repr(s))
print("\n-- bullet first-lines in span --")
for m in re.finditer(r"^\s*[-*]\s+(.{0,70})", span, re.M):
    print("  *", m.group(1))
