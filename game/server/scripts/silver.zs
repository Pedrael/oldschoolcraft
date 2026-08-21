// ===========================================================================
//  OldSchoolCraft -- silver.zs
//  "Silver bites the restless dead, and the crawling things besides."
//
//  Thermal Foundation gives us a full silver kit but treats silver as just
//  another mediocre metal. This file gives it a reason to exist: every piece
//  of silver equipment now comes off the crafting grid already enchanted.
//
//    WEAPONS  sword, axe, sickle   Smite III + Bane of Arthropods III
//    ARMOUR   helmet .. boots      Protection II
//    BOW                           Power III
//
//  Smite is vanilla enchantment id 17, Bane of Arthropods is 18. Each level
//  of either adds 2.5 damage -- Smite against the undead (zombies, skeletons,
//  wither skeletons, zombie pigmen, the Wither, and every modded mob flagged
//  UNDEAD), Bane against arthropods (spiders, cave spiders, silverfish,
//  endermites). Level 3 of each is +7.5 damage.
//
//  This is the folklore reading of silver: it harms unnatural things. Against
//  a creeper, a blaze, a ghast or another player it does nothing whatsoever,
//  so silver stays a monster-hunter's specialist kit rather than a strict
//  upgrade over iron or diamond.
//
//  Design note: nothing is taken away. Every recipe costs exactly what it
//  always cost -- same ingots, same sticks, same string. Only the output got
//  better. Presence pays; absence never costs.
//
//  Two things worth knowing:
//
//  * In 1.7.10 an anvil will NOT put Smite or Bane on an axe, because vanilla
//    classifies axes as digging tools. Applying it directly like this
//    bypasses that restriction, so a silver axe is the only monster-slaying
//    axe in the pack. That is deliberate.
//
//  * The bow gets Power III rather than Smite, because Smite has no effect
//    whatsoever on arrows. A tooltip that lies is worse than no tooltip.
//
//  The NBT tags are written inline rather than hoisted into vals -- a bare
//  NBT literal assigned to a val is not a pattern this CraftTweaker build is
//  known to accept, and one bad inference would take the whole file down.
// ===========================================================================

// ------------------------------------------------------------------- SWORD
// Standard sword shape: two ingots over a stick.
recipes.remove(<ThermalFoundation:tool.swordSilver>);
recipes.addShaped(<ThermalFoundation:tool.swordSilver>.withTag({ench: [{id: 17, lvl: 3}, {id: 18, lvl: 3}]}), [
    [<ore:ingotSilver>],
    [<ore:ingotSilver>],
    [<ore:stickWood>]
]);

// --------------------------------------------------------------------- AXE
// Standard axe shape, given in both handedness layouts.
recipes.remove(<ThermalFoundation:tool.axeSilver>);
recipes.addShaped(<ThermalFoundation:tool.axeSilver>.withTag({ench: [{id: 17, lvl: 3}, {id: 18, lvl: 3}]}), [
    [<ore:ingotSilver>, <ore:ingotSilver>],
    [<ore:ingotSilver>, <ore:stickWood>],
    [null,              <ore:stickWood>]
]);
recipes.addShaped(<ThermalFoundation:tool.axeSilver>.withTag({ench: [{id: 17, lvl: 3}, {id: 18, lvl: 3}]}), [
    [<ore:ingotSilver>, <ore:ingotSilver>],
    [<ore:stickWood>,   <ore:ingotSilver>],
    [<ore:stickWood>,   null]
]);

// ------------------------------------------------------------------ SICKLE
// Thermal Foundation's sickle is a sweeping weapon as much as a harvester,
// so it earns the same treatment. Bring it to a dark cave.
recipes.remove(<ThermalFoundation:tool.sickleSilver>);
recipes.addShaped(<ThermalFoundation:tool.sickleSilver>.withTag({ench: [{id: 17, lvl: 3}, {id: 18, lvl: 3}]}), [
    [null,            <ore:ingotSilver>, null],
    [null,            null,              <ore:ingotSilver>],
    [<ore:stickWood>, null,              <ore:ingotSilver>]
]);

// --------------------------------------------------------------------- BOW
// Vanilla bow shape with silver ingots standing in for the sticks.
// Power is enchantment id 48.
recipes.remove(<ThermalFoundation:tool.bowSilver>);
recipes.addShaped(<ThermalFoundation:tool.bowSilver>.withTag({ench: [{id: 48, lvl: 3}]}), [
    [null,              <ore:ingotSilver>, <minecraft:string>],
    [<ore:ingotSilver>, null,              <minecraft:string>],
    [null,              <ore:ingotSilver>, <minecraft:string>]
]);

// ------------------------------------------------------------------ ARMOUR
// Standard armour shapes. Protection is enchantment id 0. Vanilla has no
// undead-specific armour enchantment, so this is plain damage reduction --
// enough that a full silver set is worth wearing on a monster hunt rather
// than just carrying the sword.

