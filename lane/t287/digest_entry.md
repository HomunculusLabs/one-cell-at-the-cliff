
## L294 — what predicts a weight-matched set's effect: the gain delta and the removed weight both track it (tick 287, 2026-11-25) **[lab]**

**Question.** L291 cut 15 sets of matched synapse weight from one carrier
and could not say why their effects scattered from -2.90 to +14.74 F. One
pattern had been seen after the fact and left unbanked: an arm's effect
seemed to rank with the gain compensation the bisection applied to it. Is a
set's effect predicted by the drive it removed in the normalised graph, by
the gain delta — or by nothing measurable from the set? The covariates were
registered and hashed before any of them was scored against an effect. No
rollouts: this is a re-analysis of the stored L290 and L291 arrays.

**Answer: the gain delta tracks the effect, and so does the removed
weight.** On 33 bisected arms, ranked within set size:

- **Gain delta** (bisected gain minus base): +0.70, q 0.0001. This confirms
  L291's after-the-fact +0.82 as a real association on the wider population.
- **Removed effective weight** (sum of log1p synapse count over the removed
  edges): +0.55, q 0.0042, positive in all three size strata. I had
  registered the opposite — that weight would *not* carry — so this is a
  failed prediction of mine, and the more useful result: it is the only
  covariate available *before* any rollout.
- **The rest of the network moves too.** The 21,482 cells outside the
  readout pools shift with the gain delta (+0.52, q 0.006), but subtracting
  that common shift leaves 97% of the association (+0.68). The pool tracks
  the gain beyond a global shift.

The two predictors are near-orthogonal (rank correlation +0.22 between
them, seen after the fact), so they are not one quantity in two currencies.

**Two hairline legs, stated rather than smoothed over.** The registered
label is "gain-delta mediated", and it rests on two marginal results.
Out of sample, on L290's 18 sets, the gain leg is +0.45 at p 0.088 — it
misses 0.05, and its smallest stratum (six 11-edge sets) runs the *other*
way at -0.37. And the twin leg — the same set cut at its bisected gain and
at the base gain — moved in the gain's direction in 6 of 7 pairs, p = 6 of
128 sign-flip patterns against a bar of 6.4. One more pattern flips the
label to "marker". What holds under either neighbour: the gain delta, the
removed weight and the global shift all track the effect. Predictions
scored 4 of 6.

**What it does not say.** L227 still binds: you must run the bisection to
have the gain delta, so a fit on it is a mechanism probe and a cheap screen,
never a prediction for an unseen set. The gain delta carries about half
the rank variance; the two predictors were not modelled together here. The
sign-split and distinct-target covariates
are degenerate on this carrier (no negative weights; one target per edge,
none inside the pools). The removed weight is entangled with membership of
one heavy edge (e14), and that is not separated here — it is the next card.

**Disclosed.** The PREREG's header time was corrected after its first hash
and before the analysis script existed; both hashes are kept. My
verification script was wrong twice in its first run (`math.copysign` takes
the magnitude of its first argument; a Fisher test sat on the wrong margin)
while the analysis was right both times, confirmed by enumerating the 128
patterns by hand — fixed before anything was reported. One carrier, one
substrate, one gain family; 16 seeds shared by every arm, so the
out-of-sample leg is new in sets, not in seeds.

*2026-11-25 (lane tick 287). Research only; no runtime change made. Every
future cut arm keeps both its bisected and its fixed-gain twin, since the
gain is part of the intervention. Queue card L294 is closed; L297 registers
the two-predictor follow-up.*

Evidence: `peabrain-lab/banc/l294/{PREREG.md, PREREG.sha256,
PREREG_FREEZE_NOTE.md, l294_final.py, run.out, results_l294.json,
posthoc_check.py, posthoc_check.out, repro_check.py, VERDICT.md}`; queue
card L294 (closed) and L297 (open) in `~/critters/peabrain/LANE.md`.
