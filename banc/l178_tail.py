# ================= L178 TAIL (appended by l178_build.py) =================
# Everything above this line is l151_static.py lines 1-319 VERBATIM, so every
# L151/L142/L134/L92/L101 pin re-ran as free certification before any L178
# value is read. PREREG: l178/PREREG.md (registered first). Writes
# l178/static.json ONLY. No rollout batches; one 400-step settle per seed
# defines the linearization point, plus one nonlinear step as a self-check.
import math

import numpy as np  # noqa: F811  (already imported in head; explicit here)

o = {"design": "L178 linearized top-k path contribution on the f4wA floor-4 "
     "substrate. PREREG l178/PREREG.md. Operator J = g*diag(a)@W_beta; "
     "pool reach = complete length-d WALK sum of J into the 20 semantic "
     "motor pools, ABS and SIGNED forms reported separately.",
     "prereg": "l178/PREREG.md"}

TAU_L, DT_L, RMAX_L = 0.05, 0.01, 1.0
BG_L, NOISE_L = 0.02, 0.01
SETTLE_L = 400
BETA_L, DRIVE_D = 2.0, 0.2
ENT_AMP_L = 0.1
FLOOR = 4
GI_CARRIER = 1110
AF_T_L = 0.10905611018339793
AF_BAND = (0.095, 0.125)

S169B = json.load(open("l169b/static.json"))
F4 = S169B["forms"]["F3_fully_rederived"]

# ---------------- CERT-F4: f4 ladder re-derived (l169b2_run.py 668-701) ------
pm4 = w_syn >= FLOOR
_om4 = out_rows & cord_of_dst & pm4
outmass4 = np.zeros(Nall)
np.add.at(outmass4, src_all[_om4], np.abs(vals_all[_om4]))
_cm4 = outmass4[dn_new_g]
_tot4 = float(_cm4.sum())
_o4 = np.argsort(-_cm4)
_cum4 = np.cumsum(_cm4[_o4]) / _tot4
K4 = int(np.searchsorted(_cum4, 0.50) + 1)
heav4 = dn_new_g[_o4[:K4]]
ng4 = heav4[~is_glut[heav4]]
assert K4 == F4["K"] == 73, (K4, "f4 K drift (STOP)")
assert int((~is_glut[heav4]).sum()) == F4["n_ng"] == 55
assert int(is_glut[heav4].sum()) == F4["n_glut"] == 18
_r_car = int(np.where(ng4 == GI_CARRIER)[0][0]) + 1
_r_319 = int(np.where(ng4 == int(ng_desc[25]))[0][0]) + 1
assert _r_car == F4["carrier_rank"] == 21, (_r_car, "f4 carrier rank")
assert _r_319 == F4["twin_rank"] == 33, (_r_319, "319 f4 rank")
_jac4 = (len(set(int(x) for x in heav) & set(int(x) for x in heav4))
         / len(set(int(x) for x in heav) | set(int(x) for x in heav4)))
assert round(_jac4, 4) == F4["jaccard_heavy"] == 0.9231, _jac4
assert int((emask_n & pm4).sum()) == F4["closure_edges"] == 472095
assert int((emask_wA & pm4).sum()) == F4["wA_edges"] == 469256
GI_TWIN4 = int(ng4[21])
assert GI_TWIN4 == 290, (GI_TWIN4, "f4 twin != DNpe005-R gi 290 (STOP)")
_gap4 = abs(float(outmass4[GI_TWIN4] - outmass4[GI_CARRIER]) / _tot4)
assert round(_gap4, 6) == 2.4e-05, (_gap4, "f4 twin mass gap drift (STOP)")
# f4wA node/edge pins (l169b2/run.out line 2: n 21,789 | edges 469,618)
keep_f4 = keep_new.copy()
keep_f4[np.sort(ng4[:20])] = False
emask_f4 = keep_f4[src_all] & keep_f4[dst_all] & pm4
assert int(keep_f4.sum()) == 21789, (int(keep_f4.sum()), "f4wA n (STOP)")
assert int(emask_f4.sum()) == 469618, (int(emask_f4.sum()), "f4wA edges (STOP)")
assert keep_f4[GI_CARRIER] and keep_f4[GI_TWIN4], "actor dropped (STOP)"
FAMILY = [int(x) for x in ng4[22:] if keep_f4[int(x)]]
assert len(FAMILY) == 33, (len(FAMILY), "family size (STOP)")
log(f"[CERT-F4] GREEN K4 {K4} carrier r{_r_car} twin gi {GI_TWIN4} "
    f"gap {_gap4:.2e} | f4wA n {int(keep_f4.sum()):,} "
    f"edges {int(emask_f4.sum()):,} | family {len(FAMILY)}")
o["cert_f4"] = dict(K4=K4, carrier_rank=_r_car, twin_gi=GI_TWIN4,
                    mass_gap_rel=_gap4, n_f4wA=int(keep_f4.sum()),
                    edges_f4wA=int(emask_f4.sum()), n_family=len(FAMILY))

# ---------------- gains: stored, FLOAT EQUALITY (CERT-F4 second leg) --------
_z = np.load("l169b2/raw_l169b2.npz", allow_pickle=True)
G_F4WA = float(_z["g_f4wA"])
assert G_F4WA == 0.15051452517509462, (G_F4WA, "g_f4wA drift (STOP)")
assert float(_z["g_f4ng"]) == 0.16230986118316648, "g_f4ng drift (STOP)"
assert float(_z["g_f4tw"]) == 0.15261898636817928, "g_f4tw drift (STOP)"
assert int(_z["floor"]) == FLOOR and int(_z["K4"]) == K4
o["gains"] = dict(g_f4wA=G_F4WA, g_f4ng=float(_z["g_f4ng"]),
                  g_f4tw=float(_z["g_f4tw"]))
