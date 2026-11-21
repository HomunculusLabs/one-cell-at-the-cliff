"""L37: steering-revisited — L33's tonic-bias grid on L36-VIABLE channels.

L33 verdicted "tonic bias cannot steer" using DNg95, whose bias enters on
~1% of steps (L36 census frac_pos .011, u_max .047). L36 shipped 34
viable-modulating DN types (tonic drive lands, frequency-modulates the
intrinsic rhythm). This card re-runs the unilateral tonic-bias grid on
three viable flex channels with paired lockstep (ONE generator, ONE shared
per-step noise), drive AFTER settle, dm/first_div honesty probes, and
PREREG gates C0-C4 evaluated inline. P1-labeled; CPU-only; no live changes.
"""
import json
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 400
WIN = 6000            # 60 s
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05          # l32 arm-A frozen, verbatim
AMPS = [0.05, 0.2, 0.8]
CHANNELS = ["DNge059", "DNg105", "DNge046"]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: subnetwork (l32/l33 verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()

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
lsup, ltyp, lside = sup[keep], typ[keep], side[keep]
lnt = nt_names[keep]
log(f"sub nodes {n:,} | edges {len(gsrc):,} | {time.time()-t0:.0f}s")

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wa_vals = gw * signA[lsrc]

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
flexL = np.concatenate([PAIRS[k]["fL"] for k in PAIRS])
flexR = np.concatenate([PAIRS[k]["fR"] for k in PAIRS])
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2

Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy(Wa_vals.astype(np.float32)), (n, n)).coalesce().to_sparse_csr()
neg = Wc.values() < 0
vals = Wc.values().clone()
vals[neg] *= BETA
Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)


# ---------- stage B: static sign composition per channel ----------
chans = {}
for ct in CHANNELS:
    cL = np.where((ltyp == ct) & (lside == "L"))[0]
    cR = np.where((ltyp == ct) & (lside == "R"))[0]
    assert len(cL) and len(cR), (ct, len(cL), len(cR))
    eL_mask = np.isin(lsrc, cL)
    wLL = Wa_vals[eL_mask & np.isin(ldst, flexL)].sum()
    wLR = Wa_vals[eL_mask & np.isin(ldst, flexR)].sum()
    eR_mask = np.isin(lsrc, cR)
    wRL = Wa_vals[eR_mask & np.isin(ldst, flexL)].sum()
    wRR = Wa_vals[eR_mask & np.isin(ldst, flexR)].sum()
    pred = np.sign(wLL - wLR)          # drive-L cells: net pull on L vs R flexor mass
    chans[ct] = dict(cL=cL, cR=cR, wLL=float(wLL), wLR=float(wLR),
                     wRL=float(wRL), wRR=float(wRR), pred_L=float(pred))
    log(f"chan {ct}: L-cells {len(cL)} R-cells {len(cR)} | w(L->flexL) {wLL:+.1f} "
        f"w(L->flexR) {wLR:+.1f} w(R->flexL) {wRL:+.1f} w(R->flexR) {wRR:+.1f} "
        f"| pred turn shift (drive L) {pred:+.0f}")

rng_np = np.random.default_rng(20261113)
dncells = np.where(lsup == "descending_neuron")[0]
pool = dncells[~np.isin(ltyp[dncells], CHANNELS + ["DNg95", "DNg100"])]
rand_pairs = [rng_np.choice(pool, 2, replace=False) for _ in range(2)]
log(f"rand null pairs: {[list(map(int, p)) for p in rand_pairs]} | {time.time()-t0:.0f}s")


# ---------- stage C: paired lockstep ----------
def metrics(tr, mm):
    sl = slice(int(0.25 * WIN), WIN)
    out = dict(S_pooled={}, S_side={}, turn={}, mass={}, depth={}, rhythm={})
    for k in PAIRS:
        a = tr[k]["fL"][sl] + tr[k]["fR"][sl]
        b = tr[k]["eL"][sl] + tr[k]["eR"][sl]
        out["S_pooled"][k] = float(-np.corrcoef(a, b)[0, 1]) if a.std() > 1e-6 and b.std() > 1e-6 else np.nan
        for s_ in ("L", "R"):
            x1, x2 = tr[k][f"f{s_}"][sl], tr[k][f"e{s_}"][sl]
            out["S_side"][k + s_] = float(-np.corrcoef(x1, x2)[0, 1]) if x1.std() > 1e-6 and x2.std() > 1e-6 else np.nan
            out["depth"][k + s_ + "f"] = float(x1.max() - x1.min())
        for c in ("f", "e"):
            mL, mR = tr[k][f"{c}L"][sl].mean(), tr[k][f"{c}R"][sl].mean()
            out["turn"][k + c] = float((mL - mR) / (mL + mR + 1e-9))
        out["mass"][k] = dict(mL=float(tr[k]["fL"][sl].mean()),
                              mR=float(tr[k]["fR"][sl].mean()))
    x = mm[sl] - mm[sl].mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    band = (fr >= 0.5) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    out["rhythm"] = dict(ratio=float(pb[i] / max(np.median(pb), 1e-30)), f=float(fb[i]))
    # per-side flexor rhythm frequency (Ti pooled per side)
    for s_ in ("L", "R"):
        y = tr["Ti"][f"f{s_}"][sl]
        y = y - y.mean()
        ps_ = np.abs(np.fft.rfft(y)) ** 2
        pb_, fb_ = ps_[band], fr[band]
        j = int(np.argmax(pb_))
        out[f"f_f{s_}"] = float(fb_[j])
    out["df_side"] = out["f_fL"] - out["f_fR"]
    return out


