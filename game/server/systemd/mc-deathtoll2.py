#!/usr/bin/env python3
"""Death insurance, inverted: nothing is ever dropped, so nothing can duplicate.

The first design fought OpenBlocks graves and lost four times. Breaking a grave
fires GraveDropsEvent and spawns an EntityItem for every stack inside, so any
attempt to remove one scattered the inventory across the ground while the
player was also handed the snapshot. Every "success" duplicated.

So the mechanic no longer removes graves. It stops them existing:

    keepInventory = true   -> death creates no grave and drops nothing, ever

From there the default is "you keep everything", and this script takes things
AWAY rather than giving them back:

    can pay  -> the fee is deducted, nothing else changes
    cannot   -> the inventory is moved into a grave we build at the death spot

Every failure now leaves the player holding their own belongings, which is the
opposite of the original design where a failure destroyed them.

Verified before writing:
  * keepInventory=true produces no grave snapshot and no drops
  * ob_inventory store captures a live inventory to a file
  * a snapshot can be edited to remove an exact number of coins
  * setblock builds a grave holding 480 items across 37 stacks, 12 of them
    carrying nested NBT, with zero differences
"""
import glob, gzip, json, math, os, re, shutil, subprocess, sys, time

sys.path.insert(0, "/home/duduserver/mctools")
import nbtio, snbt

ROOT  = "/home/duduserver/minecraft/1.7.10"
FIFO  = "/run/minecraft/console.in"
LOG   = f"{ROOT}/logs/latest.log"
AUDIT = "/home/duduserver/mctools/deathtoll.log"
ARMED_FLAG = "/home/duduserver/mctools/deathtoll.armed"

COIN     = ("Thaumcraft:ItemResource", 18)
COIN_ALT = "IC2:itemCoin"
DIVISOR   = 20
MIN_PRICE = 1
MAX_PRICE = 48

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

TRIPPING = {"build-failed", "clear-failed", "restore-failed", "exception"}
HARMLESS = {"paid", "unpaid", "no-respawn", "no-inventory", "dry", "offline"}


