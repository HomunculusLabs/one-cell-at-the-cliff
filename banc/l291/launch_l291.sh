#!/bin/sh
# L291 launcher (tick 281). Run from anywhere:  sh l291/launch_l291.sh <wid> [<wid> ...]
# nice +15, hard stop 1700 s (L291 PREREG s5), 2 threads (set by the harness). The harness is identical for
# every worker; this file only decides WHICH worker ids run at the same time (at most 2 per call).
# Logs: l291/run_w<id>.log ; exit code: l291/exit_w<id> (written only after the python exits).
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
for w in "$@"; do
  ( L291_MODE=work L291_WID=$w L291_NW=2 L291_THREADS=2 nice -n 15 timeout 1700 $PY l291/edge_run_l291.py > l291/run_w$w.log 2>&1
    rc=$?
    echo "w$w exit $rc at $(date +%T)" >> l291/run_w$w.log
    echo "$rc" > l291/exit_w$w ) &
done
date +%T > l291/launch_batch_$(date +%H%M%S).started
wait