def pair_run(steer_cells, amp, seed, base_ref=None):
    """One generator, ONE shared per-step noise; base+steer in lockstep.
    Steer current applied ONLY after settle (L36 rule)."""
    gen = torch.Generator().manual_seed(seed)
    Xb = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    Xs = Xb.clone()
    Ib = torch.zeros(n, 1)
    Ib[dng100] = D
    Is = Ib.clone()
    if steer_cells is not None:
        Is[np.asarray(steer_cells)] = amp
    Z = torch.zeros(n, 1)

    def step(cur, I, nz):
        drive = torch.sparse.mm(Wb, cur) * G + I
        t = torch.relu(drive + BG)
        t = (t + nz).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for _ in range(SETTLE):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        Xb = step(Xb, Ib, nz)
        Xs = step(Xs, Ib, nz)          # settle is steer-free
    if base_ref is not None:
        assert torch.equal(Xb, base_ref), "base lockstep broken"
    if base_ref is None:
        out_ref = Xb.clone()
    afb = float((Xb > 0.05).float().mean())
    afs = float((Xs > 0.05).float().mean())
    assert 0.01 < afb < 0.9, f"op-point base {afb:.3f}"
    assert 0.01 < afs < 0.95, f"op-point steer {afs:.3f}"
    keys = ["fL", "fR", "eL", "eR"]
    trb = {k: {c: np.zeros(WIN, np.float32) for c in keys} for k in PAIRS}
    trs = {k: {c: np.zeros(WIN, np.float32) for c in keys} for k in PAIRS}
    mmb = np.zeros(WIN, np.float32)
    mms = np.zeros(WIN, np.float32)
    first_div = None
    dm = 0.0
    for i in range(WIN):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        Xb = step(Xb, Ib, nz)
        Xs = step(Xs, Is, nz)
        d = float((Xs - Xb).abs().max())
        dm = max(dm, d)
        if first_div is None and d > 1e-6:
            first_div = i
        for k, pools in PAIRS.items():
            for c in keys:
                trb[k][c][i] = Xb[pools[c]].mean()
                trs[k][c][i] = Xs[pools[c]].mean()
        mmb[i] = Xb[motor].mean()
        mms[i] = Xs[motor].mean()
    out = dict(afb=afb, afs=afs, dm=dm, first_div=first_div,
               steer=metrics(trs, mms))
    if base_ref is None:
        out["base"] = metrics(trb, mmb)
        out["base_settled"] = out_ref
    else:
        out["base"] = None
    return out


ARMS = [("base", None, None, 0.0)]
for ct in CHANNELS:
    for a in AMPS:
        ARMS.append((f"{ct}_Lx{a}", ct, "L", a))
for ct in CHANNELS:
    ARMS.append((f"{ct}_Rx0.8", ct, "R", 0.8))
for dr, p in enumerate(rand_pairs):
    ARMS.append((f"rand{dr}", None, "P", 0.8))

res = dict(n_nodes=n, n_edges=int(len(gsrc)), chans={k: {kk: vv for kk, vv in v.items()
           if kk not in ("cL", "cR")} for k, v in chans.items()},
           rand_pairs=[list(map(int, p)) for p in rand_pairs], arms={})
