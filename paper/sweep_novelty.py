#!/usr/bin/env python3
"""L140 targeted novelty sweep: single-cell causal carriers / identity-vs-mass
in connectome-constrained simulations. ALL-TIME relevance-sorted (not the 14-d
research-tick window) — the question is whether the CLAIM CLASS exists at all.
Stdlib only; sleep 3 between calls (arXiv etiquette)."""
import time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

NS = {'a': 'http://www.w3.org/2005/Atom'}
BASE = 'https://export.arxiv.org/api/query?'

QUERIES = [
    ('single-neuron-silencing-sim', 'all:connectome+AND+all:silencing+AND+all:%22single+neuron%22'),
    ('ablation-causal-connectome', 'all:connectome+AND+all:ablation+AND+all:causal+AND+all:simulation'),
    ('connectome-lesion-model', 'all:%22connectome-constrained%22+AND+all:lesion'),
    ('individual-neuron-necessary', 'all:connectome+AND+all:%22individual+neurons%22+AND+all:necessary'),
    ('cell-identity-vs-count', 'all:connectome+AND+all:ablation+AND+all:identity+AND+all:%22neuron%22'),
    ('shiu-lineage', 'au:Shiu+AND+all:connectome'),
    ('flyvis-silencing', 'all:flyvis+AND+all:silencing'),
    ('drosophila-single-cell-ablation', 'all:Drosophila+AND+all:%22single+cell%22+AND+all:ablation'),
    ('critical-neurons-network-lesion', 'all:%22critical+neurons%22+AND+all:lesion'),
    ('one-neuron-flips-behavior', 'all:Drosophila+AND+all:%22single+neuron%22+AND+all:behavior+AND+all:stimulation'),
]

for tag, q in QUERIES:
    url = (BASE + 'search_query=' + q +
           '&sortBy=relevance&sortOrder=descending&max_results=8')
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            root = ET.fromstring(r.read())
    except Exception as e:
        print(f'## {tag} :: ERROR {e}')
        time.sleep(3)
        continue
    print(f'## {tag}')
    for entry in root.findall('a:entry', NS):
        title = ' '.join(entry.find('a:title', NS).text.split())
        aid = entry.find('a:id', NS).text.strip().split('/abs/')[-1]
        pub = entry.find('a:published', NS).text[:10]
        print(f'  [{aid}] ({pub}) {title[:110]}')
    print()
    time.sleep(3)
