#!/usr/bin/env python3
"""Fill the documentation gaps found by auditing CLAUDE.md against the work
actually done this session. Anchored replacements; refuses to run twice."""
import shutil, sys, time

PATH = "/home/duduserver/minecraft/1.7.10/CLAUDE.md"
t = open(PATH, encoding="utf-8").read()

if "splice_chunks.py" in t:
    print("already patched - nothing to do"); sys.exit(0)

edits = []

# -- 1. chunk restore procedure ------------------------------------------
edits.append((
"chunks you are about to overwrite.\n",
"""chunks you are about to overwrite.

### Restoring chunks from a backup

`~/mctools/splice_chunks.py LIVE BACKUP cx,cz [cx,cz ...] [--apply]`

Dry-run by default. Copies the live region to `<name>.before-splice-<stamp>`,
rebuilds the whole file, verifies every chunk reads back, and only then swaps
it in. Server must be **stopped**. Move the `.before-splice` copy out of
`world/region/` afterwards - Minecraft tries to parse anything in that folder.

Working out what to restore:

```
cx = x >> 4        cz = z >> 4          # block  -> chunk
rx = cx >> 5       rz = cz >> 5         # chunk  -> region r.<rx>.<rz>.mca
idx = (cx & 31) + (cz & 31) * 32        # header index within the region
```

- **Use `backups/<date>/backup.zip`, not the nightly tarball.** The in-game
  backup mod runs far more often; on the 2026-08-21 restore it was hours fresher.
  Confirm it predates the damage by comparing the chunk payload sizes.
- **A changed-chunk map shows *loaded* chunks, not damage.** Diffing live
  against backup lit up a clean rectangular edge that looked like a blast
  radius and was really just the chunks that had been loaded since the backup.
  Restoring all of them would have rolled back unrelated building. Scope to the
  blast itself - 3x3 around the target was right for one TNT incident.
- Chunks identical to the backup are skipped as no-ops, so an over-wide
  coordinate list is safe; it is the *non*-identical bystanders that hurt.
- Two rollback copies survive a restore: the `.before-splice-<stamp>` file and
  whatever you copied to `~/mctools/` by hand. Keep both until the world has
  been played on and looks right.
"""))

# -- 2. the minetweaker.log trap -----------------------------------------
edits.append((
"Check `minetweaker.log` after any script change. It should contain zero `ERROR`.",
"""Check `minetweaker.log` after any script change - but **not** with a bare
`grep ERROR`. The file always carries ~38 lines reading
`ERROR ... THIS IS NOT AN ERROR`, so that check can never pass. It is also
written with null bytes, which makes grep treat it as binary:

```bash
tr -d '\\000' < config/minetweaker.log | grep ERROR | grep -v "NOT AN ERROR"
```

That should return nothing."""))

# -- 3. the quest line roster --------------------------------------------
edits.append((
"Task types in use here: `bq_standard:retrieval`, `checkbox`, `hunt`.\nRewards: `bq_standard:item` and `bq_standard:xp`.",
"""Task types in use here: `bq_standard:retrieval`, `checkbox`, `hunt`.
Rewards: `bq_standard:item` and `bq_standard:xp`.

**Keys are type-suffixed.** `questID:3`, `properties:10`, `tasks:9`,
`questLines:9` - the number is the NBT type tag, and dropping it makes the
entry invisible to BetterQuesting rather than throwing an error.

### The 20 lines, as of 2026-08-21 (207 quests)

| Line | Quests | Line | Quests |
|---|---|---|---|
| Getting Started | 14 | The Bounty Board | 21 |
| Thaumcraft | 7 | Discovery | 20 |
| Blood Magic | 6 | Secrets | 12 |
| Botania | 6 | The Great Work | 7 |
| Tech Expansion | 8 | Dressing for the Weather | 8 |
| Applied Energistics 2 | 5 | Forestry: Bees and Trees | 12 |
| Survival & Exploration | 7 | AgriCraft: Crops With Stats | 8 |
| Milestones | 4 | Power and Automation | 10 |
| Tinkers: Tools That Level | 10 | The Twilight Forest | 14 |
| **The Suit** (Modular Powersuits) | 14 | **The Cartographer** (cross-dimension) | 13 |

`The Cartographer` is the closest thing to a main quest line: it walks the
Overworld, Nether, Twilight Forest, Deep Dark, Mining World and End in order.

The generator scripts, one per line added this session:
`add_questline.py`, `add_teaching_lines.py`, `add_twilight_line.py`,
`add_powersuit_line.py`, `add_cartographer_line.py`, `add_shard_daily.py`.

**Unresolved:** CubeThePenguin reports the AgriCraft line as bugged. Every id,
icon and reward validates and the structure matches a working line, so it could
not be reproduced. If it resurfaces, get the specific quest from him and try
dropping and re-picking it - a known BetterQuesting quirk."""))

# -- 4. hidden.txt is the source of truth ---------------------------------
edits.append((
"  `PlayerCaveMapping` and `OpCaveMapping` all `false`.\n",
"""  `PlayerCaveMapping` and `OpCaveMapping` all `false`.
- `hidden.txt` in the server root is the **actual per-player state**, and it
  wins over the config. `defaultHiddenStatus` only applies to players the file
  has never seen. Cube was visible to nobody while everyone was visible to him,
  because he had logged in during the three minutes before the config changed
  and been written in as `false`. After editing the config, read this file and
  fix any `:false` by hand.
"""))

