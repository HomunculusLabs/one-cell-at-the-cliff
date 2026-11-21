"""Build l142_run.py: count-asserted transform of l135_run.py.
Spectator-arm subset (l139 law) + 5 edge-drop arms on the cutwA node set.
Drift guard: every rep count-pinned; py_compile; residual scan (no B26, no
l135/ paths, shared-line patterns count-checked)."""
import py_compile

src = open("l135_run.py").read()
reps = []


def rep(old, new, n=1):
    reps.append((old, new, n))


# R1 docstring
_ds_end = src.index('"""', src.index('"""') + 3) + 3
new_ds = '"""L142 run: DNp33 EDGE-FOOTPRINT LADDER on fresh B29. PREREG\n' \
    'l142/PREREG.md FIRST (registered before this build). Arms: full, b65,\n' \
    'cutwA (partial base), cutng25 (super reference) + 5 edge-drop arms on\n' \
    'the cutwA NODE SET (1110 kept as a cell): eOutInt(70)/eOutMot(10)/\n' \
    'eOutAll(80)/eIn(13)/eAll(93). Edge arms share cutwA init + per-step\n' \
    'noise EXACTLY (fork-grade paired reads). Spectator arms (cut/cut19/\n' \
    'cut58/cutk5/cutng19/cutng23/cutng25p/cutng26/cutng29) keep graphs +\n' \
    'pins verbatim, never advanced (l139 law); their bisects RETIRED.\n' \
    'FRESH B29 3301-3316 (absent all stored npzs incl l137 + l139 j0-j5).\n' \
    'Anchors: stored gains EXACT (cutwA/cutng25), C0A-142 vs raw_l135\n' \
    '(4 arms x 24 keys x 801/901 == 0.0), A0 structural (eAll edge set ==\n' \
    'cutng25 node drop), A-EALL bit-branch. CPU-only; raw checkpoint\n' \
    'BEFORE analysis.\n"""'
src = new_ds + src[_ds_end:]

# R2 ARMS
rep('ARMS = ["full", "b65", "cut", "cut19", "cut58",\n'
    '        "cutng19", "cutng23", "cutwA", "cutng25", "cutng25p",\n'
    '        "cutng26", "cutng29", "cutk5"]',
    'ARMS = ["full", "b65", "cutwA", "cutng25",\n'
    '        "eOutInt", "eOutMot", "eOutAll", "eIn", "eAll"]')
# R3 GAIN
rep('GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,\n'
    '            cutng19=None, cutng23=None, cutwA=None, cutng25=None,\n'
    '            cutng25p=None, cutng26=None, cutng29=None, cutk5=None)',
    'GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,\n'
    '            eOutInt=None, eOutMot=None, eOutAll=None, eIn=None,\n'
    '            eAll=None)')
# R4 batch tokens
rep('B26 = list(range(3001, 3017))  # fresh, absent l113..l133 incl raw_l133',
    'B29 = list(range(3301, 3317))  # fresh, absent l107..l137 + l139 j0-j5')
rep('SEEDS = ANCH + B26                  # anchors FIRST: early wiring verdict',
    'SEEDS = ANCH + B29                  # anchors FIRST: early wiring verdict')
rep('FRESH = B26', 'FRESH = B29')

