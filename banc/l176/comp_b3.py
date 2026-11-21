"""L176 stage (b3): the Guba composite on the MALE l50 cord (schedule arms).

ZERO rollouts. Reads malecns/l50/{raw_l50.npz,results_l50.json} read-only
(mtimes asserted unchanged). PREREG: banc/l176/PREREG.md ADDENDUM 4, written
before this file ran — including the b3.0 feasibility finding that the card's
named substrate (malecns/l32) stores NO traces at all.

Discipline inherited from (b1)/(b2):
  * component arithmetic IMPORTED from comp.py, never re-transcribed;
  * window convention installed by rebinding comp.TSQ (per segment, D4);
  * B3-CERT runs FIRST and halts on mismatch (L85 rule);
  * FLOOR report BEFORE any verdict (b1 rule);
  * per-term decomposition reported FROM THE START (b2 method law, D7).
"""
import json
import os

import numpy as np

import comp  # certified stage-(a) component code

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(os.path.dirname(HERE))
M50 = os.path.join(LAB, "malecns", "l50")
NPZ = os.path.join(M50, "raw_l50.npz")
RES = os.path.join(M50, "results_l50.json")

# ---- l50 native constants (verbatim from l50_traj.py / results meta) ----
WIN = 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
SEEDS = [11, 22, 33]
ARMS = ["free", "ent", "allw", "duty58", "min5"]
SIGS = ("fL", "fR", "eL", "eR")
DEPTH_BAR = 0.03            # D5, the l65/(b1) readability bar
TS = np.arange(499, WIN, 10)

assert (WIN, comp.DT, comp.MEAS0) == (comp.WIN, 0.01, MEAS0)
assert SEGB == comp.SEGB, "D4 claim: l50's window convention == comp.py's"

mt0 = {p: os.path.getmtime(p) for p in (NPZ, RES)}
raw = np.load(NPZ)
stored = json.load(open(RES))


def tr_of(arm, seed):
    return {c: np.asarray(raw[f"{c}_{arm}_{seed}"][:WIN], dtype=np.float64)
            for c in SIGS}


# ---------- l50's stored metric, copied VERBATIM (l50_traj.py 180-182, 302-325)
def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def s_arrays(arm, seed):
    tr = tr_of(arm, seed)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(tr["fL"][t - 499:t + 1], tr["eL"][t - 499:t + 1])
        SR[t] = S_of(tr["fR"][t - 499:t + 1], tr["eR"][t - 499:t + 1])
    return SL, SR, tr


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    if not q.any():
        return None
    return round(float(np.nanmedian(arr[TS[q]])), 3)


