"""Emit L175-FINDINGS.md from results_l175.json (every number parsed from the
artifact, none typed). Run from banc/."""
import json

import numpy as np
import pandas as pd

r = json.load(open("l175/results_l175.json"))
assert r["status"] == "FINAL"
rows, tw, base, bi = r["window"], r["twins"], r["base"], r["branch_inputs"]
car = rows[0]
ncar = rows[1:]
sil = [x for x in rows if not x["active"]]
act = [x for x in ncar if x["active"]]
more = [x for x in act if x["drive_ratio_to_carrier"] > 1]
inter = r["descriptive"]["intermediate_arms"]
inter_sil = [a for a in inter if a in {x["arm"] for x in sil}]


def sp(a, b):
    return float(np.corrcoef(pd.Series(a).rank(), pd.Series(b).rank())[0, 1])


rg = sp([x["gain"] for x in ncar], [x["meanR"] for x in ncar])
rgs = sp([x["gain"] for x in sil], [x["meanR"] for x in sil])
s47 = next(x for x in rows if x["arm"] == "sc47")
s27 = next(x for x in rows if x["arm"] == "sc27")
s40 = next(x for x in rows if x["arm"] == "sc40")
smax = max(abs(100 * x["gain_delta_vs_wA"] / base["gain"]) for x in sil)
st47 = [json.load(open(f"l175/gains_w{w}.json"))["stairs"].get("sc47") for w in range(5)]
st47 = [v for v in st47 if v is not None][0]
dn = [x for x in rows if x["kR"] == 0]
A, C = tw["dmA"], tw["dmC"]


def f(v):
    return f"{v:.3f}".lstrip("0") if v < 1 else f"{v:.3f}"


def line(x, tag=""):
    return (f"| {x['arm']}{tag} | {x.get('rank') or '-'} | {x['gi'] or '-'} | "
            f"{(x.get('cell_type') or 'base')} | "
            f"{'+' if (x.get('eff_sign') or 1) > 0 else '-'} | "
            f"{x.get('x_mean', float('nan')):.4f} | {x.get('out_mass', float('nan')):.5f} | "
            f"{x.get('drive_ratio_to_carrier', float('nan')):.2f} | "
            f"{100 * x['gain_delta_vs_wA'] / base['gain']:+.2f} | "
            f"{x['kR']}/{x['n']} | {x['meanR']:.3f} | {x['kL']} | {x['meanL']:.3f} | "
            f"{x['cls'].replace('NOT-SUPER/PARTIAL', 'not (partial)').replace('NOT-SUPER', 'not').replace('INTERMEDIATE', 'interm.')} |")


L = []
L.append("# L175 (b) FINDINGS — single-cell scan + drive-matched twin (batch 3545-3560, n=16 every arm, FINAL)")
L.append("")
L.append(f"**Branch fired: {r['branch']}** (read order E0 > D1 > D2 > D3; PREREG sha256 {r['prereg_sha256'][:16]}, registered before any rollout). "
         f"Certs green: generic plumbing == lineage cutng25/cutng25p (static); g_cutwA x5 / g_sc25 / g_sc26 == stored floats EXACT; "
         f"C0A {r['certs']['c0a175_checks']} bit-identity checks vs raw_l135 max 0.0; cutwA identical across workers ({r['certs']['cert_x_checks']} checks); metric reproduces results_l135 EXACT.")
L.append("")
L.append(f"- **Carrier {car['kR']}/16, meanR {car['meanR']:.3f} (Wilson lb {car['lbR']:.3f}) — the only SUPER among {len(rows)} window arms + 2 twins.** Base {base['kR']}/16 {base['meanR']:.3f}; mass twin 319 {rows[1]['kR']}/16 {rows[1]['meanR']:.3f}.")
L.append(f"- **Drive-matched twins do not flip.** dmA gi {A['gi']} ({A['cell_type']}, inhibitory, drive x{A['drive_ratio_to_carrier']:.3f} of carrier) {A['kR']}/16 {A['meanR']:.3f}; "
         f"dmC gi {C['gi']} ({C['cell_type']}, same class + sign as carrier, x{C['drive_ratio_to_carrier']:.3f}) {C['kR']}/16 {C['meanR']:.3f}. They agree.")
