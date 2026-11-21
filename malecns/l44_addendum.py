"""L44 addendum verdict — C0' structural anchor + S/freq protection curve.

Recomputes from l44/raw.npz + results_l44.json; writes results_l44_add.json.
Justified by PREREG ADDENDUM 1 (L40's own rel-arm r_mm during stop was
183-874 — the kill was always structural S collapse, never ratio).
"""
import json

import numpy as np

d = json.load(open("l44/results_l44.json"))
SEEDS = ("11", "22", "33")
ARMS = ("h0", "h5", "h10", "h20", "h40")
S_PROT = 0.25                       # L42/L43 structure-held bar

c0p = {s: d["table"]["h0"][s]["S_med_during"] for s in SEEDS}
c0p_pass = all(v < S_PROT for v in c0p.values())

prot_S = {a: sum(d["table"][a][s]["S_med_during"] >= S_PROT for s in SEEDS)
          for a in ARMS}
med_S = {a: round(float(np.median([d["table"][a][s]["S_med_during"]
                                    for s in SEEDS])), 3) for a in ARMS}
inverted = {a: [s for s in SEEDS if d["table"][a][s]["S_med_during"] < 0]
            for a in ARMS}
fprint = {a: {s: d["table"][a][s]["f_late"] for s in SEEDS} for a in ARMS}
f_ent = {a: sum(d["table"][a][s]["f_late"] <= 0.8 for s in SEEDS) for a in ARMS}
core_recruit = {a: round(float(np.median([d["table"][a][s]["core_late_hist"]
                                           for s in SEEDS])), 4) for a in ARMS}
sa = {a: {s: d["table"][a][s]["S_med_after"] for s in SEEDS} for a in ARMS}

# basin-entry call: >=20 s fully protected, <=10 s not (with inversion lottery)
entry = (prot_S["h20"] == 3 and prot_S["h40"] == 3 and prot_S["h0"] == 0
         and prot_S["h5"] <= 2 and prot_S["h10"] <= 2)
verdict = dict(
    C0p_structural_anchor=dict(h0_S_during=c0p, pass_=c0p_pass),
    protection_S=dict(fraction=prot_S, median=med_S, inverted_seeds=inverted),
    freq_fingerprint=dict(f_late=fprint, entrained_freq_seeds=f_ent),
    core_recruitment=dict(core_X_late_hist=core_recruit),
    S_after_disclosed_window=dict(S_med_after=sa,
                                  window="[6000,8000) = 20s vs L40 44s"),
    basin_entry_between_10_and_20s=bool(entry),
    read=("threshold/basin-entry with turbulent approach: 5-10 s pulses are a "
          "lottery that can INVERT structure (worse than no history, "
          "L41 attractor-selection); >=20 s holds free-run-level structure "
          "through the stop and carries the 0.6-0.7 Hz entrained frequency "
          "through it; the named CPG core is recruited by entrainment "
          "(X .155->.24) and never silenced specifically (C3 15/15)"),
)
json.dump(verdict, open("l44/results_l44_add.json", "w"), indent=1)
print(json.dumps(verdict, indent=1)[:2600])
