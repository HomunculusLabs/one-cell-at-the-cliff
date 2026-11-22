"""L199 Part D: the causal tone-phase manipulation. Reads the three workers'
stored raws, certifies, applies the registered block statistic (ph.part_d).
Run from banc/. Written BEFORE any rollout (PREREG)."""
import hashlib, json, math, os, sys
import numpy as np
sys.path.insert(0, "l199")
import ph
gj = ph.gj

OUT, NW = "l199", 3
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
frz = json.load(open(f"{OUT}/FREEZE.json"))
assert sha(f"{OUT}/PREREG.md") == frz["prereg_sha256"], "PREREG changed after freeze"
assert sha(f"{OUT}/ph.py") == frz["files"]["ph.py"] and sha(f"{OUT}/run_tp.py") == frz["files"]["run_tp.py"]
BASE, TAGOFF = frz["causal_seeds"], frz["tag_offset"]
assert BASE == list(range(19931, 19947)) and TAGOFF == 50000
G_CUTWA, G_SC25, ENT_AMP = 0.14365819573402408, 0.1454454553127289, 0.1
PHI = ph.tone_phi()
t = np.arange(6000)
canon = (t // 2000 == 1) | ((t % 2000) % 900 < 500)

store, secs, n_c0a = {}, {}, 0
for w in range(NW):
    for nm in ("done", "anchors", "gains"):
        assert os.path.exists(f"{OUT}/{nm}_w{w}.json"), f"worker {w} incomplete ({nm}) — no read"
    an, gn, dn = (json.load(open(f"{OUT}/{nm}_w{w}.json")) for nm in ("anchors", "gains", "done"))
    assert an["c0a_pass"] and an["c0a_max"] == 0.0 and an["n_checks"] == 92, w
    assert gn["gain"] == {"cutwA": G_CUTWA, "sc25": G_SC25} and all(gn["stored_exact"].values()), w
    assert dn["prereg_sha256"] == frz["prereg_sha256"]
    mine = BASE[w::NW] + [TAGOFF + x for x in BASE[w::NW]]
    assert dn["seeds"] == [801, 901] + mine
    n_c0a += an["n_checks"]
    secs[w] = dn["secs"]
    z = np.load(f"{OUT}/raw_w{w}.npz")
    for s in (801, 901):
        assert np.array_equal(z[f"gate_{s}"], canon)
        assert np.allclose(z[f"tone_{s}"], np.where(canon, ENT_AMP * (0.5 + 0.5 * np.sin(PHI)), 0.0), rtol=0, atol=1e-12)
    for s in mine:
        for k in ("gate_{s}", "tone_{s}", "Ti_fR_cutwA_{s}", "Ti_eR_cutwA_{s}", "Ti_fR_sc25_{s}", "Ti_eR_sc25_{s}", "xm_cutwA_{s}", "xm_sc25_{s}"):
            key = k.format(s=s)
            assert key not in store
            store[key] = z[key]
tags = BASE + [TAGOFF + b for b in BASE]
mc_max = 0.0
for b in BASE:
    g0, gp, t0, tp = store[f"gate_{b}"], store[f"gate_{TAGOFF + b}"], store[f"tone_{b}"], store[f"tone_{TAGOFF + b}"]
    assert np.array_equal(g0, canon) and np.array_equal(gp, canon), ("gate not canonical", b)
    mc_max = max(mc_max, float(np.abs(t0 + tp - ENT_AMP * canon).max()), float(np.abs(t0 - np.where(canon, ENT_AMP * (0.5 + 0.5 * np.sin(PHI)), 0.0)).max()))
    assert float(np.abs(t0 - tp).max()) > .09, ("tone not shifted", b)
    for g in ph.GRAPHS:
        for p in ("Ti_fR", "Ti_eR"):
            y0, yp = store[f"{p}_{g}_{b}"], store[f"{p}_{g}_{TAGOFF + b}"]
            assert y0.shape == (6000,) and np.isfinite(y0).all() and np.isfinite(yp).all() and not np.array_equal(y0, yp)
assert mc_max < 1e-12, mc_max
print(f"C0A {n_c0a} checks max 0.0 | gains EXACT x{NW} | gates canonical x32 | MC tone(phi0)+tone(phiPI) == ENT_AMP*gate, max dev {mc_max:.1e}")

ons = {tg: [900, 4900] for tg in tags}
nb = len(BASE)
res = dict(design="L199 Part D causal tone-phase manipulation (PREREG l199/PREREG.md)", status="FINAL",
           prereg_sha256=frz["prereg_sha256"], seeds=BASE, tag_offset=TAGOFF,
           certs=dict(c0a_checks=n_c0a, c0a_max=0.0, gains_stored_exact=True, gates_canonical=True, mc_max_dev=mc_max, worker_secs=secs))
h, lag = ph.seg_duty(store, tags, ons, 150, gj.starts_of("S"))
assert not lag.any()
Dd = ph.part_d(h, nb)
res["D"] = Dd
np.savez_compressed(f"{OUT}/segduty_causal.npz", **{f"h_{g}": h[g] for g in h})
h5, _ = ph.seg_duty(store, tags, ons, 500, np.arange(-250, 251, 10))
res["descriptive_W500"] = ph.part_d(h5, nb)
# descriptive: direct pool phase per phi arm, against each arm's OWN tone phase
res["C_by_phi"] = dict(phi0=ph.part_c(store, BASE, {b: ons[b] for b in BASE}, 500, PHI),
                       phiPI=ph.part_c(store, tags[nb:], {tg: ons[tg] for tg in tags[nb:]}, 500, PHI + math.pi))
# descriptive: pool peak phase against the UNSHIFTED tone, phiPI minus phi0 (expected ~180 if tone-locked)
sh = {}
for g in ph.GRAPHS:
    for p in ("Ti_fR", "Ti_eR"):
        dl = [float(ph.wrap(ph.pool_alpha(store[f"{p}_{g}_{TAGOFF + b}"], [900, 4900], 500, PHI)[0]
                            - ph.pool_alpha(store[f"{p}_{g}_{b}"], [900, 4900], 500, PHI)[0])) for b in BASE]
        sh[f"{p}_{g}"] = ph.circ(dl)
res["pool_phase_shift_phiPI_minus_phi0"] = sh
below = lambda x: bool(x["value"] < 0 and x["ci95"][1] < 0)
above = lambda x: bool(x["value"] > 0 and x["ci95"][0] > 0)
res["predictions"] = dict(Q7=dict(certs_mc=True, K_base_below0=below(Dd["K"]["cutwA"]), label=Dd["label"],
                                  CA1=bool(Dd["label"] in ("CA1", "CA1_sign")), CA1_sign=bool(Dd["label"] == "CA1_sign"),
                                  E_PP_above0=above(Dd["E_PP"])))
tmp = f"{OUT}/results_causal.json.tmp"
json.dump(res, open(tmp, "w"), indent=1, allow_nan=False)
os.replace(tmp, f"{OUT}/results_causal.json")
f3 = lambda d: f"{d['value']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]"
L = [f"L199 Part D — causal label {Dd['label']} (n = {nb} seeds x 2 graphs x 2 tone phases; canonical gate; C0A {n_c0a} checks max 0.0; MC dev {mc_max:.1e})"]
for nm, X in (("W150 registered", Dd), ("W500 descriptive", res["descriptive_W500"])):
    L += [f"[{nm}] duty within phi0-phi0 / phiPI-phiPI / cross 0-PI / cross PI-0: " + " ; ".join(
              f"{g} {X['blocks'][g]['w00']:.3f} / {X['blocks'][g]['wPP']:.3f} / {X['blocks'][g]['x0P']:.3f} / {X['blocks'][g]['xP0']:.3f}" for g in ph.GRAPHS),
          f"    K (within - cross): cutwA {f3(X['K']['cutwA'])} | sc25 {f3(X['K']['sc25'])} | K_I {f3(X['K_I'])} -> {X['label']}",
          f"    E (sc25 - cutwA): phi0-phi0 {f3(X['E_00'])} | phiPI-phiPI {f3(X['E_PP'])} | cross {f3(X['E_X'])} | E_PP - E_00 {f3(X['E_PP_minus_E_00'])}",
          "    same-seed duty phi0 / phiPI / cross-phi: " + " ; ".join(f"{g} {X['same_seed'][g]['phi0']:.3f} / {X['same_seed'][g]['phiPI']:.3f} / {X['same_seed'][g]['cross_phi']:.3f}" for g in ph.GRAPHS)]
for k, C in res["C_by_phi"].items():
    L.append(f"[C {k}] " + " ; ".join(f"{g} Delta {C[g]['Delta']['mean_deg']:+.1f} R {C[g]['Delta']['R']:.2f} ({C[g]['label']})" for g in ph.GRAPHS)
             + f" | paired shift {C['paired_shift']['mean_deg']:+.1f} R {C['paired_shift']['R']:.2f} -> {C['label']}")
L.append("pool peak phase vs UNSHIFTED tone, phiPI - phi0: " + " ; ".join(f"{k} {v['mean_deg']:+.1f} R {v['R']:.2f}" for k, v in sh.items()))
L.append("predictions: " + json.dumps(res["predictions"]))
open(f"{OUT}/causal.out", "w").write("\n".join(L) + "\n")
print("\n".join(L))
print("L199 CAUSAL WRITTEN (FINAL)")
