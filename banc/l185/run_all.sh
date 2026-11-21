#!/usr/bin/env bash
# L185 orchestrator: 6 fixed-plan workers (2 threads each), incremental
# verdict (results_l185.json rewritten atomically whenever a new fresh seed
# is complete on all arms), final verdict. Survives the launching session
# (setsid/nohup). Resume-safe: workers skip cached seeds and reload gains.
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
NW=6
[ -f l185/PREREG.md ] || { echo "PREREG missing — refusing to roll" >> l185/run.out; exit 2; }
[ -f l185/selection_s2.json ] || { echo "R3 selection missing — refusing to roll" >> l185/run.out; exit 2; }
echo "--- L185 rollouts: $NW workers x 2 threads, launched $(date '+%F %T') | PREREG sha $(sha256sum l185/PREREG.md | cut -c1-16) ---" >> l185/run.out
pids=()
for i in $(seq 0 $((NW-1))); do
  L185_MODE=work L185_WID=$i L185_NW=$NW L185_THREADS=2 nice -n 5 \
    $PY l185/rep_run.py >> l185/run.out 2> l185/work_w$i.err &
  pids+=($!)
  sleep 12   # stagger the graph-build memory peak (1.6 GB each)
done
echo "${pids[@]}" > l185/worker_pids.txt
last=-1
while true; do
  alive=0
  for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ $alive -eq 0 ] && break
  sleep 20
  n=$(grep -c "seed 35[789][0-9] done" l185/run.out)
  if [ "$n" != "$last" ] && [ "$n" -gt 0 ]; then
    last=$n
    $PY l185/verdict_l185.py > l185/verdict_partial.out 2>&1
  fi
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "--- workers finished $(date '+%F %T') rc=$rc ---" >> l185/run.out
$PY l185/verdict_l185.py > l185/verdict.out 2>&1
echo "--- verdict exit $? $(date '+%F %T') ---" >> l185/run.out
