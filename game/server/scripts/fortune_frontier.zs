// =====================================================================
//  OldSchoolCraft - "FORTUNE: FRONTIER"
//  Section 7 of the loot system. fortune.zs was written before Twilight
//  Forest, Modular Powersuits and Special Mobs arrived on 2026-08-18, so
//  none of the three appeared in a single loot table anywhere on the
//  server. This is that gap.
// ---------------------------------------------------------------------
//  Same rule as fortune.zs: floor -> step -> spike, and prefer a sealed
//  container so there are two reveals instead of one.
//
//  ONE IMPORTANT LIMIT: Twilight Forest does NOT use vanilla ChestGenHooks.
//  It has its own hardcoded TFTreasure/TFTreasureTable, which MineTweaker
//  cannot reach. We cannot change what is inside a TF chest. What we CAN
//  do is the opposite trick - put TF items into OVERWORLD chests, so the
//  dimension advertises itself. You find a Live Root in a mineshaft and
//  have no idea what it is; that is the hook.
//
//  Deliberately NOT here: fiery/knightly/yeti/arctic/phantom gear, naga
//  scales, scepters, the boss bows, glass sword, mazebreaker, cube of
//  annihilation. Those are the REASON to go to Twilight Forest. Handing
//  them out in an overworld dungeon would cheapen the whole dimension.
// =====================================================================

val everywhere = [
    "dungeonChest",
    "mineshaftCorridor",
    "strongholdCorridor",
    "strongholdCrossing",
    "strongholdLibrary",
    "pyramidDesertyChest",
    "pyramidJungleChest",
    "villageBlacksmith"
] as string[];

val dangerous = [
    "dungeonChest",
    "mineshaftCorridor",
    "strongholdCorridor",
    "strongholdCrossing",
    "pyramidDesertyChest",
    "pyramidJungleChest"
] as string[];

val deep = [
    "dungeonChest",
    "strongholdCrossing",
    "pyramidJungleChest"
] as string[];

val scholarly = [
    "strongholdLibrary",
    "villageBlacksmith",
    "towerChestContents"
] as string[];


// =====================================================================
//  7a. THE RUMOUR - Twilight Forest leaks into the Overworld
//      Floor: things that are merely strange. You cannot use most of
//      this yet, and that is the entire point.
// =====================================================================
for cat in everywhere {
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.liveRoot> % 14, 1, 3);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.torchberries> % 12, 2, 6);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.ironwoodRaw> % 10, 1, 3);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.magicBeans> % 6, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.experiment115> % 8, 1, 4);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.meefSteak> % 8, 1, 3);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.venisonCooked> % 8, 1, 3);
}

// Step: the tools that make somebody actually GO. A charm of keeping is
// the single most persuasive item in the mod given how this server dies.
for cat in dangerous {
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.charmOfKeeping1> % 6, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.charmOfLife1> % 5, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.oreMeter> % 4, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.moonwormQueen> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.transformPowder> % 5, 1, 3);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.steeleafIngot> % 5, 1, 3);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.knightMetal> % 4, 1, 3);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.armorShards> % 6, 1, 4);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.ironwoodIngot> % 6, 1, 3);
}

// The maps are blank until you are in the Twilight Forest, so they read
// as an invitation rather than a prize. Libraries are where they belong.
for cat in scholarly {
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.emptyMagicMap> % 7, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.emptyMazeMap> % 6, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.emptyOreMap> % 6, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.magicMapFocus> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.mazeMapFocus> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.borerEssence> % 4, 1, 2);
}

// Spike: still not boss gear. Utility that is genuinely hard to get.
for cat in deep {
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.charmOfKeeping2> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.charmOfLife2> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.cubeTalisman> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.crumbleHorn> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.oreMagnet> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.peacockFan> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.fieryIngot> % 1, 1, 2);
    vanilla.loot.addChestLoot(cat, <TwilightForest:item.carminite> % 1, 1, 2);
}


// =====================================================================
//  7b. THE MACHINE - Modular Powersuits
//      "The Suit" is a 14-quest chapter with no loot pathway at all: the
//      only way to meet the mod was to already know it existed. A Tinker
//      Table in a dungeon chest is a much better introduction than a
//      quest description.
//
//      Only metadata-free items are used here. powerArmorComponent is a
//      subtyped item and the meta order could not be verified offline;
//      per CLAUDE.md a guessed Damage value is not worth shipping.
// =====================================================================

