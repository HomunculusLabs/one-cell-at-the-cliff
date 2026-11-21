#!/usr/bin/env python3
"""L183 master fold -- the TEXT ledger: every declared edit, in order, with
its stage and its reason.  Numbers are placeholders ({{key.path|format}},
{{kn:path}} = "k of n", {{ks:path}} = "k/n", {{ci:path}} = "mean [lo, hi]",
{{TABLE:name}}) resolved from paper/numbers.json by l183_fold.render().

Stages follow banc/l183_BRIEF_manuscript.md:
  1 title + abstract        2 Results (scan-first reorder)   3 Methods
  4 Introduction / related work (+ the reference entries those paragraphs
    cite: the bidirectional citation gate forbids either half alone)
  5 Limitations + Discussion (the wet-lab prediction)
  6 references audit (no body text; gate + bib only)
  7 follow-up fold (L190b, owner-directed): the single-edge cut and its
    sham enter 2.4 (Table 3b); 3.7 gains the batch label; section 4 drops
    the two "is not reported here" markers.  Stage-7 edits anchor on text
    that earlier stages RENDERED, so a moved upstream number breaks the
    anchor loudly instead of leaving a stale copy.

CURRENT_STAGE is the stage the live draft has reached; l183_verify replays
the ledger up to it.
"""
CURRENT_STAGE = 7

EDITS = []


def rep(id, stage, old, new, reason, wrap=False):
    EDITS.append(dict(kind='rep', id=id, stage=stage, old=old, new=new,
                      wrap=wrap, reason=reason))


def span(id, stage, start, end, new, reason, wrap=False):
    EDITS.append(dict(kind='span', id=id, stage=stage, start=start, end=end,
                      new=new, wrap=wrap, reason=reason))


# =========================================================== STAGE 1 =======
span('E01-title', 1,
     '## Title (RE-SCOPED v3.8 — L168 sufficiency fold; alternates kept)\n',
     '## Abstract (draft)\n',
     '''## Title

**Removing DNp33-L selectively raises right-tibia antagonist duty in a
perturbed fly connectome model**

Rationale: this is the form the third-round referee proposed, adopted
unchanged. The previous title credited a mass-twin control with isolating
cell identity, and that twin is silent on the base it is removed from
(reported in the Results); it also called the effect an all-or-none regime transition, which a
readout crossing a registered band does not show. The adopted title states
the measured contrast and its scope: "selectively" is the outcome of a
single-cell scan with matched comparators, "perturbed" says that 24 other
descending neurons have already been removed, and "model" says that the
object is one rate model on one connectome. What was matched, and how well,
is stated in the abstract, where there is room to say it. Retired titles are
recorded in the changelog above.

''',
     'referee r3 (astra) title; r2 N1 (silent twin) and r3 section 3 '
     '("all-or-none" not shown)', wrap=True)

span('E02-abstract', 1, '## Abstract (draft)\n', '## 1. Introduction\n',
     '''## Abstract (draft)

Connectome-constrained models can ask which cells matter, not just whether
wiring does. We run the nerve-cord subnetwork of a female Drosophila
connectome (BANC v626) as a rate model in which descending neurons have
lost their brain input, every arm gain-bisected to a matched operating
point. On a base with 24 heavy descending neurons already removed,
we delete each of the next {{NL.n_window|i}} one at a time and score
right-tibia flexor-extensor antiphase duty. Only DNp33-L lifts it into the
registered high class ({{kn:S.sc25}} seeds; base {{kn:S.cutwA}}). Matched
controls stay low: a mass twin, silent on this base ({{kn:S.sc26}}); two
delivered-drive twins, one of the carrier's class and sign
({{S.dmA.kR|i}} and {{kn:S.dmC}}); and a signed-current twin ({{kn:R3}}). The
contrast replicates on a second batch
({{kn:R1.sc25.pooled_b39_b40_rematched}} pooled) and holds at the base's own
gain ({{kn:R1.sc25.fixed}}); a gain-only null moves the base between
{{R2.kR_max|i}} and {{R2.kR_min|i}} of {{B5.n|i}} with no cell removed. The
flip is a change in shared timing, not rate: antiphase survives pairing
flexor and extensor traces from different runs ({{TP.sc25.cross_k|i}} of
{{DS.n_cross_pairs|i}} pairs), and in the continuously driven 1.4-Hz segment
the carrier-removed network keeps it ({{TP.sc25.fast_k|i}} of
{{DS.n_seeds|i}}) while the base and all three scan twins score
{{TP.cutwA.fast_k|i}}. The carrier is sufficient, not unique, and
set-dependent: of seven carrier-free cohorts mass-matched to the same window
exactly one reaches the class ({{P.cutscr0.kR|i}} of {{P.cutscr0.n|i}}), a
downstream interneuron does so alone on the chopped readout ({{kn:A.rcut}}),
and the effect is absent at a stricter synapse floor. Which clock the timing
follows is unresolved. The claim concerns one perturbed model graph, not the
fly; we state a sign-specific prediction for unilateral DNp33 silencing.

''',
     'brief stage 1: control ladder, two batches, gain robustness, the 1.4-Hz '
     'panel, honest scoping; r2 N4 (abstract contradicted the body), r3 '
     '(canonical 41/50 not 39/48; drop all-or-none, kill-to-super, the '
     'mass-only band, the male-ladder sentence, the pooled p = .008)',
     wrap=True)

