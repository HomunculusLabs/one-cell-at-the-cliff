
## L174 (b3b-i) — bullets to prose in §1/§2.1/§2.2/§2.3 (tick 208, 2026-11-21)

Stage (b3b) sliced by section group: (b3b-i) §1 + §2.1 + §2.2 + §2.3 = 15
bullets (THIS), (b3b-ii) §2.5 + §2.6 + §2.8 = 11, (b3b-iii) §2.7 = 16. §1
first because it is read first and is the only block the sentence-length
gate covers.

PREREG banc/l174b3b/PREREG.md first. Contract T1 = FORMAT-ONLY, proved:
the span's numeric-token multiset (355) and citation-key multiset (45)
identical before/after, allowed delta EMPTY — strictly stronger than (b2)'s
relocation rule and (b3)'s de-duplication rule, both of which let a token
leave its block. Branch precedence B2_tokens_moved > B1_format_only.
CERT-1 six verifies green pre-edit, CERT-2 numbers.json pre-copy
(238bf2d37f51, byte-identical at the end), CERT-3 exact-slice freeze +
one-shot emit, CERT-4 the transform is PARSED (15 bullet blocks found by
regex, every opener mapped exactly once, no unused map entry), body lines
de-indented mechanically, only the 15 openers re-authored.

Result: branch B1_format_only. 15 bullet lines -> 0, 24 paragraphs,
184/184 harvested verifier literals verbatim, scramble block (table + three
numbered findings) byte-unchanged, raw chars -2.48% while VISIBLE chars
+145.

### Lessons

1. A NUMERIC MULTISET GATE IS BLIND TO LOST ADJACENCY. Run 1 harvested
   verifier literals at a >=8-char floor, which dropped SHORT number
   phrases; the reflow then split '0 of 20' (7 chars) across a line. Both
   tokens survived, so T1 passed — and l149 went honestly red afterwards.
   Harvest gate literals at a 4-char floor with a punctuation-only filter
   (>=2 alphanumerics), or short number phrases are unprotected. The
   verifier suite, not the stage's own report, is what caught it: a
   format-only proof is necessary and NOT sufficient.
2. LITERAL-AWARE REFLOW is the reusable instrument: re-wrap prose to 78
   columns treating every asserted literal occurrence as an unbreakable
   atom. Built here, inherited by (b3b-ii)/(b3b-iii). It is the l122
   wrap-fragility lesson turned into a tool instead of a bug report.
3. WRAP-FRAGILE GATES GET NORMALIZED, NOT RE-WORDED. Two required phrases
   matched only with the old bullet INDENTATION baked in ('NOT\n  MET',
   'not that\n    identity matters'); the claim text is unchanged and the
   gates now read a whitespace-normalized view. Applying the same
   normalization to the FORBIDDEN loops is a strengthening (a superseded
   wording cannot re-enter under a different wrap). Third instance landed
   inside the new section itself ('The\nU-law is read with pooled'), so:
   any multi-word gate on REFLOWED prose must be normalized by default.
4. REPORT THE VISIBLE-CHARACTER DELTA on any de-indenting pass. The raw
   count fell 2.48% here purely from stripped leading spaces, which reads
   as deletion; whitespace-stripped length (+145) is the honest measure of
   whether prose was added. Prediction Q1 (+1..+4% raw) was WRONG for
   exactly this reason and is scored as wrong.
5. A NUMBERED ENUMERATION IS NOT A BULLET LIST. The §2.2 scramble block
   (table + 1./2./3. findings) is prose convention and was pinned
   byte-identical rather than converted; the referee's complaint was
   bullet lines.
6. Card-text measurement again (L44 class): the inherited (b3b) spec said
   "42 bullet lines in §1-§2" as one job; measured per-section counts made
   the slice obvious and the slice boundaries are now in the queue text.
