"""Verify the pushed digest blob byte-identical via Gitea contents API.
sha256(base64-decode(remote content)) == sha256(local publish/peabrain.md).
Token read from the maple .env inside this process; never printed."""
import base64
import hashlib
import json
import os
import urllib.request

tok = None
for ln in open(os.path.expanduser(
        "~/.hermes/profiles/maple/.env")):
    if ln.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = ln.strip().split("=", 1)[1].strip().strip('"').strip("'")
assert tok, "token missing"
url = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
with urllib.request.urlopen(req, timeout=20) as r:
    meta = json.load(r)
remote = base64.b64decode(meta["content"])
local = open("/home/t3rpz/.hermes/profiles/maple/playground/"
             "website/publish/peabrain.md", "rb").read()
h_r = hashlib.sha256(remote).hexdigest()
h_l = hashlib.sha256(local).hexdigest()
print("remote sha256", h_r)
print("local  sha256", h_l)
print("BYTE-IDENTICAL" if h_r == h_l else "MISMATCH")
print("L142 in remote:", "L142" in remote.decode("utf-8", "ignore"))
assert h_r == h_l
