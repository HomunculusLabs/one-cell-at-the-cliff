# L162 static probe: is the ~.100 Hz slow line ONE shared clock or
# independent per-pool oscillators? PREREG l162/PREREG.md registered FIRST.
# Zero rollouts, read-only over stored npz/json. Deterministic, no RNG.
import json
import math
import re

import numpy as np

WIN, DT = 6000, 0.01
HALF = WIN // 2
FBIN = 1.0 / (WIN * DT)          # 1/60 Hz
HBIN = 1.0 / (HALF * DT)
Z = 1.959963984540054
SEG, HOP = 2000, 1000            # Welch: 20 s segments, 50% overlap -> K=5

FILES = ["l154/raw_l154.npz", "l150/raw_l150.npz"]
POOLS = ([f"Ti_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"Tr_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"{j}_{s}" for j in ("Ta", "Pr", "Sr")
            for s in ("aL", "aR", "bL", "bR")])
EXTRA = ["mm", "xm"]
CHANNELS = POOLS + EXTRA
ARMS = {"l154/raw_l154.npz": ["b65", "off"], "l150/raw_l150.npz": ["b65"]}


# ---------------- VERBATIM l157/l156 lineage machinery -----------------------
def dom_freq(x, lo=0.3):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    return float(f_hat), int(i == 0)


def bin_argmax(x, lo=0.0):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    return float(fb[int(np.argmax(pb))])


def wilson_lb(k, n):
    if n == 0:
        return float("nan")
    p = k / n
    den = 1 + Z * Z / n
    ctr = p + Z * Z / (2 * n)
    rad = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (ctr - rad) / den


# ---------------- L162 instruments -------------------------------------------
_HANN = np.hanning(SEG)
_SEG_STARTS = list(range(0, WIN - SEG + 1, HOP))     # 0,1000,2000,3000,4000
K = len(_SEG_STARTS)
_FR_FULL = np.fft.rfftfreq(WIN, DT)
_FR_SEG = np.fft.rfftfreq(SEG, DT)
BIN_FULL = 6
BIN_SEG = 2


def seg_vec(x):
    """complex K-vector: windowed segment FFT at the .100 Hz segment bin."""
    out = np.empty(K, dtype=np.complex128)
    for j, s0 in enumerate(_SEG_STARTS):
        w = x[s0:s0 + SEG]
        out[j] = np.fft.rfft((w - w.mean()) * _HANN)[BIN_SEG]
    return out


def full_bin(x):
    zz = x - x.mean()
    return complex(np.fft.rfft(zz)[BIN_FULL])


def msc_matrix(SA, SB):
    """MSC[s,s'] from segment-FFT stacks (n,K); diagonal = matched."""
    C = SA @ SB.conj().T
    PA = (np.abs(SA) ** 2).sum(axis=1)
    PB = (np.abs(SB) ** 2).sum(axis=1)
    return (np.abs(C) ** 2) / np.outer(PA, PB)


def plv_rayleigh(dphis):
    n = len(dphis)
    r = np.abs(np.mean(np.exp(1j * np.asarray(dphis))))
    return float(r), float(math.exp(-n * r * r))


# ---------------- CERT-3 bin exactness ---------------------------------------
assert abs(_FR_FULL[BIN_FULL] - 0.1) < 1e-12, _FR_FULL[BIN_FULL]
assert abs(_FR_SEG[BIN_SEG] - 0.1) < 1e-12, _FR_SEG[BIN_SEG]
assert K == 5, K
print(f"CERT-3 bin exactness: full fr[{BIN_FULL}]={_FR_FULL[BIN_FULL]!r} "
      f"seg fr[{BIN_SEG}]={_FR_SEG[BIN_SEG]!r} K={K}: PASS")

# ---------------- CERT-1 analytic self-tests ---------------------------------
tt_s = np.arange(WIN) * DT
sa = np.sin(2 * math.pi * 0.1 * tt_s)
sb = np.sin(2 * math.pi * 0.1 * tt_s + 0.6)
jit = 0.01 * np.sin(2 * math.pi * 3.3 * tt_s)          # deterministic "noise"
m_sin = float(msc_matrix(seg_vec(sa + jit)[None, :],
                         seg_vec(sb - jit)[None, :])[0, 0])
