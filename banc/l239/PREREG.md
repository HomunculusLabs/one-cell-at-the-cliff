# L239 PREREG — the cutwA MATCHED TWIN

Registered 2026-11-24 ~15:5x EST, tick 273 (CLAIM-INHERIT from tick 272, whose
14:09 run died on HTTP 429 after writing only its CLAIM line), BEFORE any
selection code ran, before the generated script existed, and before any twin
quantity was measured. Static; zero rollouts, zero settles, zero dynamics.

Two-stage freeze (references/gate-jitter-and-twins.md): rule + branches frozen
here FIRST; the picks are then frozen by the run (selection block stored with
its own sha) before any twin statistic is read.

## The question

L178/L206/L211 used a mass-matched twin (gi 290, DNpe005-R = the rank-adjacent
non-glutamatergic descending cell in f4 out-mass) as the size control for the
carrier (gi 1110, DNp33-L). L220 found gi 290 is ABSENT from the base unfloored
cutwA substrate (removed by `keep_wA`), so every cutwA claim currently has a
homolog leg (gi 928) and NO twin leg. Select a twin ON cutwA by a rule derived
from cutwA's own distributions (L212 law: never carry a bar over from another
graph), then re-run the comparison and read the carrier/twin share gap against
the homolog's.

## PREMISE CORRECTIONS (written while scoping, before measuring)

**0a — `rewire_draws` is mask-generic but NOT source-generic.** L220 PREREG 0a
called it "generic in its masks", which is true and was enough there because
the actor was always the carrier. Reading the certified body (l220_static.py
lines 494-555): `GI_CARRIER` is HARD-CODED at line 498 (`pool_rows` excludes
the carrier's rows), and at 532-539 (`sf == GI_CARRIER`, `df == GI_CARRIER`,
`present((GI_CARRIER, df))`, `do_remove((GI_CARRIER, de))`,
`do_add((GI_CARRIER, df))`). So "re-run L220's primary with that twin" cannot
be done by calling the certified function unchanged. Registered repair at the
root: a parameterised kernel `rewire_draws_src(..., gi)` in which every
`GI_CARRIER` becomes `gi`, admitted ONLY by **CERT-239K** — called with
`gi = GI_CARRIER` and the certified cutwA arguments it must reproduce the
certified function's 100 draws EXACTLY (relocated, moved, n_dst, mass_T70,
mass_motor, `cdst` array-equal, `pdst` dict-equal, `car_rows` array-equal),
the CERT-MV / CERT-236K pattern. The certified function itself is still called
for the carrier's draws and re-gated against l169c P6 (CERT-REWCUT, free).

