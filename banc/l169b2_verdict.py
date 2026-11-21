"""L169b2 verdict: the FLOOR-4 dynamic arm (stage b2).

Helper code VERBATIM l169_verdict.py (L85 cert rule: my copy is certified
against l169's STORED B35 table for the shared arms BEFORE any B36 value
is read). PREREG l169b2/PREREG.md registered the arms, the classifiers and
the G1-G4 branches before the run.
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


_SM = {}


def s_arrays(raw, a, s, pk):
    key = (id(raw), a, s, pk)
    if key not in _SM:
        ag, bg = PREF[pk]
        tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN]
              for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(tr[f"{ag}L"][t - 499:t + 1], tr[f"{bg}L"][t - 499:t + 1])
            SR[t] = S_of(tr[f"{ag}R"][t - 499:t + 1], tr[f"{bg}R"][t - 499:t + 1])
        _SM[key] = (SL, SR)
    return _SM[key]


def duty_seeds(raw, a, seeds, pk):
    """Rounded per-seed duty values (the l109/l111/l113 rounding-path atom)."""
    L, R = [], []
    for s in seeds:
        SL, SR = s_arrays(raw, a, s, pk)
        q07 = np.zeros(len(TS), bool)
        for a0, b0, f in SEGB:
            if f == 0.7:
                q07 |= (TS >= a0 + MEAS0) & (TS < b0)
        L.append(round(float(np.nanmean(SL[TS[q07]] >= .25)), 3))
        R.append(round(float(np.nanmean(SR[TS[q07]] >= .25)), 3))
    return np.array(L), np.array(R)


def side_k(raw, a, seeds, pk):
    L, R = duty_seeds(raw, a, seeds, pk)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


def _notsuper(t):
    """PREREG control form: kR <= 8 and meanR <= .50."""
    return bool(t["kR"] <= 8 and t["meanR"] <= .50)


B36 = list(range(3449, 3465))
B35 = list(range(3417, 3433))
F4 = ("f4wA", "f4ng", "f4tw")
INHERIT = ("full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
           "eMotBot5", "wAgN", "n25gW")

z = np.load("l169b2/raw_l169b2.npz")
z169 = np.load("l169/raw_l169.npz")
A = json.load(open("l169b2/anchors_run.json"))
R169 = json.load(open("l169/results_l169.json"))

# ---------------- CERT-0: the anchors the run itself measured ----------------
cert = dict(fc169_pass=A["fc169_pass"], fc169_max=A["fc169_max"],
            ntf4_pass=A["ntf4_pass"], ntf4_min=min(A["ntf4"].values()),
            c0a150_pass=A["c0a150_pass"], fc144_pass=A["fc144_pass"],
            fc145_pass=A["fc145_pass"],
            g_cutwA_exact=A["g_cutwA_stored_exact"],
            g_cutng25_exact=A["g_cutng25_stored_exact"],
            g_emottop5_exact=A["g_emottop5_stored_exact"],
            g_emotbot5_exact=A["g_emotbot5_stored_exact"],
            paf4_ok=A["paf4_ok"])
print("---- CERT-0 (run-side anchors) ----")
for k, v in cert.items():
    print(f"  {k:22s} {v}")
CERT0 = bool(cert["fc169_pass"] and cert["ntf4_pass"]
             and cert["g_cutwA_exact"] and cert["g_cutng25_exact"]
             and cert["g_emottop5_exact"] and cert["g_emotbot5_exact"])
print(f"CERT-0 (CERT-1 chain + CERT-2 subset + C0-NT): "
      f"{'GREEN' if CERT0 else 'RED'}")

# ---------------- CERT-METRIC: my helper copy vs l169's STORED B35 ----------
# (L85: certify the metric machinery on the PRIOR run's stored verdict
# before reading any new value.)
cm = {}
for key, arm in (("24", "cutwA"), ("wAgN", "wAgN"), ("n25gW", "n25gW")):
    t = side_k(z169, arm, B35, "Ti")
    st = R169["cls"][key]
    cm[arm] = dict(mine=t, stored={k: st[k] for k in
                                   ("meanR", "kR", "meanL", "kL")})
    for f in ("meanR", "kR", "meanL", "kL"):
        assert t[f] == st[f], ("CERT-METRIC FAIL", arm, f, t[f], st[f])
print("CERT-METRIC GREEN: helper copy reproduces l169 stored B35 cells "
      "(cutwA / wAgN / n25gW, 4 fields each) EXACTLY")

# ---------------- the B36 table ----------------
table, cls = {}, {}
for a in F4 + ("full", "cutwA", "cutng25"):
    t = side_k(z, a, B36, "Ti")
    lbR, ubR = wilson(t["kR"], len(B36))
    lbL, ubL = wilson(t["kL"], len(B36))
    cls[a] = dict(arm=a, **t, lbR=lbR, ubR=ubR, lbL=lbL, ubL=ubL,
                  g=float(z[f"g_{a}"]) if f"g_{a}" in z.files else None,
                  n=int(A["f4_n"][a]) if a in F4 else None,
                  edges=int(A["f4_edges"][a]) if a in F4 else None,
                  super=_super(t), partial=_partial(t), notsuper=_notsuper(t))
    table[a] = t
print("\n---- B36 Ti per-side duty (n=16) ----")
for a in F4 + ("full", "cutwA", "cutng25"):
    c = cls[a]
    gs = f"g {c['g']:.9f}" if c["g"] is not None else "g (stored)"
    print(f"{a:9s} {gs} | meanR {c['meanR']:.3f} kR {c['kR']:2d}/16 "
          f"[{c['lbR']:.3f},{c['ubR']:.3f}] | meanL {c['meanL']:.3f} "
          f"kL {c['kL']:2d}/16 | SUPER {c['super']} PARTIAL {c['partial']} "
          f"NOTSUPER {c['notsuper']}")

# paired legs within B36 (same seeds, same noise stream)
legs = {}
_, R_wA4 = duty_seeds(z, "f4wA", B36, "Ti")
for a in ("f4ng", "f4tw"):
    _, R_a = duty_seeds(z, a, B36, "Ti")
    d = R_a - R_wA4
    legs[a] = dict(mean_paired_dR_vs_f4wA=round(float(d.mean()), 3),
                   n_up=int((d > 0).sum()), n_down=int((d < 0).sum()))
    print(f"paired {a} vs f4wA: dR {legs[a]['mean_paired_dR_vs_f4wA']:+.3f} "
          f"up {legs[a]['n_up']}/16 down {legs[a]['n_down']}/16")
_, R_ng4 = duty_seeds(z, "f4ng", B36, "Ti")
_, R_tw4 = duty_seeds(z, "f4tw", B36, "Ti")
d_xor = R_ng4 - R_tw4
legs["xor"] = dict(mean_paired_dR_ng_minus_tw=round(float(d_xor.mean()), 3),
                   n_up=int((d_xor > 0).sum()), n_down=int((d_xor < 0).sum()))
print(f"paired f4ng vs f4tw (the XOR leg): "
      f"dR {legs['xor']['mean_paired_dR_ng_minus_tw']:+.3f} "
      f"up {legs['xor']['n_up']}/16 down {legs['xor']['n_down']}/16")

# ---------------- registered branches ----------------
vac = bool(cls["f4wA"]["super"])          # degenerate-XOR guard (L55 class)
g1 = bool(cls["f4ng"]["super"] and cls["f4wA"]["notsuper"]
          and cls["f4tw"]["notsuper"])
g2 = bool(not cls["f4ng"]["super"])
g3 = bool(cls["f4ng"]["super"] and cls["f4tw"]["super"])
branch = ("G1_cliff_survives_floor4" if g1 else
          "G3_position_route" if g3 else
          "G2_no_transfer" if g2 else "G4_mixed")
if vac:
    branch = "G4_mixed"
print(f"\nBRANCH: {branch} (vacuous-XOR guard fired: {vac})")
print(f"  legs: f4ng super {cls['f4ng']['super']} | f4wA notsuper "
      f"{cls['f4wA']['notsuper']} | f4tw notsuper {cls['f4tw']['notsuper']}")

out = dict(
    prereg="l169b2/PREREG.md",
    design="L169 stage (b2): the floor-4 DYNAMIC arm. Closure node set "
           "VERBATIM, edges filtered to pair-level summed syn_count >= 4 "
           "(the stored l146 ladder convention), cut at the f4-re-derived "
           "window: f4wA = ng4[:20] (carrier intact), f4ng = ng4[:21] "
           "(carrier DNp33-L gi 1110 at f4 rank 21), f4tw = ng4[:20] + the "
           "f4 mass-twin gi 290 (rank 22, mass gap 2.4e-05). Fresh per-arm "
           "af-matched bisects. ONE batch, n=16.",
    batch="B36", seeds=B36, n_seeds=len(B36),
    cert=cert, cert0=CERT0, cert_metric=cm,
    floor=int(z["floor"]), K4=int(z["K4"]),
    f4_twin_gi=int(z["f4_twin_gi"][0]),
    gains={a: float(z[f"g_{a}"]) for a in F4},
    f4_stairs=A["f4_stairs"], f4_band_ok=A["f4_band_ok"],
    f4_n=A["f4_n"], f4_edges=A["f4_edges"], paf4=A["paf4"],
    table=cls, legs=legs,
    vacuous_xor_guard=vac, g1=g1, g2=g2, g3=g3, branch=branch)
json.dump(out, open("l169b2/results_l169b2.json", "w"), indent=1)
print("\nwrote l169b2/results_l169b2.json")
