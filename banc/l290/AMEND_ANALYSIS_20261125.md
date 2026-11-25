
# AMENDMENT — analysis-script coverage fix (tick 278, 2026-11-25)

What happened: the FIRST execution of final_l290.py (sha256 43fef618a2143a1490d368e59a0c85e4484d00cbcf4965189a26831723adf9da,
kept byte-identical as `final_l290_pre_fix_tick278.py`) halted on its own line-77 assertion with
`AssertionError: (0, 'gc30', 801)` and wrote 0 bytes of results (no results_l290*.json exists;
the halt is in the verification block, 110 lines before the first effect is computed, after the
per-worker gates and before the cutwA gate).

Diagnosis (measured, t278_keys.py over all twelve npz files): the harness's `arms_for(seed)`
(edge_run_l290.py L1334) runs `cutwA` on the 3 anchor seeds + the 16 seeds (19) and EVERY other
arm on the 16 seeds only. That is the A1 structure too (l240/raw, xm: cutwA 19 seeds, e4/e12/
... 16). The analysis script wrongly demanded every arm on all 19. The certified sibling
l240/final_a2.py L86-91 checks its arms over `seeds` (16) only. PREREG s2: "Seeds 3769-3784
(16), anchors first: 801, 901 (bit), 3545 (L175 reproduction)" -- the data is as registered;
the script's check was wrong, not the run.

The fix (lines 75-82): the key-presence loop now takes ANCH + seeds for cutwA and seeds for
every other arm, and a NEW stricter clause asserts no non-control arm carries an anchor-seed
trace (exact coverage). No statistic, branch, margin, set or readout line is touched; PREREG.md,
sets.json and edge_run_l290.py are unedited (their shas are asserted at the top of every run).

Recorded by the launching shell before the second execution:
- pre-fix sha256 43fef618a2143a1490d368e59a0c85e4484d00cbcf4965189a26831723adf9da (kept as final_l290_pre_fix_tick278.py)
- post-fix sha256 685ad9e8f7420dc1dd2fd9b78d0f0f0e9838819a237a687d261cb4b3e67ecaca
- changed lines: 6 added / 1 removed; PREREG.md / sets.json / edge_run_l290.py untouched
- second execution launched 2026-11-25 00:12:51 EST

## Second halt and the key-collision fix (tick 278)

The SECOND execution (final_l290.py sha256 685ad9e8f7420dc1dd2fd9b78d0f0f0e9838819a237a687d261cb4b3e67ecaca, output kept as final_run_attempt2.out) halted at line 95, again in
verification and before any effect was computed: `AssertionError: ('an arm name is owned by two workers', 'gc30')`.

Diagnosis (read from the source, no data involved): the script keyed A1's l240 workers 0-2 AND the L290 workers 0-2 into the
SAME dicts (done / Z / X / anch), so the L290 load overwrote A1's; and the A2 workers (l240 ids 3-9) were never loaded although
`single` reads all 69 single-edge arms. The harness and the data are unaffected: PREREG.md, sets.json and edge_run_l290.py are
unedited and their shas are asserted at the top of every run.

The fix is bookkeeping only: L290 workers are stored under key w + 10 (file names keep the true id), A2 arrays are loaded, and the
gates were STRENGTHENED on what is read (xmean finite; EVERY cutwA array of each L290 worker -- control-cell, pool and
mm/xm/af/xwin traces -- compared bit-exact with A1's STORED l240 arrays, where the pre-fix gate compared 76 control-cell traces
of L290 w1/w2 against L290 w0 and never against A1). MECHANICAL CHECK, asserted by the fixer before writing: everything from the
FINAL banner to the end of the file (BASE, F, flip, contrast, the three metric branches, the verdict order, companions d/e/f and
the predictions) is BYTE-IDENTICAL to the tick-277 original. Diff versus the original: 45 lines added, 14 removed, all above the FINAL banner.

- pre-fix sha256 43fef618a2143a1490d368e59a0c85e4484d00cbcf4965189a26831723adf9da (final_l290_pre_fix_tick278.py = tick 277 original)
- post-fix sha256 7919933c735d0dc654c097279bd273b08265d8008a0a1f6666956f0401ee9316 (this file)
- third execution launched by the shell that appended the timestamp below

