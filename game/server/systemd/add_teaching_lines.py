#!/usr/bin/env python3
"""Four teaching quest lines: Forestry beekeeping, AgriCraft, Thermal+EnderIO, Tinkers.

The point is that nobody should need a wiki. Each step says what to do, why it
matters, and pays the tool for the NEXT step -- so the usual "I can't start
because I don't have the starter item" wall never appears.

Retrieval tasks use only (id, damage) pairs already proven in this world's quest
database. Anywhere the metadata is ambiguous the task is a checkbox instead:
a quest that cannot be completed is worse than one that self-ticks.

Run with the server STOPPED.
"""
import json, os, shutil, sys, time

DB = "/home/duduserver/minecraft/1.7.10/world/betterquesting/QuestDatabase.json"

def it(i, c=1, d=0): return {"id:8": i, "Count:3": c, "Damage:2": d, "OreDict:8": ""}
def bag(t=0):        return it("Thaumcraft:ItemLootBag", 1, t)

# ---------------------------------------------------------------------------
# (qid, name, x, y, prereqs, icon(id,dmg), task(id,dmg) or None, rewards[], desc)
# ---------------------------------------------------------------------------

BEES = [
 (520,"A Scoop and a Plan",0,0,[],("Forestry:scoop",0),("Forestry:scoop",0),
  [bag(0), it("Forestry:habitatLocator")],
  """Beekeeping is the deepest system in this pack and the one nobody has opened.

Wild hives are in the world — in trees, in the ground, in the desert, in the nether, in snow. §eThey are 2.5x more common than they used to be.§f

You need a §eScoop§f to break one. Anything else destroys it. Break a hive and you get a §eprincess§f and some §edrones§f.

§7Your reward includes a Habitat Locator — it points at the nearest hive biome, which saves a lot of walking.§r"""),

 (521,"Something Royal",48,0,[520],("Forestry:beePrincessGE",0),("Forestry:beePrincessGE",0),
  [bag(0), it("Forestry:apiculture",1,2)],
  """A princess is the entry point to everything else.

One princess plus one drone makes a §equeen§f. The queen works, dies, and leaves behind a new princess and more drones. That loop is the whole mod.

§eA princess drops twice 8% of the time now.§f Two lines running in parallel is far better than double speed, because you can cross them against each other.

§7Reward: an Apiary, so you can start immediately.§r"""),

 (522,"The Apiary",96,0,[521],("Forestry:apiculture",2),("Forestry:apiculture",2),
  [bag(0), it("Forestry:beealyzer")],
  """Put the princess in the top-left slot and a drone beside her.

§eFlowers must be nearby§f — within a few blocks, on grass or dirt. No flowers, no work. This is the single most common reason a new apiary does nothing.

The queen will work through a lifespan and then die, leaving a princess and drones in the output. Take them and put them straight back in.

§7Reward: a Beealyzer, for the next step.§r"""),

 (523,"Know What You're Holding",144,0,[522],("Forestry:beealyzer",0),("Forestry:beealyzer",0),
  [bag(0), it("Forestry:frameUntreated",3)],
  """A bee is not just a species. It carries §especies, speed, lifespan, fertility, tolerance, flowers§f and more — and every one of those is inherited.

Put a bee in the Beealyzer to read them. Unanalysed bees show as "Unknown", which is why your NEI page looks empty.

§7You cannot breed deliberately until you can read what you have. This is the step people skip and then wonder why nothing improves.§r"""),

 (524,"Combs, Wax and Honey",144,-48,[522],("Forestry:beeswax",0),("Forestry:beeswax",0),
  [bag(0)],
  """Combs are the raw output. Almost everything downstream is made from them.

Put combs through a §eCentrifuge§f to get beeswax, honey drops and propolis. Beeswax makes candles, capsules and — importantly — §eframes§f.

§7Honey drops feed back into your own food supply. Bees pay for themselves early.§r"""),

 (525,"Frames Make It Fast",192,-48,[524],("Forestry:frameUntreated",0),("Forestry:frameUntreated",0),
  [bag(0), it("Forestry:frameImpregnated",2)],
  """Three slots on the right of the Apiary take frames.

An §eUntreated Frame§f speeds production and shortens the queen's life. §eImpregnated§f frames last far longer. §eProven§f frames are the good ones.

§7This is the cheapest speed increase in the mod and most people never place one.§r"""),

 (526,"The Card Game Nobody Plays",192,48,[523],("Forestry:core",1),None,
  [bag(1), it("Forestry:frameProven",2)],
  """§7Read and tick. This one is about a block, not an item.§r

The §eEscritoire§f is Forestry's research table, and it is a memory-matching card game you play by hand.

Solving a mutation §epermanently multiplies its chance by 1.5§f and can add up to 5% flat on top. It also produces research notes you can apply directly.

§7LIVING-WORLD.md calls it the single most under-used block in the modpack. It is still true.§r"""),

 (527,"Your First Mutation",240,0,[523],("Forestry:beeQueenGE",0),("Forestry:beeQueenGE",0),
  [bag(1)],
  """Put two §edifferent§f species together and the daughter princess has a percentage chance of being a third species neither parent was.

That is the gamble. Most pairings give you the parents back — §eyou never lose a bee§f, which is why this is safe to grind at.

Common first mutations: Forest + Meadows, Meadows + Modest, Forest + Marshy. Analyse everything and check NEI's bee pages for what leads where.

§7Hidden mutations are deliberately not shown in NEI. Some of this you have to find.§r"""),

 (528,"Where the Tree Grows",240,-48,[527],("Forestry:treealyzer",0),("Forestry:treealyzer",0),
  [bag(0), it("Forestry:grafter")],
  """Trees have genetics exactly like bees do.

A pollinated leaf block can become a §enew species of sapling§f. Bees pollinate leaves. Butterflies pollinate leaves. So an apiary in a forest is quietly rolling tree mutations the whole time you are mining.

Use a §eGrafter§f on any leaf that looks off-colour. Use the Treealyzer to read what you got.

§7Reward: a Grafter. Go look at your leaves.§r"""),

 (529,"Royal Jelly",288,0,[527],("Forestry:royalJelly",0),("Forestry:royalJelly",0),
  [bag(1)],
  """Royal jelly is the first genuinely valuable product, and it is a marker that your line is improving.

It feeds into Forestry's own machines, into Gendustry, and into the §eGreat Grove§f stage of The Great Work.

§7If you are producing jelly reliably, you have left the beginner phase.§r"""),

 (530,"The Alveary",336,0,[529],("Forestry:alveary",0),None,
  [bag(2)],
  """§7Read and tick.§r

The §eAlveary§f is a 3x3x3 multiblock that replaces the Apiary. It is faster, holds more frames, and accepts §eupgrade blocks§f on its walls — heaters, fans, stabilisers, sieves.

It is also the only way to keep some late-game species alive, because they demand climates the overworld will not give you.

§7Built from Alveary blocks made with royal jelly. This is the point where beekeeping becomes infrastructure.§r"""),

 (531,"Industrial Beekeeping",384,0,[530],("gendustry:IndustrialApiary",0),None,
  [bag(2)],
  """§7Read and tick.§r

Gendustry is installed. It automates everything above.

The §eIndustrial Apiary§f takes upgrades and runs on power. The §eMutagen Producer§f, §eGenetic Imprinter§f and §eSampler§f let you read a gene off one bee and §ewrite it onto another§f — which turns breeding from luck into engineering.

§7This is the end of the line and the start of a much bigger one.§r"""),
]

