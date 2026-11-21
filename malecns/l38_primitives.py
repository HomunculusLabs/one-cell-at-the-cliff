"""L38: viable-primitive-table — the endgame (d_L,d_R) enumeration.

Join the L36 census machinery (per-CELL this time, split by somaSide) onto
l31/cx_dn.csv -> the honest EXECUTABLE action set for a learned gait policy,
plus dose-response (amp -> df_Ti) curves for channels BOTH signs:
DNge046 per side, DNg110 (viable), MDN / DNg88 negative (ceiling-pinned
deceleration candidates, L36). PREREG: l38/PREREG.md. CPU-only; no live
changes.
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
SETTLE, WIN = 400, 600
G, BETA = 0.01, 2.0
SEEDS = [11, 22, 33]
SPOT_WIN = 6000
MEAS0 = int(0.25 * SPOT_WIN)     # measure last 45 s (L34 window lesson)
PAIR_KEYS = ["Ti", "Tr"]

os.makedirs("l38", exist_ok=True)
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
side_raw = lab["somaSide"].to_numpy()
side_all = np.array([s if isinstance(s, str) else "?" for s in side_raw])

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
lside = side_all[keep]
assert n == 21516, f"nodes {n}"
assert len(lsrc) == 2977920, f"edges {len(lsrc)}"
log(f"substrate OK: {n:,} nodes / {len(lsrc):,} edges (L32-L37 identical)")

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


def step(cur, drive_I, gen):
    drive = torch.sparse.mm(Wb, cur) * G + drive_I
    t = torch.relu(drive + BG)
    t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
    return cur + (DT / TAU) * (t - cur)


# ---------- per-CELL census, split by somaSide ----------
dn_mask = lsup == "descending_neuron"
dn_cells = np.where(dn_mask)[0]
tcodes, tnames = pd.factorize(ltyp[dn_cells], sort=True)
ntypes = len(tnames)
dn_side = lside[dn_cells]
side_codes = {s: i for i, s in enumerate(["L", "R", "M", "?"])}
dn_side_code = np.array([side_codes.get(s, 3) for s in dn_side])
log(f"DN cells in sub: {len(dn_cells):,} / {ntypes} types | sides "
    f"L {int((dn_side=='L').sum())} R {int((dn_side=='R').sum())} other "
    f"{int((~np.isin(dn_side,['L','R'])).sum())}")

umax_cell = np.full(len(dn_cells), -1e9, np.float64)
usum_cell = np.zeros(len(dn_cells), np.float64)
upos_cell = np.zeros(len(dn_cells), np.float64)
xsum_cell = np.zeros(len(dn_cells), np.float64)
xcnt = 0.0
for seed in SEEDS:
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    for _ in range(SETTLE):
        X = step(X, Z, gen)
    af = float((X > 0.05).float().mean())
    assert 0.01 < af < 0.9, f"op-point {af:.3f}"
    for _ in range(WIN):
        X = step(X, Z, gen)
        u = (torch.sparse.mm(Wb, X) * G + BG)[dn_cells, 0].numpy()
        umax_cell = np.maximum(umax_cell, u)
        usum_cell += u
        upos_cell += (u > 0)
        xsum_cell += X[dn_cells, 0].numpy()
        xcnt += 1
    log(f"  census seed {seed}: af {af:.3f} | {time.time()-t0:.0f}s")

ucnt_cell = np.full(len(dn_cells), xcnt)
umean_cell = usum_cell / ucnt_cell
fpos_cell = upos_cell / ucnt_cell
xmean_cell = xsum_cell / xcnt


def side_verdict(u_max, mean_x, ncells):
    if ncells == 0:
        return "absent"
    if u_max > 0 and mean_x >= 0.95:
        return "pinned"
    if u_max > 0:
        return "viable"
    if u_max > -0.8:
        return "need-amp"
    return "buried"


# per (type, side) stats
rows = []
for ti, tname in enumerate(tnames):
    row = dict(dn_type=str(tname))
    for sd in ("L", "R"):
        cm = (tcodes == ti) & (dn_side_code == side_codes[sd])
        ns = int(cm.sum())
        if ns:
            um, xm = float(umax_cell[cm].max()), float(xmean_cell[cm].mean())
            row[f"n_{sd}"] = ns
            row[f"u_max_{sd}"] = um
            row[f"u_mean_{sd}"] = float(umean_cell[cm].mean())
            row[f"mean_X_{sd}"] = xm
            row[f"frac_pos_{sd}"] = float(fpos_cell[cm].mean())
            row[f"verdict_{sd}"] = side_verdict(um, xm, ns)
        else:
            row[f"n_{sd}"] = 0
            row[f"u_max_{sd}"] = np.nan
            row[f"u_mean_{sd}"] = np.nan
            row[f"mean_X_{sd}"] = np.nan
            row[f"frac_pos_{sd}"] = np.nan
            row[f"verdict_{sd}"] = "absent"
    # type-level compare (L36 form, union of cells)
    cm = tcodes == ti
    um = float(umax_cell[cm].max())
    xm = float(xmean_cell[cm].mean())
    row["u_max_type"] = um
    row["mean_X_type"] = xm
    row["cells_dyn_type"] = int(((umax_cell[cm] > 0) & (xmean_cell[cm] < 0.95)).sum())
    rows.append(row)
cen = pd.DataFrame(rows)

# C1 anchor: per-side split reproduces L37's dm finding
c1 = {}
for tname, want in (("DNge059", ("buried-or-neg", "pos")),
                    ("DNge046", ("pos", "buried-or-neg"))):
    r = cen.set_index("dn_type").loc[tname]
    lmax, rmax = r.u_max_L, r.u_max_R
    got = ("pos" if lmax > 0 else "neg", "pos" if rmax > 0 else "neg")
    ok = (got[0] == want[0] and got[1] == want[1])
    c1[tname] = dict(u_max_L=float(lmax), u_max_R=float(rmax), ok=bool(ok))
    log(f"C1 {tname}: u_max L {lmax:+.3f} / R {rmax:+.3f} -> "
        f"{'PASS' if ok else 'FAIL'} (want {want})")
c1_pass = all(v["ok"] for v in c1.values())

# ---------- join L31 + L36 + L37 ----------
cxdn = pd.read_csv("l31/cx_dn.csv")
cen = cen.merge(cxdn, on="dn_type", how="outer", indicator=True)
cen["in_sub"] = cen["_merge"] != "left_only"
cen.drop(columns="_merge", inplace=True)


def fam(r):
    ws = {"flex": r.w_flex if pd.notna(r.w_flex) else 0.0,
          "ext": r.w_ext if pd.notna(r.w_ext) else 0.0,
          "jump": r.w_jump if pd.notna(r.w_jump) else 0.0}
    f = max(ws, key=ws.get)
    return f if ws[f] >= 0.25 else "none/diffuse"


cen["family"] = cen.apply(fam, axis=1)

# L36 type-level cells_dyn join for drift check
l36c = pd.read_csv("l36/census_l36.csv")[["dn_type", "u_max", "mean_X", "cells_dyn"]]
l36c = l36c.rename(columns={"u_max": "u_max_l36", "mean_X": "mean_X_l36",
                            "cells_dyn": "cells_dyn_l36"})
cen = cen.merge(l36c, on="dn_type", how="left")

# L37 dynamic landing evidence fold (dm per channel/side/amp)
l37 = json.load(open("l37/results_l37.json"))
for tag, arm in l37["arms"].items():
    if tag == "base" or "channel" not in arm:
        continue
    ch, sd, amp = arm["channel"], arm["side"], arm["amp"]
    dms = [s["dm"] for s in arm["seeds"]]
    col = f"l37_dm_{sd}_{amp}"
    if col not in cen.columns:
        cen[col] = np.nan
    cen.loc[cen.dn_type == ch, col] = float(np.mean(dms))

cen.to_csv("l38/primitives_viable.csv", index=False)
fam_atlas = cen[cen.family.isin(["flex", "ext", "jump"]) & cen.in_sub]
side_viable = {f: int(((fam_atlas.family == f) &
                       ((fam_atlas.verdict_L == "viable") |
                        (fam_atlas.verdict_R == "viable"))).sum())
               for f in ("flex", "ext", "jump")}
c2 = dict(n_rows=int(len(cen)), n_in_sub=int(cen.in_sub.sum()),
          side_viable=side_viable,
          side_split_types=int((((cen.verdict_L != cen.verdict_R) &
                                 cen.in_sub)).sum()),
          gate=bool(side_viable.get("flex", 0) >= 1 and side_viable.get("jump", 0) >= 1))
log(f"C2 table: {c2}")


# ---------- dose-response arms (L36 run_pair verbatim) ----------
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

    for _ in range(SETTLE):
        Xc, Xa = step2(Xc, Xa, False)   # drive AFTER settle (L36 lesson)
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


def cells_of(tname, sd=None):
    cm = ltyp == tname
    if sd is not None:
        cm &= lside == sd
    return np.where(cm)[0]


ARMS = []
for sd in ("L", "R"):
    for amp in (-0.8, -0.4, -0.2, 0.2, 0.4, 0.8):
        ARMS.append((f"DNge046_{sd}", cells_of("DNge046", sd), amp))
for amp in (-0.8, -0.4, -0.2, 0.2, 0.4, 0.8):
    ARMS.append(("DNg110", cells_of("DNg110"), amp))
for amp in (-1.0, -2.0, -4.0, -8.0):
    ARMS.append(("MDN", cells_of("MDN"), amp))
for amp in (-2.0, -4.0, -8.0, -12.0):
    ARMS.append(("DNg88", cells_of("DNg88"), amp))
ARMS.append(("anchor:g100", cells_of("DNg100"), 0.8))
ARMS.append(("anchor:g95", cells_of("DNg95"), 0.2))

spot = {}
for tag, cells, amp in ARMS:
    assert len(cells) > 0, tag
    spot[f"{tag}@{amp}"] = [run_pair(cells, amp, s) for s in SEEDS]
    ms = spot[f"{tag}@{amp}"]
    dms = ", ".join("%.4f" % m["dm_max"] for m in ms)
    dfs = ", ".join("%+.3f" % (m["f_Ti_a"] - m["f_Ti_c"]) for m in ms)
    sss = ", ".join("%+.2f" % m["STr_a"] for m in ms)
    log(f"  {tag}@{amp}: n={len(cells)} dm [{dms}] df(Ti) [{dfs}]"
        f" S_Tr [{sss}] | {time.time()-t0:.0f}s")

# C0 dynamic anchors
c0 = {}
for tag, want in (("anchor:g100", 0.0), ("anchor:g95", 0.01)):
    key = f"{tag}@{0.8 if 'g100' in tag else 0.2}"
    dms = [m["dm_max"] for m in spot[key]]
    ok = all(d == 0.0 for d in dms) if want == 0.0 else all(d > 0.01 for d in dms)
    c0[tag] = dict(dm=dms, ok=bool(ok))
    log(f"C0 {tag}: dm {['%.4f' % d for d in dms]} -> {'PASS' if ok else 'FAIL'}")

# C3 positive throttle (non-decreasing |df| over landing grid)
c3 = {}
for chan in ("DNge046_L", "DNge046_R", "DNg110"):
    pos = [(a, [m["f_Ti_a"] - m["f_Ti_c"] for m in spot[f"{chan}@{a}"]])
           for a in (0.2, 0.4, 0.8)]
    lands = all(all(m["dm_max"] > 0.01 for m in spot[f"{chan}@{a}"]) for a in (0.2, 0.4, 0.8))
    meds = [np.median([d for d in df]) for _, df in pos]
    mono = all(meds[i + 1] >= meds[i] - 0.05 for i in range(len(meds) - 1))
    c3[chan] = dict(lands=bool(lands), med_df=[float(m) for m in meds],
                    monotone=bool(mono), gate=bool(lands and mono))
    log(f"C3 {chan}: lands {lands} med df(Ti) {['%+.3f' % m for m in meds]}"
        f" mono {mono} -> {'PASS' if c3[chan]['gate'] else 'FAIL'}")

# C4 deceleration: df < 0 in >=2/3 seeds at amp <= -u_max, or rhythm collapse
c4 = {}
for chan in ("MDN", "DNg88"):
    r = cen.set_index("dn_type").loc[chan]
    umax = float(np.nanmax([r.u_max_L, r.u_max_R]))
    hits = []
    for a in (-8.0, -12.0, -4.0, -2.0, -1.0):
        key = f"{chan}@{a}"
        if key not in spot or a > -umax:
            continue
        ms = spot[key]
        nslow = sum(m["f_Ti_a"] - m["f_Ti_c"] < -0.05 for m in ms)
        nkill = sum((m["STr_a"] < 0.1) and (m["STr_c"] >= 0.3) for m in ms)
        lands = all(m["dm_max"] > 0.01 for m in ms)
        hits.append(dict(amp=a, nslow=int(nslow), nkill=int(nkill), lands=bool(lands)))
    ok = any(h["nslow"] >= 2 or h["nkill"] >= 2 for h in hits)
    c4[chan] = dict(u_max=float(umax), hits=hits, gate=bool(ok))
    log(f"C4 {chan}: u_max {umax:+.1f} hits {hits} -> {'PASS' if ok else 'FAIL'}")

# C5 negative-floor control: buried side of DNge046 at -0.8
buried_side = "R" if c1.get("DNge046", {}).get(
    "u_max_L", 0) > 0 else "L" if "DNge046" in c1 else None
key = f"DNge046_{buried_side}@-0.8"
c5 = dict(side=buried_side, dm=[m["dm_max"] for m in spot[key]],
          gate=all(m["dm_max"] == 0.0 for m in spot[key]))
log(f"C5 buried side {buried_side} @-0.8: dm "
    f"{['%.4f' % m['dm_max'] for m in spot[key]]} -> "
    f"{'PASS' if c5['gate'] else 'FAIL'}")

res = dict(
    n_nodes=n, n_edges=int(len(lsrc)),
    dn_cells=int(len(dn_cells)), dn_types=int(ntypes),
    c0=c0, c1=c1, c1_pass=bool(c1_pass), c2=c2, c3=c3, c4=c4, c5=c5,
    spot=spot, runtime_s=round(time.time() - t0, 1))
json.dump(res, open("l38/results_l38.json", "w"), indent=1)
log(f"WROTE l38/primitives_viable.csv ({len(cen)} rows) + results_l38.json"
    f" | total {time.time()-t0:.0f}s")
