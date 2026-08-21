#!/usr/bin/env python3
"""AFK guard - stop EnviroMine killing people who stepped away from the keyboard.

House rule, from THE-BOOK.md: "Presence pays. Absence never costs." Right now
that is not quite true. Vanilla hunger only charges you for DOING things - we
measured exhaustion sitting at exactly 0.115 for 44 seconds of genuine idling -
but EnviroMine's thirst and temperature run on a wall clock and do not care
whether anyone is at the keyboard. Step away for twenty minutes and you can come
back dead of dehydration.

So: after AFK_MINUTES with no movement AND no change in look direction, this
tops the player's water back up and pulls body temperature to normal, once a
minute, until they move again.

Detection uses Pos + Rotation out of playerdata, so turning on the spot counts
as being present. Dimension changes count too.

Notes on the two adjustments:
  * temperature is SET to 37.0 - that is normal body temp, and EnviroMine's own
    configs use 37.0 as the neutral cap, so it is a known-good value.
  * water is ADDed in small steps rather than set to a guessed maximum. If the
    scale differs from what we assume, adding a little repeatedly still clamps
    safely at full; setting a wrong number might not.
"""
import json, os, re, struct, subprocess, sys, time

ROOT   = "/home/duduserver/minecraft/1.7.10"
FIFO   = "/run/minecraft/console.in"
LOG    = f"{ROOT}/logs/latest.log"
STATE  = "/home/duduserver/mctools/afk-state.json"
AUDIT  = "/home/duduserver/mctools/afk.log"

AFK_MINUTES = 3
WATER_STEP  = 15.0     # added per minute while AFK
BODY_TEMP   = 37.0     # EnviroMine's neutral body temperature


def console(cmd, wait=1.5):
    """Send a console command, return whatever the log emitted after it."""
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
    out = console("list", 2.0)
    names = []
    for line in out.splitlines():
        if "Players currently online" in line:
            continue
        m = re.search(r"\[Server thread/INFO\]:\s*([A-Za-z0-9_ ,]+)$", line)
        if m and "Players currently" not in line:
            for n in m.group(1).split(","):
                n = n.strip()
                if n and re.fullmatch(r"[A-Za-z0-9_]{3,16}", n):
                    names.append(n)
    return names


def uuid_map():
    try:
        return {p["name"]: p["uuid"] for p in json.load(open(f"{ROOT}/usercache.json"))}
    except Exception:
        return {}


def player_pose(uuid):
    """(dim, x, y, z, yaw, pitch) from the saved playerdata, or None."""
    p = f"{ROOT}/world/playerdata/{uuid}.dat"
    if not os.path.exists(p):
        return None
    raw = open(p, "rb").read()
    try:
        import gzip
        d = gzip.decompress(raw)
    except Exception:
        d = raw

    def dlist(name, tag, n, fmt, size):
        pat = bytes([9]) + struct.pack(">H", len(name)) + name.encode() + bytes([tag]) + struct.pack(">i", n)
        j = d.find(pat)
        if j < 0:
            return None
        o = j + len(pat)
        return [struct.unpack(">" + fmt, d[o + i * size:o + (i + 1) * size])[0] for i in range(n)]

    pos = dlist("Pos", 6, 3, "d", 8)
    rot = dlist("Rotation", 5, 2, "f", 4)
    dim = None
    pat = bytes([3]) + struct.pack(">H", 9) + b"Dimension"
    j = d.find(pat)
    if j >= 0:
        dim = struct.unpack(">i", d[j + len(pat):j + len(pat) + 4])[0]
    if not pos or not rot:
        return None
    # round so tiny float drift while standing still is not read as movement
    return (dim, round(pos[0], 2), round(pos[1], 2), round(pos[2], 2),
            round(rot[0], 1), round(rot[1], 1))


def audit(msg):
    with open(AUDIT, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}\n")


def main():
    dry = "--dry-run" in sys.argv
    if not os.path.exists(FIFO):
        return                                    # server down; nothing to do

    players = online_players()
    if not players:
        return

    # Deliberately NO save-all here. Minecraft autosaves player data on its own,
    # and forcing a full save every 60s on a 389MB world is a lag spike bought
    # for nothing: playerdata may be up to ~45s stale, which is irrelevant
    # against a 3-minute AFK threshold.
    ids = uuid_map()
    state = {}
    if os.path.exists(STATE):
        try:
            state = json.load(open(STATE))
        except Exception:
            state = {}

    now = time.time()
    new_state = {}
    for name in players:
        uuid = ids.get(name)
        pose = player_pose(uuid) if uuid else None
        if pose is None:
            continue
        prev = state.get(name)
        if prev and prev.get("pose") == list(pose):
            since = prev.get("since", now)
        else:
            since = now                            # moved or looked around
        idle_min = (now - since) / 60.0
        afk = idle_min >= AFK_MINUTES
        new_state[name] = {"pose": list(pose), "since": since, "afk": afk}

        if afk:
            if not (prev or {}).get("afk"):
                audit(f"{name} AFK ({idle_min:.1f} min) - pausing thirst/temperature")
            if not dry:
                console(f"envirostat {name} add water {WATER_STEP}", 0.4)
                console(f"envirostat {name} set temp {BODY_TEMP}", 0.4)
        elif (prev or {}).get("afk"):
            audit(f"{name} back at the keyboard")

        if dry:
            print(f"  {name:16} idle {idle_min:5.1f} min  {'AFK - would protect' if afk else 'active'}")

    json.dump(new_state, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
