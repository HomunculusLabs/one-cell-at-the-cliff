"""l144_build.py — transform l142_run.py -> l144_run.py (count-asserted
reps + residual scan + py_compile; l131/l123/l126 discipline). PREREG
l144/PREREG.md FIRST. Arms: full, b65, cutwA, cutng25, sil1110 (full
base), sil1110_wA (cutwA base, gain == cutwA stored). Edge arms DELETED
(not spectated); clamp = l137 window-loop form VERBATIM."""
import py_compile
import re
import sys

SRC = "l142_run.py"
DST = "l144_run.py"
s = open(SRC).read()
orig = s


def rep(name, old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (name, "count", n, "!=", count)
    s = s.replace(old, new)
    print(f"rep {name}: ok ({count})")


# ---- A: docstring (splice on unique opener through closing quotes) ----
i0 = s.index('"""L142 run:')
i1 = s.index('"""', i0 + 3) + 3
s = s[:i0] + '"""L144 run: sil1110-ON-wA-base — the missing grid cell of\n' \
    'L141/L142 (PREREG l144/PREREG.md FIRST). Arms: full, b65, cutwA\n' \
    '(partial base), cutng25 (super ref) + sil1110 (full graph + clamp\n' \
    'X[1110]=0, l137 form verbatim: window-loop only, after update,\n' \
    'before readouts) + sil1110_wA (cutwA graph + clamp [loc_wA[1110]],\n' \
    'gain == cutwA stored — af-matched by graph identity, disclosed).\n' \
    'Edge arms DELETED (l142 B29 ladder stands); spectator arms verbatim,\n' \
    'never advanced (l139 law). FRESH B30 3317-3332 (absent all stored\n' \
    'npzs incl l142 raws). Anchors: stored gains EXACT (cutwA/cutng25),\n' \
    'C0A-144 vs raw_l135 (4 arms), FORWARD CHAIN vs raw_l142 (4 arms) +\n' \
    'raw_l137 sil1110 @801/901 == 0.0 (clamp-wiring cert). CPU-only; raw\n' \
    'checkpoint BEFORE analysis.\n"""' + s[i1:]
print("rep docstring: ok")

# ---- B: ARMS / GAIN ----
rep("ARMS/GAIN", '''ARMS = ["full", "b65", "cutwA", "cutng25",
        "eOutInt", "eOutMot", "eOutAll", "eIn", "eAll"]
GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            eOutInt=None, eOutMot=None, eOutAll=None, eIn=None,
            eAll=None)''', '''ARMS = ["full", "b65", "cutwA", "cutng25", "sil1110", "sil1110_wA"]
GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            sil1110=G_NEW, sil1110_wA=None)  # wA clamp gain set below''')

# ---- C: B30 seeds ----
rep("B30 seeds", '''B29 = list(range(3301, 3317))  # fresh, absent l107..l137 + l139 j0-j5
SEEDS = ANCH + B29                  # anchors FIRST: early wiring verdict
FRESH = B29''', '''B30 = list(range(3317, 3333))  # fresh, absent l107..l142 (precheck)
SEEDS = ANCH + B30                  # anchors FIRST: early wiring verdict
FRESH = B30''')

# ---- D: edge build block -> CLAMP block ----
d0 = s.index("# ---- L142: edge-footprint arms on the cutwA node set")
d1m = "Wb_e = {a: wb(We[a]) for a in E_ARMS}"
d1 = s.index(d1m)
d1 = s.index("\n", d1) + 1
s = s[:d0] + '''# ---- L144: activity-clamp arms (PREREG l144; l137 CLAMP form) ----
GI_CARRIER = 1110
assert int(ng_desc[24]) == GI_CARRIER and int(ng_desc[25]) == 319
assert keep_new[GI_CARRIER] and keep_cutk["cutwA"][GI_CARRIER], \\
    "carrier 1110 must sit in BOTH the full and cutwA node sets"
CLAMP = {"sil1110": torch.tensor([int(loc_n[GI_CARRIER])]),
         "sil1110_wA": torch.tensor([int(loc_wA[GI_CARRIER])])}
GAIN["sil1110_wA"] = G_CUTWA_STORED  # graph-identity af-match (PREREG)

''' + s[d1:]
print("rep edge-build->CLAMP: ok")

# ---- E: alias loop ----
rep("alias loop", '''# L142: edge arms share cutwA's node set — alias every per-arm map
for _ea in E_ARMS:
    POOLS[_ea] = POOLS["cutwA"]
    mech[_ea] = mech["cutwA"]
    motor[_ea] = motor["cutwA"]
    dng100[_ea] = dng100["cutwA"]
    WB[_ea] = Wb_e[_ea]
    N_OF[_ea] = n_cutk["cutwA"]''', '''# L144: sil arms alias their BASE graph's per-arm maps; the window-loop
# clamp is the ONLY difference from the base arm (settle clamp-free)
for _sa, _base in (("sil1110", "full"), ("sil1110_wA", "cutwA")):
    POOLS[_sa] = POOLS[_base]
    mech[_sa] = mech[_base]
    motor[_sa] = motor[_base]
    dng100[_sa] = dng100[_base]
    WB[_sa] = WB[_base]
    N_OF[_sa] = N_OF[_base]''')

# ---- F: bisect gains dict ----
rep("bisect gains", '''cutng26=g, cutk5=g, eOutInt=g, eOutMot=g,
                                  eOutAll=g, eIn=g, eAll=g))''', '''cutng26=g, cutk5=g, sil1110=G_NEW,
                                  sil1110_wA=g))''')

# ---- G: E_ARMS bisect loop -> assert block ----
g0 = s.index("e_band_ok = {}\nfor _a in E_ARMS:")
g1m = 'log(f"A-EALL branch: {g_eall_vs_g25}")'
g1 = s.index(g1m)
g1 = s.index("\n", g1) + 1
s = s[:g0] + '''# L144: NO fresh bisects (PREREG A1) — sil1110_wA rides cutwA's stored
# gain (same node set + same gain => settle af == cutwA exactly);
# assert the identity the re-bisect above certified.
assert GAIN["sil1110_wA"] == GAIN["cutwA"] == G_CUTWA_STORED, "wA gain"
''' + s[g1:]
print("rep bisect-loop->assert: ok")

# ---- H: st dict (settle_states, 14-space) ----
rep("st dict", '''              eOutInt=Xc_wA.clone(), eOutMot=Xc_wA.clone(),
              eOutAll=Xc_wA.clone(), eIn=Xc_wA.clone(),
              eAll=Xc_wA.clone(),''',
    '''              sil1110=Xc_full.clone(), sil1110_wA=Xc_wA.clone(),''')

# ---- I: X dict (seed loop, 13-space) ----
rep("X dict", '''             eOutInt=Xc_wA.clone(), eOutMot=Xc_wA.clone(),
             eOutAll=Xc_wA.clone(), eIn=Xc_wA.clone(),
             eAll=Xc_wA.clone(),''',
    '''             sil1110=Xc_full.clone(), sil1110_wA=Xc_wA.clone(),''')

# ---- J: noise dicts (THREE sites, l123 law) ----
pat = re.compile(r"( *)eOutInt=nzn\[wA_pos_in_new\], eOutMot=nzn\[wA_pos_in_new\],\n"
                 r" *eOutAll=nzn\[wA_pos_in_new\], eIn=nzn\[wA_pos_in_new\],\n"
                 r" *eAll=nzn\[wA_pos_in_new\],")
s, nj = pat.subn(r"\1sil1110=nzn, sil1110_wA=nzn[wA_pos_in_new],", s)
assert nj == 3, ("noise dicts", nj)
print("rep noise x3: ok")

# ---- K: window-loop clamp (l137 form VERBATIM position) ----
rep("clamp insert", '''            X[a] = X[a] + (DT / TAU) * (t - X[a])
        for a in ARMS:
            mm[a][k] = X[a][motor[a]].mean()''', '''            X[a] = X[a] + (DT / TAU) * (t - X[a])
            if a in CLAMP:
                X[a][CLAMP[a], 0] = 0.0
        for a in ARMS:
            mm[a][k] = X[a][motor[a]].mean()''')

# ---- L: savez / paths ----
rep("savez head", '''np.savez_compressed("l142/raw_l142.npz", K=K,
                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
                    g_eOutInt=GAIN["eOutInt"], g_eOutMot=GAIN["eOutMot"],
                    g_eOutAll=GAIN["eOutAll"], g_eIn=GAIN["eIn"],
                    g_eAll=GAIN["eAll"],''', '''np.savez_compressed("l144/raw_l144.npz", K=K,
                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
                    g_sil1110=GAIN["sil1110"],
                    g_sil1110_wA=GAIN["sil1110_wA"],''')
rep("savez e_edges drop", '''                    e_edges=np.array([E_EDGES[a] for a in E_ARMS]),
''', "")
rep("ckpt log", 'log("raw_l135.npz checkpointed BEFORE analysis")',
    'log("raw_l144.npz checkpointed BEFORE analysis")')
rep("resume path", 'z = np.load("l142/raw_partial.npz")',
    'z = np.load("l144/raw_partial.npz")')
rep("partial path", 'np.savez("l142/raw_partial.npz", **store)',
    'np.savez("l144/raw_partial.npz", **store)')

rep("resume exists path", 'if os.path.exists("l142/raw_partial.npz"):',
    'if os.path.exists("l144/raw_partial.npz"):')

# ---- M: anchors tail (splice marker -> EOF) ----
m0 = s.index("# ---------------- C0A-142 (L142): anchors vs raw_l135")
s = s[:m0] + '''# ---------------- C0A-144 + FORWARD CHAIN (L120 law) + B30 absence ---
_prevs = ["l115/raw_l115.npz", "l117/raw_l117.npz", "l118/raw_l118.npz",
          "l119/raw_l119.npz", "l120/raw_l120.npz", "l121/raw_l121.npz",
          "l122/raw_l122.npz", "l123/raw_l123.npz", "l124/raw_l124.npz",
          "l125/raw_l125.npz", "l126/raw_l126.npz", "l127/raw_l127.npz",
          "l128/raw_l128.npz", "l131/raw_l131.npz", "l133/raw_l133.npz",
          "l135/raw_l135.npz", "l137/raw_l137.npz",
          "l139/raw_l139_j0.npz", "l139/raw_l139_j1.npz",
          "l139/raw_l139_j2.npz", "l139/raw_l139_j3.npz",
          "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz",
          "l113/raw_l113.npz",
          "l142/raw_l142.npz", "l142/raw_partial.npz"]
for _p in _prevs:
    _zp = np.load(_p)
    assert not any(f"mm_full_{s}" in _zp.files for s in B30), \\
        ("B30 collides with " + _p + " (STOP)")
log(f"B30 absence across {len(_prevs)} stored npzs: PASS")
_poolkeys144 = []
for _pk, (_ag, _bg) in ((\"Ti\", (\"f\", \"e\")), (\"Tr\", (\"f\", \"e\")),
                        (\"Ta\", (\"a\", \"b\")), (\"Sr\", (\"a\", \"b\")),
                        (\"Pr\", (\"a\", \"b\"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _poolkeys144.append(f"{_pk}_{_c}{_s}")
C0A144_KEYS = ["mm", "xm"] + _poolkeys144
_arms144 = ("full", "b65", "cutwA", "cutng25")
z135c = np.load("l135/raw_l135.npz")
z142c = np.load("l142/raw_l142.npz")
z137c = np.load("l137/raw_l137.npz")
assert all(f"{_k}_{_a}_801" in z135c.files for _k in C0A144_KEYS
           for _a in _arms144), "C0A-144 coverage miss (l135)"
assert all(f"{_k}_{_a}_801" in z142c.files for _k in C0A144_KEYS
           for _a in _arms144), "FC-142 coverage miss"
assert all(f"{_k}_sil1110_801" in z137c.files for _k in C0A144_KEYS), \\
    "FC-137 sil1110 coverage miss"
c0a144, fc142, fc137 = {}, {}, {}
for s_ in (801, 901):
    for key in C0A144_KEYS:
        for a in _arms144:
            c0a144[f"135_{key}_{a}_{s_}"] = float(np.abs(
                store[f"{key}_{a}_{s_}"] - z135c[f"{key}_{a}_{s_}"][:WIN]).max())
            fc142[f"{key}_{a}_{s_}"] = float(np.abs(
                store[f"{key}_{a}_{s_}"] - z142c[f"{key}_{a}_{s_}"][:WIN]).max())
        fc137[f"sil1110_{key}_{s_}"] = float(np.abs(
            store[f"{key}_sil1110_{s_}"]
            - z137c[f"{key}_sil1110_{s_}"][:WIN]).max())
    for a in _arms144:
        c0a144[f"135_af_{a}_{s_}"] = abs(float(store[f"af_{a}_{s_}"])
                                         - float(z135c[f"af_{a}_{s_}"]))
        fc142[f"af_{a}_{s_}"] = abs(float(store[f"af_{a}_{s_}"])
                                    - float(z142c[f"af_{a}_{s_}"]))
    fc137[f"sil1110_af_{s_}"] = abs(float(store[f"af_sil1110_{s_}"])
                                    - float(z137c[f"af_sil1110_{s_}"]))
c0a144_max = max(c0a144.values())
fc142_max = max(fc142.values())
fc137_max = max(fc137.values())
c0a144_pass = bool(all(v == 0.0 for v in c0a144.values()))
fc142_pass = bool(all(v == 0.0 for v in fc142.values()))
fc137_pass = bool(all(v == 0.0 for v in fc137.values()))
log(f"C0A-144 (4 arms x {len(C0A144_KEYS)} keys x 2 seeds) vs raw_l135: "
    f"{'PASS' if c0a144_pass else 'FAIL'} (max {c0a144_max:.1e})")
log(f"FC-142 forward chain (same 4 arms) vs raw_l142: "
    f"{'PASS' if fc142_pass else 'FAIL'} (max {fc142_max:.1e})")
log(f"FC-137 clamp-wiring cert sil1110 vs raw_l137: "
    f"{'PASS' if fc137_pass else 'FAIL'} (max {fc137_max:.1e})")
out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
           g_sil1110=GAIN["sil1110"], g_sil1110_wA=GAIN["sil1110_wA"],
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),
           clamp_sil1110=int(loc_n[GI_CARRIER]),
           clamp_sil1110_wA=int(loc_wA[GI_CARRIER]),
           c0a144_max=c0a144_max, c0a144_pass=c0a144_pass,
           fc142_max=fc142_max, fc142_pass=fc142_pass,
           fc137_max=fc137_max, fc137_pass=fc137_pass,
           n_seeds=len(SEEDS),
           c0a_pass=bool(c0a144_pass and fc142_pass and fc137_pass))
json.dump(out, open("l144/anchors_run.json", "w"), indent=1)
log(f"ANCHORS {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(C0A {c0a144_max:.1e} | FC142 {fc142_max:.1e} | "
    f"FC137 {fc137_max:.1e}) | done {time.time()-t0:.0f}s")
'''
print("rep anchors-tail: ok")

# ---- global B29 -> B30 (stragglers in logs/comments) ----
nb = s.count("B29")
s = s.replace("B29", "B30")
print(f"rep B29->B30 global: {nb} sites")
assert "B29" not in s

# ---- residual scan: deleted tokens must not survive on CODE lines ----
BAD = ["eOutInt", "eOutMot", "eOutAll", "eAll", "E_ARMS", "E_EDGES",
       "Wb_e", "build_e", "e_drop", "e_band_ok", "g_eall", "We[",
       "out_int_e", "out_mot_e", "in_sel_e", "emask_wA", "keep_wA_e"]
res = []
_in_prevs = False
for ln, line in enumerate(s.splitlines(), 1):
    st = line.strip()
    if st.startswith("#") or not st:
        continue  # comment/blank whitelist by line context (l126 law)
    if st.startswith("_prevs = ["):
        _in_prevs = True
    if _in_prevs and st.endswith("]"):
        _in_prevs = False
        if "l142/" in line:
            continue  # final _prevs line, deliberate INPUT read
    elif _in_prevs and "l142/" in line:
        continue  # deliberate INPUT reads of the prior run's raws
    if "np.load(\"l142/" in line:
        continue  # input direction (l118 law)
    if _in_prevs and st.endswith("]"):
        _in_prevs = False
    for t in BAD:
        if t in line:
            res.append((ln, t, line[:80]))
    # any WRITE to l142/ paths is a direction bug
    if "l142/" in line and ("savez" in line or "open(\"l142/" in line):
        res.append((ln, "WRITE-to-l142", line[:80]))
# 'eIn' as a WORD (avoid 'eIn' substring inside other tokens is not an
# issue here; check word boundary)
for ln, line in enumerate(s.splitlines(), 1):
    st = line.strip()
    if st.startswith("#") or not st:
        continue
    if re.search(r"\beIn\b", line):
        res.append((ln, "eIn(word)", line[:80]))
assert not res, ("residual survivors", res[:8])

# ---- presence scan: new tokens at their required sites ----
need = {"CLAMP": 4, "sil1110_wA": 12, "sil1110": 30, "B30": 6,
        "raw_l144": 2}
for t, mn in need.items():
    c = s.count(t)
    assert c >= mn, ("presence", t, c, "<", mn)
    print(f"presence {t}: {c} (>= {mn})")

open(DST, "w").write(s)
py_compile.compile(DST, doraise=True)
print(f"{DST} written ({len(s.splitlines())} lines) + py_compile OK")
print(f"delta vs {SRC}: {len(s.splitlines()) - len(orig.splitlines())} lines")
