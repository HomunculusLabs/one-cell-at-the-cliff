# L92 PREREG — banc DN-closure subnet (tick 117, 2026-11-15)

Written BEFORE any rollout. Static build + census ALREADY derived (no rollouts):
`l92/static.json` + `l92/dn_census.csv` via `l92_static.py` (extraction verbatim
from l91_run.py; only the keep rule changed). All static numbers below are
PINNED to that file and re-asserted at run start.

## Substrate amendment (the card's rule)

keep = cord | dn_into | dn_projecting, where dn_projecting = DNs with >=1 edge
INTO a cord cell (dst in cord). dn_new = dn_proj & ~dn_into = the cells the
l65 rule dropped (L91 ADDENDUM's dead-channel mechanism).

Pinned static (must match at run start, assert equal):
- nodes 21,249 -> 21,809 (cord 20,521 | DNi 728 | DNn 560; dn_proj 1,287)
- edges 627,051 -> 647,953; blocks: cord->cord 560,236, cord->DNi 5,322,
  cord->DNn 0 (by construction), DNi->cord 53,329, DNi->DNi 8,164,
  DNi->DNn 2,189, DNn->cord 14,279, DNn->DNi 3,047, DNn->DNn 1,387
- C0S: old edge set EXACT SUBSET of new (np.isin on global-id keys) + values
  bit-identical on all shared pairs. VERIFIED TRUE in static pass; re-assert.
- pools EXACT [Ti 50/51/6/6, Tr 31/31/24/24], mech 4,848, motor 728,
  DNg100 2 (both DNi). DNge046: 3/3 cells now in subnet — loc {270 L DNn,
  302 R DNi, 366 R DNn}; out_cord 16/16/5, out_w 32.5/28.9/8.8; DIRECT pool
  reach ONLY on the DNi cell (Ti_fL 1.39) — the two DNn cells have ZERO
  direct antagonist-pool edges.
- Vocabulary statics: 236 DNi + 41 DNn cells have direct antagonist-pool
  reach; DNn command mass is weaker (out_w med 27.2 vs DNi 104.6, max 490 vs
  1,090; top commands DNg98/DNge104/DNg74_a/b/DNg100/DNg108 are ALL DNi).
- af_target = 0.10905611018339793 = mean of stored l91 afv_{11,22,33} arm fn
  (full precision, from l91/raw_l91.npz — L44 rule: derived from the stored
  artifact, not the log line).

## Dynamic protocol

Frozen params verbatim from l91: TAU .05, DT .01, RMAX 1, BG .02, NOISE .01,
SETTLE 400, WIN 6000, SEGB 0.7/1.4/0.7, AMPA = hyb01 chop (500-on/400-off,
continuous in seg1), BETA 2.0, D 0.2 on the 2 DNg100 cells, HOPA volley window
[2000,2040) ∪ [4000,4040).

- P1 OP POINT: bisect gain g on the closure subnet so mean af (after settle,
  af = mean(X > .05)) over seeds {11,22,33} hits af_target within 1e-3;
  bracket [0.05, 0.60], <= 14 iters, take closest. Report g_new vs g_old 0.14.
  Registered PREDICTION (not a gate): g_new > 0.14 — the 560 DNn cells add
  sub-threshold mass to the af denominator.
- P1b NOISE SCHEME (the decomposition instrument): gen(seed) draws ONLY the
  old-cell stream — randn(21249,1) for X0_old then one randn(21249,1) per
  step — bit-identical to l91's generator sequence by construction; gen2
  (seed+9000) draws the 560-cell stream. nz_full assembled by index map.
  All closure arms share gen/gen2 draws per step (one shared noise tensor,
  L36 lesson).
- ARMS (seeds {11,22,33}, 400 settle + 6000 win):
  - oldref — OLD subnet (n=21,249, single gen = l91 stream), gain g_new, no
    volley/echo. Gain-decomposition reference.
  - cfn — closure subnet, two-gen noise, gain g_new. Closure base + census
    carrier (u/X stats over steps [0,2000) for all 1,288 DN cells:
    u = mm(Wb,X)*G + I + BG pre-relu, u_max/u_mean per cell + X_mean).
  - chop50 — cfn + drive[hop46new] += 0.5 on HOPA steps (hop46new = the TWO
    DNn DNge046 cells, local {270, 366}; the DNi cell 302 is NOT vollied —
    L91 measured it buried).
  - chop200 — same at amp 2.0 (4x dose arm; L36 un-pin dose form).
- Measures per arm/seed: af, mm (motor mean), xm (mech mean), Ti/Tr x
  fL/fR/eL/eR traces; chop arms additionally dm = max|d mm vs cfn|, fd_mm /
  fd_xm first divergence, per-pool max|d| (dynamic pool reach).

## Anchors and gates (pre-registered)

- C0S static subset+values TRUE (assert at run start against static.json).
- C1: 0.01 < af < 0.9 every arm/seed AND |mean_af(cfn) - af_target| <= 2e-3.
- C0A CONDITIONAL bit-identity: IF g_new == 0.14 exactly, oldref must equal
  stored l91 fn arm BIT-IDENTICALLY (max|d| == 0.0 on mm + Ti/Tr x 4 sigs x
  3 seeds). ELSE branch B: disclose, report max|d oldref vs stored| as the
  pure-gain divergence — no gate, decomposition only.
- C0C closure footprint (MEASURED, first of its kind — no band pinned):
  max|d| cfn vs oldref on mm + 8 pool traces x 3 seeds at matched gain and
  matched old-cell noise = the closure edges' causal footprint on the base
  regime. Reported as the substrate-law number.
- C2 volley lands: dm(chop50) > 0 on >= 2/3 seeds. If dm == 0.0 at BOTH
  amps, the L91 dead-channel verdict EXTENDS post-closure (valid outcome;
  census u/X explains why).
- E1 fd law: fd_mm(chop arms) >= 2001 hard bound (divergence before volley
  onset = wiring bug = run fails). Exact fd reported, no exact-value gate
  (one-hop law would say 2001 only with direct motor edges; DNge046-DNn has
  none — expect later; report measured).
- E2 census verdict (THE DELIVERABLE): per DN cell (1,288) verdict class —
  pinned (X_mean >= .95) / buried (u_max <= 0) / viable (else), by class DNi
  vs DNn, crossed with out_cord >= 1 and pool reach > 0. Registered
  question: does a female hop vocabulary EXIST = any VIABLE DNn cell with
  cord out-edges (and how many reach antagonist pools). DNge046 trio's
  u_max/u_mean/X_mean reported explicitly (the male-port question).
- Registered expectations (disclose measured, none gated except C2):
  X-1 g_new > 0.14; X-2 DNge046-DNn cells NOT buried (their in-edges are DN
  only — cord->DNn == 0 by construction, so the L91 burial path via cord
  inhibition CANNOT apply; residual risk = DNi->DNn inhibition); X-3 volley
  lands; X-4 pool traces move weakly (no direct pool edges — per-pool max|d|
  expected small; if structure shifts, that is L93's question, descriptive
  here only).

## Checkpoints + discipline

raw_l92.npz (all pool traces + mm/xm/af + census vectors) written BEFORE any
analysis; verdict in l92_verdict.py re-derivable from raw + static.json alone.
No live changes; experiments in banc/l92/; CPU-only.
