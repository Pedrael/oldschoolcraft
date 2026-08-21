# OldSchoolCraft — server operations notes

Minecraft **1.7.10**, Forge **10.13.4.1614**, Java **8**, ~129 server mods / 166 client mods.
Players: `DuduPhudu` (owner/op), `VerrassVerrass`, `CubeThePenguin`.

This file is context for whoever (or whatever) is administering this server. It is
mostly a list of things that are not obvious and that cost real time to discover.

---

## Layout

```
<server root>/                     /home/duduserver/minecraft/1.7.10  on duduserver
  config/                          mod configs (see warnings below)
  scripts/                         CraftTweaker / MineTweaker .zs files
  mods/                            jars — NOT in git
  world/
    region/          r.<x>.<z>.mca  chunk data
    playerdata/      <uuid>.dat     player inventories, XP, position
    data/            inventory-<player>-<timestamp>-{death,grave}-0.dat
    millenaire/      village registry — read the Millenaire section, it bites
  backups/                         rolling backup.zip archives
  region-backup-<date>/            raw .mca snapshots (easier to work with than the zips)
```

Player UUIDs are in `usercache.json`.
`DuduPhudu = e25c57a0-617f-48cd-adab-b4c2659698f0`
`VerrassVerrass = e5f0d7dc-6196-4e68-8733-ffc8e21b84fe`
`CubeThePenguin = e95d535b-8749-4c77-b161-75b953f01609`

---

## Administration

The server runs on **`duduserver`** (EndeavourOS, Ryzen 5 5600G, 30 GB), reachable
over Tailscale SSH exactly like the crypto stack:

```bash
ssh duduserver@duduserver        # note the explicit user — bare `ssh duduserver`
                                 # is rejected by the tailnet SSH policy
```

The `mc` CLI is the whole admin surface. It works on the box or over SSH
(`ssh duduserver@duduserver mc status`):

```bash
mc start | stop | restart    systemd; stop waits for a full world flush
mc status                    systemd + console + jvm cpu/rss + address
mc console                   type commands, watch the log
                             Ctrl-c leaves; the server keeps running
mc logs [n]                  tail -f latest.log
mc errors [n]                ERROR/WARN/FATAL from latest.log
mc cmd "<command>"           any console command, prints the response
mc players                   who is online
mc mt                        /mt reload + minetweaker.log error count
mc backup                    save-off, tar world/, save-on, prune >14d
```

A cold start takes about **75 seconds** to `Done (…)`. The port opens ~35 s in,
*before* mod init finishes — so a console command sent between those two points
is accepted but answers late. Wait for `Done` before trusting `mc cmd`.

`mc cmd` is how you run the grave restores from the OpenBlocks section without
attaching to a console:

```bash
ssh duduserver@duduserver mc cmd "ob_inventory spawn <file-id>"
```

**How the console works, and why not tmux.** The JVM runs in the foreground
under `mc-run`, with stdin wired to a FIFO at `/run/minecraft/console.in`.
`mc cmd` just echoes into that FIFO.

tmux was the first design and it was wrong. tmux daemonises, so systemd logged
*"Supervising process N which is not our child. We'll most likely not notice
when it exits"* — `Restart=on-failure` was silently dead, and `systemctl stop`
returned in 0.07 s while the world was still saving. A `restart` or a reboot
would have started a second JVM on a world the first still had open. With
`Type=simple` the JVM *is* the MainPID, and `ExecStop` (`mc-stop $MAINPID`)
blocks on `kill -0` until it exits — a real stop now takes ~25 s and systemd
waits for all of it.

> **Never identify the server with `pgrep -f 'forge-1.7.10.*universal.jar'`.**
> `-f` matches whole command lines, so it also matches any shell whose arguments
> merely *contain* that string — including the SSH session running the check.
> That false positive made every `stop` burn its full 290 s timeout while the
> server had already exited seconds earlier. Ask systemd instead:
> `systemctl show minecraft -p MainPID --value`.

**Resource priority.** The unit sets `CPUWeight=20` / `IOWeight=20` against the
crypto stack's default 100, so crypto wins whenever the box is actually
contended — and Minecraft still uses the full machine while crypto is idle.
`AllowedCPUs` is deliberately *not* set: hard-pinning would cap TPS even on an
idle box, and 1.7.10's tick loop is single-threaded and latency-sensitive.
`MemoryMax=14G` is a hard wall so a Minecraft leak can never get Postgres
OOM-killed. Overrides live in
`/etc/systemd/system/minecraft.service.d/memory.conf`.

`AlwaysPreTouch` commits the whole 8 GB heap at boot, so RSS reads ~8.8 GB
immediately and permanently. That is expected, not a leak.

