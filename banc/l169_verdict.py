"""L169 verdict: the GAIN-SWAP 2x2. Helper code VERBATIM l150_verdict.py
(L85 cert rule — my copy is certified against l150's STORED B33 table plus
the l135/l142/l144/l145/l148 batch certs BEFORE any B35 value is read).
PREREG l169/PREREG.md (bands + D1/D2/D3 branches registered before the run).
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


def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


# ---- batches ----
B35 = list(range(3417, 3433))
B33 = list(range(3365, 3381))
B32 = list(range(3349, 3365))
B31 = list(range(3333, 3349))
B30 = list(range(3317, 3333))
B29 = list(range(3301, 3317))
B26 = list(range(3001, 3017))
B25 = list(range(2901, 2917))
B24 = list(range(2801, 2817))
B21 = list(range(2501, 2517))
ARMS169 = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5", "eMotBot5",
           "wAgN", "n25gW"]
z169 = np.load("l169/raw_l169.npz")
z150 = np.load("l150/raw_l150.npz")
z148 = np.load("l148/raw_l148.npz")
z145 = np.load("l145/raw_l145.npz")
z144 = np.load("l144/raw_l144.npz")
z142 = np.load("l142/raw_l142.npz")
z135 = np.load("l135/raw_l135.npz")
z133 = np.load("l133/raw_l133.npz")
z131 = np.load("l131/raw_l131.npz")
z126 = np.load("l126/raw_l126.npz")
ar = json.load(open("l169/anchors_run.json"))
r135 = json.load(open("l135/results_l135.json"))
r142 = json.load(open("l142/results_l142.json"))
r144 = json.load(open("l144/results_l144.json"))
r145 = json.load(open("l145/results_l145.json"))
r148 = json.load(open("l148/results_l148.json"))
r150 = json.load(open("l150/results_l150.json"))

# ---- B-cert BEFORE any B35 read (L85 rule), SIX certs ----
bcert_fail = []
for lab, zz, rr, bb, arms in (
        ("l135", z135, r135, B26, ("cutwA", "cutng25")),
        ("l142", z142, r142, B29, ("eAll", "cutwA", "cutng25")),
        ("l144", z144, r144, B30, ("cutwA", "cutng25", "sil1110_wA")),
        ("l145", z145, r145, B31, ("cutwA", "cutng25", "eMotTop5", "eMotBot5")),
        ("l148", z148, r148, B32, ("cutwA", "cutng25")),
        ("l150", z150, r150, B33, ("cutwA", "cutng25", "silW", "eMotTop5",
                                   "eMotBot5"))):
    for a in arms:
        want = rr["table"]["Ti"][a]
        got = side_k(zz, a, bb, "Ti")
        for kk in ("kL", "kR", "meanL", "meanR"):
            if got[kk] != want[kk]:
                bcert_fail.append((lab, a, kk, got[kk], want[kk]))
assert not bcert_fail, ("B-cert FAIL (no B35 read)", bcert_fail[:6])
print("B-cert vs stored Ti tables l135(B26)+l142(B29)+l144(B30)+l145(B31)"
      "+l148(B32)+l150(B33): PASS")

# ---- P0 anchors (gate booleans ONLY, L59 rule: named keys, never .values()) --
p0 = dict(c0a_pass=ar["c0a150_pass"], c0a_max=ar["c0a150_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"],
          g_emottop5_stored_exact=ar["g_emottop5_stored_exact"],
          g_emotbot5_stored_exact=ar["g_emotbot5_stored_exact"],
          g_silW_graphid=bool(ar["g_silW"] == ar["g_cutwA"]),
          fc144_pass=ar["fc144_pass"], fc144_max=ar["fc144_max"],
          fc145_pass=ar["fc145_pass"], fc145_max=ar["fc145_max"],
          swap_gains_crossed=bool(ar["g_wAgN"] == ar["g_cutng25"]
                                  and ar["g_n25gW"] == ar["g_cutwA"]),
          nt_pass=ar["nt_pass"], nt_min=min(ar["nt"].values()),
          paf_ok=ar["paf_ok"])
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cutwA_stored_exact"]
                  and p0["g_cutng25_stored_exact"]
                  and p0["g_emottop5_stored_exact"]
                  and p0["g_emotbot5_stored_exact"] and p0["g_silW_graphid"]
                  and p0["fc144_pass"] and p0["fc145_pass"]
                  and p0["swap_gains_crossed"] and p0["nt_pass"])
print("P0 anchors (C0A-169 + stored gains x4 + FC-144 + FC-145 + swap-crossed"
      " + C0-NT):", "PASS" if p0["pass"] else "FAIL",
      f"(c0a {p0['c0a_max']:.1e} | FC-144 {p0['fc144_max']:.1e} | "
      f"FC-145 {p0['fc145_max']:.1e} | NT min {p0['nt_min']:.3e})")
assert p0["nt_pass"], "C0-NT VOID: a swap arm is bit-identical to its twin"

# ---- P4 health + registered af disclosure ----
af_mean = {a: round(float(np.mean([float(z169[f"af_{a}_{s}"]) for s in B35])), 6)
           for a in ARMS169}
af_range_ok = all(0.01 < float(z169[f"af_{a}_{s}"]) < 0.9
                  for a in ARMS169 for s in B35)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
AF_T = ar["af_target"]
af_mismatch = {a: round(abs(af_mean[a] - AF_T), 6) for a in ("wAgN", "n25gW",
                                                             "cutwA",
                                                             "cutng25")}
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band),
          af_mean=af_mean, e_band_ok=ar["e_band_ok"],
          new_stairs=ar["new_stairs"], af_target=AF_T,
          af_mismatch=af_mismatch, paf_ok=ar["paf_ok"])
print("P4", json.dumps({k: p4[k] for k in ("af_range_ok", "b65_band",
                                           "e_band_ok", "paf_ok")}))
print("af (B35 mean) | " + " | ".join(
    f"{a} {af_mean[a]:.5f}" for a in ("cutwA", "wAgN", "cutng25", "n25gW")) +
    f" | target {AF_T:.5f}")

# ---- B35 per-side duty table (5 pairs x 9 arms) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS169:
        t = side_k(z169, a, B35, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B35 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS169:
        t = table[pk][a]
        print(f"{pk} {a:9s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Ti classification (criteria VERBATIM L118-L131) ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z169, "full", B35, "Ti")
_, RwA = duty_seeds(z169, "cutwA", B35, "Ti")
_, Rng25 = duty_seeds(z169, "cutng25", B35, "Ti")
LADDER = [("0", "full"), ("24", "cutwA"), ("wAgN", "wAgN"),
          ("n25gW", "n25gW"), ("silW", "silW"), ("top5", "eMotTop5"),
          ("bot5", "eMotBot5"), ("25", "cutng25")]
cls = {}
for kk, a in LADDER:
    t = table["Ti"][a]
    _, Rd = duty_seeds(z169, a, B35, "Ti")
    legs = dict(
        mean_paired_dR_vs_full=round(float((Rd - Rfull).mean()), 3),
        n_down_vs_full=int(((Rd - Rfull) <= -.20).sum()),
        mean_paired_dR_vs_wA=round(float((Rd - RwA).mean()), 3),
        n_down_vs_wA=int(((Rd - RwA) <= -.20).sum()),
        n_up_vs_wA=int(((Rd - RwA) >= .20).sum()),
        mean_paired_dR_vs_ng25=round(float((Rd - Rng25).mean()), 3))
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR_vs_full"] <= -.20)
    cls[kk] = dict(arm=a, meanR=t["meanR"], kR=t["kR"], meanL=t["meanL"],
                   kL=t["kL"], lbR=t["lbR"], ubR=t["ubR"],
                   kill=bool(kill), restore=_restore(t), super=_super(t),
                   partial=_partial(t), legs=legs)
    print(f"Ti {kk:>6s} ({a:9s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | dR_wA "
          f"{legs['mean_paired_dR_vs_wA']:+.3f} n_up_wA "
          f"{legs['n_up_vs_wA']:2d}/16 | dR_ng25 "
          f"{legs['mean_paired_dR_vs_ng25']:+.3f} -> "
          f"{'KILL' if kill else 'no-kill'}"
          f"{'/RESTORE' if _restore(t) else ''}"
          f"{'/SUPER' if _super(t) else ''}"
          f"{'/PARTIAL' if _partial(t) else ''}")

cls_of = lambda c: ("KILL" if c["kill"] else
                    "SUPER" if c["super"] else
                    "RESTORE" if c["restore"] else
                    "PARTIAL" if c["partial"] else "NONE")

# ---- the registered 2x2 and its branch ----
grid = {
    "graph_wA__gain_wA": dict(arm="cutwA", **{k: cls["24"][k]
                                              for k in ("meanR", "kR", "meanL",
                                                        "kL", "lbR", "ubR")},
                              cls=cls_of(cls["24"]), gain=ar["g_cutwA"]),
    "graph_wA__gain_ng25": dict(arm="wAgN", **{k: cls["wAgN"][k]
                                               for k in ("meanR", "kR", "meanL",
                                                         "kL", "lbR", "ubR")},
                                cls=cls_of(cls["wAgN"]), gain=ar["g_wAgN"]),
    "graph_ng25__gain_wA": dict(arm="n25gW", **{k: cls["n25gW"][k]
                                                for k in ("meanR", "kR",
                                                          "meanL", "kL",
                                                          "lbR", "ubR")},
                                cls=cls_of(cls["n25gW"]), gain=ar["g_n25gW"]),
    "graph_ng25__gain_ng25": dict(arm="cutng25", **{k: cls["25"][k]
                                                    for k in ("meanR", "kR",
                                                              "meanL", "kL",
                                                              "lbR", "ubR")},
                                  cls=cls_of(cls["25"]),
                                  gain=ar["g_cutng25"]),
}
wAgN_super = cls["wAgN"]["super"]
wAgN_notsuper = bool(cls["wAgN"]["kR"] <= 8 and cls["wAgN"]["meanR"] <= .50)
n25gW_super = cls["n25gW"]["super"]
n25gW_notsuper = bool(cls["n25gW"]["kR"] <= 8 and cls["n25gW"]["meanR"] <= .50)
D1 = bool(wAgN_notsuper and n25gW_super)      # flip follows the GRAPH
D2 = bool(wAgN_super and n25gW_notsuper)      # flip follows the GAIN
D3 = bool(not D1 and not D2)                  # MIXED: report cell by cell
branch = "D1_graph_tracking" if D1 else "D2_gain_tracking" if D2 else "D3_mixed"
print("---- registered 2x2 (graph x gain) ----")
for k, v in grid.items():
    print(f"{k:24s} {v['arm']:8s} g {v['gain']:.9f} | meanR {v['meanR']:.3f} "
          f"kR {v['kR']:2d}/16 [{v['lbR']:.3f},{v['ubR']:.3f}] -> {v['cls']}")
print(f"BRANCH: {branch} (D1 {D1} / D2 {D2} / D3 {D3})")

# ---- pooled reads (L90 full-precision Wilson, unrounded) ----
def pooled(raws, a, batches, pk="Ti", names=None):
    Ls, Rs = [], []
    for i, (raw, b) in enumerate(zip(raws, batches)):
        nm = a if names is None else names[i]
        L, R = duty_seeds(raw, nm, b, pk)
        Ls.append(L); Rs.append(R)
    R_ = np.concatenate(Rs); L_ = np.concatenate(Ls)
    kR, kL = int((R_ >= .5).sum()), int((L_ >= .5).sum())
    lbR, ubR = wilson(kR, len(R_)); lbL, ubL = wilson(kL, len(L_))
    return dict(kR=kR, n=len(R_), lbR=lbR, ubR=ubR, kL=kL, lbL=lbL, ubL=ubL,
                meanR=round(float(R_.mean()), 3),
                meanL=round(float(L_.mean()), 3))


pooled_silW = pooled([z144, z150, z169], "silW", [B30, B33, B35],
                     names=["sil1110_wA", "silW", "silW"])
pooled_top5 = pooled([z145, z150, z169], "eMotTop5", [B31, B33, B35])
pooled_bot5 = pooled([z145, z150, z169], "eMotBot5", [B31, B33, B35])
pooled_ng25 = pooled([z131, z133, z135, z142, z144, z145, z148, z150, z169],
                     "cutng25",
                     [B24, B25, B26, B29, B30, B31, B32, B33, B35])
pooled_wA = pooled([z126, z131, z133, z135, z142, z144, z145, z148, z150,
                    z169], "cutwA",
                   [B21, B24, B25, B26, B29, B30, B31, B32, B33, B35])
print("pooled silW B30+B33+B35:", json.dumps(pooled_silW))
print("pooled eMotTop5 3-batch:", json.dumps(pooled_top5))
print("pooled eMotBot5 3-batch:", json.dumps(pooled_bot5))
print("pooled cutng25 9-batch:", json.dumps(pooled_ng25))
print("pooled cutwA 10-batch:", json.dumps(pooled_wA))

out = dict(prereg="l169/PREREG.md", batch="B35 3417-3432", n_seeds=16,
           p0=p0, p4=p4, table=table, cls={k: v for k, v in cls.items()},
           grid=grid, branch=branch,
           branch_legs=dict(wAgN_super=wAgN_super,
                            wAgN_notsuper=wAgN_notsuper,
                            n25gW_super=n25gW_super,
                            n25gW_notsuper=n25gW_notsuper,
                            D1=D1, D2=D2, D3=D3),
           pooled=dict(silW=pooled_silW, eMotTop5=pooled_top5,
                       eMotBot5=pooled_bot5, cutng25=pooled_ng25,
                       cutwA=pooled_wA),
           gains=dict(cutwA=ar["g_cutwA"], cutng25=ar["g_cutng25"],
                      wAgN=ar["g_wAgN"], n25gW=ar["g_n25gW"]),
           nt=ar["nt"], paf=ar["paf"])
json.dump(out, open("l169/results_l169.json", "w"), indent=1)
print("results_l169.json written |", branch)
