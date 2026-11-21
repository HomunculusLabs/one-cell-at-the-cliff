"""L41: structure-preserving transitions — can the three registered guards
(ramped envelope / phase-timed onset / per-side split) hold antagonist
antiphase (seg S(Tr) >= .25, 3/3 seeds, every segment) through L39's
transitions while keeping the hop's tracking win?

PREREG in l41/PREREG.md, written first. L39 controller machinery verbatim;
paired arms share ONE generator + ONE per-step noise tensor so free/ent/base
are BIT-IDENTICAL to l39 (anchor C0). P1-labeled descriptive; CPU-only; no
live changes; owner movement law respected.
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
WIN = 6000
SEG = 2000                      # 20 s per target segment
BLK = 500                       # 5 s tracking blocks
MEAS0_SEG = 500                 # skip first 5 s of each segment for S
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05    # l32 arm-A frozen
ENT_AMP = 0.3                   # l34: locks + re-hosts antiphase
HOP_AMP, HOP_VW = 0.5, 40       # l39 base volley: amp .5, 400 ms
TARGETS = [0.7, 1.4, 0.7]
LOCK_TOL = 0.10
ANCHOR = {11: 0.800, 22: 1.444, 33: 1.422}
ARMS = ["free", "ent", "base", "ramp_mm", "ramp_pm", "phase", "side", "combo"]
ENV_SQ = np.ones(HOP_VW, np.float32)                    # 40 steps
_rise = np.arange(1, 101) / 100.0
ENV_TRI = np.concatenate([_rise, _rise[::-1]]).astype(np.float32)  # 200 st
assert abs(float(ENV_TRI.sum()) - 101.0) < 1e-9
P_MM = 20.0 / 101.0                                     # mass-matched peak
# per-arm volley TABLE (L39 v1 lesson: no inline conditionals)
#   L/R: amp onto the 2 DNge046 L / R cells; env: envelope; onset: b=boundary,
#   p=phase-timed (rule in PREREG)
VC = {
    "base":    dict(L=HOP_AMP, R=0.0,    env=ENV_SQ,  onset="b"),
    "ramp_mm": dict(L=P_MM,    R=0.0,    env=ENV_TRI, onset="b"),
    "ramp_pm": dict(L=HOP_AMP, R=0.0,    env=ENV_TRI, onset="b"),
    "phase":   dict(L=HOP_AMP, R=0.0,    env=ENV_SQ,  onset="p"),
    "side":    dict(L=0.25,    R=0.25,   env=ENV_SQ,  onset="b"),
    "combo":   dict(L=0.10,    R=0.10,   env=ENV_TRI, onset="p"),
}
HOP_ARMS = list(VC)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: subnetwork (l32/l34/l39 verbatim) ----------
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
assert len(hopL) == 2 and len(hopR) == 2, (len(hopL), len(hopR))
log(f"mech {len(mech)} | 046L {len(hopL)} | 046R {len(hopR)}")

# drive phase array: replicates l39's ph accumulation EXACTLY (settle prefix
# runs at TARGETS[-1]=0.7, then per-step TARGETS[min(i//SEG,2)])
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * TARGETS[-1] * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * TARGETS[min(i // SEG, 2)] * DT
    PHI[i] = ph


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


def flexor_peak_phase(fL_hist):
    """circular mean of PHI at local maxima of fL over seg0 steps [1000,2000)."""
    seg0 = fL_hist[1000:2000]
    ph0 = PHI[1000:2000]
    pk = [i for i in range(1, len(seg0) - 1)
          if seg0[i] >= seg0[i - 1] and seg0[i] > seg0[i + 1]]
    assert len(pk) >= 3, f"too few flexor peaks: {len(pk)}"
    ang = ph0[pk]
    return math.atan2(float(np.sin(ang).mean()), float(np.cos(ang).mean())), len(pk)


def phase_onset(t, phi_fL):
    """first step k>t where (phi-phi_fL) mod 2pi wraps (phase passes the
    flexor-peak phase). Bounded t..t+300, fallback t."""
    for k in range(t + 1, min(t + 300, WIN - 1)):
        a0 = (PHI[k - 1] - phi_fL) % (2 * math.pi)
        a1 = (PHI[k] - phi_fL) % (2 * math.pi)
        if a1 < a0:
            return k
    return t


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
    # per-arm volley table resolved at runtime: onset steps per transition
    onset = {a: {0: SEG, 1: 2 * SEG} for a in HOP_ARMS if VC[a]["onset"] == "b"}
    phase_arms = [a for a in HOP_ARMS if VC[a]["onset"] == "p"]
    phi_fL, n_pk = None, 0
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in ("fL", "fR", "eL", "eR")}
          for a in ARMS}
    dm = {a: dict(first_div=-1, volley_max=0.0, dm046R=0.0, onsets=[None, None])
          for a in HOP_ARMS}

    # l39's ph is ONE accumulator through settle+WIN; settle runs at
    # TARGETS[-1]=0.7 Hz stepping the phase each step (bit-identity critical)
    settle_ph = 0.0

    def step_all(k):
        nonlocal settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            mech_add = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k]))
        else:
            settle_ph += 2 * math.pi * TARGETS[-1] * DT
            mech_add = ENT_AMP * (0.5 + 0.5 * math.sin(settle_ph))
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if a != "free":
                drive[mech, 0] = drive[mech, 0] + mech_add
            if a in VC:
                cfg = VC[a]
                ti = 0 if k < 2 * SEG else 1
                o = onset.get(a, {}).get(ti) if k >= SEG else None
                if o is not None and o <= k < o + len(cfg["env"]):
                    m = float(cfg["env"][k - o])
                    if cfg["L"] > 0:
                        drive[hopL, 0] += cfg["L"] * m
                    if cfg["R"] > 0:
                        drive[hopR, 0] += cfg["R"] * m
            t = torch.relu(drive + BG)
            t = (t + nz).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])

    # settle prefix phase continuity assert: PHI[0] = settle end + first seg0
    # increment (both accumulators started at 0 and stepped identically)
    for k in range(SETTLE):
        step_all(-1 - k)                          # settle: mech yes, volley no
    for a in ARMS:
        af = float((X[a] > 0.05).float().mean())
        assert 0.01 < af < 0.9, (a, af)
    for i in range(WIN):
        if i == SEG:                              # resolve phase onsets now
            phi_fL, n_pk = flexor_peak_phase(tr["ent"]["fL"])
            for a in phase_arms:
                onset[a] = {0: phase_onset(SEG, phi_fL),
                            1: phase_onset(2 * SEG, phi_fL)}
            log(f"  seed {seed}: phi_fL {phi_fL:.3f} rad from {n_pk} peaks; "
                f"phase onsets "
                f"{ {a: onset[a] for a in phase_arms} }")
        step_all(i)
        for a in ARMS:
            mm[a][i] = X[a][motor].mean()
            for c in ("fL", "fR", "eL", "eR"):
                tr[a][c][i] = X[a][PAIRS["Tr"][c]].mean()
        for a in HOP_ARMS:
            d = float((X[a] - X["ent"]).abs().max())
            os_ = onset.get(a, {})
            for ti, t_seg in ((0, SEG), (1, 2 * SEG)):
                o = os_.get(ti)
                if o is not None:
                    dm[a]["onsets"][ti] = o
                    if o <= i < o + len(VC[a]["env"]):
                        if d > 1e-6 and dm[a]["first_div"] < 0:
                            dm[a]["first_div"] = i - o
                        dm[a]["volley_max"] = max(dm[a]["volley_max"], d)
                        dR = float((X[a][hopR] - X["ent"][hopR]).abs().max())
                        dm[a]["dm046R"] = max(dm[a]["dm046R"], dR)
    out = {"af": {a: float((X[a] > 0.05).float().mean()) for a in ARMS},
           "dm": dm, "phi_fL": phi_fL, "n_pk": n_pk,
           "blocks": {}, "segments": {}}
    nblk = WIN // BLK
    for a in ARMS:
        out["blocks"][a] = []
        for b in range(nblk):
            f_hat, ratio = dom_freq(mm[a][b * BLK:(b + 1) * BLK])
            seg = min(b * BLK // SEG, 2)
            out["blocks"][a].append(dict(b=b, f=f_hat, ratio=ratio,
                                         target=TARGETS[seg],
                                         err=abs(f_hat - TARGETS[seg])))
        segs = []
        for s in range(3):
            sl = slice(s * SEG + MEAS0_SEG, (s + 1) * SEG)
            fL, fR, eL, eR = (tr[a][c][sl] for c in ("fL", "fR", "eL", "eR"))
            S = -np.corrcoef(fL + fR, eL + eR)[0, 1]
            SL = -np.corrcoef(fL, eL)[0, 1]
            SR = -np.corrcoef(fR, eR)[0, 1]
            blocks = out["blocks"][a][s * 4:(s + 1) * 4]
            err = float(np.mean([x["err"] for x in blocks[1:]]))
            ttl = next((x["b"] - s * 4 for x in blocks[1:]
                        if x["err"] <= LOCK_TOL), None)
            _, ratio_seg = dom_freq(mm[a][sl])
            segs.append(dict(S=float(S), SL=float(SL), SR=float(SR),
                             track_err=err, ttl=ttl, ratio=ratio_seg))
        # transition-window S (first 5 s at each transition, segs 1-2)
        for s, t_seg in ((1, SEG), (2, 2 * SEG)):
            sl = slice(t_seg, t_seg + 500)
            fL, fR, eL, eR = (tr[a][c][sl] for c in ("fL", "fR", "eL", "eR"))
            segs[s]["S_trans"] = float(-np.corrcoef(fL + fR, eL + eR)[0, 1])
        out["segments"][a] = segs
    out["_mm"] = {a: mm[a].copy() for a in ARMS}
    out["_fL"] = {a: tr[a]["fL"].copy() for a in ARMS}
    return out


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# ---------------- verdict ----------------
CANDS = ["ramp_mm", "ramp_pm", "phase", "side", "combo"]

# C0a: free anchors on l39's window
free_f = {s: dom_freq(res[str(s)]["_mm"]["free"][1500:], lo=0.5)[0] for s in SEEDS}
c0a = all(abs(free_f[s] - ANCHOR[s]) <= 0.03 for s in SEEDS)
# C0b: base BIT-IDENTICAL to l39 ent_h046
l39 = json.load(open("l39/results_l39.json"))
c0b_dS = max(abs(res[str(s)]["segments"]["base"][g]["S"]
                 - l39["segments"]["ent_h046"][str(s)][g]["S"])
             for s in SEEDS for g in range(3))
c0b_dT = max(abs(res[str(s)]["segments"]["base"][g]["track_err"]
                 - l39["segments"]["ent_h046"][str(s)][g]["track_err"])
             for s in SEEDS for g in range(3))
c0b_dm = max(abs(res[str(s)]["dm"]["base"]["volley_max"]
                 - l39["dm"]["ent_h046"][str(s)]["volley_max"]) for s in SEEDS)
c0b_fd = all(res[str(s)]["dm"]["base"]["first_div"]
             == l39["dm"]["ent_h046"][str(s)]["first_div"] for s in SEEDS)
c0 = bool(c0a and c0b_dS < 1e-6 and c0b_dT < 1e-6 and c0b_dm < 1e-6 and c0b_fd)

c1 = {a: all(res[str(s)]["dm"][a]["volley_max"] > 1e-6
             and 0 <= res[str(s)]["dm"][a]["first_div"] < len(VC[a]["env"])
             for s in SEEDS) for a in CANDS}
p1_pin = {a: all(res[str(s)]["dm"][a]["dm046R"] == 0.0 for s in SEEDS)
          for a in ("side", "combo")}
g1 = {a: all(res[str(s)]["segments"][a][g]["S"] >= 0.25
             for s in SEEDS for g in range(3)) for a in CANDS}


def segv(a, s, g, f):
    return res[str(s)]["segments"][a][g][f]


g2 = {}
for a in CANDS:
    ok = True
    for s in SEEDS:
        e1 = segv(a, s, 1, "track_err")
        b1 = segv("base", s, 1, "track_err")
        mA = (e1 + segv(a, s, 2, "track_err")) / 2
        mB = (b1 + segv("base", s, 2, "track_err")) / 2
        ok &= (e1 <= max(0.05, b1)) and (mA <= mB + 0.03)
    g2[a] = bool(ok)
verdict_arm = {a: bool(c1[a] and g1[a] and g2[a]) for a in CANDS}
mins = {a: round(min(segv(a, s, g, "S") for s in SEEDS for g in range(3)), 3)
        for a in ARMS}

verdict = dict(
    C0=dict(anchor_free=bool(c0a), base_bitident=dict(dS=c0b_dS, dT=c0b_dT,
                                                     dm=c0b_dm, fd=bool(c0b_fd)),
            pass_=c0, free_f=free_f),
    C1_volley_lands=c1, P1_046R_pinned=p1_pin, G1_allsegS_ge_25=g1,
    G2_tracking_held=g2, VERDICT=verdict_arm, min_seg_S=mins,
    S={a: {str(s): [round(segv(a, s, g, "S"), 3) for g in range(3)]
           for s in SEEDS} for a in ARMS},
    S_trans={a: {str(s): [round(segv(a, s, g, "S_trans"), 3) for g in (1, 2)]
                 for s in SEEDS} for a in ARMS},
    SL_SR={a: {str(s): [(round(segv(a, s, g, "SL"), 2), round(segv(a, s, g, "SR"), 2))
                        for g in range(3)] for s in SEEDS} for a in ARMS},
    track={a: {str(s): [round(segv(a, s, g, "track_err"), 3) for g in range(3)]
               for s in SEEDS} for a in ARMS},
    ttl={a: {str(s): [segv(a, s, g, "ttl") for g in range(3)] for s in SEEDS}
           for a in ARMS},
    dm={a: {str(s): res[str(s)]["dm"][a] for s in SEEDS} for a in HOP_ARMS},
    phi_fL={str(s): res[str(s)]["phi_fL"] for s in SEEDS},
)
log("VERDICT " + json.dumps(verdict)[:2000])

np.savez_compressed("l41/traces.npz",
                    **{f"mm_{a}_{s}": res[str(s)]["_mm"][a] for a in ARMS
                       for s in SEEDS},
                    **{f"fL_{a}_{s}": res[str(s)]["_fL"][a] for a in ARMS
                       for s in SEEDS})
dump = dict(meta=dict(tau=TAU, dt=DT, g=G, beta=BETA, d=D, win=WIN, seg=SEG,
                      blk=BLK, seeds=SEEDS, ent_amp=ENT_AMP, targets=TARGETS,
                      arms=ARMS, env_sq_len=len(ENV_SQ),
                      env_tri_len=len(ENV_TRI), p_mm=P_MM,
                      vc={a: dict(L=VC[a]["L"], R=VC[a]["R"],
                                  env="sq" if VC[a]["env"] is ENV_SQ else "tri",
                                  onset=VC[a]["onset"]) for a in VC},
                      hopL=hopL.tolist(), hopR=hopR.tolist(),
                      nodes=int(n), edges=len(gsrc)),
            segments={a: {str(s): res[str(s)]["segments"][a] for s in SEEDS}
                      for a in ARMS},
            blocks={a: {str(s): res[str(s)]["blocks"][a] for s in SEEDS}
                    for a in ARMS},
            af={a: {str(s): res[str(s)]["af"][a] for s in SEEDS} for a in ARMS},
            dm={a: {str(s): res[str(s)]["dm"][a] for s in SEEDS} for a in HOP_ARMS},
            verdict=verdict)
json.dump(dump, open("l41/results_l41.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l41/results_l41.json")
