"""L137 build: l137_run.py from l135_run.py via count-asserted splices.

Every rep asserts count==expected BEFORE replacing (drift guard, L123
discipline); a residual scan over CODE lines catches stale tokens; the
kept sections are byte-exact source slices (no retyping)."""
import py_compile

src = open("l135_run.py").read()


def rep(old, new, n=1):
    global src
    assert src.count(old) == n, (src.count(old), n, old[:70])
    src = src.replace(old, new)


def splice(opener, closer, new):
    """Replace src[opener..closer) with new; closer line KEPT verbatim."""
    global src
    i = src.index(opener)
    assert src.count(opener) == 1, opener[:60]
    j = src.index(closer, i)
    src = src[:i] + new + src[j:]


# ---- R1: docstring ----
i0 = src.index('"""')
i1 = src.index('"""', i0 + 3) + 3
NEW_DOC = '''"""L137 run (L141): the REGISTERED dynamic DNp33 probe — why does
removing 1110 (with ranks 1-24) flip kill->super while mass-twin 319
does nothing? Clamp/volley grid on the INTACT closure substrate:
{full, b65, sil1110, sil319, silrand1-3, vol1110+volrand, sil24},
fresh B27 3101-3116 (absent from ALL stored npzs, precheck passed).
L135 machinery verbatim (extraction, pools, draw order, noise); NO
bisect phase (ADDENDUM A1 — gains stored, certified by full/b65
bit-identity at 801/901 vs raw_l113 + raw_l135); probe census FIRST
(ADDENDUM A4, L95 form) -> VAMP; sil24 cells == cutwA drop (l131 pin).
CPU-only; raw checkpoint BEFORE analysis.
"""'''
src = NEW_DOC + src[i1:]

# ---- R2: ARMS/GAIN ----
rep('''ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutng19", "cutng23", "cutwA", "cutng25", "cutng25p",
        "cutng26", "cutng29", "cutk5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutng19=None, cutng23=None, cutwA=None, cutng25=None,
            cutng25p=None, cutng26=None, cutng29=None, cutk5=None)''',
     '''ARMS = ["full", "b65", "sil1110", "sil319", "silrand1", "silrand2",
        "silrand3", "vol1110", "volrand", "sil24"]
INT_ARMS = ARMS[2:]
GAIN = dict(full=G_NEW, b65=G65,
            **{a: G_NEW for a in INT_ARMS})''')

# ---- R3: stored-gain constants -> no-bisect note ----
splice("G_CUT19_STORED = 0.15096808075904844",
       "ANCH = [801, 901]",
       "# L137 (ADDENDUM A1): zero bisects — all gains stored-form;\n"
       "# certified by full/b65 bit-identity anchors at the tail.\n")

# ---- R4: seeds (single-line reps — whitespace-drift-proof) ----
rep("B26 = list(range(3001, 3017))",
    "B27 = list(range(3101, 3117))  # fresh, absent ALL stored npzs")
rep("SEEDS = ANCH + B26", "SEEDS = ANCH + B27")
rep("FRESH = B26", "FRESH = B27")

