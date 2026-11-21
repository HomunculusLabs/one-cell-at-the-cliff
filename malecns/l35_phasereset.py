"""L35: phase-reset-volley — can a BRIEF DN volley re-time the L32 self-rhythmic
gait without breaking it (phase response curve), or is phase-reset another
dead control lever at this fidelity (L33 tonic bias was)?

L34 entrained the rhythm with CONTINUOUS drive; L24 turned with TRANSIENT
volleys in the non-rhythmic regime. The missing primitive is the one-shot:
a 250 ms bilateral DNg95 volley (or a DNg100 drive pulse) delivered at a
KNOWN phase of the established rhythm -> does the rhythm's PHASE shift by a
stimulus-locked amount (PRC) and does the gait survive (S(Tr), ratio)?

Paired-noise design: control + volley runs share the generator seed, so
pre-volley dynamics are bit-identical. Instrument: HETERODYNE PHASE (L34
phase_R form; PREREG amendment 4 — the mm peak train is quasi-periodic and
cannot carry a peak-train PRC). Claim levels in l35/PREREG.md (C0..C4).
P1-labeled, CPU-only, no live changes.
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
WIN = 6000           # 60 s
MEAS0 = 1500         # measurement window (last 45 s), L34 form
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05          # l32 arm-A frozen, verbatim
ANCHOR = {11: 0.800, 22: 1.444, 33: 1.422}   # l34 results_l34.json (45 s window)
VOLLEY_NEAR = 3500    # place volley onset near this step
VSTEPS = 25           # 250 ms brief volley
DUR_ARM = 100         # ~1 cycle at 1.0 Hz duration arm
AMPS_V = [0.05, 0.15]
NBINS = 8
SHAM_DRAWS = 5
POST_S = 15.0         # dphi window length (s) after volley end + one period
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------- stage A: subnetwork (l32/l33/l34 verbatim) ----------
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
dng95 = np.where(ltyp == "DNg95")[0]
assert len(dng95) >= 1, "DNg95 cells"
dn_pool = np.where(lsup == "descending_neuron")[0]
assert len(dn_pool) > 50
log(f"DNg95 cells {len(dng95)} | DN pool {len(dn_pool)}")


# ---------- rollout (l34 step, + optional volley on trace index) ----------
def run(seed, vcells=None, vamp=0.0, k0=None, vsteps=VSTEPS):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D
    Iv = None
    if vcells is not None and vamp > 0:
        Iv = torch.zeros(n, 1)
        Iv[vcells] = vamp

    def step(cur, k):
        drive = torch.sparse.mm(Wb, cur) * G + I
        kk = k - SETTLE                      # trace index (amendment 3a)
        if Iv is not None and k0 <= kk < k0 + vsteps:
            drive = drive + Iv
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for k in range(SETTLE):
        X = step(X, k)
    af = float((X > 0.05).float().mean())
    assert 0.01 < af < 0.9, f"op-point {af:.3f}"
    assert not torch.isnan(X).any(), "NaN"
    flx = np.zeros(WIN, np.float32)
    ext = np.zeros(WIN, np.float32)
    mm = np.zeros(WIN, np.float32)
    for i in range(WIN):
        X = step(X, SETTLE + i)
        flx[i] = X[PAIRS["Tr"]["fL"]].mean() + X[PAIRS["Tr"]["fR"]].mean()
        ext[i] = X[PAIRS["Tr"]["eL"]].mean() + X[PAIRS["Tr"]["eR"]].mean()
        mm[i] = X[motor].mean()
    return dict(af=af, flx=flx, ext=ext, mm=mm)


def dom_freq(x, lo=0.5, hi=10.0):
    z = x - x.mean()
    ps = np.abs(np.fft.rfft(z)) ** 2
    fr = np.fft.rfftfreq(len(z), DT)
    band = (fr >= lo) & (fr <= hi)
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


def s_tr(a, b):
    return float(-np.corrcoef(a, b)[0, 1]) if a.std() > 1e-9 and b.std() > 1e-9 else float("nan")


# ---------- heterodyne phase instrument (amendment 4) ----------
def heterodyne(x, f0):
    """Complex demodulation at f0, smoothed over exactly one period."""
    P = max(2, int(round(1.0 / (f0 * DT))))
    tt = np.arange(len(x)) * DT
    z = (x - x.mean()) * np.exp(-2j * np.pi * f0 * tt)
    ker = np.ones(P) / P
    return np.convolve(z, ker, mode="same")


def wrap_deg(a):
    return (a + 180.0) % 360.0 - 180.0


# ---------------- controls (C0) ----------------
ctrl = {}
for s in SEEDS:
    o = run(s)
    f_hat, ratio = dom_freq(o["mm"][MEAS0:])
    f_flx, _ = dom_freq(o["flx"][MEAS0:])
    S = s_tr(o["flx"][MEAS0:], o["ext"][MEAS0:])
    z = heterodyne(o["mm"][MEAS0:], f_hat)
    R = float(np.abs(z.mean()) / (np.abs(z).mean() + 1e-30))   # coherence at f0
    ctrl[s] = dict(run=o, af=o["af"], f=f_hat, f_flx=f_flx, ratio=ratio, S=S, R=R)
    log(f"ctrl seed {s}: f {f_hat:.3f} (flx {f_flx:.3f}) ratio {ratio:.0f} "
        f"S(Tr) {S:+.2f} R {R:.2f} af {o['af']:.3f}")
    assert abs(f_hat - ANCHOR[s]) <= 0.03, f"C0 anchor seed {s}"
    assert S >= 0.40 and ratio >= 100, f"C0 S/ratio seed {s}"
    assert R >= 0.35, f"C0 heterodyne coherence seed {s}"   # amend. 5

PER = {s: int(round(1.0 / (ctrl[s]["f"] * DT))) for s in SEEDS}   # period, steps
ZC = {s: heterodyne(ctrl[s]["run"]["mm"], ctrl[s]["f"]) for s in SEEDS}
for s in SEEDS:
    log(f"seed {s}: period {PER[s]} steps ({PER[s]*DT:.2f} s)")


def place_onset(seed, phi_deg, near=VOLLEY_NEAR):
    """Onset step where the CONTROL's heterodyne angle matches phi_deg."""
    tgt = np.deg2rad(phi_deg)
    best = None
    for k0 in range(3000, 4201):
        a = np.angle(ZC[seed][k0])
        d = abs(np.angle(np.exp(1j * (a - tgt))))
        if best is None or (d, abs(k0 - near)) < best[0]:
            best = ((d, abs(k0 - near)), k0, float(np.degrees(a)))
    _, k0, a_hit = best
    return k0, a_hit


