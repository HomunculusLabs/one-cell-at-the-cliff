#!/bin/sh
# Re-run from any directory. Existing experiment outputs will be replaced.
set -eu
cd "$(dirname "$0")"
mkdir -p cache
export TMPDIR="$PWD/cache" XDG_CACHE_HOME="$PWD/cache" PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1
py=../../peabrain/.venv/bin/python
cpus=$(python -B -c "import os;print(','.join(map(str,sorted(os.sched_getaffinity(0))[:4])))")
taskset -c "$cpus" timeout 6500 "$py" -Bu probe.py >probe.log 2>&1
taskset -c "$cpus" "$py" -B report.py
