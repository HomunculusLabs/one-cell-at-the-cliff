"""L222 BUILD — assemble l222_static.py from VERBATIM inherited source:

  * l212_head.py sliced into THREE literal pieces so that two blocks are CUT:
      - line 27 `OUT = f"{LAB}/l212"`  -> re-pointed to l222 (a write to the
        PARENT's artifact directory is the worst failure class available here);
      - lines 117-122, the graceful-blocker block, whose `json.dump` writes to
        OUT/static.json. Replaced by a HALTING assert (strictly stronger).
    Everything else arrives byte-for-byte, so CERT-783 and CERT-L207 re-run.
  * the three l207_tail.py function slices l212 itself inherited (same shas).
  * l212_tail.py lines 1-227 = L212's ENTIRE measurement pipeline (SUB build,
    CERT-MV, reach_fast / power_iter_fast, CERT-GATE, lam1, the rescale NO-OP,
    Rfast, Q1 primary + cohorts, the V_AVOIDS branch, Q2 secondary, Q3 beta1),
    sliced to CUT its predictions / limitations / writer block (the L213
    pattern) so every one of those gates re-runs for free and CERT-212 can
    compare MY rebuild against the stored table.

Refuses to write if any inherited sha moved, if a slice is not a literal
substring of its source, if a cut block is still present, or if the
forbidden-token audit trips. No lab module is ever imported (L175).
"""
import hashlib
import os
import sys

LAB = "/home/t3rpz/critters/peabrain-lab/banc"
HEAD = f"{LAB}/l212_head.py"
PTAIL = f"{LAB}/l212_tail.py"
SRC207 = f"{LAB}/l207_tail.py"

# whole-file pins: the two parent sources must be exactly what L212 ran
WHOLE = {
    HEAD: "acbaef527a278ae1",
    PTAIL: "f7b533d6c384b943",
    SRC207: "1891ffdc3090b5b0",
}
# PARENT PIN: proof that those three files ARE the code that produced
# l212/static.json -- their l212_build.py concatenation must reconstruct
# l212_static.py byte-for-byte.
PARENT_STATIC = f"{LAB}/l212_static.py"
PARENT_STATIC_SHA = "b32c576b5145487e"

HEAD_SLICES = [
    (1, 26, ["import numpy as np", 'PB = "/home/t3rpz/critters/peabrain"',
             'LAB = "/home/t3rpz/critters/peabrain-lab/banc"']),
    (28, 116, ["BETA_L = 2.0", "CERT-783", "NT_CLASS = {", "assert CAR_783 =="]),
    (123, 241, ["GI_CARRIER = idx_all[CAR_783]", "def build_v783(",
                "proofread_connections_783.feather"]),
]
HEAD_INJECT_1 = (
    '\n# ===== L222 DECLARED MODIFICATION (replaces l212_head.py line 27) =====\n'
    '# the parent wrote to {LAB}/l212; this card must never touch that dir.\n'
    'OUT = f"{LAB}/l222"\n')
HEAD_INJECT_2 = (
    '\n# ===== L222 DECLARED MODIFICATION (replaces l212_head.py lines 117-122)\n'
    '# the parent\'s graceful-blocker block WRITES into OUT/static.json.\n'
    '# A HALTING assert is strictly stronger and writes nothing.\n'
    'assert CAR_783 in idx_all and MIR_783 in idx_all, (\n'
    '    "L222: a DNp33 match id is absent from the v783 proofread id set "\n'
    '    "(STOP) - this would be a real blocker, not a worked-around one")\n')
HEAD_CUT = [
    'OUT = f"{LAB}/l212"',
    "a missing id is a valid journaled blocker",
    'o["blocker"]',
]

TAIL_SLICE = (1, 227, ["def mv_fast(", "def reach_fast(", "def power_iter_fast(",
                       "CERT-MV", "CERT-GATE", "def Rfast(", "def leg(",
                       'o["Q1_primary"] = PRI', 'o["Q2_secondary_descriptive"]',
                       'o["Q3_robust_beta1"] = ROB', "rescale_noop"])
TAIL_CUT = ['o["predictions"] = P', 'o["limitations"]', 'o["comparators_L207"]',
            'log(f"[done]', 'o["runtime_s"]', 'o["pins"]']

S207_SLICES = [
    (82, 110, "fce1e71189eb1ed7", ["def reach_sub(", "def power_iter_sub("]),
    (199, 241, "340c0432c85c6e7b", ["def Rstat(", "def pct_of(",
                                    "def rankvec(", "def spearman_l("]),
    (338, 346, "f4585bcc52f7ab0a", ["def matched_cohort("]),
]

FORBIDDEN = ["systemctl", "sessions/", "serve.py", "bridge.py", "torch.save",
             "import l1", "from l1", "subprocess", "os.remove", "shutil",
             "LANE.md", "l212/static.json\", \"w\"", "itertuples"]

# the L222 tail must not RE-TRANSCRIBE an inherited function body
NO_RETRANSCRIBE = ["def reach_sub(", "def power_iter_sub(", "def Rstat(",
                   "def pct_of(", "def matched_cohort(", "def mv_fast(",
                   "def mv_slow(", "def reach_fast(", "def power_iter_fast(",
                   "def Rfast(", "def leg(", "def build_v783("]


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def slice_of(path, a, b):
    whole = open(path).read()
    lines = whole.split("\n")
    sl = "\n".join(lines[a - 1:b]) + "\n"
    assert sl in whole, (path, a, b, "slice is not a literal substring (STOP)")
    return sl


