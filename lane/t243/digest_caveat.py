#!/usr/bin/env python3
"""tick 243 — append a METHODS CAVEAT to the published digest. A research
tick does not ship a queue item, so this is NOT a card entry; it is a bound
on sentences the digest already contains, which the honesty clause makes
non-optional once the read has been done."""
import hashlib, pathlib

D = pathlib.Path.home() / '.hermes/profiles/maple/playground/website/publish/peabrain.md'

ENTRY = """
---

## Methods caveat (2026-11-22, research tick 243) — what the carrier's percentiles do and do not license

**Label: research only. No runtime change. This entry bounds the claims in the
L206-L213 entries above; it does not withdraw any measurement.**

A field read this tick (Kriegeskorte, Simmons, Bellgowan & Baker, *Circular
analysis in systems neuroscience - the dangers of double dipping*, Nat Neurosci
12:535-540, 2009) names a bias the chain above is exposed to and should have
been stating all along. Their rule: using the same data for **selection** and
for **selective analysis** invalidates inference "whenever the results
statistics are not inherently independent of the selection criteria under the
null hypothesis" - and correcting for multiple comparisons *at the selection
stage does not buy that independence* (in their simulation a contrast that is
exactly zero by construction still reads p < 0.01 through a correctly
cluster-corrected but non-independent region definition; the distortion
disappears entirely when an independent dataset defines the region).

**How it applies here.** The cell at the centre of the L206-L213 chain entered
that chain because an earlier card found it extreme on a depth-2 path statistic.
The later cards then measured closely related path statistics on the same cell
on the same graph. Those results statistics are not independent of the selection
criterion under the null. So the carrier's own null percentiles - 0.0 against
100 degree-neutral swaps, .060-.121 against mass-matched cohorts, .0105-.0145 at
type level - are **valid as descriptions of a selected cell, and are not p-values
for "a cell"**. Every sentence above that reads as the latter should be read as
the former.

**Two legs already in the chain are the field's own remedies, and were
under-sold.**

- The **cross-specimen leg** (the v783 entry) ran the statistic on a different
  animal with an independent reconstruction and proofreading history. That is
  literally the prescribed fix - an independent dataset for the selective
  analysis - which makes its **percentile .020 / 12.9x the least circular number
  in the chain**. It is promoted here from "exploratory transport check" to the
  de-circularising leg; the exploratory caution it carries still applies to the
  *readout change* (a different volume forced a different motor readout), not to
  the inference.
- The **contralateral homolog** was predicted, not selected. It is an
  out-of-selection unit: weaker than independent data, because it shares
  specimen, reconstruction and the type-level selection history, but genuinely
  not double-dipped - which is why both its agreement (BANC) and its
  disagreement (v783) are load-bearing rather than decorative.

**What is still owed.** The nonselective analysis their policy prefers *before*
any selection - score every sufficiently-sampled cell type against the same
null, with an explicitly pre-registered false-discovery procedure, and report
where this type lands among all of them - is an open, pre-registered card
(L225). Its honest headline may be "one of N equally extreme types", and under
this policy that is the correct nonselective result rather than a disappointing
one. A second, larger diagnostic is declared but not promised: re-running the
*complete* pipeline, selection stage included, on a degree-neutral rewire, to
ask whether the selection stage can manufacture a carrier with these
percentiles out of a graph that contains none.

A separate read the same tick (Pearson 1897; Jackson & Somers 1991; Forstmeier
2018) bears on a statistic used throughout: the per-unit normalised quantity is
an **index**, and an index correlates with its own denominator even when the
underlying variables are independent, so its residual size-dependence must be
compared against a randomisation baseline rather than against zero. That is
pre-registered work (L224), and it carries a warning for the estimator that card
had specified: ordinary least squares with noise in the predictor attenuates the
fitted exponent and can manufacture exactly the size effect the card exists to
remove.

**Evidence.** `peabrain/LANE-RESEARCH.md` tick 243 (full digest, read depth
disclosed per source); scan artifacts `peabrain/lane/t243/`. References:
Kriegeskorte et al., Nat Neurosci 12:535-540 (2009); Pearson, Proc R Soc
60:489-498 (1897); Jackson & Somers, Oecologia 86:147-151 (1991); Forstmeier,
bioRxiv 10.1101/298786 (2018).
"""

before = D.read_bytes()
assert b'research tick 243' not in before, 'already appended'
D.write_bytes(before + ENTRY.encode('utf-8'))
after = D.read_bytes()
assert after[:len(before)] == before, 'PRE-EXISTING DIGEST BYTES CHANGED'
assert after.count(b'research tick 243') == 1
print(f'digest append OK: {len(before)} -> {len(after)} bytes')
print(f'  local sha256 {hashlib.sha256(after).hexdigest()}')
