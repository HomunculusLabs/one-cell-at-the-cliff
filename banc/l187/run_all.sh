#!/usr/bin/env bash
# L187 orchestrator: 6 fixed-plan workers (2 threads each), incremental
# verdict (results_l187.json rewritten atomically whenever a new fresh seed
# is complete), final verdict. Survives the launching session (setsid/nohup).
# Resume-safe: workers skip cached seeds and reload gains.
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
NW=6
[ -f l187/PREREG.md ] || { echo "PREREG missing — refusing to roll" >> l187/run.out; exit 2; }
[ -f l187/L185_DONE.txt ] || { echo "L185 done-gate missing — refusing to roll" >> l187/run.out; exit 2; }
if pgrep -f 'l185/rep_run.py|l185/run_all.sh|l185/verdict_l185.py' > /dev/null; then
  echo "L185 process still alive — refusing to roll" >> l187/run.out; exit 2
fi
echo "--- L187 rollouts: $NW workers x 2 threads, launched $(date '+%F %T') | PREREG sha $(sha256sum l187/PREREG.md | cut -c1-16) ---" >> l187/run.out
pids=()
for i in $(seq 0 $((NW-1))); do
  L187_MODE=work L187_WID=$i L187_NW=$NW L187_THREADS=2 nice -n 5 \
    $PY l187/relay_run.py >> l187/run.out 2> l187/work_w$i.err &
  pids+=($!)
  sleep 12   # stagger the graph-build memory peak
done
echo "${pids[@]}" > l187/worker_pids.txt
last=-1
while true; do
  alive=0
  for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ $alive -eq 0 ] && break
  sleep 20
  n=$(grep -c "seed 36[0-9][0-9] done" l187/run.out)
  if [ "$n" != "$last" ] && [ "$n" -gt 0 ]; then
    last=$n
    $PY l187/verdict_l187.py > l187/verdict_partial.out 2>&1
  fi
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "--- workers finished $(date '+%F %T') rc=$rc ---" >> l187/run.out
$PY l187/verdict_l187.py > l187/verdict.out 2>&1
echo "--- verdict exit $? $(date '+%F %T') FINAL ---" >> l187/run.out
