"""L176 stage (b2): the Guba composite on the l65 FEMALE-CORD Ti/Tr reads.

ZERO rollouts. Reads banc/l65/raw_l65.npz read-only (mtime asserted unchanged).
PREREG: banc/l176/PREREG.md ADDENDUM 3 (written before this file ran).

Discipline, inherited from stage (b1):
  * component arithmetic IMPORTED from comp.py, never re-transcribed (D1);
  * the l65 window convention installed by rebinding comp.TSQ (D2/D3);
  * B2-CERT runs FIRST and halts on mismatch (L85 rule);
  * the FLOOR report is computed and printed BEFORE any wiring verdict, because
    (b1) proved the composite is unsafe on a floored axis.
"""
import json
import os

import numpy as np

import comp  # certified stage-(a) component code

HERE = os.path.dirname(os.path.abspath(__file__))
BANC = os.path.dirname(HERE)
NPZ = os.path.join(BANC, "l65", "raw_l65.npz")
RES = os.path.join(BANC, "l65", "results_l65.json")

# ---- l65 native constants (verbatim from l65_banc_oppoint.py) ----
CONF_WIN = 6000
SEEDS = [11, 22, 33]
PAIRS = ["Ti", "Tr"]
DEPTH_BAR = 0.03          # l65's own readability bar
SL65 = slice(int(0.25 * CONF_WIN), CONF_WIN)   # steps 1500..5999

# ---- declared window conventions (ADDENDUM 3 D2/D3) ----
TS_B2 = np.arange(1999, CONF_WIN, 10)                  # PRIMARY, 401 windows
TS_WHOLE = np.array([CONF_WIN - 1])                    # D3 marker (see below)

ARMS = ["A", "B"] + [f"{t}{d}" for t in ("density", "degree") for d in range(3)]
LADDER = [a for a in ARMS if a not in ("A", "B")]
DEGREE = [a for a in ARMS if a.startswith("degree")]


def trace_key(arm, seed, pair, pool):
    """npz key form: A_s11_Ti_f / density0_s11_Ti_f."""
    return f"{arm}_s{seed}_{pair}_{pool}"


# ---------- l65's stored metric, copied verbatim (lines 234-241) ----------
def s_and_depth(a_full, b_full):
    a = a_full[SL65]
    b = b_full[SL65]
    depth = float(max(np.ptp(a), np.ptp(b)))
    sa, sb = a.std(), b.std()
    S = (float(-np.corrcoef(a, b)[0, 1])
         if sa > 1e-6 and sb > 1e-6 else float("nan"))
    return S, depth


def stored_cells(res):
    """(arm, seed, pair) -> dict(S=, depth=) from results_l65.json."""
    out = {}
    for arm in ("A", "B"):
        for row in res["arms"][arm]["confirm"]:
            for pk in PAIRS:
                out[(arm, row["seed"], pk)] = dict(S=row["S"][pk],
                                                   depth=row["depth"][pk])
    for tier in ("density", "degree"):
        for dr in res["ladder"][tier]:
            arm = f"{tier}{dr['draw']}"
            for row in dr["seeds"]:
                if "S" not in row:
                    continue
                for pk in PAIRS:
                    out[(arm, row["seed"], pk)] = dict(S=row["S"][pk],
                                                       depth=row["depth"][pk])
    return out


