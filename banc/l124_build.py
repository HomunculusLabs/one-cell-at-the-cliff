"""Build l124_run.py from l123_run.py via exact-string transforms.

L124 = B19 rebase of the L123 window arms. Every gain is now STORED-FORM
(re-bisect EXACT; NO fresh bisect arm). (1) docstring splice (opener
guard), (2) wA/wB stored consts, (3) B18->B19 batch rename (count-pinned
AFTER docstring splice) + seed range, (4) absence list += raw_l123,
(5) stored-loop comment + tuple + _st dict extension, (6) DELETE the
fresh cutwA/cutwB bisect loop (indent-anchored whole-block), (7) NEW
C0A-123 forward-chain block after the C0A-122 log, (8) out-dict additions,
(9) output paths l123->l124 (resume path included — L39 direction class),
(10) residual scan + input-direction whitelist + py_compile. Every rep
prints its count; zero/mismatch aborts (drift guard). Anchored on FULL
indentation everywhere (L123 lesson).
"""
import py_compile
import sys

SRC = open("l123_run.py").read()
n_err = 0


def rep(old, new, count=None):
    global SRC, n_err
    c = SRC.count(old)
    if c == 0 or (count is not None and c != count):
        print(f"PATTERN MISMATCH ({c} != {count}): {old[:70]!r}")
        n_err += 1
        return
    SRC = SRC.replace(old, new)
    print(f"ok x{c}: {old[:48]!r}")


# 1. docstring splice (opener guard)
NEW_DOC = '''"""L124 run: cutwA/cutwB batch REBASE on FRESH B19. PREREG
l124/PREREG.md FIRST.

L123 machinery VERBATIM (10 arms, 5-pair pools, graphs, draw order) —
window arms cutwA/cutwB re-rolled on FRESH B19 2301-2316 (asserted absent
from raw_l113 + l115 + l117 + l118 + l119 + l120 + l121 + l122 + l123).
ALL dose/window gains STORED-FORM anchors (re-bisect EXACT; ng endpoints
from l121, window halves from l123); NO fresh bisect arm. C0A-120/121/122
retained + NEW C0A-123 forward chain ({cutk5,cutng19,cutng29,cutwA,cutwB}
vs raw_l123 at 801/901). CPU-only; raw checkpoint BEFORE analysis.
"""'''
assert SRC.startswith('"""L123 run:') and SRC.count('"""L123 run:') == 1, \
    "docstring opener drift"
_doc_end = SRC.index('"""', 3) + 3
SRC = NEW_DOC + SRC[_doc_end:]
print("ok x1: run docstring spliced")

# 2. wA/wB stored consts (anchored on the NG29 const line)
rep('G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)\n',
    'G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)\n'
    'G_CUTWA_STORED = 0.14365819573402408  # l123 fresh gain -> stored-form (C0A-123)\n'
    'G_CUTWB_STORED = 0.14922914385795596  # l123 fresh gain -> stored-form (C0A-123)\n',
    count=1)

# 3. batch rename (docstring already replaced; 8 code sites expected)
rep("B18", "B19", count=8)
rep("B19 = list(range(2201, 2217))       # fresh, absent l113/l115/l117/l118/l119/l120",
    "B19 = list(range(2301, 2317))  # fresh, absent l113..l123 incl raw_l123",
    count=1)

# 4. absence list += raw_l123
rep('''              "l120/raw_l120.npz", "l121/raw_l121.npz",
              "l122/raw_l122.npz"):''',
    '''              "l120/raw_l120.npz", "l121/raw_l121.npz",
              "l122/raw_l122.npz", "l123/raw_l123.npz"):''', count=1)

# 5. stored-loop comment + tuple + _st dict
rep('''# L122 form: ng endpoint gains are STORED-FORM anchors (re-bisect EXACT).
# L123 fresh bisects: cutwA/cutwB only (staircase + band DISCLOSED per
# PREREG — the .14-.16 band is a disclosure, never an abort).
new_stairs = {}
for _a in ("cutng19", "cutng29"):''',
    '''# L124 form: ALL dose/window gains are STORED-FORM anchors (re-bisect
# EXACT): ng endpoints from l121, window halves from l123. Staircase +
# band disclosures retained per PREREG (never an abort).
new_stairs = {}
for _a in ("cutng19", "cutng29", "cutwA", "cutwB"):''', count=1)
rep('''    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED}[_a]''',
    '''    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,
           "cutwA": G_CUTWA_STORED, "cutwB": G_CUTWB_STORED}[_a]''', count=1)

