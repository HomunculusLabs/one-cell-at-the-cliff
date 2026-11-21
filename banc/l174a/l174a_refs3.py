"""L174 stage (a) round 3: the 10.64898 bioRxiv prefix + the MANC record.

Round 2 showed bioRxiv's CURRENT DOI prefix is 10.64898 (the 10.1101 form that
our draft's note field carries returns 'no posts found'); round 3 resolves both
preprint-only entries against that prefix and re-queries the MANC connectome
paper by author+title through Crossref. Same R1/R2/R3 rules, raw stored.
"""
import json, os, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
UA = "peabrain-lane/1.0 (mailto:miso@localhost) python-urllib"


def get(url, tag):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read().decode("utf-8", "replace")
        open(os.path.join(RAW, tag), "w").write(body)
        return body
    except Exception as e:  # noqa: BLE001
        print("  !! fetch failed %s: %s" % (tag, e))
        return None


def toks(s):
    return set(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2)


def overlap(a, b):
    ta, tb = toks(a), toks(b)
    return len(ta & tb) / max(1, len(ta))


out = json.load(open(os.path.join(HERE, "refs.json")))

print("=== round 3a: bioRxiv 10.64898 prefix ===")
BIO = [("sapkal2026", "10.64898/2026.04.29.721658",
        "Central pattern generators for walking in Drosophila"),
       ("dallmann2026", "10.64898/2026.01.04.697356",
        "A dedicated brain circuit controls forward walking in Drosophila")]
for key, doi, want in BIO:
    body = get("https://api.biorxiv.org/details/biorxiv/" + doi, "biorxiv3_%s.json" % key)
    time.sleep(1.2)
    rec = None
    if body:
        coll = json.loads(body).get("collection", [])
        rec = coll[-1] if coll else None
    if not rec:
        print("  --  %-13s no record at %s" % (key, doi))
        continue
    entry = {"doi": rec.get("doi", doi),
             "title": " ".join((rec.get("title") or "").split()),
             "authors_raw": rec.get("authors", ""),
             "container": "bioRxiv", "year": (rec.get("date") or "")[:4],
             "date": rec.get("date", ""), "version": rec.get("version", ""),
             "type": "posted-content", "match_score": 1.0,
             "query": "bioRxiv details API " + doi}
    out["accepted"][key] = entry
    out["rejected"].pop(key, None)
    out["cert1"][key] = {"status": "MATCH" if overlap(want, entry["title"]) >= .8 else "DIFFERS",
                         "source": "biorxiv-api:" + entry["doi"],
                         "score": round(overlap(want, entry["title"]), 3),
                         "remote_title": entry["title"], "local_title": want}
    print("  OK  %-13s %s (%s v%s) [%s]" % (key, entry["title"][:52], entry["date"],
                                            entry["version"], out["cert1"][key]["status"]))

print("\n=== round 3b: MANC connectome record ===")
want = "A connectome of the male Drosophila ventral nerve cord"
url = ("https://api.crossref.org/works?rows=20&select=DOI,title,author,container-title,"
       "issued,volume,page,type&query.author=Takemura&query.title="
       + urllib.parse.quote("connectome male Drosophila ventral nerve cord"))
body = get(url, "q3_takemura.json")
time.sleep(1.2)
BAD = ("elife assessment", "author response", "reviewer", "decision letter",
       "editor's evaluation")
best = None
if body:
    for it in json.loads(body)["message"]["items"]:
        t = (it.get("title") or [""])[0]
        if not t or any(t.lower().startswith(p) for p in BAD):
            continue
        sc = overlap(want, t)
        has = any("takemura" in (a.get("family", "").lower()) for a in it.get("author", []) or [])
        if sc >= .60 and has:
            cand = (it.get("type") == "journal-article", sc, it, t)
            if best is None or cand[:2] > best[:2]:
                best = cand
if best:
    _, sc, it, t = best
    cont = (it.get("container-title") or [""])
    entry = {"doi": it.get("DOI", ""), "title": t,
             "authors": [(a.get("given", ""), a["family"]) for a in it.get("author", []) if a.get("family")],
             "container": cont[0] if cont else "", "volume": it.get("volume", ""),
             "pages": it.get("page", ""), "type": it.get("type", ""),
             "year": (it.get("issued", {}).get("date-parts", [[None]])[0] or [None])[0],
             "match_score": round(sc, 3),
             "query": "crossref author=Takemura title=connectome male Drosophila ventral nerve cord"}
    out["accepted"]["takemura2024"] = entry
    out["rejected"].pop("takemura2024", None)
    print("  OK  takemura2024 %.2f %-15s %s (%s) %s" % (sc, entry["type"], t[:50],
                                                        entry["year"], entry["doi"]))
else:
    print("  --  takemura2024 still unmatched -> DROPPED from this pass (R1)")

json.dump(out, open(os.path.join(HERE, "refs.json"), "w"), indent=1, sort_keys=True)
print("\naccepted=%d rejected=%s" % (len(out["accepted"]), sorted(out["rejected"])))
print("cert1 non-MATCH:", {k: v["status"] for k, v in out["cert1"].items() if v["status"] != "MATCH"})
