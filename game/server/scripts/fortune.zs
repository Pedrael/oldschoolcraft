// =====================================================================
//  OldSchoolCraft - "FORTUNE"   (world-generated chest loot layer)
// ---------------------------------------------------------------------
//  Design rule for this whole system:
//    a reward you can PREDICT is a paycheck; a reward you cannot predict
//    is a story.  Every table below is built as
//        floor  -> you always leave with something useful
//        step   -> a real upgrade shows up often enough to keep you looking
//        spike  -> a tiny tail that makes people yell in voice chat
//    and wherever possible the prize is a SEALED CONTAINER (loot bag,
//    lockbox, treasure chest, Dice of Fate) so there is a SECOND reveal
//    after the first one.  Two pulls per find, not one.
//
//  Loaded by CraftTweaker.  Reload in-game with  /mt reload  (some
//  entries only take effect on world-gen, i.e. new chunks).
// =====================================================================

// ---- category groups -------------------------------------------------
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

// places you had to fight or delve to reach
val dangerous = [
    "dungeonChest",
    "mineshaftCorridor",
    "strongholdCorridor",
    "strongholdCrossing",
    "pyramidDesertyChest",
    "pyramidJungleChest"
] as string[];

// knowledge places
val scholarly = [
    "strongholdLibrary",
    "villageBlacksmith"
] as string[];

// the deep end only
val deep = [
    "dungeonChest",
    "strongholdCrossing",
    "pyramidJungleChest"
] as string[];


// =====================================================================
//  1. THE FLOOR - never open a chest and feel nothing.
//     Sealed containers first: these are the "pull the lever again" items.
// =====================================================================
for cat in everywhere {
    // Thaumcraft loot bags = a second roll you get to open by hand.
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag> % 30, 1, 3);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag:1> % 12, 1, 2);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag:2> % 3,  1, 1);

    // small guaranteed-feels-good pile
    vanilla.loot.addChestLoot(cat, <minecraft:experience_bottle> % 25, 2, 8);
    vanilla.loot.addChestLoot(cat, <minecraft:emerald> % 15, 1, 4);
    vanilla.loot.addChestLoot(cat, <minecraft:glowstone_dust> % 15, 3, 9);
    vanilla.loot.addChestLoot(cat, <minecraft:quartz> % 15, 3, 9);
    vanilla.loot.addChestLoot(cat, <ThermalFoundation:material:64> % 18, 3, 8);
    vanilla.loot.addChestLoot(cat, <ThermalFoundation:material:65> % 18, 3, 8);
    vanilla.loot.addChestLoot(cat, <TConstruct:materials:16> % 14, 2, 6);
    vanilla.loot.addChestLoot(cat, <Botania:manaResource> % 14, 2, 8);
}


// =====================================================================
//  2. THE STEP - "oh, that's actually an upgrade"
//     Rare enough to matter, common enough to be believed in.
// =====================================================================
for cat in dangerous {
    vanilla.loot.addChestLoot(cat, <Botania:manaResource:1> % 10, 1, 3);   // mana pearl
    vanilla.loot.addChestLoot(cat, <Botania:manaResource:2> % 7,  1, 2);   // mana diamond
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemShard:6> % 10, 1, 3);   // balanced shard
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemNugget:21> % 8, 1, 4);  // cinnabar cluster
    vanilla.loot.addChestLoot(cat, <TConstruct:materials:5> % 6, 1, 3);    // manyullyn
    vanilla.loot.addChestLoot(cat, <TConstruct:materials:6> % 5, 1, 1);    // ball of moss
    vanilla.loot.addChestLoot(cat, <EnderIO:itemAlloy:6> % 9, 2, 6);       // dark steel
    vanilla.loot.addChestLoot(cat, <ExtraUtilities:unstableingot> % 7, 1, 4);
    vanilla.loot.addChestLoot(cat, <Aquaculture:item.loot:16> % 6, 1, 1);  // lockbox (sealed!)
    vanilla.loot.addChestLoot(cat, <Aquaculture:item.loot:17> % 4, 1, 1);  // treasure chest (sealed!)

    // quality-of-life prizes - these change how somebody plays tomorrow
    vanilla.loot.addChestLoot(cat, <EnderIO:itemSoulVessel> % 5, 1, 1);
    vanilla.loot.addChestLoot(cat, <EnderIO:itemMagnet> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:magnetRing> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:manaTablet> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:blackHoleTalisman> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <ExtraUtilities:golden_lasso> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <ExtraUtilities:golden_bag> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <OpenBlocks:luggage> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <xreliquary:fortune_coin> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <xreliquary:hero_medallion> % 2, 1, 1);
}


