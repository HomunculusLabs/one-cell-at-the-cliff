"""l239_build.py — generate l239_static.py = l220_static.py lines 1-1587
VERBATIM + l239_tail.py with nine verbatim L220 blocks spliced in at markers.

The slice is the parent's prefix: the certified slices of the L151 -> L178 ->
L206 -> L207 -> L211 chain AND L220's body up to the end of its cutwA build
(IX_CUT), cut at the blank line before L220's edge->CSR maps. So every parent
gate before that point re-runs as free certification (CERT-239A).

The cut region (L220 lines 1588-2007) owns L220's draws / null / cohort /
writer. This card re-runs the pieces it needs FROM THE PARENT'S OWN BYTES
(blocks below, each asserted a literal substring of the parent) and adds its
own measurement + its ONE write.

Every pin below is DERIVED from stored bytes at build time (L228: derive,
never retype) and printed. Every audit is STRUCTURAL (AST), never a bare-token
scan (L226/L227). PREREG l239/PREREG.md (registered first).
"""
import ast
import builtins as _bi
import hashlib
import pathlib

N_SLICE = 1587

# ---- parent: lines split on b"\\n" ONLY --------------------------------------
P_SRC = pathlib.Path("l220_static.py")
P_BYTES = P_SRC.read_bytes()
assert b"\r" not in P_BYTES, "parent has a CR (STOP)"
assert P_BYTES.endswith(b"\n"), "parent must end in a newline (STOP)"
P_LINES = P_BYTES[:-1].split(b"\n")
assert len(P_LINES) == 2007, (len(P_LINES), "parent line count moved (STOP)")
SLICE = b"\n".join(P_LINES[:N_SLICE]) + b"\n"
CUT = b"\n".join(P_LINES[N_SLICE:]) + b"\n"
assert SLICE + CUT == P_BYTES, "slice + cut is not the parent (STOP)"
P_WHOLE = hashlib.sha256(P_BYTES).hexdigest()[:16]
S_SHA = hashlib.sha256(SLICE).hexdigest()[:16]
C_SHA = hashlib.sha256(CUT).hexdigest()[:16]

# ---- boundary -----------------------------------------------------------------
assert P_LINES[N_SLICE] == b"", ("line 1588 is not the blank line (STOP)",)
assert P_LINES[N_SLICE + 1].startswith(b"# ---------------- global edge -> cutwA CSR"), \
    "line 1589 is not L220's edge->CSR header (STOP)"
assert P_LINES[N_SLICE - 1].rstrip().endswith(b"IX_CUT['AMAX']:.6f}\")"), \
    "line 1587 is not the end of the cutwA-built log (STOP)"


def lines(a, b):
    """1-indexed inclusive, exactly as slice_lines() defines it"""
    return b"\n".join(P_LINES[a - 1:b]) + b"\n"


def indent(block):
    return b"\n".join((b"    " + l) if l else l for l in block[:-1].split(b"\n")) + b"\n"


def first(a, text):
    assert P_LINES[a - 1].startswith(text), (a, P_LINES[a - 1][:90], "boundary (STOP)")


def free_names(func_src):
    """names a function LOADS without binding (params/locals excluded)"""
    _t = ast.parse(func_src)
    _fn = _t.body[0]
    assert isinstance(_fn, ast.FunctionDef)
    _st, _ld = set(), set()
    for _n in ast.walk(_fn):
        if isinstance(_n, ast.Name):
            (_st if isinstance(_n.ctx, (ast.Store,)) else _ld).add(_n.id)
        elif isinstance(_n, (ast.FunctionDef, ast.Lambda, ast.comprehension)):
            _args = getattr(_n, "args", None)
            if _args is not None:
                for _a in _args.args + _args.kwonlyargs:
                    _st.add(_a.arg)
                if _args.vararg:
                    _st.add(_args.vararg.arg)
    _out = sorted(_ld - _st - set(dir(_bi)))
    return _out


# ---- PARENT PIN: the parent's own banner records its tail's sha --------------
BANNER = b"\n".join(P_LINES[:13]).decode()
PT_BYTES = pathlib.Path("l220_tail.py").read_bytes()
PT_SHA = hashlib.sha256(PT_BYTES).hexdigest()
_bl = [l for l in BANNER.split("\n") if "l220_tail.py" in l]
assert len(_bl) == 1 and f"sha256 {PT_SHA[:16]}" in _bl[0], \
    (_bl, PT_SHA[:16], "banner does not record this tail (STOP)")
assert P_BYTES.endswith(PT_BYTES), "l220_tail.py is not a literal SUFFIX (STOP)"
K_TAIL = len(P_LINES) - PT_BYTES.count(b"\n") + 1
assert K_TAIL == 1410 and K_TAIL <= N_SLICE + 1, (K_TAIL, "tail does not own the whole cut (STOP)")
assert "PREREG l220/PREREG.md. Writes l220/static.json ONLY." in BANNER

