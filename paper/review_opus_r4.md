# Referee report — ROUND 4 (opus family, fresh), final pre-human gate

**Reviewer vantage:** computational neuroscientist who builds
connectome-constrained rate models of the fly nerve cord. CPU only, no
rollouts, stored artifacts only. I imported no lab analysis function; Wilson,
Newcombe and Spearman are my own implementations
(`review_opus_r4_evidence/10_recompute.py`).

**Decision: NEEDS MINOR REVISION.** The arithmetic is clean — cleaner than any
paper I have refereed. Every number I checked reproduces exactly. The remaining
distance to a human referee is not statistical, it is framing and packaging: one
adverse robustness number that three rounds have asked for and that is still not
printed, one yardstick that was never calibrated, and a figure layer that does
not resolve.

---

## 0. Pins and a disclosed drift

Pinned at start (`00_pins.txt`, 2026-11-21T14:22:18-05:00), re-pinned twice
(`99_repins.txt`). `DRAFT.md` snapshot in `01_DRAFT_snapshot.md`.

**The claim-bearing objects never moved.** Byte-identical from 14:22 to the end
of this review:

| file | sha256 | status |
|---|---|---|
| paper/DRAFT.md | `c60fc1859d94ac46…` | **unchanged** |
| paper/numbers.json | `464e5261317f6fd3…` | **unchanged** |
| paper/CLAIM-MAP.md | `a0460e3da4ba0e88…` | **unchanged** |
| paper/references.bib | `828d257469ebb984…` | **unchanged** |
| figures/fig4_caption.md | `bc1cd445…` | unchanged |
| figures/fig5_caption.md | `86f44f1c…` | unchanged |

**DRIFT, disclosed — both figures were re-rendered under me by a concurrent
figures-polish dispatch.** I was reviewing a moving target in the figure layer
and not in the text layer.

| object | start sha256 | end sha256 | moved at |
|---|---|---|---|
| fig5_threepanel.png | `8f170637…` | `9d838cc0…` | 14:26:24 |
| fig5_threepanel.svg | `1879006c…` | `029933a0…` | 14:26:24 |
| fig5_threepanel.py | `df9affcf…` | `0913a093…` | 14:26:19 |
| fig4_scatter.png | `a0f1e0ca…` | re-rendered | 14:34 |
| fig4_scatter.svg | `c01602e6…` | re-rendered | 14:34 |
| fig4_scatter.py | `be041f96…` | re-rendered | 14:34 |
| fig4_verify.py | `5d2093ca…` | re-rendered | 14:34 |

Handling, so that nothing below rests on a stale read:

- **I re-ran every figure check against the final files.** The fig4 change was a
  single constant — the x-domain upper bound went `log10(1.25)` → `log10(1.6)`
  to stop the s2t diamond clipping at x≈1. My first inverse-geometry pass
  hard-coded the old constant and threw six false mismatches; I rewrote
  `12_figcheck.py` to **parse the geometry out of the generator source** instead,
  so the check cannot go stale again. On the final files it reports **0
  disagreements**, and the lab's own `fig4_verify.py` still passes 247 checks.
  **Fig 4 is honest in both renders.**
- **Every fig5 finding in M3 holds against the new file**, re-checked after the
  rewrite: still zero `data-*` attributes, still no `fig5_verify.py`, and the
  three carrier values its caption quotes (.758 / .510 / .622) still appear
  nowhere as text in the SVG.
- `fig5_caption.md` (14:18:35) now **predates its own render by ~8 minutes** and
  was not regenerated with it. I cannot confirm caption/render agreement:
  no-vision is a rule of this dispatch, and fig5 carries no machine-readable
  attributes to check instead. That is a direct cost of M3 and the reason M3
  asks for a verifier rather than a prettier picture.

No recompute, delta-check or major below depends on a figure file. M3 is the one
finding that does, and it is stated against the final versions.

---

## 1. Recompute with my own code — everything reproduces

`10_recompute.py` / `11_recompute_out.txt`, `12_figcheck.py` /
`13_figcheck_out.txt`.

**Pooled counts, recomputed from `l172/stats.json:per_seed` by deduplicating on
seed id (the canonical §2.14 rule), not from the lab's `pooled` block.** My
Wilson score intervals, my dedupe:

| arm | mine | stored | agree |
|---|---|---|---|
| cutng25 (carrier) | 203/210, mean .7663, [.9328,.9838] | identical | ✓ |
| cutng25p (mass twin) | 30/66, .4585, [.3402,.5738] | identical | ✓ |
| cutwA (base) | 72/258, .4045, [.2279,.3367] | identical | ✓ |
| silW (clamp) | 78/98, .6435, [.7057,.8638] | identical | ✓ |
| cutscr0 | 41/50, .6233, [.6920,.9023] | identical | ✓ |
| cut58 | 1/258, .2201, [.0007,.0216] | identical | ✓ |
| cutng29 | 188/194, .7679, [.9342,.9857] | identical | ✓ |

