#!/usr/bin/env python3
"""Tick-260 fold: bracketed field-informed AMENDMENTS on L260 and L261.

Research-tick rule: fold insight as amendments on EXISTING items, never new
items. Two insertions, both immediately after the item's own last line.

Guards (house discipline):
  - pre-edit md5 asserted (scratch copy taken first, outside this script),
  - both anchors asserted UNIQUE,
  - 'tick 260' asserted ABSENT beforehand,
  - DRY RUN mode prints the difflib opcode summary and writes nothing,
  - PURE INSERTIONS: difflib must report ZERO deletions and ZERO replacements,
  - every pre-existing '- [' line preserved,
  - all '## ideas' headers preserved.
"""
import difflib, hashlib, pathlib, sys

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain')
TGT = ROOT / 'LANE.md'
DRY = '--write' not in sys.argv

A260 = '      on the gated operator, zero new rollouts if the stored X suffices.\n'
A261 = ('      membership-null percentile, and the extended cohort count.\n')

AM260 = """      [tick 260, 11-23 research scan — FIELD-INFORMED AMENDMENT, four
       parts, all of them prior art this card was about to re-derive.
       (i) THE OBJECT HAS A NAME: D·W with D diagonal on the POSTSYNAPTIC
       (row) index is the standard EFFECTIVE CONNECTIVITY matrix of a rate
       network linearised about a fixed point — "the product of the
       connectivity J and a diagonal matrix of (positive) neuronal gains",
       with the gain acting ROW-WISE so that all inputs to the same
       postsynaptic cell share one local gain f*_i (bioRxiv
       2024.12.27.630558 / PMC12330895, and the gain-renormalisation
       supplement bioRxiv 2026.09.15.751810 DC1). Cite, never claim
       (tick-252 rule), and ASSERT THE ORIENTATION in the PREREG: a
       column-scaled D·W is a different operator and nothing downstream
       would notice.
       (ii) THE GATE AS WRITTEN IS WRONG FOR OUR OWN NONLINEARITY. This
       card registers D = 1[X > 0], but brain.py L5 is
       `tau dX/dt = -X + relu(gain*(W@X) + I)` with L18 RMAX = 1.0 and L72
       `target = target.clamp(max=RMAX)` — so the local gain is 1 on
       0 < X < RMAX and EXACTLY 0 at the ceiling, where 1[X>0] scores it 1
       and enters a saturated cell at full gain. REQUIRED: measure the
       saturated fraction on both stored arms (cutwA, f4wA) BEFORE forming
       D, report it beside the branch, and use D = 1[0 < X < RMAX] (the
       card's own soft dX/dnet variant is the same object done properly).
       L208 predicts the fraction is small at a sparse operating point,
       which is exactly why it is measured rather than assumed — at 0.0000
       the correction is free and the gate becomes certified instead of
       hoped.
       (iii) THE DEPTH-k FAMILY IS A NEUMANN SERIES, AND THAT ANSWERS
       QUESTION (b) BEFORE IT IS ASKED. The perturbation response is
       r = (I - W*)^-1 h and the standard expansion is the Neumann series
       (I - W*)^-1 = sum_n (W*)^n — i.e. every depth-d term this lane has
       computed (L206/L209/L210/L215/L216/L218/L228/L261) is a partial sum
       of it, truncation error governed by rho(W*)^n. So: register rho(W*)
       by power iteration FIRST (certified machinery from L210/L216/L218).
       If rho(W*) is near 1, NO low-order truncation can approximate the
       response, which is a sharper and testable version of L228's "the
       fold lives in the relu gate"; the honest comparator is then the
       RESUMMED solve (I - W*)^-1 h by iterative linear solve (Richardson /
       CG on the normal equations), NEVER a dense inverse on ~21k nodes.
       Add a fifth branch cell G_UNTRUNCATABLE for rho(W*) >= ~0.9, where
       the truncation's failure is predicted rather than discovered.
       (iv) NEW FOURTH REGISTERED LEG — THE ISN / PARADOXICAL-SIGN TEST,
       because L228's headline is a textbook signature the lane did not
       know the name of. An inhibition-stabilized network is one at a
       STABLE fixed point "for which the excitatory subnetwork would be
       unstable if inhibitory rates were frozen" (Tsodyks 1997; Ozeki,
       Finn, Schaffer, Miller & Ferster, Neuron 62:578-592 2009; Sanzeni
       bioRxiv 656710), and Miller & Palmigiano (bioRxiv
       2020.10.13.336727) give the general criterion — a cell type responds
       paradoxically iff the network with it omitted has an ODD number of
       unstable modes — plus the clause that is L228 verbatim in our
       currency: "the net steady-state inhibition received by any unstable
       mode of the excitatory subnetwork will change paradoxically, i.e. in
       the same direction as the change in amplitude of that mode."
       L228 measured exactly that: Tr_L's rise carried by exc_srcneg
       +46,219 (removing EXCITATORY edges from net-inhibited sources) while
       the registered disinhibition quadrant SHRANK by -34,315, so the net
       inhibition delivered moved WITH the activity. MEASURE, zero new
       rollouts, on the stored settled X: rho(D·W) for the cord subnet and
       rho(D·W_EE) for the excitatory subnetwork alone. The ISN condition
       is rho(D·W) < 1 AND rho(D·W_EE) > 1 ("stable, but unstable with I
       frozen"). REGISTERED ESCAPE, written before measuring: a
       paradoxical-LOOKING share decomposition is NOT an ISN — if
       rho(D·W_EE) <= 1 the sign pattern has another cause, L228's quadrant
       table stays a description, and the lane does not borrow the
       mechanism's name without its stability condition. Note the regime
       discriminator is the SIGN on the inhibitory population, never a
       magnitude (PMC3933683: cutting all external drive to I took both
       populations ~5/10 Hz -> above 50 Hz in the ISN case, while a
       non-ISN raised E 12->35 Hz and LOWERED I 14->11 Hz).]
"""

