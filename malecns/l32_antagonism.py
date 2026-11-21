"""L32: wiring-borne-antagonism — replicate 2609.38665 on our male_graph cord.

Pre-registered claim levels in l32/PREREG.md (written BEFORE this ran).
Uniform-tau rate model, RAW signed synapse-count weights (no indegree norm —
labeled deviation), sustained bilateral DNg100 drive, 3 global params only
(gain g, inhibition scale beta, drive d). Two sign arms:
  A "ours"   glut EXCITATORY (male_graph.pt convention)
  B "flyvis" glut INHIBITORY (paper convention)
Ladder nulls on the winning arm: density / degree / legblock (PREREG).
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
SETTLE = 400
SCAN_WIN = 800      # 8 s
CONF_WIN = 6000     # 60 s
SCAN_SEEDS = [11, 22]
CONF_SEEDS = [11, 22, 33]
BETAS = [0.5, 1.0, 2.0, 4.0]
DS = [0.05, 0.2, 0.8]
GRATIOS = [0.5, 0.7, 1.0, 1.4, 2.0]
PAIR_KEYS = ["Ti", "Tr"]

os.makedirs("l32", exist_ok=True)
t0 = time.time()
res = {"stage": "build"}


def log(*a):
    print(*a, flush=True)


# ---------- stage A: subnetwork ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
neuro = (lab["somaNeuromere"].astype(str).fillna("X").str.slice(0, 1)
         + lab["somaNeuromere"].astype(str).fillna("").str.slice(0, 0)).to_numpy()  # T/A/X coarse
neuro_full = lab["somaNeuromere"].astype("string").to_numpy()

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
log(f"sub nodes {keep.sum():,} (cord {cord.sum():,} + dn_into {int(dn_into.sum()):,}) "
    f"| raw edges in full graph {len(w):,}")

# restrict edges to kept nodes
emask = keep[gsrc] & keep[gdst]
gsrc, gdst, gw = gsrc[emask], gdst[emask], gw[emask]
log(f"sub edges {len(gsrc):,} | weight max {gw.max():.0f} median {np.median(gw):.1f}")

# local index
loc = -np.ones(len(ids), np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
lsup, ltyp, lneuro = sup[keep], typ[keep], neuro_full[keep]

# sign arms (raw counts x sign)
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
SIG_B = dict(SIG_A); SIG_B["glutamate"] = -1.0
lnt = nt_names[keep]
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
signB = np.array([SIG_B.get(t, 0.3) for t in lnt], np.float32)

# pools (local)
motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
PAIRS = {}
for k in PAIR_KEYS:
    f = np.where(motor & np.isin(ltyp, [f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (ltyp == f"{k} extensor MN"))[0]
    assert len(f) > 0 and len(e) > 0, (k, len(f), len(e))
    PAIRS[k] = (f, e)
    log(f"pair {k}: flex {len(f)} ext {len(e)}")
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2, dng100
log(f"DNg100: {len(dng100)} cells (bilateral drive)")

# blocks for legblock tier
blk = np.where(lsup == "vnc_sensory", "S",
               np.where(lsup == "descending_neuron", "DN", pd.Series(lneuro).fillna("X").str[0].to_numpy()))
blk = np.array([b if b in ("S", "DN", "T1", "T2", "T3") else ("A" if str(b).startswith("A") else "X") for b in blk])


def build_W(dst, src, vals):
    t = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([dst, src])).long(),
        torch.from_numpy(vals.astype(np.float32)), (n, n))
    return t.coalesce().to_sparse_csr()


def make_arm(sign):
    return gw * sign[lsrc]  # weights travel with source; sign per source cell


Wa_vals = make_arm(signA)
Wb_vals = make_arm(signB)
Wa = build_W(ldst, lsrc, Wa_vals)
Wb = build_W(ldst, lsrc, Wb_vals)
negA = float((Wa_vals < 0).mean()); negB = float((Wb_vals < 0).mean())
log(f"neg fraction: A {negA:.3f} B {negB:.3f} | {time.time()-t0:.0f}s")


# ---------- rollout ----------
def run(Wc, g, beta, d, seed, win, want_traces=False):
    """One noisy run: settle (no drive) then sustained d on DNg100 for win steps.
    Returns (af_settle, S dict, depth dict, freq dict, traces)."""
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= beta
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals,
                                 Wc.shape)
    I = torch.zeros(n, 1); I[dng100] = d
    Z = torch.zeros(n, 1)

    def step(cur, drive_I):
        drive = torch.sparse.mm(Wb, cur) * g + drive_I
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
        sl = slice(int(0.25 * T), T)  # drop transient (2 s scan / 15 s conf)
        for pk in PAIRS:
            a = traces[pk][0][sl]; b = traces[pk][1][sl]
            out_d[pk] = float(max(np.ptp(a), np.ptp(b)))
            sa, sb = a.std(), b.std()
            out_S[pk] = float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else np.nan
    return af, out_S, out_d, traces, mm


def rhythm_ratio(tr):
    """FFT peak/median power ratio in 0.5-10 Hz on a detrended trace."""
    x = tr - tr.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    band = (fr >= 0.5) & (fr <= 10)
    pb = ps[band]; fb = fr[band]
    if pb.max() <= 0:
        return 0.0, 0.0
    i = int(np.argmax(pb))
    med = max(np.median(pb), 1e-30)
    return float(pb[i] / med), float(fb[i])


# ---------- stage B: calibrate g per arm ----------
res_arm = {}
for arm, Wc in (("A", Wa), ("B", Wb)):
    ok = []
    for g in np.logspace(-7, -1, 13):
        try:
            af, *_ = run(Wc, float(g), 1.0, 0.0, 11, 50)
            if 0.02 < af < 0.60:
                ok.append(float(g))
        except AssertionError:
            pass
    if not ok:
        log(f"ARM {arm}: NO g in band — fails C1 (af band empty)")
        res_arm[arm] = {"g_band": [], "scan": []}
        continue
    gstar = float(np.exp(np.mean(np.log(ok))))
    log(f"ARM {arm}: g band [{min(ok):.2e},{max(ok):.2e}] -> g* {gstar:.2e} "
        f"| {time.time()-t0:.0f}s")
    res_arm[arm] = {"g_band": ok, "gstar": gstar, "scan": [], "W": Wc}

# ---------- stage C: scan ----------
for arm in list(res_arm):
    if not res_arm[arm].get("g_band"):
        continue
    Wc, gstar = res_arm[arm]["W"], res_arm[arm]["gstar"]
    best = None
    for gr in GRATIOS:
        g = gstar * gr
        for beta in BETAS:
            for d in DS:
                try:
                    Ss, ds_ = [], []
                    for s in SCAN_SEEDS:
                        af, S, dd, tr, _ = run(Wc, g, beta, d, s, SCAN_WIN, True)
                        Ss.append(S); ds_.append(dd)
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
                    res_arm[arm]["scan"].append(row)
                    if readable and (best is None or mS > best["mean_S"]):
                        best = row
                except AssertionError as e:
                    res_arm[arm]["scan"].append(
                        dict(g=float(g), beta=beta, d=d, invalid=str(e)))
    res_arm[arm]["frozen"] = best
    log(f"ARM {arm} scan: {len(res_arm[arm]['scan'])} settings | frozen "
        f"{None if best is None else (round(best['g'],6), best['beta'], best['d'])} "
        f"mean_S {None if best is None else round(best['mean_S'],3)} "
        f"rhythm {None if best is None else round(best['rhythm'],1)} "
        f"| {time.time()-t0:.0f}s", )
    json.dump({a: {k: v for k, v in r.items() if k != "W"} for a, r in res_arm.items()},
              open("l32/scan_l32.json", "w"), indent=1)

# ---------- stage D: confirmation on real, both arms ----------
for arm in list(res_arm):
    fz = res_arm[arm].get("frozen")
    if not fz:
        res_arm[arm]["confirm"] = None
        continue
    Wc = res_arm[arm]["W"]
    per_seed = []
    for s in CONF_SEEDS:
        af, S, dd, tr, mm = run(Wc, fz["g"], fz["beta"], fz["d"], s, CONF_WIN, True)
        rr, fr = rhythm_ratio(mm)
        per_seed.append(dict(seed=s, S=S, depth=dd, rhythm=rr, rhythm_f=fr, af=af))
    res_arm[arm]["confirm"] = per_seed
    Sm = {k: float(np.mean([p["S"][k] for p in per_seed])) for k in PAIRS}
    log(f"ARM {arm} CONFIRM 60s x{len(CONF_SEEDS)}: S {Sm} | rhythm "
        f"{np.mean([p['rhythm'] for p in per_seed]):.0f} @ "
        f"{np.mean([p['rhythm_f'] for p in per_seed]):.1f} Hz | {time.time()-t0:.0f}s")

json.dump({a: {k: v for k, v in r.items() if k != "W"} for a, r in res_arm.items()},
          open("l32/scan_l32.json", "w"), indent=1)
res_final = {a: {k: v for k, v in r.items() if k != "W"} for a, r in res_arm.items()}

# ---------- stage E: ladder on the arm with higher real S ----------
def mean_best_S(arm):
    c = res_arm[arm].get("confirm")
    if not c:
        return -9.9
    Sm = {k: float(np.mean([p["S"][k] for p in c])) for k in PAIRS}
    return max(Sm.values())


cand = [a for a in res_arm if res_arm[a].get("confirm")]
win_arm = max(cand, key=mean_best_S) if cand else None
log(f"ladder arm: {win_arm}")
if win_arm:
    fz = res_arm[win_arm]["frozen"]
    vals = Wa_vals if win_arm == "A" else Wb_vals
    negf = negA if win_arm == "A" else negB
    rng = np.random.default_rng(20261111)

    def ms_rewire(dst, src, groups=None, factor=8):
        """MS destination swaps; weights/signs stay with source. groups: per-edge
        group id — swaps only within a group (legblock tier)."""
        dst = dst.copy()
        Mn = len(dst)
        if groups is None:
            groups = np.zeros(Mn, np.int64)
        pairs = set((dst.astype(np.int64) * n + src).tolist())
        by_g = {}
        for i, gg in enumerate(groups):
            by_g.setdefault(gg, []).append(i)
        done = 0
        for gg, mem in by_g.items():
            mem = np.array(mem)
            if len(mem) < 2:
                continue
            ii = rng.choice(mem, factor * len(mem))
            jj = rng.choice(mem, factor * len(mem))
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
                pairs.add(a); pairs.add(b)
                dst[i], dst[j] = dst[j], dst[i]
                done += 1
        assert len(pairs) == Mn
        return dst, done

    def density_draw():
        src = rng.integers(0, n, len(ldst))
        dst = rng.integers(0, n, len(ldst))
        m = src != dst
        src, dst = src[m], dst[m]
        wmag = gw[rng.integers(0, len(gw), len(src))]
        sgn = np.where(rng.random(len(src)) < negf, -1.0, 1.0).astype(np.float32)
        return dst.astype(np.int64), src.astype(np.int64), (wmag * sgn).astype(np.float32)

    block_cell = blk[lsrc].astype(object) + ">" + blk[ldst].astype(object)
    cell_id = pd.factorize(block_cell)[0]

    tiers = {}
    for tier in ["density", "degree", "legblock"]:
        draws = []
        for dr in range(2):
            if tier == "density":
                dst2, src2, v2 = density_draw()
                swaps = -1
            else:
                groups = cell_id if tier == "legblock" else None
                dst2, swaps = ms_rewire(ldst, lsrc, groups)
                src2, v2 = lsrc, gw * (signA if win_arm == "A" else signB)[lsrc]
            Wn = build_W(dst2, src2, v2)
            per_seed = []
            for s in CONF_SEEDS:
                try:
                    af, S, dd, tr, mm = run(Wn, fz["g"], fz["beta"], fz["d"], s,
                                            CONF_WIN, True)
                    per_seed.append(dict(seed=s, S=S, depth=dd, af=af,
                                         rhythm=rhythm_ratio(mm)[0]))
                except AssertionError as e:
                    per_seed.append(dict(seed=s, invalid=str(e)))
            draws.append(dict(draw=dr, swaps=swaps, seeds=per_seed))
            Sm = {k: float(np.nanmean([p["S"][k] for p in per_seed
                                       if "S" in p])) for k in PAIRS}
            log(f"tier {tier} draw {dr}: S {Sm} swaps {swaps} | {time.time()-t0:.0f}s")
        tiers[tier] = draws
    res_final["ladder_arm"] = win_arm
    res_final["ladder"] = tiers

json.dump(res_final, open("l32/results_l32.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l32/results_l32.json")
