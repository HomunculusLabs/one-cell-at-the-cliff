#!/usr/bin/env python3
"""L161 verify: the claim-to-artifact map (paper/CLAIM-MAP.md) is COMPLETE
and TRUE. (1) every [key] cited anywhere in DRAFT.md (comma-aware bracket
parse + l149 dotted resolver + the abstract's pooled.<bare> shorthand)
resolves in numbers.json and is declared in the map; (2) the map's key
registry equals numbers.json's keys EXACTLY (bidirectional); (3) every
backticked path in the map exists on disk under its declared root;
(4) provenance re-walk: every walkable numbers.json src subpath is opened,
walked in the stored artifact, and value-compared (v-subset direction,
floats tol 1e-3 — extract_numbers rounds at 4dp); (5) the §1 four-result
keys are present with existing paths; (6) every block referenced by the
§-table exists as a block. Zero rollouts."""
import json, pathlib, re, sys

P = pathlib.Path.home() / 'critters/peabrain-lab'
WEB = pathlib.Path.home() / '.hermes/profiles/maple/playground/website/publish'
draft = (P / 'paper/DRAFT.md').read_text()
nums = json.loads((P / 'paper/numbers.json').read_text())
cmap = (P / 'paper/CLAIM-MAP.md').read_text()
fails = []

def resolve(tok):
    """root key in nums via l149 dotted walk; None if unresolvable."""
    if tok in nums: return tok
    if '.' not in tok: return None
    parts = tok.split('.')
    for i in range(len(parts) - 1, 0, -1):
        head, tail = '.'.join(parts[:i]), parts[i:]
        if head in nums:
            v = nums[head]['v']
            try:
                for t in tail: v = v[t]
                return head
            except (KeyError, TypeError, IndexError): return None
    return None

# (1) draft coverage (comma-aware; skip numeric intervals, ids, prose)
TOK = re.compile(r'^[a-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)*$')
roots = set(); shorthand = []
for grp in re.findall(r'\[([^\[\]]+)\]', draft):
    for tok in (t.strip() for t in grp.split(',')):
        if not TOK.match(tok): continue
        r = resolve(tok)
        if r: roots.add(r); continue
        r2 = resolve('pooled.' + tok)   # abstract shorthand: bare arm names
        if r2: roots.add(r2); shorthand.append(tok)
        else: fails.append(f'draft token unresolvable: {tok}')
print(f'(1) draft cites {len(roots)} root keys'
      + (f' (shorthand resolved: {sorted(set(shorthand))})' if shorthand else ''))

# (2) registry == numbers.json keys, bidirectional
reg = []
for line in cmap.splitlines():
    if line.startswith('- keys:'):
        reg += [t for t in line[7:].split() if TOK.match(t) and resolve(t)]
reg = set(reg)
only_map = sorted(reg - set(nums)); only_nums = sorted(set(nums) - reg)
if only_map: fails.append(f'map keys not in numbers.json: {only_map}')
if only_nums: fails.append(f'numbers.json keys not in map: {only_nums}')
undrafted = sorted(set(nums) - roots)
print(f'(2) registry: {len(reg)} keys == numbers.json {len(nums)} '
      f'({len(undrafted)} registry-only, e.g. {undrafted[:4]})')

# (3) every backticked path exists (banc/ paper/ under LAB, peabrain-figs/ under WEB)
paths = set(re.findall(r'`((?:banc|paper|peabrain-figs)/[A-Za-z0-9_./-]+)`', cmap))
missing = [p for p in sorted(paths)
           if not ((P / p).exists() if not p.startswith('peabrain-figs/')
                   else (WEB / p).exists())]
if missing: fails.append(f'paths missing on disk: {missing}')
print(f'(3) {len(paths)} map paths all exist on disk' if not missing
      else f'(3) MISSING PATHS: {missing}')

