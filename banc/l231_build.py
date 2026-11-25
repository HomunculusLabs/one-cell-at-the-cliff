"""l231_build.py — generate l231_static.py from VERBATIM certified slices.

SLICE A = l216_static.py lines 1-1360: a literal PREFIX of the parent, cut
          immediately BEFORE its writer and AST-verified to contain ZERO
          write sites (the L230 construction, re-used). Re-runs every pin and
          CERT-F4/178/GEN/205/GAP/209 plus the NO-OP as the code that
          actually produced l216/static.json, and leaves PERRON / AINF /
          GAPS / FITS / TABLE / CELLS / SUBS / LOCAL / GROUPS / POOL_G /
          side_stats_from / decorate / pi_sub / build_sub in memory.
HEAD    = l231_head.py — defines ONLY the output dict P.
SLICE C = l230_tail.py lines 39-128: L230's OWN CERT-216 block (plus leafcmp
          / leaves and the lam1 NO-OP re-assertion), re-used VERBATIM as the
          code that passed it in tick 262 — the L225 law: re-use a prior
          card's CERTIFICATION BLOCK as a verbatim source slice, not its
          statistic. Its coverage bar is DERIVED from l216/static.json's own
          leaf count.
TAIL    = l231_tail.py.

Writes l231_static.py ONLY. Run from ~/critters/peabrain-lab/banc.
"""
import ast
import hashlib
import sys

SRC_A, LO_A, HI_A = "l216_static.py", 1, 1360
HEAD = "l231_head.py"
SRC_C, LO_C, HI_C = "l230_tail.py", 39, 128
TAIL = "l231_tail.py"
OUT = "l231_static.py"
PARENT_TAIL = "l216_tail.py"
PARENT_TAIL_SHA16 = "d9cb45022621452b"   # recorded in l216_static.py's banner
# SLICE A's sha256, as l230_build.py measured and l230_static.py's banner
# recorded it in tick 262 — asserted, never retyped from memory of a number:
SLICE_A_SHA16 = "6a3760d0b387a807"
SRC_A_SHA16 = "8d4740020fcd2a7b"
# l230_static.py's banner is the ON-DISK record of both; both are re-derived
# here and cross-checked against that banner's text.


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def read(p):
    with open(p) as f:
        return f.read()


A_full, C_full, H_full, T_full = read(SRC_A), read(SRC_C), read(HEAD), read(TAIL)
PT_full = read(PARENT_TAIL)
A_lines, C_lines = A_full.split("\n"), C_full.split("\n")
sliceA = "\n".join(A_lines[LO_A - 1:HI_A]) + "\n"
sliceC = "\n".join(C_lines[LO_C - 1:HI_C]) + "\n"

# ---- 1. the slices are literal text of their sources ----------------------
assert A_full.startswith(sliceA), "SLICE A is not a literal PREFIX of the parent"
assert sliceC in C_full, "SLICE C is not a literal substring of l230_tail.py"
print(f"[slice] A = {SRC_A} {LO_A}-{HI_A} ({len(sliceA)} B) sha {sha(sliceA)[:16]}")
print(f"[slice] C = {SRC_C} {LO_C}-{HI_C} ({len(sliceC)} B) sha {sha(sliceC)[:16]}")
print(f"[pin]   {SRC_A} whole sha {sha(A_full)[:16]}")
print(f"[pin]   {SRC_C} whole sha {sha(C_full)[:16]}")

# ---- 2. INHERITED PINS, cross-checked against l230_static.py's banner -----
# The sha values above are not trusted from memory: they must match BOTH the
# freshly computed digest AND the text l230_static.py's own generated banner
# records. (Tick 262's third halt: a hand-typed hash is a fabricated hash.)
L230_banner = read("l230_static.py")[:2000]
assert sha(sliceA)[:16] == SLICE_A_SHA16, (sha(sliceA)[:16], SLICE_A_SHA16)
assert sha(A_full)[:16] == SRC_A_SHA16, (sha(A_full)[:16], SRC_A_SHA16)
for _s in (SLICE_A_SHA16, SRC_A_SHA16):
    assert _s in L230_banner, (_s, "not recorded in l230_static.py's banner")
print(f"[inherited pin] SLICE A sha {SLICE_A_SHA16} / {SRC_A} whole sha "
      f"{SRC_A_SHA16} — BOTH re-derived here AND present in "
      f"l230_static.py's own generated banner")

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

# ---- 5. SLICE C carries CERT-216 and the NO-OP, and nothing that writes ---
assert sliceC.lstrip().startswith("EPS = float(np.finfo(float).eps)"), sliceC[:60]
assert sliceC.rstrip().endswith("equals_l216_stored=True)"), sliceC[-80:]
for tok in ("CERT-216", "def leafcmp", "def leaves", "_f216 = os.stat",
            'S216 = json.load(open("l216/static.json"))', "_bar216",
            "norm_noop_max_rel_diff"):
    assert tok in sliceC, (tok, "SLICE C lost a required piece")
