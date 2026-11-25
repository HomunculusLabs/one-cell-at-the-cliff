"""Tick 286 L295 pre-PREREG survey: constants, callers, ONE record per stored type. Read-only."""
import ast, glob, json, os, collections, datetime as dt

PB = "/home/t3rpz/critters/peabrain"
src = open(f"{PB}/bridge.py").read()
tree = ast.parse(src)

# --- constants from bridge.py (parsed, never retyped) ---
want = {"KIND_EVENTS", "MAX_REPLAYS", "TOP_FRAC", "NIGHT_ETA", "NIGHT_CAP",
        "DREAM_GAIN", "NIGHT_DOWNSCALE", "MAX_DREAMS", "DREAM_P"}
for node in tree.body:
    tg = []
    if isinstance(node, ast.Assign):
        tg = [t.id for t in node.targets if isinstance(t, ast.Name)]
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        tg = [node.target.id]
    for name in tg:
        if name in want:
            print(f"CONST {name} = {ast.get_source_segment(src, node.value)!r}  (L{node.lineno})")

# --- who calls _log_event / consolidate_night ---
for f in ("bridge.py", "serve.py"):
    s = open(f"{PB}/{f}").read()
    t = ast.parse(s)
    for node in ast.walk(t):
        if isinstance(node, ast.Call):
            fn = node.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else None)
            if nm in ("_log_event", "consolidate_night", "dream"):
                # enclosing function
                encl = "?"
                for cand in ast.walk(t):
                    if isinstance(cand, (ast.FunctionDef, ast.AsyncFunctionDef)) and cand.lineno <= node.lineno <= (cand.end_lineno or 0):
                        if encl == "?" or cand.lineno > 0: encl = cand.name
                # event arg
                arg = ast.get_source_segment(s, node.args[-1]) if node.args else ""
                print(f"CALL {nm}(...) in {f}:{node.lineno} enclosing={encl} last_arg={arg[:60]}")

# --- stored types ---
AR = f"{PB}/lane/archive"
man = [json.loads(l) for l in open(f"{AR}/manifest.jsonl") if l.strip()]
print(f"\nMANIFEST rows={len(man)}")
print("ONE manifest row:", json.dumps(man[-1])[:600])

snaps = sorted(glob.glob(f"{AR}/snap_*.json"))
print(f"\nSNAPS n={len(snaps)} first={os.path.basename(snaps[0])} last={os.path.basename(snaps[-1])}")
s = json.load(open(snaps[-1]))
print("snap top-level keys:", list(s.keys()))
for k, v in s.items():
    if isinstance(v, dict):
        print(f"  [{k}] dict keys={list(v.keys())[:14]}")
    elif isinstance(v, list):
        print(f"  [{k}] list len={len(v)}; one={json.dumps(v[0])[:260] if v else None}")

# one day_log record + key census across ALL snaps
dl_keys = collections.Counter(); evs = collections.Counter(); n_dl = []
for p in snaps:
    d = json.load(open(p))
    sess = d.get("session") or d
    dl = None
    for holder in (d, sess):
        if isinstance(holder, dict) and "day_log" in holder:
            dl = holder["day_log"]; break
    if dl is None:
        # search one level deep
        for k, v in d.items():
            if isinstance(v, dict) and "day_log" in v:
                dl = v["day_log"]; break
    if dl is None: continue
    n_dl.append(len(dl))
    for e in dl:
        dl_keys[tuple(sorted(e.keys()))] += 1
        evs[e.get("ev")] += 1
print(f"\nDAY_LOG: snaps with a day_log={len(n_dl)} len min/med/max={min(n_dl)}/{sorted(n_dl)[len(n_dl)//2]}/{max(n_dl)}")
print("day_log record key-sets:", dict(dl_keys))
print("event census over all snap day_logs:", evs.most_common())
