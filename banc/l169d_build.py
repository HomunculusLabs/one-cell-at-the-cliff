"""l169d_build.py — count-asserted ADDITIVE transform of l169c2_run.py
into l169d_run.py for L169 stage (d) (PREREG l169d/PREREG.md).

Adds THREE arms on a fresh batch B38 3513-3528:
  cutng25p = the XOR twin graph (base window + the mass-twin gi 319
             removed instead of the carrier gi 1110) at its OWN gain,
             bisected in the STORED-FORM loop so the bisect must
             reproduce g_cutng25p = 0.1435265743732452 EXACTLY;
  p25gN    = the cutng25p CSR by object identity at g_cutng25 (up);
  n25gP    = the cutng25 CSR by object identity at g_cutng25p (down).

Every replacement is count-asserted; a residual scan then refuses any
surviving WRITE to a prior run's artifact (l169c2 may appear only as an
INPUT path literal) and any surviving B37 token in a CODE line, and
py_compile gates the output.
"""
import py_compile
import re
import sys

SRC = "l169c2_run.py"
DST = "l169d_run.py"
src = open(SRC).read()
reps = []


def rep(old, new, n=1, tag=""):
    reps.append((old, new, n, tag))


# ---------------- R1: header ----------------
rep('"""L169c2 run: pre-posting control (c2), the REWIRE + SAME-FOOTPRINT-',
    '"""L169d run: pre-posting control (d), the XOR-PAIR GAIN-SWAP 2x2.\n'
    'PREREG l169d/PREREG.md FIRST. NEW ARMS: cutng25p = the twin-XOR graph\n'
    '(base window + the mass-twin gi 319 / DNpe025-R removed instead of the\n'
    'carrier gi 1110 / DNp33-L) at its OWN af-matched gain, bisected in the\n'
    'STORED-FORM loop (must reproduce g_cutng25p EXACTLY or VOID); p25gN =\n'
    'the cutng25p CSR VERBATIM at g_cutng25 (swapped UP); n25gP = the\n'
    'cutng25 CSR VERBATIM at g_cutng25p (swapped DOWN). The swap arms are\n'
    'DELIBERATELY off the matched operating point (that is the test, stage\n'
    '(a) convention) — P-af direction registered instead of an af identity.\n'
    'CERT-1 = FC-169C2 forward chain on the 16 inherited arms vs\n'
    'l169c2/raw_l169c2.npz at 801/901; CERT-2 = C0A-150 extended to FIVE\n'
    'arms so cutng25p is bit-checked against l135/raw_l135.npz (the new\n'
    "arm's free wiring certificate); C0-NT(d) = each swap arm separated\n"
    'from its own-gain twin. FRESH B38 3513-3528. Stage-(c2) prose retained\n'
    'below for lineage.\n'
    '\n'
    'L169c2 run: pre-posting control (c2), the REWIRE + SAME-FOOTPRINT-',
    1, "R1 header")

# ---------------- R2/R3: ARMS + GAIN ----------------
rep('        "rew1", "rew2", "rew3", "hom"]',
    '        "rew1", "rew2", "rew3", "hom",\n'
    '        "cutng25p", "p25gN", "n25gP"]', 1, "R2 ARMS")
rep('            hom=None)  # silW/swap/f4/c2 arms below',
    '            hom=None, cutng25p=None,\n'
    '            p25gN=None, n25gP=None)  # silW/swap/f4/c2/d arms below',
    1, "R3 GAIN")

# ---------------- R4: stored-gain constant for the twin ----------------
rep('G_EMOTBOT5_STORED = 0.14367126345634465  # l145 stored, FC-145 EXACT assert',
    'G_EMOTBOT5_STORED = 0.14367126345634465  # l145 stored, FC-145 EXACT assert\n'
    'G_CUTNG25P_STORED = 0.1435265743732452  # l135 stored, L169d CERT-3 EXACT',
    1, "R4 g_cutng25p constant")

# ---------------- R5: fresh batch ----------------
rep('B37 = list(range(3481, 3497))  # fresh (prior batch B36 = l169 stage b2;\n'
    '# key-scanned absent from all 72 stored raw npzs before registration,\n'
    '# L157 rule)\n'
    'SEEDS = ANCH + B37                  # anchors FIRST: early wiring verdict\n'
    'FRESH = B37',
    'B38 = list(range(3513, 3529))  # fresh (prior batch B37 = l169 stage c2;\n'
    '# key-scanned absent from all 74 stored raw npzs before registration,\n'
    '# L157 rule: both the mm_full_<seed> form and an any-key-endswith scan)\n'
    'SEEDS = ANCH + B38                  # anchors FIRST: early wiring verdict\n'
    'FRESH = B38',
    1, "R5 batch B38")

