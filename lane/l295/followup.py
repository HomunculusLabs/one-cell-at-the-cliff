"""L295 follow-up (read-only): system TZ (what date.today() means to the live pass), the
visitor-record date histogram, and the post-midnight sliver each midnight pass actually had."""
import glob, json, os, time, collections, datetime as dt
from zoneinfo import ZoneInfo

PB = "/home/t3rpz/critters/peabrain"
print("system TZ:", time.tzname, "| now local:", dt.datetime.now().strftime("%H:%M %Z"),
      "| TZ env:", os.environ.get("TZ"))
# what the service itself sees: read its MainPID environ for TZ
import subprocess
pid = subprocess.run(["systemctl", "--user", "show", "critter-bill-fly.service", "-p", "MainPID", "--value"],
                     capture_output=True, text=True).stdout.strip()
try:
    env = open(f"/proc/{pid}/environ", "rb").read().split(b"\0")
    tz = [e.decode() for e in env if e.startswith(b"TZ=") or e.startswith(b"PEABRAIN")]
    localtime = os.path.realpath(f"/proc/{pid}/root/etc/localtime")
    print(f"service pid {pid}: TZ-ish env={tz} | /etc/localtime -> {localtime}")
except Exception as ex:
    print("service environ unreadable:", ex)

recs = []
for p in sorted(glob.glob(f"{PB}/sessions/*.json")):
    if os.path.basename(p).startswith("world"):
        continue
    try:
        dl = (json.load(open(p)).get("day_log") or [])
    except Exception:
        continue
    for e in dl:
        recs.append((e["t"], e["ev"], os.path.basename(p)))
recs.sort()
NY = ZoneInfo("America/New_York")
by_day = collections.Counter(dt.datetime.fromtimestamp(t, NY).strftime("%m-%d") for t, _, _ in recs)
print(f"\nVISITOR records={len(recs)} sessions_with_recs={len({f for _, _, f in recs})}")
print("by local day:", sorted(by_day.items()))
print("last visitor record:", dt.datetime.fromtimestamp(recs[-1][0], NY).strftime("%Y-%m-%d %H:%M:%S"), recs[-1][1], recs[-1][2][:40])
print("last 6:", [(dt.datetime.fromtimestamp(t, NY).strftime("%m-%d %H:%M"), ev) for t, ev, _ in recs[-6:]])
kind = ("pet", "greet", "goats", "peas", "tin", "water", "shiny", "slug")
kw = [(t, ev, f) for t, ev, f in recs if ev in kind and ev != "water"]
print("last KIND non-water visitor record:", dt.datetime.fromtimestamp(kw[-1][0], NY).strftime("%Y-%m-%d %H:%M:%S"), kw[-1][1])
per_sess = collections.Counter(f for _, _, f in kw)
print("kind-non-water per session: n_sessions", len(per_sess), "| top", per_sess.most_common(5))

# the post-midnight sliver: for each archived midnight pass, how many minutes of pass-date entries could exist
res = json.load(open(f"{PB}/lane/l295/results_l295.json"))
print("\nMIDNIGHT SLIVER (pass local minute = max minutes of pass-date input the date rule can have):")
for n in res["S2_nights"]:
    pl = n["pass_local"]
    print(f"  night {n['k']} pass {pl}  sliver<= {int(pl[14:16]) + 1:>2} min  reconstructed R_DATE kept={n['R_DATE']['n_ranked']}  R_WM kept={n['R_WM']['n_ranked']}  tail_unarchived={n['unarchived_tail_min']}m")
