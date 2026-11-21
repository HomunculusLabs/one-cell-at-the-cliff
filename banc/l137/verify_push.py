"""L141 push verify: contents-API blob sha256 vs local (base64-decoded)."""
import base64
import hashlib
import json
import subprocess

API = "https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/website/publish/peabrain.md?ref=main"
tok = None
for ln in open("/home/t3rpz/.hermes/profiles/maple/.env"):
    if ln.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = ln.split("=", 1)[1].strip()
r = subprocess.run(["curl", "-s", "-H", f"Authorization: token {tok}", API],
                   capture_output=True, text=True, timeout=30)
j = json.loads(r.stdout)
blob = base64.b64decode(j["content"])
remote = hashlib.sha256(blob).hexdigest()
local = hashlib.sha256(open("/home/t3rpz/.hermes/profiles/maple/playground/"
                            "website/publish/peabrain.md", "rb").read()).hexdigest()
print("remote", remote)
print("local ", local)
print("BYTE-IDENTICAL" if remote == local else "MISMATCH")
assert remote == local
assert "L141 (l137-run)" in blob.decode()
print("L141 entry present")
