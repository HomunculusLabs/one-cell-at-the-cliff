import base64, hashlib, json, os
from pathlib import Path
tok = ""
for ln in Path(os.path.expanduser("~/.hermes/profiles/maple/.env")).read_text().splitlines():
    if ln.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = ln.split("=", 1)[1].strip().strip('"').strip("'")
assert tok, "token missing"
import urllib.request
url = "https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/website/publish/peabrain.md?ref=main"
req = urllib.request.Request(url, headers={"Authorization": "token " + tok})
data = json.load(urllib.request.urlopen(req, timeout=30))
remote = base64.b64decode(data["content"])
local = Path(os.path.expanduser("~/.hermes/profiles/maple/playground/website/publish/peabrain.md")).read_bytes()
rh, lh = hashlib.sha256(remote).hexdigest(), hashlib.sha256(local).hexdigest()
print("remote sha256:", rh)
print("local  sha256:", lh)
print("BYTE-IDENTICAL:", remote == local)
print("L146 entries remote:", remote.decode().count("L146"))
