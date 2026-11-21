# L187 FINDINGS — relay (gi 75494) silencing + cut, push-pull, sc40 control (B41 3609-3624, n=16 every arm, FINAL)

**Registered branches** (PREREG sha256 98034281b435e961, frozen 12:28:05 before any rollout; L185 done-gate checked 12:25:49): header CONTROLS_OK · **A1 = A1_unresolved** · **A2 = R1_conduit** (both gain forms, AGREE) · relay summary **MIXED** · silence-vs-cut ECHO · **A3 = R3_stack** (rematched `below_carrier`, fixed `above_carrier`) · **A4 = INTERMEDIATE** rematched / NOT-SUPER fixed · OCC (secondary) = O1c both forms.
Certs green: C0A cutwA == raw_l135 EXACT in all 6 workers (322 checks, max 0.0) + vs L175 raws @3545 (200, 0.0); g_cutwA x6 / g_sc25 / g_sc40 == stored floats EXACT; FC-150 clamp path == stored l150 silW (48, 0.0); CERT-X 2375 checks 0.0; metric reproduces l135 / l175 / l184 1.4-Hz panel / l185 rows EXACT.

| arm | manipulation | gain d% | kR | meanR | class | dR vs base [95% CI] | 1.4-Hz k / mean | relay rate |
|---|---|---|---|---|---|---|---|---|
| cutwA | base | 0 | 6 | .414 | not (partial) | - | 0 / .001 | .320 |
| sc25 / sc25F | carrier removed | +1.244 / 0 | 16 / 16 | .810 / .715 | SUPER / SUPER | +.396 / +.301 | 9 / .530 · 7 / .432 | .138 / .133 |
| rsilW (A1) | relay clamped, window only | 0 (identity) | 12 | .591 | INTERMEDIATE | +.177 [.036, .318] | 0 / .057 | 0 |
| rcut (A2) | relay removed | -0.126 | 13 | .697 | SUPER | +.283 [.150, .417] | 0 / .020 | - |
| rcutF | relay removed, base gain | 0 | 13 | .630 | SUPER | +.216 [.111, .321] | 0 / .042 | - |
| pp (A3) | carrier + gi 559 removed | -0.809 | 12 | .605 | SUPER | +.191 [.057, .325] | 3 / .242 | .165 |
| ppF | same, base gain | 0 | 16 | .792 | SUPER | +.378 [.280, .475] | 7 / .435 | .155 |
| sc40 / sc40F (A4) | gi 559 removed | -1.131 / 0 | 11 / 2 | .567 / .329 | interm. / NOT | +.153 / -.085 | 0 / .000 | .348 / .355 |
| occ / occF | carrier + relay removed | +1.066 / 0 | 16 / 15 | .839 / .730 | SUPER / SUPER | +.425 / +.316 | 16 / .729 · 13 / .595 | - |

## What was measured

1. **Relay removal alone raises the chopped duty, carrier present.** Cut: 13/16 at both gains (.697 rematched, .630 fixed; its re-bisect moved only -0.126%). Window-clamp silence: 12/16, meanR .591 — the kR leg passes, the meanR leg misses the .60 bar by .009, so A1 is unresolved by the registered band, in the same direction (+.177, CI excludes 0). Silence vs cut at the same gain: -.039 [-.171, +.093], not resolved; the ordering base < silence <= cut matches the paper's pattern (ECHO), weakly.
2. **It is not a copy of carrier removal.** (a) Chopped duty is lower than the carrier's on the same seeds: rcut - sc25 -.112 [-.228, +.003]; rcutF - sc25F -.085 [-.204, +.034]. (b) The carrier's 1.4-Hz middle-segment signature (L184) is absent: .020-.057 for the three relay arms vs .530 / .432 for carrier removal (base .001). This panel is the registered descriptive companion, not a branch.
3. **The carrier's effect does not need the relay** (secondary arm). With the relay already gone, removing the carrier still adds +.142 [.056, .228] chopped duty (fixed gain +.100 [-.028, +.228]) and the whole 1.4-Hz signature: +.709 [.617, .801] rematched, +.553 [.453, .653] fixed, 16/16 seeds positive. Relay loss on top of carrier loss raises the 1.4-Hz duty further (+.199 [.056, .342]; fixed +.163 [.016, .310]). Registered label O1c ("not diagnostic alone" on the chopped classifier, where both arms sit near the ceiling); the 1.4-Hz contrasts are post hoc (`addendum.py`).
4. **Push-pull does not cancel.** At the base gain ppF is 16/16 .792, +.076 [.007, .146] ABOVE carrier removal, with an identical 1.4-Hz duty (.435 vs .432). Removing gi 559 lifts the relay only from .138 to .165 (fixed .133 to .155): the opposite-sign input exists but restores about an eighth of the carrier-induced drop, because gi 559 is near-silent on the base (x_mean .034).
5. **The rematched push-pull arm drops to the band edge (12/16 .605, -.205 [-.301, -.108] vs sc25) and that tracks gain, not the cell.** pp re-bisects to -0.81% while sc25 re-bisects to +1.24%. Post hoc: in all three carrier-absent graphs duty RISES with gain (rematched - fixed: sc25 +.094 at +1.24%, occ +.109 at +1.07%, pp -.187 at -0.81%; slopes +.008 to +.023 per +0.1%); in the carrier-present graphs it falls (sc40 -.021, rcut -.053 n.s.; L185 base null -.023). The sign of the gain sensitivity flips with the carrier.
6. **A4:** sc40 rematched 11/16 .567 INTERMEDIATE, fixed 2/16 .329 NOT-SUPER (fixed - rematched -.238 [-.360, -.116]). Three batches now: rematched 34/48 .570 INTERMEDIATE; fixed 5/32 .335. Its lift is its -1.13% re-bisect, as L185 found.
7. **Construction identity:** a relay clamped from t = 0 IS the relay-cut graph — 22 traces bit-identical (max 0.0) at 3 anchor seeds, and `rsilF` re-bisects to the same float as `rcut` (0.14347783327102664) and equals it on all 16 fresh seeds. A1b therefore adds no evidence to A2; any silence-vs-cut gap is settle history plus gain.