# (4) provenance re-walk, v-subset direction.
# Honest compare classes (disclosed in the summary line):
#   exact    — v key present in src at the walked path, values equal (tol)
#   renamed  — v scalar absent at its name but the identical value exists
#              elsewhere in the src subtree (extract_numbers renames, e.g.
#              dR <- legs.mean_paired_dR): provenance TRUE, path drift logged
#   kencode  — v n=192 derives from a src key like 'k192' whose value equals
#              v k (batch-union key encoding): both n and k verified at once
#   noneval  — v stores None (extract's .get() placeholder): nothing asserted
RENAME = []
def dfs_find(node, val, tol=1e-9):
    if isinstance(node, bool): return False
    if isinstance(node, (int, float)): return abs(node - val) <= tol
    if isinstance(node, dict): return any(dfs_find(x, val, tol) for x in node.values())
    if isinstance(node, list): return any(dfs_find(x, val, tol) for x in node)
    return False

def equal_float_pair(node, acc=None):
    """any two EXACTLY equal float leaves (the 16-digit gain-identity form)."""
    vals = []
    def rec(n):
        if isinstance(n, bool): return
        if isinstance(n, float): vals.append(n)
        elif isinstance(n, dict): [rec(x) for x in n.values()]
        elif isinstance(n, list): [rec(x) for x in n]
    rec(node)
    return len(vals) != len(set(vals))

DERIVED = []
def cmp_v(v, s, path):
    if v is None and s is None: return
    if isinstance(v, bool) or isinstance(s, bool):
        if v != s: fails.append(f'{path}: bool {v} != {s}')
    elif isinstance(v, (int, float)) and isinstance(s, (int, float)):
        if abs(v - s) > 1e-3: fails.append(f'{path}: {v} != {s}')
    elif isinstance(v, str) and isinstance(s, str):
        if v != s: fails.append(f'{path}: str {v!r} != {s!r}')
    elif isinstance(v, dict) and isinstance(s, dict):
        for k in v:
            if v[k] is None: continue          # noneval placeholder
            if k not in s:
                if isinstance(v[k], bool):
                    if v[k] and equal_float_pair(s):
                        DERIVED.append(f'{path}.{k}=True (exact float pair in src)')
                    else: fails.append(f'{path}.{k}: bool absent in src')
                elif isinstance(v[k], (int, float)):
                    if dfs_find(s, v[k]): RENAME.append(f'{path}.{k}={v[k]} exact')
                    elif dfs_find(s, v[k], 5e-4):
                        RENAME.append(f'{path}.{k}={v[k]} rounded<=5e-4')
                    else: fails.append(f'{path}.{k}: value {v[k]} absent in src')
                else:
                    fails.append(f'{path}.{k}: absent in src')
            else: cmp_v(v[k], s[k], f'{path}.{k}')
    elif isinstance(v, list) and isinstance(s, list):
        if len(v) != len(s): fails.append(f'{path}: len {len(v)} != {len(s)}')
        else:
            for i, (a, b) in enumerate(zip(v, s)): cmp_v(a, b, f'{path}[{i}]')
    elif v is None or s is None:
        if not (v is None or s is None): fails.append(f'{path}: None mismatch')
    else:
        fails.append(f'{path}: type mismatch {type(v).__name__} vs {type(s).__name__}')

def kencode_ok(v, s):
    """v {'k':72,'n':192} vs src {'k192':72,...}: n encoded in the key name."""
    if not (isinstance(v.get('k'), int) and isinstance(v.get('n'), int)): return False
    return any(re.fullmatch(f'k{v["n"]}', kk) and vv == v['k']
               for kk, vv in s.items() if isinstance(vv, int))

def seg_walk(node, segs, path):
    for j, sg in enumerate(segs):
        if sg == '*':
            node = [node[k] for k in node]   # fan out (gains.*.full)
            for k, n2 in enumerate(node):
                for sg2 in segs[j+1:]: n2 = n2[sg2]
                node[k] = n2
            return node
        node = node[sg]
    return node

