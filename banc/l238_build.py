"""l238_build.py — generate l238_static.py = l220_static.py lines 1-1916
VERBATIM + l238_tail.py (this card's own measurement + its ONE write).

The slice is the parent's whole prefix: nine certified slices of the L151 ->
L178 -> L206 -> L207 -> L211 chain AND L220's own body, cut at the blank line
before L220's `predictions, scored` header. So L220's f4wA + cutwA walkers,
its 100 cutwA draws, its cohort on BOTH substrates and every parent gate
re-run as free certification before any L238 number is read (CERT-220).

Every pin below is DERIVED from the stored bytes at build time (L228: derive,
never retype) and printed. Every audit is STRUCTURAL (AST), never a bare-token
scan (L226/L227). PREREG l238/PREREG.md (registered first).
"""
import ast
import builtins as _bi
import hashlib
import pathlib

N_SLICE = 1916

# ---- parent: lines split on b"\n" ONLY (binary file iteration = the way the
# ---- tail itself re-reads the slice) ----------------------------------------
P_SRC = pathlib.Path("l220_static.py")
P_BYTES = P_SRC.read_bytes()
assert b"\r" not in P_BYTES, "parent has a CR (STOP)"
assert P_BYTES.endswith(b"\n"), "parent must end in a newline (STOP)"
P_LINES = P_BYTES[:-1].split(b"\n") if P_BYTES.endswith(b"\n") else P_BYTES.split(b"\n")
assert len(P_LINES) == 2007, (len(P_LINES), "parent line count moved (STOP)")
SLICE = b"\n".join(P_LINES[:N_SLICE]) + b"\n"
CUT = b"\n".join(P_LINES[N_SLICE:]) + b"\n"
assert SLICE + CUT == P_BYTES, "slice + cut is not the parent (STOP)"
assert len(SLICE.split(b"\n")) - 1 == N_SLICE
P_WHOLE = hashlib.sha256(P_BYTES).hexdigest()
S_SHA = hashlib.sha256(SLICE).hexdigest()
C_SHA = hashlib.sha256(CUT).hexdigest()

# ---- boundary: line 1916 is BLANK and 1917 is L220's predictions header -----
assert P_LINES[1915] == b"", ("line 1916 is not the blank line (STOP)", P_LINES[1915][:80])
assert P_LINES[1916].startswith(b"# ---------------- predictions, scored"), \
    ("line 1917 is not L220's predictions header (STOP)", P_LINES[1916][:80])
assert b"json.dump" in CUT and b"json.dump" not in SLICE, \
    "the writer must live in the CUT and never in the SLICE (STOP)"

# ---- PARENT PIN: the parent's own banner records its tail's sha, that tail is
# ---- a literal SUFFIX, and the CUT region lies inside it --------------------
BANNER = b"\n".join(P_LINES[:13]).decode()
PT_BYTES = pathlib.Path("l220_tail.py").read_bytes()
PT_SHA = hashlib.sha256(PT_BYTES).hexdigest()
# DERIVED probe (L227: never retype a banner): the ONE banner line naming the
# tail must carry the sha of the tail bytes on disk
_bl = [l for l in BANNER.split("\n") if "l220_tail.py" in l]
assert len(_bl) == 1 and f"sha256 {PT_SHA[:16]}" in _bl[0], \
    (_bl, PT_SHA[:16], "banner does not record this tail (STOP)")
assert P_BYTES.endswith(PT_BYTES), "l220_tail.py is not a literal SUFFIX (STOP)"
assert PT_BYTES.endswith(b"\n")
N_TAIL = PT_BYTES.count(b"\n")
K_TAIL = len(P_LINES) - N_TAIL + 1          # 1-based parent line where the tail starts
assert K_TAIL <= N_SLICE + 1, (K_TAIL, "tail does not own the whole cut region (STOP)")
assert "PREREG l220/PREREG.md. Writes l220/static.json ONLY." in BANNER
for _pin in ("CERT-HEAD1  = l151_static.py lines 1-319 VERBATIM",
             "CERT-211SL  = l211_tail.py lines 29-322 VERBATIM"):
    assert _pin in BANNER, (_pin, "inherited chain moved (STOP)")

