#!/usr/bin/env python3
"""Rewrite the death-toll flow around the snapshot file.

Two things were wrong, both found before arming:

1. /clear in 1.7.10 is `<player> [item] [data]` - there is NO count argument.
   The code passed one, so instead of taking the fee it would have wiped EVERY
   gold coin the player owned. Payment is now taken by editing the snapshot
   before it is restored, which removes exactly the price and nothing else.

2. Finding the grave by scanning recently-written region files was guesswork.
   The snapshot already carries GraveLocation, so the coordinates are exact and
   no region scan happens at all.

The snapshot stores items with STRING ids, unlike playerdata, so no id mapping
is needed here.
"""
import re, shutil, sys, time

PATH = "/home/duduserver/mctools/mc-deathtoll.py"
s = open(PATH, encoding="utf-8").read()
if "read_snapshot" in s:
    print("already rewritten"); sys.exit(0)

# ---- drop the region scan, add snapshot IO -------------------------------
OLD_SCAN = s[s.index("def recent_graves("):s.index("def block_is_gone(")]
NEW_IO = '''def snapshot_path(fid):
    return f"{ROOT}/world/data/inventory-{fid}.dat"


def read_snapshot(fid):
    """(root_compound, items_list, grave_xyz). Items carry STRING ids here."""
    import gzip
    p = snapshot_path(fid)
    raw = open(p, "rb").read()
    try:
        data = gzip.decompress(raw)
    except Exception:
        data = raw
    nm, root = nbtio.parse(data)
    inv = root.get("Inventory")
    items = inv[1]["Items"][1][1] if inv else []
    gl = root.get("GraveLocation")
    xyz = None
    if gl:
        g = gl[1]
        xyz = (g["X"][1], g["Y"][1], g["Z"][1])
    return nm, root, items, xyz


def charge_snapshot(fid, nm, root, price):
    """Remove exactly `price` coins from the snapshot, then write it back.

    This IS the payment. /clear cannot do it - 1.7.10 has no count argument and
    would take every coin the player owns.
    """
    import gzip
    items = root["Inventory"][1]["Items"][1][1]
    left = price
    keep = []
    for st in items:
        if left <= 0 or not isinstance(st, dict):
            keep.append(st); continue
        name, dmg, cnt = stack_id(st)
        is_coin = (name == COIN[0] and dmg == COIN[1]) or name == COIN_ALT[0]
        if not is_coin:
            keep.append(st); continue
        take = min(cnt, left)
        left -= take
        if cnt - take > 0:
            st["Count"] = (1, cnt - take)
            keep.append(st)
        # a stack reduced to zero is simply dropped
    if left > 0:
        return False, left           # should never happen; caller re-checks
    root["Inventory"][1]["Items"] = (9, (10, keep))
    p = snapshot_path(fid)
    shutil.copy2(p, p + ".pre-toll")
    with open(p, "wb") as f:
        f.write(gzip.compress(nbtio.serialise(nm, root)))
    read_snapshot(fid)               # prove it reads back before we rely on it
    return True, 0


'''
s = s.replace(OLD_SCAN, NEW_IO)
s = s.replace("import glob, gzip, json, os, re, subprocess, sys, time",
              "import glob, gzip, json, os, re, shutil, subprocess, sys, time")

# ---- rewrite settle() ----------------------------------------------------
OLD_SETTLE = s[s.index("def settle("):s.index("def quote(")]
NEW_SETTLE = '''def settle(player, snapshot_id, dry=False):
    uuid = uuid_of(player)
    try:
        nm, root, items, xyz = read_snapshot(snapshot_id)
    except Exception as e:
        audit(f"{player}: snapshot {snapshot_id} unreadable ({e}) - leaving alone")
        return "no-snapshot"

    pts, coins, counts = appraise(items)
    price = price_for(pts)
    audit(f"{player}: value={pts:.0f} price={price} coins={coins} "
          f"S{counts['S']} A{counts['A']} B{counts['B']} C{counts['C']} grave={xyz}")

    if dry:
        print(f"  {player}: cargo {pts:.0f} pts -> {price} coins; had {coins}; "
              f"would {'PAY' if coins >= price else 'take the grave'}; grave {xyz}")
        return "dry"

    if coins < price:
        say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
             {"text": "GRAVE", "color": "gray", "bold": True},
             {"text": " \\u00b7 ", "color": "dark_gray"},
             {"text": "Insuring that load would have cost ", "color": "white"},
             {"text": f"{price} gold coins", "color": "gold"},
             {"text": f". You had {coins}.", "color": "white"}])
        say(player, ["", {"text": "   Your grave is where you fell. Carry coins and it comes home with you.",
                          "color": "gray", "italic": True}])
        return "unpaid"

    if not xyz:
        audit(f"{player}: snapshot has no GraveLocation - leaving alone")
        return "no-location"

    # wait for the respawn: restoring into a corpse loses everything
    for _ in range(60):
        if uuid and player_alive(uuid):
            break
        time.sleep(2)
    else:
        audit(f"{player}: never respawned in time - leaving the grave")
        return "timeout"

    # take the fee out of the snapshot BEFORE restoring it
    ok, short = charge_snapshot(snapshot_id, nm, root, price)
    if not ok:
        audit(f"{player}: could not take {price} from the snapshot (short {short})")
        return "charge-failed"

    # remove the grave FIRST; if it survives, the items would exist twice
    x, y, z = xyz
    console(f"setblock {x} {y} {z} minecraft:air 0 replace", 0.8)
    if not block_is_gone(x, y, z):
        audit(f"{player}: grave at {x},{y},{z} would not clear - ABORTED, refunding")
        shutil.copy2(snapshot_path(snapshot_id) + ".pre-toll",
                     snapshot_path(snapshot_id))
        say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
             {"text": "Could not clear your grave, so nothing was charged. "
                      "It is still where you fell.", "color": "yellow"}])
        return "grave-stuck"

    console(f"ob_inventory restore {player} {snapshot_id}", 1.2)

    say(player, ["", {"text": "\\u00bb ", "color": "dark_gray"},
         {"text": "INSURED", "color": "gold", "bold": True},
         {"text": " \\u00b7 ", "color": "dark_gray"},
         {"text": "Everything came back with you.", "color": "white"}])
    say(player, ["", {"text": f"   {price} gold coins", "color": "gold"},
         {"text": f" spent \\u00b7 {coins - price} left \\u00b7 load valued at {pts:.0f}",
          "color": "gray", "italic": True}])
    audit(f"{player}: PAID {price}, restored {snapshot_id}, grave cleared at {x},{y},{z}")
    return "paid"


'''
s = s.replace(OLD_SETTLE, NEW_SETTLE)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("rewritten: payment via snapshot edit, grave coords from GraveLocation, no /clear")
