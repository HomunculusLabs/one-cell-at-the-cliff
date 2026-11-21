"""L36: DN floor-viability census — which DN types can actually carry a
drive into the cord under the frozen L32 regime (g .01 / beta 2)?

L35 showed the "sustained DNg100 drive" was floor-buried (u ~ -16) and
DNg95 lands only when amp out-lifts its inhibition (relu floor). This
census measures u = W@X*G + I + BG for EVERY DN type in the sub, crosses
with the L22 family / L24 laterality / L31 CX tables, and dynamic
spot-checks a top viable type per family. PREREG: l36/PREREG.md.
CPU-only; no live changes.
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN = 400, 600          # census: 6 s post-settle
G, BETA = 0.01, 2.0
SEEDS = [11, 22, 33]
SPOT_WIN = 6000                 # 60 s spot-check window
MEAS0 = int(0.25 * SPOT_WIN)    # measure last 45 s (PREREG, L34 lesson)
PAIR_KEYS = ["Ti", "Tr"]
AMPS = [0.2, 0.8]

os.makedirs("l36", exist_ok=True)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- substrate (l32 verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()

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
lsup, ltyp, lnt = sup[keep], typ[keep], nt_names[keep]
assert n == 21516, f"nodes {n}"
assert len(lsrc) == 2977920, f"edges {len(lsrc)}"
log(f"substrate OK: {n:,} nodes / {len(lsrc):,} edges (L32-L35 identical)")

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy((gw * signA[lsrc]).astype(np.float32)), (n, n)
).coalesce().to_sparse_csr()
neg = Wc.values() < 0
vals = Wc.values().clone()
vals[neg] *= BETA
Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
Z = torch.zeros(n, 1)

motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
PAIRS = {}
for k in PAIR_KEYS:
    f = np.where(motor & np.isin(ltyp, [f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (ltyp == f"{k} extensor MN"))[0]
    assert len(f) > 0 and len(e) > 0, (k, len(f), len(e))
    PAIRS[k] = (f, e)
log("pairs: " + ", ".join(f"{k} flex {len(f)}/ext {len(e)}" for k, (f, e) in PAIRS.items()))


def step(cur, drive_I, gen):
    drive = torch.sparse.mm(Wb, cur) * G + drive_I
    t = torch.relu(drive + BG)
    t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
    return cur + (DT / TAU) * (t - cur)


# ---------- census ----------
dn_mask = lsup == "descending_neuron"
dn_cells = np.where(dn_mask)[0]
assert len(dn_cells) > 0
tcodes, tnames = pd.factorize(ltyp[dn_cells], sort=True)
ntypes = len(tnames)
log(f"DN cells in sub: {len(dn_cells):,} across {ntypes} types | {time.time()-t0:.0f}s")

umax_cell = np.full(len(dn_cells), -1e9, np.float64)
usum = np.zeros(ntypes, np.float64)
ucnt = np.zeros(ntypes, np.float64)
upos = np.zeros(ntypes, np.float64)
xsum = np.zeros(len(dn_cells), np.float64)
xcnt = 0.0
for seed in SEEDS:
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    for _ in range(SETTLE):
        X = step(X, Z, gen)
    af = float((X > 0.05).float().mean())
    assert 0.01 < af < 0.9, f"op-point {af:.3f}"
    for i in range(WIN):
        X = step(X, Z, gen)
        u = (torch.sparse.mm(Wb, X) * G + BG)[dn_cells, 0].numpy()
        umax_cell = np.maximum(umax_cell, u)
        np.add.at(usum, tcodes, u)
        np.add.at(ucnt, tcodes, 1)
        np.add.at(upos, tcodes, (u > 0).astype(np.float64))
        xsum += X[dn_cells, 0].numpy()
        xcnt += 1
    log(f"  seed {seed}: af {af:.3f} census done | {time.time()-t0:.0f}s")

rows = []
xmean_cell = xsum / xcnt
for ti, tname in enumerate(tnames):
    cm = tcodes == ti
    rows.append(dict(
        dn_type=str(tname), n_cells=int(cm.sum()),
        u_max=float(umax_cell[cm].max()), u_mean=float(usum[ti] / ucnt[ti]),
        frac_pos=float(upos[ti] / ucnt[ti]),
        cells_free=int((umax_cell[cm] > 0).sum()),
        cells_a015=int((umax_cell[cm] > -0.15).sum()),
        cells_a08=int((umax_cell[cm] > -0.8).sum()),
        cells_dyn=int(((umax_cell[cm] > 0) & (xmean_cell[cm] < 0.95)).sum()),
        mean_X=float(xmean_cell[cm].mean())))
cen = pd.DataFrame(rows)

# ---------- join L31 table (families + laterality + CX) ----------
cxdn = pd.read_csv("l31/cx_dn.csv")
atlas_types = set(cxdn.dn_type)
cen = cen.merge(cxdn, on="dn_type", how="left", indicator=True)
cen["in_atlas"] = cen["_merge"] == "both"
cen.drop(columns="_merge", inplace=True)


def fam(r):
    ws = {"flex": r.w_flex if pd.notna(r.w_flex) else 0.0,
          "ext": r.w_ext if pd.notna(r.w_ext) else 0.0,
          "jump": r.w_jump if pd.notna(r.w_jump) else 0.0}
    f = max(ws, key=ws.get)
    return f if ws[f] >= 0.25 else "none/diffuse"


cen["family"] = cen.apply(fam, axis=1)

# ---------- C1 anchors ----------
anch = cen.set_index("dn_type")
a100 = float(anch.loc["DNg100", "u_max"])
a95 = float(anch.loc["DNg95", "u_max"])
a95m = float(anch.loc["DNg95", "u_mean"])
a95p = float(anch.loc["DNg95", "frac_pos"])
c1 = a100 < -1.0 and -0.15 <= a95 <= 0.10 and a95m < 0 and a95p < 0.5
log(f"C1 anchors: DNg100 u_max {a100:+.2f} (want < -1), "
    f"DNg95 u_max {a95:+.3f} (want [-.15,+.10]) u_mean {a95m:+.3f} (<0) "
    f"frac_pos {a95p:.3f} (<.5) -> {'PASS' if c1 else 'FAIL'}")

# ---------- C2 vocabulary ----------
fam_atlas = cen[cen.family.isin(["flex", "ext", "jump"])]
c2 = dict(
    family_types=int(len(fam_atlas)),
    freely_viable=int((fam_atlas.u_max > 0).sum()),
    viable_a015=int((fam_atlas.u_max > -0.15).sum()),
    viable_a08=int((fam_atlas.u_max > -0.8).sum()),
    buried=int((fam_atlas.u_max <= -0.8).sum()),
    ceiling_pinned=int(((fam_atlas.u_max > 0) & (fam_atlas.mean_X >= 0.95)).sum()),
    viable_modulating=int((fam_atlas.cells_dyn > 0).sum()))
c2["nonempty"] = bool(c2["freely_viable"] >= 5)
c2["nonempty_modulating"] = bool(c2["viable_modulating"] >= 5)
log("C2 vocabulary (atlas family types): "
    + " ".join(f"{k}={v}" for k, v in c2.items()))
absent = sorted(atlas_types - set(cen.dn_type))

# ---------- C3 spot-check ----------
picks = {}
for famname in ["flex", "ext", "jump"]:
    sub = fam_atlas[(fam_atlas.family == famname) & (fam_atlas.u_max > -0.05)]
    if len(sub) == 0:
        log(f"  no viable pick for family {famname}")
        continue
    sub = sub.sort_values(["cells_free", "u_max"], ascending=False)
    picks[famname] = str(sub.iloc[0].dn_type)
log(f"C3 picks: {picks}")


def rhythm(x):
    x = x - x.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    b = (fr >= 0.5) & (fr <= 10)
    pb, fb = ps[b], fr[b]
    if pb.max() <= 0:
        return 0.0, 0.0
    i = int(np.argmax(pb))
    return float(pb[i] / max(np.median(pb), 1e-30)), float(fb[i])


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def run_pair(type_cells, amp, seed):
    """Control + tonic-amp arm, PAIRED: one generator, one shared noise
    tensor per step for both arms (a separate generator per arm is offset
    by the init draw -> phantom divergence; caught via the DNg100 anchor
    which must be bit-identical, L35). Returns metrics."""
    assert len(type_cells) > 0
    gen = torch.Generator().manual_seed(seed)
    Xc = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    Xa = Xc.clone()
    I = torch.zeros(n, 1)
    I[type_cells] = amp

    def step2(cur_c, cur_a, drive_on):
        dc = torch.sparse.mm(Wb, cur_c) * G
        da = torch.sparse.mm(Wb, cur_a) * G + (I if drive_on else 0.0)
        nz = NOISE * torch.randn(n, 1, generator=gen)
        tc = (torch.relu(dc + BG) + nz).clamp(max=RMAX)
        ta = (torch.relu(da + BG) + nz).clamp(max=RMAX)
        return (cur_c + (DT / TAU) * (tc - cur_c),
                cur_a + (DT / TAU) * (ta - cur_a))

    for _ in range(SETTLE):          # settle with NO drive (L32 PREREG form;
        Xc, Xa = step2(Xc, Xa, False)  # drive-during-settle crosses DNg100's
        # shallow transient inhibition and lands on a different attractor)
    keys = [(a, pk, s) for a in "ca" for pk in PAIRS for s in "fe"]
    tr = {k: np.zeros(SPOT_WIN, np.float32) for k in keys}
    mmc = np.zeros(SPOT_WIN, np.float32)
    mma = np.zeros(SPOT_WIN, np.float32)
    dm_max, dm_sum, dm_n = 0.0, 0.0, 0
    first_div = -1
    for k in range(SPOT_WIN):
        Xc, Xa = step2(Xc, Xa, True)
        for pk, (f, e) in PAIRS.items():
            tr[("c", pk, "f")][k] = Xc[f].mean()
            tr[("c", pk, "e")][k] = Xc[e].mean()
            tr[("a", pk, "f")][k] = Xa[f].mean()
            tr[("a", pk, "e")][k] = Xa[e].mean()
        mmc[k] = Xc[motor].mean()
        mma[k] = Xa[motor].mean()
        d = float((Xa - Xc).abs().max())
        if d > 1e-6 and first_div < 0:
            first_div = k
        dm_max = max(dm_max, d)
        if k >= MEAS0:
            dm_sum += float((Xa - Xc).abs().mean())
            dm_n += 1
    afc = float((Xc > 0.05).float().mean())
    afa = float((Xa > 0.05).float().mean())
    assert 0.01 < afc < 0.9 and 0.01 < afa < 0.9, (afc, afa)
    sl = slice(MEAS0, SPOT_WIN)
    out = {"dm_max": dm_max, "dm_meas_mean": dm_sum / max(dm_n, 1),
           "first_div": first_div, "afc": afc, "afa": afa,
           "mm_shift": float(mma[sl].mean() - mmc[sl].mean())}
    for pk in PAIRS:
        _, fc = rhythm(tr[("c", pk, "f")][sl])
        _, fa = rhythm(tr[("a", pk, "f")][sl])
        out[f"f_{pk}_c"], out[f"f_{pk}_a"] = fc, fa
        out[f"S{pk}_c"] = S_of(tr[("c", pk, "f")][sl], tr[("c", pk, "e")][sl])
        out[f"S{pk}_a"] = S_of(tr[("a", pk, "f")][sl], tr[("a", pk, "e")][sl])
    return out


spot = {}
arms = []
for famname, tname in picks.items():
    cells = np.where(ltyp == tname)[0]
    assert len(cells) > 0, tname
    arms.append((f"{famname}:{tname}", cells, [0.2, 0.8]))
for tname, amp, tag in (("DNg100", 0.8, "anchor:g100"), ("DNg95", 0.2, "anchor:g95")):
    cells = np.where(ltyp == tname)[0]
    assert len(cells) > 0, tname
    arms.append((tag, cells, [amp]))

for tag, cells, amps in arms:
    spot[tag] = {}
    for amp in amps:
        spot[tag][amp] = []
        for seed in SEEDS:
            m = run_pair(cells, amp, seed)
            spot[tag][amp].append(m)
        dms = [f"{m['dm_max']:.4f}" for m in spot[tag][amp]]
        dss = [f"{m['STr_a']-m['STr_c']:+.3f}" for m in spot[tag][amp]]
        dfs = [f"{m['f_Ti_a']-m['f_Ti_c']:+.3f}" for m in spot[tag][amp]]
        log(f"  {tag} amp {amp}: dm {dms} | dS(Tr) {dss} | df(Ti) {dfs}"
            f" | {time.time()-t0:.0f}s")

# dynamic anchors: DNg100@0.8 must be BIT-IDENTICAL (dm == 0, L35); DNg95@0.2 must land (dm > .01)
anch_dyn = {}
for tag, want in (("anchor:g100", 0.0), ("anchor:g95", 0.01)):
    amp = 0.8 if tag == "anchor:g100" else 0.2
    dms = [m["dm_max"] for m in spot[tag][amp]]
    if want == 0.0:
        ok = all(d == 0.0 for d in dms)
    else:
        ok = all(d > 0.01 for d in dms)
    anch_dyn[tag] = dict(dm=dms, ok=bool(ok))
    log(f"  dynamic anchor {tag}: dm {['%.4f' % d for d in dms]} -> "
        f"{'PASS' if ok else 'FAIL'}")

# C3 verdict per pick (PREREG): dm > .01 AND (|df|>.05 or |dS(Tr)|>.05) in >=2/3 seeds
c3 = {}
for famname, tname in picks.items():
    tag = f"{famname}:{tname}"
    for amp in AMPS:
        ms = spot[tag][amp]
        n_dm = sum(m["dm_max"] > 0.01 for m in ms)
        n_fx = sum((abs(m["f_Ti_a"] - m["f_Ti_c"]) > 0.05)
                   or (abs(m["STr_a"] - m["STr_c"]) > 0.05) for m in ms)
        c3[f"{tag}@{amp}"] = dict(
            dm_pass=bool(n_dm == 3), mod_seeds=int(n_fx),
            verdict="PASS" if (n_dm == 3 and n_fx >= 2) else
                    ("CEILING-PINNED" if (n_dm == 0 and float(anch.loc[tname, "u_max"]) > 0
                                          and float(anch.loc[tname, "mean_X"]) >= 0.95)
                     else ("LANDS-NOMOD" if n_dm == 3 else "ABSORBED")))
        log(f"  C3 {tag}@{amp}: dm {n_dm}/3 mod {n_fx}/3 -> {c3[f'{tag}@{amp}']['verdict']}")

# ---------- outputs ----------
cen.sort_values("u_max", ascending=False).to_csv("l36/census_l36.csv", index=False)
res = dict(
    n_nodes=n, n_edges=int(len(lsrc)),
    dn_cells=int(len(dn_cells)), dn_types=int(ntypes),
    atlas_types_total=len(atlas_types), atlas_types_absent=absent,
    census_family_counts=cen.family.value_counts().to_dict(),
    anchors=dict(dng100_u_max=a100, dng95_u_max=a95, c1_pass=bool(c1)),
    anchors_dyn=anch_dyn,
    c2=c2, picks=picks, spot=spot, c3=c3,
    runtime_s=round(time.time() - t0, 1))
json.dump(res, open("l36/results_l36.json", "w"), indent=1)
log(f"WROTE l36/census_l36.csv ({len(cen)} types) + results_l36.json "
    f"| total {time.time()-t0:.0f}s")
