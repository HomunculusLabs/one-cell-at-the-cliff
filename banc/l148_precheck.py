"""L148 precheck: B32 (3349..3364) absent from EVERY npz under banc/."""
import glob
import zipfile

B32 = list(range(3349, 3365))
probes = [f"mm_full_{s}" for s in B32]
hits = []
npzs = sorted(glob.glob("**/*.npz", recursive=True))
for p in npzs:
    try:
        with zipfile.ZipFile(p) as z:
            names = set(z.namelist())
    except Exception as e:  # noqa: BLE001
        hits.append((p, f"UNREADABLE {e}"))
        continue
    for pr in probes:
        if pr in names:
            hits.append((p, pr))
assert not hits, ("B32 COLLISION (STOP)", hits)
print(f"B32 absence: PASS across {len(npzs)} npz files")