assert m_sin > 0.95, ("CERT-1a", m_sin)
# independent pseudo-noise, deterministic (incommensurate tone combs)
na = sum(np.sin(2 * math.pi * f * tt_s + 0.3 * i)
         for i, f in enumerate([0.0917, 0.1033, 0.1171, 0.0813]))
nb = sum(np.cos(2 * math.pi * f * tt_s + 1.1 * i)
         for i, f in enumerate([0.0971, 0.1079, 0.1123, 0.0869]))
m_noise = float(msc_matrix(seg_vec(na)[None, :], seg_vec(nb)[None, :])[0, 0])
assert m_noise < 0.75 and m_noise < m_sin - 0.2, ("CERT-1b", m_noise, m_sin)
plv_fix, p_fix = plv_rayleigh([0.6] * 36)
plv_uni, p_uni = plv_rayleigh([2 * math.pi * j / 36 for j in range(36)])
assert plv_fix > 0.999, ("CERT-1c", plv_fix)
assert plv_uni < 0.05, ("CERT-1d", plv_uni)
print(f"CERT-1 analytic: MSC sin-pair {m_sin:.4f} vs indep {m_noise:.4f}; "
      f"PLV fixed {plv_fix:.4f} / uniform {plv_uni:.2e}: PASS")

# ---------------- load + seed-grid derivation (L44 rule) ---------------------
seeds = {}
S_SEG = {}       # (file, arm, ch) -> (n,K) complex stack
S_FULL = {}      # (file, arm, ch) -> (n,) complex
CENS = {}        # (file, arm, ch) -> per-seed census dict (for CERT-2)
tt = np.arange(WIN, dtype=np.float64)
for f in FILES:
    z = np.load(f)
    ss = sorted(int(m.group(1)) for m in
                (re.match(r"^mm_b65_(\d+)$", k) for k in z.files) if m)
    seeds[f] = ss
    assert len(ss) == 18, (f, ss)
    for a in ARMS[f]:
        for ch in CHANNELS:
            segs, fulls, cen = [], [], {}
            for s in ss:
                x = z[f"{ch}_{a}_{s}"][:WIN].astype(np.float64)
                assert len(x) == WIN and np.isfinite(x).all(), (f, a, ch, s)
                segs.append(seg_vec(x))
                fulls.append(full_bin(x))
                f_glob, _ = dom_freq(x, lo=0.0)
                c = np.polyfit(tt, x, 1)
                f_det, _ = dom_freq(x - np.polyval(c, tt), lo=0.0)
                below = bool(f_glob < 0.3)
                cen[s] = dict(
                    f_glob=f_glob, below=below,
                    below_bin=bool(bin_argmax(x) < 0.3),
                    survive=bool(below and f_det < 0.3
                                 and abs(f_det - f_glob) <= FBIN + 1e-9))
            S_SEG[(f, a, ch)] = np.array(segs)
            S_FULL[(f, a, ch)] = np.array(fulls)
            CENS[(f, a, ch)] = cen
    del z
print(f"loaded: seed grids {[ (f.split('/')[0], seeds[f][:2]+['..']+seeds[f][-1:]) for f in FILES ]}")

# ---------------- CERT-2 reader identity vs l157/static.json -----------------
l157 = json.load(open("l157/static.json"))
for ch in CHANNELS:
    allv = [v for f in FILES for v in CENS[(f, "b65", ch)].values()]
    bl = [v for v in allv if v["below"]]
    mine = dict(n=len(allv), below=len(bl),
                below_bin=sum(v["below_bin"] for v in allv),
                wilson_lb=wilson_lb(len(bl), len(allv)),
                survive=sum(v["survive"] for v in bl),
                med_f_below=(float(np.median([v["f_glob"] for v in bl]))
                             if bl else None))
    ref = l157["pooled"][ch]
    for k, v in mine.items():
        if k == "med_f_below" and v is None:
            continue
        assert ref[k] == v, ("CERT-2", ch, k, ref[k], v)
print(f"CERT-2 pooled rows == l157/static.json ({len(CHANNELS)} channels, "
      f"6 fields): PASS")