# =========================================================== STAGE 2 =======
rep('E10-results-lead', 2, '## 2. Results\n\n### 2.6 The dose cliff',
    '''## 2. Results

The results are ordered by what the title claim rests on. §2.1 to §2.5
report the single-cell scan and the controls, replication, timing analysis
and pathway arms run on it. §2.6 to §2.14 report the cohort-level lineage
that located the cell, kept with the scope the later results leave it. Arms
are named in words, and the stored arm code is given once in each table so
that every cell can be traced. Throughout, the base is the nerve-cord
closure with the 24 heaviest non-glutamatergic descending neurons removed
(§3.5), and a seed counts as structured when its right-tibia antiphase duty
is at least {{D.seed_bar|f2}}. An arm is in the super class when at least
{{BD.super_kR_min|i}} of {{BD.n|i}} seeds are structured and the mean duty
is at least {{BD.super_meanR_min|f2}}, and in the not-super class when at
most {{BD.not_kR_max|i}} are and the mean is at most
{{BD.not_meanR_max|f2}} (§3.6); arms between those bands are called
intermediate. Crossing a registered band classifies one readout on one
graph. It is not evidence of a bifurcation.

### 2.1 A single-cell scan: one of {{NL.n_window|i}} deletions lifts the readout

The scan removes one descending neuron at a time from the base: each of the
{{NL.n_window|i}} cells at ranks 25 to 58 of the removal-mass ladder, plus
two cells chosen from outside the window to match the carrier's delivered
drive. Every arm ran on one fresh batch of {{ME.n_seeds|i}} seeds (batch M),
at its own gain re-bisected to the common active fraction, with the arms,
bands and branch order registered before any rollout [l175.meta]. The
stored-gain and bit-identity certificates were green:
{{CT.c0a175_checks|i}} anchor comparisons against the earlier raw traces and
{{CT.cert_x_checks|k}} cross-worker comparisons of the base, all with
maximum difference {{CT.c0a175_max|raw}} [l175.certs].

Table 1 gives every arm with three readouts side by side: the registered
one (antiphase duty in the chopped 0.7-Hz segments), the same statistic in
the continuously driven 1.4-Hz segment, and a cross-seed control in which
the flexor trace of one run is paired with the extensor trace of another
(§2.3).

{{TABLE:scan}}

Table 1 [l175.scan, l184.threepanel]. Rate is the cell's mean rate on the
base before its removal, over three census seeds. Drive is mean rate times
summed absolute outgoing weight, relative to the carrier. Gain is the arm's
re-bisected gain relative to the base. Counts are seeds with duty at least
{{D.seed_bar|f2}} out of {{ME.n_seeds|i}}, and ordered seed pairs out of
{{DS.n_cross_pairs|i}} in the cross-seed column. Sign is the effective sign
of the cell's output (+ excitatory, − inhibitory). "Partial" is the
registered sub-label of the not-super class defined in §3.6.

**Only the carrier reaches the super class.** Removing the carrier gives
{{kn:S.sc25}} structured seeds (Wilson lower bound {{S.sc25.lbR|f3}} on
the proportion) at mean duty {{S.sc25.meanR|f3}}, against {{kn:S.cutwA}} and
{{S.cutwA.meanR|f3}} for the base. Of the {{NL.n_window|i}} window arms,
{{NL.n_super|i}} is super, {{NL.n_intermediate|i}} are intermediate and
{{NL.n_not|i}} are not-super [l175.null]. The registered branch that fired
is the one in which the flip follows the cell and not its delivered drive
[l175.verdict].

**The mass twin is silent, and we say so.** The rank-26 cell matches the
carrier's removal mass to {{xor.pair_delta|e}} of cohort mass [xor] and
does not flip ({{kn:S.sc26}}, {{S.sc26.meanR|f3}}). On this base, however,
it fires at a mean rate of {{CE.mass_twin_319.x_mean|f4}} against the
carrier's {{CE.carrier.x_mean|f4}}, and so delivers
{{ME.twin_drive_ratio|f4}} of the carrier's drive [l175.census, l175.meta].
Deleting a cell that is not firing removes almost nothing from a rate
model. The mass twin therefore controls static weight and nothing else, and
its outcome is one draw from the silent-cell null described below, not a
matched control. An earlier draft of this paper was named after this
comparison. The present one does not rest on it.

**Delivered-drive twins do not flip.** Two comparators were selected, by a
rule fixed before any rollout, as the cells whose delivered drive is
nearest the carrier's. One was drawn from all {{CE.dmA.pool_n|k}} candidate
cells of any class (drive ×{{S.dmA.drive_ratio|x3}} of the carrier's; it
turned out to be inhibitory) and one from the {{CE.dmC.pool_n|i}}
candidates of the carrier's own class and sign
(×{{S.dmC.drive_ratio|x3}}) [l175.census]. Neither flips: {{kn:S.dmA}} at
{{S.dmA.meanR|f3}} and {{kn:S.dmC}} at {{S.dmC.meanR|f3}}. The two agree,
so the result does not depend on the sign mismatch of the first.

**Other active cells do not flip either.** {{BR.n_active|i}} of the
{{BR.n_window|i}} window cells are active on the base [l175.branch]. Of the
{{BR.A_n|i}} other than the carrier, none reaches the super class,
including the {{NL.n_overdrive|i}} that deliver more drive than the carrier
does (×{{NL.overdrive_min|x2}} to ×{{NL.overdrive_max|x2}}) [l175.null].
Across the active cells, delivered drive does not order the readout
(Spearman ρ = {{BR.rho_all_drive_meanR|s3}}; {{BR.rho_exc_drive_meanR|s3}}
among the {{BR.n_active_exc|i}} excitatory ones) [l175.branch]. Not
reaching the super class is not the same as having no effect: the active
excitatory cells at ranks 33 and 34 drive the count to {{S.sc33.kR|i}} and
{{kn:S.sc34}} when removed, the opposite direction.

**The null is wide, and it covaries with gain.** Removing any one of the
{{NL.n_silent|i}} silent cells, which deliver essentially nothing, gives
between {{NL.silent_kR_min|i}} and {{NL.silent_kR_max|i}} structured seeds
of {{ME.n_seeds|i}} and a mean duty between {{NL.silent_meanR_min|f3}} and
{{NL.silent_meanR_max|f3}} [l175.null]. All {{NL.n_intermediate|i}}
intermediate arms sit inside that range, and two of them (ranks 27 and 40)
sit at the edge of the super band. Across the {{NL.n_noncarrier|i}}
non-carrier arms the readout falls as the re-bisected gain rises (Spearman
ρ = {{NL.rho_gain_meanR_noncarrier|s3}};
{{NL.rho_gain_meanR_silent|s3}} among the silent cells, whose gain shifts
are at most {{NL.silent_gain_abs_max|p2}}%) [l175.null]. The carrier runs
against that trend: its gain rises by {{S.sc25.gain_pct|p2}}% and its duty
is the highest in the table. One arm (rank 47) bisected to an outlying gain
({{NL.max_gain_pct|sp2}}%) and should be read with care. These are
associations across different deletions, not a gain intervention; §2.2
supplies the intervention.

Scope of this subsection: one batch, one base, the chopped classifier as
the registered readout, and comparators matched on unsigned, time-averaged
drive pooled over all targets.

### 2.2 Replication, the gain-only null and the signed-current twin

A second fresh batch (batch N, {{M5.n_seeds|i}} seeds) re-ran the carrier,
the mass twin, both drive twins, the two edge-of-band cells and the base,
each in two gain forms. The re-matched form uses the arm's own re-bisected
gain, as in §2.1. The fixed form uses the base's gain, so that the graph is
the only thing that differs from the base. The arms, bands and branches
were registered before any rollout, and the comparator of the third
experiment below was selected after registration and before any rollout
[l185.meta, l185.certs].

{{TABLE:rep}}

Table 2 [l185.base, l185.r1, l185.r3, l175.scan]. Cells are structured
seeds of {{M5.n_seeds|i}} and mean duty. The pooled column unions batches M
and N at the re-matched gain.

**The carrier contrast replicates and does not depend on the gain
re-match.** Carrier removal gives {{kn:R1.sc25.rematched}} at
{{R1.sc25.rematched.meanR|f3}} at its re-matched gain and
{{kn:R1.sc25.fixed}} at {{R1.sc25.fixed.meanR|f3}} at the base's own gain.
At that common gain it sits {{R1.sc25.fixed_vs_base_same_gain.mean|s3}}
above the base on the same seeds, with
{{R1.sc25.fixed_vs_base_same_gain.n_up|i}} seeds up and
{{R1.sc25.fixed_vs_base_same_gain.n_dn|i}} down by the registered margin
[l185.r1]. Pooled over the two batches the carrier arm is
{{kn:R1.sc25.pooled_b39_b40_rematched}}. The mass twin, both drive twins
and the base stay in the not-super band in both gain forms.

**Neither edge-of-band cell promotes.** The rank-27 cell regresses to the
null ({{kn:S.sc27}} on batch M, {{kn:R1.sc27.rematched}} on batch N). The
rank-40 cell stays elevated at its re-matched gain
({{kn:R1.sc40.rematched}}, mean {{R1.sc40.rematched.meanR|f3}}, below the
{{BD.super_meanR_min|f2}} bar) and loses the elevation entirely at the
base's gain ({{kn:R1.sc40.fixed}};
{{R1.sc40.fixed_minus_rematched.mean|s3}} against its re-matched self, with
{{R1.sc40.fixed_minus_rematched.n_up|i}} seeds up and
{{R1.sc40.fixed_minus_rematched.n_dn|i}} down). Its lift is what its
{{R1.sc40.rematched.gain_delta_pct|sp2}}% gain shift produces, not a
deletion effect. It is the worked example of why a non-carrier elevation
that rides a re-bisected gain needs its fixed-gain arm, and a third batch
agrees ({{S40.rematched.kR|i}} of {{S40.rematched.n|i}} re-matched,
{{S40.fixed.kR|i}} of {{S40.fixed.n|i}} fixed [l187.sc40_pooled]).

**A gain-only null: the base is gain-sensitive at the sub-percent level.**
With no cell removed, the base was run at five gains spanning
{{R2.span_pct|i}} percent:

{{TABLE:null}}

The slope is {{R2.slope_meanR_per_0p1pct|f4}} mean duty per +0.1% gain (95%
CI [{{R2.slope_ci95.0|f4}}, {{R2.slope_ci95.1|f4}}];
{{R2.n_seeds_negative_slope|i}} of {{M5.n_seeds|i}} seeds negative)
[l185.r2]. A {{R2.span_pct|i}}-percent gain span thus moves the base
between {{R2.kR_max|i}} and {{R2.kR_min|i}} structured seeds with no
deletion at all, though no gain-only arm reaches the super class. The same
slope reproduces R² = {{R2.scan_comparison.within_half_pct.r2_of_gain_null_line|f3}}
of the mean-duty spread of the
{{R2.scan_comparison.within_half_pct.n|i}} scan arms whose gain shift is
within half a percent
({{R2.scan_comparison.silent_within_half_pct.r2_of_gain_null_line|f3}} for
the {{R2.scan_comparison.silent_within_half_pct.n|i}} silent ones), so
roughly a third to a half of the scan's null width is gain sensitivity
[l185.r2]. The carrier runs against it: a gain rise of
{{S.sc25.gain_pct|p2}}% should lower duty, and its duty is the highest.

Two cautions come with this null. Same-seed pairing buys no variance
reduction once the gain or the graph changes, so the paired differences in
§2.1 to §2.5 should be read as differences of batch means. And the slope
does not transfer between graphs: it is negative on carrier-present graphs
and positive on carrier-absent ones (§2.4), so it must not be extrapolated
across arms. For that reason a fixed-gain rule is adopted (§3.4): an arm's
effect is read at the base's gain first, and at its re-matched gain second.

**A signed-current twin does not flip.** The drive twins of §2.1 match an
unsigned scalar summed over all targets. The third-round referee objected
that they need not match what the carrier delivers to the scored pools. We
therefore registered a signed current: gain times mean rate times the
direct plus one-relay weight onto the right-tibia flexor and extensor
pools, gated to the linear regime (§3.5). The carrier's value is
({{R3.carrier_J.0|f5}}, {{R3.carrier_J.1|i}}) for the flexor and extensor
pools: no direct edge onto either, a small net-inhibitory relayed current
onto the flexors and none onto the extensors. Neither drive twin matches
it. The nearest of {{R3.pool_n|k}} active cells is DNg19-R (relative
distance {{R3.dist_rel|f3}}; unsigned drive ×{{R3.drive_ratio|x2}}),
excitatory like the carrier [l185.r3]. Removing it does not flip the
readout: {{kn:R3}} (Wilson upper bound {{R3.ubR|f3}} on the proportion),
mean {{R3.meanR|f3}}, at a re-bisected gain shift of
{{R3.gain_delta_pct|sp2}}% that by the null above would push duty up, not
down. This comparator is one batch and one definition. It matches a
time-averaged, linearised current over paths of at most two synapses; the
cell is rail-saturated (mean rate {{R3.x_mean|f3}}); and unlike the carrier
it receives cord input.

Taken together, the contrast stands on two batches and both gain forms,
against a mass twin, two delivered-drive twins and one signed-current twin.

### 2.3 What changes is shared timing, not rate

The readout is the fraction of sliding windows in which the right-tibia
flexor and extensor pool means are anticorrelated (§3.6). A statistic of
that kind can rise because the two pools interact differently within a run,
or because each becomes more reproducibly locked to something both share,
the stimulus above all. The third-round referee separated the two by
pairing the flexor trace of one run with the extensor trace of a different
run of the same arm. Those traces cannot have interacted, so whatever
antiphase survives is carried by timing that is common across runs. The
analysis below re-scores the stored traces of batch M. It involves no new
rollouts, and its definitions were written down before the numbers were
computed.

**Most of the carrier's chopped-window duty survives cross-seed pairing.**
In the carrier-removed arm the mean duty is {{TP.sc25.chopped_mean|f3}} for
true pairs and {{TP.sc25.cross_mean|f3}} for cross-seed pairs, and
{{TP.sc25.cross_k|i}} of {{DS.n_cross_pairs|i}} ordered pairs clear the
{{D.seed_bar|f2}} bar. In the base the corresponding values are
{{TP.cutwA.chopped_mean|f3}} and {{TP.cutwA.cross_mean|f3}}, with
{{TP.cutwA.cross_k|i}} of {{DS.n_cross_pairs|i}} pairs clearing it
[l184.threepanel]. The cross-seed duty rises by
{{Q3.sc25.delta_cross|s3}} between base and carrier removal while the
same-seed duty rises by {{Q3.sc25.delta_same|s3}}. The shared-timing
component therefore increases by more than the whole net effect
({{QR.cross_over_same_increment|x2}} times it), and the run-specific
remainder shrinks ({{Q3.sc25.delta_residual|s3}}) [l184.q3,
l184.q3_ratios]. The {{DS.n_cross_pairs|i}} pairings reuse
{{DS.n_seeds|i}} seeds and are a descriptive control, not independent
trials, and the two duties must not be subtracted to obtain a variance
fraction.

**Mean rates do not carry it.** Pool mean rates barely move between base
and carrier removal: flexor {{Q3.cutwA.flex|f4}} to {{Q3.sc25.flex|f4}} and
extensor {{Q3.cutwA.ext|f4}} to {{Q3.sc25.ext|f4}} [l184.q3]. Both pools
sit near the background current (§3.9), a property of the readout that the
reader should hold in mind. The statistic is the sign of the correlation
between small fluctuations of a near-silent flexor pool and bursts in a
small extensor pool.

**A uniform change in drive transmission does not explain it either.** At
the drive frequency the harmonic amplitude grows in the flexor pool
({{Q1.chopped.f.amp.base|m2}} to {{Q1.chopped.f.amp.sc25|m2}}, in units of
10⁻³; paired change {{Q1.chopped.f.amp.diff|sm2}}
[{{Q1.chopped.f.amp.lo|m2}}, {{Q1.chopped.f.amp.hi|m2}}]) and shrinks in
the extensor pool ({{Q1.chopped.e.amp.base|m2}} to
{{Q1.chopped.e.amp.sc25|m2}}; {{Q1.chopped.e.amp.diff|sm2}}
[{{Q1.chopped.e.amp.lo|m2}}, {{Q1.chopped.e.amp.hi|m2}}]). The signed
on-minus-off contrast of the chopping gate strengthens in both pools
({{Q1.chopped.f.gate.base|m2}} to {{Q1.chopped.f.gate.sc25|m2}} and
{{Q1.chopped.e.gate.base|sm2}} to {{Q1.chopped.e.gate.sc25|sm2}})
[l184.q1]. But the any-class drive twin matches the carrier-removed arm on
absolute extensor gate contrast, and the same-class drive twin exceeds it
in both pools, without either flipping [l184.q1_twins]. Gate penetration
alone cannot be the explanation.

**The 1.4-Hz segment separates the carrier-removed network from every
matched control.** In the continuously driven middle segment the
carrier-removed arm keeps {{TP.sc25.fast_k|i}} of {{DS.n_seeds|i}}
structured seeds (mean {{TP.sc25.fast_mean|f3}}), while the base, the mass
twin and both drive twins score {{TP.cutwA.fast_k|i}}, {{TP.sc26.fast_k|i}},
{{TP.dmA.fast_k|i}} and {{TP.dmC.fast_k|i}} [l184.threepanel]. Only one
other scan arm has any structured seed there (rank 47,
{{TP.sc47.fast_k|i}} of {{DS.n_seeds|i}}, the gain outlier of §2.1).
Applied descriptively, the registered bands put no arm in the super class
in this segment: the carrier-removed network is the strongest arm there,
not a window-independent super arm.

**Subtracting the stimulus templates leaves a deletion effect.** Removing
the fitted chopping-gate template from every trace leaves the
carrier-minus-base same-seed difference at {{SE.minus_gate.d_same|s3}}.
Removing the fitted drive-frequency tone leaves
{{SE.minus_tone.d_same|s3}}, and removing both leaves
{{SE.minus_both.d_same|s3}} with the cross-seed difference still
{{SE.minus_both.d_cross|s3}} [l184.sens]. The simple gate step is therefore
not what the shared component rides on; delayed or otherwise shared
temporal structure survives the subtraction. None of these decompositions
is a causal mediation analysis.

**Anatomy: the carrier reaches the right tibia only indirectly.** The
carrier has {{AN.n_incident|i}} incident edges on the base:
{{AN.n_in|i}} inputs, all from other descending neurons, and
{{AN.n_out|i}} outputs. No output lands on a right-tibia motor neuron. Of
its {{AN.n_out_intrinsic|i}} intrinsic targets, {{AN.n_out_premotor|i}}
synapse directly onto right-tibia motor neurons and
{{AN.n_out_intrinsic_other|i}} do not; the other
{{AN.n_out_other_motor|i}} outputs go to other motor neurons
[l184.anatomy]. The comparators share almost none of this footprint. The
mass twin, the rank-27 cell and the any-class drive twin share
{{AN.overlap.sc26.shared|i}}, {{AN.overlap.sc27.shared|i}} and
{{AN.overlap.dmA.shared|i}} of the carrier's targets, the same-class drive
twin {{AN.overlap.dmC.shared|i}}, and the rank-40 cell
{{AN.overlap.sc40.shared|i}}, one of which is the interneuron examined
next.

### 2.4 A downstream interneuron: neither necessary nor sufficient for the signature

The strongest anatomical candidate for a route from the carrier to the
scored pools runs through one cord interneuron, the left IN06B033 cell
(hereafter the relay). It is an inhibitory cell with {{RL.in_edges|i}}
inputs and {{RL.out_edges|i}} outputs that receives
{{RL.carrier_to_relay.syn|i}} synapses from the carrier and is active on
the base (mean rate {{RL.census_x_mean_3seed|f3}}) [l187.relay]. The
top-ranked four-edge paths from the carrier to both right-tibia pools pass
through it. A third fresh batch (batch P, {{M7.n_seeds|i}} seeds) tested
that route by intervention, with two registered poles: the relay is the
carrier's conduit, so that silencing or cutting it reproduces carrier
removal, or it is inert. The data landed on neither.

{{TABLE:relay}}

Table 3 [l187.base, l187.arms]. Cells are structured seeds of
{{M7.n_seeds|i}} and mean duty; the contrast column is the paired mean
difference from the base at the base's gain with its 95% interval over
seeds.

**Relay removal alone raises the chopped duty, with the carrier present.**
Cutting the relay gives {{kn:A.rcut}} structured seeds at its re-matched
gain and {{kn:A.rcutF}} at the base's gain (mean {{A.rcut.meanR|f3}} and
{{A.rcutF.meanR|f3}}), {{ci:A.rcutF.vs_base}} above the base at the base's
gain [l187.arms]. Clamping its activity to zero inside the measurement
window gives {{kn:A.rsilW}} at mean {{A.rsilW.meanR|f3}}. The count passes
the super band and the mean falls just short of its
{{BD.super_meanR_min|f2}} bar, so that arm is unresolved by the registered
rule although its direction is the same ({{ci:A.rsilW.vs_base}}).

**It is not a copy of carrier removal.** On the same seeds the relay-cut
arm reads below carrier removal on the chopped duty at the base's gain
({{ci:C.rcutF_minus_sc25F}}, not resolved) [l187.contrasts]. More
decisively, the carrier's 1.4-Hz signature is absent. The three relay arms
read {{A.rcut.mean14|f3}} to {{A.rsilW.mean14|f3}} mean duty in the
continuous segment, against {{A.sc25.mean14|f3}} and
{{A.sc25F.mean14|f3}} for carrier removal and {{AB.mean14|f3}} for the
base.

**The carrier's effect does not need the relay.** With the relay already
removed, removing the carrier as well adds {{ci:C.occ_minus_rcut}} chopped
duty at re-matched gains and {{ci:C.occF_minus_rcutF}} at the base's gain.
It also adds the whole 1.4-Hz signature: {{ci:F.occ_minus_rcut}}
re-matched and {{ci:F.occF_minus_rcutF}} fixed, with
{{F.occ_minus_rcut.n_pos|i}} and {{F.occF_minus_rcutF.n_pos|i}} of
{{M7.n_seeds|i}} seeds positive [l187.contrasts, l187.fast]. The 1.4-Hz
contrasts were computed after the registered analysis and are labelled
descriptive.

**An opposite-sign input does not cancel the carrier (push-pull).** The
rank-40 cell of §2.2 sends {{RL.sc40_to_relay.syn|i}} inhibitory synapses
to the same relay, so removing it together with the carrier might have
restored the relay's input balance. It does not. At the base's gain the
double removal is {{kn:A.ppF}} at {{A.ppF.meanR|f3}},
{{ci:C.ppF_minus_sc25F}} above carrier removal alone, with the same 1.4-Hz
duty ({{A.ppF.mean14|f3}} against {{A.sc25F.mean14|f3}}) [l187.arms,
l187.contrasts]. The rank-40 cell is nearly silent on the base (mean rate
{{RL.sc40_census_x_mean|f3}}), and with the carrier gone its removal lifts
the relay's rate only from {{RR.sc25|f3}} to {{RR.pp|f3}} (base
{{RR.base|f3}}) [l187.relay, l187.relay_rate].

**The sign of the gain sensitivity flips with the carrier.** At its
re-matched gain the double-removal arm falls to the band edge
({{kn:A.pp}}, {{A.pp.meanR|f3}}). That tracks gain, not the cell: it
re-bisects to {{A.pp.gain_delta_pct|sp3}}% where carrier removal
re-bisects to {{A.sc25.gain_delta_pct|sp3}}%. In all three carrier-absent
graphs duty rises with gain (slopes {{GS.sc25.slope_per_0p1pct|s4}} to
{{GS.pp.slope_per_0p1pct|s4}} per +0.1%), and in the carrier-present
graphs it falls ({{GS.sc40.slope_per_0p1pct|s3}} for the rank-40 removal;
{{R2.slope_meanR_per_0p1pct|s4}} for the base) [l187.gain_slopes, l185.r2].
This is post hoc and descriptive, and it is the reason for the fixed-gain
rule of §2.2.

**A construction identity worth recording.** A relay clamped from the
first step of the run is the relay-cut graph. The stored traces are
bit-identical at {{M7.silcut_anchor_seeds|i}} anchor seeds (maximum
difference {{M7.silcut_max|raw}}), and the clamped arm re-bisects to the
same gain as the cut arm [l187.meta, l187.certs]. A full-run clamp
therefore adds no evidence to a cut, and any silence-versus-cut gap in this
paper is settle history plus gain (cf. §2.9).

Reading: the relay is not the carrier's necessary conduit, and silencing it
does not reproduce the carrier's phenotype, but it is not inert. Removing
this one cord interneuron lifts the registered classifier into the super
band on its own, so that classifier by itself is not specific to the
carrier. The 1.4-Hz panel is what separates them here: the carrier-absent
arms read {{A.pp.mean14|f3}} to {{A.occ.mean14|f3}} and every
carrier-present arm at most {{A.rsilW.mean14|f3}}. What the relay's removal
does change downstream is the rate of one further interneuron, which rises
from {{G7.cutwA|f2}} on the base to {{G7.rcut|f2}} with the relay removed
and {{G7.sc25|f2}} with the carrier removed [l187.g74914_rate].

Three limits bound this subsection. Every new arm is one batch, and two of
them sit on a band edge. No relay-matched twin was run, so nothing here
says how often removing an active inhibitory cord interneuron lifts this
readout. And the relay arms remove all of the relay's outputs and its
response to all of its inputs, not the carrier's share alone; a cut of the
single carrier-to-relay edge is not reported here.

### 2.5 Which clock the timing follows is unresolved

If the shared component of §2.3 rides on the chopping gate, then moving the
gate's onsets independently in each run should move the shared timing with
them. Cross-seed antiphase should be recovered when two runs are compared
at gate-aligned times and lost when they are compared at equal elapsed
time. A registered discriminator tested this on the base and on the
carrier-removed graph with {{JP.n_seeds|i}} paired jitter schedules (batch
Q), the on-time, tone, gain and noise held matched [l186.power].

The deletion effect survives re-alignment, and neither clock wins.
Cross-seed duty in the carrier-removed graph is {{JM.sc25.aligned|f3}}
gate-aligned and {{JM.sc25.elapsed|f3}} at equal elapsed time, against
{{JM.cutwA.aligned|f3}} and {{JM.cutwA.elapsed|f3}} on the base; the
same-seed values are {{JM.sc25.same|f3}} and {{JM.cutwA.same|f3}}
[l186.means]. The deletion contrast is {{ci:JC.A}} gate-aligned and
{{ci:JC.T}} by elapsed time, and their difference is {{ci:JC.D}}
(seed-jackknife 95% intervals) [l186.contrasts]. By the registered margin
and uncertainty rule this is the mixed, unresolved branch [l186.branch]. It
is not evidence for two independent rhythms, and it is not evidence against
gate-locking.

We state the status plainly because the run could not have resolved the
question. The registered jitter band ({{JP.jitter_band_steps|i}} steps
wide) is barely larger than the {{JP.window_steps|i}}-step window over
which the statistic is computed, so the gate-aligned and elapsed-time
windows of a pair share {{JP.mean_window_overlap|pc0}}% of their samples
on average. {{JP.frac_pairs_overlap_ge_half|pc0}}% of pair-segments share
half or more, and {{JP.frac_pairs_disjoint|pc0}}% are disjoint
[l186.power]. The alignment contrast is attenuated by construction. A
decisive run needs a jitter of at least
{{JP.needed_jitter_for_disjoint_windows|k}} steps or a readout window
shorter than the jitter, and neither has been run.

One descriptive observation comes out of the same traces. With the carrier
present, the flexor and extensor pools peak about
{{JH.Ti_fR.degrees|deg0}}° and {{JH.Ti_eR.degrees|deg0}}° before the
carrier does at the drive frequency, consistently across seeds (resultant
length {{JH.Ti_fR.R|f2}} and {{JH.Ti_eR.R|f2}}, n = {{JH.Ti_fR.n|i}})
[l186.phase]. These are phase relations between signals that share a
stimulus, not transmission delays. A removed cell is structurally absent,
not silent, so no phase comparison across the deletion is available.

### 2.6 The dose cliff''',
    'brief stage 2: Results reordered around the scan table; three-panel '
    'readouts for the scan arms; relay / push-pull / occlusion; the '
    'gate-jitter status stated plainly; r3 "make the measured contrast the '
    'paper"', wrap=True)

