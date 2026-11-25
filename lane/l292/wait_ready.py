#!/usr/bin/env python3
"""L292: wait for the fly duck's first 200 after a start, then time the
FIRST /needs on each chat id given (each a fresh or returning session).
Usage: python3 lane/l292/wait_ready.py <max-wait-s> <chat> [<chat> ...]
Read-only against the duck apart from the /needs polls themselves.
"""
import json
import socket
import subprocess
import sys
import time
from urllib.parse import urlparse

URL = "http://192.168.50.58:3122"
MAX_WAIT = float(sys.argv[1])
CHATS = sys.argv[2:]


def get(path, timeout=120):
    u = urlparse(URL + path)
    t0 = time.time()
    try:
        s = socket.create_connection((u.hostname, u.port), timeout=timeout)
        s.sendall(f"GET {u.path}?{u.query} HTTP/1.0\r\nHost: {u.hostname}\r\n\r\n".encode())
        buf = b""
        while True:
            c = s.recv(65536)
            if not c:
                break
            buf += c
        s.close()
        code = int(buf.split(b" ", 2)[1])
        body = buf.split(b"\r\n\r\n", 1)[1]
    except Exception as e:  # noqa: BLE001
        return None, repr(e)[:80], time.time() - t0
    return code, body, time.time() - t0


def pid():
    return subprocess.run(["systemctl", "--user", "show", "critter-bill-fly.service",
                           "-p", "MainPID", "--value"], capture_output=True, text=True).stdout.strip()


t0 = time.time()
n = 0
while True:
    code, body, dt = get("/health")
    n += 1
    if code == 200:
        break
    if time.time() - t0 > MAX_WAIT:
        print(json.dumps({"ready": False, "waited_s": round(time.time() - t0, 1),
                          "last": [code, body], "probes": n}))
        sys.exit(1)
    time.sleep(3)
print(json.dumps({"ready": True, "first_200_after_s": round(time.time() - t0, 1),
                  "pid": pid(), "at": time.strftime("%H:%M:%S"), "probes": n,
                  "health": body.decode()[:80]}))
for chat in CHATS:
    code, body, dt = get(f"/needs?chat={chat}")
    print(json.dumps({"chat": chat, "code": code, "wall_s": round(dt, 3),
                      "at": time.strftime("%H:%M:%S"),
                      "needs": json.loads(body) if code == 200 else body[:120]}))