# ---------------- CERT-4 set derivation --------------------------------------
CARRIER = [c for c in POOLS if l157["pooled"][c]["wilson_lb"] >= 0.5]
CONTROL = [c for c in POOLS if l157["pooled"][c]["below"] <= 6]
assert len(CARRIER) == 8, CARRIER
# ADDENDUM 1: nine dead pools, not eight (Tr_fR 0/36 was missing from the
# PREREG's prose-derived list; L44 class, caught by this assert pre-read).
assert len(CONTROL) == 9, CONTROL
assert not (set(CARRIER) & set(CONTROL))
assert set(CARRIER) == {"Tr_fL", "Tr_eL", "Tr_eR", "Ta_aL", "Ta_aR",
                        "Ta_bR", "Sr_aL", "Sr_bL"}, CARRIER
assert set(CONTROL) == {"Ti_fL", "Ti_fR", "Ti_eL", "Ti_eR", "Tr_fR",
                        "Pr_aL", "Pr_aR", "Pr_bL", "Sr_aR"}, CONTROL
print(f"CERT-4 sets: CARRIER {CARRIER} | CONTROL(+Tr_fR, ADDENDUM 1) "
      f"{CONTROL}: PASS")

CP = [(CARRIER[i], CARRIER[j])
      for i in range(8) for j in range(i + 1, 8)]
NP_ = [(CONTROL[i], CONTROL[j])
       for i in range(len(CONTROL)) for j in range(i + 1, len(CONTROL))]
assert len(CP) == 28 and len(NP_) == 36


# ---------------- I1 + I2 ----------------------------------------------------
def pair_read(f, a, pa, pb):
    M = msc_matrix(S_SEG[(f, a, pa)], S_SEG[(f, a, pb)])
    n = M.shape[0]
    matched = np.diag(M)
    off = M[~np.eye(n, dtype=bool)]
    return (float(np.median(matched)), float(np.median(off)),
            float(matched.mean()), float(off.mean()), int(off.size))


def clears(mm_med, sh_med):
    return bool(mm_med >= 0.5 and mm_med >= 2.0 * sh_med)


res = {"card": "L162 slow-line origin probe", "win": WIN, "dt": DT,
       "seg": SEG, "hop": HOP, "K": K, "bin_full": BIN_FULL,
       "bin_seg": BIN_SEG, "carrier": CARRIER, "control": CONTROL,
       "seeds": {f: seeds[f] for f in FILES},
       "cert": dict(msc_sin=m_sin, msc_indep=m_noise, plv_fixed=plv_fix,
                    plv_uniform=plv_uni),
       "i1": {}, "i2": {}, "i3": {}, "verdict": {}}

for label, pairs in (("carrier", CP), ("control", NP_)):
    for f in FILES:
        for a in ARMS[f]:
            rowset = {}
            for pa, pb in pairs:
                mm_med, sh_med, mm_mu, sh_mu, nsh = pair_read(f, a, pa, pb)
                rowset[f"{pa}~{pb}"] = dict(
                    msc_matched_med=mm_med, msc_shuffled_med=sh_med,
                    msc_matched_mean=mm_mu, msc_shuffled_mean=sh_mu,
                    n_shuffled=nsh, ratio=(mm_med / sh_med if sh_med > 0
                                           else float("inf")),
                    clears=clears(mm_med, sh_med))
            res["i1"][f"{label}|{f}|{a}"] = rowset

# pooled I1 over the two b65 files: pool the 36 matched + 612 shuffled values
pooled_i1 = {}
for label, pairs in (("carrier", CP), ("control", NP_)):
    for pa, pb in pairs:
        mats, offs = [], []
        for f in FILES:
            M = msc_matrix(S_SEG[(f, "b65", pa)], S_SEG[(f, "b65", pb)])
            n = M.shape[0]
            mats.append(np.diag(M))
            offs.append(M[~np.eye(n, dtype=bool)])
        mm = np.concatenate(mats)
        sh = np.concatenate(offs)
        pooled_i1[f"{label}|{pa}~{pb}"] = dict(
            n_matched=int(mm.size), n_shuffled=int(sh.size),
            msc_matched_med=float(np.median(mm)),
            msc_shuffled_med=float(np.median(sh)),
            ratio=float(np.median(mm) / np.median(sh)),
            clears=clears(float(np.median(mm)), float(np.median(sh))))
