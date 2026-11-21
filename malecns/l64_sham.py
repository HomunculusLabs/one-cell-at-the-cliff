"""L64 sham control: donor-sham for the two candidate winner cells
(g01_d20_p max-mean, g01_d05_m max-consistency). PREREG l64/PREREG.md
(winner-sham rule); extension to 2 cells disclosed in LAB-INTENT.
Donor = l59 stored open hynohop, next-seed pairing (l63 form).
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
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
SEEDS = [11, 22, 33]
SEEDS8 = [11, 22, 33, 101, 105, 109, 111, 113]
G, BETA, D = 0.01, 2.0, 0.05
ENT_AMP = 0.3
SIGS = ("fL", "fR", "eL", "eR")
OPEN = "hynohop"
W1 = ("g01_d20_p", .1, 20, 1.0)     # name, gfb, delay, sign
W2 = ("g01_d05_m", .1, 5, -1.0)
FB = {W1[0]: W1, W2[0]: W2}
SHAM = {"sham_d20p": (.1, 20, 1.0), "sham_d05m": (.1, 5, -1.0)}
ARMS = [OPEN] + list(FB) + list(SHAM)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


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
assert n == 21516
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
    PAIRS[k] = dict(fL=f[lside[f] == "L"], fR=f[lside[f] == "R"],
                    eL=e[lside[e] == "L"], eR=e[lside[e] == "R"])
dng100 = np.where(ltyp == "DNg100")[0]
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in ("fL", "fR", "eL", "eR")])

ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

AMPA = np.zeros(WIN, np.float64)
for seg0, _, f in SEGB:
    if f != 0.7:
        AMPA[seg0:seg0 + SEG] = ENT_AMP
        continue
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
OFFS = [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)]

z59 = np.load("l59/raw_l59.npz")
DONOR = {s: SEEDS8[(SEEDS8.index(s) + 1) % len(SEEDS8)] for s in SEEDS}
DONOR_M = {}
for s in SEEDS:
    d = DONOR[s]
    DONOR_M[s] = ((z59[f"fL_hynohop_{d}"] + z59[f"fR_hynohop_{d}"]
                   + z59[f"eL_hynohop_{d}"] + z59[f"eR_hynohop_{d}"]) / 4.0
                  ).astype(np.float32)
log("donors " + " ".join(f"{s}<-{DONOR[s]}" for s in SEEDS))


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


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
    return float(f_hat)


res = {}
for seed in SEEDS:
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
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    mA = {a: np.zeros(WIN, np.float32) for a in list(FB)}
    don = DONOR_M[seed]

    def step_all(k):
        global settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        ph_k = PHI[k] if k >= 0 else None
        if k < 0:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
        sin_ph = math.sin(ph_k)
        amp_k = ENT_AMP if k < 0 else float(AMPA[k])
        sin_term = amp_k * (0.5 + 0.5 * sin_ph)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + sin_term
            if a in FB and k >= FB[a][2]:
                _, gfb, dl, sg = FB[a]
                drive[mech, 0] += gfb * sg * float(mA[a][k - dl])
            elif a in SHAM and k >= SHAM[a][1]:
                gfb, dl, sg = SHAM[a]
                drive[mech, 0] += gfb * sg * float(don[k - dl])
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
            if a in FB:
                mA[a][i] = X[a][ANTAG].mean()
    res[str(seed)] = dict(mm=mm, tr=tr)
    log(f"seed {seed} done {time.time()-t0:.0f}s")

np.savez_compressed(
    "l64/raw_l64_sham.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS})

# anchors: in-run open + fb cells must be bit-identical to the GRID run
zg = np.load("l64/raw_l64.npz")
anch = {}
for s in SEEDS:
    for a in [OPEN] + list(FB):
        anch[f"{a}_mm_{s}"] = float(np.abs(
            res[str(s)]["mm"][a] - zg[f"mm_{a}_{s}"]).max())
        for c in SIGS:
            anch[f"{a}_{c}_{s}"] = float(np.abs(
                res[str(s)]["tr"][a][c] - zg[f"{c}_{a}_{s}"]).max())
anch_pass = all(v == 0.0 for v in anch.values())
log(f"anchor grid-replication pass {anch_pass} ({len(anch)} keys)")

TS3 = np.arange(299, WIN, 10)


def duty_off(a, s):
    fL, fR, eL, eR = (res[s]["tr"][a][c] for c in SIGS)
    hits, sls, srs = [], [], []
    for lo, hi in OFFS:
        for t in TS3[(TS3 >= lo + 299) & (TS3 < hi)]:
            SL = S_of(fL[t - 299:t + 1], eL[t - 299:t + 1])
            SR = S_of(fR[t - 299:t + 1], eR[t - 299:t + 1])
            hits.append((SL >= 0.25) & (SR >= 0.25))
            sls.append(SL)
            srs.append(SR)
    return dict(duty=round(float(np.nanmean(np.array(hits, float))), 3),
                SL=round(float(np.nanmean(sls)), 3),
                SR=round(float(np.nanmean(srs)), 3))


def seg2(a, s):
    errs = []
    for b in range(WIN // 500):
        if 2000 <= b * 500 < 4000 and b * 500 > 2000:
            errs.append(abs(dom_freq(res[s]["mm"][a][b * 500:(b + 1) * 500]) - 1.4))
    return round(float(np.mean(errs)), 4)


out = dict(anchors_pass=anch_pass)
for a in ARMS:
    offs = [duty_off(a, str(s))["duty"] for s in SEEDS]
    out[a] = dict(off=[round(v, 3) for v in offs],
                  e2=[seg2(a, str(s)) for s in SEEDS],
                  SL=round(float(np.mean([duty_off(a, str(s))["SL"] for s in SEEDS])), 3),
                  SR=round(float(np.mean([duty_off(a, str(s))["SR"] for s in SEEDS])), 3))
    log(f"{a}: off {out[a]['off']} mean {np.mean(out[a]['off']):.3f} "
        f"| SL {out[a]['SL']} SR {out[a]['SR']} | e2 {out[a]['e2']}")
verdict = {}
for wname, shname in ((W1[0], "sham_d20p"), (W2[0], "sham_d05m")):
    lf = np.mean(out[wname]["off"]) - np.mean(out[OPEN]["off"])
    ls = np.mean(out[shname]["off"]) - np.mean(out[OPEN]["off"])
    verdict[wname] = dict(lift_fb=round(float(lf), 3), lift_sham=round(float(ls), 3),
                          content=bool(lf >= 0.10 and ls < 0.5 * lf))
out["verdict"] = verdict
with open("l64/results_sham.json", "w") as f:
    json.dump(out, f, indent=1)
log(f"verdict {json.dumps(verdict)} | done {time.time()-t0:.0f}s")
