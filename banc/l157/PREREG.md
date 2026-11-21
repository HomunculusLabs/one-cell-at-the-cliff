# L157 PREREG — slow-line-carrier census (STATIC, zero rollouts)

Card: LANE.md ideas 83, L157. Question: WHO oscillates at the ~.100 Hz
sub-band line L156 found in 518/518 b65 mm traces?

## Data (pinned, read-only)

- `l154/raw_l154.npz` (B34): arms {b65, off} x seeds {801, 901, 3401-3416}.
- `l150/raw_l150.npz` (B33): arms {full, cutwA, cutng25, silW, eMotTop5,
  eMotBot5, b65} x seeds {801, 901, 3301-3316}.
- Channels per (arm, seed): 20 antagonist pools
  Ti_{fL,fR,eL,eR}, Tr_{fL,fR,eL,eR} (flexor/extensor x side),
  Ta_{aL,aR,bL,bR}, Pr_{aL,aR,bL,bR}, Sr_{aL,aR,bL,bR} (antagonist
  token pairs x side, L101 vocabulary) + mm + xm, all (6000,) at DT .01.
- Card named "mech, dng100" channels: NOT present in these npz (card
  guess); the non-pool extras are mm + xm + scalar af. Disclosed.
- Reads: POOLS + mm + xm on arms b65 (both files, 36 traces/channel
  pooled) and off (l154 only, 18). Other l150 arms out of scope (this
  card is the BASELINE carrier question).

## Machinery (verbatim l156_static.py)

WIN 6000, DT .01, HALF 3000, FBIN 1/60, HBIN 1/30; dom_freq interp form
(lo param) + bin_argmax un-interpolated form (dual, ADDENDUM-1 form);
linear-detrend survive; split-half agree at HBIN tolerance; Wilson lb
Z=1.959963984540054.

## Registered metrics

Per (file, arm, channel): n, below (f_glob<0.3 interp), below_bin (dual),
survive (detrend), agree (split-half), med_f_below.
Per (file, arm, channel) pooled over both files for b65:
  pooled_below/k, wilson_lb, med_f_glob.
Slow-band power share: ps in [0.05, 0.25] Hz / ps total (mean-removed),
per channel (b65 pooled mean over 36).
Antagonist slow phase: for the 10 same-joint-side pairs
(Ti_fL/Ti_eL, Ti_fR/Ti_eR, Tr_fL/Tr_eL, Tr_fR/Tr_eR,
Ta_aL/Ta_bL, Ta_aR/Ta_bR, Pr_aL/Pr_bL, Pr_aR/Pr_bR,
Sr_aL/Sr_bL, Sr_aR/Sr_bR): per seed, bin b* = argmax of the pair's
mean power spectrum restricted to [0.03, 0.3) Hz; phase = angle of
cross-periodogram at b* (X_e * conj(X_f)); antiphase-ish if phase in
[90, 270] deg. Report per-pair circular mean + n_antiphase/18 per file.

## Registered claim classes (decision)

A channel SHOWS the line (per file, arm b65) if below >= 14/18 AND
below_bin >= 14/18 (dual form, both must hold).
- C1 CLOCK-WIDE: >= 9 of 10 antagonist PAIRS have both members showing.
- C2 READOUT-ONLY: mm and/or xm show, but pools showing <= 10 of 20.
- C3 SHEET-SPECIFIC: 3..20 pools show, C1/C2 not met — name which.
- C4 LINE ABOVE BAND IN POOLS: pools' dominant component is NOT below
  band in most pools (below <= 10/20) while mm is (518/518 pin): the
  slow line is an AGGREGATION emergent (mm-only) — mechanism note, not
  a per-pool oscillator claim.
Pooled b65 (36 traces/channel) Wilson lb reported per channel.

## Draft-fold decision rule (registered)

Fold ONE observation sentence into DRAFT §4 iff exactly one claim class
C1-C4 is met on BOTH files independently (b65 arm) with the class-defining
census at Wilson lb >= 0.5 pooled. Otherwise: LAB-INTENT observation
only, no draft edit. No new mechanism claims either way (observation
fold, L149 precedent).

## CERT chain (before any new read)

CERT-1 (l154 anchors): verbatim l156_static.py block — dom_freq band
anchors 801/901 == results_l154.json, band/full means to 1e-12, below
census {16,11}, signs {6+,10-}.
CERT-2 (mm==l156 rows): my per-channel machinery run on mm must
reproduce l156/static.json per_arm rows for l154|b65, l154|off,
l150|b65 EXACTLY (n, below, below_bin, survive, agree, med_f_below,
med_f_all) — proves the pool reader is the census reader.
CERT-3 (analytic): dom_freq self-test 0.7/1.4 Hz; cross-phase estimator
self-test on synthetic f=+0.1 rad-shifted sinusoids (recover shift).

## Output

`l157/static.json` (full precision) + printed pool table. Deterministic,
no RNG, zero rollouts, read-only over npz/json.

## ADDENDUM 1 (pre-read, registered before any census output)

PREREG pinned l150 seeds as {801, 901, 3301-3316} — WRONG: 3301-3316 is
B31/L145 vocabulary. Actual l150/raw_l150.npz grid (derived from npz key
scan, all 7 arms identical): {801, 901, 3365-3380} (B33). Census reads
the ACTUAL grid; no other change. L44 instance #11 (seed pin re-derived
from stored artifact, not log memory).
