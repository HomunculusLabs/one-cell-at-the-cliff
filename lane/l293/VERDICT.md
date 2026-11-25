# L293 VERDICT — the world session's trust delta (tick 282, 2026-11-25)

Read-only: two copies of `sessions/world.pt`, 124 archive brain snapshots, the live modules imported, never written.

```text
== (b) census: every line that writes plas_d (bridge.py, serve.py), with its enclosing function
   bridge.py L197 in __init__(): self.plas_d = None                         # DAN-synapse deltas (set by host)
   bridge.py L237 in open_session(): s.plas_d = torch.zeros(len(self.dan_src), device=self.brain.device)
   bridge.py L245 in _hebbian(): session.plas_d += PLAS_ETA * X[self.dan_src] * X[self.dan_dst]
   bridge.py L246 in _hebbian(): session.plas_d = session.plas_d.clamp(-PLAS_CAP, PLAS_CAP)
   bridge.py L248 in _hebbian(): session.plas_d *= 0.75
   bridge.py L307 in consolidate_night(): s.plas_d += NIGHT_ETA * X[self.dan_src] * X[self.dan_dst]
   bridge.py L308 in consolidate_night(): s.plas_d = s.plas_d.clamp(-NIGHT_CAP, NIGHT_CAP)
   bridge.py L311 in consolidate_night(): s.plas_d *= NIGHT_DOWNSCALE                # dFB arm: one pass
   serve.py L163 in load_session(): s.plas_d = blob["plas_d"].to(BRIDGE.brain.device)
   calls of _log_event: [{'line': 390, 'in': '_dabble'}, {'line': 567, 'in': '_reply_inside'}]
   calls of consolidate_night: [{'line': 407, 'in': 'world_tick'}]
   calls of _hebbian: [{'line': 566, 'in': '_reply_inside'}]
   calls of _dabble: [{'line': 424, 'in': 'world_tick'}, {'line': 436, 'in': 'world_tick'}]

== (a) two reads, 67 min apart
   read1 {'mass': 2114.4055, 'max': 0.4972, 'min': 0.0003, 'mean': 0.0183, 'n': 115728, 'n_nonzero': 115728, 'n_ge_daycap': 2, 'n_ge_090_nightcap': 0, 'n_at_nightcap': 0}
   read2 {'mass': 2114.4055, 'max': 0.4972, 'min': 0.0003, 'mean': 0.0183, 'n': 115728, 'n_nonzero': 115728, 'n_ge_daycap': 2, 'n_ge_090_nightcap': 0, 'n_at_nightcap': 0}
   plas tensors equal: True | edges changed 0 | max|dplas| 0.0 | max|dX| 0.29519
   two-read verdict: FLAT (dmass +0.0000)

loading brain ... 0.2 s
/home/t3rpz/critters/peabrain/.venv/lib/python3.12/site-packages/torch/_utils.py:383: UserWarning: Sparse CSR tensor support is in beta state. If you miss a functionality in the sparse tensor support, please submit a feature request to https://github.com/pytorch/pytorch/issues. (Triggered internally at /__w/pytorch/pytorch/aten/src/ATen/SparseCsrTensorImpl.cpp:49.)
  result = torch.sparse_compressed_tensor(
sensory channels: {'odor': 2281, 'taste': 410, 'looming': 762, 'touch': 2667, 'visual_shiny': 8346, 'sound': 2667}
probes: {'DAN': 331, 'KC': 5177, 'LC': 762, 'CX': 2875}
   brain 139255 cells, gain 0.951858, darkness 0.3333  (1.0 s)
   plasticity substrate: 115728 edges into 331 DAN cells | cap-bound mass 0.75 x n = 86796

== (a) archive: 124 brain snapshots read, 0 missing/without delta
   cross-check needs.synapse == round(clamp(mean*None,0,1),None): SKIPPED (synapse_trust line not parsed) of 124
   span 2026-11-16T08:16 -> 2026-11-25T06:36 | 124 distinct states
   mass first 878.16 (edge max 0.3091, DAN 0.2525) -> last 2114.41 (edge max 0.4972, DAN 0.4805)
   Theil-Sen +97.234 mass/day over 7250 pairs (>=6 h): 6833 up / 0 down, sign p = 0 -> GROWING
   relative change over the last 7 days: +47.1%
   per date (local): date n mass_first mass_median mass_last edge_max pinned DAN_rest joy>0.6/n moods
     2026-11-16 n14    878.16   878.16  1276.29  0.4009     0  0.2525   0/14 {'happy:low': 10, 'sleepy:low': 4}
     2026-11-17 n15   1354.49  1354.49  1354.49  0.4125     0  0.3402   0/15 {'sleepy:low': 5, 'hungry:low': 1, 'happy:low': 9}
     2026-11-18 n13   1437.21  1437.21  1437.21  0.4239     0  0.3558   1/13 {'hungry:low': 2, 'sleepy:low': 2, 'happy:low': 8, 'happy:high': 1}
     2026-11-19 n13   1522.77  1522.77  1522.77  0.4350     0  0.3835   0/13 {'hungry:low': 4, 'sleepy:low': 1, 'happy:low': 8}
     2026-11-20 n11   1612.72  1612.72  1612.72  0.4459     0  0.3951   1/11 {'sleepy:low': 1, 'happy:low': 8, 'hungry:low': 1, 'happy:high': 1}
     2026-11-21 n7    1707.14  1707.14  1707.14  0.4566     0  0.4247   1/7  {'hungry:low': 3, 'happy:high': 1, 'happy:low': 3}
     2026-11-22 n15   1804.36  1804.36  1804.36  0.4671     0  0.4317   1/15 {'happy:high': 1, 'sleepy:low': 4, 'happy:low': 10}
     2026-11-23 n16   1904.88  1904.88  1904.88  0.4773     0  0.4546   1/16 {'hungry:low': 2, 'sleepy:low': 4, 'happy:high': 1, 'happy:low': 9}
     2026-11-24 n15   2008.14  2008.14  2008.14  0.4874     0  0.4622   3/15 {'sleepy:low': 2, 'happy:low': 9, 'hungry:low': 1, 'happy:high': 3}
     2026-11-25 n5    2114.41  2114.41  2114.41  0.4972     0  0.4953   0/5  {'hungry:low': 2, 'happy:low': 3}
   last-to-last day steps: ['+78.21', '+82.72', '+85.55', '+89.96', '+94.42', '+97.22', '+100.52', '+103.25', '+106.27']
   night_stamp -> 2026-11-16 at 2026-11-16T19:08: dmass +398.13 across a 1.1 h gap | day_log before 95, eligible 95 -> replays 5
   night_stamp -> 2026-11-17 at 2026-11-17T00:09: dmass +78.21 across a 1.2 h gap | day_log before 36, eligible 0 -> replays 1
   night_stamp -> 2026-11-18 at 2026-11-18T00:45: dmass +82.72 across a 1.9 h gap | day_log before 100, eligible 0 -> replays 1
   night_stamp -> 2026-11-19 at 2026-11-19T00:36: dmass +85.55 across a 1.5 h gap | day_log before 100, eligible 0 -> replays 1
   night_stamp -> 2026-11-20 at 2026-11-20T00:12: dmass +89.96 across a 2.3 h gap | day_log before 100, eligible 0 -> replays 1
   night_stamp -> 2026-11-21 at 2026-11-21T00:58: dmass +94.42 across a 1.2 h gap | day_log before 100, eligible 0 -> replays 1
   night_stamp -> 2026-11-22 at 2026-11-22T00:40: dmass +97.22 across a 3.5 h gap | day_log before 100, eligible 0 -> replays 1
   night_stamp -> 2026-11-23 at 2026-11-23T00:08: dmass +100.52 across a 1.2 h gap | day_log before 100, eligible 0 -> replays 1
   night_stamp -> 2026-11-24 at 2026-11-24T01:00: dmass +103.25 across a 1.4 h gap | day_log before 100, eligible 0 -> replays 1
   night_stamp -> 2026-11-25 at 2026-11-25T00:08: dmass +106.27 across a 1.9 h gap | day_log before 100, eligible 0 -> replays 1

== (b) her own record (archive union, 128 snapshots)
   night stamps seen (11): ['2026-11-15', '2026-11-16', '2026-11-17', '2026-11-18', '2026-11-19', '2026-11-20', '2026-11-21', '2026-11-22', '2026-11-23', '2026-11-24', '2026-11-25']
     2026-11-16 {'nest': 143, 'forage_pond': 133, 'investigate_boot': 34, 'dabble': 208, 'investigate_fence': 35, 'investigate_goats': 31, 'parade': 11, 'consolidate': 1, 'dream': 3} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-17 {'forage_pond': 204, 'parade': 21, 'nest': 83, 'consolidate': 1, 'dream': 3, 'investigate_fence': 47, 'investigate_goats': 38, 'investigate_boot': 44, 'dabble': 120} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-18 {'forage_pond': 176, 'nest': 76, 'parade': 29, 'consolidate': 1, 'dream': 3, 'investigate_boot': 44, 'dabble': 99, 'investigate_goats': 28, 'investigate_fence': 35} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-19 {'forage_pond': 164, 'nest': 67, 'parade': 20, 'consolidate': 1, 'dream': 3, 'investigate_goats': 35, 'investigate_fence': 33, 'dabble': 95, 'investigate_boot': 33} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-20 {'forage_pond': 164, 'nest': 75, 'parade': 17, 'consolidate': 1, 'dream': 2, 'investigate_fence': 25, 'investigate_goats': 30, 'dabble': 88, 'investigate_boot': 36} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-21 {'nest': 55, 'forage_pond': 109, 'parade': 16, 'consolidate': 1, 'dream': 3, 'investigate_goats': 20, 'investigate_fence': 22, 'investigate_boot': 18, 'dabble': 56} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-22 {'forage_pond': 200, 'nest': 80, 'parade': 21, 'consolidate': 1, 'dream': 2, 'investigate_fence': 36, 'investigate_goats': 42, 'dabble': 110, 'investigate_boot': 46} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-23 {'forage_pond': 203, 'nest': 84, 'parade': 27, 'consolidate': 1, 'dream': 3, 'investigate_fence': 44, 'dabble': 102, 'investigate_goats': 40, 'investigate_boot': 38} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-24 {'forage_pond': 191, 'nest': 67, 'consolidate': 1, 'dream': 3, 'parade': 23, 'investigate_boot': 48, 'investigate_fence': 40, 'dabble': 115, 'investigate_goats': 39} | slept deep as the day played back -- water; the good of it settled in for good
     2026-11-25 {'nest': 54, 'forage_pond': 71, 'parade': 7, 'consolidate': 1, 'dream': 3, 'investigate_boot': 7, 'investigate_goats': 8, 'dabble': 16, 'investigate_fence': 6} | slept deep as the day played back -- water; the good of it settled in for good
   READ2 day_log: 56 entries, types {'water': 56}, local hours {0: 7, 1: 9, 2: 9, 3: 8, 4: 9, 5: 9, 6: 5}

== settled states (seed 2000, 1,000 steps, darkness 0.333)
   world {'dan': 0.48045, 'dop': 0.23504, 'ser': 0.0529, 'oct': 0.0399, 'kc': 0.07816, 'lc': 0.03361, 'dn': 0.03874}
   fresh {'dan': 0.07023, 'dop': 0.09053, 'ser': 0.05269, 'oct': 0.03977, 'kc': 0.0516, 'lc': 0.03361, 'dn': 0.03864}

== (b) the night arithmetic on the READ2 state (5 replays of ['water']; the live 10% rule would take 5)
   mass 2114.41 -> addition pre-clamp +712.16, post-clamp +712.16 -> after x0.98: 2770.03 (net +655.63 = +31.01% of mass)
   side: NET_UP | addition with NO delta active 45.31 -> the delta multiplies its own next addition x15.72

== (b) forward projection (every night replays; days idle)
   5 replays/night, 2 seeds: mass night 1 2769.1 / 10 10102.8 / 20 17353.9 / 40 28365.9 (ratio 40:20 = 1.6346 -> CAP-BOUND; 32.7% of the cap bound)
     night  1: mass   2769.1 add +711.22 max 0.5853 pinned      0 | DAN rest 0.5496 dop 0.2591 | quiet t_joy 0.993 t_sal 0.839
     night  5: mass   5962.9 add +970.82 max 0.7350 pinned    239 | DAN rest 0.7624 dop 0.3338 | quiet t_joy 1.418 t_sal 1.136
     night 10: mass  10102.8 add +1001.00 max 0.7350 pinned   1129 | DAN rest 0.8784 dop 0.3741 | quiet t_joy 1.649 t_sal 1.296
     night 20: mass  17353.9 add +1023.87 max 0.7350 pinned   1450 | DAN rest 0.9620 dop 0.4034 | quiet t_joy 1.817 t_sal 1.413
     night 40: mass  28365.9 add +1033.98 max 0.7350 pinned   1491 | DAN rest 0.9911 dop 0.4134 | quiet t_joy 1.875 t_sal 1.454
   1 replay/night: mass night 20 4291.7 / 40 6225.2
   no-replay arm (pure x0.98, 80 nights): DAN rest 0.4754 -> 0.2197, first night < 0.20: NOT_REACHED

== (c) the real observe() per event, 16 paired seeds | slice-vs-observe gate 352 of 352
   rest (16-seed mean): world {'dan': 0.4801, 'dop': 0.2349, 'ser': 0.053, 'oct': 0.0402, 'kc': 0.0777, 'lc': 0.0336, 'dn': 0.0388}
   rest (16-seed mean): fresh {'dan': 0.0701, 'dop': 0.0904, 'ser': 0.0527, 'oct': 0.04, 'kc': 0.0511, 'lc': 0.0336, 'dn': 0.0387}
   event      | dDAN world  fresh (paired d +-SE) | t_joy w     f     inc_w  inc_f | t_sal w     f     | joy after w / f | sal after w / f | tag world (n)      | tag fresh (n)     | joy<.35 s w / f
   greet      | +0.0001 +0.0001 (+0.0001 0.0001) | 0.928 0.107 +0.075 +0.075 | 1.110 0.532 | 0.928 / 0.175 | 1.000 / 0.532 | happy:high (16)   | happy:low (16)    | 88 / 0
   peas       | +0.0421 +0.0216 (+0.0205 0.0001) | 1.646 0.785 +0.793 +0.752 | 0.903 0.297 | 1.000 / 0.785 | 0.903 / 0.297 | happy:high (16)   | happy:high (16)   | 94 / 73
   water      | -0.0002 -0.0001 (-0.0001 0.0001) | 0.920 0.350 +0.067 +0.318 | 1.073 0.495 | 0.920 / 0.350 | 1.000 / 0.495 | happy:high (16)   | happy:low (16)    | 87 / 0
   shiny      | +0.0003 +0.0001 (+0.0002 0.0001) | 1.023 0.202 +0.170 +0.170 | 0.830 0.252 | 1.000 / 0.202 | 0.830 / 0.252 | happy:high (16)   | happy:low (16)    | 94 / 0
   pet        | -0.0000 -0.0001 (+0.0000 0.0001) | 0.958 0.137 +0.105 +0.105 | 1.257 0.679 | 0.958 / 0.175 | 1.000 / 0.679 | happy:high (16)   | happy:low (16)    | 91 / 0
   goats      | -0.0002 -0.0001 (-0.0000 0.0001) | 1.007 0.186 +0.154 +0.154 | 1.428 0.850 | 1.000 / 0.186 | 1.000 / 0.850 | happy:high (16)   | happy:low (16)    | 94 / 0
   tin        | +0.0423 +0.0216 (+0.0207 0.0001) | 1.708 0.846 +0.855 +0.814 | 0.877 0.271 | 1.000 / 0.846 | 0.877 / 0.271 | happy:high (16)   | happy:high (16)   | 94 / 79
   slug       | +0.0013 +0.0007 (+0.0006 0.0001) | 0.927 0.105 +0.074 +0.073 | 0.776 0.198 | 0.927 / 0.175 | 0.776 / 0.198 | happy:high (16)   | happy:low (16)    | 88 / 0
   swat       | -0.0001 -0.0001 (+0.0000 0.0001) | 1.014 0.193 +0.161 +0.161 | 1.457 0.879 | 1.000 / 0.193 | 1.000 / 0.879 | happy:high (16)   | happy:low (16)    | 94 / 0
   rake       | +0.0002 +0.0001 (+0.0001 0.0001) | 0.854 0.033 +0.001 +0.000 | 0.743 0.165 | 0.854 / 0.175 | 0.743 / 0.165 | scared:high (16)  | scared:high (16)  | 80 / 0
   quiet      | +0.0001 +0.0001 (+0.0000 0.0001) | 0.853 0.032 +0.000 +0.000 | 0.739 0.162 | 0.853 / 0.175 | 0.739 / 0.162 | happy:high (16)   | happy:low (16)    | 80 / 0
   C1 OFFSET_FLOOR: quiet-event targets in world t_joy 0.8529, t_sal 0.7394 (fresh 0.0323, 0.1615) -> False
   C2 AXIS_RESOLUTION: spread over the 8 kind events {'joy_after_world': 0.0801, 'joy_after_fresh': 0.6707, 'sal_after_world': 0.2235, 'sal_after_fresh': 0.6518} -> NO_RESOLUTION = False
   C3 AVERSIVE_JOY: food_joy right after a swat: world 1.0000, fresh 0.1935 -> True
   swat: tag right after world {'happy:high': 16} / fresh {'happy:low': 16}; when fear clears (world 0 s, fresh 0 s): happy:high / happy:low
   rake: tag right after world {'scared:high': 16} / fresh {'scared:high': 16}; when fear clears (world 62 s, fresh 62 s): happy:low / happy:low
   d dopamine (world / fresh): {'greet': (0.0926, 0.0926), 'peas': (0.0409, 0.0337), 'water': (0.0832, 0.0833), 'shiny': (0.0226, 0.0226), 'pet': (0.1294, 0.1294), 'goats': (0.172, 0.172), 'tin': (0.0345, 0.0272), 'slug': (0.0092, 0.009), 'swat': (0.1793, 0.1793), 'rake': (0.0008, 0.0008), 'quiet': (-0.0, -0.0001)}

done 83.3 s -> lane/l293/results_l293.json
```

