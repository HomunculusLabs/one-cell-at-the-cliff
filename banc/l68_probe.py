"""L68 slice A: female BANC cord entrain probe (lab-only, CPU).

Arms: l65conv (bit-identity anchor vs l65/raw_l65.npz, lone rollout),
open (free-run), hyb03/hyb01 (l55 hybrid chop schedule, amp dose guard).
PREREG: l68/PREREG.md (written first). Raw npz checkpoint BEFORE analysis.
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
SETTLE, WIN = 400, 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG, BLK, MEAS0 = 2000, 500, 500
SEEDS = [11, 22, 33]
G, BETA, D = 0.14, 2.0, 0.2          # L65 arm-B frozen
ENT_AMPS = {"hyb03": 0.3, "hyb01": 0.1}
GROUP = ["open", "hyb03", "hyb01"]
LOCK_TOL = 0.10
DATA = "/home/t3rpz/critters/peabrain-lab/banc/data"
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------------- subnet (l65 extraction verbatim) ----------------
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()

ann = pd.read_csv(f"{DATA}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv(f"{DATA}/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64),
                  nt["neurotransmitter_predicted"].astype(str).str.lower()))
is_glut = np.zeros(Nall, bool)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate":
        is_glut[j] = True

region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True

conn = pd.read_csv(f"{DATA}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all)
            & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into &= dn_all
keep = cord_mask | dn_into
assert int(keep.sum()) == 21249, keep.sum()

emask = keep[src_all] & keep[dst_all]
gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
assert len(gsrc) == 627051, len(gsrc)
loc = -np.ones(Nall, np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
gsign_a = sign_all[gsrc]
gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
Wb_vals = (np.log1p(gcount) * gsign_b).astype(np.float32)


def build_W(dst, src, vals):
    t = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([dst, src])).long(),
        torch.from_numpy(vals.astype(np.float32)), (n, n))
    return t.coalesce().to_sparse_csr()


Wc = build_W(ldst, lsrc, Wb_vals)

# pools per side
mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
in_sub = keep[mgi]


SIDE_MAP = {"L": "left", "R": "right"}


def pool(sel, sd):
    sdl = SIDE_MAP[sd.upper()]
    m = in_sub & sel & (side_m == sdl)
    return loc[mgi[m]]


def has(s, t=ptt):
    return np.array([s in x for x in t])


PAIRS = {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"), has("trochanter") & has("extensor")),
]:
    PAIRS[k] = {c: pool(fpat if c[0] == "f" else epat, c[1])
                for c in ("fL", "fR", "eL", "eR")}
    assert all(len(v) > 0 for v in PAIRS[k].values()), (k, PAIRS[k])

sub_dn = ann[ann.super_class == "descending"]
dng100_all = sub_dn.gi[sub_dn.cell_type.fillna("").astype(str)
                        .to_numpy() == "DNg100"].to_numpy()
dng100 = np.sort(loc[dng100_all[keep[dng100_all]]])
assert len(dng100) == 2, len(dng100)

# full (pooled) pools for the l65 anchor semantics — mean is order-invariant
POOLFULL = {k: (np.concatenate([d["fL"], d["fR"]]),
                np.concatenate([d["eL"], d["eR"]])) for k, d in PAIRS.items()}

motor = np.zeros(n, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor[loc[mg[keep[mg]]]] = True

# mech channel: cell_function tactile/proprioceptive (registered)
cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech = np.where(mech_mask[keep])[0]
MECH_N = int(mech_mask[keep].sum())
log(f"subnet {n:,} edges {len(lsrc):,} | mech {MECH_N} | "
    f"pools {[(k, [len(v) for v in d.values()]) for k, d in PAIRS.items()]} "
    f"| {time.time()-t0:.0f}s")

# ---------------- schedule (l55 form) ----------------
def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


AMPA = {}
for a, amp in ENT_AMPS.items():
    t = np.zeros(WIN, np.float64)
    for seg0, _, _ in SEGB:
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            t[lo:min(lo + 500, seg0 + SEG)] = amp
            c += 1
    t[2000:4000] = amp
    AMPA[a] = t
    assert (t[:500] == amp).all() and (t[500:900] == 0).all()
    assert (t[2000:4000] == amp).all()
    assert int((t > 0).sum()) + SETTLE == 4800
log("drive-on 48.0 s both hyb arms | tables asserted")


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


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


SIGS = ("fL", "fR", "eL", "eR")

# ---------------- anchor arm: l65 run() verbatim (lone) ----------------
def run_l65(seed):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wbeta = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals,
                                    Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D

    def step(cur, drive_I):
        drive = torch.sparse.mm(Wbeta, cur) * G + drive_I
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for _ in range(SETTLE):
        X = step(X, torch.zeros(n, 1))
    T = WIN
    tr = {k: {c: np.zeros(T, np.float32) for c in SIGS} for k in PAIRS}
    pf = {k: (np.zeros(T, np.float32), np.zeros(T, np.float32)) for k in PAIRS}
    mm = np.zeros(T, np.float32)
    for k in range(T):
        X = step(X, I)
        for pk in PAIRS:
            for c in SIGS:
                tr[pk][c][k] = X[PAIRS[pk][c]].mean()
            pf[pk][0][k] = X[POOLFULL[pk][0]].mean()
            pf[pk][1][k] = X[POOLFULL[pk][1]].mean()
        mm[k] = X[motor].mean()
    return tr, pf, mm


# ---------------- multi-arm group (shared noise, L45b form) ----------------
def run_group(seed):
    gen = torch.Generator().manual_seed(seed)
    X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    X = {a: X0.clone() for a in GROUP}
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals,
                                 Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    settle_ph = 0.0
    tr = {a: {pk: {c: np.zeros(WIN, np.float32) for c in SIGS}
              for pk in PAIRS} for a in GROUP}
    mm = {a: np.zeros(WIN, np.float32) for a in GROUP}

    def step_all(k):
        nonlocal settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        ph_k = PHI[k] if k >= 0 else settle_ph
        if k < 0:
            settle_ph += 2 * math.pi * 0.7 * DT
        sin_ph = math.sin(ph_k)
        for a in GROUP:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            amp_k = float(AMPA[a][k]) if (k >= 0 and a in AMPA) else (
                ENT_AMPS[a] if (k < 0 and a in AMPA) else 0.0)
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            t = torch.relu(drive + BG)
            t = (t + nz).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])

    for k in range(SETTLE):
        step_all(-1 - k)
    for a in GROUP:
        af = float((X[a] > 0.05).float().mean())
        assert 0.01 < af < 0.9, (a, af)
    for i in range(WIN):
        step_all(i)
        for a in GROUP:
            mm[a][i] = X[a][motor].mean()
            for pk in PAIRS:
                for c in SIGS:
                    tr[a][pk][c][i] = X[a][PAIRS[pk][c]].mean()
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in GROUP},
                mm=mm, tr=tr)


ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------------- rollouts + raw checkpoint ----------------
npz = {}
anch = {}
for s in SEEDS:
    tr, pf, mm = run_l65(s)
    anch[str(s)] = dict(af=None)
    for pk in PAIRS:
        npz[f"l65conv_s{s}_{pk}_f"] = pf[pk][0]
        npz[f"l65conv_s{s}_{pk}_e"] = pf[pk][1]
    npz[f"l65conv_s{s}_mm"] = mm
log(f"l65conv lone rollouts done | {time.time()-t0:.0f}s")

grp = {}
for s in SEEDS:
    grp[str(s)] = run_group(s)
    for a in GROUP:
        for pk in PAIRS:
            for c in SIGS:
                npz[f"{a}_s{s}_{pk}_{c}"] = grp[str(s)]["tr"][a][pk][c]
        npz[f"{a}_s{s}_mm"] = grp[str(s)]["mm"][a]
np.savez_compressed("l68/raw_l68.npz", **npz)
log(f"group rollouts done, raw checkpointed | {time.time()-t0:.0f}s")

# ---------------- C0 anchors ----------------
z65 = np.load("l65/raw_l65.npz")
c0_max = []
for s in SEEDS:
    for pk in PAIRS:
        for c in ("f", "e"):
            c0_max.append(float(np.abs(npz[f"l65conv_s{s}_{pk}_{c}"]
                                       - z65[f"B_s{s}_{pk}_{c}"]).max()))
    c0_max.append(float(np.abs(npz[f"l65conv_s{s}_mm"]
                               - z65[f"B_s{s}_mm"]).max()))
c0 = dict(
    l65_bitid_max=float(max(c0_max)),
    subnet_n=n == 21249, subnet_edges=len(lsrc) == 627051,
    dng100=len(dng100) == 2, mech_count=MECH_N,
    pools={k: [len(v) for v in d.values()] for k, d in PAIRS.items()},
)
# open-arm substrate health
open_r = {}
for s in SEEDS:
    rr, fr = dom_freq(grp[str(s)]["mm"]["open"])
    sl = S_of(grp[str(s)]["tr"]["open"]["Ti"]["fL"],
              grp[str(s)]["tr"]["open"]["Ti"]["eL"])
    sr = S_of(grp[str(s)]["tr"]["open"]["Ti"]["fR"],
              grp[str(s)]["tr"]["open"]["Ti"]["eR"])
    open_r[str(s)] = dict(ratio=round(rr, 1), f=round(fr, 3),
                          S_Ti_L=round(sl, 3), S_Ti_R=round(sr, 3))
c0["open_rhythm"] = open_r
c0["open_gate"] = all(v["ratio"] > 100 for v in open_r.values()) and \
    all(v["S_Ti_L"] > 0.40 or v["S_Ti_R"] > 0.40 for v in open_r.values())
# G3 dead-channel check
g3_dm = max(float(np.abs(grp[str(s)]["mm"]["hyb03"]
                         - grp[str(s)]["mm"]["open"]).max()) for s in SEEDS)
log(f"C0 l65_bitid {c0['l65_bitid_max']:.1e} | open {open_r} | dm {g3_dm:.3f}")

json.dump(dict(c0=c0, open=open_r, g3_dm=g3_dm),
          open("l68/scan_l68.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l68/raw_l68.npz + scan_l68.json "
    f"(analysis in l68_verdict.py)")
