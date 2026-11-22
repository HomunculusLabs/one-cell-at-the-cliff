"""L199 tone-phase instrument. Pure numpy; reads stored traces only.
Uses l197b/gj.py UNCHANGED for the pair-segment duty (sha asserted by callers).
Run from banc/. See l199/PREREG.md for every definition."""
import math
import sys
import numpy as np

sys.path.insert(0, "l197b")
import gj  # noqa: E402

PER = gj.PER
GRAPHS = ("cutwA", "sc25")
BINS = {"inphase": lambda r: r >= .75,
        "mid": lambda r: (r > .25) & (r < .75),
        "antiphase": lambda r: r <= .25}
wrap = lambda d: (np.asarray(d, float) + 180.0) % 360.0 - 180.0


def tone_phi(n=6000, dt=0.01):
    """The harness's elapsed tone phase (run.py: ph += 2 pi target(i) DT)."""
    PHI = np.empty(n)
    ph = 0.0
    for i in range(n):
        ph += 2 * math.pi * (1.4 if 2000 <= i < 4000 else 0.7) * dt
        PHI[i] = ph
    return PHI


def seg_duty(raw, seeds, onsets_abs, W, starts, graphs=GRAPHS):
    """h[G][seg,i,j] (aligned duty per ordered pair-segment) and lag[seg,i,j]."""
    h, lag = {}, None
    for g in graphs:
        H = gj.pair_hits(raw, g, seeds, onsets_abs, W, starts)
        h[g] = H["hit_al"].mean(-1)
        if lag is None:
            lag = H["lag"]
        assert np.array_equal(lag, H["lag"])
    return h, lag


def _jack_angle(fn, n):
    """Delete-one jackknife for an angle (deg): wrapped replicate deviations."""
    full = float(fn(list(range(n))))
    d = np.array([float(wrap(fn([k for k in range(n) if k != x]) - full)) for x in range(n)])
    se = float(np.sqrt((n - 1) / n * ((d - d.mean()) ** 2).sum()))
    return dict(value=full, se=se, ci95=[full - 1.96 * se, full + 1.96 * se])


def part_a(h, lag):
    """Registered 3-bin conditioned profile + bands."""
    n = lag.shape[-1]
    rot = gj.rot_of(lag)
    mo = np.broadcast_to(~np.eye(n, dtype=bool), rot.shape)
    mk = {b: f(rot) for b, f in BINS.items()}
    P = lambda g, b, idx=None: gj.ratio(h[g] * mk[b], mk[b].astype(float), idx)
    S = lambda g: (lambda idx=None: P(g, "inphase", idx) - P(g, "antiphase", idx))
    Ifn = lambda idx=None: S("sc25")(idx) - S("cutwA")(idx)
    one = np.ones_like(rot)
    Efn = lambda idx=None: gj.ratio(h["sc25"], one, idx) - gj.ratio(h["cutwA"], one, idx)
    out = dict(n=n, bin_counts={b: int((mk[b] & mo).sum()) for b in mk},
               profile={g: {b: gj.jack(lambda idx, g=g, b=b: P(g, b, idx), n) for b in mk} for g in GRAPHS},
               slope={g: gj.jack(S(g), n) for g in GRAPHS},
               I=gj.jack(Ifn, n), E=gj.jack(Efn, n),
               A_inphase=gj.jack(lambda idx: P("sc25", "inphase", idx) - P("cutwA", "inphase", idx), n),
               A_antiphase=gj.jack(lambda idx: P("sc25", "antiphase", idx) - P("cutwA", "antiphase", idx), n),
               curvature={g: gj.jack(lambda idx, g=g: P(g, "mid", idx) - (P(g, "inphase", idx) + P(g, "antiphase", idx)) / 2, n)
                          for g in GRAPHS})
    I, sb, sr = out["I"], out["slope"]["cutwA"], out["slope"]["sc25"]
    sign_ok = bool(sb["value"] < 0 and sb["ci95"][1] < 0 and sr["value"] > 0 and sr["ci95"][0] > 0)
    if I["value"] >= .15 and I["ci95"][0] > 0:
        lab = "PH1_sign" if sign_ok else "PH1_shape"
    elif I["ci95"][0] > -.10 and I["ci95"][1] < .10:
        lab = "PH0"
    elif I["ci95"][0] > 0:
        lab = "PH_weak"
    elif I["value"] <= -.15 and I["ci95"][1] < 0:
        lab = "PH_rev"
    else:
        lab = "PH_unresolved"
    out["sign_conditions"] = dict(base_comove=bool(sb["value"] < 0 and sb["ci95"][1] < 0),
                                  removed_alternate=bool(sr["value"] > 0 and sr["ci95"][0] > 0))
    out["label"] = lab
    return out


