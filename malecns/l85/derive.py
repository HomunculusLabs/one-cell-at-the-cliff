"""L85 derive pass (read-only): fixed-family TRIPLE mass table + fork oracles,
re-derived 100% from STORED chain artifacts (l59/l77/l82/l83/l84 npz) — zero
new rollouts (L80 precedent). Numbers pinned here go into l85/PREREG.md; the
verdict script re-derives and asserts equality.

Family (census 16 seeds = SEEDS, shared noise stream, l82 metric machinery):
  nohop trunk : hynohop(l59) + hynohop_fb(l77) + hynohop_fb07(l82)
                + glide200/300/400(l83) + cont/nod/echo(l84, base==hynohop)
  hybrid trunk: hybrid(l59) + hybrid_fb(l77) + hyglide300(l83)
TRIPLE (never summed): tracking (per-seg block err), duty_07 + duty_fast
distributions (k>=.5 + Wilson), drive budget (entrain analytic + echo mass).
Fork oracles on noise-shared stored branches (L58 form):
  O1 K0 l84 trunk      {base,cont,nod,echo}        (seg1/2 fixed)
  O2 K2000 nohop trunk {hynohop,glide200/300/400}  (prefix bit-identical)
  O3 K2000 echo'd trunk{hynohop_fb,hynohop_fb07}   (prefix bit-identical)
  O4 K2000 hybrid trunk{hybrid,hyglide300}         (prefix bit-identical)
Realizability (L58 lesson-2 instrument): Spearman of per-seed branch delta
vs fork-time exit features computed from the shared prefix.
"""
import json
import math

import numpy as np

WIN, SEG, BLK, MEAS0 = 6000, 2000, 500, 500
SETTLE, DT = 400, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEEDS = [11, 22, 33] + list(range(101, 114))
SIGS = ("fL", "fR", "eL", "eR")
ENT_AMP = 0.3
FBG = dict(gfb=.1, delay=5)  # l66 content cell

z59 = np.load("l59/raw_l59.npz")
z77 = np.load("l77/raw_l77.npz")
z82 = np.load("l82/raw_l82.npz")
z83 = np.load("l83/raw_l83.npz")
z84 = np.load("l84/raw_l84.npz")

SRC = {  # arm -> npz holding the canonical copy
    "hynohop": z59, "hybrid": z59,
    "hynohop_fb": z77, "hybrid_fb": z77,
    "hynohop_fb07": z82,
    "glide200": z83, "glide300": z83, "glide400": z83, "hyglide300": z83,
    "cont": z84, "nod": z84, "echo": z84, "base": z84,
}
CH = {a: {str(s): {c: SRC[a][f"{c}_{a}_{s}"] for c in ("mm",) + SIGS}
          for s in SEEDS} for a in SRC}
mA = {"hynohop_fb": {str(s): z77[f"mA_hynohop_fb_{s}"] for s in SEEDS},
      "hybrid_fb": {str(s): z77[f"mA_hybrid_fb_{s}"] for s in SEEDS},
      "hynohop_fb07": {str(s): z82[f"mA_hynohop_fb07_{s}"] for s in SEEDS}}


def maxd(a, b, keys=("mm",) + SIGS, s=None):
    ss = [str(x) for x in (SEEDS if s is None else [s])]
    m = 0.0
    for sd in ss:
        for c in keys:
            m = max(m, float(np.abs(CH[a][sd][c] - CH[b][sd][c]).max()))
    return m


# ---------------- anchors (30th consecutive chain anchor) ----------------
A = {}
A["A1_hynohop_xrun"] = all(
    float(np.abs(CH["hynohop"][s]["mm"] - zz[f"mm_hynohop_{s}"][:WIN]).max()) == 0.0
    and all(float(np.abs(CH["hynohop"][s][c] - zz[f"{c}_hynohop_{s}"][:WIN]).max()) == 0.0
            for c in SIGS)
    for s in map(str, SEEDS) for zz in (z77, z82, z83))
