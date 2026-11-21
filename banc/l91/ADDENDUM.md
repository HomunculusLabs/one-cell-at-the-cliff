# L91 ADDENDUM 1 (pre-verdict, before any table read) — hop arms are DEAD-CHANNEL duplicates

Trigger: run-side anchors C0P hop fd_mm == [-1] and C2 False (l91/anchors_run.json).
Diagnostic l91/l91_hopdiag.py, from stored raw + fresh static census.

## Evidence

1. fh dm vs fn == 0.0 on every seed (bit-identical, 6000 steps); fh_fb dm vs fn
   == fn_fb's dm EXACTLY (0.023488 / 0.030781 on seeds 11/501) — the volley
   changed nothing; fh_fb is fn_fb plus a null input.
2. Static census: BANC has 3 global DNge046 cells. Only ONE is in the l65/l68
   subnet, because subnet membership for DNs = receives cord input
   (dn_into = cord->DN edge present). Its cord in-edges: exactly 1. The other
   2 DNge046 cells PROJECT to cord (16 and 5 out-edges, 122/28 syn) but receive
   no cord input -> dropped by construction -> their out-edges dropped with
   them. The male hop target (DNge046 somaSide-L x2, cord-integrated) does not
   exist in this subnet.
3. The one kept cell is relu-floor buried: its subnet in-drive is dominated by
   a single inhibitory cord edge (log1p weight, xBETA=2 scaling) — u <= -amp
   at volley steps, so drive+BG <= 0 both arms, t = relu-floor identical,
   X bit-identical (L36 burial signature: un-pin needs amp > |u_mean|; the
   registered HOP_AMP .5 < |u|).
4. Contrast: DNg100 (the working entrain drive) has 621/559 out-edges, 406/395
   -> cord (5724/6776 syn) — two orders more cord command mass.

## Adjudication (L35/L36/L39/L43 class: bit-equal arm = wiring verdict)

- fh and fh_fb are EXCLUDED from the multibatch table as bit-duplicates of
  fn / fn_fb. E4's registered gates (C2 dm, fd window) FAILED for the hop —
  outcome: the male hybrid-trunk mechanism has NO female port on this subnet
  at any amp registered; that is a substrate fact, not a schedule verdict.
- Anchors re-scoped: C2 now covers the arms that claim treatment effects
  (fn_fb, fsham — both dm > 0 on all seeds; fh_fb's dm is the echo's, and its
  cells duplicate fn_fb's). hop_lands is REMOVED from the gate set and
  recorded as the dead-channel finding. C0A/C0A2/C0A3/C0P-echo/C1 unchanged.
- New assertion added to the verdict: max|mm_fh_fb - mm_fn_fb| == 0 and
  max|mm_fh - mm_fn| == 0 on every seed (duplicate-arm proof, enumerated keys).
- Everything else proceeds as registered: table = fn / fn_fb / fsham,
  Ti primary / Tr secondary, G2a-multi n=48, certification C0B.

## Follow-on lane note (not this tick)

The subnet's DN membership rule excludes pure descending command cells — a
female endgame with a real hop vocabulary needs either the DN->cord closure
rule amended (keep DNs by cord OUTPUT too — a substrate change requiring its
own re-anchored run) or a different command cell. Seeded to ideas queue, not
silently retried.

## Post-run note (verdict-time, zero reruns)

The PREREG's fallback clause "n=32 → k>=27" mis-carried the k_min: l90's
stored assert pins wilson_lb_full(28,32) >= .717 > (27,32). Caught by the
verdict's own pin assert (L44 class, 5th instance — number carried from
memory instead of the stored file). Clause moot: all 48 seeds ran, the n=48
pin (k>=41, asserted equal to l90's stored form) is what the table uses.

## Budget metric fix (verdict v2, recomputed from stored npz, zero reruns)

v1 budget divided by sin_mean only (.0251); l78's registered form divides by
the ENTRAIN DRIVE (ENT_AMP x sin_mean) -> .251, matching the registered ~.25
expectation and l78's stored 25.5% (n=3) at n=51. The C0B certification
covered the duty machinery; budget was outside it — noted as the reason it
slipped through.