def phase_read(seed, o, ke):
    """dphi (deg, perturbed vs control) + amp ratio over the post window."""
    zp = heterodyne(o["mm"], ctrl[seed]["f"])
    zc = ZC[seed]
    w0 = min(ke + PER[seed], WIN - 10)
    w1 = min(w0 + int(POST_S / DT), WIN)
    e0 = w0
    e1 = min(w0 + PER[seed], w1)                 # early: first period
    l0 = e1                                        # late: rest of window
    rel = zp * np.conj(zc)
    def cm(a, b):
        seg = rel[a:b]
        return float(np.degrees(np.angle(seg.mean()))), float(np.abs(seg.mean()))
    dphi, amp = cm(w0, w1)
    dphi_e, _ = cm(e0, e1)
    dphi_l, _ = cm(l0, w1)
    _, amp_c = cm(w0, w1)                         # |mean rel| ~ joint amp
    return dict(dphi=dphi, dphi_early=dphi_e, dphi_late=dphi_late_calc(rel, l0, w1, e1),
                amp_ratio=float(np.abs(zp[w0:w1].mean()) /
                                (np.abs(zc[w0:w1].mean()) + 1e-30)))


def dphi_late_calc(rel, l0, w1, e1):
    if w1 - max(l0, e1) < 10:
        return float("nan")
    return float(np.degrees(np.angle(rel[l0:w1].mean())))


# post-window survival metrics (flexor-based, as pre-registered)
def post_metrics(o, ke):
    sl = slice(ke + 50, WIN)
    f_flx, ratio = dom_freq(o["flx"][sl])
    return dict(f_post=f_flx, ratio_post=ratio, S_post=s_tr(o["flx"][sl], o["ext"][sl]))


results = []
trace_store = {}


def do_arm(tag, seed, vcells, vamp, phi_deg, vsteps, store=False):
    k0, a_hit = place_onset(seed, phi_deg)
    ke = k0 + vsteps
    o = run(seed, vcells=vcells, vamp=vamp, k0=k0, vsteps=vsteps)
    pre_ok = (np.array_equal(o["flx"][:k0], ctrl[seed]["run"]["flx"][:k0])
              and np.array_equal(o["mm"][:k0], ctrl[seed]["run"]["mm"][:k0]))
    # honesty probe (tick 52): did the volley perturb the motor mean AT ALL?
    # dm==0 would mean bit-identity (volley never landed); tiny-but-nonzero
    # is a real (diluted) null. dphi -0 with dm>0 = honest null result.
    dm = float(np.abs(o["mm"][ke:] - ctrl[seed]["run"]["mm"][ke:]).max()) if ke < WIN else 0.0
    pm = post_metrics(o, ke)
    pr = phase_read(seed, o, ke)
    d = dict(tag=tag, seed=seed, phi=phi_deg, k0=k0, a_hit=a_hit,
             vsteps=vsteps, vamp=vamp, pre_bitident=pre_ok, af=o["af"],
             dm_mm=dm, **pm, **pr)
    results.append(d)
    if store:
        trace_store[f"{tag}_s{seed}_phi{int(phi_deg)}"] = o["flx"].copy()
        trace_store[f"{tag}_s{seed}_phi{int(phi_deg)}_mm"] = o["mm"].copy()
    return d


