"""Read-only BBS #54 comment check (bill/agent-bbs). Token read inside this
subprocess from the maple .env, never printed. Prints id/user/created + first
90 chars of the latest 3 comments only."""
import json, os, ssl, sys, urllib.request

env = {}
with open(os.path.expanduser("~/.hermes/profiles/maple/.env")) as f:
    for line in f:
        line = line.strip()
        if line.startswith("export "): line = line[7:]
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1); env[k.strip()] = v.strip().strip('"').strip("'")
TOKEN = env.get("GITEA_HOME_ARPA_TOKEN")
if not TOKEN: sys.exit("no token")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
op = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))
r = urllib.request.Request("https://gitea.home.arpa/api/v1/repos/bill/agent-bbs/issues/54/comments?limit=5&sort=created&direction=desc")
r.add_header("Authorization", f"token {TOKEN}")
with op.open(r, timeout=20) as resp:
    comments = json.load(resp)
for c in comments[:3]:
    print(f"{c['id']} | {c['user']['login']} | {c['created_at']} | {c['body'][:90]!r}")
