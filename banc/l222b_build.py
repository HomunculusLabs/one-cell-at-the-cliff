"""L222b ADDENDUM BUILD — isolate the SINGLE SYNAPSE.

POST-HOC and declared as such. l222's LOCAL floor removed ~6,951 weak edges
into the motor readout at once, so it cannot say whether the mirror's ONE
direct motor synapse is causally relevant to its percentile. This addendum
deletes exactly that ONE edge and nothing else.

Built as its own generated script from l222_static.py lines 1-906 VERBATIM
(the parent sliced at the end of `floor_leg`, so every result block, the
branch, the predictions and the parent's writer are CUT -- the L213/l221b
pattern), with exactly ONE declared modification: the inherited V_DEGENERATE
escape at lines 432-436 writes into OUT/static.json, and OUT must stay
verbatim (the parent's own tail asserts OUT ends in "/l222"). So that block is
replaced by a strictly stronger halting assert that writes nothing. The result
is a prefix containing ZERO writes, which is what makes it safe to re-run
against the parent's own artifact directory.

Every parent gate re-runs for free.
"""
import hashlib
import os

LAB = "/home/t3rpz/critters/peabrain-lab/banc"
SRC = f"{LAB}/l222_static.py"
PARENT_SHA = "730ac82cb12f4740"
ESC = (432, 436)   # the inherited V_DEGENERATE escape (its only write)
CUT_AT = 906       # the last line of floor_leg's body ("    return L")

whole = open(SRC).read()


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


assert sha(whole) == PARENT_SHA, (sha(whole), PARENT_SHA, "PARENT MOVED (STOP)")
lines = whole.split("\n")
esc_src = "\n".join(lines[ESC[0] - 1:ESC[1]])
assert esc_src.startswith("if SPR >= 1e-6:"), esc_src[:40]
assert "json.dump" in esc_src and "sys.exit" in esc_src, esc_src

p1 = "\n".join(lines[:ESC[0] - 1]) + "\n"
p2 = "\n".join(lines[ESC[1]:CUT_AT]) + "\n"
assert p1 == whole[:len(p1)], "piece 1 is not the literal PREFIX (STOP)"
assert p2 in whole, "piece 2 is not a literal substring (STOP)"
INJECT = (
    '# ===== L222b DECLARED MODIFICATION (replaces l222_static.py lines '
    '432-436) =====\n'
    '# the inherited V_DEGENERATE escape is the prefix\'s ONLY write and it\n'
    '# targets OUT/static.json = the PARENT artifact. A halting assert is\n'
    '# strictly stronger (measured rel spread 4.11e-16) and writes nothing.\n'
    'assert SPR < 1e-6, (SPR, "power iteration did not converge (STOP)")\n')

head = p1 + INJECT + p2
MUST = ["CERT-783", "CERT-L207", "CERT-212", "CERT-FLOORGEN", "CERT-MONOTONE",
        "def build_v783(", "def build_v783_floor(", "def matched_cohort(",
        "def reach_sub(", "def Rstat(", "def floor_leg(", "def leg(",
        "Qa_anatomical", 'OUT = f"{LAB}/l222"']
for m in MUST:
    assert m in head, (m, "prefix lost a gate (STOP)")
# the parent's RESULT / BRANCH / WRITER blocks must all be CUT
CUT = ['o["Qb_global_floors"]', 'o["Qe_local_floors"]', 'o["Qf_beta1_at_f4"]',
       'o["predictions"]', "GAP_4 = GLOB[4]", 'o["primary"] = dict(statistic',
       'o["limitations"]', "FMAX_BOTH", 'log(f"[done]',
       "json.dump", "sys.exit"]
for c in CUT:
    assert c not in head, (c, "a CUT parent block is still present (STOP)")
assert head.rstrip().endswith("return L"), head.rstrip()[-40:]
assert head.count("json.dump") == 0, "the prefix must contain ZERO writes"

tail = open(f"{LAB}/l222b_tail.py").read()
FORBIDDEN = ["systemctl", "sessions/", "serve.py", "bridge.py", "torch.save",
             "import l2", "from l2", "subprocess", "os.remove", "shutil",
             "LANE.md"]
NO_RETRANSCRIBE = ["def build_v783(", "def build_v783_floor(", "def leg(",
                   "def reach_fast(", "def power_iter_fast(", "def Rfast(",
                   "def matched_cohort(", "def floor_leg("]
for n in NO_RETRANSCRIBE:
    assert n not in tail, (n, "addendum RE-TRANSCRIBES parent source (STOP)")
assert "def build_drop(" in tail and "CERT-DROPGEN" in tail

out = head + tail
for f in FORBIDDEN:
    assert f not in out, (f, "FORBIDDEN TOKEN (STOP)")
assert out.count("json.dump") == 1, (out.count("json.dump"), "writes (STOP)")
assert 'open(f"{OUT}/addendum.json", "w")' in out
assert 'open(f"{OUT}/static.json", "w")' not in out, "would clobber the parent"

dst = f"{LAB}/l222b_static.py"
open(dst, "w").write(out)
print(f"[build] prefix lines 1-{CUT_AT} with 432-436 replaced; ZERO writes")
print(f"[build] wrote {dst} ({len(out)} bytes, {out.count(chr(10))} lines)")
print(f"[build] generated sha256 {sha(out)}")
