"""L52 analytic figure QA (vision endpoint down, disclosed): SVG text
overflow scan (char-width estimate), panel-C column collision math, polyline
frame containment, and every numerically-checkable described claim diffed
against results_l52.json (L47 rule)."""
import json
import re

W, H = 1560, 940
svg = open('l52/toxic.svg').read()
res = json.load(open('l52/results_l52.json'))
bad = []

# 1. text overflow: anchor + estimated width vs canvas
for m in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"([^>]*)>(.*?)</text>', svg, re.S):
    x, y, attrs, inner = float(m.group(1)), float(m.group(2)), m.group(3), m.group(4)
    txt = re.sub(r'<[^>]+>', '', inner)
    txt = txt.replace('&#8226;', '@').replace('&#8805;', '>=')
    fs = 13.0
    fm = re.search(r'font-size="(\d+)', attrs)
    if fm:
        fs = float(fm.group(1))
    est = len(txt) * fs * 0.62
    anchor = 'start'
    am = re.search(r'text-anchor="(\w+)"', attrs)
    if am:
        anchor = am.group(1)
    lo = x - est if anchor == 'end' else (x - est / 2 if anchor == 'middle' else x)
    hi = lo + est
    if lo < -2 or hi > W + 2 or y < 8 or y > H - 2:
        bad.append(f'OVERFLOW text "{txt[:40]}" x={x:.0f} y={y:.0f} [{lo:.0f},{hi:.0f}]')

# 2. panel C column collisions: tspan x vs estimated content widths
rows = re.findall(r'<text x="60" y="(\d+)"[^>]*>(.*?)</text>', svg, re.S)
colx = [60, 250, 350, 450, 550, 880, 980, 1160]
for y, inner in rows:
    tspans = re.findall(r'<tspan x="(\d+)">([^<]*)</tspan>', inner)
    for (x1, t1), (x2, _) in zip(tspans, tspans[1:]):
        w1 = len(t1) * 13 * 0.62
        if float(x1) + w1 > float(x2) + 2:
            bad.append(f'COLLIDE row y={y}: "{t1}" width {w1:.0f} spans '
                       f'{float(x1):.0f}..{float(x1)+w1:.0f} into col {x2}')

# 3. polyline containment in panel A frame (ax+50 .. ax+aw-40, ay..ay+ah-50)
fx0, fx1, fy0, fy1 = 60 + 50, 60 + 760 - 40, 120, 120 + 460 - 50
for m in re.finditer(r'<polyline points="([^"]+)"', svg):
    for pt in m.group(1).split():
        px, py = map(float, pt.split(','))
        if not (fx0 - 1 <= px <= fx1 + 1 and fy0 - 1 <= py <= fy1 + 1):
            bad.append(f'FRAME polyline pt {px:.0f},{py:.0f} outside')

# 4. ink density per panel
for name, (x0, y0, x1, y1) in {'A': (110, 120, 780, 530),
                               'B': (930, 120, 1500, 530),
                               'C': (60, 620, 1500, 880)}.items():
    n = 0
    for m in re.finditer(r'<(circle|polyline|path|rect|line|text)([^>]*)>', svg):
        s = m.group(2)
        xm = re.search(r'[xc][xcx]?="([\d.-]+)"', s)
        if xm and x0 <= float(xm.group(1)) <= x1:
            n += 1
    print(f'panel {name}: {n} elements')

# 5. numeric claims vs data
sens = res['sensitivity']
checks = [
    ('f14a3 duty_e', sens['f14a3']['duty_early'], 0.173),
    ('f14a3 duty_l', sens['f14a3']['duty_late'], 0.033),
    ('f07a3 duty_e', sens['f07a3']['duty_early'], 0.363),
    ('f07a3 duty_l', sens['f07a3']['duty_late'], 0.381),
    ('GC 11', res['GC']['got']['11'], 0.36),
]
for name, got, want in checks:
    ok = abs(got - want) < 5e-4
    print(f'claim {name}: fig/json {got} == stated {want} -> {ok}')
    if not ok:
        bad.append(f'CLAIM {name} {got} != {want}')

print('verdict:', 'PASS' if not bad else 'FAIL')
for b in bad:
    print(' -', b)
