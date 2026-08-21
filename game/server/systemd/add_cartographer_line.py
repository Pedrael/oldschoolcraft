#!/usr/bin/env python3
"""The Cartographer - an exploration line across every dimension on this server.

There are twelve dimensions here and nothing tied them together. Milestones
covered four vanilla beats; Survival & Exploration was seven checkbox tips.
Meanwhile the Wyvern Lair had never been entered once.

One quest per dimension: go there, bring back a token. Every task is a real
retrieval - where a dimension has no truly exclusive item, the token is the
thing that gets you in or the thing you dig up while you are there. Nothing
here completes by accident in the overworld.

Quests are deliberately NOT chained. Exploration is not a ladder and the mods
do not enforce an order; only the capstone requires the rest.

Run with the server STOPPED.
"""
import json, os, shutil, sys, time

DB = "/home/duduserver/minecraft/1.7.10/world/betterquesting/QuestDatabase.json"


def it(i, c=1, d=0):
    return {"id:8": i, "Count:3": c, "Damage:2": d, "OreDict:8": ""}


def bag(t=0):
    return it("Thaumcraft:ItemLootBag", 1, t)


DESC = {
640: """§eThe Nether.§f Dimension -1, and the one everybody already knows.

A blaze rod proves you found a fortress, which is the only part of the Nether worth crossing lava for — and since the Fortune update those fortress chests have a real table under them instead of saddles and wart.

§7Blaze rods exist nowhere else. That is the whole idea of this chapter: bring back something that could only have come from there.§r""",

641: """§eThe End.§f Dimension 1.

End stone is the floor of it. You cannot get a single block of it anywhere else, which makes it the honest token.

§7You need twelve eyes of ender and a stronghold to get in. If you have never been, that is the trip — and the dragon is optional for this quest. Walking on the island is enough.§r""",

642: """§eThe Twilight Forest.§f Dimension 7, behind a thrown diamond.

Torchberries grow on the walls of hollow hills and glow faintly. They are everywhere there and nowhere else.

§7This is the easiest token in the chapter — you can have it ten minutes after building the portal, without fighting anything. See The Twilight Forest chapter for the rest.§r""",

643: """§eThe Runic Dungeons.§f Dimension -34.

You get in with Magical Chalk, which since the Fortune update turns up in ordinary dungeon chests instead of only village blacksmiths.

Runic steel is forged from what you find inside.

§7Four room types, and since the Fortune rebuild they finally have four DIFFERENT loot tables. The Obsidian room is the deep one.§r""",

644: """§eThe Spectre Dimension.§f Dimension 2.

A blank white world with nothing in it, reached with a Spectre Key. It is the closest thing this pack has to a pocket dimension you can build in without anything ever spawning.

§7Bring the key itself. Making one is the hard part; the dimension is calm once you arrive.§r""",

645: """§eThe Mining World.§f Dimension 6.

A whole world made to be strip-mined, so you never have to hollow out the one you live in. It resets in some packs; here it does not, so treat it as a second overworld with no scenery to protect.

Sticky ore only generates there.

§7If you have ever felt bad about what quarrying does to a landscape, this is where to do it instead.§r""",

646: """§eThe Deep Dark.§f Dimension -100.

Pitch black, no sky, endermen everywhere and unusually rich ore. Extra Utilities built it as a straight trade: better resources, worse conditions.

Bedrockium is the deepest thing you can come back with.

§7Bring light and bring something that stops endermen looking at you. On this server the Deep Dark is also where an air-filtering helmet stops being optional.§r""",

647: """§eThe Last Millenium.§f Dimension -112.

The end of time — a flat, dead expanse with an ender-flavoured horizon. There is very little there, and that is deliberate.

An unstable ingot is the token.

§7One of two Extra Utilities dimensions on this server, and by far the stranger of the pair.§r""",

648: """§eThe Bedrock Dimension.§f Dimension -19, from Thaumic Tinkerer.

Exactly what it says: a world of bedrock. Getting in requires building the portal, which is the whole challenge — once you are there, there is nothing to fight.

§7Bring back the portal itself. If you can make one, you can reach it.§r""",

649: """§eThe Cave Dimension.§f Dimension -2 — and this one is EnviroMine's, which means it belongs to the same system that decides whether you freeze.

Endless caves, bad air, no surface.

A Davy lamp is the miner's answer: light that does not set off the gas pockets down there.

§7There is also, very rarely, a grue. One in a million, and it does not show up on Halloween or Friday the 13th. Nobody here has met one.§r""",

650: """§eThe Wyvern Lair.§f Dimension -17.

§7This is the one nobody has ever visited. The folder for it does not exist because no player has ever set foot there.§r

Mo' Creatures built an entire flying-mount dimension behind a portal staff, and LIVING-WORLD.md called it the single biggest prize on this server. Wyverns drop eggs 10% of the time, mother wyverns 33%, and a hatched egg is a flying mount.

Bring the portal staff.

§7If you do one quest in this chapter, do this one. It is the largest unopened thing here.§r""",

651: """§eThe Outer Lands.§f Thaumcraft's eldritch dimension.

Reached through an obsidian totem in an eldritch ring, and it is hostile in a way the others are not — the guardians there hit hard, and sanity is a real resource in Thaumcraft.

An eldritch object is what you carry out.

§7This is the hardest token in the chapter. Bring the best armour you own, and something that filters air.§r""",

652: """§eTwelve dimensions.§f

Nether, End, Twilight Forest, Runic Dungeons, Spectre, Mining World, Deep Dark, Last Millenium, Bedrock, Caves, Wyvern Lair, Outer Lands.

Hand in the five that prove the long trips: a blaze rod, a block of end stone, torchberries, the wyvern staff, and sticky ore.

§7There is no reward here that beats having been. But there is a rare bag anyway, because you earned it.§r""",
}