rep('E11-dose-caveat', 2,
    '(§2.14): the unique-seed union over all admissible batches.\n\n',
    '''(§2.14): the unique-seed union over all admissible batches.

The window is a property of the chopped readout. Table 4 re-scores the
ladder in the continuously driven 1.4-Hz segment, with the same statistic
and the same bars, on the same canonical pools.

{{TABLE:ladder}}

Table 4 [l183.ladder_fast, l172.pooled]. Cells are structured seeds of the
pool and mean duty, and the interval is the 95% Wilson interval on the
proportion of structured seeds in the continuous segment. The per-seed rows were derived from the raw traces by
the second-round referee's stored script, and their chopped column
reproduces the canonical pooled count of §2.14 exactly for every arm
shown. The cross-seed panel has not been computed for these pools and is
reported for the scan arms only (Table 1).

In the continuous segment the ladder is no longer a window. The closure,
the base and the two rungs below it score {{LF.full.fast_k|i}},
{{LF.cutwA.fast_k|i}}, {{LF.cutng23.fast_k|i}} and {{LF.cutng19.fast_k|i}}
structured seeds, and carrier removal keeps {{LF.cutng25.fast_k|i}} of
{{LF.cutng25.n|i}}. The largest cut, which the chopped readout reads as
dead ({{LF.cut58.chopped_k|i}} of {{LF.cut58.n|i}}), is the strongest of
the cut arms ({{LF.cut58.fast_k|i}} of {{LF.cut58.n|i}}). The heaviest
carrier-free cohort falls from {{LF.cutscr0.chopped_k|i}} to
{{LF.cutscr0.fast_k|i}} of {{LF.cutscr0.n|i}}. Two things follow. The
non-monotone dose response is specific to the chopped readout, and so is
the carrier-free cohort's entry into the high class. The step at the
carrier is not: carrier removal is the first rung at which the continuous
segment shows any structure, and the mass twin shows none there
({{LF.cutng25p.fast_k|i}} of {{LF.cutng25p.n|i}}).

''',
    'r2 N2: the robustness panel changes the first headline result; the '
    'ladder is re-scored in the continuous segment on its canonical pools '
    '(Table 4, keyed as l183.ladder_fast)', wrap='tail')

