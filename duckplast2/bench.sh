#!/bin/sh
# timing-only benchmark, post-lock. 4 concurrent single-thread procs, then one 4-thread proc.
set -eu
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1
PY=../../peabrain/.venv/bin/python
: > bench.log
pids=""
for c in 3 5 6 7; do
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 taskset -c $c $PY -B bench.py 1 150 >> bench.$c.tmp 2>&1 &
  pids="$pids $!"
done
wait $pids
for c in 3 5 6 7; do grep -E "threads=" bench.$c.tmp >> bench.log; rm -f bench.$c.tmp; done
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 taskset -c 3,5,6,7 $PY -B bench.py 4 150 2>&1 | grep threads= >> bench.log
cat bench.log
