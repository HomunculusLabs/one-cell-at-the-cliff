import base64, hashlib, json, os, subprocess, sys
tok=None
for line in open(os.path.expanduser('~/.hermes/profiles/maple/.env')):
    if line.startswith('GITEA_HOME_ARPA_TOKEN='):
        tok=line.split('=',1)[1].strip().strip('"\'')
assert tok, 'no token'
url=('https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/'
     'website/publish/peabrain.md?ref=main')
out=subprocess.run(['curl','-s','-H',f'Authorization: token {tok}',url],
                   capture_output=True,text=True).stdout
d=json.loads(out)
remote=base64.b64decode(d['content'])
local=open(os.path.expanduser('~/.hermes/profiles/maple/playground/website/publish/peabrain.md'),'rb').read()
rh=hashlib.sha256(remote).hexdigest(); lh=hashlib.sha256(local).hexdigest()
print('remote sha256', rh[:16], 'local', lh[:16], 'IDENTICAL' if rh==lh else 'MISMATCH')
print('L169 (c2) entry present:', b'L169 (c2) \xe2\x80\x94 displacement is not removal' in remote)
sys.exit(0 if rh==lh else 1)
