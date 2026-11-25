"""L295 slice 1 — static, read-only. Which events each selection rule would have chosen.
World log reconstructed from lane/archive; visitor logs read (json.load) from sessions/.
Never writes sessions/ or lane/archive/. Last write: lane/l295/results_l295.json."""
import ast, glob, hashlib, json, os, sys, time, collections, datetime as dt
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
PB = "/home/t3rpz/critters/peabrain"
AR = f"{PB}/lane/archive"
OUT = f"{PB}/lane/l295/results_l295.json"

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

prereg_sha = sha(f"{PB}/lane/l295/PREREG.md")

# ---- constants from bridge.py (AST, never retyped) ----
bsrc = open(f"{PB}/bridge.py").read()
C = {}
for node in ast.parse(bsrc).body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in ("KIND_EVENTS", "TOP_FRAC", "MAX_REPLAYS"):
                C[t.id] = ast.literal_eval(node.value)
KIND, TOP_FRAC, MAX_REPLAYS = set(C["KIND_EVENTS"]), C["TOP_FRAC"], C["MAX_REPLAYS"]
print("CONST", C)

def n_rule(n_ranked):                       # bridge.py L296, source expression verbatim
    return max(1, min(MAX_REPLAYS, int(n_ranked * TOP_FRAC + 0.999)))

# ---- SESSIONS_DIR from serve.py ----
sv = open(f"{PB}/serve.py").read()
sess_dir = None
for node in ast.parse(sv).body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SESSIONS_DIR" for t in node.targets):
        seg = ast.get_source_segment(sv, node.value)
        try:
            sess_dir = eval(compile(ast.Expression(node.value), "x", "eval"), {"os": os, "Path": __import__("pathlib").Path, "__file__": f"{PB}/serve.py", "PEABRAIN_SESSIONS": os.environ.get("PEABRAIN_SESSIONS")})
        except Exception as e:
            print("SESSIONS_DIR eval failed:", e, "| source:", seg)
print("SESSIONS_DIR =", sess_dir, "| exists:", sess_dir and os.path.isdir(sess_dir))

def local(ts):
    return dt.datetime.fromtimestamp(ts, NY)

# ---- archive: snapshots ----
snaps = []
for p in sorted(glob.glob(f"{AR}/snap_*.json")):
    d = json.load(open(p))
    d["_file"] = os.path.basename(p)
    snaps.append(d)
cap_ts = []
for d in snaps:
    ca = d.get("captured_at")
    cap_ts.append(dt.datetime.fromisoformat(ca).timestamp() if isinstance(ca, str) else float(ca))

# ---- pass times: diary 'consolidate' entries, union across snaps, deduped by clock_s ----
passes = {}
for d in snaps:
    for e in d.get("diary") or []:
        if e.get("act") == "consolidate" and e.get("clock_s"):
            passes.setdefault(int(e["clock_s"]), e)
pass_ts = sorted(passes)
print(f"\nARCHIVE snaps={len(snaps)} passes={len(pass_ts)}")

# world non-KIND census (S3a) + lens
world_nonkind = collections.Counter(); world_ev = collections.Counter(); lens = []
for d in snaps:
    dl = d.get("day_log") or []
    lens.append(len(dl))
    for e in dl:
        world_ev[e["ev"]] += 1
        if e["ev"] not in KIND:
            world_nonkind[e["ev"]] += 1

# ---- per-night reconstruction ----
archive_start = min(cap_ts)
nights = []
for k, tk in enumerate(pass_ts):
    t_prev = pass_ts[k - 1] if k > 0 else archive_start
    open_start = (k == 0)
    inwin = [d for d, ct in zip(snaps, cap_ts) if t_prev < ct <= tk + 1e-6 or (open_start and ct <= tk + 1e-6)]
    union = {}; order = []
    lossy = False
    for d in inwin:
        dl = d.get("day_log") or []
        if len(dl) >= 100: lossy = True
        for e in dl:
            key = (e["ev"], round(float(e["t"]), 6))
            if key not in union:
                union[key] = e; order.append(key)
    recs = [union[key] for key in order]
    anomalous = sum(1 for e in recs if e["t"] <= t_prev and not open_start)
    pre = [d for d, ct in zip(snaps, cap_ts) if ct <= tk + 1e-6]
    last_cap = max(ct for ct in cap_ts if ct <= tk + 1e-6) if any(ct <= tk for ct in cap_ts) else None
    tail_min = (tk - last_cap) / 60.0 if last_cap else None
    pass_date = local(tk).date()
    r_date = [e for e in recs if local(e["t"]).date() == pass_date]
    r_wm = list(recs)
    def choose(lst):
        ranked = sorted(lst, key=lambda e: -e["dop"])
        n = n_rule(len(ranked))
        chosen = ranked[:n]
        comp = collections.Counter(e["ev"] for e in chosen)
        return {"n_ranked": len(ranked), "n": n, "composition": dict(comp),
                "kind_in_chosen": sum(1 for e in chosen if e["ev"] in KIND),
                "dop_ties_at_cut": (sum(1 for e in ranked if e["dop"] == ranked[n - 1]["dop"]) if ranked else 0)}
    c_date, c_wm = choose(r_date), choose(r_wm)
    nights.append({
        "k": k, "pass_clock_s": int(tk), "pass_local": local(tk).strftime("%Y-%m-%d %H:%M:%S"),
        "open_start": open_start, "snaps_in_window": len(inwin), "lossy": lossy,
        "union_records": len(recs), "anomalous_pre_window": anomalous,
        "unarchived_tail_min": round(tail_min, 1) if tail_min is not None else None,
        "window_h": round((tk - t_prev) / 3600.0, 2),
        "union_composition": dict(collections.Counter(e["ev"] for e in recs)),
        "union_kind": sum(1 for e in recs if e["ev"] in KIND),
        "R_DATE": c_date, "R_WM": c_wm,
        "extra_admitted_by_wm": len(recs) - len(r_date),
    })