**In-game tips.** `mc-tip.timer` says one line from
`~/mctools/tips.txt` into chat every ~75 minutes. It self-guards three ways: the
server must be up, at least one player must be online, and the hour must be
between 19:00 and 01:00. Outside those it exits silently, so it never spams an
empty server or the log. Tips are picked without repeating until the list is
exhausted (state in `~/mctools/tip-state`).

Every doc in `docs/` complains that the content exists and nobody knows about
it, and `EVENT-NIGHTS.md` opens by noting there is no scheduler mod. Since the
move there is one: the host. Add a tip by appending a line to `tips.txt` —
no restart, no reload.

## Mods added 2026-08-18

Twilight Forest 2.4.3, Modular Powersuits 0.11.1.117 (+ **Numina**, its
dependency), Special Mobs 4.2.3, Sit 1.1. Plus Hide Names and JourneyMap
installed **server-side** for stealth (see below). 169 mods now.

Things that cost time to work out:

- **Filenames lie about the Minecraft version.** Twilight Forest 2.4.3's
  `mcmod.info` contains an unsubstituted Gradle token where `mcversion` should
  be, and `sit` has no `mcmod.info` at all. The reliable test is the Forge API
  generation in the bytecode: 1.7.10 uses `cpw.mods.fml`, 1.8+ uses
  `net.minecraftforge.fml`. `~/mctools/check_mods.py` does this.
- **Dimension 7 was already reserved** by a leftover `config/TwilightForest.cfg`
  from a previous install, with no `world/DIM7` generated — so TF slotted in
  with no conflict. Dimension IDs in use: -112 -100 -42 -34 -19 -17 -2 -1 0 1 2
  6 7 69.
- **"Zip file … failed to read properly, it will be ignored" is not fatal.**
  JourneyMap is a multi-release jar (`META-INF/versions/9/`) and 1.7.10's
  coremod scanner cannot parse that. The mod still loads. Do not remove a jar
  on the strength of that warning alone — check for
  `Mod <id> is using network checker` further down the log.
- **Special Mobs needs no loot integration.** Infernal Mobs discovers new entity
  classes on its own and writes them into `permittedentities` set to `true`; all
  97 known classes are permitted, including every Special Mobs variant. They
  already roll Elite/Ultra/Infernal and already drop the rebuilt Fortune tables.
- **Special Mobs was tuned down before anyone met it.** Stock weighting made
  14–32% of spawns special, which stacks badly with Infernal Mobs. All twelve
  `*_rates` sections are now `_vanilla = 9 x variants`, i.e. a flat ~10%, and
  `_allow_vanilla=true`. `spawn_eggs` stays **false** — it would consume 106
  global entity IDs. Re-run `~/mctools/tune_specialmobs.py` after any update
  that regenerates the config.
- **Modular Powersuits ships with every module slider at zero.** A module can
  be installed, powered and lit green and still do nothing - jetpack thrust,
  movement assists, all of it starts at 0 and has to be dragged up in the
  tinker table. This costs a confused evening if you do not know it. Weight
  limit is `25000` g (`config/machinemuse/powersuits.cfg`); exceeding it does
  not disable the suit, it slows the wearer.

## Stealth: hidden names and no radar

Enforced server-side, not by asking people nicely:

- `config/tlf/HideNames.cfg` — `defaultHiddenStatus=true`, `allowCommand=false`.
  Hide Names had been installed **client-side only**, where it is just a toggle
  each player controls. Server-side it is policy.
- `config/JourneyMapServer/world.cfg` — `PlayerRadar`, `OpRadar`,
  `PlayerCaveMapping` and `OpCaveMapping` all `false`.
- `hidden.txt` in the server root is the **actual per-player state**, and it
  wins over the config. `defaultHiddenStatus` only applies to players the file
  has never seen. Cube was visible to nobody while everyone was visible to him,
  because he had logged in during the three minutes before the config changed
  and been written in as `false`. After editing the config, read this file and
  fix any `:false` by hand.

> **All three players are op level 4.** Any `Op*` setting left `true` gives
> everyone the thing you just disabled. That applies to radar, cave mapping,
> and anything else JourneyMap gates on op status.

Not covered: `Neat` draws health bars over entities client-side with no server
enforcement. If it renders them over players it is a hole in this — check
`config/Neat.cfg`, which only exists after a client has run once.

## Adding quest lines

Quest data is the only content channel that **syncs server to client on its
own**. Tooltips and recipes do not — that gap is what went wrong with torches,
and it is why teaching content belongs in the book rather than in `.zs`.

The live database is `world/betterquesting/QuestDatabase.json`
(`config/betterquesting/DefaultQuests.json` is only used for a fresh world).
BetterQuesting rewrites it on shutdown, so **edit it with the server stopped**
or the change is silently discarded.

Scripts that do this live in the repo at `game/server/systemd/`:
`add_questline.py` and `add_teaching_lines.py`. Both are idempotent, both back
the database up before writing, and both refuse to run if the quest IDs or line
name already exist.