rep('E12-twin-heading', 2,
    '### 2.7 Identity, not mass: the twin XOR\n\n',
    '''### 2.7 The mass twin and the carrier-free cohorts: static-mass controls

This subsection reports the two static-mass controls of the cohort lineage.
Both hold removal mass fixed. Neither controls delivered drive, which §2.1
does, and the heading no longer claims that they isolate identity.

''',
    'r2 N1 / r3: the section title credited the silent twin', wrap=False)

rep('E13-twin-paired', 2,
    'indistinguishable from zero, so the earlier "neutral" label was a pooling\n'
    'artefact, not a measured null.\n\n',
    '''indistinguishable from zero, so the earlier "neutral" label was a pooling
artefact, not a measured null.

Two disclosures bound this pair. First, the twin is silent. On the cut base
it fires at a mean rate of {{CE.mass_twin_319.x_mean|f4}} against the
carrier's {{CE.carrier.x_mean|f4}} [l175.census], so the pair fixes static
removal mass while leaving delivered drive unmatched by more than two
orders of magnitude. Second, the pooled p-value above borrows base seeds
the twin never ran on. Paired inference on the twin's own {{PT.n|i}} seeds
is the primary test (§3.7): both arms are structured on {{PT.both_pos|i}}
seeds, neither on {{PT.both_neg|i}}, the twin alone on {{PT.twin_only|i}}
and the base alone on {{PT.base_only|i}}, exact two-sided McNemar p =
{{PT.mcnemar_p|f4}}, with a mean paired duty difference of
{{PT.mean_duty_diff|s3}} [l172.paired_twin]. The twin-versus-base
difference is therefore not resolved on paired seeds, and "intermediate"
should be read as a position of pooled margins, not as a demonstrated
effect of the deletion.

''',
    'brief stage 3 / r2 N6 / r3: paired McNemar is the primary twin '
    'inference; the twin\'s silence disclosed where the pair is reported',
    wrap='tail')

rep('E14-scramble-pools', 2,
    '[l168.scr]; single-batch rows are DISCLOSED as such (cl40 / scrL1 / scrL2\n'
    'were run once).\n\n',
    '''[l168.scr]; single-batch rows are DISCLOSED as such (cl40 / scrL1 / scrL2
were run once).

These rows pool each cohort's own fresh batches. Under the canonical
unique-seed union of §2.14 the heaviest cohort reads {{P.cutscr0.kR|i}} of
{{P.cutscr0.n|i}} [l172.pooled]; the two counts are different pools of the
same arm, and each is labelled wherever it appears.

''',
    'r2 Task 3 / r3: 39/48 (fresh batches) vs 41/50 (canonical) must be '
    'labelled, not interchangeable', wrap='tail')

rep('E15-mass-ratio', 2,
    'any-geometry scattered band: identity beats mass at cell scale.',
    '''extra mass of the one carrier-free cohort that reaches the same class
(§2.7). That is a ratio of two measured masses, not a distance below a
mass-only band: §2.7 shows that no such band exists.''',
    'r2 N4: the "9.72x below any mass-only band" ratio had no referent',
    wrap=False)

