"""L95 ADDENDUM 1: earliest-pool fd (fd_E) for the stored l93 arms.

Registered P4 read fd_Tr_fL dilutes rank for already-open cells (pool-specific
visibility lag 0-34); the fresh sweep showed fd_E = k_open+1 EXACT (eps 0,
10/10). This addendum recomputes fd_E for every stored l93 arm from
raw_l93.npz (all pool traces stored; metric = C0E-certified abs-diff fd) and
re-runs the P4 rank test on fd_E. Post-run amendment, disclosed as ADDENDUM 1
(L44 discipline: labeled, evidence-only, no gate silently rewritten).
"""
import json

import numpy as np

BG = 0.02
SEEDS = [11, 22, 33]
POOLS = ["Ti_fL", "Ti_fR", "Ti_eL", "Ti_eR", "Tr_fL", "Tr_fR", "Tr_eL", "Tr_eR"]
READS = ["mm", "xm"] + POOLS
z3 = np.load("l93/raw_l93.npz")
z5 = np.load("l95/raw_l95.npz")
R3 = json.load(open("l93/results_l93.json"))
c2 = R3["c2"]
UNION = z5["union"]

L93_ARMS = {
    "xl080_L_20": ("xl080", 2.0), "d74b_R_20": ("d74b", 2.0),
    "d105_R_20": ("d105", 2.0), "intr16_05": ("int16", 0.5),
    "intr16_20": ("int16", 2.0), "tidon_20": ("ti16", 2.0),
    "shamdn_20a": ("shamdn_a", 2.0), "shamdn_20b": ("shamdn_b", 2.0),
    "shamint_20a": ("shamint_a", 2.0), "shamint_20b": ("shamint_b", 2.0),
}


def ub_col(seed, cell):
    return z5[f"ub_{seed}"][:, int(np.where(UNION == cell)[0][0])]


def k_open(seed, cells, amp):
    best = None
    for c in np.atleast_1d(cells):
        u = ub_col(seed, int(c))
        idx = np.where(u + amp + BG > 0)[0]
        if len(idx) and (best is None or idx[0] < best):
            best = int(idx[0])
    return best


def fd_E(a, s):
    out = {}
    for r in READS:
        d = np.abs(z3[f"{r}_{a}_{s}"] - z3[f"{r}_base_{s}"])
        out[r] = int(np.argmax(d > 0)) if (d > 0).any() else -1
    finite = [v for v in out.values() if v >= 0]
    e = min(finite) if finite else -1
    pool = min(out, key=lambda r: out[r] if out[r] >= 0 else 10 ** 9)
    return e, pool


rows = []
for a, (ck, amp) in L93_ARMS.items():
    cells = z3[ck].astype(int)
    for s in SEEDS:
        ko = k_open(s, cells, amp)
        e, pool = fd_E(a, s)
        rows.append(dict(arm=a, seed=s, amp=amp, k_open=ko, fd_E=e,
                         first_pool=pool, eps=(e - (ko + 1)) if ko is not None
                         and e >= 0 else None))
        print(f"{a:<12} s{s:<3} k_open {str(ko):>5} fd_E {e:>5} "
              f"eps {rows[-1]['eps']} first_pool {pool}")

un = [r for r in rows if r["k_open"] is not None and r["fd_E"] >= 0]
eps_all = [r["eps"] for r in un]
print(f"\nun-pinned cells {len(un)} | eps(fd_E - (k_open+1)): "
      f"min {min(eps_all)} max {max(eps_all)} | "
      f"frac==0 {np.mean([e == 0 for e in eps_all]):.3f} | "
      f"frac<=2 {np.mean([e <= 2 for e in eps_all]):.3f}")


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


rho_E = spearman([r["k_open"] + 1 for r in un], [r["fd_E"] for r in un])
print(f"ADDENDUM P4 on fd_E: Spearman(k_open+1, fd_E) = {rho_E:.3f} "
      f"(n {len(un)})")

res = json.load(open("l95/results_l95.json"))
res["addendum1"] = dict(
    note="P4 re-read on earliest-pool fd (stored l93 pool traces, "
         "C0E-certified metric); registered fd_Tr_fL read failed rho .529 "
         "from pool-visibility lag on already-open cells, disclosed.",
    rows=rows, rho_E=round(rho_E, 4),
    eps_max=max(eps_all), eps_frac0=round(float(np.mean(
        [e == 0 for e in eps_all])), 3))
json.dump(res, open("l95/results_l95.json", "w"), indent=1)
print("results_l95.json updated (addendum1)")
