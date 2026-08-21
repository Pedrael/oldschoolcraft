#!/usr/bin/env python3
"""Add a daily Thaumcraft shard quest to the Bounty Board.

Requested by CubeThePenguin. Read as "a reliable daily way to OBTAIN shards",
which is the scarce thing — primal shards come from node-adjacent ore and there
is no farm for them. So the quest pays shards for a cheap, always-available
input rather than asking for shards nobody has.

Slots into the existing Bounty Board line beside the other Quartermaster jobs,
using their exact shape: retrieval with consume, repeatTime 1728000 ticks
(24h at 20tps).

Thaumcraft:ItemShard damage = 0 Air, 1 Fire, 2 Water, 3 Earth, 4 Order,
5 Entropy, 6 Balanced.

Run with the server STOPPED.
"""
import json, os, shutil, sys, time

DB = "/home/duduserver/minecraft/1.7.10/world/betterquesting/QuestDatabase.json"
QID = 220
DAILY = 1728000


def it(i, c=1, d=0):
    return {"id:8": i, "Count:3": c, "Damage:2": d, "OreDict:8": ""}


DESC = """§7Daily. Hand in the stone, take the crystals.§r

Primal shards come out of ore that happens to sit near an aura node. There is no farm for them, no crop, no bee — you either get lucky underground or you do without, and "do without" stops a lot of Thaumcraft projects dead.

So the Quartermaster buys rubble and pays in crystal.

§eBring 64 cobblestone. Take two of each of the six primals.§f

§7Resets every 24 hours, and the timer starts when you CLAIM the reward — not when you finish the hand-in. An unclaimed bounty is a bounty that is not refilling.§r"""


def main():
    apply = "--apply" in sys.argv
    d = json.load(open(DB, encoding="utf-8"))
    qdb, ql = d["questDatabase:9"], d["questLines:9"]

    if any(q["questID:3"] == QID for q in qdb.values()):
        print(f"ABORT: quest {QID} already exists"); return

    board = None
    for k, v in ql.items():
        if v["properties:10"]["betterquesting:10"].get("name:8") == "The Bounty Board":
            board = (k, v); break
    if not board:
        print("ABORT: Bounty Board line not found"); return
    key, line = board

    # place it under the existing Quartermaster column
    ys = [q["y:3"] for q in line["quests:9"].values()]
    xs = [q["x:3"] for q in line["quests:9"].values()]
    x, y = min(xs), max(ys) + 48
    print(f"placing at x={x} y={y} (existing span x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)})")

    qdb[f"{QID}:10"] = {
        "questID:3": QID,
        "preRequisites:11": [],
        "properties:10": {"betterquesting:10": {
            "snd_complete:8": "minecraft:entity.player.levelup",
            "snd_update:8": "minecraft:entity.player.levelup",
            "taskLogic:8": "AND", "visibility:8": "NORMAL",
            "isMain:1": 0, "simultaneous:1": 0,
            "icon:10": it("Thaumcraft:ItemShard", 1, 6),
            "repeatTime:3": DAILY, "globalShare:1": 0, "questLogic:8": "AND",
            "repeat_relative:1": 1, "name:8": "Quartermaster: Crystal Harvest",
            "lockedProgress:1": 0, "autoClaim:1": 0, "isSilent:1": 0,
            "desc:8": DESC}},
        "tasks:9": {"0:10": {
            "partialMatch:1": 1, "autoConsume:1": 0, "groupDetect:1": 0,
            "ignoreNBT:1": 1, "index:3": 0, "consume:1": 1,
            "requiredItems:9": {"0:10": it("minecraft:cobblestone", 64)},
            "taskID:8": "bq_standard:retrieval"}},
        "rewards:9": {
            "0:10": {"rewardID:8": "bq_standard:item", "index:3": 0,
                     "rewards:9": {f"{i}:10": it("Thaumcraft:ItemShard", 2, i)
                                   for i in range(6)}},
            "1:10": {"rewardID:8": "bq_standard:xp", "index:3": 1,
                     "amount:3": 100, "isLevels:1": 0}},
    }

    nxt = max(int(k.split(":")[0]) for k in line["quests:9"]) + 1
    line["quests:9"][f"{nxt}:10"] = {"sizeX:3": 24, "sizeY:3": 24,
                                     "x:3": x, "y:3": y, "id:3": QID}

    print(("APPLIED" if apply else "DRY RUN") + f": quest {QID} 'Quartermaster: Crystal Harvest'")
    print("  in   : 64 cobblestone (consumed)")
    print("  out  : 2x each primal shard (Air Fire Water Earth Order Entropy) + 100 xp")
    print(f"  reset: {DAILY} ticks = {DAILY/20/3600:.0f}h")
    print(f"  line : The Bounty Board (now {len(line['quests:9'])} quests)")
    if apply:
        shutil.copy2(DB, DB + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
        json.dump(d, open(DB, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"\nwritten: {os.path.getsize(DB)} bytes")


def _lint_after_write():
    """A checkbox quest used as a prerequisite locks a whole chapter while
    still showing its tasks ticked - indistinguishable from broken data in
    game. Never leave the database in that state; see bq_lint.py."""
    import os as _os, sys as _sys
    if "--apply" not in _sys.argv:
        return
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    try:
        import bq_lint as _lint
    except ImportError:
        print("WARNING: bq_lint.py not found - quest graph NOT verified")
        return
    rc, problems = _lint.check(DB, fix=True, quiet=True)
    if problems:
        print("\nbq_lint repaired: " + "; ".join(problems))
    else:
        print("\nbq_lint: quest graph clean")


if __name__ == "__main__":
    main()
    _lint_after_write()
