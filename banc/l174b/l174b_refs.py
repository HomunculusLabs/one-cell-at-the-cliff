#!/usr/bin/env python3
"""L174 stage (b1): fetch the two tick-204 records from PRIMARY APIs.

Rule R1 (PRIMARY-ONLY): every bibliographic field that reaches the draft is
copied out of a live API response stored verbatim under l174b/raw/.
Rule R2 (acceptance): title token overlap >= .60 with our probe title AND at
least one digest author surname present in the record's author list.
Rule R3: bioRxiv's CURRENT prefix is 10.64898; the 10.1101 form of the same
identifier returns "no posts found" (proven again here as a control fetch).

Writes l174b/refs_b.json. Zero rollouts, no RNG.
"""
import json, os, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
os.makedirs(RAW, exist_ok=True)

PROBES = {
    "habib2026": dict(
        doi="10.64898/2026.10.26.762043",
        probe_title="Focal neuronal loss and cell replacement in a connectome "
                    "model of fly steering",
        surnames=["Habib", "Petr", "Rust"],
    ),
    "matsliah2026vnc": dict(
        doi="10.64898/2026.06.14.732053",
        probe_title="Uncovering Sex Differences in the Drosophila Ventral Nerve "
                    "Cord Through Connectome Alignment",
        surnames=["Matsliah", "Murthy", "Seung"],
    ),
}


def get(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "peabrain-lane/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    open(path, "wb").write(raw)
    return json.loads(raw.decode("utf-8", "replace"))


def toks(s):
    return set(w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 2)


out = {"accepted": {}, "rejected": {}, "controls": {}}
for key, p in PROBES.items():
    url = "https://api.biorxiv.org/details/biorxiv/%s" % p["doi"]
    rec_all = get(url, os.path.join(RAW, "biorxiv_%s.json" % key))
    time.sleep(2)
    coll = rec_all.get("collection") or []
    if not coll:
        out["rejected"][key] = {"reason": "no posts found", "url": url}
        continue
    rec = coll[-1]            # highest version
    ov = len(toks(p["probe_title"]) & toks(rec.get("title"))) / \
        max(1, len(toks(p["probe_title"])))
    authors = rec.get("authors", "")
    sur = [s for s in p["surnames"] if s.lower() in authors.lower()]
    ok = ov >= 0.60 and bool(sur)
    entry = {
        "doi": rec.get("doi"),
        "title": rec.get("title"),
        "authors": authors,
        "date": rec.get("date"),
        "version": rec.get("version"),
        "server": rec.get("server") or "bioRxiv",
        "category": rec.get("category"),
        "license": rec.get("license"),
        "jatsxml": rec.get("jatsxml"),
        "published": rec.get("published"),
        "n_versions": len(coll),
        "probe_title": p["probe_title"],
        "title_overlap": round(ov, 4),
        "surname_hits": sur,
        "abstract_head": " ".join((rec.get("abstract") or "").split())[:900],
        "accept": ok,
        "source_url": url,
    }
    (out["accepted"] if ok else out["rejected"])[key] = entry
    print("%-16s ov=%.3f surnames=%s v%s %s %s  ACCEPT=%s"
          % (key, ov, sur, rec.get("version"), rec.get("date"),
             rec.get("license"), ok))

# R3 control: the legacy 10.1101 form of the SAME identifier must not resolve
for key, p in PROBES.items():
    legacy = p["doi"].replace("10.64898/", "10.1101/")
    url = "https://api.biorxiv.org/details/biorxiv/%s" % legacy
    try:
        rec_all = get(url, os.path.join(RAW, "legacy_%s.json" % key))
        msg = (rec_all.get("messages") or [{}])[0].get("status", "?")
        n = len(rec_all.get("collection") or [])
    except Exception as exc:                      # noqa: BLE001
        msg, n = "fetch-error: %s" % exc, 0
    out["controls"]["legacy_%s" % key] = {"doi": legacy, "status": msg, "n": n}
    print("legacy %-22s -> %s (collection %d)" % (legacy, msg, n))
    time.sleep(2)

json.dump(out, open(os.path.join(HERE, "refs_b.json"), "w"), indent=1,
          sort_keys=True)
print("\naccepted: %s" % sorted(out["accepted"]))
print("rejected: %s" % sorted(out["rejected"]))
if len(out["accepted"]) != 2:
    sys.exit("R2 acceptance failed -> branch N2_record_differs")
print("R2 GREEN for both records")
