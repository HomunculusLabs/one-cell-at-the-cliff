"""L200 reference feasibility probe — run BEFORE PREREG, zero rollouts, zero
writes outside stdout. Execs l198/twin_run.py lines 1..(TWIN BLOCK) verbatim
(static mode) and prints ONLY: the left-Ti premotor pool size, ru2's own
reference drive onto it (is the A2 rule well-posed?), and fresh-seed absence.
NO candidate cell is enumerated; NO A4 left/right comparison is computed."""
import os, sys
os.environ["L198_MODE"] = "static"; os.environ["L198_THREADS"] = "2"
src = open("l198/twin_run.py").read()
i = src.index("# ======================= L198 TWIN BLOCK (additive) =======================")
G = {"__name__": "__probe__"}
exec(compile(src[:i], "l198/twin_run.py[:TWIN]", "exec"), G)
np = G["np"]; emask = G["emask_wA"]; src_all = G["src_all"]; dst_all = G["dst_all"]; vals = G["vals_all"]
BETA = G["BETA"]; gi_wA = G["gi_wA"]; loc_wA = G["loc_wA"]; POOLS = G["POOLS"]; cen = G["_cen"]
is_motor = G["is_motor_g"]
GI_RU2 = 70994
mnL = np.concatenate([gi_wA[POOLS["cutwA"]["Ti_fL"]], gi_wA[POOLS["cutwA"]["Ti_eL"]]])
m_in = emask & np.isin(dst_all, mnL)
PL = np.unique(src_all[m_in]); PL = PL[~is_motor[PL]]
print("left-Ti MNs", len(mnL), "| premotor pool P_L size", len(PL), "| ru2 in P_L:", bool(np.isin(GI_RU2, PL)))
m = emask & (src_all == GI_RU2) & np.isin(dst_all, PL)
weff = (np.abs(vals[m]) * np.where(vals[m] < 0, BETA, 1.0)).sum()
xb = float(cen["x_mean_3seed"][int(loc_wA[GI_RU2])])
print("ru2 edges onto P_L:", int(m.sum()), "| sum|w_eff|", float(weff), "| x_mean", xb, "| dL_ref", xb * float(weff))
print("N_NPZ_SCANNED (B43 scan, inherited)", G["N_NPZ_SCANNED"])
import glob, zipfile, re
fresh = set(range(3705, 3721)); rx = re.compile(r"_(\d+)\.npy$"); n = 0; hits = []
for f in sorted(glob.glob("../**/*.npz", recursive=True)):
    try: names = zipfile.ZipFile(f).namelist()
    except Exception as e:
        print("unreadable", f); continue
    n += 1
    for nm in names:
        mm = rx.search(nm)
        if mm and int(mm.group(1)) in fresh: hits.append((f, nm)); break
print("fresh 3705..3720 scan:", n, "npz, hits", hits[:5])