# ---------------- R6: (d) swap-arm plumbing ----------------
rep('assert N_OF["wAgN"] == n_cutk["cutwA"] and N_OF["n25gW"] == n_cutk["cutng25"]',
    'assert N_OF["wAgN"] == n_cutk["cutwA"] and N_OF["n25gW"] == n_cutk["cutng25"]\n'
    '\n'
    '# ---- L169 (d): the XOR-PAIR gain-swap arms. p25gN = the cutng25p CSR\n'
    '# at g_cutng25 (swapped UP); n25gP = the cutng25 CSR at g_cutng25p\n'
    '# (swapped DOWN). Graph objects are the SAME CSR objects as their\n'
    '# own-gain twins (object identity asserted below); the ONLY difference\n'
    '# is the scalar GAIN. No clamp, no new graph, no bisect for these two.\n'
    'D_SWAP = ("p25gN", "n25gP")\n'
    'for _sd, _tw, _Wtw in (("p25gN", "cutng25p", Wb_p25p),\n'
    '                       ("n25gP", "cutng25", Wb_p25)):\n'
    '    POOLS[_sd] = POOLS[_tw]\n'
    '    mech[_sd] = mech[_tw]\n'
    '    motor[_sd] = motor[_tw]\n'
    '    dng100[_sd] = dng100[_tw]\n'
    '    WB[_sd] = _Wtw\n'
    '    N_OF[_sd] = n_cutk[_tw]\n'
    'assert WB["p25gN"] is WB["cutng25p"] and WB["n25gP"] is WB["cutng25"], \\\n'
    '    "L169d GRAPH-IDENTITY broken (STOP)"\n'
    'assert N_OF["p25gN"] == n_cutk["cutng25p"] and \\\n'
    '    N_OF["n25gP"] == n_cutk["cutng25"]',
    1, "R6 d swap plumbing")

# ---------------- R7/R8: Xc init dicts (two indentations) ----------------
rep('              wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),\n'
    '              b65=Xo65.clone())',
    '              wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),\n'
    '              p25gN=Xc_p25p.clone(), n25gP=Xc_p25.clone(),\n'
    '              b65=Xo65.clone())', 1, "R7 Xc settle")
rep('             wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),\n'
    '             b65=Xo65.clone())',
    '             wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),\n'
    '             p25gN=Xc_p25p.clone(), n25gP=Xc_p25.clone(),\n'
    '             b65=Xo65.clone())', 1, "R8 Xc rollout")

# ---------------- R9: noise dicts (THREE sites: settle + settle-phase +
# WIN-phase; l123 rule — count-pin shared-line patterns across ALL sites)
rep('                     wAgN=nzn[wA_pos_in_new], n25gW=nzn[p25_pos_in_new],\n'
    '                     b65=nz_o)',
    '                     wAgN=nzn[wA_pos_in_new], n25gW=nzn[p25_pos_in_new],\n'
    '                     p25gN=nzn[p25p_pos_in_new],\n'
    '                     n25gP=nzn[p25_pos_in_new],\n'
    '                     b65=nz_o)', 3, "R9 noise dicts x3")

# ---------------- R10: bisect gains dict ----------------
rep('                                  wAgN=g, n25gW=g,',
    '                                  wAgN=g, n25gW=g,\n'
    '                                  p25gN=g, n25gP=g,', 1, "R10 bisect gains")

# ---------------- R11: stored-form bisect gains the twin ----------------
rep('for _a in ("cutwA", "cutng25"):\n'
    '    _stored = {"cutwA": G_CUTWA_STORED, "cutng25": G_CUTNG25_STORED}[_a]',
    'for _a in ("cutwA", "cutng25", "cutng25p"):\n'
    '    _stored = {"cutwA": G_CUTWA_STORED, "cutng25": G_CUTNG25_STORED,\n'
    '               "cutng25p": G_CUTNG25P_STORED}[_a]',
    1, "R11 stored-form bisect + cutng25p")

