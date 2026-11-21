"""L95 law: predict fd from base-arm u(k) traces (the one-probe instrument).

Reads ONLY stored artifacts (raw_l95.npz, raw_l93.npz, results_l93.json,
l93/viability.csv, l95/anchors_run.json). PREREG l95/PREREG.md gates P1-P4.
"""
import json

import numpy as np

BG = 0.02
SEEDS = [11, 22, 33]
SEG = 2000
POOLS = ["Ti_fL", "Ti_fR", "Ti_eL", "Ti_eR", "Tr_fL", "Tr_fR", "Tr_eL", "Tr_eR"]
READS = ["mm", "xm"] + POOLS
z5 = np.load("l95/raw_l95.npz")
z3 = np.load("l93/raw_l93.npz")
R3 = json.load(open("l93/results_l93.json"))
AR5 = json.load(open("l95/anchors_run.json"))
V = __import__("pandas").read_csv("l93/viability.csv")
AMPS = [float(a) for a in z5["amps"]]
UNION = z5["union"]


def log(*a):
    print(*a, flush=True)


# ---------------- C0E: fd/dm metric certification vs stored verdict ----------------
c2 = R3["c2"]
cert = 0
for k, v in c2.items():
    if not (k.startswith("fd_") or k.startswith("dm_")):
        continue
    parts = k.split("_")
    pk = "_".join(parts[1:3])
    a = "_".join(parts[3:-1])
    s = int(parts[-1])
    if k.startswith("fd_"):
        d = np.abs(z3[f"{pk}_{a}_{s}"][:6000] - z3[f"{pk}_base_{s}"][:6000])
        mine = int(np.argmax(d > 0)) if (d > 0).any() else -1
        assert mine == v, (k, mine, v)
    else:
        d = np.abs(z3[f"{pk}_{a}_{s}"][:6000] - z3[f"{pk}_base_{s}"][:6000])
        assert abs(float(d.max()) - v) < 1e-6, (k, float(d.max()), v)
    cert += 1
log(f"C0E metric certification: {cert} c2 reads reproduced EXACTLY")
c0a = AR5["c0_max"]
assert c0a == 0.0, f"C0A/C0B bit-identity FAILED: {c0a}"
log(f"C0A/C0B bit-identity vs raw_l93: max|d| {c0a} (38th chain anchor)")


# ---------------- helpers ----------------
def ub_col(seed, cell):
    j = int(np.where(UNION == cell)[0][0])
    return z5[f"ub_{seed}"][:, j]


def k_open(seed, cells, amp):
    """first k in [0,SEG) with u(k)+amp+BG>0 for ANY cell (min over cells)."""
    best = None
    for c in np.atleast_1d(cells):
        u = ub_col(seed, int(c))
        idx = np.where(u + amp + BG > 0)[0]
        if len(idx) and (best is None or idx[0] < best):
            best = int(idx[0])
    return best


def fd_reads(arm, seed):
    """per-read fd (abs-diff divergence, l93 metric) + earliest finite fd."""
    out = {}
    for r in READS:
        d = np.abs(z5[f"{r}_{arm}_{seed}"] - z5[f"{r}_base_{seed}"])
        out[r] = int(np.argmax(d > 0)) if (d > 0).any() else -1
    finite = [v for v in out.values() if v >= 0]
    out["earliest"] = min(finite) if finite else -1
    return out


# ---------------- fresh d74b sweep: fd vs headroom table ----------------
D74B = z3["d74b"].astype(int)
u74b = {s: ub_col(s, int(D74B[0])) for s in SEEDS}
u74b_max = {s: float(u74b[s].max()) for s in SEEDS}
viab74 = float(V[(V.type == "DNg74_b") & (V.side == "RIGHT")].u_max.iloc[0])
log(f"d74b seg0 u_max per seed: "
    f"{ {s: round(u74b_max[s], 3) for s in SEEDS} } | census u_max {viab74}")

table = []
for amp in AMPS:
    arm = f"d74b_{amp}"
    for s in SEEDS:
        ko = k_open(s, D74B, amp)
        fr = fd_reads(arm, s)
        h_seg0 = amp + u74b_max[s]           # per-window headroom
        table.append(dict(amp=amp, seed=s, h_seg0=round(h_seg0, 3),
                          k_open=ko, fd_E=fr["earliest"], fd_Tr_fL=fr["Tr_fL"],
                          eps_E=(fr["earliest"] - (ko + 1)) if ko is not None
                          and fr["earliest"] >= 0 else None))
log("fresh sweep table (amp, seed, h_seg0, k_open, fd_E, fd_Tr_fL, eps_E):")
for r in table:
    log(f"  {r['amp']:>4} s{r['seed']:<3} h {r['h_seg0']:>6} k_open "
        f"{str(r['k_open']):>5} fd_E {r['fd_E']:>5} Tr_fL {r['fd_Tr_fL']:>5} "
        f"eps {r['eps_E']}")

# ---------------- P1 monotone (2.0/3.0/5.0) ----------------
p1 = {}
for s in SEEDS:
    fds = [next(r["fd_E"] for r in table if r["amp"] == a and r["seed"] == s)
           for a in (2.0, 3.0, 5.0)]
    p1[s] = dict(fds=fds, mono=all(fds[i] >= fds[i + 1] for i in range(2)))