# -- 5. MPS sliders and weight -------------------------------------------
edits.append((
"Re-run `~/mctools/tune_specialmobs.py` after any update\n  that regenerates the config.\n",
"""Re-run `~/mctools/tune_specialmobs.py` after any update
  that regenerates the config.
- **Modular Powersuits ships with every module slider at zero.** A module can
  be installed, powered and lit green and still do nothing - jetpack thrust,
  movement assists, all of it starts at 0 and has to be dragged up in the
  tinker table. This costs a confused evening if you do not know it. Weight
  limit is `25000` g (`config/machinemuse/powersuits.cfg`); exceeding it does
  not disable the suit, it slows the wearer.
"""))

# -- 6. generated scripts --------------------------------------------------
edits.append((
"A stale client script means NEI shows players recipes the server will\nrefuse — this happened with torches.",
"""A stale client script means NEI shows players recipes the server will
refuse - this happened with torches.

Two of these are **generated - do not hand-edit**; re-run the generator instead,
so the tooltips always state the values the config actually holds:

| Script | Lines | Generator |
|---|---|---|
| `armour.zs` | 582 | `~/mctools/gen_armour_tooltips.py` |
| `food.zs` | 177 | `~/mctools/food_temperature.py` |

`aspects.zs` is hand-written: Thaumcraft aspects for Realistic Torches
(lit = Lux, unlit = Arbor), requested by Cube. The ModTweaker signature is
`mods.thaumcraft.Aspects.add(<item>, "lux 1")` - **the amount goes inside the
string**. The three-argument form is rejected. Aspect display in the
Thaumonomicon and NEI is rendered client-side, so this file must ship to
clients like any other.

MineTweaker3 has **no arrays and no loops** - it rejects them with
"could not find type IItemStack" or "any values not yet supported". Everything
must be flat statements, which is why these two scripts are generated."""))

# -- 7. tooling manifest ---------------------------------------------------
edits.append((
"## The git repo\n",
"""## Tooling in `~/mctools`

Mirrored to the repo at `game/server/systemd/`. Everything here is idempotent
and everything that writes takes a backup first.

**Content generation** - run with the server stopped, they edit world data:
`add_questline.py`, `add_teaching_lines.py`, `add_twilight_line.py`,
`add_powersuit_line.py`, `add_cartographer_line.py`, `add_shard_daily.py`.

**Config analysis and generation:**

| Tool | Does |
|---|---|
| `armour_coverage.py` | Audits all 334 EnviroMine armour entries; reports which worn items have no temperature/air values |
| `gen_armour_tooltips.py` | Writes `scripts/armour.zs` from the live config |
| `food_temperature.py` | Assigns 177 foods to tiers (extreme/hot/soup/warming/chilled/frozen) and writes `scripts/food.zs` |
| `clean_armour.py` | Strips duplicate and stale armour entries |
| `check_mods.py` | Verifies a jar is really 1.7.10 by Forge API generation, not by filename |
| `tune_specialmobs.py` | Re-applies the ~10% special spawn weighting |
| `enviromine_fix.py` | Config repairs |
| `nbtread.py`, `osc_batch.py` | NBT inspection; batch console commands |
| `splice_chunks.py` | Chunk rollback from backup (see *Editing region files*) |

**Running services and timers:**

| Tool | Cadence | Does |
|---|---|---|
| `mc-watcher.py` | service, tails `latest.log` | On death, hands the player their exact `/ob_inventory spawn <id>` command. Greets joins with live world facts. Announces first arrival in any of the 12 dimensions |
| `mc-tip.py` | timer | Rotates 103 tips from `tips.json` through `tellraw` |
| `mc-lifesupport.py` | timer | Reads worn armour out of playerdata; drives `/envirostat` so a power suit with a cooling module actually is climate control |
| `mc-afk-guard.py` | timer | Freezes hunger and thirst while a player is idle |
| `mc-digest.py` | weekly | Deaths, causes, play hours, quest progress, unvisited dimensions - to chat and to `digest-latest.txt` |

Two habits worth keeping in these: use `tellraw` rather than `/say`, which
stamps every line with `[Server]`; and make any `--dry-run` path return
**before** writing state, or a dry run silently consumes the rotation.

**Why life support exists at all:** EnviroMine keys its armour entries on item
ID and cannot see NBT, so it can express "power armour insulates" but never
"power armour *with a cooling system* is climate controlled". The script closes
that from outside. Tiering is by correction *frequency*, since `/envirostat`
sets a value rather than scaling one - Heat Sink every 180 s drifts and snaps
back, Liquid Nitrogen every 60 s never drifts. It checks the module is on
**worn** armour (slots 100-103); suit power and slider values are deliberately
not checked, because neither reads reliably out of playerdata.

Reading worn items out of playerdata relies on a structural fact rather than a
full NBT parse (which desyncs inside MPS item data): **Minecraft writes an
item's `Slot` tag last**, so each item's bytes lie between the previous `Slot`
marker and its own. Build that byte pattern from ints - `bytes([1, 0, 4])` -
never from an escaped literal, which is how NUL bytes got written into a source
file. 1.7.10 stores inventory items by **numeric id**, not string id, so any
pre-check looking for a mod name in the raw bytes will reject everybody.

---

## The git repo
"""))

for old, new in edits:
    if t.count(old) != 1:
        print("ABORT: anchor matched %d times: %r" % (t.count(old), old[:60]))
        sys.exit(1)
    t = t.replace(old, new)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(t)
print("patched: %d sections, now %d lines" % (len(edits), t.count("\n") + 1))
