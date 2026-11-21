# L148 PREREG — silent-and-edgeless identity arm (registered BEFORE the build/run)

Item: LANE.md ideas 77 / L148. The one open cell of the L141/L142/L144
two-factor grid: silence alone (sil1110_wA .622/14, B30) sits BELOW the
edge cut (eAll .745/14, B29) and the node drop (cutng25 .714/16, B30);
the .09-.12 remainder is unattributed. Combo arm: clamp X[1110]=0 AND
drop all 93 incident edges on the cutwA base — cell present-but-silent-
and-edgeless ~= an isolated node. 2 new arms max per the card: `se0`
(combo) + `eAll` re-pin (the lone parent that never re-rolled beyond
B29 — paired legs need it same-batch). silW stays single-batch B30,
quoted as ctx (l144 form).

## Batch-label rename (L44 instance #6, disclosed)

Card text says "fresh B31" — written 11-18, BEFORE L145 shipped B31
(3333..3348, results_l145.json). The fresh batch for L148 is
**B32 = 3349..3364** (16 seeds + ANCH 801/901 FIRST). Absence asserted
against EVERY npz on disk under banc/ (standalone scan) plus the in-run
explicit list (incl. l142/l144/l145 raws + partials; STOP on collision).

## Substrate & machinery

- Base VERBATIM l142/l144/l145: full (G_NEW .153125), b65 (G65 .14),
  cutwA (stored .14365819573402408), cutng25 (stored
  .1454454553127289). l148_run.py = count-asserted transform of
  l142_run.py (keeps eAll end-to-end; deletes eOutInt/eOutMot/eOutAll/
  eIn per the l131 residual-scan law; adds se0).
- ARMS (6): `full`, `b65`, `cutwA`, `cutng25`, `eAll`, `se0`.
  - `eAll` — drop all 93 incident edges of 1110 on the cutwA node set
    (1110 kept as a cell; l142 build verbatim). Re-bisect asserted ==
    l142 stored g_eAll 0.1454454553127289 EXACT (FC-142 deterministic
    law); e_band .14-.16 disclosed.
  - `se0` — eAll graph VERBATIM (same node set/order/gain/init/noise)
    + window-only clamp X[loc 467]=0 (l137/l144 clamp form: after the
    X update, before readouts; settle clamp-free). loc 467 ==
    int(loc_wA[1110]) asserted == l144 stored clamp_sil1110_wA.
    GAIN["se0"] = GAIN["eAll"] by graph identity — NO independent
    bisect (l144 silW disclosure form; se0 included in the bisect
    settle dict, where it settles identically to eAll).
- se0 aliases eAll/cutwA per-arm maps (POOLS/mech/motor/dng100/N_OF);
  WB[se0] = Wb_e["eAll"]; noise se0 = nzn[wA_pos_in_new] (cutwA-form).
- In-run static A0: eAll edge set == cutng25 node-drop positions
  (array_equal, 644084; l142 A0 re-pin); E_EDGES == {"eAll": 93};
  1110 ISOLATED on eAll (in-deg 0, out-deg 0); 1110 in NO pool, not in
  mech/motor/dng100 of the wA node set (readout-membership pin).
- Spectator arms (cut/cut19/cut58/cutk5/cutng19/cutng23/cutng25p/
  cutng26/cutng29) keep graphs/pins verbatim, never advanced (l139).

## Criteria (VERBATIM L118-L131, same code path as l142/l144/l145 verdict)

KILL: meanR <= m0 - .10 AND kR <= 4 AND mean_paired_dR <= -.20.
RESTORE: meanR >= .45 AND kR >= 12. SUPER: meanR >= .60 AND kR >= 12.
PARTIAL band: .35 <= meanR <= .50 AND 3 <= kR <= 8. m0 = full's meanR
on B32. Pools/metric: Ti duty07 per side, round-per-seed-then-mean
(l109 rounding path), 5-pair table reported.

## Hypotheses (registered BOTH directions)

- H-ID (identity, primary): se0 == eAll on EVERY stored channel (mm,
  xm, af, 20 pool keys), EVERY seed incl. anchors — max|d| == 0.0.
  Derived from the machinery (falsifiable): 1110 has ZERO out-edges on
  eAll (X[1110] enters W@X nowhere), no pool/mech/motor membership,
  settle clamp-free and gain-identical => clamping an isolated node
  cannot move any readout. If H-ID holds, the two-factor grid CLOSES:
  activity-silence is a strict SUBSET of edge-removal on this base —
  the silW→eAll remainder (.123 cross-batch) is settle-history/edge-
  carried, NOT window activity carried on top of the cut.
