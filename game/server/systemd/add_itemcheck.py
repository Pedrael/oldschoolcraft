#!/usr/bin/env python3
"""Teach bq_lint to validate item ids against the world's own Forge registry.

An unknown id in a retrieval task makes the quest permanently uncompletable,
and an unknown id in a reward makes it unclaimable - both invisible until a
player is standing in front of it. Fear of exactly this is why the teaching
lines used checkbox tasks as a fallback, which is what caused the lockout. So
the linter should check it directly rather than have authors avoid the problem.

Also flags a quest with no tasks that gates another quest: it may never
complete, which would lock the chain the same way a checkbox does.
"""
import shutil, sys, time

PATH = "/home/duduserver/mctools/bq_lint.py"
s = open(PATH, encoding="utf-8").read()
if "registry" in s:
    print("already added"); sys.exit(0)

HELPERS = '''

def registry(level_dat="/home/duduserver/minecraft/1.7.10/world/level.dat"):
    """Every item id this world knows, read straight out of level.dat.

    Returns an empty set if it cannot be read, and callers must treat that as
    "cannot verify" rather than "everything is invalid" - level.dat has been
    truncated by an unclean shutdown before.
    """
    import gzip, re
    try:
        raw = gzip.decompress(open(level_dat, "rb").read())
    except Exception:
        return set()
    return set(m.decode("utf8", "replace") for m in
               re.findall(rb"[A-Za-z0-9_|]{2,32}:[A-Za-z0-9_.]{2,40}", raw))


def item_ids(q):
    """(context, id) for every item a quest requires or gives."""
    out = []
    for k, v in q.items():
        if k.startswith("tasks"):
            for _, tv in v.items():
                for rk, rv in tv.items():
                    if rk.startswith("requiredItems"):
                        for _, iv in rv.items():
                            if iv.get("id:8"):
                                out.append(("task", iv["id:8"]))
        if k.startswith("rewards"):
            for _, rv in v.items():
                for rk, rrv in rv.items():
                    if rk.startswith("rewards"):
                        for _, iv in rrv.items():
                            if iv.get("id:8"):
                                out.append(("reward", iv["id:8"]))
    return out
'''

s = s.replace("\ndef load(path):", HELPERS + "\n\ndef load(path):")

OLD = """    # 1. checkbox gates
    gates = sorted({p for q in entries for p in q.get(PRE, []) if is_checkbox(byid, p)})
    if gates:
        problems.append(f"checkbox quests used as prerequisites: {len(gates)}")"""

NEW = """    # 1. checkbox gates
    gates = sorted({p for q in entries for p in q.get(PRE, []) if is_checkbox(byid, p)})
    if gates:
        problems.append(f"checkbox quests used as prerequisites: {len(gates)}")

    # 5. unknown item ids - uncompletable tasks / unclaimable rewards
    reg = registry()
    bad_items = []
    if reg:
        for q in entries:
            for ctx, i in item_ids(q):
                if i not in reg:
                    bad_items.append((q["questID:3"], ctx, i))
        if bad_items:
            problems.append(f"unknown item ids: {len(bad_items)}")

    # 6. a task-less quest that gates another may never complete
    gating_empty = []
    for q in entries:
        ts = [tv for k, v in q.items() if k.startswith("tasks") for _, tv in v.items()]
        if ts:
            continue
        i = q["questID:3"]
        if any(i in x.get(PRE, []) for x in entries):
            gating_empty.append(i)
    if gating_empty:
        problems.append(f"task-less quests used as prerequisites: {gating_empty}")"""

if s.count(OLD) != 1:
    print("ABORT: anchor matched %d" % s.count(OLD)); sys.exit(1)
s = s.replace(OLD, NEW)

OLD2 = '''    say(f"   duplicate questIDs     : {len(dupes)}")'''
NEW2 = '''    say(f"   duplicate questIDs     : {len(dupes)}")
    say(f"   unknown item ids       : {len(bad_items)}"
        + ("" if reg else "   (registry unreadable - NOT verified)"))
    say(f"   task-less gates        : {len(gating_empty)}")
    if bad_items and not quiet:
        for qid, ctx, i in bad_items[:12]:
            say(f"      quest {qid} {ctx}: {i}")'''
if s.count(OLD2) != 1:
    print("ABORT: say anchor matched %d" % s.count(OLD2)); sys.exit(1)
s = s.replace(OLD2, NEW2)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("bq_lint now validates item ids and task-less gates")
