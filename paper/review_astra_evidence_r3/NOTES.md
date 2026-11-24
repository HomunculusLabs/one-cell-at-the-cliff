Round 3, read-only CPU audit. The local L175 directory has verdict.out, not verdict_l175.out; use the actual JSON, preregistration, and worker artifacts to determine completeness. No training or fresh trials.

First pass: pinned the draft, claim map, ledger, prereg and final JSON in audit.out. Recomputed canonical pools from seed rows and separately from traces (using the lab’s admissibility list); confirmed paired asymmetry and L137 census. B39 independent scoring completed: all 37 arms, both sides, every fresh seed, both stimulus conditions. Neither B39 twin flips under either scoring window. The fast-window result is a sensitivity analysis, not a replacement decision rule.

Second pass: anchors.py verified every claimed L135 and cross-worker comparison by dtype/shape/bytes; anchors.out records counts. locked.py holds trial time fixed and crosses seed identities on selected arms, retaining all ordered pairs in the average. locked.csv distinguishes repeated-measures cross-pair denominators from the 16 independent noise seeds. Novelty references and relevance limits are in report §5.

Reproduce from lab root (NumPy, CPU; no install or simulation required):

    export CUDA_VISIBLE_DEVICES='' OPENBLAS_NUM_THREADS=1
    P=/home/t3rpz/critters/peabrain/.venv/bin/python
    E=paper/review_astra_evidence_r3
    "$P" -B "$E/audit.py" > "$E/audit.out"
    "$P" -B "$E/anchors.py" > "$E/anchors.out"
    "$P" -B "$E/locked.py"

The rounded individual seed duties in b39-seeds.csv reproduce the stored instrument; b39-arms.csv computes means with NumPy (round-half ties may differ by .001 from the lab). The locked.csv diagnostics use unrounded fractions before averaging. No tests of significance treat rolling windows or cross-pairs as independent.