# =========================================================== STAGE 3 =======
rep('E16-weights', 3,
    '(tibia flexor 101 / extensor 12). Edge weights are in-degree\n'
    'normalized; inhibitory weights are scaled by β = 2.0 [l173.model].\n'
    'Matrices are built COO → `coalesce()` → `to_sparse_csr()`, and W is\n'
    'indexed as (target, source): rows are targets, columns are sources.\n',
    '''(tibia flexor 101 / extensor 12). Edge weights are not normalized. The
weight of an edge is the natural logarithm of one plus its synapse count,
signed by the presynaptic cell's predicted transmitter, and negative
weights are then multiplied by β = 2.0 [l173.model, l135.weights].
Matrices are built COO → `coalesce()` → `to_sparse_csr()`, and W is
indexed as (target, source): rows are targets, columns are sources.
An earlier draft stated that weights were in-degree normalized. That
sentence described no code that was run and is withdrawn. The scored
right-side tibia pools hold {{RL.pool_sizes.Ti_fR|i}} flexor and {{RL.pool_sizes.Ti_eR|i}} extensor motor neurons
[l187.relay].

**Sign table.** Predicted transmitter sets the sign of a cell's outgoing
weights: acetylcholine +{{W.signs.acetylcholine|x1}}; GABA and histamine
{{W.signs.gaba|sp1}}; dopamine, serotonin and octopamine
+{{W.signs.dopamine|x1}}; tyramine and unpredicted
+{{W.default_sign|x1}}. Glutamate is stored as
+{{W.signs.glutamate|x1}} in the graph file and is forced to its negative
in every run script (the glutamate override), so glutamatergic cells act
as inhibitory and also receive the β scale [l135.weights].

**The simulated network is a deafferented closure.** Three cell sets are
used. The cord set is every cell annotated sensory, intrinsic or motor in
the ventral nerve cord ({{SUB.cord|k}} cells). The baseline network adds
the {{SUB.dn_into|i}} descending neurons that receive cord input
({{SUB.n_old|k}} cells, {{SUB.edges_old|k}} edges). The closure, on which
every removal arm runs, adds the {{SUB.dn_new|i}} descending neurons that
project to the cord without receiving cord input ({{SUB.n_new|k}} cells,
{{SUB.edges_new|k}} edges) [l92.substrate]. Those {{SUB.dn_new|i}} cells
are the source population of the removal cohort (§3.5). No brain neuron is
simulated and ascending neurons are not in the cord set, so every
descending neuron in the model has lost its brain input. Its activity is
set by the other model cells, the background current and noise, not by
anything a brain would send it. Some are consequently silent and some sit
near the rate ceiling: two window cells have mean rates
{{S.sc50.x_mean|x3}} and {{S.sc41.x_mean|f3}} on the base [l175.scan]. The
baseline network is structured in {{P.b65.kR|i}} of {{P.b65.n|i}} seeds
and the closure in {{P.full.kR|i}} of {{P.full.n|i}} [l172.pooled]. Adding
the deafferented projectors is thus what degrades the readout, and the
removal ladder is the removal of ectopically active cells from a network
they degraded. Every result in §2 should be read with that construction in
view.
''',
    'brief stage 3 / r2 N3 / r3 / second opinion item 2: the actual weight '
    'rule, the sign table, the closure substrate', wrap='tail')

rep('E17-rate-bound', 3,
    'Each cell holds a bounded rate xᵢ ∈ (0, RMAX]. One step is\n',
    '''Each cell holds a rate xᵢ that is bounded above by RMAX and has no lower
bound. With W the signed log-count matrix of §3.1 (negative entries already
scaled by β) and g the arm's gain, one step is
''',
    'brief stage 3 / r3: the (0, RMAX] statement contradicted the upper-only '
    'clamp stated two sentences later', wrap=False)

rep('E17b-percell', 3,
    'NOISE, from one generator pair shared across all arms of a run, so arms\n'
    'differ only in their graph and gain.\n',
    '''NOISE, from one generator pair shared across all arms of a run, so arms
differ only in their graph and gain.

Written per cell, the recurrent input to cell i is g·Σⱼ Wᵢⱼ xⱼ, with
Wᵢⱼ = sⱼ·ln(1 + nᵢⱼ) when sⱼ > 0 and Wᵢⱼ = β·sⱼ·ln(1 + nᵢⱼ) when sⱼ < 0.
Here nᵢⱼ is the synapse count from cell j to cell i and sⱼ is the
presynaptic sign of §3.1 after the glutamate override. Only the initial
state is clipped to the unit interval; from the first step on, the upper
clamp alone applies [l135.weights].
''',
    'brief stage 3: the actual equation written per cell (signed '
    'log1p(count), glutamate override, beta on negatives, arm gain, '
    'upper-only clamp)', wrap='tail')

rep('E18-fixed-gain', 3, '### 3.5 Cohort, removal mass and the ladder\n',
    '''**Fixed-gain rule.** Re-bisecting the gain after a deletion keeps the
active fraction matched but moves the gain, by up to a few percent, and the
base readout is itself gain-sensitive: {{R2.slope_meanR_per_0p1pct|f4}}
mean duty per +0.1% gain on the base graph (95% CI
[{{R2.slope_ci95.0|f4}}, {{R2.slope_ci95.1|f4}}]) [l185.r2], with the
opposite sign on carrier-absent graphs (§2.4). From §2.2 onward every
single-cell and compound arm is therefore also run at the base's own gain,
and that fixed-gain form is read first. The arms of the earlier cohort
lineage (§2.6 to §2.14) were run at re-matched gains only, except where a
gain-swap control is reported (§2.12).

### 3.5 Cohort, removal mass and the ladder
''',
    'brief stage 3: the gain-null slope and the fixed-gain rule', wrap=True)

rep('E19-drive-defs', 3, '### 3.6 Readouts: antagonist structure, duty, classes\n',
    '''**Delivered drive and signed current.** The delivered drive of a cell is
its mean rate on the base, averaged over three census seeds, times the
summed absolute effective weight of its outgoing edges. A drive twin is the
candidate that minimises the absolute log ratio of that quantity to the
carrier's (§2.1). The signed current of a cell onto a pool is gain times
mean rate times the summed direct weight plus the gain-scaled one-relay
weight onto that pool, with relays gated to the linear regime. A
signed-current twin minimises the relative distance of the flexor and
extensor pair to the carrier's (§2.2). Both rules were fixed before
selection.

### 3.6 Readouts: antagonist structure, duty, classes
''',
    'brief stage 1/3: the control ladder needs its currencies defined',
    wrap=False)

rep('E20-three-readouts', 3, '### 3.7 Seeds, pooling and statistics\n',
    '''**Three panels of one readout.** Unless stated otherwise, duty is the
registered chopped-segment form above. The continuous panel applies the
same statistic and the same bars to the continuously driven 1.4-Hz middle
segment after its initial transient is dropped. The cross-seed panel pairs
the flexor trace of seed i with the extensor trace of seed j ≠ i of the
same arm at identical times, over all ordered pairs. The last two are
descriptive panels, never a replacement for the registered readout
(§2.13).

### 3.7 Seeds, pooling and statistics
''',
    'brief stage 2: the three-panel readout needs a Methods definition',
    wrap=False)

rep('E21-paired', 3, '### 3.8 Preregistration, anchors and certification\n',
    '''Four further batches carry the single-cell experiments of §2.1 to §2.5 and
continue the same labelling scheme: M = B39 (the scan), N = B40 (the
replication, the gain-only null and the signed-current twin), P = B41 (the
relay arms) and Q, the gate-jitter batch, which has no internal run code
and is identified by its seeds (18601 to 18616).

**Paired inference.** Where two arms ran on the same seeds and the claim
is about one of them against the other, the primary test is paired: the
exact two-sided McNemar test on the discordant seeds, with the paired mean
difference alongside. Pooled-margin tests (Fisher, Newcombe) that draw on
seeds only one arm ran on are reported as pooled statements and are not
used to claim an effect of a deletion. For the mass twin this gives p =
{{PT.mcnemar_p|f4}} on {{PT.n|i}} paired seeds, against the pooled
{{l172.diffs.twin_vs_base.fisher_p|f3}} (§2.7) [l172.paired_twin, l172.diffs]. Contrasts between arms of one 16-seed batch are
reported as mean differences with 95% intervals over seeds, and are read as
differences of batch means (§2.2).

### 3.8 Preregistration, anchors and certification
''',
    'brief stage 3: paired McNemar as primary twin inference; the batch '
    'mapping extended in run order (O skipped)', wrap=True)

rep('E22-prereg-scope', 3, '### 3.9 Notation and constants\n',
    '''**What preregistered means here.** Each registration is a file whose
hash is recorded in the result it governs; for the runs of §2.1, §2.2 and
§2.4 the recorded hash prefixes are {{ME.prereg_sha256|raw}},
{{M5.prereg_sha256|raw}} and {{M7.prereg_sha256|raw}} [l175.meta,
l185.meta, l187.meta]. Hash agreement shows that a plan was not edited after its run recorded it. It is not an externally dated registration, and
several stages labelled preregistered in §2.6 to §2.14 are re-analyses of
stored data whose plans were written before the re-analysis, not before the
data. Public, dated registration is an open item.

### 3.9 Notation and constants
''',
    'r2 smaller points / r3 change 3: distinguish hash agreement from '
    'independently dated registration', wrap=True)

# =========================================================== STAGE 4 =======
rep('E03-intro-lead', 4,
    '## 1. Introduction\n\nWe report four load-bearing results, and state them up front:\n',
    '''## 1. Introduction

Which cells matter in a connectome-constrained model is a question that a
perturbation can answer only against a stated comparison. This paper
reports one such comparison in full. On a rate model of the female nerve
cord from which 24 heavy descending neurons have already been removed, we
delete each of the next {{NL.n_window|i}} descending neurons in the
removal-mass ranking, one at a time, and score right-tibia
flexor-extensor antiphase duty. One deletion, that of the left DNp33 cell
(hereafter the carrier), lifts the readout into the registered super class,
{{kn:S.sc25}} seeds against {{kn:S.cutwA}} for the base. No other window
cell does (§2.1).

Four checks say what that contrast is not. It is not
removal mass: the rank-adjacent mass twin does not flip, although that twin
is silent on this base and therefore controls static weight only. It is not
delivered drive: two cells matched to the carrier on mean rate times
outgoing weight do not flip, one of them of the carrier's class and sign.
It is not signed current onto the right tibia within two synapses: a cell
matched on that quantity does not flip either. And it is not the gain
re-match: the contrast holds on a second seed batch at the base's own gain,
while a gain-only sweep of the base moves its duty with no deletion (§2.2).
What the deletion changes is the shared timing of the two motor pools, not
their rates (§2.3).

We do not claim uniqueness, mechanism or biology. One carrier-free cohort
and one downstream interneuron reach the same class on the same readout.
The route through that interneuron is neither necessary nor sufficient for
the carrier's signature (§2.4). Which clock the timing follows is
unresolved (§2.5). And every statement is about one perturbed model graph.

The cohort-level lineage that located this cell came first. It rests on
four load-bearing results, restated with their present scope:
''',
    'brief stage 4 / r2 "§1\'s first paragraph is unreadable cold": the '
    'measured contrast and its control ladder lead the Introduction',
    wrap=True)

