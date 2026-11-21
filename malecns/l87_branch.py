"""L87: mid-seg-branch-library (LANE.md ideas 43). PREREG l87/PREREG.md FIRST.

Grow the fork library with mid-seg1 echo latches (K in {2500,3000,3500}) on both
trunks, re-run the L85 oracle/realizability protocol. Machinery l86_combo.py
verbatim + latch EON gates; CPU-only; raw npz checkpoint BEFORE analysis.
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
TRUNKS = ["hynohop", "hynohop_fb", "hybrid", "hybrid_fb"]
LATCH = {"nh_on2500": ("hynohop", 2500), "nh_on3000": ("hynohop", 3000),
         "nh_on3500": ("hynohop", 3500), "nh_off2500": ("hynohop_fb", 2500),
         "nh_off3000": ("hynohop_fb", 3000), "nh_off3500": ("hynohop_fb", 3500),
         "hy_on2500": ("hybrid", 2500), "hy_off2500": ("hybrid_fb", 2500)}
ARMS = TRUNKS + list(LATCH)
HOP_TRUNKS = {"hybrid", "hybrid_fb", "hy_on2500", "hy_off2500"}
ECHO_ARMS = [a for a in ARMS if a not in ("hynohop", "hybrid")]
SIGS = ("fL", "fR", "eL", "eR")
EON = {"hynohop_fb": np.ones(WIN, bool), "hybrid_fb": np.ones(WIN, bool)}
for name, (trunk, K) in LATCH.items():
    e = np.zeros(WIN, bool)
    if name.endswith("on" + str(K)):
        e[K:] = True
    else:
        e[:K] = True
    EON[name] = e
# write-time asserts (L82/L86 form): pre-latch EON == trunk state, post == latched
assert EON["hynohop_fb"].all() and EON["hybrid_fb"].all()
for name, (trunk, K) in LATCH.items():
    on = name.split("_")[1].startswith("on")
    trunk_eon = np.ones(WIN, bool) if trunk.endswith("_fb") else np.zeros(WIN, bool)
    want = EON[name]
    assert (want[:K] == trunk_eon[:K]).all(), name      # prefix == trunk gate
    assert (want[K:] == (np.ones(WIN - K, bool) if on
                         else np.zeros(WIN - K, bool))).all(), name
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l59/l66/l77/l82/l86 verbatim) ----------
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

# ---------- per-arm AMPA / HOPA tables ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
for a in ARMS:
    for seg0, _, _ in SEGB:
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA[a][2000:4000] = ENT_AMP
HOPA = {a: np.zeros(WIN, bool) for a in ARMS}
for o in TRANS:
    for a in HOP_TRUNKS:
        HOPA[a][o:o + HOP_VW] = True
assert all(np.array_equal(AMPA[a], AMPA["hynohop"]) for a in ARMS)
assert all(HOPA[a].sum() == (2 * HOP_VW if a in HOP_TRUNKS else 0) for a in ARMS)
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
assert all(v == 4800 for v in DRIVE_ON.values()), DRIVE_ON
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
    mA = {a: np.zeros(WIN, np.float32) for a in ECHO_ARMS}

    def step_all(k):
        global settle_ph
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
            if a in ECHO_ARMS and k >= FB["delay"] and EON[a][k]:
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
            if a in ECHO_ARMS:
                mA[a][i] = X[a][ANTAG].mean()
    res[str(seed)] = dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                          mm=mm, tr=tr, mA=mA)
    np.savez_compressed(
        "l87/raw_partial.npz",
        **{f"mm_{a}_{s}": res[str(s)]["mm"][a]
           for s in SEEDS if str(s) in res for a in ARMS},
        **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
           for s in SEEDS if str(s) in res for a in ARMS for c in SIGS})
    log(f"seed {seed} done {time.time()-t0:.0f}s")

log(f"runs done {time.time()-t0:.0f}s")
np.savez_compressed(
    "l87/raw_l87.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in SIGS},
    **{f"mA_{a}_{s}": res[str(s)]["mA"][a] for a in ECHO_ARMS for s in SEEDS})
log("raw_l87.npz checkpointed BEFORE analysis (crash => verdict re-derives)")

# ---------------- anchors A1-A4 (chain, vs stored raw) ----------------
z59 = np.load("l59/raw_l59.npz")
z77 = np.load("l77/raw_l77.npz")
chain = {"hynohop": z59, "hybrid": z59, "hynohop_fb": z77, "hybrid_fb": z77}
c0 = {}
for a, z in chain.items():
    for s in SEEDS:
        c0[f"mm|{a}_{s}"] = float(np.abs(
            res[str(s)]["mm"][a] - z[f"mm_{a}_{s}"][:WIN]).max())
        for c in SIGS:
            c0[f"{c}|{a}_{s}"] = float(np.abs(
                res[str(s)]["tr"][a][c] - z[f"{c}_{a}_{s}"][:WIN]).max())
chain_pass = all(v == 0.0 for v in c0.values())

# ---------------- anchor A5 (latch wiring: prefix + first-div) ----------------
a5_prefix, a5_fd, dm_lat = {}, {}, {}
for name, (trunk, K) in LATCH.items():
    for s in SEEDS:
        m = res[str(s)]
        arrs = [np.abs(m["mm"][name] - m["mm"][trunk])] + [
            np.abs(m["tr"][name][c] - m["tr"][trunk][c]) for c in SIGS]
        diffs = np.concatenate(arrs)
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        a5_fd[f"{name}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        a5_prefix[f"{name}_{s}"] = float(max(x[:K + 1].max() for x in arrs))
        dm_lat[f"{name}_{s}"] = round(float(diffs.max()), 5)
a5_prefix_pass = all(v == 0.0 for v in a5_prefix.values())
a5_fd_pass = all(a5_fd[f"{n}_{s}"] == LATCH[n][1] + 1
                 for n in LATCH for s in SEEDS)
degenerate = [n for n in LATCH if all(dm_lat[f"{n}_{s}"] == 0.0 for s in SEEDS)]
c1 = all(0.01 < res[str(s)]["af"][a] < 0.9 for s in SEEDS for a in ARMS)
log(f"A1-A4 chain {chain_pass} | A5 prefix {a5_prefix_pass} fd {a5_fd_pass}"
    f" | degenerate {degenerate} | C1 {c1}")
log(f"first_div set {sorted(set(a5_fd.values()))}")

# ---------------- analysis (l86 cells machinery verbatim) ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) not in SM:
        fL, fR, eL, eR = (res[s]["tr"][a][c] for c in SIGS)
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
            SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
        SM[(a, s)] = (SL, SR)
    return SM[(a, s)]


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    return round(float(np.nanmedian(arr[TS[q]])), 3) if q.any() else None


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

# ---------------- budget ----------------
on_steps = np.where(AMPA["hynohop"] > 0)[0]
sin_on = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in on_steps])
entrain_mass = float(ENT_AMP * sin_on.sum())
budget = {}
for fb_arm in ECHO_ARMS:
    ks = np.where(EON[fb_arm])[0]
    ks = ks[ks >= FB["delay"]]
    em = [float(FB["gfb"] * res[str(s)]["mA"][fb_arm][ks - FB["delay"]].sum())
          for s in SEEDS]
    budget[fb_arm] = dict(echo_mass_mean=round(float(np.mean(em)), 4),
                          entrain_mass=round(entrain_mass, 1),
                          ratio_mean=round(float(np.mean(em)) / entrain_mass, 4))
# A7 budget anchors (mass_table pinned)
mt = json.load(open("l85/mass_table.json"))
a7 = all(
    abs(budget[a]["echo_mass_mean"] - mt["budget"]["echo"][a]["mass"]) <= 0.1
    and abs(budget[a]["ratio_mean"] - mt["budget"]["echo"][a]["ratio"]) <= 0.001
    for a in ("hynohop_fb", "hybrid_fb"))
log(f"A7 budget {a7} | fb masses "
    f"{budget['hynohop_fb']['echo_mass_mean']}/{budget['hybrid_fb']['echo_mass_mean']}"
    f" | latch ratios "
    + " ".join(f"{a}={budget[a]['ratio_mean']}" for a in LATCH))

# ---------------- distributions ----------------
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

# A6 certification vs l85/mass_table.json on the 4 trunk arms
cert, cert_fail = True, []
for a in TRUNKS:
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
log(f"A6 certification {cert} {cert_fail if cert_fail else ''}")

# ---------------- R1: single-arm gates ----------------
gates = {}
for a in ARMS:
    d = dist[a]
    gates[a] = dict(
        g1=d["segs"][1]["err_le01"] == 16,
        g2a=d["duty07_k"] >= 15 and d["duty07_wilson"][0] >= 0.717,
        g3=d["segs"][1]["mean"] >= 0.358,
        g4=(DRIVE_ON[a] == 4800
            and (a not in ECHO_ARMS or budget[a]["ratio_mean"] <= 0.127)))
e1_arms = [a for a in LATCH if gates[a]["g2a"] and gates[a]["g3"]]

# ---------------- R2: oracle (existence; P1 lexicographic, P2 gate-aware) ----------------
def oracle(branches, label):
    per_d07 = {a: dist[a]["duty07_per_seed"] for a in branches}
    per_s1 = {a: dist[a]["segs"][1]["per_seed"] for a in branches}
    p1_pick, p2_pick = [], []
    for i in range(len(SEEDS)):
        p1_pick.append(max(branches, key=lambda a: (per_d07[a][i], per_s1[a][i])))
        ok = [a for a in branches if per_d07[a][i] >= .5] or branches
        p2_pick.append(max(ok, key=lambda a: per_s1[a][i]))
    out = {}
    for nm, pick in (("P1", p1_pick), ("P2", p2_pick)):
        d07s = [per_d07[pick[i]][i] for i in range(len(SEEDS))]
        s1s = [per_s1[pick[i]][i] for i in range(len(SEEDS))]
        k = int(sum(v >= .5 for v in d07s))
        out[nm] = dict(k=k, wilson=wilson(k, len(SEEDS)),
                       seg1_mean=round(float(np.mean(s1s)), 3),
                       picks=pick,
                       clears=(k >= 15 and float(np.mean(s1s)) >= .358))
    out["label"] = label
    return out


usable = [a for a in ARMS if gates[a]["g1"]]          # lock-clean only
O_MID = oracle(usable, "O-MIDSEG (in-run 12, lock-clean)")
stored_extra = [a for a in mt["table"] if a not in TRUNKS]
lib = {}
for a in ARMS:
    lib[a] = dict(d07=dist[a]["duty07_per_seed"], s1=dist[a]["segs"][1]["per_seed"],
                  err01=dist[a]["segs"][1]["err_le01"])
for a in stored_extra:
    row = mt["table"][a]
    lib[a] = dict(d07=row["per_seed"]["d07"], s1=row["per_seed"]["seg1"],
                  err01=row["segs"][1]["err_le01"] if "segs" in row else 16)
lib_clean = [a for a in lib if lib[a]["err01"] == 16]
# oracle over combined library using lib dict
def oracle_lib(branches):
    p1_pick, p2_pick = [], []
    for i in range(len(SEEDS)):
        p1_pick.append(max(branches, key=lambda a: (lib[a]["d07"][i], lib[a]["s1"][i])))
        ok = [a for a in branches if lib[a]["d07"][i] >= .5] or branches
        p2_pick.append(max(ok, key=lambda a: lib[a]["s1"][i]))
    out = {}
    for nm, pick in (("P1", p1_pick), ("P2", p2_pick)):
        d07s = [lib[pick[i]]["d07"][i] for i in range(len(SEEDS))]
        s1s = [lib[pick[i]]["s1"][i] for i in range(len(SEEDS))]
        k = int(sum(v >= .5 for v in d07s))
        out[nm] = dict(k=k, wilson=wilson(k, len(SEEDS)),
                       seg1_mean=round(float(np.mean(s1s)), 3), picks=pick,
                       clears=(k >= 15 and float(np.mean(s1s)) >= .358))
    return out


O_ALL = oracle_lib(lib_clean)
go1 = (O_MID["P1"]["clears"] or O_MID["P2"]["clears"])

# ---------------- R3: realizability (fork features at K=2500) ----------------
def spear(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def fork_feats(base):
    F = {"SL2500": [], "SR2500": [], "mm2500": []}
    for s in SEEDS:
        SL, SR = s_arrays(base, str(s))
        q = (TS >= 2300) & (TS < 2500)
        F["SL2500"].append(round(float(np.nanmedian(SL[TS[q]])), 3))
        F["SR2500"].append(round(float(np.nanmedian(SR[TS[q]])), 3))
        F["mm2500"].append(round(float(res[str(s)]["mm"][base][2400:2500].mean()), 5))
    return F


FORKS = {"nh_on2500": "hynohop", "nh_off2500": "hynohop_fb",
         "hy_on2500": "hybrid", "hy_off2500": "hybrid_fb"}
realiz, rules = {}, []
for latch_arm, base in FORKS.items():
    if latch_arm in degenerate:
        continue
    F = fork_feats(base)
    d_s1 = [cells[latch_arm][str(s)]["segs"][1]["duty"]
            - cells[base][str(s)]["segs"][1]["duty"] for s in SEEDS]
    d_d07 = [dist_cells - dist_base for dist_cells, dist_base in
             zip(dist[latch_arm]["duty07_per_seed"], dist[base]["duty07_per_seed"])]
    for f, v in F.items():
        realiz[f"{latch_arm}_ds1_vs_{f}"] = round(spear(v, d_s1), 3)
        realiz[f"{latch_arm}_dd07_vs_{f}"] = round(spear(v, d_d07), 3)
        # induced threshold rules (median split, both directions)
        thr = float(np.median(v))
        for direction in (">=", "<="):
            pick = []
            for i, s in enumerate(SEEDS):
                use_latch = (v[i] >= thr) if direction == ">=" else (v[i] < thr)
                pick.append(latch_arm if use_latch else base)
            d07s = [dist[pick[i]]["duty07_per_seed"][i] for i in range(len(SEEDS))]
            s1s = [dist[pick[i]]["segs"][1]["per_seed"][i] for i in range(len(SEEDS))]
            k = int(sum(x >= .5 for x in d07s))
            rules.append(dict(
                fork=latch_arm, feature=f, direction=direction,
                k=k, wilson=wilson(k, len(SEEDS)),
                seg1_mean=round(float(np.mean(s1s)), 3), picks=pick,
                clears=(k >= 15 and float(np.mean(s1s)) >= .358)))
go2 = any(r["clears"] for r in rules)

anchors_ok = dict(a1a4=chain_pass, a5_prefix=a5_prefix_pass, a5_fd=a5_fd_pass,
                  a6=cert, a7=a7, c1=c1)
log(f"R1 gates {json.dumps(gates)}")
log(f"E1 pareto movers {e1_arms}")
log(f"O_MID {json.dumps({k: O_MID[k] for k in ('P1','P2')})}")
log(f"O_ALL {json.dumps(O_ALL)}")
log(f"GO1 {go1} | realizability {json.dumps(realiz)}")
best_rules = sorted(rules, key=lambda r: (r["clears"], r["k"],
                                          r["seg1_mean"]), reverse=True)[:4]
log(f"best rules {json.dumps(best_rules)}")
log(f"GO2 {go2}")

if degenerate:
    verdict = f"DEGENERATE latch arms {degenerate} (excluded, disclosed)"
elif not all([chain_pass, a5_prefix_pass, a5_fd_pass, cert, a7, c1]):
    verdict = "ANCHOR-FAIL (addendum before any read)"
elif e1_arms:
    verdict = f"E1 PARETO MOVER {e1_arms} (single new arm clears G2a+G3)"
elif go1 and go2:
    verdict = "GO: library realizable at the registered rule class"
elif go1 and not go2:
    verdict = ("NO-GO: oracle-only mass (GO1 yes, GO2 no) — mid-seg branches "
               "not realizable; C4b echo lever stands, C4c stays diagnostic")
else:
    verdict = "NO-GO at existence (GO1 fails): library cannot clear even with "
    "seed knowledge"

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, latch={k: list(v) for k, v in LATCH.items()},
                     fb=FB, drive_on=4800, nodes=int(n), edges=len(gsrc),
                     entrain_mass=round(entrain_mass, 1)),
           anchors=anchors_ok, first_div=a5_fd, dm=dm_lat, degenerate=degenerate,
           distributions=dist, budget=budget, gates=gates,
           oracle_mid=O_MID, oracle_all=O_ALL, realizability=realiz,
           rules=rules, go=dict(go1=go1, go2=go2), verdict=verdict,
           cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS})
json.dump(out, open("l87/results_l87.json", "w"), indent=1)
log(f"VERDICT {verdict}")
log(f"done {time.time()-t0:.0f}s -> l87/results_l87.json")
