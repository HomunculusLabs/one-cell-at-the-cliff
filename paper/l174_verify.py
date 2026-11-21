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
# L183 PIN UPDATE (2026-11-21, master fold; receipt in LANE-LOG + banc/l183_worklog.md).
# OLD: sha256(numbers.json) == sha256(pre-tick copy) = 238bf2d37f51...; a whole-file
# equality, written when a reference pass had no business adding a measurement.
# NEW: the master fold legitimately ADDS measured keys (the scan, its replication,
# the timing analysis, the relay arms, the gate-jitter run, the paired twin test,
# the substrate census and the parsed weight rule), so whole-file equality is
# replaced by the same guarantee stated per key, plus two things the old form
# could not say: (a) EVERY pre-tick key is byte-identical under canonical JSON
# (a reference or prose pass still may not move a measured value); (b) the set
# of added keys equals the DECLARED set below EXACTLY, so nothing enters
# undeclared; (c) the post-fold file is itself pinned by hash in
# l183_verify.py, where each added key is also re-derived from its source.
L183_ADDED = {
    "l135.weights", "l172.paired_twin", "l175.branch", "l175.census",
    "l175.bands", "l175.certs", "l175.meta", "l175.null", "l175.scan", "l175.verdict",
    "l184.anatomy", "l184.design", "l184.q1", "l184.q1_twins", "l184.q3", "l184.q3_ratios",
    "l184.sens", "l184.threepanel", "l185.base", "l185.branches",
    "l185.certs", "l185.meta", "l185.r1", "l185.r2", "l185.r3",
    "l186.branch", "l186.contrasts", "l186.means", "l186.phase",
    "l186.power", "l187.arms", "l187.base", "l187.branches", "l187.certs",
    "l187.contrasts", "l187.fast", "l187.g74914_rate", "l187.gain_slopes",
    "l187.meta", "l187.relay", "l187.relay_rate", "l187.sc25_pooled",
    "l187.sc40_pooled", "l92.substrate",
    "l183.ladder_fast", "l183.ladder_fast_meta"}
# L190b PIN UPDATE (2026-11-21, owner-directed follow-up fold; receipt in
# LANE-LOG + banc/l190b_worklog.md).  OLD: added keys == L183_ADDED (46 keys).
# NEW: added keys == L183_ADDED | L190B_ADDED (46 + 6), still an EXACT set
# equality, and guarantee (a) is untouched: every pre-tick key byte-identical.
# REASON: the single-edge cut (banc/l190) is folded into section 2.4; its six
# keys are re-derived from the stored per-seed rows in l183_verify.py (5).
L190B_ADDED = {
    "l190.arms", "l190.certs", "l190.gain", "l190.meta", "l190.selection",
    "l190.summary"}
assert L183_ADDED.isdisjoint(L190B_ADDED) and len(L183_ADDED) == 46
# L197 PIN UPDATE (2026-11-21, owner-directed fourth-round minor repairs;
# receipt in LANE-LOG + banc/l197_worklog.md).  OLD: added keys ==
# L183_ADDED | L190B_ADDED (46 + 6).  NEW: == L183_ADDED | L190B_ADDED |
# L197_ADDED (46 + 6 + 5), still an EXACT set equality, and guarantee (a) is
# untouched: every pre-tick key byte-identical.  REASON: the per-set jitter
# table (M1) and the yardstick / null-centre calibration (M2) print numbers
# that were stored but had no key; the five keys are re-derived from their
# stored sources in l183_verify.py (5).
L197_ADDED = {
    "l139.contrast", "l139.gains", "l139.sets", "l175.null_centre",
    "l197.reference"}
assert L197_ADDED.isdisjoint(L183_ADDED | L190B_ADDED) and len(L190B_ADDED) == 6
DECLARED_ADDED = L183_ADDED | L190B_ADDED | L197_ADDED


def _numbers_guard(pre_path, label):
    if not os.path.exists(pre_path):
        fails.append("pre-tick numbers.json copy missing (%s)" % label)
        return
    old = json.load(open(pre_path))
    assert hashlib.sha256(open(pre_path, "rb").read()).hexdigest().startswith(
        "238bf2d37f51"), "the stored pre-tick copy itself moved"
    new = json.load(open(os.path.join(HERE, "numbers.json")))
    moved = sorted(k for k in old if json.dumps(old[k], sort_keys=True)
                   != json.dumps(new.get(k), sort_keys=True))
    ck(not moved, "%s: pre-tick numbers.json keys moved: %s" % (label, moved[:6]))
    added = set(new) - set(old)
    ck(added == DECLARED_ADDED, "%s: added keys differ from the declared L183 + "
       "L190b + L197 set: undeclared %s, missing %s"
       % (label, sorted(added - DECLARED_ADDED)[:6],
          sorted(DECLARED_ADDED - added)[:6]))
    return len(old), len(added)