del _z

# ---------------- channels (l169b2_run.py 545-548 / 564 / 587-589) ----------
cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
assert int(mech_mask[keep_new].sum()) == S92["mech"], "mech size (STOP)"

# ---------------- local build (l169b2 build_e form) -------------------------
loc_f4 = -np.ones(Nall, np.int64)
loc_f4[keep_f4] = np.arange(int(keep_f4.sum()))
loc_new = -np.ones(Nall, np.int64)
loc_new[keep_new] = np.arange(int(keep_new.sum()))
_ei = np.where(emask_f4)[0]
lsrc = loc_f4[src_all[_ei]]
ldst = loc_f4[dst_all[_ei]]
_sa = sign_all[src_all[_ei]]
_sb = np.where(is_glut[src_all[_ei]], -np.abs(_sa), _sa)
evals = (np.log1p(w_syn[_ei]) * _sb).astype(np.float32)
NL = int(keep_f4.sum())
W = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy(evals), (NL, NL)).coalesce().to_sparse_csr()
assert int(W.values().numel()) == int(emask_f4.sum()), "coalesce changed nnz"
_v = W.values().clone()
_v[_v < 0] *= BETA_L
WBETA = torch.sparse_csr_tensor(W.crow_indices(), W.col_indices(), _v, W.shape)

# ---- CSR ORIENTATION (card rule 3): W[target, source] against atlas rows ---
_crow = W.crow_indices().numpy()
_ccol = W.col_indices().numpy()
LC_CAR, LC_TWIN = int(loc_f4[GI_CARRIER]), int(loc_f4[GI_TWIN4])
_n_out_global = int((emask_f4 & (src_all == GI_CARRIER)).sum())
_n_in_global = int((emask_f4 & (dst_all == GI_CARRIER)).sum())
assert int((_ccol == LC_CAR).sum()) == _n_out_global, "CSR orientation (STOP)"
assert int(_crow[LC_CAR + 1] - _crow[LC_CAR]) == _n_in_global, \
    "CSR orientation rows (STOP)"
log(f"[CSR] W[target,source] GREEN: carrier out {_n_out_global} in "
    f"{_n_in_global} (local {LC_CAR})")
o["csr_orientation"] = dict(carrier_local=LC_CAR, out_edges=_n_out_global,
                            in_edges=_n_in_global, convention="W[target,source]")

# ---------------- pools, local ----------------------------------------------
POOL_L = {pk: np.where(P[keep_f4])[0] for pk, P in POOL_G.items()}
for pk, want in S92["pool_sizes"].items():
    assert len(POOL_L[pk]) == want, (pk, "pool size on f4wA (STOP)")
POOL_ALL = np.unique(np.concatenate([POOL_L[pk] for pk in POOL_L]))
PAIRS = [("Ti_fL", "Ti_eL"), ("Ti_fR", "Ti_eR"), ("Tr_fL", "Tr_eL"),
         ("Tr_fR", "Tr_eR"), ("Ta_aL", "Ta_bL"), ("Ta_aR", "Ta_bR"),
         ("Sr_aL", "Sr_bL"), ("Sr_aR", "Sr_bR"), ("Pr_aL", "Pr_bL"),
         ("Pr_aR", "Pr_bR")]
assert len(POOL_L) == 20 and len(PAIRS) == 10
POOL_GLOBAL_ANY = np.zeros(Nall, bool)
for _pk in POOL_G:
    POOL_GLOBAL_ANY |= POOL_G[_pk]
o["pools"] = dict(n_pools=len(POOL_L), n_pool_cells=int(len(POOL_ALL)),
                  sizes={pk: int(len(v)) for pk, v in POOL_L.items()})

mech_l = np.where(mech_mask[keep_f4])[0]
dng_l = np.sort(loc_f4[dng100_all[keep_f4[dng100_all]]])
assert len(mech_l) == S92["mech"] and len(dng_l) == S92["dng100"]
I_vec = torch.zeros(NL, 1)
I_vec[dng_l] = DRIVE_D

# ---------------- settle (l169b2 two-generator form, single arm) ------------
gi_old_idx = np.where(keep_old)[0]
n_old_L = int(keep_old.sum())
n_add_L = len(dn_new_g)
OLDPOS = loc_f4[gi_old_idx]
KEPTMASK = keep_f4[dn_new_g]
KEPTNEW = loc_f4[dn_new_g[KEPTMASK]]
POSINNEW = loc_new[np.where(keep_f4)[0]]
assert (OLDPOS >= 0).all() and (KEPTNEW >= 0).all()


def settle_f4(seed, g=G_F4WA):
    """l169b2 settle law, f4wA arm only (L139 spectator law: arms evolve
    independently and both noise generators are drawn globally per step, so
    settling a subset is numerically a no-op for the arm read)."""
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG_L + NOISE_L * torch.randn(n_old_L, 1, generator=gen)).clamp(0, 1)
    X0n = (BG_L + NOISE_L * torch.randn(n_add_L, 1, generator=gen2)).clamp(0, 1)
    X = torch.zeros(NL, 1)
    X[OLDPOS] = X0o
    X[KEPTNEW] = X0n[KEPTMASK]
    sp = 0.0
    last = None
    for _ in range(SETTLE_L):
        nz_o = NOISE_L * torch.randn(n_old_L, 1, generator=gen)
        nz_a = NOISE_L * torch.randn(n_add_L, 1, generator=gen2)
        nzn = torch.zeros(int(keep_new.sum()), 1)
        nzn[loc_new[gi_old_idx]] = nz_o
        nzn[loc_new[dn_new_g]] = nz_a
        noise = nzn[POSINNEW]
        sp += 2 * math.pi * 0.7 * DT_L
        sin_t = ENT_AMP_L * (0.5 + 0.5 * math.sin(sp))
        drive = torch.sparse.mm(WBETA, X) * g + I_vec
        drive[mech_l, 0] = drive[mech_l, 0] + sin_t
        last = (X.clone(), drive.clone(), noise.clone(), sp, g)
        X = X + (DT_L / TAU_L) * ((torch.relu(drive + BG_L) + noise)
                                  .clamp(max=RMAX_L) - X)
    return X, last