base_metrics = {}      # seed -> metrics of base arm
base_final = {}        # seed -> Xb final tensor
for name, ct, s_, amp in ARMS:
    per = []
    for s in SEEDS:
        cells = None
        if ct is not None:
            cells = chans[ct]["cL"] if s_ == "L" else chans[ct]["cR"]
        elif s_ == "P":
            cells = rand_pairs[int(name[-1])]
        ref = base_final.get(s)
        o = pair_run(cells, amp, s, base_ref=ref)
        if name == "base":
            base_metrics[s] = o.pop("base")
            base_final[s] = o.pop("base_settled")
            m = base_metrics[s]
        else:
            m = None
        per.append(dict(seed=s, dm=o["dm"], first_div=o["first_div"],
                        afb=o["afb"], afs=o["afs"], steer=o["steer"]))
        if name == "base":
            per[-1]["base"] = m
    res["arms"][name] = dict(channel=ct, side=s_, amp=float(amp), seeds=per)
    p0 = per[0]
    tb = [base_metrics[s]["turn"]["Tif"] for s in SEEDS]
    ts = [p["steer"]["turn"]["Tif"] for p in per]
    log(f"{name:>14}: dm {min(p['dm'] for p in per):.4f} first_div "
        f"{[p['first_div'] for p in per]} | turn_Tif base "
        + "/".join(f"{v:+.3f}" for v in tb) + " steer "
        + "/".join(f"{v:+.3f}" for v in ts)
        + f" | S_Tr " + "/".join(f"{p['steer']['S_pooled']['Tr']:+.2f}" for p in per)
        + f" | f {p0['steer']['rhythm']['f']:.2f}Hz df_side {p0['steer']['df_side']:+.2f}"
        + f" | {time.time()-t0:.0f}s")

# save steer traces for figure debugging: DNge059 dose ladder seed 22 + base
json.dump(res, open("l37/results_l37.json", "w"), indent=1, default=float)
log(f"saved l37/results_l37.json | {time.time()-t0:.0f}s")


# ---------- stage D: PREREG verdict ----------
def shift(name):
    a = res["arms"][name]
    return [p["steer"]["turn"]["Tif"] - base_metrics[p["seed"]]["turn"]["Tif"] for p in a["seeds"]]


log("\n=== PREREG verdict ===")
ok = True
for s in SEEDS:
    b = base_metrics[s]
    c0 = (.30 <= b["S_pooled"]["Tr"] <= .60) and (b["rhythm"]["ratio"] >= 50) \
        and (.05 <= b["turn"]["Tif"] <= .25)
    ok &= c0
    log(f"C0 seed {s}: S_Tr {b['S_pooled']['Tr']:+.3f} ratio "
        f"{b['rhythm']['ratio']:.0f} turn {b['turn']['Tif']:+.3f} -> "
        f"{'PASS' if c0 else 'FAIL'}")
c1 = True
for name, a in res["arms"].items():
    if name == "base":
        continue
    worst = min(p["steer"]["S_pooled"]["Tr"] for p in a["seeds"])
    dm_min = min(p["dm"] for p in a["seeds"])
    if dm_min <= 1e-4:
        log(f"DM PROBE: {name} dm {dm_min:.2e} <= 1e-4 — drive never entered (L35)")
    if worst < .30:
        c1 = False
        log(f"C1 FAIL arm {name}: worst S_Tr {worst:+.3f}")
log(f"C1 survival (S_Tr>=.30 every steer arm/seed): {'PASS' if c1 else 'FAIL'}")
c2 = []
for ct in CHANNELS:
    sh = shift(f"{ct}_Lx0.8")
    pred = chans[ct]["pred_L"]
    cons = all((v > 0) == (pred > 0) and abs(v) >= .15 for v in sh)
    if cons:
        c2.append(ct)
    log(f"C2 {ct} @L.8: shift {['%+.3f' % v for v in sh]} pred {pred:+.0f} "
        f"-> {'PASS' if cons else 'FAIL'}")
c3 = []
for ct in CHANNELS:
    mono = True
    for si in range(3):
        seq = [abs(shift(f"{ct}_Lx{a}")[si]) for a in AMPS]
        mono &= all(seq[i] <= seq[i + 1] + .01 for i in range(2))
    if mono:
        c3.append(ct)
    log(f"C3 {ct} dose-response monotone 3/3: {'PASS' if mono else 'FAIL'}")
best = max(c2, key=lambda c: abs(np.mean(shift(f"{c}_Lx0.8")))) if c2 else None
c4 = True
for dr in range(2):
    sh = [v for p in res["arms"][f"rand{dr}"]["seeds"]
          for v in [p["steer"]["turn"]["Tif"] - base_metrics[p["seed"]]["turn"]["Tif"]]]
    sgn = all((v > 0) for v in sh) or all((v < 0) for v in sh)
    big = best and max(abs(v) for v in sh) >= abs(np.mean(shift(f"{best}_Lx0.8")))
    if sgn and big:
        c4 = False
    log(f"C4 rand{dr}: shift {['%+.3f' % v for v in sh]} sign-consistent {sgn} "
        f"beats-best {bool(big)} -> {'OK' if not (sgn and big) else 'FAIL'}")
log(f"\nVERDICT: C0 {ok} | C1 {c1} | C2 revival {c2} | C3 dose {c3} | C4 nulls {c4}")
if c2:
    log("steering-by-tonic-bias REVIVES (L33 amended: channel-choice artifact)")
elif not c1:
    log("viable channels BREAK the rhythm they modulate (freq mod != steering-compatible)")
else:
    log("speed-without-steering: cord is a throttle, CX owns direction (consistent w/ L31)")
log(f"done {time.time()-t0:.0f}s")