```diff
--- final_l290_pre_fix_tick278.py (tick 277 original)
+++ final_l290.py (tick 278, fixed)
@@ -37,5 +37,11 @@
 EXIT = {w: _exit(w) for w in W}
-FIN = tuple(w for w in W if EXIT[w] is not None)
-assert all(EXIT[w] == '0' for w in FIN), ('a finished L290 worker exited non-zero', EXIT)
-FINAL = len(FIN) == 3
+FIN0 = tuple(w for w in W if EXIT[w] is not None)
+assert all(EXIT[w] == '0' for w in FIN0), ('a finished L290 worker exited non-zero', EXIT)
+FINAL = len(FIN0) == 3
+# tick 278 FIX (bookkeeping only, no statistic touched): L290 workers are stored under key w + 10.
+# The pre-fix script keyed them 0-2 -- the SAME keys as A1's l240 workers -- so the L290 load
+# OVERWROTE A1's done/Z/X/anch, the "cutwA == A1 stored" gate could only ever compare L290
+# w1/w2 with L290 w0, and A1's arms fell out of W_OF (halt 2: "an arm name is owned by two
+# workers: gc30"). File names keep the true worker id (k - 10); statistics read by key only.
+FIN = tuple(w + 10 for w in FIN0)
 seeds = list(range(3769, 3785))
@@ -50,5 +56,6 @@
     anch[w] = read(l240, f'anchors_w{w}.json')
+for w in A1W + A2W_ALL:      # tick 278 FIX: A2 workers' arrays are READ below (`single`, all 69 edges)
     Z[w], X[w] = np.load(l240 / f'raw_w{w}.npz'), np.load(l240 / f'xm_w{w}.npz')
 for w in FIN:
-    armsj[w], done[w], anch[w] = read(out, f'arms_w{w}.json'), read(out, f'done_w{w}.json'), read(out, f'anchors_w{w}.json')
+    armsj[w], done[w], anch[w] = read(out, f'arms_w{w - 10}.json'), read(out, f'done_w{w - 10}.json'), read(out, f'anchors_w{w - 10}.json')
     assert armsj[w]['stage'] == 'L290-B' and armsj[w]['prereg'] == psha and armsj[w]['sets_sha'] == ssha, (w, 'stage / shas')
@@ -60,3 +67,3 @@
         assert all(r['csr_index'] >= 0 and r['effective_weight'] != 0 for r in e['removed']), (w, a, 'removed entry')
-    Z[w], X[w] = np.load(out / f'raw_w{w}.npz'), np.load(out / f'xm_w{w}.npz')
+    Z[w], X[w] = np.load(out / f'raw_w{w - 10}.npz'), np.load(out / f'xm_w{w - 10}.npz')
 for w in A1W + FIN:
@@ -75,4 +82,10 @@
     for a in d['arms']:
-        for s in ANCH + seeds:
+        # tick 278 FIX (coverage check only, no statistic touched): the harness runs cutwA on
+        # anchors + seeds (arms_for, edge_run_l290.py L1334) and every other arm on the 16
+        # seeds only -- the same npz structure as A1 (l240) and final_a2.py's own form.
+        for s in (ANCH + seeds if a == 'cutwA' else seeds):
             assert f'xmean_{a}_{s}' in X[w].files and f'af_{a}_{s}' in Z[w].files, (w, a, s)
+            assert bool(np.isfinite(X[w][f'xmean_{a}_{s}']).all()), (w, a, s, 'xmean finite')   # tick 278 FIX
+        if a != 'cutwA':   # exact coverage: no stray anchor-seed trace on a non-control arm
+            assert not any(f'xmean_{a}_{s}' in X[w].files or f'af_{a}_{s}' in Z[w].files for s in ANCH), (w, a, 'stray anchor key')
     if w in FIN:
@@ -85,2 +98,17 @@
                 assert d['gain'][a] == STORED_G, (w, a, 'fixed twin gain')
+for w in A2W_ALL:             # tick 278 FIX: A2 arrays are read by `single` -> the same finite gates on what is read
+    d = done[w]
+    assert d['seeds'] == ANCH + seeds and d['ctr_cells'] == CTR, (w, 'A2 seeds / ctr cells')
+    assert d['secs'] < 1700, (w, 'A2 hard stop', d['secs'])
+    _an2 = read(l240, f'anchors_w{w}.json')
+    assert _an2['c0a135_pass'] and _an2['c0a175_pass'], (w, 'A2 anchors')
+    for k in Z[w].files:
+        pp = k.split('_')
+        if len(pp) == 3 and pp[0][1:].isdigit() and pp[2].isdigit():
+            x = Z[w][k]; assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (w, k); trace_count += 1
+        elif len(pp) == 4 and pp[0] in ('Ti', 'Tr', 'Ta', 'Sr', 'Pr'):
+            x = Z[w][k]; assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (w, k); pool_count += 1
+    for a in d['arms']:
+        for s in (ANCH + seeds if a == 'cutwA' else seeds):
+            assert bool(np.isfinite(X[w][f'xmean_{a}_{s}']).all()), (w, a, s, 'A2 xmean finite')
 W_OF = {}
@@ -93,3 +121,3 @@
 pools = read(l240, 'pools_w0.json')
-assert all(pools['pools'] == read(out, f'pools_w{w}.json')['pools'] for w in FIN), 'pool index sets differ'
+assert all(pools['pools'] == read(out, f'pools_w{w}.json')['pools'] for w in FIN0), 'pool index sets differ'
 ALLSEEDS = ANCH + seeds
@@ -100,6 +128,9 @@
 # ---------------- gate: every L290 worker's cutwA == A1's stored cutwA, exactly ----------------
+raw_all = [k for k in Z[0].files if '_cutwA_' in k]       # tick 278 FIX: PREREG s2 = xmean + raw POOL traces + af
 gate = {w: dict(
-    xmean=bool(all(np.array_equal(xm(w, 'cutwA', s), xm(0, 'cutwA', s)) for s in ALLSEEDS)),
-    raw=bool(all(np.array_equal(Z[w][k], Z[0][k]) for k in raw_cut)),
-    af=bool(all(np.array_equal(np.atleast_1d(Z[w][f'af_cutwA_{s}']), np.atleast_1d(Z[0][f'af_cutwA_{s}'])) for s in ALLSEEDS))) for w in FIN}
+    xmean=bool(all(np.array_equal(xm(w + 10, 'cutwA', s), xm(0, 'cutwA', s)) for s in ALLSEEDS)),
+    raw=bool(all(np.array_equal(Z[w + 10][k], Z[0][k]) for k in raw_cut)),
+    raw_all=bool(set(k for k in Z[w + 10].files if '_cutwA_' in k) == set(raw_all)
+                 and all(np.array_equal(np.atleast_1d(Z[w + 10][k]), np.atleast_1d(Z[0][k])) for k in raw_all)),
+    af=bool(all(np.array_equal(np.atleast_1d(Z[w + 10][f'af_cutwA_{s}']), np.atleast_1d(Z[0][f'af_cutwA_{s}'])) for s in ALLSEEDS))) for w in FIN0}
 assert all(all(g.values()) for g in gate.values()), ('VOID: an L290 cutwA trace != A1 stored', gate)
@@ -115,5 +146,5 @@
 base = dict(card='L290 stage B', prereg_sha256=psha, sets_sha256=ssha, harness_sha256=sha(out, 'edge_run_l290.py'), seeds=seeds,
-            workers={w: dict(arms=done[w]['arms'], secs=done[w]['secs']) for w in FIN}, exit_codes={w: EXIT[w] for w in W},
-            anchors={w: dict(c0a135_max=anch[w]['c0a135_max'], c0a175_max=anch[w]['c0a175_max']) for w in FIN},
-            cutwA_gate={w: gate[w] for w in FIN}, trace_arrays_verified=trace_count, pool_traces_verified=pool_count,
+            workers={w: dict(arms=done[w + 10]['arms'], secs=done[w + 10]['secs']) for w in FIN0}, exit_codes={w: EXIT[w] for w in W},
+            anchors={w: dict(c0a135_max=anch[w + 10]['c0a135_max'], c0a175_max=anch[w + 10]['c0a175_max']) for w in FIN0},
+            cutwA_gate={w: gate[w] for w in FIN0}, cutwA_arrays_compared=len(raw_all), trace_arrays_verified=trace_count, pool_traces_verified=pool_count,
             gains={a: done[W_OF[a]]['gain'][a] for a in W_OF}, sets={a: GROUPS[a] for a in GROUPS})
@@ -123,3 +154,3 @@
     atomic('results_l290_partial.json', base)
-    print('PARTIAL: workers', FIN, 'of 3 | exit', EXIT, '| cutwA gate', gate)
+    print('PARTIAL: workers', FIN0, 'of 3 | exit', EXIT, '| cutwA gate', gate)
     print('no effect read; branches NOT read; missing arms', base['missing_arms'])
```
third execution 2026-11-25 00:22:02 EST nice -n 15 timeout 540, final_l290.py sha256 7919933c735d0dc654c097279bd273b08265d8008a0a1f6666956f0401ee9316