A["A2_hybrid_xrun"] = all(
    float(np.abs(CH["hybrid"][s]["mm"] - zz[f"mm_hybrid_{s}"][:WIN]).max()) == 0.0
    and all(float(np.abs(CH["hybrid"][s][c] - zz[f"{c}_hybrid_{s}"][:WIN]).max()) == 0.0
            for c in SIGS)
    for s in map(str, SEEDS) for zz in (z77, z83))
A["A3_base_eq_hynohop"] = maxd("base", "hynohop") == 0.0
A["A4_echo84_seg01_eq_fb07"] = maxd("echo", "hynohop_fb07", keys=("mm",) + SIGS)  # report
A["A4_prefix4000"] = max(
    float(np.abs(CH["echo"][s][c][:4000] - CH["hynohop_fb07"][s][c][:4000]).max())
    for s in map(str, SEEDS) for c in ("mm",) + SIGS) == 0.0
fd84 = []
for s in map(str, SEEDS):
    d = np.concatenate([np.abs(CH["echo"][s]["mm"] - CH["hynohop_fb07"][s]["mm"])]
                       + [np.abs(CH["echo"][s][c] - CH["hynohop_fb07"][s][c]) for c in SIGS])
    fd84.append(int(np.argmax(d > 0)) % WIN)
A["A4_first_div_set"] = sorted(set(fd84))
A["A5_glide_prefix"] = all(
    float(np.abs(CH[g][s][c][:2000] - CH["hynohop"][s][c][:2000]).max()) == 0.0
    for g in ("glide200", "glide300", "glide400") for s in map(str, SEEDS) for c in ("mm",) + SIGS)
A["A5h_hyglide_prefix"] = all(
    float(np.abs(CH["hyglide300"][s][c][:2000] - CH["hybrid"][s][c][:2000]).max()) == 0.0
    for s in map(str, SEEDS) for c in ("mm",) + SIGS)
A["A6_fb07_fb_prefix"] = all(
    float(np.abs(CH["hynohop_fb07"][s][c][:2001] - CH["hynohop_fb"][s][c][:2001]).max()) == 0.0
    for s in map(str, SEEDS) for c in ("mm",) + SIGS)
print("ANCHORS", json.dumps({k: (v if not isinstance(v, float) else round(v, 6))
                             for k, v in A.items()}))


# ---------------- l82 metric machinery (verbatim) ----------------
def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


def dom_freq(x, lo=0.3):
    x = np.asarray(x, np.float64)
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    return float(f_hat)


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(CH[a][s]["fL"][t - 499:t + 1], CH[a][s]["eL"][t - 499:t + 1])
        SR[t] = S_of(CH[a][s]["fR"][t - 499:t + 1], CH[a][s]["eR"][t - 499:t + 1])
    SM[(a, s)] = (SL, SR)
    return SL, SR


def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


ARMS = ["hynohop", "hynohop_fb", "hynohop_fb07", "glide200", "glide300",
        "glide400", "cont", "nod", "echo", "hybrid", "hybrid_fb", "hyglide300"]
