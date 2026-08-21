# OldSchoolCraft - quest book recovery recipe
# Crafts a soulbound (EnderIO Soulbound, enchantment id 8) copy of the
# BetterQuesting guide book. BetterQuesting ships NO recipe for guide_book,
# so without this there is no way to replace one lost to lava / despawn.
# The enchantment renders its own "Soulbound" tooltip line, so none is added here.

val soulbook = <betterquesting:guide_book>.withTag({ench: [{id: 8, lvl: 1}]});

recipes.addShapeless(soulbook, [<minecraft:book>, <minecraft:ender_pearl>]);