**0b — TWO currencies share the word "share", and the card's 0.0095 is in the
null-free one.** L220's PRIMARY is `share_fh = D_fh/D_total` against 100
destination-swap draws. The homolog gap the card quotes (0.0095) is in
`fh_share_of_si = fh_mean/si_mean`, a WITHIN-SOURCE decomposition needing no
null. Both are computed and kept apart:
* **PRIMARY (the card's deliverable):** the within-source gap
  `G = |share(twin) − share(carrier)|` in `fh_share_of_si` on cutwA, read
  against the stored homolog gap `G_H` and the stored family dispersion.
* **SECONDARY (scoreable):** the twin's OWN decomposition against 100
  degree-neutral destination-swap draws of the TWIN's out-edges (same family,
  same seed 16943), under L220's four bars. This is the first time any
  non-carrier cell in this family gets its own null (L211's limitation: "the
  draws swap the CARRIER's out-edges and are not a null for any other source").

**0c — the matching quantities are defined on the cutwA OPERATOR, not carried
over from the f4 ladder.** L178's ladder used `Σ|log1p(syn)*sign|` over
cord-bound syn>=4 edges. On cutwA there is no floor and the statistic that the
twin must match is the SI index, so: `n_out(c)` = the cell's out-degree on
cutwA (= its SI menu size = END−START in the index), `m_out(c)` = Σ `jv` over
its cutwA out-edges (= the exact normaliser of T; `jv` carries BETA_L on
negative edges). `lm = ln(m_out)`. The raw L178-convention mass (Σ|vals|, no
BETA) is REPORTED beside it for transparency and does not select.

**0d — both bands are DERIVED from cutwA's own distributions at the carrier
(the L212 law), with no carried-over number.**
* Degree band = the carrier's adjacent REALISED rungs: `d_lo` = the largest
  out-degree value that occurs in the candidate pool and is < 80; `d_hi` = the
  smallest that occurs and is > 80. Band `[d_lo, d_hi]`. If 80 itself occurs
  in the pool it is inside the band. This adapts to the local density of the
  degree distribution with zero free parameters. The card's literal "80 +/-
  a derived band" is this.
* Mass bar = the carrier's adjacent gaps in the pool's `lm` ladder:
  `g_lo = lm(car) − lm(next lower)`, `g_hi = lm(next higher) − lm(car)`;
  `B_mass = max(g_lo, g_hi)` (if the carrier tops the ladder, `B_mass = g_lo`).
  A twin within one rung of the carrier's own mass neighbourhood is as matched
  as cutwA's ladder permits there.
* SENSITIVITY (descriptive, no branch): a half-IQR degree band
  `B_deg2 = (Q75 − Q25)/2` of pool out-degree, with its own nearest-in-mass
  pick; reported so a reader can see whether the conclusion depends on the band.

**0e — L212's actor-inside-cohort rule.** The candidate pool EXCLUDES the
carrier (gi 1110) and the bilateral homolog (gi 928: it is the OTHER control,
not a twin), and requires `n_out >= 1`. Asserted structurally and at run time.
The card's premise that gi 290 is off cutwA is VERIFIED in code
(`keep_wA[290]` must be False), not assumed.

**0f — sign class.** L178's rule additionally required non-glutamatergic; the
card says "same super_class". The card is followed: pool = same super_class.
The pick's `is_glut` is recorded; if it differs from the carrier's, the nearest
same-sign candidate in the band is reported as a descriptive alternative.

**0g — carrier-specific masks in the twin's draws.** `mass_T70` and
`mass_motor` in the draw records use the CARRIER's target masks; for the twin
they are computed (to keep the certified record shape) and NOT interpreted.

**0h — same null FAMILY and SEED, different realised draws.** The RNG
consumption depends on the source's edge count, so the twin's 100 draws are not
the carrier's draws. Disclosed; it is the registered null family (seed 16943).

**0i — the family dispersion is a stored quantity, so it is re-derived here.**
CERT-239B reproduces the carrier, the homolog and every cutwA-present L211
actor from this run's own walkers at float equality BEFORE the stored family is
used as a reference.

**0j — relation to L236/L237 declared.** Those cards found the DNp33 deficit is
a TYPE property (the homolog is MORE extreme) in the left-Perron currency. This
card is the search-information currency's twin leg; it cites them and does NOT
re-bank their finding as independent evidence.

## OBSERVATION STATUS (Kriegeskorte 2009; the L214 rule)

Read while scoping, therefore **DESCRIPTION**, never inference: l220/PREREG.md,
l220/VERDICT.md, l220/static.json (carrier on cutwA: fh/si 0.2582827335002662,
si 23.111887364132286, 11 distinct first hops; share_fh −0.013640206885915667;
homolog gi 928 fh/si 0.2488138786594708, stored gap 0.009468854840795404;
36 actor entries / 32 present; family fh-share median 0.2860 [0.2230, 0.3545]),
l220_static.py lines 1-1742, l211_tail.py, l178_tail.py 7-141 (the gi 290 rule:
`ng4[21]`, mass gap 2.4e-05), l212/PREREG.md. On f4wA (L211, stored): carrier
0.2611188191551899, twin 0.30678634491249146, mirror 0.246, family median
0.2834957374928224.

**NOT observed by anyone: the cutwA degree/mass ladders, the candidate set,
the twin's identity, its fh summary, its own null.** Every number the stored
artifact does not carry is quoted in code FROM the artifact, never retyped.

## SELECTION RULE (frozen)

1. Pool `P` = cutwA cells with `super_class == carrier's super_class`,
   `n_out >= 1`, excluding gi 1110 and gi 928.
2. `C = {c ∈ P : d_lo <= n_out(c) <= d_hi}` (0d).
3. `twin = argmin_{c ∈ C} |lm(c) − lm(car)|`; ties broken by smaller gi.
4. Quality: `TW_TIGHT` if `|Δlm| <= B_mass`; `TW_LOOSE` if a twin exists but
   `|Δlm| > B_mass`; `TW_NONE` if `C` is empty; `TW_DEGENERATE` if the twin
   reaches no cutwA pool cell (`fh_summary is None`).
5. Recorded for the pick: gi, cell_type, side, is_glut, n_out, Δn_out, m_out,
   Δlm, rank distance in the lm ladder, membership in L211's 33-cell family.

## Branches

**Quality (above): TW_TIGHT / TW_LOOSE / TW_NONE / TW_DEGENERATE.**
The card's registered escape: if no candidate clears both bars, say so and
report the homolog as the only available control — a missing twin named is
worth more than a loose one accepted. Under TW_NONE / TW_DEGENERATE no primary
gap is reported. Under TW_LOOSE the gap is reported and LABELLED loose.

**PRIMARY (scored only under TW_TIGHT or TW_LOOSE), on
`G = |share(twin) − share(carrier)|`:** with `G_H` = the stored homolog gap and
`D_fam` = median over the cutwA-present L211 family of `|share(a) − share(car)|`
(the distance of a typical same-class cell from the carrier; both derived in
code from l220/static.json):
* **TW_HOMOLOG_LIKE** — `G <= G_H`: the matched twin agrees with the carrier
  at least as well as the bilateral homolog does.
* **TW_FAMILY_LIKE** — `G_H < G <= D_fam`: size + class do not reproduce the
  carrier's share; the twin sits a typical family distance away while the
  homolog is closer.
* **TW_OUTSIDE_FAMILY** — `G > D_fam`: the twin is farther from the carrier
  than the median family member.

**SECONDARY (scored whenever the twin has 100 usable draws), L220's bars
unchanged on `share_fh(twin) = D_fh/D_total` against the twin's own draws:**
T_TRANSPORTS (`<= 0.40`), T_INVERTS (`>= 0.60`), T_SPLIT, T_DEGENERATE
(`D_total <= 0`, non-finite, or a draw with no reachable pool cell).

## Predictions (scored, never amended)

* **P1** — primary branch **TW_FAMILY_LIKE** (the f4wA pattern: homolog close,
  mass twin not).
* **P2** — quality is **NOT tight** (TW_LOOSE or TW_NONE): the carrier is a
  thick-edged heavy DN, so a cell with a neighbouring out-degree and a
  neighbouring out-mass is not expected to exist.
* **P3** — secondary branch **T_TRANSPORTS** (remainder dominance is generic
  for heavy same-class cells, not carrier-specific).
* **P4** — the funnel transports to the twin: `n_distinct_first_hops(twin) <=
  0.35 * n_out(twin)` (L221 put the carrier's funnel at cohort percentile
  0.286, i.e. typical).
* **P5** — band-robust: the half-IQR sensitivity pick (if different from the
  primary pick and non-degenerate) lands in the SAME primary branch.

## Gates (all HALTING)

1. **PARENT PIN** — `l220/static.json["banner"]` equals the first 13 lines of
   `l220_static.py` (the generated script's own banner inside the artifact it
   produced), and `l220_tail.py` is a literal SUFFIX of the parent whose sha
   equals the TAIL sha that banner records.
2. **SLICE** — `l239_static.py` head = `l220_static.py` lines 1-1587 as a
   literal prefix (ends after `IX_CUT` is built), write-free BY AST; the cut
   region owns the parent's only `json.dump`.
3. **CERT-239A** — every leaf of `l220/static.json` under the keys the slice
   assigns reproduced from this run's own `o` at FLOAT EQUALITY, on a coverage
   bar DERIVED from the artifact's own leaf count (L224/L234: a stored leaf
   count, not an internal check count).
