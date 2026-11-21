# L78 ADDENDUM 1 — verdict adjudication (registered criteria, applied honestly)

The automated gate returned CONTENT-GENERALIZES on exactly one window:
fbn_g01:duty_fast (lifts [-.123, +.123, +.246], n_up 2/3, fb mean +.082,
sham mean +.0407 <= 0.5 x .082 = .0410 — a PASS BY 0.0003). Per the L55
rule (a pre-registered conditional can pass degenerately; report which
prediction carries the information), this is adjudicated a NON-CARRYING
pass and the card verdict is MALE-ONLY. Grounds, all from stored
results_l78.json:

1. R1 sham control on the two REGISTERED-primary windows says
   PERTURBATION, not content:
   - duty_slow: fb lifts [.285, .166, .116] (3/3, mean +.189) vs donor-sham
     lifts [.277, .042, .227] (3/3, mean +.182) — sham carries 96% of the
     fb lift; fb beats sham on 1/3 seeds only.
   - duty_off: fb mean +.273 vs sham +.311 — sham HIGHER.
   - duty_fast: knife-edge above; sham's mean is exactly half; one fb seed
     is DOWN. Not a carrying window.
2. R2 rescue (Tr SL median > 0, SR >= .25 kept) passes for EVERY arm
   INCLUDING the sham (fb SL mean .290 vs sham .225 = sham carries 78%) —
   the male L66 signature was fb +.186 vs sham -.001 (clean); the female
   rescue is perturbation-carried, L67/L69 class (benefit lands on the
   marginal side regardless of content).
3. Loop content IS detectable on female — as a COST, not a benefit: the
   fb arms crash the per-seg spectral lock ratio below 0.5 x open on one
   cell each (fbn_g01 s22-seg1 .45, fbp_g01 s22-seg0 .32, fbn_g03
   s11-seg0 .37) while the donor sham passes 9/9 cells — a content-shaped
   destabilization (real echo couples to the rhythm, donor does not),
   n=3 suggestive, disclosed.
4. R3 no-harm FAILS at every dose INCLUDING the sham (Ti duty_07 drops to
   .69-.96 vs open .88-1.0; worst fbn_g01 s22 -.293) — any mech echo at
   g .1 taxes the female's bilateral-healthy Ti ceiling. Budget context:
   literal cell = 25.5% of entrain mass on female (2x male's 12.7%),
   budget-matched arm 8.5% — the tax is not a high-dose artifact.

VERDICT (amended in results_l78.json): MALE-ONLY at the registered content
bar. The female structure lift is real but PERTURBATION-carried; sign
winner matches male (negative; positive echo crashes duty_fast
[-.532, -.327, +.041]); census NOT triggered (content did not carry).

Consequence for L57 row D5: closed-loop echo cell stays MALE-ONLY; the
cross-specimen split is a MECHANISM finding — male: content (sham ~0);
female: perturbation (sham carries 78-96%) + content-shaped lock harm.
C0a open==l68 stored BIT-IDENTICAL (max|d| 0.0, 24th consecutive chain
anchor) certifies the baseline, so the female sham-sensitivity is a
substrate property, not an artifact of this run.
