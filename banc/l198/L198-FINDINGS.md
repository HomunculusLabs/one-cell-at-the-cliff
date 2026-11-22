# L198 FINDINGS — relay-matched cord-interneuron twin (B43 3673-3688, n=16 every arm, FINAL)

**Registered branch: T = T1_relay_special on both gain forms (AGREE), status DESCRIPTIVE** — the registered reference flag came up `REF_relay_not_super`: the relay's own re-matched arm is INTERMEDIATE on this batch (12/16, meanR .584, .016 under the .60 bar), so by PREREG the T-label is printed but not read as a claim. Header: base not SUPER, `CTRL_carrier_ok`. Runner-up panel: 0/6 SUPER, 2/6 INTERMEDIATE, 4/6 NOT-SUPER, 0/6 with the 1.4-Hz signature.
PREREG stage 1 sha c9fff8791fff1161 frozen 18:44:49 before the selection code first ran; selection + FREEZE 18:47:56 before any rollout. Certs green: C0A cutwA == raw_l135 EXACT in all 6 workers (322 checks) + vs L175 raws @3545 (175) + **vs L187 raws @3609 incl. the relay-cut arm itself (276)**, all max 0.0; g_cutwA ×6 / g_sc25 / g_rcut == stored floats EXACT; CERT-X 2200 checks 0.0; CERT-SUB on all six twin graphs; metric reproduces five stored L187 rows (chopped + 1.4-Hz) EXACT.

| arm | removed | gain d% | kR | meanR | class | dR vs base [95% CI] | 1.4-Hz k / mean |
|---|---|---|---|---|---|---|---|
| cutwA | — (base) | 0 | 2 | .319 | NOT-SUPER | — | 0 / .000 |
| sc25 / sc25F | carrier 1110 | +1.244 / 0 | 16 / 15 | .816 / .700 | SUPER / SUPER | +.497 / +.381 | 8 / .471 · 4 / .345 |
| rcut | relay 75494 | −0.126 | 12 | .584 | INTERMEDIATE | +.265 [+.143, +.388] | 0 / .037 |
| rcutF | relay, base gain | 0 | 14 | .642 | SUPER | +.324 [+.230, +.417] | 0 / .037 |
| **tw** | **twin 73008** | −0.401 | 5 | .419 | NOT-SUPER | +.100 [−.020, +.220] | 0 / **.000** |
| twF | twin, base gain | 0 | 1 | .249 | NOT-SUPER | −.070 [−.177, +.036] | 0 / .018 |
| ru1 | 67561 | +1.007 | 8 | .517 | INTERMEDIATE | +.198 [+.049, +.347] | 1 / .082 |
| ru2 | 70994 | −0.300 | 10 | .541 | INTERMEDIATE | +.222 [+.135, +.309] | 0 / .000 |
| ru3 | 64787 | −0.024 | 4 | .331 | NOT-SUPER | +.012 [−.104, +.128] | 0 / .000 |
| ru4 | 67353 | −0.837 | 2 | .244 | NOT-SUPER | −.075 [−.216, +.065] | 0 / .065 |
| ru5 | 71153 | −0.001 | 4 | .431 | NOT-SUPER | +.112 [−.008, +.232] | 0 / .000 |

Twin = gi 73008 (IN17B003-R, inhibitory): drive 86.493 vs the relay's 86.503 (ratio .99988) from the stored 3-seed census, pool 12,385 cord interneurons, none in a prior arm. All six selected cells are inhibitory, none wired directly to the carrier, the relay or gi 74914 (`SELECTION.md`).

## What was measured

