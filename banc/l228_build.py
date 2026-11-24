"""l228_build.py — generate l228_static.py from certified verbatim slices.

l228_static.py = banner
               + HEAD1 : l151_static.py lines 1-319   (BYTE-FOR-BYTE)
               + PRE   : the output dict `o`
               + HEAD2 : l178_tail.py lines 22-83     (BYTE-FOR-BYTE)
               + HEAD3 : l215_tail.py lines 1-157     (BYTE-FOR-BYTE)
               + TAIL  : l228_tail.py

HEAD1/HEAD2 are the SAME slices L205/L215 used and their sha256 are asserted
against the values l205_static.py's banner recorded (inherited-sha
discipline).  HEAD3 is NEW: it brings L215's whole certification block
(CERT-G 2, CERT-205 36, CERT-TBL 28, the substrate/pool pins and the L208
premise asserts) plus the SIDEMASK/GROUPS construction as SOURCE rather than
as a re-transcription (the L211 lesson).  HEAD3 is additionally PARENT-PINNED:
l215_tail.py must be a literal SUFFIX of l215_static.py and hash to the value
l215_static.py's own banner recorded, which is what proves the slice is the
code that actually produced l215/static.json (the L226 pattern).

Audits here are STRUCTURAL, never bare-token (the tick-248/251/256/257/258
trap): imports are checked with an ast walk over Import/ImportFrom nodes, and
HEAD3's exclusion of L215's measurement/writer is checked by an exact LINE-SET
assert plus ast-level checks, so a comment that merely NAMES a forbidden
construct cannot halt the build.

No lab module is imported (L175).  PREREG l228/PREREG.md.
"""
import ast
import hashlib
import pathlib

H1_SRC = pathlib.Path("l151_static.py")
H2_SRC = pathlib.Path("l178_tail.py")
H3_SRC = pathlib.Path("l215_tail.py")
H3_PARENT = pathlib.Path("l215_static.py")
TAIL_SRC = pathlib.Path("l228_tail.py")
OUT = pathlib.Path("l228_static.py")
N_H1 = 319
H2_LO, H2_HI = 22, 83          # 1-indexed inclusive
H3_LO, H3_HI = 1, 157          # 1-indexed inclusive

# sha256[:16] as RECORDED BY the generated banners of L205 / L215 — inherited
INHERIT = {"head1": "e6245e8306dc8a0f", "head2": "66112b0c221d02d8"}
H3_PARENT_SHA16 = "dbc507e8f48530ae"     # l215_static.py's banner, TAIL line

# ---------------- HEAD1 ----------------------------------------------------
h1_text = H1_SRC.read_text()
h1_lines = h1_text.splitlines(keepends=True)
assert len(h1_lines) >= N_H1, (len(h1_lines), "l151_static.py too short")
head1 = "".join(h1_lines[:N_H1])
assert h1_text.startswith(head1), "HEAD1 slice is not a literal prefix"

# ---------------- HEAD2 ----------------------------------------------------
h2_text = H2_SRC.read_text()
h2_lines = h2_text.splitlines(keepends=True)
assert len(h2_lines) >= H2_HI, (len(h2_lines), "l178_tail.py too short")
head2 = "".join(h2_lines[H2_LO - 1:H2_HI])
assert head2 in h2_text, "HEAD2 slice is not a literal slice"
assert head2.startswith("FLOOR = 4\n"), head2[:40]
assert head2.rstrip().endswith("del _z"), head2[-60:]

sh = {k: hashlib.sha256(v.encode()).hexdigest()
      for k, v in (("head1", head1), ("head2", head2))}
for k, want in INHERIT.items():
    assert sh[k][:16] == want, (k, sh[k][:16], want, "INHERITED SHA DRIFT (STOP)")
print("inherited sha pins GREEN:", INHERIT)

# ---------------- HEAD3 + the PARENT PIN -----------------------------------
h3_text = H3_SRC.read_text()
h3_full_sha = hashlib.sha256(h3_text.encode()).hexdigest()
assert h3_full_sha[:16] == H3_PARENT_SHA16, (
    h3_full_sha[:16], H3_PARENT_SHA16, "l215_tail.py SHA DRIFT (STOP)")
parent_text = H3_PARENT.read_text()
assert parent_text.endswith(h3_text), (
    "l215_tail.py is NOT a literal SUFFIX of l215_static.py (STOP)")
print(f"PARENT PIN GREEN: l215_tail.py sha {h3_full_sha[:16]} is a literal "
      f"suffix of l215_static.py")

h3_lines = h3_text.splitlines(keepends=True)
assert len(h3_lines) >= H3_HI, (len(h3_lines), "l215_tail.py too short")
head3 = "".join(h3_lines[H3_LO - 1:H3_HI])
assert head3 in parent_text, "HEAD3 slice is not a literal slice of the parent"
assert head3.startswith("# ================= L215 TAIL"), head3[:60]
assert head3.rstrip().endswith('f"L215 statistic")'), head3[-60:]
sh["head3"] = hashlib.sha256(head3.encode()).hexdigest()

# HEAD3 must carry the certification machinery ...
for good in ("[CERT-G]", "[CERT-205]", "[CERT-TBL]", "SIDEMASK[(J, side)]",
             "GROUPS[(J, g)]", 'S208["branch"] == "H_UNREGISTERED_SHAPE"'):
    assert good in head3, ("HEAD3 lost certified machinery", good)
