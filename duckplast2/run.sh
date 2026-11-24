#!/bin/sh
# rung R2: seeds 0,1 x {frozen, plastic}, K_idle 0, one single-thread job per core. CPU <= 4, no GPU.
set -eu
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1
PY=../../peabrain/.venv/bin/python
mkdir -p out
pids=""
set -- "0 frozen 3" "0 plastic 5" "1 frozen 6" "1 plastic 7"
for job in "$@"; do
  set -- $job
  taskset -c $3 timeout 6600 $PY -Bu run.py $1 $2 0 1 > out/log_seed$1_$2.txt 2>&1 &
  pids="$pids $!"
done
rc=0
for p in $pids; do wait $p || rc=1; done
date -Is
exit $rc
