#!/usr/bin/env python3
"""Tick 287 close-out for L294. (A) LANE.md: flip the box, add the RESULT note, register L297.
(B) LANE-LOG.md: the SHIPPED line. Byte-exact and STRUCTURAL (no retyped anchors: the card is
located by its checkbox prefix and by the next card's prefix), once-only guards, idempotent."""
import subprocess
import sys

LANE = "/home/t3rpz/critters/peabrain/LANE.md"
LOG = "/home/t3rpz/critters/peabrain/LANE-LOG.md"
PR_SHA = "77b3dfb022d1a0b8c1d862ebfb5b000514a015af52933014c89d65ff5f7a5a37"
RES_SHA = "3b6d85df32f710ba68ac3692f8f94a01d1691a71cb705cbb001f6d7fed4378b1"

NOTE = """      RESULT [tick 287, 11-25 13:10-13:2x EST]: A_GAIN_DELTA_MEDIATED /
      A_POOL_SPECIFIC, G_SHIFT_ON -- resting on TWO HAIRLINE legs. On the 33
      bisected arms the effect ranks with the arm's own gain delta within
      size stratum: +0.70 (q 0.0001). The removed effective-weight sum
      CARRIES TOO: +0.55 (q 0.0042, positive in all 3 strata) -- against the
      registered P5 ("weight does not carry"). The non-pool cells move with
      the gain delta as well (+0.52, q 0.006) and pool-minus-common keeps
      97% of it (+0.68). Out of sample (L290's 18): +0.45, p 0.088 -- misses
      0.05 (P1 false) and its n-11 stratum is REVERSED (-0.37). Twins: 6 of
      7 move in dgain's direction, S +1.63 F, p 6/128 = 0.047 (one pattern
      from TWIN_FAIL). Sign-split and distinct-targets covariates are
      degenerate by definition on this carrier. Predictions 4/6. L227
      stands: dgain needs the bisection (mechanism probe); EW_SUM is the
      pre-rollout predictor. Evidence banc/l294/ (PREREG 77b3dfb022d1a0b8,
      results 3b6d85df32f710ba; gates G1-G5 pass before any test; a second
      run reproduces every stored number). Next: L297."""

CARD = """- [ ] L297. TWO PREDICTORS, ONE SET (static re-analysis of the STORED
      L290/L291 arrays; PREREG first; zero rollouts). L294 (tick 287) read
      A_GAIN_DELTA_MEDIATED on two hairline legs: on 33 bisected arms the
      effect tracks the gain delta within size stratum (+0.70, q 0.0001),
      it tracks the removed effective weight too (+0.55, q 0.0042, against
      L294's own P5), out of sample (L290's 18) the gain leg is +0.45 at
      p 0.088 with the n-11 stratum REVERSED (-0.37), and the twins moved
      in dgain's direction 6 of 7 (6/128). OPEN: (a) EW_SUM is confounded
      with e14 membership (with / without means on the 33: +5.64 / +0.13 F
      at n 11, +9.72 / +0.22 at 30, +8.54 / -0.73 at 46) -- is there a
      continuous drive effect once e14 is in the model? (b) the two
      predictors are near-orthogonal (post-hoc strat-rho +0.22): register
      a within-stratum rank model with EW_SUM, DGAIN and E14 together and a
      label permutation for each partial, and say BEFORE scoring what 10-11
      arms per stratum can resolve (if nothing can, name the instrument
      that would). (c) The n-11 reversal: six arms -- NOT SHOWN, or a real
      size dependence? (d) A set-level ordering usable before any rollout:
      does EW_SUM alone rank the 33 well enough to pick its top half
      (hit rate against the label null)? Mind L227: DGAIN needs the
      bisection. Verify: banc/l297/ PREREG sha + results + VERDICT.md with
      the registered table; no live changes."""

