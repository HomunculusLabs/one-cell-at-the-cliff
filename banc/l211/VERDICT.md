# L211 VERDICT — the hidden route is the NEIGHBOURHOOD, not the edges

Branch **B_REMAINDER** (registered). PREREG `l211/PREREG.md` written and frozen
before any decomposed number was read. Static: zero rollouts, zero settles,
zero dynamics, zero RNG of my own. 44 s CPU.

## The decomposition

L206's search-information excess, split exactly at the carrier's own out-edge:

```
D_total  = +3.5816 bits   (carrier 22.39317740345491 - null MEAN 18.811612)
         =  D_fh  -0.0201   first hop,  the carrier's own chosen out-edge
         +  D_rem +3.6017   remainder,  everything from its 69 targets onward
additivity |D_total - (D_fh + D_rem)| = 0.0   (exactly, not to tolerance)
share_fh = -0.0056          share_rem = 1.0056
```

**The remainder carries 100.6% of the excess.** The first-hop term is not
merely small — it is slightly *negative*, and it sits at percentile **45.0**,
dead inside the draws (fh_p05 5.7105, fh_p95 6.0258, sd 0.1001), while the
remainder sits at percentile **100.0** (rem_p05 11.2359, rem_p95 14.7371,
sd 1.0713). Carrier SI percentile 100.0 is reproduced by the remainder
percentile alone.

This is the L178 anatomy finding (only 5 of the carrier's 69 targets carry any
motor-pool out-edge) restated in the routing currency: the carrier is hidden
because of **where its targets sit in the graph**, not because of how it
spreads its own out-mass.

## Registered in advance, and it is what makes the result readable

The l169c null relocates destinations with each weight travelling with its
SOURCE, so `A_E`, `csr_cols` and therefore `NLT = -log2(A/s_out)` are
bit-identical in every draw: the 69-edge first-hop **menu is invariant**
(asserted on all 100 draws, CERT-MENU; median 69 of 69 carrier out-edges
relocated per draw). D_fh could therefore only ever have been a SELECTION
effect among a fixed menu, never an allocation difference — stated in the
PREREG before measuring, and it is why "the carrier allocates its out-mass
unusually" is not an available reading of this card.

## Unregistered and kept: the first hop is CHEAPER than chance

Uniform allocation over 69 targets would cost exactly log2(69) = 6.1085 bits.
The menu's median cost is 6.1952 (skewed above uniform), yet the carrier's
realised mean first hop is **5.8473** — below both. The length metric
preferentially enters the carrier's *heaviest* out-edges, and it uses only
**11 distinct first hops** for all 303 pool cells against a null median of
**16**. The real wiring funnels pool traffic through fewer, fatter first hops
and then pays for it downstream. This refuted Q211-3 (I registered
fh_mean > log2(69)).

## The paths are longer too, and that is the same story

hop_mean 3.8053 vs null median 3.2063 (percentile 100.0); dist_mean 1.4900 vs
1.2183 (percentile 100.0). Real routes to the motor pools are both longer in
the length metric and more improbable in the transition metric, and the whole
of the improbability accrues after the first step.

## Cohort and mirror (descriptive, declared non-branching)

- 35-actor cohort: carrier fh-share of SI 0.2611 vs family median 0.2835
  (range 0.2208-0.3484), twin 0.3068. Carrier **remainder rank 32/35**, which
  is exactly its L206 SI rank 32/35; **first-hop rank 26/35**. The cohort
  reproduces the split at rank level: the remainder ranks the carrier, the
  first hop does not.
- Mirror gi 928 (DNp33-R, L207's contralateral homolog, 74 out-edges):
  si_mean **24.6340** — it is hidden *harder* than the carrier, consistent with
  L207 — fh 6.0688, rem 18.5652, fh-share 0.2464, gap to the carrier 0.0148.
  The decomposition transports to the homolog: remainder-dominated on both
  sides of the cord. Q211-5 correct. The 100 draws swap the CARRIER's edges,
  so this leg carries no null and is read against the family only.

## Predictions: 3 of 5

| id | registered | measured | |
|---|---|---|---|
| Q211-1 | B_REMAINDER, share_fh in [0.00, 0.25] | B_REMAINDER, share_fh **-0.0056** | **branch right, band wrong** |
| Q211-2 | fh inside (5,95), rem >= 99 | fh 45.0, rem 100.0 | correct |
| Q211-3 | fh_mean > 6.1085 and fh/si < 0.45 | 5.8473, 0.2611 | **wrong** |
| Q211-4 | carrier dist_mean > null median | 1.4900 vs 1.2183 | correct |
| Q211-5 | mirror share within 0.15 | 0.0148 | correct |

Q211-1 is scored FALSE honestly: the branch was predicted correctly but my
registered band excluded negative shares, and the measured share is negative.
The lesson is that a share band must admit the sign its own definition allows.

## Certification (halting gates, all green before the branch was called)

- Five verbatim source slices, forbidden-token audited, **no lab module
  imported** (L175): CERT-HEAD1 `l151_static.py` 1-319 (sha256
  e6245e8306dc8a0f, byte-identical to the head L178/L205/L206/L207/L209/L210
  recorded), CERT-HEAD2 `l178_tail.py` 7-149 (6e2e8fa4bd19eced), MID
  `l206_mid.py` (febbc390ad4f), CERT-HEAD3 `l178_tail.py` 348-458
  (5bb7b56e6b6487d5), CERT-HEAD4 `l206_tail.py` 22-263 (772a2410e76516e5,
  carrying CERT-178's 420 stored values and CERT-NULL). Each inherited sha
  asserted against L210's recorded value by the builder, so a moved source
  halts the build instead of certifying a different head.
- **CERT-HEAD5 (new): `l206_tail.py` lines 320-461 VERBATIM** — L206's whole
  search-information block re-EXECUTED rather than re-implemented, which is
  what lets this card certify SI rather than trust it.
- **CERT-SI (halting): 240 stored L206 search-information values reproduced by
  FLOAT EQUALITY** — recursive leaf comparison of the entire
  `G2_search_information` block including all 35 actors'
  si_mean/si_min/si_med/dist_mean/n_reach, the null median/p05/p95, the rank
  and the branch. This is the card's required anchor.
- **CERT-FH (halting): 61,819 EXACT equalities** (`==`, not tolerance) — my
  first-hop-tracking walker reproduces the certified `dijkstra_si`'s pool
  `dist` and `si` for the carrier, the twin and **all 100 draws**, plus the
  rebuilt null median/p05/p95 float-identical to the certified block. The
  modified walker is gated, never trusted.
- **CERT-MENU: 100 draws** — menu bit-identity and relocation count.
- `l206/static.json` and `l178/static.json` opened read-only, size+mtime_ns
  fingerprinted before and asserted unchanged after. Writes
  `l211/static.json` only.

## Limits

One substrate (f4wA floor-4), one operator, one null family (L207: a deficit
magnitude is null-specific), the disclosed `-log10(A/A_max)` domain choice,
heap-order tie-breaking uncontrolled, cohort/mirror legs descriptive. The
card's **cutwA (unfloored) transport leg is DEFERRED** — declared in the
PREREG and appended to the queue as its own item, not dropped. Relation to
**L219** declared up front: L219 asks target-choice-vs-quality in the
left-Perron currency; whichever runs second cites this one and does NOT
re-bank the finding as independent evidence.

Artifacts: `l211/{PREREG.md, static.json, VERDICT.md, run.out, run.err}`.
Code: `l211_{build,mid2,tail}.py` -> generated `l211_static.py` (1,389 lines).
