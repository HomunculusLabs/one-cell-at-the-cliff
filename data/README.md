# Data provenance

This repository derives everything from two public connectome releases plus
their annotation tables. Nothing here would exist without them — cite them
first.

## BANC v626 (female brain + nerve cord) — primary substrate

- **Source:** Harvard Dataverse, `doi:10.7910/DVN/8TFGGB` (CC BY 4.0).
  Complete adult female *Drosophila melanogaster* brain-and-nerve-cord
  connectome (FlyWire-lineage; see the release paper, Bates et al., Nature
  2026, and the distributed-control analysis of the same release).
- **Collapse rule:** connection pairs are collapsed by **summing synapse
  counts across neuropil rows**; cell annotations come from the codex flat
  table; transmitter predictions from the released NT table.
- **Floor caveat:** the BANC release carries an **implicit pair-level
  synapse floor of 3**. This matters: the male-side extraction applied no
  floor and initially looked non-transferable — that was a floor artifact of
  our own extraction, re-scoped in the draft (§2.6) and re-tested at the
  matched floor (see `banc/l170/`).
- **Graph:** `banc/banc_graph.pt` (38 MB) is the collapsed, ready-to-use
  substrate; rebuild it with `banc/build_graph_banc.py`.

## MaleCNS v1.0 (male CNS) — second substrate

- **Source:** MaleCNS v1.0 release, Janelia Research Campus FlyEM and
  collaborators (CC BY). ~165k traced neurons / 25.56M directed connections.
- **Graph:** rebuild with `malecns/build_graph_male.py`, or fetch
  `male_graph.pt` from this repo's release assets (514 MB — too large for
  the git tree) and place it at `malecns/male_graph.pt`.

## What is NOT included

- Raw connectome release files (~50 GB): download from the DOIs above; the
  build scripts name every input file they read.
- Raw rollout traces larger than the release-asset set: regenerable exactly
  from the run scripts + pinned seeds (that is the point of the bit-identity
  anchors).
