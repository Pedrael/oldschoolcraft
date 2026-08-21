#!/usr/bin/env python3
"""Record the 2026-08-21 hang, the liveness check, and the loot system."""
import shutil, sys, time

PATH = "/home/duduserver/minecraft/1.7.10/CLAUDE.md"
t = open(PATH, encoding="utf-8").read()

if "mc-health" in t:
    print("already patched"); sys.exit(0)

edits = []

# -- the incident + liveness ------------------------------------------------
edits.append((
"## Rule zero: stop the server before editing anything\n",
"""## The 2026-08-21 hang: "active and listening" is not "working"

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
"""))

# -- loot system ------------------------------------------------------------
edits.append((
"## Scripts must match on client and server\n",
"""## The loot system

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
"""))

# -- tooling manifest additions --------------------------------------------
edits.append((
"| `mc-digest.py` | weekly | Deaths, causes, play hours, quest progress, unvisited dimensions - to chat and to `digest-latest.txt` |",
"""| `mc-digest.py` | weekly | Deaths, causes, play hours, quest progress, unvisited dimensions - to chat and to `digest-latest.txt` |
| `mc-health.py` | 5 min | Asserts the server actually serves: startup finished, log advancing, console answers. `--restart` acts on failure |
| `restore_leveldat.py` | on demand | Repairs a truncated `world/level.dat` from a verified rescue copy |

**Who is online, without asking.** `mc-lifesupport` and `mc-afk-guard` used to
run `list` on every tick - three times a minute, awake or not, which put ~5700
`Players currently online: [ 0 ]` lines a day into `latest.log` and is exactly
what made the hang unreadable. `mc-watcher` already sees every join and leave,
so it now publishes `~/mctools/online.json` and the timer scripts read that
file, falling back to `list` only if the roster is stale (meaning the watcher
is down). When nobody is online they now do nothing at all. `mc-watcher`
rebuilds the roster from the whole of `latest.log` on start, because it seeks
to the end of the file and would otherwise forget everyone already connected."""))

for old, new in edits:
    if t.count(old) != 1:
        print("ABORT: anchor matched %d times: %r" % (t.count(old), old[:60]))
        sys.exit(1)
    t = t.replace(old, new)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(t)
print("patched: %d sections, now %d lines" % (len(edits), t.count("\n") + 1))
