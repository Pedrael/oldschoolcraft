#!/usr/bin/env python3
"""Close the duplication window found by testing on 2026-08-24.

Three test deaths turned 504 items into 998. The mechanic waited for the
respawn, restored the snapshot, then cleared the grave - and in the seconds
between respawning and the clear, the player simply walked over and looted his
own grave. Restored copy plus looted copy equals two of everything.

The order is now:

    respawn confirmed
    -> is the grave still a grave?   no  -> he already looted it. Do nothing,
                                            charge nothing. He has his things.
    -> clear the grave                      nothing left to loot
    -> take the fee
    -> restore
    -> did the items actually land?   no  -> refund, trip the breaker, and tell
                                            him the snapshot id so it can be
                                            handed back by hand

Clearing before restoring was the original order, and I changed it on the
theory that a failed restore would mean total loss. That was wrong: the
snapshot file is never deleted, so a failed restore is always recoverable with
    /ob_inventory spawn <id>
The player is now told that id when it happens, and the breaker stops anyone
else hitting it. A recoverable failure beats a live duplication bug.
"""
import shutil, sys, time

PATH = "/home/duduserver/mctools/mc-deathtoll.py"
s = open(PATH, encoding="utf-8").read()
if "grave_present" in s:
    print("already patched"); sys.exit(0)

# a positive check: is the grave still THERE, rather than "is it air"
HELPER = '''

def grave_present(x, y, z):
    """True if a grave block is still standing at these coordinates.

    Used to detect a player who looted their own grave during the respawn
    wait - restoring on top of that is how 504 items became 998.
    """
    before = os.path.getsize(LOG)
    console(f"testforblock {x} {y} {z} OpenBlocks:grave", 1.2)
    try:
        f = open(LOG, "r", encoding="utf-8", errors="replace")
        f.seek(before)
        out = f.read()
    except OSError:
        return False
    return "Successfully found the block" in out

'''
s = s.replace("\ndef player_alive(", HELPER + "\ndef player_alive(") \
    if "def player_alive(" in s else s.replace("\ndef inventory_size(", HELPER + "\ndef inventory_size(")

# rewrite the tail of settle(): clear first, then charge, then restore
OLD = s[s.index("    # take the fee out of the snapshot BEFORE restoring it"):s.index('    say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},\n         {"text": "INSURED"')]
NEW = '''    x, y, z = xyz

    # Did he already loot it while we waited? If so he has his things and owes
    # nothing - restoring on top would duplicate the lot.
    if not grave_present(x, y, z):
        audit(f"{player}: grave at {x},{y},{z} already gone (looted) - no charge")
        return "already-looted"

    # Clear it BEFORE restoring, so there is nothing left to walk back to.
    console(f"setblock {x} {y} {z} minecraft:air 0 replace", 0.8)
    if grave_present(x, y, z):
        audit(f"{player}: grave at {x},{y},{z} would not clear - nothing charged")
        say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
             {"text": "Could not clear your grave, so nothing was charged. "
                      "It is still where you fell.", "color": "yellow"}])
        return "grave-stuck"

    ok, short = charge_snapshot(snapshot_id, nm, root, price)
    if not ok:
        audit(f"{player}: could not take {price} from the snapshot (short {short})")
        return "charge-failed"

    console(f"ob_inventory restore {player} {snapshot_id}", 1.5)

    # The server logs success even when the items go nowhere, so read it back.
    console("save-all", 2.0)
    got = inventory_size(uuid)
    if not got:
        audit(f"{player}: restore did NOT land - refunding, snapshot kept as {snapshot_id}")
        shutil.copy2(snapshot_path(snapshot_id) + ".pre-toll",
                     snapshot_path(snapshot_id))
        say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
             {"text": "RESTORE FAILED", "color": "red", "bold": True},
             {"text": " \\u00b7 ", "color": "dark_gray"},
             {"text": "You were not charged. Your items are safe - run this:",
              "color": "white"}])
        say(player, ["", {"text": f"  /ob_inventory spawn {snapshot_id}", "color": "yellow"}])
        return "restore-failed"
    audit(f"{player}: restore landed - {got} stacks")

'''
s = s.replace(OLD, NEW)

# already-looted is harmless: the player kept everything, nothing was charged
s = s.replace('HARMLESS = {"unpaid", "no-respawn", "no-grave", "no-snapshot", "dry", "paid"}',
              'HARMLESS = {"unpaid", "no-respawn", "no-grave", "no-snapshot", "dry", "paid",\n'
              '            "already-looted"}')

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("patched: grave cleared before restore; looted graves detected and skipped")
