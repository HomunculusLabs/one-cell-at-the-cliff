"""L169c2 verdict: the REW + HOM arms (stage c2).

Helper code VERBATIM-SLICED from l169b2_verdict.py by
l169c2_verdict_build.py (L85 cert rule: the copy is certified against
l169b2's STORED B36 table for the shared arms BEFORE any B37 value is
read). PREREG l169c2/PREREG.md registered the arms, the classifiers and
the R1/R2/R3 + H1/H2 branches before the run.
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

B37 = list(range(3481, 3497))
B36 = list(range(3449, 3465))
REW = ("rew1", "rew2", "rew3")
C2 = REW + ("hom",)
BASE = ("full", "cutwA", "cutng25")

z = np.load("l169c2/raw_l169c2.npz")
zb2 = np.load("l169b2/raw_l169b2.npz")
A = json.load(open("l169c2/anchors_run.json"))
RB2 = json.load(open("l169b2/results_l169b2.json"))

# ---------------- CERT-0: the anchors the run itself measured ----------------
cert = dict(fc169b2_pass=A["fc169b2_pass"], fc169b2_max=A["fc169b2_max"],
            ntc2_pass=A["ntc2_pass"], ntc2_min=min(A["ntc2"].values()),
            fc169_pass=A["fc169_pass"], c0a150_pass=A["c0a150_pass"],
            fc144_pass=A["fc144_pass"], fc145_pass=A["fc145_pass"],
            ntf4_pass=A["ntf4_pass"],
            g_cutwA_exact=A["g_cutwA_stored_exact"],
            g_cutng25_exact=A["g_cutng25_stored_exact"],
            g_emottop5_exact=A["g_emottop5_stored_exact"],
            g_emotbot5_exact=A["g_emotbot5_stored_exact"],
            pafc2_ok=A["pafc2_ok"], c2_gains_distinct=A["c2_gains_distinct"],
            hom_incident=A["hom_incident"], c2_n=A["c2_n"],
            c2_edges=A["c2_edges"])
print("---- CERT-0 (run-side anchors) ----")
for k, v in cert.items():
    print(f"  {k:22s} {v}")
CERT0 = bool(cert["fc169b2_pass"] and cert["ntc2_pass"]
             and cert["fc169_pass"] and cert["c0a150_pass"]
             and cert["g_cutwA_exact"] and cert["g_cutng25_exact"]
             and cert["g_emottop5_exact"] and cert["g_emotbot5_exact"])
print(f"CERT-0 (CERT-1 chain + CERT-2 subset + C0-NT(c2)): "
      f"{'GREEN' if CERT0 else 'RED'}")
# structural pins the run asserted (re-read here, not re-derived)
assert cert["hom_incident"] == 101, cert["hom_incident"]
assert cert["c2_n"]["hom"] == cert["c2_n"]["rew1"] - 1, cert["c2_n"]
for _a in REW:
    assert cert["c2_edges"][_a] == cert["c2_edges"]["rew1"], cert["c2_edges"]
print("structural pins: hom 101 incident edges | rew edge counts identical")

# ---------------- CERT-METRIC: my helper copy vs l169b2's STORED B36 --------
cm = {}
for arm in ("f4wA", "f4ng", "f4tw", "cutwA"):
    t = side_k(zb2, arm, B36, "Ti")
    st = RB2["table"][arm]
    cm[arm] = dict(mine=t, stored={k: st[k] for k in
                                   ("meanR", "kR", "meanL", "kL")})
    for f in ("meanR", "kR", "meanL", "kL"):
        assert t[f] == st[f], ("CERT-METRIC FAIL", arm, f, t[f], st[f])
print("CERT-METRIC GREEN: helper copy reproduces l169b2 stored B36 cells "
      "(f4wA / f4ng / f4tw / cutwA, 4 fields each) EXACTLY")

# ---------------- the B37 table ----------------
cls = {}
for a in C2 + BASE:
    t = side_k(z, a, B37, "Ti")
    lbR, ubR = wilson(t["kR"], len(B37))
    lbL, ubL = wilson(t["kL"], len(B37))
    cls[a] = dict(arm=a, **t, lbR=lbR, ubR=ubR, lbL=lbL, ubL=ubL,
                  g=float(z[f"g_{a}"]) if f"g_{a}" in z.files else None,
                  n=int(A["c2_n"][a]) if a in C2 else None,
                  edges=int(A["c2_edges"][a]) if a in C2 else None,
                  super=_super(t), partial=_partial(t), notsuper=_notsuper(t))
print("\n---- B37 Ti per-side duty (n=16) ----")
for a in C2 + BASE:
    c = cls[a]
    gs = f"g {c['g']:.9f}" if c["g"] is not None else "g (stored)"
    print(f"{a:9s} {gs} | meanR {c['meanR']:.3f} kR {c['kR']:2d}/16 "
          f"[{c['lbR']:.3f},{c['ubR']:.3f}] | meanL {c['meanL']:.3f} "
          f"kL {c['kL']:2d}/16 | SUPER {c['super']} PARTIAL {c['partial']} "
          f"NOTSUPER {c['notsuper']}")

# ---------------- paired legs within B37 (same seeds, same noise) ----------
legs = {}
_, R_wA = duty_seeds(z, "cutwA", B37, "Ti")
_, R_ng = duty_seeds(z, "cutng25", B37, "Ti")
for a in C2:
    _, R_a = duty_seeds(z, a, B37, "Ti")
    d = R_a - R_wA
    dn = R_a - R_ng
    legs[a] = dict(mean_paired_dR_vs_cutwA=round(float(d.mean()), 3),
                   n_up=int((d > 0).sum()), n_down=int((d < 0).sum()),
                   mean_paired_dR_vs_cutng25=round(float(dn.mean()), 3))
    print(f"paired {a} vs cutwA: dR {legs[a]['mean_paired_dR_vs_cutwA']:+.3f} "
          f"up {legs[a]['n_up']}/16 down {legs[a]['n_down']}/16 | vs cutng25 "
          f"{legs[a]['mean_paired_dR_vs_cutng25']:+.3f}")

# ---------------- REW pooled over the three DRAWS (n=48, draw pool) --------
kR_pool = sum(cls[a]["kR"] for a in REW)
kL_pool = sum(cls[a]["kL"] for a in REW)
lb_pool, ub_pool = wilson(kR_pool, 3 * len(B37))
pooled = dict(kR=kR_pool, n=3 * len(B37), lb=lb_pool, ub=ub_pool,
              kL=kL_pool,
              meanR=round(float(np.mean([cls[a]["meanR"] for a in REW])), 3),
              note="draw pool (3 rewire draws x one batch), NOT a seed-batch "
                   "pool; does not satisfy the L88/L90 multi-batch rule")
base_lb, base_ub = wilson(cls["cutwA"]["kR"], len(B37))
ng_lb, ng_ub = wilson(cls["cutng25"]["kR"], len(B37))
print(f"\nREW draw-pool kR {kR_pool}/{3 * len(B37)} "
      f"[{lb_pool:.3f},{ub_pool:.3f}] | same-batch cutwA "
      f"{cls['cutwA']['kR']}/16 [{base_lb:.3f},{base_ub:.3f}] | cutng25 "
      f"{cls['cutng25']['kR']}/16 [{ng_lb:.3f},{ng_ub:.3f}]")

# ---------------- registered branches ----------------
vac = bool(cls["cutwA"]["super"])          # degenerate guard (L55 class)
n_super = sum(1 for a in REW if cls[a]["super"])
n_notsuper = sum(1 for a in REW if cls[a]["notsuper"])
r1 = bool(n_super >= 2 and lb_pool > base_ub)
r2 = bool(n_notsuper >= 2)
rew_branch = ("R1_placement" if r1 else
              "R2_mass_degree" if r2 else "R3_draw_lottery")
if vac:
    rew_branch = "R3_draw_lottery"
hom_branch = "H1_specific" if cls["hom"]["notsuper"] else (
    "H2_nonspecific" if cls["hom"]["super"] else "H_mixed")
print(f"\nREW BRANCH: {rew_branch} (super {n_super}/3, notsuper "
      f"{n_notsuper}/3, pooled lb {lb_pool:.3f} vs base ub {base_ub:.3f}; "
      f"vacuous-base guard fired: {vac})")
print(f"HOM BRANCH: {hom_branch} (super {cls['hom']['super']}, notsuper "
      f"{cls['hom']['notsuper']}, meanR {cls['hom']['meanR']:.3f})")

out = dict(
    prereg="l169c2/PREREG.md",
    design="L169 stage (c2): the REW + HOM rollout arms on the G1 cutwA "
           "base. rew1/rew2/rew3 = the cutwA node set and edge COUNT "
           "verbatim with the carrier's 80 closure out-edges "
           "degree-preservingly REWIRED (draws 0/1/2 of the registered "
           "default_rng(16943) stream, weights travelling with the source "
           "edge); hom = cutwA minus gi 928 (DNp33-R), a SAME-FOOTPRINT "
           "DIFFERENT-CLASS deletion (c1 rule C2 NONEQUIVALENT), never a "
           "homolog control. Fresh per-arm af-matched bisects. ONE batch, "
           "n=16 per arm.",
    batch="B37", seeds=B37, n_seeds=len(B37),
    cert=cert, cert0=CERT0, cert_metric=cm,
    rew_draws_first5=A["rew_draws_first5"],
    rew_chance_T70=A["rew_chance_T70"],
    carrier_out_mass=A["carrier_out_mass"],
    gains={a: float(z[f"g_{a}"]) for a in C2},
    c2_stairs=A["c2_stairs"], c2_band_ok=A["c2_band_ok"],
    c2_n=A["c2_n"], c2_edges=A["c2_edges"], pafc2=A["pafc2"],
    table=cls, legs=legs, pooled_rew=pooled,
    base_bounds=dict(cutwA=[base_lb, base_ub], cutng25=[ng_lb, ng_ub]),
    vacuous_base_guard=vac, n_super_rew=n_super, n_notsuper_rew=n_notsuper,
    r1=r1, r2=r2, rew_branch=rew_branch, hom_branch=hom_branch)
json.dump(out, open("l169c2/results_l169c2.json", "w"), indent=1)
print("\nwrote l169c2/results_l169c2.json")
