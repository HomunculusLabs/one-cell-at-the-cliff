# One cell at the cliff

**Mass-twin controls isolate cell identity — not removal mass — as the carrier of an all-or-none regime transition in a fly connectome model.**

This repository contains the full experiment lineage behind a preprint draft:
every run script, every preregistration, every stored result, the certified
number ledger, and the verification machinery that ties each number in the
draft back to raw artifacts.

## The finding, in one minute

We run the female *Drosophila* brain-and-nerve-cord connectome (BANC v626)
as a rate model, with **every perturbation arm gain-bisected to a matched
operating point** before anything is removed. Then:

- Removing ever-larger descending-neuron cohorts from a bulk-extracted cord
  subnet drives right-tibia antagonist structure through a **non-monotone,
  all-or-none window**: small removals kill it (5 of 178 seeds survive at
  k=19), slightly larger ones super-raise it (188 of 194 at k=29).
- **Mass-twin controls decompose that step.** Two cells whose removal masses
  differ by 3.9e-04: removing one (DNp33-L, "the carrier") converts kill to
  super; removing its mass twin lands intermediate, not neutral.
- The carrier is **sufficient, not unique**, and set-dependent: of seven
  carrier-free cohorts mass-matched to the same window, exactly one supers
  (39 of 48) — with a different (both-sides) signature.
- **Silence ⊂ cut**: activity-clamping the carrier alone is bit-identical to
  removing its edges on every stored channel.
- A **graph × gain 2×2** shows the transition tracks the graph, not the
  matched-gain difference, on both sides of the pair.
- Frequency claims are held **band-relative** (the .100 Hz line is evoked and
  echo-locked, not an endogenous clock — we quantify our own instrument's
  band first).

**Honest scope:** this is a claim about connectome-constrained *model
dynamics* (a uniform-tau rate model, 3 global parameters, one specimen per
connectome), not about flies. The draft scopes itself accordingly. The
methodological contribution — identity-vs-mass decomposition via
mass-matched twins at matched operating points, with preregistered
replication — is, to our knowledge (swept 2026-11-21), unclaimed in the
lesion/ablation literature, where controls are count- or type-matched (see
Habib et al., bioRxiv 10.64898/2026.10.26.762043, the closest prior art).

## Repository map

- `paper/DRAFT.md` — the preprint draft (v3.8+, with Discussion, Methods,
  canonical statistics, 37-entry reference list)
- `paper/numbers.json` — the certified number ledger: every number quoted in
  the draft lives here, keyed by experiment
- `paper/CLAIM-MAP.md` — claim → script → stored artifact → verify section
- `paper/l1{43,49,58,59,61,74}_verify.py` — verification gates (see below)
- `paper/review_fable.md` — an external model-referee's round-1 report (12
  majors) and how each was adjudicated; round-2 report to follow
- `banc/` — the BANC experiment lineage: run/static scripts at the root,
  one directory per experiment (`l101…l174`) holding `PREREG.md`,
  `results_*.json`, anchor files and verdicts
- `banc/banc_graph.pt` — the collapsed BANC v626 graph (38 MB, ready to use)
- `malecns/` — the MaleCNS v1.0 (male connectome) arms; rebuild the graph
  with `malecns/build_graph_male.py` or fetch it from the release assets
- `figures/` — the three published figures (PNG + SVG)
- `LAB-INTENT.md`, `LAB-DIFFDUCK.md` — the lab books, verbatim per-experiment
  verdicts (infrastructure details redacted)
- `MANIFEST.sha256` — checksums of every file in this tree

## Replication ladder

**L0 — verify the stored numbers (minutes, CPU, no dependencies beyond
Python 3.10+ + NumPy):**

```bash
cd one-cell-at-the-cliff
python3 paper/l143_verify.py   # -> L143 verify: ALL GREEN
python3 paper/l149_verify.py   # -> L149 verify: ALL GREEN
python3 paper/l158_verify.py   # -> L158 verify: ALL GREEN
python3 paper/l159_verify.py   # -> L159 sentence scan: PASS
python3 paper/l161_verify.py   # -> L161 verify: ALL GREEN
python3 paper/l174_verify.py   # -> L174 VERIFY: ALL GREEN
```