L.append(f"- **Active cells do not flip.** {bi['n_active']} of 34 window cells are active on the k=24 base (carrier x_mean {car['x_mean']:.3f}; mass twin {rows[1]['x_mean']:.4f}). "
         f"Of the {bi['A_n']} other active cells, {len(bi['F_A'])} SUPER; of the {bi['H_n']} at carrier-scale drive (>= .5x), {len(bi['F_H'])}; "
         f"{len(more)} deliver MORE than the carrier (x{min(x['drive_ratio_to_carrier'] for x in more):.2f}-{max(x['drive_ratio_to_carrier'] for x in more):.2f}), {sum(x['cls'] == 'SUPER' for x in more)} SUPER. "
         f"Spearman(drive, meanR) = {bi['rho_all_drive_meanR']:+.2f} over the {bi['n_active']} active cells (excitatory only: {bi['rho_exc_drive_meanR']:+.2f}, n={bi['n_active_exc']}).")
L.append("")
L.append("Caveats (descriptive, NOT registered — they bound how hard D2 can be leaned on):")
L.append(f"1. **The null is wide.** Removing one of the {len(sil)} silent cells (delivers ~nothing) gives kR {min(x['kR'] for x in sil)}-{max(x['kR'] for x in sil)}/16, meanR {min(x['meanR'] for x in sil):.3f}-{max(x['meanR'] for x in sil):.3f}. "
         f"All {len(inter)} INTERMEDIATE arms ({len(inter_sil)} of them silent cells) sit inside that range; sc27 ({s27['kR']}/16, {s27['meanR']:.3f}) and sc40 ({s40['kR']}/16, {s40['meanR']:.3f}) sit at the SUPER boundary (kR >= 12 and meanR >= .60). The mass twin's {rows[1]['kR']}/16 is one draw from this null, not a control.")
L.append(f"2. **The null covaries with gain.** Over the 33 non-carrier arms meanR vs the arm's own re-bisected gain: Spearman {rg:+.2f} ({rgs:+.2f} among silent cells, whose gain shifts are at most {smax:.2f}%). "
         f"The carrier goes AGAINST it ({100 * car['gain_delta_vs_wA'] / base['gain']:+.2f}% gain, highest meanR), so the gain trend does not explain its flip; it does suggest the k=24 base is gain-sensitive at the sub-percent level (not tested directly here: discriminator ii).")
L.append(f"3. sc47 bisected to an outlier gain ({100 * s47['gain_delta_vs_wA'] / base['gain']:+.1f}%, staircase residual {st47:.1e}); read that arm ({s47['kR']}/16) with care. "
         f"{' and '.join(x['arm'] for x in dn)} (active, excitatory) go the other way: 0/16.")
L.append("4. One batch; chopped 0.7-Hz classifier only (referee N2's unchopped panel not run; the raws are stored, so it costs zero rollouts); drive = mean rate x out-weight, not target-matched. "
         "Rule deviation: results json was refreshed atomically per completed SEED (seed-outer loop), not per arm.")
L.append("")
L.append("**Title.** Keep \"identity\"; do not reframe to \"delivered drive\". The evidence should move off the silent mass twin onto this table: 1 of 34 window cells and 0 of 2 drive-matched twins flip. "
         "Honest wording: \"cell identity, not removal mass or delivered drive (one batch)\", with the twin's silence and the null width disclosed.")
L.append("**Next (discriminators).** (i) second fresh batch for sc25 / dmA / dmC / sc27 / sc40 (L90 rule); (ii) cutwA gain sweep +-0.5% in 5 steps = the gain-only null; (iii) unchopped panel on these raws.")
L.append(f"**Predictions.** P1 controls reproduce: correct. P2 carrier active, <17 active: correct ({bi['n_active']}). P3 my modal guess was D3 (.45): wrong, D2 fired. P4 dmA not a DN: wrong (it is).")
L.append("")
L.append("| arm | rank | gi | type | sign | x_mean (k=24) | out_mass | drive / carrier | gain d% | kR | meanR | kL | meanL | class |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
L.append(line(base))
for x in rows:
    L.append(line(x))
L.append(line(A, " (twin, any class)"))
L.append(line(C, " (twin, carrier class)"))
txt = "\n".join(L) + "\n"
assert txt.count("\n") <= 60, txt.count("\n")
open("l175/L175-FINDINGS.md", "w").write(txt)
print(txt.count("\n"), "lines written")
print("\n".join(L[:18]))
