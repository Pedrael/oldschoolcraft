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
import glob, gzip, json, os, re, subprocess, sys, time

sys.path.insert(0, "/home/duduserver/mctools")
import nbtio

ROOT   = "/home/duduserver/minecraft/1.7.10"
FIFO   = "/run/minecraft/console.in"
LOG    = f"{ROOT}/logs/latest.log"
STATE  = "/home/duduserver/mctools/deathtoll-state.json"
AUDIT  = "/home/duduserver/mctools/deathtoll.log"

COIN      = ("Thaumcraft:ItemResource", 18)   # Gold Coin, verified in game
COIN_ALT  = ("IC2:itemCoin", 0)               # Industrial Credit, also accepted
DIVISOR   = 30      # value points per coin
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


def recent_graves(player, within_s=600):
    """Graves for this player in regions touched recently. A full sweep of 167
    region files takes minutes; only freshly written ones can hold a new grave."""
    out = []
    now = time.time()
    for f in glob.glob(f"{ROOT}/world/region/*.mca"):
        try:
            if now - os.path.getmtime(f) > within_s:
                continue
            R = nbtio.read_region(f)
        except Exception:
            continue
        for i, (ts, nm, c) in R.items():
            te = c.get("Level", (0, {}))[1].get("TileEntities")
            if not te:
                continue
            for t in te[1][1]:
                if not isinstance(t, dict):
                    continue
                if t.get("id", (0, ""))[1] != "openblocks_grave":
                    continue
                if t.get("perishedUsername", (8, ""))[1] != player:
                    continue
                out.append({
                    "x": t.get("x", (3, 0))[1],
                    "y": t.get("y", (3, 0))[1],
                    "z": t.get("z", (3, 0))[1],
                    "items": [s for s in (t.get("Items", (9, (10, [])))[1][1])
                              if isinstance(s, dict)],
                })
    return out


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


def player_alive(uuid):
    p = f"{ROOT}/world/playerdata/{uuid}.dat"
    try:
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


# ---------------------------------------------------------------- flow --
def settle(player, snapshot_id, dry=False):
    uuid = uuid_of(player)
    graves = recent_graves(player)
    if not graves:
        audit(f"{player}: no recent grave found - leaving alone")
        return "no-grave"
    g = graves[-1]
    pts, coins, counts = appraise(g["items"])
    price = price_for(pts)
    audit(f"{player}: value={pts:.0f} price={price} coins={coins} "
          f"S{counts['S']} A{counts['A']} B{counts['B']} C{counts['C']} "
          f"grave at {g['x']},{g['y']},{g['z']}")

    if dry:
        print(f"  {player}: cargo {pts:.0f} pts -> price {price} coins; "
              f"had {coins}; would {'PAY' if coins >= price else 'take the grave'}")
        return "dry"

    if coins < price:
        say(player, ["", {"text": "\u00bb ", "color": "dark_gray"},
             {"text": "GRAVE", "color": "gray", "bold": True},
             {"text": " \u00b7 ", "color": "dark_gray"},
             {"text": f"Insuring that load would have cost ", "color": "white"},
             {"text": f"{price} gold coins", "color": "gold"},
             {"text": f". You had {coins}.", "color": "white"}])
        say(player, ["", {"text": "   Your grave is where you fell. Carry coins and it comes home with you.",
                          "color": "gray", "italic": True}])
        return "unpaid"

    # wait for the respawn - restoring into a corpse loses everything
    for _ in range(60):
        if uuid and player_alive(uuid):
            break
        time.sleep(2)
    else:
        audit(f"{player}: never respawned in time - leaving the grave")
        return "timeout"

    # remove the grave FIRST. If this fails we must not restore, or the
    # items exist twice.
    console(f"setblock {g['x']} {g['y']} {g['z']} minecraft:air 0 replace", 0.8)
    if not block_is_gone(g["x"], g["y"], g["z"]):
        audit(f"{player}: grave at {g['x']},{g['y']},{g['z']} would not clear - ABORTED")
        say(player, ["", {"text": "\u00bb ", "color": "dark_gray"},
             {"text": "Could not clear your grave, so nothing was charged. "
                      "It is still where you fell.", "color": "yellow"}])
        return "grave-stuck"

    console(f"ob_inventory restore {player} {snapshot_id}", 1.0)
    console(f"clear {player} {COIN[0]} {COIN[1]} {price}", 0.6)

    say(player, ["", {"text": "\u00bb ", "color": "dark_gray"},
         {"text": "INSURED", "color": "gold", "bold": True},
         {"text": " \u00b7 ", "color": "dark_gray"},
         {"text": "Everything came back with you.", "color": "white"}])
    say(player, ["", {"text": f"   {price} gold coins", "color": "gold"},
         {"text": f" spent \u00b7 {coins - price} left \u00b7 load valued at {pts:.0f}",
          "color": "gray", "italic": True}])
    audit(f"{player}: PAID {price}, restored {snapshot_id}, grave cleared")
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
        print(settle(sys.argv[1], sys.argv[2], dry="--dry-run" in sys.argv))
    else:
        print(__doc__)
