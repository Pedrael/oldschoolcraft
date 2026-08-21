#!/usr/bin/env python3
"""Power suit life support - the suit answers EnviroMine.

EnviroMine keys its armour entries on item ID alone; it cannot see NBT, so it
has no way to know which modules a power suit carries. Config can therefore say
"power armour insulates" but never "power armour with a cooling system is
climate controlled". This closes that gap from outside: read the modules off
playerdata, and drive the player's stats with /envirostat.

Tiering is by CORRECTION FREQUENCY, because /envirostat can only set a value,
not scale one. A nitrogen suit is corrected every minute and effectively never
drifts; a heat sink is corrected every three, so it wanders and snaps back.
That gives a real upgrade path out of a binary command.

  Heat Sink                       every 180s   rough climate control
  Cooling System                  every  90s   comfortable nearly anywhere
  Liquid Nitrogen Cooling System  every  60s   effectively immune

Water is only maintained if a Water Tank is also installed, so that module gets
a second job too. Air is topped up regardless - a sealed suit is sealed.

The module must be on armour the player is WEARING. A spare suit in a backpack
does not count. Suit power and module slider values are NOT checked - neither
can be read reliably out of playerdata.
"""
import json, os, re, sys, time

ROOT  = "/home/duduserver/minecraft/1.7.10"
FIFO  = "/run/minecraft/console.in"
LOG   = f"{ROOT}/logs/latest.log"
STATE = "/home/duduserver/mctools/lifesupport-state.json"
AUDIT = "/home/duduserver/mctools/lifesupport.log"

# module -> (seconds between corrections, label). Order matters: best first.
TIERS = [
    (b"Liquid Nitrogen Cooling System",  60, "Liquid Nitrogen"),
    (b"Cooling System",                  90, "Cooling System"),
    (b"Heat Sink",                      180, "Heat Sink"),
]
WATER_TANK = b"Water Tank"

BODY_TEMP  = 37.0
WATER_STEP = 20.0
AIR_STEP   = 20.0

# NBT tag for a byte named "Slot": type 1, name length 0x0004, then "Slot".
# Built from ints rather than an escaped literal: escaping this through a shell
# has bitten us before and wrote real NUL bytes into the source file.
SLOT_TAG = bytes([1, 0, 4]) + b"Slot"
SLOT_RE = re.compile(re.escape(SLOT_TAG) + b"(.)", re.S)
ARMOUR_SLOTS = (100, 101, 102, 103)          # feet, legs, chest, head


def console(cmd, wait=1.0):
    if not os.path.exists(FIFO):
        return ""
    try:
        before = sum(1 for _ in open(LOG, "rb"))
    except OSError:
        before = 0
    with open(FIFO, "w") as f:
        f.write(cmd + "\n")
    time.sleep(wait)
    try:
        with open(LOG, "rb") as f:
            return b"".join(f.readlines()[before:]).decode("utf-8", "replace")
    except OSError:
        return ""


def online_players():
    out = console("list", 1.8)
    names = []
    for line in out.splitlines():
        if "Players currently online" in line:
            continue
        m = re.search(r"\[Server thread/INFO\]:\s*([A-Za-z0-9_ ,]+)$", line)
        if m:
            for n in m.group(1).split(","):
                n = n.strip()
                if re.fullmatch(r"[A-Za-z0-9_]{3,16}", n):
                    names.append(n)
    return names


def roster(max_age=150):
    """Who mc-watcher says is online, or None if its roster is stale.

    Reading a file costs nothing; running `list` writes a line to latest.log
    every single time, which is what used to bury the log.
    """
    try:
        d = json.load(open("/home/duduserver/mctools/online.json"))
    except Exception:
        return None
    if time.time() - d.get("when", 0) > max_age:
        return None
    return d.get("players", [])

def uuid_map():
    try:
        return {p["name"]: p["uuid"] for p in json.load(open(f"{ROOT}/usercache.json"))}
    except Exception:
        return {}


def worn_bytes(uuid):
    """Raw NBT of the four armour slots only.

    A full NBT parse desyncs inside MPS item data, so this uses a structural
    fact instead: Minecraft writes an item's Slot tag LAST, after its
    id/Count/Damage/tag. Each item's bytes therefore lie between the previous
    Slot marker and its own.
    """
    p = f"{ROOT}/world/playerdata/{uuid}.dat"
    if not os.path.exists(p):
        return b""
    raw = open(p, "rb").read()
    try:
        import gzip
        d = gzip.decompress(raw)
    except Exception:
        d = raw
    worn, prev_end = b"", 0
    for m in SLOT_RE.finditer(d):
        if m.group(1)[0] in ARMOUR_SLOTS:
            worn += d[prev_end:m.start()]
        prev_end = m.end()
    return worn


def suit_modules(uuid):
    """(tier_seconds, tier_label, has_water_tank) for WORN armour, or None."""
    worn = worn_bytes(uuid)
    if not worn:
        return None
    for token, secs, label in TIERS:
        if token in worn:
            return (secs, label, WATER_TANK in worn)
    return None


def audit(msg):
    with open(AUDIT, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}\n")


def main():
    dry = "--dry-run" in sys.argv
    if not os.path.exists(FIFO):
        return
    players = roster()
    if players is None:              # mc-watcher down: ask directly
        players = online_players()
    if not players:
        return

    ids = uuid_map()
    state = {}
    if os.path.exists(STATE):
        try:
            state = json.load(open(STATE))
        except Exception:
            state = {}

    now = time.time()
    for name in players:
        uuid = ids.get(name)
        info = suit_modules(uuid) if uuid else None
        if not info:
            if dry:
                print(f"  {name:16} no cooling module on worn armour")
            if state.pop(name, None) is not None:
                audit(f"{name}: life support inactive")
            continue

        secs, label, tank = info
        last = state.get(name, {}).get("last", 0)
        due = (now - last) >= secs

        if dry:
            left = "DUE" if due else f"{secs - (now - last):.0f}s to go"
            print(f"  {name:16} {label:16} every {secs:>3}s  water_tank={tank}  {left}")
            continue
        if not due:
            continue

        if state.get(name, {}).get("label") != label:
            audit(f"{name}: life support active via {label}"
                  f"{' + Water Tank' if tank else ''}")
        console(f"envirostat {name} set temp {BODY_TEMP}", 0.3)
        console(f"envirostat {name} add air {AIR_STEP}", 0.3)
        if tank:
            console(f"envirostat {name} add water {WATER_STEP}", 0.3)
        state[name] = {"last": now, "label": label}

    if not dry:
        json.dump(state, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
