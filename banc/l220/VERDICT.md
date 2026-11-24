# L220 VERDICT — the L211 split TRANSPORTS to the unfloored substrate

Run 2026-11-23, tick 250. `l220_static.py` (2,007 lines, generated), 43 s,
CPU, zero rollouts / settles / dynamics. PREREG `l220/PREREG.md` registered
first. Artifacts: `l220/static.json`, `run.out`, `run.err`, `prior.md5`.

## Branch: **T_TRANSPORTS** (registered). Predictions **5 of 5**.

| | f4wA (floor 4) | cutwA (base, no floor) |
|---|---|---|
| cells / edges | 21,789 / 469,618 | 21,785 / 644,177 (+37.2% edges) |
| carrier out-degree | 69 | **80** |
| carrier SI mean (bits) | 22.39318 | **23.11189** |
| first hop | 5.84728 | 5.96940 |
| remainder | 16.54590 | 17.14249 |
| fh / si (no null needed) | 0.261119 | **0.258283** |
| D_total vs 100 draws | +3.58157 | **+3.90518** |
| D_fh | −0.02012 | −0.05327 |
| D_rem | +3.60169 | +3.95844 |
| **share_fh = D_fh/D_total** | −0.005619 | **−0.013640** |
| percentiles si / fh / rem | 100.0 / 45.0 / 100.0 | 99.0 / 30.0 / 99.0 |
| realised distinct first hops | 11 of 69 | **11 of 80** |
| branch | B_REMAINDER | **T_TRANSPORTS** |

Additivity exact (`|D_total − (D_fh + D_rem)| = 0.0`). The remainder carries
**101.4%** of the cutwA excess (100.6% on f4wA).

## 1. The most damaging counterfactual to L211 is refuted, and it goes the other way

T_INVERTS would have made L211's remainder dominance a synapse-floor artifact.
Removing the floor adds 174,559 edges (+37.2%) and 11 carrier out-edges, and
`share_fh` moves by **0.0080** — from −0.0056 to −0.0136, i.e. further from
first-hop dominance, not toward it. The split is substrate-independent.

More than that, the **excess GROWS without the floor**: D_total +3.5816 →
+3.9052 bits (+9.0%). The carrier's own SI rises +0.7187 bits while its null's
mean rises only +0.3951, so the unfloored wiring makes the carrier's route
*more* expensive relative to relocation. The floor was suppressing part of
L206's effect, not manufacturing it.

## 2. PREREG 0b earned its place: the bare bits difference has the WRONG SIGN

The carrier's first hop costs **+0.1221 bits MORE** on cutwA (5.9694 vs
5.8473), which read bare says its first-hop choice got worse. But its own
uniform-allocation baseline moved **+0.2134 bits** (log2 80 = 6.3219 vs
log2 69 = 6.1085). Against its own baseline:

    fh − log2(out-degree):  −0.26124 (f4wA)  →  −0.35253 (cutwA),  Δ −0.09128

the carrier's first-hop **selection advantage below uniform GREW by 0.0913
bits**. Consistently, its first-hop percentile against its own null drops
45.0 → 30.0 (still inside (5,95), so not a claim).

**Transportable method law:** when the menu SIZE changes between substrates, a
bare bits difference reports the OPPOSITE SIGN of the selection effect.
Subtract each substrate's own `log2(out-degree)` before any cross-substrate
first-hop comparison. Registered in the PREREG *because* the out-degree pin
(80) was readable in advance — which is also why it is description, not a
finding.

## 3. The 11-way funnel is an invariant across substrates

The carrier realises **exactly 11 distinct first-hop costs on BOTH
substrates** — out of menus of 69 and 80 — while the null median is **16.0 on
both**. Adding 11 out-edges did not widen the funnel at all. Whether those are
the *same* 11 targets is not measured here (the identities were not recorded)
and is seeded as L238; this is L221's subject matter arriving with a second
substrate for free.

## 4. PREREG 0a: the card's dilemma was false — the null is NATIVE to cutwA

The card offered "re-run the l169c swap on cutwA, or the leg is descriptive".
Inspection of the inherited machinery showed `CERT-REW` already calls the
certified `rewire_draws` with the **wA** block (`_blk_wA`, `_sel_car_wA`, seed
16943) and gates it against `l169c/static.json` — the f4wA null L206/L211 used
is the *derived* one. So the certified function was called UNCHANGED with its
certified cutwA arguments and gated at float equality (**CERT-REWCUT, 31
checks**) before any SI number was read. The primary is scoreable.

## 5. PREREG 0c: the gain no-op MEASURED clean (contrast L218)

`L = −log10(A/A_max)` and `T = A/s_out` are mathematically invariant to a
positive global rescale of A, so f4wA's G-scaled operator and cutwA's g=1
operator are the same index in exact arithmetic. L209's law says measure it:
max |ΔL| **2.22e−16**, max |ΔT| **4.44e−15**, carrier si_mean rel **1.59e−16**,
and `fh_share_of_si` **bit-identical** (0.2611188191551899 both ways). Here the
no-op is a genuine no-op — which is what licenses the cross-substrate read.
L218's cancelling factor moved the last bit and halted a gate; the discipline
is to measure, not to predict which way it falls.

## 6. The bilateral homolog agrees BETTER on the unfloored substrate; the TWIN does not exist there