Zero duplicate seed ids in any arm. The §2.14 dedupe rule is real, not asserted.

**L175 table rows, recomputed from the raw per-seed `dutyR` arrays** (eight rows,
not the three asked for) — `cutwA, sc25, sc26, sc27, sc40, dmA, dmC, sc47`: k,
mean duty and registered class all reproduce, including the two Wilson bounds
the draft quotes in prose (carrier 16/16 → lower .8064, draft says .806; s2t
2/16 → upper .3602, draft says .360).

**Descriptive statistics, my own tie-corrected Spearman:** ρ(gain, meanR) = −.592
all 34 / **−.723** over the 33 non-carriers / **−.833** over the 20 low-rate arms;
ρ(drive, meanR) = **+.187** active / **+.548** active-excitatory. All four
draft-quoted values exact. Class census 1 super / 10 intermediate / 23 not-super
reproduces under my own re-implementation of the band rule. Silent-null width
2–11 seeds and .340–.605 exact. "Gain shifts at most 1.13%" exact (my max
1.131%, computed as Δg/g_base).

**threepanel.csv:** sc25 / cutwA / dmA rows match Table 1 in all three panels.
Cross-artifact check I added: the chopped column of `l184/threepanel.csv` agrees
with `l175/results_l175.json` for **all 37 shared arms**, with no disagreement
beyond 3-dp rounding of the stored `meanR`.

**Figure data, inverse check.** The lab's `fig4_verify.py` asserts forward
(data → pixels, 247 checks, passes). I inverted instead: parsed the marker
pixel coordinates out of `fig4_scatter.svg` and ran the generator's own axis
transform backwards to data. Seven arms (`sc25, sc27, sc40, sc41, sc50, sc33`
+ base) recover their stored x̄ and meanR to <0.01 dex and <0.002 duty. Plotted
SUPER threshold, base band and base line carry the registered band value and the
stored Wilson bounds exactly. **Fig 4 is honest geometry.**

**Table 4's strongest claim verifies.** The draft says its chopped column
"reproduces the canonical pooled count of §2.14 exactly for every arm shown." It
does, for all eleven arms. I also recomputed all eleven continuous-segment
Wilson intervals: all eleven match the printed interval.

Nothing in the arithmetic layer needs fixing. The lab should be told that
plainly; four families have now failed to break it.

---

## 2. Delta-check of rounds 1–3 and the second opinion