Three things that make a quest impossible rather than merely wrong:

- **Metadata.** `ThermalExpansion:Machine` is one id with a dozen meta values;
  `TConstruct:Smeltery` has several. A retrieval task with the wrong `Damage:2`
  can never be completed. Mine the existing database for proven `(id, damage)`
  pairs rather than guessing — there are ~168 already in use.
- **Item ids.** Validate every id against the world's own Forge registry, which
  is readable straight out of `world/level.dat` as plain strings. Both scripts
  do this and abort on a miss.
- **When unsure, use `bq_standard:checkbox` — but never as a prerequisite.**
  A quest nobody can finish is worse than no quest at all, so a checkbox is the
  right fallback wherever an item's metadata cannot be verified. **It does not
  self-tick.** An earlier version of this file claimed it did; that was wrong,
  and building the teaching lines on it locked 37 quests for one player and 27
  for another. Somebody has to open the quest and click. Retrieval tasks *do*
  detect passively, so players never learn that some quests need a click —
  there is no pattern for them to notice. Keep checkboxes out of
  `preRequisites` entirely and the mistake cannot recur.

Task types in use here: `bq_standard:retrieval`, `checkbox`, `hunt`.
Rewards: `bq_standard:item` and `bq_standard:xp`.

### Never use a checkbox quest as a prerequisite

This cost two players most of a quest book and looked exactly like a bug.

`bq_standard:retrieval` tasks **auto-detect items in a player's inventory even
while the quest is locked**. `bq_standard:checkbox` tasks do not - somebody has
to open the quest and click. So a chapter that opens with a checkbox and gates
the rest of the line on it produces this:

> every task shows ticked green, and there is no Claim button

which is indistinguishable from broken quest data. Vera reported it as "I meet
the condition but cannot claim"; Cube reported the same thing as "AgriCraft
quests bugged, maybe wrong item id". Both were this. At its worst it had **37
quests locked for Vera, 27 for Cube and 21 for Dudu** behind 29 unticked boxes.

The fix, and the rule going forward: a checkbox may be *content*, never a
*gate*. `~/mctools/unblock_checkbox_gates.py` splices any checkbox quest out of
the prerequisite graph - downstream quests inherit the checkbox's own
prerequisites, so real ordering between real quests survives - and ticks the
offending boxes with `claimed:0` so the reward is still the player's to collect.
Run it with the server **stopped**.

### `bq_lint.py` - so it cannot come back

Repairing the live database fixes today. It does **not** stop the trap being
rebuilt, and there were three places it could return from:

| Place | Why it matters |
|---|---|
| `world/betterquesting/QuestDatabase.json` | what everyone plays |
| `config/betterquesting/DefaultQuests.json` | the template a **fresh world** is built from |
| `~/mctools/add_*_line.py` | any **future** quest line |

All three are now clean, and the generators enforce it themselves: each one
calls `bq_lint.check(DB, fix=True)` after writing, so a line cannot be shipped
with a broken graph even if the author forgets.

```bash
bq_lint.py <QuestDatabase.json|DefaultQuests.json> [--fix]   # exit 1 = problems
```

It checks four things, all invisible from inside the game:

- **checkbox gates** - the fault above; `--fix` splices them out
- **dangling prerequisites** - pointing at a quest that does not exist, which
  locks the quest forever
- **self-referencing and cyclic prerequisites** - same effect
- **duplicate questIDs** - BetterQuesting matches progress to quests by
  `questID`, so a duplicate silently merges two quests' progress

Regression-tested by injecting each fault into a copy of the live database and
confirming the linter catches and repairs it.

### Parties share the work, not the acknowledgement

`world/betterquesting/QuestingParties.json` holds the party. Inside one,
**retrieval task credit propagates to every member automatically**; checkbox
tasks never do. Evidence from The Suit line: quests 621/622/623/627/629 are
credited to both party members although only one of them played the chapter,
while Cube - outside the party - has no credit on any of them.

That asymmetry is what turns the trap above into a silent lockout: a party
member is handed all the item progress and then blocked by the one task type
that cannot be shared. There is no config switch for it; progress sharing is
inherent to BQ3 parties. `globalShare` in the quest properties is a different
thing entirely - it governs server-wide *global* quests, not parties.

**Reading who did what:** `completeUsers:9` under each task is task credit;
`completed:9` on the quest is the per-player completion, and its `claimed:1`
flag is 0 when the reward is sitting there waiting. A quest with task credit
but no `completed` entry is the locked-but-ticked state described above.

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
dropping and re-picking it - a known BetterQuesting quirk.

## What the death data actually says

Measured from 164 death messages across the archived logs and 171 grave
snapshots. Worth re-running before any difficulty tuning — guessing has been
wrong twice.