CROPS = [
 (540,"Crop Sticks",0,0,[],("AgriCraft:crops",0),("AgriCraft:crops",0),
  [bag(0), it("AgriCraft:crops",16)],
  """Every plant in this pack can go on §ecrop sticks§f, and once it does it stops being scenery and becomes a stat block.

Four sticks from four wooden sticks. Place them on farmland, then plant a seed into them.

§eWeeds are off on this server.§f Nothing you plant will be strangled while you are offline.

§7Reward: sixteen more sticks. This loop wants volume.§r"""),

 (541,"Three Hidden Numbers",48,0,[540],("AgriCraft:magnifyingGlass",0),("AgriCraft:magnifyingGlass",0),
  [bag(0), it("AgriCraft:seedAnalyzer")],
  """Every crop has three hidden stats, each 1 to 10:

§eGrowth§f — how fast it matures.
§eGain§f — how much it drops.
§eStrength§f — how well it resists and how well it passes traits on.

The §eMagnifying Glass§f reads them off a planted crop. Without it you are breeding blind.

§7Reward: a Seed Analyzer, which reads seeds in your hand instead of in the ground.§r"""),

 (542,"The Analyzer",96,0,[541],("AgriCraft:seedAnalyzer",0),("AgriCraft:seedAnalyzer",0),
  [bag(0)],
  """Place the Seed Analyzer and drop seeds in it.

An unanalysed seed shows nothing. An analysed one shows all three stats permanently, in the tooltip, forever.

§7Analyse before you plant. Planting an unknown seed into a good line is how you quietly ruin it.§r"""),

 (543,"The Cross-Crop",144,0,[542],("AgriCraft:crops",0),None,
  [bag(0)],
  """§7Read and tick.§r

Put crop sticks on a plot, then put §ea second set of sticks on the same block§f. That is a cross-crop — it looks like a taller lattice.

Surround it with mature crops. Over time the cross-crop will produce §ea new plant§f, inheriting stats from its neighbours — often better than any of them.

§eThe standard layout is four plants around one cross-crop, in a plus shape.§f"""),

 (544,"Better Than Its Parents",192,0,[543],("AgriCraft:seedFerranium",0),None,
  [bag(1)],
  """§7Read and tick.§r

A cross-crop does one of three things: nothing, a copy of a neighbour, or §ea mutation into a different plant entirely§f.

§eThe mutation rate on this server was raised from 0.2 to 0.3§f — a 50% increase over stock.

Stats climb the same way. Cross two 5/5/5 plants enough times and you will see a 6. Keep the best, replant, repeat. That is the whole game.

§7You cannot lose. A failed cross gives you the crop back.§r"""),

 (545,"Careful Hands",144,48,[542],("AgriCraft:trowel",0),("AgriCraft:trowel",0),
  [bag(0), it("AgriCraft:clipper")],
  """Breaking a good crop by hand risks losing it.

The §eTrowel§f picks up a planted crop with its stats intact and lets you put it somewhere else. This is how you move a good line without gambling it.

§7Reward: a Clipper, which takes a cutting from a mature plant without destroying it — free copies of something good.§r"""),

 (546,"Water It",192,48,[545],("AgriCraft:channelValve",0),None,
  [bag(0)],
  """§7Read and tick.§r

AgriCraft has its own irrigation: §etanks, channels and sprinklers§f. A sprinkler over your plot raises growth rate across everything under it.

Channels carry water from a tank; a valve lets you control the flow. It is entirely optional and it roughly doubles your throughput.

§7Build it once and never think about it again.§r"""),

 (547,"Ore, But Vegetable",240,0,[544],("AgriCraft:seedFerranium",0),("AgriCraft:seedFerranium",0),
  [bag(2)],
  """There are plants on this server that grow §eore§f.

Iron, gold, diamond, redstone, certus, and more. They sit deep in the mutation tree, they start at terrible stats, and a maxed-out resource farm is one of the genuinely impressive things you can build here.

§7Getting one seed is the hard part. After that it is just patience and cross-crops.§r"""),
]

