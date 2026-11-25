#!/usr/bin/env python3
"""Tick-284 fold: append the research digest to LANE-RESEARCH.md and the
new card section to LANE.md. IDEMPOTENT, guarded on HEADERS (the L227
lesson: a bare-token guard fires on the text that proves the thing).

  lane/digest.md -> LANE-RESEARCH.md   unless its header line is present
  lane/t284/ideas.md -> LANE.md        unless '- [ ] L296.' is present

Never renumbers or edits an existing item. Prints what it did; exits
non-zero if a guard or a post-write read-back fails.
"""
import pathlib, sys

LAB = pathlib.Path(__file__).resolve().parent
LANE = LAB.parent.parent          # lane/t284 -> peabrain/
LOG_RESEARCH = LANE / 'LANE-RESEARCH.md'
LANE_MD = LANE / 'LANE.md'
assert LOG_RESEARCH.is_file() and LANE_MD.is_file(), LANE
HERE = LAB

HDR = '## 2026-11-25 — tick 284 (research:'
CARD = '- [ ] L296.'


def append_once(target: pathlib.Path, block: str, guard: str, label: str):
    before = target.read_text(encoding='utf-8')
    if guard in before:
        print(f'{label}: ALREADY PRESENT (guard "{guard[:40]}") -- not appended')
        return False
    if not block.startswith('\n'):
        sys.exit(f'{label}: block does not start with a blank line')
    with target.open('a', encoding='utf-8') as f:
        f.write(block)
    after = target.read_text(encoding='utf-8')
    if after != before + block:
        sys.exit(f'{label}: READ-BACK MISMATCH after append')
    if after.count(guard) != 1:
        sys.exit(f'{label}: guard count {after.count(guard)} != 1 after append')
    print(f'{label}: appended {len(block)} chars; bytes {len(before.encode())} -> '
          f'{len(after.encode())}; guard present exactly once')
    return True


digest = (HERE / 'digest.md').read_text(encoding='utf-8')
ideas = (HERE / 'ideas.md').read_text(encoding='utf-8')

n0 = LANE_MD.read_text(encoding='utf-8').count('- [ ] ')
append_once(LOG_RESEARCH, digest, HDR, 'LANE-RESEARCH.md')
append_once(LANE_MD, ideas, CARD, 'LANE.md')
n1 = LANE_MD.read_text(encoding='utf-8').count('- [ ] ')
print(f'LANE.md unchecked: {n0} -> {n1} (expected +1)')
if n1 != n0 + 1 and CARD not in LANE_MD.read_text(encoding='utf-8'):
    sys.exit('unchecked count did not move by one')
