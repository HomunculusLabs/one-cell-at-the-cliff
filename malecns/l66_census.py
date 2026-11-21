"""L66: content-cell-census (LANE.md ideas-32). PREREG l66/PREREG.md FIRST.

Census n=16 of the L64 content cell (g .1, -, delay 5) + donor sham + 8-cell
negative-sign neighborhood (delay {3,4,6,8} x gain {.05,.15}). Machinery
l64_grid.py/l64_sham.py verbatim; CPU-only; no live changes.
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
SEEDS = [11, 22, 33] + list(range(101, 114))   # l45b census grid, n=16
ANCHOR_SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05
ENT_AMP = 0.3
SIGS = ("fL", "fR", "eL", "eR")
OPEN = "hynohop"
FB = dict(gfb=.1, delay=5, sign=-1.0)
FB_NAME = "g01_d05_m"
SHAM_NAME = "sham_d05m"
NEI = {f"n{gi}_d{di}_m": dict(gfb=g, delay=dl, sign=-1.0)
       for g, gi in ((.05, "005"), (.15, "015"))
       for dl, di in ((3, "03"), (4, "04"), (6, "06"), (8, "08"))}
CFG = {FB_NAME: FB, **NEI}
ARMS = [OPEN, FB_NAME, SHAM_NAME] + list(NEI)
assert len(ARMS) == 11
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l64 verbatim) ----------
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
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
assert len(mech) > 0
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in ("fL", "fR", "eL", "eR")])
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} | antag {len(ANTAG)}"
    f" | {time.time()-t0:.0f}s")

# ---------- phase + base chop AMPA (l64 verbatim) ----------
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
seg = AMPA[:2000]
assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
assert (seg[1800:2000] == ENT_AMP).all()
OFFS = [(500, 900), (1400, 1800), (4500, 4900), (5400, 5800)]

# ---------- donors (l59 stored hynohop; cyclic next-census-seed) ----------
z59 = np.load("l59/raw_l59.npz")
need = [f"{c}_hynohop_{s}" for s in SEEDS for c in SIGS]
missing = [k for k in need if k not in set(z59.keys())]
assert not missing, missing[:4]
DONOR = {s: SEEDS[(SEEDS.index(s) + 1) % len(SEEDS)] for s in SEEDS}
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


TS3 = np.arange(299, WIN, 10)


def duty_off(fL, fR, eL, eR):
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


def seg2(mm):
    errs = []
    for b in range(WIN // 500):
        if 2000 <= b * 500 < 4000 and b * 500 > 2000:
            errs.append(abs(dom_freq(mm[b * 500:(b + 1) * 500]) - 1.4))
    return round(float(np.mean(errs)), 4)


# ---------- rollouts ----------
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
    mA = {a: np.zeros(WIN, np.float32) for a in CFG}
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
            if a in CFG and k >= CFG[a]["delay"]:
                c = CFG[a]
                drive[mech, 0] += c["gfb"] * c["sign"] * float(mA[a][k - c["delay"]])
            elif a == SHAM_NAME and k >= FB["delay"]:
                drive[mech, 0] += FB["gfb"] * FB["sign"] * float(don[k - FB["delay"]])
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
            if a in CFG:
                mA[a][i] = X[a][ANTAG].mean()
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                          mm=mm, tr=tr)
    np.savez_compressed(
        "l66/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l66/raw_l66.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS})

# ---------------- anchors (enumerated keys ONLY) ----------------
z55 = np.load("l55/raw_l55.npz")
zg = np.load("l64/raw_l64.npz")
c0 = {}
for s in ANCHOR_SEEDS:
    c0[f"open_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"][OPEN] - z55[f"mm_hynohop_{s}"][:WIN]).max())
    for c in SIGS:
        c0[f"open_{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"][OPEN][c] - z55[f"{c}_hynohop_{s}"][:WIN]).max())
c0x = {}
for s in ANCHOR_SEEDS:
    c0x[f"fb_mm_{s}"] = float(np.abs(
        res[str(s)]["mm"][FB_NAME] - zg[f"mm_{FB_NAME}_{s}"][:WIN]).max())
    for c in SIGS:
        c0x[f"fb_{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"][FB_NAME][c] - zg[f"{c}_{FB_NAME}_{s}"][:WIN]).max())
c0_pass = all(v == 0.0 for v in c0.values())
c0x_pass = all(v == 0.0 for v in c0x.values())

dm, first_div = {}, {}
for a in [FB_NAME, SHAM_NAME] + list(NEI):
    dl = FB["delay"] if a == SHAM_NAME else CFG[a]["delay"]
    for s in SEEDS:
        m = res[str(s)]
        diffs = np.concatenate(
            [np.abs(m["mm"][a] - m["mm"][OPEN])]
            + [np.abs(m["tr"][a][c] - m["tr"][OPEN][c]) for c in SIGS])
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        first_div[f"{a}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{a}_{s}"] = round(float(diffs.max()), 5)
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
log(f"C0 pass {c0_pass} (19th chain) | C0x l64-fb pass {c0x_pass} | C1 {c1}")

# ---------------- analysis ----------------
cells = {}
for a in ARMS:
    for s in SEEDS:
        d = duty_off(*[res[str(s)]["tr"][a][c] for c in SIGS])
        d["e2"] = seg2(res[str(s)]["mm"][a])
        cells[(a, str(s))] = d


def arr(a, key):
    return np.array([cells[(a, str(s))][key] for s in SEEDS], float)


open_off = arr(OPEN, "duty")
open_e2 = arr(OPEN, "e2")
open_e2_med = float(np.median(open_e2))


def wilson(k, nn, z=1.96):
    if nn == 0:
        return (0.0, 0.0, 1.0)
    p = k / nn
    den = 1 + z * z / nn
    ctr = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return (round(p, 3), round(ctr - hw, 3), round(ctr + hw, 3))


def arm_block(a):
    off = arr(a, "duty")
    lift = off - open_off
    e2 = arr(a, "e2")
    k = int((lift > 0).sum())
    return dict(off=[round(float(v), 3) for v in off],
                lift=[round(float(v), 3) for v in lift],
                lift_mean=round(float(lift.mean()), 3),
                pos=k, pwilson=wilson(k, len(SEEDS)),
                e2=[round(float(v), 4) for v in e2],
                e2_med=round(float(np.median(e2)), 4),
                cat=bool(e2.max() > 0.5),
                lock_ok=bool(np.median(e2) <= max(0.01, 2 * open_e2_med)
                             and e2.max() <= 0.5),
                SL=[round(float(v), 3) for v in arr(a, "SL")],
                SR=[round(float(v), 3) for v in arr(a, "SR")],
                dm_min=round(min(dm[f"{a}_{s}"] for s in SEEDS), 5))


fbB = arm_block(FB_NAME)
shB = arm_block(SHAM_NAME)
neiB = {a: arm_block(a) for a in NEI}

# G1: P(fb lift>0) >= 11/16 AND mean sham lift <= 0.5 x mean fb lift
g1 = dict(p_pos=fbB["pos"], need=11, pwilson=fbB["pwilson"],
          lift_fb=fbB["lift_mean"], lift_sham=shB["lift_mean"],
          sham_ratio=round(shB["lift_mean"] / fbB["lift_mean"], 3)
          if fbB["lift_mean"] != 0 else None,
          pass_G1=bool(fbB["pos"] >= 11
                       and shB["lift_mean"] <= 0.5 * fbB["lift_mean"]))
# G2: point vs basin
carries = {}
for a, b in neiB.items():
    carries[a] = bool(b["lift_mean"] >= 0.05 and b["pos"] >= 11
                      and b["lock_ok"] and b["dm_min"] > 0)
n_carry = int(sum(carries.values()))
verdict_g2 = "BASIN" if n_carry >= 5 else ("POINT" if n_carry <= 2 else "MIXED")
# P3: miss anatomy — marginal side on fb miss seeds
misses = [i for i, v in enumerate(fbB["lift"]) if v <= 0]
miss_anat = []
for i in misses:
    s = SEEDS[i]
    miss_anat.append(dict(seed=s, SL=fbB["SL"][i], SR=fbB["SR"][i],
                          sl_marginal=bool(fbB["SL"][i] < fbB["SR"][i])))
p3_n = len(miss_anat)
p3_k = sum(m["sl_marginal"] for m in miss_anat)
# degenerate branch
wired_dead = [f"{a}_{s}" for a in [FB_NAME] + list(NEI) + [SHAM_NAME]
              for s in SEEDS if dm[f"{a}_{s}"] == 0.0]
# C0P: first_div == delay for every echo arm/seed (or disclosed)
c0p_ok = all(first_div[f"{a}_{s}"] ==
             (FB["delay"] if a == SHAM_NAME else CFG[a]["delay"])
             for a in [FB_NAME, SHAM_NAME] + list(NEI) for s in SEEDS)

out = dict(arms=ARMS, seeds=SEEDS, donors={str(k): v for k, v in DONOR.items()},
           open=dict(off=[round(float(v), 3) for v in open_off],
                     e2=[round(float(v), 4) for v in open_e2],
                     e2_med=round(open_e2_med, 4),
                     SL=[round(float(v), 3) for v in arr(OPEN, "SL")],
                     SR=[round(float(v), 3) for v in arr(OPEN, "SR")]),
           fb=fbB, sham=shB, neighbors=neiB,
           anchors=dict(c0_n=len(c0), c0_pass=c0_pass, c0x_n=len(c0x),
                        c0x_pass=c0x_pass, c0p_ok=bool(c0p_ok), c1=bool(c1)),
           dm=dm, first_div=first_div, wired_dead=wired_dead,
           G1=g1, G2=dict(carries=carries, n_carry=n_carry, verdict=verdict_g2),
           P3=dict(n_miss=p3_n, sl_marginal=p3_k, anatomy=miss_anat,
                   vacuous=bool(p3_n == 0)))
with open("l66/results_l66.json", "w") as f:
    json.dump(out, f, indent=1)

# C0v value anchors vs l64 stored (L44 rule)
r64 = json.load(open("l64/results.json"))
c0v = dict(fb_off=[round(abs(cells[(FB_NAME, str(s))]["duty"] - v), 4)
                   for s, v in zip(ANCHOR_SEEDS, r64["grid"][FB_NAME]["off"])],
           open_off=[round(abs(cells[(OPEN, str(s))]["duty"] - v), 4)
                     for s, v in zip(ANCHOR_SEEDS, r64["open"]["off"])],
           fb_dm_min=fbB["dm_min"])
log(f"C0v (max |recomputed - l64 stored|): fb_off {max(c0v['fb_off'])} "
    f"open_off {max(c0v['open_off'])} | fb dm_min {fbB['dm_min']}")
log(f"G1 {g1['pass_G1']} (pos {g1['p_pos']}/16 {g1['pwilson']}, lift fb "
    f"{g1['lift_fb']} sham {g1['lift_sham']})")
log(f"G2 {verdict_g2} carry {n_carry}/8 | P3 misses {p3_n} sl_marginal {p3_k}"
    f" | wired_dead {len(wired_dead)} | C0P {c0p_ok}")
log(f"fb off {fbB['off']} mean {np.mean(fbB['off']):.3f}")
log(f"open off {out['open']['off']} mean {np.mean(out['open']['off']):.3f}")
for a, b in neiB.items():
    log(f"{a}: lift {b['lift_mean']:+.3f} pos {b['pos']}/16 "
        f"lock_ok {b['lock_ok']} dm {b['dm_min']}")
log(f"done {time.time()-t0:.0f}s")
