"""L42: entrain-hop-stop-stack — the honest endgame demo. ONE controller with
all three measured primitives {entrain, hop, stop} through a target trajectory
WITH a 10-s stop segment, gated on RECOVERY LATENCY (tick-58 amendment: repair
is post-disturbance, entrain amp is the knob; no volley-envelope gates — L41).

PREREG in l42/PREREG.md, written first (one pre-run amendment disclosed there).
Machinery l39/l41-verbatim; ONE generator + ONE shared per-step noise tensor
per seed (L36) so free/ent/stack are BIT-IDENTICAL to l39 over the anchor
windows (C0). P1-labeled descriptive; CPU-only; no live changes.
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
WIN = 7000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 5000, 0.0), (5000, 7000, 0.7)]
STOP0, STOP1 = 4000, 5000
RESTART = 5000
BLK = 500
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05        # l32 arm-A frozen
HOP_AMP, HOP_VW = 0.5, 40           # l39/l41 base volley (square)
REL_AMP = -8.0                      # L38/L40 verified stop channel
AMPS = {"free": 0.0, "ent": 0.3, "entstop": 0.3, "stack": 0.3, "stack_lo": 0.03}
HOP_ARMS = ("stack", "stack_lo")    # hop @2000 and @5000
STOP_ARMS = ("entstop", "stack", "stack_lo")
LOCK_TOL = 0.10
ENV_SQ = np.ones(HOP_VW, np.float32)
ANCHOR = {11: 0.800, 22: 1.444, 33: 1.422}
ARMS = list(AMPS)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l32/l34/l39/l41 verbatim) ----------
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
lnt = nt_names[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)
log(f"sub nodes {n:,} | edges {len(gsrc):,} | {time.time()-t0:.0f}s")

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
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
hopR = np.where((ltyp == "DNge046") & (lside == "R"))[0]
REL = np.where(ltyp == "DNg88")[0]
assert len(hopL) == 2 and len(hopR) == 2 and len(REL) > 0, (len(hopL), len(REL))
log(f"mech {len(mech)} | 046L {len(hopL)} | DNg88 {len(REL)}")

# phase accumulator: replicates l39 EXACTLY over [0,4000) (settle@0.7 +
# seg0 0.7 + seg1 1.4); FROZEN during the stop; 0.7 after
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
HOP_ONSETS = (2000, 5000)


def dom_freq(x, lo=0.3):
    z = x - x.mean()
    ps = np.abs(np.fft.rfft(z)) ** 2
    fr = np.fft.rfftfreq(len(z), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    ratio = float(pb.max() / max(np.median(pb), 1e-30))
    return float(f_hat), ratio


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
    x046 = {a: np.zeros(WIN, np.float32) for a in ARMS}
    dm = {a: dict(vm1=0.0, fd1=-1, vm_stop=0.0, vm_re=0.0, fd_re=-1) for a in ARMS}

    def step_all(k):
        nonlocal settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            ph_k = PHI[k]
        else:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            amp = AMPS[a]
            if amp > 0 and (k < 0 or target(k) > 0):
                drive[mech, 0] = drive[mech, 0] + amp * (0.5 + 0.5 * math.sin(ph_k))
            if a in STOP_ARMS and STOP0 <= k < STOP1:
                drive[REL, 0] = drive[REL, 0] + REL_AMP
            if a in HOP_ARMS and k >= 0:
                for o in HOP_ONSETS:
                    if o <= k < o + HOP_VW:
                        m = float(ENV_SQ[k - o])
                        drive[hopL, 0] += HOP_AMP * m
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
            x046[a][i] = X[a][hopL].mean()
        # dm probes vs ent (same amp .3; stack_lo exempt — amp differs)
        if i >= 2000:
            for a in ("entstop", "stack"):
                d = float((X[a] - X["ent"]).abs().max())
                if 2000 <= i < 2000 + HOP_VW and a == "stack":
                    if d > 1e-6 and dm[a]["fd1"] < 0:
                        dm[a]["fd1"] = i - 2000
                    dm[a]["vm1"] = max(dm[a]["vm1"], d)
                if STOP0 <= i < STOP1:
                    dm[a]["vm_stop"] = max(dm[a]["vm_stop"], d)
                if RESTART <= i < RESTART + HOP_VW and a == "stack":
                    if d > 1e-6 and dm[a]["fd_re"] < 0:
                        dm[a]["fd_re"] = i - RESTART
                    dm[a]["vm_re"] = max(dm[a]["vm_re"], d)
    # ---- per-seed analysis ----
    blocks = {a: [] for a in ARMS}
    for a in ARMS:
        for b in range(WIN // BLK):
            f_hat, ratio = dom_freq(mm[a][b * BLK:(b + 1) * BLK])
            seg = next(s for s, (a0, b0, _) in enumerate(SEGB)
                       if a0 <= b * BLK < b0)
            blocks[a].append(dict(b=b, f=f_hat, ratio=ratio, seg=seg,
                                  target=SEGB[seg][2],
                                  err=abs(f_hat - SEGB[seg][2])
                                  if SEGB[seg][2] > 0 else None))
    segs = {a: [] for a in ARMS}
    for a in ARMS:
        for s, (a0, b0, tg) in enumerate(SEGB):
            bl = [x for x in blocks[a] if x["seg"] == s]
            if tg > 0:
                err = float(np.mean([x["err"] for x in bl[1:]]))
                ttl = next((x["b"] - bl[0]["b"] for x in bl[1:]
                            if x["err"] <= LOCK_TOL), None)
                segs[a].append(dict(track_err=err, ttl=ttl))
            else:  # stop segment
                ratio, f_at = rhythm2(mm[a][a0:b0])
                pre_r, _ = rhythm2(mm[a][a0 - 500:a0])
                kill = next((c * 100 for c in range((b0 - a0) // 100)
                             if rhythm2(mm[a][a0 + c * 100:a0 + (c + 1) * 100])[0] < 5),
                            None)
                segs[a].append(dict(ratio=ratio, f_at=f_at, pre_ratio=pre_r,
                                    kill_latency=kill,
                                    depth=float(mm[a][b0 - 200:b0].std()
                                               / max(mm[a][a0 - 500:a0].std(), 1e-9)),
                                    min_x88=float(x88[a][a0:b0].min())))
    # rolling S + recovery
    SROLL = {}
    for a in ARMS:
        fL, fR, eL, eR = (tr[a][c] for c in SIGS)
        SROLL[a] = np.full(WIN, np.nan)
        for t in range(499, WIN, 10):
            SROLL[a][t] = S_of(fL[t - 499:t + 1] + fR[t - 499:t + 1],
                               eL[t - 499:t + 1] + eR[t - 499:t + 1])

    def recovery(a, e):
        S = SROLL[a]
        ts = np.arange(499, WIN, 10)
        for t in ts[ts >= e]:
            if t + 250 >= WIN:
                break
            if S[t] >= 0.25 and np.nanmin(S[t:t + 251:10]) >= 0.25:
                return int(t - e)
        return None

    rec = {a: dict(hop1=recovery(a, 2000 + HOP_VW), restart=recovery(a, RESTART))
           for a in ARMS}
    out = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
               dm=dm, segments=segs, blocks=blocks, recovery=rec,
               x046_rise=float(x046["stack"][RESTART:RESTART + HOP_VW].max()
                               - x046["stack"][RESTART - 1]))
    out["_mm"] = {a: mm[a].copy() for a in ARMS}
    out["_fL"] = {a: tr[a]["fL"].copy() for a in ARMS}
    out["_SR"] = {a: SROLL[a].copy() for a in ARMS}
    return out


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# ---------------- verdict ----------------
z39 = np.load("l39/traces.npz")
r39 = json.load(open("l39/results_l39.json"))
c0 = {}
for arm39, mine, hi in (("free", "free", 6000), ("ent", "ent", 4000),
                        ("ent_h046", "stack", 4000)):
    c0[arm39] = max(float(np.abs(res[str(s)]["_mm"][mine][:hi]
                                 - z39[f"mm_{arm39}_{s}"][:hi]).max())
                    for s in SEEDS)
c0["entstop_vs_ent"] = max(float(np.abs(res[str(s)]["_mm"]["entstop"][:4000]
                                        - res[str(s)]["_mm"]["ent"][:4000]).max())
                           for s in SEEDS)
c0_pass = all(v == 0.0 for v in c0.values())

c1 = dict(
    hop1_lands=all(res[str(s)]["dm"]["stack"]["vm1"] > 1e-6
                   and res[str(s)]["dm"]["stack"]["fd1"] == 0 for s in SEEDS),
    stop_lands=all(res[str(s)]["dm"]["stack"]["vm_stop"] > 1e-6 for s in SEEDS),
    x88_unpins=all(res[str(s)]["segments"]["stack"][2]["min_x88"] < 0.5
                   for s in SEEDS),
    restart_lands=all(res[str(s)]["dm"]["stack"]["vm_re"] > 1e-6 for s in SEEDS),
    restart_rise=all(res[str(s)]["x046_rise"] > 0.05 for s in SEEDS),
)
c2a = all(res[str(s)]["segments"]["stack"][1]["track_err"]
          <= max(0.05, r39["segments"]["ent_h046"][str(s)][1]["track_err"] + 0.001)
          for s in SEEDS)
c2b = sum(res[str(s)]["segments"]["stack"][3]["ttl"] is not None
          and res[str(s)]["segments"]["stack"][3]["ttl"] <= 2 for s in SEEDS) >= 2
c3 = dict(
    stack_killed=all(res[str(s)]["segments"]["stack"][2]["ratio"] < 5 for s in SEEDS),
    ent_keeps=all(res[str(s)]["segments"]["ent"][2]["ratio"] >= 20 for s in SEEDS),
    kill_lat_ok=all((res[str(s)]["segments"]["stack"][2]["kill_latency"] or 10**9)
                    <= 1000 for s in SEEDS),
)
rec_stack = {s: res[str(s)]["recovery"]["stack"]["restart"] for s in SEEDS}
c4 = sum(r is not None and r <= 1000 for r in rec_stack.values()) >= 2
rec_lo = {s: res[str(s)]["recovery"]["stack_lo"]["restart"] for s in SEEDS}
c5_pairs = []
for s in SEEDS:
    a, b = rec_stack[s], rec_lo[s]
    c5_pairs.append(a is not None and (b is None or a < b))
c5 = sum(c5_pairs) >= 2

verdict = dict(
    C0_bitident=dict(maxdiff=c0, pass_=c0_pass),
    C1_lands=c1, C2=dict(seg1_held=bool(c2a), restart_lock=bool(c2b)),
    C3_stop=c3, C4_restart_recovery=dict(latency=rec_stack, gate=bool(c4)),
    C5_knob=dict(stack=rec_stack, stack_lo=rec_lo, gate=bool(c5),
                 pairs=c5_pairs),
    recovery_table={a: {str(s): res[str(s)]["recovery"][a] for s in SEEDS}
                    for a in ARMS},
    track={a: {str(s): [round(x["track_err"], 3) for x in res[str(s)]["segments"][a]
                        if "track_err" in x] for s in SEEDS} for a in ARMS},
    stop={a: {str(s): {k: (round(v, 3) if isinstance(v, float) else v)
                       for k, v in res[str(s)]["segments"][a][2].items()}
              for s in SEEDS} for a in ARMS},
    min_x88={a: {str(s): round(res[str(s)]["segments"][a][2]["min_x88"], 3)
                 for s in SEEDS} for a in ARMS},
)
log("VERDICT " + json.dumps(verdict)[:2400])

np.savez_compressed("l42/traces.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["_mm"][a] for a in ARMS
                       for s in SEEDS},
                    **{f"fL_{a}_{s}": res[str(s)]["_fL"][a] for a in ARMS
                       for s in SEEDS},
                    **{f"SR_{a}_{s}": res[str(s)]["_SR"][a] for a in ARMS
                       for s in SEEDS})
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, segb=SEGB,
                      blk=BLK, seeds=SEEDS, amps=AMPS, hop_amp=HOP_AMP,
                      hop_vw=HOP_VW, rel_amp=REL_AMP, lock_tol=LOCK_TOL,
                      hop_onsets=HOP_ONSETS, rel_len=len(REL), nodes=int(n),
                      edges=len(gsrc)),
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            dm={a: {str(s): res[str(s)]["dm"][a] for s in SEEDS}
                for a in ("entstop", "stack")},
            x046_rise={str(s): res[str(s)]["x046_rise"] for s in SEEDS},
            segments={a: {str(s): res[str(s)]["segments"][a] for s in SEEDS}
                      for a in ARMS},
            blocks={a: {str(s): res[str(s)]["blocks"][a] for s in SEEDS}
                    for a in ARMS},
            recovery={a: {str(s): res[str(s)]["recovery"][a] for s in SEEDS}
                      for a in ARMS},
            verdict=verdict)
json.dump(dump, open("l42/results_l42.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l42/results_l42.json")
