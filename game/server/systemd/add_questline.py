#!/usr/bin/env python3
"""Add the "Dressing for the Weather" quest line to BetterQuesting.

Why a quest line and not just tooltips: quest data syncs server -> client
automatically, so this reaches VerrassVerrass and CubeThePenguin without anyone
copying a file. Tooltips don't -- that gap is what went wrong with torches.

Run with the server STOPPED. BetterQuesting writes QuestDatabase.json on
shutdown and would overwrite anything added underneath it.
"""
import json, os, shutil, sys, time

DB = "/home/duduserver/minecraft/1.7.10/world/betterquesting/QuestDatabase.json"
BAG = lambda dmg: {"id:8": "Thaumcraft:ItemLootBag", "Count:3": 1, "Damage:2": dmg, "OreDict:8": ""}


def item(i, c=1, d=0):
    return {"id:8": i, "Count:3": c, "Damage:2": d, "OreDict:8": ""}


DESC = {
508: """§7Read this one. It ticks itself.§r

Three things out here kill you quietly, and none of them show up in your health bar until it is too late.

§eThirst§f drains whenever you are awake, faster in the sun. A camel pack on your chestplate is the fix — and until today it only attached to vanilla chestplates, which is why your water never seemed to work.

§eTemperature§f swings between day and night. It has never killed anyone on this server, because it was running at a third speed. It isn't any more. Nights are cold now.

§eAir§f goes bad underground. A lead helmet fixes it for almost nothing.

The rest of this chapter is what to wear about each one.""",

509: """You are holding a camel pack.

It clips to a chestplate and drinks for you. Simple, and quietly broken for everyone wearing anything interesting.

§7An armour piece with no environmental entry did not mean "no effect". It meant the pack would not attach at all. Nine chestplates in the entire game allowed one.§r

§eEvery chestplate now carries a camel pack.§f Thaumium, manasteel, dark steel, ichorcloth, neptunium, bound plate, hazmat, scorpion, fur, and every set you haven't crafted yet. Nobody has to choose between carrying water and wearing good armour.""",

510: """A lead helmet is a respirator.

Wear one deep underground and foul air stops eating you. It is the most useful helmet in the pack for anyone who mines, and lead was the deadest metal we had.

§eThree lead and two charcoal§f makes one — the charcoal is the filter element. There is a full-price recipe too, but no reason to use it.""",

511: """Frost scorpion armour keeps you warm.

It always looked like it should and never did. Now it is the warm kit: as much heat as nickel, and it damps the cold on top rather than only adding warmth.

§7Frost scorpions live in cold biomes, which is exactly where you want this.§r

It is not free. Warm gear is a liability at noon.""",

512: """Nether scorpion armour sheds heat.

§eTin is still the best sun protection in the pack§f — that hasn't changed and isn't going to. What this does instead is shed heat §eand stay warm after dark§f, which tin emphatically does not.

Tin is desert gear. This is Nether gear, and the Nether doesn't have a night.""",

513: """Cave scorpion armour filters air.

The helmet does most of the work, but every piece contributes — §ea full set filters more than a lead helmet alone§f.

§7That is the trade. The lead helmet is one cheap slot and good enough. This is four slots and better, and you have to go kill cave scorpions for it.§r""",

514: """Fur is warm.

You have been feeding fur into nickel armour recipes as lining this whole time. Now it works on its own: real early-game warmth, available long before you have a nickel supply.

§eAnd it is stifling in the sun.§f That is the deal, same as tin's cold nights. Hide is the milder version if you want something you can leave on.""",

515: """The hazmat suit is a hazmat suit again.

It protected against nothing at all until now, which for a sealed chemical suit was quite a thing. It is now §ethe best air protection in the pack§f — better than a lead helmet, better than a full cave-scorpion set.

§7It also has almost no armour value, so you are trading protection from monsters for protection from the air. Deep mining kit, not adventuring kit.§r""",
}

