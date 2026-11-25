#!/usr/bin/env python3
"""tick 223 fold: append the research digest to LANE-RESEARCH.md and insert
field-informed bracket amendments on L174 / L175 / L178 in LANE.md.

Brackets are inserted at the END of each named card (immediately before the
next line starting '- [' or '## '), the house format. No item is renumbered,
no checkbox is touched, nothing existing is edited.
"""
import re, shutil, sys, pathlib

ROOT = pathlib.Path("/home/t3rpz/critters/peabrain")
LANE = ROOT / "LANE.md"
RES = ROOT / "LANE-RESEARCH.md"

DIGEST = """
## 2026-11-21 — tick 223 (research: hour-21 scan; arXiv 21 angles — 5 core + 16 rotated incl. two L177-aimed inhibition angles and a plain cat:q-bio.NC / cat:cs.NE recency pair; every FLY-named hit already digested, the yield came from the cs.NE listing: one full read + one abstract-level read)

Scan: core (Drosophila+connectome, FlyWire, connectome-constrained, NeuroMechFly, "fly brain"+model) returned only in-window hits already in the journal — 2611.23320 (t167), 2611.14508 (t37), 2611.14498 (t136), 2611.03897 (t195 one-liner), 2611.01866 (in-session sweep), 2611.01457 (segmentation tooling, parked). The four angles aimed at L177's question (`"reciprocal inhibition"+oscillation`, `"half-center"`, `"excitation-inhibition"+rhythm`, `"inhibitory gain"`) came back EMPTY in the 21-day window except one soft-robotics bond-graph paper (2611.16389, pneumatic excitable neurons — no fly, no handle): the field's monotone-inhibition law that L177 is registered against has no newer challenger than Guba, so the card stands as written. Lesion/identity angles (`"in silico"+lesion`, `"single neuron"+necessity`, `"virtual ablation"`, `"cell type"+deletion+network`) all zero — the novelty position from the in-session sweep is unchanged three weeks running. Scan artifacts: `lane/t223/scan1.txt`, `scan2.txt` (script `lane/t223/scan.py`, stdlib, whole-query urlencoded per the skill's trap note).

**arXiv 2611.13681v1 — Praveg Vashishtha (IIT Patna / Sopra Banking Software), "A Functional Preservation Score for Auditing Connectome Operations: Compression, Alignment, Transport, and Local-Rule Writing" (cs.NE / q-bio.NC, 10 Nov 2026; FULL READ of abstract + introduction/contributions + discussion + reproducibility + Appendix A — DISCLOSED: the arXiv HTML extraction elided the bodies of §§3-6, so the FPS formula itself is read at the level of its stated definition, not its equations)** | Introduces **FPS, a null-normalised, behaviourally grounded measure of how much of a network's input-output function survives a STRUCTURAL OPERATION**, and runs five pre-registered studies on the C. elegans connectome + whole-brain calcium (Kato 2015) + signal-propagation atlas (Randi 2023) + hippocampal replay, auditing a partition-align-write "mind-migration" pipeline. Everything deterministic, laptop-scale, every claim mapped to a committed artifact, toolkit released. | The numbers that matter: (1) **a structure-dependent QUANTISATION SPARSITY FLOOR** — uniform int4 / ternary quantisation of a real connectome is forced to roughly **73% / 98% effective sparsity** because heavy-tailed INTEGER synaptic weights round to zero, and **mixed-precision protection of hub neurons lowers those floors to ~27% / 32%**; (2) decoded replay sequences stay identifiable at top-1 **0.69 [0.63,0.74]** (chance .125, perm p<1e-3) from 10-50-bit latents, with a graceful-vs-cliff capacity trade-off; (3) the pipeline fails independently at every stage — the putative **"identity payload" is NOT a functionally separable module (p >= 0.16 at every tested size)**, Gromov-Wasserstein transport collapses once the target's wiring is respected (fidelity 1.00 -> **0.40 [0.31,0.49]**) or alignment is imperfect (**0.06 [0.00,0.13]**), and biologically plausible local plasticity cannot reach the function the target topology provably admits (**gap 0.45 [0.27,0.64], d=2.0**). Stated limits: nematode/small-network scale, coherence in simulation only. | What it changes for peabrain: (a) **a new ROBUSTNESS OPERATION for the floor family, with its own geometry.** Our floor ladders (L146 release-floor histogram, L180 cohort-rule floors) threshold weights ABSOLUTELY; quantisation kills the heavy TAIL proportionally everywhere, and our BANC weights are exactly their object — integer synapse counts, heavy-tailed, release floor 3. Our carrier's mass is .0064 (80 edges), i.e. tail mass by construction, so an int4/ternary pass is a sharper adversary than a synapse floor and costs one static census before any rollout. Their **hub-protection arm has a direct identity analogue**: protect the carrier's 80 edges under a quantisation that otherwise kills the phenotype and the identity claim is stated in a field-standard operation currency. Folded as a bracketed sibling arm on L175 (the floor-family card), static-first per the L146 discipline. (b) **Novelty positioning, and it is a clean complement rather than a threat:** they ask whether identity is a functionally SEPARABLE MODULE and answer no (p >= 0.16, C. elegans, module grain); we ask whether an emergent all-or-none structure transition is carried by ONE CELL's identity at MATCHED removal mass and answer yes (fly cord, single-cell grain). Different organism, different grain, opposite sign — the honest sentence is that module-level separability failing does not bound single-cell carriage, and our mass-matched twin is the control their module screen has no analogue of. Reference candidate, folded on L174. (c) **A convention gap worth one methods line:** FPS is NULL-NORMALISED by construction (explicit trivial-baseline null in the score); our S is compared to nulls but not normalised by them, so cross-paper magnitudes are not commensurable — the same lesson L176 just paid for on Guba's composite (decompose/declare before adopting a field instrument), now on the measure's *normalisation* rather than its terms. (d) Their reproducibility stance (deterministic, laptop, claim -> committed artifact -> figure) is a field precedent to cite beside our bit-identity anchor chain, which is strictly stronger (we certify re-derived numbers to 0.0e+00, not just re-runnability).

**arXiv 2611.16555v1 — Hartman, Hlinka, Klepl, Pidnebesna, Vidnerová (Czech Academy of Sciences / NU Institute), "Similarity-Guided Optimization Strategies for Approximate Network Symmetry Detection" (cs.NE / cs.LG / q-bio.NC, 12 Nov 2026; ABSTRACT + INTRODUCTION read, disclosed)** | Exact automorphisms vanish after a handful of edge changes, so they relax symmetry to an optimisation over permutations (Liu's approximate formulation) and ask whether node-level similarity (centralities) should bias the search. Six metaheuristics (simulated annealing, GA, tabu, PSO, differential evolution, quadratic symmetry approximator) in guided and unguided variants, plus **BASIN** (bilinear soft assignment), on four synthetic families, **structural brain connectomes**, and three networks with known automorphism groups. | The numbers that matter: **guided tabu search (SGTS) has the lowest median score of the guided variants in all 44 synthetic conditions**; BASIN is the better continuous relaxation on rewired lateral graphs; and the headline caveat — **node-similarity guidance is decisive only where a planted orbit exists that the unguided search misses, and is algorithm-dependent elsewhere: regime-dependent, not uniformly positive**. | What it changes for peabrain: a **third twin class, named in field vocabulary**. Our twins are matched on MASS (the L139/L169 mass twin) and on ROUTE (L198's relay-matched twin); approximate symmetry offers the **near-orbit twin** — the cell whose removal a structure-preserving permutation would make interchangeable with the carrier's — which is precisely the control a reviewer means by "is your twin really comparable?". It is also directly askable on our own open asymmetry: L200 found the carrier's contralateral homolog **IN07B031-L silent on base** while IN07B031-R flips the left tibia, i.e. a BROKEN near-symmetry in a cord that is nominally mirror-symmetric, and L70 already taught us to permutation-null every static asymmetry before hunting a wiring cause. Their regime caveat is the honest scope line (expect a planted-orbit regime or nothing) and SGTS is the algorithm to try first. Folded as a bracketed candidate static arm on L178 (the path-signature card, where the carrier-vs-twin structural comparison already lives); NOT a new card — research ticks amend.

Parked one-liners (not read): **2611.25830** (regime-dependent reconstruction of structural connectivity from activity — already parked t195); **2611.24782** ("Learning Trajectories Leave Decodable Traces in Neural Network Weight Space" — weight-space identity decoding, ML-side cousin of our identity axis, no connectome); **2611.16389** (bond-graph pneumatic excitable neuron — the half-center angle's only in-window hit, soft robotics, no handle).
"""