# ---- the nine blocks, each a literal of the parent ----------------------------
B = {}
B["EDGE_MAPS"] = lines(1590, 1603)
first(1590, b"_ei_cut = np.where(emask_wA)[0]")
first(1603, b'    "cutwA edge->CSR map (STOP)"')
B["REWCUT"] = lines(1609, 1627)
first(1609, b"DRAWS_CUT = rewire_draws(_blk_wA")
first(1627, b'    f"cutwA SI null is the l169c NATIVE null')
B["REBIND"] = lines(1668, 1671)
first(1668, b"START, END, L_L, T_L = (IX_CUT[")
first(1671, b"TGT0_CUT = IX_CUT[")
B["CARNULL"] = lines(1648, 1707)
first(1648, b"_cb0c, _cb1c = IX_CUT[")
first(1707, b'    f"certified dijkstra_si and the first-hop walker (carrier + 100 draws)")')
B["COHORT"] = lines(1710, 1725)
first(1710, b"COH_CUT, _absent = {}, []")
first(1725, b"    COH_CUT[_nm] = fh_summary(_d, _s, _f, _h)")
B["RESTORE"] = lines(1728, 1729)
first(1728, b"START, END, L_L, T_L = _START0, _END0, _L0, _T0")
first(1729, b"NL, N_POOL, POOLS_IDX = _NL0, _NP0, _PI0")

# CH builder: L220's changed-list loop as a function body (+1 indent)
_ch = lines(1631, 1645)
first(1631, b"for _d in DRAWS_CUT:")
first(1645, b"    CH_CUT.append(dict(n_changed=len(_ch), changed=_ch))")
B["CH_FN"] = (b"def _build_ch239(DRAWS_CUT):\n    CH_CUT = []\n"
              + indent(_ch) + b"    assert len(CH_CUT) == 100\n    return CH_CUT\n")

# L220's cohort block with its assignment target renamed (nothing else)
first(1875, b"_famc = [v for k, v in COH_CUT.items()")
assert P_LINES[1880] == b'o["L220_cohort"] = dict(', ("line 1881 (STOP)", P_LINES[1880][:60])
first(1882, b"    note=(")
first(1910, b"    all_actors=COH_CUT)")
B["L220COH"] = lines(1875, 1880) + b"L220_COH_R = dict(\n" + lines(1882, 1910)

# L220's decomposition as a function body: ONE token changed (the target)
_dc = lines(1742, 1813)
first(1742, b"SHARE_HI_220, SHARE_LO_220 = 0.60, 0.40")
assert P_LINES[1772] == b'o["L220_primary"] = dict(', ("line 1773 (STOP)", P_LINES[1772][:60])
first(1813, b'                   operator="g=1 anatomical |W_beta| (PREREG 0c)"))')
assert _dc.count(b'o["L220_primary"] = dict(') == 1
_dc = _dc.replace(b'o["L220_primary"] = dict(', b"L220_PRIM_R = dict(")
B["DECOMP_FN"] = (b"def _decomp239(CAR_CUT, NULL_CUT, N_OUT_CUT_PIN, LOG2_OUT_CUT, "
                  b"_menu_cut, _relocc):\n" + indent(_dc) + b"    return L220_PRIM_R\n")
# the two wrapped functions may touch NOTHING actor-specific beyond their args
_fr_ch = free_names(B["CH_FN"].decode())
assert _fr_ch == ["SUB_CUT", "_eipos_cut", "_pos_in_csr_cut", "dst_all"], _fr_ch
_fr_dc = free_names(B["DECOMP_FN"].decode())
assert _fr_dc == ["IX_CUT", "SUB_CUT", "_pct", "np"], _fr_dc
# every unmodified block is a literal of the parent
for _k, _v in B.items():
    if _k not in ("CH_FN", "DECOMP_FN", "L220COH"):
        assert _v in P_BYTES, (_k, "not a literal of the parent (STOP)")
assert lines(1875, 1880) in P_BYTES and lines(1882, 1910) in P_BYTES
assert _ch in P_BYTES and lines(1742, 1813) in P_BYTES
print(f"[build] parent sha {P_WHOLE} | slice 1-{N_SLICE} sha {S_SHA} | cut sha {C_SHA}")
print(f"[build] tail-of-parent starts line {K_TAIL} (sha {PT_SHA[:16]}), owns the whole cut")
for _k in ("EDGE_MAPS", "REWCUT", "CH_FN", "REBIND", "CARNULL", "DECOMP_FN", "COHORT", "L220COH", "RESTORE"):
    print(f"[build]   block {_k:10s} {len(B[_k].split(b'\n')) - 1:4d} lines sha {hashlib.sha256(B[_k]).hexdigest()[:16]}")
print(f"[build]   free names: _build_ch239 {_fr_ch} | _decomp239 {_fr_dc}")

