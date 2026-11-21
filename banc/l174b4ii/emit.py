#!/usr/bin/env python3
"""L174 (b4-ii) step 2 — the two edits, under the PREREG contract.

E1  §2.8's inherited 70-word envelope-disclosure sentence, split
    content-preservingly (T7) by ONE declared (old, new) pair.
E2  a new '## 5. Discussion' inserted before the present '## 5. Data & code',
    which renumbers to '## 6.' and pushes '## 6. Author/submit notes' to
    '## 7.'.

Usage:  emit.py --dry-run     (measure + gate, write nothing to the draft)
        emit.py --apply       (splice; refuses if the draft is already spliced)

Inherited rules honoured here:
  * tick-207 ADDENDUM 2 — freeze the EXACT draft slice, never a re-joined
    line list; assert the live slice equals the freeze before splicing.
  * tick-209 — refuse a second run (the freeze guard does it).
  * (b4-i) ADDENDUM 2 — numeric multisets compared with trailing commas
    stripped (the regex swallows them for thousands separators).
  * (b4-i) ADDENDUM 3 — T7 is proved at SECTION level (pre-image + declared
    edits == live), not per split only.
No rollouts, no RNG, no numbers.json write.
"""
import json, os, re, sys, textwrap

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b4ii"
DRAFT = os.path.join(PAPER, "DRAFT.md")
APPLY = "--apply" in sys.argv
assert APPLY or "--dry-run" in sys.argv, "pass --dry-run or --apply"

draft = open(DRAFT).read()

# --------------------------------------------------------------- E1: the split
S28_A, S28_B = "### 2.8 The slow line", "### 2.9 Statistics"
s28_pre_frozen = open(os.path.join(OUT, "s28_pre.txt")).read()
s28 = draft[draft.index(S28_A):draft.index(S28_B)]
assert s28 == s28_pre_frozen, (
    "E1 refuses: the live §2.8 is not the frozen pre-image "
    "(already spliced, or the draft moved under us)")

# the ONE declared edit. Punctuation-for-punctuation by DESIGN (T2): ',' -> '.'
# and 'so' -> 'So' keeps whitespace-stripped length constant, so l149 §(24)'s
# visible-char pin on this very region needs no re-point.
SPLITS = [(
    "11/16 seeds [l154.band], so the envelope accounts for the line's POSITION",
    "11/16 seeds [l154.band]. So the envelope accounts for the line's POSITION",
)]
s28_post = s28
for old, new in SPLITS:
    assert s28.count(old) == 1, ("T7: declared old form must match once", old)
    assert draft.count(old) == 1, ("T7: old form must be unique in the draft", old)
    assert new not in s28, ("T7: the new form already exists", new)
    s28_post = s28_post.replace(old, new)
assert s28_post != s28

NUM = re.compile(r"[-+\u2212]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|\u00d7)?")
CIT = re.compile(r"\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]")
ns = lambda t: sorted(x.rstrip(",") for x in NUM.findall(t))
vis = lambda t: len(re.sub(r"\s+", "", t))
norm = lambda t: re.sub(r"\s+", " ", t)

# T1
assert ns(s28) == ns(s28_post), "B2_tokens_moved: §2.8 numeric multiset moved"
assert sorted(CIT.findall(s28)) == sorted(CIT.findall(s28_post)), \
    "B2_tokens_moved: §2.8 citation-key multiset moved"
# T2 (neutrality to l149 §(24)'s pins on this region)
assert vis(s28_post) == vis(s28), "T2: the split must be visible-char-neutral"
# PREREG ADDENDUM 1 (written at this assert's first failure, before any draft
# byte changed): Q1 registered a NEGATIVE raw delta, which was derived for an
# em-dash-boundary variant of the split (' — but' -> '. But' loses a space).
# The split actually chosen sits at the comma boundary (', so' -> '. So'), and
# that is byte-length-NEUTRAL as well as visible-neutral — strictly stronger
# than registered, and l149 §(24)'s raw-direction pin on the enclosing region
# (a strict inequality already satisfied) still holds. Q1 is therefore scored
# WRONG on its raw leg and CORRECT on its visible leg.
assert len(s28_post) == len(s28), "T2: the comma split must be byte-neutral"
paras = lambda t: [p for p in t.split("\n\n") if p.strip()]
assert len(paras(s28_post)) == len(paras(s28)), "T2: paragraph-count neutral"

# T7 strong form: pre-image + declared edits == post
_chk = s28
for old, new in SPLITS:
    _chk = _chk.replace(old, new)
