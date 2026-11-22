"""L175 verdict: the FLOOR-4 LEFT-SIDE registered test (PREREG l175f/PREREG.md).

Helpers imported VERBATIM from l169b2_verdict.py (L85). CERT-L runs FIRST on
the STORED l169b2 npz over B36 and must reproduce the stored
addendum_L_descriptive rows and legs EXACTLY before any B37 trace is read.
"""
import json
import hashlib
import math
import sys

import numpy as np

# ---- helpers VERBATIM from l169b2_verdict.py, as an EXEC'D SOURCE SLICE ----
# A plain `import` would EXECUTE that module (it is a script, not a library):
# it reloads the npz, recomputes its own verdict and REWRITES
# l169b2/results_l169b2.json — a stored-artifact mutation. Slicing lines
# 1..91 (everything up to, and not including, the first file read) gives the
# same byte-exact helper code with zero side effects (L85 form).
_vsrc = open("l169b2_verdict.py").read().splitlines(keepends=True)
_slice = "".join(_vsrc[:91])
assert "def duty_seeds" in _slice and "def wilson" in _slice
assert "np.load(" not in _slice and "json.load(" not in _slice and \
    "json.dump(" not in _slice, "source slice is not side-effect free (STOP)"
_V = {}
exec(compile(_slice, "l169b2_verdict.py[1:91]", "exec"), _V)
print("helper slice sha256",
      hashlib.sha256(_slice.encode()).hexdigest()[:16], f"({len(_slice)} chars)")


class V:                      # namespace shim over the exec'd slice
    duty_seeds = staticmethod(_V["duty_seeds"])
    wilson = staticmethod(_V["wilson"])
    B36 = _V["B36"]

B37 = list(range(3701, 3717))
F4 = ("f4wA", "f4ng", "f4tw")
READ = F4 + ("cutwA", "cutng25")
PK = "Ti"

# ---- mirrored house bands (PREREG; identical numbers, side swapped) ----
def superL(meanL, kL):
    return bool(meanL >= .60 and kL >= 12)


def partialL(meanL, kL):
    return bool(.35 <= meanL <= .50 and 3 <= kL <= 8)


def notsuperL(meanL, kL):
    return bool(kL <= 8 and meanL <= .50)


# ================= CERT-L: the metric copy on STORED data =================
stored = json.load(open("l169b2/results_l169b2.json"))["addendum_L_descriptive"]
z_old = np.load("l169b2/raw_l169b2.npz")
cert_rows, cert_fail = {}, []
for a in READ:
    L, R = V.duty_seeds(z_old, a, V.B36, PK)
    mine = dict(meanL=round(float(L.mean()), 3), kL=int((L >= .5).sum()),
                meanR=round(float(R.mean()), 3), kR=int((R >= .5).sum()))
    st = stored["rows"][a]
    ok = all(mine[k] == st[k] for k in ("meanL", "kL", "meanR", "kR"))
    cert_rows[a] = dict(mine=mine, stored={k: st[k] for k in mine}, ok=ok)
    if not ok:
        cert_fail.append(a)
# legs
L_wA, _ = V.duty_seeds(z_old, "f4wA", V.B36, PK)
L_ng, _ = V.duty_seeds(z_old, "f4ng", V.B36, PK)
L_tw, _ = V.duty_seeds(z_old, "f4tw", V.B36, PK)
cert_legs = {}
for name, d in (("f4ng_vs_f4wA", L_ng - L_wA), ("f4tw_vs_f4wA", L_tw - L_wA),
                ("f4ng_vs_f4tw", L_ng - L_tw)):
    mine = dict(mean_paired_dL=round(float(d.mean()), 3),
                n_up=int((d > 0).sum()), n_down=int((d < 0).sum()))
    st = stored["paired_legs"][name]
    ok = all(mine[k] == st[k] for k in mine)
    cert_legs[name] = dict(mine=mine, stored=st, ok=ok)
    if not ok:
        cert_fail.append(name)
CERT_L = not cert_fail
print("---- CERT-L (metric copy vs stored B36 addendum) ----")
for a, c in cert_rows.items():
    print(f"  {a:9s} {c['ok']} mine {c['mine']}")
