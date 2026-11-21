"""L173 push verify: the remote digest blob == local, byte-for-byte.

Contents API (the /raw route 404s on this Gitea), base64-DECODE before
hashing, token read inside the subprocess and never printed.
"""
import base64
import hashlib
import json
import os
import subprocess

ENV = os.path.expanduser("~/.hermes/profiles/maple/.env")
tok = None
for line in open(ENV):
    if line.startswith("GITEA_HOME_ARPA_TOKEN="):
        tok = line.split("=", 1)[1].strip().strip('"')
assert tok, "token not found in the maple .env"

local = open(os.path.expanduser(
    "~/.hermes/profiles/maple/playground/website/publish/peabrain.md"),
    "rb").read()
url = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")
out = subprocess.run(["curl", "-s", "-H", f"Authorization: token {tok}", url],
                     capture_output=True, text=True).stdout
d = json.loads(out)
remote = base64.b64decode(d["content"])
hl = hashlib.sha256(local).hexdigest()
hr = hashlib.sha256(remote).hexdigest()
print(f"local  sha256 {hl}")
print(f"remote sha256 {hr}")
assert hl == hr, "remote blob differs from local"
txt = remote.decode()
assert "### L173 (a) — the Methods section, with every constant parsed" in txt
assert "max|Δ| = 0.0**, so branch **M1_equation_matches** fired" in txt
assert "DNg100 tonic drive D = 0.2 appears for the first time" in txt
print("PASS: remote digest byte-identical, L173 (a) entry present")
