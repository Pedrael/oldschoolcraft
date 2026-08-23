#!/usr/bin/env python3
"""mc-watcher - react to things that happen, instead of firing on a clock.

The tip system speaks on a timer. This speaks when something occurs:

  DEATH      work out the grave snapshot id and hand the player the exact
             /ob_inventory command. All three players are op level 4, so they
             can run it themselves - no SSH, no listing world/data by hand.
  JOIN       a greeting built from live server state rather than "welcome back".
  DIMENSION  announce the first time a player reaches one of the twelve, and
             say so louder when nobody has ever been there before.

Runs as a service tailing latest.log. Handles the log being rotated out from
under it (Forge replaces latest.log on every restart) by watching for the file
shrinking or its inode changing.
"""
import glob, json, os, re, time

ROOT   = "/home/duduserver/minecraft/1.7.10"
FIFO   = "/run/minecraft/console.in"
LOG    = f"{ROOT}/logs/latest.log"
STATE  = "/home/duduserver/mctools/watcher-state.json"
AUDIT  = "/home/duduserver/mctools/watcher.log"
ONLINE = "/home/duduserver/mctools/online.json"

PLAYERS = ("DuduPhudu", "VerrassVerrass", "CubeThePenguin")

DIM_NAMES = {
    -1: "the Nether", 1: "the End", 7: "the Twilight Forest",
    -34: "the Runic Dungeons", 2: "the Spectre World", 6: "the Mining World",
    -100: "the Deep Dark", -112: "the Last Millenium", -19: "the Bedrock World",
    -2: "the Cave Dimension", -17: "the Wyvern Lair", 0: "the Overworld",
}

DEATH_VERB = re.compile(
    r"^(\S+) (was |fell |drowned|went up|hit the ground|starved|suffocated|"
    r"tried to swim|died|blew up|walked into|burned|withered|got )")
LINE = re.compile(r"^\[(\d\d:\d\d:\d\d)\] \[Server thread/INFO\]: (.+)$")


def say(payload):
    if os.path.exists(FIFO):
        with open(FIFO, "w") as f:
            f.write("tellraw @a " + payload + "\n")


def whisper(player, payload):
    if os.path.exists(FIFO):
        with open(FIFO, "w") as f:
            f.write(f"tellraw {player} " + payload + "\n")


def msg(parts):
    return json.dumps(parts, ensure_ascii=False)