cells = {a: {} for a in ARMS}
for a in ARMS:
    for s in map(str, SEEDS):
        SL, SR = s_arrays(a, s)
        rows = []
        for a0_, b0, tg in SEGB:
            lo, hi = a0_ + MEAS0, b0
            q = (TS >= lo) & (TS < hi)
            both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
            bl = []
            for b in range(WIN // BLK):
                if a0_ <= b * BLK < b0 and b * BLK > a0_:
                    bl.append(abs(dom_freq(CH[a][s]["mm"][b * BLK:(b + 1) * BLK]) - tg))
            rows.append(dict(duty=round(float(np.nanmean(both)), 3),
                             f=round(dom_freq(CH[a][s]["mm"][a0_:b0]), 3),
                             err=round(float(np.mean(bl)), 4)))
        qall = np.zeros(len(TS), bool)
        q07 = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            qall |= (TS >= a0_ + MEAS0) & (TS < b0)
            if f == 0.7:
                q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
        cells[a][str(s)] = dict(
            segs=rows,
            duty_all=round(float(np.nanmean((SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
            duty_07=round(float(np.nanmean((SL[TS[q07]] >= .25) & (SR[TS[q07]] >= .25))), 3))

# ---------------- budget (analytic entrain + measured echo) ----------------
AMPA = {a: np.zeros(WIN) for a in ARMS}
for a in ARMS:                                   # l59 hynohop form everywhere
    for seg0, _, _ in SEGB:
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA[a][2000:4000] = ENT_AMP
AMPA["cont"][:2000] = ENT_AMP
AMPA["nod"][:2000] = 0.0
sin_carr = 0.5 + 0.5 * np.sin(PHI)
MASS = {a: round(float((AMPA[a] * sin_carr).sum()), 1) for a in ARMS}
ON = {a: int((AMPA[a] > 0).sum()) + SETTLE for a in ARMS}
EON = {"hynohop_fb": np.ones(WIN, bool),
       "hybrid_fb": np.ones(WIN, bool),
       "hynohop_fb07": np.r_[np.ones(2000, bool), np.zeros(2000, bool), np.ones(2000, bool)]}
ENT_MASS = MASS["hynohop"]
echo = {}
for fb in EON:
    ks = np.where(EON[fb])[0]
    ks = ks[ks >= FBG["delay"]]
    em = [float(FBG["gfb"] * mA[fb][str(s)][ks - FBG["delay"]].sum()) for s in SEEDS]
    echo[fb] = dict(mass=round(float(np.mean(em)), 1), ratio=round(float(np.mean(em)) / ENT_MASS, 4))
ks0 = np.arange(5, 2000)                          # echo84 = seg0-only echo
em84 = [float(FBG["gfb"] * mA["hynohop_fb07"][str(s)][ks0 - FBG["delay"]].sum()) for s in SEEDS]
echo["echo(l84,seg0)"] = dict(mass=round(float(np.mean(em84)), 1),
                              ratio=round(float(np.mean(em84)) / ENT_MASS, 4))

# ---------------- distributions ----------------
dist = {}
for a in ARMS:
    segs = []
    for i in range(3):
        d = np.array([cells[a][str(s)]["segs"][i]["duty"] for s in SEEDS])
        e = np.array([cells[a][str(s)]["segs"][i]["err"] for s in SEEDS])
        segs.append(dict(mean=round(float(d.mean()), 3), k=int((d >= .5).sum()),
                         wilson=wilson(int((d >= .5).sum()), 16),
                         err_le01=int((e <= .01).sum())))
    d07 = np.array([cells[a][str(s)]["duty_07"] for s in SEEDS])
    k07 = int((d07 >= .5).sum())
    dist[a] = dict(segs=segs, duty07_mean=round(float(d07.mean()), 3), duty07_k=k07,
                   duty07_wilson=wilson(k07, 16),
                   per_seed=dict(seg1=[cells[a][str(s)]["segs"][1]["duty"] for s in SEEDS],
                                 d07=[round(float(v), 3) for v in d07]))

print("\nFAMILY TRIPLE (never summed)")
for a in ARMS:
    print(f"  {a:14s} segs {[dist[a]['segs'][i]['mean'] for i in range(3)]} "
          f"err01 {[dist[a]['segs'][i]['err_le01'] for i in range(3)]} "
          f"d07 k={dist[a]['duty07_k']} m={dist[a]['duty07_mean']} W={dist[a]['duty07_wilson']} "
          f"on={ON[a]} mass={MASS[a]}" + (f" echo={echo[a]['ratio']}" if a in echo else ""))
print("BUDGET", json.dumps(dict(entrain=ENT_MASS, echo=echo)))

# ---------------- fork oracles (per-seed max over noise-shared branches) ----------------
def oracle(name, branches):
    o = dict(name=name, branches=branches)
    for ax, get in (("seg1", lambda a, s: cells[a][str(s)]["segs"][1]["duty"]),
                    ("seg2", lambda a, s: cells[a][str(s)]["segs"][2]["duty"]),
                    ("d07", lambda a, s: cells[a][str(s)]["duty_07"])):
        per = {a: [get(a, s) for s in SEEDS] for a in branches}
        m = {a: round(float(np.mean(v)), 3) for a, v in per.items()}
        omax = [max(per[a][i] for a in branches) for i in range(len(SEEDS))]
        # branch-consistent: pick branch maximizing THIS axis per seed, carry its d07
        pick = [max(branches, key=lambda a: per[a][i]) for i in range(len(SEEDS))]
        d07_of_pick = [cells[pick[i]][str(SEEDS[i])]["duty_07"] for i in range(len(SEEDS))]
        o[ax] = dict(best_fixed=max(m.values()), oracle_mean=round(float(np.mean(omax)), 3),
                     per_arm=m,
                     gap=round(float(np.mean(omax)) - max(m.values()), 3),
                     pick_d07_k=int(np.sum(np.array(d07_of_pick) >= .5)) if ax == "seg1" else None)
    return o


O = [oracle("O1_K0_l84(base==hynohop,A3)", ["hynohop", "cont", "nod", "echo"]),
     oracle("O2_K2000_nohop", ["hynohop", "glide200", "glide300", "glide400"]),
     oracle("O3_K2000_echo", ["hynohop_fb", "hynohop_fb07"]),
     oracle("O4_K2000_hybrid", ["hybrid", "hyglide300"])]
for o in O:
    print(f"\n{o['name']}: " + " | ".join(
        f"{ax} bestfix {o[ax]['best_fixed']} oracle {o[ax]['oracle_mean']} "
        f"(+{o[ax]['gap']})" for ax in ("seg1", "seg2", "d07")))

# ---------------- realizability (L58 instrument): fork-time features vs branch delta ----------------
def spear(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def exit_feats(a):
    F = {}
    for s in SEEDS:
        SL, _ = s_arrays(a, str(s))
        q = (TS >= 1500) & (TS < 2000)
        F.setdefault("SL_exit", []).append(round(float(np.nanmedian(SL[TS[q]])), 3))
        F.setdefault("mm_exit", []).append(round(float(CH[a][str(s)]["mm"][1900:2000].mean()), 5))
    return F


R = {}
Fe = exit_feats("hynohop")  # O2 fork state (shared prefix)
for g in ("glide300", "glide400"):
    d = [cells[g][str(s)]["segs"][1]["duty"] - cells["hynohop"][str(s)]["segs"][1]["duty"]
         for s in SEEDS]
    R[f"O2_{g}_minus_step_vs_SLexit"] = round(spear(d, Fe["SL_exit"]), 3)
    R[f"O2_{g}_minus_step_vs_mmexit"] = round(spear(d, Fe["mm_exit"]), 3)
Fe3 = exit_feats("hynohop_fb")  # O3 fork state (shared prefix through 2000)
d3 = [cells["hynohop_fb07"][str(s)]["segs"][1]["duty"]
      - cells["hynohop_fb"][str(s)]["segs"][1]["duty"] for s in SEEDS]
R["O3_fb07_minus_fb_seg1_vs_SLexit"] = round(spear(d3, Fe3["SL_exit"]), 3)
R["O3_fb07_minus_fb_seg1_vs_mmexit"] = round(spear(d3, Fe3["mm_exit"]), 3)
print("\nREALIZABILITY", json.dumps(R))

out = dict(meta=dict(seeds=SEEDS, source="stored npz l59/l77/l82/l83/l84 — zero reruns",
                     dt=DT, win=WIN),
           anchors={k: v for k, v in A.items()},
           dist=dist, budget=dict(entrain=ENT_MASS, on=ON, mass=MASS, echo=echo),
           oracles=O, realiz=R)
json.dump(out, open("l85/derived.json", "w"), indent=1)
print("\nwritten l85/derived.json")
