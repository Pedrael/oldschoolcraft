#!/usr/bin/env python3
"""Build add_mekanism_line.py by cloning the proven Powersuits generator.

The Powersuits generator already handles the awkward parts - type-suffixed
keys, backing the database up, refusing to run twice, and calling bq_lint over
its own output. Cloning it and swapping the data is safer than writing a fourth
copy of that logic by hand.
"""
import re, sys

SRC = "/home/duduserver/mctools/add_powersuit_line.py"
DST = "/home/duduserver/mctools/add_mekanism_line.py"
s = open(SRC, encoding="utf-8").read()

M = "Mekanism:"

DESC = {
700: """§7Mekanism is here for its §emachines§7, not for its ore.

You already have five ways to double ore - the Pulverizer, the SAG Mill, the Macerator, the Crusher and the Arc Furnace. Mekanism's own chain went up to §efive times§7, which would have made all five of them pointless, so the higher tiers are §cswitched off§7.

What is left is the part nothing else in this pack does: a miner that digs by filter, a teleporter, a block that moves items, fluid, power and gas at once, and a box that picks up a machine without breaking it.

Start with salt. It is the least impressive thing in the mod and you will need it anyway.§r""",
701: """§7Osmium is Mekanism's own metal and it does §enot§7 exist in any chunk you have already visited.

That is not a bug and it is not worth digging for at home. Walk somewhere genuinely new, or take the Mining World portal. Bring a pick.

Enriched Iron is iron plus carbon in a Metallurgic Infuser. It is the gate to everything else here.§r""",
702: """§7The §eEnrichment Chamber§7 doubles ore, and that is all it will ever do here.

The Purification Chamber, Chemical Injection Chamber, Dissolution Chamber, Washer and Crystallizer are disabled. If you find a recipe online promising five ingots from one ore, it does not work on this server, by choice.

The chamber still matters - it makes the dusts and compressed parts the rest of Mekanism is built from.§r""",
703: """§7Enriched Alloy is the workhorse component. Almost every machine wants some.

Infuse iron with redstone. Then do it again, because you will never have enough.§r""",
704: """§7Power in Mekanism is measured in Joules, but it will happily eat RF from your Thermal Expansion setup and EU from IC2 - the config allows both.

You do not need a new power plant. You need a cable and a Basic Energy Cube.§r""",
705: """§7The §eConfigurator§7 is the single most useful item in the mod and it looks like nothing.

Left-click a machine face to change what it does. Rotate blocks. Empty a tank. Pick up a machine without losing its contents. Carry it always.§r""",
706: """§7Mekanism makes §eplastic§7, which sounds dull until you want a hundred blocks of something in a specific colour that never burns.

Polyethene comes from ethene, which comes from bio-fuel and hydrogen. This is your first proper gas chain - two inputs, one output, and a reason to care about the Electrolytic Separator.§r""",
707: """§7A §eCardboard Box§7 picks up a machine - contents, orientation, energy and all - and puts it in your inventory as a single item.

Nothing else in this pack does this. Move a whole base without emptying a single chest.§r""",
708: """§7EnviroMine tracks the air you breathe. Bad air is one of the ways this world kills people.

The §eGas Mask§7 seals it completely. Not partially, like most helmets - completely. Between this and a Scuba Tank you can walk into places that were previously simply lethal.

Worth making before you need it.§r""",
709: """§7Reinforced Alloy needs Enriched Alloy and diamond dust, and an Osmium Compressor to press it.

You are now past the point where Mekanism is cheap. Everything after this is a real project.§r""",
710: """§7The §eDigital Miner§7 is why people install this mod.

Give it a filter - ore names, item ids, whatever you like - and a radius, and it mines only what you asked for, from anywhere in range, without touching the rest. Silk touch works. It will strip an ore vein out of a mountain and leave the mountain.

This is the machine that ends manual mining.§r""",
711: """§7Atomic Alloy is the top of the material ladder: Reinforced Alloy, refined obsidian and a Pressurized Reaction Chamber.

There is exactly one reason to make it, and it is the next quest.§r""",
712: """§7A §eTeleporter§7 pair, and the twelve dimensions on this server stop being far away.

Set a frequency, feed it power, and step through. The §ePortable Teleporter§7 does the same from your inventory, which is better than it sounds when you are lost.

The §eQuantum Entangloporter§7 goes further: items, fluids, power, gas and heat, wirelessly, between any two of its kind. It is the last logistics block you will ever place.§r""",
713: """§7A §eRobit§7 follows you around, picks up drops, and can be told to craft, smelt or store.

It is not necessary. It is very good company, and after the Digital Miner and the Teleporter you have earned something silly.§r""",
}

