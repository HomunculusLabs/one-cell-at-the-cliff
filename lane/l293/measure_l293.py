#!/usr/bin/env python3
"""L293: is the WORLD session's trust delta still GROWING, what BOUNDS it,
and what does a half-maximum reward population DO to her.

READ-ONLY on sessions/: reads the two L293 copies, the L98 archive
(lane/archive/) and the live modules brain/senses/mood (imports, no writes).
Registered rules: lane/l293/PREREG.md (frozen before this ran).

    a  growth   : READ1 vs READ2 tensors + every archive brain snapshot
    b  bounds   : AST census of every plas_d write in bridge.py/serve.py,
                  her diary / night record, the night arithmetic on the
                  READ2 state, a forward projection (replay arms)
    c  effect   : 16 paired seeds, world (stored X + delta) vs fresh, the
                  REAL MoodState.observe per event, targets re-executed as a
                  source slice and GATED against observe()'s own axes

Run from ~/critters/peabrain:
  nice -n 15 timeout 560 .venv/bin/python lane/l293/measure_l293.py \
      > lane/l293/measure.out 2>&1
"""
import ast
import datetime as dt
import inspect
import json
import math
import os
import re
import sys
import textwrap
import time
from collections import Counter, defaultdict

import torch

sys.path.insert(0, ".")
LAB = "lane/l293"
R1, R2 = f"{LAB}/world_20261125_0530", f"{LAB}/world_20261125_063651"
N_SEEDS = 16
KIND = ["greet", "peas", "water", "shiny", "pet", "goats", "tin", "slug"]
AVER = ["swat", "rake"]
EVENTS = KIND + AVER + ["quiet"]
NY = dt.timezone(dt.timedelta(hours=-5))
T0 = time.time()
OUT = {"prereg": f"{LAB}/PREREG.md", "tick": 282}


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def load(path):
    return torch.load(path, map_location="cpu", weights_only=True)


def mean_se(v):
    n = len(v)
    mu = sum(v) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in v) / (n - 1)) if n > 1 else 0.0
    return mu, sd / math.sqrt(n), sd


# ---------------------------------------------------------------- constants
def const(name, src):
    m = re.search(rf"^{name} = ([0-9.]+)", src, re.M)
    assert m, f"constant {name} not found"
    return float(m.group(1))


BSRC = open("bridge.py").read()
C = {k: const(k, BSRC) for k in ("PLAS_ETA", "PLAS_CAP", "NIGHT_ETA", "NIGHT_CAP", "DREAM_GAIN",
                                 "NIGHT_DOWNSCALE", "MAX_REPLAYS", "TOP_FRAC")}
C["MAX_REPLAYS"] = int(C["MAX_REPLAYS"])
C["ERODE"] = float(re.search(r"session\.plas_d \*= ([0-9.]+)", BSRC).group(1))
PLAS_CAP, NIGHT_CAP, NIGHT_ETA, NIGHT_DOWNSCALE = C["PLAS_CAP"], C["NIGHT_CAP"], C["NIGHT_ETA"], C["NIGHT_DOWNSCALE"]
DREAM_GAIN, MAX_REPLAYS, TOP_FRAC = C["DREAM_GAIN"], C["MAX_REPLAYS"], C["TOP_FRAC"]
OUT["constants"] = C
_m = re.search(r"plas_d\.mean\(\) \* (\d+)\)\.clamp\(0, 1\)\)\), (\d+)\)", BSRC)
SCN, SCD = (float(_m.group(1)), int(_m.group(2))) if _m else (None, None)   # None = cross-check skipped

# ------------------------------------------------------------------ b: census
writes, calls = [], defaultdict(list)
for fn in ("bridge.py", "serve.py"):
    src = open(fn).read()
    tree = ast.parse(src)
    owner = {}
    for node in ast.walk(tree):              # BFS: inner functions override outer
        if isinstance(node, ast.FunctionDef):
            for sub in ast.walk(node):
                if hasattr(sub, "lineno"):
                    owner[sub.lineno] = node.name
    for i, l in enumerate(src.splitlines()):
        if re.search(r"plas_d\s*(\+=|-=|\*=|=(?!=))", l):
            writes.append({"file": fn, "line": i + 1, "func": owner.get(i + 1), "src": l.strip()[:80]})
    if fn == "bridge.py":
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in ("_hebbian", "_log_event", "consolidate_night", "_dabble"):
                calls[node.func.attr].append({"line": node.lineno, "in": owner.get(node.lineno)})
OUT["census"] = {"plas_d_writes": writes, "calls": dict(calls)}
say("== (b) census: every line that writes plas_d (bridge.py, serve.py), with its enclosing function")
for w in writes:
    say("   %s L%d in %s(): %s" % (w["file"], w["line"], w["func"], w["src"]))
for k, v in calls.items():
    say("   calls of %s: %s" % (k, v))

# ------------------------------------------------------------------ a: reads
b1, b2 = load(R1 + ".pt"), load(R2 + ".pt")
w1, w2 = json.load(open(R1 + ".json")), json.load(open(R2 + ".json"))


