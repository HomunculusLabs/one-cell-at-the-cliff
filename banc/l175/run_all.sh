#!/usr/bin/env bash
# L175 stage 2 orchestrator: 5 arm-split workers (2 threads each), then verdict.
# Survives the launching session (setsid/nohup). Resume-safe: workers skip
# cached seeds and reload their gains file. cwd = banc/.
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
NW=5
echo "--- stage 2: scan + twins, $NW workers x 2 threads, launched $(date '+%F %T') ---" >> l175/run.out
pids=()
for i in $(seq 0 $((NW-1))); do
  L175_MODE=work L175_WID=$i L175_NW=$NW L175_THREADS=2 nice -n 5 \
    $PY l175/scan_run.py >> l175/run.out 2> l175/work_w$i.err &
  pids+=($!)
done
echo "${pids[@]}" > l175/worker_pids.txt
while true; do
  alive=0
  for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ $alive -eq 0 ] && break
  sleep 45
  if [ -f l175/verdict_l175.py ]; then
    $PY l175/verdict_l175.py > l175/verdict_partial.out 2>&1
  fi
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "--- workers finished $(date '+%F %T') rc=$rc ---" >> l175/run.out
if [ -f l175/verdict_l175.py ]; then
  $PY l175/verdict_l175.py > l175/verdict.out 2>&1
  echo "--- verdict exit $? $(date '+%F %T') ---" >> l175/run.out
fi
