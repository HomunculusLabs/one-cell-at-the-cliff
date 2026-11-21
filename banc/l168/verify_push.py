#!/usr/bin/env python
"""L168 digest push verification: remote blob must be byte-identical to local.

Contents API (the /raw route 404s on this Gitea) returns `content` BASE64 —
decode before hashing, or a perfect push fails its own check.
"""
import base64, hashlib, json, os, subprocess, sys

LOCAL = "/home/t3rpz/.hermes/profiles/maple/playground/website/publish/peabrain.md"
URL = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")

tok = None
for line in open("/home/t3rpz/.hermes/profiles/maple/.env"):
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = line.split("=", 1)[1].strip().strip('"').strip("'")
assert tok, "token not found in maple .env"

out = subprocess.run(
    ["curl", "-s", "-H", f"Authorization: token {tok}", URL],
    capture_output=True, text=True, timeout=60)
j = json.loads(out.stdout)
assert "content" in j, f"no content field (keys {list(j)[:6]})"
remote = base64.b64decode(j["content"])
local = open(LOCAL, "rb").read()
rh, lh = hashlib.sha256(remote).hexdigest(), hashlib.sha256(local).hexdigest()
print("remote sha256", rh[:16])
print("local  sha256", lh[:16])
print("byte-identical:", rh == lh)
print("L168 entry present on remote:",
      b"### L168 \xe2\x80\x94 scramble controls" in remote)
sys.exit(0 if rh == lh else 1)