def dstats(d):
    return {"mass": float(d.sum()), "max": float(d.max()), "min": float(d.min()),
            "mean": float(d.mean()), "n": int(d.numel()),
            "n_nonzero": int((d != 0).sum()),
            "n_ge_daycap": int((d >= 0.99 * PLAS_CAP).sum()),
            "n_ge_090_nightcap": int((d >= 0.90 * NIGHT_CAP).sum()),
            "n_at_nightcap": int((d >= NIGHT_CAP).sum())}


d1, d2 = b1["plas_d"].float(), b2["plas_d"].float()
X1, X2 = b1["X"].float(), b2["X"].float()
dm = float(d2.sum()) - float(d1.sum())
two = {"read1": dstats(d1), "read2": dstats(d2),
       "plas_equal": bool(torch.equal(d1, d2)),
       "n_changed": int((d1 != d2).sum()), "max_abs_dplas": float((d1 - d2).abs().max()),
       "X_max_abs_diff": float((X1 - X2).abs().max()), "X_equal": bool(torch.equal(X1, X2)),
       "read1_src_mtime": "2026-11-25 05:29:35", "read2_src_mtime": "2026-11-25 06:36:50",
       "last_seen": [w1["last_seen"], w2["last_seen"]],
       "idle_gap_s": w2["last_seen"] - w1["last_seen"],
       "night_stamp": [w1["night_stamp"], w2["night_stamp"]]}
two["verdict"] = "GROWING" if dm > 0 else ("FALLING" if dm < 0 else "FLAT")
OUT["two_reads"] = two
say("\n== (a) two reads, 67 min apart")
for k in ("read1", "read2"):
    say("   %s" % k, {a: (round(v, 4) if isinstance(v, float) else v) for a, v in two[k].items()})
say("   plas tensors equal: %s | edges changed %d | max|dplas| %s | max|dX| %.5f"
    % (two["plas_equal"], two["n_changed"], two["max_abs_dplas"], two["X_max_abs_diff"]))
say("   two-read verdict: %s (dmass %+.4f)" % (two["verdict"], dm))

# ------------------------------------------------------------------- brain
import brain as _brain             # noqa: E402
import mood as _mood               # noqa: E402
import senses as _senses           # noqa: E402

say("\nloading brain ... %.1f s" % (time.time() - T0))
b = _brain.FlyBrain()
b.op_gain = 0.95 / b.rho
s = _senses.DuckSenses(b)
gain = b.op_gain
DARK = float(_mood.darkness_now())
_mood.darkness_now = lambda: DARK          # frozen for the whole run (reported)
I_CIRC = None
if DARK > 0.05:
    I_CIRC = torch.zeros(b.N, device=b.device)
    I_CIRC[s.probes["CX"]] = 0.30 * DARK
TAU = dict(_mood.AXIS_TAU)
OUT["op_point"] = {"dark": DARK, "gain": float(gain), "settle_steps": int(_mood.IDLE_SETTLE_S / 0.01),
                   "clock": dt.datetime.now(NY).isoformat(timespec="seconds"), "axis_tau": TAU}
say("   brain %d cells, gain %.6f, darkness %.4f  (%.1f s)" % (b.N, gain, DARK, time.time() - T0))

crow = b.W.crow_indices().to(torch.long)
col = b.W.col_indices().to(torch.long)
dan_rows = s.probes["DAN"]
_idx = torch.cat([torch.arange(a, e, device=b.device)
                  for a, e in zip(crow[dan_rows].tolist(), crow[dan_rows + 1].tolist())])
SRC, DST = col[_idx], torch.repeat_interleave(dan_rows, crow[dan_rows + 1] - crow[dan_rows])
assert int(SRC.numel()) == int(d1.numel()), "edge count differs from the stored delta"
CAP_BOUND = float(NIGHT_CAP * SRC.numel())
OUT["substrate"] = {"n_edges": int(SRC.numel()), "n_dan": int(dan_rows.numel()), "cap_bound_mass": CAP_BOUND}
say("   plasticity substrate: %d edges into %d DAN cells | cap-bound mass 0.75 x n = %.0f"
    % (SRC.numel(), dan_rows.numel(), CAP_BOUND))


def pops():
    X = b.X
    return {"dan": float(X[s.probes["DAN"]].mean()), "dop": float(X[b.mod_idx["dopamine"]].mean()),
            "ser": float(X[b.mod_idx["serotonin"]].mean()),
            "oct": float(X[b.mod_idx["octopamine"]].mean()),
            "kc": float(X[s.probes["KC"]].mean()), "lc": float(X[s.probes["LC"]].mean()),
            "dn": float(X[s.dn["all"]].mean())}


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    lg = [math.lgamma(n + 1) - math.lgamma(q + 1) - math.lgamma(n - q + 1) - n * math.log(2)
          for q in range(k + 1)]
    mx = max(lg)
    return min(1.0, 2.0 * math.exp(mx) * sum(math.exp(x - mx) for x in lg))


