# Budget rung (resolved post-lock, timing-only benchmark; bench.log)

Benchmark at 20:29 (unmodified native step, CPU, cores 3/5/6/7):
4 concurrent single-thread processes 74-83 ms/step each (~51 steps/s total);
one 4-thread process 22.3 ms/step (~45 steps/s). Mode = 4 single-thread processes.

Projected wall (steps per job = 4 batteries x 7,680 + ~4,000 forage/replay steps x 3 days):
R0 (3 seeds, K_idle 2) ~106 min; R1 (2 seeds, K_idle 2) ~71 min; R2 (2 seeds, K_idle 0) ~56 min.

DEVIATION 1: no rung projects <= 55 min. R2, the last rung, projects ~56 and is taken;
the hard wall (2.5 h) still holds. Seeds 0 and 1, K_idle 0, one job per core.
A second lab lane (banc/l200, 6 processes) started on this box at ~20:31; real wall will
run longer than projected. run.py checkpoints after every battery and day.

Mechanical smoke (post-lock, 2 scenarios, 1 coarse day, plastic seed 0, out/smoke_*):
used only to check that the harness runs; no parameter was changed after it.
