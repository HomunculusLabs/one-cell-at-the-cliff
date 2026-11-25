#!/bin/sh
# L290 stage B launcher (tick 277). Run from banc/:  sh l290/launch_l290.sh <wid> [<wid> ...]
# nice +15, hard stop 1700 s (L290 PREREG s7). The harness is identical for every
# worker; this file only decides WHICH worker ids run at the same time (<= 2 per call).
# Logs: l290/run_w<id>.log ; exit code: l290/exit_w<id>
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
for w in "$@"; do
  ( L290_MODE=work L290_WID=$w L290_NW=3 L290_THREADS=2 nice -n 15 timeout 1700 $PY l290/edge_run_l290.py > l290/run_w$w.log 2>&1
    rc=$?
    echo "w$w exit $rc at $(date +%T)" >> l290/run_w$w.log
    echo "$rc" > l290/exit_w$w ) &
done
date +%T > l290/launch_batch_$(date +%H%M%S).started
wait