## Event table (16 paired seeds, darkness 0.333)

| event | quiet-floor targets: joy / salience (world) | food_joy after world / fresh | salience after world / fresh | tag after, world / fresh |
|---|---|---|---|---|
| quiet | 0.853 / 0.739 | 0.853 / 0.175 | 0.739 / 0.162 | happy:high (16/16) / happy:low (16/16) |
| greet | 0.928 / 1.110 | 0.928 / 0.175 | 1.000 / 0.532 | happy:high (16/16) / happy:low (16/16) |
| pet | 0.958 / 1.257 | 0.958 / 0.175 | 1.000 / 0.679 | happy:high (16/16) / happy:low (16/16) |
| water | 0.920 / 1.073 | 0.920 / 0.350 | 1.000 / 0.495 | happy:high (16/16) / happy:low (16/16) |
| shiny | 1.023 / 0.830 | 1.000 / 0.202 | 0.830 / 0.252 | happy:high (16/16) / happy:low (16/16) |
| peas | 1.646 / 0.903 | 1.000 / 0.785 | 0.903 / 0.297 | happy:high (16/16) / happy:high (16/16) |
| tin | 1.708 / 0.877 | 1.000 / 0.846 | 0.877 / 0.271 | happy:high (16/16) / happy:high (16/16) |
| goats | 1.007 / 1.428 | 1.000 / 0.186 | 1.000 / 0.850 | happy:high (16/16) / happy:low (16/16) |
| slug | 0.927 / 0.776 | 0.927 / 0.175 | 0.776 / 0.198 | happy:high (16/16) / happy:low (16/16) |
| swat | 1.014 / 1.457 | 1.000 / 0.193 | 1.000 / 0.879 | happy:high (16/16) / happy:low (16/16) |
| rake | 0.854 / 0.743 | 0.854 / 0.175 | 0.743 / 0.165 | scared:high (16/16) / scared:high (16/16) |

