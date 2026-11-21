# ================= L169 (c1) TAIL (appended by l169c_build.py) =================
# Everything above this line is l151_static.py lines 1-319 VERBATIM, so every
# L151/L142/L134 pin re-ran as free certification before any (c1) value is read.
# PREREG: l169c/PREREG.md (registered first). Zero rollouts. RNG only for the
# registered rewire-feasibility draws (default_rng(16943), 100 draws).

o9 = {"design": "L169 stage (c1): design pins + premise tests for the (c2) "
                "REW (degree-preserving carrier-edge rewire) and HOM (gi 928 "
                "deletion) rollout arms. PREREG l169c/PREREG.md. Masses "
                "|log1p(syn)*sign| on the l142 closure convention.",
      "prereg": "l169c/PREREG.md"}

# ---------------- CERT-1: l151 blocks re-derive EXACT vs stored ----------------
L151 = json.load(open("l151/static.json"))
n_cert = 0


def _eq(a, b, path):
    global n_cert
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), ("keys", path)
        for k in a:
            _eq(a[k], b[k], f"{path}/{k}")
    else:
        assert a == b, (path, a, b)
        n_cert += 1


_eq(res_s1, {k: v for k, v in L151["s1_sheet"].items() if k in res_s1}, "s1")
_eq(res_s2, L151["s2_pools"], "s2")
_eq(res_s3, L151["s3_motor"], "s3")
assert n_cert > 400, n_cert
log(f"[CERT-1] l151 s1/s2/s3 re-derive EXACT: {n_cert} scalar fields GREEN")

# ---------------- P1: carrier footprint (re-derived, not quoted) ---------------
sel_out_G1 = emask_wA & (src_all == GI)
sel_in_G1 = emask_wA & (dst_all == GI)
car_out_mass = float(np.abs(vals_all[sel_out_G1]).sum())
assert int(sel_out_G1.sum()) == 80 and int(sel_in_G1.sum()) == 13
assert np.isclose(car_out_mass, 183.96376182027785, rtol=0, atol=1e-9)
o9["P1_carrier"] = dict(gi=GI, out_edges=int(sel_out_G1.sum()),
                        in_edges=int(sel_in_G1.sum()),
                        incident=int(((src_all == GI) | (dst_all == GI))
                                     [emask_wA].sum()),
                        out_mass=car_out_mass,
                        ng_rank=int(np.where(ng_desc == GI)[0][0]))

# ---------------- P2: 928 identity + membership -------------------------------
HOM = 928
hrow = ann[ann.gi == HOM]
assert len(hrow) == 1, len(hrow)
hr = hrow.iloc[0]
cols = [c for c in ("pt_root_id", "super_class", "cell_type", "side", "region",
                    "nerve", "peripheral_target_type") if c in ann.columns]
hom_id = dict((c, (None if pd.isna(hr[c]) else
                   (int(hr[c]) if c == "pt_root_id" else str(hr[c]))))
              for c in cols)
hom_id["nt_predicted"] = nt_map.get(int(hr["pt_root_id"]), None)
hom_id["gi"] = HOM
hom_id["is_glut_arm"] = bool(is_glut[HOM])
mem = dict(cord_mask=bool(cord_mask[HOM]), dn_all=bool(dn_all[HOM]),
           dn_into=bool(dn_into[HOM]), dn_proj=bool(dn_proj[HOM]),
           in_keep_old_l65=bool((cord_mask | dn_into)[HOM]),
           in_keep_new_closure=bool(keep_new[HOM]),
           in_dn_new_g=bool(HOM in set(dn_new_g.tolist())),
           in_heav_K=bool(HOM in set(heav.tolist())),
           in_ng_desc=bool(HOM in set(ng_desc.tolist())),
           in_glut_desc=bool(HOM in set(glut_desc.tolist())),
           in_cut_window24=bool(win24_mask[HOM]),
           in_cut_window25=bool(HOM in set(ng_desc[:25].tolist())),
           present_on_G1_cutwA=bool(keep_wA[HOM]))
