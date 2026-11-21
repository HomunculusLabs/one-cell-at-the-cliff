# PREREG — L187: relay silencing + relay cut + push-pull (sequenced behind L185)

Registered 2026-11-21 ~12:30 EST, BEFORE any rollout of this card (no settle,
no bisect, no trace exists under `banc/l187/`). Owner-directed
(`BRIEF_relay.md`); experimenter = fable session. What exists at registration:
the brief, `build_relay.py` + three block files, the generated `relay_run.py`,
`build_verdict.py` + `verdict_tail.py.txt` + `verdict_l187.py`, `run_all.sh`,
`static.json` from `L187_MODE=static` (ZERO rollouts, no RNG: graph tables,
stored-file reads, seed-key scan), `probe_stored.py/.out` (stored L175
covariates only) and `L185_DONE.txt` (the sequencing gate: L185 FINAL, all
arms n=16, its workers / orchestrator / dispatch session gone, checked
12:25:49). Nothing here was tuned on an L187 outcome. Stored L175 (B39), L184
(anatomy) and L185 (B40) results are prior data and are used openly below.

## Question

L184 named a candidate route for the carrier's (DNp33-L, gi 1110) influence on
the right tibia: 4-edge chains through relay interneuron gi 75494 (IN06B033,
left, inhibitory), which sc40's cell (gi 559, DNge084, inhibitory) also enters
with the opposite sign. Is the relay the conduit of the carrier's regime flip
(silencing or cutting the relay, carrier present, reproduces it), and does
removing the carrier and gi 559 together cancel or stack?

## Machinery (inherited; nothing lineage-side edited)

`relay_run.py` (sha256 b7c486bf3250…, 1765 lines) is a count-asserted ADDITIVE
transform of the certified L175 harness `l175/scan_run.py` (sha256
bbfea4e07ff4…, 1397 lines; builder `build_relay.py` d786df71ec17…, 17 rep
sites). VERBATIM: extraction, ladder, `build()/wb()/pools_for()`,
`add_arm()/gen_init()`, `settle_states` draw order and step arithmetic,
`bisect_vec`, the rollout step loop, store keys, per-seed atomic checkpoints.
REPLACED: seed list, arm block, gains + anchors block, tail; census mode
removed. ADDED inside lineage functions, guarded by arm name and inert for
every other arm: a full-run clamp `CLAMPF` (4 sites: init + step of both
settles) and read-only per-step traces of cells 1110 / 75494 / 559 (3 sites).
Constants unchanged (TAU .05, DT .01, BG .02, NOISE .01, SETTLE 400, WIN 6000,
BETA 2, D .2, AF_T 0.10905611018339793). Readout `verdict_l187.py`
(d42702ff7378…) = the `l150_verdict.py` helper block lines 1-71 VERBATIM (sha
5c8323f2755f1d0c, the slice L175 and L185 used) + `verdict_tail.py.txt`
(4f8d00680a08…), written before any rollout.

## Seeds

FRESH **B41 = 3609..3624, n = 16 for EVERY arm** (next slot of the lineage's
32-step grid). Verified absent from all 225 npz files in the lab (`banc/**`
including the L175 and L185 outputs, plus sibling dirs) by an
any-key-endswith scan, in-script assert re-run by every process. Non-sample
anchor seeds, rolled FIRST: 801, 901 (vs `l135/raw_l135.npz`) and 3545 (one
stored B39 seed, vs the L175 raws). Bisect settle anchors 11/22/33 (lineage).

## Stored facts used to design and predict (no L187 rollout)

- Relay on the k=24 base: active (census x̄ .329), inhibitory, 58 in / 51 out
  edges, delivered drive 86.5 (carrier 71.6); one direct edge onto a right-Ti
  flexor motor neuron (8 syn), none onto the extensors.
- Carrier → relay is excitatory (21 syn). In stored B39 arms the relay's mean
  rate is .327 on the base, **.138 with the carrier removed**, .346 with gi 559
  removed; relay target gi 74914 goes .200 → .355 / .152. So carrier removal
  already is a ~58% relay silencing; clamping takes it to 0.
