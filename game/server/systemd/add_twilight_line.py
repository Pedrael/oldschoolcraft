#!/usr/bin/env python3
"""Twilight Forest teaching line — folds TF into the quest book.

TF ships a full parallel progression that connects to nothing else on this
server: not the Fortune tables, not the Great Work, not the book. This line is
the bridge. Prerequisites mirror TF's OWN gating (the Lich is invulnerable until
the Naga is dead, and so on), so the chain teaches the real order rather than an
invented one.

Every id below was verified against this world's registry first.
Run with the server STOPPED.
"""
import json, os, shutil, sys, time

DB = "/home/duduserver/minecraft/1.7.10/world/betterquesting/QuestDatabase.json"
T = "TwilightForest:"


def it(i, c=1, d=0):
    return {"id:8": i, "Count:3": c, "Damage:2": d, "OreDict:8": ""}


def bag(t=0):
    return it("Thaumcraft:ItemLootBag", 1, t)


DESC = {
600: """§7Read and tick. Building the portal is the whole first step.§r

Dig a 2x2 pool of water somewhere grassy and wooded. Put §eflowers or mushrooms§f all the way around the edge — any of them, at least one per side.

Then throw a §ediamond§f into the water. Not place. §eThrow§f it — Q, into the pool.

Lightning strikes, and the pool becomes a portal. Jump in.

§7The Twilight Forest is permanently dusk. The surface is not especially dangerous; the danger is inside the structures, and each one is locked until you have beaten the one before it.§r""",

601: """You are holding a live root.

Hollow hills are the small grassy domes scattered everywhere. They come in three sizes, and the bigger they are the nastier what is inside. §eStart with the small ones.§f

Inside you will find ores, live roots and the occasional chest. Live root is the early material here — it makes ironwood, which is the first gear worth owning.

§7Everything at this stage is safe enough to do alone. Very little after it is.§r""",

602: """A magic map focus.

Combine it with a blank map for a §eMagic Map§f, which draws TF structures as icons instead of terrain. That is the difference between wandering and hunting.

There is also a §eMaze Map§f for labyrinths and an §eOre Map§f for underground.

§7Your minimap does not show TF structures. This does. Make one before you go looking for the Naga.§r""",

603: """Ironwood — the first real material here.

Live root plus gold makes ironwood raw, which smelts into ingots. The armour is roughly iron tier, but it §erepairs itself slowly§f and never needs an anvil.

§7This is the gear you want before touching the Naga. Walking in wearing iron is how people bounce off Twilight Forest and never go back.§r""",

604: """§eYou killed the Naga.§f

First boss, first real gate. Scales come from its courtyard — the big spiral of stone walls.

Scale armour is the best available at this point, and more importantly §ekilling the Naga is what makes the Lich vulnerable§f. The bosses are locked in order. You cannot skip ahead.

§7Bring a bow. It charges in straight lines, and the pillars are there for a reason.§r""",

605: """§eThe Lich is dead.§f

Second boss, in the tall dark tower. It shields itself and summons help — break the shields by §ereflecting its own bolts back§f with any sword.

Its scepters are genuinely good: Twilight fires bolts, Zombie raises minions, Life Drain heals you for damage dealt.

§7Killing the Lich unlocks the Labyrinth and the Hydra. The ladder continues.§r""",

606: """Steeleaf.

Dropped in the Labyrinth and by the Minoshroom. It is a tier above ironwood — genuinely good armour, and light.

§7If you are going to collect one material here and make a full set of it, make it this one. It carries you through the middle of the mod.§r""",

607: """Meef. From the Minoshroom, at the bottom of the Labyrinth.

The Labyrinth is an underground maze under a grassy ceiling — the entrance is a hole in the ground, not a building. Bring a §eMaze Map§f or you will be down there a very long time.

§7Meef Stroganoff is one of the better foods in the pack. And now that food moves your body temperature, a hot meal underground is not just calories.§r""",

608: """§eThe Hydra is dead.§f Three heads to start, more as you cut them off.

Fiery blood is the drop, and it makes §efiery armour and the fiery sword§f — the sword sets things alight, the armour burns whatever hits you.

§7On this server fiery armour also sheds heat and stays warm after dark. That is not stock Twilight Forest, that is the environment system this server runs. Read the tooltip.§r""",

609: """Knightmetal, from the Goblin Knight Stronghold.

The stronghold is guarded by armoured knights that block from the front — §ehit them from behind or above§f. Armor shards fuse into knightmetal ingots.

Knightly armour is the heavy tier, and the §eknightmetal ring§f is a genuinely useful bauble.

§7This is where Twilight Forest stops being a side trip and becomes a project.§r""",

610: """Carminite. From the Dark Tower, and the Ur-Ghast at the top of it.

The tower is full of §ecarminite reactors and builders§f — blocks that rebuild the maze around you while you are still inside it. It is the most hostile structure in the mod.

§7Carminite gates the late tiers. If you are holding this, you have done most of Twilight Forest.§r""",

611: """Arctic fur, from the Glacier.

Yetis drop it. The Alpha Yeti drops §ealpha fur§f, which is the better version.

Arctic armour is the cold-weather kit — and §eon this server that means something§f. It is one of the warmest sets in the game here, rivalling nickel, because the environment system gives it real insulation rather than a flat bonus.

§7Check the tooltip. It says exactly what it does.§r""",

612: """§7Read and tick.§r

The §eUncrafting Table§f is Twilight Forest's best-kept secret, and it is not a boss drop — you can build one early.

It takes a crafted item back apart into its ingredients. It also §erepairs damaged items§f, and with some cleverness it moves enchantments between things.

§7It costs XP, and it works on items from every mod on this server, not only Twilight Forest. That is why it matters more than it sounds.§r""",

613: """A Charm of Keeping.

Die with it and you keep your inventory — tier 1 keeps the hotbar, tier 2 keeps everything, tier 3 keeps armour too. It is consumed when it saves you.

The §eCharm of Life§f is the other one: it revives you where you fell, at half health, once.

§7This server already writes a full backup of your inventory on every single death, so nothing is ever truly lost. But getting it back needs an op and a walk. A charm needs neither.§r""",
}