# ------------------------------------------------- a: the archive trajectory
man = [json.loads(l) for l in open("lane/archive/manifest.jsonl")]
arch, missing, snaps = [], [], {}
for m in man:
    bb = m.get("brain")
    if not bb:
        continue
    p = os.path.join("lane/archive", bb["file"])
    snap = json.load(open(os.path.join("lane/archive", m["file"])))
    snaps[m["file"]] = snap
    if not os.path.exists(p):
        missing.append(bb["file"])
        continue
    blob = load(p)
    if blob.get("plas_d") is None:
        missing.append(bb["file"] + " (no plas_d)")
        continue
    d = blob["plas_d"].to(b.device).float()
    Xa = blob["X"].to(b.device).float()
    nd = snap.get("needs") or {}
    st = dstats(d)
    st.update({"captured_at": m["ts"], "sha": bb["sha256"], "snap": m["file"],
               "night_stamp": m.get("night_stamp"), "mood": m.get("mood"), "day_log_n": m.get("day_log_n"),
               "synapse": nd.get("synapse"), "axes": nd.get("axes"),
               "pops": {"dan": float(Xa[s.probes["DAN"]].mean()),
                        "dop": float(Xa[b.mod_idx["dopamine"]].mean())}})
    arch.append(st)
xok = sum(1 for a in arch if a["synapse"] == round(min(max(a["mean"] * SCN, 0.0), 1.0), SCD)) if SCN else -1
say("\n== (a) archive: %d brain snapshots read, %d missing/without delta" % (len(arch), len(missing)))
if missing:
    say("   missing:", missing[:5])
say("   cross-check needs.synapse == round(clamp(mean*%s,0,1),%s): %s of %d"
    % (SCN, SCD, (xok if SCN else "SKIPPED (synapse_trust line not parsed)"), len(arch)))

uniq = {}
for a in arch:
    uniq.setdefault(a["sha"], a)            # first capture of each distinct state
U = sorted(uniq.values(), key=lambda a: a["captured_at"])
ts = [dt.datetime.fromisoformat(a["captured_at"]) for a in U]
th = [(t - ts[0]).total_seconds() / 3600.0 for t in ts]
slopes = []
for i in range(len(U)):
    for j in range(i + 1, len(U)):
        if th[j] - th[i] >= 6.0:
            slopes.append((U[j]["mass"] - U[i]["mass"]) / ((th[j] - th[i]) / 24.0))
