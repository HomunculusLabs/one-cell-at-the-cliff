# L178 PREREG — linearized top-k path contribution: does the carrier have a PATH signature the mass-matched twin does not?

Registered 2026-11-22 ~08:05 EST, tick 232, BEFORE any L178 value was read.
Static cost. No rollout batches; the ONLY dynamics executed is the 400-step
af-matched SETTLE needed to define the linearization point, plus ONE nonlinear
step used solely as the instrument's self-check (Q5).

## Substrate (named, not implied)

PRIMARY = **f4wA**, the floor-4 base substrate of the L169b2/L175 family:
node set `keep_new` minus `ng4[:20]`, edge set filtered by pair-level summed
`syn_count >= FLOOR = 4`. This is the substrate on which the carrier/twin
dynamic contrast was actually measured (f4ng = + carrier removed = the SUPER
arm; f4tw = + mass-matched twin removed = the control), so it is the only
substrate where a path-level explanation of that contrast is on-topic.
Pins asserted EXACT before any new read: n 21,789 / edges 469,618 (l169b2
run.out), K4 = 73, carrier f4 rank 21, gi 319 f4 rank 33, GI_F4TWIN = ng4[21]
= 290 with relative out-mass gap 2.4e-05, jaccard_heavy 0.9231, closure_edges
472,095, wA_edges 469,256 (l169b/static.json F3_fully_rederived).

ACTORS on f4wA (all present, none removed):
- CARRIER gi 1110 (DNp33-L, f4 ng rank 21).
- TWIN gi 290 (DNpe005-R, f4 ng rank 22) — the mass-matched twin.
- FAMILY = the remaining ng4 cells present on f4wA (ranks 23..55, expected 33
  cells) — the mass-ordered reference family. NOTE, registered honestly: the
  card's phrase "the ng-family cells as the known SUPER arm" cannot be taken
  literally on f4wA, because the cells whose removal defines the base
  (ng4[:20]) are by construction ABSENT from it. The family arm is therefore
  the mass-ordered ng tail, used as the mass-covariate reference for Q3, and
  this substitution is disclosed rather than silently renamed.
- NULL = 100 degree-neutral rewire draws of the carrier's out-edges, the
  l169c P5/P6 destination-swap protocol transcribed VERBATIM and re-seeded
  `default_rng(16943)`, adapted to the floor-4 edge block. Both halves of each
  swap are applied (carrier row AND partner row), so out-degree, the carrier's
  out-weight multiset and every target's in-degree are preserved exactly.

## Linearization (convention stated in advance)

Dynamics law (l169b2 verbatim): `u = g * (W_beta @ X) + I + sin_t`, then
`X <- X + (DT/TAU) * (clamp(relu(u + BG) + noise, max=RMAX) - X)` with
TAU .05, DT .01, BG .02, NOISE .01, RMAX 1.0, SETTLE 400, D 0.2 on DNg100,
ENT_AMP .1 half-wave 0.7 Hz on the mechanosensory channel, W_beta = W with
negative values scaled by BETA = 2.0.