Q = [
 (700, "Salt and Sawdust",       0,   0, [],    M+"Salt",             M+"Salt",             "[bag(0)]"),
 (701, "Somewhere New",         48,   0, [700], M+"EnrichedIron",     M+"EnrichedIron",     "[bag(0), it(M+'EnrichedIron', 8)]"),
 (702, "Two Times, No More",    96,   0, [701], M+"Dust",             None,                 "[bag(0)]"),
 (703, "Enriched Alloy",        96, -48, [701], M+"EnrichedAlloy",    M+"EnrichedAlloy",    "[bag(0), it(M+'EnrichedAlloy', 4)]"),
 (704, "Joules, RF and EU",    144, -48, [703], M+"EnergyTablet",     M+"EnergyTablet",     "[bag(0)]"),
 (705, "The Configurator",     192, -48, [704], M+"Configurator",     M+"Configurator",     "[bag(1)]"),
 (706, "Plastic and Gas",      144,  48, [703], M+"Polyethene",       M+"Polyethene",       "[bag(1)]"),
 (707, "Move a Machine",       240, -48, [705], M+"CardboardBox",     M+"CardboardBox",     "[bag(1), it(M+'CardboardBox', 2)]"),
 (708, "Something to Breathe", 240,  48, [705], M+"GasMask",          M+"GasMask",          "[bag(1), it(M+'ScubaTank', 1)]"),
 (709, "Reinforced",           192,  48, [706], M+"ReinforcedAlloy",  M+"ReinforcedAlloy",  "[bag(1)]"),
 (710, "The Digital Miner",    288, -48, [707], M+"Configurator",     None,                 "[bag(2)]"),
 (711, "Atomic",               240,  96, [709], M+"AtomicAlloy",      M+"AtomicAlloy",      "[bag(2)]"),
 (712, "No Distance At All",   288,  96, [711], M+"TeleportationCore",M+"TeleportationCore","[bag(2), it(M+'PortableTeleporter',1)]"),
 (713, "Robit",                336, -48, [710], M+"Robit",            M+"Robit",            "[bag(2)]"),
]

# ---- build the new file -------------------------------------------------
new_desc = "DESC = {\n" + "".join(
    f'{k}: """{v}""",\n' for k, v in DESC.items()) + "}\n"

lines = ["Q = ["]
for qid, name, x, y, pre, icon, task, rew in Q:
    t = f'"{task}"' if task else "None"
    lines.append(f' ({qid}, "{name}", {x}, {y}, {pre}, "{icon}", {t}, {rew}),')
lines.append("]\n")
new_q = "\n".join(lines)

# swap the constant
s = re.sub(r'^P = "powersuits:"$', 'M = "Mekanism:"', s, flags=re.M)
s = s.replace("P+", "M+")

# swap DESC block (from 'DESC = {' up to the line before 'Q = [')
s = re.sub(r"DESC = \{.*?\n\}\n", new_desc, s, count=1, flags=re.S)
# swap Q block
s = re.sub(r"Q = \[.*?\n\]\n", new_q, s, count=1, flags=re.S)
# line name
s = s.replace('NAME = "The Suit"', 'NAME = "The Machine Age"')
# docstring
s = re.sub(r'^""".*?"""', '"""Mekanism teaching line - "The Machine Age".\n\n'
           'Built by cloning the Powersuits generator, so it inherits the same\n'
           'safeguards: backs the database up, refuses to run twice, and lints its\n'
           'own output. Ore processing is deliberately absent from the content -\n'
           'the higher tiers are disabled on this server and the line says so.\n"""',
           s, count=1, flags=re.S)

open(DST, "w", encoding="utf-8").write(s)
print(f"wrote {DST}")
print(f"  quests: {len(Q)}  ids {Q[0][0]}-{Q[-1][0]}  line: The Machine Age")
