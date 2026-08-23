#!/usr/bin/env python3
"""Fix the bug that lost DuduPhudu's inventory on 2026-08-24.

player_alive() read playerdata off DISK, and Minecraft does not write that file
when someone dies. Four seconds after the death it still said "health 20,
alive", so the wait-for-respawn loop exited on its first pass and
/ob_inventory restore fired while the player was still on the death screen.
The server dutifully reported success. The items went into a player object that
the respawn then discarded.

Two changes, because one of them alone would not have been enough:

1. RESPAWN DETECTION THAT CANNOT BE FOOLED. save-all is issued to force
   playerdata to disk, and the file is only trusted once its mtime is NEWER
   than the death itself. A stale file can no longer answer the question. On
   top of that a hard floor of MIN_WAIT seconds applies - nobody clicks respawn
   in under three.

2. VERIFY THE OUTCOME, NOT THE COMMAND. "Restored inventory for player X" is
   printed even when the items go nowhere, so it proves nothing. The player's
   inventory is now read back after the restore, and if it is still empty the
   grave is LEFT ALONE and the player is told to loot it normally. Better a
   grave than a confident lie.
"""
import re, shutil, sys, time

PATH = "/home/duduserver/mctools/mc-deathtoll.py"
s = open(PATH, encoding="utf-8").read()
if "inventory_size" in s:
    print("already patched"); sys.exit(0)

# ---- 1. trustworthy respawn detection ------------------------------------
OLD = s[s.index("def player_alive("):s.index("def uuid_of(")]
NEW = '''def inventory_size(uuid):
    """Stack count from playerdata on disk. Callers must force a save first."""
    p = f"{ROOT}/world/playerdata/{uuid}.dat"
    try:
        nm, root = nbtio.parse(gzip.decompress(open(p, "rb").read()))
    except Exception:
        return None
    inv = root.get("Inventory")
    return len([x for x in inv[1][1] if isinstance(x, dict)]) if inv else 0


def respawned(uuid, since):
    """Alive AND the file is newer than the death.

    Health alone is a trap: Minecraft does not write playerdata on death, so a
    stale file reports the player hale and hearty for as long as it likes. Only
    a file written AFTER the death can answer this.
    """
    p = f"{ROOT}/world/playerdata/{uuid}.dat"
    console("save-all", 1.5)
    try:
        if os.path.getmtime(p) <= since:
            return False
        nm, root = nbtio.parse(gzip.decompress(open(p, "rb").read()))
    except Exception:
        return False
    h = root.get("HealF") or root.get("Health")
    return bool(h) and h[1] > 0


'''
s = s.replace(OLD, NEW)

# ---- 2. use it, and verify the restore actually landed -------------------
OLD2 = s[s.index("    # wait for the respawn"):s.index("    # take the fee")]
NEW2 = '''    # Wait for a respawn we can actually believe in. MIN_WAIT is a floor:
    # nobody clicks the respawn button in under three seconds, and restoring
    # into the death screen is precisely how this went wrong the first time.
    MIN_WAIT = 3
    died_at = time.time()
    time.sleep(MIN_WAIT)
    for _ in range(60):
        if uuid and respawned(uuid, died_at):
            break
        time.sleep(2)
    else:
        audit(f"{player}: no confirmed respawn - leaving the grave alone")
        say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
             {"text": "Could not confirm your respawn, so nothing was charged. "
                      "Your grave is where you fell.", "color": "yellow"}])
        return "no-respawn"

'''
s = s.replace(OLD2, NEW2)

# ---- 3. prove the items landed before touching the grave ----------------
OLD3 = '''    console(f"ob_inventory restore {player} {snapshot_id}", 1.2)

    x, y, z = xyz'''
NEW3 = '''    console(f"ob_inventory restore {player} {snapshot_id}", 1.5)

    # "Restored inventory for player X" is logged even when the items go
    # nowhere, so the server's own success message proves nothing. Read the
    # inventory back instead.
    console("save-all", 2.0)
    got = inventory_size(uuid)
    if not got:
        audit(f"{player}: restore reported success but inventory is still empty "
              f"- REFUNDING and leaving the grave")
        shutil.copy2(snapshot_path(snapshot_id) + ".pre-toll",
                     snapshot_path(snapshot_id))
        say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
             {"text": "The restore did not take, so you were not charged. "
                      "Your grave is still where you fell.", "color": "yellow"}])
        return "restore-failed"
    audit(f"{player}: restore landed - {got} stacks")

    x, y, z = xyz'''
assert s.count(OLD3) == 1, "restore anchor"
s = s.replace(OLD3, NEW3)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("patched: respawn must be proven by a fresh file; restore verified by reading it back")