rep('E04-intro-twin-scope', 4,
    '[l172.pooled, l172.diffs]). That carrier is\n'
    'sufficient, not unique, and set-dependently so: of seven carrier-free cohorts\n'
    'mass-matched to the same window, one reaches super (39/48 [l168.scr]) and six\n',
    '''[l172.pooled, l172.diffs]). The twin
is silent on the cut base, so that pair fixes static mass and nothing else,
and on the twin's own {{PT.n|i}} seeds the twin-versus-base difference is not
resolved (exact McNemar p = {{PT.mcnemar_p|f4}} [l172.paired_twin]). The scan
of §2.1 is the comparison the identity statement now rests on. That carrier is
sufficient, not unique, and set-dependently so: of seven carrier-free cohorts
mass-matched to the same window, one reaches super (39/48 on its own fresh
batches [l168.scr]; {{P.cutscr0.kR|i}} of {{P.cutscr0.n|i}} on the canonical pool [l172.pooled]) and six
''',
    'r2 N1 + N6: result (2) of the section-1 map must carry the twin\'s '
    'silence and the paired test; r2 Task 3: the per-batch 39/48 is labelled '
    'beside the canonical 41/50', wrap=False)

rep('E05-intro-lineages', 4,
    'Walking-CPG field context (Sapkal et al. [34]) supplies three findings that\n',
    '''Three older lineages bear directly on what is and is not new here. The first
is identified-cell ablation. The touch circuit of Caenorhabditis elegans was
established by combining serial reconstruction with laser killing of cell
precursors [38]. Connectome-informed models have since been fitted to
single-class ablation phenotypes in its locomotor circuit [39]. And ablation
with optogenetics has shown that rhythm generation for forward locomotion is
distributed, not owned by one cell [40], a standing caution against reading a
single-cell effect as a single-cell oscillator. The second lineage is lesion
location in network models. Lesions of equal size, 50 nodes each, placed at
different sites of a human structural connectome have markedly different
effects on simulated dynamics [41], so location-dependence at matched lesion
size is established prior art. Equal node count is not equal removed synaptic
weight or equal delivered drive, which is the distinction our control ladder
draws, but we do not claim the size-matched design as ours. The third lineage
is the clinical lesion literature, in which infarct location carries outcome
information after adjustment for volume [42], while for mortality the
association with location is greatly reduced once volume is controlled [43]. Neither location nor
size wins in general, and adjustment is not the same as matching.

Walking-CPG field context (Sapkal et al. [34]) supplies three findings that
''',
    'brief stage 4: Alstott (equal-SIZE lesions, precise wording), the C. '
    'elegans ablation lineage, the stroke lesion literature', wrap=False)

rep('E06-intro-drivers', 4, '[15, 16, 17]. In-model,\n',
    '''[15, 16, 17, 45]. An updated catalogue of split-GAL4 driver lines for
descending neurons [44] is the practical starting point for genetic access to
individual types. In-model,
''',
    'r2 "state whether a driver line exists": the verified catalogue is '
    'cited; a later paper by the first author of entry 15 added as entry 45', wrap=False)

rep('E07-intro-currency', 4,
    'First, matching currency: their controls are\n'
    'matched on cell count and ours on removal mass. Count-matching is the weaker\n'
    'control, because 37 cells drawn from a spatial mask carry only a\n'
    "fraction of 37 descending neurons' out-mass, and our carrier sits\n"
    '9.72× below any mass-only band (§2.7). Second, resolution:\n',
    '''First, matching currency: their controls are
matched on cell count and ours on removal mass, and then on delivered drive,
class and sign, and signed current (§2.1, §2.2). No single currency suffices:
a count match leaves removed weight free and a mass match leaves delivered
drive free, as our own silent mass twin shows. Second, resolution:
''',
    'r2 "is the mass-vs-count distinction crisp? not yet": the asserted '
    'out-mass claim about their data and the referent-less 9.72x are '
    'withdrawn from this paragraph', wrap=False)

rep('E07b-intro-unit', 4, 'while ours is one cell against one mass twin.',
    'while ours is one cell against single-cell comparators.',
    'the comparison is no longer one mass twin', wrap=False)

span('E08-intro-gap', 4,
     'The gap this paper fills, stated after both narrowings above:',
     '## 2. Results\n',
     '''(e) The closest neighbour on the motor side is the connectome simulation of
fly walking [4]. Rate simulations of the ventral nerve cord, a
descending-activation screen and pruning identify a three-interneuron
rhythm-generating circuit across four connectome datasets, and silencing
either of two of its interneurons individually in the full simulation
abolishes leg motor rhythms. A single identified interneuron being necessary
for a motor rhythm in a connectome-scale rate simulation is therefore prior
art too. The two studies are complementary and not competing. Theirs asks what
generates the rhythm, with descending neurons as inputs under the
experimenter's control. Ours asks what gates the timing of a readout in a
network whose descending neurons run free and deafferented (§3.1). We make no
claim about rhythm generation.

The gap this paper fills, stated after the narrowings above, is a conjunction
and not any one of its parts. That identity matters is prior art [6, 36]. That
lesion location matters at matched size is prior art [41]. That one identified
interneuron can be necessary for a motor rhythm in a connectome-scale rate
model is prior art [4]. What we did not find in the literature is the
particular matched comparison reported here: one identified cell in an
uncurated bulk-extracted subnet, a shared-timing readout in a motor-pool pair,
and a ladder of comparators defined in advance on removal mass, delivered
drive, class and sign, and signed current, replicated on a second batch at
fixed and re-matched gain. Absence from our sweeps is not evidence of
priority. The contribution is the comparison and its result, not the invention
of size-controlled lesions, single-cell ablation scans or location-dependence.

''',
     'brief stage 4: Pugliese as the complementary closest neighbour; the '
     'novelty claim scoped to the conjunction', wrap=False)

rep('E25-refs-preamble', 4, ' No citation is written from memory. BibTeX\n',
    '''
Entries 38-45 were added on 2026-11-21 from the third-family prior-art dig
(paper/priorart_terra_20261121.md), each of whose items had its abstract or
author summary fetched and read; only the fields that file records are used
(first author, year, title, venue, identifier), so author lists are held at
the first author until the primary records are pulled programmatically.
No citation is written from memory. BibTeX
''',
    'brief stage 6: references extended from the verified prior-art list '
    'only', wrap=False)

rep('E25b-refs-entries', 4, '\n## Verification (this skeleton)\n',
    '''38. Chalfie et al. The neural circuit for touch sensitivity in Caenorhabditis
    elegans. Journal of Neuroscience (1985).
    doi:10.1523/JNEUROSCI.05-04-00956.1985
39. Rakowski et al. Synaptic polarity of the interneuron circuit controlling
    C. elegans locomotion. Frontiers in Computational Neuroscience (2013).
    doi:10.3389/fncom.2013.00128
40. Fouad et al. Distributed rhythm generators underlie Caenorhabditis elegans
    forward locomotion. eLife (2018). doi:10.7554/eLife.29913
41. Alstott et al. Modeling the Impact of Lesions in the Human Brain. PLOS
    Computational Biology (2009). doi:10.1371/journal.pcbi.1000408
42. Rangaraju et al. The role of acute lesion topography in initial ischemic
    stroke severity and long-term functional outcomes. Stroke (2015).
    doi:10.1161/STROKEAHA.115.009643
43. Laredo et al. Prognostic Significance of Infarct Size and Location: The
    Case of Insular Stroke. Scientific Reports (2018).
    doi:10.1038/s41598-018-27883-3
44. Zung et al. An updated catalogue of split-GAL4 driver lines for descending
    neurons in Drosophila melanogaster. bioRxiv (2025).
    doi:10.1101/2025.02.22.639679
45. Stürner et al. Comparative connectomics of Drosophila descending and
    ascending neurons. Nature (2025). doi:10.1038/s41586-025-08925-z (see also
    entry 15, a preprint by the same first author on the same subject).

## Verification (this skeleton)
''',
    'brief stage 6: entries 38-45, fields copied from the verified list',
    wrap=False)

