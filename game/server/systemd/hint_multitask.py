#!/usr/bin/env python3
"""Tell players when a quest has more than one task.

BetterQuesting shows ONE task at a time with a small pager beside the
Detect/Submit button. Vera hit "Kill Zombie 200/200" on The Long Patrol,
saw a full bar and a greyed-out Claim button, and reported it as broken.
She was on page 1 of 3 - skeletons and creepers were still owed.

Only two quests in the book have multiple tasks, so this just appends a
line to their descriptions saying so.

Run with the server STOPPED - BetterQuesting rewrites the database on
shutdown and would discard this.
"""
import json, shutil, subprocess, sys, time

DBF = "/home/duduserver/minecraft/1.7.10/world/betterquesting/QuestDatabase.json"
APPLY = "--apply" in sys.argv

MARK = "§7This quest has"          # idempotency marker

state = subprocess.run(["systemctl", "is-active", "minecraft"],
                       capture_output=True, text=True).stdout.strip()
if state == "active" and APPLY:
    print("ABORT: minecraft is running - BQ would discard this on shutdown")
    sys.exit(1)
print(f"server: {state}\n")

raw = json.load(open(DBF, encoding="utf-8"))
db = raw["questDatabase:9"]

changed = 0
for q in db.values():
    tasks = [tv for k, v in q.items() if k.startswith("tasks") for _, tv in v.items()]
    if len(tasks) < 2:
        continue
    for k, v in q.items():
        if not k.startswith("properties"):
            continue
        for _, pp in v.items():
            if not isinstance(pp, dict):
                continue
            d = pp.get("desc:8", "")
            nm = pp.get("name:8", "?")
            if MARK in d:
                print(f"  {nm}: already hinted")
                continue
            n = len(tasks)
            hint = (f"\n\n§7This quest has §e{n} separate tasks§7. "
                    f"The book shows one at a time — use the §e›§7 arrow "
                    f"beside Detect/Submit to see the rest. The reward unlocks only "
                    f"when §eall {n}§7 are done.§r")
            print(f"  {nm}: adding hint ({n} tasks)")
            changed += 1
            if APPLY:
                pp["desc:8"] = d + hint

print(f"\ndescriptions changed: {changed}")
if not APPLY:
    print("DRY RUN - nothing written. Pass --apply.")
    sys.exit(0)

stamp = time.strftime("%Y%m%d-%H%M%S")
shutil.copy2(DBF, f"{DBF}.bak-{stamp}")
json.dump(raw, open(DBF, "w", encoding="utf-8"), indent=1)
json.load(open(DBF, encoding="utf-8"))
print(f"written and re-read OK. backup: QuestDatabase.json.bak-{stamp}")
