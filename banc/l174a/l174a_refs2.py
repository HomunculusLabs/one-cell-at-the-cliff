"""L174 stage (a) round 2: the three Crossref misses + the dallmann CERT gap.

eLife articles return an 'eLife Assessment' / 'Author response' record ahead of
the article itself, so round 2 re-queries with those record classes filtered out.
bioRxiv-only DOIs are resolved against the bioRxiv API (primary server) rather
than Crossref. Same R1/R2/R3 rules; raw responses stored under raw/.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
PAPER = os.path.abspath(os.path.join(HERE, "..", "..", "paper"))
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
                print("  !! fetch failed %s: %s" % (tag, e))
                return None
            time.sleep(3)


def toks(s):
    return set(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2)


def overlap(a, b):
    ta, tb = toks(a), toks(b)
    return len(ta & tb) / max(1, len(ta))


def fmt(item):
    au = []
    for a in item.get("author", []) or []:
        if a.get("family"):
            au.append((a.get("given", ""), a["family"]))
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

BAD_PREFIX = ("elife assessment", "author response", "reviewer", "editor's evaluation",
              "decision letter")

out = json.load(open(os.path.join(HERE, "refs.json")))

print("=== round 2a: eLife articles (assessment records filtered) ===")
R2 = [
    ("cheong2024", "Transforming descending input into behavior: the organization of premotor circuits in the Drosophila male adult nerve cord connectome", "Cheong",
     "Cheong Tuthill premotor circuits Drosophila male adult nerve cord connectome descending input behavior"),
    ("takemura2024", "A connectome of the male Drosophila ventral nerve cord", "Takemura",
     "Takemura Hayworth Scheffer a connectome of the male Drosophila ventral nerve cord"),
]
for key, want, surname, q in R2:
    items = [fmt(i) for i in crossref_query(q, "q2_%s.json" % key, rows=10)]
    cands = []
    for it in items:
        t = (it["title"] or "").strip().lower()
        if any(t.startswith(p) for p in BAD_PREFIX):
            continue
        sc = overlap(want, it["title"]) if it["title"] else 0.0
        has = any(surname.lower() in f.lower() for _, f in it["authors"])
        if sc >= 0.60 and has:
            cands.append((it["type"] == "journal-article", sc, it))
    cands.sort(key=lambda c: (c[0], c[1]), reverse=True)
    if cands:
        _, sc, it = cands[0]
        it["match_score"] = round(sc, 3)
        it["query"] = q + " [round2: assessment records filtered]"
        out["accepted"][key] = it
        out["rejected"].pop(key, None)
        print("  OK  %-13s %.2f %-16s %s (%s) %s" % (key, sc, it["type"],
              it["title"][:55], it["year"], it["doi"]))
    else:
        print("  --  %-13s still no match" % key)

print("\n=== round 2b: bioRxiv API for the preprint-only DOIs ===")
BIO = [("sapkal2026", "10.1101/2026.04.29.721658"),
       ("dallmann2026", "10.1101/2026.01.04.697356")]
for key, doi in BIO:
    body = get("https://api.biorxiv.org/details/biorxiv/" + doi, "biorxiv_%s.json" % key)
    time.sleep(1.2)
    rec = None
    if body:
        try:
            coll = json.loads(body).get("collection", [])
            rec = coll[-1] if coll else None
        except Exception:  # noqa: BLE001
            rec = None
    if not rec:
        print("  --  %-13s bioRxiv API returned no record for %s" % (key, doi))
        out["rejected"][key] = {"note": "bioRxiv API: no record for " + doi}
        continue
    entry = {
        "doi": rec.get("doi", doi),
        "title": " ".join((rec.get("title") or "").split()),
        "authors_raw": rec.get("authors", ""),
        "container": "bioRxiv",
        "year": (rec.get("date") or "")[:4],
        "date": rec.get("date", ""),
        "version": rec.get("version", ""),
        "type": "posted-content",
        "match_score": 1.0,
        "query": "bioRxiv details API " + doi,
    }
    out["accepted"][key] = entry
    out["rejected"].pop(key, None)
    print("  OK  %-13s %s (%s v%s)" % (key, entry["title"][:58], entry["date"], entry["version"]))

# CERT-1 follow-up for dallmann: record the resolution source actually used
if "dallmann2026" in out["accepted"]:
    out["cert1"]["dallmann2026"] = {
        "status": "MATCH" if overlap(
            "A dedicated brain circuit controls forward walking in Drosophila",
            out["accepted"]["dallmann2026"]["title"]) >= 0.8 else "DIFFERS",
        "source": "biorxiv-api:" + out["accepted"]["dallmann2026"]["doi"],
        "score": round(overlap("A dedicated brain circuit controls forward walking in Drosophila",
                               out["accepted"]["dallmann2026"]["title"]), 3),
        "remote_title": out["accepted"]["dallmann2026"]["title"],
        "local_title": "A dedicated brain circuit controls forward walking in Drosophila",
    }
    print("\n  CERT-1 dallmann2026 -> %s (%.2f)" % (
        out["cert1"]["dallmann2026"]["status"], out["cert1"]["dallmann2026"]["score"]))

with open(os.path.join(HERE, "refs.json"), "w") as f:
    json.dump(out, f, indent=1, sort_keys=True)
print("\naccepted=%d rejected=%d" % (len(out["accepted"]), len(out["rejected"])))
print("rejected keys:", sorted(out["rejected"]))