# R5 block A: edge-drop computation + edge-arm graphs (after Wb builds)
BLK_A = '''
# ---- L142: edge-footprint arms on the cutwA node set (PREREG l142) ----
GI_CARRIER = 1110
E_ARMS = ("eOutInt", "eOutMot", "eOutAll", "eIn", "eAll")
assert int(ng_desc[24]) == GI_CARRIER and int(ng_desc[25]) == 319
keep_wA_e = keep_cutk["cutwA"]
emask_wA = keep_wA_e[src_all] & keep_wA_e[dst_all]
assert int(emask_wA.sum()) == cutk_pins["cutwA"]["edges"]
_sel_out = emask_wA & (src_all == GI_CARRIER)
out_int_e = _sel_out & (tier_of_dst[dst_all] == "intrinsic")
out_mot_e = _sel_out & (tier_of_dst[dst_all] == "motor_other")
in_sel_e = emask_wA & (dst_all == GI_CARRIER)
e_drop = {"eOutInt": out_int_e, "eOutMot": out_mot_e,
          "eOutAll": _sel_out, "eIn": in_sel_e,
          "eAll": _sel_out | in_sel_e}
E_EDGES = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert E_EDGES == {"eOutInt": 70, "eOutMot": 10, "eOutAll": 80,
                   "eIn": 13, "eAll": 93}, E_EDGES


def build_e(keep, drop):
    em = keep[src_all] & keep[dst_all] & ~drop
    gsrc, gdst, gcount = src_all[em], dst_all[em], w_syn[em]
    loc_e = -np.ones(Nall, np.int64)
    loc_e[keep] = np.arange(int(keep.sum()))
    gsign_a3 = sign_all[gsrc]
    gsign_b3 = np.where(is_glut[gsrc], -np.abs(gsign_a3), gsign_a3)
    vals_e = (np.log1p(gcount) * gsign_b3).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([loc_e[gdst], loc_e[gsrc]])).long(),
        torch.from_numpy(vals_e),
        (int(keep.sum()), int(keep.sum()))).coalesce().to_sparse_csr()
    return W


We = {a: build_e(keep_wA_e, e_drop[a]) for a in E_ARMS}
for _a in E_ARMS:
    assert int(We[_a].values().numel()) == int(emask_wA.sum()) - E_EDGES[_a], _a
# A0 structural law (PREREG): eAll edge positions == cutng25 node-drop
_keep25 = keep_new.copy()
_keep25[ng_desc[:25]] = False
_em25 = _keep25[src_all] & _keep25[dst_all]
assert np.array_equal(np.where(emask_wA & ~e_drop["eAll"])[0],
                      np.where(_em25)[0]), "A0 eAll != cutng25 (STOP)"
Wb_e = {a: wb(We[a]) for a in E_ARMS}
'''
rep('''Wb_ng19, Wb_ng29, Wb_wA, Wb_p23, Wb_p25, Wb_p25p, Wb_p26, Wb_k5 = (
    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_p23), wb(Wc_p25),
    wb(Wc_p25p), wb(Wc_p26), wb(Wc_k5))''',
    '''Wb_ng19, Wb_ng29, Wb_wA, Wb_p23, Wb_p25, Wb_p25p, Wb_p26, Wb_k5 = (
    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_p23), wb(Wc_p25),
    wb(Wc_p25p), wb(Wc_p26), wb(Wc_k5))
''' + BLK_A)

# R6 block B: per-arm map aliases (after N_OF, before AMPA)
BLK_B = '''
# L142: edge arms share cutwA's node set — alias every per-arm map
for _ea in E_ARMS:
    POOLS[_ea] = POOLS["cutwA"]
    mech[_ea] = mech["cutwA"]
    motor[_ea] = motor["cutwA"]
    dng100[_ea] = dng100["cutwA"]
    WB[_ea] = Wb_e[_ea]
    N_OF[_ea] = n_cutk["cutwA"]
'''
rep('''        "cutk5": n_cutk["cutk5"],
        "b65": n_old}

AMPA''',
    '''        "cutk5": n_cutk["cutk5"],
        "b65": n_old}
''' + BLK_B + '''
AMPA''')

# R7 settle st dict (14-space)
rep('''              cutk5=Xc_k5.clone(),
              b65=Xo65.clone())''',
    '''              cutk5=Xc_k5.clone(),
              eOutInt=Xc_wA.clone(), eOutMot=Xc_wA.clone(),
              eOutAll=Xc_wA.clone(), eIn=Xc_wA.clone(),
              eAll=Xc_wA.clone(),
              b65=Xo65.clone())''')
