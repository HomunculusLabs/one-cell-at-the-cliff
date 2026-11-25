#!/usr/bin/env python3
"""L292 probe A: tight-loop /needs latency (same chat id) across >= 2 world
ticks. Read-only against the live duck (plain /needs is the probe every
previous tick used). Writes one CSV row per probe to lane/l292/probeA.csv.

A periodic cluster of slow probes at the 45 s world-tick period = the lock
is held by the world tick (lock wait). All-fast = the lock is not the cold
cause."""
import csv
import subprocess
import sys
import time
import urllib.parse
import urllib.request

URL = "http://192.168.50.58:3122/needs"
OUT = "/home/t3rpz/critters/peabrain/lane/l292/probeA.csv"
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 95.0


def swap_state():
    rss = swp = None
    with open("/proc/3896241/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                rss = int(line.split()[1])
            elif line.startswith("VmSwap:"):
                swp = int(line.split()[1])
    vm = {}
    with open("/proc/vmstat") as f:
        for line in f:
            k, v = line.split()
            if k in ("pswpin", "pswpout", "pgmajfault"):
                vm[k] = int(v)
    return rss, swp, vm


def main():
    t_start = time.time()
    rows = []
    prev = swap_state()
    while time.time() - t_start < DUR:
        a = time.time()
        try:
            with urllib.request.urlopen(URL, timeout=120) as r:
                code = r.status
                body = r.read()
        except Exception as e:  # noqa: BLE001
            code = "ERR"
            body = repr(e).encode()
        b = time.time()
        cur = swap_state()
        rows.append({
            "t": f"{a - t_start:.3f}", "code": code,
            "lat_s": f"{b - a:.4f}", "bytes": len(body),
            "rss_mb": f"{cur[0] / 1024:.1f}", "swap_mb": f"{cur[1] / 1024:.1f}",
            "d_pswpin": cur[2]["pswpin"] - prev[2]["pswpin"],
            "d_pswpout": cur[2]["pswpout"] - prev[2]["pswpout"],
            "d_majflt": cur[2]["pgmajfault"] - prev[2]["pgmajfault"],
        })
        prev = cur
        time.sleep(0.5)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    lats = sorted(float(r["lat_s"]) for r in rows)
    slow = [r for r in rows if float(r["lat_s"]) > 0.5]
    print(f"probes={len(rows)} dur={DUR:.0f}s "
          f"median={lats[len(lats) // 2]:.4f} p90={lats[int(len(lats) * .9)]:.4f} "
          f"max={lats[-1]:.4f} n_over_0.5s={len(slow)}")
    for r in slow:
        print("SLOW", " ".join(f"{k}={v}" for k, v in r.items()))
    codes = {}
    for r in rows:
        codes[r["code"]] = codes.get(r["code"], 0) + 1
    print("codes", codes)
    print("sum d_pswpin", sum(r["d_pswpin"] for r in rows),
          "sum d_majflt", sum(r["d_majflt"] for r in rows))


if __name__ == "__main__":
    main()
