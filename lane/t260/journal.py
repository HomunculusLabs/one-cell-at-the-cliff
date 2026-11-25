#!/usr/bin/env python3
"""Tick-260 research journal: append lane/t260/digest.md to LANE-RESEARCH.md.

Guards (house discipline, tick 252 pattern):
  - pre-existing bytes asserted unchanged by PREFIX compare after the write,
  - 'tick 260' asserted ABSENT beforehand (HEADER-scoped: the '## ' line),
  - idempotent: refuses to run twice,
  - shas + char counts printed for the log line.
"""
import hashlib, pathlib, sys

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain')
TGT = ROOT / 'LANE-RESEARCH.md'
SRC = ROOT / 'lane' / 't260' / 'digest.md'

pre = TGT.read_text()
add = SRC.read_text()

HEADER = '## 2026-11-23 — tick 260 (research:'
assert HEADER in add, 'digest is missing its own header'
if HEADER in pre:
    print('ALREADY APPENDED — refusing (idempotent guard)')
    sys.exit(0)

# the digest must not accidentally carry another tick's header
assert add.count('## ') == 1, f'digest has {add.count("## ")} headers, expected 1'

pre_sha = hashlib.sha256(pre.encode()).hexdigest()[:16]
TGT.write_text(pre + add)
post = TGT.read_text()

assert post.startswith(pre), 'PREFIX COMPARE FAILED — pre-existing bytes moved'
assert post[len(pre):] == add, 'appended bytes differ from source'
assert post.count(HEADER) == 1, 'header not present exactly once'
post_sha = hashlib.sha256(post.encode()).hexdigest()[:16]
print(f'OK  sha {pre_sha} -> {post_sha}  chars {len(pre)} -> {len(post)}  '
      f'added {len(add)}')
