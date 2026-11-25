"""l229_build.py — generate l229_static.py from certified verbatim slices.

l229_static.py = HEAD1 : l151_static.py lines 1-319      (BYTE-FOR-BYTE)
               + PRE   : the single hand-written `o = {...}` seam
               + HEAD2 : l178_tail.py lines 22-83          (BYTE-FOR-BYTE)
               + HEAD3 : l215_tail.py lines 1-164          (BYTE-FOR-BYTE)
               + HEAD4 : l169b2_verdict.py lines 13-63     (BYTE-FOR-BYTE)
               + TAIL  : l229_tail.py

HEAD1/HEAD2 sha256[:16] are asserted against the values L215's OWN generated
banner recorded; HEAD4's against the value L208's banner recorded. HEAD3 is
additionally PARENT-PINNED: l215_tail.py's whole-file sha must equal the TAIL
sha in l215_static.py's banner AND be a literal SUFFIX of l215_static.py,
which is what proves the inherited slice is the code that actually produced
l215/static.json (the L226/L228 pattern). No lab module is imported (L175) —
every slice is read as TEXT and the generated script is AST-audited.

PREREG l229/PREREG.md (registered BEFORE this file existed).
"""
import ast
import hashlib
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "l229_static.py"

# ---- inherited sha pins, as RECORDED BY THE PARENTS' OWN BANNERS ----------
INHERIT = {
    "head1": "e6245e8306dc8a0f",          # l215_static.py banner
    "head2": "66112b0c221d02d8",          # l215_static.py banner
    "head3_parentfile": "dbc507e8f48530ae",  # l215_static.py banner (TAIL)
    "head4": "de636f4a18ee789b",          # l208_static.py banner
}

h1_text = (HERE / "l151_static.py").read_text()
h1_lines = h1_text.splitlines(keepends=True)
N_H1 = 319
assert len(h1_lines) >= N_H1, "l151_static.py too short (STOP)"
head1 = "".join(h1_lines[:N_H1])
assert h1_text.startswith(head1), "HEAD1 is not a literal PREFIX (STOP)"

h2_text = (HERE / "l178_tail.py").read_text()
h2_lines = h2_text.splitlines(keepends=True)
H2_LO, H2_HI = 22, 83
head2 = "".join(h2_lines[H2_LO - 1:H2_HI])
assert head2 in h2_text, "HEAD2 is not a literal slice (STOP)"

h3_text = (HERE / "l215_tail.py").read_text()
h3_lines = h3_text.splitlines(keepends=True)
H3_HI = 164
head3 = "".join(h3_lines[:H3_HI])
assert h3_text.startswith(head3), "HEAD3 is not a literal PREFIX (STOP)"
assert head3.startswith("# ================= L215 TAIL"), "HEAD3 head drift"
assert head3.rstrip().endswith(
    "return (float(v[v > 0].sum()), float(-v[v < 0].sum()), int(sel.sum()))"), \
    "HEAD3 last line drift (STOP)"

h4_text = (HERE / "l169b2_verdict.py").read_text()
h4_lines = h4_text.splitlines(keepends=True)
H4_LO, H4_HI = 13, 63
head4 = "".join(h4_lines[H4_LO - 1:H4_HI])
assert head4 in h4_text, "HEAD4 is not a literal slice (STOP)"
assert head4.startswith("WIN, DT = 6000, 0.01\n"), "HEAD4 first line drift"
assert head4.rstrip().endswith(
    "meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))"), \
    "HEAD4 last line drift (STOP)"

sh = {k: hashlib.sha256(v.encode()).hexdigest()
      for k, v in (("head1", head1), ("head2", head2), ("head3", head3),
                   ("head4", head4))}
sh["head3_parentfile"] = hashlib.sha256(h3_text.encode()).hexdigest()
for k, want in INHERIT.items():
    if k == "head3":
        continue
    assert sh[k].startswith(want), (k, sh[k][:16], want, "inherited sha (STOP)")
print("inherited sha pins GREEN:", {k: v[:16] for k, v in sh.items()})

# ---- PARENT PIN: l215_tail.py is a literal SUFFIX of l215_static.py ------
parent_static = (HERE / "l215_static.py").read_text()
assert parent_static.endswith(h3_text), \
    "l215_tail.py is NOT a literal suffix of l215_static.py (STOP)"
assert f"TAIL  = l215_tail.py (sha256 {sh['head3_parentfile'][:16]})" \
    in parent_static, "l215_static.py banner TAIL sha disagrees (STOP)"
print("PARENT PIN GREEN: HEAD3's source file is the code that produced "
      "l215/static.json")

# ---- HEAD3 LINE-SET AUDIT: the CUT lines own L215's measurement + writer --
cut3 = "".join(h3_lines[H3_HI:])
assert len(h3_lines) == 402, (len(h3_lines), "l215_tail.py line count (STOP)")
assert len(cut3.splitlines()) == 402 - H3_HI
for owned in ("ROWS = {}", "Q1 = dict(", "json.dump(", "o[\"branch\"] = "):
    assert owned in cut3, ("CUT must own", owned, "(STOP)")
    assert owned not in head3, ("slice must NOT contain", owned, "(STOP)")
