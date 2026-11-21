import base64
import hashlib
import json
import urllib.request

# verify push via contents API (base64-decode before hashing — 11-17 law)
url = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
token = [l.split("=", 1)[1].strip().strip('"')
         for l in open("/home/t3rpz/.hermes/profiles/maple/.env")
         if l.startswith("GITEA_HOME_ARPA_TOKEN")][0]
req = urllib.request.Request(url, headers={"Authorization": "token " + token})
with urllib.request.urlopen(req, timeout=30) as r:
    meta = json.load(r)
remote = base64.b64decode(meta["content"])
local = open("/home/t3rpz/.hermes/profiles/maple/playground/website/"
             "publish/peabrain.md", "rb").read()
assert hashlib.sha256(remote).hexdigest() == hashlib.sha256(local).hexdigest(), \
    "blob mismatch"
assert b"### L154" in remote and b"NOT MET at rate fidelity" in remote
print("remote blob sha256 BYTE-IDENTICAL; L154 entry present")