# C1 pairing check rides the first real arm of each seed
first = {}
for s in SEEDS:
    d = do_arm("dng95", s, dng95, AMPS_V[0], 0.0, VSTEPS, store=True)
    assert d["pre_bitident"], f"C1 pairing seed {s}"
    first[s] = d
log("C1 pairing: pre-volley traces bit-identical 3/3")

# ---------------- real arms ----------------
for chan, cells in (("dng95", dng95), ("dng100pulse", dng100)):
    for amp in AMPS_V:
        for b in range(NBINS):
            phi = b * 45.0
            per = [do_arm(chan, s, cells, amp, phi, VSTEPS,
                          store=(chan == "dng95" and amp == 0.15))
                   for s in SEEDS]
            log(f"{chan} A{amp} phi{int(phi):>3}: dphi " +
                " ".join(f"{p['dphi']:+.0f}" for p in per) +
                f" | S_post " + " ".join(f"{p['S_post']:+.2f}" for p in per) +
                f" | ampr " + " ".join(f"{p['amp_ratio']:.2f}" for p in per) +
                f" | dm " + " ".join(f"{p['dm_mm']:.1e}" for p in per) +
                f" | {time.time()-t0:.0f}s")

# duration arm: dng95 amp .15, dur 100, bins {0,180}
for phi in (0.0, 180.0):
    per = [do_arm("dng95_dur100", s, dng95, 0.15, phi, DUR_ARM, store=True)
           for s in SEEDS]
    log(f"dng95 dur100 phi{int(phi):>3}: dphi " +
        " ".join(f"{p['dphi']:+.0f}" for p in per))

# ---------------- sham (L33 null form) ----------------
sham_rng = np.random.default_rng(2026)
sham_pairs = [sham_rng.choice(dn_pool, 2, replace=False) for _ in range(SHAM_DRAWS)]
sham_phis = [float(sham_rng.uniform(0, 360)) for _ in range(SHAM_DRAWS)]
for d_i in range(SHAM_DRAWS):
    pair = sham_pairs[d_i]
    phi = sham_phis[d_i]
    per = [do_arm(f"sham{d_i}", s, pair, 0.15, phi, VSTEPS) for s in SEEDS]
    log(f"sham{d_i} (phi {phi:.0f}): dphi " +
        " ".join(f"{p['dphi']:+.0f}" for p in per))

# ---------------- verdict ----------------
real = [r for r in results if r["tag"] in ("dng95", "dng100pulse", "dng95_dur100")]
c2 = all(r["ratio_post"] >= 10 and r["S_post"] >= 0.30 and
         abs(r["f_post"] - ctrl[r["seed"]]["f_flx"]) <= 0.15 for r in real)
c2_fail = [(r["tag"], r["seed"], r["phi"]) for r in real
           if not (r["ratio_post"] >= 10 and r["S_post"] >= 0.30 and
                   abs(r["f_post"] - ctrl[r["seed"]]["f_flx"]) <= 0.15)]

# PRC per channel/amp: max over bins of |mean-over-seeds dphi|
prc = {}
for chan in ("dng95", "dng100pulse"):
    for amp in AMPS_V:
        rows = [r for r in results if r["tag"] == chan and r["vsteps"] == VSTEPS
                and r["vamp"] == amp]
        curve = []
        for b in range(NBINS):
            per = [r for r in rows if r["phi"] == b * 45.0]
            curve.append((b * 45.0, float(np.mean([p["dphi"] for p in per])),
                          [p["dphi"] for p in per]))
        amp_deg, mean_at, per_at = max(curve, key=lambda c: abs(c[1]))
        prc[f"{chan}_A{amp}"] = dict(
            prc_amplitude=abs(float(amp_deg)), argmax_bin=float(mean_at),
            curve=[(float(p), float(m)) for p, m, _ in curve],
            per_seed_at_argmax=per_at)
        log(f"PRC {chan} A{amp}: amplitude {abs(amp_deg):.1f} deg "
            f"@ bin {mean_at:.0f} deg | per-seed " +
            " ".join(f"{v:+.0f}" for v in per_at))

sham_rows = [r for r in results if r["tag"].startswith("sham")]
sham_means = [abs(float(np.mean([r["dphi"] for r in sham_rows if r["seed"] == s])))
              for s in SEEDS]