4. **CERT-REWCUT (free)** — the certified `rewire_draws` on the cutwA block
   reproduces l169c P6.
5. **CERT-239K** — the parameterised kernel equals the certified one exactly
   on the carrier (0a).
6. **CERT-239B** — carrier, homolog and every cutwA-present L211 actor
   reproduced at float equality from this run's walkers (0i).
7. **CERT-239W** — the twin walker equals `dijkstra_si` exactly on every pool
   cell, for the twin and all 100 of its draws.
8. **CERT-239N** — the null kernel applied to the CARRIER reproduces L220's
   stored `null_mean`, `null_median`, `null_spread`, `percentiles`, D_total,
   D_fh, D_rem and share_fh at float equality BEFORE it is applied to the twin.
9. **CERT-REBIND** — f4wA values bit-identical after restoring the globals.
10. Structural: twin ∉ {1110, 928}; `keep_wA[290]` False; additivity
    `< 1e-9`; finiteness of every reported mean; one write site.
11. Read-only priors md5'd before and after.

## Named limits

* ONE substrate (cutwA), ONE operator (g = 1, `|W_beta|`), ONE null family
  (degree-neutral destination swaps, seed 16943) — L207's law.
* A single twin answers "is THIS matched cell like the carrier", not "how
  often" (the registered runners-up would cost one null each; not run).
* The first-hop menu is invariant across a source's own draws (L220 CERT-MENUCUT
  for the carrier; re-measured for the twin), so `D_fh` is SELECTION among a
  fixed menu by construction, never allocation.
* The degree band is the distribution's own resolution at degree 80; a reader
  who prefers a caliper should read the half-IQR sensitivity leg.
* Selected-unit caveat: the carrier was selected for an extreme SI; the twin
  leg is a control on that selection, not an independent test of it.
