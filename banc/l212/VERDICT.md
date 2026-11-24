# L212 VERDICT — the v783 leg, re-posed so it is ANSWERABLE

branch **V_AVOIDS** (registered as the expected one). Predictions **3 of 5**.
Label: **EXPLORATORY** — and it stays that word everywhere.

Static, zero rollouts / zero settles / zero dynamics, 283 s CPU.
Artifacts `l212/{PREREG.md, static.json, run.out, run.err}`,
code `l212_{build,head,tail}.py` -> generated `l212_static.py` (619 lines).

## The question L207 could not ask

L207 recorded `UNANSWERABLE-BY-VOLUME`: FAFB v783 is brain-only, so the 831-cell
leg-motor readout has no counterpart there. Re-posed: **does the matched cell
avoid the nearest readout its own volume HAS?** Registered PRIMARY readout =
v783 `super_class == motor` (110 cells, 5 nerve pools PhN 40 / MxLbN 26 / CV 20 /
AN 14 / ON 10) — same CATEGORY as BANC's readout (terminal motor output), only
the body segment moved.

## Measured

| leg | carrier R | pct | rank | cohort med | deficit |
|---|---|---|---|---|---|
| PRIMARY motor (beta 2) | 1.6001e-06 | **0.020** | 3/100 | 2.0582e-05 | **12.86x** |
| SECONDARY descending (descriptive) | 1.5709e-04 | 0.290 | 30/100 | 2.2587e-04 | 1.44x |
| ROBUSTNESS beta=1 | 3.1863e-06 | 0.070 | 8/100 | 3.4477e-05 | 10.82x |

- **The carrier's avoidance TRANSPORTS to the other connectome, other volume,
  other readout**: pct 0.020 against BANC's 0.070 (closure) / 0.121 (cutwA) /
  0.059 (f4wA). Suggestive only, by registration.
- **The avoidance is READOUT-SPECIFIC, not general poor connectivity**: swap the
  readout to the descending population and the deficit collapses 12.86x -> 1.44x
  (pct .02 -> .29). The quiet cell is not quiet into everything.
- **Robust to the sign convention**: beta=1 keeps pct 0.070 / 10.82x (d +0.050,
  cohort Jaccard 0.709).
- **The lam1^2 division is a measured NO-OP** (R invariant under A -> 3A, rel
  diff 3.97e-16): L209's law re-measured on a third graph.
- lam1(v783, beta 2) = 552.634080, rel spread last-6 4.11e-16.

## The result I did not register: the BILATERAL SYMMETRY BREAKS

Q212-2 is **FALSE**. In BANC the mirror was hidden HARDER than the carrier
(.06 vs .10) and L211's search-information split transported to it. On v783 the
mirror is **not hidden at all**: pct **0.250**, rank 26/100, R 1.0028e-05.

The per-pool table says what the percentile hides:

| | CV | AN | ON | P1 (depth-1) | P2 |
|---|---|---|---|---|---|
| carrier (left) | 2.484 | 10.164 | 0.000 | **0.000** | 12.648 |
| mirror (right) | 14.652 | 45.019 | 8.618 | **0.693** | 68.289 |

The mirror carries 5.4x the depth-2 motor mass, reaches a pool (ocellar) the
carrier never touches, and has a **direct monosynaptic motor edge** — P1 =
0.693147 = log1p(1) = **exactly one synapse** — while the carrier has literally
none. So the honest statement is: the CELL that L178/L206/L207 identified (the
LEFT DNp33, matched by root id) stays quiet in the brain too; the TYPE-level
bilateral reading does NOT survive the volume change. L207's own law — a
cell-type claim needs the homolog — bites in the other direction here.

Registered caveat on that one-synapse edge, written into the follow-on: a
single-synapse edge sits at the detection floor, and v783 carries NO synapse
floor. **L222 tests whether the bilateral gap survives syn>=2 / syn>=4 before
anyone calls it biology.**

## Honest failures