# 6. DELETE the fresh cutwA/cutwB bisect loop (whole block, indent-anchored
#    on its unique `for` line through the log line before rollouts)
rep('''for _a in ("cutwA", "cutwB"):
    lo_d, hi_d = 0.12, 0.18
    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _a), bisect_af_mean(hi_d, _a)
    log(f"{_a} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo_d < AF_T < af_hi_d, f"{_a} bracket fail"
    for it in range(24):
        mid = (lo_d + hi_d) / 2
        if bisect_af_mean(mid, _a) < AF_T:
            lo_d = mid
        else:
            hi_d = mid
    GAIN[_a] = lo_d
    af_d = bisect_af_mean(lo_d, _a)
    new_stairs[_a] = abs(af_d - AF_T)
    _band = " [OUTSIDE PREREG band .14-.16 — DISCLOSED]" \\
        if not (0.14 <= lo_d <= 0.16) else ""
    log(f"g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "
        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")

# ---------------- rollouts ----------------''',
    '''# (L124: the L123 fresh cutwA/cutwB bisect loop is DELETED — both gains
# are stored-form now; the stored loop above re-bisects them EXACT.)

# ---------------- rollouts ----------------''', count=1)

# 7. NEW C0A-123 forward chain (after the C0A-122 log)
rep('''log(f"C0A-122 forward chain vs raw_l122: {'PASS' if c0a122_pass else 'FAIL'} "
    f"(max {c0a122_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")''',
    '''log(f"C0A-122 forward chain vs raw_l122: {'PASS' if c0a122_pass else 'FAIL'} "
    f"(max {c0a122_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")
# C0A-123 (NEW anchor class): forward chain — {cutk5,cutng19,cutng29,
# cutwA,cutwB} at stored seeds vs raw_l123 (l123 ran every arm at all 18
# seeds).
z123c = np.load("l123/raw_l123.npz")
c0a123 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29", "cutwA", "cutwB"):
            c0a123[f"123_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z123c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29", "cutwA", "cutwB"):
        c0a123[f"123_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z123c[f"af_{a}_{s}"]))
c0a123_max = max(c0a123.values())
c0a123_pass = bool(all(v == 0.0 for v in c0a123.values()))
log(f"C0A-123 forward chain vs raw_l123: {'PASS' if c0a123_pass else 'FAIL'} "
    f"(max {c0a123_max:.1e}, {len(C0A120_KEYS)} keys x 5 arms x 2 seeds)")''',
    count=1)

# 8. out-dict additions (anchored, full indentation)
rep('''           c0a122_max=c0a122_max, c0a122_pass=c0a122_pass,''',
    '''           c0a122_max=c0a122_max, c0a122_pass=c0a122_pass,
           c0a123_max=c0a123_max, c0a123_pass=c0a123_pass,
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           g_cutwB_stored_exact=bool(GAIN["cutwB"] == G_CUTWB_STORED),''',
    count=1)
rep('''           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass
                          and c0a121_pass and c0a122_pass))''',
    '''           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass
                          and c0a121_pass and c0a122_pass and c0a123_pass))''',
    count=1)

# 9. output paths l123 -> l124 (resume path FIRST — L39 direction class)
rep('if os.path.exists("l123/raw_partial.npz"):',
    'if os.path.exists("l124/raw_partial.npz"):', count=1)
rep('z = np.load("l123/raw_partial.npz")',
    'z = np.load("l124/raw_partial.npz")', count=1)
rep('np.savez("l123/raw_partial.npz", **store)',
    'np.savez("l124/raw_partial.npz", **store)', count=1)
rep('np.savez_compressed("l123/raw_l123.npz"',
    'np.savez_compressed("l124/raw_l124.npz"', count=1)
rep('log("raw_l123.npz checkpointed BEFORE analysis")',
    'log("raw_l124.npz checkpointed BEFORE analysis")', count=1)
rep('json.dump(out, open("l123/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l124/anchors_run.json", "w"), indent=1)', count=1)

open("l124_run.py", "w").write(SRC)

# ---------------- residual scan + direction check ----------------
bad = []
s = open("l124_run.py").read()
for tok in ("B18", "2201", "2216"):
    if tok in s:
        bad.append(("l124_run.py", "stale token " + tok))
import re
# l123 inputs are LEGITIMATE (static pins + raw_l123 C0A-123 anchor);
# every other l1x path must be an INPUT from the whitelist; the ONLY
# output paths must be l124/*.
OK_IN = {"l107/static.json", "l92/static.json", "l101/static.json",
         "l121/static.json", "l123/static.json", "l113/raw_l113.npz",
         "l115/raw_l115.npz", "l117/raw_l117.npz", "l118/raw_l118.npz",
         "l119/raw_l119.npz", "l120/raw_l120.npz", "l121/raw_l121.npz",
         "l122/raw_l122.npz", "l123/raw_l123.npz"}
for m in re.finditer(r'"(l1\d+/[^"]+)"', s):
    p = m.group(1)
    if p.startswith("l124/"):
        continue
    if p not in OK_IN:
        bad.append(("l124_run.py", "unexpected l-path " + p))
if n_err or bad:
    print("BUILD FAIL:", n_err, bad)
    sys.exit(1)
py_compile.compile("l124_run.py", doraise=True)
print("BUILD OK: l124_run.py compiled; scans clean (verdict built separately)")
