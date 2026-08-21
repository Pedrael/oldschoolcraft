#!/usr/bin/env python3
"""Food that changes your body temperature.

EnviroMine's items{} section already supports this and nothing in the pack uses
it. The semantics, read off the vanilla entries rather than guessed:

    Effect Temperature      the RATE the effect pulls you at
    Effect Temperature Cap  the DESTINATION it pulls you toward (37.0 = normal)
    Effect Hydration        0-100 scale; apple 5.0, water bottle 25.0

So a water bottle is rate -0.1 toward cap 37: it cools you, but never below
normal. Chilli is the same idea pointed the other way -- a positive rate and a
cap ABOVE 37. The cap, not the rate, decides how hot you can get, which makes
it the safety lever.

Heat Stroke and Hypothermia are both enabled on this server and both are lethal
(the mod ships death messages for them). EnviroMine's documented thresholds are
roughly 40C hot and 32C cold, so only the EXTREME tier is placed past the line
-- deliberately, so eating extreme chilli in a desert is a real mistake.

Run with the server STOPPED.
"""
import glob, gzip, os, re, sys

ROOT = "/home/duduserver/minecraft/1.7.10"
CP   = f"{ROOT}/config/enviromine/profiles/default/CustomProperties"
LVL  = f"{ROOT}/world/level.dat"

#            rate,  cap,  hydration, colour,        tooltip
TIERS = {
 "extreme": (0.50, 42.0,  0.0, "darkRed",     "Dangerously hot. This can give you heat stroke."),
 "hot":     (0.30, 40.0,  0.0, "red",         "Warms you up fast. Good before a cold night."),
 "soup":    (0.20, 39.0,  8.0, "gold",        "Warming, and a little hydrating."),
 "warming": (0.20, 39.0,  6.0, "gold",        "Warms you gently."),
 "chilled": (-0.20, 34.0, 20.0, "aqua",       "Cools you down and hydrates well."),
 "frozen":  (-0.30, 33.0, 10.0, "darkAqua",   "Cools you hard. Careful in the cold."),
}

# order matters: first match wins
RULES = [
 ("extreme", r"^extremechili$"),
 ("hot",     r"chili|curry|jalapeno|wasabi|horseradish|spicy"),
 ("warming", r"ginger|cinnamon|coffee|chai|cocoa|hotchocolate|mulled"),
 ("soup",    r"soup|stew|chowder|broth|ramen|porridge|oatmeal|gumbo"),
 ("frozen",  r"icecream|milkshake|popsicle|sorbet|sundae|gelato"),
 ("chilled", r"smoothie|yogurt|juice|cider|lemonade|limeade|soda|punch"),
]

EXTRA = {   # outside HarvestCraft
 "ThaumicHorizons:iceCream": "frozen",
 "MoCreatures:turtlesoup":   "soup",
 "Natura:natura.stewbowl":   "soup",
 "IC2:itemMugCoffee":        "warming",
}

TMPL = """
    {key} {{
        S:01.Name={ident}
        I:02.Damage=-1
        B:"03.Enable Ambient Temperature"=false
        D:"04.Ambient Temperature"=0.0
        D:"05.Ambient Air Quality"=0.0
        D:"06.Ambient Santity"=0.0
        D:"07.Effect Temperature"={rate}
        D:"08.Effect Air Quality"=0.0
        D:"09.Effect Sanity"=0.0
        D:"10.Effect Hydration"={hyd}
        D:"11.Effect Temperature Cap"={cap}
        I:"12.CamelPack Fill Amount"=0
        S:"13.CamelPack Return Item"=
        I:"14.CamelPack Return Meta"=0
    }}
"""


def registry(kind=b"\x02"):
    d = gzip.decompress(open(LVL, "rb").read())
    return {n.decode() for k, n in re.findall(
        rb"([\x01\x02])([A-Za-z][A-Za-z0-9_]{1,30}:[A-Za-z0-9_.\-]{2,48})", d) if k == kind}


def classify():
    items, blocks = registry(), registry(b"\x01")
    out = {}
    for x in sorted(items):
        if x in EXTRA:
            out[x] = EXTRA[x]; continue
        if not x.startswith("harvestcraft:") or not x.endswith("Item"):
            continue
        if x in blocks:
            continue
        n = x.split(":", 1)[1][:-4].lower()
        if re.search(r"seed|sapling|crop", n):
            continue
        for tier, pat in RULES:
            if re.search(pat, n):
                out[x] = tier
                break
    return out


def read(p):
    if not os.path.exists(p): return "# Configuration file\n\n", "\n"
    raw = open(p, "rb").read()
    return raw.decode("utf-8", "replace").replace("\r\n", "\n"), ("\r\n" if b"\r\n" in raw else "\n")


def cfg_for(mod, files):
    for f in files:
        if f[:-4] == mod: return f
    for f in files:
        if f[:-4].lower() == mod.lower(): return f
    return f"{mod}.cfg"


def add_section(text, section, entries):
    body = "".join(entries)
    m = re.search(rf"^{section} \{{$", text, re.M)
    if not m: return text.rstrip("\n") + f"\n\n{section} {{\n{body}}}\n"
    s = m.end(); c = re.search(r"^\}$", text[s:], re.M)
    return text[:s + c.start()] + body + text[s + c.start():]


def main():
    apply = "--apply" in sys.argv
    tiers = classify()
    files = sorted(f for f in os.listdir(CP) if f.endswith(".cfg"))

    by_file, counts = {}, {}
    for ident, tier in tiers.items():
        counts[tier] = counts.get(tier, 0) + 1
        by_file.setdefault(cfg_for(ident.split(":", 1)[0], files), []).append((ident, tier))

    added = 0
    for f, items in sorted(by_file.items()):
        path = os.path.join(CP, f)
        text, nl = read(path)
        new = []
        for ident, tier in sorted(items):
            if f"S:01.Name={ident}\n" in text:
                continue
            rate, cap, hyd, _, _ = TIERS[tier]
            key = "item_" + re.sub(r"[^A-Za-z0-9]+", "_", ident.split(":", 1)[1]).strip("_").lower()
            new.append(TMPL.format(key=key, ident=ident, rate=f"{rate:.3f}",
                                   cap=f"{cap:.1f}", hyd=f"{hyd:.1f}"))
        if new:
            text = add_section(text, "items", new)
            if apply:
                open(path, "wb").write(text.replace("\n", nl).encode("utf-8"))
            added += len(new)
            print(f"  {f}: +{len(new)}")

    print(("\nAPPLIED " if apply else "\nDRY RUN ") + f"{added} food entries")
    print("\n  by tier:")
    for t, n in sorted(counts.items(), key=lambda x: -x[1]):
        rate, cap, hyd, _, _ = TIERS[t]
        print(f"    {t:8} {n:>4}   rate {rate:+.2f} -> cap {cap:.1f}C   hydration {hyd:.0f}")

    if "--tooltips" in sys.argv:
        with open(f"{ROOT}/scripts/food.zs", "w") as fh:
            print("// ======================================================================", file=fh)
            print("//  food.zs - GENERATED by food_temperature.py. Do not hand-edit.", file=fh)
            print("//  Food now changes body temperature; these say so. Tooltips come from", file=fh)
            print("//  the client's own copy, so this file must be on every client.", file=fh)
            print("// ======================================================================", file=fh)
            for ident, tier in sorted(tiers.items()):
                _, _, _, col, txt = TIERS[tier]
                print(f'<{ident}>.addTooltip(format.{col}("{txt}"));', file=fh)
        print(f"\n  wrote scripts/food.zs ({len(tiers)} tooltips)")


if __name__ == "__main__":
    main()
