# LAB-INTENT — is the needs-ladder intent in the motor port? (L7b, tick 21)

Question: can the needs-ladder intent (beg/to_bowl/settle/to_boot/parade/
to_pond/investigate/stay) be linearly decoded from the DN population vector
(1,303 descending neurons, v783), and does the DN placement carry more of it
than random same-size populations?

## Method (peabrain-lab/l7b_intent_decode.py, artifacts l7b/)

- 288-sample grid: {day 12h/sleep .05, night 23h/sleep .85} x hunger
  {.2,.9} x trust {.10,.45,.90} x curiosity {0,.5} x parade_ticks {0,2} x
  event {quiet, rake, swat, shiny, water, peas}. Body scalars set directly
  (they live at the bridge, never in the brain); brain fired through the
  REAL MoodState.observe (0.5 s window — peak targets identical to the live
  2.0 s call; hunger/sleep advance <1e-3), X0-snapshot restored per sample,
  100-step history with the CX circadian tonic when dark. Ladder conditions
  copied verbatim from bridge.needs() (incl. CURIOSITY_GATE .35, hunger
  outranks fear). Features = DN vector at the same step the live peak-read
  uses (stim step 20; ambient X for quiet). 5 random non-DN population draws
  recorded at the IDENTICAL read step (null ensemble); 3-scalar arm = the
  (mean, L, R) cx_intent uses today. z-scored multinomial logistic (L2
  2e-2, 600 full-batch iters), 75/25 split, fixed seed.
- Exact ceiling: body state never enters the brain, so features can only
  depend on (hour, event) — best possible decoder = majority label per cell.

## Results (held-out, n_test=72)

| arm        | train | held-out | notes                                   |
|------------|-------|----------|-----------------------------------------|
| DN-vector  | 0.995 | 0.319    | fits train (memorizes noise), no signal |
| DN-3scalar | 0.306 | 0.306    | cannot even fit train                   |
| null-0..4  | .45-1.0 | 0.236-0.458 (mean .361) | spread swallows DN arm |
| ceiling    |   —   | 0.528    | brain-only decoder bound                |

Label mass: settle 84 (29%), beg 72 + to_bowl 48 (42%, hunger), parade 36,
rest small. Majority-class baseline (always settle) = 0.292.

Per-class (noisy, n2-n22): settle is the ONE thing everyone finds
(DN .50, 3-scalar .77, null-0 .77 — the circadian tonic is readable from
the DN MEAN, i.e. ambient activity, not from event structure); event-driven
classes (to_boot n4-in-test) too small for per-class claims.

## Verdict (negative, clean)

The needs-ladder intent is NOT decodable from the DN population vector
beyond what random same-size populations carry (0.319 vs null .236-.458;
both under the 0.528 ceiling). Why, mechanically:

1. The ladder's dominant inputs are BODY state the brain never sees:
   hunger (42% of label mass: beg/to_bowl), parade_ticks, banked curiosity.
   No readout can recover information that never entered the population.
2. The brain-visible mass is mostly circadian (settle), which reaches DN
   as a slow ambient shift — the 3-scalar cx_intent readout already carries
   it (settle recall .77); the full vector adds nothing but overfit noise.
3. Event-driven intents (to_boot on looming) are real but tiny mass on any
   realistic grid, and at the event peak the DN encodes the EVENT (greet
   .43 vs ambient .05, live-verified; preflight z=+7.7), not the ladder's
   body-overridden ANSWER (a hungry duck begs even mid-rake — by design).

## Consequences

- Keep cx_intent framed as an EVENT-RESPONSE readout (move/turn/arousal at
  the peak) — it was never an intent predictor and this confirms it must
  not become one by reading more neurons. Selection stays at the drive
  ladder (consistent with Nanni&Lee: CX normalizes, doesn't select).
- L12's condition is TRIGGERED: brain-born begging needs an interoceptive
  input channel (hunger tonic onto an ANS-like population, body-labeled
  like the CX circadian tonic) — otherwise hunger-class intents can never
  live in the brain. Owner call before any live wiring.
- L7b's fusion card (distill the intent ladder onto DN-class gains) is
  DEAD as stated — distilling a body-dominated function onto neural gains
  would just relearn the circadian mean. If we revisit, distill the
  EVENT->move/turn map (which IS neural) instead.

## L11 — malecns DN->motor: real-wiring gait prototype (tick 22, 11-10)

Setup: male_graph.pt (166.7k, 25.56M edges), brain.py recipe verbatim
(tau .05 / dt .01, bg .02, noise .01). Op point BISECTED: 0.95/rho
saturates here (53.7% active) — male in-degrees ~5x female — matched to
16.4% active at gain .8846 (matched-op-point lesson). Events 20 steps,
peak-read, 3 noise seeds per arm.

| event (amp)     | motor mean abs-delta | motor self-cos | DN self-cos | notes |
|-----------------|----------------------|----------------|-------------|-------|
| looming LC4/16/11/12 (8) | .0037 | +.02 (noise) | +.86 | top DNs DNp04/02/03/01 (leg/escape) |
| odor olfactory (8)       | .0035 | +.01 (noise) | +.25 | top DNs DNc01/02 (neck) |
| touch cord-mechano (2)   | .0284 | +.99 | +.96 | top DNs DNge104/122, DNxl114; motor mean +88%, turn -.023 |
| touch, DN->motor CUT     | .0283 | +.99 | — | peak .0582 -> .0562 = cut costs 3.4% |
| ctrl random-VP (8)       | —     | —    | +.72 | ctrl vs looming .32, looming vs odor .09 |

Amp sweep 1..30 FLAT: LC cells saturate by step ~5 — downstream response
is wiring-limited, not amplitude-limited.

Verdict (layered, honest):
1. REPLACEMENT WORKS for cord-origin commands: a cord mechano event
   drives a REPRODUCIBLE motor-population command through real wiring
   (self-cos .987, motor mean +88%, L/R turn asymmetry) — the linear-head
   stand-in is retired for this event class.
2. Brain events (looming/odor) do NOT survive to reproducible motor
   vectors at this fidelity (self-cos = noise; deflection 8x smaller):
   in-degree normalization dilutes a focal ~4-hop brain path below motor
   noise. They ARE reproducible and event-distinct AT THE DN PORT
   (.86/.96 self; .09 cross-modality; .32 within-visual) with
   biologically apt responders — the female L7 cx_intent shape (read the
   port, not the muscle) is the right readout for brain-origin commands.
3. The 23,616 direct DN->motor edges carry only ~3.4% of the cord motor
   command (cut test): at this fidelity DN->motor is modulatory; the
   cord-intrinsic arc (vnc_sensory->intrinsic->motor, 512k edges) owns
   the fast gait command — consistent with DNs gating cord programs.
Prototype scope: single graph, no null ensemble yet (no structure claim).
No live changes. Artifacts: malecns/{l11_dn_motor,l11_sweep,l11_vectors,
l11_controls}.py, l11/{results_l11.json,vectors_l11.json,cut_touch_motor.npy}

## L13 — malecns-gait-v2: synapse-scale pathway weighting (tick 24, 11-10)

Question: L11 showed brain events die below motor noise (in-degree dilution;
direct DN->motor = 3.4% of cord command). Can PER-SYNAPSE pathway weighting —
multiplying the real DN->motor synapses by g — let a looming/odor volley
produce a REPRODUCIBLE (self-cos >.5) and EVENT-DISTINCT motor vector?
This is engineering, not biology: testing whether the connectome CONTAINS a
usable pathway once flat synapse weights are freed (real DNs gate cord
programs; flat-weight connectomes may undercount their effective drive).

Setup: male_graph.pt, L11 op point (gain .8846, af .163), l11 seeds 11/22/33,
events looming (LC4/16/11/12, amp 8) vs odor (olfactory 2,639, amp 8),
motor-vector = X_peak(motor) − X_base per run, cos across 3 noise seeds.

### a) FLAT gain on ALL 23,616 DN->motor edges (l13_gait_v2.py)

| arm                | motor tonic | looming self | odor self | loom~odor | DNp01-04 clamp (loom) |
|--------------------|-------------|--------------|-----------|-----------|-----------------------|
| base g=1           | .0308       | +.023        | +.008     | +.259     | —                     |
| g=20               | .0666       | +.566        | +.097     | +.250     | —                     |
| g=200              | .3864       | +.928        | +.371     | +.280     | .859 — does NOT kill  |
| g=200 edgecut      | .0290       | +.008        | —         | —         | — (edges carry it)    |

Flat gain WORKS for reproducibility but is NON-SPECIFIC: clamping the 8
DNp01-04 cells leaves self-cos .859 — the carrier is the BROAD DN
population's event lift through the amplified edges, not the class volley;
and motor tonic inflates .031→.386 (flat gain amplifies spontaneous DN
drive as much as the volley).

### b) PER-DN-CLASS gain — only DNp01-04→motor (118 edges, w-sum .27) and
DNc01/02→motor (60 edges, w-sum .07) amplified (l13b_perclass.py)

| arm @g=200   | looming self | odor self | loom~odor | clamp DNp01-04 | clamp DNc01/02 | motor tonic |
|--------------|--------------|-----------|-----------|----------------|----------------|-------------|
| value        | +.971        | +.672     | −.002     | +.018 (dead)   | +.008 (dead)   | .0339       |
| @g=2000      | +.998        | +.981     | −.044     | +.137 (dead)   | −.082 (dead)   | .0614       |

Verdict: PATHWAY WEIGHTING WORKS, and only the per-class form is honest.
- Reproducible: looming self-cos .971/.998 (g=200/2000), odor .672/.981 —
  gate >.5 passed at both gains.
- DISTINCT: loom~odor cos −.002/−.044 — essentially orthogonal patterns.
- CUT/CLAMP: silencing the 8 DNp01-04 cells kills the looming motor signal
  (.971→.018); silencing DNc01/02 kills odor's (.672→.008); L13a edgecut
  (zero the engineered set) also kills it (.008). The signal rides the
  engineered class-specific path, NOT diffuse leakage. ✓ verify line met.
- Cheap tonically: motor baseline .0339 vs .0308 base (vs .3864 flat).
- The wiring picks the anatomy, not us: looming lands on TTMn (jump muscle
  MNs), Ti extensor/sternal rotator/i1 MNs (leg joints), DLMn/DVMn (flight)
  — biologically apt escape machinery reached through the REAL DNp01-04
  edges; we scaled weights, never chose targets.
- Steering is present but weak vs the cord reflex: looming turn −.0073/
  −.0127 (g=200/2000) vs cord mechano −.023 (L11).

Frame: the flat-weight male connectome UNDERCOUNTS DN→motor drive; ~118
real DNp01-04 edges ×200 (mean w .0023→.46, still below the cord arc's
typical synapse) is enough for a reproducible, orthogonal, class-routed
motor command — consistent with DNs as GATE/modulator of cord programs
(here: gain-scaled gate) rather than the fast path itself. No structure
claim (single graph, no null ensemble — the null question is now "does the
DNp01-04→TTMn channel survive degree-preserving rewiring", a natural L14).
No live changes. Artifacts: malecns/{l13_gait_v2,l13b_perclass}.py,
l13/{results_l13.json,results_l13b.json,run.out,runb.out}.

## L14 — null-duck the L13 gait channel (focused DN→motor block rewiring)

Design: Maslov-Sneppen destination swaps WITHIN the 23,616-edge DN→motor
block only — out-degree + out-strength per DN preserved (weights travel with
the source DN), in-degree per motor cell preserved, the other 25,536,463
edges (interior, sensory→DN routing) FROZEN, isolating the L13 claim. Same
per-class ×200 amplification re-applied per draw (118 leg + 60 neck edges,
asserted non-empty). 5 dynamic draws + 100 static draws; real reference
reproduced L13b exactly (self .971, cross −.002, same top-6). Operating
point stable across draws (global af .0393, sd 7.6e-8 — no re-bisect needed).

Static enrichment (100 draws, weights with sources):
| class      | real top-5 target types                        | w-frac real | null        | z     |
| DNp01-04   | DLMn c-f, TTMn, DVMn 3a-b, GNG651, DVMn 1a-c   | .499        | .061±.026   | +16.7 |
| DNc01/02   | MNml78, MNad03, MNad25, MNx04, MNad69          | .476        | .014±.022   | +21.0 |

Dynamic (5 draws, looming/odor × seeds, clamp DNp01-04):
| metric                  | real        | null mean±sd  | chance |
| looming self-cos        | .971        | .958±.002     | —      |
| loom~odor cross-cos     | −.002       | +.117±.030    | —      |
| clamp-kill \|dm\| ratio | .37 (L13b)  | .340±.002     | —      |
| anatomy cos vs real     | —           | .171±.024     | ~0     |
| top-6 \|dm\| mass       | .205        | .022±.017     | .0074  |

Verdict — the L13 result splits cleanly:
- REPRODUCIBILITY is BULK: self-cos .958 survives complete rewiring of the
  block — any fixed amplified edge set gives a seed-stable vector. Gain +
  source-class volley carry it, not placement.
- ORTHOGONALITY is MOSTLY bulk: cross +.117 vs −.002 real — random targets
  overlap by chance; the real placement keeps the two class channels disjoint.
- The GESTURE (anatomy) is WIRING: loading on the real top-6 collapses to
  near-chance (.022 vs .205, ~10×, chance .0074); null top responders are
  random motor cells (ps2 MN, MNad26, GNG283, b3 MN…), never the jump set;
  static enrichment z=+16.7/+21.0 — DNp01-04 genuinely targets the
  giant-fiber jump/flight power MNs (TTM/DLM/DVM muscles), DNc01/02 its own
  neck/leg MN set.

Frame: the per-class GATE works on any same-degree wiring, but WHAT it gates
— a coordinated jump vs a random twitch — is carried entirely by the real
DNp01-04 placement. Gate = bulk, gesture = wiring. Methodological rule for
pathway nulls: self-cos survives any fixed edge set, so reproducibility can
never credit wiring alone — the placement claim needs the loading-profile /
enrichment test. No live changes. Artifacts: malecns/l14_null.py,
l14/results_l14.json.

## L15 — escape-gesture-time: is the gesture's TEMPORAL structure wiring-carried? (tick 26, 11-10)

Question: L14 said WHICH cells load is wiring; does that anatomy also carry
TIME structure — family sequencing (jump then drive), sustained-vs-transient
phases, L/R asymmetry through time — or is time another gain-carried bulk
dimension at rate-model fidelity?

Protocol (l13b machinery verbatim, g=200, amp 8, gain .8846): looming volley
60 steps (0.6 s) + 180 decay; record the FULL motor difference tensor
(815 cells x 240 steps). Real x3 seeds vs 5 l14-style focused-null draws
(rewired DN->motor block, same per-class amplification, 118/60 asserted).
Family masks FROZEN from the real profile: jump = TTMn/DLMn/DVMn (26 cells);
drive = next-loaded 20 (GNG650/651, MNhm03/42, MNwm36, CvN5, sternal
rotator — the real top6 at x200 is TTMn x2 + GNG651 x2 + GNG650 x2).
Crude 2D path (v=mean motor dm, omega=L/R asym) as DESCRIPTOR only.

Anchor: exact l13b peak protocol reproduced .971 (pipeline verified).

Results:
- space-time self-cos (whole cells x time tensor): real .914 vs null
  .865±.006 — reproducibility again mostly gain-carried (real edge +.049).
- top-6 loading MASS SHARE through the whole tensor: real .0949 vs null
  .0140±.0075, chance .0074 — L14's static anatomy claim holds
  time-integrated (~6.8x null, ~12.8x chance). The wiring specifies WHICH
  cells, for the entire gesture.
- family TIMING: no reliable sequencing anywhere. Real leads (drive minus
  jump t_peak): +2/+10/+0 steps — not sign-consistent; null draws
  -13..+19, draw-idiosyncratic. Both families peak within a few steps of
  event end (real t_pk 49-61).
- DECAY: half-times 72-73 steps in EVERY run, both families, both arms —
  the decay phase is tau-carried (homogeneous TAU=0.05 s), zero family or
  arm structure. Sustained-vs-transient is not in this edge set.
- crude path: net displacement .0044 and straightness .9995 IDENTICAL
  across all arms; heading change is seed noise (-1.2..+0.9 rad) — the
  descriptor is uninformative at this fidelity, reported as such.

Verdict — TIME IS BULK at rate-model fidelity: with homogeneous time
constants, the DN->motor edge set cannot carry gesture phases; the only
time-domain wiring signature is the persistent ANATOMY (top-6 mass), which
specifies which cells act, never when. Gate = bulk, gesture-cells = wiring,
gesture-TIME = not in this substrate. Implication for the endgame card
(learned locomotion from CX/locomotor populations): sequencing must come
from (a) the CORD REFLEX ARC's multi-hop dynamics (L11: vnc_sensory ->
intrinsic -> motor owns fast gait) which the DN channel gates, or (b)
per-class time constants — not from DN->motor edge placement alone.
Natural follow-up card (L16): does the cord arc produce family-sequenced
phases (e.g., swing/stance alternation across antagonist leg MN pairs)
under the L11 cord event, i.e., is the TIME structure sitting in the
interior cord wiring we froze in L14? No live changes (CPU-only, 8
threads, live duck untouched). Artifacts: malecns/l15_gesture.py,
l15/results_l15.json, l15/gesture_mats.npz.

## L16 — cord reflex arc: does the INTERIOR carry gesture TIME? (tick 27, 11-10)

Question (the L15 card): L15 showed the looming (brain) path cannot
phase-sequence; is the TIME structure sitting in the cord reflex arc
interior (vnc_sensory -> intrinsic -> motor) that L11 made reproducible
(peak self-cos .987) and L14 froze? The MaleCNS type vocabulary names the
actual antagonist pools — Ti flexor (84 cells + Acc.) vs Ti extensor (12),
Tr flexor (57 + Acc.) vs Tr extensor (11) — the swing/stance substrate.

Protocol (l16_cordtime.py; l15 machinery, cord mechano event amp 2.0,
EVENT 20 + POST 220): full 815x240 motor difference tensor, 3 seeds real
vs 5 draws of a FOCUSED INTERIOR null — MS swaps on the 2,189,125-edge
interior block (sensory->intrinsic 357.8k + intrinsic->intrinsic 1.83M,
~16.6M swaps/draw), weights travel with source, ALL 187,916 edges INTO
motor (intrinsic->motor + sensory->motor + DN->motor) and everything
outside the cord FROZEN — the readout boundary is preserved (Dhiman/Park
lesson). Anchor: L11 cord peak self-cos reproduced EXACTLY (.987).

Results:
- NO antagonist sequencing in EITHER arm. Flexor and extensor pools of
  the same joint peak at the SAME step (t_pk 20-21 = event end, leads
  [0,-1,0]/[-1,+1,0] not sign-consistent; nulls 0/5 both pairs, leads
  <=1 step). No reciprocal-inhibition anti-phase: demeaned xcorr min
  -0.035 (Ti) / -0.054 (Tr) real vs -0.029/-0.044 null — noise floor.
- ONE temporal component everywhere: PCA var1/var2 = .956/.013 real,
  .963/.017 null. The cord motor response is a single lump in time.
- BUT the real interior carries a wiring-specific TEMPORAL SMEAR: per-cell
  t_pk spread (top-200 loaded, sign-corrected) 21.3 real vs 13.0±0.6 null
  (+63%); decay half-time spread 6.8 vs 2.0±0.1 (3.4x). And comp2 —
  1.3% variance — separates Ti flexor from extensor loadings at +0.62 z
  real vs -0.21±0.02 in EVERY null draw (sign flip): real antagonist
  pools do not ride the lump identically, but it is a whisper, not a phase.
- Anatomy through the frozen boundary: top-6 = Tr flexor MN x3 + Fe
  reductor MN x3, mass 3.37 real vs 2.69±0.02 null (real interior adds
  ~25% concentration on top of the boundary's). st self-cos .850 real vs
  .900±.001 null (real structure adds specific variation; lumps reproduce
  trivially — the L15 pattern again).

Verdict — the cord interior does NOT phase-sequence at homogeneous-tau
rate fidelity: simultaneous antagonist recruitment, no anti-phase, one
time course. What the real interior wiring DOES buy is the ENVELOPE'S
WIDTH (when-cells-act spread) and a weak flex/ext distinction — wiring
smeares time, never orders it. With L15 this closes the placement
question from both sides (brain path and cord arc): a first-order rate
model with uniform tau cannot express swing/stance phasing no matter
which edges carry it — the missing ingredients are KINETICS (per-class
time constants, adaptation) or delays, not more wiring. L17 card: tau
tiers on MN pools (both assignments tested, tau-map shuffle null); note
the fidelity ceiling honestly — real CPG phase structure lives in
nonspiking premotor interneurons, plateau currents and conduction delays
that this model class does not represent. No live changes (CPU-only 8
threads; live duck starved to 000 once under load, PID 3637121
unchanged, 200 in 7.8 s at rest — verified starvation not crash).
Artifacts: malecns/l16_cordtime.py, l16/results_l16.json,
l16/cord_mats.npz, l16/run.out.

## L17 — MN kinetics tiers: the model class CAN phase once taus differ (tick 28, 11-10)

Protocol — l16 machinery verbatim (cord mechano event amp 2.0, 20+220
steps, gain .8846, 3 seeds) with a per-cell tau vector on the antagonist
pools only: base .05 everywhere; A1 fast-ext/slow-flex (tau .02/.20, the
bio-suggested direction — extensor tibiae = phasic power muscle), A2 the
reverse, and 5 tau-shuffle draws (A1's multiset 23 fast / 141 slow
permuted across the 164-cell pool union). Homogeneous arm = the L16
anchor: leads [0,-1,0]/[-1,1,0] EXACT reproduction, no sign-consistency.

Result — per-class taus DO create antagonist phasing, and the sign
follows the assignment:
- A1 (fast ext): Ti lead −6.3 steps [−7,−6,−6], Tr −5.3 [−6,−5,−5] —
  3/3 seeds sign-consistent BOTH pairs; extensors peak ~60 ms early.
- A2 (fast flex): +6.3 [6,7,6] / +6.3 [6,7,6] — 3/3, exactly opposite.
- Shuffle null: Ti max|lead| 3.7 (sc 3/5, draw-luck on the 12-cell ext
  pool), Tr max 2.0 (sc 1/5) — BOTH assignments clear the null max on
  BOTH pairs; null leads are small and draw-idiosyncratic.
- Response width is tau-carried as expected: A1 Ti half-time flex 48 /
  ext 29 steps (homog 32/33 identical); xcorr dips only mildly negative
  (−.075/−.119) — this is a LEAD, not reciprocal-inhibition anti-phase.

Verdict — the phasing was never missing from the wiring; it was missing
from the MODEL CLASS. The same connectome that cannot phase at uniform
tau produces a sign-consistent, assignment-directed swing/stance-style
lead the moment antagonist pools carry different time constants —
L15/L16's "kinetics not wiring" card closed from the constructive side.
Honesty rails: tau values are FREE PARAMETERS chosen for 10x contrast,
not measured MN time constants; which pool is fast is biology OUTSIDE
the edge list; and a first-order lead is still not CPG anti-phase
(nonspiking premotor + plateau currents + delays remain outside the
class). For a biology-facing gesture, measured per-family MN/muscle
kinetics is the parameter source, and the tau-shuffle null stays the
control. No live changes (CPU-only, 8 threads, 311 s).
Artifacts: malecns/l17_kinetics.py, l17/results_l17.json,
l17/mean_tensors.npz, l17/run.out.

## L18 — literature-tau calibration (tick 30, 11-10)

Question (queue): does a BIOLOGICAL tau gap still clear the tau-shuffle
null, or does L17's phasing live only at unrealistic 10x contrast?
Anchors from the tick-29 field digest: TDT (the muscle TTMn drives)
RELAXATION tau ~51 ms is the only MEASURED class number (resolvable at
DT 10 ms = 5 steps); the TDT TWITCH is <5 ms = SUB-STEP at DT 10 ms (the
resolution floor: any jump-family lead needs DT 1-2 ms); per-muscle
activation taus are UNMEASURED by the field (2509.06426 used literature
defaults) so the tonic/slow side is swept at ratios 2/3/5x, labeled
underdetermined; IFM (DLMn/DVMn, 24 cells) is asynchronous — neural
drive does not time its contractions, so those MNs keep base tau and are
EXCLUDED from the fast family (L17 gave jump kinetics to all of
TTMn+DLMn+DVMn; corrected here).

Arm A (DT 10 ms, decay side, L17 protocol): ext = 51 ms (measured),
flex = 51*r ms. homog anchor reproduced EXACTLY ([0,-1,0]/[-1,1,0], af
.1638 = L11's bisected op point, stable across every arm). Emergence is
monotone in the tonic ratio: 2x -> Ti/Tr leads -1.7/-2.0 (3/3 sc), 3x ->
-3.7/-3.3 (3/3), 5x -> -5.7/-6.0 [-5,-7,-5]/[-6,-6,-6] (3/3 sc both
pairs); lit5rev = +6.0/+6.3 exactly sign-opposite. Tau-shuffle null (5x
multiset, 5 draws): Ti max|lead| 2.7 (sc 2/5), Tr max 3.0 (sc 2/5) —
the biological 5x gap CLEARS the null with margin; halves are
tau-carried (lit5x Ti flex/ext 53/33, rev swaps to 32/52). Caveat
logged: the 2x/3x arms are sign-consistent but their MAGNITUDES sit
inside the 5x-drawn null max — the null multiset must match the arm
(stricter nulls for small gaps not run, cost).
GATE PASSED at the biological anchor: phasing survives realistic
contrast on the decay side.

Arm B (DT 2 ms downshift, twitch side): TTMn (2 cells) tau 4 ms,
leg pools 51 ms. homog: jump-vs-leg leads [-30,+10,+40] NOT
sign-consistent (uniform tau = no family timing, anchor holds); af
.1488 identical in both arms. lit: leads +137.7/+142.0 steps 3/3 sc vs
null max 8.0/11.7 (sc 0/5) — the gate clears, but read the SIGN: this
is a LAG, not a lead. With tau 2 steps, TTMn stops being an integrator
and becomes a faithful REPORTER of its drive — and the drive reaching
TTMn through the uniform-50 ms interior peaks at steps [172,164,233]
(330-470 ms, ttm half 191) while the leg pairs peak ~40-60 steps: the
cord-interior smearing (L16's agent) DELAYS the jump-MN drive. A fast
jump contraction gated by this arc would fire LATE — this event class
(cord mechano, amp 2) carries no escape-jump temporal ordering. Family
contrast also changes the within-joint picture: Ti pair leads [1,1,8]
~simultaneous both arms = co-activation (matches 2509.06426's
grooming co-act reading; antagonists alternate in locomotion only).

Verdict — the model's temporal resolution floor is pinned by DT: at
10 ms only the ~51 ms decay side is expressible (and a biological 5x
tonic gap is ENOUGH for sign-consistent antagonist phasing — L17's 10x
was generous, not necessary); at 2 ms the twitch side becomes
expressible but a fast tau makes the cell a drive reporter, exposing
that the interior — not the MN kinetics — sets jump-family timing (lag
+138 steps through uniform-tau premotor; per-class INTERIOR taus or
delays would be the next lever, model class again). No wiring claim:
graph identical in every arm, only taus moved; nulls are tau-shuffles.
No live changes (CPU-only 8 threads, A 407 s + B 266 s; one /needs 000
during the run was load-11 starvation, PID 3637121 unchanged, 200 in
1.6 s on retry).
Artifacts: malecns/l18_bio_tau.py, l18/results_l18_{A,B}.json,
l18/ttm_mean_tensor_B.npz, l18/run_{A,B}.out.


## L19 — full-chain escape gesture (tick 31, 11-11)

The first honest whole-path demo: ONE rollout strings every shipped link —
looming volley at LC4/16/11/12 (amp 8, 20 steps) -> DN port (read at ITS
peak) -> per-class amplified DNp01-04 x200 + DNc01/02 x200 edges (L13b
verbatim: 118 + 60 edges) -> lit5x decay-side taus (ext 51 ms MEASURED /
flex 255 ms) -> full motor cells-x-time tensor. 5 arms x 3 seeds + 5
tau-shuffle draws, CPU 387 s.

Chain integrity — every link's shipped metric reproduced INSIDE the chain:
- L11 DN port: self-cos +0.889 (standalone .86), cross loom~odor +0.093
  (.09); loading DNp01-04 0.189 vs DNc01/02 0.002 of |DN vector| mass —
  the event lands on the leg-DN port, event-distinct.
- L13b motor peak: loom self +0.976 (.971), odor self +0.711 (.672),
  cross -.008 (-.002, orthogonal), clamp-DNp KILLS self to +0.025 (.018)
  — the command rides the engineered class path, not leakage.
- L14/15 anatomy: top-6 time-integrated mass 0.0722 vs chance 0.0074
  (~10x; L15's real-wiring number was 0.0949 — same family); top cells
  TTMn x2, GNG651 x2, GNG650 x2 = jump muscle reproducibly first.

New findings:
1. JUMP-FIRST through the direct path: TTMn t_pk [22,23,23] vs leg pools
   [23,29,26] every seed. L18B's +138-step jump LAG was a ROUTE property
   (uniform-tau interior smearing); the amplified direct DNp01-04 edges
   bypass the interior and deliver the jump command first. Route, not
   kinetics, sets family timing — now shown from both sides.
2. PHASING NOT EXPRESSED — mechanistically. lit5x leads Ti [0,-2,-13],
   Tr [-20,-81,-41], not sign-consistent, null max|lead| 71/104: gate
   FAILS. Pool amplitudes (seed-mean tensor, tail-noise floor 0.0016):
   TTMn 239x, Ti ext 8.9x, Tr ext 5.2x — but Ti flex 1.7x, Tr flex 1.5x
   = AT NOISE. L14 predicted it: DNp01-04 targets jump/extensor MNs; the
   descending escape route drives a POWER STROKE (TDT/TTMn + extensors)
   and never drives the flexor pools. Tau-tier phasing needs BOTH
   antagonists driven — it expressed in L17/L18's cord reflex arc (both
   pools driven) and cannot express here, because there is no antagonist
   alternation in this route to phase. Matches the fly: the escape-jump
   crouch (flexor wind-up) is a separate preparatory program; the looming
   DN volley carries the extensor power stroke.
3. The gesture: monophasic jump-first stroke, reproducible anatomy,
   event-orthogonal, clampable. theta(t) = ext - flex is a single hump
   (peak step 23) — a one-joint sketch, not a locomotion claim.

Figure: l19/gesture.png (three panels, SNR legend; vision-verified
legible, nothing clipped). Artifacts: malecns/l19_chain.py, l19_pools.py,
l19_fig.py; l19/{results_l19.json, gesture_mean.npz, pool_amplitudes.json,
run.out, gesture.svg, gesture.png}. No live changes; duck healthy
(PID 3637121 unchanged, /needs 200 — one 26 s answer under the owner's own
load before my run started).

## L20 — crouch-then-jump: the flexor DN channel exists and composes (11-11, tick 32)

Stage 1 STATIC scan (l20_scan.py; 100-draw Maslov-Sneppen destination-swap
null on the 23,616-edge DN->motor block, weights travel with sources):

- Flexor-targeting DN classes EXIST — a DNg family: DNg105 (52.7% of its
  motor weight onto Ti/Tr flexor MNs, z +24.9), DNg95 (80.1%, z +19.5),
  DNge079 (51.9%, +19.4), DNg74_b (41.2%, +17.5), DNg35 (59.1%, +16.4),
  DNg108 (42.4%, +15.1) — each a 2-cell bilateral pair; 15+ types at
  z >= +10 (>=5 block edges).
- DNp01-04 reference is jump-pure: DNp01 100% jump weight (flexor z -0.4),
  DNp03 44.6% jump + flexor DEPLETED (z -3.0). Clean double dissociation:
  DNp = extensor power stroke, DNg = crouch candidates.
- Block-level flexor weight share 2.89% observed vs 6.74% null — flexor
  targeting is globally DEPLETED in mass terms; the DNg signal is
  PLACEMENT enrichment (L13/L14 frame: flat weights undercount DN drive).
- Upstream of DNg105/DNg95/DNge079 (1,677/504/1,754 in-edges):
  vnc_intrinsic + ascending + DN/motor recurrency; essentially NO sensory
  classes (1 unknown_sensory edge in 1,754). The crouch program's drive
  lives upstream of the DNs — so stage 2 volleys the crouch DNs DIRECTLY
  (optogenetic-style, labeled as such).

Stage 2 DYNAMIC (l20_crouch.py; l19 machinery verbatim — lit5x taus,
x200 on 378 DNg{top6}->flexor edges + 118 DNp01-04->motor edges, both
edge sets asserted non-empty; CPU-only, 363 s):

- SNR GATE (L19 rule, measured FIRST): PASS — crouch volley drives
  flexors 25.1x the tail noise floor (L19 undriven: 1.5-1.7x); clamp-DNg
  kills it to 1.5x. Ext 6.3->4.2x and TTMn 7.3->7.4x under clamp = noise
  max-statistics + DNg's small flat extensor share (7-8%): the crouch
  channel is flexor-specific.
- Double dissociation: crouch-only = pure trough (theta -0.0788, no swing
  +0.0027); stroke-only = pure swing (+0.0307, no dip -0.0013).
- Two-phase (crouch volley 20 steps -> DNp01-04 volley at DEL):
  DEL=60  BIPHASIC (trough -0.0788 @23 -> peak +0.0211 @80, TTMn t_pk 85)
  DEL=100 BIPHASIC, full swing recovery (+0.0288 ~ stroke-only +0.0307)
  DEL=30  SWALLOWED (peak +0.0027 = crouch-only level — the 255 ms flexor
          tau owns theta and the joint never extends; TTMn still fires at
          55: MN drive != joint angle)
- Reading: theta(t) = ext - flex is biphasic with the crouch BEFORE the
  jump, with an inter-phase refractory constraint set by the slow flexor —
  you cannot jump mid-crouch. TTMn t_pk = DEL+25 exactly (the direct
  amplified-edge route; L19's jump-first, now as a composed gesture).

Honesty labels: direct DN volleys (no sensory route into the crouch DNs
exists in this connectome at the 1-edge level); per-class amplified edges
(flat weights undercount DN drive); taus literature-calibrated decay-side
only (L18); DESCRIPTIVE — no locomotion claim (owner movement law).

Figure: l20/crouch.png (3 panels; vision-verified PASS after 3 fix passes
— the persistent panel-B strikethrough was panel A's theta sub-band using
the full panel height and spilling into B). Artifacts:
malecns/{l20_scan.py, l20_crouch.py, l20_fig.py}; l20/{scan_results.json,
results_l20.json, two_phase.npz, scan.out, crouch.out, crouch.svg/png}.
No live changes; duck healthy (PID unchanged, /needs 200).

## L21 — interior kinetics tiers: transit delay is PATH-INTEGRAL, no class shortcut (11-11, tick 33)

Question (queue): per-class taus on the cord INTRINSIC populations — do they
shrink the interior transit delay to TTMn at DT 2 ms (L18B: 172-233 steps =
344-466 ms), and can any tau make brain-origin ordering resolvable?

Classing: vnc_intrinsic (13,161 cells) has NO class column — only hemilineage
type names (~20-30 cells/type), so 'local vs projecting' is not annotated.
Graph-native classes = hop-distance-to-motor tiers via reverse BFS.
INSTRUMENT BUG caught by the never-reach control: a SIGNED-weight BFS drops
every inhibitory premotor cell (20.3% of the 226,486 direct motor in-edges,
46,010 edges) from the closure — reachability must use ABS values. With abs:
the cord interior is a 2-HOP SHEET (d1 10,826 / d2 2,316 / d3+ 0; only 18
intrinsic cells never reach motor). L18B's 344-466 ms therefore cannot be a
long tau-chain through the interior — the sheet is shallow.

(a) Transit, cord mechano event, TTMn with the measured 4 ms twitch tau as
drive REPORTER (L18B lesson), 3 seeds per arm, arm = which cells get tau 5 ms
(rest 51 ms; everything else = L18 base):
- uniform sweep u51/u20/u10/u5: TTMn t_pk [172,164/246,233] IDENTICAL in all
  four arms; u51-vs-u5 seed-11 trace corr .998, peaks .0116 both.
- tiers d1 (10,826 premotor incl. inhibitory) / d2 / far (18): flat.
- asc+DN fast (3,160 cells): flat. Random 2,316-cell draws (2 accidental):
  flat. u51 reproduces the L18B anchor family (2/3 seeds exact; seed-2 246
  vs 164 — our leg pools carry the reporter tau, L18B's did not).
- WHOLE-GRAPH 5 ms: collapse — TTMn t_pk 7-17 steps (14-34 ms), leg 16-19,
  TTMn LEADS leg +3/+9/+2 (sign-consistent); af shifts .1485->.1781
  (faster cells average higher instantaneous activity; op-point note).
VERDICT (a): the interior transit delay is a PATH-INTEGRAL of ~9 distributed
base-tau stages (sensory -> sheet -> ascending -> brain -> DN -> motor); NO
single class shortcut exists in this model class. Interior kinetics tiers
are a dead lever for brain-origin gesture timing — the levers that move
timing are ROUTE (L19 direct edges: jump-first) and whole-graph kinetics
(outside biology; labeled underdetermined model-class exploration).

(b) Brain-origin (looming LC4/16/11/12 volley, amp 8):
- b1, NO amplification (bulk interior route): pool SNR vs tail floor
  ttm 10.5x / leg 10.9x — flat across tau 51/10/5. Pool-mean amplitude SNR
  is a DIFFERENT quantity from L11's motor-vector reproducibility (which
  died at this fidelity): the diffuse wake lifts pools above per-cell noise
  while remaining non-reproducible in vector space.
- b2, L19 amplification ON, DT 2 ms: DN port peaks SLOW (47-50 steps =
  94-100 ms; LC->DN through base-tau brain) and TTMn tracks it within 1-4
  steps (direct route, L19 confirmed at fine clock). Inter-pool ordering
  margin (leg - TTMn): full-window [-3,-12,197] not sc; early-window
  (direct component, first 100 steps) [-3,-12,41] not sc — L19's DT-10ms
  jump-first sits AT the resolution limit; at DT 2 ms the margins fall
  inside seed noise, tau-insensitive.

Honesty labels: interior taus are free parameters (field has not measured
cord interneuron membrane taus — sweep spans 51->5 ms, only the 51 side is
anchored); reporter tau on monitored MN pools is an instrument choice;
DESCRIPTIVE only — no locomotion claim (owner movement law). Two control
arms earned their keep tonight: never-reach caught the signed-BFS bug, the
fast_cells count print caught a phase-dispatch bug (a3 ran 'rand' arms
twice before the fix; pilot outputs kept as *_pilot*.out).

Figure: l21/delay.png (3 panels, vision-verified PASS, 2nd pass). Artifacts:
malecns/{l21_tau.py, l21_fig.py}; l21/{results_l21_a0a1.json,
results_l21_a3.json, results_l21_b.json, traces_l21_*.npz, run_*.out}.
No live changes; CPU-only; duck PID 3637121 unchanged, /needs 200 (one 000
under load-5.7 gaming starvation, 200 in 0.83 s on retry).

## L22. dn-route-atlas — the DN->motor gesture vocabulary (tick 34, 11-11)

Question (LANE ideas-8): convert our one-off route findings (L13 DNp01-04
jump, L20 DNg crouch) into the connectome's full gesture vocabulary.

Method: for every DN type with >=2 cells present in the 23,616-edge DN->motor
block (443 rows; 391 with >=5 edges = 99.5% of block weight), weight profile
over all 185 destination motor TYPES, each cell enriched against a 300-draw
Maslov-Sneppen destination-swap null (l20_scan.rewire_block verbatim: degrees
kept, weights travel with source DN, so per-type out-weight totals are
invariant and shares comparable). l22_atlas.py, CPU-only, 76 s.

Results (l22/atlas.csv, 391 rows; results_l22.json):
- Purity: 36 PURE channels (top-1 target >=50% of the type's motor weight),
  145 mixed (>=25%), 210 diffuse. 365/391 types have a top-1 target that is
  both >=10% weight and z>=+5 over the null — target specificity is the
  NORM, not the exception, in this block.
- New channels the route work can cite (share, z, all >=5 edges):
  * flight power: DNg110 -> DLMn c-f .33 top1 (jump-family share .77,
    z +34.8) — a second jump/flight channel besides DNp01-04.
  * ltm (ltm MN): DNb08 .74, DNg43 .69, DNg63 .49 — tibia/femur long-tendon
    channels, PURE-ish.
  * Fe reductor: DNge009 .60 PURE (z +23.5), DNge068 .59 — femur reductor
    family with its own DN classes (postural?).
  * abdominal (MNad*): the single biggest vocabulary — DNd04 -> MNad55 .80
    PURE z +51.3 (the atlas max), DNp43 -> MNad55 .68 z +47.6, DNp46, DNp65,
    DNg33, DNpe034... a large dedicated abdomen-gesture subsystem.
  * head/thorax turn: no neck/cervical motor types exist in the block at
    all — L13's "DNc01/02 neck" label was nomenclature, not motor anatomy;
    the atlas gives DNc01 -> MNad25/MNx04, DNc02 -> MNml78 .30 z +11.6
    (mesothoracic leg + abdominal). The L13 orthogonality claim stands (it
    was measured); the channel NAME gets this correction.
- Family channel counts (share >=.10 AND z >= +5): jump 22 types, flexor
  39, extensor 12. Flexor vocabulary is much richer than the crouch six
  from L20 (DNg105 .53 z+19.5, DNg95 .80 z+18.4, DNge079 .52 z+18.1,
  DNge035, DNg93 .38 over 453 edges, DNa01 .59, DNg14, DNg31, DNg12_e...).

Anchors (verify line): DNp01-04 CLASS-pooled jump share .491 z +15.9
(PASS >=15; L14's original +16.7 at 100 draws) — per-type DNp01 is share
1.000 but z +6.3 (6 edges, noisy; class form is the anchor form). DNg105
per-type flex .527 z +19.5 (PASS; L20's +24.9 at 100 draws, different
rng — same verdict). Gate PASS.

Instrument notes (two first-pass bugs caught by the anchors themselves):
family z must pool the share PER DRAW then take std (std of a sum, not sum
of stds — sum-of-stds understated z x2.5); per-cell z where the 300-draw
null NEVER hits a rare motor type had std 0 -> z 1e8, floored by a
binomial SE sqrt(p(1-p)/E_eff) with E_eff = (Sw)^2/Sww (40,594/83,065
cells floored; conservative — binomial SE overstates MS-swap variance,
l20 draw z +24.9 vs binomial +10 — so the floor only shrinks inflated z).

Artifacts: malecns/l22_atlas.py; l22/{atlas.csv,
results_l22.json, atlas.out}. No live changes; CPU-only.

## L23. route-composition — simultaneous DN routes superpose (tick 35, 11-11)

Question: L20 composed crouch->stroke SEQUENTIALLY; do two class-amplified
DN routes fired at the SAME ONSET stay orthogonal (L13 cross-cos -.002) or
interfere? Protocol: L13b substrate verbatim (DNp01-04 x200 + DNc01/02 x200
in ONE brain, 118+60 edges asserted), looming amp 8 (route A) + odor amp 8
(route B), 3 seeds; SNR gate FIRST (L19 rule); deliverable = cross-cos table
joint vs solo + clamp controls; both dm forms (L13 peak-snapshot AND
window-averaged dm_int — the fair readout when routes peak at different
steps: t_pk A 22-24, B 18-26).

SNR gate PASS on every route-owned pool: TTMn 26.4x, extensor 6.8x (A);
MNml78 20.8x, MNx04 12.2x, MNad03 5.4x, MNad25 5.2x (B) — vs L19's
mechanically-undriven 1.5-1.7x.

VERDICT: SUPERPOSITION — the L22 atlas behaves like an orthogonal basis at
the motor port, at both L13b gains:
* solo~solo cross-cos A~B: -.002 (dm) / +.016 (dm_int) — L13's -.002
  reproduced exactly.
* cos(dJoint, dA+dB): +.987/+.983 at G=200 (resid .163/.185, |dJ|/|dS|
  .982/.960 = ~2-4% SUB-additive); +.999 at G=2000 (resid .056, ratio 1.019,
  cos(A,B) -.044). Motor saturation 0.000 (G200) / 0.006 (G2000) — the
  nonlinearity that could couple routes never engages at the motor end.
* Per-pool interference joint/solo: 1.00-1.03 on ALL six pools — each
  route's landing zones are untouched by the other route firing
  simultaneously. Cross-route leak 0.006-0.012 ~ 1-2x the pool noise floor.
* Clamp controls: joint-with-DNc-clamped ~ soloA cos .981/.974 (= A's own
  self-cos .981/.974 — removal recovers the solo EXACTLY); joint-with-DNp-
  clamped ~ soloB cos .765/.736 (= B's own self-cos .781/.736 — recovered to
  B's reproducibility ceiling, not below it). Clamped route is gone from the
  joint (jClampA~soloA .036). killA anchor: looming+clamp-DNp dm_mag .0035
  vs soloA .0095 (L13 clamp-kill form).
* Boundary notes: amp sweep is DEAD (a8 == a16 bit-identical at G=2000 —
  input populations are RMAX-pinned at amp 8; L11's flat amp sweep
  reproduced; gain is the live lever, and superposition survives to G=2000).
  The G=200 residual (.163) lives in the SHARED INTERIOR (rectification at
  interior cells driven by both routes) — un-decomposed here, open note.

Mechanism honesty: superposition here = anatomically disjoint motor targets
+ each route far from RMAX at motor. This is a statement about THESE two
routes at OUR fidelity/gains, not a general law — same-family routes (e.g.
DNg105+DNg95 both -> Ti/Tr flexors) share targets and must interfere BY
CONSTRUCTION; that is the next composition question (ideas 9, L25).

Artifacts: malecns/l23_route_composition.py, l23b_boundary.py;
l23/{results_l23.json, results_l23b_g2000_a8.json, _a16, _g200_a16, l23.out}.
No live changes; CPU-only 142 s + 3x ~55 s.

## L24 — steering-laterality (tick 36, 11-11)

Question (ideas 9): which DN classes own LEFT vs RIGHT leg motor; are L/R
homologues separate channels; does a unilateral volley turn the motor
vector; does a turn superpose with the jump route (L23 form)?

Static (l24_laterality.py; 500-draw motor-side permutation, 500-draw
within-type source-side permutation; motor somata 409 L / 406 R, matched
L/R pools for every leg type):
- NET laterality: NO type is side-lateralized — max |LI z| = 3.3 (DNd05,
  49 edges), zero types at |z|>=5. Per-type default is bilateral balance.
- MIRROR structure: the 344 bilateral types (>=10 edges, both L and R
  somata) are ~perfectly mirror-separated — each member projects
  essentially exclusively to ONE motor side (|LI_L| ~ |LI_R| ~ 1,
  opposite signs). Pooled ipsi fraction .633 vs null .503 sd .0098 =
  z +13.3 (L-soma->L + R-soma->R dominates the block).
- BOTH mirror organizations exist: IPSI (DNg95: LI_L +.958 / LI_R -1.000)
  and CROSSED (DNg105: -.961/+.963; also DNge117, DNg97 at -1). Not every
  channel mirrors: DNg110 (2nd jump/flight channel, 6 cells) is
  bilateral-diffuse (LI_L +.118 / LI_R -.145).
- SIGN discovery: DNg105 — L20's top flexor-z channel — has ALL 243 motor
  edges NEGATIVE (w-sum -1.52, max edge -.0004): an inhibitory CROSSED
  flexor channel. L20's crouch SNR was carried by the positive-weight
  classes (DNg95 +0.40, etc.). RULE: check a class's edge-sign total
  before volleying it.

Dynamic (l24_steer2.py; 8 arms x 3 seeds, G=200 per-class on DNg95/DNg105/
DNp01-04 -> motor, direct DN volleys amp 8 — L20/L23 optogenetic form):
- SNR gate PASS first (L19 rule): flexL 83.6x / flexR 121.0x.
- Unilateral steering: DNg95 L-cell volley -> STRICTLY ipsilateral flexor
  burst (flexL dm +.165, flexR +.0004 = noise floor); R-cell volley is
  the mirror (+.150). turn_flex sign-flip PASS 3/3 (+.65/+.71/+.71 vs
  -.98/-.92/-.93); turn_all +.46/-.47. Static ipsi prediction confirmed.
- Crossed inhibition arm: DNg105-L volley SUPPRESSES flexR (-.0033 vs
  noise +.0004) — real but FLOOR-LIMITED: the pool already sits near the
  relu floor, so the inhibitory push-pull arm has little dynamic range at
  this operating point. Push-pull (DNg95-L + DNg105-L): turn +.514 vs
  steer-only +.459 = gain 1.05, sign-consistent 3/3 (excitation dominates).
- Composition with the bilateral jump route: cos(dJoint, dSteer+dJump)
  +.999 (resid .034, both dm forms), turn_flex retained in joint 1.00,
  clamp-DNg95 recovers jump (cos .982, turn -> +.009), sat 0.000
  everywhere. L23's superposition extends to the L/R dimension: a
  turn-during-jump motor basis composes at rate fidelity.
- Instrument honesty: the strict per-seed "shape" check (flexR <= 0) was
  mis-specified against a +.0004 noise mean (prints 0/3) — margins must
  be noise-scaled; the side readout is unambiguous (~400x asymmetry).

Verdict: the steering vocabulary is MIRROR-SEPARATED L/R homologues
inside symmetric types — net LI ~ 0 is the straight-locomotion default,
not the absence of steering. The flexor family carries excitatory ipsi
mirrors (DNg95) AND an inhibitory crossed mirror (DNg105) = a push-pull
substrate, floor-limited on the inhibitory side at our operating point.
Unilateral volleys produce reproducible turns that superpose with the
jump route exactly (L23 form).

Artifacts: malecns/l24_laterality.py, l24_steer.py (v1 — the inhibitory-
channel lesson), l24_steer2.py; l24/{laterality.csv, results_l24_static.json,
results_l24_steer.json, results_l24_steer2.json}. No live changes;
CPU-only 4 s + 135 s + 183 s.


## L25. same-family-composition — shared pools break superposition GRACEFULLY (tick 38 + tick 40, 11-11)

Question: L23's superposing pair had DISJOINT motor targets; the honest
counter-test is same-family — two flexor DN routes into SHARED pools,
fired together. Prediction if composition breaks: sub-additive shared-
pool peak + RMAX ceiling onset; staggered onsets (L20 form) may rescue.

Provenance: tick 38 ran v1 (11 arms) at 10:32, edited the script 45 s
later (stag10/20 added) and never re-ran or journaled; tick 40 took the
stale claim, added the t-clip probe, re-ran all 13 arms — v1 numbers
reproduce exactly (soloA .2264 / joint .3439 / ratios .790-.792).

Route choice + STATIC SIGN FINDING: of L20's six crouch classes only
DNg95 (w +.403) and DNg35 (w +.526) are EXCITATORY onto flexors;
DNg105 / DNge079 / DNg74_b / DNg108 are ALL-inhibitory (flex w -.66 /
-.66 / -.96 / -.62) — L24's DNg105 sign lesson generalizes: the DNg
flexor family is mostly inhibitory, so an excitatory same-family pair
must be picked by sign, not by enrichment alone. B = DNg35 (positive
flexor weight, flex-type profile cos +.896 with DNg95 = genuine shared
pools). Amplified edges 84 + 110 = 194, asserted non-empty.

SNR gate (L19 rule): PASS — flexL 56.8x / flexR 57.4x.

MAIN RESULT — sub-additivity confirmed, graceful: joint/(soloA+soloB)
flexL 0.790 [seeds .790/.792/.790] / flexR 0.824 at G200; 0.754/0.777 at
G2000 — vs L23's disjoint-target 1.00-1.03. ~18-21% of the summed mass
is lost, but the vector stays clean: cos(dJoint, dA+dB) dm +.966 / dm_int
+.975 (L23: .987-.999), and clamp jClampA-vs-soloB cos +.999 — the joint
minus one route recovers the other's solo to ceiling; composition is
route-specific, no corruption, no diffuse leakage.

MECHANISM (t-clip probe, added tick 40): sat(X) = 0.000 at G200, yet the
PRE-noise t-ceiling fraction on flexL runs soloA .017 / soloB .019 /
joint .040 (≈ additive) — the RMAX clamp on the relu TARGET engages on
the most-driven cells while integrated X never shows it. A cell pinned
at t>=1 integrates toward X=1 no matter WHICH route (or both) drives it,
so the deficit concentrates in exactly the top-mass cells. At G2000 clip
rises to .159 and the solo peak DROPS .2264 -> .1373: past the ceiling,
more gain buys LESS pool-mean response (L11/L23's dead-amp lever, now
with the mechanism instrumented). First-order arithmetic: event-window
pinned fraction x ~.5 deficit/pinned cell ~ the observed .09 pool-mean
deficit — order matches, per-cell decomposition not run (labeled).

STAGGER (L20 form): B-window peak / soloB = DEL10 1.58 / DEL20 1.29 /
DEL30 1.02 / DEL60 1.00 / DEL100 1.00. Read twice: (a) short delays
INFLATE the windowed peak because B rides A's decay tail — a measurement
caution, not a gain (trace-max at DEL10 is .3307 < joint .3439, i.e.
staggering does NOT beat simultaneous on the max metric); (b) B's OWN
amplitude is fully restored once drives separate by >=30 steps (300 ms):
the interference is strictly co-temporal, no lasting occlusion.

Gain ceiling: sat(X) 0.000 (G200, all arms) -> G2000 soloA .055 /
soloB .072 / joint .101 (sub-linear vs .127 sum); pool-mean level
ceiling ~.43-.45, far from 1.0 — Sobol one-deciding-param (solo
headroom to RMAX) measured via lvl_max + clip.

Estimands (tick 37 amendment): all arms P1-form (per-class gain
re-applied on the real wiring) — valid for the additivity/magnitude
question; NO wins-claim made ("wiring prevents X" would need the P2
gain-re-tuned control). Scope: two positive classes of ONE family
(flexor); mixed-sign composition onto a shared pool (excite+inhibit =
push-pull) was L24's floor-limited case and is not re-tested here.

Consequence for the gesture card: overlapping same-family drives cost
~20% of the summed shared-pool mass; L20's crouch->stroke sequencing
(DEL>=60 steps) sits in the FREE regime; simultaneous same-family merge
is lossy but clean. Composition regime is decided by TARGET OVERLAP,
not DN-class identity (L23 vs L25 same machinery).

Artifacts: malecns/l25_samefamily.py; l25/{results_l25.json (tick 40,
13 arms incl. stag10/20 + clip), results_l25_v1_tick38.json (v1
provenance), run_tick40.out}. CPU-only 456 s, exit 0. No live changes;
duck /needs 200 throughout (one 28.9 s reply under run load, 1.8 s
after; PID 3637121 unchanged).



## L26 — ascending-echo: does the brain receive a copy of its own jump? (11-11)

The loop's unexplored half. Every prior item flows sensory->DN->motor
(descending); this asks the reverse: after the L19 jump chain, do
ASCENDING (cord->brain) populations carry a copy of the motor burst —
the electrical interoception route (L12's endocrine route measured dead).
Pool = `ascending_neuron` superclass, 1,846 cells (census also:
sensory_ascending 537, efferent_ascending 8 — kept out).

ANATOMY (claim-carrier, static):
- MNs DO have central out-edges: 22,885 edges from 815 MNs -> 8,494 dsts
  (total abs weight only ~54; the cord is recurrent, not feed-forward).
- Motor->ascending DIRECT: 1,024 edges, abs_w ~1.2 = 2.3% of motor-out
  weight — featherweight. ABS-reachability (L21 form): ALL 1,846 asc
  cells reachable in <=3 hops (524 d1 / 1,320 d2 / 2 d3) via
  vnc_intrinsic — the path exists structurally, end to end.
- Ascending IN-provenance (abs-w share): vnc_intrinsic .435, other asc
  .197, DESCENDING .129, vnc_sensory .117, cb_intrinsic .074 — asc
  cells integrate cord state + command, not motor output.
- Ascending OUT recipients: vnc_intrinsic .343, cb_intrinsic .264 (the
  brain-side landing zone), vnc_sensory .131 — the echo's consumer is
  central-brain intrinsic + cord sensory, not motor/DN.

DYNAMICS (P1-labeled per tick-37; l19_chain machinery verbatim):
- jump (L19 chain): asc pool lifts at SNR 6.9x (base .0281+/-0.0001 ->
  peak .0287), asc vector self-cos +0.208 — reliable POOL-MEAN lift,
  fine structure mostly seed-noise (L21 lesson: name which SNR you mean).
- jump_clampM (X[motor]=0 every step, L2 opto form): SNR 6.8x, self
  +0.208, cos_vs_jump +1.000 — PERFECT identity. The ascending signal
  is ENTIRELY motor-independent = a central corollary, not a copy of
  the movement.
- mnvolley (155 MNs driven directly at amp 8 — motor_pk .21 vs jump's
  .04, a 5x harder burst): asc SNR 2.9x, self-cos +.000, top-10 mass
  .0211 vs destination-swap null .0210+/-0.0002 (chance .0054) — the
  mass concentration is degree-skew, present in the null; NO
  reproducible motor-borne echo. In-degree dilution (L11 class).
- l26b jump_clampDN (the 12 amplified command DNs silenced): SNR
  6.9->5.8x, cos_vs_jump +.997 — the corollary is a DISTRIBUTED
  DN-population broadcast (12.9% of asc in-weight is descending), not
  carried by the jump-command cells specifically.

VERDICT: at rate fidelity the brain's copy of its own jump is a
COMMAND-LEVEL corollary (DN-borne, distributed, motor-independent);
the proprioceptive/motor-borne echo is anatomically complete (<=3 hops
to every asc cell) but dynamically unreadable — like the null-duck
split, feelings-as-drive vs structure-as-memory, now on the return
path. If the sim ever wants body feedback ("she feels her wings"), it
must be bridge-level body semantics (L12 form) — the real motor->asc
route cannot carry it at this fidelity. Sobol one-deciding-param:
per-class ASCENDING gains/taus (unmodeled; uniform gain assumed — a
high-gain asc pool could in principle amplify the diluted d1/d2 drive,
so scope the negative to "rate fidelity, uniform gain"). Amp dead-lever
not re-tested here (L11/L23 established); gain would be the lever.

Estimands: anatomy = structure claims; dynamics = P1-form; the
mnvolley negative is the conservative direction (re-tuned gains could
only ADD signal, never remove the null match).

Artifacts: malecns/l26_ascending.py, l26b_clampdn.py; l26/
{results_l26.json, results_l26b.json, asc_vectors.npz, run.out,
run_l26b.out}. CPU-only 378 s + 51 s. No live changes; duck /needs 200
throughout (slow only under box load).

## L27 — arousal-gated-escape: oct neither creates nor amplifies the gesture (11-11, tick 41)

Question: motor-side twin of the live duck's oct-is-arousal lesson — does
tonic octopamine, as a STATE, amplify the L19 looming escape route through
real wiring, and can arousal alone create a gesture?

CENSUS (existence claims; MaleCNS consensus_nt 'octopamine' = 101 cells):
- CENTRAL 51 (35 cb_intrinsic OA-AL/ASM + 16 visual_centrifugal, w 16.72):
  DN-ENRICHED (5.0% of out-weight, z +3.5 vs 5 random-51 central draws) but
  CORD-DEPLETED (vnc_intrinsic 0.0%, z -2.6), motor 0.01%; 9 direct
  oct->DNp01-04 edges (w .0029).
- PERIPHERAL 50 (49 vnc_efferent + 1 efferent_ascending, w 23.80): carries
  the oct->motor-system wiring candidates — 33% of out-weight onto DNs, 47%
  onto vnc_intrinsic, 1.1% DIRECT onto motor; zero direct DNp01-04 edges.
  The two oct populations have OPPOSITE target profiles.

DYNAMICS (P1-labeled; l19 machinery verbatim, lit5x taus, x200 per-class,
DT 10 ms, 3 seeds, baseline re-measured WITH the state on):
- ANCHOR reproduced exactly: loom TTM pk .3857, motor self-cos +.976
  (L19's .976), SNR 137x, af .1641.
- loom + octCENTRAL amp {1,2,4}: TTM ratio x0.999 (<=0.1% dip, sub-noise
  scale vs rand51 sd .0004), route vector cos-vs-anchor +1.000, self-cos
  unchanged +.976 — the escape route is NOT oct-amplified. rand51 states
  identical (mu 1.000). State is RMAX-pinned already at amp 1 (identical
  numbers across amps — L11/L23 dead-amp lever family).
- oct ALONE (the create-gesture check): TTM nudge .0098 = 2.5% of the
  looming gesture, SNR 3.3x, ext .0016 / flex .0001 — arousal cannot create
  the gesture: the live lesson TRANSPOSES to real motor wiring.
- l27b probes: octALL(101) alone is BIT-IDENTICAL to octC(51) (TTM .0098,
  DNp lift .0352, all pools equal) — the peripheral oct census weight onto
  cord/DN is in-degree-diluted below pool noise at this fidelity (L11
  class). clampDNp (X=0 each step, L2 form) halves the nudge
  (.0098->.0047, SNR 3.27->2.10): ~half rides the 9-edge DNp channel
  through the x200 gate; the residual ~2.1x sits near the undriven floor
  (1.5-1.7x) with DNc01/02 unclamped.

VERDICT: at rate-model fidelity oct arousal neither creates NOR amplifies
the escape route — escape gain is not oct-gated at the cord in this model
class; the live duck's "oct amplifies fear but never crosses threshold"
lives at the BRIDGE (body-level mood targets), not in this circuit readout.
The oct->cord wiring exists (peripheral census) but is undetectable at
population-pool fidelity. Sobol one-deciding-param: per-class oct synaptic
gains (unmodeled; flat connectome weights assumed).

Artifacts: malecns/{l27_arousal.py, l27b_probe.py}; l27/{results_l27.json,
results_l27b.json, pool_traces.npz, run.out, run_l27b.out}. CPU-only
495 s + 169 s. No live changes; duck /needs 200 throughout (slow under run
load, then normal).

## L28 — grooming-alternation: anti-phase DN drive DOES alternate antagonist pools; the flexor tau sets the rhythm ceiling (11-11, tick 42)

Question: L18's Ti-pair co-activation carried a "(grooming reading)" label
that was never tested AS grooming — drive the antagonist channels
ALTERNATELY at grooming-range rhythms and see whether the motor output
alternates or merges.

Static (claim-carrier; CSR convention W[target, source] — rows are targets
under torch.sparse.mm, cols are sources):
- A = DNg95 (2 cells) -> Ti/Tr FLEXOR MNs: net sign +0.322, 45 edges;
  extorsors 5 edges (+0.008) — flex/ext selectivity 41.9x.
- B = DNg79 (4 cells; backup DNge037 +0.098/22e also excitatory) ->
  Ti/Tr EXTENSOR MNs: +0.078, 24 edges; flexors 3 edges — 15.1x. Double
  dissociation, both net EXCITATORY (L24/L25 sign rule applied at
  SELECTION, before any volley). x200 on the class edges only (45+24,
  L13b form); direct volley on the DN cells (L20 optogenetic-style label).

Dynamic (P1-labeled; 3 seeds, DT 10 ms, lit5x decay taus ext 51 ms MEASURED
/ flex 255 ms underdetermined; square-wave half-cycle drive, 6-10 integer
cycles; alt (anti-phase) vs sim (in-phase control) at 1/2/5 Hz spanning
L25's 1.67 Hz co-temporal boundary):
- SNR gate PASS (L19 rule): soloA flex 816x, soloB ext 369x vs pool noise.
- ALTERNATION CARRIES: alt drive -> flex-vs-ext rel phase -134 / -129 /
  -132 deg at 1/2/5 Hz (per-seed spread +-1 deg); sim control +42/+46/+35
  deg. The ~175 deg alt-vs-sim contrast is drive-faithful at EVERY
  frequency: the cord does not merge antagonists given anti-phase drive.
  L18's co-activation was a DRIVE-PATTERN artifact (one event driving both
  pools), not a cord property.
- RHYTHM CEILING IS MOTOR-TAU: flex power-at-drive-f .98 -> .78 -> .09
  (1->5 Hz) while ext holds .88 / .82 / .33; flex amp@f collapses 5.3x
  (0.074 -> 0.014) vs ext 3.2x. Fast (5 Hz) grooming rides the extensor
  (51 ms) channel; the 255 ms flexor tau low-passes flexors out of the
  gesture — an honest model-class floor pinned to an UNDERDETERMINED
  parameter (L18: tonic-side flexor tau is swept, not measured).
- Phase never exactly 180 deg: the ~45 deg offset is the flexor's tau
  lag on its own half-cycle — tau-carried phase, consistent with L17/L18.
- alt-vs-sim amplitudes identical (x1.00 at all f): drive PHASE changes
  output phase, not output amplitude, at these frequencies.

Verdict: a leg-rub gesture trace is CARRIED by this model class whenever
the drive alternates at <=~2 Hz; at grooming-fast rhythm flexor
participation is tau-limited. Descriptive only (owner movement law);
capability claim, not wiring-exclusivity — no rewired null run.
Artifacts: malecns/l28_grooming.py, l28_fig.py; l28/{results_l28.json,
pool_traces.npz, grooming.svg, grooming.png (vision-verified PASS),
run.out}. CPU-only, 765 s. No live changes; duck /needs 200 (PID
3637121 unchanged; slow only under box load 15-18 from other lanes).

### correction to L27's static census (found while building L28)
l27_arousal.py's census() selected oct-as-ROW x class-as-COL; under the
CSR convention rows are TARGETS, so its "oct out-weight target census" and
"oct->DNp01-04 direct edges (9, w .0029)" are actually oct's IN-edge
provenance (DN->oct etc.). The z-enrichments stand as measured (same
estimator on the random draws) and every DYNAMIC arm of L27 is
convention-free (tonic input onto oct cells propagates through real
out-edges regardless) — the verdict (no create, no amplify) is unaffected.
L28's static numbers use the corrected orientation.

## L29 — cord-transfer-function: the uniform-tau interior is a ~3-stage low-pass, cutoff 5 Hz; stride rhythm does not survive it (11-11, tick 45)

Question: L21 measured the interior as a PATH-INTEGRAL delay (~9 base-tau
stages summed along the route). Complete the characterization as a FILTER:
sinusoidal current onto the cord mechano sensory population (3,588 cells,
amp 2.0*(0.5+0.5 sin), L16 event form), freqs {0.5,1,2,5,10,20} Hz, DT 10 ms
(f<=5) / 2 ms (f>=10), 5 Hz at BOTH DTs as the mixing check; DFT exactly at
the drive freq over the last 6 integer cycles; depth = amp/mean, 2f harmonic
as the in-run noise/distortion reference. Real x 2 seeds; L16 focused
interior MS-rewire null x 3 draws x {0.5,2,10} Hz. Step form W@X+I (the L30
feedforward-clamp probe honored; settled af0 at the L11 operating point).

Numbers (depth, 'all' pool; seed spread +/-0.001):
  0.288 (0.5 Hz) -> 0.265 -> 0.196 (2 Hz) -> 0.064 (5) -> 0.014 (10) -> 0.0005 (20).
- HALF-DEPTH CUTOFF = 5 Hz on EVERY pool (depth@0.5: Ti_flex .294,
  Ti_ext .372, Tr_flex .375, Tr_ext .309, all .288): 5 Hz carries 22% of the
  quasi-static depth, 10 Hz 5%, 20 Hz dead. A 5-10 Hz stride rhythm does NOT
  survive the homogeneous-tau interior.
- CASCADE FIT n = 2.7-3.2 per pool (rmse .001-.05) — NOT the ~9 stages the
  transit delay suggested. Attenuation rides the SHORT-path bulk = L21's
  2-hop sheet (d1/d2 premotor); the 344-466 ms smear is the long tail.
  Delay and attenuation are DIFFERENT MOMENTS of one path-length
  distribution: never predict a cutoff from a transit delay (or vice versa).
- Phase: -111/-131/-166/-220/-245 deg (unwrapped; 20 Hz dropped, snr 0.2);
  cascade pred (n=3.2) tracks the same order. 5 Hz DT consistency:
  DT10 .0645/.0640 vs DT2 .057 (-11%, discretization of the 50 ms tau;
  corner verdict unchanged either way).
- NULL (L16 interior rewire, 3 draws, sd ~.002): +21% MORE depth at 0.5 Hz
  (.349 vs .288), +15% at 2 Hz, both arms dead at 10 Hz (.011 vs .014);
  curve SHAPE n~2.8 in both arms. The real wiring attenuates ABSOLUTE
  modulation depth below its degree class (the envelope-width twin of L16's
  t_pk-spread finding); the cutoff BAND itself is model-class, robust to
  routing.
- Gate honesty: 0.5 Hz snr-vs-2f is only ~2.5x per pool — at 0.5 Hz the 2f
  reference is genuine 1 Hz PASSTHROUGH, not noise; reproducibility instead
  comes from seed agreement (+/-.001) and the mid-band snr (5 Hz: 9x).

Verdict: the cord reflex arc at uniform tau=50 ms is a ~3-stage low-pass —
gait rhythm at step frequency must ride per-class kinetics (L17/L18 taus) or
direct DN routes (L19 bypass), never the diffuse interior. Feeds the L7/L31
CX-gait endgame: do not ask this interior to oscillate at 5-10 Hz.
Anchors: tick 43's rebooted run reproduced bit-for-bit (seed 22 20 Hz depth
.000 ph -76; null draw 0 @0.5 Hz .347/-114 — l29/run_tick43_killed.out).
Artifacts: malecns/l29_transfer.py, l29_fig.py (house SVG + rsvg-convert —
no matplotlib on this box); l29/{results_l29.json, transfer.svg,
transfer.png (vision-verified PASS, 3 passes), run_tick45.out,
run_tick43_killed.out}. CPU-only, 656 s. No live changes; duck /needs 200.

## L30 — cross-leg-coupling: the cord is SEGMENT-MODULAR; cross-segment wiring is depleted everywhere (11-11, tick 44)

Question: L24 mapped the L/R mirror axis; is there a SERIAL (T1->T3)
inter-leg vocabulary in the cord, or is each leg's channel modular?
Segment keys: motor somaNeuromere T1 173/T2 175/T3 152 (+A1-10; instance
column carries muscle+side, e.g. 'Ti flexor MN_L'); vnc_intrinsic T1
3,380/T2 4,493/T3 3,417; vnc_sensory has NO neuromere (scope: MS null
rewires intr->intr only, 1,831,323 edges, weights travel with source,
2.5M swaps/draw; sensory carries no T label so it cannot affect the
T-tables). CSR W[target,source] throughout.

STATIC (claim-carrier; 500-draw intrinsic-neuromere label permutation):
- S1 direct intr(Ta)->motor(Tb) weight mass: diag 43.6/43.0/36.4 vs
  off-diag 1.4..9.4 — cross-share 0.196 vs null 0.666+-0.017, z -27.3.
  Per-cell z: diag +17/+14/+13, ALL six off-diag cells DEPLETED (-6..-8).
- S2 sheet intr(Ta)->intr(Tb): diag 430/460/343, off-diag -30..+123 —
  cross-share 0.119 vs null 0.661+-0.004, z -124.8. Per-cell z: diag
  +23/+14/+17, all off-diag NEGATIVE (-3.3..-12.1). The big cross masses
  (T1->T2 +57.7, T2->T3 +122.8) are still BELOW their null expectations:
  no cross channel is ENRICHED; T2->T3 is merely least-suppressed, and
  reverse paths sit at ~0 / net-inhibitory (T3->T2 -30.1). Directional
  rostral->caudal bias in RELATIVE terms only — no enrichment claim.
- S3 2-hop intr(Ta)->sheet->motor(Tb) (P[a,b] = sum_edges w*g_b[t]):
  cross-share 0.219 vs label null 0.674 (z -17.3) AND vs focused
  MS-rewire null 0.642+-0.003 (z -131.9) — the within-segment routing is
  a WIRING property, far beyond degree structure (both nulls agree).
- S4 readable: each leg pool draws 51-58% of total in-weight from its OWN
  segment's intrinsic (T1L .567/T1R .583; T2 .552; T3 .533/.507), any
  single other segment <=13.5%, sensory 5-9%, DN 4-13% (T1/T2 higher than
  T3). abd pools: no thoracic dominance (.014-.062 per segment).

DYNAMIC (P1-labeled; L20 optogenetic-style input volley on T1/T3
PREMOTOR-intrinsic, 2,681/2,711 cells, 300 ms @ amp 8, NO amplification,
uniform tau 50 ms, DT 10 ms, af0 0.163 = L11 op point restored after a
feedforward wiring bug in my first rollout — drive must be W@X+I, caught
because af0 came out 0.000):
- T1v: T1L/T1R SNR 580/733x vs T2 96-129x, T3 71-89x, abd 38x — same
  segment 5-8x above every cross pool. T3v mirrors (T3 576-666x, T2
  54-70x, T1 18-30x) and drives abd 164x — the CAUDAL neighbor responds
  more than T2 does, rostrocaudal gradient as anatomy predicts.
- Size-matched RANDOM-intrinsic arm flattens (151-262x everywhere): the
  gradient belongs to the segment-organized premotor set, not volley mass.
- SNR gate (L19) passes on every cross pool (>=18x), so the cross reads
  are measurements, not noise floors. t_pk 25-30 steps everywhere = no
  resolvable cross-pool delay at this drive class (sledgehammer volley,
  RMAX-pinned): NO timing claim; delay questions stay with L21's
  path-integral result. Pool-mean amplitude-SNR class (L21), not vector
  reproducibility.

VERDICT: inter-leg coordination is NOT carried by rich distributed
cross-wiring — the connectome actively SEGREGATES legs (every cross cell
below chance under both nulls). What cross-talk exists is thin, biased
caudal-ward (T2->T3 least suppressed; T3->abd strong), and readable at
rate fidelity — enough for phase-coupling modulation, not enough to be
the coordination substrate. Coordination mass is owned upstream (CX/DN),
consistent with L11's DN-gates-cord-programs reading — strengthens the
CX-gait endgame card (L31 preflight queued). Honest scope: dynamics are
P1-form (real gains, no per-arm retuning needed since no route was
amplified); segment labels are soma-side (somaNeuromere), not
dendrite-arbor side — a T2-soma cell arboring into T3 neuropil would be
counted T2 (S4's in-provenance is target-side so it partially captures
this; a root/neuropil-side census is a follow-up if ever needed).

Artifacts: l30/{results_l30.json, traces_T1v.npz, crossleg.png
(vision-verified 2 passes), crossleg.svg, run.out}; l30_crossleg.py +
l30_fig.py; CPU-only 314 s; no live changes.

## L31 — cx-dn-census: the CX speaks to DNs through LAL, not around it (11-11, tick 47)

Question: which CX cell types reach which DN families, at what hop depth
and weight — the static vocabulary a learned gait policy would act through
(L11: read at the DN port, never motor). Joins the L22 atlas (DN family ->
motor targets) and L24 laterality (L/R mirror org) so (d_L,d_R)-style DIAYN
primitives are enumerable from one table (tick-46 amendment, 2610.34638).

STATIC (P1-labeled; l31_census.py, CPU 9 s):
- CX = 2,950 cells (class 'CX', all cb_intrinsic, fully typed): FB 1,422 /
  EB 350 / NO+PFN 472 / PB 60 / PFL-out 50 / ExR-out 26 / other 570.
  DN = 1,314 cells, 481 types.
- DIRECT CX->DN is thin: 914 edges onto 168 DN cells (12.8%); max CX share
  of any DN type's total in-weight 7.3% (DNp48); most top-20 types <=5%.
- ALL 1,314 DN cells reachable <=3 hops over abs weights: 168 direct /
  1,126 (85.7%) first reached at hop 2 / 20 at hop 3 — the interface is
  overwhelmingly ONE relay wide.
- CX OUTPUT identity: PFL3 .50 + ExR8 .50 + PFL2 .20 + EPG .027 + PFL1
  .022 = ~75% of ALL direct CX->DN weight — the textbook CX output
  classes carry the port (weights in per-cell normalized units).
- RELAY decomposition of 2-hop mass (linearized abs product — descriptive,
  no cancellation claim): after CX-internal relays (PFL3/ExR8/PFL2
  relaying within the 2-step walk), the non-CX relay station is the LAL
  (LAL022 .073 / LAL126 .045 / LAL190 .044 / LAL200 .034 / LAL021 / 
  LAL083) plus SMP297/110/457; DN->DN chains (DNp48 .065, DNg36_a .032,
  DNa03 .028) add a second-order path. CX->LAL->DN is the connectome's
  route, not an assumption.
- ENRICHED direct targets (300-draw destination-swap null ON the block,
  weights travel with source, binomial-SE floor for never-hit types):
  DNg36_a z+28.6 (4 cells 2L/2R, ipsi -> CvN5 neck motor), DNpe015
  z+20.4 (11 cells -> MNhl87), DNpe016 z+5.0. DEPLETED (less direct CX
  than degree predicts): DNp48 z-3.3, DNc02 z-2.3, DNc01 z-2.2, MDN
  z-1.3 — placement, not weight mass, picks the direct partners.
- ESCAPE ROUTES ARE CX-INDEPENDENT (measured): DNp01-04 (L19 jump) and
  the L20 crouch six (DNg95/105/DNge079/DNg74_b/DNg35/DNg108) have direct
  CX weight ~0 (.0000-.0003) and 2-hop mass at the table floor
  (.0002-.0021). The looming->DNp route bypassing CX is anatomy, not our
  event choice. CX owns steering/posture/head-neck channels; the escape
  power stroke is sensory-parallel.
- Steering-primitive candidates (leg+gesture families ranked by CX 2-hop
  mass; every row carries nL/nR + ipsi/crossed + motor family):
  MDN .082 direct (4 cells 2L/2R, crossed, ext .28 — grooming/extensor
  lever, CX's strongest direct motor-relevant channel), DNg97 .042
  (crossed, Ti flexor .43, ALSO direct .032), DNpe022 .014 (ipsi, Ti
  flexor .49), DNg110 .009 (ipsi, jump .77 — a CX-reachable flight/jump
  channel distinct from DNp01-04), DNa01 .007 (ipsi, flexor .59), DNg79
  .003 (crossed, ext .27 — the L28 grooming channel). DNc01/02 + DNg36_a
  (neck/head) are the strongest direct levers overall.
- VERDICT for the CX-gait endgame (R1/L7, 2610.34638 recipe): a policy
  reading CX acts at the DN port through PFL3/ExR8/PFL2 + LAL relays onto
  steering/posture families, ~2 hops deep; it cannot reach the escape
  power routes — those stay sensory-parallel (L19). (d_L,d_R) primitives:
  enumerate L-cell vs R-cell drives per family from l31/cx_dn.csv; the
  ipsi/crossed org column gives the turn sign, the L22-join columns give
  the gesture sign (flex/ext/jump share).

Caveats: static census only (no dynamics run); lin2 is a linearized
abs-product descriptor; hop counts are min-hop existence over abs weights;
direct weights in per-cell normalized units; nulls are block-internal
destination swaps (in/out degrees kept) — they test type PLACEMENT of CX
input, not whether CX reaches DN at all.

Artifacts: l31/{cx_dn.csv (481 rows), results_l31.json, run.out};
l31_census.py; CPU-only 9 s; no live changes; duck untouched.

## L32 — wiring-borne-antagonism (tick 48, 2026-11-11): REPLICATED — real cord
wiring DOES order antagonist antiphase under sustained drive; the missing
ingredients were inhibition SCALE + drive REGIME, not the glutamate sign.

Protocol (2609.38665 ported to male_graph; claims pre-registered in
l32/PREREG.md BEFORE scanning): cord subnetwork (sensory+intrinsic+motor
13,006 cells + 1,469 DNs projecting in; 2.88M edges), weights = RAW signed
synapse counts (no indegree norm — labeled deviation from male_graph.pt),
uniform tau 50 ms (NO per-class taus — that is the point), 3 global params
only: gain g, inhibition scale beta, sustained bilateral DNg100 drive d
(2 cells, 1L/1R). Two sign arms: A "ours" glut-excitatory, B "flyvis"
glut-inhibitory. Scan 60 settings/arm x 2 seeds (8 s) -> frozen best ->
60-s confirmation x 3 seeds -> ladder nulls (density / degree / legblock
= MS within neuromere-block cells, >=2 draws each) at the SAME frozen
setting. Op-point assert every run (af .176-.191); depth gate 0.03 before
any S read.

- C1 RHYTHM: PASS everywhere (frozen rhythm 125 (A) / 1091 (B), max scan
  11k/15k) at 1.2-1.4 Hz (paper MaleCNS: 2.4-4.1 Hz — same order, slower
  at rate fidelity). Rhythm is not the claim; it appears in nulls too.
- C2(i) REAL: arm A pair Tr S per-seed [+.492,+.472,+.507] mean +.490,
  all seeds > 0, depth .30-.43 (10x gate). Ti is NEGATIVE (-.067): the
  antagonism is pair-specific in our vocabulary. Arm B FAILS: best pair
  Ti +.079 < .15, per-seed Tr wild [-.055,+.103,-.717] — the flyvis arm's
  scan S (.274) was 8-s-window-fragile.
- C2(ii) LADDER (arm A, frozen g=.01 beta=2.0 d=.05): REAL +.490 vs
  density +.032/-.031, degree +.055/+.178, legblock -.019/-.013 -> every
  draw below real, margin +.313 >= .05. PASS. Ladder shape non-monotone:
  legblock (block matrix preserved, placement scrambled) is DEADER than
  degree — within-block PLACEMENT carries the phasing, the block-mass
  matrix (the L30 object) does not. Degree keeps a residue (+.178):
  degree structure contributes part of the antagonism, placement the rest.
- C3 ATTRIBUTION (outcome adjacent to prereg branch 2, honestly labeled):
  passes under arm A ONLY -> the missing ingredient was inhibition SCALE
  (beta=2 on GABA) + SUSTAINED drive; the glutamate->inhibitory sign rule
  was neither necessary (A passes without it) nor sufficient (B fails
  with it).
- Honesty notes: frozen setting = scan argmax (pre-registered criterion;
  nulls evaluated at the same frozen setting — no re-tuning); density
  draw 1 made its OWN anticorrelation on the OTHER pair (S(Ti) +.301) —
  rhythm everywhere, pair IDENTITY wiring-specific; 3 noisy seeds, not
  the paper's 20 (budget form); our Tr pool ('Tr flexor MN' vs 'Tr
  extensor MN') is the paper's ThC/CTr analog only by name-guess — their
  ThC-first hierarchy is not nameable in our type vocabulary; raw-count
  weights change the operating point machinery (g calibrated per arm,
  bands logged in scan_l32.json).
- Consequences: L16 ("wiring smears time") held for TRANSIENT volleys;
  L28 ("antiphase only via anti-phase DN drive") held for DRIVEN pools;
  under SUSTAINED drive the cord interior self-orders antagonists — the
  CX-gait endgame (L7/L31) gains a cord that can self-pace under tonic
  DN drive, so steering can be a MODULATION of an intrinsic rhythm
  rather than a full trajectory command.

Artifacts: l32/{PREREG.md, results_l32.json, scan_l32.json, run.out};
l32_antagonism.py; CPU-only 468 s; no live changes; duck /needs 200
throughout.

## L33 — steering-modulated-rhythm (tick 49, 2026-11-12): tonic DN bias does
NOT steer the self-rhythmic cord — robust, refractory, metastably lateralized

Question (ideas 14): L32 left the CX-gait endgame with a cord that self-orders
antagonist antiphase under sustained drive. Does a unilateral tonic steering
bias (DNg95, the L24 ipsi flexor channel) GRADE the turn while the rhythm
survives — modulation, the endgame assumption — or break/refuse it?

Setup: L32 arm-A substrate IDENTICAL (verified: l32/run.out and l33 both log
"sub nodes 21,516 (cord 20,239 + dn_into 1,277) / 2,977,920 edges" — the
"13,006 + 1,469" in tick-48's summary was a transcription slip). Params are
the l32 frozen g .01 / beta 2 / d .05, arm A signs, raw-count weights,
uniform tau, settle-then-drive, 60-s window, seeds 11/22/33. DNg95 1L/1R
present; flexor pools split cleanly (Ti 43L/41R, Tr 29L/28R). Bias amps
d x {0.25, 0.5, 1, 2, 4}; R-side sign controls at 1x/4x; 2 random-DN-pair
nulls at max amp. PREREG l33/PREREG.md written first (C0-C4).
P1-labeled (frozen real-tuned params reused, no per-arm re-tune).

VERDICT against pre-registered claims:
- C0 anchor PASS: base S(Tr) +.48/+.46/+.49, rhythm ratio 176-591 @
  1.33-1.43 Hz = L32 reproduced (tiny numeric offset vs l32's +.49/+.47/+.51:
  l33 pools flexors by summing L+R trace means, l32 pooled all cells —
  weighting difference only, family identical).
- C1 survival PASS: EVERY arm/seed keeps S(Tr) > +.43 pooled and rhythm > 160x
  median. The self-pacing regime is robust to any bias here — antiphase
  survives.
- C2 graded FAIL: baseline |turn| is +.13 (a WIRING-set operating asymmetry,
  not noise — 3/3 seeds within .007) and no bias level moves it beyond that:
  seeds 22/33 flat .127-.141 across the whole 16x amp sweep; seed 11 shows a
  non-monotone transient (+.29/+.31 at amps 0.25-0.5x, back to +.13 at >=1x).
- C3 sign FAIL: R-side bias flips turn on 1/3 seeds only (seed 33 at 4x:
  Ti -.035 with R-side oscillation amplitude +.44) — not sign-consistent.
- C4 specificity FAIL in the informative direction: random DN pairs perturb
  as much or MORE than DNg95 (rand1 seed 11: |turn| .203 vs DNg95 .133;
  amp asymmetry -.77 — the biggest deflection in the whole grid came from a
  RANDOM pair).

Mechanism read (depth/af checked, pools NOT saturated: flexor oscillation
depth .12-.20, af .18-.19 = op point healthy):
1. The regime is bias-REFRACTORY: a tonic drive anywhere in the DN layer is
   absorbed by the operating point without a parametric motor readout. Not
   an amp problem — the sweep covers 16x with no graded response (echoes the
   L11/L23/L25 dead-amp family, but here at pool OSCILLATION level too).
2. The two sides are weakly-coupled near-independent oscillators: L/R flexor
   cross-corr only +.13..+.34, lag unstable (±100-200 ms, occasional 1-20 s
   slips) — "the rhythm" is not one global clock a bias could phase-shift.
3. Which side CARRIES the antiphase is metastable: baseline is left-organized
   (S_TrL +.64 vs S_TrR +.12-.38, all seeds); seed 11 at low bias flips the
   organization (S_TrL .17-.19 / S_TrR .72-.79) and returns at >=1x; a random
   pair flips it too. Perturbations SWITCH side-dominance stochastically —
   they do not MODULATE it.

Boundary for the endgame card (the point of the card): steering-by-tonic-bias
is dead at this substrate/fidelity. What survives for CX-gait: (i) phasic
route-amplified volleys (L24 form — graded turn +.46/-.47 was measured in the
TRANSIENT regime, not on a sustained rhythm); (ii) L34 entrainment — phase-
locking a periodic drive to the coupled oscillators; (iii) reading steering
at the DN port (L11) rather than motor pools. Also honest: the +.13 baseline
turn means even the "unsteered" cord model has a built-in circling asymmetry
— worth remembering if this substrate ever drives a body.

Post-hoc (labeled): AC amplitude asymmetry and L/R lag computed per arm
(results json "ac" field); nothing parametric there either. Sobol one-param:
DNg95 tonic rate is unmeasured — but a 16x sweep with zero graded trend is a
structural failure, not a wrong-amp failure.

Determinism: v1 (results_l33_v1.json) and v2 (trace-saving rerun) agree
exactly on every overlapping number (base, all L/R arms, rand) despite the
mid-run code additions.

Artifacts: l33/{PREREG.md, results_l33.json, results_l33_v1.json,
mm_traces.npz (motor + per-pool traces), steering.svg/png, run.out, run2.out};
l33_steering.py, l33_verdict.py, l33_fig.py; CPU-only ~110 s/run; no live
changes; duck /needs 200 throughout. Figure steering.png vision-verified.

## L34 — rhythm-entrainment (tick 50, 2026-11-12): the self-rhythmic cord
ENTRAINS — body-level feedback CAN phase-stabilize gait (C0-C4 all PASS)

Question (ideas 14): L33 killed tonic-bias steering; the remaining modulation
path was PHASIC external drive — the body-feedback channel (L26 bridge form).
Does periodic mechanosensory drive LOCK the L32 self-rhythm (entrainment:
motor freq tracks drive, phase concentrates vs free-run), or is the cord's
rhythm autonomous and drive-refractory?

Setup: L32/L33 substrate IDENTICAL (asserted 21,516 nodes / 2,977,920 edges;
frozen g .01 / beta 2 / d .05 arm A; settle 400 then 60 s window, measure
last 45 s; seeds 11/22/33; af op-point + NaN asserts every run). Drive:
bilateral sinusoidal current on ALL 3,588 sub-network mechano sensory cells,
I = A*(0.5+0.5 sin(2pi f_d t)) — substrate-vibration form, symmetric. Grid
f_d {0.7...3.0} x A {0.01, 0.03, 0.1, 0.3} x 3 seeds + free runs, 123 runs,
CPU-only 489 s. PREREG l34/PREREG.md written before any scan; P1-labeled.

INSTRUMENT FINDING (probe l34/probe.out, pre-grid): my free-run rerun is
BIT-IDENTICAL to l33's saved mm traces (max|diff| 0.0, all seeds) yet seed
11 FFTs to 0.800 Hz where l33's json said 1.333 — l33's rhythm metric read
the FULL 60 s (transient included) while its npz saved the last 45 s. The
attractor freqs are {0.800, 1.444, 1.422}; "1.33-1.43" was transient-carried.
C0 anchor amended to the pre-registered measurement window BEFORE any grid
data existed (documented in PREREG amendment block). Lesson: when a summary
metric and a saved artifact use different windows, the artifact wins.

VERDICT against pre-registered claims — ALL PASS, first full-positive since
L22:
- C0 anchor PASS: S(Tr) +.48/+.46/+.49, ratio 169-288, f_free anchors hit.
- C1 survival PASS: gentlest amp keeps rhythm everywhere (ratio >= 10).
- C2 FREQUENCY LOCK PASS, 13 cells: locking is absent at A=.01, begins at
  A=.03 ({1.0, 1.75}), nearly complete at A=.1 (8/10 cells >= 2/3 seeds),
  complete at A=.3 (10/10, only near-resonance freqs excluded by the
  pre-registered |f_free - f_d| >= .15 eligibility rule). Strongest: f_d 1.0
  locks 3/3 seeds at EVERY amp >= .03; seeds 22/33 get dragged DOWN from
  1.44 to 0.70 Hz at A=.1 — real frequency pulling below resonance, not
  superposition.
- C3 PHASE LOCK PASS: locked cells concentrate motor phase rel drive at
  R .71-.99 (mean ~.9) vs sham free-run R <= .23 at every C3-qualifying
  freq. Honest footnote: global max sham R = .334 at (seed 33, f_d 0.7) and
  .302 at (0.85) — sub-threshold mixing in the free rhythm's own band, at
  freqs OUTSIDE the pre-registered C2-eligible set; no C3 cell is affected.
- C4 TONGUE PASS: lockset grows monotonically {} -> {1.0,1.75} -> 5 freqs ->
  6 freqs — textbook Arnold tongue widening with amplitude.

COST structure (the layered part): entrainment and antagonist organization
are NOT free of each other. At A=.01 the antiphase is preserved (S(Tr) mean
+.45, free-run level) but NOTHING locks. Locking ONSET (A=.03) collapses the
organization (S mean -.05, min -.41). At A=.3 the lock is complete AND the
antiphase is largely restored (S mean +.35, up to +.64) — the strongly driven
sensory->motor reflex pathway (L11/L16/L28 arc) carries its own antagonist
structure, so the driven rhythm re-hosts the antiphase. Non-monotone in amp:
dead->locked-but-disorganized->locked-and-organized. Edge: f_d 3.0 fails at
A=.1 (0.53/1.58/0.51, quasi-periodic) yet locks at A=.3 — the tongue's
high-frequency edge tracks the L29 ~3-stage low-pass (5 Hz half-depth) of
the sensory pathway.

Endgame consequence (what this buys): L33's dead end had three exits —
phasic volleys, ENTRAINMENT, DN-port read. Entrainment now measured ALIVE:
a bridge-level periodic body signal can set gait frequency and phase, and
at sufficient amplitude it carries the antagonist antiphase with it. The
honest control loop for CX-gait is: CX/DN output PHASE-RESETS or entrains
the cord through periodic (not tonic) input; body feedback closes the loop
through this same measured channel. Taste note for the queue: phase-reset
by BRIEF DN volleys (one-cycle correction, L24 form) is the natural next
probe before any closed loop.

Determinism: free runs bit-identical to l33 npz (probe); grid deterministic
(seeded generators, per-run af asserts all passed).

Artifacts: l34/{PREREG.md (incl. window amendment), results_l34.json,
traces.npz, entrain.svg/png, run.out, probe.out}; l34_entrainment.py,
l34_probe.py, l34_fig.py; CPU-only; no live changes; duck /needs 200 (16.6 s
under box load), unit active, no stray python. Figure entrain.png
vision-verified (2 fix passes: legend/title collision, x-label/legend
collision).

## L35 — phase-reset-volley (tick 51-52, 11-12)

Question: can a BRIEF (250 ms) DN volley delivered at a known phase re-time
the L32 self-rhythmic gait (phase response curve) without breaking it — the
one-cycle-correction primitive between L24 (transient turn) and L34
(continuous entrainment)?

Design (PREREG l35/PREREG.md, 5 pre-data amendments — instrument evolved
BEFORE any PRC arm ran: dom-freq band matched to L34; PRC subject moved to
the motor-mean gait oscillator after the flexor peak train proved
quasi-periodic; heterodyne phase (L34 form) replaced peak-train PRC; R gate
relaxed to .35 with the paired-noise rationale). Paired-noise: control +
volley share the generator seed; C1 pre-volley bit-identity 3/3. 120 runs:
dng95 x {0.05,0.15} x 8 phase bins, dng100pulse x 2 amps x 8 bins, dur-100
arm, 5 sham draws (random DN pair, random phase, amp .15). Heterodyne dphi
over a 15 s post window; survival ratio/S(Tr)/freq.

VERDICT (corrected, l35_verdict.py — the in-run analysis had a name-swapped
unpack that exchanged PRC amplitude and argmax bin, an empty C4 filter, and
a C2 freq leg against the full-window flexor ripple; all caught on the log,
recomputed from saved artifacts, gates NOT moved):

- C0/C1 green: anchors exact (0.800/1.444/1.422 Hz, ratio 169-288, S(Tr)
  .48/.46/.49, R .46-.48); substrate identical to L32/L33/L34.
- C2 SURVIVAL green where it matters: ratio_post >= 10 and S(Tr) >= .30 in
  EVERY arm (0/64 fails); the gait never breaks. mm-rhythm freq shifts
  > .15 Hz in only 4/64 arms (seed 11, bins 45/225 — the strongest re-timing
  events). The as-coded flexor-ripple freq leg (53 fails) is an instrument
  artifact, not a break.
- C3 PRC FAIL, all four channel/amp arms: dng95 A0.05 max |mean dphi| 10.8
  deg @ bin 45 (sign-consistent 3/3 but 8/24 volleys absorbed), A0.15 18.9
  deg @ bin 270 (0/24 absorbed, sign +21/+42/-6 breaks) — both far below the
  3x-sham gate 57.6 deg; sham (random DN pairs, same amp) deflects MORE
  (per-seed |mean| 19.0/19.2/0.1, single max 73.6). L33's lesson repeats:
  random DN perturbation >= the named channel.
- C4: dose monotone (10.8 -> 18.9); PERSISTENCE REFUTES reset — early-window
  deflection [-41,-6,-29] deg does not carry: late window [+37,+43,-5]
  relaxes/flips back toward the attractor phase. dur-1000 ms gives bigger
  single-seed swings (+119/-82 seed 11, phase-dependent!) but seeds 22/33 do
  not replicate (-22/+14, -3/-5).

MECHANISM (probe l35_probe2.py, measured on control rollouts): volley
efficacy is RELU-FLOOR-GATED. DNg95's total drive u = W@X*G + I + BG at the
volley windows: absorbed bins u_max <= -0.064, landed bins u_max >= -0.038 —
the +0.05 volley crossing zero is EXACTLY the absorption boundary (8/24
absorbed at A0.05, 0/24 at A0.15 — a bigger volley out-lifts the inhibition;
amplitude HELPS, the opposite of ceiling-pinning). The floor-gated phase
structure: the oscillator's own inhibition schedules when a brief input can
reach the circuit.

REGIME CORRECTION (probe l35_probe3.py — relabels L32/L33/L34, findings
stand, mechanism label changes): the "sustained bilateral DNg100 drive"
(D=0.05) is INERT. DNg100 cells sit ~16 units BELOW the relu floor (u in
[-17.5,-15.9], X ~ 0.006, floor-pinned silent) and D=0.0 reproduces the
saved control trajectories BIT-IDENTICALLY (max|dflx| = max|dmm| = 0.0, all
3 seeds). The self-rhythmic antagonist cord of L32-L34 is CORD-INTRINSIC at
(g .01, beta 2) — it never received DN drive at all. Consequences: (1)
L32's replication of 2609.38665 is STRONGER than claimed (real wiring
orders antiphase with zero drive, vs rewired nulls) but the "sustained
drive" ingredient was never actually tested — our d never participated;
(2) L33's tonic-bias absorption and L34's entrainment conclusions are
unchanged (their substrate is the same intrinsic rhythm); (3) the endgame
card must find a REAL drive channel: a DN class whose cells sit above the
relu floor under the regime (L36 candidate: floor-viability census over the
L22 atlas types); (4) L35's dng100pulse arm was dead by construction —
modulating a drive whose cells are floor-buried cannot land, at any amp
(48/48 bit-identical).

Frame: P1-labeled throughout (frozen L32 params re-applied); no WHEN-claims
beyond measured window shifts; no live changes.

Artifacts: l35/{PREREG.md (5 amendments, all pre-data), results_l35.json,
verdict_l35.json (corrected), traces.npz, probe_mech.json, run_tick52.out,
prc.svg/png}; l35_phasereset.py, l35_verdict.py, l35_probe2.py,
l35_probe3.py, l35_fig.py. CPU-only 515 s + probes; duck /needs 200
throughout. Figure prc.png vision-verified PASS (3 fix passes: panel
A/B title collision, panel C off-canvas at W=1160, panel C annotation
overlap).

### L36 — dn-floor-viability-census (tick 53, 11-12): the drive-channel
### vocabulary is REAL and two-sided

Question (seeded by L35's regime correction): which DN types can actually
carry a drive into the cord under the frozen L32 regime (g .01, beta 2) —
the "sustained drive ingredient that is real this time"?

CENSUS (l36_census.py, substrate asserted identical to L32-L35: 21,516
nodes / 2,977,920 edges; u = W·X·g + BG, l35_probe2 definition; 3 seeds x
6 s post-settle, I=0 — probe3 proved that IS the control regime): 1,277
cord-reaching DN cells across 476 types; joined to the L22/L24/L31 table
(l31/cx_dn.csv: family shares, L/R org, CX hop). 76 atlas family types
(flex 47 / jump 23 / ext 6; 5 atlas types absent from the cord sub — they
target only non-cord motor).

TWO-SIDED viability (the amendment the MDN spot-check forced): a tonic
channel needs floor headroom (u_max > 0) AND ceiling headroom (baseline
X < .95). Vocabulary: **34 viable-modulating types (18 flex / 14 jump /
2 ext)**, 27 need-amp (u_max in (-.8, 0]), 13 buried (<= -.8, incl. L20
crouch classes DNg108/­DNge063/073), 2 CEILING-PINNED (DNg88 u_max +10.8,
MDN +4.5 — both mean_X = 1.0000 exactly: u_max > 0 alone is NOT
viability; the clamp kills upward range). Top per family: flex DNge059
(u_max 4.5, X .88) / DNg105 (3.6, X .75 — L20's crouch class, crossed),
ext DNb05/DNg79 (L28's grooming extensor channel is viable), jump DNg110
(1.6, X .81) + DNp02 (L13's jump class, viable). Floor-hugging anchor
DNg95 (u_max +.047, frac_pos .011) and buried anchor DNg100 (-15.78)
reproduce L35 exactly.

DYNAMIC SPOT-CHECKS (tonic amp .2/.8, 3 seeds, 60 s, metrics on last 45 s,
P1): DNge046 (flex, crossed) and DNg110 (jump) PASS at both amps — dm
lands at window step 0 (freely-active cells) and the rhythm RESPONDS:
f_Ti 0.80→1.98 / 2.04→2.16 / 1.91→3.40 Hz (DNge046@.2). **A tonic viable
channel modulates the intrinsic rhythm's FREQUENCY by ~+1-1.5 Hz — the
real sustained-drive ingredient L32-L34 assumed.** MDN: dm EXACTLY 0 at
both amps (bit-identical) = ceiling-pinned, the census-side mean_X ≥ .95
predictor — L35's floor/ceiling amp-taxonomy now has a static census
test. Anchors: DNg100@.8 bit-identical (PASS), DNg95@.2 lands (PASS).

INSTRUMENT LESSONS (two mid-run catches, both before any verdict was
read): (1) paired control/arm noise needs ONE generator and ONE shared
noise tensor per step — two same-seed generators are OFFSET by the init
draw (phantom divergence, dm saturates ~1.0 everywhere; fingerprint:
identical dm/dS/df across unrelated arms); (2) drive must enter AFTER
settle — during settle the arm crosses DNg100's SHALLOW TRANSIENT
inhibition (u ≈ -0.6 before the attractor deepens it to -16) and lands on
a different attractor entirely. The attractor's deep inhibition is BUILT
during settle; census u measures the settled regime, which is the honest
control state. PREREG amendments disclosed in l36/PREREG.md (DNg95
free-window band; C2b two-sided criterion — both pre-verdict).

Frame: P1-labeled; no WHEN-claims; no live changes. Artifacts:
l36/{PREREG.md, census_l36.csv (476 types), results_l36.json,
viability.svg/png (vision-PASS, 3 fix passes), run2-run5.out};
l36_census.py, l36_probe.py, l36_probe2b.py, l36_summary.py, l36_fig.py.
CPU-only ~210 s final run; duck /needs 200 at tick end (7.6 s under box
load 3.5-6.7), both units active, no stray lane python.

### L37 — steering-revisited on viable channels (tick 54, 11-12): CONFIRMED,
### not a channel artifact — and viability is SIDE-asymmetric

Question: L33 verdicted "tonic bias cannot steer" using DNg95, whose bias
enters on ~1% of steps. With L36's 34 viable-modulating channels, was that
negative just a channel-choice artifact? PREREG l37/PREREG.md (claims C0-C4
written before any scan). Substrate l32-frozen verbatim; paired lockstep
(ONE generator, ONE shared per-step noise, L36 rule); drive AFTER settle;
dm probe + first_div every arm (L35); 15 arms x 3 seeds; l37_steer.py exit 0
(385 s CPU-only, run3; run1 died on my own assert bug — base reference
snapshotted at end-of-window but compared post-settle, fixed; run2 killed by
a 420 s foreground cap with 14/15 arms done; run2/run3 base rows identical
+.139/+.132/+.132 — deterministic).

Verdict (pre-registered branch 2, speed-without-steering, and it is the
honest layered read):
- C0 PASS: base S_Tr +.48/+.46/+.49, rhythm ratio 169-288, wiring-set turn
  +.139/+.132/+.132 (L33's +.13 reproduced exactly).
- C2 FAIL — the headline: channels whose drive LANDS (dm ~1.01, driven
  cells fully active) still do not steer. Max |dTurn| .016 vs the .15 gate;
  sign not seed-consistent (DNg105_L -.001/+.001/+.016; DNge046_L
  -.011/-.008/+.004). Per-side mass shifts <= .005. L33's negative is
  CONFIRMED and STRENGTHENED: not a channel-choice artifact. Steering at
  rate fidelity stays phasic (L24 volleys), entrained (L34), or DN-port
  (L11) — a self-rhythmic antagonist cord is a throttle, not a yoke.
- C1 as-written FAIL solely via a NULL arm: rand0 at .8 shoves turn
  -.171/-.170/-.228 sign-consistent 3/3 BUT by breaking the antiphase
  (S_Tr -.22/-.20/-.01); every curated channel arm preserves S_Tr >= .38.
  Disruption masquerades as steering if you read turn without checking the
  rhythm survived — instrument both. (Inline branch-picker printed the C1
  branch; the layered read above is the shipped verdict. C3 "PASS" for
  DNge059/DNg105 is vacuous — zero/tiny monotone shifts. C4's beats-best
  clause never fired because no channel passed C2.)
- NEW FINDING (dm probe, in-run): viability is SIDE-asymmetric. DNge059's
  L cell is [WORDING CORRECTED BY L38, tick 55: CEILING-PINNED, not
  floor-buried — u_mean +4.0 / mean_X 1.0; t clamped at RMAX, so positive
  amp at ANY strength is invisible; the asymmetry itself stands] dead at
  every amp (dm 0.0000, bit-identical to base)
  while its R cell lands (dm 1.01); DNge046 is the mirror image (L lands,
  R buried). The L36 census pools the TYPE — its u_max was carried by one
  side. L38's primitive table must carry per-SIDE viability (folded into
  LANE.md L38). DNg105 first_div [53, 483, 77] steps: intermittent floor
  crossing at single-cell resolution (the census frac_pos story, one cell).
- Static composition (signed, arm-A signs): DNge059 strictly ipsilateral
  excitatory (w L->flexL +538.0, L->flexR 0.0); DNg105 strictly crossed
  inhibitory (L->flexR -1401.0, R->flexL -1577.0 — L24 all-inhibitory
  confirmed); DNge046 direct flexor weight ~ -1 total (its census w_flex
  .28 rides 2-hop paths, med_hop 2 — direct-edge composition would have
  predicted nothing, and dynamics agreed: it lands but moves nothing).
- Per-side rhythm FFT is seed-unstable in the BASE (f_fR 0.80/3.47/3.38 —
  L33's metastable side-dominance), so no per-side frequency claim is made
  here; pooled mm f 1.22 -> 1.39-1.41 across landing channels.

Artifacts: l37/{PREREG.md, results_l37.json, steer.png/.svg, run.out,
run2.out, run3.out}; l37_steer.py, l37_fig2.py (fig v1 + l37_fig.py
superseded). Figure vision-PASS after 3 fix passes (base band plotted at
+.13 on a SHIFT axis — moved to zero-reference; legend-over-data; label
collision). No live changes; duck /needs 200 at tick end.

## L38 — viable-primitive-table (tick 55, 2026-11-12)

Question: the endgame (d_L,d_R) enumeration — join the L36 census onto
l31/cx_dn.csv PER SIDE (L37 amendment) and dose the channels BOTH signs
(the two-sided rule + ceiling-pinned types as deceleration candidates).

Deliverable SHIPPED: l38/primitives_viable.csv (481 families, per-side
{n, u_max, u_mean, mean_X, frac_pos, verdict} + cells_free/pinned/total per
side + L31 laterality/CX cols + L22 family weights + L37 dm fold). Gates:
C0 PASS (substrate 21,516/2,977,920; DNg100@.8 dm 0.0 bit-identical 3/3,
DNg95@.2 lands), C2 PASS (18 flex / 14 jump / 2 ext types have a VIABLE
side; 107/481 types have SPLIT side verdicts). 172 types free cells both
sides; 56 types pinned-only R side.

C1 FAIL — and the failure RESOLVES L37's mechanism label. L37 called the
dead mirror halves "floor-buried"; the per-cell census says CEILING-PINNED:
DNge059 L cell 11127 u_max +4.518 / u_mean +4.018 / mean_X 1.0 (probe
l38_probe.py) — u+BG sits ABOVE the RMAX clamp, t pinned at 1.0, so ANY
positive amp changes nothing (dm=0 flat across .05-.8 = L35's clamp-ceiling
signature; a true floor-burial needs amp to help, L35 DNg95 8/24->0/24).
Static/dynamic fully reconciled: DNge059 R free (lands) / L pinned (dead);
DNge046 mirror (L free, R pinned). The L37 asymmetry claim stands; the
"buried" word was wrong — LAB-INTENT L37 amended in place above.

C3 FAIL (honest, mechanistic): no graded throttle. DNge046_L + DNg110 land
(dm 1.01) at every entering amp but df(Ti) is SEED-INCONSISTENT and
non-monotone in amp (DNg110@.2 [+1.42,+.13,+1.53]; @.4 [+1.58,-1.27,+1.47];
medians +1.42/+1.47/+0.62) = the intrinsic rhythm HOPS among its attractor
set (~0.7-3.4 Hz, L33/L34/L36) under any entering perturbation. DNge046_R
positive: FLAT dm=0 at ALL amps .2-.8 (pinned side cannot accelerate).

C4 FAIL as written / phenomenon measured: pinned types are a STOP, not a
slow. DNg88 (u_max +10.8, both cells X=1.0): -2/-4 dm=0 (still pinned),
-8 ENTERS and KILLS the antagonist rhythm S(Tr) .47-.51 -> .06-.12
(strict nkill gate counted 1/3 — .10 not < .10 — disclosed); -12 enters,
S partially recovers .21-.47. MDN (u_max +4.5): -1 dm=0, -2/-4/-8 enter
but only perturb (df sign flips, S survives .41-.91). No df<0 slowing
anywhere: negative drive un-pins into DISRUPTION, not deceleration.

C5 FAIL (informative): DNge046_R @-0.8 dm 1.01 — the pinned side is
positive-invisible but NEGATIVE-SENSITIVE once amp ~ -u_mean (un-pin
threshold between -0.4 and -0.8). Two-sided rule confirmed on the SAME
cells: R side flat-zero for +.2..+.8, alive at -.8.

ENDGAME CONSEQUENCE: the executable action set is DISCRETE, not a graded
dial — (a) per-side, two-sided channels (positive acts on free cells;
pinned cells are negative-only brakes), (b) entering drives select among
attractor frequencies rather than modulate a speed, (c) the graded lever
remains ENTRAINMENT (L34). A learned gait policy should act through
attractor selection + entrainment + DN-port reads, never tonic bias.

Artifacts: l38/{PREREG.md, results_l38.json, primitives_viable.csv,
cells_dump.json, dose.png/.svg, run.out}; l38_primitives.py, l38_cells.py,
l38_probe.py, l38_fig.py. 84 paired arms + census, CPU-only 724 s. Figure
dose.png vision-PASS (2 passes; cosmetic notes accepted: one stray
bottom-right dot, tight legend-to-dot gap in panel B). No live changes.

## L39 — discrete-gait-controller: entrain + hop (tick 56, 2026-11-12)

**Question.** Can a 2-primitive controller — ENTRAIN (sinusoidal mechano
drive, L34 regime, A=.3) + one brief HOP volley (DNge046_L amp .5 / DNg110,
400 ms at each transition) — hold a stepped gait-frequency target
0.7 → 1.4 → 0.7 Hz against the cord's intrinsic attractors and metastable
side-flips (L33)? PREREG l39/PREREG.md written first (C0-C4).

**Substrate/anchors.** Frozen L32 regime verbatim (21,516 / 2,977,920);
4 paired arms x 3 seeds, ONE generator + shared per-step noise (L36). Free
arms BIT-IDENTICAL to l34's saved traces (max|diff| = 0.0, all seeds,
last-45-s window); free_f {0.8004, 1.4438, 1.4236} = anchors to <1e-3.

**INSTRUMENT CATCH (the tick's lesson).** Run v1's volley line
`drive[hop046 if a=="ent_h046" else hop110, 0] += AMP` fed the DNg110
volley to the ent CONTROL arm too — ent_h110 came back bit-identical to
ent (dm=0.0) and I initially read "DNg110 ceiling-pinned under
entrainment". The dm probe forced the wiring check; a static u/X probe
showed h110 cells mid-range (u~0.95, X~0.80) — inconsistent with pinning —
and the diff review found the control contamination. v1 preserved
(results_l39_v1_bug.json); clean rerun below. Rule: a bit-identical PERTURBED
arm means the control and treatment received the SAME drive before it means
the channel is dead (L35's dm probe catches wiring bugs, not just floors).

**C1 hop lands — BOTH channels.** first_div 0 (first volley step),
volley_max ~1.0, 3/3 seeds each. DNge046_L and DNg110 both carry a volley
into the regime (two-sided census verdicts transfer, contra the v1 reading).

**C2 entrain-only: n=1/3 (WEAK).** Mean |f-target|: ent 0.267/0.175/0.104
vs free 0.659/0.437/0.448 — always better than free, but only seed 33
clears the 0.15 gate. The hard step is UP to 1.4: seed 11 seg1 err 0.275
(blocks wander 0.4-0.56), seed 22 seg1 0.334 — the drive alone fights the
attractor through the whole 20-s segment (Arnold tongue is thin there at
these attractor distances).

**C3 hop accelerates — constructive core, formal FAIL on survival.**
ent_h046 tracks STRICTLY BETTER on 3/3 seeds (mean err 0.176/0.062/0.093;
seg1 rescued universally: 0.275→0.001, 0.334→0.002, 0.008→0.001; ttl to
block 1). But the pre-registered survival gate fails: seed 33 seg1
S(Tr) = −0.316 (the volley locked FREQUENCY while INVERTING the antagonist
relation — in-phase!), h046 seg2 dips 0.16-0.21, and even clean ent dips
below 0.25 in 3/9 segments (0.19-0.22 at transitions; L34's non-monotone
cost, now measured per-segment). As registered: a hop that buys frequency
at the cost of antiphase is not steering — C3 FAIL, disclosed with the
constructive half. DNg110 is channel-inconsistent: helps 22/33
(0.064/0.070), HURTS seed 11 (0.328, seg1 0.613 — the jump channel's
attractor kick throws the 0.8-attractor seed off target). The flexor-
rhythm-adjacent channel (DNge046, crossed) is the reliable hop primitive.

**C4 survival: FAIL.** Transition segments dip S below 0.25 in every
controlled arm (min −0.316); rhythm itself never dies (ratios >> 10 all
segments). Descriptive side note: free seed 33 flips side dominance
mid-run ([-1,+1,+1], L33 metastability); entrainment stabilizes side
choice (8/9 segments stable); the h046 volley FLIPPED seed 33's side
dominance at the S-inversion segment.

**Verdict.** Frequency-only steering is DONE at this fidelity: entrain
carries near-attractor segments, one DNge046_L volley per transition makes
the hard step universal (3/3 seeds, ~0 err on the 1.4-pull). Gait-with-
structure is NOT held: antagonist antiphase and side organization pay at
every transition (S dips/inverts; the structure-cost L34 predicted).
Endgame synthesis: the (d_L,d_R) discrete action set (L38) + entrain+hop
controller (L39) covers the frequency axis; structure-preserving
transitions (phased volley envelopes, slower ramps, or per-side volleys)
are the open card. P1-labeled; CPU-only 57 s + 11 s probe; no live changes.

Artifacts: l39/{PREREG.md, results_l39.json, traces.npz, probe_h110.json,
ctrl.png, results_l39_v1_bug.json}; l39_controller.py, l39_probe.py,
l39_fig.py. Figure ctrl.png vision-PASS (2 fix passes: half-scale block
geometry + legend overlap).

## L40 — release-composition (tick 57, 11-12)

**Question.** L38 made the action set two-sided: DNg88 −8 is a STOP channel
(S .49→.06–.12), DNge046_L +0.2 a viable HOP. Do they compose — fired
together or staggered (stop-then-go / go-then-stop) — or does the release
rupture what the hop needs? PREREG l40/PREREG.md (two disclosed analysis
addenda, rollouts deterministic/unchanged).

**Setup.** L32 arm-A frozen substrate (21,516/2,977,920 asserted), no mech
entrainment (kept pure; the entrain join is a later card). Paired ctl + 7
arms, one generator + shared per-step noise, drives after settle, per-arm
drive table, dm probes on drive cells, af asserts every phase. Window:
PRE 25 s / ON 30 s (2a 15 s + 2b 15 s) / POST 45 s; seeds 11/22/33.

**C0 PASS (epoch-matched).** The shared-noise control reproduces L38's
controls EXACTLY on L38's own window: f_Ti 0.800/2.044/1.911 (err
0.0/.004/.001); free arm bit-identical (dm 0.0, 3/3). V1's C0 "fail" was a
window artifact — the free cord MIGRATES attractors (by 60–104 s the ctl
sits at 3.34/3.46/2.02 Hz), so freq anchors must be epoch-matched (L34
window lesson, now at 100-s scale). **C1 PASS all arms** (drives land in
every firing sub-window; pre-first-drive off-windows dm exactly 0.0 = no
leakage; post-first-drive off-windows are CARRYOVER, reported ungated — the
release's divergence persists at DNg88 ~0.80 through 2b, and reaches the
hop cells ~0.47). **C2 PASS** — release stops: ON-window S .109/.129/.117
vs ctl .47–.49, with measured KILL KINETICS (2a partial .15/.15/.23 → 2b
dead .13/.04/.04; ~15 s to full stop at −8). DNg88 un-pins 1.00→0.24
in-run (census mechanism confirmed).

**C3 PASS — stop-then-go composes.** After the release kills the rhythm in
2a, the 2b hop still lands (f-shift vs ctl 1.04/0.16/1.52 Hz; ≥.3 in 2/3,
dm > .01 3/3) and antiphase RECOVERS once drives are off (POST S
.516/.452/.364, all ≥ .25). The stop is NOT a rupture. **C4 layered** —
simultaneous (joint) is partial interference, not release dominance: ON S
[.325,.144]/[.05,.17]/[.208,.363] (seed-dependent; seed 22 killed, 11/33
half-preserved), POST S .43–.46 universal recovery. **C5 PASS** — no
lasting damage: POST rhythm ratio ≥ 95 in every arm (gate 10).

**Verdict.** Stop-and-go is ONE gesture vocabulary at this fidelity: the
discrete action set (L38) composes sequentially for free and simultaneously
with bounded (recoverable) structure cost. Combined with L39 (entrain+hop
holds frequency trajectories), the endgame controller vocabulary is now
{entrain, hop, stop} with composition rules measured. P1-labeled; CPU-only
204 s ×2 + fix reruns; no live changes.

Artifacts: l40/{PREREG.md, results_l40.json, traces.npz, run.out,
release.png, release.svg}; l40_release.py, l40_fig.py. Figure vision-PASS
(1 bolden pass).

## L41 — structure-preserving transitions (tick 58, 11-12)

**Question.** L39's winner (entrain + DNge046_L square hop) tracks the stepped
target 0.7→1.4→0.7 Hz but antagonists dip/invert through transitions (min seg
S(Tr) −0.316). Can any of the three registered guards — ramped envelope,
phase-timed onset, per-side split — hold seg S ≥ .25 in all 9 (seed,segment)
cells while keeping the hop's tracking win (~.001 err)?

**Arms** (L39 machinery verbatim, shared-noise paired, PREREG first):
base = L39 ent_h046 (square 40 steps, amp .5, 2×DNge046_L, at boundary);
ramp_mm (2-s triangle, mass-matched peak .198); ramp_pm (triangle peak .5);
phase (square, onset delayed to the next L-flexor-peak drive phase from
seg0's circular-mean phase, 53-74 peaks detected, onsets +8..+44 steps);
side (square split .25 L + .25 R); combo (mass-matched triangle .1 L + .1 R,
phase-timed). Gates G1 (all 9 cells S ≥ .25) and G2 (seg1 err ≤ max(.05,
base) AND mean(segs1-2) ≤ base+.03) pre-registered.

**C0 anchors PERFECT.** free_f {0.800, 1.444, 1.424} exact; the base arm is
BIT-IDENTICAL to l39/results_l39.json ent_h046 (max ΔS 0.0, Δtrack 0.0, Δdm
0.0, first_div equal) — the l39 controller replication is exact, all
candidate deltas are real.

**No guard passes.** G1 fails for all five candidates (min seg S: ramp_mm
+.135, phase +.093, ramp_pm −.124, side −.006, combo −.038 vs base −.316).
G2 fails for all five: only the hard square volley buys the seg1 lock
(err .001/.002/.001); every gentler/staggered form loses it on ≥1 seed
(ramp_mm .292/.002/.592, side .281/.0/.333, combo .004/.001/.336 — combo
holds 2/3). **The tradeoff is the finding**: volley mass at the boundary
buys frequency lock; the same mass makes antagonist organization a
seed-dependent lottery. Neither envelope shape, nor phase timing, nor side
splitting buys both.

**Mechanism (layered).** (1) The dips are NOT transition transients: for the
inverted cell (base seed 33 seg1) S AT the transition window is +.724 —
healthy — and the inversion develops over the following 15 s: the hop SELECTS
a post-transition attractor (L38 attractor-hopping, now measured on
structure, not just frequency). The inversion is BILATERAL (SL −.20, SR −.21
both flip), not a metastable side-flip (L33). (2) The frequency step alone
already breaks structure: ent (no hop) dips to .190 seed 33 seg1 and .212
seed 11 seg2 — while the free cord never dips below .36. Structure loss
through transitions is substantially the ENTRAINMENT re-locking transient
(L34's locking-onset cost) plus the hop's attractor selection on top.
(3) Phase timing HURTS (seg1 S .093/.495/.280 vs base .326/.286/−.316; the
pre-volley drift window + the mid-cycle landing is worse than firing at the
boundary). (4) P1 prediction held for side but broke for combo: dm@046R ==
0.0 exactly under the .25 square (ceiling-pinned, L38) yet the gentler .1
triangle CROSSES into visibility on seed 11 (dm .972) — census "pins" are
attractor-state-qualified, not absolute. (5) The gentle ramps DO fix the
catastrophic cell (seed 33 seg1: −.316 → +.622 ramp_mm / +.525 side / +.457
combo) — the worst failure mode is preventable; the .25 floor in 9/9 cells
is not, at this fidelity, by volley shaping alone.

**Consequence for the endgame (folded into L42).** Structure repair is a
POST-HOP problem, not a volley-shape problem: the L34 entrain drive at amp
.3 re-hosts antiphase (+.35) after locking — the stack card should measure
STRUCTURE-RECOVERY LATENCY (steps from hop to S ≥ .25) with entrain amp as
the repair knob, instead of gating on volley envelopes. The controller's
honest state is: frequency = controllable (hop/entrain), antagonist
organization = monitored-and-repaired, not guaranteed.

P1-labeled; CPU-only 97 s; deterministic; af asserts clean; no live
changes. Artifacts: l41/{PREREG.md, results_l41.json, traces.npz, run.out,
transitions.png, transitions.svg}; l41_transitions.py, l41_fig.py. Figure
vision-PASS (2 passes: rotated panel-B labels).

## L42 — entrain-hop-stop-stack (tick 59, 11-12)

Task 0.7 -> 1.4 -> STOP (10 s, target 0) -> 0.7 Hz on the frozen L32
substrate; arms free / ent (.3) / entstop (ent + DNg88 -8) / stack (ent +
hops @2000+@5000 + stop) / stack_lo (stack, entrain .03). Hop = l39 volley
verbatim (DNge046_L, amp .5, 40-step square). PREREG l42/PREREG.md written
first (one PRE-run amendment: l39 tracking convention; one POST-run
deviation disclosed: recovery window starts at 5000, not the registered
5040 — 40 steps generous, no gate flips).

- C0 PASS, bit-identical anchors: free [0,6000) and ent+stack [0,4000) vs
  l39 free/ent/ent_h046, entstop vs own ent — all max|diff| EXACTLY 0.0
  (the fourth consecutive l39-anchored replication).
- C1 PASS: every primitive lands — hop1 volley_max ~.47 first_div 0; stop
  dm ~1.01 with DNg88 un-pinning 1.0 -> .14-.17; restart volley vm ~1.0
  with the x046 rise probe .53-.56 (carryover-disambiguated).
- C2 PASS: seg1 track_err .001-.002 (l39's hop win intact through the
  longer trajectory); restart lock ttl = 1 block 3/3 — at 0.7 Hz re-lock
  is easy and the restart hop is NOT needed for frequency (entstop
  identical); the hard target remains 1.4 (L39).
- C3 FAIL — the measured finding: -8 for 10 s does NOT park a released-
  entrained cord. mm rhythm ratio through the stop 66-140 (ent, drive
  simply switched off, keeps 60-67); amplitude depth only ~halved
  (.22/.38/1.08). L40's ~15-s kill was measured on the INTRINSIC cord;
  the entrained-release regime is stop-resistant at this duration (longer/
  stronger untested — honest open card L43). What the stop DOES reliably
  do in 10 s: suppress antagonist STRUCTURE (S_roll medians fall to
  +.06/+.09/+.15 from seg1's .18-.28).
- C4 PASS, 89 steps (0.9 s) 3/3 after restart — scoped: fast RE-LOCK, not
  resurrection (structure was suppressed-not-dead at stop end because C3
  failed); the resurrection latency remains unmeasured.
- NEW endgame number: seed 11's hop1 inversion (rolling S never
  persistently >= .25 for 3049 steps = 30 s, through seg1 AND the stop)
  clears EXACTLY at the restart — the stop-restart combo is the most
  reliable structure-REPAIR event measured (L41's "repair is
  post-disturbance" prediction confirmed constructively).
- C5 PASS: the repair knob is the ENTRAIN AMP — stack_lo (.03) never
  recovers seg3 structure (S medians -.07/-.48/-.16; recovery null 2/3)
  and tracks poorly (seg0 err .21-.90); .3 recovers 3/3. L34's
  re-hosting arm is the stack's structure engine.

P1-labeled; CPU-only 84 s; deterministic; af asserts clean; no live
changes. Artifacts: l42/{PREREG.md, results_l42.json, traces.npz, run.out,
stack.png, stack.svg}; l42_stack.py, l42_fig.py.

## L43 — stop-dose-resurrection (tick 60, 11-12)

Question: L42's stop (DNg88 −8 × 10 s) suppressed structure but did NOT park
the entrained cord. Two numbers were missing: the KILL DOSE (does any
duration × amp reach L40's intrinsic-cord kill, rhythm ratio < 5?) and
RESURRECTION latency after a stop that parks.

Protocol (PREREG first + disclosed addendum): 3×3 dose grid (10/20/30 s ×
−4/−8/−12 on DNg88, drive OFF during stop) + ent reference + entx
(drive-ON-through-release at the deepest dose), 11 arms × 3 seeds on the
frozen L32 substrate, l42-verbatim machinery, shared per-step noise.

**C0 PASS (5th consecutive anchor)**: all 11 arms + entx bit-identical to
l42 `stack` over [0,4000), d10a8 over [0,5000), ent vs l42 `ent` — max|d| = 0.0.

**C2 FAIL = the finding: NO KILL DOSE EXISTS.** Even 30 s at −12 with DNg88
fully un-pinned (X 1.0 → −0.01) leaves the cord rhythmic (late ratio 87–171
vs ent's own 763–1913; post-stop ratios 264–1424). L40's ~15-s kill was the
INTRINSIC cord; 40 s of entrainment history makes the cord stop-RESISTANT —
protection is the entrained STATE (basin memory), not the drive during the
release (drive-off arms survive too). The stop primitive can suppress
STRUCTURE, never park this cord.

**Structure dose-inverts (the honest cost):** during-release rolling-S median
at d10a12 −0.29..+0.15 → d30a12 −0.74/−0.74/−0.33 — deep doses INVERT
antagonism (negative S = anti-phase flipped), not merely damp it.

**C4 layered (fixed entx, addendum disclosed):** v1's target_a collapsed
entx to a d30a12 duplicate (bit-equal — third instance of the L39-v1
drive-wiring class). Fixed lone-arm rerun (anchor 0.0 = stream replication
proof): drive-through DOES attenuate — rhythm ratio 522–1386 vs 87–171,
during-release S +0.07/+0.20/−0.12 vs −0.74/−0.74/−0.33 — but the registered
"re-hosts" bar (S ≥ .25 on 3/3) fails: structure still sags under the
release with the drive ON. Graded protection, not immunity.

**C5 (premise failed, number delivered):** nothing parks, so "resurrection"
reads as REPAIR-FROM-INVERSION: S returns ≥ .25 within 9–279 steps
(0.09–2.8 s) of drive resuming at every dose — structure repair is fast and
dose-robust even from S = −0.74. C1: −4 never un-pins DNg88 (X = 1.00 =
sub-threshold release, L38 two-sided arithmetic; −8 partial 0.13–0.17,
−12 full −0.01). C3: no consistent amplitude ordering in late ratio (noisy).

Endgame consequence: {entrain, hop, stop} is complete as a vocabulary, but
"stop" is a structure-suppressor + frequency-blank, NOT an off-switch on an
entrained cord; a true park requires either killing the intrinsic attractor
(L40 regime) or a different channel.

P1-labeled; CPU-only 245 s + 37 s (entx rerun); deterministic; af asserts
clean. Artifacts: l43/{PREREG.md, results_l43.json, traces.npz, raw.npz,
run.out, run_b.out, dose.png, dose.svg}; l43_dose.py, l43b_entx.py, l43_fig.py.

## L44 — entrain-history-protection (tick 62, 2026-11-12)

Question: is L43's stop-protection GRADED in entrain-history length or
THRESHOLDED (basin entry)? Arms H in {0,5,10,20,40} s of 0.7 Hz mech
entrainment immediately before a fixed stop (DNg88 -8, 20 s), free-settled
cord, one shared noise stream per seed, no hop. l44_history.py exit 0
(CPU 82 s), substrate 21,516/2,977,920 asserted, C1 PASS (entrain lands
dm>0, prefix bit-identity h5/h10/h20 vs h0 exactly 0.0, x88 un-pins
everywhere). CPG-core cells (Pugliese names, 6 cells each) recorded per the
tick-61 amendment.

ANCHOR CORRECTION (disclosed, PREREG ADDENDUM 1): the pre-registered ratio
anchor (late_ratio < 5) FAILED 0/3 — because it was never true: L40's OWN
stored rel arm shows r_mm 183-874 DURING its kill stop; the L40 kill was
always STRUCTURAL (S 2b .13/.04/.04 vs ctl .45/.46/.52). L44's h0
reproduces the structural kill at 20 s @ -8 (S_med_during
.159/.150/.067, recovering post .39-.51) = C0' PASS.

VERDICT — basin entry between 10 and 20 s, with a turbulent approach:
protection fraction (S_med_during >= .25) 0/3 -> 2/3 -> 1/3 -> 3/3 -> 3/3;
medians .15/.37/-.05/.46/.55. Short pulses (5-10 s) are a LOTTERY that can
INVERT structure (h5 seed33 -.05, h10 seeds 11/22 -.23/-.05 — worse than no
history; L41 attractor-selection class: a brief pulse selects the
post-stop attractor). >=20 s holds free-run-level structure through the
stop AND carries the entrained frequency through it (f_late 1.40 3/3 at
h0 vs 0.60 3/3 at h40 — the frequency fingerprint switches on with the
basin entry). The stop never silences the named CPG core specifically
(core ratio >=5 in 15/15 protected pairs), and entrainment RECRUITS it
(core pool X .155 -> .235-.244, saturating by 5 s of history) — the
protected state rides exactly the cells Pugliese et al. name as the
walking-CPG core. Disclosed window caveat: S_med_after window is 20 s vs
L40's 44 s; h40's post-stop S (~0.0-0.03 at 20 s) has not recovered in
that window while h0/h20 have — post-stop recovery latency of deep-history
cords is unmeasured (next-step note, not a claim).

P1-labeled; deterministic; CPU-only. Artifacts: l44/{PREREG.md (+ADDENDUM
1), results_l44.json, results_l44_add.json, traces.npz, raw.npz, run.out,
history.png, history.svg}; l44_history.py, l44_addendum.py, l44_fig.py.
No live changes.

## L45a — Pugliese pruning screen on our intrinsic rhythm (tick 63, 2026-11-13)

Transplant of the Nature-2026 walking-CPG screen onto OUR frozen regime:
clamp the named core types to X=0 (activity clamp, 50 s) while the intrinsic
rhythm runs. 14 arms x 3 seeds (l45_prune.py, CPU 281 s; run-1 rollouts died
in analysis on a list-round bug — deterministic rerun; PREREG first + 2
disclosed addenda). C1 mechanics PERFECT: prefix bit-identity 0.0 all arms,
clamped X max exactly 0.0, op point in range. Random-type null bar 0.087
(3 types drawn from a 199-candidate pool with the same {T1,T2,T3}x{L,R}
structure).

VERDICT (layered, P1):
1. NO KILL AT ANY DOSE — the rhythm's EXISTENCE is sheet-distributed. Even
   c_coreAll (all 36 cells of the 6 named types) leaves ratio 1531-2206 =
   3-8x BASE's own 218-535 and S +0.33..+0.54: wholesale clamping SHARPENS
   the rhythm. Honest contrast with their 86%-of-screens spiking result: at
   rate fidelity no 6-cell (or 36-cell) core owns the rhythm's survival.
2. But the named core is NOT inert — TWO cells own the rhythm's STRUCTURE
   through their BALANCE:
   - c_E1 (IN17A001, DNg100's direct target): effect 0.896 = 10.3x the rnd
     bar (3/3): frequency SLOWS 3/3 (1.29->0.88-1.00, 1.42->0.54-0.62,
     1.46->1.04-1.08 Hz) and antagonist S INVERTS 2/3 (+.49 -> -.385/-.443).
   - c_X464 (INXXX464, DNb08's top target, the E1-slot of the strongest
     triads): effect 0.498 = 5.7x (3/3): S collapses to ~0 (-.012/-.001/
     -.016 = decorrelation, NOT inversion) while rhythm ratio is the HIGHEST
     measured (983/454/415 vs base 535/318/218). Clean dissociation: the
     rhythm-amplitude carrier and the antagonist-structure carrier are
     DIFFERENT cells.
   - E2/I1/I2/E3 individually indistinguishable from noise (0.24-0.86x bar).
3. MEDIATOR PROBE (l45_probe.py, 100 s, bit-exact anchors): c_E1X464 = FULL
   RESCUE (f 1.25/1.48/1.46 = base band; S +.472/+.633/+.446; ratio 1485/
   999/1081); c_E1I2E3 does NOT rescue (S -.35/-.049/-.516, f still slowed);
   c_I2E3 alone inert. So E1's disruption travels THROUGH X464: E1
   restrains X464; clamp E1 -> X464 unopposed -> flexor bias (static
   in_Trf: E3 .043 > X464 .026 > I2 .020 > E1 .0009) -> slow + inverted
   antagonists. The DNg100-pathway cell and the DNb08-pathway cell are each
   other's COUNTERWEIGHTS — the two Pugliese pathways meet as antagonists
   at the structure level in our model.
4. PER-LEG (C4): E1@T1 (2 cells) and core@T1 (6 cells) collapse S to
   .04-.14 (3/3, 4.4-4.8x bar) without touching f: antagonist structure is
   per-leg concentrated; frequency is not.

Consequences: (a) L45b attractor census MUST carry the structure axis (S
sign) as a state variable — the E1/X464 balance selects among {antiphase,
decorrelated, inverted} and both are 6-cell channels = cheap control knobs
alongside the L36 DN vocabulary; (b) "silencing the CPG core kills walking"
does NOT transpose to rate fidelity — existence vs structure must be
claimed separately in any core-silencing story.

Artifacts: l45/{results_l45a.json, results_l45a_probe.json, raw_l45a.npz,
probe_traces.npz, PREREG-L45a.md + addenda, prune.png}. Figure QA: vision
endpoint timed out 3x this tick — analytic QA instead (per-pane ink density,
label-strip render, no title overflow, rotation-spacing math 20px > 10.5px
text height); disclosed. No live changes.

## L45b — attractor census + channel transition edges (tick 64, 11-13)

PREREG-L45b.md (+2 addenda) first; l45_census.py (substrate l45a-verbatim,
16 base seeds, 6 tonic channels from t=50 s, paired same-seed counterfactual;
v1 had a per-arm-init bug CAUGHT by the C1 prefix bit-identity gate, fixed,
rerun clean: C0 6/6, C1 prefix max d = 0.0). Artifacts: l45/results_l45b.json,
raw_l45b.npz, run_l45b*.out.

- CENSUS: 6 states over 16 seeds — mid|+- 7, mid|+0 4, mid|00 2, mid|-0 1,
  mid|0- 1, slow|00 1. S_L positive on 11/16 (pinned axis); S_R roams +/0/-
  (fluid axis). 11/16 seeds migrate state within 60 s: the free cord is a
  FLUID attractor gas, not discrete wells. Anchor-grade replication: seeds
  11/22/33 SEG-A f = 1.35/1.45/0.70 EXACTLY l40's stored ctl-pre numbers;
  seed 33 migrates 0.70 -> 1.44-1.46 exactly as l40's post.
- EDGES (MOVED/HELD/same-as-base, 8 seeds per channel): DNg88 release
  (-8.0): 7/8 MOVED, ALL to mid|00 = STRUCTURE-STOP — rhythm persists
  mid-band while antagonist S decorrelates bilaterally (L45a X464-family
  signature: decorrelation WITH sharp rhythm). This refines L40's "kill":
  the stop channel kills ORGANIZATION, not oscillation. DNg95 (+.25):
  3 MOVED + 3 HELD, all S-sign tilts (SR 0 -> -), f untouched. DNg110 /
  DNge046 (L36's hop exemplars): 2/1 MOVED, 5 same, 1/2 HELD, ZERO
  fast-band hops — L36's registered expectation failed at census amp;
  tonic DN drive mostly falls INSIDE the spontaneous redistribution.
  E1 (+.25, 6 cells): 0 MOVED, 3 HELD, dm ~ 0 (absorbed). X464: 1 MOVED,
  3 HELD.
- VERDICT for the endgame controller: spontaneous migration (11/16 per
  60 s) is the NOISE FLOOR any transition claim must clear; only the
  release channel (structure-stop) and DNg95 (S-tilt) land outside it at
  census amp. Control vocabulary stays {entrainment L34, phasic volleys
  L24, structure-stop DNg88rel, S-tilt DNg95} — census-side quantification
  of L38's discrete-action verdict. No live changes.


## L46 — post-stop recovery kinetics (tick 65, 2026-11-13)

Question: L44's disclosed note — the MOST stop-protected arm (h40: S_dur
.39-.59) showed ~ZERO antagonist structure at the 20-s post window
(S_after -.037..+.032) while h0/h20 recovered (.37-.51). Window artifact
or cost of protection? Design: l44 machinery verbatim, post window 20 s
-> 120 s, arms {h0,h20,h40}, stop unchanged (DNg88 -8, 20 s), seeds
11/22/33. PREREG l46/PREREG.md first; l46_recovery.py exit 0 (CPU 102 s).

- C0 PERFECT (6th consecutive anchored run): prefix bit-identity
  max|mm_l46 - mm_l44| == 0.0 on ALL 9 arm-seed pairs over [0,8000) —
  noise-stream replication is the design; premise replicated exactly
  (h40 S20s -.037/.020/.032 = l44 stored; match to <5e-3).
- C1 PASS: entrain lands (dm .063-.074), x88 un-pins everywhere.
- C2 VERDICT: IMPAIRED — protection has a COST. h40 late-post S (median
  over [12000,18000)) = -.090/-.075/-.110, duty_late .000-.007: NO
  recovery in 120 s (duty DECLINES; SLOW-RECOVERY alternative refuted).
  h0 late = .448-.480, duty .995-1.0. late gap h40-h0 = -.53..-.57.
  h20 intermediate (.371-.386 late, duty .85-.97). lat_first for h40
  reads 0.09 s — an artifact: S at stop-off is still the protected value,
  then collapses; first-crossing latency inherits the DURING-stop state,
  window medians/duty are the honest recovery metric.
- MECHANISM (per-side decomposition — pooled bilateral S ~ 0 HIDES a
  sign-inverted side, not decorrelation): h40 pre-stop S_R = +.62..+.77
  (entrainment organizes the right side bilaterally); late post S_R =
  -.47..-.49 INVERTED 3/3 seeds while S_L holds +.28. The cord sits in
  the L45b census state SL+|SR- and does NOT migrate out for 120 s
  (beyond the 11/16-per-60-s spontaneous floor; sign consistency across
  seeds is the tell — a selected attractor, not a re-roll). h0 re-rolls
  straight back to its intrinsic wiring-set organization (SL .63-.67 /
  SR .15-.19, matching its pre-stop pattern).
- The entrained STATE persists through the collapse: f_late h40 =
  0.717-0.733 (the 0.7 Hz memory holds 120 s post), CPG core stays
  recruited (.246-.249 vs h0 relaxed .154-.155), rhythm ratio HIGHEST of
  all arms (556-902 vs h0 246-542). Everything entrainment built
  persists EXCEPT the right-side antagonist phase relation, which the
  stop flips.
- Endgame spec line: the stop primitive is valid on a rested cord (h0:
  rebounds in seconds); on a deeply-entrained cord it leaves SL+|SR-
  for >= 120 s — budget a structure-repair primitive (L42: re-entrain
  restart is the most reliable repair event measured) after every stop
  on an entrained cord.
Artifacts: l46/results_l46.json, raw_l46.npz, traces_l46.npz,
recovery.png (vision-PASS 2 passes), PREREG.md. No live changes.

## L47 — repair-after-stop: the re-entrain restart is NOT a repair (tick 66, 11-13)

Q (L46's spec line): is the L42 re-entrain restart a sufficient repair
primitive for the post-stop SL+|SR- census state? Design l46-verbatim,
per-arm DRIVE TABLE: norepair / rep0 (entrain [6000,8000)) / rep60
(deferred [12000,14000)); all arms h40 deep-entrain then 20 s DNg88 -8.
PREREG l47/PREREG.md first. l47_repair.py exit 0 (CPU 103 s; run-1
analysis crashed on a boolean-index size mismatch AFTER the raw npz
checkpoint — L45a checkpoint lesson paid off; deterministic rerun).

- C0 PERFECT, 7th consecutive anchor: norepair bit-identical to l46 h40
  over the FULL [0,18000) window (0.0 x3 seeds); rep0/rep60 prefix
  [0,6000) 0.0 x6 — drive-wiring clean (no arm leakage).
- C1 PASS: repair lands (dm .063-.073 both arms x3 seeds; x88 un-pins).
- C2 NOT-REPAIRED everywhere (per-side gates): duty(both>=.25) late =
  0.000 in ALL 9 arm-seed cells — not one late sample with both sides
  organized. The 1-2 s lat_both crossings are during-drive transients
  (the L46 first-crossing lesson, third instance).
- MECHANISM, two layers:
  (1) DRIVE-HELD: during the repair drive the inverted side RE-ORGANIZES
      under it — S_R -.49 -> +.68..+.78 (pooled S +.56..+.70). The drive
      CAN cross the inversion; 20 s of it moves nothing persistent.
  (2) RELEASE = a fresh attractor lottery from the compromised posture:
      rep0 late — s22 falls back to the census state (SL +.32 / SR -.52,
      f .70, core .247 preserved: the restart was harmless); s11/s33 HOP
      (f 1.513/1.625, ratio 2582/6520) into a BOTH-SIDES-NEGATIVE state
      (SL -.19/-.36, SR -.29/-.42) with the CPG core partially
      discharged (.246 -> .196) — a state NOT in the L45b free-cord
      census (which sampled free evolution, not post-repair releases).
      rep60: same shape, 1/3 hop (deferred repair was not worse — with
      n=3 that is a suggestion, not a claim).
- Endgame vocabulary amended: {entrain, hop, stop} gains NO repair
  primitive from the restart; the restart repairs FREQUENCY transitions
  (L42) but not antagonist structure. Structure is drive-held only.
  Next lever (L48, seeded): shape the RELEASE (graded ramp-down — L41
  showed gentle ramps cure catastrophic inversion on hops) or extend
  dwell, and gate on the post-release window per side.
- Fig l47/repair.png vision-PASS 2 passes (fixes: t<T0S curve spill
  outside frames, in-pane legends relocated to empty bottom band);
  panel-C markers verified NUMERICALLY against the SVG (18/18 exact)
  after vision's description claimed 'all circles above gate' when 3/9
  sit below — the figure was right, the description was not.
Artifacts: l47/results_l47.json, raw_l47.npz, traces_l47.npz,
repair.png/svg, PREREG.md. No live changes.

## L48. repair-release-shaping (tick 67, 2026-11-13)

Question: L47 showed the re-entrain restart is drive-held and its hard-off
release re-runs the attractor lottery. Does a GRADED release (entrain amp
0.3 -> 0 over 10/30/60 s) or LONGER dwell (60/120 s then hard-off) carry
the during-drive bilateral structure (S_R +.75) across the release?

Setup: l47-verbatim machinery, WIN 24000 (240 s); shared prefix ent-0.7 Hz
amp .3 [0,4000) + stop DNg88 -8 [4000,6000); arms norepair + rep0
(anchors) + ramp10/30/60 + dwell60/120; per-arm AMP table, one generator,
shared per-step noise. PREREG l48/PREREG.md first. CPU 266 s.

- C0 PERFECT — 8th consecutive anchor in the chain: norepair AND rep0
  bit-identical to l47 stored traces over [0,18000) (0.0 x6); every
  treatment arm prefix-identical to norepair [0,6000) AND rep0 [0,8000)
  (0.0 x18; no arm leakage — the DUR-span loop had to exclude norepair,
  caught at write-time: a generic full-amp span would have made norepair
  === rep0 and voided the anchor).
- C1 PASS: dm .068-.069 all arms/seeds over DUR; x88 un-pins everywhere.
- Premise reproduced: SR_dur +.676..+.777 in all 18 treatment cells.
- C2 NOT-REPAIRED for every shape — no release form carries bilateral
  structure across release: duty(both>=.25) post < .5 in 18/18 treatment
  cells (max .443). Nearest-ever cells: ramp10/s33 (SL +.53 / SR +.24,
  duty .41) and ramp30/s33 (SL +.54 / SR +.24, duty .44) — both miss the
  gates by <.02 on SR; dwell arms never come close (max duty .108).
- MECHANISM (the sharpening): structure persists THROUGH the fade and dies
  AT the amp->0 crossing — SR medians during the fades +.388..+.821 (9/9
  ramp cells, including cells that end up hopping). The lottery is
  release-CROSSING-carried, not release-ABRUPTNESS-carried: a 60-s
  adiabatic fade buys nothing over a hard-off.
- The lottery distribution over 18 treatment releases: bimodal, shape-
  INSENSITIVE. 13/18 hop to the 1.4-band (f 1.48-1.62, ~+0.9 Hz hop from
  the locked f_dur 0.700 in 18/18); 5/18 keep the 0.7-band census state.
  dwell does NOT deepen the 0.7 basin (dwell120 hops 2/3 = rep0's rate).
  Bilateral-positive post states EXIST but are rare and unselected:
  ramp10/s33 (0.7-band SL+|SR+) and ramp30/s33 (1.4-band SL+|SR+), 2/18,
  both seed 33, both ramps.
- core_post is bimodal {.1954-.1975} vs {.2460-.2536} and tracks the
  frequency band in 16/18; 2 exceptions (ramp30/s33, dwell60/s22) hop
  while keeping the core recruited (.249/.254) — both strong-left cells.
  The CPG-core discharge is a concomitant of the hop, not its cause.
- norepair floor probe: the post-stop SL+|SR- census state holds 3/3 out
  to 220 s post-stop (extends L46's 120 s; it NEVER self-repairs).
- lat_both 0.09-s values are the L46 first-crossing artifact (4th
  instance: crossing inherits the during-drive high state at release-off).
- Endgame spec line: repair-after-stop is NOT achievable by release
  shaping within this vocabulary — a controller that needs bilateral
  antagonist structure after a stop must KEEP the entrain drive on
  (structure is drive-held, L47+L48); stops remain parked-segment tools.
- Fig l48/release.png vision-PASS 3 passes (legend collisions x2, then
  subtitle count 17/18 corrected to 18/18 by numeric QA — every described
  figure claim re-derived from results json: duty 18/18, hop 13/18, fades
  +.388..+.821, ramp30/s33 +.536/+.235/.443, norepair state set).
Artifacts: l48/results_l48.json, raw_l48.npz, traces_l48.npz,
release.png/svg, PREREG.md. No live changes.

## L49. drive-gap-tolerance (tick 68, 2026-11-13)

Question: with bilateral antagonist structure established under continuous
0.7-Hz entrain, how long can the drive be SWITCHED OFF before structure
collapses — and does it re-form on resume? The scheduling-slack number a
real gait controller budgets around. Design: h40 prefix (l46-l48 verbatim,
anchor-grade), then gap 5/10/20/40/80 s drive-off, then drive on 60+ s;
6 arms x 3 seeds, shared noise, WIN 18000; PREREG first. l49_gap.py exit 0,
CPU 176 s.

Verdict (layered): SLACK = 5 s, SHARP — and the "safe state" itself is
only marginal in time.
- C0 PERFECT, 9th consecutive anchor: all 18 arm-seed prefixes bit-identical
  to l48/traces_l48.npz mm_norepair [0,4000) (max|d| 0.0) + pairwise exact.
- C1 PASS after a disclosed one-step operationalization: first divergence
  from cont at t=4001 uniformly (the sensory-side drive enters W
  postsynaptically; motor readout lags one synaptic step — registered
  "exactly 4000" was my wording error, not a wiring issue); dm_gap > 0
  in 15/15 (drive-off is real); amp-table asserts green; af clean.
- C2 the slack curve: gap5 HELD 3/3 (both sides >= .25 at end-of-gap);
  EVERY arm >= 10 s collapses — t_collapse 5.49-5.69 s sustained, 15/15
  arm-seeds, i.e. the collapse time is gap-LENGTH-INDEPENDENT (the cord
  does not degrade gracefully; it exits the driven state at ~5.5 s).
  End-of-gap reads at longer gaps are LOTTERY draws from the L45b census
  gas, not tolerance: 3/12 long-gap cells re-held (gap20/s33, gap80/s33 —
  both seed 33, the L45b migrator), seeds 11/22 end SL+|SR- (s11) or
  both-negative (s22). Never read an end-point without t_collapse.
- C3 resume: re-formed sustained-5s in 15/15 (0.09-50.8 s). The axis
  entrainment builds (S_R) re-builds fast and holds: S_R resume medians
  +.676..+.793 everywhere (l47's during-drive S_R re-organization, now
  median over a full 60-s window). S_L is the marginal axis — and P0
  FAILED as registered: even the CONT arm holds both sides only weakly
  (duty_both .157/.427/.559 over 140 s; SL med .233/.281/-.096; seed 33
  flips S_L mid-window under CONTINUOUS drive). The L48 spec-line premise
  ("continuous entrain = the only both-sides state") is WINDOW-SCOPED:
  true on the 20-40-s horizons L44/L48 measured, marginal-in-time at 140 s.
  So the C3 PARTIALs are the operating point's S_L ceiling, not a gap cost.
- C4: max safe gap = 5 s (registered class (i) graded; crossover measured
  at exactly the 5/10-s boundary — sharper than my registered guess of a
  5-40 s crossover). Rhythm PERSISTS through every gap (f_gap .60-1.56,
  f_resume 0.700 locked 15/15) — structure dies, oscillation does not
  (L43-consistent, now on pure drive-gaps). Core stays recruited through
  gaps (.196/.248 bimodal as l47/l48).
- Controller line: budget drive gaps < 5 s; after any longer gap the
  rhythm is intact but bilateral structure is a fresh lottery draw, and
  resume re-forms S_R in seconds while S_L needs the same ~45-s re-build
  window as from scratch (and is marginal even then at amp .3).

Deviations disclosed (PREREG addendum): C1 first_div gate re-operationalized
HIST -> HIST+1 (one synaptic step, uniform 15/15); lat_sust5 computed with
hold=5000 steps (50 s) in-run — caught post-run, recomputed from
traces_l49.npz at the registered 500 steps (5 s), results json annotated;
cont f field initially stored the FFT ratio — corrected to freq (0.700
3/3, ratio 7e4-1.2e5) with f_ratio retained.
Fig l49/gap.png vision-PASS 2 passes; every described claim re-derived
numerically (caught own wrong panel-A end-state label: s22 ends
both-negative, not SL+|SR-; SR range .676-.793 -> .68..+.79; cont SL med
.23/.28/-.10 substituted for the looser duty range).
Artifacts: l49/{results_l49.json, raw_l49.npz, traces_l49.npz, gap.png/svg,
PREREG.md, run.out}. No live changes.

## L50 — always-driven-trajectory: the cost table (tick 69, 2026-11-13)

Question (LANE.md ideas-24): with the vocabulary complete {entrain, hop,
stop} and the slack number measured (L49: 5 s), run the honest full-stack
trajectory demo — 0.7 -> 1.4 -> 0.7 Hz, hops at both transitions, no stop
segments — and score the trade: tracking err + bilateral S duty + drive-on
seconds, always-driven (allw, 64 s) vs drive-budgeted variants (duty58 =
5-on/4-off cycles at the slack cadence, 40 s; min5 = 5-s prime per
segment, 19 s). PREREG l50/PREREG.md first; l39-verbatim machinery (ONE
generator, shared per-step noise, global phase), 5 arms x seeds 11/22/33.

Verdict: TRACKING COSTS DRIVE, STRUCTURE DOES NOT FOLLOW — the two
objectives CONFLICT in the fast segment, and the drive budget is nearly
free.

- C0 PERFECT — 10th consecutive anchor in the l39-l50 chain: free, ent,
  allw(=l39 ent_h046) mm traces BIT-IDENTICAL to l39 over the full
  [0,6000) window (0.0); duty58/min5 prefixes bit-identical to ent over
  [0,500). A0 analysis anchor 0.0 — my segment-S code reproduces l39's
  stored values exactly (free/ent/allw, all 9 seg values). C1 PASS
  (first_div allw 2000 / duty58+min5 500 exactly; volley lands ~1.0;
  af in range).
- COST TABLE (mean duty / seg1 err): free 0 s, .455 / no lock;
  min5 19 s, .284 / .289; duty58 40 s, .576 / .922; ent 64 s, .307 / .205;
  allw 64 s, .285 / .001 (locked, ttl 1-2).
- THE INVERSION (P2 PASS by EXCEEDING): duty58 beats allw on bilateral
  duty on every seed (.884/.387/.458 vs .387/.347/.120; mean .576 vs
  .285 — DOUBLE) at 62% of the drive. The 4-s off windows cost nothing
  (split: duty_on .536 / duty_off .563) — the L49 slack harvests clean.
  But duty58 LOSES the fast-segment lock (seg1 err .93; segment FFT
  still peaks 1.4 for seeds 22/33 but per-block f bounces .4-1.4; seed
  11 falls to a .35-Hz off-target lock in seg0 AND seg1 — chopped
  entrainment is intermittent).
- THE TOXICITY (new number): the 1.4-Hz segment is structure-toxic under
  CONTINUOUS drive — allw seg1 duty .022, ent .133, vs free .538 and
  duty58 .454: the UNDRIVEN cord has MORE bilateral structure in the
  fast segment than the continuously-driven ones. The hop that buys the
  lock (ent seg1 .133 -> allw .022) pays for it in structure — L41's
  attractor-selection mechanism, now measured as a per-segment duty.
- P3 registered prediction FAILED at parity: min5 duty .284 ~= allw .285
  (gate wanted < .5x). The collapse is real (7/9 off spans collapse at
  4.99-6.99 s, latency gate PASS — L49's ~5.5 s confirmed) but the 5-s
  re-prime rebuilds to ceiling-equivalent duty, and the L48 release
  lottery sometimes holds THROUGH a 15-s gap (seed 11 seg2: collapse
  latency 14.99 = never; duty .813). Parity, not preservation: min5's
  structure is temporally clustered (5 s alive / 15 s dead), duty alone
  hides the clustering.
- Controller spec from the whole chain: frequency tracking needs
  continuous drive (allw only, err .001); bilateral structure prefers
  chopped or no drive; the two axes must be scored SEPARATELY, never
  summed. A real gait controller should schedule: continuous drive where
  tracking is critical, duty-cycled where structure is (L51 queued:
  the hybrid schedule).

Deviations: none — all registered gates ran as written; P2's seg1-err
companion was registered descriptive and failed (disclosed above); the
one .453/.454 is a rounding path (mean of rounded vs rounded of mean).
Fig l50/cost.png vision-PASS 2 passes (legend clip fixed); every headline
number re-derived from traces_l50.npz (duty/collapse/seg tables exact).
Artifacts: l50/{results_l50.json, raw_l50.npz, traces_l50.npz,
cost.png/svg, PREREG.md, run.out}. No live changes.

## L51. structure-aware-hybrid-schedule (tick 71, 2026-11-13)

Question (ideas-25): L50's table implies CONTINUOUS drive in the
tracking-critical fast segment, DUTY-CYCLED 5-on/4-off in the
structure-carrying 0.7 segments — does the hybrid hold allw-level
tracking (seg1 err <= .01) at duty58-level structure (pooled duty
>= .5)?

Construction: l50 machinery verbatim; hybrid = duty58's exact AMPA table
on seg0/seg2, amp .3 continuous on seg1, hops at both transitions
(drive-on 48.0 s = 44 s of task + settle, vs allw 64 / duty58 40);
hynohop = same AMPA, no hops (hop-wiring reference, pre-registered).
PREREG l51/PREREG.md first, incl. a registered correction of the LANE
sketch's anchor sentence (prefix = allw through seg1 is infeasible with
a duty-cycled seg0; the strongest construction-permitted anchor is
hybrid == duty58 over [0,2500)).

Anchors: C0 PERFECT — allw AND duty58 bit-identical to l50 stored traces
full window (0.0, 11th consecutive chain anchor); hybrid == duty58
through [0,2500) (0.0); first_div(hybrid,allw)=500,
first_div(hybrid,duty58)=2500, first_div(allw,duty58)=500, all exact
3/3. C1 PASS: first_div(hybrid,hynohop)=2000 exactly (hop wiring),
volley_max ~1.0, af .181-.187 every arm.

THE TRIPLE (pre-registered gates):
- G1 TRACKING PASS: hybrid seg1 err .0037/.0007/.001 — allw-level
  (.01 gate cleared 3/3).
- G2 POOLED FAIL: duty .489/.582/.382, mean .484 (misses .5 by .016;
  s33 .382 under the .45 floor).
- G2' WINDOW-SCOPED PASS: 0.7-window duty .667/.56/.573, mean .600
  (duty58's own 0.7-window duty .638).
- VERDICT (pre-registered mapping, G1+G2'+not-G2): the conflict is
  IRREDUCIBLE AT THE FAST WINDOW at amp .3 — the hybrid holds
  allw-level tracking AND duty58-level structure in their respective
  windows; no schedule can serve both in the fast window itself, so the
  endgame controller spec is complete in WINDOW-SCOPED form and carries
  tracking and structure as separate numbers (L50's spec line, now
  constructive).

Mechanism, three findings beyond the gate:
- The fast window is a seed LOTTERY, not a fixed toxicity: hybrid seg1
  duty .133/.627/0.0 (mean .253) vs allw's uniformly toxic .022 —
  same continuous 1.4 drive, different entry state (chopped vs
  continuous seg0). L50's ".022 toxicity" needs the continuous-entry
  qualifier; the outcome is attractor-selection at the transition
  (L41/L47 class), state-conditional.
- The hop is STATE-CONDITIONAL (hynohop arm): from chopped entry the
  continuous 1.4 LOCKS WITHOUT the hop (err .0007/.0013/.0027; l39's
  continuous-entry ent missed at .21-.29) — and the hop COSTS structure
  when it is unneeded (hybrid s33 seg1 duty 0.0 vs hynohop .213; nohop
  pooled duty .496 > hybrid .484, tracking intact). The lock-buying
  volley is only needed from the continuous-entry state. n=3, one task:
  an observation for controller design, not a general claim.
- Hybrid on/off split in the 0.7 windows REVERSES duty58's: on .442 /
  off .637 — off windows read BETTER than on (seg2's on-windows follow
  the fast segment while structure is still re-forming; offs carry the
  re-formation). Seg0 duty .64 == duty58's .64 exactly (identical
  drives, bit-identical by construction — verified in-data).

Predictions scored (registered in PREREG): P_a PASS, P_c PASS; P_b FAIL
— direction right (G2 fail) but the registered .30-.45 band missed
(.484): the fast window read .253, not the .02-.13 predicted from
allw's entry state; P_d FAIL — the registered surprise (nohop locked).
Next-step note (not a claim): the pooled gate is within reach by hop
SCHEDULING (nohop .496 with tracking intact) — a refinement card, not
shipped; L52's mechanism question is unchanged and now sharper (the
toxicity is entry-state-conditional).

Deviations: run-1 died at a WRITE-TIME table assert (my assert wrongly
applied the chopped pattern to the hybrid's by-design constant fast
segment; the wiring was correct, the assert was fixed — zero rollouts
wasted, the L39v1/L43v1/L48 write-time-check discipline working as
intended). Vision endpoint timed out twice at figure time — analytic QA
substituted and disclosed: 0 text overflows, 0 label collisions (bbox
scan; one duty58-tail/hybrid-label collision found and FIXED by label
re-staggering), both .5 gate lines present, per-pane ink density
confirmed (A .027/B .021/C .021 bright-pixel content); figure claims
re-derived numerically from artifacts (all exact).
Artifacts: l51/{results_l51.json, raw_l51.npz, traces_l51.npz,
hybrid.png/svg, PREREG.md, run.out} + l51_hybrid.py, l51_fig.py.
CPU-only 66 s. No live changes.

## L52. why-is-fast-segment-toxic (tick 72, 2026-11-13)

Question: L50's toxicity number (allw seg1 duty .022 vs free .538) —
RE-LOCK TRANSIENT (settles with dwell) or SELECTED attractor (held low)?
Design: single 60-s treatment from the shared h40 state, no transitions,
no hops; 0.7 control (= l49 cont schedule through 10k, the anchor) x amp
{.3,.2,.1} and 1.4 x amp {.3,.2,.1}; duty(both S>=.25) in ten 6-s bins +
early/late 20-s windows. PREREG l52/PREREG.md (+2 disclosed addenda).

C0 PERFECT — 12th consecutive chain anchor: f07a3 mm AND SL/SR
bit-identical to l49/traces_l49.npz cont over [0,10000), max|d| 0.0 on
all 9 arrays; GC duty reproduces the stored-artifact {.360,.645,.112}
with EXACTLY equal boolean duty arrays (run-gate tolerance bug — 1e-9 vs
3-decimal registered — recomputed at registered precision, disclosed).
Anchor debugging (2 dead runs, zero waste): run-1 settle applied the
mech drive (l39/l50/l51 convention) while l49's settle is drive-free
(k>=0 guard) — two settle conventions coexist in the lineage; run-2 had
a DOUBLE settle phase (explicit pre-loop + in-step increments; ph_end
475.0 = 10,800 increments vs 457.4 = 10,400), localized by mm[0]-exact/
mm[1]-diverge -> step-0 drive -> ph_end arithmetic.

VERDICT: formally MIXED (neither registered gate fired) but the pattern
is one-directional on every seed — DWELL-DEEPENING COLLAPSE, the
OPPOSITE of a recovering transient (post-hoc label, in results json):
- f14a3 LOCKS 1.400 Hz perfectly everywhere (err 0.000, FFT ratio
  12-17k) while duty falls early {.237/.163/.120} -> late {0.0/.1/0.0}
  (slope -.237/-.063/-.120, negative 3/3). Bins show entry structure
  dying with seed-dependent lifetime ~6-30 s, non-monotone (s11 flares
  .783 at 18-24 s then dead; s33 dies in bin 1; s22 wobbles to 0).
- Mechanism (per-side medians): the fast state is structure-LESS or
  ONE-SIDE-INVERTED — s11 late SL -.523 (inverted) / SR +.10; s33 both
  fade (.07/.13); s22 holds both ~.19-.34 but under the .25 gate. The
  1.4 attractor never holds bilateral antagonism; what the h40 entry
  carried erodes inside it. Connects L41/L46: disturbance-selection now
  measured as a slow decay, not a step.
- Control f07a3 STABLE (early .363 -> late .381, slope +.018 3/3
  direction); s33's S_L stays marginal even at 0.7 (SL_late -.19) —
  L49's S_L ceiling replicated on the anchored arm.
- Amp sweep (t70 table, all 12 arm-seeds LOCKED — P3's low-amp-unlock
  prediction FAILED: from h40 entry even amp .1 holds the lock, basin
  memory carries frequency; L34's gentle-never-lock was free-run entry):
  1.4@.2 is the SHIFT point — s33 HOLDS a bilateral fast gait (.333->
  .397, the only seed at any amp), s22 just under gate, s11 dead; 1.4@.1
  is structure-free from the start (.01-.10 early -> 0 late); 0.7@.2/.1
  also lose the .25 gate (.218/.207, .218/.176). Toxicity conclusion
  HOLDS in sign at every amp; amp .2 buys a 1/3-seed lottery, never 3/3.
CONTROLLER LINE (closes L50's open mechanism): a structure-preserving
fast gait is impossible BY DWELL at .3 and a per-seed lottery at .2 —
the fast window stays structure-poor at any amp; keep L51's window-
scoped spec (score tracking and structure separately) and, if a fast
structured gait is ever needed, the lever is NOT dwell and NOT amp —
it is a different state class (e.g. L34 re-hosting at amp .3 via the
reflex arc after the transition, which L50 never gave time for).

Artifacts: l52/{PREREG.md, results_l52.json, raw_l52.npz, traces_l52.npz,
toxic.png/svg, run.out run2.out run3.out}; l52_toxic.py, l52_fig.py,
l52_verdict.py (GC recompute), l52_fig_qa.py (analytic QA). CPU-only
141+134 s (runs 1/3) + 31 s single-arm bisect; no live changes; duck
/needs 200, units active, no strays (checked at log time).
Fig QA: analytic PASS (vision endpoint down 3rd tick, disclosed) —
overflow scan, column-collision math (12 found -> fixed -> 0), polyline
frame containment, all 5 numeric claims diffed against the json exact.

## L53. trust-rule-saturation-audit (tick 73, 2026-11-13)

Field-informed by tick 70's digest of Asis 2611.09930 (depression-only
plasticity saturates; only a timing-asymmetric rule unlearns/relearns).
Audited OUR rule offline against the real substrate: 115,728 synapses into
331 DAN neurons; per-event v = X[src]*X[dst] captured from the REAL brain
through serve's exact stim path (20-step 200-ms window, 3 seeds); replayed
200-event sequences from the REAL visitor mix (194 day_logs: greet .34 /
water .29 / peas .16), nights every 50 events (2x replay + x0.98), arms
LIVE / TIMING (eta x2 within 5 events post-swat) / RAND (mass control).

VERDICT — the rule is SAFE where Asis's was fragile, blind where it isn't:
- P1 PASS: displayed trust pins at event 90 (late gain 0.0) — but the
  DISPLAY scale (mean*200) is the binding constraint, NOT the substrate:
  capf = 0.0000 everywhere (per-edge cap 0.5 unreached, ~100x headroom).
  Asis's saturation does NOT transfer: our negative side is multiplicative-
  proportional, not depression-only.
- P3 FAIL = good news: NO young-bond scar. Early alternating abuse holds
  trust at 0.02 during abuse (protective) but pin delay is only 90->99
  events; proportional erosion on low mass costs almost nothing absolute.
- P4 FAIL = honest null: TIMING == RAND on EVERY metric (pin/end/recovery/
  rejoin; heavy both 0.410) — timing carries no information beyond mass
  because the rule is mass-linear at these scales (never near CAP).
- P2 band-miss: post-swat recovery 6-7 kind events (registered <=5).
- G1 no erasure anywhere (sustained heavy abuse equilibrium 0.269, floor
  0.114); G2 no saturation harm.
- Observation card (not proposed): past pin the display is uninformative —
  every well-treated visitor reads 1.0; a wider/log display scale could
  use the substrate headroom. No live change proposed; audit descriptive.

Artifacts: l53/ (PREREG.md, capture_l53.npz, results_l53.json, traj_l53.npz,
trust.png vision-CLEAN 2 passes). Run: capture 82 s CPU + replay 1 s.

## L54 — trust-display-headroom (tick 74, 2026-11-13)

Question: L53 pinned the display scale (mean*200) as the binding constraint
(display pins at event ~90; substrate capf 0.0000). What would relationship
depth look like under slower scales, and which should we recommend?

Verdict: NONE of the three candidates passes — pin delay trades ~1:1 against
legibility, because the substrate's realistic dynamic range is only ~8x wide
(heavy-abuse equilibrium m=.00131 <-> mix@200 m=.01117) and S0's pin point
(m=.005) already sits mid-span. S0 STAYS (registered outcome; display is
visitor-facing — no live change without the owner anyway).

- Gates (PREREG l54/PREREG.md, registered before the run):
  S0 x200 (live ref): pin ev 94.3, sep .737, dip .161, order 3/3 — fails G1
    (it IS the constraint under audit).
  S1 lin20: pin 200 (never) but sep .197 (G2 FAIL), dip .016 (G4 FAIL).
  S2 sqrt20: pin 200, sep .310 (G2 pass), dip .033 (G4 FAIL).
  S3 log: pin 200, sep .392 (G2 pass), dip .042 (G4 FAIL — closest).
  Ordering (G3) holds 3/3 seeds under every scale; the scar-visibility gap
  (young-abuse vs mix @ev100) is tiny under ALL scales (.005-.020) — L53's
  no-scar finding is scale-invariant.
- REAL sessions (440 parsed read-only): 0/440 pinned TODAY — max m .00382
  (display .76 under S0), median m .000044. world (the one long-lived
  relationship, 64 events/4 days): m .00180 -> S0 .355, S1 .036, S2 .189,
  S3 .127; behavioral trust 0 (solo duck) so displayed = .5*syn.
  The pin is a DENSE-relationship phenomenon (~94 kindness events at audit
  cadence — far beyond every real visitor on this tree; world needed 4 days
  for 64 events of self-directed history).
- Blend (mask-or-sharpen): under S0 the syn term's late-window std is exactly
  0.000 when pinned (blend range compressed to [.5,1]) vs S1 .025 / S2 .031 /
  S3 .039 — but since no real session pins, the blend is informative for
  everyone real today. The masking problem only exists for the hypothetical
  dense visitor.
- Recommendation: keep S0. If a real visitor ever approaches the pin
  (watchdog line: m > .004), the shape that unpins WITHOUT losing legibility
  must be PIECEWISE (keep x200 slope below .005, compress above) — a single
  global form cannot do both on an 8x-wide m-axis. Registered as a note, not
  a card; revisit only when real data approaches it.

Anchors: A1 stored-traj reproduction FAILED as disclosed (l53 seeded seqs via
hash() -> PYTHONHASHSEED per-process; maxdiff .087) -> A2 crc32-seq fallback
with (a) double-run bit-identity max|dm| = 0.0 exactly, (b) band replication
under S0: pin 94.3 in [70,110] (L53 ~90), heavy end .263 vs L53 .269,
sep .737 vs .731. Scales are pure post-hoc functions of ONE shared m-traj —
the L39-v1 arm-leak class is structurally impossible.

Artifacts: l54/ (PREREG.md, l54_scale.py, l54_fig.py, results_l54.json,
mtraj_l54.npz, scale.png vision-PASS 2 passes — endpoint back up after 3
down ticks; 2 collisions found+fixed pass 1). Run: replay+survey 2 s CPU.
No live changes.

## L55 — hop scheduling: the conditional never fires; no policy owns the pooled gate (the attractor lottery does)

Question (LANE ideas-26): L51 left the pooled gate (.5) "within reach by hop
scheduling alone" (nohop .496 vs hybrid .484). Registered test: 2x2 hop
FACTORIAL (none / entry@2000 / exit@4000 / both) on the hybrid AMPA schedule
+ the LANE conditional policy (hop at KD=3000 iff in-flight fast-seg lock
err > THR .05). PREREG l55/PREREG.md first; substrate l51-verbatim
(21,516 nodes / 2,977,920 edges, l32 arm-A frozen, ENT_AMP .3, hops =
DNge046_L amp .5 for 40 steps); ONE generator + shared per-step noise
tensor; 5 arms x seeds {11,22,33}; CPU 97 s.

Verdict (registered mapping + exploratory completion):
- P1 PASS but DEGENERATE: the conditional NEVER fires (in-flight err at
  k=3000: .001/.0002/.0002, FFT ratio 1278-2975 = razor-locked) — cond is
  bit-identical to nohop (max|d| 0.0 full trace). Pooled [.511,.464,.513]
  meets >= .5 on 2/3 seeds exactly as nohop did. The trigger watches
  TRACKING, but at amp .3 all the variance is STRUCTURAL — an err-triggered
  conditional has nothing to trigger on, and a structure-triggered one would
  fire the hop INTO the weakness (P3 below).
- P2 PASS (never fires, 3/3). P3 PASS (3/3): the ENTRY hop alone sets the
  fast-window structure cost — fast-seg duty identical .22/.8/.213 without
  it (nohop = exit-hop = cond) vs .133/.627/.0 with it (entry = both).
- Exploratory factorial surprise: single hops RAISE the pooled MEAN
  (entry .535, exit .530 vs none .496; both-hops worst .484) — but each
  single-hop cell still drops exactly one seed below .5, and the missed
  seed MIGRATES (nohop/cond miss s22 .464; entry/exit miss s33 .369/.462;
  both-hops misses s11+s33). Mechanism: any hop is a downstream attractor
  RE-ROLL (L45b gas) — the entry volley at k=2000 re-rolls seg2 twenty
  seconds later (seg2 .507/.147/.66 -> .873/.827/.44).
- Closing read: hop scheduling cannot make the pooled gate seed-robust;
  the residual is the attractor lottery, not a control error. Min-risk
  controller spec stays "drop the hops" (worst seed .464 vs .369); the
  window-scoped reporting of L51 remains the honest spec. A graded
  structure-repair trigger is NOT proposed (L47/L48: release is a lottery;
  L55: the volley is too).

Anchors: C0a hynohop vs l51 raw = 0.0 bit-identical; C0b hybrid vs l51 =
0.0; first_div vs nohop exactly 2000/4000/2000 (3/3 each); cond full-trace
bit-identity when never-fired (strongest C0c form); C1 af + volley maxes
(entry 1.01/.97/1.01, exit .46, cond exactly 0.0 = clean never-fired
record). Drive-on 48.0 s every arm (hops ride on-windows, l39-l51
convention).

Artifacts: l55/ (PREREG.md, l55_hop.py, raw_l55.npz checkpointed before
analysis, results_l55.json, traces_l55.npz, run.out, hop.png vision-PASS
pass 2 + footnote claim re-derived programmatically after pass-2 caught a
wrong "every policy drops one" label — hybrid drops two). Fig:
publish/peabrain-figs/l55-hop.png. No live changes.

## L56 — seg2 re-roll law: distribution volley-invariant, S-state flip needs a drive edge (tick 76, 2026-11-13)

- Question (L55's surprise): is "any hop re-rolls the downstream lottery" a
  LAW (any volley, any time = pure re-draw, mean-neutral) or are TRANSITIONS
  special? Design: l55 hybrid schedule verbatim, volley placement sweep —
  nohop / k=4000 (seg1→2 transition; chain anchors vs l55) / k=4300 (mid,
  drive-ON window) / k=4600 (mid, drive-OFF) / k=4900 (chopped re-on edge);
  DNge046_L .5 × 40 steps; seeds 11/22/33; shared per-step noise.
- C0 PERFECT, 13th consecutive chain anchor: nohop AND hop4k bit-identical
  to l55 raw on mm AND all four antagonist traces (0.0), first_div
  4000/4300/4600/4900 exact; l55's P4 seg2 numbers reproduce exactly.
- Layered verdict (registered MIXED, decomposed post-hoc):
  1. DUTY-level: the LAW holds. Any volley at any time re-draws the seg2
     duty level (per-seed deltas both signs, e.g. v43 s33 .66→.36, v46 s11
     .507→.56), and the distribution is mean-neutral — grand volley mean
     .421 vs nohop .438 (P3 PASS); P1c sign counts 11/12 L+, 12/12 R+ vs
     ref 5/6, 6/6, chi2 L .6 / R .0 (n=12/6, descriptive).
  2. STATE-level: TRANSITIONS (and drive re-on edges) are special. S-sign
     LABEL flips occur only at edge-coincident volleys: hop4k|22 (0+→++,
     the s22 rescue), v49|11 (0+→++, SL .15→.38 BUILD), v49|22 (++→0+,
     SL .21→.04 DESTROY) — 3/6 edge cells flip, 0/6 mid-window
     (v43/v46 absorbed: label held in 6/6 while duty moved ±.3; Fisher
     one-sided p=.091, n small, disclosed). The edge volley builds OR
     destroys — it re-rolls S_L, it is not a rescue primitive.
  3. P1a FAIL (.203 mean diff v46 vs hop4k) is carried entirely by s22:
     the transition volley rescues its seg2 (.147→.627); a mid-seg2 volley
     never does (.187/.113/.147).
- Queue question ANSWERED: the s22 seg2 miss state is slow|0+ — SL-marginal
  (.095–.175, straddling the .15 sign threshold) with SR healthy
  (.37–.60). ALL 4 misses are seed-22 SL-marginal cells; never SL+|SR-,
  never bilateral-negative. The seg2 lottery is S_L-owned = L49's marginal
  side under continuous drive, now at volley resolution.
- Controller line: a volley can re-roll S_L only when delivered at a drive
  edge (segment transition or chopped re-on); mid-window it perturbs the
  within-state level only. Edges re-roll BOTH ways — scheduling a hop at an
  edge is a coin-flip on S_L, not a repair (consistent with L41/L47/L48).
- Verified: l56_reroll.py exit 0 (CPU 78 s, 5 arms × 3 seeds, PREREG first,
  raw npz checkpoint); fig l56/reroll.png analytic-QA PASS 0 OOB / 0
  collisions / 8 numeric claim re-derivations (vision endpoint down 000,
  disclosed); artifacts l56/. No live changes.

## L57 — endgame cord controller spec: the substrate contract (tick 77, 2026-11-13)

- Synthesis card, NO new runs: L34-L56 assembled into the one-table
  substrate contract the CX-gait endgame card (kanban peabrain t_7fa32128
  "Learned locomotion: CX-driven gait") drives against. Every row: lane
  IDs + the number that matters + M (measured on stored artifacts) /
  X (extrapolated). This tick re-verified the four most load-bearing
  rows from RAW artifacts (l44 _add protection curve, l48 18/18 table,
  l49 gap table, l51 triple), not from summary sentences.

| # | Contract row (what a controller may/must do) | Lane | The number that matters | M/X |
|---|---|---|---|---|
| A1 | Substrate = frozen intrinsic cord (21,516 nodes / 2.98M edges, g .01, beta-2 GABA, DT 10 ms). Rhythm is CORD-INTRINSIC — zero drive; L32's "sustained DNg100 drive" was inert | L32/L35/L45b | free attractors 0.7-1.6 Hz, fluid gas: 6 states/16 seeds, 11/16 migrate spontaneously per 60 s (the noise floor for every transition claim) | M |
| A2 | CPG substrate: Pugliese core E1/E2/I1/I2/E3 joins annotations (6 cells/leg); rhythm existence is sheet-distributed; E1(IN17A001)<->X464(INXXX464) are mutual STRUCTURE counterweights; per-leg T1 clamps collapse S | t61/L45a | pruning screen NO KILL at any dose (coreAll sharpens 3-8x); E1 clamp inverts S 2/3 at 10.3x the random-type bar | M |
| A3 | Readout ports: brain-origin events at the DN PORT, never motor; command corollary is DN-borne and motor-independent; body feedback must be bridge-level, not wiring | L11/L21/L26 | DN port self-cos .86-.97, clamp-kill .018-.025; X[motor]=0 clamp leaves corollary cos +1.000; distinguish pool-mean SNR from vector reproducibility | M |
| B1 | NO tonic dial: tonic DC bias never parametrically steers, even when the drive lands; entering tonic drives HOP among attractor freqs | L33/L37/L38 | max |dTurn| .016 vs .15 gate at dm ~1.01; df seed-inconsistent, non-monotone in amp | M |
| B2 | ENTRAIN = sinusoidal vnc_sensory drive 0.5-3 Hz; Arnold tongue widens with amp; amp is the structure knob, cost non-monotone | L34/L29 | phase R .71-.99 vs sham <=.23; A .01 never locks (S intact); locking onset collapses S; A .3 re-hosts S; 3 Hz needs A>=.3 (interior low-pass ~5 Hz) | M |
| B3 | HOP = single viable-channel volley; duty level re-draws at ANY volley time (mean-neutral law), S-sign flips ONLY at drive edges; hops are S_L coin-flips, never repairs | L38/L39/L55/L56 | 3/6 edge vs 0/6 mid-window S-flips (Fisher p=.091, small n); seg2 duty mean .421 vs .438; mid-seg2 never rescues a miss (3/3) | M |
| B4 | STOP = DNg88 negative release: structure-suppressor + frequency-blank, NEVER an off-switch on a moving cord; entrainment history (basin entry ~20 s) is the protection | L40/L42/L43/L44 | no parking dose (30 s @ -12: ratio 87-171 vs ent 763-1913); protection fraction 0/3 -> 2/3 -> 1/3 -> 3/3 -> 3/3 across h0/5/10/20/40 | M |
| B5 | Channel vocabulary: per-SIDE two-sided census; pinned types are NEGATIVE-only, buried need amp; check edge SIGN before volleying a class | L36/L37/L38/L24 | 18 flex / 14 jump / 2 ext viable-modulating types; DNg88/MDN pinned (X=1.0000); DNg105 all-243-edges inhibitory | M |
| B6 | TURN = mirror L/R homologues (ipsi DNg95, crossed DNg105); unilateral volley = strictly ipsilateral flexor burst; superposes with bilateral routes | L24 | sign-flip 3/3, SNR 84-121x, composition cos +.999, turn retained 1.00 (transient regime) | M |
| C1 | Scheduling slack: drive-off gaps <= 5 s; beyond that structure collapses at ~5.5 s regardless of gap length; rhythm survives gaps, structure does not; resume re-forms | L49 | gap5 HELD 3/3; >= 10 s collapse 15/15 at 5.49-5.69 s; f_resume 0.700 locked 15/15 | M |
| C2 | DRIVE-STAYS-ON law: bilateral structure is drive-held; release re-runs the lottery at the amp->0 CROSSING (envelope shape + dwell irrelevant); NO repair primitive exists; post-stop SL+|SR- holds >= 120-220 s | L46/L47/L48 | duty(both>=.25) post-release < .5 in 18/18 treatment cells (max .443); S_R persists through 60-s fades, dies AT crossing | M |
| C3 | Fast-window contract: continuous fast drive locks frequency perfectly but is structure-TOXIC at every amp (dwell-deepening collapse); entry-state-conditional — from chopped entry the fast lock is FREE | L50/L51/L52 | 1.4 Hz err .000 with duty {.24/.16/.12}->{0/.1/0}, slope neg 3/3; amp .2 = shift lottery 1/3; free lock err <= .0027 | M |
| C4 | HYBRID schedule = the spec: continuous drive in tracking-critical fast windows, chopped at 0.7 Hz where structure matters | L50/L51/L58/L59 | seg1 err .0037/.0007/.001 (gate .01) AND 0.7-window duty .600; pooled .484 misses .5 by .016 (s33 .382), carried by the fast-window seed lottery. L58 AMENDMENT: denser chop 500-on/200-off lifts duty07 .600 -> .732 (min .56) at 54 s with a BETTER lock (err .000 3/3) — the 5/4 numbers were a point on the Pareto edge, not the ceiling. L59 AMENDMENT (census n=16, tick 82): the pooled gate is a FAIR COIN — P(duty_all >= .5) = 8/16 BOTH arms, Wilson 95% CI [.28,.72], means .489/.513; tracking FREE 16/16 both arms; pooled-min-seed and pooled-mean gates RETIRED (L58's .473 min was itself a lottery draw; census min .28/.33); structure gates go DISTRIBUTIONAL/window-scoped — P(window duty >= .5) with CI, duty07 >= .7 mean, drive on the Pareto edge (spec handed to kanban t_7fa32128, L61) | M |
| C5 | Min-risk policy: NO HOPS, no structure-triggered conditionals (they fire into weakness) | L55/L56 | nohop worst seed .464 vs .369; each single-hop policy drops exactly one seed and the miss migrates; pooled gate owned by the attractor gas | M |
| C6 | Score tracking err + per-window structure duty + drive-on seconds SEPARATELY; never sum into one scalar; report windows, never pools alone | L50/L51 | duty58 doubles duty at 62% drive (.576 vs .285) but loses the fast lock (err .92 vs .001) | M |
| C7 | Repair budget: stop->re-entrain restart is the most reliable structure-repair event measured; entrain amp is the repair knob | L42/L43 | inversion clears exactly at restart; repair-from-inversion 9-279 steps after drive resumes; amp .03 never recovers | M |
| D1 | Model-class limits: no WHEN-claims beyond route timing; transit delay is path-integral (~9 stages), attenuation is a separate ~3-stage low-pass moment | L15/L16/L21/L29 | TTMn smear 344-466 ms invariant under per-class taus; half-depth cutoff 5 Hz; never predict one from the other | M |
| D2 | The action set is DISCRETE: attractor selection + entrainment + per-side two-sided channels; a learned policy picks primitives, never dials | L38 | DNg88 -8 kills S .49->.06-.12 instead of slowing; no df<0 slowing anywhere; the cord is a throttle | M |
| D3 | CX half: CX->DN goes through LAL (85.7% at 2 hops); CX owns steering/posture/neck, never the power stroke; executable enumeration = l31 x l38 join | L31/L38 | 481 primitive families, 107 split across sides; escape routes CX-independent (direct mass ~.0000-.0003) | M |
| D4 | EXTRAPOLATION BOUNDARY (untested): closed-loop learned composition of these primitives; pooled-gate distribution at n>3 seeds/cell; edge-volley PLACEMENT policy shifting the gas (L56 gives mechanism, n=6/6) | — | every schedule cell above is n=3 seeds; treat single-seed outcomes as lottery draws | X |
| D5 | Body-echo closed loop is a MEASURED OPTION, never a default: naive echo (gain .5, +, 100 ms) is structure-toxic (L63); the census-confirmed content cell is gain .1, NEGATIVE, delay 50 ms — a POINT, not a basin | L63/L64/L66 | off-duty lift +.186 mean, P(lift>0) 14/16 Wilson [.64,.965], donor sham -.001 (content TRUE), lock pristine (.0005 vs open .0006); only 2/8 neighbors carry (both gain .05); benefit LEFT-loaded: mean S_L .326->.561 (all 16 seeds >= .409), S_R .153->.186 unmoved, both census misses SR-marginal | M |

- Closing read: the cord is a THROTTLE with a discrete vocabulary
  {entrain, hop, stop} whose structure axis is drive-held and whose pooled
  outcomes ride an attractor gas. A CX-side learned controller composes
  these primitives under window-scoped gates; it never modulates
  continuously, never expects offline repair, and never sums objectives.
- Handoff: kanban peabrain t_7fa32128 annotated with this section as its
  substrate contract. Gate-setting follow-ups seeded as L58/L59 (ideas 28)
  per the L6d-0 lesson: pre-measure reachable mass BEFORE training.
- Verified: all rows cite shipped lane artifacts; this tick re-derived
  l44 protection {0,2,1,3,3}, l48 18/18 (max .443 ramp30/s33), l49
  gap5-held + 5.49-5.69 s collapse + f_resume .700 15/15, l51 triple
  (.0037/.0007/.001; .600; .484 s33 .382) from the stored results jsons.
  No new runs; no live changes.

## L58 — gait reachable-mass: the SCHEDULE owns it; pooled gate un-ownable (tick 78, 2026-11-13)

Pre-training headroom measurement on the L51 task (L6d-0 form), PREREG
first (l58/PREREG.md). 19 family cells: 9 new arms run this tick
(l58_headroom.py, CPU 135 s, 3 seeds) + 10 anchor cells re-derived from
STORED raw npz (l51 allw/duty58/hybrid, l55 hop2k/hop4k/cond, l56
v43/v46/v49); l50's free cell UNAVAILABLE (its traces lack the antagonist
pools — disclosed, P6 skipped). Fork oracle = stored branch arms sharing
the noise stream, prefix bit-identity 0.0 asserted at every fork.

- C0 PERFECT, 14th consecutive chain anchor: in-run nohop bit-identical to
  l55 hynohop on mm AND all four antagonist traces, full window, max|d| 0.0;
  fd_expected exact {off200 700, off300 800, off500 900, off700 900,
  min5seg 900, fast2 2000, seg2off 4000, seg2a2 4000}. Write-time AMPA
  asserts caught two of my own table bugs BEFORE any rollout (seg2off fast
  seg unset; off300 boundary clip = 5200 not 5400 steps).
- HEADROOM TABLE (the gate a learned endgame policy must clear):
  - TRACKING is FREE: 13/19 cells lock <= .01 on 3/3 seeds; cheapest
    lock-holder 44 s (off700, err .000/.000/.007). Failures: duty58 never
    locks (.90-.93, L50 exact), min5seg no re-lock (s11 .335), off500 one
    miss (.012).
  - STRUCTURE (0.7-window duty): best = off200 (500-on/200-off) .732
    mean / .56 min at 54 s — a DENSER CHOP beats the L51 spec schedule
    (nohop .539/.297) by +.19 mean. Structure IS gap-limited in the
    improving direction (P1b FAIL = the finding: +.193 at 200-step gaps).
  - POOLED: NO cell reaches min-seed >= .5 (best .473 off200; best mean
    .623 off200) across all 19 cells → GATE-IS-THE-BUG, formally: the
    pooled gate is un-ownable by any FIXED policy at n=3; endgame gates
    must be window-scoped or distributional (L59's 16-seed ensemble).
  - DRIVE FLOOR: 44 s (off700: lock + duty07 .500 — a Pareto corner, not
    a spec: its fast-window duty .033, pooled .344). Pareto edge runs
    34 s (min5seg, structure .236) → 44 s (lock, .50) → 48 s (nohop,
    .539) → 54 s (off200, .732) → 64 s (allw, .416 toxic).
- SLACK LAW CORRECTION (P1 FAIL, the honest one): L49's 5-s gap tolerance
  is PROTOCOL-BOUND. Inside a chopped schedule, 500/500 and 500/700 chops
  (5-7 s gaps) still hold duty07 (.558/.500 mean); only the single-prime
  min5seg collapses (.236). The 5-s number measured gaps WITHIN deep
  continuous entrainment; a chop schedule never enters that basin, so its
  gaps are tolerated. Never port a tolerance number across drive protocols.
- AMP ROWS: fast seg at .2 locks 3/3 (.006/.003/.004) with fast-window
  duty still lottery (min .062) — L52's shift point does NOT rescue the
  fast window from chopped entry (P3 PASS). Seg2 at amp .2 COSTS window
  structure (.417 vs .539, delta -.122; P4 half-fail): the 0.7-window
  structure knob wants FULL amp — amp is not a drive-substitute.
- FORK ORACLE (state-conditioned, 1-segment greedy):
  - Fork A @2000: entry hop hurts 3/3 (.22/.8/.213 -> .133/.627/.0);
    oracle picks nohop — zero closed-loop gain at the fast entry.
  - Fork B @4000: exit hop re-rolls seg2 (nohop .507/.147/.66 vs hop
    .487/.627/.507); closed-loop per-seed max = .598 vs best-fixed .540
    = +.058 — the ONLY closed-loop mass found, and it is NOT realizable:
    fork-time S_L {.357/.278/-.100} does not separate benefit
    {-.02/+.48/-.153} (rank corr +.5, P5 FAIL; the seed with the
    sign-inverted side at fork time is hurt WORST, not rescued). No
    S_L-threshold policy captures the +.06 in this sample.
  - Fork C mid-seg2 (v43/v46/v49): seg2 .4-.65, never rescues the s22
    miss (.187/.113/.147) — l56 confirmed at fork-grade anchoring.
- VERDICT for the endgame: the reachable mass is owned by the SCHEDULE
  (off200 dominates the L51 hybrid on structure at both 0.7 windows AND
  matches its lock); the learned policy's measured residual over the best
  fixed family is <= +.06 on one window, unrealizable by the measured
  fork-state readout at n=3. Gate the learned controller on: tracking
  <= .01 (free), duty07 >= .7 mean / .55 min (off200 constructs the
  ceiling), drive budget stated on the Pareto edge — and DROP pooled as a
  fixed-policy gate. L57 C4 amended below.

Artifacts: l58/{PREREG.md, l58_headroom.py, run.out, raw_l58.npz,
results_l58.json} (raw checkpointed before analysis; per-seed seg tables
in json). No live changes; duck untouched.

## L59 — spec-seed-ensemble: the pooled gate is a fair coin at census n; S_L owns the miss; hops decorrelate entry from outcome (tick 79, 2026-11-13)

Question: every schedule number in the L57 contract is n=3 (its D4
extrapolation flag). Run the l51 hybrid + l55 hynohop schedules verbatim on
the l45b 16-seed census grid and turn the single-seed lottery reads into
distributional claims. Machinery l55 verbatim (ARMS trimmed, seeds swapped);
PREREG l59/PREREG.md first; C0 = 15th consecutive chain anchor.

ANCHORS (C0 PERFECT after ADDENDUM 1 gate-logic fix): seeds 11/22/33 both
arms bit-identical 0.0 to l55/raw_l55.npz on mm + all four antagonist
traces; hop wiring fd=2000 on 16/16 seeds, volley vmax .479; af in range
everywhere. Run-1's C0_pass computed False from a gate bug (the all-zero
float sweep caught the DIAGNOSTIC vmax .4788) — fixed in-script, re-derived
from the stored json; rollouts untouched.

DISTRIBUTIONS (the contract's new rows):
- POOLED GATE = FAIR COIN: P(duty_all >= .5) = 8/16 BOTH arms, Wilson 95%
  CI [.28,.72]; means .489/.513, medians .495/.499, min .276 (s103)/.329
  (s112). P1 registered point<.5 FAILS at exactly .5 — the honest read is
  INCONCLUSIVE-AT-16: no schedule owns the pooled gate; it is seed-lottery
  (L45b gas). L58's "best min-seed .473" was itself a lottery draw — at
  census n the min-seed framing dissolves (min .28/.33).
- MISS MIGRATES (L55 re-roll law, census-n): miss sets {22,101,103,104,107,
  109,111,112} vs {11,33,101,105,106,107,109,112} — only 4/8 shared; s11
  and s33 PASS under hynohop and MISS under hybrid (its entry/exit hops
  re-rolled them out).
- FAST WINDOW: duty wide (0-.89), dead tail <.1 in 4/16 both arms (P2 FAIL,
  marginal: registered >=5), <.25 in 7/16, >=.5 in 6-7/16; means .375/.402.
  TRACKING FREE UNIVERSALLY: seg1 err <= .01 on 16/16 BOTH arms (P4 PASS
  at the ceiling, registered >=12/16 — the chopped-entry free lock is not
  a lottery).
- MISS ANATOMY (P3 PASS both arms): failing segments are S_L-owned —
  hynohop 9 SL / 1 SR / 3 both (.692 share), hybrid 6/2/3 (.545); L56's
  n=3 S_L-marginal finding generalizes. Failing segments sit in seg0+seg1
  (14-15 of them); seg2 is the healthiest window.
- ENTRY JOIN (P5, exploratory): seg0 S_L health predicts pooled outcome at
  rank +.612 under hynohop — but only +.174 under hybrid: the hops
  DECORRELATE entry state from outcome, a census-n confirmation of the
  re-roll law from the correlation side.

CONSEQUENCES for the L57 contract: (1) pooled-min-seed rows dissolve —
any learned-policy gate must be DISTRIBUTIONAL (P(clear) with CI at census
n, or window-scoped); (2) tracking is free at census n (16/16), so the
learned controller's whole contestable mass is structure; (3) if a policy
wants entry-state predictability it should AVOID hops (hynohop preserves
the +.6 entry-outcome correlation) — but that buys prediction, not
performance (means .489 vs .513).

Artifacts: l59/{PREREG.md + ADDENDUM 1, l59_ensemble.py, l59_fig.py,
l59_qa.py, run.out, raw_l59.npz, traces_l59.npz, results_l59.json,
ensemble.png/svg}. CPU-only 190 s. Fig vision-PASS pass 2 + analytic QA
12/12 claims re-derived. No live changes.

## L60 — side-asymmetric-entrain (tick 81, 2026-11-13): NEGATIVE as a
## targeted repair lever; the anatomy is ipsi but the structure effect is
## CROSSED. Static pre-checks + 4-arm x 8-miss-seed dose (l59 machinery
## verbatim, hynohop schedule).

QUESTION: the pooled-gate misses are S_L-owned (L59 P3). Is a modest
rootSide-L amp bump on the mech entrain drive (1.25x/1.5x, direction
control 0.8x) a targeted repair lever — marginal side's duty rises without
losing the lock or crashing SR?

STATIC (l60/l60_static.py -> l60_static.json):
- somaSide is DEAD for vnc_sensory (3586/3588 NaN — peripheral somata);
  rootSide joins 0.9997 (1789 L / 1798 R / 1 unknown). The card's
  "not side-joinable" branch fires on somaSide but rootSide carries it.
- Minnick 2% input-share floor (t80 amendment): DIRECT 1-hop mech->pool
  ipsi share .0066-.0216 (mean .0141) — below the floor on 6/8 pools and
  EXCLUSIVELY ipsilateral (contra ~0 everywhere). The 2-hop via-intrinsic
  pathway is ipsi-dominant 10.2x-32.8x on EVERY pool (mean mass 114.8 vs
  6.5): the conduction channel the entrain drive actually rides (L21/L34)
  is strongly side-resolved. Static GO.

DYNAMIC (l60/l60_asym.py, CPU 152 s, raw npz checkpoint pre-analysis):
C0 PERFECT — 16th consecutive chain anchor: a100 vs l59 raw hynohop
BIT-IDENTICAL 0.0 on mm + all four antagonist traces, all 8 miss seeds
(ratio 1.0 arm keeps l59's exact single-index-add form). dm gate FAILED on
an off-by-one in MY gate logic (demanded first_div==0; the dm loop starts
i=1) — re-derived from raw traces: every asym arm diverges at t<=2 steps,
|d_mm| 6.5-7.9e-2 — the split drive entered differentially everywhere.
Registered P3 err_all form was WRONG (it averages the chop-off windows,
.14-.20 in a100 too); re-derived seg1-only from stored cells.

PREDICTIONS (all registered pre-rollout, l60/PREREG.md + ADDENDUM 1):
- P1 DOSE FAIL: dSL means a100 .509 | a125 .489 | r080 .567 | a150 .605 —
  NOT monotone (the modest boost DIPS below baseline; the DIRECTION CONTROL
  beats it) and a150-a100 = +.096 < the +.10 gate. Per-seed deltas swing
  both signs in every arm = re-roll lottery (L55/L56), not dose-response.
- P2 GATE FAIL: pooled-duty conversion a100 0/8 (by construction, miss set)
  -> a125 1/8, a150 3/8, r080 0/8 vs the registered >=6/8. The gate stays
  a fair coin under the lever.
- P3 LOCK FAIL: seg1 err <= .01 — a100 8/8 (l59 tracking-free replicated),
  a125 5/8, a150 5/8, r080 7/8: ANY drive perturbation costs the lock on
  ~3/8 seeds (one .33-block per failure, the l55 off-block class).
- P4 NO-CRASH FAIL on r080: dSR .765 -> .543 (-.222) — and the per-seed
  deltas are DOWN 6/8 (mean -.23).
- P5 DIRECTION FAIL: r080 dSL .567 > a100 .509; a125 > r080 on only 3/8.

TWO REAL STRUCTURE FINDINGS (small-n, 6/8 each, labeled):
1. GLOBAL LIFT, NOT SIDE-TARGETED: a150 (+50% L-mech) raises BOTH sides'
   structure duty (dSL +.096 6/8, dSR +.060 6/8) = an amp-flavored global
   re-hosting (L34's A-cost curve), not ipsi repair.
2. CROSSED STRUCTURE COUPLING, opposite the static anatomy: R-side structure
   tracks L-mech drive mass in BOTH arms (a150: dSR up 6/8; r080: dSR down
   6/8, ipsi L spared/up 6/8 in both) — while the static pathway mass is
   ipsi 10-33x. The ipsi side re-rolls; the contra side is systematically
   coupled. A static ipsi-dominant pathway does NOT imply an ipsi-dominant
   effect — measure the effect, never read it off the anatomy.

VERDICT: side-asymmetric mechano entrain is NOT a targeted S_L repair
lever — the L45b gas owns the outcome (no dose, no direction, lock cost,
gate conversion 3/8 max). Endgame spec unchanged: symmetric entrain,
no hops, distributional/window-scoped gates; the side-resolved input
vocabulary remains DN volleys (L24/L37). The crossed-coupling observation
is a note for any future body-level feedback design (L63), not a lever.

Artifacts: l60/{PREREG.md + ADDENDUM 1, l60_static.py, l60_static.json,
l60_asym.py, raw_l60.npz, traces_l60.npz, results_l60.json}. CPU-only
152 s. No live changes.

## L61 — endgame-gate-handoff: the distributional gate spec (tick 82, 2026-11-13)

- Synthesis card, NO new runs: folds L58 (reachable mass) + L59 (16-seed
  census) into the CX-gait endgame card as the DISTRIBUTIONAL gate spec,
  retiring every pooled fixed-policy gate. Numbers cited from the stored
  results jsons (malecns/l58/results_l58.json, malecns/l59/results_l59.json)
  and the L58/L59 sections above — re-read this tick, not re-derived from
  rollouts (no runs by design).

THE SPEC (posted verbatim as a kanban comment on peabrain t_7fa32128,
2026-11-13 ~23:5x):
1. TRACKING err <= .01: FREE at census n=16 (16/16 seeds both schedules)
   — not contestable; all contestable mass is STRUCTURE.
2. STRUCTURE gates: window-scoped P(window duty >= .5) with Wilson 95% CI
   at census n. POOLED gates RETIRED — the pooled gate is a FAIR COIN
   (P=8/16 both arms, CI [.28,.72], means .489/.513; L58's .473 min-seed
   was a lottery draw, census min .28/.33).
3. duty07 >= .7 MEAN = the constructible ceiling (off200: .732/.56 at 54 s,
   err .000); drive budget stated on the Pareto edge
   (44 s lock / 48 s nohop .539 / 54 s off200 .732 / 64 s toxic).
4. HOP POLICY: hops re-roll and DECORRELATE entry from outcome
   (+.612 nohop vs +.174 hybrid) — entry-conditioned controllers stay
   NO-HOP (prediction, not performance: .489 vs .513); misses S_L-owned
   (.692/.545).

FIELD FORM (t80 fold, cited in the comment): Mahdavi 2611.06929 publishes
this gate shape as a certified family — one-sided bounds over held-out
draws at tolerance (eps, rho); their interface-only-baseline rule = our
no-drive/free arm (L35's D=0 lesson, now field-named). Minnick 2610.33881:
own-motor-command replay senses-off 2.0% vs 94.0% closed-loop — the
field's citation for bridge-level feedback (L12/L26) in the endgame loop.
Necessity claims stay fidelity-bound: their 3-IN necessity on Pugliese vs
our L45a sheet-distributed no-kill — same object, different model class.

- L57 row C4 amended with the L59 census numbers (this tick, diff above).
- Verified: kanban comment posted (CLI receipt "Comment added to
  t_7fa32128"; task show lists it, len ~1.9k); C4 row patched; digest
  updated + pushed. No live changes; duck untouched.

## L63 — closed-loop-cord, slice A: the naive delayed echo HURTS (2026-11-14, tick 84)

Question (LANE.md ideas-30): Minnick's 2.0% senses-off vs 94.0% closed-loop —
does closing OUR loop (delayed, attenuated antagonist-motor-mass echo onto
vnc_sensory mechano; body-level, L12 form; GFB .5, DELAY 100 ms) widen slack,
soften fast-window toxicity, or break tracking? PREREG l63/PREREG.md; arms
hynohop/fbh/sham (donor-paired open trace, same GFB) + openL/fbL (500/700 chop
= 7 s gaps); n=8 census seeds, machinery l59 verbatim, CPU 158 s.

ANCHORS: C0 17th consecutive chain anchor — hynohop BIT-IDENTICAL to
l55/raw_l55.npz (mm + 4 traces, seeds 11/22/33, 0.0); openL identical <900
(schedule-share prefix, 0.0); fbh/sham identical <DELAY (0.0); C2 feedback
LANDS (max d mm .1445); C1 af in range 40/40.

VERDICT — ALL THREE registered outcomes FAIL, and the harm is
LOOP-CONTENT-SPECIFIC (fb worse than mass-matched sham on every read):
- P1 off-window structure (base chop): duty lift -.151 (sham -.088);
  open mean .216 -> fb .064; P(>=.5) 0/8 both.
- P1L 7 s gaps: lift -.162 (openL .198 -> fbL .037). Slack does NOT extend.
- P3 fast-window toxicity: seg2 duty lift -.257 (sham -.077) — the echo
  DEEPENS L52 toxicity instead of softening it.
- P2 registered form (all-seg mean err) PASSED DEGENERATELY — it was carried
  by the chopped segs' free-run errors (.21 open baseline both arms).
  Discriminating read (PREREG ADDENDUM 1, L55 class, 2nd instance): seg2-only
  lock err — open 8/8 <=.01 (L59 tracking-free replicated), fb 6/8 with two
  catastrophic losses (.6165, 1.000 on seeds 109/111), sham 8/8. The true
  loop makes the fast-seg lock FRAGILE; uncorrelated mass does not.

MECHANISM (secondary reads): the echo keeps the pools MOVING — off-window
antagonist amplitude +59% (.0255 -> .0405) — while DESTROYING the antagonist
relation on one side: off S_L +.283 -> -.230 (sign flip), S_R +.126 -> +.613;
the SL-|SR+ selected-attractor pattern (L46 form). A delayed POSITIVE echo at
100 ms is ~1/4 cycle at 0.7 Hz — energy injected at destabilizing phase
pumps co-activation/inversion, not antiphase.

CONSEQUENCE FOR THE L57 SPEC: the open-loop assumption of the cord controller
spec is SAFE at these parameters, cited — Minnick's whole-body 2%/94% gap
does NOT transfer to a naive delayed echo at rate fidelity; a properly tuned
body model (gain, delay, sign, pathway) is a PREREQUISITE for closed-loop
benefit, not a free win. Dose/delay/sign sensitivity unregistered (single
.5/100 ms point) — the honest boundary of this negative.
Artifacts: l63/{PREREG.md, results.json, raw_l63.npz, run.out},
l63_closed.py. No live changes.

## L64 — echo dose–phase map: the loop is NOT closed; low-gain negative
echo carries content (tick 85, 2026-11-14)

QUESTION: L63 closed ONE point (gain .5, 100 ms, positive) as harmful — is
ANY (gain, delay, sign) region of body echo helpful before the endgame loop
borrows or finally rejects the idea? Registered closure rule: no cell clears
off-duty lift >= +.10 with lock kept => body-echo CLOSED at rate fidelity.

METHOD: 24-cell grid gain {.1,.25,.5} x delay {2,5,10,20} steps (20-200 ms)
x sign {+,-}, l63 machinery verbatim (chop schedule, own-antagonist-mass
echo onto mechano, shared-noise paired arms, seeds 11/22/33), PREREG
l64/PREREG.md first; donor sham run for the two candidate winners (max-mean
g01_d20_p, max-consistency g01_d05_m — extension to 2 cells disclosed).

VERDICT: P2 CLOSED REJECTED — a low-gain NEGATIVE window carries loop-CONTENT
structure benefit:
- g01_d05_m (gain .1, -, 50 ms): off-window duty lift +.190, EVERY seed up
  (.432/.477/.523 vs open .227/.250/.386), S_L .534 / S_R .313 both healthy,
  seg2 lock pristine (.0003-.0011); donor sham lift -.068 => content=TRUE
  (sham < 0.5x fb, PREREG P1 rule). The FIRST measured closed-loop benefit
  in this lane; L63's tuned-body-model prerequisite is satisfied by DOSE and
  SIGN, not by a phase model.
- g01_d20_p (gain .1, +, 200 ms): fb +.205 vs sham +.160 => content=FALSE —
  perturbation/mass-carried (donor mass does ~all of it, and the sham itself
  crashes one seed's lock .334: donor mass at this dose is not free either).
- DOSE DOMINATES PHASE: gain .1 mean lift +.120 (min .000, never hurts any
  cell), gain .25 -.019, gain .5 -.197 (always hurts, -.038..-.280); L63's
  point reproduced inside the grid (g05_d10_p -.250, cell bit-identical to
  l63 fbh, C0x). P3 as registered FAILS: positive harm does NOT deepen
  toward quarter-cycle delay (flat-to-easing); the classical 20-ms negative
  cell is NOT the best negative cell (50 ms is); zero floor-buried cells
  (all 24 dm >= .059 — every echo entered the dynamics).

CAVEATS: n=3 anchor seeds — lottery texture visible elsewhere (g025_d02_m
.0/.409/.841); the content claim needs census-n replication before it
enters L57 (ideas 32 -> L66). l63's catastrophic lock seeds (109/111) are
not in this subset: the lock-fragility dimension is under-sampled here,
disclosed. Mechanism not claimed beyond the sham separation.

ANCHORS: C0 18th consecutive chain (grid open bit-identical l55 raw, mm+4
traces x 3 seeds, 0.0); C0x g05_d10_p bit-identical to l63 fbh (cross-run
wiring replication, 0.0); C0P all 24 cells prefix-exact, first_div == delay
(d2->3, d5->6 sample); C1 af in range; the sham run replicated the grid on
45 enumerated keys (0.0) — stream replication proven before reading sham.

L57 CONSEQUENCE: the open-loop spec stays DEFAULT (content cell = n=3, one
schedule, one substrate). Row D amendment recorded: "low-gain negative echo
(g .1, -, ~50 ms) = the one measured content-carrying window — census
replication pending (L66)".

Artifacts: l64/{PREREG.md, results.json, results_sham.json, raw_l64.npz,
raw_l64_sham.npz, grid.png, run.out, run_sham.out}, l64_grid.py,
l64_sham.py, l64_fig.py. Fig vision-QA'd 2 passes; pass 1 caught my own
sign-encoding defect (abs-lift labeled with the ECHO sign — vision read
+.190 as -.190); fixed to true signed lift + separate 'echo +/-' tag,
re-verified programmatically (24/24 signed tokens) AND on pixels. No live
changes.

## L65 — BANC female op-point + L32 antiphase replication: WIRING REPLICATES

Question (LANE ideas-31): does real FEMALE cord wiring self-order antagonist
antiphase the way male does (L32 S(Tr) +.49)? First dynamics on the same-sex
substrate (v626; live brain stays female v783). PREREG l65/PREREG.md first;
verdicts re-derived by l65_verdict.py from results_l65.json.

- P1 PASS: full-graph (80,635) gain bisect g* 0.8058 -> af 16.8% active
  (band .13-.17). Male context 0.885 — close because both are in-deg
  normalized (the rho .2498 raw figure was unnormalized).
- Subnet (L32 form): cord 20,521 + DN-into-cord 728 = 21,249 nodes, 627,051
  raw edges (log1p syn, no indeg norm in-subnet, sign per source NT).
  Pools via peripheral_target_type: Ti 101/12, Tr 62/48 — female gives BOTH
  pairs (male census had Ti only via type names).
- P2 PASS arm B (flyvis glut-INH, frozen g .14/beta 2/d .2): S(Ti) .720 and
  S(Tr) .499, 3/3 seeds positive, depths .26-.29/.08, rhythm 671-1009x @
  0.77-1.15 Hz. S(Tr) lands EXACTLY on male's +.49. Arm A (glut-EXC) PARTIAL:
  .290/.265 positive everywhere but under the .30 level.
- P3 PASS wiring-specific: degree-MS draws (3, degrees asserted preserved,
  ~4.9M swaps each) max mean S(Ti) .019 vs real .720 (gap .70 >> .15
  registered); density draws dead (max .038). The antiphase is placement-
  carried on female wiring too.
- SEX/GRAPH CONTRAST (report, not gated): male L32's winning arm was glut-EXC
  ("ours"); female BANC's winner is glut-INH (flyvis). Real wiring orders
  antiphase under EITHER convention, but the strong arm flips between
  connectomes — sign conventions are graph-empirical, not universal.
- No legblock tier (D3): BANC flat table has no neuromere column.
Artifacts: banc/l65/{PREREG.md, scan_l65.json, results_l65.json, raw_l65.npz,
run.out}; scripts l65_banc_oppoint.py, l65_verdict.py, l65_probe.py. No live
changes.

## L66 — content-cell-census: the L64 echo window is REAL at census n; a POINT, not a basin; benefit LEFT-loaded (tick 87, 2026-11-14)

Question (LANE ideas-32): L64 found one loop-content window (gain .1, sign −,
delay 5 = 50 ms) at n=3 anchor seeds. Does it survive the 16-seed census with
its donor sham, and is it a point or a basin?

Design: l64 machinery verbatim; census grid [11,22,33]+101..113; arms OPEN +
fb(g .1, −, d5) + donor sham (l59 stored hynohop, cyclic next-seed pairing,
never self) + 8 negative-sign neighbors (delay {3,4,6,8} x gain {.05,.15}).
176 rollouts CPU, PREREG first, raw npz checkpointed pre-analysis.

- G1 PASS — the content cell is census-confirmed: off-duty lift mean +.186,
  P(lift>0) 14/16 (misses s110 −.25, s111 .0), Wilson 95% [.64,.965];
  donor sham lift −.001 (pos 5/16, ratio ~0 << 0.5 gate) = content TRUE;
  lock pristine (fb e2 median .0005 vs open .0006, no catastrophic seed).
  → L57 row D5 amended: closed loop is a MEASURED OPTION at exactly this
  cell, never a default.
- G2 POINT — 2/8 neighbors carry (n005_d03_m +.148 11/16, n005_d06_m +.158
  13/16; BOTH gain .05). The gain .15 column is dead (max +.116 at 10/16,
  d08 negative). Useful region: gain ≤ .1, delay 3-6 — thin in gain.
- P3 FAIL = the real finding: both census misses are SR-MARGINAL (s110
  SL .512/SR .153, s111 SL .494/SR .022) — the OPPOSITE side from the l59
  no-hop misses (S_L-owned). The bilateral negative echo rescues S_L
  (mean .326 → .561, ALL 16 seeds ≥ .409 under fb) and leaves S_R unmoved
  (.153 → .186). The echo's content benefit is LEFT-loaded in this
  parameterization; the residual weakness it does not touch is the right
  side. (Bilateral drive, asymmetric effect — the L60 lesson again:
  effect side is not readable off input anatomy.)
- Anchors: C0 PERFECT 19th consecutive chain anchor (open = l55 hynohop
  bit-identical 0.0, mm + 4 traces, seeds 11/22/33); C0x fb = l64 stored
  bit-identical 0.0; C0v value anchors exact (fb/open off-duty == l64
  stored, max diff 0.0); wired_dead 0 (no degenerate arm, L55 rule clean).
  C0P run-1 False was a GATE bug (L44 class, 2nd instance): my registered
  "first_div == delay" came from LANE-LOG's summary sentence; L64's STORED
  json carries first_div = delay+1 for every cell (echo enters mech at
  k=delay, pools see it one hop later). ADDENDUM 1 disclosed; re-derived
  from stored artifacts: 0 violations, fd matches l64, prefix [0,6) exact
  16/16. Zero reruns.

Artifacts: l66/{PREREG.md + ADDENDUM 1, l66_census.py, l66_verdict.py,
run.out, raw_l66.npz, raw_partial.npz, results_l66.json, verdict_l66.json}.
No live changes; duck untouched.

## L67 — side-split-echo (tick 88, 2026-11-14): the echo benefit lands on the
## MARGINAL side, not the wired side — S_R is routing-unrescuable

Question: L66's bilateral negative echo rescues S_L everywhere and never
touches S_R; both misses SR-marginal. Does splitting the echo per side
(own mass -> own rootSide mech; L60 join 0.9997) lift S_R, or does unilateral
echo behave like L60's asymmetric drive (re-roll lottery / crossed)?
PREREG l67/PREREG.md registered first (both branches). Machinery l66
verbatim; open reused from l66 stored raw (value-anchored); census n=16.

- VERDICT: branch B — LOTTERY-CROSSED. An R-only echo moves the LEFT side
  (+.102, 11/16) MORE than the right (−.019, 8/16 = coin flip): P1 FAIL,
  P3 crossed fires grossly. No routing rescues S_R at this operating point:
  dSR = bi +.033 / lonly +.056 / ronly −.019 / split +.008 (all ≤ .056,
  Wilson on ronly [.28,.72]). The echo's benefit lands where the GAS is
  marginal (S_L, L56/L59 anatomy) regardless of which side's loop closes.
- Ranking on dSL is monotone in L-loop mass — bi +.235 (15/16) > lonly
  +.171 (13/16) > ronly +.102 (11/16) > split's R-half nothing — an ipsi
  bonus EXISTS (P2 PASS: lonly lifts its own side first, .171 > .056) but
  the crossed component carries most of a unilateral dose.
- S_R marginality is STRUCTURAL here, not a missing-feedback problem: the
  one intervention that ever lifted BOTH sides is L60's global amp re-
  hosting (a150 +.096/+.060) — amp, not routing. Card L69.
- P4 PASS: lock pristine in every arm (e2 medians at open level, no
  catastrophic seed, cat False everywhere); P5 FAIL (split gets no R lift);
  dSR sign flips ronly-vs-split 4/16 (< 5 threshold); wired_dead 0
  (dm_min .38-.41 all arms — every echo landed; L55 vacuous-pass rule clean).
- Spec consequence (L57 row D5): the closed-loop option stays BILATERAL —
  best S_L rescue per dose (.235 vs .171/.102); a side-tuning knob does
  not exist at this cell. Per-side duty confirms (bi dutyL +.227/dutyR
  +.053; ronly dutyL +.048/dutyR +.016 — even the duty read crosses).
- Anchors: C0 PERFECT — bi BIT-IDENTICAL to l66 stored g01_d05_m on all
  16 seeds, 80 keys, 0.0 (20th consecutive chain anchor). C0O: open
  metrics recomputed from l66 traces == l66 json exactly. C0s: prefix
  [0,6) == 0 AND first_div == 6 for ALL arms/seeds incl. bi (the L66
  ADDENDUM-1 form, now measured on the bi arm too). C1 af asserted in-run.
  bi value replication: dSL/dSR/off-lift +.235/+.033/+.186 == l66 stored.
- Honest disclosure: run-1 analysis crashed post-rollout (arm_block read
  dm['bi_*'], side-arms-only dict — analysis bug, not wiring); verdict
  re-derived from the checkpointed raw_l67.npz via l67_verdict.py (l66
  precedent), zero reruns. A pre-rollout nonlocal/global syntax slip killed
  attempt 1 before any rollout (run.out line 1). Sham not rerun: content
  was established in L66; this is a mechanism card.

Artifacts: l67/{PREREG.md, l67_sidesplit.py, l67_verdict.py, run.out,
raw_l67.npz (open copies included), raw_partial.npz, results_l67.json}.
No live changes; duck untouched.

## L68 — banc-entrain-replication (slice A, tick 89, 2026-11-14)
QUESTION: does the L34–L66 entrainment contract (male-cord measured)
replicate on the FEMALE BANC cord (L65 substrate frozen: g .14 / beta 2 /
DNg100 d .2, raw log1p, glut-INH arm) under the core l55 schedule (chop
500-on/400-off 0.7 + continuous 1.4)?
VERDICT: PARTIAL REPLICATION — the drive reaches motor output but the 1:1
razor lock does not transfer; bilateral off-window structure DOES.
- G1 (1:1 razor lock, registered): FAIL 0/3 both freqs (block-argmax err
  fast .70-1.05, slow ~.47 — the cord keeps its intrinsic 0.5-0.83 Hz
  attractor alongside the driven component; never tracks target within .1).
- G1' (n:m spectral, ADDENDUM 1): PASS 3/3 both freqs — P_mm(f_drive)/open
  at hyb01: 0.7 43.7/59.1/37.6x, 1.4 29.5/235.1/54.2x; chop envelope
  181-273x (hyb01) = the motor output FOLLOWS the chop gating. DOSE
  INVERTS: gentle amp .1 beats .3 at BOTH frequencies (L64 dose-dominates
  family); at .3 the fast seg SUBHARMONICS (s33 P@0.7 = 22.6 = 2:1 lock,
  the male contract has no subharmonic row).
- G2 structure: PASS 3/3, duty_07 1.0/1.0/0.996 — the female cord holds
  bilateral antagonist structure through the chop schedule far better than
  male (.45-.64); open-arm baseline is bilateral-healthy (S_L .64-.67 /
  S_R .68-.74 both sides) — the male gas's left-handedness (L70 card) is
  NOT a female property.
- Open-arm rhythm: 0.50-0.83 Hz ratio 644-942 (L65 replicated under this
  script's machinery).
ANCHORS: C0 21st consecutive — l65conv mm BIT-IDENTICAL 0.0 x3 seeds vs
l65/raw_l65.npz (state exact); pooled pool traces 2-6e-08 (float32 sum
order: concat vs row index order — disclosed, mm proves the trajectory).
Subnet/pool/mech asserts all exact (21,249 / 627,051 / Ti 50-51/6-6, Tr
31-31/24-24 / DNg100 2 / mech 4,848 = cell_function tactile+proprioception,
the male mechano_tactile+proprioceptive analog 3,588/6,370).
INSTRUMENT: probe's open-arm f/ratio labels were crossed (L35 class,
caught by magnitude sanity); one crashed json.dump corrupted
results_l68.json mid-write — BOTH verdict stages re-derived from raw
npz checkpoint, zero rollout waste (2 code bugs pre-data: uppercase-side
pool filter, DATA-dir shadowing drive D).
CONTRACT CONSEQUENCE (L57): tracking row = MALE-ONLY (1:1 razor lock does
not generalize; female locks spectrally/n:m, amp-tuned — an n:m row with a
dose map is the female-honest form); structure/off-window rows GENERALIZE
(female duty_07 ~1.0). Slice B (census n=16 + amp map) NOT run — verdict
did not require it; card CLOSED. Artifacts: l68/ (PREREG + ADDENDUM 1,
raw_l68.npz, results_l68.json). No live changes.

## L69 — echo-side-dose-response (tick 93, 2026-11-14)

QUESTION (ideas-34): before "S_R is structural" hardens into contract
language, does ANY ronly-echo dose flip S_R positive? Sweep ronly x gain
{.05,.1,.2,.4} x delay 5 (sign -), census n=16, l67 machinery verbatim,
open reused from l67 stored; lonly swept at the same gains (superset of the
card's best-dose mirror control). PREREG l69/PREREG.md + ADDENDUM 1.

VERDICT: STRUCTURAL CEILING CONFIRMED — no dose flips S_R, and the dose
demonstrably LANDS. P1 FAIL at every gain: dSR_mean +.032 / -.019 / +.053 /
+.019, Spearman rho vs gain 0.0 (no dose ordering at all — pure L59 lottery
scatter, per-seed -.45..+.45); P2 PASS flat-floor (max +.053 << +.10 gate),
STRENGTHENED by the landing probe (ADDENDUM 1): dm > 0 on all 128 arm-seeds
(wired_dead 0) + dose-dependent amplitude swing +9.4% -> -2.0% — the echo
enters at every dose and S_R still does not care. It is not a wiring floor;
S_R marginality is substrate-level (L67's routing-unrescuable verdict now
dose-hardened: L57 D5 stays bilateral at gain .1, no dose caveat needed).
P3: crossed law holds 3/4 doses (g.2 the exception, both deltas noise-scale).
P4 PASS: lock pristine at every dose (e2_max < .5, no catastrophic arm).
P5 MIRROR (new finding): the lonly ipsi bonus PEAKS at g.2 (+.230 dSL) and
the high doses actively HURT the other side — lonly dSR -.079 (g.2) / -.124
(g.4), dutyR -.096/-.109 = the L63 high-gain toxicity, now measured on the
DOSE axis: an echo gain above ~.2 buys nothing on its own side and taxes the
other. Best-r-dose mirror (registered rule, ronly_g200): dSL +.230 vs dSR
-.079 at the same gain — the substrate's own L/R asymmetry (open SL .326 vs
SR .153) is the binding constraint, not the routing.
ANCHORS: C0 PERFECT (ronly@.1 AND lonly@.1 bit-identical to l67 stored, 160
keys, 0.0); C0O open recompute == l67 json exact; C0P first_div == 6 all
arm-seeds + prefix [0,6) zero; C1 af ok; wired_dead 0. Two pre-rollout
assert fixes (OFF_TS count 44, one dead editing artifact), zero wasted
rollouts. CPU 611 s. Artifacts: l69/ (PREREG + ADDENDUM, raw_l69.npz +
raw_partial, results_l69.json). No live changes.

## L70 — sl-sr-baseline-anatomy (tick 94, 2026-11-14)

VERDICT: G2 — the male open-cord left-handedness (SL .326 vs SR .153) is
STATE/SEED TEXTURE on a nearly side-symmetric sheet: a LEFT-BIASED ATTRACTOR
LOTTERY, not wiring. Every static arm fails the pre-registered |z|>=3 bar:
M1 pool input LI z in [-0.56, +1.29] (Tr_f flexors even lean R, LI -.077);
M2 the DNg100 DRIVE PAIR IS BILATERALLY SYMMETRIC by mirror-CONTRA wiring —
cell 6 (soma L) loads R targets (massL 2.5k/massR 9.2k), cell 9 (soma R)
mirrors it (9.9k/2.8k), pooled LI +.015 z 0.23 (L24's DNg105 crossed form,
now shown for the regime's own drive); M3 reciprocity LI_recip +.029 z 2.56 —
same-direction trend, BELOW the bar (the only lean the wiring offers, and it
is weak). M4 nails the texture: per-seed h = SL-SR spans [-.155, +.520]
(sd .208 > mean .173), h>0 on 12/16 (one seed is RIGHT-handed) — the gas
RE-ROLLS handedness per seed with a left bias; L59's miss migration is
indeed its signature. No cells named (G1's "name the cells" branch moot);
sub-threshold observation only: direct DNg100->pool mass favors L pools 67
vs 41 (flexor 59 vs 27) — tiny counts, no claim, points the same way as M3.
M3/G3: the male premotor sheet (10,826 intrinsic + 708 motor, 1.65M edges)
carries 201,919 reciprocal pairs = 22.4x ER enrichment — the reciprocal
structure is REAL, and MS-rewiring (degree-preserving, not pair-preserving)
would collapse it to ~ER: the tick-90 caveat now has a measured basis and
L32/L45 rewired-null claims carry it (reciprocity-matched null tier = future
card if a recurrent-structure claim ever gates something).
M5/G4 CROSS-GRAPH: female BANC sheet (9,094 nodes, 311,620 edges) recip
fraction 0.0625 = 0.45x male -> registered prediction FALSIFIED on the raw
fraction — but over-rep vs ER is 33.1x, HIGHER than male's 22.4x: the raw
fraction tracks graph DENSITY (female subnet 627k vs male 2.98M edges),
the density-normalized enrichment does not. Transferable rule: cross-graph
motif comparisons are only honest as OVER-REPRESENTATION, never as raw
fractions. Female per-side LI z 0.93 = side-symmetric sheet, coherent with
L68's bilateral-healthy female gas.
ANCHORS: A1 substrate asserts exact (n 21,516 / 2,977,920 / DNg100 2 /
8 pools non-empty, l67 numbers); A2 M4 recompute == l66 stored open means
(.326/.153, tol .01, PASS); A3/A4 raw nulls + observed checkpointed to
l70/raw_l70.npz + raw_l70_banc.npz BEFORE verdict; 100-draw side-label
permutation nulls (L24 form) on every asymmetry metric. CPU 10 s + 3 s.
Artifacts: malecns/l70/ (PREREG, results_l70.json, results_l70_banc.json,
raw npz x2, run.out x2). No live changes.
CONSEQUENCE: no side-targeted static lever exists to repair S_R (L67/L69
dynamic verdicts now have the static counterpart: the asymmetry is not in
the wiring, it is in the attractor landscape); the endgame controller
(L61 handoff) treats handedness as a per-seed roll to be measured, not
steered — consistent with the no-hop distributional gates.

## L71 — dream-vs-day C2ST on her own readouts (tick 95, 2026-11-14)
Instrument: (Butter)fly-Dream 2611.01866 form — logistic C2ST (IRLS, Add.1)
on mean/sd/lag1/mac of 7 pools (DAN/KC/dop/ser/oct/LC/CX), 20-step L3-protocol
fires, 13-event battery x 10 seeds, grouped-by-event 5-fold CV + 200-perm null.
Arms: A state (day-x0.3 vs night-x0.3) | B selection (night-all vs night TOP5
by acquisition dop) | C honest (day-x1.0 vs night-x0.3 TOP5). PREREG + 3
addenda in l71/PREREG.md; raw_l71*.npz checkpointed pre-analysis.
- A (state): AUC .628-.636, p=.005 EVERY run, within-event .69 — the
  day-residue vs night-relaxed initial state IS a readable dream signature
  (P3 predicted chance: honest negative of my prediction).
- B (selection): AUC .757-.759, p=0 every run, stable — the STRONGEST
  signature: the night's choice itself (louder traces read dream-like,
  generalizes across events). within-event degenerate by construction (disclosed).
- C (honest): cross-event median ~.63, range .51-.70 over 4 IRLS runs
  (UNSTABLE — dim dreams of loud events overlap full-gain quiet day events;
  fold-local-sd weight explosion amplifies; ranks stand) — does NOT robustly
  clear .75 (P1 FAIL); within-event STABLE .74-.77 across all 5 runs: paired
  same-event dream-vs-day separates reliably. Gain cue is event-relative.
- Carrier: amplitude family (mac/sd) dominates every weight table; lag-1
  dream-positive only 3-4/7 pools (P4 weak) — their lag-1 carrier does NOT
  transfer as primary at rate fidelity.
- Selection key finding: TOP5-by-dop = swat/hold/hose/goats/pet (touch/sound
  distress+loud family; peas only .073) — dop at acquisition ranks salient
  touch over food; her nights replay arousal, not meals.
- Instrument lessons: grouped-by-event CV is the WRONG form for a
  never-trained single-group control (A2 run-1 .29 -> sequence-level form
  .99+); CUDA sparse-mm atomics break bit-reproduction (CPU cord-lane anchors
  were exact 0.0 — replicate instead on GPU, report spread).
Verdict: HER READOUTS TELL HER DREAMS FROM HER DAYS — carried by WHAT the
night selects > state residue > gain; not by autocorr structure. [lab]

## L72 — dream-vs-day C2ST on her REAL days (organic day_log battery)

Card: L71's instrument on the live world.json day_log (copy-not-mutate).
Organic battery: 77 instances, 100% class 'water' (all 2026-11-14), logged
acquisition dop .158-.198 sd .0105; tonight's real replay set by the live
rule = top-5 by dop (MAX_REPLAYS=5 caps the 8-instance decile). Lab anchor
re-derived from l71 raw npz THIS tick (L44 rule): water arm-A within-event
.82 (.81-.83, 4 replicates).

- A_LIVE (state, x0.3-vs-x0.3): AUC .833/.833 (2 CUDA replicates), null
  [.46,.54] p=0 — INSIDE registered band [.72,.92]: the lab state signature
  holds on the organic day, water specifically.
- C_LIVE (honest, x1.0 day vs x0.3 night): AUC **1.0** both replicates,
  zero rank errors at 770-vs-770 — ABOVE the lab cross-event pooled
  (.51-.70) AND within-event (.74-.77): L71's honest-contrast instability
  was CROSS-EVENT composition mixing with the gain cue; within the single
  class her nights actually replay, day-vs-dream is perfectly separable.
  Carrier amplitude again (amp_in_top3 2/3; oct_mac/LC_sd/CX_mac top).
- B_LIVE (EXACT live selection rule, top-5-by-logged-dop vs rest-72):
  AUC .526/.526 p=.68 — CHANCE as predicted; B_Q power form .491/.491
  p=.87 chance. The selection lever is structurally absent from same-class
  days: re-fires carry no instance context (A6 r(logged dop, re-fired dop
  mean) = .0798 ~ 0) — whatever a selection key changes must act at
  ACQUISITION time (feeds L73).
- A7 spread: organic dop CV 6.3% (max/min 1.25) vs lab battery cross-event
  CV 49.8% (3.87) — the scripted-vs-organic gap in one number; an organic
  single-class day offers the selection lever an ~8x narrower key.
- Anchors ALL PASS both replicates (A0 finite/af, A2 1.0, A3 1.000, A4
  .0039, A5 nulls [.49,.50]). grouped-by-INSTANCE 5-fold CV (single-class
  analog of grouped-by-event); 200 nulls/arm; IRLS (L71 Addendum-1 form);
  weight-magnitude caveat carried (fold standardization).
Verdict: on organic histories the dream/day signatures hold in the only
form a single-class day permits — state + gain (gain PERFECTLY); the
cross-event selection lever (lab's strongest, .757) is structurally absent
from her actual one-class days. [lab]

## L73 — selection-key A/B for night consolidation (tick 97, 2026-11-14)

Design: 41-event diverse battery through the EXACT live path (41 -> n=5
replays/night), one dusk snapshot per seed (7/21/33), arms off / doplive /
dop-replica / dan / sal / joy / food / food5, identical night+morning,
read-only DAN/KC probes at dawn. Pairing: snapshot restore + brain-gen
restore + last_seen pinning (PREREG). Anchors: dop-replica BIT-IDENTICAL
to live consolidate_night 3/3; off BIT-IDENTICAL to dusk 6/6; subset
dusk cross-run max|d| 3.2e-5..1.6e-4 (CUDA sparse-mm, ADDENDUM 2).

1. THE LIVE DOP KEY WRITES NOTHING ON A DIVERSE DAY: it selects
   hold/swat/hose every seed (P1 3/3 — L71's touch-bias, now at the
   write level) — zero KIND events, so the night is downscale-only:
   morning trust .1043 < off .1063. On any day whose most salient
   moments are unpleasant her consolidation is effectively OFF and the
   x0.98 dFB pass slowly erases. (On her real one-class water days this
   cannot fire — water is kind AND dop-rich; L72's organic finding and
   this one compose: the live rule is safe today, fragile by
   construction.)
2. KIND-SELECTING KEYS RESTORE THE WRITE: joy .295 / dan .271 / food5
   .202 vs off .106, dop .103 (P2 PASS, subset-aligned). dan selects
   5xpeas (DAN-at-acquisition is a pea detector on this battery); joy
   tin,tin,peas,peas,peas; sal selects IDENTICALLY to dop (cos 1.0 —
   salience and dop rank the same events).
3. PEA DEPTH (P3 PASS 3/3): food5 pea-probe DAN lift +.0141..+.0148 vs
   dop ~0 (noise +-0.0004) — but food5 replayed WATER (water out-ranks
   peas on logged dop inside the food pool): its pea lift is
   GENERALIZATION, not pea replay. The true pea-nights are dan/joy:
   peas DAN lift +.039/+.043 vs +.019/+.022 on every other class (~2x
   replayed-class bonus) and KC peas +.011 vs +.0026 (~4x) — replaying
   peas deepens the pea memory circuit specifically (DAN+KC, the L9
   structure channel).
4. LEVEL vs PROFILE: all positive arms' lift profiles rank-identify
   (Spearman 1.0 for dan/joy/food5 pairwise; the registered vs-dop .943
   is DEGENERATE — dop's lift vector is noise-scale-zero, disclosed).
   Substrate: night writes land >=.986-cos on the SAME edges (bulk
   deepening of the day's Hebbian mass; plas-norm ratios dan 2.6x /
   food5 2.0x dop); the class bonus is a small rotation, not new
   circuits.
5. Controller-facing: the selection key is a real lever WITH a failure
   mode — dop wastes the night after unpleasant-salient days; dan/joy
   turn every night into food-memory consolidation. A dop-among-KIND
   hybrid is the obvious live-proposal candidate — parked for the owner
   (runtime changes travel as pinned deltas, never prose).

Small-n: 3 scripted seeds, all per-seed signs consistent (trust deltas
.202/.202/.202 food5; P3 3/3). Evidence: l73/ (PREREG + 2 addenda,
results_l73*.json, raw npz x3 + subset x3, verdict_l73.json, run*.out).
[lab] no live changes; sessions/ untouched (world.json advancing on its
own ticks throughout).

## L74 — multi-night key trajectories: the single-night difference
## COMPOUNDS 24x in a week; display saturates, substrate separates 3.2x
[tick 98, 2026-11-14]

5-day diverse week (41 events/day, fresh permutation per day, arm-blind),
4 keys x 3 seeds, one trajectory per arm-seed (arms diverge at night 1;
day 1 = the L73 battery verbatim behind a shared dusk snapshot). Run
3602 s CUDA; incremental checkpoint per arm-seed.

Anchors ALL PASS: dusk-1 cross-run max|d| 1.23e-4 (<5e-4); dop night-1
selection EXACT 2/3 seeds, set-equal 3/3 (s33 hold<->swat logged-dop
near-tie inside the drift; both non-kind -> zero write difference;
ADDENDUM 2.1); snapshot restore bit-fidelitous 3/3; off arm a no-op 3/3.

- P1 COMPOUNDING CONFIRMED (plas form, ADDENDUM 2.2 — display trust
  saturates 1.0 in EVERY arm incl. off by morning 4: day Hebbian writes
  alone pin the display on a 180-kind-event week, L53's ~94-event pin
  reproduced at week scale): joy-dop plas gap .00095-.00096 at morning 1
  -> .0233-.0239 at morning 5 = 24x growth, 3/3 seeds. The key choice is
  a small single-night difference that the week multiplies.
- P2 EROSION CONFIRMED, BOUNDED: dop < off at mornings 2 AND 5 on 3/3;
  dop/off plas ratio .980 -> .947 (m5 .945-.950) — ABOVE the pure
  0.98^5 = .904 downscale line: day writes compensate part of the
  downscale. Erosion real, not catastrophic.
- P3 CLASS DEEPENING CONFIRMED: pea-probe DAN lift (m5-m1) joy
  +.510/+.510/+.529, hybrid +.469/+.414/+.482 vs dop +.166/+.136/+.176
  ~= off +.171/+.142/+.180. The LIVE dop key's nights add ~nothing
  beyond day exposure to food memory (functionally no-consolidation at
  week scale — L73's finding, now compounded); kind keys triple it.
- P4 HYBRID = KIND FAMILY: chosen 100% kind on all 15 nights; m5 plas
  closer to joy than dop 3/3; hybrid .0205 captures ~79% of joy's .0258
  gap over dop .0080 — dop-informed selection loses little.
- P5 PIN REACH: every arm crosses the .005 display pin (off .0083, dop
  .0080, hybrid .0205, joy .0258) — L54's "pin = dense-visitor
  phenomenon" bound is crossed by any 5-day diverse week; the DISPLAY
  masks all key differences while the SUBSTRATE separates 3.2x.

Consequence for L75 (hybrid proposal parked for the owner): the proposal now
carries trajectory evidence — hybrid keeps dop-informed selection, lands
in the kind family, and roughly 2.5x's the substrate trust vs the live
key at week scale. Display-side: any week saturates /trust — key
differences are only visible in synapse substrate and probe reads, never
in the visitor-facing number (L54's recommendation stands).

Evidence: l74/ (l74_multi.py, l74_verdict.py, l74_fig.py, PREREG.md +
ADDENDA 1-2, results_l74{,_s7,_s21,_s33}.json, raw_l74_s*.npz +
raw_partial checkpoints, verdict_l74.json, traj.png vision-PASS 1 pass +
numeric-QA cross-check 12/12). [lab] no live changes; sessions/
untouched; duck /needs 200 mid-run under shared GPU.

## L75 — hybrid-key pinned delta (tick 99, 2026-11-14)

PROPOSAL artifact, not a deploy: the dop-among-KIND night-selection key
(L73/L74-measured) as a PINNED DELTA to live bridge.py + offline gate
suite, parked for the owner (PROPOSAL.md). Delta = module-level select_replay()
+ one call-site swap in consolidate_night (write/downscale/dream code
untouched); base sha256 d8cd0587… pinned, live tree never modified
(asserted at start AND exit of every run).

Gates G1-G7 (PREREG l75/PREREG.md + ADDENDUM 1): G1 diverse day -> hybrid
keeps ONLY kind events (live rule on the same log keeps swat/hold/hose —
the L73 failure mode); G2 all-kind day -> hybrid ≡ live rule EXACTLY (her
real one-class water days unchanged by construction); G3 all-aversive day
-> fallback ≡ live rule (dream-only); G4 budget pinned to the DAY never
the pool (41/3kind -> 3; 10/8kind -> 1); G5 delta integrity STRUCTURAL;
G6 dynamic diverse night through the real patched path (entry, all-kind
fired sequence == raw top-5-kind-by-dop prediction, write strictly over
the downscale floor, bookkeeping + second-call gate, L74 stored raw-
multiset anchor); G7 dynamic all-aversive night (chosen == live top-1,
plas == pre x 0.98 exact = pure downscale, dream-only).

INSTRUMENT LESSONS (both caught by the gates, zero silent passes): (1) a
helper inserted at a mid-class seam (flush-left between indented methods)
SILENTLY RE-MOTHERS every method after it into nested defs inside the
helper — compiles, imports, helper works, class loses session_turn et al.
(run 2 AttributeError; G5 is now structural hasattr checks, not a textual
grep); (2) s.dream_pool is UNIQUE-event by live design (L4) — raw-vs-
unique comparison can never match; capture the raw replay sequence with a
counting shim around senses.input_for (ADDENDUM 1). CPU-only run (laya
trainer owned the GPU — lane rule): 41-event day 135 s, night_entry 3x
observe(60) ~ 18k steps ~ 5 min per night on CPU.

Evidence: l75/ (PREREG.md, bridge_l75.delta.md, apply_delta.py,
test_l75_hybrid.py, PROPOSAL.md, results_l75.json, run_l75.out). No live
changes; deployed only on the owner's word via the hardened path.

## L76 — sal-dop key identity (tick 102, 2026-11-15)

Question: L73's `sal` key picked identically to `dop` (cos 1.0) — general
identity or battery-specific? Answer: the identity is ARCHITECTURAL, and
it breaks exactly where designed.

**The law (mood.py source): the salience axis's event target IS the
dopamine peak** — `t_sal = 4 * (dop_peak - 0.05)`, plus a body floor
(shiny .25), delivered through peak-hold (tau 15 s). Verified EXACT on all
four corpora: max |pred - logged| 1.9-2.0e-4 on L73 batteries x3 seeds AND
the organic 77-water day_log (the residual IS the dop 4-dp rounding bound;
zero unlogged sal sources in the live serve). Deviation channels, measured:
(F) floor — shiny x3/battery; (C) carryover — 1 event/battery (slug after
water, .324*exp(-22/15) = .0748 exactly), bounded by cap*exp(-gap/tau) <=
.23 at lab gaps, which can NEVER reorder a loud battery's top (lifting a
.68 target needs a predecessor > 2.9 > the 1.0 cap); (K) clamp at dop
>= .30 — never engaged anywhere to date (max .228). L73's cos 1.0 was
never a coincidence: top-decile MULTISETS coincide on all 4 corpora (P4;
seed 33 shows an intra-top order permutation, same multiset).

**Dynamic separator** (28-event quiet battery, peas x14 + shiny x8 + tin x4
+ slug x2, n_top 3; arms off/dop/sal, l73 machinery verbatim, 3 seeds —
145 s CUDA):
- P1 PASS 3/3: selection DISJOINT — dop replays {peas x3}, sal replays
  {shiny x3} (C0b: chosen == closed-form prediction from logged day_log,
  both keys, all seeds).
- P3 PASS 3/3: morning pea-DAN lift dop +.0346..+.0349 vs sal
  +.0130..+.0134 = 2.6x — the replayed class keeps the memory.
- P2 FAIL as registered (.90 gate), informative: write cos .9806-.9808 —
  the plas WRITE is bulk even under disjoint selections (L73's bulk law on
  a disjoint battery).
- Second-order finding: the sal night is a WEAKER night — write mass
  .00036 vs .00059 (shiny's replay co-fires less DAN), morning trust .272
  vs .317 (off .199), and even the SHINY probe lifts more under the peas
  night (+.0143 vs +.0086): generalization dominates, class rotation is
  the small term.
- Anchors: C0a off bit-identical to dusk 3/3; law on the SEP battery
  1.8-2.0e-4 (C0d).

**Verdict for the parked L75 hybrid decision**: a sal-based key is a REAL
but strictly worse lever — it selects body-level NOVELTY over food
comfort, writes less mass, and deepens the salient class's memory less
than a dop-key night deepens food. The identity sal == affine(dop) holds
everywhere except floor/carryover batteries; on loud batteries the keys
are provably equivalent. The hybrid (dop-among-KIND) remains the right
shape; nobody should reach for "salience" as the more natural key.

Evidence: l76/ (PREREG.md, l76_identity.py, results_l76_static.json,
results_l76_s{7,21,33}.json, results_l76_dyn.json, raw_l76_s*.npz,
verdict_l76.json, run_dyn.out). No live changes; sessions read via the l72
world copy.

## L77 — echo-on-endgame-census (tick 103, 2026-11-15) — SHIPPED, NEGATIVE at the registered bar
Question: does the l66 content-cell echo (g .1, -, 50 ms), run ON the l59
endgame schedules, bias the pooled structure coin (8/16 both arms)?
- P1 FAIL at the registered >=11/16 bar: hybrid_fb k=10/16 (Wilson
  [.386,.815] — still compatible with a fair coin at n=16), hynohop_fb
  k=8/16 (unchanged). Net flips hybrid_fb: up 6 / down 4 = mean shift with
  lottery scatter, not a lever.
- The benefit stays WHERE L66 MEASURED IT: duty_07 +.080 (hybrid .569→.649)
  / +.126 (hynohop .547→.673); S_L rescue signature present (seg0 SL
  .445→.579, seg2 .272-.344→.451-.472); the fast-seg structure lottery is
  UNTOUCHED and slightly worsened (seg1 duty .375→.292 / .402→.298) — the
  L52 entry-state law survives the echo.
- Lock razor PRISTINE in all four arms (seg1 err<=.01 16/16 each); P3
  budget: echo mass 12.7-12.8% of entrain mass (mean amp .0142).
- Registered EXPECTATION held (k in [9,13], duty07-lift > seg1-lift) — the
  discriminating structure carried the information, not the pooled k.
- L57 consequence: row D5 unchanged ("measured option at exactly this
  cell, never a default") + the endgame pooled gate stays a per-seed roll
  (L70 handedness lottery); echo cannot serve as the endgame structure lever.
Anchors: C0a hynohop == l59 raw BIT-IDENTICAL (23rd consecutive chain
anchor); C0b hybrid == l59 raw BIT-IDENTICAL; C0x hynohop_fb == l66 raw
g01_d05_m BIT-IDENTICAL (cross-run wiring probe, l59-loop == l66-loop);
C0P amended (ADDENDUM 1, third L44-class instance: first_div == 6 ==
l66 stored, my PREREG had mis-carried the ==5 sentence); C1 green;
wired_dead 0 (dm > 0 all 32 fb arm-seeds). D4 value anchors: twin pooled
means .489/.513 == l59 stored exactly. Evidence: l77/ (PREREG + ADDENDUM 1,
results_l77.json, raw_l77.npz) + l77_census.py + l77_verdict.py. No live
changes.

## L78 — banc-echo-replication (tick 104, 2026-11-15) — SHIPPED, MALE-ONLY at the content bar; female lift is PERTURBATION-carried

Question: does the male content-cell echo (g .1, sign −, 50 ms; L64/L66)
have a counterpart on the FEMALE BANC cord, or is L57 row D5 male-only?

Headroom first (STORED l68 results, L44 rule): female Ti is bilateral-
healthy at ceiling (duty_07 .94-1.0) but Tr is SIDE-SPLIT — SL median
NEGATIVE on slow segs (−.18/−.00/−.41 seg0) with SR healthy (.53-.75),
duty .02-.34. The male marginal-side rescue question transposes cleanly.

Design (PREREG l78/PREREG.md first): l68 substrate verbatim (glut-INH,
G .14/beta 2/D .2, hyb01 amp .1 schedule), 5 arms one shared-noise group
x 3 anchor seeds: open (l68 replica), fbn_g01 (literal male cell), fbp_g01
(sign re-derivation), fbn_g03 (budget-matched; literal cell = 25.5% of
entrain mass on female = 2x male 12.7%), sham_g01 (next-seed cyclic donor
from l68 stored traces).

VERDICT: MALE-ONLY at the registered content bar — and the split is a
MECHANISM finding. (1) The female structure lift is real (fbn_g01 duty_
slow +.285/+.166/+.116, 3/3) but the DONOR SHAM CARRIES 96% of it
(+.277/+.042/+.227, 3/3; duty_off sham HIGHER +.311 vs +.273) — on male
the sham was ~0 (L66: fb +.186, sham −.001); on female ANY mech echo
re-rolls/lifts the marginal Tr SL side (L67/L69 perturbation class).
(2) R2 Tr-SL rescue passes for EVERY arm INCLUDING sham (fb SL mean .290
vs sham .225 = 78% sham-carried). (3) Loop content IS detectable on
female — as a COST: the fb arms crash the per-seg spectral lock below
.5x open on one cell each (fbn_g01 s22-seg1 .45; fbp_g01 s22-seg0 .32;
fbn_g03 s11-seg0 .37) while the donor sham passes 9/9 — a content-shaped
rhythm destabilization (n=3, suggestive, disclosed). (4) R3 no-harm
FAILS at every dose incl sham (Ti duty_07 → .69-.96 vs open .88-1.0,
worst −.293) — the female's bilateral-healthy ceiling is echo-taxed.
(5) Sign winner MATCHES male (negative; the positive echo crashes
duty_fast −.532/−.327/+.041). Auto-gate's CONTENT-GENERALIZES was a
knife-edge duty_fast pass (sham rule margin 3e-4, one seed down) —
adjudicated NON-CARRYING per the L55 rule (ADDENDUM 1, verdict amended
in results_l78.json with verdict_auto preserved); census NOT triggered.

Consequence: L57 row D5 keeps its male-only flag; cross-specimen echo
contract = male content / female perturbation + lock harm. New cross-
graph lesson for the lane: a content cell certified by a sham on ONE
connectome does not transport — the sham control is the transport test.

Anchors: C0a open == l68/raw_l68.npz hyb01 BIT-IDENTICAL (max|d| 0.0 on
mm + Ti/Tr x 4 traces x 3 seeds — 24th consecutive chain anchor; adding
arms to the shared-noise group left the shared arm exact). C0P two-level
timing anchor exact: first mech divergence == 5, first MOTOR-mm
divergence == 6, every arm/seed (derived from l66 STORED json, not the
log sentence — L77 rule held). C2 dm > 0 all treatment arm-seeds; C1 af
in range. Instrument catches pre-rollout: nonlocal->global at module
scope (L77 class, SyntaxError, zero wasted rollouts); c2 dict-key
collision fixed pre-run.

Evidence: l78/ (PREREG.md, ADDENDUM.md, l78_run.py, l78_verdict.py,
results_l78.json, raw_l78.npz, raw_partial.npz, scan_l78.json,
out/run.out). CPU 33 s rollouts; no live changes; sessions/ untouched.

## L79 — fast-window rehosting: the 5-s chop re-prime is structure-TOXIC; L58's gap lesson is protocol-bound twice (tick 105, 2026-11-15)

Question (L52's named open lever): fast-seg toxicity is entry-state-
conditional and dwell-deepened; the one untested shape was a POST-
TRANSITION re-prime — one 5-s chopped head (on 2000-2500, identical to
baseline) + one L58-ratio 200-step off-gap (2500-2700) immediately after
the frequency step, before continuous fast drive. Machinery l77_census
verbatim (FB removed); arms hynohop/hybrid are l59 bit-identical anchors;
16 census seeds; PREREG l79/PREREG.md first.

P1 VERDICT: HURT at the registered claim level, BOTH schedule families.
reprime W_post duty .249 vs hynohop .411 (paired mean delta -.162,
non-positive 13/16, 5 exact zeros = seeds dead in BOTH arms); hyreprime
.274 vs hybrid .422 (-.148, 12/16). The damage is carried by seeds whose
twin had HIGH fast structure (s22 1.0 -> .025; s104 .662 -> 0) — the gap
removes the fast structure a seed would have carried and gives nothing
to the structure-poor (a couple of up-flips, lottery scatter; L77-class
shape, negative). Pooled diagnostic drops too (duty_all .489/.513 == l59
EXACT -> .460/.432).

P3 mechanism discriminator: NO re-formation signature — d_early is
negative from the first straddle window (-.147/-.07) and deepens with
dwell (reprime d_late -.223): the gap never hosts structure, it
subtracts from the start. Re-formation predicted W_early >= W_post;
measured the opposite ordering. The L58 200-step gap formed structure on
the 0.7 CHOP; the same gap inside the 1.4 continuous segment is toxic —
second instance of the protocol-bound-tolerance class (L58's own slack
law, now on the gap shape itself): drive-regime numbers do not port
between protocols, in either direction.

P2 lock: post-gap lock pristine for reprime (16/16 err <= .01, mean
.0016); hyreprime 15/16 (mean .0324, one seed). Straddle block errs
.34/.46 by construction (2-s free gap inside a 5-s FFT block) — excluded
as registered. P4: W_post misses stay S_L-owned (.60/.556 shares — L59
anatomy holds under the intervention). P5: budget -4.2% drive-on (the
intervention REMOVES drive; the honest reading is not "less drive hurts"
but "the free window itself costs" — amp rows in L58 showed the fast
window is amp-insensitive; candidate mechanisms: L45b-class free
migration out of a drive-supported partial antiphase, or the gap
breaking phase-locked support it cannot re-acquire on resume).

Consequence for L52's "different state class": the chop-head re-prime
shape is EXCLUDED (with volleys and without). The remaining named shape
is the OPPOSITE sign of intervention — L34's strong sinusoidal drive
RE-HOSTS antiphase via the reflex arc; seeded as L81 (ideas 40). L57
contract rows unchanged; L80's window-scoped amendment unaffected (it
was already scoped to the 0.7 segs, where this result adds no
conflict).

Anchors: C0a/C0b hynohop+hybrid == l59/raw_l59.npz BIT-IDENTICAL (mm +
4 traces, 3 seeds — 25th consecutive chain anchor); C0P-1 prefix fork
[0,2500) max|d| 0.0 16/16 both pairs; C0P-2 first divergence == 2501
everywhere (one-hop law from l77 STORED json: fd = perturb+1); C1 af
in-run PASSED; wired_dead 0. Instrument notes: write-time AMPA assert
caught a TWINS-unpack reversal BEFORE any rollout (zero waste); analysis
crashed post-checkpoint (dist_of nested-key) -> l79_verdict.py re-derived
ALL reads from raw_l79.npz, zero reruns (l77 precedent); verdict-script
P5 assert off-by-settle (4800 vs 4400) — my own check, fixed, disclosed.

Evidence: l79/ (PREREG.md, results_l79.json, raw_l79.npz,
raw_partial.npz, run.out), l79_reprime.py, l79_verdict.py. CPU 245 s
rollouts; no live changes; sessions/ untouched.

## L80 — window-scoped structure row: the L57 contract amendment, drafted + parked (tick 106, 2026-11-15)

No new runs (by card design): the amendment synthesizes l59 + l66 + l77 +
l79 into a proposal. Every cited number re-derived this tick from STORED
artifacts (L44 rule) — l77/results_l77.json, l79/results_l79.json (census
n=16, seeds 11,22,33,101-113); l59 numbers carried by l77's bit-identical
C0a/C0b anchors.

- The POOLED gate stays a fair coin under every tested intervention:
  8/16 [.28,.72] both l59 arms; l77 fb arms 8/16 and 10/16 [.386,.815];
  l79 re-prime even lowers pooled (.460/.432 vs .489/.513). No pooled
  Wilson lower bound >= .5 in any arm.
- The 0.7-window is where levers land: echo lifts duty_07 mean .547->.673
  (nohop, +.126) / .569->.649 (hybrid, +.080), floor .297->.437 /
  .317->.447, seg0 S_L .445->.579, lock 16/16 in ALL FOUR arms, echo
  budget 12.7-12.8% of entrain mass.
- NEW distributional read (derived post hoc this tick from stored l77
  arrays — DISCLOSED; the .5-threshold form was pre-registered for
  POOLED in l59, applying it to duty_07 is this amendment's proposal;
  Wilson unadjusted for the 4-arm family): P(duty_07 >= .5) goes
  11/16 [.444,.858] -> 15/16 [.717,.989] on the nohop family (hybrid
  13/16 [.570,.934] both) — the strongest lever statement in the
  lineage, invisible at the pooled read.
- Fast-seg row: entry-state-conditional (L52), no known positive lever
  (echo .375->.292; l79 re-prime .411->.249 paired -.162, 13/16 non-pos,
  no re-formation signature) — L81 reflex-arc re-host is the one
  untested shape, already queued.
- AMENDMENT (l80/AMENDMENT.md, full before/after): C4 splits into
  C4a tracking (seg1 err <= .01, free) / C4b structure WINDOW-SCOPED
  (duty_07 distributional + Wilson at n=16; echo cell = the ONE measured
  lever, MALE substrate only per L78) / C4c fast-seg (diagnostic, never
  a gate, until a lever exists) / C4d pooled duty DEMOTED to reported
  diagnostic, never a gate. D5 tail amended with the L77/L78 endgame
  evidence.
- Disclosed: no donor-sham arm on the HYBRID schedule (L66's content
  certification ran on nohop; l77 hybrid_fb is echo on/off only —
  offered to the owner as the one optional symmetry run, 2 arms x 16 seeds).
- PARKED FOR BILL: BBS bill/agent-bbs#54 comment 2790 (marker
  miso:l80-structure-row:v1, body read-back byte-identical, posted
  07:46 EST). Live L57 table in this file unchanged until his word
  (L75 precedent).

Instrument notes: gitea.home.arpa DNS flapped mid-tick (LAN resolver on
<lan-ip> = the Gitea host itself; recovered) — posted via pinned IP
with correct SNI (Caddy internal-CA front refuses no-SNI handshakes with
TLS internal_error). Unexplained local oddity, disclosed: `python3
<file>.py` runs of the posting script hung in getresponse every time
while the byte-identical logic inline completed in <0.1s (5/5); shipped
inline. Timeout rule honored: marker re-fetch proved the hung runs never
reached POST (no duplicate). Evidence: l80/AMENDMENT.md,
scratch/l80_body.md; no live changes; sessions/ untouched.

## L81 — reflex-arc re-host: HURT at every dose; L52's shape space exhausted (tick 107, 2026-11-15)

Card: LANE.md ideas-40. The one remaining L52 shape with a measured prior
(L34: strong sinusoidal drive re-hosts antiphase through the reflex arc).
l79 machinery verbatim; the off-gap is replaced by a STRONG sinusoidal
mechano volley at the 1.4 carrier (amp {2x,3x} = {.6,.9} entrain, [2500,2800)
= 3 s), then back to continuous .3. Arms rehost2x/3x (twin hynohop) +
hyrehost2x/3x (twin hybrid), census n=16, PREREG l81/PREREG.md first; the
1x arm = registered NO-OP parity control (table-asserted, not rolled out);
CPU-only 613 s; no live changes.

- P1 HURT every arm at the l79 thresholds, and the verdict is carried by
  the LOCK-CLEAN 2x arms (le01 15/16, 16/16): rehost2x d_post -.353
  (wpost duty .411 -> .058, k>=.25 9/16 -> 2/16, Wilson [.035,.36] vs
  twin [.332,.769] — clean separation), hyrehost2x -.325 (.422 -> .097,
  8 -> 2/16); rehost3x -.223 (.411 -> .188, 9 -> 7), hyrehost3x -.274
  (.422 -> .148, 8 -> 5). d_late deepens below d_post (-.398/-.247/
  -.339/-.225) — the L79 dwell-deepening signature, not a transient.
- DOSE NON-MONOTONE: 3x hurts structure LESS than 2x (P1b nohop +.131,
  10/16; hy +.051, 8/16) but starts CRASHING the spectral lock (3x lock
  errs 0.5/0.89 on 3/16 nohop, 6/16 hy incl one 1.0 — L63/L78 strong-
  perturbation-at-transition family). The 2x arm is the honest primary:
  pristine lock, largest structure loss.
- THE L34 SIGNATURE IS THERE — AS DRIVE-HELD ONLY: the 3x arms lift the
  EARLY/straddle window ABOVE twin (d_early +.080/+.115, wearly mean
  .414/.495 vs .334/.379) and the lift DECAYS to negative by wpost and
  deepens late — re-hosting exists only WHILE the strong drive is on;
  its release re-rolls from the pumped state and lands WORSE than the
  plain transition (L47 law, now measured on the fast-seg entry). 2x is
  too weak to lift even early (-.080/-.112): perturbation without
  re-host. Per-seed d_early scatter is wide (-.66..+.79) — a lifted-
  lottery mean, not a uniform lift (L59 class).
- Misses stay SL-OWNED (sl_share .714/.875/.714/.818) — the volley
  damages the LEFT side's structure, as every intervention in this
  lineage does. Budget +6.6%/+13.2% entrain mass (drive-on steps equal,
  4800, by design). seg0 (duty_07 window) untouched by construction
  (prefix bit-identity).
- CONSEQUENCE: L52's post-transition shape space is EXHAUSTED — off-gap
  (L58 form, L79: HURT), chop re-prime (L79: HURT), reflex-arc volley
  both doses (L81: HURT). Fast-seg structure is entry-state-conditional,
  full stop; L80's C4c (diagnostic, never a gate) stands with "no lever
  exists" now measured three ways. The only positive structure levers in
  the lineage remain DRIVE-HELD: L34 strong drive while on, the echo on
  0.7 windows (l66/l77), chopped duty (L50) — Ideas 41 probes the
  echo's own hold law (L82) and the one untested ENTRY envelope, a
  frequency GLIDE (L83).

Anchors: C0a/C0b hynohop/hybrid == l59 raw BIT-IDENTICAL (mm + fL/fR/
eL/eR, seeds 11/22/33, max|d| 0.0) — 26th consecutive chain anchor;
C0P-1 prefix [0,2500) == 0.0 all 64 volley arm-seeds; C0P-2 first_div
{2501: 64/64} EXACT (l79 stored law, no addendum needed); C1 green;
wired_dead 0. Tables write-time asserted (twin parity outside [2500,2800),
volley amps exact, DRIVE_ON 4800 all arms, 1x no-op table-identity,
HOPA twin parity). Evidence: l81/ (PREREG.md, run.out, raw_l81.npz,
raw_partial.npz, results_l81.json), l81_rehost.py.

## L82 — echo-hold-law (tick 108, 2026-11-15)

Question (L80 C4b operational): must the l66 content-cell echo (g .1,
sign −, delay 5) run THROUGH the fast seg, or only during the 0.7 segs it
lifts? Arms on the l59 nohop schedule (census n=16): never / fb-throughout
(l66 wiring verbatim) / fb07-NEW (echo gate ON [0,2000) ∪ [4000,6000),
OFF for all of seg1). PREREG l82/PREREG.md first; one new rollout arm,
never/fb re-rolled fresh for pairing (shared noise stream, one generator).

VERDICT: MOSTLY WINDOW-LOCAL, WITH A MEASURED CONTINUITY COST — and the
fast seg is NOT rescued by gating.
- R2 (carries the verdict): seg2 duty never .488 → fb .608 → fb07 .556.
  The seg2 lift SURVIVES the gate: fb07−never +.067, 8/16 positive /
  8/16 zero-or-negative at seed level but sign-consistent positive mean
  (per-seed 8/8 strictly-positive among non-zero) = 56% of fb's +.119
  lift retained. fb07−fb −.052 (8/8 split even) = a real −44% continuity
  cost: the echo's fast-seg presence contributes to the LATER window.
  H-A band missed by .002 on the fb side; H-B far away → MIXED,
  H-A-leaning; amendment keeps "echo throughout" as the certified form,
  gated variant disclosed as cheaper-but-weaker.
- R3 FAIL — the finding: gating the echo OFF in seg1 does NOT restore
  the fast seg (seg1 duty .216 vs never .375, paired −.159, WORSE than
  fb's −.082). The echo's fast-seg structure cost is ENTRY-CARRIED
  (seg0 echo history sets the fast-seg entry state), not within-seg
  drive-carried. Side anatomy: fb07 seg1 SL median −.286 (INVERTED-side
  attractor selected, L46 SL|SR state) vs fb +.285 / never +.223 — the
  echo-ON arm actually HELD the fast-seg left side above never. Third
  independent demonstration of the L52 entry-state law.
- R4: echo mass 84.76 → 57.53 per seed (ratio .127 → .0862 = 32%
  saving), drive-on steps equal 4800.
- R5 (L80 gate form, summary): P(duty_07>=.5) never 11/16 [.444,.858],
  fb 15/16 [.717,.989], fb07 12/16 [.505,.898] — the gated echo keeps
  most of the lever; Wilson overlaps both neighbors.
- Lock never at risk: seg1 err<=.01 16/16 in every arm.

Anchors: C0a never == l59 raw BIT-IDENTICAL; C0x fb == l77 raw AND l66
raw BIT-IDENTICAL (mm + 4 traces, seeds 11/22/33) — 27th consecutive
chain anchor; C0P-1 fb07-vs-fb prefix [0,2000] == 0.0 16/16;
C0P-2 first_div measured {6, 2001} EXACTLY as pre-registered from the
stored law (echo gate closes at k=2000, motor pools one hop later);
wired_dead 0; not degenerate. Analysis crashed post-checkpoint on the
l77-class dom_freq[0] slip → l82_verdict.py re-derived ALL reads from
raw_l82.npz, zero reruns (l77/l79 precedent). The l66/l77 nonlocal→global
scope bug caught by SyntaxError PRE-rollout again (transcription, zero
waste). Evidence: l82/ (PREREG.md, run.out, raw_l82.npz, raw_partial.npz,
results_l82.json), l82_hold.py, l82_verdict.py. No live changes.

## L83 — glide-entry (tick 109, 2026-11-15)

Question: the last untested ENTRY envelope — replace the 0.7→1.4 STEP at
k=2000 with a linear phase-continuous chirp over G ∈ {200,300,400} steps
(amp continuous .3, budget equal: glide replaces the step's frequency, adds
no mass). Does the fast window's structure distribution lift? PREREG
l83/PREREG.md first; l81 machinery verbatim (6 arms × 16 census seeds,
shared noise stream); per-arm PHASE tables (twins share the base PHI object;
glide prefixes [0,2000) EXACT-equal by construction, asserted).

VERDICT: NEGATIVE at the registered HELP bar — and the negative has a
clean SPEED axis. No glide duration lifts fast-window structure above the
step entry; SHORT glides actively HURT:

- glide200 (2 s): wpost .224 vs twin .411 — HURT (d_post −.187, 12/16
  down, k 5/16 Wilson [.142,.556] vs twin 9/16 [.332,.769]).
- glide300 (3 s): .382 vs .411 — NULL (−.029, k 7/16).
- glide400 (4 s): .442 vs .411 — NULL (+.031, k 10/16; coin-level above
  twin, inside lottery noise at n=16).
- hyglide300: .310 vs .422 — NULL by the registered rule (−.112 but only
  9/16 down); the hybrid family's hops compose with the glide to nothing.
- P1b DOSE-ORDERING MONOTONE: d_post −.187 → −.029 → +.031
  (glide300−glide200 +.158 10/16 pos; glide400−glide300 +.060 9/16).
  Transition speed modulates the damage monotonically — slower is never
  worse — but converges to step-NEUTRAL at ~4 s, never above. The entry
  envelope cannot buy structure; L52's entry-state law stands with a
  measured speed axis attached, L80's C4c diagnostic row unchanged.

Registered predictions, honestly scored:
- E1 (no rescue, band [−.15,+.10]): HELD for glide300/glide400/hyglide300;
  VIOLATED DOWNWARD at glide200 (−.187) — a 2-s chirp is WORSE than the
  instant step: dragging the cord through its intrinsic-attractor band at
  that speed re-rolls structure harder than the hard step's single
  selection event (L41/L45b selection family, now on the entry side).
- E2 (Arnold tracking, ≥14/16 lock): PASS — lock_post err≤.01 15/16
  (glide200; seed 11 hops OFF 1.4 late in the hold, err .30, disclosed,
  L45b-gas class: its 2400-2900 straddle was clean .0009) and 16/16
  elsewhere. glide300 straddle .063 = the cord arrives at 1.4 slightly
  late after mid glides (f_glide_med 1.334/1.031/0.905 for G=200/300/400
  — glide-block reads dominated by the slower early ramp), re-locked by
  3000 everywhere else.
- E3 (window-locality): sign-matched where non-null (glide200 −.158/−.187,
  hyglide −.119/−.112); glide200 d_late −.261 = the L79 dwell-deepening
  signature present on the entry side too.
- E4 (misses SL-owned ≥.5): MIXED — glide300 (.556)/glide400 (.50) hold;
  glide200 .455 marginal; hyglide300 .375 fails with the BOTH-owned share
  grown (5/8): glide misses are more BILATERAL than the step lottery's
  SL-owned misses. The damage mechanism differs in kind, not just degree.
- Budget: drive-on 4800 every arm (asserted); mass ratios .988-1.002
  (chirp re-arranges the sin table only); carrier offsets 1.863/5.947/
  3.748 rad = closed-form 2π·DT·0.35(G+1) mod 2π verified (phase-
  continuous chirp; the drive is the only clock, covariant in phase reads).

Anchors: C0a/C0b twins == l59 raw BIT-IDENTICAL (mm + fL/fR/eL/eR, seeds
11/22/33, full window) — 28th consecutive chain anchor; C0T twin wpost ==
l81 stored cells EXACTLY; C0P-1 glide prefixes [0,2000) == 0.0 ×64;
C0P-2 first_div {2001: 64/64} — drive enters mech at k=2000, motor traces
diverge one hop later at 2001, the l66/l77 stored delay+1 law family
(predicted 2000 with a pre-registered {2000,2001} indexing tolerance; the
measured law is 2001 — motor-mm first-div = drive-index+1, named);
wired_dead 0; C1 green; build-time asserts (PHIT prefix exact, AMPA
all-equal, DRIVE_ON 4800, HOPA twin parity) all fired pre-rollout. Dead
scaffold (an unused step_all with undefined names) + a stray walrus caught
by read-through BEFORE launch, zero wasted rollouts. Rollouts 451 s CPU
(l83_glide.py exit 0); raw_partial per seed; raw_l83.npz checkpointed
pre-analysis. Evidence: l83/ (PREREG.md, run.out, raw_l83.npz,
raw_partial.npz, results_l83.json), l83_glide.py. No live changes.

## L84 — seg0-entry-library (tick 110, 2026-11-15)

Question: is the seg1 (fast-seg) structure draw summarized by a LOW-DIM
seg0-exit feature a controller could SET, or trace-level (re-rollable)?
Arms vary ONLY seg0 [0,2000): base (l59 hynohop verbatim) / cont
(continuous 0.7) / nod (no mech) / echo (base chop + l66 echo during seg0
only); seg1/seg2 identical everywhere; 16 census seeds; PREREG first
(l84/PREREG.md, 1 pre-run addendum). Exit features F1-F5 (SL/SR/both/
mm/cpg-core) on the seg0 tail; outcome = seg1 duty >= .25.

VERDICT: PARTIAL — no settable low-dim summary; the draw is mostly
seed-attractor identity with a partial S_L-associated tilt, and the causal
arms DISSOCIATE the best-correlated feature from the outcome.

- Arm table (seg0 duty | exit S_L | seg1 duty mean | k>=.25 Wilson):
  base .605 | .437 | .375 | 9/16 [.332,.769]  (seg1 .375 == l59 stored
  exact); cont .377 | .005 | .107 | 2/16 [.035,.36]; nod .116 | .237 |
  .168 | 4/16 [.102,.495]; echo .739 | .561 | .216 | 5/16 [.142,.556].
- CAUSAL DISSOCIATION (the finding): the echo arm LIFTS seg0 structure
  (duty .605->.739, exit S_L .437->.561 — the L66/L77/L80 lift reproduced
  on the seg0 window) yet LOWERS the seg1 draw (.375->.216, k 9->5);
  cont CRUSHES exit S_L (.005) and also draws worst (.107). Raising the
  exit summary does not buy the fast draw — consistent with L82's
  seg0-carried echo cost; exit S_L is NOT the causal carrier.
- P2 pooled univariate AUCs: both_exit .610, SL_exit .603 (E1 FAILED:
  registered >= .65 from L59 P5's single-family +.612 — the relation
  dilutes across a 4-arm library), SR .501, mm .573, f0 .516; cpg_exit
  .299 = ANTI-gradient (low CPG-core X at exit predicts the draw at
  ~.70 reversed; per-seed rho -.27, 4/16 positive) — the library's
  surprise: CPG-core recruitment at seg0 exit TAXES the fast-seg draw.
- P2 paired-within (discordant-label arm pairs, the controller read):
  SL_exit .727, both_exit .591, SR .523, mm .477, cpg .341 — SL_exit
  carries the within-seed ordering partially, but the causal arms break
  it (base-vs-echo pair discordant).
- P3 LOSO multivariate .682 < .70; P4 per-seed Spearman SL_exit rho
  .212 (11/16 positive, exactly at the registered consistency bar).
- Diagnostics: seg2 duty .455-.548 (seg0 history washes out by seg2 —
  the chop re-hosts it, L34 form); cont arm lock degrades marginally
  (le01 43/48, mean err .102 vs .001 — continuous seg0 entrainment
  leaves 5 seg1 blocks just off-frequency); budget unequal BY DESIGN
  (drive-on 3600-5600 steps; mechanism card, reported not gated).
- Anchors ALL PASS: C0a base == l59 raw BIT-IDENTICAL (mm+4 sigs, 16
  seeds — 29th consecutive chain anchor); C0x echo prefix [0,2000) ==
  l82 fb BIT-IDENTICAL (cross-run wiring probe); C0x2 first-div vs l82
  fb {2001:16}; C0P {6:16, 501:16, 1:16} == PREREG ADDENDUM 1 (4th
  L44-class instance, this time caught PRE-run from the stored one-hop
  law — the discipline held); C1/C2 green; E2 spans 13/16 exactly at
  bar; not seed-locked; var_all=2.

Consequence for the endgame: the fast-seg structure row stays
entry-state-conditional with NO settable exit summary (L80 C4c stands,
now with mechanism evidence); a learned entry controller has at most a
partial S_L tilt plus an unexploited anti-cpg lever to test. L85
(gait-reachable-mass) next. Evidence: l84/ (PREREG.md, run.out,
raw_l84.npz, raw_partial.npz, results_l84.json), l84_entry.py; CPU 287 s;
no live changes.

## L85 — gait-reachable-mass: GATE-L85 registered, training NO-GO on this library (tick 111, 2026-11-15)

Question: L6e/L6f pre-measure protocol applied to the window-scoped gait
task — what mass is REACHABLE by any policy before spending a training tick?

Method: zero new rollouts. The whole stored chain family (12 arms, census 16
seeds, noise-shared) re-derived from raw npz l59/l77/l82/l83/l84 with the
l82 metric machinery; machinery CERTIFIED against l82's own stored verdict
on the 3 shared arms (equal on every pinned read). Fork oracles = per-seed
max over noise-shared stored branches at seg boundaries (L58 form) +
branch-consistent picks + fork-time realizability (Spearman vs exit
S_L/mm). One instrument bug caught in derive: dom_freq parabola tuple
transcribed permuted (L35 swapped-unpack class; seg1 err_le01 read 0 vs
l82's 16 — the stored-json diff caught it before any pinning).

Findings: (1) constructive Pareto front = hybrid (k13, seg1 .402, no echo) /
fb (k15, .292, .127) / glide400 (k13, .368, 0) — NO arm holds k>=15 AND
seg1>=.30. (2) seg0-only echo ties the k=15 ceiling at ratio .0431 (34% of
fb's echo cost) but pays the L84 seg1 tax (.216). (3) The hop trunk
(hybrid) DOMINATES hynohop on both structure axes at equal budget — C5's
no-hop rule was coined under the retired pooled worst-seed read. (4) Oracle
gaps are big (+.11..+.22 seg1) but branch-consistent picks cap at k=14:
the union is not clearable even with seed knowledge. (5) Realizability
weak-to-anti (glide400 vs SL_exit rho -.500 ANTI) — L84's SEED-ONLY
verdict extends to glide/echo forks.

Verdict: GATE-L85 registered (G1 lock 16/16; G2a k>=15 Wilson>=.717; G3
seg1>=.358 SEPARATE window-scoped row; G4 budget caps; union demoted to
diagnostic per L58 lesson-3). TRAINING NO-GO pre-registered on this branch
library; GO requires a grown mid-seg branch library + re-measure. Next
levers seeded: L86 hybrid-trunk + seg0-only-echo combo arm (direct Pareto
mover: k15 budget tier + the hop's seg1 .402?), L87 mid-seg branch library.
Artifacts: l85/{derive.py,derived.json,PREREG.md,mass_table.py,mass_table.json}.

## L86 — hybrid-echo-combo (tick 112, 2026-11-15): E2, TAX LAW WINS — C4c closes

Question (ideas 43): L85's two best facts in ONE arm — hop trunk (k13/seg1
.402) x seg0-only echo (k15 ceiling at ratio .0431). Does the hop lift the
echo'd arm above the stored Pareto front (G2a k>=15 AND G3 seg1>=.358), or
does the L84 echo'd-seg0 entry tax outrank it?

Arms (all hybrid trunk, HOPA verbatim l59/l77; l82 machinery; census n=16
shared noise): hybrid (anchor) / hybrid_fb (anchor, echo throughout) /
hybrid_e0 (NEW: EON [0,2000) only). CPU 218 s; raw npz checkpointed
pre-analysis.

VERDICT E2 — TAX LAW WINS, and it fails BOTH structure axes:
- hybrid_e0 segs .739/.251/.505; the echo'd-seg0 tax on the hop trunk is
  -.151 paired vs hybrid (11/16 down) ~= the nohop tax -.159 (l84 .375->.216)
  = the L84 entry-carried law PORTS across trunks; echo-off-in-seg1 does not
  help (e0 vs fb seg1 -.047, 5 pos/5 neg — L82's entry-not-window finding,
  third trunk replication).
- G3 FAIL: seg1 .251 < .358. G2a FAIL: d07 k=14/16 Wilson (.640,.965) — one
  seed short (below-.5 seeds .307/.477); seg0 .739 + seg2 .505 (echo-off
  seg2 also trails no-echo .533 and fb .560: the entry tax reaches seg2).
- G1 lock PRISTINE 16/16; G4 green (ratio .0431 == the l84-pinned value to
  4 dp; budget 28.778 mass / 667.5 entrain).
- C4c (fast-seg structure row) CLOSES FOR GOOD per the card's registered
  branch: no stored arm, no combo, no entry lever reaches seg1>=.358 at
  k>=15; the remaining L87 branch class is mid-seg (inside-seg1 toggles),
  which L84's causal dissociation says is the only untested entry point.

Anchors ALL GREEN (31st consecutive chain anchor): A1 hybrid == l59 raw
BIT-IDENTICAL mm+4sigs 16 seeds; A2 hybrid_fb == l77 raw BIT-IDENTICAL;
A3 e0-vs-fb prefix [0,2000] 0.0 + first_div {2001} exact (EON-flip one-hop
law); A4 echo fd {6} both pairs (l77 stored law); A5 budget hybrid_fb
85.63/.1283 == l85 pinned; A6 CERTIFICATION — my re-derived hybrid +
hybrid_fb distributions equal l85/mass_table.json on EVERY pinned value
(seg means/k/wilson/err_le01, d07 mean/k/wilson, per-seed seg1+d07 arrays);
A7 e0 seg0 cells == fb seg0 per seed EXACT (S windows cannot see the k=2000
flip). Instrument: wilson returned as LIST for json-comparability (tuple !=
list would fake an A6 fail). Zero wasted rollouts; zero addenda needed.

Artifacts: l86/{PREREG.md, l86_combo.py, run.out, raw_l86.npz,
results_l86.json}. Research only; no live changes.

## L87 — mid-seg-branch-library (tick 113, 2026-11-15): NO-GO at the registered rule class — oracle mass grows, realizability still cannot cash it

The GO condition L85 registered (grown library + re-measured realizability before
any training tick), run at census n=16 after L86 left the gap (k14 one short,
seg1 .251). 12 arms in one shared-noise rollout: 4 trunks (hynohop, hynohop_fb,
hybrid, hybrid_fb) + 8 mid-seg1 echo latches (EON flip at K in {2500,3000,3500},
latch persists to 6000): nh_on/off x3 from the nohop trunk, hy_on2500/hy_off2500
from the hybrid trunk. Echo cell verbatim (gfb .1, delay 5, sign -); AMPA
identical (drive-on 4800 everywhere); glide variant DISCLOSED cut (realizability
measured ANTI in L85; stored glide arms still enter the oracle via mass_table
per_seed lists — the cross-run union is free).

FINDINGS
- NO single-arm Pareto mover: best new arms nh_off3500 (k14, seg1 .331),
  nh_on3500 (k13, seg1 .362 G3-pass at ratio .0534 = 42% of fb's echo cost),
  nh_off3000 (k13, seg1 .363). No arm holds k>=15 AND seg1>=.358.
- ORACLE (existence) STRONGER THAN EVER: O-MIDSEG P1 (lexicographic max d07)
  k=16/seg1 .410; P2 (max seg1 s.t. d07>=.5) k=16/seg1 .765; the 20-arm
  library adds nothing (.780). With seed knowledge the gates clear trivially —
  the mass has always been there; GO1 = PASS.
- REALIZABILITY (the load-bearing leg) FAILS at the registered class: best of
  24 median-split induced rules = nh_off2500 fork on SR2500 (k=15, Wilson
  [.717,.989], seg1 .329 < .358 — misses by .029). GO2 = FAIL => NO-GO for a
  training tick; C4b echo lever stands, C4c stays diagnostic.
- Descriptive (post-hoc, disclosed): mid-seg fork features are the STRONGEST
  realizability signal in the lineage — |rho| .735 (nh_on dd07 vs SL2500) and
  .535 (nh_on ds1 vs SR2500) vs L84's seg0-exit .30-.61 — the fork STATE is
  readable; the median-split rule class is too coarse to cash it into both
  axes at once. A 2-feature rule might; any such search must pre-register on
  these cells + replicate on FRESH census seeds (24 rules already scanned here
  — overfitting risk is real and disclosed).
- MECHANISM BONUS (L82 entry law from the positive side): nh_off3000 keeps
  seg1 .363 vs fb's .292 — echo ON through early seg1 (entry) does the seg1
  damage; dropping it after 3000 restores the draw while d07 keeps .629 (the
  k15 comes from echo-through-seg2). Echo's fast-seg tax is EARLY-SEG1-gated,
  matching L82 fb07's worse-when-off-at-2000 (entry state changed there).

ANCHORS ALL GREEN (32nd consecutive chain anchor): A1-A4 all four trunks ==
l59/l77 raw bit-identical (mm+4 sigs, 16 seeds); A5 every latch arm prefix
[0,K] 0.0 with motor first-div == K+1 EXACT ({2501,3001,3501} — the l86 A3
one-hop law, no addendum needed); A6 certification vs l85/mass_table equal on
every pinned value x 4 trunks; A7 hynohop_fb 84.8/.127 + hybrid_fb 85.6/.1283;
C1 green; zero degenerate arms; lock pristine 16/16 on every arm except
nh_off2500 (15/16, disclosed — it is excluded from the library's usable set).
Note: hybrid_fb G4 False at the strict .127 cap (.1283 stored-pinned) —
inherited, not new.

CONSEQUENCE: the oracle-only pattern has now repeated 3x (L85/L86/L87) with a
mechanism (L84: the draw is seed-attractor identity). Training on this library
is NO-GO at the registered bar; if pursued anyway, the honest opener is the
2-feature rule scan on stored cells + fresh-seed replication, never a pooled
retrain. Evidence: l87/ (PREREG.md, l87_branch.py, run.out, raw_l87.npz,
results_l87.json); no live changes.

## L88 — fresh-seed-rule-replication (tick 114, 2026-11-15): NO-GO at the 2-feature class, and the deeper find: G2a's k-bar is BATCH-FRAGILE

Split-sample execution of L87's registered follow-up. Phase 1 (stored cells
only, PREREG first): fork features recomputed from raw_l87.npz CERTIFIED
against all 24 stored single-feature rules (C0E 24/24 exact); the registered
96-rule 2-feature family (fork x pair x direction-combo x AND/OR, census-
median thresholds) yields ZERO census-clearing rules — the rank-0 rule
(hy_on2500, latch iff SL2500>=.06 AND SR2500<.7425; census k13/s1 .495)
went fresh as pre-registered confirmatory. Phase 2: both fork arms rolled
on census 16 (C0V bit-identity vs raw_l87 = 33rd consecutive chain anchor,
mm+4sigs+mA 0.0 all 16 seeds) + fresh 501-516 (never used in the chain),
rule applied ONLINE (features read at K=2500 from the in-flight base
trace; census picks == phase-1 picks exactly). C0F first-div {2501} both
batches, C0M 667.5, C1 green, zero degenerate.

VERDICT (registered): NO-GO on fresh — G1 FAIL (lock 15/16, the miss is a
BASE-trunk seed), G2a FAIL (k 8/16, Wilson [.28,.72]), G3 PASS (s1 .448 —
the fast-window axis HELD), G4 PASS (ratio .082). The 2-feature class
closes; L89 closes unopened; C4b/C4c stand; the L80 amendment is final
pending the owner.

POST-HOC decomposition (descriptive, disclosed — computed after the fresh
read, not registered): the failure is mostly the TRUNK, not the rule.
Pure-arm fresh scores: hybrid k 13->9 (lock 16->15), hy_on2500 12->10 —
the census batch was FAVORABLE for the duty_07 axis; even the 2-arm
seed-knowledge oracle reaches only k 13/16 on fresh (P1 .419 / P2 .473
seg1). G2a's k>=15 bar, calibrated on the census grid, does not transfer
across seed batches, while G3/seg1 is batch-stable (.40-.50 everywhere).
Consequence for L80's C4b: the echo-lever Wilson row (11/16 -> 15/16 on
census) must carry a batch-variance disclosure — the 4-seed margin is the
same order as the trunk-level batch swing (4 seeds). A registered
multi-batch re-base of G2a is the honest next step (queued, ideas 45).
Evidence: l88/ (PREREG.md, l88_fresh.py, run.out, raw_l88.npz,
results_l88.json, phase1_selection.json); CPU 320 s; no live changes.

## L90 — multi-batch gate re-base: G2a-multi registered, nothing clears it, C4b collapsed to pooled strength (2026-11-15, tick 115)

PREREG l90/PREREG.md pinned BEFORE any rollout (batches B0 census stored /
B1 501-516 completed / B2 601-616 / B3 701-716, arms = 4 l87 trunks,
amended form, C4b outcome criteria, anchors). Pre-run disclosure: the
ORIGINAL n=16 G2a lb clause passed at k=15 only through 3-decimal rounding
(true lb .71674 rounds to .717) — the census bar was effectively "k>=15";
the amended form pins full precision. REGISTERED FORM (replaces the census
row for all future citations): pooled Wilson lb >= .717 over the batch
union, k >= 53/64 (41/48 if a batch drops); per-batch k = diagnostics.
The "k>=15 on >=2/3 batches" alternative was rejected on power grounds
(dichotomization: a true p̂~.85-.9 lever fails it 30-60% of the time).

Results (64 seeds/arm, shared-noise machinery verbatim, CPU 859 s):
hynohop 39/64 lb .487 | hynohop_fb 51/64 .683 | hybrid 39/64 .487 |
hybrid_fb 52/64 .700 — NO arm clears; hybrid_fb misses by one seed.
Per-batch k swings exactly as L88 predicted (hybrid 13/9/7/10, nohop_fb
15/12/13/11) while seg1 means are batch-stable (.30-.44) and echo budget
is pinned (.127-.129/batch; G4 cap re-based .127 -> .129). C4b margin
re-read: COLLAPSED at the registered bar (fb .683 < .717) -> BBS #54
batch-disclosure addendum posted (marker miso:l90-batch-rebase:v1). The
reshaped claim: the echo lever's DIRECTION is batch-robust (fb > base 3/4
and 4/4 batches, pooled +12/+13 seeds, delta means +.024..+.127) — base
p̂ .61 [.49,.72] vs fb .80 [.68,.88] / .81 [.70,.89] — but the census
15/16 (.94) was batch-inflated. Cite the pooled effect, never 15/16.
Secondary: hy_on2500 (L88's winner rule) n=32 descriptive k 22/32 lb
.514 — also far below the bar.

Anchors ALL GREEN: C0A 34th consecutive chain bit-identity (4 trunks x
census 11/22/33 == raw_l87, mm+4 sigs 0.0), C0B my cells machinery on
stored raw_l87 == results_l87.json distributions EXACT (metric
certification), C0D hybrid-B1 bit-identical to raw_l88 AND cells equal
(cross-run noise-stream law held: one generator per seed, arm count
cannot perturb the stream), C0E fd(fb vs base)==6 on every new seed
(l66/l77 one-hop law doubles as anti-degenerate), C1 green. Lock: 16/16
most arm-batches, four 15/16 cells disclosed (incl. L88's known hybrid
B1 miss). Evidence: l90/ (PREREG.md, l90_multibatch.py, l90_verdict.py,
run.out, verdict.out, raw_l90.npz, results_l90.json); no live changes.

## L91 — banc-endgame-rebase: female cord says the OPPOSITE of male on batch-robustness (11-15, tick 116)

L90's multibatch protocol ported to the female BANC cord (l78 substrate
verbatim, G .14/BETA 2/D .2, ENT_AMP .1, Ti primary pair per stored l68
geometry): 3 fresh batches x 16 + 3 anchor seeds, 5 arms shared-noise
(fn / fn_fb / fh / fh_fb / fsham donor-sham transport control), CPU 598 s.

FINDINGS. (1) The card's question answers OPPOSITE to male: fn duty_07(Ti)
= 48/48, pooled lb .9259 — G2a-multi CLEARS at BASE; the female Ti structure
is batch-ROBUST where the male Tr base collapsed to p-hat .61 (39/64,
lb .487). Batch-fragility is GRAPH+PAIR-specific, not a protocol property.
(2) Tr at base is 0/48 with a PER-SIDE structural split (duty07_L .16-.17
dead vs R .95-.98) — the female Tr failure is a one-sided wiring fact, not a
lottery; the male-style both-sides duty cell can never read it. (3) The
literal echo cell: Ti tax -.203 (L78's healthy-pair tax replicated at
n=48), Tr lift +.288 with SHAM SHARE 73.2% (l78's 96% at n=3 lands at 73%
at n=48 — perturbation, not content, CONFIRMED at scale); fb Tr 15/48
lb .1995 fails G2a-multi; on Ti base already clears => echo lever MOOT on
the female cord at this bar. Budget .2511 = 2x male .127. G1p rhythm 48/48
all arms. (4) HOP ARMS DEAD-CHANNEL (ADDENDUM 1): fh bit-identical to fn
on every seed, fh_fb == fn_fb exactly; mechanism measured — the subnet's DN
membership rule (receives cord input) EXCLUDES the 2 pure-descending DNge046
command cells (they project to cord, 16/5 out-edges, but receive none), and
the 1 kept DNge046 is relu-floor buried behind a single inhibitory cord
in-edge (amp .5 < |u|; DNg100 contrast: 400+ cord out-edges vs 16). The male
hybrid-trunk mechanism has NO female port on this subnet at any registered
amp — a substrate fact. Female endgame with hops needs the DN closure rule
amended (keep DNs by cord OUTPUT too), its own re-anchored run.

ANCHORS. C0A fn == l68 hyb01 bit-identical 0.0; C0A2 fn_fb == l78 fbn_g01
bit-identical 0.0; C0A3 fsham == l78 sham_g01 bit-identical 0.0 (free
anchor: one generator per seed, arm count cannot perturb the stream —
cross-run noise-stream law again); C0P-echo fd xm==5/mm==6 every seed;
C2 landed (fn_fb, fsham all seeds); duplicate-proof fh/fh_fb max 0.0 all
51 seeds; C1 green; C0B certification EXACT vs results_l78.json on 3 shared
arms x 6 reads (l78's own 300-step form). E1/E1b band misses at +/- .003
(anchor traces bit-identical; the .94-1.0/.04-.20 bands were derived from
l68's 300-step form, read here with the male 500-step form — machinery-band
miss, disclosed). L44 instance #5 caught by pin assert: n=32 k_min is 28
(l90 stored assert), not 27 from memory. Budget-form bug caught post-verdict
(divided by sin_mean, not ENT_AMP*sin_mean) — fixed, recomputed from stored
npz, zero reruns; C0B did not cover budget (noted). Evidence: banc/l91/
(PREREG.md, ADDENDUM.md, l91_run.py, l91_verdict.py, l91_hopdiag.py,
out/, raw_l91.npz, results_l91.json); no live changes; sessions/ untouched.

## L92 — banc-dn-closure-subnet: the rule fix works — female hop vocabulary EXISTS, and the closure is not silent (11-15, tick 117)

QUESTION (ideas 47): the l65 subnet's DN rule (keep DNs that RECEIVE cord
input) deleted pure-descending command cells (L91 dead-channel). Build the
closure-amended subnet (keep = cord | dn_into | dn_projecting), re-derive the
op point, and census whether a female hop vocabulary exists.

SUBSTRATE (static, pinned pre-run in l92/static.json — derived BEFORE any
rollout, L44 rule): n 21,249 -> 21,809 (+560 DNn; dn_proj 1,287), edges
627,051 -> 647,953 (+20,902). Blocks: cord->cord 560,236 / cord->DNi 5,322 /
DNi->cord 53,329 / DNi->DNi 8,164 (the old 627,051 EXACTLY) + NEW
DNn->cord 14,279 / DNi->DNn 2,189 / DNn->DNi 3,047 / DNn->DNn 1,387; and
cord->DNn == 0 BY CONSTRUCTION (the closure cannot create cord input into
the added cells — the L91 burial path via cord inhibition structurally
cannot apply to them). C0S: old edge set EXACT SUBSET of new (global-id key
join), values bit-identical on all shared pairs — the closure is purely
additive. Pools/mech/motor/DNg100 EXACT unchanged.

RESULTS. (1) OP POINT: bisect gain on the closure net to l91's stored af
(0.109056, mean of stored afv_{11,22,33}) -> g* 0.153125 vs 0.14 (+9.4%),
af 0.10820 within 1e-3 — prediction X-1 (g rises; sub-threshold DNn mass
dilutes af) CONFIRMED. (2) THE VOCABULARY EXISTS: of 1,288 DN cells (728
DNi + 560 DNn), 442+442 are VIABLE (L36 two-sided: u_max>0, X_mean<.95);
883 viable cells carry cord out-edges (441 DNi / 442 DNn) — the l65 rule had
deleted HALF the command surface; 26 DNn cells reach antagonist pools
DIRECTLY (top: DNg72 4, DNg79 3, DNge043/034/069 2 each) vs 117 DNi. DNn
command mass is weaker (out_w med 27 vs 105) but the population is real.
(3) THE PORT IS FIXED: DNge046 3/3 cells in-subnet and ALL viable (u_max
1.46/0.72/1.27; X_mean .199/.057/.562) — the previously-buried DNi cell is
u_max>0 at the new gain too (L36 law: census pins are op-point-qualified).
Volley on the two DNn DNge046 cells: LANDS 3/3 seeds at amp .5 AND 2.0
(dm .026-.041; L91's dead channel is repaired by the rule fix alone).
(4) E1 fd law: fd_mm 2001-2006 >= 2001 bound PASS; mechanism — the DNn
DNge046 cells DO carry direct MOTOR edges (2 and 1; non-antagonist MNs), so
the registered "expect > 2001, no direct motor edges" prediction was WRONG
in an informative way: direct-motor reach exists, antagonist POOLS are
still reached only through the interior. Per-pool max|d| at amp .5: Ti_eR
.477, Ti_eL .308, Ti_fL .193 — the pools move a LOT (prediction X-4 'weakly'
REFUTED in magnitude) while the dose .5->2.0 is non-monotone across seeds
(dm s22 .038->.030) — the volley RE-ROLLS rather than grades (L38 attractor-
selection signature). (5) SUBSTRATE LAW — THE CLOSURE IS NOT SILENT: at
matched gain and bit-matched old-cell noise (two-generator scheme: gen draws
ONLY old-shaped tensors in l91's exact order), the closure edges alone move
pool traces max|d| 0.615 (mm-only 0.081) — MORE than the pure-gain arm
(oldref@g_new vs stored l91 fn@g_old: 0.499). The l65 subnet's base regime
was not merely missing command cells; completing the DN->cord closure
materialially changes the dynamics the endgame was calibrated on. L93 lever
scans must run on the CLOSURE substrate, not l65.

INSTRUMENT LESSONS. (a) pandas 3.1: bool Series + bool Series is now
ELEMENTWISE OR (bool dtype), not int — the `(a+b)>1` AND-idiom silently
returns all-False; use explicit & (cross-tab vs vocab-line contradiction
caught it; zero rollouts wasted). (b) My C0S v1/v2 compared sorted key
arrays as a PREFIX across different index spaces — sorted arrays INTERLEAVE;
subset must be np.isin + dict-join on values, in GLOBAL id space. (c) The
per-seed af consistency assert compared one seed against the 3-seed bisect
MEAN — assert the aggregate after the loop, not inside it.

ANCHORS. C0S static (asserted at run start); C1 True (af band + |mean-af
target| 8.6e-4 <= 2e-3); bisect consistency mean af_c == af_final exact;
C0A branch gain-decomp disclosed (g_new != 0.14; max|d| 0.4995 = the
gain-decomposition read); C0C 0.6154/0.0806 (closure footprint, first of
its kind, no band pinned); C2 lands 3/3 both amps; E1 fd_min 2001 >= 2001;
E2 census table + DNge046 trio u/X explicit. PREREG l92/PREREG.md BEFORE
any rollout (static derivation first, all numbers pinned). Evidence:
banc/l92/ (PREREG.md, static.json, dn_census.csv, dn_census_dyn.csv,
l92_static.py, l92_run.py, l92_verdict.py, run.out, raw_l92.npz,
anchors_run.json, results_l92.json); CPU 31 s run + 3 s static; no live
changes; sessions/ untouched.

## L93 — female-own-lever-scan: Tr-L is neither absent nor buried — it is an attractor draw no tested volley hosts (11-15, tick 118)

CARD: Tr duty07_L dead vs R alive — pathway absence, buried drive, or
lands-but-no-structure? PREREG l93/PREREG.md FIRST (static derivation +
base pin from STORED l92 cfn before any rollout; ADDENDUM 1 disclosed
pre-verdict). Substrate = L92 closure (g* 0.153125), arms = 3 buried DN
joint-L reachers (amp 2.0), intr16 Tr-L premotor set (amp .5/2.0), Ti-L
donor, 2 random-DN + 2 random-intrinsic shams; volley seg0 [0,2000);
paired-noise shared per step; seeds 11/22/33 (mechanism census, n=3
disclosed — any CONTENT verdict would require multibatch replication).

FINDINGS (layered):
1. STATIC: absence REFUTED — 61 DN cells carry direct Tr_fL edges; Tr pools
   are 84-88% INTRINSIC-driven (premotor sheet owns the pool); intr16 (top-16
   both-pool EXCITATORY premotor, incl. INXXX466/IN19B003 = male CPG-family
   kin) clears the 2% conduction floor at its entry hop (Tr_fL .0364 /
   Tr_eL .0203). Every top DN joint-L reacher is relu-floor BURIED (u_max
   -.019..-2.353) — DNg105-R/DNxl080-L/DNg74_b-R.
2. DELIVERY: not the bottleneck — EVERY arm incl. all 4 shams moves both Tr
   pools (dm .15-.26). Buried cells deliver once amp clears |u_max| (d74b at
   2.0 vs 1.763) with fd = the X un-pin rise-time (441/1098/97 steps — the
   ADDENDUM-1 law; fast cells fd 1-35). P1 PASS: intr16_20 dm >= every DN arm
   (delivery follows conduction share — the one content layer).
3. STRUCTURE: PERTURBATION everywhere — candidate lifts (intr16_20
   -.05/-.01/-.07; DN arms ~0) indistinguishable from shams, and the table's
   BIGGEST Tr-L lift is a RANDOM intrinsic sham (shamint_20a +.44/+.18/+.07);
   nothing persists into seg2 (post-release lottery, L47). E3 no-harm
   breaches are CLASS-WIDE (shams breach lock/TiL as hard as candidates,
   df0 to +-.44 both signs) = the tonic-volley-hops-the-attractor signature
   (L38 class), not candidate harm.
VERDICT: Tr-L deadness is neither pathway absence (static) nor burial
(delivery lands) — the side's antagonist antiphase is an attractor-draw
property of the regime; pool-reaching tonic volleys, selected or random,
re-roll it. No female-own lever exists in this drive vocabulary; the L91
side-split stands as the wiring-level explanation. Closure-substrate base
pin DISCLOSED: duty07_L {.057,.047,.037} / duty07_R {.557,.460,.257} — the
closure substrate is deader on BOTH sides than l65's .16/.95 (L92 substrate
law; all reads paired vs THIS base).

ANCHORS: C0 base == l92 cfn BIT-IDENTICAL 0.0 (mm+xm+8 pools x 3 seeds —
36th consecutive chain anchor); C1 af-equal across arms + vs l92 stored
exact; base duty pin re-derived from l92 npz and ASSERTED equal pre-read;
raw_l93.npz checkpointed before analysis; verdict re-derived from npz
(results_l93.json). INSTRUMENT: 3 pre-launch catches (pandas groupby
key-form; .loc column-name collision; global-vs-local index bug in the
intrinsic sham pool + a dead scaffold) — zero wasted rollouts; heredoc-with-&
gateway block replaced by a .py file. Artifacts l93/. No live changes.

## L94 — female-closure-rebase (tick 119, 2026-11-16)

CARD: L91 multibatch protocol (5 trunk arms, 3 fresh batches x 16, G2a-multi
pooled Wilson form) re-run on the L92 CLOSURE substrate (n 21,809 / edges
647,953 / g* 0.153125; two-generator noise law). Q1: does female Ti
batch-robustness survive the closure? Q2: does the Tr side-split persist or
re-draw? Arms cfn/cfn_fb/csham/cfh/cfh_fb; hop = ALL 3 in-subnet DNge046
[270,302,366] amp .5 VW 40 at transitions (first LIVE trunk port); batches
B4 801-816 / B5 901-916 / B6 1001-1016; donors l68 hyb01 cyclic (l91 form).

FINDINGS (results_l94.json):
1. Ti base COLLAPSES: 0/48 pooled (lb 0.0; l65 measured 48/48 lb .9259 on
   the SAME protocol, same metric code, C0B-certified). Per-side closure
   L .35-.38 / R .43-.49 — both sides mid-band, the AND-cell never crosses
   .5. The l65 extraction rule (dropping projecting DNs) was LOAD-BEARING
   FOR the robustness itself: female-cord batch-robustness is a SUBNET-RULE
   property, not a cord property. The endgame contract must now cite the
   closure substrate (L92 law) — and on it NO pair has robust base
   structure.
2. Tr side-split PERSISTS: L .032/.051/.056 vs R .372/.421/.451 per batch
   (split >= .32, sign-consistent 3/3; E2 PASS). R is off the l65 ceiling
   (.95-.98 -> .37-.45) — the split's ORDERING is robust to the substrate
   change, its magnitude is not.
3. Echo lever NULL on closure: fb-vs-cfn lift Ti -.007 / Tr -.006 (l65:
   Ti -.203 tax / Tr +.288 lift); no positive lift to decompose, sham share
   undefined. The l65 Tr lift was itself a substrate property. DISCLOSED
   budget asymmetry: closure ANTAG mean .0192 vs l68 donor .1274 = 6.6x —
   the donor-sham injects 6.6x the fb arm's own echo mass (both arms null,
   so the E3 read stands; the asymmetry would matter for any future
   positive-lift read on this substrate).
4. Hop trunk port lands female-side for the first time (dm .023-.046 all 51
   seeds, fd_mm {2001,2002} in the l92 band; cfh_fb-vs-cfn_fb same law) but
   is NOT a structure lever: duty deltas Ti L +.03 / R +.025, Tr R +.046 /
   L -.006, k 1/48 (Ti) 0/48 (Tr) — perturbation class, consistent with
   L93's verdict.
5. Lock G1p 48/48 every arm; seg1 duties ~0 (structure dead in the fast seg
   too on closure); echo budget .037 (l65 .2511 — the ANTAG pools run 6.6x
   cooler here, same ratio as the disclosure above).

ANCHORS: C0A cfn == l93 base BIT-IDENTICAL 0.0 (mm+xm+8 pools x 3 seeds —
37th consecutive chain anchor); C0B metric certification PASS (this
verdict's cells/budget code on stored raw_l91.npz == results_l91.json every
pinned read: 3 arms x 2 pairs x per-batch k/wilson/5 means + pooled rows +
anchors + budget .2511); C0P-1 echo law {xm 5, mm 6} all 51 seeds; C0P-2
hop fd {2001,2002} in-band BOTH forms (vs cfn and vs cfn_fb); C2 all arms
dm > 0 (channel live); C1 af .104-.112 equal across arms; anchor pins EXACT
(pre-derived from stored l93 raw, l94/prederive_anchor.json). INSTRUMENT:
2 pre-launch catches (dead Io scaffold line; mech_o used-in-settle but
never defined — NameError at step 1) — zero wasted rollouts; pre-derivation
key-collision bug (dict keyed by side only, Tr overwrote Ti) caught by the
identical-Ti/Tr smell test before pinning. CPU 519 s rollouts + 90 s
verdict. Artifacts l94/. No live changes.

CONSEQUENCE: L91's "female Ti batch-robust" claim is now scoped to the l65
subnet; the closure substrate (the honest one per L92) has NO robust base
pair. Endgame contract numbers (L80 amendment's C4 rows) were all measured
on l65/male — a closure-side rebase note goes to the next digest; no BBS
milestone change claimed (research-only card).

## L95. fd-burial-probe (tick 120, 2026-11-16)

QUESTION (instrument card): generalize L93's ADDENDUM-1 law into a cheap
burial instrument — predict a volley's pool first-divergence fd from static
+ one base probe, replacing the 3-seed u-census when screening drive
candidates.

VERDICT: the CROSSING LAW is EXACT, and it sharpens the census itself.
fd(earliest pool = motor-sheet mean, every case) = k_open + 1 + eps with
eps in {0,1} on 40/40 cells (10 fresh d74b amp-sweep cells eps 0 EXACT;
30 stored l93 arm-seed cells: 27 eps 0, 3 eps 1 — shamdn_a's first opening
is marginal by a hair, one extra float32-visibility accumulation step).
k_open = first k with u_base(k) + amp + BG > 0 from the SAME-noise-stream
base trace. Mechanism confirmed at the cell: dX(d74b) bit-exactly 0.0
until k_open-1, first nonzero AT k_open (0.001-0.016), pool +1 (L77/L83
one-hop law). Pin law verified as an inequality per cell: never diverges
iff max_k u(k) + amp + BG <= 0 (internally consistent on every arm-seed).

FINDINGS beyond the registered gates:
1. Burial depth is SEED-DEPENDENT: d74b seg0 u_max = -1.951/-1.501/-1.896
   (seeds 11/22/33; census scalar -1.763). P3's registered "amp 1.5 pinned
   3/3" FAILED on seed 22 — it opens at k=1103, fd = 1104 = k_open+1 exact.
   The census u_max is a cross-seed BOUND with +-0.25 seed spread: never
   classify marginal amps with it; the one-probe u(k) trace on the SAME
   noise stream is exact. (This is the L35/L36 burial-census lesson
   sharpened to a measured spread.)
2. Registered P4 rank read (fd_Tr_fL) rho .529 = dilution by pool-specific
   visibility lag (Tr_fL lags 0-34 steps for already-open cells); ADDENDUM 1
   re-read on fd (earliest pool) from stored raw_l93 pool traces: |eps|<=1
   everywhere, Spearman .798 — tie-degenerate (27/30 predictions are the
   SAME value 1; a rank gate cannot certify exactness on a near-constant
   prediction; the L55 degenerate class in reverse). The error table is the
   claim-carrier, not rho.
3. P1 monotone PASS 3/3 seeds (440->1->1, 1098->99->1, 97->80->1 for amps
   2.0/3.0/5.0); amp 1.8 marginal exactly as the per-seed traces predict
   (2 seeds pinned h<0, seed 22 opens at 1100).
4. F2 naive hyperbola (card's original guess) rho .719 descriptive —
   carries signal but cannot classify pin at all; F0 crossing law is the
   instrument.

INSTRUMENT SPEC (the deliverable): screening drive candidates needs ONE
base-arm rollout on the target noise stream passively recording u(k) for
candidate cells during the drive window (zero volley arms, zero extra
rollouts; the l95 probe with 5 validation arms ran 37 s CPU). Then per amp:
pinned (max u + amp + BG <= 0), k_open, fd at direct-target pools =
k_open+1(+1). Table l95/fd_headroom.csv; law + verdict l95/results_l95.json
(incl. addendum1 rows).

ANCHORS: C0A/C0B d74b_2.0 + base arms == raw_l93 BIT-IDENTICAL max|d| 0.0
mm+xm+8 pools x 3 seeds (38th consecutive chain anchor, same noise stream);
C0E metric certification 120/120 c2 reads reproduced EXACTLY from stored
npz before any new read; af assert == l93 stored per seed. PREREG FIRST
(l95/PREREG.md); P3/P4 registered-gate failures journaled with diagnosis,
amendment labeled ADDENDUM 1. INSTRUMENT: 3 parse bugs caught by
error/NoneType pre-analysis (tuple-unpack in certification loop,
underscore-containing arm names) — zero wasted rollouts. CPU 37 s probe +
3 s law. Artifacts l95/. No live changes.

CONSEQUENCE: any future volley/drvie-screening card (female or male) uses
the one-probe fd law instead of the 3-seed u-census; census u_max demoted
to a cross-seed bound, never a per-seed classifier at marginal amps.

## L96. live-pet-first-week — field notes (2026-11-16 03:1x, tick 121)

Sources (copy-never-mutate; sessions/ untouched): lane/l96/world_snapshot_1116.json
(NOW, copied 03:12), peabrain-lab/l72/world_copy.json (11-14 16:2x), LANE-LOG
recorded probes 11-08..11-16 (labeled log-derived), live read-only GETs
/needs?chat=world + /diary (<lan-ip>:3122) during this tick. No live changes.

EVIDENCE TABLE (what the week actually shows):
- Hoard (L10): 2 (11-10 11:40, log) -> 52 (11-14 16:2x, archive) -> 68 (11-16
  03:12) = 11.9/day then 11.0/day — a STABLE shiny economy at 12% roll; implies
  ~92-99 forage finds/day, consistent with the archive's single-day day_log
  (77 'water' events by 16:00; 77 x .12 = 9.2 expected shinies that day).
- Day class (L72 organic, extended): every observed day_log is 100% 'water'
  (forage finds; 77/77 on 11-14, len 0 pre-dawn 11-16). KIND_EVENTS includes
  water+slug -> EVERY night's consolidation writes (the L73 dop-key failure
  mode never triggers on her real days; the live key is safe by ecology).
- Consolidation (L3): night_stamp monotone-advancing on every observed
  snapshot (11-13 in archive, 11-15 now); day_log consumed same-night; exact
  pass-count since 11-09 is NOT recoverable from stored data (see GAP 1).
- Dreams (L4): both observed nights hit the MAX_DREAMS=3 cap with
  dream_pool ['water'] — content = day's single class, every night, then the
  cap binds. L72's lab twin (day-vs-dream separable within class) stands.
- Trust/synapse trajectory: .127 (11-09, log) -> synapse .614 (11-14 AM, log)
  -> pinned 1.0 display+synapse+axes (11-15 and 11-16, snapshots). L74's
  m4-display-pin prediction verified LIVE at ~5 days / ~95 kind events/day.
- Curiosity walks (L5): archive diary window (11-14 afternoon): dabble 30 /
  forage_pond 10 / investigate 10 (6 goats, 2 boot, 2 fence) — investigates
  cluster in low-drives lulls exactly as designed (ladder misses fear/sleep/
  hunger first). NOW: curiosity 6.5e-9 (spent+decayed), curious_at to_fence.
- Overnight state (live-verified 03:12): hunger 1.0 + sleep 1.0 + fear 0 +
  mood hungry:high + intent beg + cx move 0.0/arousal .041.

FINDINGS (mechanics read off the code + snapshots, not new experiments):
1. NIGHT TRAP (welfare finding for the owner): world_tick's ladder tests sleep>.75
   BEFORE hunger>.7, so a sleeping duck never forages; hunger rises all night
   with no relief. needs() reads hunger FIRST, so the UI shows intent 'beg'
   with a maxed hunger bar while she sleeps — for most of every night. Dawn
   (sleep<.75) starts forage relief. Suggested fix (owner call, not shipped):
   order needs() ambient sleep-first when sleep>.9, or let sleeping hunger
   cap at 0.85, or add a 'sleep-beg' ambient. Pinned-delta proposal material.
2. DIARY IS NIGHT-BLIND (observability gap): diary entries carry NO
   timestamps ('t' is a random tie-break), cap 50, and nest entries append
   every 45 s tick while asleep -> by ~37 min into night the ENTIRE diary is
   naps; every /diary read overnight (and any morning read before dawn
   activity) shows 50 identical nest lines. Day acts (forage/investigate/
   parade/consolidate/dream) roll off within the first hour of night. /diary
   served now = 50 x nest, verified live. This also erased all week-scale
   diary evidence (GAP 1). Proposal: stamp entries with clock_s (or iso
   time), skip diary-append for repeated nest acts (coalesce), and keep an
   append-only diary archive file — small pinned delta, owner call.
3. DREAM CAP BINDS NIGHTLY: 3/3 dreams both observed nights; pool always the
   day's single class. With one-class days the dream theater is 3x the same
   water dream — fine, but any future dream-diversity work starts at
   MAX_DREAMS and the selection key, both already lab-measured (L73).
4. ECONOMY SELF-CONSISTENT: hoard rate x roll probability x day_log count
   agree within noise (11-12 shinies/day, ~.12 roll, ~77-95 finds/day) —
   the L10/L5 world parameters behave as shipped, no drift over a week.
5. SATURATION REGIME REACHED: display/synapse trust pinned 1.0 since ~11-15;
   from here the world session's relationship channels are invisible to
   visitors at the DISPLAY level (L74 live confirmation) — substrate-side
   reads (plas norm) remain the only informative ones, lab-only.

GAPS (honest): exact consolidation-pass count, dream texts, and any diary
text history before 11-14 16:2x are unrecoverable (cap + no timestamps);
pre-11-14 quantitative state exists only as LANE-LOG sentences. The two
proposals above (needs order/coalesce + diary stamping/archive) would make
the second week measurable; both are pinned-delta-sized, parked for the owner
alongside L6-deploy / L75 hybrid key / L80 amendment.

Verified: snapshots diffed programmatically (json loads, both files); live
/needs 200 with the exact overnight state quoted; /diary 200 window=50 nest
entries counted; both units active throughout; sessions/ never written.

## L98. pet-archive-watcher — read-only longitudinal archive (2026-11-16 05:5x, tick 123)

Week-2 pet evidence was unrecoverable (L96: diary/day_log caps 50/100 roll
entries off; entries carry no timestamps). Shipped the interim, no-owner-call
observability: every lane tick now snapshots the world session + live /needs
into peabrain/lane/archive/ (sessions/ strictly read-only), and an offline
merger reconstructs week-scale history.

- Machinery: lane/archive_tick.py (snapshot + manifest.jsonl append; wrapped
  so it can never block a tick) + lane/archive_merge.py (union with
  first_seen/last_seen bounds per unique entry, nest coalescing by text,
  consolidation nights from night_stamp, night-trap exposure = share of
  [22:00,06:00) snapshots showing intent 'beg'). Protocol pre-step added to
  LANE.md ground rules (hourly cadence via the existing lane engines — no
  new cron).
- Verified live: snap_20261116_055647 + snap_20261116_055723 (36 s apart);
  snapshots DIFFER (sleep axis 0.9002 -> 0.8986 = a world tick fired between
  them); merger: 2 snapshots, diary union 1 unique act (nest n=100 = both
  capped 50-windows coalesced), consolidation nights ['2026-11-15'],
  night-trap exposure 2/2 share 1.0 (hungry:high + intent beg + hunger 1.0 +
  sleep ~0.90 at 05:56-05:57 — the L99 night-trap state is now archived
  evidence, not a one-off screenshot).
- Owner-call cards parked untouched: L99 night-trap fix, L100 diary
  night-vision (BBS #54 checked 05:55: only Mai's 2800 receipt, no owner
  reply — the parked queue stands).
- No live changes; sessions/ never written; both units active throughout.

## L101 — closure-pool-vocabulary scan (tick 124, 2026-11-16)

Question: L94's "closure substrate has NO robust base pair" was measured on
exactly 2 pairs (Ti, Tr). Property of the whole semantic antagonist
vocabulary, or of tibia/trochanter?

- Pairs (semantic tokens in BANC peripheral_target_type, closure subnet,
  eligibility >= 3 in-subnet cells per side pool — ALL 5 eligible):
  Ti 50/51/6/6, Tr 31/31/24/24, Ta (tarsus depr/lev) 12/12/3/3,
  Sr (sternal ant/post rotator) 6/6/11/13, Pr (tergopleural promotor /
  pleural remotor+abductor) 4/4/3/3. Unpaired-by-semantics disclosed, not
  scanned: long_tendon 47, femur_reductor 34 (+ head/wing/abdomen muscles).
- Run: cfn BASE arm only, seeds = l94's exact 51 (ANCHOR+B4+B5+B6), l94
  machinery verbatim; raw_l101.npz checkpointed pre-analysis (l101/).
- Anchors: C0A BIT-IDENTICAL to raw_l94.npz — mm+xm all 51 seeds AND Ti/Tr
  8 pools x 6 cert seeds, max|d| 0.0 (39th consecutive chain anchor);
  C1 af == l94 stored exact all 51; C0B metric certification PASS (my
  generalized cells/table code on raw_l94 reproduces results_l94.json cfn
  Ti/Tr reads EXACTLY incl. per-batch 7 keys, pooled 5, anchor pins,
  lock_g1p 48); lock 48/48 on L101's own traces.
- VERDICT: NO pair in the vocabulary clears G2a-multi (both-sides duty_07
  cell, pooled Wilson lb >= .717): all five 0/48, lb 0.0, zero NaN seeds.
  L94's no-robust-base claim is now VOCABULARY-WIDE: the honest closure
  substrate is structure-dead as a base for every joint. l65's Ti 48/48
  remains the only robust pairing on the female cord — the extraction
  rule (L94) stays the load-bearing ingredient.
- NEW descriptive finding — side-splits are JOINT-HETEROGENEOUS:
  Ti R>L (L .35-.38 / R .43-.49, kR 22/48), Tr R>>L (0 vs 13/48),
  Ta INVERTED L>>R (kL 7/48, kR 0 — opposite of Ti/Tr), Sr R>L (kR 10/48),
  Pr dead both. One-sided antagonist structure scatters across joints
  with NO consistent laterality (3 patterns across 5 joints); no side
  cell clears the bar anywhere (max lbL .117 / lbR .326). seg1 fast-window
  ~0 everywhere (batch-stable axis dead too, matches L94).
- Limits: base arm only (echo/hop lever reads stay L94's); small pools
  3-13 cells carry the small-pool caveat; rate fidelity, 0.7-1.4-0.7
  protocol only; long_tendon/femur_reductor unscanned (no semantic
  antagonist token — pairing them needs anatomy, not strings).
- No live changes. Evidence: l101/{static.json, PREREG.md, raw_l101.npz,
  results_l101.json, run.out}.

## L102. brain-state-intent-dataset (tick 125, 2026-11-16)

Owner-rule endgame, step 1 (learned locomotion from her own populations —
read-only archive growth, no live changes, no owner call needed).

- **What shipped:** archive_tick.py now also copies sessions/world.pt
  into lane/archive/brain/ (brain_YYYYMMDD_HHMMSS.pt) on every tick,
  READ-ONLY (sessions/ never written; hash-verified copy with one retry
  because the live .pt save is not atomic — an unstable mid-save source
  is skipped, never fatal). Byte-identical brains dedupe onto the
  previous archive file (last.json). Bounded: MAX_BRAIN_COUNT 336
  (~2 weeks hourly) AND 420 MiB hard byte cap, oldest-first prune,
  brain/ scope only. Each snap json + manifest line pairs the brain
  descriptor (file/sha/size/dedup) with the /needs intent+mood captured
  in the SAME snapshot — that pairing IS the dataset record.
- **Loader:** lane/archive/load_brain_states.py — dataset report
  (n pairs, n-with-intent, unique brains, intent distribution, MB,
  missing-file warning exit 1); `--load` torch-loads samples:
  X (139255,) + plas_d (115728,) verified on real captures.
- **Offline:** lane/test_l102_archive.py 13/13 (missing-source None,
  descriptor/last.json, dedupe-no-new-file, changed-source new file,
  prune count cap oldest-first + scope guard + last.json kept + byte
  cap, unstable-skip removes partial). Two expectation bugs in the TEST
  were caught by the assertions themselves (same-filename reuse at
  fixed ts — benign live, distinct-second names in prod; byte-cap math
  forgot the 2 KiB real files) — the code was correct both times.
- **Live-verified:** 2 captures 84 s apart (brain shas differ — the
  45 s world tick drifts X as expected), intent paired both times
  ('stay', happy:low), manifest lines carry brain descriptors,
  dataset = 2 pairs / 2.0 MB at 08:17. Cadence ≈ 24 pairs/day → the
  week-scale card (~170 pairs) is on schedule.
- **Limits:** intent distribution today is bridge-ladder output (the
  CX-population decode is the future card — this dataset is its
  training table); hourly cron + any /loop engine both snapshot (both
  capped); plas_d shape (115728,) recorded for the future probe.

## L103 — unpaired-pool closure census (long_tendon + femur_reductor)
[tick 127, 2026-11-16 10:31-11:0x | banc/l103/ | PREREG l103/PREREG.md]

**Question.** L101 scanned 5 semantic antagonist pairs; the two
unpaired-by-semantics motor pools (long_tendon 47, femur_reductor 34,
disclosed there) were the vocabulary's last unscanned members. Does
either hold a batch-robust structure cell on the closure substrate at
base?

**Registered definitional port (before rollouts).** Antagonism is
semantically undefined for these pools → the registered antagonist
surrogate is the CONTRALATERAL HOMOLOGUE: S_LR = -corr(pool_L, pool_R)
on 5-s rolling windows; duty_07 / .25 / .5-clear / G2a-multi pooled
Wilson (k >= 53-41 form, k_min 41/48 asserted) all l101-verbatim.
Per-side cells = ALIVE duty (0.7-window trace >= .05, the af threshold),
diagnostic. FlyHack secondary (tick-126 amendment): phase-shift null
(circular 5-s shift of R, computed ALWAYS, verdict-carrier only on a
primary clear) + sustain_frac beside every k/n cell; never-fires branch
registered (L55 lesson).

**Static (pinned pre-rollout).** LT_L 23 / LT_R 24, FR_L 17 / FR_R 17;
totals == L101's disclosed 47/34 exactly; both eligible (>= 3/side).

**Results.** BOTH POOLS FAIL: LT k [0,0,0] pooled 0/48 lb 0.0, FR 0/48
lb 0.0, sustain 0.0, NaN 0, lock 48/48. FlyHack secondary (descriptive,
never-fires branch): real duty ~.094/.098 vs shift-500 null .144/.102
(margin -.050/-.004; extra shifts {100,300,700,900} bracket it) — the
raw LR anticorrelation carries NO content above the null, the verdict is
two-sided clean. Descriptive NEW: both unpaired pools are L-modulated /
R-SILENT at base — 0.7-window means LT_L .0349 (max .168) vs LT_R .0012
(max .046); FR_L .0312 (max .274) vs FR_R .0046 (max .055): the R side
never crosses the .05 line in any sampled seed. Adds two L-leaning
entries to L101's joint-heterogeneous laterality scatter (activity-axis,
not structure-axis — disclosed).

**Verdict.** MOTOR VOCABULARY COMPLETE under the registered LR cell: no
robust base anywhere on the closure substrate but l65's Ti (extraction
rule load-bearing, L94); closure endgame stays closed as a base
substrate. Caveat carried in claim wording: the unpaired cell is a
definitional port (contralateral-homologue anticorrelation), not the
paired-pool antagonist cell.

**Verification.** C0A PASS max 0.0 — mm+xm all 51 seeds + Ti_aL/Ti_bR
pool traces (anchor seeds) + af exact vs raw_l101.npz (40th consecutive
chain bit-identity, noise-stream law); C0B PASS — l101-verbatim cells
code on raw_l101.npz reproduces results_l101.json EXACTLY (5 pairs x
per-batch 8 reads + pooled + side + nan + lock 48); C1 PASS (af in
band, == l101 stored, all 51). PREREG first; raw_l103.npz checkpointed
before analysis; resume-safe. Instrument notes: f-string line-continuation
SyntaxError caught by lint pre-run; levels-probe boolean-mask length bug
(551 vs 6000) caught by traceback, zero impact on pinned reads; gateway
blocks inline heredocs containing `&` — small .py files (known lesson).

## L105 — closure free-run scan (does zero drive self-order the closure cord?)

**Intent.** L94/L101/L103's "no robust base" verdicts were all measured
UNDER the chopped entrainment trunk (+ tonic DNg100). The one unread cell
of the substrate matrix: does the L92 closure substrate self-order
antagonist structure at ZERO sinusoidal drive? The l65 EXTRACTION
substrate did (stored ladder_real_S .7196, Ti, arm B). Arms: cfn (l101
verbatim, cert) / free (no sinusoid anywhere) / freenod (no sinusoid,
D=0 — L35 D-law probe); 51 seeds, generators re-seeded per arm so all
arms share the per-seed noise stream; pools 5 pairs x 4 sides + LT/FR x
2 (l103 tokens) + Ti cert pools. PREREG l105/PREREG.md first; P1
never-fires branch registered; FlyHack secondary unconditional.

**Results.** P1 (expected, clean negative): NO free-run self-ordering —
all 5 pairs k [0,0,0], pooled 0/48 lb 0.0 (duty07 means .00-.14); LT/FR
LR cells 0/48. The l65 extraction rule owned the self-ordering, not the
cord: L94's substrate law now covers zero drive. RHYTHM WITHOUT
STRUCTURE: lock 48/48 on the free arm (dom_ratio >= 10 all 3 windows,
every seed) — the cord's intrinsic rhythm persists with zero drive while
antagonist structure is absent everywhere. P4 joint-heterogeneous drive
response: removing drive RAISES Sr structure (+.058, 37up/10dn =
drive-toxic for sternal rotator) while LOWERING Ti (-.047, 17up/30dn =
drive-helped); Tr/Ta/Pr ~0 — per-joint sign flips, same
joint-heterogeneity family as L101's laterality. P2: freenod-vs-free
max|d| 0.033 (bit-identical seeds 11/33, differs on 22): tonic DNg100 is
MARGINALLY live on closure — L35's male D-inert law is seed-qualified
here, not a clean port. P3 (never-fires branch, tie-broken best cell
pair:Tr at p_hat 0.0): margin -.05 negative — two-sided clean. LT LR
margin +.061 (real .142 vs shift .081) is a descriptive curiosity only
(k 0/48, never fires).

**Verdict.** The honest closure substrate has no antagonist structure at
base, under drive, or at zero drive, anywhere in the motor vocabulary —
the extraction rule (keep cord + DN-into) was load-bearing for the l65
self-ordering itself, not just its batch-robustness. Substrate matrix
closed.

**Verification.** C0A PASS max 0.0 — cfn arm bit-identical to BOTH
raw_l101.npz (mm+xm 51 seeds + Ti/Tr 4 pools x 6 cert seeds + af exact)
AND raw_l103.npz (LT/FR x 51 seeds + Ti_aL/Ti_bR x 3) = 41st consecutive
chain bit-identity; C1 PASS; C0D free!=cfn PASS (drive wiring live);
C0B PASS — generalized cells/table code reproduces results_l101.json
(5 pairs x per-batch 8 + pooled + side + nan + lock) AND results_l103
.json (LT/FR pooled k + flyhack real/shift means) EXACTLY; Wilson bar
assert (41/48) held. l105_run.py exit 0 CPU 567 s; raw_l105.npz
checkpointed before analysis; resume-safe. Instrument note: C0B caught
MY OWN cert-code transcription (nan_seed_count read at pooled/side level
instead of table level) — certification-before-pin worked as designed,
zero wasted rollouts.

## L106 — laterality scatter figure (the publish view of the L94-L105 arc)

**Question.** One honest figure for the vocabulary-scan arc: the per-side
(L vs R) structure scatter the pooled both-sides gates cannot see, with
the L105 zero-drive overlay.

**Protocol.** banc/l106/l106_data.py: metric copies verbatim from
l105_verdict.py (itself C0B-certified in tick 128); CERTIFICATION FIRST
(L85 rule) — reproduce results_l101.json (5 pairs x per-batch duty07L/R
means), results_l103.json (LT/FR alive spreadL/R), results_l105.json
(free-arm 5 pairs x per-batch duty07 means) EXACTLY before any figure
value is pinned. New reads with the certified machinery: free-arm
PER-SIDE duty07/alive07 (the stored l105 tables are pooled-only) and
cfn pooled side means + batch min/max. 48 seeds (B4/B5/B6), TS step 10,
S>=.25 side cells, alive>=.05, rounding order identical to the source
verdicts.

**Certification result.** PASS — 30 l101 + 4 l103 lists + 15 l105 reads
EXACT. First run failed ONLY the l105 block: my probe averaged (L+R)/2
where the stored cell is the AND-form (L07 & R07) — wrong cell form,
not a machinery bug; fixed, l101/l103 certs never wavered.

**Figure (banc/l106/l106_laterality.png, 960x560 one-dark).** Panel A:
5 antagonist pairs, x=RIGHT duty, y=LEFT duty, diagonal y=x symmetric
reference; filled warm = entrainment-trunk base, open cool = zero-drive
free-run, dotted connector = same pool across arms, whiskers = batch
min/max. Panel B: LT/FR on the ACTIVITY axis (alive>=.05, hi=.6), axis
difference disclosed in-figure.

**Reads (figure_data.json, all certified-machinery).** cfn: Ti L .370 /
R .466; Tr .046/.414; Ta .364/.007; Sr .143/.391; Pr .018/.094;
LT .247/.004; FR .209/.001. free: Ti .479/.371; Tr .080/.153;
Ta .086/.006; Sr .282/.470; Pr .019/.076; LT .064/.010; FR .029/.000.
=> sidedness SURVIVES zero drive on Tr (R>L), Ta (L>>R), Sr (R>L),
LT/FR (L-only), Pr stays dead; magnitudes shrink everywhere; **Ti is
the exception — dominant side FLIPS R->L at zero drive** (connector
crosses the symmetric diagonal in-figure; attractor re-roll class L38).
Laterality is a per-joint attractor property, not a wiring constant.

**Verification.** Vision QA pass 1 found 4 label-collision defects
(panel-B origin cluster, panel-A Ti/Ta/Pr crowding, tag-on-axis) — all
fixed (per-pool offsets, shared label for coincident Pr/FR markers,
shorter Ti tag); pass 2 verified every fix, found 1 new defect (footer
clip at right edge) — fixed by splitting the caption; final re-check
ANALYTIC after 3 vision timeouts (disclosed): pixel-level ImageMagick
edge scan — right-edge strips of all 4 text bands + full outer border
max |dBG| = 0, PASS. Figure + digest pushed (commit e2cefb3a,
ls-remote-verified; raw-read grep=1, fig HTTP 200). No live changes;
sessions/ untouched.

## L100 — diary night vision (clock_s stamps + nest coalescing + archive)

**Decision.** Owner call 11-16 ~11:40 EST ("yay, B, yay!", third item;
BBS #54 `miso:owner-calls-1116:v1`): APPROVED as instrumentation only.
L96's evidence: the 50-cap filled with identical nest lines within ~37 min
of dusk, entries carried no timestamps (t = random tie-break), week-scale
diary evidence unrecoverable.

**Mechanism.** One module-level `bridge.diary_append(s, act, text, t)`
replaces all four append sites (consolidate / dream / world action /
parade): every entry stamped `clock_s` + `clock_s_end` (int epoch s) and
`n` (run count); identical consecutive (act, text) within 900 s coalesce
into one counted entry; entries evicted by the 50-cap are appended to
`sessions/world_diary_archive.jsonl` before dropping (append-only).
ZERO new rng draws — callers pass the t they already drew, because draw
order IS behavior (the world ladder shares that stream). Old-format
entries never coalesce (first deploy caught the default-window fallback
merging a legacy entry — partial stamps; fixed by requiring a stamped
tail, gate 7).

**Verification.** test_l100.py 17/17 (stamps; coalesce + window + aged
tail; ordered append-only archive growth; json round-trip; unwritable
archive resilience; distinct dreams never merge; old tail never merges).
No-behavior-change: 40-tick seeded world_tick baseline pre vs post —
acts/hoard/curiosity/entry-counts/texts BIT-IDENTICAL; the t draws differ
between ANY two runs including same-code controls (unseeded global
stream, pre-existing), draw count identical (605=605). Deployed via the
cron-safe kill-literal-PID + start path: /health 200, gate_live 25/25,
/diary serving stamped entries with true wall-clock times (14:24-14:26
EST), and the archive file receiving evicted old-format entries LIVE as
new stamps push them off the cap. Pinned delta + tests + provenance:
`peabrain/lane/deltas/l100_diary_night_vision/`. The L98 archive
pre-step is RETAINED (L104 brain-pair capture depends on it; only its
diary-substitute role is superseded). L99 (deep-hunger wake, same owner
call, option b) remains open as a separate delta.

## L107 — extraction-rule-decomposition (tick 132, 2026-11-16)

Question: WHICH ingredient of the l65 extraction rule owns the Ti 48/48
self-ordering that closure killed (L94)? Static + ONE bisection slice,
B4 16 seeds, l94 machinery verbatim, PREREG first (l107/PREREG.md).

Static (claim-carrier, l107/static.json): closure = l65 + 560 dn_new,
purely additive; NO l65-kept class is dropped — the card's "largest
l65-only class re-added" form does not exist; slice AMENDED to
subtraction. Added edges 20,902 = dnnew->old 17,326 (out) + dnnew->dnnew
1,387 + old->dnnew 2,189. Target tiers of the out-mass (28,583.9):
intrinsic 89.8% (12,991 edges / 25,669.9), motor_other 9.1%, the 8
antagonist pools 129 edges / 271.3 (~0.2-2% of pool in-mass) — DIRECT
pool bombardment RULED OUT; the added DNs project onto the premotor
interior. Top-77 cells (13.8%) carry 50.24% of cord out-mass.

Dynamic (arms full/b65/h65/cut, shared noise, C0A bit-identical):
- full == stored l94 cfn max|d| 0.0 (42nd consecutive chain anchor),
  k_Ti 0/16 (stored 0) — replication anchor green.
- b65 (l65 @ .14): k_Ti 16/16, duty07 .993 (L 1.000 / R .993) — l65
  robustness REPLICATES under l94 machinery; the Tr side-split also
  replicates exactly (L .150 / R .961 vs l91's .16/.95-.98).
- h65 (l65 @ .153125, +9.4% gain): k 16/16, duty07 .925 — THE GAIN IS
  INNOCENT; the op-point story is dead.
- cut (closure minus top-77, g_cut .145108 bisected): k 0/16 both-sides
  — NOT the top-77 alone. REGISTERED READ: distributed membership.
- NEW descriptive the both-sides cell hides (L46 lesson): the membership
  ladder is SIDE-HETEROGENEOUS and non-monotone per side — Ti_L
  1.000 (l65) -> .836 (cut) -> .378 (closure): removing the heavy 77
  partially RESTORES the left; Ti_R .993 -> .143 -> .425: the same
  removal collapses the right FURTHER. Shifted-window (+250 steps)
  secondary confirms all reads grid-stable (cut L .844; b65 .992;
  h65 .918; cfn .128). n=16 single batch — per-side law needs the
  multi-batch rebase (L109) before it's citable.

Anchors/gates: C0A bit-identity 0.0 (16 seeds x 10 keys); C0B cert PASS
(my B4 cells on stored raw_l94 cfn == results_l94.json B4 fields EXACT,
Ti+Tr); C1 af ranges green, b65 band [.1051,.1131] green (.109196);
ADDENDUM 1: bisect landed af_final .108534 vs target .109056 (gap
5.22e-4 ~ 11 cells) — target sits INSIDE a discrete-cell staircase
jump; g_cut = closest attainable below; l92's own bisect was +1.0e-4
off the same target. Lock 16/16 every arm; zero NaN.

Verdict: the extraction rule's load-bearing ingredient is the DN
MEMBERSHIP (not the op point), carried DISTRIBUTED by the small-per-cell
intrinsic-projecting bulk with SIDE-SPECIFIC action — the l65 rule's
robust Ti pair is a property of what the extraction LEFT OUT.
Artifacts: l107/ (static.json, PREREG.md, raw_l107.npz,
results_l107.json, addendum_shift.json). No live changes.

## L108 — free-rhythm-descriptor (tick 133, 2026-11-16)

Pure analysis of stored raw_l105.npz (zero rollouts). PREREG first
(l108/PREREG.md + ADDENDUM 1 registered before the full-table compute).
Certification (L85) PASSED pre-pin: this script's lock machinery reproduced
free 48 / freenod 48 (raw_l105) and cfn 48 (raw_l101, certified same traces)
EXACTLY.

**Verdict: the closure substrate's zero-drive "rhythm without structure"
(L105 lock 48/48 free) is a SLOW, BROAD motor-mass oscillation — an order
slower than the male antagonist band, and NOT displaced by entrainment.**

- Registered read (band .3-10 Hz, lock machinery verbatim): free full
  argmax .339±.038 Hz — but 12/51 seeds pinned AT the .3 band floor
  (validity threat quantified, disclosed): the band truncates the true
  dominant component. DIAG-A (0.02-10 Hz): free global peak MEDIAN .217 Hz,
  IQR [.150, .267] (period ~3.7-6.7 s), ratio median 22,166x median power
  = a real spectral line in EVERY seed, not trend (detrend probe moved
  nothing). Seed-spread: broad band, not a discrete attractor (male cord
  was {0.80, 1.44, 1.42}); within-seed stationarity only 20/51 (wanders).
- Driven arm carries the SAME slow family UNDER the drive lines: cfn global
  peak median .15 Hz IQR [.10, .25]; DIAG-B drive-line SNR 51/51 seeds >=10x
  in EVERY segment (medians 1,924-2,817x) — the 0.7/1.4 lines are always
  present and strong; they are simply not always the ABSOLUTE max (seg1
  1.4-line dominates globally in 38/51; seg0 argmax at drive in only 15/51 —
  the slow line usually out-powers 0.7). Entrainment COEXISTS with the slow
  attractor; no relocation. Same-family answer: free .217 and cfn-under-drive
  .15 Hz are one slow family; the drive line is additive on top (L23
  superposition regime, not attractor capture).
- E3: freenod == free in 38/51 identical-freq seeds, max full-freq diff
  .067 Hz, mm_mean identical (.0619) — tonic DNg100 (D=.2) does not move
  the rhythm family (P2 marginal result confirmed on the frequency axis).
- L105 reinterpretation (scoped): the free-arm "spectral lock" the chop
  protocol measured IS this slow line (or its in-band shoulder); lock as a
  RATIO gate stays valid (cert 48/48/48), but any future freq-LOCATION claim
  on this substrate must read the untruncated spectrum — inherited bands are
  ratio instruments, not location instruments.

Artifacts: l108/{PREREG.md, results_l108.json}, l108_freq.py. No rollouts,
no live changes.

## L109 — per-side-membership-ladder-rebase (tick 134, 2026-11-16)

Question (L107 follow-up, L88/L90 rule): is the per-side membership ladder
(cut restores Ti_L .378->.836 while collapsing Ti_R .425->.143 on B4) a LAW
or a single-batch draw?

Card amendment (L44 instance #6): card said "fresh B5 901-916 / B6
1001-1016" but l94's stored meta shows those WERE l94's batches — fresh
sample re-defined as B7 1101-1116 + B8 1201-1216 (verified absent from
raw_l94.npz and raw_l107.npz before launch).

Design: 4 arms (full/b65/h65/cut) x 32 fresh seeds, l107 machinery
VERBATIM; anchors 801+901 run first; g_cut re-bisected deterministically.

Anchors ALL GREEN: C0A PASS max 0.0e+00 (full_801/901 == l94 cfn bit-
identical; b65/h65/cut_801 == raw_l107 bit-identical; g_cut == stored
0.14510760426521305 EXACT); C0B certification PASS (my side_k cells on
raw_l107 == results_l107.json means, l107 per-seed rounding path matched);
PREREG k-side pins PASS (full L3/R5, b65 16/16, h65 16/16, cut L16/R0);
C1 PASS (af ranges, b65 band .109193).

RESULT — the ladder is a LAW on every structure axis, at ceiling margins:
- cut  L: 32/32 (B7 16/16, B8 16/16; means .836/.870 vs B4 .836)
- cut  R: 0/32 (0/16 + 0/16; means .154/.174 vs B4 .143)
- b65: 32/32 BOTH sides; h65: 32/32 BOTH sides (robustness replicates a
  4th+5th time; Wilson lb .893 everywhere)
- P2 ladder order holds: cutL>fullL, b65R>cutR, cutR<fullR (all True).
- P1 formally DRAW: ONE of five conditions missed — the full-arm DEAD-BASE
  bar (k_R <= 11) came in at 12/32, one seed over; full_L passed (5/32).
  P3: full_R is the ONLY batch-drawn axis (all 7 others batch-stable on
  both batches individually). The miss is a marginal base-arm negativity
  bar, not a structure condition — disclosed, not rounded up to "law".
- Zero-rollout extra: l94's stored B5+B6 cfn (901-1016) full-arm per-side
  cells = L 7/32 (m .367) / R 17/32 (m .486) — across 4 base batches the
  closure base stays L<R-leaning but noisy (.31-.53 p-hat R), consistent
  with l94's no-robust-base verdict while per-side R occasionally rises.

Verdict: side-specific DN-membership action on the closure substrate is
BATCH-ROBUST (cut asymmetry 32/32 vs 0/32 — the strongest replication
margins in the lineage); per-side reads are now the required form for any
future substrate edit. The closure BASE's R-side level is the one
batch-drawn quantity — cite it as a distribution, never a point.

Method lesson (L55/L88 family): a 5-condition AND gate with equal weights
let the LEAST important cell (a base-arm dead-bar) formally void the
primary claim while every structure condition held at 32/32 with lb .893
vs .000 separation. Register structure conditions as PRIMARY and base-bar
conditions as SECONDARY/descriptive, or weight them — an unweighted AND
makes the substantive claim hostage to the noisiest cell.

Artifacts: l109/{PREREG.md, anchors_run.json, results_l109.json,
run.out}, l109_run.py, l109_verdict.py, raw_l109.npz. No live changes;
sessions/ untouched.

## L110 — heavy-vs-light intrinsic-target profile diff (tick 135, 2026-11-16)

Question (L107/L109 follow-up, static, ZERO rollouts): do the removed 77
heavy dn_new projectors differ from the kept 483 light in intrinsic-target
PROFILE (sign mix, side-of-target, cell types) in a way that predicts the
side-specific action (cut restores Ti_L 32/32, keeps Ti_R dead 0/32)?

PREREG l110/PREREG.md first (pins from l107/static.json + results_l109.json).
C0 PASS pre-read: all extraction pins EXACT incl. K 77 / mass_share .5024;
C0B per-pool direct edges+mass EXACT (8 pools x 2 fields) — the plumbing
certification my new reads ride on. Instrument catches pre-verdict: stored
cut.families is TOP-12 TRUNCATED (subset-compare, L44 #7); gi-vs-row mask
indexing; np.repeat on the 2-hop join offsets. Zero wasted rollouts.

REGISTERED VERDICT — P1 FAILS, honestly: signed 2-hop side-asymmetry does
NOT separate heavy from light vs the 77-of-560 subset null at |z|>=2
(z_heavy +1.33, z_light -1.13; null sd .63 — the dn_new pool's own signed
asymmetry is that noisy). P2 direction matches (dA +1.56 names R, the side
cut fails to restore) but rides the failed P1 -> directional only.
R3: target-side placement is SYMMETRIC (heavy -0.033 vs subset null
-0.023+/-0.080; side-permutation z -1.83) — side-specificity is NOT in
which-side-targets (L24-consistent).

POST-HOC ADDENDUM (registered pre-rerun, gates nothing — the follow-up
lead list):
- A1: heavy is GLUTAMATE-ENRICHED 19/77 vs hypergeom 6.05+/-2.19, z +5.9
  (3.1x; ACh z -1.95, gaba null). 1-hop negative-mass frac 0.42 vs 0.29.
- Per-pool signed 2-hop MIRROR (descriptive): heavy -> Ti_fL +1821 (4.6x
  light's +394) / Ti_fR -389 (net INHIBITORY); light -> Ti_fR +1961.
  Heavy carries a LEFT-flexor-excitatory profile, light the RIGHT-flexor
  one — directionally coherent with the double dissociation under an
  attractor-bias reading (L38 class), NOT certified as a prediction.
- A2 family table (Ti_fL/Ti_fR signed): DNg79 +503/+344, DNbe002 +287/+243,
  DNg43 +283/+177 bilateral-excitatory; DNpe006 +354/-206 L-mirror;
  DNpe045 +109/-449, DNp69 +24/-399 R-inhibitory; DNge103 -263/-202,
  DNg72, DNge120, DNb07 bilateral-inhibitory; DNge025 -17/+436 R-only.
- A3: heavy Ti_fL excitation CONCENTRATED: top-5 cells 70.8%, 41/77 positive.

Verdict for the queue: static profile does NOT clear the prediction bar —
the side-specific membership action stays placement/attractor-dynamic, not
profile-static; the addendum names the cells/families for a targeted
volley/silence card if we ever want the mechanism video.

Artifacts: l110/results_l110.json + types_l110.json (40 intrinsic types,
z vs subset null) + PREREG.md; l110_profile.py; run 2x CPU ~2.5 min each.
No live changes.

## L111 — glutamate-subset ladder (closure − 19 glutamatergic heavy; 11-16, tick 137)

Question: is the closure's side-specific Ti kill TRANSMITTER-carried (the 19
glutamatergic cells of the heavy-77, l110 addendum z +5.9) or MASS/PLACEMENT-
carried? Arms = l107/l109 machinery VERBATIM (full / b65 / cut) + NEW cut19 =
closure minus exactly those 19; h65 dropped (settled 32/32 twice). Seeds:
anchors 801+901 vs raw_l109 + FRESH B9 1301-1316 (verified absent pre-launch).
g_cut reproduced stored EXACT; g_cut19 bisected fresh (.150968, af .109026,
staircase |d| 3.06e-05 disclosed). PREREG l111/PREREG.md first.

VERDICT: the two side actions DECOMPOSE.
- Ti_L (P1): cut19 kL 14/16, meanL .663 — kL clears the transmitter arm
  (>=12) but meanL misses .70 by .037 => registered verdict MIXED, never
  rounded up. The glut-19 carry 57% of the L-restore ((.663-.407)/(.853-.407))
  from 22% of the heavy cord out-mass (.1103 of .5024; P5 disclosure beside
  the table, duty-form cells only per tick-136 amendment). Majority
  transmitter-carried + a residual mass/placement component.
- Ti_R (P2): cut19 kR 0/16, meanR .045 — DEEPER than cut-77's own .121.
  The R-kill rides the glut-19 essentially ALONE (the 58 non-glut heavy
  contribute nothing to it). Tr secondary agrees (cut19 Tr R 1/16 .201 vs
  cut 3/16 .350; b65 Tr R 16/16 .977 = the l65 side-split replicates).
- So: 22% of removed mass carries >=100% of the R-kill + 57% of the
  L-restore — per-mass, the transmitter subset is the action carrier on BOTH
  sides, but the L-restore is not complete without the 58.

Anchors ALL GREEN: C0A full/b65/cut vs raw_l109 on 801+901 BIT-IDENTICAL
max 0.0e+00 (adding cut19 added zero RNG draws — 43rd consecutive chain
anchor); C0B certification PASS vs results_l109 pooled + per-batch after
matching l109's pooled rounding path EXACTLY (mean of ROUNDED per-batch
means; a grand-mean-over-32 cert differs in the 3rd decimal on two h65
cells — the known L109 cert class, caught by the cert itself, zero wasted
rollouts); P3 ladder replicates on B9 (cut kL 16/16, b65 16/16 both sides);
P4 af all green.

DISCLOSED: single fresh batch n=16 (the card's ONE slice); the tight call
is meanL .663 vs the .70 bar (k-cell fresh-batch swing is the known L88/L90
axis) — the mirror slice (cut58) + optional second batch are the follow-up
cards (ideas 57). h65 certified on stored data only.

Artifacts: l111/{PREREG.md, run.out, anchors_run.json, raw_l111.npz,
verdict.out, results_l111.json}; l111_run.py (asserted exact-string
transform of l109_run.py, l111_build.py), l111_verdict.py. CPU 213 s.
No live changes.

## L113 — cut58 mirror slice: the side actions are SUBSET-REDUNDANT (2026-11-17)

Question (ideas 57): mirror of L111 — remove the 58 NON-glutamatergic
heavy (keep the 19 glut in; .3921 removed vs .1103 kept) and read the
per-side Ti duty cells. Registered arms (l113/PREREG.md BEFORE any
rollout): full/b65/cut/cut19 identical (cut19 retained as L114's second
batch; zero new RNG draws), cut58 NEW, g bisected fresh .154173
(staircase 3.65e-06 disclosed); anchors 801+901 vs raw_l111; FRESH B10
1401-1416 verified absent from raw_l94/l107/l109/l111 pre-launch.

VERDICT — both registered outcomes fired at once, and their conjunction
is the finding: P1 MASS/PLACEMENT (cut58 Ti_L kL 16/16 meanL .790 ==
cut-77's own .809 on B10): the 58 ALONE restore L fully. P2
R-KILLED-BY-58 (cut58 Ti_R kR 0/16 meanR .207 vs full-B10 kR 9/16
meanR .505; registered revision arm): the 58 ALONE kill R too. So
EITHER half of the heavy-77 alone produces the FULL cut phenotype
(L restored, R dead): the closure's side-specific action is
SUBSET-REDUNDANT — a mass/threshold attractor flip, not a
transmitter-parcelled channel. This REVISES L111's "the R-kill rides
the glut-19 essentially alone" (that read compared cut19 vs cut — both
already dead; the mirror shows the 58 carry the same action
independently). Consistent with L107 R3 (placement/attractor-dynamic,
not profile-static) and L93 (perturbation-not-content). Tr secondary
DISSENTS on R: cut58 Tr_R kR 5/16 meanR .472 ~= full 4/16 .401 (Tr R
survives removing the 58; Tr_L dead in every arm) — the laterality
stays joint-heterogeneous per L101.

L114 rebase (registered as P6 pre-run; pooled B9+B10 n=32): kL 29/32
Wilson lb .7578 (k-cell rock-solid at 2 batches) but meanL32 .680
misses .70 by .020 -> MIXED PERSISTS honestly; L111's verdict stands.

Anchors ALL GREEN: C0A full/b65/cut/cut19 vs raw_l111 on 801+901
BIT-IDENTICAL max 0.0e+00 (44th consecutive chain anchor) + g_cut AND
g_cut19 deterministic re-bisects == stored EXACT (new C0A(c19) anchor);
C0B certification PASS (my cell machinery on stored raw_l111 ==
results_l111.json Ti+Tr tables, every pinned read); P3 ladder
replicates on B10; P4 af green, b65 band green. Instrument: the P0
print's all(p0.values()) swept in the c0a_max 0.0 diagnostic and read
FAIL with every gate True (L59 anchor-key class, in miniature) — fixed
pre-report, zero wasted rollouts (pure-analysis rerun).

Artifacts: l113/{PREREG.md, run.out, anchors_run.json, raw_l113.npz,
results_l113.json, verdict output in terminal}; l113_run.py (asserted
exact-string transform of l111_run.py, l113_build.py), l113_verdict.py.
CPU 315 s (5 arms x 18 seeds). No live changes.

## L115 — random-19-subset flip control (tick 139, 2026-11-17)

Question: is L113's subset-redundant cut phenotype (either transmitter
half alone restores L AND kills R) a pure mass/threshold flip, or does
WHICH-19 matter? Decisive control: 3 random 19-of-heavy-77 cuts.

Result: aggregate P1 = MIXED honestly, but the DECOMPOSED read is the
claim — the two axes SPLIT. L-RESTORE IS MASS-LIKE: 2 of 3 random draws
restore Ti_L at/near real-subset level (cutR2 kL 15/16 .793 ~= cut's
own .825; cutR3 13/16 .640; cutR1 10/16 .525 = the one NO-FLIP), from
removed mass .106-.131 (glut-19's own is .1103) — no random draw fails
L in the closure band on 2/3 draws. R-KILL IS SUBSET-SPECIFIC: ZERO of
3 random draws kill Ti_R (kR 3/13/10, meanR .329/.629/.563 vs 0/16 for
BOTH true partition halves cut19 .043 and cut58 .207-B10; paired leg
TRUE for R2/R3 — R survives at full-like levels). The R-kill needs a
COHERENT transmitter-class half removed, not any 19 cells; mass does
not explain it (lowest-mass draw R1 .1063 has the MOST R-kill, highest
R3 .1311 keeps R 10/16). Descriptive covariate n=3: glut-count gradient
8/7/3 -> kR 3/13/10 (cutR1, 8 of the 19 glut cells, kills R most) —
consistent with glut-fraction tracking R-kill, though cut58 (0 glut,
R dead 0/16) breaks monotonicity: partition COHERENCE, not glut count,
is the surviving story. Verdict: L = mass/threshold attractor flip;
R = class-coherence-sensitive. L113's "either half alone" refined: any
~19-58 cells flip L; only whole-class halves kill R.

Also: cutR3 needed g .181913 — highest gain in the lineage (subnet
stiffness read, ADDENDUM 1 bracket [.12,.32], attempt 1 aborted IN
BISECT zero rollouts). P6 diagnostic: pooled cut19 3-batch n=48 =
kL 43/48 lb .778, meanL48 .700 EXACTLY ON the .70 bar (3-dp rounding;
L114's MIXED closed at n=32 stands, batch swing disclosed, L88/L109
class).

Verified: PREREG l115/PREREG.md + ADDENDUM 1 registered pre-rerun; C0B
certification PASS (my cell machinery on stored raw_l113 == results_l113
Ti+Tr B10 tables every pinned read, BEFORE any L115 pin); P0 anchors ALL
GREEN — full/b65/cut/cut19 vs raw_l113 on 801+901 BIT-IDENTICAL max
0.0e+00 (45th consecutive chain anchor) + g_cut AND g_cut19
re-bisects == stored EXACT; P3 ladder sanity on B11 PASS (cut 16/16
.825, b65 16/16 both, cut19 14/16 .740); P4 af green all 7 arms, b65
band green. raw_l115.npz checkpointed pre-analysis. 1 instrument catch
(noise-dict pattern count 2 -> 3: settle + rollout-settle + rollout-WIN)
at build time, zero wasted rollouts.

Artifacts: l115/{PREREG.md, run.out, run.err, anchors_run.json,
raw_l115.npz, results_l115.json}; l115_run.py (asserted exact-string
transform of l113_run.py, l115_build.py), l115_verdict.py. CPU 529 s
attempt 2 (7 arms x 18 seeds + 5 bisects). No live changes.

## L116 — flip-joint-scan: the cut58 flip is NOT Ti-specific (Sr is a
second Ti-like flip; Tr spared; Ta anti-flip) + b65's first 5-pair table

Design: l113 machinery VERBATIM (all 5 arms, graphs, gains, draw order,
seeds 801/901 + l113's own B10 1401-1416) — a replication-form EXTENSION
readout of the SAME trajectories with the pool set extended to the 5
semantic pairs (Ta/Sr/Pr new in l101 a/b naming; Ti/Tr keep f/e names so
C0A keys match). Disclosed: B10 is l113's batch, NOT an independent draw;
Ti/Tr columns are the anchor, the Ta/Sr/Pr columns are the new data.

Anchors ALL GREEN before any read: C0A FULL-BATCH — every l113-schema key
(mm, xm, 8 Ti/Tr pools, af) over ALL 18 seeds x 5 arms == raw_l113.npz
EXACT, max|d| 0.0e+00 (46th consecutive chain anchor, first full-batch
one); NEW C0A(c58) class — g_cut58 re-bisected == l113 stored
.15417299151420596 EXACT; g_cut/g_cut19 == stored EXACT; C0B PASS (the
pair-generalized verdict machinery reproduces results_l113.json Ti+Tr
tables on ALL 5 arms every pinned read) + metric-level identity of the
l116 npz against the same pins; C1 af green all arms, b65 band green.

Findings (5-pair x 5-arm per-side duty table, B10 n=16):

1. NOT Ti-SPECIFIC: Sr flips Ti-like under cut58 — dL +.668 (L .165 kL
   6/16 -> .833 15/16), dR -.392 (R .449 6/16 -> .057 0/16). Under cut
   (-77) Sr is "L-restore with R-SPARED" instead — the two removal arms
   dissociate on Sr_R.
2. Tr IS SPARED: no side moves under cut or cut58 (Tr_R stays 4-5/16
   .40-.48 through every arm except cut19 .279 1/16 — Tr_R dies hardest
   under glut-19 removal, the OPPOSITE direction from Sr/Ti).
3. L-RESTORE IS MASS-LIKE ACROSS THE VOCABULARY (extends L115 beyond
   Ti): Sr_L restores with removed mass .471 (cut19, .1103 removed) <
   .629 (cut, .5024) ~ .833 (cut58, .3921); Ti_L same shape .696 <
   .809 ~ .790.
4. Ta IS ANTI-FLIP: its dominant side Ta_L SUPPRESSES with heavy-DN
   removal (.357 -> .182 cut -> .138 cut58; b65 kills it .071) — the
   added-heavy DNs CARRY Ta_L structure. Ta_R dead everywhere (<= .08).
5. Sr_R subset-paradox (disclosed, lottery-class reading): dies under
   EITHER half-removal (cut19 .101 / cut58 .057) yet re-draws marginal
   under full cut (.486 7/16) — a MARGINAL side (base 6/16 .449)
   re-running the attractor lottery per perturbation, never a robust
   structure; same caveat class as L56/L115 covariate n=3. L117's dose
   ladder should watch Sr_R alongside Ti_R.
6. Pr floor everywhere (max mean .265, mostly 0) — registered
   expected-floor, no-signal artifact, never specificity evidence.
7. BONUS (b65's first 5-pair table, free from the retained reference
   arm): the l65 substrate is bilateral-robust ONLY on Ti (16/16 both
   sides); Tr is R-only-robust (16/16 R, 0/16 L), Sr is L-only-robust
   (16/16 L, 0/16 R), Ta + Pr dead — the extraction rule's robustness is
   itself joint-heterogeneous per side, the l65-side twin of L101's cfn
   finding.

Verdict: L116 answers the card — the cut58 flip pattern is
JOINT-HETEROGENEOUS (Ti + Sr flip, Tr spared, Ta inverted-suppressed, Pr
floor); no single-joint story survives, and the L-restore mass-law
(L115) generalizes across pairs while the R axis stays
pair-idiosyncratic.

Verified: PREREG l116/PREREG.md registered BEFORE any rollout (bands +
base expectations from stored l101 51-seed distribution); l116_run.py =
asserted exact-string transform of l113_run.py (l116_build.py, all 10
patterns clean); run exit 0 CPU 326 s; l116_verdict.py exit 0. Artifacts:
l116/{PREREG.md, run.out, run.err, anchors_run.json, raw_l116.npz,
results_l116.json}. No live changes.

## L117 — glut-dose-ladder: the R-kill is a STEP at k<=5 (heaviest-glut subset), not a fraction curve, not class coherence; Sr_R is a confirmed lottery

Card (ideas 59): remove k of the 19 glutamatergic heavy cells for k in
{5,10,15} (deterministic heaviest-first ladder, dose=count primary, mass
disclosed), fresh B12 1601-1616, watch Ti_R dose shape + Sr_R (L116
amendment). Registered hypotheses: FRACTION (monotone kR fall) vs
COHERENCE (R full-like until the whole class is gone).

Design: l116 machinery VERBATIM (5-pair pools, graphs, gains, draw
order); arms full/b65/cut/cut19/cut58 retained as anchors + cutk5/cutk10/
cutk15 = closure minus the k HEAVIEST glut heavy (heav is mass-desc;
positional filter, zero RNG; static pins l117/static.json: masses
.0425/.0723/.0952 of new-cell mass = 38.5/65.5/86.3% of the glut-19's
.1103; n 21804/21799/21794; edges pinned; drops strict subsets of
cut19_drop; DNg100 not in heavy-77 re-asserted).

Results (B12, n=16):
- Ti_R DOSE CURVE: full .473 (7/16) -> k5 .023 (0/16, paired dR -.450,
  14/16 down) -> k10 .104 (0/16) -> k15 .074 (0/16) -> k19 .018 (0/16).
  The R-kill fires COMPLETE at k=5 — removing only the 5 heaviest glut
  cells (4.25% of new-cell mass) kills Ti_R outright. BOTH registered
  hypotheses REJECTED: not FRACTION (no gradual response; dead at the
  first dose, m5<m10 floor blip non-monotone) and not COHERENCE (does
  not wait for class completeness). The R-kill is carried by a SPECIFIC
  SMALL SUBSET — the heaviest glutamatergic cells. Cleanest mass-rejection
  yet: k=5 at mass .0425 kills R while L115's random-19 draws at mass
  .106-.131 did NOT (kR 3/13/10; random draws rarely contain the top-5
  glut) — mass cannot explain R, paired across lineages.
- Ti_L NON-MONOTONE (registered monotone-rise expectation REFUTED at low
  dose, disclosed): meanL .364 -> .196 (k5) -> .266 (k10) -> .710 (k15,
  kL 15/16) -> .712 (k19, 15/16). The top-5 glut cells are load-bearing
  for BOTH sides' structure — low-dose removal is purely destructive
  (bilateral depression), the L-restore arrives only with mass ~>= .095
  (k15). Refines L115/L116's L-mass-law with a floor: below the restore
  threshold, removal adds NO structure on either side.
- Sr_R = LOTTERY CONFIRMED (dose-INCONSISTENT): .401 -> .077 (k5) ->
  .136 (k10) -> .357 (k15, 4/16 RE-DRAWS) -> .199 (k19). Dies, dies,
  re-draws at k15, dies again — no dose structure whatsoever; the L116
  marginal-side-lottery reading is the answer (perturbation class, never
  class-coherent). Registered watch rule returned OTHER, honestly.
- Tr_R mildly suppressed late (k15 .216 / k19 .253 vs full .349, kR
  0/16) — spared-ish, consistent with L116. Ta/Pr floors unchanged.
- Dose gains bisected fresh: cutk5 .139820 [OUTSIDE the registered .14-.16
  disclosure band — DISCLOSED, af target-matched: mean af .1066, per-seed
  .101-.117, staircase 8.8e-6], cutk10 .140691, cutk15 .158205 (in band).
  Removing the heaviest excitatory drivers shifts the gain need slightly
  DOWN — the band was a heuristic from stored arm gains, not a gate.

Anchors ALL GREEN: C0A stored arms x seeds {801,901} x 10-key schema ==
raw_l113 EXACT max 0.0 (47th consecutive chain anchor; B12 asserted
absent from stored); g_cut .145108 / g_cut19 .150968 / g_cut58 .154173
re-bisected == stored EXACT all three; C0B certification PASS (pair-
generalized machinery on stored raw_l113 == results_l113.json Ti+Tr
tables, every pinned read, BEFORE any L117 pin); P4 af ranges + b65 band
PASS; full-arm B12 reads inside registered bands (Ti .364/.473, Sr
.133/.401); ladder sanity PASS (cut 16/16, b65 16/16 both, cut19 15/16).

Honesty clauses honored: one batch n=16 + anchor seeds (k-cells carry the
known batch swing; paired same-seed deltas are the claim-carriers); mass
and count co-vary by construction — L118 (mass-matched pure-non-glut-19)
owns the separation, and its reading sharpens: if R survives L118 (as
L115 suggests), transmitter identity + top-mass PLACEMENT jointly carry
the R-kill. Follow-up seeded: L119 minimal-subset ladder (k in {1,2,3} +
random-5-of-19-glut control) to find where the step lands and whether it
is "the heaviest 5" or "any 5 glut".

Verdict: L117 answers the card — NEITHER registered dose shape holds;
the Ti_R kill is a specific-subset effect concentrated in the heaviest
glutamatergic cells, the L axis keeps its mass threshold (with a newly
measured destructive floor below it), and Sr_R re-draws under every
perturbation class.

Verified: PREREG l117/PREREG.md registered BEFORE any rollout (static
pins from l117_static.py, zero rollouts, run pre-launch); l117_run.py =
asserted exact-string transform of l116_run.py (l117_build.py, all 18
patterns clean; l116's latent raw_partial load-path quirk fixed);
l117_static.py exit 0; run exit 0 CPU 785 s (8 arms x 18 seeds + 6
bisects); l117_verdict.py exit 0. Artifacts: l117/{PREREG.md,
static.json, run.out, run.err, anchors_run.json, raw_l117.npz,
raw_partial.npz, results_l117.json}. No live changes.

## L118 — mass-matched pure-non-glut 19s: registered MIXED — neither coherence-kill nor clean glut-identity; the R axis is a perturbation lottery at this mass, and only glut-19 removal kills it EVERY time
Question (ideas 59 card): cut19 (glut-19 @ .1103) and cut58 (58 non-glut
@ .3921) both kill Ti_R 0/16 on every batch; L115's random mixed 19s
(.106-.131) never did (kR 3/13/10). Class COHERENCE (any single-class
half at glut-19 mass kills) vs GLUT IDENTITY? Design: 3 rejection draws
of 19 NON-glutamatergic heavy cells, mass-matched to glut-19's UNROUNDED
.11033 (pinned torch seeds 1180/1181/1182, tol .0045, zero fallback;
masses .11187/.10958/.11145; pairwise overlap 7/4/9 cells; card
amendment: 3 draws not 1, L115's 3-draw form), fresh B13 1701-1716
(asserted absent from l113/l115/l117 stored batches in-run), l117
machinery verbatim (l118_build.py exact-string transform + residual
token scan). RESULT: registered classification MIXED, kills 1/3,
survivors 1/3 — Ti_R .276 (kR 2, dR -.193, marginal-miss kill by .007
on the paired leg) / .426 (kR 4, dR -.043, SURVIVOR) / .185 (kR 0, dR
-.284, KILL); full .469 (7/16), cut19 .060, cut58 .228 all inside
registered bands. Pure-non-glut .11-mass removal re-rolls Ti_R anywhere
between near-kill and survival — it is a PERTURBATION LOTTERY class
(L41/L56/Sr_R family), NOT a reliable kill: contrast glut-19 removal,
dead 0/16 on FOUR consecutive independent batches (B10/B11/B12/B13) and
at 1/26th of cut58's mass (L117 k=5 @ .0425). Descriptive gradient
(post-hoc, disclosed, not registered): at ~.11 mass, glut kills
reliably, mixed mostly survives, pure non-glut is mid/lottery; non-glut
kills reliably only near-full-pool (.3921). L-axis: mass-law holds for
non-glut too — cutngb restores L 16/16 .911 (cut19-like), cutnga/cutngc
partial (.459/.553). Sr_R watch: cutnga/cutngb RAISE Sr_R above full
(14/16 .613, 11/16 .575 vs 4/16 .405), cutngc kills it (1/16 .204) —
same lottery, both directions. Draw gains .1635-.1676 OUTSIDE the
.14-.16 disclosure band (DISCLOSED; af target-matched .1085-.1105 —
non-glut cuts need MORE gain to hold af; in-degree profile differs,
descriptive). Anchors: C0A max 0.0e+00 (48th consecutive chain anchor,
stored 5 arms x seeds 801/901 vs raw_l113), all 3 stored gains
re-bisected EXACT, C0B certified pre-pin (l113 Ti+Tr tables all 5
arms), P4 green, full-arm B13 inside all bands, sanity PASS (b65 16/16
both sides, cut_kL 16, cut19_kL 13). Instruments caught pre-launch: the
build's global path rename rewired the C0A absence-assert onto the run's
OWN output npz (L39 control-rewiring class, fixed in build 9b) and the
derivation block asserted dng100_all before its def-site (NameError,
moved to the downstream pin); verdict key mismatch (g_-prefix) caught at
lint. Follow-up queued: non-glut dose ladder (how much of the 58 does
the R-kill need?) beside L119 (glut k in {1,2,3} step locator).
Artifacts: l118/{PREREG.md, static.json, run.out, run.err,
anchors_run.json, raw_l118.npz, raw_partial.npz, results_l118.json}.
No live changes.

## L119. minimal-glut-subset-step (tick 143, 2026-11-17)

QUESTION: L117 found the Ti_R kill fires COMPLETE at k=5 (the 5 heaviest
glut cells, .0425 mass) — where exactly does the step land, and is it the
heaviest-5's PLACEMENT or glut IDENTITY at 5-cell granularity?

DESIGN: 10 arms — 5 stored anchors + cutk1/cutk2/cutk3 (the k heaviest
glut, deterministic mass-desc filter; k5 arm included with its l117
stored gain asserted EXACT) + cutr5 (pinned torch seed 1190,
randperm(19)[:5]: cells 763/994/1304/1434/1777, mass .0231, ZERO overlap
with the heaviest-5, all from the lighter half — positions 7-17 of 19).
Fresh B14 1801-1816 (absent from l113/l115/l117/l118 npz asserted in-run).
PREREG l119/PREREG.md FIRST (kill criterion = L118 registered form:
meanR <= m0-.10 AND kR<=4 AND paired dR <= -.20). l119_run.py =
asserted exact-string transform of l118_run.py (l119_build.py, every rep
count-checked; residual scan + file-path direction check).

FINDINGS (B14, n=16, same-batch curve):
- P1 k* = 5, SHARP STEP: k=1 (.0096) .393/5 — k=2 (.0185) .437/6 —
  k=3 (.0268) .508/8 (ABOVE full, dR +.077) — k=5 (.0425) .061/0 KILL
  (dR -.370, 13/16 down) — k=19 .030/0 KILL. The three low doses leave
  R intact (k3 even above full); the kill completes only with the
  heaviest-5 SET. l117's B12 k5 kill REPLICATES fresh (cross-batch
  worry resolved). k=4 window untested — L120 disambiguates WHICH of
  #4 (cell 204) / #5 (cell 32014) completes it.
- P2 PLACEMENT: cutr5 (.0231, light-5, zero overlap) does NOT kill
  (.415, 6/16, dR -.016, n_down 3/16) — "any 5 glut" is dead. Mass
  story dead at BOTH ends: .0268 heaviest (no kill) vs .106-.131
  random-19 (no kill, L115) vs .0425 heaviest-5 (kill every batch) —
  the specific heavy placement carries the R-kill.
- L-axis CHAOS at single-cell dose (descriptive): Ti_L full .357 (4/16)
  -> k1 .553 (12/16!) -> k2 .271 (0/16) -> k3 .475 -> k5 .238 ->
  k19 .758 (16/16). ONE cell (.0096) re-draws L from 4/16 to 12/16 —
  the L117 non-monotone reading strengthens into full lottery shape.
- Sr_R watch (no gate, lottery confirmed): .358/.481/.203/.421/.070/.175
  at k 0/1/2/3/5/19, kR 2/7/0/7/0/1 — dose-inconsistent, both
  directions. Tr_R also re-draws UP at k3 (13/16 .583 vs full 2/16).
- Gains DISCLOSED outside .14-.16 band: cutk1 .166175, cutk3 .174042
  (cutk2 .147846, cutr5 .159249 inside); all af-matched to .109056,
  staircases 1.4e-05..5.4e-04 disclosed. g_cutk5 == l117 stored EXACT
  (0.13981970071792604) — 4th deterministic stored-gain anchor class.

ANCHORS ALL GREEN: C0A max 0.0e+00 (49th consecutive chain anchor;
stored 5 arms x seeds 801/901 x 10-key schema vs raw_l113, full batch);
g_cut/g_cut19/g_cut58/g_cutk5 re-bisects == stored EXACT all four; C0B
machinery cert PASS on stored raw_l113 BEFORE any L119 pin; P4 af range
+ b65 band green; full-arm B14 inside all registered bands (Ti L .357
R .431, Sr both); sanity PASS (cut_kL 16, b65 16/16 both, cut19_kL 16).
CPU 1133 s. Instruments: the residual scan CAUGHT a real pre-launch
miss — the run-resume np.load path was not renamed (would have loaded
l118's partial; L39 direction class, fixed in build step 13b); verdict
g_cutk5 key lives in the savez not the anchors json (KeyError caught at
first verdict pass, read from raw npz — zero wasted rollouts).
Artifacts: l119/{PREREG.md, static.json, run.out, run.err,
anchors_run.json, raw_l119.npz, raw_partial.npz, results_l119.json,
verdict.out} + l119_static.py, l119_build.py, l119_run.py,
l119_verdict.py. No live changes. Follow-up seeded: L120 (cutk4 both
orders — which cell completes the kill).

## L120 — cutk4-disambiguation: CELL 204 COMPLETES THE R-KILL (XOR, placement-pure)

Card: LANE.md ideas-62 L120. Tick 144, 2026-11-17 09:00-10:2x. PREREG
l120/PREREG.md registered BEFORE l120_run.py (all anchors re-derived from
stored jsons). No live changes.

Arms (9): anchors full/b65/cut/cut19/cut58 (seeds 801/901 vs raw_l113) +
cutk3 (drop 286,313,561; .0268) + cutk4a (+204, 4th heaviest; .0347) +
cutk4b (+32014 instead, 5th; .0346) + cutk5 (both; .0425) on FRESH
B15 1901-1916 (asserted absent from raw_l113/l115/l117/l118/l119).
k4a/k4b are MASS-MATCHED BY CONSTRUCTION: rounded .0347 vs .0346,
unrounded delta 9.2e-05 — one-cell difference (204 vs 32014), so a kill
difference between them is placement-pure, mass cannot explain it.

VERDICT (P1, registered kill criterion meanR<=m0-.10 AND kR<=4 AND
paired dR<=-.20, m0 = full .468):
- cutk4a KILLS Ti_R: .115, 0/16, dR -.353, 13/16 down.
- cutk4b does NOT kill: .732, 15/16, dR +.264 — R not merely survives,
  it is the HIGHEST R of any arm (above full .468).
- XOR fires: CELL 204 (the 4th-heaviest glutamatergic heavy) completes
  the R-kill given the top-3 removed. Minimal killing SET identified =
  4 cells {204,286,313,561}; per-cell necessity of 286/313/561 within
  that set untested (disclosed; would be the next sub-slice if wanted).
- cutk5 (superset) also kills (.017, 0/16, 16/16 down) — internally
  consistent; k3 no-kill (.554, 10/16, ABOVE full).
- P1b: kill mass bound tightens [.0268,.0425] -> [.0268,.0347]; the
  matched-mass partner survives AT the same mass, so the bound is not a
  mass law at this granularity — placement (l115/l119's conclusion, now
  at single-cell resolution).

L-AXIS secondary (no gate, l119 chaos warning heeded — descriptive):
the two cells carry OPPOSITE side actions on L too: 4a (204 out, 32014
in) restores Ti_L FULLY .753 16/16 == cut19's .754; 4b (32014 out, 204
in) kills L .043 0/16; k5 (BOTH out) leaves L dead .227 — L-restore
requires 204-out AND 32014-in: a JOINT (interaction) condition, not a
per-cell one, and it revises l117's ~.095 mass threshold for L (4a
restores L at .0347 < .095 — the threshold was a property of the
dose-ladder PATH, not of mass). Secondaries: Sr_R needs BOTH cells
(4a/4b .495/.489 survive, k5 kills .102) — Sr_R is 2-cell like Ti_R;
Tr_R re-draws marginal under every k arm (15/16 at k3 — noisy axis,
watch only); Ta/Pr floors except Pr cutk4b .684 14/16 (lottery-class
re-draw, disclosed, no gate).

ANCHORS ALL GREEN: C0A vs raw_l113 max 0.0e+00 (50th consecutive chain
anchor); NEW C0A-119 class — cutk3/cutk5 at 801/901 vs l119/raw_l119.npz
bit-identical max 0.0 (22 keys x 2 arms x 2 seeds; l119 ran every arm at
all 18 seeds, so its own new arms anchor the chain forward); FIVE stored
gains re-bisected EXACT: g_cut .14510760426521305 (l107), g_cut19
.15096808075904844 (l111), g_cut58 .15417299151420596 (l113), g_cutk5
.13981970071792604 (l117/l119), g_cutk3 .17404209494590758 (l119 fresh
gain, new stored-form anchor — deterministic bisect landed on it).
Fresh gains cutk4a .155166 / cutk4b .14765 BOTH inside the .14-.16
disclosure band (stairs 3.0e-04 / 6.0e-05). C0B certified pre-pin
(stored l113 Ti+Tr tables all 5 arms, PASS). P4 af-range + b65-band
green. Full-arm B15 bands: Ti L .469 slightly above (.30,.45) —
DISCLOSED (B14 .357; batch swing, disclosure-only band); Sr both in.

Instruments: l120_build.py = asserted exact-string transform of
l119_run.py; build residual scan CAUGHT the L39-class resume bug again
pre-launch (np.load("l119/raw_partial.npz") — fixed to l120 before any
rollout) + one leftover B14 comment; two duplicate-site count fixes
(X-dict tail indent-independent fragment; noise dict 3 sites not 2).
l120_verdict_build.py = asserted transform of l119_verdict.py (B14
whitelist for intentional historical labels). Run exit 0, CPU 1603 s
(9 arms x 18 seeds + 7 bisects). raw_l120.npz checkpointed BEFORE
analysis (L45a rule).

Artifacts: l120/{PREREG.md, static.json, run.out, run.err,
anchors_run.json, raw_l120.npz, raw_partial.npz, results_l120.json,
verdict.out} + l120_static.py, l120_build.py, l120_run.py,
l120_verdict_build.py, l120_verdict.py. No live changes. Follow-up
seeded: L121 (non-glut dose ladder, takes B16 per the batch-sharing
note); the 32014 L-interaction slice is a taste candidate if the R story
ever needs the L twin.

## L121 — nonglut-dose-ladder: registered MASS-FRACTION cell fires at k19, but the curve is NON-MONOTONE (k29 re-rolls R to the lineage's highest); cutk5 kill replicates on a 4th batch

Card: LANE.md ideas-61 L121. Tick 145, 2026-11-17 10:46-11:1x. PREREG
l121/PREREG.md registered BEFORE l121_run.py (static pins derived
zero-rollout first: l121_static.py). No live changes.

Arms (9): anchors full/b65/cut/cut19/cut58 (801/901 vs raw_l113) +
RETAINED cutk5 (dual registered purpose: C0A-120 forward-chain anchor vs
raw_l120 AND free B16 replication of the L120 XOR kill) + deterministic
heaviest-first NON-glut dose ladder cutng19 (.1946) / cutng29 (.2588) /
cutng39 (.3132), k58 endpoint == cut58 (.3921, set identity + edge
recompute 641205). NO RNG. FRESH B16 2001-2016 (asserted absent from
l113/l115/l117/l118/l119/l120). Static surprise vs the card's guess:
heaviest-19 non-glut = .1946 (card guessed ~.11); the single heaviest
heavy cell (id 32160, .01715) is NON-glutamatergic.

VERDICT (P1, kill criterion meanR<=m0-.10 AND kR<=4 AND dR<=-.20,
m0 = full .483):
- cutng19 KILLS: .250, 0/16, dR -.233, 9/16 down — first non-glut kill
  BELOW pool completeness (.1946 vs cut58's .3921); registered
  MASS-FRACTION cell fired.
- BUT the registered monotonicity read REFUTES smooth mass-tracking:
  cutng29 (.2588) RE-ROLLS R UP to .727, 16/16, dR +.244 — the HIGHEST
  R of ANY arm in the lineage (above full .483, above l120's cutk4b
  .732-tier); cutng39 (.3132) full-like .496 7/16; cut58 kills .202
  0/16 (l113's B10 endpoint replicates in-batch).
- Honest shape: the ENVELOPE is mass-consistent (both extremes kill:
  .1946 and .3921) but the MIDDLE is a lottery (L115/L118 class at dose
  resolution) — a monotone mass story predicts kill depth ordered
  .1946<=.2588<=.3132; measured .250/.727/.496 refutes it. Single batch
  B16; L88/L90 rule — a fresh-batch rebase (B17) is owed before the
  k19-kill is cited as batch-robust.
- P2: cutk5 KILLS on B16 — .045, 0/16, dR -.437, 16/16 down — 4th
  consecutive batch (B12 l117 / B14 l119 / B15 l120 / B16): the L120
  single-cell placement claim is now BATCH-ROBUST. (Cosmetic: the
  results-json cls string reads "B12/B14/B16/B16" — my B15->B16 sweep
  hit the label inside the f-string; data correct, disclosed.)
- L-axis mirror (watch, no gate): k29 kills L (.200 0/16) while RAISING
  R; k39 restores L (.640 15/16); k58 restores fully (.774 16/16 ==
  l113). Dose-level mirror of l120's cell-level opposite side actions.
- Sr_R: killed by EVERY ng dose (meanR .002-.103, all kR 0) — the most
  fragile axis in the vocabulary; any heavy non-glut removal kills it.
  Tr_R dies at 19/29 (.006/.003), partial at 39 (.206); Tr_L dead
  everywhere (l116 form).

Anchors ALL GREEN: C0A full-batch vs raw_l113 max 0.0e+00 (51st
consecutive chain anchor); NEW C0A-120 class (cutk5 vs raw_l120, 22 keys
x 2 seeds) max 0.0e+00 — the L120 forward-chain addendum works; FOUR
stored gains re-bisected EXACT (g_cut/g_cut19/g_cut58/g_cutk5); fresh
gains .150260/.144264/.146254 ALL in the .14-.16 disclosure band (no
disclosure needed); C0B certified on stored l113 pre-pin (Ti+Tr, all 5
stored arms); P4 af-range + b65 band green; full-arm B16 in all
disclosure bands; sanity PASS (cut kL 16, b65 16/16 both, cut19 kL 16).
Run 905 s CPU (graphs 3 s, 7 bisects, 18 seeds x 9 arms).
raw_l121.npz checkpointed BEFORE analysis. Artifacts: l121/{static.json,
PREREG.md, run.out, anchors_run.json, raw_l121.npz, results_l121.json};
build transforms l121_build.py / l121_verdict_build.py (exact-string,
drift-guarded, residual scans CLEAN).

Next-slice notes (taste): (1) the k19 kill + k29 super-raise pair is a
2-point mass-nearly-matched CONTRAST on the ng side (.1946 vs .2588,
10 cells apart) — a cell-resolution dissection between ng[19:29] is the
L120-shaped question there; (2) B17 rebase of the k19 kill before it is
cited; (3) 32160 (heaviest cell, non-glut) single-cell arm.

## L122 — cutng19/cutng29 batch-rebase (B17): the ENTIRE non-monotone dose curve is BATCH-ROBUST point-for-point; pooled n=32 numbers now the citable form

Card: LANE.md ideas-63 L122. Tick 146, 2026-11-17 12:14-13:0x. PREREG
l122/PREREG.md registered BEFORE build/run (pins from stored
results_l121.json / raw_l121.npz, never log sentences). No live changes.

Design: L121's two single-batch claims (ng19 kill at .1946; ng29
super-raise .727 = highest R of any arm) re-rolled on FRESH B17
2101-2116 with the IDENTICAL 9-arm ladder, machinery verbatim, NO RNG
arms. ng gains cutng19/29/39 became STORED-FORM anchors (l121 fresh
gains asserted EXACT — deterministic re-bisects re-land, L120 addendum
rule; all three landed EXACT first try). l122_run.py/l122_verdict.py =
asserted exact-string transforms of l121_* (drift guard caught 3
wrap-fragile patterns pre-launch: docstring exact-match -> splice, B16
count 10->8 after docstring swap, g_cutk5 literal x2 — zero wasted
rollouts).

VERDICT — R1/R2/R3 ALL REPLICATE; the dose-curve SHAPE itself is
batch-robust (B17 vs B16 point-for-point):
- R1 cutng19 KILLS on B17: .204, 0/16, paired dR -.236, 10/16 down
  (B16: .250, 0/16, -.233, 9/16) — the .1946 non-glut kill below pool
  completeness is BATCH-ROBUST (2/2). L121's MASS-FRACTION firing
  upgraded to citable.
- R2 cutng29 raise REPLICATES: .749, 15/16, dR +.309 (B16 .727, 16/16,
  +.244) — AGAIN the highest R of any arm, now on BOTH batches; the
  middle-dose lottery re-rolls UP reproducibly. A perturbation lottery
  with a reproducible TOP: the strongest "middle is not smooth mass"
  evidence in the lineage.
- R3 endpoints: cut58 kills .238 0/16 (3rd batch: B10/B16/B17); cutk5
  kills .044 0/16 (5th consecutive batch B12/B14/B15/B16/B17 — the
  L120 cell-204 placement kill is now as batch-robust as anything the
  lane measures).
- ng39 stays full-like .475 7/16 (B16 .496 7/16). Curve: kill ->
  super-raise -> full-like -> kill, identical shape both batches.
- POOLED (L90 form, batch union B16+B17, FULL-PRECISION Wilson,
  unrounded): Ti_R cutng19 0/32 [.000,.107]; cutng29 31/32 p-hat .969
  [.843,.995]; cutng39 14/32 [.282,.607]; cutk5 0/32; cut58 0/32; full
  11/32 p-hat .344 [.204,.517] (base R stays the known noisy
  distribution, 4-7/16 per batch). These n=32 numbers are the citable
  form; per-batch k stays diagnostic.
- Sr_R: killed by EVERY ng dose again (B17 .005-.123, all kR 0) —
  2 batches; most fragile axis in the vocabulary confirmed.
- L-axis watch: mirrors non-monotonically as on B16 (k29 kills L .164
  0/16 while raising R; k39 .628 15/16, k58 .838 16/16 restore).

Anchors ALL GREEN: C0A vs raw_l113 max 0.0 (52nd consecutive chain
anchor); C0A-120 retained PASS; NEW C0A-121 forward-chain class PASS
first try ({cutk5,cutng19,cutng29,cutng39} x 22 pool keys x 801/901 vs
raw_l121, max 0.0 — second consecutive run the L120 addendum extends
the chain for free); SEVEN stored gains re-bisected EXACT (3 new ng
stored-form anchors); C0B certified pre-pin + NEW B16-cert (my duty
machinery on raw_l121 B16 == results_l121.json Ti table, all 9 arms)
BEFORE the pooling read; P4 af/b65-band green; full-arm B17 bands
green (Ti L .416, R .440 inside widened (.25,.48)/(.35,.58); disclosed
as batch-swing-widened); sanity PASS (cut kL 16, b65 16/16 both,
cut19 kL 16).

Run 1127 s CPU (graphs 3 s, 7 bisects, 18 seeds x 9 arms).
raw_l122.npz checkpointed BEFORE analysis. Artifacts: l122/{PREREG.md,
run.out, anchors_run.json, raw_l122.npz, results_l122.json}; build
transforms l122_build.py (exact-string, drift-guarded; 3 catches).

Next-slice notes (taste): (1) the ng[19:29] cell-resolution dissection
(L120-shaped XOR window on the non-glut side — which of the 10 cells
between .1946 and .2588 carries the super-raise vs the kill?);
(2) 32160 single-cell arm (heaviest cell, non-glut); (3) with the
curve batch-robust, a 2-batch REGISTERED replication of the ng-side
envelope exists — the glut side (l117/l119/l120) and ng side now both
have batch-robust kills, and the cross-side contrast (4-cell glut
placement kill vs mass-envelope ng kill) is the citable asymmetry.

## L123 — ng[19:29] window XOR: NEITHER half flips alone (W4); the heavier
quintet's removal buys HALF the recovery, the lighter's buys NONE, and the
super-raise needs the whole window OUT (tick 147, 2026-11-17)

Question (ideas-64): ng19 (drop 19 heaviest non-glut, .1946) KILLS Ti_R;
ng29 (drop 29, .2588) SUPER-RAISES it. Which of the 10 window cells
(ranks 20-29) carries the flip? Arms cutwA = ng_desc[:24] (remove ranks
20-24, the HEAVIER quintet {558,80,628,32072,585}, .2286) vs cutwB =
ng_desc[:19]+ng_desc[24:29] (remove ranks 25-29, the LIGHTER quintet
{1110,319,707,354,32271}, .2248) — quasi-mass-matched (delta .0038),
both drop 24 cells; window per-cell shares .0059-.0070 = FLAT, no
cell-204.

VERDICT (fresh B18 2201-2216, kill criterion verbatim, RESTORE bar
meanR>=.45 & kR>=12): registered **W4 INTERMEDIATE/MIXED**, decomposed —
- cutwB (lighter half out): DEEP KILL .183 0/16 paired dR -.328 ==
  ng19's own .243 1/16 — removing ranks 25-29 buys NOTHING toward the
  flip; the kill regime extends to 24 cells while the heavier quintet
  stays IN.
- cutwA (heavier half out): PARTIAL un-wind .413 5/16 dR -.098 — halfway
  between ng19's kill and full's .511, NOT a restore; the flip does not
  complete in either half -> the super-raise needs the WHOLE 10-cell
  window out (a 2-step placement structure, not a single-cell XOR —
  contrast L120 cell 204).
- Mass dead at window resolution AGAIN: delta-mass .0038 between arms,
  outcome gap .23 meanR / 5-vs-0 k-cells, and the LIGHTER removal kills
  harder (L119/L121 class).
- The ng29 "super-raise" (.791 16/16, ABOVE full .511) is not
  restoration but a reproducible attractor OVERSHOOT — and it is now
  nearly deterministic pooled: **47/48** Wilson [.891,.996] (B16 16/16 +
  B17 15/16 + B18 16/16).
- Side-anticorrelation inside one arm: ng29 super-raises R (16/16 .791)
  while KILLING L (0/16 .129) — the window removals flip the sides in
  opposite directions simultaneously.

Secondaries: cutk5 KILL replicates 6th consecutive batch (B12/B14/B15/
B16/B17/B18, .046 0/16 dR -.465); ng19 KILL + ng29 SUPER-RAISE replicate
3rd batch each; Sr_R killed by EVERY dose again (3rd batch, .004-.119).
Pooled n=48 citables (L90 full-precision Wilson): full 21/48 [.307,.577],
cutng19 1/48 [.004,.109], cutng29 47/48 [.891,.996], cutk5 0/48
[.000,.074], cut58 1/48 [.004,.109].

Anchors ALL GREEN: C0A vs raw_l113 max 0.0 (53rd consecutive), C0A-120
PASS, C0A-121 (3 arms) PASS, **NEW C0A-122 forward chain PASS first try**
(cutk5/cutng19/cutng29 vs raw_l122, 22 keys x 3 arms x 2 seeds, max 0.0
— the L120 addendum chain extends a second run forward for free); 6
stored gains re-bisected EXACT (g_cut/cut19/cut58/cutk5/cutng19/cutng29);
C0B certified on raw_l113 + **B17-cert** (machinery reproduces
results_l122.json Ti table, all 9 arms) BEFORE any window read; P4
af-range + b65 band green; fresh gains cutwA .143658 / cutwB .149229
BOTH in .14-.16 band (stairs 2.1e-5/8.9e-4); full-arm B18 bands green
(Ti L .358, R .511; Sr L .158, R .402); sanity PASS (cut kL 16, b65
16/16 both, cut19 kL 15). l123_static.py re-pinned k19/k29/k58 == l121
stored EXACT; window halves verified to PARTITION the k29 drop set
(union == k29, overlap == k19).

Single batch B18 for the window arms (disclosed): the wA/wB contrast is
single-batch — rebase owed (L124 queued) before the half-asymmetry is
cited robust; every arm it leans ON (ng19/ng29/cutk5/cut58/full) is now
3+-batch. Cosmetic: run-log "NEW arms excluded" print lists cutwA not
cutwB (inherited label string; anchors are computed from real dicts,
zero effect).

Run 1396 s CPU (10 arms x 18 seeds + 8 bisects incl 2 fresh).
raw_l123.npz checkpointed BEFORE analysis. Artifacts: l123/{PREREG.md,
static.json, run.out, anchors_run.json, raw_l123.npz, results_l123.json};
build transforms l123_build.py + l123_verdict_build.py (exact-string,
drift-guarded; 3 catches pre-launch: noise-dict count 2->3, substring
double-append g_cutwB, verdict scan over-match on its own W1 text).


## L124 — cutwA/cutwB batch rebase (B19): W4 BATCH-ROBUST (tick 148, 11-17)

Question (ideas-65): is L123's W4 window finding (neither half flips the
ng19-kill -> ng29-super-raise alone) batch-robust, and do the citable
pooled numbers exist yet? Re-rolled BOTH window halves + endpoints + k5 +
full on FRESH B19 2301-2316 (asserted absent from all 9 stored npzs
pre-launch, verified independently before CPU), l123 machinery VERBATIM
(l124_build.py/l124_verdict_build.py exact-string transforms, 17+23 reps
all count-exact, zero drift-guard catches this time — the anchored-rep
discipline held).

Verdict — W4 BATCH-ROBUST, R1/R2/R3 all green:
- R1 PASS: cutwB KILLS on B19 (.164 kR 1/16, paired dR -.258, 10/16
  down) — deep-kill replicates 2nd batch.
- R2 PARTIAL-ROBUST: cutwA .376 kR 4/16 INSIDE the registered partial
  band [.35,.50]/kR 3-8 (B18 was .413/5) — the partial un-wind is a
  stable intermediate, not a lottery draw.
- R3 no: neither half reaches RESTORE/SUPER on B19.
- So the super-raise needs the WHOLE 10-cell window OUT on BOTH batches:
  the ng[19:29] window acts as a 2-STEP PLACEMENT UNIT (no single-cell
  XOR, contrast L120's cell 204; no half-flip, contrast L123's own
  registered W1).
- POOLED window union n=32 (L90 full-precision Wilson, B18-cert FIRST):
  cutwA 9/32 [.156,.454] — intermediate mass strictly between cutwB and
  full; cutwB 1/32 [.006,.157] — kill. The gap between the halves is
  now citable at 2 batches.
- Secondaries: cutk5 KILL 7th consecutive batch (0/16; pooled 0/64
  [.000,.057]); ng19 kill + ng29 super-raise 4th batch each (pooled
  ng29 62/64 [.893,.991] — the super-raise is near-deterministic;
  ng19 2/64 [.009,.107]; cut58 1/64; full 23/64 — base R confirmed
  noisy distribution, cite never as a point). Sr_R killed by EVERY ng
  dose again (4th batch: .025/.106/.009/.055/.051 vs full .409). L-axis
  mirror persists (ng29 kills L 0/16 .189 while super-raising R 15/16).

Anchors ALL GREEN: C0A vs raw_l113 max 0.0 (54th consecutive chain
anchor), C0A-120/121/122 retained PASS, NEW C0A-123 forward-chain class
PASS FIRST TRY ({cutk5,cutng19,cutng29,cutwA,cutwB} vs raw_l123, 22 keys
x 5 arms x 2 seeds — chain now extends THREE runs forward free), EIGHT
stored gains re-bisected EXACT (wA/wB promoted to stored-form this run:
.14365819573402408 / .14922914385795596), C0B + NEW B18-cert (machinery
reproduces results_l123.json Ti table all 10 arms) BEFORE any B19 read,
P4 af-range + b65 band green, full-arm B19 bands green (Ti L .364
R .422; Sr L .121 R .409), sanity PASS (cut kL 16, b65 16/16, cut19
kL 14). Staircases 3.1e-5..8.9e-4 disclosed.

Run 1473 s CPU (10 arms x 18 seeds; NO fresh bisects — all gains
stored-form). raw_l124.npz checkpointed BEFORE analysis. Artifacts:
l124/{PREREG.md, run.out, anchors_run.json, raw_l124.npz,
results_l124.json}; transforms l124_build.py + l124_verdict_build.py.
No live changes. Follow-ups seeded (ideas 66): L125 window-scramble
control (count/dose vs contiguous placement — the strongest remaining
null), L126 within-window interpolation.

## L125. window-scramble control: the window is NOT uniquely privileged — a coherent decile, not THE window, owns the super-raise (ideas-66, tick 149, 2026-11-17)

CARD AMENDMENT (registered pre-run, feasibility): the card's "+-0.01 mass
match to .2588" for 10-of-ranks-30-58 is INFEASIBLE — the entire 29-cell
pool carries .1333 (l121 stored pins); max non-window-10 = ranks 30-39 =
.0544 -> max total .2490; 100000 rejection attempts found zero. Amended:
scr0 = DETERMINISTIC max-mass scramble (k19 + ranks 30-39, .2490, window
kept IN the graph — the mass-armor arm); scr1/2/3 = pinned-RNG random
10-of-pool draws (.2422/.2409/.2388, attempt-1 draws, seeds 1251-1253).
12 arms x fresh B20 2401-2416, l124 machinery verbatim, scr arms FRESH
bisected (scr1 .1699 / scr3 .1650 OUTSIDE .14-.16 band, af-matched,
DISCLOSED per PREREG).

PRIMARY (kill criterion verbatim; m0 .447): SC1 FIRED — scr0 SUPER-RAISES
Ti_R .622 12/16 (RESTORE-grade AND super) BILATERALLY (Ti_L .610 12/16,
unlike ng29 which kills L .216 0/16): dropping the ADJACENT DECILE with
the window kept in also flips the kill -> super-raise, at .0098 BELOW the
window's mass. But count/dose is NOT sufficient either: scr1 (random 10,
.2422, only .0068 below scr0) is the DEEPEST KILL of any arm (.041 0/16,
dR -.405, 15/16 down); scr2 .469 6/16 PARTIAL; scr3 .425 6/16 PARTIAL.
Registered tree label "COUNT-CARRIED" is carried by scr0 alone — the
per-draw decomposition (L55/L109 rule) is the claim-carrier: {super, kill,
partial, partial} at near-identical masses = a draw LOTTERY with a wide
envelope, and the operative discriminator is COHERENCE of the removed set
(a contiguous heavy decile: ng29 ranks 20-29 -> .779 16/16; scr0 ranks
30-39 -> .622 12/16; scattered random 10s: kill/partial/partial). L124's
"needs the WHOLE 10-cell window" REVISED: it needs A coherent heavy decile
out, not THE window. Coherence-vs-heaviness confound OPEN (a contiguous
LIGHT decile arm, e.g. ranks 40-49, would separate them — L127 seed).
Single-batch scr arms — rebase owed before scr0-super is cited robust.

Secondaries: cutk5 KILL 8th consecutive batch (pooled 0/80 [.000,.046] —
strongest citable in the lineage); ng19 kill + ng29 super 5th batch each
(pooled ng29 78/80 [.913,.993], ng19 3/80 [.013,.105], cut58 1/80, full
29/80 — base R noisy distribution again, never cite as a point); Sr_R
lottery both directions across scr draws (raised .144 at scr1, killed
elsewhere — watch, no gate); Ta_L scr3 raises .606 (new pair-axis lottery,
watch). Anchors ALL GREEN: C0A vs raw_l113 max 0.0 (55th consecutive),
C0A-120/121/122 retained, C0A-123 retained (3 shared arms), NEW C0A-124
forward chain PASS FIRST TRY (3 arms x 22 keys x 2 seeds vs raw_l124 —
chain 4 runs forward free), 6 stored gains re-bisected EXACT, C0B + NEW
B19-cert (machinery == results_l124.json Ti table, all 10 arms) BEFORE any
B20 read, P4/bands/sanity PASS. Build drift-guard catches pre-launch:
noise-dict pattern count 2->3 (the l123 lesson — settle + rollout-settle
+ rollout-WIN) and C0A-123 tuple 8/12-vs-4/8 indent; verdict-time B18
NameError (analysis-only, zero wasted rollouts). Artifacts: l125/
{PREREG.md, static.json, raw_l125.npz, anchors_run.json, results_l125.json,
run.out, verdict.out}. CPU-only 1900 s; no live changes.

## L126 — window-interpolation (B21, 13 arms; tick 150, 2026-11-17)

Card: LANE.md ideas-66. PREREG l126/PREREG.md FIRST; static pins
l126_static.py zero-rollout pre-launch (cutng21 n=21788 e=644509 .2086 /
cutng23 n=21786 e=644282 .2220 / cutwA==k24 re-pinned == l123 stored EXACT
n=21785 e=644177 .2286 / cutng26 n=21783 e=643979 .2411 / cutng28
n=21781 e=643725 .2529; strictly nested ng21<ng23<wA<ng26<ng28<k29;
DNg100 in no drop). l126_run.py = asserted exact-string transform of
l124_run.py (51 reps ALL count-exact; ONE residual-scan catch: the stale
-token list flagged deliberate cutwB DISCLOSURE comments — scan amended to
whitelist comment/docstring cross-references explicitly, never code).
Run exit 0 CPU 2319 s (13 arms x 18 seeds + 11 bisects, incl 7 stored
re-bisects EXACT + 4 fresh in-band .1448-.1509).

RESULT — D2 SECOND STEP fires; the transition is NOT smooth, NOT a cliff
at 29, and NOT a lottery: the kill->super flip lives in a 2-rank band
INSIDE the window. Same-batch B21 Ti_R curve: k19 .185 KILL -> k21 .156
KILL -> k23 .087 KILL (deepest point of any ng dose) -> k24/wA .365 3/16
PARTIAL -> k26 .804 16/16 SUPER -> k28 .817 SUPER -> k29 .772 SUPER.
Steps: 19->21 -.029, 21->23 -.069, 23->24 +.278, 24->26 +.439 (largest
single transition in the lineage's dose curves), 26->28 +.013, 28->29
-.045 — MONOTONE through the transition, zero dips (lottery cell dead).
D3 refuted: k28 IS super, so the whole-unit story is dead — the unit
completes by rank 26, i.e. THREE ranks BEFORE the window ends; the
L124 "2-step placement unit" resolves into partial-at-24 + complete-at-26
(the transition band = ranks 25-26 = ids {1110, 319}, the two cells
between wA and cutng26). wA's PARTIAL is a stable intermediate, 3rd
batch in band [.35,.50] & kR 3-8: B18 .413/5, B19 .376/4, B21 .365/3.
Ti_L mirrors monotonically DEAD through the transition (.457 at k21 ->
.124 at k29; ng29 L-death anticorrelation already full at k26, .150 0/16)
— the side-flip is part of the SAME step, not a k29-specific effect.

Secondaries ALL green: cutk5 KILL 9th consecutive batch (pooled n=96
0/96 [.0000,.0385] — the lineage's strongest citable); ng19 kill + ng29
super 6th batch each; pooled R4 n=96: ng29 94/96 [.9272,.9943], ng19
3/96 [.0107,.0879], cut58 1/96, full 35/96 (base R noisy distribution
2-10/16 per batch, never cite as a point). Watch: Tr_R killed by EVERY
prefix dose 19-29 (0/16 all — more fragile than Sr_R this batch; Tr
spared only at the cut58 endpoint .488, consistent with L123/L124);
Sr_R killed by every ng dose 5th batch.

Anchors ALL GREEN: C0A vs raw_l113 max 0.0 (56th consecutive chain
anchor), C0A-120/121/122 retained, C0A-123 trimmed to the 4 shared arms
PASS, NEW C0A-124 forward chain PASS FIRST TRY (4 arms x 22 keys x 2
seeds vs raw_l124, incl cutwA) AND NEW C0A-125 PASS FIRST TRY (3 arms vs
raw_l125) — the chain now extends FIVE runs forward free; 7 stored gains
re-bisected EXACT (g_cutwA .143658 promoted to stored-form anchor);
C0B cert PASS on raw_l113 + NEW B20-cert (machinery == results_l125.json
Ti table, all 12 arms) BEFORE any B21 read; P4 af/b65-band green;
fresh prefix gains ALL in .14-.16 band; full-arm B21 bands green;
sanity PASS (cut 16, b65 16/16, cut19 15). Artifacts: l126/{PREREG.md,
static.json, raw_l126.npz, anchors_run.json, results_l126.json, run.out}.
CPU-only; no live changes.

## L127 — contiguous-light-decile: C2 HEAVINESS fires; coherence kills at light mass (tick 151, 11-17)

Card LANE.md ideas-67. Question (L125's confound): scr0 (k19 + ranks
30-39, .0544 extra) SUPER-RAISED while scattered 10s re-rolled — is the
carrier the decile's COHERENCE or its HEAVINESS? Design: hold extra mass
FIXED at the light decile (.0450, ranks 40-49) and vary geometry —
cutcl40 (contiguous, deterministic, .2396) vs cutscrL1/2 (pinned-RNG
scattered 10-of-ranks-30-58 mass-matched, .2406/.2386, extras .0460/
.0439, deltas <=.0011) — with cutscr0 re-run same-batch as the
heavy-coherent context (.2490, stored-form gain from l125). Fresh B22
2601-2616; PREREG first (card amendment: the "~.03" light-decile guess
was WRONG — ranks 40-49 carry .0450; heavy-scattered cell impossible at
matched mass by construction, stays l125's scr1-3 cross-batch).

VERDICT — C2 HEAVINESS (registered cell, clean): NOTHING at .045-extra
supers. cutcl40 (contiguous-light) KILLED .257 0/16 paired dR -.169 —
contiguity buys NOTHING at light mass (worst of the three arms);
cutscrL1 near-super .569 10/16 (sub-criterion on BOTH legs, .031 meanR
/ 2 seeds short); cutscrL2 PARTIAL .356 4/16. scr0 SUPER .611 12/16
(2nd batch; pooled B20+B22 24/32 Wilson [.579,.868]). The refined law:
the kill->super flip's RELIABLE band starts at ~.054 removed-extra mass
(both .0544/.0642 coherent-HEAVY deciles super every batch; ng29 pooled
107/112 [.900,.981]); at .045 ANY geometry re-rolls {KILL, near-super,
PARTIAL} — the L125 lottery at lower mass. Geometry is not the carrier;
the heavy cells' mass is. Sharpened for L128: scr1 (scattered .0476
extra) re-base now PINS the threshold between .045 and .054.

Secondaries: S1 cutk5 KILL 10th consecutive (pooled 0/112 [.000,.033]);
S2 endpoint MISS DISCLOSED — ng19 .230 1/16 missed the kill gate by
.004 on the paired-dR leg (-.196 > -.20; pooled 4/112 its own citable),
ng29 SUPER .718 13/16 7th batch; scrL1 is a BROAD structure-raiser
(Ti_R .569 + Sr_R .590 10/16 + Tr_R .629 11/16 in ONE draw while
killing Ti_L .228 0/16 — the ng29-class side-flip anticorrelation in a
scattered draw); cl40 mirrors it L-restored .553 11/16 / R-dead; Sr_R
killed by every ng dose 6th batch. Fresh gains: cl40 .165077 [OUTSIDE
.14-.16 band DISCLOSED, af-matched], scrL1 .151787, scrL2 .149097.

Anchors ALL GREEN: C0A vs raw_l113 max 0.0 (57th consecutive);
C0A-120/121/122/123/124 retained; EXTENDED C0A-125 (4 arms incl scr0 vs
raw_l125) PASS FIRST TRY; NEW C0A-126 forward chain (3 arms vs
raw_l126) PASS FIRST TRY — chain 6 runs forward; 7 stored gains
re-bisected EXACT (scr0 .15423982501029967 NEW stored-form); C0B on
l113 + NEW B21-cert (all 13 l126 arms) BEFORE any B22 read; P4/bands/
sanity PASS. Build: l127_build.py asserted exact-string transform of
l125_run.py (2 pre-launch instrument catches: B20 docstring count, and
the savez OUTPUT vs absence-list INPUT split on l125/raw_l125.npz — L39
direction class, zero wasted rollouts). Artifacts: banc/l127/
{PREREG.md, static.json, raw_l127.npz, results_l127.json, verdict.out},
l127_run.py CPU 1824 s exit 0, l127_static.py zero-rollout. No live
changes.

## L128 — scr batch rebase: the .045-.0544 band edge is DRAW-STRUCTURED (H1A)
[tick 152, 2026-11-17 22:49-00:0x. Card LANE.md ideas-67 L128 (amended by
L127: scr0 do-not-reroll — it rolled anyway as the uniform arm-set
necessity for the C0A-125 anchor, banked as bonus n=48, PREREG-registered
interpretation). PREREG l128/PREREG.md FIRST; l128_run.py = 21-rep
asserted exact-string transform of l125_run.py (identical 12-arm list,
scr1-3 pinned draws re-derived from l125/static.json EXACT), l128_verdict.py
= 38-rep transform of l127_verdict.py; drift guard caught 2 real pre-launch
misses (resume np.load still pointed at l125's partial — L39 class; the
_prev-loop B20 collision assert) + a build-script regex bug of mine, zero
wasted rollouts. Run exit 0 CPU 1581 s (12 arms x 18 seeds incl anchors
801/901, FRESH B23 2701-2716 asserted absent from all 13 stored npzs).]

VERDICT (H1A): scr1's scattered .0476-extra KILL REPLICATES — B23 meanR
.022 kR 0/16 paired dR -.404 (14/16 down), KILL label with all three legs;
pooled B20+B23 0/32 Wilson [.0000,.1072] = draw-RELIABLE kill (0 seed
survivors on either batch), and it kills BOTH sides (B23 meanL .099 0/16).
scr2 at .0463 extra — .0013 LESS mass — sits PARTIAL in BOTH batches
(.469/.458 meanR, 6/6 kR, pooled 12/32 [.229,.548] = a stable intermediate,
not a lottery draw); scr3 (.0442) partial->high (.425->.557, pooled 17/32
.531, no-super); scr0 (.0544) SUPER 3rd batch (15/16, pooled 39/48
[.681,.898]). So L127's "reliable kill->super band starts ~.054" is
AMENDED: within the .0442-.0476-extra band the OUTCOME CLASS IS
DRAW-SPECIFIC (kill vs partial vs high at near-identical mass, scr1-vs-scr2
gap .0013) but DRAW-RELIABLE (each draw replicates its class across
batches — scr1 kill 0/32, scr2 partial 12/32 with per-batch kR exactly
6/16 = 6, scr0 super 39/48). The discriminator at the band edge is WHICH
cells the draw removes, not how much mass: mass cannot order scr3<scr2<scr1
into partial/partial/kill. What mass DOES own (L125/L127/L128 jointly):
>=.0544 extra super-raises on every draw tried (window, adjacent decile,
max-mass scramble); the coherent-HEAVY story narrows to ">=.0544 any
geometry super" + "the k19+10 scattered family spans kill..high by draw".

Secondaries: S1 cutk5 KILL 11th consecutive batch — pooled 0/128
[.0000,.0291], the lineage's strongest single citable. S2 MISS DISCLOSED:
ng19 misses the KILL label on the paired-dR leg for the THIRD consecutive
batch (-.196 B22, -.180 B23 — direction consistent, bar -.20; meanR .246
kR 0/16 pass the other legs; pooled 4/128 [.0122,.0776] is the honest
citable); ng29 SUPER 16/16 .779 with the L-death mirror intact (L .185
0/16). R4 pooled n=128: full 45/128 [.274,.438] (noisy base, never a
point), ng29 123/128 [.912,.983], cut58 1/128. Sr_R killed by every
scr/ng dose again (6th batch). scr0 B23 L .660 13/16 = bilateral super;
scr1 bilateral kill — the scr family spans the full side-action space at
matched mass. full-arm B23 bands all green (Ti L .438/R .426, Sr in-band);
af all in range; b65 band green.

Anchors ALL GREEN: C0A vs raw_l113 max 0.0 (58th consecutive), C0A-120/
121/122/123(3-shared)/124/126 retained, C0A-125 EXTENDED to ALL 12 arms vs
raw_l125 max 0.0 (22 keys x 12 arms x 2 seeds — strongest chain form yet,
same-arm-list bit-identity), NEW C0A-127 forward chain (9 shared arms vs
raw_l127) PASS FIRST TRY (chain 7 runs forward), 10/10 stored gains
re-bisected EXACT (scr0-3 promoted stored-form), C0B on l113 + NEW B22-cert
(machinery == results_l127.json Ti table, 9 shared arms) BEFORE any B23
read. raw_l128.npz checkpointed pre-analysis. No live changes; CPU-only.
Artifacts: l128/{PREREG.md, results_l128.json, raw_l128.npz, run.out,
verdict.out}, l128_run.py, l128_verdict.py + build scripts.

## L129 — duck-bench mood-nulls (2-rung null ladder, delvetown-owed table)

Date: 2026-11-18, tick 153. PREREG l129/PREREG.md first; zero live changes
(scratch world copies; frozen diffduck15 student; GPU light battery 761 s,
duck verified healthy after: sleepy:low settle trust 1.0, both units
active).

RUNG1 (wiring-vs-routing) — CITED from pinned stored runs (card's
cite-if-exists branch; zero new rollouts): l9a frozen-student ensemble
(MS x5 / BP x5, op-point matched) + l9b fresh students + NULL-DUCK legacy
single-draw pins. Mood SURVIVES full rewiring (frozen exact MS 96.7% /
BP 97.7% vs real 97.3%; fresh-trained-on-null BP-fresh 98.3% ABOVE real;
swat->dop x1.00/x0.97, greet->ser x1.09-1.28); memory COLLAPSES
(peas->KC x0.26 MS / x0.09 BP frozen, x0.22/x0.08 fresh-trained;
peas->DAN x0.59/x0.21 frozen). Claim numbers now programmatic in
results_l129_rung1.json — the duck post's prose no longer outruns data.

RUNG2 (chemistry-vs-degree) — NEW, 4 broadcast-off arms on REAL wiring
(source-in-pop CSR values zeroed, row in-degree renormalized, structure
kept): offSer 2281 cells / 113,929 values; offDop 5,909 / 656,389; offOct
216 / 62,114; offAll 8,406 / 832,432. Anchors A1-A3 ALL GREEN —
spontaneous af .0660 == stored; fingerprints real seed77 max|diff| 0.00e+00
(bit-identical, L85 cert); evaluate real exact/family exact to 1e-7.
- OP PASS every arm (af gap <= .0033 vs .010 bar; alphas .998-1.021).
- F1 PASS: axes' own reads survive broadcast cut — offSer greet->ser .978 /
  peas->ser .950, offDop swat->dop 1.001 => mood reads are READ-LEVEL
  (the modulator cells' own activity carries each axis).
- T1 FAILS (registered-honest): offAll exact tags 91.7% < .943 bar
  (offDop alone 92.3%; offOct alone 97.3% = untouched) while FAMILY stays
  99.4% — the mood surface is wiring-robust but its EXACT bins carry a
  ~5-pt broadcast sensitivity the family bins hide.
- F2 PARTIAL + surprise: offDop peas->KC x0.643 (KC odor lift ~2/3 calyx
  feedforward + ~1/3 DAN broadcast; offSer x0.90, offOct x0.99 = null arm
  clean); peas->DAN crashes to x0.11 (offAll x0.108) — the DAN memory-WRITE
  signal is ~90% recurrent dopaminergic SELF-BROADCAST, not feedforward
  input: a direct population read is not evidence its drive is external.
  Memory is BOTH wiring-placed (rung1) AND broadcast-carried (rung2).

2x2 (the social table, from stored numbers): feelings = wiring-robust,
read-level chemistry, mild exact-bin broadcast sensitivity; memory =
wiring-load-bearing AND dopaminergic-broadcast-carried (KC partial, DAN
deep). Nulls printed both ways.

SOCIAL HANDOFF: results_l129.json (merged) is the citable artifact — the
social lane posts the delvetown table from it under the duck thread
(root 3n2idyfrrje2n, reply under navi-cl 3n2ies6qyvu2n), due Sun Nov 22.
Disclosures live in the json (trust out of battery; fingerprint =
peak-read form not L73 day-battery form; l9a-cert anchors not closure
C0A chain; offDop cuts all 5,909 dop cells incl the 331-cell DAN probe
subset).

Evidence: peabrain-lab/l129/{PREREG.md, rung2_run.py, rung1_assemble.py,
merge_final.py, results_l129_rung1.json, results_l129_rung2.json,
results_l129.json, rung2.out}. Box CLOSED on the measurement side;
posting is the social lane's move.

## L131 — rank-25/26 completion XOR (tick 154, 2026-11-18)

Question (ideas 69): does ONE named cell carry the k24-PARTIAL -> k26-SUPER
flip inside the ng[19:29] window? cutng25 = wA + rank 25 ONLY, on fresh B24
2801-2816, l126 machinery verbatim, PREREG l131/PREREG.md first.

Static (l131_static.py, zero rollouts): rank 25 = id 1110 (m .006436),
rank 26 = id 319 (m .006045), pair delta 3.91e-04; card claim verified
from stored ng_desc ordering (L44 rule). cutng25 n=21784 edges=644084
mass .2350; all l121/l123/l126 pins re-pinned EXACT.

Run (l131_run.py = 50-rep asserted transform of l126_run.py; drift guard
caught 5 unmapped plumbing sites + 2 wrap mismatches pre-launch, zero
wasted rollouts): 12 arms x 18 seeds, CPU 1569s, 1 fresh bisect
(g_cutng25 .145445, in .14-.16 band), 9 stored gains re-bisected EXACT.

Anchors ALL GREEN: C0A vs raw_l113 max 0.0 (59th consecutive);
C0A-120..125 retained; C0A-126 EXTENDED to all 9 shared cut arms vs
raw_l126 PASS FIRST TRY; NEW C0A-127 (6 arms) + C0A-128 (6 arms) PASS
FIRST TRY (chain now 7 runs forward). B23-cert vs results_l128.json Ti
table ALL 12 arms PASS before any B24 read. P4/bands/sanity PASS.

VERDICT — X1 FIRES: rank 25 (id 1110) COMPLETES the kill->super flip
ALONE. B24 curve: k19 KILL .246/1 -> k23 KILL .081/0 (deepest) ->
k24/wA PARTIAL .436/6 (4th batch in band) -> k25 .770 16/16 SUPER ->
k26 .768 16/16 -> k29 .809 16/16. The 24->25 step (+.334) IS the whole
transition; 25->26 = -.002 (319 adds nothing on top). L126's "completes
at k=26" was ONE RANK OFF — the L120 cell-204 pattern replicates at
window scale: a single named DN carries the flip. WHO: id 1110 = DNp33
LEFT side (id 319 = DNpe025 RIGHT): one left-hemisphere DNp-lineage
descending neuron completes the RIGHT-side Ti super-raise while Ti_L
dies through the same step (.276 -> .182 -> .142) — crossed effect,
L60 class. P2 disclosed: 1110/319 are mass-twins (delta 3.9e-04) and
k26-adds-nothing refutes mass-beyond-.2411, but the wA+{319}-alone arm
(would-be k25', .2346) was NOT run — sufficiency of 1110 is proven,
insufficiency of 319-alone is inferred only from its null marginal.
Seeded as L133.

Secondaries: S1 cutk5 KILL 12th consecutive batch, pooled 0/144
[.0000,.0260] (strongest citable). S2 ng19 KILL with the dR leg
PASSING this time (-.206 <= -.20, 3-batch miss pattern broken) + ng29
SUPER 9th, pooled 139/144 [.9213,.9851]. S3 wA partial 4th batch
(.436/6). P3 (L132 prebase, registered in PREREG): transition arms
pooled B21+B24 n=32 — ng23 0/32 KILL-robust, wA 9/32 [.156,.454],
ng26 32/32 [.893,1.0], ng29 32/32 — the transition is 2-batch citable,
and L132's rollout needs are fully delivered by this run (checked off
by pointer). WATCH: Sr_R killed by every ng dose 6th batch; Tr_R killed
by every prefix 19-29.

Artifacts: l131/{static.json,PREREG.md,raw_l131.npz,anchors_run.json,
results_l131.json,run.out,verdict.out}; l131_static.py, l131_build.py,
l131_verdict_build.py, l131_run.py, l131_verdict.py.

## L133 — wA-plus-319-alone: the XOR leg resolves IDENTITY-DOMINATED, not binary (W3 band-edge)
[tick 155, 2026-11-18; PREREG l133/PREREG.md first; l131 machinery verbatim;
fresh B25 2901-2916 (13 arms, CPU 1937s, 10 stored gains EXACT + cutng25p
fresh 0.143527 IN .14-.16 band; static l133/static.json: 25p n=21784 ==
ng25 count, edges 644072, mass .2346, delta vs ng25 = -3.9e-04 = the twin
pair delta -> mass-matched by construction)]
VERDICT: W3 (registered degenerate) BY A BAND EDGE — and the substance is
the best kind of honest. cutng25p (wA + rank 26/id 319 ONLY, 1110 skipped)
lands meanR .508 kR 7/16: the kR leg is INSIDE the partial range 3-8, the
meanR leg misses the [.35,.50] ceiling by .008. Criteria verbatim -> W3;
per the L131 X3 rule, neither W1 nor W2 is read off a band-edge miss.
- W2 (position-thin, both cells complete) DEAD: 319-alone .508/7 vs
  1110-alone .781/16 (ng25 same batch) — 319 does NOT complete.
- W1 (clean binary XOR) fails by the letter; the DECOMPOSITION carries:
  paired-vs-full dR legs: 25p -.017 (4 down/1 up = 319-alone is
  FULL-NEUTRAL, an intermediate between wA .466 and full .525), while
  25 +.256 (9 up/0 down) = 1110 IS the super-raise. The flip is
  IDENTITY-DOMINATED by 1110: steps 24->25p +.042 vs 24->25 +.315;
  319 is REDUNDANT given 1110 (ng26 .747 vs ng25 .781, third batch of
  adds-nothing).
- L-AXIS COHERENCE (new): the Ti_L death rides the SAME cell — ng25
  L .149 0/16 vs 25p L .258 ~ wA .294. One cell (1110 = DNp33-L)
  carries BOTH the R super-raise and the L death; 319 carries neither.
- L131 X1 REPLICATES (S4): ng25 SUPER 2nd batch .781 16/16, pooled
  B24+B25 32/32 Wilson [.893, 1.0] — single-cell sufficiency is
  batch-robust; L126's "completes at 26" stays corrected to k25.
Secondaries: S1 cutk5 KILL 13th consecutive batch, pooled 0/160
[.0000,.0234] (strongest citable); S2 ng19 KILL with the dR leg PASSING
this batch (-.324) + ng29 SUPER 10th pooled 155/160 [.929,.987]; S3 wA
PARTIAL 5th batch (.466/6, band [.35,.50]); Sr_R killed by EVERY ng dose
7th batch (25p .089 0/16); Tr_R killed by all prefix arms. P3 transition
pooled n=48: ng23 0/48, wA 15/48 [.200,.453], ng26 47/48, ng29 48/48.
Anchors ALL GREEN: C0A 60th consecutive max 0.0; C0A-120..128 retained;
NEW C0A-131 forward chain (10 shared arms vs raw_l131) PASS FIRST TRY =
chain 8 runs forward; B24-cert (machinery == results_l131.json Ti table
12/12) BEFORE any B25 read; C0B on l113 PASS; P4 green; full-arm bands
green. 25p verdict labeled SINGLE-BATCH n=16 (L88/L90 discipline — L135
rebase seeded).
Build discipline: l133_build.py 60+ count-asserted reps; drift guard
caught 5 pre-launch (11-space out-dict substring of savez 20-space line —
l123 class; resume np.load path FOURTH L39-class instance, caught by the
residual scan; 2 indent mismatches; 1 probe-string miss) + ONE post-launch
(rollout X-dict 13-space twin of the settle st-dict 14-space line — the
exact l131 per-site lesson, now count-pinned == 2). Zero wasted rollouts
after the X-dict crash was a 1-seed settle crash before first savez.
Artifacts: l133/{static.json, PREREG.md, run.out, verdict.out,
raw_l133.npz, results_l133.json}. No live changes.

## L134 — dnp33-characterization (STATIC, zero rollouts) — tick 156, 2026-11-18

Card: who is gi 1110 (rank-25 ng cell, the L131 X1 carrier) beyond the
type label. l134_static.py = extraction VERBATIM from l133_static.py
(l113 form) with the ladder pins re-asserted FIRST (k19/k29/k58 ==
l121 stored, l126/l131 prefixes, rank twins 1110/319, ladder mass
0.006436 exact, Ti/Tr pool sizes == l92 pins) so any drift trips before
a characterization number is read. Deterministic, no RNG, no rollouts.

IDENTITY — gi 1110 = BANC v626 root 720575941639588127:
super_class descending / cell_class descending_neuron / cell_type
DNp33 / side LEFT / region neck_connective / hemilineage
putative_primary; NT acetylcholine (inline col AND dv_11837016 join
AGREE; non-glutamate asserted — consistent with its ng-ladder
membership); manc_121_match_id 12064; fafb_783_match_id
720575940604103084 — and that id IS PRESENT in the live female v783
brain_graph.pt (the carrier has a live-brain homologue, string-level
cross-join verified in-graph).

TWINS — BANC carries exactly 2 DNp33: the LEFT one is our carrier
(heavy77 rank 31, ng-58 rank 25, ladder |m| 183.96); the RIGHT twin
(gi 928) is IN the closure but NOT heavy — the ladder carrier is
hemisphere-specific, not a type-level fact.

WIRING (closure subnet, all 80 out-edges, |m| 183.96): 87% onto
vnc_intrinsic (70 edges), 13% onto motor (10 edges, targets i2 + iii4,
both LEFT), ZERO onto vnc_sensory, ZERO DIRECT onto any of the 20
antagonist pools (Ti/Tr/Ta/Sr/Pr f/e x L/R). Top |w| targets are LEFT
IN-hemilineage intrinsic cells (IN03B069 x2, IN11B012/B017 x2/B022,
IN19B008, IN12A061). Walking-CPG family string join (IN17A001/
INXXX466/IN16B036/IN19A007/IN19B012): ZERO direct hits — the CPG
family is NOT the private channel. In-edges: 13, ALL from
descending_neuron — DN-driven, no sensory/cord input (L91 dn_into
class).

COMPARATIVE (vs the ng-58, ranks/58, medians): out-degree 80 rank 39
(med 93.5); out-mass 183.96 rank 34 (med 194.7); intrinsic share .87
rank 20 (med .839); pool_direct 0.0 rank 27 — GROUP MEDIAN IS 0.0: NO
heavy added-DN projects directly onto the antagonist pools, L107's
target-tier law at single-cell resolution; motor share .13 rank 9 (med
.017) = the only mild distinction (top-decile direct-motor share for a
heavy ng cell).

MALECNS JOIN ('DNp33' string): 2 cells, L/R mirror. L22 atlas: mixed
purity, top targets hi1 MN .320 z+25.6 / MNad28 .117 z+9.8 / DVMn 1a-c
.106 z+3.5; family weights flex 0.0 (z-1.3) / ext 0.0 (z-0.8) / jump
.171 (z+2.4). CROSS-CONNECTOME CONVERGENCE: DNp33 is NOT a direct
leg-antagonist driver in EITHER connectome — MaleCNS reads it as a
haltere/abdominal/flight-power (steering/posture) channel; in BANC its
leg influence must ride the intrinsic sheet.

SURPRISE (the framing the writeup wants): the X1 carrier is
STATICALLY UNREMARKABLE — mid-pack bulk, zero antagonist contact, no
CPG-family hits, ordinary intrinsic share. Its kill->super causal
power is NOT readable off static wiring; what names it is identity +
position in the ng mass ladder, and (hypothesis, untested) dynamic
routing through the intrinsic sheet. Statics cannot predict this
carrier — a placement claim stays a placement claim.

Artifacts: l134/{static.out, static.json, l134_static.py}. No
rollouts, no RNG, no live changes. LAB-INTENT.md L134 (this section).

## L135 — cutng25p batch rebase (B26; tick 157, 2026-11-18)
PREREG l135/PREREG.md FIRST (uniform-arm-set interpretation registered,
L128 precedent). l135_run.py = count-asserted transform of l133_run.py
(zero fresh bisects — FIRST all-stored run; 3 pre-launch drift catches:
a B25 token inside my own new docstring would have been corrupted by the
global rename, whitelist missed the S133 static-load line, const count 4
not 3; plus ONE post-launch catch, the deferred-xor print KeyError, fixed
in the build + verdict rerun — crash was AFTER B25-cert PASS and BEFORE
results json written, no B26 number pinned on uncertified machinery).
Static re-pin == l133/static.json EXACT (zero rollouts). B26 3001-3016
pre-verified absent from all 16 stored npzs. 13 arms x 18 seeds, CPU
2059s, exit 0. ALL anchors green: C0A 61st consecutive max 0.0,
C0A-120..128 + C0A-131 retained, NEW C0A-133 forward chain (13 arms x 22
keys x 2 seeds vs raw_l133) PASS FIRST TRY = chain 9 runs forward;
11/11 stored gains re-landed EXACT (25p now stored-form .1435265743732452,
stairs max 4.7e-04); B25-cert 13/13 arms vs results_l133.json BEFORE any
B26 read; P4/bands/sanity PASS (sr_b65_kR 0 = the known b65-right quiet
axis, disclosed as before).

VERDICT: registered R fires NEITHER (L55-honest) — but the decomposition
REPLICATES and is now POOLED-CITABLE. B26 drew LOW (full .437/4); 25p
landed meanR .399 kR 5/16 = INSIDE the verbatim PARTIAL band this time
(B25 missed its meanR leg by .008), paired dR -0.038 n_down 3/16 ~ base;
R1's registered window (.45,.60) missed because the BATCH moved, not the
arm. The identity legs: 1110-alone (cutng25) SUPER 3rd batch .754/15 dR
+.317, pooled 47/48 Wilson [.891,.996]; 319-alone (cutng25p) pooled
B25+B26 12/32 p_hat .375 [.229,.547] — Wilson CONTAINS .5, DISJOINT from
ng25's, and mass-matched to 3.9e-04: NEITHER kill-class (worst pooled
cutk5 0/176 [.0000,.0214]) NOR super. 319/DNpe025-R is base-neutral at
mass-match in 2/2 batches (dR -.017/-.038) while twin 1110/DNp33-L
carries the flip (+.256/+.317) — the L131 X1 identity claim closes
batch-robust. Ti_L rides the same cell again (ng25 L .123/0 vs 25p L
.301/2 ~ wA .245/1).
Secondaries: S1 cutk5 KILL 14th consecutive batch, pooled 0/176
[.0000,.0214] — lineage's strongest citable extends; S2 ng19 KILL all
three legs this time (dR -.240), ng29 SUPER 11th batch 170/176 [.9276,
.9843]; S3 wA PARTIAL 6th batch (.383/5, pooled 20/64 [.212,.434]);
S4 ng25 3rd batch. Transition pooled n=64: ng23 0/64, wA 20/64, ng26
63/64, ng29 63/64. Evidence: l135/{results_l135.json, raw_l135.npz,
run.out, verdict.out}; no live changes.

## L136 — transition-law synthesis figure (STATIC, zero rollouts; tick 159, 2026-11-18)

Card: consolidate the L113-L135 kill->super window story into ONE dose-placement
table + ONE hand-built SVG figure, every number re-derived from stored
results_*.json (L44 rule: never from log prose).

- Extraction (l136/l136_extract.py -> l136/plot_data.json): loads the 11 ng-era
  runs (l121-l135), independently re-sums per-run table['Ti'] cells into the
  REGISTERED pool unions, recomputes Wilson 95% at full precision, and asserts
  EQUALITY with l135's stored pooled / pooled_transition blocks — k totals
  (full 66/176, ng19 5/176, ng29 170/176, k5 0/176, cut58 1/176; ng23 0/64,
  wA 20/64, ng26 63/64, ng25 47/48, 25p 12/32), per-batch k_b fields, and
  lb/ub to 1e-12 — ALL GREEN. Dose curve (l135 dose) asserted == its own table
  cells for all 10 keys x {meanR,kR,meanL,kL}; legs == stored; single-batch
  context rungs (21/28 @ l126, 39 @ l121) asserted to their tables; masses:
  l135 mass_prefix + l121 ladder + xor twins (ng25 = wA + m(1110) = .2350 vs
  25p = .2346, delta 3.91e-04). Classification labels from l135/l133 interp
  (stored verdicts) + l121 classification.k58_kill for cut58 — no invented
  thresholds.
- Figure (l136/l136_fig.py -> fig_l136.svg/.png, house dark style +
  rsvg-convert): panel A = ordinal dose curve with pooled Wilson bars and
  classification coloring (the 24->25 step callout: +cell 1110 only, pooled
  47/48); panel B = identity XOR (wA / +1110 / +319) with paired-dR
  annotations; panel C = Ti_L pooled kL/n showing the left pool dies with the
  SAME cell (25 kL 0/48 vs 25p kL 3/32). The figure script RE-VERIFIES every
  drawn value against the source jsons before drawing (its own assert pass).
- QA: eyes-on-pixels UNAVAILABLE (vision endpoint timed out 3x) — substituted
  analytic QA (l136/l136_qa.py, disclosed): entities renderable / 0 bare
  ampersands, anchor-aware overflow scan PASS incl. rotated labels, tick slots
  68px PASS, per-panel ink density A .0123 / B .0146 / C .0316 all in range,
  all 10 pooled k/n numerals present in the text layer. VERDICT PASS.
- Table: l136/table.md (source-derived, see file). The synthesis reads: the
  U-shaped dose law is monotone kill->partial->super through ranks 19-29 with
  the ENTIRE 24->25 transition carried by cell 1110 (DNp33-L) at 3.9e-04 mass
  (319/DNpe025-R base-neutral), then back to kill at full 58-cell removal;
  Ti_L rides 1110 too. Figure + table ready for the publish page.
- No rollouts, no live changes. Sources: results_l121/l126/l133/l135.json.

## L137 — dnp33-dynamic-probe: Zhang static arm + dynamic design card (tick 160, 2026-11-18)

Card: L134 showed first-order statics cannot predict the carrier; tick-158
field fold (Zhang 2610.00690, shared input predicts DN-DN interconnection
in BANC + MaleCNS) supplied the second-order candidate. PREREG
(banc/l137/PREREG.md) registered Z1-Z4 BEFORE any computation; static ran
zero-rollout, deterministic, l134 extraction verbatim (pins green: k-ladder
k19/k29/k58 + rank twins 1110/319 re-asserted).

RESULT — Z1 FIRES ON NEITHER SUBSTRATE (3-leg gate: paired mean, >=31/56
sign test, 58-internal rank):
- closure (PRIMARY, the substrate the dynamics runs on): 1110 fam_mean
  .0025 rank 53/58 vs 319 .0207 rank 21/58; paired diff -.0185, sign
  2/56; core (r1-19) overlap 1110 EXACTLY 0.0 vs 319 .0225 (0/19); twin
  cos 0.0. The carrier is an input-side ISOLATE in the closure: 13
  in-edges (mass 28.2, all-DN per L134), ZERO direct edges to any family
  cell, ZERO shared-in-mass with the always-cut core. 319 (3 in-edges)
  shares input and carries the family's only 2 interconnect edges.
- full-graph (robustness, Zhang's all-partner form): mixed and chance-
  level — 1110 .0194 rank 28 vs 319 .0128 rank 38 (legs i/iii pass) but
  paired sign 22/56 = coin-flip, leg_ii fails. No handle.
- Z4 REGISTERED BRANCH: the mechanism hunt stays DYNAMIC. Disclosed as
  POST-HOC observation (prediction was carrier > twin; the closure went
  the OPPOSITE way): input-side isolation is now the leading structural
  candidate ingredient for WHY removing this one mid-pack cell flips
  kill->super — an un-shared-input cell is not redundant with the cut
  core, so its removal subtracts an independent channel. That is a
  hypothesis for the RUN to test, not a static claim (two substrates,
  two opposite readings = exactly the L134 lesson at second order).

DESIGN CARD SHIPPED (l137/PREREG.md section D, registered now for the
next tick's l137_run): intact-closure clamp/volley grid separating the
two live mechanisms — ACTIVITY (ongoing drive suppresses Ti_R; removal
releases it) vs WIRING (edge footprint + renormalization). Arms: full,
sil1110 (X-clamp, L2 opto form, edges remain), sil319 (neutral-twin
control), silrand1-3 (L78/L91 sham class — no bare-arm credit, arm-minus-
spread), vol1110 + volrand sham, secondary sil24 (population clamp of
ranks 1-24 = class-level clamp twin of cutwA, resolves the L20 class-vs-
cell lesson by direct test). Verdict criteria VERBATIM L118-L131 (KILL/
SUPER/PARTIAL/RESTORE with kR/meanR/paired-dR legs). G1 discriminator
registered (a) clamp reproduces super/partial = ACTIVITY mechanism,
(b) clamp ~ sham spread = WIRING mechanism (named, not failure),
(c) wrong-direction = L35/L38 census re-read. Fresh B27 3101-3116 with
absence precheck; ONE gain (graph identical across clamp arms — drives
enter after settle, L36 law); pre-run viability census (one base rollout,
L95 form) classifies clamp-no-op risk before the grid; C0A chain + B-cert
before any B27 read; dm probe + af assert every arm.

Artifacts: l137/{PREREG.md, static.json, static.out} (l137_static.py);
zero rollouts, no RNG, duck untouched.

## L138 — cross-connectome DNp33 replication: the LADDER does not transfer (static, zero rollouts)

Card LANE.md ideas-72 L138 (referee q#1). PREREG l138/PREREG.md registered FIRST
(S1-S5 + dynamic design card D). Zero rollouts, no RNG; BANC pins re-asserted green
(k-ladder, rank twins 1110/319, K/mass_split) before any L138 number; male side is
the l32 extraction verbatim (superclass cord, consensus_nt, type-name pools).

**S1 — the closure mirror collapses on male.** keep_old 21,516 (== the l32 male
substrate) but keep_new only 21,544: dn_new = **28** cells (BANC: **560**),
added edges 1,942, heavy-50% cut K=9 (0 glut / 9 ng). The BANC ng-58 window
(ranks 20-29, the whole kill->super cliff) has NO male analog — n_ng=9 < 19.

**S2 — DNp33 is reciprocal on male (branch c, stronger).** Male DNp33 = 2 ACh
cells (L/R), dn_into AND dn_proj: 222/224 OUT->cord edges (raw w 1860/2305),
33/37 IN<-cord edges — it sits INSIDE the base substrate, closure-ladder mass
0.0 (its edges are OLD edges). Cause measured: **97.2% of male DNs receive cord
input** (1,277/1,314 dn_into; pure-proj only 28). BANC's 560-cell pure-projecting
cohort — the entire L113-L135 ladder substrate — is an extraction-cohort artifact
of the BANC split, not a cross-connectome structure.

**S4 — triangulation GREEN.** 'DNp33' string-joins in all three graphs: BANC 2
(1110-L carrier + R twin), MaleCNS 2 (L/R), v783 2 (left/right; peabrain/data/
neuron_annotations.tsv); BANC 1110's inline fafb_783_match_id 720575940604103084
IS in live brain_graph.pt. v783 cliff arm structurally impossible (brain-only
graph — no cord/motor antagonist readout), disclosed.

**S5 (context).** Male pools Ti 84/12, Tr 57/11 (flex/ext, both sides) vs BANC
Ti 101/12, Tr 62/48 totals — non-empty everywhere, no equality gate (different
specimens/annotation schemas; male Tr-ext much sparser, disclosed).

**Verdict.** The DNp33 identity cliff is BOUNDED to the BANC closure-extraction
cohort — L94/L107's extraction-rule law now demonstrated at cross-connectome
scale. Design card D (slice B, the male dynamic run) CLOSED PRE-RUN by measured
infeasibility (L125 precedent): branches a/b need a ladder that doesn't exist,
branch c's ng19/ng29 arms are undefined at n_ng=9. For the preprint (L140): the
honest limitation line writes itself — identity decomposition is a single-
specimen, single-extraction-cohort claim; the homolog is named and conserved
(3-graph triangulation), the ladder is not. A male single-cell flip question,
if ever wanted, is a NEW card (different claim class).

Artifacts: banc/l138/{PREREG.md (+ADDENDUM), static.json, static.out, probe.out,
l138_static.py, l138_probe.py}. No live changes; duck healthy (this tick's log).

## L139 — gain-ensemble robustness of the identity cliff (sustain fractions)

Referee question #2 (FlyHack 2610.13018: lesion claims swing across model
seeds/gains) answered by measurement: 6 decisive arms re-run under 5
af-matched jitter gain sets (1% iid multiplicative edge jitter, L2/diffduck15
form, default_rng(2001..2005), applied to the BASE table so the same
per-edge multiplier flows into every arm) + the base set, fresh B28 3201-3216
(absent all 59 stored npzs), SAME seeds every set = paired design (noise
streams are seed-parameterized, independent of W). VERDICT: the cliff's
ENDPOINTS are GAIN-ROBUST, its INTERIOR is GAIN-LABILE. Sustain fractions
(registered classes verbatim): cutng25->SUPER 5/5 ROBUST (the DNp33-L
carrier claim — P1 PASS; mR .65-.80, kR 13-16/16 every set, paired dR
+.15..+.30); cutng23->KILL 4/5 (J5 OTHER = pdR -.197 misses the -.20 leg by
.003 with kR 0/16 — leg-level miss disclosed); cutng29->SUPER 4/5 (J4 drew
NEUTRAL-INT mR .520 kR 9). cutwA->PARTIAL 0/5 and cutng25p->NEUTRAL-INT 0/5:
the transition band's middle stations SCATTER (wA: NEUTRAL/OTHER/OTHER/KILL/
SUPER; 25p: OTHER/PARTIAL/PARTIAL/KILL/SUPER) — under weight jitter the
kill->super interior re-draws (L115/L118 lottery class, now at gain-ensemble
scale), while the single-cell flip endpoint holds. Paired seed flips: 25p
flips 6-9/16 seeds per set vs carrier 25's 2-5 — the twin's outcome is the
gain-sensitive one, the carrier's is not. full kR {8,7,6,4,9,4} stays inside
the 2-10 base spread (P3 pass, no base-regime caveat). SECONDARY (disclosed):
af-matched re-gains under 1% jitter span g_full 0.1487-0.1750 (+-8% — the
in-degree renormalization amplifies weight jitter into gain; the tested
family is BROADER than the critique demanded, making the 5/5 stronger).
Certification: C0B-135 (machinery reproduces l135's stored B26 Ti table for
all 6 shared arms EXACT) + C0A-135 (set-0 bit-identity vs raw_l135 at
801/901, 120 key-arm-seeds, max 0.0e+00 — the ARMS-subset transform proven
clean: dropped arms are spectators, arms evolve independently) + 5 stored
re-bisects EXACT + all stairs < 6.4e-4 + af sanity all green. Referee
answer #2: the identity-carrier result is gain-robust; the dose-curve
interior is gain-sensitive and must be framed as regime-dependent in L140.
Artifacts: l139/{PREREG.md, raw_l139_j0..j5.npz, anchors_j*.json, run_j*.out,
results_l139.json}, l139_run.py (10-rep count-asserted transform of
l135_run.py via l139_build.py, residual scan clean), l139_precheck.py,
l139_verdict.py, l139_driver.sh. Zero live changes.

## L140 — preprint skeleton (tick 163, 2026-11-18)
NOVELTY SWEEP FIRST (card order): 10 arXiv angles x 3 rounds, all-time
relevance-sorted (SS blocked 429 all rounds, disclosed); scripts
paper/sweep_novelty{,2,3}.py. VERDICT: claim class UNCLAIMED — nearest
neighbors ApproxBrain 2611.06929 (search-certified subset necessity, curated
circuit), larval frozen rate operator 2606.17745 (NEW digest in
LANE-RESEARCH: placement-vs-statistics at whole-graph level, methods
convergence cite), VFP 2512.06934 (blockade sims as feature), wet-lab
single-cell induction lineage (sufficiency in the animal). Differentiators
kept: mass-twin XOR + preregistered batch pooling + gain ensemble +
cross-connectome boundary.
DELIVERABLES: paper/DRAFT.md (title candidates, abstract draft, full section
skeleton 1-6 with claims + numbers, honest limitations, data/license notes,
owner-submit gate); paper/numbers.json (every quoted number keyed to stored
results json, extracted by paper/extract_numbers.py — L44 rule); sweep
scripts. Fig 1 = published peabrain-figs/l136_transition_law.png. REMAINING
(explicit TODO in draft): full prose pass, real reference list, figure
polish, venue choice — OWNER REVIEW PARKED (he reads DRAFT.md, then decides;
submission his hands only).
Zero rollouts, zero live changes, CPU-only.

## L141 — l137-run: the DNp33 dynamic probe (WIRING verdict; mechanism decomposed)

Substrate/machinery: l135 verbatim via count-asserted splice transform
(l137_build.py; drift guard caught 2 pre-build bugs in MY OWN builder —
closer-duplication splice + whitespace-drift multi-line rep; residual scan
clean; py_compile ok). 10 arms x 20 seeds CPU 576s; probe 7s; fresh B27
3101-3116 absent from all 36 stored npzs (l137_precheck.py).

RESULT (G1 branch b, PREREG L118-L131 + ADDENDUM A5): the kill->super
completion is WIRING, not ACTIVITY. (1) sil1110 — clamping the ACTIVE
carrier's X to 0 every window step (census: 1110 u_min +0.197, x_mean
.454 — never buried; dm .049 nonzero = channel live, L35 instrument)
lands meanR .376 kR 2/16, IN full's band, paired dR -.088: no super, no
kill, at/below the sham floor's low edge (disclosed). (2) sil319 — the
SILENT twin (x_mean .0033) — .424/6. (3) silrand1-3 spread .075 (kR
5-8): every single-cell clamp/volley inside ±spread = no bare-arm claim
(L91). (4) G2: vol1110 tonic at census amp .2972 — dR +.022 vs volrand
+.077: pushing the carrier's activity moves NOTHING in either
direction. (5) THE DECOMPOSITION: sil24 (clamp ALL ranks 1-24 as a
population) lands PARTIAL .432/5 == the cutwA CUT class (.383/5) AND
kills Ti_L (.119, 0/16) like the cut — so the population's collective
DRIVE carries kill->partial, while the rank-25 completion (partial->
super) rides 1110's EDGE FOOTPRINT/renormalization, unreachable by
activity removal or boost. Two-factor law: DRIVE MASS (population,
activity-mediated) + IDENTITY EDGES (single cell, wiring-mediated).

Certifications ALL GREEN: C0A full/b65@801/901 vs raw_l113 AND raw_l135
max 0.0 (no-bisect ADDENDUM A1 held — machinery bit-identical at stored
gains); PROBE anchor full@3101 same-generator reroll 22 keys max 0.0;
C0B (l113 5-arm atoms) PASS; B-cert: l135's FULL 13-arm Ti table
recomputed from stored raw_l135 == results_l135.json EXACT before any
B27 read (ADDENDUM A2); P4 af green (b65 .1097 in band); sanity b65
16/16. Pooled full Ti_R now n=192: 72/192 Wilson [.3096,.4453].
CLASS-LABEL disclosure: full itself lands in the PARTIAL band on this
quiet batch (m0 .464/6) — the G1 legs carry the verdict (ΔmeanR/kR
gaps), never the class labels alone (L109 rule). Preprint consequence:
the L140 draft gains a mechanism section — identity carrier = edges not
activity, measured. Artifacts: l137/{PREREG.md+ADDENDUM, run.out,
raw_l137.npz, anchors_run.json, results_l137.json, l137_run.py,
l137_verdict.py, build scripts}. No live changes.

## L142 — DNp33 edge-footprint ladder: BOTH directions carry the flip; node-drop ≡ incident-edge-drop BIT-EXACT (2026-11-18, tick 165)

PREREG l142/PREREG.md FIRST (hypotheses before feasibility pins; static
l142_static.py zero-rollout exit 0). Substrate: cutwA window base (n 21785,
644177 edges, pins == l131 EXACT); carrier 1110 PRESENT with all edges.

STATIC: all 80 out-edges inside the window — 70 onto vnc_intrinsic
(.005599 ladder-mass) + 10 onto motor (.000837); 13 in-edges, all-DN
sources, none in the ng-58 family (.000987); eAll (93 edges) selects the
IDENTICAL global edge positions as the cutng25 node drop
(np.array_equal). The card's "renormalization control" was a MIS-CARRY:
the lineage build path has no in-degree renormalization at all (verified
in build code; vals = raw log1p x sign) — L44 lesson applied to card
text; disclosed in PREREG.

RUN (l142_run.py = 11-rep count-asserted transform of l135_run.py,
spectator-arm subset l139-form; build drift guard caught pre-launch: the
noise-dict pattern lives in THREE dicts (settle + rollout settle-phase +
WIN-phase — l123 class), and the resume np.load path (l118/l135 class);
post-launch l131-class def-order catch: the bisect splice first swallowed
def bisect_af_mean itself, crash pre-rollout, zero wasted compute).
B29 3301-3316, 9 arms x 18 seeds, 1187s CPU, exit 0.

RESULTS (Ti_R duty07, criteria VERBATIM L118-L131, B-cert on l135 B26
Ti table EXACT before any B29 read):
- cutwA .377/4 PARTIAL (7th consecutive batch; pooled B21+B24+B25+B26+B29
  24/80 [.211,.408]).
- eOutInt .781/15 SUPER — the 70-edge intrinsic sheet ALONE completes the
  kill->super flip at .0056 removed mass, 12x BELOW L127's .0544
  reliable-super band and below the whole .0442-.0544 lottery band:
  identity beats mass at the cell scale.
- eIn .793/15 SUPER — H3 counter-branch: the 13 IN-edges carry it too,
  INDEPENDENTLY. Two redundant channels; cutting either releases the
  super state. 1110's structural role is not one footprint.
- eOutMot .525/9 — between classes (meanR >= .45 but kR < 12; dR_wA
  +.148, n_up 6/16): a half-step, dose hint (L145 seeded).
- eAll .745/14 == cutng25 .745/14 BIT-IDENTICAL: g_eAll bisected to
  0.1454454553127289 == stored g_cutng25 EXACT, and A-EALL max|d| 0.0e+00
  over mm/xm/22 pools x 801/901 — node-drop ≡ incident-edge-drop through
  6000-step dynamics, exactly. Strongest anchor class in the lineage.
- cutng25 pooled B24+B25+B26+B29 61/64 [.871,.984] (4 batches).
- Ti_L dies with every flipping arm (eOutInt L .082/0, eIn L .105/0) —
  the L131 crossed law rides every channel.

ANCHORS: stored gains re-bisect EXACT (cutwA .14365819573402408,
cutng25 .1454454553127289); C0A-142 {full,b65,cutwA,cutng25} x 22 keys x
801/901 vs raw_l135 max 0.0e+00 (spectator transform proven on shared
arms); B29 absence across 24 stored npzs; P4 green; e-band 5/5 in
.14-.16; sanity b65 16/16.

THE GRID CELL LEFT OPEN (L144 seeded): L141's sil1110 clamp ran on the
INTACT closure (in full's band); L142's cuts run on the PARTIAL base.
sil1110-ON-wA (clamp X[1110]=0 on the cutwA window) is the one missing
cell — activity-vs-edges on the SAME substrate. Note the tension it
resolves: sil1110 clamps activity (out-edges carry ~0 downstream) yet
did not flip the intact base; eOutAll flips the wA base — different
bases, both true; L144 makes the split clean.

Artifacts: l142/{PREREG.md, static.json, static.out, raw_l142.npz,
results_l142.json, run.out, verdict.out}; builders l142_static_build.py,
l142_build.py, l142_vbuild.py. No live changes; duck healthy throughout.

## L143 — preprint mechanism section (fold L141+L139+L142 into DRAFT.md)

Card: LANE.md ideas-74 tick-165 amendment. Static writing tick, zero
rollouts. DRAFT.md v1 (L140) -> v2:

- NEW §2.4 "Mechanism: two factors — drive mass vs identity edges":
  (a) clamp battery (l137/B27): carrier census x_mean .454, clamp live
  (dm .0486), sil1110 dR -.088 inside .075 sham spread, vol1110 +.022 vs
  sham +.077, sil24 = PARTIAL .432/5 + Ti_L death == cutwA cut class;
  (b) edge ladder (l142/B29): eOutInt .781 15/18 SUPER at .0056 mass
  (12x below .0544 band), eIn .793 15/18 SUPER independent (redundant
  channels), eOutMot .525 9/18 half-step, eAll == cutng25 bit-identical
  (gain .1454454553127289 exact, max|d| 0.0); 10-row clamp-vs-cut grid
  TABLE (card's "figure panel if cheap" — markdown table chosen over
  SVG because the vision endpoint was down at L136 and analytic-only QA
  on a brand-new figure would be weaker than a table the verify script
  can check value-by-value; disclosed); interpretation paragraph ties
  the two-factor law to L139 endpoints-vs-interior (labeled reading).
- Abstract: mechanism sentences appended (two factors + 93 edges +
  node≡edge bit-identity), all keyed.
- §2.4->2.5, §2.5->2.6 renumbered; §4 cross-ref fixed; STALE "dynamic
  probe designed but unrun (L141)" limitation replaced by honest
  single-batch disclosure + open-cell (L144) + unread motor dose.
- numbers.json: +11 keys (l137.g1/g2/g3/sil24/pooled_full,
  l142.ti/h2a/h2b/h3/aeall/pooled/window) via extract_numbers.py
  extension; regenerated.
- Verify: paper/l143_verify.py — 21 cited [keys] all resolve (incl
  xor.pair_delta/xor.steps sub-field resolution), every table cell and
  quoted delta/gain equal to stored results jsons EXACTLY; ALL GREEN.
  Two checker-iteration catches (leading-zero style, slice bug) were
  checker bugs, not draft bugs — draft values never wrong.

Artifacts: paper/{DRAFT.md v2, numbers.json, extract_numbers.py,
l143_verify.py}. No live changes. Draft PARKED ON OWNER; submission is
his hands only.

## L144 — sil1110-on-wA-base: the grid cell FLIPS — activity-carried, substrate-gated (2026-11-18, tick 168)

PREREG l144/PREREG.md FIRST (hypotheses both directions, H-EDGE was the
expected branch). Machinery: l144_run.py = count-asserted transform of
l142_run.py (residual scan clean; drift guard caught 2 pre-build
survivors — the os.path.exists resume path, l118 class, + _prevs
whitelist-by-context, l126 law; presence floors pinfixed after 2 honest
builder-assert failures). 6 arms x 18 seeds, 434s CPU, exit 0; clamps =
l137 form VERBATIM (window-loop only, settle clamp-free); sil1110_wA
rides cutwA's stored gain (graph-identity af-match — af equals cutwA's
BIT-EXACT every seed, disclosed in PREREG).

RESULT (Ti duty07, criteria VERBATIM L118-L131, B-cert on l142 B29 Ti
table EXACT before any B30 read):
- **sil1110_wA .622 kR 14/16 SUPER** — clamping X[1110]=0 on the cutwA
  window base flips PARTIAL->SUPER; paired dR vs cutwA **+.189**
  (>> .075 clamp scale, n_up 6/16). H-ACT: the wA-base flip needs only
  1110's SILENCE.
- sil1110 (same clamp, INTACT closure) .392/3, dR_vs_full -.036 — P1
  replication leg holds (L141 B27 recomputed from raw_l137: .376/2 vs
  full .464/6, paired dR -.088 EXACT as published).
- Same intervention, same cell, same certified wiring — only the
  substrate differs, and the verdict INVERTS. L78/L79 portability class
  at its cleanest: an intervention verdict does not transport between
  substrates, even bit-identity-certified ones.
- AMENDS the L141 two-factor law: "rank-25 completion rides 1110's EDGE
  FOOTPRINT, unreachable by activity removal" was measured on the
  INTACT closure — true there, false on the window. On cutwA, 1110's
  residual ACTIVITY (through its edges) holds the super state down:
  silence (.622) and edge-cut (.745, L142 eAll) are two handles on the
  same suppression. Silence carries ~2/3 of the cut's margin (.189 of
  .281); the remainder (.092, just above the .075 scale) is the
  open cell — L148 seeds the predicted-identity arm (silent+edgeless
  == isolated node == cutng25's readout, af-denominator aside).
- cutwA .433/5 PARTIAL (8th consecutive batch; pooled 6 batches
  29/96 [.219,.400]); cutng25 .714/16 (pooled 5 batches 77/80
  [.895,.987]); full .428/6 (batch-drawn band, disclosed); Ti_L stays
  dead on every flipping arm (sil1110_wA .306/1 — crossed law rides
  this channel too, P3).

ANCHORS ALL GREEN at 0.0e+00: stored gains re-bisect EXACT (cutwA
.14365819573402408, cutng25); C0A-144 {full,b65,cutwA,cutng25} x 22
keys x 801/901 vs raw_l135; **FC-142 FORWARD CHAIN** (same 4 arms vs
raw_l142, L120 law — chain extended one run free); **FC-137
clamp-wiring cert** (sil1110 vs raw_l137 bit-identical — the strongest
possible proof my clamp is L141's clamp). B30 absence across 26 npzs
(precheck 69 raws zero-collision). P4 green (b65 band OK).

Artifacts: l144/{PREREG.md, raw_l144.npz, raw_partial.npz,
anchors_run.json, results_l144.json, run.out, verdict.out}; builders
l144_build.py, l144_verdict.py. No live changes; duck healthy
throughout.

## L145 — eOutMot middle-dose (2026-11-19, tick 169)

QUESTION (ideas 75/L145): eOutMot (.525/9 B29) sat BETWEEN partial and
super — dose (graded within-sheet) or lottery? PREREG l145/PREREG.md
FIRST (both directions + sign-count + half-mass proportionality anchors).

VERDICT: NOT A DOSE — a THRESHOLD FOOTPRINT whose halves are inert.
- H-REPLIC counter-branch: eOutMot SUPERs on fresh B31 (.632 kR 12/16,
  paired dR vs cutwA +.201, n_up 8/16) — the B29 middle was batch-drawn.
  Pooled B29+B31 21/32 [.483,.796] sits significantly BETWEEN cutwA
  34/112 ub .394 and cutng25 93/96 lb .912 (non-overlapping CIs both
  sides): the intermediate POSITION is real, at the flip-RATE level.
- H-DOSE FAILS decisively: eMotTop5 +.007 / eMotBot5 -.013 paired dR
  (both inside the .075 clamp floor; order sign count 8/16 = coin flip;
  half-mass proportionality fails). Dropping EITHER 5-edge half does
  NOTHING; dropping all 10 SUPERs — all-or-nothing at the sheet scale,
  L115/L118 re-draw class. The motor footprint is a UNIT, not a graded
  mass channel: intermediate pooled position + non-graded decomposition
  = the position is a re-draw RATE between endpoints, not a mass dose.
  (L139 endpoints-vs-interior, now extended INSIDE the carrier footprint.)
- Static pin (l145/static.json): top-5 = iii4(35)/i2(31)/iv1(20)/
  DVM1a-c(12)/hi1-MN(9) = 62.55% of motor mass, all heavier than every
  bottom-5 edge (i1/DVM/DVM/DLM1-4/iv4) — the split was clean, the null
  is not a tie artifact.
- H-COMBO: eMotIn (10 mot out + 13 in) SUPER .801/15 == eIn's lone
  .793/15 (B29) — in-edge redundancy confirmed on a fresh batch.
- P3 crossed law: Ti_L dies with EVERY flipping arm (mot kL 1, motIn 0,
  cutng25 0/16) — the L-side channel rides every flip, dose split or not.

ANCHORS (all green before any B31 read): C0A-145 vs raw_l135 4 arms x 22
keys x 801/901 max 0.0e+00; FC-142 FORWARD CHAIN — eOutMot bisect
re-landed l142's stored gain EXACT and its 801/901 traces are
BIT-IDENTICAL to raw_l142 (chain L135->L142->L145 extended one run
free); stored gains cutwA/cutng25 EXACT; B-cert TWO certs (l135 B26
cutwA/cutng25 + l142 B29 eOutMot/cutwA/cutng25 Ti tables EXACT) before
any B31 read; B31 3333-3348 absent from 28 stored npzs + standalone
66-npz precheck; P4 green (all e-arms in .14-.16 band); subset law
top5|bot5 == eOutMot positions array_equal; b65 sanity 16/16.

MACHINERY: l145_static.py (verbatim l142 extraction slice + dose tail);
l145_run.py = count-asserted transform of l142_run.py via l145_build.py
(residual scan caught a 5th plumbing site my manual map missed — the
bisect gains-dict signature, l131 law again); l145_verdict.py (l142
helper code verbatim, two B-certs). Run 827s CPU, exit 0. No live
changes; run reaped.


L146 — synapse-floor robustness of the identity cliff: the release IS
floor-3; carrier robust to the strongest admissible floor (STATIC)

QUESTION (tick-167 fold, Kopel 2611.23320): their preregistered BANC
compartment test fails at a 2-3-synapse floor because single-synapse
connections are load-bearing there — is our identity cliff (carrier
1110/DNp33-L, 80 out-edges / 13 in, ladder mass .0064) the class a floor
deletes?

TWO-LAYER ANSWER (PREREG l146/PREREG.md FIRST; ADDENDUM A registered
BEFORE f4 was computed):

1. f2/f3 VACUOUS-BY-RELEASE (L55 degenerate-arm class, disclosed): the
   v626 connections release contains 2,676,592 unique pairs and EVERY
   pair sums to >= 3 — 811,821 exactly at 3, ZERO at 1-2. The 574,733
   single-synapse and 419,792 two-synapse ROWS are intra-pair breakdowns
   (462,170 pairs contain a 1-syn row yet still sum >= 3). Floors f2/f3
   delete NOTHING anywhere (closure 647,953 edges all >= 3; carrier
   80/80; ng-58 6,251 out + 535 in all intact; wA window 644,177
   intact); the re-derived ladder is IDENTICAL (K 77, glut/ng 19/58,
   Jaccard 1.0, carrier/twin ranks 25/26, prefix masses .1946/.2286/
   .235/.2588). The L62 "no min-synapse filter" knob was MOOT: the
   release carries an implicit pair-level floor of 3. Kopel's
   single-synapse sensitivity CANNOT be probed on this dataset — D1's
   "survives" is vacuous in the strong sense and is NOT read as a pass.

2. f4 (first informative floor; deletes 175,858/647,953 = 27.1% of
   closure edges, the 811,821 at-3 pairs release-wide): the CARRIER is
   robust — D4a fires per the registered rule. Ladder re-derives to
   K=73, glut/ng 18/55, heavy-set Jaccard .9231; carrier 1110 rank
   25 -> 21 (moves UP, inside the registered 19-29 window), 69/80
   out-edges survive (86.3%; 11 of 80 sit exactly at 3 — 9 intrinsic +
   2 motor DLM1-4/iv4 — and 1 of the 13 in-edges); twin 319 rank
   26 -> 33: IN cohort but the twin ADJACENCY does not port (disclosed:
   the twin-XOR decomposition's SELECTION is floor-3-contingent; the
   carrier claim is not). Prefix masses re-derive close (ng19 .1988 /
   wA .2342 / ng25 .2405 / ng29 .2649 vs base .1946/.2286/.235/.2588).

VERDICT: the identity cliff's carrier is robust to the strongest floor
this data admits; the Kopel critique is INADMISSIBLE on v626 (implicit
release floor 3) — preprint limitation/methods line + L62 note get the
number. No dynamic arms (registered: statics bound deletions; a dynamic
f4 run would be a new card only if the owner asks).

PINS/VERIFY: S0 pin block ALL GREEN before any L146 number (l145_static
slice verbatim: closure counts, cut K/mass_share, 19/58 split, rank
twins 1110/319, 13 ladder mass/edge pins, carrier 80/70/10/13, motor syn
values == l145 stored EXACT); ladder(1) re-derives the base pins EXACT
before f2/f3/f4 are read; deterministic, zero rollouts, no RNG.
Decision rules D1-D3 + D4a-c registered in PREREG + ADDENDUM A before
their computations.

MACHINERY: l146_static.py (verbatim l145_static.py extraction+pin slice
lines 1-366 + census tail). Static run ~3 min CPU, exit 0. PREPRINT
FOLD QUEUED: L149 card amended with item (c) — the data-floor
disclosure. No live changes.

## L147 — forward-walking channel static join: the field's channel joins EVERY endgame substrate (zero rollouts)

CONTEXT: Dallmann bioRxiv 697356 (tick 167 digest) maps the fly's
forward-walking channel as RRN -> BPN -> {DNg100, DNg97/oDN1} on FlyWire
v783. Card LANE.md L147: does that channel join OUR graphs, and does it
survive the endgame subnet rules (l65 = only DNs that RECEIVE cord
input, L91; closure = into|proj, L107)?

MACHINERY: l147_static.py — PREREG l147/PREREG.md registered FIRST
(before any census number); the first run tripped the DNp33 control pin
and ADDENDUM 1 was registered BEFORE any census number was accepted
(L44 instance #9: my own pre-registered pin text mis-carried '319 twin'
— 319 is the l131 ladder rank-26 MASS twin; the DNp33 homologue pair in
the FULL v626 graph is {928 R, 1110 L}; corrected assert == [928, 1110]).
Corrected rerun exit 0, ~1 min CPU, deterministic. (Tick 171 was
claimed 02:49 but died at the provider 429 before the rerun; completed
this wakeup — no state lost, PREREG + corrected script were already on
disk.)

FINDINGS (all three graphs, exact-string DN law):
- BANC v626: DNg100 2 cells (L gi2 406e/5724s OUT->cord; R gi5
  395e/6776s), DNg97 2 cells (R gi44 164e/2039s; L gi32125 186e/1819s)
  — ALL FOUR dn_into=True => in_l65 AND in_closure. The L91 '400+ cord
  out-edges' memory pin re-derived EXACTLY (406/395). DNp33 control row
  re-derives the L107 decomposition on the same table: 1110-L (the
  carrier) pure_proj => closure-ONLY, 928-R into => l65. The surprise
  rule fired POSITIVE: the field's forward-walking channel survives the
  STRICTEST extraction (l65) where our own L137/L141 carrier (1110)
  does not — the endgame vocabulary can name the Dallmann channel.
- BANC DN totals: 1313 descending, 728 into (55.4%), 1287 proj, 560
  pure_proj (42.6% of projectors dropped by the l65 rule) — vs male
  1277/1314 into (97.2%, L138 pin re-derived EXACT; male pure_proj only
  28). The l65 rule's BITE is graph-specific (BANC keeps whole-brain
  completeness incl. pure descending projectors).
- MaleCNS: DNg100 2/2 (940/939e out), DNg97 2/2 (545/559e), DNp33 2/2
  (222/224e) — all dn_into=True, all in the cord graph.
- v783 (live brain, brain-only): all three names 2/2, super_class
  descending, top_nt acetylcholine, all 6 root ids inside
  proofread_root_ids_783. DNp33 hemibrain_type SAD095. Cord fate
  structurally undefined (no cord in the specimen, L138 precedent).
- RRN/BPN scan: ZERO hits across every name-bearing column of all three
  annotation tables ('rrn'/'roadrunner'/'bpn'); alias scan oDN1/BDN2: 0
  in v783 synonyms|hbt. As pre-registered: vocabulary ABSENCE (circuit
  nicknames), never circuit absence — the channel joins through its DN
  targets, which join 2/2/2 everywhere. DNg97's out-footprint (164-186e)
  is mid-class: far above the DNge046 burial class (16e, L91), below
  DNg100's ~400e.

VERDICT: Dallmann's forward-walking channel sits INSIDE every endgame
substrate (l65/closure/male cord graph/v783 brain). No divergence to
flag; the notable asymmetry is l65-robust forward-walking DNs vs the
l65-dropped identity carrier on the SAME table.

Evidence: banc/l147/{static.json, PREREG.md}; banc/l147_run.out.
No rollouts, no live changes. NEXT: L148.

## L148 — silent-and-edgeless identity arm (2026-11-19, tick 172)

CARD: LANE ideas 77 / L148. The two-factor grid's last open cell: silence
(.622/14 silW, B30) BELOW edge-cut (.745/14 eAll, B29) and node-drop
(.714/16, B30) — is the .09-.12 remainder activity-carried on top of the
cut? Combo arm se0 = eAll graph (93 incident edges dropped, 1110 kept)
+ window-only clamp X[loc 467]=0. Fresh batch B32 3349-3364 (card's
"fresh B31" label predated L145's ship — PREREG rename disclosure, L44
#6). PREREG l148/PREREG.md registered BEFORE the build; l148_run.py =
count-asserted transform of l142_run.py (the residual scan caught a live
resume-path np.load still pointing at l142 + an un-swept B29
absence-assert NameError — both fixed pre-launch; the noise-dict block
lives in THREE dicts, l123 law, one n=3 rep).

RESULT (run 440s CPU exit 0, all anchors 0.0):
- SE-ID BIT-IDENTICAL: se0 == eAll == cutng25 on EVERY stored channel
  (mm/xm/af-set/20 pool keys), all 18 seeds (anchors + 16 fresh). The
  ONLY channel the isolated cell touches is the af DENOMINATOR —
  identical active numerators (2365/2388/2355 across probe seeds) over
  N 21784 vs 21785, exactly the card's "to the af-denominator
  difference". H-ID holds; H-DENOM branch did not fire.
- eAll lone re-pin: .768/15 SUPER on B32 — replicates B29's .745/14;
  pooled B29+B32 = 29/32, lbR .758. The endpoint SUPER is now a
  two-batch fact (L139 endpoints law extended).
- GRID CLOSED: silence is a strict SUBSET of edge-removal on the wA
  base. silW .622 < eAll .768 with se0==eAll bitwise => the remainder
  is SETTLE-HISTORY/EDGE-carried (1110's wiring present through silW's
  clamp-free settle), never window activity on top of the cut. Paired
  dR eAll-vs-wA on B32: +.398, n_up 15/16.
- P3 crossed law: Ti_L dead with every flipping arm (kL 0/16).
- Pooled growth: cutng25 7 batches n=112 (108/112, lb .912); cutwA 8
  batches n=128 (38/128, lb .225).

Anchors: g_cutwA/g_cutng25/g_eAll re-bisects EXACT (g_se0 identity);
C0A-148 4-arm chain vs raw_l135 0.0; FC-142 eAll traces vs raw_l142 0.0
(L142->L148 forward chain); SE-ID + A-EALL in-run 0.0; B-cert x4 BEFORE
any B32 read (l135 B26, l142 B29 incl eAll, l144 B30 incl the silW
clamp arm, l145 B31); B32 absence 79 npzs standalone + 30 in-run; b65
16/16 band ok; e_band ok.

Evidence: banc/l148/{PREREG.md, run.out, verdict.out, anchors_run.json,
results_l148.json, raw_l148.npz}; banc/l148_{build,run,verdict,precheck}
.py. No live changes. NEXT: L149 (draft-fold-144-145 + amendments).

## L149 — draft-fold-144-145 (+146 floor, +148 grid close) [SHIPPED 2026-11-19]

Card L149 (ideas 78) + two disclosed extensions: item (d) = L148 grid
close folded same protocol (tick precedent: L143 folded L142), and a v2
ERROR CORRECTION. Zero rollouts, CPU-only, no live changes.

Folded into paper/DRAFT.md (v3):
(a) §2.4(a) substrate-scope — sil1110 inert on intact closure (B27
    −.088 / B30 replication −.036) but SUPER on cutwA base (.622, 14/16,
    paired +.189, 6/16 up 0 down, 2.5x the .075 clamp scale);
    "activity carries nothing" amended to SUBSTRATE-GATED (v2 inversion
    disclosed in-text).
(b) §2.4(b) + grid table — motor sheet = THRESHOLD FOOTPRINT: top5
    +.007 / bot5 −.013 (both inside .075; order sign 8/16), all-10 SUPER
    .632/12 B31, pooled B29+B31 21/32 [.483,.796] between cutwA 38/128
    ub .381 and cutng25 108/112 lb .912 = re-draw RATE not mass dose;
    eMotIn .801/15 (eIn redundancy fresh). Table: open cell filled
    (.622 SUPER), new rows eMotTop5/eMotBot5/eMotIn/se0 (14 rows).
(c) §4 DATA FLOOR — release re-derived FROM RAW (dv_11842997) and pinned
    as l146/static.json:S0_release (the card's 2,676,592/811,821/
    574,733/462,170 lived only in log prose — L44 violation to quote):
    all pairs sum >=3, zero below; f2/f3 VACUOUS-BY-RELEASE; carrier
    robust to f4 (rank 25->21, 69/80 edges, Jaccard .9231, closure
    647,953->472,095 = 27.1%), twin-XOR selection floor-3-contingent
    (26->33).
(d) §2.4(b)/abstract — se0 == eAll BIT-IDENTICAL (seid_all_max 0.0):
    activity-silence ⊂ edge-removal; silW->eAll margin (~.13) is
    settle-history; eAll replicates B32 .768/15, pooled 29/32 lb .758.

ERROR CORRECTION (v2 -> v3): the L143 grid table's per-arm denominators
were WRONG — /20 (l137 rows) and /18 (l142 rows) instead of the stored
n=16. Caught by Wilson-bound identity: l137 full kR 9 bounds
.3318/.7690 match n=16 exactly (not 20); l142 pooled cutng25 n=64 over
4 named batches = 16/arm; every b65 is 16/16. Root cause: denominators
inherited from LOG PROSE ("20 seeds" in the L141 log line, "18" from the
older era) — the L143 checker's kR-string test was circular (asserted
the string I wrote was in the draft) and could not catch it. l143_verify
patched to corrected strings; new l149_verify.py PROVES n=16 three ways
(pooled arithmetic, Wilson recomputation on 4 arms, b65 saturation) and
guards '/18|/20' out of the draft body. No meanR/kR VALUE was wrong —
only the denominators; all v2 values re-verified unchanged.

Verification: paper/l149_verify.py ALL GREEN (34 cited keys resolve;
every table cell + prose quote == stored jsons; release census + f4 ==
pinned S0_release/static.json; new numbers.json keys == sources);
paper/l143_verify.py ALL GREEN post-patch; extract_numbers.py regen —
38 old keys byte-identical, 12 new (l144.silw/silf, l145.dose/mot/
motin/pooled, l146.release/f4, l148.h_id/seid/eall/pooled). Release
floor derivation: banc/l146/release_floor_addendum.py (deterministic,
zero RNG, ~90 s; numbers matched the card text exactly, now
artifact-pinned).

Evidence: paper/{DRAFT.md v3, numbers.json, extract_numbers.py,
l149_verify.py, l143_verify.py}; banc/l146/static.json:S0_release. No
submission (owner's hands). NEXT FIRST UNCHECKED: L150 (ideas 79).

## L150 — silW batch rebase (+ eMot halves second batch) [SHIPPED 11-19]

PREREG l150/PREREG.md + ADDENDUM 1 (both pre-run). 7 arms x 18 seeds
(ANCH 801/901 + B33 3365-3380), l148 machinery transform (26 count-asserted
reps, residual scan clean, drift guard caught 2 of my own tokens pre-build:
docstring + batch-line comment). Run 615 s CPU, exit 0.

**H1 silW REPLICATES, both legs.** B33 class SUPER .659 kR 14/16 (B30
.622/14 — batch-stable); paired dR vs wA +.281 n_up 9/16 (registered leg
>= +.10); pooled B30+B33 28/32 Wilson lb .719 [.719,.950] (registered
>= 20/32 & lb >= .50). The substrate-gated flip (carrier clamp inert on
intact closure, SUPER on cut base) is now a TWO-BATCH claim; no draft
amendment (non-replication branch did not fire).

**H2 halves: threshold footprint carries at n=32 each.** top5 B33
PARTIAL .460/8 dR +.081, bot5 B33 NONE .350/2 dR -.028 — neither flips;
pooled top5 14/32 lb .282 / bot5 8/32 lb .133, BOTH below the all-10
endpoint (21/32, p-hat .656) and far below cutng25 8-batch lb .922 —
all-or-nothing at the sheet scale holds; top5>bot5 ordering (14 vs 8) is
a disclosed soft hint, not graded mass (L145/L139 endpoints-vs-interior).
No single-batch SUPER flip.

P3 crossed law: silW + cutng25 flip with Ti_L kL 0/16 both. Pooled bases:
cutng25 8-batch 124/128 lb .922; cutwA 9-batch 43/144 ub .378.

**Anchors ALL 0.0 / EXACT:** C0A-150 vs raw_l135 (4 arms x 22 keys x
801/901); FC-144 silW == l144 sil1110_wA @801/901 bit-identical (clamp-
wiring cert); FC-145 eMotTop5/eMotBot5 == raw_l145 @801/901 bit-identical;
fresh bisects re-land l145 stored gains EXACT (.143613/.143671); cutwA/
cutng25 stored-form EXACT; B-cert FIVE tables (l135 B26, l142 B29, l144
B30, l145 B31 incl eMot arms, l148 B32) == stored results EXACT before any
B33 read; B33 absence 81 npz standalone + 32 in-run; b65 16/16; af range
ok; silW af == cutwA af every seed (graph-identity).

**REAL DEFECT CAUGHT (ADDENDUM 1):** l145_static.py's motor_edges_ranked
zips UNRANKED mot_pos with RANKED dst/w/syn columns — stored 'pos' column
pairs the wrong edge (signature: pos column exactly ascending). Probe
(l150_rank_probe.py) pinned both orderings from unchanged data (mtimes
11-14). SCOPE: l145 RUN arms UNAFFECTED (masks from mot_ord; FC-145
bit-identity now proves it); mass splits + top5_share correct (mask-
computed); dst_gi/syn columns were the ranked order (tick-169's
"top5 = iii4/i2/iv1/DVM/hi1" quote was always right); consumed NOWHERE
downstream (draft grep clean). Corrected table pinned l150/static.json;
l145/static.json untouched (immutability). Amended pin = (syn,dst_gi)
columns + pos-set equality + ascending-signature assert.

Cosmetic: run log line says "C0A-148" (label string not in rename set;
json keys c0a150_* correct, final line C0A-150 correct).

Artifacts: l150/{PREREG.md, run.out, raw_l150.npz, raw_partial.npz,
anchors_run.json, results_l150.json, static.json}; l150_run.py;
l150_build.py; l150_verdict.py; l150_precheck.py; l150_rank_probe.py;
l150_static_fix.py. No live changes. NEXT: L151 (substrate-gate statics),
L152 (references/Fig2, owner-gated); L153 seeded (draft v3.1 numbers
refresh incl two-batch silW + corrected-pos disclosure).

## L151 substrate-gate-statics (tick 176, 2026-11-19)
Zero-rollout static decomposition of WHY the carrier's activity is
load-bearing only on the cut base. PREREG l151/PREREG.md FIRST (H-SUB
registered with both legs >= 3). l151_static.py (l142_run extraction
verbatim; all pins GREEN incl 1110 out-edge set array_equal G0/G1, eAll
global positions == cutng25, pool sizes keep-intersected — a raw-mask
count caught 1 Pr_bL cell outside the closure pre-read).
VERDICT: H-SUB REFUTED, cleanly. (1) The carrier is ALREADY the dominant
single DN input into its 70-cell sheet on the INTACT closure: ng58-others
combined 52.03 = 0.33x its 160.04; share-of-DN-sheet 14.47% G0 vs 14.67%
G1 — the cut barely moves its dominance, so input redundancy cannot be
the gate (the clamp is inert exactly where it is already dominant).
(2) The crossed lever is CUT-INVARIANT: one left intermediary (gi75494
IN06B033-L, dn_in 30.86 unchanged, zero cohort input) carries 1110's
2-hop pathway into ALL FIVE right-side pools (Ti_fR/Tr_fR/Ta_aR/Sr_bR/
Pr_bR, shared twohop share .10016 identical G0==G1 to 15 digits) while
Ti_fL has ZERO sheet->pool edges (twohop_dn_total 0.0) — the static
mirror of the L131 crossed law. (3) The only cut-sensitive sheet cell is
gi70458 INXXX467-R (Ti_eL route, dn_in 23.03 -> 19.63) — cohort input
exists only on the extensor route corner, never the flexor route that
flips. CONCLUSION: the substrate gate is DYNAMICAL (which base's regime
routes through the carrier's channel), not a static redundancy
differential — amends the §2.4(a) 'cohort makes it redundant' reading to
'dynamically redundant, statically dominant' (folded, observation label).
Folded: DRAFT v3.1 §2.4(a) + numbers.json l151.{sheet,crossed,verdict}
(old 50 keys byte-identical) + l149_verify section (5) ALL GREEN.
Artifacts: l151/{PREREG.md, static.json, static.out, static.err},
l151_static.py, l151_followup.py. Zero rollouts, no live changes.

## L153 (tick 177, 2026-11-19) — draft v3.2: silW two-batch, halves pooled, bases refreshed, field cites folded

Zero-rollout draft fold (card L153 + research-tick-175 bracket). DRAFT.md
v3.2: (1) silW substrate-gated flip now TWO-BATCH everywhere it is
claimed — abstract sentence, §2.4(a) replication (B33 .659/14, paired
dR +.281, 9/16 up 0 down; pooled B30+B33 28/32 Wilson lb .719), grid row
(.622 / .659, 14, 14/16), §4 batch-thin limitation cell amended (motor+in
combo is now the only single-batch mechanism arm). (2) Halves two-batch
pooled: top5 14/32 [.282,.607], bot5 8/32 [.133,.421], both under the
all-10 rate — "neither half alone" now n=32. (3) Pooled bases refreshed
in §2.2 and §2.4(b): cutng25 124/128 lb .922 (8 batches), cutwA 43/144
[.230,.378] (9 batches); superseded 108/112 and 38/128 strings asserted
GONE from the draft (the verifier now checks absence, not presence —
supersession is itself pinned). (4) §3 data-integrity note: l145
motor_edges_ranked pos-column zip defect, caught by the pre-registered
rank pin, corrected in l150/static.json, run arms bit-identity-certified,
consumed nowhere downstream. (5) Field cites (tick 175): Sapkal bioRxiv
2026.04.29.721658 walking-CPG context bullet (deafferentation survival,
duty->0.5 with order conserved, FeCO modulates-never-necessary, IN12B003
flexor drive = field support for flexor-first pools) + DUCKOPHILA framing
line (independent LIF whole-brain duck; rewired startle collapse 0 of 20
vs intact 1.00 [.91,1.00]; input-null 0.50 encoder-share as the honest
control form). Machinery: extract_numbers.py +2 keys (l150.h1,
l150.pooled), 53 old keys byte-identical on regen; l149_verify.py
extended with section (6) — stored values asserted vs
l150/results_l150.json, full-precision Wilson recomputation on all 5 new
pooled unions (L90 form), n=16 Wilsons on the B33 arms, batch-union
arithmetic (128=8x16, 144=9x16), both-batch grid-row strings, numbers.json
== sources. ALL GREEN (6 sections); l143_verify.py still ALL GREEN. One
own bug caught by the verifier itself: my duckophila "0/20" phrasing
tripped the stale-/20 denominator guard — reworded to "0 of 20" rather
than weakening the guard (guard intact, still fires on the v2 failure
class). Research only, no runtime changes.

## L154 (a) static — 2026-11-19 12:5x (tick 178)
Card ideas 81, Sapkal deprivation arm, stage (a) zero-rollout join.
PREREG FIRST (l154/PREREG.md) incl. format-fact pins from the pre-probe;
run l154_static.py -> l154/static.json. H1 PASS (6/10 names join BANC rm;
Pugliese-5 sums to 24 == l62 pin; manc_121_match_id dead for this vocab;
IN9A002/IN3A006/INXX464/INXX466-2X join NEITHER graph — paper aliases;
card's INXX466 spelling == INXXX466 three-X real). H2 PASS (IN19A007
gaba 6/6 male + 5/5 BANC, no glut-convention dependence; male flexor
61e/2001m vs ext 13/328 = 6.1x). H3 PASS + disclosure (IN12B003 flexor
2.0x extensor male mass, direction holds BANC; but direct flexor mass =
0.8% of its own out-mass — "strong flexor influence" is functional/
mediated, not direct-mass). H4 census pinned both graphs; bonus: NT
table matches Pugliese E/E/E/I/I labels exactly (IN19B012=ACh = family's
strongest DIRECT flexor driver, male 5121 / BANC 4733 — excitatory onto
flexors). GO for (b) dynamic mech-OFF/ON arms next tick, registered form
(l65 b65 substrate, anchor = l150 stored b65 traces bit-identical at
seeds 11/22/33, L85 cert before any off-arm read).

## L154 (2026-11-19, tick 179) — Sapkal deprivation arms (a)+(b) complete

(a) static join shipped tick 178 (H1/H2/H3 PASS, GO). This tick: (b) dynamic.
ADDENDUM 2 registered pre-run: C0A anchor seeds corrected 11/22/33 -> 801/901
(the PREREG mis-carried l150's BISECT anchor seeds into the rollout anchor
slot — re-derived from raw_l150.npz key scan; L44 instance #10, caught
pre-run). B34 = 3401-3416 (absence-verified all npzs on disk, zero
collisions). l154_run.py = count-asserted transform of l150_run.py via
l154_build.py: ARMS -> [b65(on), off]; off aliases b65's CSR object
verbatim (same graph by construction), stored G65=.14 both arms (no
bisects, l144 A1 graph-identity form), mech sinusoid removed ENTIRE run
(2 guards a != "off"); settle_states/bisect block deleted (dead code, main
loop re-implements settle). Drift guard caught 2 of my own builder bugs
pre-rollout (own-output npz in the absence list + comment-on-path-line
whitelist break, L120 input-vs-output direction class).

RUN (CPU 172s + resume tail): C0A-154 b65(on) vs l150 STORED at 801/901
max|d| 0.0e+00 over 22 keys x 2 seeds + af — the off arm consumed ZERO
extra generator draws exactly as designed (noise/X0 shared-stream form).
B34 absence 34 npzs PASS. VERDICT (l154_verdict.py, metric machinery
copied from l94_verdict.py + CERT vs l94 stored cfn duty_07 {11:.073,
22:.517, 33:.2} EXACT + dom_freq analytic self-test 0.7/1.4 Hz):
CLAIM NOT MET — paired dom_freq(off)-dom_freq(on), registered band form,
full WIN: +6/-10, p=.4545. Wet-lab direction (deafferentation SPEEDS)
does not transfer at rate fidelity. Why (diagnostics): global spectral
peak BELOW the 0.3-10 band in 16/16 on vs 11/16 off seeds (untrunc mean
.100 -> .203 Hz, L108 class); anchors 801/901 on .700/.316 vs off
.449/1.089 = per-seed attractor re-draw (L41/L56 lottery; the sensory
sinusoid was the ENTRAINER, L34 frequency-pulling), not a parametric
throttle. Secondary: S07 antiphase SURVIVES off (Ti L .606/R .715, Tr R
.762 — structure needs no sensory drive: MATCHES Sapkal's CPG-central
claim on the structure axis, diverges on frequency); duty07 L/R asym
.013->.047 (symmetrization analog not met, small); dm probe min .026
over 18 seeds (L35 channel-alive). Post-hoc untrunc paired sign 11+/5-
labeled DESCRIPTIVE in results json. Artifacts: l154/{PREREG.md,
static.json, anchors_run.json, raw_l154.npz, results_l154.json}.
Lane: L154 CHECKED; ideas 82 seeded (L155 draft-fold, L156 sub-band
slow-line census). Zero live changes.

## L155 — draft v3.3: the Sapkal negative folded (frequency axis honest, structure axis claimed) [2026-11-19]

Zero-rollout draft fold of L154's honest negative. paper/DRAFT.md v3.3:
(a) §1 Sapkal bullet AMENDMENT — the signed field prediction
(deafferentation speeds the CPG) was preregistered and ran at rate
fidelity: NOT MET (6+/10− of 16, p=.4545 [l154.freq]); removal re-draws
the attractor (anchor seeds .70/.32 Hz on → .45/1.09 off) — sensory
sinusoid was the ENTRAINER; STRUCTURE axis matches the field: S07
antiphase survives mech-OFF on both live sides (Ti L +.61 / R +.72, Tr
R +.76), dead Tr-L wakes (−.08 → +.04) [l154.structure]. (b) §4 NEW
limitation: frequency claims are BAND-RELATIVE (global peak below the
0.3–10 Hz band in 16/16 on vs 11/16 off seeds; untruncated mean
.10 → .20 Hz [l154.band]; sub-band slow-line census queued as L156);
post-hoc untruncated sign 11+/5− labeled descriptive, not
claim-carrying. (c) numbers.json +3 keys (l154.freq/.structure/.band;
55 old keys byte-identical on regen) — S07 means RECOMPUTED from the
stored per-seed duty07 tables in extract_numbers.py, never log prose.
(d) paper/l149_verify.py section (7): every l154 quote asserted as a
DRAFT literal + numerically re-derived (sign counts, p, anchor
roundings, S07 means recomputed independently, band census, posthoc
label, numbers.json==json scalars); l143_verify untouched-green.
Known cosmetics: stored json posthoc string uses ASCII '11+/5-', the
draft renders typographic '11+/5−' (verify checks both sides
separately); house-style quotes carry no leading zero ('+.61'), so
verify asserts literals + tolerance, not f-string round-trips.
Lane: L155 CHECKED (L156 first unchecked, L152 owner-gated). Zero live
changes.

## L156 — sub-band slow-line census (static, zero rollouts; tick 181, 11-19)
PREREG l156/PREREG.md FIRST + ADDENDUM 1 (registered pre-read, after CERT
caught a definition mismatch): stored l154 below_band_census {on:16, off:11}
is reproduced ONLY by the UN-INTERPOLATED bin argmax — off seed 3401's peak
bin lands EXACTLY at 0.3 Hz (not <0.3) while interp gives .298253 (12); the
key was written by a post-verdict inline snippet, no script on disk carries
it — definition recovered from the data (L44 rule); census rows carry BOTH
forms. CERT vs l154 stored: anchors 801/901 x {b65,off} dom_band EXACT,
dom_band/dom_full means EXACT, below {16,11} bin-form, signs 6+/10-.
Census (l156_static.py: 45 raw npz -> 28 carry mm_b65, 0 excluded, ~1,036
mm traces, 5.9 s CPU): b65 baseline global peak BELOW the 0.3 Hz floor in
518/518 traces (28 batches), median .100 Hz, linear-detrend SURVIVE 518/518
(real oscillation, not trend wander), split-half peak agreement 414/518;
intact closure 'full' arm 361/500 below (Wilson lb .6812), survive 331/361,
split-half agreement only 80/361 (slow component frequency-unstable).
VERDICT: the lineage's registered 0.3-10 Hz dom_freq read NEVER sees the
baseline arm's true dominant component — every band-form frequency claim is
band-relative BY CONSTRUCTION; now quantified lineage-wide. Registered
decision rule fired YES: DRAFT v3.4 §4 amended (supersession pinned:
'census is queued (L156)' clause asserted GONE), numbers.json +l156.pooled
(58 old keys byte-identical on regen), l149_verify section (8) ALL GREEN
(pooled counts/Wilson/medians independently recomputed from rows; bin-form
cert cross-file == stored census), l143_verify untouched ALL GREEN.
Artifacts: banc/l156/{PREREG.md,static.json}, banc/l156_static.py.
No rollouts, no live changes.

## L157 — slow-line-carrier census: the .100 Hz line lives in a Tr/Ta/Sr pool subset, NOT clock-wide (zero rollouts)

Card LANE.md ideas 83. PREREG l157/PREREG.md FIRST (+ADDENDUM 1 pre-read:
the PREREG's l150 seed pin 3301-3316 was a B31/L145 mis-carry — actual
l150 npz grid is {801,901,3365-3380}, re-derived from the stored artifact,
L44 instance #11). Reads: 20 antagonist pools + mm + xm per (arm,seed) on
l154 B34 (b65/off) + l150 B33 (b65), L156 machinery verbatim (interp +
bin dual form, detrend survive, split-half, Wilson).

CERT chain ALL GREEN before any new read: analytic dom_freq 0.7/1.4 +
cross-phase estimator self-test (+0.10 rad recovered); CERT-1 l154 stored
anchors/means/below {16,11}/signs {6+,10-} exact; CERT-2 my per-channel
reader on mm reproduces l156/static.json per_arm rows for l154|b65,
l154|off, l150|b65 EXACTLY (7 fields each) — the pool reader IS the
L156 census reader.

RESULT (pooled b65, 36 traces/channel): the slow line is NOT antagonist-
clock-wide. Strong carriers (lb>=.56, 8/20): Tr_fL 34/36 .819, Tr_eL
36/36 .904, Tr_eR 26/36 .560, Ta_aL 32/36 .747, Ta_aR 36/36 .904,
Ta_bR 36/36 .904, Sr_aL 29/36 .650, Sr_bL 33/36 .782 — all Tr/Ta/Sr;
subset median of med_f_below .1002 (draft '.100 Hz' at 3-dec). Ti pair
DEAD (max 6/36, Ti_fR 0/36); Pr pair DEAD (max Pr_bR 20/36, lb .396).
mm and xm 36/36 lb .904 each — mm sees the line because the carrier
pools dominate its mass, not because every pool oscillates. Two carriers
(Tr_eL, Ta_aR) have below-band medians at .025/.019 — even-slower
components inside the same below-band regime (the L156 'less
frequency-stable' caveat, now per-pool).

Registered classifier: C2_readout_only fired on its LITERAL condition
(mm/xm show AND <=10 pools showing) — but the honest structure is the
C2/C3 boundary: a specific 8-pool carrier ensemble inside the aggregate.
Disclosed; the DRAFT v3.5 sentence states the STRUCTURE (subset + Ti/Pr
nulls), not the label. Draft-fold decision rule (exactly one class on
both files + defining lb>=.5): YES.

Descriptive phase reads (registered output, no claim): at each pair's
own slow bin, antagonist phase is heterogeneous — Tr_R antiphase
(+162/+168 deg, 12-13/18), Tr_L IN-phase (+21/+25, 0/18), Sr_aL~bL
antiphase (+164/+165, 15-16/18), Sr_aR~bL-side in-phase — a per-side
heterogeneity that rhymes with L94/L101 per-side wiring facts; labeled
descriptive pending a dedicated design.

FOLD: DRAFT.md v3.5 §4 band-relative bullet + one observation sentence
[157.pooled keyed]; numbers.json +l157.pooled (59 old keys byte-identical
on regen); l149_verify.py section (9) ALL GREEN — pooled dict re-derived
independently from the per-file table, subset asserted all-Tr/Ta/Sr,
Ti<=6/Pr=20/pr lb .396/strong_med recomputed, draft literals pinned;
l143_verify untouched-green. Two in-run verify fixes (tuple+list concat;
strong_med float equality -> 3-dec tolerance, values were .1002 not
exact .1).

Evidence: banc/l157/{PREREG.md (+ADDENDUM 1), static.json, run.out},
banc/l157_static.py; paper/{DRAFT.md v3.5, extract_numbers.py,
numbers.json, l149_verify.py}. Zero rollouts, no live changes.

## L158 — preprint abstract pass: the four load-bearing results stated with keyed numbers; abstract numeric vocabulary frozen (zero rollouts)

Card: DRAFT v3.4's abstract + §1 opening read as v-skeleton. Pass (v3.6):
- R1 sharpened: the collapse/super U-law is now explicitly AT certified
  matched operating points (clause added; endpoints already keyed).
- R4 ADDED (was absent from the abstract): band-relative frequency honesty
  — 518/518 sub-band baseline (28 batches, lb .993, detrend-stable median
  .100 Hz) [l156.pooled]; 16/16 on vs 11/16 mech-off [l154.band]; carrier
  = Tr/Ta/Sr subset 8/20 pools lb>=.56, Ti <=6/36, mm 36/36 [l157.pooled].
- §1 gains a four-result map bullet (all numbers previously quoted).
- Card-term decode disclosed: "operating-point null-collapse" has NO
  numbers.json key as a literal null/rewiring result — read as the U-law
  collapse at af-matched operating points (all its numbers keyed); the
  female-v783 null-duck operating-regime material is NOT this paper's
  claim set and was not added (no-new-numbers rule held).
- paper/l158_verify.py: (1) 14 abstract citations resolve; (2) four result
  markers + §1 map literals; k/n cross-anchor to post-abstract text
  (sole abstract-only cell 20/64, pre-v3, disclosed); U-law endpoints
  Wilson-recomputed vs stored l135 bounds (0/176, 5/176, 170/176, 1/176);
  (3) band numbers independently recomputed from l154/l156/l157 stored
  jsons; (4) NUMERIC VOCABULARY FREEZE — 71-token v3.6 allowlist, any
  future abstract number outside it fails verify.
Verified: l158_verify ALL GREEN; l149_verify ALL GREEN (exit 0, all 9
sections). Zero rollouts. Digest entry updated + pushed.

## L159 — preprint title + prose pass (tick 184, 2026-11-19)

Card: pick the title (candidates 1 vs 3 or a tightened merge), one flow
pass over §2 (carrier vs DNp33-L first-mention discipline, §2.4 (a)/(b)
label ordering, tense), NO number changes of any kind. Zero rollouts.

Shipped (DRAFT v3.7):
1. TITLE PICKED — candidates 1+3 tightened merge: "One cell at the cliff:
   mass-twin controls isolate identity — not removal mass — as the carrier
   of an all-or-none regime transition in a fly connectome model" (hook +
   identity-not-mass from 1, method foreground from 3, "fly connectome
   model" over "fly-cord simulation"; alternates kept in the draft).
2. §2 flow: carrier NAME bound at first §2 mention (twin-XOR row now reads
   "id 1110 (DNp33-L — THE carrier)" / "id 319 (DNpe025-R, the neutral
   twin)"); §2.4 labels reordered factor-first — (a) "Factor 1 — drive
   mass, activity-mediated", (b) "Factor 2 — identity edges" — matching the
   section title's two-factor order; one tense/flow fix ("the v2 open
   cell" → "the one open cell of the v2 grid").
3. Sentence-length outliers HONESTLY CAUGHT by the card's own scan (7
   pre-existing >60-word sentences in abstract/§1, all predating this
   pass): fixed by PUNCTUATION-ONLY splits (semicolons/colons → periods +
   capitalization). Numeric contract PROVEN: abstract+§1 numeric token
   multiset byte-identical pre/post (script assertion, not eyeball).

Verified: l158_verify ALL GREEN (abstract vocabulary freeze intact, 71
tokens); l149_verify ALL GREEN (all 9 sections, every pinned §1/§2
literal survived incl the line-wrap-sensitive 'NOT\n  MET' and
'.70/.32 Hz on → .45/1.09 off'); l143_verify ALL GREEN; NEW
paper/l159_verify.py (sentence scan) PASS — longest sentence now 58w,
zero >60w in abstract/§1. Zero rollouts, no live changes.

## L160 — Fig. 3: slow-line carrier figure, hand-built SVG (tick 185, 2026-11-19)

Card: figure-2-svg (ideas 84). NUMBERING DECISION: shipped as **Fig. 3** —
L152 (seeded earlier, owner-gated) already reserves "Fig 2 = clamp-vs-cut
grid"; the card's "figure-2" name was a seeding artifact, disclosed here.

Built banc/l160/fig_l160.py (l136 house form) + l160_qa.py:
- Panel A: 22 Wilson-lb bars (20 pools + mm/xm, n=36 each), carrier subset
  green (lb ≥ .5 PREREG rule → exactly the 8 named pools), weak amber, dead
  red, mm/xm blue; threshold line at .5; mm "median .100 Hz" annotation;
  family brackets from peripheral_target_type vocabulary.
- Panel B: b65 (518/518, lb .993) vs closure 'full' (361/500, lb .681),
  solid vs dashed-stem+hollow markers (house dash rule), stacked sub-labels
  incl detrend-survive/split-half with BELOW-subset denominators.
- DRAW-TIME ASSERTS all green pre-ink: 22 lbs + 2 l156 arms RECOMPUTED from
  stored k/n (max dev < 1e-12); carrier set, Ti ≤ 6/36, Pr max 20/36,
  mm/xm 36/36, medians (.100/.100/.117), survive/agree pins asserted.

Two in-run defects caught and fixed (disclosed):
1. My own L44 instance #12: l156 survive/agree pins were typed from the LOG
   SENTENCE (361) not the stored dict (331/361) — assert fired, artifact won.
2. L143 denominator class in my own label: panel-B survive/agree printed /n
   (/500) but the counts are within the BELOW-subset → now /below (331/361,
   80/361; b65 unchanged 518/518, 414/518).

QA: analytic ALL GREEN (entities, overflow incl NEW un-anchored-text net,
slot width, ink density, numeral trace 22 k/n + pins) — the un-anchored net
was added because vision caught the panel-B title escaping the canvas, a
text class the anchored-only l136 regex missed. EYES-ON-PIXELS: vision
pass 1 found 4 real defects (threshold label occluded by mm bars; median
annotation same-color-on-own-bar = invisible; panel-B title off-canvas;
solid/dashed legend claim not visible since b65 CI collapses at k=n) — all
fixed (label left, FG annotation, bx 1230 + shortened title, hollow/dashed
closure + "CI collapses at k=n" note), vision pass 2 verdict CLEAN.

Shipped: publish/peabrain-figs/l160_slowline_carrier.{png,svg}; DRAFT.md §4
gains "(Fig. 3)" after [l157.pooled] (no numbers added). Post-edit verifies:
l158_verify + l149_verify + l143_verify + l159_verify ALL GREEN (exit 0).
Zero rollouts, no live changes.

## L152 — references + Fig. 2 (owner-gated card, opened in-chat; in-session Miso with owner present, 2026-11-19)
Owner gate opened by the owner ("let's keep working on it"). CLAIM logged to LANE-LOG pre-work (21:33) so the hourly tick skipped it. REFERENCES: 13 entries, each primary-source verified this session (5 arXiv abs pages via web extract; Nature/PubMed/Cell pages for flyvis, Shiu, Pugliese, MaleCNS-Berg; the BANC project README for Bates Nature doi + Dataverse; Dallmann via the NSF PAR fulltext + Pugliese ref list) — paper/references.bib + DRAFT.md References section; card's ten (flyvis, Minnick, ApproxBrain, FlyHack, Pugliese, larval operator, BANC, MaleCNS, Kopel, Dallmann) + substrate three (Shiu, FlyWire v783, Schlegel annotations). The l149 stale-denominator guards shaped formatting: bioRxiv in dotted date.number form (no slash-year substrings). FIG. 2: l152_fig2.py hand-built SVG (house One Dark, l136/l160 form) — dashed ACTIVITY family (intact base: sil1110 x2 batches, vol1110, sil24) vs solid WIRING family (cutwA base: cutwA 43/144, silW 28/32, cutng25 124/128, eOutInt, eIn, eOutMot 21/32, eMotTop5 14/32, eMotBot5 8/32, eMotIn, eAll 29/32) + se0 as an open twin of eAll (bit-identical per l148.h_id); substrate-gate arrow from stored paired deltas (−.036 intact vs +.189 cut base). Pre-ink asserts: every value vs numbers.json, Wilson lb/ub recomputed dev<1e-12 on all 7 pooled whiskers, gate legs (in_full_band, n_down 0, b33_class SUPER) asserted. numbers.json +l137.vol1110 (61 keys, 60 prior byte-identical on regen; extract_numbers.py extended in house put() style). Vision endpoint down 2x → analytic QA substituted + DISCLOSED (l152_qa.py: XML validity, canvas bounds with rotated-label exemption, same-row collision net, dot-vs-stored-meanR sampling); the net caught 2 real defect classes pre-ink (subtitle off-canvas; adjacent x-label collisions at 77px slots) — fixed (two-line subtitle, bare k/n subs, trimmed footer), QA ALL GREEN. Two self-caught builder bugs also fixed (dead scaffolding loop; missing quote in an annotation attr — caught by rsvg XML parse). Post-edit gates: l143_verify, l149_verify (all 9 sections), l158_verify (71-token freeze intact), l159_verify (0 sentences >60w) ALL GREEN. Figure published publish/peabrain-figs/l152_clamp_cut_grid.{png,svg}. Research only, no live changes, no submission.

## L161 — claim-to-artifact map (research-only, zero rollouts; tick 187, 2026-11-19)
Card: release-form README mapping every DRAFT claim -> script + results/static
json + verify section. Shipped paper/CLAIM-MAP.md: path roots (LAB banc/ +
paper/, WEB peabrain-figs/), key-resolution convention (dotted walk + the
abstract's pooled.<bare> shorthand), a 15-row §-by-§ claim table (draft locus
-> keys -> lane block), 18 lane blocks B1-B18 each carrying scripts, stored
artifacts incl raw npz + anchors + PREREG, verify sections (l143 §1-§3,
l149 §1-§9, l158/l159, per-lane publish/verify scripts, draw-time asserts),
figures + references rows, and a re-verify command list. Methods-constant
DISCLOSURE: the "< 6.4e-4" staircase-residual ceiling is a prose constant not
itself stored anywhere — largest |af_final-target| printed across lane run
logs is 5.23e-04 (e.g. banc/l150/run.out af_final 0.109035 vs target 0.10906);
flagged in the map as a candidate one-word tighten for the next owner-gated
prose pass, NO draft edit made (card is map-only).
NEW paper/l161_verify.py (6 checks, ALL GREEN): (1) draft [key] coverage via
comma-aware bracket parse + l149 dotted resolver + shorthand — 51 root keys,
5 bare arm names resolved via pooled.<tok>; (2) map registry == numbers.json
61 keys bidirectional; (3) all 142 backticked map paths exist on disk (incl
the 3 published figures under website/publish/peabrain-figs/); (4) provenance
re-walk of every walkable src: 48 walked exact (tol 1e-3), 1 star-walk
(gains.*.full multiset), 1 kencode (l137.pooled_full n=192 from key 'k192'),
19 renamed-path DISCLOSED (values verified present in src under drifted
names: 15 exact e.g. dR <- legs.mean_paired_dR, 4 rounded<=5e-4 l151.sheet
ratios), 1 derived-bool (l142.aeall.gains_equal=True, exact float pair in
src), 11 declared-not-walkable (prose subpaths in src strings) — 61/61
accounted; (5) §1 four-result keys 6/6 in map + cited + src exists; (6) all
18 §-table block refs defined. Self-caught during build: ellipsis bullets
backticked would false-fail path check (fixed pre-run); l149's single-token
regex is blind to comma-list brackets — the comma-aware parser here covers
the 4 keys that hid inside them (l150.pooled.eMotTop5/eMotBot5 etc.).
Post-edit: l149/l143/l158/l159 verifies ALL GREEN, numbers.json untouched.
Zero rollouts, no live changes.

## L162 — slow-line ORIGIN probe: the .100 Hz line is EVOKED, echo-locked (2026-11-20, tick 188)

Card (ideas 84): one shared clock or independent per-pool oscillators?
Static, zero rollouts, read-only over l154/raw_l154.npz (B34) +
l150/raw_l150.npz (B33); PREREG `banc/l162/PREREG.md` registered FIRST,
then THREE addenda, each one disclosing a caught defect:

- ADDENDUM 1 (pre-read, L44 class): the PREREG's CONTROL set was typed
  from L157's prose ("Ti dead, Pr dead") and missed **Tr_fR (0/36)** — nine
  dead pools, not eight. Caught by the registered CERT-4 assert before any
  instrument output; control pair count 28 -> 36, no registered bar touched.
- ADDENDUM 2 (post-I1, pre-residual): the registered seed-shuffled MSC
  null is **CONTAMINATED**. Carrier matched MSC .660/.719 but shuffled
  .46-.93, so 0/28 pairs clear the 2x bar and the registered rule returns
  "D2_independent, fold YES" — a **DEGENERATE pass (L55 class)**, NOT
  reported as a finding. Mechanism: a seed-shuffle is an independence null
  only if each channel's phase is per-rollout random; I2 showed the
  opposite at ceiling (carrier-pair PLV .941-.995, Rayleigh p <= 1.4e-14,
  28/28 locked vs 10/36 control), so the null arm carries the same
  time-origin-locked component as the matched arm and the ratio is pinned
  near 1 by construction.
- ADDENDUM 3 (CERT-5 fired, pre-data): the replacement residual
  instrument was ALSO degenerate and its own analytic self-test killed it
  before any data read — at a single Fourier bin the ensemble-mean-
  subtracted residual of a jittered oscillator is RANK-1 (same waveform,
  seed-dependent coefficient) and MSC is scale-invariant, so MSC == 1 in
  BOTH arms (shared ratio 1.00 vs the registered >= 2).

**The well-posed instrument and the result.** If each pool's own .100 Hz
phase is locked to the rollout time origin there is no per-rollout phase
freedom to share, and the card's dichotomy is not a distinction this
ensemble expresses. So measure that directly:

- I4' PLV_self (per channel, 36 pooled b65 seeds, full-trace bin 6 = .100 Hz
  exactly): carrier median **.9838 / .9840** (l154 / l150), per-pool .962-.997,
  circular SD 4.4-17.2 deg; evoked fraction |mean X|^2 / mean|X|^2 = .867-.988.
  Verdict **E1_evoked_dichotomy_not_expressed** (CERT-6: instrument separates
  pinned 1.0000 from free-running 4.5e-17).
- I6 within-rollout coherence vs the DEAD-POOL arm + the analytic 1/K floor
  (K=5 Welch segments, 20 s, 50% overlap, segment bin 2 = .100 Hz exactly):
  23/28 carrier pairs at matched MSC >= .5 (l154 23, l150 24) median .696,
  vs 2/36 dead-pool pairs median .185 — the control arm sits ON the analytic
  independence floor .200 (calibration check passed). Labelled
  **F1_carrier_coherent, DESCRIPTIVE-STRONG, not a pre-registered pass**:
  both components were registered (.5 absolute bar; carrier-vs-control median
  clause) but the recombination was written with the table in hand.
  **NO draft edit this tick** (ADDENDUM 3 binding); held-out re-basing queued.
- **Off-arm kicker (descriptive, strongest new handle):** in the l154 **off**
  arm the carrier median PLV_self collapses to **.186** and mm's evoked
  fraction to **.072** (vs .979 in b65). The slow line's phase lock is
  **ECHO-dependent** — with the b65 echo the .100 Hz component is an evoked,
  time-origin-pinned response; without it there is no reproducible phase.
  The line is not a free-running cord clock in this substrate.
- Refinement of L157: phase locking is BROADER than dominance. Pools L157
  scored dead on dominant-frequency (Ti_fL .947, Tr_fR .929, Pr_aR .933,
  Pr_bR .986) carry a strongly phase-locked .100 Hz COMPONENT — the carrier
  census measured which pools the line DOMINATES, never which pools contain
  it. Genuinely free pools exist too (Pr_bL .033, Pr_aL .159, Sr_aR .015).
- I3 (frequency concordance) withdrawn as uninformative as registered: the
  within-seed SD across carriers (.112 Hz) mixes seeds whose dominant line
  is the FAST component, so it never measured concordance.

Artifacts: `banc/l162/PREREG.md` (+3 addenda), `l162_static.py` ->
`l162/static.json` + `run.out` (I1/I2, CERT-1..4 incl CERT-2 = l157 pooled
rows reproduced EXACTLY on all 22 channels), `l162b_residual.py` ->
`l162/residual.out` (CERT-5 failure, instrument withdrawn, exit 1 by
design), `l162c_phase.py` -> `l162/addendum3.json` + `addendum3.out`
(CERT-6, I4'/I5/I6). Zero rollouts, no live changes, DRAFT + numbers.json
untouched (all five paper verifies ALL GREEN post-tick).

## L167 stage (a) — fable-5.2 referee report adjudicated (2026-11-20)

External peer review arrived (paper/review_fable.md, 12 major issues, major
revision). Stage (a) = adjudicate every issue against OUR OWN stored artifacts.
PREREG banc/l167/PREREG.md registered the verdict vocabulary and the evidence
rule (reviewer probe outputs are CLAIMS, not evidence) before any read.

VERDICT: 12/12 CONFIRMED at least in direction, zero REFUTED. Full table with
per-issue artifact paths: banc/l167/ADJUDICATION.md (+ adjudication.json,
run.out). Highlights, all re-derived here from our jsons/code:
 - I1 our own cutscr0 = 39/48 [.681,.898] right-side over 3 batches, kL also
   high, carrier excluded => SUFFICIENT, not unique; absent from draft+ledger.
 - I3 drive is chopped 500-of-900 in code; Methods states neither the chop nor
   any waveform. Converges with our own L162 (evoked + echo-locked).
 - I4 flip arms re-bisected +1.06..+1.30% vs cutwA, non-flip +-0.03%, eOutMot
   -0.57%; silW flips at UNCHANGED gain => real untested confound, not the
   whole mechanism.
 - I5 per-set Fisher: carrier-vs-twin clear in 3 of 5 jitter sets (16v5 7e-5,
   13v6 .029, 14v0 ~0; 16v13 .23, 13v13 1.0).
 - I6 cohort array defined 1x BEFORE the floor loop, 0x inside => floor
   robustness is frozen-membership-conditional.
 - I7 twin-vs-base Fisher p=.406; "-.088 inside the .075 sham spread" is false
   on its face; l156 = 518 traces from 449 UNIQUE seeds.
 - I9 on the lesion arms every non-tibia pair is exactly 0/16 both sides.
Two issues carry REVIEWER-REPORTED components (I2 matched-floor male ladder,
I6 floor-4 re-derived membership) barred from the draft until we reproduce them.

FIVE DEFECTS IN MY OWN ADJUDICATION SCRIPT, all caught pre-report (run 1
printed 12 confident verdicts; 4 had no data behind them, 1 self-contradicted):
empty-collection interpolation (I5 "0/0 sets"), title-block-instead-of-abstract
locator (I8/I11), a 2,600-char cap truncating section 2.4 (I10), a regex
matching a COMMENT and inverting the finding (I6), and a `duty` false positive
making I3 contradict itself. Transferable rule: a verdict-table script needs
the same locator/assert discipline as a metric script — anchor every
grep-shaped read, length-assert every located span, and assert any interpolated
collection non-empty, or the table reads confident where it is blind.

No DRAFT.md / numbers.json edit this stage (mtimes unchanged), no rollouts, no
figure redraw, reviewer's rewritten abstract untouched. Response cards seeded
as LANE.md ideas 87 (L168-L174). All five paper verify scripts ALL GREEN after.


## L168 — scramble controls into the manuscript; uniqueness re-scoped to set-dependent sufficiency (2026-11-20, tick 190)

Card: LANE.md ideas-87 L168 (referee response #1). PREREG banc/l168/PREREG.md
registered FIRST with decision branches D1/D2/D3 and the L167 evidence rule
(no referee number may enter the draft). Zero rollouts — a fold of arms the
lane already ran in L125/L127/L128.

QUESTION the card answers: a single-cell identity claim invites the obvious
objection "what about a DIFFERENT cohort of the same mass that does not
contain the carrier?". Seven such carrier-free cohorts exist (ranks 30-58 of
the removal-mass ladder, each mass-matched to the k=29 window at .2588).

MEASURED (re-derived from stored table.Ti rows, l168_pools.py):
  arm        mass   extra   nb   right          left
  cutscr0    .2490  .0544   3    39/48 [.681,.898]  35/48 [.590,.834]
  cutscr3    .2388  .0442   2    17/32 [.364,.691]  12/32 [.229,.547]
  cutscr2    .2409  .0463   2    12/32 [.229,.547]  23/32 [.546,.844]
  cutscrL1   .2406  .0460   1    10/16 [.386,.815]   0/16 [.000,.194]
  cutscrL2   .2386  .0439   1     4/16 [.102,.495]   9/16 [.332,.769]
  cutcl40    .2396  .0450   1     0/16 [.000,.194]  11/16 [.444,.858]
  cutscr1    .2422  .0476   2     0/32 [.000,.107]   0/32 [.000,.107]
  full base    -      -     3    16/48 [.217,.475]  15/48 [.199,.453]

VERDICT: rule D3 (heterogeneous) fired. Exactly one carrier-free cohort
reaches SUPER on the right, so the carrier is SUFFICIENT, not unique. The
ordering is NOT mass: the second-heaviest set (cutscr1 .0476) kills outright
while two lighter sets (.0442, .0460) sit well above it. And the one scramble
that supers raises BOTH sides above the base band, so it never reproduces the
carrier's CROSSED right-up/left-down signature — same class, different state.
What the carrier owns is sufficiency plus the crossed state, not exclusivity.

FOLDED: DRAFT v3.8 — title re-scoped ("Sufficient, not unique: mass-twin
controls isolate cell identity — not removal mass — as A carrier of ...",
v3.7 title retained as retired alternate (0) with its reason), abstract
sufficiency sentences, §1 result-2 amendment, and a new §2.2 scramble-control
subsection (7-row table + 3 numbered consequences). numbers.json +4 keys
(l168.scr/base/window_mass/verdict), 61 old keys byte-identical on regen.
CLAIM-MAP.md +B19, l161_verify bidirectional 65/65.

METHOD NOTES worth keeping:
- The honest branch was the one I did NOT expect. D1 ("context-dependent
  sufficiency", the card's own wording) would have been a softer and LESS
  accurate claim than what the data support: the family is heterogeneous at
  matched mass, so SET-dependent is the correct word. Registering three
  branches made the stronger wording available instead of inheriting the
  card's phrasing by default.
- A re-scope needs a CONTRACT, not just an edit. l158_verify's abstract
  vocabulary freeze was deliberately re-cut to v3.8 with the seven scramble
  tokens marked REQUIRED, and both l149 §10 and l158 (4b) now fail on any
  affirmative uniqueness claim returning to title/abstract/§1/§2.2. An
  honesty fix that is not gated is one careless prose pass from reverting.
- The fuzzy patch matcher silently DROPPED a certified literal ("CONTAINS
  .5") from the abstract while editing the neighbouring sentence — caught by
  reading the returned diff, not by a verify (l149 would have caught it, but
  the point is the diff is the cheap check). Known house pitfall, second
  instance on prose edits: read the diff of every fuzzy match on a line that
  carries pinned literals.
- Claim (3) is asserted IN THE DATA, not in prose: l149 §10 requires
  cutscr0's pooled lb to exceed the base band's ub on BOTH sides before the
  "raises both sides" sentence is allowed to stand.

VERIFIED: CERT-1..4 green pre-verdict (24 stored side-bounds == n=16 Wilson
<1e-9; our pools == stored l128 pooled_scr rows <1e-12 incl per-batch
decomposition; stored 2-batch pooled_scr0 == our 3-batch prefix; masses
cross-file consistent). l149_verify (10 sections) / l143 / l158 / l159 / l161
ALL GREEN. Digest pushed 98d46584..743d30ae, remote blob sha256 a28e89a5
byte-identical after base64-decode. No live changes.

## L169 stage (a) — the gain-swap 2x2 (2026-11-20, tick 191)

Referee response card #2 (L167 issue I4). The confound: every arm is
re-gained to a matched active fraction and the FLIP arms sit +1.06-1.30%
above g_cutwA while non-flip arms sit at +-0.03%, so on the published
diagonal "carrier removed" and "slightly higher gain" are confounded.

Design: the off-diagonal of {graph} x {gain}. Two new arms, each the twin's
CSR object verbatim at the OTHER cell's bisected gain (object-identity
asserted; the only difference is the scalar GAIN):
  wAgN  = cutwA graph   @ g_cutng25 = 0.1454454553127289
  n25gW = cutng25 graph @ g_cutwA   = 0.14365819573402408
Fresh B35 (3417-3432) plus anchors 801/901; the seven inherited l150 arms
ride along (free FC anchors + a third batch each). Paired noise stream, one
X0 draw cloned per arm.

PREREG (banc/l169/PREREG.md) registered first: cells, class bands, the
C0-NT non-triviality probe (a swap arm bit-identical to its own-gain twin
= VOID), the P-af direction (deliberate off-op-point, so the L30 af
identity is re-scoped to a direction prediction), and branches D1 (graph-
tracking) / D2 (gain-tracking) / D3 (mixed, no single-word verdict).

Result: D1. Ti right-side duty on B35, n=16 per cell —
  graph wA   @ g_wA    cutwA   meanR .426 kR  4/16  PARTIAL
  graph wA   @ g_ng25  wAgN    meanR .317 kR  2/16  (no class)
  graph ng25 @ g_wA    n25gW   meanR .702 kR 15/16  SUPER [.717,.989]
  graph ng25 @ g_ng25  cutng25 meanR .753 kR 16/16  SUPER
Paired on the same batch: n25gW +.276 vs cutwA (10/16 up); wAgN -.109
BELOW cutwA (2/16 up). The whole confounded gain step, applied to the
carrier-intact graph, moves the readout the OPPOSITE way to the confound
hypothesis; removing it from the carrier-cut graph does not un-flip it.
With silW (flips at unchanged gain) the confound is bounded from both
sides: a real design asymmetry, not the mechanism.

Disclosures. (1) The swap arms are off the matched op point by only
+-.0010-.0013 in af, because the confound's own magnitude is 1.24% of
gain; the probe is therefore small BY CONSTRUCTION and exactly the size of
the thing being tested. (2) The registered PER-SEED P-af direction holds
in the batch means (wAgN .11039 > .10906 > n25gW .10802) but on only 15 of
18 seeds — per-seed af spread is the size of the gain step. Reported as
PARTIAL rather than rounded up to the mean. (3) C0-NT min separation
1.9e-2, so no dead-channel/arm-leak reading (L35/L39 class).

Free-rider pools (the inherited arms' third/ninth/tenth batches):
silW 42/48 lb .753, cutng25 140/144 lb .931, cutwA 47/160 ub .368,
eMotTop5 19/48, eMotBot5 13/48. These supersede the two-batch figures in
DRAFT §2.4; one-pooled-count-per-arm is L172, not this card.

Anchors: C0A-169 vs raw_l135 (4 shared arms x 22 keys x 2 seeds) 0.0;
FC-144 silW vs raw_l144:sil1110_wA 0.0; FC-145 both motor halves vs
raw_l145 0.0; four fresh bisects reproduce their stored gains EXACT; B35
absent from 36 stored npzs; six-way B-cert (l135 B26, l142 B29, l144 B30,
l145 B31, l148 B32, l150 B33) before any B35 read.

Build note worth carrying: l169_build.py is a count-asserted ADDITIVE
transform of l150_run.py (no arm removed, so the l131 removal plumbing
never came up). The residual scan over CODE lines needed TWO whitelist
refinements — the module docstring's continuation lines do not start with
a quote, and the `_prevs` INPUT absence list is a legitimate
cross-reference to prior runs' npzs (whitelisted by matching a pure
string-literal list element, per the l126 line-context rule). The same
scan surfaced an inherited L120-class direction bug in l150_run.py: it
checked for its OWN raw_partial.npz and then loaded l148's. Fixed in the
l169 copy (both paths l169/).

Artifacts: banc/l169/{PREREG.md, raw_l169.npz, raw_partial.npz,
anchors_run.json, results_l169.json, run.out, run.err, verdict.out,
verify_push.py}; banc/{l169_build.py, l169_run.py, l169_verdict.py}.
Paper: DRAFT.md v3.9 §2.7, extract_numbers.py (+6 l169.* keys, 65 old
byte-identical), l149_verify.py section (11), CLAIM-MAP.md block B20.

## L169 stage (b1) — frozen-vs-rederived floor forms (2026-11-20, tick 192)

Static premise test before building the dynamic f4 machinery. The card's
own premise ("our I6 showed the published robustness is frozen-membership-
only") came from my adjudication script's code-shape heuristic, not from an
artifact — L44 rule, 12th instance. PREREG banc/l169b/PREREG.md registered
four forms (F0 base, F1 frozen-all, F2 frozen-set/re-ordered, F3 fully
re-derived), a CERT block and rule E1/E2/E3 before any computation.

l169b_static.py is a 1-site additive transform of l146_static.py
(l169b_build.py: count-asserted rep, residual scan refusing any surviving
write to the l146 artifact, py_compile), so l146's own pin asserts re-ran as
free certification. 3.3 s CPU, zero rollouts, no RNG.

Rule E1 fired: the I6 scope component is REFUTED. ladder() assigns K,
heav_f and ng_desc_f inside its own body (ast parse) and ladder(4)
reproduces the stored S4_ladder.f4 field-for-field; a genuinely frozen form
returns 25/26 by construction while the artifact carries 21/33. New
decomposition: frozen SET + re-order (F2) already gives 21/33 — the shift is
re-ordering, not turnover (5 out / 1 in, K 77 -> 73, Jaccard 72/78 = .9231).

Disclosed in-run CERT fix: the stored l146/static.json is AUGMENTED after
the fact by l146/release_floor_addendum.py (S0_release), so CERT-1 is a
subset compare over the 10 keys l146_static.py writes plus an assert that
S0_release is the only extra and that the addendum file writes it (L110
class). Two trivial build-time bugs (missing `re` import in the spliced
tail, and the same tail's regex using the un-aliased module) were caught by
the first two runs, fixed in the BUILD script rather than the generated
file so provenance stayed intact.

Design pins for stage (b2) stored in banc/l169b/static.json:pins — the f4
XOR window is cut-first-20 vs cut-first-21 over a re-derived ladder (base
window ports 23 of 24 cells; prefix mass .2061/.2133 vs base .2286/.2350,
so the f4 arm removes LESS mass), carrier footprint 69/80 out + 12/13 in,
f4 mass-nearest twin DNpe005-R rank 22 gap 2.4e-05 (base twin DNpe025-R
falls to rank 33), f4 closure 472,095 edges (27.14% deleted), fresh
af-matched bisect required.

Fold: DRAFT v3.10 §4 DATA FLOOR scope clause, numbers.json +l169b.forms /
+l169b.scope (71 pre-existing keys byte-identical on regen), l149_verify
§12, CLAIM-MAP B21, and a CORRECTION section in l167/ADJUDICATION.md
(review score now 11/12 confirmed + 1 scope-component refuted). The
reviewer's own floor-4 numbers stay REVIEWER-REPORTED and barred.

## L169 stage (b2) — the floor-4 DYNAMIC arm (2026-11-20, lane tick 193)

PREREG banc/l169b2/PREREG.md FIRST: substrate convention (closure node set
VERBATIM, edges filtered to pair-level summed syn_count >= 4 — the stored
l146 ladder convention), three arms over the f4-re-derived ng ladder
(f4wA = cut first 20, carrier intact; f4ng = cut first 21, carrier DNp33-L
gi 1110 at f4 rank 21; f4tw = cut first 20 + the f4 mass-twin DNpe005-R
gi 290, rank 22, mass gap 2.4e-05), fresh per-arm af-matched bisects,
inherited R-side duty classifiers, branches G1-G4 + a vacuous-XOR guard.

REGISTERED BRANCH G2_no_transfer. All three f4 arms sit at kR 0/16
(meanR .043 / .081 / .082, k=0 Wilson ub .194) while the base-substrate
arms reproduce on the SAME B36 seeds (cutng25 SUPER 16/16 meanR .754,
cutwA PARTIAL 3/16 .371, full PARTIAL .475) and the f4ng-vs-f4tw XOR leg
is flat (-.001 paired, 8 up / 8 down). The published floor-4 robustness is
therefore a property of the STATIC ladder, not of the dynamics on the
floored substrate (L94 substrate-rule law, now with a floor instance).

DESCRIPTIVE (post-hoc, no registered claim, separate results key): on the
floored substrate the structure SWITCHES SIDES. f4wA carries meanL .698
kL 16/16 (base cutwA .233 kL 0/16), and there the carrier is still the
lever with an INVERTED sign — removing it costs structure (f4ng meanL
.289, paired -.409, 0 up / 16 down) nearly 3x harder than removing its
mass-matched twin (f4tw .560, paired -.139, 6 up / 9 down). A registered
left-side test is seeded as L175; nothing in the draft's §2 depends on it.

Gains (fresh, never ported): f4wA .150514525, f4ng .162309861, f4tw
.152618986 — the floor deletes 27.14% of closure edges, so the matched
operating point needs MORE gain, and f4ng (carrier removed) needs the most.
Staircase residuals 1.0e-04 / 3.6e-05 / 5.3e-06; rollout-af max offset
4.8e-03 disclosed as a different quantity from the settled bisect af.

Method notes worth keeping:
- The L139 spectator law transfers to the BISECT: restricting settle_states
  to the single arm being read cut 12 arms of settle cost per bisect
  iteration, and the four inherited stored-form bisects landing EXACT
  (g_cutwA / g_cutng25 / g_eMotTop5 / g_eMotBot5) is the certification —
  free, and stronger than an argument.
- A cross-run helper constant typed by hand is still prose: my §13 k=0
  Wilson upper-bound literal was wrong in the 5th decimal
  (.19359580693979172 vs the recomputed .1936076805344365) and the assert
  caught it. Recompute, never retype (L44 class, 13th instance).
- GI_TWIN did not exist in the l169 lineage (only GI_CARRIER); re-derive
  such a constant from the BASE ladder with an assert (ng_desc[25] == 319)
  instead of pasting the number.

## L169 (c1) — design pins and premise tests for the two queued (c) arms (tick 194, 2026-11-20)

PREREG banc/l169c/PREREG.md registered FIRST: the (c) card named two arms
(a degree-preserving rewire of the carrier's edges, and "deletion of the right
homolog 928") and presumed two things it never checked. The (b1) split is
repeated here — premise test before machinery — and both presumptions moved.

Build: l169c_static.py = a 1-SITE ADDITIVE transform of l151_static.py (lines
1-319 VERBATIM + l169c_tail.py), so every L151/L142/L134 pin re-ran as free
certification before any (c1) value was read. Guards: splice anchor
count-asserted at line 320, residual scan refusing any surviving WRITE to a
prior artifact (l151/, l146/), a single asserted json.dump target, py_compile,
and a byte-identity assert that the head prefix is unmodified. 4 s CPU, zero
rollouts, RNG only for the registered rewire draws.

RULE C1 -> C1_independent. gi 928 is in NO cut window, so the deletion arm is
non-vacuous on the G1 cutwA base — and the reason is the interesting part.

RULE C2 -> C2_nonequivalent, failing ONLY the class leg while all three
footprint legs pass: 88 vs 80 closure out-edges (1.1x), out-mass 200.05 vs
183.96 (1.09x), intrinsic share .855 vs .870, tiers 77/11 vs 70/10. The carrier
is a PURE PROJECTOR (dn_proj and not dn_into); 928 RECEIVES cord input, so the
closure-only extraction rule never admits it to dn_new_g and it can never enter
the ranked cohort. The card's "right homolog" is therefore a same-footprint,
DIFFERENT-CLASS cell — which makes the arm a good mass-and-degree control and a
bad mirror control. Anatomy agrees in the direction that matters: destinations
are nearly disjoint (6 shared of 80/88, Jaccard .0370, 5 of 928's targets in
T70) while the direct MOTOR edges mirror the side cleanly (carrier 9 left /
1 right, 928 1 left / 10 right), and NEITHER cell touches any of the 22
antagonist pools directly — both levers are 2-hop, the static mirror of the
L151 crossed law.

RULE C3 -> admissible. Partner pool 64,328 DN->cord rows = 804.1x the carrier's
out-degree; the median draw relocates 80/80 edges; median mass returned to the
carrier's own T70 sheet is 0.0000 of 183.96 (gate <10%; chance share .0070).
Degree-neutrality is asserted EXACTLY per draw: the destination multiset over
every touched row is preserved, 100/100.

Fold: DRAFT v3.12 §2.7 (the superseded "right-homolog" label asserted GONE),
1 numbers.json key (75 old byte-identical), l149_verify §14, CLAIM-MAP B23.
All five paper verifies ALL GREEN; abstract untouched.

Method notes worth keeping:
- A card's own VOCABULARY is a premise. "Right homolog" encoded an assumed
  equivalence; the two cells match on every footprint axis and differ on the
  one axis that decides cohort membership. Test a control's label with the
  same rules you would test its effect (L107/L94 membership class, static).
- A degree-preserving rewire needs a feasibility census BEFORE it is run:
  partner-pool size, median relocation count, and the chance-level return
  mass to the cell's own target sheet. Our chance share (.0070) is what makes
  the 0.0000 median meaningful — report both or neither.
- The cheapest certification available to an additive static transform is the
  verbatim head: 415 scalar fields of the prior run's own output re-derived
  and compared field-for-field, for free, before any new number is read.
  Subset-compare when the stored artifact was augmented later by a second
  script (L110 class; l151's signed_1110_out_G1 is appended after the block).

## L169 stage (c2) — REW + HOM rollout arms (tick 196, 2026-11-20)

PREREG banc/l169c2/PREREG.md FIRST (arms, batch B37 3481-3496, the
inherited R-side classifiers, CERT block, branches R1/R2/R3 + H1/H2).
Build: l169c2_build.py = 21 count-asserted ADDITIVE reps on l169b2_run.py
(the f4 loop idiom made the per-arm plumbing cheap: st/X/noise loops,
bisect gains dict, savez pins) + a residual scan whitelisting the prior
run's dir ONLY as an input PATH literal and only inside docstrings for
prose; the scan's first form flagged six docstring/log-label survivors,
which is the l126 line-context rule (whitelist by context, not by token).

Result. Base reproduces on the fresh batch (cutwA PARTIAL meanR .452 kR
5/16; cutng25 SUPER .786 15/16) so nothing is vacuous. Three registered
degree-preserving rewire draws SPLIT: rew1 SUPER (.724, 16/16, paired
+.272 vs cutwA, 15/16 up), rew2 (.333, 1/16, -.119) and rew3 (.302, 3/16,
-.150) NOT-SUPER and BELOW the carrier-intact base. Draw pool 20/48
[.288,.557] straddles cutwA's [.142,.556]. Registered branch
R2_mass_degree fires on the 2-of-3 majority AND R3_draw_lottery's
pooled-straddle clause is also true — my own PREREG left the precedence
ambiguous, so the honest report is the CONJUNCTION (displacement is not
removal; a single draw's outcome is a lottery). hom (gi 928, 101 incident
edges) NOT-SUPER (.301, 2/16, paired -.150, 13/16 down) => H1_specific:
the flip is not "any heavy DN deletion" on the class axis either.

Not a gain story: all three rewire gains sit ABOVE g_cutwA
(.144464/.145617/.150060 vs .143658) and the readout is NON-MONOTONE in
them (rew3 lowest gain -> .302, rew1 middle -> .724, rew2 highest ->
.333). The first draft of my §15 gate asserted rew3 sat BELOW g_cutwA —
the assert refuted it and the draft sentence was wrong in the same way;
fixed to the non-monotonicity claim both places.

Anchors: FC-169B2 12 inherited arms x 22 keys x 2 seeds vs
l169b2/raw_l169b2.npz max 0.0e+00; C0A-150/FC-144/FC-145/FC-169 all 0.0;
four stored-form bisects EXACT; CERT-REW the in-run 100-draw rewire loop
== l169c/static.json P5/P6 field-for-field (first-5 draws compared as
dicts); CERT-REW-DEGREE the built CSR carries EXACTLY cutwA's 644,177
edges per draw (no coalescing = no multi-edge slipped the swap
bookkeeping), the edge mask is elementwise identical to cutwA's, and the
GLOBAL in-degree bincount is preserved; CERT-HOM 101 incident edges and
n = cutwA - 1; C0-NT(c2) min 1.853e-2; staircase residuals <= 5.9e-4.
Run 1215 s CPU exit 0, raw npz checkpointed before analysis.

Own-catch worth keeping (l121 label-string class, new instance): the §14
gate `'right-homolog' not in draft` reads the WHOLE file, and the v3.12
VERSION BANNER deliberately discloses the label's removal — so the gate
was red from the moment the disclosure was written (banner edited after
tick 194's verify pass). A removal gate must be scoped to the draft BODY;
banners and changelogs are where removals are announced. Both the (14)
and (15) removal gates are now body-scoped with the reason in-source.

Coincidence disclosed: rew3 and hom round to nearly the same batch mean
(.302 / .301) but differ per seed by up to .46 — different arms, checked
in the verifier.

Evidence: banc/l169c2/{PREREG.md, raw_l169c2.npz, anchors_run.json,
results_l169c2.json, run.out, verdict.out}, banc/{l169c2_build.py,
l169c2_run.py, l169c2_verdict_build.py, l169c2_verdict.py}, paper/
{DRAFT.md v3.13, extract_numbers.py, numbers.json (76 old keys
byte-identical + 6 new), l149_verify.py section (15), CLAIM-MAP.md B24}.

## L169 stage (d) — the XOR pair at swapped gains (tick 197, 2026-11-20)

INTENT: close L169 by running the control the title's own claim needs. The
stage-(a) 2x2 tested the cutwA/cutng25 contrast; the twin-XOR pair that
carries the identity claim (cutng25 = carrier gi 1110 removed vs cutng25p =
mass-twin gi 319 removed, 3.9e-04 mass delta) had never been crossed against
its own gain asymmetry — and the twin arm sits at a gain 1.337% BELOW the
carrier arm's (g .143526574 vs .145445455).

DESIGN (PREREG banc/l169d/PREREG.md, registered before any computation):
three new arms on a fresh batch B38 3513-3528 (n=16, absence-verified across
74 stored npzs BEFORE registration) — cutng25p at its OWN gain, bisected in
the STORED-FORM loop so the bisect must reproduce l135's g_cutng25p exactly;
p25gN = the cutng25p CSR by object identity at g_cutng25 (swapped UP);
n25gP = the cutng25 CSR by object identity at g_cutng25p (swapped DOWN).
Branches E0-E3 registered with EXPLICIT precedence (stage (c2) left R2/R3
ambiguous and had to report a conjunction).

RESULT: branch E1_graph_tracking — the strongest of the four. Own-gain
diagonal reproduces on B38 (cutng25 SUPER .798 16/16; cutng25p NOT-SUPER
.477 8/16, paired +.321 16/16 up). Off-diagonal: the twin graph at the
carrier's HIGHER gain does NOT flip (.324, 1/16, paired -.152 below its own
gain) and the carrier graph at the twin's LOWER gain STAYS SUPER (.651,
15/16). Read at FIXED gain the contrast is maximal: +.474 with 16/16 seeds
up at g_cutng25 and +.174 with 12/16 at g_cutng25p — neither column reverses
the ordering. Disclosed: the twin arm sits AT the NOT-SUPER boundary on this
batch (kR exactly 8/16, meanR .477 under the .50 bar), raising a gain helped
NEITHER graph, and the per-seed af direction holds 15/18 and 13/18 (PARTIAL).

METHOD NOTES WORTH KEEPING:
- A new arm whose full per-arm plumbing already exists in the lineage (the
  l131-l169c2 dicts all carry "cutng25p") costs three reps plus a bisect:
  grep the dict key BEFORE writing the transform, and name the new arm with
  the EXISTING key rather than a fresh alias.
- When a prior run already rolled the arm you are adding, its anchor is
  FREE: extending C0A-150's arm tuple from 4 to 5 bit-checked cutng25p
  against l135/raw_l135.npz (max 0.0) — the strongest possible wiring
  certificate for a "new" arm, and it cost one token.
- l149_verify §14's draft slice anchored on the exact prose sentence I
  rewrote in this fold ("Design pins for those two remaining arms"), so a
  deliberate prose improvement broke a PRIOR section's gate. Fixed by
  re-anchoring §14, not by reverting the prose — but the lesson is that
  index()-based slice anchors are prose contracts too: when you edit a
  sentence a verifier slices on, grep the verifiers for it first.
- The fuzzy patch matcher ate a line boundary in the version banner
  ("flips). Branch H1_specific" -> "branch H1_specific"), the known
  LANE.md-anchor pitfall now observed in the DRAFT: re-read every patched
  anchor region.
- CLAIM-MAP's §-by-§ table had NO row for B24 (l161 only checks that
  REFERENCED blocks exist, never that every block is referenced) — added
  rows for B24 and B25; the table now references all 25 blocks.

ARTIFACTS: banc/l169d/{PREREG.md, raw_l169d.npz, anchors_run.json,
results_l169d.json, run.out, verdict.out}, banc/{l169d_build.py,
l169d_run.py, l169d_verdict_build.py, l169d_verdict.py}, paper/
{DRAFT.md v3.14, extract_numbers.py, numbers.json (82 old keys
byte-identical + 5 new), l149_verify.py section (16), CLAIM-MAP.md B25}.

## L170 — male extraction at the MATCHED synapse floor (static, zero rollouts)

PREREG banc/l170/PREREG.md FIRST (M1/M2/M3 + P1-P4 registered before any
floor>=2 number). Feasibility pre-check first per L146/L125: the MaleCNS
significant-only release has min weight 1.0, 0 duplicate ordered pairs,
10,295,463 weight-1 pairs of 25,568,639 -> floor 3 ADMISSIBLE and
non-vacuous (unlike the BANC side, where the same arm class was degenerate).

l170_static.py = purely ADDITIVE transform of l138_static.py via
l170_build.py: head kept VERBATIM (12,691 chars, byte-identity asserted), so
every BANC pin (L92/L107/L121/L131 k-ladder, rank twins 1110/319,
K/mass_split) re-ran as free certification. Residual scan refuses any write
outside l170/, single json.dump target, l138/static.json read-only (mtime
unchanged). CERT-1/2: the floor-1 arm reproduces the stored l138 male side
EXACTLY (9 s1 fields + window + dn_into 1277 + pure_proj 28 + both DNp33
rows + ng top-10 + the 9-entry mass list) BEFORE any floor>=2 read.

BRANCH M1_floor_changes_cohort fired (rel change 11.21): dn_new 28 -> 342,
ng 9 -> 43, K 9 -> 52 (BANC K 77). Window shares computable for the FIRST
time: male .2818/.0667/.0670 vs BANC .1946/.0642/.1333 — the rank-20-29
window agrees to .0025, the tail does not. Ladder dn_new {1:28, 2:199,
3:342, 4:458}, dn_into 1277 -> 963 at floor 3. Mechanism is the registered
one: cohort membership is disqualified by ONE cord->DN edge and 97.2% of
male DNs have one at floor 1, so stripping weak edges MOVES cells into the
pure-projector cohort (P1 + P2 both met).

So "no ladder exists to walk" was a FLOOR ARTIFACT of our own extraction.
Status is UNTESTED AT MATCHED FLOOR (no dynamics; L169(b2) is the standing
static->dynamic warning). SURVIVES the match: male DNp33 stays RECIPROCAL at
both floors (cord in-edges 37/33 -> 6/2, never 0, ladder mass exactly 0.0) =>
M3_dnp33_pure did NOT fire. Design pins stored: floor-3 ranks 25/26 =
DNp54-R / DNpe028-L, mass gap 4.4e-04 = 1.13x BANC's own XOR pair delta
3.9e-04, so an analogous mass-twin test is CONSTRUCTIBLE on the male side.

OWN-CATCH (L44/L85 class, 14th instance): the first §2.6 sentence called the
male twin pair "~18x looser", using the 2.4e-05 gap from a DIFFERENT ladder
(l169b's floor-4 twin) carried in log prose. Re-deriving BOTH gaps from their
stored artifacts (l170 pins + l131/static.json:rank_mass.pair_delta) turned
an order-of-magnitude dismissal into a near-match; l149_verify §17 now
asserts the ratio band so the prose cannot drift back. Lesson: a cross-run
constant quoted from a log line is prose even when it is about YOUR OWN
ladder — ladders are per-floor objects and their twin gaps are not
interchangeable.

Evidence rule held: the reviewer's floor-3 figures (342 / K=52) stay
REVIEWER-REPORTED and BARRED from the draft; our independent run lands on
exactly those two values, recorded in LANE-LOG + CLAIM-MAP B26 only.

Folds: DRAFT v3.15 §2.6 rewritten; numbers.json +l170.matched/+l170.pins
with all 87 old keys BYTE-IDENTICAL; l149_verify NEW section (17);
CLAIM-MAP B26 + the §-table row; all five paper verifies ALL GREEN with the
abstract untouched. Digest pushed 8bdef3a2..cda95962, remote blob byte-
identical (l170/verify_push.py PASS).

## L171 — slow-line re-attribution + two-window robustness panel (2026-11-20, tick 199)

Card: LANE.md L171 (ideas 87, referee response #4 in the reviewer's order).
PREREG banc/l171/PREREG.md FIRST (A1/A2/A3 attribution, B1-B4 robustness
with B4 checked first per re-score, mandatory mech-off disclosure, P1-P6).
ZERO rollouts, no RNG, no graph build: banc/l171_rescore.py re-scores the
STORED B26 traces (banc/l135/raw_l135.npz) and rebuilds the drive envelope
from banc/l135_run.py's own loop.

BRANCH A1_envelope_line. Envelope FFT over the 60-s window: dominant non-DC
line = bin 6 = .100 Hz EXACTLY (rank 1, local max, amp 115.17 vs 46.78/53.60
at bins 5/7). Mechanism is gap ALIGNMENT, not the chop period: the
continuous 1.4-Hz segment overrides two of six possible gaps, leaving four
centred at 7/16/47/56 s whose 4-gap vector strength is .951 at .100 Hz and
.174 at the 500-on/400-off chop's 9-s fundamental (.1111 Hz, bin 6.667).
=> the CARD's own Methods sentence ("the 0.1-Hz peak is the 9-s stimulus
cycle") is WRONG and the run refutes it; the corrected mechanism is what the
draft states and what l149_verify §18 gates (it asserts the chop bin != the
dominant bin).

BRANCH B2_preserved. Re-scored carrier-vs-twin (cutng25 vs cutng25p), n=16:
  q07 published      15/16 .754 | twin 5/16 .399 | d .355 | d_k 10
  UNCHOPPED 1.4 Hz   12/16 .628 | twin 0/16 .000 | d .628 | 16/16 up
  0.3-Hz high-pass   15/16 .676 | twin 1/16 .370 | d .306 | 15/16 up
Ordering preserved in BOTH; "cleaner" is METRIC-DEPENDENT (high-pass mean
contrast DOWN .306<.355 while seed separation UP 14>10) so the verdict is
PRESERVED, not cleaner. The registered B4 degenerate branch did NOT fire:
only the twin arm is at floor, so the fast-segment re-score adjudicates (the
L50/L79 fast-drive toxicity law predicted it might not).

CERT: published q07 cells reproduced EXACT (4 fields x 2 arms) + stored
Wilson bounds to <1e-9 BEFORE any new window/filter read; n=16 DERIVED from
the stored k=0 Wilson ub .19360768 (the npz carries 18 seeds — two
forward-chain anchors excluded, never assumed); high-pass self-tested on
synthetic input (.05 Hz att >100x, 1.4 Hz rel err 2.2e-15) before touching a
pool trace; q14 mask 150 points, zero overlap with q07.

OWN-CATCHES (both disclosed in the draft/CLAIM-MAP):
 1. First run's CERT failed with kR 17 vs stored 15 — my P6 took ALL npz
    seeds. The stored k=0 Wilson ub identifies the batch size; derive n
    from a stored bound, never from the key scan. (L109-class rounding/
    denominator family.)
 2. numbers.json regenerated WITHOUT copying the pre-tick file, so the house
    byte-identity check could not run in its usual form. Substitute: a
    regenerate-with-the-l171-block-stripped run reproduces all 89 keys
    byte-identically (json.dumps sort_keys equality) + the generator diff is
    purely additive. House rule for next time: cp numbers.json first.
 3. l149_verify §8 (l156 fold) asserts a §4 prose literal I rewrote
    ("a real slow oscillation, not trend") — SECOND instance of the L169d
    lesson that index()/literal gates are prose contracts; re-anchored to
    the new wording rather than reverting the prose.
 4. Heredoc trap: '\n' inside a triple-quoted builder string becomes a REAL
    newline in the emitted file (unterminated string literal at compile) —
    escape or avoid newline-bearing literals in builder heredocs.

FOLDS: DRAFT v3.16 — abstract result 4 + §1 map re-written (slow-line
censuses relocated), NEW §2.8, Methods envelope bullet, §4 amended;
numbers.json +l171.envelope +l171.panel; l149_verify NEW §18 (envelope
rebuilt from constants PARSED out of l135_run.py, independent duty/S
re-derivation of all 6 cells, branch proven from cells, metric-dependence
asserted both directions); l158_verify freeze RE-CUT to v3.16 (re-attribution
tokens + language REQUIRED, endogenous-clock re-assertion FORBIDDEN);
CLAIM-MAP B27 + §-table row; l161 bidirectional 91/91; all five verifies
GREEN. Digest pushed cda95962..be1feb43, remote blob byte-identical.

## L172 (a) — the statistics pass: one canonical pooled count per arm (2026-11-20, tick 200)

PREREG banc/l172/PREREG.md written first. ZERO rollouts, no graph build, no
torch; RNG only for the registered bootstrap (seed 1720).

ADMISSIBILITY RULE A (the load-bearing method piece): a stored batch
contributes to an arm's pooled count only when its run script's constant
block, PARSED FROM SOURCE, equals l135_run.py's (TAU .05, DT .01, RMAX 1,
BG .02, NOISE .01, SETTLE 400, WIN 6000, SEG 2000, SEGB
[(0,2000,.7),(2000,4000,1.4),(4000,6000,.7)]), the arm's stored gain matches
the canonical value to 1e-9, and the seed has not already been counted.
38 of 49 stored trace files qualify; the five l139 jittered-gain sets are
EXCLUDED as different networks (they re-roll the SAME seeds on jittered
weights — that is not extra noise-seed evidence) and three pre-protocol
files fail the constant block.

CERT-first, and CERT-1 earned its keep: re-deriving l156's stored census
cells from its stored per-seed rows revealed the stored `agree` field is
counted ONLY among sub-band rows (a row-wide count gives 84 where the
stored pooled value is 80). CERT-2/3 then reproduced four stored per-batch
duty cells EXACTLY (l142 cutng25, l145 eMotTop5, l150 silW, l169d cutng25:
kR, kL, meanR at the stored 3-dp rounding) with stored Wilson bounds to
1e-9, before any pooled number was read.

RESULT. Canonical unique-seed pooled counts (right side): b65 513/513,
full 207/513, cutk5 0/226, cutng19 5/178, cutng23 0/82, cutwA 72/258,
cutng25 203/210, cutng25p 30/66, cutng29 188/194, cut58 1/258, silW 78/98,
eMotTop5 31/98, eMotBot5 25/98, eOutMot 21/34 — each with full-precision
Wilson and a 10k-resample bootstrap CI on mean duty. Branch
S1_counts_stable: every class the draft states survives the re-pool.

P4 REFUTED, and this is the finding. The card asked me to "disclose
twin-vs-base p=.406 as underpowered rather than neutral". At the canonical
pool the question is not underpowered at all: twin − base = +.175, 95% CI
[+.047,+.305], Fisher p = .008 — the interval EXCLUDES zero. "Behaviourally
neutral" was a SMALL-POOL ARTEFACT, not a measured null, and the twin is
relabelled INTERMEDIATE (graded between base and carrier: twin − carrier
= −.512 [−.628,−.388]). A card's prescribed wording is a hypothesis too.

P2 held and relocates the card's own worry: the published duty counts were
ALREADY unique-seed clean (pooled n = 16 x batches, blocks disjoint) — the
unique-seed problem bit the slow-line CENSUS, which pooled TRACES. Its
unique-seed forms are 449 of 449 (lb .992) and 348 of 433 (lb .764, rate
.722 -> .804); 69 and 67 repeat observations removed, ZERO disagreeing
(so S3 did not fire and forward-chain bit-identity holds at the metric
level too). P1 PARTIAL: 18 recurring seeds, not the 2 anchors I predicted —
two early runs both rolled one 16-seed block.

LESSONS.
- The real defect was never a wrong number, it was INCONSISTENT pooling:
  the same arm appeared with two different unions in different sections
  (4-batch and 9-batch cutwA; 3-batch and 8-batch carrier). One canonical
  union per arm is the only form that cannot drift between sections.
- An arm's NAME is not its identity across a long lineage: l144's
  `sil1110_wA` and l150's `silW` are the same manipulation (the draft
  already pooled them), so the pooled table needs an explicit ALIAS map.
  Conversely the jitter sets share seeds but not networks. Pool by
  (manipulation, network), never by token.
- Literal gates in a verifier are prose contracts (L169d/L171 lesson, 3rd
  and 4th instances here): changing the pooled counts broke draft-string
  asserts in l149 sections (3) and (8) and the whole l158 freeze. Fix =
  re-anchor the literal to the new wording and keep the stored-artifact
  assert as-is; never loosen the stored check to make a prose gate pass.
- A paper that pools batches needs the UNIT OF INFERENCE in writing: ours
  is a noise seed of ONE fixed network (one graph, one gain, one protocol).
  Written into §4 so no interval can be read as cross-connectome variance.

Artifacts: banc/l172/{PREREG.md,l172_stats.py,stats.json,stats.out,inv2.json};
DRAFT v3.17 (abstract + §1 map + §2.1 + §2.2 + §2.4 re-counted, NEW §2.9
statistics section with the pooled table and the 13-row difference table,
§4 unit-of-inference + unique-seed census + the n=3 sham caveat replacing
the false "−.088 inside the .075 sham spread"); numbers.json +4 l172.* keys
with all 91 pre-existing keys byte-identical (pre-tick copy taken FIRST this
time — the house rule l171 had to journal); l149_verify §19; l158_verify
freeze re-cut to v3.17; l161_verify §1 key set re-cut, 28 blocks;
CLAIM-MAP B28. All five paper verifies ALL GREEN.

## L173 (a) — the Methods write-up, every constant parsed from source (2026-11-20)

Card L173 has two halves; this stage ships the SECOND one first, by
dependency order: the card asks for the §2.4 bit-identities to be
*moved into Methods*, so Methods has to exist before §2.4 can be
rebuilt. §2.4 is stage (b), and the verifier asserts §2.4 is untouched
here.

PREREG `banc/l173/PREREG.md` first: source-of-truth rules S1-S4 (every
constant PARSED, never transcribed), CERT-1/2/3, branches
M2_equation_differs > M1_equation_matches, pins P1-P5.

Branch **M1_equation_matches**. The card prescribed an update equation
from memory; rather than trusting it, `l173_methods.py` extracts the
run script's OWN three update lines by regex, `exec`s them on a 7-node
random system, and compares against an independent implementation of
the prescribed equation — max|Δ| = 0.0 exactly. So §3.2 states the
code's semantics, including the two details prose usually gets wrong:
the noise enters AFTER the rectifier and INSIDE the clamp, and the
clamp has NO lower bound.

CERTs: CERT-1 = 15 constants identical in `l135_run.py` and the CURRENT
`l169d_run.py` (a Methods that describes a retired protocol is the
failure this blocks); CERT-2 = AF_T + four stored-form gains equal to
`l135/anchors_run.json` within 1e-12; CERT-3 = the cohort rule
re-derived from `l131_static.py` source equals the stored K = 77 /
share .5024 / 19+58 split / mass split .1103-.3921.

New in the paper: the DNg100 tonic drive D = 0.2 appears for the FIRST
time (every earlier draft silently omitted a standing input term), the
active-fraction definition (x > 0.05, mean after 400 settle steps over
three anchor seeds, 24 bisect iterations on [0.12, 0.18] to AF_T
.109056), the removal-mass definition (ABS out-mass onto cord targets,
shortest prefix carrying 50%), the duty/class criteria as literals, the
pooling rule, and a 15-row notation table.

Method lesson worth keeping: a Methods section is the one place where
hand-typed constants are maximally dangerous and maximally cheap to
avoid — ast + regex over the run script costs 3 seconds and converts
the whole section into a gate that BREAKS when the protocol changes.
`l149_verify.py` §20 re-parses everything independently and re-runs the
equation probe from scratch, so the draft cannot drift away from the
code silently.

Artifacts: `banc/l173/PREREG.md`, `banc/l173_methods.py`,
`banc/l173/methods.json`, DRAFT v3.18 §3 (ten subsections),
numbers.json +3 keys (95 pre-existing byte-identical),
`paper/l149_verify.py` §20, CLAIM-MAP B29 + §-table row.

## L173 (b) — the §2.4 rebuild around the gain-clean arm (2026-11-20, tick 202)

PREREG `banc/l173b/PREREG.md` FIRST (T1-T4 source-of-truth, CERT-1..6,
branches B2_silW_gain_differs > B1_silW_gain_unchanged, pins P1-P4, plus a
registered SCOPE EXTENSION for the mass-ratio correction). ZERO rollouts,
zero RNG, no graph build: `banc/l173b/l173b_cert.py` is arithmetic over
stored values only.

BRANCH B1_silW_gain_unchanged. The card called silW "the cleanest arm" and
the reason is now measured rather than asserted: silW's gain is EXACTLY its
base's (.14365819573402408 in both l144 and l150, five files agreeing on the
base value), while every edge-removal flip arm carries a +1.06..+1.30%
af-matched gain increase (eOutInt +1.297, cutng25/eAll +1.244, eOutAll
+1.238, eIn +1.087, eMotIn +1.062) and the two non-flip motor halves sit
within ±0.03% (−0.031 / +0.009; intermediate eOutMot −0.568). So across the
edge ladder identity and gain CO-VARY — reviewer issue I4's confound — and
silW is the single arm that breaks the covariance from the activity side;
§2.7's graph × gain 2×2 closes it from the wiring side. §2.4 now leads with
that arm.

Three honesty repairs in the same fold. (1) The "−.088 inside the .075
random-cell sham spread" wording is gone from §2.4 too (tick 200 fixed only
the abstract): |−.088| is LARGER than the three shams' range, so the arm is
reported as "no demonstrated effect", and the verifier forbids the old
wording body-wide. (2) sil24 now discloses that its PARTIAL label is a
class-label match with NO demonstrated separation from either comparator at
n = 16 (5/16 vs the same batch's untreated intact base 6/16 vs the cut base
5/16) — reviewer I10's second component. (3) The carrier-mass ratio is
corrected from the printed 12× to its re-derived 9.72× (.0544/.005599) in
§2.4 AND the abstract; the l158 freeze is re-cut with 9.72 REQUIRED and
"12× below" FORBIDDEN so it cannot grow back.

Relocation as the card ordered: both bit-identities (eAll ≡ cutng25 at an
equal gain to 16 digits, max|Δ| = 0.0; se0 ≡ eAll over 23 keys × 16 seeds)
now live in Methods §3.8 as construction-level sanity checks, and §2.4 keeps
only the ~.13 silW→eAll margin they leave as a result. The "two-factor law"
framing is retired body-wide (the changelog banner keeps its history).

Verified: CERT-1..6 all green BEFORE any draft line was edited (exact float
equality, band membership asserted rather than assumed, Wilson to 1e-9, the
retired sentence re-proven false in the data, the ratio recomputed, the
sil24 comparators re-read). numbers.json +1 key with all 98 pre-existing
keys BYTE-IDENTICAL on regen (pre-tick cp first). l149_verify §21 re-reads
every gain from its stored anchors field and re-derives every percent delta
independently of cert.json, takes the flip partition from stored class
booleans, and asserts the relocation + the retired framing's absence. All
five paper verifies ALL GREEN (l143 / l149 21 sections / l158 / l159 / l161
with 30 blocks). CLAIM-MAP B30 + its §-table row.

Own-catches (disclosed): §21 is the FIFTH instance of the prose-contract
lesson — three prior-section literals ("6/16 seeds up and 0 down", "14.5%
intact vs 14.7% cut") and one of my own new gates broke purely on LINE
WRAPPING (l122 class), fixed by reflowing the draft to keep the literals
contiguous and by gating my own new check on a short unwrapped fragment.
Also: §2.4 grew 8,502 -> ~9,900 chars because the gain-confound disclosure
is new content; the reviewer's "3.4k chars" compression is L174's prose
pass, not this one.

## L174 stage (a) — the reference pass (tick 203, 2026-11-20)

Card L174 is three passes; stage (a) = references + cited-work
characterizations, taken first because numeric markers need a numbered list.
PREREG banc/l174a/PREREG.md (R1 primary-only, R2 match evidence, R3 version
honesty, R4 no renumber, R5 the referee's text is raw material; CERT-1/2/3;
branches A2_approxbrain_necessity_confirmed > A1; P1-P4). Zero rollouts, zero
RNG, no measured value moved (numbers.json byte-identical, gated).

Shipped: 22 entries (14-35) with every field copied programmatically from a
live primary record (Crossref works API / bioRxiv details API / GitHub
repository API), raw responses under l174a/raw/. In-text numeric markers 1 ->
37 tokens covering all 35 entries. NEW paper/l174_verify.py = bidirectional
citation gate + per-entry provenance against the stored records + required /
retired characterization text + cited-field-number traceability +
numbers.json byte-identity.

Branch A2 fired: ApproxBrain DOES report single-interneuron necessity (mean
task distance .017 over 32 held-out draws), so single-cell necessity in a
connectome-constrained model is PRIOR ART and our contrast narrows to
(i) emergence in an uncurated bulk-extracted subnet and (ii) the
matched-removal-mass twin. FlyHack re-characterized (swing across comparison
model / intervention form / trained solution; 25 of 50 members; .872 -> .126).
Kopel re-characterized: the applicable caveat is synapse DETECTION (22%
attachment in BANC vs 41.9% / 40.1%), not pair weights - the §4
"INADMISSIBLE" sentence is gone and the draft now states that our floor arms
cannot bound attachment completeness.

Mechanical facts worth keeping:
- eLife returns an ASSESSMENT record ahead of the article; a naive top-hit
  match cites the review. Filter titles starting "eLife Assessment" /
  "Author response" / "Reviewer" and prefer type == journal-article.
- bioRxiv's CURRENT DOI prefix is 10.64898; the 10.1101/<date>.<id> form of
  the same identifier returns "no posts found" from bioRxiv's own API. Our
  pre-existing entry 13 carried a bare id and is now a resolvable DOI.
- CERT-1 re-resolved all 13 pre-existing entries; 12 matched >= .89 title
  overlap and the single non-match was MY probe title, not the list's.

Own-catches: a new 78-word sentence tripped l159 (split, not loosened), and
l149's stale-denominator guard fired on a legitimate "10.1101/2024..." DOI -
the guard is now scoped to the prose above the reference list with the reason
in source. Four of my own l174_verify gates were wrong on first run
(threshold, entry segmentation across continuation lines, eLife DOI
capitalisation) and were fixed in the verifier.

Remaining on L174: (b) prose/abstract/Discussion/code-strip, (c) figures.

## L174 stage (b1) — the tick-204 novelty narrowing + references 36/37 (2026-11-20, tick 205)

Stage (b) of L174 is too large for one tick, so it is sliced: (b1) the
MANDATORY field amendment of tick 204, (b2) the abstract rewrite + bullets
to prose + a Discussion + the changelog/code strip + the §2.4 compression,
(c) the figure redraws. This tick is (b1). Zero rollouts, zero RNG, no
graph build, no torch, no measured value touched.

PREREG banc/l174b/PREREG.md first, inheriting the l174a PRIMARY-ONLY rule:
every bibliographic field is copied programmatically out of a live API
response stored under banc/l174b/raw/. Acceptance (R2) = title token
overlap >= .60 AND an author-surname match from our own digest. Both
records came back at overlap 1.000 with full surname matches — Habib,
Petr & Rust v1 posted 2026-10-27 (cc_by) and Matsliah et al. v2 posted
2026-06-27 (cc_by_nd, which confirms the abstract-level read our digest
disclosed). Branch N1_identity_prior_art_confirmed: the Habib record's own
abstract independently carries the 6.5%-at-2,000 displacement and the
.04-.95 straightness range our digest attributes to it, so the narrowing
was written. R3's control fetch is recorded rather than remembered: the
legacy 10.1101 form of BOTH identifiers returns "no posts found" from
bioRxiv's own API, which is why entry 13 needed re-resolving in stage (a).

The substantive half is that our novelty claim narrowed for the second
time in two ticks. ApproxBrain established single-cell necessity in a
curated subset; this preprint establishes identity-beats-number with
explicit COUNT-matched controls. So §1 gained neighbour (d) and the gap
paragraph lost its identity-over-count framing. What remains ours is
stated as four specific things and nothing more: matching currency (their
count-matched 37-vs-37 from one spatial mask against our mass-matched
twin, carrier 9.72x below any mass-only band), resolution (a class vs one
cell against one mass twin), readout (a behavioural scalar decoded through
a hand-built open-loop controller measured once per realization vs an
emergent structure statistic inside the network's own dynamics), and
direction plus substrate (remove-then-add on the male CNS vs removal on
the female cord). Their own claim is cited as TYPE-DEPENDENT INTEGRATION,
not single-cell identity, because 89 of their 100 matched cells copy a
reflected same-type neighbour — their disclosure, kept in our sentence.

Two convergences were folded as such rather than as wins. Their 15%
synaptic-amplitude cut abolishing intact wing-motor output is the
operating-point proximity our L139 af-matched gain ensemble bounds; §4
says the fragility is MEASURED here, not absent. Their independent unit
(the realization, not its gust trajectories) matches our L172 §4
unit-of-inference paragraph. The third fold is a limitation, not a
convergence: our cross-connectome type joins are string-level, and
topology-only female-VNC typing [37] is the principled replacement, so
§2.6's scope arm is now explicitly labelled string-joined until redone.

Gate work: l174_verify.py gained sections (8)/(8b)/(8c)/(8d) — per-entry
provenance against the stored records (DOI + version + posted date + >=.90
title overlap), both legacy DOIs asserted unresolved, 21 required
narrowing texts with the superseded gap sentence asserted GONE, a
predicate sensitivity self-test, 9 field numbers asserted present in our
own LANE-RESEARCH digests (rule R5: no number about another group's paper
enters the draft unless our digest carries it), and a byte-identity pin on
the Abstract block so a prose stage cannot disturb the v3.8 freeze. All
six paper verifies green (l143 / l149 21 sections / l158 / l159 zero
over-length sentences / l161 32 blocks / l174).

OWN-CATCH, second instance of the tick-200 lesson: my CLAIM-MAP splice
anchor ENDED on the "## How to re-verify the whole package" heading and
swallowed it; the post-patch re-read caught it and the heading was
re-emitted. A patch anchor that is or ends on a heading must re-emit the
heading — this is now twice in six ticks, so it belongs in the builder
lessons rather than in a single run's notes.

Remaining on L174: (b2) abstract <= 1,920 chars, bullets to prose, a
Discussion, strip the changelog banner + lane/batch codes + the all-caps
tokens, reviewer I10's §2.4 compression; then (c) the three figure
redraws.

## L174 (b2) — the abstract compression (tick 206, 2026-11-20)

Stage (b2) of the manuscript pass, sliced to the ABSTRACT only (the rest
of (b) becomes (b3) bullets->prose + §2.4 compression and (b4) Discussion
+ changelog/code/caps strip). Zero rollouts, zero RNG, no torch beyond the
verify scripts' own imports.

Done: the abstract went 5,322 -> 1,916 flattened chars (card limit 1,920)
with no inline citation keys, caps tokens {BANC} only, zero arm/lane/batch
codes and a longest sentence of 53 words. Branch R1_relocation_complete:
of the v3.21 abstract's 102 numeric tokens, 31 survive and ALL 76 dropped
ones are asserted present in the certified body, 9 of those being
slash->prose re-formattings of cells the abstract still states.

The two method contributions of the tick:

1. TRACEABILITY MOVED INTO THE GATE. The card forbids inline [key]
   citations, which were the abstract's whole provenance story. The
   replacement in l158_verify (6) is a 19-row claim -> numbers.json table
   asserted BY VALUE (not merely "the key exists"), plus 9 explicitly
   declared non-measurement tokens (release version, cell name, confidence
   level, exponent digits) — and an assertion that those two sets COVER
   every numeric token in the text. Strictly stronger than what the
   brackets gave.
2. THE FREEZE BECAME A TWO-PLACE CONTRACT. l158_verify (4) used to require
   ~30 numeric cells IN the abstract. It now splits them: REQUIRED_ABS
   (28 tokens the compressed text must carry) and RELOCATED_TO_BODY (30
   cells each asserted present in the body). A cell may not vanish from
   both places, so a compression can never silently become a deletion.
   Section (2) keeps the Wilson recompute for all SEVEN U-law arms — the
   source certification does not shrink with the abstract — and only moves
   five locators to the body.

LESSON (new, and the reason the registered branch mattered): a RELOCATION
GATE WRITTEN OVER NUMERIC TOKENS IS BLIND TO PHRASE-LEVEL ORPHANS. My own
reloc.py reported 0 orphans and was right about every number, yet four
gates in other files then failed honestly because they keyed on spellings
that existed ONLY in the old abstract: the ASCII `max|d| = 0.0` (l143 and
l149 — the body's certified home is Methods 3.8, which writes it
`max|Δ| = 0.0`), the en-dash sham RANGE `.429–.504` (l149 — §2.4 lists all
three means `.429/.502/.504`), and five of the seven U-law cells in slash
form (l158 itself). Every one was re-scoped to the body form after
confirming the claim's body home; none was loosened, and the sham check
came out STRONGER (it now matches all three stored values instead of the
range endpoints). The transferable rule: when compressing any certified
block, grep the OTHER verifiers for string literals sliced out of that
block BEFORE editing it, because a numeric-token relocation check cannot
see them.

Second own-catch, the l161 token-scanner class: the v3.22 banner sentence
"no inline [key] citations" made l161 read `[key]` as an unresolvable
citation token and FAIL. Prose that NAMES a notation is parsed as that
notation — reworded to "no inline citation keys". Same family as the
l121 label-sweep cosmetic and the l169c2 banner-scoping lesson.

Gates: l158_verify re-cut to v3.22 with NEW sections (5) length, (6) the
trace table + exemptions + coverage, (7) caps, (8) arm/lane codes, (9)
relocation against the frozen pre-image banc/l174b2/abstract_v321.txt, and
(10) a hash pin; l174_verify P3 re-pinned to the compressed block; a new
body-slice pin banc/l174b2/body_pin_b2.txt (sha df2faa2d022560e1, 70,650
chars) so stage (b3) has a before-anchor for the sections it will rewrite.
CERT-1 all six verifies GREEN on the PRE-edit draft, CERT-2 numbers.json
copied first and byte-identical at the end (238bf2d37f51), CERT-3 the
pre-image frozen and asserted equal before the splice, CERT-4 the trace
table. All six verifies GREEN after. DISCLOSED degenerate pass (L55): with
102 -> 31 tokens the retired-cell FORBIDDEN guard had fewer chances to
fail, so it is a guard that held, not evidence.

## L174 (b3) — the §2.4 editorial pass (tick 207, 2026-11-21)

PREREG banc/l174b3/PREREG.md first. Zero rollouts, zero RNG, no graph, no
torch beyond the verifiers' own imports: the whole tick is string/char
arithmetic over the stored draft, the six verifier sources and numbers.json.

CARD-TEXT CORRECTION (L44 class). The inherited (b3) spec paired "bullets ->
prose in §1-§2" with "the §2.4 compression" and said "(they touch the same
blocks)". Measured: §2.4 contains ZERO bullet lines and the 42 remaining
bullets live in §1/§2.1/§2.2/§2.3/§2.5/§2.6/§2.7/§2.8. The jobs are disjoint,
so (b3) = §2.4 only and the bullets become (b3b).

PREMISE TEST BEFORE MACHINERY (the (b1) split, third deliberate use). I10's
row was re-read from banc/l167/ADJUDICATION.md rather than from the queue
summary, and all THREE of its substantive components are already true in the
draft: the section leads on silW, both construction-level bit-identities live
in Methods §3.8 and are absent from §2.4, and sil24 is disclosed as not
separable from either comparator (shipped by L173 (a)/(b), ticks 201/202).
Branch S1_editorial_only. The referee's quoted "3.4k chars" is a MEASUREMENT,
not a target — the same file records that I10's locator truncated §2.4 at a
2,600-char cap.

OUR OWN GATE WAS THE MIS-DERIVED THING (ADDENDUM 1, the transferable lesson).
I registered a 7,200-char cap by subtracting gate-literal chars and the table
from the pre-image, i.e. by assuming the remaining prose was padding. It is
not: §2.4 states 143 numeric tokens and 24 citation keys and each needs a
clause, so the cap was unreachable without DELETING disclosures — the exact
failure T1 exists to forbid. A char cap on certified prose rewards deletion;
the gate was therefore replaced (pre-splice, in the PREREG) by G1'
DE-DUPLICATION COMPLETENESS: no (meanR, kR/n) cell the grid table carries may
be restated in the prose unless a verifier asserts that exact prose spelling,
implemented as SPAN CONTAINMENT (the substring form exempted nothing and fired
on the asserted '.768, 15/16'). The char reduction is then reported, not
gated, with a >=10% floor so the stage cannot be vacuous. Rule: when a
registered numeric target turns out to be unreachable, replace it with a
STRUCTURAL rule that cannot be satisfied by deletion — and give the new rule a
sensitivity self-test (G1' fails on the frozen pre-image with five restated
cells, passes on the compression).

RESULT: §2.4 9,937 -> 8,562 chars (-13.8%) with 101 of 101 verifier literals
verbatim (including the three carrying an internal newline), 24 of 24 citation
keys, the grid table byte-unchanged, 7 of 7 bold claim leads, 12 dropped
numeric tokens all present elsewhere in the body (0 orphans), 0 new numbers.

THE TICK-206 LESSON PAID OFF IMMEDIATELY. Its closing rule was "grep the other
verifiers for string literals sliced out of a block BEFORE editing it". Done
here as step one: 101 literals enumerated, 62 of them occurring nowhere else
in the draft. All six paper verifies came up green on the FIRST post-splice
run — against four honest gate failures when the same class of edit was done
without the enumeration one tick earlier. Note the pin itself needed
correcting: the first (ASCII-only) harvest said 38 exclusive literals; decoding
the verifiers' unicode-escaped literals gives 62.

ADDENDUM 2 (new builder lesson): freeze a block as the EXACT draft slice,
never as a re-joined line list. My first freeze lost the span's trailing
newline (9,936 vs the live 9,937), so emit.py's T4 pre-image assert failed and
wrote NOTHING — the one-shot splice guard behaved exactly as designed, and the
fix cost one re-freeze instead of a corrupted draft.

Evidence: banc/l174b3/ (PREREG.md with both addenda, premise.py + premise.json,
gate.py + gate.json, emit.py, sec24_pre.txt frozen pre-image, sec24_new.txt,
lits24.json, draft_pre_b3.md, numbers_pre.json, raw/ with the CERT-1 baseline
and every post-edit verify run). DRAFT v3.23, CLAIM-MAP B34 + its §-table row,
l149_verify NEW section (22) makes the de-duplication permanent and caps the
section length. numbers.json byte-identical (238bf2d37f51).

## L174 (b3b-i) — bullets to prose in §1/§2.1/§2.2/§2.3 (tick 208, 2026-11-21)

Stage (b3b) sliced by section group: (b3b-i) §1 + §2.1 + §2.2 + §2.3 = 15
bullets (THIS), (b3b-ii) §2.5 + §2.6 + §2.8 = 11, (b3b-iii) §2.7 = 16. §1
first because it is read first and is the only block the sentence-length
gate covers.

PREREG banc/l174b3b/PREREG.md first. Contract T1 = FORMAT-ONLY, proved:
the span's numeric-token multiset (355) and citation-key multiset (45)
identical before/after, allowed delta EMPTY — strictly stronger than (b2)'s
relocation rule and (b3)'s de-duplication rule, both of which let a token
leave its block. Branch precedence B2_tokens_moved > B1_format_only.
CERT-1 six verifies green pre-edit, CERT-2 numbers.json pre-copy
(238bf2d37f51, byte-identical at the end), CERT-3 exact-slice freeze +
one-shot emit, CERT-4 the transform is PARSED (15 bullet blocks found by
regex, every opener mapped exactly once, no unused map entry), body lines
de-indented mechanically, only the 15 openers re-authored.

Result: branch B1_format_only. 15 bullet lines -> 0, 24 paragraphs,
184/184 harvested verifier literals verbatim, scramble block (table + three
numbered findings) byte-unchanged, raw chars -2.48% while VISIBLE chars
+145.

### Lessons

1. A NUMERIC MULTISET GATE IS BLIND TO LOST ADJACENCY. Run 1 harvested
   verifier literals at a >=8-char floor, which dropped SHORT number
   phrases; the reflow then split '0 of 20' (7 chars) across a line. Both
   tokens survived, so T1 passed — and l149 went honestly red afterwards.
   Harvest gate literals at a 4-char floor with a punctuation-only filter
   (>=2 alphanumerics), or short number phrases are unprotected. The
   verifier suite, not the stage's own report, is what caught it: a
   format-only proof is necessary and NOT sufficient.
2. LITERAL-AWARE REFLOW is the reusable instrument: re-wrap prose to 78
   columns treating every asserted literal occurrence as an unbreakable
   atom. Built here, inherited by (b3b-ii)/(b3b-iii). It is the l122
   wrap-fragility lesson turned into a tool instead of a bug report.
3. WRAP-FRAGILE GATES GET NORMALIZED, NOT RE-WORDED. Two required phrases
   matched only with the old bullet INDENTATION baked in ('NOT\n  MET',
   'not that\n    identity matters'); the claim text is unchanged and the
   gates now read a whitespace-normalized view. Applying the same
   normalization to the FORBIDDEN loops is a strengthening (a superseded
   wording cannot re-enter under a different wrap). Third instance landed
   inside the new section itself ('The\nU-law is read with pooled'), so:
   any multi-word gate on REFLOWED prose must be normalized by default.
4. REPORT THE VISIBLE-CHARACTER DELTA on any de-indenting pass. The raw
   count fell 2.48% here purely from stripped leading spaces, which reads
   as deletion; whitespace-stripped length (+145) is the honest measure of
   whether prose was added. Prediction Q1 (+1..+4% raw) was WRONG for
   exactly this reason and is scored as wrong.
5. A NUMBERED ENUMERATION IS NOT A BULLET LIST. The §2.2 scramble block
   (table + 1./2./3. findings) is prose convention and was pinned
   byte-identical rather than converted; the referee's complaint was
   bullet lines.
6. Card-text measurement again (L44 class): the inherited (b3b) spec said
   "42 bullet lines in §1-§2" as one job; measured per-section counts made
   the slice obvious and the slice boundaries are now in the queue text.

## L174 (b3b-ii) — bullets to prose in §2.5, §2.6, §2.8 (tick 209, 2026-11-21)

Second slice of the bullets-to-prose pass, under the SAME format-only
contract tick 208 registered: the edited span's numeric-token multiset
(411) and citation-key multiset (37) must be identical before and after.
Branch B1_format_only. 11 bullet lines -> 0, span census 27 -> 16 (all 16
of them §2.7's), 26 paragraphs, 229 of 232 harvested verifier literals
verbatim, numbers.json byte-identical, all six paper verifies green.
Permanent gate: l149_verify section (24).

Transferable method, in order of how much work it saved:

1. A FROZEN SUB-SLICE INSIDE THE EDIT SPAN. §2.7 belongs to the next
   slice but sits in the middle of the natural span (§2.5 -> §2.9). The
   choice was two disjoint splices or one span with §2.7 frozen; freezing
   won: `sev_pre.txt` is asserted byte-identical inside the new span, so
   the single-block substitution proof (`d[:i] + new + d[j:]`) stays
   intact and the next slice inherits its material untouched. This is
   tick 208's scramble-block instrument promoted from a sub-block to a
   whole subsection.
2. DE-DASH BY PARSER. 8 of the 11 openers were already full sentences,
   so the rewrite map declares them `new=None` and the parser strips
   `- `. Nothing that needs no re-authoring gets retyped, which deletes
   the whole typo class from those blocks. Only §2.5's three label-ish
   fragments were authored (longest authored sentence 41 words).
3. A FROZEN-RANGE GUARD MUST TEST MEMBERSHIP, NOT A ONE-SIDED BOUND.
   The block parser's continuation rule carried `nb < sev_last`, which
   is right for text before the frozen region and wrong for everything
   after it: §2.8's robustness-panel table fell out of its bullet block
   and the P4 table gate caught it on the DRY RUN, before any draft byte
   changed. The fix is `not (sev_first <= nb < sev_last)`.
4. TABLES ARE THE ONE PROSE UNIT A REFLOW DESTROYS. The chunker
   classifies a blank-line-separated run of `|`-leading lines as a table
   and emits it verbatim (de-indented only); everything else goes
   through the literal-aware reflow. Gate it on row count AND one row's
   content, or a silently reflowed table still reads as "4 rows".
5. The three declared T3 exceptions were §2.6 literals carrying the old
   bullet INDENTATION inside their own line break. The l149 §(17) loop
   was made WRAP-INSENSITIVE (claim text unchanged), which is strictly
   stronger: a literal can no longer hide behind a different wrap. That
   is the second consecutive slice where the wrap-fragility class showed
   up exactly where the harvest predicted it would.
6. Disclosed, not fixed here: the span carries one inherited 70-word
   sentence (§2.8's envelope disclosure; 71 with the bullet dash
   counted). It predates this stage and belongs to the stage (b4) prose
   discipline — a slice reports inherited debt instead of quietly
   absorbing it.

## L174 (b3b-iii) — bullets to prose in §2.7 (tick 210, 2026-11-21)

Final slice of (b3b). Branch B1_format_only under the inherited contract: the
span's numeric-token multiset (248) and citation-key multiset (22) IDENTICAL
before and after. 16 bullet lines -> 0, and with that §1-§2 carries no bullet
list at all (asserted §1 through §3 in the new gate). 19 paragraphs, 159 of
166 harvested literals verbatim, raw chars -0.2% while VISIBLE chars +108.
Zero rollouts, zero RNG; the only compute is string arithmetic.

METHOD CONTRIBUTION 1 — the RAW-PASSTHROUGH PROOF. Nine multiline verifier
literals live in the span but only seven are at risk: two sit in the
non-bullet "Design pins" paragraph, which the transform passes through as raw
lines. Asserting those two BYTE-exact while the seven bullet-internal ones go
normalized turns the exemption into evidence — it PROVES the untouched
paragraphs were never reflowed instead of claiming it. Generalizable: when a
transform exempts a class of gate literals, find the members of that class
that the transform does NOT touch and keep them byte-exact as the control.

METHOD CONTRIBUTION 2 — a RETIRED FREEZE BECOMES A FORWARD-CHAIN ANCHOR.
Section (24) pinned §2.7 byte-identical against the LIVE draft, which is
exactly what this stage changes. Instead of deleting the pin it now asserts
sev_pre.txt == banc/l174b3biii/span_pre.txt: tick 209's handoff proven
against the NEXT stage's own frozen pre-image. Strictly stronger than the
live check (it still holds after the section is edited; L120 form). The same
re-scope moved (24)'s census/paragraph/visible pins onto its own edit region
(span minus the live §2.7), so its measurement — 7 -> 16 paragraphs, visible
+48 — survives verbatim, and the §2.7-only literals are deferred to (25)
through the harvest's own n_in_sev field rather than a hand-written list.
RULE: a stage that supersedes a predecessor's freeze re-points it at stored
artifacts; it never loosens or deletes it.

PROSE-DISCIPLINE FINDING (PREREG ADDENDUM 1-b, written pre-splice):
l159_verify scans the ABSTRACT and §1 ONLY, so §2 has never been under the
>60-word sentence rule. §2.7's stage-(d) anchors bullet carried a 67-word
sentence — a bullet can hold that, a prose paragraph should not, and this
stage is what turns it into one. It is the one block re-authored over its
FULL body (eat=5), split at its own clause boundaries into three sentences
with no token moved; longest §2.7 sentence 67 -> 52 words, now under a NEW
permanent section-scoped 60-word gate. The next-longest (48 words, stage-c2
anchors) is disclosed and left INTACT. LESSON: de-bulleting EXPOSES prose
defects the prose gates never covered — when a conversion moves text into a
gate's blind spot, extend the gate in the same tick.

SCORED PREDICTIONS, both instructive misses: Q2 predicted 0..5 wrap-fragile
literals, answer SEVEN (§2.7 is the most number-dense subsection, so more of
its gate literals straddle a break). Q4 predicted a MAJORITY of openers would
need no authoring (8 of 11 one stage earlier) and only 3 of 16 did — §2.7 is
a controls catalogue written as a table of verdicts, so `Label [key]: clause`
is its native form. Both are properties of the SECTION, not of the machinery.
Q1 (+108 visible, band +50..+400) and Q3 (l159 green, untouched) hold.

TWO OWN-CATCHES. (1) The gate splicer's idempotence guard tested the first 40
characters of the inserted block, which are a `# ----` divider section (24)
already carries — it refused to run on a clean file. A guard token must be
UNIQUE to the block it protects. (2) The CLAIM-MAP §-table patch anchor was a
row PREFIX ("| §2.5/§2.6/§2.8 prose (v3.25) |") and the replacement swallowed
the rest of that row, merging two rows into one line; the post-patch re-read
caught it and both rows were re-emitted. Same family as the tick-200/205
heading-anchor lesson, now with a TABLE-ROW instance: a markdown table row is
a single line, so a prefix anchor inside it eats the row — anchor on the
whole row or splice a new line after it.

Dry run was clean on the first attempt (no draft byte wasted), and all six
paper verifies came up green on the FIRST post-splice run — the tick-206
rule (enumerate the verifier literals BEFORE editing a block) holding for the
third consecutive slice.
Evidence: banc/l174b3biii/ (PREREG.md + ADDENDUM 1 a/b/c, harvest.py,
emit.py, gate.py, span_pre/span_post/span_post_preview, literals.json,
emit_report.json, numbers_pre.json, raw/cert1_*.txt + raw/post_*.txt).
Gate permanent as l149_verify section (25). DRAFT v3.26, CLAIM-MAP B37.

## L174 (b4-i) — §4 Limitations: bullets to prose + the sentence splits (tick 211, 2026-11-21)

Fourth prose slice of card L174's stage (b4). Zero rollouts, zero RNG, no
graph build; the only compute is string arithmetic over the stored draft and
the six stored verifier sources.

SLICE DECISION, from a census re-derived this tick (never inherited):
§3 Methods 0 bullets, §4 Limitations 10, §5 Data & code 4, §6 Author notes 1,
Verification 2 — and §4's sentence scan returns SEVEN sentences over 60 words
(107, 77, 73, 68, 66, 65, 65), the longest prose in the manuscript. So (b4)
splits into (b4-i) §4 THIS TICK, (b4-ii) the Discussion + the inherited
70-word §2.8 sentence, (b4-iii) the lane/batch-code + all-caps strip (which
also carries the PREMISE TEST for touching §5/§6 at all — a data-availability
list is journal house style and §6 is not a manuscript section), (b4-iv) the
changelog banner LAST per the card.

CONTRACT: the (b3b) FORMAT-ONLY contract unchanged (T1 both token multisets
identical, T3 every verifier literal verbatim modulo declared exceptions, T4
single-block substitution against an exact frozen slice, T5 six verifies
green) plus NEW T7, the content-preserving sentence split.

RESULT, branch B1_format_only: 10 bullet lines -> 0 (§1-§4 now carries no
list item at all), numeric multiset 166 and citation-key multiset 18
IDENTICAL, the section's CONTENT-WORD SEQUENCE identical under all thirteen
declared edits, 135 of 140 harvested literals verbatim, 11 paragraphs,
longest sentence 107 -> 53 words, raw chars 7,769 -> 7,541 (-2.9%) and
VISIBLE chars -14.

THREE TRANSFERABLE THINGS.

(1) T7, the CONTENT-PRESERVING SENTENCE SPLIT. The over-length sentences live
in BODY text, which the (b3b) opener map cannot reach. Each is split by a
declared (old, new) pair applied to the joined paragraph text before reflow;
each pair must match exactly once, must carry an identical numeric and
citation-key multiset locally, and must leave the content-word sequence
identical, where content words are every alphanumeric token outside a CLOSED
connective set (and / while / so / therefore). The permanent gate proves it
the strong way: pre-image + all thirteen declared edits must reproduce the
live section's content sequence exactly. OWN-CATCH that forced that form:
emit.py proved the sequence PER SPLIT, which is blind to the two authored
openers, and the gate's whole-span form went red on its first run. A per-edit
invariant is not a per-section invariant.

(2) A SECOND verifier-literal exception class: the bullet MARKER, not just
the bullet indentation. Two §4 literals ('- DATA FLOOR:', '- Wet-lab
predictions') are l149 SLICE LOCATORS, not content checks, and de-bulleting
deletes them by construction. They are re-pointed at the prose form anchored
to a LINE START — equally strong (the labelled paragraph must still open its
own line and the locator can no longer match mid-sentence), never loosened.
Rule: before converting a block, ask of every literal in it whether it checks
CONTENT or merely LOCATES; a locator gets re-pointed, a content check gets
preserved.

(3) The prose-discipline blind spot, second instance. l159 scans the abstract
and §1 only; tick 210 extended the rule to §2.7 and this tick extends it to
§4 — which turned out to carry the manuscript's worst sentence (107 words,
invisible while it was a bullet). The gate's splitter PROTECTS abbreviations
so a false split at 'Fig.' cannot satisfy it, and the §2.8 disclosed
exception is measured PER PARAGRAPH with table paragraphs excluded, because a
flattened markdown table reads as a 115-token pseudo-sentence and masked the
real 70-word offender on the first run (the tick-209 table lesson again).

ALSO: PREREG ADDENDUM 2 — the numeric regex swallows a trailing comma (it
must, for thousands separators like 2,676,592), so the boundary that turns
'10-15, and' into '10-15. The' read as a changed numeric token; trailing
commas are stripped on both sides while the digits still compare exactly.
And the CLAIM-MAP heading-anchor lesson bit for a FOURTH time: the B38 patch
anchor ended at the '## How to re-verify the whole package' heading and the
replacement swallowed it (caught by the post-patch re-read, heading
re-emitted).

PREDICTIONS: Q1 SCORED WRONG and instructively — a positive visible-char
delta was predicted and the answer is -14, because a sentence split DROPS
conjunctions (7 removed, 2 inserted). This is the first stage of the lineage
that edits sentence structure rather than line structure, and the first that
shrinks. Q2 (3..9 wrap-fragile literals) 3, Q3 (l159 untouched) green, Q4 (a
majority of openers need no authoring) 8 of 10, Q5 (<25 inserted connectives)
2 but for the opposite reason predicted.

EVIDENCE: banc/l174b4i/ (PREREG.md + addenda, harvest.py, emit.py,
span_pre.txt, span_post.txt, span_post_preview.txt, literals.json,
emit_report.json, numbers_pre.json, raw/). Gate permanent as
paper/l149_verify.py section (26). CLAIM-MAP B38 + its §-table row. DRAFT
v3.27. All six paper verifies ALL GREEN; numbers.json BYTE-IDENTICAL
(238bf2d37f51). No live changes.

## L174 stage (b4-ii) — the Discussion, and the §2.8 closure (tick 212, 2026-11-21)

Card: L174 (ideas 87), stage (b4-ii). Zero rollouts, zero RNG, no graph
build; the only compute is string arithmetic over the stored draft and the
six stored verifier sources. PREREG `banc/l174b4ii/PREREG.md` written FIRST.

TWO EDITS, nothing else.

E1 — §2.8's inherited 70-word envelope-disclosure sentence, the ONE
>60-word sentence left in §1-§4. l149 §(26) pinned it at 70 words one tick
earlier precisely so that closing it would be gate-visible, and this stage
closes it with ONE declared content-preserving split (T7) at the comma
boundary: `[l154.band], so the envelope` -> `[l154.band]. So the envelope`.
That boundary was chosen for a REGISTERED reason (T2): `,`->`.` plus
`so`->`So` is byte- AND visible-character-neutral, so l149 §(24)'s pins
measured on this very region (visible delta +48, 16 paragraphs, the four
bold leads, the robustness-panel table) hold with NO re-point at all. The
alternative em-dash boundary (` — but` -> `. But`) would have read better
as prose but costs a space, and a nicer `therefore` form would have cost
seven visible characters and a §(24) re-point. Measured: numeric (87) and
citation-key (3) multisets identical, content-word sequence identical under
the T7 strong form (pre-image + declared edits == live), all 69 harvested
literals verbatim with ZERO exceptions, longest sentence 70 -> 56.

E2 — a DISCUSSION, the card's own ask, inserted as `## 5. Discussion`
between §4 and the data note (renumbered §6; author notes §7). Placement was
registered, not rationalised afterwards: inserting ahead of Methods would
renumber §3.1-§3.10 plus §4 plus every verifier slice that locates them, for
a running order the owner sets at submission anyway — so this stage commits
the TEXT and leaves the ORDER to stage (c). 825 words over 7 paragraphs,
longest sentence 52.

THREE TRANSFERABLE THINGS.

(1) T8, the BORN-CLEAN contract. Stage (b4-iii) still owes the body a strip
of lane IDs, batch codes and all-caps tokens, so a section authored today is
gated against ADDING to that debt: §5 asserts zero list items, zero
`L\d{2,3}`, zero `B\d{2}`, zero all-caps emphasis tokens, zero bracket
provenance keys and zero new numeric citation markers. The strongest clause
is the last one: every number §5 quotes must appear VERBATIM elsewhere in the
draft (§-references stripped before the scan), so a PROSE stage structurally
cannot introduce a measurement. General form: when a later stage owes a
cleanup, gate the new text against the cleanup's own predicate now.

(2) The LENGTH-PRESERVING literal-aware reflow. The (b3b) reflow protected
asserted literals from line breaks by substituting placeholders; here the
placeholder was SHORTER than its atom, so `textwrap.fill` wrapped to 78 and
the restore pushed two lines to 79/81 (caught by the house-width assert on
the dry run, zero draft bytes spent). The fix is to pad each placeholder to
its atom's exact length: a literal-aware reflow has to be length-preserving,
not merely break-preserving.

(3) A re-pointed pin beats a deleted pin, again. §(26)'s 70-word §2.8 assert
was the thing this stage removes, so it is not deleted: it moves onto
`banc/l174b4ii/s28_pre.txt` and now proves BOTH that the 70-word form existed
AND that the live section is under 60 — strictly stronger than the pin it
replaces, and the same shape (b3b-iii) used on §(24)'s §2.7 freeze.

PREDICTIONS (scored honestly; two wrong).
Q1 visible delta exactly 0 — CORRECT; raw delta -1 or -2 — WRONG, it is 0,
because the band was derived for the em-dash variant (PREREG ADDENDUM 1,
written at the failing assert before any draft byte changed).
Q2 the new longest §2.8 sentence 40-55 words — WRONG at 56, and
instructively: the binding constraint after a split is not the split's own
pieces but the section's NEXT-longest INHERITED sentence (the licensing
sentence at 56, which predates every (b4) stage). A sentence-splitting stage
should read the whole section's descending sentence table before registering
a band.
Q3 zero literals need an exception — CORRECT (the three wrap-fragile ones
live in §2.6).
Q4 850-1,200 words over 6-8 paragraphs, longest under 55 — PARTIAL: 7
paragraphs and 52 words are inside the bands, 825 words is 25 below the
low edge, disclosed rather than rounded up.
Q5 l159 stays green and untouched, §5's own 60-word rule registered in l149
§(27) instead — CORRECT.

VERIFIED. CERT-1 all six paper verifies green on the PRE-edit draft
(`raw/cert1_*.txt`, six exit 0). CERT-2 numbers.json copied first
(sha 238bf2d37f51) and asserted BYTE-IDENTICAL at the end (cmp, twice).
CERT-3 both edit regions frozen as EXACT draft slices with emit.py asserting
the live slice equals its freeze before splicing and REFUSING a second run
(re-tested: AssertionError). CERT-4 the §2.8 edit is DECLARED, not typed —
the old form must match exactly once in the span and once in the whole draft,
the new form must not already exist. Dry run CLEAN before the apply (two
own-catches spent only dry-run time: the length-preserving placeholder above,
and the T9 required-string checks needing whitespace normalization because
the reflow breaks lines inside them — the tick-208/209 lesson now applied by
default). One own-catch AFTER the splice: the §5 word-count assert added the
three-token heading twice (stored 828 includes it), caught by l149 going red
and fixed by pinning both readings (828 tokens / 825 body words). l149
section (27) makes all of it permanent; §(26)'s pin re-pointed; ALL SIX
paper verifies ALL GREEN after (l143 / l149 27 sections, run with the
peabrain venv python / l158 freeze intact, abstract untouched / l159 zero
>60-word sentences / l161 bidirectional, 39 blocks referenced / l174).
DRAFT v3.28 banner; CLAIM-MAP B39 + its §-table row (re-emitted whole, and
the `## How to re-verify` heading re-checked present once — the tick-210/211
anchor lessons).

## L174 (b4-iii-a) — the lane-ID strip, the §6/§7 premise finding, and the frozen all-caps partition (tick 213, 2026-11-21)

Stage (b4-iii) was sliced after a census RE-DERIVED this tick, because the
card's single line ("strip lane/batch codes and 81 all-caps tokens from the
body") measures as three jobs of different KIND, not one job of three sizes:
lane IDs (13 occurrences) carry nothing to a reader and are deletable; batch
codes (22 occurrences, 12 distinct) carry which paired comparison ran within
which batch, so they need a reader-facing RELABEL plus a Methods mapping —
deleting them would destroy a disclosure, which T1 of every stage in this
lineage forbids; all-caps tokens (310 occurrences, 179 distinct) need a
per-token judgement before anything may be touched. (a) ships the first,
FREEZES the judgement the third needs, and leaves both applications to their
own stages.

PREMISE TEST (the (b1) split, used deliberately again): the card says the
strip "also owns §5/§6's remaining bullets", now §6 Data & code (4 items) and
§7 Author/submit notes (1). Read rather than assumed: §6 is a
data-availability list and every venue wants it as a list; §7 is not a
manuscript section at all (it names the owner, assigns venue choice, carries
"TODO before review"). Both stay lists, §7 is declared OUT OF MANUSCRIPT
SCOPE for every remaining strip stage, and the gate asserts §7 BYTE-UNCHANGED
rather than clean — so its two surviving identifiers are a declaration, not an
oversight.

MEASURED: 13 declared edits; 13 lane-ID occurrences -> 0 in §1-§6 + the
References preamble; pre-image + the 13 edits == the live draft byte for byte
from the title onward; measurement multiset and citation keys IDENTICAL; the
15 removed identifier digit runs asserted BY NAME with none added; raw chars
-101, visible -87; the §2.8 heading 109 -> 84; one declared re-wrap is the
only line-count change; partition 179 distinct / 310 occurrences = 18 KEEP /
23 DEFER / 138 STRIP.

THREE TRANSFERABLE THINGS.

1. A STRIP STAGE MUST GATE ON RESIDUE, NEVER ON ITS OWN ENUMERATION OF SITES.
   The hand-built edit list (12 entries, built from the context scan) MISSED
   `(L168)` at the end of §2.2's bold lead. T10 — which asserts the regex
   finds zero residue rather than that the declared edits applied — failed on
   the dry run and named the token (ADDENDUM 2, edit 13). The enumeration is
   exactly the artefact most likely to be incomplete, so a gate that only
   re-checks the declared list can never catch the site the author did not
   see.

2. AN INHERITED NUMERIC MULTISET GATE IS NOT A MEASUREMENT GATE. This
   lineage's harvest regex has no left word boundary, so it counts the digits
   INSIDE an identifier: `L139` contributes `139`, `B30` contributes `30`,
   `v3.28` contributes `3.28`. A stage whose whole job is deleting identifiers
   therefore fails T1 BY CONSTRUCTION while no measurement has moved. The fix
   is not a looser regex: measurement tokens (identifier-internal digit runs
   excluded, §-references stripped per the (b4-ii) house form) PLUS the
   removed identifier digit runs asserted BY NAME — strictly stronger than the
   original, because it proves both that no measurement moved and exactly
   which identifier left. Sub-trap worth its own line: `(?<![A-Za-z])` only
   blocks the FIRST digit of a run, so `L139` still yielded `39`; the
   lookbehind must exclude a preceding ALPHANUMERIC.

3. A MEASUREMENT SURVIVES A RE-POINT BY DECOMPOSITION, NOT BY RE-TYPING. Five
   inherited pins sat on regions this stage edits. The visible-char
   measurements of (b3b-i)/(b3b-ii)/(b3b-iii) (+145 / +48 / +108) are
   preserved VERBATIM by inserting this stage's own frozen pre-tick draft as
   the intermediate state: each span's delta now reads as the prose conversion
   (the original number, unchanged) plus the strip's own cost (-25 / -51 /
   -15), rather than being replaced by a new net figure. One attempt to apply
   the declared edits to the OLD freeze directly failed and is worth
   recording: that freeze predates the reflow and wraps the same sentences
   differently, so a declared edit string from the live draft does not match
   it — the intermediate-artefact form is the one that generalizes. §(27)'s
   §2.8 byte-identity is re-pointed THROUGH the three declared edits, and its
   content-word sequence check now pins the difference by name (six words out,
   two in) so the strip cannot hide an undeclared word behind "a word left".

Also: T11 as registered ("the caps occurrence count is UNCHANGED") was
self-contradictory, because the caps regex matches the very class this stage
removes; re-formed (ADDENDUM 3) to read the STORED partition — every non-owned
class occurrence-identical, the owned class driven to zero. That coupling
immediately caught a classification gap in the partition itself: the
possessive form `L162'` had fallen into STRIP_EMPHASIS instead of DEFER_LANE,
so possessives must classify with their stem. And the lineage's two
anchor-swallowing lessons BOTH fired again in CLAIM-MAP (the heading anchor
ate `## How to re-verify the whole package`, 5th instance; a row-prefix anchor
merged two table rows, 2nd instance) — both caught by the post-patch re-read
and re-emitted as whole units.

PREDICTIONS: Q1 CORRECT (visible -87, inside the registered -60..-200 — the
first stage of this lineage whose job is deletion). Q2 CORRECT in letter and
WRONG in spirit, disclosed: zero AT-RISK literals needed exemption, but one
literal needed one anyway — `LANE-RESEARCH.md` — because the at-risk harvest
tested only whether a literal CONTAINS an edit's old form, and this literal is
CONTAINED BY it. Overlap must be tested in BOTH directions; the exception is
re-pointed to the stronger absence-plus-replacement form. Q3 CORRECT (l159
untouched and green). Q4 CORRECT (138 of 179 distinct tokens in STRIP, over
the registered >=120). Q5 CORRECT (all heading locators in the verifier suite
are PREFIXES that stop before the lane parenthetical, so none needed a
re-point for the five heading edits).

Evidence: banc/l174b4iii/. Gate: l149_verify.py section (28). CLAIM-MAP B40,
DRAFT v3.29. Zero rollouts, zero RNG, numbers.json byte-identical.

## L174 (b4-iii-b) — the batch-code relabel and the §3.7 mapping (tick 214, 2026-11-21)

Branch R1_relabel_only. PREREG banc/l174b4iiib/PREREG.md first, inheriting the
(b3b)/(b4-i)/(b4-ii)/(b4-iii-a) contract (T3 literals verbatim modulo declared
exceptions, T4' declared sparse edits against an EXACT frozen pre-image, T5 six
verifies green, T7-STRONG, T10 zero residue, T8 born-clean for new text) plus
four new instruments: T1' RELABEL-ONLY, T12 BIJECTION + MAPPING, T13 ARTEFACT
KEYS ARE NAMES, T14 DECLARED REFLOW. Zero rollouts, zero RNG, no graph build;
the only compute is string arithmetic over the stored draft and the six stored
verifier sources.

PREMISE FINDING (registered, read not assumed). The `B<n>` shape covers TWO
semantic classes and the frozen caps partition had conflated them: DEFER_BATCH
held `B1-B4`, which is a PREREGISTERED BRANCH range, not a batch. A third class
fell out of the same read: six occurrences live INSIDE stored artefact keys
(`l145.pooled.eOutMot_B29_B31`, `l148.pooled.eAll_B29_B32`) and those are
FILENAMES — relabeling them would break correspondence with the npz/json on
disk. So the census is 39 occurrences = 19 BATCH prose (11 distinct) / 6
ARTEFACT_KEY / 4 BRANCH / 10 banner (stage (b4-iv)) / 0 in §7, and the partition
is AMENDED rather than applied (DEFER_BATCH -> KEEP_MAPPING 11 + DEFER_BRANCH 1,
still 179 distinct tokens), which also tells (b4-iii-c) to KEEP the codes where
this stage leaves them.

DESIGN, with the reason registered BEFORE the edit: labels are LETTERS
(A,B,C,D,E,F,G,H,J,K,L — I and O skipped so a label cannot read as a digit),
assigned in the internal codes' own RUN ORDER. Two reasons, both gate-level
rather than aesthetic: a letter adds no digit run, so the measurement multiset
stays identical with NO new exclusion class (the (b4-iii-a) ADDENDUM-1 lesson
says never loosen a measurement gate to pass a strip), and the labels sit beside
seed counts ("fresh batch K, n=16") where a numeric label invites a misread.
Monotone-in-run-order makes the draft's own "fresh batch X" claims readable in
sequence. The substitution rule is ONE rule: bare letter when the preceding text
ends in batch/batches or a label separator, else `batch <letter>`; the prettier
alternative (bare letters inside the "(Batches: ...)" parenthetical) needs a
second rule and is disclosed, not taken.

MEASURED: 19 substitutions (6 bare, 13 prefixed); both multisets IDENTICAL with
the 19 removed identifier runs and the 11 entered mapping rows asserted BY NAME;
pre-image + the declared edits == the live draft BYTE FOR BYTE from the title
onward; two paragraphs re-wrapped with their line counts unchanged; body-only raw
delta +40, mapping block 589 chars, title-onward +630; zero residue in §1-§6 +
the References preamble outside the mapping block; §7 byte-unchanged.

FOUR TRANSFERABLE THINGS.
(1) A RELABEL IS NOT A STRIP, AND THE SHAPE IS NOT THE CLASS. One regex shape
    (`B<n>`) carried batches, branch labels and filename fragments; the card's
    word for the job ("strip the batch codes") would have destroyed a
    disclosure in one class and a stored correspondence in another. Classify by
    SYNTACTIC POSITION (preceding `_` or `.` = inside a key; following `_` = a
    branch label) before touching anything.
(2) A LABEL-SCHEME CHOICE CAN BE MADE BY THE GATE. Picking letters over numbers
    was not taste: it is the only choice that leaves an inherited measurement
    gate untouched. When two surface forms are equally readable, prefer the one
    your existing gates can still prove.
(3) READ BOTH SIDES OF A COUNTER DIFFERENCE SEPARATELY. The mapping block
    re-introduces the eleven codes it documents, and a whole-draft
    Counter(pre) - Counter(post) silently CANCELLED eleven of the nineteen
    removals (the first gate run reported 9 instead of 19). Measure removals on
    the body with the declared new block excised, and the additions on the block
    alone.
(4) THE DECOMPOSITION LADDER KEEPS GROWING, AND THAT IS THE POINT. Six inherited
    pins in §(22)-§(27) were re-pointed through this stage's own frozen pre-tick
    draft as a second intermediate, so (b3b-i)'s +145, (b3b-ii)'s +48,
    (b3b-iii)'s +108, (b4-i)'s -14 and (b4-iii-a)'s -25/-51/-15/21 all survive
    VERBATIM with the relabel's cost split out; §(28)'s whole-draft strong form
    was re-pointed from the LIVE draft onto that artifact (strictly stronger: it
    now survives every later stage) with its live-only properties re-asserted on
    live bytes in §(29). A stage that supersedes a predecessor's freeze
    re-points it at stored artifacts; it never loosens or deletes it.

PREDICTIONS: Q1 CORRECT (six verifies green with exactly five verifier literal
re-points and no other verifier edit); Q2 CORRECT (measurement multiset
identical with ZERO named removals needed — the first stage in this lineage that
needs no removed-run disclosure); Q3 CORRECT (l159 untouched and green); Q4
CORRECT (exactly one partition class amended, 179 still covered); Q5 CORRECT
(the "(Batches: ...)" parenthetical survives as content — it carries which ARM
ran in which batch, which the mapping does not — and this stage deletes nothing).

VERIFIED: CERT-1 all six verifies green on the PRE-edit draft (raw/cert1_*.txt);
CERT-2 numbers.json copied first (sha 238bf2d37f51) and byte-identical at the
end; CERT-3 the whole draft frozen as draft_pre.md with emit.py asserting the
live draft equals the freeze before splicing and refusing a second run; CERT-4
the transform PARSED not typed (every occurrence classified by rule, every batch
token mapped, the class census asserted); DRY RUN CLEAN before the apply, after
two pre-PREREG catches in the planning scripts (the artefact-key detector missed
a bracket opening on an earlier line, so two filename fragments were about to be
relabeled; and the label-separator clause was evaluated against the OLD text, so
`batches, G/batch H` would have shipped); l149_verify section (29) makes it
permanent; all six verifies green after; DRAFT v3.30; CLAIM-MAP B41 + its
§-table row.

## L175 stage (b) — single-cell scan + drive-matched twin (2026-11-21, experiment dispatch)

L175 stage (b), 2026-11-21 (owner-directed experiment, fable 5.2 as experimenter): single-cell scan of ng ranks 25-58 on the k=24 base + drive-matched twins, fresh batch 3545-3560, n=16 on all 37 arms -> registered branch D2_identity_carried: carrier 16/16 meanR 0.758 is the only SUPER; mass twin 2/16 (x_mean 0.0005 on the base); drive-matched twins dmA gi 511 5/16 0.390 and dmC gi 1480 2/16 0.366 (drive x1.003/x1.006); 0 of 13 other active cells SUPER; base 5/16; caveat: silent-cell removals span kR 2-11/16 and covary with the re-bisected gain, one batch. Verified: PREREG before any rollout (~/critters/peabrain-lab/banc/l175/PREREG.md); count-asserted transform of l150_run.py (~/critters/peabrain-lab/banc/l175/build_scan.py -> scan_run.py); g_cutwA/g_cutng25/g_cutng25p stored floats EXACT; 322 C0A bit-identity checks vs ~/critters/peabrain-lab/banc/l135/raw_l135.npz max 0.0; metric cert vs results_l135 EXACT; results ~/critters/peabrain-lab/banc/l175/results_l175.json, census ~/critters/peabrain-lab/banc/l175/census_k24.npz, write-up ~/critters/peabrain-lab/banc/l175/L175-FINDINGS.md. No DRAFT/numbers/LANE edit.

## L174 (b4-iii-c-i) — the all-caps de-emphasis of §1 and §4 (tick 215, 2026-11-21)

Stage (b4-iii-c) was sliced THREE ways, and the slice is by KIND rather than
size. A fresh live census (`banc/l174b4iiic/census.py`) re-derived the
all-caps distribution after the (b4-iii-b) relabel and produced three facts
the card's one line did not anticipate:

1. §5 Discussion carries ZERO all-caps tokens of any class. Stage (b4-ii)
   wrote it in the lowercase house form, so §5 is this stage's STYLE
   REFERENCE, not its workload — and §(30) now pins it caps-free so a later
   stage cannot re-emphasise it.
2. §3 Methods is a different KIND of job. Four tokens there are MODEL SYMBOLS
   living inside the state equation and the parameter table (BG, DT, TAU,
   WIN — and tick 213's partition classified TAU and WIN at TOKEN level as
   NOTATION/STRIP), and one token splits by POSITION inside §3 alone: `CC BY
   4.0` the licence name versus `BY CONSTRUCTION` the emphasis. §3 also hosts
   the eleven KEEP_MAPPING codes, which must survive byte-exact. Deferred as
   slice (c-ii).
3. §2 Results is the bulk (89 strip + 36 class labels + 16 tokens needing
   fresh judgement). Deferred as slice (c-iii).

This slice therefore took §1 Introduction and §4 Limitations, where every
owned occurrence is unambiguous de-emphasis. Branch C1_deemphasis_only.

### Measured

64 declared occurrences lowered (26 in §1, 38 in §4), with the five
outcome-class labels becoming the lowercase defined terms §5 already uses.
The edit is PROVED CASE-ONLY over the whole draft: title-onward length
identical, exactly 412 differing bytes, every one an uppercase letter
replaced by its lowercase self. Visible-character and byte deltas are
therefore EXACTLY ZERO — a first for this lineage, whose earlier stages cost
+145/+48/+108/−14/−87/+40 — and both the measurement and citation-key
multisets are identical with NO named removal and NO named addition (tick 213
needed 15 named removed digit runs, tick 214 needed 11 named mapping rows).
§2 Results and everything from §5 onward are byte-IDENTICAL. KEEP survivors
are occurrence-pinned: §1 CPG, CPG-, IN12B003, S07, XOR; §4 BANC, BANC',
EMG, XOR.

### Four method contributions, all inheritable

1. **A literal harvest cannot see a gate built from a regex or a token
   list.** The first harvest found and re-pointed 16 broken verifier literals
   and reported clean — then two gates broke anyway: an
   `re.search(r'(?m)^DATA FLOOR:')` locator in l149 §(26)'s prose contract,
   and an `INTERMEDIATE` entry inside l158's required §1-map token list.
   Neither is a draft-quoting string literal in the harvest's sense. A strip
   or de-emphasis stage must scan the verifier SOURCES for its owned tokens,
   not only for their quoted literals.
2. **A whole-draft presence test cannot see a section-scoped gate.** The
   changelog banner QUOTES the edited prose, so `'UNIT OF INFERENCE'` stayed
   present draft-wide while the §4-scoped gate that reads it (`_lim172 =
   draft[draft.index('## 4. Limitations'):]`) failed. The second-order scan
   (`harvest2.py`) tests presence inside the EDITED SECTION RANGES — and also
   decodes escape sequences, a third blind spot: the first harvest's
   `"[^"\n]*"` literal regex reads `'fully RE-DERIVED, not\n  frozen'` as a
   two-character backslash-n that appears nowhere in the draft, so a real
   breakage looked clean. The scan over-reports on short tokens (`'PARTIAL'`
   used as a stored-artefact class name), so each hit is adjudicated by
   reading its USE, never applied blindly.
3. **Line-start is not sentence-start in a hard-wrapped draft.** The first
   transform rule treated a token at column 0 as sentence-initial and
   capitalised SEVEN mid-sentence wrap openers — "Fixed network" for a
   sentence that began on the previous line, and the same for SUFFICIENT,
   ORDER, SUFFICIENCY, MASS-, CARRIER, COSTS. The fixed rule reads the
   PREVIOUS line's ending (blank, heading, `.` or `:`), and the fix was
   applied by restoring the freeze and RE-RUNNING the parsed transform, never
   by hand-editing the draft — the parsed-not-typed discipline is what made a
   seven-site rule error a one-command repair.
4. **A global file-level replace cannot tell a live-draft quote from a
   stored-pre-image quote.** `emit.py`'s `str.replace` over l149_verify.py
   lowered the PRE-IMAGE side of a `_SPL_B4` pair (`'cutwA PARTIAL 3/16
   .371), and the f4ng-vs-f4tw'` quotes the (b4-i) stored span, which still
   carries the uppercase form), and the gate caught it with
   "split pre-image form not unique". Pre-image quotes must stay verbatim.
   Related: nested literals must be re-pointed LONGEST FIRST, or replacing
   the short form rewrites the long one's interior and the long form
   "vanishes" (caught on the first dry run).

### Gate

Permanent as `l149_verify` section (30): T15 case-only over the whole draft
(same length, 412 upper→lower byte differences, nothing else), the
out-of-scope byte identities computed TITLE-RELATIVE — an own-catch, because
the banner gains this stage's own entry and every absolute offset shifts —
the KEEP survivor sets for both edited sections, §5's caps-free pin, the
class labels in their house form, and both multisets. §(23), §(26) and §(29)
are re-pointed THROUGH this stage: their frozen literal pins now accept
case-insensitive images WITH the retired all-caps form asserted ABSENT, which
is strictly stronger than either check alone and is bounded by §(30)'s
whole-draft case-only proof. §(26) additionally pins §4's pre-strip caps
census (39 distinct / 45 occurrences) and its 7 surviving KEEP occurrences,
and declares that exactly ONE of its two bullet-marker locators was
de-emphasised so the exemption cannot silently cover a second label.

Six paper verifies green; `numbers.json` byte-identical (sha 238bf2d37f51).
DRAFT v3.31, CLAIM-MAP B42. Evidence `banc/l174b4iiic/`.


§L184 — Mechanism analysis (stored B39 traces + cutwA wiring; CPU only, zero rollouts). Preregistered harmonics/gate, audited all 37 arms and enumerated 93 incident edges. sc25 Δsame +.3504 = Δcross +.5246 plus residual −.1742; gate transmission vs base is not a general harmonic gain. B39 individual carrier phase was not stored. Report: banc/l184/L184-FINDINGS.md; numeric panels: banc/l184/threepanel.csv.

§L185 — Replication + gain null + signed-current twin (2026-11-21, owner-directed experiment dispatch; CPU only, 6 workers, 17 min of rollouts). Fresh batch 3577-3592, n=16 on 19 arms + base, all on the k=24 base -> registered branches R1 REP_D2 / gain form GAIN_ROBUST / R2 GAIN_SENSITIVE_NEGATIVE / R3 S2_NO_FLIP (D2_hardened true): carrier gi 1110 15/16 meanR .770 SUPER at its L175 gain and 15/16 .683 SUPER at fixed base gain (pooled with B39 31/32); base 3/16; mass twin 4/16; drive twins dmA 5/16, dmC 2/16; boundary cells do not promote (sc27 4/16; sc40 12/16 .538 INTERMEDIATE, 3/16 at fixed gain = a gain artifact); gain-only null slope -0.0228 meanR per +0.1% gain (95% CI -.036..-.0095; base 8/16 at -0.5% vs 3/16 at +0.5%, no arm SUPER; R2 .36 of the L175 scan spread within +-.5%); signed-current twin gi 1508 (DNg19-R, dist_rel .003 to the carrier's gated <=2-path current onto right-Ti pools; L175's drive twins did not match it) 2/16 .345 NOT-SUPER. Caveats: R3 one batch + one gate definition; sc40 pooled 23/32 under its re-bisected gain; prediction P5 (contrast sign follows gain shift) wrong. Verified: PREREG before any rollout (~/critters/peabrain-lab/banc/l185/PREREG.md, sha f1f7150240e6, 13 pinned shas unchanged at the end: ~/critters/peabrain-lab/banc/l185/PREREG.sha256); count-asserted transform of the L175 harness (~/critters/peabrain-lab/banc/l185/build_rep.py -> rep_run.py); every worker re-bisected g_cutwA + its L175 arm == stored floats EXACT; C0A 368 checks vs ~/critters/peabrain-lab/banc/l135/raw_l135.npz + 300 checks vs the stored L175 raws (seed 3545) max 0.0; cutwA identical across workers (2185) and == generic alias g000 (437); metric reproduces results_l135 and results_l175 EXACT. Results ~/critters/peabrain-lab/banc/l185/results_l185.json, selection ~/critters/peabrain-lab/banc/l185/selection_s2.json, write-up ~/critters/peabrain-lab/banc/l185/L185-FINDINGS.md. No DRAFT/numbers/LANE edit.

§L187 — Relay silencing + cut, push-pull, sc40 control (2026-11-21, owner-directed experiment dispatch, sequenced behind L185; CPU only, 6 workers x 2 threads, fresh B41 3609-3624, n=16 every arm). PREREG banc/l187/PREREG.md sha 98034281b435e961 frozen 12:28:05 before any rollout; L185 done-gate banc/l187/L185_DONE.txt. Harness = count-asserted transform of l175/scan_run.py (banc/l187/build_relay.py -> relay_run.py). Certs: C0A cutwA == raw_l135 EXACT in all 6 workers (322 checks) + vs L175 raws @3545 (200), stored gains EXACT, FC-150 clamp path == stored l150 silW, CERT-X 0.0. Branches: A1 relay window-clamp 12/16 .591 = A1_unresolved (meanR .009 under the bar; +.177 vs base); A2 relay cut 13/16 .697, fixed gain 13/16 .630 = R1_conduit label; relay summary MIXED; A3 push-pull R3_stack — fixed gain 16/16 .792 (+.076 above carrier removal), rematched 12/16 .605 (-.205, tracks its -0.81% re-bisect); A4 sc40 11/16 .567 INTERMEDIATE, fixed 2/16 .329. Base 6/16 .414; carrier 16/16 .810 (fixed 16/16 .715). Secondary occlusion arm (carrier + relay removed) 16/16 .839: with the relay gone the carrier's removal still adds +.142 chopped duty and the whole 1.4-Hz signature (.020 -> .729), so the relay is not the carrier's necessary conduit; relay removal alone raises chopped duty WITHOUT that signature (.02-.06 vs .43-.53). Construction identity: a relay clamped from t=0 is bit-identical to the relay-cut graph (max 0.0; same re-bisected float). Post hoc: gain sensitivity flips sign with the carrier (duty rises with gain in 3/3 carrier-absent graphs, falls in carrier-present ones). Caveats: one batch, two labels on the band edge, no relay-matched twin, single carrier->relay edge cut not run. No draft/lane edit. Report banc/l187/L187-FINDINGS.md; results banc/l187/results_l187.json; post hoc panels banc/l187/addendum.json.

L186 gate-jitter: E3-mixed/unresolved; aligned/elapsed deletion contrasts +0.275/+0.290, 16 paired seeds; C0A exact. banc/l186/L186-FINDINGS.md and results_l186.json.

## tick 216 — L186 adjudication: the discriminator whose power is computable from its own schedule (2026-11-21, zero rollouts)

L186 (gate-jitter) landed at 12:49 un-adjudicated and un-journaled on the lane
side. Tick 216 took it as the tick item under the L167 evidence rule (a child's
number is a claim until it reproduces under my own code).

VERIFICATION, 33 named checks green (banc/l186/t216_verify.{py,json,out}): every
stored value in results_l186.json reproduces from the stored per-pair matrices
under my own reader -- duty means to 4 decimals over 240 ordered pairs per arm
per clock, the same-seed diagonal IDENTICAL between clocks (the registered
wiring check), the delete-one-SEED jackknife re-derived at A +0.2752
[+0.179,+0.371], T +0.2904 [+0.181,+0.400], D -0.0153 [-0.156,+0.126], C0A 92
checks max |delta| 0.0 against raw_l135, g_cutwA exactly the lineage pin
0.14365819573402408 (sc25 +1.244%), af matched .10904 vs .10902, seeds
18601-18616 fresh with ZERO numeric-token collisions over every prior banc npz
archive, anchors 801/901 left at the stored [900, 4900] schedule, and all 32
displaced onsets inside the registered 900+-300 / 4900+-300 bands with the
500-step pulse never crossing a segment edge.

THE RESULT THAT STANDS: the carrier-removal duty elevation SURVIVES
independently jittered gate onsets under BOTH clocks (A and T both above the
registered .15 survival bar, both CIs excluding zero). The phenotype is not an
artifact of one shared fixed gate schedule -- a robustness win for the draft.

WHY NEITHER CLOCK WON (banc/l186/t216_power.{py,json,out}, zero rollouts, stored
onsets only). The primary metric correlates 500-step windows; the registered
jitter is +-300 steps. So the aligned and elapsed views of a pair differ by
lag = onset_i - onset_j and OVERLAP by max(0, 1 - |lag|/500) of their samples:
measured mean overlap 0.62, median 0.65, 70.4% of the 480 pair-segments share
half or more, only 2.1% are disjoint, mean |lag| 190 steps = 1.33 tone periods
but 0.38 of ONE window. D is attenuated by construction and E1/E2 were
unreachable whatever the biology. The transferable rule: an ALIGNMENT
discriminator's displacement must exceed its readout window, and that ratio is
computable from the drawn schedule BEFORE any rollout -- so it should be a
pre-run gate, not a post-hoc explanation.

THE TONE CONFOUND IS CLEARED, which keeps the E3 informative rather than empty.
The jitter spans 3.6 tone periods, so it genuinely had the range to break tone
alignment; per-pair aligned-minus-elapsed duty does NOT track the relative
tone-phase rotation it induces (rho +.148 carrier-removed, -.110 base = weak and
sign-INCONSISTENT across arms; near-in-phase vs near-antiphase pair means
+.087/-.024 and +.017/+.053). The cross-seed structure is therefore not locked
to the shared elapsed-time tone either -- which is the one rival E2's own PREREG
flagged.

Secondary phase block holds as filed: pool peaks sit near a quarter cycle before
GI 1110 (Ti_fR -100.2 deg R .916, Ti_eR -90.4 deg R .754, n=16 both).

BOARD RECONCILIATION the same tick: L184/L185/L186/L187/L188/L189 all completed
in-session today but sat unchecked, so the first-unchecked pointer was stale for
both engines. Each was verified against its own stored artifacts before
check-off, and two of my own verification greps were WRONG in the direction that
reads a perfect result as missing -- paper/ lives in peabrain-LAB not peabrain,
and the digest headings carry "[lab, 2026-11-21]" WITH the comma. Verify a
claim-checking pattern on a known-present line before believing its zero.
Precedence re-pointed to L183 with the reason registered in the ideas-87 header;
L190/L191/L192 carded as ideas 96.


Duck lesion dispatch (offline): 4/8 intact hides, 0/8 with the looming pool clamped; no decision flips across 91 single-cell clamps. Scope and evidence: ducklesion/DUCK-FINDINGS.md.

L190 single-edge cut — B3-partial. Removing 1110→75494 on the rematched k=24 base raised chopped right-tibia duty (+.223 paired, 95% CI +.082 to +.364), without the carrier-cut 1.4-Hz signature. Matched sham 48→75494 was base-like. Anchors exact; n=16 each. Evidence: banc/l190/L190-FINDINGS.md and results_l190.json. No fixed-gain inference.