// =====================================================================
//  3. THE ARCHIVE - libraries & blacksmiths reward curiosity, not combat
// =====================================================================
for cat in scholarly {
    vanilla.loot.addChestLoot(cat, <minecraft:book> % 30, 3, 9);
    vanilla.loot.addChestLoot(cat, <minecraft:paper> % 25, 6, 18);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemResource:15> % 8, 1, 3);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemResource:16> % 5, 1, 2);  // void metal
    vanilla.loot.addChestLoot(cat, <Botania:blackLotus> % 6, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:manaBottle> % 6, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:overgrowthSeed> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemGoggles> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <ThaumicTinkerer:xpTalisman> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <ThaumicTinkerer:placementMirror> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:itemFinder> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:tinyPlanet> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:diviningRod> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <xreliquary:alkahest_tome> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:baubleBox> % 1, 1, 1);
}


// =====================================================================
//  4. THE SPIKE - the tail nobody plans around.
//     Weight 1 against ~250-400 of table weight: you will see one of
//     these maybe once every few hundred chests.  That is the point.
// =====================================================================
for cat in deep {
    vanilla.loot.addChestLoot(cat, <Botania:dice> % 1, 1, 1);              // random Botania relic
    vanilla.loot.addChestLoot(cat, <Botania:manaResource:4> % 1, 1, 4);    // terrasteel
    vanilla.loot.addChestLoot(cat, <Botania:manaRing> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:auraRing> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <xreliquary:witherless_rose> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <xreliquary:phoenix_down> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <xreliquary:void_tear_empty> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <ExtraUtilities:angelBlock> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <minecraft:nether_star> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemEldritchObject:3> % 1, 1, 1);
}


// =====================================================================
//  5. THE BAGS THEMSELVES
//     Everything above hands out Thaumcraft loot bags on purpose, so the
//     bags have to be worth opening.  This is the second reveal.
// =====================================================================

// -- common bag: the pellet. small, frequent, never insulting.
mods.thaumcraft.Loot.addCommonLoot(<minecraft:experience_bottle>, 30);
mods.thaumcraft.Loot.addCommonLoot(<minecraft:emerald>, 20);
mods.thaumcraft.Loot.addCommonLoot(<minecraft:glowstone_dust>, 20);
mods.thaumcraft.Loot.addCommonLoot(<minecraft:quartz>, 20);
mods.thaumcraft.Loot.addCommonLoot(<ThermalFoundation:material:64>, 18);
mods.thaumcraft.Loot.addCommonLoot(<ThermalFoundation:material:65>, 18);
mods.thaumcraft.Loot.addCommonLoot(<TConstruct:materials:16>, 15);
mods.thaumcraft.Loot.addCommonLoot(<TConstruct:materials:8>, 12);
mods.thaumcraft.Loot.addCommonLoot(<Botania:manaResource>, 15);
mods.thaumcraft.Loot.addCommonLoot(<Botania:manaBottle>, 10);
mods.thaumcraft.Loot.addCommonLoot(<EnderIO:itemAlloy:3>, 12);
mods.thaumcraft.Loot.addCommonLoot(<ExtraUtilities:unstableingot>, 8);
mods.thaumcraft.Loot.addCommonLoot(<Aquaculture:item.loot:10>, 8);       // sushi
mods.thaumcraft.Loot.addCommonLoot(<minecraft:golden_carrot>, 8);
mods.thaumcraft.Loot.addCommonLoot(<minecraft:speckled_melon>, 8);
mods.thaumcraft.Loot.addCommonLoot(<MoCreatures:sugarlump>, 6);
// tiny chance the common bag hands you a better bag - bags inside bags
mods.thaumcraft.Loot.addCommonLoot(<Thaumcraft:ItemLootBag:1>, 4);

