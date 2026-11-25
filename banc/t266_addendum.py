"""t266_addendum.py — POST-HOC, pure arithmetic on l234/static.json's own
certified stored values. No operator, no eigenvector, no new measurement.

Why it exists: Q2 fired K2_SEPARATED at pct 0.200, and 15 of the 100 draw K2
values are NEGATIVE. A percentile on a sign-indefinite quantity mixes sign
and magnitude, so the comparison with K (whose null is strictly positive by
Perron-Frobenius) needs the sign-conditioned read beside it. Declared
DESCRIPTION: it was not registered in l234/PREREG.md.
"""
import json

import numpy as np

S = json.load(open("l234/static.json"))
# per-draw K lives in the PARENT artifact (one of the five keys L218 writes
# after L234's slice boundary); CERT-234A proved this run reproduces every
# other leaf of that file at float equality, so it is a certified input.
S218 = json.load(open("l218/static.json"))
q2 = S["Q2_K2_null"]
K2K = np.array(q2["per_draw_K2"], dtype=float)
KK = np.array([r["K"] for r in S218["rows_per_draw_recomputed"]], dtype=float)
K2R = float(q2["K2_real"])
KR = float(q2["K_real"])
n = len(K2K)

# gates: every input reproduced from the artifact's own stored fields
assert len(K2K) == len(KK) == n == 100, (len(K2K), len(KK))
assert float((K2K < K2R).mean()) == q2["pct_K2"], "pct_K2 drift (STOP)"
assert int((K2K < 0).sum()) == q2["n_draws_K2_negative"], "neg count (STOP)"
assert float(np.median(K2K)) == q2["K2_draw_med"], "median drift (STOP)"
assert float(np.median(KK)) == q2["K_draw_med"], "median K drift (STOP)"
assert int((KK < 0).sum()) == 0, "a K draw is negative (STOP)"
assert float(np.median(K2K) / np.median(KK)) == S["Q3_compose"][
    "ratio_of_medians"], "ratio-of-medians drift (STOP)"
ng = 7

pos = K2K[K2K > 0]
out = dict(
    design=("POST-HOC addendum to L234 Q2: the sign-conditioned read of K2's "
            "null. DESCRIPTION, not registered."),
    n_draws=n,
    n_K2_negative=int((K2K < 0).sum()),
    n_K_negative=int((KK < 0).sum()),
    pct_K2_all=float((K2K < K2R).mean()),
    n_below_real=int((K2K < K2R).sum()),
    n_below_real_and_negative=int(((K2K < K2R) & (K2K < 0)).sum()),
    n_below_real_and_positive=int(((K2K < K2R) & (K2K > 0)).sum()),
    n_positive_draws=int((K2K > 0).sum()),
    pct_K2_among_positive_draws=float((pos < K2R).mean()),
    pct_K_all=float((KK < KR).mean()),
    pct_K_stored=S["Q2_K2_null"]["pct_K_stored"],
    suppression_fold_K=float(np.median(KK) / KR),
    suppression_fold_K2_all=float(np.median(K2K) / K2R),
    suppression_fold_K2_positive=float(np.median(pos) / K2R),
    fold_ratio_K_over_K2=float((np.median(KK) / KR)
                               / (np.median(K2K) / K2R)),
    abs_pct_K2=float((np.abs(K2K) < abs(K2R)).mean()),
    n_gates=ng,
    reading=("K's null is strictly positive BY PERRON-FROBENIUS (0 of 100 "
             "draws negative) while K2's straddles zero (15 of 100), so the "
             "two marginals are not comparable on a raw percentile scale: "
             "of the 20 draws below K2_real, 15 are below because they are "
             "NEGATIVE and only 5 because they are smaller in magnitude. "
             "Conditioned on positive draws the carrier's subdominant "
             "overlap sits at pct 0.0588 against K's 0.000, and the "
             "suppression folds are 11.40x vs 4.49x — so L218's claim that "
             "the carrier avoids the dominant mode HARDER survives, in a "
             "currency that has to be named."),
)
json.dump(out, open("l234/addendum_sign.json", "w"), indent=1)
for k, v in out.items():
    if k not in ("design", "reading"):
        print(f"{k}: {v!r}")
print(f"\n[gates] {ng} stored values reproduced at float equality")
print(out["reading"])