- H-DENOM (the registered branch): any nonzero se0−eAll diff => the
  isolated cell's mere presence, noise draw, or af-denominator
  contribution carries readout mass (or the clamp loc is wired wrong —
  this gate is also the clamp-wiring tripwire). Quantify per-seed
  per-key, disclose, no class forced. Either branch publishable.
- H-REPLIC: eAll re-pin on B32 SUPERs (meanR >= .60, kR >= 12) —
  endpoint-class expectation (L139 endpoints law; .745/14 on B29).
  Counter: B32 re-draws to partial/none => single-batch class was
  batch-drawn (L88/L90); pooled B29+B32 (n=32) Wilson carries the
  verdict, disclosed.
- P3 (crossed-law, descriptive): read Ti_L on eAll/se0 (lineage: every
  flipping arm kills Ti_L, kL <= 2). Either answer a finding.

## Anchors (gates; ALL green BEFORE any B32 CLASS read)

- A0 static (in-run, pre-bisect): pins above (STOP on any miss).
- A1 stored gains: cutwA/cutng25 re-bisect EXACT (STOP on drift).
- A1b FC-142: eAll re-bisect == l142 stored EXACT (STOP on drift);
  g_se0 == g_eAll == g_cutng25 EXACT (graph-identity + A-EALL).
- A2 C0A-148: {full, b65, cutwA, cutng25} x {mm, xm, 20 pool keys, af}
  x {801, 901} vs raw_l135.npz — max|d| == 0.0.
- A3 FC-142 traces: eAll (mm, xm, 20 pool keys, af) @801/901 vs
  raw_l142.npz == 0.0 (certifies the re-introduced eAll plumbing).
- A4 SE-ID @801/901: se0 vs eAll == 0.0 on named keys (mm/xm/af/pools;
  L59 rule — enumerated keys only); se0 vs cutng25 pools == 0.0
  (A-EALL extension, gains equal EXACT).
- A5 SE-ID on ALL B32 seeds (verdict, BEFORE classes): se0 vs eAll
  max|d| == 0.0 over the same enumerated keys — the H-ID gate; STOP
  before class reads if it fails (H-DENOM branch instead).
- A6 B32 absence (standalone scan + in-run list; STOP on collision).
- A7 P4 health: per-arm af in (0.01, 0.9) every seed; b65 mean-af band
  .105056-.113056.
- B-cert BEFORE any B32 read (verdict): (i) raw_l135 B26 {cutwA,
  cutng25} == results_l135.json Ti EXACT; (ii) raw_l142 B29 {eAll,
  cutwA, cutng25} == results_l142.json Ti EXACT; (iii) raw_l144 B30
  {cutwA, cutng25, sil1110_wA} == results_l144.json Ti EXACT (clamp-
  arm trace read certified); (iv) raw_l145 B31 {cutwA, cutng25} ==
  results_l145.json Ti EXACT.

## Pooled reads (L90 full-precision Wilson, unrounded)

- eAll pooled B29+B32 (n=32; FIRST replication of the .745).
- cutng25 pooled B24+B25+B26+B29+B30+B31+B32 (n=112); cutwA pooled
  B21+B24+B25+B26+B29+B30+B31+B32 (n=128). Recomputed from stored
  raws, never from log prose.

## Disclosures (pre-registered)

- se0 has no independent gain: af-matched by graph identity to eAll
  (same nodes, same gain, same clamp-free settle) — settled af equals
  eAll's bit-for-bit by construction; disclose rather than re-bisect.
- Clamp is window-only (l137 form): 1110's settle trajectory untouched
  on BOTH arms (eAll keeps it isolated through settle anyway).
- The H-ID prediction is machinery-DERIVED (no out-edges + no
  membership); the run's payload is the falsifiable all-seed identity
  gate (clamp-wiring tripwire), the first eAll replication batch, and
  the pooled growth. Discriminating reads registered so a vacuous pass
  cannot read as a win (L55 guard): SE-ID max|d| table + eAll B32
  class + pooled CIs + P3.
- full's own class on B32 is batch-drawn (2-10/16 base spread): class
  labels read against m0/paired legs, not bare bands (L109 rule).
- silW (.622/14) and the other e-arms stay single-batch (B30/B29);
  L148 changes nothing about their standing numbers.