log(f"P1 monotone fd(2.0)>=fd(3.0)>=fd(5.0): "
    f"{ {s: p1[s]['mono'] for s in SEEDS} } fds "
    f"{ {s: p1[s]['fds'] for s in SEEDS} }")

# ---------------- P2 crossing law eps ----------------
eps_fresh = [r["eps_E"] for r in table
             if r["eps_E"] is not None and r["amp"] in (1.8, 2.0, 3.0, 5.0)]
neg = [e for e in eps_fresh if e < 0]
p2 = dict(min_eps=min(eps_fresh), any_negative=bool(neg),
          frac_le8=float(np.mean([e <= 8 for e in eps_fresh])),
          eps_sorted=sorted(eps_fresh))
log(f"P2 eps (fd_E - (k_open+1)): min {p2['min_eps']} | negatives {neg} | "
    f"frac<=8 {p2['frac_le8']:.2f} | all {p2['eps_sorted']}")

# ---------------- P3 pin law (amp 1.5) ----------------
p3 = {}
for s in SEEDS:
    mx = float((u74b[s] + 1.5 + BG).max())
    fr = fd_reads("d74b_1.5", s)
    p3[s] = dict(max_net=round(mx, 4),
                 all_dead=all(v == -1 for v in fr.values() if isinstance(v, int)))
    assert (mx <= 0) == p3[s]["all_dead"], ("pin inconsistency", s, mx, fr)
log(f"P3 pin law amp 1.5: {p3}")

# ---------------- P4 one-probe classification on the l93 arm table ----------------
L93_ARMS = {  # arm -> (cells key in raw_l93, amp)
    "xl080_L_20": ("xl080", 2.0), "d74b_R_20": ("d74b", 2.0),
    "d105_R_20": ("d105", 2.0), "intr16_05": ("int16", 0.5),
    "intr16_20": ("int16", 2.0), "tidon_20": ("ti16", 2.0),
    "shamdn_20a": ("shamdn_a", 2.0), "shamdn_20b": ("shamdn_b", 2.0),
    "shamint_20a": ("shamint_a", 2.0), "shamint_20b": ("shamint_b", 2.0),
}
p4_rows, disagree = [], 0
for a, (ck, amp) in L93_ARMS.items():
    cells = z3[ck].astype(int)
    for s in SEEDS:
        ko = k_open(s, cells, amp)
        meas = c2[f"fd_Tr_fL_{a}_{s}"]
        pred_pinned = ko is None
        meas_pinned = meas == -1
        if pred_pinned != meas_pinned:
            disagree += 1
        p4_rows.append(dict(arm=a, seed=s, n_cells=len(cells), amp=amp,
                            k_open=ko, pred=(ko + 1) if ko is not None else -1,
                            meas_Tr_fL=meas))
un = [r for r in p4_rows if r["k_open"] is not None and r["meas_Tr_fL"] >= 0]


def ranks(v):
    v = np.asarray(v, float)
    o = np.argsort(v)
    rk = np.empty(len(v), float)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
            j += 1
        rk[o[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


rho = spearman([r["k_open"] + 1 for r in un], [r["meas_Tr_fL"] for r in un])
log(f"P4 pinned-classification disagreements: {disagree} | un-pinned cells "
    f"{len(un)} | Spearman(k_open+1, fd_Tr_fL) = {rho:.3f}")
log("P4 table (arm, seed, k_open, pred fd, meas fd_Tr_fL):")
for r in p4_rows:
    log(f"  {r['arm']:<12} s{r['seed']:<3} n{r['n_cells']:<3} "
        f"k_open {str(r['k_open']):>5} pred {r['pred']:>5} meas {r['meas_Tr_fL']:>5}")

# ---------------- F2 descriptive (naive hyperbola) ----------------
hs = [r["h_seg0"] for r in table if r["fd_E"] >= 0 and r["amp"] > 1.5]
fs = [r["fd_E"] for r in table if r["fd_E"] >= 0 and r["amp"] > 1.5]
f2_rho = spearman(1.0 / np.maximum(hs, 1e-6), fs)
log(f"F2 descriptive: Spearman(1/headroom, fd_E) fresh sweep = {f2_rho:.3f}")

# ---------------- verdict ----------------
verdict = dict(
    c0e_certified=cert, c0a=c0a,
    p1={str(s): p1[s] for s in SEEDS},
    p1_pass=all(p1[s]["mono"] for s in SEEDS),
    p2=p2, p2_pass=(not p2["any_negative"]),
    p2_sharp_pass=p2["frac_le8"] >= 2 / 3,
    p3={str(s): p3[s] for s in SEEDS},
    p3_pass=all(p3[s]["all_dead"] for s in SEEDS),
    p4_disagree=disagree, p4_rho=round(rho, 4),
    p4_pass=(disagree == 0 and rho >= 0.90),
    f2_rho=round(f2_rho, 3),
    u74b_seg0_max={str(s): u74b_max[s] for s in SEEDS},
    u74b_census=viab74)
json.dump(verdict, open("l95/results_l95.json", "w"), indent=1)
import csv
with open("l95/fd_headroom.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(table[0].keys()))
    w.writeheader()
    w.writerows(table)
log(f"VERDICT: P1 {verdict['p1_pass']} | P2 {verdict['p2_pass']} "
    f"(sharp {verdict['p2_sharp_pass']}) | P3 {verdict['p3_pass']} | "
    f"P4 {verdict['p4_pass']} (rho {rho:.3f}, disagree {disagree})")