# carrier's own membership, for the C2 (i) comparison
car_mem = dict(dn_into=bool(dn_into[GI]), dn_proj=bool(dn_proj[GI]),
               in_keep_old_l65=bool((cord_mask | dn_into)[GI]),
               in_dn_new_g=bool(GI in set(dn_new_g.tolist())),
               pure_proj=bool(dn_proj[GI] and not dn_into[GI]))
mem["pure_proj"] = bool(mem["dn_proj"] and not mem["dn_into"])
o9["P2_hom_identity"] = {"identity": hom_id, "membership": mem,
                         "carrier_membership": car_mem}

# ---------------- P3: 928 footprint on G0 / G1 --------------------------------
TIERS = ("intrinsic", "motor_other", "vnc_sensory")


def footprint(E, cell):
    so = E & (src_all == cell)
    si = E & (dst_all == cell)
    tot = float(np.abs(vals_all[so]).sum())
    tier = {}
    for t in TIERS:
        m = so & (tier_of_dst[dst_all] == t)
        tier[t] = dict(edges=int(m.sum()), mass=float(np.abs(vals_all[m]).sum()))
    return dict(out_edges=int(so.sum()), in_edges=int(si.sum()), out_mass=tot,
                in_mass=float(np.abs(vals_all[si]).sum()), tiers=tier,
                intrinsic_share=(tier["intrinsic"]["mass"] / tot) if tot else None,
                n_dst=int(len(np.unique(dst_all[so]))))


fp = {"hom_G0": footprint(emask_n, HOM), "hom_G1": footprint(emask_wA, HOM),
      "carrier_G0": footprint(emask_n, GI), "carrier_G1": footprint(emask_wA, GI)}
o9["P3_footprint"] = fp
# the carrier's tier split must reproduce the l151 pins 70 intrinsic / 10 motor
assert fp["carrier_G1"]["tiers"]["intrinsic"]["edges"] == 70
assert fp["carrier_G1"]["tiers"]["motor_other"]["edges"] == 10

# ---------------- P4: destination overlap + side composition ------------------
side_arr = np.full(Nall, "", dtype=object)
side_arr[mgi] = side_m
dst_car = set(np.unique(dst_all[sel_out_G1]).tolist())
sel_out_hom = emask_wA & (src_all == HOM)
dst_hom = set(np.unique(dst_all[sel_out_hom]).tolist())
inter = dst_car & dst_hom
uni = dst_car | dst_hom


def motor_sides(sel):
    m = sel & motor_G[dst_all]
    d = dst_all[m]
    v = np.abs(vals_all[m])
    r = {}
    for s in ("left", "right", ""):
        k = np.array([side_arr[x] == s for x in d], bool) if len(d) else \
            np.zeros(0, bool)
        r[s or "unknown"] = dict(edges=int(k.sum()),
                                 mass=float(v[k].sum()) if len(d) else 0.0)
    return r


pool_direct = {}
for pk, P in POOL_G.items():
    pool_direct[pk] = dict(
        carrier=float(np.abs(vals_all[sel_out_G1 & P[dst_all]]).sum()),
        hom=float(np.abs(vals_all[sel_out_hom & P[dst_all]]).sum()))
o9["P4_overlap"] = dict(
    n_dst_carrier=len(dst_car), n_dst_hom=len(dst_hom),
    n_shared=len(inter), jaccard=len(inter) / len(uni) if uni else None,
    hom_dst_in_T70=int(sum(T70[d] for d in dst_hom)),
    hom_dst_in_T10=int(sum(T10[d] for d in dst_hom)),
    hom_mass_into_T70=float(np.abs(vals_all[sel_out_hom & T70[dst_all]]).sum()),
    motor_sides_carrier=motor_sides(sel_out_G1),
    motor_sides_hom=motor_sides(sel_out_hom),
    pool_direct_mass=pool_direct,
    pool_direct_nonzero=sorted(k for k, v in pool_direct.items()
                               if v["carrier"] or v["hom"]))

