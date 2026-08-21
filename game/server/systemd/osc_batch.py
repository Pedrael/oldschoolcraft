#!/usr/bin/env python3
"""OldSchoolCraft — batched EnviroMine change set.

Phases (run with --phase N --apply):

  1  probe    write ONE MoCreatures entry only. EnviroMine rewrites configs it
              owns on load, so if the file comes back normalised after a boot we
              know hand-created files are picked up -- and that answers it for
              Millenaire too, which also has no config today.
  2  full     everything else.

All of it is additive. Nothing existing is removed or retuned; every entry
written here targets an item or block that EnviroMine currently has no data for.

Values sit inside the envelope the metals update already established:
temp adds -1.00..+2.00, multipliers 0.80..1.05, air 0.00..1.00 per piece.
"""
import gzip, os, re, sys

ROOT = "/home/duduserver/minecraft/1.7.10"
CP   = f"{ROOT}/config/enviromine/profiles/default/CustomProperties"
DEF  = f"{ROOT}/config/enviromine/profiles/default/default_Settings.cfg"
LVL  = f"{ROOT}/world/level.dat"

# ---------------------------------------------------------------- armour ----
# (night, shade, sun, mNight, mShade, mSun, air)
NEUTRAL = (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 0.00)

FROST   = (2.00, 1.50, 0.00, 0.90, 0.95, 1.00, 0.00)   # cold specialist
NETHER  = (0.00, 0.00, -0.50, 1.00, 0.95, 0.85, 0.00)  # heat, warm after dark
DIRT    = (0.00, 0.00, 0.00, 0.95, 0.95, 0.95, 0.00)   # mild all-round
FUR     = (1.00, 0.75, 0.00, 1.00, 1.00, 1.10, 0.00)   # warm, hot in sun
HIDE    = (0.50, 0.25, 0.50, 1.00, 1.00, 1.00, 0.00)   # mild general

def cave(piece):   # full-set respirator: helmet carries most of it
    return (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 0.75 if piece == "helmet" else 0.25)

def hazmat(piece):  # best air in the pack, no combat value to trade against
    return (0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 1.00 if piece == "helmet" else 0.50)

MC_PIECES = {"helmet": "helmet", "plate": "plate", "legs": "legs", "boots": "boots"}

ARMOUR = {}   # ident -> tuple

for piece in MC_PIECES:
    ARMOUR[f"MoCreatures:scorp{piece}frost"]  = FROST
    ARMOUR[f"MoCreatures:scorp{piece}nether"] = NETHER
    ARMOUR[f"MoCreatures:scorp{piece}dirt"]   = DIRT
    ARMOUR[f"MoCreatures:scorp{piece}cave"]   = cave(piece)

for a, b in (("helmet", "helmet"), ("chest", "chest"), ("legs", "legs"), ("boots", "boots")):
    ARMOUR[f"MoCreatures:fur{b}"]  = FUR
    ARMOUR[f"MoCreatures:hide{b}"] = HIDE

ARMOUR["IC2:itemArmorHazmatHelmet"]     = hazmat("helmet")
ARMOUR["IC2:itemArmorHazmatChestplate"] = hazmat("chest")
ARMOUR["IC2:itemArmorHazmatLeggings"]   = hazmat("legs")

# Millenaire: modest regional jobs, deliberately weaker than the metals
ML = {
    "byzantine":           (0.00, 0.00, -0.25, 1.00, 1.00, 0.95, 0.00),
    "norman":              (1.00, 0.50, 0.00, 1.00, 1.00, 1.05, 0.00),
    "japaneseGuard":       (0.00, 0.00, 0.00, 0.95, 0.95, 0.95, 0.00),
    "japaneseWarriorBlue": (0.00, 0.00, 0.00, 0.95, 0.95, 0.95, 0.00),
    "japaneseWarriorRed":  (0.00, 0.00, 0.00, 0.95, 0.95, 0.95, 0.00),
}
for setname, vals in ML.items():
    for piece in ("Helmet", "Plate", "Legs", "Boots"):
        ARMOUR[f"millenaire:item.ml_{setname}{piece}"] = vals

