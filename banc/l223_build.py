"""L223 BUILD — assemble l223_static.py from VERBATIM inherited source.

Inherited, in order:
  * l212_head.py sliced into THREE literal pieces so that two blocks are CUT:
      - line 27 `OUT = f"{LAB}/l212"` -> re-pointed to l223 (writing into a
        PARENT's artifact directory is the worst failure class available here);
      - lines 117-122, the graceful-blocker block, whose `json.dump` writes to
        OUT/static.json.  Replaced by a HALTING assert (strictly stronger).
  * the three l207_tail.py function slices l212 itself inherited (same shas).
  * l212_tail.py lines 1-227 = L212's ENTIRE measurement pipeline, sliced to
    CUT its predictions / limitations / writer block (the L213 pattern).  This
    is what puts CV (motor leg) and CV2 (descending leg) in scope over the
    IDENTICAL cohort COH_U -- PREREG 0a, the reason this card needs no new
    cohort machinery at all.
  * a tiny L223 INJECT defining PARENT_BRANCH + the OUT assert, then
  * l222_tail.py lines 26-88 = CERT-212 VERBATIM (re-use as SOURCE, never
    re-implementation -- the L211 lesson), cut before its `del SUB2, SUB3,
    CV2, CV3` so this card KEEPS the descending leg it needs.
  * l223_tail.py = this card's own measurement.

Refuses to write if any inherited sha moved, if a slice is not a literal
substring of its source, if a cut block survives, if l222_tail.py is not a
literal SUFFIX of l222_static.py, or if the forbidden-token audit trips.
No lab module is ever imported (L175).
"""
import hashlib
import os
import sys

LAB = "/home/t3rpz/critters/peabrain-lab/banc"
HEAD = f"{LAB}/l212_head.py"
PTAIL = f"{LAB}/l212_tail.py"
SRC207 = f"{LAB}/l207_tail.py"
C212 = f"{LAB}/l222_tail.py"

WHOLE = {
    HEAD: "acbaef527a278ae1",
    PTAIL: "f7b533d6c384b943",
    SRC207: "1891ffdc3090b5b0",
    C212: "bafcb3419f661fc9",
}
PARENT_STATIC = f"{LAB}/l212_static.py"
PARENT_STATIC_SHA = "b32c576b5145487e"
L222_STATIC = f"{LAB}/l222_static.py"
L222_STATIC_SHA = "730ac82cb12f4740"

HEAD_SLICES = [
    (1, 26, ["import numpy as np", 'PB = "/home/t3rpz/critters/peabrain"',
             'LAB = "/home/t3rpz/critters/peabrain-lab/banc"']),
    (28, 116, ["BETA_L = 2.0", "CERT-783", "NT_CLASS = {", "assert CAR_783 =="]),
    (123, 241, ["GI_CARRIER = idx_all[CAR_783]", "def build_v783(",
                "proofread_connections_783.feather"]),
]
HEAD_INJECT_1 = (
    '\n# ===== L223 DECLARED MODIFICATION (replaces l212_head.py line 27) =====\n'
    '# the parent wrote to {LAB}/l212; this card must never touch that dir.\n'
    'OUT = f"{LAB}/l223"\n')
HEAD_INJECT_2 = (
    '\n# ===== L223 DECLARED MODIFICATION (replaces l212_head.py lines 117-122)\n'
    "# the parent's graceful-blocker block WRITES into OUT/static.json.\n"
    '# A HALTING assert is strictly stronger and writes nothing.\n'
    'assert CAR_783 in idx_all and MIR_783 in idx_all, (\n'
    '    "L223: a DNp33 match id is absent from the v783 proofread id set "\n'
    '    "(STOP) - this would be a real blocker, not a worked-around one")\n')
HEAD_CUT = ['OUT = f"{LAB}/l212"',
            "a missing id is a valid journaled blocker",
            'o["blocker"]']

TAIL_SLICE = (1, 227, ["def mv_fast(", "def reach_fast(", "def power_iter_fast(",
                       "CERT-MV", "CERT-GATE", "def Rfast(", "def leg(",
                       'o["Q1_primary"] = PRI', 'o["Q2_secondary_descriptive"]',
                       'o["Q3_robust_beta1"] = ROB', "rescale_noop",
                       "CV2 = {g: Rfast(SUB2, g, LAM1)", "COH_U = sorted("])
TAIL_CUT = ['o["predictions"] = P', 'o["limitations"]', 'o["comparators_L207"]',
            'log(f"[done]', 'o["runtime_s"]', 'o["pins"]']

# CERT-212 inherited from l222_tail.py, cut BEFORE its `del SUB2, SUB3, CV2, CV3`
C212_SLICE = (26, 88, ["CERT-212", "def _walk(", 'assert not _bad',
                       "_stp2.st_mtime_ns", 'o["cert_212"]'])
C212_CUT = ["del SUB2", 'OUT.endswith("/l222")', "build_v783_floor",
            "GAP_ARTIFACT_BAR"]

L223_INJECT = (
    '\n# ===== L223 INJECT (3 lines): the two names the inherited CERT-212\n'
    '# slice needs from its parent tail, plus this card\'s OUT guard. =====\n'
    'assert OUT.endswith("/l223") and os.path.isdir(OUT), (OUT, "OUT (STOP)")\n'
    'PARENT_BRANCH = o.get("branch")\n'
    'o["parent_branch_reproduced"] = PARENT_BRANCH\n')

S207_SLICES = [
    (82, 110, "fce1e71189eb1ed7", ["def reach_sub(", "def power_iter_sub("]),
    (199, 241, "340c0432c85c6e7b", ["def Rstat(", "def pct_of(",
                                    "def rankvec(", "def spearman_l("]),
    (338, 346, "f4585bcc52f7ab0a", ["def matched_cohort("]),
]