Round-1 majors (12), round-2 fresh majors (N1–N7), round-3 three-changes, and
the owner-supplied claude.ai second opinion (5 points + "the control she didn't
run").

| from | issue | verdict in THIS draft | pointer |
|---|---|---|---|
| R1-1 | scramble arms unreported, uniqueness overclaim | **resolved** | §2.7 table + "sufficient, not unique" in title logic, abstract, §5 |
| R1-2 | male non-transfer was a floor artifact | **resolved** | §2.11 "UNTESTED AT MATCHED FLOOR"; §5 repeats it correctly; the false Discussion sentence r2 caught is gone |
| R1-3 | slow line described the stimulus | **resolved** | §2.13, §3.3, §4; out of the headline |
| R1-4 | gain re-matching confounded with the flip | **resolved, well** | §2.2 gain-only null, §2.12 two 2×2s, §3.4 fixed-gain rule. This is now a strength |
| R1-5 | jitter robustness narrower than stated | **COSMETIC ONLY** | see M1 |
| R1-6 | floor robustness only with membership frozen | **resolved** | §4 f4 dynamic arm run and its failure printed |
| R1-7 | statistical wording outruns tests | **resolved** | §2.14, §3.7 paired-inference rule |
| R1-8 | abstract/body inconsistencies | **resolved** | abstract now matches the body on every figure I checked |
| R1-9 | readout scope; other four antagonist pairs are 0/16 | **PARTIAL, third round running** | §4 "One readout family" names the tibia pair but the draft **still never states that the other four antagonist pairs score 0/16 in the lesion arms** (grep: no such sentence). r1 asked, r2 logged it as a residual, it is still absent |
| R1-10 | §2.4 incoherent as a two-factor law | **resolved** | rebuilt on silW; identities moved to §3.8 |
| R1-11 | "not yet a manuscript" | **PARTIAL** | all-caps down 222 → **165** tokens (91 distinct) between abstract and §5; but line 1 is still `# WORKING DRAFT — preprint skeleton (L140 + L143)` with **533 lines of changelog above the title**, §2.6's heading still carries a file path, and §7 still says "13 entries" and "figure polish … remain TODO" |
| R1-12 | figures | **UNRESOLVED, and now worse** | see M3 |
| R2-N1 | mass twin is silent | **resolved, exemplary** | §2.1 "The mass twin is silent, and we say so", title retired, drive twins + signed-current twin added, abstract states it |
| R2-N2 | robustness panel applied to one contrast only | **resolved** | Table 1 carries all three panels for all 37 arms; Table 4 re-scores the ladder |
| R2-N3 | Methods describe a model that was not run | **resolved** | §3.1–§3.3 printed equation, sign table, DNg100 tonic term, in-degree sentence explicitly withdrawn |
| R2-N4 | abstract/Discussion contradict body | **resolved** | |
| R2-N5 | seed certainty vs network fragility | **COSMETIC ONLY** | see M1 |
| R2-N6 | twin p=.008 borrows base seeds | **resolved, well** | §2.7 + §3.7: McNemar p=.0895 is now the primary, .008 labelled pooled |
| R2-N7 | readout sits in near-silent pools | **resolved** | §2.3 prints pool rates .0260/.0248 and .0262/.0330 and says they sit near background |
| R3-1 | make the measured contrast the paper | **resolved** | title adopted verbatim; scan is now §2.1 |
| R3-2 | validate specificity on a frozen second batch | **resolved** | §2.2 batch N, both gain forms, signed-current twin |
| R3-3 | make model and estimand reconstructible | **resolved** | §3 + §2.14 |
| 2nd-op 1 | twin is silent | resolved (= N1) | |
| 2nd-op 2 | Methods misstate the model | resolved (= N3) | |
| 2nd-op 3 | effect is fragile | **partial** | floor-4 and rewire failures are printed in §4/§5; the jitter leg is not (M1) |
| 2nd-op 4 | novelty overstated, Alstott missed | **resolved** | Alstott is now [41] and §1's third lineage is honest about it |
| 2nd-op 5 | "preregistered" unverifiable | **resolved as disclosure** | §3.8 "What preregistered means here"; "Public, dated registration is an open item" |
| 2nd-op | "the control she didn't run" (single-cell null) | **resolved** | the 34-arm scan IS that control |

**Tally: 21 resolved, 3 partial, 2 cosmetic-only, 1 unresolved, 0 regressed.**

The two cosmetic-only fixes are both the fragility item (R1-5 / R2-N5). §2.10
gained the sentence "the interior re-draws across gains (wA hit KILL in one set,
SUPER in another)" — which is true — without gaining the number that sentence is
standing in front of. Details in M1. I want to be precise about the charge: this
is not concealment, it is a disclosure written one abstraction level above the
damaging number.

---

## 3. Fresh majors from my vantage

### M1 (major). In one of five jitter networks the title contrast reverses, and §2.10 does not say so.

`banc/l139/results_l139.json:sets`, recomputed in `20_openitems.py` / `21_openitems_out.txt`:

| set | base cutwA | twin cutng25p | carrier cutng25 | carrier − base | carrier − twin |
|---|---|---|---|---|---|
| 0 | 3/16 PARTIAL | 9/16 NEUT | 14/16 SUPER | +11 | +5 |
| 1 | 10/16 NEUT | 13/16 OTHER | 16/16 SUPER | +6 | **+3** |
| 2 | 0/16 | 5/16 PARTIAL | 16/16 SUPER | +16 | +11 |
| 3 | 3/16 | 6/16 PARTIAL | 13/16 SUPER | +10 | +7 |
| 4 | 1/16 KILL | 0/16 KILL | 14/16 SUPER | +13 | +14 |
| **5** | **15/16 SUPER** | **13/16 SUPER** | 13/16 SUPER | **−2** | **0** |

In set 5 the base reaches the super class **with the carrier still in it**, the
mass twin reaches it too, and the carrier arm is the *lowest* of the three. The
paper's whole claim — that removing this cell is what lifts the readout into the
registered class — is false in that network. In set 1 the carrier-vs-twin margin
is 3 seeds.

§2.10 reports only class-sustain fractions (`cutng25` 5/5, `cutwA` 0/5,
`cutng25p` 0/5) and the sentence about the interior re-drawing. A reader cannot
recover the table above from the draft, and the base's per-set spread
(3, 10, 0, 3, 1, **15**) appears nowhere. §4's "Network-level fragility" card
cites §2.10 for this and inherits the same gap.

