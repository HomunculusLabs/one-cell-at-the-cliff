#!/usr/bin/env python3
"""L292 probe B: WHERE does a cold /needs call spend its wall time?

For each chat id given on the command line, fire ONE /needs call and
bracket it with the live process's own counters (read-only, /proc only):
wall time, the process's CPU time (utime+stime, all threads; per-thread
top), memory-pressure stalls (PSI "some"/"full" cumulative us), swap-ins
(system-wide), and a ~5 ms sample of every thread's scheduler state and
kernel wait channel while the call is in flight.

Reading:
  d_cpu ~ wall            -> CPU-bound inside the duck (zram decompress counts
                             as kernel stime; so does a lock-holding world tick
                             in another thread -- the per-thread table and the
                             state samples separate them).
  d_cpu << wall, state D  -> blocked on page-in from a real device.
  d_cpu << wall, state S  -> blocked on the GPU or on the lock.
"""
import collections
import json
import os
import socket
import sys
import threading
import time
from urllib.parse import urlparse

PID = "3896241"
URL = "http://192.168.50.58:3122/needs?chat="
HZ = os.sysconf("SC_CLK_TCK")


def _tasks():
    try:
        return os.listdir(f"/proc/{PID}/task")
    except OSError:
        return []


def _stat(tid):
    with open(f"/proc/{PID}/task/{tid}/stat") as f:
        s = f.read()
    r = s.rindex(")")
    p = s[r + 2:].split()
    # schedstat field 1 = cumulative runtime in NANOSECONDS (ns resolution;
    # utime/stime ticks are 10 ms and read 0 on sub-tick calls)
    try:
        with open(f"/proc/{PID}/task/{tid}/schedstat") as f:
            ns = int(f.read().split()[0])
    except OSError:
        ns = 0
    return p[0], ns   # state, runtime ns


def proc_cpu():
    tot = 0
    for tid in _tasks():
        try:
            tot += _stat(tid)[1]
        except OSError:
            pass
    return tot


def thread_cpu():
    out = {}
    for tid in _tasks():
        try:
            out[tid] = _stat(tid)[1]
        except OSError:
            pass
    return out


def thread_name(tid):
    try:
        with open(f"/proc/{PID}/task/{tid}/comm") as f:
            return f.read().strip()
    except OSError:
        return "?"


def psi():
    out = {}
    with open("/proc/pressure/memory") as f:
        for line in f:
            tok = line.split()
            if tok:
                out[tok[0]] = int(tok[-1].split("total=")[1])
    return out


def vm():
    out = {}
    with open("/proc/vmstat") as f:
        for line in f:
            k, v = line.split()
            if k in ("pswpin", "pgmajfault"):
                out[k] = int(v)
    return out


def swap_mb():
    with open(f"/proc/{PID}/status") as f:
        for line in f:
            if line.startswith("VmSwap:"):
                return int(line.split()[1]) / 1024
    return -1


def _wchan(tid):
    try:
        with open(f"/proc/{PID}/task/{tid}/wchan") as f:
            return f.read().strip() or "0"
    except OSError:
        return "?"


def call_and_sample(chat, samples, stop):
    u = urlparse(URL + chat)
    s = socket.create_connection((u.hostname, u.port), timeout=120)
    s.sendall(f"GET {u.path}?{u.query} HTTP/1.0\r\nHost: {u.hostname}\r\n\r\n".encode())
    s.settimeout(0.05)
    buf = b""
    done = False
    while not done:
        got = False
        try:
            chunk = s.recv(65536)
            buf += chunk
            got = True
            if not chunk:
                done = True
        except socket.timeout:
            pass
        if not done and buf.endswith(b"\r\n\r\n"):
            head, _, body = buf.partition(b"\r\n\r\n")
            cl = [l for l in head.split(b"\r\n") if l.lower().startswith(b"content-length")]
            if cl and len(body) >= int(cl[0].split(b":")[1]):
                done = True
        # sample (about every 5 ms; each iteration costs ~1-3 ms at 23 threads)
        for tid in _tasks():
            try:
                st, _ = _stat(tid)
                samples[(tid, thread_name(tid), st, _wchan(tid))] += 1
            except OSError:
                pass
        if time.time() - stop[0] > 0 and time.time() - stop[0] > 120:
            done = True
    s.close()
    return buf


def run(chat):
    samples = collections.Counter()
    stop = [0.0]
    t0 = time.time()
    c0 = proc_cpu()
    th0 = thread_cpu()
    p0 = psi()
    v0 = vm()
    sw0 = swap_mb()
    box = {}

    def worker():
        box["buf"] = call_and_sample(chat, samples, stop)

    th = threading.Thread(target=worker, daemon=True)
    stop[0] = time.time()
    th.start()
    th.join(130)
    t1 = time.time()
    c1 = proc_cpu()
    th1 = thread_cpu()
    p1 = psi()
    v1 = vm()
    sw1 = swap_mb()
    lat = t1 - t0
    dcpu = (c1 - c0) / 1e9
    per = sorted(((th1[t] - th0.get(t, 0)) / 1e9, t) for t in th1)
    top = [(f"{dt:.4f}s", t, thread_name(t)) for dt, t in per[::-1] if dt > 0.0005][:4]
    idle = ("__futex_wait", "poll_schedule", "futex_wait", "do_select", "hrtimer_nanosleep")
    active = [list(k) + [n] for k, n in samples.most_common()
              if not (k[2] == "S" and k[3].startswith(idle)) and k[3] != "0"][:10]
    out = {
        "chat": chat, "wall_s": round(lat, 3), "d_cpu_s": round(dcpu, 4),
        "cpu_over_wall": round(dcpu / lat, 3) if lat else None,
        "d_psi_some_us": p1["some"] - p0["some"],
        "d_psi_full_us": p1["full"] - p0["full"],
        "d_pswpin": v1["pswpin"] - v0["pswpin"],
        "d_majflt": v1["pgmajfault"] - v0["pgmajfault"],
        "swap_mb": [round(sw0, 1), round(sw1, 1)],
        "resp_bytes": len(box.get("buf", b"")),
        "threads_cpu_top": top,
        "active_samples": active,
    }
    print(json.dumps(out))
    return out


if __name__ == "__main__":
    for chat in sys.argv[1:]:
        run(chat)