1. **The drive-matched twin does not do what the relay does.** Re-matched 5/16 .419, fixed gain 1/16 .249; 1.4-Hz middle value .000 (fixed .018). Paired on the same seeds it sits below the relay in both forms: tw − rcut −.165 [−.301, −.030]; twF − rcutF −.394 [−.509, −.279]. Its small re-matched rise (+.100, CI includes 0) is exactly what its −0.40% re-bisect predicts from the L185 gain-only slope (+.091); at the base gain it is −.070.
2. **The relay's own effect replicated in size, not in label.** dR +.265 re-matched and +.324 at fixed gain (L187: +.283 / +.216), both CIs clear of 0, the relay's downstream cell 74914 disinhibited again (.199 → .426), 1.4-Hz middle .037. But the re-matched arm classes INTERMEDIATE here (12/16 .584) where L187 had SUPER (13/16 .697); the fixed-gain form is SUPER in both batches (13/16 .630, 14/16 .642). Pooled over the two batches (post hoc, `addendum.json`): re-matched 25/32 .641, fixed 27/32 .636 — SUPER on scaled bands; 1.4-Hz .028 / .040.
3. **The class is not uniformly inert (secondary panel, one batch each, re-matched only).** Of six drive-matched inhibitory cord interneurons none reaches SUPER, but two lift the chopped duty with CIs clear of 0: ru2 +.222, ru1 +.198 — 75-84% of the relay's +.265, and neither is separable from the relay on paired seeds (ru2 − rcut −.044 [−.190, +.103]; ru1 − rcut −.067 [−.243, +.109]). The other four are separable (−.154 to −.341). The relay has the largest rise of the seven; six-cell mean +.095, sd .112.
4. **The 1.4-Hz signature stays the carrier's alone.** Carrier removal .471 / .345 (8 and 4 seeds ≥ .5); every other arm ≤ .082, twin .000. Now 6 further cord interneurons on top of L187's relay arms.
5. **Not asked, seen:** removing ru2 (IN07B031-R) flips the LEFT tibia instead — left duty 16/16 .840 (base 0/16 .262) and the carrier's own rate rises .38 → .59. The right-tibia readout this card registers does not see it.

## Reading

L187's caveat is narrowed, not closed. What is supported: a cord interneuron matched to the relay's delivered drive to 1 part in 10^4 leaves the base regime alone at both gains, so delivered drive within the class does not predict the relay's effect, and the relay's rise is the largest of seven such cells. What is not supported: "special to THIS interneuron" as a class statement — two of five further drive-matched cells produce an intermediate rise the relay cannot be told apart from on 16 seeds, and the relay's own re-matched arm sits on the band edge (.697, then .584).

## Caveats

- The registered reference flag failed, so T1 is DESCRIPTIVE by the PREREG's own rule. The paired contrasts in item 1 do not depend on that flag; the label does.
- One batch for every new arm; ru1..ru5 have no fixed-gain form. ru1's rise comes with a +1.0% re-bisect (the L185 gain-only slope predicts a FALL of .23 there, so its excess is larger than its dR — but that is the slope extrapolated beyond ±.5%, and L187 showed the slope's sign depends on the graph).
- Drive matching is not wiring matching: the twin reaches the relay's drive with a lower rate (.146 vs .329) through 151 output edges (relay 51), and none of the six has the relay's direct edge onto a right-Ti flexor motor neuron. Runners-up were rolled as a declared deviation from the brief's single arm.
- Chopped 0.7-Hz right-tibia classifier + the 1.4-Hz panel only. Items 2 (pooling), 3 (vs-relay contrasts), 5 and the gain-null arithmetic are post hoc.

## What it would change (nothing edited)

- Keep L187's wording that the chopped classifier alone is not unique to the carrier; add that it is also not unique to the relay — intermediate rises occur in about a third of drive-matched cord interneurons (2/6), SUPER in none.
- "The relay does it" can be written as: largest chopped-duty rise of seven drive-matched cord-interneuron removals, replicated in size across two batches (+.27 / +.28 re-matched, +.32 / +.22 fixed), absent in its closest drive twin. Not as: unique.
- The conjunction claim is safer than before on its second leg: every carrier-present arm across L187 / L190 / L198 (base, relay, edge, sham, sc40 and seven cord-interneuron removals) shows a 1.4-Hz middle value ≤ .082.

**Next.** (i) fixed-gain forms + a second batch for ru1 / ru2 (are the intermediate rises real at the base gain?); (ii) a twin matched on wiring position (direct right-Ti flexor edge + an input from the carrier) rather than drive; (iii) the ru2 left-tibia flip as its own card.

**Predictions.** Correct: P1 controls, P3 (modal T1), P4 twin 1.4-Hz < .10, P5 ≤ 1 of 6 SUPER (0), P6 gain shift ≤ .5% and gain forms agree. Wrong: P2 — I gave .65 to rcut classing SUPER again; it came in INTERMEDIATE (its 1.4-Hz < .10 half held).

Files: `results_l198.json`, `verdict.out`, `addendum.py/.json/.out`, `selection.json` + `SELECTION.md`, `static.json`, `raw_w0-5.npz`, `xm_w0-5.npz`, `anchors_w0-5.json`, `gains_w0-5.json`, `PREREG.md` + `PREREG.sha256` + `FREEZE.json`, scripts `build_twin.py` → `twin_run.py`, `build_verdict.py` → `verdict_l198.py`, `run_all.sh`. Wall 18:37 → 19:06 (rollouts 18:48-19:05, 6 workers × 2 threads, CPU only).
