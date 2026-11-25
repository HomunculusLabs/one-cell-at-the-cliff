# Run from banc/:  python l291/write_prereg.py
# Freezes l291/PREREG.md BEFORE any L291 set is drawn and before any rollout. Every pin is
# DERIVED from the stored artifact it names (never retyped); the file is refused if it exists.
import hashlib
import json
import re
from pathlib import Path

import numpy as np

out = Path('l291')
assert not (out / 'PREREG.md').exists(), 'PREREG.md already exists: no edit after freezing (STOP)'
read = lambda d, n: json.loads((d / n).read_text())
sha = lambda d, n: hashlib.sha256((d / n).read_bytes()).hexdigest()
S = read(Path('l290'), 'sets.json')
R = read(Path('l290'), 'results_l290.json')
syn = [int(m['syn']) for m in S['menu']]
assert len(syn) == 69
N0 = set(S['noop'])
USED = {m: sorted(int(j) for j in S['used'][m]) for m in ('abs', 'crofts', 'hop')}
SIZEU = {11: 'abs', 30: 'crofts', 46: 'hop'}
UARM = {'abs': 'g11', 'crofts': 'gc30', 'hop': 'gh46'}
F = float(R['F'])
R1 = read(Path('l240'), 'results_l240.json')
G11F = float(R1['effects']['g11f']['mean']) / F
assert R['verdict'] == 'NO_DECISION' and abs(F - 2.2931491480943385e-4) < 1e-18, F
T = {n: sum(syn[j] for j in USED[SIZEU[n]]) for n in SIZEU}
assert T == {11: 210, 30: 429, 46: 624}, T
BAND = {n: (int(np.ceil(0.95 * T[n])), int(np.floor(1.05 * T[n]))) for n in SIZEU}
assert BAND == {11: (200, 220), 30: (408, 450), 46: (593, 655)}, BAND
sd = {n: float(np.sqrt(np.var(syn) * n * (69 - n) / 68.0)) for n in SIZEU}
mc = Path('l291/static_probe.out').read_text()
_m5 = re.findall(r'band \+/-5%\s+width\s+[\d.]+\s+accept ([\d.]+).*P\(e14\|band\) ([\d.]+)', mc)
acc = [float(a) for a, p in _m5]
pe14 = [float(p) for a, p in _m5]
pct = [float(x) for x in re.findall(r'percentile ([\d.]+)', mc)]
assert len(acc) == 3 and len(pct) == 3 and len(pe14) == 3, (acc, pct, pe14)
raw = {int(n): sorted(int(j) for j in v) for n, v in S['raw'].items()}
A = R['arms']
inb = {}
for n in SIZEU:
    inb[n] = [(f'r{n}k{k}', sum(syn[j] for j in S['random'][f'r{n}k{k}']), 14 in S['random'][f'r{n}k{k}'],
               A[f'r{n}k{k}']['in_F']) for k in range(1, 6)
              if BAND[n][0] <= sum(syn[j] for j in S['random'][f'r{n}k{k}']) <= BAND[n][1]]
