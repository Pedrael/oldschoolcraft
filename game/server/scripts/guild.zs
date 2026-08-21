// ===========================================================================
//  OldSchoolCraft -- guild.zs
//  Phase 3: interdependence.
//
//  Three additive crafting recipes. Each one turns materials from several
//  DIFFERENT mod trees into a Fortune loot bag (the same bags fortune.zs
//  fills with the variable-reward tables).
//
//  Nothing is removed. Nothing is gated. No recipe that worked yesterday
//  stops working. The only thing these do is give a player who has ONE tree
//  a concrete reason to go find the player who has ANOTHER tree.
//
//  Ladder:
//    Trade Seal   -> common bag    -- 3 trees
//    Guild Seal   -> uncommon bag  -- 5 trees
//    Charter Seal -> rare bag      -- 7 trees
//
//  This file is deliberately SEPARATE from fortune.zs: if any bracket in
//  here ever fails to resolve, only this file dies, not the loot rebuild.
// ===========================================================================

// -- one confirmed component per tree ---------------------------------------
// Tinkers' Construct   steel ingot          TConstruct:materials:16
// Botania              manasteel ingot      Botania:manaResource:0
// Applied Energistics  certus quartz        appliedenergistics2:item.ItemMultiMaterial:0
// Thaumcraft           thaumium ingot       Thaumcraft:ItemResource:2
// Forestry             royal jelly          Forestry:royalJelly
// Blood Magic          reinforced slate     AWWayofTime:reinforcedSlate
// IndustrialCraft 2    advanced circuit     IC2:itemPartCircuitAdv

// ---------------------------------------------------------------- TRADE SEAL
// 3 trees + gold -> 1 COMMON loot bag.
// Cheap on purpose. This is the tier that teaches people the recipes exist.
recipes.addShaped(<Thaumcraft:ItemLootBag>, [
    [<TConstruct:materials:16>, <Botania:manaResource:0>, <appliedenergistics2:item.ItemMultiMaterial:0>],
    [null,                      <minecraft:gold_ingot>,   null],
    [null,                      null,                     null]
]);

// ---------------------------------------------------------------- GUILD SEAL
// 5 trees -> 1 UNCOMMON loot bag.
recipes.addShaped(<Thaumcraft:ItemLootBag:1>, [
    [<TConstruct:materials:16>, <Botania:manaResource:0>, <appliedenergistics2:item.ItemMultiMaterial:0>],
    [<Thaumcraft:ItemResource:2>, <minecraft:gold_block>, <Forestry:royalJelly>],
    [null,                      null,                     null]
]);

// -------------------------------------------------------------- CHARTER SEAL
// 7 trees -> 1 RARE loot bag.
// Realistically nobody on a three-person server holds all seven of these at
// once. That is the entire point.
recipes.addShaped(<Thaumcraft:ItemLootBag:2>, [
    [<TConstruct:materials:16>, <Botania:manaResource:0>, <appliedenergistics2:item.ItemMultiMaterial:0>],
    [<Thaumcraft:ItemResource:2>, <minecraft:diamond_block>, <Forestry:royalJelly>],
    [<AWWayofTime:reinforcedSlate>, <IC2:itemPartCircuitAdv>, <minecraft:ender_eye>]
]);

// ------------------------------------------------------------------ tooltips
<Thaumcraft:ItemLootBag>.addTooltip(format.darkGray("Craftable: 3 mod trees + gold."));
<Thaumcraft:ItemLootBag:1>.addTooltip(format.darkGray("Craftable: 5 mod trees."));
<Thaumcraft:ItemLootBag:2>.addTooltip(format.darkGray("Craftable: 7 mod trees. Ask a friend."));

print("[Guild] cross-tree seal recipes loaded.");
