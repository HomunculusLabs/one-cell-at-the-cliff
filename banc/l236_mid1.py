
# =========================== L236 MID1 =====================================
# read-only fingerprints + the parent artifacts. Nothing measured yet.
import os as _os236

_RO236 = ["l219/static.json", "l210/static.json", "l218/static.json",
          "l207/static.json", "l178/static.json", "l206/static.json",
          "l219_static.py", "l219_tail.py"]
_FP236 = {}
for _p in _RO236:
    _st = _os236.stat(_p)
    _FP236[_p] = (int(_st.st_size), int(_st.st_mtime_ns))
log(f"[L236 read-only] fingerprinted {len(_FP236)} prior artifacts")

S219 = json.load(open("l219/static.json"))
S207 = json.load(open("l207/static.json"))

# PREREG 0h: the homolog's global id is READ from the stored artifact, never
# hand-typed (the derive-never-retype law).
GI_HOMOLOG = int(S207["Q2_mirror"]["mirror_identity"]["gi"])
_HOM_META = S207["Q2_mirror"]["mirror_identity"]
assert _HOM_META["cell_type"] == "DNp33" and _HOM_META["side"] == "right", \
    (_HOM_META, "homolog identity moved (STOP)")
log(f"[L236] homolog gi {GI_HOMOLOG} = {_HOM_META['cell_type']} "
    f"{_HOM_META['side']} (derived from l207/static.json)")

assert S219["Q219_1_primary"]["branch"] == "TARGET_QUALITY", \
    "L219 branch moved (STOP)"
assert S219["Q219_3_weight_matched"]["verdict"] == "WM_REPRODUCES", \
    "L219 Q219-3 verdict moved (STOP)"
