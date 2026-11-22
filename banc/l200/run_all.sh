#!/usr/bin/env bash
# L200 orchestrator: 6 fixed-plan workers (1 thread each = 6 CPU), ONE final
# verdict after the workers exit. Resume-safe: workers skip cached seeds, reload gains.
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
NW=6
TH=${L200_THREADS:-1}
[ -f l200/PREREG.md ] && [ -f l200/FREEZE.json ] && [ -f l200/selection.json ] || { echo "PREREG/FREEZE/selection missing — refusing to roll" >> l200/run.out; exit 2; }
echo "--- L200 rollouts: $NW workers x $TH thread(s), launched $(date '+%F %T') | PREREG sha $(sha256sum l200/PREREG.md | cut -c1-16) ---" >> l200/run.out
pids=()
for i in $(seq 0 $((NW-1))); do
  L200_MODE=work L200_WID=$i L200_NW=$NW L200_THREADS=$TH OMP_NUM_THREADS=$TH MKL_NUM_THREADS=$TH nice -n 5 \
    $PY l200/ru2_run.py >> l200/run.out 2> l200/work_w$i.err &
  pids+=($!)
  sleep 8
done
echo "${pids[@]}" > l200/worker_pids.txt
last=-1
while true; do
  alive=0
  for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ $alive -eq 0 ] && break
  sleep 20   # no incremental verdict: a 7th process would exceed the 6-CPU cap
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "--- workers finished $(date '+%F %T') rc=$rc ---" >> l200/run.out
OMP_NUM_THREADS=1 $PY l200/verdict_l200.py > l200/verdict.out 2>&1
echo "--- verdict exit $? $(date '+%F %T') FINAL ---" >> l200/run.out