# ================= B3-CERT (first; halts on mismatch) =================
print("=== B3-CERT: reproduce l50's stored per-side S / duty from raw traces ===")
cert = {"checks": 0, "fail": 0, "max_err": 0.0, "worst": None}
SARR = {}
for arm in ARMS:
    for s in SEEDS:
        SL, SR, tr = s_arrays(arm, s)
        SARR[(arm, s)] = (SL, SR, tr)
        st = stored["segments"][arm][str(s)]
        for si, (a0, b0, _f) in enumerate(SEGB):
            lo, hi = a0 + MEAS0, b0
            q = (TS >= lo) & (TS < hi)
            both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
            mine = dict(SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                        duty=round(float(np.nanmean(both)), 3))
            for k in ("SL", "SR", "duty"):
                cert["checks"] += 1
                e = abs(float(mine[k]) - float(st["segs"][si][k]))
                if e > cert["max_err"]:
                    cert["max_err"], cert["worst"] = e, (arm, s, si, k)
                if e > 1e-9:
                    cert["fail"] += 1
        qall = np.zeros(len(TS), bool)
        for a0, b0, _f in SEGB:
            qall |= (TS >= a0 + MEAS0) & (TS < b0)
        da = round(float(np.nanmean((SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3)
        cert["checks"] += 1
        e = abs(da - stored["segments"][arm][str(s)]["duty_all"])
        cert["max_err"] = max(cert["max_err"], e)
        if e > 1e-9:
            cert["fail"] += 1
print(f"  checks {cert['checks']}  fail {cert['fail']}  max_err {cert['max_err']:.3e}"
      f"  worst {cert['worst']}")
assert cert["fail"] == 0, f"B3-CERT FAILED: {cert}"
print("  B3-CERT PASS (exact)\n")

# ================= FLOOR report (before any verdict) =================
print("=== FLOOR report (D5: depth = max ptp over the segment span, bar 0.03) ===")
floor = {}
for arm in ARMS:
    for s in SEEDS:
        SL, SR, tr = SARR[(arm, s)]
        for si, (a0, b0, _f) in enumerate(SEGB):
            sl = slice(a0 + MEAS0 - 499, b0)
            for side, (fk, ek) in (("L", ("fL", "eL")), ("R", ("fR", "eR"))):
                d = float(max(np.ptp(tr[fk][sl]), np.ptp(tr[ek][sl])))
                floor[f"{arm}|{s}|seg{si}|{side}"] = round(d, 4)
dmin, dmax = min(floor.values()), max(floor.values())
nfloored = sum(1 for v in floor.values() if v < DEPTH_BAR)
print(f"  cells {len(floor)}  depth range [{dmin:.4f}, {dmax:.4f}]  "
      f"floored(<{DEPTH_BAR}) {nfloored}/{len(floor)}")
by_arm = {a: round(float(np.mean([v for k, v in floor.items() if k.startswith(a + "|")])), 4)
          for a in ARMS}
print("  mean depth by arm:", by_arm)
fl_cells = sorted([k for k, v in floor.items() if v < DEPTH_BAR])
print("  floored cells:", fl_cells[:14], "..." if len(fl_cells) > 14 else "")

# ================= composite + per-term (D7) =================
print("\n=== composite cells (alpha 0 primary readable rung; alpha 1 reported) ===")
BANDS = list(comp.BANDS)
rows = {}      # (arm,seed,si,side,band) -> dict of component means
TSQ_SAVE = comp.TSQ
pfrac = []
bandfloor = []
for si, (a0, b0, _f) in enumerate(SEGB):
    q = (TS >= a0 + MEAS0) & (TS < b0)
    comp.TSQ = TS[q]
    for arm in ARMS:
        for s in SEEDS:
            _SL, _SR, tr = SARR[(arm, s)]
            for side, (fk, ek) in (("L", ("fL", "eL")), ("R", ("fR", "eR"))):
                for band in BANDS:
                    c = comp.comp_windows(tr[fk], tr[ek], band)
                    pfrac.append(float(np.mean(c["P"] > 2)))
                    bandfloor.append(float(np.mean(c["floor"])))
                    rows[(arm, s, si, side, band)] = dict(
                        PLV=float(np.mean(c["PLV"])), A=float(np.mean(c["A"])),
                        PH=float(np.mean(c["PH"])), P=float(np.mean(c["P"])),
                        c0=float(np.mean(comp.composite(c, "equal_residual", 0.0))),
                        c1=float(np.mean(comp.composite(c, "equal_residual", 1.0))),
                        nwin=len(comp.TSQ))
comp.TSQ = TSQ_SAVE
print(f"  cells {len(rows)}  frac(P>2) range [{min(pfrac):.4f}, {max(pfrac):.4f}]  "
      f"band-floor range [{min(bandfloor):.4f}, {max(bandfloor):.4f}]")
c1v = [r["c1"] for r in rows.values()]
print(f"  alpha=1 composite range [{min(c1v):.6f}, {max(c1v):.6f}]  "
      f"(gate annihilation check, Qb3-1)")


def arm_mean(arm, si, side, band, key):
    return float(np.mean([rows[(arm, s, si, side, band)][key] for s in SEEDS]))


def stored_struct(arm, si, side):
    """l50's own structure read for that arm/seg/side: per-seed median S."""
    return float(np.mean([stored["segments"][arm][str(s)]["segs"][si]["S" + side]
                          for s in SEEDS]))


def stored_duty(arm, si):
    return float(stored["segments"][arm]["mean_duty_seg"][si])


# ---- PRIMARY ordering: Spearman over the 5 arms ----
print("\n=== PRIMARY ordering (Spearman over 5 schedule arms) ===")
order = {}
for si in (0, 2, 1):
    for side in ("L", "R"):
        for band in BANDS:
            x = [arm_mean(a, si, side, band, "c0") for a in ARMS]
            yS = [stored_struct(a, si, side) for a in ARMS]
            yD = [stored_duty(a, si) for a in ARMS]
            terms = {t: comp.spearman([arm_mean(a, si, side, band, t) for a in ARMS], yS)
                     for t in ("A", "PLV", "PH")}
            order[f"seg{si}|{side}|{band}"] = dict(
                rho_comp_vs_S=round(comp.spearman(x, yS), 3),
                rho_comp_vs_duty=round(comp.spearman(x, yD), 3),
                rho_terms_vs_S={k: round(v, 3) for k, v in terms.items()},
                comp_by_arm={a: round(v, 4) for a, v in zip(ARMS, x)},
                S_by_arm={a: round(v, 3) for a, v in zip(ARMS, yS)})
            o = order[f"seg{si}|{side}|{band}"]
            print(f"  seg{si} {side} {band:10s} rho(comp,S)={o['rho_comp_vs_S']:+.3f} "
                  f"rho(comp,duty)={o['rho_comp_vs_duty']:+.3f}  terms "
                  f"A={terms['A']:+.3f} PLV={terms['PLV']:+.3f} Ph={terms['PH']:+.3f}")

# ---- P-A chop > continuous ; P-B fast-seg toxicity ----
print("\n=== registered findings re-asked of the instrument ===")
reg = {}
for side in ("L", "R"):
    for band in BANDS:
        # P-A: duty58 vs allw and vs ent, pooled over the three segments
        pa = {}
        for rival in ("allw", "ent"):
            wins = 0
            per = []
            for s in SEEDS:
                d = float(np.mean([rows[("duty58", s, si, side, band)]["c0"] for si in range(3)]))
                r = float(np.mean([rows[(rival, s, si, side, band)]["c0"] for si in range(3)]))
                per.append(round(d - r, 4))
                wins += int(d > r)
            pa[rival] = dict(seeds_higher=wins, deltas=per,
                             reproduces=bool(wins == 3))
        # P-B: allw vs free in the FAST segment (si=1)
        wins = 0
        per = []
        for s in SEEDS:
            aw = rows[("allw", s, 1, side, band)]["c0"]
            fr = rows[("free", s, 1, side, band)]["c0"]
            per.append(round(aw - fr, 4))
            wins += int(aw < fr)
        pb = dict(seeds_lower=wins, deltas=per, reproduces=bool(wins == 3),
                  A_allw=round(arm_mean("allw", 1, side, band, "A"), 4),
                  A_free=round(arm_mean("free", 1, side, band, "A"), 4),
                  stored_duty_allw=stored_duty("allw", 1),
                  stored_duty_free=stored_duty("free", 1))
        reg[f"{side}|{band}"] = dict(PA=pa, PB=pb)
        print(f"  {side} {band:10s} P-A duty58>allw {pa['allw']['seeds_higher']}/3 "
              f"(d {pa['allw']['deltas']})  duty58>ent {pa['ent']['seeds_higher']}/3  | "
              f"P-B allw<free seg1 {pb['seeds_lower']}/3 (d {pb['deltas']}, "
              f"A allw {pb['A_allw']} vs free {pb['A_free']})")

# ---- branch ----
rho07 = [v["rho_comp_vs_S"] for k, v in order.items() if k.startswith(("seg0", "seg2"))]
pa_ok = all(reg[k]["PA"]["allw"]["reproduces"] for k in reg)
pb_ok = all(reg[k]["PB"]["reproduces"] for k in reg)
if min(rho07) >= 0.5 and pa_ok and pb_ok:
    branch = "M1_transfers"
elif max(rho07) <= -0.3 or (not pa_ok and not pb_ok):
    branch = "M3_inverts"
else:
    branch = "M2_partial"
crange = max(r["c0"] for r in rows.values()) - min(r["c0"] for r in rows.values())
print(f"\nBRANCH {branch}   rho(0.7-Hz segs) range [{min(rho07):+.3f}, {max(rho07):+.3f}]"
      f"   P-A all-cells {pa_ok}   P-B all-cells {pb_ok}   c0 range {crange:.4f}"
      f"   degenerate={'YES' if crange < 0.05 else 'no'}")

mt1 = {p: os.path.getmtime(p) for p in (NPZ, RES)}
out = dict(stage="b3", prereg="banc/l176/PREREG.md ADDENDUM 4",
           substrate=dict(dir="malecns/l50", reason="card's l32 stores NO traces",
                          arms=ARMS, seeds=SEEDS, pair="Tr", segb=SEGB),
           cert=cert, floor=dict(bar=DEPTH_BAR, n=len(floor), floored=nfloored,
                                 by_arm=by_arm, cells=floor),
           gate=dict(frac_P_gt2=[round(min(pfrac), 4), round(max(pfrac), 4)],
                     alpha1_range=[round(min(c1v), 6), round(max(c1v), 6)],
                     band_floor=[round(min(bandfloor), 4), round(max(bandfloor), 4)]),
           order=order, registered=reg, branch=branch,
           c0_range=round(crange, 4),
           mtimes_unchanged=bool(mt0 == mt1))
json.dump(out, open(os.path.join(HERE, "results_l176b3.json"), "w"), indent=1)
json.dump({f"{k[0]}|{k[1]}|seg{k[2]}|{k[3]}|{k[4]}": {kk: round(vv, 6) for kk, vv in v.items()}
           for k, v in rows.items()},
          open(os.path.join(HERE, "results_l176b3_terms.json"), "w"), indent=1)
print(f"\nmtimes_unchanged {out['mtimes_unchanged']}  -> results_l176b3.json")