These re-derive, from the stored `results_*.json` files in `banc/`, every
statistic the draft quotes: Wilson bounds recomputed, pooled unions
re-counted, abstract numeric vocabulary frozen against the ledger. If a
number in `DRAFT.md` ever drifts from its artifact, a gate fails.

Two gates additionally require the **raw anchor traces** (bit-identity
anchors used to prove a re-run reproduces a stored rollout exactly). Those
files exceed GitHub's in-tree size limit and ship as release assets:

```bash
# download the release assets, then place them at these exact relative paths:
#   raw_l135.npz   -> banc/l135/raw_l135.npz
#   raw_l169.npz   -> banc/l169/raw_l169.npz
#   raw_l169c2.npz -> banc/l169c2/raw_l169c2.npz
#   raw_l169d.npz  -> banc/l169d/raw_l169d.npz
#   male_graph.pt  -> malecns/male_graph.pt
```

**L1 — re-run the rollouts (CPU hours, needs PyTorch ≥2.0, CPU-only is fine):**

Each experiment directory's run script is the experiment. Example — the
gain-swap 2×2 that closes the identity-vs-gain confound:

```bash
python3 banc/l169d_run.py   # (scripts at banc/ root; see CLAIM-MAP.md §L169d)
```

Every rollout script carries its own pinned constants block (TAU .05 s,
DT .01 s, RMAX 1, BG .02, NOISE .01, SETTLE 400, WIN 6000, SEG 2000) and
deterministic seeds. The `PREREG.md` in the same directory records the
registered branches and pins that were declared **before** the run; the
stored `anchors_run.json` + anchor npz let you check your re-run is
bit-identical to ours where the design promises it.

**L2 — from raw connectome data (half a day, ~50 GB disk):**

```bash
# 1. Obtain BANC v626 (Harvard Dataverse doi:10.7910/DVN/8TFGGB, CC BY 4.0)
#    and the MaleCNS v1.0 release (Janelia FlyEM, CC BY).
# 2. Rebuild the collapsed graphs:
python3 banc/build_graph_banc.py
python3 malecns/build_graph_male.py
# 3. Re-derive any static card, then any dynamic arm, then the verify gates.
```

See `data/README.md` for full provenance of every input (connectome
releases, annotations, transmitter predictions) and the collapse rules
(synapse counts summed across neuropil rows per connection pair; BANC's
implicit pair-level floor of 3; the male file's no-floor caveat and the
matched-floor re-extraction that follows from it).

## The verification philosophy (why this repo looks over-engineered)

- **Preregistration per experiment:** every dynamic arm has a `PREREG.md`
  declaring branches, pins and precedence before any rollout; post-hoc
  observations are labelled as such in the results files.
- **Bit-identity anchors:** shared-noise rollout streams are anchored to
  stored npz traces; a re-run that the design promises to be identical must
  match to 0.0e+00, or the gate refuses.
- **One canonical ledger:** `numbers.json` is the only source of draft
  numbers; the verify scripts fail if draft text, ledger and artifacts
  disagree at any tolerance they pin (several at exact equality).
- **Honest negatives are shipped:** failed gates, refuted scopes and
  superseded numbers stay in the lineage with their verdict files; the
  draft's supersession claims are asserted against the stored strings.

## Status

Draft v3.8+ (2026-11-21). One external model-referee round adjudicated
(12/12 issues confirmed-in-direction and addressed); a second round is in
flight. Submission to a preprint server is the owner's call, not ours.

**Snapshot note (2026-11-21):** the initial push was taken while the
manuscript's identifier-relabel pass was mid-flight (one gate, `l149`,
transiently red at that instant — a prose edit, not a numbers/artifact
mismatch). This commit is the follow-up snapshot from the next green
checkpoint: all six verification gates pass from this tree.

## License

Code and experiment lineage: MIT (see `LICENSE`). The draft text and
figures: CC BY 4.0. Connectome data remain under their releasing licenses
(CC BY 4.0 for both BANC v626 and MaleCNS v1.0) — cite the original
releases, listed in `data/README.md`.
