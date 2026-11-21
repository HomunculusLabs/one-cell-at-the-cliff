import io

LAB = "/home/t3rpz/critters/peabrain-lab/LAB-INTENT.md"
LOG = "/home/t3rpz/critters/peabrain/LANE-LOG.md"

lab = """
## L169 stage (a) — the gain-swap 2x2 (2026-11-20, tick 191)

Referee response card #2 (L167 issue I4). The confound: every arm is
re-gained to a matched active fraction and the FLIP arms sit +1.06-1.30%
above g_cutwA while non-flip arms sit at +-0.03%, so on the published
diagonal "carrier removed" and "slightly higher gain" are confounded.

Design: the off-diagonal of {graph} x {gain}. Two new arms, each the twin's
CSR object verbatim at the OTHER cell's bisected gain (object-identity
asserted; the only difference is the scalar GAIN):
  wAgN  = cutwA graph   @ g_cutng25 = 0.1454454553127289
  n25gW = cutng25 graph @ g_cutwA   = 0.14365819573402408
Fresh B35 (3417-3432) plus anchors 801/901; the seven inherited l150 arms
ride along (free FC anchors + a third batch each). Paired noise stream, one
X0 draw cloned per arm.

PREREG (banc/l169/PREREG.md) registered first: cells, class bands, the
C0-NT non-triviality probe (a swap arm bit-identical to its own-gain twin
= VOID), the P-af direction (deliberate off-op-point, so the L30 af
identity is re-scoped to a direction prediction), and branches D1 (graph-
tracking) / D2 (gain-tracking) / D3 (mixed, no single-word verdict).

Result: D1. Ti right-side duty on B35, n=16 per cell —
  graph wA   @ g_wA    cutwA   meanR .426 kR  4/16  PARTIAL
  graph wA   @ g_ng25  wAgN    meanR .317 kR  2/16  (no class)
  graph ng25 @ g_wA    n25gW   meanR .702 kR 15/16  SUPER [.717,.989]
  graph ng25 @ g_ng25  cutng25 meanR .753 kR 16/16  SUPER
Paired on the same batch: n25gW +.276 vs cutwA (10/16 up); wAgN -.109
BELOW cutwA (2/16 up). The whole confounded gain step, applied to the
carrier-intact graph, moves the readout the OPPOSITE way to the confound
hypothesis; removing it from the carrier-cut graph does not un-flip it.
With silW (flips at unchanged gain) the confound is bounded from both
sides: a real design asymmetry, not the mechanism.

Disclosures. (1) The swap arms are off the matched op point by only
+-.0010-.0013 in af, because the confound's own magnitude is 1.24% of
gain; the probe is therefore small BY CONSTRUCTION and exactly the size of
the thing being tested. (2) The registered PER-SEED P-af direction holds
in the batch means (wAgN .11039 > .10906 > n25gW .10802) but on only 15 of
18 seeds — per-seed af spread is the size of the gain step. Reported as
PARTIAL rather than rounded up to the mean. (3) C0-NT min separation
1.9e-2, so no dead-channel/arm-leak reading (L35/L39 class).

Free-rider pools (the inherited arms' third/ninth/tenth batches):
silW 42/48 lb .753, cutng25 140/144 lb .931, cutwA 47/160 ub .368,
eMotTop5 19/48, eMotBot5 13/48. These supersede the two-batch figures in
DRAFT §2.4; one-pooled-count-per-arm is L172, not this card.

Anchors: C0A-169 vs raw_l135 (4 shared arms x 22 keys x 2 seeds) 0.0;
FC-144 silW vs raw_l144:sil1110_wA 0.0; FC-145 both motor halves vs
raw_l145 0.0; four fresh bisects reproduce their stored gains EXACT; B35
absent from 36 stored npzs; six-way B-cert (l135 B26, l142 B29, l144 B30,
l145 B31, l148 B32, l150 B33) before any B35 read.

Build note worth carrying: l169_build.py is a count-asserted ADDITIVE
transform of l150_run.py (no arm removed, so the l131 removal plumbing
never came up). The residual scan over CODE lines needed TWO whitelist
refinements — the module docstring's continuation lines do not start with
a quote, and the `_prevs` INPUT absence list is a legitimate
cross-reference to prior runs' npzs (whitelisted by matching a pure
string-literal list element, per the l126 line-context rule). The same
scan surfaced an inherited L120-class direction bug in l150_run.py: it
checked for its OWN raw_partial.npz and then loaded l148's. Fixed in the
l169 copy (both paths l169/).

Artifacts: banc/l169/{PREREG.md, raw_l169.npz, raw_partial.npz,
anchors_run.json, results_l169.json, run.out, run.err, verdict.out,
verify_push.py}; banc/{l169_build.py, l169_run.py, l169_verdict.py}.
Paper: DRAFT.md v3.9 §2.7, extract_numbers.py (+6 l169.* keys, 65 old
byte-identical), l149_verify.py section (11), CLAIM-MAP.md block B20.
"""

