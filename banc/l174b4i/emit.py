#!/usr/bin/env python3
"""L174 stage (b4-i) — §4 Limitations: bullets to prose, plus the seven
over-length sentences the conversion drags into prose.

Inherited from l174b3biii/emit.py (the (b3b) machinery) with three changes:
  * the span is §4;
  * NEW T7 sentence-split instrument — seven declared (old, new) pairs applied
    to the joined paragraph text before reflow, each proven CONTENT-PRESERVING
    (the alphanumeric word sequence with the declared connective set CONN
    removed must be IDENTICAL before and after, so no number, citation key or
    content word can move; punctuation and capitalization are the only free
    edits, plus insert/delete of CONN members, which are reported per split);
  * a SECOND declared exception class for verifier literals: literals that
    contain the BULLET MARKER itself ('- DATA FLOOR:'), not merely the old
    bullet indentation. Those two are l149 SLICE LOCATORS; they are re-pointed
    at the prose form anchored to a line start (equally strong, not loosened).

Format-only by construction and by gate (PREREG T1): the numeric-token and
citation-key multisets of the edited span are IDENTICAL before and after.
One-shot: refuses to run twice.
"""
import json, os, re, sys

PAPER = "/home/t3rpz/critters/peabrain-lab/paper"
OUT = "/home/t3rpz/critters/peabrain-lab/banc/l174b4i"
DRAFT = os.path.join(PAPER, "DRAFT.md")

START, END = "## 4. Limitations", "## 5. Data & code"

span_pre = open(os.path.join(OUT, "span_pre.txt")).read()
draft = open(DRAFT).read()
i = draft.index(START)
j = draft.index(END)
live = draft[i:j]
assert live == span_pre, ("T4/CERT-3: live span differs from the freeze — "
                         "emit.py refuses to run (already spliced?)")

# --------------------------------------------------------------------------
# The rewrite map. Key = the bullet's exact opener line (dash included).
# new=None  -> DEDASH: the opener already reads as a paragraph lead, so the
#              parser strips '- ' and nothing is retyped. Two of the eight
#              are `LABEL: clause` leads, which §2.7 and §2.8 already use as
#              house style (tick-210 finding), so they are NOT re-authored.
# new=[...] -> re-authored opener (the two true fragments: a bare noun phrase
#              and a verbless 'with ...' clause).
# --------------------------------------------------------------------------
MAP = {
 "- Rate fidelity: no spikes, no per-cell kinetics; the claim is about the":
   dict(new=None, eat=0),
 "- Frequency claims are BAND-RELATIVE, and the sub-band line is":
   dict(new=None, eat=0),
 "- Readout is simulated motor-pool structure duty, not behavior or EMG.":
   dict(new=None, eat=0),
 "- Single specimen per connectome (BANC v626 one female; MaleCNS one male);":
   dict(new=["There is a single specimen per connectome (BANC v626 one female;",
             "MaleCNS one male);"], eat=0),
 "- OPERATING-POINT PROXIMITY, with a convergent disclosure from the":
   dict(new=["OPERATING-POINT PROXIMITY carries a convergent disclosure from the"],
        eat=0),
 "- The transition interior is gain-regime-dependent (2.5) — we report the":
   dict(new=None, eat=0),
 "- UNIT OF INFERENCE: every interval in this paper is over NOISE SEEDS of":
   dict(new=None, eat=0),
 "- Arm depth is unequal by construction: an arm's canonical count unions":
   dict(new=None, eat=0),
 "- DATA FLOOR: the BANC v626 connections release carries an IMPLICIT":
   dict(new=None, eat=0),
 "- Wet-lab predictions are NOT derived here.":
   dict(new=None, eat=0),
}

