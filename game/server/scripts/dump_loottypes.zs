// Diagnostic: prints every chest-loot category the server actually has,
// including any registered by mods, into  logs/minetweaker.log  as
//     [LOOTTYPE] <name>
// Harvest that list, then delete this file (or leave it, it is harmless).
for t in vanilla.loot.lootTypes {
    print("[LOOTTYPE] " ~ t);
}