SEEDS = [801, 901, 11]
settled = {}
for s in SEEDS:
    Xs, lastp = settle_f4(s)
    af = float((Xs > 0.05).float().mean())
    assert AF_BAND[0] <= af <= AF_BAND[1], (s, af, "op point out of band (STOP)")
    settled[s] = (Xs, lastp, af)
    log(f"[settle] seed {s}: af {af:.5f} (AF_T {AF_T_L:.5f})")
o["op_point"] = dict(af={str(s): settled[s][2] for s in SEEDS},
                     AF_T=AF_T_L, band=list(AF_BAND),
                     stored_rollout_af_f4wA=0.10889)


def row_mask(X, g):
    """a_i = relu'(u_i+BG) AND not saturating, at the state X under drive."""
    sp = settled[SEEDS[0]][1][3]  # phase continues from the settle tail
    drive = torch.sparse.mm(WBETA, X) * g + I_vec
    sin_t = ENT_AMP_L * (0.5 + 0.5 * math.sin(sp + 2 * math.pi * 0.7 * DT_L))
    drive[mech_l, 0] = drive[mech_l, 0] + sin_t
    u = drive + BG_L
    return ((u > 0) & (torch.relu(u) < RMAX_L)).squeeze(1).numpy(), u


# ---------------- Q5 INSTRUMENT (halting, runs before any path read) --------
def jmatvec(x, jv, ls, ld):
    y = np.zeros(NL)
    np.add.at(y, ld, jv * x[ls])
    return y


Xp, lastp, _af = settled[801]
a_mask, u_set = row_mask(Xp, G_F4WA)
jv_sgn = (G_F4WA * _v.numpy().astype(np.float64))  # CSR value order
# rebuild edge arrays in CSR order so jv aligns with (row=target, col=source)
csr_rows = np.repeat(np.arange(NL), np.diff(_crow))
csr_cols = _ccol
jv_sgn = jv_sgn * a_mask[csr_rows]
jv_abs = np.abs(G_F4WA * _v.numpy().astype(np.float64)) * a_mask[csr_rows]

gq = torch.Generator().manual_seed(17801)
dX = 1e-4 * torch.randn(NL, 1, generator=gq)
sp_next = lastp[3] + 2 * math.pi * 0.7 * DT_L
sin_next = ENT_AMP_L * (0.5 + 0.5 * math.sin(sp_next))
gq2 = torch.Generator().manual_seed(27801)
noise_shared = NOISE_L * torch.randn(NL, 1, generator=gq2)


def one_step(X):
    drive = torch.sparse.mm(WBETA, X) * G_F4WA + I_vec
    drive[mech_l, 0] = drive[mech_l, 0] + sin_next
    return X + (DT_L / TAU_L) * ((torch.relu(drive + BG_L) + noise_shared)
                                 .clamp(max=RMAX_L) - X)


meas = (one_step(Xp + dX) - one_step(Xp)).squeeze(1).numpy()
pred = ((1 - DT_L / TAU_L) * dX.squeeze(1).numpy()
        + (DT_L / TAU_L) * jmatvec(dX.squeeze(1).numpy(), jv_sgn,
                                   csr_cols, csr_rows))
relerr = float(np.linalg.norm(pred - meas) / np.linalg.norm(meas))
Q5 = bool(relerr < 1e-2)
log(f"[Q5] linearization one-step rel err {relerr:.3e} -> "
    f"{'PASS' if Q5 else 'FAIL (BLOCKED)'}")
o["Q5_instrument"] = dict(rel_err=relerr, bar=1e-2, PASS=Q5,
                          active_rows=int(a_mask.sum()),
                          active_frac=float(a_mask.mean()),
                          dX_norm=float(np.linalg.norm(dX.numpy())))
assert Q5, f"Q5 FAILED (rel err {relerr:.3e}) — card BLOCKED, no path read"

# ---------------- path census ----------------------------------------------
out_mass_global = np.zeros(Nall)
np.add.at(out_mass_global, src_all[_ei], np.abs(vals_all[_ei]))


def reach(c_local, jv, depth=3):
    """complete length-d walk sums of J from c into each pool."""
    x = np.zeros(NL)
    x[c_local] = 1.0
    res = {}
    for d in range(1, depth + 1):
        x = jmatvec(x, jv, csr_cols, csr_rows)
        res[d] = {pk: float(x[POOL_L[pk]].sum()) for pk in POOL_L}
    return res


def pi_index(sgn_d):
    num = sum(abs(sgn_d[a] - sgn_d[b]) for a, b in PAIRS)
    den = sum(abs(sgn_d[a]) + abs(sgn_d[b]) for a, b in PAIRS)
    return float(num / den) if den else float("nan")


ACTORS = {"carrier": LC_CAR, "twin": LC_TWIN}
for _k, _gi in enumerate(FAMILY):
    ACTORS[f"fam{_k:02d}_{_gi}"] = int(loc_f4[_gi])
GI_OF = {"carrier": GI_CARRIER, "twin": GI_TWIN4}
GI_OF.update({f"fam{_k:02d}_{_gi}": int(_gi) for _k, _gi in enumerate(FAMILY)})

