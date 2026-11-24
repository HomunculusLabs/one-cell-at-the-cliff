"""L223b BUILD — the POST-HOC addendum, as a literal PREFIX of the parent.

l223b_static.py = l223_static.py lines 1-819 VERBATIM (the prefix ends right
after the Q223-3 companion rank values are computed, so PCT_LOG_* and
PC_RANK_* are in scope and every L223 gate re-runs for free) with EXACTLY ONE
declared modification: the inherited V_DEGENERATE escape at lines 432-436,
whose json.dump writes the PARENT's artifact, is replaced by a halting assert
(SPR was MEASURED at 4.11e-16, so the branch is unreachable anyway).  After
that substitution the prefix contains ZERO writes, which is asserted here.

Then l223b_tail.py, which writes ONLY l223/addendum.json.
"""
import hashlib
import os

LAB = "/home/t3rpz/critters/peabrain-lab/banc"
PARENT = f"{LAB}/l223_static.py"
PARENT_SHA = "d1b06d9df0df2582"
CUT = 818


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


whole = open(PARENT).read()
assert sha(whole) == PARENT_SHA, (sha(whole), "PARENT SHA MOVED (STOP)")
lines = whole.split("\n")
pre = "\n".join(lines[:CUT]) + "\n"
assert pre in whole, "prefix is not a literal substring (STOP)"

ESC = ('if SPR >= 1e-6:\n'
       '    o["branch"] = "V_DEGENERATE"\n'
       '    o["degenerate_reason"] = f"power iteration rel spread {SPR}"\n'
       '    json.dump(o, open(f"{OUT}/static.json", "w"), indent=1)\n'
       '    sys.exit("V_DEGENERATE: power iteration did not converge")\n')
REPL = ('# ===== L223b DECLARED MODIFICATION (replaces the inherited escape)\n'
        '# the parent escape WRITES l223/static.json; this addendum must never\n'
        '# touch it.  SPR was MEASURED at 4.11e-16, so a halting assert is\n'
        '# strictly stronger and writes nothing.\n'
        'assert SPR < 1e-6, (SPR, "power iteration did not converge (STOP)")\n')
assert pre.count(ESC) == 1, (pre.count(ESC), "escape block not found once (STOP)")
pre = pre.replace(ESC, REPL)

# the parent's OUT is l223; the addendum needs that name but must not write it
pre += ('\n# ===== L223b INJECT (1 line): alias the parent OUT for the guard\n'
        'OUTB = OUT\n')

assert "json.dump" not in pre, "PREFIX STILL CONTAINS A WRITE (STOP)"
assert 'open(f"{OUT}/static.json", "w")' not in pre, "prefix write (STOP)"
for m in ("CERT-212", "CERT-PAIR", "CERT-RANK", "Q223_0_rho_first",
          "PC_RANK_MIR, CR_MIR, CRV_M = crank_pct", 'o["branch"] = BRANCH223'):
    assert m in pre, (m, "prefix lost a required block (STOP)")
for m in ('o["predictions"] = P', 'o["limitations"]', 'o["runtime_s"]',
          "Q223_4_descriptive"):
    assert m not in pre, (m, "prefix reaches past its cut (STOP)")

tail = open(f"{LAB}/l223b_tail.py").read()
for n in ("def rankvec(", "def pct_of(", "def spearman_l(", "def crank_pct(",
          "def clog_vec(", "def Rfast("):
    assert n not in tail, (n, "addendum RE-TRANSCRIBES inherited source (STOP)")
assert tail.count("json.dump") == 1 and "addendum.json" in tail

out = pre + tail
assert out.count("json.dump") == 1, (out.count("json.dump"), "write count (STOP)")
assert "static.json\", \"w\"" not in out, "a static.json write survived (STOP)"
for f in ("systemctl", "sessions/", "serve.py", "bridge.py", "subprocess",
          "os.remove", "shutil", "LANE.md"):
    assert f not in out, (f, "FORBIDDEN TOKEN (STOP)")

dst = f"{LAB}/l223b_static.py"
open(dst, "w").write(out)
print(f"[build] prefix = l223_static.py lines 1-{CUT} (parent sha {PARENT_SHA})")
print(f"[build] wrote {dst} ({len(out)} bytes, {out.count(chr(10))} lines)")
print(f"[build] generated sha256 {sha(out)}")
