"""L170 BUILD: generate l170_static.py as a purely ADDITIVE transform of
l138_static.py.

House rules applied (lineage l169b/l169c precedent):
  - the HEAD of l138_static.py (everything above its `out = dict(design=` write)
    is kept VERBATIM and byte-identity-asserted, so every BANC/male pin in it
    re-runs as free certification of this run's substrate;
  - the splice anchor is count-asserted (exactly one site);
  - the generated file is residual-scanned: no surviving WRITE to l138/,
    l146/, l151/ or any path outside l170/, and exactly one json.dump target;
  - py_compile gate before the generated script is ever run.
"""
import py_compile
import re
import sys

SRC = "l138_static.py"
DST = "l170_static.py"
ANCHOR = "out = dict(design=\"L138 slice A static: MaleCNS closure-mirror ladder + DNp33 \""

src = open(SRC).read()
assert src.count(ANCHOR) == 1, f"anchor count != 1 ({src.count(ANCHOR)}) — STOP"
head = src[:src.index(ANCHOR)]
assert head == src[:len(head)], "head prefix drift — STOP"
assert "l138/static.json" not in head, "head already writes the l138 artifact — STOP"
print(f"head kept VERBATIM: {len(head):,} chars, {head.count(chr(10)):,} lines")

TAIL = '''
# ==================== L170: matched synapse floor (male side) ===============
# PREREG l170/PREREG.md registered FIRST (before any floor>=2 number).
# Everything ABOVE this line is l138_static.py VERBATIM (head-prefix byte
# identity asserted by l170_build.py), so all BANC + male pins above re-ran as
# free certification. l138/static.json is NEVER rewritten by this script.
print("\\n== L170: matched synapse floor on the male side ==")
P170 = json.load(open("l170/precheck.json"))
S138 = json.load(open("l138/static.json"))
assert P170["w_min"] == 1.0 and P170["dup_pairs"] == 0, "precheck drift (STOP)"

m_cord_f = np.isin(msup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
assert bool((m_cord_f == m_cord).all()), "cord mask drift vs head (STOP)"


def male_ladder(floor):
    """l138 male closure-mirror extraction, forms VERBATIM, over weight>=floor."""
    ke = mwv >= float(floor)
    s, d, v = msrc[ke], mdst[ke], mwv[ke]
    into = np.zeros(N_m, bool)
    into[d[m_cord_f[s]]] = True
    into &= m_dn_all
    proj = np.zeros(N_m, bool)
    proj[s[m_cord_f[d]]] = True
    proj &= m_dn_all
    k_old = m_cord_f | into
    k_new = m_cord_f | into | proj
    add = k_new[s] & k_new[d] & ~(k_old[s] & k_old[d])
    gi_n, gi_o = np.where(k_new)[0], np.where(k_old)[0]
    dnn = gi_n[~np.isin(gi_n, gi_o)]
    inew = np.zeros(N_m, bool)
    inew[dnn] = True
    om = add & inew[s] & m_cord_f[d]
    omass = np.zeros(N_m)
    np.add.at(omass, s[om], np.log1p(np.abs(v[om])))
    cm = omass[dnn]
    assert len(dnn) > 0 and cm.sum() > 0, f"empty cohort at floor {floor} (STOP)"
    order = np.argsort(-cm)
    cum = np.cumsum(cm[order]) / cm.sum()
    K = int(np.searchsorted(cum, 0.50) + 1)
    heav = dnn[order[:K]]
    glut_d = heav[m_glut[heav]]
    ng_d = heav[~m_glut[heav]]
    hmass = cm[order[:K]] / cm.sum()
    ngmass = hmass[~m_glut[heav]]
    s1 = dict(n_keep_old=int(k_old.sum()), n_keep_new=int(k_new.sum()),
              dn_new=int(len(dnn)), added_edges=int(add.sum()),
              added_dn_out_edges=int(om.sum()),
              dn_new_glut=int(len(glut_d)), dn_new_ng=int(len(ng_d)),
              heavy_K=int(K), heavy_mass_share=round(float(cum[K - 1]), 4))
    window = dict(
        r1_19=round(float(ngmass[:19].sum()), 4) if len(ngmass) >= 19 else None,
        r20_29=round(float(ngmass[19:29].sum()), 4) if len(ngmass) >= 29 else None,
        r30_rest=round(float(ngmass[29:].sum()), 4) if len(ngmass) > 29 else None,
        n_ng=int(len(ngmass)))
    # DNp33 position under this floor
    d33 = []
    for g in md33:
        oe = int(((s == g) & m_cord_f[d]).sum())
        ie = int(((d == g) & m_cord_f[s]).sum())
        in_coh = bool(inew[g])
        ngr = (int(np.where(ng_d == g)[0][0]) + 1
               if (in_coh and bool(np.isin(g, ng_d))) else None)
        d33.append(dict(gi=int(g), bodyId=int(mids[g]),
                        somaSide=str(lab.somaSide.iloc[int(g)]),
                        dn_into=bool(into[g]), dn_proj=bool(proj[g]),
                        out_cord_edges=oe, in_cord_edges=ie,
                        in_cohort=in_coh, ng_rank=ngr,
                        mass=round(float(omass[g]), 4),
                        mass_share=round(float(omass[g] / cm.sum()), 6)))
    # design pins for a future dynamic walk (BANC analog: ng ranks 25/26 twins)
    pins = dict(ng_top10=[str(lab.type.iloc[int(g)]) for g in ng_d[:10]],
                ng_mass_list=[round(float(x), 6) for x in ngmass[:40]])
    if len(ng_d) > 25:
        a, b = int(ng_d[24]), int(ng_d[25])
        pins["rank25"] = dict(gi=a, bodyId=int(mids[a]),
                              type=str(lab.type.iloc[a]),
                              somaSide=str(lab.somaSide.iloc[a]),
                              mass_share=round(float(omass[a] / cm.sum()), 6))
        pins["rank26"] = dict(gi=b, bodyId=int(mids[b]),
                              type=str(lab.type.iloc[b]),
                              somaSide=str(lab.somaSide.iloc[b]),
                              mass_share=round(float(omass[b] / cm.sum()), 6))
        pins["twin_gap"] = round(float(abs(omass[a] - omass[b]) / cm.sum()), 8)
    return dict(floor=int(floor), edges_kept=int(ke.sum()), s1=s1,
                window=window, dnp33=d33, pins=pins,
                dn_total=int(m_dn_all.sum()), dn_into=int(into.sum()),
                dn_proj=int(proj.sum()))


LAD = {}
for fl in (1, 2, 3, 4):
    LAD[fl] = male_ladder(fl)
    r = LAD[fl]
    print(f"floor {fl}: edges {r['edges_kept']:>11,} | dn_into {r['dn_into']:>5,}"
          f" dn_proj {r['dn_proj']:>5,} | dn_new {r['s1']['dn_new']:>4,}"
          f" (glut {r['s1']['dn_new_glut']:>3} / ng {r['s1']['dn_new_ng']:>4})"
          f" | K {r['s1']['heavy_K']:>3} share {r['s1']['heavy_mass_share']}"
          f" | n_ng {r['window']['n_ng']:>4} window {r['window']['r1_19']},"
          f"{r['window']['r20_29']},{r['window']['r30_rest']}")

# ---------------- CERT block (before any floor>=2 number is READ) -----------
c1 = LAD[1]["s1"]
for k, want in S138["male_s1"].items():
    assert c1[k] == want, f"CERT-1 FAIL {k}: {c1[k]} != {want} (STOP)"
assert LAD[1]["s1"]["heavy_mass_share"] == 0.5187
assert (LAD[1]["dn_total"], LAD[1]["dn_into"]) == (
    S138["probe"]["male_dn_total"], S138["probe"]["male_dn_into"]), "CERT-2 dn counts"
assert LAD[1]["s1"]["dn_new"] == S138["probe"]["male_pure_proj"] == 28
for got, want in zip(LAD[1]["dnp33"], S138["probe"]["male_dnp33"]):
    assert got["gi"] == want["gi"] and got["somaSide"] == want["side"]
    assert got["out_cord_edges"] == want["out_cord_edges"], ("CERT-2 out", got, want)
    assert got["in_cord_edges"] == want["in_cord_edges"], ("CERT-2 in", got, want)
    assert got["dn_into"] is want["dn_into"] and got["dn_proj"] is want["dn_proj"]
assert LAD[1]["window"] == S138["male_s3_window"], (
    "CERT-2 window", LAD[1]["window"], S138["male_s3_window"])
assert LAD[1]["pins"]["ng_top10"] == S138["male_ng_top10"], "CERT-2 top10"
assert LAD[1]["pins"]["ng_mass_list"] == S138["male_ng_mass_list"], "CERT-2 mass"
print("CERT-1/2 GREEN: floor-1 arm reproduces the stored l138 male side EXACTLY")

# ---------------- registered verdict (PREREG branches) ----------------------
dn1, dn3 = LAD[1]["s1"]["dn_new"], LAD[3]["s1"]["dn_new"]
K1, K3 = LAD[1]["s1"]["heavy_K"], LAD[3]["s1"]["heavy_K"]
rel = abs(dn3 - dn1) / dn1
m1 = bool(rel >= 0.20)
m2 = bool((not m1) and abs(K3 - K1) <= 1)
d33_f3 = LAD[3]["dnp33"]
m3 = bool(all(x["in_cohort"] for x in d33_f3))
branch = ("M1_floor_changes_cohort" if m1 else
          ("M2_floor_neutral" if m2 else "NEITHER_disclose"))
p1 = bool(dn3 > dn1)
p2 = bool(all(a["in_cord_edges"] < b["in_cord_edges"]
              for a, b in zip(d33_f3, LAD[1]["dnp33"])))
print(f"\\nBRANCH {branch} | rel change {rel:.4f} (dn_new {dn1} -> {dn3}), "
      f"K {K1} -> {K3}")
print(f"P1 (dn_new rises) {p1} | P2 (DNp33 in-edges fall) {p2} | "
      f"M3_dnp33_pure {m3} ({[x['ng_rank'] for x in d33_f3]} ng ranks)")
print("P4 window computable at floor 3:",
      LAD[3]["window"]["r30_rest"] is not None,
      "| BANC baseline", banc_window)

out170 = dict(
    design="L170 static: MaleCNS closure-mirror extraction at MATCHED synapse "
           "floor (BANC's implicit pair-level floor 3). Head block is "
           "l138_static.py VERBATIM. Zero rollouts, no RNG. PREREG "
           "l170/PREREG.md registered FIRST.",
    precheck=P170,
    ladder={str(k): v for k, v in LAD.items()},
    banc_window=banc_window, banc_K=K,
    verdict=dict(branch=branch, rel_change=round(float(rel), 4),
                 dn_new_1=dn1, dn_new_3=dn3, K_1=K1, K_3=K3,
                 M1=m1, M2=m2, M3_dnp33_pure=m3, P1=p1, P2=p2,
                 P4_window_computable=bool(
                     LAD[3]["window"]["r30_rest"] is not None)),
    reviewer_reported=dict(pure_proj=342, K=52,
                           note="REVIEWER-REPORTED (L167 I2), BARRED from the "
                                "draft; stored only for the lane log comparison"))
json.dump(out170, open("l170/static.json", "w"), indent=1)
print("\\nl170/static.json written")
'''

