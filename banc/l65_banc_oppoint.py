"""L65: BANC female op-point + L32 antiphase replication (lab-only, CPU).

Stage 1  full-graph (80,635) gain bisection to ~15% active (male L11 form).
Stage 2  cord subnet (L32 form): raw log1p signed weights, sign arms A (glut exc)
         / B (flyvis glut inh), scan g x beta x d, sustained DNg100 drive,
         S = -corr(flex, ext) on Ti/Tr pools; confirm 60 s on frozen best/arm.
Stage 3  ladder: density + degree MS-rewired draws x3 (PREREG D3: no legblock).
PREREG: l65/PREREG.md (written first). Checkpoints: l65/scan_l65.json,
         l65/raw_l65.npz (pool traces, pre-analysis).
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
SETTLE = 400
SCAN_WIN = 800      # 8 s
CONF_WIN = 6000     # 60 s
SCAN_SEEDS = [11, 22]
CONF_SEEDS = [11, 22, 33]
BETAS = [0.5, 1.0, 2.0, 4.0]
DS = [0.05, 0.2, 0.8]
GRATIOS = [0.7, 1.0, 1.4]
PAIR_KEYS = ["Ti", "Tr"]
D = "/home/t3rpz/critters/peabrain-lab/banc/data"

os.makedirs("l65", exist_ok=True)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------------- stage 0: graph + annotations ----------------
G = torch.load("banc_graph.pt", weights_only=False)
ids_all = G["ids"].numpy().astype(np.uint64)
Nall = int(G["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
Wfull = G["W"]
sign_all = G["sign"].numpy()  # arm A convention (glut exc, hist -1, amines .2)

ann = pd.read_csv(f"{D}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv(f"{D}/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64),
                  nt["neurotransmitter_predicted"].astype(str).str.lower()))
is_glut = np.zeros(Nall, bool)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate":
        is_glut[j] = True
log(f"graph {Nall:,} nnz {G['n_edges']:,} | glut cells {is_glut.sum():,} "
    f"| {time.time()-t0:.0f}s")

# ---------------- stage 1: full-graph op-point bisection ----------------
def op_point(g, seed=11, steps=SETTLE):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(Nall, 1, generator=gen)).clamp(0, 1)
    for _ in range(steps):
        t = torch.relu(torch.sparse.mm(Wfull, X) * g + BG)
        t = (t + NOISE * torch.randn(Nall, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
    assert not torch.isnan(X).any()
    return float((X > 0.05).float().mean())


lo, hi = 1e-4, 1e1
curve = []
for it in range(18):
    g = float(np.sqrt(lo * hi))
    af = op_point(g)
    curve.append(dict(g=g, af=af))
    log(f"  bisect it{it}: g {g:.4g} -> af {af:.4f} | {time.time()-t0:.0f}s")
    if af < 0.13:
        lo = g
    elif af > 0.17:
        hi = g
    else:
        break
g_star = g
P1 = dict(g_star=g_star, af=af, curve=curve,
          in_band=bool(0.13 <= af <= 0.17))
log(f"P1 op-point: g* {g_star:.4g} af {af:.4f} in_band {P1['in_band']} "
    f"(male context 0.885) | {time.time()-t0:.0f}s")

# ---------------- stage 2a: cord subnet (L32 form, D4) ----------------
region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True

conn = pd.read_csv(f"{D}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all)
            & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
pre = np.array([int(a) for a, _ in g_grp.index], np.int64)
post = np.array([int(b) for _, b in g_grp.index], np.int64)
src_all = np.array([idx_all[r] for r in pre], np.int64)
dst_all = np.array([idx_all[r] for r in post], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into &= dn_all
keep = cord_mask | dn_into
log(f"subnet: cord {int(cord_mask.sum()):,} + dn_into {int(dn_into.sum()):,} "
    f"= {int(keep.sum()):,}")

emask = keep[src_all] & keep[dst_all]
gsrc, gdst = src_all[emask], dst_all[emask]
gcount = w_syn[emask]
log(f"subnet edges {len(gsrc):,} | syn {gcount.sum():,.0f} | "
    f"{time.time()-t0:.0f}s")

loc = -np.ones(Nall, np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
gsign_a = sign_all[gsrc]
gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
Wa_vals = (np.log1p(gcount) * gsign_a).astype(np.float32)
Wb_vals = (np.log1p(gcount) * gsign_b).astype(np.float32)

# pools (D2: semantic peripheral_target_type)
mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
mgi = mot_rows.gi.to_numpy()
in_sub = keep[mgi]


def pool(sel_str):
    m = in_sub & sel_str
    return loc[mgi[m]]


def has(s):
    return np.array([s in t for t in ptt])


PAIRS = {}
for k, fpat, epat in [
    ("Ti", (has("tibia") & has("flexor")), (has("tibia") & has("extensor"))),
    ("Tr", (has("trochanter") & has("flexor")), (has("trochanter") & has("extensor"))),
]:
    PAIRS[k] = (pool(fpat), pool(epat))
    log(f"pair {k}: flex {len(PAIRS[k][0])} ext {len(PAIRS[k][1])}")

ct = ann[ann.super_class == "descending"].cell_type.fillna("").astype(str)
sub_dn = ann[ann.super_class == "descending"]
dng100_all = sub_dn.gi[sub_dn.cell_type.fillna("").astype(str)
                        .to_numpy() == "DNg100"].to_numpy()
dng100 = np.sort(loc[dng100_all[keep[dng100_all]]])
motor = np.zeros(n, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor[loc[mg[keep[mg]]]] = True
log(f"DNg100 in subnet: {len(dng100)} | motor cells {int(motor.sum())}")

C0 = dict(
    Ti_flex=len(PAIRS["Ti"][0]) >= 90, Ti_ext=len(PAIRS["Ti"][1]) >= 10,
    Tr_flex=len(PAIRS["Tr"][0]) >= 50, Tr_ext=len(PAIRS["Tr"][1]) >= 40,
    dng100=len(dng100) == 2,
    same_structure=bool(len(Wa_vals) == len(Wb_vals)),
    negB_gt_A=bool((Wb_vals < 0).mean() > (Wa_vals < 0).mean()),
)
log(f"C0 anchors: {C0}")
assert all(C0.values()), "C0 failed — stop before verdicts"


def build_W(dst, src, vals):
    t = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([dst, src])).long(),
        torch.from_numpy(vals.astype(np.float32)), (n, n))
    return t.coalesce().to_sparse_csr()


Wa = build_W(ldst, lsrc, Wa_vals)
Wb = build_W(ldst, lsrc, Wb_vals)
log(f"arms built (nnz {Wa._nnz():,}) | {time.time()-t0:.0f}s")

# ---------------- rollout (L32 form) ----------------
def run(Wc, g, beta, d, seed, win, want_traces=False):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= beta
    Wbeta = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals,
                                    Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = d
    Z = torch.zeros(n, 1)

    def step(cur, drive_I):
        drive = torch.sparse.mm(Wbeta, cur) * g + drive_I
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for _ in range(SETTLE):
        X = step(X, Z)
    af = float((X > 0.05).float().mean())
    assert 0.01 < af < 0.9, f"op-point {af:.3f}"
    assert not torch.isnan(X).any(), "NaN"
    T = win
    traces = {k: (np.zeros(T, np.float32), np.zeros(T, np.float32))
              for k in PAIRS} if want_traces else None
    mm = np.zeros(T, np.float32) if want_traces else None
    for k in range(T):
        X = step(X, I)
        if want_traces:
            for pk, (f, e) in PAIRS.items():
                traces[pk][0][k] = X[f].mean()
                traces[pk][1][k] = X[e].mean()
            mm[k] = X[motor].mean()
    out_S, out_d = {}, {}
    if want_traces:
        sl = slice(int(0.25 * T), T)
        for pk in PAIRS:
            a = traces[pk][0][sl]
            b = traces[pk][1][sl]
            out_d[pk] = float(max(np.ptp(a), np.ptp(b)))
            sa, sb = a.std(), b.std()
            out_S[pk] = float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else np.nan
    return af, out_S, out_d, traces, mm


def rhythm_ratio(tr):
    x = tr - tr.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    band = (fr >= 0.5) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    if pb.max() <= 0:
        return 0.0, 0.0
    i = int(np.argmax(pb))
    return float(pb[i] / max(np.median(pb), 1e-30)), float(fb[i])


# ---------------- stage 2b: per-arm g band + scan ----------------
ARM_W = {"A": Wa, "B": Wb}
ARM_VALS = {"A": Wa_vals, "B": Wb_vals}
res = {"P1": P1, "C0": C0, "subnet": dict(n=n, edges=len(lsrc),
      cord=int(cord_mask.sum()), dn_into=int(dn_into.sum())),
      "pools": {k: [len(v[0]), len(v[1])] for k, v in PAIRS.items()},
      "arms": {}}
for arm, Wc in ARM_W.items():
    ok = []
    for g in np.logspace(-7, -1, 13):
        try:
            af, *_ = run(Wc, float(g), 1.0, 0.0, 11, 50)
            if 0.02 < af < 0.60:
                ok.append(float(g))
        except AssertionError:
            pass
    if not ok:
        log(f"ARM {arm}: NO g in band (C1)")
        res["arms"][arm] = {"g_band": [], "scan": []}
        continue
    gstar_sub = float(np.exp(np.mean(np.log(ok))))
    log(f"ARM {arm}: g band [{min(ok):.2e},{max(ok):.2e}] -> g* {gstar_sub:.2e}")
    scan = []
    best = None
    for gr in GRATIOS:
        g = gstar_sub * gr
        for beta in BETAS:
            for d in DS:
                try:
                    Ss, ds_ = [], []
                    for s in SCAN_SEEDS:
                        af, S, dd, tr, _ = run(Wc, g, beta, d, s, SCAN_WIN, True)
                        Ss.append(S)
                        ds_.append(dd)
                    Smean = {k: float(np.nanmean([x[k] for x in Ss])) for k in PAIRS}
                    readable = [k for k in PAIRS
                                if all(d_[k] >= 0.03 for d_ in ds_)]
                    mS = (float(np.mean([Smean[k] for k in readable]))
                          if readable else np.nan)
                    rr, fr = rhythm_ratio(
                        np.concatenate([tr[k][0] for k in PAIRS]))
                    row = dict(g=float(g), beta=beta, d=d, S=Smean,
                               readable=readable, mean_S=mS, rhythm=rr,
                               rhythm_f=fr, af=af)
                    scan.append(row)
                    if readable and (best is None or mS > best["mean_S"]):
                        best = row
                except AssertionError as e:
                    scan.append(dict(g=float(g), beta=beta, d=d, invalid=str(e)))
    res["arms"][arm] = {"g_band": ok, "gstar": gstar_sub, "scan": scan,
                        "frozen": best}
    log(f"ARM {arm} scan {len(scan)} rows | frozen "
        f"{None if best is None else (round(best['g'], 6), best['beta'], best['d'], round(best['mean_S'], 3))} "
        f"| {time.time()-t0:.0f}s")
json.dump(res, open("l65/scan_l65.json", "w"), indent=1)

# ---------------- stage 2c: confirm 60 s on both arms ----------------
npz = {}
for arm in res["arms"]:
    fz = res["arms"][arm].get("frozen")
    if not fz:
        res["arms"][arm]["confirm"] = None
        continue
    per_seed = []
    for s in CONF_SEEDS:
        af, S, dd, tr, mm = run(ARM_W[arm], fz["g"], fz["beta"], fz["d"], s,
                                CONF_WIN, True)
        rr, fr = rhythm_ratio(mm)
        per_seed.append(dict(seed=s, S=S, depth=dd, rhythm=rr, rhythm_f=fr,
                             af=af))
        for pk in PAIRS:  # checkpoint raw traces pre-analysis
            npz[f"{arm}_s{s}_{pk}_f"] = tr[pk][0]
            npz[f"{arm}_s{s}_{pk}_e"] = tr[pk][1]
            npz[f"{arm}_s{s}_mm"] = mm
    res["arms"][arm]["confirm"] = per_seed
    Sm = {k: float(np.mean([p["S"][k] for p in per_seed])) for k in PAIRS}
    log(f"ARM {arm} CONFIRM 60 s: S {Sm} | rhythm "
        f"{np.mean([p['rhythm'] for p in per_seed]):.0f} @ "
        f"{np.mean([p['rhythm_f'] for p in per_seed]):.1f} Hz | "
        f"{time.time()-t0:.0f}s")

# ---------------- stage 3: ladder on higher-real-S arm ----------------
def best_pair_mean(arm):
    c = res["arms"][arm].get("confirm")
    if not c:
        return -9.9, None
    Sm = {k: float(np.mean([p["S"][k] for p in c])) for k in PAIRS}
    k = max(Sm, key=Sm.get)
    return Sm[k], k


cand = [a for a in res["arms"] if res["arms"][a].get("confirm")]
win_arm = max(cand, key=lambda a: best_pair_mean(a)[0]) if cand else None
log(f"ladder arm: {win_arm}")
if win_arm:
    real_S, bp = best_pair_mean(win_arm)
    fz = res["arms"][win_arm]["frozen"]
    vals_arm = ARM_VALS[win_arm]
    negf = float((vals_arm < 0).mean())
    rng = np.random.default_rng(20261114)

    def ms_rewire(dst, src, factor=8):
        dst = dst.copy()
        Mn = len(dst)
        pairs = set((dst.astype(np.int64) * n + src).tolist())
        ii = rng.choice(Mn, factor * Mn)
        jj = rng.choice(Mn, factor * Mn)
        done = 0
        for k in range(len(ii)):
            i, j = int(ii[k]), int(jj[k])
            if i == j:
                continue
            a = dst[i] * n + src[j]
            b = dst[j] * n + src[i]
            if a in pairs or b in pairs or src[j] == dst[i] or src[i] == dst[j]:
                continue
            pairs.discard(dst[i] * n + src[i])
            pairs.discard(dst[j] * n + src[j])
            pairs.add(a)
            pairs.add(b)
            dst[i], dst[j] = dst[j], dst[i]
            done += 1
        assert len(pairs) == Mn
        return dst, done

    wpool = np.abs(vals_arm)
    tiers = {}
    for tier in ["density", "degree"]:
        draws = []
        for dr in range(3):
            if tier == "density":
                src2 = rng.integers(0, n, len(ldst))
                dst2 = rng.integers(0, n, len(ldst))
                m = src2 != dst2
                src2, dst2 = src2[m].astype(np.int64), dst2[m].astype(np.int64)
                v2 = (wpool[rng.integers(0, len(wpool), len(src2))]
                      * np.where(rng.random(len(src2)) < negf, -1.0, 1.0)
                      ).astype(np.float32)
                swaps = -1
            else:
                dst2, swaps = ms_rewire(ldst, lsrc)
                src2, v2 = lsrc, vals_arm
                # degree preservation assert (C0)
                assert np.array_equal(np.bincount(ldst, minlength=n),
                                      np.bincount(dst2, minlength=n))
                assert np.array_equal(np.bincount(lsrc, minlength=n),
                                      np.bincount(src2, minlength=n))
            Wn = build_W(dst2, src2, v2)
            per_seed = []
            for s in CONF_SEEDS:
                try:
                    af, S, dd, tr, mm = run(Wn, fz["g"], fz["beta"], fz["d"], s,
                                            CONF_WIN, True)
                    per_seed.append(dict(seed=s, S=S, depth=dd, af=af,
                                         rhythm=rhythm_ratio(mm)[0]))
                    for pk in PAIRS:
                        npz[f"{tier}{dr}_s{s}_{pk}_f"] = tr[pk][0]
                        npz[f"{tier}{dr}_s{s}_{pk}_e"] = tr[pk][1]
                except AssertionError as e:
                    per_seed.append(dict(seed=s, invalid=str(e)))
            draws.append(dict(draw=dr, swaps=swaps, seeds=per_seed))
            Sm = {k: float(np.nanmean([p["S"][k] for p in per_seed
                                       if "S" in p])) for k in PAIRS}
            log(f"tier {tier} draw {dr}: S {Sm} swaps {swaps} | "
                f"{time.time()-t0:.0f}s")
        tiers[tier] = draws
    res["ladder_arm"] = win_arm
    res["ladder_best_pair"] = bp
    res["ladder_real_S"] = real_S
    res["ladder"] = tiers

np.savez_compressed("l65/raw_l65.npz", **npz)
json.dump(res, open("l65/results_l65.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l65/results_l65.json")