# (qid, name, x, y, prereqs, icon, task or None, rewards)
Q = [
 (600, "A Diamond in the Water",   0,   0, [],    "minecraft:diamond",        None,                       [bag(0)]),
 (601, "Hollow Hills",            48,   0, [600], T+"item.liveRoot",          T+"item.liveRoot",          [bag(0), it(T+"item.magicMapFocus")]),
 (602, "Read the Land",           48, -48, [600], T+"item.magicMapFocus",     T+"item.magicMapFocus",     [bag(0), it("minecraft:map")]),
 (603, "Ironwood",                96,   0, [601], T+"item.ironwoodIngot",     T+"item.ironwoodIngot",     [bag(0), it(T+"item.ironwoodIngot", 4)]),
 (604, "The Naga",               144,   0, [603], T+"item.nagaScale",         T+"item.nagaScale",         [bag(1), it(T+"item.charmOfKeeping1")]),
 (605, "The Lich",               192,   0, [604], T+"item.scepterTwilight",   T+"item.scepterTwilight",   [bag(1)]),
 (606, "Steeleaf",               240, -48, [605], T+"item.steeleafIngot",     T+"item.steeleafIngot",     [bag(1), it(T+"item.steeleafIngot", 6)]),
 (607, "The Labyrinth",          240,   0, [605], T+"item.meefRaw",           T+"item.meefRaw",           [bag(1), it(T+"item.mazeMapFocus")]),
 (608, "The Hydra",              288,   0, [607], T+"item.fieryBlood",        T+"item.fieryBlood",        [bag(2)]),
 (609, "Knightly Business",      336,   0, [608], T+"item.knightMetal",       T+"item.knightMetal",       [bag(2), it(T+"item.armorShards", 4)]),
 (610, "The Dark Tower",         384,   0, [609], T+"item.carminite",         T+"item.carminite",         [bag(2)]),
 (611, "The Cold Ones",          288,  48, [608], T+"item.arcticFur",         T+"item.arcticFur",         [bag(1), it(T+"item.arcticFur", 4)]),
 (612, "The Uncrafting Table",    96, -48, [601], T+"tile.TFUncraftingTable", None,                       [bag(1)]),
 (613, "Charm of Keeping",       144, -48, [602], T+"item.charmOfKeeping1",   T+"item.charmOfKeeping1",   [bag(1)]),
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
    NAME = "The Twilight Forest"
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
            "icon:10": it(T + "item.nagaScale"),
            "bg_image:8": "", "bg_size:3": 256,
            "desc:8": "A whole dimension behind a thrown diamond. The bosses are locked in order."}},
        "quests:9": {f"{i}:10": {"sizeX:3": 24, "sizeY:3": 24, "x:3": q[2], "y:3": q[3], "id:3": q[0]}
                     for i, q in enumerate(Q)},
        "lineID:3": key, "order:3": len(ql)}
    print(("APPLIED " if apply else "DRY RUN ") + f"{len(Q)} quests, line {key}")
    for q in Q:
        print(f"  {q[0]}  {q[1]:24} {'checkbox' if q[6] is None else q[6]}")
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