- **Q212-5 FALSE**: cohort log-mass spread 0.316 (carrier) / 0.349 (mirror)
  against a registered <= 0.15. The v783 descending population is ~3x sparser in
  log out-mass around these cells than BANC's was (.10-.12), so this percentile
  rests on a **looser mass match than L207's** — a real limit on resolution, not
  a rounding note.
- **Q212-2 FALSE** as above (the finding).
- PREREG amended BEFORE any measurement: the operator could not be recovered from
  `peabrain/brain_graph.pt` as the PREREG first proposed, because that graph is
  in-degree normalised (`Wv /= max(indeg,1)[dst]`), which makes every row with
  indeg >= 1 sum to exactly 1 and the raw log1p mass unrecoverable. Rebuilt from
  the raw Zenodo feather in BANC's own expression instead; the live graph was
  demoted to a provenance gate (its coalesced nnz).

## Verified

- **CERT-783** (halting, 6 checks): `ids` array-EQUAL to the Zenodo
  `proofread_root_ids_783.npy` (N 139,255), live `meta` pins (139255 / 16847997 /
  sign dict) asserted, and my per-pair collapse of the 16,847,997 raw neuropil
  rows gives **15,091,983 unique pairs == the live graph's coalesced nnz**.
- **CERT-L207** (halting, 8 checks): both match ids read from `l207/static.json`
  opened READ-ONLY with size+mtime_ns fingerprinted before and asserted unchanged
  after; `verdict == UNANSWERABLE-BY-VOLUME`; both cells asserted present in the
  v783 id set (a missing id was coded as a journaled blocker + exit, not a
  workaround), `cell_type == DNp33` both, sides left/right, both `descending`.
- **CERT-SRC**: three VERBATIM `l207_tail.py` slices, sha256 asserted by the
  builder, each asserted a literal substring of its source and to still contain
  its functions — 82-110 `fce1e71189eb1ed7` (reach_sub, power_iter_sub), 199-241
  `340c0432c85c6e7b` (Rstat, pct_of, rankvec, spearman_l), 338-346
  `f4585bcc52f7ab0a` (matched_cohort). No lab module imported (L175);
  forbidden-token audit on the generated file; generated sha b32c576b5145487e.
- **CERT-MV** (halting, 4 EXACT array equalities): the bincount matvec == the
  verbatim `np.add.at` kernel on 4 probes (carrier impulse, mirror impulse,
  uniform, random).
- **CERT-GATE** (halting, 32 float equalities): the fast reach reproduces the
  verbatim `reach_sub` on both actors at every depth and pool (22), the fast power
  iteration reproduces `power_iter_sub` at 12 iters (2), and `Rfast` reproduces
  the verbatim `Rstat` on both actors across P1/P2/m_out/R/R1 (10). The modified
  kernels are GATED, never trusted.
- Readout pools asserted non-overlapping and summing to exactly 110; DN count
  1303 and motor count 110 asserted; both actors asserted to have non-zero
  out-mass; power-iteration convergence asserted (< 1e-6) with V_DEGENERATE
  wired as a real exit path.

## Limitations (from static.json, verbatim intent)

EXPLORATORY (L78): readout, volume and body segment all moved at once, so
neither direction can confirm or refute L207. Anatomical only — no mask, no
settle, no seed (L164). Walks with revisits, not paths. v783 has no synapse
floor, so the closest BANC comparator is closure/cutwA, not f4wA. 110-cell head
readout vs BANC's 303-cell leg readout. **A descending neuron's real output
LEAVES this volume** — its in-brain out-edges are not its functional output, and
that is the deepest limit of the whole v783 leg. Mass-matched cohort percentile,
NOT the l169c degree-neutral rewire null; the two are never compared. v783's 614
`unknown` top_nt cells are scored at build_graph_banc's default magnitude 0.3.
No BANC pin chain is inherited (the BANC head loads banc_graph.pt and is not
sliced); provenance rests on CERT-783.
