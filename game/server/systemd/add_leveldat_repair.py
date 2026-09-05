#!/usr/bin/env python3
"""Let mc-health repair a truncated level.dat by itself.

Twice now an unclean shutdown has truncated world/level.dat to 0 bytes, and
both times the next boot deadlocked in futex_do_wait while reading it, holding
port 25565 open so everything looked healthy. The August one went unnoticed for
13 hours; tonight's for about ten minutes.

The repair is deterministic and already scripted: stop, restore from the
world's own level.dat_old, start. mc-health can do that unattended.

It is safe to automate because restore_leveldat.py refuses to act unless the
live file is genuinely unreadable AND the fallback both gunzips and carries the
Forge registry. If either check fails it does nothing, and this stays a
report-only failure like any other.

The EcoFlow now backing the machine covers short outages, but it is invisible to
the OS - no USB HID, no power_supply entry - so a long one still ends this way.
"""
import shutil, sys, time

PATH = "/home/duduserver/mctools/mc-health.py"
s = open(PATH, encoding="utf-8").read()
if "leveldat_broken" in s:
    print("already patched"); sys.exit(0)

HELPER = '''

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

'''
s = s.replace("\ndef awaiting_fml_query(", HELPER + "\ndef awaiting_fml_query(")

OLD = '''        if awaiting_fml_query(log):'''
NEW = '''        if leveldat_broken(log):
            return False, ("BROKEN: world/level.dat is unreadable - an unclean "
                           "shutdown truncated it. Repairable from level.dat_old")
        if awaiting_fml_query(log):'''
assert s.count(OLD) == 1, "check anchor"
s = s.replace(OLD, NEW)

OLD2 = '''        if reason.startswith("BLOCKED:"):'''
NEW2 = '''        if reason.startswith("BROKEN:"):
            repair_leveldat()
        elif reason.startswith("BLOCKED:"):'''
assert s.count(OLD2) == 1, "restart anchor"
s = s.replace(OLD2, NEW2)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("patched: mc-health now repairs a truncated level.dat instead of looping on it")
