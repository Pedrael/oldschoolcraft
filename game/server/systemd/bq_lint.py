#!/usr/bin/env python3
"""Check a BetterQuesting database for the faults that silently break a book.

Import it from a generator and call check(path) as the last step, or run it
directly:

    bq_lint.py <QuestDatabase.json|DefaultQuests.json> [--fix]

Checks:

  1. CHECKBOX GATES - a bq_standard:checkbox quest used as a prerequisite.
     Checkbox tasks do NOT self-complete; somebody has to open the quest and
     click. Retrieval tasks detect passively, so players never learn that
     some quests need a click. A checkbox in preRequisites therefore locks a
     whole chapter while still showing its tasks ticked green, which reads as
     broken quest data rather than as an unmet prerequisite. This is what
     locked 37 quests for one player and 27 for another on 2026-08-21.
     --fix splices them out: downstream quests inherit the checkbox's own
     prerequisites, so ordering between real quests survives.

  2. DANGLING PREREQUISITES - a preRequisite pointing at a quest that does
     not exist. Locks the quest forever with no way to tell from in-game.

  3. SELF/CYCLIC PREREQUISITES - a quest that gates itself, directly or
     through a loop. Same effect.

  4. DUPLICATE questIDs - BetterQuesting matches progress to quests by
     questID, so a duplicate silently merges two quests' progress.

Exit code is 0 when clean, 1 when something is wrong, so a generator can
simply refuse to ship.
"""
import json, shutil, sys, time

PRE = "preRequisites:11"


def load(path):
    # BetterQuesting writes DefaultQuests.json with a UTF-8 BOM
    with open(path, encoding="utf-8-sig") as f:
        raw = json.load(f)
    for k, v in raw.items():
        if "questDatabase" in k:
            return raw, k, v
    raise ValueError("no questDatabase key found")


def is_checkbox(byid, qid):
    q = byid.get(qid)
    if not q:
        return False
    ts = [tv.get("taskID:8") for k, v in q.items() if k.startswith("tasks")
          for _, tv in v.items()]
    return bool(ts) and all(t == "bq_standard:checkbox" for t in ts)


def name(q):
    for k, v in q.items():
        if k.startswith("properties"):
            for _, pp in v.items():
                if isinstance(pp, dict):
                    return pp.get("name:8", "?")
    return "?"


def check(path, fix=False, quiet=False):
    raw, key, db = load(path)
    entries = list(db.values())
    byid = {q["questID:3"]: q for q in entries}
    problems = []

    def say(*a):
        if not quiet:
            print(*a)

    # 4. duplicate questIDs
    seen, dupes = set(), set()
    for q in entries:
        i = q["questID:3"]
        if i in seen:
            dupes.add(i)
        seen.add(i)
    if dupes:
        problems.append(f"duplicate questIDs: {sorted(dupes)}")

    # 2/3. dangling, self, cyclic
    dangling, selfref = [], []
    for q in entries:
        i = q["questID:3"]
        for p in q.get(PRE, []):
            if p not in byid:
                dangling.append((i, p))
            if p == i:
                selfref.append(i)
    if dangling:
        problems.append(f"dangling prerequisites: {dangling[:10]}")
    if selfref:
        problems.append(f"self-referencing prerequisites: {selfref[:10]}")

    def cyclic(start):
        seen_, stack = set(), [start]
        while stack:
            cur = stack.pop()
            if cur == start and seen_:
                return True
            if cur in seen_:
                continue
            seen_.add(cur)
            stack.extend(byid.get(cur, {}).get(PRE, []))
        return False

    cycles = sorted({i for i in byid if any(cyclic(p) for p in byid[i].get(PRE, []))})
    if cycles:
        problems.append(f"cyclic prerequisites: {cycles[:10]}")

    # 1. checkbox gates
    gates = sorted({p for q in entries for p in q.get(PRE, []) if is_checkbox(byid, p)})
    if gates:
        problems.append(f"checkbox quests used as prerequisites: {len(gates)}")

    say(f"{path}")
    say(f"   quests                 : {len(entries)}")
    say(f"   checkbox gates         : {len(gates)}")
    say(f"   dangling prerequisites : {len(dangling)}")
    say(f"   cyclic / self          : {len(cycles) + len(selfref)}")
    say(f"   duplicate questIDs     : {len(dupes)}")

    if gates and not quiet:
        for g in gates:
            say(f"      gate {g}: {name(byid[g])}")

    if not fix or not gates:
        if problems and not quiet:
            say("\n   PROBLEMS:")
            for p in problems:
                say(f"      - {p}")
        return (0 if not problems else 1), problems

    # ---- fix: splice checkbox quests out of the prerequisite graph ----
    def resolve(qid, seen_=None):
        seen_ = seen_ or set()
        if qid in seen_:
            return []
        seen_.add(qid)
        if not is_checkbox(byid, qid):
            return [qid]
        out = []
        for p in byid.get(qid, {}).get(PRE, []):
            for r in resolve(p, seen_):
                if r not in out:
                    out.append(r)
        return out

    changed = 0
    for q in entries:
        old = q.get(PRE)
        if not old:
            continue
        new = []
        for p in old:
            for r in resolve(p):
                if r not in new:
                    new.append(r)
        if new != old:
            q[PRE] = new
            changed += 1

    stamp = time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, f"{path}.bak-{stamp}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=1)
    load(path)  # re-read to prove it parses
    say(f"\n   FIXED: {changed} quests re-linked. backup: {path}.bak-{stamp}")
    return 0, []


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    rc, _ = check(args[0], fix="--fix" in sys.argv)
    sys.exit(rc)
