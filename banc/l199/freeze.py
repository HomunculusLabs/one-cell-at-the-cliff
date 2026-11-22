"""L199 freeze: key-scan the fresh seeds + tags against every lab npz, refuse if
any L199 raw/gains/result already exists, hash everything. Run from banc/."""
import glob, hashlib, json, os, re, time, zipfile

OUT = "l199"
BASE, TAGOFF = list(range(19931, 19947)), 50000
fresh = set(BASE) | {TAGOFF + b for b in BASE}
for pat in ("raw_w*.npz", "xm_w*.npz", "gains_w*.json", "anchors_w*.json", "done_w*.json", "results_*.json", "segduty_*.npz", "primary.out", "causal.out"):
    assert not glob.glob(f"{OUT}/{pat}"), ("L199 output exists before freeze (STOP)", pat)
nscan = 0
for f in sorted(glob.glob("../**/*.npz", recursive=True)):
    if f.startswith("../banc/l199/"):
        continue
    try:
        names = zipfile.ZipFile(f).namelist()
    except (zipfile.BadZipFile, FileNotFoundError, OSError):
        assert f.endswith(".tmp.npz"), ("unreadable npz (STOP)", f)
        continue
    nscan += 1
    for k in names:
        assert not (set(map(int, re.findall(r"\d+", k))) & fresh), ("fresh seed/tag token collides (STOP)", f, k)
# concurrent L200: no text file there may already name one of these seeds
l200_hits = [p for p in glob.glob("l200/*") if os.path.isfile(p) and not p.endswith(".npz")
             and (set(map(int, re.findall(r"\d+", open(p, errors="ignore").read()))) & fresh)]
assert not l200_hits, ("L200 names one of these seeds (STOP)", l200_hits)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FILES = ["PREREG.md", "ph.py", "selftest.py", "selftest.json", "analyze_primary.py", "analyze_causal.py",
         "build_tp.py", "run_tp.py", "run_all.sh", "freeze.py"]
frz = dict(prereg_sha256=sha(f"{OUT}/PREREG.md"), files={f: sha(f"{OUT}/{f}") for f in FILES},
           src_l186_run=sha("l186/run.py"), gj_sha256=sha("l197b/gj.py"),
           causal_seeds=BASE, tag_offset=TAGOFF,
           keyscan=dict(npz_scanned=nscan, collisions=0, tokens="19931..19946 and 69931..69946"),
           frozen=time.strftime("%Y-%m-%d %H:%M:%S %Z") + " before any L199 statistic or rollout (no raw/gains/results file exists under l199)")
assert frz["gj_sha256"] == json.load(open("l197b/FREEZE.json"))["files"]["gj.py"]
json.dump(frz, open(f"{OUT}/FREEZE.json", "w"), indent=1)
open(f"{OUT}/PREREG.sha256", "w").write("".join(f"{v}  {k}\n" for k, v in frz["files"].items()) + "frozen " + frz["frozen"] + "\n")
print("FROZEN", frz["prereg_sha256"][:16], "| keyscan", nscan, "npz, 0 collisions |", frz["frozen"])
