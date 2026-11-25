#!/usr/bin/env python3
"""Tick-284 ledger line: appends ONE `shipped --` line to LANE-LOG.md.
Idempotent: guarded on a line that starts `tick 284 | ` and holds `shipped`.
The duck readings in the line are PROBED here (never retyped); a failed
probe writes UNVERIFIED into that slot instead of a number."""
import datetime, pathlib, re, subprocess, sys
from zoneinfo import ZoneInfo

LOG = pathlib.Path(__file__).resolve().parent.parent.parent / 'LANE-LOG.md'
before = LOG.read_text(encoding='utf-8')
if re.search(r'^tick 284 \| .*shipped —', before, flags=re.M):
    print('LANE-LOG.md: tick-284 shipped line ALREADY PRESENT -- not appended')
    sys.exit(0)


def probe(cmd, timeout=8):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ''
    except Exception:                                  # noqa: BLE001
        return ''


unit = probe(['systemctl', '--user', 'show', 'critter-bill-fly.service',
              '-p', 'ActiveState', '-p', 'MainPID', '-p', 'NRestarts'])
kv = dict(l.split('=', 1) for l in unit.splitlines() if '=' in l) if unit else {}
pid, nr, state = kv.get('MainPID', '?'), kv.get('NRestarts', '?'), kv.get('ActiveState', '?')
code = probe(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
              '--max-time', '5', 'http://192.168.50.58:3122/needs'])
duck = (f'fly duck {state}, PID {pid}, NRestarts {nr}, /needs {code}'
        if code else f'fly duck {state}, PID {pid}, NRestarts {nr}, /needs UNVERIFIED (probe failed)')
now = datetime.datetime.now(ZoneInfo('America/New_York'))
end = now.strftime('%H:%M')

