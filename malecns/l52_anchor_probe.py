import numpy as np

z = np.load('l49/traces_l49.npz')
print('keys:', sorted(z.files)[:8], '... total', len(z.files))
TS = np.arange(499, 18000, 10)
for s in (11, 22, 33):
    SL, SR = z[f'SL_cont_{s}'], z[f'SR_cont_{s}']
    q = (TS >= 4000) & (TS < 10000)
    both = (SL[TS[q]] >= .25) & (SR[TS[q]] >= .25)
    q2 = (TS >= 10000) & (TS < 18000)
    both2 = (SL[TS[q2]] >= .25) & (SR[TS[q2]] >= .25)
    qe = (TS >= 4000) & (TS < 7000)
    ql = (TS >= 7000) & (TS < 10000)
    e = np.nanmean((SL[TS[qe]] >= .25) & (SR[TS[qe]] >= .25))
    l = np.nanmean((SL[TS[ql]] >= .25) & (SR[TS[ql]] >= .25))
    print(f's{s}: duty[40,100)s={np.nanmean(both):.3f} duty[100,180)s={np.nanmean(both2):.3f} '
          f'early={e:.3f} late={l:.3f}')
    print(f'      SLmed[40,100)={np.nanmedian(SL[TS[q]]):.3f} SRmed={np.nanmedian(SR[TS[q]]):.3f} '
          f'mm_first={z[f"mm_cont_{s}"][:3].round(4)}')
