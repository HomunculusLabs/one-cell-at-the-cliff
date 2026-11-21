# L162 ADDENDUM-2 instruments: I4 residual (induced) coherence + I5 evoked
# fraction. Registered in l162/PREREG.md ADDENDUM 2 BEFORE this output.
# Zero rollouts, read-only, deterministic (no RNG).
import json
import math
import re

import numpy as np

WIN, DT = 6000, 0.01
SEG, HOP = 2000, 1000
FILES = ["l154/raw_l154.npz", "l150/raw_l150.npz"]
POOLS = ([f"Ti_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"Tr_{s}" for s in ("fL", "fR", "eL", "eR")]
         + [f"{j}_{s}" for j in ("Ta", "Pr", "Sr")
            for s in ("aL", "aR", "bL", "bR")])
EXTRA = ["mm", "xm"]
CHANNELS = POOLS + EXTRA
ARMS = {"l154/raw_l154.npz": ["b65", "off"], "l150/raw_l150.npz": ["b65"]}

_HANN = np.hanning(SEG)
_STARTS = list(range(0, WIN - SEG + 1, HOP))
K = len(_STARTS)
BIN_SEG, BIN_FULL = 2, 6
assert abs(np.fft.rfftfreq(SEG, DT)[BIN_SEG] - 0.1) < 1e-12
assert abs(np.fft.rfftfreq(WIN, DT)[BIN_FULL] - 0.1) < 1e-12


def seg_vec(x):
    out = np.empty(K, dtype=np.complex128)
    for j, s0 in enumerate(_STARTS):
        w = x[s0:s0 + SEG]
        out[j] = np.fft.rfft((w - w.mean()) * _HANN)[BIN_SEG]
    return out


def msc_matrix(SA, SB):
    C = SA @ SB.conj().T
    PA = (np.abs(SA) ** 2).sum(axis=1)
    PB = (np.abs(SB) ** 2).sum(axis=1)
    return (np.abs(C) ** 2) / np.outer(PA, PB)


# CERT-5 analytic: the residual instrument must SEPARATE the two branches
t = np.arange(WIN) * DT
n_t = 18
# branch A: one shared clock with per-rollout phase jitter -> residual coherent
jit = [0.9 * math.sin(3.1 * i) for i in range(n_t)]
A1 = np.array([seg_vec(np.sin(2 * math.pi * 0.1 * t + jit[i])) for i in range(n_t)])
A2 = np.array([seg_vec(1.3 * np.sin(2 * math.pi * 0.1 * t + jit[i] + 0.4))
               for i in range(n_t)])
# branch B: independent jitter per channel -> residual decoheres
jb = [0.9 * math.sin(1.7 * i + 2.0) for i in range(n_t)]
B1 = A1
B2 = np.array([seg_vec(1.3 * np.sin(2 * math.pi * 0.1 * t + jb[i] + 0.4))
               for i in range(n_t)])


def resid_stack(raws):
    m = raws.mean(axis=0)
    return np.array([seg_vec(x - m) for x in raws])


RA1 = resid_stack(np.array([np.sin(2 * math.pi * 0.1 * t + jit[i])
                            for i in range(n_t)]))
RA2 = resid_stack(np.array([1.3 * np.sin(2 * math.pi * 0.1 * t + jit[i] + 0.4)
                            for i in range(n_t)]))
RB2 = resid_stack(np.array([1.3 * np.sin(2 * math.pi * 0.1 * t + jb[i] + 0.4)
                            for i in range(n_t)]))
MA = msc_matrix(RA1, RA2)
MB = msc_matrix(RA1, RB2)
ra = float(np.median(np.diag(MA)) / np.median(MA[~np.eye(n_t, dtype=bool)]))
rb = float(np.median(np.diag(MB)) / np.median(MB[~np.eye(n_t, dtype=bool)]))
assert ra >= 2.0, ("CERT-5 shared branch", ra)
assert rb < 2.0, ("CERT-5 independent branch", rb)
print(f"CERT-5 residual instrument separates branches: shared ratio "
      f"{ra:.2f} (>=2) vs independent {rb:.2f} (<2): PASS")

# ---------------- load ------------------------------------------------------
l157 = json.load(open("l157/static.json"))
CARRIER = [c for c in POOLS if l157["pooled"][c]["wilson_lb"] >= 0.5]
CONTROL = [c for c in POOLS if l157["pooled"][c]["below"] <= 6]
assert len(CARRIER) == 8 and len(CONTROL) == 9
CP = [(CARRIER[i], CARRIER[j]) for i in range(8) for j in range(i + 1, 8)]
NP_ = [(CONTROL[i], CONTROL[j])
       for i in range(9) for j in range(i + 1, 9)]
assert len(CP) == 28 and len(NP_) == 36

RSEG, EV, seeds = {}, {}, {}
for f in FILES:
    z = np.load(f)
    ss = sorted(int(m.group(1)) for m in
                (re.match(r"^mm_b65_(\d+)$", k) for k in z.files) if m)
    seeds[f] = ss
    assert len(ss) == 18
    for a in ARMS[f]:
        for ch in CHANNELS:
            raws = np.array([z[f"{ch}_{a}_{s}"][:WIN].astype(np.float64)
                             for s in ss])
            m = raws.mean(axis=0)
            RSEG[(f, a, ch)] = np.array([seg_vec(x - m) for x in raws])
            Xs = np.array([np.fft.rfft(x - x.mean())[BIN_FULL] for x in raws])
            EV[(f, a, ch)] = float(abs(Xs.mean()) ** 2
                                   / np.mean(np.abs(Xs) ** 2))
    del z

out = {"card": "L162 ADDENDUM 2: I4 residual coherence + I5 evoked fraction",
       "cert5": dict(shared_ratio=ra, independent_ratio=rb),
       "carrier": CARRIER, "control": CONTROL,
       "i5_evoked_fraction": {f"{f}|{a}|{ch}": EV[(f, a, ch)]
                              for (f, a, ch) in EV},
       "i4": {}, "i4_pooled": {}, "verdict": {}}

for label, pairs in (("carrier", CP), ("control", NP_)):
    for f in FILES:
        for a in ARMS[f]:
            rows = {}
            for pa, pb in pairs:
                M = msc_matrix(RSEG[(f, a, pa)], RSEG[(f, a, pb)])
                n = M.shape[0]
                mm = np.diag(M)
                sh = M[~np.eye(n, dtype=bool)]
                mmd, shd = float(np.median(mm)), float(np.median(sh))
                rows[f"{pa}~{pb}"] = dict(
                    matched_med=mmd, shuffled_med=shd,
                    ratio=(mmd / shd if shd > 0 else float("inf")),
                    clears_r=bool(mmd >= 2.0 * shd))
            out["i4"][f"{label}|{f}|{a}"] = rows

for label, pairs in (("carrier", CP), ("control", NP_)):
    for pa, pb in pairs:
        mats, offs = [], []
        for f in FILES:
            M = msc_matrix(RSEG[(f, "b65", pa)], RSEG[(f, "b65", pb)])
            mats.append(np.diag(M))
            offs.append(M[~np.eye(M.shape[0], dtype=bool)])
        mm = np.concatenate(mats)
        sh = np.concatenate(offs)
        mmd, shd = float(np.median(mm)), float(np.median(sh))
        out["i4_pooled"][f"{label}|{pa}~{pb}"] = dict(
            n_matched=int(mm.size), n_shuffled=int(sh.size),
            matched_med=mmd, shuffled_med=shd, ratio=mmd / shd,
            clears_r=bool(mmd >= 2.0 * shd))


def ncl(label, f, a):
    return sum(v["clears_r"] for v in out["i4"][f"{label}|{f}|{a}"].values())


def medm(label, f, a):
    return float(np.median([v["matched_med"]
                            for v in out["i4"][f"{label}|{f}|{a}"].values()]))


per_file = {}
for f in FILES:
    nc = ncl("carrier", f, "b65")
    cm, ct = medm("carrier", f, "b65"), medm("control", f, "b65")
    d = ("D1r_shared_clock" if (nc >= 22 and cm > ct)
         else "D2r_independent" if nc <= 7 else "D3r_mixed")
    per_file[f] = dict(n_clear_r=nc, n_clear_r_control=ncl("control", f, "b65"),
                       med_matched_carrier=cm, med_matched_control=ct, cls=d)
pooled_nc = sum(v["clears_r"] for k, v in out["i4_pooled"].items()
                if k.startswith("carrier|"))
pooled_ctl = sum(v["clears_r"] for k, v in out["i4_pooled"].items()
                 if k.startswith("control|"))
same = per_file[FILES[0]]["cls"] == per_file[FILES[1]]["cls"]
cls = per_file[FILES[0]]["cls"]
sets = [frozenset(k for k, v in out["i4"][f"carrier|{f}|b65"].items()
                  if v["clears_r"]) for f in FILES]
if cls == "D1r_shared_clock":
    ok = pooled_nc >= 22
elif cls == "D2r_independent":
    ok = pooled_nc <= 7
else:
    ok = bool(8 <= pooled_nc <= 21 and sets[0] == sets[1])
out["verdict"] = dict(per_file=per_file, i4_class=cls, same_on_both=same,
                      pooled_n_clear_r=pooled_nc,
                      pooled_n_clear_r_control=pooled_ctl,
                      defining_ok=bool(ok), fold_draft=bool(same and ok),
                      clearing_sets={f: sorted(s) for f, s in zip(FILES, sets)},
                      sets_identical=bool(sets[0] == sets[1]))
json.dump(out, open("l162/residual.json", "w"), indent=1)

print(f"\nI4 class: {cls} (same both files: {same}); pooled clears-r "
      f"{pooled_nc}/28 carrier vs {pooled_ctl}/36 control; fold: "
      f"{'YES' if out['verdict']['fold_draft'] else 'NO'}")
for f in FILES:
    v = per_file[f]
    print(f"  {f}: {v['cls']} clears-r {v['n_clear_r']}/28 (control "
          f"{v['n_clear_r_control']}/36) med residual matched MSC carrier "
          f"{v['med_matched_carrier']:.3f} vs control "
          f"{v['med_matched_control']:.3f}")
print("\npooled carrier residual pairs: matched | shuffled | ratio | clears-r")
for pa, pb in CP:
    v = out["i4_pooled"][f"carrier|{pa}~{pb}"]
    print(f"  {pa:6s}~{pb:6s} {v['matched_med']:.3f} | {v['shuffled_med']:.3f}"
          f" | {v['ratio']:6.2f} | {'Y' if v['clears_r'] else '.'}")
print("\ncontrol residual pairs (median summary): "
      f"matched med {medm('control', FILES[0], 'b65'):.3f} / "
      f"{medm('control', FILES[1], 'b65'):.3f}, clears-r "
      f"{ncl('control', FILES[0], 'b65')}/36 + {ncl('control', FILES[1], 'b65')}/36")
print("\nI5 evoked fraction at .100 Hz (b65, both files):")
for ch in CHANNELS:
    tag = ("CARRIER" if ch in CARRIER else
           "control" if ch in CONTROL else "       ")
    print(f"  {ch:5s} {tag} l154 {EV[(FILES[0], 'b65', ch)]:.3f} | "
          f"l150 {EV[(FILES[1], 'b65', ch)]:.3f}")
print(f"\noff-arm (descriptive): clears-r {ncl('carrier', FILES[0], 'off')}/28 "
      f"carrier, {ncl('control', FILES[0], 'off')}/36 control; med matched "
      f"{medm('carrier', FILES[0], 'off'):.3f} vs "
      f"{medm('control', FILES[0], 'off'):.3f}; mm ev "
      f"{EV[(FILES[0], 'off', 'mm')]:.3f}")
print("l162/residual.json written")
