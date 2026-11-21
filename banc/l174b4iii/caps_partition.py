"""T11: PARTITION the 179 distinct all-caps tokens of §1-§5 into the classes
stage (b4-iii-c) will act on. DERIVATION ONLY — zero draft bytes change here.
House form pinned from §5 Discussion (authored under T8 born-clean, 0 caps):
the outcome classes are written LOWERCASE as defined terms ("the super class",
"intermediate"), never as caps emphasis."""
import re, json, collections
D=open('/home/t3rpz/critters/peabrain-lab/paper/DRAFT.md').read().split('\n')
body='\n'.join(D[456:1506])
CAPS=re.compile(r"\b[A-Z][A-Z0-9\|\-\']{2,}\b")
occ=collections.Counter(CAPS.findall(body))
toks=sorted(occ)

# --- class rules, applied in order; first match wins ---
KEEP_PROPER   = {'BANC',"BANC'",'COO'}                       # specimen/release + sparse format
KEEP_ACRONYM  = {'XOR','CPG','CPG-','RNG','PLV','EMG','DVN','DN-','FFT-'}
KEEP_SYMBOL   = {'RMAX'}                                      # a model constant named in Methods §3.9
KEEP_CELLID   = {'IN06B033','IN12B003','S07','C0A','C0B'}     # cell / certification identifiers
DEFER_BATCH   = re.compile(r'^B\d{1,2}(?:-B\d{1,2})?$')       # stage (b4-iii-b), a RELABEL not a strip
DEFER_LANE    = re.compile(r'^L\d{2,3}$')                     # stage (b4-iii-a) = this tick
CLASS_LABEL   = {'SUPER','PARTIAL','KILL','NOT-SUPER','INTERMEDIATE'}  # -> lowercase defined terms
NOTATION      = {'TAU','SEG','PREREG','LANE-RESEARCH'}        # -> spelled out in prose

cls={}
for t in toks:
    if   t in KEEP_PROPER:        cls[t]='KEEP_PROPER'
    elif t in KEEP_ACRONYM:       cls[t]='KEEP_ACRONYM'
    elif t in KEEP_SYMBOL:        cls[t]='KEEP_SYMBOL'
    elif t in KEEP_CELLID:        cls[t]='KEEP_CELLID'
    # possessive forms ("L162's" -> token "L162'") must classify with their stem;
    # the T11 coupling in emit.py caught this gap in the first derivation.
    elif DEFER_BATCH.match(t.rstrip("'")): cls[t]='DEFER_BATCH'
    elif DEFER_LANE.match(t.rstrip("'")):  cls[t]='DEFER_LANE'
    elif t in CLASS_LABEL:        cls[t]='CLASS_LABEL_lowercase'
    elif t in NOTATION:           cls[t]='NOTATION_spell_out'
    else:                         cls[t]='STRIP_EMPHASIS'

keep ={t for t,c in cls.items() if c.startswith('KEEP')}
defer={t for t,c in cls.items() if c.startswith('DEFER')}
strip={t for t,c in cls.items() if c in ('STRIP_EMPHASIS','CLASS_LABEL_lowercase','NOTATION_spell_out')}
# --- the partition assertions ---
assert keep|defer|strip == set(toks),        'partition misses tokens'
assert not (keep&defer) and not (keep&strip) and not (defer&strip), 'classes overlap'
assert len(toks)==179 and sum(occ.values())==310, (len(toks),sum(occ.values()))
by=collections.Counter(cls.values())
for c,n in sorted(by.items(), key=lambda kv:-kv[1]):
    o=sum(occ[t] for t,cc in cls.items() if cc==c)
    print(f'{n:4d} distinct {o:4d} occ  {c}')
print(f'\nKEEP {len(keep)} distinct / {sum(occ[t] for t in keep)} occ')
print(f'DEFER {len(defer)} distinct / {sum(occ[t] for t in defer)} occ')
print(f'STRIP {len(strip)} distinct / {sum(occ[t] for t in strip)} occ')
json.dump({'occ':dict(occ),'class':cls,'counts':dict(by),
           'keep':sorted(keep),'defer':sorted(defer),'strip':sorted(strip),
           'house_form':'lowercase defined terms per §5 Discussion'},
          open('caps_partition.json','w'),indent=1)
print('\npartition frozen -> caps_partition.json (zero draft bytes touched)')
