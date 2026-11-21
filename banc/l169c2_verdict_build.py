"""l169c2_verdict_build.py — assemble l169c2_verdict.py as the VERBATIM
helper head of l169b2_verdict.py (imports + S_of/s_arrays/duty_seeds/
side_k/wilson/_super/_partial/_notsuper) plus a new (c2) tail.

House rules applied: the helper head is sliced, never retyped (L85 cert
rule still certifies it against the PRIOR run's stored table at runtime);
the assembled output is asserted to contain every helper def (L142 law:
a builder that slices helpers must assert them in the OUTPUT, not the
intermediate slice); py_compile gates the file.
"""
import py_compile
import sys

HEAD_SRC = "l169b2_verdict.py"
DST = "l169c2_verdict.py"
lines = open(HEAD_SRC).read().split("\n")

# slice from the first import to the end of _notsuper (exclusive of the
# run-specific batch constants that follow it)
i0 = next(i for i, l in enumerate(lines) if l.startswith("import json"))
i1 = next(i for i, l in enumerate(lines)
          if l.startswith('    return bool(t["kR"] <= 8'))
head = "\n".join(lines[i0:i1 + 1])
for fn in ("def S_of", "def s_arrays", "def duty_seeds", "def side_k",
           "def wilson", "def _super", "def _partial", "def _notsuper"):
    assert fn in head, f"helper slice missing {fn}"
assert "B36 = list(range" not in head, "slice ran past the helpers"

DOC = '''"""L169c2 verdict: the REW + HOM arms (stage c2).

Helper code VERBATIM-SLICED from l169b2_verdict.py by
l169c2_verdict_build.py (L85 cert rule: the copy is certified against
l169b2's STORED B36 table for the shared arms BEFORE any B37 value is
read). PREREG l169c2/PREREG.md registered the arms, the classifiers and
the R1/R2/R3 + H1/H2 branches before the run.
"""
'''

TAIL = '''

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
print("\\n---- B37 Ti per-side duty (n=16) ----")
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
print(f"\\nREW draw-pool kR {kR_pool}/{3 * len(B37)} "
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
print(f"\\nREW BRANCH: {rew_branch} (super {n_super}/3, notsuper "
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
print("\\nwrote l169c2/results_l169c2.json")
'''

body = DOC + head + TAIL
for fn in ("def S_of", "def s_arrays", "def duty_seeds", "def side_k",
           "def wilson", "def _super", "def _partial", "def _notsuper"):
    assert fn in body, f"ASSEMBLED OUTPUT missing {fn} (L142 law)"
assert body.count("import numpy as np") == 1
open(DST, "w").write(body)
py_compile.compile(DST, doraise=True)
print(f"wrote {DST} ({len(body.splitlines())} lines) | py_compile OK | "
      f"helper head sliced {i1 - i0 + 1} lines verbatim")