# (id, name, x, y, prereqs, icon, task_item, rewards)
QUESTS = [
 (508, "Three Ways to Die",            0,   0, [],    "enviromine:camelPack",            None,                            [BAG(0)]),
 (509, "Your Water Was Never Working", 48, -48, [508], "enviromine:camelPack",            "enviromine:camelPack",          [BAG(0), item("enviromine:camelPack")]),
 (510, "The Cheap Respirator",         48,   0, [508], "ThermalFoundation:armor.helmetLead", "ThermalFoundation:armor.helmetLead", [BAG(0), item("ThermalFoundation:armor.helmetLead")]),
 (511, "Frost Chitin",                 48,  48, [508], "MoCreatures:scorpplatefrost",     "MoCreatures:scorpplatefrost",   [BAG(1)]),
 (512, "Nether Chitin",                96,  48, [511], "MoCreatures:scorpplatenether",    "MoCreatures:scorpplatenether",  [BAG(1)]),
 (513, "Cave Chitin",                  96,   0, [510], "MoCreatures:scorpplatecave",      "MoCreatures:scorpplatecave",    [BAG(1)]),
 (514, "Skin It",                      96,  96, [511], "MoCreatures:furchest",            "MoCreatures:furchest",          [BAG(0), item("MoCreatures:fur", 4)]),
 (515, "Sealed",                      144,   0, [513], "IC2:itemArmorHazmatHelmet",       "IC2:itemArmorHazmatHelmet",     [BAG(2)]),
]


def build(qid, name, x, y, prereqs, icon, task_item, rewards):
    tasks = ({"0:10": {"index:3": 0, "taskID:8": "bq_standard:checkbox"}} if task_item is None
             else {"0:10": {"partialMatch:1": 1, "autoConsume:1": 0, "groupDetect:1": 0,
                            "ignoreNBT:1": 1, "index:3": 0, "consume:1": 0,
                            "requiredItems:9": {"0:10": item(task_item)},
                            "taskID:8": "bq_standard:retrieval"}})
    return {
        "questID:3": qid,
        "preRequisites:11": prereqs,
        "properties:10": {"betterquesting:10": {
            "snd_complete:8": "minecraft:entity.player.levelup",
            "snd_update:8": "minecraft:entity.player.levelup",
            "taskLogic:8": "AND", "visibility:8": "NORMAL",
            "isMain:1": 0, "simultaneous:1": 0,
            "icon:10": item(icon),
            "repeatTime:3": -1, "globalShare:1": 0, "questLogic:8": "AND",
            "repeat_relative:1": 1, "name:8": name,
            "lockedProgress:1": 0, "autoClaim:1": 0, "isSilent:1": 0,
            "desc:8": DESC[qid]}},
        "tasks:9": tasks,
        "rewards:9": {
            "0:10": {"rewardID:8": "bq_standard:item", "index:3": 0,
                     "rewards:9": {f"{i}:10": r for i, r in enumerate(rewards)}},
            "1:10": {"rewardID:8": "bq_standard:xp", "index:3": 1,
                     "amount:3": 100, "isLevels:1": 0}},
    }


def main():
    apply = "--apply" in sys.argv
    d = json.load(open(DB, encoding="utf-8"))
    qdb, ql = d["questDatabase:9"], d["questLines:9"]

    existing_ids = {q["questID:3"] for q in qdb.values()}
    clash = existing_ids & {q[0] for q in QUESTS}
    if clash:
        print("ABORT: quest IDs already used:", sorted(clash)); return

    line_key = f"{max(int(k.split(':')[0]) for k in ql) + 1}:10"
    if any(v["properties:10"]["betterquesting:10"].get("name:8") == "Dressing for the Weather"
           for v in ql.values()):
        print("ABORT: quest line already present"); return

    for q in QUESTS:
        qdb[f"{q[0]}:10"] = build(*q)

    ql[line_key] = {
        "properties:10": {"betterquesting:10": {
            "visibility:8": "NORMAL", "name:8": "Dressing for the Weather",
            "icon:10": item("enviromine:camelPack"),
            "bg_image:8": "", "bg_size:3": 256,
            "desc:8": "Thirst, cold and bad air. What to wear about each."}},
        "quests:9": {f"{i}:10": {"sizeX:3": 24, "sizeY:3": 24, "x:3": q[2], "y:3": q[3],
                                 "id:3": q[0]} for i, q in enumerate(QUESTS)},
        "lineID:3": int(line_key.split(":")[0]),
        "order:3": len(ql),
    }

    print(f"{'APPLY' if apply else 'DRY RUN'}: +{len(QUESTS)} quests, line key {line_key}")
    for q in QUESTS:
        kind = "checkbox" if q[6] is None else f"retrieve {q[6]}"
        print(f"  {q[0]}  {q[1]:32} {kind}")
    if apply:
        bak = DB + f".bak-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(DB, bak)
        json.dump(d, open(DB, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"\nbackup: {bak}\nwritten: {DB} ({os.path.getsize(DB)} bytes)")


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