POWER = [
 (560,"Power Is a Resource",0,0,[],("ThermalExpansion:Dynamo",0),None,
  [bag(0)],
  """§7Read and tick.§r

Thermal Expansion and EnderIO both run on §eRF§f — Redstone Flux. They speak the same power, so you can mix them freely.

Three things matter: §emake it§f (dynamos, generators), §emove it§f (ducts, conduits), §estore it§f (cells, capacitor banks).

Everything below is one of those three."""),

 (561,"Your First Dynamo",48,0,[560],("ThermalExpansion:Dynamo",0),None,
  [bag(0)],
  """§7Read and tick.§r

A §eSteam Dynamo§f burns fuel and water. A §eMagmatic Dynamo§f drinks lava and is the one most people settle on early — lava is effectively free once you can reach it.

Dynamos push power out of their §eflat face§f. Point that at the thing you want to run, or at a duct.

§7A dynamo with nowhere to send power will simply stop. That is not a bug.§r"""),

 (562,"The Pulverizer",96,0,[561],("ThermalExpansion:Machine",1),("ThermalExpansion:Machine",1),
  [bag(0)],
  """The §ePulverizer§f turns one ore into §etwo dust§f, and dust smelts into ingots.

That is a straight doubling of every ore you mine, and it pays for itself within an hour. It is the first machine anyone should build.

§7It also has a chance of a bonus secondary output — nickel from iron, gold from copper, and so on.§r"""),

 (563,"The Induction Smelter",144,0,[562],("ThermalExpansion:Machine",3),("ThermalExpansion:Machine",3),
  [bag(1)],
  """The §eInduction Smelter§f combines two inputs into an alloy — and it is how you make §eelectrum, invar, bronze and signalum§f.

Ore plus sand also gives you §emore ingots than smelting§f, which stacks with the Pulverizer for a serious yield increase.

§7Invar and electrum both matter for the armour jobs in Dressing for the Weather.§r"""),

 (564,"Moving Power",96,48,[561],("ThermalDynamics:ThermalDynamics_0",0),None,
  [bag(0)],
  """§7Read and tick.§r

Thermal Dynamics §eEnergy Ducts§f carry RF. Fluiducts carry liquids. Itemducts carry items.

Ducts connect automatically. A §eServo§f on the end of an itemduct pulls items out of a machine; a §eFilter§f decides which ones.

§7This is where a pile of machines becomes a factory.§r"""),

 (565,"Storing Power",144,48,[564],("ThermalExpansion:Cell",0),None,
  [bag(0)],
  """§7Read and tick.§r

An §eEnergy Cell§f is a buffer. Fill it while you are away, drain it when you need a burst.

Its faces are configurable — set input on one side and output on another, or it will happily do nothing.

§7A buffer between your generators and your machines means a machine never stalls mid-job.§r"""),

 (566,"The SAG Mill",192,0,[563],("EnderIO:blockSagMill",0),("EnderIO:blockSagMill",0),
  [bag(1)],
  """EnderIO's answer to the Pulverizer, and it does something the Pulverizer cannot: it takes §egrinding balls§f.

A grinding ball raises output, adds bonus chance, or lowers power use depending on which one you load. §eDark steel balls§f are the usual pick.

§7Running both a Pulverizer and a SAG Mill is normal. They are good at different ores.§r"""),

 (567,"The Alloy Smelter",240,0,[566],("EnderIO:blockAlloySmelter",0),("EnderIO:blockAlloySmelter",0),
  [bag(1)],
  """The §eAlloy Smelter§f makes EnderIO's own materials — §eelectrical steel, redstone alloy, conductive iron, dark steel§f.

Dark steel is the one to aim for. It makes the best armour in the mod, the grinding balls above, and the Dark Steel Pickaxe.

§7It has three modes. Leave it on Alloying unless you know why you are changing it.§r"""),

 (568,"Conduits Do Everything",192,48,[567],("EnderIO:itemPowerConduit",0),None,
  [bag(1)],
  """§7Read and tick.§r

EnderIO conduits are the reason people run EnderIO. §ePower, fluid, item and redstone conduits all occupy the same block space§f, so one line carries everything.

Hide them inside a §eConduit Facade§f and your base stops looking like a server room.

§7Item conduits have filters and round-robin built in. No servos needed.§r"""),

 (569,"Capacitor Banks",240,48,[568],("EnderIO:blockCapBank",0),None,
  [bag(2)],
  """§7Read and tick.§r

A §eCapacitor Bank§f is EnderIO's storage, and unlike an Energy Cell it §etiles§f — place them adjacent and they merge into one larger bank with a shared display.

Wall of them, one input face, one output face, done.

§7At this point you have generation, transport, storage and processing. That is the whole tech spine.§r"""),
]

