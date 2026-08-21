#!/usr/bin/env python3
"""Full EnviroMine coverage for every armour piece in the pack.

Policy: HALF-STRENGTH material flavour. Same directions as vanilla's own model
(metal cold at night and hot in sun, cloth insulating, dense damping) at roughly
half the magnitude -- so every set gets character without compounding the
BodyTemp increase, which has no play data behind it yet.

Vanilla's model, for reference:
    leather  +1.0 / +1.0 / +1.0   mults 1.00
    iron     -1.0 /  0.0 / +2.0   xSun 1.10
    gold      0.0 /  0.0 / +2.5   xSun 1.20
    diamond   0.0 /  0.0 /  0.0   xSun 0.90

Everything here stays inside the established envelope: adds -1.00..+2.50,
multipliers 0.80..1.20, air 0.00..1.00 per piece.

Sets we deliberately tuned are PROTECTED and never rewritten. Chestplates added
in the earlier pass carry neutral values, so they ARE rewritten to their
material profile -- otherwise a thaumium helmet would behave differently from a
thaumium chestplate.

Run with the server STOPPED.
"""
import gzip, glob, os, re, shutil, sys, time

ROOT = "/home/duduserver/minecraft/1.7.10"
CP   = f"{ROOT}/config/enviromine/profiles/default/CustomProperties"
LVL  = f"{ROOT}/world/level.dat"

# (night, shade, sun, xNight, xShade, xSun, air)
# FULL vanilla strength. Half-strength was tried first and was a mistake:
# biome ambient temperature on this server spans -7.4C to +45C, a 52C range,
# so a full set of half-strength cloth moved the needle 2C -- about 4% of the
# span, which players correctly reported as doing nothing.
#
# Multipliers matter more than adds for "fighting the climate": an add is a flat
# offset, a multiplier scales with how extreme the biome actually is. Cloth now
# insulates (damping multipliers) rather than only trickling warmth in.
ROBE   = (1.75, 1.25, 1.00, 0.88, 0.94, 1.05, 0.00)   # magic cloth: rivals nickel at night
CLOTH  = (1.25, 1.00, 1.00, 0.90, 0.95, 1.05, 0.00)   # ordinary fabric, insulating
METAL  = (-1.00, 0.00, 2.00, 1.00, 1.00, 1.10, 0.00)  # vanilla iron
GOLDY  = (0.00, 0.00, 2.50, 1.00, 1.00, 1.20, 0.00)   # vanilla gold
DENSE  = (0.00, 0.00, 0.00, 1.00, 1.00, 0.90, 0.00)   # vanilla diamond
FIRE   = (1.00, 0.50, -1.00, 1.00, 0.92, 0.85, 0.00)  # nether: warm, sheds sun
def SEALED(slot):                                      # boron/lead: shielded
    return (1.00, 0.50, 0.00, 1.00, 1.00, 1.00, 0.50 if slot == "head" else 0.25)

# Never touched -- deliberately designed elsewhere
# Only the sets that were deliberately tuned. An earlier, broader pattern also
# shielded four Thermal Foundation sets and vanilla chainmail that nobody had
# ever tuned, leaving 15 pieces with no entry while their chestplates had one.
PROTECTED = re.compile(
    r"^(ThermalFoundation:armor\.\w*(Copper|Tin|Lead|Nickel|Invar)$"
    r"|minecraft:(leather|iron|golden|diamond)_"
    r"|millenaire:item\.ml_(byzantine|norman|japaneseGuard|japaneseWarriorBlue|japaneseWarriorRed)"
    r"|IC2:itemArmorHazmat"
    r"|MoCreatures:(scorp|fur|hide))", re.I)

# Explicit overrides, applied before material matching
SPECIAL = {
    "enviromine:gasMask":            (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 1.00),
    "IC2:itemArmorQuantumHelmet":    (0.00, 0.00, 0.00, 1.00, 1.00, 0.95, 1.00),
    "IC2:itemArmorNanoHelmet":       (0.00, 0.00, 0.00, 1.00, 1.00, 0.95, 0.50),
    "enviromine:hardHat":            (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 0.25),
}

CLOTHY = re.compile(r"robe|cloth|manaweave|cultist|silk|wool|fabric|jerkin|tunic|"
                    r"overalls|sanguine|apiarist|vest|hood|cowl|leather", re.I)
