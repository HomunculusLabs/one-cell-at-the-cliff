#!/usr/bin/env python3
"""L201 stage-10 builder: cuts every OLD side from the stage-9 built body
(so no old side is typed), pairs it with the NEW template in stage10_new.py,
and writes the declared edits E90-E94 + STAGE_NOTES[10] into
paper/l183_text.py, bumping CURRENT_STAGE 9 -> 10.  Idempotence guard: refuses
to run if the ledger already carries stage 10.
"""
import os, re, sys
LAB = os.path.expanduser('~/critters/peabrain-lab')
PAPER = os.path.join(LAB, 'paper')
sys.path.insert(0, PAPER)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l183_fold as F          # noqa: E402
import l183_text as TXT        # noqa: E402
import stage10_new as N        # noqa: E402

assert TXT.CURRENT_STAGE == 9 and not any(e['stage'] == 10 for e in TXT.EDITS), \
    'ledger already at stage 10'
nums = F.load_nums()
body = F.build_body(nums, upto=9)
live = open(os.path.join(PAPER, 'DRAFT.md')).read()
assert live[live.index(F.T):] == body, 'live draft is not the stage-9 build'


def para_with(text, needle):
    flat = lambda s: re.sub(r'\s+', ' ', s)
    hits = [p for p in text.split('\n\n') if flat(needle) in flat(p)]
    assert len(hits) == 1, (needle, len(hits))
    p = hits[0] + '\n\n'
    assert body.count(p) == 1, needle
    return p


def flat1(s):
    return re.sub(r'\s+', ' ', s).strip()


# E90 -- section 2.5, whole section
i, j = body.index('### 2.5 Which clock'), body.index('### 2.6 The dose cliff')
old_25 = body[i:j]
# E91 -- abstract paragraph
a0 = body.index('## Abstract (draft)\n\n') + len('## Abstract (draft)\n\n')
a1 = body.index('\n\n## 1. Introduction')
old_abs = body[a0:a1]
e60 = next(e for e in TXT.EDITS if e['id'] == 'E60-abstract-yardstick')
assert e60['new'].count(N.ABS_OLD_SENT) == 1
new_abs = e60['new'].replace(N.ABS_OLD_SENT, N.ABS_NEW_SENT)
assert F.wrap(F.render(e60['new'], nums)) == old_abs, 'E60 render != live abstract'
# E92 -- section 1 paragraph
old_intro = para_with(body, N.INTRO_OLD_SENT)
new_intro = flat1(old_intro).replace(N.INTRO_OLD_SENT, N.INTRO_NEW_SENT) + '\n\n'
assert N.INTRO_NEW_SENT in new_intro
# E93 -- section 4 timing-attribution card
old_lim = para_with(body, 'Timing attribution: which clock the shared timing')
# E94 -- the Discussion mechanism paragraph
old_disc = para_with(body, 'The readout rises because the two motor pools share')
assert flat1(N.DISC).startswith(flat1(old_disc).split(' Whether the shared timing')[0])

EDITS = [
    ('E90-sec25-tone-phase', old_25, N.SEC25, True,
     'L201 tone-phase fold: section 2.5 replaces "unresolved" with the resolved '
     'statement; the L186 run is kept as the first run and its open status is '
     'stated as superseded by L197b (no internal rhythm, elevation signed by '
     'tone phase) and L199 (tone shifted half a period at identical gates: '
     'causal branch met, sign refinement not met; asymmetric extensor-carried '
     'rotation, descriptive)'),
    ('E91-abstract-timing', old_abs, new_abs, True,
     'L201 tone-phase fold: the abstract\'s "Which clock the timing follows is '
     'unresolved" becomes the resolved statement (abstract length stays under '
     '1,920)'),
    ('E92-intro-timing', old_intro, new_intro, True,
     'L201 tone-phase fold: section 1 echoes the resolved timing statement'),
    ('E93-limit-timing', old_lim, N.LIMIT, True,
     'L201 tone-phase fold: the section-4 timing card states what remains '
     'open (one causal batch, one shift, onset vs in-pulse phase not '
     'separated, removed-graph K touches zero) instead of "unresolved"'),
    ('E94-discussion-two-pool', old_disc, N.DISC, True,
     'L201 tone-phase fold: the Discussion mechanism paragraph names the '
     'shared stimulus (the drive phase) and gains the asymmetric two-pool '
     'picture (base co-move; carrier removed: extensor-carried rotation, no '
     'antiphase), stated as description, not mechanism'),
]

NOTE10 = '''> Stage 10 (L201 tone-phase fold, owner-directed, 2026-11-22): 2.5 is
> retitled and rewritten around the resolved timing statement. The gate-jitter
> run of batch Q stays as the first run, its open status superseded by a
> powered second run (no internal rhythm; the deletion elevation is signed by
> the tone's phase) and a causal third run (the tone shifted half a period at
> identical gates inverts the elevation; registered causal branch met, sign
> refinement not met). The asymmetric two-pool picture enters 2.5 and the
> Discussion as description: the base pools peak together, and with the
> carrier removed the extensor's phase rotates by about a third of a period
> while the flexor's holds. Abstract, section 1 and the section-4 timing card
> follow. Four keys entered numbers.json first (l197b.timing, l199.causal,
> l199.phase, l199.meta).
'''

src_path = os.path.join(PAPER, 'l183_text.py')
src = open(src_path).read()


def q(s):
    assert "'''" not in s
    return "'''" + s.replace('\\', '\\\\') + "'''"


block = ['', '# =========================================================== STAGE 10 ======',
         '# L201 tone-phase fold (owner-directed, 2026-11-22; banc/l201_BRIEF_fold.md,',
         '# banc/l201_worklog.md).  Produced by banc/l201/build_stage10.py: every old',
         '# side is cut from the stage-9 body, every new number is a placeholder on',
         '# l197b.timing / l199.causal / l199.phase.']
for eid, old, new, wrap, reason in EDITS:
    block.append("rep(%r, 10,\n    %s,\n    %s,\n    %r,\n    wrap=%r)\n"
                 % (eid, q(old), q(new), reason, wrap))
block = '\n'.join(block) + '\n'
anchor = '# ------------------------------------------------------------------ banner'
assert src.count(anchor) == 1 and src.count('CURRENT_STAGE = 9\n') == 1
src = src.replace(anchor, block + anchor)
src = src.replace('CURRENT_STAGE = 9\n', 'CURRENT_STAGE = 10\n')
doc_old = '''    lowercase pass over twelve passages of 2.6-2.12 and section 3.
'''
assert src.count(doc_old) == 1
src = src.replace(doc_old, doc_old + '''  10 tone-phase fold (L201, owner-directed): 2.5 resolved (L197b + L199
    supersede L186's open status), the asymmetric two-pool picture in 2.5 and
    the Discussion, with the abstract, section 1 and section 4 following.
''')
tail = '''> no number added and no section renumbered. No key entered numbers.json.
\'\'\',
}'''
assert src.rstrip().endswith(tail), 'STAGE_NOTES tail moved'
src = src.rstrip()[:-1] + '    10: ' + q(NOTE10) + ',\n}\n'
open(src_path, 'w').write(src)
print('stage 10 written: %d edits; old sides cut from the stage-9 body' % len(EDITS))
