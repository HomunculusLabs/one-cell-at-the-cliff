# ================= L231 HEAD (appended by l231_build.py) ==================
# Above this line, VERBATIM:
#   SLICE A = l216_static.py lines 1-1360 (a literal PREFIX of the parent,
#     cut immediately BEFORE its writer; AST-verified to hold ZERO write
#     sites), so every pin plus CERT-F4, CERT-178, CERT-GEN, CERT-205,
#     CERT-GAP, CERT-209 and the NO-OP re-run as the code that actually
#     produced l216/static.json, and PERRON / AINF / GAPS / FITS / TABLE /
#     CELLS / SUBS / LOCAL / GROUPS / side_stats_from / decorate / pi_sub /
#     build_sub / POOL_G are in memory.
# This HEAD defines ONLY the output dict P, so that the next slice (L230's own
# CERT-216 block, re-used VERBATIM) can record into it.
_T231 = time.time()
log("=" * 72)
log("[L231] does the LEFT-heavy Perron mode have a SOURCE? | NONSELECTIVE "
    "over pools x super_class x populations, BH-FDR | PREREG l231/PREREG.md")

P = dict(
    design="L231 does the LEFT-heavy Perron mode have a SOURCE? L216's "
           "unregistered finding is that the anatomical operator's dominant "
           "mode is strongly left-heavy on every beta pool cell (A_inf +0.26 "
           "to +0.44, pct_abs 1.000). This card asks it NONSELECTIVELY "
           "(Kriegeskorte step 1): the SAME per-cell-mean asymmetry of v1 "
           "over five cord pool pairs, every super_class, and the whole "
           "labelled population, on four cord operator arms plus a "
           "whole-graph arm, with BH-FDR across the entire family instead of "
           "a percentile on a preselected pool. The reconstruction caveat is "
           "the table's first two rows: per-side cell COUNT and per-side "
           "in-mass.",
    prereg="l231/PREREG.md")
P["inherited_certs"] = {k: o[k] for k in
                        ("cert_f4", "cert_178", "cert_gen", "cert_205",
                         "cert_gap", "cert_209", "gain_invariance",
                         "csr_orientation", "pools", "gains")}
P["norm_noop_max_rel_diff"] = MAXREL
