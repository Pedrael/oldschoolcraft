#!/usr/bin/env python3
"""Remove the grave the moment we know the player can pay, not after respawn.

Dudu spotted the hole. The grave stood in the world for as long as the dead
player took to click respawn - which can be minutes - and anyone else could
walk up and empty it. The victim then respawns to nothing while somebody else
carries his gear, and the mechanic sees a missing grave and concludes he looted
it himself.

Affordability is already known at the moment of death, because the snapshot
holds both the cargo and the coins. So the decision can be made immediately:

    can pay   -> clear the grave NOW, before anyone can reach it. The snapshot
                 is the only copy from that point on, and it is authoritative.
                 Restore when the respawn is confirmed.
    cannot pay -> leave the grave completely alone. Exactly today's behaviour.

That removes the window entirely rather than narrowing it, and needs no grave
to be rebuilt, because the grave is only ever destroyed in the branch where the
items are coming back anyway.

If the player logs off without respawning, the snapshot is still on disk and is
handed back on their next join - see the pending queue in mc-watcher.
"""
import shutil, sys, time

PATH = "/home/duduserver/mctools/mc-deathtoll.py"
s = open(PATH, encoding="utf-8").read()
if "PENDING" in s:
    print("already patched"); sys.exit(0)

# ---- move the grave removal to immediately after the affordability check ---
OLD = s[s.index("    if not xyz:"):s.index("    console(f\"ob_inventory restore")]
NEW = '''    if not xyz:
        audit(f"{player}: snapshot has no GraveLocation - leaving alone")
        return "no-location"

    x, y, z = xyz

    # He can pay, so the grave dies NOW - before he has respawned and before
    # anybody else can walk over and empty it. From here the snapshot is the
    # only copy and it is authoritative.
    if not grave_present(x, y, z):
        audit(f"{player}: grave at {x},{y},{z} already gone - no charge")
        return "already-looted"

    console(f"setblock {x} {y} {z} minecraft:air 0 replace", 0.8)
    if grave_present(x, y, z):
        audit(f"{player}: grave at {x},{y},{z} would not clear - nothing charged")
        say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
             {"text": "Could not clear your grave, so nothing was charged. "
                      "It is still where you fell.", "color": "yellow"}])
        return "grave-stuck"
    audit(f"{player}: grave cleared at {x},{y},{z} - snapshot is now the only copy")

    say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
         {"text": "INSURED", "color": "gold", "bold": True},
         {"text": " \\u00b7 ", "color": "dark_gray"},
         {"text": "Your things are held safe. Respawn to collect them.",
          "color": "white"}])

    # Record it before waiting. If he closes the game instead of respawning,
    # mc-watcher hands it back on his next join rather than losing it.
    remember_pending(player, snapshot_id, price)

    # Now wait for a respawn we can believe in.
    MIN_WAIT = 3
    died_at = time.time()
    time.sleep(MIN_WAIT)
    for _ in range(90):
        if uuid and respawned(uuid, died_at):
            break
        time.sleep(2)
    else:
        audit(f"{player}: no respawn yet - snapshot {snapshot_id} left pending")
        return "pending"

    ok, short = charge_snapshot(snapshot_id, nm, root, price)
    if not ok:
        audit(f"{player}: could not take {price} from the snapshot (short {short})")
        return "charge-failed"

'''
s = s.replace(OLD, NEW)

# ---- drop the now-duplicated wait/clear block that used to follow ---------
import re
s = re.sub(r"\n    # Wait for a respawn we can actually believe in.*?return \"no-respawn\"\n\n",
           "\n", s, flags=re.S)

# ---- pending queue so an unclaimed snapshot is never lost -----------------
PENDING = '''

PENDING = "/home/duduserver/mctools/deathtoll-pending.json"


def remember_pending(player, fid, price):
    """Note that this player is owed a snapshot, in case they log off dead."""
    try:
        d = json.load(open(PENDING))
    except Exception:
        d = {}
    d[player] = {"fid": fid, "price": price, "when": time.time()}
    try:
        json.dump(d, open(PENDING, "w"), indent=1)
    except OSError:
        pass


def clear_pending(player):
    try:
        d = json.load(open(PENDING))
    except Exception:
        return
    if d.pop(player, None) is not None:
        json.dump(d, open(PENDING, "w"), indent=1)

'''
s = s.replace("\nARMED_FLAG =", PENDING + "\nARMED_FLAG =")

# clear the pending marker once the items are actually back
s = s.replace('    audit(f"{player}: restore landed - {got} stacks")',
              '    audit(f"{player}: restore landed - {got} stacks")\n'
              '    clear_pending(player)')

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("patched: grave removed the moment affordability is known; pending queue added")
