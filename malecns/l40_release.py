"""L40: release-composition — stop-and-go as ONE gesture vocabulary?

L38's two-sided action set: negative tonic on ceiling-pinned DNg88 is a STOP
channel (S(Tr) .49 -> .06-.12 at -8); DNge046_L free side is a viable HOP
(dm ~1.0, freq up, S survives). Do they COMPOSE — fired together or
staggered (stop-then-go / go-then-stop) — or does the release rupture what
the hop needs? PREREG: l40/PREREG.md (written first).

L32 arm-A frozen substrate (g .01, beta 2, D=0 — L35 proved that drive
inert); NO mech entrainment (kept pure; the entrain join is a later card).
Paired control + 7 arms, ONE generator + ONE shared per-step noise (L36);
drives AFTER settle (L36); per-arm drive table (L39 v1 bug); dm probes on
the drive cells per sub-window (L35/L38); af op-point assert every phase.
P1-labeled; CPU-only; no live changes; owner movement law respected.
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
G, BETA = 0.01, 2.0
SETTLE = 400
WIN = 10400
P1E, M1 = 2500, 500            # PRE end, PRE measure start
ONA, ONB, ONE = 2500, 4000, 5500   # ON sub-windows 2a/2b
M2A, M2B, M2E = 2750, 4250, 5500   # measure windows (burn-ins)
POST, MPOST = 10400, 6000
SEEDS = [11, 22, 33]
HOP_AMP, REL_AMP = 0.2, -8.0   # L38 verified landing amps
CTL_F = {11: 0.80, 22: 2.04, 33: 1.91}   # L38 spot Ti-flexor controls
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- substrate (l38/l32 verbatim) ----------
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
log(f"substrate OK: {n:,} nodes / {len(lsrc):,} edges (L32-L39 identical)")

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

motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
PAIRS = {}
for k in ("Ti", "Tr"):
    f = np.where(motor & np.isin(ltyp, [f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (ltyp == f"{k} extensor MN"))[0]
    fL, fR = f[lside[f] == "L"], f[lside[f] == "R"]
    eL, eR = e[lside[e] == "L"], e[lside[e] == "R"]
    assert len(fL) and len(fR) and len(eL) and len(eR), (k, len(fL), len(fR))
    PAIRS[k] = dict(fL=fL, fR=fR, eL=eL, eR=eR)


def cells_of(tname, sd=None):
    m = ltyp == tname
    if sd is not None:
        m &= lside == sd
    return np.where(m)[0]


HOP = cells_of("DNge046", "L")     # the L38/L39 viable free side
REL = cells_of("DNg88")            # the L38 stop channel (whole type)
assert len(HOP) == 2 and len(REL) > 0, (len(HOP), len(REL))
log(f"HOP DNge046_L {len(HOP)} cells | REL DNg88 {len(REL)} cells")

IN2A = lambda k: ONA <= k < ONB
IN2B = lambda k: ONB <= k < ONE
INON = lambda k: ONA <= k < ONE
# per-arm drive table: arm -> [(cells, amp, active_fn)]  (L39 v1 lesson)
DRIVES = {
    "free":    [],
    "hop":     [(HOP, HOP_AMP, INON)],
    "rel":     [(REL, REL_AMP, INON)],
    "joint":   [(HOP, HOP_AMP, INON), (REL, REL_AMP, INON)],
    "s_rh":    [(REL, REL_AMP, IN2A), (HOP, HOP_AMP, IN2B)],   # stop-then-go
    "s_hr":    [(HOP, HOP_AMP, IN2A), (REL, REL_AMP, IN2B)],   # go-then-stop
    "hop_2b":  [(HOP, HOP_AMP, IN2B)],
}
ARMS = list(DRIVES)
SIG = ["fL", "fR", "eL", "eR", "ti_f", "mm", "x046", "x88"]
SUBW = {"2a": (ONA, ONB), "2b": (ONB, ONE), "on": (ONA, ONE), "post": (ONE, WIN)}


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
    X = {"ctl": (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)}
    for a in ARMS:
        X[a] = X["ctl"].clone()
    I = torch.zeros(n, 1)

    def drive_vec(arm, k):
        I.zero_()
        on_tags = []
        for cells, amp, act in DRIVES[arm]:
            if act(k):
                I[cells, 0] = I[cells, 0] + amp
                on_tags.append((len(cells), amp))
        return on_tags

    tr = {t: {s: np.zeros(WIN, np.float32) for s in SIG} for t in X}
    dm = {a: {w: dict(hop=0.0, rel=0.0) for w in SUBW} for a in ARMS}
    dmfree = 0.0
    afends = {}

    def record(t, k, cur):
        d = tr[t]
        d["fL"][k] = cur[PAIRS["Tr"]["fL"]].mean()
        d["fR"][k] = cur[PAIRS["Tr"]["fR"]].mean()
        d["eL"][k] = cur[PAIRS["Tr"]["eL"]].mean()
        d["eR"][k] = cur[PAIRS["Tr"]["eR"]].mean()
        d["ti_f"][k] = cur[PAIRS["Ti"]["fL"]].mean() + cur[PAIRS["Ti"]["fR"]].mean()
        d["mm"][k] = cur[motor].mean()
        d["x046"][k] = cur[HOP].mean()
        d["x88"][k] = cur[REL].mean()

    def af(cur):
        return float((cur > 0.05).float().mean())

    for _ in range(SETTLE):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        for t in X:
            d = torch.sparse.mm(Wb, X[t]) * G
            tn = (torch.relu(d + BG) + nz).clamp(max=RMAX)
            X[t] = X[t] + (DT / TAU) * (tn - X[t])
    for t in X:
        v = af(X[t])
        assert 0.01 < v < 0.9, ("settle", t, v)

    for k in range(WIN):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        for t in X:
            d = torch.sparse.mm(Wb, X[t]) * G
            if t != "ctl":
                for cells, amp, act in DRIVES[t]:
                    if act(k):
                        d[cells, 0] = d[cells, 0] + amp
            tn = (torch.relu(d + BG) + nz).clamp(max=RMAX)
            X[t] = X[t] + (DT / TAU) * (tn - X[t])
            record(t, k, X[t])
        if k >= ONA:
            diff = {a: float((X[a] - X["ctl"]).abs().max()) for a in ARMS}
            dmfree = max(dmfree, diff["free"])
            for a in ARMS:
                for w, (w0, w1) in SUBW.items():
                    if w0 <= k < w1:
                        dh = float((X[a][HOP] - X["ctl"][HOP]).abs().max())
                        dr = float((X[a][REL] - X["ctl"][REL]).abs().max())
                        dm[a][w]["hop"] = max(dm[a][w]["hop"], dh)
                        dm[a][w]["rel"] = max(dm[a][w]["rel"], dr)
        if k in (P1E, ONE, WIN - 1):
            for t in X:
                v = af(X[t])
                afends[f"{t}@{k}"] = v
                assert 0.01 < v < 0.9, ("phase", t, k, v)

    MEAS = {"pre": (M1, P1E), "2a": (M2A, ONB), "2b": (M2B, M2E),
            "on": (M2A, M2E), "post": (MPOST, POST),
            "l38win": (1500, 6000)}   # epoch-matched anchor (L38's window)
    out = {"af": afends, "dmfree": dmfree, "dm": dm, "win": {}}
    for t in X:
        out["win"][t] = {}
        for wname, (a0, a1) in MEAS.items():
            fL = tr[t]["fL"][a0:a1]
            fR = tr[t]["fR"][a0:a1]
            eL = tr[t]["eL"][a0:a1]
            eR = tr[t]["eR"][a0:a1]
            r_ti, f_ti = rhythm2(tr[t]["ti_f"][a0:a1])
            r_mm, f_mm = rhythm2(tr[t]["mm"][a0:a1])
            out["win"][t][wname] = dict(
                S=S_of(fL + fR, eL + eR), SL=S_of(fL, eL), SR=S_of(fR, eR),
                r_ti=r_ti, f_ti=f_ti, r_mm=r_mm, f_mm=f_mm,
                x046=float(tr[t]["x046"][a0:a1].mean()),
                x88=float(tr[t]["x88"][a0:a1].mean()))
    out["_tr"] = {t: {s: tr[t][s].copy() for s in SIG} for t in ("ctl", "rel", "s_rh")}
    return out


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")


def g(t, w, f, s):
    return res[str(s)]["win"][t][w][f]


def S0(t, w, s):   # nan -> 0.0 for gates (nan = no variance = dead rhythm)
    v = g(t, w, "S", s)
    return 0.0 if np.isnan(v) else v


# C0 substrate — anchor on the EPOCH-MATCHED l38 window (my PRE window sits
# at a different point of the free run's attractor migration; window lesson)
c0_f = {s: abs(g("ctl", "l38win", "f_ti", s) - CTL_F[s]) for s in SEEDS}
c0_S = {s: g("ctl", "l38win", "S", s) for s in SEEDS}
c0_free = all(res[str(s)]["dmfree"] == 0.0 for s in SEEDS)
c0 = dict(f_err=c0_f, S=c0_S, free_bitident=bool(c0_free),
          gate=bool(all(v <= 0.05 for v in c0_f.values())
                    and all(v >= 0.40 for v in c0_S.values()) and c0_free))

# C1 drives land (dm on the drive cells, in the sub-windows where each fires).
# Negative control: OFF windows that PRECEDE the arm's first drive must have
# dm EXACTLY 0 (no leakage); off windows AFTER the first drive are CARRYOVER
# (the earlier drive's lasting divergence — reported, never gated: that is
# the composition signal, not leakage).
c1 = {}
for a in ARMS:
    first_fire = min((k for k in range(ONA, ONE)
                      for cells, amp, act in DRIVES[a] if act(k)), default=ONE)
    checks, off_clean, carry = [], [], []
    for cells, amp, act in DRIVES[a]:
        tag = "hop" if cells is HOP else "rel"
        for w in ("2a", "2b"):
            w0, w1 = SUBW[w]
            mid = (w0 + w1) // 2
            dmv = [res[str(s)]["dm"][a][w][tag] for s in SEEDS]
            if act(mid):
                ok = all(v > 0.01 for v in dmv)
                checks.append(dict(tag=tag, w=w, ok=bool(ok), dm=dmv))
            elif w1 <= first_fire:
                off_clean.append(dict(tag=tag, w=w,
                                      dm_zero=all(v == 0.0 for v in dmv),
                                      dm=dmv))
            else:
                carry.append(dict(tag=tag, w=w, dm=dmv))
    c1[a] = dict(checks=checks, off_clean=off_clean, carryover=carry,
                 gate=all(c["ok"] for c in checks)
                      and all(c["dm_zero"] for c in off_clean))

# C2 release stops (L38 anchor, in-phase; gate on the continuous ON window
# as PREREG text; 2a/2b kept as the kill-kinetics decomposition)
c2_S = {str(s): dict(on=round(S0("rel", "on", s), 3),
                     two_a=round(S0("rel", "2a", s), 3),
                     two_b=round(S0("rel", "2b", s), 3)) for s in SEEDS}
c2_ctl = {str(s): round(g("ctl", "on", "S", s), 3) for s in SEEDS}
c2 = dict(S_rel=c2_S, S_ctl_on=c2_ctl,
          gate=bool(sum(c2_S[str(s)]["on"] < 0.15 for s in SEEDS) >= 2
                    and all(g("ctl", "on", "S", s) >= 0.40 for s in SEEDS)))

# C3 stop-then-go
c3_shift = {str(s): abs(g("s_rh", "2b", "f_ti", s) - g("ctl", "2b", "f_ti", s))
            for s in SEEDS}
c3_postS = {str(s): round(S0("s_rh", "post", s), 3) for s in SEEDS}
c3 = dict(f_shift_2b=c3_shift, post_S=c3_postS,
          hop_lands=bool(sum(c3_shift[str(s)] >= 0.3 for s in SEEDS) >= 2),
          survives=bool(sum(c3_postS[str(s)] >= 0.25 for s in SEEDS) >= 2))
c3["gate"] = bool(c3["hop_lands"] and c3["survives"])

# C4 simultaneity
c4 = dict(S_joint_on={str(s): [round(S0("joint", w, s), 3) for w in ("2a", "2b")]
                      for s in SEEDS},
          S_joint_post={str(s): round(S0("joint", "post", s), 3) for s in SEEDS},
          release_dominates=bool(sum(all(S0("joint", w, s) < 0.15
                                         for w in ("2a", "2b")) for s in SEEDS) >= 2))
c4["post_S_gate"] = bool(sum(c4["S_joint_post"][str(s)] >= 0.25 for s in SEEDS) >= 2)

# C5 no lasting damage
c5 = {a: {str(s): dict(r_ti=round(g(a, "post", "r_ti", s), 1),
                       f_ti=round(g(a, "post", "f_ti", s), 3),
                       dpost=round(abs(g(a, "post", "f_ti", s)
                                       - g("ctl", "post", "f_ti", s)), 3))
          for s in SEEDS} for a in ARMS}
c5_gate = {a: all(v["r_ti"] >= 10 for v in c5[a].values()) for a in ARMS}

verdict = dict(C0=c0, C1=c1, C2=c2, C3=c3, C4=c4, C5=c5, C5_gate=c5_gate)
log("VERDICT " + json.dumps(verdict)[:1600])

np.savez_compressed(
    "l40/traces.npz",
    **{f"{t}_{s}_{sig}": res[str(s)]["_tr"][t][sig]
       for s in SEEDS for t in ("ctl", "rel", "s_rh") for sig in SIG})
dump = dict(
    meta=dict(g=G, beta=BETA, hop_amp=HOP_AMP, rel_amp=REL_AMP, win=WIN,
              phases=dict(pre=(0, P1E), on=(ONA, ONE), on2a=(ONA, ONB),
                          on2b=(ONB, ONE), post=(ONE, POST)),
              meas=dict(pre=(M1, P1E), a=(M2A, ONB), b=(M2B, M2E),
                        on=(M2A, M2E), post=(MPOST, POST)),
              seeds=SEEDS, hop=HOP.tolist(), rel=REL.tolist(),
              nodes=int(n), edges=int(len(lsrc))),
    win={t: {str(s): res[str(s)]["win"][t] for s in SEEDS} for t in
         ["ctl"] + ARMS},
    dm={a: {str(s): res[str(s)]["dm"][a] for s in SEEDS} for a in ARMS},
    dmfree={str(s): res[str(s)]["dmfree"] for s in SEEDS},
    af={str(s): res[str(s)]["af"] for s in SEEDS},
    verdict=verdict, runtime_s=round(time.time() - t0, 1))
json.dump(dump, open("l40/results_l40.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l40/results_l40.json")
