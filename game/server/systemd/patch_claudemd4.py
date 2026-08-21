#!/usr/bin/env python3
"""Document bq_lint and the three places the checkbox trap could return."""
import shutil, sys, time

PATH = "/home/duduserver/minecraft/1.7.10/CLAUDE.md"
t = open(PATH, encoding="utf-8").read()
if "bq_lint" in t:
    print("already patched"); sys.exit(0)

OLD = """The fix, and the rule going forward: a checkbox may be *content*, never a
*gate*. `~/mctools/unblock_checkbox_gates.py` splices any checkbox quest out of
the prerequisite graph - downstream quests inherit the checkbox's own
prerequisites, so real ordering between real quests survives - and ticks the
offending boxes with `claimed:0` so the reward is still the player's to collect.
Run it with the server **stopped**."""

NEW = """The fix, and the rule going forward: a checkbox may be *content*, never a
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
confirming the linter catches and repairs it."""

if t.count(OLD) != 1:
    print("ABORT: anchor matched %d times" % t.count(OLD)); sys.exit(1)
t = t.replace(OLD, NEW)

OLD2 = "| `unblock_checkbox_gates.py` | on demand | Splices checkbox quests out of the prerequisite graph and ticks the ones that were gating |"
NEW2 = OLD2 + "\n| `bq_lint.py` | after any quest edit | Validates a quest graph: checkbox gates, dangling/cyclic prerequisites, duplicate questIDs. `--fix` repairs. Generators call it automatically |"
if t.count(OLD2) != 1:
    print("ABORT: tooling anchor matched %d" % t.count(OLD2)); sys.exit(1)
t = t.replace(OLD2, NEW2)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(t)
print("patched, now %d lines" % (t.count("\n") + 1))