def _harm(y, psi, m):
    X = np.column_stack([np.ones(m.sum()), np.cos(2 * np.pi * psi[m]), np.sin(2 * np.pi * psi[m])])
    return np.linalg.lstsq(X, y[m], rcond=None)[0]


def part_b(h, lag):
    """Registered signed-offset (first-harmonic) profile + bands."""
    n = lag.shape[-1]
    psi = (lag / PER) % 1.0

    def sel(idx):
        k = np.zeros(n, bool)
        k[idx] = True
        return np.broadcast_to(k[:, None] & k[None, :] & ~np.eye(n, dtype=bool), psi.shape)

    def coef(y):
        return lambda idx: _harm(y, psi, sel(idx))

    def theta(y):
        c = coef(y)
        return lambda idx: math.degrees(math.atan2(*c(idx)[[2, 1]]))

    out = dict(n=n, graphs={})
    full = list(range(n))
    for g in GRAPHS:
        m_, a_, b_ = coef(h[g])(full)
        out["graphs"][g] = dict(mean=float(m_), a_cos=float(a_), b_sin=float(b_), R=float(math.hypot(a_, b_)),
                                R_jack=gj.jack(lambda idx, g=g: float(np.hypot(*coef(h[g])(idx)[1:])), n),
                                theta=_jack_angle(theta(h[g]), n))
    dy = h["sc25"] - h["cutwA"]
    m_, a_, b_ = coef(dy)(full)
    out["phenotype"] = dict(mean=float(m_), a_cos=float(a_), b_sin=float(b_), R=float(math.hypot(a_, b_)),
                            theta=_jack_angle(theta(dy), n))
    tb, tr = theta(h["cutwA"]), theta(h["sc25"])
    out["dtheta"] = _jack_angle(lambda idx: float(wrap(tr(idx) - tb(idx))), n)
    out["dtheta"]["value"] = float(wrap(out["dtheta"]["value"]))
    # 8-bin signed profile (descriptive): octants centred 0, 45, ..., 315 deg
    octant = np.floor(((psi + 1 / 16) % 1.0) * 8).astype(int)
    mo = sel(full)
    out["octants"] = {g: [float(h[g][mo & (octant == k)].mean()) if (mo & (octant == k)).any() else None
                          for k in range(8)] for g in GRAPHS}
    out["octant_counts"] = [int((mo & (octant == k)).sum()) for k in range(8)]
    thb, thr = out["graphs"]["cutwA"]["theta"], out["graphs"]["sc25"]["theta"]
    det = bool(thb["se"] <= 22.5 and thr["se"] <= 22.5)
    near = lambda v, c: bool(abs(float(wrap(v - c))) <= 45.0)
    dt = out["dtheta"]
    if not det:
        lab = "Hu"
    elif near(thb["value"], 180.0) and near(thr["value"], 0.0):
        lab = "H1"
    elif abs(dt["value"]) + 1.96 * dt["se"] < 45.0:
        lab = "H0"
    else:
        lab = "Hq"
    out["checks"] = dict(determinable=det, base_near_180=near(thb["value"], 180.0), removed_near_0=near(thr["value"], 0.0))
    out["label"] = lab
    return out


def pool_alpha(y, onsets_abs, pulse, PHI):
    """Peak tone phase (deg) + amplitude of a pool trace over the displaced pulses."""
    idx = np.concatenate([np.arange(o, o + pulse) for o in onsets_abs])
    sg = np.repeat(np.arange(len(onsets_abs)), pulse)
    X = np.column_stack([(sg == k).astype(float) for k in range(len(onsets_abs))] + [np.cos(PHI[idx]), np.sin(PHI[idx])])
    be = np.linalg.lstsq(X, np.asarray(y, np.float64)[idx], rcond=None)[0]
    return math.degrees(math.atan2(be[-1], be[-2])), float(math.hypot(be[-1], be[-2]))


def circ(deg):
    z = np.exp(1j * np.radians(np.asarray(deg, float)))
    return dict(mean_deg=float(np.degrees(np.angle(z.mean()))), R=float(np.abs(z.mean())), n=int(z.size))


def c_label(c):
    if c["R"] < .5:
        return "dispersed"
    a = abs(c["mean_deg"])
    return "co-move" if a <= 60 else "alternate" if a >= 120 else "intermediate"