**The play window is 18:00–03:00 and nothing else.** Zero deaths have ever been
recorded between 04:00 and 17:00. 69% fall between 22:00 and 01:00. This is why
the backup runs at 04:10 and tips stop at 01:00.

**What kills people**, in order: skeletons (20), zombies (19), fire (13), falls
(10), other players (12), **thirst (10)**, explosions (8), lava (6),
suffocation (6), Eldritch Guardians (10 across two forms), and four people
squashed by a falling block — EnviroMine physics, not a mob.

**Nobody has ever died of cold or heat.** Not once. Any temperature gear is
flavour, not a fix for a live threat. Hydration, by contrast, is 6% of all
deaths and was made worse by the camel-pack gap.

**Graves are not broken.** 25% of deaths produce no grave file, which looks
alarming and isn't: death snapshots for those deaths have a median size of 286
bytes against 1391 for the rest, and 61% are under 300 bytes. OpenBlocks does
not place a grave when there is nothing to put in it — those are people dying
with empty pockets, usually on the way back to their stuff. Fire, lava and
drowning account for most of the remainder, and even those stay recoverable
because the `-death-` snapshot is written unconditionally.

**AFK guard.** `mc-afk-guard.timer` runs every 60s. After **3 minutes** with no
change in position *or* look direction, it tops the player's water up and pulls
body temperature back to 37, once a minute, until they move again.

This exists because "Presence pays, absence never costs" was not quite true.
Vanilla hunger only charges you for *doing* things — measured: exhaustion sat at
exactly 0.115 through 44 seconds of genuine idling — but **EnviroMine's thirst
and temperature run on a wall clock** and do not care whether anyone is at the
keyboard. Twenty minutes away could mean coming back dead of dehydration.

Detection reads `Pos` and `Rotation` straight out of `world/playerdata/*.dat`,
so turning on the spot counts as being present. It deliberately does **not**
call `save-all` — Minecraft autosaves player data anyway, and forcing a full
save every 60s on a 389 MB world is a lag spike bought for nothing. Playerdata
can be ~45s stale, which is irrelevant against a 3-minute threshold.

Temperature is `set` to 37.0 (EnviroMine's own neutral value, used as the
default cap everywhere in its configs). Water is `add`ed in steps of 15 rather
than `set` to a guessed maximum — if the scale is not what we assume, adding a
little repeatedly still clamps safely at full.

> **`/envirostat` is a setter with no getter.** `envirostat <player> <add|set>
> <temp|sanity|water|air> <float>` can change a stat but cannot read one back,
> and it prints nothing on success — it only prints its usage line when the
> syntax is wrong. So "no output" means accepted. There is no way to verify the
> effect landed from the console; watch the in-game bar instead.

Detections are logged to `~/mctools/afk.log`; current state is in
`~/mctools/afk-state.json`.

**Power suit life support.** `mc-lifesupport.timer`, every 30s. A cooling module
on **worn** armour takes over body temperature; the tier sets how often it is
corrected — Heat Sink 180s, Cooling System 90s, Liquid Nitrogen 60s. A Water
Tank adds thirst. Air is topped up regardless.

EnviroMine keys armour on item ID and cannot see NBT, so it can never know which
modules a suit carries — hence doing it from outside with `/envirostat`. Tiering
is by *frequency* because `/envirostat` can only set a value, not scale one.

Worn detection uses a structural fact, because a full NBT parse desyncs inside
MPS item data: **Minecraft writes an item's `Slot` tag last**, so each item's
bytes lie between the previous `Slot` marker and its own. Slots 100–103 are
feet/legs/chest/head. Suit power and slider values are *not* checked — neither
reads reliably.

**Event watcher.** `mc-watcher.service`, long-running, tails `latest.log`:

