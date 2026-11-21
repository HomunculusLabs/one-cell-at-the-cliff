#!/usr/bin/env python3
"""Round-2 probe 7: per-file recheck of the §2.7 / §4 control cells from RAW-derived duty rows,
both sides, plus abstract length and a scan of abstract/Discussion sentences against §2.6."""
import json, os, re, collections, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'out_duty_rows.json')))['rows']
def cell(f, arm, n16=True):
    v = sorted([r for r in R if r['file'] == f and r['arm'] == arm], key=lambda r: r['seed'])
    return v
def show(f, arms, drop_anchor=2):
    for a in arms:
        v = cell(f, a)
        if not v: print('   ', a, 'absent'); continue
        allk = (sum(x['duty07R'] >= .5 for x in v), sum(x['duty07L'] >= .5 for x in v), len(v))
        seeds = [x['seed'] for x in v]
        fresh = [x for x in v if x['seed'] >= max(seeds) - 15]      # the 16 consecutive fresh seeds
        print('    %-9s fresh-16: R %2d/%d (mean %.3f)  L %2d/%d (mean %.3f) | incl. anchors R %d/%d L %d/%d | unchopped R %d/%d'
              % (a, sum(x['duty07R'] >= .5 for x in fresh), len(fresh), np.mean([x['duty07R'] for x in fresh]),
                 sum(x['duty07L'] >= .5 for x in fresh), len(fresh), np.mean([x['duty07L'] for x in fresh]),
                 allk[0], allk[2], allk[1], allk[2], sum(x['duty14R'] >= .5 for x in fresh), len(fresh)))
print('l169 (batch J) gain-swap 2x2, draft: wA 4/16 .426 | wAgN 2/16 .317 | n25gW 15/16 .702 | cutng25 16/16 .753')
show('l169/raw_l169.npz', ['cutwA', 'wAgN', 'n25gW', 'cutng25'])
print('l169d (batch L) XOR swap, draft: cutng25 16/16 .798 | cutng25p 8/16 .477 | p25gN 1/16 .324 | n25gP 15/16 .651')
show('l169d/raw_l169d.npz', ['cutng25', 'cutng25p', 'p25gN', 'n25gP', 'cutwA'])
print('l169c2 (batch K) rewire + deletion, draft: cutwA 5/16 .452 | cutng25 15/16 .786 | rew1 16/16 .724 | rew2 1/16 .333 | rew3 3/16 .302 | hom 2/16 .301')
show('l169c2/raw_l169c2.npz', ['cutwA', 'cutng25', 'rew1', 'rew2', 'rew3', 'hom'])
print('l169b2 floor-4 dynamic arm, draft: f4wA/f4ng/f4tw all 0/16 R (.043/.081/.082); cutng25 16/16 .754; cutwA 3/16 .371; f4wA L 16/16 .698, f4ng L .289, f4tw L .560')
show('l169b2/raw_l169b2.npz', ['f4wA', 'f4ng', 'f4tw', 'cutwA', 'cutng25'])
D = open('/home/t3rpz/critters/peabrain-lab/paper/review_fable_evidence_r2/snap1/DRAFT.md.a1848d89').read()
ab = D[D.index('## Abstract (draft)') + len('## Abstract (draft)'):D.index('## 1. Introduction')]
flat = re.sub(r'\s+', ' ', ab).strip()
print('\nabstract flattened chars:', len(flat), '| words:', len(flat.split()))
for pat in ['admits no such ladder', 'does not transfer to the male', 'UNTESTED AT MATCHED FLOOR', 'converts kill to', 'We\nrelease|We release', 'private tree', 'Wet-lab predictions are NOT', 'wet-lab replication can refute',
            'in-degree', 'BROADER family', r'rank \(34/58\)|\(34/58\)', '13 entries', 'own removal mass', 'brain-and-nerve-cord']:
    for m in re.finditer(pat, D):
        ln = D[:m.start()].count('\n') + 1
        print('  line %4d: %-34s | %s' % (ln, pat[:34], re.sub(r'\s+', ' ', D[max(0, m.start() - 70):m.end() + 60])))
