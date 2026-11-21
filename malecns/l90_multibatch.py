"""L90: multi-batch gate re-base (LANE.md ideas 45). PREREG l90/PREREG.md FIRST.

Roll the 4 l87 trunk arms on fresh batches B2=601-616, B3=701-716, complete
B1=501-516 (hybrid bit-anchor vs raw_l88), re-roll census seeds 11/22/33 as
the chain anchor. l87_branch.py step order VERBATIM. CPU-only; checkpoint to
l90/raw_partial.npz per seed (resume-safe); l90_verdict.py re-derives reads.
"""
import math
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
WIN = 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
HOP_AMP, HOP_VW = 0.5, 40
TRANS = [2000, 4000]
FB = dict(gfb=.1, delay=5, sign=-1.0)          # l66 content cell verbatim
TRUNKS = ["hynohop", "hynohop_fb", "hybrid", "hybrid_fb"]
HOP_TRUNKS = {"hybrid", "hybrid_fb"}
ECHO_ARMS = ["hynohop_fb", "hybrid_fb"]
SIGS = ("fL", "fR", "eL", "eR")
EON = {a: (np.ones(WIN, bool) if a in ECHO_ARMS else np.zeros(WIN, bool))
       for a in TRUNKS}
CENSUS_ANCHOR = [11, 22, 33]
B1 = list(range(501, 517))
B2 = list(range(601, 617))
B3 = list(range(701, 717))
PLAN = [("B1", B1), ("B2", B2), ("B3", B3), ("B0a", CENSUS_ANCHOR)]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l59/l66/l77/l82/l86/l87 verbatim) ----------
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
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)

ntk = nt_names[keep]
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in ntk], np.float32)
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
hopL = np.where((ltyp == "DNge046") & (lside == "L"))[0]
assert len(hopL) == 2, len(hopL)
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
assert len(mech) > 0
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in SIGS])   # l66-verbatim
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} | antag {len(ANTAG)}"
    f" | 046L {len(hopL)} | {time.time()-t0:.0f}s")

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- per-arm AMPA / HOPA tables (l87 verbatim) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in TRUNKS}
for a in TRUNKS:
    for seg0, _, _ in SEGB:
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA[a][2000:4000] = ENT_AMP
HOPA = {a: np.zeros(WIN, bool) for a in TRUNKS}
for o in TRANS:
    for a in HOP_TRUNKS:
        HOPA[a][o:o + HOP_VW] = True
assert all(np.array_equal(AMPA[a], AMPA["hynohop"]) for a in TRUNKS)
assert all(HOPA[a].sum() == (2 * HOP_VW if a in HOP_TRUNKS else 0) for a in TRUNKS)
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in TRUNKS}
assert all(v == 4800 for v in DRIVE_ON.values()), DRIVE_ON
assert EON["hynohop_fb"].all() and EON["hybrid_fb"].all()
assert not EON["hynohop"].any() and not EON["hybrid"].any()
log("drive-on 48.0s all arms | tables asserted")

# ---------- resume ----------
store = {}
if os.path.exists("l90/raw_partial.npz"):
    z = np.load("l90/raw_partial.npz")
    store = {k: z[k] for k in z.files}
    log(f"resume: {len(set(k.rsplit('_', 1)[1] for k in store if k.startswith('mm_')))}"
        f" seeds already complete")


def save_partial():
    if store:
        np.savez("l90/raw_partial.npz", **store)


