#!/usr/bin/env python3
"""L183 emit -- the ONLY writer of paper/DRAFT.md during the master fold.

DRAFT.md = pinned pre-tick banner + this fold's declared banner entries
           + l183_fold.build_body(numbers.json, upto=CURRENT_STAGE).
Idempotent; l183_verify.py checks the result byte for byte.
Run: python3 paper/l183_emit.py [--check]
"""
import hashlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l183_fold as F      # noqa: E402
import l183_text as TXT    # noqa: E402

OLD_BANNER_SHA = '903835b965aa554b62a52d17776cd0611ec546fadd25dfe84a1600cd6d10f6df'
p = os.path.join(HERE, 'DRAFT.md')
live = open(p).read()
banner = live[:live.index(F.T)]
i = banner.find('\n' + TXT.BANNER_HEAD)
old = (banner[:i] if i >= 0 else banner).rstrip('\n')
assert hashlib.sha256(old.encode()).hexdigest() == OLD_BANNER_SHA, 'banner moved'
st = TXT.CURRENT_STAGE
out = old + '\n'
if st:
    out += TXT.BANNER_HEAD + ''.join(TXT.STAGE_NOTES[k] for k in range(1, st + 1))
out += '\n' + F.build_body(F.load_nums(), upto=st)
if '--check' in sys.argv:
    print('up to date' if out == live else 'STALE'); sys.exit(out != live)
open(p, 'w').write(out)
print('DRAFT.md emitted at stage %d: %d bytes, sha256 %s'
      % (st, len(out), hashlib.sha256(out.encode()).hexdigest()))