# ---- whole-file pins (print-then-verify so a legitimate first run can pin) --
observed = {p: sha(open(p).read()) for p in WHOLE}
for p, want in WHOLE.items():
    print(f"[whole] {os.path.basename(p)} sha256-16 {observed[p]} (pinned {want})")
if os.environ.get("L222_PIN") == "write":
    print("[pin] L222_PIN=write -> printing pins for the builder, NOT building")
    for p in WHOLE:
        print(f'    "{p}": "{observed[p]}",')
    sys.exit(0)
for p, want in WHOLE.items():
    assert observed[p] == want, (p, observed[p], want, "WHOLE SHA MOVED (STOP)")

# ---- PARENT PIN (halting): reconstruct l212_static.py from these very files -
_w207 = open(SRC207).read()
_l207 = _w207.split("\n")
_rp = []
for a, b, want, _m in S207_SLICES:
    _sl = "\n".join(_l207[a - 1:b]) + "\n"
    assert sha(_sl) == want, (a, b, "parent-pin slice sha (STOP)")
    _rp.append(f"\n# ===== VERBATIM l207_tail.py lines {a}-{b} "
               f"(sha256-16 {want}) =====\n" + _sl)
_recon = open(HEAD).read() + "".join(_rp) + open(PTAIL).read()
_cur = open(PARENT_STATIC).read()
assert _recon == _cur, "PARENT PIN: reconstruction != l212_static.py (STOP)"
assert sha(_cur) == PARENT_STATIC_SHA, (sha(_cur), "parent static sha (STOP)")
print(f"[PARENT PIN] GREEN l212_static.py reconstructed byte-for-byte from "
      f"these three sources (sha {PARENT_STATIC_SHA})")

parts = []
# head piece 1 + inject + head piece 2 + inject + head piece 3
h1 = slice_of(HEAD, *HEAD_SLICES[0][:2])
for m in HEAD_SLICES[0][2]:
    assert m in h1, (m, "head slice 1 lost content (STOP)")
parts.append(f"# ===== VERBATIM l212_head.py lines 1-26 (sha {sha(h1)}) =====\n" + h1)
parts.append(HEAD_INJECT_1)
h2 = slice_of(HEAD, *HEAD_SLICES[1][:2])
for m in HEAD_SLICES[1][2]:
    assert m in h2, (m, "head slice 2 lost content (STOP)")
parts.append(f"\n# ===== VERBATIM l212_head.py lines 28-116 (sha {sha(h2)}) =====\n" + h2)
parts.append(HEAD_INJECT_2)
h3 = slice_of(HEAD, *HEAD_SLICES[2][:2])
for m in HEAD_SLICES[2][2]:
    assert m in h3, (m, "head slice 3 lost content (STOP)")
parts.append(f"\n# ===== VERBATIM l212_head.py lines 123-241 (sha {sha(h3)}) =====\n" + h3)
print(f"[head] slices sha {sha(h1)} / {sha(h2)} / {sha(h3)}")

# the three l207_tail function slices (the pins L212 itself asserted)
for a, b, want, must in S207_SLICES:
    sl = slice_of(SRC207, a, b)
    got = sha(sl)
    assert got == want, (a, b, got, want, "INHERITED SHA MOVED (STOP)")
    for m in must:
        assert m in sl, (a, b, m, "slice lost its function (STOP)")
    parts.append(f"\n# ===== VERBATIM l207_tail.py lines {a}-{b} "
                 f"(sha256-16 {want}) =====\n" + sl)
    print(f"[slice] l207_tail {a}-{b} sha {got} OK ({len(sl)} bytes)")

# L212's whole measurement pipeline, sliced to CUT its writer block
a, b, must = TAIL_SLICE
pt = slice_of(PTAIL, a, b)
for m in must:
    assert m in pt, (m, "parent tail slice lost content (STOP)")
for c in TAIL_CUT:
    assert c not in pt, (c, "parent tail slice still contains its writer (STOP)")
assert pt.count("json.dump") == 1, (pt.count("json.dump"),
                                    "parent slice json.dump count (STOP)")
parts.append(f"\n# ===== VERBATIM l212_tail.py lines {a}-{b} (sha {sha(pt)}) "
             f"= L212's WHOLE measurement pipeline, writer CUT =====\n" + pt)
print(f"[slice] l212_tail {a}-{b} sha {sha(pt)} OK ({len(pt)} bytes)")

tail = open(f"{LAB}/l222_tail.py").read()
for n in NO_RETRANSCRIBE:
    assert n not in tail, (n, "L222 tail RE-TRANSCRIBES inherited source (STOP)")
assert "def build_v783_floor(" in tail and "CERT-212" in tail

out = "".join(parts) + tail
for f in FORBIDDEN:
    assert f not in out, (f, "FORBIDDEN TOKEN in generated script (STOP)")
for c in HEAD_CUT:
    assert c not in out, (c, "a CUT head block is still present (STOP)")
# exactly two writes: the inherited V_DEGENERATE escape + this card's writer,
# and both now point at l222 because OUT was re-pointed.
assert out.count('open(f"{OUT}/static.json", "w")') == 2, "unexpected writes"
assert out.count("json.dump") == 2, (out.count("json.dump"), "json.dump count")
assert 'OUT = f"{LAB}/l222"' in out
assert "proofread_connections_783.feather" in out
assert out.count('LAB = "/home/t3rpz/critters/peabrain-lab/banc"') == 1

dst = f"{LAB}/l222_static.py"
open(dst, "w").write(out)
print(f"[build] wrote {dst} ({len(out)} bytes, {out.count(chr(10))} lines)")
print(f"[build] generated sha256 {sha(out)}")
