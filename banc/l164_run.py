"""L164 run: the slow-line ORIGIN rollout arm (PREREG l164/PREREG.md FIRST,
drive pre-measurement GATE passed in l164/drive_static.json).

Substrate: b65 (= keep_old closure) VERBATIM from l154_run.py's extraction,
G65 = 0.14 stored constant, no bisect (graph-identity). Two arms on ONE
shared noise stream per seed:
  fix — o_s = 0, the stored protocol (positive control + C0A bit-anchor)
  rnd — per-seed random drive onset phase (l164_drive.drive_series)
Fresh batch B42 4201-4216 + anchors 801/901 (fix only).
Raw checkpoint BEFORE analysis (L43). CPU-only.
"""
import json
import math
import os
import time

import numpy as np
import pandas as pd
import torch

from l164_drive import B42, OFF, drive_series   # gate re-fires on import

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN = 400, 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
BETA, D = 2.0, 0.2
ENT_AMP = 0.1
G65 = 0.14
ANCH = [801, 901]
SEEDS = ANCH + B42
OFF_OF = dict(zip(B42, OFF))
S92 = json.load(open("l92/static.json"))
S101 = json.load(open("l101/static.json"))["sizes"]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ---------------- extraction (l154_run.py VERBATIM, trimmed to b65) --------
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()

ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv("data/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64),
                  nt["neurotransmitter_predicted"].astype(str).str.lower()))
is_glut = np.zeros(Nall, bool)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate":
        is_glut[j] = True

region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True

conn = pd.read_csv("data/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = (conn["pre_root_id"].astype(np.uint64).isin(idx_all)
        & conn["post_root_id"].astype(np.uint64).isin(idx_all))
conn = conn[in_g]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into = dn_into & dn_all
dn_proj = np.zeros(Nall, bool)
dn_proj[src_all[cord_mask[dst_all]]] = True
dn_proj = dn_proj & dn_all
keep_old = cord_mask | dn_into
keep_new = cord_mask | dn_into | dn_proj
assert int(keep_old.sum()) == S92["n_old"] and int(keep_new.sum()) == S92["n_new"]
gi_new = np.where(keep_new)[0]
gi_old = np.where(keep_old)[0]
dn_new_g = gi_new[~np.isin(gi_new, gi_old)]
assert len(dn_new_g) == S92["dn_new"]
n_old, n_add = int(keep_old.sum()), len(dn_new_g)


def build(keep):
    emask = keep[src_all] & keep[dst_all]
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    lsrc, ldst = loc[gsrc], loc[gdst]
    gsign_a2 = sign_all[gsrc]
    gsign_b2 = np.where(is_glut[gsrc], -np.abs(gsign_a2), gsign_a2)
    vals = (np.log1p(gcount) * gsign_b2).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([ldst, lsrc])).long(),
        torch.from_numpy(vals), (int(keep.sum()), int(keep.sum()))
    ).coalesce().to_sparse_csr()
    return W, loc


def wb(W):
    neg = W.values() < 0
    vals = W.values().clone()
    vals[neg] *= BETA
    return torch.sparse_csr_tensor(W.crow_indices(), W.col_indices(), vals, W.shape)


Wc_o, loc_o = build(keep_old)
assert Wc_o.values().numel() == S92["edges_old"]
Wb_o = wb(Wc_o)

mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


def pools_for(loc, keep):
    out = {}
    for k, fpat, epat, pf, pe in [
        ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor"),
         "f", "e"),
        ("Tr", has("trochanter") & has("flexor"),
         has("trochanter") & has("extensor"), "f", "e"),
        ("Ta", has("tarsus") & has("depressor"), has("tarsus") & has("levator"),
         "a", "b"),
        ("Sr", has("sternal") & has("anterior") & has("rotator"),
         has("sternal") & has("posterior") & has("rotator"), "a", "b"),
        ("Pr", has("promotor"), has("remotor"), "a", "b"),
    ]:
        for c in ("L", "R"):
            m = keep[mgi] & fpat & (side_m == SIDE_MAP[c])
            out[f"{k}_{pf}{c}"] = np.sort(loc[mgi[m]])
            m = keep[mgi] & epat & (side_m == SIDE_MAP[c])
            out[f"{k}_{pe}{c}"] = np.sort(loc[mgi[m]])
    return out


POOLS = pools_for(loc_o, keep_old)
for pk, want in S92["pool_sizes"].items():
    assert len(POOLS[pk]) == want, pk
for pk, want in S101.items():
    if pk.split("_")[0] in ("Ti", "Tr"):
        continue
    assert len(POOLS[pk]) == want, pk

cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech_o = np.where(mech_mask[keep_old])[0]
mg_all = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor_o = np.zeros(n_old, bool)
motor_o[loc_o[mg_all[keep_old[mg_all]]]] = True
sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100_o = np.sort(loc_o[dng100_all[keep_old[dng100_all]]])
assert len(dng100_o) == S92["dng100"]
log(f"graph built {time.time()-t0:.0f}s | n_old {n_old:,} "
    f"edges {Wc_o.values().numel():,} | mech {len(mech_o)} "
    f"motor {int(motor_o.sum())} DNg100 {len(dng100_o)}")