assert _chk == s28_post, "T7: post-image is not the pre-image plus the edits"
CLOSED = {"and", "while", "so", "therefore"}
cwords = lambda t: [w for w in re.findall(r"[0-9A-Za-z][0-9A-Za-z._/'\u2212-]*",
                                          norm(t))
                    if w.lower() not in CLOSED]
assert [w.lower() for w in cwords(s28)] == [w.lower() for w in cwords(s28_post)], \
    "T7: the §2.8 content-word sequence moved"

# T3: every harvested literal survives verbatim (zero exceptions expected)
lit = json.loads(open(os.path.join(OUT, "literals.json")).read())
miss = [s for s in lit["literals"] if s not in s28_post]
assert not miss, ("B3_literal_lost", miss[:4])

# sentence rule, measured per paragraph with table paragraphs excluded
ABB = re.compile(r"(?<![A-Z])(?<!Fig)(?<!cf)(?<!vs)(?<!e\.g)(?<!i\.e)"
                 r"(?<!approx)(?<![.])([.!?]) +(?=[\"\u201c(\u00a7*A-Z0-9])")
def sents(t):
    return [s for s in ABB.sub(r"\1\n", norm(t).strip()).split("\n") if s.strip()]
def longest(sec):
    out = []
    for p in sec.split("\n\n"):
        if not p.strip() or any(l.lstrip().startswith("|") for l in p.split("\n")):
            continue
        out += [(len(s.split()), s) for s in sents(p)]
    return sorted(out, reverse=True)
L28_pre, L28_post = longest(s28), longest(s28_post)
assert L28_pre[0][0] == 70, "the pre-image must carry the pinned 70-word sentence"
assert L28_post[0][0] <= 60, ("a >60-word sentence survives in §2.8",
                              L28_post[0][0])

# ---------------------------------------------------- E2: author the Discussion
H_DATA, H_AUTH = "## 5. Data & code", "## 6. Author/submit notes"
assert draft.count(H_DATA) == 1 and draft.count(H_AUTH) == 1
assert "## 5. Discussion" not in draft, "E2 refuses: a Discussion already exists"

src = open(os.path.join(OUT, "disc_src.txt")).read().strip("\n")
blocks = [b.strip() for b in src.split("\n\n") if b.strip()]
assert blocks[0] == "## 5. Discussion", "disc_src must open with its heading"
body_blocks = blocks[1:]

# reflow to the draft's 78-column house width, with the quoted number phrases
# protected as unbreakable atoms (the tick-208 literal-aware reflow, reduced:
# the Discussion carries no provenance keys, only number phrases).
ATOMS = ["39 of 48", "78 of 98", "5 of 5", "0 of 5", "9.72\u00d7"]
# the placeholder is the SAME LENGTH as the atom it stands for (own-catch on
# the dry run: a short placeholder wraps a line to 78 and then grows past it
# when the atom is restored — a literal-aware reflow has to be
# length-preserving, not merely break-preserving)
PH = [("\u0001%d" % i).ljust(len(a), "\u0001") for i, a in enumerate(ATOMS)]
assert len(set(PH)) == len(PH) and all(len(p) == len(a)
                                       for p, a in zip(PH, ATOMS))
def reflow(p):
    tmp = p
    for a, ph in zip(ATOMS, PH):
        tmp = tmp.replace(a, ph)
    out = textwrap.fill(tmp, width=78, break_long_words=False,
                        break_on_hyphens=False)
    for a, ph in zip(ATOMS, PH):
        out = out.replace(ph, a)
    return out
disc = "## 5. Discussion\n\n" + "\n\n".join(reflow(p) for p in body_blocks) + "\n\n"
for a in ATOMS:
    assert a in disc and ("\n".join(disc.split("\n"))).count(a) == src.count(a), \
        ("reflow broke a protected atom", a)
assert max(len(l) for l in disc.split("\n")) <= 78, "house width"