# --------------------------------------------------------------------------
# T7: the seven sentence splits. Each entry is (old, new). Applied to the
# JOINED paragraph text, each must match EXACTLY ONCE across the whole span.
# CONN is the closed set of function words a split may insert or drop.
# --------------------------------------------------------------------------
CONN = {"and", "while", "so", "therefore"}
SPLITS = [
 # 107 words -> 3 sentences
 ("n = 16) and the registered R-side cliff does NOT transfer",
  "n = 16). The registered R-side cliff does NOT transfer"),
 ("cutwA PARTIAL 3/16 .371), and the f4ng-vs-f4tw XOR leg is flat",
  "cutwA PARTIAL 3/16 .371). The f4ng-vs-f4tw XOR leg is flat"),
 # 77 words -> 3 sentences
 ("quantifies the pattern: in the l65-baseline arm",
  "quantifies the pattern. In the l65-baseline arm"),
 ("but a stimulus-locked one (§2.8) — while the intact closure is sub-band",
  "but a stimulus-locked one (§2.8). The intact closure is sub-band"),
 # 73 words -> 3 sentences
 ("is not antagonist-clock-wide: the mm/xm aggregates carry it",
  "is not antagonist-clock-wide. The mm/xm aggregates carry it"),
 ("strongest members 36/36), while the Ti pools stay",
  "strongest members 36/36). The Ti pools stay"),
 # 68 words -> 2 sentences
 ("heavy-cohort Jaccard .9231 — while the TWIN selection is "
  "floor-3-contingent (twin rank 26 → 33, adjacency does not port): the "
  "identity claim",
  "heavy-cohort Jaccard .9231. The TWIN selection is "
  "floor-3-contingent (twin rank 26 → 33, adjacency does not port), so the "
  "identity claim"),
 # 66 words -> 2 sentences
 ("rather than weight: in that preregistered screen",
  "rather than weight. In that preregistered screen"),
 ("thresholds of 10–15, and the stated cause is measurement",
  "thresholds of 10–15. The stated cause is measurement"),
 # 65 words -> 2 sentences
 ("[l169b2.lat_descriptive]; a registered left-side test is queued",
  "[l169b2.lat_descriptive]. A registered left-side test is queued"),
 # 65 words (the DATA FLOOR opener block) -> 2 sentences
 ("[l146.release] — so a single-synapse sensitivity critique has no purchase",
  "[l146.release]. A single-synapse sensitivity critique therefore has no "
  "purchase"),
]

BRE = re.compile(r"^(\s*)([-*]) (\S.*)$")
lines = span_pre.split("\n")

# ---- parse blocks ---------------------------------------------------------
def nxt_nonblank(k):
    while k < len(lines) and lines[k].strip() == "":
        k += 1
    return k

blocks, k = [], 0
while k < len(lines):
    m = BRE.match(lines[k])
    if not m:
        blocks.append(("text", [lines[k]]))
        k += 1
        continue
    body = []
    e = k + 1
    while e < len(lines):
        ln = lines[e]
        if ln.strip() == "":
            nb = nxt_nonblank(e)
            if (nb < len(lines) and lines[nb].startswith("  ")
                    and not BRE.match(lines[nb])):
                body.extend(lines[e:nb])
                e = nb
                continue
            break
        if BRE.match(ln) or not ln.startswith(" "):
            break
        body.append(ln)
        e += 1
    blocks.append(("bullet", [lines[k]] + body))
    k = e

bullets = [b for t, b in blocks if t == "bullet"]
assert len(bullets) == 10, "expected 10 bullet blocks, found %d" % len(bullets)
seen = {}
for b in bullets:
    op = b[0]
    assert op in MAP, "unmapped bullet opener: %r" % op[:72]
    seen[op] = seen.get(op, 0) + 1
for op, c in seen.items():
    assert c == 1, "opener matched %d blocks (must be 1): %r" % (c, op[:60])
assert set(seen) == set(MAP), "unused map entries: %r" % (set(MAP) - set(seen))

# ---- literal-aware reflow (tick-208 instrument) ---------------------------
WRAP = 78
_LITS = sorted(json.load(open(os.path.join(OUT, "literals.json")))["literals"],
               key=len, reverse=True)
