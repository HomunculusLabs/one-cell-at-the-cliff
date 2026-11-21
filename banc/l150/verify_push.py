"""L150 push verify: contents-API blob sha256 vs local peabrain.md digest.
Token read from maple .env inside the process, never printed."""
import base64
import hashlib
import json
import os
import urllib.request

tok = None
for line in open(os.path.expanduser(
        "~/.hermes/profiles/maple/.env")):
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = line.strip().split("=", 1)[1]
        break
assert tok, "token not found"
url = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
req = urllib.request.Request(url, headers={"Authorization": "token " + tok})
doc = json.load(urllib.request.urlopen(req, timeout=30))
raw = base64.b64decode(doc["content"])
remote_sha = hashlib.sha256(raw).hexdigest()
local = open(os.path.expanduser(
    "~/.hermes/profiles/maple/playground/website/publish/peabrain.md"), "rb").read()
local_sha = hashlib.sha256(local).hexdigest()
print("remote sha256:", remote_sha)
print("local  sha256:", local_sha)
print("BYTE-IDENTICAL" if remote_sha == local_sha else "MISMATCH")
print("L150 entry present:", "### L150" in raw.decode())
