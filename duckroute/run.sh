#!/bin/sh
# held-out tier: seeds 2,3 x {frozen, plastic}, v2's rung (K_idle 0, one single-thread job per core).
# run.py is a byte-identical copy of duckplast2/run.py; it writes to ./out only. CPU <= 4, no GPU.
set -eu
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1
PY=../../peabrain/.venv/bin/python
mkdir -p out
[ "$(sha256sum < run.py)" = "$(sha256sum < ../duckplast2/run.py)" ]
pids=""
set -- "2 frozen 3" "2 plastic 5" "3 frozen 6" "3 plastic 7"
for job in "$@"; do
  set -- $job
  taskset -c $3 timeout 6600 $PY -Bu run.py $1 $2 0 1 > out/log_seed$1_$2.txt 2>&1 &
  pids="$pids $!"
done
rc=0
for p in $pids; do wait $p || rc=1; done
date -Is
exit $rc