for n, c in cert_legs.items():
    print(f"  {n:14s} {c['ok']} mine {c['mine']}")
print(f"CERT-L: {'PASS' if CERT_L else 'FAIL ' + str(cert_fail)}")
if not CERT_L:
    sys.exit("CERT-L FAILED — B_VOID, no B37 value read (STOP)")

# ================= anchors from the run =================
anch = json.load(open("l175f/anchors_run.json"))
gates0 = dict(fc169b2_pass=anch["fc169b2_pass"], fc169b2_max=anch["fc169b2_max"],
              fc169_pass=anch["fc169_pass"], c0a150_pass=anch["c0a150_pass"],
              fc144_pass=anch["fc144_pass"], fc145_pass=anch["fc145_pass"],
              ntf4_pass=anch["ntf4_pass"], nt_pass=anch["nt_pass"],
              paf4_ok=anch["paf4_ok"], c0a_pass=anch["c0a_pass"],
              f4_gain_exact=anch["f4_gain_exact"])
print("\n---- run anchors ----")
for k, v in gates0.items():
    print(f"  {k}: {v}")
if not (anch["fc169b2_pass"] and anch["c0a_pass"]):
    sys.exit("ANCHOR FAILED — B_VOID (STOP)")

# ================= B37 read =================
z = np.load("l175f/raw_l175f.npz")
assert all(f"{PK}_fL_f4wA_{s}" in z.files for s in B37), "B37 coverage miss"
rows, per_seed = {}, {}
for a in READ:
    L, R = V.duty_seeds(z, a, B37, PK)
    lbL, ubL = V.wilson(int((L >= .5).sum()), len(B37))
    rows[a] = dict(meanL=round(float(L.mean()), 3), kL=int((L >= .5).sum()),
                   lbL=round(lbL, 3), ubL=round(ubL, 3),
                   meanR=round(float(R.mean()), 3), kR=int((R >= .5).sum()),
                   superL=superL(float(L.mean()), int((L >= .5).sum())),
                   partialL=partialL(round(float(L.mean()), 3),
                                     int((L >= .5).sum())),
                   notsuperL=notsuperL(int((L >= .5).sum()),
                                       round(float(L.mean()), 3)))
    per_seed[a] = dict(L=[float(x) for x in L], R=[float(x) for x in R])

print("\n---- B37 Ti LEFT-side duty (n=16, FRESH) ----")
for a in READ:
    r = rows[a]
    print(f"{a:9s} meanL {r['meanL']:.3f} kL {r['kL']:2d}/16 "
          f"[{r['lbL']:.3f},{r['ubL']:.3f}] | meanR {r['meanR']:.3f} "
          f"kR {r['kR']:2d}/16 | superL {r['superL']}")

Lv = {a: np.array(per_seed[a]["L"]) for a in READ}
Rv = {a: np.array(per_seed[a]["R"]) for a in READ}

# ---- G1: replication of the floored-substrate L structure (two bars) ----
g1_mean = bool(rows["f4wA"]["meanL"] >= .60)
g1_k = bool(rows["f4wA"]["kL"] >= 12)
G1 = bool(g1_mean and g1_k)

# ---- G2: carrier vs mass-matched twin on the L axis (two bars) ----
d_ng_tw = Lv["f4ng"] - Lv["f4tw"]
n_down = int((d_ng_tw < 0).sum())
n_up = int((d_ng_tw > 0).sum())
mean_d = round(float(d_ng_tw.mean()), 3)
g2_count = bool(n_down >= 12)
g2_mag = bool(mean_d <= -0.10)
G2 = bool(g2_count and g2_mag)


def sign_p(k, n):
    """one-sided binomial sign-test p for >= k of n at p0 = .5"""
    return float(sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n)


p_sign = sign_p(n_down, n_down + n_up) if (n_down + n_up) else float("nan")