// Floor: a Lux Capacitor is a light source with a story attached.
for cat in dangerous {
    vanilla.loot.addChestLoot(cat, <powersuits:tile.luxCapacitor> % 8, 1, 3);
}

// Step: the table IS the invitation. Finding one means you can begin.
for cat in dangerous {
    vanilla.loot.addChestLoot(cat, <powersuits:tile.tinkerTable> % 3, 1, 1);
}

// Spike: a single piece of the suit, never a set. One boot is a mystery;
// a full set is a handout.
for cat in deep {
    vanilla.loot.addChestLoot(cat, <powersuits:item.powerArmorBoots> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <powersuits:item.powerArmorHelmet> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <powersuits:item.powerFist> % 1, 1, 1);
}


// =====================================================================
//  7c. THE BAGS - the second reveal has to know about these mods too
// =====================================================================

// common: strange, cheap, no idea what it does
mods.thaumcraft.Loot.addCommonLoot(<TwilightForest:item.torchberries>, 12);
mods.thaumcraft.Loot.addCommonLoot(<TwilightForest:item.liveRoot>, 10);
mods.thaumcraft.Loot.addCommonLoot(<TwilightForest:item.ironwoodRaw>, 8);
mods.thaumcraft.Loot.addCommonLoot(<TwilightForest:item.experiment115>, 8);
mods.thaumcraft.Loot.addCommonLoot(<TwilightForest:item.meefSteak>, 6);
mods.thaumcraft.Loot.addCommonLoot(<powersuits:tile.luxCapacitor>, 6);

// uncommon: now it is worth something
mods.thaumcraft.Loot.addUncommonLoot(<TwilightForest:item.charmOfKeeping1>, 8);
mods.thaumcraft.Loot.addUncommonLoot(<TwilightForest:item.charmOfLife1>, 6);
mods.thaumcraft.Loot.addUncommonLoot(<TwilightForest:item.steeleafIngot>, 8);
mods.thaumcraft.Loot.addUncommonLoot(<TwilightForest:item.knightMetal>, 6);
mods.thaumcraft.Loot.addUncommonLoot(<TwilightForest:item.armorShards>, 8);
mods.thaumcraft.Loot.addUncommonLoot(<TwilightForest:item.emptyMagicMap>, 6);
mods.thaumcraft.Loot.addUncommonLoot(<TwilightForest:item.oreMeter>, 5);
mods.thaumcraft.Loot.addUncommonLoot(<powersuits:tile.tinkerTable>, 4);

// rare: remembered
mods.thaumcraft.Loot.addRareLoot(<TwilightForest:item.charmOfKeeping3>, 4);
mods.thaumcraft.Loot.addRareLoot(<TwilightForest:item.charmOfLife2>, 4);
mods.thaumcraft.Loot.addRareLoot(<TwilightForest:item.fieryIngot>, 5);
mods.thaumcraft.Loot.addRareLoot(<TwilightForest:item.carminite>, 4);
mods.thaumcraft.Loot.addRareLoot(<TwilightForest:item.cubeTalisman>, 3);
mods.thaumcraft.Loot.addRareLoot(<TwilightForest:item.crumbleHorn>, 3);
mods.thaumcraft.Loot.addRareLoot(<TwilightForest:item.oreMagnet>, 3);
mods.thaumcraft.Loot.addRareLoot(<powersuits:item.powerArmorBoots>, 3);
mods.thaumcraft.Loot.addRareLoot(<powersuits:item.powerArmorHelmet>, 3);
mods.thaumcraft.Loot.addRareLoot(<powersuits:item.powerFist>, 2);

print("[Fortune:Frontier] Twilight Forest + Modular Powersuits loot loaded.");


// =====================================================================
//  7d. THE MACHINE AGE - Mekanism
//      Added 2026-08-22. Mekanism's ore multiplication is disabled, so
//      nothing here is an ore shortcut: it is components, utilities and
//      the wearables, which is the part of the mod worth finding.
//
//      Metadata-free items only. Ingot, ControlCircuit, EnergyCube and
//      Balloon are all subtyped and their meta order was not verified,
//      and a wrong Damage value is not worth shipping.
// =====================================================================