# (qid, name, x, y, prereqs, icon, task item(s), rewards)
Q = [
 (640, "The Nether",           0,   0, [], "minecraft:blaze_rod",             [("minecraft:blaze_rod", 1)],              [bag(0)]),
 (641, "The End",             48,   0, [], "minecraft:end_stone",             [("minecraft:end_stone", 1)],              [bag(1)]),
 (642, "The Twilight Forest", 96,   0, [], "TwilightForest:item.torchberries",[("TwilightForest:item.torchberries", 1)], [bag(0)]),
 (643, "The Runic Dungeons", 144,   0, [], "runicdungeons:item.runicSteel",   [("runicdungeons:item.runicSteel", 1)],    [bag(1)]),
 (644, "The Spectre World",    0,  48, [], "RandomThings:spectreKey",         [("RandomThings:spectreKey", 1)],          [bag(1)]),
 (645, "The Mining World",    48,  48, [], "Aroma1997sDimension:stickyOre",   [("Aroma1997sDimension:stickyOre", 1)],    [bag(0)]),
 (646, "The Deep Dark",       96,  48, [], "ExtraUtilities:bedrockiumIngot",  [("ExtraUtilities:bedrockiumIngot", 1)],   [bag(1)]),
 (647, "The Last Millenium", 144,  48, [], "ExtraUtilities:unstableingot",    [("ExtraUtilities:unstableingot", 1)],     [bag(1)]),
 (648, "The Bedrock World",    0,  96, [], "ThaumicTinkerer:bedrockPortal",   [("ThaumicTinkerer:bedrockPortal", 1)],    [bag(1)]),
 (649, "The Cave Dimension",  48,  96, [], "enviromine:davy_lamp",            [("enviromine:davy_lamp", 1)],             [bag(1)]),
 (650, "The Wyvern Lair",     96,  96, [], "MoCreatures:staffportal",         [("MoCreatures:staffportal", 1)],          [bag(2)]),
 (651, "The Outer Lands",    144,  96, [], "Thaumcraft:ItemEldritchObject",   [("Thaumcraft:ItemEldritchObject", 1)],    [bag(2)]),
 (652, "The Cartographer",   216,  48, [640,641,642,643,644,645,646,647,648,649,650,651],
       "TwilightForest:item.magicMap",
       [("minecraft:blaze_rod",1), ("minecraft:end_stone",1), ("TwilightForest:item.torchberries",1),
        ("MoCreatures:staffportal",1), ("Aroma1997sDimension:stickyOre",1)],
       [bag(2), bag(2)]),
]


