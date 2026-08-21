#!/usr/bin/env python3
"""Record the checkbox-gate trap and how BetterQuesting parties share progress."""
import shutil, sys, time

PATH = "/home/duduserver/minecraft/1.7.10/CLAUDE.md"
t = open(PATH, encoding="utf-8").read()

if "checkbox quest as a prerequisite" in t:
    print("already patched"); sys.exit(0)

OLD = """Task types in use here: `bq_standard:retrieval`, `checkbox`, `hunt`.
Rewards: `bq_standard:item` and `bq_standard:xp`."""

NEW = """Task types in use here: `bq_standard:retrieval`, `checkbox`, `hunt`.
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
but no `completed` entry is the locked-but-ticked state described above."""

if t.count(OLD) != 1:
    print("ABORT: anchor matched %d times" % t.count(OLD)); sys.exit(1)
t = t.replace(OLD, NEW)

OLD2 = "| `restore_leveldat.py` | on demand | Repairs a truncated `world/level.dat` from a verified rescue copy |"
NEW2 = OLD2 + "\n| `unblock_checkbox_gates.py` | on demand | Splices checkbox quests out of the prerequisite graph and ticks the ones that were gating |"
if t.count(OLD2) != 1:
    print("ABORT: tooling anchor matched %d times" % t.count(OLD2)); sys.exit(1)
t = t.replace(OLD2, NEW2)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(t)
print("patched, now %d lines" % (t.count("\n") + 1))