- **death** → finds the grave snapshot and whispers the player the exact
  `/ob_inventory spawn <id>`. Everyone is op 4, so they run it themselves. Falls
  back to the `-death-` snapshot and says so (it omits Baubles/Traveller's Gear).
- **join** → greeting built from live state (day, quest count, what nobody has done)
- **dimension** → announces a player's first visit, louder if nobody has ever been

Seeded from existing `world/DIM*` folders so old ground never reads as new. Only
**DIM-17, the Wyvern Lair**, can still trigger the first-ever announcement.

**Weekly digest.** `mc-digest.timer`, Sunday 21:00, posts to chat and writes
`~/mctools/digest-latest.txt`. Two traps found while building it, both fixed:
PvP deaths reported the *killer's name* as a cause ("Mostly: DuduPhudu x5"), and
"never visited" must come from **world folder existence**, not the watcher's
per-player state, which only counts from the day it was installed.

**Tips.** `mc-tip.timer`, 50 min, 103 tips in five categories (`tip`, `hint`,
`warn`, `stat`, `lore`) sent with **`/tellraw`** — `/say` stamps an ugly
`[Server]` prefix. `stat` lines carry live tokens resolved at send time:
`{quests} {lines} {deaths} {dims} {mods} {armour} {day}`. Category weighting
shifts by hour, so late night leans to flavour. Add one by appending to
`~/mctools/tips.json`; no restart needed.

> **Shell escaping has corrupted files three times this session.** Passing
> binary escapes like `\x01` through the Bash tool produced real NUL bytes in a
> Python source file. Build byte patterns from integers instead —
> `bytes([1, 0, 4]) + b"Slot"` — and prefer writing files directly over
> patching them through a shell heredoc, which also breaks on apostrophes.

Backups: `minecraft-backup.timer` runs `mc backup` nightly at 04:10 local,
clear of the crypto stack's 03:20 UTC window. It pauses chunk writes around the
tar, so `region/` is never captured mid-write. 14-day retention.

## The 2026-08-21 hang: "active and listening" is not "working"

An unclean shutdown at `08:25:47` truncated `world/level.dat` to **0 bytes**.
On the next boot the server threw `EOFException` reading it, then **deadlocked
during world load** instead of falling back to `level.dat_old`. It sat in
`futex_do_wait` at 0% CPU for **13 hours**. Every check available said it was
healthy:

| Check | Said | Reality |
|---|---|---|
| `systemctl is-active` | `active` | JVM alive, blocked on a lock |
| port 25565 | listening | socket bound *before* world load began |
| `mc-watcher` | quiet | a server that stops logging looks like a quiet one |

**What actually proves the server is up:** `Done (` appears in the *current*
`latest.log`, **and** the log is still advancing, **and** the console answers.
`~/mctools/mc-health.py` asserts all three every 5 minutes (`mc-health.timer`)
and restarts on failure with `--restart`. It was regression-tested against the
real hung log, which survives as `logs/2026-08-21-3.log.gz`.

Recovery, if it happens again:

```bash
systemctl stop minecraft          # a deadlocked JVM will need SIGKILL; nothing
                                  # is in memory to lose - the world never loaded
python3 ~/mctools/restore_leveldat.py   # refuses unless the live file is really broken
systemctl start minecraft
```

`level.dat` carries the **Forge item registry** (~1200 modded ids). Losing both
it and `level.dat_old` scrambles every modded item in the world, so the restore
script verifies the rescue copy gunzips *and* contains registry entries before
it writes anything. Note `gzip.decompress(b"")` returns `b""` rather than
raising - an empty file will read as "valid" unless you check for content.

Damage was limited to that one file: all 210 region files had valid headers and
all playerdata gunzipped. The 0-byte `RedstoneEther/node*.dat`, `cofh/*.cfg` and
`labyrinth.dat` files are **normal** empty stubs, present in every dimension.

**`mc-watcher` will not come back on its own.** It is `BindsTo=minecraft.service`,
which propagates stop but not start. A drop-in at
`/etc/systemd/system/minecraft.service.d/watcher.conf` adds `Wants=mc-watcher.service`
so it is pulled up with the server.

---

## Rule zero: stop the server before editing anything

Mods rewrite their own config files at runtime and on shutdown. Infernal Mobs
rewrites `InfernalMobs.cfg` whenever it meets a new entity class. Millenaire
rewrites `villages.txt` on load. Forge rewrites most `.cfg` files on startup.

Edit a config while the server is up and it will be silently reverted. This has
already happened once. **Stop the server, edit, verify, start.**

Config files here are **CRLF**. Preserve them — a whole-file line-ending change
buries the real diff.

---

## Millenaire: `villages.txt` is NOT the source of truth

This one cost a full day and a wrong fix.

`world/millenaire/villages.txt` is a **derived index**. Millenaire rebuilds it on
every load by scanning `world/millenaire/buildings/`. Removing a line from
`villages.txt` does nothing — the village reappears on next boot, appended to the
*bottom* of the file. That reappearance-at-the-bottom is the diagnostic tell.

To actually delete a village, delete its files:

```
world/millenaire/buildings/<X>_<Y>_<Z>.gz
world/millenaire/buildings/<X>_<Y>_<Z>_temp.gz
world/millenaire/buildings/<X>_<Y>_<Z>_paths.bin
world/millenaire/buildings/<X>_<Y>_<Z>_pathstoclear.bin
```

Then clean `villages.txt` and any `village_reputations=` / `village_diplomacy=` /
quest lines referencing it in `world/millenaire/profiles/<player>/`.

`<X>_<Y>_<Z>_temp.gz` is **gzipped NBT** and readable. It contains every building
with anchor coordinates, width, length and orientation — the exact village
footprint, far better than guessing a radius around the town hall.

`world/millenaire/config.txt` has `generate_villages=true|false`. Currently `true`
by choice: villages elsewhere are wanted, only specific ones get removed.

**Known upstream bug:** Millenaire drops villages onto player builds even with a
large minimum distance configured. Expect this to recur.

---

## OpenBlocks graves: nothing is ever really lost

`storeContents=true` in `OpenBlocks.cfg`. On **every death**, OpenBlocks writes a
full NBT snapshot to `world/data/`:

```
inventory-<player>-<YYYY-MM-DD_HH.MM.SS>-death-0.dat   player-slot layout (0-35 main, 36-39 armour)
inventory-<player>-<YYYY-MM-DD_HH.MM.SS>-grave-0.dat   flattened, but includes Baubles / Traveller's Gear
```

Restore in-game, no file editing, server stays up:

```
/ob_inventory spawn <file-id>                  drops items at YOUR feet — safest, overwrites nothing
/ob_inventory restore <player> <file-id>       puts it in their inventory, REPLACES what they carry
```

`<file-id>` is the filename minus the `inventory-` prefix and the `.dat` suffix.

Prefer the `-grave-` file: it includes equipment-slot items the `-death-` file lacks.
Prefer `spawn` over `restore` unless the player's inventory is genuinely empty.

### Why graves used to vanish

EnviroMine physics treated the grave as a falling block. `Enable Physics=true`
and `Default Stability Type (BlockIDs > 175)=loose`, and the grave block
(id 2496) had no EnviroMine entry, so it inherited `loose`. A grave placed on
anything that isn't valid support — a carpet, famously — got converted to a
falling block on the next physics pass, and the tile entity went with it.

Fixed by pinning it in
`config/enviromine/profiles/default/CustomProperties/OpenBlocks.cfg`:

```
blocks { tile_openblocks_grave_grave { S:01.Name=OpenBlocks:grave  S:10.Stability=none ... } }
```

**Every modded block in the pack still inherits `loose` by default.** Any modded
block that ends up unsupported is a candidate for the same treatment. Changing
that default to `none` would immunise the whole pack in one line — not done yet,
discuss before doing.

---

## Editing region files (`.mca`)

Format: 4096 B of location entries (1024 × [3-byte sector offset, 1-byte count]),
4096 B of timestamps, then chunk payloads on 4096-byte boundaries as
`[4-byte length][1-byte compression][data]` — compression 1 = gzip, 2 = zlib.
Chunk `(cx, cz)` is at header index `(cx & 31) + (cz & 31) * 32`.

This world is **NEID-extended**: chunk sections carry `Blocks16` alongside
`Blocks`/`Add`. Any block-level tooling must account for it.

When splicing chunks, **rebuild the whole region file** rather than patching
sectors in place — no stale sectors, no fragmentation, header always consistent.

### Before rolling back any chunk, check for graves

A chunk rollback destroyed a player's grave that had been placed seven minutes
earlier. Always scan `world/data/` for `inventory-*` files newer than the backup
you are restoring from, and check whether the grave coordinates fall inside the
chunks you are about to overwrite.

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

---

## Changes made to this pack (2026-08)

**`scripts/silver.zs`** — Thermal Foundation silver gear crafts pre-enchanted at
no extra cost: sword/axe/sickle get Smite III + Bane of Arthropods III, bow gets
Power III, all four armour pieces get Protection II. Also two craftable enchanted
books: 4 silver + 4 rotten flesh + book = Smite III; string instead of flesh =
Bane III. Books use `StoredEnchantments`, **not** `ench` — that is the difference
between a working book and a decorative one.

**`scripts/eggs.zs`** — 22 craftable spawn eggs. Nine-slot pattern: 4 of the
creature's own drops + 4 binder ingots + 1 chicken egg centre. Binders: gold
nuggets (livestock), gold ingots (wild), silver (hostile), diamond+emerald
(villager). You cannot craft an egg for something you have never killed.

**`scripts/survival.zs`** + `config/enviromine/.../ThermalFoundation.cfg` — five
dead Thermal Foundation metals given environmental jobs. Copper = camel-pack
capable (water). Lead helmet = `Air 1.0` respirator. Nickel = warm at night.
Invar = damps heat and cold both. Tin = best sun multiplier, cold after dark.
Plus cheaper recipes trading metal for MoCreatures fur/hide and charcoal.

All numbers pinned inside EnviroMine's own vanilla envelope (Temp Add −1.0..2.5,
multipliers 0.90..1.20, taken from its leather/iron/diamond/gold entries).

