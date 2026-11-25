# ================= L232 HEAD (appended by l232_build.py) ==================
# Above this line, VERBATIM:
#   SLICE A = l216_static.py lines 1-1360 (a literal PREFIX of the parent,
#     cut immediately BEFORE its writer; AST-verified to hold ZERO write
#     sites), so every pin plus CERT-F4, CERT-178, CERT-GEN, CERT-205,
#     CERT-GAP, CERT-209 and the NO-OP re-run as the code that actually
#     produced l216/static.json, and TABLE / NULLS / AINF / PERRON / CELLS /
#     SUBS / OPS / LAMS / LOCAL / GROUPS / PERM / arrivals /
#     side_stats_from / decorate are in memory.
#   SLICE B = l217_tail.py lines 245-258 (L217's `dcross`), so the crossing
#     EXISTENCE is decided by the EXPRESSION that produced l217/static.json.
# This HEAD defines ONLY the output dict P, so that the next slice (L230's
# own CERT-216 / NO-OP / CERT-AINF / CERT-217 block, re-used VERBATIM) can
# record into it.
_T232 = time.time()
log("=" * 72)
log("[L232] the CROSSING-EXISTENCE rate as the PRIMARY | plateau in D "
    "FIRST, then NONSELECTIVE BH-FDR | PREREG l232/PREREG.md")

P = dict(
    design="L232 the CROSSING-EXISTENCE rate as the PRIMARY. L217's "
           "registered timing contrast was unscoreable because its "
           "handedness null produces a measured crossing in BOTH joints in "
           "only 0.0505 of draws — a degeneracy diagnostic, post-hoc on "
           "that card. This card re-poses the event rate itself as the "
           "primary statistic on a question whose null is still unknown, "
           "and measures FIRST the one quantity that decides whether "
           "0.0505 is an effect or a truncation artifact of DMAX=8: the "
           "null's censoring rate as a function of the depth horizon D. "
           "Then the family of 12 existence tests (8 single-joint + 4 "
           "pair-level) is read NONSELECTIVELY with BH-FDR, plus a "
           "multiplicity-free omnibus over the shared draw index.",
    prereg="l232/PREREG.md")
P["inherited_certs"] = {k: o[k] for k in
                        ("cert_f4", "cert_178", "cert_gen", "cert_205",
                         "cert_gap", "cert_209", "gain_invariance",
                         "csr_orientation", "pools", "gains")}
P["norm_noop_max_rel_diff"] = MAXREL