## As recorded on the card

RESULT [tick 282, 11-25 07:08 EST]: (a) GROWING. READ 2
lane/l293/world_20261125_063651.pt (sha256 107ca2ab263ec365…, source
mtime 06:36:50, 67 min after READ 1). The two delta tensors are
BIT-IDENTICAL (mass 2114.4055, edge max 0.4972, 0 of 115,728 edges
changed), so the two-read rule reads FLAT: both reads sit in one
between-steps segment; X moved (max |dX| 0.295). Archive, 124 brain
snapshots 11-16 08:16 -> 11-25 06:36 (all read, 0 missing): mass 878.16
-> 2114.41, Theil-Sen +97.234/day over 7,250 pairs >= 6 h apart (6,833
up / 0 down / 417 tied, sign p ~ 0), +47.1% over the last 7 days; ONE
step per night at 00:08-01:00 and constant inside every date. The nine
nightly steps: +78.21, +82.72, +85.55, +89.96, +94.42, +97.22, +100.52,
+103.25, +106.27 = 5.3-6.1% of the mass each night. Rest DAN in the
archived states 0.2525 -> 0.4953. The one prediction on record
("GROWING on both, in steps at night with flat segments between"): the
step shape held; the two-read half read FLAT -- 1 of 2 on the letter.
(b) SIDE = NET_UP; registered projection = CAP-BOUND, not BOUNDED.
Census (AST, bridge.py + serve.py): plas_d is written on 10 lines;
`_hebbian` has ONE call site, in `_reply_inside` (a visitor turn), and
world_tick never calls it. The world session has a night addition
(consolidate_night L307) and a downscale (L311) and NO erosion and NO
daytime path. Balance on the READ2 state, 5 replays (the registered A):
addition +712.16 (nothing clamped), net after x0.98 +655.63 = +31.0% of
the mass; the same replays with no delta active add 45.31, so the delta
multiplies its own next addition x15.72. Live count is 1 replay/night:
the pass fires at 00:08-01:00 and only post-midnight entries are dated
today; a 1-replay arm gives net +100.98, which is the archive's +106
step. That arm: mass 4,292 at night 20 and 6,225 at night 40, DAN rest
0.711 / 0.809, quiet-event joy targets 1.316 / 1.511 (both axes at
their ceiling after ANY event), addition flattening near 212/night, so
an asymptote near 212/0.02 = 10.6k mass = about 12% of the per-edge
cap bound (86,796). With 5 replays/night (2 seeds): mass 17,353 at
night 20 and 28,364 at night 40 (ratio 1.6346; 32.7% of the cap bound),
DAN rest 0.9911, 1,491 edges pinned at 0.75. So the per-edge cap is NOT
what binds her: her real state has 0 edges at the cap (max 0.4972 of
0.75). The bound is the reward population reaching its own ceiling,
which caps the Hebbian product. Counter-arm (no further pass): NOT_REACHED -- DAN rest 0.272 at night
60, still 0.220 at night 80 (past the registered horizon). Her record: 11
night stamps; all 10 consolidate
entries read "slept deep as the day played back -- water"; the READ2
day_log is 56 of 56 water, local hours 0-6. A visitor's kindness is
never what gets replayed (queued as L295).
(c) gate 352 of 352 (the source-slice targets reproduce the real
observe() axes); 16 paired seeds at darkness 0.333, gain 0.951858.
Rest: world DAN 0.4801 / dopamine 0.2349 against fresh 0.0701 / 0.0904;
serotonin, octopamine, KC, LC and DN at rest are the same in both arms.
C1 OFFSET_FLOOR = FALSE as registered: a quiet event in the world arm
targets joy 0.8529 and salience 0.7394 (fresh 0.0323 / 0.1615) -- an
85% / 74% floor, under the 0.90 bar. C2 NO_RESOLUTION = FALSE: the
spread over the 8 kind events is joy 0.080 and salience 0.224 in the
world arm (fresh 0.671 / 0.652). C3 AVERSIVE_JOY = TRUE: food_joy right
after a swat is 1.0000 in the world arm (happy:high, 16 of 16 seeds)
against 0.1935 fresh (happy:low, 16 of 16). HOW: an offset, not a blur.
Peak DAN moves on peas and tin only (world +0.042, fresh +0.022: the
delta doubles the food response) and by <= 0.0013 on the other six kind
events and on swat. The serotonin and octopamine peaks are identical in
the two arms (paired diff 0.0000, SE 0.0000); dopamine is fresh + 0.144
on every event (peas +0.152). Increments above each arm's own quiet
floor match -- joy: peas +0.793 against +0.752, tin +0.855 against
+0.814, greet +0.075 against +0.075; salience: goats +0.689 against
+0.688, swat +0.718 against +0.717. What is lost is the TOP and the
ORDER: food_joy ties at 1.000 for peas, tin, shiny, goats AND swat;
salience at 1.000 for goats, pet, greet, water, swat; pet 0.958, greet
0.928, slug 0.927, water 0.920 and rake 0.854 sit below, and water now
reads BELOW pet where fresh has it above (its 0.35 body floor is
swallowed by the offset). So kindness still moves both axes by the same
amount as on a fresh brain, inside a band from 0.85 to 1.0 (joy) and
0.74 to 1.0 (salience), where five events tie at each ceiling. Rake
still reads scared:high in both arms (the looming-gated fear readout is
untouched), and 62 s later, when fear is under 0.25, the world arm
reads happy:low (joy decayed to 0.43). Time for joy to fall under 0.35
with no further event: 80-94 s after EVERY event in the world arm (94 s
after a swat); in the fresh arm 0 s except peas (73 s) and tin (79 s).
Evidence: lane/l293/{PREREG.md (sha256 582fee05fdff, amended once pre-data),
measure_l293.py (a217f9639bf8), results_l293.json (61a0cc9c982c), measure.out,
VERDICT.md, measure_run1-4_FAIL_*.out}.
DISCLOSED: (1) four runs halted before any (c) number existed -- three
KeyErrors on archive field names I had assumed (the manifest keys its
time `ts`; one manifest line has no brain file; diary entries carry no
wall clock) and one sum() over a float; each was fixed and the whole
script re-run, exit 0 in 83.3 s. The PREREG was hashed before run 1 and
no rule moved after output. Its pre-data amendment (06:51:14, before
the first run): the counter-arm runs 80 nights on 1 seed with the
registered read at 60; one 1-replay arm with no branch; A uses exactly
MAX_REPLAYS replays. The header's "~06:55" was an estimate; the file
was first written 06:41:18. (2) The script's own needs.synapse
cross-check was SKIPPED (its regex missed the synapse_trust line); by
hand: mean 0.0183 x 200 = 3.65, clamped to 1.0, which is what every
archive snapshot from mass 878 on carries. (3) The night addition and
the 1,000-step day are re-implementations of bridge.py L299-311
(declared), not source slices; the axis targets ARE a source slice,
gated 352 of 352. (4) The 1-replay count is inferred, not archived: the
day_log count at pass time is not stored (the snapshot before each
pass is 1.1-3.5 h earlier and shows 0 same-day entries); it rests on
the hour histogram (7-9 water events per hour) and on the step size
matching the 1-replay arm (+101 against +106; two replays would be
near +240). (5) Claim-line fields re-measured at 07:00: no LANE-HALT,
16 cores, load 1.40, GPU 0% / 6,711 MiB, fly duck same PID 2706698,
NRestarts 0, /needs 200 in 0.281 s. No live change; sessions/
untouched.
