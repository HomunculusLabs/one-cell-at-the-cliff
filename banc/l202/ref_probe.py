"""L202 ref_probe — ZERO rollouts, run BEFORE the PREREG is frozen. Reads stored
names / pins only: fresh-batch key scan, which stored files carry which arm
(anchor plumbing), stored gains, and the two bilateral candidates' registered
covariates from the frozen l200/selection.json. No outcome of any L202 arm
exists yet; no new statistic on a stored outcome is computed here."""
import json
import re
import zipfile
from pathlib import Path

import numpy as np

seen, n = set(), 0
for p in sorted(Path("..").rglob("*.npz")):
    if "l202" in p.parts:
        continue
    try:
        with zipfile.ZipFile(p) as z:
            for k in z.namelist():
                m = re.search(r"_(\d+)\.npy$", k)
                if m:
                    seen.add(int(m[1]))
    except zipfile.BadZipFile:
        print("bad zip", p)
    n += 1
start = 3737
while seen.intersection(range(start, start + 16)):
    start += 32
print(f"npz scanned {n} | first free 16-block on the 32-grid from 3737: {start}..{start+15}")
print("seeds >= 3700 present anywhere:", sorted(s for s in seen if 3700 <= s < 4200))

for run, nw in (("l187", 6), ("l198", 6), ("l200", 6), ("l190", 1)):
    for w in range(nw):
        z = np.load(f"{run}/raw_w{w}.npz")
        arms = sorted(set(re.match(r"mm_(.+)_(\d+)$", k)[1] for k in z.files if k.startswith("mm_")))
        seeds = sorted(set(int(re.match(r"mm_(.+)_(\d+)$", k)[2]) for k in z.files if k.startswith("mm_")))
        g = json.load(open(f"{run}/gains_w{w}.json"))["gain"]
        print(run, w, arms, f"seeds {seeds[0]}..{seeds[-1]} n={len(seeds)}",
              {a: g[a] for a in g if a != "cutwA"})
z = np.load("l190/raw_w0.npz")
print("l190 key kinds @3641:", sorted(k for k in z.files if k.endswith("_E-edge_3641"))[:40])
print("l190 xwin shape", z["xwin_E-edge_3641"].shape, "| xm keys", np.load("l190/xm_w0.npz").files[:4])
print("l190 done:", {k: v for k, v in json.load(open("l190/done_w0.json")).items()
                     if k in ("arms", "seeds", "threads", "track", "ctr_cells")})
sel = json.load(open("l200/selection.json"))
for r in sel["top5"]:
    print({k: r[k] for k in ("rank", "gi", "cell_type", "side", "x_mean", "dL", "dR", "dL_ratio",
                             "total_drive_ratio", "edges_onto_PM_L", "edges_onto_PM_R",
                             "in_PM_L", "in_PM_R")},
          "edges car/ru2:", r["edge_from_carrier"]["n"], r["edge_to_carrier"]["n"],
          r["edge_from_ru2"]["n"], r["edge_to_ru2"]["n"])
r = sel["ru2"]
print("ru2", {k: r[k] for k in ("gi", "x_mean", "dL", "dR", "total_drive", "edges_onto_PM_L",
                               "edges_onto_PM_R")}, "edge to/from carrier",
      r["edge_to_carrier"], r["edge_from_carrier"])
r200 = json.load(open("l200/results_l200.json"))
print("l200 gains:", {a: r200["arms"][a]["gain"] for a in ("sc25", "l2", "l2c", "l2cF")})
r198 = json.load(open("l198/results_l198.json"))
print("l198 arms:", list(r198["arms"]))
