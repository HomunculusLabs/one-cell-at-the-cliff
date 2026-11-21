"""L43b: fixed-entx re-run — v1's target_a collapsed entx's drive-on window
(entx came out BIT-EQUAL to d30a12: same release, same drive-off; the C4
re-host arm never existed — L39-v1 arm-wiring class, third instance).

Uses the l43 raw.npz checkpoint for the 11 v1 arms and re-runs ONLY entx
(fixed: target 0.7 through the release, DNg88 -12 x 30 s, hop @2000) on the
same per-seed noise stream (X0 draw, then one nz per step — lone-arm reruns
reproduce shared-noise trajectories exactly, L41's replication instrument).
Anchor gate: entx prefix vs l42 `stack` over [0,4000) must be 0.0 — that IS
the lone-run determinism proof. Merges C4 into l43/results_l43.json.
"""
import json
import math
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN, STOP0 = 400, 11000, 4000
DUR, RAMP = 3000, -12.0
HOP_ONSET, HOP_VW, HOP_AMP = 2000, 40, 0.5
ENT_AMP = 0.3
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- substrate (l42/l43-verbatim) ----------
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
ltyp, lside, lcls = typ[keep], side[keep], cls[keep]
assert n == 21516 and len(gsrc) == 2977920
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
lnt = nt_names[keep]
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wa_vals = gw * signA[loc[gsrc]]
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([loc[gdst], loc[gsrc]])).long(),
    torch.from_numpy(Wa_vals.astype(np.float32)), (n, n)).coalesce().to_sparse_csr()
