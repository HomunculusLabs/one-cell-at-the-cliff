"""L45b: attractor census + channel transition edges on the frozen cord.

Census: 16 base seeds, state = (motor-freq band) x (S-sign L) x (S-sign R)
per 20-s segment; transitions: 6 tonic channels from step 5000, FROM=SEG-B,
TO=SEG-C, paired against the base arm's own spontaneous evolution.
PREREG l45/PREREG-L45b.md written first. Substrate l45_prune.py verbatim.
CPU-only; no live changes.
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
WIN = 11000
DRIVE0 = 5000                      # drive onset (t 50 s)
SEG_A, SEG_B, SEG_C = (500, 2500), (2500, 5000), (7500, 11000)
CENSUS = [11, 22, 33] + list(range(101, 114))          # 16 base seeds
TSEEDS = [11, 22, 33] + list(range(101, 106))           # 8 transition seeds
G, BETA, D = 0.01, 2.0, 0.05
CHANNELS = [                       # (label, type, amp) — PREREG order
    ("d_DNg110", "DNg110", 0.25),
    ("d_DNge046", "DNge046", 0.25),
    ("d_DNg95", "DNg95", 0.25),
    ("d_DNg88rel", "DNg88", -8.0),
    ("d_E1", "IN17A001", 0.25),
    ("d_X464", "INXXX464", 0.25),
]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l45_prune.py verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
neuro = lab["somaNeuromere"].astype(str).fillna("").to_numpy()

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
lsup, ltyp, lside = sup[keep], typ[keep], side[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)

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
SIDE_POOLS = {}
for k in ("Ti", "Tr"):
    f = np.where(motor & tm.isin([f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (tm == f"{k} extensor MN"))[0]
    SIDE_POOLS[f"fL{k}"] = f[lside[f] == "L"]
    SIDE_POOLS[f"fR{k}"] = f[lside[f] == "R"]
    SIDE_POOLS[f"eL{k}"] = e[lside[e] == "L"]
    SIDE_POOLS[f"eR{k}"] = e[lside[e] == "R"]
for kk, v in SIDE_POOLS.items():
    assert len(v), kk
FL = np.concatenate([SIDE_POOLS["fLTi"], SIDE_POOLS["fLTr"]])
FR = np.concatenate([SIDE_POOLS["fRTi"], SIDE_POOLS["fRTr"]])
EL = np.concatenate([SIDE_POOLS["eLTi"], SIDE_POOLS["eLTr"]])
ER = np.concatenate([SIDE_POOLS["eRTi"], SIDE_POOLS["eRTr"]])
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2

CH_CELLS = {}
for lab_, tname, amp in CHANNELS:
    cells = np.where(ltyp == tname)[0]
    assert len(cells) > 0, tname
    sd = sorted(set(lside[cells].tolist()))
    CH_CELLS[lab_] = cells
    log(f"channel {lab_}: {tname} n={len(cells)} sides={sd} amp={amp}")

neg = Wc.values() < 0
vals = Wc.values().clone()
vals[neg] *= BETA
Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
I0 = torch.zeros(n, 1)
I0[dng100] = D
I_CH = {lab_: None for lab_, _, _ in CHANNELS}
for lab_, tname, amp in CHANNELS:
    v = torch.zeros(n, 1)
    v[CH_CELLS[lab_]] = amp
    I_CH[lab_] = v


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


def ssign(s):
    return "+" if s > 0.15 else ("-" if s < -0.15 else "0")


def fband(r, f):
    if r < 5:
        return "FLAT"
    if f < 1.0:
        return "slow"
    if f < 1.8:
        return "mid"
    if f < 2.6:
        return "fast2"
    return "fast3"


def run_seed(seed, arms):
    """One shared-noise rollout; channel drive from DRIVE0 on channel arms."""
    gen = torch.Generator().manual_seed(seed)
    X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    X = {a: X0.clone() for a in arms}
    sigs = ("fL", "fR", "eL", "eR")
    mm = {a: np.zeros(WIN, np.float32) for a in arms}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in sigs} for a in arms}
    chx = {a: np.zeros(WIN // 100, np.float32) for a in arms if a != "base"}
    ch_last = {a: np.zeros(WIN // 100, np.float32) for a in arms if a != "base"}
    af_settle = {}

    def step_all(k):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        for a in arms:
            drive = torch.sparse.mm(Wb, X[a]) * G + I0
            if a != "base" and k >= DRIVE0:
                drive = drive + I_CH[a]
            t = torch.relu(drive + BG)
            t = (t + nz).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])

    for k in range(SETTLE):
        step_all(-1 - k)
    for a in arms:
        af = float((X[a] > 0.05).float().mean())
        assert 0.01 < af < 0.9, (a, af)
        af_settle[a] = af
    for i in range(WIN):
        step_all(i)
        for a in arms:
            mm[a][i] = X[a][motor].mean()
            tr[a]["fL"][i] = X[a][FL].mean()
            tr[a]["fR"][i] = X[a][FR].mean()
            tr[a]["eL"][i] = X[a][EL].mean()
            tr[a]["eR"][i] = X[a][ER].mean()
            if a != "base" and i % 100 == 0:
                chx[a][i // 100] = X[a][CH_CELLS[a]].mean()
                ch_last[a][i // 100] = X["base"][CH_CELLS[a]].mean()
    return dict(mm=mm, tr=tr, chx=chx, ch_base=ch_last, af=af_settle)


def seg_state(a, r, seg):
    lo, hi = seg
    r_mm, f = rhythm2(r["mm"][a][lo:hi])
    S = {}
    for sd_, ff, ee in (("L", "fL", "eL"), ("R", "fR", "eR")):
        ss = np.full(hi, np.nan)
        for t in range(lo + 499, hi, 10):
            ss[t] = S_of(r["tr"][a][ff][t - 499:t + 1], r["tr"][a][ee][t - 499:t + 1])
        S[sd_] = float(np.nanmedian(ss[lo + 499:hi]))
    b = fband(r_mm, f)
    lab_ = f"{b}|{ssign(S['L'])}{ssign(S['R'])}"
    return dict(label=lab_, band=b, f=round(f, 3), r=round(r_mm, 1),
                SL=round(S["L"], 3), SR=round(S["R"], 3))


# ---------- rollouts ----------
res, af_all = {}, {}
for s in CENSUS:
    arms = ["base"] + ([c[0] for c in CHANNELS] if s in TSEEDS else [])
    res[s] = run_seed(s, arms)
    af_all[s] = res[s]["af"]
    log(f"seed {s} done ({time.time()-t0:.0f}s, arms {len(arms)})")

np.savez_compressed(
    "l45/raw_l45b.npz",
    **{f"mm_{a}_{s}": res[s]["mm"][a] for s in CENSUS for a in res[s]["mm"]},
    **{f"{c}_{a}_{s}": res[s]["tr"][a][c]
       for s in CENSUS for a in res[s]["mm"] for c in ("fL", "fR", "eL", "eR")},
    **{f"chx_{a}_{s}": res[s]["chx"][a]
       for s in TSEEDS for a in res[s]["chx"]})
log(f"raw checkpointed ({time.time()-t0:.0f}s)")

# ---------- analysis ----------
census = {str(s): dict(A=seg_state("base", res[s], SEG_A),
                       B=seg_state("base", res[s], SEG_B),
                       C=seg_state("base", res[s], SEG_C)) for s in CENSUS}
states_A = [census[str(s)]["A"]["label"] for s in CENSUS]
from collections import Counter
census_states = dict(Counter(states_A))
migrations = {}
for s in CENSUS:
    labs = [census[str(s)][k]["label"] for k in ("A", "B", "C")]
    migrations[str(s)] = labs
n_mig = sum(1 for s in CENSUS
            if len(set(migrations[str(s)])) > 1)

# C0 anchors
anch_seeds = [11, 22, 33]
anch_reads = [(s, k) for s in anch_seeds for k in ("A", "B")]
anch_ok = sum(1 for s, k in anch_reads
              if census[str(s)][k]["band"] in ("slow", "mid"))
r_med = float(np.median([census[str(s)]["A"]["r"] for s in CENSUS]))
sl_med = float(np.median([census[str(s)]["A"]["SL"] for s in CENSUS]))
c0 = dict(anch_ok=f"{anch_ok}/6", r_med=round(r_med, 1), SL_med=round(sl_med, 3),
          anchor_pass=bool(anch_ok >= 5 and r_med >= 60 and sl_med > 0))

# C1 mechanics
prefix = {}
for s in TSEEDS:
    for lab_, _, _ in CHANNELS:
        prefix[f"{lab_}_{s}"] = float(np.abs(
            res[s]["mm"][lab_][:DRIVE0] - res[s]["mm"]["base"][:DRIVE0]).max())
c1 = dict(af_ok=all(0.01 < v < 0.9 for d_ in af_all.values() for v in d_.values()),
          prefix_bitident=all(v == 0.0 for v in prefix.values()),
          prefix_max=max(prefix.values()) if prefix else None)

# C3 transitions
edges = {lab_: {} for lab_, _, _ in CHANNELS}
dm_tbl = {}
for lab_, _, _ in CHANNELS:
    for s in TSEEDS:
        cs = res[s]["chx"][lab_]
        dm = float(np.mean(cs[(SEG_C[0] // 100):(SEG_C[1] // 100)])
                   - np.mean(res[s]["ch_base"][lab_][(SEG_C[0] // 100):(SEG_C[1] // 100)]))
        frm = census[str(s)]["B"]["label"]
        to = seg_state(lab_, res[s], SEG_C)
        base_to = census[str(s)]["C"]["label"]
        dm_tbl[f"{lab_}_{s}"] = round(dm, 4)
        e = edges[lab_].setdefault(frm, {"to": Counter(), "dm": [], "flat": 0})
        if abs(dm) == 0.0:
            e["to"]["<pinned:dm=0>"] += 1
            continue
        key = to["label"] if to["label"] != base_to else f"<same-as-base:{to['label']}>"
        e["to"][key] += 1
        e["dm"].append(round(dm, 3))
        if to["band"] == "FLAT":
            e["flat"] += 1

verdict = dict(C0_anchor=c0, C1_mechanics=c1,
               census_states=census_states, n_states=len(census_states),
               n_migrations=n_mig,
               migrations=migrations,
               edges={k: {f: dict(to=dict(v["to"]), flat=v["flat"],
                                  dm=v["dm"]) for f, v in vv.items()}
                      for k, vv in edges.items()},
               dm=dm_tbl)
log("VERDICT " + json.dumps({k: verdict[k] for k in
                             ("C0_anchor", "C1_mechanics", "census_states",
                              "n_states", "n_migrations")})[:1200])

json.dump(dict(meta=dict(g=G, beta=BETA, d=D, win=WIN, drive0=DRIVE0,
                         segs=[SEG_A, SEG_B, SEG_C], census=CENSUS,
                         tseeds=TSEEDS,
                         channels=[(l, t, a) for l, t, a in CHANNELS],
                         nodes=int(n), edges=len(gsrc)),
               census=census, verdict=verdict),
          open("l45/results_l45b.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l45/results_l45b.json")
