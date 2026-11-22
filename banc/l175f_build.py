"""Build l175f_run.py as a MECHANICAL derivation of l169b2_run.py.

Edits allowed (PREREG l175f/PREREG.md): fresh batch, output paths, one added
forward-chain anchor block (FC-169B2). Every other byte identical. The script
asserts the diff is exactly the intended edit set before writing.
"""
import hashlib
import os
import re
import sys

SRC = "l169b2_run.py"
DST = "l175f_run.py"

src = open(SRC).read()
print("src sha256", hashlib.sha256(src.encode()).hexdigest()[:16], len(src), "chars")

out = src

# (i) fresh batch B37 = 3701-3716 (n=16, matching B36)
assert "B36 = list(range(3449, 3465))" in out
out = out.replace("B36 = list(range(3449, 3465))", "B37 = list(range(3701, 3717))")
n_b36 = out.count("B36")
out = out.replace("B36", "B37")
print("B36 -> B37 occurrences replaced:", n_b36)

# (ii) output paths -> l175f/
pairs = [('"l169b2/raw_partial.npz"', '"l175f/raw_partial.npz"'),
         ('"l169b2/raw_l169b2.npz"', '"l175f/raw_l175f.npz"'),
         ('"l169b2/anchors_run.json"', '"l175f/anchors_run.json"'),
         ('"raw_l169b2.npz checkpointed BEFORE analysis"',
          '"raw_l175f.npz checkpointed BEFORE analysis"')]
for a, b in pairs:
    assert out.count(a) >= 1, ("missing path token", a)
    out = out.replace(a, b)

# (iii) B37 absence must also scan l169b2's own stored npzs
assert '"l169/raw_partial.npz"]' in out
out = out.replace('"l169/raw_partial.npz"]',
                  '"l169/raw_partial.npz",\n'
                  '          "l169b2/raw_l169b2.npz",\n'
                  '          "l169b2/raw_partial.npz"]')

# (iv) FC-169B2: the card's registered anchor — ALL 12 arms vs l169b2 stored
ANCHOR_MARK = 'log(f"FC-169 (9 arms x {len(C0A150_KEYS)} keys x 2 seeds) vs raw_l169: "\n    f"{\'PASS\' if fc169_pass else \'FAIL\'} (max {fc169_max:.1e})")\n'
assert ANCHOR_MARK in out, "FC-169 log anchor not found"
FC_B2 = '''# ---- FC-169B2 (L175 REGISTERED ANCHOR, PREREG l175f/PREREG.md V2): ALL
# TWELVE arms must be BIT-IDENTICAL to l169b2/raw_l169b2.npz at 801/901.
# This is the card's own forward chain: the f4 substrate, the f4 gains and
# the step loop are inherited verbatim, so any non-zero here is a stream or
# substrate break and the run is VOID (no B37 value may be read).
z169b2c = np.load("l169b2/raw_l169b2.npz")
assert all(f"{_k}_{_a}_801" in z169b2c.files for _k in C0A150_KEYS
           for _a in ARMS), "FC-169B2 coverage miss"
fc169b2 = {}
for s in (801, 901):
    for key in C0A150_KEYS:
        for a in ARMS:
            fc169b2[f"{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z169b2c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ARMS:
        fc169b2[f"af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(z169b2c[f"af_{a}_{s}"]))
fc169b2_max = max(fc169b2.values())
fc169b2_pass = bool(all(v == 0.0 for v in fc169b2.values()))
log(f"FC-169B2 (12 arms x {len(C0A150_KEYS)} keys x 2 seeds) vs raw_l169b2: "
    f"{'PASS' if fc169b2_pass else 'FAIL'} (max {fc169b2_max:.1e})")
# gain identity: the three fresh f4 bisects must land on l169b2's stored gains
_G_F4_STORED = {"f4wA": 0.15051452517509462, "f4ng": 0.16230986118316648,
                "f4tw": 0.15261898636817928}
f4_gain_exact = {k: bool(GAIN[k] == v) for k, v in _G_F4_STORED.items()}
log(f"f4 gain identity vs l169b2 stored: {f4_gain_exact}")
'''
out = out.replace(ANCHOR_MARK, ANCHOR_MARK + FC_B2)

# carry the new anchor results into anchors_run.json
assert "fc169_max=fc169_max, fc169_pass=fc169_pass," in out
out = out.replace("fc169_max=fc169_max, fc169_pass=fc169_pass,",
                  "fc169_max=fc169_max, fc169_pass=fc169_pass,\n"
                  "           fc169b2_max=fc169b2_max, fc169b2_pass=fc169b2_pass,\n"
                  "           f4_gain_exact=f4_gain_exact,")
assert "and nt_pass and fc169_pass and ntf4_pass))" in out
out = out.replace("and nt_pass and fc169_pass and ntf4_pass))",
                  "and nt_pass and fc169_pass and ntf4_pass\n"
                  "                         and fc169b2_pass\n"
                  "                         and all(f4_gain_exact.values())))")

# header note
out = out.replace('"""L169b2 run: pre-posting control (b2), the FLOOR-4 DYNAMIC arm.',
                  '"""L175 run: the FLOOR-4 LEFT-SIDE registered test (fresh batch B37).\n'
                  'MECHANICALLY DERIVED from l169b2_run.py by l175f_build.py — only the\n'
                  'batch, the output paths and the added FC-169B2 anchor differ. PREREG\n'
                  'l175f/PREREG.md was frozen BEFORE this file existed.\n\n'
                  'Lineage docstring of the source follows verbatim.\n\n'
                  'L169b2 run: pre-posting control (b2), the FLOOR-4 DYNAMIC arm.')

# ---- diff audit: every changed line must be in the intended edit set ----
sl, dl = src.splitlines(), out.splitlines()
import difflib
changed = [l for l in difflib.unified_diff(sl, dl, lineterm="", n=0)
           if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
allowed = re.compile(r"B3[67]|l175f|l169b2|FC-169B2|fc169b2|f4_gain_exact|_G_F4_STORED|"
                     r"raw_l175f|ntf4_pass|MECHANICALLY|PREREG|Lineage|batch, the output|"
                     r"^[+-]\s*$|z169b2c|ARMS|store\[|log\(|assert|for |fc169b2_max|"
                     r"raw_partial\.npz|0\.15261898636817928|"
                     r"L169b2 run:|# |'''|\"\"\"")
bad = [c for c in changed if not allowed.search(c)]
print(f"diff lines changed: {len(changed)}; unexplained: {len(bad)}")
for b in bad[:10]:
    print("  UNEXPLAINED:", b)
assert not bad, "unexplained diff line (STOP)"

open(DST, "w").write(out)
print("wrote", DST, len(out), "chars  sha256",
      hashlib.sha256(out.encode()).hexdigest()[:16])
