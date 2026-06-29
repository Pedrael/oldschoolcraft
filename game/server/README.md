# OldSchoolCraft — Server

Minecraft 1.7.10 · Forge `10.13.4.1614` · Java 8

## Install
1. Run the Forge 1.7.10-10.13.4.1614 installer in "install server" mode (or place the universal jar).
2. Download every jar in [`modlist.txt`](modlist.txt) into `mods/`.
3. Keep `config/` and `scripts/` alongside the server jar.
4. Copy `server.properties`, create `eula.txt` with `eula=true`, then start.

## Recommended additions (server-side, not yet in the list)
- **AromaBackup** — scheduled world backups (uses Aroma1997Core, already present).
- **OpenEye** — crash/error analytics (uses OpenModsLib, already present).
- **TickDynamic** — holds TPS under load by throttling busy dimensions.
- **WorldEdit (Forge 1.7.10)** — grief rollback / terrain repair.
- Configure existing **FTBUtilities** for claims, permissions, ranks, `/home`/`/back`.

Do NOT add Fastcraft — it conflicts with the existing mixin perf stack
(unimixins / gtnhlib / hodgepodge / archaicfix).

## Watch-list
- `tcnodetracker` may be client-only; remove it if the log throws a client-class error.
- `journeymap` was removed (client map); re-add server-side only if you want its op/radar features.
