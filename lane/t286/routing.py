"""Tick 286: which SESSION receives each _log_event, and which session consolidate_night runs on. Read-only."""
import ast, re

PB = "/home/t3rpz/critters/peabrain"
b = open(f"{PB}/bridge.py").read().split("\n")
sv = open(f"{PB}/serve.py").read()
svl = sv.split("\n")

def show(lines, a, z, tag):
    print(f"--- {tag} L{a}-{z} ---")
    for i in range(a, z + 1):
        print(f"{i}|{lines[i-1]}")

show(b, 386, 392, "bridge _dabble -> _log_event")
show(b, 396, 412, "bridge world_tick -> consolidate_night")
show(b, 560, 569, "bridge _reply_inside -> _log_event")

# enclosing def of world_tick + its session arg
tree = ast.parse("\n".join(b))
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and n.name in ("world_tick", "_reply_inside", "_dabble", "reply", "tick"):
        print(f"DEF {n.name} L{n.lineno} args={[a.arg for a in n.args.args]}")

print("\n--- serve.py: session resolution / world tick scheduling ---")
pat = re.compile(r"world_tick|def (get_session|_session|session_for|load_session)|sessions\[|WORLD|chat_id|\"world\"|'world'")
for i, ln in enumerate(svl, 1):
    if pat.search(ln):
        print(f"{i}|{ln[:150]}")

print("\n--- callers of bridge.reply / _reply_inside in serve.py ---")
t2 = ast.parse(sv)
for n in ast.walk(t2):
    if isinstance(n, ast.Call):
        fn = n.func
        nm = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else None)
        if nm in ("reply", "handle", "world_tick", "consolidate_night", "get_session", "session_for"):
            print(f"  serve.py:{n.lineno} {nm}({', '.join(ast.get_source_segment(sv, a)[:40] for a in n.args)})")