def audit(t):
    with open(AUDIT, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {t}\n")


def load():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            pass
    return {"visited": {}, "seen_dims": []}


def save(s):
    json.dump(s, open(STATE, "w"), indent=1)


# ----------------------------------------------------------------- roster --
def write_online(names):
    """Publish who is online so the timer scripts need not ask the console."""
    try:
        json.dump({"players": sorted(names), "when": time.time()},
                  open(ONLINE, "w"), indent=1)
    except OSError:
        pass


def rebuild_online():
    """Replay the current latest.log to work out who is on right now.

    Needed because this service seeks to the END of the log on start, so a
    restart would otherwise forget everyone already connected.
    """
    on = set()
    try:
        with open(LOG, "r", encoding="utf-8", errors="replace") as f:
            for ln in f:
                m = LINE.match(ln.rstrip("\n"))
                if not m:
                    continue
                b = m.group(2).strip()
                j = re.match(r"^(\S+) joined the game$", b)
                l = re.match(r"^(\S+) left the game$", b)
                if j and j.group(1) in PLAYERS:
                    on.add(j.group(1))
                elif l and l.group(1) in PLAYERS:
                    on.discard(l.group(1))
    except OSError:
        pass
    return on


# ------------------------------------------------------------------ facts --
def facts():
    f = {}
    try:
        db = json.load(open(f"{ROOT}/world/betterquesting/QuestDatabase.json"))
        f["quests"] = len(db["questDatabase:9"])
        f["lines"] = len(db["questLines:9"])
    except Exception:
        pass
    try:
        import gzip, struct
        d = gzip.decompress(open(f"{ROOT}/world/level.dat", "rb").read())
        j = d.find(b"\x04\x00\x07DayTime")
        if j >= 0:
            f["day"] = struct.unpack(">q", d[j + 10:j + 18])[0] // 24000
    except Exception:
        pass
    f["deaths"] = len(glob.glob(f"{ROOT}/world/data/inventory-*-death-0.dat"))
    return f


def player_dim(player):
    try:
        cache = {p["name"]: p["uuid"] for p in json.load(open(f"{ROOT}/usercache.json"))}
        uuid = cache.get(player)
        if not uuid:
            return None
        import gzip, struct
        p = f"{ROOT}/world/playerdata/{uuid}.dat"
        raw = open(p, "rb").read()
        try:
            d = gzip.decompress(raw)
        except Exception:
            d = raw
        pat = bytes([3, 0, 9]) + b"Dimension"
        j = d.find(pat)
        if j < 0:
            return None
        return struct.unpack(">i", d[j + len(pat):j + len(pat) + 4])[0]
    except Exception:
        return None


# ----------------------------------------------------------------- events --
def on_death(player, message):
    """Settle the death toll, then hand over a grave snapshot if there is one.

    The toll MUST be launched first and unconditionally. With keepInventory on
    there is no grave and therefore no snapshot file, and this function used to
    return early when it could not find one - which meant the mechanic was
    never called at all.
    """
    audit(f"death: {player}")
    try:
        import subprocess as _sp
        armed = os.path.exists("/home/duduserver/mctools/deathtoll.armed")
        _sp.Popen(["/usr/bin/python3", "/home/duduserver/mctools/mc-deathtoll2.py",
                   player] + ([] if armed else ["--dry-run"]),
                  stdout=open("/home/duduserver/mctools/deathtoll.out", "a"),
                  stderr=_sp.STDOUT)
    except Exception as e:
        audit(f"deathtoll failed to launch: {e}")

    time.sleep(3)                       # let OpenBlocks finish writing the file
    pat = f"{ROOT}/world/data/inventory-{player}-*-grave-0.dat"
    files = sorted(glob.glob(pat), key=os.path.getmtime)
    if not files:
        pat = f"{ROOT}/world/data/inventory-{player}-*-death-0.dat"
        files = sorted(glob.glob(pat), key=os.path.getmtime)
        kind = "death"
    else:
        kind = "grave"
    if not files:
        return
    newest = os.path.basename(files[-1])
    if time.time() - os.path.getmtime(files[-1]) > 120:
        return                          # stale: this death produced no snapshot
    fid = newest[len("inventory-"):-len(".dat")]

    whisper(player, msg(["",
        {"text": "» ", "color": "dark_gray"},
        {"text": "RECOVERY ", "color": "light_purple", "bold": True},
        {"text": "· ", "color": "dark_gray"},
        {"text": "Your inventory was saved. Run this to drop it at your feet:",
         "color": "white"}]))
    whisper(player, msg(["",
        {"text": "  /ob_inventory spawn " + fid, "color": "yellow"}]))
    if kind == "death":
        whisper(player, msg(["",
            {"text": "  ", "color": "dark_gray"},
            {"text": "(no grave was placed - this is the death snapshot, "
                     "which omits Baubles and Traveller's Gear)",
             "color": "gray", "italic": True}]))
    audit(f"death: {player} -> {fid} ({kind})")



def settle_pending(player):
    """Hand back a snapshot to someone who logged off before respawning.

    Their grave was already removed - they could pay - so the snapshot is the
    only copy. Losing it because they closed the game would be unforgivable.
    """
    PEND = "/home/duduserver/mctools/deathtoll-pending.json"
    try:
        d = json.load(open(PEND))
    except Exception:
        return
    owed = d.get(player)
    if not owed:
        return
    import subprocess
    subprocess.Popen(["/usr/bin/python3", "/home/duduserver/mctools/mc-deathtoll.py",
                      player, owed["fid"]],
                     stdout=open("/home/duduserver/mctools/deathtoll.out", "a"),
                     stderr=subprocess.STDOUT)
    audit(f"pending settle launched for {player} -> {owed['fid']}")


def on_join(player, state):
    settle_pending(player)
    f = facts()
    bits = []
    if "day" in f:
        bits.append(f"Day {f['day']}.")
    if "quests" in f:
        bits.append(f"{f['quests']} quests in {f['lines']} chapters.")
    visited = set(state["visited"].get(player, []))
    unseen = [d for d in DIM_NAMES if d not in visited and d != 0]
    tail = ""
    if -17 not in visited:
        tail = "The Wyvern Lair still has no visitors."
    elif unseen:
        tail = f"{len(unseen)} dimensions you have never set foot in."
    whisper(player, msg(["",
        {"text": "» ", "color": "dark_gray"},
        {"text": " ".join(bits), "color": "white"},
        {"text": (" " + tail) if tail else "", "color": "gray", "italic": True}]))
    audit(f"join: {player}")


def check_dims(state):
    changed = False
    for p in PLAYERS:
        d = player_dim(p)
        if d is None:
            continue
        been = state["visited"].setdefault(p, [])
        if d in been:
            continue
        been.append(d)
        changed = True
        name = DIM_NAMES.get(d, f"dimension {d}")
        first_ever = d not in state["seen_dims"]
        if first_ever:
            state["seen_dims"].append(d)
            say(msg(["",
                {"text": "» ", "color": "dark_gray"},
                {"text": "FIRST ", "color": "gold", "bold": True},
                {"text": "· ", "color": "dark_gray"},
                {"text": f"Somebody has reached {name} for the first time. "
                         f"Nobody had ever been there.", "color": "gold"}]))
        else:
            say(msg(["",
                {"text": "» ", "color": "dark_gray"},
                {"text": f"Someone set foot in {name} for the first time.",
                 "color": "gray", "italic": True}]))
        audit(f"dim: {p} -> {d} ({name}){' FIRST EVER' if first_ever else ''}")
    return changed


# ------------------------------------------------------------------- main --
def main():
    state = load()
    # seed seen_dims from folders that already exist, so old ground is not "new"
    if not state["seen_dims"]:
        for p in glob.glob(f"{ROOT}/world/DIM*"):
            try:
                state["seen_dims"].append(int(os.path.basename(p)[3:]))
            except ValueError:
                pass
        state["seen_dims"].append(0)
        save(state)

    online = rebuild_online()
    write_online(online)

    f = None
    inode = None
    pos = 0
    last_dim_check = 0
    last_roster_touch = 0

    while True:
        try:
            if f is None:
                if not os.path.exists(LOG):
                    time.sleep(5); continue
                f = open(LOG, "r", encoding="utf-8", errors="replace")
                st = os.fstat(f.fileno())
                inode = st.st_ino
                f.seek(0, os.SEEK_END)       # only new lines
                pos = f.tell()

            line = f.readline()
            if line:
                pos = f.tell()
                m = LINE.match(line.rstrip("\n"))
                if m:
                    body = m.group(2).strip()
                    jm = re.match(r"^(\S+) joined the game$", body)
                    lm2 = re.match(r"^(\S+) left the game$", body)
                    if jm and jm.group(1) in PLAYERS:
                        online.add(jm.group(1))
                        write_online(online)
                        time.sleep(2)
                        on_join(jm.group(1), state)
                    elif lm2 and lm2.group(1) in PLAYERS:
                        online.discard(lm2.group(1))
                        write_online(online)
                    elif DEATH_VERB.match(body) and body.split(" ", 1)[0] in PLAYERS:
                        on_death(body.split(" ", 1)[0], body)
            else:
                # nothing new: check rotation, then dimensions
                try:
                    st = os.stat(LOG)
                    if st.st_ino != inode or st.st_size < pos:
                        f.close(); f = None
                        online = rebuild_online()
                        write_online(online)
                        continue
                except OSError:
                    f.close(); f = None; continue

                now = time.time()
                # re-stamp the roster so consumers can tell it is still fresh
                if now - last_roster_touch > 30:
                    last_roster_touch = now
                    write_online(online)
                if now - last_dim_check > 20:
                    last_dim_check = now
                    if check_dims(state):
                        save(state)
                time.sleep(1)
        except Exception as e:
            audit(f"ERROR {type(e).__name__}: {e}")
            try:
                if f: f.close()
            except Exception:
                pass
            f = None
            time.sleep(5)


if __name__ == "__main__":
    main()
