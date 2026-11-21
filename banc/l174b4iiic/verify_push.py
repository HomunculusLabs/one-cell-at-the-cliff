#!/usr/bin/env python
"""Verify the pushed digest blob matches local, byte for byte.

Gitea's /raw route 404s on this instance; use the contents API and
BASE64-DECODE `content` before hashing (hashing the encoded string fails a
perfect push).  The token is read inside this process and never printed, and
the API is hit over https DIRECTLY (plain http 308-redirects and curl -L
strips the Authorization header on the cross-host hop).
"""
import base64, hashlib, json, os, pathlib, re, subprocess, sys

LOCAL = pathlib.Path('/home/t3rpz/.hermes/profiles/maple/playground/website/'
                     'publish/peabrain.md')
ENV = pathlib.Path('/home/t3rpz/.hermes/profiles/maple/.env')
tok = None
for line in ENV.read_text().split('\n'):
    m = re.match(r'\s*(?:export\s+)?GITEA_HOME_ARPA_TOKEN\s*=\s*(.+)', line)
    if m:
        tok = m.group(1).strip().strip('"\'')
assert tok, 'GITEA_HOME_ARPA_TOKEN not found in the maple .env'

url = ('https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/'
       'website/publish/peabrain.md?ref=main')
out = subprocess.run(['curl', '-sS', '-k', '-H', f'Authorization: token {tok}',
                      url], capture_output=True, text=True)
assert out.returncode == 0, out.stderr[:300]
j = json.loads(out.stdout)
remote = base64.b64decode(j['content'])
local = LOCAL.read_bytes()
rh = hashlib.sha256(remote).hexdigest()
lh = hashlib.sha256(local).hexdigest()
print('remote sha256', rh[:16])
print('local  sha256', lh[:16])
assert rh == lh, 'PUSH MISMATCH: remote blob != local file'
txt = remote.decode()
for s in ('L174 (b4-iii-c-i)',
          'the de-emphasis that cost zero bytes',
          'exactly **412 bytes differ**',
          'A literal harvest cannot see a gate built from a regex or a token'):
    assert s in txt, ('required digest string missing from the remote blob', s)
print('BYTE-IDENTICAL, entry present — verify_push PASS')
