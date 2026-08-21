#!/usr/bin/env python3
"""Correct an over-broad claim about MineTweaker arrays/loops.

fortune.zs iterates `string[]` with `for` and loads with zero errors, so the
blanket "no arrays and no loops" is wrong. What actually fails is IItemStack[].
"""
import sys

PATH = "/home/duduserver/minecraft/1.7.10/CLAUDE.md"
t = open(PATH, encoding="utf-8").read()

OLD = """MineTweaker3 has **no arrays and no loops** - it rejects them with
"could not find type IItemStack" or "any values not yet supported". Everything
must be flat statements, which is why these two scripts are generated."""

NEW = """MineTweaker3 arrays and `for` loops **do work** - `fortune.zs` declares
`string[]` loot-category lists and iterates them, and loads with zero errors.
What it rejects is `as IItemStack[]` ("could not find type IItemStack") and
`any` values, so a list of *items* cannot be built or looped over. That is the
whole reason `armour.zs` and `food.zs` are generated as flat statements while
`fortune.zs` can loop over category names by hand."""

if NEW.split("\n")[0] in t:
    print("already corrected"); sys.exit(0)
if t.count(OLD) != 1:
    print("ABORT: anchor matched %d times" % t.count(OLD)); sys.exit(1)

open(PATH, "w", encoding="utf-8").write(t.replace(OLD, NEW))
print("corrected the arrays/loops claim")
