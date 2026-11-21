"""L45a: Pugliese-style pruning screen on our intrinsic self-rhythm.

Transplant of the Nature-2026-10-28 walking-CPG screen onto OUR frozen l32
regime: clamp the named core types (E1/E2/I1/I2/E3 + INXXX464, 6 cells each =
one per leg neuropil x side) to X=0 while the rhythm runs; does the rhythm
die (core-carried), perturb beyond random-type controls, or absorb it?

Activity clamp = the only honest silencing (L2 lesson). PREREG l45/PREREG-
L45a.md written first. Machinery l44-verbatim (substrate, shared noise, S
windows, rhythm2). CPU-only; no live changes.
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
CL0, CL1 = 4000, 9000            # clamp window [4000,9000) = 50 s
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05     # l32 arm-A frozen (D inert per L35)
CORE_TYPES = ("IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012",
              "INXXX464")
NAMES = {"IN17A001": "E1", "INXXX466": "E2", "IN16B036": "I1",
         "IN19A007": "I2", "IN19B012": "E3", "INXXX464": "X464"}
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: substrate (l32/l34/l39/l41-l44 verbatim) ----------
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()
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
lsup, ltyp, lside, lcls = sup[keep], typ[keep], side[keep], cls[keep]
lneuro = neuro[keep]
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

# ---------- clamped sets ----------
cells_of = {ct: np.where(ltyp == ct)[0] for ct in CORE_TYPES}
for ct, v in cells_of.items():
    assert len(v) == 6, (ct, len(v))
    got = sorted(set(lneuro[v]) | {s + m for s, m in zip(lside[v], lneuro[v])})
    assert set(lneuro[v]) == {"T1", "T2", "T3"}, (ct, got)
    for nr in ("T1", "T2", "T3"):
        assert ((lneuro[v] == nr).sum() == 2), ct

E1, E2, I1 = cells_of["IN17A001"], cells_of["INXXX466"], cells_of["IN16B036"]
core3 = np.concatenate([E1, E2, I1])
core_all = np.concatenate([cells_of[ct] for ct in CORE_TYPES])

# random controls: vnc_intrinsic types with the same 6-cell {T1,T2,T3}x{L,R}
vi = np.where(lsup == "vnc_intrinsic")[0]
grp = pd.DataFrame(dict(t=ltyp[vi], nr=lneuro[vi], sd=lside[vi]))
cand = []
for tname, gg in grp.groupby("t"):
    if tname in CORE_TYPES:
        continue
    if len(gg) == 6 and set(gg["nr"]) == {"T1", "T2", "T3"} \
            and (gg.groupby("nr")["sd"].nunique() == 2).all() \
            and set(gg["sd"]) == {"L", "R"}:
        cand.append(tname)
rng = np.random.default_rng(7)
rnd_types = sorted(rng.choice(cand, 3, replace=False).tolist())
rnd_cells = [np.where(ltyp == rt)[0] for rt in rnd_types]

ARMS = ["base"] + [f"c_{NAMES[ct]}" for ct in CORE_TYPES] + \
    ["c_core3all", "c_coreAll", "c_E1T1", "c_coreT1"] + \
    [f"rnd{i+1}" for i in range(3)]
CLAMP = {a: np.array([], np.int64) for a in ARMS}
for ct in CORE_TYPES:
    CLAMP[f"c_{NAMES[ct]}"] = cells_of[ct]
CLAMP["c_core3all"] = core3
CLAMP["c_coreAll"] = core_all
CLAMP["c_E1T1"] = E1[lneuro[E1] == "T1"]
CLAMP["c_coreT1"] = core3[lneuro[core3] == "T1"]
for i, rc in enumerate(rnd_cells):
    CLAMP[f"rnd{i+1}"] = rc
for a in ARMS:
    if a != "base":
        assert len(CLAMP[a]) > 0, a
log(f"sub {n:,}/{len(gsrc):,} | arms {len(ARMS)} | rnd types {rnd_types} "
    f"(of {len(cand)} cand) | clamp sizes "
    + ", ".join(f"{a}:{len(CLAMP[a])}" for a in ARMS if a != "base"))

# static context: clamped sets' in-weight share onto Tr pools + cord out-w
Trf = np.concatenate([PAIRS["Tr"]["fL"], PAIRS["Tr"]["fR"]])
Tre = np.concatenate([PAIRS["Tr"]["eL"], PAIRS["Tr"]["eR"]])
vi_all = np.where(lsup == "vnc_intrinsic")[0]


def inshare(dstset, srcset):
    ds = np.zeros(n, bool)
    ds[dstset] = True
    ss = np.zeros(n, bool)
    ss[srcset] = True
    m = ds[ldst] & ss[lsrc]
    return float(gw[m].sum() / gw[ds[ldst]].sum()) if ds.any() else 0.0


def outshare(srcset):
    ss = np.zeros(n, bool)
    ss[srcset] = True
    return float(gw[ss[lsrc]].sum() / gw.sum())


static = {}
for a in ARMS:
    if a == "base":
        continue
    static[a] = dict(n_cells=int(len(CLAMP[a])),
                     in_Trf=round(inshare(Trf, CLAMP[a]), 5),
                     in_Tre=round(inshare(Tre, CLAMP[a]), 5),
                     out_share=round(outshare(CLAMP[a]), 6))
static["coreAll_ref"] = dict(in_Trf=round(inshare(Trf, core_all), 5),
                             in_Tre=round(inshare(Tre, core_all), 5),
                             out_share=round(outshare(core_all), 6))
log("static " + json.dumps(static)[:600])


# ---------- rollouts ----------
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
    SIGS = ("fL", "fR", "eL", "eR")
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    xc = {a: {ct: np.zeros(WIN, np.float32) for ct in CORE_TYPES} for a in ARMS}
    cl_max = {a: 0.0 for a in ARMS}

    def step_all(k):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            t = torch.relu(drive + BG)
            t = (t + nz).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
            if a != "base" and CL0 <= k < CL1:
                X[a][CLAMP[a]] = 0.0

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
            for ct in CORE_TYPES:
                xc[a][ct][i] = X[a][cells_of[ct]].mean()
        if CL0 <= i < CL1:
            for a in ARMS:
                if a != "base":
                    cl_max[a] = max(cl_max[a], float(X[a][CLAMP[a]].max()))
    return dict(mm=mm, tr=tr, xc=xc, cl_max=cl_max,
                af_end={a: float((X[a] > 0.05).float().mean()) for a in ARMS})


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l45/raw_l45a.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"fL_{a}_{s}": res[str(s)]["tr"][a]["fL"] for a in ARMS for s in SEEDS},
    **{f"eL_{a}_{s}": res[str(s)]["tr"][a]["eL"] for a in ARMS for s in SEEDS},
    **{f"xc_{ct}_{a}_{s}": res[str(s)]["xc"][a][ct]
       for a in ARMS for s in SEEDS for ct in CORE_TYPES})
log("raw checkpointed")

# ---------------- analysis ----------------
D0, D1, D2 = 4100, 6500, 8900          # during halves
P0, P1 = 9100, 11000


def windows(a, s):
    r = res[s]
    fL, fR = r["tr"][a]["fL"], r["tr"][a]["fR"]
    eL, eR = r["tr"][a]["eL"], r["tr"][a]["eR"]
    S = np.full(WIN, np.nan)
    for t in range(499, WIN, 10):
        S[t] = S_of(fL[t - 499:t + 1] + fR[t - 499:t + 1],
                    eL[t - 499:t + 1] + eR[t - 499:t + 1])
    ts = np.arange(499, WIN, 10)
    med = lambda m: (float(np.nanmedian(S[ts[(ts >= m[0]) & (ts < m[1])]]))
                     if ((ts >= m[0]) & (ts < m[1])).any() else float("nan"))
    r_pre, f_pre = rhythm2(r["mm"][a][3400:4000])
    r_dur, f_dur = rhythm2(r["mm"][a][D0:D2])
    r_d1, f_d1 = rhythm2(r["mm"][a][D0:D1])
    r_d2, f_d2 = rhythm2(r["mm"][a][D1:D2])
    r_post, f_post = rhythm2(r["mm"][a][P0:P1])
    return dict(r_pre=round(r_pre, 1), f_pre=round(f_pre, 3),
                r_dur=round(r_dur, 1), f_dur=round(f_dur, 3),
                r_d1=round(r_d1, 1), f_d1=round(f_d1, 3),
                r_d2=round(r_d2, 1), f_d2=round(f_d2, 3),
                r_post=round(r_post, 1), f_post=round(f_post, 3),
                S_pre=round(med((3400, 4000)), 3),
                S_dur=round(med((D0, D2)), 3),
                S_post=round(med((P0, P1)), 3))


tbl = {a: {str(s): windows(a, str(s)) for s in SEEDS} for a in ARMS}
clmax = {a: max(res[str(s)]["cl_max"][a] for s in SEEDS) for a in ARMS}
prefix = {}
for a in ARMS:
    if a != "base":
        prefix[a] = max(float(np.abs(res[str(s)]["mm"][a][:CL0]
                                     - res[str(s)]["mm"]["base"][:CL0]).max())
                        for s in SEEDS)
af_end = {a: {str(s): round(res[str(s)]["af_end"][a], 4) for s in SEEDS}
          for a in ARMS}

# ---------------- verdict ----------------
md = lambda a, k: float(np.median([tbl[a][str(s)][k] for s in SEEDS]))
ANCH = {"11": 0.80, "22": 1.44, "33": 1.42}
c0 = dict(f_pre={str(s): tbl["base"][str(s)]["f_pre"] for s in SEEDS},
          anchor_ok=all(abs(tbl["base"][str(s)]["f_pre"] - ANCH[str(s)]) <= 0.05
                        for s in SEEDS),
          base_ratio_ok=md("base", "r_pre") >= 60,
          base_S_ok=md("base", "S_pre") >= 0.38)
c1 = dict(prefix_bitident=all(v == 0.0 for v in prefix.values()),
          clamp_held=all(clmax[a] == 0.0 for a in ARMS if a != "base"),
          af_ok=all(0.01 < v < 0.9 for a in ARMS for v in af_end[a].values()))

kills = {}
for a in ARMS:
    if a == "base":
        continue
    ks = [s for s in SEEDS if tbl[a][str(s)]["r_dur"] < 5 and tbl[a][str(s)]["S_dur"] < 0.1]
    if ks:
        kills[a] = [str(s) for s in ks]
c2 = dict(kills=kills, any_kill=len(kills) > 0)

effects = {}
for a in ARMS:
    if a == "base":
        continue
    per = []
    for s in SEEDS:
        b, x = tbl["base"][str(s)], tbl[a][str(s)]
        dS = abs(x["S_dur"] - b["S_dur"])
        dfn = abs(x["f_dur"] - b["f_dur"])
        ld = np.log10(max(x["r_pre"], 1e-9) / max(x["r_dur"], 1e-9))
        per.append(max(dS, dfn, float(ld)))
    effects[a] = dict(per_seed=[round(v, 3) for v in per],
                      med=round(float(np.median(per)), 3))
rnd_bar = max(float(v) for i in range(3)
              for v in effects[f"rnd{i+1}"]["per_seed"])
c3 = dict(rnd_bar=round(rnd_bar, 3),
          carriers={a: dict(med=effects[a]["med"],
                            ratio=round(effects[a]["med"] / max(rnd_bar, 1e-9), 2),
                            seeds_over_2x=sum(v > 2 * rnd_bar for v in
                                              effects[a]["per_seed"]))
                    for a in ARMS if a not in ("base", "rnd1", "rnd2", "rnd3")})

c4 = {p: dict(child=effects[p]["med"], parent=effects[q]["med"])
      for p, q in (("c_E1T1", "c_E1"), ("c_coreT1", "c_core3all"))}
c5 = {a: dict(all_recover=all(tbl[a][str(s)]["r_post"] >= 5 for s in SEEDS),
              f_post={str(s): tbl[a][str(s)]["f_post"] for s in SEEDS})
      for a in ARMS}

verdict = dict(C0_anchor=c0, C1_mechanics=c1, C2_kill=c2, C3_rank=c3,
               C4_modularity=c4, C5_restore=c5)
log("VERDICT " + json.dumps(verdict)[:2600])

json.dump(dict(meta=dict(g=G, beta=BETA, d=D, win=WIN, clamp=[CL0, CL1],
                         seeds=SEEDS, nodes=int(n), edges=len(gsrc),
                         rnd_types=rnd_types, n_cand=len(cand)),
               static=static, table=tbl, cl_max=clmax, prefix=prefix,
               af_end=af_end, effects=effects, verdict=verdict),
          open("l45/results_l45a.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l45/results_l45a.json")