# ---- splice the markers ------------------------------------------------------
TAIL_SRC = pathlib.Path("l239_tail.py").read_bytes()
assert b"\r" not in TAIL_SRC and TAIL_SRC.endswith(b"\n")
T_LINES = TAIL_SRC[:-1].split(b"\n")
OUT_LINES = list(P_LINES[:N_SLICE])
_i = 0
while _i < len(T_LINES):
    _l = T_LINES[_i]
    if _l.startswith(b"#@@") and _l.endswith(b"@@"):
        _k = _l[3:-2].decode()
        assert _k in B, (_k, "unknown marker (STOP)")
        OUT_LINES += B[_k][:-1].split(b"\n")
    else:
        assert b"#@@" not in _l, (_l, "stray marker text (STOP)")
        OUT_LINES.append(_l)
    _i += 1
OUT = b"\n".join(OUT_LINES) + b"\n"
assert OUT.startswith(SLICE), "the head is not the parent's prefix (STOP)"
assert b"#@@" not in OUT[N_SLICE:], "a marker survived (STOP)"

# ---- STRUCTURAL audits on the generated file ----------------------------------
TREE = ast.parse(OUT.decode())


def audit(src):
    _ks, _wr, _ims = set(), [], set()
    for _n in ast.walk(ast.parse(src)):
        if isinstance(_n, ast.Assign) and len(_n.targets) == 1:
            _tg = _n.targets[0]
            if (isinstance(_tg, ast.Subscript) and isinstance(_tg.value, ast.Name)
                    and _tg.value.id == "o" and isinstance(_tg.slice, ast.Constant)
                    and isinstance(_tg.slice.value, str)):
                _ks.add(_tg.slice.value)
        if (isinstance(_n, ast.Call) and isinstance(_n.func, ast.Name)
                and _n.func.id == "open" and len(_n.args) >= 2
                and isinstance(_n.args[1], ast.Constant)
                and isinstance(_n.args[1].value, str)
                and any(_c in _n.args[1].value for _c in "wa+")):
            _wr.append((_n.lineno, "open"))
        if (isinstance(_n, ast.Call) and isinstance(_n.func, ast.Attribute)
                and _n.func.attr in ("dump", "save", "savez", "write_text",
                                     "write_bytes", "makedirs", "mkdir", "to_csv")):
            _wr.append((_n.lineno, _n.func.attr))
        if isinstance(_n, ast.Import):
            for _a in _n.names:
                _ims.add(_a.name.split(".")[0])
        if isinstance(_n, ast.ImportFrom) and _n.module:
            _ims.add(_n.module.split(".")[0])
    return _ks, _wr, _ims


K_SL, W_SL, I_SL = audit(SLICE.decode())
K_TL, W_TL, I_TL = audit(OUT[len(SLICE):].decode())
K_CUT, W_CUT, _ = audit(CUT.decode())
assert not W_SL, (W_SL, "the slice writes (STOP)")
assert sorted(a for _, a in W_TL) == ["dump", "makedirs", "open"], W_TL
assert sorted(a for _, a in W_CUT) == ["dump", "open"], W_CUT
_CARD_KEYS = {"design", "prereg", "certification", "limitations", "pins"}
assert (K_SL & K_TL) == {"design", "prereg"}, sorted(K_SL & K_TL)  # card identity, overwritten AFTER CERT-239A
assert not (K_SL & K_CUT), sorted(K_SL & K_CUT)
assert (K_TL & set(K_CUT)) == _CARD_KEYS - {"design", "prereg"}, sorted(K_TL & set(K_CUT))
assert K_SL == set(audit(OUT.decode())[0]) - (K_TL - {"design", "prereg"})
assert len(K_TL - set(K_CUT)) >= 12, len(K_TL - set(K_CUT))  # this card's own blocks
# L175: no lab module is imported (scripts re-run and rewrite their artifacts)
assert I_SL <= {"json", "time", "numpy", "pandas", "torch", "math", "heapq", "os"}, sorted(I_SL)
assert I_TL <= {"ast", "hashlib", "os"}, sorted(I_TL)
print(f"[build] slice: {len(K_SL)} o-keys, 0 write sites | tail: {len(K_TL)} o-keys "
      f"(all new), write sites {W_TL} | imports slice {sorted(I_SL)} tail {sorted(I_TL)}")

OUT_SHA = hashlib.sha256(OUT).hexdigest()[:16]
TAIL_SHA = hashlib.sha256(OUT[len(SLICE):]).hexdigest()[:16]
if pathlib.Path("l239_static.py").exists():
    _old = pathlib.Path("l239_static.py").read_bytes()
    print(f"[build] replacing an earlier l239_static.py (sha {hashlib.sha256(_old).hexdigest()[:16]})")
pathlib.Path("l239_static.py").write_bytes(OUT)
assert pathlib.Path("l239_static.py").read_bytes() == OUT
assert len(OUT.split(b"\n")) - 1 == N_SLICE + len(OUT[len(SLICE):].split(b"\n")) - 1
print(f"[build] WROTE l239_static.py {len(OUT):,} B, {len(OUT.split(bytes([10]))) - 1} lines")
print(f"[build]   static sha {OUT_SHA} | appended tail sha {TAIL_SHA} "
      f"(= l239_tail.py with 9 blocks spliced: {len(T_LINES)} source lines)")
