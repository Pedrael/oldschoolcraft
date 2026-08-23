#!/usr/bin/env python3
"""Death insurance: pay gold coins to keep your inventory, or take the grave.

Two problems, one mechanic. Graves are a chore, and gold coins are a currency
nobody has any reason to pick up - 788 of them sit in chests while all three
players carry a combined total of one.

On death:
  * work out what the load you were carrying is WORTH
  * if you have enough coins to cover it, they are consumed and your whole
    inventory comes straight back
  * if you do not, nothing changes at all - the grave is there, exactly as
    before, and you are told what it would have cost

The downside is therefore bounded: the worst case is today's behaviour. This
adds an option, it never takes one away.

Price scales with the load, so dying in a stone pickaxe is nearly free and
dying while hauling a nether star hurts. That also means carrying treasure is
a real decision rather than a free action.

WHY THE GRAVE MUST DIE: /ob_inventory restore hands the snapshot back to the
player. If the grave block also survives, the items exist twice. So the grave
is located and removed FIRST, and the restore only happens once that is
confirmed - a normal grave is a far better failure mode than duplication.
"""
import glob, gzip, json, os, re, shutil, subprocess, sys, time

sys.path.insert(0, "/home/duduserver/mctools")
import nbtio

ROOT   = "/home/duduserver/minecraft/1.7.10"
FIFO   = "/run/minecraft/console.in"
LOG    = f"{ROOT}/logs/latest.log"
STATE  = "/home/duduserver/mctools/deathtoll-state.json"
AUDIT  = "/home/duduserver/mctools/deathtoll.log"

COIN      = ("Thaumcraft:ItemResource", 18)   # Gold Coin, verified in game
COIN_ALT  = ("IC2:itemCoin", 0)               # Industrial Credit, also accepted
DIVISOR   = 20      # value points per coin (lower = pricier)
MIN_PRICE = 1
MAX_PRICE = 48

# ---------------------------------------------------------------- value --
# Deliberately coarse. The point is that hauling treasure costs more than
# hauling cobblestone, not that every item is appraised exactly.
TIER_S = re.compile(r"nether_star|EldritchObject|manaResource:(4|9|14)|dragonstone|"
                    r"ichor|ItemResource:16|AtomicAlloy|divisionSigil|kingKey|"
                    r"aesirRing|primordial|gaia|terrasteel", re.I)
TIER_A = re.compile(r"diamond|emerald|manyullyn|cobalt|ardite|elementium|thaumium|"
                    r"ReinforcedAlloy|EnrichedAlloy|darkSteel|dark_steel|quantum|"
                    r"nano|neptunium|voidmetal|Ingot:0|Ingot:1|blaze_rod|ghast_tear|"
                    r"ender_eye|nether_wart", re.I)
TIER_B = re.compile(r"ingot|block|redstone|lapis|quartz|gold|iron|steel|bronze|"
                    r"silver|lead|copper|tin|manaResource|coal|obsidian", re.I)

PTS = {"S": 25.0, "A": 8.0, "B": 2.0, "C": 0.25}


def tier(name, dmg):
    key = f"{name}:{dmg}"
    if TIER_S.search(key): return "S"
    if TIER_A.search(key): return "A"
    if TIER_B.search(key): return "B"
    return "C"


def stack_id(s):
    """(string_name, damage, count) from a stack whose id may be string or numeric."""
    t, v = s.get("id", (8, ""))
    dmg = s.get("Damage", (2, 0))[1]
    cnt = s.get("Count", (1, 1))[1]
    return (v if t == 8 else str(v)), dmg, cnt


def appraise(items):
    """(value_points, coin_count, breakdown) for a list of stacks."""
    pts = 0.0
    coins = 0
    counts = {"S": 0, "A": 0, "B": 0, "C": 0}
    for s in items:
        if not isinstance(s, dict):
            continue
        name, dmg, cnt = stack_id(s)
        if (name == COIN[0] and dmg == COIN[1]) or name == COIN_ALT[0]:
            coins += cnt
            continue                      # the payment itself is not cargo
        k = tier(name, dmg)
        counts[k] += cnt
        # worn armour and held tools are the losses that actually sting
        mult = 2.0 if re.search(r"helmet|chestplate|leggings|boots|plate|sword|"
                                r"pickaxe|axe|shovel|bow|wand|staff", name, re.I) else 1.0
        pts += PTS[k] * cnt * mult
    return pts, coins, counts


def price_for(pts):
    import math
    return max(MIN_PRICE, min(MAX_PRICE, int(math.ceil(pts / DIVISOR))))


# ---------------------------------------------------------------- world --
def console(cmd, wait=0.4):
    if not os.path.exists(FIFO):
        return
    with open(FIFO, "w") as f:
        f.write(cmd + "\n")
    time.sleep(wait)


def say(player, parts):
    console("tellraw %s %s" % (player, json.dumps(parts, ensure_ascii=False)), 0.2)


def audit(msg):
    with open(AUDIT, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}\n")


def snapshot_path(fid):
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


def block_is_gone(x, y, z):
    """Confirm the grave really went. Never restore while it might still exist."""
    before = os.path.getsize(LOG)
    console(f"testforblock {x} {y} {z} minecraft:air", 1.2)
    try:
        tail = open(LOG, "r", encoding="utf-8", errors="replace")
        tail.seek(before)
        out = tail.read()
    except OSError:
        return False
    return "Successfully found the block" in out


def inventory_size(uuid):
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


