# L156 digest push verify: contents API (base64) -> sha256 == local blob
import base64, hashlib, json, os, urllib.request
URL = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
tok = None
for ln in open(os.path.expanduser("~/.hermes/profiles/maple/.env")):
    if ln.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = ln.split("=", 1)[1].strip()
req = urllib.request.Request(URL, headers={"Authorization": f"token {tok}"})
meta = json.load(urllib.request.urlopen(req, timeout=30))
remote = base64.b64decode(meta["content"])
local = open(os.path.expanduser(
    "~/.hermes/profiles/maple/playground/website/publish/peabrain.md"), "rb").read()
rh, lh = hashlib.sha256(remote).hexdigest(), hashlib.sha256(local).hexdigest()
txt = remote.decode()
print("remote sha256", rh[:16], "| local", lh[:16],
      "| BYTE-IDENTICAL" if rh == lh else "| MISMATCH")
print("L156 entry present:", "### L156" in txt)
assert rh == lh and "### L156" in txt and "518 of 518" in txt
print("verify_push L156: PASS")
