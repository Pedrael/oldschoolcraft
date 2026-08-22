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
M = "Mekanism:"


def it(i, c=1, d=0):
    return {"id:8": i, "Count:3": c, "Damage:2": d, "OreDict:8": ""}


def bag(t=0):
    return it("Thaumcraft:ItemLootBag", 1, t)


DESC = {
700: """§7Mekanism is here for its §emachines§7, not for its ore.

You already have five ways to double ore - the Pulverizer, the SAG Mill, the Macerator, the Crusher and the Arc Furnace. Mekanism's own chain went up to §efive times§7, which would have made all five of them pointless, so the higher tiers are §cswitched off§7.

What is left is the part nothing else in this pack does: a miner that digs by filter, a teleporter, a block that moves items, fluid, power and gas at once, and a box that picks up a machine without breaking it.

Start with salt. It is the least impressive thing in the mod and you will need it anyway.§r""",
701: """§7Osmium is Mekanism's own metal and it does §enot§7 exist in any chunk you have already visited.

That is not a bug and it is not worth digging for at home. Walk somewhere genuinely new, or take the Mining World portal. Bring a pick.

Enriched Iron is iron plus carbon in a Metallurgic Infuser. It is the gate to everything else here.§r""",
702: """§7The §eEnrichment Chamber§7 doubles ore, and that is all it will ever do here.

The Purification Chamber, Chemical Injection Chamber, Dissolution Chamber, Washer and Crystallizer are disabled. If you find a recipe online promising five ingots from one ore, it does not work on this server, by choice.

The chamber still matters - it makes the dusts and compressed parts the rest of Mekanism is built from.§r""",
703: """§7Enriched Alloy is the workhorse component. Almost every machine wants some.

Infuse iron with redstone. Then do it again, because you will never have enough.§r""",
704: """§7Power in Mekanism is measured in Joules, but it will happily eat RF from your Thermal Expansion setup and EU from IC2 - the config allows both.

You do not need a new power plant. You need a cable and a Basic Energy Cube.§r""",
705: """§7The §eConfigurator§7 is the single most useful item in the mod and it looks like nothing.

Left-click a machine face to change what it does. Rotate blocks. Empty a tank. Pick up a machine without losing its contents. Carry it always.§r""",
706: """§7Mekanism makes §eplastic§7, which sounds dull until you want a hundred blocks of something in a specific colour that never burns.

Polyethene comes from ethene, which comes from bio-fuel and hydrogen. This is your first proper gas chain - two inputs, one output, and a reason to care about the Electrolytic Separator.§r""",
707: """§7A §eCardboard Box§7 picks up a machine - contents, orientation, energy and all - and puts it in your inventory as a single item.

Nothing else in this pack does this. Move a whole base without emptying a single chest.§r""",
708: """§7EnviroMine tracks the air you breathe. Bad air is one of the ways this world kills people.

The §eGas Mask§7 seals it completely. Not partially, like most helmets - completely. Between this and a Scuba Tank you can walk into places that were previously simply lethal.

Worth making before you need it.§r""",
709: """§7Reinforced Alloy needs Enriched Alloy and diamond dust, and an Osmium Compressor to press it.

You are now past the point where Mekanism is cheap. Everything after this is a real project.§r""",
710: """§7The §eDigital Miner§7 is why people install this mod.

Give it a filter - ore names, item ids, whatever you like - and a radius, and it mines only what you asked for, from anywhere in range, without touching the rest. Silk touch works. It will strip an ore vein out of a mountain and leave the mountain.

This is the machine that ends manual mining.§r""",
711: """§7Atomic Alloy is the top of the material ladder: Reinforced Alloy, refined obsidian and a Pressurized Reaction Chamber.

There is exactly one reason to make it, and it is the next quest.§r""",
712: """§7A §eTeleporter§7 pair, and the twelve dimensions on this server stop being far away.

Set a frequency, feed it power, and step through. The §ePortable Teleporter§7 does the same from your inventory, which is better than it sounds when you are lost.

The §eQuantum Entangloporter§7 goes further: items, fluids, power, gas and heat, wirelessly, between any two of its kind. It is the last logistics block you will ever place.§r""",
713: """§7A §eRobit§7 follows you around, picks up drops, and can be told to craft, smelt or store.

It is not necessary. It is very good company, and after the Digital Miner and the Teleporter you have earned something silly.§r""",
}

# (qid, name, x, y, prereqs, icon, task or None, rewards)
Q = [
 (700, "Salt and Sawdust", 0, 0, [], "Mekanism:Salt", "Mekanism:Salt", [bag(0)]),
 (701, "Somewhere New", 48, 0, [700], "Mekanism:EnrichedIron", "Mekanism:EnrichedIron", [bag(0), it(M+'EnrichedIron', 8)]),
 (702, "Two Times, No More", 96, 0, [701], "Mekanism:Dust", None, [bag(0)]),
 (703, "Enriched Alloy", 96, -48, [701], "Mekanism:EnrichedAlloy", "Mekanism:EnrichedAlloy", [bag(0), it(M+'EnrichedAlloy', 4)]),
 (704, "Joules, RF and EU", 144, -48, [703], "Mekanism:EnergyTablet", "Mekanism:EnergyTablet", [bag(0)]),
 (705, "The Configurator", 192, -48, [704], "Mekanism:Configurator", "Mekanism:Configurator", [bag(1)]),
 (706, "Plastic and Gas", 144, 48, [703], "Mekanism:Polyethene", "Mekanism:Polyethene", [bag(1)]),
 (707, "Move a Machine", 240, -48, [705], "Mekanism:CardboardBox", "Mekanism:CardboardBox", [bag(1), it(M+'CardboardBox', 2)]),
 (708, "Something to Breathe", 240, 48, [705], "Mekanism:GasMask", "Mekanism:GasMask", [bag(1), it(M+'ScubaTank', 1)]),
 (709, "Reinforced", 192, 48, [706], "Mekanism:ReinforcedAlloy", "Mekanism:ReinforcedAlloy", [bag(1)]),
 (710, "The Digital Miner", 288, -48, [707], "Mekanism:Configurator", None, [bag(2)]),
 (711, "Atomic", 240, 96, [709], "Mekanism:AtomicAlloy", "Mekanism:AtomicAlloy", [bag(2)]),
 (712, "No Distance At All", 288, 96, [711], "Mekanism:TeleportationCore", "Mekanism:TeleportationCore", [bag(2), it(M+'PortableTeleporter',1)]),
 (713, "Robit", 336, -48, [710], "Mekanism:Robit", "Mekanism:Robit", [bag(2)]),
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
    NAME = "The Machine Age"
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
            "icon:10": it(M + "Configurator"),
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
