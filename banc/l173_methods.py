"""L173 stage (a): build the Methods constant/definition table BY PARSING
the run + verdict + static sources, and certify the card's prescribed
update equation against the code's own three lines.

PREREG l173/PREREG.md FIRST (source-of-truth rule S1-S4, CERT-1/2/3,
branches M2_equation_differs > M1_equation_matches, pins P1-P5).
ZERO rollouts, no graph build; the only computation is the 7-node
equation-equivalence probe (fixed seed).
"""
import ast
import json
import os
import re

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
OUT = {}


def src(p):
    return open(p).read()


def consts(path, names):
    """Module-level literal assignments, parsed (S1). Handles tuple targets."""
    tree = ast.parse(src(path))
    got = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        tgts = node.targets[0]
        if isinstance(tgts, ast.Tuple) and isinstance(node.value, ast.Tuple):
            for t, v in zip(tgts.elts, node.value.elts):
                if isinstance(t, ast.Name) and t.id in names:
                    got[t.id] = ast.literal_eval(v)
        elif isinstance(tgts, ast.Name) and tgts.id in names:
            try:
                got[tgts.id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return got


RUN = "l135_run.py"
RUN_NOW = "l169d_run.py"
VER = "l169d_verdict.py"
VER0 = "l135_verdict.py"
STAT = "l131_static.py"

NAMES = ["TAU", "DT", "RMAX", "BG", "NOISE", "SETTLE", "WIN", "SEG",
         "SEGB", "BETA", "D", "ENT_AMP", "AF_T", "G_NEW", "G65"]
c = consts(RUN, NAMES)
assert set(NAMES) <= set(c), sorted(set(NAMES) - set(c))

# ---------------- CERT-1: the current lineage runs the SAME protocol ----
c_now = consts(RUN_NOW, NAMES)
cert1 = {}
for k in NAMES:
    if k in c_now:
        assert c_now[k] == c[k], ("CERT-1 protocol drift", k, c[k], c_now[k])
        cert1[k] = True
assert len(cert1) >= 13, ("CERT-1 too few shared constants", sorted(cert1))
print(f"CERT-1 OK: {len(cert1)} constants identical in {RUN} and {RUN_NOW}")

# ---------------- CERT-2: AF_T + stored-form gains ---------------------
anch135 = json.load(open("l135/anchors_run.json"))
s131 = json.load(open("l131/static.json"))
gain_names = {"G_CUTWA_STORED": "cutwA", "G_CUTNG25_STORED": "cutng25",
              "G_CUTNG25P_STORED": "cutng25p", "G_CUTNG29_STORED": "cutng29"}
gsrc = consts(RUN, list(gain_names))
gains = {gain_names[k]: v for k, v in gsrc.items()}
assert len(gains) == 4, gains
# the run script's own asserts pin these EXACT; re-pin against the stored
# anchors json (the run's own fresh/stored-form bisect record), to 1e-12
for a, g in gains.items():
    st_g = anch135[f"g_{a}"]
    assert abs(st_g - g) <= 1e-12, ("CERT-2", a, g, st_g)
assert abs(c["AF_T"] - 0.10905611018339793) < 1e-15
print(f"CERT-2 OK: AF_T {c['AF_T']:.17g} + 4 stored-form gains equal to "
      f"l135/anchors_run.json within 1e-12")

# ---------------- CERT-3: cohort / mass / ladder definitions -----------
st = src(STAT)
m = re.search(r"K = int\(np\.searchsorted\(cum, ([0-9.]+)\) \+ 1\)", st)
assert m, "K rule not found in l131_static.py"
K_RULE = float(m.group(1))
assert "cum = np.cumsum(cell_mass[order]) / cell_mass.sum()" in st
assert "np.add.at(outmass, src_all[om], np.abs(vals_all[om]))" in st
m2 = re.search(r"assert mass_split == \{\"glut19\": ([0-9.]+), "
               r"\"other58\": ([0-9.]+)\}", st)
assert m2, "mass_split pin not found"
split = {"glut19": float(m2.group(1)), "other58": float(m2.group(2))}
m3 = re.search(r"assert len\(glut_desc\) == (\d+) and len\(ng_desc\) == (\d+)",
               st)
n_glut, n_ng = int(m3.group(1)), int(m3.group(2))
assert s131["mass_split"] == split, (s131["mass_split"], split)
s107 = json.load(open("l107/static.json"))
assert s107["cut"]["K"] == n_glut + n_ng, (s107["cut"]["K"], n_glut, n_ng)
K = s107["cut"]["K"]
assert abs(s107["cut"]["mass_share"] - K_RULE) < 0.01, s107["cut"]
print(f"CERT-3 OK: K rule = first k with cum mass >= {K_RULE} -> K {K} "
      f"= {n_glut} glut + {n_ng} non-glut, mass_split {split}, "
      f"stored share {s107['cut']['mass_share']}")

# ---------------- P1: chop geometry, parsed ----------------------------
rs = src(RUN)
m = re.search(r"while seg0 \+ c \* (\d+) < seg0 \+ SEG:", rs)
CHOP_PERIOD = int(m.group(1))
m = re.search(r"AMPA\[lo:min\(lo \+ (\d+), seg0 \+ SEG\)\] = ENT_AMP", rs)
CHOP_ON = int(m.group(1))
m = re.search(r"AMPA\[(\d+):(\d+)\] = ENT_AMP", rs)
CONT_LO, CONT_HI = int(m.group(1)), int(m.group(2))
assert (CONT_LO, CONT_HI) == (c["SEG"], 2 * c["SEG"])
assert "sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0" in rs
assert "ph += 2 * math.pi * target(i) * DT" in rs
OFF = CHOP_PERIOD - CHOP_ON
print(f"P1 OK: chop {CHOP_ON} on / {OFF} off (period {CHOP_PERIOD}), "
      f"segment [{CONT_LO},{CONT_HI}) continuous, phase-continuous sinusoid")

# ---------------- P2: active fraction + bisect, parsed -----------------
m = re.search(r"return \{a: float\(\(st\[a\] > ([0-9.]+)\)", rs)
AF_THR = float(m.group(1))
m = re.search(r"ANCH = \[11, 22, 33\]", rs)
assert m, "bisect anchor list changed"
BIS_ANCH = [11, 22, 33]
m = re.search(r"lo_g, hi_g = ([0-9.]+), ([0-9.]+)", rs)
BRK = (float(m.group(1)), float(m.group(2)))
m = re.search(r"for it in range\((\d+)\):\n    mid = \(lo_g \+ hi_g\) / 2", rs)
BIS_IT = int(m.group(1))
assert len(re.findall(r"for it in range\(" + str(BIS_IT) + r"\):", rs)) >= 4, \
    "bisect iteration count is not uniform across the bisect loops"
assert "afs.append(float((st[arm] > 0.05).float().mean()))" in rs
print(f"P2 OK: active = x > {AF_THR}, af = mean over anchors {BIS_ANCH} "
      f"after SETTLE, bisect {BIS_IT} iters on {BRK} to AF_T "
      f"{c['AF_T']:.6f}")

# ---------------- P3/P4: class criteria + duty, parsed -----------------
vs = src(VER)
m = re.search(r'return bool\(t\["meanR"\] >= ([0-9.]+) and t\["kR"\] >= (\d+)\)',
              vs)
SUP = (float(m.group(1)), int(m.group(2)))
m = re.search(r'return bool\(([0-9.]+) <= t\["meanR"\] <= ([0-9.]+) and '
              r'(\d+) <= t\["kR"\] <= (\d+)\)', vs)
PAR = (float(m.group(1)), float(m.group(2)), int(m.group(3)), int(m.group(4)))
m = re.search(r'return bool\(t\["kR"\] <= (\d+) and t\["meanR"\] <= ([0-9.]+)\)',
              vs)
NSUP = (int(m.group(1)), float(m.group(2)))
m = re.search(r"np\.nanmean\(SL\[TS\[q07\]\] >= \.(\d+)\)", vs)
DUTY_BAR = float("0." + m.group(1))
m = re.search(r"kL=int\(\(L >= \.(\d+)\)\.sum\(\)\)", vs)
SEED_BAR = float("0." + m.group(1))
m = re.search(r"TS = np\.arange\((\d+), WIN, (\d+)\)", vs)
TS0, TS_STRIDE = int(m.group(1)), int(m.group(2))
m = re.search(r"SL\[t\] = S_of\(tr\[f\"\{ag\}L\"\]\[t - (\d+):t \+ 1\]", vs)
S_WIN = int(m.group(1)) + 1
m = re.search(r"MEAS0 = (\d+)", vs)
MEAS0 = int(m.group(1))
assert "return float(-np.corrcoef(a, b)[0, 1])" in vs
# S2: the same literals in the EARLIEST verdict script of this lineage
v0 = src(VER0)
for lit in (f'>= .{str(SUP[0])[2:]}', f'>= {SUP[1]}',
            f"TS = np.arange({TS0}, WIN, {TS_STRIDE})",
            f"MEAS0 = {MEAS0}"):
    assert lit in v0, ("S2 definition drift vs l135_verdict.py", lit)
print(f"P3/P4 OK: S = -corr over {S_WIN} steps sampled every {TS_STRIDE}; "
      f"duty = fraction of samples with S >= {DUTY_BAR} inside the 0.7-Hz "
      f"windows (first {MEAS0} steps dropped); seed counts at duty >= "
      f"{SEED_BAR}; SUPER {SUP}, PARTIAL {PAR}, NOT-SUPER {NSUP}")

# ---------------- S4: the pooling rule ---------------------------------
s172 = json.load(open("l172/stats.json"))
adm = s172["admissibility"]
POOL = dict(n_admissible=adm["n_admissible"],
            n_rejected=len(adm["rejected"]),
            unit=s172["unit_of_inference"])
print(f"S4 OK: pooling = maximal unique-seed union over "
      f"{POOL['n_admissible']} admissible trace files "
      f"({POOL['n_rejected']} rejected)")

# ---------------- E-TEST: the card's equation vs the code's lines ------
UP = ["drive = torch.sparse.mm(WB[a], st[a]) * gains[a] + I[a]",
      "drive[mech[a], 0] = drive[mech[a], 0] + sin_t"]
for u in UP:
    assert u in rs, ("update line not found verbatim", u[:48])
m = re.search(r"st\[a\] = st\[a\] \+ \(DT / TAU\) \* \(\(torch\.relu\(drive \+ BG\)"
              r" \+ noise\[a\]\)\s*\.clamp\(max=RMAX\) - st\[a\]\)", rs)
assert m, "the x-update line was not found in l135_run.py"
UP.append(re.sub(r"\s*\n\s*", " ", m.group(0)))
code = "\n".join(UP)

torch.manual_seed(1730)
N = 7
Wd = torch.randn(N, N, dtype=torch.float64) * 0.3
W = Wd.to_sparse_csr()
x0 = torch.rand(N, 1, dtype=torch.float64)
nz = torch.randn(N, 1, dtype=torch.float64) * c["NOISE"]
mk = np.array([1, 4])
g = 0.1452
Iv = torch.zeros(N, 1, dtype=torch.float64)
Iv[2] = c["D"]
sin_t = c["ENT_AMP"] * 0.37

scope = dict(torch=torch, WB={"a": W}, st={"a": x0.clone()},
             gains={"a": g}, I={"a": Iv}, mech={"a": mk},
             noise={"a": nz}, sin_t=sin_t, a="a",
             DT=c["DT"], TAU=c["TAU"], BG=c["BG"], RMAX=c["RMAX"])
exec(compile(code, "<l135 update>", "exec"), scope)
x_code = scope["st"]["a"]

# independent implementation of the equation AS WRITTEN FOR METHODS:
# x <- x + (DT/TAU) * ( clamp( relu(g*W x + I + sin*1[mech] + BG) + noise,
#                              max=RMAX ) - x )
u = g * (W @ x0) + Iv
u[mk, 0] = u[mk, 0] + sin_t
x_me = x0 + (c["DT"] / c["TAU"]) * (
    (torch.relu(u + c["BG"]) + nz).clamp(max=c["RMAX"]) - x0)
dmax = float((x_code - x_me).abs().max())
BRANCH = "M1_equation_matches" if dmax == 0.0 else "M2_equation_differs"
assert dmax == 0.0, ("M2: the card's equation is NOT the code's", dmax)
print(f"E-TEST OK: max|d| {dmax:.1e} -> branch {BRANCH} "
      f"(noise enters AFTER relu and INSIDE the clamp; clamp has NO lower "
      f"bound, so x can sit slightly below 0 on a negative noise draw)")

EQ = ("x <- x + (DT/TAU) * ( clamp( relu(g*W x + I + s(t)*1_mech + BG) "
      "+ noise, max=RMAX ) - x )")

OUT["model"] = dict(
    TAU=c["TAU"], DT=c["DT"], RMAX=c["RMAX"], BG=c["BG"], NOISE=c["NOISE"],
    SETTLE=c["SETTLE"], WIN=c["WIN"], SEG=c["SEG"], BETA=c["BETA"],
    D=c["D"], ENT_AMP=c["ENT_AMP"], AF_T=round(c["AF_T"], 6),
    af_threshold=AF_THR, equation=EQ, branch=BRANCH, eq_maxd=dmax,
    cert1_shared=len(cert1))
OUT["protocol"] = dict(
    segb=[[int(a), int(b), f] for a, b, f in c["SEGB"]],
    chop_on=CHOP_ON, chop_off=OFF, chop_period=CHOP_PERIOD,
    continuous_seg=[CONT_LO, CONT_HI],
    bisect_anchors=BIS_ANCH, bisect_bracket=list(BRK), bisect_iters=BIS_IT,
    win_s=c["WIN"] * c["DT"], dng100_drive=c["D"])
OUT["defs"] = dict(
    K=K, K_mass_rule=K_RULE, mass_share=s107["cut"]["mass_share"],
    n_glut=n_glut, n_nonglut=n_ng, mass_split=split,
    duty_bar=DUTY_BAR, seed_bar=SEED_BAR, s_window=S_WIN,
    sample_stride=TS_STRIDE, meas0=MEAS0,
    super_meanR=SUP[0], super_k=SUP[1],
    partial_lo=PAR[0], partial_hi=PAR[1],
    partial_k_lo=PAR[2], partial_k_hi=PAR[3],
    notsuper_k=NSUP[0], notsuper_meanR=NSUP[1],
    pool_admissible=POOL["n_admissible"], pool_rejected=POOL["n_rejected"],
    unit=POOL["unit"])
OUT["gains_stored_form"] = {k: v for k, v in sorted(gains.items())}
OUT["sources"] = dict(run=RUN, run_now=RUN_NOW, verdict=VER,
                      verdict_first=VER0, static=STAT,
                      pooling="l172/stats.json")

os.makedirs("l173", exist_ok=True)
json.dump(OUT, open("l173/methods.json", "w"), indent=1, sort_keys=True)
print("\nwrote l173/methods.json")
print(json.dumps(OUT, indent=1, sort_keys=True)[:1400])
