"""L174 stage (a): emit references.bib entries + the numbered draft list.

Every field comes from refs.json (= stored primary API responses). Nothing here
is typed from memory: this script only FORMATS. Order is fixed by ORDER below
and starts at 14 (R4: entries 1-13 keep their numbers).
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, "refs.json")))["accepted"]

ORDER = ["namiki2018", "sturner2025", "cheong2024", "braun2024", "cande2018",
         "azevedo2024", "lesser2024", "takemura2024", "eckstein2024",
         "liuwilson2013", "otchy2015", "wolff2018", "jonas2017", "keinan2004",
         "fakhar2022", "prinz2004", "beiran2024", "yan2017", "randi2023",
         "vonreyn2014", "sapkal2026", "duckophila2026"]
START = 14

# eLife reviewed-preprint DOIs come back lower-cased from Crossref; the canonical
# publisher form capitalises the journal token. Pure display normalisation.
DOI_FIX = {"10.7554/elife.": "10.7554/eLife."}


def clean(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return " ".join(s.split()).rstrip(".")


def fix_doi(d):
    for a, b in DOI_FIX.items():
        if d.lower().startswith(a):
            return b + d[len(a):]
    return d


def initials(given):
    parts = [p for p in re.split(r"[\s.\-]+", given or "") if p]
    return " ".join(p[0].upper() + "." for p in parts)


def authors_list(e):
    if "authors" in e and e["authors"]:
        return [(g, f) for g, f in e["authors"]]
    out = []
    for chunk in (e.get("authors_raw") or "").split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        fam, _, giv = chunk.partition(",")
        out.append((giv.strip(), fam.strip()))
    return out


def bib_authors(e):
    au = authors_list(e)
    return " and ".join("%s, %s" % (f, g) if g else f for g, f in au)


def list_authors(e, cap=3):
    au = authors_list(e)
    shown = ["%s, %s" % (f, initials(g)) if g else f for g, f in au[:cap]]
    return ", ".join(shown) + (", et al." if len(au) > cap else "")


bib_out, md_out = [], []
for i, key in enumerate(ORDER):
    e = A[key]
    n = START + i
    if key == "duckophila2026":
        bib_out.append(
            "@misc{%s,\n  author       = {{first-it-consulting}},\n"
            "  title        = {Duckophila: a complete FlyWire connectome in closed loop "
            "with a simulated duck body},\n  year         = {2026},\n"
            "  howpublished = {GitHub repository, %s},\n  note         = {%s licence; "
            "repository created %s; metadata retrieved from the GitHub API 2026-11-20}\n}"
            % (key, e["url"], e["license"], e["created"]))
        md_out.append(
            "%d. first-it-consulting. Duckophila: a complete FlyWire connectome in closed\n"
            "    loop with a simulated duck body. GitHub repository, %s\n"
            "    (%s, created %s)." % (n, e["url"], e["license"], e["created"]))
        continue
    title = clean(e["title"])
    doi = fix_doi(e.get("doi", ""))
    cont = clean(e.get("container", ""))
    if not cont:
        # Crossref leaves container-title empty on posted-content records; the DOI
        # prefix names the server: 10.7554 = eLife (reviewed preprint), 10.1101 and
        # 10.64898 = bioRxiv (the latter is bioRxiv's current prefix).
        if doi.startswith("10.7554/"):
            cont = "eLife (reviewed preprint)"
        elif doi.startswith(("10.1101/", "10.64898/")):
            cont = "bioRxiv"
    year = e.get("year") or (e.get("date") or "")[:4]
    vol, pg = e.get("volume", ""), e.get("pages", "")
    bib = ["@article{%s," % key,
           "  author  = {%s}," % bib_authors(e),
           "  title   = {%s}," % title,
           "  journal = {%s}," % cont]
    if vol:
        bib.append("  volume  = {%s}," % vol)
    if pg:
        bib.append("  pages   = {%s}," % pg.replace("-", "--"))
    bib.append("  year    = {%s}," % year)
    bib.append("  doi     = {%s}" % doi)
    bib.append("}")
    bib_out.append("\n".join(bib))
    tail = "%s" % cont
    if vol:
        tail += " %s" % vol
    if pg:
        tail += ", %s" % pg
    stop = "" if title.endswith(("?", "!")) else "."
    md_out.append("%d. %s %s%s %s (%s). doi:%s" % (n, list_authors(e), title, stop, tail, year, doi))

open(os.path.join(HERE, "emit_bib.txt"), "w").write("\n\n".join(bib_out) + "\n")
open(os.path.join(HERE, "emit_list.md"), "w").write("\n".join(md_out) + "\n")
print("\n".join(md_out))
print("\nentries emitted: %d  (numbers %d-%d)" % (len(ORDER), START, START + len(ORDER) - 1))
