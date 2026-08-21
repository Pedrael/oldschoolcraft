#!/usr/bin/env python3
"""Stop mc-lifesupport and mc-afk-guard hammering the console with `list`.

Between them they ran `list` three times a minute, awake or not, which put
~5700 "Players currently online: [ 0 ]" lines a day into latest.log. That noise
is what made the 2026-08-21 hang so hard to read.

mc-watcher already tails the log and sees every join and leave, so it can keep
an authoritative roster in online.json. The two timer scripts then read the
file, and only fall back to `list` if the roster is stale (i.e. mc-watcher is
down). When nobody is online they now do nothing at all - no console traffic.
"""
import re, shutil, sys, time

TOOLS = "/home/duduserver/mctools"

# ---------------------------------------------------------------- watcher --
WATCHER = f"{TOOLS}/mc-watcher.py"
w = open(WATCHER, encoding="utf-8").read()

if "ONLINE" in w:
    print("mc-watcher: already patched")
else:
    w = w.replace(
        'AUDIT  = "/home/duduserver/mctools/watcher.log"',
        'AUDIT  = "/home/duduserver/mctools/watcher.log"\n'
        'ONLINE = "/home/duduserver/mctools/online.json"')

    # roster helpers, inserted just before the facts section
    w = w.replace(
        "# ------------------------------------------------------------------ facts --",
        '''# ----------------------------------------------------------------- roster --
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
                m = LINE.match(ln.rstrip("\\n"))
                if not m:
                    continue
                b = m.group(2).strip()
                j = re.match(r"^(\\S+) joined the game$", b)
                l = re.match(r"^(\\S+) left the game$", b)
                if j and j.group(1) in PLAYERS:
                    on.add(j.group(1))
                elif l and l.group(1) in PLAYERS:
                    on.discard(l.group(1))
    except OSError:
        pass
    return on


# ------------------------------------------------------------------ facts --''')

    # maintain the roster as events arrive
    w = w.replace(
        """                    if jm and jm.group(1) in PLAYERS:
                        time.sleep(2)
                        on_join(jm.group(1), state)""",
        """                    lm2 = re.match(r"^(\\S+) left the game$", body)
                    if jm and jm.group(1) in PLAYERS:
                        online.add(jm.group(1))
                        write_online(online)
                        time.sleep(2)
                        on_join(jm.group(1), state)
                    elif lm2 and lm2.group(1) in PLAYERS:
                        online.discard(lm2.group(1))
                        write_online(online)""")

    # seed the roster at startup and refresh the timestamp periodically
    w = w.replace(
        """    f = None
    inode = None
    pos = 0
    last_dim_check = 0""",
        """    online = rebuild_online()
    write_online(online)

    f = None
    inode = None
    pos = 0
    last_dim_check = 0
    last_roster_touch = 0""")

    w = w.replace(
        """                now = time.time()
                if now - last_dim_check > 20:""",
        """                now = time.time()
                # re-stamp the roster so consumers can tell it is still fresh
                if now - last_roster_touch > 30:
                    last_roster_touch = now
                    write_online(online)
                if now - last_dim_check > 20:""")

    # a rotated log means a server restart: nobody is online across it
    w = w.replace(
        """                    if st.st_ino != inode or st.st_size < pos:
                        f.close(); f = None; continue""",
        """                    if st.st_ino != inode or st.st_size < pos:
                        f.close(); f = None
                        online = rebuild_online()
                        write_online(online)
                        continue""")

    shutil.copy2(WATCHER, WATCHER + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
    open(WATCHER, "w", encoding="utf-8").write(w)
    print("mc-watcher: now publishes online.json")

# -------------------------------------------------------------- consumers --
SNIPPET = '''

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
'''

for name, callsite in [("mc-lifesupport.py", "    players = online_players()"),
                       ("mc-afk-guard.py",   "    players = online_players()")]:
    path = f"{TOOLS}/{name}"
    s = open(path, encoding="utf-8").read()
    if "def roster(" in s:
        print(f"{name}: already patched"); continue
    if s.count(callsite) != 1:
        print(f"{name}: ABORT - call site matched {s.count(callsite)}x"); sys.exit(1)

    # add the helper after the online_players definition block
    anchor = "def online_players():"
    idx = s.index(anchor)
    end = s.index("\ndef ", idx + 1)
    s = s[:end] + "\n" + SNIPPET.strip("\n") + "\n" + s[end:]

    s = s.replace(callsite,
                  "    players = roster()\n"
                  "    if players is None:              # mc-watcher down: ask directly\n"
                  "        players = online_players()")

    shutil.copy2(path, path + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
    open(path, "w", encoding="utf-8").write(s)
    print(f"{name}: now reads the roster, falls back to `list` only if stale")

print("\ndone")
