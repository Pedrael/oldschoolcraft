#!/usr/bin/env python3
"""Tune Special Mobs down so it does not stack with Infernal Mobs.

Each *_rates section is a weighted table: _vanilla against one weight per
variant. Stock is _vanilla=30 against ~14 variants at 1, so ~32% of spawns are
special. This server already runs Infernal Mobs (roughly 1 in 15 hostile mobs
is Elite or better) with Regen and 1UP deliberately disabled because fights
became unwinnable. Two independent modifier systems both firing on a third of
mobs is how you get that back.

Target: ~10% special, i.e. _vanilla = 9 x (number of variants).

spawn_eggs stays false on purpose - it would consume 106 global entity IDs in a
pack running 167 mods.
"""
import re, sys

CFG = "/home/duduserver/minecraft/1.7.10/config/SpecialMobs.cfg"
TARGET = 0.10

apply = "--apply" in sys.argv
text = open(CFG).read()
out, changes = text, []

for sec in re.finditer(r"^(\w+_rates) \{$(.*?)^\}$", text, re.S | re.M):
    name, body = sec.group(1), sec.group(2)
    variants = [m for m in re.findall(r"^\s+I:(?!_vanilla)(\w+)=(\d+)$", body, re.M)]
    cur = re.search(r"^\s+I:_vanilla=(\d+)$", body, re.M)
    if not variants or not cur:
        continue
    nvar = sum(int(v) for _, v in variants)
    old = int(cur.group(1))
    new = max(1, round(nvar * (1 - TARGET) / TARGET))
    pct_old = nvar / (nvar + old) * 100
    pct_new = nvar / (nvar + new) * 100
    changes.append((name, len(variants), old, new, pct_old, pct_new))
    out = out.replace(f"{name} {{{body}}}",
                      f"{name} {{{re.sub(r'(^\s+I:_vanilla=)\d+$', lambda m: m.group(1)+str(new), body, flags=re.M)}}}")

# keep ordinary mobs ordinary where the option exists
n_av = len(re.findall(r"B:_allow_vanilla=false", out))
out = out.replace("B:_allow_vanilla=false", "B:_allow_vanilla=true")

print(("APPLIED" if apply else "DRY RUN") + f"  target {TARGET*100:.0f}% special\n")
print(f"{'section':22}{'variants':>9}{'vanilla':>9}{'->':>4}{'new':>7}{'special%':>10}{'->':>4}{'new%':>7}")
for n, c, o, w, po, pn in changes:
    print(f"{n:22}{c:>9}{o:>9}{'->':>4}{w:>7}{po:>9.0f}%{'->':>4}{pn:>6.0f}%")
print(f"\n_allow_vanilla flipped to true in {n_av} sections (ordinary mobs stay ordinary)")
print(f"spawn_eggs left at: {re.search(r'B:spawn_eggs=(\w+)', out).group(1)}  (false saves 106 entity IDs)")

if apply:
    import shutil, time
    shutil.copy2(CFG, CFG + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
    open(CFG, "w").write(out)
    print("\nwritten")