GOLDLY = re.compile(r"gold|electrum|brass", re.I)
DENSEY = re.compile(r"diamond|void|ichor|terrasteel|elementium|primordial|gaia|"
                    r"netherite|obsidian|dark ?steel|darkSteel|quantum|neptunium|"
                    r"thaumium|fortress|spectre|manyullyn", re.I)
FIREY  = re.compile(r"\bimp\b|imphelmet|impboots|impjerkin|impleggings|blaze|nether|"
                    r"flame|ember|pyro|fire", re.I)
SEALY  = re.compile(r"boron|lead|uranium|plutonium|thorium|graphite|beryllium|"
                    r"tough|radiation", re.I)

ARM = re.compile(r"(helmet|helm$|chestplate|leggings|legs$|boots$|robe|hood|cap$|mask|"
                 r"tunic|cuirass|greaves|cowl|plate$|plate[A-Z]|vest|overalls|goggles|"
                 r"armor\.|armour)", re.I)
BAD = re.compile(r"pressure|_plate$|itemPlates|DensePlates|CarbonPlate|largeplate|"
                 r"terraPlate|incensePlate|FramingBoard|PrintPlate|AtlasPlate|"
                 r"EnchantedPlate|template|upgrade|icon|achievement|boat|"
                 r"^ThermalExpansion:Plate|Railcraft:part\.plate|^ExtraTiC|"
                 r"^StorageDrawers|^ObsidiPlates|^CarpentersBlocks|^voltzengine|"
                 r"^icbm|armourForge|armourInhibitor", re.I)

TMPL = """
    {key} {{
        S:01.ID={ident}
        D:"02.Temp Add - Night"={v[0]:.2f}
        D:"03.Temp Add - Shade"={v[1]:.2f}
        D:"04.Temp Add - Sun"={v[2]:.2f}
        D:"05.Temp Multiplier - Night"={v[3]:.2f}
        D:"06.Temp Multiplier - Shade"={v[4]:.2f}
        D:"07.Temp Multiplier - Sun"={v[5]:.2f}
        D:08.Sanity=0.0
        D:09.Air={v[6]:.2f}
        B:"10.Allow Camel Pack"={camel}
    }}
"""


def toks(ident):
    """Split a registry name into words. Substring matching gives false
    positives that matter: 'Leader' contains 'lead', 'Neighborhood' contains
    'hood', 'Probe' contains 'robe', 'Harvest' contains 'vest'."""
    name = ident.split(":", 1)[1]
    out = []
    for part in re.split(r"[^A-Za-z0-9]+", name):
        out += [w.lower() for w in re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z]*|[a-z]+|[0-9]+", part)]
    return out

HEAD  = {"helmet","helm","hood","cap","mask","cowl","goggles","hat","circlet","crown"}
CHEST = {"chestplate","chest","plate","robe","jerkin","tunic","vest","cuirass","overalls","body"}
LEGS  = {"leggings","legs","greaves","pants","leg"}
FEET  = {"boots","boot","shoes","sandals"}
NOTARM= {"block","tile","record","sigil","probe","obelisk","conduit","disc","seed",
         "template","upgrade","cover","servo","filter","relay","retriever","forge",
         "inhibitor","minecart","portable","bag","backpack","pouch","cell","capsule",
         "chestnut","bodypart","part","crossbow","nut","butter"}


def slot(ident):
    """Substring, not token, matching. Names like 'scorpbootscave' and
    'furchest' are one lowercase run with a suffix, so tokenising misses them
    entirely -- that flaw hid 21 pieces of real armour from an earlier audit."""
    n = ident.split(":", 1)[1].lower()
    if re.search(r"helmet|helm|hood|mask|cowl|goggles|hat|circlet|crown", n): return "head"
    if re.search(r"boots|boot", n):                                          return "feet"
    if re.search(r"leggings|legs|greaves|pants", n):                         return "legs"
    if re.search(r"chestplate|chest|plate|robe|jerkin|tunic|vest|cuirass|overalls", n): return "chest"
    return None


def is_armour(ident):
    if BAD.search(ident):                       return False
    n = ident.split(":", 1)[1].lower()
    # "chestnut" contains "chest"; "CrossbowBodyPart" contains "body"
    if re.search(r"chestnut|bodypart|crossbow", n):  return False
    if ident in blocks():                       return False   # storage, machines, decor
    if any(x in NOTARM for x in toks(ident)):   return False
    return slot(ident) is not None


