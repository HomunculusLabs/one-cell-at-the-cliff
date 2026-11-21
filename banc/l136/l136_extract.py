"""L136 extraction: re-derive the L113-L135 kill->super window story from STORED
results jsons ONLY (L44 rule: never from log prose). Zero rollouts, static.

Outputs l136/plot_data.json. Every pooled number is independently recomputed
from per-run table cells and asserted EQUAL to the stored pooled blocks
(l135 results: pooled / pooled_transition) before it may be plotted.
"""
import json
import math
import os

BANC = os.path.expanduser("~/critters/peabrain-lab/banc")
OUT = os.path.join(BANC, "l136")
os.makedirs(OUT, exist_ok=True)

RUNS = ["l121", "l122", "l123", "l124", "l125", "l126", "l127", "l128",
        "l131", "l133", "l135"]  # the 11-run ng-family era (== l135 pooled union)
R = {}
for d in RUNS:
    R[d] = json.load(open(f"{BANC}/{d}/results_{d}.json"))

# batch-label <-> run map, verified against the k_b fields of l135's pooled blocks
BATCH_OF_RUN = {"l126": "b21", "l131": "b24", "l133": "b25", "l135": "b26"}


def cell(run, arm, side):
    t = R[run]["table"]["Ti"][arm]
    return {"k": t[f"k{side}"], "mean": t[f"mean{side}"],
            "lb": t[f"lb{side}"], "ub": t[f"ub{side}"]}


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return ctr - hw, ctr + hw


# ---------------------------------------------------------------- pooled bars
# registered unions: outer rungs = all 11 runs; transition rungs = their runs
POOLS = {
    # arm: (union runs, stored source run, stored block, stored key)
    "full":     (RUNS, "l135", "pooled", "full"),
    "cutng19":  (RUNS, "l135", "pooled", "cutng19"),
    "cutng29":  (RUNS, "l135", "pooled", "cutng29"),
    "cutk5":    (RUNS, "l135", "pooled", "cutk5"),
    "cut58":    (RUNS, "l135", "pooled", "cut58"),
    "cutng23":  (["l126", "l131", "l133", "l135"], "l135", "pooled_transition", "cutng23"),
    "cutwA":    (["l126", "l131", "l133", "l135"], "l135", "pooled_transition", "cutwA"),
    "cutng26":  (["l126", "l131", "l133", "l135"], "l135", "pooled_transition", "cutng26"),
    "cutng25":  (["l131", "l133", "l135"], "l135", "pooled_transition", "cutng25"),
    "cutng25p": (["l133", "l135"], "l135", "pooled_transition", "cutng25p"),
}

pooled = {}
for arm, (union, srun, sblock, skey) in POOLS.items():
    per_run = {}
    k = n = 0
    kL = 0
    for run in union:
        c = cell(run, arm, "R")
        assert run in R and arm in R[run]["table"]["Ti"], (arm, run)
        per_run[run] = c["k"]
        k += c["k"]; n += 16
        kL += cell(run, arm, "L")["k"]
    stored = R[srun][sblock][skey]
    kN = [v for kk, v in stored.items() if kk.startswith("k") and kk[1:].isdigit() and kk != "k_b"]
    # stored total key like k176 / k64 / k48 / k32
    tot_key = [kk for kk in stored if kk[0] == "k" and kk[1:].isdigit()][0]
    assert stored[tot_key] == k, (arm, "k total", stored[tot_key], k)
    assert int(tot_key[1:]) == n, (arm, "n", tot_key, n)
    for run, blab in BATCH_OF_RUN.items():
        if f"k_{blab}" in stored and run in per_run:
            assert stored[f"k_{blab}"] == per_run[run], (arm, run, blab)
    lb, ub = wilson(k, n)
    assert abs(lb - stored["lb"]) < 1e-12 and abs(ub - stored["ub"]) < 1e-12, (arm, lb, ub)
    pooled[arm] = {
        "k": k, "n": n, "p_hat": k / n, "lb": lb, "ub": ub, "kL": kL,
        "mean_R_runs": {run: cell(run, arm, "R")["mean"] for run in union},
        "per_run_kR": per_run,
        "provenance": f"{srun}/results_{srun}.json:{sblock}:{skey} (independently re-summed)",
    }

# --------------------------------------------------- dose curve (l135 latest)
dose = R["l135"]["dose"]["Ti"]
DOSE_ARM = {"0": "full", "19": "cutng19", "23": "cutng23", "24": "cutwA",
            "25": "cutng25", "25p": "cutng25p", "26": "cutng26", "29": "cutng29",
            "58": "cut58", "k5": "cutk5"}