# ---- the tail ---------------------------------------------------------------
T_SRC = pathlib.Path("l238_tail.py")
T_BYTES = T_SRC.read_bytes()
T_TXT = T_BYTES.decode()
assert b"\r" not in T_BYTES and T_BYTES.endswith(b"\n")
T_SHA = hashlib.sha256(T_BYTES).hexdigest()
N_T = T_BYTES.count(b"\n")
T_TREE = ast.parse(T_TXT)

# unambiguous mutator ATTRIBUTES (a call `x.<attr>(...)`): serialization
# writers, directory creation, fs mutation, process launch
_MUT = {"savez", "savez_compressed", "save", "to_csv", "makedirs",
        "mkdir", "unlink", "rmtree", "copyfile", "copy2", "move", "symlink",
        "chmod", "rmdir", "system", "popen", "fork", "execv", "kill"}
# attr names that are harmless on str/array but mutating on os/shutil/Path:
# flagged ONLY when called on those modules
_OSISH = {"replace", "rename", "remove", "write"}
_OSNAMES = {"os", "shutil", "pathlib", "Path", "_os238"}


def _calls(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute):
                yield n, f.attr, f
            elif isinstance(f, ast.Name):
                yield n, f.id, f


def _mut_sites(tree):
    hits = []
    for n, nm, f in _calls(tree):
        if nm in _MUT:
            hits.append((nm, getattr(n, "lineno", -1)))
        elif nm in _OSISH and isinstance(f, ast.Attribute) \
                and isinstance(f.value, ast.Name) and f.value.id in _OSNAMES:
            hits.append((f"{f.value.id}.{nm}", getattr(n, "lineno", -1)))
    return hits


def _lit(a):
    return a.value if isinstance(a, ast.Constant) else None


def _opens(tree):
    out = []
    for n, nm, f in _calls(tree):
        if nm == "open":
            mode = _lit(n.args[1]) if len(n.args) > 1 else "r"
            out.append((_lit(n.args[0]), mode or "r", getattr(n, "lineno", -1)))
    return out


# (i) exactly ONE dump and ONE write-mode open, both to l238/static.json
_dumps = [n for n, nm, f in _calls(T_TREE) if nm == "dump"]
assert len(_dumps) == 1, (len(_dumps), "the tail must have exactly ONE dump (STOP)")
# the dump's STREAM argument must be an open() of l238/static.json in "w"
_df = _dumps[0].args[1]
assert (isinstance(_df, ast.Call) and isinstance(_df.func, ast.Name)
        and _df.func.id == "open" and _lit(_df.args[0]) == "l238/static.json"
        and _lit(_df.args[1]) == "w"), "dump target (STOP)"
_tw = [x for x in _opens(T_TREE) if any(c in x[1] for c in "wax+")]
assert [(p, m) for p, m, _ in _tw] == [("l238/static.json", "w")], (_tw, "write-mode opens (STOP)")
# line number DERIVED from the dump node (never retyped): the single write-open IS the dump's stream
assert _tw[0][2] == _df.lineno, (_tw[0][2], _df.lineno, "the write-open is not the dump's stream (STOP)")
# (ii) no other write / process / fs-mutation call anywhere in the tail
_bad = _mut_sites(T_TREE)
assert not _bad, (_bad, "tail mutates something it must not (STOP)")
assert not any(isinstance(n, (ast.Import, ast.ImportFrom))
               and any((a.name.split(".")[0] in ("subprocess", "shutil", "socket", "ctypes"))
                       for a in n.names) for n in ast.walk(T_TREE)), \
    "tail imports a process/fs module (STOP)"
assert pathlib.Path("l238").is_dir(), "l238/ must exist (the tail does not mkdir)"
assert "l238/PREREG.md" in T_TXT and T_TXT.count("l238/static.json") >= 2
assert "subprocess" not in T_TXT and "systemctl" not in T_TXT