cens = {}
for name, lc in ACTORS.items():
    ra = reach(lc, jv_abs)
    rs = reach(lc, jv_sgn)
    gi_ = GI_OF[name]
    m_out = float(out_mass_global[gi_])
    _sel_c = (src_all[_ei] == gi_) & POOL_GLOBAL_ANY[dst_all[_ei]]
    row = dict(gi=gi_, local=lc, m_out=m_out,
               n_out=int((emask_f4 & (src_all == gi_)).sum()),
               direct_pool_mass=float(np.abs(vals_all[_ei][_sel_c]).sum()))
    for d in (1, 2, 3):
        row[f"P{d}abs"] = float(sum(ra[d].values()))
        row[f"S{d}sgn"] = float(sum(rs[d].values()))
        row[f"P{d}abs_per_mass"] = row[f"P{d}abs"] / m_out if m_out else None
        row[f"PI{d}"] = pi_index(rs[d])
    row["per_pool_abs2"] = {pk: ra[2][pk] for pk in POOL_L}
    row["per_pool_sgn2"] = {pk: rs[2][pk] for pk in POOL_L}
    cens[name] = row
log(f"[census] {len(cens)} actors, depths 1-3, abs+signed")

# ---------------- Q6 exhaustive depth-2 enumeration (certifies the search) --
# out-edge lists by source (CSR is by target, so group by col)
_ord = np.argsort(csr_cols, kind="stable")
_cs = csr_cols[_ord]
_cstart = np.searchsorted(_cs, np.arange(NL))
_cend = np.searchsorted(_cs, np.arange(NL) + 1)
pool_flag = np.zeros(NL, bool)
pool_flag[POOL_ALL] = True


def enum2(c_local):
    paths = []
    for e1 in _ord[_cstart[c_local]:_cend[c_local]]:
        m = int(csr_rows[e1])
        w1 = jv_abs[e1]
        if w1 == 0.0:
            continue
        for e2 in _ord[_cstart[m]:_cend[m]]:
            p = int(csr_rows[e2])
            if not pool_flag[p]:
                continue
            paths.append(w1 * jv_abs[e2])
    paths.sort(reverse=True)
    tot = float(sum(paths))
    return paths, tot


q6 = {}
for name in list(ACTORS):
    paths, tot = enum2(ACTORS[name])
    mv = cens[name]["P2abs"]
    rel = abs(tot - mv) / mv if mv else 0.0
    q6[name] = dict(n_paths=len(paths), enum_total=tot, matvec_total=mv,
                    rel_diff=float(rel),
                    top10_share=float(sum(paths[:10]) / tot) if tot else None,
                    top100_share=float(sum(paths[:100]) / tot) if tot else None)
    assert rel < 1e-6, (name, "depth-2 enumeration != matvec (STOP)")
log("[Q6] exhaustive depth-2 enumeration == matvec for all actors (<1e-6)")
o["Q6_topk"] = {k: {kk: vv for kk, vv in v.items()} for k, v in q6.items()}

# ---------------- CERT-REW: l169c destination-swap, verbatim transcription --
def rewire_draws(emask_block, carrier_rows_sel, n_draws, seed, Tmask, Mmask):
    dn_pres = dn_all & (emask_block is not None)
    del dn_pres
    blk = emask_block
    pool_rows = np.where(blk & (src_all != GI_CARRIER))[0]
    car_rows = np.where(carrier_rows_sel)[0]
    base_pairs = set(zip(src_all[np.where(blk)[0]].tolist(),
                         dst_all[np.where(blk)[0]].tolist()))
    car_vals = np.abs(vals_all[car_rows])
    rng = np.random.default_rng(seed)
    out_draws = []
    for d in range(n_draws):
        cdst = dst_all[car_rows].copy()
        pdst = {}
        added, removed = set(), set()

        def present(p):
            return (p in base_pairs and p not in removed) or p in added

        def do_remove(p):
            if p in added:
                added.discard(p)
            else:
                removed.add(p)

        def do_add(p):
            if p in removed:
                removed.discard(p)
            else:
                added.add(p)

        nrel = 0
        for i in range(len(car_rows)):
            for _ in range(20):
                j = int(pool_rows[rng.integers(len(pool_rows))])
                sf = int(src_all[j])
                df = int(pdst.get(j, dst_all[j]))
                de = int(cdst[i])
                if sf == GI_CARRIER or df == de or df == GI_CARRIER or de == sf:
                    continue
                if present((GI_CARRIER, df)) or present((sf, de)):
                    continue
                do_remove((GI_CARRIER, de))
                do_remove((sf, df))
                do_add((GI_CARRIER, df))
                do_add((sf, de))
                cdst[i] = df
                pdst[j] = de
                nrel += 1
                break
        moved = cdst != dst_all[car_rows]
        tj = sorted(pdst)
        before = sorted(dst_all[car_rows].tolist() + [int(dst_all[j]) for j in tj])
        after = sorted(cdst.tolist() + [int(pdst[j]) for j in tj])
        assert before == after, ("degree non-neutral", d)
        out_draws.append(dict(
            relocated=int(nrel), moved=int(moved.sum()),
            mass_T70=float(car_vals[Tmask[cdst]].sum()),
            mass_motor=float(car_vals[Mmask[cdst]].sum()),
            n_dst=int(len(set(cdst.tolist()))),
            cdst=cdst.copy(), car_rows=car_rows, pdst=dict(pdst)))
    return out_draws


