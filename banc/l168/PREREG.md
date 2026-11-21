# L168 PREREG — scramble arms into Results + ledger, and re-scope the claim

Card: LANE.md ideas-87 L168 (tick 189 / L167 stage (a) response card #1, the
reviewer's own highest-priority fix). Registered 2026-11-20 ~02:4x BEFORE any
L168 computation or draft edit. ZERO ROLLOUTS — this is a fold of ALREADY
STORED arms into the manuscript plus a claim re-scope.

## Why the card exists (from L167 adjudication, issue I1, CONFIRMED)

The draft contains ZERO mentions of the scramble control family and
numbers.json contains ZERO `scr` keys, while our own stored arms show that a
mass-matched cohort that EXCLUDES the carrier also super-raises the right
side. So the manuscript's "one cell" framing overreaches: the measured claim
is CONTEXT-DEPENDENT SUFFICIENCY isolated by a mass-matched twin control, not
uniqueness.

## Evidence rule (inherited from L167)

Nothing from the external referee report may enter the draft as a number.
Every value folded here is re-derived inside `l168_pools.py` from our own
stored results jsons, full precision, with a CERT block that reproduces the
stored per-batch Wilson bounds and the stored pooled rows before any new
number is read. Sources, fixed in advance:

- `banc/l125/results_l125.json:table.Ti.{cutscr0,cutscr1,cutscr2,cutscr3}` (B20)
- `banc/l127/results_l127.json:table.Ti.{cutscr0,cutcl40,cutscrL1,cutscrL2}` (B22)
- `banc/l128/results_l128.json:table.Ti.{cutscr0,cutscr1,cutscr2,cutscr3}` (B23)
- masses: `mass_scr` / `extra_mass_scr` (l125, l127, l128) and `mass.cutng29`
  (= the k29 window mass the scramble arms are mass-matched against)
- stored pooled rows for cross-check: `l128:pooled_scr`, `l127:pooled_scr0`

Batch identity is taken from the stored `k_b*` keys of those pooled rows, NOT
from log prose (L44 rule).

## Registered CERT block (must pass BEFORE any verdict or draft edit)

- CERT-1: for every scramble arm in every file, Wilson(kR,16) and Wilson(kL,16)
  reproduce the stored `lbR/ubR/lbL/ubL` to < 1e-9.
- CERT-2: pooled Wilson over the batch union reproduces the stored
  `l128:pooled_scr` rows (cutscr0 n=48, cutscr1/2/3 n=32) to < 1e-12 on
  k, p_hat, lb, ub AND the per-batch `k_b*` decomposition matches our sum.
- CERT-3: `l127:pooled_scr0` (n=32, B20+B22) reproduces as the 2-batch
  prefix of our 3-batch cutscr0 pool.
- CERT-4: `mass_scr` / `extra_mass_scr` agree between l125 and l128 EXACTLY
  (same arms, same substrate) and `mass.cutng29` is identical in all three
  files.

## Registered fold (what enters the draft, conditional on CERT green)

(a) §2.2 gains a scramble-control paragraph with pooled Wilson for
    cutscr0 (3 batches), cutscr1/2/3 (2 batches each), and cutcl40 /
    cutscrL1 / cutscrL2 (single batch, DISCLOSED as single-batch).
(b) numbers.json gains `l168.scr` (per-arm pooled k/n/lb/ub + per-batch k)
    and `l168.mass` via `extract_numbers.py`; every pre-existing key must
    regenerate BYTE-IDENTICAL.
(c) Title / abstract / §2.2 re-scoped from uniqueness to context-dependent
    SUFFICIENCY isolated by a mass-matched twin control. Registered language
    constraint: the words "only cell", "unique", "uniquely" must not appear
    as a claim about the carrier anywhere in title/abstract/§2.2 after this
    fold, and the scramble family must be named in the abstract.
(d) §2.2 states explicitly that cutscr0 raises BOTH sides, so it is NOT the
    crossed state the carrier produces — i.e. the scramble reaches the same
    right-side class by a different route, which is what makes the carrier
    sufficient-in-context rather than unique.

## Registered decision rule

- D1 (expected): cutscr0 pools SUPER on the right (lb > .5) with the carrier
  excluded => fold (a)-(d) exactly as above, re-scope mandatory.
- D2: cutscr0 does NOT pool above .5 => the uniqueness framing survives;
  fold (a)+(b) only, journal that the reviewer's I1 direction did not
  reproduce at the pooled level, and do NOT re-scope.
- D3: the scramble family is heterogeneous (some super, some kill) => fold as
  D1 but the re-scope language must state that sufficiency is
  SET-dependent, not merely context-dependent (this is the honest reading if
  mass-matched sets at similar mass disagree with each other).

## Registered verification (post-fold)

- `extract_numbers.py` regen: all pre-existing keys byte-identical.
- `l149_verify.py` gains a section (10) that re-derives the scramble pools
  from the three stored tables INDEPENDENTLY of numbers.json and asserts the
  draft literals.
- `l158_verify.py` abstract vocabulary allowlist RE-FROZEN to the post-fold
  token set (the freeze is a contract, so it must be re-cut deliberately,
  with the new scramble tokens listed as REQUIRED).
- `l143_verify.py`, `l159_verify.py`, `l161_verify.py` must stay ALL GREEN.

## Out of scope for this card

No rollouts. No gain swap (L169). No male floor-matched extraction (L170).
No slow-line surgery (L171). No statistics rewrite (L172). Those are their
own cards and must not be smuggled in here.
