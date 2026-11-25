
## ideas 89 (seeded 2026-11-20, tick 195 by Miso — research tick: the field
## handed us an adversary for our structure metric, a monotone law to beat,
## and a path instrument for the carrier. Precedence UNCHANGED: L169 stays
## FIRST unchecked, then L170-L175; these three sit behind them.)

- [ ] L176. composite-antiphase-metric re-read (ZERO rollouts, stored
      traces only). Guba 2611.22639 fits a composite antiphase score on
      N=7,000 annotated segments and finds that **amplitude balance
      carries w_amp ~ .963** of the discriminative power (AUC .766 vs
      phase-only PLV .741), plus an envelope-peak gate
      g(P)=exp(-alpha*max(0,P-2)) that penalises more than 2 envelope
      peaks per window. Our S has NEITHER term — and our own hard-won
      failure modes are exactly what those terms catch (L46: a pooled
      bilateral S ~ 0 hid a sign-INVERTED side; L50: a duty parity hid
      temporal clustering, 5 s alive / 15 s dead netting the same mean as
      continuous). So re-read the STORED antagonist pool traces (L45a's
      save-every-pool rule means they are already in the npzs) with a
      three-term composite and ask whether our published rank orderings
      survive a field-standard instrument. Scope: the lineage arms whose
      verdicts the draft actually cites (l135/l169/l169b2 base arms
      cutwA / cutng25 / full / twin, plus the l65 Ti/Tr reads), one
      window convention, both sides decomposed.
      PREREG first: (1) the metric definition pinned in the PREREG with
      alpha and the weights FIXED to their published values (we are
      testing OUR claims under THEIR instrument, not fitting a new one —
      a fitted metric on our own traces would be an L162 A2/A3
      post-hoc); (2) primary cell = does the carrier-vs-twin paired sign
      survive (identity axis), secondary = does the arm RANK ORDER
      survive (Spearman vs the stored S/duty ordering), both per side;
      (3) register the degenerate branch explicitly (if amplitude
      balance is near-constant across arms the composite is a monotone
      transform of S and the check is VACUOUS — disclose it as such,
      L55 class); (4) register the opposite branch too: if a stored
      verdict FLIPS under the composite, the draft gains a
      metric-sensitivity paragraph and the claim gets qualified, not
      quietly rewritten.
      Verify: CERT the re-implementation by reproducing each arm's
      STORED S/duty value from the same traces BEFORE computing any
      composite (L85 rule — a bit-identical input anchor cannot catch a
      metric-code bug, and match the stored rounding path); Hilbert band
      stated as a RATIO instrument, never a location one, and
      argmax-at-band-floor quantified (L108); no npz rewritten (read-only
      asserts on mtimes).

- [ ] L177. beta ladder vs the field's monotone-inhibition law
      (rollouts, PREREG first). Guba's DC arm reports that strengthening
      reciprocal inhibition improves antiphase synchronization
      MONOTONICALLY, with Ia reciprocal inhibition ranked first by
      permutation importance. Our beta (inhibition scale) has sat pinned
      at 2 since L32/L65 and was never laddered — and our own
      drive-budget law came out NON-monotone (L50: structure duty is
      non-monotone in drive budget; a chopped schedule beat continuous at
      62% of the drive). So this is a real cross-model discriminator, not
      a confirmation exercise: register the field's monotone law as the
      null to beat.
      Design: beta ladder (e.g. 1.0 / 1.5 / 2.0 / 3.0 / 4.0, pinned in
      the PREREG) on the l65 female cord subnet, af-matched FRESH bisect
      per rung (disclose the gain spread — L139 found in-degree
      renormalization turns small weight changes into a broad effective
      gain family, and beta changes are NOT small), the same seeds every
      rung (paired reads), per-SIDE decomposition mandatory (L46/L101:
      per-joint laterality never generalizes), and the drive-relevance
      probe first (L35: rerun with drive 0 — if beta alone moves S the
      law is intrinsic, which is what our own cord-intrinsic verdict
      predicts).
      Registered predictions: P1 monotone-increasing S in beta (their
      law); P2 non-monotone with an interior optimum (our L50 family);
      P3 saturation then collapse (too much inhibition pins pools at the
      relu floor — in which case assert u_max/mean_X per pool, L36/L38
      viability census, because a floor-pinned pool reads as lost
      structure for a trivial reason). Report WHICH prediction the
      cells carry, and state the obvious limit in the write-up: beta is
      our free parameter, so a monotone result is a model-class
      agreement, not a measurement of the fly.
      Verify: PREREG first; settled active fraction asserted against
      the bisected op point on EVERY rung before any arm is read (L30);
      checkpoint raw rollouts to npz before analysis (L43); forward-chain
      bit-identity anchor at beta=2.0 against the stored l65/l91 arms on
      shared seeds (max 0.0) — that rung is a re-run of existing work
      and must reproduce exactly.

- [ ] L178. linearized top-k path contribution: does the carrier have a
      PATH signature the mass-matched twin does not? (static cost, no
      rollouts; PREREG first.) Liu/Ganguli/Baccus 2611.26101 give a
      complete per-path decomposition with a top-k-paths search that is
      empirically linear in k. We cannot use their theorem (our graph is
      recurrent and our readout S is not an additive output — write that
      limitation into the draft per the L152 bracket), but the top-k
      machinery applies to the LINEARIZED operator at our settled
      operating point: J = g * W (*) relu'(u) evaluated on the settled
      state, paths of depth 2-3 from the carrier and from the
      mass-matched twin into the 22 semantic antagonist pools. This is
      the open mechanistic question on the identity cliff: the carrier
      has ZERO direct antagonist edges and acts 2-hop (L151 crossed law;
      L169c confirmed BOTH levers are 2-hop and neither touches any pool
      directly), so a path-level asymmetry at MATCHED out-mass would
      give the identity result a mechanism instead of only a cause.
      Registered rules: (1) carrier vs twin at matched mass is the
      claim-carrying contrast, with the ng-family cells as the known
      SUPER arm and 100 degree-neutral rewire draws (the l169c protocol,
      already certified admissible) as the null; (2) ABS weights for any
      closure/hop computation (L21: a signed-weight BFS silently drops
      20.3% inhibitory premotor edges) BUT the signed path products
      reported separately, since sign is the whole point of an E/I path
      read; (3) CSR orientation asserted against a known atlas row
      before any mask is trusted (W[target, source]: src_mask[cols] &
      pool_mask[rows], L27/L28); (4) register the degenerate branch — if
      top-k paths rank purely by out-mass the read is a mass restatement
      and the card is a negative (which is itself worth one draft
      sentence). Optional static arm from Realmuto 2611.23441: their
      self-organized connectivity is strong-homonymous /
      weak-heteronymous / VERY-weak-antagonist; check whether BANC's
      five semantic antagonist pairs show the same within >> cross
      premotor asymmetry, and whether carrier and twin sit inside or
      outside it (enumerate pools from peripheral_target_type TOKENS,
      never type-name strings, L101).
      Verify: PREREG first; the linearization asserted against a real
      rollout (one-step J@dX vs the measured one-step response, relative
      error disclosed — a linearized instrument that does not predict
      one step cannot be trusted over three); top-k paths spot-checked
      by brute-force enumeration at depth 2 (exhaustive there, so the
      search is certifiable); every pin re-derived from stored artifacts,
      never from a log sentence (L44).