The **transmission operator** is `J = g * diag(a) @ W_beta`, with the row mask
`a_i = 1` iff `u_i + BG > 0` AND `relu(u_i + BG) + noise_i < RMAX` at the
settled state (relu' AND the saturation clamp). The full discrete Jacobian is
`(1 - DT/TAU) I + (DT/TAU) J`; path statistics are computed on **J**, and that
convention is reported with every number.

Depth-d pool reach of source c is the complete length-d WALK sum of J from c
into the pool set (recurrent graph: walks, not simple paths; revisits
included). Reported in two forms, both registered:
- ABS form on `|J|` (L21 rule: a signed-weight traversal silently drops
  inhibitory premotor edges), and
- SIGNED form on `J`, since sign is the whole point of an E/I path read.

Pools = the 20 `peripheral_target_type`-derived semantic motor pools
(POOL_G, L101 token rule, never type-name strings): Ti/Tr flexor-extensor and
Ta/Sr/Pr a-b, both sides. (The card says "22"; the instrument has 20 pools —
the 22 is the stored trace-channel count, which adds mm and af.)

## Registered gates (SEPARATE objects, L109 — each reported with its own verdict)

- **Q5 INSTRUMENT (runs FIRST, halting).** At the settled state, perturb
  `dX = 1e-4 * randn` and run ONE nonlinear step for X and X+dX under the
  SAME noise tensor (L36 paired-noise rule). Predicted response
  `(1 - DT/TAU) dX + (DT/TAU) J dX`. PASS iff relative L2 error < 1e-2. If it
  fails, the card reports BLOCKED and no path number is cited — a linearized
  instrument that cannot predict one step is not trusted over three.
- **Q1 CLAIM-CARRYING.** `r2 := (P2abs_pools(carrier)/m_out(carrier)) /
  (P2abs_pools(twin)/m_out(twin))`, i.e. normalized 2-hop pool reach at
  matched out-mass. Branches, registered with both directions live:
  - `r2 >= 1.25` -> **A_CARRIER_HIGH** (path signature, carrier-favouring)
  - `r2 <= 0.80` -> **B_CARRIER_LOW** (path signature, twin-favouring)
  - `0.80 < r2 < 1.25` -> **C_NO_SIGNATURE** at depth 2.
  Depth 3 (`r3`) reported identically as a SECOND object, never merged into Q1.
- **Q2 NULL.** Percentile of the carrier's `P2abs_pools/m_out` in the 100
  degree-neutral draws. PASS (carrier path geometry non-random) iff the
  carrier is above the 95th or below the 5th percentile. Reported with the
  draw median and IQR. LIMITATION REGISTERED IN ADVANCE: the null draws reuse
  the REAL substrate's row mask `a` and the REAL gain — they test path
  GEOMETRY under degree-neutral relocation at the real operating point, not a
  re-settled null (l169c P7 requires a fresh af-matched bisect per draw, which
  is rollout-scale and out of scope). No draw number may be written up as a
  dynamics null.
- **Q3 DEGENERATE / MASS-RESTATEMENT BRANCH (registered as a real outcome).**
  Spearman rho between `P2abs_pools` and `m_out` across the 35 ng actors
  (carrier + twin + family). If `rho >= 0.95`, the card is a **NEGATIVE**:
  top-k path reach is a restatement of out-mass, worth exactly one draft
  sentence and no mechanism claim. Reported before Q1 is interpreted.
- **Q4 ANTAGONIST POLARIZATION (descriptive, no branch).** For the 10
  antagonist pairs, `PI_d := sum_pairs |S_d(a) - S_d(b)| / sum_pairs
  (|S_d(a)| + |S_d(b)|)` on the SIGNED form. Carrier vs twin vs null
  percentile, depths 2 and 3.
- **Q6 TOP-K CONCENTRATION (descriptive).** Exhaustive per-path enumeration at
  depth 2 for carrier/twin/family: top-10 and top-100 share of total abs path
  mass, and the depth-2 enumeration total asserted equal to the matvec total
  to < 1e-6 relative — this is the card's registered brute-force certification
  that the search machinery is exact.

## Certifications (must pass before any L178 value is read)

- **CERT-HEAD.** `l178_static.py` is GENERATED: its head is
  `l151_static.py` lines 1-319 byte-for-byte (sha256 of the slice asserted in
  the builder), so every L151/L142/L134/L92/L101 pin re-runs as free
  certification. No module is ever `import`ed from a lab run script (L175:
  importing a `*_verdict.py`/run script EXECUTES it and mutates its artifacts).
- **CERT-F4.** The f4 ladder is RE-DERIVED here from the global edge arrays and
  asserted field-for-field against l169b/static.json F3_fully_rederived; the
  three gains are read from `l169b2/raw_l169b2.npz` and asserted to FLOAT
  EQUALITY against the l175f-verified values (g_f4wA 0.15051452517509462,
  g_f4ng 0.16230986118316648, g_f4tw 0.15261898636817928).
- **CERT-REW.** The transcribed l169c destination-swap, re-run on the ORIGINAL
  cutwA block with seed 16943, must reproduce l169c/static.json P6 EXACTLY:
  med_relocated 80.0, min_relocated 80, med_moved 80.0, med_mass_T70 0.0,
  med_mass_motor_share 0.1090891270920994, med_n_dst 80.0, and
  per_draw_first5 field-for-field. Only then is the floor-4 adaptation trusted.
- **CSR ORIENTATION (card rule 3).** `W[target, source]` asserted against a
  known atlas row before any mask is trusted: the carrier's local out-edges
  must be found in the COLUMN index and number exactly its global out-edge
  count on f4wA, and its in-edges in the row index.
- **OP POINT (L30).** settled af asserted inside the stored band; the stored
  rollout af mean for f4wA is 0.10889 and the bisect target AF_T is
  0.10905611018339793. Band registered as af in [0.095, 0.125] per seed.
- Every pin re-derived from stored ARTIFACTS, never from a log sentence (L44).

## Limitations binding on any write-up

1. Liu/Ganguli/Baccus 2611.26101's path-decomposition THEOREM does not apply:
   our graph is recurrent and our readout is not an additive output. Only the
   top-k machinery is borrowed, on the linearized operator. (L152 bracket.)
2. The linearization point is a single settled state under a PERIODIC drive;
   per L164 it is a PHASE SNAPSHOT, not a verified operating point, and no
   result here may be written as an intrinsic property of the substrate.
3. Walk sums at depth 3 include revisits; they are operator powers, not
   simple-path counts.
4. The null is a geometry null at the real op point (see Q2).
