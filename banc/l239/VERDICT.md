# L239 VERDICT — the cutwA matched twin exists now: gi 339 (DNp57-R)

Run 2026-11-24 15:46-15:47 EST, tick 273. `l239_static.py` sha256 `5b044427264a39bd`
(2,586 lines = `l220_static.py` 1-1587 VERBATIM + `l239_tail.py` with 9 parent blocks
spliced). Artifact `l239/static.json` sha256 `452bf45dba10aa84`. PREREG frozen before
the selection code existed: sha256 `3352c352bcc3df6d` (stored in the artifact and equal
to the file on disk after the run). Zero rollouts, zero settles, zero dynamics.

## Certification (all halting, all GREEN, `l239/run.out`)

| gate | what it proves | count |
|---|---|---|
| PARENT PIN | `l220_tail.py` is a literal suffix of `l220_static.py`; slice write-free | 2007 lines, tail sha `8620a357d74f6f3e` |
| CERT-239A | 18 slice keys of `l220/static.json` reproduced at float equality (bar derived from the artifact: 753; floor 674) | 753 leaves |
| CERT-REWCUT | cutwA null = the `l169c` native null (100 draws, seed 16943) | 31 |
| CERT-239K | source-parameterised kernel == certified `rewire_draws` on all 100 carrier draws | 800 |
| CERT-MENUCUT | 80-edge first-hop menu bit-identical in all 100 draws | 100 |
| CERT-239N | null kernel reproduces all 100 verbatim L220 draws AND L220's whole primary block (T_TRANSPORTS, share_fh -0.013640) | 1061 |
| CERT-239B | L220's cutwA cohort re-derived from this run's own walkers | 357 |
| CERT-239W | `dijkstra_si` == first-hop walker for twin + all usable draws | 61206 |
| CERT-REBIND | f4wA values bit-identical after rebinding globals to cutwA and back | 606 |

Prior artifacts opened read-only; `md5sum -c l239/prior.md5` OK before and after.

## Selection (frozen before any twin statistic: sha `a8e81fea0ed1daba`, recomputed from the stored block after the run)

- pool: 1,262 descending-projection cells on cutwA (carrier + homolog 928 excluded)
- degree band = the carrier's adjacent realised rungs: [79, 81], 13 cells
- mass bar B_mass 0.0023 -> **no cell in band is mass-tight**
- pick: **gi 339, DNp57 right**, n_out 81, lm gap 0.0453 -> **TW_LOOSE**
- runner-up gi 592 (lm gap 0.0519). Rule and branches were written before the
  selection code existed, so TW_LOOSE is the rule's honest yield, not a rescue.

## Primary: G = |fh_share(twin) - fh_share(carrier)| on cutwA -> **TW_FAMILY_LIKE**

| | gi | n_out | si | fh | rem | fh/si | distinct fh |
|---|---|---|---|---|---|---|---|
| carrier | 1110 | 80 | 23.1119 | 5.9694 | 17.1425 | **0.2583** | 11 |
| homolog | 928 | - | 25.0485 | 6.2324 | 18.8161 | 0.2488 | 9 |
| cutwA twin | 339 | 81 | 21.4739 | 5.8855 | 15.5884 | **0.2741** | 12 |

G 0.01579 | homolog gap 0.00947 | family median distance 0.03115 (30 members, 3 within
the homolog gap). The twin sits closer to the carrier than the typical family
member, but ~1.7x the homolog gap: "family-like", not "indistinguishable".

For reference (pattern being re-run): on f4wA the L178 twin gi 290 read fh/si
0.3068 vs carrier 0.2611 = G 0.0457 against a homolog gap 0.0148.

## Secondary: the twin's OWN null (first null any non-carrier cell of this family has had) -> **T_TRANSPORTS**

Same family and seed (16943), 100 degree-neutral destination-swap draws, kernel
admitted by CERT-239K, loop gated by CERT-239N.