_PROT = [re.sub(r"\s+", " ", s) for s in _LITS if len(re.sub(r"\s+", " ", s)) > 3]

def reflow(text):
    t = re.sub(r"\s+", " ", text).strip()
    if not t:
        return []
    guard = [False] * len(t)
    for p in _PROT:
        start = 0
        while True:
            k2 = t.find(p, start)
            if k2 < 0:
                break
            for q in range(k2, k2 + len(p)):
                guard[q] = True
            start = k2 + 1
    breaks = [q for q, ch in enumerate(t) if ch == " " and not guard[q]]
    out_lines, line_start = [], 0
    while line_start < len(t):
        if len(t) - line_start <= WRAP:
            out_lines.append(t[line_start:])
            break
        cand = [b for b in breaks if line_start < b <= line_start + WRAP]
        if not cand:
            nx = [b for b in breaks if b > line_start + WRAP]
            if not nx:
                out_lines.append(t[line_start:])
                break
            b = nx[0]
        else:
            b = cand[-1]
        out_lines.append(t[line_start:b])
        line_start = b + 1
    return out_lines

# ---- build the new span ---------------------------------------------------
def split_chunks(body_lines):
    """body -> list of ('para', text) / ('tbl', rows), blank-line separated."""
    chunks, cur = [], []
    for ln in body_lines + [""]:
        if ln.strip() == "":
            if cur:
                if all(c.lstrip().startswith("|") for c in cur):
                    chunks.append(("tbl", [c.strip() for c in cur]))
                else:
                    chunks.append(("para", " ".join(c.strip() for c in cur)))
                cur = []
            continue
        cur.append(ln)
    return chunks

units, join_prev = [], False
for bi, (kind, body) in enumerate(blocks):
    if kind == "text":
        nxt_is_bullet = (bi + 1 < len(blocks) and blocks[bi + 1][0] == "bullet")
        if join_prev and body[0].strip() == "" and nxt_is_bullet:
            continue
        units.append(("raw", body[0]))
        join_prev = False
        continue
    spec = MAP[body[0]]
    rest = body[1 + spec["eat"]:]
    opener = [body[0][2:].rstrip()] if spec["new"] is None else spec["new"]
    chunks = split_chunks(rest)
    if chunks and chunks[0][0] == "para":
        chunks[0] = ("para", " ".join(opener) + " " + chunks[0][1])
    else:
        chunks = [("para", " ".join(opener))] + chunks
    for ci, (ck, cv) in enumerate(chunks):
        if ci == 0 and join_prev and units and units[-1][0] == "para":
            assert ck == "para"
            units[-1] = ("para", units[-1][1] + " " + cv)
        else:
            units.append((ck, cv))
    join_prev = bool(spec.get("join"))

# ---- T7: apply the declared sentence splits -------------------------------
norm = lambda s: re.sub(r"\s+", " ", s)
WORD = re.compile(r"[0-9A-Za-z][0-9A-Za-z._/%+-]*")
# a token's TRAILING sentence punctuation is not part of the word: '.' is the
# edit this instrument is allowed to make, so strip it on both sides before
# comparing (interior dots survive: 'l169b2.lat_descriptive', '.100').
tok = lambda w: w.lower().rstrip(".,;:")
def content_seq(t):
    return [tok(w) for w in WORD.findall(norm(t)) if tok(w) not in CONN]
NUMre = re.compile(r"[-+−]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|×)?")
CITre = re.compile(r"\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]")
# PREREG ADDENDUM 2: the numeric regex swallows a TRAILING COMMA (it has to,
# for thousands separators like 2,676,592), so a clause boundary that turns
# '10-15, and' into '10-15. The' reads as a CHANGED numeric token. A trailing
# comma is punctuation, which is exactly what T7 is allowed to edit, so every
# numeric multiset in this stage is compared with trailing commas stripped;
# the DIGITS of every token are still compared exactly.
numset = lambda t: sorted(x.rstrip(",") for x in NUMre.findall(t))

