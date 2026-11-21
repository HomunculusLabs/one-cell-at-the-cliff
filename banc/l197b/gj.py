"""L197b (gate-jitter v2) shared readout. Pure numpy, reads stored traces only.

Generalises l186/analyze.py's primary metric to an arbitrary correlation
window W and start-offset grid (v1: W=500, starts -250..+250 step 10); with
the v1 parameters it must reproduce results_l186.json EXACTLY (CERT-V1).

For ordered seed pair (i, j), outer segment g, start offset o:
  flex window  = Ti_fR of seed i at [on_i + o, on_i + o + W)
  aligned ext  = Ti_eR of seed j at [on_j + o, on_j + o + W)
  elapsed ext  = Ti_eR of seed j at the SAME absolute steps as the flex window
  hit = Pearson r <= -.25 and both SDs > 1e-6 (flat = miss)
Per pair-segment-offset we also record, for the elapsed view, the fraction of
the ext window during which seed j's gate is ON (any pulse).
"""
import numpy as np

PER = 1.0 / 0.7 / 0.01          # tone period in steps (142.857)
SEG0 = (0, 4000)                # outer (0.7-Hz) segment starts


def _unit(y, idx, W):
    v = y[..., idx].astype(np.float64)
    v = v - v.mean(-1, keepdims=True)
    n = np.linalg.norm(v, axis=-1)
    return v / np.maximum(n[..., None], 1e-99), n > np.sqrt(W) * 1e-6


def pair_hits(raw, arm, seeds, onsets, W, starts, gate_key="gate_{s}"):
    """Returns dict of arrays [seg, i, j, offset]:
    hit_al, hit_el (bool), on_frac (elapsed-view partner gate-on fraction),
    plus lag[seg, i, j] = on_i - on_j."""
    n, no = len(seeds), len(starts)
    win = np.asarray(starts)[:, None] + np.arange(W)[None, :]      # [o, W]
    f = np.stack([raw[f"Ti_fR_{arm}_{s}"] for s in seeds])          # [n, T]
    e = np.stack([raw[f"Ti_eR_{arm}_{s}"] for s in seeds])
    gate = np.stack([raw[gate_key.format(s=s)] for s in seeds]).astype(np.float64)
    hit_al = np.zeros((2, n, n, no), bool)
    hit_el = np.zeros((2, n, n, no), bool)
    on_frac = np.zeros((2, n, n, no), np.float32)
    lag = np.zeros((2, n, n))
    for g in range(2):
        on = np.array([onsets[s][g] for s in seeds])
        lag[g] = on[:, None] - on[None, :]
        # aligned ext windows of every seed at its own onset
        ea, eok = [], []
        for j in range(n):
            u, ok = _unit(e[j], win + on[j], W)
            ea.append(u)
            eok.append(ok)
        ea, eok = np.stack(ea), np.stack(eok)                       # [n, o, W], [n, o]
        for i in range(n):
            idx = win + on[i]                                        # [o, W]
            assert idx.min() >= SEG0[g] and idx.max() < SEG0[g] + 2000
            fu, fok = _unit(f[i], idx, W)                            # [o, W], [o]
            r_al = np.einsum("ow,jow->jo", fu, ea)
            hit_al[g, i] = (r_al <= -.25) & fok[None, :] & eok
            eu, eok2 = _unit(e, idx, W)                              # [n, o, W], [n, o]
            r_el = np.einsum("ow,jow->jo", fu, eu)
            hit_el[g, i] = (r_el <= -.25) & fok[None, :] & eok2
            on_frac[g, i] = gate[:, idx].mean(-1)
    return dict(hit_al=hit_al, hit_el=hit_el, on_frac=on_frac, lag=lag)


def pair_matrix(hit):
    """v1 estimator atom: equal weight over offsets and the two segments."""
    return hit.mean(-1).mean(0)                                      # [i, j]


def offdiag_mean(M, idx=None):
    if idx is not None:
        M = M[np.ix_(idx, idx)]
    m = ~np.eye(M.shape[0], dtype=bool)
    return float(M[m].mean())


