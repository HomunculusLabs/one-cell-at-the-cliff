# L211 PREREG — is the hidden route the CARRIER's EDGES or its NEIGHBOURHOOD?

Registered 2026-11-22 17:5x, tick 240, BEFORE any decomposed number was read.
Static. Zero rollouts, zero settles, zero dynamics, zero RNG of my own (the
null stream is L178/l169c's, seed 16943, reproduced not re-drawn).

## What L206 found (the object being decomposed)

On the f4wA floor-4 female-cord substrate, with the anatomical walk operator
A = |g*W_beta|, the carrier (gi 1110, DNp33-L) routes to the 303 motor-pool
cells with mean SEARCH INFORMATION 22.39317740345491 bits vs the 100
degree-neutral destination-swap draws' median 18.71799427882452 — excess
**3.675 bits at percentile 100.0** (branch G2_SI_HIGH), with all 303 pool
cells reachable in both the real graph and every draw (null_reach_med 303).

SI is accumulated during relaxation along the L-shortest path, L_uv =
-log10(A_uv/A_max), T_uv = A_uv / out-strength(u), SI(path) = sum -log2 T.

## The decomposition (primary)

For every pool cell p reached from source c, the L-shortest path's SI splits
EXACTLY into two terms:

- FIRST HOP  fh(p) = -log2 T(c -> t1(p)), the one chosen out-edge of c;
- REMAINDER  rem(p) = SI(p) - fh(p), everything from t1(p) onward.

Means over the reached pool cells give, for the carrier and for each of the
100 draws, si_mean = fh_mean + rem_mean identically. The decomposition of the
EXCESS is therefore additive against the draws' MEANS (not medians — median of
a sum is not the sum of medians, so the primary uses means and the medians are
reported beside as description):

  D_total = si_car - mean_k(si_k) = (fh_car - mean_k fh_k) + (rem_car - mean_k rem_k)
          = D_fh + D_rem        (asserted to < 1e-9 absolute)

  share_fh = D_fh / D_total.

## Registered branches (one object per cell, L109)

- **B_FIRSTHOP** share_fh >= 0.60 — a WEIGHT-ALLOCATION story: the carrier's
  own out-mass spread makes every route start improbable.
- **B_REMAINDER** share_fh <= 0.40 — a TARGET-SELECTION story: the carrier
  picked a neighbourhood that is itself badly connected to the motor pools
  (the L178 anatomy finding — only 5 of its 69 targets carry any pool
  out-edge — restated in SI currency).
- **B_SPLIT** 0.40 < share_fh < 0.60 — both; the card reports the share.
- **B_DEGENERATE** D_total <= 0, or any non-finite fh/rem, or the additivity
  assert fails. Fires before any share is interpreted.

## Registered IN ADVANCE: the first-hop multiset is INVARIANT by construction

The l169c null relocates destinations with the weight travelling with its
SOURCE, so A_E, csr_cols and therefore NLT = -log2(A/s_out) are bit-identical
in every draw. The 69 first-hop costs available out of the carrier are
consequently the SAME MULTISET in the real graph and in all 100 draws. This is
asserted numerically, and it fixes the meaning of any first-hop effect in
advance: **D_fh can only be SELECTION among a fixed menu**, never a difference
in the menu. A reader who sees a first-hop term must not read it as "the
carrier allocates its weights differently from the nulls" — it cannot.

## Secondary cells (declared, non-branching)

1. **Separate percentiles.** fh_car and rem_car each against their own 100-draw
   distribution (pct = fraction of draws strictly below). Reported; the branch
   is called on the share, not on these.
2. **The family.** fh/rem split for all 35 L206 actors (carrier, mass-matched
   twin gi 290, 33-cell ng family), so the carrier's share is read against a
   cohort rather than a single twin. Descriptive (L207's cohort-resolution
   law: a percentile against 35 is resolution-limited).