# ---- R5: per-arm extension + intervention table (before AMPA) ----
rep("AMPA = np.zeros(WIN, np.float64)",
    '''# ---- L137: intervention arms share the FULL graph (PREREG D) ----
for a in INT_ARMS:
    WB[a] = Wb_n
    N_OF[a] = n_new
    POOLS[a] = POOLS["full"]
    mech[a] = mech["full"]
    motor[a] = motor["full"]
    dng100[a] = dng100["full"]
assert len(dng100["sil24"]) == S92["dng100"]
# twins pinned (l131 static): rank25 = 1110 carrier, rank26 = 319 neutral
assert int(ng_desc[24]) == 1110 and int(ng_desc[25]) == 319, "twin pins"
_pn = lambda g: int(loc_n[int(g)])
POOL56 = np.array(sorted(int(x) for x in ng_desc
                         if int(x) not in (1110, 319)))
assert len(POOL56) == 56
_rng = np.random.default_rng(20261118)
_rand4 = _rng.choice(POOL56, size=4, replace=False)
assert not np.isin(_rand4, (1110, 319)).any()
CLAMP = {a: torch.tensor([_pn(g)]) for a, g in
         (("sil1110", 1110), ("sil319", 319),
          ("silrand1", int(_rand4[0])), ("silrand2", int(_rand4[1])),
          ("silrand3", int(_rand4[2])))}
CLAMP["sil24"] = torch.tensor([_pn(g) for g in cutk_drop["cutwA"]])
assert len(CLAMP["sil24"]) == 24
VOLLEY_CELL = {"vol1110": _pn(1110), "volrand": _pn(int(_rand4[3]))}
CEN_IDS = [1110, 319] + [int(x) for x in ng_desc]
CEN_POS = torch.tensor([_pn(g) for g in CEN_IDS], dtype=torch.long)
log(f"interventions: silrand {list(map(int, _rand4[:3]))} volrand "
    f"{int(_rand4[3])} | sil24 n=24 | census n={len(CEN_IDS)}")
VAMP = None  # set by the probe below (ADDENDUM A4)

AMPA = np.zeros(WIN, np.float64)''')

# ---- R6: bisect section -> no-bisect note (settle machinery kept) ----
splice("# ---------------- P1 bisect for g_cut (l92 form, settle-only) ----------------",
       "# ---------------- rollouts ----------------",
       "# ---------------- L137: NO bisect phase (ADDENDUM A1) ----------------\n"
       "# settle_states/af_of retained verbatim above (reference, uncalled).\n"
       "\n")

# ---- R7: probe before the store/resume block ----
rep('''store = {}
if os.path.exists("l135/raw_partial.npz"):''',
    '''# ---------------- L137 probe (ADDENDUM A4): ONE base rollout --------
# Full arm ONLY at seed 3101, L95 form: window u/X census for the twins
# + all ng-58 -> VAMP = |u_min(1110)| + .1. Same generator seeds and
# draw order as the main loop => main-pass full@3101 must reproduce
# these traces bit-identically (free anchor, checked at the tail).
def probe_full(seed):
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    Xf = torch.zeros(n_new, 1)
    Xf[old_pos_in_new] = X0o
    Xf[new_pos] = X0n
    Ivf = torch.zeros(n_new, 1)
    Ivf[dng100["full"]] = D
    sp = 0.0
    for _ in range(SETTLE):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        sp += 2 * math.pi * 0.7 * DT
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))
        drive = torch.sparse.mm(WB["full"], Xf) * GAIN["full"] + Ivf
        drive[mech["full"], 0] = drive[mech["full"], 0] + sin_t
        Xf = Xf + (DT / TAU) * ((torch.relu(drive + BG) + nzn)
                                .clamp(max=RMAX) - Xf)
    cen_u_l = np.zeros((len(CEN_POS), WIN), np.float32)
    cen_x_l = np.zeros((len(CEN_POS), WIN), np.float32)
    mm = np.zeros(WIN, np.float32)
    xm = np.zeros(WIN, np.float32)
    tr = {kk: np.zeros(WIN, np.float32) for kk in POOLS["full"]}
    for k in range(WIN):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
        drive = torch.sparse.mm(WB["full"], Xf) * GAIN["full"] + Ivf
        if sin_t > 0:
            drive[mech["full"], 0] = drive[mech["full"], 0] + sin_t
        cen_u_l[:, k] = (drive[CEN_POS, 0] + BG).numpy()
        t = torch.relu(drive + BG)
        t = (t + nzn).clamp(max=RMAX)
        Xf = Xf + (DT / TAU) * (t - Xf)
        cen_x_l[:, k] = Xf[CEN_POS, 0].numpy()
        mm[k] = Xf[motor["full"]].mean()
        xm[k] = Xf[mech["full"]].mean()
        for kk in POOLS["full"]:
            tr[kk][k] = Xf[POOLS["full"][kk]].mean()
    return cen_u_l, cen_x_l, mm, xm, tr


cen_u, cen_x, probe_mm, probe_xm, probe_tr = probe_full(3101)
VAMP = abs(float(cen_u[CEN_IDS.index(1110)].min())) + 0.1
assert VAMP > 0
log(f"probe done {time.time()-t0:.0f}s | VAMP {VAMP:.4f} "
    f"(1110 u_min {float(cen_u[CEN_IDS.index(1110)].min()):+.4f})")

store = {}
if os.path.exists("l137/raw_partial.npz"):''')