- gi 559 is near-silent on the base (x̄ .034, below the .05 "active" bar).
- L185 (B40): carrier 15/16 .770 (fixed gain 15/16 .683); sc40 rematched
  12/16 .538, **fixed gain 3/16 .341**; gain-only null slope −.0228 meanR per
  +0.1% gain. A re-bisected gain shift alone therefore moves duty.

## Arms (all on the k=24 = cutwA base; g_cutwA = 0.14365819573402408)

| arm | graph / manipulation | gain | role |
|---|---|---|---|
| `cutwA` | base (lineage plumbing VERBATIM) | stored | base; C0A anchor; in EVERY worker |
| `sc25` / `sc25F` | wA − 1110 | L175 stored 0.1454454553127289 / g_cutwA | carrier removal: same-batch reference for "mimics" |
| `rsilW` | base matrix, relay clamped to 0 in the WINDOW (lineage silW form, the existing `CLAMP` line) | re-bisected; == g_cutwA by graph identity (asserted) | **A1 relay-silence (branch read)** |
| `rsilF` | base matrix, relay clamped from t = 0 (init + settle + window) | re-bisected UNDER the clamp | A1b, reported beside A1 |
| `rcut` / `rcutF` | wA − 75494 (all 109 incident edges gone) | own stored-form bisect / g_cutwA | **A2 relay-cut (branch read = rematched)** |
| `pp` / `ppF` | wA − 1110 − 559 | own bisect / g_cutwA | **A3 push-pull (branch read = rematched)**; fixed twin |
| `sc40` / `sc40F` | wA − 559 | L175 stored 0.14203338861465453 / g_cutwA | **A4 control** |
| `occ` / `occF` | wA − 1110 − 75494 | own bisect / g_cutwA | SECONDARY occlusion arm (not in the brief) |

Two readings of "activity-clamp … re-bisected" exist and both are run. The
lineage's silence (l144 / l150 `silW`, the arm behind the paper's
silence-within-cut result) clamps in the window only; the stored-form bisect is
settle-only, so its matched gain IS the base gain — re-bisected here and
asserted equal, not assumed. That arm (`rsilW`) carries the A1 branch because
it is the only relay manipulation with no gain change. `rsilF` is the other
reading; with the clamp in force from t = 0 a silenced cell is dynamically an
absent cell, so `rsilF` should coincide with `rcut` up to the active-fraction
denominator (N vs N−1) — a construction check, not independent evidence.
"Edge-removal" = node removal (the lineage's eAll ≡ cut identity, Methods
§3.8). Fixed-gain twins are added for every graph arm (the brief makes A3's
optional) because L185 showed the re-bisected gain alone moves duty.

Worker plan (fixed, 6 × 2 threads): w0 sc25, sc25F · w1 sc40, sc40F · w2 rcut,
rcutF · w3 rsilW, rsilF (+ cert-only arms on anchor seeds) · w4 pp, ppF · w5
occ, occF.

## Readout and bands (inherited verbatim, no new instrument)

