#!/usr/bin/env python3
"""Modular Powersuits teaching line - "The Suit".

MPS is the one mod here where you literally build the armour piece by piece,
so the Iron Man framing is not decoration: it is how the mod actually works.
Craft a shell, bolt a reactor in, and everything after that is choices about
what to carry and what to leave behind.

Most steps are checkbox tasks because MPS modules are installed through the
Tinker Table GUI and are not items - there is nothing to "retrieve". The eight
that ARE items use verified ids.

Two things this line deliberately teaches, because both are invisible and both
stop people cold:
  * an uncharged suit is worse than no armour at all
  * there is a WEIGHT LIMIT, and going over it slows you to a crawl

Run with the server STOPPED.
"""
import json, os, shutil, sys, time

DB = "/home/duduserver/minecraft/1.7.10/world/betterquesting/QuestDatabase.json"
P = "powersuits:"


def it(i, c=1, d=0):
    return {"id:8": i, "Count:3": c, "Damage:2": d, "OreDict:8": ""}


def bag(t=0):
    return it("Thaumcraft:ItemLootBag", 1, t)


DESC = {
620: """§7Read and tick. This is what the whole line is about.§r

Every other set of armour in this pack arrives finished. You craft it, you wear it, that is the end of the conversation.

§eThis one arrives empty.§f

A power suit is a shell with slots in it. What it does — fly, glow, dig, shoot, keep you cool, keep you fed — depends entirely on what you bolt into it, and on whether you left enough power and enough weight allowance to run any of it.

You are not crafting armour. You are building a machine that you happen to wear.""",

621: """Power armour components. The box of scraps.

These are the raw parts every piece of the suit is made from, and you will want a lot more of them than you think.

§7Everything downstream is gated on these. Make a stack before you start, or you will be stopping every five minutes to make four more.§r""",

622: """The §eTinker Table§f. Your workshop.

This is where the entire mod happens. Place it, right click it, and put a suit piece in the slot.

The left panel is every module you could install. The right is what it costs and what it weighs. §eNothing you do at a crafting bench matters after this point§f — the table is the mod.

§7It also SALVAGES. Pull a module back out and you get most of the materials back, so nothing you try is permanent and nothing is wasted.§r""",

623: """The chestplate. The core of it.

Start here rather than with the helmet, for a blunt reason: the chest piece has the most room, so it is where your battery goes, and §ewithout a battery nothing else on the suit runs at all§f.

An unpowered power suit is not weak armour. It is §eno armour§f, with weight.

§7Craft the other three pieces when you can, but power this one first.§r""",

624: """§7Read and tick. Open the Tinker Table and install a battery.§r

§eBasic, Advanced, then Elite.§f Each holds far more than the last and weighs far more too.

This is the arc reactor. Everything the suit does draws from it, and when it hits empty the suit stops being a suit and starts being an expensive shirt.

§7Put it in the chestplate. Batteries are heavy and the chest has the most capacity to spare.§r""",

625: """§7Read and tick. Charge the suit.§r

MPS runs on §eRF§f, the same power as Thermal Expansion and EnderIO — which you already have if you have touched the Power and Automation chapter.

Stand a charged §eEnergy Cell§f or §eCapacitor Bank§f down, put the suit in it, and wait. Or wear it and stand near a charger.

§eEnergy per RF is 0.1 here§f, so a modest generator refills you quickly. Getting power to the suit is not the hard part; remembering to is.""",

626: """§7Read and tick. Install plating, and meet the weight limit.§r

§eIron Plating§f is cheap. §eDiamond Plating§f is better. Each point of armour costs weight.

Now the part nobody tells you and everybody hits:

§eThe suit has a WEIGHT LIMIT of 25,000 grams.§f Go over it and you do not get a warning, an error, or a red icon — you just get §eslow§f, and you spend an hour wondering what broke.

§7Watch the weight number in the Tinker Table. It is the real budget in this mod, more than power ever is.§r""",

627: """The helmet. Now it has a face.

§7Read and tick once you have installed something into it.§r

The helmet is where the suit stops being armour and starts being equipment:

§eNight Vision§f — see in the dark, permanently, for a trickle of power.
§eOre Scanner§f — highlights ore through stone.
§eBinoculars§f — zoom.
§eAuto-Feeder§f — eats for you, out of your inventory.

§7On this server the helmet is also a sealed respirator with full air filtering. That is not stock MPS, that is the environment system here. Check the tooltip.§r""",

628: """§7Read and tick. Get off the ground.§r

Flight comes in stages and you want them in this order:

§eJump Assist§f — jump higher. Cheap, light, immediately useful.
§eGlider§f — hold space while falling, travel a long way down a hill.
§eJetpack§f then §eJet Boots§f — actual powered flight.
§eFlight Control§f — makes the above steerable rather than alarming.
§eParachute§f — the one that stops you dying when the battery runs out.

§7Top flight speed here is 25 m/s. Fitting a jetpack and forgetting a parachute is the single most common way to die in this mod.§r""",

629: """The Power Fist. The repulsor.

One item, every tool, and a weapon if you want one. Install into it:

§ePickaxe, Axe, Shovel, Shears, Grafter, Chisel§f — the whole toolbox in one slot.
§ePlasma Cannon§f — charge and release.
§eRailgun§f — long range, expensive per shot.
§eBlade Launcher§f, §eLightning Summoner§f — exactly what they sound like.

§7Tool modules on the fist mean the rest of your hotbar is free. That alone is worth the build.§r""",

630: """§7Read and tick. Deal with the heat.§r

Every module you run makes §eheat§f, and the suit has a cap — §e50 by default here§f. Fill it and you start taking damage and the suit throttles.

§eHeat Sink§f — passive, cheap.
§eCooling System§f — active, better.
§eLiquid Nitrogen Cooling§f — the serious one.

Solar generators are the worst offenders: they make power in daylight and a lot of heat with it.

§7A suit that overheats in a desert at noon is a suit built for somewhere else. Now that this server has real temperature, that is doubly true.§r""",

631: """§7Read and tick. Cut the cord.§r

Generators let the suit charge itself:

§eSolar Generator§f — daylight, and heat with it.
§eThermal Generator§f — burns fuel.
§eKinetic Generator§f — charges as you walk and run. The quiet favourite: no heat, no fuel, and you were walking anyway.

§7Stack a kinetic generator with jump assist and the suit pays for its own movement. That is the point where it stops needing a base.§r""",

632: """A Lux Capacitor.

Fires a light that sticks to whatever it hits, in whatever colour you set. No torch, no placement, no gravity.

§7Useful, and also the most fun thing in the mod. Light a whole cavern from the entrance.§r""",

633: """§7Read and tick when all four pieces and the fist are built and powered.§r

§eThe Mark III.§f

Helmet, chestplate, leggings, boots, and the fist. Powered, plated, cooled, and under the weight limit.

What it actually is: night vision that never runs out, flight, every tool in one slot, a magnet that picks up drops, a feeder so you never open your inventory to eat, and armour that repairs at a table instead of an anvil.

§7There is no tier above this. From here the suit only changes when you change your mind about what to carry.§r""",
}

