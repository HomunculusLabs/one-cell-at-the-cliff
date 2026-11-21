import numpy as np, json, os
for p in ['../l135/raw_l135.npz','../l169/raw_l169.npz','../l169b2/raw_l169b2.npz','../l65/raw_l65.npz']:
    print('===',p, os.path.getsize(p))
    z=np.load(p)
    ks=list(z.keys())
    print('n_keys',len(ks))
    for k in ks[:18]:
        print('  ',k, z[k].shape if hasattr(z[k],'shape') else type(z[k]), z[k].dtype if hasattr(z[k],'dtype') else '')