TOOLS = [
 (580,"Patterns First",0,0,[],("TConstruct:blankPattern",0),("TConstruct:blankPattern",0),
  [bag(0), it("TConstruct:ToolStationBlock",1,0)],
  """Tinkers' tools are §eassembled from parts§f, and every part starts as a pattern.

A §eBlank Pattern§f is four planks and two sticks. Put it in a §ePattern Chest§f or a Stencil Table and carve it into the shape you want — pickaxe head, tool rod, binding.

§7Reward: a Tool Station, which is where everything below happens.§r"""),

 (581,"The Tool Station",48,0,[580],("TConstruct:ToolStationBlock",0),("TConstruct:ToolStationBlock",0),
  [bag(0)],
  """The §eTool Station§f shows you every tool you can build and exactly which parts it needs.

Click a tool on the left and it tells you what is missing. §eThis is the in-game manual — you do not need a wiki for recipes.§f

§7There is also a book. It is genuinely good and most people never open it.§r"""),

 (582,"Your First Pickaxe",96,0,[581],("TConstruct:pickaxeHead",2),("TConstruct:pickaxeHead",2),
  [bag(0)],
  """Three parts: §epickaxe head, tool rod, binding§f.

Each part can be a different material, and §eeach material brings its own trait§f. The head decides mining speed and harvest level. The rod decides durability and handling. The binding modifies both.

§7Stone head, wooden rod is the normal start. It is deliberately not much better than vanilla — the point is what happens next.§r"""),

 (583,"Tools That Level Up",144,0,[582],("TConstruct:materials",2),None,
  [bag(1)],
  """§7Read this one carefully — it is the part wikis get wrong for this server.§r

§eIguanaTweaks is installed.§f That changes stock Tinkers rules significantly:

Tools §egain XP as you use them§f and level up. Each level grants a free modifier. A tool you have used for a week is genuinely better than the same tool built fresh.

§eHarvest level is gated by material§f, and mining a block above your level is slower rather than impossible.

§7Do not throw away a levelled tool. Repair it.§r"""),

 (584,"Modifiers",192,0,[583],("TConstruct:materials",16),None,
  [bag(1)],
  """§7Read and tick.§r

Put a tool plus a material in the Tool Station and it takes a §emodifier§f:

§eRedstone§f — speed. §eQuartz§f — attack. §eLapis§f — luck, which is Fortune and Looting.
§eMoss§f — self-repair. §eObsidian, Diamond, Emerald§f — durability and level cap.

§7A Ball of Moss on a mining tool means you effectively never repair it again. It is the best modifier in the mod.§r"""),

 (585,"Lapis Means Looting",240,0,[584],("TConstruct:materials",16),None,
  [bag(1)],
  """§7Read and tick. This one has a number attached.§r

Luck on a Tinkers weapon is Looting. And on this server §eLooting is the entire trophy mechanism§f.

No Looting: about §e1 in 2000§f. Looting I: §e1 in 222§f. Looting II: §e1 in 118§f. Looting III: §e1 in 80§f.

§7Grinding without Looting is forty times slower than Looting without grinding. Put lapis on the sword.§r"""),

 (586,"The Smeltery",144,48,[583],("TConstruct:Smeltery",0),("TConstruct:Smeltery",0),
  [bag(1), it("TConstruct:SearedBlock",4,0)],
  """The §eSmeltery§f is a multiblock that melts ore into liquid metal — and it gives §etwo ingots per ore§f, same as a Pulverizer, plus it can alloy.

You need: a Controller, a base of Seared Bricks, walls, a §eSmeltery Drain§f, and a Tank with lava.

§7Build the base one layer, walls two or three high, controller in the wall. It tells you when it is valid.§r"""),

 (587,"Seared Bricks",192,48,[586],("TConstruct:SearedBlock",0),("TConstruct:SearedBlock",0),
  [bag(0), it("TConstruct:LavaTank",2,0)],
  """Grout — clay, sand and gravel — smelted into §eSeared Brick§f. That is the whole smeltery, and it is dirt cheap.

Build it bigger than you think you need. Expanding later means taking the walls apart.

§7Reward: two Lava Tanks. Lava is the fuel; a tank holds it.§r"""),

 (588,"Casting",240,48,[587],("TConstruct:Smeltery",2),None,
  [bag(1)],
  """§7Read and tick.§r

Liquid metal comes out of the Drain and into a §eCasting Table§f or §eCasting Basin§f.

Put a pattern on the table and pour metal on it to cast a §etool part§f. Put nothing on it and pour to cast an ingot. The basin makes blocks.

§7This is how you make parts out of metals you cannot craft by hand — and how alloys like manyullyn happen.§r"""),

 (589,"The Tool Forge",288,0,[585],("TConstruct:ToolForgeBlock",0),None,
  [bag(2)],
  """§7Read and tick.§r

The §eTool Forge§f is the Tool Station's big brother. It builds the tools the Station cannot: §ehammers, excavators, lumber axes, cleavers, battleaxes§f.

Those are the 3x3 mining tools. One of them plus a Ball of Moss and a levelled harvest level is the last mining tool you will ever build.

§7Built on a base of metal blocks. Which metal does not matter.§r"""),
]