# resume-path load + per-seed checkpoint path (l39-class direction pins)
rep('z = np.load("l135/raw_partial.npz")',
    'z = np.load("l137/raw_partial.npz")')
rep('np.savez("l135/raw_partial.npz", **store)',
    'np.savez("l137/raw_partial.npz", **store)')

# ---- R9: X dict ----
rep('''    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
             cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),
             cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),
             cutng25p=Xc_p25p.clone(),
             cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),
             cutk5=Xc_k5.clone(),
             b65=Xo65.clone())''',
    '''    X = dict(full=Xc_full.clone(), b65=Xo65.clone(),
             **{a: Xc_full.clone() for a in INT_ARMS})''')

# ---- R10: noise dicts (THREE sites: settle_states + settle + window) ----
rep("                     b65=nz_o)",
    "                     b65=nz_o,\n"
    "                     **{a: nzn for a in INT_ARMS})", n=3)

# ---- R11: window-step hooks ----
rep('''        for a in ARMS:
            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            if sin_t > 0:
                drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            t = torch.relu(drive + BG)
            t = (t + noise[a]).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])''',
    '''        for a in ARMS:
            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            if sin_t > 0:
                drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            if a in VOLLEY_CELL:
                drive[VOLLEY_CELL[a], 0] = drive[VOLLEY_CELL[a], 0] + VAMP
            t = torch.relu(drive + BG)
            t = (t + noise[a]).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
            if a in CLAMP:
                X[a][CLAMP[a], 0] = 0.0''')

# ---- R12: final savez (R13 replaces the tail from the C0A header) ----
splice('np.savez_compressed("l135/raw_l135.npz"',
       "# ---------------- C0A (PREREG): FULL-BATCH anchors vs raw_l113 ----------------",
       '''np.savez_compressed("l137/raw_l137.npz",
                    g_full=G_NEW, g65=G65, vamp=np.float64(VAMP),
                    census_ids=np.array(CEN_IDS),
                    census_u=cen_u, census_x=cen_x,
                    silrand_ids=_rand4.astype(np.int64),
                    clamp_sil24=np.array([int(x) for x in cutk_drop["cutwA"]],
                                         np.int64),
                    batches=np.array(SEEDS), **store)
log("raw_l137.npz checkpointed BEFORE analysis")

''')

