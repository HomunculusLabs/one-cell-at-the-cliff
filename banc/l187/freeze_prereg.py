"""L187: stamp the current file shas into PREREG.md and write PREREG.sha256.
Run from banc/ BEFORE any rollout (refuses if a raw npz exists)."""
import glob
import hashlib
import time

assert not glob.glob("l187/raw_w*.npz"), "rollouts exist — PREREG is frozen"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


p = "l187/PREREG.md"
s = open(p).read()


def sub1(old, new):
    global s
    assert s.count(old) == 1, (old[:40], s.count(old))
    s = s.replace(old, new)


sub1("8723bc88e2d6", sha("l187/relay_run.py")[:12])
sub1("0acf20d30c44", sha("l187/verdict_l187.py")[:12])
sub1("f79e0e47378b", sha("l187/verdict_tail.py.txt")[:12])
assert sha("l187/build_relay.py")[:12] == "d786df71ec17"
sub1("  cell's x_mean must be exactly 0; the full-window maximum is reported.\n",
     "  cell's x_mean must be exactly 0; the full-window maximum is reported.\n"
     "  A failure voids `rsilF` only (reported, not read); `rsilW` rests on FC-150.\n")
open(p, "w").write(s)
assert open("l187/relay_run.py").read().count("\n") == 1765
files = ["PREREG.md", "relay_run.py", "build_relay.py", "arms_block.py.txt",
         "gains_block.py.txt", "tail_block.py.txt", "verdict_l187.py",
         "verdict_tail.py.txt", "build_verdict.py", "run_all.sh", "static.json",
         "L185_DONE.txt"]
with open("l187/PREREG.sha256", "w") as f:
    for n in files:
        f.write(f"{sha('l187/' + n)}  {n}\n")
    f.write(f"frozen {time.strftime('%F %T %Z')} before any rollout\n")
print(open("l187/PREREG.sha256").read())