def ratio(num, den, idx=None):
    """sum(num)/sum(den) over ordered off-diagonal pairs ([.., i, j] arrays)."""
    if idx is not None:
        num, den = num[..., idx, :][..., :, idx], den[..., idx, :][..., :, idx]
    m = ~np.eye(num.shape[-1], dtype=bool)
    d = den[..., m].sum()
    return float(num[..., m].sum() / d) if d > 0 else float("nan")


def jack(fn, n):
    """Delete-one-seed jackknife (v1 form): normal 95% interval."""
    full = fn(list(range(n)))
    reps = np.array([fn([k for k in range(n) if k != d]) for d in range(n)])
    se = float(np.sqrt((n - 1) / n * ((reps - reps.mean()) ** 2).sum()))
    return dict(value=float(full), se=se, ci95=[float(full - 1.96 * se), float(full + 1.96 * se)])


def overlap_stats(onsets, seeds, W):
    lags, ov = [], []
    for si in seeds:
        for sj in seeds:
            if si == sj:
                continue
            for g in (0, 1):
                L = abs(onsets[si][g] - onsets[sj][g])
                lags.append(L)
                ov.append(max(0.0, 1.0 - L / W))
    lags, ov = np.array(lags, float), np.array(ov, float)
    return dict(n_pair_segments=int(lags.size), mean_abs_lag=float(lags.mean()),
                median_abs_lag=float(np.median(lags)), mean_overlap=float(ov.mean()),
                median_overlap=float(np.median(ov)),
                frac_disjoint=float((ov == 0).mean()), window=int(W))


def rot_of(lag):
    """Relative tone-phase rotation: 1 = in phase, 0 = antiphase (t216 form)."""
    return np.abs(((lag / PER) % 1.0) - 0.5) * 2.0


