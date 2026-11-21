import base64, hashlib, json, os, subprocess, re
env=open('/home/t3rpz/.hermes/profiles/maple/.env').read()
tok=re.search(r'GITEA_HOME_ARPA_TOKEN=([^\n]+)',env).group(1).strip().strip('"')
url=('https://gitea.home.arpa/api/v1/repos/miso/workshop/contents/'
     'website/publish/peabrain.md?ref=main')
out=subprocess.run(['curl','-sS','-H','Authorization: token '+tok,url],
                   capture_output=True,text=True).stdout
j=json.loads(out)
remote=base64.b64decode(j['content'])
local=open('/home/t3rpz/.hermes/profiles/maple/playground/website/publish/peabrain.md','rb').read()
print('remote sha256', hashlib.sha256(remote).hexdigest()[:16])
print('local  sha256', hashlib.sha256(local).hexdigest()[:16])
assert remote==local, 'remote blob != local file'
txt=remote.decode()
for s in ['### L174 (b4-iii-b) — the relabel that proved a regex shape is not a class',
          'they split **three** ways the frozen partition had conflated',
          'the label-scheme choice was made by the gate',
          'cancelled eleven of the nineteen removals',
          'DRAFT v3.30; CLAIM-MAP gains block B41']:
    assert s.lower() in txt.lower(), ('missing entry string', s[:40])
print('PUSH VERIFIED: remote byte-identical, (b4-iii-b) entry present')