txt = open(LANE, encoding="utf-8").read()
lines = txt.split("\n")
n0 = len(lines)
has_note = "RESULT [tick 287, 11-25" in txt
has_297 = any(l[:10] in ("- [ ] L297", "- [x] L297") for l in lines)
if has_note and has_297:
    print("LANE.md: ALREADY DONE (note + L297 present)")
elif has_note != has_297:
    sys.exit("HALF-APPLIED LANE.md: note %s / L297 %s -- repair by hand" % (has_note, has_297))
else:
    idx = [k for k, l in enumerate(lines) if l.startswith("- [ ] L294. ")]
    if len(idx) != 1:
        sys.exit("HALT: open L294 card line count = %d" % len(idx))
    i = idx[0]
    lines[i] = "- [x] " + lines[i][6:]
    j = i + 1
    while not lines[j].startswith("- ["):
        j += 1
    k = j - 1
    while not lines[k].strip():
        k -= 1
    if not lines[k].strip().endswith("prediction of an unseen set."):
        sys.exit("HALT: L294 card's last line is not the expected sentence: %r" % lines[k])
    lines[k + 1:k + 1] = NOTE.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    lines += [""] + CARD.split("\n") + [""]
    open(LANE, "w", encoding="utf-8").write("\n".join(lines))
    print("LANE.md written: lines %d -> %d" % (n0, len(lines)))

after = open(LANE, encoding="utf-8").read().split("\n")
i = [k for k, l in enumerate(after) if l.startswith("- [x] L294. ")][0]
print("CHECK box line %d: %s" % (i + 1, after[i][:60]))
for l in after:
    if l.startswith("      RESULT [tick 287"):
        print("CHECK note first line:", l.strip()[:70])
print("CHECK note lines:", sum(1 for l in after if "L297." in l or "pre-rollout predictor" in l))
print("CHECK L294 box open elsewhere:", sum(1 for l in after if l.startswith("- [ ] L294. ")))
print("CHECK L295 still open:", sum(1 for l in after if l.startswith("- [ ] L295. ")))
t = [k for k, l in enumerate(after) if l.startswith("- [ ] L297. ")]
print("CHECK L297 at line", [x + 1 for x in t], "| last 2 non-empty lines:", [x[:60] for x in after if x.strip()][-2:])

# ---------------------------------------------------------------- (B) journal
log = open(LOG, encoding="utf-8").read()
tag = "tick 287 | 2026-11-25 13:05-13:"
if tag in log:
    print("JOURNAL: ALREADY PRESENT")
