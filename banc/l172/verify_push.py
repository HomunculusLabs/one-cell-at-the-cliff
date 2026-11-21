import base64, hashlib, json, os, subprocess, sys
LOCAL = os.path.expanduser('~/.hermes/profiles/maple/playground/website/publish/peabrain.md')
TOKEN = None
for line in open(os.path.expanduser('~/.hermes/profiles/maple/.env')):
    if line.startswith('GITEA_HOME_ARPA_TOKEN='):
        TOKEN = line.split('=', 1)[1].strip().strip('"\'')
assert TOKEN, 'no token'
url = ('https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/'
       'website/publish/peabrain.md?ref=main')
out = subprocess.run(['curl', '-sk', '-H', f'Authorization: token {TOKEN}', url],
                     capture_output=True, text=True).stdout
d = json.loads(out)
remote = base64.b64decode(d['content'])
local = open(LOCAL, 'rb').read()
rh = hashlib.sha256(remote).hexdigest()
lh = hashlib.sha256(local).hexdigest()
print('remote sha256', rh[:16])
print('local  sha256', lh[:16])
assert rh == lh, 'BLOB MISMATCH'
assert b'L172 (a) \xe2\x80\x94 one pooled count per arm' in remote, 'L172 entry absent'
assert b'twin \xe2\x88\x92 base = +.175' in remote, 'claim sentence absent'
print('PASS: remote blob byte-identical and carries the L172 (a) entry')
