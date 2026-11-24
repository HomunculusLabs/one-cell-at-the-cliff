# L212 PREREG — the v783 leg, re-posed so it is ANSWERABLE

Written BEFORE any L212 number was measured. Tick 241, 2026-11-22.
Label: **EXPLORATORY** (L78 non-transport law), and the digest must carry that word.

## What L207 left behind

L207 found both DNp33 members carry an inline `fafb_783_match_id`
(carrier gi 1110 -> 720575940604103084, mirror gi 928 -> 720575940633165452)
and recorded `Q3_v783_handle.verdict = "UNANSWERABLE-BY-VOLUME"`: FAFB v783 is a
BRAIN-ONLY volume, so the 831-cell leg-motor readout that L178/L206/L207 measure
into has no counterpart. The portable question is therefore NOT "does the matched
cell avoid its leg motor pools" but **"does the matched cell avoid the nearest
readout its own volume HAS"**.

## The readout CHOICE, registered first, with the reason

Candidates named on the card: (a) v783 descending neurons as the brain's output
layer, (b) neck motor neurons, (c) the VNC-projecting DN population.

**PRIMARY = (b), widened to its honest anatomical form: the v783 `super_class ==
motor` population** (the brain's own motor neurons: neck via the cervical
connective plus proboscis/maxillary-labial/antennal/ocellar motor neurons).
Reason, and it is the whole reason: this keeps the readout's CATEGORY identical to
BANC's (motor neurons, the terminal output of the volume) and changes only the
body segment. Candidates (a) and (c) are rejected as PRIMARY because the carrier
IS a descending neuron, so the readout would contain the actor and would be
nearly identical to the mass-matched cohort it is scored against — a percentile of
a set against itself.

Readout is partitioned into **5 semantic pools by nerve** (PhN, MxLbN, CV, AN, ON)
so the arrival mass is summed over named groups exactly as the BANC form sums over
its 20 semantic pools. Pool sizes are asserted non-overlapping and are reported.

**SECONDARY, DESCRIPTIVE ONLY (no branch): (a)** the 1,303 descending cells minus
the carrier and its mirror. Reported because the card names it; it cannot carry a
branch for the reason above.

## The statistic (unchanged in form from L207)

Anatomical, g-free, no mask, no settle, no seed, no rollouts:

    A = |W_beta|, BETA_L = 2.0 on inhibitory edges (gaba OR glutamate source)
    R(c) = P2(c) / (lam1^2 * m_out(c))

where P2 = total arrival mass at the readout at depth 2 from a unit impulse at c,
m_out = sum of |A| over c's out-edges, lam1 = spectral radius of A by power
iteration (400 iters, rel spread of the last 6 reported).
Registered in advance: R is invariant to any global rescaling of A (L209's law), so
the lam1^2 division is a NO-OP for the ratio and will be MEASURED as one, not
asserted in prose.

Operator provenance: v783 edge weights are log1p(syn_count) recovered from the live
`peabrain/brain_graph.pt` by dividing out the live per-source sign scale, then
re-signed under the BANC convention (glutamate treated as inhibitory). Disclosed
convention differences vs BANC, written before measuring:
1. the live v783 graph signs monoamines at 0.2 and glutamate at +1.0; the
   recovery + re-sign makes the OPERATOR's form match BANC's, and the recovery is
   gated by float equality on every non-monoamine edge;
2. `unknown` top_nt is treated as excitatory (v783 carries an `unknown` class
   BANC's NT release does not);
3. v783 has **no synapse floor** (BANC's f4 substrates use syn>=4). This is the
   closure-like substrate, so the closest BANC comparator is G0_closure/G1_cutwA
   (carrier pct .070 / .121), not F4_f4wA.

**ROBUSTNESS LEG (reported, no branch): BETA_L = 1.0** (pure |W|).

## Cohort / null

Mass-matched cohort of **k = 100** v783 descending cells, nearest in log out-mass,
carrier and mirror excluded — L207's mirror-leg null, same expression
(`matched_cohort`, sliced verbatim). Percentile = fraction of the cohort STRICTLY
SMALLER (low = avoider). Cohort log-mass spread reported per actor (L207 reported
.10-.12). This is NOT the l169c degree-neutral rewire null and is never compared to
one (L207's cross-null law, L207 limitation 5).

## Branch table (SIGN x BAND, the L205 four-cell rule)

| branch | condition on carrier_pct, PRIMARY readout |
|---|---|
| **V_AVOIDS** | pct <= 0.10 — low, same direction as L207 |
| **V_HIGH** | pct >= 0.90 |
| **V_MIDDLE** | 0.10 < pct < 0.90 |
| **V_DEGENERATE** | carrier m_out == 0, or > 50% of cohort R values are 0 (readout unreachable at depth 2), or any power iteration fails to converge (rel spread >= 1e-6) |

**Registered interpretation, written before measuring and binding on the write-up:**
a readout CHANGE is a different object. V_AVOIDS is **suggestive only** — it does
not confirm L207, because the readout, the volume and the specimen's segment all
moved at once. V_MIDDLE or V_HIGH **does NOT refute L207** for the same reason.
V_DEGENERATE is a journaled blocker, not a finding.

## Verify (the card's own line)

- PREREG first (this file).
- The v783 graph's own stored pins reproduced before any new read:
  **CERT-783** = N == 139255, nnz exact, and `ids` array-EQUAL to the raw Zenodo
  `proofread_root_ids_783.npy`; the live `meta` signs dict asserted.
- The two match ids asserted present in the v783 id set AND in the annotation
  table with `cell_type == DNp33` and opposite `side` — **a missing id is a valid
  journaled blocker**, not a worked-around one.
- **CERT-L207** = the two match ids read from `l207/static.json` (opened
  READ-ONLY, size+mtime_ns fingerprinted before and asserted unchanged after) and
  asserted equal to the ids used here, so this card cannot drift off L207's cells.
- **CERT-SRC** = three verbatim source slices of `l207_tail.py` with sha256
  asserted: lines 82-110 (`reach_sub`, `power_iter_sub`, sha fce1e71189eb1ed7),
  199-241 (`Rstat`, `pct_of`, `rankvec`, `spearman_l`, sha 340c0432c85c6e7b),
  338-346 (`matched_cohort`, sha f4585bcc52f7ab0a). No lab module is imported
  (L175). Forbidden-token audit on the generated script.
  Disclosed: the BANC head (l151_static.py) is NOT sliced — it loads
  `banc_graph.pt` — so this card inherits NO BANC pin chain and stands on CERT-783
  instead.
- **CERT-MV** = the fast bincount matvec asserted EXACTLY array-equal (==) to the
  verbatim `np.add.at` kernel on 4 probes, and the gated `reach_sub`/power
  iteration asserted to reproduce the verbatim functions at FLOAT EQUALITY on the
  carrier before any cohort value is read (the L210/L211 pattern).
- Cohort log-mass spread reported.

## Predictions (scored honestly, right or wrong)

1. **Q212-1**: branch = **V_AVOIDS**.
2. **Q212-2**: the mirror is also low AND `mirror_pct <= carrier_pct` (hidden
   harder, as in L207 .06 vs .10 and L211's si 24.63 vs 22.x).
3. **Q212-3**: the SECONDARY descending-readout leg gives a **higher** percentile
   than the PRIMARY motor leg (descending cells talk to descending cells more
   readily than to head motor neurons).
4. **Q212-4**: the BETA_L = 1.0 robustness leg moves carrier_pct by <= 0.10
   absolute.
5. **Q212-5**: cohort log-mass spread <= 0.15 for both actors.
