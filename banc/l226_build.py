"""Build l226_run.py as a MECHANICAL derivation of l175f_run.py.

PREREG l226/PREREG.md was frozen BEFORE this file existed.

Edits allowed (and ONLY these):
 (i)   ARMS -> the five registered arms (the card's cost slice)
 (ii)  fresh batch B38 = 3801-3816, output paths -> l226/
 (iii) B38 absence scan extended to l175f's own npzs (L157)
 (iv)  THREE EXCISIONS, each one solely because it reads an arm this card
       does not roll out: the in-rollout `paf` block (wAgN/n25gW),
       the C0A-150 / FC-144 / FC-145 / FC-169 anchor block (full, b65,
       silW, eMot*, wAgN, n25gW), and the C0-NT swap + P-af direction
       block (wAgN/n25gW).
 (v)   the final `out = dict(...)` + json.dump + log block REWRITTEN to
       drop the excised fields and add the CERT-SUBSET halting gate.

Every other byte identical. The builder asserts each excision is a literal
unique slice with the expected first/last line, and audits the difflib diff
so no unexplained line can land in the generated file.
"""
import difflib
import hashlib
import re

SRC = "l175f_run.py"
DST = "l226_run.py"

src = open(SRC).read()
SRC_SHA = hashlib.sha256(src.encode()).hexdigest()
print("src sha256", SRC_SHA[:16], len(src), "chars")
lines = src.splitlines(keepends=True)
assert len(lines) == 1391, ("l175f_run.py line count drift", len(lines))

out = src

# ---------- (iv) the three excisions, by LINE RANGE, each asserted ----------
def excise(text, a, b, first, last, why):
    """Cut 1-indexed lines a..b inclusive; assert slice identity + uniqueness."""
    sl = "".join(lines[a - 1:b])
    assert sl in text, ("excision is not a literal slice (STOP)", a, b)
    assert text.count(sl) == 1, ("excision slice is not unique (STOP)", a, b)
    assert sl.splitlines()[0] == first, ("first line drift", a, sl.splitlines()[0])
    assert sl.splitlines()[-1] == last, ("last line drift", b, sl.splitlines()[-1])
    print(f"excise {a}-{b} ({b - a + 1} lines): {why}")
    return text.replace(sl, "")


out = excise(
    out, 1094, 1098,
    "    # P-af (PREREG): swap arms are DELIBERATELY off the matched point.",
    '                     n25gW_below=bool(af_c["n25gW"] < AF_T))',
    "in-rollout paf block reads af_c['wAgN'/'n25gW'] (arms not rolled out)")
out = excise(
    out, 1211, 1279,
    'z135c = np.load("l135/raw_l135.npz")',
    "    f\"{'PASS' if fc169_pass else 'FAIL'} (max {fc169_max:.1e})\")",
    "C0A-150/FC-144/FC-145/FC-169 read full,b65,silW,eMot*,wAgN,n25gW")
out = excise(
    out, 1337, 1354,
    "# ---- C0-NT (PREREG): a swap arm bit-identical to its own-gain twin",
    "    f\"{np.mean([v['n25gW'] for v in _afmis.values()]):.4f}\")",
    "C0-NT swap + P-af direction read the two swap arms")

