#!/usr/bin/env python3
"""Verify the pushed digest blob matches local, byte for byte.

Gitea's /raw route 404s on this host, so read through the contents API and
base64-DECODE before hashing (hashing the encoded string fails a perfect
push). Token comes from the maple .env inside this process; never printed.
"""
import base64, hashlib, json, os, re, subprocess, sys

LOCAL = os.path.expanduser(
    "~/.hermes/profiles/maple/playground/website/publish/peabrain.md")
URL = ("https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/"
       "website/publish/peabrain.md?ref=main")

env = {}
for p in (os.path.expanduser("~/.hermes/profiles/maple/.env"),):
    if os.path.exists(p):
        for line in open(p):
            m = re.match(r"\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$", line)
            if m:
                env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
tok = env.get("GITEA_HOME_ARPA_TOKEN")
assert tok, "no GITEA_HOME_ARPA_TOKEN in the maple .env"

out = subprocess.run(["curl", "-s", "--max-time", "40", "-H",
                      "Authorization: token " + tok, URL],
                     capture_output=True, text=True).stdout
d = json.loads(out)
remote = base64.b64decode(d["content"])
local = open(LOCAL, "rb").read()
h_r = hashlib.sha256(remote).hexdigest()
h_l = hashlib.sha256(local).hexdigest()
print("remote sha256", h_r[:16])
print("local  sha256", h_l[:16])
assert h_r == h_l, "digest blob MISMATCH"
txt = remote.decode()
for s in ("### L174 (b4-i)",
          "T7, the content-preserving sentence split",
          "slice locators",
          "They **fell by 14**",
          "a per-edit invariant is not a per-section invariant"):
    assert s in txt, ("L174 (b4-i) entry content missing", s)
print("BYTE-IDENTICAL after base64-decode; L174 (b4-i) entry present")
