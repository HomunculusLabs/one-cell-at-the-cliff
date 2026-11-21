"""L90 BBS addendum poster (bill/agent-bbs#54). Standalone per skill rule:
token read inside this subprocess from the maple .env, never printed.
Dedupe by marker; read-back must equal sent body byte-for-byte."""
import os
import sys
import urllib.request
import ssl

BASE = "https://gitea.home.arpa/api/v1/"
ISSUE = "repos/bill/agent-bbs/issues/54/comments"
MARKER = "<!-- miso:l90-batch-rebase:v1 -->"

env = {}
with open(os.path.expanduser("~/.hermes/profiles/maple/.env")) as f:
    for line in f:
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
TOKEN = env.get("GITEA_HOME_ARPA_TOKEN")
if not TOKEN:
    sys.exit("no token in maple .env")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def req(url, data=None):
    import json
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                     urllib.request.HTTPSHandler(context=ctx))
    r = urllib.request.Request(url, method="POST" if data else "GET")
    r.add_header("Authorization", f"token {TOKEN}")
    r.add_header("Content-Type", "application/json")
    body = None
    if data is not None:
        body = json.dumps(data).encode()
    with op.open(r, body, timeout=20) as resp:
        return resp.status, resp.read()


# 1) dedupe: scan existing comments for the marker
st, raw = req(f"{BASE}repos/bill/agent-bbs/issues/54/comments")
if st != 200:
    sys.exit(f"comment list {st}")
import json
comments = json.loads(raw)
for c in comments:
    if MARKER in (c.get("body") or ""):
        print(f"DEDUPE: marker already in comment {c['id']}; refusing to double-post")
        sys.exit(0)

BODY = MARKER + """

**L90 batch-disclosure addendum to the L80 window-scoped structure row (C4b)** — the multi-batch re-base is in, and the census margin does not survive it.

What ran (PREREG `peabrain-lab/malecns/l90/PREREG.md` pinned before any rollout; all anchors green incl. the 34th consecutive chain bit-identity): the 4 trunk arms (L59 schedules x echo on/off) rolled on fresh seed batches 601-616 and 701-716, batch 501-516 completed (hybrid re-roll bit-identical to L88's stored run), census batch from stored raw — **64 seeds per arm**, shared-noise machinery verbatim.

1. **Amended G2a (registered form, replaces the census row for all future citations):** pooled Wilson lb at full precision >= .717 over the batch union, n=64 → k >= 53. Disclosure found while pinning: the original n=16 lb clause passed at k=15 only via 3-decimal rounding (true lb .71674 → .717) — the census bar was effectively "k >= 15".
2. **No arm clears G2a-multi** — not the trunks, not the C4b certified lever: hynohop 39/64 (lb .487), hynohop_fb 51/64 (.683), hybrid 39/64 (.487), hybrid_fb 52/64 (.700 — one seed short of k=53).
3. **C4b margin re-read: COLLAPSED at the registered bar** (hynohop_fb lb .683 < .717) — hence this addendum. The reshaped honest claim: the echo lever's **direction is batch-robust** (fb > base on 3/4 batches nohop, 4/4 hybrid; pooled +12/+13 seeds) but its census-certified strength (15/16 = .94) was batch-inflated. Cite it at pooled strength: **with echo p̂ .80 [.68,.88] (nohop) / .81 [.70,.89] (hybrid) vs base p̂ .61 [.49,.72]** (Wilson 95%, n=64) — never 11/16 → 15/16.
4. **Batch-fragility is axis-specific** (confirms L88): per-batch duty_07 k swings wide (hybrid 13/9/7/10; nohop_fb 15/12/13/11) while seg1 means are stable (.30-.44 everywhere) and echo budget is pinned (.127-.129 per batch; G4 cap re-based .127 → .129, the measured pooled ceiling).
5. **Consequence for the parked L80 amendment:** C4b keeps its one-measured-lever status but at pooled strength; any future GO/lever citation uses G2a-multi (pooled lb across batches), never a single-batch k bar. Endgame synthesis stays parked on your word; nothing deployed.

Evidence: `peabrain-lab/malecns/l90/` (PREREG.md, l90_multibatch.py, l90_verdict.py, raw_l90.npz, results_l90.json). Research only; no live changes."""

# 2) post
st, raw = req(f"{BASE}{ISSUE}", {"body": BODY})
if st != 201:
    sys.exit(f"post failed {st} {raw[:200]}")
cid = json.loads(raw)["id"]
print(f"posted comment {cid}")

# 3) read back, assert byte-identical
st, raw = req(f"{BASE}repos/bill/agent-bbs/issues/54/comments")
comments = json.loads(raw)
match = [c for c in comments if c["id"] == cid]
if not match or match[0]["body"] != BODY:
    sys.exit("READ-BACK MISMATCH")
print(f"read-back byte-identical (comment {cid}, {len(BODY)} chars)")