gen = head + TAIL
open(DST, "w").write(gen)

# ------------------------- residual scan -----------------------------------
bad = []
for i, line in enumerate(gen.split("\n"), 1):
    code = line.split("#")[0]
    if re.search(r'open\(\s*"(?!l170/)', code) and ("\"w\"" in code or "'w'" in code):
        bad.append((i, line.strip()))
    for forbidden in ("l138/static.json\", \"w\"", "l151/", "l146/"):
        if forbidden in code and ("\"w\"" in code or "'w'" in code):
            bad.append((i, line.strip()))
assert not bad, f"residual scan FAIL (writes outside l170/): {bad}"
dumps = [l for l in gen.split("\n") if "json.dump(" in l.split("#")[0]]
assert len(dumps) == 1 and "l170/static.json" in dumps[0], dumps
code_lines = [l.split("#")[0] for l in gen.split("\n")]
assert sum(l.count("l138/static.json") for l in code_lines) == 1, \
    "l138 artifact referenced !=1 time in CODE"
assert "open(\"l138/static.json\")" in gen, "l138 artifact must be READ-only"
py_compile.compile(DST, doraise=True)
print(f"{DST} written: {len(gen):,} chars; residual scan CLEAN; py_compile OK")
print(f"single json.dump target: {dumps[0].strip()}")
sys.exit(0)
