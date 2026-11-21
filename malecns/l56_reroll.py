"""L56: seg2-reroll-law (LANE.md ideas-27).

Is "any hop re-rolls the downstream attractor lottery" a LAW (any volley at
any time = pure re-draw, mean-neutral) or are TRANSITIONS special? Volley
placement sweep on the l55 hybrid schedule: nohop / hop@4000 (transition,
chain anchors vs l55) / v43 / v46 / v49 (mid-seg2, drive-on/off/re-on
coincidence). PREREG l56/PREREG.md written first. Raw npz checkpoint BEFORE
analysis. CPU-only; P1-labeled; no live changes.
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
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05      # l32 arm-A frozen
ENT_AMP = 0.3
HOP_AMP, HOP_VW = 0.5, 40
ARMS = ["nohop", "hop4k", "v43", "v46", "v49"]
VOLLEY_AT = {"hop4k": 4000, "v43": 4300, "v46": 4600, "v49": 4900}
DM_PAIRS = [(a, "nohop") for a in ("hop4k", "v43", "v46", "v49")]
LOCK_TOL = 0.10
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------- stage A: substrate (l32/l34/l39/l50/l51/l55 verbatim) ----------
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
lnt = nt_names[keep]
assert n == 21516, n
assert len(gsrc) == 2977920, len(gsrc)
log(f"sub nodes {n:,} | edges {len(gsrc):,} | {time.time()-t0:.0f}s")

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
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
hopL = np.where((ltyp == "DNge046") & (lside == "L"))[0]
assert len(hopL) == 2, len(hopL)
log(f"mech {len(mech)} | 046L {len(hopL)}")

# ---------- global phase (l39 convention) ----------
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------- per-arm AMPA / HOPA tables (write-time asserted) ----------
AMPA = {a: np.zeros(WIN, np.float64) for a in ARMS}
for a in ARMS:                                  # hybrid AMPA for every arm
    for seg0, _, _ in SEGB:
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA[a][2000:4000] = ENT_AMP                # fast segment CONTINUOUS
HOPA = {a: np.zeros(WIN, bool) for a in ARMS}
for a, at in VOLLEY_AT.items():
    HOPA[a][at:at + HOP_VW] = True

assert all(np.array_equal(AMPA[a], AMPA["nohop"]) for a in ARMS)
for seg0, segend, f in SEGB:
    seg = AMPA["nohop"][seg0:seg0 + SEG]
    if f == 0.7:
        assert (seg[:500] == ENT_AMP).all() and (seg[500:900] == 0).all()
        assert (seg[900:1400] == ENT_AMP).all() and (seg[1400:1800] == 0).all()
        assert (seg[1800:2000] == ENT_AMP).all()
    else:
        assert (AMPA["nohop"][seg0:segend] == ENT_AMP).all()
assert not HOPA["nohop"].any()
for a, at in VOLLEY_AT.items():
    assert HOPA[a].sum() == HOP_VW and HOPA[a][:at].sum() == 0 \
        and HOPA[a][at + HOP_VW:].sum() == 0, a
assert [HOPA[a].argmax() for a in ARMS[1:]] == [4000, 4300, 4600, 4900]
DRIVE_ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
assert all(DRIVE_ON[a] == 4800 for a in ARMS), DRIVE_ON
log("drive-on 48.0s all arms | volley tables asserted")


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
    settle_ph = 0.0
    SIGS = ("fL", "fR", "eL", "eR")
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {c: np.zeros(WIN, np.float32) for c in SIGS} for a in ARMS}
    dm = {p: dict(first_div=-1, vmax=0.0) for p in DM_PAIRS}
    hop_win = np.zeros(WIN, bool)                # dm probe windows (union)
    for at in VOLLEY_AT.values():
        hop_win[at:at + HOP_VW] = True

    def step_all(k):
        nz = NOISE * torch.randn(n, 1, generator=gen)
        if k >= 0:
            ph_k = PHI[k]
        else:
            nonlocal settle_ph
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
        if i >= 1:
            for p in DM_PAIRS:
                d = float((X[p[0]] - X[p[1]]).abs().max())
                if hop_win[i] and d > dm[p]["vmax"]:
                    dm[p]["vmax"] = d
                if d > 1e-6 and dm[p]["first_div"] < 0:
                    dm[p]["first_div"] = i
    return dict(af={a: float((X[a] > 0.05).float().mean()) for a in ARMS},
                dm=dm, mm=mm, tr=tr)


res = {str(s): run_seed(s) for s in SEEDS}
log(f"runs done {time.time()-t0:.0f}s")

# raw checkpoint BEFORE analysis (L45a lesson)
np.savez_compressed(
    "l56/raw_l56.npz",
    **{f"mm_{a}_{s}": res[str(s)]["mm"][a] for a in ARMS for s in SEEDS},
    **{f"{c}_{a}_{s}": res[str(s)]["tr"][a][c]
       for a in ARMS for s in SEEDS for c in ("fL", "fR", "eL", "eR")})

# ---------------- C0 anchors vs l55 ----------------
z55 = np.load("l55/raw_l55.npz")
c0 = {}
for a, l55a in (("nohop", "hynohop"), ("hop4k", "hop4k")):
    c0[f"{a}_vs_l55"] = max(float(np.abs(res[str(s)]["mm"][a][:WIN]
                                         - z55[f"mm_{l55a}_{s}"][:WIN]).max())
                            for s in SEEDS)
    c0[f"{a}_tr_vs_l55"] = max(
        float(np.abs(res[str(s)]["tr"][a][c][:WIN]
                     - z55[f"{c}_{l55a}_{s}"][:WIN]).max())
        for s in SEEDS for c in ("fL", "fR", "eL", "eR"))
fd = {}
for a, want in VOLLEY_AT.items():
    fd[a] = [res[str(s)]["dm"][(a, "nohop")]["first_div"] for s in SEEDS]
    assert fd[a] == [want] * 3, (a, fd[a])
c0["first_div"] = {a: fd[a] for a in fd}
c0_pass = all(v == 0.0 for v in c0.values() if isinstance(v, float))

# ---------------- C1 wiring ----------------
vm = {a: [round(res[str(s)]["dm"][(a, "nohop")]["vmax"], 4) for s in SEEDS]
      for a in VOLLEY_AT}
c1 = dict(af_ok=all(0.01 < res[str(s)]["af"][a] < 0.9
                    for s in SEEDS for a in ARMS), volley_max=vm)
c1["pass_"] = (c1["af_ok"] and all(v > 1e-6 for a in VOLLEY_AT for v in vm[a]))

# ---------------- analysis (l55-verbatim S windows) ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    fL, fR, eL, eR = (res[str(s)]["tr"][a][c] for c in ("fL", "fR", "eL", "eR"))
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


def ssign(s):
    return "+" if s > 0.15 else ("-" if s < -0.15 else "0")


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


def label_of(a, s, lo, hi):
    SL, SR = s_arrays(a, s)
    mml = res[str(s)]["mm"][a]
    r_mm, f = rhythm2(mml[lo:hi])
    sl, sr = wmed(lo, hi, SL), wmed(lo, hi, SR)
    return dict(label=f"{fband(r_mm, f)}|{ssign(sl)}{ssign(sr)}",
                f=round(f, 3), r=round(r_mm, 1), SL=sl, SR=sr)


def duty_of(a, s, lo, hi):
    SL, SR = s_arrays(a, s)
    q = (TS >= lo) & (TS < hi)
    both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
    return round(float(np.nanmean(both)), 3)


SEG2 = (4000, 6000)
rows = {}
for a in ARMS:
    for s in SEEDS:
        lab_full = label_of(a, str(s), SEG2[0] + MEAS0, SEG2[1])   # l55 window
        d_full = duty_of(a, str(s), SEG2[0] + MEAS0, SEG2[1])
        cell = dict(seg2_duty=d_full, seg2_label=lab_full["label"],
                    SL=lab_full["SL"], SR=lab_full["SR"], f=lab_full["f"])
        if a in VOLLEY_AT and VOLLEY_AT[a] > 4000:      # mid-seg2 arms
            at = VOLLEY_AT[a]
            pre = label_of(a, str(s), SEG2[0] + 50, at)
            post = label_of(a, str(s), at + HOP_VW + 100, SEG2[1])
            cell.update(pre_label=pre["label"], post_label=post["label"],
                        pre_duty=duty_of(a, str(s), SEG2[0] + 50, at),
                        post_duty=duty_of(a, str(s), at + HOP_VW + 100, SEG2[1]),
                        pre_SL=pre["SL"], pre_SR=pre["SR"],
                        post_SL=post["SL"], post_SR=post["SR"])
        rows[f"{a}|{s}"] = cell

# pooled duty (l55-verbatim, all segs, MEAS0-relative) for continuity
qall = np.zeros(len(TS), bool)
for a0_, b0, _ in SEGB:
    qall |= (TS >= a0_ + MEAS0) & (TS < b0)


def pooled_of(a, s):
    SL, SR = s_arrays(a, s)
    both = (SL[TS[qall]] >= 0.25) & (SR[TS[qall]] >= 0.25)
    return round(float(np.nanmean(both)), 3)


pooled = {a: round(float(np.mean([pooled_of(a, str(s)) for s in SEEDS])), 3)
          for a in ARMS}

# ---------------- P1a: transition-specialness ----------------
seg2 = {a: [rows[f"{a}|{s}"]["seg2_duty"] for s in SEEDS] for a in ARMS}
mean46, mean4k = float(np.mean(seg2["v46"])), float(np.mean(seg2["hop4k"]))
p1a_diff = round(abs(mean46 - mean4k), 3)
per_seed_dir = [seg2["v46"][i] - seg2["hop4k"][i] for i in range(3)]
same_dir_all = all(d > 0.15 for d in per_seed_dir) or \
    all(d < -0.15 for d in per_seed_dir)
p1a = bool(p1a_diff < 0.10 and not same_dir_all)

# ---------------- P1b: mid-seg2 re-draw ----------------
redraw_cells, absorbed_cells = [], []
for a in ("v43", "v46", "v49"):
    for s in SEEDS:
        c = rows[f"{a}|{s}"]
        if c["post_label"] != c["pre_label"]:
            redraw_cells.append(f"{a}|{s}: {c['pre_label']}->{c['post_label']}")
        else:
            absorbed_cells.append(f"{a}|{s}: {c['pre_label']}")
p1b_redraw_n = len(redraw_cells)
p1b = bool(redraw_cells)            # law expects >= 1 re-draw cell

# ---------------- P1c: distribution unchanged (small-n, descriptive) ------
volley_cells = [rows[f"{a}|{s}"] for a in VOLLEY_AT for s in SEEDS]
ref_cells = [rows[f"{a}|{s}"] for a in ("nohop", "hop4k") for s in SEEDS]


def sign_counts(cells):
    sl = [c["seg2_label"].split("|")[1][0] for c in cells]
    sr = [c["seg2_label"].split("|")[1][1] for c in cells]
    return {"L+": sl.count("+"), "L0": sl.count("0"), "L-": sl.count("-"),
            "R+": sr.count("+"), "R0": sr.count("0"), "R-": sr.count("-")}


volley_sc, ref_sc = sign_counts(volley_cells), sign_counts(ref_cells)
chi2 = {}
for ax in ("L", "R"):
    obs = np.array([volley_sc[f"{ax}+"], volley_sc[f"{ax}0"],
                    volley_sc[f"{ax}-"]], float)
    exp = np.array([ref_sc[f"{ax}+"], ref_sc[f"{ax}0"], ref_sc[f"{ax}-"]], float)
    exp = exp / exp.sum() * obs.sum()
    keepm = exp > 0
    chi2[ax] = round(float(((obs[keepm] - exp[keepm]) ** 2 / exp[keepm]).sum()), 2)
census_sc = {"L+": 11, "L0": 4, "L-": 1, "R+": 0, "R0": 8, "R-": 9}  # l45b free

# ---------------- P2: miss decomposition ----------------
misses = {k: dict(duty=v["seg2_duty"], SL=v["SL"], SR=v["SR"],
                  label=v["seg2_label"])
          for k, v in rows.items() if v["seg2_duty"] < 0.25}

# ---------------- P3: mean-neutrality ----------------
volley_means = {a: round(float(np.mean(seg2[a])), 3) for a in VOLLEY_AT}
grand_volley = round(float(np.mean([seg2[a] for a in VOLLEY_AT])), 3)
nohop_mean = round(float(np.mean(seg2["nohop"])), 3)
p3 = bool(abs(grand_volley - nohop_mean) <= 0.10)

# ---------------- verdict ----------------
if p1a and p1b:
    verdict = (f"LAW-SUPPORTED: volley TIME does not own the re-roll (v46 vs "
               f"hop4k seg2 mean diff {p1a_diff}), mid-seg2 volleys re-draw too "
               f"({p1b_redraw_n} cells); distribution counts reported small-n")
elif not p1b:
    verdict = ("TRANSITIONS-SPECIAL: mid-seg2 volleys are absorbed (post label "
               "== pre label in all cells) while the boundary hop re-rolls")
else:
    verdict = (f"MIXED: re-draw happens mid-seg2 ({p1b_redraw_n} cells) but "
               f"placement matters (v46 vs hop4k mean diff {p1a_diff})")

dump = dict(meta=dict(win=WIN, seeds=SEEDS, volley_at=VOLLEY_AT,
                      hop_amp=HOP_AMP, hop_vw=HOP_VW, ent_amp=ENT_AMP,
                      drive_on=4800, nodes=int(n), edges=len(gsrc)),
            C0=c0, C0_pass=bool(c0_pass), C1=c1,
            seg2=seg2, rows=rows, pooled=pooled,
            P1a=dict(diff=p1a_diff, per_seed=[round(d, 3) for d in per_seed_dir],
                     pass_=p1a),
            P1b=dict(redraw=redraw_cells, absorbed=absorbed_cells,
                     n_redraw=p1b_redraw_n, pass_=p1b),
            P1c=dict(volley_signs=volley_sc, ref_signs=ref_sc,
                     chi2_vs_ref=chi2, l45b_free_census=census_sc,
                     note="n=12 volley / n=6 ref cells; descriptive only; "
                          "free-cord marginals confounded by chopped-0.7 drive"),
            P2_misses=misses,
            P3=dict(volley_means=volley_means, grand=grand_volley,
                    nohop=nohop_mean, pass_=p3),
            verdict=verdict)
log("VERDICT " + json.dumps(dump)[:2400])
np.savez_compressed("l56/traces_l56.npz",
                    **{f"SL_{a}_{s}": s_arrays(a, str(s))[0]
                       for a in ARMS for s in SEEDS},
                    **{f"SR_{a}_{s}": s_arrays(a, str(s))[1]
                       for a in ARMS for s in SEEDS})
json.dump(dump, open("l56/results_l56.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l56/results_l56.json")