AM261 = """      [tick 260, 11-23 research scan — FIELD-INFORMED AMENDMENT: the depth
       sweep is a NEUMANN SERIES partial-sum sweep of the linear response
       operator (I - W*)^-1 = sum_n (W*)^n (bioRxiv 2024.12.27.630558 /
       PMC12330895), so (a) is a truncation-convergence profile and its
       governing quantity is rho(W*), not an unnamed "spectral gap" —
       report rho(W*) and the predicted truncation error rho^d BESIDE the
       measured agreement at each depth, so a non-monotone profile can be
       told from a slowly-converging one. The registered A_inf escape is
       strengthened, not weakened: the series' limit IS the resummed
       response, so if agreement is 2/2 at every depth >= 2 the right
       report is the RESUMMED operator's asymmetry, with the Perron reading
       as its leading term. Also inherited from L260's amendment: whichever
       gate L260 certifies (D = 1[0 < X < RMAX], NOT 1[X>0]) is the one
       this sweep must use, or the two cards measure different operators.]
"""

pre = TGT.read_text()
assert 'tick 260' not in pre, "'tick 260' already present"
assert pre.count(A260) == 1, f'A260 anchor count {pre.count(A260)}'
assert pre.count(A261) == 1, f'A261 anchor count {pre.count(A261)}'

post = pre.replace(A260, A260 + AM260).replace(A261, A261 + AM261)

pl, ql = pre.splitlines(True), post.splitlines(True)
sm = difflib.SequenceMatcher(None, pl, ql, autojunk=False)
ins = dels = reps = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'insert':
        ins += (j2 - j1)
    elif tag == 'delete':
        dels += (i2 - i1)
    elif tag == 'replace':
        reps += 1
assert dels == 0, f'{dels} DELETIONS — refusing'
assert reps == 0, f'{reps} REPLACEMENTS — refusing'

box_pre = [l for l in pl if l.startswith('- [')]
box_post = [l for l in ql if l.startswith('- [')]
assert box_pre == box_post, 'a "- [" line changed'
ideas_pre = [l for l in pl if l.startswith('## ideas')]
assert ideas_pre == [l for l in ql if l.startswith('## ideas')], 'ideas header moved'

unchecked = sum(1 for l in box_post if l.startswith('- [ ]'))
checked = sum(1 for l in box_post if l.startswith('- [x]'))
print(f'opcodes: insert {ins} lines, delete {dels}, replace {reps}')
print(f'boxes unchanged: unchecked {unchecked}, checked {checked}, '
      f'ideas {len(ideas_pre)}')
print(f'chars {len(pre)} -> {len(post)}')
print(f'md5 pre {hashlib.md5(pre.encode()).hexdigest()[:16]}')

if DRY:
    print('DRY RUN — nothing written. re-run with --write')
    sys.exit(0)

TGT.write_text(post)
chk = TGT.read_text()
assert chk == post, 'readback differs'
print(f'WROTE. md5 post {hashlib.md5(chk.encode()).hexdigest()[:16]}')
