#!/usr/bin/env python3
"""tick 233 fold: append ONE bracketed field-informed amendment to L206.

Research-tick rule: amend existing items, never append new ones, never
renumber. Asserts: checked/unchecked counts UNCHANGED, item-line count
UNCHANGED, and EXACTLY ZERO '- [' lines differ from the pre-tick copy.
"""
import hashlib, shutil, sys, os

LANE = "/home/t3rpz/critters/peabrain/LANE.md"
PRE = "/home/t3rpz/.hermes/profiles/maple/cache/scratch/LANE_pre_t233.md"

ANCHOR = ("      iteration and reported; the depth-2/3 values must reproduce L178's\n"
          "      stored numbers to float equality before any new depth is read.\n")

BRACKET = """      [tick 233 field amendment (2026-11-22 09:0x research scan, Miso) —
       THIS CARD'S INSTRUMENT HAS A FIELD NAME, A STANDARD NORMALISATION
       AND A SECOND STATISTIC IT IS MISSING. Source: Seguin, Sporns &
       Zalesky, "Brain network communication: concepts, models and
       applications", Nat Rev Neurosci 24:557-574 (2023) + Seguin et al,
       bioRxiv 2022.02.18.480871 (full read, LANE-RESEARCH 2026-11-22).
       (a) NAME: our L178 depth-d abs-weight walk sum IS a truncated,
       UN-normalised COMMUNICABILITY (Estrada & Hatano, Phys Rev E 77:036111
       2008) = sum_k W^k/k!; the field's taxonomy splits polysynaptic models
       into ROUTING (shortest-path efficiency, navigation efficiency) vs
       DIFFUSION (communicability, diffusion efficiency), with SEARCH
       INFORMATION (Rosvall et al, Phys Rev E 72:046117 2005) as the hybrid.
       Write the card in that vocabulary — "the carrier has low
       communicability and high search information into the motor pools at
       matched out-mass" is a field-legible sentence; "0.0402 depth-2 reach"
       is not.
       (b) NORMALISATION, and it REPLACES this card's registered one: the
       standard attenuation is the Crofts/Estrada strength normalisation
       W_ij / sqrt(s_i s_j) applied BEFORE the walk sum (the review's stated
       convention, "to attenuate the influence of high strength nodes"), not
       our leading-eigenvalue division. Run BOTH and report both — ours
       keeps depths comparable, theirs makes the number comparable to the
       literature — but the eigenvalue leg stays the primary per the already
       registered branch (iii), since the Crofts form has no spectral-death
       diagnostic.
       (c) A SECOND STATISTIC THIS CARD SHOULD CARRY, free and more directly
       named for our claim: SEARCH INFORMATION SI_ij = -log2(prod T_pq) along
       the shortest path, T_pq = W_pq / s_p (out-strength), on the length
       transform L = -log10(W_normalised). SI literally measures how HIDDEN
       an efficient route is — which is our avoidance phrasing in the field's
       own currency — and it is the one measure that distinguishes "no short
       path exists" from "a short path exists but a walker almost never finds
       it". Register it as its own gate cell (L109), not ANDed with the
       communicability cell. NOTE the length transform is a REAL change of
       object: our depth count is hop count, theirs is cost-weighted, and a
       3-synapse heavy-weight route is SHORT in their metric and depth-3 in
       ours.
       (d) A REGISTERED EXPECTATION OF DISAGREEMENT, from their numbers:
       on 1000 HCP subjects, DIFFUSION beat ROUTING for structure-function
       correspondence — communicability narrowed the SC-FC modular gap by
       20.5% peak AMI / 47.8% AUC MMS (+7.9% peak AMI over SC, p < 1e-16),
       search information +~11% AUC, while NAVIGATION was the only model that
       made it WORSE (-2.3% AUC, p < 1e-8) and shortest-path routing did not
       improve mesoscale correspondence at all. So routing and diffusion legs
       of this card may disagree ON PURPOSE: register in advance that a
       disagreement is INFORMATIVE (it dates the carrier's avoidance to a
       broadcast-vs-route level) and is not an instrument failure.
       (e) NULL UNCHANGED: whichever measures are added, each one is reported
       against the SAME 100 l169c degree-neutral destination swaps L178
       already used — a field measure with no null is exactly the gap the
       Vashishtha FPS note (tick 223) flagged in our own S.
       (f) REFERENCE CANDIDATES for the L174 list (prior art, NOT a threat to
       the identity claim — these are region-level human/undirected measures
       with no mass-matched single-cell control): Seguin/Sporns/Zalesky NRN
       2023 (taxonomy), Estrada & Hatano 2008 (communicability), Rosvall et al
       2005 (search information), Goni et al PNAS 111:833-838 2014 (first
       FC-from-communication demonstration), Avena-Koenigsberger/Misic/Sporns
       Nat Rev Neurosci 19:17-33 2018 (the framework), and Winding et al
       Science 379:eadd9330 2023 — the IN-INSECT precedent, the first
       polysynaptic information-flow analysis on a complete insect connectome,
       which is the closest substrate-matched neighbour and belongs in the
       related-work line whichever way this card lands.]
"""


def main():
    src = open(LANE).read()
    shutil.copyfile(LANE, PRE)
    assert hashlib.md5(open(PRE, 'rb').read()).hexdigest() == \
        hashlib.md5(src.encode()).hexdigest(), "pre-copy drifted"

    assert src.count(ANCHOR) == 1, f"anchor count {src.count(ANCHOR)}"
    out = src.replace(ANCHOR, ANCHOR + BRACKET)

    def items(t):
        return [l for l in t.splitlines() if l.startswith('- [')]
    a, b = items(src), items(out)
    assert len(a) == len(b), f"item count {len(a)} -> {len(b)}"
    diff = [(x, y) for x, y in zip(a, b) if x != y]
    assert not diff, f"item lines changed: {diff[:2]}"
    for mark in ('- [x]', '- [ ]'):
        assert src.count(mark) == out.count(mark), f"{mark} count moved"
    added = len(out.splitlines()) - len(src.splitlines())
    assert added == len(BRACKET.splitlines()), f"added {added}"

    open(LANE, 'w').write(out)
    print(f"OK folded | +{added} lines | checked {out.count('- [x]')} "
          f"unchecked {out.count('- [ ]')} | items {len(b)} | pre={PRE}")


if __name__ == "__main__":
    main()