# ---------------- R12: (d) swap gains ----------------
rep("log(f\"L169 swap gains | wAgN {GAIN['wAgN']:.9f} (cutwA graph) | \"\n"
    "    f\"n25gW {GAIN['n25gW']:.9f} (cutng25 graph)\")",
    "log(f\"L169 swap gains | wAgN {GAIN['wAgN']:.9f} (cutwA graph) | \"\n"
    "    f\"n25gW {GAIN['n25gW']:.9f} (cutng25 graph)\")\n"
    '# L169 (d) swap: the XOR pair\'s OWN bisected gains, imported, never\n'
    '# re-bisected. p25gN = twin graph at the carrier arm\'s HIGHER gain;\n'
    '# n25gP = carrier graph at the twin arm\'s LOWER gain.\n'
    'GAIN["p25gN"] = GAIN["cutng25"]\n'
    'GAIN["n25gP"] = GAIN["cutng25p"]\n'
    'assert GAIN["p25gN"] == G_CUTNG25_STORED and \\\n'
    '    GAIN["n25gP"] == G_CUTNG25P_STORED, \\\n'
    '    "L169d swap gains not the stored pair (STOP)"\n'
    'assert GAIN["p25gN"] != GAIN["cutng25p"] and \\\n'
    '    GAIN["n25gP"] != GAIN["cutng25"], "L169d swap is a no-op (STOP)"\n'
    'assert GAIN["cutng25p"] < GAIN["cutwA"] < GAIN["cutng25"], \\\n'
    '    "stored gain ORDER drift (STOP)"\n'
    "log(f\"L169d swap gains | p25gN {GAIN['p25gN']:.9f} (cutng25p graph, \"\n"
    "    f\"up) | n25gP {GAIN['n25gP']:.9f} (cutng25 graph, down)\")",
    1, "R12 d swap gains")

# ---------------- R13: P-af records for the (d) arms ----------------
rep('                     n25gW_below=bool(af_c["n25gW"] < AF_T))',
    '                     n25gW_below=bool(af_c["n25gW"] < AF_T),\n'
    '                     cutng25p=af_c["cutng25p"],\n'
    '                     p25gN=af_c["p25gN"], n25gP=af_c["n25gP"],\n'
    '                     p25gN_above=bool(af_c["p25gN"] > AF_T),\n'
    '                     n25gP_below=bool(af_c["n25gP"] < AF_T))',
    1, "R13 paf d records")

# ---------------- R14/R15: own output paths ----------------
rep('if os.path.exists("l169c2/raw_partial.npz"):',
    'if os.path.exists("l169d/raw_partial.npz"):', 1, "R14a partial exists")
rep('    z = np.load("l169c2/raw_partial.npz")   # own partial (L120 direction)',
    '    z = np.load("l169d/raw_partial.npz")   # own partial (L120 direction)',
    1, "R14b partial load")
rep('    np.savez("l169c2/raw_partial.npz", **store)',
    '    np.savez("l169d/raw_partial.npz", **store)', 1, "R14c partial save")
rep('np.savez_compressed("l169c2/raw_l169c2.npz", K=K,\n'
    '                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],',
    'np.savez_compressed("l169d/raw_l169d.npz", K=K,\n'
    '                    g_cutng25p=GAIN["cutng25p"],\n'
    '                    g_p25gN=GAIN["p25gN"], g_n25gP=GAIN["n25gP"],\n'
    '                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],',
    1, "R15a raw checkpoint")
rep('log("raw_l169c2.npz checkpointed BEFORE analysis")',
    'log("raw_l169d.npz checkpointed BEFORE analysis")', 1, "R15b checkpoint log")

# ---------------- R16: absence scan (B38) + l169c2 added as prior ----------
rep('          "l169b2/raw_l169b2.npz",\n'
    '          "l169b2/raw_partial.npz"]',
    '          "l169b2/raw_l169b2.npz",\n'
    '          "l169b2/raw_partial.npz",\n'
    '          "l169c2/raw_l169c2.npz",\n'
    '          "l169c2/raw_partial.npz"]', 1, "R16a prevs")
rep('    assert not any(f"mm_full_{s}" in _zp.files for s in B37), \\\n'
    '        ("B37 collides with " + _p + " (STOP)")\n'
    'log(f"B37 absence across {len(_prevs)} stored npzs: PASS")',
    '    assert not any(f"mm_full_{s}" in _zp.files for s in B38), \\\n'
    '        ("B38 collides with " + _p + " (STOP)")\n'
    'log(f"B38 absence across {len(_prevs)} stored npzs: PASS")',
    1, "R16b absence B38")

# ---------------- R17: C0A-150 extended to the twin arm ----------------
rep('_arms150 = ("full", "b65", "cutwA", "cutng25")',
    '_arms150 = ("full", "b65", "cutwA", "cutng25", "cutng25p")', 1,
    "R17a arms150")
rep('log(f"C0A-148 (4 arms x {len(C0A150_KEYS)} keys x 2 seeds) vs raw_l135: "',
    'log(f"C0A-148 ({len(_arms150)} arms x {len(C0A150_KEYS)} keys x 2 seeds) '
    'vs raw_l135: "', 1, "R17b arms150 log")

