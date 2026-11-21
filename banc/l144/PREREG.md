# L144 PREREG — sil1110-on-wA-base (registered BEFORE the build/run)

Item: LANE.md ideas 75 / L144. The one missing cell of the L141/L142 grid:
clamp X[1110]=0 (L137 sil form VERBATIM: window-loop only, after the X
update, before readouts; settle clamp-free) on the cutwA window base.
L141 ran the clamp on the INTACT closure (nothing moved, dR -.088);
L142's EDGE cuts ran on this wA base (everything flips). Same substrate,
activity-vs-edges split — the two-factor law's cleanest statement.

## Substrate & machinery

- Base graphs VERBATIM l142: full (closure, G_NEW .153125), cutwA window
  (n 21785, stored gain .14365819573402408), cutng25 (stored
  .1454454553127289), b65 (G65). No fresh bisects except the two
  stored-form re-bisect asserts (cutwA/cutng25 EXACT, STOP on drift).
- ARMS (6): `full`, `b65`, `cutwA`, `cutng25`, `sil1110` (full graph +
  clamp [loc_n[1110]]), `sil1110_wA` (cutwA graph + clamp [loc_wA[1110]],
  gain == cutwA's stored gain — same node set + same gain ⇒ settle af ==
  cutwA EXACT; no independent bisect by construction, DISCLOSED).
- sil arms alias their BASE's POOLS/mech/motor/dng100/WB/N_OF; noise
  sil1110=nzn (full-form), sil1110_wA=nzn[wA_pos_in_new] (cutwA-form).
- Spectator arms (cut/cut19/cut58/cutk5/cutng19/cutng23/cutng25p/
  cutng26/cutng29) keep graphs/pins verbatim, never advanced (l139 law);
  l142's FIVE edge arms are DELETED (not spectated) — residual scan.
- Fresh batch B30 = 3317-3333-1 = 3317..3332 (18 seeds incl. anchors
  801/901 FIRST). Asserted absent from ALL stored npzs l107..l142
  (incl. l142 raws) before any read.

## Criteria (VERBATIM L118-L131, same code path as l142_verdict)

KILL: meanR <= m0 - .10 AND kR <= 4 AND mean_paired_dR <= -.20.
RESTORE: meanR >= .45 AND kR >= 12. SUPER: meanR >= .60 AND kR >= 12.
PARTIAL band: .35 <= meanR <= .50 AND 3 <= kR <= 8. m0 = full's meanR on
B30. Pools/metric: Ti duty07 per side, round-per-seed-then-mean (l109
rounding path), 5-pair table reported.

## Hypotheses (registered BOTH directions)

- H-EDGE (edges carry it on this base too): sil1110_wA stays in cutwA's
  partial band AND |mean paired dR vs cutwA| <= the L141 clamp reference
  scale (.075 silrand spread). => Two-factor law's cleanest statement:
  same substrate, silencing the carrier's ACTIVITY does nothing while
  cutting its EDGES flips kill->super.
- H-ACT (activity-carried, substrate-gated): sil1110_wA RESTOREs or
  SUPERs (meanR >= .45/.60, kR >= 12) with paired dR vs cutwA >> .075.
  => the wA-base flip needs only 1110's SILENCE; intact-vs-window is the
  gate. Both branches publishable; neither is a failure.
- Intermediate OUTCOME (partial-band edge but dR beyond .075, or off-band
  without RESTORE): DISCLOSE as intermediate, no class forced (L109).
- P1 (replication leg): sil1110 vs full on B30 stays small (L141 B27
  found dR -.088, in full's band). If P1 FAILS, B30 is anomalous for
  clamps — read all legs against that, do not force H branches.
- P2: the fork-grade paired dR legs (shared noise+X0+node set) are the
  PRIMARY discriminators; class labels secondary.
- P3 (crossed-law read, descriptive): L142's every flipping arm killed
  Ti_L. If sil1110_wA flips, read whether Ti_L dies WITH it (same
  mechanism) or survives (activity-silence ≠ edge-cut mechanically) —
  either answer is a finding, registered descriptive.

## Anchors (gates; ALL green BEFORE any B30 read)

- A1 stored gains: cutwA/cutng25 re-bisect EXACT (in-run assert, STOP).
- A2 C0A-144: {full, b65, cutwA, cutng25} × {mm, xm, 20 pool keys} ×
  {801, 901} vs raw_l135.npz — max|d| == 0.0.
- A3 FORWARD CHAIN (L120 law): (a) same 4 arms vs raw_l142.npz @801/901
  == 0.0; (b) sil1110 vs raw_l137.npz sil1110 @801/901 == 0.0 (certifies
  the clamp wiring end-to-end; l137 rolled every arm at the anchor
  seeds). Any A3 miss = clamp/graph wiring bug: STOP before B30 reads.
- A4 B30 absence across all stored npzs (STOP on collision).
- A5 P4 health: per-arm af in (0.01, 0.9) every seed; b65 mean-af band
  .105056-.113056.
- B-cert BEFORE any B30 read: verdict machinery recomputed on raw_l142
  B29 for {cutwA, cutng25} == results_l142.json Ti table EXACT (L85).

## Pooled reads (L90 full-precision Wilson, unrounded)

- cutwA pooled B21+B24+B25+B26+B29+B30 (n=96, raws z126/z131/z133/
  z135/z142/z144); cutng25 pooled B24+B25+B26+B29+B30 (n=80). sil arms:
  single-batch B30, disclosed (L141 B27 sil1110 quoted beside).

## Disclosures (pre-registered)

- full's own class on B30 is batch-drawn (2-10/16 base spread): classes
  read against m0/paired legs, not bare bands (L109 rule).
- sil1110_wA has no independent gain: af-matched BY GRAPH IDENTITY to
  cutwA (same nodes, same stored gain, same settle) — settled af equals
  cutwA's bit-for-bit; disclose rather than re-bisect.
- Clamp is window-only (l137 form): 1110's settle trajectory is
  untouched, its X is zeroed from window step 0 onward.
- No e-arm reruns: l142's edge ladder stands on B29 (single-batch,
  disclosed there); L144 changes NOTHING about it.