LINES = [
 ("Forestry: Bees and Trees", "Bees are a long game. This is the short path into it.", ("Forestry:beePrincessGE",0), BEES),
 ("AgriCraft: Crops With Stats", "Every plant here is a stat block. Here is how to read and improve one.", ("AgriCraft:crops",0), CROPS),
 ("Power and Automation", "Make it, move it, store it, then let it run without you.", ("ThermalExpansion:Machine",1), POWER),
 ("Tinkers': Tools That Level", "Assembled, modified, and levelled. IguanaTweaks changes the rules.", ("TConstruct:ToolStationBlock",0), TOOLS),
]


def build_quest(qid, name, x, y, prereqs, icon, task, rewards, desc):
    tasks = ({"0:10": {"index:3": 0, "taskID:8": "bq_standard:checkbox"}} if task is None
             else {"0:10": {"partialMatch:1": 1, "autoConsume:1": 0, "groupDetect:1": 0,
                            "ignoreNBT:1": 1, "index:3": 0, "consume:1": 0,
                            "requiredItems:9": {"0:10": it(task[0], 1, task[1])},
                            "taskID:8": "bq_standard:retrieval"}})
    return {"questID:3": qid, "preRequisites:11": prereqs,
            "properties:10": {"betterquesting:10": {
                "snd_complete:8": "minecraft:entity.player.levelup",
                "snd_update:8": "minecraft:entity.player.levelup",
                "taskLogic:8": "AND", "visibility:8": "NORMAL",
                "isMain:1": 0, "simultaneous:1": 0,
                "icon:10": it(icon[0], 1, icon[1]),
                "repeatTime:3": -1, "globalShare:1": 0, "questLogic:8": "AND",
                "repeat_relative:1": 1, "name:8": name,
                "lockedProgress:1": 0, "autoClaim:1": 0, "isSilent:1": 0,
                "desc:8": desc}},
            "tasks:9": tasks,
            "rewards:9": {"0:10": {"rewardID:8": "bq_standard:item", "index:3": 0,
                                   "rewards:9": {f"{i}:10": r for i, r in enumerate(rewards)}},
                          "1:10": {"rewardID:8": "bq_standard:xp", "index:3": 1,
                                   "amount:3": 150, "isLevels:1": 0}}}


