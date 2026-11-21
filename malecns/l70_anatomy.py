"""L70: sl-sr-baseline-anatomy — static L/R asymmetry census (PREREG l70/PREREG.md).

Substrate l67 stage A verbatim; NO rollouts. M1 pool input asymmetry,
M2 DNg100 side loading, M3 reciprocal motifs (tick-90 arm), M4 stored-trace
per-seed handedness. 100-draw side-label permutation nulls (L24 form).
Raw nulls checkpointed to l70/raw_l70.npz BEFORE verdict reading.
"""
import json
import time

import numpy as np
import pandas as pd

rng = np.random.default_rng(70)
NDRAW = 100
BETA = 2.0
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- substrate (l67 stage A verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()

nt = pd.read_feather("data/body-neurotransmitters-male-cns-v1.0.feather",
                     columns=["body", "consensus_nt"])
nt_map = dict(zip(nt["body"].astype(np.uint64).astype(str), nt["consensus_nt"]))
nt_names = np.array([str(nt_map.get(str(int(b)), "unknown")).lower() for b in ids])

w = pd.read_feather(
    "data/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
w = w[w["body_pre"].isin(idx) & w["body_post"].isin(idx)]
gsrc = w["body_pre"].map(idx).to_numpy(np.int64)
gdst = w["body_post"].map(idx).to_numpy(np.int64)
gw = w["weight"].to_numpy(np.float32)

cord = np.isin(sup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
dn_all = sup == "descending_neuron"
dn_into = np.zeros(len(ids), bool)
dn_into[gdst[cord[gsrc]]] = True
dn_into &= dn_all
keep = cord | dn_into

emask = keep[gsrc] & keep[gdst]
gsrc, gdst, gw = gsrc[emask], gdst[emask], gw[emask]
loc = -np.ones(len(ids), np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
lsup, ltyp, lside, lcls = sup[keep], typ[keep], side[keep], cls[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)

ntk = nt_names[keep]
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in ntk], np.float32)
wa = gw * signA[lsrc]
wb_abs = np.abs(wa) * np.where(wa < 0, BETA, 1.0)   # |Wb|: census drive mass

motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
tm = pd.Series(ltyp)
PAIRS = {}
for k in ("Ti", "Tr"):
    f = np.where(motor & tm.isin([f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (tm == f"{k} extensor MN"))[0]
    fL, fR = f[lside[f] == "L"], f[lside[f] == "R"]
    eL, eR = e[lside[e] == "L"], e[lside[e] == "R"]
    assert len(fL) and len(fR) and len(eL) and len(eR), (k, len(fL), len(fR))
    PAIRS[k] = dict(fL=fL, fR=fR, eL=eL, eR=eR)
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2
log(f"A1 substrate OK: n={n:,} edges={len(gsrc):,} | {time.time()-t0:.0f}s")
log("pools: " + " ".join(f"{k}:{c}={len(v)}" for k, d in PAIRS.items()
                         for c, v in d.items()))


def zof(obs, nulls):
    mu, sd = float(np.mean(nulls)), float(np.std(nulls))
    return (float(obs) - mu) / sd if sd > 1e-12 else float("nan")


out = {"pools": {k: {c: int(len(v)) for c, v in d.items()} for k, d in PAIRS.items()},
       "subnet": {"n": n, "edges": int(len(gsrc))}}
raw = {}

# ---------- M1: pool input asymmetry ----------
log("--- M1 pool input asymmetry ---")
m1 = {}
for k in ("Ti", "Tr"):
    for fam in ("f", "e"):
        Lp, Rp = PAIRS[k][fam + "L"], PAIRS[k][fam + "R"]
        mem = np.concatenate([Lp, Rp])
        # per-member in-mass (abs Wb) + in-deg
        member_mass = np.array([wb_abs[ldst == m].sum() for m in mem], np.float64)
        member_deg = np.array([(ldst == m).sum() for m in mem], np.int64)
        nl = len(Lp)
        tot = member_mass.sum()
        obs_li = (member_mass[:nl].sum() - member_mass[nl:].sum()) / tot
        nulls = np.empty(NDRAW)
        for d in range(NDRAW):
            pm = rng.permutation(len(mem))
            lsel = np.zeros(len(mem), bool)
            lsel[pm[:nl]] = True
            nulls[d] = (member_mass[lsel].sum() - member_mass[~lsel].sum()) / tot
        # source-side decomposition of in-mass (pooled both sides of family)
        pool_all = mem
        inb = np.isin(ldst, pool_all)
        src_side = lside[lsrc[inb]]
        mv = wb_abs[inb]
        dec = {s: float(mv[src_side == s].sum()) for s in ("L", "R")}
        dec["unlabeled"] = float(mv[(src_side != "L") & (src_side != "R")].sum())
        key = f"{k}_{fam}"
        m1[key] = dict(
            nL=int(nl), nR=int(len(mem) - nl),
            massL=float(member_mass[:nl].sum()), massR=float(member_mass[nl:].sum()),
            LI=round(float(obs_li), 4), z=round(zof(obs_li, nulls), 2),
            degL=int(member_deg[:nl].sum()), degR=int(member_deg[nl:].sum()),
            src_side_mass={a: round(b, 1) for a, b in dec.items()})
        raw[f"m1_null_{key}"] = nulls
        raw[f"m1_obs_{key}"] = np.array([obs_li])
        log(f"{key}: n {nl}/{len(mem)-nl} | mass {m1[key]['massL']:.0f}/"
            f"{m1[key]['massR']:.0f} | LI {obs_li:+.4f} z {m1[key]['z']}")
out["M1"] = m1

# ---------- M2: DNg100 side-resolved output ----------
log("--- M2 DNg100 side loading ---")
labeled = np.where((lside == "L") | (lside == "R"))[0]
lab_L = lside[labeled] == "L"
out["M2_env"] = dict(labeled_cells=int(len(labeled)), nL=int(lab_L.sum()))
m2 = {"per_cell": []}
dn_out = np.isin(lsrc, dng100)
dn_targets = ldst[dn_out]
dn_mass = wb_abs[dn_out]
tgt_side = lside[dn_targets]
tl = dn_mass[tgt_side == "L"].sum()
tr = dn_mass[tgt_side == "R"].sum()
obs_li = (tl - tr) / (tl + tr)
# null: shuffle labels among labeled cells, masses fixed
tgt_in_lab = np.isin(dn_targets, labeled)
mass_lab = dn_mass[tgt_in_lab]
tgt_local = dn_targets[tgt_in_lab]
# map each labeled target to its index in `labeled`
pos_in_labeled = np.full(n, -1, np.int64)
pos_in_labeled[labeled] = np.arange(len(labeled))
tgt_pos = pos_in_labeled[tgt_local]
nulls = np.empty(NDRAW)
for d in range(NDRAW):
    pl = rng.permutation(len(labeled))
    isL = np.zeros(len(labeled), bool)
    isL[pl[: int(lab_L.sum())]] = True
    ml = mass_lab[isL[tgt_pos]].sum()
    mr = mass_lab[~isL[tgt_pos]].sum()
    nulls[d] = (ml - mr) / (ml + mr)
m2["pooled"] = dict(massL=float(tl), massR=float(tr), LI=round(float(obs_li), 4),
                    z=round(zof(obs_li, nulls), 2))
raw["m2_null"] = nulls
raw["m2_obs"] = np.array([obs_li])
for cell in dng100:
    co = lsrc == cell
    ct, cm = ldst[co], wb_abs[co]
    cts = lside[ct]
    row = dict(cell=int(cell), side=str(lside[cell]), n_out=int(co.sum()),
               massL=float(cm[cts == "L"].sum()), massR=float(cm[cts == "R"].sum()),
               mass_unlabeled=float(cm[(cts != "L") & (cts != "R")].sum()))
    for sc in ("motor", "vnc_intrinsic"):
        msk = np.isin(ct, np.where(np.isin(lsup, [sc]))[0])
        row[f"{sc}_mass"] = float(cm[msk].sum())
    # direct mass onto the 8 pools
    pm = {}
    for k in ("Ti", "Tr"):
        for c, parr in PAIRS[k].items():
            pm[c] = float(cm[np.isin(ct, parr)].sum())
    row["pool_mass"] = {a: round(b, 2) for a, b in pm.items()}
    m2["per_cell"].append(row)
    log(f"cell {cell} side {row['side']}: massL {row['massL']:.0f} "
        f"massR {row['massR']:.0f} pools "
        f"{ {a: round(b) for a, b in pm.items() if b > 0} }")
log(f"DNg100 pooled LI {obs_li:+.4f} z {m2['pooled']['z']} "
    f"(massL {tl:.0f} / massR {tr:.0f})")
out["M2"] = m2

# ---------- M3: reciprocal motifs (premotor sheet) ----------
log("--- M3 reciprocity ---")


def recip_table(nodes, src, dst, label_of):
    """Induced directed subgraph on `nodes` (local idx). Returns dict + pair table."""
    remap = np.full(n, -1, np.int64)
    remap[nodes] = np.arange(len(nodes))
    inb = (remap[src] >= 0) & (remap[dst] >= 0)
    s_local = remap[src[inb]]
    d_local = remap[dst[inb]]
    self_loop = s_local == d_local
    if self_loop.any():
        s_local, d_local = s_local[~self_loop], d_local[~self_loop]
    s = len(nodes)
    m = len(s_local)
    a = np.minimum(s_local, d_local)
    b = np.maximum(s_local, d_local)
    pid = a * s + b
    u, inv = np.unique(pid, return_inverse=True)
    cnt = np.bincount(inv)
    recip = cnt == 2
    p_src, p_dst = u // s, u % s
    dens = m / (s * (s - 1)) if s > 1 else 0.0
    frac_er = dens**2 / (2 * dens - dens**2) if dens > 0 else 0.0
    frac = float(recip.mean())
    lab = label_of[nodes]
    # observed per-side fractions
    def side_frac(sm):
        both = sm[p_src] & sm[p_dst]
        den = int(both.sum())
        return (float(recip[both].sum()) / den) if den else float("nan"), den
    fL, dL = side_frac(lab == "L")
    fR, dR = side_frac(lab == "R")
    # cross pairs: exactly one L one R
    lm, rm = lab == "L", lab == "R"
    cross = (lm[p_src] & rm[p_dst]) | (rm[p_src] & lm[p_dst])
    fX = float(recip[cross].sum()) / int(cross.sum()) if cross.sum() else float("nan")
    return dict(size=int(s), edges=int(m), recip_pairs=int(recip.sum()),
                connected=int(len(u)), fraction=round(frac, 6),
                er_fraction=round(float(frac_er), 8),
                over_rep=round(frac / frac_er, 1) if frac_er > 0 else None,
                fL=round(fL, 4), fL_den=dL, fR=round(fR, 4), fR_den=dR,
                f_cross=round(fX, 4), cross_den=int(cross.sum())), \
        (p_src, p_dst, recip, lab)


# premotor sheet: intrinsic cells with >=1 out-edge onto motor (+ motor itself)
pm_mask = np.zeros(n, bool)
pm_mask[np.unique(lsrc[np.isin(ldst, np.where(motor)[0])])] = True
pm_mask &= lsup == "vnc_intrinsic"
sheet = np.sort(np.concatenate([np.where(pm_mask)[0], np.where(motor)[0]]))
prim, ptab = recip_table(sheet, lsrc, ldst, lside)
p_src, p_dst, recip, lab = ptab
log(f"sheet: intrinsic {int(pm_mask.sum())} + motor {int(motor.sum())} "
    f"= {prim['size']:,} nodes, {prim['edges']:,} edges | recip "
    f"{prim['recip_pairs']:,}/{prim['connected']:,} = {prim['fraction']:.4f} "
    f"(ER {prim['er_fraction']:.2e}, over-rep {prim['over_rep']}x)")
log(f"per-side: fL {prim['fL']} (n={prim['fL_den']}) fR {prim['fR']} "
    f"(n={prim['fR_den']}) cross {prim['f_cross']} (n={prim['cross_den']})")
obs_li_rec = (prim["fL"] - prim["fR"]) / (prim["fL"] + prim["fR"])
nulls_rec = np.empty(NDRAW)
nl_count = int((lab == "L").sum())
for d in range(NDRAW):
    pl = rng.permutation(len(lab))
    isL = np.zeros(len(lab), bool)
    isL[pl[:nl_count]] = True
    bothL = isL[p_src] & isL[p_dst]
    bothR = (~isL[p_src]) & (~isL[p_dst])
    fLd = recip[bothL].sum() / max(bothL.sum(), 1)
    fRd = recip[bothR].sum() / max(bothR.sum(), 1)
    nulls_rec[d] = (fLd - fRd) / (fLd + fRd)
z_rec = zof(obs_li_rec, nulls_rec)
prim["LI_recip"] = round(float(obs_li_rec), 4)
prim["z"] = round(z_rec, 2)
raw["m3_null"] = nulls_rec
raw["m3_obs"] = np.array([obs_li_rec])
log(f"LI_recip {obs_li_rec:+.4f} z {z_rec}")
# secondary: intrinsic-only induced subgraph
intrinsic_sheet = np.sort(np.where(pm_mask)[0])
sec, _ = recip_table(intrinsic_sheet, lsrc, ldst, lside)
log(f"intrinsic-only: {sec['size']:,} nodes {sec['edges']:,} edges "
    f"recip {sec['fraction']:.4f} over-rep {sec['over_rep']}x "
    f"fL {sec['fL']} fR {sec['fR']}")
out["M3"] = {"sheet": prim, "intrinsic_only": sec}

# ---------- M4: stored-trace per-seed handedness ----------
log("--- M4 stored-trace handedness (l66 hynohop open) ---")
z66 = np.load("l66/raw_l66.npz")
SEEDS = [11, 22, 33] + list(range(101, 114))
OFFS = [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)]
TS3 = np.arange(299, 6000, 10)


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


per_seed = {}
for s in SEEDS:
    fL = z66[f"fL_hynohop_{s}"]
    eL = z66[f"eL_hynohop_{s}"]
    fR = z66[f"fR_hynohop_{s}"]
    eR = z66[f"eR_hynohop_{s}"]
    sls, srs = [], []
    for lo, hi in OFFS:
        for t in TS3[(TS3 >= lo + 299) & (TS3 < hi)]:
            sls.append(S_of(fL[t - 299:t + 1], eL[t - 299:t + 1]))
            srs.append(S_of(fR[t - 299:t + 1], eR[t - 299:t + 1]))
    per_seed[s] = (round(float(np.nanmean(sls)), 3),
                   round(float(np.nanmean(srs)), 3))
h = np.array([a - b for a, b in per_seed.values()])
SLm = float(np.mean([a for a, _ in per_seed.values()]))
SRm = float(np.mean([b for _, b in per_seed.values()]))
out["M4"] = {"per_seed": {str(s): v for s, v in per_seed.items()},
             "SL_mean": round(SLm, 3), "SR_mean": round(SRm, 3),
             "h_mean": round(float(h.mean()), 3), "h_sd": round(float(h.std()), 3),
             "h_min": round(float(h.min()), 3), "h_max": round(float(h.max()), 3),
             "h_pos_count": int((h > 0).sum()), "n_seeds": len(SEEDS)}
log(f"open SL {SLm:.3f} SR {SRm:.3f} | h {h.mean():+.3f} sd {h.std():.3f} "
    f"range [{h.min():+.3f},{h.max():+.3f}] | h>0 on {(h > 0).sum()}/{len(h)}")
assert abs(SLm - 0.326) < 0.01 and abs(SRm - 0.153) < 0.01, (SLm, SRm)
log("A2 PASS: M4 recompute matches l66 stored open means (.326/.153)")

# ---------- checkpoint raw BEFORE verdict ----------
np.savez_compressed("l70/raw_l70.npz", **raw)
with open("l70/results_l70.json", "w") as f:
    json.dump(out, f, indent=1)
log(f"checkpointed l70/raw_l70.npz + results_l70.json | {time.time()-t0:.0f}s")

# ---------- verdict (G1/G2/G3, pre-registered) ----------
cands = [(f"M1:{k}", v["LI"], v["z"]) for k, v in m1.items()]
cands += [("M2:pooled", m2["pooled"]["LI"], m2["pooled"]["z"]),
          ("M3:LI_recip", prim["LI_recip"], prim["z"])]
# G1 directional: L-ENRICHED wiring (LI>0, z>=+3) matches SL-healthier bias
winners = [(nm, li, z) for nm, li, z in cands
           if np.isfinite(z) and z >= 3 and li > 0]
antis = [(nm, li, z) for nm, li, z in cands
         if np.isfinite(z) and z <= -3 and li < 0]
g1 = bool(winners)
log(f"G1 wiring-carried (L-enriched, z>=+3): {g1} " +
    (f"-> {winners}" if winners else
     f"(best |z| {max(abs(z) for _, _, z in cands if np.isfinite(z)):.2f})"))
if antis:
    log(f"G1 anti-matches (R-enriched, z<=-3, CONTRADICT the L-bias): {antis}")
g3 = prim["over_rep"] is not None and prim["over_rep"] >= 2
log(f"G3 reciprocity over-ER: {g3} ({prim['over_rep']}x)")
log(f"G2 state-texture fallback read: h>0 on {out['M4']['h_pos_count']}/16 "
    f"(>=13 = biased coin)")