_g7 = _numbers_guard(os.path.join(L174A, "numbers_pretick.json"), "(7)")
if _g7:
    print("(7) numbers.json: all %d pre-tick keys byte-identical per key; the %d "
          "added keys are exactly the declared L183 + L190b + L197 set" % _g7)

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
# L183 PIN UPDATE (2026-11-21, master fold; receipt in LANE-LOG and
# banc/l183_worklog.md).  OLD: all 21 strings required verbatim in the LIVE
# body.  The fold renumbers the Results subsections (old 2.2 -> 2.7) and, at
# its related-work stage, withdraws three of the 21 on referee instruction:
#   "9.72x below any mass-only band" -- round 2 showed there is no mass-only
#       band for the ratio to refer to (a carrier-free cohort reaches the
#       class), so the phrase is replaced by the multi-currency statement;
#   "ours is one cell against one mass twin" -- the comparison is now a
#       ladder of single-cell comparators, and the mass twin is silent.
# NEW, never looser: (i) all 21 are still required VERBATIM in the body they
# were written for, the stored hash-pinned pre-image; (ii) in the LIVE body
# the other 19 are required under the declared renumber, and each withdrawn
# string must be GONE and its declared successor PRESENT, so neither the old
# nor a third wording can stand.  The live body is bound to the pre-image by
# byte replay in (8d).
sys.path.insert(0, HERE)
import l183_fold as F183   # noqa: E402  (stdlib only; never writes a file)
import l183_text as T183   # noqa: E402
_pre_body = F183.pre_body()
for s in REQUIRED_B:
    ck(s in _pre_body or _ws(s) in _ws(_pre_body),
       "stage (b1) required text missing from the stored pre-image: %r" % s[:52])
_st = T183.CURRENT_STAGE
WITHDRAWN_B = {
    "9.72\u00d7 below any mass-only band (\u00a72.2)":
        "No single currency suffices",
    "ours is one cell against one mass twin":
        "ours is one cell against single-cell comparators",
    # the gap paragraph it sat in claimed an "all-or-none identity step" that
    # "survives a mass-matched twin control"; the concession is KEPT, in a
    # stronger and separately cited form
    "not that identity matters":
        "That identity matters is prior art [6, 36]",
}
n_live = 0
for s in REQUIRED_B:
    if s in WITHDRAWN_B and _st >= 4:
        gone = s.replace("(\u00a72.2)", "").strip()
        ck(gone not in body and _ws(gone) not in _ws(body),
           "withdrawn stage-(b1) wording still in the live body: %r" % s[:52])
        ck(_ws(WITHDRAWN_B[s]) in _ws(body),
           "declared successor of %r missing" % s[:40])
        continue
    live_s = s.replace("(\u00a72.2)", "(\u00a72.7)") if _st >= 2 else s
    ck(live_s in body or _ws(live_s) in _ws(body),
       "stage (b1) required text missing from the live body: %r" % s[:52])
    n_live += 1
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
print("(8b) %d narrowing texts present in the stored pre-image; in the live body "
      "%d required (under the declared renumber) and %d withdrawn-with-successor; "
      "%d superseded gone; predicate sensitivity self-test OK"
      % (len(REQUIRED_B), n_live, len(REQUIRED_B) - n_live, len(GONE_B)))

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
# L183 PIN UPDATE (2026-11-21, master fold; receipt in LANE-LOG and
# banc/l183_worklog.md).  OLD: the LIVE abstract must hash to the stored
# stage-(b2) pin 20be2db8d67f...  The owner-directed fold replaces the
# abstract (three referee rounds retired its headline wording), so the pin
# is re-pointed, not dropped: (i) the stored pin must still match the
# abstract of the stored pre-image banc/l174b4iiic/draft_post_preview.md,
# and (ii) the live draft must equal declared_edits(that pre-image) byte for
# byte.  A later prose stage therefore still cannot drift the abstract: it
# would have to add a declared edit to the ledger, and l158_verify (16)
# carries the new byte pin.
PRE183 = F183.pre_composite(DRAFT)
abst = PRE183[PRE183.index("## Abstract"):PRE183.index("## 1. Introduction")]
pin = open(os.path.join(L174B, "abstract_pin_b2.txt")).read().strip()
ck(hashlib.sha256(abst.encode()).hexdigest() == pin,
   "the stored pre-image Abstract no longer matches the stage-(b2) pin (%s)"
   % pin[:12])
