import shutil, sys, time
PATH="/home/duduserver/minecraft/1.7.10/CLAUDE.md"
t=open(PATH,encoding="utf-8").read()
if "## Death insurance" in t: print("already patched"); sys.exit(0)
NEW = """## Death insurance (added 2026-08-24)

Pay gold coins on death to keep your inventory, or take the grave as before.
Two problems, one mechanic: graves are a chore, and `Thaumcraft:ItemResource:18`
(Gold Coin) was a currency nobody had a reason to pick up - 788 sat in chests
while all three players carried a combined total of one.

`~/mctools/mc-deathtoll.py`, launched by `mc-watcher` on every death. Armed by
the presence of `~/mctools/deathtoll.armed`; delete it to stop instantly, no
restart.

**Order matters and is the whole design:**

```
respawn proven -> grave still there? -> clear it -> take fee -> restore -> did it land?
```

- **Respawn must be PROVEN.** `player_alive()` originally read playerdata off
  disk, and Minecraft does not write that file on death. Four seconds after a
  death it still said "health 20", so the restore fired into the death screen
  and the inventory was destroyed. `respawned()` now forces `save-all` and
  refuses to trust the file unless its mtime is **newer than the death**.
- **Grave still there?** If it has gone, the player looted it during the wait.
  Restoring on top of that duplicates everything. Nothing is charged.
- **Clear before restoring.** Leaving the grave lootable until after the
  restore is the duplication window. A failed restore is recoverable -
  the snapshot file is never deleted and `/ob_inventory spawn <id>` still
  works - so clearing first is the safer order, not the riskier one.
- **Verify the outcome, not the command.** `Restored inventory for player X`
  is logged even when the items go nowhere. The inventory is read back; if it
  is empty the fee is refunded and the grave is left alone.

**Payment is made by editing the snapshot, never with `/clear`.** 1.7.10's
`/clear` is `<player> [item] [data]` with **no count argument** - it would take
every coin the player owns.

**It disarms itself.** Any outcome that could cost somebody items
(`restore-failed`, `grave-stuck`, `charge-failed`, `no-location`, any unhandled
exception) deletes the armed flag, announces it in chat, and lets later deaths
fall through to ordinary graves. Outcomes where the player simply keeps their
grave (`unpaid`, `no-respawn`, `already-looted`) do **not** trip it - a breaker
that fires on harmless outcomes is one people switch off.

Price is `ceil(value / DIVISOR)` clamped to 1-48, `DIVISOR = 20`. Value is a
coarse tier model in the script; worn armour and held tools count double. A
full kit prices around 22 coins, an empty-handed death at the floor of 1.

`mc-deathtoll.py --quote` prints what dying would cost each player right now,
without anybody having to die.

**Test environments get dirty.** After a clean test a player held 82 items more
than his own death snapshot. It was not the mechanic - the grave had captured
all 38 stacks, and the surplus was debris from an earlier failure lying on the
ground, including 33 loose gold coins, which he walked over. Check the ground
before blaming the code.

---

"""
A="## The loot system\n"
assert t.count(A)==1
open(PATH,"w",encoding="utf-8").write(t.replace(A,NEW+A))
print("patched, now %d lines" % (t.count("\n")+1))