`duty_07` on the Ti pair per side (chopped 0.7-Hz windows). Per arm: kR, kL,
meanR, meanL, Wilson 95%, paired dR vs same-seed cutwA. Bands (n=16):
**SUPER** ("duty rises / flips") meanR >= .60 AND kR >= 12; **NOT-SUPER** ("no
rise") kR <= 8 AND meanR <= .50 (PARTIAL sub-label .35 <= meanR <= .50 AND 3
<= kR); else **INTERMEDIATE** (unresolved, never rounded). Truncation: SUPER kR
>= ceil(.75m), NOT-SUPER kR <= floor(.5m); m < 8 = no branch read.
Paired contrasts: mean difference in duty R on the same seeds, sd, t, 95%
t-CI, counts at ±.20. Descriptive companions (no branch): the same instrument
on the continuous 1.4-Hz middle segment (carrier-removal fingerprint in L184:
.510 vs 0 on the base); window-mean rates of carrier / relay / 74914 per arm;
the gain-null expectation SLOPE_B40 × (arm's gain shift) and the arm's excess
over it (flagged as extrapolated beyond ±.5%).

Power (as L175/L185): a base-like arm is called SUPER with p = 2.4e-4, a
carrier-like arm with p = .9998; a mid-rate arm (.65) lands SUPER .29 /
NOT-SUPER .16 / between .55 — one batch cannot resolve a true mid-rate arm.

## Certification (all must hold BEFORE any B41 value is read)

- **CERT-GEN / CERT-MULTI / CERT-SUB (static, PASS at registration)**: sc25
  generic plumbing == lineage cutng25 field-for-field; the k-cell builder with
  one cell == `add_arm()` (for 1110 and 75494); every graph arm's stepped
  matrix == the base matrix minus the removed rows/columns EXACTLY, with init,
  noise, pool, mech, motor and drive maps equal to the base maps restricted to
  kept cells (this covers the cord-cell removal path the relay exercises).
- **CERT-G**: stored-form bisect returns g_cutwA in EVERY worker, the L175
  stored floats for sc25 and sc40, and g_cutwA for rsilW — all EXACT.
- **C0A-187a (mandatory)**: cutwA @801/901 bit-identical to
  `l135/raw_l135.npz` on 22 trace keys + af in EVERY worker (sc25 vs stored
  cutng25 in w0). Non-zero -> that worker exits before any fresh seed; VOID.
- **C0A-187b**: cutwA (+ sc25 / sc40 in their workers) @3545 bit-identical to
  the stored L175 raws (22 keys + af + full x_mean vector + window x_mean).
- **FC-150 (clamp wiring)**: `silWg` = generic base alias + window clamp on
  the CARRIER, the exact code path `rsilW` uses with a different index, must
  reproduce the lineage's stored `l150` silW @801/901 bit-for-bit (and differ
  from cutwA).
- **CERT-SILCUT (full-clamp wiring)**: at 801/901/3545, `rsilFF` (full-run
  relay clamp at g_cutwA) vs `rcutF` (relay cut at g_cutwA): the 22 traces
  must agree to <= 1e-5 over the first 500 window samples and the clamped
  cell's x_mean must be exactly 0; the full-window maximum is reported.
  A failure voids `rsilF` only (reported, not read); `rsilW` rests on FC-150.
- **CERT-X**: cutwA identical across the 6 workers on all 19 seeds.
- **CERT-METRIC**: the verdict helper reproduces `results_l135.json` (B26),
  the stored `results_l175.json` rows for base / sc25 / sc40 (B39), L184's
  1.4-Hz panel for those three arms, and five `results_l185.json` rows (B40),
  EXACT, before any B41 read.

## Registered branches (read in this order; rematched form unless stated)

0. `E0_base_super` — cutwA SUPER: no claim, everything descriptive.
1. `CTRL_FAIL_carrier` — sc25 not SUPER on B41: "mimics carrier removal" has
   no same-batch reference; A1/A2 labels are printed but DESCRIPTIVE.
2. **A1 (on `rsilW`)**: `R1_conduit` (SUPER: relay silence, carrier present,
   reproduces the rise) / `R2_carrier_specific` (strict NOT-SUPER: no rise) /
   `A1_unresolved` (INTERMEDIATE). `rsilF`'s label is printed beside it.
3. **A2 (on `rcut`)**: same three labels; `rcutF`'s label beside it and
   `A2_gain_form` = AGREE / GAIN_FORM_DEPENDENT. **Relay summary**:
   `CONDUIT_SUPPORTED` = rsilW, rcut AND rcutF all SUPER; `CARRIER_SPECIFIC` =
   all three strict NOT-SUPER; anything else `MIXED`, stated arm by arm.
   **Silence vs cut**: `ECHO` if 0 <= Δ(rsilW) <= Δ(rcut) with Δ = meanR −
   base meanR (silence effect contained in the cut effect, the paper's
   pattern); `NOT_TESTABLE` if neither moves meanR by .10; else `NO_ECHO`.
   The three-way split rsilW − rcutF (history only, same gain), rcutF − rcut
   (gain only), rsilW − rcut is reported.