# ---------- rollouts (l87 step order verbatim) ----------
for bname, seeds in PLAN:
    for seed in seeds:
        if f"mm_hynohop_{seed}" in store:
            log(f"{bname} seed {seed} cached, skip")
            continue
        gen = torch.Generator().manual_seed(seed)
        X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
        X = {a: X0.clone() for a in TRUNKS}
        neg = Wc.values() < 0
        vals = Wc.values().clone()
        vals[neg] *= BETA
        Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals,
                                     Wc.shape)
        I = torch.zeros(n, 1)
        I[dng100] = D
        settle_ph = 0.0
        mm = {a: np.zeros(WIN, np.float32) for a in TRUNKS}
        tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in TRUNKS}
        mA = {a: np.zeros(WIN, np.float32) for a in ECHO_ARMS}
        af = {}

        def step_all(k):
            global settle_ph
            nz = NOISE * torch.randn(n, 1, generator=gen)
            if k >= 0:
                ph_k = PHI[k]
            else:
                settle_ph += 2 * math.pi * 0.7 * DT
                ph_k = settle_ph
            sin_ph = math.sin(ph_k)
            for a in TRUNKS:
                drive = torch.sparse.mm(Wb, X[a]) * G + I
                if k < 0:
                    amp_k = ENT_AMP
                else:
                    amp_k = float(AMPA[a][k])
                if amp_k > 0.0:
                    drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
                if k >= 0 and HOPA[a][k]:
                    drive[hopL, 0] += HOP_AMP
                if a in ECHO_ARMS and k >= FB["delay"] and EON[a][k]:
                    drive[mech, 0] += (FB["gfb"] * FB["sign"]
                                       * float(mA[a][k - FB["delay"]]))
                t = torch.relu(drive + BG)
                t = (t + nz).clamp(max=RMAX)
                X[a] = X[a] + (DT / TAU) * (t - X[a])

        for k in range(SETTLE):
            step_all(-1 - k)
        for a in TRUNKS:
            af[a] = float((X[a] > 0.05).float().mean())
            assert 0.01 < af[a] < 0.9, (a, af[a])
        for i in range(WIN):
            step_all(i)
            for a in TRUNKS:
                mm[a][i] = X[a][motor].mean()
                for c in SIGS:
                    tr[a][c][i] = X[a][PAIRS["Tr"][c]].mean()
                if a in ECHO_ARMS:
                    mA[a][i] = X[a][ANTAG].mean()
        for a in TRUNKS:
            store[f"mm_{a}_{seed}"] = mm[a]
            for c in SIGS:
                store[f"{c}_{a}_{seed}"] = tr[a][c]
        for a in ECHO_ARMS:
            store[f"mA_{a}_{seed}"] = mA[a]
        store[f"af_{seed}"] = np.array([af[a] for a in TRUNKS], np.float32)
        save_partial()
        log(f"{bname} seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")

# ---------- final checkpoint (compressed) ----------
final_keys = [k for k in store if not k.startswith("af_")]
np.savez_compressed("l90/raw_l90.npz",
                    **{k: store[k] for k in final_keys},
                    **{f"afv_{k[3:]}": v for k, v in store.items()
                       if k.startswith("af_")})
log("raw_l90.npz checkpointed BEFORE analysis (crash => l90_verdict.py re-derives)")

# ---------------- anchors (run-side) ----------------
z87 = np.load("l87/raw_l87.npz")
z88 = np.load("l88/raw_l88.npz")
c0a = {}
for a in TRUNKS:
    for s in CENSUS_ANCHOR:
        c0a[f"mm|{a}_{s}"] = float(np.abs(
            store[f"mm_{a}_{s}"] - z87[f"mm_{a}_{s}"][:WIN]).max())
        for c in SIGS:
            c0a[f"{c}|{a}_{s}"] = float(np.abs(
                store[f"{c}_{a}_{s}"] - z87[f"{c}_{a}_{s}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())
c0d = {}
for s in B1:
    c0d[f"mm|hybrid_{s}"] = float(np.abs(
        store[f"mm_hybrid_{s}"] - z88[f"mm_hybrid_{s}"][:WIN]).max())
    for c in SIGS:
        c0d[f"{c}|hybrid_{s}"] = float(np.abs(
            store[f"{c}_hybrid_{s}"] - z88[f"{c}_hybrid_{s}"][:WIN]).max())
c0d_pass = all(v == 0.0 for v in c0d.values())

# C0E: fb-vs-base first divergence == 6 on every NEW seed (B1/B2/B3)
c0e_fd = {}
for s in B1 + B2 + B3:
    for fb, base in (("hynohop_fb", "hynohop"), ("hybrid_fb", "hybrid")):
        diffs = np.concatenate(
            [np.abs(store[f"mm_{fb}_{s}"] - store[f"mm_{base}_{s}"])] + [
                np.abs(store[f"{c}_{fb}_{s}"] - store[f"{c}_{base}_{s}"])
                for c in SIGS])
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        c0e_fd[f"{fb}_{s}"] = fd
c0e_pass = all(v == 6 for v in c0e_fd.values())
c1 = all(0.01 < float(v) < 0.9 for k, v in store.items()
         if k.startswith("af_") for v in v)

log(f"C0A chain(census 3-seed x 4 trunks) {c0a_pass} | C0D hybrid-B1 "
    f"{c0d_pass} | C0E fd==6 {c0e_pass} (set {sorted(set(c0e_fd.values()))})"
    f" | C1 {c1}")
json_anchor = dict(c0a_max=max(c0a.values()), c0d_max=max(c0d.values()),
                   c0e_fd=c0e_fd, c0a_pass=c0a_pass, c0d_pass=c0d_pass,
                   c0e_pass=c0e_pass, c1=c1)
import json
json.dump(json_anchor, open("l90/anchors_run.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l90/raw_l90.npz + anchors_run.json")
