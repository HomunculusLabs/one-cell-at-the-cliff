"""l232_build.py — generate l232_static.py from VERBATIM certified slices.

SLICE A = l216_static.py lines 1-1360: a literal PREFIX of the parent, cut
          immediately BEFORE its writer and AST-verified to contain ZERO
          write sites (the L230/L231 construction, re-used). Re-runs every
          pin and CERT-F4/178/GEN/205/GAP/209 plus the NO-OP as the code
          that actually produced l216/static.json, and leaves TABLE /
          NULLS / AINF / PERRON / CELLS / SUBS / OPS / LAMS / LOCAL /
          GROUPS / PERM / arrivals / side_stats_from / decorate in memory.
SLICE B = l217_tail.py lines 245-258: L217's `dcross`, so the crossing
          EXISTENCE is decided by the expression that produced
          l217/static.json.
HEAD    = l232_head.py — defines ONLY the output dict P.
SLICE C = l230_tail.py lines 39-211: L230's OWN EPS / leafcmp / leaves +
          CERT-216 + the lam1 NO-OP re-assertion + CERT-AINF + CERT-217,
          re-used VERBATIM as the code that passed them in tick 262 (the
          L225 law: re-use a prior card's CERTIFICATION BLOCK as a verbatim
          source slice, not its statistic). Coverage bars DERIVED from the
          artifacts' own leaf counts.
TAIL    = l232_tail.py.

Writes l232_static.py ONLY. Run from ~/critters/peabrain-lab/banc.
"""
import ast
import hashlib
import sys

SRC_A, LO_A, HI_A = "l216_static.py", 1, 1360
SRC_B, LO_B, HI_B = "l217_tail.py", 245, 258
HEAD = "l232_head.py"
SRC_C, LO_C, HI_C = "l230_tail.py", 39, 211
TAIL = "l232_tail.py"
OUT = "l232_static.py"
PARENT_TAIL = "l216_tail.py"
PARENT_TAIL_SHA16 = "d9cb45022621452b"   # recorded in l216_static.py's banner
# Inherited pins. Every one of these is ALSO asserted to be present in
# l230_static.py's own generated banner, so it is read off disk rather than
# retyped from memory (tick 262's fabricated-hash halt, repaired at the root).
SLICE_A_SHA16 = "6a3760d0b387a807"
SRC_A_SHA16 = "8d4740020fcd2a7b"
SLICE_B_SHA16 = "b26c0ab47cf0e2bb"
SRC_B_SHA16 = "9ffc9d582e205637"
SRC_C_SHA16 = "e9be8999c9d9d351"       # l230_tail.py whole-file, from banner


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def read(p):
    with open(p) as f:
        return f.read()


A_full, B_full, C_full = read(SRC_A), read(SRC_B), read(SRC_C)
H_full, T_full = read(HEAD), read(TAIL)
PT_full = read(PARENT_TAIL)
A_lines, B_lines, C_lines = (A_full.split("\n"), B_full.split("\n"),
                             C_full.split("\n"))
sliceA = "\n".join(A_lines[LO_A - 1:HI_A]) + "\n"
sliceB = "\n".join(B_lines[LO_B - 1:HI_B]) + "\n"
sliceC = "\n".join(C_lines[LO_C - 1:HI_C]) + "\n"

# ---- 1. the slices are literal text of their sources ----------------------
assert A_full.startswith(sliceA), "SLICE A is not a literal PREFIX of the parent"
assert sliceB in B_full, "SLICE B is not a literal substring of l217_tail.py"
assert sliceC in C_full, "SLICE C is not a literal substring of l230_tail.py"
for nm, lo, hi, s, src in (("A", LO_A, HI_A, sliceA, SRC_A),
                           ("B", LO_B, HI_B, sliceB, SRC_B),
                           ("C", LO_C, HI_C, sliceC, SRC_C)):
    print(f"[slice] {nm} = {src} {lo}-{hi} ({len(s)} B) sha {sha(s)[:16]}")
for src, full in ((SRC_A, A_full), (SRC_B, B_full), (SRC_C, C_full)):
    print(f"[pin]   {src} whole sha {sha(full)[:16]}")

