import re, pathlib, sys
t = pathlib.Path(sys.argv[1]).read_text().strip()
flat = re.sub(r'\s+', ' ', t)
print('raw chars :', len(t))
print('flat chars:', len(flat), '  limit 1920   slack', 1920 - len(flat))
print('words     :', len(flat.split()))
sents = [s for s in re.split(r'(?<=[.!?])\s+', flat) if s.strip()]
print('sentences :', len(sents), ' max words', max(len(s.split()) for s in sents))
for s in sents:
    if len(s.split()) > 60: print('  LONG:', len(s.split()), s[:80])
print('caps tokens:', sorted(set(re.findall(r'\b[A-Z]{3,}(?:-[A-Z]+)*\b', t))))
print('bracket keys:', sorted(set(re.findall(r'\[[a-z0-9_.]+\]', t))))
bad = re.findall(r'\bcut[a-zA-Z]|\bsil[A-Z0-9]|\bscr\d|\bb65\b|\bB\d{2}\b|\bL\d{2,3}\b|\bl1\d\d\.', t)
print('arm/lane codes:', bad)
print('num tokens:', sorted(set(re.findall(r'\d+\.\d+|\d+/\d+|\d+', flat))))
