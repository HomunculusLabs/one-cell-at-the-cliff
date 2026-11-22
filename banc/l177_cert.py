"""L177 stage (b) CERTIFICATION CORE — C0S-177 (static) + C0A-177 (forward-chain
bit-identity anchor), per l177/PREREG.md section 4.

Build block copied VERBATIM from l65_banc_oppoint.py (stage 0 + stage 2a + run()),
with l65's stage 1 (full-graph bisection) omitted: it feeds only P1 and every
stage-2 rollout seeds its OWN torch.Generator, so omitting it cannot move any
stage-2 draw. Threads pinned to 8 to match l65.

Writes l177/cert.json + stdout. Reads l65/* READ-ONLY. Zero new science.
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 400
CONF_WIN = 6000     # 60 s
CONF_SEEDS = [11, 22, 33]
PAIR_KEYS = ["Ti", "Tr"]
D = "/home/t3rpz/critters/peabrain-lab/banc/data"
os.makedirs("l177", exist_ok=True)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------------- stage 0: graph + annotations (l65 verbatim) -------------
G = torch.load("banc_graph.pt", weights_only=False)
ids_all = G["ids"].numpy().astype(np.uint64)
Nall = int(G["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = G["sign"].numpy()

ann = pd.read_csv(f"{D}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv(f"{D}/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64),
                  nt["neurotransmitter_predicted"].astype(str).str.lower()))
is_glut = np.zeros(Nall, bool)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate":
        is_glut[j] = True
log(f"graph {Nall:,} nnz {G['n_edges']:,} | glut cells {is_glut.sum():,} "
    f"| {time.time()-t0:.0f}s")

# ---------------- stage 2a: cord subnet (l65 verbatim) --------------------
region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True

conn = pd.read_csv(f"{D}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all)
            & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
pre = np.array([int(a) for a, _ in g_grp.index], np.int64)
post = np.array([int(b) for _, b in g_grp.index], np.int64)
src_all = np.array([idx_all[r] for r in pre], np.int64)
dst_all = np.array([idx_all[r] for r in post], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into &= dn_all
keep = cord_mask | dn_into

emask = keep[src_all] & keep[dst_all]
gsrc, gdst = src_all[emask], dst_all[emask]
gcount = w_syn[emask]

loc = -np.ones(Nall, np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
gsign_a = sign_all[gsrc]
gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
Wa_vals = (np.log1p(gcount) * gsign_a).astype(np.float32)
Wb_vals = (np.log1p(gcount) * gsign_b).astype(np.float32)
log(f"subnet n {n:,} edges {len(lsrc):,} | cord {int(cord_mask.sum()):,} "
    f"dn_into {int(dn_into.sum()):,} | {time.time()-t0:.0f}s")

mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
mgi = mot_rows.gi.to_numpy()
in_sub = keep[mgi]


def pool(sel_str):
    m = in_sub & sel_str
    return loc[mgi[m]]


def has(s):
    return np.array([s in t for t in ptt])


PAIRS = {}
for k, fpat, epat in [
    ("Ti", (has("tibia") & has("flexor")), (has("tibia") & has("extensor"))),
    ("Tr", (has("trochanter") & has("flexor")), (has("trochanter") & has("extensor"))),
]:
    PAIRS[k] = (pool(fpat), pool(epat))

sub_dn = ann[ann.super_class == "descending"]
dng100_all = sub_dn.gi[sub_dn.cell_type.fillna("").astype(str)
                        .to_numpy() == "DNg100"].to_numpy()
dng100 = np.sort(loc[dng100_all[keep[dng100_all]]])
motor = np.zeros(n, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor[loc[mg[keep[mg]]]] = True


def build_W(dst, src, vals):
    t = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([dst, src])).long(),
        torch.from_numpy(vals.astype(np.float32)), (n, n))
    return t.coalesce().to_sparse_csr()


Wb = build_W(ldst, lsrc, Wb_vals)
log(f"arm B built (nnz {Wb._nnz():,}) | {time.time()-t0:.0f}s")


# ---------------- rollout (l65 verbatim) ----------------------------------
def run(Wc, g, beta, d, seed, win, want_traces=False):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= beta
    Wbeta = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals,
                                    Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = d
    Z = torch.zeros(n, 1)

    def step(cur, drive_I):
        drive = torch.sparse.mm(Wbeta, cur) * g + drive_I
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for _ in range(SETTLE):
        X = step(X, Z)
    af = float((X > 0.05).float().mean())
    assert 0.01 < af < 0.9, f"op-point {af:.3f}"
    assert not torch.isnan(X).any(), "NaN"
    T = win
    traces = {k: (np.zeros(T, np.float32), np.zeros(T, np.float32))
              for k in PAIRS} if want_traces else None
    mm = np.zeros(T, np.float32) if want_traces else None
    for k in range(T):
        X = step(X, I)
        if want_traces:
            for pk, (f, e) in PAIRS.items():
                traces[pk][0][k] = X[f].mean()
                traces[pk][1][k] = X[e].mean()
            mm[k] = X[motor].mean()
    out_S, out_d = {}, {}
    if want_traces:
        sl = slice(int(0.25 * T), T)
        for pk in PAIRS:
            a = traces[pk][0][sl]
            b = traces[pk][1][sl]
            out_d[pk] = float(max(np.ptp(a), np.ptp(b)))
            sa, sb = a.std(), b.std()
            out_S[pk] = float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else np.nan
    return af, out_S, out_d, traces, mm


# ---------------- C0S-177: static cert vs l65's stored values -------------
stored = json.load(open("l65/results_l65.json"))
sB = stored["arms"]["B"]
fz = sB["frozen"]

# arm-B g band, l65 verbatim (certifies the gstar float itself, not a quote)
ok = []
for g in np.logspace(-7, -1, 13):
    try:
        af, *_ = run(Wb, float(g), 1.0, 0.0, 11, 50)
        if 0.02 < af < 0.60:
            ok.append(float(g))
    except AssertionError:
        pass
gstar_sub = float(np.exp(np.mean(np.log(ok)))) if ok else float("nan")

C0S = dict(
    n=(n, stored["subnet"]["n"]),
    edges=(len(lsrc), stored["subnet"]["edges"]),
    cord=(int(cord_mask.sum()), stored["subnet"]["cord"]),
    dn_into=(int(dn_into.sum()), stored["subnet"]["dn_into"]),
    Ti=( [len(PAIRS["Ti"][0]), len(PAIRS["Ti"][1])], stored["pools"]["Ti"]),
    Tr=( [len(PAIRS["Tr"][0]), len(PAIRS["Tr"][1])], stored["pools"]["Tr"]),
    dng100=(int(len(dng100)), 2),
    gband=(ok, sB["g_band"]),
    gstar=(repr(gstar_sub), repr(sB["gstar"])),
    frozen_g=(repr(gstar_sub * 1.4), repr(fz["g"])),
    frozen_beta=(fz["beta"], 2.0),
    frozen_d=(fz["d"], 0.2),
    frozen_af=(round(fz["af"], 4), 0.1038),
)
c0s_pass = {k: (v[0] == v[1]) for k, v in C0S.items()}
for k, v in C0S.items():
    log(f"C0S {k:11s} {'OK ' if c0s_pass[k] else 'FAIL'} mine={v[0]} stored={v[1]}")
assert all(c0s_pass.values()), "C0S-177 FAILED — halt, analyse nothing"
log(f"C0S-177 PASS ({len(c0s_pass)} cells) | {time.time()-t0:.0f}s")

# ---------------- C0A-177: forward-chain bit-identity anchor --------------
ref = np.load("l65/raw_l65.npz")
anchor = {}
conf = {}
for s in CONF_SEEDS:
    af, S, dd, tr, mm = run(Wb, fz["g"], fz["beta"], fz["d"], s, CONF_WIN, True)
    conf[s] = dict(af=af, S=S, depth=dd)
    for pk in PAIRS:
        for suf, arr in (("f", tr[pk][0]), ("e", tr[pk][1])):
            key = f"B_s{s}_{pk}_{suf}"
            anchor[key] = float(np.max(np.abs(arr - ref[key])))
    anchor[f"B_s{s}_mm"] = float(np.max(np.abs(mm - ref[f"B_s{s}_mm"])))
    log(f"  anchor seed {s}: af {af:.4f} S {{Ti {S['Ti']:.4f} Tr {S['Tr']:.4f}}} "
        f"| max|d| {max(v for k, v in anchor.items() if f'_s{s}_' in k):.3e} "
        f"| {time.time()-t0:.0f}s")

a_max = max(anchor.values())
# S re-derivation against the stored confirm block (metric-code cert, L85)
stored_conf = {p["seed"]: p for p in sB["confirm"]}
s_match = {s: all(conf[s]["S"][pk] == stored_conf[s]["S"][pk] for pk in PAIRS)
           and conf[s]["af"] == stored_conf[s]["af"] for s in CONF_SEEDS}
log(f"C0A-177 max|d| over {len(anchor)} traces = {a_max:.6e}")
log(f"C0A-177 stored-S/af exact match per seed: {s_match}")
c0a_pass = (a_max == 0.0) and all(s_match.values())

json.dump(dict(
    c0s={k: dict(mine=v[0], stored=v[1], ok=c0s_pass[k]) for k, v in C0S.items()},
    c0s_pass=bool(all(c0s_pass.values())),
    anchor_maxd=anchor, anchor_max=a_max,
    s_match={str(k): bool(v) for k, v in s_match.items()},
    confirm={str(s): dict(af=conf[s]["af"], S=conf[s]["S"], depth=conf[s]["depth"])
             for s in CONF_SEEDS},
    c0a_pass=bool(c0a_pass),
    gstar_sub=gstar_sub, frozen=fz, n=n, edges=int(len(lsrc)),
    wall_s=time.time() - t0,
), open("l177/cert.json", "w"), indent=1)

log(f"C0A-177 {'PASS' if c0a_pass else 'FAIL'} | wall {time.time()-t0:.0f}s "
    f"-> l177/cert.json")
assert c0a_pass, "C0A-177 FAILED — halt per PREREG section 4"
log("CERT CORE GREEN: stage (b) may proceed from this build.")