# ---- 2. INHERITED PINS, cross-checked against l230_static.py's banner -----
L230_banner = read("l230_static.py")[:2000]
assert sha(sliceA)[:16] == SLICE_A_SHA16, (sha(sliceA)[:16], SLICE_A_SHA16)
assert sha(A_full)[:16] == SRC_A_SHA16, (sha(A_full)[:16], SRC_A_SHA16)
assert sha(sliceB)[:16] == SLICE_B_SHA16, (sha(sliceB)[:16], SLICE_B_SHA16)
assert sha(B_full)[:16] == SRC_B_SHA16, (sha(B_full)[:16], SRC_B_SHA16)
assert sha(C_full)[:16] == SRC_C_SHA16, (sha(C_full)[:16], SRC_C_SHA16)
for _s in (SLICE_A_SHA16, SRC_A_SHA16, SLICE_B_SHA16, SRC_B_SHA16,
           SRC_C_SHA16):
    assert _s in L230_banner, (_s, "not recorded in l230_static.py's banner")
print("[inherited pin] SLICE A / SLICE B / l230_tail.py whole-file shas — "
      "ALL re-derived here AND present in l230_static.py's own banner")

# ---- 3. PARENT PIN: l216_tail.py is a literal SUFFIX of l216_static.py ----
assert A_full.endswith(PT_full), f"{PARENT_TAIL} is not a SUFFIX of {SRC_A}"
assert sha(PT_full)[:16] == PARENT_TAIL_SHA16, \
    (sha(PT_full)[:16], PARENT_TAIL_SHA16, "parent tail sha drift")
assert f"TAIL       = {PARENT_TAIL} (sha256 {PARENT_TAIL_SHA16})" in A_lines[11], \
    ("banner line 12", A_lines[11])
print(f"[PARENT PIN] {PARENT_TAIL} sha {PARENT_TAIL_SHA16} is a literal SUFFIX "
      f"of {SRC_A} AND the value that file's own banner records — GREEN")

# ---- 4. STRUCTURAL cut audit on SLICE A (AST, never a line count) ---------
cutA = A_lines[HI_A:]
cut_txt = "\n".join(cutA)
for tok in ('os.makedirs("l216"', 'json.dump(o, open("l216/static.json"',
            "L216 DONE"):
    assert tok in cut_txt, (tok, "expected in the CUT region")
    assert tok not in sliceA, (tok, "leaked into SLICE A")
_ct = ast.parse(cut_txt)
_cut_calls = []
for _n in _ct.body:
    assert isinstance(_n, ast.Expr) and isinstance(_n.value, ast.Call), \
        (ast.unparse(_n)[:60], "CUT region carries a non-call statement")
    _f = _n.value.func
    _cut_calls.append(_f.attr if isinstance(_f, ast.Attribute) else _f.id)
assert sorted(_cut_calls) == ["dump", "log", "log", "makedirs"], \
    (_cut_calls, "unexpected CUT content")
print(f"[cut] {len(cutA)} cut lines / {len(_ct.body)} statements {_cut_calls} "
      f"— AST-proven to be the parent's writer plus its closing log")

# ---- 5. SLICE B is exactly dcross ----------------------------------------
_bt = ast.parse(sliceB)
_bdefs = sorted(n.name for n in _bt.body if isinstance(n, ast.FunctionDef))
assert _bdefs == ["dcross"], (_bdefs, "SLICE B is not exactly dcross")
assert len([n for n in _bt.body]) == 1, "SLICE B carries extra statements"
print(f"[slice B] AST: defines exactly {_bdefs} and nothing else")

# ---- 6. SLICE C carries the four certification gates, and nothing else ----
assert sliceC.lstrip().startswith("EPS = float(np.finfo(float).eps)"), sliceC[:60]
assert sliceC.rstrip().endswith("l217_null_frac_both_cross=_L217_RATE)"), \
    sliceC[-90:]
