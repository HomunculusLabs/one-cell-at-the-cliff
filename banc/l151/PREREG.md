# L151 PREREG — substrate-gate statics (zero rollouts, no RNG)

Card: WHY is the carrier's (gi 1110, DNp33-L, ng-rank 25) ACTIVITY load-bearing
only on the cut base (L144: clamp X[1110]=0 on cutwA flips SUPER .622/14;
the SAME clamp on the intact closure is inert, dR -.036 B30 / -.088 B27)?
Static decomposition only — OBSERVATION label per card, either outcome.
Registered BEFORE any measurement below is computed.

## Graphs (l142_run.py build verbatim)

- G0 = intact closure (keep_new) — clamp inert here
- G1 = cutwA (ng_desc[:24] cut; 1110 + all 93 incident edges PRESENT) — clamp flips here
- G2 = eAll (cutwA node set minus 1110's 93 incident edges) — SUPER base (edge side)

Weights: |log1p(syn)·sign| (ladder convention, outmass form), subnet-internal
edges only. Signed sums additionally reported for 1110's own edges. ALL
denominators below are these subnet in-mass sums — disclosed per metric.

## Populations

- T70 = 70 intrinsic out-targets of 1110 (l134/l142 pin); T10 = 10 motor targets
- Antagonist pools: 5 semantic pairs x L/R (l142 pools_for VERBATIM);
  Ti_fL/Ti_fR are the ladder readout pools (flagged)
- DN = super_class descending present in graph; ng58 cohort; window24 = ng_desc[:24]

## S1 — sheet redundancy (the hypothesis carrier)

Per G in {G0, G1} (G2 context row: m1110=0 by construction):
- D_sheet(G)  = total |w| in-mass of T70 (subnet edges)
- m1110       = |w|(1110 -> T70)        [identical G0/G1 — assert]
- m_ngothers  = |w|(ng58 \ {1110} present -> T70)
- m_dn_rest   = |w|(DN present, not 1110, not ng58 -> T70)
- m_intr, m_sens, m_other = non-DN input into T70
- share_1110_sheet(G) = m1110 / D_sheet(G)
- share_1110_of_DNsheet(G) = m1110 / (m1110 + m_ngothers + m_dn_rest)
- redundancy_ratio(G) = m_ngothers / m1110   [card's "~1x vs >>1" number]

H-SUB (registered, both legs): share_1110_of_DNsheet(G1)/share_1110_of_DNsheet(G0) >= 3
AND redundancy_ratio(G0)/redundancy_ratio(G1) >= 3. Both fire = card hypothesis
supported (observation); anything else = honest decomposition table, observation.

## S2 — pool routing at the entry depth (L60 rule: DN drive enters pools 2-hop via T70)

Per pool P (10 pools) x G in {G0, G1, G2}:
- direct_1110(P) = |w|(1110 -> P)   [expect 0 — pin against l134]
- D_pool(G) = total |w| in-mass of P; consistency: D_pool(G2) == D_pool(G1) - direct_1110
- sheet_to_pool(G) = |w|(T70 -> P) / D_pool(G)
- twohop_1110(P,G) = sum over (i->P, i in T70) |w(i,P)| * |w(1110->i)|
- twohop_dn_total(P,G) = same with dninput(i,G) = |w|(DN present -> i), all DN
- twohop_share(P,G) = twohop_1110 / twohop_dn_total
Registered context (no gate): whether twohop_share jumps on G1 the way S1 does —
the depth-consistency read (L60: measure the share at the hop depth the drive enters).

## S3 — motor flank

Direct: |w|(1110 -> motor pop)/D_motor per graph; via-sheet 2-hop form of S2
with P = all motor cells. T10 identity pinned (l134: iii4, i2, ... left).

## Anchor pins (assert EXACT before any new read; L44 rule)

- l107/S92: K 77, cut mass_share .50, closure nnz == ST["edges_cut"], S92 n/edges
- l131 pins: ng_desc[24]==1110, ng_desc[25]==319; cutwA .2286/644177; cutng25 .235/644084
- l142/static.json: E_EDGES {eOutInt 70, eOutMot 10, eOutAll 80, eIn 13, eAll 93};
  eAll nnz 644084; A0 re-verified: eAll global edge positions == cutng25 (L142b law)
- l134/static.json: out_edges 80, tiers 70/10, raw out-mass 183.96376182027785,
  in_edges 13 (all-DN), pool_direct = 0
- 1110 out-edge SET identical on G0 and G1 (global positions array_equal)
- pool sizes == S92["pool_sizes"] / S101 for all three graphs
- sheet consistency: D_sheet(G2) == D_sheet(G1) - m1110 (in-edge drop touches only 1110)

## Output

l151/static.json (all raw masses + shares + ratios) + printed verdict table.
No rollouts, no RNG, no live modules. Fold into paper/DRAFT.md §2.4(a)
interpretation ONLY as labeled observation.
