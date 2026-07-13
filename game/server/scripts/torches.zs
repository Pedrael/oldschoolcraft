// ============================================================================
//  Torch unification for Realistic Torches
//  Goal: the Realistic Torches UNLIT torch is the only craftable torch.
//        Players must light it (Matchbox / fire). Vanilla + Tinkers torches off.
// ============================================================================

// --- 2) Disable the Tinkers' Construct stone torch --------------------------
// Removes every crafting recipe that outputs the TConstruct stone torch, so it
// can no longer be made. (Displayed in-game simply as "Torch".)
recipes.remove(<TConstruct:decoration.stonetorch>);

// Optional: if you'd rather REPLACE it with an unlit realistic torch instead of
// removing it outright, delete the line above and uncomment this pair instead:
// recipes.remove(<TConstruct:decoration.stonetorch>);
// recipes.addShapeless(<RealisticTorches:TorchUnlit>, [<TConstruct:decoration.stonetorch>]);

// --- 3) Make sure NO vanilla torch stays craftable --------------------------
// RealisticTorches already strips these at load, but this guarantees it even if
// another script/mod re-adds one later in the load order.
recipes.remove(<minecraft:torch>);

// --- 1) Let recipes that CONSUME a torch accept realistic torches -----------
// Any recipe written against <ore:blockTorch> will now accept the realistic
// lit/unlit torches (and the vanilla one) as an ingredient.
<ore:blockTorch>.add(<RealisticTorches:TorchUnlit>);
<ore:blockTorch>.add(<RealisticTorches:TorchLit>);

// ----------------------------------------------------------------------------
//  To redirect ANOTHER mod's torch to the unlit realistic torch, copy this:
//      recipes.remove(<modid:itemname>);
//      recipes.addShaped(<RealisticTorches:TorchUnlit>.withAmount(4), [ ...grid... ]);
//  Reload in-game after editing with:  /mt reload   (op required)
// ----------------------------------------------------------------------------