# Chestplates that must accept a camel pack (camel flag only, stays neutral)
CHESTPLATES = [
    "minecraft:chainmail_chestplate",
    "Thaumcraft:ItemChestplateThaumium", "Thaumcraft:ItemChestplateVoid",
    "Thaumcraft:ItemChestplateFortress", "Thaumcraft:ItemChestplateVoidFortress",
    "Thaumcraft:ItemChestplateRobe", "Thaumcraft:ItemChestplateCultistPlate",
    "Thaumcraft:ItemChestplateCultistRobe", "Thaumcraft:ItemChestplateCultistLeaderPlate",
    "Botania:manasteelChest", "Botania:elementiumChest",
    "Botania:terrasteelChest", "Botania:manaweaveChest",
    "EnderIO:item.darkSteel_chestplate",
    "IC2:itemArmorBronzeChestplate", "IC2:itemArmorAlloyChestplate",
    "IC2:itemArmorNanoChestplate", "IC2:itemArmorQuantumChestplate",
    "IC2:itemArmorHazmatChestplate",
    "Aquaculture:item.NeptuniumPlate",
    "AWWayofTime:boundPlate", "AWWayofTime:boundPlateEarth", "AWWayofTime:boundPlateFire",
    "AWWayofTime:boundPlateWater", "AWWayofTime:boundPlateWind", "AWWayofTime:sanguineRobe",
    "BloodArsenal:glass_chestplate", "BloodArsenal:life_imbued_chestplate",
    "TConstruct:chestplateWood", "TConstruct:heavyPlate", "TConstruct:travelVest",
    "ThaumicTinkerer:ichorclothChest", "ThaumicTinkerer:ichorclothChestGem",
    "WitchingGadgets:item.WG_AdvancedRobeChest", "WitchingGadgets:item.WG_PrimordialChest",
    "RandomThings:spectreChestplate", "Railcraft:armor.steel.plate",
    "ThermalFoundation:armor.plateBronze", "ThermalFoundation:armor.plateElectrum",
    "ThermalFoundation:armor.platePlatinum", "ThermalFoundation:armor.plateSilver",
    "etfuturum:netherite_chestplate", "harvestcraft:hardenedleatherchestItem",
    "MoCreatures:scorpplatefrost", "MoCreatures:scorpplatenether",
    "MoCreatures:scorpplatecave", "MoCreatures:scorpplatedirt",
    "MoCreatures:furchest", "MoCreatures:hidechest",
    "millenaire:item.ml_byzantinePlate", "millenaire:item.ml_normanPlate",
    "millenaire:item.ml_japaneseGuardPlate",
    "millenaire:item.ml_japaneseWarriorBluePlate", "millenaire:item.ml_japaneseWarriorRedPlate",
]

# ---------------------------------------------------------------- blocks ----
FUNCTIONAL = {
 "appliedenergistics2","ae2stuff","ae2wct","extracells","neenergistics","thaumicenergistics",
 "EnderIO","IC2","Forestry","gendustry","MagicBees","ExtraBees","BinnieCore",
 "AWWayofTime","BloodArsenal","ThaumicTinkerer","ThaumicHorizons","ThaumicExploration",
 "WitchingGadgets","ForbiddenMagic","evilcraft","OpenComputers","OpenBlocks",
 "Railcraft","ImmersiveEngineering","NuclearCraft","openmodularturrets","AgriCraft",
 "JABBA","IronChest","StorageDrawers","EnderStorage","tinker_io","mffs","TMechworks",
 "ThermalExpansion","ThermalDynamics","Translocator","ExpandedRedstone","CompactSolars",
 "EnderTech","RotaryCraft","ReactorCraft","ElectriCraft","ChromatiCraft","runicdungeons",
 "waystones","locks","betterquesting","bq_standard","adventurebackpack","ironbackpacks",
 "WR-CBE_Addons","WR-CBE_Core","WR-CBE_Logic","icbmclassic","voltzengine",
}
MIXED = {"Thaumcraft","Botania","TConstruct","ExtraUtilities","RandomThings","BiblioCraft","Natura"}
PATTERN = re.compile(r"device|altar|pedestal|matrix|crucible|jar|table|node|airy|warded|"
                     r"pool|spreader|runic|agglomeration|flower|apiary|alveary|chest|"
                     r"tank|barrel|drawer|furnace|machine|generator|infuser|brewery|"
                     r"pylon|hourglass|opencrate|forestEye|teru|avatar|corporea|"
                     r"spawner|beacon|enchant|quest|smeltery|searedblock|castingchannel|"
                     r"drum|filing|manavoid|manadetector|distributor|lightrelay", re.I)
# 'prism' would also catch prismarine, which is decoration -- name these instead
EXTRA_PIN = {"Botania:prism"}
NEVER_PIN = re.compile(r"prismarine|Thaumcraft:blockCosmetic", re.I)

ARMOUR_TMPL = """
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
BLOCK_TMPL = """
    {key} {{
        S:01.Name={ident}
        I:02.MetaID=-1
        S:03.DropName=
        I:04.DropMetaID=-1
        I:05.DropNumber=-1
        B:"06.Enable Temperature"=false
        D:07.Temperature=0.0
        D:"08.Air Quality"=1.0
        D:09.Sanity=0.0
        S:10.Stability=none
        B:11.Slides=false
        B:"12.Slides When Wet"=false
    }}
