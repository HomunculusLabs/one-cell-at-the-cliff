
## 2026-11-23 — tick 260 (research: hour-21 scan; 23 arXiv angles — 1 control + 5 core + 17 ROTATED onto the GATED-LINEARISATION / effective-connectivity literature that L260 needs. arXiv fly field QUIET: all four in-window fly-named hits already digested. The yield is entirely OFF arXiv and it is the largest prior-art correction this lane has taken: L260's instrument, the whole depth-k family's identity, AND L228's own headline all have established names — and L260's gate as written is provably WRONG for our own nonlinearity.)

- Pipeline validated BEFORE any zero was scored: control `cat:q-bio.NC` parsed
  14 / in-window 14; **23 angles, 0 errored** at 6.5 s spacing (the tick-243
  rate-limit law). Angle builder `lane/t260/angles.py` runs every term through
  `urllib.parse.quote` — no raw quote is ever concatenated into the URL (arxiv
  skill law). Raw output `lane/t260/scan.out`.
- ALREADY DIGESTED (grepped before reading, per protocol): 2611.23320 (t167),
  2611.14508 (t37), 2611.14498 (t136). `all:FlyWire` 12 parsed / 0 in-window;
  `all:NeuroMechFly` and `all:flyGNN` parsed 0. arXiv's fly field produced
  nothing new in the 14-day window.
- ROTATION ZEROS AS A POINTER (tick-233 law, third time): rot-perron,
  rot-walklen, rot-gain, rot-balnet and rot-silence returned 0–2 parsed with 0
  in-window. These are not quiet fields — the gated-linearisation literature is
  journal-hosted and 25+ years old, which is exactly where the tick went next.

**READ 1 — the LINEAR-RESPONSE identity. "Exact linear theory of perturbation
response in a space- and feature-dependent cortical circuit model" (bioRxiv
2024.12.27.630558 / PMC12330895), read full-text at the derivation + discussion
sections; plus the gain-renormalisation supplement bioRxiv 2026.09.15.751810
DC1 read at its own equations.** | What they state, and it is a definition not a
result: *"the linearized dynamics of a nonlinear network around a fixed point is
driven by an effective connectivity matrix W equal to the product of the
connectivity J and a diagonal matrix of (positive) neuronal gains"*, and the
supplement makes the orientation explicit — *"gain renormalization acts ROW-WISE
on incoming synaptic weights: all inputs to the same postsynaptic neuron are
multiplied by the same local response gain"*, W*_ij ≡ f*_i W_ij with
f*_i = ∂f(h*_i) the local gain at the operating point. | The number that
matters: the perturbation response is **r = (I − W*)^{-1} h**, and *"the most
common approach is to compute the perturbative expansion of the linear response
operator in the form of a Neumann series (I − W)^{-1} = Σ_{n=0}^∞ W^n"* — their
own truncation for comparison is at **3rd order**, with the exact inverse being
the paper's contribution. | **What it changes for peabrain — three things, all
of them corrections to cards already written.** (1) **The instrument L260 was
about to build has a name: the EFFECTIVE CONNECTIVITY matrix.** `D·W` with D
diagonal on the POSTSYNAPTIC index is standard, decades old, prior art — cite,
never claim (the tick-252 rule). (2) **The whole depth-k family (L206, L209,
L210, L215, L216, L218, L228, L261) is the truncated Neumann series of the
linear response operator.** The lane has been computing partial sums of
Σ_n W^n and calling them depth-1, depth-2, depth-d terms without naming the
series or its convergence condition. (3) **And that identity ANSWERS L228's
open question quantitatively.** A Neumann truncation converges at rate ρ(W*)^n;
L228 measured a depth-2 term that moves **8%** against dynamic folds of
**1.76x–110.74x** and concluded "the fold lives in the relu gate". The series
says something sharper and testable: if ρ(W*) is anywhere near 1, **no low-order
truncation can approximate the response at all**, and the honest object is the
RESUMMED solve (I − W*)^{-1}h — an iterative linear solve, never a dense inverse
on 21k nodes. ρ(W*) is one power iteration on machinery the lane already
certified (L210/L216/L218). This is now a registered leg of L260 rather than a
new card.