LINE = r'''tick 284 | 2026-11-25 09:23-@@END@@ | research (hour-09 field scan) | shipped — arXiv FLY FIELD QUIET again (the core's only in-window hit 2611.23320 was already digested at t167; FlyWire 12 parsed / 0 in-window; connectome-constrained 14/0; NeuroMechFly 0; flyGNN 0) and the yield is OFF arXiv again. Hour 09 at wakeup = RESEARCH tick (clock-derived, LANE.md L59-L70); no LANE-HALT. SCAN: 24 angles (1 control + 5 core + 18 ROTATED) via lane/t284/angles.py, which builds every query through urllib.parse.quote (arxiv skill law); control cat:q-bio.NC parsed:14 in-window:14 so the pipeline was VALIDATED before any zero was scored; **0 angles errored** at 6.5 s spacing (tick-243 law); window 14 days, cutoff 2026-11-11, which OVERLAPS tick 260's window because the 11-24 hour-09 and hour-21 windows have no research line (disclosed in the CLAIM); raw lane/t284/scan.out. ROTATION, aimed at the two open cards: A = the BOUND of a Hebbian accumulator (L293/L295; 8 angles: Hebbian+homeostatic, synaptic scaling, reward-modulated, metaplasticity, three-factor, sliding threshold, weight normalization, runaway) → 0 in-window on all eight; B = REPLAY SELECTION (L295; Drosophila sleep+memory, dopamine+sleep+consolidation, replay+sleep+selection, synaptic tagging) → 0 in-window on all four; tick-233 law a FOURTH time, both literatures are old and journal-hosted, and LANE-RESEARCH.md held 0 prior digest on the plasticity-theory terms (BCM, Turrigiano, three-factor, reward-modulated, runaway) -- its adjacent entry is the tick-6 R3 rules, see FOLDED; C = L294's matched-comparison heterogeneity (Shapley, component ablation, matching, effect heterogeneity, lesion compensation) → 0 RELEVANT, and one angle (`matching AND observational AND balance`) returned 8 in-window hits that were ALL homonyms (object detection, a factory simulator, world models, black-hole horizons, a compiler, stellarator plasmas): an in-window count is not a yield. READS, depth disclosed: (1) Matsuno ... Saitoe, PLOS Biol 24(4):e3003752, full-text page as head 10,259 + tail 3,478 of 17,318 chars -- aged flies' engrams answer shock-paired, unpaired AND novel odors because dopaminergic (PPL1) activity during consolidation is too high; causal both ways (inhibition of PPL1 rescues the aged defects; activating PPL1 in YOUNG flies after training lowers LTM and raises generalization); readout = a lost DIFFERENTIAL (a2sc-MBON response, CS+ vs other odors). It answers half of L293's owner question from the field's side: the signature of that regime is a lost trained-vs-untrained MARGIN, and L293 registered only the spread among KIND events → folded into L295 as a MARGIN companion (kind minus quiet, world.pt vs fresh; DESCRIPTION on the already-read arms per L214, a branch needs unread seeds). (2) Yan ... Griffith, Liu, eLife 14:RP104862 (version of record 23 Sep 2026), ABSTRACT + eLife assessment only: disrupting PAM-DAN basal activity in the consolidation window, by briefly ACTIVATING or INHIBITING the two DPM neurons, each impairs 24 h LTM and fragments sleep, and sleep rescue restores LTM → the biology holds a resting TONE around a set point, which favours L295's resting-rate homeostat over a mass cap as the candidate (does not decide the owner question). (3) Hassan, Ho & Aslam, bioRxiv 2026.11.23.768740, ABSTRACT in full: a no-learning lookup of a BANC neuron's partners through its MATCHED FlyWire neuron reaches MRR 0.18-0.48 (true partner vs 100 degree-proportional non-partners) and per-region graph models beat it in all 12 regions → seeded L296 (ideas 134): measure partner-set overlap at matched cells on OUR two graphs, since every cross-specimen claim (L154, L233, L65) leans on that join. (4) Elmeligy, Pashine & Schwarz, arXiv 2611.22070, ABSTRACT only: continual learning in a spring network is a per-bond dominance measurement that active learning biases → a candidate bound for L295, NOT registered. NOT GROUNDED: Zenke, Poole & Ganguli 2017's bound on total update -- both full-text routes dropped the derivation (the PDF extract holds no bound passage in 45,544 chars, ar5iv returned an image shell) -- journaled as REMEMBERED-not-read. FOLDED: LANE-RESEARCH.md tick-284 entry (726 → @@RLINES@@ lines, header present exactly once); a bracketed amendment on L295 (anchor re-read, line breaks intact); an ADJACENT-PRIOR-ENTRY paragraph in the digest tying L293's unbounded accumulator back to tick-6 rule 3 (the x0.98 pass was adopted as "preserves ranking, prevents saturation"; L293 measured the last clause FALSE, and a x0.98 factor holds an accumulator still only once the nightly add has fallen to 2% of its mass); L296 appended under ideas 134 (unchecked 72 → 73; the live thread's head stays L294, still tick 283's: banc/l294 untouched, build queue untouched). VERIFIED: lane/t284/verify_quotes.py re-checked @@NQ@@ quoted strings against THIS run's fetched text (@@NOK@@/@@NQ@@ found; numbers pinned to the page they come from, because a bare number matches any cache file); lane/t284/fixdigest.py applied 8 in-place corrections to the digest with exact-once guards; fold.py read-back equal on both files and idempotent on re-run (ALREADY PRESENT x2); @@DUCK@@. BUILD: three of my own scripts halted at 0 bytes of output before any write (fold.py twice on path/name errors -- a wrong parent dir, then a name my own fix deleted; adjacent.py once on a quote check that did not allow for the journal's line wraps) and the audit script needed two needle corrections before its zero meant anything (a citation's spacing, and the pruned web_* archives are JSON-escaped, so a literal backslash-n is a line break); the first draft of the digest, written after a context compaction, carried a depth figure typed from memory, two quotations whose first letter I had lower-cased, a transliterated greek letter and a model sentence quoted without its authors' hedge -- all caught by the quote audit and corrected in place. Publish digest not touched (research tick, same as tick 260). Next: L294 (build tick).
'''

# facts read from the artifacts, not typed
res = pathlib.Path(__file__).resolve().parent.parent.parent / 'LANE-RESEARCH.md'
rlines = res.read_text(encoding='utf-8').count('\n')
LINE = (LINE.replace('@@END@@', end).replace('@@RLINES@@', str(rlines))
        .replace('@@DUCK@@', duck))
for tok in ('@@NQ@@', '@@NOK@@'):
    pass
LINE = LINE.replace('@@NQ@@', sys.argv[1] if len(sys.argv) > 1 else '?')
LINE = LINE.replace('@@NOK@@', sys.argv[2] if len(sys.argv) > 2 else '?')
assert '@@' not in LINE, [t for t in re.findall(r'@@[A-Z]+@@', LINE)]
assert LINE.startswith('tick 284 | 2026-11-25 09:23-') and LINE.count('\n') == 1 and LINE.endswith('\n')
with LOG.open('a', encoding='utf-8') as f:
    f.write(LINE)
after = LOG.read_text(encoding='utf-8')
assert after == before + LINE
print(f'LANE-LOG.md: appended {len(LINE)} chars; last line starts: {after.splitlines()[-1][:60]!r}; end {end}; {duck}; research lines {rlines}')
