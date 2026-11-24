"""Timing-only benchmark of the UNMODIFIED native step (post-lock, per PREREG section 2).
Prints ms/step and nothing behavioural. argv: n_threads n_steps"""
import os, sys, time
from pathlib import Path
D = Path(__file__).resolve().parent; P = D.parent.parent / 'peabrain'
sys.path.insert(0, str(P))
import torch
nt = int(sys.argv[1]); n = int(sys.argv[2])
torch.set_num_threads(nt); torch.set_num_interop_threads(1)
from brain import FlyBrain
t = time.monotonic(); b = FlyBrain(str(P / 'brain_graph.pt'), 'cpu'); load = time.monotonic() - t
g = .95 / b.rho; b.seed()
for _ in range(10): b.step(gain=g)
t = time.monotonic()
for _ in range(n): b.step(gain=g)
print(f'threads={nt} load_s={load:.1f} ms_per_step={(time.monotonic() - t) / n * 1e3:.2f}', flush=True)