def uuid_of(name):
    try:
        for p in json.load(open(f"{ROOT}/usercache.json")):
            if p["name"] == name:
                return p["uuid"]
    except Exception:
        pass
    return None



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
            {"text": "\u00bb ", "color": "dark_gray"},
            {"text": "INSURANCE OFF", "color": "red", "bold": True},
            {"text": " \u00b7 ", "color": "dark_gray"},
            {"text": "Death insurance just failed and has shut itself down.",
             "color": "white"}], ensure_ascii=False), 0.3)
        console("tellraw @a " + json.dumps(["",
            {"text": "   Deaths now leave a normal grave. Nobody will be charged "
                     "until this is looked at.", "color": "gray", "italic": True}],
            ensure_ascii=False), 0.3)
    except Exception:
        pass


# ---------------------------------------------------------------- flow --
def settle(player, snapshot_id, dry=False):
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
        say(player, ["", {"text": "\u00bb ", "color": "dark_gray"},
             {"text": "GRAVE", "color": "gray", "bold": True},
             {"text": " \u00b7 ", "color": "dark_gray"},
             {"text": "Insuring that load would have cost ", "color": "white"},
             {"text": f"{price} gold coins", "color": "gold"},
             {"text": f". You had {coins}.", "color": "white"}])
        say(player, ["", {"text": "   Your grave is where you fell. Carry coins and it comes home with you.",
                          "color": "gray", "italic": True}])
        return "unpaid"

    if not xyz:
        audit(f"{player}: snapshot has no GraveLocation - leaving alone")
        return "no-location"

    # Wait for a respawn we can actually believe in. MIN_WAIT is a floor:
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
        say(player, ["", {"text": "\u00bb ", "color": "dark_gray"},
             {"text": "Could not confirm your respawn, so nothing was charged. "
                      "Your grave is where you fell.", "color": "yellow"}])
        return "no-respawn"

    # take the fee out of the snapshot BEFORE restoring it
    ok, short = charge_snapshot(snapshot_id, nm, root, price)
    if not ok:
        audit(f"{player}: could not take {price} from the snapshot (short {short})")
        return "charge-failed"

    # ORDER MATTERS, and it is the opposite of what it first looks like.
    # Clearing the grave before restoring risks TOTAL LOSS if the restore
    # fails. Restoring first risks a DUPLICATE if the grave will not clear.
    # A duplicate is annoying and fixable; a lost inventory is not. So the
    # items go back first, and a stuck grave becomes a loud warning.
    console(f"ob_inventory restore {player} {snapshot_id}", 1.5)

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
        say(player, ["", {"text": "\u00bb ", "color": "dark_gray"},
             {"text": "The restore did not take, so you were not charged. "
                      "Your grave is still where you fell.", "color": "yellow"}])
        return "restore-failed"
    audit(f"{player}: restore landed - {got} stacks")

    x, y, z = xyz
    console(f"setblock {x} {y} {z} minecraft:air 0 replace", 0.8)
    if not block_is_gone(x, y, z):
        audit(f"{player}: RESTORED but grave at {x},{y},{z} would NOT clear - "
              f"possible duplicate, needs manual cleanup")
        say(player, ["", {"text": "» ", "color": "dark_gray"},
             {"text": "WARNING", "color": "red", "bold": True},
             {"text": " · ", "color": "dark_gray"},
             {"text": "Your items came back, but the grave would not clear.",
              "color": "white"}])
        say(player, ["", {"text": f"   Do NOT loot it - looting would duplicate. It is at {x} {y} {z}.",
                          "color": "yellow"}])

    say(player, ["", {"text": "\u00bb ", "color": "dark_gray"},
         {"text": "INSURED", "color": "gold", "bold": True},
         {"text": " \u00b7 ", "color": "dark_gray"},
         {"text": "Everything came back with you.", "color": "white"}])
    say(player, ["", {"text": f"   {price} gold coins", "color": "gold"},
         {"text": f" spent \u00b7 {coins - price} left \u00b7 load valued at {pts:.0f}",
          "color": "gray", "italic": True}])
    audit(f"{player}: PAID {price}, restored {snapshot_id}, grave cleared at {x},{y},{z}")
    return "paid"


def quote(player):
    """What would dying cost this player right now? No death required."""
    uuid = uuid_of(player)
    if not uuid:
        print(f"  {player}: unknown"); return
    p = f"{ROOT}/world/playerdata/{uuid}.dat"
    nm, root = nbtio.parse(gzip.decompress(open(p, "rb").read()))
    items = []
    for key in ("Inventory",):
        n = root.get(key)
        if n: items += [s for s in n[1][1] if isinstance(s, dict)]
    # playerdata uses NUMERIC ids; map them back so the tiers match
    try:
        idmap = json.load(open("/tmp/idmap.json"))
        rev = {v: k for k, v in idmap.items()}
    except Exception:
        rev = {}
    for s in items:
        t, v = s.get("id", (8, ""))
        if t == 2 and v in rev:
            s["id"] = (8, rev[v])
    pts, coins, counts = appraise(items)
    print(f"  {player:16} load {pts:7.0f} pts -> {price_for(pts):2} coins   "
          f"holding {coins:3}   S{counts['S']} A{counts['A']} B{counts['B']} C{counts['C']}")


if __name__ == "__main__":
    if "--quote" in sys.argv:
        for who in ("DuduPhudu", "VerrassVerrass", "CubeThePenguin"):
            quote(who)
    elif len(sys.argv) >= 3:
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