r11 = [(f'r11k{k}', sum(syn[j] for j in S['random'][f'r11k{k}']), A[f'r11k{k}']['in_F']) for k in range(1, 6)]
order = sorted(range(69), key=lambda j: (-syn[j], j))
TXT = f"""# L291 PREREG -- WEIGHT-MATCHED comparators for the group question

Frozen {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST by Miso, tick 281 (LANE.md card L291).
Parent: L290 (PREREG sha {sha(Path('l290'), 'PREREG.md')[:16]}..., VERDICT NO_DECISION, predictions 0/8).
Rule: no edit after freezing. Amendments only as new dated files. A journaled blocker is a valid tick; a
fabricated number is the only failure.

## s0 The question
L290 could not separate "the metric's ENTRY SET is special" from "the set carries heavy edges, or carries e14".
Its random comparators were UNIFORM (not weight-matched) and 9 of 15 cleared the floor.
STATIC FACT, measured this tick from stored sets before any draw: L290's heaviest-synapse comparators were not
weight-matched either. Raw synapse sums: rw11 {sum(syn[j] for j in raw[11])} vs U_abs {T[11]} ({sum(syn[j] for j in raw[11]) / T[11]:.2f}x),
rw30 {sum(syn[j] for j in raw[30])} vs U_crofts {T[30]} ({sum(syn[j] for j in raw[30]) / T[30]:.2f}x), rw46 {sum(syn[j] for j in raw[46])} vs U_hop {T[46]} ({sum(syn[j] for j in raw[46]) / T[46]:.2f}x).
Q: when a random subset is MATCHED to the used-set on raw synapse sum, does the used set still differ from it,
and is any remaining difference carried by e14's MEMBERSHIP rather than by the rest of the set?

## s1 Declared inputs (SEEN, stored; design input, not L291 data)
- Unit F = {F!r} (A1 noise-twin SD/4, l240/results_l240.json, re-read by L290); eps = 2F = {2 * F!r}.
- Used-set effects (stored, in F): g11 {A['g11']['in_F']:+.2f} (A1), gc30 {A['gc30']['in_F']:+.2f}, gh46 {A['gh46']['in_F']:+.2f} (L290). e14 alone {A['e14']['in_F']:+.2f} (A1).
  A1's stored fixed-gain twin of the 11-set: g11f {G11F:+.2f} (l240/results_l240.json effects, reported, not re-run).
- 69-edge menu raw syn: total {sum(syn)}, per-edge mean {np.mean(syn):.1f}, min {min(syn)}, max {max(syn)}. e14 = {syn[14]} synapses, weight rank {order.index(14) + 1} of 69.
- Used-set sums T_n and where they sit in the UNIFORM n-subset sum distribution: U_abs {T[11]} at n 11 ({(T[11] - np.mean(syn) * 11) / sd[11]:+.2f} SD, pct {pct[0]:.3f});
  U_crofts {T[30]} at n 30 ({(T[30] - np.mean(syn) * 30) / sd[30]:+.2f} SD, pct {pct[1]:.3f}); U_hop {T[46]} at n 46 ({(T[46] - np.mean(syn) * 46) / sd[46]:+.2f} SD, pct {pct[2]:.3f}). SD of a uniform n-subset sum: {sd[11]:.1f} / {sd[30]:.1f} / {sd[46]:.1f}.
- SEEN in-band L290 uniform arms (declared so nobody reads L291 as blind): n 11 none (the five r11 arms sum {[r[1] for r in r11]} synapses, all e14-free, E {[round(r[2], 2) for r in r11]} F);
  n 30 {[(a, s, round(e, 2)) for a, s, h, e in inb[30]]} (e14 in {[a for a, s, h, e in inb[30] if h]});
  n 46 {[(a, s, round(e, 2)) for a, s, h, e in inb[46]]} (e14 in {[a for a, s, h, e in inb[46] if h]}).
- Monte Carlo (2e6 uniform draws per size, l291/static_probe.out): acceptance of the registered band {acc[0]:.4f} / {acc[1]:.4f} / {acc[2]:.4f};
  P(a band draw contains e14) {pe14[0]:.3f} / {pe14[1]:.3f} / {pe14[2]:.3f}.

## s2 Design (nothing below is drawn or run until this file is frozen and hashed)
Lineage: byte-identical harness lineage to L240 stage A2 / L290 (l240/edge_run_a2.py sha {sha(Path('l240'), 'edge_run_a2.py')};
generated harness sha pinned by the builder and by the analysis script).
Arms, 17, every one a cut from carrier gi 1110's 69-edge menu (W[target, source] CSR, out-edges in the TARGET rows):
 (i) 15 STRATIFIED subsets. For each size n in (11, 30, 46) with used-set U_n = {SIZEU}: 3 subsets WITH e14
     (s{{n}}w1..3) and 2 WITHOUT e14 (s{{n}}f1..2). Draw: rng = numpy Generator(PCG64(29113)); sizes in order
     11, 30, 46; cells in order w (k = 1..3) then f (k = 1..2); each arm is the FIRST uniform n-subset
     (rng.choice(69, size=n, replace=False)) that has the cell's e14 membership AND a raw synapse sum inside the
     integer band [ceil(0.95 T_n), floor(1.05 T_n)] = [{BAND[11][0]}, {BAND[11][1]}] / [{BAND[30][0]}, {BAND[30][1]}] / [{BAND[46][0]}, {BAND[46][1]}].
     Rejection count is stored per arm. Cap 2,000,000 raw draws per arm: a cap hit is UNDRAWABLE, that arm is
     reported missing and the band is NEVER widened. No re-roll for any other reason: a subset equal to the
     used set (or to another arm) is kept and scored VACUOUS BY IDENTITY.
 (ii) 2 FIXED-GAIN twins: gc30f and gh46f = the stored L290 group graphs (L290 sets.json), at the stored base gain
     g_cutwA = 0.14365819573402408 (edge-not-gain check for the group arms).
Gain rule: every stratified arm is bisected to AF_T in its own process, as in L290 (a per-arm gain bisection is
part of the intervention). Readout windows SETTLE 400 / WIN 6000, 2 threads, float32, as A2.
Seeds 3769-3784 reused (16) so every arm pairs to A1's STORED cutwA traces: a same-draw consistency check,
not an independent replication.
Workers (2): w0 = cutwA + s11w1 s11w2 s11w3 s11f1 s11f2 s30w1 s30w2 s30w3 gc30f;
w1 = cutwA + s30f1 s30f2 s46w1 s46w2 s46w3 s46f1 s46f2 gh46f.
Comparators for the verdict: ONLY the 15 stratified arms. L290's uniform arms are reported beside them, never scored.

## s3 Readout and statistics (inherited from L290 s4, unchanged)
P_a(s) = mean over the 303-cell pool union of the whole-window mean activity (xmean), arm a, seed s, 16 seeds.
d_a(s) = P_a(s) - P_cutwA(s) with A1's stored cutwA; E_a = mean_s d_a(s); reported in F.
Arm-vs-arm: Delta(u,x)(s) = P_u(s) - P_x(s); D = mean; SE = SD/4; exact two-sided sign-flip test over 2^16.
Advantage A = sign(E_u) * D; p_adv = P(null >= A).
EXCEEDS: A >= eps and p_adv <= 0.01. EXCEEDED_BY: A <= -eps and p_adv_down <= 0.01. else WITHIN.
Companion readout (descriptive, no branch): per-pool 20-vector unsigned norm N_a against the A1 vector floor.

## s4 Registered verdict (FIRST MATCH), companions, predictions
For each metric m in (abs, crofts, hop), u = its used-set arm, comparators = its 5 stratified arms
(W = with e14, F = e14-free): exW = number of W comparators u EXCEEDS, exF = the same over F,
by = number of comparators (either cell) that EXCEED u, within = 5 - exW - exF - by.
 (c) I_INSTRUMENT_AT_GROUP: fewer than 8 of the 15 stratified arms clear the floor (|E| > eps).
 (a) SET_BEYOND_WEIGHT:<m>: some m with exW + exF == 5 (all five weight-matched comparators EXCEEDED).
 (b) E14_MEMBERSHIP_NOT_WEIGHT: at least 2 metrics with exF == 2 and exW == 0.
 (w) WEIGHT_CARRIES: at least 2 metrics with exW == 0, exF == 0 and by == 0 (all five WITHIN).
 (n) NOT_SPECIAL_AT_WEIGHT: at least 2 metrics with exW + exF == 0 and by >= 1.
 else NO_DECISION.
The instrument check is FIRST (L290 had it third): a used set beating five floor-level comparators says
nothing about weight. Per-metric labels are stored beside the verdict.
Companions (reported, never gating):
 (g) WEIGHT_LIFTS_E14FREE, paired on the same 16 seeds, per size: mean P over the size's e14-free stratified
     arms minus mean P over its e14-free L290 uniform arms; sign-flip p.
 (h) midrank Spearman of E with effective size among the 15 stratified arms (reported only if >= 10 distinct values).
 (f) EDGE_NOT_GAIN_GROUP: gc30f, gh46f sign-concordant with gc30, gh46 and |E_f - E_b| <= eps; 2 of 2 to fire.
Predictions (registered before any L291 set exists):
 P1  n_clear >= 8 of 15.
 P2  exF == 2 in at least 2 of 3 metrics (the used sets beat their e14-free weight-matched subsets).
 P3  abs reads exF == 2 and exW == 0.
 P4  hop is NOT an E14_MEMBERSHIP metric: exW >= 1.
 P5  EDGE_NOT_GAIN_GROUP fires 2 of 2.
 P6  (g) at n = 11 is positive with p_up <= 0.01.
 P7  VERDICT is neither WEIGHT_CARRIES nor I_INSTRUMENT_AT_GROUP.

## s5 Compute and honesty
nice +15, 2 threads, timeout 1700 per worker, at most 2 workers per background call and 3 concurrent; each worker
admitted only through its exit-code file. Both workers exit 0 -> FINAL; otherwise PARTIAL: verification only, no
effect read, branches NOT read (the verdict needs all three metrics).
Writes confined to banc/l291/ plus the LANE.md bracket, the LANE-LOG lines and the research digest. Prior dirs
read-only. sessions/ never touched. The fly duck is never touched: same PID, NRestarts 0, /needs probed before
and after. The analysis script is executed end-to-end on a synthetic set BEFORE any worker finishes (L290 lesson).
Gates per worker (inherited, a failure VOIDS the worker): anchors 801, 901 bit-exact; cutwA traces bit-identical
to A1's stored l240/raw_w0-2 and xm_w0-2; bisected cutwA gain == 0.14365819573402408; F == {F!r}.

## s6 Disclosures
- DEVIATION FROM THE CARD TEXT. The card said e14 membership is "REPORTED, never conditioned on". This PREREG
  conditions it: 3 with / 2 without e14 per size. Reason: under pure sum-stratification P(no e14-bearing draw in 5)
  at n = 11 is about (1 - {pe14[0]:.3f})^5 = {(1 - pe14[0]) ** 5:.2f}, so the card's own e14-versus-weight question
  would be left to a coin toss on set composition. No L291 effect exists; the allocation is fixed before any draw.
- The static facts in s0/s1 were measured this tick from STORED sets and effects (L221, L240, L290) before the
  freeze. They are why the band is +-5 % and why the raw comparators of L290 cannot answer this question.
- Tick budget: 35 min from 04:58 EST. The rollouts alone need about 18-20 min after the build, so this tick is
  expected to overrun by roughly 20 min. Disclosed here and in the lane log.
"""
(out / 'PREREG.md').write_text(TXT)
h = hashlib.sha256((out / 'PREREG.md').read_bytes()).hexdigest()
(out / 'PREREG.sha256').write_text(f'{h}  PREREG.md\n')
print('frozen', h, len(TXT.encode()), 'bytes | bands', BAND, '| mc acc', acc, 'pct', pct, 'pe14', pe14)
print('in-band seen:', inb)
print('r11:', r11)
