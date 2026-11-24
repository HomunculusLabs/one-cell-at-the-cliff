#!/bin/sh
set -eu
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=4 CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1
exec timeout 8800 ../../peabrain/.venv/bin/python -Bu run.py
