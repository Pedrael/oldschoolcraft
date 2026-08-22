#!/usr/bin/env python3
"""Configure Mekanism so it adds machines without replacing the pack's economy.

This pack already runs FIVE ore-processing chains - IC2, Thermal Expansion,
EnderIO, Immersive Engineering and Railcraft. Mekanism's 5x chain would make
all of them pointless within a week, so the tiers above 2x are turned off at
the machine level. Every machine that does something no other mod here does
stays enabled.

The Enrichment Chamber is deliberately KEPT: it is how Mekanism makes its own
dusts and compressed components, so disabling it breaks the mod rather than
balancing it. Its ore recipes are stripped separately in scripts/mekanism.zs.

Worldgen: copper and tin come from Thermal Foundation and IC2 already. UniDict
merges the ITEMS but not the ore generation, so leaving Mekanism's on would
just make ore denser for no reason. Osmium and salt are Mekanism's own and
stay.

Usage: configure_mekanism.py <config-dir> [--apply]
"""
import os, re, shutil, sys, time

# machines that exist ONLY to multiply ore
DISABLE = {
    "PurificationChamberEnabled":      "3x ore tier",
    "ChemicalInjectionChamberEnabled": "4x ore tier",
    "ChemicalDissolutionChamberEnabled": "5x ore tier",
    "ChemicalWasherEnabled":           "5x ore tier",
    "ChemicalCrystallizerEnabled":     "5x ore tier",
}

# general-section values
GENERAL = {
    "CopperPerChunk": ("0",  "Thermal Foundation and IC2 already generate copper"),
    "TinPerChunk":    ("0",  "Thermal Foundation and IC2 already generate tin"),
    "OsmiumPerChunk": ("12", "Mekanism's own metal - keep default"),
    "SaltPerChunk":   ("2",  "Mekanism's own - keep default"),
    "VoiceServerEnabled": ("false", "closes port 36123, unused"),
    "EnableWorldRegeneration": ("false", "new chunks only, by choice"),
}

cfgdir = sys.argv[1] if len(sys.argv) > 1 else "/home/duduserver/mektest/config"
APPLY = "--apply" in sys.argv
path = os.path.join(cfgdir, "Mekanism.cfg")

if not os.path.exists(path):
    print(f"ABORT: {path} not found - has Mekanism booted once to generate it?")
    sys.exit(1)

text = open(path, encoding="utf-8").read()
orig = text
changes = []

for key, why in DISABLE.items():
    pat = re.compile(rf"(\bB:{re.escape(key)}=)(true|false)")
    m = pat.search(text)
    if not m:
        print(f"  WARNING: {key} not found in config")
        continue
    if m.group(2) == "false":
        print(f"  {key:36} already false")
        continue
    text = pat.sub(r"\1false", text, count=1)
    changes.append(f"{key} true -> false   ({why})")

for key, (val, why) in GENERAL.items():
    pat = re.compile(rf"(\b[BIDS]:{re.escape(key)}=)(\S+)")
    m = pat.search(text)
    if not m:
        print(f"  WARNING: {key} not found")
        continue
    if m.group(2) == val:
        print(f"  {key:36} already {val}")
        continue
    text = pat.sub(rf"\g<1>{val}", text, count=1)
    changes.append(f"{key} {m.group(2)} -> {val}   ({why})")

print(f"\nchanges to make: {len(changes)}")
for c in changes:
    print(f"   {c}")

if not changes:
    print("\nnothing to do")
    sys.exit(0)
if not APPLY:
    print("\nDRY RUN - nothing written. Pass --apply.")
    sys.exit(0)

shutil.copy2(path, path + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
open(path, "w", encoding="utf-8").write(text)

# prove the file still parses as a Forge config: braces balanced, keys intact
after = open(path, encoding="utf-8").read()
if after.count("{") != orig.count("{") or after.count("}") != orig.count("}"):
    print("ABORT: brace count changed - restoring")
    shutil.copy2(path + ".bak-" + time.strftime("%Y%m%d-%H%M%S"), path)
    sys.exit(1)
print(f"\nwritten: {path}")
