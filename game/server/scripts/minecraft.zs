// --- Torch crafting -> Realistic Torches (unlit) ---
// RealisticTorches already removes vanilla torch recipes and makes coal/charcoal
// + stick craft an UNLIT torch. We must NOT re-add vanilla torches here, or we
// bypass the burn-out system. Instead, output the unlit realistic torch.
// See scripts/torches.zs for the rest of the torch handling.

// Remove any leftover vanilla torch crafting recipes (belt-and-suspenders).
recipes.removeShaped(<minecraft:torch>, [[<minecraft:coal:*>], [<minecraft:stick>]]);
recipes.removeShaped(<minecraft:torch>, [[<ore:fuelCoke>], [<ore:stickWood>]]);

// Coal / charcoal + stick -> 4 unlit torches (matches the mod's own recipe).
recipes.addShaped(<RealisticTorches:TorchUnlit>.withAmount(4), [
    [<minecraft:coal:*>],
    [<ore:stickWood>]]);

// Coal coke + stick -> 8 unlit torches.
recipes.addShaped(<RealisticTorches:TorchUnlit>.withAmount(8), [
    [<ore:fuelCoke>],
    [<ore:stickWood>]
]);