# ---------- (v) rewrite the output block ----------
TAILBLK = "".join(lines[1354:1391])
assert TAILBLK in out and out.count(TAILBLK) == 1
assert TAILBLK.startswith('out = dict(g_cutwA=GAIN["cutwA"]')
assert TAILBLK.rstrip().endswith('f"FC-145 {out[\'fc145_max\']:.1e}) | done {time.time()-t0:.0f}s")')
NEWTAIL = '''# ---- CERT-SUBSET (L226 PREREG 0a, HALTING): FC-169B2 restricted to the
# five registered arms by construction is the arm-subset no-op proof. A
# non-zero max means dropping arms from the ROLLOUT loop moved the stream
# or the substrate -> the run is VOID and no B38 value may be read.
assert len(ARMS) == 5 and set(ARMS) == {"f4wA", "f4ng", "f4tw", "cutwA",
                                        "cutng25"}, "ARMS slice drift (STOP)"
assert fc169b2_pass and fc169b2_max == 0.0, \\
    ("CERT-SUBSET: arm subset is NOT a bit-exact rollout no-op (VOID)",
     fc169b2_max)
assert len(fc169b2) == 2 * (len(C0A150_KEYS) + 1) * len(ARMS), \\
    ("CERT-SUBSET coverage", len(fc169b2))
log(f"CERT-SUBSET GREEN: {len(fc169b2)} bit-identity checks "
    f"(5 arms x {len(C0A150_KEYS)} keys + af, 2 anchor seeds) max "
    f"{fc169b2_max:.1e}")
# ---- CERT-GAIN (HALTING): all five gains land on their stored values.
assert GAIN["cutwA"] == G_CUTWA_STORED and GAIN["cutng25"] == G_CUTNG25_STORED, \\
    "CERT-GAIN base gains drifted (STOP)"
assert all(f4_gain_exact.values()), ("CERT-GAIN f4 drift", f4_gain_exact)
assert GAIN["eMotTop5"] == G_EMOTTOP5_STORED and \\
    GAIN["eMotBot5"] == G_EMOTBOT5_STORED, "CERT-GAIN eMot drift (STOP)"
log("CERT-GAIN GREEN: 7 fresh bisects == stored values EXACT")
# ---- CERT-SEP (HALTING): the floor must have entered the step loop.
assert ntf4_pass, ("CERT-SEP: an f4 arm is bit-identical to a twin (VOID)",
                   min(ntf4.values()))
log("CERT-SEP GREEN: all f4 arms separated from base + from each other")
out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),
           g_eMotTop5=GAIN["eMotTop5"], g_eMotBot5=GAIN["eMotBot5"],
           g_emottop5_stored_exact=bool(GAIN["eMotTop5"] == G_EMOTTOP5_STORED),
           g_emotbot5_stored_exact=bool(GAIN["eMotBot5"] == G_EMOTBOT5_STORED),
           e_band_ok=e_band_ok, new_stairs=new_stairs,
           e_edges=E_EDGES, K=K, mass_split=mass_split,
           arms=list(ARMS), batch=[int(s) for s in B38],
           n_seeds=len(SEEDS), af_target=AF_T,
           g_f4wA=GAIN["f4wA"], g_f4ng=GAIN["f4ng"],
           g_f4tw=GAIN["f4tw"], floor=FLOOR, K4=K4,
           f4_twin_gi=GI_F4TWIN, f4_carrier_rank=_r_carrier,
           f4_stairs=f4_stairs, f4_band_ok=f4_band_ok,
           f4_edges={_a4: int(WB[_a4].values().numel()) for _a4 in F4_ARMS},
           f4_n={_a4: N_OF[_a4] for _a4 in F4_ARMS},
           cert_subset_checks=len(fc169b2),
           fc169b2_max=fc169b2_max, fc169b2_pass=fc169b2_pass,
           f4_gain_exact=f4_gain_exact,
           ntf4=ntf4, ntf4_pass=ntf4_pass, paf4=paf4, paf4_ok=paf4_ok,
           c0a_pass=bool(fc169b2_pass and ntf4_pass
                         and all(f4_gain_exact.values())))
json.dump(out, open("l226/anchors_run.json", "w"), indent=1)
log(f"L226 ANCHORS {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(CERT-SUBSET {out['fc169b2_max']:.1e} over "
    f"{out['cert_subset_checks']} checks) | done {time.time()-t0:.0f}s")
'''
out = out.replace(TAILBLK, NEWTAIL)

# ---------- (i) ARMS -> the five registered arms ----------
OLD_ARMS = ('ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",\n'
            '        "eMotBot5", "wAgN", "n25gW", "f4wA", "f4ng", "f4tw"]\n')
assert OLD_ARMS in out and out.count(OLD_ARMS) == 1, "ARMS line not found"
out = out.replace(
    OLD_ARMS,
    '# L226 COST SLICE (PREREG 0a): only the five arms all three batches\n'
    '# share are rolled out. The generator stream is ARMS-independent (one\n'
    '# nz_o / nz_a draw per step from gen / gen2 regardless), so this is a\n'
    '# no-op for the arms read — PROVEN, not assumed, by CERT-SUBSET below.\n'
    'ARMS = ["f4wA", "f4ng", "f4tw", "cutwA", "cutng25"]\n')

# ---------- (ii) fresh batch B38 + output paths ----------
assert "B37 = list(range(3701, 3717))" in out
out = out.replace("B37 = list(range(3701, 3717))", "B38 = list(range(3801, 3817))")
n_b37 = out.count("B37")
out = out.replace("B37", "B38")
print("B37 -> B38 occurrences replaced:", n_b37)
for a, b in [('"l175f/raw_partial.npz"', '"l226/raw_partial.npz"'),
             ('"l175f/raw_l175f.npz"', '"l226/raw_l226.npz"'),
             ('"raw_l175f.npz checkpointed BEFORE analysis"',
              '"raw_l226.npz checkpointed BEFORE analysis"')]:
    assert out.count(a) >= 1, ("missing path token", a)
    out = out.replace(a, b)

# ---------- (iii) B38 absence scan extended to l175f ----------
assert '"l169b2/raw_partial.npz"]' in out
out = out.replace('"l169b2/raw_partial.npz"]',
                  '"l169b2/raw_partial.npz",\n'
                  '          "l175f/raw_l175f.npz",\n'
                  '          "l175f/raw_partial.npz"]')