else:
    now = subprocess.run(["date", "+%H:%M"], capture_output=True, text=True,
                         env={"TZ": "America/New_York", "PATH": "/usr/bin:/bin"}).stdout.strip()
    duck = subprocess.run(
        ["bash", "-c", "systemctl --user show critter-bill-fly.service -p MainPID -p NRestarts "
         "| tr '\\n' ' '; curl -s -o /dev/null -w 'HTTP %{http_code} in %{time_total}s' "
         "--max-time 8 http://192.168.50.58:3122/needs"], capture_output=True, text=True).stdout.strip()
    line = (
        "\ntick 287 | 2026-11-25 13:05-%s | L294 (WHAT PREDICTS A WEIGHT-MATCHED SET'S EFFECT; static "
        "re-analysis of the STORED L290 + L291 arrays; PREREG first; zero rollouts) | shipped — "
        "**A_GAIN_DELTA_MEDIATED / A_POOL_SPECIFIC, G_SHIFT_ON, resting on TWO HAIRLINE legs -- and the "
        "removed effective weight carries too, against this tick's own registered P5.** "
        "Ticks 283 and 285 both died on HTTP 429 before any PREREG existed; re-took under the 2 h rule "
        "(tick 285's claim was more than 2 h old at 13:05). Hour 13 at wakeup = build tick; no LANE-HALT; "
        "GPU 0%% / 7.6 GiB. "
        "PREREG banc/l294/PREREG.md frozen BEFORE any covariate was scored against an effect (sha256 %s); "
        "one DISCLOSED post-hash edit: the header's freeze time 13:24 -> 13:10, made before the analysis "
        "script existed (PREREG_FREEZE_NOTE.md carries both hashes; no design text changed). "
        "REGISTERED FAMILY (within-size-stratum midrank Spearman, label permutation B 20,000 PCG64(29400), "
        "BH q 0.10 over m 6): T1 E x DGAIN on L290's 18 (out of sample) +0.4476 p 0.08785 (n11 -0.37 "
        "REVERSED, n30 +0.94, n46 +0.77); T2 on all 33 bisected arms +0.7000 q 0.00015; T3 E x EW_SUM "
        "(sum of log1p syn over the removed edges) +0.5455 q 0.0042, positive in all 3 strata; T4 twins "
        "S +1.63 F, 6 of 7 concordant, p 6/128 = 0.047 (discordant pair e27); T5 non-pool cells x DGAIN "
        "+0.5182 q 0.0059 = the global-shift confound is ON; T6 pool-minus-common x DGAIN +0.6788 "
        "q 0.00015 = 97%% of T2 survives. "
        "PREDICTIONS 4/6: P2 P3 P4 P6 held; P1 FALSE (T1 misses 0.05); P5 FALSE (weight DOES carry). "
        "Hairline: T1's q 0.0878 against a 0.10 bar; T4 clears by 0.4 of a pattern (one more -> B "
        "GAIN_DELTA_MARKER; T1 +0.013 higher -> C WEIGHT_CARRIES). Stable under both neighbours: T2 T3 T5 "
        "T6. Degenerate by definition on this carrier: sign-split (0 of 69 negative weights), distinct "
        "targets (== n within a stratum; 0 of 69 menu targets inside the pool union). Mirror read before "
        "T3: rho(EW_SUM, SYN) 0.972. POST-HOC, unregistered, never gating (posthoc_check.out): the two "
        "predictors are near-orthogonal, strat-rho(EW_SUM, DGAIN) +0.215; L291's 'negative dgain -> "
        "floor' out of sample 6 of 9 against 1 of 9 (Fisher 0.050). L227 stands: dgain needs the "
        "bisection = mechanism probe; EW_SUM is the pre-rollout predictor. "
        "VERIFIED: l294_final.py (om, nice +15, timeout 1700) exit 0 through its last write with gates "
        "G1 G2 G2b G3 G4 G5 PASS before any test was computed -- every E and every per-seed value "
        "re-derived from the stored xmean arrays (max deviation 0.0 over 37 arms), the prior cards' "
        "anchors reproduce (L291's +0.82 = +0.8214 ordinal; 0.5892857143; 0.4286057679; L291 cell means "
        "to 0.005 F); results_l294.json sha256 %s; a second run reproduced the first on every stored "
        "leaf (0 differing); parents untouched (results_l290 83498d7c933414c7, results_l291 "
        "a8b80c85491417a1, mtimes unchanged). "
        "BUILD: the VERIFICATION script was the buggy one, twice -- math.copysign(dE, dgain) is |dE| "
        "with dgain's sign, not sign(dgain)*dE (it reported 24/128), and its Fisher test sat on the "
        "wrong margin (0.002); enumerating the 128 patterns by hand on its own printed magnitudes "
        "confirmed the analysis (6/128, 0.050) -- both fixed before anything was reported. "
        "LANE.md: L294 box flipped + RESULT note + L297 registered by a structural byte-exact edit "
        "with once-only guards. No live change; sessions/ untouched; fly duck %s. Next: L295 (slice 2), "
        "then L296, L297."
    ) % (now, PR_SHA, RES_SHA, duck)
    open(LOG, "a", encoding="utf-8").write(line)
    a = open(LOG, encoding="utf-8").read()
    print("JOURNAL appended at %s: 'tick 287 |' now occurs %dx; duck: %s" % (now, a.count("tick 287 |"), duck))