## Third halt (synthetic self-check) and fix 4: the tail rule of `contrast` (tick 278)

THIRD execution (sha256 7919933c735d0dc654c097279bd273b08265d8008a0a1f6666956f0401ee9316, output final_run_attempt3.out) passed every
load/coverage/cutwA-vs-A1 gate and halted at `flip self-check (sign reversal)` with 0 bytes of stdout: the check fed the
15-ones-and-a-minus-one vector an expectation (2/65536, 1.0) that holds only for a 16/16 vector. Synthetic input, no data.
The exact values for a 15/16 vector are 34/65536 and 17/65536 (C(16,0)+C(16,1) = 17 sign vectors a side); the check now uses
-_p for the reversal and asserts those two derived values for _m. The function `flip` is untouched (sha before fix 4: efd5d1b8f41a328acf10fa775f6e1f5a98d20c9fb3c07fe7003eb02205b65702).

FIX 4, found by reading the statistics section against the PREREG BEFORE any effect was printed (stdout of all three halts: 0 bytes).
PREREG s4/s5: A = sign(E_U) * D; "the one-sided tail p_up for D > 0"; EXCEEDS iff A >= eps and p_up <= 0.01; IS EXCEEDED BY iff
A <= -eps and (1 - p_up) <= 0.01. The tick-277 code chose the tail by the sign of A instead of testing A itself, so for a used-set
with E > 0 a comparator that significantly exceeded it read WITHIN, IS_EXCEEDED_BY could not fire, and the metric still counted
towards ESCAPE. The two rules give IDENTICAL p_adv and IDENTICAL EXCEEDS whenever A > 0 (so raw leg, random leg, SUPPORT and
WINS cannot differ); they differ only when A <= -eps is significant. p_two, D and SE are identical by construction (asserted per
contrast). The tick-277 status is still computed for every contrast and STORED (`tick277_status`), with the list of contrasts whose
status changed and the verdict the old rule would have printed (`amendment_tick278`), so nothing of the pre-fix reading is hidden.
Also made verbatim: the per-metric label CONFOUNDED_BY_E14 now requires NO e14-containing comparator (PREREG s5 (b) sentence);
it never changes the verdict (a CONFOUNDED metric cannot win under either wording).

