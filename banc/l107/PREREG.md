# L107 PREREG — extraction-rule-decomposition (static + ONE bisection slice)

Written BEFORE rollouts. Static pins in l107/static.json (already computed,
asserted == l92/static.json on n_old/n_new/edges_old/edges_new/dn_new).
Stored-artifact pins re-derived from results jsons (L44 rule), listed below.

## Static (claim-carrier, no rollouts)

- Membership diff: closure = l65 + 560 dn_new cells (dn_proj & ~dn_into);
  NO cell class that l65 keeps is dropped by closure (additive, C0S l92).
  Therefore the card's "largest l65-only class re-added" does not exist as
  written; the honest decomposition is SUBTRACTION from closure. AMENDED
  slice form: cut = closure minus the top-cord-out-mass dn_new subset.
- Added edges 20,902 = dnnew->old 17,326 + dnnew->dnnew 1,387 + old->dnnew 2,189.
- Target tiers of the out-edges: intrinsic 12,991 edges / mass 25,669.9
  (89.8% of cord out-mass 28,583.9); motor_other 1,130/2,593.8;
  motor_pools (the 8 antagonist pools) only 129 edges / mass 271.3
  (~0.2-2% of pool in-mass, per-pool table in static.json); vnc_sensory 29.
  => direct pool bombardment is ruled out as the kill mechanism; the added
  DNs project onto the PREMOTOR INTERIOR.
- dn_new families scattered (DNpe054 21, DNge091 19, DNg07 18, ...).
- Cut slice: K=77 cells (13.8% of dn_new) carry 50.24% of cord out-mass;
  n_cut 21,732; edges_cut 639,164.

## Arms (B4 = seeds 801-816, n=16; l94_run.py draw order EXACT: per seed
## gen=Generator(seed), gen2=Generator(seed+9000); X0o=randn(n_old,1)@gen,
## X0n=randn(n_add,1)@gen2; settle 400 then WIN 6000, per-step nz_o@gen then
## nz_a@gen2, shared across arms; nzn_full scatter = l94 form)

1. full — keep_new @ g 0.153125, tonic DNg100 D=.2. ANCHOR ARM: must be
   BIT-IDENTICAL to stored raw_l94.npz cfn (mm, xm, 8 pools x 16 B4 seeds).
2. b65 — keep_old @ g 0.14 (l65 stored op point), same tonic/schedule.
   Fresh same-protocol replication of l65 (NOT bit-comparable to l91 fn:
   stream form differs — l91 predates the two-generator law; disclosed).
3. h65 — keep_old @ g 0.153125 (closure's gain on l65 wiring). GAIN-SLICE
   diagnostic: settle af floats ABOVE target (no bisect, disclosed).
4. cut — keep_cut (closure minus 77 top-out-mass dn_new) @ g_cut, bisected
   settle-only on anchor seeds 11/22/33 mean af -> af_target 0.10905611018339793
   (l92 P1 form, ~24 iters, 6-decimals, take lo; bisect consistency:
   anchor-seed mean of the main run == bisect final, EXACT).

## Pinned expectations (stored; verdict certifies BEFORE pinning new reads)

- l94 cfn Ti B4: k 0, wilson [0.0, 0.194], duty07_mean .135, seg1 .003,
  seg2 .098, duty07L .378, duty07R .425 (results_l94.json).
- l94 cfn Tr B4: k 0, duty07_mean .017, L .032, R .372.
- l91 fn Ti: 16/16 in EACH of B1/B2/B3 (pooled 48/48 lb .9259) — the
  robustness b65 replicates; duty07_mean .992/.996 (B1/B2).
- af spread sanity: l94 cfn B4+anchor af mean .109962 sd .002377
  range [.1056,.1157] => b65 B4-mean band [target-.004, target+.004]
  = [.105056, .113056].

## Gates

- C0A (HARD STOP if fail): full == stored cfn max|d| 0.0 exactly, every
  key, every B4 seed. Else wiring bug — no read.
- C0B (verdict, before any new pin): verdict's B4 cells on stored
  raw_l94.npz cfn reproduce results_l94.json B4 per-batch fields EXACTLY
  (Ti+Tr x 7 fields).
- C1: every arm-seed settle af in (0.01, 0.9); b65 mean in band;
  cut bisect-consistency exact.
- E1 (replication): k_b65 = #{duty_07(Ti) >= .5 on B4}. Direction:
  k_b65 >= 12/16 replicates l65 robustness under l94 machinery.
  k_b65 <= 8 = non-replication (protocol-form finding; reads continue,
  disclosed).
- E2 (bisection): k_cut vs {k_full = 0, k_b65}.
  k_cut >= 12 → the 77 removed cells carry the kill (CONCENTRATED).
  k_cut <= 4  → distributed membership and/or gain (NOT concentrated).
  5-11 → partial; follow-up slices.
- E3 (gain): k_h65 <= 4 → the +9.4% gain alone kills l65 Ti (op-point
  ingredient); k_h65 >= 12 → gain innocent, membership implicated.
  Middle → mixed.
- Descriptive: per-arm duty07_L/R means, seg duties, dom_freq lock count
  (dom_ratio >= 10 per 2000-step seg), per-seed af table, duty at a
  +250-step shifted window grid for any arm with k >= 12 (FlyHack-style
  stability secondary, descriptive only).

## Interpretation table (pre-registered)

- k_b65>=12 & k_h65>=12 & k_cut<=4  → kill is DISTRIBUTED membership
  (small per-cell, carried by the intrinsic-projecting bulk).
- k_b65>=12 & k_h65<=4              → kill is the OP POINT (gain), not
  membership; L94's "extraction rule load-bearing" = "extraction rule's
  gain headroom".
- k_b65>=12 & k_cut>=12             → kill CONCENTRATED in 77 cells
  (follow-up: family decomposition of the 77).
- k_b65<=8                          → l65 robustness does not port to the
  l94 stream/protocol form; substrate claim weakened, disclose.

## Scope / disclosures

Single batch n=16 directional slice; any clearing arm requires pooled
multi-batch re-base (L88/L90 rule) before it re-opens anything. h65 is
af-unmatched by design. No live changes; sessions/ untouched.