# --- T8: the Discussion is born clean -------------------------------------
assert not re.search(r"(?m)^\s*[-*]\s+\S", disc), "T8: a list item in §5"
assert not re.search(r"\bL\d{2,3}\b", disc), "T8: a lane ID in §5"
assert not re.search(r"\bB\d{2}\b", disc), "T8: a batch code in §5"
ACR_OK = set()
caps = [w for w in re.findall(r"\b[A-Z][A-Z]{2,}\b", disc) if w not in ACR_OK]
assert not caps, ("T8: all-caps emphasis in §5", caps)
assert not CIT.findall(disc), "T8: a provenance key in §5"
assert not re.search(r"\[\d+(,\s*\d+)*\]", disc), "T8: a new citation marker in §5"
# every number the Discussion quotes must already appear VERBATIM in the draft
# (§-references are not numbers: strip them first)
scrub = re.sub(r"\u00a7\d+(\.\d+)?(\([a-d]\))?", " ", disc)
qnums = sorted(set(x.rstrip(",") for x in NUM.findall(scrub)))
unseen = [q for q in qnums if q not in draft]
assert not unseen, ("T8: a NEW numeric value entered in a prose stage", unseen)
# 60-word rule on the Discussion itself (the (b4-i) precedent: extend the gate
# that owns the region, do not widen l159's abstract/§1 scope)
L5 = longest(disc)
assert L5[0][0] <= 60, ("T8: a >60-word sentence in §5", L5[0][0], L5[0][1][:90])

# --- T9: no claim inflation ------------------------------------------------
REQ = ["sufficient route into the super class rather than the only one",
       "established prior art", "\u00a74 enumerates",
       "None of this is a statement about the animal"]
FORB = ["unique cause", "the only cell", "we prove", "proves that",
        "first demonstration", "unprecedented", "for the first time"]
for r in REQ:
    # normalized: every multi-word check on REFLOWED prose is break-insensitive
    # by default (the tick-208/209 lesson, strictly stronger than a raw match)
    assert norm(r) in norm(disc), ("T9: required statement missing", r)
for f in FORB:
    assert norm(f) not in norm(disc).lower(), ("T9: forbidden claim wording", f)

# ------------------------------------------------------------------- splice
new = draft[:draft.index(S28_A)] + s28_post + draft[draft.index(S28_B):]
new = new.replace(H_AUTH, "## 7. Author/submit notes")
new = new.replace(H_DATA, disc + "## 6. Data & code")
assert new.count("## 5. Discussion") == 1 and new.count("## 6. Data & code") == 1
assert new.count("## 7. Author/submit notes") == 1
assert new.index("## 4. Limitations") < new.index("## 5. Discussion") \
    < new.index("## 6. Data & code") < new.index("## 7. Author/submit notes")
BUL = re.compile(r"^\s*[-*]\s+\S", re.M)
body14 = new[new.index("## 1. Introduction"):new.index("## 5. Discussion")]
assert not BUL.findall(body14), "§1-§4 must still carry zero list items"

rep = {
    "s28": {"chars_pre": len(s28), "chars_post": len(s28_post),
            "visible_delta": vis(s28_post) - vis(s28),
            "raw_delta": len(s28_post) - len(s28),
            "numeric_tokens": len(ns(s28_post)),
            "citation_key_tokens": len(CIT.findall(s28_post)),
            "literals_verbatim": len(lit["literals"]),
            "longest_pre": L28_pre[0][0], "longest_post": L28_post[0][0],
            "second_longest_pre": L28_pre[1][0],
            "splits": len(SPLITS), "paragraphs": len(paras(s28_post))},
    "disc": {"chars": len(disc), "words": len(disc.split()),
             "paragraphs": len(body_blocks), "longest_sentence": L5[0][0],
             "numbers_quoted": qnums, "sentences": len(longest(disc))},
    "draft": {"chars_pre": len(draft), "chars_post": len(new)},
    "applied": bool(APPLY),
}
json.dump(rep, open(os.path.join(OUT, "emit_report.json"), "w"), indent=1,
          sort_keys=True)
print(json.dumps(rep, indent=1, sort_keys=True))
print("\n-- new longest §2.8 sentence (%d w) --\n%s" % (L28_post[0][0],
                                                        L28_post[0][1][:200]))
print("\n-- longest §5 sentence (%d w) --\n%s" % (L5[0][0], L5[0][1][:200]))

if APPLY:
    open(os.path.join(OUT, "s28_post.txt"), "w").write(s28_post)
    open(os.path.join(OUT, "disc.txt"), "w").write(disc)
    open(DRAFT, "w").write(new)
    print("\nAPPLIED: §2.8 split + §5 Discussion spliced, §5/§6 renumbered.")
else:
    open(os.path.join(OUT, "s28_post_preview.txt"), "w").write(s28_post)
    open(os.path.join(OUT, "disc_preview.txt"), "w").write(disc)
    print("\nDRY RUN: previews written, draft untouched.")