S169C = json.load(open("l169c/static.json"))["P6_rewire_draws"]
_dnw = dn_all & keep_wA
_blk_wA = emask_wA & _dnw[src_all] & cord_of_dst
_sel_car_wA = emask_wA & (src_all == GI_CARRIER)
_d_cert = rewire_draws(_blk_wA, _sel_car_wA, 100, 16943, T70, motor_G)


def _med(dd, k):
    return float(np.median([x[k] for x in dd]))


_car_mass_wA = float(np.abs(vals_all[np.where(_sel_car_wA)[0]]).sum())
assert _med(_d_cert, "relocated") == S169C["med_relocated"]
assert min(x["relocated"] for x in _d_cert) == S169C["min_relocated"]
assert _med(_d_cert, "moved") == S169C["med_moved"]
assert _med(_d_cert, "mass_T70") == S169C["med_mass_T70"]
assert _med(_d_cert, "mass_motor") / _car_mass_wA == S169C["med_mass_motor_share"]
assert _med(_d_cert, "n_dst") == S169C["med_n_dst"]
for _i5, _st5 in enumerate(S169C["per_draw_first5"]):
    for _k5 in ("relocated", "moved", "mass_T70", "mass_motor", "n_dst"):
        assert _d_cert[_i5][_k5] == _st5[_k5], (_i5, _k5, "CERT-REW (STOP)")
log("[CERT-REW] GREEN: l169c P6 reproduced EXACTLY (100 draws, seed 16943)")
o["cert_rew"] = dict(med_relocated=_med(_d_cert, "relocated"),
                     med_mass_motor_share=_med(_d_cert, "mass_motor") / _car_mass_wA,
                     first5_match=True)
del _d_cert

# ---------------- Q2 NULL on the floor-4 block ------------------------------
_dnf = dn_all & keep_f4
_blk_f4 = emask_f4 & _dnf[src_all] & cord_of_dst
_sel_car_f4 = emask_f4 & (src_all == GI_CARRIER)
assert int(_sel_car_f4.sum()) == _n_out_global
draws = rewire_draws(_blk_f4, _sel_car_f4, 100, 16943, T70, motor_G)
log(f"[Q2] {len(draws)} floor-4 draws: relocated med "
    f"{_med(draws, 'relocated'):.1f} min {min(x['relocated'] for x in draws)}")

# apply BOTH halves of each swap to the local edge arrays and recompute reach
_eipos = {int(p): i for i, p in enumerate(_ei)}
_csr_of_edge = None
# map global edge position -> CSR value index (coalesce sorted by (row, col))
_key_csr = csr_rows.astype(np.int64) * NL + csr_cols.astype(np.int64)
_ordkey = np.argsort(_key_csr, kind="stable")
assert np.array_equal(_key_csr[_ordkey], _key_csr), "CSR not row-major sorted"
_key_e = ldst.astype(np.int64) * NL + lsrc.astype(np.int64)
_pos_in_csr = np.searchsorted(_key_csr, _key_e)
assert np.array_equal(_key_csr[_pos_in_csr], _key_e), "edge->CSR map (STOP)"

null_vals = []
_vnp = _v.numpy().astype(np.float64)
for d in draws:
    jv_a2 = jv_abs.copy()
    jv_s2 = jv_sgn.copy()
    cr = d["car_rows"]
    newd = d["cdst"]
    changed = []
    for i, gpos in enumerate(cr):
        if int(newd[i]) == int(dst_all[gpos]):
            continue
        changed.append((int(_pos_in_csr[_eipos[int(gpos)]]),
                        int(loc_f4[int(newd[i])])))
    for jpos, de in d["pdst"].items():
        changed.append((int(_pos_in_csr[_eipos[int(jpos)]]),
                        int(loc_f4[int(de)])))
    # zero the old slots, then accumulate the relocated weights at new targets
    extra_ls, extra_ld, extra_va, extra_vs = [], [], [], []
    for cidx, new_target in changed:
        src_l = int(csr_cols[cidx])
        # weight travels with the SOURCE (L9 convention); the row mask follows
        # the NEW target, so re-apply a_mask at the destination
        base_s = G_F4WA * _vnp[cidx]
        base_a = abs(base_s)
        jv_a2[cidx] = 0.0
        jv_s2[cidx] = 0.0
        extra_ls.append(src_l)
        extra_ld.append(new_target)
        extra_va.append(base_a * a_mask[new_target])
        extra_vs.append(base_s * a_mask[new_target])
    ls2 = np.concatenate([csr_cols, np.array(extra_ls, np.int64)])
    ld2 = np.concatenate([csr_rows, np.array(extra_ld, np.int64)])
    va2 = np.concatenate([jv_a2, np.array(extra_va, np.float64)])
    vs2 = np.concatenate([jv_s2, np.array(extra_vs, np.float64)])
    # anatomical variant of the SAME draw (row mask a == 1)
    jv_an2 = np.abs(G_F4WA * _vnp).copy()
    extra_an = []
    for cidx, new_target in changed:
        jv_an2[cidx] = 0.0
        extra_an.append(abs(G_F4WA * _vnp[cidx]))
    va2_an = np.concatenate([jv_an2, np.array(extra_an, np.float64)])

    x = np.zeros(NL)
    x[LC_CAR] = 1.0
    rec = {}
    xs = x.copy()
    for dd in (1, 2, 3):
        y = np.zeros(NL)
        np.add.at(y, ld2, va2 * x[ls2])
        x = y
        ys = np.zeros(NL)
        np.add.at(ys, ld2, vs2 * xs[ls2])
        xs = ys
        rec[f"P{dd}abs"] = float(sum(x[POOL_L[pk]].sum() for pk in POOL_L))
        rec[f"S{dd}sgn"] = float(sum(xs[POOL_L[pk]].sum() for pk in POOL_L))
        rec[f"PI{dd}"] = pi_index({pk: float(xs[POOL_L[pk]].sum())
                                   for pk in POOL_L})
    rec["n_changed"] = len(changed)
    xa = np.zeros(NL)
    xa[LC_CAR] = 1.0
    for dd in (1, 2, 3):
        ya = np.zeros(NL)
        np.add.at(ya, ld2, va2_an * xa[ls2])
        xa = ya
        rec[f"P{dd}abs_an"] = float(sum(xa[POOL_L[pk]].sum() for pk in POOL_L))
    null_vals.append(rec)

