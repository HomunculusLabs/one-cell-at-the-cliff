#!/usr/bin/env python3
"""tick 223 research scan: arXiv API sweep, core + rotated angles.
Writes one block per query to stdout. Stdlib only (urlencode the WHOLE query)."""
import sys, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = {'a': 'http://www.w3.org/2005/Atom'}
WINDOW_DAYS = 21
CUT = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)

CORE = [
    ("core: Drosophila+connectome", 'all:Drosophila AND all:connectome'),
    ("core: FlyWire", 'all:FlyWire'),
    ("core: connectome-constrained", 'abs:"connectome-constrained"'),
    ("core: NeuroMechFly", 'all:NeuroMechFly'),
    ("core: fly brain simulation", 'abs:"fly brain" AND abs:model'),
]
ROTATED = [
    # L177-relevant: the beta / reciprocal-inhibition monotonicity question
    ("rot: reciprocal inhibition + oscillation", 'abs:"reciprocal inhibition" AND abs:oscillation'),
    ("rot: half-center oscillator", 'abs:"half-center"'),
    ("rot: E/I ratio + rhythm", 'abs:"excitation-inhibition" AND abs:rhythm'),
    ("rot: inhibitory gain + network dynamics", 'abs:"inhibitory gain"'),
    # L178-relevant: path contribution / mechanistic attribution in recurrent nets
    ("rot: path contribution attribution", 'abs:"path contribution"'),
    ("rot: recurrent attribution Jacobian", 'abs:Jacobian AND abs:"recurrent network" AND abs:interpretability'),
    # identity / lesion axis (the preprint's claim class)
    ("rot: in silico lesion", 'abs:"in silico" AND abs:lesion'),
    ("rot: single neuron necessity", 'abs:"single neuron" AND abs:necessity'),
    ("rot: virtual ablation network model", 'abs:"virtual ablation"'),
    ("rot: cell type deletion simulation", 'abs:"cell type" AND abs:deletion AND abs:network'),
    # motor / cord
    ("rot: motor neuron pool model", 'abs:"motor neuron" AND abs:pool AND abs:model'),
    ("rot: ventral nerve cord", 'abs:"ventral nerve cord"'),
    ("rot: insect locomotion control", 'abs:insect AND abs:locomotion AND abs:control'),
    # sleep / plasticity (duck side)
    ("rot: memory consolidation replay model", 'abs:"memory consolidation" AND abs:replay AND abs:model'),
    # recency listings
    ("rot: cat q-bio.NC recency", 'cat:q-bio.NC'),
    ("rot: cat cs.NE recency", 'cat:cs.NE AND abs:brain'),
]

def fetch(q, n=12):
    url = ("https://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": q, "max_results": n,
        "sortBy": "submittedDate", "sortOrder": "descending"}))
    req = urllib.request.Request(url, headers={"User-Agent": "peabrain-lane/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def run(pairs):
    for label, q in pairs:
        try:
            raw = fetch(q)
            root = ET.fromstring(raw)
        except Exception as e:
            print(f"### {label} -- ERROR {e}")
            time.sleep(3); continue
        hits = []
        for e in root.findall('a:entry', NS):
            pub = e.find('a:published', NS).text
            dt = datetime.strptime(pub, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if dt < CUT:
                continue
            aid = e.find('a:id', NS).text.strip().split('/abs/')[-1]
            ti = ' '.join(e.find('a:title', NS).text.split())
            summ = ' '.join(e.find('a:summary', NS).text.split())[:300]
            hits.append((pub[:10], aid, ti, summ))
        print(f"### {label}  [{q}]  in-window({WINDOW_DAYS}d): {len(hits)}")
        for d, aid, ti, s in hits:
            print(f"  - {d} [{aid}] {ti}")
            print(f"      {s}")
        print()
        sys.stdout.flush()
        time.sleep(3)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"# tick 223 scan | cutoff {CUT.date()} | {datetime.now(timezone.utc).isoformat()}")
    run(CORE if which == "core" else ROTATED if which == "rot" else CORE + ROTATED)