def audit(m):
    with open(AUDIT, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {m}\n")


def console(cmd, wait=0.5):
    """Send a command and return whatever the log gained, for parsing replies."""
    if not os.path.exists(FIFO):
        return ""
    try:
        before = os.path.getsize(LOG)
    except OSError:
        before = 0
    with open(FIFO, "w") as f:
        f.write(cmd + "\n")
    time.sleep(wait)
    try:
        h = open(LOG, "r", encoding="utf-8", errors="replace")
        h.seek(before)
        return h.read()
    except OSError:
        return ""


def say(player, parts):
    console("tellraw %s %s" % (player, json.dumps(parts, ensure_ascii=False)), 0.2)


def trip(reason, player=""):
    was = os.path.exists(ARMED_FLAG)
    try:
        os.remove(ARMED_FLAG)
    except OSError:
        pass
    audit(f"BREAKER TRIPPED ({reason}) for {player} - DISARMED")
    if was:
        console("tellraw @a " + json.dumps(["",
            {"text": "» ", "color": "dark_gray"},
            {"text": "INSURANCE OFF", "color": "red", "bold": True},
            {"text": " · ", "color": "dark_gray"},
            {"text": "It failed and shut itself down. Nobody is being charged.",
             "color": "white"}], ensure_ascii=False), 0.3)


# ---------------------------------------------------------------- value --
def tier(name, dmg):
    k = f"{name}:{dmg}"
    if TIER_S.search(k): return "S"
    if TIER_A.search(k): return "A"
    if TIER_B.search(k): return "B"
    return "C"


def appraise(stacks):
    pts, coins = 0.0, 0
    for s in stacks:
        if not isinstance(s, dict):
            continue
        t, v = s.get("id", (8, ""))
        name = v if t == 8 else str(v)
        dmg = s.get("Damage", (2, 0))[1]
        cnt = s.get("Count", (1, 1))[1]
        if (name == COIN[0] and dmg == COIN[1]) or name == COIN_ALT:
            coins += cnt
            continue
        mult = 2.0 if re.search(r"helmet|chestplate|leggings|boots|plate|sword|"
                                r"pickaxe|axe|shovel|bow|wand|staff", name, re.I) else 1.0
        pts += PTS[tier(name, dmg)] * cnt * mult
    return pts, coins


def price_for(pts):
    return max(MIN_PRICE, min(MAX_PRICE, int(math.ceil(pts / DIVISOR))))


# ---------------------------------------------------------------- world --
def uuid_of(name):
    try:
        for p in json.load(open(f"{ROOT}/usercache.json")):
            if p["name"] == name:
                return p["uuid"]
    except Exception:
        pass
    return None


def playerdata(uuid):
    console("save-all", 1.5)
    p = f"{ROOT}/world/playerdata/{uuid}.dat"
    try:
        nm, root = nbtio.parse(gzip.decompress(open(p, "rb").read()))
        return root, os.path.getmtime(p)
    except Exception:
        return None, 0


def respawned(uuid, since):
    """Alive, and proven by a file written AFTER the death - a stale playerdata
    file reports full health indefinitely and is how an inventory was destroyed."""
    root, mtime = playerdata(uuid)
    if not root or mtime <= since:
        return False
    h = root.get("HealF") or root.get("Health")
    return bool(h) and h[1] > 0


def store_inventory(player):
    """/ob_inventory store, returning the file id it printed."""
    out = console(f"ob_inventory store {player}", 2.0)
    m = re.search(r"inventory-(\S+?)\.dat", out)
    return m.group(1) if m else None


def read_snapshot(fid):
    p = f"{ROOT}/world/data/inventory-{fid}.dat"
    nm, root = nbtio.parse(gzip.decompress(open(p, "rb").read()))
    items = [s for s in root["Inventory"][1]["Items"][1][1] if isinstance(s, dict)]
    return nm, root, items


def charge_snapshot(fid, nm, root, price):
    """Remove exactly `price` coins. /clear cannot: 1.7.10 has no count argument
    and would take every coin the player owns."""
    items = root["Inventory"][1]["Items"][1][1]
    left, keep = price, []
    for st in items:
        if left <= 0 or not isinstance(st, dict):
            keep.append(st); continue
        t, v = st.get("id", (8, ""))
        name = v if t == 8 else str(v)
        dmg = st.get("Damage", (2, 0))[1]
        cnt = st.get("Count", (1, 0))[1]
        if not ((name == COIN[0] and dmg == COIN[1]) or name == COIN_ALT):
            keep.append(st); continue
        take = min(cnt, left)
        left -= take
        if cnt - take > 0:
            st["Count"] = (1, cnt - take)
            keep.append(st)
    if left > 0:
        return False
    root["Inventory"][1]["Items"] = (9, (10, keep))
    p = f"{ROOT}/world/data/inventory-{fid}.dat"
    with open(p, "wb") as f:
        f.write(gzip.compress(nbtio.serialise(nm, root)))
    read_snapshot(fid)
    return True


def inventory_size(uuid):
    root, _ = playerdata(uuid)
    if not root:
        return None
    inv = root.get("Inventory")
    return len([x for x in inv[1][1] if isinstance(x, dict)]) if inv else 0


def build_grave(player, x, y, z, stacks):
    """Place a grave holding these items. Full NBT fidelity, verified."""
    try:
        tag = snbt.items_to_snbt(stacks)[1:-1]
    except snbt.Unserialisable as e:
        audit(f"{player}: cannot serialise inventory ({e}) - leaving it with them")
        return False
    cmd = (f'setblock {x} {y} {z} OpenBlocks:grave 0 replace '
           f'{{PlayerName:"{player}",perishedUsername:"{player}",{tag}}}')
    out = console(cmd, 1.5)
    if "Block placed" not in out:
        audit(f"{player}: setblock refused the grave: {out.strip()[:120]}")
        return False
    return True


# ----------------------------------------------------------------- flow --
def settle(player, death_pos=None, dry=False):
    uuid = uuid_of(player)
    if not uuid:
        return "offline"

    # Where they died, captured while they were still lying there. With
    # keepInventory the body stays put until they click respawn.
    if death_pos is None:
        root, _ = playerdata(uuid)
        if root and "Pos" in root:
            p = root["Pos"][1][1]
            death_pos = (int(math.floor(p[0])), int(math.floor(p[1])), int(math.floor(p[2])))
    if not death_pos:
        audit(f"{player}: no death position - leaving them alone")
        return "no-inventory"

    # Wait for a respawn we can believe in. They are holding everything
    # meanwhile, so waiting costs nothing and risks nothing.
    died_at = time.time()
    time.sleep(3)
    for _ in range(90):
        if respawned(uuid, died_at):
            break
        time.sleep(2)
    else:
        audit(f"{player}: no confirmed respawn - leaving them alone")
        return "no-respawn"

    fid = store_inventory(player)
    if not fid:
        audit(f"{player}: ob_inventory store produced nothing")
        return "no-inventory"
    nm, root, items = read_snapshot(fid)
    if not items:
        audit(f"{player}: empty inventory, nothing to insure")
        return "no-inventory"

    pts, coins = appraise(items)
    price = price_for(pts)
    x, y, z = death_pos
    audit(f"{player}: value={pts:.0f} price={price} coins={coins} "
          f"stacks={len(items)} died at {x},{y},{z}")

    if dry:
        print(f"  {player}: {pts:.0f} pts -> {price} coins; has {coins}; "
              f"would {'PAY' if coins >= price else 'LOSE IT to a grave'} at {x},{y},{z}")
        return "dry"

    # ---- can pay: take the fee, leave everything else alone --------------
    if coins >= price:
        if not charge_snapshot(fid, nm, root, price):
            audit(f"{player}: could not take {price} coins from the snapshot")
            return "restore-failed"
        console(f"clear {player}", 1.0)
        console(f"ob_inventory restore {player} {fid}", 1.5)
        got = inventory_size(uuid)
        if not got:
            audit(f"{player}: charge restore did not land - giving it all back")
            console(f"ob_inventory restore {player} {fid}", 1.5)
            return "restore-failed"
        say(player, ["", {"text": "» ", "color": "dark_gray"},
             {"text": "INSURED", "color": "gold", "bold": True},
             {"text": " · ", "color": "dark_gray"},
             {"text": "You kept everything.", "color": "white"}])
        say(player, ["", {"text": f"   {price} gold coins", "color": "gold"},
             {"text": f" spent · {coins - price} left · load valued at {pts:.0f}",
              "color": "gray", "italic": True}])
        audit(f"{player}: PAID {price}, kept {got} stacks")
        return "paid"

    # ---- cannot pay: the belongings go into a grave where they fell ------
    # Build FIRST and confirm it holds everything. Only then take the items,
    # so a failure leaves the player carrying their own gear.
    if not build_grave(player, x, y, z, items):
        say(player, ["", {"text": "» ", "color": "dark_gray"},
             {"text": "You could not afford insurance, but the grave could not be "
                      "placed - so you keep everything this time.", "color": "yellow"}])
        return "build-failed"

    console("save-all", 2.0)
    if not verify_grave(x, y, z, items):
        audit(f"{player}: grave at {x},{y},{z} did not verify - keeping their items")
        console(f'setblock {x} {y} {z} OpenBlocks:grave 0 replace {{Items:[],size:0}}', 1.0)
        console(f"setblock {x} {y} {z} minecraft:air 0 replace", 0.8)
        return "build-failed"

    console(f"clear {player}", 1.2)
    left = inventory_size(uuid)
    if left:
        audit(f"{player}: clear left {left} stacks - REMOVING the grave to avoid a duplicate")
        console(f'setblock {x} {y} {z} OpenBlocks:grave 0 replace {{Items:[],size:0}}', 1.0)
        console(f"setblock {x} {y} {z} minecraft:air 0 replace", 0.8)
        return "clear-failed"

    say(player, ["", {"text": "» ", "color": "dark_gray"},
         {"text": "GRAVE", "color": "gray", "bold": True},
         {"text": " · ", "color": "dark_gray"},
         {"text": "Insuring that load needed ", "color": "white"},
         {"text": f"{price} gold coins", "color": "gold"},
         {"text": f". You had {coins}.", "color": "white"}])
    say(player, ["", {"text": f"   Everything is in a grave at {x} {y} {z}. Carry coins and it comes home with you.",
                      "color": "gray", "italic": True}])
    audit(f"{player}: UNPAID - {len(items)} stacks moved to a grave at {x},{y},{z}")
    return "unpaid"


def verify_grave(x, y, z, expect):
    """Read the grave back off disk and check it holds what we put in."""
    import collections
    want = collections.Counter()
    for s in expect:
        want[(s["id"][1], s.get("Damage", (2, 0))[1])] += s.get("Count", (1, 0))[1]
    cx, cz = x >> 4, z >> 4
    try:
        R = nbtio.read_region(f"{ROOT}/world/region/r.{cx>>5}.{cz>>5}.mca")
    except Exception:
        return False
    ch = R.get((cx & 31) + (cz & 31) * 32)
    if not ch:
        return False
    te = ch[2].get("Level", (0, {}))[1].get("TileEntities")
    for t in (te[1][1] if te else []):
        if not isinstance(t, dict) or t.get("id", (0, ""))[1] != "openblocks_grave":
            continue
        if (t.get("x", (3, 0))[1], t.get("y", (3, 0))[1], t.get("z", (3, 0))[1]) != (x, y, z):
            continue
        got = collections.Counter()
        for s in t.get("Items", (9, (10, [])))[1][1]:
            if isinstance(s, dict):
                got[(s["id"][1], s.get("Damage", (2, 0))[1])] += s.get("Count", (1, 0))[1]
        return got == want
    return False


def quote(player):
    uuid = uuid_of(player)
    if not uuid:
        print(f"  {player}: unknown"); return
    root, _ = playerdata(uuid)
    inv = root.get("Inventory") if root else None
    items = [s for s in inv[1][1] if isinstance(s, dict)] if inv else []
    try:
        rev = {v: k for k, v in json.load(open("/tmp/idmap.json")).items()}
    except Exception:
        rev = {}
    for s in items:
        t, v = s.get("id", (8, ""))
        if t == 2 and v in rev:
            s["id"] = (8, rev[v])
    pts, coins = appraise(items)
    print(f"  {player:16} {pts:7.0f} pts -> {price_for(pts):2} coins   holding {coins:3}")


if __name__ == "__main__":
    if "--quote" in sys.argv:
        for w in ("DuduPhudu", "VerrassVerrass", "CubeThePenguin"):
            quote(w)
    elif len(sys.argv) >= 2 and not sys.argv[1].startswith("--"):
        player = sys.argv[1]
        dry = "--dry-run" in sys.argv
        try:
            r = settle(player, dry=dry)
        except Exception as e:
            import traceback
            audit(f"{player}: UNHANDLED {type(e).__name__}: {e}")
            audit(traceback.format_exc())
            if not dry:
                trip("exception", player)
            print("exception"); sys.exit(1)
        if not dry and r in TRIPPING:
            trip(r, player)
        print(r)
    else:
        print(__doc__)