**READ 2 — the PARADOXICAL-RESPONSE / ISN literature, which NAMES L228's own
headline. Miller & Palmigiano, "Generalized paradoxical effects in
excitatory/inhibitory networks", bioRxiv 2020.10.13.336727 (read abstract +
analysis statements in full); primary source Ozeki, Finn, Schaffer, Miller &
Ferster, Neuron 62:578–592 (2009) "Inhibitory stabilization of the cortical
network underlies visual surround suppression" (PMC2691725, read at
results-quote level); Sanzeni et al., bioRxiv 656710 "Inhibition stabilization
is a widespread property of cortical networks" (abstract + results quotes);
plus Tsodyks et al. (1997) as the originating reference.** | What they did: an
**inhibition-stabilized network (ISN)** is defined as a network at a *stable*
fixed point *"for which the excitatory subnetwork would be unstable if
inhibitory rates were frozen at their fixed point values"* — stable overall,
unstable with I frozen. Its signature is a **sign inversion**: adding
excitatory input to I cells *lowers* their steady-state rate; removing
inhibition *raises* inhibitory activity; and in Ozeki's own words, in an ISN
*"addition of external inhibition to E cells causes a reduction in the total
inhibition they receive, because of the induced decrease in r_I"*, i.e.
**ΔI^TOT < ΔE_E in an ISN while the total inhibition received INCREASES in a
non-ISN**. Miller & Palmigiano generalise it to a criterion: *"a given cell type
shows a paradoxical change in steady-state rate in response to input it
receives, if and only if the network with that cell type omitted has an ODD
NUMBER OF UNSTABLE MODES"*, and — the clause that matters for us — *"the net
steady-state inhibition received by any unstable mode of the excitatory
subnetwork will change paradoxically, i.e. in the same direction as the change
in amplitude of that mode."* | The numbers that matter: the effect is large and
qualitative, not marginal — in a balanced-network demonstration (PMC3933683)
eliminating ALL external input to the inhibitory neurons drove both populations
from ~5/10 Hz to **above 50 Hz**, and the same manipulation in a weak-synapse
(non-ISN) network *raised* E from 12→35 Hz while *lowering* I from 14→11 Hz —
the two regimes are told apart by the SIGN on the inhibitory population, not by
a magnitude. | **What it changes for peabrain: L228's result is a textbook
paradoxical-sign signature and the lane did not know the name.** L228 measured
that the floor's activity RISE on Tr_L was dominated by `exc_srcneg` **+46,219**
— removing *excitatory* edges from net-inhibited sources — while the quadrant it
had registered as the mechanism, genuine disinhibition, **shrank by −34,315**;
the net inhibition delivered to the pool moved in the SAME direction as the
pool's own activity change. That is clause (3) of Miller & Palmigiano verbatim,
in our currency. **Folded into L260 as its fourth registered leg** (not a new
item, per the research-tick rule): with the gated operator in hand, measure
ρ(D·W) for the whole cord subnet AND ρ(D·W_EE) for the excitatory subnetwork
alone — the ISN condition is ρ(D·W) < 1 *with* ρ(D·W_EE) > 1, which is exactly
"stable, but unstable with I frozen", and it is a zero-rollout read on stored
settled X. **Registered escape, written before measuring:** a paradoxical-
looking share decomposition is NOT an ISN. If ρ(D·W_EE) ≤ 1 the sign pattern
has some other cause and L228's quadrant table stays a description — the lane
does not get to borrow the mechanism's name without its stability condition.

**THE CORRECTNESS BITE, found by reading the prior art against our own code:
L260's gate as written is WRONG for peabrain's nonlinearity.** The card
registers `D = 1[X > 0]`. But `brain.py` line 5 is
`tau dX/dt = -X + relu(gain*(W@X) + I)` with **line 18 `RMAX = 1.0`** and
**line 72 `target = target.clamp(max=RMAX)`** — so the local gain f*_i is 1 on
`0 < X < RMAX` and **exactly 0 at the ceiling**, where `1[X>0]` scores it 1.
Every saturated cell would be entered into the effective operator at full gain.
Amended into L260: **MEASURE the saturated fraction on both stored arms
(cutwA, f4wA) BEFORE forming D, report it beside the branch, and use
`D = 1[0 < X < RMAX]`** (the card's own soft `dX/dnet` variant is the same
object done properly). L208's lesson predicts the fraction is small at a sparse
operating point — which is precisely why it must be measured rather than
assumed, and if it is 0.0000 the correction is free and the gate is certified
instead of hoped.

Parked one-liner (read at abstract level only, not folded): **2611.27322** —
Oh & Lee, "Spiking Neural Networks Incrementally Track Firing-Rate Networks"
(cs.NE, 20 Nov). Proves a converted discrete SNN's output *"continuously tracks
the instantaneous ANN output implicitly determined by the SNN input"* and builds
LIF-Stream on it for streaming inference. Of standing interest to the lane's
rate-vs-spiking fidelity caveat (L15: a homogeneous-tau rate model cannot carry
temporal structure) — the theorem says the rate network is the object a spiking
net *tracks*, so fixed-point-level claims are the transportable ones and
transients are where the two diverge. But it is an efficiency framework for
converted ANNs, not a statement about biological spiking, so it is parked rather
than used as support.