def part_c(raw, seeds, onsets_abs, pulse, PHI=None, phi_of=None):
    """Registered direct pool phase. phi_of(seed) -> tone phase array (default PHI)."""
    PHI = tone_phi() if PHI is None else PHI
    out, per = {}, {}
    for g in GRAPHS:
        al = {p: [] for p in ("Ti_fR", "Ti_eR")}
        D, keep = [], []
        for s in seeds:
            ph = PHI if phi_of is None else phi_of(s)
            af, Af = pool_alpha(raw[f"Ti_fR_{g}_{s}"], onsets_abs[s], pulse, ph)
            ae, Ae = pool_alpha(raw[f"Ti_eR_{g}_{s}"], onsets_abs[s], pulse, ph)
            if Af <= 1e-6 or Ae <= 1e-6:
                continue
            al["Ti_fR"].append(af)
            al["Ti_eR"].append(ae)
            D.append(float(wrap(af - ae)))
            keep.append(s)
        per[g] = dict(zip(keep, D))
        c = circ(D)
        out[g] = dict(Delta=c, label=c_label(c), alpha={p: circ(v) for p, v in al.items()})
    both = [s for s in seeds if s in per["cutwA"] and s in per["sc25"]]
    sh = circ([float(wrap(per["sc25"][s] - per["cutwA"][s])) for s in both])
    out["paired_shift"] = sh
    lb, lr = out["cutwA"]["label"], out["sc25"]["label"]
    out["label"] = ("D1" if lb == "co-move" and lr == "alternate" else
                    "D0" if lb == lr and lb != "dispersed" and abs(sh["mean_deg"]) <= 30 and sh["R"] >= .5 else "Dq")
    return out


# ---------------- Part D (causal) ----------------
def part_d(h, nb):
    """h[G][seg, t, u] over 2*nb tags (first nb = phi0, last nb = phiPI, same
    base-seed order). Registered block statistics + bands."""
    def blocks(g, idx):
        idx = np.asarray(idx)
        a, b = idx, nb + idx
        off = ~np.eye(len(idx), dtype=bool)
        sub = lambda r, c: h[g][:, r][:, :, c][:, off].mean()
        return dict(w00=sub(a, a), wPP=sub(b, b), x0P=sub(a, b), xP0=sub(b, a))

    def K(g):
        return lambda idx: (lambda B: (B["w00"] + B["wPP"]) / 2 - (B["x0P"] + B["xP0"]) / 2)(blocks(g, idx))

    def E(k):
        return lambda idx: (blocks("sc25", idx)[k] - blocks("cutwA", idx)[k])

    full = list(range(nb))
    out = dict(n=nb, blocks={g: {k: float(v) for k, v in blocks(g, full).items()} for g in GRAPHS},
               K={g: gj.jack(K(g), nb) for g in GRAPHS},
               K_I=gj.jack(lambda idx: K("sc25")(idx) - K("cutwA")(idx), nb),
               E_00=gj.jack(E("w00"), nb), E_PP=gj.jack(E("wPP"), nb),
               E_X=gj.jack(lambda idx: (E("x0P")(idx) + E("xP0")(idx)) / 2, nb),
               E_PP_minus_E_00=gj.jack(lambda idx: E("wPP")(idx) - E("w00")(idx), nb))
    ar = np.arange(nb)
    out["same_seed"] = {g: dict(phi0=float(h[g][:, ar, ar].mean()), phiPI=float(h[g][:, nb + ar, nb + ar].mean()),
                                cross_phi=float((h[g][:, ar, nb + ar].mean() + h[g][:, nb + ar, ar].mean()) / 2))
                        for g in GRAPHS}
    KI, kb, kr, epp = out["K_I"], out["K"]["cutwA"], out["K"]["sc25"], out["E_PP"]
    sign_ok = bool(kb["value"] < 0 and kb["ci95"][1] < 0 and kr["value"] > 0 and kr["ci95"][0] > 0)
    if KI["value"] >= .15 and KI["ci95"][0] > 0 and epp["value"] > 0 and epp["ci95"][0] > 0:
        lab = "CA1_sign" if sign_ok else "CA1"
    elif KI["ci95"][0] > -.10 and KI["ci95"][1] < .10:
        lab = "CA0"
    elif KI["ci95"][0] > 0 and KI["value"] < .15:
        lab = "CA_weak"
    elif KI["value"] <= -.15 and KI["ci95"][1] < 0:
        lab = "CA_rev"
    else:
        lab = "CA_unresolved"
    out["sign_conditions"] = dict(base_K_negative=bool(kb["value"] < 0 and kb["ci95"][1] < 0),
                                  removed_K_positive=bool(kr["value"] > 0 and kr["ci95"][0] > 0))
    out["label"] = lab
    return out