for tok in ("CERT-216", "CERT-AINF", "CERT-217", "def leafcmp", "def leaves",
            "_f216 = os.stat", '_f217 = os.stat',
            'S216 = json.load(open("l216/static.json"))',
            'S217 = json.load(open("l217/static.json"))',
            "_bar216", "norm_noop_max_rel_diff", "DXNULL", "_L217_RATE",
            "RESFLOOR"):
    assert tok in sliceC, (tok, "SLICE C lost a required piece")
_cc = ast.parse(sliceC)
_cdefs = sorted(n.name for n in _cc.body if isinstance(n, ast.FunctionDef))
assert _cdefs == ["leafcmp", "leaves"], (_cdefs, "SLICE C defines extra defs")
# NEGATIVE, structural: no L230 MEASUREMENT block and no writer. (A bare-token
# guard would fire on SLICE C's own inherited prose, so each token below is a
# CODE token that appears only inside L230's measurement blocks.)
for tok in ("LOGRHO = {}", "CF = {}", "share_K", "D_cf", 'P["branch"]',
            'P["predictions"]', "json.dump"):
    assert tok not in sliceC, (tok, "L230 measurement leaked into SLICE C")
print(f"[slice C] AST: defines exactly {_cdefs}; carries CERT-216 + NO-OP + "
      f"CERT-AINF + CERT-217; no L230 measurement, no branch, no writer")

# ---- 7. assemble ----------------------------------------------------------
banner = (
    '"""GENERATED by l232_build.py — do not edit by hand.\n'
    f"SLICE A = {SRC_A} lines {LO_A}-{HI_A} VERBATIM, a literal PREFIX cut\n"
    f"          immediately before the parent's writer (sha256 "
    f"{sha(sliceA)[:16]}; whole-file sha256 {sha(A_full)[:16]}).\n"
    f"          AST-verified: ZERO write sites. Inherits every pin plus\n"
    f"          CERT-F4 / CERT-178 / CERT-GEN / CERT-205 / CERT-GAP /\n"
    f"          CERT-209 and the lam1 NO-OP as the code that produced\n"
    f"          l216/static.json.\n"
    f"PARENT PIN: {PARENT_TAIL} (sha256 {PARENT_TAIL_SHA16}) is a literal\n"
    f"          SUFFIX of {SRC_A} and the sha that file's banner records.\n"
    f"SLICE B = {SRC_B} lines {LO_B}-{HI_B} VERBATIM — L217's dcross\n"
    f"          (sha256 {sha(sliceB)[:16]}; whole-file sha256 "
    f"{sha(B_full)[:16]}).\n"
    f"HEAD    = {HEAD} (sha256 {sha(H_full)[:16]}) — defines P only.\n"
    f"SLICE C = {SRC_C} lines {LO_C}-{HI_C} VERBATIM — L230's own\n"
    f"          CERT-216 + NO-OP + CERT-AINF + CERT-217 block plus\n"
    f"          leafcmp/leaves (sha256 {sha(sliceC)[:16]}; whole-file\n"
    f"          sha256 {sha(C_full)[:16]}).\n"
    f"TAIL    = {TAIL} (sha256 {sha(T_full)[:16]}).\n"
    'PREREG l232/PREREG.md. Writes l232/static.json ONLY.\n'
    '"""\n')
out = (banner + sliceA + "\n" + sliceB + "\n" + H_full + "\n" + sliceC
       + "\n" + T_full)

# ---- 8. AST audits on the GENERATED file ----------------------------------
tree = ast.parse(out)

bad = []
for n in ast.walk(tree):
    if isinstance(n, ast.Import):
        bad += [a.name for a in n.names]
    elif isinstance(n, ast.ImportFrom):
        bad.append(n.module or "")
mods = sorted(set(m.split(".")[0] for m in bad))
lab = [m for m in mods if m.startswith("l") and len(m) > 1 and m[1].isdigit()]
assert not lab, (lab, "a lab module is imported (L175)")
print(f"[AST import] modules {mods} — no lab module imported")

WRITE_FUNCS = {"savez", "savez_compressed", "write_text", "to_csv",
               "replace", "rename", "savefig", "save"}