# ---- S1 + S3b: visitor sessions (read-only) ----
vis = []; vis_kind_nonwater = 0; vis_records = 0; vis_nonkind = collections.Counter(); vis_ev = collections.Counter()
all_vis_recs = []
if sess_dir and os.path.isdir(sess_dir):
    for p in sorted(glob.glob(os.path.join(sess_dir, "*.json"))):
        name = os.path.basename(p)
        if name.startswith("world"):
            continue
        try:
            s = json.load(open(p))
        except Exception as ex:
            vis.append({"file": name, "error": str(ex)[:80]}); continue
        dl = s.get("day_log") or []
        evc = collections.Counter(e.get("ev") for e in dl)
        knw = sum(1 for e in dl if e.get("ev") in KIND and e.get("ev") != "water")
        vis_records += len(dl); vis_kind_nonwater += knw
        for e in dl:
            vis_ev[e.get("ev")] += 1
            if e.get("ev") not in KIND: vis_nonkind[e.get("ev")] += 1
            all_vis_recs.append((name, e))
        vis.append({"file": name, "day_log_n": len(dl), "events": dict(evc), "kind_non_water": knw,
                    "night_stamp": s.get("night_stamp", "<absent>"), "plas_mass": None if s.get("plas_d") is None else "present"})
S1 = vis_kind_nonwater > 0

# ---- S3c: what a cross-session union would expose per night ----
for n in nights:
    tk, k = n["pass_clock_s"], n["k"]
    t_prev = pass_ts[k - 1] if k > 0 else archive_start
    win = [(f, e) for f, e in all_vis_recs if t_prev < e["t"] <= tk + 1e-6]
    n["union_visitor"] = {
        "records": len(win), "sessions": len({f for f, _ in win}),
        "events": dict(collections.Counter(e["ev"] for _, e in win)),
        "kind_non_water": sum(1 for _, e in win if e["ev"] in KIND and e["ev"] != "water"),
        "non_kind": sum(1 for _, e in win if e["ev"] not in KIND),
    }

both_water = sum(1 for n in nights if set(n["R_DATE"]["composition"]) <= {"water"} and set(n["R_WM"]["composition"]) <= {"water"})
res = {
    "card": "L295 slice 1 (PREREG on stored day_logs)", "tick": 286,
    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "prereg_sha256": prereg_sha,
    "constants": {"KIND_EVENTS": sorted(KIND), "TOP_FRAC": TOP_FRAC, "MAX_REPLAYS": MAX_REPLAYS},
    "inputs": {"archive_snaps": len(snaps), "archive_first": snaps[0]["_file"], "archive_last": snaps[-1]["_file"],
               "archive_start_local": local(archive_start).strftime("%Y-%m-%d %H:%M"), "sessions_dir": sess_dir},
    "world_census": {"records": sum(world_ev.values()), "events": dict(world_ev), "non_kind": dict(world_nonkind),
                     "snap_daylog_len_min_med_max": [min(lens), sorted(lens)[len(lens) // 2], max(lens)],
                     "snaps_at_cap_100": sum(1 for l in lens if l >= 100)},
    "S2_nights": nights,
    "S2_summary": {"n_nights": len(nights), "both_rules_water_only": both_water,
                   "lossy_nights": sum(1 for n in nights if n["lossy"]),
                   "wm_extra_admitted_total": sum(n["extra_admitted_by_wm"] for n in nights),
                   "pass_local_hours": sorted({n["pass_local"][11:13] for n in nights})},
    "S1_visitor": {"verdict": "TRUE" if S1 else "FALSE", "sessions_scanned": len([v for v in vis if "error" not in v]),
                   "sessions_with_errors": len([v for v in vis if "error" in v]),
                   "records": vis_records, "kind_non_water_records": vis_kind_nonwater,
                   "events": dict(vis_ev), "non_kind": dict(vis_nonkind), "per_session": vis},
    "S3": {"a_world_non_kind_records": sum(world_nonkind.values()),
           "b_visitor_non_kind_records": sum(vis_nonkind.values()),
           "c_union_non_kind_per_night": {str(n["k"]): n["union_visitor"]["non_kind"] for n in nights},
           "c_union_kind_non_water_per_night": {str(n["k"]): n["union_visitor"]["kind_non_water"] for n in nights}},
}
os.makedirs(f"{PB}/lane/l295", exist_ok=True)
with open(OUT, "w") as f:
    json.dump(res, f, indent=1, default=str)
print("\n==== SUMMARY ====")
print("world census:", res["world_census"])
print("S2:", res["S2_summary"])
for n in nights:
    print(f"  night {n['k']:2d} pass {n['pass_local']} win {n['window_h']:5.1f}h open_start={n['open_start']} snaps={n['snaps_in_window']} "
          f"union={n['union_records']:3d} {n['union_composition']} lossy={n['lossy']} tail={n['unarchived_tail_min']}m | "
          f"DATE n={n['R_DATE']['n']} {n['R_DATE']['composition']} | WM n={n['R_WM']['n']} {n['R_WM']['composition']} | extra={n['extra_admitted_by_wm']} "
          f"| visitor-in-window={n['union_visitor']['records']} kindNW={n['union_visitor']['kind_non_water']} nonkind={n['union_visitor']['non_kind']}")
print("S1:", {k: v for k, v in res["S1_visitor"].items() if k != "per_session"})
print("S3:", res["S3"])
print("\nWROTE", OUT, os.path.getsize(OUT), "bytes")