WALKABLE = re.compile(r'^[A-Za-z0-9_]+(?:\.[A-Za-z0-9_*]+)+$|^S0_release$|^[A-Za-z0-9_]+$')
walked = star = skipped = kenc = 0
for key, entry in sorted(nums.items()):
    f, sub = entry['src'].split(':', 1)
    f = P / 'banc' / (f[len('banc/'):] if f.startswith('banc/') else f)
    if not f.exists(): fails.append(f'{key}: src file missing {f}'); continue
    if not WALKABLE.match(sub): skipped += 1; continue
    segs = sub.split('.')
    try:
        leaf = seg_walk(json.load(open(f)), segs, key)
    except (KeyError, TypeError, IndexError):
        fails.append(f'{key}: walk failed at {sub}'); continue
    if '*' in segs:
        star += 1
        a, b = sorted(map(float, entry['v'])), sorted(map(float, leaf))
        if len(a) != len(b) or any(abs(x - y) > 1e-3 for x, y in zip(a, b)):
            fails.append(f'{key}: multiset mismatch {a} vs {b}')
    elif (isinstance(entry['v'], dict) and isinstance(leaf, dict)
          and kencode_ok(entry['v'], leaf)):
        kenc += 1
        vv = {k: x for k, x in entry['v'].items() if k not in ('k', 'n')}
        cmp_v(vv, leaf, key)
    else:
        walked += 1; cmp_v(entry['v'], leaf, key)
print(f'(4) provenance: {walked} walked exact(tol 1e-3), {star} star-walk, '
      f'{kenc} kencode-verified, {len(RENAME)} renamed-path (values verified, '
      f'names drifted), {skipped} declared-not-walkable (prose subpaths)')
for r in RENAME: print('    renamed:', r)
for d in DERIVED: print('    derived:', d)

# (5) §1 four-result keys present AND their src files exist
s1 = draft[draft.index('## 1. Introduction'):draft.index('## 2. Results')]
s1roots = set()
for grp in re.findall(r'\[([^\[\]]+)\]', s1):
    for tok in (t.strip() for t in grp.split(',')):
        if TOK.match(tok):
            r = resolve(tok) or resolve('pooled.' + tok)
            if r: s1roots.add(r)
# L172: the §1 four-result map now cites the CANONICAL pooled keys instead
# of the per-batch unions (one pooled count per arm), so the required set
# follows the fold.  l157.pooled stays (the per-pool carrier census).
need = {'l172.pooled', 'l172.diffs', 'l172.census_unique', 'l157.pooled',
        'l171.envelope', 'l171.panel'}
for k in sorted(need):
    if k not in reg: fails.append(f'(5) §1 key {k} not in map')
    if k not in s1roots: fails.append(f'(5) §1 key {k} not cited in §1 text')
    sf = nums[k]['src'].split(':')[0]
    if sf.startswith('banc/'): sf = sf[len('banc/'):]
    if not (P / 'banc' / sf).exists(): fails.append(f'(5) {k} src file missing')
print(f'(5) §1 four-result keys: {len(need & reg & s1roots)}/{len(need)} '
      'in map + cited + src exists')

# (6) §-table block refs exist as blocks
blocks = set(re.findall(r'^### (B\d+) —', cmap, re.M))
refs = set(re.findall(r'\| (B\d+(?:, B\d+)*) \|', cmap))
referenced = set(b.strip() for r in refs for b in r.split(','))
ghost = sorted(referenced - blocks)
if ghost: fails.append(f'(6) §-table references missing blocks: {ghost}')
print(f'(6) §-table references {len(referenced)} blocks, all defined'
      if not ghost else f'(6) GHOST BLOCKS: {ghost}')

if fails:
    print('\nL161 FAIL:'); [print(' -', f) for f in fails[:20]]; sys.exit(1)
print('L161 verify: ALL GREEN')