// -- uncommon bag: the step.
mods.thaumcraft.Loot.addUncommonLoot(<minecraft:diamond>, 20);
mods.thaumcraft.Loot.addUncommonLoot(<minecraft:ender_eye>, 15);
mods.thaumcraft.Loot.addUncommonLoot(<minecraft:blaze_rod>, 15);
mods.thaumcraft.Loot.addUncommonLoot(<minecraft:ghast_tear>, 10);
mods.thaumcraft.Loot.addUncommonLoot(<Botania:manaResource:1>, 15);
mods.thaumcraft.Loot.addUncommonLoot(<Botania:manaResource:2>, 12);
mods.thaumcraft.Loot.addUncommonLoot(<Botania:manaResource:7>, 8);       // elementium
mods.thaumcraft.Loot.addUncommonLoot(<Thaumcraft:ItemResource:16>, 10);  // void metal
mods.thaumcraft.Loot.addUncommonLoot(<Thaumcraft:ItemNugget:21>, 10);
mods.thaumcraft.Loot.addUncommonLoot(<TConstruct:materials:5>, 10);
mods.thaumcraft.Loot.addUncommonLoot(<EnderIO:itemAlloy:6>, 12);
mods.thaumcraft.Loot.addUncommonLoot(<EnderIO:itemSoulVessel>, 6);
mods.thaumcraft.Loot.addUncommonLoot(<Botania:magnetRing>, 5);
mods.thaumcraft.Loot.addUncommonLoot(<Botania:manaTablet>, 5);
mods.thaumcraft.Loot.addUncommonLoot(<ExtraUtilities:golden_lasso>, 5);
mods.thaumcraft.Loot.addUncommonLoot(<Aquaculture:item.loot:16>, 6);     // lockbox
mods.thaumcraft.Loot.addUncommonLoot(<xreliquary:fortune_coin>, 4);
mods.thaumcraft.Loot.addUncommonLoot(<Thaumcraft:ItemLootBag:2>, 3);     // -> rare bag

// -- rare bag: the spike. this one should be remembered.
mods.thaumcraft.Loot.addRareLoot(<Botania:manaResource:4>, 12);          // terrasteel
mods.thaumcraft.Loot.addRareLoot(<Botania:manaResource:9>, 10);          // dragonstone
mods.thaumcraft.Loot.addRareLoot(<Botania:manaResource:14>, 3);          // GAIA INGOT
mods.thaumcraft.Loot.addRareLoot(<Thaumcraft:ItemEldritchObject:3>, 4);  // primordial pearl
mods.thaumcraft.Loot.addRareLoot(<minecraft:nether_star>, 5);
mods.thaumcraft.Loot.addRareLoot(<Botania:dice>, 5);
mods.thaumcraft.Loot.addRareLoot(<Botania:manaRing>, 6);
mods.thaumcraft.Loot.addRareLoot(<Botania:auraRing>, 6);
mods.thaumcraft.Loot.addRareLoot(<Botania:travelBelt>, 6);
mods.thaumcraft.Loot.addRareLoot(<Botania:tinyPlanet>, 6);
mods.thaumcraft.Loot.addRareLoot(<Thaumcraft:ItemGirdleHover>, 4);
mods.thaumcraft.Loot.addRareLoot(<Thaumcraft:ItemAmuletRunic>, 4);
mods.thaumcraft.Loot.addRareLoot(<ThaumicTinkerer:ichorSword>, 3);
mods.thaumcraft.Loot.addRareLoot(<xreliquary:kraken_shell>, 3);
mods.thaumcraft.Loot.addRareLoot(<xreliquary:infernal_tear>, 3);
mods.thaumcraft.Loot.addRareLoot(<xreliquary:phoenix_down>, 3);
mods.thaumcraft.Loot.addRareLoot(<xreliquary:witherless_rose>, 3);
mods.thaumcraft.Loot.addRareLoot(<ExtraUtilities:divisionSigil>, 2);
mods.thaumcraft.Loot.addRareLoot(<Aquaculture:item.loot:18>, 3);         // Neptune's Bounty
mods.thaumcraft.Loot.addRareLoot(<MoCreatures:amuletpegasus>, 3);

