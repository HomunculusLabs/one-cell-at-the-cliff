#!/bin/sh
# L240 stage A2 launcher (tick 275). Run from banc/:  sh l240/launch_a2.sh <wid> [<wid> ...]
# nice +15, hard stop 1700 s (A2_ADDENDUM s8). The harness is identical for every
# worker; this file only decides WHICH worker ids run at the same time.
# Logs: l240/run_a2_w<id>.log ; exit code: l240/exit_a2_w<id>
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
for w in "$@"; do
  ( L240_MODE=work L240_WID=$w L240_NW=7 L240_THREADS=2 nice -n 15 timeout 1700 $PY l240/edge_run_a2.py > l240/run_a2_w$w.log 2>&1
    rc=$?
    echo "w$w exit $rc at $(date +%T)" >> l240/run_a2_w$w.log
    echo "$rc" > l240/exit_a2_w$w ) &
done
date +%T > l240/launch_a2_batch_$(date +%H%M%S).started
wait
