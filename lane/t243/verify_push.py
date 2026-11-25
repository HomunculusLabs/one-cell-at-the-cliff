#!/usr/bin/env python3
"""tick 243 — remote-verify the pushed digest byte-for-byte.
Gitea contents API returns `content` BASE64-ENCODED: decode BEFORE hashing.
Hit https:// DIRECTLY (plain http 308-redirects and curl -L strips the
Authorization header on the cross-host hop). Token read in-process, never
printed."""
import base64, hashlib, json, os, pathlib, ssl, urllib.request

ENV = pathlib.Path.home() / '.hermes/profiles/maple/playground/.env'
tok = None
for cand in [ENV, pathlib.Path.home() / '.hermes/profiles/maple/.env']:
    if cand.exists():
        for line in cand.read_text().splitlines():
            if line.startswith('GITEA_HOME_ARPA_TOKEN='):
                tok = line.split('=', 1)[1].strip().strip('"').strip("'")
assert tok, 'GITEA_HOME_ARPA_TOKEN not found in maple .env'

URL = ('https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/'
       'website/publish/peabrain.md?ref=main')
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request(URL, headers={'Authorization': f'token {tok}'})
with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
    status = r.status
    payload = json.load(r)

remote = base64.b64decode(payload['content'])
local = (pathlib.Path.home()
         / '.hermes/profiles/maple/playground/website/publish/peabrain.md').read_bytes()

hr = hashlib.sha256(remote).hexdigest()
hl = hashlib.sha256(local).hexdigest()
print(f'HTTP {status}')
print(f'  remote {len(remote)} bytes sha256 {hr}')
print(f'  local  {len(local)} bytes sha256 {hl}')
assert hr == hl, 'REMOTE DIFFERS FROM LOCAL'
assert remote.count(b'research tick 243') == 1, 'caveat section not present exactly once'
assert remote.count(b'de-circularising leg') == 1
print('REMOTE BYTE-IDENTICAL; tick-243 caveat present exactly once')
