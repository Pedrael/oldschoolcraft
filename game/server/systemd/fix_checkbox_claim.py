#!/usr/bin/env python3
"""Correct the claim that a checkbox quest 'self-ticks'.

It does not, and that single wrong belief is the root of the 2026-08-21
lockout: the teaching lines used checkbox tasks as safe fallbacks, chained
each quest to the previous one, and so gated every chapter behind a click
nobody knew they had to make.
"""
import shutil, sys, time

PATH = "/home/duduserver/minecraft/1.7.10/CLAUDE.md"
t = open(PATH, encoding="utf-8").read()

OLD = """- **When unsure, use `bq_standard:checkbox`.** A quest that self-ticks and
  explains something still teaches. A quest nobody can finish is worse than no
  quest at all."""

NEW = """- **When unsure, use `bq_standard:checkbox` — but never as a prerequisite.**
  A quest nobody can finish is worse than no quest at all, so a checkbox is the
  right fallback wherever an item's metadata cannot be verified. **It does not
  self-tick.** An earlier version of this file claimed it did; that was wrong,
  and building the teaching lines on it locked 37 quests for one player and 27
  for another. Somebody has to open the quest and click. Retrieval tasks *do*
  detect passively, so players never learn that some quests need a click —
  there is no pattern for them to notice. Keep checkboxes out of
  `preRequisites` entirely and the mistake cannot recur."""

if NEW.split("\n")[0] in t:
    print("already corrected"); sys.exit(0)
if t.count(OLD) != 1:
    print("ABORT: anchor matched %d times" % t.count(OLD)); sys.exit(1)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(t.replace(OLD, NEW))
print("corrected the self-ticks claim")