# R8 noise dicts (21-space, THREE sites: settle_states + rollout settle
# phase + rollout WIN phase — l123 shared-line lesson)
rep('''                     cutk5=nzn[k5_pos_in_new],
                     b65=nz_o)''',
    '''                     cutk5=nzn[k5_pos_in_new],
                     eOutInt=nzn[wA_pos_in_new], eOutMot=nzn[wA_pos_in_new],
                     eOutAll=nzn[wA_pos_in_new], eIn=nzn[wA_pos_in_new],
                     eAll=nzn[wA_pos_in_new],
                     b65=nz_o)''', n=3)
# R9 rollout X dict (13-space)
rep('''             cutk5=Xc_k5.clone(),
             b65=Xo65.clone())''',
    '''             cutk5=Xc_k5.clone(),
             eOutInt=Xc_wA.clone(), eOutMot=Xc_wA.clone(),
             eOutAll=Xc_wA.clone(), eIn=Xc_wA.clone(),
             eAll=Xc_wA.clone(),
             b65=Xo65.clone())''')
# R10 bisect gains dict
rep('''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,
                                  cutng25=g, cutng25p=g, cutng23=g,
                                  cutng26=g, cutk5=g))''',
    '''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,
                                  cutng25=g, cutng25p=g, cutng23=g,
                                  cutng26=g, cutk5=g, eOutInt=g, eOutMot=g,
                                  eOutAll=g, eIn=g, eAll=g))''')

for old, new, n in reps:
    c = src.count(old)
    assert c == n, (f"rep count {c} != {n} for: {old[:60]!r}")
    src = src.replace(old, new)

# R11 bisect section splice (opener-anchored, l122 wrap-fragile lesson).
# NOTE: the region between the section header and the first USAGE contains
# ANCH/lo_g/hi_g AND THE DEF of bisect_af_mean itself — splice from the
# first usage line, never the header (l131 def-order lesson).
_b0 = src.index("af_lo, af_hi = bisect_af_mean(lo_g), bisect_af_mean(hi_g)")
_b0 = src.rindex("# ---------------- P1 bisect", 0, _b0)
# keep everything up to AND INCLUDING the def block: find def end
_def_start = src.index("def bisect_af_mean(")
_def_end = src.index("return float(np.mean(afs))", _def_start) \
    + len("return float(np.mean(afs))")
assert _def_end < _b0 + 2000
BISECT = '''# ---------------- bisects (L142: 2 stored-form + 5 fresh) ----------------
new_stairs = {}
for _a in ("cutwA", "cutng25"):
    _stored = {"cutwA": G_CUTWA_STORED, "cutng25": G_CUTNG25_STORED}[_a]
    lo_d, hi_d = 0.12, 0.18
    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _a), bisect_af_mean(hi_d, _a)
    log(f"{_a} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo_d < AF_T < af_hi_d, f"{_a} bracket fail"
    for it in range(24):
        mid = (lo_d + hi_d) / 2
        if bisect_af_mean(mid, _a) < AF_T:
            lo_d = mid
        else:
            hi_d = mid
    GAIN[_a] = lo_d
    assert GAIN[_a] == _stored, (_a, GAIN[_a], _stored)
    af_d = bisect_af_mean(lo_d, _a)
    new_stairs[_a] = abs(af_d - AF_T)
    log(f"g_{_a} {lo_d:.6f} == stored EXACT | af_final {af_d:.6f}")
e_band_ok = {}
for _a in E_ARMS:
    lo_d, hi_d = 0.12, 0.18
    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _a), bisect_af_mean(hi_d, _a)
    log(f"{_a} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo_d < AF_T < af_hi_d, f"{_a} bracket fail"
    for it in range(24):
        mid = (lo_d + hi_d) / 2
        if bisect_af_mean(mid, _a) < AF_T:
            lo_d = mid
        else:
            hi_d = mid
    GAIN[_a] = lo_d
    af_d = bisect_af_mean(lo_d, _a)
    new_stairs[_a] = abs(af_d - AF_T)
    e_band_ok[_a] = bool(0.14 <= lo_d <= 0.16)
    _note = "" if e_band_ok[_a] else " [OUTSIDE .14-.16 band — DISCLOSED]"
    log(f"g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "
        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_note}")
g_eall_vs_g25 = dict(g_eAll=GAIN["eAll"], g_cutng25=GAIN["cutng25"],
                     equal=bool(GAIN["eAll"] == GAIN["cutng25"]))
log(f"A-EALL branch: {g_eall_vs_g25}")

'''
_b1 = src.index("# ---------------- rollouts ----------------")
# keep header + ANCH + lo_g/hi_g + def bisect_af_mean VERBATIM (through its
# return), replace only the old bisect-USAGE region (first usage .. rollouts)
src = src[:_def_end] + "\n\n" + BISECT + src[_b1:]