def profile(ident):
    """Material class. Substring matching (names like 'hardenedleatherchest'
    are one lowercase run), but ROBE/CLOTH are tested BEFORE the shielded
    metals so 'CultistLeaderPlate' cannot match 'lead' -- that exact false
    positive shipped once already."""
    if ident in SPECIAL:
        return SPECIAL[ident], "special"
    n = ident.split(":", 1)[1].lower()
    if re.search(r"robe|manaweave|cultist|sanguine|ichorcloth|silk|arcane|wizard", n):
        return ROBE, "robe"
    if re.search(r"cloth|wool|fabric|jerkin|tunic|overalls|apiarist|vest|hood|cowl|leather", n):
        return CLOTH, "cloth"
    if re.search(r"imp|blaze|nether|flame|ember|pyro|fire", n):
        return FIRE, "fire"
    if re.search(r"boron|uranium|plutonium|thorium|graphite|beryllium|tough", n)        or ident.split(":", 1)[1].startswith("dU")        or "lead" in toks(ident):
        return SEALED(slot(ident)), "sealed"
    if re.search(r"diamond|void|ichor|terrasteel|elementium|primordial|gaia|obsidian|"
                 r"darksteel|dark_steel|steel|quantum|neptunium|thaumium|fortress|"
                 r"spectre|manyullyn|platinum", n):
        return DENSE, "dense"
    if re.search(r"gold|electrum|brass|crown", n):
        return GOLDY, "gold"
    return METAL, "metal"

def registry():
    d = gzip.decompress(open(LVL, "rb").read())
    return {n.decode() for k, n in re.findall(
        rb"([\x02])([A-Za-z][A-Za-z0-9_]{1,30}:[A-Za-z0-9_.\-]{2,48})", d)}



BLOCKS = None


def blocks():
    """Block registry. A storage chest is a block; armour is item-only --
    that is the clean way to tell 'minecraft:chest' from 'NuclearCraft:boronChest'."""
    global BLOCKS
    if BLOCKS is None:
        d = gzip.decompress(open(LVL, "rb").read())
        BLOCKS = {n.decode() for k, n in re.findall(
            rb"([])([A-Za-z][A-Za-z0-9_]{1,30}:[A-Za-z0-9_.\-]{2,48})", d)}
    return BLOCKS

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
    reg = registry()
    arm = sorted(x for x in reg if is_armour(x))
    files = sorted(f for f in os.listdir(CP) if f.endswith(".cfg"))

    added, rewritten, protected, per_kind = [], [], [], {}
    by_file = {}
    for ident in arm:
        if PROTECTED.search(ident):
            protected.append(ident); continue
        v, kind = profile(ident)
        per_kind[kind] = per_kind.get(kind, 0) + 1
        by_file.setdefault(cfg_for(ident.split(":", 1)[0], files), []).append((ident, v, kind))

    for f, items in sorted(by_file.items()):
        path = os.path.join(CP, f)
        text, nl = read(path)
        new = []
        for ident, v, kind in items:
            camel = "true" if slot(ident) == "chest" else "false"
            block = re.search(rf"\n    \w+ \{{\n        S:01\.ID={re.escape(ident)}\n.*?\n    \}}\n",
                              text, re.S)
            entry = TMPL.format(key=f"item_{re.sub(r'[^A-Za-z0-9]+','_',ident.split(':',1)[1]).strip('_').lower()}",
                                ident=ident, v=v, camel=camel)
            if block:
                text = text[:block.start()] + entry + text[block.end():]
                rewritten.append(ident)
            else:
                new.append(entry); added.append(ident)
        if new:
            text = add_section(text, "armor", new)
        if (new or any(i in rewritten for i, _, _ in items)) and apply:
            open(path, "wb").write(text.replace("\n", nl).encode("utf-8"))

    print(("APPLIED" if apply else "DRY RUN") + f"  — {len(arm)} armour items seen")
    print(f"  added      : {len(added)}")
    print(f"  rewritten  : {len(rewritten)}   (neutral -> material profile)")
    print(f"  protected  : {len(protected)}   (deliberately tuned, untouched)")
    print("\n  by material:")
    for k, n in sorted(per_kind.items(), key=lambda x: -x[1]):
        print(f"    {k:9} {n}")
    ch = [i for i in added + rewritten if slot(i) == "chest"]
    print(f"\n  chestplates given a camel pack: {len(ch)}")


if __name__ == "__main__":
    main()
