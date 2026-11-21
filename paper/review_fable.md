# Referee report — fable 5.2 (claude-fable-5-2 via official Anthropic)

Review of DRAFT.md (sha256 b32c9781…febe8, 514 lines, reviewed 2026-11-19 23:15–00:26).
Reviewer hit its tool-iteration cap after evidence gathering, so this file is
reconstructed verbatim from its final structured answer by the dispatching
agent. All probe scripts, outputs and working notes are preserved at
`paper/review_fable_evidence/` (NOTES.md is the reviewer's own log). Figure
findings are analytic (SVG/OCR/collision checks): the reviewer's vision tool
failed 6/7 calls with a provider-config error (documented in NOTES.md), so it
did NOT eyeball the PNGs — treat figure findings as high-confidence-analytic,
not visual.

## Verdict

**Major revision.** The core finding holds and survived re-scoring: on the
24-cell-lesioned base, deleting DNp33-L (124/128) but not its mass-matched
twin (12/32) flips the right tibia readout, and silencing it at unchanged
gain does the same (28/32). The framing on top overreaches: uniqueness ("one
cell"), cross-connectome non-transfer, floor robustness, the "slow line", and
jitter robustness of the identity claim. The draft is also still a skeleton
(abstract 3,521 chars vs arXiv's 1,920 limit, bulleted sections, no model
equation). All four verify scripts pass, but they check value-vs-ledger
equality, not whether claims follow.

## Major issues

1. **Unreported contrary data (title, abstract, §2.2)** — the lab's scramble
   arms (l125/l127/l128) are absent from the draft and numbers.json. A
   29-cell lesion that spares DNp33-L (cutscr0) is right-side SUPER in 39/48
   seeds [.68,.90] over three batches; other equal-size scrambles give 0/32,
   12/32, 17/32. The carrier is sufficient on the k=24 base, not necessary
   or unique. (cutscr0 also raises the left side, so it is not the same
   crossed state.)
2. **§2.6 non-transfer is a threshold artifact** — the MaleCNS weights file
   has no floor (10.3M of 25.6M pairs have weight 1), while BANC has an
   implicit ≥3 floor. Reviewer reproduces the paper's 28 cells / K=9 at
   floor ≥1; at the matched floor ≥3 the male extraction yields 342
   pure-projection DNs, K=52 (BANC 560/77). Transfer is untested, not
   negative.
3. **Result (4), Fig 3 and the last third of the abstract describe the
   stimulus** — the mechanosensory drive is chopped 5 s on / 4 s off in the
   scored segments (l135_run.py 551–557), which Methods never mentions. With
   drive on, motor-mass tracks the chop envelope at median r=+.55 (17/18
   peaks at 0.1 Hz); with drive off r=−.03. 298 of 300 scoring windows
   straddle an on/off edge.
4. **Gain re-matching is confounded with the flip (§2.4)** — every flip arm
   was re-bisected to +1.1–1.3% above the cutwA gain (cutng25, eOutInt, eIn,
   eAll, eMotIn), while non-flip arms sit within ±0.1% (twin, both 5-edge
   halves). Only silW flips at unchanged gain, and the intermediate eOutMot
   arm is at −0.6%, so gain is not the whole story. No gain-swap control
   exists; the "~.13 silW→eAll margin" attributed to settle history could
   equally be the +1.24% gain.
5. **§2.5 robustness narrower than stated** — the 25-cell lesion stays SUPER
   in 5/5 jitter sets, but the carrier-vs-twin contrast is clear in only 3/5
   (16v5, 13v6, 14v0; absent at 13v13, n.s. at 16v13). The k=24 base itself
   ranges 0/16–15/16 under 1% weight jitter. The "±8% gain" span applies to
   the untreated arm only; lesioned-arm gains moved about 1%. Far narrower
   than FlyHack's ensemble, intervention and representation axes.
6. **§4 floor robustness holds only with cohort membership frozen** —
   reproduces rank 25→21 and Jaccard .9231 that way; re-applying the
   extraction rule at floor 4 gives carrier rank 46, twin 72, Jaccard .35,
   and 9/24 overlap in the first 24 cells. Analysis is static (zero
   rollouts). The right homolog (id 928) is outside the cohort only because
   it has ≥3-synapse cord input. "Kopel-class critiques are INADMISSIBLE" is
   unsupported, and Kopel is not a critique paper.
7. **Statistical wording outruns the tests** — twin "neutral" is 12/32 vs
   base 43/144 (p=.41, difference +.08, approx 95% CI −.09 to +.26), and
   21/48 if the un-jittered B28 batch is included. Carrier silencing on the
   intact net is called "inert" but trends down in both batches (5/32 vs
   12/32, p=.09), and "−.088 inside the .075 sham spread" is false on its
   face (n=3 shams). "Threshold footprint" rests on 14/32 vs 21/32 (p=.13).
   Left-side "death" is 0/48 vs 5/64 (p=.07). The census counts 518 traces
   from 449 unique seeds; 361/500 becomes 348/433 on unique seeds.
8. **Abstract/body inconsistencies the gates miss** — abstract quotes 20/64
   and 47/48 for arms §2.2 gives as 43/144 and 124/128; "kill→super" for a
   step that is partial→super; "12× below" where .0544/.005599 = 9.7×;
   "+.256/+.317" carries no key; "all 10 SUPER" vs the body's "between
   classes"; "k5" in the U-law is a glutamatergic control, not a ladder
   point; rank 25 (§2.2) vs "rank 34/58" (§2.3); the abstract promises a
   protocol release that §5 says is private/TBD.
9. **Readout scope** — only the tibia pair moves (the other four antagonist
   pairs are ~0 in every cohort arm, B26). k/n dichotomises a unimodal duty
   distribution near its centre for baseline-like arms, and "k=58 kills
   again" is a side switch (left 16/16). In the unchopped 1.4-Hz segment
   (reviewer's re-scoring, B26 only) baseline is 0/16 and k=58 is 13/16,
   while carrier-vs-twin gets cleaner (12/16 vs 0/16).
10. **§2.4 not coherent as a "two-factor law"** — (a) says the carrier's
    firing is load-bearing on the cut base, (b) concludes "its edges, not
    its firing". The two bit-identities (edge-removal ≡ node-removal; clamp
    on a disconnected cell ≡ no clamp) are true by construction — sanity
    checks, not findings. sil24 "reproduces the cut exactly" is 5/16 vs
    intact 6/16 in the same batch. §2.3 says statics cannot predict the
    carrier while §2.4a lists static features that single it out.
11. **Not yet a manuscript** — bullets in §1–§3, a 40-line changelog,
    lane/batch codes and 119 all-caps tokens in the body, no captions, no
    Discussion, and no model equation, drive, readout or class definitions.
    "Brain-and-cord connectome" describes a 21,809-neuron cord subnet whose
    DNs have no brain inputs. Zero numeric citations in the text; Shiu,
    Pugliese, Schlegel and Dallmann never cited; Sapkal and DUCKOPHILA cited
    but not listed; DNp01 uncited.
12. **Figures (analytic)** — nearly all text under 5 pt at 6.5-in width on a
    dark background (grey labels 2.3:1 contrast), titles carry lane IDs.
    Fig 1: panel A titled "monotone" against the draft's "non-monotone",
    pools stale, "B17–B26" given for 11 batches, +.334 conflicts with the
    text's +.371, k5 mass prints 0.000, one caption line crosses panel C's
    frame. Fig 2: whiskers join a mean-duty dot to a Wilson lower bound of a
    seed proportion. Fig 3: "xm" is the driven sensory mean but grouped as
    "motor-mass"; footer says 3×12 where the table is 2×18; referenced only
    from Limitations.

## Questions for the authors

- Why are the scramble arms (which the lab's own L125 verdict called
  "count-carried, placement story dead") absent from the Results?
- Is the MaleCNS extraction comparison made at matched synapse floors?
- What is the sensory drive waveform, and where is it stated?
- What exactly was re-bisected per arm, and by how much did gains move?
- What is the unit of inference — a noise seed of one fixed network?

## Missing citations (reviewer's list, with its rationales)

Namiki 2018, Stürner 2025, Cheong 2024, Braun 2024, Cande 2018 (descending
neurons); Azevedo 2024, Lesser 2024, Takemura 2024 (VNC connectomes — a third
transfer target); Eckstein 2024, Liu & Wilson 2013 (neurotransmitter sign);
Otchy 2015, Wolff & Ölveczky 2018, Jonas & Kording 2017, Keinan 2004, Fakhar
& Hilgetag 2022 (lesion inference); Prinz 2004, Beiran & Litwin-Kumar 2025
(parameter degeneracy); Yan 2017, Randi 2023 (single-neuron predictions from
a connectome); von Reyn 2014 (DNp01). Also: cite all 13 existing entries in
text; add Sapkal and a proper DUCKOPHILA repo cite; correct the Kopel,
FlyHack and ApproxBrain characterizations (ApproxBrain already reports
single-interneuron necessity over 32 held-out draws).

## Ranked improvements

1. Re-scope title, abstract and §2.2 to what the data support: a
   context-dependent, sufficient-not-unique single-cell effect isolated by a
   mass-matched control. Add the scramble arms to Results and the ledger.
2. Run four cheap controls before posting: gain swap (cutwA at cutng25's
   gain and vice versa; eOutAll at fixed gain vs silW); MaleCNS extraction
   at floor ≥3, then walk that ladder or say "untested"; a floor-4 dynamic
   run with re-derived membership; a degree-preserving rewire of the
   carrier's 93 edges plus deletion of the right homolog (928).
3. Cut the slow-line result from the abstract and headline list; state in
   Methods that the 0.1-Hz peak is the 9-s stimulus cycle. Report the
   readout re-scored in the unchopped 1.4-Hz segment and after a 0.3-Hz
   high-pass as a robustness panel — it strengthens the main contrast.
4. Rebuild §2.4 around its cleanest arm (silencing at unchanged gain flips
   28/32), then the edge decomposition. Drop "two-factor law"; move the
   bit-identities to Methods.
5. Write the manuscript: abstract ≤1,920 chars without keys/caps/arm codes
   (a 1,760-char draft is at review_fable_evidence/abstract_rewrite.txt);
   prose sections; a Discussion; Methods with the update equation,
   constants, DNg100 and chopped sensory drive, active-fraction target,
   cohort/mass/ladder and class definitions, pooling rule. Add a notation
   table with plain names.
6. Statistics: one pooled count per arm everywhere; differences with
   intervals instead of "contains .5"; mean duty with bootstrap CIs beside
   k/n; unique seeds only; state the unit of inference. Enlarge the jitter
   ensemble (≥20 sets, >1%) and report per-set carrier-vs-twin contrast.
7. Redraw figures for print (light background, ≥7 pt, captions in draft, no
   lane IDs); fix the listed defects.
8. References: the missing-citations list above.
9. Back "preregistered" with public timestamps (no version-control history
   found in the lab tree) and reconcile the release promise with §5.