L174_BRACKET = """      [tick 223 research fold, 11-21: REFERENCE CANDIDATE + one positioning
       sentence from arXiv 2611.13681 (Vashishtha, FPS, cs.NE 11-10, C.
       elegans). Their pre-registered screen finds the putative "identity
       payload" is NOT a functionally separable module (p >= 0.16 at every
       tested size). That is the module-grain NEGATIVE beside our
       single-cell POSITIVE: different organism, different grain, and a
       module screen has no analogue of our mass-matched twin, so the
       honest sentence is "module-level separability failing does not
       bound single-cell carriage at matched mass" — never "they found
       the opposite". Second, smaller line for Methods/Discussion: FPS is
       NULL-NORMALISED by construction while our S is null-COMPARED but
       not normalised, so cross-paper magnitudes are not commensurable;
       say so once rather than inviting the comparison. Their
       reproducibility stance (deterministic, laptop, claim -> committed
       artifact -> figure) is a precedent to cite beside our anchor chain,
       which is strictly stronger. Primary-only rule applies (arXiv entry,
       abs + DOI 10.48550/arXiv.2611.13681). See LANE-RESEARCH.md tick 223.]
"""

L175_BRACKET = """      [tick 223 research fold, 11-21: SIBLING ROBUSTNESS ARM in a different
       deletion geometry, from arXiv 2611.13681 (FPS). Their study 1
       measures a structure-dependent QUANTISATION SPARSITY FLOOR on a
       real connectome: uniform int4 / ternary forces ~73% / 98% effective
       sparsity because heavy-tailed INTEGER synaptic weights round to
       zero, and mixed-precision protection of HUB neurons lowers those
       floors to ~27% / 32%. Our weights are the same object (BANC integer
       syn_counts, heavy-tailed, release floor 3 per L146), and our floor
       ladders threshold ABSOLUTELY while quantisation kills the tail
       PROPORTIONALLY everywhere — a genuinely different adversary for a
       carrier whose whole mass (.0064, 80 edges) is tail. Registered
       shape if taken: (i) STATIC FIRST per the L146 discipline — histogram
       the effective sparsity our graph is forced to at int8/int4/ternary
       and report what fraction of the CARRIER's 80 edges survives each,
       before any rollout; (ii) rollout arms only if the static census
       shows the carrier class moving; (iii) the identity arm is their
       hub-protection trick aimed at us — protect the carrier's edges
       under a quantisation that otherwise kills the phenotype, which
       states the claim in a field-standard operation currency; (iv) their
       floors are C. elegans numbers, so ours must be measured, never
       assumed to match. Zero-rollout slice is (i) alone. See
       LANE-RESEARCH.md tick 223.]
"""

