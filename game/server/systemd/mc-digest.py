#!/usr/bin/env python3
"""mc-digest - the week, summarised.

Reads what already exists rather than tracking anything new: grave snapshots
give deaths and their timing, the archived logs give causes and play hours,
QuestProgress gives completions, and the watcher's state gives dimensions.

Posts to chat and writes the same thing to a file, so it can be shared with
whoever was not online when it fired.

Deltas come from a snapshot of the previous run. The first run has nothing to
compare against and says so instead of inventing a number.
"""
import glob, gzip, json, os, re, sys, time, datetime, collections

ROOT  = "/home/duduserver/minecraft/1.7.10"
FIFO  = "/run/minecraft/console.in"
SNAP  = "/home/duduserver/mctools/digest-snapshot.json"
OUT   = "/home/duduserver/mctools/digest-latest.txt"
WATCH = "/home/duduserver/mctools/watcher-state.json"

PLAYERS = ("DuduPhudu", "VerrassVerrass", "CubeThePenguin")
DAYS = 7

DIM_NAMES = {-1: "the Nether", 1: "the End", 7: "the Twilight Forest",
             -34: "the Runic Dungeons", 2: "the Spectre World", 6: "the Mining World",
             -100: "the Deep Dark", -112: "the Last Millenium", -19: "the Bedrock World",
             -2: "the Cave Dimension", -17: "the Wyvern Lair", 0: "the Overworld"}

VERB = re.compile(r"^(\S+) (was |fell |drowned|went up|hit the ground|starved|"
                  r"suffocated|tried to swim|died|blew up|walked into|burned|withered|got )")


def cause(msg):
    m = msg.split(" ", 1)[1]
    for pat, lab in [(r"died of thirst", "thirst"), (r"squashed", "falling blocks"),
                     (r"fell out of the world", "the void"), (r"tried to swim in lava", "lava"),
                     (r"fell from|hit the ground", "falling"), (r"drowned", "drowning"),
                     (r"suffocat", "suffocation"), (r"went up in flames|burned|walked into fire", "fire"),
                     (r"blown up|blew up", "explosions"), (r"withered", "wither"),
                     (r"was (shot|slain|killed|fireballed) by (.+)", None)]:
        mm = re.search(pat, m, re.I)
        if mm:
            if lab:
                return lab
            who = mm.group(2).strip()
            # a player name is a killer, not a cause - do not print "DuduPhudu x5"
            for pl in PLAYERS:
                if who.startswith(pl):
                    return "each other"
            return re.sub(r" using .*$", "", who)
    return "something else"


def scan_logs(since):
    """(deaths, play_seconds) from archived logs newer than `since`."""
    deaths, sessions = [], collections.defaultdict(float)
    online = {}
    files = sorted(glob.glob(f"{ROOT}/logs/*.log.gz")) + [f"{ROOT}/logs/latest.log"]
    for fn in files:
        base = os.path.basename(fn)
        m = re.match(r"(\d{4}-\d{2}-\d{2})", base)
        day = m.group(1) if m else datetime.date.today().isoformat()
        if m and day < since.strftime("%Y-%m-%d"):
            continue
        op = gzip.open if fn.endswith(".gz") else open
        try:
            with op(fn, "rt", encoding="utf-8", errors="replace") as f:
                for ln in f:
                    lm = re.match(r"^\[(\d\d):(\d\d):(\d\d)\] \[Server thread/INFO\]: (.+)$",
                                  ln.rstrip("\n"))
                    if not lm:
                        continue
                    hh, mm_, ss, body = lm.groups()
                    body = body.strip()
                    t = int(hh) * 3600 + int(mm_) * 60 + int(ss)
                    jm = re.match(r"^(\S+) joined the game$", body)
                    lv = re.match(r"^(\S+) left the game$", body)
                    if jm and jm.group(1) in PLAYERS:
                        online[jm.group(1)] = t
                    elif lv and lv.group(1) in PLAYERS:
                        s = online.pop(lv.group(1), None)
                        if s is not None and t >= s:
                            sessions[lv.group(1)] += t - s
                    elif VERB.match(body) and body.split(" ", 1)[0] in PLAYERS:
                        deaths.append((day, body.split(" ", 1)[0], cause(body)))
        except Exception:
            pass
    return deaths, sessions


