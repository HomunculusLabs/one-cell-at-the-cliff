"""L82: echo-hold-law (LANE.md ideas-41). PREREG l82/PREREG.md FIRST.

Does the l66 content-cell echo need to run THROUGH the fast seg, or only
during the 0.7 segs it lifts? 3 arms on the l59 nohop schedule: never /
echo-throughout (l66 wiring verbatim) / echo-on-0.7-segs-only (NEW).
Machinery l77_census.py verbatim; CPU-only; raw npz checkpoint BEFORE
analysis; no live changes.
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
BLK = 500
MEAS0 = 500
SEEDS = [11, 22, 33] + list(range(101, 114))   # l45b census grid, n=16
ANCHOR_SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
LOCK_TOL = 0.10
FB = dict(gfb=.1, delay=5, sign=-1.0)          # l66 content cell verbatim
ARMS = ["hynohop", "hynohop_fb", "hynohop_fb07"]
FB_ARMS = ["hynohop_fb", "hynohop_fb07"]
TWINS = {"hynohop_fb": "hynohop", "hynohop_fb07": "hynohop"}
SIGS = ("fL", "fR", "eL", "eR")
# echo gate: throughout vs 0.7-segs-only (gate closed for ALL of seg1)
EON = {"hynohop_fb": np.ones(WIN, bool)}
g07 = np.zeros(WIN, bool)
g07[:2000] = True
g07[4000:] = True
EON["hynohop_fb07"] = g07
assert EON["hynohop_fb"].all() and EON["hynohop_fb07"][:2000].all()
assert not EON["hynohop_fb07"][2000:4000].any() and EON["hynohop_fb07"][4000:].all()
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l59/l66/l77 verbatim) ----------
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
ANTAG = np.concatenate([PAIRS["Tr"][c] for c in SIGS])   # l66-verbatim
log(f"sub nodes {n:,} | edges {len(gsrc):,} | mech {len(mech)} | antag {len(ANTAG)}"
    f" | {time.time()-t0:.0f}s")

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- AMPA table (nohop schedule, identical for all arms) ----------
AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:                         # 500-on/400-off per 0.7 seg
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP                       # fast segment CONTINUOUS
for seg0, segend, f in SEGB:
    seg = AMPA[seg0:seg0 + SEG]
    if f == 0.7:
        assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
        assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
        assert (seg[1800:2000] == ENT_AMP).all()
    else:
        assert (AMPA[seg0:segend] == ENT_AMP).all()
DRIVE_ON = SETTLE + int((AMPA > 0).sum())
assert DRIVE_ON == 4800, DRIVE_ON
log("drive-on 48.0s all arms | tables asserted")


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


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


# ---------- rollouts (l59 step loop + l66 echo line, EON-gated) ----------
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
    mA = {a: np.zeros(WIN, np.float32) for a in FB_ARMS}

    def step_all(k):
        global settle_ph        # l66/l77 scope form (nonlocal = SyntaxError here)
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            ph_k = PHI[k]
        else:
            settle_ph += 2 * math.pi * 0.7 * DT
            ph_k = settle_ph
        sin_ph = math.sin(ph_k)
        for a in ARMS:
            drive = torch.sparse.mm(Wb, X[a]) * G + I
            if k < 0:
                amp_k = ENT_AMP
            else:
                amp_k = float(AMPA[k])
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            if a in FB_ARMS and k >= FB["delay"] and EON[a][k]:
                drive[mech, 0] += (FB["gfb"] * FB["sign"]
                                   * float(mA[a][k - FB["delay"]]))
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
            if a in FB_ARMS:
                mA[a][i] = X[a][ANTAG].mean()
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                          mm=mm, tr=tr, mA=mA)
    np.savez_compressed(
        "l82/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l82/raw_l82.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS},
    **{f"mA_{a}_{s}": res[str(s)]["mA"][a] for a in FB_ARMS for s in SEEDS})

# ---------------- anchors (enumerated keys ONLY) ----------------
z59 = np.load("l59/raw_l59.npz")
z77 = np.load("l77/raw_l77.npz")
z66 = np.load("l66/raw_l66.npz")
c0a, c0x = {}, {}
for s in ANCHOR_SEEDS:
    c0a[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hynohop"] - z59[f"mm_hynohop_{s}"][:WIN]).max())
    c0x[f"mm77_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hynohop_fb"] - z77[f"mm_hynohop_fb_{s}"][:WIN]).max())
    c0x[f"mm66_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hynohop_fb"] - z66[f"mm_g01_d05_m_{s}"][:WIN]).max())
    for c in SIGS:
        c0a[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hynohop"][c] - z59[f"{c}_hynohop_{s}"][:WIN]).max())
        c0x[f"{c}77_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hynohop_fb"][c]
            - z77[f"{c}_hynohop_fb_{s}"][:WIN]).max())
        c0x[f"{c}66_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hynohop_fb"][c]
            - z66[f"{c}_g01_d05_m_{s}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())
c0x_pass = all(v == 0.0 for v in c0x.values())

PAIRSETS = [("hynohop_fb", "hynohop"), ("hynohop_fb07", "hynohop"),
            ("hynohop_fb07", "hynohop_fb")]
first_div, dm, prefix = {}, {}, {}
for a, b in PAIRSETS:
    for s in SEEDS:
        m = res[str(s)]
        arrs = [np.abs(m["mm"][a] - m["mm"][b])] + [
            np.abs(m["tr"][a][c] - m["tr"][b][c]) for c in SIGS]
        diffs = np.concatenate(arrs)
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        first_div[f"{a}|{b}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{a}|{b}_{s}"] = round(float(diffs.max()), 5)
        prefix[f"{a}|{b}_{s}"] = float(max(
            x[:2001].max() for x in arrs))          # indices [0,2000] inclusive
c0p1 = all(prefix[f"hynohop_fb07|hynohop_fb_{s}"] == 0.0 for s in SEEDS)
c0p2 = (all(first_div[f"hynohop_fb|hynohop_{s}"] == 6 for s in SEEDS)
        and all(first_div[f"hynohop_fb07|hynohop_{s}"] == 6 for s in SEEDS)
        and all(first_div[f"hynohop_fb07|hynohop_fb_{s}"] == 2001 for s in SEEDS))
degenerate = all(
    dm[f"hynohop_fb07|hynohop_fb_{s}"] == 0.0 for s in SEEDS)
wired_dead = [k for k, v in dm.items() if v == 0.0]
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
log(f"C0a {c0a_pass} | C0x l77+l66 {c0x_pass} | C0P-1 prefix {c0p1}"
    f" | C0P-2 first_div {c0p2} | degenerate {degenerate} | C1 {c1}"
    f" | wired_dead {len(wired_dead)}")
if degenerate:
    log("DEGENERATE: fb07 bit-identical to fb — gate never closed; NO VERDICT")
log(f"first_div {sorted(set(first_div.values()))}")

# ---------------- analysis (l77 cells machinery verbatim) ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    fL, fR, eL, eR = (res[s]["tr"][a][c] for c in SIGS)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    SM[(a, s)] = (SL, SR)
    return SL, SR


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    if not q.any():
        return None
    return round(float(np.nanmedian(arr[TS[q]])), 3)


cells = {a: {str(s): {} for s in SEEDS} for a in ARMS}
for a in ARMS:
    for s in SEEDS:
        SL, SR = s_arrays(a, str(s))
        rows = []
        for si, (a0_, b0, tg) in enumerate(SEGB):
            lo, hi = a0_ + MEAS0, b0
            q = (TS >= lo) & (TS < hi)
            both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
            f_seg = dom_freq(res[str(s)]["mm"][a][a0_:b0])
            bl_errs, ttl = [], None
            for b in range(WIN // BLK):
                if a0_ <= b * BLK < b0 and b * BLK > a0_:
                    f_hat = dom_freq(res[str(s)]["mm"][a][b * BLK:(b + 1) * BLK])
                    e = abs(f_hat - tg)
                    bl_errs.append(e)
                    if ttl is None and e <= LOCK_TOL:
                        ttl = b * BLK - a0_
            rows.append(dict(
                duty=round(float(np.nanmean(both)), 3),
                SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                f=round(f_seg, 3),
                err=round(float(np.mean(bl_errs)), 4), ttl=ttl))
        qall = np.zeros(len(TS), bool)
        q07 = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            qall |= (TS >= a0_ + MEAS0) & (TS < b0)
            if f == 0.7:
                q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
        cells[a][str(s)] = dict(
            segs=rows,
            duty_all=round(float(np.nanmean(
                (SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
            duty_07=round(float(np.nanmean(
                (SL[TS[q07]] >= .25) & (SR[TS[q07]] >= .25))), 3))

# ---------------- budget (exact gate-mask echo mass) ----------------
on_steps = np.where(AMPA > 0)[0]
sin_on = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in on_steps])
entrain_mass = float(ENT_AMP * sin_on.sum())
budget = {}
for fb in FB_ARMS:
    ks = np.where(EON[fb])[0]
    ks = ks[ks >= FB["delay"]]
    em = [float(FB["gfb"] * res[str(s)]["mA"][fb][ks - FB["delay"]].sum())
          for s in SEEDS]
    budget[fb] = dict(echo_mass_mean=round(float(np.mean(em)), 4),
                      echo_mass_min=round(float(np.min(em)), 4),
                      echo_mass_max=round(float(np.max(em)), 4),
                      entrain_mass=round(entrain_mass, 1),
                      ratio_mean=round(float(np.mean(em)) / entrain_mass, 4))
log(f"R4 budget {json.dumps(budget)}")


# ---------------- registered reads ----------------
def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


dist = {}
for a in ARMS:
    per_seg = []
    for i in range(3):
        d = np.array([cells[a][str(s)]["segs"][i]["duty"] for s in SEEDS])
        e = np.array([cells[a][str(s)]["segs"][i]["err"] for s in SEEDS])
        per_seg.append(dict(
            mean=round(float(d.mean()), 3),
            k_ge_half=int((d >= .5).sum()),
            wilson=wilson(int((d >= .5).sum()), len(SEEDS)),
            err_le01=int((e <= .01).sum()),
            per_seed=[round(float(v), 3) for v in d]))
    d07 = np.array([cells[a][str(s)]["duty_07"] for s in SEEDS])
    k07 = int((d07 >= .5).sum())
    dist[a] = dict(segs=per_seg,
                   duty07_mean=round(float(d07.mean()), 3),
                   duty07_k=k07, duty07_wilson=wilson(k07, len(SEEDS)),
                   duty07_per_seed=[round(float(v), 3) for v in d07])

# R1 parity: fb07 seg0 == fb seg0 exactly (bit-identical window)
r1_pass = all(
    cells["hynohop_fb07"][str(s)]["segs"][0]["duty"]
    == cells["hynohop_fb"][str(s)]["segs"][0]["duty"] for s in SEEDS)

# R2 THE question: paired seg2 deltas
def paired(a, b, seg):
    d = np.array([cells[a][str(s)]["segs"][seg]["duty"]
                  - cells[b][str(s)]["segs"][seg]["duty"] for s in SEEDS])
    return dict(mean=round(float(d.mean()), 3),
                pos=int((d > 0).sum()), neg=int((d < 0).sum()),
                per_seed=[round(float(v), 3) for v in d])


r2 = dict(fb07_vs_fb=paired("hynohop_fb07", "hynohop_fb", 2),
          fb07_vs_never=paired("hynohop_fb07", "hynohop", 2))
d1 = r2["fb07_vs_fb"]["mean"]
d2 = r2["fb07_vs_never"]["mean"]
if -.05 <= d1 <= .05 and d2 >= .05:
    r2_verdict = "H-A WINDOW-LOCAL"
elif d1 <= -.10 and abs(d2) <= .05:
    r2_verdict = "H-B CONTINUITY-NEEDED"
else:
    r2_verdict = "MIXED"

# R3 fast-seg de-tox
r3 = dict(fb07_vs_never_seg1=paired("hynohop_fb07", "hynohop", 1),
          fb_vs_never_seg1=paired("hynohop_fb", "hynohop", 1),
          seg1_err_le01={a: dist[a]["segs"][1]["err_le01"] for a in ARMS})
r3_pass = (abs(r3["fb07_vs_never_seg1"]["mean"]) <= .05
           and r3["seg1_err_le01"]["hynohop_fb07"] == 16)

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, fb=FB, drive_on=DRIVE_ON,
                     nodes=int(n), edges=len(gsrc),
                     entrain_mass=round(entrain_mass, 1)),
           anchors=dict(c0a_pass=c0a_pass, c0x_pass=c0x_pass,
                        c0p1_prefix=c0p1, c0p2_first_div=bool(c0p2),
                        degenerate=bool(degenerate), c1=bool(c1),
                        wired_dead=wired_dead,
                        first_div=first_div, dm=dm, prefix=prefix),
           distributions=dist, budget=budget,
           reads=dict(r1_parity=bool(r1_pass), r2=r2, r2_verdict=r2_verdict,
                      r3=r3, r3_pass=bool(r3_pass),
                      r4_budget_ok=bool(
                          budget["hynohop_fb07"]["ratio_mean"]
                          < budget["hynohop_fb"]["ratio_mean"]),
                      r5_duty07={a: dict(k=dist[a]["duty07_k"],
                                         wilson=dist[a]["duty07_wilson"],
                                         mean=dist[a]["duty07_mean"])
                                 for a in ARMS}),
           cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS})
json.dump(out, open("l82/results_l82.json", "w"), indent=1)
log(f"R1 parity {r1_pass} | R2 {r2_verdict} "
    f"fb07-fb {d1} fb07-never {d2} | R3 {r3_pass} | R4 "
    f"{budget['hynohop_fb07']['ratio_mean']:.4f} < "
    f"{budget['hynohop_fb']['ratio_mean']:.4f}")
log(f"R5 duty07 k {json.dumps({a: dist[a]['duty07_k'] for a in ARMS})}"
    f" means {json.dumps({a: dist[a]['duty07_mean'] for a in ARMS})}")
log(f"seg means {json.dumps({a: [dist[a]['segs'][i]['mean'] for i in range(3)] for a in ARMS})}")
log(f"done {time.time()-t0:.0f}s -> l82/results_l82.json")