# (qid, name, x, y, prereqs, icon, task or None, rewards)
Q = [
 (620, "A Box of Scraps",        0,   0, [],    P+"powerArmorComponent",    None,                        [bag(0)]),
 (621, "Components",            48,   0, [620], P+"powerArmorComponent",    P+"powerArmorComponent",     [bag(0), it(P+"powerArmorComponent", 8)]),
 (622, "The Workshop",          96,   0, [621], P+"tile.tinkerTable",       P+"tile.tinkerTable",        [bag(0), it(P+"powerArmorComponent", 8)]),
 (623, "The Core",             144,   0, [622], P+"item.powerArmorChestplate", P+"item.powerArmorChestplate", [bag(1)]),
 (624, "The Reactor",          192,   0, [623], "ThermalExpansion:Cell",    None,                        [bag(1)]),
 (625, "Charging",             240,   0, [624], "ThermalExpansion:Cell",    None,                        [bag(0)]),
 (626, "Plating, and Weight",  288,   0, [625], "minecraft:diamond",        None,                        [bag(1)]),
 (627, "The Helmet",           192, -48, [624], P+"item.powerArmorHelmet",  P+"item.powerArmorHelmet",   [bag(1)]),
 (628, "Get Off the Ground",   288, -48, [626], "minecraft:feather",        None,                        [bag(2)]),
 (629, "The Repulsor",         240,  48, [625], P+"item.powerFist",         P+"item.powerFist",          [bag(2)]),
 (630, "Heat",                 336,   0, [626], "minecraft:blaze_powder",   None,                        [bag(1)]),
 (631, "Off the Grid",         336, -48, [630], "minecraft:daylight_detector", None,                     [bag(1)]),
 (632, "Let There Be Light",   144, -48, [622], P+"tile.luxCapacitor",      P+"tile.luxCapacitor",       [bag(0), it(P+"tile.luxCapacitor", 4)]),
 (633, "The Mark III",         384,   0, [631], P+"item.powerArmorChestplate", None,                     [bag(2)]),
]


def build(qid, name, x, y, pre, icon, task, rewards):
    tasks = ({"0:10": {"index:3": 0, "taskID:8": "bq_standard:checkbox"}} if task is None
             else {"0:10": {"partialMatch:1": 1, "autoConsume:1": 0, "groupDetect:1": 0,
                            "ignoreNBT:1": 1, "index:3": 0, "consume:1": 0,
                            "requiredItems:9": {"0:10": it(task)},
                            "taskID:8": "bq_standard:retrieval"}})
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
            "tasks:9": tasks,
            "rewards:9": {"0:10": {"rewardID:8": "bq_standard:item", "index:3": 0,
                                   "rewards:9": {f"{i}:10": r for i, r in enumerate(rewards)}},
                          "1:10": {"rewardID:8": "bq_standard:xp", "index:3": 1,
                                   "amount:3": 200, "isLevels:1": 0}}}


def main():
    apply = "--apply" in sys.argv
    d = json.load(open(DB, encoding="utf-8"))
    qdb, ql = d["questDatabase:9"], d["questLines:9"]
    NAME = "The Suit"
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
            "icon:10": it(P + "item.powerArmorChestplate"),
            "bg_image:8": "", "bg_size:3": 256,
            "desc:8": "Armour that arrives empty. What it does is up to you."}},
        "quests:9": {f"{i}:10": {"sizeX:3": 24, "sizeY:3": 24, "x:3": q[2], "y:3": q[3], "id:3": q[0]}
                     for i, q in enumerate(Q)},
        "lineID:3": key, "order:3": len(ql)}
    print(("APPLIED " if apply else "DRY RUN ") + f"{len(Q)} quests, line {key}")
    for q in Q:
        print(f"  {q[0]}  {q[1]:22} {'checkbox' if q[6] is None else q[6]}")
    if apply:
        shutil.copy2(DB, DB + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
        json.dump(d, open(DB, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"\nwritten: {os.path.getsize(DB)} bytes")


if __name__ == "__main__":
    main()
