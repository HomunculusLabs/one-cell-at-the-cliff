"""L86: hybrid-echo-combo (LANE.md ideas 43). PREREG l86/PREREG.md FIRST.

L85's two best structure facts in one arm: hop trunk x seg0-only echo.
Arms (all hybrid trunk, HOPA verbatim l59/l77): hybrid (anchor, no echo) /
hybrid_fb (anchor, echo throughout) / hybrid_e0 (NEW: EON [0,2000) only).
Machinery l82_hold.py verbatim + l77 hop lines; CPU-only; raw npz checkpoint
BEFORE analysis; no live changes.
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
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
HOP_AMP, HOP_VW = 0.5, 40
TRANS = [2000, 4000]
LOCK_TOL = 0.10
FB = dict(gfb=.1, delay=5, sign=-1.0)          # l66 content cell verbatim
ARMS = ["hybrid", "hybrid_fb", "hybrid_e0"]
FB_ARMS = ["hybrid_fb", "hybrid_e0"]
SIGS = ("fL", "fR", "eL", "eR")
# echo gates: fb throughout; e0 seg0-only (gate closed for ALL of seg1+seg2)
EON = {"hybrid_fb": np.ones(WIN, bool)}
g0 = np.zeros(WIN, bool)
g0[:2000] = True
EON["hybrid_e0"] = g0
assert EON["hybrid_fb"].all()
assert EON["hybrid_e0"][:2000].all() and not EON["hybrid_e0"][2000:].any()
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l59/l66/l77/l82 verbatim) ----------
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

# ---------- per-arm AMPA / HOPA tables (l59/l77 write-time asserts) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
for a in ARMS:                                  # hybrid AMPA for every arm
    for seg0, _, _ in SEGB:
        c = 0                                   # 500-on/400-off per 0.7 seg
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA[a][2000:4000] = ENT_AMP                # fast segment CONTINUOUS
HOPA = {a: np.zeros(WIN, bool) for a in ARMS}
for o in TRANS:                                 # hop trunk for ALL arms
    for a in ARMS:
        HOPA[a][o:o + HOP_VW] = True
assert all(np.array_equal(AMPA[a], AMPA["hybrid"]) for a in ARMS)
for seg0, segend, f in SEGB:
    seg = AMPA["hybrid"][seg0:seg0 + SEG]
    if f == 0.7:
        assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
        assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
        assert (seg[1800:2000] == ENT_AMP).all()
    else:
        assert (AMPA["hybrid"][seg0:segend] == ENT_AMP).all()
assert all(HOPA[a].sum() == 2 * HOP_VW for a in ARMS)
assert all(np.array_equal(HOPA[a], HOPA["hybrid"]) for a in ARMS)
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
assert all(DRIVE_ON[a] == 4800 for a in ARMS), DRIVE_ON
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


# ---------- rollouts (l59 step order + l66 echo line, EON-gated) ----------
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
        global settle_ph        # l66/l77/l82 scope form
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
                amp_k = float(AMPA[a][k])
            if amp_k > 0.0:
                drive[mech, 0] = drive[mech, 0] + amp_k * (0.5 + 0.5 * sin_ph)
            if k >= 0 and HOPA[a][k]:
                drive[hopL, 0] += HOP_AMP
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
        "l86/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l86/raw_l86.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS},
    **{f"mA_{a}_{s}": res[str(s)]["mA"][a] for a in FB_ARMS for s in SEEDS})
log("raw_l86.npz checkpointed BEFORE analysis (crash => verdict re-derives)")

# ---------------- anchors (enumerated keys ONLY) ----------------
z59 = np.load("l59/raw_l59.npz")
z77 = np.load("l77/raw_l77.npz")
c0a, c0x = {}, {}
for s in SEEDS:
    c0a[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hybrid"] - z59[f"mm_hybrid_{s}"][:WIN]).max())
    c0x[f"mm77_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hybrid_fb"] - z77[f"mm_hybrid_fb_{s}"][:WIN]).max())
    for c in SIGS:
        c0a[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hybrid"][c] - z59[f"{c}_hybrid_{s}"][:WIN]).max())
        c0x[f"{c}77_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hybrid_fb"][c]
            - z77[f"{c}_hybrid_fb_{s}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())
c0x_pass = all(v == 0.0 for v in c0x.values())

PAIRSETS = [("hybrid_fb", "hybrid"), ("hybrid_e0", "hybrid"),
            ("hybrid_e0", "hybrid_fb")]
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
        pre = float(max(x[:2001].max() for x in arrs))   # idx [0,2000] incl
        prefix[f"{a}|{b}_{s}"] = pre
a3_prefix = all(prefix[f"hybrid_e0|hybrid_fb_{s}"] == 0.0 for s in SEEDS)
a3_fd = all(first_div[f"hybrid_e0|hybrid_fb_{s}"] == 2001 for s in SEEDS)
a4_fd = (all(first_div[f"hybrid_fb|hybrid_{s}"] == 6 for s in SEEDS)
         and all(first_div[f"hybrid_e0|hybrid_{s}"] == 6 for s in SEEDS))
degenerate = all(dm[f"hybrid_e0|hybrid_fb_{s}"] == 0.0 for s in SEEDS)
wired_dead = [k for k, v in dm.items() if v == 0.0]
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
log(f"A1 {c0a_pass} | A2 {c0x_pass} | A3 prefix {a3_prefix} fd {a3_fd}"
    f" | A4 fd {a4_fd} | degenerate {degenerate} | C1 {c1}"
    f" | wired_dead {len(wired_dead)}")
log(f"first_div {sorted(set(first_div.values()))}")
if degenerate:
    log("DEGENERATE: hybrid_e0 bit-identical to hybrid_fb — EON never applied;"
        " NO VERDICT")

# ---------------- analysis (l82 cells machinery verbatim) ----------------
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

# ---------------- budget (exact gate-mask echo mass, l82 form) ----------------
on_steps = np.where(AMPA["hybrid"] > 0)[0]
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
log(f"budget {json.dumps(budget)}")

# A5 budget anchors (l85-pinned)
a5 = (abs(budget["hybrid_fb"]["echo_mass_mean"] - 85.6) <= 0.1
      and abs(budget["hybrid_fb"]["ratio_mean"] - 0.1283) <= 0.001
      and abs(budget["hybrid_e0"]["echo_mass_mean"] - 28.8) <= 0.1
      and 0.0420 <= budget["hybrid_e0"]["ratio_mean"] <= 0.0445)

# ---------------- distributions (l82 dist form) ----------------
def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return [round(c - hw, 3), round(c + hw, 3)]   # LIST (json-comparable)


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

# A6 certification vs l85/mass_table.json (L85 across-run form)
mt = json.load(open("l85/mass_table.json"))
cert, cert_fail = True, []
for a in ("hybrid", "hybrid_fb"):
    row = mt["table"][a]
    mine = dist[a]
    checks = {
        f"{a}.seg_means": [mine["segs"][i]["mean"] for i in range(3)],
        f"{a}.seg_k": [mine["segs"][i]["k_ge_half"] for i in range(3)],
        f"{a}.seg_wilson": [mine["segs"][i]["wilson"] for i in range(3)],
        f"{a}.seg_err_le01": [mine["segs"][i]["err_le01"] for i in range(3)],
        f"{a}.duty07_mean": mine["duty07_mean"],
        f"{a}.duty07_k": mine["duty07_k"],
        f"{a}.duty07_wilson": mine["duty07_wilson"],
        f"{a}.per_seed_seg1":
            [cells[a][str(s)]["segs"][1]["duty"] for s in SEEDS],
        f"{a}.per_seed_d07": mine["duty07_per_seed"],
    }
    want = {
        f"{a}.seg_means": [row["segs"][i]["mean"] for i in range(3)],
        f"{a}.seg_k": [row["segs"][i]["k"] for i in range(3)],
        f"{a}.seg_wilson": [row["segs"][i]["wilson"] for i in range(3)],
        f"{a}.seg_err_le01": [row["segs"][i]["err_le01"] for i in range(3)],
        f"{a}.duty07_mean": row["duty07_mean"],
        f"{a}.duty07_k": row["duty07_k"],
        f"{a}.duty07_wilson": row["duty07_wilson"],
        f"{a}.per_seed_seg1": row["per_seed"]["seg1"],
        f"{a}.per_seed_d07": row["per_seed"]["d07"],
    }
    for key in checks:
        if checks[key] != want[key]:
            cert = False
            cert_fail.append((key, checks[key], want[key]))
log(f"A5 budget {a5} | A6 certification {cert} {cert_fail if cert_fail else ''}")

# A7 parity: hybrid_e0 seg0 cells == hybrid_fb seg0 cells per seed
a7 = all(
    cells["hybrid_e0"][str(s)]["segs"][0][k]
    == cells["hybrid_fb"][str(s)]["segs"][0][k]
    for s in SEEDS for k in ("duty", "SL", "SR", "f", "err"))
log(f"A7 seg0 parity {a7}")

# ---------------- registered reads (GATE-L85 rows, SEPARATE axes) ----------------
e0 = dist["hybrid_e0"]
g1 = e0["segs"][1]["err_le01"] == 16
g2a = e0["duty07_k"] >= 15 and e0["duty07_wilson"][0] >= 0.717
g2b = e0["duty07_k"] >= 15 and budget["hybrid_e0"]["ratio_mean"] <= 0.0431
g3 = e0["segs"][1]["mean"] >= 0.358
g4 = all(v == 4800 for v in DRIVE_ON.values()) and \
    budget["hybrid_e0"]["ratio_mean"] <= 0.127


def paired(a, b, seg):
    d = np.array([cells[a][str(s)]["segs"][seg]["duty"]
                  - cells[b][str(s)]["segs"][seg]["duty"] for s in SEEDS])
    return dict(mean=round(float(d.mean()), 3),
                pos=int((d > 0).sum()), neg=int((d < 0).sum()),
                per_seed=[round(float(v), 3) for v in d])


pairs = dict(e0_vs_hybrid_seg1=paired("hybrid_e0", "hybrid", 1),
             e0_vs_fb_seg1=paired("hybrid_e0", "hybrid_fb", 1),
             e0_vs_hybrid_seg2=paired("hybrid_e0", "hybrid", 2),
             e0_vs_fb_seg2=paired("hybrid_e0", "hybrid_fb", 2),
             e0_vs_hybrid_d07=dict(
                 per_seed=[round(a_ - b_, 3) for a_, b_ in
                           zip(dist["hybrid_e0"]["duty07_per_seed"],
                               dist["hybrid"]["duty07_per_seed"])]))

anchors_ok = dict(a1=c0a_pass, a2=c0x_pass, a3_prefix=bool(a3_prefix),
                  a3_fd=bool(a3_fd), a4_fd=bool(a4_fd), a5=bool(a5),
                  a6=bool(cert), a7=bool(a7), c1=bool(c1),
                  degenerate=bool(degenerate))
if degenerate:
    verdict = "DEGENERATE-WIRING (no verdict)"
elif not all([c0a_pass, c0x_pass, a3_prefix, a3_fd, a4_fd, a5, cert, a7, c1]):
    verdict = "ANCHOR-FAIL (addendum before any read)"
elif g2a and g3:
    verdict = "E1 PARETO MOVER (k>=15 AND seg1>=.358 — no stored arm reaches)"
elif g3 is False and e0["segs"][1]["mean"] < 0.358:
    axis = ("G2a PASS + G3 FAIL = always-fb mimic shape (axis split named)"
            if g2a else "G2a FAIL too")
    verdict = f"E2 TAX LAW WINS ({axis})"
else:
    verdict = "MIXED (g3 boundary; addendum)"

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, fb=FB, drive_on=DRIVE_ON,
                     nodes=int(n), edges=len(gsrc),
                     entrain_mass=round(entrain_mass, 1), hop_amp=HOP_AMP,
                     hop_vw=HOP_VW, trans=TRANS),
           anchors=anchors_ok,
           first_div=first_div, dm=dm, prefix=prefix,
           wired_dead=wired_dead,
           distributions=dist, budget=budget,
           gates=dict(g1=bool(g1), g2a=bool(g2a), g2b=bool(g2b),
                      g3=bool(g3), g4=bool(g4)),
           pairs=pairs,
           verdict=verdict,
           cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS})
json.dump(out, open("l86/results_l86.json", "w"), indent=1)
log(f"segs means {json.dumps({a: [dist[a]['segs'][i]['mean'] for i in range(3)] for a in ARMS})}")
log(f"d07 k {json.dumps({a: dist[a]['duty07_k'] for a in ARMS})}"
    f" wilson {json.dumps({a: dist[a]['duty07_wilson'] for a in ARMS})}")
log(f"gates G1 {g1} G2a {g2a} G2b {g2b} G3 {g3} G4 {g4}")
log(f"VERDICT {verdict}")
log(f"done {time.time()-t0:.0f}s -> l86/results_l86.json")
