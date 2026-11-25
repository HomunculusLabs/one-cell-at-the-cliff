#!/usr/bin/env python3
"""L292 probe C: the cold /needs call, attributed to the duck's own cgroup.

Usage: probe_c.py <label> <chat> [<chat> ...]

Per call: wall time, the duck process's CPU (ns, schedstat, per thread),
the handler thread's scheduler state sampled every ~5 ms by a SEPARATE
thread (R = running, D = uninterruptible with its kernel wait channel),
and the service cgroup's own memory.stat deltas (pswpin/pgmajfault/pgscan/
pgsteal/workingset_refault* are PER-CGROUP there, unlike /proc/vmstat).
PID comes from systemd (the restart changes it). Read-only against the duck.
"""
import collections
import json
import os
import socket
import subprocess
import sys
import threading
import time
from urllib.parse import urlparse

URL = "http://192.168.50.58:3122/needs?chat="
CG = ("/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/app.slice/"
      "critter-bill-fly.service")
KEYS = ("pswpin", "pswpout", "pgmajfault", "pgscan", "pgsteal",
        "pgscan_direct", "pgsteal_direct", "pgscan_kswapd", "pgsteal_kswapd",
        "workingset_refault_file", "workingset_refault_anon",
        "workingset_activate_file", "workingset_activate_anon")
STATE = {"R": "run", "D": "D", "S": "sleep"}


def pid():
    out = subprocess.run(["systemctl", "--user", "show", "critter-bill-fly.service",
                          "-p", "MainPID", "--value"], capture_output=True, text=True)
    return out.stdout.strip()


def memstat():
    out = {}
    with open(CG + "/memory.stat") as f:
        for line in f:
            k, v = line.split()
            if k in KEYS:
                out[k] = int(v)
    for k in ("memory.current", "memory.swap.current", "memory.peak", "memory.swap.peak"):
        try:
            with open(CG + "/" + k) as f:
                out[k] = int(f.read())
        except OSError:
            pass
    return out


def thr(P):
    """tid -> (runtime ns, utime ticks, stime ticks) -- the tick fields give
    the user/kernel split at 10 ms resolution."""
    out = {}
    for t in os.listdir(f"/proc/{P}/task"):
        try:
            with open(f"/proc/{P}/task/{t}/schedstat") as f:
                ns = int(f.read().split()[0])
            with open(f"/proc/{P}/task/{t}/stat") as f:
                s = f.read()
            p = s[s.rindex(")") + 2:].split()
            out[t] = (ns, int(p[11]), int(p[12]))
        except OSError:
            pass
    return out


def sampler(P, base, counts, stop, live):
    """Sample only threads that did NOT exist before the call (handler).
    Keep each new thread's LAST schedstat/utime/stime in `live` -- the
    handler exits as soon as the response is written, so a read taken
    after the call would miss its CPU entirely (the exit artifact)."""
    poll = 0.005
    while not stop[0]:
        try:
            for t in os.listdir(f"/proc/{P}/task"):
                if t in base:
                    continue
                try:
                    with open(f"/proc/{P}/task/{t}/schedstat") as f:
                        ns = int(f.read().split()[0])
                    with open(f"/proc/{P}/task/{t}/stat") as f:
                        s = f.read()
                    p = s[s.rindex(")") + 2:].split()
                    live[t] = (ns, int(p[11]), int(p[12]))
                    with open(f"/proc/{P}/task/{t}/wchan") as f:
                        wc = f.read().strip() or "running"
                    counts[(t, p[0], wc)] += 1
                except OSError:
                    pass
        except OSError:
            pass
        time.sleep(poll)


def one(P, chat):
    base = thr(P)
    m0 = memstat()
    counts = collections.Counter()
    live = {}
    stop = [False]
    sm = threading.Thread(target=sampler, args=(P, base, counts, stop, live), daemon=True)
    box = {}
    t0 = time.time()
    sm.start()

    def worker():
        u = urlparse(URL + chat)
        s = socket.create_connection((u.hostname, u.port), timeout=180)
        s.sendall(f"GET {u.path}?{u.query} HTTP/1.0\r\nHost: {u.hostname}\r\n\r\n".encode())
        buf = b""
        while True:
            c = s.recv(65536)
            if not c:
                break
            buf += c
        box["n"] = len(buf)
        s.close()

    w = threading.Thread(target=worker, daemon=True)
    w.start()
    w.join(180)
    t1 = time.time()
    stop[0] = True
    sm.join(2)
    m1 = memstat()
    b1 = thr(P)
    d = {k: m1.get(k, 0) - m0.get(k, 0) for k in m1 if isinstance(m1[k], int)}
    new_cpu = sum(v[0] for t, v in b1.items() if t not in base) / 1e9
    old_cpu = sum(v[0] - base[t][0] for t, v in b1.items() if t in base) / 1e9
    split = {}
    for t, v in b1.items():
        if t not in base or v[0] - base[t][0] > 1e7:
            b = base.get(t, (0, 0, 0))
            split[t] = {"new": t not in base, "ns_s": round((v[0] - b[0]) / 1e9, 3),
                        "utime_s": round((v[1] - b[1]) / 100.0, 2),
                        "stime_s": round((v[2] - b[2]) / 100.0, 2)}
    by_state = collections.Counter()
    by_wchan = collections.Counter()
    for (t, st, wc), n in counts.items():
        by_state[STATE.get(st, st)] += n
        if st == "D":
            by_wchan[wc] += n
    out = {"chat": chat, "pid": P, "wall_s": round(t1 - t0, 3),
           "cpu_new_threads_s": round(new_cpu, 3), "cpu_old_threads_s": round(old_cpu, 3),
           "resp_bytes": box.get("n"), "cg_delta": d, "thread_split": split,
           "handler_cpu": {t: {"ns_s": round(v[0] / 1e9, 3),
                               "utime_s": round(v[1] / 100.0, 2),
                               "stime_s": round(v[2] / 100.0, 2)}
                           for t, v in live.items()},
           "cg_after": {k: m1.get(k) for k in ("memory.current", "memory.swap.current")},
           "samples_by_state": dict(by_state),
           "D_wchan_top": by_wchan.most_common(5),
           "new_thread_wchan_top": collections.Counter(
               wc for (t, st, wc), n in counts.items() for _ in range(n)).most_common(6)}
    print(json.dumps(out))
    return out


if __name__ == "__main__":
    label = sys.argv[1]
    P = pid()
    print(json.dumps({"label": label, "pid": P, "time": time.strftime("%H:%M:%S")}))
    for chat in sys.argv[2:]:
        one(P, chat)
