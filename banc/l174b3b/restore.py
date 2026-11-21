#!/usr/bin/env python3
"""L174 (b3b) restore step — put the frozen pre-image back into DRAFT.md.

Needed because the first splice's literal-aware reflow was fed a literal set
harvested at a >=8-char floor, which silently dropped SHORT gate literals
('0 of 20', 7 chars) and let the reflow break one across a line. The numeric
multiset gate cannot see that class of damage: both tokens survive, only
their adjacency is lost. So: restore, re-harvest at a 4-char floor, re-splice.
"""
import os, sys

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b3b"
DRAFT = os.path.join(PAPER, "DRAFT.md")

pre = open(os.path.join(OUT, "span_pre.txt")).read()
post = open(os.path.join(OUT, "span_post.txt")).read()
d = open(DRAFT).read()
assert d.count(post) == 1, "the spliced span is not present exactly once"
assert pre not in d, "the pre-image is already in place"
open(DRAFT, "w").write(d.replace(post, pre, 1))
os.rename(os.path.join(OUT, "span_post.txt"),
          os.path.join(OUT, "span_post_run1.txt"))
print("restored: §1-§2.3 is the frozen pre-image again (run-1 span kept as "
      "span_post_run1.txt)")
