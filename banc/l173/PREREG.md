# L173 PREREG — stage (a): the Methods write-up (ZERO rollouts)

Registered BEFORE any file was written. Card L173 (LANE.md ideas 87) has
two halves: (i) rebuild §2.4 around its cleanest arm and drop the
"two-factor law" framing, (ii) write the Methods the reviewer asked for
(update equation, constants, the DNg100 tonic drive the draft never
mentions, the chopped sinusoid, the active-fraction target and bisect,
cohort/mass/ladder/class definitions, the pooling rule, a notation
table). This tick ships **(ii) only**, by dependency order: the card
itself says the §2.4 bit-identities get *moved to Methods*, so Methods
must exist first. §2.4 is stage (b), seeded in the queue bracket.

## Scope clause

- ZERO rollouts, zero RNG (one small deterministic tensor probe, seeded),
  no graph build, no live changes. No §2.4 edit in this stage — the
  §2.4 prose stays exactly as it is, and the two bit-identity passages
  stay there until (b) relocates them.
- No new measurement. Every number that enters Methods is either parsed
  out of a run script's source or already pinned in a stored artifact.

## SOURCE-OF-TRUTH RULE (the card's Verify line, operationalized)

S1. Every model/protocol constant written into §3 is PARSED from
    `banc/l135_run.py` at write time (ast over the module body), never
    hand-typed from memory. A hand-typed constant in prose is the L85
    failure class; three lane instances already.
S2. Every definition written into §3 (duty, the per-seed bar, the class
    criteria, the S window) is PARSED from `banc/l169d_verdict.py`
    (the current verdict machinery) and asserted equal to the same
    literal in the earliest verdict script that defined it.
S3. Cohort / mass / ladder definitions are PARSED from
    `banc/l131_static.py` (the XOR-pin static) and asserted against the
    stored pins in `banc/l131/static.json`.
S4. The pooling rule is the canonical L172 rule, taken from
    `banc/l172/stats.json` (admissibility verdict), not restated.

## CERT (must pass BEFORE any Methods text is written)

CERT-1  The constants parsed from `l135_run.py` match the ones the
        current lineage still runs: `l169d_run.py` must carry identical
        TAU / DT / RMAX / BG / NOISE / SETTLE / WIN / SEG / SEGB / BETA /
        D / ENT_AMP / AF_T. Any mismatch STOPS the tick (the Methods
        would describe a retired protocol).
CERT-2  AF_T and the four stored-form gains quoted in Methods are equal
        to the values stored in `l135/results_l135.json` /
        `l131/static.json` to 1e-12.
CERT-3  The ladder pins re-derived from `l131_static.py` source
        (K, the 19/58 split, the two mass-split shares) equal the stored
        `l131/static.json` values exactly.

## EQUATION EQUIVALENCE (the one computation this stage runs)

The card prescribes

    x <- x + (DT/TAU)*(clamp(relu(g*W x + I + sin[mech] + BG) + noise,
                             max=RMAX) - x)

E-TEST: extract the THREE update lines verbatim from `l135_run.py`
source text, `exec` them on a small random system (fixed seed, N=7,
dense-to-sparse W), and compare bit-for-bit against my own independent
implementation of the equation as written above.

- **M1_equation_matches** — max|difference| == 0.0 exactly. The card's
  form is correct and goes into Methods verbatim (with the bracket
  structure spelled out: the noise enters AFTER relu and INSIDE the
  clamp, and the clamp has NO lower bound).
- **M2_equation_differs** — any nonzero difference. Then the CODE wins:
  Methods carries the corrected form, the card's prescription is
  recorded as refuted in the queue bracket and in LANE-LOG, and the
  difference is named explicitly.

Precedence: M2 > M1 (a difference is the finding).

## Design pins (derived, not typed — recorded for the verifier)

P1. Chop geometry: period and on-duration read from the AMPA loop, plus
    the override line that makes the middle segment continuous.
P2. Active fraction: the threshold (x > ?) and the anchor seed list used
    by the bisect, both parsed; bracket + iteration count parsed.
P3. Class criteria: `_super`, `_partial`, `_notsuper` thresholds parsed
    from the verdict source as literals.
P4. Duty: the S bar, the per-seed bar, the correlation window length and
    the sample stride, parsed.
P5. The notation table must contain one row per parsed symbol and NO
    row whose value was not parsed.

## Verify (this stage)

- `l149_verify.py` gains a NEW section that re-parses every constant out
  of `banc/l135_run.py` **from source**, re-runs the equation
  equivalence test independently, and asserts the §3 literals verbatim.
  A protocol change in the run script therefore breaks the gate.
- `numbers.json` regenerates with all 95 pre-existing keys
  BYTE-IDENTICAL (pre-tick copy taken first, per the tick-199 lesson).
- CLAIM-MAP gains the block + its §-table row; `l161_verify.py`
  bidirectional.
- All five paper verifies green; the abstract is NOT touched.