# NEGATIVE, structural: no L230-specific measurement block and no writer
_cc = ast.parse(sliceC)
_cdefs = sorted(n.name for n in _cc.body if isinstance(n, ast.FunctionDef))
assert _cdefs == ["leafcmp", "leaves"], (_cdefs, "SLICE C defines extra defs")
for tok in ("dcross", "CF_", "D_cf", "share_K", "AINF_NULL", "CERT-217",
            "P[\"branch\"]", "P[\"predictions\"]"):
    assert tok not in sliceC, (tok, "L230 measurement leaked into SLICE C")
print(f"[slice C] AST: defines exactly {_cdefs}; carries CERT-216 + the "
      f"NO-OP; no L230 measurement, no branch, no writer")

# ---- 6. assemble ----------------------------------------------------------
banner = (
    '"""GENERATED by l231_build.py — do not edit by hand.\n'
    f"SLICE A = {SRC_A} lines {LO_A}-{HI_A} VERBATIM, a literal PREFIX cut\n"
    f"          immediately before the parent's writer (sha256 "
    f"{sha(sliceA)[:16]}; whole-file sha256 {sha(A_full)[:16]}).\n"
    f"          AST-verified: ZERO write sites. Inherits every pin plus\n"
    f"          CERT-F4 / CERT-178 / CERT-GEN / CERT-205 / CERT-GAP /\n"
    f"          CERT-209 and the lam1 NO-OP as the code that produced\n"
    f"          l216/static.json.\n"
    f"PARENT PIN: {PARENT_TAIL} (sha256 {PARENT_TAIL_SHA16}) is a literal\n"
    f"          SUFFIX of {SRC_A} and the sha that file's banner records.\n"
    f"HEAD    = {HEAD} (sha256 {sha(H_full)[:16]}) — defines P only.\n"
    f"SLICE C = {SRC_C} lines {LO_C}-{HI_C} VERBATIM — L230's own CERT-216\n"
    f"          block + leafcmp/leaves + the NO-OP re-assertion (sha256\n"
    f"          {sha(sliceC)[:16]}; whole-file sha256 {sha(C_full)[:16]}).\n"
    f"TAIL    = {TAIL} (sha256 {sha(T_full)[:16]}).\n"
    'PREREG l231/PREREG.md. Writes l231/static.json ONLY.\n'
    '"""\n')
out = banner + sliceA + "\n" + H_full + "\n" + sliceC + "\n" + T_full

# ---- 7. AST audits on the GENERATED file ----------------------------------
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
assert "'l231/static.json'" in opens[0][2].replace('"', "'"), opens[0]
assert len(makedirs) == 1 and "l231" in makedirs[0][1], makedirs
print(f"[AST write] exactly ONE write site: line {opens[0][0]} "
      f"json.dump(..., open({opens[0][2]}, 'w')) + one makedirs {makedirs[0][1]}")

for nm, src in (("SLICE A", sliceA), ("SLICE C", sliceC)):
    w, md = write_sites(src)
    assert not w and not md, (nm, w, md, "slice is NOT write-free")
    print(f"[AST write] {nm} proven WRITE-FREE (0 write sites, 0 makedirs)")

# ---- 8. the tail reads the objects it claims to inherit -------------------
for nm in ("PERRON", "AINF", "SUBS", "OPS", "GROUPS", "POOL_G",
           "JOINTS", "keep_wA", "ann", "ann_gi", "sup", "region", "src_all",
           "asym", "pi_sub", "build_sub", "S101", "Nall",
           "EPS", "_f209", "_f210"):
    assert nm in T_full, (nm, "tail does not use an inherited object")
    assert nm in (sliceA + sliceC), (nm, "inherited object not in a slice")
assert "_f216" in T_full and "_f216 = os.stat" in sliceC
assert "MAXREL" in H_full and "MAXREL" in sliceA
print("[deps] every inherited object the tail reads is defined in a slice")

# ---- 9. the tail must not write any prior artifact ------------------------
for p in ("l216/static.json", "l209/static.json", "l210/static.json",
          "l215/static.json", "l92/static.json", "l101/static.json"):
    assert f'open("{p}", "w")' not in T_full, (p, "tail writes a prior!")
    assert f"open('{p}', 'w')" not in T_full, (p, "tail writes a prior!")

with open(OUT, "w") as f:
    f.write(out)
print(f"[write] {OUT} {len(out.splitlines())} lines sha {sha(out)[:16]}")
print(f"[write] head sha {sha(H_full)[:16]} tail sha {sha(T_full)[:16]}")
sys.exit(0)