**Hydration gotcha:** EnviroMine sets `Allow Camel Pack` on all four *vanilla*
chestplates. Modded chestplates with no entry **block camel packs entirely**.
This is invisible in-game and is why hydration felt brutal. Worth extending the
flag to the modded chestplates people actually wear.

**`config/InfernalMobs.cfg`** — `MM_Regen` and `MM_1UP` disabled. Regen was
+1 HP per 500 ms forever (hardcoded, no rate config, so off was the only lever);
1UP snapped mobs to full health below 25%. `MM_Lifesteal` deliberately left on.
Expect harmless "tag mismatch" log spam for mobs saved before the change.

**`config/waystones.cfg`** — `Teleport Button in GUI=true`, so warping needs no
Warp Stone. Players still must physically visit a waystone before they can travel
to it; one waystone gives an empty menu.

---

## The loot system

Built as **floor -> step -> spike**: you always leave with something, a real
upgrade shows up often enough to believe in, and a tiny tail makes people shout.
Wherever possible the prize is a *sealed container* (loot bag, lockbox, Dice of
Fate) so there are two reveals instead of one.

| Where | File / config | Scale |
|---|---|---|
| Vanilla + mod chest categories | `scripts/fortune.zs` | 16 categories |
| Twilight Forest + Modular Powersuits | `scripts/fortune_frontier.zs` | 36 items |
| Thaumcraft loot bags (common/uncommon/rare) | both scripts | 3 tiers |
| Elite / Ultra / Infernal mob drops | `config/InfernalMobs.cfg` | already dense |
| Runic Dungeons rooms | `config/RunicDungeons/ChestGeneration.cfg` | 4 tables, 537 entries |