# ---- G3: asymmetry of cost vs f4wA (one bar) ----
d_ng_wA = Lv["f4ng"] - Lv["f4wA"]
d_tw_wA = Lv["f4tw"] - Lv["f4wA"]
m_ng, m_tw = float(d_ng_wA.mean()), float(d_tw_wA.mean())
ratio = abs(m_ng) / abs(m_tw) if abs(m_tw) > 1e-9 else float("inf")
G3 = bool(abs(m_ng) >= 2.0 * abs(m_tw))

legs = {
    "f4ng_vs_f4wA": dict(mean_paired_dL=round(m_ng, 3),
                         n_up=int((d_ng_wA > 0).sum()),
                         n_down=int((d_ng_wA < 0).sum())),
    "f4tw_vs_f4wA": dict(mean_paired_dL=round(m_tw, 3),
                         n_up=int((d_tw_wA > 0).sum()),
                         n_down=int((d_tw_wA < 0).sum())),
    "f4ng_vs_f4tw": dict(mean_paired_dL=mean_d, n_up=n_up, n_down=n_down,
                         sign_p=round(p_sign, 4)),
}
print("\n---- paired legs (L axis, per seed) ----")
for k, v in legs.items():
    print(f"  {k:14s} dL {v['mean_paired_dL']:+.3f} up {v['n_up']:2d}/16 "
          f"down {v['n_down']:2d}/16")
print(f"\nG1 replication  meanL>=.60 {g1_mean} | kL>=12 {g1_k}  -> {G1}")
print(f"G2 carrier/twin n_down>=12 {g2_count} ({n_down}/16, sign p {p_sign:.4f}) "
      f"| dL<=-.10 {g2_mag} ({mean_d:+.3f})  -> {G2}")
print(f"G3 asymmetry    |dng|/|dtw| = {ratio:.2f} >= 2.0 -> {G3} "
      f"({m_ng:+.3f} vs {m_tw:+.3f})")

# ---- G4: side-swap diagnostic (DESCRIPTIVE, no branch depends on it) ----
dom_seeds = {a: int((Lv[a] > Rv[a]).sum()) for a in READ}
dom_mean = {a: ("L" if rows[a]["meanL"] > rows[a]["meanR"] else "R")
            for a in READ}
# replication of B36's dominance call, arm by arm
dom_stored = stored["side_dominance"]
dom_replicates = {a: bool(dom_mean[a] == dom_stored[a]) for a in READ}
print("\n---- G4 side-swap diagnostic (descriptive) ----")
for a in READ:
    print(f"  {a:9s} per-seed L>R {dom_seeds[a]:2d}/16 | mean-dominant "
          f"{dom_mean[a]} (B36 {dom_stored[a]}, replicates "
          f"{dom_replicates[a]})")

# ---- branch ----
if not CERT_L or not anch["fc169b2_pass"]:
    branch = "B_VOID"
elif not G1:
    branch = "B_BATCH_DRAW"
elif G2:
    branch = "B_REPLICATES_IDENTITY"
else:
    branch = "B_REPLICATES_FLAT"
print(f"\nBRANCH: {branch}")

out = dict(prereg="l175f/PREREG.md", batch="B37 3701-3716", seeds=B37,
           pair=PK, cert_L=dict(passed=CERT_L, rows=cert_rows, legs=cert_legs),
           anchors=gates0, rows=rows, per_seed=per_seed, legs=legs,
           g1=dict(mean_bar=g1_mean, k_bar=g1_k, passed=G1),
           g2=dict(count_bar=g2_count, mag_bar=g2_mag, n_down=n_down,
                   n_up=n_up, mean_paired_dL=mean_d, sign_p=p_sign,
                   passed=G2),
           g3=dict(ratio=round(ratio, 3), m_ng=round(m_ng, 4),
                   m_tw=round(m_tw, 4), passed=G3),
           g4=dict(label="DESCRIPTIVE — no branch depends on this",
                   per_seed_L_gt_R=dom_seeds, mean_dominant=dom_mean,
                   b36_dominant=dom_stored, replicates=dom_replicates),
           branch=branch,
           stored_b36_comparators=stored["rows"])
json.dump(out, open("l175f/results_l175f.json", "w"), indent=1)
print("\nwrote l175f/results_l175f.json")