print(f"HEAD3 line-set audit GREEN: slice = lines 1-{H3_HI} of 402; the "
      f"{402 - H3_HI} cut lines own L215's ROWS loop, Q-blocks and writer")

# ---- write-token audit on every slice (L205's certified list) ------------
FORBIDDEN = ('"w"', "'w'", "import l1", "import l9", "savez", "to_csv",
             "json.dump", "write_text", "os.replace")
for name, blob in (("HEAD1", head1), ("HEAD2", head2), ("HEAD3", head3),
                   ("HEAD4", head4)):
    for bad in FORBIDDEN:
        assert bad not in blob, (name, "forbidden token", bad, "(STOP)")
print("write-token audit on all four slices: clean")

PRE = (
    "\n# ---- L229 PRE (the only hand-written lines between certified"
    " slices):\n"
    "# HEAD2 writes o['cert_f4'] and o['gains'], so the dict must exist"
    " first.\n"
    "# (Inherited verbatim from l215_build.py's own PRE seam; the design\n"
    "#  string is overwritten by the L229 tail before the single write.)\n"
    "o = {\"design\": \"L229 near-balance population question (static)\",\n"
    "     \"prereg\": \"l229/PREREG.md\"}\n\n")

tail = (HERE / "l229_tail.py").read_text()
sh["tail"] = hashlib.sha256(tail.encode()).hexdigest()

preamble = (
    '"""GENERATED by l229_build.py — do not edit by hand.\n'
    f"HEAD1 = l151_static.py lines 1-{N_H1} VERBATIM (sha256 "
    f"{sh['head1'][:16]}).\n"
    f"HEAD2 = l178_tail.py lines {H2_LO}-{H2_HI} VERBATIM (sha256 "
    f"{sh['head2'][:16]}).\n"
    f"HEAD3 = l215_tail.py lines 1-{H3_HI} VERBATIM (sha256 "
    f"{sh['head3'][:16]}; parent file {sh['head3_parentfile'][:16]}).\n"
    f"HEAD4 = l169b2_verdict.py lines {H4_LO}-{H4_HI} VERBATIM (sha256 "
    f"{sh['head4'][:16]}).\n"
    f"TAIL  = l229_tail.py (sha256 {sh['tail'][:16]}).\n"
    "PREREG l229/PREREG.md. Writes l229/static.json ONLY.\n"
    '"""\n')

written = preamble + head1 + PRE + head2 + "\n\n" + head3 + "\n\n" + \
    head4 + "\n\n" + tail
OUT.write_text(written)
sh["generated"] = hashlib.sha256(written.encode()).hexdigest()

# ---- AST audits on the GENERATED script ---------------------------------
tree = ast.parse(written)
imports = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imports.update(a.name for a in node.names)
    elif isinstance(node, ast.ImportFrom):
        imports.add(node.module or "")
for m in sorted(imports):
    assert not m.startswith(("l1", "l2", "l9")), ("lab module imported", m)
print("AST import audit GREEN (L175):", sorted(imports))

writes = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        f = node.func
        nm = (f.attr if isinstance(f, ast.Attribute) else
              (f.id if isinstance(f, ast.Name) else ""))
        if nm in ("open", "dump", "savez", "savez_compressed", "write_text",
                  "to_csv", "replace"):
            lit = [a.value for a in node.args
                   if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            mode = [a.value for a in node.args[1:]
                    if isinstance(a, ast.Constant)]
            writes.append((nm, lit, mode, node.lineno))
# A single `json.dump(o, open(p, "w"))` is TWO Call nodes on ONE line; the
# audit counts write SITES, asserts each category exactly once, and asserts
# they coincide (so the dump cannot target a second, unaudited handle).
opens_w = [w for w in writes if w[0] == "open" and any(m == "w" for m in w[2])]
dumps = [w for w in writes if w[0] == "dump"]
others = [w for w in writes
          if w[0] in ("savez", "savez_compressed", "write_text", "to_csv",
                      "replace")]
assert others == [], ("unexpected write-class call", others)
assert len(opens_w) == 1, ("expected exactly ONE open(...,'w')", opens_w)
assert len(dumps) == 1, ("expected exactly ONE json.dump", dumps)
assert opens_w[0][1][0] == "l229/static.json", opens_w
assert opens_w[0][3] == dumps[0][3], ("dump and open are not the same site",
                                      opens_w, dumps)
print(f"AST write audit GREEN: exactly ONE write site, l229/static.json "
      f"(line {opens_w[0][3]}); no savez/to_csv/write_text/os.replace")

print(f"wrote {OUT} ({len(written.splitlines())} lines)")
for k, v in sh.items():
    print(f"  {k} sha256 {v}")
