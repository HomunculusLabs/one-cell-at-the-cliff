"""Verify the pushed digest via the Gitea contents API (token read inside the process, never printed)."""
import base64, hashlib, json, os, re, urllib.request

LOCAL = "/home/t3rpz/.hermes/profiles/maple/playground/website/publish/peabrain.md"
URL = "https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/website/publish/peabrain.md?ref=main"
HEAD = "## L294 — what predicts a weight-matched set's effect".encode("utf-8")

tok = None
for cand in (os.path.expanduser("~/.hermes/profiles/maple/.env"), os.path.expanduser("~/.hermes/.env")):
    if not os.path.exists(cand):
        continue
    for ln in open(cand, encoding="utf-8", errors="replace"):
        m = re.match(r'\s*(?:export\s+)?GITEA_HOME_ARPA_TOKEN\s*=\s*["\']?([^"\'\s]+)', ln)
        if m:
            tok = m.group(1); break
    if tok:
        break
if not tok:
    print("NO TOKEN FOUND in candidate .env files -> cannot verify via API"); raise SystemExit(2)

req = urllib.request.Request(URL, headers={"Authorization": f"token {tok}", "Accept": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        status = r.status
        body = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP", e.code); raise SystemExit(3)

remote = base64.b64decode(body["content"]).replace(b"\r\n", b"\n")
local = open(LOCAL, "rb").read().replace(b"\r\n", b"\n")
rh, lh = hashlib.sha256(remote).hexdigest(), hashlib.sha256(local).hexdigest()
print("api status", status, "| remote blob sha", body.get("sha"), "| size", body.get("size"))
print("remote sha256", rh)
print("local  sha256", lh)
print("MATCH" if rh == lh else "MISMATCH", "| remote lines", remote.count(b"\n"), "| L294 header in remote:", remote.count(HEAD))