# (iii) the TAIL's own claims about the slice, checked here as code
assert f"N_SLICE238 = {N_SLICE}" in T_TXT, "tail slice width differs (STOP)"


# (iv) unresolved-name audit (STRUCTURAL, by AST): every free name the tail
# loads must be bound in the slice or the tail or be a builtin
def _bound(tree, args=False):
    b = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            b.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b.add(n.name)
        elif args and isinstance(n, ast.arg):
            b.add(n.arg)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                b.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ExceptHandler) and n.name:
            b.add(n.name)
        elif isinstance(n, ast.MatchAs) and n.name:
            b.add(n.name)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            b |= set(n.names)
    return b


def _mod_loads(tree):
    """Name loads at MODULE scope only (function/lambda bodies skipped, so a
    parameter can never mask an undefined global)."""
    out = set()
    stack = list(tree.body)
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            for d in getattr(n, "decorator_list", []):
                stack.append(d)
            for d in getattr(n, "args", ast.arguments(defaults=[], kw_defaults=[])).defaults:
                stack.append(d)
            continue
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            out.add(n.id)
        stack.extend(ast.iter_child_nodes(n))
    return out


S_TREE = ast.parse(SLICE.decode())
S_BOUND, T_BOUND = _bound(S_TREE), _bound(T_TREE)
T_MOD_LOADS = _mod_loads(T_TREE)
UNRES = sorted(T_MOD_LOADS - S_BOUND - T_BOUND - set(dir(_bi)))
assert not UNRES, (UNRES, "the tail loads names the slice does not bind (STOP)")
# loose companion INSIDE function bodies (params allowed): catches typos only
T_LOADS = {n.id for n in ast.walk(T_TREE)
           if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
UNRES_ALL = sorted(T_LOADS - _bound(S_TREE, True) - _bound(T_TREE, True) - set(dir(_bi)))
assert not UNRES_ALL, (UNRES_ALL, "unresolved name inside a function (STOP)")


def _mod_bound(tree):
    """Names bound at MODULE scope (function/lambda/class bodies skipped)."""
    b = set()
    stack = list(tree.body)
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b.add(n.name)
            continue
        if isinstance(n, ast.Lambda):
            continue
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            b.add(n.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                b.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ExceptHandler) and n.name:
            b.add(n.name)
        stack.extend(ast.iter_child_nodes(n))
    return b


def _free_globals(fn):
    """Globals a certified function READS at call time (params + anything
    assigned inside it are local; nested scopes over-approximate locals)."""
    local = {a.arg for a in fn.args.args + fn.args.kwonlyargs + fn.args.posonlyargs}
    for a in (fn.args.vararg, fn.args.kwarg):
        if a:
            local.add(a.arg)
    loads, forced = set(), set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Name):
            (loads if isinstance(n.ctx, ast.Load) else local).add(n.id)
        elif isinstance(n, ast.Global):
            forced |= set(n.names)
        elif isinstance(n, ast.arg):
            local.add(n.arg)
        elif isinstance(n, ast.FunctionDef) and n is not fn:
            local.add(n.name)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            local.add(n.name)
    return (loads - local) | forced


T_MOD_BOUND, S_MOD_BOUND = _mod_bound(T_TREE), _mod_bound(S_TREE)
S_FUNCS = {n.name for n in S_TREE.body if isinstance(n, ast.FunctionDef)}
CALLED = sorted({f.id for n, nm, f in _calls(T_TREE)
                 if isinstance(f, ast.Name) and f.id in S_FUNCS})
_FREE = set()
for _fn in S_TREE.body:
    if isinstance(_fn, ast.FunctionDef) and _fn.name in CALLED:
        _FREE |= _free_globals(_fn)