for kk, arm in DOSE_ARM.items():
    assert dose["meanR"][kk] == cell("l135", arm, "R")["mean"], (kk, arm, "meanR")
    assert dose["kR"][kk] == cell("l135", arm, "R")["k"], (kk, arm, "kR")
    assert dose["meanL"][kk] == cell("l135", arm, "L")["mean"], (kk, arm, "meanL")
    assert dose["kL"][kk] == cell("l135", arm, "L")["k"], (kk, arm, "kL")

# single-batch context rungs (l126: 21, 28; l121: 39) — asserted to their tables
d126 = R["l126"]["dose"]["Ti"]
d121 = R["l121"]["dose"]["Ti"]
for src, dd, pairs in (("l126", d126, {"21": "cutng21", "28": "cutng28"}),
                       ("l121", d121, {"39": "cutng39"})):
    for kk, arm in pairs.items():
        assert dd["meanR"][kk] == cell(src, arm, "R")["mean"], (src, kk)
        assert dd["kR"][kk] == cell(src, arm, "R")["k"], (src, kk)

# ------------------------------------------------------------------ masses
# ladder semantic = REMOVED ng-family in-mass fraction (grows with k); full = 0
mass = dict(R["l135"]["mass_prefix"])          # k21/23/24(wA)/26/28
m121 = R["l121"]["mass"]
for cand in ("cutng19", "cutng29", "cutng39", "cut58"):
    if cand in m121:
        mass[cand] = m121[cand]
mass["cut58ng"] = mass.pop("cut58")            # lineage arm name cut58 (ng family, 58 cells)
# identity twins: ng25 = wA + cell 1110 (m25); 25p = wA + cell 319 (stored .2346)
xor135 = R["l135"]["xor"]["p2"]
assert abs(xor135["m25"] - xor135["m26"] - xor135["pair_delta"]) < 1e-15
mass["cutng25"] = mass["cutwA"] + xor135["m25"]
assert abs(mass["cutng25"] - (xor135["mass_25p"] + xor135["pair_delta"])) < 1e-3
mass["cutng25p"] = xor135["mass_25p"]
mass["full"] = 0.0                             # removed-mass convention, disclosed

# interp classifications (l133 curve -> same arms in l135 interp)
interp = R["l135"].get("interp", {}).get("curve", R["l133"]["interp"]["curve"])
cls = {}
for kk, arm in DOSE_ARM.items():
    if kk in interp:
        c = interp[kk]
        cls[arm] = ("kill" if c["kill"] else "super" if c["super"] else
                    "partial" if c["partial"] else "restore" if c["restore"] else "?")
        assert c["arm"] == arm or (arm == "cutwA" and c["arm"] == "cutwA"), (kk, c["arm"], arm)
# cut58 label from l121's own stored classification block (k58_kill: true)
cls["cut58"] = "kill" if R["l121"]["classification"]["k58_kill"] else "?"

# paired dR legs (l135)
legs = dose["legs"]

# l126 mono curve for the 21/28 context + l126 dose classification of 24->26
plot_data = {
    "pooled": pooled,
    "dose_l135": {"meanR": dose["meanR"], "kR": dose["kR"],
                  "meanL": dose["meanL"], "kL": dose["kL"], "legs": legs},
    "context_single_batch": {
        "21": {"run": "l126", "meanR": d126["meanR"]["21"], "kR": d126["kR"]["21"]},
        "28": {"run": "l126", "meanR": d126["meanR"]["28"], "kR": d126["kR"]["28"]},
        "39": {"run": "l121", "meanR": d121["meanR"]["39"], "kR": d121["kR"]["39"]},
    },
    "mass": mass,
    "classification": cls,
    "xor": {"rank25_id": xor135["rank25_id"], "rank26_id": xor135["rank26_id"],
            "m25": xor135["m25"], "m26": xor135["m26"],
            "pair_delta": xor135["pair_delta"], "steps": R["l135"]["xor"]["steps"]},
    "banc_subnet": "l65 cord subnet (20,521 cord + 728 DN-into), Ti flexor pool n=101",
    "runs": RUNS,
}
json.dump(plot_data, open(f"{OUT}/plot_data.json", "w"), indent=1)
print("EXTRACTION OK — all asserts passed")
print("pooled rungs:")
for arm, p in pooled.items():
    print(f"  {arm:9s} {p['k']:3d}/{p['n']:3d} p={p['p_hat']:.3f} "
          f"[{p['lb']:.3f},{p['ub']:.3f}] kL={p['kL']}")
print("mass:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in sorted(mass.items())})
print("cls:", cls)
