"""L174 stage (a): splice the emitted entries into references.bib and DRAFT.md.

Both targets are appended to, never renumbered (PREREG R4). The emitted text is
read from emit_bib.txt / emit_list.md, which l174a_emit.py built from the stored
primary API records — this script does no formatting of its own.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.abspath(os.path.join(HERE, "..", "..", "paper"))
BIB = os.path.join(PAPER, "references.bib")
DRAFT = os.path.join(PAPER, "DRAFT.md")

bib_new = open(os.path.join(HERE, "emit_bib.txt")).read().rstrip("\n")
md_new = open(os.path.join(HERE, "emit_list.md")).read().rstrip("\n")
refs = json.load(open(os.path.join(HERE, "refs.json")))

# ---- references.bib -------------------------------------------------------
bib = open(BIB).read()
assert "namiki2018" not in bib, "bib already spliced"
n_before = len(re.findall(r"^@", bib, re.M))
header = (
    "\n%% L174 stage (a) — the reviewer's missing-citation list, every field\n"
    "%% COPIED from a live primary record (Crossref works API, bioRxiv details\n"
    "%% API, GitHub repository API) stored under banc/l174a/raw/ on 2026-11-20.\n"
    "%% Preprint-only entries use bioRxiv's CURRENT 10.64898 DOI prefix: the\n"
    "%% 10.1101 form of the same identifier returns 'no posts found'.\n"
    "%% eLife reviewed-preprint records (10.7554/eLife.<n>.<v>) are cited as such.\n\n")
bib = bib.rstrip("\n") + "\n" + header + bib_new + "\n"
open(BIB, "w").write(bib)
n_after = len(re.findall(r"^@", bib, re.M))
print("references.bib: %d -> %d entries" % (n_before, n_after))

# ---- DRAFT.md references list --------------------------------------------
d = open(DRAFT).read()
assert "34. Sapkal" not in d, "draft list already spliced"
old_head = ("All entries verified against the publisher or preprint server on 2026-11-19\n"
            "(L152; primary-source check, no citation from memory). BibTeX keys in\n"
            "paper/references.bib.\n")
new_head = ("Entries 1–13 were verified against the publisher or preprint server on\n"
            "2026-11-19 (L152) and re-resolved on 2026-11-20; entries 14–35 were added\n"
            "on 2026-11-20 with every field copied programmatically from a live primary\n"
            "record (Crossref works API, bioRxiv details API, GitHub repository API),\n"
            "stored under banc/l174a/raw/. No citation is written from memory. BibTeX\n"
            "keys in paper/references.bib.\n")
assert d.count(old_head) == 1, "reference header anchor not unique"
d = d.replace(old_head, new_head)

anchor = "\n## Verification (this skeleton)"
assert d.count(anchor) == 1
tail_marker = "    2026.01.04.697356 (2026).\n"
assert d.count(tail_marker) == 1, "entry-13 tail anchor not found"
d = d.replace(tail_marker, tail_marker + md_new + "\n")
open(DRAFT, "w").write(d)

nums = [int(m) for m in re.findall(r"^(\d+)\. ", d.split("## References")[1], re.M)]
print("draft list numbers: %d..%d (count %d, contiguous=%s)"
      % (min(nums), max(nums), len(nums), nums == list(range(1, len(nums) + 1))))
print("accepted records used: %d" % len(refs["accepted"]))