- D_total +2.5126 bits, D_fh -0.1287, D_rem +2.6412 (additivity 8.9e-16)
- **share_fh -0.0512** -> T_TRANSPORTS (bar: transports <= 0.40)
- percentiles: si 100 / fh 19 / rem 99 / hop 100 / dist 63
- funnel: twin 12 distinct first hops of 81 edges vs null median 15 (ratio 0.148)
- menu invariant 100/100 draws; 0 unreachable draws

So the L220 carrier/twin share holds on cutwA: a degree-matched non-homolog shows the
same sign, i.e. "remainder information, not first-hop selection" is not special to
the carrier.

## Predictions: 4 true / 1 false

1. primary TW_FAMILY_LIKE — TRUE
2. quality not tight (TW_LOOSE) — TRUE
3. secondary T_TRANSPORTS — TRUE
4. funnel ratio <= 0.35 (read 0.148) — TRUE
5. band robustness (half-IQR band pick lands in the same primary branch) — **FALSE**

## The caveats that matter

1. **The twin reading is BAND-DEPENDENT, and the alternate call is marginal.** The
   half-IQR band (B_deg2 33.5, 380 cells) picks gi 409: n_out 90, lm gap 0.00078
   (58x tighter in mass than the primary pick, but 9 more out-edges: log2 90 =
   6.49 bits vs log2 81 = 6.34), fh/si 0.2911 -> TW_OUTSIDE_FAMILY with distance
   0.0328 against the 0.0311 bar — **by 5%** (L238's companion lesson: report the
   margin beside the branch). Two defensible picks straddle the bar on the same
   substrate: G 0.0158 (degree-matched, loose in mass) vs 0.0328 (mass-tight,
   9 more edges). Mass alone does not make a twin; the degree match carries it.

2. **The primary branch has a ~54% base rate inside the band.** All 13 in-band
   candidates were scored (descriptive, after the pick, none selected on it):
   7 TW_FAMILY_LIKE / 6 TW_OUTSIDE_FAMILY; 0 of 13 within the homolog gap
   (gap_min 0.0135, gap_med 0.0302). "Family-like" alone is therefore weak
   evidence about mass matching.

3. **DESCRIPTION, post-hoc, UNREGISTERED — no branch reads it.** Inside the band
   the gap grows with the mass gap: Spearman(lm_gap, gap_vs_carrier) = +0.5879
   over 13 cells (13 distinct values each side); the top 8 by mass are 7/8
   family-like, the bottom 5 are 0/5. That is the pattern "at fixed degree,
   nearer out-mass -> nearer first-hop share", seen after the fact on 13 cells.
   It is the thing to REGISTER next (wider band, candidates not yet scored,
   Monte-Carlo null at n=13), not a result of this card.

This agrees with L220's lesson (menu size moves the uniform baseline) and with
L212's (never carry a bar across graphs).

## Limits

- Timestamp disclosure: the PREREG header self-dates "~15:5x EST", which is
  wrong — the file was written at 15:28 EST (its mtime), before the build
  script, the first generated `l239_static.py` and every run (first attempt
  15:42, green run 15:46-15:47). The freeze rests on the ORDER, and the order
  is right; the frozen file is not edited because its sha is recorded in the
  artifact (`3352c352bcc3df6d`).
- TWO substrates, one operator (g=1 anatomical |W_beta|), one null family, one seed.
- The pick is loose in mass (0.0453 vs bar 0.0023): the rule is degree-first by
  design, and on this pool that costs mass tightness.
- `L239_sign_class` is a description only (twin and carrier both non-glutamatergic;
  no null, no branch reads it).
- f4wA vs cutwA magnitudes are not compared; only the within-substrate shares are.
- Three aborted attempts before the green run are kept (`run_attempt{1,2,3}.*`):
  (1) a wrong write-site invariant, (2) a hand-typed leaf count, (3) a numpy bool at
  `json.dump`. None reached a different number; attempt 3's log carries the same frozen pick
  (gi 339) but printed no share before the write, so it is evidence of the same
  pick, not of the same share.

## Files

`banc/l239/{PREREG.md, prior.md5, run.out, run.err, static.json, run_attempt*.out/.err}`,
`banc/l239_tail.py`, `banc/l239_build.py`, `banc/l239_static.py`.