# ... and NONE of L215's own measurement or writer.  STRUCTURAL: the slice is
# asserted to be EXACTLY the first H3_HI lines, and the parent's measurement /
# writer lines are asserted to live OUTSIDE that line set (an exact line-set
# assert, not a token scan -- tick 258's repair).
h3_cut = h3_lines[H3_HI:]
_cut_text = "".join(h3_cut)
for owned_by_cut in ("def signed_in(", "ROWS = {}", "Q4 = {}",
                     'o["branch"] = BRANCH', "json.dump(o,"):
    assert owned_by_cut in _cut_text, ("expected in the CUT region",
                                       owned_by_cut)
    assert owned_by_cut not in head3, ("HEAD3 contains cut machinery",
                                       owned_by_cut)
print(f"HEAD3 line-set audit GREEN: {len(h3_lines)} lines, slice 1-{H3_HI}, "
      f"{len(h3_cut)} lines cut (measurement + writer)")

# ---------------- AST import audit over every slice + the tail -------------
tail = TAIL_SRC.read_text()
sh["tail"] = hashlib.sha256(tail.encode()).hexdigest()

BANNED_MODULE_PREFIXES = ("l1", "l2", "l9")


def _is_lab_module(root):
    """lab modules are named l<digit>... (l151_static, l178_tail, l92_x)."""
    return len(root) >= 2 and root[0] == "l" and root[1].isdigit()


def _imported_names(src, label):
    names = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    for nm in names:
        root = nm.split(".")[0]
        assert not _is_lab_module(root), (label, nm,
                                          "LAB MODULE IMPORT (L175) (STOP)")
    return names


for label, blob in (("HEAD1", head1), ("HEAD2", head2), ("HEAD3", head3),
                    ("TAIL", tail)):
    _imported_names(blob, label)
print("AST import audit GREEN (no lab module imported, L175)")

# ---------------- write-token audit: the TAIL owns the only write ----------
def _write_calls(src, label):
    n = 0
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call):
            f = node.func
            nm = getattr(f, "attr", None) or getattr(f, "id", None)
            if nm == "open":
                mode = None
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    mode = node.args[1].value
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        mode = kw.value.value
                if mode is None:
                    mode = "r"
                if any(c in mode for c in "wax+"):
                    n += 1
                    assert label == "TAIL", (label, "WRITE outside the tail")
            if nm in ("savez", "savez_compressed", "to_csv", "write_text"):
                assert label == "TAIL", (label, nm, "writer outside the tail")
            if (nm == "replace" and isinstance(f, ast.Attribute)
                    and isinstance(f.value, ast.Name) and f.value.id == "os"):
                assert label == "TAIL", (label, "os.replace outside the tail")
    return n


_nw = sum(_write_calls(b, lab) for lab, b in
          (("HEAD1", head1), ("HEAD2", head2), ("HEAD3", head3),
           ("TAIL", tail)))
assert _nw == 1, (_nw, "the generated script must have EXACTLY one write")
print("AST write audit GREEN: exactly 1 write (l228/static.json), in the tail")

# the tail must not re-transcribe the inherited certified machinery
for bad in ("def mass(", "pm4 = w_syn", "keep_f4 = keep_new",
            "CERT-205] GREEN", "CERT-TBL] GREEN"):
    assert bad not in tail, ("TAIL re-transcribes certified machinery", bad)

PRE = (
    "\n# ---- L228 PRE (the only hand-written lines between the certified"
    " slices):\n"
    "# HEAD2 writes o['cert_f4'] and o['gains'], so the dict must exist"
    " first.\n"
    "o = {\"design\": \"L228 depth-2 account of the dead-left-trochanter \"\n"
    "     \"resurrection (static): signed two-hop drive d2(P) = sum over \"\n"
    "     \"edges e into P of vals[e] * net_in(src[e]) on cutwA vs f4wA, \"\n"
    "     \"per side per joint, gain^2-scaled, against the same \"\n"
    "     \"sign-neutral counterfactual and the same membership null. \"\n"
    "     \"Zero rollouts, zero dynamics.\",\n"
    "     \"prereg\": \"l228/PREREG.md\"}\n\n")

banner = (
    '"""GENERATED by l228_build.py — do not edit by hand.\n'
    f"HEAD1 = l151_static.py lines 1-{N_H1} VERBATIM (sha256 {sh['head1'][:16]}).\n"
    f"HEAD2 = l178_tail.py lines {H2_LO}-{H2_HI} VERBATIM "
    f"(sha256 {sh['head2'][:16]}).\n"
    f"HEAD3 = l215_tail.py lines {H3_LO}-{H3_HI} VERBATIM "
    f"(sha256 {sh['head3'][:16]}); l215_tail.py whole-file "
    f"{h3_full_sha[:16]} == l215_static.py's banner AND a literal suffix "
    "of it.\n"
    f"TAIL  = l228_tail.py (sha256 {sh['tail'][:16]}).\n"
    'PREREG l228/PREREG.md. Writes l228/static.json ONLY.\n'
    '"""\n')

body = banner + head1 + PRE + head2 + head3 + tail
OUT.write_text(body)
written = OUT.read_text()
assert written == body
for name, blob in (("HEAD1", head1), ("HEAD2", head2), ("HEAD3", head3),
                   ("TAIL", tail)):
    assert blob in written, f"generated file lost {name}"
ast.parse(written)
gen_sha = hashlib.sha256(written.encode()).hexdigest()
print(f"wrote {OUT} ({len(written.splitlines())} lines)")
for k, v in sh.items():
    print(f"{k} sha256 {v}")
print(f"generated sha256 {gen_sha}")