# ---- R13: anchor tail ----
tail = src.index("# ---------------- C0A (PREREG): FULL-BATCH anchors vs raw_l113 ----------------")
src = src[:tail] + '''# ---------------- anchors (ADDENDUM A1/A4) ----------------
zprev = np.load("l113/raw_l113.npz")
z135a = np.load("l135/raw_l135.npz")
C0A_KEYS = ["mm", "xm"] + [f"{k}_{c}{s}" for k in ("Ti", "Tr")
                           for c in ("f", "e") for s in ("L", "R")]
assert all(f"{k}_full_801" in zprev.files for k in C0A_KEYS)
assert all(f"{k}_full_801" in z135a.files for k in C0A_KEYS)
# B27 freshness across the whole stored shelf (precheck re-assert)
for _prev in ("l113/raw_l113.npz", "l115/raw_l115.npz",
              "l117/raw_l117.npz", "l118/raw_l118.npz",
              "l119/raw_l119.npz", "l120/raw_l120.npz",
              "l121/raw_l121.npz", "l122/raw_l122.npz",
              "l123/raw_l123.npz", "l124/raw_l124.npz",
              "l125/raw_l125.npz", "l126/raw_l126.npz",
              "l127/raw_l127.npz", "l128/raw_l128.npz",
              "l131/raw_l131.npz", "l133/raw_l133.npz",
              "l135/raw_l135.npz",
              "l139/raw_l139_j0.npz", "l139/raw_l139_j1.npz",
              "l139/raw_l139_j2.npz", "l139/raw_l139_j3.npz",
              "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B27), \\
        ("B27 collides with " + _prev + " (STOP)")
    _zp.close()
ANCH_ARMS = ("full", "b65")
c0a = {}
c0a135 = {}
for s in (801, 901):
    for key in C0A_KEYS:
        for a in ANCH_ARMS:
            c0a[f"113_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - zprev[f"{key}_{a}_{s}"][:WIN]).max())
            c0a135[f"135_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z135a[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ANCH_ARMS:
        c0a[f"113_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(zprev[f"af_{a}_{s}"]))
        c0a135[f"135_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z135a[f"af_{a}_{s}"]))
c0a_pass = bool(all(v == 0.0 for v in c0a.values()))
c0a135_pass = bool(all(v == 0.0 for v in c0a135.values()))
log(f"C0A full/b65 vs raw_l113: {'PASS' if c0a_pass else 'FAIL'} "
    f"(max {max(c0a.values()):.1e}) | vs raw_l135: "
    f"{'PASS' if c0a135_pass else 'FAIL'} (max {max(c0a135.values()):.1e})")
# probe anchor (ADDENDUM A4): deterministic same-generator reroll
probe_keys = ["mm", "xm"] + sorted(POOLS["full"])
pa = {"mm": float(np.abs(store["mm_full_3101"] - probe_mm).max()),
      "xm": float(np.abs(store["xm_full_3101"] - probe_xm).max())}
for key in sorted(POOLS["full"]):
    pa[key] = float(np.abs(store[f"{key}_full_3101"]
                           - probe_tr[key]).max())
probe_pass = bool(all(v == 0.0 for v in pa.values()))
log(f"PROBE anchor full@3101 reroll: {'PASS' if probe_pass else 'FAIL'} "
    f"(max {max(pa.values()):.1e}, {len(pa)} keys)")


def _census(cid):
    i = CEN_IDS.index(cid)
    return dict(u_min=float(cen_u[i].min()), u_mean=float(cen_u[i].mean()),
                u_max=float(cen_u[i].max()), x_mean=float(cen_x[i].mean()))


cen_1110 = _census(1110)
cen_319 = _census(319)
log(f"census 1110 {cen_1110} | 319 {cen_319} | VAMP {VAMP:.4f}")
out = dict(c0a_pass=c0a_pass, c0a_max=max(c0a.values()),
           c0a135_pass=c0a135_pass, c0a135_max=max(c0a135.values()),
           probe_pass=probe_pass, probe_max=max(pa.values()),
           vamp=VAMP, census_1110=cen_1110, census_319=cen_319,
           silrand=[int(x) for x in _rand4],
           clamp_sil24_n=len(CLAMP["sil24"]),
           n_seeds=len(SEEDS))
json.dump(out, open("l137/anchors_run.json", "w"), indent=1)
log(f"anchors written | done {time.time()-t0:.0f}s")
'''

# ---- residual scan (code lines; comments/docstrings whitelisted) ----
FORBID = ["B26", "bisect_af_mean", "G_CUT", "lo_g", "af_final",
          "cutng25p_stored", "l135/raw_partial", "new_stairs",
          "raw_l135.npz\")", "c0a120", "c0a133"]
bad = []
for ln, line in enumerate(src.splitlines(), 1):
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    if "np.load" in line or "for _prev in" in line:  # prior-run INPUTS ok
        if any(f in line for f in ("raw_l113", "raw_l135", "raw_l139",
                                   "raw_l115", "raw_l117", "raw_l118",
                                   "raw_l119", "raw_l120", "raw_l121",
                                   "raw_l122", "raw_l123", "raw_l124",
                                   "raw_l125", "raw_l126", "raw_l127",
                                   "raw_l128", "raw_l131", "raw_l133")):
            continue
    for f in FORBID:
        if f in line:
            bad.append((ln, f, line.strip()[:80]))
assert not bad, ("RESIDUAL SCAN FAIL", bad[:10])
print("residual scan clean")

open("l137_run.py", "w").write(src)
py_compile.compile("l137_run.py", doraise=True)
print("l137_run.py written + py_compile OK,", len(src.splitlines()), "lines")