## Reading

Neither registered pole. The relay is not the carrier's necessary conduit (item 3), and silencing it does not reproduce the carrier phenotype (item 2); but it is not inert either — removing this one cord interneuron raises the chopped classifier into the SUPER band on its own (item 1). L184's 4-edge chains through 75494 remain a candidate route, not the mechanism: the chain's interior cells 71392 / 74468 / 64322 are silent on the base, and the relay's actual downstream change is a disinhibition of gi 74914 (.200 base -> .43 relay-off; .35 carrier-off; .48-.49 both).

## Caveats (bound how hard any of this can be leaned on)

- One batch for every new arm (L90). rsilW and pp sit ON the band edge (meanR .591 and .605; kR 12 each): a second batch can move either label.
- **No relay-matched twin.** L175's null was built from descending window cells; nothing here says how often removing an active inhibitory cord interneuron lifts chopped duty. "The relay does it" is not shown to be specific to 75494.
- Relay arms remove all 51 outputs and the response to all 58 inputs, not the carrier's share. The direct test — cutting the single carrier->relay edge (21 syn) — was not run.
- Chopped 0.7-Hz right-tibia classifier; the 1.4-Hz panel, the gain-slope sign and the per-graph rates are descriptive / post hoc. Rule deviations are declared in PREREG (two clamp forms, fixed twins for all graph arms, occlusion arm, extra anchor seed, cert-only arms).

## What it would change (nothing edited)

- Do not write that the carrier acts through 75494. Supported wording: "a downstream interneuron on the carrier's route raises the chopped duty when removed, without the carrier's 1.4-Hz signature, and the carrier's effect survives its removal (one batch)."
- The identity claim's scope is "among descending window cells + twins": a cord interneuron reaching SUPER on the chopped classifier means that classifier alone is not unique to the carrier. The 1.4-Hz signature separated them here (carrier-absent arms .24-.73, every carrier-present arm <= .06).
- Compound or cross-regime arms should lead with the fixed-gain form: re-matching pushes carrier-present and carrier-absent graphs in opposite directions (item 5).

**Next.** (i) second batch for rcut / rcutF / rsilW / occ; (ii) drive-matched cord-interneuron twins for the relay; (iii) single-edge cut 1110->75494; (iv) per-step traces of cells 1110 / 75494 / 559 are stored for every arm and seed (`c<gi>_<arm>_<seed>`), so L184's phase question costs zero rollouts.

**Predictions.** Correct: P1 controls, P2 sc40, P4 A2 = R1 (and gain shift negative, silence <= cut, full clamp == cut), P5 stack, P5b ppF at carrier (+.076 < .10), P6 occ SUPER, P7. Wrong: P3 (A1 modal R1; it landed unresolved, direction right), P5c (I expected pp >= sc25 rematched; it is .205 below — I applied the base graph's gain slope to a carrier-absent graph).

Files: `results_l187.json`, `verdict.out`, `addendum.json/.out`, `raw_w0-5.npz`, `xm_w0-5.npz`, `anchors_w0-5.json`, `gains_w0-5.json`, `static.json`, `PREREG.md` + `PREREG.sha256`, `L185_DONE.txt`, scripts `build_relay.py` -> `relay_run.py`, `build_verdict.py` -> `verdict_l187.py`, `run_all.sh`. Wall: 12:13 -> 12:45 (rollouts 12:28-12:42, 6 workers x 2 threads, CPU only).
