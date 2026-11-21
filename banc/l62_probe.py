"""L62 banc-eval slice A: format + joinability probe (READ-ONLY, no graph build).

Questions (R4 form):
  1. What do the Dataverse flat files carry (cols, sizes, snapshot)?
  2. Do annotations join the connections table (id coverage)?
  3. L32-family antagonist pools: do MN flexor/extensor vocabularies exist
     (MaleCNS names 'Ti/Tr flexor MN' etc. will NOT match FlyWire names —
     search for flexor/extensor substrings in whatever type column exists)?
  4. Pugliese triad carry-over: banc_manc_reviewed_matches.csv -> MANC type
     names IN17A001/INXXX466/IN16B036/IN19A007/IN19B012 — how many BANC
     cells join?
  5. NT predictions join coverage + mix (sanity vs 65/18/14 ACh/glut/GABA).
  6. DN vocabulary: superclass counts + DNp/DNg-style names present?
"""
import gzip
import pandas as pd
import numpy as np

D = "/home/t3rpz/critters/peabrain-lab/banc/data"

print("=" * 70)
conn = pd.read_csv(f"{D}/dv_11842997", compression="gzip")
print("connections_princeton:", conn.shape)
print(conn.columns.tolist())
print(conn.head(3).to_string())

print("=" * 70)
ann = pd.read_csv(f"{D}/dv_11845666", sep="\t", low_memory=False)
print("codex_annotations_flat_table:", ann.shape)
print(ann.columns.tolist()[:40])

ci = pd.read_csv(f"{D}/dv_11844865", sep="\t", low_memory=False)
print("cell_info:", ci.shape)
print(ci.columns.tolist()[:40])

tax = pd.read_csv(f"{D}/dv_11845667", sep="\t", low_memory=False)
print("annotations_taxonomy:", tax.shape)
print(tax.head(10).to_string())

print("=" * 70)
nt = pd.read_csv(f"{D}/dv_11837016", low_memory=False)
print("banc_neurotransmitter_prediction:", nt.shape)
print(nt.columns.tolist())

mm = pd.read_csv(f"{D}/dv_11837145", low_memory=False)
print("banc_manc_reviewed_matches:", mm.shape)
print(mm.columns.tolist())
print(mm.head(3).to_string())
