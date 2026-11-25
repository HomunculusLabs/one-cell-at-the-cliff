# PREREG freeze note (tick 287, 2026-11-25)

- First hash of `PREREG.md`: `1d8d72969e88a0a53a465d4b9698a4394fe7f4011d6dfbe929e6bad08c3cbd6a` (9,845 B),
  written at 13:10:15 EST. Its header line said "Frozen 2026-11-25 13:24 EST", a time AHEAD of the
  clock (the freeze time had been estimated, not read).
- The header was corrected to 13:10 EST and the file re-hashed. No design text changed (one token on
  line 2) and NO test had been computed between the two hashes: the analysis script did not exist yet
  (`ls l294/` shows survey2.out / survey3.out / survey4.out only at that moment).
- The binding hash is the one in `PREREG.sha256`; the script (G5) refuses to run without it.