# =========================================================== STAGE 5 =======
rep('E23-limits', 5, 'Wet-lab predictions are not derived here.\n',
    '''Single-batch classes: the scan's class labels for the non-carrier arms
rest on one batch of {{ME.n_seeds|i}} seeds each. The silent-cell null is
wide enough ({{NL.silent_kR_min|i}} to {{NL.silent_kR_max|i}} structured
seeds of {{ME.n_seeds|i}}) that an individual label can move on a second
batch, as the rank-27 cell's did (§2.2). The carrier, the mass twin, both
drive twins, the two edge-of-band cells and the base are the only
single-cell arms with a second batch; the relay, push-pull and occlusion
arms and the signed-current twin have one. Statements about those arms are
statements about a batch mean.

No relay-matched twin: the downstream interneuron of §2.4 reaches the super
band on the chopped readout when removed, and nothing here says how often
removing an active inhibitory cord interneuron does the same. The identity
statement is scoped to descending window cells and their twins, and the
chopped classifier alone is not specific to the carrier. A cut of the
single carrier-to-relay edge is not reported here.

One readout family: every result is a statistic of one antagonist pair on
one side, right-tibia flexor against extensor pool means
({{RL.pool_sizes.Ti_fR|i}} and {{RL.pool_sizes.Ti_eR|i}} motor neurons),
in pools that sit near the background rate. The three panels (chopped,
continuous, cross-seed) are three views of that one statistic, not three
readouts. The chopped panel changes frequency, envelope and position in
the trial together, so a difference between panels is not an experiment
that isolates chopping. Re-scored in the continuous segment, the cohort
ladder's large-cut endpoint reverses and the heaviest carrier-free cohort no
longer reaches the class (§2.6, Table 4). The cross-seed panel exists for
the scan arms only.

Model class and construction: the network is a rate model with signed
log-count weights, a sign table with a glutamate override, and descending
neurons that have lost all brain input (§3.1). The carrier effect is
defined on a base from which 24 other descending neurons have already been
removed, and on the intact closure silencing the same cell has no
demonstrated effect (§2.9). The effect is carried by the left cell of the pair. The
contralateral DNp33 cell receives cord input, so the extraction rule never
admits it to the cohort, and deleting it does not flip the readout
(§2.12). A left-right difference
within one bilateral pair in one specimen is more economically explained
by reconstruction or individual variation than by cell-type function.

Network-level fragility: the intervals in this paper measure how
reproducibly one deterministic graph behaves under different noise. They do
not say whether a slightly different graph behaves the same way, and our
own controls say it need not. The transition interior re-draws across the
weight-jitter sets (§2.10), the effect is absent on the floor-4 substrate
(above), and a degree-preserving rewire of the carrier's edges flips in one
draw of three (§2.12).

Timing attribution: which clock the shared timing follows is unresolved
(§2.5), and the run that would resolve it has not been done.

Registration: hash agreement between a registration file and its result is
an integrity check, not an external timestamp (§3.8).

A wet-lab prediction is stated in §5, with the conditions under which the
model does and does not license it.
''',
    'brief stage 5: single-batch classes, no relay-matched twin, one readout '
    'family, model class; r2 N3/N5/N7 and the mirror-symmetry point',
    wrap=True)

span('E24-discussion', 5, '## 5. Discussion\n', '## 6. Data & code\n',
     '''## 5. Discussion

A connectome-constrained model is usually asked whether wiring matters. We
asked it which cell matters, against comparators fixed in advance. On a
nerve-cord rate model from which a cohort of heavy descending neurons had
already been removed, deleting one further cell at a time moves a tibia
antiphase readout into its registered high class for exactly one of the
cells tried ({{kn:S.sc25}} seeds against {{kn:S.cutwA}} for the base).
That cell is the left member of one descending type (§2.1).

What makes the contrast worth reporting is what it survives. A comparator
matched on removal mass does not flip, but it is silent on this base and so
controls static weight only; we state that and do not build on it.
Comparators matched on delivered drive do not flip, including one of the
carrier's own class and sign, and neither does a comparator matched on
signed current onto the scored pools. The contrast replicates on a second
batch ({{kn:R1.sc25.pooled_b39_b40_rematched}} pooled) and holds when the
gain is not re-matched ({{kn:R1.sc25.fixed}}), which matters because a
small gain change moves the base readout by itself (§2.2). Each of these is
a specific comparison with a stated tolerance, and none of them isolates
identity from every possible description of what a cell delivers.

The readout rises because the two motor pools share more of their timing,
not because either fires more. Most of the effect survives pairing traces
from different runs ({{TP.sc25.cross_k|i}} of {{DS.n_cross_pairs|i}}
pairs), and in the continuously driven segment the carrier-removed network
is the one arm of the scan that keeps the structure in half its seeds
(§2.3). That is why we describe the readout as antiphase duty and not as
endogenous motor organisation: a network that is merely more reproducibly
locked to a shared stimulus passes the same test. Whether the shared timing
follows the stimulus gate or elapsed time is unresolved, and the experiment
that left it unresolved could not have resolved it (§2.5).

The carrier is a sufficient route into the high class and not the only one.
One of seven carrier-free cohorts matched on removal mass reaches it,
raising both sides where the carrier's signature is crossed (§2.7). One
interneuron downstream of the carrier reaches it alone on the chopped
readout ({{kn:A.rcut}}), without the carrier's signature in the continuous
segment (§2.4). That interneuron is neither the carrier's necessary conduit
nor inert, and the carrier's effect survives its removal. We therefore
claim neither uniqueness nor a mechanism. The cohort-level results that
located the cell stand as measured on the chopped readout, with the scope
that §2.6 to §2.14 give them: the non-monotone window, the edge-set
decomposition and the substrate-gated clamp.

Single-cell necessity in a connectome-constrained model, identity beating
cell number in a fly connectome model, location-dependence of equal-sized
lesions in a connectome model, and a single interneuron necessary for a
motor rhythm in a connectome-scale rate simulation are all established
prior art (§1). Our contribution is the conjunction: one identified cell in
an uncurated subnet, a shared-timing readout, and a ladder of comparators
on mass, drive, class and sign, and signed current, replicated at fixed
gain. The nearest motor-side study asks what generates a walking rhythm
with descending neurons as controlled inputs. Ours asks what gates the
timing of a readout in a network whose descending neurons run free. The two
are complementary.

The robustness picture is deliberately split and not summarised in one
word. Seed-level certainty here is high and network-level certainty is not.
The endpoints of the cohort transition hold across a small weight-jitter
ensemble while its interior re-draws (§2.10). The effect is absent at a
stricter synapse floor (§4). A rewire of the carrier's own edges flips in
one draw of three (§2.12). And the male connectome is untested at a matched
floor, not shown to lack the ladder (§2.11). A result measured on an
extracted subnet is scoped to the extraction rule that produced it. Our
answer to that instability is not immunity but that the arms, bands and
branches were written down before the numbers existed, and that the
failures are reported with the successes (§3.8).

One claim in this lineage was withdrawn by its own controls, and we keep it
in view and do not delete it (§2.13). A sub-band spectral line we had read
as a property of the substrate sits where the drive envelope's own spectrum
peaks, so the line's position is stimulus-set and needs no endogenous
antagonist clock. The transferable rule is that a frequency claim in a
driven model stays band-relative until the drive's own spectrum has been
computed on the same window, and we hold our own earlier reading to it.

None of this is a statement about the animal, but it does yield a
prediction that an experiment could refute, and we state it with its
conditions. The manipulation is acute unilateral silencing of the left
DNp33 neuron, with the right one as the within-animal control. The assay is
the step-phase relation between tibia flexor and extensor activity on each
side, read from femur-tibia joint kinematics in a tethered walking fly or
from calcium imaging of the tibia motor neurons in the cord. The predicted sign is a strengthening of
flexor-extensor antiphase on the right side, contralateral to the silenced
cell, with little change in mean motor-pool activity. No strengthening is
predicted on the left, where the model shows only a small weakening of a
structure that is already nearly absent (§2.14). The
predicted scope is narrow. In the model the effect appears only after other
descending input has been removed, and on the intact network silencing the
same cell has no demonstrated effect (§2.9). The intact-animal prediction
is therefore a null, and the sign-specific prediction applies to a
preparation in which descending drive is broadly reduced; we do not specify
how to build one. Three outcomes would count against the model's account:
an antiphase change of the opposite sign, a change of equal size on both
sides, or the same change from silencing the right cell. We know of no
functional study of this cell type and have verified no driver line
specific to it, so the feasibility of the experiment is itself an open
question.

''',
     'brief stage 5: the wet-lab prediction as a testable spec; r2 N4 (the '
     'Discussion asserted a male non-transfer the body had retracted, and a '
     'mass-twin licence the scan replaces)', wrap=True)

rep('E26-verification', 5,
    '- Fig 1 candidate: peabrain-figs/l136_transition_law.png (values asserted\n'
    '  against sources by l136_fig.py at draw time).',
    '''- Fig 1 candidate: peabrain-figs/l136_transition_law.png (values asserted
  against sources by l136_fig.py at draw time).
- Master-fold replay: `python3 paper/l183_verify.py` rebuilds this draft from
  the stored pre-image and the declared edit ledger (paper/l183_text.py) and
  requires byte equality from the title onward; every number in the folded
  text is a placeholder resolved from numbers.json.''',
    'the fold is replayable; say so where verification is described',
    wrap=False)


