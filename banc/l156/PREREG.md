# L156 PREREG — sub-band slow-line census (STATIC on stored traces, zero rollouts)

Card: quantify the L108-class finding — untruncated spectra of mm traces across
the stored lineage batches (b65 + closure arms), detrend probe (real slow line
vs trend wander), per-arm below-band fraction + slow-line frequency table.
Output = methods note + possible band-choice amendment disclosure for the draft.

## Scope (data-driven, pinned at run time into static.json:inventory)

- Files: every `raw_l*.npz` under `~/critters/peabrain-lab/banc/*/` (sorted
  glob) whose key set contains at least one `mm_b65_{seed}` trace. The file
  list itself is an input pin, recorded in static.json.
- Traces: EVERY `mm_{arm}_{seed}` key in each included file, arm parsed as
  everything before the final `_`, seed as the final token. Trace read as
  `[:WIN]` with WIN=6000 (the l154 claim-carrier form, full 60 s @ DT 0.01).
- Exclusions (registered): traces with length < WIN after slicing, or any
  non-finite sample → excluded and COUNTED in static.json:excluded (none
  expected).
- No new rollouts; no npz is modified; read-only.

## Metric machinery (VERBATIM l154_verdict.py / l94 lineage, CERT before read)

dom_freq(x, lo=0.3): mean-remove, |rfft|^2, band [lo, 10] Hz, argmax,
3-point parabola interpolation, returns (f_hat, at_floor flag = argmax at
the band floor bin). Untruncated form = lo=0.0 (DC bin has zero power after
mean removal). Frequency resolution 1/60 Hz over WIN=6000.

Per-trace reads:
- f_band, at_floor  = dom_freq(x)            # band form, l154 claim-carrier
- f_glob            = dom_freq(x, lo=0.0)    # untruncated global peak
- below_band        = f_glob < 0.3           # the L108 signature quantified
- Detrend probe: xd = x - linear fit (polyfit deg 1 over sample index);
  f_det = dom_freq(xd, lo=0.0). SURVIVE := f_det < 0.3 AND
  |f_det - f_glob| <= 1/60 + 1e-9 (one fine bin). A trend-wander-dominated
  sub-band peak collapses or drifts under linear detrend; a real slow line
  stays pinned.
- Split-half probe (secondary, convergent): f1 = dom_freq(x[:3000], 0.0),
  f2 = dom_freq(x[3000:], 0.0); AGREE := |f1 - f2| <= 1/30 + 1e-9 (one
  coarse bin; halves have 1/30 Hz resolution).

## CERT block (L85 rule — must pass BEFORE any L156 read)

1. Analytic self-test: dom_freq(sin(2π·f·t)) recovers f=0.7 and 1.4 within
   0.01 Hz (parabola code path).
2. Reproduce l154 STORED (results_l154.json) from raw_l154.npz EXACTLY:
   anchors 801/901 × {b65, off} dom_band (4 values, full float equality);
   dom_band_mean and dom_full_mean for both arms; at_floor_count {b65:0,
   off:2}; below_band_census {on:16, off:11} recomputed as count of
   f_glob<0.3 over B34=3401..3416; n_pos=6, n_neg=10, p_two_sided.
   Any mismatch = abort, no L156 number is computed.

## Aggregation (registered form)

- Per (file, arm): n traces, below-band count + fraction, detrend-SURVIVE
  count among below-band, split-half AGREE count among below-band, median
  f_glob among below-band seeds, median f_glob over all seeds. Full
  precision in static.json:per_arm; per-seed values in static.json:rows.
- Pooled b65 across NON-JITTER files (all included files except l139_j*):
  below-band k/N + Wilson 95% lb (unrounded), SURVIVE k/N, AGREE k/N,
  slow-line median. 'full' (intact-closure) arm pooled the same way over
  the files that carry it (file list recorded).
- l139_j* files pooled SEPARATELY (jittered gains are a different gain
  family; L139 law) and disclosed as their own row.
- Treatment arms are reported per-file (context) and NOT pooled across
  files: same name ≠ same gain/substrate across runs.

## Disclosure decision rule (registered BEFORE computing)

Amend DRAFT.md §4 (one sentence + numbers.json l156.* keys + l149_verify
section 8) IFF pooled b65 (non-jitter) below-band Wilson lb >= 0.5 AND
detrend-SURVIVE >= half of the pooled below-band cases. Otherwise: methods
note only (LAB-INTENT.md + static.json), draft untouched.

## Honesty clause

A degenerate census (e.g. all arms all files below-band at 100%, or zero
below-band outside l154) is itself the finding and is reported as measured.
No band redefinition is applied retroactively to any stored claim.

## ADDENDUM 1 (registered pre-read, after CERT caught a definition mismatch)

The stored l154 `below_band_census` {on:16, off:11} is reproduced ONLY by the
UN-INTERPOLATED bin argmax (no parabola): re-derived from raw_l154.npz —
off seed 3401's global peak bin sits EXACTLY at 0.3 Hz (not <0.3 → off=11)
while the interpolated f_hat is 0.298253 (<0.3 → off=12); b65=16 both forms.
The stored census was written by a post-verdict inline snippet (no script on
disk carries the key); its definition is recovered from the data, L44 rule.
Amendments: (i) the CERT leg for below_band_census uses the bin form;
(ii) every census row stores BOTH f_glob (interpolated, registered metric)
and f_glob_bin (bin form); per-arm/pooled tables report below (interpolated)
AND below_bin, and any pooled claim names boundary seeds where they differ.
No other change to the registered reads.
