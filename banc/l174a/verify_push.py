import base64, hashlib, json, os, subprocess, sys
tok = None
for line in open(os.path.expanduser('~/.hermes/profiles/maple/.env')):
    if line.startswith('GITEA_HOME_ARPA_TOKEN='):
        tok = line.split('=', 1)[1].strip().strip('"')
assert tok, 'token missing'
url = ('https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/'
       'website/publish/peabrain.md?ref=main')
out = subprocess.run(['curl', '-sS', '-H', f'Authorization: token {tok}', url],
                     capture_output=True, text=True).stdout
d = json.loads(out)
remote = base64.b64decode(d['content'])
local = open(os.path.expanduser('~/.hermes/profiles/maple/playground/website/'
                                'publish/peabrain.md'), 'rb').read()
rs, ls = hashlib.sha256(remote).hexdigest(), hashlib.sha256(local).hexdigest()
print('remote sha256', rs[:16], 'local', ls[:16], 'identical', rs == ls)
print('L174a entry present remote:', b'### L174 (a) \xe2\x80\x94 the references, fetched rather than remembered' in remote)
assert rs == ls and b'### L174 (a)' in remote
print('PASS')
