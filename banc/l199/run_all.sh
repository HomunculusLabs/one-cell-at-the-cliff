#!/usr/bin/env bash
# L199 Part D orchestrator: 3 workers x 2 threads (CPU <= 6), nice 5.
# Refuses to roll without PREREG + FREEZE. L200 runs concurrently elsewhere.
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
NW=3
[ -f l199/PREREG.md ] && [ -f l199/FREEZE.json ] || { echo "PREREG/FREEZE missing — refusing to roll" >> l199/run.out; exit 2; }
echo "--- L199 Part D rollouts: $NW workers x 2 threads, launched $(date '+%F %T') | PREREG sha $(sha256sum l199/PREREG.md | cut -c1-16) ---" >> l199/run.out
pids=()
for i in $(seq 0 $((NW-1))); do
  L175_MODE=work L175_WID=$i L175_NW=$NW L175_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 \
    CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 nice -n 5 \
    $PY -B l199/run_tp.py >> l199/run.out 2> l199/work_w$i.err &
  pids+=($!)
  sleep 5
done
echo "${pids[@]}" > l199/worker_pids.txt
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "--- workers finished $(date '+%F %T') rc=$rc ---" >> l199/run.out
[ $rc -eq 0 ] || { echo "worker failure — no analysis" >> l199/run.out; exit 3; }
OMP_NUM_THREADS=2 $PY -B l199/analyze_causal.py > l199/causal_analyze.out 2>&1
echo "--- causal analysis exit $? $(date '+%F %T') FINAL ---" >> l199/run.out