logline = (
    "tick 191 | 2026-11-20 03:44-05:0x | L169 stage (a) (ideas 87: "
    "pre-posting control, gain-swap 2x2) | shipped — REGISTERED BRANCH D1: "
    "the transition tracks the GRAPH, not the gain. Off-diagonal of {graph} x "
    "{gain} on fresh B35 (3417-3432, n=16): carrier-intact graph at the HIGHER "
    "cutng25 gain (wAgN) does NOT flip (meanR .317 kR 2/16, paired dR -.109 "
    "BELOW cutwA, 2/16 up) while the carrier-cut graph at the LOWER cutwA gain "
    "(n25gW) stays SUPER (.702/15 of 16 [.717,.989], paired +.276, 10/16 up); "
    "diagonal reproduced on the same batch (cutwA PARTIAL .426/4, cutng25 "
    "SUPER .753/16). The confounded +1.24% gain step applied to the "
    "carrier-intact graph moves the readout the OPPOSITE way, and removing it "
    "from the cut graph does not un-flip it — with silW (flips at unchanged "
    "gain) the I4 confound is bounded from both sides: real design asymmetry, "
    "not the mechanism. Free-rider pools from the seven inherited arms: silW "
    "42/48 lb .753 (3 batches), cutng25 140/144 lb .931 (9), cutwA 47/160 ub "
    ".368 (10), eMotTop5 19/48, eMotBot5 13/48 (supersede the two-batch §2.4 "
    "figures; reconciliation is L172). THREE HONEST DISCLOSURES: swap arms "
    "deliberately off the matched op point (af offsets only +-.0010-.0013 "
    "because the confound itself is 1.24% of gain); the registered PER-SEED "
    "P-af direction holds in the batch means but on 15/18 seeds only (per-seed "
    "af spread ~ the gain step) and is reported PARTIAL, not rounded up; "
    "two-point probe cannot locate a threshold between .143658 and .145445 | "
    "verified: PREREG banc/l169/PREREG.md FIRST (cells, bands, C0-NT VOID "
    "rule, P-af direction, D1/D2/D3 branches); l169_run.py = count-asserted "
    "ADDITIVE transform of l150_run.py via l169_build.py (23 reps, residual "
    "scan over CODE lines CLEAN after two whitelist refinements — docstring "
    "continuation lines + the _prevs INPUT npz list by l126 line-context "
    "rule); the scan also caught an INHERITED L120-class direction bug in "
    "l150_run.py (checked its OWN raw_partial.npz, loaded l148's) — fixed in "
    "the l169 copy; GRAPH-IDENTITY asserted by python object identity (WB "
    "swap arm IS the twin's CSR) + swap-is-not-a-no-op assert; C0-NT min "
    "1.893e-02 (not a dead channel, L35/L39 class); ANCHORS ALL 0.0e+00 — "
    "C0A-169 vs raw_l135 (4 arms x 22 keys x 2 seeds), FC-144 silW vs "
    "raw_l144 sil1110_wA, FC-145 eMotTop5+eMotBot5 vs raw_l145; four fresh "
    "bisects reproduce stored g_cutwA/g_cutng25/g_eMotTop5/g_eMotBot5 EXACT; "
    "B35 absence across 36 stored npzs; SIX-WAY B-cert (l135 B26 / l142 B29 / "
    "l144 B30 / l145 B31 / l148 B32 / l150 B33 Ti tables EXACT) before any "
    "B35 value read; run 686s CPU exit 0, raw npz checkpointed BEFORE "
    "analysis; results_l169.json + verdict.out; DRAFT v3.9 §2.7 folded per "
    "the PREREG's D1 branch, numbers.json +6 l169.* keys with all 65 "
    "pre-existing keys BYTE-IDENTICAL on regen, l149_verify NEW section (11) "
    "re-derives the whole 2x2 from the RAW B35 traces with the run's own duty "
    "machinery (kR/meanR/Wilson to 1e-12), recomputes the paired legs, proves "
    "branch D1 from the measured cells rather than the stored label, and "
    "asserts the §2.7 literals verbatim; CLAIM-MAP +B20 and l161_verify "
    "bidirectional; ALL FIVE paper verifies ALL GREEN (l143/l149 11 sections/"
    "l158/l159/l161); abstract untouched so the v3.8 vocabulary freeze still "
    "holds; LAB-INTENT.md L169 appended by absolute path; LANE.md L169 kept "
    "UNCHECKED with a stage-(a)-DONE bracket + remaining stages (b)(c)(d) "
    "named (anchor region re-read clean; L169 stays first unchecked); digest "
    "committed+pushed 743d30ae..e2140144 (push exit 0 bare), remote "
    "contents-API blob sha256 ecc2c14e2a8f9c54 BYTE-IDENTICAL after "
    "base64-decode with the L169 entry present (l169/verify_push.py exit 0); "
    "GPU 0% idle at start, no live changes, no stray lab procs (run reaped, "
    "exit 0)"
)

with io.open(LAB, "a", encoding="utf-8") as f:
    f.write(lab)
with io.open(LOG, "a", encoding="utf-8") as f:
    f.write(logline + "\n")
print("LAB-INTENT appended:", LAB)
print("LANE-LOG appended:", LOG)