# ---------------- P5/P6: registered rewire feasibility draws -------------------
dn_present_wA = dn_all & keep_wA
blk = emask_wA & dn_present_wA[src_all] & cord_of_dst
pool_rows = np.where(blk & (src_all != GI))[0]
car_rows = np.where(sel_out_G1)[0]
assert len(car_rows) == 80
base_pairs = set(zip(src_all[np.where(blk)[0]].tolist(),
                     dst_all[np.where(blk)[0]].tolist()))
chance_T70 = float(np.abs(vals_all[pool_rows][T70[dst_all[pool_rows]]]).sum()
                   / np.abs(vals_all[pool_rows]).sum())
car_vals = np.abs(vals_all[car_rows])
rng = np.random.default_rng(16943)
draws = []
for d in range(100):
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
            if sf == GI or df == de or df == GI or de == sf:
                continue
            if present((GI, df)) or present((sf, de)):
                continue
            do_remove((GI, de))
            do_remove((sf, df))
            do_add((GI, df))
            do_add((sf, de))
            cdst[i] = df
            pdst[j] = de
            nrel += 1
            break
    moved = cdst != dst_all[car_rows]
    # degree-neutrality: the swap exchanges destinations, so the multiset of
    # destinations over the touched rows is preserved EXACTLY
    tj = sorted(pdst)
    before = sorted(dst_all[car_rows].tolist() + [int(dst_all[j]) for j in tj])
    after = sorted(cdst.tolist() + [int(pdst[j]) for j in tj])
    assert before == after, ("degree non-neutral", d)
    draws.append(dict(
        relocated=int(nrel), moved=int(moved.sum()),
        mass_T70=float(car_vals[T70[cdst]].sum()),
        mass_motor=float(car_vals[motor_G[cdst]].sum()),
        n_dst=int(len(set(cdst.tolist())))))


def med(k):
    return float(np.median([x[k] for x in draws]))


o9["P5_rewire_pool"] = dict(
    block_edges=int(blk.sum()), partner_rows=int(len(pool_rows)),
    partner_over_carrier=float(len(pool_rows) / len(car_rows)),
    chance_mass_share_T70=chance_T70,
    n_dn_present_G1=int(dn_present_wA.sum()))
o9["P6_rewire_draws"] = dict(
    n_draws=len(draws), seed=16943,
    med_relocated=med("relocated"), min_relocated=min(x["relocated"] for x in draws),
    med_moved=med("moved"),
    med_mass_T70=med("mass_T70"),
    med_mass_T70_share=med("mass_T70") / car_out_mass,
    med_mass_motor_share=med("mass_motor") / car_out_mass,
    med_n_dst=med("n_dst"), carrier_n_dst=len(dst_car),
    per_draw_first5=draws[:5])
o9["P7_bisect_required"] = {
    "REW": "fresh af-matched bisect required (edge count unchanged, per-target "
           "in-degree redistributed); stored g_cutwA may NOT be re-used",
    "HOM": "fresh af-matched bisect required (node deletion removes edges)"}

# ---------------- registered rules ----------------
c1 = not mem["in_cut_window25"]
c2i = (mem["pure_proj"] == car_mem["pure_proj"])
h1, c1g = fp["hom_G1"], fp["carrier_G1"]
c2ii = (0.5 <= h1["out_edges"] / c1g["out_edges"] <= 2.0)
c2iii = (0.5 <= h1["out_mass"] / c1g["out_mass"] <= 2.0)
c2iv = abs((h1["intrinsic_share"] or 0) - (c1g["intrinsic_share"] or 0)) <= 0.20
c2 = bool(c2i and c2ii and c2iii and c2iv)
c3a = (len(pool_rows) >= 10 * len(car_rows)) and (med("relocated") >= 0.95 * 80)
c3b = (med("mass_T70") / car_out_mass) < 0.10
o9["rules"] = dict(
    C1_independent=bool(c1),
    C1_label="C1_independent" if c1 else "C1_vacuous_by_design",
    C2_mirror=c2,
    C2_label="C2_mirror" if c2 else "C2_nonequivalent",
    C2_legs=dict(same_class=bool(c2i), edges_factor2=bool(c2ii),
                 mass_factor2=bool(c2iii), intrinsic_share_20pp=bool(c2iv),
                 edge_ratio=h1["out_edges"] / c1g["out_edges"],
                 mass_ratio=h1["out_mass"] / c1g["out_mass"]),
    C3_expressible=bool(c3a), C3_nondegenerate=bool(c3b),
    C3_admissible=bool(c3a and c3b))