// =====================================================================
//  6. THE PLACES THE FIRST PASS MISSED
//     A /mt dump of vanilla.loot.lootTypes showed sixteen live chest
//     categories on this server.  The first five sections only covered
//     eight of them.  These are the other eight, same floor/step/spike
//     shape, themed to where you are actually standing.
// =====================================================================

// -- 6a. THE NETHER --------------------------------------------------
//    Fortress corridor chests.  Vanilla stocks them with saddles, gold
//    horse armour and nether wart.  You cross a lava ocean for that.
val nether = [
    "netherFortress"
] as string[];

for cat in nether {
    // floor
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag> % 25, 1, 3);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag:1> % 12, 1, 2);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag:2> % 4, 1, 1);
    vanilla.loot.addChestLoot(cat, <minecraft:experience_bottle> % 22, 2, 8);
    vanilla.loot.addChestLoot(cat, <minecraft:quartz> % 20, 6, 18);
    vanilla.loot.addChestLoot(cat, <minecraft:glowstone_dust> % 18, 4, 12);
    vanilla.loot.addChestLoot(cat, <minecraft:magma_cream> % 12, 2, 5);

    // step - nether-themed, so it reads as "this place, specifically"
    vanilla.loot.addChestLoot(cat, <minecraft:blaze_rod> % 12, 1, 3);
    vanilla.loot.addChestLoot(cat, <minecraft:ghast_tear> % 8, 1, 2);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemNugget:21> % 9, 1, 4);  // cinnabar
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemShard:6> % 9, 1, 3);    // balanced shard
    vanilla.loot.addChestLoot(cat, <EnderIO:itemAlloy:6> % 9, 2, 6);       // dark steel
    vanilla.loot.addChestLoot(cat, <EnderIO:itemAlloy:7> % 7, 1, 4);       // soularium
    vanilla.loot.addChestLoot(cat, <TConstruct:materials:5> % 6, 1, 3);    // manyullyn
    vanilla.loot.addChestLoot(cat, <Botania:manaResource:1> % 8, 1, 3);    // mana pearl
    vanilla.loot.addChestLoot(cat, <EnderIO:itemSoulVessel> % 5, 1, 1);
    vanilla.loot.addChestLoot(cat, <Aquaculture:item.loot:16> % 4, 1, 1);  // lockbox (sealed!)

    // spike
    vanilla.loot.addChestLoot(cat, <xreliquary:infernal_tear> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <xreliquary:phoenix_down> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemEldritchObject:3> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <minecraft:nether_star> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:dice> % 1, 1, 1);
}


// -- 6b. THE ARCANE TOWER --------------------------------------------
//    Thaumcraft's tower chests (Witching Gadgets writes here too).
//    Magic building, magic payout.
val arcane = [
    "towerChestContents"
] as string[];

