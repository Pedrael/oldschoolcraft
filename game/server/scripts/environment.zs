// ============================================================================
//  environment.zs - tooltips for the environmental gear pass (2026-08-16)
//
//  House rule: every gameplay change gets a tooltip, because nobody reads
//  changelogs. This is the tooltip half of the EnviroMine config change.
//
//  MUST be identical on the server and in EVERY client instance. Recipes sync
//  from the server, but tooltips and NEI display come from the client's own
//  copy. A stale client here tells people the wrong thing about staying alive.
//
//  Written flat, without arrays or loops: MineTweaker3 on 1.7.10 rejects both
//  ("could not find type IItemStack" / "any values not yet supported").
// ============================================================================

// --- water ---
// An item with NO EnviroMine entry used to BLOCK camel packs outright.
<minecraft:chainmail_chestplate>.addTooltip(format.aqua("Carries a camel pack."));
<Thaumcraft:ItemChestplateThaumium>.addTooltip(format.aqua("Carries a camel pack."));
<Thaumcraft:ItemChestplateVoid>.addTooltip(format.aqua("Carries a camel pack."));
<Thaumcraft:ItemChestplateFortress>.addTooltip(format.aqua("Carries a camel pack."));
<Thaumcraft:ItemChestplateVoidFortress>.addTooltip(format.aqua("Carries a camel pack."));
<Thaumcraft:ItemChestplateRobe>.addTooltip(format.aqua("Carries a camel pack."));
<Thaumcraft:ItemChestplateCultistPlate>.addTooltip(format.aqua("Carries a camel pack."));
<Thaumcraft:ItemChestplateCultistRobe>.addTooltip(format.aqua("Carries a camel pack."));
<Thaumcraft:ItemChestplateCultistLeaderPlate>.addTooltip(format.aqua("Carries a camel pack."));
<Botania:manasteelChest>.addTooltip(format.aqua("Carries a camel pack."));
<Botania:elementiumChest>.addTooltip(format.aqua("Carries a camel pack."));
<Botania:terrasteelChest>.addTooltip(format.aqua("Carries a camel pack."));
<Botania:manaweaveChest>.addTooltip(format.aqua("Carries a camel pack."));
<EnderIO:item.darkSteel_chestplate>.addTooltip(format.aqua("Carries a camel pack."));
<IC2:itemArmorBronzeChestplate>.addTooltip(format.aqua("Carries a camel pack."));
<IC2:itemArmorAlloyChestplate>.addTooltip(format.aqua("Carries a camel pack."));
<IC2:itemArmorNanoChestplate>.addTooltip(format.aqua("Carries a camel pack."));
<IC2:itemArmorQuantumChestplate>.addTooltip(format.aqua("Carries a camel pack."));
<IC2:itemArmorHazmatChestplate>.addTooltip(format.aqua("Carries a camel pack."));
<Aquaculture:item.NeptuniumPlate>.addTooltip(format.aqua("Carries a camel pack."));
<AWWayofTime:boundPlate>.addTooltip(format.aqua("Carries a camel pack."));
<AWWayofTime:boundPlateEarth>.addTooltip(format.aqua("Carries a camel pack."));
<AWWayofTime:boundPlateFire>.addTooltip(format.aqua("Carries a camel pack."));
<AWWayofTime:boundPlateWater>.addTooltip(format.aqua("Carries a camel pack."));
<AWWayofTime:boundPlateWind>.addTooltip(format.aqua("Carries a camel pack."));
<AWWayofTime:sanguineRobe>.addTooltip(format.aqua("Carries a camel pack."));
<BloodArsenal:glass_chestplate>.addTooltip(format.aqua("Carries a camel pack."));
<BloodArsenal:life_imbued_chestplate>.addTooltip(format.aqua("Carries a camel pack."));
<TConstruct:chestplateWood>.addTooltip(format.aqua("Carries a camel pack."));
<TConstruct:heavyPlate>.addTooltip(format.aqua("Carries a camel pack."));
<TConstruct:travelVest>.addTooltip(format.aqua("Carries a camel pack."));
<ThaumicTinkerer:ichorclothChest>.addTooltip(format.aqua("Carries a camel pack."));
<ThaumicTinkerer:ichorclothChestGem>.addTooltip(format.aqua("Carries a camel pack."));
<WitchingGadgets:item.WG_AdvancedRobeChest>.addTooltip(format.aqua("Carries a camel pack."));
<WitchingGadgets:item.WG_PrimordialChest>.addTooltip(format.aqua("Carries a camel pack."));
<RandomThings:spectreChestplate>.addTooltip(format.aqua("Carries a camel pack."));
<Railcraft:armor.steel.plate>.addTooltip(format.aqua("Carries a camel pack."));
<ThermalFoundation:armor.plateBronze>.addTooltip(format.aqua("Carries a camel pack."));
<ThermalFoundation:armor.plateElectrum>.addTooltip(format.aqua("Carries a camel pack."));
<ThermalFoundation:armor.platePlatinum>.addTooltip(format.aqua("Carries a camel pack."));
<ThermalFoundation:armor.plateSilver>.addTooltip(format.aqua("Carries a camel pack."));
<etfuturum:netherite_chestplate>.addTooltip(format.aqua("Carries a camel pack."));
<harvestcraft:hardenedleatherchestItem>.addTooltip(format.aqua("Carries a camel pack."));
<MoCreatures:scorpplatefrost>.addTooltip(format.aqua("Carries a camel pack."));
<MoCreatures:scorpplatenether>.addTooltip(format.aqua("Carries a camel pack."));
<MoCreatures:scorpplatecave>.addTooltip(format.aqua("Carries a camel pack."));
<MoCreatures:scorpplatedirt>.addTooltip(format.aqua("Carries a camel pack."));
<MoCreatures:furchest>.addTooltip(format.aqua("Carries a camel pack."));
<MoCreatures:hidechest>.addTooltip(format.aqua("Carries a camel pack."));
<millenaire:item.ml_byzantinePlate>.addTooltip(format.aqua("Carries a camel pack."));
<millenaire:item.ml_normanPlate>.addTooltip(format.aqua("Carries a camel pack."));
<millenaire:item.ml_japaneseGuardPlate>.addTooltip(format.aqua("Carries a camel pack."));
<millenaire:item.ml_japaneseWarriorBluePlate>.addTooltip(format.aqua("Carries a camel pack."));
<millenaire:item.ml_japaneseWarriorRedPlate>.addTooltip(format.aqua("Carries a camel pack."));