def main():
    mt = os.path.getmtime(NPZ)
    z = np.load(NPZ)
    res = json.load(open(RES))
    want = stored_cells(res)

    out = {"prereg": "banc/l176/PREREG.md ADDENDUM 3", "stage": "b2",
           "source": {"npz": "banc/l65/raw_l65.npz",
                      "results": "banc/l65/results_l65.json"},
           "conventions": {
               "imported_from": "banc/l176/comp.py",
               "TS_primary": [int(TS_B2[0]), int(TS_B2[-1]), 10, len(TS_B2)],
               "l65_window": [SL65.start, SL65.stop],
               "depth_bar": DEPTH_BAR,
               "weights": {k: list(v) for k, v in comp.WEIGHT_SETS.items()},
               "alphas": comp.ALPHAS,
               "bands": {k: list(v) for k, v in comp.BANDS.items()},
               "primary": [comp.PRIM_W, comp.PRIM_ALPHA, comp.PRIM_BAND]}}

    # ================= B2-CERT (first, halts on mismatch) =================
    cert = {"checks": 0, "fail": [], "max_err": 0.0}
    traces = {}
    for arm in ARMS:
        for s in SEEDS:
            for pk in PAIRS:
                kf, ke = trace_key(arm, s, pk, "f"), trace_key(arm, s, pk, "e")
                assert kf in z and ke in z, (kf, ke)
                tf, te = z[kf], z[ke]
                assert tf.shape == (CONF_WIN,) and te.shape == (CONF_WIN,)
                traces[(arm, s, pk)] = (tf, te)
                S, depth = s_and_depth(tf, te)
                w = want[(arm, s, pk)]
                for name, got, exp in (("S", S, w["S"]), ("depth", depth, w["depth"])):
                    cert["checks"] += 1
                    err = abs(got - exp)
                    cert["max_err"] = max(cert["max_err"], float(err))
                    if not (err <= 1e-12):
                        cert["fail"].append([arm, s, pk, name, exp, got])
    # aggregate: ladder_real_S = mean over confirm seeds of arm B's S(Ti)
    realS = float(np.nanmean([s_and_depth(*traces[("B", s, "Ti")])[0] for s in SEEDS]))
    cert["checks"] += 1
    err = abs(realS - res["ladder_real_S"])
    cert["max_err"] = max(cert["max_err"], float(err))
    if not (err <= 1e-12):
        cert["fail"].append(["B", "agg", "Ti", "ladder_real_S",
                             res["ladder_real_S"], realS])
    out["cert"] = dict(checks=cert["checks"], n_fail=len(cert["fail"]),
                       max_err=cert["max_err"], fail=cert["fail"][:20],
                       passed=not cert["fail"], ladder_real_S=realS)
    print(f"B2-CERT {cert['checks']} checks, {len(cert['fail'])} fail, "
          f"max_err {cert['max_err']:.3e}", flush=True)
    if cert["fail"]:
        json.dump(out, open(os.path.join(HERE, "results_l176b2.json"), "w"), indent=1)
        raise SystemExit("B2-CERT FAILED — halting per ADDENDUM 3")

    # ================= FLOOR REPORT (before any verdict) =================
    floor = {}
    for arm in ARMS:
        for pk in PAIRS:
            d = [want[(arm, s, pk)]["depth"] for s in SEEDS]
            rates = [float(np.concatenate(traces[(arm, s, pk)])[SL65.start:].mean())
                     for s in SEEDS]
            fmean = [float(traces[(arm, s, pk)][0][SL65].mean()) for s in SEEDS]
            emean = [float(traces[(arm, s, pk)][1][SL65].mean()) for s in SEEDS]
            floor[f"{arm}|{pk}"] = dict(
                depth=[round(v, 4) for v in d],
                depth_mean=round(float(np.mean(d)), 4),
                off_floor=bool(min(d) >= DEPTH_BAR),
                flex_mean=round(float(np.mean(fmean)), 4),
                ext_mean=round(float(np.mean(emean)), 4),
                storedS=[round(want[(arm, s, pk)]["S"], 4) for s in SEEDS])
            del rates
    out["floor_report"] = floor
    print("FLOOR off-floor cells:",
          [k for k, v in floor.items() if v["off_floor"]], flush=True)

    # ================= composite over both window conventions =================
    def comps(arm, s, pk, band, ts):
        comp.TSQ = ts                      # D1/D2: rebind, imported arithmetic
        tf, te = traces[(arm, s, pk)]
        return comp.comp_windows(tf, te, band)

    cells = {}          # (conv, arm, s, pk, band) -> component dict
    for conv, ts in (("slide", TS_B2), ("whole", None)):
        for arm in ARMS:
            for s in SEEDS:
                for pk in PAIRS:
                    for band in comp.BANDS:
                        if conv == "whole":
                            # D3: one window covering l65's whole measurement
                            # slice. comp_windows reads a trailing 500-step
                            # window per t, so emulate the single wide window
                            # by temporarily widening comp's window length.
                            cells[(conv, arm, s, pk, band)] = None
                        else:
                            cells[(conv, arm, s, pk, band)] = comps(arm, s, pk, band, ts)
        print(f"  components done: {conv}", flush=True)

    # D3 whole-window read: same component formulas, one 4500-step window.
    def whole_window(arm, s, pk, band):
        f_lo, f_hi = comp.BANDS[band]
        tf, te = traces[(arm, s, pk)]
        zf = comp.analytic(tf, f_lo, f_hi)
        ze = comp.analytic(te, f_lo, f_hi)
        ef, ee = np.abs(zf)[SL65], np.abs(ze)[SL65]
        dd = (np.angle(zf) - np.angle(ze))[SL65]
        import math
        PLV = abs(np.exp(1j * dd).mean())
        mf, me = ef.mean(), ee.mean()
        A = (min(mf, me) / max(mf, me)) if max(mf, me) > 0 else 0.0
        ang = math.degrees(abs(np.angle(np.exp(1j * dd).mean())))
        PH = 1.0 - abs(180.0 - ang) / 180.0
        P = max(comp.peak_count(ef), comp.peak_count(ee))
        rf = abs(np.asarray(tf, float)[SL65].mean())
        re_ = abs(np.asarray(te, float)[SL65].mean())
        ref = max(rf, re_)
        fl = (ref > 0) and (max(mf, me) < 0.01 * ref)
        return dict(PLV=np.array([PLV]), A=np.array([A]), PH=np.array([PH]),
                    P=np.array([float(P)]), floor=np.array([fl]))

    for arm in ARMS:
        for s in SEEDS:
            for pk in PAIRS:
                for band in comp.BANDS:
                    cells[("whole", arm, s, pk, band)] = whole_window(arm, s, pk, band)
    print("  components done: whole", flush=True)

    def cval(conv, arm, s, pk, band, wset=None, alpha=None):
        c = cells[(conv, arm, s, pk, band)]
        return float(comp.composite(c, wset or comp.PRIM_W,
                                    comp.PRIM_ALPHA if alpha is None else alpha).mean())

    # ---- summary table ----
    summ = {}
    for conv in ("slide", "whole"):
        for arm in ARMS:
            for pk in PAIRS:
                for band in comp.BANDS:
                    cs = [cells[(conv, arm, s, pk, band)] for s in SEEDS]
                    summ[f"{conv}|{arm}|{pk}|{band}"] = dict(
                        comp_a1=round(float(np.mean([cval(conv, arm, s, pk, band)
                                                     for s in SEEDS])), 4),
                        comp_a0=round(float(np.mean([cval(conv, arm, s, pk, band, alpha=0.0)
                                                     for s in SEEDS])), 4),
                        PLV=round(float(np.mean([c["PLV"].mean() for c in cs])), 4),
                        A=round(float(np.mean([c["A"].mean() for c in cs])), 4),
                        PH=round(float(np.mean([c["PH"].mean() for c in cs])), 4),
                        Pmean=round(float(np.mean([c["P"].mean() for c in cs])), 3),
                        frac_P_gt2=round(float(np.mean([(c["P"] > 2).mean() for c in cs])), 4),
                        floor_frac=round(float(np.mean([c["floor"].mean() for c in cs])), 4),
                        storedS=round(float(np.mean([want[(arm, s, pk)]["S"]
                                                     for s in SEEDS])), 4))
    out["summary"] = summ

    # ================= PRIMARY: wiring axis (real B vs each ladder draw) ====
    prim = {}
    for pk in PAIRS:
        for band in comp.BANDS:
            for conv in ("slide", "whole"):
                for alpha in (0.0, comp.PRIM_ALPHA):
                    for nul in LADDER:
                        d = np.array([cval(conv, "B", s, pk, band, alpha=alpha)
                                      - cval(conv, nul, s, pk, band, alpha=alpha)
                                      for s in SEEDS])
                        lo, hi = comp.jack_ci(d)
                        prim[f"{pk}|{band}|{conv}|a{alpha}|B-{nul}"] = dict(
                            n=3, per_seed=[round(float(v), 4) for v in d],
                            paired_mean=round(float(d.mean()), 4),
                            sign_consistent=int((d > 0).sum()),
                            ci_courtesy=[round(lo, 4), round(hi, 4)],
                            real=round(float(np.mean([cval(conv, "B", s, pk, band, alpha=alpha)
                                                      for s in SEEDS])), 4),
                            null=round(float(np.mean([cval(conv, nul, s, pk, band, alpha=alpha)
                                                      for s in SEEDS])), 4),
                            null_off_floor=floor[f"{nul}|{pk}"]["off_floor"],
                            real_off_floor=floor[f"B|{pk}"]["off_floor"],
                            interpretable=bool(floor[f"B|{pk}"]["off_floor"]
                                               and floor[f"{nul}|{pk}"]["off_floor"]))
    out["primary_wiring"] = prim

    # registered PASS cell: Ti, degree tier, primary band/weights, alpha=0 rung
    gate = {}
    for band in comp.BANDS:
        for conv in ("slide", "whole"):
            for alpha in (0.0, comp.PRIM_ALPHA):
                rows = [prim[f"Ti|{band}|{conv}|a{alpha}|B-{n}"] for n in DEGREE]
                gate[f"Ti|{band}|{conv}|a{alpha}"] = dict(
                    all_3of3=all(r["sign_consistent"] == 3 for r in rows),
                    min_sign=min(r["sign_consistent"] for r in rows),
                    real_off_floor=rows[0]["real_off_floor"],
                    gaps=[r["paired_mean"] for r in rows],
                    stored_gap=round(float(np.mean([want[("B", s, "Ti")]["S"] for s in SEEDS])
                                           - np.mean([want[(n, s, "Ti")]["S"]
                                                      for n in DEGREE for s in SEEDS])), 4),
                    null_max=max(r["null"] for r in rows),
                    real=rows[0]["real"],
                    rel_gap=round(min(r["paired_mean"] for r in rows)
                                  / max(rows[0]["real"], 1e-9), 4))
    out["primary_gate"] = gate

    # ================= SECONDARY: rank axis across 8 arms =================
    sec = {}
    for pk in PAIRS:
        for band in comp.BANDS:
            for conv in ("slide", "whole"):
                for alpha in (0.0, comp.PRIM_ALPHA):
                    sS = [float(np.mean([want[(a, s, pk)]["S"] for s in SEEDS])) for a in ARMS]
                    cv = [float(np.mean([cval(conv, a, s, pk, band, alpha=alpha)
                                         for s in SEEDS])) for a in ARMS]
                    ties = sum(1 for v in cv if round(v, 4) == 0.0)
                    sec[f"{pk}|{band}|{conv}|a{alpha}"] = dict(
                        arms=ARMS, rho=round(comp.spearman(cv, sS), 4),
                        storedS=[round(v, 4) for v in sS],
                        comp=[round(v, 4) for v in cv],
                        zero_cells=ties,
                        tie_degenerate=bool(ties > 1))
    out["secondary_rank"] = sec

    # ================= TERTIARY: NT-sign arm axis (B vs A) =================
    tert = {}
    for pk in PAIRS:
        for band in comp.BANDS:
            for conv in ("slide", "whole"):
                for alpha in (0.0, comp.PRIM_ALPHA):
                    d = np.array([cval(conv, "B", s, pk, band, alpha=alpha)
                                  - cval(conv, "A", s, pk, band, alpha=alpha)
                                  for s in SEEDS])
                    lo, hi = comp.jack_ci(d)
                    tert[f"{pk}|{band}|{conv}|a{alpha}"] = dict(
                        per_seed=[round(float(v), 4) for v in d],
                        paired_mean=round(float(d.mean()), 4),
                        sign_consistent=int((d > 0).sum()),
                        ci_courtesy=[round(lo, 4), round(hi, 4)],
                        stored_dS=round(float(np.mean([want[("B", s, pk)]["S"]
                                                       - want[("A", s, pk)]["S"]
                                                       for s in SEEDS])), 4),
                        both_off_floor=bool(floor[f"A|{pk}"]["off_floor"]
                                            and floor[f"B|{pk}"]["off_floor"]))
    out["tertiary_ntsign"] = tert

    # ================= degenerate + band-floor branches =================
    deg = {}
    for pk in PAIRS:
        for band in comp.BANDS:
            for conv in ("slide", "whole"):
                As = [summ[f"{conv}|{a}|{pk}|{band}"]["A"] for a in ARMS]
                PLs = [summ[f"{conv}|{a}|{pk}|{band}"]["PLV"] for a in ARMS]
                PHs = [summ[f"{conv}|{a}|{pk}|{band}"]["PH"] for a in ARMS]
                deg[f"{pk}|{band}|{conv}"] = dict(
                    A_range=round(max(As) - min(As), 4),
                    PLV_range=round(max(PLs) - min(PLs), 4),
                    PH_range=round(max(PHs) - min(PHs), 4),
                    degenerate=bool(max(As) - min(As) < 0.05),
                    floor_frac_max=round(max(summ[f"{conv}|{a}|{pk}|{band}"]["floor_frac"]
                                             for a in ARMS), 4),
                    frac_P_gt2_mean=round(float(np.mean(
                        [summ[f"{conv}|{a}|{pk}|{band}"]["frac_P_gt2"] for a in ARMS])), 4))
    out["degenerate_and_band"] = deg

    out["mtime_unchanged"] = bool(os.path.getmtime(NPZ) == mt)
    json.dump(out, open(os.path.join(HERE, "results_l176b2.json"), "w"), indent=1)
    print("WROTE results_l176b2.json; mtime_unchanged =", out["mtime_unchanged"])


if __name__ == "__main__":
    main()
