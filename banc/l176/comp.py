"""L176 stage (a): the Guba composite antiphase metric on OUR stored traces.

ZERO rollouts. Reads stored npz read-only. CERT first (reproduce every stored
kL/kR/meanL/meanR exactly, L85 rule), then the composite cells of PREREG.md.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BANC = os.path.dirname(HERE)

WIN, DT = 6000, 0.01
FS = 1.0 / DT
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
TS = np.arange(499, WIN, 10)
PAIRS = ["Ti", "Tr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
ANCHORS = {801, 901}
Z = 1.959963984540054

RUNS = [("l135", "raw_l135.npz", "results_l135.json"),
        ("l169", "raw_l169.npz", "results_l169.json"),
        ("l169b2", "raw_l169b2.npz", "results_l169b2.json")]

# ---- declared conventions (PREREG section 1) ----
W_AMP = 0.963
WEIGHT_SETS = {
    "equal_residual": (0.0185, W_AMP, 0.0185),      # PRIMARY
    "resid_to_plv": (0.037, W_AMP, 0.0),
    "resid_to_ph": (0.0, W_AMP, 0.037),
    "uniform": (1 / 3, 1 / 3, 1 / 3),
}
ALPHAS = [0.0, 0.5, 1.0, 2.0]
PRIM_W, PRIM_ALPHA = "equal_residual", 1.0
BANDS = {"pub_1_10": (1.0, 10.0), "sub_03_10": (0.3, 10.0)}
PRIM_BAND = "sub_03_10"
PROM = 0.25


def q07_mask():
    q = np.zeros(len(TS), bool)
    for a0, b0, f in SEGB:
        if f == 0.7:
            q |= (TS >= a0 + MEAS0) & (TS < b0)
    return q


Q07 = q07_mask()
TSQ = TS[Q07]


# ================= stored metric (verbatim l135_verdict.py) =================
def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def s_arrays(raw, a, s, pk):
    ag, bg = PREF[pk]
    tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN]
          for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(tr[f"{ag}L"][t - 499:t + 1], tr[f"{bg}L"][t - 499:t + 1])
        SR[t] = S_of(tr[f"{ag}R"][t - 499:t + 1], tr[f"{bg}R"][t - 499:t + 1])
    return SL, SR, tr


def duty_from_S(SL, SR):
    return (round(float(np.nanmean(SL[TSQ] >= .25)), 3),
            round(float(np.nanmean(SR[TSQ] >= .25)), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ================= the composite (PREREG C1-C9) =================
def analytic(x, f_lo, f_hi):
    """Band-limited analytic signal, pure numpy (C1)."""
    n = len(x)
    xd = np.asarray(x, dtype=np.float64)
    xd = xd - xd.mean()
    X = np.fft.fft(xd)
    fr = np.fft.fftfreq(n, d=DT)
    out = np.zeros(n, dtype=np.complex128)
    keep = (fr > 0) & (fr >= f_lo) & (fr <= f_hi)
    out[keep] = 2.0 * X[keep]
    if f_lo <= 0:
        out[0] = X[0]
    return np.fft.ifft(out)


def peak_count(env):
    if len(env) < 3:
        return 0
    lo, hi = env.min(), env.max()
    thr = lo + PROM * (hi - lo)
    c = env[1:-1]
    m = (c > env[:-2]) & (c >= env[2:]) & (c >= thr)
    return int(m.sum())


def comp_windows(tr_f, tr_e, band):
    """Per-window component arrays over TSQ for one antagonist pair/side."""
    f_lo, f_hi = BANDS[band]
    zf, ze = analytic(tr_f, f_lo, f_hi), analytic(tr_e, f_lo, f_hi)
    ef, ee = np.abs(zf), np.abs(ze)
    d = np.angle(zf) - np.angle(ze)
    raw_f = np.asarray(tr_f, dtype=np.float64)
    raw_e = np.asarray(tr_e, dtype=np.float64)
    n = len(TSQ)
    PLV = np.empty(n)
    A = np.empty(n)
    PH = np.empty(n)
    P = np.empty(n)
    floor_hit = np.zeros(n, bool)
    for i, t in enumerate(TSQ):
        sl = slice(t - 499, t + 1)
        wf, we = ef[sl], ee[sl]
        dd = d[sl]
        PLV[i] = abs(np.exp(1j * dd).mean())
        mf, me = wf.mean(), we.mean()
        A[i] = (min(mf, me) / max(mf, me)) if max(mf, me) > 0 else 0.0
        ang = math.degrees(abs(np.angle(np.exp(1j * dd).mean())))
        PH[i] = 1.0 - abs(180.0 - ang) / 180.0
        P[i] = max(peak_count(wf), peak_count(we))
        rf, re_ = abs(raw_f[sl].mean()), abs(raw_e[sl].mean())
        ref = max(rf, re_)
        floor_hit[i] = (ref > 0) and (max(mf, me) < 0.01 * ref)
    return dict(PLV=PLV, A=A, PH=PH, P=P, floor=floor_hit)


def composite(c, wset, alpha):
    wp, wa, wh = WEIGHT_SETS[wset]
    core = (wp * c["PLV"] + wa * c["A"] + wh * c["PH"]) / (wp + wa + wh)
    g = np.exp(-alpha * np.maximum(0.0, c["P"] - 2.0))
    return core * g


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    def rk(v):
        o = v.argsort()
        r = np.empty(len(v), float)
        r[o] = np.arange(len(v), dtype=float)
        # average ties
        for u in np.unique(v):
            m = v == u
            if m.sum() > 1:
                r[m] = r[m].mean()
        return r
    rx, ry = rk(x), rk(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def jack_ci(d):
    d = np.asarray(d, float)
    n = len(d)
    th = d.mean()
    lo = np.array([np.delete(d, i).mean() for i in range(n)])
    se = math.sqrt((n - 1) / n * ((lo - lo.mean()) ** 2).sum())
    return th - 1.959963984540054 * se, th + 1.959963984540054 * se


# ================= run =================
def main():
    out = {"prereg": "banc/l176/PREREG.md", "stage": "a",
           "conventions": {"W_AMP": W_AMP, "weight_sets": {k: list(v) for k, v in WEIGHT_SETS.items()},
                           "alphas": ALPHAS, "bands": {k: list(v) for k, v in BANDS.items()},
                           "primary": [PRIM_W, PRIM_ALPHA, PRIM_BAND], "prom": PROM}}
    mtimes = {}
    cert = {"checks": 0, "fail": []}
    store = {}   # (run, arm, pair) -> dict(seeds, dutyL, dutyR, comp...)

    for run, npz, res in RUNS:
        p = os.path.join(BANC, run, npz)
        mtimes[p] = os.path.getmtime(p)
        z = np.load(p)
        r = json.load(open(os.path.join(BANC, run, res)))
        tbl = r["table"]
        for pk in PAIRS:
            if pk not in tbl:
                continue
            arms = list(tbl[pk].keys())
            seeds = sorted({int(k.rsplit("_", 1)[1]) for k in z.keys()
                            if k.startswith(f"{pk}_fR_{arms[0]}_")} - ANCHORS)
            for a in arms:
                dL, dR = [], []
                comp = {}
                for s in seeds:
                    SL, SR, tr = s_arrays(z, a, s, pk)
                    x, y = duty_from_S(SL, SR)
                    dL.append(x)
                    dR.append(y)
                    ag, bg = PREF[pk]
                    for band in BANDS:
                        for side in ("L", "R"):
                            c = comp_windows(tr[f"{ag}{side}"], tr[f"{bg}{side}"], band)
                            comp.setdefault((band, side), []).append(c)
                dL, dR = np.array(dL), np.array(dR)
                got = dict(kL=int((dL >= .5).sum()), kR=int((dR >= .5).sum()),
                           meanL=round(float(dL.mean()), 3), meanR=round(float(dR.mean()), 3))
                want = tbl[pk][a]
                for kk in ("kL", "kR", "meanL", "meanR"):
                    cert["checks"] += 1
                    if want.get(kk) != got[kk]:
                        cert["fail"].append([run, pk, a, kk, want.get(kk), got[kk]])
                store[(run, a, pk)] = dict(seeds=seeds, dL=dL, dR=dR, comp=comp)
        del z

    out["cert"] = dict(checks=cert["checks"], n_fail=len(cert["fail"]),
                       fail=cert["fail"][:20], passed=not cert["fail"])
    print(f"CERT {cert['checks']} checks, {len(cert['fail'])} fail", flush=True)
    if cert["fail"]:
        json.dump(out, open(os.path.join(HERE, "results_l176a.json"), "w"), indent=1)
        raise SystemExit("CERT FAILED — halting per PREREG section 3")

    # ---- composite summaries ----
    def cmean(rec, band, side, wset=PRIM_W, alpha=PRIM_ALPHA):
        return np.array([composite(c, wset, alpha).mean()
                         for c in rec["comp"][(band, side)]])

    summ = {}
    for (run, a, pk), rec in store.items():
        for band in BANDS:
            for side in ("L", "R"):
                cs = rec["comp"][(band, side)]
                key = f"{run}|{a}|{pk}|{band}|{side}"
                summ[key] = dict(
                    comp=round(float(cmean(rec, band, side).mean()), 4),
                    PLV=round(float(np.mean([c["PLV"].mean() for c in cs])), 4),
                    A=round(float(np.mean([c["A"].mean() for c in cs])), 4),
                    PH=round(float(np.mean([c["PH"].mean() for c in cs])), 4),
                    Pmean=round(float(np.mean([c["P"].mean() for c in cs])), 3),
                    frac_P_gt2=round(float(np.mean([(c["P"] > 2).mean() for c in cs])), 4),
                    g_mean=round(float(np.mean([np.exp(-PRIM_ALPHA * np.maximum(0, c["P"] - 2)).mean()
                                                for c in cs])), 4),
                    floor_frac=round(float(np.mean([c["floor"].mean() for c in cs])), 4),
                    duty=round(float((rec["dL"] if side == "L" else rec["dR"]).mean()), 3),
                )
    out["summary"] = summ

    # ---- PRIMARY: carrier vs twin, paired within seed ----
    prim = {}
    PAIRSET = [("l169", "cutwA", "silW", "mass twin"),
               ("l169b2", "cutwA", "silW", "mass twin"),
               ("l169b2", "f4wA", "f4tw", "floor-4 twin")]
    for run, ca, tw, lab in PAIRSET:
        for pk in PAIRS:
            if (run, ca, pk) not in store or (run, tw, pk) not in store:
                continue
            rc, rt = store[(run, ca, pk)], store[(run, tw, pk)]
            assert rc["seeds"] == rt["seeds"]
            for band in BANDS:
                for side in ("L", "R"):
                    for wset in WEIGHT_SETS:
                        for al in ALPHAS:
                            cc = cmean(rc, band, side, wset, al)
                            ct = cmean(rt, band, side, wset, al)
                            d = cc - ct
                            lo, hi = jack_ci(d)
                            prim[f"{run}|{ca}-{tw}|{pk}|{band}|{side}|{wset}|a{al}"] = dict(
                                label=lab, n=len(d),
                                mean_carrier=round(float(cc.mean()), 4),
                                mean_twin=round(float(ct.mean()), 4),
                                paired_mean=round(float(d.mean()), 4),
                                sign=int(np.sign(d.mean())),
                                k_up=int((d > 0).sum()),
                                ci=[round(lo, 4), round(hi, 4)],
                                ci_excl_0=bool(lo > 0 or hi < 0),
                                duty_carrier=round(float((rc["dL"] if side == "L" else rc["dR"]).mean()), 3),
                                duty_twin=round(float((rt["dL"] if side == "L" else rt["dR"]).mean()), 3),
                            )
    out["primary"] = prim

    # ---- SECONDARY: rank order vs stored duty ----
    sec = {}
    for run, _, _ in RUNS:
        for pk in PAIRS:
            arms = sorted({a for (r2, a, p2) in store if r2 == run and p2 == pk})
            if len(arms) < 4:
                continue
            for band in BANDS:
                for side in ("L", "R"):
                    duty = [float((store[(run, a, pk)]["dL"] if side == "L"
                                   else store[(run, a, pk)]["dR"]).mean()) for a in arms]
                    comp = [summ[f"{run}|{a}|{pk}|{band}|{side}"]["comp"] for a in arms]
                    sec[f"{run}|{pk}|{band}|{side}"] = dict(
                        n_arms=len(arms), arms=arms,
                        rho=round(spearman(comp, duty), 4),
                        duty=[round(v, 3) for v in duty], comp=comp)
    out["secondary"] = sec

    # ---- degenerate branch + band-floor diagnostic ----
    deg = {}
    for run, _, _ in RUNS:
        for pk in PAIRS:
            arms = sorted({a for (r2, a, p2) in store if r2 == run and p2 == pk})
            if not arms:
                continue
            for band in BANDS:
                for side in ("L", "R"):
                    As = [summ[f"{run}|{a}|{pk}|{band}|{side}"]["A"] for a in arms]
                    PLs = [summ[f"{run}|{a}|{pk}|{band}|{side}"]["PLV"] for a in arms]
                    PHs = [summ[f"{run}|{a}|{pk}|{band}|{side}"]["PH"] for a in arms]
                    deg[f"{run}|{pk}|{band}|{side}"] = dict(
                        A_range=round(max(As) - min(As), 4),
                        PLV_range=round(max(PLs) - min(PLs), 4),
                        PH_range=round(max(PHs) - min(PHs), 4),
                        degenerate=bool(max(As) - min(As) < 0.05),
                        floor_frac_max=round(max(summ[f"{run}|{a}|{pk}|{band}|{side}"]["floor_frac"]
                                                 for a in arms), 4),
                        frac_P_gt2_mean=round(float(np.mean(
                            [summ[f"{run}|{a}|{pk}|{band}|{side}"]["frac_P_gt2"] for a in arms])), 4),
                    )
    out["degenerate_and_band"] = deg
    out["mtimes_unchanged"] = all(os.path.getmtime(p) == m for p, m in mtimes.items())
    json.dump(out, open(os.path.join(HERE, "results_l176a.json"), "w"), indent=1)
    print("WROTE results_l176a.json; mtimes_unchanged =", out["mtimes_unchanged"])


if __name__ == "__main__":
    main()