def analyse(raw, seeds, onsets, W, starts, arms=("cutwA", "sc25")):
    """All registered statistics for one design arm."""
    n = len(seeds)
    H = {a: pair_hits(raw, a, seeds, onsets, W, starts) for a in arms}
    M = {a: dict(aligned=pair_matrix(H[a]["hit_al"]), elapsed=pair_matrix(H[a]["hit_el"]))
         for a in arms}
    for a in arms:      # same-seed diagonal identical between the clocks (wiring)
        assert np.array_equal(M[a]["aligned"].diagonal(), M[a]["elapsed"].diagonal())
    out = dict(n=n, W=int(W), n_offsets=len(starts),
               means={a: dict(aligned=offdiag_mean(M[a]["aligned"]),
                              elapsed=offdiag_mean(M[a]["elapsed"]),
                              same=float(M[a]["aligned"].diagonal().mean())) for a in arms})

    def con(cl):
        return lambda idx: offdiag_mean(M["sc25"][cl], idx) - offdiag_mean(M["cutwA"][cl], idx)

    out["A"] = jack(con("aligned"), n)
    out["T"] = jack(con("elapsed"), n)
    out["D"] = jack(lambda idx: con("aligned")(idx) - con("elapsed")(idx), n)
    # --- secondary: elapsed view split by partner gate state -----------------
    def split_el(a, sel):
        h, fr = H[a]["hit_el"], H[a]["on_frac"]
        m = sel(fr)
        return (h & m).sum(-1).astype(float), m.sum(-1).astype(float)   # [seg, i, j]

    for nm, sel in (("T_on", lambda fr: fr >= .5), ("T_off", lambda fr: fr < .5)):
        nd = {a: split_el(a, sel) for a in arms}
        out[nm] = jack(lambda idx: ratio(*nd["sc25"], idx) - ratio(*nd["cutwA"], idx), n)
        out[nm]["window_share"] = float(nd["cutwA"][1].sum() / H["cutwA"]["hit_el"].size)
        out[nm]["means"] = {a: ratio(*nd[a]) for a in arms}
    # --- secondary: aligned view split by segment-level tone rotation --------
    rot = rot_of(H["cutwA"]["lag"])                                   # [seg, i, j]
    def split_al(a, m):
        h = H[a]["hit_al"].mean(-1)                                   # [seg, i, j]
        return h * m, m.astype(float)

    nd_in = {a: split_al(a, rot >= .75) for a in arms}
    nd_an = {a: split_al(a, rot <= .25) for a in arms}
    f_in = lambda idx: ratio(*nd_in["sc25"], idx) - ratio(*nd_in["cutwA"], idx)
    f_an = lambda idx: ratio(*nd_an["sc25"], idx) - ratio(*nd_an["cutwA"], idx)
    out["A_inphase"] = jack(f_in, n)
    out["A_antiphase"] = jack(f_an, n)
    out["A_in_minus_anti"] = jack(lambda idx: f_in(idx) - f_an(idx), n)
    # --- registered tone control: the t216 instrument VERBATIM (pair-level) ---
    mo = ~np.eye(n, dtype=bool)
    Lp = H["cutwA"]["lag"].mean(0)                                    # mean over the 2 segments
    rp = rot_of(Lp)
    tone = {}
    for a in arms:
        dd = (M[a]["aligned"] - M[a]["elapsed"])[mo]
        tone[a] = dict(rho_rot=float(np.corrcoef(rp[mo], dd)[0, 1]),
                       rho_abslag=float(np.corrcoef(np.abs(Lp[mo]), dd)[0, 1]),
                       rho_rot_aligned_only=float(np.corrcoef(rp[mo], M[a]["aligned"][mo])[0, 1]))
    # segment-level form (the pair-level mean of two INDEPENDENT segment lags
    # smears the rotation; this one uses each pair-segment's own lag)
    ms = np.broadcast_to(mo, rot.shape)
    for a in arms:
        al = H[a]["hit_al"].mean(-1)
        el = H[a]["hit_el"].mean(-1)
        tone[a]["rho_rot_segment_aligned"] = float(np.corrcoef(rot[ms], al[ms])[0, 1])
        tone[a]["rho_rot_segment_al_minus_el"] = float(np.corrcoef(rot[ms], (al - el)[ms])[0, 1])
    out["tone_instrument"] = tone
    out["rot_bin_share"] = dict(inphase=float((rot[ms] >= .75).mean()),
                                antiphase=float((rot[ms] <= .25).mean()))
    out["pair_matrices"] = {a: {k: v.tolist() for k, v in M[a].items()} for a in arms}
    return out


ARM_CODE = {"S": 1, "W": 2}
DESIGN = {
    # S: v1's schedule (500-step pulse, onset 900 +- 300), SHORT readout window
    "S": dict(pulse=500, onset_lo=600, onset_hi=1200, W=150, start_lo=-75, start_hi=425),
    # W: WIDE jitter (band 1000) with a 250-step pulse and a 250-step window
    "W": dict(pulse=250, onset_lo=525, onset_hi=1525, W=250, start_lo=-125, start_hi=125),
}


def draw_onsets(arm, seed):
    """Two independent integer onsets (first, last outer segment), PCG64
    SeedSequence([197, arm code, seed])."""
    d = DESIGN[arm]
    rng = np.random.default_rng(np.random.SeedSequence([197, ARM_CODE[arm], int(seed)]))
    return [int(o) for o in rng.integers(d["onset_lo"], d["onset_hi"] + 1, 2)]


def starts_of(arm):
    d = DESIGN[arm]
    return np.arange(d["start_lo"], d["start_hi"] + 1, 10)


def expected_gate(arm, onsets):
    """Boolean gate of a jittered seed: boundary pulses + 1.4-Hz middle
    segment unchanged, ONE movable pulse per outer segment."""
    t = np.arange(6000)
    g = (t // 2000 == 1) | ((t % 2000 < 500) | (t % 2000 >= 1800))
    for b, o in zip(SEG0, onsets):
        g[b + o:b + o + DESIGN[arm]["pulse"]] = True
    return g
