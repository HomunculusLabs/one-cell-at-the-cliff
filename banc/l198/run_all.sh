#!/usr/bin/env bash
# L198 orchestrator: 6 fixed-plan workers (2 threads each), incremental verdict,
# final verdict. Resume-safe: workers skip cached seeds and reload gains.
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
NW=6
[ -f l198/PREREG.md ] && [ -f l198/FREEZE.json ] && [ -f l198/selection.json ] || { echo "PREREG/FREEZE/selection missing — refusing to roll" >> l198/run.out; exit 2; }
echo "--- L198 rollouts: $NW workers x 2 threads, launched $(date '+%F %T') | PREREG sha $(sha256sum l198/PREREG.md | cut -c1-16) ---" >> l198/run.out
pids=()
for i in $(seq 0 $((NW-1))); do
  L198_MODE=work L198_WID=$i L198_NW=$NW L198_THREADS=2 nice -n 5 \
    $PY l198/twin_run.py >> l198/run.out 2> l198/work_w$i.err &
  pids+=($!)
  sleep 10
done
echo "${pids[@]}" > l198/worker_pids.txt
last=-1
while true; do
  alive=0
  for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ $alive -eq 0 ] && break
  sleep 20
  n=$(grep -c "seed 36[78][0-9] done" l198/run.out)
  if [ "$n" != "$last" ] && [ "$n" -gt 0 ]; then
    last=$n
    $PY l198/verdict_l198.py > l198/verdict_partial.out 2>&1
  fi
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "--- workers finished $(date '+%F %T') rc=$rc ---" >> l198/run.out
$PY l198/verdict_l198.py > l198/verdict.out 2>&1
echo "--- verdict exit $? $(date '+%F %T') FINAL ---" >> l198/run.out
