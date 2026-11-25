#!/usr/bin/env python3
"""Tick-284 research scan driver (hour-09 RESEARCH tick, 2026-11-25).

Builds URL-ENCODED angle queries and hands them to lane/scan_arxiv.py via
its `--` extra-query interface (the built-in control + 5 core angles run
first; see scan_arxiv.py).

Rotation this tick is aimed at the two open cards in the live thread:
  L293/L295 -- the WORLD session's Hebbian trust delta has no bound but the
      reward population's own ceiling (L293) and the night pass replays one
      post-midnight event (L295).  Angles A (bound) and B (replay selection)
      go after the homeostatic-plasticity and sleep-consolidation literature.
  L294 -- "what predicts a weight-matched set's effect": group ablation is
      not the sum of its members (L240), a weight-matched band still scatters
      9-17 F (L291).  Angles C go after component-ablation / interaction and
      matched-comparison heterogeneity.

Every term goes through urllib.parse.quote (arxiv skill law: never
string-concatenate a raw quote into the URL).
"""
import subprocess, sys, urllib.parse, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SCAN = HERE.parent / 'scan_arxiv.py'


def enc(terms):
    """terms: raw query atoms joined with +AND+ markers."""
    return urllib.parse.quote(terms, safe='+:').replace('%20', '+')


ANGLES = [
    # --- A: the BOUND on a Hebbian accumulator (L293 / L295 proposal 2) ---
    ('rotA-hebbhome', 'all:Hebbian AND all:homeostatic AND all:stability'),
    ('rotA-scaling',  'all:"synaptic scaling" AND all:plasticity'),
    ('rotA-rwmod',    'all:"reward-modulated" AND all:Hebbian'),
    ('rotA-meta',     'all:metaplasticity'),
    ('rotA-threefac', 'all:"three-factor" AND all:plasticity'),
    ('rotA-slide',    'all:"sliding threshold" AND all:plasticity'),
    ('rotA-wnorm',    'all:"weight normalization" AND all:spiking'),
    ('rotA-runaway',  'all:runaway AND all:synaptic AND all:plasticity'),
    # --- B: WHAT GETS REPLAYED (L295 proposal 1) ---
    ('rotB-flysleep', 'all:Drosophila AND all:sleep AND all:memory'),
    ('rotB-dasleep',  'all:dopamine AND all:sleep AND all:consolidation'),
    ('rotB-replaysel','all:replay AND all:sleep AND all:selection'),
    ('rotB-tagging',  'all:"synaptic tagging" AND all:consolidation'),
    # --- C: matched sets / group ablation heterogeneity (L294) ---
    ('rotC-shapley',  'all:Shapley AND all:neurons AND all:ablation'),
    ('rotC-ablgrp',   'all:ablation AND all:"neural network" AND all:interaction AND all:components'),
    ('rotC-matching', 'all:matching AND all:observational AND all:balance'),
    ('rotC-hetero',   'all:"effect heterogeneity" AND all:matching'),
    ('rotC-lescomp',  'all:lesion AND all:connectome AND all:compensation'),
    # --- plain listings beside the control ---
    ('rot-listNCsleep', 'cat:q-bio.NC AND all:sleep'),
]

extra = []
for tag, q in ANGLES:
    raw = q.replace(' AND ', '+AND+').replace(' ', '+')
    extra.append(f'{tag}={urllib.parse.quote(raw, safe="+:")}')

cmd = [sys.executable, str(SCAN), '14', '--'] + extra
print('# angles (driver):', len(ANGLES), '| window: 14 days | built-in: 1 control + 5 core')
for e in extra:
    print('#  ', e)
print(flush=True)
sys.exit(subprocess.call(cmd))
