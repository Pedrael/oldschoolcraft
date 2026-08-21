// ===========================================================================
//  OldSchoolCraft -- eggs.zs
//  "You must have met one to make one."
//
//  Spawn eggs are normally creative-only. This file makes them earnable.
//
//  Every egg uses the SAME nine-slot shape, so once you have seen one recipe
//  you can guess all the others:
//
//        B  S  B          E = one ordinary chicken egg (the vessel)
//        S  E  S          S = four of the creature's own signature drop
//        B  S  B          B = four binder ingots
//
//  The signature drop is the honest part: you cannot make a creature you
//  have never hunted, farmed or traded with. The binder sets the price.
//
//        gold nugget  ->  livestock you could already breed
//        gold ingot   ->  wild animals that are a pain to find
//        SILVER       ->  hostile mobs. Silver binds the restless.
//        diamond      ->  villagers
//
//  Nothing here is removed and nothing is gated behind a mod you do not
//  play. Every recipe is purely additive.
//
//  Worth saying out loud: this is NOT the only way to move creatures around.
//  It is the cheapest and dumbest way. The pack already contains three
//  better ones, and they are all more interesting than a crafting grid:
//
//    * EnderIO Soul Vial   - right-click any living mob, villagers included,
//                            and it goes in the bottle. Release it later and
//                            it is the SAME animal: same name, same trades,
//                            same everything. Reusable forever.
//    * Containment Focus   - Thaumic Horizons wand focus. Same idea, but the
//                            creature ends up in a Warded Jar you can carry.
//    * Incarnation         - Thaumic Horizons research. Draw blood from any
//                            creature with a Warded Syringe, feed the sample
//                            to a Curative Vat with four Victus and a
//                            Nutrient Mix, and it grows you a clone.
//                            Human souls cannot be copied. Everything else
//                            is fair game.
// ===========================================================================

val vessel = <minecraft:egg>;

val bindLivestock = <minecraft:gold_nugget>;
val bindWild      = <minecraft:gold_ingot>;
val bindHostile   = <ore:ingotSilver>;
val bindVillager  = <minecraft:diamond>;

// ==================================================================== TIER 1
//  Livestock. Cheap on purpose -- this tier exists to teach the shape.
// ===========================================================================

// Pig -- raw porkchop
recipes.addShaped(<minecraft:spawn_egg:90>, [
    [bindLivestock,          <minecraft:porkchop>, bindLivestock],
    [<minecraft:porkchop>,   vessel,               <minecraft:porkchop>],
    [bindLivestock,          <minecraft:porkchop>, bindLivestock]
]);

// Sheep -- wool of any colour
recipes.addShaped(<minecraft:spawn_egg:91>, [
    [bindLivestock,        <minecraft:wool:*>, bindLivestock],
    [<minecraft:wool:*>,   vessel,             <minecraft:wool:*>],
    [bindLivestock,        <minecraft:wool:*>, bindLivestock]
]);

// Cow -- leather
recipes.addShaped(<minecraft:spawn_egg:92>, [
    [bindLivestock,        <minecraft:leather>, bindLivestock],
    [<minecraft:leather>,  vessel,              <minecraft:leather>],
    [bindLivestock,        <minecraft:leather>, bindLivestock]
]);

// Chicken -- feather
recipes.addShaped(<minecraft:spawn_egg:93>, [
    [bindLivestock,        <minecraft:feather>, bindLivestock],
    [<minecraft:feather>,  vessel,              <minecraft:feather>],
    [bindLivestock,        <minecraft:feather>, bindLivestock]
]);

// ==================================================================== TIER 2
//  Wild animals. Findable, but nobody enjoys looking for them.
// ===========================================================================

// Squid -- ink sac
recipes.addShaped(<minecraft:spawn_egg:94>, [
    [bindWild,             <minecraft:dye:0>, bindWild],
    [<minecraft:dye:0>,    vessel,            <minecraft:dye:0>],
    [bindWild,             <minecraft:dye:0>, bindWild]
]);

// Wolf -- bone
recipes.addShaped(<minecraft:spawn_egg:95>, [
    [bindWild,           <minecraft:bone>, bindWild],
    [<minecraft:bone>,   vessel,           <minecraft:bone>],
    [bindWild,           <minecraft:bone>, bindWild]
]);

// Mooshroom -- red mushroom
recipes.addShaped(<minecraft:spawn_egg:96>, [
    [bindWild,                    <minecraft:red_mushroom>, bindWild],
    [<minecraft:red_mushroom>,    vessel,                   <minecraft:red_mushroom>],
    [bindWild,                    <minecraft:red_mushroom>, bindWild]
]);

// Ocelot -- raw fish
recipes.addShaped(<minecraft:spawn_egg:98>, [
    [bindWild,             <minecraft:fish:0>, bindWild],
    [<minecraft:fish:0>,   vessel,             <minecraft:fish:0>],
    [bindWild,             <minecraft:fish:0>, bindWild]
]);

// Horse -- golden carrot
recipes.addShaped(<minecraft:spawn_egg:100>, [
    [bindWild,                     <minecraft:golden_carrot>, bindWild],
    [<minecraft:golden_carrot>,    vessel,                    <minecraft:golden_carrot>],
    [bindWild,                     <minecraft:golden_carrot>, bindWild]
]);

