import numpy as np

z52 = np.load('l52/raw_l52.npz')
z49 = np.load('l49/raw_l49.npz')
for s in (11, 22, 33):
    a = z52[f'mm_f07a3_{s}']
    b = z49[f'mm_cont_{s}'][:10000]
    d = np.abs(a - b)
    i = int(np.argmax(d > 1e-6)) if (d > 1e-6).any() else -1
    print(f's{s}: first_div={i} (0=window start, settle excluded) max|d|={d.max():.4f}')
    if i >= 0:
        print('   around:', d[max(0, i-3):i+6].round(5))