_FREE -= set(dir(_bi))
# the only globals of a certified function the tail may REBIND are the walker
# globals it swaps for cutwA and restores (L220's own convention)
_WALK = {"START", "END", "L_L", "T_L", "NL", "N_POOL", "POOLS_IDX"}
REDEF = sorted(T_MOD_BOUND & S_MOD_BOUND)                  # all module-level rebinds
CRIT = sorted((T_MOD_BOUND & _FREE) - _WALK)
assert not CRIT, (CRIT, CALLED, "tail rebinds a global a certified function reads (STOP)")
assert set(REDEF) - (_FREE | _WALK) == set(REDEF) - _WALK, "unreachable"

# (v) the slice must be WRITE-FREE (structural): no dump/save/mkdir and no
# write-mode open -> "the slice wrote nothing" holds by construction and is
# re-measured at runtime by the fingerprint gate
_sbad = _mut_sites(S_TREE)
assert not _sbad and sum(1 for n, nm, f in _calls(S_TREE) if nm == "dump") == 0, \
    (_sbad, "the slice mutates something (STOP)")
_so = _opens(S_TREE)
assert not [x for x in _so if any(c in x[1] for c in "wax+")], \
    ([x for x in _so if any(c in x[1] for c in "wax+")], "the slice opens a file for writing (STOP)")

# ---- assemble --------------------------------------------------------------
OUT = pathlib.Path("l238_static.py")
OUT.write_bytes(SLICE + T_BYTES)
G = OUT.read_bytes()
assert G == SLICE + T_BYTES and G.endswith(T_BYTES) and G.startswith(SLICE)
assert hashlib.sha256(G[:len(SLICE)]).hexdigest() == S_SHA
N_G = G.count(b"\n")
_g = ast.parse(G.decode())
_imp = set()
for n in ast.walk(_g):
    if isinstance(n, ast.Import):
        _imp |= {a.name.split(".")[0] for a in n.names}
    elif isinstance(n, ast.ImportFrom) and n.module:
        _imp.add(n.module.split(".")[0])
assert not (_imp & {"l220_static", "l220_tail", "l238_tail", "brain", "serve",
                    "bridge", "senses", "mood"}), (_imp, "L175: a lab/live module is IMPORTED (STOP)")
_ = _imp  # the generated file imports: see the printed set below
_gw = _mut_sites(_g)
assert _gw == [] and sum(1 for n, nm, f in _calls(_g) if nm == "dump") == 1, \
    (_gw, "generated file must carry exactly the tail's ONE dump (STOP)")

print(f"[l238_build] wrote l238_static.py {N_G} lines sha256 {hashlib.sha256(G).hexdigest()}")
print(f"[l238_build] SLICE = l220_static.py 1-{N_SLICE} VERBATIM sha256 {S_SHA[:16]} "
      f"(parent whole-file {P_WHOLE[:16]}, 2007 lines) | CUT {len(P_LINES) - N_SLICE} lines "
      f"sha256 {C_SHA[:16]} (inside l220_tail.py = parent lines {K_TAIL}-2007, {N_TAIL} lines)")
print(f"[l238_build] PARENT PIN = l220_tail.py sha256 {PT_SHA[:16]} recorded in the "
      f"parent's own banner AND a literal SUFFIX of it")
print(f"[l238_build] TAIL = l238_tail.py sha256 {T_SHA[:16]} ({N_T} lines) | ONE dump + ONE "
      f"write-mode open -> l238/static.json | 0 other mutation calls")
print(f"[l238_build] AST name audit: {len(T_MOD_LOADS)} module-level names loaded by the tail, "
      f"0 unresolved (0 inside functions too); certified functions called {CALLED} read "
      f"{len(_FREE)} globals; tail rebinds of them = {sorted(T_MOD_BOUND & _FREE)} (walker swap only)")
print(f"[l238_build] SLICE write-free: 0 dump/save/mkdir, 0 write-mode opens "
      f"({len(_so)} read-mode opens: {sorted(set(x[0] for x in _so))})")
print(f"[l238_build] generated-file imports: {sorted(_imp)}")