try:
    STAGE183 = F183.assert_bound(DRAFT)
except AssertionError as _e:
    STAGE183 = -1
    ck(False, "(8d) %s" % _e)
pre_b = os.path.join(L174B, "numbers_pretick.json")
# L183 PIN UPDATE: same re-statement as section (7) -- per-key identity of every
# pre-tick key plus the exact declared added set, instead of whole-file equality.
_numbers_guard(pre_b, "(8d)")
print("(8d) stored pre-image Abstract == the stage-(b2) pin and the live draft == "
      "declared_edits(pre-image) at fold stage %d; numbers.json pre-tick keys "
      "unchanged" % STAGE183)


# ------------------------------------------------------------------ (9)
# L183 master fold, references: entries 38-45.  The source of truth is the
# stored, verified prior-art digest paper/priorart_terra_20261121.md (each
# item's abstract or author summary was fetched and read there).  Records are
# PARSED from that file -- title, venue and DOI are never typed here -- and
# the draft list and references.bib must both carry them.  Author lists are
# held at the first author by declaration: the digest records nothing more,
# and no citation field may be written from memory.
PRIOR = open(os.path.join(HERE, "priorart_terra_20261121.md")).read()
PREC = {}
for m in re.finditer(r"^(\d+)\. (.+?) \((\d{4})\), \u201c(.+?),\u201d (.+?)\. "
                     r"https://doi\.org/(\S+)", PRIOR, re.M):
    PREC[(m.group(2).split()[0], m.group(3))] = dict(
        title=m.group(4), venue=m.group(5).replace(" preprint", "").split(",")[0],
        doi=m.group(6))
ORDER_C = [("chalfie1985", "Chalfie", "1985"), ("rakowski2013", "Rakowski", "2013"),
           ("fouad2018", "Fouad", "2018"), ("alstott2009", "Alstott", "2009"),
           ("rangaraju2015", "Rangaraju", "2015"), ("laredo2018", "Laredo", "2018"),
           ("zung2025", "Zung", "2025"), ("sturner2025nature", "St\u00fcrner", "2025")]
n_c = 0
if STAGE183 >= 4:
    ck(N == 37 + len(ORDER_C), "the list has %d entries, expected %d" % (N, 37 + len(ORDER_C)))
    for i, (key, sn, yr) in enumerate(ORDER_C):
        n = 38 + i
        rec = PREC.get((sn, yr))
        seg = segs.get(n, "")
        if not ck(rec is not None, "%s %s is not in the verified digest" % (sn, yr)):
            continue
        ck(seg.startswith("%d. %s et al." % (n, sn)), "entry %d is not %s et al." % (n, sn))
        ck(("(%s)" % yr) in seg, "entry %d year not from the digest" % n)
        ck(("doi:" + rec["doi"]) in seg, "entry %d DOI not copied from the digest" % n)
        ck(rec["venue"] in seg, "entry %d venue %r not from the digest" % (n, rec["venue"]))
        ov = len(toks(rec["title"]) & toks(seg)) / max(1, len(toks(rec["title"])))
        ck(ov >= 0.9, "entry %d title does not match the digest (%.2f)" % (n, ov))
        ck(("@article{%s," % key) in BIB and rec["doi"] in BIB and rec["title"] in BIB,
           "bib entry %s missing, or its DOI / title not from the digest" % key)
        ck("%s and others" % sn in BIB, "bib entry %s author not held at first author" % key)
        n_c += 1
    # the two statements the digest corrects must be worded as it words them
    ck("equally sized 50-node lesions" in _ws(PRIOR) and "50 nodes each" in _ws(body),
       "the equal-size lesion detail is not stated as the digest verifies it")
    ck("no mass control" not in _ws(body) and "no size control" not in _ws(body),
       "the draft denies a size control the cited study has")
    # the digest does not say that entry 45 is the journal version of entry 15,
    # so the list may not say it either
    ck("see also entry 15" in _ws(refsec_body)
       and "journal version of entry 15" not in _ws(refsec_body),
       "entry 45 must point at entry 15 without asserting an unverified relation")
    print("(9) entries 38-%d: %d of %d parsed from the verified prior-art digest and "
          "matched in the list and in references.bib (title, venue, year, DOI); "
          "authors held at first author by declaration"
          % (37 + len(ORDER_C), n_c, len(ORDER_C)))
else:
    ck(N == 37, "entries beyond 37 before the fold's related-work stage")
    print("(9) entries 38-45 not yet folded (stage %d); %d digest records parsed"
          % (STAGE183, len(PREC)))

print()
if fails:
    print("L174 VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("L174 VERIFY: ALL GREEN")
