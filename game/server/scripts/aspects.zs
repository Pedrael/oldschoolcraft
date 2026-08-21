// ============================================================================
//  aspects.zs — Thaumcraft aspects for items that shipped without any
//
//  Realistic Torches replaces the vanilla torch with a three-state one, and
//  none of the three states carry aspects. That makes them useless in a
//  crucible and invisible to Thaumometer scanning, which is a gap rather than
//  a design choice.
//
//  Requested by CubeThePenguin: lit = Lux, unlit = Arbor.
//
//  Signature is (IItemStack, "aspect amount") - the amount goes INSIDE the
//  string. scripts/witchinggadgets.zs already uses this form.
//
//  Must be present on the client too — aspect display in Thaumonomicon/NEI
//  comes from the client's own scripts.
// ============================================================================

// A burning torch is light itself.
mods.thaumcraft.Aspects.add(<RealisticTorches:TorchLit>, "lux 1");

// Unlit, it is just a stick with a lump on the end.
mods.thaumcraft.Aspects.add(<RealisticTorches:TorchUnlit>, "arbor 1");

// Smouldering sits between the two: still wood, still barely alight.
mods.thaumcraft.Aspects.add(<RealisticTorches:TorchSmoldering>, "arbor 1");
mods.thaumcraft.Aspects.add(<RealisticTorches:TorchSmoldering>, "lux 1");
