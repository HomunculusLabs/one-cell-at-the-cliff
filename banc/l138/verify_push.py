"""L138 push verify: contents-API blob sha256 (base64-decode FIRST) vs local."""
import base64
import hashlib
import json
import os
import subprocess

LOCAL = os.path.expanduser(
    "~/.hermes/profiles/maple/playground/website/publish/peabrain.md")

tok = None
with open(os.path.expanduser("~/.hermes/profiles/maple/.env")) as f:
    for line in f:
        if line.strip().startswith("GITEA_HOME_ARPA_TOKEN="):
            tok = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
            break
assert tok, "token not found in maple .env"

url = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
out = subprocess.run(
    ["curl", "-s", "-m", "30", "-H", f"Authorization: token {tok}", url],
    capture_output=True, text=True, check=True).stdout
d = json.loads(out)
rem_sha = hashlib.sha256(base64.b64decode(d["content"])).hexdigest()
loc_sha = hashlib.sha256(open(LOCAL, "rb").read()).hexdigest()
print("local ", loc_sha)
print("remote", rem_sha)
print("BYTE-IDENTICAL" if rem_sha == loc_sha else "MISMATCH")
assert rem_sha == loc_sha