This is the single highest-risk item in the manuscript. A human referee who
opens `l139` — and the repo is public — finds a 1-in-5 sign reversal of the
headline contrast that the robustness section did not print. Three model rounds
asked for exactly this number. Print it, in §2.10 **and** in the abstract's
robustness clause, and state what it does and does not cost the claim. My own
view is that it costs less than the lab fears: with weights jittered, the base
sometimes does not need the deletion, which is a statement about the base's
proximity to threshold (already §4's own disclosure, citing [36]) rather than
about the carrier. Said out loud it is a limitation. Found by the referee it is
a rejection.

### M2 (major). The registered band was never calibrated against the undamaged network, so "super" names a partial rescue.

The construction is a deafferented closure: 560 descending neurons that project
into the cord but receive no cord input are added to a baseline network, and all
of them have lost their brain input (§3.1). The measured consequence, from the
draft's own Table 4 and §2.14:

| network | chopped | continuous |
|---|---|---|
| b65, before the projectors are added | 513/513, mean .995 | 513/513, 1.000 |
| closure, nothing removed | 207/513, .457 | 0/513 |
| base (24 removed) | 72/258, .404 | 0/258 |
| **carrier removed** | **203/210, .766** | 132/210 |

Adding the projectors is the largest effect in the paper: my Newcombe interval
for b65 − closure in the continuous segment is **+1.000 [+.989, +1.000]**. The
entire removal ladder is the partial undoing of a deficit the extraction rule
inflicted, and the carrier arm at .766 does not restore the .995 the network had
before the projectors arrived.

§3.1 says this, honestly and in one place: "the removal ladder is the removal of
ectopically active cells from a network they degraded. Every result in §2 should
be read with that construction in view." That sentence is doing more work than
any other in the Methods, and it appears in neither the abstract nor the
Discussion. The registered SUPER band (meanR ≥ .60, kR ≥ 12/16) was frozen on
the damaged substrate, where the base sits at .408 — it is a yardstick
calibrated to the lesion, and b65 sits far above its top.

Two of my own findings converge on the same reading, and neither is in the draft:

- **Deleting almost any window cell nudges the readout up.** Mean paired ΔR
  against the base over the 20 low-rate arms is **+.044**, with **14 of 20**
  above the base; over the 14 active arms it is −.009. The "silent-cell null" is
  not a null centred on no-effect, it is an upward-shifted band. The right null
  for "does deleting *this* cell raise duty" is centred at +.044, not at 0.
- **The carrier is the strongest of several upward movers, not the only one.**
  Of the 14 active window cells, 4 move duty up by >.05 (`sc25` +.351, `sc39`
  +.139, `sc50` +.119, `sc53` +.075) and 6 move it down by >.05. §2.1 mentions
  only ranks 33 and 34 as opposite-direction movers. The claude.ai rebuild found
  the same shape independently ("1 up, 9 down, 25 unchanged").

I am **not** asking the lab to retract anything. The scan result survives this
reframing intact — the carrier is still the only arm that crosses the band, and
crossing it from a +.044 null is still a 12-of-16-seed, 8σ-ish event. I am
asking for the frame to be stated where a reader meets the claim, because it is
the first thing a model-builder will reconstruct and the paper currently makes
them do it themselves.

### M3 (major, cheap to fix). The figure layer does not resolve.

- The draft cites **Fig 1, Fig 2, Fig 3** only. Fig 1 and Fig 2 are cited as
  `peabrain-figs/l136_transition_law.png` and
  `peabrain-figs/l152_clamp_cut_grid.png`. **The directory `peabrain-figs/`
  does not exist** anywhere under `~/critters` (checked). The files exist at
  `banc/l136/fig_l136.png` and `paper/fig_l152.png`. **Fig 3** is cited bare in
  §4 with no path, and I could not locate a file for it.
- **Fig 4 and Fig 5 are never cited in DRAFT.md** (grep: zero `fig4`/`fig5`
  references). They are the two figures built to answer rounds 2 and 3 — the
  36-arm scatter and the three-readout honesty panel — they are captioned, and
  fig4 is verified. They are orphans.
- **Fig 5 has no verifier and no machine-readable data.** `fig4_scatter.svg`
  carries 54 `data-arm` attributes plus `data-v`/`data-lo`/`data-hi` on the
  threshold and band, and `fig4_verify.py` runs 247 assertions. The current
  `fig5_threepanel.svg` carries **zero** `data-*` attributes and there is **no
  `fig5_verify.py`** — still true after the 14:26 rewrite. The three carrier
  values the caption quotes (.758 / .510 / .622) do not appear as text in the SVG
  either. So the one figure carrying the three-readout dissociation — the
  backbone of §2.4's mechanism claim — is the one figure no one can check
  without eyes, and this dispatch has no eyes. The mid-review re-render
  demonstrated the cost: the caption is now older than the picture it describes
  and nothing in the repo can tell you whether they still agree.
- Round 2 marked Fig 2 UNRESOLVED because its printed labels (43/144, 124/128,
  21/32 …) disagreed with the canonicalised table (72/258, 203/210, 21/34 …).
  `paper/fig_l152.png` has not been touched since 2026-11-19 21:43. §2.9 still
  points the reader at it.

### M4 (minor-major). "Silent" is an operating-point label doing duty as a drive label.

§2.1: "Removing any one of the **20 silent cells, which deliver essentially
nothing**…". But §3.4 defines active as x > .05, so "silent" here means x ≤ .05.
Eight of the twenty fire well above numerical zero:

| arm | rank | x̄ | % of carrier's rate | drive ×carrier | kR | meanR |
|---|---|---|---|---|---|---|
| sc27 | 27 | .0408 | 10.5% | .115 | 11/16 | .596 |
| sc40 | 40 | .0343 | 8.8% | .194 | 11/16 | .605 |
| sc38 | 38 | .0243 | 6.3% | .065 | 3/16 | .340 |
| sc52 | 52 | .0201 | 5.2% | .076 | 8/16 | .506 |
| sc45 | 45 | .0200 | 5.1% | .050 | 4/16 | .462 |
| sc30 | 30 | .0194 | 5.0% | .099 | 10/16 | .531 |
| sc56 | 56 | .0171 | 4.4% | .060 | 5/16 | .407 |
| sc48 | 48 | .0075 | 1.9% | .032 | 9/16 | .497 |

The two "edge-of-band" arms the draft singles out — ranks 27 and 40, the two that
come nearest the super band — are **the top two of this subgroup by rate**. The
quoted null width (2–11 seeds, .340–.605) has its ceiling set by its least
silent members: the 12 genuinely near-zero cells span meanR .355–.489, the 8
sub-threshold-active ones span .340–.605. Within the 20, ρ(x̄, meanR) = +.426
and ρ(drive, meanR) = +.489.

Two consequences. (i) "which deliver essentially nothing" is not true of 8 of
the 20 and should be cut or quantified — a cell at 10% of the carrier's rate and
12% of its drive is a weak comparator, not an inert one. (ii) The sentence "its
outcome is one draw from the silent-cell null" is *fine for the mass twin*
(x̄ = .0005, genuinely silent), and the draft should say that explicitly rather
than leaning on a pool that is heterogeneous. Relabel: "20 cells below the
operating-point bar, of which 12 are numerically inactive and 8 fire at 2–10% of
the carrier's rate."

### M5 (minor). The 60% edge ratio is used quantitatively after being disclaimed.

§2.4: the carrier-to-relay edge cut gives +.223 [+.082, +.364] chopped duty
against the carrier's +.370 [+.257, +.483] on shared seeds; the draft reports
the point ratio as 60%, notes "that ratio has no interval", then uses it twice as
a mechanism statement ("about 60% of the carrier's shift by point ratio", "the
chopped component is reproduced in substantial part").

A referee can bound it from the printed intervals: .082/.483 to .364/.257, i.e.
**17% to >100%**. One number inside that range should not carry the phrase "in
substantial part". Worse, the edge arm exists only at a re-bisected gain of
−0.358%, and §2.2's own base slope (−.0228 duty per +0.1% gain) predicts
**+.082** from the gain change alone — **37% of the observed +.223**. The draft
states this risk in prose ("without a fixed-gain form the deletion is not
separated from its gain adjustment") but never does the subtraction. Do it, or
run the fixed-gain arm; it is one batch of 16.

The second leg of the dissociation is in better shape: the 1.4-Hz signature is
0/16 for the edge cut against 8/16 for carrier removal on shared seeds, and no
carrier-present graph in either batch shows it. **"Double dissociation in a
limited sense" is earned as wording** — the draft defines the limitation in the
same paragraph (two readouts, two batches, no necessity claim), which is the
right way to use a hedge. I would keep it.

### M6 (minor). Table 4's "specific to the chopped readout" is very slightly over-claimed.

The claim is "the non-monotone dose response is specific to the chopped readout".
In the continuous column the ladder is also non-monotone: k=25 is 132/210 (.629)
and k=29 is 108/194 (.557). My Newcombe interval for that difference is
**+.072 [−.024, +.166]** — non-monotone in point estimate, unresolved as a
difference. The k=58 rise over k=29 is resolved (+.164 [+.075, +.251]).

The defensible claim is narrower and still interesting: *the window closes* — the
large-cut collapse that made the chopped ladder a window reverses, and the
carrier step is the first rung with any continuous structure. Say that; drop
"non-monotone … is specific".

### M7 (minor). Inference units, as a model-builder reads them.

The unit-of-inference discipline (§2.14, §3.7, §4) is the best I have seen in
this literature and I want that on the record. Three residual unit problems:

1. **Mean duty has no stated unit of inference in the 16-seed tables.** Wilson
   intervals are on the *proportion* of structured seeds; the mean-duty column
   carries bootstrap intervals only in the §2.14 pooled table. Table 1 prints
   `16/16 .758` with no interval on .758 at all, and fig4's caption has to say
   "not a confidence interval for meanR" to stop the reader misreading the band.
   Give mean duty a seed-bootstrap interval in Table 1 or drop the band.
2. **"×1.003 of the carrier's drive" is a ratio of two three-seed census means**
   (§3.5: "averaged over three census seeds"). A match quoted to four
   significant figures on n=3 invites a question the paper cannot answer. Quote
   the match tolerance with its census spread.
3. **Pool sizes are stated three ways.** §2.6 "the Ti flexor pool has n=101";
   §3.1 "tibia flexor 101 / extensor 12" then "The scored right-side tibia pools
   hold 51 flexor and 6 extensor"; §4 "(51 and 6 motor neurons)". These are
   bilateral-vs-right counts and they are all correct, but a reader meeting
   "n=101" in §2.6 and "51 and 6" in §4 will think one is a typo. Normalise to
   "right tibia: 51 flexor, 6 extensor (bilateral 101/12)".

### M8 (minor). Wet-lab spec: testable, and the paper is honest about why it probably is not.

The §5 prediction is unusually well-formed for a modelling paper: named cell
(left DNp33), within-animal control (right DNp33), named assay (femur-tibia
kinematics or tibia MN calcium imaging), **signed** prediction (right-side
antiphase strengthens, mean activity little changed), stated null on the left,
and three named falsifiers. That is a real preregisterable experiment and it is
the right thing to have added.

Its problem is the scope clause, and the draft states it: the effect exists only
after 24 other descending types are gone, the intact-animal prediction is a
null, and "we do not specify how to build" a broadly-descending-drive-reduced
preparation. A bench referee will read that as: the only version of this
experiment you can actually do in a fly predicts nothing. Two cheap repairs,
neither requiring a rollout:

- **Name the preparation.** Decapitated or neck-connective-severed walking
  preparations exist and are the standard way to study cord-autonomous leg
  motor output; a headless fly is the closest real analogue to a deafferented
  closure with descending drive removed. Say whether the model's base
  corresponds to that preparation, and if not, why not. Right now §5 gestures at
  "a preparation in which descending drive is broadly reduced" without naming the
  one every reader will think of.
- **Give the prediction a magnitude.** The model says +.3 duty on a 0–1
  correlation-fraction scale. State what that is in a measurable unit
  (phase-lag concentration, % of step cycles antiphasic) or say explicitly that
  only the sign is predicted.

Also: §5 says "we have verified no driver line specific to it" while §1 cites
[44] (Zung, split-GAL4 DN catalogue) as "the practical starting point for
genetic access". Those two sentences should meet — did the catalogue contain a
DNp33 line or not? That is a lookup, not an experiment.

### M9 (observation, not a fault). What the deafferented substrate framing buys.

A model-builder's note, offered as framing rather than criticism. The paper's
mechanism story and its construction story fit together better than the draft
lets them. §2.9 reports that the carrier is already the dominant single DN input
into its 70-cell intrinsic sheet (the other 57 cohort cells combined deliver
0.33× its mass), and that clamping it on the *intact* closure has no demonstrated
effect while clamping it on the *cut* base completes the flip — "its firing is
load-bearing exactly when the cohort's drive is gone". Combine that with M2 and
you get a single coherent account: 560 brain-deprived projectors inject ectopic
drive that decorrelates the tibia pools; removing them in bulk partially
restores antiphase; and the carrier is the single remaining projector whose
ectopic contribution to that sheet is largest, so it is the one cell whose
removal crosses the band.

That account predicts most of the paper's own oddities — the upward-shifted
silent null, the +.044 baseline drift, why 4 of 14 active cells move duty up,
why the effect vanishes on a substrate re-extracted at floor 4 (different
projector set), and why a rewire that relocates the carrier's mass elsewhere
does not reproduce it. It also makes the result *less* surprising and *more*
defensible, which is a trade I think the paper should take at this stage. It is
not currently anywhere in the draft as a connected argument.

---

## 4. Prior art my training knows that the fable / astra / terra sweeps may not

Every item below is offered for the lab to fetch and verify; I am naming them
from training knowledge, I have **not** fetched them in this dispatch, and
details (year, venue) should be checked before citing. I have excluded anything
already in `references.bib` and anything astra named in round 3 (Honey & Sporns
2008, Luccioli 2014, Soloperto 2016, Boes 2015, Prinz 2003).

**(a) Single-cell perturbation that reconfigures *timing* in a motor network —
the closest phenotype match in all of neuroscience, and I believe it is missing.**

- **Bartos & Nusbaum**, on MCN1 (modulatory commissural neuron 1) in the crab
  stomatogastric nervous system — *J Neurosci*, late 1990s. A **single
  identified projection neuron** whose activity switches the gastric-mill
  rhythm; related work (Bartos, Manor, Nadim, Marder, Nusbaum) shows the
  resulting coordination depends on the interaction between the two rhythms, not
  on the cell's firing rate alone.
- **Nusbaum & Marder**, on the single modulatory projection neuron (MPN)
  reconfiguring the pyloric rhythm — *J Neurosci* ~1989, two companion papers.
- **Nusbaum, Blitz, Marder**, review of microcircuit modulation by identified
  projection neurons — *Nat Rev Neurosci* ~2001/2017.

This lineage is the reason a fly referee may be unimpressed by "one cell changes
a motor readout's timing": in the STG it is a 35-year-old result with
single-spike resolution. The paper's defensible contrast is that MCN1/MPN are
*modulatory inputs under experimenter control* in a 30-cell circuit, whereas this
is a *deletion* from a 21,809-cell bulk-extracted subnet with comparators
matched on four currencies. §1 should draw that contrast explicitly — it is the
same move §1 already makes well against [4] and [36], and leaving the STG
unmentioned is the most conspicuous gap in an otherwise thorough §1.

**(b) The method §2.3 reinvents already has a name, a canonical caution, and a
60-year literature.**

The cross-seed pairing — flexor from run *i*, extensor from run *j* — is the
**shift predictor** / trial-shuffle corrector.

- **Perkel, Gerstein & Moore**, "Neuronal spike trains and stochastic point
  processes. II. Simultaneous spike trains", *Biophys J* 1967 — the origin of the
  shuffle/shift corrector for separating stimulus-locked from interaction-driven
  correlation.
- **Brody**, "Correlations without synchrony", *Neural Computation* ~1999 —
  **the single most relevant missing citation in the paper.** Brody shows that
  slow covariations and latency covariations across trials produce correlation
  structure that is *not* interaction, and that trial-shuffling is the diagnostic.
  §2.3's entire logic is Brody's, and his analysis also supplies the caution the
  draft reaches by hand ("a network that is merely more reproducibly locked to a
  shared stimulus passes the same test").
- **Aertsen, Gerstein, Habib & Palm**, "Dynamics of neuronal firing
  correlation: modulation of effective connectivity", *J Neurophysiol* 1989 —
  the JPSTH framework for exactly this decomposition.
- **Grün**, "Data-driven significance estimation for precise spike correlation",
  *J Neurophysiol* ~2009, and **Stark & Abeles** ~2009 — the modern treatment of
  what trial-shuffling does and does not license.

Citing these converts §2.3 from "the third-round referee suggested a clever
control" into "we applied the standard shift-predictor decomposition and report
it with its known limitations". That is strictly better for the paper, and it
pre-empts a human referee saying "this is just a shuffle corrector, and the
authors do not seem to know it".

**(c) Rate/oscillator-model lesion methodology beyond Alstott.**

- **Young, Hilgetag & Scannell**, "On imputing function to structure from the
  behavioural effects of brain lesions", *Phil Trans R Soc B* ~2000 — the
  canonical statement of what a lesion deficit does and does not license in a
  network. Complements [26] (Jonas & Kording) from the systems-neuroscience side.
- **Váša et al.**, "Effects of lesions on synchrony and metastability in cortical
  networks", *NeuroImage* ~2015 — lesions in a coupled-oscillator model of a
  structural connectome, with lesion size controlled. Methodologically the
  nearest neighbour to §2.10 and closer than Alstott to what this paper does.
- **Aerts, Fias, Caeyenberghs & Marinazzo**, "Brain networks under attack:
  robustness properties and the impact of lesions", *Brain* ~2016 — targeted vs
  random node attack in connectomes; the review that frames "which node" as the
  question.
- **Kaiser, Martin, Andras & Young**, "Simulation of robustness against lesions
  of cortical networks", *Eur J Neurosci* ~2007 — sequential node removal and
  cascading failure.
- **Keinan, Sandbank, Hilgetag, Meilijson & Ruppin**, "Axiomatic scalable
  neurocontroller analysis via the Shapley value", *Artificial Life* ~2006 —
  the formal result that **no single matching currency suffices** and that
  contributions must be attributed over subsets. §1 asserts exactly this ("No
  single currency suffices: a count match leaves removed weight free and a mass
  match leaves delivered drive free"). There is a theorem for it; cite it.
  Extends [27]/[28], which are already in the bib.

**(d) Timing-vs-rate phenotypes and single-DN causal control in the fly.**

- **Rayshubskiy et al.**, "Neural control of steering in walking *Drosophila*"
  (bioRxiv ~2020; later journal version) — DNa02/DNa01, a **single DN pair**
  whose activity predicts and causally biases turning. The nearest fly analogue
  to a single-DN causal motor claim, and complementary to [17] (Braun).
- **Bidaye et al.**, "Two brain pathways initiate distinct forward walking
  programs in *Drosophila*", *Neuron* ~2020 — DNp09; single DN type, distinct
  motor program, with a freezing/walking switch. Relevant to [13]'s lineage.
- **Mamiya, Gurung & Tuthill**, "Neural coding of leg proprioception in
  *Drosophila*", *Neuron* 2018 — FeCO encoding. Relevant to §1's
  deafferentation framing and to [34]'s FeCO result, which §1 already leans on.
- **Marder & Bucher**, on phase maintenance in rhythmic motor circuits
  (*Annu Rev Physiol* ~2007; *Curr Biol* ~2001) — the standard reference for why
  a *phase/timing* readout is the right thing to measure in a CPG-adjacent
  system and why it dissociates from rate. Supports the paper's own choice of
  statistic.

**Priority note I would want in §1:** none of the above is an antecedent for
this paper's actual conjunction, and I did not find one. But (a) and (b) are
close enough in *phenotype* and *method* respectively that their absence reads
as a gap in the literature search rather than as absence of prior art.

---

## 5. Verdict

**NEEDS MINOR REVISION** — and I want to be exact about what "minor" means
here, because three rounds of "major revision" preceded it. Nothing in the
measurement layer needs to change. No experiment needs to be run. Every one of
M1–M8 is a writing or packaging fix against numbers that already exist in the
lab's stored artifacts. If M1, M2 and M3 are done, I would sign this through to
a preprint without a further model round.

### The three changes that most raise survival odds with a human referee

1. **Print the per-set jitter table (M1).** Put the six-row base/twin/carrier
   table into §2.10, state that in set 5 the base reaches the super class with
   the carrier present and the contrast reverses by 2 seeds, and add one clause
   to the abstract's robustness sentence. Three rounds have asked for this
   number and the repo is public. This is the only item on my list that can get
   the paper rejected rather than revised.

2. **Reframe the ladder as partial rescue, where the reader meets the claim
   (M2).** Move §3.1's sentence about ectopically active projectors into the
   abstract and the Discussion's opening; add the b65 row to the reader's view
   early (513/513, .995 chopped) so "super at .766" is read as partial recovery
   of a construction-induced deficit, not as a regime transition; and correct
   the silent-cell null to its measured centre (+.044, 14 of 20 above base)
   rather than presenting it as a band around no-effect. This costs the paper
   nothing it actually claims and removes the single most available hostile
   reading.

3. **Make the figure layer resolve, and give Fig 5 a verifier (M3).** Fix the
   three broken `peabrain-figs/` paths, cite Fig 4 and Fig 5 in the body where
   §2.1 and §2.3/§2.4 need them, regenerate Fig 2 against the canonical pooled
   counts (it still shows 43/144 and 124/128), and add `data-*` attributes plus
   a `fig5_verify.py` on the model of `fig4_verify.py`. Then drop the
   `# WORKING DRAFT — preprint skeleton` banner and the 533 changelog lines
   above the title (R1-11, still open), and settle the "other four antagonist
   pairs are 0/16" sentence that r1 and r2 both asked for and that is still
   absent (R1-9).

### One blind spot I suspect all four families share

**We all audited the numbers against the band, and none of us audited the band.**

Four families — two fable rounds, astra, an independent claude.ai rebuild, and
now me — have recomputed counts, intervals, Spearmans, McNemars, pooling rules
and bit-identity certificates. All of it holds. Not one of us asked where
`SUPER = meanR ≥ .60 and kR ≥ 12/16` came from, or checked it against the
network *before* the deafferented projectors were added, where the readout sits
at .995 with 513 of 513 seeds structured. The band was frozen on the damaged
substrate, so it is a yardstick calibrated to the lesion: "crossing into the
super class" measures distance from a degraded base, not approach to the
network's own intact behaviour. The draft's §2 is scrupulous that crossing a
registered band "is not evidence of a bifurcation" — but the deeper point is
that the band's *location* encodes the construction, and every count in the
paper, including every control's negative result, is expressed in those units.

The reason I think this is a shared blind spot rather than an oversight is
structural: the lab gave each of us a gate-certified artifact tree and asked us
to verify claims against it, and a preregistered band is exactly the kind of
object a referee treats as given. It was given. It was also never justified.
A human referee from this field, who thinks in terms of what the intact cord
does, is likely to ask the question in their first pass.

---

## Evidence index — `paper/review_opus_r4_evidence/`

| file | contents |
|---|---|
| `00_pins.txt` | sha256 + mtimes of 13 objects, pinned 14:22:18 |
| `01_DRAFT_snapshot.md` | DRAFT.md as reviewed (`c60fc185…`, verified identical) |
| `10_recompute.py` | my recompute: own Wilson, own Spearman, own seed-dedupe |
| `11_recompute_out.txt` | its output — 7 pooled arms, 8 L175 rows, 5 ρ, 2 bounds, 37-arm cross-artifact check |
| `12_figcheck.py` | inverse SVG geometry (pixels → data) + caption arithmetic + fig5 attribute audit |
| `13_figcheck_out.txt` | its output |
| `20_openitems.py` | jitter per-set table, Table 4 Newcombe intervals, active/silent movers, silent-label audit, 60%-ratio bounds |
| `21_openitems_out.txt` | its output |
| `99_repins.txt` | end-of-review re-pin **+ the fig5 drift disclosure** |

**Writes:** this file and that directory only. I edited no draft, gate, artifact
or figure. No rollouts; CPU only; no vision tools used.
