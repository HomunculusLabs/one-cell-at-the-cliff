#!/usr/bin/env python3
"""Tick-260 research scan driver: builds URL-ENCODED angle queries and
hands them to lane/scan_arxiv.py via its `--` extra-query interface.

Rotation this tick is aimed at the cards L228/L215 both named next:
L260 (the GATED linearised two-hop operator at the operating point),
L229 (near-balance as a POPULATION question), L261 (depth profile +
the Perron asymmetry A_inf), L257 (out-of-sample audit), L254
(achieved power of the lane's null verdicts).

Never string-concatenate raw quotes into the URL (arxiv skill law):
every term goes through urllib.parse.quote with safe='+'.
"""
import subprocess, sys, urllib.parse, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SCAN = HERE.parent / 'scan_arxiv.py'


def enc(terms):
    """terms: list of raw query atoms already joined with +AND+ markers."""
    return urllib.parse.quote(terms, safe='+:')


ANGLES = [
    # --- the gated/linearised operator literature (L260) ---
    ('rot-linz',   'all:linearization AND all:"recurrent neural network" AND all:dynamics'),
    ('rot-jacob',  'all:Jacobian AND all:"neural dynamics"'),
    ('rot-effcon', 'all:"effective connectivity" AND all:connectome'),
    ('rot-gain',   'all:"gain modulation" AND all:"network dynamics"'),
    ('rot-linresp','all:"linear response" AND all:"spiking network"'),
    # --- near-balance as a population question (L229) ---
    ('rot-eibal',  'all:"excitation-inhibition balance" AND all:connectome'),
    ('rot-balnet', 'all:"balanced network" AND all:Drosophila'),
    ('rot-disinh', 'all:disinhibition AND all:circuit AND all:model'),
    # --- depth profile / spectral asymptote (L261) ---
    ('rot-perron', 'all:"Perron" AND all:"brain network"'),
    ('rot-walklen','all:"walk length" AND all:"brain network"'),
    ('rot-spectr', 'all:spectral AND all:connectome AND all:propagation'),
    # --- method cards (L254 power, L257 out-of-sample) ---
    ('rot-power',  'all:"statistical power" AND all:connectomics'),
    ('rot-oos',    'all:"out-of-sample" AND all:"neural model" AND all:validation'),
    # --- fly angles outside the core five ---
    ('rot-dn',     'all:"descending neuron" AND all:Drosophila'),
    ('rot-silence','all:silencing AND all:connectome AND all:simulation'),
    ('rot-vnc',    'all:"ventral nerve cord" AND all:model'),
    # --- plain recency listings ---
    ('rot-listNE', 'cat:cs.NE'),
]

extra = [f'{tag}={enc(q.replace(" AND ", "+AND+").replace(" ", "+"))}'
         for tag, q in ANGLES]

cmd = [sys.executable, str(SCAN), '14', '--'] + extra
print('# angles:', len(ANGLES))
for e in extra:
    print('#  ', e)
print(flush=True)
sys.exit(subprocess.call(cmd))
