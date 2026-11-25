#!/usr/bin/env python3
"""tick 243 research scan — arXiv sweep, stdlib only.

Per the arxiv skill: urlencode the WHOLE search_query value, print the raw
parsed entry count beside the in-window count so an API failure cannot
masquerade as a quiet field, and validate the pipeline with a known-hit
control query before trusting any zero.
"""
import sys, time, datetime as dt
import urllib.parse, urllib.request
import xml.etree.ElementTree as ET

NS = {'a': 'http://www.w3.org/2005/Atom'}
API = 'https://export.arxiv.org/api/query?'
WINDOW_DAYS = 21
NOW = dt.datetime(2026, 11, 22, tzinfo=dt.timezone.utc)
CUTOFF = NOW - dt.timedelta(days=WINDOW_DAYS)

CORE = [
    ('core:drosophila-connectome', 'all:Drosophila AND all:connectome'),
    ('core:flywire',               'all:FlyWire'),
    ('core:connectome-constrained','all:"connectome-constrained"'),
    ('core:neuromechfly',          'all:NeuroMechFly'),
    ('core:fly-brain-model',       'all:"fly brain" AND all:model'),
]

# ROTATED this tick onto the statistics-of-cell-type-claims literature that
# L213's open follow-ons (L224 mass-neutral statistic, L225 multiple
# comparisons) need, plus the spectral/eigenvector angle L210 opened.
ROT = [
    ('rot:multiple-comparisons',   'all:"multiple comparisons" AND all:connectome'),
    ('rot:fdr-neuroscience',       'all:"false discovery rate" AND all:"brain network"'),
    ('rot:celltype-null',          'all:"cell type" AND all:"null model" AND all:network'),
    ('rot:permutation-test-brain', 'all:"permutation test" AND all:connectome'),
    ('rot:eigenvector-centrality', 'all:"eigenvector centrality" AND all:brain'),
    ('rot:spectral-connectome',    'all:spectral AND all:connectome AND all:dynamics'),
    ('rot:degree-correction',      'all:"degree correction" AND all:network AND all:null'),
    ('rot:confound-size',          'all:confound AND all:"network size" AND all:neuroscience'),
    ('rot:single-neuron-necessity','all:"single neuron" AND all:perturbation AND all:connectome'),
    ('rot:descending-neuron',      'all:"descending neuron" AND all:Drosophila'),
    ('rot:bilateral-asymmetry',    'all:bilateral AND all:asymmetry AND all:connectome'),
    ('rot:insect-motor-control',   'all:insect AND all:"motor control" AND all:neural'),
    ('rot:qbio-nc-recent',         'cat:q-bio.NC'),
    ('rot:csne-recent',            'cat:cs.NE'),
]

CONTROL = [('CONTROL:known-hit', 'ti:"attention is all you need"')]


def query(label, q, maxr=30):
    params = {'search_query': q, 'start': 0, 'max_results': maxr,
              'sortBy': 'submittedDate', 'sortOrder': 'descending'}
    url = API + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            raw = r.read()
    except Exception as e:
        print(f'[{label}] ERROR {e}')
        return
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f'[{label}] PARSE-ERROR {e} bytes={len(raw)}')
        return
    entries = root.findall('a:entry', NS)
    inwin = []
    for e in entries:
        pub = e.find('a:published', NS).text
        d = dt.datetime.strptime(pub, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
        if d >= CUTOFF:
            aid = e.find('a:id', NS).text.strip().split('/abs/')[-1]
            ti = ' '.join(e.find('a:title', NS).text.split())
            cats = ','.join(c.get('term') for c in e.findall('a:category', NS))
            inwin.append((pub[:10], aid, ti, cats))
    print(f'[{label}] parsed:{len(entries)} in-window:{len(inwin)}  q={q}')
    for d, aid, ti, cats in inwin:
        print(f'    {d}  {aid}  [{cats}]  {ti}')
    print()


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    sets = {'control': CONTROL, 'core': CORE, 'rot': ROT,
            'all': CONTROL + CORE + ROT}[which]
    for label, q in sets:
        query(label, q)
        time.sleep(6.0)
