"""L176 stage (b1): the l169b2 arm-keyed CERT reader + the floor-4 twin pair
under the Guba composite.

ZERO rollouts. Reads l169b2/raw_l169b2.npz read-only. Every metric function is
IMPORTED from comp.py (stage (a)'s certified machinery) — nothing is
re-transcribed here (L85). Registered in PREREG.md ADDENDUM 2.
"""
import json
import os

import numpy as np

import comp as C

HERE = os.path.dirname(os.path.abspath(__file__))
BANC = os.path.dirname(HERE)

RUN = "l169b2"
NPZ = os.path.join(BANC, RUN, "raw_l169b2.npz")
RES = os.path.join(BANC, RUN, "results_l169b2.json")
PAIR = "Ti"          # derived from l169b2/PREREG.md line 54 (ADDENDUM 2)
ANCHORS = C.ANCHORS  # {801, 901}

CARRIER, TWIN, XOR_ARM = "f4wA", "f4tw", "f4ng"


def main():
    out = {"prereg": "banc/l176/PREREG.md (ADDENDUM 2)", "stage": "b1",
           "run": RUN, "pair": PAIR,
           "pair_identity_source": "l169b2/PREREG.md line 54: duty_07 per side "
                                   "on the Ti antagonist pair",
           "conventions_inherited_from": "banc/l176/comp.py (stage a)",
           "primary_cells": [CARRIER, TWIN], "xor_arm": XOR_ARM}

    mt = os.path.getmtime(NPZ)
    z = np.load(NPZ)
    r = json.load(open(RES))
    tbl = r["table"]
    arms = list(tbl.keys())
    rows = r["addendum_L_descriptive"]["rows"]
    seeds = sorted({int(k.rsplit("_", 1)[1]) for k in z.keys()
                    if k.startswith(f"{PAIR}_fR_{arms[0]}_")} - ANCHORS)
    out["arms"] = arms
    out["seeds"] = seeds
    out["n_seeds"] = len(seeds)
    assert len(seeds) == 16, seeds

    # ---------------- B1-CERT ----------------
    cert = {"checks": 0, "fail": [], "n_arms_table": len(arms),
            "n_arms_perseed": len(rows),
            "perseed_arms": sorted(rows.keys())}
    assert len(rows) == 5, f"ADDENDUM 2 registered 5 per-seed arms, got {len(rows)}"
    store = {}
    for a in arms:
        dL, dR, comp = [], [], {}
        for s in seeds:
            SL, SR, tr = C.s_arrays(z, a, s, PAIR)
            x, y = C.duty_from_S(SL, SR)
            dL.append(x)
            dR.append(y)
            ag, bg = C.PREF[PAIR]
            for band in C.BANDS:
                for side in ("L", "R"):
                    comp.setdefault((band, side), []).append(
                        C.comp_windows(tr[f"{ag}{side}"], tr[f"{bg}{side}"], band))
        dL, dR = np.array(dL), np.array(dR)
        got = dict(kL=int((dL >= .5).sum()), kR=int((dR >= .5).sum()),
                   meanL=round(float(dL.mean()), 3), meanR=round(float(dR.mean()), 3))
        want = tbl[a]
        for kk in ("kL", "kR", "meanL", "meanR"):
            cert["checks"] += 1
            if want.get(kk) != got[kk]:
                cert["fail"].append([a, kk, want.get(kk), got[kk]])
        if a in rows:                      # per-seed anchor (subset compare, L110)
            ps = rows[a]["perseedL"]
            assert len(ps) == len(seeds)
            for i, v in enumerate(ps):
                cert["checks"] += 1
                if float(v) != float(dL[i]):
                    cert["fail"].append([a, f"perseedL[{i}]", v, float(dL[i])])
        store[a] = dict(dL=dL, dR=dR, comp=comp)
        print(f"  cert {a}: {got} ({cert['checks']} checks, {len(cert['fail'])} fail)",
              flush=True)

    out["cert"] = dict(checks=cert["checks"], n_fail=len(cert["fail"]),
                       fail=cert["fail"][:20], passed=not cert["fail"],
                       n_arms_table=cert["n_arms_table"],
                       n_arms_perseed=cert["n_arms_perseed"],
                       perseed_arms=cert["perseed_arms"])
    print(f"B1-CERT {cert['checks']} checks, {len(cert['fail'])} fail", flush=True)
    if cert["fail"]:
        json.dump(out, open(os.path.join(HERE, "results_l176b1.json"), "w"), indent=1)
        raise SystemExit("B1-CERT FAILED — halting per ADDENDUM 2")

    def cmean(a, band, side, wset=C.PRIM_W, alpha=C.PRIM_ALPHA):
        return np.array([C.composite(c, wset, alpha).mean()
                         for c in store[a]["comp"][(band, side)]])

    # ---------------- summaries ----------------
    summ = {}
    for a in arms:
        for band in C.BANDS:
            for side in ("L", "R"):
                cs = store[a]["comp"][(band, side)]
                summ[f"{a}|{band}|{side}"] = dict(
                    comp=round(float(cmean(a, band, side).mean()), 4),
                    PLV=round(float(np.mean([c["PLV"].mean() for c in cs])), 4),
                    A=round(float(np.mean([c["A"].mean() for c in cs])), 4),
                    PH=round(float(np.mean([c["PH"].mean() for c in cs])), 4),
                    Pmean=round(float(np.mean([c["P"].mean() for c in cs])), 3),
                    frac_P_gt2=round(float(np.mean([(c["P"] > 2).mean() for c in cs])), 4),
                    g_mean=round(float(np.mean(
                        [np.exp(-C.PRIM_ALPHA * np.maximum(0, c["P"] - 2)).mean()
                         for c in cs])), 4),
                    floor_frac=round(float(np.mean([c["floor"].mean() for c in cs])), 4),
                    duty=round(float((store[a]["dL"] if side == "L"
                                      else store[a]["dR"]).mean()), 3),
                )
    out["summary"] = summ

    # ---------------- PRIMARY-b1 + XOR leg ----------------
    def paired(ca, tw, band, side, wset, al):
        cc, ct = cmean(ca, band, side, wset, al), cmean(tw, band, side, wset, al)
        d = cc - ct
        lo, hi = C.jack_ci(d)
        dut_c = float((store[ca]["dL"] if side == "L" else store[ca]["dR"]).mean())
        dut_t = float((store[tw]["dL"] if side == "L" else store[tw]["dR"]).mean())
        return dict(n=len(d),
                    mean_carrier=round(float(cc.mean()), 4),
                    mean_twin=round(float(ct.mean()), 4),
                    paired_mean=round(float(d.mean()), 4),
                    sign=int(np.sign(d.mean())), k_up=int((d > 0).sum()),
                    ci=[round(lo, 4), round(hi, 4)],
                    ci_excl_0=bool(lo > 0 or hi < 0),
                    duty_a=round(dut_c, 3), duty_b=round(dut_t, 3),
                    duty_sign=int(np.sign(dut_c - dut_t)),
                    sign_agrees_duty=bool(np.sign(d.mean()) == np.sign(dut_c - dut_t)
                                          and d.mean() != 0))

    prim, xleg = {}, {}
    for band in C.BANDS:
        for side in ("L", "R"):
            for wset in C.WEIGHT_SETS:
                for al in C.ALPHAS:
                    tag = f"{band}|{side}|{wset}|a{al}"
                    prim[tag] = paired(CARRIER, TWIN, band, side, wset, al)
                    xleg[tag] = paired(XOR_ARM, TWIN, band, side, wset, al)
    out["primary_b1"] = prim
    out["xor_leg"] = xleg
    out["xor_stored"] = r["legs"]["xor"]
    out["branch_stored"] = r["branch"]

    # ---------------- SECONDARY-b1 ----------------
    sec = {}
    for band in C.BANDS:
        for side in ("L", "R"):
            duty = [float((store[a]["dL"] if side == "L" else store[a]["dR"]).mean())
                    for a in arms]
            cv = [summ[f"{a}|{band}|{side}"]["comp"] for a in arms]
            sec[f"{band}|{side}"] = dict(n_arms=len(arms), arms=arms,
                                         rho=round(C.spearman(cv, duty), 4),
                                         duty=[round(v, 3) for v in duty], comp=cv)
    out["secondary_b1"] = sec

    # term-only ladders (which term carries the ordering)
    terms = {}
    for band in C.BANDS:
        for side in ("L", "R"):
            duty = [float((store[a]["dL"] if side == "L" else store[a]["dR"]).mean())
                    for a in arms]
            for t in ("A", "PLV", "PH"):
                vals = [summ[f"{a}|{band}|{side}"][t] for a in arms]
                terms[f"{band}|{side}|{t}"] = dict(rho=round(C.spearman(vals, duty), 4),
                                                   vals=vals)
    out["term_rho_b1"] = terms

    # ---------------- degenerate + band floor ----------------
    deg = {}
    for band in C.BANDS:
        for side in ("L", "R"):
            As = [summ[f"{a}|{band}|{side}"]["A"] for a in arms]
            PLs = [summ[f"{a}|{band}|{side}"]["PLV"] for a in arms]
            PHs = [summ[f"{a}|{band}|{side}"]["PH"] for a in arms]
            deg[f"{band}|{side}"] = dict(
                A_range=round(max(As) - min(As), 4),
                PLV_range=round(max(PLs) - min(PLs), 4),
                PH_range=round(max(PHs) - min(PHs), 4),
                degenerate=bool(max(As) - min(As) < 0.05),
                floor_frac_max=round(max(summ[f"{a}|{band}|{side}"]["floor_frac"]
                                         for a in arms), 4),
                frac_P_gt2_mean=round(float(np.mean(
                    [summ[f"{a}|{band}|{side}"]["frac_P_gt2"] for a in arms])), 4),
            )
    out["degenerate_and_band_b1"] = deg
    out["mtime_unchanged"] = os.path.getmtime(NPZ) == mt
    json.dump(out, open(os.path.join(HERE, "results_l176b1.json"), "w"), indent=1)
    print("WROTE results_l176b1.json; mtime_unchanged =", out["mtime_unchanged"])


if __name__ == "__main__":
    main()
