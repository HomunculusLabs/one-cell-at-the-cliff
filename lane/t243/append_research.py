#!/usr/bin/env python3
"""tick 243 — append the research digest to LANE-RESEARCH.md, asserting the
pre-existing bytes are untouched (the append-only discipline)."""
import hashlib, pathlib, sys

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain')
TGT = ROOT / 'LANE-RESEARCH.md'
SRC = ROOT / 'lane/t243/digest_entry.md'

before = TGT.read_bytes()
h_before = hashlib.sha256(before).hexdigest()
n_head_before = before.count(b'\n## ')
entry = SRC.read_bytes()

assert b'tick 243' in entry, 'entry must name its tick'
assert '2026-11-22 \u2014 tick 243'.encode('utf-8') in entry
assert b'tick 243' not in before, 'tick 243 already journalled - refusing double append'

TGT.write_bytes(before + entry)

after = TGT.read_bytes()
assert after[:len(before)] == before, 'PRE-EXISTING BYTES CHANGED'
assert hashlib.sha256(after[:len(before)]).hexdigest() == h_before
assert after[len(before):] == entry, 'appended bytes differ from source'
n_head_after = after.count(b'\n## ')
assert n_head_after == n_head_before + 1, (n_head_before, n_head_after)

print('LANE-RESEARCH.md append OK')
print(f'  pre-existing sha256 {h_before[:16]} preserved ({len(before)} bytes)')
print(f'  appended {len(entry)} bytes; ## headers {n_head_before} -> {n_head_after}')
print(f'  new total {len(after)} bytes, sha256 {hashlib.sha256(after).hexdigest()[:16]}')
