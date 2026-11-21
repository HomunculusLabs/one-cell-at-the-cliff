import base64, hashlib, json, os, subprocess, sys

tok = None
for line in open(os.path.expanduser('~/.hermes/profiles/maple/.env')):
    if line.startswith('GITEA_HOME_ARPA_TOKEN='):
        tok = line.split('=', 1)[1].strip().strip('"')
assert tok, 'token missing'
url = ('https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/'
       'website/publish/peabrain.md?ref=main')
out = subprocess.run(['curl', '-sS', '-H', 'Authorization: token ' + tok, url],
                     capture_output=True, text=True).stdout
d = json.loads(out)
remote = base64.b64decode(d['content'])
local = open(os.path.expanduser('~/.hermes/profiles/maple/playground/website/'
                                'publish/peabrain.md'), 'rb').read()
rs, ls = hashlib.sha256(remote).hexdigest(), hashlib.sha256(local).hexdigest()
print('remote sha256', rs[:16], 'local', ls[:16], 'identical', rs == ls)
present = b'### L174 (b1) ' in remote
claim = b'identity-beats-number is now prior art' in remote
print('L174 (b1) entry present remote:', present, '| claim sentence:', claim)
assert rs == ls and present and claim
print('PASS')