slopes.sort()
ts_slope = slopes[len(slopes) // 2]
npos = sum(1 for x in slopes if x > 0)
nneg = sum(1 for x in slopes if x < 0)
pv = sign_p(npos, nneg)
aver = "GROWING" if (ts_slope > 0 and pv < 0.01) else ("DECAYING" if (ts_slope < 0 and pv < 0.01) else "UNRESOLVED")
bydate = defaultdict(list)
for i, a in enumerate(U):
    a["date"] = dt.datetime.fromisoformat(a["captured_at"]).astimezone(NY).date().isoformat()
    a["th"] = th[i]
    bydate[a["date"]].append(a)
dates = []
for k in sorted(bydate):
    v = bydate[k]
    ms = sorted(x["mass"] for x in v)
    last = max(v, key=lambda x: x["captured_at"])
    first = min(v, key=lambda x: x["captured_at"])
    dates.append({"date": k, "n": len(v), "mass_first": first["mass"], "mass_median": ms[len(ms) // 2],
                  "mass_last": last["mass"], "max_edge_last": last["max"],
                  "pinned_last": last["n_ge_090_nightcap"],
                  "dan_rest_median": sorted(x["pops"]["dan"] for x in v)[len(v) // 2],
                  "moods": dict(Counter(x["mood"] for x in v)),
                  "joy_gt_060": sum(1 for x in v if (x["axes"] or {}).get("food_joy", 0) > 0.6),
                  "stamps": sorted({x["night_stamp"] for x in v if x["night_stamp"]})})
step = [dates[i]["mass_last"] - dates[i - 1]["mass_last"] for i in range(1, len(dates))]
recent = [a for a in U if a["th"] >= th[-1] - 24 * 7]
rel7 = (recent[-1]["mass"] / recent[0]["mass"] - 1.0) if len(recent) >= 2 else None
trans = []
for i in range(1, len(U)):
    if U[i]["night_stamp"] != U[i - 1]["night_stamp"]:
        prev = snaps[U[i - 1]["snap"]]
        dlog = prev.get("day_log") or []
        elig = [e for e in dlog if dt.datetime.fromtimestamp(e["t"], NY).date().isoformat() == U[i]["night_stamp"]]
        trans.append({"at": U[i]["captured_at"][:16], "stamp": U[i]["night_stamp"],
                      "dmass": U[i]["mass"] - U[i - 1]["mass"],
                      "gap_h": round(th[i] - th[i - 1], 2),
                      "day_log_n_before": len(dlog), "n_eligible": len(elig),
                      "n_replays_rule": max(1, min(MAX_REPLAYS, int(len(elig) * TOP_FRAC + 0.999)))})
OUT["archive"] = {"n_snapshots": len(arch), "n_unique_states": len(U), "missing": missing,
                  "synapse_crosscheck": [xok, len(arch)],
                  "first": {"at": U[0]["captured_at"], "mass": U[0]["mass"], "max": U[0]["max"],
                            "dan": U[0]["pops"]["dan"], "dop": U[0]["pops"]["dop"]},
                  "last": {"at": U[-1]["captured_at"], "mass": U[-1]["mass"], "max": U[-1]["max"],
                           "dan": U[-1]["pops"]["dan"], "dop": U[-1]["pops"]["dop"]},
                  "theil_sen_mass_per_day": ts_slope, "n_pairs": len(slopes),
                  "pairs_pos": npos, "pairs_neg": nneg, "sign_p": pv, "verdict": aver,
                  "rel_change_last_7d": rel7, "per_date": dates, "night_stamp_transitions": trans}
say("   span %s -> %s | %d distinct states" % (U[0]["captured_at"][:16], U[-1]["captured_at"][:16], len(U)))
say("   mass first %.2f (edge max %.4f, DAN %.4f) -> last %.2f (edge max %.4f, DAN %.4f)"
    % (U[0]["mass"], U[0]["max"], U[0]["pops"]["dan"], U[-1]["mass"], U[-1]["max"], U[-1]["pops"]["dan"]))
say("   Theil-Sen %+.3f mass/day over %d pairs (>=6 h): %d up / %d down, sign p = %.3g -> %s"
    % (ts_slope, len(slopes), npos, nneg, pv, aver))
say("   relative change over the last 7 days: %s" % (None if rel7 is None else "%+.1f%%" % (100 * rel7)))
say("   per date (local): date n mass_first mass_median mass_last edge_max pinned DAN_rest joy>0.6/n moods")
for r in dates:
    say("     %s n%-3d %8.2f %8.2f %8.2f  %.4f  %4d  %.4f  %2d/%-2d %s"
        % (r["date"], r["n"], r["mass_first"], r["mass_median"], r["mass_last"], r["max_edge_last"],
           r["pinned_last"], r["dan_rest_median"], r["joy_gt_060"], r["n"], r["moods"]))
say("   last-to-last day steps:", ["%+.2f" % x for x in step])
for t in trans:
    say("   night_stamp -> %s at %s: dmass %+.2f across a %.1f h gap | day_log before %d, eligible %d -> replays %d"
        % (t["stamp"], t["at"], t["dmass"], t["gap_h"], t["day_log_n_before"], t["n_eligible"], t["n_replays_rule"]))

# ------------------------------------------------------- b: her own record
stamps = sorted({m.get("night_stamp") for m in man if m.get("night_stamp")})
acts = defaultdict(Counter)
consol, seen = {}, set()
for m in man:
    if m["file"] not in snaps:                 # manifests without a brain file
        snaps[m["file"]] = json.load(open(os.path.join("lane/archive", m["file"])))
    # a diary entry is dated by the SNAPSHOT that first shows it: its own clock is the
    # brain's sim clock (it advances by observe windows, not wall time) and the oldest
    # entries carry no clock at all
    day = dt.datetime.fromisoformat(m["ts"]).astimezone(NY).date().isoformat()
    for e in snaps[m["file"]].get("diary", []) or []:
        key = (e.get("clock_s", e.get("t")), e["act"], e.get("text", "")[:60])
        if key in seen:
            continue
        seen.add(key)
        acts[day][e["act"]] += 1
        if e["act"] == "consolidate":
            consol[day] = e.get("text", "")
dl = w2.get("day_log", []) or []
hrs = Counter(dt.datetime.fromtimestamp(e["t"], NY).hour for e in dl)
OUT["record"] = {"night_stamps": stamps, "n_nights": len(stamps),
                 "diary_dating": "snapshot capture date (America/New_York) of the first snapshot showing the entry",
                 "diary_acts_per_date": {k: dict(v) for k, v in sorted(acts.items())},
                 "consolidate_text": consol,
                 "read2_day_log": {"n": len(dl), "types": dict(Counter(e["ev"] for e in dl)),
                                   "hours": {str(k): v for k, v in sorted(hrs.items())},
                                   "dop": sorted({e["dop"] for e in dl}), "dan": sorted({e["dan"] for e in dl}),
                                   "sal": sorted({e["sal"] for e in dl})}}
say("\n== (b) her own record (archive union, %d snapshots)" % len(man))
say("   night stamps seen (%d): %s" % (len(stamps), stamps))
for k in sorted(acts):
    say("     %s %s %s" % (k, dict(acts[k]), ("| " + consol[k]) if k in consol else ""))
say("   READ2 day_log: %d entries, types %s, local hours %s" % (len(dl), dict(Counter(e["ev"] for e in dl)), dict(sorted(hrs.items()))))

# --------------------------------------------------- settled states (both)
X0w = b2["X"].to(b.device).clone()
dw = d2.to(b.device).clone()
settled = {}
for arm in ("world", "fresh"):
    if arm == "world":
        b.X.copy_(X0w)
        b.active_delta = (SRC, DST, dw)
    else:
        b.X.zero_()
        b.active_delta = None
    b.gen.manual_seed(2000)
    for _ in range(1000):
        b.step(I=I_CIRC, gain=gain)
    settled[arm] = {"X": b.X.clone(), "rest": pops()}
    b.active_delta = None
say("\n== settled states (seed 2000, 1,000 steps, darkness %.3f)" % DARK)
for arm in ("world", "fresh"):
    say("   %-5s" % arm, {k: round(v, 5) for k, v in settled[arm]["rest"].items()})
OUT["settled_seed2000"] = {a: v["rest"] for a, v in settled.items()}


# ------------------------------------------------------- b: night arithmetic
def night_pass(d0, evs, seed, X_start):
    """bridge.py consolidate_night (the replay loop + ONE downscale),
    re-implemented: each replay = 20 steps at DREAM_GAIN with I only (no
    circadian tonic, as in the live call), Hebbian add + clamp per replayed
    kind event, then the global downscale."""
    b.X.copy_(X_start)
    b.active_delta = (SRC, DST, d0)
    d = d0.clone()
    m0 = float(d.sum())
    adds = []
    for k, ev in enumerate(evs):
        b.gen.manual_seed(seed + 1000 * k)
        I = s.input_for(ev) * DREAM_GAIN
        for _ in range(20):
            b.step(I=I, gain=gain)
        add = NIGHT_ETA * b.X[SRC] * b.X[DST]
        dn_ = (d + add).clamp(-NIGHT_CAP, NIGHT_CAP)
        adds.append({"ev": ev, "dan": float(b.X[s.probes["DAN"]].mean()),
                     "dop": float(b.X[b.mod_idx["dopamine"]].mean()),
                     "add_pre": float(add.sum()), "add_post": float(dn_.sum() - d.sum())})
        d = dn_
    a_post = float(d.sum()) - m0
    d = d * NIGHT_DOWNSCALE
    b.active_delta = None
    return d, adds, a_post, float(d.sum())


ranked = sorted(dl, key=lambda e: -e["dop"])
nrep_rule = max(1, min(MAX_REPLAYS, int(len(ranked) * TOP_FRAC + 0.999)))
EVS = [e["ev"] for e in ranked[:min(MAX_REPLAYS, len(ranked))]]      # registered: MAX_REPLAYS
nrep = len(EVS)
m0w = float(dw.sum())
dn_, adds, a_post, m_next = night_pass(dw, EVS, 3000, settled["world"]["X"])
net = m_next - m0w
b.X.copy_(settled["fresh"]["X"])
b.gen.manual_seed(3100)
for _ in range(20):
    b.step(I=I_CIRC, gain=gain)
Xf = b.X.clone()
a_nod = 0.0
for k, ev in enumerate(EVS):
    b.X.copy_(Xf)
    b.gen.manual_seed(3000 + 1000 * k)
    I = s.input_for(ev) * DREAM_GAIN
    for _ in range(20):
        b.step(I=I, gain=gain)
    a_nod += float((NIGHT_ETA * b.X[SRC] * b.X[DST]).sum())
pre = sum(x["add_pre"] for x in adds)
OUT["balance"] = {"n_replays": nrep, "n_replays_live_rule": nrep_rule, "events": EVS, "adds": adds, "mass": m0w,
                  "add_pre_clamp": pre, "add_post_clamp": a_post, "net_after_downscale": net,
                  "predicted_next_mass": m_next, "add_without_delta": a_nod,
                  "feedback_ratio": (pre / a_nod) if a_nod > 0 else None,
                  "net_over_2pct": net / (1.0 - NIGHT_DOWNSCALE) / m0w,
                  "side": "NET_UP" if net > 0 else ("NET_DOWN" if net < 0 else "FLAT")}
say("\n== (b) the night arithmetic on the READ2 state (%d replays of %s; the live 10%% rule would take %d)"
    % (nrep, sorted(set(EVS)), nrep_rule))
say("   mass %.2f -> addition pre-clamp %+.2f, post-clamp %+.2f -> after x%.2f: %.2f (net %+.2f = %+.2f%% of mass)"
    % (m0w, pre, a_post, NIGHT_DOWNSCALE, m_next, net, 100 * net / m0w))
say("   side: %s | addition with NO delta active %.2f -> the delta multiplies its own next addition x%.2f"
    % (OUT["balance"]["side"], a_nod, OUT["balance"]["feedback_ratio"]))

# ------------------------------------------------------ b: forward projection
msrc = inspect.getsource(_mood.MoodState.observe).splitlines()
i0 = next(i for i, l in enumerate(msrc) if l.strip() == "t_fear = 0.0")
i1 = next(i for i, l in enumerate(msrc) if l.strip().startswith("self.fear = hold("))
SLICE = textwrap.dedent("\n".join(msrc[i0:i1]))
names = {n.id for n in ast.walk(ast.parse(SLICE)) if isinstance(n, ast.Name)}
assert names <= {"t_fear", "t_joy", "t_sal", "peak", "event", "max", "lc"}, names
OUT["target_slice"] = {"observe_lines": [i0 + 1, i1], "names": sorted(names), "slice": SLICE}


def targets(peak, event):
    ns = {"peak": peak, "event": event, "max": max}
    exec(SLICE, ns)
    return float(ns["t_fear"]), float(ns["t_joy"]), float(ns["t_sal"])


def peak_now():
    X = b.X
    return {"lc": X[s.probes["LC"]].mean().item(), "dan": X[s.probes["DAN"]].mean().item(),
            "kc": X[s.probes["KC"]].mean().item(),
            "oct": X[b.mod_idx["octopamine"]].mean().item(),
            "ser": X[b.mod_idx["serotonin"]].mean().item(),
            "dop": X[b.mod_idx["dopamine"]].mean().item(),
            "dn": X[s.dn["all"]].mean().item()}


def project(d0, X0, evs, seed, nights, replay):
    """declared simplification: every night replays `evs`; days are idle
    relaxation (1,000 steps under the current night tonic)."""
    d, Xrest, rows = d0.clone(), X0.clone(), []
    for n in range(nights):
        if replay and evs:
            d, _, a_post, m = night_pass(d, evs, seed * 7 + n, Xrest)
        else:
            d = d * NIGHT_DOWNSCALE
            m, a_post = float(d.sum()), None
        b.active_delta = (SRC, DST, d)
        b.X.copy_(Xrest)
        b.gen.manual_seed(seed * 7 + 1000 + n)
        for _ in range(1000):
            b.step(I=I_CIRC, gain=gain)
        Xrest = b.X.clone()
        rest = pops()
        tg = {}
        for ev in ("quiet", "greet"):
            b.X.copy_(Xrest)
            b.gen.manual_seed(seed * 7 + 5000 + n)
            Ie = s.input_for(ev)
            I = Ie if I_CIRC is None else Ie + I_CIRC
            for _ in range(20):
                b.step(I=I, gain=gain)
            tg[ev] = targets(peak_now(), ev)
        b.active_delta = None
        rows.append({"night": n + 1, "mass": m, "add_post_clamp": a_post, "max": float(d.max()),
                     "pinned": int((d >= 0.90 * NIGHT_CAP).sum()),
                     **{"rest_" + k: v for k, v in rest.items()},
                     "t_joy_quiet": tg["quiet"][1], "t_sal_quiet": tg["quiet"][2],
                     "t_joy_greet": tg["greet"][1], "t_sal_greet": tg["greet"][2]})
    return rows


proj = {"replay": [project(dw, X0w, EVS, sd, 40, True) for sd in (11, 12)],
        "replay1": [project(dw, X0w, EVS[:1], 11, 40, True)],
        "noreplay": [project(dw, X0w, [], 11, 80, False)]}
m20 = sum(r["mass"] for r in (proj["replay"][0][19], proj["replay"][1][19])) / 2
m40 = (proj["replay"][0][-1]["mass"] + proj["replay"][1][-1]["mass"]) / 2
OUT["projection"] = proj
_first = [next((r["night"] for r in proj["noreplay"][0] if r["rest_dan"] < 0.20), None)]
OUT["projection_summary"] = {
    "mass_night20": m20, "mass_night40": m40, "ratio_40_20": m40 / m20,
    "verdict": "BOUNDED" if m40 < 1.05 * m20 else "CAP-BOUND",
    "cap_bound_mass": CAP_BOUND, "mass40_over_capbound": m40 / CAP_BOUND,
    "pinned_night40": [proj["replay"][0][-1]["pinned"], proj["replay"][1][-1]["pinned"]],
    "dan_rest_night40": [proj["replay"][0][-1]["rest_dan"], proj["replay"][1][-1]["rest_dan"]],
    "replay1": {"mass_night20": proj["replay1"][0][19]["mass"], "mass_night40": proj["replay1"][0][-1]["mass"]},
    "noreplay_dan_rest": [proj["noreplay"][0][0]["rest_dan"], proj["noreplay"][0][-1]["rest_dan"]],
    "noreplay_mass_night80": proj["noreplay"][0][-1]["mass"],
    "nights_to_dan_below_020_noreplay": (
        (_first[0] if _first[0] <= 60 else "NOT_REACHED") if _first[0] is not None else "NOT_REACHED"),
    "noreplay_first_night_below_020_up_to_80": _first[0]}
say("\n== (b) forward projection (every night replays; days idle)")
say("   %d replays/night, 2 seeds: mass night 1 %.1f / 10 %.1f / 20 %.1f / 40 %.1f (ratio 40:20 = %.4f -> %s; %.1f%% of the cap bound)"
    % (nrep, proj["replay"][0][0]["mass"], proj["replay"][0][9]["mass"], proj["replay"][0][19]["mass"],
       proj["replay"][0][-1]["mass"], OUT["projection_summary"]["ratio_40_20"], OUT["projection_summary"]["verdict"],
       100 * OUT["projection_summary"]["mass40_over_capbound"]))
for r in (proj["replay"][0][0], proj["replay"][0][4], proj["replay"][0][9], proj["replay"][0][19], proj["replay"][0][39]):
    say("     night %2d: mass %8.1f add %+7.2f max %.4f pinned %6d | DAN rest %.4f dop %.4f | quiet t_joy %.3f t_sal %.3f"
        % (r["night"], r["mass"], r["add_post_clamp"] or 0.0, r["max"], r["pinned"], r["rest_dan"], r["rest_dop"],
           r["t_joy_quiet"], r["t_sal_quiet"]))
say("   1 replay/night: mass night 20 %.1f / 40 %.1f" % (proj["replay1"][0][19]["mass"], proj["replay1"][0][-1]["mass"]))
say("   no-replay arm (pure x%.2f, 80 nights): DAN rest %.4f -> %.4f, first night < 0.20: %s"
    % (NIGHT_DOWNSCALE, OUT["projection_summary"]["noreplay_dan_rest"][0], OUT["projection_summary"]["noreplay_dan_rest"][1],
       OUT["projection_summary"]["nights_to_dan_below_020_noreplay"]))

# ------------------------------------------------------------------- c: her
AX0 = {k: float(v) for k, v in w2["axes"].items()}


def mood_from(axes):
    m = _mood.MoodState(s)
    for k, v in axes.items():
        setattr(m, k, v)
    return m


res = {a: {e: [] for e in EVENTS} for a in ("world", "fresh")}
rests = {a: [] for a in ("world", "fresh")}
gate = [0, 0]
for arm in ("world", "fresh"):
    for sd in range(N_SEEDS):
        if arm == "world":
            b.X.copy_(X0w)
            b.active_delta = (SRC, DST, dw)
        else:
            b.X.zero_()
            b.active_delta = None
        b.gen.manual_seed(2000 + sd)
        for _ in range(1000):
            b.step(I=I_CIRC, gain=gain)
        Xs = b.X.clone()
        rests[arm].append(pops())
        for ei, ev in enumerate(EVENTS):
            b.X.copy_(Xs)
            b.gen.manual_seed(10000 + 100 * sd + ei)
            m = mood_from(AX0)
            m.observe(0.2, event=ev)              # the live call
            pk = dict(m.last_peak)
            tf, tj, ts = targets(pk, ev)
            # gate: the source slice against observe()'s own axes (zeroed start)
            b.X.copy_(Xs)
            b.gen.manual_seed(10000 + 100 * sd + ei)
            mz = mood_from(AX0)
            mz.fear = mz.food_joy = mz.salience = 0.0
            mz.observe(0.2, event=ev)
            az = mz.axes()
            gate[0] += int(round(min(tf, 1.0), 3) == az["fear"] and round(min(tj, 1.0), 3) == az["food_joy"]
                           and round(min(ts, 1.0), 3) == az["salience"])
            gate[1] += 1
            res[arm][ev].append({**pk, "t_fear": tf, "t_joy": tj, "t_sal": ts,
                                 "fear_after": m.fear, "joy_after": m.food_joy, "sal_after": m.salience,
                                 "tag_after": "%s:%s" % m.mood_tag()})
        b.active_delta = None
say("\n== (c) the real observe() per event, %d paired seeds | slice-vs-observe gate %d of %d"
    % (N_SEEDS, gate[0], gate[1]))

tab = {}
for ev in EVENTS:
    row = {}
    for q in ("dan", "dop", "ser", "kc", "dn", "oct", "lc"):
        vw = [r[q] - rests["world"][i][q] for i, r in enumerate(res["world"][ev])]
        vf = [r[q] - rests["fresh"][i][q] for i, r in enumerate(res["fresh"][ev])]
        mw, ew, _ = mean_se(vw)
        mf, ef, _ = mean_se(vf)
        dd = [a - c for a, c in zip(vw, vf)]
        md, ed, _ = mean_se(dd)
        row["d_" + q] = {"world": mw, "world_se": ew, "fresh": mf, "fresh_se": ef, "diff": md, "diff_se": ed,
                         "n_world_gt_fresh": sum(1 for x in dd if x > 0)}
    for q in ("t_joy", "t_sal", "t_fear", "joy_after", "sal_after", "fear_after"):
        vw = [r[q] for r in res["world"][ev]]
        vf = [r[q] for r in res["fresh"][ev]]
        mw, ew, _ = mean_se(vw)
        mf, ef, _ = mean_se(vf)
        md, ed, _ = mean_se([a - c for a, c in zip(vw, vf)])
        row[q] = {"world": mw, "world_se": ew, "fresh": mf, "fresh_se": ef, "diff": md, "diff_se": ed}
    for q, key in (("t_joy", "inc_joy"), ("t_sal", "inc_sal")):      # above the arm's own quiet floor
        iw = [res["world"][ev][i][q] - res["world"]["quiet"][i][q] for i in range(N_SEEDS)]
        iff = [res["fresh"][ev][i][q] - res["fresh"]["quiet"][i][q] for i in range(N_SEEDS)]
        mw, ew, _ = mean_se(iw)
        mf, ef, _ = mean_se(iff)
        md, ed, _ = mean_se([a - c for a, c in zip(iw, iff)])
        row[key] = {"world": mw, "world_se": ew, "fresh": mf, "fresh_se": ef, "diff": md, "diff_se": ed,
                    "n_pos_world": sum(1 for x in iw if x > 0)}
    row["tag_world"] = dict(Counter(r["tag_after"] for r in res["world"][ev]))
    row["tag_fresh"] = dict(Counter(r["tag_after"] for r in res["fresh"][ev]))
    for arm in ("world", "fresh"):          # closed form, no further event
        joy, fear, sal = row["joy_after"][arm], row["fear_after"][arm], row["sal_after"][arm]
        t35 = TAU["food_joy"] * math.log(joy / 0.35) if joy > 0.35 else 0.0
        tfear = TAU["fear"] * math.log(fear / 0.25) if fear > 0.25 else 0.0
        mm = mood_from(AX0)
        mm.fear = fear * math.exp(-tfear / TAU["fear"])
        mm.food_joy = joy * math.exp(-tfear / TAU["food_joy"])
        mm.salience = sal * math.exp(-tfear / TAU["salience"])
        row["t_joy_below_035_" + arm] = t35
        row["t_fear_below_025_" + arm] = tfear
        row["tag_when_fear_clears_" + arm] = "%s:%s" % mm.mood_tag()
    tab[ev] = row
OUT["effect"] = {"n_seeds": N_SEEDS, "gate": gate, "axes_start": AX0,
                 "rest_world": {q: mean_se([r[q] for r in rests["world"]])[:2] for q in rests["world"][0]},
                 "rest_fresh": {q: mean_se([r[q] for r in rests["fresh"]])[:2] for q in rests["fresh"][0]},
                 "events": tab}
say("   rest (16-seed mean): world", {k: round(v[0], 4) for k, v in OUT["effect"]["rest_world"].items()})
say("   rest (16-seed mean): fresh", {k: round(v[0], 4) for k, v in OUT["effect"]["rest_fresh"].items()})
say("   event      | dDAN world  fresh (paired d +-SE) | t_joy w     f     inc_w  inc_f | t_sal w     f     | joy after w / f | sal after w / f | tag world (n)      | tag fresh (n)     | joy<.35 s w / f")
for ev in EVENTS:
    r = tab[ev]
    say("   %-10s | %+.4f %+.4f (%+.4f %.4f) | %.3f %.3f %+.3f %+.3f | %.3f %.3f | %.3f / %.3f | %.3f / %.3f | %-17s | %-17s | %.0f / %.0f"
        % (ev, r["d_dan"]["world"], r["d_dan"]["fresh"], r["d_dan"]["diff"], r["d_dan"]["diff_se"],
           r["t_joy"]["world"], r["t_joy"]["fresh"], r["inc_joy"]["world"], r["inc_joy"]["fresh"],
           r["t_sal"]["world"], r["t_sal"]["fresh"], r["joy_after"]["world"], r["joy_after"]["fresh"],
           r["sal_after"]["world"], r["sal_after"]["fresh"],
           max(r["tag_world"], key=r["tag_world"].get) + " (%d)" % max(r["tag_world"].values()),
           max(r["tag_fresh"], key=r["tag_fresh"].get) + " (%d)" % max(r["tag_fresh"].values()),
           r["t_joy_below_035_world"], r["t_joy_below_035_fresh"]))

q = tab["quiet"]
c1 = bool(q["t_joy"]["world"] >= 0.90 and q["t_sal"]["world"] >= 0.90)
sp = {k + "_" + arm: max(tab[e][k][arm] for e in KIND) - min(tab[e][k][arm] for e in KIND)
      for k in ("joy_after", "sal_after") for arm in ("world", "fresh")}
c2 = bool(sp["joy_after_world"] < 0.05 and sp["sal_after_world"] < 0.05
          and (sp["joy_after_fresh"] >= 0.10 or sp["sal_after_fresh"] >= 0.10))
c3 = bool(tab["swat"]["joy_after"]["world"] >= 0.90)
OUT["c_verdicts"] = {"C1_OFFSET_FLOOR": c1, "C2_NO_RESOLUTION": c2, "C3_AVERSIVE_JOY": c3, "kind_spread": sp,
                     "C1_inputs": {"t_joy_quiet_world": q["t_joy"]["world"], "t_sal_quiet_world": q["t_sal"]["world"]}}
say("   C1 OFFSET_FLOOR: quiet-event targets in world t_joy %.4f, t_sal %.4f (fresh %.4f, %.4f) -> %s"
    % (q["t_joy"]["world"], q["t_sal"]["world"], q["t_joy"]["fresh"], q["t_sal"]["fresh"], c1))
say("   C2 AXIS_RESOLUTION: spread over the 8 kind events %s -> NO_RESOLUTION = %s"
    % ({k: round(v, 4) for k, v in sp.items()}, c2))
say("   C3 AVERSIVE_JOY: food_joy right after a swat: world %.4f, fresh %.4f -> %s"
    % (tab["swat"]["joy_after"]["world"], tab["swat"]["joy_after"]["fresh"], c3))
say("   swat: tag right after world %s / fresh %s; when fear clears (world %.0f s, fresh %.0f s): %s / %s"
    % (tab["swat"]["tag_world"], tab["swat"]["tag_fresh"], tab["swat"]["t_fear_below_025_world"],
       tab["swat"]["t_fear_below_025_fresh"], tab["swat"]["tag_when_fear_clears_world"], tab["swat"]["tag_when_fear_clears_fresh"]))
say("   rake: tag right after world %s / fresh %s; when fear clears (world %.0f s, fresh %.0f s): %s / %s"
    % (tab["rake"]["tag_world"], tab["rake"]["tag_fresh"], tab["rake"]["t_fear_below_025_world"],
       tab["rake"]["t_fear_below_025_fresh"], tab["rake"]["tag_when_fear_clears_world"], tab["rake"]["tag_when_fear_clears_fresh"]))
say("   d dopamine (world / fresh):", {e: (round(tab[e]["d_dop"]["world"], 4), round(tab[e]["d_dop"]["fresh"], 4)) for e in EVENTS})

OUT["wall_s"] = round(time.time() - T0, 1)
with open(f"{LAB}/results_l293.json", "w") as f:
    json.dump(OUT, f, indent=1, default=float)
say("\ndone %.1f s -> %s/results_l293.json" % (OUT["wall_s"], LAB))