570 chest-loot entries total. `scripts/dump_loottypes.zs` prints every live
category as `[LOOTTYPE] <name>` into `minetweaker.log` - harvest that list
before adding categories rather than guessing names.

**Twilight Forest chests cannot be modified.** TF does not use vanilla
`ChestGenHooks` at all; it has its own hardcoded `TFTreasure`/`TFTreasureTable`,
which MineTweaker cannot reach. Confirmed by unpacking the jar - there is not a
single `ChestGenHooks` reference in it. So `fortune_frontier.zs` does the
inverse: it seeds **TF items into Overworld chests** so the dimension advertises
itself. You find a Live Root in a mineshaft and have no idea what it is.

Two rules that keep that from backfiring:

- **Never put boss-tier gear in overworld chests.** Fiery/knightly/yeti/arctic
  gear, naga scales, scepters and the boss bows are the *reason* to go to
  Twilight Forest. Handing them out elsewhere cheapens the dimension you are
  advertising. Entry-tier materials, charms, maps and food only.
- **Validate every id against the world registry before shipping.** The registry
  is readable straight out of `world/level.dat`; all 36 ids in
  `fortune_frontier.zs` were checked against it, and the loot categories against
  the `[LOOTTYPE]` dump. A typo here fails silently as a missing entry.

**`powersuits:powerArmorComponent` is deliberately absent.** It is a subtyped
item and the metadata order could not be verified offline - the class strings
list `componentTooltip` first, which is a tooltip key rather than a component,
so the obvious reading is off by one. Only metadata-free MPS items are used
(`tinkerTable`, `luxCapacitor`, `powerFist`, and single armour pieces). If you
want components in loot, confirm the metas in-game first.

---

## Scripts must match on client and server

`scripts/*.zs` has to be identical in the server folder and in the client instance
(`.../PrismLauncher/instances/OldSchoolCraft_1.0.0/minecraft/scripts/`). Recipes
sync from the server, but **tooltips and NEI display come from the client's own
copy**. A stale client script means NEI shows players recipes the server will
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

MineTweaker3 arrays and `for` loops **do work** - `fortune.zs` declares
`string[]` loot-category lists and iterates them, and loads with zero errors.
What it rejects is `as IItemStack[]` ("could not find type IItemStack") and
`any` values, so a list of *items* cannot be built or looped over. That is the
whole reason `armour.zs` and `food.zs` are generated as flat statements while
`fortune.zs` can loop over category names by hand.

Check `minetweaker.log` after any script change - but **not** with a bare
`grep ERROR`. The file always carries ~38 lines reading
`ERROR ... THIS IS NOT AN ERROR`, so that check can never pass. It is also
written with null bytes, which makes grep treat it as binary:

```bash
tr -d '\000' < config/minetweaker.log | grep ERROR | grep -v "NOT AN ERROR"
```

That should return nothing.

---

## Tooling in `~/mctools`

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
| `mc-health.py` | 5 min | Asserts the server actually serves: startup finished, log advancing, console answers. `--restart` acts on failure |
| `restore_leveldat.py` | on demand | Repairs a truncated `world/level.dat` from a verified rescue copy |
| `unblock_checkbox_gates.py` | on demand | Splices checkbox quests out of the prerequisite graph and ticks the ones that were gating |
| `bq_lint.py` | after any quest edit | Validates a quest graph: checkbox gates, dangling/cyclic prerequisites, duplicate questIDs. `--fix` repairs. Generators call it automatically |

