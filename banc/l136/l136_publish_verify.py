"""L136 publish verify: contents-API readback, base64-decode, sha256 vs local."""
import base64
import hashlib
import json
import os
import subprocess
import sys

ENV = os.path.expanduser("~/.hermes/profiles/maple/.env")
tok = ""
for line in open(ENV):
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = line.strip().split("=", 1)[1]
        break
assert tok, "token not found in maple .env"
url = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
out = "/tmp/l136_api.json"
subprocess.run(["curl", "-s", "--max-time", "25",
                "--header", f"Authorization: token {tok}", url, "-o", out],
               check=True)
api = json.load(open(out))
remote = base64.b64decode(api["content"])
local = open(os.path.expanduser(
    "~/.hermes/profiles/maple/playground/website/publish/peabrain.md"), "rb").read()
rh, lh = hashlib.sha256(remote).hexdigest(), hashlib.sha256(local).hexdigest()
print("remote sha256", rh)
print("local  sha256", lh)
print("BYTE-IDENTICAL" if rh == lh else "MISMATCH",
      "| remote bytes", len(remote), "| L136 entry present:", b"### L136" in remote)
sys.exit(0 if rh == lh else 1)