# ---------- header ----------
out = out.replace(
    '"""L175 run: the FLOOR-4 LEFT-SIDE registered test (fresh batch B38).',
    '"""L226 run: the FLOOR currency OUT OF SAMPLE — fresh batch B38, the\n'
    'FIVE shared arms only. MECHANICALLY DERIVED from l175f_run.py by\n'
    'l226_build.py (src sha256 ' + SRC_SHA[:16] + '): arms, batch, paths,\n'
    'three excisions of dropped-arm anchor blocks and one rewritten output\n'
    'block with the CERT-SUBSET / CERT-GAIN / CERT-SEP halting gates.\n'
    'PREREG l226/PREREG.md was frozen BEFORE this file existed.\n\n'
    'Lineage docstring of the source follows verbatim.\n\n'
    'L175 run: the FLOOR-4 LEFT-SIDE registered test (fresh batch B37).')

# ---------- negative audit ----------
# NOT a bare-token scan on "l175f" (the tick-248/256/257 trap): the parent
# batch's npzs MUST appear, inside the B38 absence-scan list and nowhere
# else. Gate STRUCTURALLY: exactly the two inserted _prevs lines, and no
# write/consume path pointing at l175f.
_l175f_hits = [ln for ln in out.splitlines() if "l175f/" in ln]
assert _l175f_hits == [
    'l175f/PREREG.md was frozen BEFORE this file existed.',          # lineage prose
    '          "l175f/raw_l175f.npz",',                              # absence scan
    '          "l175f/raw_partial.npz"]',                            # absence scan
    '# ---- FC-169B2 (L175 REGISTERED ANCHOR, PREREG l175f/PREREG.md V2): ALL',
], _l175f_hits
for tok in ('af_c["wAgN"]', 'z135c', 'z144c', 'z145c', 'z169c',
            'fc144', 'fc145', 'fc169_max', '_afmis', 'paf_ok'):
    assert tok not in out, ("excised token survived in output", tok)
assert out.count("json.dump") == 1 and out.count("np.savez") == 2, \
    "write count drift (STOP)"
assert 'l226/anchors_run.json' in out and 'l226/raw_l226.npz' in out
assert out.count("fc169b2_max == 0.0") == 1, "CERT-SUBSET gate missing"

# ---------- diff audit ----------
# STRUCTURAL for deletions (strictly stronger than a regex): every removed
# line must belong to one of the THREE declared excision slices or to the
# rewritten output block. The regex is applied only to ADDED lines.
EXCISED = set()
for _a, _b in ((1094, 1098), (1211, 1279), (1337, 1354), (1355, 1391)):
    for _ln in "".join(lines[_a - 1:_b]).splitlines():
        EXCISED.add(_ln)
EDITED_OLD = {OLD_ARMS.splitlines()[0], OLD_ARMS.splitlines()[1],
              "B37 = list(range(3701, 3717))",
              '          "l169b2/raw_partial.npz"]'}
changed = [l for l in difflib.unified_diff(src.splitlines(), out.splitlines(),
                                           lineterm="", n=0)
           if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
dels = [c[1:] for c in changed if c.startswith("-")]
adds = [c[1:] for c in changed if c.startswith("+")]
unex_del = [d for d in dels
            if d not in EXCISED and d not in EDITED_OLD
            and "l175f" not in d and "B37" not in d and "ARMS" not in d]
allowed = re.compile(
    r"B38|l226|raw_l226|l175f|ARMS|CERT-SUBSET|CERT-GAIN|CERT-SEP|"
    r"fc169b2|ntf4|f4_gain_exact|paf4|out = dict|json\.dump|log\(|assert |"
    r"MECHANICALLY|PREREG|Lineage|L175 run:|L226 run:|arms, batch, paths|"
    r"three excisions|block with|^\s*$|^#|^\s+f\"|^\s+\"|^\s+'|"
    r"g_|e_band_ok|e_edges|K=K|K4|floor=FLOOR|f4_|n_seeds|af_target|"
    r"mass_split|new_stairs|batch=|arms=|cert_subset|c0a_pass|"
    r"GAIN\[|generator stream|no-op for the arms|share are rolled out")
unex_add = [a for a in adds if not allowed.search(a)]
print(f"diff: {len(dels)} deletions ({len(unex_del)} unexplained), "
      f"{len(adds)} additions ({len(unex_add)} unexplained)")
for b in (unex_del + unex_add)[:12]:
    print("  UNEXPLAINED:", repr(b))
assert not unex_del, "a deleted line is outside every declared excision (STOP)"
assert not unex_add, "unexplained ADDED line (STOP)"

import ast
ast.parse(out)
open(DST, "w").write(out)
print("wrote", DST, len(out), "chars  sha256",
      hashlib.sha256(out.encode()).hexdigest()[:16],
      len(out.splitlines()), "lines")
