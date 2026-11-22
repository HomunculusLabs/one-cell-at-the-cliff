#!/usr/bin/env bash
# L202 orchestrator: 4 fixed-plan workers (1 thread each = 4 CPU), ONE final
# verdict after the workers exit. Resume-safe: workers skip cached seeds, reload gains.
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
NW=4
TH=${L202_THREADS:-1}
[ -f l202/PREREG.md ] && [ -f l202/FREEZE.json ] && [ -f l202/static.json ] || { echo "PREREG/FREEZE/static missing — refusing to roll" >> l202/run.out; exit 2; }
echo "--- L202 rollouts: $NW workers x $TH thread(s), launched $(date '+%F %T') | PREREG sha $(sha256sum l202/PREREG.md | cut -c1-16) ---" >> l202/run.out
pids=()
for i in $(seq 0 $((NW-1))); do
  L202_MODE=work L202_WID=$i L202_NW=$NW L202_THREADS=$TH OMP_NUM_THREADS=$TH MKL_NUM_THREADS=$TH nice -n 5 \
    $PY l202/nec_run.py >> l202/run.out 2> l202/work_w$i.err &
  pids+=($!)
  sleep 8
done
echo "${pids[@]}" > l202/worker_pids.txt
while true; do
  alive=0
  for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ $alive -eq 0 ] && break
  sleep 20   # no incremental verdict: a 5th process would exceed the 4-CPU cap
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "--- workers finished $(date '+%F %T') rc=$rc ---" >> l202/run.out
OMP_NUM_THREADS=1 $PY l202/verdict_l202.py > l202/verdict.out 2>&1
echo "--- verdict exit $? $(date '+%F %T') FINAL ---" >> l202/run.out
