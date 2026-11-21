#!/usr/bin/env bash
# L197b orchestrator: refuses to start while any L198 process is alive or L198
# is not FINAL (chain order + the 6-worker CPU cap). 6 workers x 2 threads.
cd /home/t3rpz/critters/peabrain-lab/banc || exit 1
PY=/home/t3rpz/critters/peabrain/.venv/bin/python
NW=6
[ -f l197b/PREREG.md ] && [ -f l197b/FREEZE.json ] && [ -f l197b/schedule.json ] || { echo "PREREG/FREEZE/schedule missing — refusing to roll" >> l197b/run.out; exit 2; }
grep -q "L198 VERDICT WRITTEN (FINAL)" l198/verdict.out 2>/dev/null || { echo "L198 not FINAL — refusing to roll (chain order)" >> l197b/run.out; exit 2; }
if pgrep -f 'l198/twin_run.py|l198/run_all.sh|l198/verdict_l198.py' > /dev/null; then
  echo "L198 process still alive — refusing to roll" >> l197b/run.out; exit 2
fi
$PY - <<'P' >> l197b/run.out 2>&1 || exit 2
import json; s=json.load(open('l197b/schedule.json')); assert s['gate']['pass'] is True, 'overlap gate REFUSED'
print('overlap gate PASS', {a: round(s['arms'][a]['overlap']['mean_overlap'],4) for a in 'SW'})
P
echo "--- L197b rollouts: $NW workers x 2 threads, launched $(date '+%F %T') | PREREG sha $(sha256sum l197b/PREREG.md | cut -c1-16) ---" >> l197b/run.out
pids=()
for i in $(seq 0 $((NW-1))); do
  L175_MODE=work L175_WID=$i L175_NW=$NW L175_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 \
    CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 nice -n 5 \
    $PY -B l197b/run_v2.py >> l197b/run.out 2> l197b/work_w$i.err &
  pids+=($!)
  sleep 8
done
echo "${pids[@]}" > l197b/worker_pids.txt
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "--- workers finished $(date '+%F %T') rc=$rc ---" >> l197b/run.out
[ $rc -eq 0 ] || { echo "worker failure — no analysis" >> l197b/run.out; exit 3; }
$PY -B l197b/analyze_v2.py > l197b/analyze.out 2>&1
echo "--- analysis exit $? $(date '+%F %T') FINAL ---" >> l197b/run.out
