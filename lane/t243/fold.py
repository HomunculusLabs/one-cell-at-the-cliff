#!/usr/bin/env python3
"""tick 243 fold — bracketed field amendments onto the EXISTING L224/L225
items. Research ticks AMEND, they do not append new items. Exact-string
anchors only (the patch tool's fuzzy matcher has merged line breaks in
LANE.md before)."""
import hashlib, pathlib

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain')
LANE = ROOT / 'LANE.md'

before = LANE.read_text(encoding='utf-8')
h_before = hashlib.md5(before.encode('utf-8')).hexdigest()
assert h_before == 'bdee8493f83b03e1c8f8561d087d2121', h_before

A224 = ("      fit; the k=1 case asserted to reproduce l213/static.json's population\n"
        "      R vector EXACTLY; bootstrap seeds registered.\n")
A225 = ("      perm_within with the SAME seed asserted to reproduce l213's DNp33\n"
        "      null percentile exactly before any other type is scored.\n")

AM224 = """      [tick 243 (hour-21 research), field amendment — the RATIO/INDEX
       prior art, and it carries a CORRECTNESS WARNING on this card as
       written. Pearson 1897 (Proc R Soc 60:489-498) proves an index
       correlates with its own denominator even when the underlying
       variables are drawn at random ("spurious organic correlation",
       0.4-0.5 from independent variables); Jackson & Somers 1991
       (Oecologia 86:147-151) state the operative rule — "identifying the
       appropriate null correlation is of utmost importance when
       statistically evaluating ratios" — and give the randomisation test
       as the instrument. (a) REQUIRED FIRST LEG, ahead of any fit: the
       measured Spearman(R, m_out) = +.53 is currently compared against
       ZERO and zero is the wrong null; recompute rho under a
       component-shuffling randomisation (P2 and m_out decoupled, seeds
       registered) and report the SPURIOUS baseline rho beside the
       measured one. Q2's "residual rho <= .05" bar is re-expressed
       against that baseline, not against 0, BEFORE measuring. (b) THE
       WARNING: Forstmeier 2018 (bioRxiv 10.1101/298786) shows OLS with
       noise in the PREDICTOR attenuates the slope (~10% in his fitted
       case, correction 1/0.91 = 1.097) and thereby MANUFACTURES a group
       difference in simulated data containing none — i.e. this card's
       own primary estimator (log-log OLS) biases k low and leaves R_k
       carrying exactly the size dependence the card exists to remove.
       Add a reduced-major-axis / errors-in-variables leg beside OLS,
       report all three k estimates together and treat their spread as
       the uncertainty; Theil-Sen is robust to OUTLIERS but not to
       predictor noise and does NOT substitute. (c) Scope line for the
       verdict: this is biometry, not connectomics — it transfers because
       the mathematics is about ratios, not organs. Refs for L174:
       Pearson 1897, Jackson & Somers 1991, Atchley et al Syst Zool
       25:137-148 (1976). See LANE-RESEARCH.md tick 243.]
"""

AM225 = """      [tick 243 (hour-21 research), field amendment — this card IS the
       field's prescribed remedy and should be framed as one.
       Kriegeskorte, Simmons, Bellgowan & Baker, Nat Neurosci 12:535-540
       (2009), "Circular analysis — the dangers of double dipping": using
       the same data for SELECTION and for selective analysis invalidates
       inference "whenever the results statistics are not inherently
       independent of the selection criteria under the null hypothesis",
       and correction for multiple comparisons AT THE SELECTION STAGE
       does not buy that independence (their simulated contrast is
       exactly zero and still reads p < 0.01 under a correctly
       cluster-corrected non-independent ROI; the distortion vanishes
       with an independent dataset). (a) STATE THE SELECTION HISTORY IN
       THE PREREG: gi 1110 entered this chain because L178 found it
       extreme on a depth-2 path statistic, and L206/L207/L210/L211/L213
       then measured closely related path statistics on the same cell on
       the same graph — so the carrier's own null percentiles are valid
       as DESCRIPTIONS of a selected cell, not as p-values for "a cell",
       and the verdict must say so in those words. (b) This card is
       Kriegeskorte's policy step (1), the NONSELECTIVE whole-population
       analysis with multiple-test correction that his policy prefers
       BEFORE any selection; F_COMMON ("DNp33 is one of N equally extreme
       types") is therefore the honest nonselective headline his policy
       predicts, not a disappointing outcome. (c) RETRO-NOTE for the
       digest/draft, no new work: two legs we already have ARE his
       remedies and were under-sold — L212's v783 leg is literally step
       (3), an INDEPENDENT SPECIMEN for the selective analysis (pct .020
       / 12.86x = the least circular number in the chain; promote from
       "exploratory transport check" to "the de-circularising leg",
       keeping the L78 caution for the readout CHANGE rather than for
       the inference), and the homolog gi 928 was PREDICTED, not
       selected, so it is an out-of-selection unit (weaker than
       independent data — shared specimen, reconstruction and
       type-level selection history — but not double-dipped). (d)
       DECLARED OPTIONAL LEG, not required and explicitly bigger than a
       35-min slice: his null-data diagnostic = run the COMPLETE
       pipeline INCLUDING L178's selection stage on a degree-neutral
       rewire and ask whether the selection stage manufactures a carrier
       with our percentiles from a graph with no real carrier. Ref for
       L174. See LANE-RESEARCH.md tick 243.]
"""

assert before.count(A224) == 1, before.count(A224)
assert before.count(A225) == 1, before.count(A225)
assert 'tick 243' not in before, 'already folded'

after = before.replace(A224, A224 + AM224).replace(A225, A225 + AM225)

# invariants: additions only, no checkbox flipped, no item renumbered
assert len(after) > len(before)
for tok, lbl in ((' - [ ] ', 'open'), ('- [x] ', 'checked')):
    pass
assert after.count('\n- [ ] ') == before.count('\n- [ ] '), 'unchecked count changed'
assert after.count('\n- [x] ') == before.count('\n- [x] '), 'checked count changed'
assert after.count('\n## ideas ') == before.count('\n## ideas '), 'ideas sections changed'
# every pre-existing line still present, in order, with only insertions
import difflib
sm = difflib.SequenceMatcher(None, before.splitlines(True), after.splitlines(True))
ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
assert all(o[0] == 'insert' for o in ops), ops
assert len(ops) == 2, ops
ins_lines = sum(o[4] - o[3] for o in ops)

LANE.write_text(after, encoding='utf-8')
print('LANE.md fold OK (AMEND only, 2 pure insertions)')
print(f'  unchecked {before.count(chr(10)+"- [ ] ")} (unchanged), '
      f'checked {before.count(chr(10)+"- [x] ")} (unchanged), '
      f'ideas {before.count(chr(10)+"## ideas ")} (unchanged)')
print(f'  +{ins_lines} lines; {len(before)} -> {len(after)} bytes')
print(f'  md5 {h_before[:12]} -> {hashlib.md5(after.encode()).hexdigest()[:12]}')