**Who is online, without asking.** `mc-lifesupport` and `mc-afk-guard` used to
run `list` on every tick - three times a minute, awake or not, which put ~5700
`Players currently online: [ 0 ]` lines a day into `latest.log` and is exactly
what made the hang unreadable. `mc-watcher` already sees every join and leave,
so it now publishes `~/mctools/online.json` and the timer scripts read that
file, falling back to `list` only if the roster is stale (meaning the watcher
is down). When nobody is online they now do nothing at all. `mc-watcher`
rebuilds the roster from the whole of `latest.log` on start, because it seeks
to the end of the file and would otherwise forget everyone already connected.

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

`https://github.com/Pedrael/oldschoolcraft` — monorepo, `game/server/`,
`game/client/`, `website/`. Mod jars are gitignored (licensing + size);
`modlist.txt` files are the source of truth. `world/`, `logs/`, `backups/`,
`ops.json` and `usercache.json` are also excluded.

`tools/sync_pack.py` (also at `Modding/sync_pack.py`) copies live config and
scripts into the repo. It matches each file's **existing** line endings, because
the repo mixes LF and CRLF with no `.gitattributes` — copying blind marks 400+
files as fully rewritten. It refuses to touch `server.properties` (the repo copy
is a sanitised template) and hard-fails the push on Windows user paths, rcon
passwords, GitHub tokens or new routable IPs.

The server address is committed in `game/*/config/itlt.cfg` and hardcoded in
`website/src/components/ServerMonitor.tsx`. Deliberate — the site shows server
status. It used to be a literal residential IP, which broke in three places at
once on every rotation; all three now hold `oldschoolcraft.duckdns.org:25565`,
so a rotation is invisible.

**The repo's `game/client/scripts/` is badly stale** — 7 files against the live
client instance's 15 and the server's 16. `game/server/scripts/` is current.
Run `tools/sync_pack.py` before trusting the client side of the repo for
anything.

---

## The move to `duduserver` (2026-08-16)

Migrated off the Windows PC (`192.168.110.239`) to `duduserver`. What the move
actually turned up, for whenever this happens again:

- **Java 8 is not in the Arch repos.** EndeavourOS has no `jre8-openjdk` and no
  `archlinux-java`. Installed the Temurin 8 tarball to `/opt/java/temurin8` —
  same build `START-SERVER.bat` used to fetch. No AUR build, no package churn.
- **`jre8/` and the `libjnlua*-windows-x86_64.dll` files did not come across.**
  OpenComputers extracted its own `libjnlua5{2,3,4}-linux-x86_64.so` on first
  boot, as hoped. Verified present.
- **`firewalld` is active on `duduserver`** and silently blocked 25565 on the LAN
  while the tailnet worked fine (`tailscale0` sits in the `trusted` zone, the
  LAN NICs in `public`). This looks exactly like a dead server. Fixed
  permanently: `firewall-cmd --zone=public --add-port=25565/tcp --permanent`.
- **The public IP did not change** — both machines are behind the same router, so
  the household public IP still resolves the same. Only the router's internal forward
  target moved, `.239` → `.59`.
- **Two NICs on the same subnet**: `enp5s0` (192.168.110.59, ethernet, default
  route) and `wlan0` (192.168.110.38). Forward to the ethernet one.
- No Windows path was baked into any config — the grep came back empty.
- The world copied cleanly with the server stopped: 129 mod jars, 529 configs,
  152 region files, 3 playerdata, 46 Millenaire files, all counts matching.
  162 mods loaded, zero FML errors, zero MineTweaker errors.

The old Windows folder at `C:\Users\DuduPhudu\MinecraftServer\1.7.10` is now a
**stale snapshot**. Nothing auto-starts it (checked: no scheduled task, nothing in
the Startup folder), and `START-SERVER.bat` was removed from the Linux copy. Do
not boot it — two divergent worlds on one public port is the failure mode.

## Dynamic DNS

Players connect to **`oldschoolcraft.duckdns.org:25565`**, not the raw IP. A
`duckdns.timer` refreshes it every 5 minutes, so an ISP address rotation heals
itself. The token lives in `/etc/duckdns/token` (root, 0600).

This is why the hostname now appears in `game/{server,client}/config/itlt.cfg`,
`website/src/components/ServerMonitor.tsx` and `website/src/content/text.json`
instead of a literal IP — those three used to go stale together on every rotation.

---

## Conventions worth keeping

- Changes are **additive**. Nothing that worked yesterday stops working; recipes
  are added, not removed. Where an item is buffed, the ingredient cost stays the
  same.
- Every gameplay change gets a **tooltip**. Nobody reads changelogs.
- Ore dictionary (`<ore:ingotSilver>`) for recipe *inputs* — UniDict is installed
  and unifies duplicates. Exact item IDs only for outputs.
- Verify shaped recipes for shape collisions across all scripts before shipping.
- Player-facing release notes live in `OldSchoolCraft-Update.md`.

**Do not add Fastcraft.** It conflicts with the existing mixin performance stack
(unimixins / gtnhlib / hodgepodge / archaicfix).