// ==================================================================== TIER 3
//  Hostiles. Bound with silver, because of course they are.
//  These are the farm-builder's tier.
// ===========================================================================

// Creeper -- gunpowder
recipes.addShaped(<minecraft:spawn_egg:50>, [
    [bindHostile,            <minecraft:gunpowder>, bindHostile],
    [<minecraft:gunpowder>,  vessel,                <minecraft:gunpowder>],
    [bindHostile,            <minecraft:gunpowder>, bindHostile]
]);

// Skeleton -- bone
recipes.addShaped(<minecraft:spawn_egg:51>, [
    [bindHostile,        <minecraft:bone>, bindHostile],
    [<minecraft:bone>,   vessel,           <minecraft:bone>],
    [bindHostile,        <minecraft:bone>, bindHostile]
]);

// Spider -- string
recipes.addShaped(<minecraft:spawn_egg:52>, [
    [bindHostile,          <minecraft:string>, bindHostile],
    [<minecraft:string>,   vessel,             <minecraft:string>],
    [bindHostile,          <minecraft:string>, bindHostile]
]);

// Zombie -- rotten flesh
recipes.addShaped(<minecraft:spawn_egg:54>, [
    [bindHostile,                 <minecraft:rotten_flesh>, bindHostile],
    [<minecraft:rotten_flesh>,    vessel,                   <minecraft:rotten_flesh>],
    [bindHostile,                 <minecraft:rotten_flesh>, bindHostile]
]);

// Slime -- slimeball
recipes.addShaped(<minecraft:spawn_egg:55>, [
    [bindHostile,              <minecraft:slime_ball>, bindHostile],
    [<minecraft:slime_ball>,   vessel,                 <minecraft:slime_ball>],
    [bindHostile,              <minecraft:slime_ball>, bindHostile]
]);

// Ghast -- ghast tear
recipes.addShaped(<minecraft:spawn_egg:56>, [
    [bindHostile,              <minecraft:ghast_tear>, bindHostile],
    [<minecraft:ghast_tear>,   vessel,                 <minecraft:ghast_tear>],
    [bindHostile,              <minecraft:ghast_tear>, bindHostile]
]);

// Zombie Pigman -- gold nugget
recipes.addShaped(<minecraft:spawn_egg:57>, [
    [bindHostile,                <minecraft:gold_nugget>, bindHostile],
    [<minecraft:gold_nugget>,    vessel,                  <minecraft:gold_nugget>],
    [bindHostile,                <minecraft:gold_nugget>, bindHostile]
]);

// Enderman -- ender pearl
recipes.addShaped(<minecraft:spawn_egg:58>, [
    [bindHostile,                <minecraft:ender_pearl>, bindHostile],
    [<minecraft:ender_pearl>,    vessel,                  <minecraft:ender_pearl>],
    [bindHostile,                <minecraft:ender_pearl>, bindHostile]
]);

// Cave Spider -- fermented spider eye
recipes.addShaped(<minecraft:spawn_egg:59>, [
    [bindHostile,                          <minecraft:fermented_spider_eye>, bindHostile],
    [<minecraft:fermented_spider_eye>,     vessel,                           <minecraft:fermented_spider_eye>],
    [bindHostile,                          <minecraft:fermented_spider_eye>, bindHostile]
]);

// Blaze -- blaze rod
recipes.addShaped(<minecraft:spawn_egg:61>, [
    [bindHostile,              <minecraft:blaze_rod>, bindHostile],
    [<minecraft:blaze_rod>,    vessel,                <minecraft:blaze_rod>],
    [bindHostile,              <minecraft:blaze_rod>, bindHostile]
]);

// Magma Cube -- magma cream
recipes.addShaped(<minecraft:spawn_egg:62>, [
    [bindHostile,                <minecraft:magma_cream>, bindHostile],
    [<minecraft:magma_cream>,    vessel,                  <minecraft:magma_cream>],
    [bindHostile,                <minecraft:magma_cream>, bindHostile]
]);

// Witch -- glowstone dust
recipes.addShaped(<minecraft:spawn_egg:66>, [
    [bindHostile,                    <minecraft:glowstone_dust>, bindHostile],
    [<minecraft:glowstone_dust>,     vessel,                     <minecraft:glowstone_dust>],
    [bindHostile,                    <minecraft:glowstone_dust>, bindHostile]
]);

// ==================================================================== TIER 4
//  The one everybody actually wants.
//
//  Four emeralds and four diamonds is steep, and it is meant to be. A
//  villager is a permanent trading partner, and the emeralds enforce the
//  rule the whole file is built on: you must have met one to make one.
//  Millenaire villagers trade emeralds, extreme hills carry emerald ore,
//  and dungeon loot coughs them up -- so this is reachable without ever
//  finding a vanilla village, just not cheaply.
// ===========================================================================

recipes.addShaped(<minecraft:spawn_egg:120>, [
    [bindVillager,           <minecraft:emerald>, bindVillager],
    [<minecraft:emerald>,    vessel,              <minecraft:emerald>],
    [bindVillager,           <minecraft:emerald>, bindVillager]
]);

// --------------------------------------------------------------- SIGNPOSTS
<minecraft:egg>.addTooltip(format.gray("Surround with a creature's drops and binder ingots to seed a spawn egg."));