def write_sites(src):
    t = ast.parse(src)
    w, md = [], []
    for n in ast.walk(t):
        if not isinstance(n, ast.Call):
            continue
        fn = n.func
        name = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else "")
        if name == "open":
            mode = ""
            if len(n.args) > 1 and isinstance(n.args[1], ast.Constant):
                mode = str(n.args[1].value)
            for kw in n.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = str(kw.value.value)
            if any(c in mode for c in "wax+"):
                w.append((n.lineno, "open:" + mode,
                          ast.unparse(n.args[0]) if n.args else "?"))
        elif name == "dump" and isinstance(fn, ast.Attribute) \
                and isinstance(fn.value, ast.Name) and fn.value.id == "json":
            w.append((n.lineno, "json.dump",
                      ast.unparse(n.args[1]) if len(n.args) > 1 else "?"))
        elif name in WRITE_FUNCS and isinstance(fn, ast.Attribute) \
                and isinstance(fn.value, ast.Name) \
                and fn.value.id in ("np", "os", "torch", "plt"):
            w.append((n.lineno, f"{fn.value.id}.{name}",
                      ast.unparse(n.args[0]) if n.args else "?"))
        elif name == "makedirs":
            md.append((n.lineno, ast.unparse(n.args[0]) if n.args else "?"))
    return w, md


writes, makedirs = write_sites(out)
opens = [w for w in writes if w[1].startswith("open:")]
dumps = [w for w in writes if w[1] == "json.dump"]
others = [w for w in writes if w not in opens and w not in dumps]
assert not others, (others, "unexpected write-like call")
assert len(opens) == 1 and len(dumps) == 1, (opens, dumps, "write count")
assert opens[0][0] == dumps[0][0], (opens, dumps, "open and dump differ")
assert "'l232/static.json'" in opens[0][2].replace('"', "'"), opens[0]
assert len(makedirs) == 1 and "l232" in makedirs[0][1], makedirs
print(f"[AST write] exactly ONE write site: line {opens[0][0]} "
      f"json.dump(..., open({opens[0][2]}, 'w')) + one makedirs {makedirs[0][1]}")

for nm, src in (("SLICE A", sliceA), ("SLICE B", sliceB), ("SLICE C", sliceC)):
    w, md = write_sites(src)
    assert not w and not md, (nm, w, md, "slice is NOT write-free")
    print(f"[AST write] {nm} proven WRITE-FREE (0 write sites, 0 makedirs)")

# ---- 9. the tail reads the objects it claims to inherit -------------------
for nm in ("TABLE", "NULLS", "AINF", "CELLS", "SUBS", "OPS", "LAMS",
           "LOCAL", "JOINTS", "DMAX", "DMAX_CERT", "NDRAW", "SEED_PERM",
           "arrivals", "side_stats_from", "_f209", "_f210"):
    assert nm in T_full, (nm, "tail does not use an inherited object")
    assert nm in sliceA, (nm, "inherited object not in SLICE A")
assert "MAXREL" in H_full and "MAXREL" in sliceA, "MAXREL not inherited"
for nm in ("dcross",):
    assert nm in T_full and nm in sliceB, (nm, "dcross not inherited")
for nm in ("RESFLOOR", "DX", "DXNULL", "_L217_RATE", "_f216", "_f217"):
    assert nm in T_full and nm in sliceC, (nm, "SLICE C object not inherited")
assert "P = dict(" in H_full and 'P["cert_216"]' in sliceC
print("[deps] every inherited object the tail reads is defined in a slice")

# ---- 10. the tail must not write any prior artifact ----------------------
for p in ("l216/static.json", "l217/static.json", "l209/static.json",
          "l210/static.json", "l205/static.json", "l215/static.json",
          "l92/static.json", "l101/static.json", "l230/static.json",
          "l231/static.json"):
    assert f'open("{p}", "w")' not in T_full, (p, "tail writes a prior!")
    assert f"open('{p}', 'w')" not in T_full, (p, "tail writes a prior!")

with open(OUT, "w") as f:
    f.write(out)
print(f"[write] {OUT} {len(out.splitlines())} lines sha {sha(out)[:16]}")
print(f"[write] head sha {sha(H_full)[:16]} tail sha {sha(T_full)[:16]}")
sys.exit(0)
