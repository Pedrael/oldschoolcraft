#!/usr/bin/env python3
"""Teach the armour auditor about Mekanism's five wearables.

Only the Gas Mask was picked up, and it was handed a METAL profile with
Air=0.00 - which is precisely backwards for a sealed breathing mask. The other
four were skipped entirely because slot() cannot infer a slot from names like
"ScubaTank" or "FreeRunners".

EnviroMine already ships enviromine:gasMask at Air=1.00, so the Mekanism mask
and the scuba tank simply match that precedent: thermally neutral, fully
sealed. The jetpacks and free runners are worn metal and get the metal profile.

Tuple order is (night, shade, sun, multNight, multShade, multSun, Air).
"""
import re, shutil, sys, time

PATH = "/home/duduserver/mctools/armour_coverage.py"
s = open(PATH, encoding="utf-8").read()
if "Mekanism:ScubaTank" in s:
    print("already patched"); sys.exit(0)

OLD = '''    "enviromine:hardHat":            (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 0.25),
}'''
NEW = '''    "enviromine:hardHat":            (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 0.25),
    # Mekanism wearables. The mask and tank are sealed breathing gear and get
    # the same treatment EnviroMine gives its own gas mask above; the auditor
    # would otherwise hand the mask a metal profile with no air protection at
    # all, which is exactly backwards.
    "Mekanism:GasMask":              (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 1.00),
    "Mekanism:ScubaTank":            (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 1.00),
    "Mekanism:Jetpack":              (-1.00, 0.00, 2.00, 1.00, 1.00, 1.10, 0.00),
    "Mekanism:ArmoredJetpack":       (-1.00, 0.00, 2.00, 1.00, 1.00, 1.10, 0.00),
    "Mekanism:FreeRunners":          (-1.00, 0.00, 2.00, 1.00, 1.00, 1.10, 0.00),
}'''
assert s.count(OLD) == 1, "SPECIAL anchor"
s = s.replace(OLD, NEW)

# slot() cannot guess these from their names; be specific so nothing else matches
OLD2 = '''    if re.search(r"boots|boot", n):                                          return "feet"'''
NEW2 = '''    if re.search(r"boots|boot|freerunners", n):                               return "feet"'''
assert s.count(OLD2) == 1, "feet anchor"
s = s.replace(OLD2, NEW2)

OLD3 = '''    if re.search(r"chestplate|chest|plate|robe|jerkin|tunic|vest|cuirass|overalls", n): return "chest"'''
NEW3 = '''    if re.search(r"chestplate|chest|plate|robe|jerkin|tunic|vest|cuirass|overalls|"
                 r"scubatank|jetpack", n): return "chest"'''
assert s.count(OLD3) == 1, "chest anchor"
s = s.replace(OLD3, NEW3)

shutil.copy2(PATH, PATH + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(PATH, "w", encoding="utf-8").write(s)
print("patched armour_coverage.py: 5 Mekanism wearables, mask + tank sealed at Air=1.00")