split_report = []
for old, new in SPLITS:
    hits = sum(norm(v).count(norm(old)) for kk, v in units if kk == "para")
    assert hits == 1, ("T7(a): split pattern matched %d times (must be 1): %r"
                       % (hits, old[:70]))
    # (b) local number / citation-key multiset identity
    assert numset(old) == numset(new), \
        ("T7(b): numeric multiset changed inside a split: %r" % old[:60])
    assert sorted(CITre.findall(old)) == sorted(CITre.findall(new)), \
        ("T7(b): citation-key multiset changed inside a split: %r" % old[:60])
    # (c) content-word sequence identity (nothing deleted, added or reordered
    #     outside CONN)
    co, cn = content_seq(old), content_seq(new)
    assert co == cn, ("T7(c): content sequence changed inside a split.\n old=%r\n new=%r"
                      % (co, cn))
    wo = [w.lower() for w in WORD.findall(norm(old))]
    wn = [w.lower() for w in WORD.findall(norm(new))]
    dropped = [w for w in wo if w in CONN]
    added = [w for w in wn if w in CONN]
    # diff of the CONN multisets, reported
    from collections import Counter
    dd = Counter(dropped) - Counter(added)
    aa = Counter(added) - Counter(dropped)
    split_report.append(dict(old=old[:72], conn_removed=sorted(dd.elements()),
                             conn_inserted=sorted(aa.elements())))
    for kk in range(len(units)):
        if units[kk][0] == "para" and norm(old) in norm(units[kk][1]):
            units[kk] = ("para", norm(units[kk][1]).replace(norm(old), norm(new)))
            break

out = []
for ui, (kind, val) in enumerate(units):
    if kind == "raw":
        out.append(val)
        continue
    if out and out[-1].strip() != "":
        out.append("")
    out.extend(reflow(val) if kind == "para" else val)
    nxt = units[ui + 1] if ui + 1 < len(units) else None
    if nxt and (nxt[0] != "raw" or nxt[1].strip() != ""):
        out.append("")
new_span = "\n".join(out)

# ---- gates ----------------------------------------------------------------
BUL = re.compile(r"^\s*[-*]\s+\S", re.M)

n_old, n_new = numset(span_pre), numset(new_span)
c_old, c_new = sorted(CITre.findall(span_pre)), sorted(CITre.findall(new_span))
assert n_old == n_new, ("T1 BREACH (branch B2_tokens_moved): numeric multiset "
                        "changed. only-old=%r only-new=%r"
                        % (sorted(set(n_old) - set(n_new)), sorted(set(n_new) - set(n_old))))
assert c_old == c_new, ("T1 BREACH: citation-key multiset changed. %r / %r"
                        % (sorted(set(c_old) - set(c_new)), sorted(set(c_new) - set(c_old))))
assert len(BUL.findall(new_span)) == 0, (
    "bullet census must fall to 0, found %d" % len(BUL.findall(new_span)))

LIT = json.load(open(os.path.join(OUT, "literals.json")))["literals"]
# PREREG ADDENDUM 1-a: three bullet-internal literals carry the OLD BULLET
# INDENTATION inside their own line break and cannot survive de-indentation;
# their l149 loops are made WRAP-INSENSITIVE (claim text unchanged).
WRAP_EXEMPT = ["fully RE-DERIVED, not\n  frozen",
               "re-ordering rather than\n  turnover",
               "the unit of inference\n  is the simulation realization"]
# PREREG ADDENDUM 1-b (NEW exception class this stage): two literals contain
# the BULLET MARKER itself and are used as l149 SLICE LOCATORS. They are
# re-pointed at the prose form anchored to a LINE START — equally strong.
MARKER_EXEMPT = ["- DATA FLOOR:", "- Wet-lab predictions"]
missing, exempt_ok, marker_ok = [], [], []
for s in LIT:
    if s in new_span:
        continue
    if s in WRAP_EXEMPT:
        assert norm(s) in norm(new_span), "declared wrap-fragile literal lost: %r" % s
        exempt_ok.append(s)
    elif s in MARKER_EXEMPT:
        assert re.search(r"(?m)^" + re.escape(s[2:]), new_span), \
            "declared marker literal lost its prose form: %r" % s
        marker_ok.append(s)
    else:
        missing.append(s)