m_out_car = cens["carrier"]["m_out"]
null_arr = {k: np.array([r[k] for r in null_vals], float)
            for k in ("P2abs", "P3abs", "S2sgn", "S3sgn", "PI2", "PI3")}
car_p2n = cens["carrier"]["P2abs"] / m_out_car
null_p2n = null_arr["P2abs"] / m_out_car   # out-mass preserved by construction
pct2 = float((null_p2n < car_p2n).mean() * 100)
pct3 = float((null_arr["P3abs"] / m_out_car < cens["carrier"]["P3abs"] / m_out_car).mean() * 100)
Q2 = bool(pct2 >= 95.0 or pct2 <= 5.0)
o["Q2_null"] = dict(
    n_draws=len(null_vals), seed=16943,
    med_relocated=_med(draws, "relocated"),
    med_n_changed=float(np.median([r["n_changed"] for r in null_vals])),
    carrier_P2abs_per_mass=car_p2n, carrier_P3abs_per_mass=cens["carrier"]["P3abs"] / m_out_car,
    null_P2_med=float(np.median(null_p2n)),
    null_P2_q25=float(np.percentile(null_p2n, 25)),
    null_P2_q75=float(np.percentile(null_p2n, 75)),
    null_P2_p05=float(np.percentile(null_p2n, 5)),
    null_P2_p95=float(np.percentile(null_p2n, 95)),
    carrier_percentile_P2=pct2, carrier_percentile_P3=pct3,
    PASS=Q2,
    null_PI2_med=float(np.median(null_arr["PI2"])),
    null_PI2_p05=float(np.percentile(null_arr["PI2"], 5)),
    null_PI2_p95=float(np.percentile(null_arr["PI2"], 95)),
    limitation="geometry null at the REAL op point: draws reuse the real row "
               "mask a and the real gain; NOT a re-settled dynamics null "
               "(l169c P7 requires a fresh af-matched bisect per draw).")
log(f"[Q2] carrier P2abs/mass {car_p2n:.4f} vs null med "
    f"{float(np.median(null_p2n)):.4f} -> percentile {pct2:.1f} "
    f"({'PASS' if Q2 else 'FAIL'})")

# ---------------- Q1 / Q3 / Q4 ---------------------------------------------
r2n_car = cens["carrier"]["P2abs_per_mass"]
r2n_tw = cens["twin"]["P2abs_per_mass"]
r3n_car = cens["carrier"]["P3abs_per_mass"]
r3n_tw = cens["twin"]["P3abs_per_mass"]
r2 = (r2n_car / r2n_tw) if r2n_tw else float("inf") if r2n_car else float("nan")
r3 = (r3n_car / r3n_tw) if r3n_tw else float("inf") if r3n_car else float("nan")
branch = ("D_BOTH_ZERO" if not np.isfinite(r2) and not r2n_car and not r2n_tw
          else "A_CARRIER_HIGH" if r2 >= 1.25 else
          "B_CARRIER_LOW" if r2 <= 0.80 else "C_NO_SIGNATURE")
o["Q1_claim"] = dict(
    r2=float(r2), r3=float(r3), branch=branch,
    carrier=dict(m_out=cens["carrier"]["m_out"],
                 P2abs=cens["carrier"]["P2abs"],
                 P2abs_per_mass=cens["carrier"]["P2abs_per_mass"],
                 P3abs_per_mass=cens["carrier"]["P3abs_per_mass"]),
    twin=dict(m_out=cens["twin"]["m_out"], P2abs=cens["twin"]["P2abs"],
              P2abs_per_mass=cens["twin"]["P2abs_per_mass"],
              P3abs_per_mass=cens["twin"]["P3abs_per_mass"]),
    mass_ratio=float(cens["carrier"]["m_out"] / cens["twin"]["m_out"]))

names35 = list(ACTORS)
mv = np.array([cens[n]["m_out"] for n in names35])
pv2 = np.array([cens[n]["P2abs"] for n in names35])
pv3 = np.array([cens[n]["P3abs"] for n in names35])


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    return float((ra * rb).sum() / np.sqrt((ra ** 2).sum() * (rb ** 2).sum()))


rho2 = spearman(mv, pv2)
rho3 = spearman(mv, pv3)
Q3_degenerate = bool(rho2 >= 0.95)
o["Q3_mass_restatement"] = dict(
    n_actors=len(names35), spearman_P2abs_vs_mout=rho2,
    spearman_P3abs_vs_mout=rho3, bar=0.95, DEGENERATE=Q3_degenerate,
    verdict=("NEGATIVE: top-k path reach restates out-mass"
             if Q3_degenerate else
             "path reach carries structure beyond out-mass"),
    pearson_log=float(np.corrcoef(np.log(mv), np.log(pv2))[0, 1]))
log(f"[Q3] spearman(P2abs, m_out) over {len(names35)} ng actors = {rho2:.4f} "
    f"-> {'DEGENERATE (negative card)' if Q3_degenerate else 'structure beyond mass'}")

_pi_null = null_arr["PI2"][np.isfinite(null_arr["PI2"])]
_pi_car = cens["carrier"]["PI2"]
pi_pct2 = (float((_pi_null < _pi_car).mean() * 100)
           if (len(_pi_null) and np.isfinite(_pi_car)) else None)
