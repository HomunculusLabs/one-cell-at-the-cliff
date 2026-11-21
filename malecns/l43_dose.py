"""L43: stop-dose-resurrection — the two numbers L42 left unmeasured.

(1) KILL DOSE of the DNg88 release on the entrained cord: stop duration
{10,20,30 s} x amp {-4,-8,-12} -> late-stop rhythm ratio; does any cell reach
the L40 intrinsic kill level (ratio < 5), and is `entx` (drive kept ON through
the release) protected = entrain re-hosts through the release?
(2) RESURRECTION latency: for parked cells, steps from stop-off to persistent
rolling S >= .25 under entrain amp .3 ALONE (no hop — l42's C4 was re-lock).

PREREG in l43/PREREG.md, written first. Machinery l42-verbatim; ONE generator
+ ONE shared per-step noise tensor per seed (L36); dose arms + entx anchor
BIT-IDENTICALLY to l42 `stack` over [0,4000), d10a8 over [0,5000), ent to l42
`ent` over [0,4000) (C0). P1-labeled descriptive; CPU-only; no live changes.
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
SETTLE = 400
WIN = 11000
STOP0 = 4000
HOP_ONSET, HOP_VW, HOP_AMP = 2000, 40, 0.5
BLK = 500
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05        # l32 arm-A frozen
ENT_AMP = 0.3                       # l42 ent/stack amp
DURS = (1000, 2000, 3000)           # 10/20/30 s
RAMPS = (4.0, 8.0, 12.0)            # |release amp|
DOSE = {(du, ra): f"d{du // 100}a{int(ra)}" for du in DURS for ra in RAMPS}
ARMS = ["ent", "entx"] + list(DOSE.values())
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l32/l34/l39/l41/l42 verbatim) ----------
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
lsup, ltyp, lside, lcls = sup[keep], typ[keep], side[keep], cls[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)
log(f"sub nodes {n:,} | edges {len(gsrc):,} | {time.time()-t0:.0f}s")

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(str(nt_names[keep][i]), 0.3) for i in range(n)],
                 np.float32)
lsrc, ldst = loc[gsrc], loc[gdst]
Wa_vals = gw * signA[lsrc]
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy(Wa_vals.astype(np.float32)), (n, n)).coalesce().to_sparse_csr()

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
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
assert len(mech) > 0
hopL = np.where((ltyp == "DNge046") & (lside == "L"))[0]
REL = np.where(ltyp == "DNg88")[0]
assert len(hopL) == 2 and len(REL) > 0, (len(hopL), len(REL))
log(f"mech {len(mech)} | 046L {len(hopL)} | DNg88 {len(REL)}")

# per-arm drive table (L39 v1 lesson: no inline conditionals in the loop)
DUR_OF = {a: 0 for a in ARMS}
RAMP_OF = {a: 0.0 for a in ARMS}
for (du, ra), a in DOSE.items():
    DUR_OF[a], RAMP_OF[a] = du, -ra
DUR_OF["entx"], RAMP_OF["entx"] = 3000, -12.0


DRIVE_THROUGH = {"entx"}          # release + drive ON (C4 re-host arm)


def target_a(a, k):
    if k < 2000:
        return 0.7
    if k < 4000:
        return 1.4
    if a == "ent" or a in DRIVE_THROUGH:
        return 0.7
    return 0.0 if k < 4000 + DUR_OF[a] else 0.7


# per-arm phase accumulator, l42 recursion with t_a
PHIS = {}
for a in ARMS:
    ph = 0.0
    for _ in range(SETTLE):
        ph += 2 * math.pi * 0.7 * DT
    arr = np.empty(WIN, np.float64)
    for i in range(WIN):
        ph += 2 * math.pi * target_a(a, i) * DT
        arr[i] = ph
    PHIS[a] = arr


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


def run_seed(seed):
    gen = torch.Generator().manual_seed(seed)
    X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    X = {a: X0.clone() for a in ARMS}
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    settle_ph = 0.0
    SIGS = ("fL", "fR", "eL", "eR")
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    x88 = {a: np.zeros(WIN, np.float32) for a in ARMS}

    def step_all(k):
        nonlocal settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            ph_k = {a: PHIS[a][k] for a in ARMS}
        else:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = {a: settle_ph for a in ARMS}
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if k < 0 or target_a(a, k) > 0:
                drive[mech, 0] = drive[mech, 0] + ENT_AMP * (0.5 + 0.5 * math.sin(ph_k[a]))
            if a != "ent" and STOP0 <= k < STOP0 + DUR_OF[a]:
                drive[REL, 0] = drive[REL, 0] + RAMP_OF[a]
            if a != "ent" and HOP_ONSET <= k < HOP_ONSET + HOP_VW:
                drive[hopL, 0] += HOP_AMP
            t = torch.relu(drive + BG)
            t = (t + nz).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])

    for k in range(SETTLE):
        step_all(-1 - k)
    for a in ARMS:
        af = float((X[a] > 0.05).float().mean())
        assert 0.01 < af < 0.9, (a, af)
    for i in range(WIN):
        step_all(i)
        for a in ARMS:
            mm[a][i] = X[a][motor].mean()
            for c in SIGS:
                tr[a][c][i] = X[a][PAIRS["Tr"][c]].mean()
            x88[a][i] = X[a][REL].mean()
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                mm=mm, tr=tr, x88=x88)


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l43/raw.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"fL_{a}_{s}": res[str(s)]["tr"][a]["fL"] for a in ARMS for s in SEEDS},
    **{f"fR_{a}_{s}": res[str(s)]["tr"][a]["fR"] for a in ARMS for s in SEEDS},
    **{f"eL_{a}_{s}": res[str(s)]["tr"][a]["eL"] for a in ARMS for s in SEEDS},
    **{f"eR_{a}_{s}": res[str(s)]["tr"][a]["eR"] for a in ARMS for s in SEEDS},
    **{f"x88_{a}_{s}": res[str(s)]["x88"][a] for a in ARMS for s in SEEDS})

# ---------------- analysis ----------------
def stop_metrics(a, s):
    du = DUR_OF[a]
    end = STOP0 + (du or 3000)   # ent (no release): reference = deepest window
    r = res[s]
    late, f_late = rhythm2(r["mm"][a][end - 500:end])
    pre, _ = rhythm2(r["mm"][a][3500:4000])
    kill = (next((c for c in range(du // 100)
                  if rhythm2(r["mm"][a][STOP0 + c * 100:STOP0 + (c + 1) * 100])[0] < 5),
                 None) if du else None)
    depth = float(r["mm"][a][end - 200:end].std() / max(r["mm"][a][3500:4000].std(), 1e-9))
    return dict(dur=du // 100, ramp=RAMP_OF[a], pre_ratio=round(pre, 1),
                late_ratio=round(late, 1), f_late=round(f_late, 3),
                depth=round(depth, 3), kill_latency=kill,
                min_x88=round(float(r["x88"][a][STOP0:end].min()), 3))


def post_metrics(a, s):
    end = STOP0 + DUR_OF[a]
    r = res[s]
    early, f_e = rhythm2(r["mm"][a][end:end + 500])
    last, f_l = rhythm2(r["mm"][a][WIN - 500:WIN])
    # rolling S
    fL, fR, eL, eR = (r["tr"][a][c] for c in ("fL", "fR", "eL", "eR"))
    S = np.full(WIN, np.nan)
    for t in range(499, WIN, 10):
        S[t] = S_of(fL[t - 499:t + 1] + fR[t - 499:t + 1],
                    eL[t - 499:t + 1] + eR[t - 499:t + 1])
    ts = np.arange(499, WIN, 10)
    lat = None
    for t in ts[ts >= end]:
        if t + 250 >= WIN:
            break
        if S[t] >= 0.25 and np.nanmin(S[t:t + 251:10]) >= 0.25:
            lat = int(t - end)
            break
    med_after = float(np.nanmedian(S[ts[(ts >= end) & (ts < end + 3000)]]))
    med_during = (float(np.nanmedian(S[ts[(ts >= STOP0) & (ts < end)]]))
                  if end > STOP0 else float("nan"))
    return dict(post_early_ratio=round(early, 1), f_post_early=round(f_e, 3),
                post_last_ratio=round(last, 1), f_post_last=round(f_l, 3),
                resurrect_latency=lat, S_med_after=round(med_after, 3),
                S_med_during=round(med_during, 3)), S


dose_tbl, post_tbl = {}, {}
SR_all = {}
for (du, ra), a in DOSE.items():
    dose_tbl[a] = {str(s): stop_metrics(a, str(s)) for s in SEEDS}
    post_tbl[a] = {}
    for s in SEEDS:
        p, S = post_metrics(a, str(s))
        post_tbl[a][str(s)] = p
        SR_all[f"SR_{a}_{s}"] = S
# ent/entx window rows (same window as deepest dose)
for a in ("ent", "entx"):
    dose_tbl[a] = {str(s): stop_metrics(a, str(s)) for s in SEEDS}
    post_tbl[a] = {}
    for s in SEEDS:
        p, S = post_metrics(a, str(s))
        post_tbl[a][str(s)] = p
        SR_all[f"SR_{a}_{s}"] = S

# ---------------- verdict ----------------
z42 = np.load("l42/traces.npz")


def c0diff(mine, ref, hi):
    return max(float(np.abs(res[str(s)]["mm"][mine][:hi] - z42[f"mm_{ref}_{s}"][:hi]).max())
               for s in SEEDS)


c0 = {"dose_prefix_stack_4000": max(c0diff(a, "stack", 4000) for a in DOSE.values()),
      "entx_prefix_stack_4000": c0diff("entx", "stack", 4000),
      "d10a8_stack_5000": c0diff("d10a8", "stack", 5000),
      "ent_prefix_ent_4000": c0diff("ent", "ent", 4000)}
c0_pass = all(v == 0.0 for v in c0.values())

DOSE_ARMS = list(DOSE.values())
c1 = {a: all(dose_tbl[a][str(s)]["min_x88"] < 0.5 for s in SEEDS)
      for a in DOSE_ARMS}
cells_killed = {a: sum(dose_tbl[a][str(s)]["late_ratio"] < 5 for s in SEEDS)
                for a in DOSE_ARMS}
c2_exist = any(v >= 2 for v in cells_killed.values())
c2_min = next((a for a in DOSE_ARMS if cells_killed[a] >= 2), None)
c3 = {f"d{du // 100}": bool(np.median([dose_tbl[f"d{du // 100}a12"][str(s)]["late_ratio"]
                                       for s in SEEDS])
                            < np.median([dose_tbl[f"d{du // 100}a4"][str(s)]["late_ratio"]
                                         for s in SEEDS]))
      for du in DURS}
entx_ok = (sum(dose_tbl["entx"][str(s)]["late_ratio"] >= 5 for s in SEEDS) >= 2
           and all(post_tbl["entx"][str(s)]["S_med_during"] >= 0.25 for s in SEEDS))
deep_killed = cells_killed.get("d30a12", 0) >= 2
c4_rehost = bool(entx_ok and deep_killed)
c5 = {a: {str(s): post_tbl[a][str(s)]["resurrect_latency"] for s in SEEDS}
      for a in DOSE_ARMS if cells_killed[a] >= 1}

verdict = dict(
    C0_bitident=dict(maxdiff=c0, pass_=c0_pass),
    C1_unpin=c1, C2_kill_dose=dict(cells=cells_killed, exists=bool(c2_exist),
                                   minimal=c2_min),
    C3_dose_order=c3,
    C4_rehost=dict(entx_ok=bool(entx_ok), d30a12_killed=bool(deep_killed),
                   verdict="entrain re-hosts through the release" if c4_rehost else
                   ("both killed: resistance was basin memory/dose, not re-hosting"
                    if not entx_ok and deep_killed else "layered — see table")),
    C5_resurrection=c5,
)
log("VERDICT " + json.dumps(verdict)[:2000])

np.savez_compressed("l43/traces.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
                    **{f"fL_{a}_{s}": res[str(s)]["tr"][a]["fL"] for a in ARMS for s in SEEDS},
                    **SR_all)
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, stop0=STOP0,
                      seeds=SEEDS, ent_amp=ENT_AMP, hop=(HOP_ONSET, HOP_VW, HOP_AMP),
                      durs=list(DURS), ramps=list(RAMPS), nodes=int(n),
                      edges=len(gsrc)),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            dose=dose_tbl, post=post_tbl, verdict=verdict)
json.dump(dump, open("l43/results_l43.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l43/results_l43.json")