3. **The mirror.** gi 928 (DNp33-R, L207's contralateral homolog) as a 36th
   source on the SAME substrate. DECLARED DESCRIPTIVE-ONLY: the 100 draws swap
   the CARRIER's out-edges, so they are not a null for the mirror. It is read
   against the family, and no branch depends on it.
4. **dist_mean / hop count.** The L-shortest path's hop count to each pool
   cell, carrier vs draws, because a first-hop share is trivially large when
   paths are short — the share must be read with the path length beside it.

## SCOPED OUT of this tick, appended as its own queue item

The card's second transport leg ("does the same decomposition hold on the base
unfloored cutwA substrate?") needs the SI index arrays rebuilt for a second
substrate, i.e. a generic version of L206's index construction gated by exact
array equality against the certified f4wA specialisation. That is a second
slice's worth of machinery and is registered here as deliberately deferred,
not forgotten. The mirror leg (same substrate, new source) IS in scope because
it reuses the certified dijkstra unchanged.

## Certification plan (halting gates, run BEFORE any L211 number is read)

- Inherited free, as literal source slices: CERT-HEAD1 (l151_static.py 1-319),
  CERT-HEAD2 (l178_tail.py 7-149, CERT-F4 + gains at float equality + CSR
  orientation + 20 pool sizes), MID (l206_mid.py), CERT-HEAD3 (l178_tail.py
  348-458, CERT-REW + the 100 draws), CERT-HEAD4 (l206_tail.py 22-263,
  CERT-178's 420 values + lam1 + the depth sweep + CERT-NULL).
- **CERT-SI (new, halting):** CERT-HEAD5 = l206_tail.py lines 320-461 VERBATIM
  re-runs L206's whole search-information block, and every float in the
  resulting `o["G2_search_information"]` is asserted EQUAL to the stored
  l206/static.json block — recursively, by float equality, including all 35
  actors' si_mean/si_min/si_med/dist_mean/n_reach. This is the card's required
  anchor ("SI reproduced on the real graph against l206/static.json by float
  equality before any decomposed term is read").
- **CERT-FH (new, halting):** my first-hop-tracking walker is a MODIFIED copy
  of the certified dijkstra, so it is gated the L210/CERT-MV way — for the
  carrier, the twin and ALL 100 draws it must reproduce the certified
  dijkstra's pool dist and si values by EXACT equality (==, not tolerance).
  Any inequality halts the run.
- **CERT-MENU (new):** NLT bit-identity and the 69-edge first-hop multiset
  invariance asserted against every draw's edge-target vector.
- No lab module is imported (L175: a lab *_verdict.py / *_static.py is a
  SCRIPT — importing it rewrites its own artifacts). All slices are audited
  for forbidden tokens (file writes, lab imports) by the builder.
- l206/static.json, l178/static.json opened READ-ONLY, size+mtime_ns
  fingerprinted before and asserted unchanged after. Writes l211/static.json
  ONLY.

## Predictions (recorded before measuring; scored honestly)

- **Q211-1:** branch **B_REMAINDER**. Reason: the menu is fixed by
  construction, so the only first-hop freedom is which of 69 edges the length
  metric picks, and the L178 anatomy says the real targets are the badly
  placed ones. I expect share_fh in [0.00, 0.25].
- **Q211-2:** fh_car will sit INSIDE the draws (pct between 5 and 95) while
  rem_car sits at or near pct 100.
- **Q211-3:** carrier fh_mean > log2(69) = 6.109 bits (its out-mass is spread,
  so no single edge is cheap) and fh_mean / si_mean < 0.45.
- **Q211-4:** the carrier's dist_mean (1.4900) exceeds the draws' median
  dist_mean, i.e. the real routes are also LONGER in the length metric — if
  they are SHORTER while SI is higher, that is a genuine dissociation and I
  will report it as such.
- **Q211-5:** the mirror gi 928 will land in the same branch region as the
  carrier (share_fh within 0.15 of the carrier's), because L207 found it
  avoids harder, not differently.

## Limits to state in the verdict regardless of outcome

One substrate, one operator, one null family (L207's cross-null law: a
deficit magnitude is null-specific), one length metric with the DISCLOSED
domain choice (-log10(A/A_max) rather than the field's (0,1] normalisation),
ties in L broken by heap order and not controlled, and the relation to L219
declared: L219 asks the same target-choice-vs-quality question in the
left-Perron currency, so whichever runs second cites the first and does NOT
re-bank the finding as independent evidence.