o9["pins"] = "ALL GREEN"

log("=" * 72)
log(f"P1 carrier gi {GI}: out {o9['P1_carrier']['out_edges']} in "
    f"{o9['P1_carrier']['in_edges']} incident {o9['P1_carrier']['incident']} "
    f"mass {car_out_mass:.5f} ng_rank {o9['P1_carrier']['ng_rank']}")
log(f"P2 hom gi {HOM}: {hom_id.get('cell_type')} side {hom_id.get('side')} "
    f"nt {hom_id.get('nt_predicted')}")
log(f"   membership: " + " ".join(f"{k}={v}" for k, v in mem.items()))
log(f"   carrier   : " + " ".join(f"{k}={v}" for k, v in car_mem.items()))
for k in ("carrier_G1", "hom_G1", "hom_G0"):
    f = fp[k]
    log(f"P3 {k:11s} out {f['out_edges']:4d} ({f['out_mass']:8.2f}) in "
        f"{f['in_edges']:3d}  intr {f['tiers']['intrinsic']['edges']:4d} "
        f"motor {f['tiers']['motor_other']['edges']:3d} sens "
        f"{f['tiers']['vnc_sensory']['edges']:3d}  intr_share "
        f"{(f['intrinsic_share'] or 0):.3f}  ndst {f['n_dst']}")
log(f"P4 dst overlap: carrier {len(dst_car)} / hom {len(dst_hom)} / shared "
    f"{len(inter)} / Jaccard {o9['P4_overlap']['jaccard']:.4f}; hom dst in T70 "
    f"{o9['P4_overlap']['hom_dst_in_T70']} T10 {o9['P4_overlap']['hom_dst_in_T10']}")
log(f"   motor sides carrier {o9['P4_overlap']['motor_sides_carrier']}")
log(f"   motor sides hom     {o9['P4_overlap']['motor_sides_hom']}")
log(f"   pools with direct mass: {o9['P4_overlap']['pool_direct_nonzero']}")
log(f"P5 partner pool {len(pool_rows)} rows ({o9['P5_rewire_pool']['partner_over_carrier']:.1f}x "
    f"carrier), DN->cord block {int(blk.sum())}, chance T70 mass share {chance_T70:.4f}")
log(f"P6 draws(100): relocated med {med('relocated'):.1f} min "
    f"{min(x['relocated'] for x in draws)}, T70 mass share med "
    f"{med('mass_T70')/car_out_mass:.4f}, motor share med "
    f"{med('mass_motor')/car_out_mass:.4f}, ndst med {med('n_dst'):.1f} "
    f"(carrier {len(dst_car)})")
log("-" * 72)
log(f"RULE C1 -> {o9['rules']['C1_label']} (928 in cut window25="
    f"{mem['in_cut_window25']})")
log(f"RULE C2 -> {o9['rules']['C2_label']}  legs {o9['rules']['C2_legs']}")
log(f"RULE C3 -> expressible {c3a} nondegenerate {c3b} admissible {c3a and c3b}")
log("=" * 72)
json.dump(o9, open("l169c/static.json", "w"), indent=1)
log(f"written l169c/static.json ({time.time()-t0:.0f}s)")
