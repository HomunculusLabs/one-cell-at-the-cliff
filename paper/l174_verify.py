#!/usr/bin/env python3
"""L174 stage (a) verifier — the reference pass as a permanent gate.

Checks, all from artifacts (never from prose):
 (1) bidirectional citation gate: every in-text [n] marker resolves to a
     numbered entry, and every numbered entry is cited at least once in the
     body (the References block and the changelog banner are excluded).
 (2) list integrity: numbers contiguous 1..N, no duplicate DOIs, every entry
     carries a resolvable identifier.
 (3) references.bib <-> draft list: equal counts, and every new entry's DOI
     appears in both files.
 (4) provenance: entries 14-35 match the STORED primary API records in
     banc/l174a/refs.json field-by-field (DOI + title token overlap).
 (5) characterizations: the corrected ApproxBrain / FlyHack / Kopel wordings
     are present verbatim and the superseded wordings are GONE from the body.
 (6) cited field numbers trace to our own stored digests in LANE-RESEARCH.md.
 (7) numbers.json is byte-identical to the pre-tick copy (a reference pass may
     not move a measured value).

Run: python3 paper/l174_verify.py
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, ".."))
DRAFT = open(os.path.join(HERE, "DRAFT.md")).read()
BIB = open(os.path.join(HERE, "references.bib")).read()
L174A = os.path.join(LAB, "banc", "l174a")
REFS = json.load(open(os.path.join(L174A, "refs.json")))
RESEARCH = open(os.path.join(os.path.expanduser("~"), "critters", "peabrain",
                             "LANE-RESEARCH.md")).read()
fails = []


def _ws(s):
    """whitespace-normalized view (L174 b3b): gate literals must not depend
    on where a prose pass puts its line breaks (l122 wrap-fragility lesson)."""
    return re.sub(r"\s+", " ", s)


def ck(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


# ------------------------------------------------------------------ (1)+(2)
head, _, refsec = DRAFT.partition("## References")
refsec_body, _, _ = refsec.partition("## Verification (this skeleton)")
# the changelog banner sits above the title; markers there are history, not citations
banner_end = DRAFT.index("## Title")
body = DRAFT[banner_end:head.rindex("## References")] if False else head[banner_end:]

entries = re.findall(r"^(\d+)\. ", refsec_body, re.M)
nums = [int(n) for n in entries]
ck(nums == list(range(1, len(nums) + 1)),
   "reference numbers not contiguous 1..N: %s" % nums[:50])
N = len(nums)
print("(1) %d numbered entries" % N)
ck("doi:10.64898/2026.01.04.697356" in refsec_body,
   "entry 13 lost the DOI re-resolved from the bioRxiv details API")

markers = set()
for grp in re.findall(r"\[([0-9][0-9,\s]*)\]", body):
    for tok in grp.split(","):
        tok = tok.strip()
        if tok.isdigit():
            markers.add(int(tok))
bad = sorted(m for m in markers if not 1 <= m <= N)
ck(not bad, "in-text markers with no entry: %s" % bad)
uncited = sorted(set(range(1, N + 1)) - markers)
ck(not uncited, "entries never cited in the body: %s" % uncited)
n_marker_tokens = sum(len([t for t in g.split(",") if t.strip().isdigit()])
                      for g in re.findall(r"\[([0-9][0-9,\s]*)\]", body))
print("(2) in-text numeric citation markers: %d tokens, %d distinct entries, uncited %d"
      % (n_marker_tokens, len(markers), len(uncited)))
# the gate's purpose: every entry cited at least once (so >= N tokens) and the
# adjudicated count of 1 decisively exceeded
ck(n_marker_tokens >= N, "in-text citation markers (%d) below one per entry (%d)"
   % (n_marker_tokens, N))

# identifiers + duplicate DOIs (segments split on the numbered-entry openers, so a
# field wrapped onto a continuation line still belongs to its own entry)
parts = re.split(r"\n(?=\d+\. )", refsec_body.strip())
segs = {}
for part in parts:
    m = re.match(r"(\d+)\. ", part)
    if m:
        segs[int(m.group(1))] = " ".join(part.split())
dois = re.findall(r"doi:([^\s,)]+)", refsec_body)
ck(len(dois) == len(set(dois)), "duplicate DOIs in the list: %s"
   % [d for d in set(dois) if dois.count(d) > 1])
ck(sorted(segs) == nums, "entry segmentation does not cover every number")
for n in nums:
    seg = segs[n]
    ck(("doi:" in seg) or ("arXiv:" in seg) or ("github.com" in seg),
       "entry %d carries no resolvable identifier" % n)

# ------------------------------------------------------------------ (3)
bib_keys = re.findall(r"^@\w+\{([^,]+),", BIB, re.M)
ck(len(bib_keys) == N, "bib entries %d != list entries %d" % (len(bib_keys), N))
ck(len(set(bib_keys)) == len(bib_keys), "duplicate bib keys")
print("(3) references.bib keys: %d (unique=%s)" % (len(bib_keys), len(set(bib_keys)) == len(bib_keys)))

# ------------------------------------------------------------------ (4)
def toks(s):
    return set(w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 2)


ORDER = ["namiki2018", "sturner2025", "cheong2024", "braun2024", "cande2018",
         "azevedo2024", "lesser2024", "takemura2024", "eckstein2024",
         "liuwilson2013", "otchy2015", "wolff2018", "jonas2017", "keinan2004",
         "fakhar2022", "prinz2004", "beiran2024", "yan2017", "randi2023",
         "vonreyn2014", "sapkal2026", "duckophila2026"]
checked = 0
for i, key in enumerate(ORDER):
    n = 14 + i
    rec = REFS["accepted"][key]
    seg_flat = segs[n]
    ck(key in BIB, "bib key missing: %s" % key)
    if key == "duckophila2026":
        ck(rec["url"] in seg_flat, "entry %d missing the stored repo url" % n)
        ck(rec["license"] in seg_flat and rec["created"] in seg_flat,
           "entry %d missing stored licence/created date" % n)
    else:
        doi = rec["doi"]
        # the only transform allowed between record and list is eLife's capitalisation
        ck(doi.lower() in seg_flat.lower(), "entry %d DOI %s not from the record" % (n, doi))
        ov = len(toks(rec["title"]) & toks(seg_flat)) / max(1, len(toks(rec["title"])))
        ck(ov >= 0.9, "entry %d title does not match the stored record (%.2f)" % (n, ov))
        # eLife's canonical DOI capitalisation is the one display transform allowed
        ck(doi.lower() in BIB.lower(), "bib entry %s missing DOI %s" % (key, doi))
    checked += 1
print("(4) %d of %d new entries verified against the stored primary records" % (checked, len(ORDER)))

# CERT-1 status recorded by the fetch script
c1 = REFS["cert1"]
nonmatch = {k: v["status"] for k, v in c1.items() if v["status"] != "MATCH"}
ck(len(c1) >= 13, "CERT-1 covered only %d pre-existing entries" % len(c1))
for k, v in c1.items():
    if v["status"] != "MATCH":
        # a non-MATCH is admissible only where the LIST now carries the record's own
        # title (our local probe title was a guess, the stored record is the source)
        ck(k in ORDER, "CERT-1 non-MATCH on a pre-existing entry: %s" % k)
print("(4b) CERT-1 re-resolution of the pre-existing entries: %d/%d MATCH%s"
      % (sum(1 for v in c1.values() if v["status"] == "MATCH"), len(c1),
         " (non-MATCH: %s)" % nonmatch if nonmatch else ""))

# ------------------------------------------------------------------ (5)
REQUIRED = [
    "ApproxBrain [6] is the closest formal neighbour",
    "individually necessary",
    "over 32 held-out parameter draws",
    "necessity is",
    "compared against other subsets rather than against a cell of",
    "matched removal mass",
    "FlyHack [5] stress-tests a connectome-constrained visual",
    "only 25 of 50 ensemble",
    "Kopel-class caveat that does apply is about detection rather than",
    "only 22% of",
    "they cannot bound attachment completeness",
    "Walking-CPG field context (Sapkal et al. [34])",
    "Duckophila [35]",
]
for s in REQUIRED:
    ck(s in body or _ws(s) in _ws(body),
       "required characterization text missing: %r" % s[:48])
GONE = [
    "certifies SUBSET SUFFICIENCY/NECESSITY by",
    "no emergent-transition",
    "shows silencing CLAIMS",
    "critiques (Kopel-class) are INADMISSIBLE",
    "2606.17745",
    "2610.13018",
    "2611.06929",
]
for s in GONE:
    ck(s not in body and _ws(s) not in _ws(body),
       "superseded wording still in the body: %r" % s[:48])
print("(5) %d required characterizations present, %d superseded wordings gone"
      % (len(REQUIRED), len(GONE)))

# ------------------------------------------------------------------ (6)
FIELD = ["32 held-out draws", "25/50 models", "0.872", "0.126", "22%", "41.9%", "40.1%"]
for s in FIELD:
    ck(s in RESEARCH, "cited field number %r is not in our stored digests" % s)
print("(6) %d cited field numbers traced to LANE-RESEARCH digests" % len(FIELD))

# ------------------------------------------------------------------ (7)
pre = os.path.join(L174A, "numbers_pretick.json")
if os.path.exists(pre):
    h1 = hashlib.sha256(open(pre, "rb").read()).hexdigest()
    h2 = hashlib.sha256(open(os.path.join(HERE, "numbers.json"), "rb").read()).hexdigest()
    ck(h1 == h2, "numbers.json changed during a reference pass (%s vs %s)" % (h1[:12], h2[:12]))
    print("(7) numbers.json byte-identical to the pre-tick copy (sha %s)" % h1[:12])
else:
    fails.append("pre-tick numbers.json copy missing")

# ------------------------------------------------------------------ (8)
# stage (b1): the tick-204 novelty narrowing + entries 36/37.
L174B = os.path.join(LAB, "banc", "l174b")
REFS_B = json.load(open(os.path.join(L174B, "refs_b.json")))
ORDER_B = [("habib2026", 36), ("matsliah2026vnc", 37)]
for key, n in ORDER_B:
    rec = REFS_B["accepted"][key]
    seg = segs.get(n, "")
    ck(bool(seg), "entry %d missing from the list" % n)
    ck(rec["accept"] is True, "%s was never accepted under rule R2" % key)
    ck(rec["title_overlap"] >= 0.60, "%s title overlap %.2f below R2" % (key, rec["title_overlap"]))
    ck(bool(rec["surname_hits"]), "%s has no author-surname match (R2)" % key)
    ck(rec["doi"] in seg, "entry %d DOI not copied from the stored record" % n)
    ck(("version %s" % rec["version"]) in seg, "entry %d version not from the record" % n)
    ck(rec["date"] in seg, "entry %d posted date not from the record" % n)
    ov = len(toks(rec["title"]) & toks(seg)) / max(1, len(toks(rec["title"])))
    ck(ov >= 0.9, "entry %d title does not match the record (%.2f)" % (n, ov))
    ck(key in BIB and rec["doi"] in BIB, "bib entry %s missing or DOI absent" % key)
# rule R3 control: the legacy 10.1101 form of both identifiers must not resolve
for ckey, cv in REFS_B["controls"].items():
    ck(cv["n"] == 0, "legacy DOI %s unexpectedly resolved" % cv["doi"])
print("(8) entries 36-37 verified against banc/l174b/refs_b.json; legacy-DOI "
      "controls both unresolved")

REQUIRED_B = [
    "Focal neuronal loss and cell replacement in a connectome model of fly",
    "steering [36] is the closest prior art to the identity half",
    "leaves 57.4% of intact",
    "leave 101.0%",
    "62.5% [60.9-64.0]",
    "10.1% [9.1-11.1]",
    "60.0%",
    "6.7% [6.3-7.0]",
    "89 of their 100 matched cells copy their partners from a",
    "type-dependent integration rather than as single-cell identity",
    "matched on cell count and ours on removal mass",
    "9.72× below any mass-only band (§2.2)",
    "their unit is a class",
    "ours is one cell against one mass twin",
    "they remove and then add",
    "not that identity matters",
    "15% synaptic-amplitude reduction abolished intact",
    "may therefore partly reflect proximity to",
    "the unit of inference\n  is the simulation realization",
    "13,000 neurons intrinsic to the female",
    "[37], which is the",
]
for s in REQUIRED_B:
    ck(s in body or _ws(s) in _ws(body),
       "stage (b1) required text missing: %r" % s[:52])
GONE_B = [
    "The gap this paper fills: an emergent, all-or-none transition",
    "decomposed into IDENTITY vs MASS by",
]
for s in GONE_B:
    ck(s not in body and _ws(s) not in _ws(body),
       "superseded stage-(b1) wording still present: %r" % s[:52])
# sensitivity self-test: the predicate must FAIL on a body with the text removed
probe = REQUIRED_B[2]
ck(probe not in body.replace(probe, "", 1),
   "the required-text predicate is not content-sensitive")
print("(8b) %d narrowing texts present, %d superseded gone, predicate "
      "sensitivity self-test OK" % (len(REQUIRED_B), len(GONE_B)))

FIELD_B = ["57.4%", "101.0%", "62.5%", "10.1%", "60.0%", "6.7%",
           "15% synaptic-amplitude reduction abolished intact wing-motor output",
           "89 of the 100 matched-identity cells",
           "13,000 neurons intrinsic to the"]
for s in FIELD_B:
    ck(s in RESEARCH, "stage-(b1) field number %r is not in our stored digests" % s[:48])
print("(8c) %d stage-(b1) field numbers traced to LANE-RESEARCH digests" % len(FIELD_B))

# P3: the Abstract block pin.  RE-PINNED by stage (b2), which compressed the
# abstract 5,322 -> 1,916 chars under its own contract (l158_verify sections
# 5-10).  The pin's job is unchanged: a LATER prose stage cannot drift the
# abstract without deliberately re-pinning here.
abst = DRAFT[DRAFT.index("## Abstract"):DRAFT.index("## 1. Introduction")]
pin = open(os.path.join(L174B, "abstract_pin_b2.txt")).read().strip()
ck(hashlib.sha256(abst.encode()).hexdigest() == pin,
   "the Abstract block moved since the stage-(b2) pin (%s)" % pin[:12])
pre_b = os.path.join(L174B, "numbers_pretick.json")
ck(hashlib.sha256(open(pre_b, "rb").read()).hexdigest() ==
   hashlib.sha256(open(os.path.join(HERE, "numbers.json"), "rb").read()).hexdigest(),
   "numbers.json moved during stage (b1)")
print("(8d) Abstract block byte-identical to the stage-(b1) pin; numbers.json "
      "unchanged")


print()
if fails:
    print("L174 VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("L174 VERIFY: ALL GREEN")