4. **A3 (on `pp`)**: `R3_cancel` (strict NOT-SUPER: duty ≈ base) / `R3_stack`
   (SUPER) / `R3_partial` (INTERMEDIATE). Under R3_stack the paired pp − sc25
   contrast sub-labels it `above_carrier` / `at_carrier` / `below_carrier` by
   its 95% CI; the duty ceiling limits "above". `ppF` gets the same labels
   beside it. Additivity on the duty scale (Δpp vs Δsc25 + Δsc40) descriptive.
5. **A4**: sc40's class on B41, rematched and fixed; the three-batch pool
   (B39 + B40 + B41, n = 48, scaled bands) is DESCRIPTIVE.
6. **OCC (secondary, both gain forms)**: with the relay absent, does removing
   the carrier still flip? `O1_flip_survives_relay_removal` (occ SUPER while
   relay removal alone is not: the relay is not a necessary conduit) / `O1c`
   (occ SUPER and relay removal alone also SUPER: occlusion, consistent with
   conduit, not diagnostic alone) / `O2_flip_abolished_without_relay` (occ
   strict NOT-SUPER while sc25 SUPER) / `O3_unresolved`.

A conduit claim would need CONDUIT_SUPPORTED and an OCC label that is not O1.
Nothing here licenses a paper edit; FINDINGS states what it would change.

## Predictions (registered, to be scored)

- P1 (.80): controls reproduce — cutwA not SUPER, sc25 SUPER, sc25F SUPER.
- P2 (.60): sc40 rematched is not SUPER, sc40F strict NOT-SUPER, and
  sc40F − sc40 < 0 (its B39/B40 lift is the −1.13% re-bisect, not the cell).
- P3: A1 prior R1_conduit .45 / R2 .30 / unresolved .25; direction (.70):
  meanR(rsilW) > meanR(cutwA). Modal guess R1.
- P4: A2 prior R1_conduit .50 / R2 .25 / unresolved .25. P4b (.75): rcut's
  re-bisected gain shift is NEGATIVE (an active inhibitory cell is removed).
  P4c (.65): meanR(rsilW) <= meanR(rcut). P4d (.85): |meanR(rsilF) −
  meanR(rcut)| <= .03 (gains exactly equal: .50).
- P5: A3 prior R3_stack .70 / partial .20 / cancel .10 — gi 559 is near-silent
  on the base, so it has little to pull with. P5b (.65): |ppF − sc25F| < .10.
  P5c (.65): pp − sc25 >= 0 in the rematched form (pp re-bisects to a lower
  gain than sc25).
- P6 (.55): occ is SUPER (occF .50).
- P7 (.60): CERT-SILCUT full-window maximum <= 1e-3 on all three anchor seeds.

## Scope

One batch for every new arm (L90: a single-batch class is not a class); one
model class; one base (k=24); the chopped 0.7-Hz right-tibia classifier.
Silencing or cutting the relay removes ALL 51 of its outputs and its response
to all 58 inputs, not only the carrier's share of it: R1 would show the relay
is sufficient to reproduce the rise, not that the carrier acts only through
it; that is what the secondary occlusion arm bounds. No relay-matched twin is
run, so a relay effect is not shown to be specific to this interneuron. No
DRAFT / numbers.json / LANE / existing-artifact edit follows.

## Compute and writes

CPU only, 6 worker processes × 2 threads, launched staggered after the L185
done-gate; seeds are the outer loop with an atomic raw checkpoint per seed;
`results_l187.json` is rewritten atomically by the orchestrator as seeds
complete. Writes: `banc/l187/**` and one LAB-INTENT.md §L187 append.
Deviations from the brief's letter, declared: A1 run in two clamp forms with
the window form carrying the branch; fixed-gain twins for all graph arms;
carrier control arms and one extra non-sample anchor seed (3545); a secondary
occlusion arm; three cert-only arms on anchor seeds; per-step traces of three
cells stored for later zero-rollout analysis.
