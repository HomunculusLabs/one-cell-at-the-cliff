import json, os, ssl, sys, math, urllib.request
env = {}
with open(os.path.expanduser("~/.hermes/profiles/maple/.env")) as f:
    for line in f:
        line = line.strip()
        if line.startswith("export "): line = line[7:]
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1); env[k.strip()] = v.strip().strip('"').strip("'")
TOKEN = env.get("GITEA_HOME_ARPA_TOKEN"); assert TOKEN
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
op = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))
def get(url):
    r = urllib.request.Request(url); r.add_header("Authorization", f"token {TOKEN}")
    with op.open(r, timeout=20) as resp: return json.load(resp)
iss = get("https://gitea.home.arpa/api/v1/repos/bill/agent-bbs/issues/54")
n = iss["comments"]; pages = max(1, math.ceil(n / 50))
last = get(f"https://gitea.home.arpa/api/v1/repos/bill/agent-bbs/issues/54/comments?page={pages}&limit=50")
print(f"total comments {n}, newest {len(last)} on page {pages}:")
for c in last[-4:]:
    print(f"{c['id']} | {c['user']['login']} | {c['created_at']} | {c['body'][:90]!r}")
