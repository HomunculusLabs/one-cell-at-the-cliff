"""Verify the L174 (b3) digest push: remote blob must be BYTE-IDENTICAL to the
local publish/peabrain.md after base64-decode of the contents-API payload
(11-17 lesson: hash the DECODED content, hit https directly)."""

import base64
import hashlib
import json
import os
import urllib.request

from pathlib import Path

TOKEN = None
env = Path.home() / ".hermes" / "profiles" / "maple" / ".env"
for line in env.read_text().splitlines():
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
assert TOKEN, "token not found in ~/critters/.env"

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
assert b"L174 (b3)" in blob and b"de-duplication completeness" in blob
print("REMOTE BLOB BYTE-IDENTICAL after base64-decode; L174 (b3) entry present")
