# L38 PREREG — viable-primitive-table (tick 55, 2026-11-12)

Substrate: frozen L32 regime sub verbatim (21,516 nodes / 2,977,920 edges,
g .01 / beta 2 / tau .05 / DT .01), asserted at start. CPU-only. Census
machinery = L36 verbatim (3 seeds 11/22/33, settle 400, window 600, per-CELL
u = W@X*G + I + BG this time, split by somaSide). Dynamic arms = L36 run_pair
verbatim (one generator, shared per-step noise tensor, drive AFTER settle,
dm_max + first_div every arm, af asserts both arms).

## Claim levels (pre-registered BEFORE any data)

- C0 substrate/anchors: node/edge counts exact; 0.01 < af < 0.9 both arms;
  DNg100@0.8 dm == 0.0 bit-identical 3/3; DNg95@0.2 dm > .01 3/3.
- C1 per-side census anchor (reproduces L37's dm finding STATICALLY):
  DNge059 L-side u_max <= 0 AND R-side u_max > 0; DNge046 the mirror
  (L > 0, R <= 0). If both sides agree instead, the L37 amendment is
  falsified — disclose, do not patch.
- C2 table: l38/primitives_viable.csv covers every cx_dn family (481) with
  per-side {n, u_max, u_mean, mean_X, frac_pos, verdict} joined onto
  L31 laterality/CX columns + L22 family weights + L37 dm evidence;
  verdict per side: pinned (u_max>0 & mean_X>=.95) / viable (u_max>0 &
  mean_X<.95) / need-amp (-.8<u_max<=0) / buried (u_max<=-.8) / absent.
  Gate: >=1 VIABLE side inside the flex family AND inside the jump family.
- C3 positive throttle (dose-response): DNge046-L, DNge046-R, DNg110 at
  amps {-.8,-.4,-.2,.2,.4,.8}: PASS if >=1 channel-side has dm landing
  3/3 AND |df_Ti| non-decreasing in amp over the landing grid with
  S(Tr)_a survival reported (no gate — descriptive, L33/L37 own steering).
- C4 deceleration (negative-drive side): MDN amps {-1,-2,-4,-8},
  DNg88 amps {-2,-4,-8,-12} (both ceiling-pinned per L36). PASS if at
  amp <= -u_max_side the channel shows df_Ti < 0 in >=2/3 seeds OR rhythm
  collapse (S(Tr)_a < .1 with control >= .3) = pinned types are BRAKES.
  FAIL -> "ceiling-pinned types are not deceleration levers at this
  fidelity", disclosed.
- C5 negative-floor control: the buried side of DNge046 at amp -0.8 is
  dm == 0 bit-identical 3/3 (negative drive on a below-floor population
  cannot enter — the two-sided rule's floor half).

Amendments only pre-grid; any post-hoc change disclosed in LAB-INTENT.
