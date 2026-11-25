#!/usr/bin/env python3
"""Tick-284 quote audit: every string quoted in lane/t284/digest.md is
checked against the text THIS run fetched. Whitespace is collapsed on both
sides; the match is case-sensitive. A needle may be pinned to one file
(a bare number matches any cache file, so numbers are checked where they
belong). Prints FOUND/MISSING and exits non-zero if any is MISSING."""
import glob, pathlib, re, sys

HOME = pathlib.Path('/home/t3rpz/.hermes/profiles/maple')
RUN = 'local-ce5843ed9839ef941df138a55b5322db1d3ad24a77df527fee7fcb35d83827a8_20261125T143840Z_'
PRUNED = HOME / 'cache/pruned'
paths = sorted(set(glob.glob(str(HOME / 'cache/web/*.md')) +
                   glob.glob(str(PRUNED / (RUN + 'web_*'))) +
                   [str(HOME.parent.parent.parent / 'critters/peabrain/lane/t284/scan.out')]))
texts = {}
for p in paths:
    try:
        raw = pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
        # the pruned web_* archives hold the result JSON-escaped: a literal
        # backslash-n is a line break there, not a word character
        texts[p] = re.sub(r'\s+', ' ', raw.replace('\\n', ' ').replace('\\t', ' '))
    except OSError as e:
        print('UNREADABLE', p, type(e).__name__)

PLOS_WIN = RUN + 'web_extract_98247732.txt'          # the head+tail window I read
BIORXIV = 'www.biorxiv.org-28c15fc726.md'
SCAN = 'lane/t284/scan.out'

# (label, needle, pin: substring the file NAME must contain, or None)
NEEDLES = [
    ('PLOS-window', 'are activated specifically by odors previously paired with electrical shocks', PLOS_WIN),
    ('PLOS-window', 'engrams in old flies are activated by shock-paired, unpaired, and novel odors', PLOS_WIN),
    ('PLOS-window', 'This enhancement of engram cell activation occurs because of increased activity of dopaminergic neurons during memory consolidation in old flies', PLOS_WIN),
    ('PLOS-window', 'we observed a significant decrease in LTM and an increase in generalization in young flies', PLOS_WIN),
    ('PLOS-window', 'differential response of α2sc-MBONs to CS+ versus other odors', PLOS_WIN),
    ('PLOS-window', 'our data are consistent with a model where reactivation of engram cells during consolidation reinforces memory specificity, while inhibition of engram cell activity during consolidation enhances engram cell connectivity to non-specific inputs', PLOS_WIN),
    ('PLOS-window', 'This increase does not occur after massed training', PLOS_WIN),
    ('PLOS-window', 'Feeding aged flies memantine', PLOS_WIN),
    ('PLOS-window', 'MK801', PLOS_WIN),
    ('PLOS-window', 'Knockdown of Dop2 receptors in engram cells reduces generalization in aged flies', PLOS_WIN),
    ('PLOS-window', 'increasing glial EAAT1 expression', PLOS_WIN),
    ('PLOS-window', 'stimulatory hM1Dq DREADD in PPL1 neurons after training', PLOS_WIN),
    ('PLOS-window', 'rescued by inhibition of PPL1 in aged flies', PLOS_WIN),
    ('PLOS-window', 'aberrant activation of PPL1 neurons in young flies', PLOS_WIN),
    ('PLOS-window', 'Showing 10,259 chars (head) + 3,478 chars (tail) of 17,318 total clean characters', PLOS_WIN),
    ('PLOS-any', 'Published: April 1, 2026', None),
    ('PLOS-any', 'PLoS Biol 24(4): e3003752', None),
    ('BIORXIV', 'Looking up each masked neuron\'s partners through its matched FlyWire neuron, with no learning, reached MRR 0.18–0.48, and the regional models exceeded this lookup in all twelve regions', BIORXIV),
    ('BIORXIV', 'every regional model outperformed the best of three non-graph baselines: geometric-mean MRR ratios ran from 1.33 to 2.08, and model MRR from 0.36 to 0.60', BIORXIV),
    ('BIORXIV', 'Each true partner was ranked against 100 non-partners drawn in proportion to their visible degree', BIORXIV),
    ('BIORXIV', "the second brain's cell types were assigned by matching neurons to FlyWire, and only the graph models read the wiring of a masked neuron's visible same-type neurons (a rule that only copies those neurons' partners lost to the regional models on every confirmation instance)", BIORXIV),
    ('BIORXIV', "features were computed from each neuron's complete reconstruction", BIORXIV),
    ('BIORXIV', 'Ahmadh Hassan, Tyler Ho, Ali Aslam', BIORXIV),
    ('ELIFE', 'disruption of basal activity of a small subset of protocerebral anterior medial DANs (PAM-DANs), by either brief activation or inhibition of the two dorsal posterior medial (DPM) neurons, impairs 24 h LTM', None),
    ('ELIFE', 'result in sleep loss and fragmentation, especially at night', None),
    ('ELIFE', 'pharmacological rescue of sleep after manipulation restores LTM', None),
    ('ELIFE', 'limited evidence to support the mechanistic claim that this circuit directly links sleep and memory consolidation', None),
    ('ELIFE', 'Dop1R1 primarily mediates the link between sleep and memory', None),
    ('ELIFE', 'Version of Record : September 23, 2026', None),
    ('ELIFE', '*eLife* **14**:RP104862', None),
    ('ARX22070', 'We identify an exact algebraic relationship between the polarization of bond dominance and the network', None),
    ('ARX22070', 'the forces associated with active learning bias these local measurements and interfere with restoration', None),
    ('ARX22070', 'Nada Elmeligy, Nidhi Pashine, J. M. Schwarz', None),
    ('ARX22070', 'Submitted on 17 Nov 2026', None),
    ('ARX22070', 'physics.bio-ph', None),
    ('NEWS', 'doi: 10.1126/science.zbwnxjo', None),
    ('NEWS', 'The team connected each of 96 leg muscles to the motor neurons that make them contract', None),
    ('SCAN', 'Positive Weights Do Not Certify TWFE Inference: A Design Diagnostic under Treatment-Effect Heterogeneity', SCAN),
    ('SCAN', '=== SUMMARY: 24 angles, 0 still ERRORED, 5 with in-window hits', SCAN),
    ('ZENKE', 'Continual Learning Through Synaptic Intelligence', None),
]

bad = 0
for label, needle, pin in NEEDLES:
    n = re.sub(r'\s+', ' ', needle)
    cand = [(p, t) for p, t in texts.items() if (pin is None or pin in p)]
    hits = [(p, t) for p, t in cand if n in t]
    if not hits:
        bad += 1
        print(f'MISSING  {label}: {needle[:90]}   [files searched: {len(cand)}]')
    else:
        p, t = hits[0]
        i = t.index(n)
        print(f'FOUND    {label}: {needle[:58]!r}  <- {pathlib.Path(p).name[-34:]}  (of {len(cand)} pinned files)\n'
              f'            ...{t[max(0, i - 40): i + len(n) + 50]}...')
print(f'--- {bad} missing of {len(NEEDLES)} needles over {len(texts)} fetched/scan texts')
sys.exit(1 if bad else 0)
