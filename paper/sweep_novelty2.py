#!/usr/bin/env python3
"""L140 novelty sweep round 2: looser phrasings + Semantic Scholar (claim class:
single-cell causal carriers, identity-vs-mass, connectome sims)."""
import json, time, urllib.request, urllib.parse

def arxiv(q, n=8):
    url = (f'https://export.arxiv.org/api/query?search_query={q}'
           f'&sortBy=relevance&sortOrder=descending&max_results={n}')
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode()

def show_arxiv(tag, q):
    import xml.etree.ElementTree as ET
    NS = {'a': 'http://www.w3.org/2005/Atom'}
    try:
        root = ET.fromstring(arxiv(q))
    except Exception as e:
        print(f'## {tag} :: ERROR {e}'); time.sleep(3); return
    print(f'## {tag}')
    for entry in root.findall('a:entry', NS):
        title = ' '.join(entry.find('a:title', NS).text.split())
        aid = entry.find('a:id', NS).text.strip().split('/abs/')[-1]
        pub = entry.find('a:published', NS).text[:10]
        print(f'  [{aid}] ({pub}) {title[:110]}')
    print()
    time.sleep(3)

def ss(tag, q, n=10):
    url = ('https://api.semanticscholar.org/graph/v1/paper/search?query=' +
           urllib.parse.quote(q) +
           f'&limit={n}&fields=title,year,externalIds,citationCount')
    req = urllib.request.Request(url, headers={'User-Agent': 'peabrain-lane/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:
        print(f'## SS {tag} :: ERROR {e}'); time.sleep(2); return
    print(f'## SS {tag}')
    for p in data.get('data', []):
        ax = (p.get('externalIds') or {}).get('ArXiv', '-')
        print(f'  [{ax}] ({p.get("year")}) {p.get("title","")[:110]} (cites {p.get("citationCount")})')
    print()
    time.sleep(2)

show_arxiv('loose-single-neuron-conn', 'abs:%22single-neuron%22+AND+abs:connectome')
show_arxiv('loose-silencing-drosophila', 'abs:silencing+AND+abs:Drosophila+AND+abs:model')
show_arxiv('larval-rate-followup', 'all:%22larval+connectome%22+AND+all:rate')
show_arxiv('elegans-single-cell-ablation', 'abs:%22C.+elegans%22+AND+abs:ablation+AND+abs:%22single+neuron%22')
ss('single-neuron-ablation-connectome', 'single neuron ablation connectome simulation')
ss('identity-vs-number-lesion', 'neuron identity versus number lesion connectome model')
ss('silencing-one-neuron-flips', 'silencing one neuron changes network behavior connectome')
ss('critical-cell-connectome-simulation', 'critical cells connectome simulation perturbation')