def build(qid, name, x, y, pre, icon, tasks_items, rewards):
    req = {f"{i}:10": it(n, c) for i, (n, c) in enumerate(tasks_items)}
    return {"questID:3": qid, "preRequisites:11": pre,
            "properties:10": {"betterquesting:10": {
                "snd_complete:8": "minecraft:entity.player.levelup",
                "snd_update:8": "minecraft:entity.player.levelup",
                "taskLogic:8": "AND", "visibility:8": "NORMAL",
                "isMain:1": 0, "simultaneous:1": 0, "icon:10": it(icon),
                "repeatTime:3": -1, "globalShare:1": 0, "questLogic:8": "AND",
                "repeat_relative:1": 1, "name:8": name,
                "lockedProgress:1": 0, "autoClaim:1": 0, "isSilent:1": 0,
                "desc:8": DESC[qid]}},
            "tasks:9": {"0:10": {
                "partialMatch:1": 1, "autoConsume:1": 0, "groupDetect:1": 0,
                "ignoreNBT:1": 1, "index:3": 0, "consume:1": 0,
                "requiredItems:9": req, "taskID:8": "bq_standard:retrieval"}},
            "rewards:9": {"0:10": {"rewardID:8": "bq_standard:item", "index:3": 0,
                                   "rewards:9": {f"{i}:10": r for i, r in enumerate(rewards)}},
                          "1:10": {"rewardID:8": "bq_standard:xp", "index:3": 1,
                                   "amount:3": 250, "isLevels:1": 0}}}


def main():
    apply = "--apply" in sys.argv
    d = json.load(open(DB, encoding="utf-8"))
    qdb, ql = d["questDatabase:9"], d["questLines:9"]
    NAME = "The Cartographer"
    if any(v["properties:10"]["betterquesting:10"].get("name:8") == NAME for v in ql.values()):
        print("ABORT: line already present"); return
    have = {q["questID:3"] for q in qdb.values()}
    clash = have & {q[0] for q in Q}
    if clash:
        print("ABORT: quest ids already in use:", sorted(clash)); return
    for q in Q:
        qdb[f"{q[0]}:10"] = build(*q)
    key = max(int(k.split(":")[0]) for k in ql) + 1
    ql[f"{key}:10"] = {
        "properties:10": {"betterquesting:10": {
            "visibility:8": "NORMAL", "name:8": NAME,
            "icon:10": it("TwilightForest:item.magicMap"),
            "bg_image:8": "", "bg_size:3": 256,
            "desc:8": "Twelve dimensions. Bring something back from each."}},
        "quests:9": {f"{i}:10": {"sizeX:3": 24, "sizeY:3": 24, "x:3": q[2], "y:3": q[3], "id:3": q[0]}
                     for i, q in enumerate(Q)},
        "lineID:3": key, "order:3": len(ql)}
    print(("APPLIED " if apply else "DRY RUN ") + f"{len(Q)} quests, line {key}")
    for q in Q:
        print(f"  {q[0]}  {q[1]:22} {', '.join(n for n, _ in q[6])}")
    if apply:
        shutil.copy2(DB, DB + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
        json.dump(d, open(DB, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"\nwritten: {os.path.getsize(DB)} bytes")


if __name__ == "__main__":
    main()
