"""L197b: draw every gate schedule BEFORE any rollout, compute the window
overlap of the two clocks from the drawn schedule, and REFUSE (gate.pass =
False) if either design arm exceeds .25 (the L197 card's verify rule).
Zero rollouts. Run from banc/. Writes l197b/schedule.json."""
import glob, json, re, sys, zipfile
import numpy as np
sys.path.insert(0, "l197b")
import gj

N = int(sys.argv[1]) if len(sys.argv) > 1 else 96
SEEDS = {"S": list(range(19001, 19001 + N)), "W": list(range(19201, 19201 + N))}
assert not set(SEEDS["S"]) & set(SEEDS["W"])
allseeds = set(SEEDS["S"]) | set(SEEDS["W"])
nscan = 0
for f in sorted(glob.glob("../**/*.npz", recursive=True)):
    if f.startswith("../banc/l197b/"):
        continue
    try:
        names = zipfile.ZipFile(f).namelist()
    except (zipfile.BadZipFile, FileNotFoundError, OSError):
        assert f.endswith(".tmp.npz"), ("unreadable npz (STOP)", f)
        continue
    nscan += 1
    for k in names:
        toks = set(map(int, re.findall(r"\d+", k)))
        assert not (toks & allseeds), ("fresh seed token collides (STOP)", f, k)
out = dict(n_per_arm=N, keyscan=dict(npz_scanned=nscan, collisions=0,
                                     rule="any numeric token of any member name (L186 form), all lab npz"),
           design=gj.DESIGN, arms={}, gate=dict(max_mean_overlap=.25))
ok = True
for arm in ("S", "W"):
    d = gj.DESIGN[arm]
    ons = {s: gj.draw_onsets(arm, s) for s in SEEDS[arm]}
    for s, o in ons.items():
        for x in o:
            assert d["onset_lo"] <= x <= d["onset_hi"]
            assert x >= 500 + 25 and x + d["pulse"] <= 1800 - 25, "pulse touches a boundary pulse"
            assert x + d["start_lo"] >= 0 and x + d["start_hi"] + d["W"] <= 2000, "window leaves the segment"
        g = gj.expected_gate(arm, o).reshape(3, -1).sum(1)
        assert list(g) == [700 + d["pulse"], 2000, 700 + d["pulse"]]
    ov = gj.overlap_stats(ons, SEEDS[arm], d["W"])
    lagsteps = np.array([ons[a][g] - ons[b][g] for a in SEEDS[arm] for b in SEEDS[arm] if a != b for g in (0, 1)], float)
    rot = gj.rot_of(lagsteps)
    ov.update(jitter_span_steps=[int(min(min(o) for o in ons.values())), int(max(max(o) for o in ons.values()))],
              rot_inphase_share=float((rot >= .75).mean()), rot_antiphase_share=float((rot <= .25).mean()),
              on_steps_per_outer_segment=700 + d["pulse"])
    ov["pass"] = bool(ov["mean_overlap"] <= .25)
    ok &= ov["pass"]
    out["arms"][arm] = dict(seeds=SEEDS[arm], pulse=d["pulse"], onsets={str(s): o for s, o in ons.items()}, overlap=ov)
    print(arm, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in ov.items()})
out["gate"]["pass"] = bool(ok)
json.dump(out, open("l197b/schedule.json", "w"), indent=1)
print("OVERLAP GATE:", "PASS" if ok else "REFUSE", "| keyscan", nscan, "npz, 0 collisions")
