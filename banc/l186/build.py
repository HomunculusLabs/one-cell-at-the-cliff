"""Generate L186 by slicing the hash-pinned L175 harness (1-based inclusive)."""
from pathlib import Path
from hashlib import sha256
p=Path(__file__).resolve().parent
src=(p.parent/'l175/scan_run.py').read_bytes();assert sha256(src).hexdigest()=='bbfea4e07ff414dc4992b0d17ca4d890ecba58a13482ebe9a7cdf8bbf9488a20'
lines=src.decode().splitlines(True)
def L(a,b):return ''.join(lines[a-1:b])
s=L(19,65)+'''B39=list(range(18601,18617)); SEEDS=ANCH_BIT+B39
'''+L(70,636)+'OUT="l186"\n'+L(638,682)+'''from pathlib import Path
nfiles=0
for archive in Path('.').rglob('*.npz'):
    if archive.parts[0]==OUT: continue
    with zipfile.ZipFile(archive) as z:
        assert all(not (set(map(int,re.findall(r'\\d+',k))) & set(B39)) for k in z.namelist()),archive
    nfiles+=1
log('fresh keyscan PASS',nfiles)
'''+L(714,718)+L(743,808)+'''add_arm('sc25',1110)
if True:
'''+L(818,837)+'''TRACK=[1110]; DM={}
assert LOC_OF('sc25')[1110]<0
'''+L(890,1063)+'''MY_ARMS=['sc25']
RAW_PATH,XM_PATH=OUT+'/raw.npz',OUT+'/xm.npz'; GAINS_PATH=OUT+'/gains.json'
'''+L(1074,1121)+'''ANCH_PATH=OUT+'/anchors.json'
'''+L(1126,1165)+'''    AMPA=canonical.copy()
    if seed not in ANCH_BIT:
        for b,j in zip((0,4000),np.random.default_rng(np.random.SeedSequence([186,seed])).integers(-300,301,2)):
            AMPA[b+900:b+1400]=0
            AMPA[b+900+j:b+1400+j]=ENT_AMP
    store[f'gate_{seed}']=AMPA>0
    carrier=np.empty(WIN,np.float32)
'''+L(1166,1300)+'''        carrier[k]=X['cutwA'][loc_wA[1110],0].item()
'''+L(1301,1306)+'''    store[f'GI1110_cutwA_{seed}']=carrier
    store[f'GI1110_sc25_{seed}']=np.full(WIN,np.nan,np.float32)
'''+L(1307,1324)
s=s.replace('for seed in SEEDS:', 'canonical=AMPA.copy()\nfor seed in SEEDS:'); assert 'AMPA = np.zeros' in s and 'ST = json.load' in s
compile(s,'run.py','exec');(p/'run.py').write_text(s)