4 of the 35 L211 actors are absent from cutwA — **including the matched twin**
(GI 290, DNpe005-R, removed by `keep_wA`). f4wA was constructed to contain it;
the base substrate is not. Named as a limitation, not worked around.

The mirror homolog gi 928 **is** present: `fh_share_of_si` 0.248814 vs the
carrier's 0.258283, gap **0.0095** (0.015 on f4wA) — the L207/L212 homolog leg
for free, agreeing slightly better without the floor. Cohort (DESCRIPTIVE, 31
ranked): carrier fh-share 0.2583 vs family median 0.2860 [0.2230, 0.3545];
carrier remainder rank 28/31 (32/35 on f4wA).

## 7. What the null cannot move, named before decomposing (L211's law)

**CERT-MENUCUT**: the 80-edge first-hop menu is bit-identical in all 100 cutwA
draws (median **80 of 80** out-edges relocated per draw, min ≥ 1). So on cutwA
too, `D_fh` can only be SELECTION among a fixed menu — it is NOT evidence about
how the carrier allocates out-weight.

## Disclosures

* `reach` percentile reads 0.0 because the carrier **and every draw** reach all
  303 pool cells (median 303.0); `_pct` is a strict `<`, so this is a TIE, not
  a deficit. Saturated readout, reported as such.
* `si` percentile 99.0 (not 100.0) = exactly one of 100 cutwA draws is at or
  above the carrier's SI. The effect is slightly less extreme than on f4wA
  while the *magnitude* is larger — L207's law: percentiles are
  resolution-limited at 100 draws.
* Two substrates, one operator family, one null family (seed 16943). This card
  tests transport of a dimensionless SHARE, never of a magnitude.
* SI length divides by A_max (domain choice) and L-ties break by heap order —
  inherited from L206 unchanged.
* This is L211's own deferred leg. It cites L211 and does NOT re-bank L211's
  finding as independent evidence.

## Certification

**64,296 halting equalities in this card's five new gates**, on top of L211's
62,159 and L206's/L178's re-running free inside the verbatim slices.

| gate | kind | n |
|---|---|---|
| CERT-211 (required anchor) | float equality, recursive leaf | **434** |
| CERT-SIGEN | exact list/array equality | **1,922,356** |
| CERT-REWCUT | float equality vs l169c P6 | **31** |
| CERT-MENUCUT | bit-identical menu / 100 draws | **100** |
| CERT-WALKCUT | exact equality, cutwA walkers | **61,206** |
| CERT-REBIND | bit-identical f4wA after round trip | **606** |
| CERT-SI (free in slice) | float equality vs l206 | 240 |
| CERT-FH (free in slice) | exact equality | 61,819 |
| CERT-MENU (free in slice) | 100 draws | 100 |
| CERT-GEN / CERT-178 / CERT-NULL / CERT-F4 / CERT-REW | free in heads | — |

* **CERT-211** reproduced L211's entire `L211_primary` + `L211_cohort` from my
  own re-run at float equality BEFORE any cutwA number was read. That is what
  licenses calling this a transport test rather than a fresh measurement.
* **CERT-SIGEN** certifies ONE generic SI-index builder against the certified
  f4wA specialisation on `START`, `END`, `L_L`, `T_L`, `TGT0`,
  `pos_in_sorted`, `A_max` by exact list/array equality **before** it is
  applied to cutwA (the CERT-MV / L44 discipline the card asked for).
* **CERT-REBIND** is what makes the card's "call the UNCHANGED certified
  dijkstra on the rebound globals" safe: after rebinding the module globals to
  cutwA and restoring them, `dijkstra_si(LC_CAR, TGT0)` is bit-identical on
  every one of the 303 f4wA pool cells.
* **NINE verbatim source slices**, forbidden-token audited, no lab module
  imported (L175), with **seven inherited sha pins** asserted by the builder
  plus a **PARENT PIN**: `l211_tail.py`'s whole-file sha256 must equal the TAIL
  sha `l211_static.py`'s own generated banner recorded
  (`01344b557db98d29` GREEN), or the CERT-211SL slice would not be the code
  that produced the stored table CERT-211 certifies against.
* `CERT-211SL = l211_tail.py 29-322` is sliced to **CUT** L211's own
  predictions/certification/writer block (L213's pattern), asserted POSITIVELY
  (CERT-SI, CERT-MENU, CERT-FH, both walkers, `_pct`, both `o[...]` blocks)
  and NEGATIVELY (`o["predictions"]`, `o["pins"]`, `FP_SRC`, `json.dump`,
  `L211 DONE`).
* Four prior artifacts opened READ-ONLY with `(size, mtime_ns)` fingerprinted
  before and asserted unchanged after; `md5sum -c` GREEN against
  `l220/prior.md5` (12 files) before the run.
* Generated sha256 `bbbd7154633774b2`.

## Seeded follow-ons

* **L238** — are the 11 realised first hops the SAME 11 targets on both
  substrates? Record the target identities and the per-target contribution,
  nonselectively over all 31 cutwA-present actors with BH-FDR.
* **L239** — the twin is absent from cutwA. Select a matched-degree,
  matched-out-mass twin ON cutwA by the L212 cohort-quality rule derived from
  cutwA's OWN degree distribution, and re-run the homolog leg properly.
