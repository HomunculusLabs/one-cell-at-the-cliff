# L290 pre-run audit (tick 278) — written BEFORE final_l290.py was executed

Scope: final_l290.py (mtime 2026-11-24 22:44, written 4 min after the 22:40 launch and before
the first worker finished at 22:59) was read line by line against l290/PREREG.md
(27b6a473...) BEFORE its first execution. No effect number existed when this note was written
(there is no results_l290*.json in this directory and no l290/ file is newer than 23:02).
The script is NOT edited; the two readings below are recorded so the verdict prose uses them.

## Faithful (checked clause by clause)

- s3 sets/arms: 20 group arms + 5 fixed twins = PLAN 25; SAME-SET exclusion via
  sets.json `same_set_pairs`; deleted entries must equal the set per worker.
- s5 eps = 2F with F recomputed from A1's stored nf arm and asserted equal to A1's.
- s5 advantage, EXCEEDS (>= eps, p <= .01), WINS legs raw (.001) / random (all > 0, >= 4 of 5
  EXCEEDS) / SUPPORT (>= 1 e14 comparator, all EXCEEDED), verdict order (a) -> (b) -> (c) ->
  NO_DECISION, (c) = fewer than 8 of 15 random arms with |E| > 2F.
- Companions (d), (e) with its >= 8 support rule, (f) computed only after VERDICT is fixed.
- Predictions S1/S2/N1/R1-R5 scored exactly as s6 writes them.

## Reading 1 — the "(1 - p_up) <= 0.01" clause of IS EXCEEDED BY

PREREG s5 writes the exceedance tail as "(1 - p_up)". Literally that equals the lower tail
only when sign(E_U) = +1. The code uses `p_opp` = the one-sided tail IN THE DIRECTION of the
observed (negative) advantage. The two agree whenever every used-set has E > 0 (which is
prediction R2's first half); they could differ only for a used-set with E < 0 that is exceeded
through a positive D. The results file stores D, p_adv and p_opp per contrast, so which case
occurred is checkable from the artifact; the verdict prose will state it.

## Reading 2 — the per-metric label CONFOUNDED_BY_E14 covers two cases

The code labels a metric CONFOUNDED_BY_E14 when raw and random pass but `support` is False.
`support` is False both when there is NO e14-containing comparator (the PREREG's definition)
and when e14 comparators EXIST but at least one is not exceeded (the PREREG's SUPPORT failure,
which it does not label). The card-level VERDICT is unaffected (WINS requires `support`).
The verdict prose will disambiguate from the stored `e14_comparators` and `support` fields.

## Frozen inputs at execution

- PREREG.md sha256 27b6a473bdb2f9d6d8753d45ba2ca999150674411610467f9cd10f89a323e1f1 (re-hashed this tick = sidecar)
- edge_run_l290.py: asserted in-script to 4c60ce6e8e81029b...
- exit_w0/w1/w2 = 0 / 0 / 0 (22:59:35 / 23:00:24 / 23:02:03)
- final_l290.py sha256 and execution timestamp: appended below by the launching shell.
- final_l290.py sha256 43fef618a2143a1490d368e59a0c85e4484d00cbcf4965189a26831723adf9da, recorded 2026-11-25 00:10:47 EST before first execution

POSTSCRIPT (tick 278, 2026-11-25 00:33 EST, after the run): this paper audit was written before the first execution and
was WRONG about the script. It passed the contrast clause on reading, yet the code's tail rule made IS EXCEEDED BY
unreachable (defect 4), it did not notice that A1's and L290's worker keys collided (defect 2), nor that the A2 arrays
were never loaded, nor that one self-check was fed the wrong synthetic vector (defect 3). An audit that compares a
script with its PREREG clause by clause on paper is not an execution: the script had never been run, and it halted
four times before producing a result. What actually protected the reading is that every halt came BEFORE any print
(zero bytes of stdout in all four), that the original was kept byte-identical, and that the registered rule -- not
the code -- decided what the fix had to be. Next time: execute the analysis script against stale or synthetic
artifacts BEFORE the workers finish.