o["Q4_polarization"] = dict(
    carrier_PI2=cens["carrier"]["PI2"], twin_PI2=cens["twin"]["PI2"],
    carrier_PI3=cens["carrier"]["PI3"], twin_PI3=cens["twin"]["PI3"],
    family_PI2_med=float(np.nanmedian([cens[n]["PI2"] for n in names35[2:]])),
    carrier_PI2_null_percentile=pi_pct2,
    n_null_PI2_finite=int(len(_pi_null)),
    S2_carrier=cens["carrier"]["S2sgn"], S2_twin=cens["twin"]["S2sgn"],
    S3_carrier=cens["carrier"]["S3sgn"], S3_twin=cens["twin"]["S3sgn"],
    nan_note="PI is NaN when the actor's signed pool reach is identically "
             "zero at that depth (no walk arrives) — reported, never imputed.",
    inhib_frac_note="signed vs abs totals: S/P ratio is the net E/I balance "
                    "of the walk ensemble, reported per actor in the census.")
log(f"[Q1] r2 {r2} r3 {r3} -> {branch}")
log(f"[Q4] PI2 carrier {cens['carrier']['PI2']} twin "
    f"{cens['twin']['PI2']} null pct {pi_pct2}")

# ---------------- D: why is the depth-2 reach what it is? -------------------
# per-actor: how many of its depth-1 targets carry ANY out-edge into a pool
pool_out_deg = np.zeros(NL, np.int64)
_into_pool = pool_flag[csr_rows]
np.add.at(pool_out_deg, csr_cols[_into_pool], 1)
diag = {}
for name, lc in ACTORS.items():
    tg = csr_rows[_ord[_cstart[lc]:_cend[lc]]]
    tg = np.unique(tg)
    diag[name] = dict(
        n_targets=int(len(tg)),
        n_targets_active=int(a_mask[tg].sum()),
        n_targets_with_pool_outedge=int((pool_out_deg[tg] > 0).sum()),
        pool_outedges_from_targets=int(pool_out_deg[tg].sum()),
        n_targets_in_pool=int(pool_flag[tg].sum()))
o["D_depth2_anatomy"] = dict(
    per_actor={k: diag[k] for k in ("carrier", "twin")},
    family_med_targets_with_pool_outedge=float(np.median(
        [diag[n]["n_targets_with_pool_outedge"] for n in names35[2:]])),
    family_n_with_zero=int(sum(
        1 for n in names35[2:] if diag[n]["n_targets_with_pool_outedge"] == 0)),
    pool_cells_total=int(len(POOL_ALL)),
    pool_cells_active=int(a_mask[POOL_ALL].sum()),
    pool_cell_active_frac=float(a_mask[POOL_ALL].mean()),
    all_actor_diag=diag)
log(f"[D] carrier targets {diag['carrier']['n_targets']} "
    f"({diag['carrier']['n_targets_with_pool_outedge']} with pool out-edges) | "
    f"twin {diag['twin']['n_targets']} "
    f"({diag['twin']['n_targets_with_pool_outedge']}) | pool cells active "
    f"{int(a_mask[POOL_ALL].sum())}/{len(POOL_ALL)}")

# ---------------- seed robustness of the row mask ---------------------------
mask_rob = {}
for s in SEEDS:
    am, _u = row_mask(settled[s][0], G_F4WA)
    mask_rob[str(s)] = dict(active_frac=float(am.mean()),
                            jaccard_vs_801=float((am & a_mask).sum()
                                                 / (am | a_mask).sum()))
o["row_mask_robustness"] = mask_rob
log("[mask] " + " ".join(f"{k}:af{v['active_frac']:.4f}/J{v['jaccard_vs_801']:.4f}"
                         for k, v in mask_rob.items()))

o["census"] = {k: {kk: vv for kk, vv in v.items()} for k, v in cens.items()}

# ---------------- E: ANATOMICAL census (row mask a == 1) --------------------
# Separates "the wiring has no short path" from "the gate closes the path".
jv_abs_an = np.abs(G_F4WA * _vnp)
jv_sgn_an = G_F4WA * _vnp
cens_an = {}
for name, lc in ACTORS.items():
    ra = reach(lc, jv_abs_an)
    rs = reach(lc, jv_sgn_an)
    m_out = cens[name]["m_out"]
    row = {}
    for d in (1, 2, 3):
        row[f"P{d}abs"] = float(sum(ra[d].values()))
        row[f"S{d}sgn"] = float(sum(rs[d].values()))
        row[f"P{d}abs_per_mass"] = row[f"P{d}abs"] / m_out if m_out else None
        row[f"PI{d}"] = pi_index(rs[d])
    cens_an[name] = row
_a2c, _a2t = cens_an["carrier"]["P2abs_per_mass"], cens_an["twin"]["P2abs_per_mass"]
_a3c, _a3t = cens_an["carrier"]["P3abs_per_mass"], cens_an["twin"]["P3abs_per_mass"]
pv2_an = np.array([cens_an[n]["P2abs"] for n in names35])
o["E_anatomical"] = dict(
    note="row mask a == 1 (pure |g*W_beta| operator): anatomy only, no gating.",
    r2_anat=float(_a2c / _a2t) if _a2t else None,
    r3_anat=float(_a3c / _a3t) if _a3t else None,
    carrier=cens_an["carrier"], twin=cens_an["twin"],
    spearman_P2abs_vs_mout=spearman(mv, pv2_an),
    family_P2abs_per_mass_med=float(np.median(
        [cens_an[n]["P2abs_per_mass"] for n in names35[2:]])),
    carrier_rank_of_35_P2_per_mass=int(
        1 + sum(1 for n in names35
                if cens_an[n]["P2abs_per_mass"] > _a2c)),
    all_actors={k: v for k, v in cens_an.items()})