# ---------------- R18: the (d) certification + P-af blocks ----------------
rep('out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],',
    '# ---- FC-169C2 (CERT-1): the 16 inherited arms must be BIT-IDENTICAL\n'
    '# to l169c2/raw_l169c2.npz at 801/901 — adding arms consumes no\n'
    '# generator draws, so any non-zero is a stream break and this run VOID.\n'
    'z169c2 = np.load("l169c2/raw_l169c2.npz")\n'
    '_arms169c2 = ("full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",\n'
    '              "eMotBot5", "wAgN", "n25gW", "f4wA", "f4ng", "f4tw",\n'
    '              "rew1", "rew2", "rew3", "hom")\n'
    'assert all(f"{_k}_{_a}_801" in z169c2.files for _k in C0A150_KEYS\n'
    '           for _a in _arms169c2), "FC-169C2 coverage miss"\n'
    'fc169c2 = {}\n'
    'for s in (801, 901):\n'
    '    for key in C0A150_KEYS:\n'
    '        for a in _arms169c2:\n'
    '            fc169c2[f"{key}_{a}_{s}"] = float(np.abs(\n'
    '                store[f"{key}_{a}_{s}"]\n'
    '                - z169c2[f"{key}_{a}_{s}"][:WIN]).max())\n'
    '    for a in _arms169c2:\n'
    '        fc169c2[f"af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])\n'
    '                                     - float(z169c2[f"af_{a}_{s}"]))\n'
    'fc169c2_max = max(fc169c2.values())\n'
    'fc169c2_pass = bool(all(v == 0.0 for v in fc169c2.values()))\n'
    'log(f"FC-169C2 ({len(_arms169c2)} arms x {len(C0A150_KEYS)} keys x 2 "\n'
    '    f"seeds) vs raw_l169c2: {\'PASS\' if fc169c2_pass else \'FAIL\'} "\n'
    '    f"(max {fc169c2_max:.1e})")\n'
    '# ---- C0-NT(d) (PREREG): a (d) swap arm bit-identical to its own-gain\n'
    '# twin means the gain never entered the step loop -> VOID, read nothing.\n'
    'ntd = {}\n'
    'for _sd, _tw in (("p25gN", "cutng25p"), ("n25gP", "cutng25")):\n'
    '    for s in (801, 901):\n'
    '        ntd[f"{_sd}_vs_{_tw}_{s}"] = float(np.abs(\n'
    '            store[f"mm_{_sd}_{s}"] - store[f"mm_{_tw}_{s}"]).max())\n'
    'ntd_pass = bool(all(v > 0.0 for v in ntd.values()))\n'
    'log(f"C0-NT(d) swap-vs-own-gain mm separation: "\n'
    '    f"{\'PASS\' if ntd_pass else \'VOID\'} (min {min(ntd.values()):.3e})")\n'
    '# ---- P-af(d) (PREREG): DIRECTION only for the swap arms (they are off\n'
    '# the matched point by construction); the own-gain twin gets P-stair.\n'
    'pafd_dir = {s: dict(p25gN_above=bool(d["p25gN_above"]),\n'
    '                    n25gP_below=bool(d["n25gP_below"]))\n'
    '            for s, d in paf.items()}\n'
    'pafd_ok = bool(all(d["p25gN_above"] and d["n25gP_below"]\n'
    '                   for d in pafd_dir.values()))\n'
    'pafd_nup = int(sum(1 for d in pafd_dir.values() if d["p25gN_above"]))\n'
    'pafd_ndn = int(sum(1 for d in pafd_dir.values() if d["n25gP_below"]))\n'
    'log(f"P-af(d) direction (p25gN above / n25gP below AF_T): "\n'
    '    f"{\'PASS\' if pafd_ok else \'PARTIAL\'} ({pafd_nup}/{len(pafd_dir)} "\n'
    '    f"up, {pafd_ndn}/{len(pafd_dir)} down)")\n'
    'pafd = {}\n'
    'for _da2 in ("cutng25p",) + D_SWAP:\n'
    '    _vd = [float(store[f"af_{_da2}_{s}"]) for s in FRESH]\n'
    '    pafd[_da2] = dict(g=GAIN[_da2],\n'
    '                      rollout_af_mean=float(np.mean(_vd)),\n'
    '                      rollout_af_maxoff=float(np.max(np.abs(\n'
    '                          np.array(_vd) - AF_T))))\n'
    '    log(f"P-af {_da2}: g {GAIN[_da2]:.9f} | rollout af mean "\n'
    '        f"{pafd[_da2][\'rollout_af_mean\']:.5f} (max off "\n'
    '        f"{pafd[_da2][\'rollout_af_maxoff\']:.2e})")\n'
    'd_stair = new_stairs["cutng25p"]\n'
    'd_band_ok = bool(d_stair <= 5e-3)\n'
    'log(f"P-stair cutng25p |af-target| {d_stair:.2e} -> "\n'
    '    f"{\'PASS\' if d_band_ok else \'DISCLOSE\'}")\n'
    'out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],',
    1, "R18 d cert blocks")

