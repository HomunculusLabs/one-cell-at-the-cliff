"""Verify the L152 digest push: remote blob BYTE-IDENTICAL to local
publish/peabrain.md after base64-decode (verify_push_l155 form; 11-17
lesson: hash DECODED content, hit https directly with the LAN CA
exception). Also asserts the L152 entry and the Fig. 2 reference are
present in the SERVED bytes."""

import base64, hashlib, json, urllib.request, ssl
from pathlib import Path

TOKEN = None
env = Path.home() / ".hermes" / "profiles" / "maple" / ".env"
for line in env.read_text().splitlines():
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
assert TOKEN, "token not found in maple .env"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE  # LAN internal CA — documented exception

url = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
req = urllib.request.Request(url, headers={"Authorization": f"token {TOKEN}"})
data = json.load(urllib.request.urlopen(req, timeout=30, context=ctx))
blob = base64.b64decode(data["content"])
local = Path.home() / ".hermes/profiles/maple/playground/website/publish/peabrain.md"
ref = local.read_bytes()
h_r, h_l = hashlib.sha256(blob).hexdigest(), hashlib.sha256(ref).hexdigest()
print(f"remote sha256 {h_r[:16]} | local sha256 {h_l[:16]}")
assert blob == ref, "MISMATCH"
assert blob.count(b"### L152") == 1 and b"clamp-vs-cut grid" in blob
print("L152 verify PASS: byte-identical, entry present")