assert not missing, ("branch B3_literal_lost: %d literal(s) not verbatim: %r"
                     % (len(missing), [m[:60] for m in missing]))
assert sorted(exempt_ok) == sorted(WRAP_EXEMPT), (
    "the wrap exemption set must be EXACTLY the three declared: used %r" % sorted(exempt_ok))
assert sorted(marker_ok) == sorted(MARKER_EXEMPT), (
    "the marker exemption set must be EXACTLY the two declared: used %r" % sorted(marker_ok))

# T5/T7: no sentence over 60 words. The splitter PROTECTS abbreviations so an
# abbreviation's false split cannot satisfy the gate (new this stage).
ABBR = [("Fig.", "Fig\x00"), ("e.g.", "e\x00g\x00"), ("i.e.", "i\x00e\x00"),
        ("cf.", "cf\x00"), ("vs.", "vs\x00"), ("et al.", "et al\x00")]
def sentences(t):
    t = norm(t)
    for a, b in ABBR:
        t = t.replace(a, b)
    return [x.replace("\x00", ".") for x in re.split(r"(?<=[.!?])\s+", t)
            if x.strip()]
sents = sentences(new_span)
top = sorted(((len(x.split()), x[:70]) for x in sents), reverse=True)[:4]
longest = top[0][0]
assert longest <= 60, "T7: a sentence of %d words survives: %r" % top[0]

vis = lambda s: len(re.sub(r"\s", "", s))
rep = dict(
  chars_pre=len(span_pre), chars_post=len(new_span),
  char_delta=len(new_span) - len(span_pre),
  char_delta_pct=round(100.0 * (len(new_span) - len(span_pre)) / len(span_pre), 2),
  visible_chars_pre=vis(span_pre), visible_chars_post=vis(new_span),
  visible_char_delta=vis(new_span) - vis(span_pre),
  bullets_pre=len(BUL.findall(span_pre)), bullets_post=len(BUL.findall(new_span)),
  numeric_tokens=len(n_new), numeric_multiset_identical=(n_old == n_new),
  citation_tokens=len(c_new), citation_multiset_identical=(c_old == c_new),
  literals_checked=len(LIT),
  literals_verbatim=len(LIT) - len(exempt_ok) - len(marker_ok),
  literals_wrap_exempt=sorted(exempt_ok),
  literals_marker_exempt=sorted(marker_ok),
  dedash_blocks=sum(1 for v in MAP.values() if v["new"] is None),
  reauthored_blocks=sum(1 for v in MAP.values() if v["new"] is not None),
  sentence_splits=len(SPLITS),
  conn_words_inserted=sum(len(r["conn_inserted"]) for r in split_report),
  conn_words_removed=sum(len(r["conn_removed"]) for r in split_report),
  split_report=split_report,
  sentences_over_60w_pre=len([1 for s in sentences(span_pre)
                              if len(s.split()) > 60]),
  longest_sentence_words=longest, top_sentences=top,
  paragraphs=len([p for p in new_span.split("\n\n") if p.strip()]),
)
json.dump(rep, open(os.path.join(OUT, "emit_report.json"), "w"), indent=1)
for k2, v in rep.items():
    print("%-32s %s" % (k2, v))

if "--apply" not in sys.argv:
    open(os.path.join(OUT, "span_post_preview.txt"), "w").write(new_span)
    print("\nDRY RUN — preview written, draft untouched. Re-run with --apply.")
    sys.exit(0)

open(os.path.join(OUT, "span_post.txt"), "w").write(new_span)
open(DRAFT, "w").write(draft[:i] + new_span + draft[j:])
print("\nSPLICED: §4 bullets -> prose + 11 sentence splits (single-block "
      "substitution).")