# =========================================================== STAGE 7 =======
# L190b follow-up fold (owner-directed, brief banc/l190b_BRIEF_fold.md): the
# single-edge cut banc/l190 landed while the master fold ran and stage 6 left
# it out.  Every `old` below is text an EARLIER stage rendered (whole
# paragraphs, so the 78-column wrap stays deterministic); every new number is
# a placeholder on the l190.* keys that entered numbers.json first.
rep('E30-edge-cut', 7,
    '''Three limits bound this subsection. Every new arm is one batch, and two of
them sit on a band edge. No relay-matched twin was run, so nothing here says
how often removing an active inhibitory cord interneuron lifts this readout.
And the relay arms remove all of the relay's outputs and its response to all
of its inputs, not the carrier's share alone; a cut of the single
carrier-to-relay edge is not reported here.''',
    '''The relay arms remove all of the relay's outputs and its response to all of
its inputs, not the carrier's share alone. A further fresh batch (batch R,
{{EM.n_seeds|i}} seeds) therefore cut only the carrier's edge onto the relay,
an excitatory edge of {{ES.E-edge.syn|i}} synapses, and left both cells and
every other edge in place. Its control is a sham cut of a count-matched edge
onto the same relay: {{ES.E-sham.syn|i}} synapses from another excitatory
descending neuron outside the scan window, the only candidate the registered
selection rule admitted. Both edited graphs were re-bisected, and the base
and the carrier-removed graph were re-run on the same seeds.

{{TABLE:edge}}

Table 3b [l190.arms, l190.summary, l190.selection, l190.gain]. The four arms
share their seeds, and each runs at its own re-matched gain. The contrast
column is the paired mean difference in chopped duty from the base with its
95% interval over seeds, and the 1.4-Hz column is the continuous segment of
Table 3.

**Cutting the one edge raises the chopped duty and leaves the 1.4-Hz panel
at zero.** The edge cut gives {{kn:EA.edge}} structured seeds at mean
{{EA.edge.meanR|f3}}, {{ci:EA.edge.vs_base}} above the base. That meets the
registered super band at its count floor of {{BD.super_kR_min|i}} seeds. The
point ratio to the carrier's shift on the same seeds
({{EA.carrier.vs_base.mean|s3}}) is {{EM.edge_share_of_carrier|pc0}}%, and
that ratio has no interval. The edge cut's 1.4-Hz duty is
{{EA.edge.meanmid|f3}} against {{EA.carrier.meanmid|f3}} for carrier
removal, so by the registered rule it reproduces carrier removal in part and
is not a copy of it. The sham reads {{kn:EA.sham}} at {{EA.sham.meanR|f3}},
{{ci:EA.sham.vs_base}} from the base. That is base-like by the registered
rule, which describes the point estimate and is not a test of equivalence
[l190.arms, l190.meta].

**The two readouts dissociate in both directions.** Removing the relay, or
only the edge that links the carrier to it, raises the chopped duty and
leaves the 1.4-Hz panel at the base's level. Removing the carrier with the
relay already gone adds the whole 1.4-Hz signature and a smaller chopped
increment, which is resolved at re-matched gains and not at the base's gain.
Read together this is a double dissociation in a limited sense. The chopped
component is reproduced in substantial part by cutting one bottleneck edge,
about {{EM.edge_share_of_carrier|pc0}}% of the carrier's shift by point
ratio. The 1.4-Hz signature appears only when the whole carrier is removed:
no graph that keeps the carrier shows it in either batch, the edge cut
included. The statement compares two readouts across two batches, and it
does not show that the edge is a necessary route.

Four limits bound this subsection. Every new arm is one batch, and three of
them sit on a band edge. No relay-matched twin was run, so nothing here says
how often removing an active inhibitory cord interneuron lifts this readout.
The edge and sham arms exist only at re-bisected gains,
{{EA.edge.gain_delta_pct|sp3}}% for the edge cut and
{{EA.sham.gain_delta_pct|sp3}}% for the sham. On the base a lower gain
raises the duty by itself ({{R2.slope_meanR_per_0p1pct|s4}} per +0.1%,
§2.2), so without a fixed-gain form the deletion is not separated from its
gain adjustment. And the sham is the one eligible edge, so it shows that
this edge differs from that one, not from large edges onto the relay in
general.''',
    'fold the single-edge cut + count-matched sham into 2.4 (Table 3b), state '
    'the double dissociation with its limits, remove the "is not reported '
    'here" marker; "two of them sit on a band edge" becomes three (the edge '
    'cut sits on the count floor), checked in l183_verify (5)',
    wrap=True)

rep('E31-batch-label', 7,
    '''Four further batches carry the single-cell experiments of §2.1 to §2.5 and
continue the same labelling scheme: M = B39 (the scan), N = B40 (the
replication, the gain-only null and the signed-current twin), P = B41 (the
relay arms) and Q, the gate-jitter batch, which has no internal run code and
is identified by its seeds (18601 to 18616).''',
    '''Five further batches carry the single-cell experiments of §2.1 to §2.5 and
continue the same labelling scheme: M = B39 (the scan), N = B40 (the
replication, the gain-only null and the signed-current twin), P = B41 (the
relay arms), Q, the gate-jitter batch, and R, the single-edge batch of §2.4.
Neither Q nor R has an internal run code: Q is identified by its seeds
(18601 to 18616) and R by its own ({{EM.seed_lo|i}} to {{EM.seed_hi|i}}).''',
    'the single-edge batch gets the next label in the declared scheme (R) '
    'and, like Q, is identified by its seed range (it has no internal run '
    'code); "Four further batches" becomes five',
    wrap=True)

rep('E32-limits-single-batch', 7,
    '''Single-batch classes: the scan's class labels for the non-carrier arms rest on
one batch of 16 seeds each. The silent-cell null is wide enough (2 to 11
structured seeds of 16) that an individual label can move on a second batch,
as the rank-27 cell's did (§2.2). The carrier, the mass twin, both drive
twins, the two edge-of-band cells and the base are the only single-cell arms
with a second batch; the relay, push-pull and occlusion arms and the
signed-current twin have one. Statements about those arms are statements about
a batch mean.''',
    '''Single-batch classes: the scan's class labels for the non-carrier arms rest on one batch of 16 seeds each. The silent-cell null is wide enough (2 to 11 structured seeds of 16) that an individual label can move on a second batch, as the rank-27 cell's did (§2.2). The carrier, the mass twin, both drive twins, the two edge-of-band cells and the base are the only single-cell arms with a second batch; the relay, push-pull and occlusion arms, the single-edge cut and its sham, and the signed-current twin have one. Statements about those arms are statements about a batch mean.''',
    'the single-edge cut and its sham are single-batch arms; the list of '
    'such arms in section 4 must name them',
    wrap=True)

rep('E33-limits-edge', 7,
    '''No relay-matched twin: the downstream interneuron of §2.4 reaches the super
band on the chopped readout when removed, and nothing here says how often
removing an active inhibitory cord interneuron does the same. The identity
statement is scoped to descending window cells and their twins, and the
chopped classifier alone is not specific to the carrier. A cut of the single
carrier-to-relay edge is not reported here.''',
    '''No relay-matched twin: the downstream interneuron of §2.4 reaches the super band on the chopped readout when removed, and nothing here says how often removing an active inhibitory cord interneuron does the same. The identity statement is scoped to descending window cells and their twins, and the chopped classifier alone is not specific to the carrier. The cut of the single
carrier-to-relay edge (§2.4) has a count-matched sham, but it is one batch at
re-bisected gains with one eligible sham edge and no fixed-gain form. It does
not separate the deletion from its gain adjustment, and it does not show that
the edge is a necessary route.''',
    'section 4 said the single-edge cut "is not reported here"; it is now '
    'reported, so the sentence states what that arm does not establish',
    wrap=True)


# ------------------------------------------------------------------ banner
# Appended to the changelog banner (the banner is outside the replayed body;
# l183_verify requires the old banner as an exact prefix and this entry after
# it).  STAGE_NOTES[n] is appended when stage n lands.
BANNER_HEAD = '''>
> v3.32 = L183 master fold (owner-directed; the scientist-ready draft). The
> body from the title onward is now a REPLAY: the stored pre-image
> banc/l174b4iiic/draft_post_preview.md, a declared bijective renumber of the
> Results subsections (old 2.1-2.9 -> 2.6-2.14; the single-cell scan and its
> controls take 2.1-2.5) and the declared edit ledger paper/l183_text.py, in
> which every number is a placeholder resolved from numbers.json.
> paper/l183_verify.py requires byte equality with this file, so nothing
> outside a declared edit moved and no new number is hand-typed. The fold
> answers three referee rounds from two model families plus an independent
> rebuild, and a verified prior-art dig.
'''
STAGE_NOTES = {
    1: '''> Stage 1 (title + abstract): the third-round referee's title is adopted
> ("Removing DNp33-L selectively raises right-tibia antagonist duty in a
> perturbed fly connectome model"); the abstract now carries the control
> ladder (mass, delivered drive, class and sign, signed current), two
> batches, the fixed-gain form and the gain-only null, the cross-seed and
> 1.4-Hz panels and the scope statements, and drops "all-or-none", "kill to
> super", the mass-only band, the male-ladder sentence and the pooled p-value.
''',
    2: '''> Stage 2 (Results): reordered around the scan table. New 2.1 (the 34-cell
> scan + two drive twins, three readouts per arm), 2.2 (replication at fixed
> and re-matched gain, the gain-only null, the signed-current twin), 2.3
> (shared timing, not rate), 2.4 (relay, push-pull, occlusion: neither
> registered pole) and 2.5 (the gate-jitter discriminator: UNRESOLVED, and
> underpowered by construction). The mass twin's silence and the paired
> McNemar test are disclosed where the pair is reported, and Table 4
> re-scores the cohort ladder in the continuous segment on its canonical
> pools: the non-monotone window is specific to the chopped readout.
''',
    3: '''> Stage 3 (Methods): the weight rule actually run (signed log1p synapse
> count, glutamate override, beta on negatives; the "in-degree normalized"
> sentence is WITHDRAWN), the sign table, the deafferented closure substrate,
> the (0, RMAX] contradiction fixed, the fixed-gain rule with the gain-null
> slope, the three readout panels, paired inference as the primary twin
> test, four new batch labels (M, N, P, Q) and what "preregistered" means.
''',
    4: '''> Stage 4 (Introduction / related work): the measured contrast and its
> control ladder lead the section; equal-SIZE lesion location (entry 41), the
> C. elegans ablation lineage (38-40), the stroke lesion literature (42-43)
> and the walking-CPG simulation as the complementary closest neighbour
> (entry 4) are cited, and the novelty statement is scoped to the
> conjunction. Entries 38-45 enter the reference list here, with the
> paragraphs that cite them, because the bidirectional citation gate forbids
> either half alone.
''',
    5: '''> Stage 5 (Limitations + Discussion): single-batch classes, no
> relay-matched twin, one readout family, model class and construction,
> network-level fragility, unresolved timing attribution; the Discussion is
> rewritten around the scan and ends in a wet-lab prediction stated as a
> testable spec (manipulation, assay, predicted sign, predicted null,
> refutation), with the intact-animal prediction stated as a null.
''',
    6: '''> Stage 6 (references): entries 38-45 audited against the verified
> prior-art list by a new l174_verify section (title, venue, year and DOI
> parsed from that list, never typed); references.bib extended from it only,
> with author lists held at the first author because the list records no
> more. NOT in this fold: the single-edge cut that landed while it ran, the
> cross-seed panel for the cohort pools, new figures, and the deferred
> all-caps pass over the old Results and Methods text.
''',
    7: '''> Stage 7 (follow-up fold, owner-directed, same day): the single-edge cut
> that stage 6 lists as not folded is now in 2.4 as Table 3b (base, carrier
> removed, carrier-to-relay edge cut, count-matched sham; one fresh batch,
> R), with the double-dissociation reading stated in its limited sense and
> its limits (one batch, re-bisected gains only, one eligible sham edge).
> 3.7 gains the batch label, and section 4 names the two new single-batch
> arms and drops its "is not reported here" marker. Six l190.* keys entered
> numbers.json first.
''',
}