sham_max = float(max(sham_means))
sham_all_abs = max(abs(r["dphi"]) for r in sham_rows)
log(f"sham |mean dphi| per seed: " + " ".join(f"{m:.1f}" for m in sham_means) +
    f" | single max {sham_all_abs:.1f} deg")

c3 = {}
for k, v in prc.items():
    signs = [np.sign(x) for x in v["per_seed_at_argmax"]]
    c3[k] = dict(gate_amp=v["prc_amplitude"] >= 10.0,
                 gate_sham=v["prc_amplitude"] >= 3 * sham_max,
                 gate_sign=len(set(signs)) == 1,
                 passes=(v["prc_amplitude"] >= 10.0 and
                         v["prc_amplitude"] >= 3 * sham_max and
                         len(set(signs)) == 1))
    log(f"C3 {k}: amp>=10 {c3[k]['gate_amp']} | 3xsham {c3[k]['gate_sham']} "
        f"| sign 3/3 {c3[k]['gate_sign']} -> {'PASS' if c3[k]['passes'] else 'FAIL'}")

# C4 descriptive: dose at argmax bin + persistence (early vs late window)
c4 = {}
for chan in ("dng95", "dng100pulse"):
    hi, lo = prc[f"{chan}_A0.15"], prc[f"{chan}_A0.05"]
    dose_mono = abs(hi["prc_amplitude"]) >= abs(lo["prc_amplitude"])
    rows_hi = [r for r in results if r["tag"] == chan and r["vamp"] == 0.15
               and r["phi"] == hi["argmax_bin"] and r["vsteps"] == VSTEPS]
    early = [r["dphi_early"] for r in rows_hi]
    late = [r["dphi_late"] for r in rows_hi]
    c4[chan] = dict(dose_monotone=bool(dose_mono),
                    amp05=lo["prc_amplitude"], amp15=hi["prc_amplitude"],
                    dphi_early=early, dphi_late=late)
    log(f"C4 {chan}: dose mono {dose_mono} ({lo['prc_amplitude']:.1f} -> "
        f"{hi['prc_amplitude']:.1f} deg) | early " +
        " ".join(f"{p:+.0f}" for p in early) + " | late " +
        " ".join(f"{p:+.0f}" for p in late))

dur_rows = {p: [r["dphi"] for r in results
                if r["tag"] == "dng95_dur100" and r["phi"] == p]
            for p in (0.0, 180.0)}
short_rows = {p: [r["dphi"] for r in results
                  if r["tag"] == "dng95" and r["vamp"] == 0.15
                  and r["vsteps"] == VSTEPS and r["phi"] == p]
              for p in (0.0, 180.0)}
c4["dur"] = {str(int(p)): dict(dur100=dur_rows[p], dur25=short_rows[p])
             for p in (0.0, 180.0)}
log("C4 dur (dphi dur25 vs dur100): " +
    json.dumps({k: {kk: [round(x) for x in vv] for kk, vv in v.items()}
                for k, v in c4["dur"].items()}))

verdict = dict(
    C0_substrate=True,
    C1_pairing=all(first[s]["pre_bitident"] for s in SEEDS),
    C2_survival=bool(c2), C2_failures=c2_fail,
    C3={k: v["passes"] for k, v in c3.items()},
    C3_detail=prc, C4=c4,
    sham_max_mean=sham_max, sham_single_max=sham_all_abs,
    ctrl_R={str(s): ctrl[s]["R"] for s in SEEDS},
    n_runs=3 + len(results))
log("VERDICT " + json.dumps(verdict)[:1500])

np.savez_compressed("l35/traces.npz",
                    **{f"ctrl_{s}": ctrl[s]["run"]["flx"] for s in SEEDS},
                    **{f"ctrl_{s}_mm": ctrl[s]["run"]["mm"] for s in SEEDS},
                    **trace_store)
dump = dict(meta=dict(g=G, beta=BETA, d=D, tau=TAU, dt=DT, win=WIN, meas0=MEAS0,
                      vsteps=VSTEPS, dur_arm=DUR_ARM, amps=AMPS_V, nbins=NBINS,
                      sham_draws=SHAM_DRAWS, seeds=SEEDS, anchor=ANCHOR,
                      post_s=POST_S, nodes=int(n), edges=int(len(gsrc)),
                      dng95_cells=int(len(dng95))),
            ctrl={str(s): {k: v for k, v in ctrl[s].items() if k != "run"}
                  for s in SEEDS},
            arms=[{k: (v.item() if hasattr(v, "item") else v)
                   for k, v in r.items()} for r in results],
            verdict=verdict)
json.dump(dump, open("l35/results_l35.json", "w"), indent=1)
log(f"done {time.time()-t0:.0f}s -> l35/results_l35.json")