# drive waveforms (imported constructor — never re-transcribed, L85)
S_FIX, _ = drive_series(0)
S_RND = {s: drive_series(OFF_OF[s])[0] for s in B42}
ARMS = ["fix", "rnd"]
CHANNELS = sorted(POOLS) + ["mm", "xm"]

# ---------------- B42 absence across every stored npz (L157) --------------
_prev = []
for root, _dirs, files in os.walk("."):
    for fn in files:
        if fn.endswith(".npz") and not root.startswith("./l164"):
            _prev.append(os.path.join(root, fn))
for _p in sorted(_prev):
    try:
        _z = np.load(_p)
    except Exception:
        continue
    assert not any(f"mm_b65_{s_}" in _z.files or f"mm_fix_{s_}" in _z.files
                   for s_ in B42), f"B42 collides with {_p} (STOP)"
log(f"B42 absence across {len(_prev)} stored npzs: PASS")

# ---------------- rollouts ------------------------------------------------
store = {}
if os.path.exists("l164/raw_partial.npz"):
    z = np.load("l164/raw_partial.npz")
    store = {k: z[k] for k in z.files}
Iv = torch.zeros(n_old, 1)
Iv[dng100_o] = D
for seed in SEEDS:
    arms = ["fix"] if seed in ANCH else ARMS
    if all(f"mm_{a}_{seed}" in store for a in arms):
        log(f"seed {seed} cached, skip")
        continue
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    _X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    X = {a: X0o.clone() for a in arms}
    off = {"fix": 0, "rnd": OFF_OF.get(seed, 0)}
    sp = {a: 2 * math.pi * 0.7 * DT * off[a] for a in arms}
    for _ in range(SETTLE):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        _nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        for a in arms:
            sp[a] += 2 * math.pi * 0.7 * DT
            sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp[a]))
            drive = torch.sparse.mm(Wb_o, X[a]) * G65 + Iv
            drive[mech_o, 0] = drive[mech_o, 0] + sin_t
            X[a] = X[a] + (DT / TAU) * ((torch.relu(drive + BG) + nz_o)
                                        .clamp(max=RMAX) - X[a])
    af_c = {a: float((X[a] > 0.05).float().mean()) for a in arms}
    for a in arms:
        assert 0.01 < af_c[a] < 0.9, (a, af_c[a])     # L30 op point
    SV = {"fix": S_FIX, "rnd": S_RND.get(seed, S_FIX)}
    mm = {a: np.zeros(WIN, np.float32) for a in arms}
    xm = {a: np.zeros(WIN, np.float32) for a in arms}
    tr = {a: {kk: np.zeros(WIN, np.float32) for kk in POOLS} for a in arms}
    for k in range(WIN):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        _nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        for a in arms:
            sin_t = float(SV[a][k])
            drive = torch.sparse.mm(Wb_o, X[a]) * G65 + Iv
            if sin_t > 0:
                drive[mech_o, 0] = drive[mech_o, 0] + sin_t
            t = torch.relu(drive + BG)
            t = (t + nz_o).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
            mm[a][k] = X[a][motor_o].mean()
            xm[a][k] = X[a][mech_o].mean()
            for kk in POOLS:
                tr[a][kk][k] = X[a][POOLS[kk]].mean()
    for a in arms:
        store[f"mm_{a}_{seed}"] = mm[a]
        store[f"xm_{a}_{seed}"] = xm[a]
        for kk in POOLS:
            store[f"{kk}_{a}_{seed}"] = tr[a][kk]
        store[f"af_{a}_{seed}"] = np.float32(af_c[a])
    np.savez("l164/raw_partial.npz", **store)
    log(f"seed {seed} done af {af_c} off {off} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")
np.savez_compressed("l164/raw_l164.npz", g65=G65, arms=np.array(ARMS),
                    batches=np.array(SEEDS), ent_amp=ENT_AMP,
                    offsets=np.array([OFF_OF[s] for s in B42]), **store)
log("raw_l164.npz checkpointed BEFORE analysis")

# ---------------- C0A-164 bit-identity vs l150 stored b65 -----------------
z150 = np.load("l150/raw_l150.npz")
c0a = {}
for s_ in ANCH:
    for ch in CHANNELS:
        assert f"{ch}_b65_{s_}" in z150.files, (ch, s_)
        c0a[f"{ch}_{s_}"] = float(np.abs(
            store[f"{ch}_fix_{s_}"] - z150[f"{ch}_b65_{s_}"][:WIN]).max())
    c0a[f"af_{s_}"] = abs(float(store[f"af_fix_{s_}"])
                          - float(z150[f"af_b65_{s_}"]))
c0a_max = max(c0a.values())
c0a_pass = bool(all(v == 0.0 for v in c0a.values()))
json.dump(dict(g65=G65, seeds=SEEDS, anchors=ANCH, offsets=OFF_OF,
               c0a_max=c0a_max, c0a_pass=c0a_pass,
               n_checks=len(c0a)),
          open("l164/anchors_run.json", "w"), indent=1)
log(f"C0A-164 fix vs l150 STORED b65 ({len(c0a)} checks): "
    f"{'PASS' if c0a_pass else 'FAIL'} (max {c0a_max:.1e}) "
    f"| {time.time()-t0:.0f}s")
assert c0a_pass, "C0A-164 FAIL (STOP before verdict)"
