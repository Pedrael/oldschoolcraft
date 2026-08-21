#!/usr/bin/env python3
"""Stop informational checkbox quests from silently locking whole chapters.

The teaching lines open with a bq_standard:checkbox quest - "read this, then
tick it". Those openers were also made prerequisites for the rest of the
chapter. BetterQuesting's RETRIEVAL tasks auto-detect items in a player's
inventory even while the quest is LOCKED, so a player who never clicked the
opener sees every downstream task ticked green with no Claim button. That is
indistinguishable from a broken quest, and it is what Vera and Cube both hit.

Two changes:

  1. SPLICE - any checkbox quest used as a prerequisite is replaced by its own
     prerequisites, recursively. Real ordering between real quests is kept;
     the checkbox simply stops being a gate.

  2. TICK - the checkbox quests that were gating get marked complete for all
     three players, with claimed:0 so the reward is still theirs to collect.

Run with the server STOPPED: BetterQuesting rewrites both files on shutdown
and would discard anything written underneath it.
"""
import json, shutil, subprocess, sys, time

BQ    = "/home/duduserver/minecraft/1.7.10/world/betterquesting"
DBF   = f"{BQ}/QuestDatabase.json"
PROGF = f"{BQ}/QuestProgress.json"

PLAYERS = {
    "e25c57a0-617f-48cd-adab-b4c2659698f0": "Dudu",
    "e5f0d7dc-6196-4e68-8733-ffc8e21b84fe": "Vera",
    "e95d535b-8749-4c77-b161-75b953f01609": "Cube",
}
APPLY = "--apply" in sys.argv

state = subprocess.run(["systemctl", "is-active", "minecraft"],
                       capture_output=True, text=True).stdout.strip()
if state == "active" and APPLY:
    print("ABORT: minecraft is running - BetterQuesting would discard this on shutdown")
    sys.exit(1)
print(f"server: {state}\n")

db_raw   = json.load(open(DBF, encoding="utf-8"))
prog_raw = json.load(open(PROGF, encoding="utf-8"))
db, prog = db_raw["questDatabase:9"], prog_raw["questProgress:9"]

byid = {v["questID:3"]: v for v in db.values()}
pbyid = {v["questID:3"]: v for v in prog.values()}


def name(q):
    for k, v in q.items():
        if k.startswith("properties"):
            for _, pp in v.items():
                if isinstance(pp, dict):
                    return pp.get("name:8", "?")
    return "?"


def is_checkbox(qid):
    q = byid.get(qid)
    if not q:
        return False
    tasks = [tv.get("taskID:8") for k, v in q.items() if k.startswith("tasks")
             for _, tv in v.items()]
    return bool(tasks) and all(t == "bq_standard:checkbox" for t in tasks)


PRE = "preRequisites:11"

# which checkbox quests currently act as gates
gating = sorted({p for q in byid.values() for p in q.get(PRE, []) if is_checkbox(p)})
print(f"checkbox quests acting as gates: {len(gating)}")
for g in gating:
    print(f"   {g:4} {name(byid[g])}")


def resolve(qid, seen=None):
    """Replace a checkbox prerequisite with its own prerequisites, recursively."""
    seen = seen or set()
    if qid in seen:
        return []
    seen.add(qid)
    if not is_checkbox(qid):
        return [qid]
    out = []
    for p in byid.get(qid, {}).get(PRE, []):
        for r in resolve(p, seen):
            if r not in out:
                out.append(r)
    return out


# ---- 1. splice -----------------------------------------------------------
spliced = 0
for q in db.values():
    old = q.get(PRE)
    if not old:
        continue
    new = []
    for p in old:
        for r in resolve(p):
            if r not in new:
                new.append(r)
    if new != old:
        spliced += 1
        if APPLY:
            q[PRE] = new

print(f"\nquests whose prerequisites change: {spliced}")

# ---- 2. tick the gates ---------------------------------------------------
now = int(time.time() * 1000)
ticked = {n: 0 for n in PLAYERS.values()}

for qid in gating:
    e = pbyid.get(qid)
    if e is None:
        continue
    for _, tv in e.get("tasks:9", {}).items():
        cu = tv.setdefault("completeUsers:9", {})
        have = set(cu.values())
        nxt = len(cu)
        for uuid, who in PLAYERS.items():
            if uuid not in have:
                if APPLY:
                    cu[f"{nxt}:8"] = uuid
                nxt += 1
    comp = e.setdefault("completed:9", {})
    have = {c.get("uuid:8") for c in comp.values()}
    nxt = len(comp)
    for uuid, who in PLAYERS.items():
        if uuid not in have:
            ticked[who] += 1
            if APPLY:
                # claimed:0 - the reward is still theirs to collect
                comp[f"{nxt}:10"] = {"claimed:1": 0, "uuid:8": uuid, "timestamp:4": now}
            nxt += 1

print("\ncheckbox quests newly ticked (reward left unclaimed):")
for who, n in ticked.items():
    print(f"   {who:6} {n}")

if not APPLY:
    print("\nDRY RUN - nothing written. Pass --apply.")
    sys.exit(0)

stamp = time.strftime("%Y%m%d-%H%M%S")
shutil.copy2(DBF, f"{DBF}.bak-{stamp}")
shutil.copy2(PROGF, f"{PROGF}.bak-{stamp}")
json.dump(db_raw, open(DBF, "w", encoding="utf-8"), indent=1)
json.dump(prog_raw, open(PROGF, "w", encoding="utf-8"), indent=1)

# read back
json.load(open(DBF, encoding="utf-8"))
json.load(open(PROGF, encoding="utf-8"))
print(f"\nwritten and re-read OK. backups: *.bak-{stamp}")
