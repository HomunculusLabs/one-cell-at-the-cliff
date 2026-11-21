"""Verify the L143 digest push: remote blob BYTE-IDENTICAL to local
publish/peabrain.md after base64-decode (hash DECODED content, https
directly — no redirect hop)."""
import base64
import hashlib
import json
import urllib.request
from pathlib import Path

TOKEN = None
env = Path.home() / ".hermes" / "profiles" / "maple" / ".env"
for line in env.read_text().splitlines():
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
assert TOKEN, "token not found in maple .env"

url = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
req = urllib.request.Request(url, headers={"Authorization": f"token {TOKEN}"})
data = json.load(urllib.request.urlopen(req, timeout=30))
blob = base64.b64decode(data["content"])
local = Path.home() / ".hermes/profiles/maple/playground/website/publish/peabrain.md"
ref = local.read_bytes()
h_r, h_l = hashlib.sha256(blob).hexdigest(), hashlib.sha256(ref).hexdigest()
print(f"remote sha256 {h_r[:16]} | local sha256 {h_l[:16]}")
assert blob == ref, "MISMATCH"
assert blob.count(b"### L143") >= 1 and b"two factors + both directions" in blob
print("L143 verify PASS: byte-identical, entry present")