L178_BRACKET = """      [tick 223 research fold, 11-21: CANDIDATE STATIC ARM — the near-orbit
       twin, from arXiv 2611.16555 (Hartman/Hlinka et al., approximate
       network symmetry, cs.NE 11-12). Exact automorphisms die after a few
       edge changes; they recast symmetry as an optimisation over
       permutations and benchmark six metaheuristics + BASIN on synthetic
       families, structural brain connectomes and known automorphism
       groups. Guided tabu search (SGTS) wins all 44 synthetic conditions;
       their honest caveat is that similarity guidance is decisive only
       where a PLANTED ORBIT exists and is regime-dependent otherwise.
       For us this names a THIRD twin class beside the mass twin (L139/
       L169) and the relay-matched twin (L198): the cell a structure-
       preserving permutation would make interchangeable with the carrier
       — the control a reviewer means by "is your twin really comparable?"
       It is also directly askable on an open asymmetry: L200's carrier
       homolog IN07B031-L is SILENT on base while -R flips the left tibia,
       a broken near-symmetry in a nominally mirror-symmetric cord (and
       L70's rule stands — permutation-null any static asymmetry before
       hunting a wiring cause). Scope honestly: expect a planted-orbit
       regime or nothing, and their benchmark is structural connectomes,
       not weighted directed cord subnets. Static cost, no rollouts; a
       candidate arm inside this card, not a card of its own. See
       LANE-RESEARCH.md tick 223.]
"""

# NOTE: the board carries TWO cards numbered L175 (the floor-4 LEFT-side test
# and a checked review2-adjudication master card) — the same collision class as
# the two L197s. Anchor on the FULL opening line, never on the bare number.
INSERTS = [
    ("- [ ] L174. manuscript + figures + references pass (zero rollouts, do", L174_BRACKET),
    ("- [ ] L175. floor-4 LEFT-side registered test (rollouts, PREREG first).", L175_BRACKET),
    ("- [ ] L178. linearized top-k path contribution: does the carrier have a", L178_BRACKET),
]


def main():
    text = LANE.read_text()
    lines = text.split("\n")
    n_before = len(lines)
    checked_before = sum(1 for l in lines if l.startswith("- [x]"))
    unchecked_before = sum(1 for l in lines if l.startswith("- [ ]"))

    for card, bracket in INSERTS:
        idxs = [i for i, l in enumerate(lines) if l == card]
        assert len(idxs) == 1, (card, idxs)
        start = idxs[0]
        # end = first following line starting a new item or a new section
        end = None
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("- [") or lines[j].startswith("## "):
                end = j
                break
        assert end is not None, card
        blines = bracket.rstrip("\n").split("\n")
        lines[end:end] = blines
        print(f"inserted {len(blines)} lines for {card} at line {end+1}")

    out = "\n".join(lines)
    LANE.write_text(out)

    # post-conditions
    lines2 = LANE.read_text().split("\n")
    added = len(lines2) - n_before
    checked_after = sum(1 for l in lines2 if l.startswith("- [x]"))
    unchecked_after = sum(1 for l in lines2 if l.startswith("- [ ]"))
    print(f"lines {n_before} -> {len(lines2)} (+{added})")
    print(f"checked {checked_before} -> {checked_after} | unchecked {unchecked_before} -> {unchecked_after}")
    assert checked_before == checked_after and unchecked_before == unchecked_after
    # digest append
    with RES.open("a") as f:
        f.write(DIGEST)
    print("LANE-RESEARCH.md lines:", len(RES.read_text().split("\n")))


if __name__ == "__main__":
    main()
