# L147 PREREG — forward-walking channel static join (registered 2026-11-19 02:5x, BEFORE any census compute)

Card: LANE.md L147 (ideas 76, seeded tick 167 from Dallmann bioRxiv 697356).
Zero rollouts, deterministic, no RNG, CPU-only, descriptive census + join table.

## Names joined (exact-string law, L134/L138 precedent)

- cell_type == 'DNg100' (field forward-walking DN #1)
- cell_type == 'DNg97'  (field forward-walking DN #2; paper alias oDN1)
- cell_type == 'DNp33'  (CONTROL pin: L138 verified 2/2/2 BANC/v783/male,
  BANC pair = 1110-L carrier + 319 R twin — re-assert as machinery check)
- 'BDN2', 'oDN1' — scanned; pre-registered expectation ABSENT from all
  three type vocabularies (naming-scheme aliases; the DNg names are the
  joinable canonical strings). 0 hits = expected, disclosed as such.

## Graphs + columns

- BANC v626: data/dv_11845666 (pt_root_id, super_class, cell_class,
  cell_type, side, region); edges data/dv_11842997 collapsed pairs (l138
  form). Cord = super_class in {sensory, ventral_nerve_cord_intrinsic,
  motor} AND region == ventral_nerve_cord. DN = super_class == 'descending'.
- MaleCNS v1.0: ../malecns/data/body-annotations (superclass/type/somaSide)
  + connectome-weights significant-only feather (l138_probe form verbatim).
  Cord = superclass in {vnc_sensory, vnc_intrinsic, vnc_motor}; DN =
  superclass == 'descending_neuron'.
- v783 (live brain): ~/critters/peabrain/data/
  neuron_annotations.tsv. Brain-only specimen — NO cord exists; the cord
  fate columns are structurally undefined and disclosed as such (L138
  precedent). Report count/sides/super_class + membership among
  proofread_root_ids_783.npy.

## Census fields (per matched cell, both graphs that have cord)

- side/somaSide, NT where cheap (v783 top_nt; BANC nt predictions not
  loaded — skip, not needed for a wiring census).
- OUT->cord: n edges, syn sum. IN<-cord: n edges, syn sum.
- dn_into flag (receives cord input), dn_proj flag (projects into cord),
  pure_proj = proj & ~into.
- Subnet fate, binary by rule: in_l65 = dn_into (L91 law: l65 keeps only
  DNs that RECEIVE cord input); in_closure = dn_into | dn_proj (L107 form).

## Pre-registered expectations (from stored runs / lane memory, verified live)

- male DNg100 = 2 cells (L32/L134 lineage pin); male DNp33 = 2 (L138).
- male DNs are 97.2% dn_into (L138 probe) → expect both DNg100/DNg97 male
  cells dn_into=True (in l65-equivalent).
- BANC DNp33 pair = 2 cells with sides L/R (gi 1110 + twin 319).
- BANC DNg100: memory pin '400+ cord out-edges' (L91 census contrast vs
  DNge046's 16) — re-derive exactly.
- Surprise rule (the card's purpose): if DNg97's cord fate DIVERGES from
  DNg100's (pure_proj → dropped by the l65 rule, or cord-degenerate),
  that row is the headline — the endgame vocabulary must name what the
  extraction actually keeps.

## RRN / BPN scan (pre-registered interpretation)

Case-insensitive substring over the NAME-bearing columns of each
annotation table (v783: cell_class, cell_type, supertype, synonyms, nerve,
super_class; BANC: super_class, cell_class, cell_type; male: superclass,
type): 'rrn', 'roadrunner', 'bpn'. Pre-registered reading: RRN/BPN are the
paper's CIRCUIT-LAYER nicknames (2 central-brain cells), NOT necessarily
public type-vocabulary strings. ZERO hits is an expected vocabulary
absence (disclosed as "name not in annotations vocabulary"), never
"circuit absent" — the channel joins through its DN targets, which DO
join 2/2/2. Any nonzero hit gets reported verbatim with column+value.

## Outputs

- l147/static.json (machine table) + printed human table.
- Verdict line per graph: does the field's forward-walking DN pair sit
  INSIDE the endgame substrates (l65/closure/male cord graph)?
- No LANE queue edits beyond checking L147; no live changes; digest push.

## ADDENDUM 1 (registered 02:5x, after first run tripped the pin, before any census number was accepted)

- The pre-registered control pin "BANC pair = 1110-L carrier + 319 R twin"
  mis-carried vocabulary (L44 class, instance #9): **319 is the MASS-ADJACENT
  LADDER twin** (l131 rank_ids.rank26 == 319, asserted at l134_static.py:131
  "rank twins (1110/319)"), NOT the DNp33 homologue. The DNp33 cell_type pair
  in the FULL v626 graph is gis **{928 (right, homologue twin — l134
  static.json twins[0].gi=928, root 720575941451941498), 1110 (left, carrier)}**.
- Corrected control assert: sorted DNp33 full-graph gis == [928, 1110].
- All other registered fields unchanged. The census rows already printed
  before the trip are re-derived by the corrected rerun from scratch
  (same deterministic script); nothing was read into a verdict pre-fix.