// --- scorpion / frost ---
<MoCreatures:scorphelmetfrost>.addTooltip(format.aqua("Frost chitin holds heat. Warm kit."));
<MoCreatures:scorpplatefrost>.addTooltip(format.aqua("Frost chitin holds heat. Warm kit."));
<MoCreatures:scorplegsfrost>.addTooltip(format.aqua("Frost chitin holds heat. Warm kit."));
<MoCreatures:scorpbootsfrost>.addTooltip(format.aqua("Frost chitin holds heat. Warm kit."));

// --- scorpion / nether ---
<MoCreatures:scorphelmetnether>.addTooltip(format.gold("Sheds heat, and stays warm after dark."));
<MoCreatures:scorpplatenether>.addTooltip(format.gold("Sheds heat, and stays warm after dark."));
<MoCreatures:scorplegsnether>.addTooltip(format.gold("Sheds heat, and stays warm after dark."));
<MoCreatures:scorpbootsnether>.addTooltip(format.gold("Sheds heat, and stays warm after dark."));

// --- scorpion / cave ---
<MoCreatures:scorphelmetcave>.addTooltip(format.green("Filters foul air. The full set filters more."));
<MoCreatures:scorpplatecave>.addTooltip(format.green("Filters foul air. The full set filters more."));
<MoCreatures:scorplegscave>.addTooltip(format.green("Filters foul air. The full set filters more."));
<MoCreatures:scorpbootscave>.addTooltip(format.green("Filters foul air. The full set filters more."));

// --- scorpion / dirt ---
<MoCreatures:scorphelmetdirt>.addTooltip(format.gray("Steady in heat and cold alike. Mildly."));
<MoCreatures:scorpplatedirt>.addTooltip(format.gray("Steady in heat and cold alike. Mildly."));
<MoCreatures:scorplegsdirt>.addTooltip(format.gray("Steady in heat and cold alike. Mildly."));
<MoCreatures:scorpbootsdirt>.addTooltip(format.gray("Steady in heat and cold alike. Mildly."));

// --- fur ---
<MoCreatures:furhelmet>.addTooltip(format.aqua("Warm at night. Stifling in the sun."));
<MoCreatures:furchest>.addTooltip(format.aqua("Warm at night. Stifling in the sun."));
<MoCreatures:furlegs>.addTooltip(format.aqua("Warm at night. Stifling in the sun."));
<MoCreatures:furboots>.addTooltip(format.aqua("Warm at night. Stifling in the sun."));

// --- hide ---
<MoCreatures:hidehelmet>.addTooltip(format.gray("A little warmth, a little shade."));
<MoCreatures:hidechest>.addTooltip(format.gray("A little warmth, a little shade."));
<MoCreatures:hidelegs>.addTooltip(format.gray("A little warmth, a little shade."));
<MoCreatures:hideboots>.addTooltip(format.gray("A little warmth, a little shade."));

// --- hazmat ---
<IC2:itemArmorHazmatHelmet>.addTooltip(format.green("A real respirator. Best air protection in the pack."));

// --- hazmat body ---
<IC2:itemArmorHazmatChestplate>.addTooltip(format.green("Sealed. Filters foul air."));
<IC2:itemArmorHazmatLeggings>.addTooltip(format.green("Sealed. Filters foul air."));

// --- millenaire / norman ---
<millenaire:item.ml_normanHelmet>.addTooltip(format.aqua("Northern kit. Keeps the cold off."));
<millenaire:item.ml_normanPlate>.addTooltip(format.aqua("Northern kit. Keeps the cold off."));
<millenaire:item.ml_normanLegs>.addTooltip(format.aqua("Northern kit. Keeps the cold off."));
<millenaire:item.ml_normanBoots>.addTooltip(format.aqua("Northern kit. Keeps the cold off."));

// --- millenaire / byzantine ---
<millenaire:item.ml_byzantineHelmet>.addTooltip(format.gold("Mediterranean kit. Takes the edge off the sun."));
<millenaire:item.ml_byzantinePlate>.addTooltip(format.gold("Mediterranean kit. Takes the edge off the sun."));
<millenaire:item.ml_byzantineLegs>.addTooltip(format.gold("Mediterranean kit. Takes the edge off the sun."));
<millenaire:item.ml_byzantineBoots>.addTooltip(format.gold("Mediterranean kit. Takes the edge off the sun."));

// --- notes ---
<enviromine:camelPack>.addTooltip(format.aqua("Attaches to any chestplate now, not just vanilla ones."));

// --- lead ---
<ThermalFoundation:armor.helmetLead>.addTooltip(format.green("Respirator. The cheap answer to foul air."));
