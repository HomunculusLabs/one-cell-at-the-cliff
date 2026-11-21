#!/usr/bin/env python3
"""L174 stage (b1): emit reference entries 36/37 and their bib records from the
STORED primary responses, and splice them into the draft list + references.bib.

Every bibliographic field comes from l174b/refs_b.json (rule R1). The only
transforms are author-list formatting and the "et al." cut at >3 authors.
Idempotent: refuses to run twice (checks for the DOI already present).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, "..", ".."))
PAPER = os.path.join(LAB, "paper")
REFS = json.load(open(os.path.join(HERE, "refs_b.json")))["accepted"]

ORDER = [("habib2026", 36), ("matsliah2026vnc", 37)]


def authors(rec, cut=3):
    people = [a.strip() for a in rec["authors"].split(";") if a.strip()]
    people = [p for p in people if not p.lower().startswith("the ")]
    if len(people) > cut:
        return ", ".join(people[:cut]) + ", et al."
    return ", ".join(people[:-1]) + " & " + people[-1]


def wrap(text, first_indent, cont_indent, width=78):
    words, lines, cur = text.split(), [], first_indent
    for w in words:
        cand = (cur + " " + w) if cur.strip() else cur + w
        if len(cand) > width and cur.strip():
            lines.append(cur)
            cur = cont_indent + w
        else:
            cur = cand
    lines.append(cur)
    return "\n".join(lines)


draft_path = os.path.join(PAPER, "DRAFT.md")
bib_path = os.path.join(PAPER, "references.bib")
draft = open(draft_path).read()
bib = open(bib_path).read()

list_block, bib_block = [], []
for key, n in ORDER:
    rec = REFS[key]
    assert rec["accept"], key
    txt = ("%s %s. bioRxiv (2026). doi:%s (version %s, posted %s)."
           % (authors(rec), rec["title"], rec["doi"], rec["version"], rec["date"]))
    list_block.append(wrap("%d. %s" % (n, txt), "", "    "))
    first = [a.strip() for a in rec["authors"].split(";") if a.strip()
             and not a.strip().lower().startswith("the ")]
    bib_block.append(
        "@article{%s,\n"
        "  title        = {%s},\n"
        "  author       = {%s},\n"
        "  year         = {2026},\n"
        "  journal      = {bioRxiv},\n"
        "  doi          = {%s},\n"
        "  note         = {preprint version %s, posted %s; %s licence; fields "
        "from the bioRxiv details API, stored in banc/l174b/raw/}\n"
        "}\n" % (key, rec["title"], " and ".join(first), rec["doi"],
                 rec["version"], rec["date"], rec["license"]))

for key, _ in ORDER:
    if REFS[key]["doi"] in draft:
        sys.exit("already spliced (%s present) — nothing to do" % key)

anchor = "\n## Verification (this skeleton)"
assert draft.count(anchor) == 1
draft = draft.replace(anchor, "\n" + "\n".join(list_block) + "\n" + anchor, 1)

prov_old = ("on 2026-11-20 with every field copied programmatically from a live primary\n"
            "record (Crossref works API, bioRxiv details API, GitHub repository API),\n"
            "stored under banc/l174a/raw/.")
assert draft.count(prov_old) == 1
draft = draft.replace(prov_old, prov_old[:-1] + (
    "; entries 36-37 were added the same\n"
    "day from the bioRxiv details API under the same rule, stored under\n"
    "banc/l174b/raw/ (the legacy 10.1101 form of both identifiers returns \"no\n"
    "posts found\" and is recorded as a control fetch)."), 1)

open(draft_path, "w").write(draft)
open(bib_path, "a").write("\n" + "\n".join(bib_block))
print("spliced entries %s" % [n for _, n in ORDER])
print("\n".join(list_block))
