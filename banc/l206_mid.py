# ================= L206 MID (bridge; l206_mid.py) =========================
# The ONLY code between CERT-HEAD2 and CERT-HEAD3: the two CSR index arrays
# CERT-HEAD3's edge->CSR map needs. Transcribed from l178_tail.py's Q5 block
# (two lines) and immediately re-certified against the CSR invariant, because
# the Q5 block itself needs a settle this card does not run (anatomical leg).
csr_rows = np.repeat(np.arange(NL), np.diff(_crow))
csr_cols = _ccol
assert csr_rows.shape == csr_cols.shape == _v.shape, "csr arrays shape"
assert int(csr_rows.max()) < NL and int(csr_cols.max()) < NL
# invariant: the CSR (row, col) pairs are exactly the edge (ldst, lsrc) pairs
_k_csr0 = csr_rows.astype(np.int64) * NL + csr_cols.astype(np.int64)
_k_e0 = ldst.astype(np.int64) * NL + lsrc.astype(np.int64)
assert np.array_equal(np.sort(_k_csr0), np.sort(_k_e0)), "CSR != edge set"
assert int((csr_cols == LC_CAR).sum()) == o["csr_orientation"]["out_edges"]
assert int((csr_rows == LC_CAR).sum()) == o["csr_orientation"]["in_edges"]
log(f"[MID] csr arrays GREEN ({csr_rows.size:,} edges, orientation re-checked)")
del _k_csr0, _k_e0