# R12 savez splice
_z0 = src.index('np.savez_compressed("l135/raw_l135.npz"')
_z1 = src.index('batches=np.array(SEEDS), **store)') + len('batches=np.array(SEEDS), **store)')
SAVEZ = '''np.savez_compressed("l142/raw_l142.npz", K=K,
                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
                    g_eOutInt=GAIN["eOutInt"], g_eOutMot=GAIN["eOutMot"],
                    g_eOutAll=GAIN["eOutAll"], g_eIn=GAIN["eIn"],
                    g_eAll=GAIN["eAll"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    cutng19_drop=cutk_drop["cutng19"], cutng29_drop=cutk_drop["cutng29"],
                    cutwA_drop=cutk_drop["cutwA"],
                    cutng25_drop=cutk_drop["cutng25"],
                    cutng25p_drop=cutk_drop["cutng25p"],
                    cutng23_drop=cutk_drop["cutng23"],
                    cutng26_drop=cutk_drop["cutng26"],
                    cutk5_drop=cutk_drop["cutk5"],
                    e_edges=np.array([E_EDGES[a] for a in E_ARMS]),
                    new_mass=np.array([cutk_pins[a]["mass_removed"] for a in NEW_ARMS]),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)'''
src = src[:_z0] + SAVEZ + src[_z1:]
src = src.replace('np.savez("l135/raw_partial.npz", **store)',
                  'np.savez("l142/raw_partial.npz", **store)')
src = src.replace('if os.path.exists("l135/raw_partial.npz"):',
                  'if os.path.exists("l142/raw_partial.npz"):')
src = src.replace('    z = np.load("l135/raw_partial.npz")',
                  '    z = np.load("l142/raw_partial.npz")')
assert 'l135/raw' not in src, "stale l135 path"

