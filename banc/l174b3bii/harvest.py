#!/usr/bin/env python3
"""L174 (b3b-ii) step 1 — freeze the §2.5-§2.8 span and harvest every
verifier literal that lives inside it (the tick-206 lesson as step one,
inherited from l174b3b/harvest.py with the span and the bullet pin changed).

Span = the exact draft slice from '### 2.5 Robustness' through the character
immediately before '### 2.9 Statistics' (tick-207 ADDENDUM 2: freeze the
EXACT slice, never a re-joined line list). §2.7 sits INSIDE this span and is
the (b3b-iii) job: emit.py proves it byte-identical instead of touching it.

Harvest floor is 4 chars (tick-208 lesson: an 8-char floor silently drops
short number phrases such as '0 of 20', and a numeric MULTISET gate is
structurally blind to a lost adjacency).

Writes span_pre.txt (byte-exact pre-image) and literals.json.
No draft edit, no numbers.json touch.
"""
import ast, json, os, re, sys

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b3bii"
VERIFIERS = ["l143_verify.py", "l149_verify.py", "l158_verify.py",
             "l159_verify.py", "l161_verify.py", "l174_verify.py"]

START = "### 2.5 Robustness"
END = "### 2.9 Statistics"
# §2.7 is excluded from the edit by a byte-identity gate, not by span surgery
SEV_START = "### 2.7 Pre-posting controls"
SEV_END = "### 2.8 The slow line"

draft = open(os.path.join(PAPER, "DRAFT.md")).read()
i = draft.index(START)
j = draft.index(END)
span = draft[i:j]
assert span.endswith("\n"), "span must keep its trailing newline(s)"
BULLET = re.compile(r"^\s*[-*]\s+\S", re.M)
n_bul = len(BULLET.findall(span))
assert n_bul == 27, (
    "the live span carries %d bullets, expected 27 (11 editable + §2.7's 16) "
    "— refusing to freeze an already-spliced span" % n_bul)
# the editable sub-spans (§2.5+§2.6 and §2.8) must carry exactly 11
sev = span[span.index(SEV_START):span.index(SEV_END)]
assert len(BULLET.findall(sev)) == 16, "§2.7 bullet pin moved"
assert n_bul - len(BULLET.findall(sev)) == 11, "editable bullet pin moved"
open(os.path.join(OUT, "span_pre.txt"), "w").write(span)
open(os.path.join(OUT, "sev_pre.txt"), "w").write(sev)

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
            "n_in_sev": sev.count(s),
            "multiline": "\n" in s,
        }

excl = [s for s, d in in_span.items() if d["n_elsewhere"] == 0]
multi = [s for s, d in in_span.items() if d["multiline"]]
# literals that live ONLY in §2.7 are not at risk this stage
editable = {s: d for s, d in in_span.items() if d["n_span"] > d["n_in_sev"]}
multi_edit = [s for s, d in editable.items() if d["multiline"]]

NUM = re.compile(r"[-+−]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|×)?")
CIT = re.compile(r"\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]")

nums = sorted(NUM.findall(span))
keys = sorted(CIT.findall(span))

rep = {
    "span_chars": len(span),
    "span_lines": span.count("\n"),
    "bullet_lines": n_bul,
    "bullet_lines_sev": len(BULLET.findall(sev)),
    "bullet_lines_editable": n_bul - len(BULLET.findall(sev)),
    "numeric_tokens": len(nums),
    "numeric_distinct": len(set(nums)),
    "citation_key_tokens": len(keys),
    "citation_keys_distinct": len(set(keys)),
    "literals_in_span": len(in_span),
    "literals_exclusive_to_span": len(excl),
    "literals_multiline": len(multi),
    "literals_touching_editable_text": len(editable),
    "literals_multiline_editable": len(multi_edit),
}
json.dump({"report": rep, "literals": in_span, "editable": sorted(editable),
           "nums": nums, "keys": keys},
          open(os.path.join(OUT, "literals.json"), "w"), indent=1, sort_keys=True)

for k, v in rep.items():
    print(f"{k:34s} {v}")
print("\n-- multiline literals touching editable text --")
for s in multi_edit:
    print(repr(s))
print("\n-- bullet first-lines in the EDITABLE sub-spans --")
edit_text = span[:span.index(SEV_START)] + span[span.index(SEV_END):]
for m in re.finditer(r"^\s*[-*]\s+(.{0,72})", edit_text, re.M):
    print("  *", m.group(1))
