# L138 PREREG — cross-connectome DNp33 replication, SLICE A (statics + triangulation + design card)

Registered 2026-11-18 12:5x EST BEFORE any L138 computation. Card: LANE.md ideas-72 L138.
Slice B (the dynamic male run) is the design card in section D below, seeded per the
tick-160/L137→L141 precedent. Zero rollouts in slice A. Deterministic, no RNG.

## Substrate mirror (registered construction)

MaleCNS analog of the BANC l92-closure ladder, extraction VERBATIM l32_antagonism.py
forms: cord = superclass in {vnc_sensory, vnc_intrinsic, vnc_motor}; dn_all =
superclass == 'descending_neuron'; dn_into = DN with an edge INTO cord; dn_proj =
DN with an edge INTO cord FROM itself (src DN, dst cord); keep_old = cord|dn_into
(the l32/l65-analog); keep_new = cord|dn_into|dn_proj (the closure analog);
dn_new = keep_new − keep_old; added = closure edges not in old edges. Ladder mass
per dn_new cell = Σ|log1p(weight)| over its ADDED edges with cord destinations
(motor/intrinsic/vnc_sensory), the BANC l107 ladder metric mirrored exactly.
is_glut from body-neurotransmitters consensus_nt == 'glutamate'.

## Static legs (all read-only; every leg discloses BOTH directions, L84 rule)

- S1 FEASIBILITY: report n(keep_old), n(keep_new), n(dn_new), n(added edges).
  No gate (descriptive); if dn_new < 50 or added < 10k, the closure-ladder
  structure has no male analog and that IS the finding (L94 extraction-rule class).
- S2 DNP33 POSITION (the decisive static): both male DNp33 cells (type string,
  L134 join; assert n==2, somaSide L/R) — ng-ladder membership, rank, mass share.
  Branches: (a) >=1 cell inside the ng heavy set (top-50% mass cut, BANC K-form)
  → slice-B design mirrors BANC ranks around ITS position; (b) both outside the
  heavy set (or glut) → no ladder analog at the carrier; slice-B shifts to
  mass-matched add/remove arms (D-b); (c) DNp33 not in the closure at all →
  carrier-not-portable disclosure, slice-B scoped to ladder shape only (D-c).
  No static branch closes the DYNAMIC question (L134 law: statics cannot predict
  the carrier — the BANC carrier also had zero direct antagonist edges).
- S3 WINDOW SHAPE: male ng cumulative-mass profile vs BANC's (shares of ranks
  1-19 / 20-29 / 30-58 at each graph's own heavy cut). Descriptive, no gate.
- S4 TRIANGULATION: BANC DNp33 = 2 cells (1110 L carrier + R twin, L134 pins);
  male DNp33 = 2 cells; v783 live-brain join = cell_type 'DNp33' rows in
  peabrain/data/neuron_annotations.tsv + re-assert 1110's inline
  fafb_783_match_id is in brain_graph.pt ids (L134 finding). Gate: type string
  present in ALL THREE graphs (n>=1 each). If v783 lacks the string, disclose
  (try other_names/synonyms column) — never force a join.
- S5 POOL SANITY: male Ti/Tr flexor/extensor MN pool sizes (l32 type-name form,
  'Acc. ' stripped) reported beside BANC's (Ti 101/12, Tr 62/48 — l92 pins).
  Assert non-empty; NO cross-graph equality gate (different specimens/schemas).

Pins re-asserted BEFORE any new number: l107 cut K/mass_share, l92 n_old/n_new/
dn_new/pool_sizes, l121 ngladder drop_ids, l131 rank twins 1110/319 (BANC side);
l32 male pool-type strings + SIG_A sign set (male side, quoted not re-derived).

## Section D — SLICE B design card (the dynamic male run; NOT run this tick)

Substrate: male closure-analog subnet (S1 construction), L32-CERTIFIED regime
verbatim — RAW signed synapse-count weights (labeled deviation), SIG_A signs
(glut EXCITATORY — the male's own winning arm; BANC used glut-INH, L65 flip law:
never assume one sign across connectomes), g=0.01, beta=2, uniform tau .05/
DT .01, tonic background .02, noise .01, settle 400, win 800+ steps.
Metric: per-seed Ti pool structure duty (L91 male-census form) with the k>=bar
cell CALIBRATED from the male FULL-arm distribution over >=2 fresh batches
(B28+/B29+, absence-checked against every stored npz) BEFORE any arm is cited —
L88/L90 law: a bar calibrated on one batch inherits the draw. Pooled unrounded
Wilson over the batch union for every citable cell.
Arms (branch on S2): (a) maleFull + maleNgK ladder cuts at the BANC-decisive
ranks {19,23,24,25,26,29} mapped onto the male ng ladder's OWN ordering, plus
DNp33-in/out XOR at its actual position (mass-matched twin control = the cells
at the mirrored rank window, L120 form); (b) if DNp33 outside heavy set:
maleFull + DNp33-removed + mass-matched-random-pair-removed x3 draws
(L125 form) + ng19/ng29 endpoint arms; (c) if DNp33 absent from closure:
maleFull + ng19/ng29 only — ladder-shape replication, carrier disclosure.
Anchors: af assert every arm (L30), dm probe every perturbed arm (L35), one
shared-noise-stream fork form, C0A chain n/a (new substrate — its own
B-cert: re-run full on 2 stored-config seeds bit-identically before any arm).
Gain: single bisect to the male af target disclosed unrounded (staircase law,
L107); never port BANC gains (L39).

## ADDENDUM (post-static, pre-any-slice-B-run — 2026-11-18 13:0x)

S1/S2 OUTCOMES (l138/static.json + l138/probe.out, zero rollouts):
- S1: male closure mirror is 2 orders smaller — keep_new 21,544 vs old 21,516,
  dn_new 28 cells (BANC: 560), added edges 1,942, heavy-50% cut K=9 (0 glut,
  9 ng). There is NO male ng window (BANC r20-29 band has no analog; n_ng=9).
- S2 branch = (c), STRONGER: male DNp33 (2 cells, L/R, ACh, string-joined)
  is RECIPOCAL — dn_into AND dn_proj (222/224 OUT->cord edges w 1860/2305,
  33/37 IN<-cord) — it lives INSIDE the base l32 substrate, carries ZERO
  closure-ladder mass, and 97.2% of male DNs receive cord input (BANC's
  560-cell pure-proj cohort exists only because BANC's extraction left them
  non-reciprocal).
- S4 triangulation GREEN: 'DNp33' in all three graphs (BANC 2 = 1110-L carrier
  + R twin; MaleCNS 2 L/R; v783 2 left/right) + BANC 1110 fafb_783_match_id
  720575940604103084 IS in live brain_graph.pt. v783 cliff arm structurally
  impossible (brain-only graph, no cord/motor antagonist readout) — disclosed.

SLICE B (section D) CLOSED PRE-RUN, measured infeasibility (L125 precedent):
branches (a)/(b) require an ng ladder/window that does not exist on male;
branch (c)'s ng19/ng29 arms are undefined (n_ng=9 < 19). The DNp33 identity
cliff is NOT portable as a ladder question across connectomes — the honest
replication boundary is: the cliff is a property of the BANC closure-extraction
cohort (L94/L107 extraction-rule law, now shown at cross-connectome scale).
A male single-cell flip question, if ever wanted, is a NEW card (different
claim class), not L138.

