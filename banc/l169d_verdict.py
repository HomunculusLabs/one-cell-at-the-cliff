"""L169d verdict: the XOR-pair GAIN-SWAP 2x2 (stage d).

Helper code VERBATIM-SLICED from l169c2_verdict.py by
l169d_verdict_build.py (L85 cert rule: the copy is certified against
l169c2's STORED B37 table for the shared arms BEFORE any B38 value is
read). PREREG l169d/PREREG.md registered the arms, the classifiers and
the E0/E1/E2/E3 branches — with explicit precedence — before the run.
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

B38 = list(range(3513, 3529))
B37 = list(range(3481, 3497))
D_SWAP = ("p25gN", "n25gP")
XOR = ("cutng25", "cutng25p")
BASEROWS = ("full", "cutwA")
ROWS = XOR + D_SWAP + BASEROWS

z = np.load("l169d/raw_l169d.npz")
zc2 = np.load("l169c2/raw_l169c2.npz")
A = json.load(open("l169d/anchors_run.json"))
RC2 = json.load(open("l169c2/results_l169c2.json"))
R135 = json.load(open("l135/results_l135.json"))

# ---------------- CERT-0: the anchors the run itself measured ----------------
cert = dict(fc169c2_pass=A["fc169c2_pass"], fc169c2_max=A["fc169c2_max"],
            ntd_pass=A["ntd_pass"], ntd_min=min(A["ntd"].values()),
            c0a150_pass=A["c0a150_pass"], c0a150_max=A["c0a150_max"],
            fc169b2_pass=A["fc169b2_pass"], fc169_pass=A["fc169_pass"],
            fc144_pass=A["fc144_pass"], fc145_pass=A["fc145_pass"],
            ntf4_pass=A["ntf4_pass"], ntc2_pass=A["ntc2_pass"],
            nt_pass=A["nt_pass"],
            g_cutwA_exact=A["g_cutwA_stored_exact"],
            g_cutng25_exact=A["g_cutng25_stored_exact"],
            g_cutng25p_exact=A["g_cutng25p_stored_exact"],
            g_emottop5_exact=A["g_emottop5_stored_exact"],
            g_emotbot5_exact=A["g_emotbot5_stored_exact"],
            d_stair=A["d_stair"], d_band_ok=A["d_band_ok"],
            pafd_ok=A["pafd_ok"], pafd_nup=A["pafd_nup"],
            pafd_ndn=A["pafd_ndn"], d_n=A["d_n"], d_edges=A["d_edges"])
print("---- CERT-0 (run-side anchors) ----")
for k, v in cert.items():
    print(f"  {k:22s} {v}")
CERT0 = bool(cert["fc169c2_pass"] and cert["ntd_pass"]
             and cert["c0a150_pass"] and cert["fc169b2_pass"]
             and cert["fc169_pass"] and cert["g_cutwA_exact"]
             and cert["g_cutng25_exact"] and cert["g_cutng25p_exact"]
             and cert["g_emottop5_exact"] and cert["g_emotbot5_exact"])
print(f"CERT-0 (CERT-1 FC-169C2 + CERT-2 C0A-150/5-arm + CERT-3 bisects "
      f"+ C0-NT(d)): {'GREEN' if CERT0 else 'RED'}")
# structural pins (re-read, not re-derived): the two swap arms must BE
# their own-gain twins' graphs (object identity was asserted in-run; here
# the node counts and edge counts must match exactly).
assert cert["d_n"]["p25gN"] == cert["d_n"]["cutng25p"], cert["d_n"]
assert cert["d_edges"]["p25gN"] == cert["d_edges"]["cutng25p"], cert["d_edges"]
print("structural pins: p25gN graph == cutng25p graph "
      f"(n {cert['d_n']['p25gN']:,} | edges {cert['d_edges']['p25gN']:,})")

# ---------------- CERT-METRIC: my helper copy vs l169c2's STORED B37 --------
cm = {}
for arm in ("rew1", "rew2", "rew3", "hom", "cutwA", "cutng25"):
    t = side_k(zc2, arm, B37, "Ti")
    st = RC2["table"][arm]
    cm[arm] = dict(mine=t, stored={k: st[k] for k in
                                   ("meanR", "kR", "meanL", "kL")})
    for f in ("meanR", "kR", "meanL", "kL"):
        assert t[f] == st[f], ("CERT-METRIC FAIL", arm, f, t[f], st[f])
print("CERT-METRIC GREEN: helper copy reproduces l169c2 stored B37 cells "
      "(rew1 / rew2 / rew3 / hom / cutwA / cutng25, 4 fields each) EXACTLY")

# ---------------- the B38 table ----------------
cls = {}
for a in ROWS:
    t = side_k(z, a, B38, "Ti")
    lbR, ubR = wilson(t["kR"], len(B38))
    lbL, ubL = wilson(t["kL"], len(B38))
    cls[a] = dict(arm=a, **t, lbR=lbR, ubR=ubR, lbL=lbL, ubL=ubL,
                  g=float(z[f"g_{a}"]) if f"g_{a}" in z.files else None,
                  super=_super(t), partial=_partial(t), notsuper=_notsuper(t))
print("\n---- B38 Ti per-side duty (n=16) ----")
for a in ROWS:
    c = cls[a]
    gs = f"g {c['g']:.9f}" if c["g"] is not None else "g (stored)"
    print(f"{a:9s} {gs} | meanR {c['meanR']:.3f} kR {c['kR']:2d}/16 "
          f"[{c['lbR']:.3f},{c['ubR']:.3f}] | meanL {c['meanL']:.3f} "
          f"kL {c['kL']:2d}/16 | SUPER {c['super']} PARTIAL {c['partial']} "
          f"NOTSUPER {c['notsuper']}")

# ---------------- paired legs within B38 (same seeds, same noise) ----------
legs = {}
_, R_ng = duty_seeds(z, "cutng25", B38, "Ti")
_, R_tw = duty_seeds(z, "cutng25p", B38, "Ti")
_, R_wA = duty_seeds(z, "cutwA", B38, "Ti")
_, R_pg = duty_seeds(z, "p25gN", B38, "Ti")
_, R_nP = duty_seeds(z, "n25gP", B38, "Ti")


def leg(name, a, b):
    d = a - b
    legs[name] = dict(mean_paired_dR=round(float(d.mean()), 3),
                      n_up=int((d > 0).sum()), n_down=int((d < 0).sum()))
    print(f"paired {name}: dR {legs[name]['mean_paired_dR']:+.3f} "
          f"up {legs[name]['n_up']}/16 down {legs[name]['n_down']}/16")


leg("p25gN_minus_cutng25p", R_pg, R_tw)   # twin graph, gain swapped UP
leg("n25gP_minus_cutng25", R_nP, R_ng)    # carrier graph, gain swapped DOWN
leg("cutng25_minus_cutng25p", R_ng, R_tw)  # the XOR identity contrast
leg("cutng25_minus_cutwA", R_ng, R_wA)    # the carrier-removal step
leg("cutng25p_minus_cutwA", R_tw, R_wA)   # the twin-removal step
leg("p25gN_minus_cutng25", R_pg, R_ng)    # twin-at-carrier-gain vs carrier
leg("n25gP_minus_cutng25p", R_nP, R_tw)   # carrier-at-twin-gain vs twin

# ---------------- cross-batch (P-batch): B38 vs the stored B25 cells -------
_t135 = R135["table"]["Ti"]
xbatch = {}
for a in XOR:
    xbatch[a] = dict(b38=dict(kR=cls[a]["kR"], meanR=cls[a]["meanR"]),
                     b25_stored=dict(kR=_t135[a]["kR"],
                                     meanR=_t135[a]["meanR"]))
    print(f"P-batch {a}: B38 kR {cls[a]['kR']}/16 meanR {cls[a]['meanR']:.3f} "
          f"| stored B25 kR {_t135[a]['kR']}/16 meanR "
          f"{_t135[a]['meanR']:.3f}")
xbatch_note = ("cutng25p now rides a 3rd batch (B24/B25 stored + B38) — "
               "NOT the pooled 4-batch bar of the L88/L90 rule; any pooled "
               "statement from this stage is explicitly 3-batch")

# ---------------- registered branches (PRECEDENCE EXPLICIT) ----------------
ng, tw = cls["cutng25"], cls["cutng25p"]
pg, nP = cls["p25gN"], cls["n25gP"]
e0 = bool(not ng["super"])
e1 = bool(pg["notsuper"] and nP["super"])
e2 = bool(pg["super"] and nP["notsuper"])
if e0:
    branch = "E0_batch_fail"
elif e1:
    branch = "E1_graph_tracking"
elif e2:
    branch = "E2_gain_tracking"
else:
    branch = "E3_mixed"
xor_reproduced = bool(ng["super"] and tw["notsuper"])
print(f"\nBRANCH: {branch}")
print(f"  E0 (cutng25 not SUPER on B38): {e0}")
print(f"  E1 (p25gN NOT-SUPER and n25gP SUPER): {e1}")
print(f"  E2 (p25gN SUPER and n25gP NOT-SUPER): {e2}")
print(f"  XOR contrast reproduced on B38 (cutng25 SUPER, cutng25p "
      f"NOT-SUPER): {xor_reproduced}")
print(f"  gains | cutng25p {cls['cutng25p']['g']:.9f} < cutwA "
      f"{cls['cutwA']['g']:.9f} < cutng25 {cls['cutng25']['g']:.9f} "
      f"(swap span {100 * (cls['cutng25']['g'] / cls['cutng25p']['g'] - 1):.2f}%)")

out = dict(
    prereg="l169d/PREREG.md",
    design="L169 stage (d): the XOR-pair gain-swap 2x2. cutng25p = the "
           "twin-XOR graph (base window with the mass-twin gi 319 removed "
           "instead of the carrier gi 1110) at its OWN stored-form "
           "af-matched gain; p25gN = the cutng25p CSR by object identity at "
           "g_cutng25 (swapped UP); n25gP = the cutng25 CSR by object "
           "identity at g_cutng25p (swapped DOWN). Swap arms deliberately "
           "off the matched operating point (stage (a) convention). ONE "
           "fresh batch B38, n=16 per arm.",
    batch="B38", seeds=B38, n_seeds=len(B38),
    cert=cert, cert0=CERT0, cert_metric=cm,
    gains={a: float(z[f"g_{a}"]) for a in ("cutng25", "cutng25p", "cutwA")},
    swap_gain_span_pct=round(
        100 * (float(z["g_cutng25"]) / float(z["g_cutng25p"]) - 1), 4),
    pafd=A["pafd"], pafd_ok=A["pafd_ok"], pafd_nup=A["pafd_nup"],
    pafd_ndn=A["pafd_ndn"], d_stair=A["d_stair"], d_band_ok=A["d_band_ok"],
    table=cls, legs=legs, xbatch=xbatch, xbatch_note=xbatch_note,
    e0=e0, e1=e1, e2=e2, branch=branch, xor_reproduced=xor_reproduced,
    scope="Two-point gain probe: bounds the readout at the two bisected "
          "gains only; it cannot locate a threshold between them.")
json.dump(out, open("l169d/results_l169d.json", "w"), indent=1)
print("\nwrote l169d/results_l169d.json")
