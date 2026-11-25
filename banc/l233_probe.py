"""l233_probe.py — FEASIBILITY probe for L233, reads NO Perron vector and no
connectivity. Annotations only: do the Ti/Tr pool cells carry a cell_type, and
can left cells be PAIRED to right homologs by type (the L207/L212 leg)?

Writes NOTHING. Printed numbers are declared in l233/PREREG.md before any
statistic on v1 is computed.
"""
import numpy as np
import pandas as pd

ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
print("[cols]", list(ann.columns))
ann = ann[ann["super_class"].notna()].copy()
mot = ann[ann.super_class == "motor"].copy()
ptt = mot.peripheral_target_type.fillna("").astype(str).to_numpy()
side = mot.side.fillna("").astype(str).str.lower().to_numpy()
ct = mot.cell_type.fillna("").astype(str).to_numpy()


def has(s):
    return np.array([s in x for x in ptt])


PATS = {
    ("Ti", "f"): has("tibia") & has("flexor"),
    ("Ti", "e"): has("tibia") & has("extensor"),
    ("Tr", "f"): has("trochanter") & has("flexor"),
    ("Tr", "e"): has("trochanter") & has("extensor"),
}
for (J, g), pat in PATS.items():
    for c, sv in (("L", "left"), ("R", "right")):
        m = pat & (side == sv)
        n = int(m.sum())
        nct = int((ct[m] != "").sum())
        print(f"[pool] {J}_{g}{c}: n={n} with_cell_type={nct} "
              f"distinct_types={len(set(ct[m][ct[m] != '']))}")

# pairability by cell_type, per joint (flexor+extensor together = the A_inf set)
for J in ("Ti", "Tr"):
    pat = PATS[(J, "f")] | PATS[(J, "e")]
    mL = pat & (side == "left")
    mR = pat & (side == "right")
    cL = [x for x in ct[mL] if x != ""]
    cR = [x for x in ct[mR] if x != ""]
    from collections import Counter
    kL, kR = Counter(cL), Counter(cR)
    shared = sorted(set(kL) & set(kR))
    npair = sum(min(kL[t], kR[t]) for t in shared)
    one2one = [t for t in shared if kL[t] == 1 and kR[t] == 1]
    print(f"[pair] {J}: L={int(mL.sum())} R={int(mR.sum())} "
          f"typedL={len(cL)} typedR={len(cR)} shared_types={len(shared)} "
          f"paired_cells={npair} one_to_one_types={len(one2one)}")
    print(f"       multiplicity L {dict(sorted(kL.items()))}")
    print(f"       multiplicity R {dict(sorted(kR.items()))}")
print("[probe] DONE — no artifact written")
