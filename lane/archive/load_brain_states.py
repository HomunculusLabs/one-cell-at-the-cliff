#!/usr/bin/env python3
"""L102 loader: the (brain-state, intent) dataset over the L98 archive.

Pairs each archived world-session .pt snapshot (copied read-only by
archive_tick.py) with the /needs intent+mood captured in the SAME json
snapshot — the first dataset toward the owner-rule endgame (learned
locomotion from her own CX/locomotor populations). Read-only.

Usage:
  python3 load_brain_states.py            # dataset report (no torch)
  python3 load_brain_states.py --load     # also torch.load a few files
                                          # (run with the peabrain venv)
Exits 1 if any snapshot references a pruned/missing .pt.
"""
import glob
import json
import os
import sys
from collections import Counter

ARCH = os.path.dirname(os.path.abspath(__file__))   # lane/archive itself


def pairs():
    """All (brain-state, intent) pairs in capture order."""
    out = []
    for p in sorted(glob.glob(os.path.join(ARCH, "snap_*.json"))):
        try:
            with open(p) as f:
                s = json.load(f)
        except Exception:
            continue
        b = s.get("brain")
        if not b:
            continue                       # pre-L102 snapshot
        needs = s.get("needs") or {}
        out.append({
            "snap": os.path.basename(p),
            "captured_at": s["captured_at"],
            "intent": needs.get("intent"),
            "mood": needs.get("mood"),
            "pt": os.path.join(ARCH, b["file"]),
            "exists": os.path.exists(os.path.join(ARCH, b["file"])),
            "size": b.get("size"),
            "sha256": b.get("sha256"),
            "dedup": b.get("dedup", False),
        })
    return out


def main():
    ps = pairs()
    have_intent = [p for p in ps if p["intent"]]
    missing = [p for p in ps if not p["exists"]]
    uniq_brains = len({p["sha256"] for p in ps})
    c = Counter(p["intent"] for p in have_intent)
    total_mb = sum(p["size"] or 0 for p in ps if p["exists"]) / 1e6
    print(f"brain-state snapshots: {len(ps)} "
          f"({len(have_intent)} with intent, {uniq_brains} unique brains)")
    print(f"intent distribution: {dict(c.most_common())}")
    print(f"archive size: {total_mb:.1f} MB")
    if "--load" in sys.argv:
        import torch
        for p in ps[:3]:
            d = torch.load(p["pt"], map_location="cpu")
            shapes = {k: tuple(v.shape) for k, v in d.items()}
            print(os.path.basename(p["pt"]), shapes)
    if missing:
        print(f"WARNING: {len(missing)} snapshots reference pruned/missing "
              f".pt files (prune is oldest-first by design)")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