recipes.remove(<ThermalFoundation:armor.helmetSilver>);
recipes.addShaped(<ThermalFoundation:armor.helmetSilver>.withTag({ench: [{id: 0, lvl: 2}]}), [
    [<ore:ingotSilver>, <ore:ingotSilver>, <ore:ingotSilver>],
    [<ore:ingotSilver>, null,              <ore:ingotSilver>]
]);

recipes.remove(<ThermalFoundation:armor.plateSilver>);
recipes.addShaped(<ThermalFoundation:armor.plateSilver>.withTag({ench: [{id: 0, lvl: 2}]}), [
    [<ore:ingotSilver>, null,              <ore:ingotSilver>],
    [<ore:ingotSilver>, <ore:ingotSilver>, <ore:ingotSilver>],
    [<ore:ingotSilver>, <ore:ingotSilver>, <ore:ingotSilver>]
]);

recipes.remove(<ThermalFoundation:armor.legsSilver>);
recipes.addShaped(<ThermalFoundation:armor.legsSilver>.withTag({ench: [{id: 0, lvl: 2}]}), [
    [<ore:ingotSilver>, <ore:ingotSilver>, <ore:ingotSilver>],
    [<ore:ingotSilver>, null,              <ore:ingotSilver>],
    [<ore:ingotSilver>, null,              <ore:ingotSilver>]
]);

recipes.remove(<ThermalFoundation:armor.bootsSilver>);
recipes.addShaped(<ThermalFoundation:armor.bootsSilver>.withTag({ench: [{id: 0, lvl: 2}]}), [
    [<ore:ingotSilver>, null,              <ore:ingotSilver>],
    [<ore:ingotSilver>, null,              <ore:ingotSilver>]
]);

// ================================================================ THE BOOKS
//  Pre-enchanted gear gives an immediate payoff. These give agency: spend
//  silver to move the bite onto a weapon you actually care about.
//
//  They use the SAME nine-slot shape as every recipe in eggs.zs, on purpose,
//  so the whole update reads as one idea:
//
//        S  D  S          B = one book, in the centre
//        D  B  D          D = four drops from the thing you want to kill
//        S  D  S          S = four silver ingots
//
//  You bind the essence of the prey into the silver. Rotten flesh teaches
//  the book to hate the dead; spider string teaches it to hate the crawling.
//
//  Enchanted books store their magic under StoredEnchantments, NOT under
//  ench -- that is the difference between a book that works and a book that
//  looks enchanted and does nothing.
//
//  These are a deliberate second market for silver. A diamond sword carrying
//  a silver Smite III book beats a silver sword outright, which is exactly
//  right: silver is the cheap early answer, and later it becomes the
//  currency you spend to upgrade something better.
// ===========================================================================

// Smite III -- bound with rotten flesh.
recipes.addShaped(<minecraft:enchanted_book>.withTag({StoredEnchantments: [{id: 17, lvl: 3}]}), [
    [<ore:ingotSilver>,           <minecraft:rotten_flesh>, <ore:ingotSilver>],
    [<minecraft:rotten_flesh>,    <minecraft:book>,         <minecraft:rotten_flesh>],
    [<ore:ingotSilver>,           <minecraft:rotten_flesh>, <ore:ingotSilver>]
]);

// Bane of Arthropods III -- bound with spider string.
recipes.addShaped(<minecraft:enchanted_book>.withTag({StoredEnchantments: [{id: 18, lvl: 3}]}), [
    [<ore:ingotSilver>,     <minecraft:string>, <ore:ingotSilver>],
    [<minecraft:string>,    <minecraft:book>,   <minecraft:string>],
    [<ore:ingotSilver>,     <minecraft:string>, <ore:ingotSilver>]
]);

// --------------------------------------------------------------- SIGNPOSTS
// Nobody reads changelogs. They do read tooltips.
<ore:ingotSilver>.addTooltip(format.gray("Silver gear is forged already enchanted. Weapons bite the unnatural."));
<ore:ingotSilver>.addTooltip(format.gray("Silver + a book + a creature's drops binds that bite into an enchanted book."));
<ThermalFoundation:tool.swordSilver>.addTooltip(format.gray("Bites the undead and the crawling. Ordinary against all else."));
<ThermalFoundation:tool.axeSilver>.addTooltip(format.gray("Bites the undead and the crawling. Ordinary against all else."));
<ThermalFoundation:tool.sickleSilver>.addTooltip(format.gray("Bites the undead and the crawling. Ordinary against all else."));
<ThermalFoundation:tool.bowSilver>.addTooltip(format.gray("Silver-limbed. Draws harder than it has any right to."));
<ThermalFoundation:armor.helmetSilver>.addTooltip(format.gray("Part of the monster-hunter's kit."));
<ThermalFoundation:armor.plateSilver>.addTooltip(format.gray("Part of the monster-hunter's kit."));
<ThermalFoundation:armor.legsSilver>.addTooltip(format.gray("Part of the monster-hunter's kit."));
<ThermalFoundation:armor.bootsSilver>.addTooltip(format.gray("Part of the monster-hunter's kit."));