log(f"[E] ANATOMICAL r2 {o['E_anatomical']['r2_anat']} r3 "
    f"{o['E_anatomical']['r3_anat']} | carrier P2/mass {_a2c:.6f} twin "
    f"{_a2t:.6f} | rho(P2,mass) {o['E_anatomical']['spearman_P2abs_vs_mout']:.4f}")

# ---------------- Q2b: ANATOMICAL null (same 100 draws, a == 1) -------------
_an2 = np.array([r["P2abs_an"] for r in null_vals], float) / m_out_car
_an3 = np.array([r["P3abs_an"] for r in null_vals], float) / m_out_car
_p2b = float((_an2 < _a2c).mean() * 100)
_p3b = float((_an3 < _a3c).mean() * 100)
Q2b = bool(_p2b >= 95.0 or _p2b <= 5.0)
o["Q2b_null_anatomical"] = dict(
    n_draws=len(_an2), carrier_P2abs_per_mass=_a2c, carrier_P3abs_per_mass=_a3c,
    null_P2_med=float(np.median(_an2)), null_P2_p05=float(np.percentile(_an2, 5)),
    null_P2_p95=float(np.percentile(_an2, 95)),
    null_P2_q25=float(np.percentile(_an2, 25)),
    null_P2_q75=float(np.percentile(_an2, 75)),
    null_P3_med=float(np.median(_an3)),
    carrier_percentile_P2=_p2b, carrier_percentile_P3=_p3b, PASS=Q2b,
    twin_P2abs_per_mass=_a2t,
    note="same degree-neutral destination-swap draws, row mask a == 1 — this "
         "is the mask-free geometry null and the one Q2 claim rests on, "
         "because the gated carrier value is identically zero.")
log(f"[Q2b] ANAT carrier P2/mass {_a2c:.6f} vs null med "
    f"{float(np.median(_an2)):.6f} [p05 {float(np.percentile(_an2, 5)):.6f}, "
    f"p95 {float(np.percentile(_an2, 95)):.6f}] -> pct {_p2b:.1f} "
    f"({'PASS' if Q2b else 'FAIL'}); depth3 pct {_p3b:.1f}")

# ---------------- F: per-seed row-mask robustness of Q1 ---------------------
seedrob = {}
for s in SEEDS:
    am, _u = row_mask(settled[s][0], G_F4WA)
    jva = np.abs(G_F4WA * _vnp) * am[csr_rows]
    cp2 = sum(float(jmatvec(jmatvec(np.eye(1, NL, LC_CAR)[0], jva, csr_cols,
                                    csr_rows), jva, csr_cols,
                            csr_rows)[POOL_L[pk]].sum()) for pk in POOL_L)
    tp2 = sum(float(jmatvec(jmatvec(np.eye(1, NL, LC_TWIN)[0], jva, csr_cols,
                                    csr_rows), jva, csr_cols,
                            csr_rows)[POOL_L[pk]].sum()) for pk in POOL_L)
    x3c = np.eye(1, NL, LC_CAR)[0]
    for _ in range(3):
        x3c = jmatvec(x3c, jva, csr_cols, csr_rows)
    x3t = np.eye(1, NL, LC_TWIN)[0]
    for _ in range(3):
        x3t = jmatvec(x3t, jva, csr_cols, csr_rows)
    seedrob[str(s)] = dict(
        active_frac=float(am.mean()),
        pool_cells_active=int(am[POOL_ALL].sum()),
        carrier_P2abs=cp2, twin_P2abs=tp2,
        carrier_P3abs=float(sum(x3c[POOL_L[pk]].sum() for pk in POOL_L)),
        twin_P3abs=float(sum(x3t[POOL_L[pk]].sum() for pk in POOL_L)),
        r2=float((cp2 / cens["carrier"]["m_out"])
                 / (tp2 / cens["twin"]["m_out"])) if tp2 else None)
o["F_seed_robustness"] = seedrob
log("[F] " + " | ".join(
    f"s{k}: pool-active {v['pool_cells_active']}/{len(POOL_ALL)} carrP2 "
    f"{v['carrier_P2abs']:.3e} twinP2 {v['twin_P2abs']:.3e} r2 {v['r2']}"
    for k, v in seedrob.items()))

o["limitations"] = [
    "Liu/Ganguli/Baccus 2611.26101 theorem does NOT apply (recurrent graph, "
    "non-additive readout); only the top-k machinery is borrowed on the "
    "linearized operator (L152 bracket).",
    "the linearization point is a settled state under a PERIODIC drive = an "
    "L164 PHASE SNAPSHOT, not a verified operating point; nothing here is an "
    "intrinsic property of the substrate.",
    "depth-3 sums are operator powers (walks with revisits), not simple paths.",
    "Q2 is a geometry null at the real op point, not a re-settled null.",
    "the 'ng-family SUPER arm' of the card text is absent from f4wA by "
    "construction; the family arm is the ng tail ranks 23-55 (disclosed).",
]
o["pins"] = "ALL GREEN"
json.dump(o, open("l178/static.json", "w"), indent=1)
log("=" * 72)
log(f"L178 DONE {time.time()-t0:.0f}s | Q5 {Q5} | Q1 {branch} (r2 {r2}) | "
    f"Q2 pct {pct2:.1f} {'PASS' if Q2 else 'FAIL'} | Q3 rho {rho2:.4f} "
    f"{'DEGENERATE' if Q3_degenerate else 'ok'}")
