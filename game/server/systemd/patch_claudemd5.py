#!/usr/bin/env python3
"""Record the Mekanism integration and what it taught us."""
import shutil, sys, time

PATH = "/home/duduserver/minecraft/1.7.10/CLAUDE.md"
t = open(PATH, encoding="utf-8").read()
if "## Mekanism (added 2026-08-22)" in t:
    print("already patched"); sys.exit(0)

NEW = """## Mekanism (added 2026-08-22)

Mekanism 9.1.1 + MekanismTools, for the machines only. Registry 6492 -> 6682.

**The ore chain is deliberately crippled.** This pack already runs five
ore-processing chains - IC2, Thermal Expansion, EnderIO, Immersive Engineering,
Railcraft - and Mekanism's 5x would have retired all of them. Disabled in
`config/Mekanism.cfg`: Purification Chamber, Chemical Injection Chamber,
Chemical Dissolution Chamber, Chemical Washer, Chemical Crystallizer. Re-apply
with `~/mctools/configure_mekanism.py <config-dir> --apply` after any update
that regenerates the config.

**The Enrichment Chamber stays enabled at 2x**, which is exactly what the
Macerator, Pulverizer and SAG Mill already give. It is also how Mekanism makes
its own dusts and compressed parts, and Refined Obsidian is gated behind it -
which gates the Teleporter, Digital Miner and Quantum Entangloporter in turn.
Disabling it does not balance the mod, it breaks it.

**Removing its ore recipes with ModTweaker is impossible here.** MineTweaker
executes its scripts at 18:38:15; Mekanism finishes registering at 18:38:54.
There is nothing to remove yet, and all seven `removeRecipe` calls returned
"Command ignored". Do not try again - the answer is the load order, not syntax.

Copper and tin worldgen are set to 0: Thermal Foundation and IC2 already
generate both, and UniDict merges the *items* but not the ore. Osmium and salt
stay. Osmium only appears in **newly generated chunks** - that was accepted
rather than using Mekanism's world-regen.

**Known cosmetic error:** ModTweaker2 0.9.6's `SolarEvaporation` handler throws
`NoClassDefFoundError` against Mekanism 9.1.1 - the recipe class was renamed.
It fails to register and nothing else is affected, but it means
`minetweaker.log` now has a permanent ERROR line. Filter it out along with the
`NOT AN ERROR` noise.

### Adding any mod to this world will block the boot

FML compares the world's registry against the loaded mods and asks about the
difference **on stdin**, then blocks on `readLine()` forever. The boot stalls at
`Preparing level` and looks exactly like a deadlock. Adding Mekanism made it ask
about one stale `UniDict:cratedIngotSilver` entry.

Writing the answer into the console FIFO does **not** work - Minecraft's own
console thread competes for stdin and eats it. The mechanism that does work is
already built into `start.sh`:

```bash
touch fml-confirm-once.flag && systemctl restart minecraft
```

which passes `-Dfml.queryResult=confirm` exactly once.

**Read what it wants to drop before confirming - it deletes those blocks and
items from the world.** Scan first: player inventories, every tile entity, and
the raw bytes of the region files. For the Mekanism install that came back zero,
so nothing was lost.

`mc-health` now recognises this state by its log signature and will **never**
auto-restart it - a restart re-asks the same question forever and wipes
`latest.log` each time, which is exactly what happened before the fix.

---

"""

ANCHOR = "## The loot system\n"
if t.count(ANCHOR) != 1:
    print("ABORT: anchor matched %d" % t.count(ANCHOR)); sys.exit(1)
t = t.replace(ANCHOR, NEW + ANCHOR)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(t)
print("patched, now %d lines" % (t.count("\n") + 1))
