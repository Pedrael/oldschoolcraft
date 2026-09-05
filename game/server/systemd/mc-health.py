#!/usr/bin/env python3
"""mc-health - is the server actually serving, or just holding the port open?

On 2026-08-21 an unclean shutdown truncated world/level.dat to 0 bytes. The
server then deadlocked during world load and sat in futex_do_wait for 13 hours.
Every check we had said it was fine:

  systemctl is-active   -> active   (the JVM was alive, just blocked)
  port 25565            -> listening (bound before world load ever started)
  mc-watcher            -> quiet    (a server that stops logging looks the same
                                     as a server with nothing happening)

So this asserts the three things those miss:

  1. startup COMPLETED       - "Done (" appears in the current latest.log
  2. the log is ADVANCING    - it has grown, or the server answers on the
                               console, within STALE_AFTER seconds
  3. the console RESPONDS    - write to the FIFO and see output appear

Any failure is logged and announced once; recovery is announced too, so the
log does not fill with repeats. --restart lets it act rather than just report.
"""
import json, os, re, subprocess, sys, time

ROOT  = "/home/duduserver/minecraft/1.7.10"
LOG   = f"{ROOT}/logs/latest.log"
FIFO  = "/run/minecraft/console.in"
STATE = "/home/duduserver/mctools/health-state.json"
AUDIT = "/home/duduserver/mctools/health.log"

STALE_AFTER   = 900    # 15 min with no new log line AND no console reply
BOOT_GRACE    = 900    # 15 min: adding a mod re-allocates ids and boots slowly


def audit(msg):
    with open(AUDIT, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}\n")


def load():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def uptime_seconds():
    out = subprocess.run(
        ["systemctl", "show", "minecraft", "-p", "ActiveEnterTimestampMonotonic",
         "--value"], capture_output=True, text=True).stdout.strip()
    try:
        started = int(out) / 1_000_000
    except ValueError:
        return None
    with open("/proc/uptime") as f:
        now = float(f.read().split()[0])
    return now - started


def console_replies(timeout=6.0):
    """Write to the FIFO and see whether the log grows. A deadlocked server
    accepts the write (the FIFO has a permanent reader) but never answers."""
    if not os.path.exists(FIFO):
        return False
    try:
        before = os.path.getsize(LOG)
    except OSError:
        return False
    try:
        # non-blocking open: if nothing is reading, do not hang forever
        fd = os.open(FIFO, os.O_WRONLY | os.O_NONBLOCK)
        os.write(fd, b"seed\n")     # harmless, prints the world seed
        os.close(fd)
    except OSError:
        return False
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(0.4)
        try:
            if os.path.getsize(LOG) > before:
                return True
        except OSError:
            return False
    return False




def leveldat_broken(log):
    """Is the boot stuck because world/level.dat cannot be read?

    Distinct from a plain hang: this one has a known, scripted repair, so it
    can be fixed rather than merely restarted. Restarting alone just meets the
    same corrupt file again - which is exactly what happened on 2026-09-05.
    """
    return ("Exception reading ./world/level.dat" in log
            and "Done (" not in log)


def repair_leveldat():
    """Stop, restore level.dat from the world's own level.dat_old, start."""
    audit("level.dat unreadable - attempting the scripted repair")
    subprocess.run(["sudo", "-n", "systemctl", "stop", "minecraft"],
                   timeout=120, capture_output=True)
    time.sleep(5)
    # a boot that never loaded the world has nothing worth saving
    pid = subprocess.run(["systemctl", "show", "minecraft", "-p", "MainPID", "--value"],
                         capture_output=True, text=True).stdout.strip()
    if pid and pid != "0":
        subprocess.run(["sudo", "-n", "kill", "-9", pid], capture_output=True)
        time.sleep(3)
    r = subprocess.run(["/usr/bin/python3", "/home/duduserver/mctools/restore_leveldat.py"],
                       capture_output=True, text=True, timeout=180)
    audit("restore_leveldat: " + " | ".join(
        l.strip() for l in r.stdout.splitlines() if l.strip())[:300])
    if r.returncode != 0:
        audit("repair FAILED - leaving the server down for a human")
        return False
    subprocess.run(["sudo", "-n", "systemctl", "reset-failed", "minecraft"],
                   capture_output=True)
    subprocess.run(["sudo", "-n", "systemctl", "start", "minecraft"], capture_output=True)
    audit("repair applied, server restarted")
    return True


def awaiting_fml_query(log):
    """Is the boot stalled on an FML confirmation prompt rather than deadlocked?"""
    return any(m in log for m in (
        "missing blocks/items will get removed",
        "Forge Mod Loader detected missing blocks/items",
        "There are unidentified mappings in this world",
    ))

def check():
    """-> (ok, reason)"""
    state = subprocess.run(["systemctl", "is-active", "minecraft"],
                           capture_output=True, text=True).stdout.strip()
    if state != "active":
        return False, f"service is {state}"

    up = uptime_seconds()
    if up is not None and up < BOOT_GRACE:
        return True, f"starting up ({int(up)}s, within grace)"

    try:
        log = open(LOG, "r", encoding="utf-8", errors="replace").read()
    except OSError as e:
        return False, f"cannot read latest.log: {e}"

    if "Done (" not in log:
        # A boot blocked on an FML startup question looks exactly like a hung
        # boot, but restarting re-asks the same question forever and wipes the
        # log each time. Never restart this - it needs a person.
        if leveldat_broken(log):
            return False, ("BROKEN: world/level.dat is unreadable - an unclean "
                           "shutdown truncated it. Repairable from level.dat_old")
        if awaiting_fml_query(log):
            return False, ("BLOCKED: FML is waiting for a yes/no answer about the "
                           "world registry. Do NOT restart - inspect what it wants "
                           "to drop, then: touch fml-confirm-once.flag && "
                           "systemctl restart minecraft")
        return False, "startup never completed - no 'Done (' in latest.log"

    for pat, why in [(r"Exception reading \./world/level\.dat", "level.dat unreadable"),
                     (r"Failed to start the minecraft server", "server failed to start")]:
        if re.search(pat, log):
            return False, why

    age = time.time() - os.path.getmtime(LOG)
    if age > STALE_AFTER and not console_replies():
        return False, (f"log idle {int(age/60)} min and console did not answer "
                       f"- server is hung")
    return True, "ok"


def main():
    may_restart = "--restart" in sys.argv
    ok, reason = check()
    prev = load().get("ok")

    if not ok and prev is not False:
        audit(f"UNHEALTHY: {reason}")
    elif ok and prev is False:
        audit(f"recovered: {reason}")

    json.dump({"ok": ok, "reason": reason, "when": time.time()},
              open(STATE, "w"), indent=1)

    print(("OK   " if ok else "FAIL ") + reason)

    if not ok and may_restart:
        if reason.startswith("BROKEN:"):
            repair_leveldat()
        elif reason.startswith("BLOCKED:"):
            audit("NOT restarting - server is waiting for a human to answer FML")
        else:
            audit("restarting minecraft")
            subprocess.run(["sudo", "-n", "systemctl", "restart", "minecraft"])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