FORBIDDEN = ["systemctl", "sessions/", "serve.py", "bridge.py", "torch.save",
             "import l1", "from l1", "subprocess", "os.remove", "shutil",
             "LANE.md", 'l212/static.json", "w"', "itertuples"]

NO_RETRANSCRIBE = ["def reach_sub(", "def power_iter_sub(", "def Rstat(",
                   "def pct_of(", "def matched_cohort(", "def mv_fast(",
                   "def mv_slow(", "def reach_fast(", "def power_iter_fast(",
                   "def Rfast(", "def leg(", "def build_v783(",
                   "def rankvec(", "def spearman_l(", "def _walk(", "def _eq("]


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def slice_of(path, a, b):
    whole = open(path).read()
    lines = whole.split("\n")
    sl = "\n".join(lines[a - 1:b]) + "\n"
    assert sl in whole, (path, a, b, "slice is not a literal substring (STOP)")
    return sl


observed = {p: sha(open(p).read()) for p in WHOLE}
for p, want in WHOLE.items():
    print(f"[whole] {os.path.basename(p)} sha256-16 {observed[p]} (pinned {want})")
if os.environ.get("L223_PIN") == "write":
    print("[pin] L223_PIN=write -> printing pins for the builder, NOT building")
    for p in WHOLE:
        print(f'    "{p}": "{observed[p]}",')
    sys.exit(0)
for p, want in WHOLE.items():
    assert observed[p] == want, (p, observed[p], want, "WHOLE SHA MOVED (STOP)")

# ---- PARENT PIN 1: reconstruct l212_static.py from these very files --------
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
print(f"[PARENT PIN 1] GREEN l212_static.py reconstructed byte-for-byte "
      f"(sha {PARENT_STATIC_SHA})")

# ---- PARENT PIN 2: l222_tail.py IS the tail of the script that ran L222 ----
_l222s = open(L222_STATIC).read()
assert sha(_l222s) == L222_STATIC_SHA, (sha(_l222s), "l222_static sha (STOP)")
assert _l222s.endswith(open(C212).read()), \
    "PARENT PIN 2: l222_tail.py is not a literal SUFFIX of l222_static.py (STOP)"
print(f"[PARENT PIN 2] GREEN l222_tail.py is the verbatim suffix of "
      f"l222_static.py (sha {L222_STATIC_SHA}) -> CERT-212 arrives as the "
      f"code that actually ran")

parts = []
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

for a, b, want, must in S207_SLICES:
    sl = slice_of(SRC207, a, b)
    got = sha(sl)
    assert got == want, (a, b, got, want, "INHERITED SHA MOVED (STOP)")
    for m in must:
        assert m in sl, (a, b, m, "slice lost its function (STOP)")
    parts.append(f"\n# ===== VERBATIM l207_tail.py lines {a}-{b} "
                 f"(sha256-16 {want}) =====\n" + sl)
    print(f"[slice] l207_tail {a}-{b} sha {got} OK ({len(sl)} bytes)")

a, b, must = TAIL_SLICE
pt = slice_of(PTAIL, a, b)
for m in must:
    assert m in pt, (m, "parent tail slice lost content (STOP)")
for c in TAIL_CUT:
    assert c not in pt, (c, "parent tail slice still contains its writer (STOP)")
assert pt.count("json.dump") == 1, (pt.count("json.dump"), "parent json.dump")
parts.append(f"\n# ===== VERBATIM l212_tail.py lines {a}-{b} (sha {sha(pt)}) "
             f"= L212's WHOLE measurement pipeline, writer CUT =====\n" + pt)
print(f"[slice] l212_tail {a}-{b} sha {sha(pt)} OK ({len(pt)} bytes)")

parts.append(L223_INJECT)

a, b, must = C212_SLICE
ct = slice_of(C212, a, b)
for m in must:
    assert m in ct, (m, "CERT-212 slice lost content (STOP)")
for c in C212_CUT:
    assert c not in ct, (c, "CERT-212 slice reaches past its cut (STOP)")
assert "json.dump" not in ct, "CERT-212 slice must contain NO write (STOP)"
parts.append(f"\n# ===== VERBATIM l222_tail.py lines {a}-{b} (sha {sha(ct)}) "
             f"= CERT-212, inherited as SOURCE (L211) =====\n" + ct)
print(f"[slice] l222_tail {a}-{b} sha {sha(ct)} OK ({len(ct)} bytes)")

tail = open(f"{LAB}/l223_tail.py").read()
for n in NO_RETRANSCRIBE:
    assert n not in tail, (n, "L223 tail RE-TRANSCRIBES inherited source (STOP)")
assert "CERT-PAIR" in tail and "CERT-RANK" in tail and "Q223_0_rho_first" in tail

out = "".join(parts) + tail
for f in FORBIDDEN:
    assert f not in out, (f, "FORBIDDEN TOKEN in generated script (STOP)")
for c in HEAD_CUT:
    assert c not in out, (c, "a CUT head block is still present (STOP)")
assert out.count('open(f"{OUT}/static.json", "w")') == 2, "unexpected writes"
assert out.count("json.dump") == 2, (out.count("json.dump"), "json.dump count")
assert 'OUT = f"{LAB}/l223"' in out
assert "proofread_connections_783.feather" in out
assert out.count('LAB = "/home/t3rpz/critters/peabrain-lab/banc"') == 1

dst = f"{LAB}/l223_static.py"
open(dst, "w").write(out)
print(f"[build] wrote {dst} ({len(out)} bytes, {out.count(chr(10))} lines)")
print(f"[build] generated sha256 {sha(out)}")
