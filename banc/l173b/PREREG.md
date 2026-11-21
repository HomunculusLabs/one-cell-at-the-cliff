# L173 PREREG — stage (b): the §2.4 rebuild (ZERO rollouts)

Registered BEFORE any file was written or any draft line was edited.
Stage (a) (tick 201) shipped the Methods half; this stage ships the
§2.4 half the card specifies:

> Rebuild §2.4 around its cleanest arm (silW: flips at UNCHANGED gain),
> then the edge decomposition; drop the "two-factor law" framing; move
> both bit-identities to Methods as sanity checks (they hold by
> construction).

Reviewer issue I10 (CONFIRMED, banc/l167/ADJUDICATION.md row 10) is the
external statement of the same thing, and issue I4 (CONFIRMED in
direction) is what makes silW *the* clean arm: gain and identity co-vary
across the edge ladder, and silW is the one flip arm whose gain does
not move at all.

## Scope clause

- ZERO rollouts, zero RNG, no graph build, no torch, no live changes.
- NO new measurement. Every number entering §2.4 is already stored in a
  results json; the only new computation is arithmetic (percent gain
  deltas, one ratio) over stored values.
- Edits confined to: `paper/DRAFT.md` (§2.4 rebuild, the §1 sentence
  that names the retired framing, §3.8 receiving the two identities),
  `paper/numbers.json` (+ this stage's keys), `paper/l149_verify.py`
  (new section + re-anchor of the stage-(a) scope gate), `paper/
  CLAIM-MAP.md`, `paper/l158_verify.py` (freeze re-cut, see the
  SCOPE EXTENSION below), `banc/l173b/*`.

## SCOPE EXTENSION (registered, with reason)

The card does not mention the mass ratio, but §2.4 carries the number
reviewer issue I8 found wrong: it prints the eOutInt removal mass as
"12× below the .0544 band" while .0544 / .005599 = **9.716**. Since
this stage rewrites the sentence that contains it, leaving the wrong
value in place would be a knowing falsehood. Registered decision:

- Fix the ratio to its re-derived value in BOTH places it appears (§2.4
  body and the abstract). The abstract is otherwise untouched; the
  l158 vocabulary freeze is deliberately re-cut with `9.72×` REQUIRED
  and `12×` FORBIDDEN, so the wrong value cannot grow back.
- This is the only abstract edit in this stage, and it is a single
  number correction, not prose work (prose is L174).

## SOURCE-OF-TRUTH RULES

T1. Every gain quoted in §2.4 is read from a stored `anchors.g_*` field
    of a results json — never from l167's adjudication table, never
    retyped from log prose (the L44 class; 14 lane instances).
T2. The percent deltas are computed in the cert script from those
    stored floats, at full precision, and rounded once for prose.
T3. The silW gain claim is an EXACT float equality against the base's
    stored gain, in both of silW's batches (l144, l150) — not a
    tolerance.
T4. The reviewer's own figures stay REVIEWER-REPORTED and may not enter
    the draft (the L167 evidence rule). Our independent re-derivation
    is what the draft cites.

## CERT (must pass BEFORE any draft line is edited)

CERT-1  `g_sil1110_wA` (l144) == `g_silW` (l150) == `g_cutwA`
        (l142/l144/l145/l148/l150, all five files agree) as EXACT
        float equality. If any inequality appears, branch B2 fires.
CERT-2  The six flip arms' gain deltas vs `g_cutwA` all land in
        [+1.00%, +1.35%]; the two non-flip motor halves land within
        ±0.05%; eOutMot lands in [−0.60%, −0.50%]. Band membership is
        asserted, not assumed.
CERT-3  The stored silW duty cells reproduce: (.622, 14) on B30 and
        (.659, 14) on B33, with paired ΔR +.189 (6 up / 0 down) and
        +.281 (9 up / 0 down), and the canonical pool 78/98 with the
        stored Wilson bounds to 1e-9 (l172 stats).
CERT-4  The sham cells reproduce from l137: three random-cell clamps at
        meanR .429/.502/.504 (kR 5/8/8), max−min = .075, and the
        carrier's own intact paired ΔR = −.088 — so |−.088| > .075 is
        re-proven in the data before the sentence is rewritten.
CERT-5  The mass ratio re-derives: .0544 / .005599 (both stored) rounds
        to 9.72, and 12 is NOT within 0.5 of it.
CERT-6  sil24's non-separability (reviewer I10) re-derives: sil24
        kR = 5 against the SAME batch's untreated intact base kR = 6
        and the cut base kR = 5 — a class-label match with no
        demonstrated separation at n = 16.

## BRANCHES (precedence B2 > B1)

- **B1_silW_gain_unchanged** — CERT-1 holds exactly. §2.4 is rebuilt
  with silW as the lead arm, and the gain-confound disclosure is
  written as "every edge-removal flip arm moves the gain; this one does
  not".
- **B2_silW_gain_differs** — any inequality in CERT-1. Then the card's
  own premise is wrong, silW is NOT the clean arm, §2.4 must be rebuilt
  around the §2.7 gain-swap 2×2 instead, and the card's prescription is
  recorded as refuted.

## Design pins (derived, not typed)

P1. The flip / non-flip arm partition is taken from the stored class
    booleans (`super` / `notsuper`), not from my memory of which arm
    flipped.
P2. The two passages that move to §3.8 are identified by their stored
    anchors (`l142.aeall.a_eall_max == 0.0` with `gains_equal`, and
    `l148.seid == 0.0` with `h_id.bit_identical`), and §2.4 keeps the
    INTERPRETIVE consequence (the ~.13 silW→eAll margin is
    settle-history carried by the edges) — only the identity statements
    relocate.
P3. "two factors" / "Factor 1" / "Factor 2" / "two-factor law" must
    survive NOWHERE in the BODY (from `## 1. Introduction` onward).
    The changelog banner keeps its history (banner-scoped, per the
    l169c2 lesson).
P4. Every draft literal a prior verify section asserts must still be
    present somewhere in the draft after the rebuild — the relocation
    may move a string between sections but may not delete one.

## Verify (this stage)

- `l149_verify.py` gains a NEW section that: re-reads all nine gains
  from their stored jsons and re-derives every percent delta; re-asserts
  the exact silW equality; recomputes the mass ratio; reproduces the
  sham and sil24 cells; proves branch B1 from the data; asserts the new
  §2.4 literals verbatim; asserts the retired framing GONE from the
  body; and asserts both identity passages now live in §3.8 and no
  longer in §2.4.
- The stage-(a) scope gate (section 20(e), which asserts §2.4 UNCHANGED)
  is re-anchored to the stage-(b) state — a gate flip is a code edit,
  never a claim loosening.
- `numbers.json` regenerates with all 98 pre-existing keys
  BYTE-IDENTICAL (pre-tick copy taken FIRST).
- CLAIM-MAP gains the block + its §-table row; `l161_verify` bidirectional.
- All five paper verifies green.