# R13 C0A section + tail splice
_c0 = src.index("# ---------------- C0A (PREREG): FULL-BATCH anchors")
_c1 = src.index("out = dict(")
C0A = '''# ---------------- C0A-142 (L142): anchors vs raw_l135 + B29 absence -----
_prevs = ["l115/raw_l115.npz", "l117/raw_l117.npz", "l118/raw_l118.npz",
          "l119/raw_l119.npz", "l120/raw_l120.npz", "l121/raw_l121.npz",
          "l122/raw_l122.npz", "l123/raw_l123.npz", "l124/raw_l124.npz",
          "l125/raw_l125.npz", "l126/raw_l126.npz", "l127/raw_l127.npz",
          "l128/raw_l128.npz", "l131/raw_l131.npz", "l133/raw_l133.npz",
          "l135/raw_l135.npz", "l137/raw_l137.npz",
          "l139/raw_l139_j0.npz", "l139/raw_l139_j1.npz",
          "l139/raw_l139_j2.npz", "l139/raw_l139_j3.npz",
          "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz",
          "l113/raw_l113.npz"]
for _p in _prevs:
    _zp = np.load(_p)
    assert not any(f"mm_full_{s}" in _zp.files for s in B29), \\
        ("B29 collides with " + _p + " (STOP)")
log(f"B29 absence across {len(_prevs)} stored npzs: PASS")
_poolkeys142 = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _poolkeys142.append(f"{_pk}_{_c}{_s}")
C0A142_KEYS = ["mm", "xm"] + _poolkeys142
z135c = np.load("l135/raw_l135.npz")
_arms142 = ("full", "b65", "cutwA", "cutng25")
assert all(f"{_k}_{_a}_801" in z135c.files for _k in C0A142_KEYS
           for _a in _arms142), "C0A-142 coverage miss"
c0a142 = {}
for s in (801, 901):
    for key in C0A142_KEYS:
        for a in _arms142:
            c0a142[f"135_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z135c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in _arms142:
        c0a142[f"135_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z135c[f"af_{a}_{s}"]))
c0a142_max = max(c0a142.values())
c0a142_pass = bool(all(v == 0.0 for v in c0a142.values()))
log(f"C0A-142 (4 arms x {len(C0A142_KEYS)} keys x 2 seeds) vs raw_l135: "
    f"{'PASS' if c0a142_pass else 'FAIL'} (max {c0a142_max:.1e})")
a_eall = {}
for s in (801, 901):
    for key in C0A142_KEYS:
        a_eall[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_eAll_{s}"] - store[f"{key}_cutng25_{s}"]).max())
a_eall_max = max(a_eall.values())
log(f"A-EALL eAll vs cutng25 in-run: max {a_eall_max:.1e} "
    f"(gains equal: {g_eall_vs_g25['equal']})")
'''
src = src[:_c0] + C0A + src[_c1:]

# R14 tail rewrite
_t0 = src.index("out = dict(")
TAIL = '''out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),
           g_eOutInt=GAIN["eOutInt"], g_eOutMot=GAIN["eOutMot"],
           g_eOutAll=GAIN["eOutAll"], g_eIn=GAIN["eIn"], g_eAll=GAIN["eAll"],
           e_band_ok=e_band_ok, new_stairs=new_stairs,
           e_edges=E_EDGES, K=K, mass_split=mass_split,
           n_seeds=len(SEEDS), g_eall_vs_g25=g_eall_vs_g25,
           a_eall_max=a_eall_max,
           c0a142_max=c0a142_max, c0a142_pass=c0a142_pass,
           c0a_pass=bool(c0a142_pass))
json.dump(out, open("l142/anchors_run.json", "w"), indent=1)
log(f"C0A-142 {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a142_max']:.1e}) | A-EALL max {a_eall_max:.1e} | "
    f"done {time.time()-t0:.0f}s")
'''
src = src[:_t0] + TAIL

# ---- drift guard + residual scan ----
assert "B26" not in src, "stale B26 token"
for tok, n in (("eAll=nzn[wA_pos_in_new],", 3),   # 3 noise dicts (settle+2 rollout phases)
               ("eAll=Xc_wA.clone(),", 2)):       # settle st + rollout X dicts
    c = src.count(tok)
    assert c == n, (f"token {tok!r} count {c} != {n}")
# semantic presence guards (lower-bounded, not guessed exact)
for tok, n in (('"eAll"', 1), ("build_e(", 2), ("E_ARMS", 5),
               ("bisect_af_mean(", 8),
               ("G_CUTWA_STORED", 2), ("G_CUTNG25_STORED", 2),
               ("C0A142_KEYS", 5), ("A-EALL", 3)):
    c = src.count(tok)
    assert c >= n, (f"token {tok!r} count {c} < {n}")
open("l142_run.py", "w").write(src)
py_compile.compile("l142_run.py", doraise=True)
print("l142_run.py written", len(src), "chars | py_compile OK | reps",
      len(reps))