motor = np.isin(sup[keep], ["vnc_motor", "cb_motor"])
tm = pd.Series(ltyp)
PAIRS = {}
for k in ("Ti", "Tr"):
    f = np.where(motor & tm.isin([f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (tm == f"{k} extensor MN"))[0]
    fL, fR = f[lside[f] == "L"], f[lside[f] == "R"]
    eL, eR = e[lside[e] == "L"], e[lside[e] == "R"]
    assert len(fL) and len(fR) and len(eL) and len(eR)
    PAIRS[k] = dict(fL=fL, fR=fR, eL=eL, eR=eR)
dng100 = np.where(ltyp == "DNg100")[0]
mech = np.where((sup[keep] == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
hopL = np.where((ltyp == "DNge046") & (lside == "L"))[0]
REL = np.where(ltyp == "DNg88")[0]
assert len(dng100) == 2 and len(hopL) == 2 and len(REL) > 0 and len(mech) > 0
log(f"sub ok | mech {len(mech)} | 046L {len(hopL)} | DNg88 {len(REL)}")


def target(k):  # entx FIXED: drive ON through the release
    if k < 2000:
        return 0.7
    if k < 4000:
        return 1.4
    return 0.7


ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph


def rhythm2(x, lo=0.5, hi=10.0):
    x = x - x.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    b = (fr >= lo) & (fr <= hi)
    pb, fb = ps[b], fr[b]
    if pb.max() <= 0:
        return 0.0, 0.0
    i = int(np.argmax(pb))
    return float(pb[i] / max(np.median(pb), 1e-30)), float(fb[i])


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


out = {}
for seed in SEEDS:
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    settle_ph = 0.0
    SIGS = ("fL", "fR", "eL", "eR")
    mm = np.zeros(WIN, np.float32)
    tr = {c: np.zeros(WIN, np.float32) for c in SIGS}
    x88 = np.zeros(WIN, np.float32)

    def step(k):
        global settle_ph, X
        nz = NOISE * torch.randn(n, 1, generator=gen)
        ph_k = PHI[k] if k >= 0 else (settle_ph := settle_ph + 2 * math.pi * 0.7 * DT)
        drive = torch.sparse.mm(Wb, X) * G + I
        drive[mech, 0] = drive[mech, 0] + ENT_AMP * (0.5 + 0.5 * math.sin(ph_k))
        if STOP0 <= k < STOP0 + DUR:
            drive[REL, 0] = drive[REL, 0] + RAMP
        if HOP_ONSET <= k < HOP_ONSET + HOP_VW:
            drive[hopL, 0] += HOP_AMP
        t = torch.relu(drive + BG)
        t = (t + nz).clamp(max=RMAX)
        X += (DT / TAU) * (t - X)

    for k in range(SETTLE):
        step(-1 - k)
    af = float((X > 0.05).float().mean())
    assert 0.01 < af < 0.9, af
    for i in range(WIN):
        step(i)
        mm[i] = X[motor].mean()
        for c in SIGS:
            tr[c][i] = X[PAIRS["Tr"][c]].mean()
        x88[i] = X[REL].mean()
    out[str(seed)] = dict(af=af, mm=mm, tr=tr, x88=x88)
    log(f"seed {seed} done {time.time()-t0:.0f}s")

# ---------- anchor gate: lone-run determinism proof ----------
z42 = np.load("l42/traces.npz")
anchor = max(float(np.abs(out[str(s)]["mm"][:4000] - z42[f"mm_stack_{s}"][:4000]).max())
             for s in SEEDS)
log(f"ANCHOR entx-vs-l42stack[0,4000) max|d| = {anchor}")
assert anchor == 0.0, "lone-run noise stream diverged — C4 invalid"

# ---------- metrics (l43_dose forms verbatim) ----------
end = STOP0 + DUR
metrics = {}
SR = {}
for s in ("11", "22", "33"):
    r = out[s]
    late, f_late = rhythm2(r["mm"][end - 500:end])
    pre, _ = rhythm2(r["mm"][3500:4000])
    kill = next((c for c in range(DUR // 100)
                 if rhythm2(r["mm"][STOP0 + c * 100:STOP0 + (c + 1) * 100])[0] < 5), None)
    depth = float(r["mm"][end - 200:end].std() / max(r["mm"][3500:4000].std(), 1e-9))
    early, f_e = rhythm2(r["mm"][end:end + 500])
    last, f_l = rhythm2(r["mm"][WIN - 500:WIN])
    fL, fR, eL, eR = (r["tr"][c] for c in SIGS)
    S = np.full(WIN, np.nan)
    for t in range(499, WIN, 10):
        S[t] = S_of(fL[t - 499:t + 1] + fR[t - 499:t + 1],
                    eL[t - 499:t + 1] + eR[t - 499:t + 1])
    SR[s] = S
    ts = np.arange(499, WIN, 10)
    lat = None
    for t in ts[ts >= end]:
        if t + 250 >= WIN:
            break
        if S[t] >= 0.25 and np.nanmin(S[t:t + 251:10]) >= 0.25:
            lat = int(t - end)
            break
    metrics[s] = dict(
        pre_ratio=round(pre, 1), late_ratio=round(late, 1), f_late=round(f_late, 3),
        depth=round(depth, 3), kill_latency=kill,
        min_x88=round(float(r["x88"][STOP0:end].min()), 3),
        post_early_ratio=round(early, 1), f_post_early=round(f_e, 3),
        post_last_ratio=round(last, 1), f_post_last=round(f_l, 3),
        resurrect_latency=lat,
        S_med_during=round(float(np.nanmedian(S[ts[(ts >= STOP0) & (ts < end)]])), 3),
        S_med_after=round(float(np.nanmedian(S[ts[(ts >= end) & (ts < end + 3000)]])), 3))
log("ENTX " + json.dumps(metrics)[:1200])

# ---------- merge into results_l43.json ----------
res43 = json.load(open("l43/results_l43.json"))
res43["dose"]["entx"] = metrics
res43["post"]["entx"] = metrics  # same dict carries both windows' fields
res43["af"]["entx"] = {s: out[s]["af"] for s in out}
entx_ok = (sum(metrics[s]["late_ratio"] >= 5 for s in metrics) >= 2
           and all(metrics[s]["S_med_during"] >= 0.25 for s in metrics))
deep = res43["verdict"]["C2_kill_dose"]["cells"].get("d30a12", 0) >= 2
res43["verdict"]["C4_rehost"] = dict(
    entx_ok=bool(entx_ok), d30a12_killed=bool(deep),
    v1_bug="v1 entx was drive-off (bit-equal d30a12) — target_a collapsed the "
           "drive-through case; fixed + lone-arm rerun on the same noise stream "
           "(anchor 0.0). Disclosed as a PREREG addendum.",
    verdict=("entrain re-hosts through the release" if entx_ok and deep else
             ("no park anywhere: C4 premise failed — entrainment history itself "
              "is the protection (see C2)" if not deep and not entx_ok else
              "layered — see table")))
json.dump(res43, open("l43/results_l43.json", "w"), indent=1)

# rewrite traces.npz with the fixed entx
z43 = dict(np.load("l43/traces.npz"))
for s in ("11", "22", "33"):
    z43[f"mm_entx_{s}"] = out[s]["mm"]
    z43[f"fL_entx_{s}"] = out[s]["tr"]["fL"]
    z43[f"SR_entx_{s}"] = SR[s]
np.savez_compressed("l43/traces.npz", **z43)
log(f"done {time.time()-t0:.0f}s -> merged l43/results_l43.json + traces.npz")
