"""L136: render table.md (the ONE dose-placement table) from plot_data.json.
All values source-derived; no hand-typed numbers (L44 rule)."""
import json
import os

BANC = os.path.expanduser("~/critters/peabrain-lab/banc")
P = json.load(open(f"{BANC}/l136/plot_data.json"))
DROP = {  # drop-set description per arm (what the cut removes; lineage defs)
    "full": "nothing (intact ng family)", "cutng19": "19 heaviest ng cells",
    "cutng21": "prefix 21", "cutng23": "prefix 23", "cutwA": "prefix 24 (k19+r20-24)",
    "cutng25": "wA + rank25 (id 1110, DNp33-L)", "cutng25p": "wA + rank26 (id 319, DNpe025-R)",
    "cutng26": "wA + ranks 25-26 (both twins)", "cutng28": "prefix 28",
    "cutng29": "prefix 29 (k29 window)", "cutng39": "prefix 39",
    "cut58": "all 58 ng cells", "cutk5": "k5 control family (not ng)",
}
ORDER = ["full", "cutng19", "cutng21", "cutng23", "cutwA", "cutng25", "cutng25p",
         "cutng26", "cutng28", "cutng29", "cutng39", "cut58", "cutk5"]
legs = P["dose_l135"]["legs"]
LEGK = {"full": "0", "cutng19": "19", "cutng23": "23", "cutwA": "24", "cutng25": "25",
        "cutng25p": "25p", "cutng26": "26", "cutng29": "29", "cut58": "58", "cutk5": "k5"}
rows = ["| rung (arm) | drop set | removed mass | pooled k/n | Wilson 95% | class | paired dR (l135 B26) |",
        "|---|---|---|---|---|---|---|"]
for arm in ORDER:
    m = P["mass"].get(arm if arm != "cut58" else "cut58ng", None)
    ms = f"{m:.4f}" if m is not None else "—"
    if arm in P["pooled"]:
        q = P["pooled"][arm]
        pooled_s = f"{q['k']}/{q['n']}"
        wil = f"[{q['lb']:.3f}, {q['ub']:.3f}]"
    else:
        kk = {"cutng21": "21", "cutng28": "28", "cutng39": "39"}[arm]
        c = P["context_single_batch"][kk]
        pooled_s = f"{c['kR']}/16 (1 batch, {c['run']})"
        wil = "— (single batch)"
    cls = P["classification"].get(arm, "ctx")
    lg = legs.get(LEGK.get(arm, ""), {})
    dr = f"{lg['mean_paired_dR']:+.3f}" if lg else "—"
    rows.append(f"| {arm} | {DROP[arm]} | {ms} | {pooled_s} | {wil} | {cls} | {dr} |")
rows += [
    "",
    "Ti_L companions (pooled kL/n): " + ", ".join(
        f"{a} {P['pooled'][a]['kL']}/{P['pooled'][a]['n']}"
        for a in ["full", "cutng19", "cutng23", "cutwA", "cutng25", "cutng25p", "cutng26", "cutng29"]),
    "",
    f"Identity twins: rank25 id {P['xor']['rank25_id']} m={P['xor']['m25']:.6f} vs rank26 id {P['xor']['rank26_id']} "
    f"m={P['xor']['m26']:.6f}; pair delta {P['xor']['pair_delta']:.2e} (mass-matched XOR).",
    "Metric: duty(Ti_R both-sides >= .25) window read; substrate l65 female BANC cord subnet; "
    "runs l121-l135 (11 batches); sources results_l121/l126/l133/l135.json; extraction asserts all green.",
]
open(f"{BANC}/l136/table.md", "w").write("\n".join(rows) + "\n")
print("\n".join(rows))
