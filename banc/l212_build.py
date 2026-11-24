"""L212 BUILD — assemble l212_static.py from VERBATIM l207_tail.py slices plus
this card's own head/tail. Refuses to write if any inherited sha moved, if a
slice is not a literal substring of its source, or if the forbidden-token audit
trips. No lab module is ever imported (L175).
"""
import hashlib
import os
import sys

LAB = "/home/t3rpz/critters/peabrain-lab/banc"
SRC = f"{LAB}/l207_tail.py"
# (first_line, last_line, sha256-16, must-contain)
SLICES = [
    (82, 110, "fce1e71189eb1ed7", ["def reach_sub(", "def power_iter_sub("]),
    (199, 241, "340c0432c85c6e7b", ["def Rstat(", "def pct_of(",
                                    "def rankvec(", "def spearman_l("]),
    (338, 346, "f4585bcc52f7ab0a", ["def matched_cohort("]),
]
FORBIDDEN = ["systemctl", "sessions/", "serve.py", "bridge.py", "torch.save",
             "import l1", "from l1", "subprocess", "os.remove", "shutil",
             "LANE.md"]

whole = open(SRC).read()
lines = whole.split("\n")
parts = []
for a, b, want, must in SLICES:
    sl = "\n".join(lines[a - 1:b]) + "\n"
    got = hashlib.sha256(sl.encode()).hexdigest()[:16]
    assert got == want, (a, b, got, want, "INHERITED SHA MOVED (STOP)")
    assert sl in whole, (a, b, "slice is not a literal substring (STOP)")
    for m in must:
        assert m in sl, (a, b, m, "slice lost its function (STOP)")
    parts.append(f"\n# ===== VERBATIM l207_tail.py lines {a}-{b} "
                 f"(sha256-16 {want}) =====\n" + sl)
    print(f"[slice] {a}-{b} sha {got} OK ({len(sl)} bytes)")

head = open(f"{LAB}/l212_head.py").read()
tail = open(f"{LAB}/l212_tail.py").read()
out = head + "".join(parts) + tail
for f in FORBIDDEN:
    assert f not in out, (f, "FORBIDDEN TOKEN in generated script (STOP)")
assert out.count('open(f"{OUT}/static.json", "w")') == 3, "unexpected writes"
assert "proofread_connections_783.feather" in out
dst = f"{LAB}/l212_static.py"
open(dst, "w").write(out)
print(f"[build] wrote {dst} ({len(out)} bytes, {out.count(chr(10))} lines)")
print(f"[build] generated sha256 {hashlib.sha256(out.encode()).hexdigest()[:16]}")