// floor: unfamiliar industrial oddments
for cat in everywhere {
    vanilla.loot.addChestLoot(cat, <Mekanism:Salt> % 14, 2, 6);
    vanilla.loot.addChestLoot(cat, <Mekanism:Sawdust> % 12, 2, 8);
    vanilla.loot.addChestLoot(cat, <Mekanism:BioFuel> % 12, 3, 9);
    vanilla.loot.addChestLoot(cat, <Mekanism:CompressedRedstone> % 8, 1, 3);
    vanilla.loot.addChestLoot(cat, <Mekanism:CompressedCarbon> % 8, 1, 3);
    vanilla.loot.addChestLoot(cat, <Mekanism:Substrate> % 8, 1, 4);
}

// step: the components that actually unlock the machines
for cat in dangerous {
    vanilla.loot.addChestLoot(cat, <Mekanism:EnrichedIron> % 10, 2, 6);
    vanilla.loot.addChestLoot(cat, <Mekanism:EnrichedAlloy> % 7, 1, 4);
    vanilla.loot.addChestLoot(cat, <Mekanism:ReinforcedAlloy> % 4, 1, 2);
    vanilla.loot.addChestLoot(cat, <Mekanism:EnergyTablet> % 5, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:ElectrolyticCore> % 5, 1, 2);
    vanilla.loot.addChestLoot(cat, <Mekanism:Polyethene> % 6, 1, 4);
    // utilities - these change how somebody plays tomorrow
    vanilla.loot.addChestLoot(cat, <Mekanism:Configurator> % 4, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:Dictionary> % 4, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:NetworkReader> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:SeismicReader> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:CardboardBox> % 4, 1, 2);
    vanilla.loot.addChestLoot(cat, <Mekanism:WalkieTalkie> % 2, 1, 1);
}

// the mask is a genuine survival find here - EnviroMine tracks air, and
// this is one of the few things that seals it completely.
for cat in dangerous {
    vanilla.loot.addChestLoot(cat, <Mekanism:GasMask> % 4, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:FreeRunners> % 3, 1, 1);
}

// scholarly places: the reference tools
for cat in scholarly {
    vanilla.loot.addChestLoot(cat, <Mekanism:Dictionary> % 5, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:ConfigurationCard> % 4, 1, 2);
    vanilla.loot.addChestLoot(cat, <Mekanism:CraftingFormula> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:GaugeDropper> % 3, 1, 1);
}

// spike: remembered
for cat in deep {
    vanilla.loot.addChestLoot(cat, <Mekanism:ScubaTank> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:Jetpack> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:ArmoredJetpack> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:AtomicDisassembler> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:AtomicAlloy> % 2, 1, 2);
    vanilla.loot.addChestLoot(cat, <Mekanism:TeleportationCore> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:PortableTeleporter> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:Robit> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Mekanism:ElectricBow> % 1, 1, 1);
}

// bags
mods.thaumcraft.Loot.addCommonLoot(<Mekanism:Salt>, 12);
mods.thaumcraft.Loot.addCommonLoot(<Mekanism:BioFuel>, 10);
mods.thaumcraft.Loot.addCommonLoot(<Mekanism:CompressedRedstone>, 8);
mods.thaumcraft.Loot.addUncommonLoot(<Mekanism:EnrichedAlloy>, 8);
mods.thaumcraft.Loot.addUncommonLoot(<Mekanism:Configurator>, 5);
mods.thaumcraft.Loot.addUncommonLoot(<Mekanism:CardboardBox>, 5);
mods.thaumcraft.Loot.addUncommonLoot(<Mekanism:GasMask>, 5);
mods.thaumcraft.Loot.addRareLoot(<Mekanism:ScubaTank>, 4);
mods.thaumcraft.Loot.addRareLoot(<Mekanism:Jetpack>, 3);
mods.thaumcraft.Loot.addRareLoot(<Mekanism:AtomicDisassembler>, 2);
mods.thaumcraft.Loot.addRareLoot(<Mekanism:Robit>, 2);
mods.thaumcraft.Loot.addRareLoot(<Mekanism:PortableTeleporter>, 2);

print("[Fortune:Frontier] Mekanism loot loaded.");