for cat in arcane {
    // floor
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag> % 25, 1, 3);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag:1> % 14, 1, 2);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag:2> % 5, 1, 1);
    vanilla.loot.addChestLoot(cat, <minecraft:experience_bottle> % 20, 2, 8);
    vanilla.loot.addChestLoot(cat, <minecraft:paper> % 18, 4, 12);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemShard:6> % 14, 1, 4);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemNugget:21> % 12, 1, 4);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemResource:15> % 10, 1, 3);
    vanilla.loot.addChestLoot(cat, <Botania:manaResource> % 12, 2, 8);

    // step - knowledge tools, the things that change how you play
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemResource:16> % 7, 1, 2);  // void metal
    vanilla.loot.addChestLoot(cat, <Botania:manaResource:1> % 8, 1, 3);
    vanilla.loot.addChestLoot(cat, <Botania:manaBottle> % 7, 1, 2);
    vanilla.loot.addChestLoot(cat, <Botania:blackLotus> % 6, 1, 1);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemGoggles> % 4, 1, 1);
    vanilla.loot.addChestLoot(cat, <ThaumicTinkerer:xpTalisman> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <ThaumicTinkerer:placementMirror> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:itemFinder> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:tinyPlanet> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:baubleBox> % 2, 1, 1);

    // spike
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemAmuletRunic> % 2, 1, 1);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemGirdleHover> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:manaResource:4> % 1, 1, 3);     // terrasteel
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemEldritchObject:3> % 1, 1, 1);
    vanilla.loot.addChestLoot(cat, <Botania:dice> % 1, 1, 1);
}


// -- 6c. SETTLEMENTS -------------------------------------------------
//    IE village crates, Railcraft workshops, Forestry naturalist huts,
//    composting piles, and the world-start bonus chest.  Civilised
//    places: useful, generous, never legendary.  You did not risk
//    anything to open these, so the tail stays short.
val settled = [
    "ieVillageCrates",
    "railcraft:workshop",
    "naturalistChest",
    "composting",
    "bonusChest"
] as string[];

for cat in settled {
    // floor
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag> % 22, 1, 2);
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag:1> % 8, 1, 1);
    vanilla.loot.addChestLoot(cat, <minecraft:experience_bottle> % 20, 1, 5);
    vanilla.loot.addChestLoot(cat, <minecraft:emerald> % 14, 1, 3);
    vanilla.loot.addChestLoot(cat, <ThermalFoundation:material:64> % 15, 2, 6);
    vanilla.loot.addChestLoot(cat, <ThermalFoundation:material:65> % 15, 2, 6);
    vanilla.loot.addChestLoot(cat, <TConstruct:materials:16> % 12, 2, 5);
    vanilla.loot.addChestLoot(cat, <Botania:manaResource> % 12, 2, 6);
    vanilla.loot.addChestLoot(cat, <EnderIO:itemAlloy:3> % 10, 1, 4);
    vanilla.loot.addChestLoot(cat, <minecraft:golden_carrot> % 10, 1, 3);

    // step - small, practical, quality-of-life
    vanilla.loot.addChestLoot(cat, <Botania:manaBottle> % 6, 1, 2);
    vanilla.loot.addChestLoot(cat, <Aquaculture:item.loot:16> % 5, 1, 1);  // lockbox
    vanilla.loot.addChestLoot(cat, <EnderIO:itemMagnet> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <ExtraUtilities:golden_bag> % 3, 1, 1);
    vanilla.loot.addChestLoot(cat, <ExtraUtilities:golden_lasso> % 2, 1, 1);

    // a single thin thread to the top of the system
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag:2> % 1, 1, 1);
}


// -- 6d. THE TRAP ----------------------------------------------------
//    Jungle temple dispensers.  This is the arrow trap.  Whoever
//    disarms it should occasionally find the builders left something.
val trap = [
    "pyramidJungleDispenser"
] as string[];

for cat in trap {
    vanilla.loot.addChestLoot(cat, <Thaumcraft:ItemLootBag> % 4, 1, 1);
    vanilla.loot.addChestLoot(cat, <minecraft:experience_bottle> % 4, 1, 2);
    vanilla.loot.addChestLoot(cat, <minecraft:emerald> % 2, 1, 2);
}


print("[Fortune] chest + loot-bag tables loaded.");