# ---------------- R19: out dict + json path ----------------
rep('           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass\n'
    '                         and nt_pass and fc169_pass and ntf4_pass\n'
    '                         and fc169b2_pass and ntc2_pass))\n'
    'json.dump(out, open("l169c2/anchors_run.json", "w"), indent=1)',
    '           g_cutng25p=GAIN["cutng25p"],\n'
    '           g_cutng25p_stored_exact=bool(\n'
    '               GAIN["cutng25p"] == G_CUTNG25P_STORED),\n'
    '           g_p25gN=GAIN["p25gN"], g_n25gP=GAIN["n25gP"],\n'
    '           fc169c2_max=fc169c2_max, fc169c2_pass=fc169c2_pass,\n'
    '           ntd=ntd, ntd_pass=ntd_pass, pafd=pafd, pafd_dir=pafd_dir,\n'
    '           pafd_ok=pafd_ok, pafd_nup=pafd_nup, pafd_ndn=pafd_ndn,\n'
    '           d_stair=d_stair, d_band_ok=d_band_ok,\n'
    '           d_n={_a3: N_OF[_a3] for _a3 in ("cutng25p",) + D_SWAP},\n'
    '           d_edges={_a3: int(WB[_a3].values().numel())\n'
    '                    for _a3 in ("cutng25p",) + D_SWAP},\n'
    '           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass\n'
    '                         and nt_pass and fc169_pass and ntf4_pass\n'
    '                         and fc169b2_pass and ntc2_pass\n'
    '                         and fc169c2_pass and ntd_pass))\n'
    'json.dump(out, open("l169d/anchors_run.json", "w"), indent=1)',
    1, "R19 out dict")

# ---------------- apply ----------------
out = src
for old, new, n, tag in reps:
    c = out.count(old)
    assert c == n, f"REP COUNT MISS [{tag}]: found {c}, expected {n}"
    out = out.replace(old, new)
    print(f"  rep ok ({c}x): {tag}")

# ---------------- residual scan (L120 / l126 line-context form) ----------
# Whitelist by LINE CONTEXT: docstring bodies and comments may name the
# prior run for lineage; CODE lines may name it only as an INPUT path
# literal. A log/label string that merely mentions it is not a path.
bad = []
in_doc = False
for i, line in enumerate(out.split("\n"), 1):
    nq = line.count('"""')
    code = line.split("#")[0] if not line.strip().startswith("#") else ""
    if in_doc:
        if nq:
            in_doc = (nq % 2 == 0)
        continue
    if nq % 2 == 1:
        in_doc = True
        continue
    if line.strip().startswith("#") or not code.strip():
        continue
    for lit in re.findall(r'"([^"]*)"', code):
        looks_path = "/" in lit or lit.endswith((".npz", ".json", ".md"))
        if looks_path and "l169c2" in lit:
            if not re.fullmatch(r"l169c2/raw_(l169c2|partial)\.npz", lit):
                bad.append((i, "l169c2 non-input path", line))
        if looks_path and "l169d" in lit and \
                re.fullmatch(r"l169d/.*", lit) is None:
            bad.append((i, "malformed l169d path", line))
    if re.search(r"\bB37\b", code):
        bad.append((i, "B37 survivor", line))
for m in re.finditer(r'np\.savez(?:_compressed)?\("([^"]+)"', out):
    if not m.group(1).startswith("l169d/"):
        bad.append((0, "write outside l169d/", m.group(1)))
for m in re.finditer(r'open\("([^"]+)", "w"\)', out):
    if not m.group(1).startswith("l169d/"):
        bad.append((0, "json write outside l169d/", m.group(1)))
if bad:
    for b in bad:
        print("RESIDUAL:", b)
    sys.exit("RESIDUAL SCAN FAILED")
print("residual scan: CLEAN")

open(DST, "w").write(out)
py_compile.compile(DST, doraise=True)
print(f"wrote {DST} ({len(out.splitlines())} lines) | py_compile OK")