res["i1_pooled"] = pooled_i1

# I2 across-seed PLV on the pooled 36 b65 seeds
for label, pairs in (("carrier", CP), ("control", NP_)):
    for pa, pb in pairs:
        d = []
        for f in FILES:
            A, B = S_FULL[(f, "b65", pa)], S_FULL[(f, "b65", pb)]
            d.extend(np.angle(A * np.conj(B)).tolist())
        plv, pr = plv_rayleigh(d)
        res["i2"][f"{label}|{pa}~{pb}"] = dict(
            n=len(d), plv=plv, rayleigh_p=pr,
            circ_mean_deg=math.degrees(
                math.atan2(float(np.mean(np.sin(d))),
                           float(np.mean(np.cos(d))))),
            locked=bool(plv >= 0.5 and pr < 0.01))

# I3 descriptive frequency concordance (tie-degeneracy disclosed)
with_seed, with_car = [], []
for f in FILES:
    for i, s in enumerate(seeds[f]):
        fs = [CENS[(f, "b65", c)][s]["f_glob"] for c in CARRIER]
        with_seed.append(float(np.std(fs)))
for c in CARRIER:
    fs = [CENS[(f, "b65", c)][s]["f_glob"]
          for f in FILES for s in seeds[f]]
    with_car.append(float(np.std(fs)))
res["i3"] = dict(
    within_seed_sd_across_carriers=dict(
        median=float(np.median(with_seed)), vals=with_seed),
    within_carrier_sd_across_seeds=dict(
        median=float(np.median(with_car)), vals=with_car),
    fbin=FBIN,
    note=("DESCRIPTIVE ONLY — L157 med_f values are bin-pinned at .100/.101 "
          "so a both-small outcome carries no information (L95 "
          "tie-degeneracy class)."))

# ---------------- registered classes ----------------------------------------
def n_clear(label, f, a):
    return sum(v["clears"] for v in res["i1"][f"{label}|{f}|{a}"].values())


def med_matched(label, f, a):
    return float(np.median([v["msc_matched_med"]
                            for v in res["i1"][f"{label}|{f}|{a}"].values()]))


per_file = {}
for f in FILES:
    nc = n_clear("carrier", f, "b65")
    cm, ctl = med_matched("carrier", f, "b65"), med_matched("control", f, "b65")
    if nc >= 22 and cm > ctl:
        d = "D1_shared_clock"
    elif nc <= 7:
        d = "D2_independent"
    else:
        d = "D3_mixed_clustered"
    per_file[f] = dict(n_clear_carrier=nc, n_clear_control=n_clear("control", f, "b65"),
                       med_matched_carrier=cm, med_matched_control=ctl, cls=d)
pooled_nc = sum(v["clears"] for k, v in pooled_i1.items()
                if k.startswith("carrier|"))
pooled_nc_ctl = sum(v["clears"] for k, v in pooled_i1.items()
                    if k.startswith("control|"))
same_cls = per_file[FILES[0]]["cls"] == per_file[FILES[1]]["cls"]
cls = per_file[FILES[0]]["cls"]
d3_sets = [frozenset(k for k, v in res["i1"][f"carrier|{f}|b65"].items()
                     if v["clears"]) for f in FILES]
if cls == "D1_shared_clock":
    defining_ok = pooled_nc >= 22
elif cls == "D2_independent":
    defining_ok = pooled_nc <= 7
else:
    # registered D3 rule: pooled count in band AND the named subset
    # reproduces on both files (identical clearing-pair sets)
    defining_ok = bool(8 <= pooled_nc <= 21 and d3_sets[0] == d3_sets[1])
n_locked = sum(v["locked"] for k, v in res["i2"].items()
               if k.startswith("carrier|"))
n_locked_ctl = sum(v["locked"] for k, v in res["i2"].items()
                   if k.startswith("control|"))
pcls = ("P1_phase_reproducible" if n_locked >= 14
        else "P2_phase_lottery" if n_locked <= 7 else "P3_mixed")