def main():
    apply = "--apply" in sys.argv
    d = json.load(open(DB, encoding="utf-8"))
    qdb, ql = d["questDatabase:9"], d["questLines:9"]
    have_ids = {q["questID:3"] for q in qdb.values()}
    have_names = {v["properties:10"]["betterquesting:10"].get("name:8") for v in ql.values()}

    total = 0
    next_line = max(int(k.split(":")[0]) for k in ql) + 1
    for lname, ldesc, licon, quests in LINES:
        if lname in have_names:
            print(f"SKIP (already present): {lname}"); continue
        clash = have_ids & {q[0] for q in quests}
        if clash:
            print(f"SKIP {lname}: quest IDs already used {sorted(clash)}"); continue
        for q in quests:
            qdb[f"{q[0]}:10"] = build_quest(*q)
        ql[f"{next_line}:10"] = {
            "properties:10": {"betterquesting:10": {
                "visibility:8": "NORMAL", "name:8": lname,
                "icon:10": it(licon[0], 1, licon[1]),
                "bg_image:8": "", "bg_size:3": 256, "desc:8": ldesc}},
            "quests:9": {f"{i}:10": {"sizeX:3": 24, "sizeY:3": 24,
                                     "x:3": q[2], "y:3": q[3], "id:3": q[0]}
                         for i, q in enumerate(quests)},
            "lineID:3": next_line, "order:3": len(ql)}
        print(f"  + {lname:32} {len(quests)} quests  (line {next_line})")
        total += len(quests); next_line += 1

    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {total} quests across "
          f"{len([l for l in LINES if l[0] not in have_names])} lines")
    if apply and total:
        bak = DB + f".bak-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(DB, bak)
        json.dump(d, open(DB, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"backup: {bak}\nwritten: {os.path.getsize(DB)} bytes")


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
