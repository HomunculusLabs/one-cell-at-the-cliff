"""L174 stage (a): primary-source reference fetch + CERT.

Rules (PREREG l174a): every bibliographic field is COPIED from a live primary
API response stored raw under raw/; nothing is typed from memory. Acceptance
needs title token-overlap >= .60 AND a surname match. Journal records are
preferred over preprint records (R3).

Zero rollouts, zero RNG, read-only on all lab artifacts.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
PAPER = os.path.abspath(os.path.join(HERE, "..", "..", "paper"))
os.makedirs(RAW, exist_ok=True)

UA = "peabrain-lane/1.0 (mailto:miso@localhost) python-urllib"


def get(url, tag):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                body = r.read().decode("utf-8", "replace")
            with open(os.path.join(RAW, tag), "w") as f:
                f.write(body)
            return body
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                print(f"  !! fetch failed {tag}: {e}")
                return None
            time.sleep(3)


def toks(s):
    return set(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2)


def overlap(a, b):
    ta, tb = toks(a), toks(b)
    return len(ta & tb) / max(1, len(ta))


def crossref_query(q, tag, rows=5):
    url = ("https://api.crossref.org/works?rows=%d&select=DOI,title,author,"
           "container-title,issued,volume,page,type,publisher&query.bibliographic=%s"
           % (rows, urllib.parse.quote(q)))
    body = get(url, tag)
    time.sleep(1.1)
    if not body:
        return []
    try:
        return json.loads(body)["message"]["items"]
    except Exception:  # noqa: BLE001
        return []


def crossref_doi(doi, tag):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    body = get(url, tag)
    time.sleep(1.1)
    if not body:
        return None
    try:
        return json.loads(body)["message"]
    except Exception:  # noqa: BLE001
        return None


def arxiv_id(aid, tag):
    url = "https://export.arxiv.org/api/query?id_list=" + aid
    body = get(url, tag)
    time.sleep(3.1)
    if not body:
        return None
    import xml.etree.ElementTree as ET
    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(body)
        e = root.find("a:entry", ns)
        if e is None:
            return None
        return {
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [a.find("a:name", ns).text for a in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text[:10],
            "id": e.find("a:id", ns).text,
        }
    except Exception:  # noqa: BLE001
        return None


def fmt(item):
    au = []
    for a in item.get("author", []) or []:
        fam = a.get("family")
        giv = a.get("given", "")
        if fam:
            au.append((giv, fam))
    cont = (item.get("container-title") or [""])
    return {
        "doi": item.get("DOI", ""),
        "title": (item.get("title") or [""])[0],
        "authors": au,
        "container": cont[0] if cont else "",
        "year": (item.get("issued", {}).get("date-parts", [[None]])[0] or [None])[0],
        "volume": item.get("volume", ""),
        "pages": item.get("page", ""),
        "type": item.get("type", ""),
        "publisher": item.get("publisher", ""),
    }


# ---------------------------------------------------------------- targets
# (key, intended title, required surname, query string)
TARGETS = [
    ("namiki2018", "The functional organization of descending sensory-motor pathways in Drosophila", "Namiki",
     "Namiki functional organization of descending sensory-motor pathways in Drosophila eLife"),
    ("sturner2025", "Comparative connectomics of the descending and ascending neurons of the Drosophila nervous system", "Stürner",
     "Sturner comparative connectomics descending ascending neurons Drosophila nervous system"),
    ("cheong2024", "Transforming descending input into behavior: the organization of premotor circuits in the Drosophila male adult nerve cord connectome", "Cheong",
     "Cheong transforming descending input into behavior premotor circuits Drosophila male adult nerve cord connectome"),
    ("braun2024", "Descending networks transform command signals into population motor control", "Braun",
     "Braun Ramdya descending networks transform command signals into population motor control Nature"),
    ("cande2018", "Optogenetic dissection of descending behavioral control in Drosophila", "Cande",
     "Cande optogenetic dissection of descending behavioral control in Drosophila eLife"),
    ("azevedo2024", "Connectomic reconstruction of a female Drosophila ventral nerve cord", "Azevedo",
     "Azevedo connectomic reconstruction of a female Drosophila ventral nerve cord Nature"),
    ("lesser2024", "Synaptic architecture of leg and wing premotor control networks in Drosophila", "Lesser",
     "Lesser synaptic architecture of leg and wing premotor control networks in Drosophila Nature"),
    ("takemura2024", "A connectome of the male Drosophila ventral nerve cord", "Takemura",
     "Takemura a connectome of the male Drosophila ventral nerve cord eLife"),
    ("eckstein2024", "Neurotransmitter classification from electron microscopy images at synaptic sites in Drosophila melanogaster", "Eckstein",
     "Eckstein neurotransmitter classification from electron microscopy images at synaptic sites Drosophila melanogaster Cell"),
    ("liuwilson2013", "Transient and specific inactivation of Drosophila neurons in vivo using a native ligand-gated ion channel", "Liu",
     "Liu Wilson transient and specific inactivation of Drosophila neurons in vivo native ligand-gated ion channel Current Biology"),
    ("otchy2015", "Acute off-target effects of neural circuit manipulations", "Otchy",
     "Otchy acute off-target effects of neural circuit manipulations Nature"),
    ("wolff2018", "The promise and perils of causal circuit manipulations", "Wolff",
     "Wolff Olveczky the promise and perils of causal circuit manipulations Current Opinion in Neurobiology"),
    ("jonas2017", "Could a neuroscientist understand a microprocessor?", "Jonas",
     "Jonas Kording could a neuroscientist understand a microprocessor PLoS Computational Biology"),
    ("keinan2004", "Fair attribution of functional contribution in artificial and biological networks", "Keinan",
     "Keinan fair attribution of functional contribution in artificial and biological networks Neural Computation"),
    ("fakhar2022", "Systematic perturbation of an artificial neural network: a step towards quantifying causal contributions in the brain", "Fakhar",
     "Fakhar Hilgetag systematic perturbation of an artificial neural network quantifying causal contributions brain"),
    ("prinz2004", "Similar network activity from disparate circuit parameters", "Prinz",
     "Prinz Bucher Marder similar network activity from disparate circuit parameters Nature Neuroscience"),
    ("beiran2024", "Prediction of neural activity in connectome-constrained recurrent networks", "Beiran",
     "Beiran Litwin-Kumar prediction of neural activity in connectome-constrained recurrent networks"),
    ("yan2017", "Network control principles predict neuron function in the Caenorhabditis elegans connectome", "Yan",
     "Yan network control principles predict neuron function Caenorhabditis elegans connectome Nature"),
    ("randi2023", "Neural signal propagation atlas of Caenorhabditis elegans", "Randi",
     "Randi Leifer neural signal propagation atlas of Caenorhabditis elegans Nature"),
    ("vonreyn2014", "A spike-timing mechanism for action selection", "Reyn",
     "von Reyn Card a spike-timing mechanism for action selection Nature Neuroscience"),
]

out = {"accepted": {}, "rejected": {}, "cert1": {}, "notes": []}

print("=== (1) missing-citation list: Crossref primary records ===")
for key, want, surname, q in TARGETS:
    items = [fmt(i) for i in crossref_query(q, "q_%s.json" % key)]
    scored = []
    for it in items:
        sc = overlap(want, it["title"]) if it["title"] else 0.0
        has_sur = any(surname.lower().replace("ü", "u") in (f.lower().replace("ü", "u"))
                      for _, f in it["authors"])
        scored.append((sc, has_sur, it))
    # R3: prefer journal-article among acceptable candidates
    ok = [s for s in scored if s[0] >= 0.60 and s[1]]
    ok.sort(key=lambda s: (s[2]["type"] == "journal-article", s[0]), reverse=True)
    if ok:
        sc, _, it = ok[0]
        it["match_score"] = round(sc, 3)
        it["query"] = q
        out["accepted"][key] = it
        print("  OK  %-14s %.2f  %-18s %s (%s) %s" % (
            key, sc, it["type"], it["title"][:62], it["year"], it["doi"]))
    else:
        best = max(scored, key=lambda s: s[0]) if scored else (0, False, {})
        out["rejected"][key] = {"best_score": round(best[0], 3),
                                "best_title": best[2].get("title", ""),
                                "query": q}
        print("  --  %-14s NO MATCH (best %.2f: %s)" % (
            key, best[0], best[2].get("title", "")[:60]))

print("\n=== (2) Sapkal bioRxiv DOI ===")
sap = crossref_doi("10.1101/2026.04.29.721658", "doi_sapkal.json")
if sap:
    it = fmt(sap)
    it["match_score"] = 1.0
    it["query"] = "DOI lookup 10.1101/2026.04.29.721658 (id from our own L154 artifacts)"
    out["accepted"]["sapkal2026"] = it
    print("  OK  sapkal2026  %s (%s) %s" % (it["title"][:70], it["year"], it["container"]))
else:
    out["rejected"]["sapkal2026"] = {"best_score": 0.0, "note": "DOI did not resolve"}
    print("  --  sapkal2026 DOI did not resolve")

print("\n=== (3) Duckophila software record (GitHub API) ===")
gh = get("https://api.github.com/search/repositories?q=duckophila&per_page=5", "gh_duckophila.json")
if gh:
    try:
        hits = json.loads(gh).get("items", [])
    except Exception:  # noqa: BLE001
        hits = []
    for h in hits:
        print("  cand: %s  stars=%s  license=%s  created=%s" % (
            h.get("full_name"), h.get("stargazers_count"),
            (h.get("license") or {}).get("spdx_id"), (h.get("created_at") or "")[:10]))
    pick = next((h for h in hits if "duckophila" in (h.get("name") or "").lower()), None)
    if pick:
        out["accepted"]["duckophila2026"] = {
            "repo": pick.get("full_name"), "url": pick.get("html_url"),
            "license": (pick.get("license") or {}).get("spdx_id", ""),
            "created": (pick.get("created_at") or "")[:10],
            "description": pick.get("description", ""),
            "match_score": 1.0, "query": "GitHub search api: duckophila",
        }
        print("  OK  duckophila2026 -> %s" % pick.get("full_name"))
    else:
        out["rejected"]["duckophila2026"] = {"note": "no repo named duckophila in search hits"}
time.sleep(1)

print("\n=== CERT-1: re-resolve the 13 existing bib entries ===")
bib = open(os.path.join(PAPER, "references.bib")).read()
entries = re.findall(r"@article\{([^,]+),(.*?)\n\}", bib, re.S)
print("  bib entries found: %d" % len(entries))
for key, body in entries:
    title = re.search(r"title\s*=\s*\{(.*?)\},?\n", body, re.S)
    title = " ".join(title.group(1).split()) if title else ""
    doi = re.search(r"doi\s*=\s*\{([^}]+)\}", body)
    note = re.search(r"arXiv:(\d{4}\.\d{4,5})", body)
    rec, src = None, ""
    if doi:
        m = crossref_doi(doi.group(1), "cert_%s.json" % key)
        if m:
            rec, src = fmt(m), "crossref:" + doi.group(1)
    elif note:
        a = arxiv_id(note.group(1), "cert_%s.xml" % key)
        if a:
            rec, src = {"title": a["title"], "year": a["published"][:4]}, "arxiv:" + note.group(1)
    if rec is None:
        out["cert1"][key] = {"status": "UNRESOLVED", "source": src or "none"}
        print("  ??  %-18s UNRESOLVED" % key)
        continue
    sc = overlap(title.replace("{", "").replace("}", ""), rec["title"])
    status = "MATCH" if sc >= 0.80 else "DIFFERS"
    out["cert1"][key] = {"status": status, "source": src, "score": round(sc, 3),
                         "remote_title": rec["title"], "local_title": title}
    print("  %-7s %-18s %.2f  %s" % (status, key, sc, rec["title"][:58]))

with open(os.path.join(HERE, "refs.json"), "w") as f:
    json.dump(out, f, indent=1, sort_keys=True)

print("\naccepted=%d rejected=%d cert1_match=%d/%d" % (
    len(out["accepted"]), len(out["rejected"]),
    sum(1 for v in out["cert1"].values() if v["status"] == "MATCH"), len(out["cert1"])))
