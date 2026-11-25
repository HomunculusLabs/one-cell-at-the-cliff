#!/usr/bin/env python3
"""tick 233 research scan: arXiv API sweep, core + FRESH rotated angles.

Rotation this tick is aimed at L178's inverted finding (the carrier is a
short-path AVOIDER of the motor readout, below 100/100 degree-neutral nulls)
and its two follow-ons L206 (avoidance LENGTH SCALE) / L207 (cell or ladder
slot) -- i.e. the network-COMMUNICATION / path-geometry literature, plus the
null-model-methodology angle and the lateralization angle L205 needs.
Stdlib only; the WHOLE query is urlencoded (skill trap note).
"""
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
    # --- L206/L178: path geometry + network communication (FRESH angle) ---
    ("rot: network communication connectome", 'abs:"network communication" AND abs:connectome'),
    ("rot: communicability brain network", 'abs:communicability AND abs:brain'),
    ("rot: shortest path connectome", 'abs:"shortest path" AND abs:connectome'),
    ("rot: signal propagation brain network", 'abs:"signal propagation" AND abs:"brain network"'),
    ("rot: structural controllability brain", 'abs:"structural controllability" AND abs:brain'),
    ("rot: polysynaptic pathway model", 'abs:polysynaptic AND abs:model'),
    # --- null-model methodology (the leg L178's claim rests on) ---
    ("rot: degree-preserving null network", 'abs:"degree-preserving" AND abs:null'),
    ("rot: configuration model brain network", 'abs:"configuration model" AND abs:brain'),
    # --- L205/L207: lateralization + homolog identity ---
    ("rot: lateralization connectome", 'abs:lateralization AND abs:connectome'),
    ("rot: left-right asymmetry circuit", 'abs:"left-right" AND abs:asymmetry AND abs:circuit'),
    # --- fly-side rotations not used in t204/t223 ---
    ("rot: proprioception Drosophila", 'abs:proprioception AND abs:Drosophila'),
    ("rot: descending neuron locomotion", 'abs:"descending neuron" AND abs:locomotion'),
    ("rot: mushroom body model", 'abs:"mushroom body" AND abs:model'),
    ("rot: fruit fly cs.NE", 'all:"fruit fly" AND cat:cs.NE'),
    # --- recency listings ---
    ("rot: cat q-bio.NC recency", 'cat:q-bio.NC'),
    ("rot: cat cs.NE + connectome", 'cat:cs.NE AND abs:connectome'),
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
            time.sleep(3)
            continue
        hits = []
        n_total = len(root.findall('a:entry', NS))
        for e in root.findall('a:entry', NS):
            pub = e.find('a:published', NS).text
            dt = datetime.strptime(pub, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if dt < CUT:
                continue
            aid = e.find('a:id', NS).text.strip().split('/abs/')[-1]
            ti = ' '.join(e.find('a:title', NS).text.split())
            summ = ' '.join(e.find('a:summary', NS).text.split())[:320]
            hits.append((pub[:10], aid, ti, summ))
        print(f"### {label}  [{q}]  parsed: {n_total}  in-window({WINDOW_DAYS}d): {len(hits)}")
        for d, aid, ti, s in hits:
            print(f"  - {d} [{aid}] {ti}")
            print(f"      {s}")
        print()
        sys.stdout.flush()
        time.sleep(3)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"# tick 233 scan | cutoff {CUT.date()} | {datetime.now(timezone.utc).isoformat()}")
    # VALIDATION: one known-hit query first, so a quiet field is proven quiet
    # (skill note: an unencoded query returns an empty body that parses as zero hits).
    run([("VALIDATE: known-hit (attention is all you need)", 'ti:"attention is all you need"')])
    run(CORE if which == "core" else ROTATED if which == "rot" else CORE + ROTATED)
