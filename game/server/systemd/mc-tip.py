#!/usr/bin/env python3
"""mc-tip - say something into chat that the server never told anyone.

Replaces the original bash version. Three reasons for the rewrite:

  * /say stamps an ugly "[Server]" prefix on everything. /tellraw does not, and
    takes real JSON, so lines can be coloured and structured.
  * tips now have CATEGORIES, each with its own look, so a warning does not
    read like a piece of flavour text.
  * tips can carry live values - quest counts, dimension counts, the in-game
    day - resolved at send time instead of going stale in a text file.

Guards, unchanged in spirit from the bash original: the server must be up, at
least one player must be online, and the hour must be inside the window people
actually play. Measured from the grave snapshots, that is 18:00-03:00, with
69% of all activity between 22:00 and 01:00.

Selection is weighted by time of night and never repeats until the pool for
that category is exhausted.
"""
import json, os, random, re, subprocess, sys, time

ROOT  = "/home/duduserver/minecraft/1.7.10"
FIFO  = "/run/minecraft/console.in"
LOG   = f"{ROOT}/logs/latest.log"
TIPS  = "/home/duduserver/mctools/tips.json"
STATE = "/home/duduserver/mctools/tip-state.json"

# category -> (glyph+colour, label, label colour, body colour)
STYLE = {
    "tip":   ("§b", "TIP",     "§b", "§f"),
    "hint":  ("§e", "HINT",    "§e", "§f"),
    "warn":  ("§c", "CAREFUL", "§c", "§f"),
    "lore":  ("§5", "",        "§5", "§7"),
    "stat":  ("§a", "SERVER",  "§a", "§f"),
}

# how much each category is worth at a given hour - late night leans to flavour
WEIGHTS = {
    19: {"tip": 5, "hint": 4, "warn": 2, "stat": 2, "lore": 1},
    20: {"tip": 5, "hint": 4, "warn": 2, "stat": 2, "lore": 2},
    21: {"tip": 5, "hint": 4, "warn": 3, "stat": 2, "lore": 2},
    22: {"tip": 4, "hint": 4, "warn": 3, "stat": 2, "lore": 3},
    23: {"tip": 3, "hint": 3, "warn": 3, "stat": 2, "lore": 5},
    0:  {"tip": 2, "hint": 2, "warn": 2, "stat": 2, "lore": 6},
    1:  {"tip": 2, "hint": 2, "warn": 2, "stat": 1, "lore": 6},
}


def console(cmd, wait=1.2):
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


def online_count():
    out = console("list", 1.8)
    m = re.search(r"Players currently online:\s*\[\s*(\d+)", out)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------- live data --
def facts():
    f = {}
    try:
        db = json.load(open(f"{ROOT}/world/betterquesting/QuestDatabase.json"))
        f["quests"] = len(db["questDatabase:9"])
        f["lines"] = len(db["questLines:9"])
    except Exception:
        f["quests"] = f["lines"] = "?"
    try:
        import glob
        f["deaths"] = len(glob.glob(f"{ROOT}/world/data/inventory-*-death-0.dat"))
        f["dims"] = len(glob.glob(f"{ROOT}/world/DIM*"))
        f["mods"] = len(glob.glob(f"{ROOT}/mods/*.jar"))
        cp = f"{ROOT}/config/enviromine/profiles/default/CustomProperties"
        armour = 0
        for p in glob.glob(f"{cp}/*.cfg"):
            s = re.search(r"^armor \{$(.*?)^\}$", open(p).read(), re.S | re.M)
            if s:
                armour += len(re.findall(r"S:01\.ID=", s.group(1)))
        f["armour"] = armour
    except Exception:
        pass
    # in-game day, straight out of level.dat
    try:
        import gzip, struct
        d = gzip.decompress(open(f"{ROOT}/world/level.dat", "rb").read())
        j = d.find(b"\x04\x00\x07DayTime")
        if j >= 0:
            f["day"] = struct.unpack(">q", d[j + 10:j + 18])[0] // 24000
    except Exception:
        pass
    return f


def render(tip, fact):
    glyph, label, lcol, body = STYLE.get(tip["cat"], STYLE["tip"])
    text = tip["text"]
    for k, v in fact.items():
        text = text.replace("{" + k + "}", str(v))
    if "{" in text and "}" in text:       # an unresolved token: skip this tip
        return None
    parts = ["", {"text": "» ", "color": "dark_gray"}]
    if label:
        parts.append({"text": label + " ", "color": COLOR[lcol], "bold": True})
        parts.append({"text": "· ", "color": "dark_gray"})
    parts.append({"text": text, "color": COLOR[body],
                  "italic": tip["cat"] == "lore"})
    return json.dumps(parts, ensure_ascii=False)


COLOR = {"§b": "aqua", "§e": "yellow", "§c": "red",
         "§5": "dark_purple", "§a": "green", "§f": "white",
         "§7": "gray"}


def main():
    dry = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    hour = time.localtime().tm_hour
    if not force and not (hour >= 19 or hour <= 1):
        if dry: print(f"outside 19:00-01:00 (hour {hour})")
        return
    if not os.path.exists(FIFO):
        if dry: print("server not running")
        return
    n = online_count()
    if not force and n == 0:
        if dry: print("nobody online - staying quiet")
        return

    tips = json.load(open(TIPS))
    state = {}
    if os.path.exists(STATE):
        try: state = json.load(open(STATE))
        except Exception: state = {}
    used = set(state.get("used", []))

    w = WEIGHTS.get(hour, {"tip": 4, "hint": 3, "warn": 2, "stat": 2, "lore": 3})
    pool = [t for i, t in enumerate(tips) if i not in used]
    if not pool:                       # cycle exhausted, start again
        used, pool = set(), tips[:]
    weighted = []
    for t in pool:
        weighted += [t] * w.get(t["cat"], 1)
    if not weighted:
        weighted = pool

    fact = facts()
    random.shuffle(weighted)
    for tip in weighted:
        payload = render(tip, fact)
        if payload:
            break
    else:
        return

    if dry:
        # a dry run must NOT consume the tip, or previewing burns the cycle
        print(f"[{n} online, hour {hour}] {tip['cat']:5} | {tip['text'][:110]}")
        return

    used.add(tips.index(tip))
    json.dump({"used": sorted(used)}, open(STATE, "w"))
    console("tellraw @a " + payload, 0.4)


if __name__ == "__main__":
    main()