res["verdict"] = dict(per_file=per_file, coherence_class=cls,
                      same_on_both_files=same_cls,
                      pooled_n_clear_carrier=pooled_nc,
                      pooled_n_clear_control=pooled_nc_ctl,
                      defining_ok=bool(defining_ok),
                      fold_draft=bool(same_cls and defining_ok),
                      phase_class=pcls, n_locked_carrier=n_locked,
                      n_locked_control=n_locked_ctl,
                      d3_clearing_sets={f: sorted(s) for f, s
                                        in zip(FILES, d3_sets)},
                      d3_sets_identical=bool(d3_sets[0] == d3_sets[1]))

json.dump(res, open("l162/static.json", "w"), indent=1)

# ---------------- report -----------------------------------------------------
print(f"\nCOHERENCE class: {cls} (same both files: {same_cls}); "
      f"pooled clears {pooled_nc}/28 carrier vs {pooled_nc_ctl}/{len(NP_)} control; "
      f"draft fold: {'YES' if res['verdict']['fold_draft'] else 'NO'}")
for f in FILES:
    v = per_file[f]
    print(f"  {f}: {v['cls']} clears {v['n_clear_carrier']}/28 "
          f"(control {v['n_clear_control']}/{len(NP_)}) med matched MSC "
          f"carrier {v['med_matched_carrier']:.3f} vs control "
          f"{v['med_matched_control']:.3f}")
print(f"PHASE class: {pcls} — locked {n_locked}/28 carrier, "
      f"{n_locked_ctl}/{len(NP_)} control (PLV>=.5 & Rayleigh p<.01)")
print("\npooled carrier pairs (36 matched / 612 shuffled): "
      "matched_med | shuffled_med | ratio | clears | PLV | p")
for pa, pb in CP:
    k = f"carrier|{pa}~{pb}"
    a1, a2 = pooled_i1[k], res["i2"][k]
    print(f"  {pa:6s}~{pb:6s} {a1['msc_matched_med']:.3f} | "
          f"{a1['msc_shuffled_med']:.3f} | {a1['ratio']:5.2f} | "
          f"{'Y' if a1['clears'] else '.'} | {a2['plv']:.3f} | "
          f"{a2['rayleigh_p']:.2e} | {a2['circ_mean_deg']:+7.1f} deg")
print("\ncontrol (dead-pool) pairs, same instrument:")
for pa, pb in NP_:
    k = f"control|{pa}~{pb}"
    a1, a2 = pooled_i1[k], res["i2"][k]
    print(f"  {pa:6s}~{pb:6s} {a1['msc_matched_med']:.3f} | "
          f"{a1['msc_shuffled_med']:.3f} | {a1['ratio']:5.2f} | "
          f"{'Y' if a1['clears'] else '.'} | {a2['plv']:.3f} | "
          f"{a2['rayleigh_p']:.2e}")
print("\nsanity (aggregates contain carrier mass by construction):")
for ch in EXTRA:
    for c in CARRIER[:3]:
        mats, offs = [], []
        for f in FILES:
            M = msc_matrix(S_SEG[(f, "b65", ch)], S_SEG[(f, "b65", c)])
            mats.append(np.diag(M))
            offs.append(M[~np.eye(M.shape[0], dtype=bool)])
        print(f"  {ch}~{c:6s} matched {np.median(np.concatenate(mats)):.3f} "
              f"shuffled {np.median(np.concatenate(offs)):.3f}")
print("\nI3 (descriptive): within-seed SD across carriers med "
      f"{res['i3']['within_seed_sd_across_carriers']['median']:.5f} Hz vs "
      f"within-carrier SD across seeds med "
      f"{res['i3']['within_carrier_sd_across_seeds']['median']:.5f} Hz "
      f"(FBIN {FBIN:.5f})")
print("\noff-arm (l154, DESCRIPTIVE secondary): clears "
      f"{n_clear('carrier', FILES[0], 'off')}/28 carrier, "
      f"{n_clear('control', FILES[0], 'off')}/{len(NP_)} control; med matched "
      f"{med_matched('carrier', FILES[0], 'off'):.3f} vs "
      f"{med_matched('control', FILES[0], 'off'):.3f}")
print("l162/static.json written")
