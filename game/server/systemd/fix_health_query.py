#!/usr/bin/env python3
"""Teach mc-health the difference between a hung boot and a boot WAITING FOR A HUMAN.

Adding Mekanism made FML ask whether to drop one stale registry entry. It then
blocked on readLine() from stdin, which nothing answers, and the boot stalled at
"Preparing level" - visually identical to the 2026-08-21 deadlock.

mc-health saw no "Done (", called it unhealthy and restarted. The restart hit
the same question and stalled again. Left alone it would have looped forever,
and each restart destroys the evidence in latest.log.

A restart cannot fix a question. So this state is now detected, reported
distinctly, and explicitly NOT restarted. The fix is a human answering it:

    touch fml-confirm-once.flag && systemctl restart minecraft

which makes start.sh pass -Dfml.queryResult=confirm exactly once. Check WHAT is
being dropped before confirming - it deletes those blocks/items from the world.

Boot grace also goes from 7 to 15 minutes: adding a mod re-allocates ids across
the whole registry and a first boot legitimately takes far longer than a normal
one.
"""
import shutil, sys, time

PATH = "/home/duduserver/mctools/mc-health.py"
s = open(PATH, encoding="utf-8").read()
if "awaiting_fml_query" in s:
    print("already patched"); sys.exit(0)

s = s.replace("BOOT_GRACE    = 420    # 7 min: world load on this pack takes ~1 min, be generous",
              "BOOT_GRACE    = 900    # 15 min: adding a mod re-allocates ids and boots slowly")

OLD = '''    if "Done (" not in log:
        return False, "startup never completed - no 'Done (' in latest.log"'''
NEW = '''    if "Done (" not in log:
        # A boot blocked on an FML startup question looks exactly like a hung
        # boot, but restarting re-asks the same question forever and wipes the
        # log each time. Never restart this - it needs a person.
        if awaiting_fml_query(log):
            return False, ("BLOCKED: FML is waiting for a yes/no answer about the "
                           "world registry. Do NOT restart - inspect what it wants "
                           "to drop, then: touch fml-confirm-once.flag && "
                           "systemctl restart minecraft")
        return False, "startup never completed - no 'Done (' in latest.log"'''
assert s.count(OLD) == 1, "check() anchor"
s = s.replace(OLD, NEW)

HELPER = '''

def awaiting_fml_query(log):
    """Is the boot stalled on an FML confirmation prompt rather than deadlocked?"""
    return any(m in log for m in (
        "missing blocks/items will get removed",
        "Forge Mod Loader detected missing blocks/items",
        "There are unidentified mappings in this world",
    ))
'''
s = s.replace("\ndef check():", HELPER + "\ndef check():")

# never auto-restart a question
OLD2 = '''    if not ok and may_restart:
        audit("restarting minecraft")
        subprocess.run(["sudo", "-n", "systemctl", "restart", "minecraft"])'''
NEW2 = '''    if not ok and may_restart:
        if reason.startswith("BLOCKED:"):
            audit("NOT restarting - server is waiting for a human to answer FML")
        else:
            audit("restarting minecraft")
            subprocess.run(["sudo", "-n", "systemctl", "restart", "minecraft"])'''
assert s.count(OLD2) == 1, "restart anchor"
s = s.replace(OLD2, NEW2)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("patched mc-health.py: FML-query state detected, never auto-restarted; grace 7 -> 15 min")