"""
HEADER = "# Configuration file\n\n"


def registry():
    d = gzip.decompress(open(LVL, "rb").read())
    blocks, items = set(), set()
    for kind, name in re.findall(rb"([\x01\x02])([A-Za-z][A-Za-z0-9_]{1,30}:[A-Za-z0-9_.\-]{2,48})", d):
        (blocks if kind == b"\x01" else items).add(name.decode())
    return blocks, items


def read(path):
    if not os.path.exists(path):
        return HEADER, "\n"
    raw = open(path, "rb").read()
    nl = "\r\n" if b"\r\n" in raw else "\n"
    return raw.decode("utf-8", "replace").replace("\r\n", "\n"), nl


def write(path, text, nl, apply):
    if apply:
        open(path, "wb").write(text.replace("\n", nl).encode("utf-8"))


def key_for(i):
    return re.sub(r"[^A-Za-z0-9]+", "_", i).strip("_").lower()


def cfg_for(mod, files):
    for f in files:
        if f[:-4] == mod:
            return f
    for f in files:
        if f[:-4].lower() == mod.lower():
            return f
    return f"{mod}.cfg"          # created if absent


def add_section(text, section, entries):
    body = "".join(entries)
    m = re.search(rf"^{section} \{{$", text, re.M)
    if not m:
        return text.rstrip("\n") + f"\n\n{section} {{\n{body}}}\n"
    start = m.end()
    close = re.search(r"^\}$", text[start:], re.M)
    return text[:start + close.start()] + body + text[start + close.start():]


def main():
    apply = "--apply" in sys.argv
    phase = 2
    if "--phase" in sys.argv:
        phase = int(sys.argv[sys.argv.index("--phase") + 1])

    blocks, items = registry()
    files = sorted(f for f in os.listdir(CP) if f.endswith(".cfg"))
    log, created = [], []

    # ---- phase 1: single probe entry ----------------------------------
    if phase == 1:
        ident = "MoCreatures:scorphelmetfrost"
        assert ident in items, "probe item not in registry"
        path = os.path.join(CP, "MoCreatures.cfg")
        existed = os.path.exists(path)
        text, nl = read(path)
        if f"S:01.ID={ident}\n" not in text:
            e = ARMOUR_TMPL.format(key=f"item_{key_for(ident.split(':',1)[1])}",
                                   ident=ident, v=FROST, camel="false")
            text = add_section(text, "armor", [e])
            write(path, text, nl, apply)
        print("PHASE 1 — probe" + ("  [APPLIED]" if apply else "  [dry run]"))
        print(f"  {'updated' if existed else 'CREATED'} {path}")
        print(f"  one entry: {ident}")
        print("\n  Boot the server, then re-read the file. EnviroMine rewrites configs it")
        print("  owns, so a reformatted file proves hand-created configs are loaded.")
        return

    # ---- phase 2: everything ------------------------------------------
    by_file = {}
    unknown = []
    for ident, vals in ARMOUR.items():
        if ident not in items:
            unknown.append(ident); continue
        by_file.setdefault(cfg_for(ident.split(":", 1)[0], files), {})[ident] = vals
    for ident in CHESTPLATES:
        if ident not in items:
            if ident not in unknown: unknown.append(ident)
            continue
        f = cfg_for(ident.split(":", 1)[0], files)
        by_file.setdefault(f, {}).setdefault(ident, NEUTRAL)

    camel = set(CHESTPLATES)
    for f, idents in sorted(by_file.items()):
        path = os.path.join(CP, f)
        if not os.path.exists(path):
            created.append(f)
        text, nl = read(path)
        new = {i: v for i, v in idents.items() if f"S:01.ID={i}\n" not in text}
        if not new:
            continue
        entries = [ARMOUR_TMPL.format(key=f"item_{key_for(i.split(':',1)[1])}", ident=i, v=v,
                                      camel="true" if i in camel else "false")
                   for i, v in sorted(new.items())]
        write(path, add_section(text, "armor", entries), nl, apply)
        log.append(f"{f}: +{len(new)} armour entr{'y' if len(new)==1 else 'ies'}")

    # blocks -> Stability=none
    pin = []
    for b in sorted(blocks):
        mod, name = b.split(":", 1)
        if NEVER_PIN.search(b):
            continue
        if mod in FUNCTIONAL or (mod in MIXED and PATTERN.search(name)) or b in EXTRA_PIN:
            pin.append(b)
    per = {}
    for b in pin:
        per.setdefault(cfg_for(b.split(":", 1)[0], files), []).append(b)
    npin = 0
    for f, idents in sorted(per.items()):
        path = os.path.join(CP, f)
        if not os.path.exists(path):
            created.append(f)
        text, nl = read(path)
        new = [b for b in idents if f"S:01.Name={b}\n" not in text]
        if not new:
            continue
        entries = [BLOCK_TMPL.format(key=key_for(b.split(":", 1)[1]), ident=b) for b in new]
        write(path, add_section(text, "blocks", entries), nl, apply)
        npin += len(new)
    if npin:
        log.append(f"{npin} blocks pinned to Stability=none across {len(per)} files")

    # modded-block default: dirt-tier -> masonry-tier. Physics stays ON.
    text, nl = read(DEF)
    if 'S:"Default Stability Type (BlockIDs > 175)"=loose' in text:
        write(DEF, text.replace('"=loose', '"=average'), nl, apply)
        log.append("default_Settings.cfg: modded block stability loose -> average")

    print("PHASE 2" + ("  [APPLIED]" if apply else "  [dry run — nothing written]"))
    print(f"\nchanges ({len(log)}):")
    for x in log: print("  +", x)
    if created:
        print(f"\nconfig files CREATED ({len(sorted(set(created)))}): {', '.join(sorted(set(created)))}")
    if unknown:
        print(f"\nnot in registry, skipped ({len(unknown)}):")
        for u in unknown: print("  ?", u)


if __name__ == "__main__":
    main()
