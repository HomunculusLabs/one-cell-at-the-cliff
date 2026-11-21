#!/usr/bin/env python3
"""L140 novelty sweep round 3: mass-matched/twin control angle + SS retry with backoff."""
import json, time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
NS = {'a': 'http://www.w3.org/2005/Atom'}

def arxiv_show(tag, q, n=8):
    url = (f'https://export.arxiv.org/api/query?search_query={q}'
           f'&sortBy=relevance&sortOrder=descending&max_results={n}')
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            root = ET.fromstring(r.read())
    except Exception as e:
        print(f'## {tag} :: ERROR {e}'); time.sleep(3); return
    print(f'## {tag}')
    for e in root.findall('a:entry', NS):
        t = ' '.join(e.find('a:title', NS).text.split())
        aid = e.find('a:id', NS).text.strip().split('/abs/')[-1]
        pub = e.find('a:published', NS).text[:10]
        print(f'  [{aid}] ({pub}) {t[:110]}')
    print()
    time.sleep(3)

def ss_retry(tag, q):
    url = ('https://api.semanticscholar.org/graph/v1/paper/search?query=' +
           urllib.parse.quote(q) + '&limit=10&fields=title,year,externalIds,citationCount')
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'peabrain-lane/1.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            print(f'## SS {tag}')
            for p in data.get('data', []):
                ax = (p.get('externalIds') or {}).get('ArXiv', '-')
                print(f'  [{ax}] ({p.get("year")}) {p.get("title","")[:110]} (cites {p.get("citationCount")})')
            print()
            return
        except Exception as e:
            wait = 10 * (attempt + 1)
            print(f'SS {tag} attempt {attempt+1} failed ({e}); sleep {wait}')
            time.sleep(wait)
    print(f'## SS {tag} :: GAVE UP')

arxiv_show('mass-matched-lesion', 'abs:%22mass-matched%22+AND+abs:lesion+AND+abs:neural')
arxiv_show('twin-control-ablation', 'abs:%22matched+control%22+AND+abs:ablation+AND+abs:connectome')
arxiv_show('emulation-lesion-sweep', 'all:%22brain+emulation%22+AND+all:lesion')
ss_retry('single-neuron-ablation-connectome', 'single neuron ablation connectome simulation Drosophila')
