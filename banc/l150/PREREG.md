# L150 PREREG — silW batch rebase (+ eMot halves second batch)

Registered 2026-11-19 07:4x EST, BEFORE any build/run. Card: LANE.md ideas 79
(L150). Machinery: l148_run.py transform (latest hardened form); clamp arm
l144 form verbatim; e-drop dose split l145 form verbatim.

## Design

Fresh B33 = seeds 3365..3380 (n=16), ANCH 801/901 rolled FIRST (early wiring
verdict). Arms (7): full, b65, cutwA (partial base), cutng25 (super ref),
**silW** (= l144 `sil1110_wA`: cutwA GRAPH verbatim + window-only clamp
X[loc 467]=0, settle clamp-free, gain graph-identity to cutwA — l144 A1
form, NO fresh bisect), **eMotTop5**, **eMotBot5** (l145 dose split verbatim:
10 motor out-edges ranked |log1p(syn)| DESC / pos ASC, top5 = 62.55% of motor
mass; fresh bisect each, asserted == l145 stored gains EXACT:
g_eMotTop5 0.1436134350299835, g_eMotBot5 0.14367126345634465).

Rationale: the v3 draft's substrate-gated flip (silW .622/14 on B30) and the
threshold-footprint halves (top5 +.007 / bot5 -.013 on B31) are single-batch
claims the abstract leans on; L90/L139 batch-swing law requires a rebase
before they are citable.

## Registered bands (from STORED artifacts — L44 rule)

- silW B30 (l144/results_l144.json table.Ti.sil1110_wA): kR 14/16, meanR
  .622, Wilson lbR .6398; paired dR vs wA +.189, n_up 6/16.
- eMotTop5 B31 (l145): kR 6/16, meanR .438, dR_wA +.007 (n_up 2, n_dn 4).
- eMotBot5 B31: kR 6/16, meanR .418, dR_wA -.013 (n_dn 5, n_up 3).
- clamp/sham scale floor .075 (l137 silrand spread); all-10 endpoint
  eOutMot pooled B29+B31 = 21/32 lbR .483; cutng25 pooled 7-batch 108/112
  lbR .912 (l148); cutwA pooled 8-batch 38/128 ubR .381 (l149-verified n).

## Gates (criteria classes VERBATIM L118-L131)

- **P1 (primary) silW replicates** if EITHER leg holds on B33:
  (a) class leg: SUPER (meanR >= .60 AND kR >= 12) — the B30 class; OR
  (b) pooled leg: pooled B30+B33 kR >= 20/32 AND Wilson lb >= .50.
  Companion registered: paired dR vs wA >= +.10 on B33.
  NON-replication branch (registered): if B33 meanR < .45 AND pooled lb < .50,
  DRAFT v3's abstract substrate-gate sentence gets a batch-scoped amendment
  the SAME TICK (honesty clause; the claim degrades to "B30 + pooled trend").
- **P2 (secondary) halves carry two batches**: registered expectation = each
  half stays NEITHER-class on B33 (not SUPER, not KILL), |dR_wA| small; the
  citable claim becomes pooled B31+B33 (n=32 each) — threshold footprint
  (all-or-nothing at the sheet scale) predicted: both halves' pooled lbR
  BELOW cutng25's pooled lb (.912) AND their kR below the all-10 pooled 21/32
  rate (p-hat .656). If a half flips SUPER on B33 alone: disclosed as batch
  re-draw (L139 interior class); pooled decides any amendment.
- **P3**: Ti_L dead on every SUPER/flipping arm (kL <= 2) — crossed law.
- **P4**: af range (0.01, 0.9) all arms/seeds; b65 af-mean band
  [.105056, .113056]; e-arms gains inside [.14, .16] band (disclosed if out).

## Anchors (all must be 0.0 / EXACT; B-cert BEFORE any B33 read)

1. Standalone absence precheck: B33 seeds absent from EVERY npz under banc/.
2. In-run B-cert (L85 rule), FIVE tables recomputed from stored raws and
   asserted == stored results EXACT: l135 B26 (cutwA/cutng25), l142 B29
   (cutwA/cutng25/eAll), l144 B30 (cutwA/cutng25/sil1110_wA), l145 B31
   (cutwA/cutng25/eMotTop5/eMotBot5), l148 B32 (cutwA/cutng25).
3. C0A-150 vs raw_l135 @801/901: {full, b65, cutwA, cutng25} x {mm, xm, 20
   pool keys} + af — max 0.0.
4. FC-144 (clamp-wiring cert, l144's own FC-137 form): silW @801/901
   bit-identical to raw_l144 sil1110_wA traces (same clamp, same graph,
   same gain, seed-parameterized noise = W-independent).
5. FC-145 (L120 forward-chain law): eMotTop5/eMotBot5 @801/901 bit-identical
   to raw_l145 traces + both fresh bisects == l145 stored gains EXACT.
6. Stored-form bisects cutwA/cutng25 == G_CUTWA/G_CUTNG25 stored EXACT.
7. Staircase residuals disclosed (|af_final - AF_T| per bisected arm).

## Arm-add note (l131 law)

The per-arm plumbing sites touched by this transform: ARMS/GAIN (1), E_ARMS
block (1), silW per-arm alias block (1), settle_states st dict (1), rollout X
dict (1), noise dicts x3 (21-space pattern count-pinned 3, l123 law),
bisect gains-dict signature (1), savez gains (1), anchors/absence lists (1
each), out dict (1). Residual scan: zero surviving 'eAll'/'se0'/'B32'/'l148'
code tokens in l150_run.py (comments whitelist by line context only).

## ADDENDUM 1 (registered 2026-11-19 ~08:05, BEFORE the rerun)

Run v1 crashed pre-rollout at my rank pin (assert 'top5 rank drift', index
0) — zero seeds rolled. Root cause is NOT builder drift: l145_static.py's
motor_edges_ranked table zips the UNRANKED ascending position list
(mot_pos) with the RANKED dst/w/syn columns (mot_dst/mot_w/mot_cnt from
mot_ord) — the stored 'pos' column pairs the wrong edge (defect signature:
stored pos column is exactly ascending = np.where(out_mot)[0], while
dst_gi/syn columns are the true ranked order; probe l150_rank_probe.py
pinned both orderings from the unchanged data files, mtimes 11-14).

Scope: l145's RUN is UNAFFECTED (eMotTop5/eMotBot5 masks built from mot_ord
in l145_run.py, subset law asserted on MASKS in-run; graphs are
order-insensitive via coalesce). The published l145 numbers that touch the
table are the mass splits (.000523/.000313, .6255 share — computed from
masks, correct) and the top-5 dst identities (dst column = ranked dsts,
correct); only the pos↔value PAIRING in the json table is wrong.

Amended pin (L66/L77 class — re-derive from stored values + mechanism):
pin my ranked order against the stored (syn, dst_gi) columns, assert the
stored pos column equals its own ascending sort (defect signature), and
assert position SET equality with my derivation. FC-145 bit-identity
vs raw_l145 remains the definitive arm-level cert. Corrected table pinned
post-run at l150/static.json; l145/static.json left untouched (stored
artifacts immutable). Draft-consumption check of the bad pos column
queued post-run (L112-class).
