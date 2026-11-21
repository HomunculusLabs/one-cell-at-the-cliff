"""L78: female BANC echo replication (lab-only, CPU). PREREG l78/PREREG.md FIRST.

Arms (one shared-noise group per seed): open (hyb01 replica, C0a anchor),
fbn_g01 (male content cell), fbp_g01 (sign re-derivation), fbn_g03
(budget-matched), sham_g01 (next-seed cyclic donor from l68 stored hyb01).
Rollouts -> raw npz + scan json (anchors C0a/C0P/C1/C2 + budget).
Analysis (R1-R5) in l78_verdict.py, separate so a crash costs nothing.
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
SEG = 2000
SEEDS = [11, 22, 33]
G, BETA, D = 0.14, 2.0, 0.2          # L65 arm-B frozen (l68 verbatim)
ENT_AMP = 0.1                         # hyb01
SIGS = ("fL", "fR", "eL", "eR")
OPEN = "open"
CFG = {
    "fbn_g01": dict(gfb=.1, sign=-1.0, delay=5),
    "fbp_g01": dict(gfb=.1, sign=+1.0, delay=5),
    "fbn_g03": dict(gfb=.0333, sign=-1.0, delay=5),
}
SHAM = "sham_g01"
SHAM_CFG = dict(gfb=.1, sign=-1.0, delay=5)
ARMS = [OPEN] + list(CFG) + [SHAM]
DATA = "/home/t3rpz/critters/peabrain-lab/banc/data"
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------------- subnet (l68_probe.py extraction verbatim) ----------------
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

Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy(Wb_vals.astype(np.float32)), (n, n)
).coalesce().to_sparse_csr()

# pools per side (l68 verbatim)
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
# l68 stored pool sizes — extraction-drift guard
assert {k: [len(v) for v in d.values()] for k, d in PAIRS.items()} == \
    {"Ti": [50, 51, 6, 6], "Tr": [31, 31, 24, 24]}, "pool sizes drifted"

sub_dn = ann[ann.super_class == "descending"]
dng100_all = sub_dn.gi[sub_dn.cell_type.fillna("").astype(str)
                       .to_numpy() == "DNg100"].to_numpy()
dng100 = np.sort(loc[dng100_all[keep[dng100_all]]])
assert len(dng100) == 2, len(dng100)

motor = np.zeros(n, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor[loc[mg[keep[mg]]]] = True

cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech = np.where(mech_mask[keep])[0]
MECH_N = int(mech_mask[keep].sum())
assert MECH_N == 4848, MECH_N

ANTAG = np.concatenate([PAIRS["Tr"][c] for c in SIGS])   # male echo-source form
pools_str = {k: [len(v) for v in d.values()] for k, d in PAIRS.items()}
log(f"subnet {n:,} edges {len(lsrc):,} | mech {MECH_N} | antag {len(ANTAG)} "
    f"| pools {pools_str} | {time.time()-t0:.0f}s")

# ---------------- schedule: l68 hyb01 AMPA table verbatim ----------------
AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
assert (AMPA[:500] == ENT_AMP).all() and (AMPA[500:900] == 0).all()
assert (AMPA[2000:4000] == ENT_AMP).all()
assert int((AMPA > 0).sum()) + SETTLE == 4800

ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# donors: next-seed cyclic hyb01 ANTAG-mean from l68 stored raw (l66 form)
z68 = np.load("l68/raw_l68.npz")
DONOR = {s: SEEDS[(SEEDS.index(s) + 1) % len(SEEDS)] for s in SEEDS}
DONOR_M = {}
for s in SEEDS:
    d = DONOR[s]
    DONOR_M[s] = ((z68[f"hyb01_s{d}_Tr_fL"] + z68[f"hyb01_s{d}_Tr_fR"]
                   + z68[f"hyb01_s{d}_Tr_eL"] + z68[f"hyb01_s{d}_Tr_eR"])
                  / 4.0).astype(np.float32)
log("donors " + " ".join(f"{s}<-{DONOR[s]}" for s in SEEDS))


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


# ---------------- rollouts (l68 run_group form + echo wiring) ----------------
res = {}
for seed in SEEDS:
    gen = torch.Generator().manual_seed(seed)
    X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    X = {a: X0.clone() for a in ARMS}
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals,
                                 Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    settle_ph = 0.0
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    xm = {a: np.zeros(WIN, np.float32) for a in ARMS}   # mech mean (fd anchor)
    mA = {a: np.zeros(WIN, np.float32) for a in CFG}    # echo source per arm
    tr = {a: {pk: {c: np.zeros(WIN, np.float32) for c in SIGS}
              for pk in PAIRS} for a in ARMS}
    don = DONOR_M[seed]

    def step_all(k):
        global settle_ph
        nz = NOISE * torch.randn(n, 1, generator=gen)
        ph_k = PHI[k] if k >= 0 else settle_ph
        if k < 0:
            settle_ph += 2 * math.pi * 0.7 * DT
        sin_ph = math.sin(ph_k)
        amp_k = ENT_AMP if k < 0 else float(AMPA[k])
        sin_term = amp_k * (0.5 + 0.5 * sin_ph)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + sin_term
            if a in CFG and k >= CFG[a]["delay"]:
                c = CFG[a]
                drive[mech, 0] += c["gfb"] * c["sign"] * float(mA[a][k - c["delay"]])
            elif a == SHAM and k >= SHAM_CFG["delay"]:
                drive[mech, 0] += (SHAM_CFG["gfb"] * SHAM_CFG["sign"]
                                   * float(don[k - SHAM_CFG["delay"]]))
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
            xm[a][i] = X[a][mech].mean()
            for pk in PAIRS:
                for c in SIGS:
                    tr[a][pk][c][i] = X[a][PAIRS[pk][c]].mean()
            if a in CFG:
                mA[a][i] = X[a][ANTAG].mean()
    res[str(seed)] = dict(
        af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
        mm=mm, xm=xm, tr=tr, mA=mA)
    np.savez_compressed(
        "l78/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a]["Tr"][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")

# ---------------- raw checkpoint (BEFORE any analysis) ----------------
np.savez_compressed(
    "l78/raw_l78.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"xm_{a}_{s}": res[str(s)]["xm"][a] for a in ARMS for s in SEEDS},
    **{f"mA_{a}_{s}": res[str(s)]["mA"][a] for a in CFG for s in SEEDS},
    **{f"{pk}_{c}_{a}_{s}": res[str(s)]["tr"][a][pk][c]
       for a in ARMS for s in SEEDS for pk in PAIRS for c in SIGS})

# ---------------- anchors (enumerated keys ONLY) ----------------
# C0a: open == l68 stored hyb01, bit-identical, on mm + Tr + Ti traces
c0a = {}
for s in SEEDS:
    c0a[f"open_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"][OPEN] - z68[f"hyb01_s{s}_mm"][:WIN]).max())
    for pk in PAIRS:
        for c in SIGS:
            c0a[f"open_{pk}_{c}_{s}"] = float(np.abs(
                res[str(s)]["tr"][OPEN][pk][c]
                - z68[f"hyb01_s{s}_{pk}_{c}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())

# C0P: first divergence vs open, xm (mech, expect 5) and mm (motor, expect 6)
c0p = {}
for a in list(CFG) + [SHAM]:
    for s in SEEDS:
        dx = np.abs(res[str(s)]["xm"][a] - res[str(s)]["xm"][OPEN])
        dm = np.abs(res[str(s)]["mm"][a] - res[str(s)]["mm"][OPEN])
        c0p[f"fd_xm_{a}_{s}"] = int(np.argmax(dx > 0)) if (dx > 0).any() else -1
        c0p[f"fd_mm_{a}_{s}"] = int(np.argmax(dm > 0)) if (dm > 0).any() else -1
c0p_pass_xm = all(c0p[f"fd_xm_{a}_{s}"] == 5 for a in CFG for s in SEEDS)
c0p_pass_mm = all(c0p[f"fd_mm_{a}_{s}"] == 6 for a in list(CFG) + [SHAM]
                  for s in SEEDS)

# C2 dm probe: every treatment arm must actually diverge
c2 = {f"{a}_{s}": float(np.abs(res[str(s)]["mm"][a] - res[str(s)]["mm"][OPEN]).max())
      for a in list(CFG) + [SHAM] for s in SEEDS}
c2_pass = all(v > 0.0 for v in c2.values())

# R5 budget: mean|echo| / mean sin_term over drive-on steps
on = AMPA > 0
sin_mean = float(np.mean([ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k]))
                          for k in range(WIN) if on[k]]))
budget = {}
for a in CFG:
    g = CFG[a]
    e = np.abs(res[str(SEEDS[0])]["mA"][a][
        [k - g["delay"] for k in range(WIN) if k >= g["delay"] and on[k]]])
    budget[a] = round(float(g["gfb"] * e.mean() / sin_mean), 4)
don_e = np.abs(DONOR_M[SEEDS[0]][
    [k - 5 for k in range(WIN) if k >= 5 and on[k]]])
budget[SHAM] = round(float(SHAM_CFG["gfb"] * don_e.mean() / sin_mean), 4)

scan = dict(
    arms=ARMS, seeds=SEEDS, c0a=c0a, c0a_pass=bool(c0a_pass),
    c0p=c0p, c0p_pass_xm=bool(c0p_pass_xm), c0p_pass_mm=bool(c0p_pass_mm),
    c2=c2, c2_pass=bool(c2_pass), budget=budget,
    af={s: res[str(s)]["af"] for s in SEEDS},
    mech_n=MECH_N, antag_n=int(len(ANTAG)))
json.dump(scan, open("l78/scan_l78.json", "w"), indent=1)
log(f"C0a bit-id pass {c0a_pass} (max {max(c0a.values()):.1e}) | "
    f"C0P xm5 {c0p_pass_xm} mm6 {c0p_pass_mm} | C2 {c2_pass} | "
    f"budget {budget}")
log(f"done {time.time()-t0:.0f}s -> l78/raw_l78.npz + scan_l78.json "
    f"(R1-R5 in l78_verdict.py)")
