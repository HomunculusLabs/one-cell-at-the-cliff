import base64, hashlib, json, os, subprocess, sys
TOK=None
for ln in open(os.path.expanduser('/home/t3rpz/.hermes/profiles/maple/.env')):
    if ln.startswith('GITEA_HOME_ARPA_TOKEN='): TOK=ln.split('=',1)[1].strip().strip('"')
assert TOK, 'token not found'
url=('https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/'
     'website/publish/peabrain.md?ref=main')
out=subprocess.run(['curl','-s','-H','Authorization: token '+TOK,url],
                   capture_output=True,text=True).stdout
j=json.loads(out)
remote=base64.b64decode(j['content'])
local=open('/home/t3rpz/.hermes/profiles/maple/playground/website/publish/peabrain.md','rb').read()
rh,lh=hashlib.sha256(remote).hexdigest(),hashlib.sha256(local).hexdigest()
print('remote sha256',rh[:16]); print('local  sha256',lh[:16])
assert rh==lh, 'remote blob != local'
txt=remote.decode()
for s in ['L174 (b4-iii-a) — the strip that had to gate on what was left',
          'The frozen partition is the instrument the next stages inherit',
          'B40', 'DRAFT v3.29']:
    assert s in txt, ('missing entry content', s[:50])
print('push verified: byte-identical, (b4-iii-a) entry present')
