"""Verify the pushed digest blob matches local, byte for byte (contents API,
base64-decoded before hashing — the /raw route 404s on this Gitea)."""
import base64
import hashlib
import json
import os
import subprocess

LOCAL = "/home/t3rpz/.hermes/profiles/maple/playground/website/publish/peabrain.md"
URL = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")

tok = None
for line in open("/home/t3rpz/.hermes/profiles/maple/.env"):
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = line.split("=", 1)[1].strip().strip('"')
assert tok, "token not found"
out = subprocess.run(["curl", "-s", "-H", f"Authorization: token {tok}", URL],
                     capture_output=True, text=True).stdout
d = json.loads(out)
remote = base64.b64decode(d["content"])
local = open(LOCAL, "rb").read()
rs, ls = hashlib.sha256(remote).hexdigest(), hashlib.sha256(local).hexdigest()
print("remote sha256", rs[:16])
print("local  sha256", ls[:16])
assert rs == ls, "BLOB MISMATCH"
txt = remote.decode()
assert "### L176 — our claims under the field's own antiphase metric" in txt
assert "176/176 stored duty statistics reproduced exactly" in txt
assert "9.3\u201328.1" in txt or "9.3-28.1" in txt
print("content asserts OK; byte-identical")
