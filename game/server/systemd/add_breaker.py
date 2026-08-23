#!/usr/bin/env python3
"""Give the death toll a circuit breaker so it disarms ITSELF.

Last time this failed, it kept running because disarming depended on a human
noticing. Two other players were online at the time; the bug was deterministic,
so any death of theirs would have destroyed their inventory too.

Anything that could cost somebody items now trips the breaker: the armed flag
is deleted, the failure is announced in chat, and every later death falls
straight through to a normal grave until a person looks at it. It fails to the
boring outcome, on its own, immediately.

Trips on:
  restore-failed   the restore did not land - the exact bug that cost an
                   inventory on 2026-08-24
  grave-stuck      items restored but the grave would not clear (duplicate)
  charge-failed    could not take the fee cleanly
  no-location      snapshot has no GraveLocation to clear
  any exception    an unhandled error means nobody knows what state this is in

Does NOT trip on:
  unpaid / no-respawn / no-grave / no-snapshot - these all end with the player
  keeping a perfectly good grave, which is exactly what would have happened
  without the mechanic. Nothing is lost, so there is nothing to stop.
"""
import shutil, sys, time

PATH = "/home/duduserver/mctools/mc-deathtoll.py"
s = open(PATH, encoding="utf-8").read()
if "def trip(" in s:
    print("already has a breaker"); sys.exit(0)

BREAKER = '''

ARMED_FLAG = "/home/duduserver/mctools/deathtoll.armed"

# Outcomes that mean somebody could be out of pocket. Anything here disarms the
# mechanic immediately rather than waiting for a human to notice.
TRIPPING = {"restore-failed", "grave-stuck", "charge-failed", "no-location", "exception"}

# Outcomes that are simply the old behaviour: the player keeps their grave.
# Nothing is lost, so there is nothing to trip.
HARMLESS = {"unpaid", "no-respawn", "no-grave", "no-snapshot", "dry", "paid"}


def trip(reason, player=""):
    """Disarm, loudly. Costs one restart of nothing and saves an inventory."""
    was_armed = os.path.exists(ARMED_FLAG)
    try:
        os.remove(ARMED_FLAG)
    except OSError:
        pass
    audit(f"BREAKER TRIPPED ({reason}) for {player} - mechanic DISARMED")
    if not was_armed:
        return
    try:
        console("tellraw @a " + json.dumps(["",
            {"text": "\\u00bb ", "color": "dark_gray"},
            {"text": "INSURANCE OFF", "color": "red", "bold": True},
            {"text": " \\u00b7 ", "color": "dark_gray"},
            {"text": "Death insurance just failed and has shut itself down.",
             "color": "white"}], ensure_ascii=False), 0.3)
        console("tellraw @a " + json.dumps(["",
            {"text": "   Deaths now leave a normal grave. Nobody will be charged "
                     "until this is looked at.", "color": "gray", "italic": True}],
            ensure_ascii=False), 0.3)
    except Exception:
        pass

'''
s = s.replace("\n# ---------------------------------------------------------------- flow --",
              BREAKER + "\n# ---------------------------------------------------------------- flow --")

# route every settle() result through the breaker
OLD_MAIN = s[s.index('    elif len(sys.argv) >= 3:'):]
NEW_MAIN = '''    elif len(sys.argv) >= 3:
        player, fid = sys.argv[1], sys.argv[2]
        dry = "--dry-run" in sys.argv
        try:
            outcome = settle(player, fid, dry=dry)
        except Exception as e:
            import traceback
            audit(f"{player}: UNHANDLED {type(e).__name__}: {e}")
            audit(traceback.format_exc())
            if not dry:
                trip("exception", player)
            print("exception")
            sys.exit(1)
        if not dry and outcome in TRIPPING:
            trip(outcome, player)
        print(outcome)
    else:
        print(__doc__)
'''
s = s.replace(OLD_MAIN, NEW_MAIN)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("added: self-disarming circuit breaker on every harmful outcome")
