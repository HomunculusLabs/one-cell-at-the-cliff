# PREREG — L174 stage (b2): the ABSTRACT compression

Written BEFORE any draft line is edited. Tick 206, 2026-11-20.
Zero rollouts, zero RNG, no graph build, no torch. The only compute is
string/char arithmetic over the stored draft and stored jsons.

## Slice declaration (why this is not all of stage (b))

Stage (b2) as inherited from tick 205 names five jobs: (i) abstract
<= 1,920 chars with no citation keys, no all-caps emphasis and no arm
codes; (ii) 37 bullet lines -> prose; (iii) a Discussion section; (iv)
strip the changelog banner + lane/batch codes + the all-caps tokens
body-wide; (v) reviewer I10's section 2.4 compression. That is four to
five ticks of prose work on a 94,048-char draft. This tick takes (i)
ONLY and appends the rest to the queue bracket as (b3) and (b4):

- (b2) THIS TICK: the abstract, its numeric/vocabulary contract, and the
  three other gates that pin abstract text.
- (b3) bullets -> prose in sections 1-2 plus the I10 section 2.4
  compression (they touch the same blocks).
- (b4) the Discussion, the changelog-banner strip, and the body-wide
  lane/batch-code + all-caps strip (the banner strip must come LAST
  because every other stage's removal gates are banner-scoped per the
  l169c2 lesson).

## Source of truth

- T1. The abstract's claims are CARRIED by the certified body. Compression
  is RELOCATION, never deletion: any numeric token or claim phrase that
  leaves the abstract must be demonstrably present in the body.
- T2. No number enters the new abstract that is not already in
  numbers.json (or recomputable from a stored json). The abstract loses
  its inline [key] citations by order of the card, so traceability moves
  INTO the verifier as an explicit token -> key table.
- T3. Nothing retired by an earlier cut may come back. Every FORBIDDEN
  set in l158_verify (superseded per-batch counts, the 12x mass ratio,
  the endogenous-clock readings, affirmative uniqueness) survives this
  re-cut unchanged.
- T4. The abstract is the only draft block this stage may edit. Section
  1, the Results, Methods, Limitations and the reference list are
  UNTOUCHED (asserted).

## Certification before any edit (CERT)

- CERT-1. All six paper verifies GREEN on the PRE-edit draft (a stage
  that starts red cannot attribute its own failures). Stored under
  banc/l174b2/raw/cert1_*.txt.
- CERT-2. numbers.json copied FIRST to banc/l174b2/numbers_pretick.json
  and asserted byte-identical at the end (sha 238bf2d37f51...).
- CERT-3. The v3.21 abstract block frozen verbatim to
  banc/l174b2/abstract_v321.txt before the splice, so the relocation
  gate has a fixed source for "what left".
- CERT-4. Every numeric token in the NEW abstract is mapped, in the
  verifier source, to the numbers.json key that certifies it, and the
  value is asserted to match.

## Branches (precedence: R2 > R1)

- R2_relocation_incomplete. If any token or claim phrase dropped from the
  v3.21 abstract is NOT present in the certified body, the compression is
  a DELETION and the claim set shrank. Fire this branch, name the orphans
  and either restore the token to the abstract or add the body sentence
  that carries it. Checked FIRST because it is the failure that would
  silently weaken the paper.
- R1_relocation_complete. Every dropped token/phrase is carried by the
  body, the new abstract is <= 1,920 chars, and the contract gates are
  re-cut to the new text with every FORBIDDEN set intact.

## Pins (predicted before measuring)

- P1. v3.21 abstract body length is 5,322 chars; the target is a >= 63%
  cut, so several numeric cells MUST leave. Predicted orphan count after
  the body check: 0 (the body is the certified home of every cell).
- P2. The retired-token FORBIDDEN sets will all still pass trivially
  after compression (fewer tokens = fewer chances to re-assert) — a
  DEGENERATE pass per the L55 rule, and it is disclosed as such rather
  than reported as a win.
- P3. l158_verify section (1) (abstract [key] citations resolve) becomes
  VACUOUS when the keys leave: predicted cited-key count 0. The honest
  replacement is CERT-4's token -> key table, which is strictly stronger
  (it certifies values, not just that a key exists). Disclose the
  vacuity, do not report "(1) green" as evidence.
- P4. Three OTHER gates pin abstract text and will break honestly:
  l149_verify (19g) (8 abstract prose literals), l149_verify (18)
  (superseded-clause scan, scoped to the abstract — should still pass),
  and l174_verify (8d) (abstract byte-identity pin to the stage-(b1)
  state). (19g)'s literals get BODY-scoped and (8d) gets RE-PINNED to
  the new text. A gate is re-cut or re-pinned, never deleted or loosened.
- P5. The new abstract must contain zero tokens matching the arm-code
  and lane-code patterns (cut<arm>, sil<arm>, scr<n>, b65, Bnn, Lnnn,
  lnnn.key) and zero all-caps emphasis tokens apart from the proper noun
  BANC. Predicted: 0 and 1 (BANC) respectively.

## What a pass does NOT license

A shorter abstract is not a stronger claim. This stage changes no
measurement, no number and no scope. If a reader of the new abstract
would conclude anything the v3.21 abstract did not already license, the
compression is wrong and R2 fires.