Diff of fix 4: +22 / -7 lines.
- pre-fix sha256 43fef618a2143a1490d368e59a0c85e4484d00cbcf4965189a26831723adf9da (final_l290_pre_fix_tick278.py = tick 277 original)
- post-fix-4 sha256 e85b1f50f8289aa6ccd9ed03396f7926a0762c3b4171e3d766cc3d6dc87f30a1
- fourth execution launched by the shell that appended the timestamp below

```diff
--- final_l290.py before fix 4 (sha efd5d1b8f41a)
+++ final_l290.py after fix 4 (sha e85b1f50f828)
@@ -231,6 +231,14 @@
     f = flip(P[u] - P[x]); adv = sg * f['D']
-    p_adv = f['p_up'] if sg * f['D'] > 0 else f['p_down']
-    p_opp = f['p_down'] if sg * f['D'] > 0 else f['p_up']
-    st = 'EXCEEDS' if (adv >= eps and p_adv <= 0.01) else ('EXCEEDED_BY' if (adv <= -eps and p_opp <= 0.01) else 'WITHIN')
-    return dict(advantage=adv, in_F=adv / F, D=f['D'], SE=f['SE'], p_two=f['p_two'], p_adv=p_adv, p_opp=p_opp, status=st)
+    # tick 278 FIX (PREREG s4/s5 verbatim): the tested statistic is the ADVANTAGE A = sign(E_u) * D and
+    # "the one-sided tail p_up" is P(null >= A). The tick-277 lines chose the tail by the sign of A, so
+    # for a used-set with E > 0 a comparator that significantly EXCEEDED it read WITHIN (IS EXCEEDED BY
+    # = A <= -eps and 1 - p_up <= 0.01 could not fire) and such a metric still counted as ESCAPES.
+    g = flip(sg * (P[u] - P[x]))
+    assert abs(g['D'] - adv) < 1e-15 and abs(g['p_two'] - f['p_two']) < 1e-12 and abs(g['SE'] - f['SE']) < 1e-15, (u, x, 'symmetry')
+    p_adv, p_opp = g['p_up'], g['p_down']
+    st = 'EXCEEDS' if (adv >= eps and p_adv <= 0.01) else ('EXCEEDED_BY' if (adv <= -eps and (1 - p_adv) <= 0.01) else 'WITHIN')
+    _pa, _po = (f['p_up'], f['p_down']) if adv > 0 else (f['p_down'], f['p_up'])       # the tick-277 rule, RECORDED, never read
+    st277 = 'EXCEEDS' if (adv >= eps and _pa <= 0.01) else ('EXCEEDED_BY' if (adv <= -eps and _po <= 0.01) else 'WITHIN')
+    return dict(advantage=adv, in_F=adv / F, D=f['D'], SE=f['SE'], p_two=f['p_two'], p_adv=p_adv, p_opp=p_opp, status=st,
+                tick277_status=st277, tie_mass=p_adv + p_opp - 1)
 
@@ -253,3 +261,3 @@
         label = 'WINS'
-    elif raw_ok and all_pos and n_exc >= 4:
+    elif raw_ok and all_pos and n_exc >= 4 and not e14c:       # tick 278 FIX: PREREG s5 (b) "has NO e14-containing comparator"
         label = 'CONFOUNDED_BY_E14'
@@ -300,3 +308,7 @@
 effr = [len([j for j in GROUPS[a] if j not in N0]) for a in RAND]
-res = dict(base, status='FINAL', verdict=VERDICT, K=K, eps=eps, F=F, floorN=floorN, per_metric=MET,
+_sts277 = [r['tick277_status'] for M in MET.values() for r in M['comparators'].values()]
+VERDICT277 = 'ESCAPE' if all(s == 'WITHIN' for s in _sts277) else VERDICT        # EXCEEDS is identical under both rules
+res = dict(base, status='FINAL', verdict=VERDICT,
+           amendment_tick278=dict(contrasts_status_changed=[f'{m}:{c}' for m in MET for c, r in MET[m]['comparators'].items()
+                                                     if r['status'] != r['tick277_status']], verdict_under_tick277_rule=VERDICT277), K=K, eps=eps, F=F, floorN=floorN, per_metric=MET,
            instrument=dict(random_clears=clear, n_clear=n_clear, bar=K, with_e14=with14, without_e14=free14,
@@ -325,2 +337,4 @@
 print('FINAL: cutwA gate', all(all(g.values()) for g in gate.values()), '| traces', trace_count, 'pools', pool_count, '| F', F, 'eps', eps)
+print('AMEND tick278: contrasts whose status the PREREG-exact tail rule changed', len(res['amendment_tick278']['contrasts_status_changed']),
+      res['amendment_tick278']['contrasts_status_changed'], '| verdict under the tick-277 rule', VERDICT277)
 print('VERDICT', VERDICT, '| WINS', win, '| CONFOUNDED_BY_E14', conf, '| escapes all', escape_all)
@@ -331,3 +345,4 @@
     for c, r in M['comparators'].items():
-        print(f"      vs {c:6s} adv {r['advantage']:+.3e} ({r['in_F']:+.2f} F) p_adv {r['p_adv']:.5f} p_opp {r['p_opp']:.5f} {r['status']}")
+        print(f"      vs {c:6s} adv {r['advantage']:+.3e} ({r['in_F']:+.2f} F) p_adv {r['p_adv']:.5f} p_opp {r['p_opp']:.5f} {r['status']}"
+              + (f"  [tick277 rule read {r['tick277_status']}]" if r['status'] != r['tick277_status'] else ''))
 print('random clears', n_clear, 'of 15 (bar', K, ') | with e14', [int(clear[a]) for a in with14], '| without', n_free_clear, 'of', len(free14))
```
fourth execution 2026-11-25 00:26:35 EST nice -n 15 timeout 540, sha e85b1f50f8289aa6ccd9ed03396f7926a0762c3b4171e3d766cc3d6dc87f30a1
fourth execution: exit 0 in 3.6 s at 2026-11-25 00:31:12 EST, 5434 B of stdout (final_run.out), results_l290.json sha256 83498d7c933414c7ee02f8ff088bcf62d59ec1bac16bc5ff5d274ff3a0628f5f. Verdict NO_DECISION; the tail-rule fix moved 2 of 18 contrasts (crofts:r30k1, crofts:r30k3 WITHIN -> EXCEEDED_BY); verdict under the tick-277 rule, stored in the results: NO_DECISION.
