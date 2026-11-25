# ================= L233 HEAD (appended by l233_build.py) ==================
# Above this line, VERBATIM:
#   SLICE A = l216_static.py lines 1-1360 (a literal PREFIX of the parent,
#     cut immediately BEFORE its writer; AST-verified to hold ZERO write
#     sites), so every pin plus CERT-F4, CERT-178, CERT-GEN, CERT-205,
#     CERT-GAP, CERT-209 and the lam1 NO-OP re-run as the code that actually
#     produced l216/static.json, and GROUPS / PERM / LOCAL / OPS / LAMS /
#     PERRON / AINF / INMASS / SUB / SUBS / side_stats_from / decorate /
#     asym / pct_up / mot_rows / mgi are in memory.
#   SLICE B = l217_tail.py lines 245-258 (L217's `dcross`), required by
#     SLICE C's CERT-217.
# This HEAD defines ONLY the output dict P, so the next slice (L230's own
# CERT-216 / NO-OP / CERT-AINF / CERT-217 block, re-used VERBATIM) can
# record into it.
_T233 = time.time()
log("=" * 72)
log("[L233] does the DESTINATION GEOMETRY explain the asymptote? | "
    "in-degree / in-mass / mode-residual / leverage | PREREG l233/PREREG.md")

P = dict(
    design="L233 does the destination geometry explain the asymptote? "
           "L217 refuted the SOURCE-population account BY HOMOGENEITY, so "
           "the leftward drift is a property of the pools' OWN in-wiring. "
           "A_inf = asym(per-cell means of v1) over a joint's pool cells, "
           "so this card asks what distinguishes the LEFT pool cells from "
           "their RIGHT homologs in v1: (a) raw in-degree, (b) in-MASS, "
           "(c) position in the Perron mode independent of both (the "
           "residual after regressing log v1 on log in-mass within pool), "
           "or (d) a small number of high-leverage cells. The card's own "
           "escape is registered: if (a)/(b) explain it, the whole A_inf "
           "family demotes to a description of the pools' in-mass "
           "asymmetry, which L205 already measured.",
    prereg="l233/PREREG.md")
P["inherited_certs"] = {k: o[k] for k in
                        ("cert_f4", "cert_178", "cert_gen", "cert_205",
                         "cert_gap", "cert_209", "gain_invariance",
                         "csr_orientation", "pools", "gains")}
P["norm_noop_max_rel_diff"] = MAXREL
