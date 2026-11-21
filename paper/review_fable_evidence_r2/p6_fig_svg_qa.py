#!/usr/bin/env python3
"""Round-2 probe 6: analytic figure QA (no vision). SVG text, font sizes, background, stale labels."""
import re, os, sys, glob
P = os.path.expanduser('~/.hermes/profiles/maple/playground/website/publish/peabrain-figs')
figs = sorted(glob.glob(P + '/l136_transition_law*.svg') + glob.glob(P + '/l152_clamp_cut_grid*.svg') + glob.glob(P + '/l160_slowline_carrier*.svg'))
figs.append('/home/t3rpz/critters/peabrain-lab/paper/fig_l152.svg')
for f in figs:
    s = open(f, errors='replace').read()
    m = re.search(r'<svg[^>]*width="([\d.]+)(pt|px)?"[^>]*height="([\d.]+)', s)
    w = float(m.group(1)) if m else None
    sizes = [float(x) for x in re.findall(r'font(?:-size)?:\s*([\d.]+)px', s)] + [float(x) for x in re.findall(r'font-size="([\d.]+)', s)]
    texts = re.findall(r'<!-- (.*?) -->', s)
    glyph_text = [t for t in texts if len(t) > 1]
    bg = re.findall(r'<rect[^>]*fill="(#[0-9a-fA-F]{3,6})"', s)[:1] + re.findall(r'style="fill:\s*(#[0-9a-fA-F]{6})', s)[:2]
    print('\n', os.path.basename(f), '| bytes', len(s), '| mtime', __import__('time').strftime('%m-%d %H:%M', __import__('time').localtime(os.path.getmtime(f))))
    print('  width', w, m.group(2) if m else None, '| first fills', bg, '| n font sizes', len(sizes), '| min/median/max', (min(sizes), sorted(sizes)[len(sizes)//2], max(sizes)) if sizes else None)
    if w and sizes:
        sc = 6.5 * 72 / w      # pt scale if placed at 6.5 in width
        import numpy as np
        a = np.array(sizes) * sc
        print('  at 6.5-in print width: scale %.3f -> text min %.1f pt, median %.1f pt, share under 7 pt: %.0f%%' % (sc, a.min(), np.median(a), 100 * (a < 7).mean()))
    for pat in ['monotone', 'B17', 'B2[0-9]', 'B3[0-9]', r'\.334', r'\.371', 'L1[0-9][0-9]', 'l1[0-9][0-9]', 'NEUTRAL', 'neutral', '12/32', '30/66', '43/144', '72/258', '124/128', '203/210', '28/32', '78/98', '3x12', '2x18', 'two-factor', 'xm']:
        hits = [t for t in glyph_text if re.search(pat, t)]
        if hits:
            print('   [%s] %d: %s' % (pat, len(hits), ' | '.join(h[:90] for h in hits[:3])))
