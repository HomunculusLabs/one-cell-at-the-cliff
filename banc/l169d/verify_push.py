"""verify_push.py (L169 d) — remote blob byte-verify of the pushed digest.

Reads the Gitea contents API (the /raw route 404s on this instance), which
returns `content` BASE64-ENCODED: decode BEFORE hashing, or a perfect push
fails its own check. Token read inside the subprocess, never printed.
"""
import base64
import hashlib
import json
import os
import subprocess
import sys

ENV = os.path.expanduser("~/.hermes/profiles/maple/.env")
LOCAL = os.path.expanduser(
    "~/.hermes/profiles/maple/playground/website/publish/peabrain.md")
URL = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")

tok = None
for line in open(ENV):
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = line.split("=", 1)[1].strip().strip('"')
assert tok, "token not found in maple .env"

r = subprocess.run(["curl", "-sS", "-H", f"Authorization: token {tok}", URL],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stderr[:200]
j = json.loads(r.stdout)
remote = base64.b64decode(j["content"])
local = open(LOCAL, "rb").read()
rh = hashlib.sha256(remote).hexdigest()
lh = hashlib.sha256(local).hexdigest()
print(f"remote sha256 {rh[:16]} | local sha256 {lh[:16]}")
print(f"byte-identical: {rh == lh}")
entry = "### L169 (d) — the XOR pair at swapped gains"
print(f"L169 (d) entry present in REMOTE blob: {entry.encode() in remote}")
assert rh == lh, "remote blob differs from local"
assert entry.encode() in remote, "L169 (d) entry missing from remote"
print("verify_push (L169 d): PASS")
sys.exit(0)