def quests_done():
    try:
        d = json.load(open(f"{ROOT}/world/betterquesting/QuestProgress.json"))
        prog = d.get("questProgress:9", {})
        n = 0
        for q in prog.values():
            for k, v in q.items():
                if k.startswith("tasks") and isinstance(v, dict):
                    n += len(v)
        return len(prog), n
    except Exception:
        return 0, 0


def main():
    post = "--post" in sys.argv
    since = datetime.date.today() - datetime.timedelta(days=DAYS)
    deaths, sessions = scan_logs(since)
    qlines, qtasks = quests_done()

    snap = {}
    if os.path.exists(SNAP):
        try:
            snap = json.load(open(SNAP))
        except Exception:
            pass

    total_deaths = len(glob.glob(f"{ROOT}/world/data/inventory-*-death-0.dat"))
    visited = {}
    try:
        visited = json.load(open(WATCH)).get("visited", {})
    except Exception:
        pass

    by_player = collections.Counter(d[1] for d in deaths)
    by_cause = collections.Counter(d[2] for d in deaths)

    L = []
    L.append(f"The week to {datetime.date.today().isoformat()}")
    L.append("")
    hrs = sum(sessions.values()) / 3600
    if hrs:
        L.append(f"Played: {hrs:.1f} hours across "
                 f"{sum(1 for v in sessions.values() if v)} of you.")
    L.append(f"Deaths: {len(deaths)} this week, {total_deaths} since the world began.")
    if by_cause:
        top = ", ".join(f"{c} x{n}" for c, n in by_cause.most_common(3))
        L.append(f"Mostly: {top}.")
    if by_player:
        L.append("By hand: " + ", ".join(f"{p} {n}" for p, n in by_player.most_common()))
    # A dimension folder only exists once somebody has generated it, which is a
    # far better record of "has anyone ever been" than the watcher's per-player
    # state - that only starts counting from the day the watcher was installed.
    seen = set()
    for pth in glob.glob(f"{ROOT}/world/DIM*"):
        try:
            seen.add(int(os.path.basename(pth)[3:]))
        except ValueError:
            pass
    seen.add(0)
    missing = [DIM_NAMES[d] for d in DIM_NAMES if d not in seen and d != 0]
    if missing:
        L.append(f"Never visited: {', '.join(missing[:4])}"
                 + (f" and {len(missing)-4} more" if len(missing) > 4 else "") + ".")
    if snap.get("qtasks") is not None:
        delta = qtasks - snap["qtasks"]
        L.append(f"Quest tasks completed this week: {delta if delta >= 0 else 0}.")
    else:
        L.append("Quest progress recorded - next week will show the change.")

    text = "\n".join(L)
    open(OUT, "w").write(text + "\n")
    json.dump({"qtasks": qtasks, "qlines": qlines, "deaths": total_deaths,
               "when": time.time()}, open(SNAP, "w"))

    if not post:
        print(text)
        return
    if not os.path.exists(FIFO):
        return
    with open(FIFO, "w") as f:
        f.write("tellraw @a " + json.dumps(["",
            {"text": "» ", "color": "dark_gray"},
            {"text": "THE WEEK", "color": "gold", "bold": True}], ensure_ascii=False) + "\n")
        for line in L[2:]:
            if not line:
                continue
            f.write("tellraw @a " + json.dumps(["",
                {"text": "   " + line, "color": "gray"}], ensure_ascii=False) + "\n")
            time.sleep(0.2)


if __name__ == "__main__":
    main()
